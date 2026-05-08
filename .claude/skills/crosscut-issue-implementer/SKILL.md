---
name: crosscut-issue-implementer
dimension: D4
description: >
  GitHub Issue を起点に Claude Code CLI で AI 実装を自動起動する横断機構。
  「ready-for-ai 付けた Issue が動かない」「Issue から自動で PR 出すやつ設定したい」
  「triage で弾かれた」「issue-pickup.yml が type-aware 化された件」「circuit-breaker の閾値」
  「P4 暴走介入」「CLAUDE_CODE_OAUTH_TOKEN の設定漏れ」「autonomous_scope full なのに走らない」
  「実装失敗時のフォールバック gemini-cli への切替」等、ready-for-ai ラベル経由の自動実装パイプライン
  および issue-pickup.yml 関連の発話で本スキルの起動を必ず検討する。
  3 段階フィルター + AI triage で Issue 選別、Pro/Max サブスクリプションで追加 API 課金なし。
  「Issue にして」（→ issue-dispatcher）「Issue 品質チェック」（→ issue-quality-gate）
  「PR レビュー」（→ independent-reviewer）「auto-merge workflow deploy」（→ autonomous-drive）
  との混同を避ける。
  philosophy.md 第 7 条「AI 組織論」のサポート skill 枠。
  dev_mode `autonomous` + `autonomous_scope: full` のみで active 化（local_only / github_assisted では起動しない）。
---

# Issue Implementer

## 発動条件

- Issue に label `ready-for-ai` が付与された（人間 P2 の明示 GO サイン、philosophy 第 7 条）
- REGIME.md `dev_mode: autonomous` + `autonomous_scope: full` （local_only / github_assisted では起動しない）
- Repository Secrets: **CLAUDE_CODE_OAUTH_TOKEN + GEMINI_API_KEY + GH_REVIEW_PAT** が設定済（v5.7.1〜、詳細は `references/setup-checklist.md`）

## 処理フロー（v5.7.1 改訂版）

```
1. Pre-check: CLAUDE_CODE_OAUTH_TOKEN + GEMINI_API_KEY + GH_REVIEW_PAT availability
2. Circuit Breaker check: 日次/月次 Issue pickup 上限の確認 (references/circuit-breaker-spec.md)
3. 3 段階フィルター実行 (references/issue-filter-spec.md):
   一次: label `ready-for-ai` 確認（trigger 条件で既に通過）
   二次: author allowlist + 本文必須項目（type-aware、v5.10.0 追加 — 下記 §Issue 本文必須セクション規格 参照）
   三次: AI triage (gemini-cli が Issue 内容を読んで pickup 可否判定)
        - SPEC.md / DONT.md / current_focus と照合
        - skip 時は理由 label を自動付与（needs-clarification / out-of-scope / focus-mismatch）
        - Issue は close せず人間差し戻し
3.5. crosscut-issue-quality-gate 最終確認（v5.8.0 追加、発動契機 (d)）
4. Pickup 確定: label `in-progress` 自動付与、Issue 番号で branch 作成（feat/<issue-num>-<slug>）
5. 実装: **Claude Code CLI** (anthropics/claude-code-action) が repo を clone + Issue + SPEC を読み込み + 実装 + commit
6. PR 作成: gh pr create + ready-for-review。**v5.9.0 で `auto-merge` ラベル自動付与は廃止**（opt-in→opt-out 反転、Council 諮問 `council-2026-05-06T08:30:00Z-amrev1` 由来）。opt-in 領域（`crosscut-autonomous-drive/references/auto-merge-boundary.md` §opt-in 領域）に該当する変更を含む場合のみ `--label human-review-needed` を付与
7. 後段委譲: 既存 gemini-review.yml + auto-merge.yml が引き継ぎ（auto-merge.yml は stop ラベル不在をデフォルトに反転済）
8. 統計記録: .gemini/issue-pickup-stats.json に pickup 結果を append (Circuit Breaker 用、v5.7.x で永続化完成予定)
```

## Issue 本文必須セクション規格 (v5.10.0 追加)

dialog-harness の autonomous-drive 入力 Issue は philosophy 第 5 条（献上哲学）の起票元類型に従い **2 系統**に分類される。`issue-pickup.yml` の `body_check` ステップは `discussion` ラベルの有無で分岐し、type 別に必須セクションを検査する。

### bug-style（`discussion` ラベルなし）

利用者の bug 報告・機能要望（philosophy 第 7 条 P1/P2 起票）を想定。GitHub の標準 bug template と互換。

| セクション | 必須 | 用途 |
|---|---|---|
| `## 再現手順` または `## Steps to reproduce` | ✅ | bug の再現条件 |
| `## 期待動作` または `## Expected behavior` | ✅ | 修正後の正しい挙動 |
| `## 受入条件` または `## Acceptance criteria` | ✅ | 完了判定基準 |

### discussion-style（`discussion` ラベルあり）

`crosscut-issue-dispatcher` 経由の SPEC/ADR 差分起票、`crosscut-feedback-loop` 経由の検証 Issue、L0 spec-architect 対話起点の仕様改訂提案（philosophy 第 7 条 P3/P4 起票）を想定。

