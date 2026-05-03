# Implement Protocol

`crosscut-issue-implementer` の実装フロー詳細。spec §3.2.5 を本体化。

**v5.7.1 で全面改訂**: 実装エージェントを Claude Code CLI (`anthropics/claude-code-action@v0`) に切替、CTL ベースの分岐を `autonomous_scope` ベースに整理（CTL は本 skill では参照しない、SKILL.md「CTL との関係」節参照）。

## モード別動作

### dev_mode = `local_only` または `github_assisted`

issue-pickup.yml は **発火しない**。本 skill は dev_mode `autonomous` + `autonomous_scope: full` のみで active 化される（SKILL.md §発動条件）。

### dev_mode = `autonomous`

| autonomous_scope | issue-pickup.yml | 実装エージェント | レビュー | auto-merge | 並列度 |
|---|---|---|---|---|---|
| full | ✅ 起動 | Claude Code CLI (anthropics/claude-code-action) | gemini-review + Copilot review | ✅ 自動 (CI 全通過時のみ) | 1（同 Issue concurrency 排他） |
| merge_gated | △ 起動可（PR 作成まで） | Claude Code CLI | 人間 approve | ❌ 付与しない | 個別 |
| custom | 個別指定 | 個別 | 個別 | 個別 | 個別 |

並列度は `REGIME.md` の `## parallel_impl_limit` で上書き可能（v5.7.x 候補）。

## 実行手段：anthropics/claude-code-action（v5.7.1〜）

Anthropic 公式の [claude-code-action](https://github.com/anthropics/claude-code-action) を採用。
ワークフロー実体は `.github/workflows/issue-pickup.yml` および `templates/github-workflows/issue-pickup.yml.template`。

### バージョン

- v5.7.1 時点: `@v0` タグ（最新 stable）
- SHA pin は v5.7.x で観測駆動判断

### 必要な GitHub Secrets

- `CLAUDE_CODE_OAUTH_TOKEN`（必須、v5.7.1〜）— Anthropic Pro/Max サブスクリプション、`claude setup-token` で取得
- `GEMINI_API_KEY`（必須）— AI triage + PR レビュー、Google AI Studio 無料 tier 可
- `GH_REVIEW_PAT`（必須）— Fine-grained PAT、Contents/PR/Issues = Read and write

詳細手順: [`setup-checklist.md`](./setup-checklist.md)

### v5.7.0 以前との差分

- 旧: `ANTHROPIC_API_KEY`（API key 経路、追加課金）→ **廃止**（v5.7.0 AD-026 で gemini-cli に切替後、v5.7.1 AD-029 で Pro/Max OAuth 経路に確定）
- 旧: `templates/.github/workflows/issue-to-impl.yml` → **廃止**（issue-pickup.yml に統合、v5.7.0）
- 旧: gemini-cli が実装本体 → **Claude Code CLI に変更**（v5.7.1）

## self-review（PR 作成後）

`layer1-independent-reviewer` を起動して `delivery/VERIFICATION.md` を生成（M2 以上、layer1-autonomous-dev フロー §7 で必須）。

| autonomous_scope | self-review 結果の扱い |
|---|---|
| full | PASS なら auto-merge 候補、FAIL なら自動差戻し（自力修正上限内）|
| merge_gated | PASS でも人間 approve 必須 |
| custom | 個別設定 |

## auto-merge 発動条件（autonomous_scope = full のみ）

`.github/workflows/auto-merge.yml`（v5.5.3 で新設）で実装。発動条件：

1. PR に `auto-merge` label が付いている（issue-pickup.yml が full 時に自動付与）
2. PR に `do-not-merge` label が付いていない
3. 全 CI check が green（gemini-review + verify + Copilot review 等）
4. PR が ready for review（draft でない）

これらすべて満たした場合のみ `gh pr merge --auto --squash` を実行。

`autonomous_scope: merge_gated` では auto-merge label を付与しないため、本 workflow は発動しない。

## Issue → 実装失敗時の挙動

Claude Code CLI 失敗時：

1. workflow が Issue に label `pickup-failed` 自動付与
2. Issue コメントで notice 出力
3. **自動フォールバックなし**（人間 P4 判断、philosophy 第 4 条「人間が判断する場面」+ 第 7 条 P4「暴走時介入」）
4. 選択肢: gemini-cli で再 trigger（手動運用、v5.7.x で workflow 化予定）/ `do-not-pickup` で block / Issue 本文更新 + `ready-for-ai` 再付与

詳細は SKILL.md「Claude Code 失敗時のフォールバック」節参照。

## CHANGELOG 記録

各 PR 作成・マージごとに `history/CHANGELOG.md` にレベル A 追記（layer1-autonomous-dev §7.5 履歴層更新規約）。

## バージョン

- v0.1.0 (v5.0.0 で導入、ANTHROPIC_API_KEY + issue-to-impl.yml 前提、未稼働)
- v0.2.0 (v5.7.0 で gemini-cli 改訂、issue-pickup.yml に統合)
- **v0.3.0 (v5.7.1 で全面改訂)**: Claude Code CLI (claude-code-action@v0) + CLAUDE_CODE_OAUTH_TOKEN 経路、CTL 参照廃止、autonomous_scope ベース整理
