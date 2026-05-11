# Council 採決記録 — Wave 3 Phase B

**起票**: 2026-05-11T09:00:00Z
**起票元**: PR #80 (Phase A) 後続、咀嚼プロトコル Wave 3 Phase B（SPEC starter §3 諮問 agenda）
**branch**: `claude/chew-protocol-spec-wave3-phaseBC`
**Council 形式**: business council（経営者 / 開発者 / 哲学者）3 ペルソナ、諮問 1 は `category: conception` 適用
**規格根拠**: `crosscut-council/SKILL.md` + `crosscut-council/council-weights.md` + `philosophy.md` 第 6 条「人間最終承認」+ 第 7 条「AI 組織論」+ 第 8 条候補（本諮問で本格採決）

---

## 諮問 1: philosophy 第 8 条本格諮問

- **invocation_id**: `council-2026-05-11T09:00:00Z-w3qb01`
- **judgment_type**: tradeoff（philosophy 改訂 vs 候補温存）
- **category**: `conception` — `crosscut-council/council-weights.md` §situational_modifier.conception 適用
- **final_weights**: base 3/4/3 + conception 補正 0/-1/+2 = **経営者 3 / 開発者 3 / 哲学者 5**
- **context**: Wave 1 PHILOSOPHY-NOTE-autonomy-with-guardrails-2026-05-11 で起草された第 8 条候補「自律性原則 + 哲学ガードレール」を、Wave 1 + Wave 2 の B 系収束 2 サンプルを経験的根拠として `philosophy.md` に正式追加するかを諮問。

### options

| ID | stance |
|---|---|
| A | 第 8 条として明文化、philosophy.md に追加（3 段階: 観測 → 候補化 → 人間最終承認） |
| B | 第 8 条候補のまま PHILOSOPHY-NOTE で温存、Wave 4 / Wave 5 で再諮問 |
| C | 第 8 条として明文化、ただし「観測 → 候補化 → 採決 → 適用」の 4 段階に拡張（Council 必須を明示） |

### persona 並列意見

- **経営者** (weight 3): 規範の明文化は意思決定速度を上げ、後続 Wave の判断負荷を減らす。3 段階で十分、4 段階は Council 起動コストが大きい → **A 推奨**（confidence 0.70）
- **開発者** (weight 3): 第 8 条は B 系収束パターンの言語化で、判断基準として実装に役立つ。3 段階の方が運用負荷が低い。「人間最終承認」の解釈分裂を防ぐ意味で C も検討余地あり、ただし 3 段階で先行運用 Wave 4 末で 4 段階拡張を再評価する案を優先 → **A 推奨**（confidence 0.75）
- **哲学者** (weight 5): 第 8 条候補は Wave 1 + Wave 2 で 2 サンプル蓄積、philosophy.md に正式条文として組み込む準備が整っている。ただし「人間最終承認」が曖昧で、Council を経由しない単独人間判断を許容するかが論点。4 段階拡張案 C は philosophy 第 7 条「AI 組織論」P3 責務分離と整合する。第 7 条との接続性を考えると C 推奨 → **C 推奨**（confidence 0.85）

### 採点

| stance | supporters | weight_sum | weighted_score |
|---|---|---|---|
| A | 経営者 + 開発者 | 6 | (3×0.70) + (3×0.75) = 2.10 + 2.25 = **4.35** |
| B | （該当者なし） | 0 | 0 |
| C | 哲学者 | 5 | 5 × 0.85 = **4.25** |

A が max (4.35)、C が次点 (4.25)、差 0.10 で接近。

### 判定

