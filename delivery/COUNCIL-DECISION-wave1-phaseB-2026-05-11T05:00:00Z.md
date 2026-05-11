# Council Decision — Wave 1 Phase B 諮問 3 件

**起動日時**: 2026-05-11T05:00:00Z
**起点 PR**: [PR #76](https://github.com/samejima-ai/dialog-harness/pull/76)（Wave 1 SPEC 起点）
**source_skill**: layer0-spec-architect（Wave 1 SPEC 詳細起草フェーズ）
**council_type**: business（経営者 / 開発者 / 哲学者）
**Phase 到達**: phase_3（Phase 0→1→3、Phase 2 はスキップ）
**判定根拠**: `delivery/CHEW-PROTOCOL-SPEC-wave1-starter.md` §3 Phase B 諮問予定

---

## 諮問 1: hooks.json event types サブセット選別

### invocation_id: `council-2026-05-11T05:00:00Z-w1qb01`

### question_to_answer
Wave 1 で採用する Claude Code hooks.json の event types はどのサブセットか?

### options
- **A**: 5 event 採用（PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd、PreCompact 除外）
- **B**: 6 event 全採用（PreCompact 含む）
- **C**: 3 event 最小採用（PreToolUse / Stop / SessionStart）

### category
implementation

### final_weights
- 経営者: 2
- 開発者: 6
- 哲学者: 2

### persona_summary

| Persona | stance | confidence | dimension | reason 要約 |
|---|---|---|---|---|
| 経営者 | A | 0.7 | ROI / 運用コスト | 5 event で観測の中核は確保、PreCompact は v5.13.0 候補で温存する方が運用コスト最小 |
| 開発者 | A | 0.85 | 保守性 / 実装容易性 | PreCompact は DH の `/compact` 連携が未確立で実装コストが余分、5 event は ECC 既存実装を直接参照可能 |
| 哲学者 | A | 0.75 | 観測温存 / 5 次元 | PreCompact は context 圧縮への自動介入で「観測の連続性」を毀損するリスクあり、Wave 1 では除外して観察期間を設ける |

### conflict_type
**unanimous**（A で全会一致）

### weight_calculation
- method: `weight_times_confidence`
- A: 経営者 (2 × 0.7) + 開発者 (6 × 0.85) + 哲学者 (2 × 0.75) = 1.4 + 5.1 + 1.5 = **8.0**
- 最高スコア stance: A
- tie_break_applied: false

### judgment

- **recommended**: A（5 event 採用、PreCompact 除外）
- **judgment_confidence**: 0.78
- **reasoning**: 3 ペルソナが ROI / 実装容易性 / 観測温存の異なる射程で同一結論に到達。PreCompact は DH 既存の `/compact` 機構との連携が未確立で、観察期間を設けることで第 6 条「人間最終承認」原則と整合する。Wave 3（v5.13.0 候補）で `/compact` 連携 SPEC と一緒に再諮問。
- **minority_opinion**: なし（全会一致）
- **final_decision**: null（実装者の合意プロセスを経て確定）
- **human_escalated**: false

### implementer_consent
**agreed_recommended**（本セッション内で確定、2026-05-11T05:02:00Z）

---

## 諮問 2: 既存 17 skill description 修正タイミング

### invocation_id: `council-2026-05-11T05:00:00Z-w1qb02`

### question_to_answer
候補 1（PROACTIVELY トリガー語彙）の規約確定後、既存 17 skill の description 監査・修正をいつ実施するか?

### options
- **A**: Wave 2 で一括修正（v5.12.x 第 2 PR で 17 skill を一気に更新）
- **B**: 各 skill の次回更新時に逐次修正（規約確定 → 機能改修ついでに描画）
- **C**: Wave 1 内で実施（本 PR スコープに 17 skill 修正を含める）

### category
operation

### final_weights
- 経営者: 4
- 開発者: 4
- 哲学者: 3

### persona_summary

| Persona | stance | confidence | dimension | reason 要約 |
|---|---|---|---|---|
| 経営者 | B | 0.75 | ROI / 機会損失 | 逐次修正で工数分散、Wave 1 規格確定後に各 skill 更新時に組み込めば追加工数 0、機会損失も最小 |
| 開発者 | B | 0.85 | 保守性 / 並列性 | Wave 1 で規約を確定 → 17 skill 一斉修正は merge conflict と並列レビュー負荷大、逐次修正で各 skill 動作確認を並行可能 |
| 哲学者 | C | 0.55 | 第 7 条 AI 組織論 | 自動起動精度を即時改善するなら Wave 1 内修正、ただし 17 skill の品質保証は逐次が安全との認識あり、B でも可 |

### conflict_type
**simple_conflict**（B 多数 / C 少数）

### weight_calculation
- method: `weight_times_confidence`
- B: 経営者 (4 × 0.75) + 開発者 (4 × 0.85) = 3.0 + 3.4 = **6.4**
- C: 哲学者 (3 × 0.55) = **1.65**
- 最高スコア stance: B
- third_way_excluded: なし
- tie_break_applied: false

### judgment

- **recommended**: B（各 skill 次回更新時に逐次修正）
- **judgment_confidence**: 0.70
- **reasoning**: 経営者・開発者の B 推奨が weight × confidence で支配的（6.4 vs 1.65）。哲学者の C 推奨は「即時改善」の理念的価値を保持するが、17 skill 一斉修正の並列レビュー負荷と動作確認の困難性から運用上 B が現実的。Wave 1 では監査チェックリストのみ作成、修正は各 skill の次回更新時に組み込む。
- **minority_opinion**: 「哲学者: 自動起動精度を即時改善することは第 7 条 AI 組織論の規範性と整合する。逐次修正の選択は『品質保証 vs 規範速度』のトレードオフで、品質保証側に寄った判断。Wave 2 末で監査進捗（17 skill 中何件修正済か）を観測し、進捗が遅い場合は Wave 3 で一括修正を再諮問」
- **final_decision**: null
- **human_escalated**: false

### implementer_consent
**agreed_recommended**（本セッション内で確定、2026-05-11T05:02:00Z）

---

## 諮問 3: templates/rules/ 言語先取りの是非

### invocation_id: `council-2026-05-11T05:00:00Z-w1qb03`

### question_to_answer
候補 6（rules common + 14 言語別）の Wave 1 採用において、言語別 rules を先取りで含めるか?

### options
- **A**: 言語先取りなし（DH 流遅延戦略、L0 対話で必要言語のみ生成）
- **B**: よく使う 3 言語のみ先取り（python / typescript / go の `templates/rules/<lang>/` を空 scaffold で先設置）
- **C**: ECC 14 言語全部先取り

### category
conception

### final_weights
- 経営者: 3
- 開発者: 3
- 哲学者: 5

### persona_summary

| Persona | stance | confidence | dimension | reason 要約 |
|---|---|---|---|---|
| 経営者 | B | 0.65 | 市場想定 / 初期コスト | python / typescript は実利用率高、3 言語先取りで初期セットアップコスト削減、ROI 観点で先取りメリットあり |
| 開発者 | A | 0.80 | 実装範囲管理 / 可逆性 | 遅延戦略は L0 対話で必要言語のみ生成、初期実装範囲を最小化、後から追加可能で reversibility 高 |
| 哲学者 | A | 0.70 | フラクタル原則 / 観測温存 | 言語別 rules を先取りで含めると DH の「対話で確定」原則に反する、L0 対話の選択肢として残すべき。先取りは「業界実装プリミティブをそのまま吸収」に該当 |

### conflict_type
**simple_conflict**（A 多数 / B 少数 / C 不採）

### weight_calculation
- method: `weight_times_confidence`
- A: 開発者 (3 × 0.80) + 哲学者 (5 × 0.70) = 2.4 + 3.5 = **5.9**
- B: 経営者 (3 × 0.65) = **1.95**
- C: 該当なし
- 最高スコア stance: A
- third_way_excluded: なし
- tie_break_applied: false

### judgment

- **recommended**: A（言語先取りなし、DH 流遅延戦略）
- **judgment_confidence**: 0.72
- **reasoning**: 開発者と哲学者の A 推奨が weight × confidence で支配的（5.9 vs 1.95）。哲学者の「業界実装プリミティブをそのまま吸収しない」原則は議題 0（B + 哲学者止揚）の核心とも整合。経営者の「実利用率の高い 3 言語先取り」は ROI 妥当性を持つが、L0 対話で必要言語を確定する DH 流プロトコルの方が **第 1 条フラクタル原則** との整合性が高い。
- **minority_opinion**: 「経営者: python / typescript / go は ECC 14 言語の中でも実利用率上位 3 で、L0 対話確定の手間を削減できる。Wave 2 末で実プロジェクト適用例を観測し、L0 対話で 3 言語が頻出する場合は『推奨言語プリセット』として再諮問」
- **final_decision**: null
- **human_escalated**: false

### implementer_consent
**agreed_recommended**（本セッション内で確定、2026-05-11T05:02:00Z）

---

## まとめ（Wave 1 SPEC への反映方針）

| 諮問 | recommended | 実装反映 |
|---|---|---|
| 1: hooks event types | A: 5 event 採用 | `.claude/hooks.json`（Claude Code 公式 schema 準拠位置）に PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd の 5 event のみ定義、PreCompact は v5.13.0 候補として温存メモ。当初 SPEC starter で harness-verifier 配下配置を想定したが、harness-verifier 独立性原則と整合させるため Claude Code 標準位置に配置決定 |
| 2: skill description 修正時期 | B: 逐次修正 | Wave 1 では `dev-env-spec.md` に規約追加 + 17 skill 監査チェックリスト作成のみ、修正は各 skill 次回更新時 |
| 3: rules 言語先取り | A: 言語先取りなし | `templates/rules/common/` + `templates/rules/README.md` のみ作成、言語別ディレクトリは L0 対話で生成 |

3 件すべて `judgment_confidence ≥ 0.7` で全件 `agreed_recommended` 成立。`human_escalated: false`、合意プロセスで方針確定。

minority opinion 2 件は Wave 2/3 末の振り返り儀式で観測・再評価項目として温存:
- 諮問 2 minority: 17 skill 監査進捗 → Wave 2 末で観測、遅い場合 Wave 3 で一括修正を再諮問
- 諮問 3 minority: L0 対話での 3 言語頻出度 → Wave 2 末で観測、頻出する場合「推奨言語プリセット」を再諮問
