# Judgment Agent — 優先度バランス評定機構

3 軸の観測と優先度配分から、`question_to_answer` に対する単一の答えを導く。

> **本機構は投票の集計装置ではない**（[../SKILL.md](../SKILL.md) §重みの意味論）。
> 重みは議決権数ではなく「単独通過に要する強度の閾値」であり、`weighted_score` の比較は
> 多数派の判定ではなく**優先度バランスの評定**である。`recommended` は「勝った案」ではなく
> 「骨格として選ばれた案」であり、敗れた軸の主張は `minority_opinion` と（統合した場合は）本文に吸収される。

## 役割

- 3 Persona 出力 + （PR2: 討論ログ）+ 優先度配分 + conflict_type を受領
- 優先度バランスを評定して単一回答を構成
- 意見の質と動的変化を評価
- 少数意見を保持（消さない）

## 設計原則

### 中立性

- **人格づけしない**（4 人目の Persona にならない）
- 自身の意見を持たない、3 Persona の発言を集約する立場
- 重み配分の機械的適用を強調する

### Temperature

- **0.1** に固定（決定論寄り）
- 論理整理と機械的判定が主要タスクのため、創造性は不要

### 入力

```json
{
  "question_to_answer": "どの実装案を採用すべきか",
  "options": ["案A: ...", "案B: ..."],
  "persona_outputs": [
    {"persona": "経営者", "stance": "案A", "reason": "...", "confidence": 0.7, ...},
    {"persona": "開発者", "stance": "案B", "reason": "...", "confidence": 0.9, ...},
    {"persona": "哲学者", "stance": "案A", "reason": "...", "confidence": 0.5, ...}
  ],
  "final_weights": {"経営者": 2, "開発者": 6, "哲学者": 2},
  "conflict_type": "simple_conflict",  // unanimous / reason_divergence / simple_conflict
  "discussion_log": null  // PR2 で Phase 2 結果
}
```

### 出力

```json
{
  "recommended": "案B（開発者重視 + 開発者の高 confidence）",
  "reasoning": "重み配分 implementation で開発者 6 が支配的。開発者は confidence 0.9 で案B を支持。経営者・哲学者は案A を支持するが、合計重み 4 で開発者 6 を覆さない。技術的実現性で案B が優位",
  "minority_opinion": "経営者と哲学者は案A を支持。理由は『短期 ROI と意味付け』。案B 採用時はこの観点でのフォローアップを推奨",
  "weight_note": "implementation カテゴリで開発者重視（6/10）。重み配分は council-weights.md §situational_modifier.implementation を適用",
  "judgment_confidence": 0.75,
  "final_decision": null
}
```

## prompt 設計

### system prompt（PR1）

```
あなたは Council System の Judgment Agent です。

役割:
- 3 Persona の発言を、与えられた重み配分に基づいて集約する
- question_to_answer に対する単一の推奨を導く
- 少数意見を必ず保持する

制約:
- 自身の意見・人格を持たない（4 人目の Persona にならない）
- 重み配分を機械的に適用する
- final_decision は常に null で返す（決定は実装者の合意プロセスが行う）
- judgment_confidence < 0.5 の場合は理由を reasoning に明記する

出力形式: 別添 schema（output-format.md §4 Judgment Agent 出力）

入力に含まれる discussion_log が null の場合は、Phase 1 のみで判定する（PR1）。
conflict_type が "reason_divergence" の場合は多様性として質を評価し、どの次元がどう満たされたかを軸ごとに列挙する。
conflict_type が "unanimous" の場合は観測次元も重複しているため被覆不足を疑い、未被覆の観点を minority_opinion に記録する（多様性として扱わない）。

重み計算規則（PR1 単純対立、必須遵守）:
- 各 Persona の final_weight は不可分の整数。複数 stance に按分してはならない（按分は哲学違反）
- options 外 stance（「第3の道」「保留」等）は weight 加算対象外。weight_calculation.third_way_excluded に退避する（理由文付き）
- recommended は weight_calculation.max_score_stance と接頭辞一致させる（不一致は Orchestrator 検算で自動的にリトライ → judgment_failed）
- 出力には weight_calculation フィールド（output-format.md §4 のスキーマ）を必須で含める
- 同点（差 < 0.01）の場合は weight_calculation.tie_break_applied = true、max_score_stance = null、judgment_confidence < 0.4 で出力し人間エスカレーションへ誘導する
- weight_calculation.scores[*].weighted_score は weight × confidence の純粋計算結果（小数第2位）で記載する。意味的調整や dimension 軸での加点は行わない
```

