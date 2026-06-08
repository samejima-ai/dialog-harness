# 情報代謝 regime 定義（正本）

3 層保持 regime（HOT / WARM / COLD）と二軸フラクタルの**定義の正本**。
決定3（境界規約の正本化先・P4 承認済 / Council mtbl01 批准）に従い、framework 定義は本ファイル（SK references / D4）に置き、
project 固有パラメータ（閾値の値・tier 別パス・リズム間隔等）は利用者プロジェクトの REGIME.md `## 情報代謝設定` に置く。
SPEC.md は本定義への**ポインタ 1 行のみ**を持つ（実体を持たない＝SPEC 肥大回避＝購読量保護）。

> 一度書けば全 DH プロジェクトが継承する framework 叡智。SKILL.md 本体（常時ロード側）からは薄いポインタで参照し、
> 本ファイルは必要時のみロードする（progressive disclosure ＝購読量保護）。
>
> **上位の理論層**（なぜこの regime なのか・圧縮 ≠ 結晶化・二種の結晶・5 相循環）は仮結晶 `context-circulation-theory.md`。
> 本ファイルはその**実装拘束部分**（確定分のみ）。理論の §10 未決事項は実装仕様ではない。

---

## 0. 最上位不変条件: AI 購読量の上限（北極星）

すべての tier 設計・プロトコルは、この一本の評価関数に従属する。

- **最小化対象**: AI が毎サイクル**既定でロードする購読量**（そのタスクで実際に読み込む context 量）
- **非対象**: repo / COLD のディスクサイズ（無制限に太ってよい）
- **目的**: 購読量と history 蓄積量の**線形連動を断つ**。現状の病理は episodic が約 925 行/cycle で単調増加し、購読量がそれに連動して膨張すること（代謝天井）
- **帰結**: 結晶化は**密度↑であって量↑ではない**。HOT が budget を超えたらそれ自体が再圧縮の発火条件になる
- **自己適用**: 代謝処理（reindex）自身が購読量を侵さない（増分のみ読む・全 rescan 禁止・冪等）

---

## 1. 二軸フラクタル

情報代謝は 2 つの直交軸でフラクタルに反復する（philosophy 第1条の深掘り）。

### 軸A: 還元先軸（DH 本体 D4 ⇄ 固有プロジェクト D1-D3）

流入する history は「**何に還元されるか**」で二分される。

| 還元型 | 例 | 結晶化先の叡智 |
|---|---|---|
| **DH 還元型** | 「早すぎる結晶化は偽 convention を固定する」等、特定 project を超えて framework に効く学習 | DH 本体叡智（philosophy / skill references / RL / 罠） |
| **project 還元型** | 「このアプリのカート上限は 30」等、その project に閉じた事実 | project 叡智（SPEC / DOMAINS / DONT / INTENT） |

**咀嚼吸収の切り替えルール**:
- DH メタスキル開発中（dialog-harness repo 内での開発）→ DH 還元型を食べる
- 固有プロジェクト開発中 → project 還元型を食べる

reindex は episodic を還元先で**仕分け**し、正しい叡智層へ振り分ける。HOT/WARM/COLD の 3 層に、この還元先軸が直交する（「どちらの層の HOT か」）。

### 軸B: 時間軸（短い操作ループ ⇄ 長い履歴結晶化）

同一の純度回復（期待⇔現実の擦り合わせ）を 2 つの時間スケールで反復する。
- 短時間軸: clean-state-per-attempt（汚れた状態での再試行が相関失敗を生む問題の回避）
- 長時間軸: 本 regime の履歴結晶化

両者は同じ P1 フラクタルの粒度違い。将来、共通の排出機構として統合する余地がある（未決・別セッション）。

---

## 2. 3 層保持（HOT / WARM / COLD）

| Tier | 中身 | 既定ロード | 形態 | 購読量への寄与 |
|---|---|---|---|---|
| **HOT（結晶層）** | conventions・罠・invariants・確定 domain・判断の先取り | 常時（ただし progressive disclosure で関連分のみ） | 密な RL/SK | **乗る**（だから budget 管理対象） |
| **WARM（圧縮層）** | 生きた設計根拠・直近 INTENT・未消化 delta | 関連時のみ | 要約圧縮 | 関連時のみ乗る |
| **COLD（アーカイブ層）** | 抜け殻の生ログ・一回性詳細・創造性シード | しない（retrievable） | 生 + 逆引きポインタ | **乗らない**（だからディスクは無制限 OK） |

### 昇降格（流れは一方向: episodic → wisdom enrich → cold archive）

| 遷移 | 条件 | ゲート |
|---|---|---|
| WARM → HOT | 反復パターンが結晶化に値する（叡智化） | **Council 判定（§5-1）** |
| WARM → COLD | 陳腐化（栄養を抜かれた抜け殻） | 結晶化完了の確認 |
| HOT → （再圧縮） | HOT が購読量 budget 超過 | 罠の統合・陳腐 HOT/WARM の COLD 降格 |

