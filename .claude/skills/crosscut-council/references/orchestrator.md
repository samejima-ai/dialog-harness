# Orchestrator — フラット実装プロトコル

情報を運び、応答を集約し、重みを決定論で計算する。**判断機能を持たない**。

## 責務

- Pre-Check 出力の受領
- 重み計算（`council-weights.md` を参照）
- 3 Persona への並列呼び出し指示
- Persona 応答の収集（情報純度を守る）
- Judgment Agent への入力組み立て
- **決定論検算**（Judgment Agent 出力の `weight_calculation` 整合性検証、PR1 新規）
- COUNCIL-LOG への追記

## 責務に含まれないこと（フラット原則）

- **判断しない**: Orchestrator は内容評価を行わない
- **編集しない**: Persona の発言や Judgment Agent の判断の**意味内容**は改変しない。ただし、スキーマ不適合時の `stance: "malformed"` 付与のような**構造正規化・エラーマーカー付与**はこの禁止に含めない（詳細は本ファイル §スキーマ検証 を参照）
- **誘導しない**: Persona への入力に偏向（重みの事前開示等）を含めない
- **学習しない**: 過去の COUNCIL-LOG を参照して入力を調整しない

これらは全て `philosophy.md` §3 情報純度原則に反する。Orchestrator の責務は**運搬と計算**に限定される。

**例外的に許可される計算**: `weight_calculation` の決定論検算（本ファイル §決定論検算プロトコル）は
「内容評価」ではなく「Judgment Agent 出力の構造的整合性検証」であり、フラット原則違反にあたらない。
`philosophy.md` §2 Shift Left 原則に基づく純粋関数化として位置付ける。

## 重み計算プロトコル

### 入力

- `council-weights.md` の fenced YAML ブロック
- Pre-Check 出力の `council_type` と `category`

### 計算式

```
final_weight[persona] = base_weight[persona] × ethos_multiplier[persona]
                      + situational_modifier[category][persona]
```

### 制約

- `final_weight < 0` の場合は 0 にクランプ（負の重みは意味を持たない）
- 3 Persona の合計 final_weight を Judgment Agent に渡す（正規化は Judgment Agent 側で行う）
- category が未定義の場合は `judgment` にフォールバックし、COUNCIL-LOG に `category_fallback: true` を記録

### 計算例

`council_type = business`、`category = implementation` の場合：

```
base_weights.business = { 経営者: 3, 開発者: 4, 哲学者: 3 }
ethos_multiplier.business = { 経営者: 1.0, 開発者: 1.0, 哲学者: 1.0 }
situational_modifier.implementation = { 経営者: -1, 開発者: +2, 哲学者: -1 }

final_weights = {
  経営者: 3 × 1.0 + (-1) = 2,
  開発者: 4 × 1.0 + (+2) = 6,
  哲学者: 3 × 1.0 + (-1) = 2
}
```

## Phase 1 並列呼び出しプロトコル

### 入力組み立て

各 Persona への入力は**同一**の context を含むが、Persona system prompt のみ異なる：

```json
{
  "system_prompt_path": "references/personas/business/{persona}.md",
  "temperature": {persona によって 0.2 / 0.3 / 0.7},
  "context": {元の発動要請の context},
  "options": {元の発動要請の options},
  "question_to_answer": {元の発動要請の question_to_answer},
  "other_persona_outputs": null,
  "weights": null
}
```

### 重要な禁止事項

- **他 Persona の出力は渡さない**（Phase 1 独立性、`philosophy.md` §3 情報純度）
- **重み配分は Persona に渡さない**（重みに応じた忖度を防ぐため）
- **過去の COUNCIL-LOG は渡さない**（Few-shot は system prompt 内で事前構成済み）

### 並列性の担保

3 Persona は**真に並列**に呼び出す。逐次呼び出しは禁止（先に話した Persona の応答を知らせないため）。
応答タイムアウトは各 Persona 60 秒を上限とする（Phase 1 合計 60 秒で打ち切り）。

### 応答の検証

Persona 応答は `output-format.md` のスキーマに適合する JSON でなければならない。
適合しない場合、Orchestrator は該当 Persona を最大 1 回リトライする。
それでも不適合なら、該当 Persona を `stance: "malformed"` として扱い、Judgment Agent 入力に含める（重みは 0 に設定）。

## Phase 3 への橋渡し

Orchestrator は以下を Judgment Agent に渡す：

