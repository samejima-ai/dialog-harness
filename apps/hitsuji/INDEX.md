# Hitsuji — 目次

ADHD 傾向のある人向け「コトの忘れもの」防止アテンションアプリ（Android Native）。

## ドキュメント（生成状態を明記）

### ✅ 本 PR で生成済み（第 1 段階）

| ファイル | 役割 |
|---|---|
| `SPEC.md` | 機能仕様（WHY / WHAT / 条件 / 優先順位 / ドメインモデル / API 連携 / ゲーミフィケーション） |
| `DONT.md` | スコープ外定義（明示的に作らないもの） |
| `REGIME.md` | モード判定結果（M2 / github_assisted / monolith / Claude Opus 4.7） |
| `DESIGN.md` | 視覚仕様（カラー・タイポ・spacing・コンポーネント・Do's and Don'ts） |
| `README.md` | プロジェクト概要 + クレジット |

### ⏳ 第 2 段階で生成予定（未生成）

| ファイル | 役割 | 状態 |
|---|---|---|
| `CLAUDE.md` | エージェントの行動ルール（L1 向け RL） | *未生成 / 第 2 段階予定* |
| `spec/subphase-manifest.md` | サブフェーズ選定結果と起動ログ | *未生成 / 第 2 段階予定* |
| `spec/state-diagrams.md` | L0-4: タスク状態 + 通知エスカレーションの Mermaid 図 | *未生成 / 第 2 段階予定* |
| `spec/invariants.feature` | L0-6: 層間不変条件（Gherkin Happy / Sad / Evil） | *未生成 / 第 2 段階予定* |
| `sensors/computational.md` | 機械的検証（lint / build / test） | *未生成 / 第 2 段階予定* |
| `sensors/inferential.md` | 推論的検証（5 層エラー検出スタック） | *未生成 / 第 2 段階予定* |
| `sensors/review-checklist.md` | 独立検証の観点 | *未生成 / 第 2 段階予定* |
| `delivery/ADR-001-subphase-scope.md` | サブフェーズ縮退判断の ADR | *未生成 / 第 2 段階予定* |
| `delivery/SELF-VERIFICATION-INITIAL.md` | §7.4 自己検証結果 | *未生成 / 第 2 段階予定* |

## 配布物・骨組みディレクトリ

- `delivery/` — L1 からの献上先（空ディレクトリで初期化済み）
- `assets/` — 共有入力の置き場（空ディレクトリで初期化済み）
- `android/` — Android Kotlin プロジェクト本体（第 2 段階で骨組みを置き、L1 が実装で埋める）
- `spec/` — L0 サブフェーズ成果物（第 2 段階で生成）
- `sensors/` — 検証センサー類（第 2 段階で生成）

## 視覚仕様への参照

視覚仕様: `DESIGN.md`
