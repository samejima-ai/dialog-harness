# Output Format — JSON 入出力規格

Council System の全エントリポイントの入出力 JSON スキーマ定義。

## 1. 発動要請（Invocation Request）

実装者または他スキルから Council を起動する際の入力。

```json
{
  "context": "string (100-2000 字の状況説明)",
  "options": ["string (検討中の選択肢、2-8 個)"],
  "question_to_answer": "string (答えるべき問い、1 文)",
  "source_skill": "string (発動元スキル名、例: layer1-autonomous-dev)",
  "category": "string (重み配分カテゴリ)"
}
```

### category の取り得る値

`council-weights.md` の `situational_modifier` のキー：

- `implementation`
- `operation`
- `maintenance`
- `issue_triage`
- `error_handling`
- `judgment` （デフォルト）
- `conception`

未定義カテゴリは `judgment` にフォールバックされ、COUNCIL-LOG に `category_fallback: true` が記録される。

## 2. Pre-Check 出力

```json
{
  "status": "pre_check_passed | pre_check_failed",
  "council_type": "business | life | hybrid",
  "category": "string",
  "invocation_id": "string (council-<ISO 8601 Z>-<6-char [a-z0-9]>)",
  "reason": "string (pre_check_failed 時のみ、差し戻し理由)"
}
```

`invocation_id` の採番主体は **Pre-Check のみ**。形式・採番ロジックは [pre-check.md](pre-check.md) §Pre-Check 出力 を参照。

## 3. Persona 出力（Phase 1）

各 Persona は以下のスキーマで応答する：

```json
{
  "persona": "string (例: 経営者 / 開発者 / 哲学者)",
  "stance": "string (取った立場、options のいずれか or 自由記述)",
  "reason": "string (300 字以内、立場の根拠)",
  "confidence": "number (0.0-1.0, 自己評価)",
  "dimension": "string (評価軸: ROI / 保守性 / 意味 / meta 等)",
  "premise": "string (前提となる時間軸や条件)",
  "concerns": ["string (懸念点、0-5 個)"]
}
```

### `stance` の制約

- 通常は `options` のいずれか（または「保留」）
- options に含まれない自由記述も許容（Persona の独立性のため）
- malformed 時は Orchestrator が `"malformed"` に置換し、重みを 0 にする

### `dimension` の意義

対立類型 D（次元ずれ、PR2 実装）の判定に使用。
PR1 でも記録は取る（将来の振り返り儀式で活用）。

## 4. Judgment Agent 出力（Phase 3）

```json
{
  "recommended": "string (推奨される方針、自由記述)",
  "reasoning": "string (推奨に至った論理、500 字以内)",
  "minority_opinion": "string (採用されなかった視点を保持、200 字以内)",
  "weight_note": "string (重み配分の説明、100 字以内)",
  "weight_calculation": {
    "method": "weight_times_confidence",
    "scores": [
      {
        "stance": "string (options のいずれか)",
        "supporters": ["string (persona 名)"],
        "weight_sum": "number",
        "weighted_score": "number (小数第2位)",
        "components": [
          {"persona": "string", "weight": "number", "confidence": "number"}
        ]
      }
    ],
    "third_way_excluded": [
      {"persona": "string", "stance": "string", "weight": "number", "confidence": "number", "reason": "string"}
    ],
    "max_score_stance": "string (recommended と接頭辞一致必須、tie 時 null)",
    "tie_break_applied": "boolean"
  },
  "judgment_confidence": "number (0.0-1.0, Judgment Agent の自己評価)",
  "consensus_mode": "auto_agree | escalate_to_human (Orchestrator が決定論で計算、PR2 拡張領域)",
  "final_decision": null,

  "actual_outcome": {
    "status": null,
    "evaluated_at": null,
    "modifier_note": null
  },
  "invocation_id": "council-2026-04-25T10:30:00Z-xxxxxx",
  "project_metadata": {
    "ctl_at_invocation": "CTL-2",
    "council_type": "business",
    "category": "operation",
    "decision_category": "C3"
  }
}
```

### `final_decision` は常に null

このフィールドは合意プロセス（`consensus-protocol.md`）が埋める。
Judgment Agent が埋めることは哲学違反（`council-philosophy.md` §3）。
スキーマ上は値を持つが、Council は常に `null` を返す。

### `weight_calculation` — 決定論検算用（PR1 新規）

Orchestrator が `verify_weight_calculation`（[orchestrator.md](orchestrator.md) §決定論検算プロトコル）で
`recommended` と `max_score_stance` の一致、および各 stance の `weighted_score` の純粋関数結果との
一致を検証する。不一致時は最大 1 回リトライ、2 回目も不一致なら `status = judgment_failed` で
人間エスカレーション（[consensus-protocol.md](consensus-protocol.md) §Step 8）。