```json
{
  "question_to_answer": {元の発動要請の question_to_answer},
  "options": {元の発動要請の options},
  "persona_outputs": [{3 Persona の応答}],
  "final_weights": {計算結果},
  "conflict_type": {PR1: "unanimous" or "simple_conflict"},
  "discussion_log": null  // PR2 で Phase 2 結果を入れる
}
```

## 決定論検算プロトコル（PR1 新規）

Judgment Agent 出力受領後、Orchestrator は以下の純粋関数を実行し、`weight_calculation` の
整合性と `recommended` との一致を検証する。設計契機は COUNCIL-LOG `council-2026-04-29T18-00-00Z-d1m4n5`
で発生した weight 分割逸脱（開発者 weight 6 を A 寄り 4 / C 寄り 2 に按分し A を recommended に捏造）。

### compute_weight_scores（純粋関数）

```python
def compute_weight_scores(persona_outputs, final_weights, options):
    """
    Args:
        persona_outputs: [{persona, stance, confidence, ...}, ...]
        final_weights: {"経営者": int, "開発者": int, "哲学者": int}
        options: ["Option A", "Option B", ...]  # 元の発動要請の options

    Returns:
        {
            "scores": [{stance, supporters, weight_sum, weighted_score, components}, ...],
            "third_way_excluded": [{persona, stance, weight, confidence, reason}, ...],
            "max_score_stance": str | None,
            "tie_break_applied": bool
        }
    """
    score_map = {}        # stance -> {supporters, weight_sum, weighted_score, components}
    excluded = []

    for p in persona_outputs:
        persona = p["persona"]
        stance = p["stance"]
        weight = final_weights.get(persona, 0)
        confidence = p.get("confidence", 0.0)

        # malformed は weight 0 扱い（既存仕様、§スキーマ検証）
        if stance == "malformed" or weight == 0:
            continue

        # options 外 stance（「第3の道」「保留」「自由記述」等を含む）は
        # third_way_excluded へ
        # (conflict-typology.md §第3の道 stance の PR1 暫定運用ルール)
        # judgment-agent.md §単純対立時の扱い 規則 2 と整合: 「保留」も options に
        # 明示されない限り weight 加算対象外
        if stance not in options:
            excluded.append({
                "persona": persona, "stance": stance,
                "weight": weight, "confidence": confidence,
                "reason": "options 外 stance のため weight 加算対象外（PR1 暫定運用）"
            })
            continue

        if stance not in score_map:
            score_map[stance] = {"supporters": [], "weight_sum": 0,
                                 "weighted_score": 0.0, "components": []}
        score_map[stance]["supporters"].append(persona)
        score_map[stance]["weight_sum"] += weight
        score_map[stance]["weighted_score"] += weight * confidence
        score_map[stance]["components"].append(
            {"persona": persona, "weight": weight, "confidence": confidence}
        )

    scores = [{"stance": s, **v} for s, v in score_map.items()]
    if not scores:
        return {"scores": [], "third_way_excluded": excluded,
                "max_score_stance": None, "tie_break_applied": False}

    sorted_scores = sorted(scores, key=lambda x: x["weighted_score"], reverse=True)
    top = sorted_scores[0]
    tie = (len(sorted_scores) > 1 and
           abs(sorted_scores[0]["weighted_score"] - sorted_scores[1]["weighted_score"]) < 0.01)

    return {
        "scores": scores,
        "third_way_excluded": excluded,
        "max_score_stance": None if tie else top["stance"],
        "tie_break_applied": tie
    }
```

### classify_conflict（純粋関数・v6.7.0 で 3 値化）

`conflict_type` を決定論で導く。実装と設計根拠は
[conflict-typology.md](conflict-typology.md) §判定ロジック（決定論・v6.7.0）が一次情報源。

- `stance` が割れる → `simple_conflict`
- `stance` 全一致 かつ 全ペアの `dimension` Jaccard ≤ 0.30 → **`reason_divergence`**（類型 B）
- `stance` 全一致 かつ いずれかのペアで Jaccard > 0.30 → `unanimous`
- `dimension` 欠落時は判定不能 → 保守的に `unanimous`

Orchestrator は判定結果を Judgment Agent に渡すのみで、**内容評価はしない**（フラット原則）。
判定は純粋関数であり LLM 推論を挟まない（`philosophy.md` §2 Shift Left）。

### compute_confidence_band（純粋関数・v6.5.0 新規 / v6.7.0 で conflict_type 対応）

