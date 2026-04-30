# COUNCIL-LOG

Council 発動の履歴（append-only）。
スキーマは `.claude/skills/crosscut-council/references/output-format.md` §8 に準拠。

## 訂正記録（PR #21 マージ後の一度限りの整合修正）

PR #21（v5.2.0）merge 後の Copilot review で以下のスキーマ違反を検出し、append-only の例外として一度限りの訂正を実施した（PR: chore/address-pr-21-22-23-reviews）:

1. **invocation_id 重複**: `d4mtr1` を 4 entry で再利用していた（spec: 「1 invocation = 1 エントリ」違反）。4 論点それぞれに固有 ID を割当： `d4mtr1` (論点 1: 命名) / `d4mtr2` (論点 2: 機構名) / `d4mtr3` (論点 3: バージョン) / `d4mtr4` (論点 4: スコープ)。元々は同 timestamp での 4 sub-judgment を batch session として記録していたが、各エントリが独立 judgment 出力を持つ構造のため renumber が schema 整合に最も近い。なお、本訂正以前のドキュメント（`history/CHANGELOG.md` / `history/INTENT.md` / `history/REGIME-LOG.md` / `history/ARCH-DECISIONS.md` / `delivery/SELF-VERIFICATION-v5.2.0.md` 等）で `council-2026-04-29T21:00:00Z-d4mtr1` を「4 論点一括の invocation_id」として参照している記述は、以後は論点別に読み替える。すなわち論点 1 → `d4mtr1`、論点 2 → `d4mtr2`、論点 3 → `d4mtr3`、論点 4 → `d4mtr4` に対応する（旧記述の歴史的事実は保存し、本訂正記録が翻訳鍵を提供する）。
2. **conflict_type schema 違反**: `unanimous_with_variance` は PR1 schema (`unanimous` / `simple_conflict`) に存在しない。`unanimous` に修正、variance は既に `persona_summary` に保持されている。

これは crosscut-council/history/COUNCIL-LOG.md の m4t4q1 (`agreed` → `agreed_with_modification`) 訂正と同型の例外措置。本訂正以降、同種の renumber/schema 修正は行わない。

---

- invocation_id: "council-2026-04-29T21:00:00Z-d4mtr1"
  timestamp: "2026-04-29T21:00:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "次元論の命名統一（D-numbering / Tier naming / 階層形容詞）"
  council_type: "business"
  category: "conception"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "simple_conflict"
  final_weights:
    経営者: 3
    開発者: 3
    哲学者: 5
  persona_summary:
    経営者: { stance: "案 a: D-numbering", confidence: 0.7 }
    開発者: { stance: "案 a: D-numbering", confidence: 0.92 }
    哲学者: { stance: "案 a + 案 c のハイブリッド（思想文書並走）", confidence: 0.65 }
  judgment_confidence: 0.78
  recommended: "案 a: D-numbering（D1〜D5）を機械可読命名として採用、思想文書では階層形容詞を並走"
  human_escalated: false
  implementer_consent: "agreed_recommended"
  follow_up_questions_count: 0
  agreed_at: "2026-04-29T21:30:00Z"

- invocation_id: "council-2026-04-29T21:00:00Z-d4mtr2"
  timestamp: "2026-04-29T21:00:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "D4 検査機構の名称（meta-verifier / harness-verifier / dh-integrity / singularity）"
  council_type: "business"
  category: "conception"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "simple_conflict"
  final_weights:
    経営者: 3
    開発者: 3
    哲学者: 5
  persona_summary:
    経営者: { stance: "(ii) harness-verifier/", confidence: 0.65 }
    開発者: { stance: "(ii) harness-verifier/", confidence: 0.88 }
    哲学者: { stance: "(iv) singularity/ — 副題に harness-verifier 併記", confidence: 0.6 }
  judgment_confidence: 0.82
  recommended: "harness-verifier/ を機械可読名として採用、PHILOSOPHY.md で singularity 併記の二重命名"
  human_escalated: false
  implementer_consent: "agreed_recommended"
  follow_up_questions_count: 0
  agreed_at: "2026-04-29T21:30:00Z"

