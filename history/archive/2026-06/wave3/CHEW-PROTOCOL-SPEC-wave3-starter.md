# 咀嚼プロトコル Wave 3 SPEC starter（ドラフト）

**起票**: 2026-05-11T08:30:00Z（Wave 2 PR #78 merged 後続、PR #79 archive 並行）
**起票元**: spec-architect L0 経由、議題 0 採決 `council-2026-05-11T03:49:01Z-4go7g1` に基づく Wave 3 着手
**branch**: `claude/chew-protocol-spec-wave3`
**Phase**: Phase A — SPEC ドラフト起草 + 優先順位確定 + Council 諮問 agenda 提示

---

## 0. 本ファイルの位置づけ

咀嚼プロトコル Wave 3 の **Phase A 起点ファイル**。Wave 1 SPEC（PR #76 merged）+ Wave 2 SPEC（PR #77 + PR #78 merged）の到達点と minority opinion / 申し送り素材を継承し、Wave 3 で着手すべき候補群を整理して Phase B 諮問 agenda を提示する。

Wave 3 の最重要議題は **議題 2「Step 2 第 2 段（残候補の取り込み）」の再上程** および **philosophy 第 8 条候補（自律性 + 哲学ガードレール）の本格諮問** の 2 件。前者は Wave 1 末 / Wave 2 末で観測された運用実績を踏まえた再判断、後者は Wave 1 + Wave 2 で観察された **B 系収束パターン** の哲学的言語化。

## 1. Wave 1 + Wave 2 振り返り

### 1.1 完遂事項

| Wave | PR | 主要成果 |
|---|---|---|
| Wave 1 | #76 | 咀嚼プロトコル枠組み確立、5 hooks event 採用、skill description 監査 (逐次)、templates/rules 階層化、observation/hook 観測機構 |
| Wave 2 Phase A | #77 | Wave 2 SPEC ドラフト、ファイル意図ベース配置規則の確立 |
| Wave 2 Phase B+C | #78 | HV 検査項目 6 (hook 観測一貫性)、crosscut-continuous-learning 新設、origin/version frontmatter 規格、AgentShield 参照導入規約 |
| 移行 | #79 | PR #77 規約準拠で過去 Wave ファイル 36 件を history/ archive |

### 1.2 確認された経験的事実

**B 系収束パターンの 2 回連続観測**:

Wave 1 Phase B (3 諮問 + 1 省略)、Wave 2 Phase B (3 諮問 + 1 省略) のすべてが B 系（保守的・人間最終承認尊重）に収束した。具体的には:

| 諮問 | recommended |
|---|---|
| w1qb01 (5 event 採用 vs 全 9 event) | B: 5 event + PreCompact 棄却 |
| w1qb02 (skill description 一括 vs 逐次) | B: 逐次 |
| w1qb03 (言語先取り) | A: 言語先取りなし |
| w2qb01 (continuous-learning 自動度) | B: 候補出力のみ、人間最終承認 |
| w2qb02 (AgentShield 採用範囲) | B: 5 カテゴリ warn のみ参照導入 |
| w2qb03 (frontmatter 適用タイミング) | B: 逐次適用 |

T3 (サブセット選別) + ガードレール語彙化 が DH 哲学の自然な帰結として動作することの **2 サンプル蓄積**。Wave 3 で philosophy 第 8 条候補を本格諮問する際の経験的根拠として参照可能になった。

### 1.3 Wave 2 末振り返りの観測項目（Wave 3 で評価）

| 観測項目 | 評価対象 | 発生 minority opinion |
|---|---|---|
| crosscut-continuous-learning 候補出力経路の運用実績 | w2qb01 minority A (CTL 連動自動度) | Wave 3 で再諮問 |
| 17 skill description 監査逐次進捗 | w1qb02 minority A (一括) | 進捗 ≤ 50% で Wave 3 一括再諮問 |
| 17 skill frontmatter 監査逐次進捗 | w2qb03 minority A (一括) | 進捗 ≤ 50% で Wave 3 一括再諮問 |
| ECC 14 言語 L0 対話頻出度 | w1qb03 minority A (3 言語先取り) | 頻出 3 言語が L0 対話確定の場合は推奨プリセット化 |
| AgentShield npm install 推奨実績 | w2qb02 minority A (utilizer 側手動 install 推奨可) | 利用者側の実 install 観察 |
| Wave 1 ECC-SURVEY 6 ヶ月再観察予約 | 2026-11-11 予定 | ECC 進化追従 |

