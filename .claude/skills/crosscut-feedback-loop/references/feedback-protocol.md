# Feedback Protocol

`crosscut-feedback-loop` の CTL 別動作詳細・還流先判定詳細。spec §3.2.7 を本体化。

## モード別動作

### github_assisted モード（CTL 不問）

```
全て手動還流
```

検出された問題は `delivery/DRIFT-REPORT.md` 等に記録され、人間が手動で Issue 作成 / SPEC 修正 / 実装層差戻しを行う。

### github_autonomous モード × CTL 別

| CTL | drift | 思想違反 | 形式 FAIL |
|---|---|---|---|
| CTL-0 | 手動（assisted 相当） | 該当なし | 自動修復試行（既存 L1 自己修復） |
| CTL-1 | 自動還流（Issue 生成） | 人間確認 | 自動修復 |
| CTL-2 | 自動還流 + Council 判定 | Council 経由で自動還流 | 自動修復 |
| CTL-3 | 完全自動（事後献上のみ） | 完全自動（事後献上のみ） | 自動修復 |

## 還流先の判定マトリクス

| 検出種別 | 第一還流先 | 補助還流先 | アクション |
|---|---|---|---|
| `formal_fail`（型 / lint / test） | 実装層 | — | `layer1-autonomous-dev` の自己修復起動 |
| `drift` | 設計層 | 実装層 | `crosscut-issue-dispatcher` 経由で SPEC 追記 Issue 生成 |
| `philosophy_violation` | crosscut-council | 設計層 / L0 | Council 判定 → 結果に応じて SPEC 修正 or L0 対話復帰 |
| `interaction_cost_breach` | 実装層 | L0 | UX 修正 PR 自動作成、改善されない場合は L0 対話で要件再確認 |
| `dont_violation` | 実装層 | crosscut-council | 即時 revert 候補。Council で重大度判定 |

## 還流処理フロー（共通）

1. 検出種別を確認（`delivery/DRIFT-REPORT.md` / VERIFICATION.md / sensor 出力 から）
2. 還流先を上記マトリクスから決定
3. CTL に応じて自動 / 人間確認の分岐
4. 還流先へ通知
   - 設計層への還流 → `crosscut-issue-dispatcher` 起動
   - 実装層への還流 → `layer1-autonomous-dev` の差戻し起動
   - L0 への還流 → `delivery/UPGRADE-CONFLICT.md` に記載 + 人間献上
5. 還流結果を `history/CHANGELOG.md` にレベル A 追記
6. 重大事案（CTL ≥ 2 で Council `judgment_confidence < 0.5` 等）は `delivery/UPGRADE-CONFLICT.md` 経由で人間献上

## philosophy_violation の v5.0.0 取り扱い

`crosscut-verifier-philosophy` が placeholder のため、v5.0.0 では philosophy_violation 種別の還流要求は届かない。本 skill で受信した場合は「未実装エラー」として人間献上する（v5.1.0 で接続予定）。

## CTL ≥ 2 での Council 判定

drift の重大度判定や還流先の妥当性確認のために `crosscut-council` を起動する。

入力構造：

```yaml
context: 検出された drift / philosophy_violation の詳細
options:
  - 還流先 A（マトリクス第一還流先）
  - 還流先 B（補助還流先）
  - 還流せず人間献上
question_to_answer: 「この問題をどう還流すべきか」
source_skill: crosscut-feedback-loop
category: maintenance
```

`recommended` で `judgment_confidence ≥ 0.5` なら Council 判断通り還流。それ以外は人間献上。

## CHANGELOG 記録例

```markdown
### Feedback 還流（YYYY-MM-DD HH:MM）
- 種別: drift (medium)
- 元: PR #123 の crosscut-verifier-drift 検出
- 還流先: 設計層（SPEC.md F3 セクション追記）
- アクション: crosscut-issue-dispatcher 経由で Issue #126 自動生成
- CTL: 2、Council 事前検証: PASS（confidence 0.71）
```