- invocation_id: "council-2026-04-29T21:00:00Z-d4mtr3"
  timestamp: "2026-04-29T21:00:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "バージョン昇格区分（v5.2.0 minor / v6.0.0 major / v5.2.0 + v5.3.0 後送）"
  council_type: "business"
  category: "judgment"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "simple_conflict"
  final_weights:
    経営者: 4
    開発者: 4
    哲学者: 3
  persona_summary:
    経営者: { stance: "(c) v5.2.0 minor + philosophy verifier 後送", confidence: 0.75 }
    開発者: { stance: "(a) v5.2.0 minor", confidence: 0.9 }
    哲学者: { stance: "(b) v6.0.0 major", confidence: 0.55 }
  judgment_confidence: 0.7
  recommended: "(c) v5.2.0 minor で次元論 + D4 機構実装、philosophy verifier は v5.3.0 へ後送"
  human_escalated: false
  implementer_consent: "agreed_recommended"
  follow_up_questions_count: 0
  agreed_at: "2026-04-29T21:30:00Z"

- invocation_id: "council-2026-04-29T21:00:00Z-d4mtr4"
  timestamp: "2026-04-29T21:00:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "検証スコープ 5 項目の D4 対象妥当性"
  council_type: "business"
  category: "implementation"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "unanimous"
  final_weights:
    経営者: 2
    開発者: 6
    哲学者: 2
  persona_summary:
    経営者: { stance: "5項目維持 + 5層構造保全のスコープを D4 に明記", confidence: 0.7 }
    開発者: { stance: "5項目すべて D4 対象として妥当 + 各項目の実装定義明示化", confidence: 0.92 }
    哲学者: { stance: "5項目維持 + 第6項目『次元境界保全』を v5.3.0 候補温存", confidence: 0.6 }
  judgment_confidence: 0.85
  recommended: "5項目すべて D4 対象として実装、5層構造保全の D4 解釈を仕様書明示。第6項目は v5.3.0 候補"
  human_escalated: false
  implementer_consent: "agreed_recommended"
  follow_up_questions_count: 0
  agreed_at: "2026-04-29T21:30:00Z"

- invocation_id: "council-2026-04-29T22:30:00Z-c1fix1"
  timestamp: "2026-04-29T22:30:00Z"
  source_skill: "layer1-autonomous-dev"
  question_to_answer: "C-1 解決方針（自前パーサ拡張 / インライン化 / PyYAML 採用）"
  council_type: "business"
  category: "implementation"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "unanimous"
  final_weights:
    経営者: 2
    開発者: 6
    哲学者: 2
  persona_summary:
    経営者: { stance: "案 b: glossary.yml をインラインリスト形式に書き換え", confidence: 0.8 }
    開発者: { stance: "案 b + 案 a の最小限改修（block list 検出時 SyntaxError）併走", confidence: 0.9 }
    哲学者: { stance: "案 b + 案 a の構文制約を BOUNDARY.md / glossary.yml 冒頭コメントに昇格", confidence: 0.65 }
  judgment_confidence: 0.88
  recommended: "案 b 中核 + 案 a 防御 + 哲学者ドキュメント宣言の三段統合（subset YAML 形式宣言、block list 構文を SyntaxError 化、BOUNDARY.md §9 に独立性の代償条項追加）"
  human_escalated: false
  implementer_consent: "agreed_recommended"
  follow_up_questions_count: 0
  agreed_at: "2026-04-29T22:45:00Z"

