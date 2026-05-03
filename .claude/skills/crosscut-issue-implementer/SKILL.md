---
name: crosscut-issue-implementer
dimension: D4
description: >
  GitHub Issue を起点に AI 実装を起動する横断機構（仕様2、v5.0.0 追加 / v5.7.0 改訂 / v5.7.1 で Claude Code CLI メイン化）。
  GitHub Actions workflow (issue-pickup.yml) 経由で起動、3 段階フィルター + AI triage で Issue 選別。
  Issue label `ready-for-ai` 付与で自動発動、または明示コマンドで起動。
  実装エージェント: **Claude Code CLI** (anthropics/claude-code-action + CLAUDE_CODE_OAUTH_TOKEN、Pro/Max サブスクリプション、追加 API 課金なし)。
  AI triage は **gemini-cli** 維持（軽量、無料 tier）、実装失敗時のフォールバックも gemini-cli（人間 P4 判断発動）。
  philosophy.md 第 7 条「AI 組織論」の「サポート skill」枠（4 役割を補助、L3 運用層ではない）。
  dev_mode `autonomous` + `autonomous_scope: full` のみで active 化。
---

# Issue Implementer

## 発動条件

- Issue に label `ready-for-ai` が付与された（人間 P2 の明示 GO サイン、philosophy 第 7 条）
- REGIME.md `dev_mode: autonomous` + `autonomous_scope: full` （local_only / github_assisted では起動しない）
- Repository Secrets: GEMINI_API_KEY + GH_REVIEW_PAT が設定済

## 処理フロー（v5.7.0 改訂版）

```
1. Pre-check: GEMINI_API_KEY + GH_REVIEW_PAT availability
2. Circuit Breaker check: 日次/月次 Issue pickup 上限の確認 (references/circuit-breaker-spec.md)
3. 3 段階フィルター実行 (references/issue-filter-spec.md):
   一次: label `ready-for-ai` 確認（trigger 条件で既に通過）
   二次: author allowlist + 本文必須項目（再現手順 / 期待動作 / 受入条件）
   三次: AI triage (gemini-cli が Issue 内容を読んで pickup 可否判定)
        - SPEC.md / DONT.md / current_focus と照合
        - skip 時は理由 label を自動付与（needs-clarification / out-of-scope / focus-mismatch）
        - Issue は close せず人間差し戻し
4. Pickup 確定: label `in-progress` 自動付与、Issue 番号で branch 作成（feat/<issue-num>-<slug>）
5. 実装: gemini-cli が repo を clone + Issue + SPEC を読み込み + 実装 + commit
6. PR 作成: gh pr create + ready-for-review + (autonomous_scope: full なら) `auto-merge` label 自動付与
7. 後段委譲: 既存 gemini-review.yml + auto-merge.yml が引き継ぎ
8. 統計記録: .gemini/issue-pickup-stats.json に pickup 結果を append (Circuit Breaker 用)
```

## 実装エージェント: Claude Code CLI (v5.7.1 で改訂)

### v5.7.1 メイン: Claude Code CLI

`anthropics/claude-code-action@v0` を採用、`CLAUDE_CODE_OAUTH_TOKEN`（Anthropic Pro/Max サブスクリプションから発行）で認証。**追加 API 課金なし**（サブスクリプション内で稼働）。

旧版経緯：
- v5.0.0: claude-code-action 前提（API key、未稼働）
- v5.7.0: gemini-cli 採用（API 回避目的、AD-026）
- **v5.7.1**: Pro/Max サブスクリプション + OAuth token 経路の発見で Claude Code CLI を再採用（AD-029、AD-026 訂正）

### gemini-cli の継続用途（v5.7.1）

| 用途 | エージェント |
|---|---|
| AI triage（Issue 内容判定、軽量処理） | **gemini-cli** メイン継続（GEMINI_API_KEY 無料 tier）|
| 実装本体（コード生成、PR 作成）| **Claude Code CLI** メイン、gemini-cli はフォールバック |
| PR レビュー (gemini-review.yml) | **gemini-cli** メイン継続（変更なし）|