**禁止**: COLD → HOT/WARM の常時昇格（COLD は retrievable だが既定ロードに戻さない。必要時に明示 retrieve のみ）。

---

## 3. 摂取選択基準（何を食べるか・Council 哲学者 minority 由来）

「吸収」「排泄」の前に、**そもそも何を口に入れるか／何が結晶化に値するか**の判定基準。
結晶化主体が AI である以上、AI の現在のバイアスが未来の正本を汚染し、「重要でない」と判断された声が永久に COLD に沈むリスクがある。これを構造で抑える。

1. **反復性**: 同一パターンが閾値回（REGIME.md `metabolism.council_gate.repetition_threshold`）反復した episodic を結晶化候補にする。単発は候補にしない（早すぎる結晶化の防止）
2. **還元先の明確さ**: 還元先（DH / project）が判定できる episodic のみ吸収する。判定不能なものは WARM に留置（捨てない）
3. **可監査性**: 結晶化候補は「要再確認リスト」（SUMMARY.md）に列挙し、人間が摂取選択そのものを監査できるようにする。`**確度**: AI推定` メタデータを付す
4. **非対称成長の許容**: 現実の組織知は自己相似に整わず非対称に成長する。フラクタルの美しさを「設計が完成した」錯覚の根拠にしない。摂取漏れは次サイクルで拾えるよう WARM を温存する
5. **沈黙した声の救済**: AI が「重要でない」と判断した episodic も COLD で retrievable に保ち、逆引きポインタで救済可能にする（§5-2, §5-3）

---

## 4. 結晶化／排出プロトコル

### 結晶化（構築代謝）

| 反復の性質 | 結晶化先 |
|---|---|
| 成功の反復 | RL / convention（HOT） |
| 失敗の反復 | DONT（罠）（HOT） |
| 設計根拠・意図 | INTENT / DOMAINS / invariants |

- 出力は**生ログより密で判断を先取りした**形であること（密度↑≠量↑）。これを満たさない結晶化は無効
- HOT 昇格は Council ゲート（§5-1）を通す

### 排出（分解代謝）

- 対象は**結晶化完了済みの抜け殻のみ**（順序: 吸収→排泄）
- COLD へ移送し、**逆引き source pointer** を結晶側に付す（疑義が出たら生ログまで遡れる）
- **delete しない**（§5-2）。retrievable + 創造性シードとして保持
- 「自層が吸収しなかった他層の食料」は排泄対象に含めない（排泄判定は結晶化完了で決まる）

---

## 5. 不変条件（5 つ・lossy 圧縮を毒にしないための憲法）

1. **早すぎる結晶化＝偽 convention の固定化を防ぐ**。HOT 昇格は **Council 判定をゲート**にする（自動カウンタで上げない）。DH 既存の「同一 override が 3 機能タイプ以上で反復 → Council 諮問」を一般化して流用。**定量基準**（参照頻度 < N 回/期間・経過日数閾値・反復回数閾値）は REGIME.md `## 情報代謝設定` に project 固有値として置く（Council 指摘 #1）
2. **COLD ＝ archive ≠ delete**。「可逆性・監査可能性への投資」を破壊しない。作業集合から外す（retrievable）のであって消さない
3. **叡智に source pointer**。結晶化した罠/RL は元の COLD episodic への逆引きポインタを持つ。形式は `reindex-protocol.md` §逆引きポインタ
4. **代謝自体のコストを抑える**。reindex を毎 cycle 全行にかけない。リズムは sparse + 冪等（増分のみ読む・全 rescan 禁止）
5. **独自補完しない**。reindex は「そこにある生ログの蒸留」であって、無い叡智の捏造ではない（TBD を埋めない）
6. **結晶化は COLD lossless 原本から読む（不変条件 A）**。WARM の lossy 要約層からは結晶化しない——lossy-on-lossy 汚染（意味的に欠けた要約から正典を著述する）を防ぐ。要約は参照の入口、結晶化の素材は原本
7. **「情報欠損なし」は HOT の誤った目標（不変条件 B）**。lossless は COLD 監査層に隔離する責務であって、HOT の目標ではない。HOT は forgetting is a feature で**意図的に lossy**（判断に効く結晶だけ残す）。捨てるから速い
8. **パターン結晶は反-発火条件を必須化**。形式に「いつ適用**しない**か」を含める。反例（falsification）が偽類推（表層一致での誤発火）の唯一の防壁。誤パターンは fuzzy に誤発火し debug 困難ゆえ、HOT 昇格証拠は規則結晶より高くする。**【caveat】本条はパターン結晶の形式が確定（context-circulation-theory §10 未決）してから発効する。形式未確定の現時点では「方針」であって運用必須条件ではない**