- invocation_id: "council-2026-04-30T09:00:00Z-d4at01"
  timestamp: "2026-04-30T09:00:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "S/U/R 三軸スコア統合方針（議題 1 / D4 整合性監査 PR-γ）"
  council_type: "business"
  category: "conception"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "unanimous"
  final_weights:
    経営者: 3
    開発者: 3
    哲学者: 5
  persona_summary:
    経営者: { stance: "案A: 独立維持", confidence: 0.7, dimension: "ROI / 機会損失" }
    開発者: { stance: "案A: 独立維持", confidence: 0.8, dimension: "保守性 / 可逆性" }
    哲学者: { stance: "案A: 独立維持", confidence: 0.6, dimension: "意味 / 階層性" }
  judgment_confidence: 0.78
  weight_calculation:
    method: "weight_times_confidence"
    scores:
      - stance: "案A: 独立維持"
        supporters: ["経営者", "開発者", "哲学者"]
        weight_sum: 11
        weighted_score: 7.5
        components:
          - { persona: "経営者", weight: 3, confidence: 0.7 }
          - { persona: "開発者", weight: 3, confidence: 0.8 }
          - { persona: "哲学者", weight: 5, confidence: 0.6 }
    third_way_excluded: []
    max_score_stance: "案A: 独立維持"
    tie_break_applied: false
  weight_calculation_retry_count: 0
  recommended: "案A: 独立維持。3 つの S/U/R は射程が異なる（regime / Council 介入閾値 / hybrid）。共通用語表は M-4 で導入済"
  minority_opinion: "哲学者: 将来的な統合視点（案 B）を保持しつつ運用は独立で。glossary.yml の score_axes が単一典拠として機能"
  human_escalated: false
  consensus_mode: "auto_agree"
  implementer_consent: "agreed_recommended"
  follow_up_questions_count: 0
  agreed_at: "2026-04-30T09:00:30Z"

- invocation_id: "council-2026-04-30T09:01:00Z-d4at02"
  timestamp: "2026-04-30T09:01:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "DH-PHILOSOPHY-INSIGHTS.md 最終配置（議題 2 / D4 整合性監査 PR-γ）"
  council_type: "business"
  category: "operation"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "unanimous"
  final_weights:
    経営者: 4
    開発者: 4
    哲学者: 2
  persona_summary:
    経営者: { stance: "案A: history/ 維持", confidence: 0.6, dimension: "ROI / 運用コスト" }
    開発者: { stance: "案A: history/ 維持", confidence: 0.7, dimension: "YAGNI / 保守性" }
    哲学者: { stance: "案A: history/ 維持", confidence: 0.65, dimension: "意味 / 経緯記録" }
  judgment_confidence: 0.72
  weight_calculation:
    method: "weight_times_confidence"
    scores:
      - stance: "案A: history/ 維持"
        supporters: ["経営者", "開発者", "哲学者"]
        weight_sum: 10
        weighted_score: 6.5
        components:
          - { persona: "経営者", weight: 4, confidence: 0.6 }
          - { persona: "開発者", weight: 4, confidence: 0.7 }
          - { persona: "哲学者", weight: 2, confidence: 0.65 }
    third_way_excluded: []
    max_score_stance: "案A: history/ 維持"
    tie_break_applied: false
  weight_calculation_retry_count: 0
  recommended: "案A: history/ 維持。INSIGHTS.md は経緯ドキュメントとして INTENT.md と並列扱い。仕様核取り込みは v6.0.0 major で扱う"
  minority_opinion: "哲学者: 将来 reference 頻度上昇時の再判断余地を残す。signal 条件として『INSIGHTS への参照 month 1 件以上』を mitigation で監視"
  human_escalated: false
  consensus_mode: "auto_agree"
  implementer_consent: "agreed_recommended"
  follow_up_questions_count: 0
  agreed_at: "2026-04-30T09:01:30Z"

