---
name: crosscut-verifier-drift
dimension: D4
description: >
  実装が SPEC/ADR から逸脱していないかを検証する横断機構（仕様3-drift、v5.0.0 追加）。
  CTL ≥ 1 で発動。CI 上で自動実行され、PR 作成時の自動 drift 検出を担う。
  「drift チェック」「SPEC 逸脱検出」「実装が仕様から離れていないか確認」
  等の発話でも起動。
  既存の 5 層エラー検出スタックを補完する追加層として位置づけられる。
---

# Drift Verifier

## 発動条件

- PR 作成時の CI 実行（雛形は dialog-harness リポジトリ `templates/.github/workflows/spec-drift.yml`。利用者プロジェクト (D3) には同梱されず、autonomous-drive deployment で展開される upstream テンプレートを参照）
- REGIME.md の CTL ≥ 1
- 明示コマンド（「drift チェック」等）

## 処理フロー

1. PR 差分を取得（変更ファイル / 追加行 / 削除行）
2. SPEC.md / ADR と照合
   - 機能の追加が SPEC.md に記載されているか
   - 削除が ADR で承認されているか
   - 制約違反（DONT.md 抵触）が無いか
3. drift 検出時：
   - 種別を分類（仕様未記載追加 / 削除未承認 / DONT 抵触）
   - 重大度判定（severity: low / medium / high）
4. `crosscut-feedback-loop` へ還流要求（重大度に応じた還流先決定）
5. PR コメントに drift 報告を追記

## 既存検出スタックとの位置関係

5 層エラー検出スタック（philosophy.md §4 / inferential-sensor-v2.md）を補完する追加層：

| 層 | 対象 |
|---|---|
| Shift Left 基盤 | 型 / lint / フォーマット |
| 第1層 計算的センサー | 単体 / 統合テスト |
| 第2層 E2E 機械検証 | Playwright 等 |
| 第3層 Interaction Cost | UX 測定 |
| 第4層 推論的センサー | 「仕様に合う・動く・使える」 |
| 第5層 独立検証 | layer1-independent-reviewer |
| **追加層 drift** | **SPEC/ADR との乖離（本 skill）** |
| 追加層 思想 | 5 本柱整合（crosscut-verifier-philosophy、v5.1.0） |

## 関連

- `references/verify-protocol.md` — CTL 別動作詳細
- `crosscut-feedback-loop/SKILL.md` — 還流先
- `templates/.github/workflows/spec-drift.yml` — 自動化雛形（dialog-harness リポジトリのテンプレート。利用者プロジェクトに同梱されず、autonomous-drive deployment 経由で `.github/workflows/` へ展開）
