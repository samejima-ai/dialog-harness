# Migration Guide: v5.0.0 → v5.1.0

dialog-harness-layers v5.1.0 は **後方互換維持の minor 昇格**。破壊的変更なし。
本書は v5.0.0 環境を v5.1.0 で利用するための移行手順を要約する。

---

## What's new in v5.1.0

PR #19 のテストレビュー（シナリオ「ケロぴの森」: M2 monolith Web PWA / 中学生算数 / 絵で答える）で判明した L0 charter「AI 自律駆動開発が可能な開発環境の構築」未達 P0 4 項目を解消する。

| 追加 | 内容 |
|---|---|
| §0 受け入れ基準 | L0 完了 = ドキュメント生成 + scaffold 実体 + smoke test + §7.4 PASS の 4 条件すべて |
| Pre-flight 必読化 | §1.5 / §3.5 / §4 / §6 / §7 各冒頭に「Pre-flight: X を必読」行を追加（読まずに進行禁止） |
| scaffold-checklist.md | references/ に新設。Vite+TS+React+PWA の必須生成ファイル 12 種と smoke test 手順 |
| §7.4 自己検証 | broken reference / smoke test / DONT 自己照合 / Pre-flight 充足 / 受け入れ基準充足の 5 件チェック |

`crosscut-verifier-philosophy` の本実装は v5.1.0 では行わない（v5.2.0 候補として継続検討）。

---

## 既存プロジェクトへの影響

**強制適用なし**。Lifecycle ≥ 1 の既存プロジェクトはそのまま v5.1.0 配下で動作する。

| ケース | 適用タイミング |
|---|---|
| 新規プロジェクト | v5.1.0 以降に立ち上げた瞬間から §0 受け入れ基準・Pre-flight・scaffold checklist・§7.4 が全面適用 |
| 既存 Lifecycle ≥ 1 プロジェクト、既存機能 | 遡及修正は **不要**。既存成果物に v5.1.0 基準を適用する義務なし |
| 既存プロジェクトの v5.1.0 以降に追加開始する機能・フェーズ | 段階適用。L0 が再起動されるタイミングで自然に新基準を取り込む |

---

## 必須移行手順

なし。本 minor は user-scope に追加コピーするだけで利用可能。

```bash
# 1. dialog-harness 配布元から最新を取得
cd ~/path/to/dialog-harness
git pull origin master

# 2. user-scope への反映（手動コピー、AI は同期しない原則）
cp -R .claude/skills/layer0-spec-architect ~/.claude/skills/
```

---

## 任意手順（推奨）

### A. 既存プロジェクトで scaffold-checklist を活用したい

新機能追加時に L0 が起動するタイミングで `references/scaffold-checklist.md` の必須ファイル群を確認し、未生成のものは追加生成する。既存 src/ 配下の実装は変更しない。

### B. 既存プロジェクトで §7.4 自己検証を採用したい

次回 L0 起動時に §7.4 の 5 件チェックボックスを delivery/SELF-VERIFICATION-*.md に複製し、PASS/FAIL を記録する。FAIL があれば §7（出力）に進まず原因を解消する。

### C. credit-template のバージョン更新

L1 献上時に AI が `assets/credit-template.md` のバージョン番号差分を自動検出する（v4.2 から不変の挙動）。手動操作不要。

---

## 後退（v5.1.0 → v5.0.0）

破壊的変更なしのため、`.claude/skills/layer0-spec-architect/` を v5.0.0 時点のものに置き換えるだけで完全に v5.0.0 へ戻せる。新規追加された `references/scaffold-checklist.md` は削除、SKILL.md は v5.1.0 追加箇所（§0 受け入れ基準 / Pre-flight 行 / §7.4 / v5.1.0 履歴節）を除去する。

---

## FAQ

**Q1. v5.1.0 から `crosscut-verifier-philosophy` が動くか？**
A. 動かない。本リリースでも description 冒頭の「**v5.0.0 では発動禁止**」表記は更新するが、判定ロジックの本実装は v5.2.0 候補（別 minor）として扱う。v5.1.0 環境でも誤発動防止のため、いかなる発話でもこの skill を選択しないこと。

**Q2. scaffold-checklist は他 stack（Next.js / Vue 等）で使えるか？**
A. v5.1.0 では Vite+TS+React+PWA に限定。他 stack は将来 minor で追加（scaffold-checklist.md 内の「将来拡張ポイント」表参照）。

**Q3. §7.4 自己検証で FAIL したらどうする？**
A. §7（出力）に進まず原因を解消する。解消困難な場合は理由を `delivery/SELF-VERIFICATION-*.md` に明記したうえで、判断を人間献上する。

**Q4. Lifecycle ≥ 1 の既存プロジェクトで §0 受け入れ基準を満たさないが、続行できるか？**
A. 続行可能。本基準は v5.1.0 以降に追加開始する機能・フェーズに段階適用するため、既存成果物の遡及修正は要求されない。新規機能を追加する際の L0 起動時に新基準を適用する。

**Q5. v5.1.0 を skip して v5.2.0 を待っても良いか？**
A. v5.2.0 は v5.1.0 を前提に設計される（philosophy verifier が §0 受け入れ基準のチェック結果を入力に取る等）。skip は推奨しない。