gap（1 位と 2 位の `weighted_score` 差）という連続量から `judgment_confidence` の許容帯を導く。
`stance` 全一致時は gap が定義されないため `conflict_type` で帯を決める。
設計根拠と校正の扱いは [judgment-agent.md](judgment-agent.md) §judgment_confidence の帯。

```python
def compute_confidence_band(scores, third_way_excluded, final_weights,
                            malformed_count=0, tie_break_applied=False,
                            conflict_type=None):
    """
    Args:
        scores: compute_weight_scores() の "scores"（stance ごとの weighted_score を含む）
        third_way_excluded: 同 "third_way_excluded"
        final_weights: {"経営者": int, ...}
        malformed_count: stance == "malformed" の Persona 数
        tie_break_applied: 同点判定フラグ
        conflict_type: classify_conflict の出力（v6.7.0）。stance 全一致時の帯を決める

    Returns:
        (lo: float, hi: float)  # judgment_confidence の許容帯（両端含む）

    注意: 本関数は帯だけを返す。gap の生値を Judgment Agent へ渡してはならない
    （重み配分を渡さないのと同じ理由 — 忖度の防止、§重要な禁止事項）。
    """
    # ハードストップ（既存規則との等価性を保つ）
    if malformed_count > 0:
        return (0.00, 0.30)
    if tie_break_applied:
        return (0.00, 0.39)

    total_weight = sum(final_weights.values())
    if total_weight <= 0:
        return (0.00, 0.30)

    ranked = sorted((s["weighted_score"] for s in scores), reverse=True)
    if len(ranked) < 2:
        # 単一 stance のみ ＝ stance 全一致。gap が定義されないので conflict_type で決める。
        # reason_divergence（独立した次元から同一結論）＝ 真の多様性 → 高め
        # unanimous（次元も重複）＝ 被覆不足の疑い → 引き下げ
        # （judgment-agent.md §stance 一致時の扱い / council-philosophy.md 第2条の系）
        if conflict_type == "unanimous":
            return (0.45, 0.70)
        return (0.60, 0.90)   # reason_divergence および conflict_type 未指定時
    gap_ratio = (ranked[0] - ranked[1]) / total_weight

    if gap_ratio < 0.10:
        lo, hi = 0.30, 0.50
    elif gap_ratio < 0.25:
        lo, hi = 0.45, 0.70
    else:
        lo, hi = 0.60, 0.90

    # 高優先度軸が options 外に出たシグナル（既存の 30% 規則を帯へ統合）
    tw_weight = sum(x.get("weight", 0) for x in third_way_excluded)
    if tw_weight / total_weight >= 0.30:
        hi = min(hi, 0.50)
        lo = min(lo, hi - 0.10)

    return (round(lo, 2), round(hi, 2))
```

**ΣW について**: `total_weight` は `final_weights` の実測合計を使う（定数 10 を仮定しない）。
`council-weights.md` の `situational_modifier` は `judgment` / `conception` で合計が +1 になっており
実 ΣW が 11 になる既知の宣言違反があるため（同ファイル §既知の宣言違反）、
gap を絶対値でなく**比率**で評価することで、数値是正の前後で帯の意味が変わらないようにする。

### verify_weight_calculation（決定論検算）