> 不変条件 #6–#8 の理論的根拠と二種の結晶（規則結晶 / パターン結晶）・圧縮 ≠ 結晶化の詳細は、上位の仮結晶理論 `context-circulation-theory.md` を参照（§5・§6・§8）。

---

## 6. 哲学的接地（DH 整合）

| 柱 / 概念 | 接地 |
|---|---|
| P1 フラクタル | 純度回復を時間軸（軸B）と還元先軸（軸A）で反復 |
| P2 Shift Left | episodic 肥大を早期に圧縮し上層負荷を未然に下げる |
| P3 情報純度 | 抜け殻ノイズを HOT から排除し信号対雑音比を回復 |
| 情報代謝サイクル | 摂取・処理に欠けていた構築代謝（結晶化）＋分解代謝（排出）を補完。代謝の完成 |
| forgetting is a feature | 組織は episodic を忘れる（archive）ことで速くなる。忘却は選択的（episodic を忘れ結晶を残す） |
| 検証後評価原則 | 結晶化は cycle 境界で実行（開発中の割り込み禁止と整合） |

**「保持したまま速く」の因果**: 速くなる＝密度↑＋意思決定の先取り＋純度↑。context が保持される＝再利用可能な project 特化 context は叡智層（罠/SPEC/INTENT）に住み、抜け殻は COLD に retrievable。捨てても判断に効く context は失われない。

---

## 7. E2E episodic ソースの tier 対応（v5.24.0 追加）

E2E テストの実行結果・履歴は、**専用サイクルを新設せず本 regime の新しい episodic ソース**として流す
（構造同形の維持・重複機構の回避）。構築側の正本は
`../../layer1-autonomous-dev/references/e2e-best-practices.md` §9「E2E 情報代謝サイクル」、
project history への置き場は `../../layer0-spec-architect/references/history-layer-spec.md` §E2E-LOG.md。

### 還元先（軸A）: 既定 project（D1-D3）

E2E が生む大半（run 履歴・flaky パターン・artifact）は「**このアプリのこの画面**」に閉じた事実＝
**project 還元**。一部「AI 駆動 E2E 一般で flaky はこう出やすい」等は DH 還元（D4）になりうるが**既定は project**。
∴ E2E 代謝の正本は利用者プロジェクトの REGIME.md `## 情報代謝設定`（Council mtbl01 で確立した
「DH 使用プロジェクト開始以降は project のための代謝機構」原則と一致）。
**DH 本体（dialog-harness repo）は対面アプリを持たないため E2E 代謝を稼働しない**（定義のみ・dog-food 対象外。
一般代謝は dog-food するが E2E はしない）。

### tier 対応（二相分離が COLD/HOT に直結）

| Tier | E2E の中身 | 居場所（project ローカル） | 購読量 |
|---|---|---|---|
| **COLD** | 相 A artifact（Trace/動画/network/console）・生 run ログ詳細 | `history/archive/YYYY-MM/e2e/`（生成時はランタイム出力 dir = ephemeral、cycle 境界で COLD 保持） | 乗らない（retrievable・disk 無制限 OK） |
| **WARM** | run 要約列（pass/fail・flaky・duration・provenance） | `history/E2E-LOG.md`（append-only・cursor 追跡） | 関連時のみ（reindex が増分読み） |
| **HOT** | flaky 罠（反-発火条件付）・安定 journey RL・provenance 観測規律・B-ID/C5 oracle 結晶 | PATTERNS.md / DONT / SPEC / INTENT / SUMMARY | 常時（密度↑≠量↑） |

> 北極星の急所: E2E は毎 CI 実行で大量データを生むが、**artifact は COLD 直行で絶対に既定ロードしない**。
> 蒸留された flaky 罠だけが HOT に乗る。履歴が無限に貯まっても購読量は膨らまない（量↑でなく密度↑）。
> v5.23.0 の二相分離（相 A in-loop 知覚器 / 相 B 耐久資産）が、そのまま COLD / HOT に対応する。

### 8 不変条件の E2E 具体化

- **#1 早すぎる結晶化防止**: 単発 flaky を罠にしない。`council_gate.repetition_threshold` 回反復＋
  `min_age_days` 経過＋Council ゲートを通って初めて HOT 罠化（偶発的 flaky の固定化を防ぐ）
- **#2 COLD=archive≠delete**: artifact・生 run ログは消さず retrievable（後から原因究明・再現に使う）
- **#3 source pointer**: flaky 罠は元の生 run ログ（`cold://.../e2e/...`）へ逆引きポインタを持つ
- **#6 COLD 原本から結晶化**: 罠は生 run ログ（COLD lossless）から蒸留する。E2E-LOG の lossy 要約からは結晶化しない
- **#8 反-発火条件必須**: flaky 罠は「いつ**適用しない**か」を必須化（例: この不安定は特定 viewport/低速 CI 限定、
  他環境では誤発火させない）。表層一致での誤発火が debug 困難な flaky では特に重要

