# Council Decision — メタスキル開発案件 Phase 1 採決記録

**採決日時**: 2026-05-11T03:14:18Z
**Council 機構**: crosscut-council Phase 1（PR1 walking skeleton, business 固定）
**起点 HANDOFF**: `5fd827fa-HANDOFFDHmetaskillindustryabsorption.md`
**上程文書**: `delivery/COUNCIL-AGENDA-metaskill-2026-05-11.md`
**起動主体**: layer0-spec-architect（PR #75 経由）
**実行環境**: CTL-2 / dev_mode=github_assisted / business Council 固定

---

## サマリ

| 議題 | invocation_id | recommended | judgment_confidence | consensus_mode | final_decision |
|---|---|---|---|---|---|
| **議題 1**: ECC 参照カタログ配置先 | `council-2026-05-11T03:14:18Z-vbxdnd` | **A** `.claude/refs/industry/ecc/` | 0.45 | `escalate_to_human` | null |
| **議題 2**: philosophy.md 追記 package | `council-2026-05-11T03:14:18Z-5v4xqq` | **B** P1+P2+P3 採用、用語/構造/配分は別議題分離 | 0.45 | `escalate_to_human`（H1 哲学変更） | null |

両議題とも `final_decision: null`（Council 哲学）、`human_escalated: true`。人間最終承認待ち。

---

## 議題 1: ECC 参照カタログ 5 ファイルの出力先ディレクトリ判定

### 入力

- **context**: ECC（v2.0.0-rc.1）48 agents / 182 skills / hooks.json / AgentShield / Instincts。Phase 0 で `delivery/refs-draft/ecc/` に draft 配置済 5 ファイル。将来 BMAD/Cline/Aider 等の追加可能性。
- **options**: A `.claude/refs/industry/ecc/` / B `history/refs/industry/ecc/` / C `intent/references/industry/ecc/` / D `assets/industry/ecc/` / E `.claude/skills/layer0-spec-architect/references/ecc-catalog/`
- **question_to_answer**: ECC 参照カタログ 5 ファイルを A〜E のどのディレクトリに配置すべきか
- **category**: `conception`
- **decision_category**: C3（構造変更）
- **final_weights**: 経営者 3 / 開発者 3 / 哲学者 5（base 3/4/3 + situational_modifier.conception 0/-1/+2）

### Phase 1 — Persona 独立並列出力

#### 経営者 (temp 0.3, weight 3)

```json
{
  "persona": "経営者",
  "stance": "A",
  "reason": "将来 BMAD/Cline/Aider 等の参照標本化が見込まれる以上、`.claude/refs/industry/`という業界横断カテゴリを早期に確立する方が、後から複数ファイルを移動する手戻りコストより安い。`.claude/`配下に集約することで AI が参照する際のパス探索コストも最小化でき、ROI が最も高い。B/D は意味的不一致で再整理リスク、C は新規 root 作成コスト、E はスケール時に確実に破綻する。",
  "confidence": 0.7,
  "dimension": "ROI / リスク",
  "premise": "3〜12ヶ月以内に 2〜3 件の追加参照標本（BMAD/Cline 等）が発生する前提",
  "concerns": [
    "`.claude/refs/`という新カテゴリがツールチェーン側の前提（skills/agents のみスキャン）と衝突する可能性",
    "業界横断カテゴリの命名規約（industry/ の粒度）が後から再定義され移動コストが発生するリスク",
    "参照標本の更新責任者・更新頻度が未定のまま配置すると陳腐化する"
  ]
}
```

#### 開発者 (temp 0.2, weight 3)

```json
{
  "persona": "開発者",
  "stance": "A",
  "reason": "参照標本は読み専用かつ複数 skill（L0/L1/crosscut）から横断参照されるため、特定 skill 配下（E）に置くと相対 path が深く・所有権が偏り保守性が劣化する。`.claude/refs/industry/ecc/` は skill 機構と同じ `.claude/` namespace に収まり、industry/ecc の階層化で BMAD/Cline 等の追加に対し O(1) 拡張可能。B は append-only 性質と用途不一致、C は新 root 創設で構成複雑化、D の assets はテンプレート慣例で読み専用参照標本と意味が衝突する。",
  "confidence": 0.85,
  "dimension": "保守性",
  "premise": "v5.11.0 時点で参照標本は読み専用、将来複数ベンダー追加の可能性あり、skill からは相対 path 参照",
  "concerns": [
    "`.claude/` 配下に skills 以外のディレクトリを置く先例がない場合、harness の探索ロジックや lint と衝突する可能性",
    "相対 path `../../refs/...` が skill 移動時に壊れる脆さ",
    "industry/ecc の二段階階層が将来 vendor 1 件運用では過剰になる懸念"
  ]
}
```