- invocation_id: "council-2026-04-30T09:02:00Z-d4at03"
  timestamp: "2026-04-30T09:02:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "philosophy.md 第 7 条「次元論と D4 の独立性」昇格スケジュール（議題 3 / D4 整合性監査 PR-γ）"
  council_type: "business"
  category: "conception"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "unanimous"
  final_weights:
    経営者: 3
    開発者: 3
    哲学者: 5
  persona_summary:
    経営者: { stance: "案A: v6.0.0 一括昇格", confidence: 0.7, dimension: "計画性 / コミュニケーションコスト" }
    開発者: { stance: "案A: v6.0.0 一括昇格", confidence: 0.75, dimension: "保守性 / バージョン境界" }
    哲学者: { stance: "案A: v6.0.0 一括昇格", confidence: 0.7, dimension: "意味 / 階層整合性" }
  judgment_confidence: 0.81
  weight_calculation:
    method: "weight_times_confidence"
    scores:
      - stance: "案A: v6.0.0 一括昇格"
        supporters: ["経営者", "開発者", "哲学者"]
        weight_sum: 11
        weighted_score: 7.85
        components:
          - { persona: "経営者", weight: 3, confidence: 0.7 }
          - { persona: "開発者", weight: 3, confidence: 0.75 }
          - { persona: "哲学者", weight: 5, confidence: 0.7 }
    third_way_excluded: []
    max_score_stance: "案A: v6.0.0 一括昇格"
    tie_break_applied: false
  weight_calculation_retry_count: 0
  recommended: "案A: v6.0.0 major で一括昇格。minor 内では予告強化（M-6）のみ実施。DIMENSIONS.md §11 残タスク表の集約参照を強化する"
  minority_opinion: "哲学者: harness-verifier monthly report で『dimension 境界跨ぎ試行』『D5 escalate 件数』を集計するように記録項目を v5.4.0 で追加すべき（v5.3.0 では先送り）"
  human_escalated: false
  consensus_mode: "auto_agree"
  implementer_consent: "agreed_recommended"
  follow_up_questions_count: 0
  agreed_at: "2026-04-30T09:02:30Z"

- invocation_id: "council-2026-04-30T09:03:00Z-d4at04"
  timestamp: "2026-04-30T09:03:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "5 本柱 vs 5 本柱+第 6 条 表記統一（議題 4 / D4 整合性監査 PR-γ、HIGH-1 思想統一案件）"
  council_type: "business"
  category: "conception"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "unanimous"
  final_weights:
    経営者: 3
    開発者: 3
    哲学者: 5
  persona_summary:
    経営者: { stance: "案A: P1-P5 統一", confidence: 0.7, dimension: "ROI / 後方互換" }
    開発者: { stance: "案A: P1-P5 統一", confidence: 0.85, dimension: "論理整合性 / 仕様核遵守" }
    哲学者: { stance: "案A: P1-P5 統一", confidence: 0.85, dimension: "意味 / 概念階層" }
  judgment_confidence: 0.88
  weight_calculation:
    method: "weight_times_confidence"
    scores:
      - stance: "案A: P1-P5 統一"
        supporters: ["経営者", "開発者", "哲学者"]
        weight_sum: 11
        weighted_score: 8.9
        components:
          - { persona: "経営者", weight: 3, confidence: 0.7 }
          - { persona: "開発者", weight: 3, confidence: 0.85 }
          - { persona: "哲学者", weight: 5, confidence: 0.85 }
    third_way_excluded: []
    max_score_stance: "案A: P1-P5 統一"
    tie_break_applied: false
  weight_calculation_retry_count: 0
  recommended: "案A: P1-P5 統一。philosophy.md（不変対象）と DIMENSIONS.md §8.1 が確定済の構造（5 本柱 = P1-P5、第 6 条 = 別概念）に harness-verifier 系（glossary.yml + PHILOSOPHY.md）と REGIME-LOG.md v5.2.0 行を整合化。glossary.yml `philosophy_pillars` から P6 を移動し別キー `philosophy_articles: 第1-6条` を新設"
  minority_opinion: "なし（全会一致）。共通理解: 「5 本柱 = 行動原則 (P1-P5)」と「第 6 条 = 関係性原則」は概念階層が異なる。同一カテゴリ内にまとめる harness-verifier 表記は階層混合の罠"
  human_escalated: false
  consensus_mode: "auto_agree"
  implementer_consent: "agreed_recommended"
  follow_up_questions_count: 0
  agreed_at: "2026-04-30T09:03:30Z"

