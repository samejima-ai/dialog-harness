# COUNCIL-LOG

Council 発動の append-only ログ。

## 運用ルール

- **append-only の定義**: 既存エントリの**削除・書き換え禁止**。新しいエントリは時系列昇順で末尾追加のみ。エントリ順序の変更も禁止
- **記録タイミング**: Judgment Agent の出力取得時点で 1 エントリを append する。実装者の合意確定時点で下記の「合意プロセス後追記フィールド」を **null → 値** に埋め込む
- **粒度**: 1 invocation = 1 エントリ（follow-up 質問は同じエントリ内に追記）
- **監査用途**: F1（週次）/ F2（月次）/ F3（四半期）儀式で集計し、傾向分析に使用
- **プライバシー**: 社外秘情報が含まれ得るため、skill 内部に閉じて保管する

### append-only の例外条項（合意プロセスの後追記）

合意プロセスは**発動の完結点**であり append 対象の新規情報だが、COUNCIL-LOG の粒度設計（1 invocation = 1 entry）上、新エントリを作ると invocation_id 対応が煩雑化する。この妥協点として、以下のフィールドに限り **null → 値への単方向の埋め込み**を許容する：

| フィールド | 値 | 条件 |
|------------|-----|------|
| `implementer_consent` | `"agreed_recommended"` / `"agreed_with_modification"` / `"escalated"` | 合意プロセス完了時 |
| `follow_up_questions_count` | 0-3 の整数 | 合意プロセス完了時 |
| `agreed_at` | ISO 8601 タイムスタンプ | 合意プロセス完了時 |
| `modification_note` | 自由記述 | `agreed_with_modification` の場合のみ |
| `escalation_reason` | 自由記述 | `escalated` の場合のみ |

**許容条件**: これらのフィールドが発動時点で **null として宣言されていた場合に限り**、単方向の埋め込み（null → 値）を認める。

**禁止事項**:

- 一度値を埋めたフィールドの書き換え
- null 宣言されていないフィールドの新規追加
- 他フィールド（invocation_id / timestamp / persona_summary / judgment 系 等）の削除・改変
- 合意プロセス情報以外の後追記（訂正は新エントリで行う）
- エントリ順序の変更

**監査マーカー**: `implementer_consent != null` を「合意完了済み」のマーカーとして扱える。`null` のままのエントリは合意プロセス未完 = 進行中または放棄された invocation。

### 施行時点と遡及適用

本例外条項は **PR1 マージ以降に発行されるエントリ**（施行時点以降）に対して適用する。