#### 哲学者 (temp 0.7, weight 5)

```json
{
  "persona": "哲学者",
  "stance": "第3の道: `intent/references/industry/ecc/` を採用しつつ、`intent/references/README.md` で『業界実装は参照標本であり吸収対象ではない』という存在論的境界を明文化する（C の精神化）",
  "reason": "配置先選択は技術判断ではなく『業界語彙と DH 語彙の関係性をどう存在論的に定義するか』の問い。A は業界を `.claude/` 内部化し DH 自身の一部と誤認させる危険、B は『過去』に幽閉し現在の参照価値を曖昧化、D は assets の機能的意味論に飲まれ哲学的距離が消える、E は横断概念の局所化で『同等以上を生成する方法論』を毀損する。C は『intent（意図）』の語が業界実装と DH 意図の非対称性を保存し、観測温存と存在論的距離を同時に成立させる。",
  "confidence": 0.65,
  "dimension": "前提への問い / 長期影響",
  "premise": "5 年スケールで ECC 以外の業界プリミティブ（次世代 framework, MCP 拡張等）が継続的に到来する前提。配置はカテゴリの存在論的位置付けを決める初手であり、後続の参照標本群の場所論を規定する",
  "concerns": [
    "『業界参照を取り込む』行為自体が DH の『同等以上を生成する方法論』への自己信頼を侵食する可能性",
    "intent/ 新規創出が D1-D5 の 5 次元論に未定義カテゴリを増やし、メタ構造を複雑化させる",
    "『参照のみ・吸収しない』境界が時間と共に風化し、いずれ ECC 由来パターンが skill に滲入する",
    "『業界』という二項対立的語彙自体が DH/業界の本質的差異を強化しすぎる懸念",
    "配置先の議論に時間を費やすこと自体が、本来問うべき『なぜ ECC を参照する必要があるのか』を覆い隠している"
  ]
}
```

### Phase 3 — Judgment Agent 出力

```json
{
  "recommended": "A `.claude/refs/industry/ecc/` を採用。経営者・開発者が独立に同一 stance に収束、weighted_score 4.65。ただし哲学者の第3の道（C 精神化）は weight 5/11=45% を占める少数意見として保持し、人間承認時に『業界実装は参照標本であり吸収対象ではない』旨の README 明文化を A の付帯条件として検討すべき",
  "reasoning": "category=conception の重み配分（経営者 3 / 開発者 3 / 哲学者 5）で options 内集計は A のみ。weighted_score(A) = 3×0.70 + 3×0.85 = 4.65。哲学者は options 外（第3の道）で third_way_excluded に退避。A 集計内 weight = 6（経営者 + 開発者）、excluded weight = 5（哲学者）で、excluded 比率 45.5% > 30% 閾値のため judgment_confidence は 0.5 以下に抑制（0.45）。A 採択は妥当だが、哲学者の存在論的問い（intent 語の非対称性保存、業界吸収の DH 自己信頼侵食）は人間判断で必ず参照されるべき重要少数意見",
  "minority_opinion": "哲学者: A は『業界を `.claude/` 内部化し DH 自身の一部と誤認させる危険』。第3の道として『intent/references/industry/ecc/ + README で存在論的境界を明文化』を提案。配置先の議論が『なぜ ECC を参照する必要があるのか』本来の問いを覆い隠しているという根本批判も保持",
  "weight_note": "council-weights.md §situational_modifier.conception (経営者 0 / 開発者 -1 / 哲学者 +2) を適用。最終配分 3/3/5。weight_calculation は weight_times_confidence 純粋関数。哲学者 stance は options 外につき third_way_excluded（暫定運用、PR2 で third_way 類型として正式化予定）",
  "weight_calculation": {
    "method": "weight_times_confidence",
    "scores": [
      {
        "stance": "A",
        "supporters": ["経営者", "開発者"],
        "weight_sum": 6,
        "weighted_score": 4.65,
        "components": [
          {"persona": "経営者", "weight": 3, "confidence": 0.70},
          {"persona": "開発者", "weight": 3, "confidence": 0.85}
        ]
      }
    ],
    "third_way_excluded": [
      {
        "persona": "哲学者",
        "stance": "第3の道: intent/references/industry/ecc/ + README 明文化（C の精神化）",
        "weight": 5,
        "confidence": 0.65,
        "reason": "options 外 stance のため weight 加算対象外（PR1 暫定運用）"
      }
    ],
    "max_score_stance": "A",
    "tie_break_applied": false
  },
  "judgment_confidence": 0.45,
  "consensus_mode": "escalate_to_human",
  "final_decision": null,
  "actual_outcome": {"status": null, "evaluated_at": null, "modifier_note": null},
  "invocation_id": "council-2026-05-11T03:14:18Z-vbxdnd",
  "project_metadata": {
    "ctl_at_invocation": "CTL-2",
    "council_type": "business",
    "category": "conception",
    "decision_category": "C3"
  }
}
```

