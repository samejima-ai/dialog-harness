# COUNCIL-LOG

Council 発動の append-only ログ。

## 運用ルール

- **append-only**: 既存エントリは改変しない。訂正は新エントリで行う
- **記録タイミング**: Judgment Agent の出力取得時点で1エントリ、実装者の合意確定時点で `implementer_consent` を追記
- **粒度**: 1 invocation = 1 エントリ（follow-up 質問は同じエントリ内に追記）
- **監査用途**: F1（週次）/ F2（月次）/ F3（四半期）儀式で集計し、傾向分析に使用
- **プライバシー**: 社外秘情報が含まれ得るため、skill 内部に閉じて保管する

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
| `implementer_consent` | 合意時に追記。内容は自由記述 |

詳細スキーマは [../references/output-format.md](../references/output-format.md) §7 を参照。

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
  "implementer_consent": null
}
```

### 合意プロセス記録

PR1 Walking Skeleton テスト実行のため、実装者による合意プロセスはこのエントリ生成時点では未実施。
後続の合意プロセスで `implementer_consent` を追記する設計。

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
  "implementer_consent": "agreed_with_modification"
}
```

### 合意プロセス記録

eval-B-l1-end-to-end/with_skill のドライラン (iteration-1)。layer1-autonomous-dev の step 4 で PDF 抽出ライブラリ選定の判断点を検出し、step 4.5 に従って Council を起動。Judgment (0.78) を受領後、実装者は `agreed_with_modification` で合意：案A (pdfplumber, MIT) を採用しつつ哲学者の第3の道 (extractor 抽象レイヤ) を mitigation として実装に統合。詳細は `.claude/skills/council-workspace/iteration-1/eval-B-l1-end-to-end/with_skill/outputs/09-l1-consensus.md` 参照。follow_up_questions_count: 0 / agreed_at: 2026-04-21T00:05:00Z。

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
  "implementer_consent": "agreed"
}
```

### 合意プロセス記録

PR1 council skill 実装後の検証で発見された 3 件の不備の修正範囲を、Council 自身に諮るメタ反復。実装者（samejima-ai + Claude）は `agreed` で合意し、案1 を即実行：

- `pre-check.md` に category 選択ガイド（7 カテゴリ × 典型場面）と invocation_id 採番手順（`council-<ISO 8601 Z>-<6-char alnum>`）を追記
- `output-format.md` に invocation_id の採番主体が Pre-Check のみである旨を明記し、pre-check.md への相互参照を追加
- `conflict-typology.md` に「第3の道」stance の扱いを PR2 未決事項として明記（本 COUNCIL-LOG エントリ `b7e2f1` を実例として参照）
- `design-history.md` に本メタ反復（Council を Council に諮る自己言及構造）を短く記録

follow_up_questions_count: 0 / agreed_at: 2026-04-21T15:35:00Z
