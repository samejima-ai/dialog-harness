# Council 採決記録 — Wave 2 Phase B

**起票**: 2026-05-11T07:00:00Z
**起票元**: PR #77 後続、咀嚼プロトコル Wave 2 Phase B（SPEC starter §3 諮問 agenda）
**branch**: `claude/chew-protocol-spec-wave2-phaseBC`
**Council 形式**: business council（経営者 / 開発者 / 哲学者）3 ペルソナ、諮問 2 は + 哲学者重み増強
**規格根拠**: `crosscut-council/SKILL.md` + `philosophy.md` 第 6 条「人間最終承認」+ 第 7 条「AI 組織論」+ 議題 0 採決 `council-2026-05-11T03:49:01Z-4go7g1`

---

## 諮問 1: continuous-learning v2.1 の自動度境界

- **invocation_id**: `council-2026-05-11T07:00:00Z-w2qb01`
- **judgment_type**: tradeoff（自動化効率 vs 哲学整合性）
- **context**: 候補 5（continuous-learning v2.1）で pattern 検出 → instinct promote の自動度を確定する。philosophy 第 6 条「人間最終承認」と第 7 条 P4 介入権、および第 8 条候補（自律性 + 哲学ガードレール）との同時整合が必須。

### options

| ID | stance |
|---|---|
| A | CTL に応じた段階的自動度（CTL 0 = inactive / CTL 1 = 候補出力のみ / CTL 2+ = 自動 promote だが Council 必須） |
| B | 全 CTL で候補出力のみ、適用は人間最終承認（最も保守的） |
| C | 自動 promote を 1 度も実装せず、Wave 3 でも候補出力のみで運用継続 |

### persona 並列意見

- **経営者**: 効率重視。CTL 連動の段階的自動化で生産性向上、開発体験を ECC に近づける → **A 推奨**（confidence 0.70）
- **開発者**: 誤 promote の影響大。観測データ不足の段階で自動経路を開くのはリスク高、まず候補出力で運用実証 → **B 推奨**（confidence 0.80）
- **哲学者**: 第 6 条「人間最終承認」原則の厳格適用。自動 promote は哲学ガードレールを侵食する。第 8 条候補「自律性 + 哲学ガードレール」の語彙化前に自動経路を開くのは哲学侵食の先行 → **B 推奨**（confidence 0.85）

### 採点

| stance | supporters | weight_sum | weighted_score |
|---|---|---|---|
| A | 経営者 | 3 | 2.10 |
| B | 開発者 + 哲学者 | 8 (3 + 5) | **6.65** ← max |
| C | （該当者なし） | 0 | 0 |

### 判定

- **recommended**: **B**（候補出力のみ、適用は人間最終承認）
- **judgment_confidence**: 0.82
- **minority_opinion (A)**: 経営者意見 — Wave 2 末振り返り儀式で「候補出力経路の運用実績 / 誤 promote 発生回数 / 人間レビュー負荷」を観測、健全運用が確認できれば Wave 3 で CTL 連動自動度を再諮問
- **third_way_excluded**: なし
- **human_escalated**: false
- **consensus_mode**: auto_agree
- **implementer_consent**: agreed_recommended

### cascade_to

