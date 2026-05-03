---
name: crosscut-issue-implementer
dimension: D4
description: >
  GitHub Issue を起点に AI 実装を起動する横断機構（仕様2、v5.0.0 追加 / v5.7.0 で gemini-cli base に全面改訂）。
  GitHub Actions workflow (issue-pickup.yml) 経由で起動、3 段階フィルター + AI triage で Issue 選別。
  Issue label `ready-for-ai` 付与で自動発動、または明示コマンドで起動。
  実装エージェント: gemini-cli (Anthropic API 回避、既存 GEMINI_API_KEY 流用)。
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

## 実装エージェント: gemini-cli (v5.7.0)

旧版（v5.0.0）は Anthropic 公式 claude-code-action 前提だったが、ユーザー要望「Anthropic API 回避、低コスト」に応じて **gemini-cli を実装エージェントとして転用**。既存 GEMINI_API_KEY を流用（追加コスト 0、Google AI Studio 無料 tier）。

**未踏領域**: PR レビュー（gemini-review.yml で実証済）から「実装」への拡張は未検証。失敗時のフォールバック候補：
- ローカル Claude Code セッション（手動運用継続）
- Copilot Workspace 切替
- 一時的 Anthropic API 使用

実装段階で品質懸念が顕在化した場合は autonomous-dev が独自 Council 起動可（adrv01-Ph1 自己申告プロトコル経由）。

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