これらは **Wave 3 Phase A の起票時点で評価できない**（運用データ蓄積待ち）。Wave 3 Phase B / 後続セッションで再評価し、再諮問の起票判断材料とする。

## 2. Wave 3 候補一覧と優先順位

### 2.1 優先 1: 議題 3 (philosophy 第 8 条候補の本格諮問)

**Wave 1 PHILOSOPHY-NOTE-autonomy-with-guardrails-2026-05-11** で起草され、Wave 1 + Wave 2 の B 系収束 2 サンプルを経験的根拠として、philosophy.md 第 8 条として **正式追加** するかを諮問する。

#### 条文ドラフト

> **第 8 条 自律性原則 + 哲学ガードレール**
>
> AI 自律性の拡張は、観測 → 候補化 → 人間最終承認 の 3 段階を経由するものとする。各段階の自動化レベルは CTL に連動し、CTL 0 では候補出力すら抑止する（観察温存）。自律拡張の各機構（continuous-learning / instinct promotion / 自動 Issue 化 / 自動 PR merge 等）は、本条の 3 段階を経由しない経路を持たないことを設計時に検証する。

#### 候補数

- **A**: 第 8 条として明文化、philosophy.md に追加
- **B**: 第 8 条候補のまま PHILOSOPHY-NOTE で温存、Wave 4 / Wave 5 で再諮問
- **C**: 第 8 条として明文化、ただし「観測 → 候補化 → 人間最終承認」の 3 段階を「観測 → 候補化 → 採決 → 適用」の 4 段階に拡張（Council 必須を明示）

#### Council 諮問の重み配分

第 8 条本格採決には `category: conception` を適用する。`crosscut-council/council-weights.md` の規約に従い、`base_weights.business` (経営者 3 / 開発者 4 / 哲学者 3) + `situational_modifier.conception` (経営者 0 / 開発者 -1 / 哲学者 +2) により、**final_weights = 経営者 3 / 開発者 3 / 哲学者 5** で計算される。

これは議題 0 採決 `council-2026-05-11T03:49:01Z-4go7g1`（同じく `category: conception` 適用）と同一規約準拠。Wave 3 諮問では council-weights.md の編集（L0 経由のみ可）は行わず、既存規約のカテゴリ選択で対応する（私が以前のドラフトで書いた「哲学者重み 5 → 7/8 増強」記述は規約根拠を持たない誤記で、本改訂で訂正）。

#### 緊張度

**最高**: philosophy.md 改訂は DH 全体の規範変更で、後続 Wave のすべての判断基盤に影響する。Council 諮問は agenda 単独で扱う。

### 2.2 優先 2: 議題 2 再上程（Step 2 第 2 段）

**議題 0 採決** で Wave 1 着手と確定したが、議題 2 は「採決時点では時期尚早」で温存された残候補群:

- 候補 1 残り: hooks 9 event のうち PreCompact / UserPromptSubmit / Notification / SubagentStop （Wave 1 は 5 event 採用）
- 候補 5 残り: continuous-learning CTL 連動自動度（Wave 2 は候補出力のみ）

#### 候補数

- **A**: Wave 3 で全 4 event を採用（観測実績 2 サンプル蓄積後の再判断）
- **B**: PreCompact のみ採用（Wave 1 で唯一個別 minority opinion あり）、他 3 event は Wave 4 申し送り
- **C**: 全 4 event を Wave 3 でも採用せず、Wave 4 / 5 で再諮問

continuous-learning の自動度は、観測ログの実 entry 数が 1000 件超 + 誤 promote 候補 0 件を確認した場合のみ B 段階に進める拘束条件付き。

#### 緊張度

**中**: philosophy 第 7 条 P4 介入権との緊張は存続するが、Wave 1 + Wave 2 で得られた経験データを根拠に判断可能。

### 2.3 優先 3: 候補 7 — philosophy delta auto-emit

PHILOSOPHY-NOTE / philosophy.md の改訂時に、改訂 delta を **専用 changelog ファイル** に自動 emit する機構。

#### 動機

philosophy.md は DH 全体の規範であり、改訂履歴を append-only に追跡する仕組みが現状欠落している。第 8 条追加（Wave 3 で実施されれば）+ 後続改訂で履歴管理を制度化する。

#### 候補数