- invocation_id: "council-2026-04-30T11:00:00Z-l0agg1"
  timestamp: "2026-04-30T11:00:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "cross-project ログ集約の Mirror 方式（Push/Pull/Council のみ Push/Hybrid）"
  council_type: "business"
  category: "conception"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "unanimous"
  final_weights:
    経営者: 3
    開発者: 3
    哲学者: 5
  persona_summary:
    経営者: { stance: "案A-3: Council のみ Push, 他は Pull", confidence: 0.75, dimension: "ROI / 既存資産活用" }
    開発者: { stance: "案A-3: Council のみ Push, 他は Pull", confidence: 0.85, dimension: "保守性 / 経路分離の明確性" }
    哲学者: { stance: "案A-3: Council のみ Push, 他は Pull", confidence: 0.7, dimension: "意味 / 即時性 vs 事後性の質的差" }
  judgment_confidence: 0.83
  weight_calculation:
    method: "weight_times_confidence"
    scores:
      - stance: "案A-3: Council のみ Push, 他は Pull"
        supporters: ["経営者", "開発者", "哲学者"]
        weight_sum: 11
        weighted_score: 8.3
        components:
          - { persona: "経営者", weight: 3, confidence: 0.75 }
          - { persona: "開発者", weight: 3, confidence: 0.85 }
          - { persona: "哲学者", weight: 5, confidence: 0.7 }
    third_way_excluded: []
    max_score_stance: "案A-3: Council のみ Push, 他は Pull"
    tie_break_applied: false
  weight_calculation_retry_count: 0
  recommended: "案A-3: Council のみ Push, 他は Pull。既存 ~/.claude/council-data/ の投資を活用し新規概念を最小化"
  minority_opinion: "なし（全会一致、dimension は ROI/保守性/意味と多様性あり）"
  human_escalated: false
  consensus_mode: "auto_agree"
  implementer_consent: null
  follow_up_questions_count: null
  agreed_at: null

- invocation_id: "council-2026-04-30T11:01:00Z-l0agg2"
  timestamp: "2026-04-30T11:01:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "cross-project ログ集約の対象スコープ（Council のみ / +DH evolution / +verification / すべて）"
  council_type: "business"
  category: "conception"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "unanimous"
  final_weights:
    経営者: 3
    開発者: 3
    哲学者: 5
  persona_summary:
    経営者: { stance: "案B-1: Council 判定のみ", confidence: 0.7, dimension: "ROI / MVP" }
    開発者: { stance: "案B-1: Council 判定のみ", confidence: 0.85, dimension: "YAGNI / 保守性" }
    哲学者: { stance: "案B-1: Council 判定のみ", confidence: 0.7, dimension: "意味 / 集約の本質" }
  judgment_confidence: 0.82
  weight_calculation:
    method: "weight_times_confidence"
    scores:
      - stance: "案B-1: Council 判定のみ"
        supporters: ["経営者", "開発者", "哲学者"]
        weight_sum: 11
        weighted_score: 8.15
        components:
          - { persona: "経営者", weight: 3, confidence: 0.7 }
          - { persona: "開発者", weight: 3, confidence: 0.85 }
          - { persona: "哲学者", weight: 5, confidence: 0.7 }
    third_way_excluded: []
    max_score_stance: "案B-1: Council 判定のみ"
    tie_break_applied: false
  weight_calculation_retry_count: 0
  recommended: "案B-1: Council 判定のみ。CTL 学習・権限委譲・振り返り調整 (F1) のいずれも council ログから派生可能"
  minority_opinion: "哲学者: F1 で『DH 自身の改修動向』を cross-project で見たいケースは将来出る可能性あり、v5.4.0 候補として B-2 (DH evolution 拡張) を温存"
  human_escalated: false
  consensus_mode: "auto_agree"
  implementer_consent: null
  follow_up_questions_count: null
  agreed_at: null

