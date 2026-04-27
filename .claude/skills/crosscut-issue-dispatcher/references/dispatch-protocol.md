# Dispatch Protocol

`crosscut-issue-dispatcher` の CTL 別動作詳細。spec §3.2.4 を本体化。

## モード別動作

### github_assisted モード（CTL 不問）

```
明示コマンド「Issue にして」
  ↓
L1（spec-architect）が SPEC/ADR 差分から最大 5 Issue 生成
  ↓
ユーザー確認 → GitHub Issue 作成
```

ユーザー確認は必須。CTL は参照しない（assisted モードは CTL-0 相当の動作）。

### github_autonomous モード × CTL 別

| CTL | 動作 |
|---|---|
| CTL-0 | ユーザー確認必須（assisted 相当の動作にフォールバック） |
| CTL-1 | 軽微な Issue は自動作成、重要（label `priority:high` 等）は人間確認 |
| CTL-2 | 完全自動 + `crosscut-council` 事前検証必須 |
| CTL-3 | 完全自動（事前検証も省略可能、事後献上のみ） |

「軽微 / 重要」の判定は SPEC.md の Priority（critical / standard / cosmetic）に従う：
- critical → 重要（人間確認、CTL-1 まで）
- standard → 軽微（CTL-1 で自動）
- cosmetic → 軽微（CTL-1 で自動）

## 暴走防止

- 1 commit あたり最大 5 Issue（暫定値、`REGIME.md` の `## issue_dispatch_limit` で上書き可能）
- CTL ≥ 2 で `crosscut-council` 事前検証発動（生成内容の妥当性 + 重複検知 + DONT 抵触チェック）
- 異常時（差分過大 / SPEC 矛盾 / GitHub API レート超過）は処理中断 → `delivery/UPGRADE-CONFLICT.md` 経由で人間献上

## Council 事前検証（CTL ≥ 2）

入力構造：

```yaml
context: SPEC/ADR 差分の概要 + 生成予定 Issue リスト
options:
  - 生成案 A（提案された Issue 群）
  - 生成案 B（一部削減した代替案）
  - 生成しない（差分が小さすぎる等の判断）
question_to_answer: 「この Issue 群を生成すべきか、修正すべきか、保留すべきか」
source_skill: crosscut-issue-dispatcher
category: implementation
```

Council judgment が `recommended: 生成案 A` で `judgment_confidence ≥ 0.5` なら生成続行。
それ以外は人間献上。

## CHANGELOG 記録

各 Issue 射出ごとに `history/CHANGELOG.md` にレベル A（自動承認）で追記：

```markdown
### Issue 射出（YYYY-MM-DD HH:MM）
- mode: github_autonomous, ctl: 2
- 差分: SPEC.md F3 セクション追加、ADR-012 採用
- 生成 Issue: #45, #46, #47
- Council 事前検証: PASS（confidence 0.78）
```