**設計意図**: Judgment Agent が weight を恣意的に分割する哲学違反
（COUNCIL-LOG `council-2026-04-29T18-00-00Z-d1m4n5` で発生）を構造的に防ぐ。
1 persona = 1 weight 不可分の制約をスキーマ層で明示する。`components` を persona 単位の
配列にすることで、按分自体がスキーマ上書けない構造とする。

**third_way_excluded**: options 外の自由記述 stance（「第3の道」「保留」等）は
PR1 では weight 加算対象から外す暫定運用（[conflict-typology.md](conflict-typology.md)
§第3の道 stance の PR1 暫定運用ルール）。退避された意見は `minority_opinion` にも転載する。
PR2 で `third_way` 類型として正式化する際にここから移行する。

**max_score_stance の null 許容**: 1 位と 2 位の `weighted_score` 差が 0.01 未満（同点）の場合のみ
null とし、同時に `tie_break_applied = true` を立てる。`recommended` 接頭辞一致検証はスキップされ、
代わりに `judgment_confidence < 0.4` を要求する（同点処理の安全弁）。

### v4.2 で追加されたフィールド

#### `consensus_mode` — Orchestrator 決定論出力

`auto_agree` / `escalate_to_human` の二値。Orchestrator が `compute_consensus_mode`
（`consensus-protocol.md`）で算出し、Judgment Agent 出力に**後付け**で含める。
受信側 skill（L0/L1/L2）はこのフィールドだけを見て LLM 解釈を挟まず分岐できる。

PR1 では Judgment Agent 自身は埋めない（PR2 で Orchestrator 統合と同時に正式化予定）。
本ファイルではフィールドの所在を明示するために v4.2 で追記。

#### `actual_outcome` — 事後評価用（人間が後から記入）

開発中は全フィールド `null`。事後評価フェーズ（philosophy.md 第 6 条）で
人間が `~/.claude/council-data/invocations/<ISO8601Z (コロン→ハイフン)>-<invocation_id 末尾 6 文字>.json`
の `actual_outcome` を更新し、stats.json の集計に反映される（ファイル命名規則は
`ctl-calculation.md` §4 を参照）。

| フィールド | 値 | 意味 |
|---|---|---|
| `status` | `"agreed"` / `"modified"` | 人間判断との一致／修正の別 |
| `evaluated_at` | ISO 8601 | 事後評価の実施日時 |
| `modifier_note` | string or null | `"modified"` 時の修正理由（任意） |

#### `invocation_id` — 横断蓄積の主キー

`council-<ISO8601Z>-<6-char [a-z0-9]>` 形式。Pre-Check が採番し、
COUNCIL-LOG / `~/.claude/council-data/invocations/` 双方の主キーとして共有する。

#### `project_metadata` — CTL 算出用メタデータ

`ctl_at_invocation` は本判定が行われた時点の Council Trust Level。
`category` は既存の重み配分カテゴリ（`operation` / `judgment` / `conception` /
`implementation` 等、§8 COUNCIL-LOG エントリの category と同義）。
`decision_category` は v4.2 で追加された判断委譲カテゴリ（`H1`-`H4` / `C1`-`C4`、
philosophy.md 第 6 条）。両者は直交概念（詳細は `consensus-protocol.md` の
「category と decision_category の役割分担」節を参照）。
プロジェクト名・コード断片は含めない（プライバシー配慮、`ctl-calculation.md` §4）。

## 5. Council 全体応答

Orchestrator が実装者に返す最終応答：

```json
{
  "status": "success | timeout | judgment_failed | pre_check_failed",
  "invocation_id": "string",
  "council_type": "business",
  "phase_reached": "phase_1 | phase_2 | phase_3",
  "conflict_type": "unanimous | simple_conflict",
  "final_weights": {"経営者": 2, "開発者": 6, "哲学者": 2},
  "persona_outputs": [{...Persona 出力 × 3...}],
  "judgment": {...Judgment Agent 出力...},
  "human_escalation_required": false,
  "follow_up_endpoint": "string (追加質問用、invocation_id を再使用)"
}
```

`human_escalation_required: true` の条件：

- `judgment_confidence < 0.5`
- `status` が `judgment_failed`
- 対立類型 E / G（PR2 で実装）

## 6. 追加質問リクエスト（Follow-up Question）

実装者から Council への追加質問：

