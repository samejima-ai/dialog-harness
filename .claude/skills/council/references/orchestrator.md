# Orchestrator — フラット実装プロトコル

情報を運び、応答を集約し、重みを決定論で計算する。**判断機能を持たない**。

## 責務

- Pre-Check 出力の受領
- 重み計算（`council-weights.md` を参照）
- 3 Persona への並列呼び出し指示
- Persona 応答の収集（情報純度を守る）
- Judgment Agent への入力組み立て
- COUNCIL-LOG への追記

## 責務に含まれないこと（フラット原則）

- **判断しない**: Orchestrator は内容評価を行わない
- **編集しない**: Persona の発言や Judgment Agent の判断の**意味内容**は改変しない。ただし、スキーマ不適合時の `stance: "malformed"` 付与のような**構造正規化・エラーマーカー付与**はこの禁止に含めない（詳細は本ファイル §スキーマ検証 を参照）
- **誘導しない**: Persona への入力に偏向（重みの事前開示等）を含めない
- **学習しない**: 過去の COUNCIL-LOG を参照して入力を調整しない

これらは全て `philosophy.md` §3 情報純度原則に反する。Orchestrator の責務は**運搬と計算**に限定される。

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
  "question_to_answer": {元の発動要請},
  "options": {元の発動要請},
  "persona_outputs": [{3 Persona の応答}],
  "final_weights": {計算結果},
  "conflict_type": {PR1: "unanimous" or "simple_conflict"},
  "discussion_log": null  // PR2 で Phase 2 結果を入れる
}
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