```python
def verify_weight_calculation(judgment_output, persona_outputs, final_weights, options):
    """
    Returns:
        ("ok", None)
        ("retry", reason: str)
        ("judgment_failed", reason: str)  # 2 回目不一致時に Orchestrator が変換
    """
    expected = compute_weight_scores(persona_outputs, final_weights, options)
    actual = judgment_output.get("weight_calculation")

    if actual is None:
        return ("retry", "weight_calculation フィールド欠落")

    # 同点処理: tie 時は judgment_confidence < 0.4 を要求
    if expected["tie_break_applied"]:
        if judgment_output.get("judgment_confidence", 1.0) >= 0.4:
            return ("retry",
                    "同点（差 < 0.01）だが judgment_confidence ≥ 0.4。"
                    "0.4 未満で再提出すること")

    # actual.tie_break_applied の一致検証（型チェック含む、truthy 偽装を防ぐ）
    if "tie_break_applied" not in actual:
        return ("retry", "weight_calculation.tie_break_applied フィールド欠落")

    actual_tie_break_applied = actual.get("tie_break_applied")
    if not isinstance(actual_tie_break_applied, bool):
        return ("retry",
                "weight_calculation.tie_break_applied は bool である必要がある "
                f"(actual={actual_tie_break_applied!r})")

    if actual_tie_break_applied != expected["tie_break_applied"]:
        return ("retry",
                f"tie_break_applied 不一致 "
                f"actual={actual_tie_break_applied!r} expected={expected['tie_break_applied']!r}")

    # actual.max_score_stance の一致検証
    if actual.get("max_score_stance") != expected["max_score_stance"]:
        return ("retry",
                f"max_score_stance 不一致 "
                f"actual={actual.get('max_score_stance')!r} expected={expected['max_score_stance']!r}")

    # max_score_stance と recommended の接頭辞一致検証
    # （recommended は「Option B（一文で）...」のような自然文付きで来るため、
    #  max_score_stance の文字列が recommended の先頭から完全一致すれば OK）
    if expected["max_score_stance"] is not None:
        recommended = judgment_output.get("recommended", "")
        expected_stance = expected["max_score_stance"]
        if not recommended.startswith(expected_stance):
            return ("retry",
                    f"recommended ('{recommended[:60]}...') が "
                    f"weight_calculation.max_score_stance ('{expected_stance}') と接頭辞不一致")

    # scores の stance 集合一致検証（按分・stance 捏造の検出）
    expected_stances = sorted([s["stance"] for s in expected["scores"]])
    actual_stances = sorted([s["stance"] for s in actual.get("scores", [])])
    if expected_stances != actual_stances:
        return ("retry",
                f"scores stance 集合不一致 "
                f"actual={actual_stances} expected={expected_stances}")

    # スコア値検証（小数第2位へ丸めた値が厳密一致）
    expected_by_stance = {s["stance"]: round(s["weighted_score"], 2) for s in expected["scores"]}
    for s in actual.get("scores", []):
        e = expected_by_stance.get(s["stance"])
        actual_rounded = round(s["weighted_score"], 2)
        if e is None or actual_rounded != e:
            return ("retry",
                    f"weighted_score 不一致 stance={s['stance']} "
                    f"actual={actual_rounded} expected={e}")

    # weight_sum 検証（按分検出: persona の weight 合計が final_weights と一致するか）
    expected_weight_sum_by_stance = {s["stance"]: s["weight_sum"] for s in expected["scores"]}
    for s in actual.get("scores", []):
        e_sum = expected_weight_sum_by_stance.get(s["stance"])
        if e_sum is None or s.get("weight_sum") != e_sum:
            return ("retry",
                    f"weight_sum 不一致 stance={s['stance']} "
                    f"actual={s.get('weight_sum')} expected={e_sum}")

    # third_way_excluded の persona 集合一致
    expected_excluded_personas = sorted([x["persona"] for x in expected["third_way_excluded"]])
    actual_excluded_personas = sorted([x["persona"] for x in actual.get("third_way_excluded", [])])
    if expected_excluded_personas != actual_excluded_personas:
        return ("retry",
                f"third_way_excluded persona 集合不一致 "
                f"actual={actual_excluded_personas} expected={expected_excluded_personas}")

    # components の整合性検証（按分隠蔽の構造的検出）
    # supporters と components の persona 集合一致 + components の weight/confidence が
    # 入力（final_weights / persona_outputs）と完全一致することを確認。
    # これにより components を欠落させて weight_sum だけ合わせる隠蔽を防ぐ。
    persona_outputs_by_persona = {p["persona"]: p for p in persona_outputs}
    for s in actual.get("scores", []):
        stance = s["stance"]
        components = s.get("components", [])
        component_personas = sorted(c.get("persona") for c in components)
        supporter_set = sorted(s.get("supporters", []))
        if component_personas != supporter_set:
            return ("retry",
                    f"components persona 集合 != supporters stance={stance} "
                    f"components={component_personas} supporters={supporter_set}")
        for c in components:
            persona = c.get("persona")
            expected_weight = final_weights.get(persona)
            if c.get("weight") != expected_weight:
                return ("retry",
                        f"components[*].weight != final_weights stance={stance} "
                        f"persona={persona} actual={c.get('weight')} expected={expected_weight}")
            persona_output = persona_outputs_by_persona.get(persona)
            if persona_output is None:
                return ("retry",
                        f"components persona が persona_outputs に存在しない "
                        f"stance={stance} persona={persona}")
            expected_conf = persona_output.get("confidence", 0.0)
            if c.get("confidence") != expected_conf:
                return ("retry",
                        f"components[*].confidence != persona_outputs stance={stance} "
                        f"persona={persona} actual={c.get('confidence')} expected={expected_conf}")

    # judgment_confidence の帯検査（v6.5.0 新規、compute_confidence_band）
    # gap という連続量を下流に接続する。帯の外は「収束度の申告が実測と乖離」として retry。
    band_lo, band_hi = compute_confidence_band(
        expected["scores"], expected["third_way_excluded"], final_weights,
        malformed_count=sum(1 for p in persona_outputs if p.get("stance") == "malformed"),
        tie_break_applied=expected["tie_break_applied"],
        conflict_type=classify_conflict(persona_outputs),   # v6.7.0
    )
    jc = judgment_output.get("judgment_confidence")
    if not isinstance(jc, (int, float)):
        return ("retry", "judgment_confidence が数値でない")
    if not (band_lo <= jc <= band_hi):
        return ("retry",
                f"judgment_confidence {jc} が許容帯 [{band_lo}, {band_hi}] の外 "
                f"（judgment-agent.md §judgment_confidence の帯）。"
                f"帯内で再提出すること")

    # 1 persona = 1 weight 不可分担保: 各 persona は scores または third_way_excluded
    # のいずれか一箇所にのみ出現すべき（重複出現は按分の兆候）
    # 上記 components 整合性検証で components persona ⊆ supporters が確定した後の二重防御
    seen_personas: set[str] = set()
    for s in actual.get("scores", []):
        for c in s.get("components", []):
            persona = c.get("persona")
            if persona in seen_personas:
                return ("retry",
                        f"persona 重複出現 (按分の兆候): {persona!r}")
            seen_personas.add(persona)
    for x in actual.get("third_way_excluded", []):
        persona = x.get("persona")
        if persona in seen_personas:
            return ("retry",
                    f"persona が scores と third_way_excluded の両方に出現: {persona!r}")
        seen_personas.add(persona)

    return ("ok", None)
```