```json
{
  "type": "follow_up_question",
  "original_invocation_id": "string",
  "additional_question": "string (1 文)",
  "current_understanding": "string (実装者の現時点での解釈)"
}
```

## 7. 追加質問応答（Follow-up Response）

Judgment Agent から実装者への delta 応答：

```json
{
  "type": "follow_up_response",
  "original_invocation_id": "string",
  "delta_response": "string (元 judgment への追加情報のみ、200 字以内)",
  "updates_to_judgment": null,
  "follow_up_count": "number (この follow-up の通番、1 or 2)",
  "max_reached": "boolean (true なら次回はエスカレーション必須)"
}
```

`updates_to_judgment` は常に `null`（元 judgment は不変、`consensus-protocol.md` §Step 4）。

### `follow_up_count` と COUNCIL-LOG `follow_up_questions_count` の違い

| フィールド | 所在 | 意味 |
|------------|------|------|
| `follow_up_count` | Follow-up Response（本節） | この応答が本 invocation における何回目の follow-up か（1 または 2、Judgment Agent が応答時に採番） |
| `follow_up_questions_count` | COUNCIL-LOG エントリ（§8） | 本 invocation で実施された follow-up の**総数**（合意プロセス完了時に実装者が後追記、0-3） |

両者は粒度が異なる。前者は個別応答のカウンタ、後者は invocation 全体の総数。

## 8. COUNCIL-LOG エントリ

`history/COUNCIL-LOG.md` に追記される 1 エントリ：

```yaml
- invocation_id: "council-2026-04-21T15:30:00Z-a1b2c3"
  timestamp: "2026-04-21T15:30:00Z"
  source_skill: "layer1-autonomous-dev"
  question_to_answer: "..."
  council_type: "business"
  category: "implementation"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "simple_conflict"
  final_weights:
    経営者: 2
    開発者: 6
    哲学者: 2
  persona_summary:
    経営者: { stance: "案A", confidence: 0.7 }
    開発者: { stance: "案B", confidence: 0.9 }
    哲学者: { stance: "案A", confidence: 0.5 }
  judgment_confidence: 0.75
  weight_calculation:
    method: "weight_times_confidence"
    scores:
      - stance: "案A"
        supporters: ["経営者", "哲学者"]
        weight_sum: 4
        weighted_score: 1.65
        components:
          - { persona: "経営者", weight: 2, confidence: 0.70 }
          - { persona: "哲学者", weight: 2, confidence: 0.50 }
      - stance: "案B"
        supporters: ["開発者"]
        weight_sum: 6
        weighted_score: 5.40
        components:
          - { persona: "開発者", weight: 6, confidence: 0.90 }
    third_way_excluded: []
    max_score_stance: "案B"
    tie_break_applied: false
  weight_calculation_retry_count: 0
  recommended: "案B（一文で）"
  human_escalated: false
  # 後追記（合意プロセス完了時）— append-only 例外条項により null 宣言済みフィールドへの単方向埋め込みを許容
  implementer_consent: "agreed_recommended"
  follow_up_questions_count: 0
  agreed_at: "2026-04-21T15:35:00Z"
```

## バリデーション

各スキーマ違反時の Orchestrator の対応：

| 違反 | 対応 |
|------|------|
| 発動要請の必須フィールド欠落 | Pre-Check 差し戻し |
| Persona 出力スキーマ不適合 | 1 回リトライ → malformed として扱う |
| Judgment Agent 出力スキーマ不適合 | `judgment_failed` で人間エスカレーション |
| `final_decision` が null 以外 | エラー応答、再生成（哲学違反） |
| follow-up が 3 回目 | 強制エスカレーション |
| `weight_calculation` フィールド欠落 | スキーマ不適合扱い、1 回リトライ → 不一致継続なら `judgment_failed` |
| `weight_calculation.max_score_stance` ≠ `recommended` 接頭辞 | 1 回リトライ → 不一致継続なら `judgment_failed` で人間エスカレーション |
| `weight_calculation.scores[*].weighted_score` が `compute_weight_scores` 結果と不一致（小数第2位） | 1 回リトライ → 不一致継続なら `judgment_failed` |
| `weight_calculation.tie_break_applied = true` かつ `judgment_confidence ≥ 0.4` | 1 回リトライ（同点処理の confidence 引き下げ要求）→ 不一致継続なら `judgment_failed` |

## PR1 での制限

- スキーマ検証は Orchestrator が行うが、自動的な linter は実装しない（PR3）
- `dimension` / `premise` フィールドは記録するが、PR1 では判定に使わない（PR2 で類型判定に使用）
- COUNCIL-LOG エントリの後追記は手動（PR3 で自動化）