| セクション | 必須 | 用途 |
|---|---|---|
| `## L0 spec-architect 対話記録` | ✅ | L0 通過の証跡 + 確定軸（実装の根拠） |
| `## 実装スコープ` | ✅ | 変更対象ファイル + バージョン（実装の対象） |
| `## 背景` または `## 課題` | 推奨 | 検査対象外（実装文脈の参考情報） |
| `## 関連 Issue / PR` | 推奨 | 検査対象外（既存ロジックとの関係） |

### 設計根拠

`autonomous-drive` の実装エージェント（Claude Code CLI）が必要とする最小情報を type 別に逆算した結果：

- bug-style: **何が壊れているか**（再現手順）/ **何が正しいか**（期待動作）/ **どこまで直すか**（受入条件）
- discussion-style: **なぜこの設計か**（確定軸）/ **何を変更するか**（実装スコープ）

discussion-style の "受入条件" 相当は `## L0 spec-architect 対話記録` 内の「確定軸」セクションに「選択: X」形式で記述される（個別軸が完了判定基準を兼ねる）ため、独立セクションとしては不要。

### Issue Quality Gate との整合

`crosscut-issue-quality-gate` (#46, v5.8.0) の 12 軸チェックは type 中立であり、本規格と直交する。Quality Gate は「Issue 自体の構造的健全性」を検査し、本規格は「自動 pickup の機械可読性」を検査する。両者は順次適用される（一次/二次フィルターは本規格、三次フィルターで Quality Gate）。

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
| 二次フィルター FAIL (本文不足) | label `needs-clarification` + Issue は close せず人間差し戻し（v5.10.0 で type-aware 化、`discussion` ラベル有無で必須セクションが分岐 — §Issue 本文必須セクション規格 参照） |
| 三次フィルター FAIL (out-of-scope / focus-mismatch) | 該当 label 自動付与 + 人間判断要請 |
| 実装中の致命的エラー (Claude Code CLI 失敗) | label `pickup-failed` + Issue に notice コメント + 自動フォールバックなし（人間 P4 判断、philosophy 第 4 条 + 第 7 条）|
| PR 作成後 24h 以内に変更なし | 自動 release（label `in-progress` 削除）+ notice |

## CTL との関係

CTL は本 v5.7.0 改訂で参照しない（v5.0.0 旧版で言及されていたが未稼働だった）。`autonomous_scope` 軸（v5.6.0 追加）が運用粒度を決定する。**v5.9.0 で opt-in→opt-out 反転後は `auto-merge` ラベル運用が廃止され、stop ラベル付与の有無で挙動を切り替える**：

| autonomous_scope | issue-pickup.yml | stop ラベル運用 | 後段 |
|---|---|---|---|
| full | ✅ 起動 | opt-in 領域該当時のみ `human-review-needed` 付与（v5.9.0 反転） | gemini-review + auto-merge（デフォルト走行） |
| merge_gated | △ 起動可（PR 作成まで） | ✅ 必ず `human-review-needed` 付与（明示 GO 待ち） | 人間が解除後に auto-merge |
| custom | 個別指定 | 個別 | 個別 |

opt-in / opt-out 領域の境界 SPEC は `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md` を一次情報源とする。

## 関連ドキュメント

### このスキル内 references/

- [references/issue-filter-spec.md](references/issue-filter-spec.md) — 3 段階フィルター詳細
- [references/triage-protocol.md](references/triage-protocol.md) — gemini-cli AI triage プロトコル
- [references/circuit-breaker-spec.md](references/circuit-breaker-spec.md) — 経済的暴走防止機構
- [references/implement-protocol.md](references/implement-protocol.md) — 実装プロトコル詳細（v5.0.0 から維持、v5.7.0 で gemini-cli 対応に追補）

### このスキル外

- `.claude/skills/crosscut-issue-quality-gate/SKILL.md` — Issue 品質チェック（発動契機 (d)）
- `.github/workflows/issue-pickup.yml` — dialog-harness 自身の deploy
- `templates/github-workflows/issue-pickup.yml.template` — 利用者プロジェクト展開用
- `.claude/skills/layer0-spec-architect/references/autonomous-drive-deployment.md` — deployment ガイド
- `.claude/skills/layer0-spec-architect/references/regime-assessment.md` §current_focus 判定 — pickup 判定で参照
- `.claude/skills/layer0-spec-architect/references/philosophy.md` 第 7 条 — DH AI 組織論（本 skill の位置づけ）
- `.claude/skills/layer1-autonomous-dev/SKILL.md` — 実装本体（gemini-cli が呼び出される側の規約）
- `.claude/skills/layer1-independent-reviewer/SKILL.md` — self-review 実行体
- `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md` — v5.9.0 opt-in/opt-out 境界 SPEC（一次情報源）

## バージョン

- v0.1.0 (v5.0.0 で導入、claude-code-action 前提、未稼働)
- **v0.2.0 (v5.7.0 で全面改訂)**: gemini-cli base、3 段階フィルター + AI triage + Circuit Breaker、dialog-harness 自身に deploy
- **v0.3.0 (v5.9.0 で改訂)**: opt-in→opt-out 反転、`auto-merge` ラベル運用廃止、stop ラベル方式（`do-not-merge` / `human-review-needed` / `pickup-failed`）に統合。境界 SPEC は `crosscut-autonomous-drive/references/auto-merge-boundary.md` に集約
- v5.7.x 候補: gemini-cli 実装品質観測 + 必要時の Council 起動（フォールバック判断）