- **A**: `history/PHILOSOPHY-CHANGELOG.md` を新設、Wave 3 で第 8 条追加と同時に運用開始
- **B**: 機構のみ実装、運用は philosophy 改訂発生時に逐次
- **C**: 自動 emit ではなく手動運用（commit message 規約のみ）

#### 緊張度

**低**: 観察補助機構、philosophy 本体に変更なし、tradeoff 不在。

### 2.4 優先 4: 候補 8 — 共通振り返り儀式 chewed

Wave 末振り返り儀式の **テンプレート化**。Wave 1 / Wave 2 で個別ファイル（RITUAL-2026-05-11-metaskill.md）を生成したが、Wave 3 以降は共通テンプレートに基づく規格化を提案。

#### 候補数

- **A**: `templates/rituals/wave-end-retrospective.template.md` を新設、Wave 3 末から運用
- **B**: テンプレート化せず、Wave 別個別ファイルのまま継続
- **C**: テンプレート化 + 「振り返り儀式 skill」として独立 skill 化（過剰）

#### 緊張度

**低**: 振り返り儀式の規格化、新機構導入ではない。

### 2.5 優先 5: minority opinions 再評価（観測データ駆動）

Wave 2 末振り返りで蓄積された運用実績に基づき、Wave 1 + Wave 2 で温存された 5 件の minority opinion を再評価する:

| Wave | minority | 再評価条件 | 再諮問起票判断 |
|---|---|---|---|
| w1qb02 A | 一括 description 修正 | 17 skill 進捗 ≤ 50% | データ駆動 |
| w1qb03 A | 3 言語先取り (python/typescript/go) | L0 対話頻出度観測 | データ駆動 |
| w2qb01 A | continuous-learning CTL 連動自動度 | 候補出力経路 運用実績 | データ駆動 |
| w2qb02 A | ecc-agentshield utilizer 側 install 推奨 | 利用者側 install 観察 | データ駆動 |
| w2qb03 A | 一括 frontmatter 修正 | 17 skill 進捗 ≤ 50% | データ駆動 |

これらは **Wave 3 Phase A 時点では起票しない**（運用データ未蓄積）。Phase B / 後続 PR で運用データを評価し、起票判断を行う。

## 3. Phase B Council 諮問 agenda

### agenda 1 (議題 3): philosophy 第 8 条本格諮問 — `council-w3qb01`

- **judgment_type**: tradeoff（philosophy 改訂 vs 候補温存）
- **persona**: business council、`category: conception` 適用（council-weights.md §situational_modifier.conception）。final_weights = 経営者 3 / 開発者 3 / 哲学者 5（base 3/4/3 + conception 補正 0/-1/+2）。
- **options**: A (第 8 条として明文化) / B (候補ノートのまま温存) / C (3 段階 → 4 段階拡張)
- **expected**: A or C への収束、B は Wave 4 申し送り
- **緊張度**: 最高（philosophy 改訂）

### agenda 2 (議題 2 再上程): Wave 3 での議題 2 残候補 — `council-w3qb02`

- **judgment_type**: tradeoff（観測実績 2 サンプル後の判断）
- **persona**: business council 標準
- **options**: A (全 4 event 採用) / B (PreCompact のみ) / C (Wave 4 / 5 再申し送り)
- **expected**: B 系（PreCompact のみ）または C 系収束、A は時期尚早
- **緊張度**: 中

### agenda 3 (候補 7): philosophy-changelog auto-emit — `council-w3qb03`

- **judgment_type**: simple_conflict（運用方式選定）
- **persona**: business council 標準
- **options**: A (auto-emit 実装 + Wave 3 運用開始) / B (機構のみ実装) / C (手動運用)
- **expected**: A 系収束、第 8 条追加と同期
- **緊張度**: 低

### agenda 4 (候補 8): 振り返り儀式テンプレート化 — `council-w3qb04`

- **判定**: **諮問省略**
- **省略根拠**: chewing protocol §3 諮問判定で `confidence ≥ 0.7` 基準を満たす
  - 振り返り儀式の規格化は philosophy 本体に変更なし
  - templates/ 配下追加のみ、既存機構に影響なし
  - 緊張度 **軽微**、tradeoff 不在
- **implementer_consent**: `auto_proceed`

## 4. Wave 3 全体マイルストーン

