# Hitsuji — 目次

ADHD 傾向のある人向け「コトの忘れもの」防止アテンションアプリ（Android Native）。

## ドキュメント

### コア仕様（第 1 段階）

| ファイル | 役割 |
|---|---|
| `SPEC.md` | 機能仕様（WHY / WHAT / 条件 / 優先順位 / ドメインモデル / API 連携 / ゲーミフィケーション） |
| `DONT.md` | スコープ外定義（明示的に作らないもの） |
| `REGIME.md` | モード判定結果（M2 / github_assisted / monolith / Claude Opus 4.7） |
| `DESIGN.md` | 視覚仕様（カラー・タイポ・spacing・コンポーネント・Do's and Don'ts） |
| `README.md` | プロジェクト概要 + クレジット |

### 開発環境（第 2 段階）

| ファイル | 役割 |
|---|---|
| `CLAUDE.md` | エージェントの行動ルール（L1 向け RL） |
| `spec/subphase-manifest.md` | サブフェーズ選定結果と起動ログ |
| `spec/state-diagrams.md` | L0-4: タスク状態 + 通知エスカレーションの Mermaid 図 |
| `spec/invariants.feature` | L0-6: 層間不変条件（Gherkin Happy / Sad / Evil） |
| `sensors/computational.md` | 機械的検証（lint / build / test） |
| `sensors/inferential.md` | 推論的検証（5 層エラー検出スタック） |
| `sensors/review-checklist.md` | 独立検証の観点 A〜H |
| `delivery/ADR-001-subphase-scope.md` | サブフェーズ縮退判断の ADR |
| `delivery/SELF-VERIFICATION-INITIAL.md` | §7.4 自己検証結果 |

## ディレクトリ構成

- `delivery/` — L1 からの献上先（ADR-001 / SELF-VERIFICATION-INITIAL 配置済）
- `assets/` — 共有入力の置き場（空ディレクトリで初期化済み）
- `android/` — Android Kotlin プロジェクト scaffold（settings/build/Manifest/MainActivity placeholder 配置済、L1 が本実装で埋める）
- `spec/` — L0 サブフェーズ成果物（subphase-manifest / state-diagrams / invariants.feature 配置済）
- `sensors/` — 検証センサー類（computational / inferential / review-checklist 配置済）

## 視覚仕様への参照

視覚仕様: `DESIGN.md`