異質モデル併走（philosophy 第 3 条「情報純度」）は triage / 実装フォールバック / PR レビューの 3 場面で gemini を維持することで保全。

### Claude Code 失敗時のフォールバック

`anthropics/claude-code-action@v0` 失敗時の挙動（**自動フォールバックなし、人間 P4 判断**）：

1. workflow が Issue に label `pickup-failed` 自動付与
2. Issue コメントで notice: 「Claude Code 実装失敗。人間判断要請: gemini-cli で再 trigger するか、`do-not-pickup` で block するか」
3. 人間 P4 が判断（philosophy.md 第 4 条「人間が判断する場面」+ 第 7 条 P4「暴走時介入」と整合）
4. gemini で再 trigger する場合: 別 workflow 起動（v5.7.x で実装、現状は手動運用）

自動フォールバック導入は v5.7.x 以降に観測駆動で判断（fail パターン蓄積後）。

## 失敗時の挙動

| 失敗種別 | 対処 |
|---|---|
| Pre-check FAIL (secrets 未設定) | notice 出力で skip（red CI にしない） |
| Circuit Breaker 上限超過 | label `circuit-broken` 自動付与 + workflow 全停止 + notice |
| 二次フィルター FAIL (本文不足) | label `needs-clarification` + Issue は close せず人間差し戻し |
| 三次フィルター FAIL (out-of-scope / focus-mismatch) | 該当 label 自動付与 + 人間判断要請 |
| 実装中の致命的エラー (gemini-cli 失敗) | label `pickup-failed` + Issue に notice コメント + branch 削除 |
| PR 作成後 24h 以内に変更なし | 自動 release（label `in-progress` 削除）+ notice |

## CTL との関係

CTL は本 v5.7.0 改訂で参照しない（v5.0.0 旧版で言及されていたが未稼働だった）。`autonomous_scope` 軸（v5.6.0 追加）が運用粒度を決定する：

| autonomous_scope | issue-pickup.yml | auto-merge label 付与 | 後段 |
|---|---|---|---|
| full | ✅ 起動 | ✅ 自動 | gemini-review + auto-merge |
| merge_gated | △ 起動可（PR 作成まで） | ❌ 付与しない | 人間 approve 待ち |
| custom | 個別指定 | 個別 | 個別 |

## 関連ドキュメント

### このスキル内 references/

- [references/issue-filter-spec.md](references/issue-filter-spec.md) — 3 段階フィルター詳細
- [references/triage-protocol.md](references/triage-protocol.md) — gemini-cli AI triage プロトコル
- [references/circuit-breaker-spec.md](references/circuit-breaker-spec.md) — 経済的暴走防止機構
- [references/implement-protocol.md](references/implement-protocol.md) — 実装プロトコル詳細（v5.0.0 から維持、v5.7.0 で gemini-cli 対応に追補）

### このスキル外

- `.github/workflows/issue-pickup.yml` — dialog-harness 自身の deploy
- `templates/github-workflows/issue-pickup.yml.template` — 利用者プロジェクト展開用
- `.claude/skills/layer0-spec-architect/references/autonomous-drive-deployment.md` — deployment ガイド
- `.claude/skills/layer0-spec-architect/references/regime-assessment.md` §current_focus 判定 — pickup 判定で参照
- `.claude/skills/layer0-spec-architect/references/philosophy.md` 第 7 条 — DH AI 組織論（本 skill の位置づけ）
- `.claude/skills/layer1-autonomous-dev/SKILL.md` — 実装本体（gemini-cli が呼び出される側の規約）
- `.claude/skills/layer1-independent-reviewer/SKILL.md` — self-review 実行体

## バージョン

- v0.1.0 (v5.0.0 で導入、claude-code-action 前提、未稼働)
- **v0.2.0 (v5.7.0 で全面改訂)**: gemini-cli base、3 段階フィルター + AI triage + Circuit Breaker、dialog-harness 自身に deploy
- v5.7.x 候補: gemini-cli 実装品質観測 + 必要時の Council 起動（フォールバック判断）