### Few-shot 例（PR1）

PR1 では Few-shot 例を 2 例埋め込む（unanimous と simple_conflict 各 1）。
内容は本ファイルでは省略。実装時に Orchestrator が prompt 組み立て時に挿入する。
PR2 以降で COUNCIL-LOG から実例を抽出して差し替える。

## judgment_confidence の帯（v6.5.0 追加・決定論の上下限）

`judgment_confidence` は「推奨の正しさへの自信」ではなく
**「バランス評定が単一の推奨に収束した度合い」**である。したがって
スコア差（gap）という連続量から決定論で帯（下限・上限）を導き、
Judgment Agent の自己評価はその帯の内側でのみ許される。

**設計契機**: 2026-07-26 の実測で、gap と `judgment_confidence` の相関が **r = +0.341**（n=17）と弱く、
gap 1.4 で jc が 0.45〜0.82 に散っていた。すなわち重みの精緻さが算出されながら下流で消費されていない。
本帯を適用すると既存 17 件のうち **7 件が「過信」として検出される**（過小は 0 件）。
検出された 7 件は全て gap が小さい領域にあり、gap が大きい 6 件は全て帯内だった
＝ **jc は gap によらず 0.7〜0.8 に張り付く系統的バイアスがあった**。

算出は Orchestrator の純粋関数 `compute_confidence_band`
（[orchestrator.md](orchestrator.md) §confidence 帯プロトコル）が行い、
Judgment Agent には**帯だけを渡す**（gap の生値は渡さない — 忖度を防ぐため）。

**stance が全一致した場合**（gap が定義されない）は `conflict_type` で帯が決まる（v6.7.0）：

| conflict_type | 帯 | 根拠 |
|---|---|---|
| `reason_divergence` | 0.60 – 0.90 | 独立した次元からの同一結論 ＝ 真の多様性 |
| `unanimous` | 0.45 – 0.70 | 次元も重複 ＝ 被覆不足の疑い（§stance 一致時の扱い） |

**stance が割れた場合**は gap（1 位と 2 位の `weighted_score` 差）で決まる：

| gap 率（= gap ÷ ΣW） | 帯 | 意味 |
|---|---|---|
| < 0.10（拮抗） | 0.30 – 0.50 | 収束していない。人間エスカレーション圏 |
| 0.10 – 0.25 | 0.45 – 0.70 | 部分的に収束 |
| ≥ 0.25（明瞭） | 0.60 – 0.90 | 単一の推奨に収束 |

上書き規則（既存規則を帯へ統合）：

- `third_way_excluded` の weight 合計が ΣW の 30% 以上 → 上限を **0.50** に切り下げ
  （高優先度軸が選択形式で吸収できないシグナル）
- `malformed` Persona を含む → 帯は **0.00 – 0.30**
- `tie_break_applied = true` → 帯は **0.00 – 0.39**（既存の「0.4 未満」要求と等価）

帯を外れた出力は Orchestrator が検算でリトライを要求する
（[orchestrator.md](orchestrator.md) §決定論検算プロトコル）。2 回目も帯外なら `judgment_failed`。

