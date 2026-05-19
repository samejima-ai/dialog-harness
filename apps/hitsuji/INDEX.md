# Hitsuji — 目次

ADHD 傾向のある人向け「コトの忘れもの」防止アテンションアプリ（Android Native）。

## ドキュメント

| ファイル | 役割 |
|---|---|
| `SPEC.md` | 機能仕様（WHY / WHAT / 条件 / 優先順位 / ドメインモデル / API 連携 / ゲーミフィケーション） |
| `DONT.md` | スコープ外定義（明示的に作らないもの） |
| `REGIME.md` | モード判定結果（M2 / github_assisted / monolith / Claude Opus 4.7） |
| `DESIGN.md` | 視覚仕様（カラー・タイポ・spacing・コンポーネント・Do's and Don'ts） |
| `CLAUDE.md` | エージェントの行動ルール（第 2 段階で生成） |
| `README.md` | プロジェクト概要 + クレジット |

## サブフェーズ成果物（`spec/`）

| ファイル | 役割 |
|---|---|
| `spec/subphase-manifest.md` | サブフェーズ選定結果と起動ログ |
| `spec/state-diagrams.md` | L0-4: タスク状態 + 通知エスカレーションの Mermaid 図 |
| `spec/invariants.feature` | L0-6: 層間不変条件（Gherkin Happy / Sad / Evil） |

## センサー（`sensors/`）

| ファイル | 役割 |
|---|---|
| `sensors/computational.md` | 機械的検証（lint / build / test） |
| `sensors/inferential.md` | 推論的検証（5 層エラー検出スタック） |
| `sensors/review-checklist.md` | 独立検証の観点 |

## 配布物・履歴

- `delivery/` — L1 からの献上先
- `assets/` — 共有入力の置き場
- `android/` — Android Kotlin プロジェクト本体（L1 が実装で埋める）

## 視覚仕様への参照

視覚仕様: `DESIGN.md`