`delivery/CHEW-PROTOCOL-SPEC-wave2-starter.md §2.2.4 へ反映、Phase C で `crosscut-continuous-learning` skill を「候補出力のみ / 自動 promote なし / CTL 0 inactive」で実装。Wave 2 末振り返り儀式の観測項目に「continuous-learning 候補出力経路の運用実績」を追加

---

## 諮問 2: AgentShield 102 ルール / 5 カテゴリの DH 採用範囲

- **invocation_id**: `council-2026-05-11T07:00:00Z-w2qb02`
- **judgment_type**: tradeoff（安全性 vs 自律性 + 独立性原則）
- **persona**: business council + **哲学者重み増強**（candidate 4 仕様、緊張度「高」のため）
- **context**: 候補 4 観察結果（PR #75 ECC-SURVEY + `delivery/refs-draft/ecc/agentshield-spec.md`）により、AgentShield は **102 静的解析ルール × 5 カテゴリ** で、`ecc-agentshield` npm package として独立配布される。DH は自前実装ではなく **参照導入** が現実的。`--fix` 自動修復経路と `--opus --stream` 外部 LLM 経路は DH 哲学（独立性原則・観察温存）と緊張する。

### options

| ID | stance |
|---|---|
| A | 全 5 カテゴリ採用 + `--fix` 自動修復推奨、利用者プロジェクトに `ecc-agentshield` npm install を強推奨 |
| B | 5 カテゴリは warn のみ参照導入、`--fix` 自動修復は採用せず、`--opus --stream` 経路も採用せず |
| C | 採用せず、Wave 3 で 102 ルール詳細観察後に再判断 |

### persona 並列意見

- **経営者**: ECC 連携で利用者プロジェクトの脆弱性検査を強化、エコシステム接続点として価値高 → **A 推奨**（confidence 0.65）
- **開発者**: `--fix` 自動修復は破壊的変更可能、CI 統合の運用負荷大。warn のみ参照導入が現実的 → **B 推奨**（confidence 0.85）
- **哲学者**: `--fix` は第 6 条「人間最終承認」を侵食、`--opus --stream` は外部 LLM 呼出で独立性原則・観察温存と緊張。warn のみ参照導入は philosophy 整合範囲 → **B 推奨**（confidence 0.90、重み 5 → **6** に増強）

### 採点

| stance | supporters | weight_sum | weighted_score |
|---|---|---|---|
| A | 経営者 | 3 | 1.95 |
| B | 開発者 + 哲学者（重み 6） | 9 (3 + 6) | **8.10** ← max |
| C | （該当者なし） | 0 | 0 |

### 判定

- **recommended**: **B**（5 カテゴリ warn のみ参照導入、`--fix` / `--opus --stream` 経路は採用せず）
- **judgment_confidence**: 0.85
- **minority_opinion (A)**: 経営者意見 — 利用者プロジェクト側で `ecc-agentshield` を **手動 install** することは推奨可。DH 側からの自動連携・強制起動は採用しない
- **third_way_excluded**: 自前実装（c.f. ECC-SURVEY §6「DH 方法論での生成手順」）は Wave 3 で v6.0.0 候補として別議題化
- **human_escalated**: false
- **consensus_mode**: auto_agree
- **implementer_consent**: agreed_recommended

### cascade_to

`dev-env-spec.md` に「AgentShield 参照導入規約」セクション追加、`templates/rules/common/agentshield-reference.md` で 5 カテゴリと採用方針を明示。DH 側に自前ルール実装は行わない（Wave 3 で v6.0.0 候補として再評価）

---

## 諮問 3: origin/version frontmatter 既存 17 skill 適用タイミング

- **invocation_id**: `council-2026-05-11T07:00:00Z-w2qb03`
- **judgment_type**: simple_conflict（Wave 1 諮問 w1qb02 と同型）
- **context**: 候補 2（origin/version frontmatter 規格）を Wave 1 で `crosscut-hook-observer/SKILL.md` に先取り適用済。既存 17 skill への展開タイミングを確定する。

### options

| ID | stance |
|---|---|
| A | Wave 2 内で 17 skill 一括適用（PR 規模大、frontmatter 既存形式との衝突 risk あり） |
| B | 各 skill 次回更新時に逐次適用（Wave 1 諮問 w1qb02 と同型、運用負荷分散） |
| C | Wave 2 で 5 skill のみ先行（layer0 / layer1 / layer2 兄弟）、残り 12 skill は Wave 3 申し送り |

### persona 並列意見

- **経営者**: 一括の方が後の運用効率良い、frontmatter 完全性を早期に確立 → **A 推奨**（confidence 0.70）
- **開発者**: 一括は変更範囲大、PR review 負担増、frontmatter 既存形式との衝突 risk → **B 推奨**（confidence 0.80）
- **哲学者**: Wave 1 諮問 w1qb02 の判決を踏襲、逐次は哲学的に並列性高、Wave 2 末で進捗評価後 Wave 3 で再判断 → **B 推奨**（confidence 0.78）

### 採点

| stance | supporters | weight_sum | weighted_score |
|---|---|---|---|
| A | 経営者 | 3 | 2.10 |
| B | 開発者 + 哲学者 | 8 (3 + 5) | **6.30** ← max |
| C | （該当者なし） | 0 | 0 |

### 判定

- **recommended**: **B**（各 skill 次回更新時に逐次適用、Wave 1 諮問 w1qb02 と同パターン）
- **judgment_confidence**: 0.76
- **minority_opinion (A)**: 経営者意見 — Wave 2 末振り返り儀式で「逐次適用の進捗 ≤ 50%」が観測された場合、Wave 3 で一括適用を再諮問
- **third_way_excluded**: なし
- **human_escalated**: false
- **consensus_mode**: auto_agree
- **implementer_consent**: agreed_recommended

### cascade_to

`dev-env-spec.md` に「origin/version frontmatter 規格」セクション正式化、Wave 1 「skill description 監査チェックリスト」と同型の「frontmatter 監査チェックリスト」を作成。本 PR では新設 skill（crosscut-continuous-learning）に先取り適用、既存 17 skill は次回更新時に逐次

---

## 諮問予備 4: HV 拡張の harness-verify.yml 経路（省略判定）

- **invocation_id**: `council-2026-05-11T07:00:00Z-w2qb04`
- **判定**: **諮問省略**
- **省略根拠**: chewing protocol §3 諮問判定で `confidence ≥ 0.7` 基準を満たす
  - HV 拡張は読取専用 + 独立出力 → philosophy 第 6 条「人間最終承認」と整合
  - harness-verify.yml workflow の `--strict` PR 経路は不変、月次経路で観測解析を追加するだけ → HUMAN-PROTOCOL.md §1 と整合
  - 緊張度 **軽微**、tradeoff 不在 → 諮問必要性なし
- **implementer_consent**: `auto_proceed`（諮問省略時のデフォルト）
- **cascade_to**: SPEC starter §2.1.4 通り Phase C で実装

---

## Phase B 完遂要約

| 諮問 | recommended | confidence | 実装反映 |
|---|---|---|---|
| 1: continuous-learning 自動度 | B: 候補出力のみ、人間最終承認 | 0.82 | Phase C で `crosscut-continuous-learning` skill を「候補出力 / CTL 0 inactive / 自動 promote なし」で実装 |
| 2: AgentShield 採用範囲 | B: 5 カテゴリ warn のみ参照導入 | 0.85 | Phase C で `dev-env-spec.md` AgentShield 参照導入規約 + `templates/rules/common/agentshield-reference.md` 配置、自前実装なし |
| 3: frontmatter 適用タイミング | B: 逐次適用 | 0.76 | Phase C で `dev-env-spec.md` frontmatter 規格正式化 + 監査チェックリスト作成、新設 skill に先取り適用 |
| 予備 4: HV 拡張 yml 経路 | 諮問省略 | confidence ≥ 0.7 | Phase C で SPEC 通り実装 |

3 件すべて `agreed_recommended` で合意成立、`human_escalated: false`。Wave 2 全諮問は B 系（保守的・人間最終承認尊重）に収束、Wave 1 で確立した「DH 流遅延戦略」が Wave 2 にも継承された。

minority opinion 3 件は Wave 2 末 / Wave 3 末の振り返り儀式で再評価項目として温存:
- 諮問 1 minority A: continuous-learning CTL 連動自動度 → Wave 2 末で運用実績観測
- 諮問 2 minority A: ecc-agentshield 利用者側手動 install 推奨は採用可
- 諮問 3 minority A: frontmatter 逐次進捗 ≤ 50% なら Wave 3 で一括再諮問

---

## 哲学的注記

Wave 2 Phase B 諮問結果は Wave 1 Phase B と同様 **B 系（保守的）に収束** したが、これは偶然ではない:

- Wave 1 Phase B: hooks event subset で「5 event 採用、PreCompact 棄却」「skill description 逐次修正」「言語先取りなし」とすべて T3（サブセット選別）に収束
- Wave 2 Phase B: continuous-learning「候補出力のみ」AgentShield「warn のみ参照導入」frontmatter「逐次適用」とすべて T3 + ガードレール語彙化に収束

これは咀嚼プロトコル §3「翻訳」の T3 と、PHILOSOPHY-NOTE-autonomy-with-guardrails の「適用条件のガードレール化」が、DH 哲学（philosophy 6 条 + 第 7 条 + 第 8 条候補）の自然な帰結として動作している証拠。Wave 3 で第 8 条候補が本格諮問される際の経験的根拠が Wave 1 + Wave 2 の 2 サンプルで蓄積された。

特に **諮問 2** では業界実装（AgentShield の `--fix` / `--opus --stream`）が「便利だが哲学侵食」の典型パターンとして観察され、咀嚼プロトコルが「素材構造を保持しつつ適用条件をガードレール化する」翻訳機構として動作することが実証された。

Wave 3 で議題 2「Step 2 第 2 段」を再上程する際、本 Phase B の B 系収束パターンは「DH 哲学 + 咀嚼プロトコルが業界実装を吸収する境界線」として参照素材になる。
