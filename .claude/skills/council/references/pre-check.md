# Pre-Check — Phase 0 Council 種別判定

発動要請を受理し、どの Council を起動すべきかを決定論的に判定する。

## 責務

- Council 種別の判定（business / life / hybrid）
- 発動要請フォーマットの検証
- 入力不備時の差し戻し

## 判定ルール（PR1 実装）

PR1 では **business 固定**。以下のロジックで簡略実装する：

```
if source_skill in ["layer1-autonomous-dev", "layer1-independent-reviewer",
                    "layer2-orchestrator", "layer2-integration-verifier"]:
    → business Council
elif source_skill == "layer0-spec-architect" and category == "life":
    → PR3 で有効化。PR1 では pre_check_failed +
       reason: "life_council_not_implemented_in_pr1" を返して差し戻す
else:
    → business Council （デフォルト）
```

life Council 要請時の PR1 応答形式（`output-format.md` §2 の `pre_check_failed` スキーマに準拠）：

```json
{
  "status": "pre_check_failed",
  "reason": "life_council_not_implemented_in_pr1",
  "detail": "life Council is scheduled for PR3. Current PR1 scope is business Council only."
}
```

## 判定ルール（PR3 完全版の予告）

PR3 では以下に拡張：

| 判定条件 | Council | 備考 |
|---------|---------|------|
| category が `implementation/operation/maintenance/issue_triage/error_handling` | business | 事業系の判断 |
| category が `life/health/family/tradeoff_personal` | life | 人生系の判断（L0 専用） |
| 判定曖昧（入力から読み取れない） | hybrid | 例外処理、常用しない |

## 入力検証

必須フィールドが欠落している場合、Pre-Check は発動要請を**差し戻す**（Council を起動しない）：

- `context`（状況説明文字列、100-2000 字）
- `options`（検討中の選択肢配列、2-8 個）
- `question_to_answer`（答えるべき問い、1 文）
- `source_skill`（発動元スキル名）
- `category`（重み配分カテゴリ、`implementation` 等）

差し戻し時の応答：

```json
{
  "status": "pre_check_failed",
  "reason": "required field 'options' is missing or has < 2 entries",
  "required_fields": ["context", "options", "question_to_answer", "source_skill", "category"]
}
```

## category 選択ガイド（発動側向け）

発動側（L1 等）が `category` を指定する時の振り分け指針。迷ったら `judgment` にフォールバックしてよい（COUNCIL-LOG に `category_fallback: true` は記録されない — 明示指定としての判定）。

| 典型場面 | 推奨 category |
| --- | --- |
| 実装方針・ライブラリ選定・アルゴリズム選択 | `implementation` |
| 不可逆操作・リリース・デプロイ判断 | `operation` |
| リファクタ方針・既存コード修正 | `maintenance` |
| 障害・不具合の初動判断 | `issue_triage` |
| エラーハンドリング設計・例外方針 | `error_handling` |
| 実装範囲・スコープ・PR 境界のメタ判断 | `judgment` |
| 新規構造・思想・将来性の議論 | `conception` |

判定が割れる時は「最も質問の本質に近い 1 つ」を選ぶ。完全な一意性は求めない（振り返り儀式で傾向を監査する）。

## Pre-Check 出力

```json
{
  "status": "pre_check_passed",
  "council_type": "business",
  "category": "implementation",
  "invocation_id": "council-2026-04-21T15:30:00Z-a1b2c3"
}
```

`invocation_id` は Pre-Check が採番する。形式は `council-<ISO 8601 timestamp with Z>-<6 文字の英小文字+数字ランダム>`。PR1 簡略実装では以下を採用：

```python
invocation_id = "council-" + utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") + "-" + random_alnum_6()
```

採番主体は Pre-Check のみ。以降 COUNCIL-LOG・追加質問プロトコル・合意プロセスですべて同じ ID を参照する。

## PR1 での簡略化

- 判定曖昧時の hybrid 発動はしない（business にフォールバック）
- category 未指定時は `judgment` にフォールバック（COUNCIL-LOG に `category_fallback: true` を記録）
- life Council の判定ロジックは書き出すが、PR1 実装では `pre_check_failed` + `reason: "life_council_not_implemented_in_pr1"` で差し戻す（`output-format.md` §2 スキーマに準拠）

## 決定論性の担保

Pre-Check は LLM ではなく決定論的ロジックで実装する（`philosophy.md` §2 Shift Left 原則）。
判定に曖昧さが発生した場合は hybrid にフォールバック（PR3）するか、business デフォルト（PR1）にする。
LLM による推論判定は禁止する（判定コスト・情報純度の両方で不利）。
