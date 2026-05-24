# auto-merge boundary — opt-in / opt-out 領域の不変分類

v5.9.0 で auto-merge の人間承認モデルを **opt-in（明示 GO ラベル）から opt-out（暗黙オート + stop ラベル）に反転** した。本ファイルは反転の安全弁として、**AI が境界を動かせない不変仕様** を定義する。

Council 諮問 `council-2026-05-06T08:30:00Z-amrev1`（unanimous C ハイブリッド、judgment_confidence 0.80）の minority_opinion 由来 4 実装要件のうち **「(1) 境界の SPEC 不変化」** に対応。

## 設計原則

1. **デフォルト = auto-merge 走行**（opt-out）
2. **stop ラベル付与で skip**: `do-not-merge` / `human-review-needed` / `pickup-failed` のいずれか
3. **opt-in 領域に該当する変更は AI が対話中に必ず stop ラベル付与確認を発話する**
4. 本ファイルの分類表は SPEC であり、AI が Issue/PR 単位で動かせない（philosophy.md §3 情報純度原則の延長）

## opt-in 領域（stop ラベル付与確認が必須）

該当する変更は **PR 作成前に人間に発話確認** し、`human-review-needed` ラベルを付与する。

| カテゴリ | 該当パス / 状況 | 推奨ラベル |
|----------|----------------|-----------|
| **philosophy 改修** | `.claude/skills/layer0-spec-architect/references/philosophy.md` の追記・改訂 | `human-review-needed` |
| **harness-verifier 自己改修** | `harness-verifier/**`（reports/ 配下の月次レポート自動生成は除外） | `human-review-needed` |
| **不可逆操作** | DB migration、データ削除、外部 API 破壊変更、secrets 削除、branch 強制 push | `do-not-merge`（差し戻し）or `human-review-needed` |
| **DONT.md 抵触** | プロジェクトの `DONT.md` で禁止された領域への侵入 | `do-not-merge`（差し戻し） |
| **Council 起動 + 低 confidence** | Council 諮問が起動し `judgment_confidence < 0.5` で escalate | `human-review-needed` |
| **複数 SPEC ファイル横断改修** | 3 ファイル以上の `.claude/skills/*/SKILL.md` または references/*.md を同 PR で改修 | `human-review-needed` |
| **autonomous-drive workflow 自身の改修** | `.github/workflows/auto-merge.yml` `.github/workflows/issue-pickup.yml` `.github/workflows/gemini-review.yml` の改修 | `human-review-needed` |
| **本ファイル自身の改修** | 本 `auto-merge-boundary.md` の改修（メタ自己参照） | `human-review-needed` |

## opt-out 領域（暗黙オート、stop ラベル不要）

以下の変更は AI が無言で PR を作成し、auto-merge.yml 既定の verifier 群（harness-verify / gemini-review）が SUCCESS を返せば自動 merge される。

| カテゴリ | 該当例 |
|----------|--------|
| **単一機能追加 / bug fix** | 1 つの skill 内に閉じる feature / fix |
| **typo / format 修正** | 全角・半角括弧統一、誤字、改行・インデント |
| **documentation 更新** | `history/**`（CHANGELOG / INTENT / REGIME-LOG / COUNCIL-LOG）、`delivery/**` |
| **単一 skill SPEC 追記** | 1 ファイル内に閉じる SPEC / references 追加 |
| **リファクタ（動作不変）** | コード移動、定数抽出、命名変更で動作変更を伴わないもの |
| **monthly report 自動生成** | `harness-verifier/reports/<YYYY-MM>.md`（cron 経路で `harness-verify.yml` が自己 commit） |

## stop ラベル定義

| ラベル | 意味 | 付与主体 | 解除方針 |
|--------|------|---------|---------|
| `do-not-merge` | 永続ブロック（差し戻し） | 人間（明示）/ AI（DONT.md 抵触検知） | 人間判断のみ、AI 自動解除禁止 |
| `human-review-needed` | 人間レビュー待ちで一時停止 | AI（opt-in 領域検知）/ Council（confidence<0.5）/ 人間 | 人間レビュー後に手動解除 → auto-merge 再評価 |
| `pickup-failed` | issue-pickup.yml 実装失敗 | issue-pickup.yml | 人間 P4 判断、`ready-for-ai` 再付与で再 trigger |
| `circuit-broken` | Circuit Breaker 上限到達 | issue-pickup.yml | 翌日／翌月の自然解除 or 人間判断 |

## review 応答ループの終端境界（loop termination）

自動レビュアー（`claude-review.yml` / `gemini-review.yml`）の指摘に応答する AI は、指摘の **重大度** で応答を分岐し、自己彫琢ループ（churn）に陥らない。本境界は §stop ラベル定義と連結し、ループの出口を既存ラベルに着地させる。

| 重大度 | 定義 | 応答 | 出口 |
|--------|------|------|------|
| **重大** | merge をブロックする指摘、または §opt-in 領域該当（不可逆操作 / DONT.md 抵触 / Council `judgment_confidence < 0.5` / RL 外項目 / H 区分該当）のいずれか | 修正 → 再レビューを **解決までループ** | 解決＝ループ終了。スコープ外 / 解決不能なら `human-review-needed` を付与して **人間献上** |
| **軽微** | merge をブロックしない非ブロッキング指摘（観点メモ・整流余地・将来余地） | **最大 1 回**の微修正で終了 | 修正が生む新たな軽微 nit は追わない（記録のみ）。opt-out 領域ならそのまま auto-merge 走行 |

### 終端規則（churn 防止）

- **判定主体と信号**: 重大度は応答エージェント（babysit / autonomous-drive 経路）が判定する。信号はレビュアー出力の既存フィールド——merge ブロックの有無 / `human_escalation_required` / §opt-in 領域該当——を用い、新たな機械カウンタは要しない。「最大 1 回」は応答エージェントの **行動規範** であって runtime カウンタではない（LLM エージェントにとって本 spec 自体が実装面＝spec/code 乖離による死文化は生じない）。
- 軽微指摘は「1 回修正 → 終了」が既定。修正が次 round で新たな軽微 nit を生んでも、それは **自己彫琢の自己目的化**（第 7 条 P4 が抑止する暴走の一種）であり追従しない。
- 重大指摘のみがループ継続を正当化する。「解決まで or 人間献上」の二択で、無限ループには陥らせない。
- 重大度判定が曖昧なときは重大側に倒す（fail-safe＝見落としより過剰停止が安全。第 6 条 人間最終承認）。

**根拠**: 第 2/3 条（決定論・情報純度 ＞ 確率的多 round 彫琢＝純度/コストの逆転防止）、第 7 条 P4（自己目的化したループの暴走抑止）。経験的観察として、自己改修ループでは軽微指摘が単調にメタ化し Council confidence が逓減する。本境界はその凍結基準を成文化する。

## 旧 `auto-merge` ラベルの廃止

v5.9.0 で `auto-merge` ラベルは **廃止**（二重ラベル方式の腐敗回避、Council minority_opinion (3)）。

- `crosscut-autonomous-drive` deployment 時のラベル作成リストから除外
- `issue-pickup.yml` の `--label auto-merge` 自動付与を削除
- `auto-merge.yml` の条件 1（whitelist）を削除し、stop ラベル blacklist 方式に置換
- 既存 PR で `auto-merge` ラベルが残存する場合は **無視**（merge 判定に影響しない）

## メタ承認機構（PR1 placeholder）

Council minority_opinion (4) の「AI 自身の判定基準該当判定の信頼性検査」は v5.9.0 PR1 では placeholder 実装。**v5.9.0 で workflow が `auto-merge` ラベルを参照しなくなったため、roll-back 指標 4 項目のうち workflow で自動検知できないもの（AI 判定漏れ・境界曖昧化・二重ラベル腐敗）はすべて本機構の手動運用に統合する**：

- **AI 判定漏れ監視**: AI が opt-out 判定した PR で **後から人間が `human-review-needed` を付与** した場合、その PR を「AI 判定漏れ」として記録（手動運用、PR3 で sensor 化候補）
- **二重ラベル腐敗監視**（v5.9.0 反転由来）: merge 済 PR に旧 `auto-merge` ラベルが残存しているか月次で `gh pr list --state merged --label auto-merge` で確認、1 件でも検出されたら即 roll-back ゲート起動
- **境界曖昧化監視**: opt-in / opt-out の判定が曖昧だった事例（philosophy 周辺等）を月次で振り返り、月 2 件以上なら roll-back 評価
- **集計**: 月次で「AI 判定漏れ率」「二重ラベル検出件数」「境界曖昧化件数」を `history/REGIME-LOG.md` または専用ログに append、閾値超過で roll-back 評価ゲートを起動（下記 §roll-back プロトコル）

## roll-back プロトコル（6 ヶ月後検証）

Council minority_opinion (2) 由来。**v5.9.0 merge 後 6 ヶ月時点（2026-11-06）で必須評価**。

### 評価指標

| 指標 | 閾値 | 出典 | 検知主体 |
|------|------|------|----------|
| **暗黙 merge 事故件数** | 1 件以上で要再評価 | 哲学者懸念（『気づいたら merge』の事後発覚） | 人間（事後監視）+ メタ承認機構 |
| **AI 判定漏れ率** | 5% 超で要再評価 | 上記メタ承認機構の月次集計 | メタ承認機構（手動運用、PR3 で sensor 化候補） |
| **境界曖昧化事例** | 月 2 件以上で要再評価 | 経営者懸念（philosophy 周辺の判定揺らぎ） | 人間（事後監視） |
| **二重ラベル腐敗** | 旧 `auto-merge` ラベル残存 PR が 1 件でも auto-merge → 即 roll-back | 開発者懸念 | **人間（事後監視）** — workflow は v5.9.0 で `auto-merge` ラベルをチェックしなくなったため自動検知不可。メタ承認機構の手動運用に統合する |

### roll-back 手順

1. v5.9.0 → v5.10.0 として opt-in モデルに復帰（philosophy.md 改修を伴う）
2. `auto-merge.yml` 条件 1（whitelist）復元、stop ラベル blacklist は補助的に残置
3. `auto-merge` ラベルを再導入
4. roll-back 理由を `history/REGIME-LOG.md` v5.10.0 セクションに記録
5. Council 諮問を再起動（同一 question_to_answer で再判定、本判定の `actual_outcome.status = "modified"` を記入）

### roll-back せず継続する場合

評価指標すべて閾値未満なら継続。**ただし 1 年後（2027-05-06）に再評価ゲート**。
本ファイルに `evaluation_history` セクションを追記し、過去評価の事実関係を append-only で残す。

## 実装で参照する箇所

| ファイル | 参照内容 |
|---------|---------|
| `.github/workflows/auto-merge.yml` | 条件 1: 本ファイル §stop ラベル定義 |
| `.github/workflows/claude-review.yml` / `gemini-review.yml` | 指摘の重大度提示（本ファイル §review 応答ループの終端境界） |
| PR 応答エージェント（babysit / autonomous-drive 経路） | 重大度分岐とループ終端（本ファイル §review 応答ループの終端境界） |
| `.github/workflows/issue-pickup.yml` | `--label auto-merge` 削除（本ファイル §旧 auto-merge ラベルの廃止） |
| `.claude/skills/layer1-autonomous-dev/SKILL.md` | 対話中タグ付け判定基準（本ファイル §opt-in 領域） |
| `.claude/skills/crosscut-issue-implementer/SKILL.md` | opt-in→opt-out philosophy 反転（本ファイル §設計原則） |
| `.claude/skills/crosscut-autonomous-drive/SKILL.md` | label 作成リストから `auto-merge` 除外（本ファイル §旧ラベルの廃止） |
| `.claude/skills/layer0-spec-architect/references/philosophy.md` | 第 5 条 / 第 7 条への opt-out 反転の注記（本ファイル §設計原則） |

## evaluation_history（append-only）

| 日付 | 評価結果 | 次回評価日 | 備考 |
|------|---------|-----------|------|
| 2026-05-06 | v5.9.0 として初導入 | 2026-11-06 | Council `council-2026-05-06T08:30:00Z-amrev1` |