### リトライ運用

1. 1 回目不一致 → Judgment Agent に `verify_weight_calculation` の reason を含めて再要請
2. 2 回目も不一致 → status を `judgment_failed` に設定し、`consensus-protocol.md` §Step 8 経路で
   人間エスカレーション
3. リトライ回数は COUNCIL-LOG の `weight_calculation_retry_count` フィールドに記録（0 / 1 / 2、
   2 は judgment_failed と等価）

### 計算例（d1m4n5 を入力した場合の期待出力）

```
入力:
  options = ["Option A: callback Route Handler 単独",
             "Option B: SQL trigger 単独",
             "Option C: ハイブリッド（条件付き）"]
  final_weights = {"経営者": 2, "開発者": 6, "哲学者": 2}
  persona_outputs:
    経営者: stance="Option A: callback Route Handler 単独", confidence=0.72
    開発者: stance="Option C: ハイブリッド（条件付き）", confidence=0.75
    哲学者: stance="第3の道（A をベースに概念配置論で再構成）", confidence=0.62

compute_weight_scores の出力:
  scores:
    - stance: "Option A: callback Route Handler 単独"
      weighted_score: 1.44 (= 2 × 0.72)
    - stance: "Option C: ハイブリッド（条件付き）"
      weighted_score: 4.50 (= 6 × 0.75)
  third_way_excluded:
    - persona: "哲学者", stance: "第3の道（...）", weight: 2, confidence: 0.62
  max_score_stance: "Option C: ハイブリッド（条件付き）"
  tie_break_applied: false

→ recommended は "Option C: ハイブリッド" で始まらなければ retry
→ d1m4n5 の現行 recommended "Option A 採用 + ..." は不一致 → retry
→ 2 回目も不一致なら judgment_failed で人間エスカレーション
```

## COUNCIL-LOG への追記

Orchestrator は発動完了時（Judgment Agent 出力受領後）に 1 エントリ追記する。
スキーマは `SKILL.md` のログ要件セクション参照。
追記は **append-only**、既存エントリの編集は行わない。

## PR1 での簡略化

- Phase 2 討論はスキップ（`discussion_log: null`）
- 対立度判定は 2 値のみ（全会一致 / 単純対立）
- リトライ回数は 1 回固定（PR3 で動的調整）
- 並列呼び出しの実装は skill 実行環境の機能に依存（Task agent 並列など）