- invocation_id: "council-2026-04-30T11:02:00Z-l0agg3"
  timestamp: "2026-04-30T11:02:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "user-scope 集約時の Privacy フィルタ（全文転送/schema-only/自動匿名化/Council のみ匿名化）"
  council_type: "business"
  category: "judgment"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "unanimous"
  final_weights:
    経営者: 4
    開発者: 4
    哲学者: 3
  persona_summary:
    経営者: { stance: "案C-2: schema-only", confidence: 0.7, dimension: "ROI / リスク" }
    開発者: { stance: "案C-2: schema-only", confidence: 0.85, dimension: "保守性 / 機械可読性" }
    哲学者: { stance: "案C-2: schema-only", confidence: 0.8, dimension: "意味 / 集約の純粋性" }
  judgment_confidence: 0.85
  weight_calculation:
    method: "weight_times_confidence"
    scores:
      - stance: "案C-2: schema-only"
        supporters: ["経営者", "開発者", "哲学者"]
        weight_sum: 11
        weighted_score: 8.6
        components:
          - { persona: "経営者", weight: 4, confidence: 0.7 }
          - { persona: "開発者", weight: 4, confidence: 0.85 }
          - { persona: "哲学者", weight: 3, confidence: 0.8 }
    third_way_excluded: []
    max_score_stance: "案C-2: schema-only"
    tie_break_applied: false
  weight_calculation_retry_count: 0
  recommended: "案C-2: schema-only。final_weights / persona_summary / confidence / agreement_rate / category 等の構造データのみ user-scope へ転送、テキスト本文は project-scope に残す"
  minority_opinion: "なし（全会一致）。共通理解: 自動匿名化 (C-3) は完全な匿名化が不可能で誤検出が安全感を生み逆に構造的甘さを生む罠"
  human_escalated: false
  consensus_mode: "auto_agree"
  implementer_consent: null
  follow_up_questions_count: null
  agreed_at: null

- invocation_id: "council-2026-04-30T11:03:00Z-l0agg4"
  timestamp: "2026-04-30T11:03:00Z"
  source_skill: "layer0-spec-architect"
  question_to_answer: "Consumer (spec-architect / harness-verifier / Council CTL) が user-scope を読むクエリ API（直読み/共通ライブラリ/CLI/harness-verifier 統合）"
  council_type: "business"
  category: "implementation"
  category_fallback: false
  phase_reached: "phase_3"
  conflict_type: "unanimous"
  final_weights:
    経営者: 2
    開発者: 6
    哲学者: 2
  persona_summary:
    経営者: { stance: "案D-2: 共通ライブラリ ~/.claude/dh-data/lib/", confidence: 0.7, dimension: "ROI / 将来コスト" }
    開発者: { stance: "案D-2: 共通ライブラリ ~/.claude/dh-data/lib/", confidence: 0.9, dimension: "技術的実現性 / 責務集約" }
    哲学者: { stance: "案D-2: 共通ライブラリ ~/.claude/dh-data/lib/", confidence: 0.8, dimension: "意味 / 階層性" }
  judgment_confidence: 0.90
  weight_calculation:
    method: "weight_times_confidence"
    scores:
      - stance: "案D-2: 共通ライブラリ ~/.claude/dh-data/lib/"
        supporters: ["経営者", "開発者", "哲学者"]
        weight_sum: 10
        weighted_score: 8.4
        components:
          - { persona: "経営者", weight: 2, confidence: 0.7 }
          - { persona: "開発者", weight: 6, confidence: 0.9 }
          - { persona: "哲学者", weight: 2, confidence: 0.8 }
    third_way_excluded: []
    max_score_stance: "案D-2: 共通ライブラリ ~/.claude/dh-data/lib/"
    tie_break_applied: false
  weight_calculation_retry_count: 0
  recommended: "案D-2: 共通ライブラリ ~/.claude/dh-data/lib/。Python 標準ライブラリのみ依存、Consumer は import で集計責務を再利用。harness-verifier 統合 (D-4) は独立性原則違反のため却下"
  minority_opinion: "なし（全会一致）。共通理解: harness-verifier 統合は『検査機構が集計機構を兼ねる』論理階層混合の罠"
  human_escalated: false
  consensus_mode: "auto_agree"
  implementer_consent: null
  follow_up_questions_count: null
  agreed_at: null