**帯の幅は校正パラメータである**: 上表の初期値は 2026-07-26 時点の実測 17 件から逆算した。
escalation 率に直接効くため（帯を狭めると献上が増え CTL 蓄積速度が落ちる）、
振り返り儀式 F2/F3 で実測分布を見て校正する。校正時は本表と
`compute_confidence_band` の定数を同時に更新する（片方だけ変えると検算が恒常的に落ちる）。

## judgment_confidence の算出指針

以下は帯の**内側で**自己評価する際の考慮事項である（帯と矛盾する場合は帯が優先する）：

- 重み配分が支配的（最大重み Persona の confidence が高い、かつ stance が他と一致）→ 高 confidence
- `reason_divergence`（独立した次元から同一結論） → 0.6-0.9
- `unanimous`（次元も重複） → 0.45-0.7（被覆不足の疑いゆえ引き下げる。v6.7.0 で是正）
- 単純対立だが重み差が大きい → 0.6-0.8
- 単純対立で重みが拮抗 → 0.4-0.6
- 全 Persona の confidence が低い → 0.3-0.5
- 入力が malformed Persona を含む → 0.3 以下
- weight_calculation の最大スコアと第二位スコアの差が < 0.5 → 0.4-0.6
- options 外 stance（third_way_excluded）が存在し全 weight の 30% 以上を占める → 0.5 以下
- weight_calculation.tie_break_applied = true → 0.4 未満（人間エスカレーション必須）

`judgment_confidence < 0.5` の場合、Orchestrator は出力に `human_escalation_required: true` を付加する。

## stance 一致時の扱い（v6.7.0 で 2 分）

`stance` が全一致した場合、**観測次元が分離しているかどうかで扱いを分ける**
（判定は決定論。[conflict-typology.md](conflict-typology.md) §判定ロジック）。

### `conflict_type = "reason_divergence"`（類型 B ＝ 独立した次元から同一結論）

**これが「多様性（プルラリティ）として質を評価する」対象である**（`council-philosophy.md` §2）。
3 軸が異なる物差しで同じ答えに到達したのだから、3 つの独立した支持を得たことになる。

1. 一致した stance を `recommended` に設定
2. `reasoning` に**どの次元がどう満たされたかを軸ごとに列挙する**
   （例「ROI 軸では〜、保守性軸では〜、意味軸では〜が満たされる」）。
   単に「全員一致」と書いてはならない——**何が独立に支持されたかが本類型の情報である**
3. `minority_opinion` に「結論は一致するが観測次元は分離（各軸の dimension を列挙）」を記録
4. `weight_note` に「stance 一致のため重み配分は判定に影響しなかった」と記載
5. `judgment_confidence` は高め（帯 0.60–0.90）

### `conflict_type = "unanimous"`（次元も一致 ＝ 観測の重複の疑い）

**多様性として扱ってはならない。** 同じ物差しで同じ答えが出ただけであり、
3 軸で観測したことによる被覆の増加が得られていない。

1. 一致した stance を `recommended` に設定
2. `reasoning` に**観測次元が重複している事実を明記する**（どの軸間で重なったか）
3. `minority_opinion` に「**被覆不足の疑い**: 本判定は 3 軸が同一次元を観測したため、
   未観測の次元が残っている可能性がある」を記録し、各軸の `concerns` から
   本判定で扱われなかった観点を拾って列挙する
4. `weight_note` に「stance 一致のため重み配分は判定に影響しなかった」と記載
5. `judgment_confidence` は**引き下げる**（帯 0.45–0.70）

> **なぜ引き下げるか**: `council-philosophy.md` 第2条の系のとおり、
> 「全会一致を質と読む」規則は被覆不足の隠蔽装置に反転しうる。
> v6.6.0 までは次元の重複を問わず 0.7–0.9 を与えていたため、
> **最も情報の少ない一致に最も高い確信度が付いていた**。v6.7.0 でこれを是正する。

## 単純対立時の扱い（PR1）

`conflict_type = "simple_conflict"` の場合：

