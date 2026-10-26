# Subphase Manifest — Hitsuji L0

L0 サブフェーズ判定の起動ログと成果物配置の一覧。

## 判定 5 問

| # | 質問 | 回答 | 起動判定 |
|---|---|---|---|
| S1 | データ保存？ DB 使う？ | YES (Room/SQLite) | L0-2 ドメインモデル起動候補 |
| S2 | 外部 API とつなぐ？ | YES (Android SDK + Google Calendar) | L0-3 API 契約起動候補 |
| S3 | 画面 / 遷移は複雑？ | 中（4〜5 画面、通知エスカレーション）| L0-4 状態遷移起動 |
| S4 | 複数ユーザー権限？ | NO | L0-5 スキップ |
| S5 | 時間経過で状態自動遷移？ | YES（通知エスカレーション）| L0-6 不変条件起動 |

## 起動 / 縮退の最終結果

| サブフェーズ | モード | 成果物 | 縮退理由 |
|---|---|---|---|
| **L0-2** ドメインモデル | 縮退（SPEC.md 内） | `SPEC.md` `## ドメインモデル` | Kotlin Native のため TS+Zod 不適合 → ADR-001 |
| **L0-3** API 契約 | 縮退（SPEC.md 内） | `SPEC.md` `## 外部 API 連携` | 同上、TypeSpec 不適合 → ADR-001 |
| **L0-4** 状態遷移 | 簡易（Mermaid のみ） | `spec/state-diagrams.md` | XState JSON 機械化は MVP では過剰 → ADR-001 |
| **L0-5** 認可 | **スキップ** | — | 単一ユーザー前提（DONT 4） |
| **L0-6** 不変条件 | 完全実施 | `spec/invariants.feature` | 通知信頼性は致命的、Evil 系で守る必要 |

詳細根拠は `delivery/ADR-001-subphase-scope.md` を参照。

## DESIGN.md 起動判定（§3.6）

UI ありプロジェクト → **起動確定**。
成果物: `DESIGN.md`

## 横断機構の発動状態

| 横断機構 | 状態 | 根拠 |
|---|---|---|
| crosscut-issue-dispatcher | inactive | dev_mode=github_assisted (CTL=0)、手動 Issue 化のみ |
| crosscut-issue-implementer | inactive | autonomous_scope ≠ full |
| crosscut-autonomous-drive | inactive | dev_mode ≠ autonomous |
| crosscut-verifier-drift | inactive | CTL=0 |
| crosscut-verifier-philosophy | inactive | v5.0.0+ では発動禁止 |
| crosscut-feedback-loop | inactive (manual) | CTL=0、人間献上経由のみ |
| crosscut-council | on-demand | 実装時の judgment 必要時に L1 から起動 |
| crosscut-hook-observer | optional | 観測層、必須でない |
| crosscut-continuous-learning | inactive | CTL=0 |

## 起動ログ

- 2026-05-19 03:22 — REGIME 判定（M2 / github_assisted / monolith）確定
- 2026-05-19 03:24 — SPEC.md / DONT.md 生成（第 1 段階）
- 2026-05-19 03:25 — REGIME.md 生成、persona=sheep-navigator 適用
- 2026-05-19 03:26 — DESIGN.md / INDEX.md / README.md 生成（第 1 段階完了）
- 2026-05-19 03:30 — 第 1 段階人間レビュー（6 確認ポイント提示）
- 2026-05-19 03:32 — Copilot 自動レビュー 4 件指摘 → 即時修正
- 2026-05-19 03:xx — 「全部 OK」承認 → 第 2 段階着手
- 2026-05-19 03:xx — ADR-001 / state-diagrams / invariants / sensors / CLAUDE 生成
- 2026-05-19 03:xx — android scaffold 配置、§7.4 自己検証実施