### 議題 1 ステータス

- `status`: success
- `phase_reached`: phase_3
- `conflict_type`: simple_conflict（options 内 1 stance + third_way_excluded 1）
- `human_escalation_required`: **true**（judgment_confidence < 0.5）
- `weight_calculation_retry_count`: 0

---

## 議題 2: philosophy.md 追記 package の採否

### 入力

- **context**: philosophy.md 二層実装（harness-verifier + layer0-spec-architect/references）への P1（業界吸収方針）/ P2（業界 5 パターン位置付け）/ P3（独占 4 軸規範化）追記。CaaF/CDD 用語導入、第 8 条新設 vs 補論、二層配分の論点を含む。
- **options**: A 全採用 / B P1+P2+P3 採用＋他論点分離 / C P1 のみ / D 棄却・温存
- **question_to_answer**: philosophy.md 追記 package と関連論点を A〜D のどの粒度で採用すべきか
- **category**: `conception`
- **decision_category**: **H1（哲学変更）** — philosophy.md 改修は第 6 条 H1 直撃、即時 escalate_to_human
- **final_weights**: 経営者 3 / 開発者 3 / 哲学者 5

### Phase 1 — Persona 独立並列出力

#### 経営者 (temp 0.3, weight 3)

```json
{
  "persona": "経営者",
  "stance": "B",
  "reason": "P1+P2+P3 は DH の独自性を市場・人材獲得面で言語化する資産であり、採用の事業価値は明確。一方、CaaF/CDD 用語導入・第8条新設・二層配分は構造変更コストと後戻りリスクが高く、同一 minor で混載するとリリース遅延と検証範囲爆発の機会損失が出る。規範化（高 ROI 部分）を v5.12.x で先行収穫し、構造論は v5.13.0 以降に分離して段階的に償却するのが投資効率最良。A は範囲過大、C は機会損失、D は競合に対する独自性訴求の遅延。",
  "confidence": 0.70,
  "dimension": "ROI / リソース配分",
  "premise": "3〜6 ヶ月の minor リリース cadence を維持し、philosophy 改修によるドキュメント整合コストを最小化する前提",
  "concerns": [
    "P1+P2+P3 採用後に第 8 条新設要否で再議論コスト発生",
    "二層 philosophy.md の整合性管理が分離議題で後回しになるリスク",
    "CaaF/CDD 用語が業界で先行普及した場合の語彙負債",
    "別議題分離による意思決定疲労と棚上げ常態化"
  ]
}
```

#### 開発者 (temp 0.2, weight 3)

```json
{
  "persona": "開発者",
  "stance": "B",
  "reason": "P1+P2+P3 の追記自体は破壊なしで技術的に低リスク。ただし第 8 条新設はナンバリング変動を伴い、二層配分の整合性維持コストも別軸。CaaF/CDD は DH 内出現数 0 の新規用語で保守コスト純増、根拠薄弱。Shift Left 原則で「決定論的に分離可能な論点」は分離すべき。一括採用 A は変更範囲過大で diff レビュー困難、C は P2/P3 の意義を逃す、D は過剰先送り。B が最小スコープで段階的に検証可能。",
  "confidence": 0.85,
  "dimension": "保守性",
  "premise": "v5.9.0 で philosophy 改修は opt-in（human-review-needed 必須）、二層実装の整合性維持が前提。v5.12.x → v5.13.0 の段階展開が可能な時間軸。",
  "concerns": [
    "第 8 条新設時のナンバリング変動が既存 skill 参照に与える影響の事前検証が必要",
    "二層配分（簡潔版/詳説版）の同期維持が将来の保守負債化するリスク",
    "CaaF/CDD 用語を後続議題で採用する場合、DH 既存用語との衝突チェックが必須",
    "P1/P2/P3 を分割適用する際の PR 単位設計（独立 merge 可能性）",
    "別議題分離の運用が形骸化し v5.13.0 で再度 package 化される逆戻りリスク"
  ]
}
```

