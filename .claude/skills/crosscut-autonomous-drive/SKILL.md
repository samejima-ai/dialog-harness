---
name: crosscut-autonomous-drive
dimension: D4
description: >
  autonomous-drive 標準化の deployment ヘルパー。dialog-harness の workflow テンプレートを
  利用者プロジェクトの `.github/workflows/` に placeholder 置換して deploy する。
  「autonomous-drive を deploy したい」「auto-merge.yml と gemini-review.yml を配置したい」
  「stop ラベル（do-not-merge / human-review-needed）と ready-for-ai を一括作成」
  「Repository Secrets（GH_REVIEW_PAT / GEMINI_API_KEY / CLAUDE_CODE_OAUTH_TOKEN）の設定ガイド」
  「auto-merge を opt-in から opt-out に反転（v5.9.0）したい」「workflow テンプレの placeholder 一覧」
  「opt-in / opt-out 境界 SPEC を確認」「autonomous-drive deploy が失敗、secrets 漏れか」等、
  autonomous-drive 機構の利用者プロジェクトへの配置・workflow テンプレ展開・
  ラベル/Secrets セットアップに関する発話で本スキルの起動を必ず検討する。
  spec-architect が dev_mode `autonomous` 判定時に明示起動する deployment 専用スキル。
  「Issue 自動実装」（→ issue-implementer）「Issue 品質チェック」（→ issue-quality-gate）
  「git auto-merge を GitHub UI で enable」（→ 別文脈、本スキルは workflow ファイル deploy 専用）
  との混同を避ける。
  philosophy.md 第 7 条のサポート skill 枠。境界 SPEC は `references/auto-merge-boundary.md` が一次情報源。
---

# Crosscut Autonomous-Drive (Deployment)

autonomous-drive 機構を利用者プロジェクトに deploy するためのサポート skill。
philosophy.md 第 7 条 4 役割属性（L0 設計 / L1 実装 / L2 統括 / Council 判断）の **サポート枠** に位置づく。
L3 運用層ではない（運用インシデントは L0 spec-architect へ還元する原則と整合）。

## 責務

1. **template 取得**: `templates/github-workflows/` から `auto-merge.yml.template` / `gemini-review.yml.template` を読み込む
2. **placeholder 置換**: spec-architect 対話で確定した値（`${ALLOWED_AUTHORS}` 等）を template に展開
3. **配置**: 利用者プロジェクトの `.github/workflows/` 配下にコピー
4. **label 作成**: GitHub UI または API 経由で `ready-for-ai` / `do-not-merge` / `human-review-needed` label を作成（autonomous_scope に応じて）。**v5.9.0 で `auto-merge` ラベルは廃止**（opt-in→opt-out 反転、二重ラベル方式の腐敗回避）
5. **secrets ガイド**: `GH_REVIEW_PAT` / `GEMINI_API_KEY` / **`CLAUDE_CODE_OAUTH_TOKEN`** (v5.7.1〜、issue-pickup.yml が必要とする) の設定手順をユーザーに提示（実際の入力は人間 P4 / spec-architect 対話で確認）。GH_REVIEW_PAT は **Contents/PR/Issues = Read and write** が必要（Read のみでは Claude Code 実装の commit/push が失敗）。詳細: `.claude/skills/crosscut-issue-implementer/references/setup-checklist.md`

## 起動条件

- `dev_mode: autonomous` が REGIME.md に記録されている
- `autonomous_scope` が `full` / `merge_gated` / `custom` のいずれかに確定済み
- spec-architect が deployment フェーズで本 skill を明示起動

ユーザー発話で「autonomous-drive を deploy して」「自律駆動の workflow を入れて」「auto-merge を有効化して」等の入力でも起動候補。

## 起動しないケース

- `dev_mode: local_only` または `github_assisted`（本機構は autonomous モード専用）
- spec-architect の dev_mode 判定が完了していない（先に L0 対話を完了させる）
- 既に deployment 済み（idempotent ではない、再 deploy は明示確認後）

## 処理フロー

```
1. REGIME.md から dev_mode + autonomous_scope を読み取る
2. autonomous_scope に応じた template セットを選択
   - full: auto-merge.yml.template + gemini-review.yml.template
   - merge_gated: gemini-review.yml.template のみ
   - custom: dev-env-spec.md Level C 詳細表に従う個別選択
3. 各 template ファイルを読み込み、placeholder を spec-architect 対話で確定した値で置換
   - placeholder 一覧と規約は references/placeholder-spec.md 参照
4. 利用者プロジェクトの .github/workflows/ 配下に配置
5. label 作成（autonomous_scope に応じた set）
6. Repository Secrets 設定ガイドを表示（人間が GitHub UI で実際に設定）
7. 配置結果を DELIVERY.md に記録（成功/失敗、配置パス、placeholder 値、未設定 secrets）
```

## 失敗時の挙動

- placeholder 値が未確定 → L0 spec-architect への Type C 献上（仕様改訂提案）
- template ファイル読み込み失敗 → Type D 献上（技術例外）
- 既存 workflow ファイル衝突検出 → 上書き前に明示確認、衝突履歴を `delivery/` に記録
- Repository Secrets 確認失敗（API 経由） → 人間 P4 へ手動確認依頼（暴走防止の安全側 fail）

## 失敗時の独立検証

`autonomous_scope: full` で deploy した場合、初回 PR で auto-merge.yml が稼働する時点が事実上の独立検証。dialog-harness 自身では PR #42 で実証済み（self-merge 成功）。

## 関連ドキュメント

### このスキル内 references/

- [references/placeholder-spec.md](references/placeholder-spec.md) — placeholder 一覧 + 規約
- [references/setup-checklist.md](references/setup-checklist.md) — label / secret / PAT 設定手順チェックリスト
- [references/auto-merge-boundary.md](references/auto-merge-boundary.md) — v5.9.0 opt-in/opt-out 境界 SPEC（一次情報源、AI が動かせない不変仕様）

### このスキル外

- `templates/github-workflows/auto-merge.yml.template` — auto-merge workflow テンプレート（dialog-harness リポジトリ ルート、v5.9.0 で opt-out 反転）
- `templates/github-workflows/gemini-review.yml.template` — gemini-review workflow テンプレート（同上）
- `.claude/skills/layer0-spec-architect/references/autonomous-drive-deployment.md` — spec-architect 対話レベルのガイド
- `.claude/skills/layer0-spec-architect/references/dev-env-spec.md` Level C — deploy 対象機能の autonomous_scope 別表
- `.claude/skills/layer0-spec-architect/references/philosophy.md` 第 7 条 — DH AI 組織論（本 skill の位置づけ）
- `.claude/skills/layer1-autonomous-dev/SKILL.md` §7.5 — PR 作成時の stop ラベル判定（境界 SPEC を参照する触発点）

## バージョン

- v0.1.0（v5.6.0 で新規導入、deployment 専念）
- **v0.2.0（v5.9.0 で改訂）**: opt-in→opt-out 反転、`auto-merge` ラベル廃止、stop ラベル方式に統合、境界 SPEC `auto-merge-boundary.md` を一次情報源化
- v5.6.x 候補: destructive change detector / circuit breaker（guardian 機能）の追加
- v5.7.0 候補: ALLOWED_AUTHORS 動的化（複数 contributor 体制で必要時）
