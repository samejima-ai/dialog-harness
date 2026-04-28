# Implement Protocol

`crosscut-issue-implementer` の CTL 別動作詳細。spec §3.2.5 を本体化。

## モード別動作

### github_assisted モード（CTL 不問）

```
ローカル worktree で CC 手動実行
  ↓
PR 作成 → ユーザーレビュー → Merge
```

`layer1-autonomous-dev` を手動起動 / 監視あり。auto-merge は発動しない。

### github_autonomous モード × CTL 別

| CTL | 実行手段 | レビュー | auto-merge | 並列度 |
|---|---|---|---|---|
| CTL-0 | ローカル worktree（assisted 相当） | 人間レビュー必須 | × | 1 |
| CTL-1 | GitHub Actions 経由（claude-code-action） | 人間レビュー必須 | × | 1-2 |
| CTL-2 | GitHub Actions 経由 | self-review pass で OK | ○（CI 全通過時のみ） | 2-3 |
| CTL-3 | GitHub Actions 経由 | self-review のみ | ○ | 並列上限なし（リソース次第） |

並列度は `REGIME.md` の `## parallel_impl_limit` で上書き可能。

## 実行手段：claude-code-action（CTL ≥ 1）

Anthropic 公式の [claude-code-action](https://github.com/anthropics/claude-code-action) を採用。
ワークフロー雛形は `templates/.github/workflows/issue-to-impl.yml`。

### バージョンプレースホルダ

雛形では `<latest>` プレースホルダで記述。実装時点で公式リポジトリの最新版を確認し、ピン止め推奨。

### 必要な GitHub Secrets

- `ANTHROPIC_API_KEY`（必須）
- `GITHUB_TOKEN`（自動付与、PR 操作用）

## self-review（PR 作成後）

`layer1-independent-reviewer` を起動して `delivery/VERIFICATION.md` を生成。

| CTL | self-review 結果の扱い |
|---|---|
| CTL-0/1 | 参考情報。最終判断は人間 |
| CTL-2 | PASS なら auto-merge 候補、FAIL なら自動差戻し |
| CTL-3 | PASS なら無条件 auto-merge、FAIL なら自動差戻し + Council 起動 |

## auto-merge 発動条件（CTL ≥ 2）

`templates/.github/workflows/auto-merge.yml` で実装。発動条件：

1. PR に `ctl-2-or-higher` label が付いている
2. self-review が PASS（`delivery/VERIFICATION.md` の判定が PASS）
3. CI 全 job が green（basic-ci, e2e-ci, spec-drift, interaction-cost）
4. PR 作成者が claude-code-action（人間 PR は対象外）

これらすべて満たした場合のみ `gh pr merge --auto --squash` を実行。

## Issue → 実装失敗時の挙動

CI 連続失敗・self-review 連続 FAIL 等で実装が完遂しない場合：

| CTL | 挙動 |
|---|---|
| CTL-0/1 | Issue に失敗コメント追記、人間判断待ち |
| CTL-2 | 3 連続失敗で `auto-degrade.yml` トリガ（autonomous → assisted に自動降格） |
| CTL-3 | 同上 + Council 起動（仕様自体に問題ないか判定） |

詳細は `templates/.github/workflows/auto-degrade.yml` 参照。

## CHANGELOG 記録

各 PR 作成・マージごとに `history/CHANGELOG.md` にレベル A 追記。