#### 哲学者 (temp 0.7, weight 5)

```json
{
  "persona": "哲学者",
  "stance": "B + 第 3 の道：P1/P2/P3 を「問いの形」で残し、断定を避ける",
  "reason": "哲学条文は「答え」ではなく「問い」を留める器であるべき。P1-P3 を断定形（〜である）で刻むと、5 年後の業界実装が DH の語彙を内包した時に憲法自体が桎梏となる。「DH は業界語彙で説明できるか」という問いを開いたまま条文化し、CaaF/CDD のような外来語は意図的に留保する B 案の構造を支持しつつ、文体は規範ではなく問いとして残すことを推奨する。独占性の主張は、独占を恐れる態度の裏返しでもある。",
  "confidence": 0.55,
  "dimension": "前提への問い / 長期影響",
  "premise": "5-10 年スパンで業界実装と DH 方法論の境界自体が溶ける可能性を前提とする",
  "concerns": [
    "『独占 4 軸』という語彙が排他性を内包し、第 6 条（人間最終承認）の謙抑性と緊張する",
    "第 8 条新設は『業界との差異化』を憲法に刻む行為であり、DH の自己定義が他者依存になる倒錯を招く",
    "CaaF/CDD の出現数 0 を理由に却下するのは経験主義的だが、未到来の語彙を philosophy で先取りする選択肢も哲学的には開かれている",
    "二層配分（簡潔/詳説）は読者への配慮として妥当だが、簡潔版が一人歩きして詳説が忘却される D5 監視外のリスクがある",
    "『同等以上のものを生成できる方法論』という P1 の自負は、検証不能な命題を憲法化することになる"
  ]
}
```

### Phase 3 — Judgment Agent 出力

```json
{
  "recommended": "B P1+P2+P3 のみ採用、CaaF/CDD 用語/第 8 条新設 vs 補論/二層配分は別議題（v5.13.0 以降）に分離。経営者・開発者が独立に同一 stance に収束、weighted_score 4.65。哲学者は『B + 文体を問いの形に』という第 3 の道で接近するが options 外につき third_way_excluded。ただし decision_category=H1（哲学変更）に該当するため、Council 推奨 B は人間最終承認を要する",
  "reasoning": "category=conception の重み配分（経営者 3 / 開発者 3 / 哲学者 5）で options 内集計は B のみ。weighted_score(B) = 3×0.70 + 3×0.85 = 4.65。哲学者の『B + 第 3 の道（問いの形）』は options 外で third_way_excluded（weight 5、confidence 0.55）。excluded 比率 45.5% > 30% 閾値で judgment_confidence は 0.45 に抑制。さらに decision_category=H1 哲学変更により compute_consensus_mode は無条件 escalate_to_human を返す。B 採択は経営/技術の両面で妥当だが、哲学者の『P1-P3 を断定形で刻むと 5 年後に憲法自体が桎梏になる』『独占性の主張は独占を恐れる態度の裏返し』という根本批判は人間判断で必ず参照されるべき",
  "minority_opinion": "哲学者: P1/P2/P3 を断定形（〜である）でなく問いの形で残すべき。『独占 4 軸』語彙の排他性が第 6 条（人間最終承認）の謙抑性と緊張する。第 8 条新設は DH 自己定義が他者依存（業界差異化）になる倒錯を招く。CaaF/CDD 出現数 0 を理由に却下するのは経験主義的（未到来の語彙を先取りする選択肢も哲学的には開かれている）",
  "weight_note": "council-weights.md §situational_modifier.conception (経営者 0 / 開発者 -1 / 哲学者 +2) を適用。最終配分 3/3/5。weight_calculation は weight_times_confidence 純粋関数。哲学者 stance は options 外（B + 修飾語）につき third_way_excluded。decision_category=H1 哲学変更により consensus_mode は confidence によらず escalate_to_human",
  "weight_calculation": {
    "method": "weight_times_confidence",
    "scores": [
      {
        "stance": "B",
        "supporters": ["経営者", "開発者"],
        "weight_sum": 6,
        "weighted_score": 4.65,
        "components": [
          {"persona": "経営者", "weight": 3, "confidence": 0.70},
          {"persona": "開発者", "weight": 3, "confidence": 0.85}
        ]
      }
    ],
    "third_way_excluded": [
      {
        "persona": "哲学者",
        "stance": "B + 第 3 の道：P1/P2/P3 を「問いの形」で残し断定を避ける",
        "weight": 5,
        "confidence": 0.55,
        "reason": "options 外 stance（B + 修飾語の自由記述）のため weight 加算対象外（PR1 暫定運用）"
      }
    ],
    "max_score_stance": "B",
    "tie_break_applied": false
  },
  "judgment_confidence": 0.45,
  "consensus_mode": "escalate_to_human",
  "final_decision": null,
  "actual_outcome": {"status": null, "evaluated_at": null, "modifier_note": null},
  "invocation_id": "council-2026-05-11T03:14:18Z-5v4xqq",
  "project_metadata": {
    "ctl_at_invocation": "CTL-2",
    "council_type": "business",
    "category": "conception",
    "decision_category": "H1"
  }
}
```

