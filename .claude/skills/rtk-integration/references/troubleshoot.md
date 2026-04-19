# トラブルシュート

rtk-integration 導入時の典型的な失敗ケースと対処。

## ケース 1: `rtk --version` で `command not found` / `rtk is not recognized`

### 原因
- インストールは成功したが、現在のシェルセッションに PATH 変更が反映されていない

### 対処
1. **新しいターミナルを開く**（最も確実）
2. もしくは現セッションで:
   ```powershell
   $env:Path = "$env:Path;$env:USERPROFILE\.local\bin\rtk"
   ```
3. それでも駄目なら、User PATH に登録されているか確認:
   ```powershell
   [Environment]::GetEnvironmentVariable('Path', 'User')
   ```
   `.local\bin\rtk` が含まれていない場合は install.ps1 を再実行する。

---

## ケース 2: `rtk init -g` が権限エラーで失敗

### 原因
- 書き込み先（`~/.claude/settings.json` 等）の権限不足
- OneDrive 等の同期ディレクトリが書き込みを弾いている

### 対処
1. `~/.claude/` ディレクトリの権限を確認:
   ```powershell
   Get-Acl $env:USERPROFILE\.claude
   ```
2. OneDrive 配下に `.claude` がある場合、ファイルのロック状態を確認する
3. PowerShell を管理者権限ではなく**通常ユーザー権限**で再実行（rtk は User scope 専用）

---

## ケース 3: 圧縮されない（出力が素のコマンドと同じ）

### 原因
- グローバルフックが設置されていない
- Claude Code の hook 機構が無効化されている

### 対処
1. フック設置状況を確認:
   ```bash
   rtk init --show
   ```
2. 未設置なら再実行:
   ```bash
   rtk init -g
   ```
3. それでも効かない場合、明示呼び出しで動作確認:
   ```bash
   rtk git status
   ```
   これで圧縮されるなら、フックレイヤーの問題。

---

## ケース 4: ダウンロード失敗（`Invoke-WebRequest` エラー）

### 原因
- 企業プロキシ / ファイアウォール
- GitHub へのアクセス制限

### 対処
1. 手動ダウンロード:
   - <https://github.com/rtk-ai/rtk/releases/download/v0.37.1/rtk-x86_64-pc-windows-msvc.zip>
2. `%TEMP%\rtk-x86_64-pc-windows-msvc.zip` に配置
3. install.ps1 を再実行（既に zip があればダウンロードをスキップする実装に非対応なので、URL 部分をコメントアウトして手動で展開ステップから始める）

---

## ケース 5: 越境パッチが未適用（既存 skill で通知が出ない）

### 原因
- skill ディレクトリのパス不一致（`$SkillsDir` 既定値 `$env:USERPROFILE\.claude\skills` と実配置の食い違い）
- 既に他バージョンのパッチが適用されている

### 対処
1. パッチ適用状況を確認:
   ```powershell
   Select-String -Path "$env:USERPROFILE\.claude\skills\*\SKILL.md" -Pattern 'rtk-integration: begin'
   ```
2. 該当ファイルが存在しないなら、対象スキルが別パスに置かれている可能性。install.ps1 の `$SkillsDir` 定義を調整。

---

## ケース 6: uninstall 後もバイナリが残る / PATH が消えない

### 原因
- rtk プロセスがバックグラウンドで動作中
- PowerShell のセッションが古い PATH をキャッシュ

### 対処
1. タスクマネージャーで `rtk.exe` 関連プロセスを終了
2. uninstall.ps1 を再実行
3. 新しいターミナルで `where rtk` が何も返さないことを確認

---

## 解決しない場合

以下を集めて human-in-the-loop で報告:

- `rtk --version` の出力（or エラーメッセージ）
- `rtk init --show` の出力
- `[Environment]::GetEnvironmentVariable('Path', 'User')` の出力
- `~/.local/share/rtk/tee/` の最新ログ（フィルタ失敗時の生出力）