- **recommended**: **A**（第 8 条として明文化、3 段階「観測 → 候補化 → 人間最終承認」）
- **judgment_confidence**: 0.55（max スコア 4.35 と次点 4.25 の差 0.10 で接近、`judgment-agent.md` §confidence 算出規則「差 < 0.5 → 0.4-0.6」適用）
- **minority_opinion (C)**: 哲学者意見 — 4 段階拡張（Council 必須）は philosophy 第 7 条 P3 責務分離と整合する。Wave 4 末で 3 段階運用の実績観測後、「Council 経由率 ≤ 20%」が確認されれば Wave 5 で 4 段階拡張を再諮問
- **third_way_excluded**: なし
- **human_escalated**: false（confidence 0.55 は接近採決だが、`judgment-agent.md` §人間エスカレーション条件「confidence < 0.4」未満、escalate_to_human は適用外）
- **consensus_mode**: auto_agree
- **implementer_consent**: agreed_recommended（実装容易性を踏まえ 3 段階先行に合意）

### cascade_to

`philosophy.md` 第 8 条として明文化、3 段階「観測 → 候補化 → 人間最終承認」+ CTL 連動の active/inactive 規約を明記。Phase C で実装。`history/PHILOSOPHY-CHANGELOG.md` に第 8 条追加を記録（w3qb03 採決に従い手動運用）。Wave 4 末振り返り儀式で 4 段階拡張再評価の観測項目を設定。

### 哲学的注記

本諮問は Wave 1 / Wave 2 で 2 サンプル連続観測された B 系収束パターンを **正式条文化** する歴史的議題。判定 A (3 段階) は哲学者の C 案 (4 段階) と接近採決で、minority opinion 温存により Wave 5 で「Council 経由率」の実観測データを根拠に再諮問可能な経路を確保する。これにより「philosophy 改訂は慎重に + 拡張余地を温存」という DH 設計原則と整合する。

---

## 諮問 2: 議題 2 残候補（hooks 残り 4 event / continuous-learning CTL 連動）

- **invocation_id**: `council-2026-05-11T09:00:00Z-w3qb02`
- **judgment_type**: tradeoff（観測実績 2 サンプル後の判断）
- **category**: `judgment`（default 判断、conception ほど構想性は強くない）— council-weights.md §situational_modifier.judgment 適用
- **final_weights**: base 3/4/3 + judgment 補正 +1/0/0 = **経営者 4 / 開発者 4 / 哲学者 3**
- **context**: 議題 0 採決で温存された残候補（候補 1 残り 4 event + 候補 5 残り CTL 連動自動度）の Wave 3 採用判断。

### options

| ID | stance |
|---|---|
| A | Wave 3 で全 4 event を採用（PreCompact / UserPromptSubmit / Notification / SubagentStop）+ continuous-learning CTL 連動自動度を実装 |
| B | PreCompact のみ採用（Wave 1 で minority opinion あり）、他 3 event は Wave 4 申し送り、continuous-learning は候補出力のみ継続 |
| C | 全 4 event を Wave 3 でも採用せず、Wave 4 / 5 で再諮問 |

### persona 並列意見

- **経営者** (weight 4): 観測経路の拡張は実利大、4 event 採用で観測カバレッジを上げる。CTL 連動は効率化に寄与 → **A 推奨**（confidence 0.60、運用データ不足を考慮）
- **開発者** (weight 4): observation log の volume 増は HV 負荷増、4 event 一括は時期尚早。PreCompact のみ採用が現実的。CTL 連動は w2qb01 判決を 1 Wave で覆すのは経験不足 → **B 推奨**（confidence 0.78）
- **哲学者** (weight 3): 第 8 条 (A 採決で 3 段階) 採決後、自律拡張は「観測 → 候補化 → 人間最終承認」を経由必要。CTL 連動自動度は Wave 4 で第 8 条運用観測後に判断。PreCompact は単機能で緊張低、採用可 → **B 推奨**（confidence 0.80）

### 採点

| stance | supporters | weight_sum | weighted_score |
|---|---|---|---|
| A | 経営者 | 4 | 4 × 0.60 = **2.40** |
| B | 開発者 + 哲学者 | 7 | (4×0.78) + (3×0.80) = 3.12 + 2.40 = **5.52** |
| C | （該当者なし） | 0 | 0 |

B が max (5.52)、明確な収束。

### 判定

