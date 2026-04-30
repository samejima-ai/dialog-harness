---
name: crosscut-issue-implementer
dimension: D4
description: >
  GitHub Issue を起点に CC 実装を起動する横断機構（仕様2、v5.0.0 追加）。
  ローカル worktree または GitHub Actions 経由（claude-code-action 公式採用）で実行。
  CTL 連動で実行手段と並列度が変化する。
  Issue assigned / label `ready-for-ai` 付与で自動発動、または明示コマンドで起動。
  github_assisted 以上で有効、local_only では無効。
---

# Issue Implementer

## 発動条件

- Issue が assigned された、または label `ready-for-ai` が付与された
- REGIME.md の `dev_mode` + CTL に応じて実行モードが決定される

## 処理フロー

1. Issue 内容を読込（タイトル / 本文 / 関連 SPEC.md セクション）
2. CTL を確認して実行モード決定（`references/implement-protocol.md` 参照）
   - CTL-0/1: ローカル worktree で `layer1-autonomous-dev` 起動（手動 / 監視あり）
   - CTL-2/3: GitHub Actions 経由（claude-code-action 公式）
3. 実装実行（`layer1-autonomous-dev` の規約に従う）
4. PR 作成（タイトル: `feat(<area>): <issue-title>` 等、label `from-ai-impl` 付与）
5. `layer1-independent-reviewer` による self-review 実行
6. `history/CHANGELOG.md` にレベル A 追記

## claude-code-action 採用注記

GitHub Actions 経由での実装は Anthropic 公式の [claude-code-action](https://github.com/anthropics/claude-code-action) を採用する。
ワークフロー雛形は `templates/.github/workflows/issue-to-impl.yml`。
実装時点で公式リポジトリの最新バージョンを確認すること（`<latest>` プレースホルダを差し替え）。

## CTL 別動作（要約）

| CTL | 実行手段 | レビュー | auto-merge |
|---|---|---|---|
| CTL-0 | ローカル worktree | 人間レビュー必須 | × |
| CTL-1 | Actions 経由 | 人間レビュー必須 | × |
| CTL-2 | Actions 経由 | self-review pass で OK | ○（CI 全通過時のみ） |
| CTL-3 | Actions 経由 | self-review のみ | ○ |

詳細は `references/implement-protocol.md`。

## 関連

- `references/implement-protocol.md` — CTL 別動作詳細
- `layer1-autonomous-dev/SKILL.md` — 実装本体
- `layer1-independent-reviewer/SKILL.md` — self-review 実行体
- `templates/.github/workflows/issue-to-impl.yml` — 自動化雛形
- `templates/.github/workflows/auto-merge.yml` — CTL ≥ 2 + CI 全通過時のみ発動