1. **weight 分割は禁止**。各 persona の `final_weight` は不可分の整数として扱う。1 persona = 1 stance = 1 weight 値。複数 stance への按分（例: 開発者 6 を A に 4 / C に 2）は哲学違反であり、Orchestrator の決定論検算で不一致となる。1 回目の不一致でリトライが要求され、2 回目も不一致なら `judgment_failed` 扱いとなる
2. **options 外 stance（「第3の道」「保留」「自由記述」等）は weight 加算対象外**。これらは `weight_calculation.third_way_excluded` に退避し、`minority_opinion` にも転載する（暫定運用、PR2 で `third_way` 類型として正式化、[conflict-typology.md](conflict-typology.md) §第3の道 stance の PR1 暫定運用ルール）
3. `options` に含まれる stance のみで `final_weights × confidence` の積を集計する
4. 各 stance の `weighted_score = Σ (weight_i × confidence_i)`（同一 stance を支持する全 persona の積の合計）
5. 最大 `weighted_score` の stance を `recommended` に設定する。`recommended` の文字列は `weight_calculation.max_score_stance` から始めること（接頭辞一致で Orchestrator が検証する）
6. 同点（1 位と 2 位の `weighted_score` 差 < 0.01）の場合は `weight_calculation.tie_break_applied = true` を立て、`weight_calculation.max_score_stance = null` を返し、`judgment_confidence < 0.4` で人間エスカレーションへ誘導する
7. 採用されなかった stance + `third_way_excluded` を `minority_opinion` に保持する
8. `weight_calculation` フィールドに計算過程を構造化して**必ず出力する**（[output-format.md](output-format.md) §4 のスキーマ参照）
9. `weight_note` には「`weight_calculation` を機械的に適用した」旨と適用カテゴリ（implementation / operation 等）を明記する
10. `judgment_confidence` はスコア差に応じて算出する（差大→高、差小→低、本ファイル §judgment_confidence の算出指針）

### 禁止事項（哲学違反、Orchestrator 検算で必ず検出される）

- **1 persona の weight を複数 stance に按分する**（例: 開発者 6 → A に 4 / C に 2 は禁止）
- **options 外 stance を任意の options に意味的包含で振り分ける**（「第3の道（実質 A）」を A に統合する等）
- **`weight_calculation.max_score_stance` と `recommended` の接頭辞不一致**（`recommended` が `max_score_stance` で始まらない場合は哲学違反）
- **`weight_calculation.scores[*].weighted_score` の数値を純粋関数結果（Orchestrator §`compute_weight_scores`）と異なる値で書く**

これらは `weight_calculation` フィールド出力の必須化と Orchestrator の決定論検算
（[orchestrator.md](orchestrator.md) §決定論検算プロトコル）によって構造的に防がれる。
COUNCIL-LOG `council-2026-04-29T18-00-00Z-d1m4n5` の事例（開発者 weight 6 を A 寄り 4 / C 寄り 2 に分割）が
本節の制約強化の契機。

## final_decision の扱い

**Judgment Agent は final_decision を絶対に埋めない**。常に `null` を返す。

これは `council-philosophy.md` §3 認識合わせと合意の分離 / §6 人間との距離感の実装。
決定は実装者の合意プロセス（`consensus-protocol.md`）または人間が行う。

prompt にも明記：「final_decision は常に null で返す。あなたが決定を埋めることは哲学違反である」

## PR1 での簡略化

- Few-shot 例は 2 例（unanimous, simple_conflict 各 1）
- discussion_log は受け取るが常に null（Phase 2 未実装）
- 自己診断は judgment_confidence のみ（PR2 でより詳細な自己診断を追加）
- 動的変化の追跡（時系列で意見がどう変わったか）は PR3 で実装

## PR2 以降の予告

- Phase 2 討論ログを受け取り、Persona の意見変化を追跡
- 対立類型ごとの判定ロジックの精緻化
- Few-shot を実 COUNCIL-LOG から抽出
- 自己診断項目の拡張（重み妥当性、論理整合性、premise 整合性）