- **recommended**: **B**（PreCompact のみ採用、他 3 event と continuous-learning CTL 連動は Wave 4 申し送り）
- **judgment_confidence**: 0.79
- **minority_opinion (A)**: 経営者意見 — Wave 4 末で PreCompact 採用の運用実績を観測（observation log 件数 ≥ 500 + PreCompact entry が観測ログ全体の ≥ 5% を占めた場合）、健全なら UserPromptSubmit / Notification を Wave 5 で追加諮問
- **third_way_excluded**: なし
- **human_escalated**: false
- **consensus_mode**: auto_agree
- **implementer_consent**: agreed_recommended

### cascade_to

`.claude/hooks.json` に PreCompact event 追加（5 → 6 event）。`crosscut-hook-observer/SKILL.md` の SUPPORTED_EVENTS 列挙に PreCompact 追加。`harness-verifier/checks/hook_observations.py` の SUPPORTED_EVENTS set に追加。`crosscut-hook-observer/references/output-format.md` の event 一覧更新。continuous-learning CTL 連動は本 Wave 不実装、Wave 4 申し送り素材として SPEC starter §5 に記録。

---

## 諮問 3: philosophy-changelog auto-emit

- **invocation_id**: `council-2026-05-11T09:00:00Z-w3qb03`
- **judgment_type**: simple_conflict（運用方式選定）
- **category**: `operation`（運用判断）— council-weights.md §situational_modifier.operation 適用
- **final_weights**: base 3/4/3 + operation 補正 +1/0/-1 = **経営者 4 / 開発者 4 / 哲学者 2**
- **context**: philosophy.md 改訂時に delta を `history/PHILOSOPHY-CHANGELOG.md` に追記する機構の運用方式選定。

### options

| ID | stance |
|---|---|
| A | PHILOSOPHY-CHANGELOG.md 新設 + 自動 emit（commit hook or PR action）、Wave 3 で第 8 条追加と同時に運用開始 |
| B | PHILOSOPHY-CHANGELOG.md 新設 + 改訂時手動追記、自動 emit は不要 |
| C | CHANGELOG 不要、commit message 規約のみで運用 |

### persona 並列意見

- **経営者** (weight 4): 改訂履歴の集中管理は意思決定速度に寄与、自動 emit で運用負荷ゼロ → **A 推奨**（confidence 0.80）
- **開発者** (weight 4): 自動 emit の実装は重い（commit hook or PR action 設計）、手動運用で十分 → **B or C** 推奨、B 側で運用継続。**B 推奨**（confidence 0.70）
- **哲学者** (weight 2): philosophy 改訂は append-only な歴史記録として制度化すべき、CHANGELOG 形式は適切。ただし「自動 emit」は第 8 条 (A 採決で 3 段階) と整合する必要なく、手動運用（採決時に必ず CHANGELOG 追記）の方がプロセス可視化に寄与 → **B 推奨**（confidence 0.75）

### 採点

| stance | supporters | weight_sum | weighted_score |
|---|---|---|---|
| A | 経営者 | 4 | 4 × 0.80 = **3.20** |
| B | 開発者 + 哲学者 | 6 | (4×0.70) + (2×0.75) = 2.80 + 1.50 = **4.30** |
| C | （該当者なし） | 0 | 0 |

B が max (4.30)。

### 判定

- **recommended**: **B**（PHILOSOPHY-CHANGELOG.md 新設、改訂時に手動追記、自動 emit は不要）
- **judgment_confidence**: 0.72
- **minority_opinion (A)**: 経営者意見 — Wave 4 末で philosophy 改訂頻度 ≥ 2 件/Wave 観測時、自動 emit 化（commit hook or PR action）を再諮問
- **third_way_excluded**: なし
- **human_escalated**: false
- **consensus_mode**: auto_agree
- **implementer_consent**: agreed_recommended

### cascade_to

`history/PHILOSOPHY-CHANGELOG.md` 新設、Wave 3 で第 8 条追加と同時に初回エントリ追加。第 8 条追加 commit で CHANGELOG を手動更新する手順を `dev-env-spec.md` に明記。

---

## 諮問 4: 振り返り儀式テンプレート化（省略判定）