### 議題 2 ステータス

- `status`: success
- `phase_reached`: phase_3
- `conflict_type`: simple_conflict（options 内 1 stance + third_way_excluded 1）
- `human_escalation_required`: **true**（judgment_confidence < 0.5 + decision_category=H1）
- `weight_calculation_retry_count`: 0

---

## 人間判断のための論点整理（合意プロセス Step 1: 理解）

### 議題 1 で人間が判断すべき軸

1. **A 採択（Council 推奨）**: 想定通り `.claude/refs/industry/ecc/` に正式配置し、5 ファイルを `delivery/refs-draft/ecc/` から移動
2. **A 採択 + 哲学者の付帯条件吸収**: A 採択した上で `.claude/refs/industry/README.md` に「業界実装は参照標本であり吸収対象ではない」存在論的境界を明文化（哲学者の第 3 の道精神を A に統合）
3. **C 採択**: 哲学者の第 3 の道（C ベース + README 明文化）を全面採用、`intent/` ディレクトリを新規創出
4. **保留**: 配置先議論より先に「なぜ ECC を参照する必要があるのか」本来の問いに立ち戻る（哲学者の根本批判）

### 議題 2 で人間が判断すべき軸

1. **B 採択（Council 推奨）**: P1+P2+P3 を v5.12.x で先行採用、CaaF/CDD 用語/第 8 条新設 vs 補論/二層配分は v5.13.0 以降の別議題に分離
2. **B 採択 + 哲学者の文体修正吸収**: P1+P2+P3 を「断定形」ではなく「問いの形」で起草し直す（独占性主張の謙抑化）
3. **A 採択（範囲過大の覚悟）**: L0 推奨 package 全体を一括採用
4. **D 採択（先送り）**: philosophy 改修自体を v6.0.0 メジャーに先送り

### 共通の構造的論点

- 両議題で哲学者は「業界実装吸収という行為自体への根本懐疑」を提示している（議題 1: 「`.claude/` 内部化は DH 自己信頼の侵食」/ 議題 2: 「独占性主張は独占を恐れる態度の裏返し」）。これは Phase 1 独立性で 2 議題に独立に出現した同型批判であり、`philosophy.md` 改修議論の前提として参照されるべき構造的論点
- 経営者・開発者は両議題で安定して Council 推奨に集約（confidence 0.70-0.85）。両者の独立収束は決定論的判断の側面が強いことを示唆

---

## 後続フロー

1. 本ファイルを PR #75 にコミット
2. `history/COUNCIL-LOG.md` に 2 invocation エントリを追加（append-only）
3. PR コメントで人間最終承認を要請（`human-review-needed` ラベル相当）
4. 人間承認後:
   - 議題 1 採決結果に従い `delivery/refs-draft/ecc/` を確定パスへ移動
   - 議題 2 採決結果に従い `philosophy.md` 二層への追記（v5.12.0 minor 候補）を実施
   - COUNCIL-LOG の `implementer_consent` / `agreed_at` を後追記

## ファイル配置

- 本ファイル: `delivery/COUNCIL-DECISION-metaskill-2026-05-11T03:14:18Z.md`
- 起点議題: `delivery/COUNCIL-AGENDA-metaskill-2026-05-11.md`
- COUNCIL-LOG エントリ追記先: `history/COUNCIL-LOG.md`
