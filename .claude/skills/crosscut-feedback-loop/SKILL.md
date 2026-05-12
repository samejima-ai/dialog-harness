---
name: crosscut-feedback-loop
dimension: D4
description: >
  検証層（drift verifier / philosophy verifier / 5 層検出スタック）で発覚した問題を、
  種別判定して設計層・実装層・L0 へルーティングする横断機構。
  「drift verifier の指摘を SPEC に戻したい」「形式 FAIL と drift が両方出た時の還流先」
  「思想違反検出後どこに還流」「自動 merge 後に drift 検出した、P3 に投げ返す手順」
  「verifier-philosophy の placeholder fallback」「CTL 0 の local_only モードでの還流動作」
  等、検証結果の還流先振り分けに関する発話で本スキルの起動を必ず検討する。
  drift は dispatcher 経由 Issue 化、思想違反は Council 経由、形式 FAIL は L1 に再献上、
  CTL に応じて自動化度が変化（CTL ≥ 1 から自動還流、CTL 0 では人間に献上のみ）。
  「drift チェック走らせて」（→ verifier-drift）「Issue にして」（→ issue-dispatcher）
  「振り返り儀式」（→ spec-architect）「Council に諮る」（→ council）との混同を避ける。
  本 skill は仕様 1〜3 の検証結果を受けて起動される下流機構であり、検証自体は行わない。
---

# Feedback Loop

## 発動条件

- 検証層（`crosscut-verifier-drift` / `crosscut-verifier-philosophy` / 5 層検出スタック）からの還流要求
- REGIME.md の `dev_mode` + CTL に応じて還流手段が変化
- 明示コマンド（「drift を Issue 化」等）

## 処理フロー

1. 検出種別を確認（formal_fail / drift / philosophy_violation / interaction_cost_breach 等）
2. 還流先を決定（種別 × CTL × dev_mode）
3. 還流先へ通知
   - 形式 FAIL → 実装層（自己修復）
   - drift → 設計層（自動 Issue 生成、`crosscut-issue-dispatcher` 経由）
   - 思想 FAIL → `crosscut-council` 発動 → 設計層 or L0
   - interaction_cost 超過 → 実装層（UX 修正）or L0（要件再確認）
4. 還流結果を `history/CHANGELOG.md` にレベル A で追記
5. 重大事案（人間判断必要）は `delivery/UPGRADE-CONFLICT.md` に記載して人間献上

## 還流先の判定マトリクス

| 検出種別 | 第一還流先 | 補助還流先 | CTL 影響 |
|---|---|---|---|
| formal_fail（型 / lint / test） | 実装層 | — | CTL 関与なし（即時自動修復） |
| drift | 設計層（Issue 生成） | 実装層（コード修正） | CTL ≥ 1 で自動還流、< 1 で人間確認 |
| philosophy_violation | crosscut-council | 設計層 / L0 | CTL ≥ 2 で自動 Council 発動 |
| interaction_cost_breach | 実装層 | L0（仕様再確認） | CTL 関与なし |

詳細は `references/feedback-protocol.md`。

## CTL 別動作（要約）

| CTL | drift | 思想 |
|---|---|---|
| CTL-0 | 手動還流 | （v5.0.0 placeholder） |
| CTL-1 | drift 自動還流、思想は人間確認 | （v5.0.0 placeholder） |
| CTL-2 | drift + 思想自動還流（Council 判定） | v5.1.0 で自動 |
| CTL-3 | 完全自動（事後献上のみ） | v5.1.0 で自動 |

## 関連

- `references/feedback-protocol.md` — CTL 別動作詳細・還流先判定詳細
- `crosscut-verifier-drift/SKILL.md` — drift 検出元
- `crosscut-verifier-philosophy/SKILL.md` — 思想検証元（v5.1.0）
- `crosscut-issue-dispatcher/SKILL.md` — drift → Issue 還流の実装
- `crosscut-council/SKILL.md` — 思想 FAIL 時の判定機構
- `templates/.github/workflows/drift-feedback.yml` — 自動化雛形（dialog-harness リポジトリのテンプレート。利用者プロジェクトに同梱されず、autonomous-drive deployment 経由で `.github/workflows/` へ展開）
