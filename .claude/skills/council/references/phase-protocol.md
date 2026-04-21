# Phase Protocol — Phase 0→3 処理規格

Council の処理フロー全体の規格。Orchestrator が本プロトコルに従って各 Phase を順次実行する。

## 全体フロー

```
[入力受領]
   ↓
[Phase 0] Pre-Check  → pre-check.md
   ↓ (pre_check_passed)
[重み計算]           → orchestrator.md §重み計算プロトコル
   ↓
[Phase 1] 3 Persona 並列発言
   ↓
[対立度判定]
   ↓
[Phase 2] 討論（PR1 はスキップ）
   ↓
[Phase 3] Judgment Agent → judgment-agent.md
   ↓
[出力返却 + ログ追記]
```

## Phase 0: Pre-Check

詳細は [pre-check.md](pre-check.md)。

- 入力検証
- Council 種別判定（PR1 は business 固定）
- invocation_id 発行
- 不適合時は差し戻し（Council を起動しない）

## 重み計算

詳細は [orchestrator.md](orchestrator.md) §重み計算プロトコル。

- `council-weights.md` を読み込み
- `final_weight[persona]` を決定論で算出
- Persona へは渡さない（Judgment Agent のみに渡す）

## Phase 1: 3 Persona 独立並列発言

### 目的

各視点の**独立な**意見を生成する。本人らしさの再現と、視点の多様性の確保。

### プロトコル

1. Orchestrator が 3 Persona を並列呼び出し（逐次禁止）
2. 各 Persona は `personas/business/{ceo,dev,phil}.md` の system prompt + temperature 設定で起動
3. 各 Persona は `context / options / question_to_answer` のみ受け取る
4. **他 Persona の出力、重み配分、過去ログは渡さない**（情報純度）
5. 各 Persona は `output-format.md` 準拠の JSON を返す

### 出力フォーマット

各 Persona の出力：

```json
{
  "persona": "経営者",
  "stance": "実装する | しない | 保留",
  "reason": "...（300字以内）",
  "confidence": 0.7,
  "dimension": "ROI | 保守性 | 意味 | meta",
  "premise": "前提となる時間軸や条件",
  "concerns": ["懸念点1", "懸念点2"]
}
```

`dimension` と `premise` は対立類型判定（PR2）に必須。PR1 でも記録は取る。

## 対立度判定

### PR1（簡略版）

2 値のみ：

- **unanimous**: 3 Persona の `stance` が全て一致
- **simple_conflict**: それ以外

### PR2 以降（完全版）

対立類型 A-G の決定論的分類。詳細は [conflict-typology.md](conflict-typology.md)。

### PR1 での動作

- `unanimous`: Phase 2 スキップ、Phase 3 へ（Judgment Agent は多様性評価モードで動作）
- `simple_conflict`: Phase 2 スキップ（PR1 は未実装）、Phase 3 へ（Judgment Agent が重み付きで単一回答を導出）

## Phase 2: 討論

### PR1 ではスキップ

`conflict_type` を `discussion_log: null` と共に Phase 3 に渡す。

### PR2 以降の予告

対立類型に応じた討論形式：

- **反駁形式**（類型 A）: 対立する Persona に反論を書かせる
- **質問形式**（類型 C）: 確信度低い Persona から高い Persona へ質問

詳細プロトコルは PR2 で `discussion-formats.md` に記述。

## Phase 3: Judgment Agent

詳細は [judgment-agent.md](judgment-agent.md)。

### 入力

- Phase 1 の 3 Persona 出力
- `final_weights`（Orchestrator 計算結果）
- `conflict_type`（PR1: unanimous / simple_conflict）
- `discussion_log`（PR1: null）
- 元の `question_to_answer` と `options`

### 出力

```json
{
  "recommended": "...",
  "reasoning": "...",
  "minority_opinion": "...",
  "weight_note": "...",
  "judgment_confidence": 0.8,
  "final_decision": null
}
```

`final_decision` は**常に null**。実装者の合意プロセスが埋める（`consensus-protocol.md`）。

### 自動エスカレーション

`judgment_confidence < 0.5` の場合、Orchestrator は Judgment Agent 出力と共に `"human_escalation_required": true` を付記して返す。

## Phase 間のデータ受け渡し

| Phase | 入力 | 出力 | 次 Phase への連携 |
|-------|------|------|-----------------|
| 0 | 発動要請 | pre_check 結果 | council_type / category |
| 重み計算 | council-weights + category | final_weights | Phase 3 のみに渡す |
| 1 | context / options / question_to_answer | 3 Persona 出力 | 対立度判定 + Phase 3 |
| 対立度 | 3 Persona 出力 | conflict_type | Phase 2 / Phase 3 |
| 2 | （PR1 スキップ） | null | Phase 3 |
| 3 | Phase 1 出力 + weights + conflict + discussion | Judgment | 出力返却 |

## タイムアウト

| Phase | タイムアウト |
|-------|-------------|
| Phase 0 | 5 秒（決定論） |
| 重み計算 | 1 秒（決定論） |
| Phase 1 | 60 秒（3 Persona 並列の合計） |
| 対立度判定 | 1 秒（決定論） |
| Phase 2 | PR1 N/A（PR2 で定義） |
| Phase 3 | 60 秒 |

タイムアウト超過時は `"status": "timeout"` で返却。COUNCIL-LOG には `timeout_at_phase` を記録。

## エラー時の扱い

- **Phase 0 失敗**: 発動要請を差し戻し、Council を起動しない
- **Phase 1 失敗（Persona 応答不備）**: 該当 Persona を `stance: "malformed"` として Phase 3 に渡す
- **Phase 3 失敗**: `"status": "judgment_failed"` で返却、人間エスカレーション
- **全 Phase 共通**: エラー内容を COUNCIL-LOG に記録し、実装者に返却する