施行時点より前に発行された既存エントリ（`r7k3t1` / `b7e2f1` / `m4t4q1`）には、Copilot 再レビュー指摘 (#11) を契機として後追記対象フィールドの **null プレースホルダを補完する遡及措置**を一度だけ実施した。これは「null 宣言されていないフィールドの新規追加禁止」ルールに対する **例外条項施行前事象への一度限りの遡及補完** として扱い、以降の遡及的書き換えは禁止する。

## エントリスキーマ（必須フィールド）

| フィールド | 説明 |
|-----------|------|
| `invocation_id` | Pre-Check が採番した一意 ID |
| `timestamp` | ISO 8601（発動時刻） |
| `source_skill` | 呼び出し元スキル（例: `layer1-autonomous-dev`） |
| `council_type` | `business` / `life` / `hybrid` |
| `question_to_answer` | 問いの文言 |
| `category` | situational_modifier 適用カテゴリ |
| `phase_reached` | `phase_1` / `phase_2`（PR2 以降） / `phase_3` |
| `conflict_type` | `unanimous` / `simple_conflict` / `A`-`G`（PR2 以降） |
| `final_weights` | Orchestrator が算出した重み |
| `judgment_confidence` | Judgment Agent の自己申告 |
| `recommended` | Judgment Agent 推奨案 |
| `minority_opinion` | 少数意見の要約 |
| `human_escalated` | bool |
| `implementer_consent` | 合意時に追記。値は `agreed_recommended` / `agreed_with_modification` / `escalated` の enum |

詳細スキーマは [../references/output-format.md](../references/output-format.md) §8 を参照。

## エントリ形式

各エントリは `## <invocation_id>` 見出しで開始し、以下を fenced JSON で記述する：

```
## council-2026-04-21T12:34:56Z-a1b2c3

\`\`\`json
{
  "invocation_id": "council-2026-04-21T12:34:56Z-a1b2c3",
  "timestamp": "2026-04-21T12:34:56Z",
  ...
}
\`\`\`

### 合意プロセス記録（任意）

実装者の理解・質問・方針決定の経緯を自由記述。
```

---

<!-- エントリはここから下に追記される。最新が下（時系列昇順） -->

## council-2026-04-21T12:00:00Z-r7k3t1

```json
{
  "invocation_id": "council-2026-04-21T12:00:00Z-r7k3t1",
  "timestamp": "2026-04-21T12:00:00Z",
  "source_skill": "rtk-integration",
  "council_type": "business",
  "question_to_answer": "dialog-harness の rtk-integration スキルは将来切り出し可能な構造を維持すべきか、それとも dialog-harness 本体と密結合にして最適化すべきか",
  "category": "conception",
  "category_fallback": false,
  "phase_reached": "phase_3",
  "conflict_type": "unanimous",
  "final_weights": {
    "経営者": 3,
    "開発者": 3,
    "哲学者": 5
  },
  "persona_summary": {
    "経営者": { "stance": "案A: 切り出し可能な構造を維持", "confidence": 0.75, "dimension": "機会損失" },
    "開発者": { "stance": "案A: 切り出し可能な構造を維持", "confidence": 0.9,  "dimension": "保守性" },
    "哲学者": { "stance": "案A: 切り出し可能な構造を維持", "confidence": 0.65, "dimension": "意味" }
  },
  "judgment_confidence": 0.82,
  "recommended": "案A: rtk-integration スキルは将来切り出し可能な構造（自己完結 + 通知のみの越境パッチ）を維持する",
  "minority_opinion": "全員一致だが dimension が機会損失/保守性/意味で異なる多様性あり。共通懸念は『疎結合の教条化リスク』『切り出し計画不在時の開発遅延』『重複実装の発生』の 3 点。",
  "human_escalated": false,
  "implementer_consent": null,
  "follow_up_questions_count": null,
  "agreed_at": null,
  "modification_note": null,
  "escalation_reason": null
}
```

### 合意プロセス記録

PR1 Walking Skeleton テスト実行のため、実装者による合意プロセスはこのエントリ生成時点では未実施。
後続の合意プロセスで `implementer_consent` を追記する設計。

（例外条項施行前のエントリであり、null プレースホルダ 4 件は PR1 マージ時の遡及補完で追加された。以降の書き換えは禁止）

## council-2026-04-21T00:00:00Z-b7e2f1

```json
{
  "invocation_id": "council-2026-04-21T00:00:00Z-b7e2f1",
  "timestamp": "2026-04-21T00:00:00Z",
  "source_skill": "layer1-autonomous-dev",
  "council_type": "business",
  "category": "implementation",
  "category_fallback": false,
  "question_to_answer": "POST /extract の PDF テキスト抽出ライブラリとして、pdfplumber (案A) と pymupdf (案B) のどちらを採用すべきか。",
  "phase_reached": "phase_3",
  "conflict_type": "simple_conflict",
  "final_weights": { "経営者": 2, "開発者": 6, "哲学者": 2 },
  "persona_summary": {
    "経営者": { "stance": "案A: pdfplumber", "confidence": 0.7, "dimension": "リスク" },
    "開発者": { "stance": "案A: pdfplumber", "confidence": 0.85, "dimension": "保守性 / 可逆性" },
    "哲学者": { "stance": "第3の道: extractor 抽象 + デフォルト案A + 案B opt-in", "confidence": 0.55, "dimension": "意味 / 前提への問い" }
  },
  "judgment_confidence": 0.78,
  "recommended": "案A (pdfplumber) + extractor 抽象レイヤ（哲学者の第3の道を mitigation として統合）",
  "minority_opinion": "哲学者の『今選ばない』という構造的示唆。抽象レイヤで差し替え余地を残すこと。",
  "human_escalated": false,
  "implementer_consent": "agreed_with_modification",
  "follow_up_questions_count": 0,
  "agreed_at": "2026-04-21T00:05:00Z",
  "modification_note": "案A (pdfplumber) を採用しつつ哲学者の第3の道 (extractor 抽象レイヤ) を mitigation として統合",
  "escalation_reason": null
}
```

### 合意プロセス記録

eval-B-l1-end-to-end/with_skill のドライラン (iteration-1)。layer1-autonomous-dev の step 4 で PDF 抽出ライブラリ選定の判断点を検出し、step 4.5 に従って Council を起動。Judgment (0.78) を受領後、実装者は `agreed_with_modification` で合意：案A (pdfplumber, MIT) を採用しつつ哲学者の第3の道 (extractor 抽象レイヤ) を mitigation として実装に統合。詳細は `.claude/skills/council-workspace/iteration-1/eval-B-l1-end-to-end/with_skill/outputs/09-l1-consensus.md` 参照。

（例外条項施行前のエントリであり、`follow_up_questions_count` / `agreed_at` / `modification_note` / `escalation_reason` の 4 フィールドは PR1 マージ時の遡及補完で JSON 本体に昇格。以前は合意プロセス記録本文に散文で記載されていた）

## council-2026-04-21T15:30:00Z-m4t4q1

```json
{
  "invocation_id": "council-2026-04-21T15:30:00Z-m4t4q1",
  "timestamp": "2026-04-21T15:30:00Z",
  "source_skill": "skill-creator",
  "council_type": "business",
  "category": "judgment",
  "category_fallback": false,
  "question_to_answer": "PR1 council skill のマージ前に、検出された 3 件の不備（カテゴリ選択基準の不在 / invocation_id 採番主体不明 / 第3の道 stance の conflict_type 分類規定なし）をどこまで修正すべきか",
  "phase_reached": "phase_3",
  "conflict_type": "unanimous",
  "final_weights": {
    "経営者": 4,
    "開発者": 4,
    "哲学者": 3
  },
  "persona_summary": {
    "経営者": { "stance": "案1: 1, 2 だけ PR1 で直す / 3 は PR2 送り", "confidence": 0.75, "dimension": "ROI / 機会損失" },
    "開発者": { "stance": "案1", "confidence": 0.9, "dimension": "保守性 / Shift Left" },
    "哲学者": { "stance": "案1", "confidence": 0.65, "dimension": "意味 / 不完全性の受容" }
  },
  "judgment_confidence": 0.85,
  "recommended": "案1: 不備 1（カテゴリ選択ガイド）と 2（invocation_id 採番手順）を PR1 で最小追記し、3（第3の道 stance の conflict_type 分類）は conflict-typology.md に PR2 予告メモとして残す",
  "minority_opinion": "全員一致だが共通懸念として『1, 2 の追記が想定外に膨らみ Walking Skeleton 原則を破壊するリスク』が複数ペルソナから提起された。1, 2 の修正は最小限の追記に留めるべき（カテゴリ選択ガイドは『迷ったら judgment にフォールバック』程度、invocation_id 採番者は『Pre-Check が ISO 8601 + 6-char random で発番』と一行追記程度）。哲学者は本件が『Council を Council に諮る』メタ反復である点を指摘しており、PR1 完了後にこの反復構造を design-history.md に短く記録することを推奨。",
  "human_escalated": false,
  "implementer_consent": "agreed_with_modification",
  "follow_up_questions_count": 0,
  "agreed_at": "2026-04-21T15:35:00Z",
  "modification_note": "案1 を採用し、哲学者 minority_opinion の推奨（メタ反復構造の記録）を mitigation として design-history.md に追記",
  "escalation_reason": null
}
```

### 合意プロセス記録

PR1 council skill 実装後の検証で発見された 3 件の不備の修正範囲を、Council 自身に諮るメタ反復。実装者（samejima-ai + Claude）は案1 を即実行：

- `pre-check.md` に category 選択ガイド（7 カテゴリ × 典型場面）と invocation_id 採番手順（`council-<ISO 8601 Z>-<6-char alnum>`）を追記
- `output-format.md` に invocation_id の採番主体が Pre-Check のみである旨を明記し、pre-check.md への相互参照を追加
- `conflict-typology.md` に「第3の道」stance の扱いを PR2 未決事項として明記（本 COUNCIL-LOG エントリ `b7e2f1` を実例として参照）
- `design-history.md` に本メタ反復（Council を Council に諮る自己言及構造）を短く記録 ← 哲学者 minority_opinion の mitigation

（例外条項施行前のエントリ。元の `implementer_consent: "agreed"` は enum 違反だったため、PR1 マージ時の遡及補完で `agreed_with_modification` に訂正し、mitigation 内容を `modification_note` に昇格。以前は散文で記載されていた `follow_up_questions_count` / `agreed_at` も同時に JSON 本体に昇格）

## council-2026-04-21T16:00:00Z-p7c7k1

```json
{
  "invocation_id": "council-2026-04-21T16:00:00Z-p7c7k1",
  "timestamp": "2026-04-21T16:00:00Z",
  "source_skill": "skill-creator",
  "council_type": "business",
  "category": "judgment",
  "category_fallback": false,
  "question_to_answer": "PR1 council skill のマージ前に、Copilot 再レビューで検出された 7 件の不整合をどこまで修正すべきか",
  "phase_reached": "phase_3",
  "conflict_type": "unanimous",
  "final_weights": {
    "経営者": 4,
    "開発者": 4,
    "哲学者": 3
  },
  "persona_summary": {
    "経営者": { "stance": "案1", "confidence": 0.75, "dimension": "ROI / 機会損失" },
    "開発者": { "stance": "案1", "confidence": 0.9, "dimension": "保守性 / Shift Left" },
    "哲学者": { "stance": "案1", "confidence": 0.65, "dimension": "意味 / 不完全性の受容" }
  },
  "judgment_confidence": 0.82,
  "recommended": "案1: Copilot 再レビュー指摘 7 件を全て 1 コミットで PR1 内修正。2 の遡及修正は『例外条項施行前エントリは適用外』の注釈付きで null プレースホルダを追加、7 は `pre_check_failed` + reason で life Council 扱いを統一",
  "minority_opinion": "全員一致だが共通懸念: 修正スコープが Walking Skeleton 原則を破壊するほど膨らむリスク。経営者は案2 へのフォールバック余地、哲学者は完璧主義への警戒とコミットメッセージに Walking Skeleton 精神を明記すべき、開発者は『append-only 例外の例外』の将来的複雑化を懸念",
  "human_escalated": false,
  "consensus_mode": "auto_agree",
  "implementer_consent": "agreed_recommended",
  "follow_up_questions_count": 0,
  "agreed_at": "2026-04-21T16:05:00Z",
  "modification_note": null,
  "escalation_reason": null
}
```

### 合意プロセス記録

Copilot 再レビュー (PR #11 commit 271a5bb) で検出された 7 件の不整合の修正範囲を、Council に諮るメタ反復 (m4t4q1 に続く 2 回目)。consensus_mode = `auto_agree` の PR2 先行適用として、実装者 (Claude) は即同意し案1 を実行：

- `council/SKILL.md`: philosophy.md 相対パスを `../layer0-spec-architect/...` に修正
- `orchestrator.md`: Judgment Agent 入力例で `{元の発動要請の question_to_answer}` / `{元の発動要請の options}` に明示化
- `consensus-protocol.md`: follow-up 例の `original_invocation_id` に `council-` prefix 追加
- `pre-check.md`: life Council 要請時の応答を `pre_check_failed` + `reason: "life_council_not_implemented_in_pr1"` に統一（`output-format.md` §2 スキーマ準拠）
- `history/COUNCIL-LOG.md`:
  - 必須フィールド表の `implementer_consent` を enum 定義に修正
  - 既存 3 エントリ (`r7k3t1` / `b7e2f1` / `m4t4q1`) に後追記 4 フィールドの null プレースホルダを遡及補完
  - `m4t4q1` の `"agreed"` (enum 違反) を `"agreed_with_modification"` に訂正し、mitigation 内容を `modification_note` に昇格
  - 「施行時点と遡及適用」節を追加し、遡及補完を「施行前事象への一度限りの例外措置」として明示

哲学者 minority_opinion（完璧主義への警戒）を受け、本コミットは Walking Skeleton 原則の枠内で整合性回復のみに留める方針。新規機能追加なし。
