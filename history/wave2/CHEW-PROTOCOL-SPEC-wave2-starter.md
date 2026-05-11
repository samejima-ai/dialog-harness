# 咀嚼プロトコル Wave 2 SPEC ドラフト起点

**作成日時**: 2026-05-11T06:30:00Z
**起点 PR**: [PR #77](https://github.com/samejima-ai/dialog-harness/pull/77)（Wave 2 Phase A）
**前提 PR**: [PR #76](https://github.com/samejima-ai/dialog-harness/pull/76)（Wave 1、merged）
**Council 採決根拠**: 議題 0 `council-2026-05-11T03:49:01Z-4go7g1`（B 採択 + 哲学者止揚、咀嚼プロトコル 4 ステップ規格化）
**ユーザー方針補足**: 「AI 自律駆動 + 哲学ガードレール経路」（DH の自律性は philosophy 6 条 + 第 8 条候補で保護）

---

## 0. 本 PR 範囲（Phase A）

本 PR の commit に含めるのは:
- 本ファイル（Wave 2 SPEC 起草）
- draft PR 作成

Phase B 以降（Council 諮問 / SPEC 実装 / 検証 / merge）は **後続セッションで実行**。Wave 1 と同じ段階分割アプローチ（candidate 単位ではなく Phase 単位の commit）を継承。

優先順位は本 SPEC §1.2 で確定: **harness-verifier 拡張 → 候補 5 → 候補 2 → 候補 4**。

---

## 1. Wave 2 全体スコープ

### 1.1 採用候補

PR #75 CHEW-CANDIDATES-metaskill-2026-05-11.md の 8 候補のうち、Wave 1 で未着手の以下を Wave 2 で扱う:

| # | 候補名 | origin | DH 緊張度 | 優先 |
|---|---|---|---|---|
| **HV** | harness-verifier hook 観測ログ読取拡張 | Wave 1 申し送り | 軽微 | **1**（土台） |
| **5** | continuous-learning v2.1（hook → instinct promotion） | ECC `continuous-learning/` | **最高** | **2** |
| **2** | origin/version frontmatter 規格を全 chewed skill 必須化 | ECC frontmatter 慣例 | 軽微 | **3** |
| **4** | AgentShield ルールサブセット選別 | ECC `AgentShield/` | 高 | **4** |

候補 7（philosophy delta auto-emit）/ 候補 8（共通振り返り儀式 chewed）/ 議題 2 再上程 / philosophy 第 8 条候補は **Wave 3 へ申し送り**。

### 1.2 優先順位の根拠（ユーザー方針 + Council 議題 0 整合）

「harness-verifier 拡張 → 候補 5 → 候補 2 → 候補 4」の順:

1. **HV (harness-verifier 拡張)** を最初に置く理由:
   - Wave 1 で hook 観測ログ生成までは実装済だが、消費側（verify.py 読取）は未実装
   - 候補 5（continuous-learning）は hook 観測ログを入力源とする → 消費側の骨格が先に必要
   - 独立性原則の最終形（書き手 = skill / 読み手 = harness-verifier）を Wave 2 の冒頭で確立

2. **候補 5（continuous-learning v2.1）** を 2 番目に置く理由:
   - DH 哲学との緊張度 **最高**（自動学習 / instinct promotion が哲学ガードレールを侵食する危険）
   - Wave 2 で最も重い諮問対象（philosophy 第 6 条「人間最終承認」 + 第 7 条「AI 組織論」 + 第 8 条候補「自律性原則 + 哲学ガードレール」との同時整合）
   - HV 拡張が完了してから着手することで、CL の動作実証経路が独立検証付きで担保される

3. **候補 2（origin/version frontmatter 必須化）** を 3 番目に置く理由:
   - DH 緊張度 **軽微**、T1 構造保持の純粋な語彙化作業
   - Wave 1 で crosscut-hook-observer に先取り適用済の規格を、既存 17 skill に展開
   - 候補 5 の動作実証データが揃った段階で「観測 origin がどう保護されたか」の根拠を SPEC に書き込める

4. **候補 4（AgentShield ルールサブセット選別）** を 4 番目に置く理由:
   - DH 緊張度 **高**、哲学者ペルソナ Council 必須
   - ECC AgentShield の 11+ ルール群から DH 哲学と整合するもののみ採用
   - 候補 5 と候補 2 の経験を踏まえ「ガードレール語彙が成熟した状態」で着手

### 1.3 Wave 2 で扱わないこと

- **候補 7 (philosophy delta auto-emit)**: 候補 5 の動作実証が前提、Wave 3 で実装
- **候補 8 (共通振り返り儀式 chewed)**: 候補 5 + 候補 2 の Wave 2 末振り返り儀式で観測してから Wave 3 で実装判断
- **議題 2 再上程**: philosophy 第 8 条候補と同梱で Wave 3 へ
- **philosophy 第 8 条候補 (PHILOSOPHY-NOTE-autonomy-with-guardrails)**: Wave 3 で本格諮問

---

## 2. 候補別 SPEC ドラフト

### 2.1 HV: harness-verifier hook 観測ログ読取拡張

#### 2.1.1 観察 (Step A) — Wave 1 申し送り

Wave 1 Phase C で `.claude/skills/crosscut-hook-observer/scripts/observe.py` が `harness-verifier/reports/hook-observations.jsonl` に append-only で観測ログを書き込む経路が確立済。消費側は未実装で、ログは「将来の消費者に向けて蓄積される素材」として機能している。

Wave 1 SPEC starter §5 + SKILL.md §「Wave 2 以降の予定」+ output-format.md §「harness-verifier 側の読み取り規約（Wave 2 以降の予定）」で実装予定を明示済。

#### 2.1.2 分解 (Step B)

| 要素 | 採用 | 翻訳タイプ |
|---|---|---|
| `harness-verifier/verify.py` 拡張: hook-observations.jsonl 読取 | ✓ | 新規（T1 構造保持の延長） |
| 末尾 N 行読取（暫定 N = 1000） | ✓ | 新設定数 |
| JSONL parse error 行の skip | ✓ | fail-open 継承 |
| event / tool / session_id パターン分析 | ✓ | D5 観測項目に追加 |
| 観測結果の独立出力 | ✓ | `harness-verifier/reports/<run-id>.md` |
| observation ファイル改変 | ✗ | append-only 維持、改変は厳禁 |
| harness-verifier/glossary.yml への用語追加 | ✓ | `hook_observation` 等の用語化 |
| harness-verify.yml workflow への影響 | △ | `--strict` 経路は不変、月次経路で観測解析を追加 |

#### 2.1.3 DH 哲学フィルター適用

| 要素 | 哲学的判定 |
|---|---|
| 読取専用（observation ファイル改変なし） | ✓ 独立性原則（一方向依存）と整合 |
| 検証結果の独立出力 | ✓ D5「機構自身の自律性保護」と整合 |
| parse error の fail-open | ✓ 第 6 条「人間最終承認」と整合（自動 block しない） |
| 月次 cron で経過レポート生成 | ✓ HUMAN-PROTOCOL.md §1 と整合 |

#### 2.1.4 Wave 2 実装スコープ（HV）

- 拡張: `harness-verifier/verify.py` — 新検査項目 6「hook 観測一貫性」追加
- 新設: `harness-verifier/checks/hook_observations.py`（または既存 checks/ に追加、コードベース確認後決定）
- 拡張: `harness-verifier/glossary.yml` — `hook_observation` / `instinct_promotion`（候補 5 連動）等の用語追加
- 拡張: `harness-verifier/README.md` / `BOUNDARY.md` — 観測ログ消費の範囲を明文化

#### 2.1.5 検証項目（Step D, HV）

- [ ] verifier-philosophy: 読取専用かつ独立出力の経路が第 6 条と整合
- [ ] verifier-drift: SPEC.md / DONT.md / harness-verifier/PHILOSOPHY.md と整合
- [ ] 動作実証: 観測ログを mock 流し込み → verify.py が D5 報告に反映するか確認
- [ ] glossary 整合: 新規追加用語が既存 prefix 規約と衝突しない

---

### 2.2 候補 5: continuous-learning v2.1

#### 2.2.1 観察 (Step A)

ECC `continuous-learning/` は **「ユーザー / 観測の振る舞いから skill が自動学習し、頻出パターンを instinct（直感層） に promote する」** 機構。Wave 1 で観測 hook を導入したことで、DH も同様の learning loop を組み込み可能な状態になった。

ただし DH 哲学では「人間 ≒ Council」原則（philosophy 第 6 条）と「AI 組織論」（第 7 条）があり、自動学習・自動 promotion は **無条件採用できない**。

#### 2.2.2 分解 (Step B)

ECC continuous-learning の主要要素:

| 要素 | DH 採用判断 |
|---|---|
| 観測 → pattern 検出 → 候補化 | ✓ 採用候補 |
| pattern 候補 → instinct への自動 promote | △ Council 諮問必須（自動 vs 半自動 vs 全手動の境界） |
| 既存 skill の auto-amend | ✗ 棄却候補（人間最終承認原則と衝突、独立性原則違反） |
| feedback loop（pattern → SPEC 反映） | △ crosscut-feedback-loop と接続点（責務分離が必要） |
| 学習データの透明性（観測ログから根拠提示） | ✓ 採用、harness-verifier 経由で観測根拠を保護 |

#### 2.2.3 DH 哲学フィルター適用

| 要素 | 哲学的判定 |
|---|---|
| pattern 検出経路 | ✓ 観測層と一致 |
| **自動 promote** | △ CTL 連動で自動度変化（CTL 0 = 全手動 / CTL 1+ = 半自動 / CTL 2+ = 自動だが Council 推奨） |
| 既存 skill auto-amend | ✗ **棄却**（第 6 条 + 第 7 条 P4 介入権 + 独立性原則すべてに抵触） |
| 学習根拠の透明性 | ✓ 第 6 条「人間最終承認」の前提を強化 |
| 観測ログへの自動書き戻し | ✗ append-only 違反、独立性原則違反 |

#### 2.2.4 Wave 2 実装スコープ（候補 5）

候補 5 は範囲が大きいため、**Wave 2 内では「pattern 検出層」と「promote 半自動経路」のみ実装**:

- 新設 skill: `crosscut-continuous-learning`（pattern 検出 + promote 候補生成）
  - 入力: `harness-verifier/reports/hook-observations.jsonl`（観測ログ）
  - 出力: `delivery/CONTINUOUS-LEARNING-CANDIDATES-<timestamp>.md`（promote 候補リスト、人間レビュー前提）
- **自動 promote は実装しない**（Wave 3 候補に温存、Council 諮問次第）
- CTL 0 では skill 自体を inactive 化（philosophy 第 6 条厳格適用）
- CTL ≥ 1 で active、promote 候補を delivery/ に出力するのみ、適用は人間判断
- Council 諮問の少数意見をすべて温存（Wave 3 振り返り儀式で再評価）

#### 2.2.5 検証項目（Step D, 候補 5）

- [ ] verifier-philosophy: 自動 promote が **実装されていない** ことの SPEC 整合確認
- [ ] verifier-drift: 第 6 条 / 第 7 条 / 第 8 条候補との整合
- [ ] 動作実証: hook-observations mock データから promote 候補を生成し、人間レビュー workflow が成立するか
- [ ] 独立性: continuous-learning skill が harness-verifier に依存していないこと（一方向）

---

### 2.3 候補 2: origin/version frontmatter 全 skill 必須化

#### 2.3.1 観察 (Step A)

ECC では skill / agent / プロンプト系資産に対し `origin` / `origin_source` / `origin_version` 等の frontmatter で素材出自を明示する慣例がある。Wave 1 で `crosscut-hook-observer/SKILL.md` に先取り適用済（5 フィールド: origin / origin_source / origin_version / chewing_translation / chewing_pr）。

#### 2.3.2 分解 (Step B)

| 要素 | DH 採用判断 |
|---|---|
| origin: ECC-derived / DH-native / external 等の分類 | ✓ |
| origin_source: 元素材の参照ポインタ | ✓ |
| origin_version: 元素材の version 固定 | ✓ |
| chewing_translation: T1/T2/T3 タイプ表示 | ✓ DH 拡張 |
| chewing_pr: 取り込み PR 番号 | ✓ DH 拡張 |
| chewed_at: 取り込み日時 | △ 採用 / 検証時刻と分離 |
| chewing_council_ref: 諮問 invocation_id | ✓ Council 経由素材のみ |

#### 2.3.3 DH 哲学フィルター適用

| 要素 | 哲学的判定 |
|---|---|
| origin 明示 | ✓ 観察温存原則と整合 |
| version 固定 | ✓ drift verifier との接続点 |
| chewing_pr 記録 | ✓ 第 7 条「AI 組織論」のトレーサビリティ強化 |
| 既存 skill への一括適用 | △ Wave 1 と同じく逐次 vs 一括の諮問が必要 |

#### 2.3.4 Wave 2 実装スコープ（候補 2）

- 拡張: `dev-env-spec.md` に「origin/version frontmatter 規格」セクション追加（Wave 1 で SKILL.md に書いた規格を正式化）
- 拡張: 既存 17 skill の SKILL.md frontmatter に origin 系フィールド追加（**Council 諮問次第で一括 / 逐次決定**）
- 拡張: `harness-verifier/glossary.yml` に `origin_prefix` 等の規約追加
- 拡張: drift verifier が origin_version mismatch を検出できる経路（既存検査項目との衝突回避が必要）

#### 2.3.5 検証項目（Step D, 候補 2）

- [ ] verifier-drift: origin_version 規約が drift 検出を阻害しない
- [ ] 既存 skill との backward compat: 旧 frontmatter フィールドが残っていても fail しない
- [ ] harness-verifier --strict 維持

---

### 2.4 候補 4: AgentShield ルールサブセット選別

#### 2.4.1 観察 (Step A)

ECC `AgentShield/` は AI agent 向けの安全規約集で、11+ のルール（rule-001 〜 rule-011+）から構成される。DH 哲学との緊張度が **高い** ため、哲学者ペルソナ Council 必須。

#### 2.4.2 分解 (Step B) — 暫定

詳細な 11+ ルールの DH 哲学整合性検査は **Phase B で哲学者ペルソナ Council 諮問** に委ねる。Phase A では「諮問構造のみ確定」。

仮 chunking:

| ルール群 | DH 哲学との整合性（暫定） |
|---|---|
| 入力 sanitization 系 | ✓ 採用候補 |
| 出力検閲系 | △ Council 諮問（検閲は第 6 条と緊張） |
| tool use 制限系 | △ Council 諮問（philosophy 第 7 条 P4 介入権との関係） |
| 自動 block 系 | ✗ 棄却候補（hook 機構と同じ理由、warn のみ採用） |

#### 2.4.3 Wave 2 実装スコープ（候補 4）

- 新設 (Phase B 後): `delivery/AGENTSHIELD-SUBSET-DECISION-wave2.md`（哲学者ペルソナ Council 採決記録）
- 新設 (Phase C, 採用ルールのみ): `templates/rules/common/agentshield-<rule-id>.md` 等
- 拡張: `dev-env-spec.md` で AgentShield 規約参照

#### 2.4.4 検証項目（Step D, 候補 4）

- [ ] verifier-philosophy: 採用ルールが第 6 条 + 第 7 条と整合
- [ ] 棄却ルールが Council 採決記録に温存され、Wave 3 再諮問可能な状態

---

## 3. Phase B Council 諮問 agenda（Wave 2、暫定 3 件 + 候補 4 専用 1 件）

Phase A 完遂後、後続セッションの Phase B で以下を諮問する:

### 諮問 1: continuous-learning v2.1 の自動度境界

- **agenda_id**: `council-w2qb01`
- **context**: 候補 5 で「pattern 候補生成」までは決定済。Council 諮問で「自動 promote の境界」を決定する。
- **judgment_type**: tradeoff（自動度 vs 哲学整合性）
- **options**:
  - A: CTL に応じた段階的自動度（CTL 0 = inactive / CTL 1 = 候補出力のみ / CTL 2 = 自動 promote だが Council 必須）
  - B: 全 CTL で候補出力のみ、適用は人間最終承認（最も保守的、Wave 3 で再諮問）
  - C: 自動 promote を 1 度も実装せず、Wave 3 でも候補出力のみで運用継続

### 諮問 2: AgentShield 11+ ルールの DH 採用範囲

- **agenda_id**: `council-w2qb02`
- **context**: 候補 4 の 11+ ルールから DH 哲学と整合するもののみ採用。哲学者ペルソナ Council 必須。
- **judgment_type**: tradeoff（安全性 vs 自律性 + 第 6 条「人間最終承認」整合）
- **persona**: business council + 哲学者ペルソナ単独追加（候補 4 専用）
- **options**: 11+ ルール個別に採否判定（A 採用 / B 棄却 / C 条件付き採用）

### 諮問 3: origin/version frontmatter 既存 17 skill 適用タイミング

- **agenda_id**: `council-w2qb03`
- **context**: Wave 1 の skill description 監査と同型問題。一括 vs 逐次の選択。
- **judgment_type**: simple_conflict（Wave 1 と同パターン）
- **options**:
  - A: Wave 2 内で 17 skill 一括適用
  - B: 各 skill 次回更新時に逐次適用（Wave 1 と同型）
  - C: Wave 2 で 5 skill のみ先行、残り 12 skill は Wave 3 申し送り

### 諮問予備: HV 拡張の harness-verify.yml 経路

- **agenda_id**: `council-w2qb04`（オプショナル）
- **context**: harness-verifier 拡張で月次 cron に観測解析を追加するか、`--strict` PR 経路は不変のまま月次のみ拡張するか。
- 緊張度が低ければ Phase B で省略可能（chewing protocol §3 諮問判定で confidence ≥ 0.7 なら諮問不要）

---

## 4. Wave 2 全体マイルストーン

| Phase | 内容 | 完了基準 | 状態 |
|---|---|---|---|
| **Phase A**（PR #77） | Wave 2 SPEC ドラフト + 優先順位確定 + Council 諮問 agenda 提示 | SPEC starter commit + draft PR | ✅ 完遂（PR #77 merged） |
| **Phase B**（本 PR） | Council 諮問 3 件採決 + 予備 1 件省略判定 | 諮問 1-3 agreed_recommended、諮問 4 省略 | ✅ 完遂（本 commit） |
| **Phase C**（本 PR） | SPEC 実装（HV → 候補 5 → 候補 2 → 候補 4 の順） | 実装 + harness-verifier --strict PASS | ✅ 完遂（本 commit） |
| **Phase D** | 検証 + verifier 経由抵触チェック | philosophy / drift 抵触 0 | レビュー時 |
| **Phase E** | merge + REGIME-LOG 記録 + Wave 3 への申し送り | v5.13.x minor リリース | merge 後 |

### Phase B 諮問結果サマリ（本 commit で確定）

| invocation_id | recommended | confidence | conflict_type |
|---|---|---|---|
| `council-2026-05-11T07:00:00Z-w2qb01`（continuous-learning 自動度） | **B**: 候補出力のみ、人間最終承認 | 0.82 | tradeoff、B 系収束 |
| `council-2026-05-11T07:00:00Z-w2qb02`（AgentShield 採用範囲） | **B**: 5 カテゴリ warn のみ参照導入 | 0.85 | tradeoff、B 系収束（哲学者重み増強） |
| `council-2026-05-11T07:00:00Z-w2qb03`（frontmatter 適用タイミング） | **B**: 逐次適用（Wave 1 と同型） | 0.76 | simple_conflict、B 系収束 |
| `council-2026-05-11T07:00:00Z-w2qb04`（HV 拡張 yml 経路） | 諮問省略（confidence ≥ 0.7） | — | 緊張度軽微 |

3 件すべて `human_escalated: false` + `agreed_recommended`、`history/wave2/COUNCIL-DECISION-wave2-phaseB-2026-05-11T07:00:00Z.md` に詳細記録、`history/COUNCIL-LOG.md` に append-only 追記済。

minority opinion 3 件は Wave 2 末 / Wave 3 末の振り返り儀式で再評価項目として温存。Wave 2 Phase B は Wave 1 Phase B と同様 **B 系（保守的・人間最終承認尊重）に収束** し、咀嚼プロトコル T3 + ガードレール語彙化が DH 哲学の自然な帰結として動作することが実証された。

---

## 5. 後続 Wave への申し送り

### Wave 3（候補 7 + 8 + 議題 2 再上程 + 第 8 条候補）の前提条件

- Wave 2 で hook 観測 → continuous-learning → harness-verifier 解析の loop が動作していること
- Wave 2 で origin/version frontmatter が安定運用されていること
- AgentShield Council 採決記録（諮問 2）で哲学ガードレール語彙が成熟していること
- philosophy 第 8 条候補（PHILOSOPHY-NOTE-autonomy-with-guardrails）の v5.13.0 reservation が、Wave 3 で本格諮問可能な状態に揃っていること

### Wave 3 諮問予定

- 議題 2 再上程: Wave 1 で「Step 1 (Wave 1) の検証データが揃ってから Step 2 として実装」が conditional accept された議題の本諮問
- philosophy 第 8 条候補: 自律性原則 + 哲学ガードレールの philosophy.md 第 8 条化
- 候補 5 自動 promote 再諮問: Wave 2 諮問 1 で棄却 / 保留された経路の再評価
- 候補 7 (philosophy delta auto-emit): 候補 5 動作実証経路上に乗せる
- 候補 8 (共通振り返り儀式 chewed): Wave 2 末振り返り儀式の観測データを根拠に実装判断

---

## 6. 哲学的注記

Wave 2 は Wave 1 と比べて **DH 哲学との緊張度が一段階高い** 範囲を扱う。特に候補 5（continuous-learning）と候補 4（AgentShield）は、ECC の素材をそのまま採用すると DH 第 6 条「人間最終承認」と第 7 条「AI 組織論」の両方を侵食する危険がある。

このため Wave 2 では Wave 1 の T1 + T3 中心の翻訳から **T3 + ガードレール語彙化** が中心戦略になる:

- **T3（サブセット選別）**: ECC の機能網羅性を捨て、DH 哲学整合分のみ採用
- **ガードレール語彙化**: CTL / dev_mode / philosophy 条文との整合経路を SPEC に明文化

優先順位「HV → 候補 5 → 候補 2 → 候補 4」は **緊張度ではなく依存順序** で決定されている:

1. HV: 候補 5 の入力源を保護する基盤
2. 候補 5: Wave 2 で最も重い諮問対象、観測データの蓄積が始まる前に実装
3. 候補 2: 候補 5 の動作実証データを「origin 明示で保護」する規格
4. 候補 4: 候補 2 までで成熟した語彙を踏まえて選別

Wave 1 で確立した咀嚼プロトコル 4 ステップ（観察 → 分解 → 翻訳 → 検証）は Wave 2 でも厳格に適用される。Wave 1 と異なるのは **「翻訳」段階でガードレール語彙が中心になる** 点で、これは PHILOSOPHY-NOTE-autonomy-with-guardrails で先取りした「咀嚼 = 構造保持 + 適用条件のガードレール化」と整合する。