- **invocation_id**: `council-2026-05-11T09:00:00Z-w3qb04`
- **判定**: **諮問省略**
- **省略根拠**: chewing protocol §3 諮問判定で `confidence ≥ 0.7` 基準を満たす
  - 振り返り儀式の規格化は philosophy 本体に変更なし
  - templates/rituals/ 配下追加のみ、既存機構に影響なし
  - 緊張度 **軽微**、tradeoff 不在
- **implementer_consent**: `auto_proceed`（諮問省略時のデフォルト）
- **cascade_to**: Phase C で `templates/rituals/wave-end-retrospective.template.md` を配置

---

## Phase B 完遂要約

| 諮問 | recommended | confidence | category | 実装反映 |
|---|---|---|---|---|
| w3qb01: 第 8 条本格諮問 | **A**: 3 段階明文化 | 0.55 | conception | philosophy.md 第 8 条追加（3 段階）、minority C 温存 |
| w3qb02: 議題 2 残候補 | **B**: PreCompact のみ | 0.79 | judgment | hooks.json + observer + HV に PreCompact 追加 |
| w3qb03: philosophy-changelog | **B**: 手動運用 | 0.72 | operation | history/PHILOSOPHY-CHANGELOG.md 新設、手動追記 |
| w3qb04: 儀式テンプレート | 諮問省略 | ≥ 0.7 | — | templates/rituals/ 配置 |

3 件すべて `agreed_recommended` で合意成立、`human_escalated: false`。

### Wave 1 / 2 の B 系収束パターンとの比較

| Wave | 収束方向 |
|---|---|
| Wave 1 (3 諮問) | すべて B 系（保守的） |
| Wave 2 (3 諮問) | すべて B 系（保守的） |
| **Wave 3 (3 諮問)** | **w3qb01: A（哲学者 C と接近、minority 温存）、w3qb02: B、w3qb03: B** |

Wave 3 諮問 1 では Wave 1 / 2 の純粋な B 系収束パターンが **崩れて** A 系（哲学者の C と接近採決）に収束した。これは第 8 条本格諮問の特殊性（philosophy 改訂は不可逆度高、3 段階先行 + 4 段階拡張を minority opinion 温存で扱う方が DH 設計原則と整合）の反映で、Wave 4 / 5 で minority opinion 再評価機構が機能するかの実証機会となる。

### category 適用の Wave 別記録

| Wave | 諮問 | 適用 category | final_weights |
|---|---|---|---|
| Wave 3 | w3qb01 | conception | 3/3/5 |
| Wave 3 | w3qb02 | judgment | 4/4/3 |
| Wave 3 | w3qb03 | operation | 4/4/2 |

Wave 1 / 2 では諮問記録に category の明示が抜けていた箇所が一部あったが、Wave 3 では SPEC starter の Copilot review (PR #80) を受けて全諮問で明示することにした。本記録は council-weights.md 規約の実適用例として後続 Wave の参照素材となる。

---

## 哲学的注記

Wave 3 Phase B 諮問結果は **Wave 1 / 2 の純粋な B 系収束を初めて部分的に破った** Wave:

- **諮問 1 (philosophy 改訂)**: A（3 段階明文化）で経営者 + 開発者が連合、哲学者の C 案（4 段階）と接近採決。第 8 条 minority opinion を Wave 5 で 4 段階拡張に発展させる経路を温存
- **諮問 2 (議題 2 残)**: B（保守的、PreCompact のみ）で Wave 1 / 2 の収束パターン継承
- **諮問 3 (philosophy-changelog)**: B（手動運用）で Wave 1 / 2 の収束パターン継承

これは咀嚼プロトコル T3 + ガードレール語彙化の自然な動作で、「philosophy 改訂は最小単位で前進、拡張余地は minority opinion で温存」という DH 設計原則の素直な反映。

特に **諮問 1** で 0.55 という接近採決の confidence が記録されたことは、Wave 5 で「3 段階運用の実 Council 経由率」を観測することで minority C を再諮問する **経験的データ駆動の再判断機構** が DH に組み込まれていることの実証となる。