| Phase | 内容 | 完了基準 | 状態 |
|---|---|---|---|
| **Phase A**（PR #80） | Wave 3 SPEC ドラフト + 優先順位確定 + Council 諮問 agenda 提示 | 本 commit + draft PR | ✅ 完遂（PR #80） |
| **Phase B**（本 PR） | Council 諮問 3 件採決 + 予備 1 件省略判定 | 諮問 1-3 採決、諮問 4 省略 | ✅ 完遂（本 commit） |
| **Phase C**（本 PR） | SPEC 実装（第 8 条追加 → 議題 2 残 → 候補 7 → 候補 8） | 実装 + harness-verifier --strict PASS | ✅ 完遂（本 commit） |
| **Phase D** | 検証 + verifier 経由抵触チェック | philosophy / drift 抵触 0 | レビュー時 |
| **Phase E** | merge + REGIME-LOG / PHILOSOPHY-CHANGELOG 記録 + Wave 4 申し送り | v5.14.x minor リリース | merge 後 |

### Phase B 諮問結果サマリ（本 commit で確定）

| invocation_id | recommended | confidence | category | 適用 weights |
|---|---|---|---|---|
| `council-w3qb01`（第 8 条本格諮問） | **A**: 3 段階明文化 | 0.55 | conception | 3/3/5 |
| `council-w3qb02`（議題 2 残候補） | **B**: PreCompact のみ採用 | 0.79 | judgment | 4/4/3 |
| `council-w3qb03`（philosophy-changelog） | **B**: 手動運用 | 0.72 | operation | 4/4/2 |
| `council-w3qb04`（儀式テンプレート） | 諮問省略 | ≥ 0.7 | — | — |

3 件すべて `human_escalated: false` + `agreed_recommended`、`history/wave3/COUNCIL-DECISION-wave3-phaseB-2026-05-11T09:00:00Z.md` に詳細記録、`history/COUNCIL-LOG.md` に append-only 追記済。

### Wave 1 / 2 との収束パターン差異

| Wave | 諮問 | 収束方向 |
|---|---|---|
| Wave 1 (3 諮問) | w1qb01-03 | すべて B 系（保守的） |
| Wave 2 (3 諮問) | w2qb01-03 | すべて B 系（保守的） |
| **Wave 3 (3 諮問)** | w3qb01-03 | **w3qb01: A（接近採決、minority C 温存）、w3qb02/03: B** |

Wave 3 諮問 1 では Wave 1 / 2 の純粋な B 系収束パターンが **崩れて** A 系（哲学者の C と接近採決、confidence 0.55）に収束した。これは第 8 条本格諮問の特殊性（philosophy 改訂は不可逆度高、3 段階先行 + 4 段階拡張を minority opinion 温存）の反映で、Wave 4 / 5 で minority opinion 再評価機構の実証機会となる。

## 5. Wave 3 末申し送り素材（暫定枠）

Wave 3 完遂時点で Wave 4 に申し送るべき項目の予定:

1. minority opinions 5 件のうち Wave 3 で再評価できなかった分
2. 議題 2 残候補のうち Wave 3 で採用に至らなかった event 群
3. Wave 1 ECC-SURVEY 6 ヶ月再観察（2026-11-11 予約）
4. philosophy 第 8 条運用初期データ（CTL 連動の実観測）
5. 候補 9 以降の素材調査結果（Wave 3 中に追加候補が発見された場合）

詳細は Wave 3 末振り返り儀式（`templates/rituals/wave-end-retrospective.template.md` ベース、候補 8 採用時）で集約。

## 6. 哲学的注記

Wave 3 は咀嚼プロトコルの **第 2 段階完成期**:
- Wave 1: 枠組み確立（観察 + 候補抽出）
- Wave 2: 候補実装（HV + skill + 規約）
- **Wave 3: 哲学言語化**（B 系収束 2 サンプルを第 8 条として明文化）

これにより、咀嚼プロトコル §3 「翻訳」の T3 + ガードレール語彙化が **DH 哲学の正式条文** となり、後続 Wave での候補取り込み時に「第 8 条準拠」が判断基盤として常時参照可能になる。

議題 2 残候補と候補 7/8 は本 Wave の哲学言語化を補完する位置づけで、本質的な重心は agenda 1 (第 8 条本格諮問) にある。

`category: conception` 適用（哲学者 5 / 経営者 3 / 開発者 3）は council-weights.md 既存規約準拠の素直な選択で、新規 / 構想カテゴリの判断では既に哲学者重みが優位な配分になる。これは「philosophy 改訂は慎重に、撤回困難な変更は最小限に」という DH 設計原則と council-weights 設計の整合反映。
