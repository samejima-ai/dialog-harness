# SHA256 更新プロトコル

`rtk-integration/scripts/install.ps1` の `$ExpectedSha256` を `$RtkVersion` の bump 時に更新する手順。本ファイルは Council 諮問 `council-2026-05-13T03:35:00Z-rtkSHA`（unanimous 案 A + 哲学者 minority 採用、`agreed_with_modification`）により新設された。

---

## 設計意図（なぜ SHA verification が必要か）

`install.ps1` は GitHub Releases から rtk の zip を download し、ユーザーの `~/.local/bin/rtk` に展開する。**install スクリプトを実行する時点で、download 元が改ざんされていないこと（MITM / mirror compromise / supply-chain attack 等）を保証する手段が SHA256 のみ**である。

そのため、本 skill は以下の構造で hardening している:

1. **default で SHA verification 必須**: `$ExpectedSha256` を script 内に hard-code し、download 後の zip と byte 単位照合。mismatch なら install 中止
2. **`$ExpectedSha256` が empty な場合は install 拒否**: SHA を埋め忘れた状態 = 「Maintainer が承認していない」状態として扱い、自動 install を block する（philosophy 第 6 条「人間最終承認」の具現）
3. **明示 escape hatch のみ skip 可能**: `$env:RTK_SKIP_VERIFY -eq '1'` の場合のみ warning 出力で続行（philosophy 第 7 条 P4 介入権の事前付与、明示意思表示）

この設計は dialog-harness PR #93（v5.16.1）で確立。Council 諮問 `rtkSHA` で再確認され、philosophy 第 2 条 Shift Left 原則（発生防止 > 検出）および第 6 条「人間最終承認」と整合することが unanimous 判定された。

---

## 更新タイミング

以下のいずれかが発生した時:

- `$RtkVersion` を新しいバージョンに bump する（例: v0.37.1 → v0.38.0）
- 上流（rtk-ai/rtk）が同バージョンの zip を re-release した（稀だが起こり得る）

更新せずに `$RtkVersion` のみ書き換えると **既存 SHA と download zip が mismatch して install が中止される**（fail-safe）。これは意図通りの挙動であり、SHA 更新を促す signal として機能する。

---

## 取得 + verify 手順

### 1. 公式 checksums.txt から SHA を取得

GitHub Releases は zip と同じディレクトリに `checksums.txt` を公開している:

```bash
curl -sL "https://github.com/rtk-ai/rtk/releases/download/v<NEW_VERSION>/checksums.txt"
```

出力から `rtk-x86_64-pc-windows-msvc.zip` の行を抽出:

```
3b9f207e8ea360d744649760788cbcf7d6ce62d8ccb8677aa3c8d1513a9d2cc2  rtk-x86_64-pc-windows-msvc.zip
```

### 2. zip を独立 download + self-compute で cross-verify

`checksums.txt` が同じ release から配布されているため、公式値を盲信せず **手元で zip を download + self-compute** して cross-verify する（trust-but-verify、第 3 条 情報純度原則）:

```bash
TMP_ZIP=$(mktemp -p /tmp --suffix=.zip)
curl -sL -o "$TMP_ZIP" "https://github.com/rtk-ai/rtk/releases/download/v<NEW_VERSION>/rtk-x86_64-pc-windows-msvc.zip"
sha256sum "$TMP_ZIP"
rm -f "$TMP_ZIP"
```

`checksums.txt` の値と `sha256sum` の出力が **完全一致** することを確認する。一致しない場合は本プロトコル中止 + dialog-harness Issue 起票（supply chain compromise の可能性）。

### 3. `install.ps1` の `$ExpectedSha256` 定数を更新

`install.ps1` 冒頭の `$ExpectedSha256` 代入行を新しい SHA 値に書き換える:

```powershell
# Before
$ExpectedSha256 = '<OLD_SHA>'

# After
$ExpectedSha256 = '<NEW_SHA_FROM_STEP_2>'
```

合わせて `$RtkVersion` 定数も新バージョンに更新する（こちらが先でも後でもよい、commit を 1 つにまとめる）。

> 行番号は将来のコメント追記等で容易にずれるため、本プロトコル内では定数名（`$ExpectedSha256` / `$RtkVersion`）で参照する。最新の行番号は `grep -n '^\$ExpectedSha256\|^\$RtkVersion' .claude/skills/rtk-integration/scripts/install.ps1` で都度確認のこと。

### 4. Windows 実機で動作確認（推奨、Council 諮問 rtkSHA の test plan）

可能であれば Windows native PowerShell で `install.ps1` を実行:

```powershell
# Clean state (既存 ~/.local/bin/rtk があれば uninstall)
& "$env:USERPROFILE\.claude\skills\rtk-integration\scripts\uninstall.ps1"

# Re-install with new SHA
& "$env:USERPROFILE\.claude\skills\rtk-integration\scripts\install.ps1"
```

期待出力: `[rtk-integration] SHA256 OK.` が出ること。`SHA256 mismatch` が出る場合は SHA 値の typo または supply chain 問題を疑う。

Windows 実機検証が困難な場合は、最低限 `install.ps1` を PowerShell parser で構文チェック（`pwsh -NoProfile -Command "Get-Command -Syntax ..."` 等）+ Linux 上で `sha256sum` cross-verify を厳密にやることでカバーする。

---

## 失敗時の対処（escape hatch、緊急時のみ）

`$ExpectedSha256` を空のままにすることは **本プロトコル下では禁止**だが、緊急時（公式 checksums.txt 配信停止 + 上流対応待ち等）には以下の escape hatch が存在する:

```powershell
$env:RTK_SKIP_VERIFY = '1'
& "$env:USERPROFILE\.claude\skills\rtk-integration\scripts\install.ps1"
```

この経路は MITM 検出を諦める明示意思表示であり、`install.ps1` が WARNING を出力する。常用しない。緊急利用後は本プロトコルに従って SHA を確定し、escape hatch を不要にする状態に戻す。

---

## 関連 Council

- `council-2026-05-13T03:35:00Z-rtkSHA` — 本プロトコル新設根拠（unanimous 案 A + 哲学者 minority 採用）
- DH PR #93（v5.16.1, 2026-05-12 merged）— `$ExpectedSha256` + escape hatch 構造の導入元

---

## 関連ドキュメント

- `../scripts/install.ps1` — `$ExpectedSha256` の更新対象
- `../SKILL.md` — skill 全体の責務と起動条件
- `../../layer0-spec-architect/references/philosophy.md` 第 2 条 Shift Left / 第 6 条 人間最終承認 — 本プロトコルの哲学根拠
