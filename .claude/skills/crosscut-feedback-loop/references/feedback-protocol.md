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
| `flaky_rate_breach`（E2E flaky 率超過） | auto-merge ゲート / circuit-breaker | 設計層 / L0 | auto-merge 停止 + `human-review-needed` 自動付与（偽陽性 merge の構造阻止）。再試行が circuit-breaker 上限超過なら churn 打ち切り（P4）。**teeth は opt-in / 段階**（auto-merge-boundary 準拠） |
| `e2e_quarantine`（flaky 隔離台帳） | 実装層 | 設計層 | 隔離＝実装/テスト/仕様のどこかの構造歪みシグナル。一定期間で修正 or 削除。台帳は cycle 境界で代謝の WARM delta として設計層へ還流 |
| `judgment_failed`（weight_calculation 検算不一致） | crosscut-council | L0 (prompt 改訂) | F1 集計で頻発時に L0 へ自動還流（PR1 では手動）。本還流種別は本ファイル末尾 §F1 振り返り儀式での weight_calculation 監査 を参照 |

## E2E 代謝サイクルとの接続（v5.24.0）

`flaky_rate_breach` / `e2e_quarantine` は E2E 情報代謝サイクル（`../../layer0-reindex-librarian/references/metabolism-regime.md` §7、
`../../layer1-autonomous-dev/references/e2e-best-practices.md` §9）の **④還流フェーズ**にあたる。run 要約（WARM）の
集計から flaky 率・隔離台帳を検出し、本マトリクスで振り分ける。これは v5.23.0 で「接続地図のみ」とした teeth の本体化だが、
**強制連動（auto-merge.yml の変更）は opt-in / 段階導入**とする（実 E2E 運用データが貯まるまで閾値を固定しない＝
metabolism 設計自身が推奨する Dry-run 精神。境界は `../../crosscut-autonomous-drive/references/auto-merge-boundary.md`）。

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

## F1 振り返り儀式での weight_calculation 監査（PR1 新規）

直近 N 件の COUNCIL-LOG エントリから `weight_calculation` の整合性を集計し、
Judgment Agent の規定逸脱頻度を可視化する。設計契機: COUNCIL-LOG
`council-2026-04-29T18-00-00Z-d1m4n5` で発生した weight 分割逸脱を、
**振り返り儀式で機械的に検出可能にする**ための監査経路。

### 監査手順

1. `.claude/skills/crosscut-council/history/COUNCIL-LOG.md` を対象に、
   F1 期間（週次、直近 7 日）のエントリを抽出
   （`history/COUNCIL-LOG.md` 等のリポジトリルート COUNCIL-LOG が存在する場合はそれも対象に追加）
2. 各エントリの `weight_calculation.scores` を `weighted_score` 降順で並べ替え、
   上位 2 件の差分から最大 stance を再計算する
   （例: `sorted(scores, key=lambda s: s["weighted_score"], reverse=True)` を用い、
   1 位と 2 位の `weighted_score` 差が `< 0.01` なら tie と判定）。
   - tie でない場合: 1 位の stance がエントリ内の `max_score_stance` と一致し、
     かつ `recommended` がその `max_score_stance` で始まることを確認
   - tie の場合: `max_score_stance=null` かつ `tie_break_applied=true` を確認し、
     このエントリでは `recommended` 接頭辞照合をスキップ
3. 以下を集計:
   - **一致率**: tie でないエントリのうち、`recommended` が `max_score_stance` で始まるエントリの割合
   - **third_way_excluded 出現率**: `third_way_excluded` が空でないエントリの割合
   - **retry 発生率**: `weight_calculation_retry_count > 0` のエントリの割合
   - **judgment_failed 件数**: `status = judgment_failed` のエントリ数
4. 集計結果を `delivery/F1-COUNCIL-AUDIT-<YYYY-WW>.md` に記録
5. 一致率 < 95% の場合は L0 spec-architect に還流（`judgment-agent.md` prompt 改訂候補、
   上記マトリクス §`judgment_failed` の還流フロー）

### 集計フォーマット例

```markdown
### F1 Council Audit (週 2026-W18)
- 対象エントリ数: 12
- recommended ↔ max_score_stance 一致率: 11/12 = 91.7%
- 不一致詳細:
  - council-2026-04-29T18-00-00Z-d1m4n5: max="Option C" / recommended="Option A 採用..."
    （事後合理化補注済み、append-only 例外条項 post_hoc_rationalization_note）
- third_way_excluded 出現率: 1/12 = 8.3%（哲学者発のみ）
- retry 発生率: 0/12 = 0%
- judgment_failed: 0 件
- 還流推奨: 一致率 < 95% のため judgment-agent.md prompt の few-shot 強化を検討
```

### 遡及適用の扱い

施行時点（PR1 マージ）以前のエントリで `weight_calculation` フィールドが未記入のものは、
`compute_weight_scores` を `persona_summary` から再構成して試算するが、
集計結果には「**遡及試算**」マーカーを付ける（COUNCIL-LOG 例外条項施行前事象として
F1 集計の分母から除外可能）。
