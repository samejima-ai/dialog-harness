---
name: crosscut-issue-dispatcher
dimension: D4
description: >
  SPEC/ADR 差分から GitHub Issue を生成する横断機構（仕様1、v5.0.0 追加）。
  REGIME.md の dev_mode が github_assisted 以上で発動。CTL 連動で自動化度が変化する。
  「Issue にして」「Issue 射出して」「タスク分解して」「SPEC を Issue に落として」
  等の発話、または commit hook から起動。
  local_only モードでは無効。
---

# Issue Dispatcher

## 発動条件

- REGIME.md の `dev_mode` が `github_assisted` 以上
- 明示コマンド（「Issue にして」等）または commit hook 経由
- CTL に応じて自動化度が変化（`crosscut-council/references/ctl-calculation.md` 参照）

`local_only` モードでは発動しない（環境的に GitHub が無い）。

## 処理フロー

1. SPEC.md / ADR の最新差分を取得（最後の Issue 射出時点との比較）
2. REGIME.md の CTL を確認 → 動作モード決定（CTL 別動作は `references/dispatch-protocol.md` 参照）
3. Issue 分解（最大 5、REGIME.md で上書き可能）
4. CTL ≥ 2 の場合：`crosscut-council` 事前検証を発動
5. `crosscut-issue-quality-gate` による品質チェック（v5.8.0 追加、発動契機 (a)）
6. GitHub Issue 作成（label: `ready-for-ai` 等を付与）
7. `history/CHANGELOG.md` にレベル A（自動承認）で追記

## 暴走防止

- 1 commit あたり最大 5 Issue（暫定値、REGIME.md で `## issue_dispatch_limit` として上書き可能）
- CTL ≥ 2 で `crosscut-council` 事前検証を発動
- 異常系（差分過大・SPEC 矛盾・API レート超過 等）は処理中断 → 人間に献上

## 関連

- `references/dispatch-protocol.md` — CTL 別動作詳細
- `crosscut-council/SKILL.md` — 事前検証時の判定機構
- `crosscut-issue-quality-gate/SKILL.md` — Issue 品質チェック（発動契機 (a)）
- `templates/.github/workflows/issue-dispatch.yml` — 自動化雛形（dialog-harness リポジトリのテンプレート。利用者プロジェクトに同梱されず、autonomous-drive deployment 経由で `.github/workflows/` へ展開）
