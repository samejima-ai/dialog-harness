# DH 更新プロトコル（既存プロジェクトの旧 DH を更新する正典手順）

> このドキュメントは **DH 側が提供する正典の更新手順**。既存プロジェクトの CC（Claude Code）が
> DH リモートを参照して更新するとき、**本ファイルと `dh-manifest.yml` に従えば安全に更新できる**。
> 各プロジェクトが手順を再発明しなくてよいようにするのが目的（単一情報源）。
>
> 関連: 配布 boundary は `dh-manifest.yml`、現行版は `VERSION`、メジャー移行経路は `dh-upgrades/`。

---

## 0. 前提と原則

- **配布＝コピー方式**: DH はパッケージマネージャや submodule ではなく、フレームワーク部を
  プロジェクトへコピーして導入する。更新も「新しい DH の DH 所有物を再 sync する」だけ。
- **boundary は推測しない**: 何を上書きし何を保護するかは `dh-manifest.yml` が正典（§2）。
- **同一メジャー内は後方互換**: v5.x → v5.y は追加のみ。再 sync で安全。メジャー跨ぎ（v4 以前→v5）だけ
  個別移行が要る（§4）。
- **移行の決定はプロジェクト個別判断**: DH は手順を**提供**するが、メジャー跨ぎの適用是非は各プロジェクトが判断する。

---

## 1. ピン留め（最初に必ず）

DH には現状リリースタグが無く、`master` HEAD は **開発途中状態（in progress 版）を含む**。
更新先を**特定の commit SHA に固定**して、全プロジェクトを同じ版に揃える。

```bash
# DH リモートを参照（例: 一時 clone）。<PIN> は更新時に決めた DH の commit SHA
git clone https://github.com/samejima-ai/dialog-harness /tmp/dh && git -C /tmp/dh checkout <PIN>
DH=/tmp/dh
cat "$DH/VERSION"          # 更新先バージョンを確認
cat "$DH/dh-manifest.yml"  # boundary を確認
```

> DH 側がリリースタグ運用を始めたら `<PIN>` をタグ（例 `v5.21.0`）にできる（推奨・将来）。

---

## 2. プロジェクト側で更新を実行（同一メジャー内）

`dh-manifest.yml` の分類どおりに処理する。**更新前に必ず `git commit`**（ロールバック用）。

```bash
cd <your-project>
git add -A && git commit -m "pre-DH-update snapshot" || true

# (a) overwrite: DH 所有 → ディレクトリごと sync（置換）。
#     merge ではなく置換にするのは rename/削除（例 council→crosscut-council）を orphan にしないため。
rm -rf .claude/skills && cp -r "$DH/.claude/skills" .claude/
rm -rf templates && cp -r "$DH/templates" ./

# (b) merge: プロジェクトがカスタムしうる → 差分を見て手動マージ（raw 上書き禁止）。
diff .claude/hooks.json "$DH/.claude/hooks.json" || echo "↑ 差分があれば手動マージ"

# (c) redeploy: placeholder を含む → raw コピー不可。crosscut-autonomous-drive で再展開。
#     CC に「autonomous-drive で workflow を再 deploy（placeholder 再展開・衝突は確認）」と指示。

# (d) never_touch: SPEC/DONT/REGIME/CLAUDE/history/delivery/.claude/disabled/ と自コードは触らない。
```

> `.claude/skills` を「置換」する際、プロジェクトが skills 内を独自カスタムしていたら失われる。
> ただし正しい使い方なら skill 本体はプロジェクト不変（差異は SPEC/sensors 等の入力に閉じる）なので
> 丸ごと置換してよい。カスタムがある場合のみ事前に退避・差分確認する。

---

## 3. バージョン記録

更新後、プロジェクトの `REGIME.md` に更新先バージョンと PIN を記録する（次回更新の起点になる）。

```
## DH バージョン
- updated_to: 5.21.0
- pinned_sha: <PIN>
- updated_at: <date>
```

---

## 4. メジャー跨ぎ（v4 以前 → v5）の場合

`dh-manifest.yml` の `min_same_major_from` より前のプロジェクトは**後方互換破壊あり**。
§2 の素朴な再 sync では壊れる。該当メジャーの `dh-upgrades/upgrade-spec-vX.0.0.md` の
**移行経路**に従う（例 v5.0.0: `council/` → `crosscut-council/` 配置換え、不要要素は削除でなく
`.claude/disabled/` へ退避、各段階で動く状態を保つ段階的移行）。

> upgrade-spec の注意どおり「設計意図を理解せずに手順だけ実行は禁止」。メジャー跨ぎは個別判断。

---

## 5. 更新後の検証（必須）

- `harness-verifier` を実行して構造健全性を確認
- 振り返り儀式（LC ≥ 1 なら）で文脈整合を確認
- `dh-manifest.yml` の `never_touch` が侵されていないか（SPEC/REGIME/history 等が無傷か）を確認

問題があれば §2 冒頭の pre-update commit に `git reset --hard` で戻す。

---

## 6. 将来の自動化（申し送り）

本プロトコルを skill 化した `crosscut-dh-self-update`（「DH を更新して」で起動 → manifest 読込 →
minor 自動 sync / major 移行誘導 → verifier 検証 → バージョン記録）を v5.22.0 以降で検討。
リリースタグ運用・`migrations.yml`（版遷移→手順の索引）も併せて。
