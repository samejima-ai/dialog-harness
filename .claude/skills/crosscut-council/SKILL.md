---
name: crosscut-council
dimension: D4
description: >
  横断判定機構（crosscut prefix）。Layer 0/1/2 のいずれにも属さず、全 Layer から献上を受けて判定を返す。
  人間 ≒ Council 原則（philosophy.md 第6条）の実装主体。
  実装中に発生する判断点で AI 自身が発動する**多軸観測 ＋ 優先度バランス評定機構（Council / 合議）の sub-skill**。
  3 軸の並列独立観測と、軸ごとに宣言された優先度による**バランス評定**で、トレードオフ判断・結論対立・
  不可逆操作・SPEC 矛盾・複数実装案の拮抗に対する判断支援を提供する。
  **本機構は多数決でも投票でもない**（§重みの意味論）。重みは議決権数ではなく
  「その軸の主張を単独で通すために要する強度の閾値」であり、高重み軸の単独主張は
  低重み 2 軸の合意に敗れうる。
  L1（autonomous-dev）/ L2（orchestrator/integration-verifier）/ L0（仕様策定中）から
  横断的に呼ばれる。
  **ユーザーが対話段階で「迷っている」と発話するケース自体は起動条件に含めない** —
  それは spec-architect の対話で吸収する。
  起動対象は **L1/L2 実行中に生じる実装上の判断点** に限る：
  (a) AI 側の内部判断状態（「複数の実装案で拮抗している」「どちらを採るべきか実装判断が必要」
  「trade-off がある」「confidence < 0.6」等）、または
  (b) 実装指示・タスク記述内の文言（「Council に諮る」「合議」「重み付き判定」「止揚」「複数案が拮抗」等）。
  出力は判断（judgment）であって決定（decision）ではなく、実装者は合意プロセスで方針化する。
  final_decision は常に null で返し、人間または実装者の合意プロセスが埋める。
  タイポ修正・フォーマット調整・明確仕様の素直実装・リファクタ定型処理では起動しない。
  PR1 スコープ: business Council（経営者/開発者/哲学者）固定、Phase 1 のみ、単一段のバランス評定。
---

# Council System (多軸観測 ＋ 優先度バランス評定機構)

実装中に発生する判断要請を受理し、3 軸の独立観測を優先度バランスで評定して単一の推奨を導く sub-skill。
Dialog Harness 本体から**独立**した構造で設計され、将来切り出し可能。

## 重みの意味論（v6.5.0 で明文化・最初に読むこと）

**「Council」「合議」の名称は保持する。ただしその語が含意する多数決・投票は本機構の実体ではない。**

命名は合議制・多数決・投票の含意から出発したが、実装された機構は別物であり、
実測（`history/COUNCIL-LOG.md` の `simple_conflict` 17 件）はその別物のほうが機能していることを示した。
本節はその実体を定義として確定する。

| 誤読 | 実体 |
|---|---|
| 重み = 議決権数。重い軸が勝つ | 重み = **その軸の主張を単独で通すために要する強度の閾値**。`weighted_score` は stance ごとの**合算**なので、重み 5 の単独軸は重み 3+3 の合意に敗れる |
| 判定 = 選択肢の取捨選択（投票） | 判定 = **軸ごとに宣言された優先度によるトレードオフのバランス評定**。捨てるのではなく釣り合わせる |
| 全会一致 = 合意が取れた | 全会一致 = 多様性（プルラリティ）の質評価（`council-philosophy.md` 第2条）。**被覆不足の可能性も同時に疑う** |
| 高重み軸が options 外に出たら少数意見として保存 | それは「**選択では吸収できない**」というシグナル。`judgment_confidence` を押し下げ、判定を降りて人間に渡す経路が正しい挙動 |

### 実測による裏づけ（2026-07-26、`simple_conflict` 17 件）

- 最大重み軸の stance が `recommended` になったのは **6/17**。11 件で最重量軸が負けている
  → 「重い軸が勝つ機構」ではない。
- `judgment_confidence < 0.5`（判定を降りた）4 件は**全件が「第3の道／止揚」を含む**。
  第3の道を含まない 9 件では 0 件（jc 平均 0.750 vs 0.565）
  → 高優先度軸が options 外に出たことを機構が検知して献上している。
- 以上より、重みは「勝たせる装置」ではなく「**取り落とせない主張を明示する装置**」である。

### 帰結（実装上の禁止事項）

- **重みを「多数派の形成」として説明してはならない**（Persona prompt・ログの `weight_note`・
  人間可読 markdown のいずれにおいても）。
- **`recommended` を「勝った案」と記述してはならない**。骨格として選ばれた案であり、
  敗れた軸の主張は `minority_opinion` と（統合した場合は）本文に吸収されている。
- `judgment_confidence` は「推奨の正しさへの自信」ではなく
  **「バランス評定が単一の推奨に収束した度合い」**である（§judgment_confidence の帯）。

## 原則

- **Council 内部は非フラクタル**: 起点・分岐点としての決断機構であり、フラクタル原則の**内部的例外**。トリガー構造（Council を呼ぶ側）は `philosophy.md` §1 のフラクタル原則に従う（A⇄B の擦り合せループが全階層で反復）
- **Orchestrator はフラット**: 情報を流し応答を集約するのみ。判断機能を持たない。重みの適用は決定論的計算
- **判断 ≠ 決定**: Judgment Agent の出力は Council の最終判断。**決定は実装者の合意プロセスを経て成立**する
- **final_decision は常に null**: Council は決して決定を埋めない。実装者が合意プロセスで方針化するか、人間に献上する
- **対立は構造化する**: 対立は合意のために討論する価値がある差異。解消は目的ではない、見える化が目的
- **重みは議決権ではない**: 重みは「単独通過に要する強度の閾値」であり、多数派形成の道具ではない（§重みの意味論）
- **少数意見を必ず保持**: Judgment Agent 出力の `minority_opinion` フィールドで保持
- **実装者の裁量を尊重**: 優秀な実装者である前提で設計する。過度に縛らない
- **情報純度**: Persona は独立に意見生成する（Phase 1 では他 Persona 出力を参照しない）

## 発動基準

### 自動発動すべき場面

- SPEC.md / DONT.md との矛盾検出時
- 複数の実装案が拮抗している（≥ 2 案が viable）
- 不可逆操作（削除・マイグレーション・データ破壊）の直前
- 実装者自身が confidence < 0.6 と自己評価した時

### 実装者の裁量で進める場面（Council 発動しない）

- タイポ修正、フォーマット調整
- 選択肢のない単一パス実装
- 明確な仕様に基づく素直な実装
- リファクタリングの定型処理
- 実装者が自信を持って判断できる技術的選択

### 確認を挟む場面

- 設計の曖昧さ、性能のトレードオフ

### 実装者の confidence 評価指標

実装者は以下のいずれかに該当した時、自身の confidence を低いと判定する：

- (a) 2案以上の実装パスが viable（択一できない）
- (b) SPEC/DONT の記述に曖昧さを検出
- (c) 不可逆操作を行う直前
- (d) 自己評価 confidence < 0.6（明示的に自問して採点）

### 自己申告プロトコル（v5.5.0 adrv01-Ph1 で明文化）

実装者の自己 confidence < 0.6 自己評価は **Council 起動の正式トリガー**である。「自己評価しただけ」「自分で考えてみる」等で内部完結させてはならず、該当条件を検出した時点で本 skill を起動する義務を負う。

**自己申告 → Council 起動の正式経路**:

```
実装者が (a)〜(d) のいずれかを検出
  ↓
self-report をログ化（DELIVERY.md / 実装メモ等に invocation_id 採番前の素材を記録）
  ↓
本 skill 起動（context + options + question_to_answer + source_skill + category）
  → category 選択は references/pre-check.md L70-78 を参照（迷ったら judgment にフォールバック）
  ↓
[Phase 0〜3 + 合意プロセス]
```

**self-report の最低限フィールド**:

- `self_reported_confidence`: 0.0〜1.0（実装者の自己評価値）
- `trigger`: (a) / (b) / (c) / (d) のいずれか
- `reason`: なぜ confidence が低いと判断したか（1〜2 文）

これらは Council 起動時の `context` に含めて受け渡す（PR1 では構造化フィールドではなく自然文として埋め込む。PR2 で `output-format.md` の発動要請スキーマに正式追加候補）。

**Council 起動を内部完結で代替してはならない理由**:

実装者の自己 confidence は内側からしか見えない（self-感知の特性）が、判断の正当性は外側からの観測で補強する必要がある（philosophy.md §3 情報純度・§5 献上哲学）。Council は「自己申告 = 一次入力 + 重み付き判定 = 二次検証」の二相構造で、自己申告だけでは情報純度が確保されない。adrv01-Ph2（v5.6.0 候補）で予告される独立観測機構（harness-verifier 同型）はこの構造のメタ層検証として位置づけられる。

**スコープ**:

本プロトコルは layer1-autonomous-dev / layer1-independent-reviewer / layer0-spec-architect / layer0-archeo-architect から起動される全 Council 呼び出しに適用される。crosscut-issue-implementer 等の crosscut-* skill からの起動も同形（v5.6.0 Ph2 で hook 経路を本実装）。

## 処理フロー（PR1: Phase 0 + 1 + 3、Phase 2 のみスキップ）

```
[入力] 発動要請 (context + options + question_to_answer + source_skill)
  ↓
[Phase 0] Pre-Check: Council 種別判定
  → PR1 は business 固定（詳細: references/pre-check.md）
  ↓
[重み計算] base_weights × ethos_multiplier + situational_modifier
  → Orchestrator が決定論で計算（詳細: references/orchestrator.md）
  ↓
[Phase 1] 3 Persona 独立並列発言
  → 経営者(temp 0.3) / 開発者(temp 0.2) / 哲学者(temp 0.7)
  → 他 Persona の出力を参照しない（情報純度）
  → **実装契約**: 3 つの独立した `messages.create` API call で生成、context 共有禁止
  → それぞれに「他ペルソナ出力を含まない context + system prompt」のみ渡す
  → 各 Persona は references/personas/business/*.md の system prompt に従う
  ↓
[対立度判定] 3値: 次元分離の同一結論 / 全会一致 / 単純対立（v6.7.0 で類型 B を分離）
  → 完全な類型 A-G 判定は PR2 で実装（references/conflict-typology.md 参照）
  ↓
[Phase 2] PR1 ではスキップ（PR2 で追加）
  ↓
[Phase 3] Judgment Agent による重み付き単一回答の導出
  → temperature 0.1、人格なし（references/judgment-agent.md）
  → 次元分離の同一結論（reason_divergence）は多様性として質を評価
  → 次元も重複した全会一致（unanimous）は被覆不足を疑い confidence を引き下げる
  ↓
[出力] JSON（final_decision は常に null）
  ↓
[ログ] history/COUNCIL-LOG.md に追記（project-scope）
  → decision_category（C1〜C4 / H1〜H4）を**必ず含める**（Phase 0 で判定済み・§CTL 記録）
  ↓
[CTL記録] 同期コマンドを実行（user-scope, **自動・毎回必須**・下記 §クロージング手順）
  → 事後評価（actual_outcome）は後段の合意プロセス完了時／振り返り儀式で埋める
  ↓
[合意プロセス] 実装者が理解→質問→方針決定（references/consensus-protocol.md）
```

### クロージング手順（CTL 自動同期・毎回必須）

**COUNCIL-LOG への追記を終えたら、同じターン内で必ず以下を実行する**。これが CTL 記録の主経路
（§CTL 記録 §同期の発火主体）。実行を次ターンや儀式まで先送りしない — 先送りが v6.1.0 以前の
「手順書依存で空文化」を再演させる。

```bash
# 発動したプロジェクトの COUNCIL-LOG を同期する（自プロジェクトのみ・--prune は付けない）
python3 scripts/council-log-sync.py sync --recompute
```

- **`scripts/` が無い利用者プロジェクトの場合**: DH 本体の clone から
  `python3 <DH>/scripts/council-log-sync.py sync --recompute --log ./history/COUNCIL-LOG.md`
  を実行する。それも不可なら §CTL 記録 2. の「invocation JSON 直接書き」でフォールバックする。
- **`--prune` は付けない**（他プロジェクトの invocation を巻き添えで消す。§CTL 記録の警告参照）。
- **失敗しても Council フローは止めない**（判断 ＞ 記録）。warn として可視化し、次回の同期または
  L0 振り返り儀式で回収する。同期は冪等ゆえ再実行は無害。
- 実行後、`python3 scripts/council-ctl.py status` で CTL と未評価件数を確認できる（任意）。

## 入出力規格

入出力の JSON schema は [references/output-format.md](references/output-format.md) を参照。
要点のみ：

- **Persona 出力**: `persona / stance / reason / confidence / dimension / premise / concerns`
- **Judgment Agent 出力**: `recommended / reasoning / minority_opinion / weight_note / judgment_confidence / final_decision`
- `final_decision` は常に `null` を返す（合意プロセス前の判断であるため）
- `judgment_confidence < 0.5` の場合は自動的に人間エスカレーション

## Council 種別

| 種別 | 構成 | 用途 | PR1 |
|------|------|------|-----|
| business | 経営者 / 開発者 / 哲学者 | 事業・実装・AI自律駆動開発の判断 | ✅ |
| life | 男 / 父 / 開発者 | 人生トレードオフ（L0 専用） | PR3 |
| hybrid | business + life 並列 | 例外処理（常用しない） | PR3 |

PR1 では business Council に固定。Pre-Check も business を即返す簡略実装。

## 合意プロセス

Judgment Agent 出力を受け取った実装者は [references/consensus-protocol.md](references/consensus-protocol.md) に従って合意する：

```
Judgment Agent 出力（Council の判断）
    ↓ 実装者が理解
    ↓ 実装者が質問（必要なら Council に追加質問、最大2往復）
    ↓ 方針決定 = 合意成立
    ↓ 実装に反映
```

**合意できない場合**: 実装者は Council の判断を保留にして人間に献上する。Council 判断を無視して独自実装することは `philosophy.md` §5 献上哲学に反する。

## ログ要件

発動のたびに `history/COUNCIL-LOG.md` に1エントリ追記する。フィールド：

- 発動日時（ISO 8601）
- 発動元スキル（layer1-autonomous-dev 等）
- question_to_answer
- Council種別
- Phase到達（PR1 は常に `1→3`）
- conflict_type（`unanimous` / `reason_divergence` / `simple_conflict`）
- final_weights（適用された重み配分）
- judgment_confidence
- implementer_consent（後追記、合意プロセス完了時）
- human_escalated（bool）

**記録は必ず `- invocation_id: "..."` ブロック形式（[references/output-format.md](references/output-format.md) §8）で書く**
（2026-07-20 明文化）。見出し形式（`## council-...`）や自由 Markdown での記録は
`council-log-sync.py` のパーサが読めず**CTL に一切算入されない**（利用者プロジェクトで
発動 6 件が見出し形式で記録され全件 CTL から脱落した実害あり）。軽量発動は §8 の
「CTL 最小必須セット」だけで記録してよい。詳細な議論の自由記述は別ファイル
（triage doc / delivery 等）へ分離する。

COUNCIL-LOG は append-only。編集不可。振り返り儀式（F1-F3、PR3 で連携）で監査する。

### CTL 記録（user-scope, COUNCIL-LOG から同期）

CTL（Council Trust Level）の蓄積データ `~/.claude/council-data/invocations/` は、
**`history/COUNCIL-LOG.md`（project-scope, append-only）を単一情報源として同期で導出する**
（スキーマ・命名は [references/ctl-calculation.md](references/ctl-calculation.md) §4 が一次情報源）。

**なぜ同期経路か（v6.1.0 で再設計、Council 諮問 `council-2026-07-01T-ctlrec1`）**:
かつては「発動のたびに手で `record` を叩く」手順書依存だったが、それを強制する実行主体が
無く空文化した（発動 53 回に対し CTL 記録は 1 件）。COUNCIL-LOG には**全発動が確実に追記される**
（本 SKILL §ログ要件）ので、これを唯一のソースとし、`scripts/council-log-sync.py` が
council-data を導出する。これで「書く側の経路」の二重化を解消する。詳細は
`dh-upgrades/upgrade-spec-v6.1.0.md`。

```bash
python3 scripts/council-log-sync.py sync --recompute           # 同期 + CTL 再計算（主経路）
python3 scripts/council-log-sync.py sync --dry-run             # 生成予定を確認（書かない）
```

> **`--prune` を主経路に置かない**（2026-07-20 改訂）: `--prune` は「引数のログに対応しない
> invocation」を全件削除する。council-data は **user-scope でプロジェクト横断**（philosophy 第 6 条）
> ゆえ、あるプロジェクトのログで同期すると**他プロジェクト由来の invocation が全件孤児判定される**。
> 実測では DH 本体のログで同期して platform 由来 43 件が、逆で DH 由来 57 件が孤児として列挙された。
> `--prune` は「同一ログ内の別採番手動 record を掃除する」目的でのみ、**削除対象 id を目視確認した上で**
> 使う。孤児警告が出ても、他プロジェクトを併用しているなら**それは正常**であり掃除してはならない。

**同期の発火主体（実行経路への接続 — 手順書依存に戻さない）**:
同期は「スクリプトを作っただけ」では①と同じ轍を踏む。以下 2 つを主経路とする：

- **【主】Council 発動のたび、本 SKILL の最終ステップで同期する**（§9 クロージング手順）。
  COUNCIL-LOG への追記直後に実行するため、**発動と記録の間に時間差が生じない**。
  「発動 → COUNCIL-LOG 追記 → 同期」を 1 つの不可分な手順として扱う。
- **【従】L0 振り返り儀式（F1/F2/F3）の冒頭でも同期を走らせる**
  （`layer0-spec-architect/references/ritual-protocol.md` §CTL 事後評価）。
  儀式は「同期 → `pending` 列挙 → 未評価判定を人間に問う」を 1 手順として固定する。
  主経路が失敗・省略された場合の**取りこぼし回収**として機能する（同期は冪等ゆえ二重実行は無害）。

CC hooks は tool 単位発火で「Council 発動」という抽象イベントに口が無いため、**hook 発火は採らない**
（`upgrade-spec-v6.1.0.md` §2.1 案B 却下理由）。上記【主】は hook ではなく**skill 自身の手順**として
実装するため、この却下理由の射程外である（skill は自分の発動を知っている）。

**decision_category は同期で機械導出しない**: COUNCIL-LOG に明示された C1〜C4 / H1〜H4 が
あればそれを使い、無ければ `null` で載せる。重み配分軸の `category`（conception/judgment 等）
から `decision_category`（委譲軸）へ写像してはならない（両者は
[references/consensus-protocol.md](references/consensus-protocol.md) §category と decision_category の役割分担
で直交と明記。写像は非全射で、埋めると「満ちているが意味は空」な統計になり CTL 算出が偽の確信を生む）。
`null` の invocation は `_compute_stats` の null-skip で統計から除外される。よって**将来分は
Phase 0（発動時）で `decision_category` を必須記録する**（[references/pre-check.md](references/pre-check.md) §decision_category 必須ゲート）。

**記録失敗時の規範（判断 ＞ 記録）**: Council の一次成果物は judgment であり、CTL 記録は従属物。
COUNCIL-LOG への追記（本 SKILL §ログ要件）さえ済んでいれば、同期はいつでも後追いできる。
同期・record が失敗しても **Council フロー（出力・合意プロセス）は止めない**。失敗は **warn として
可視化**し（黙殺しない）、後日 `sync --recompute` で復元する。記録失敗を理由に判断を握り潰すのは
献上哲学（philosophy.md §5）に反する。

**個別 record は「COUNCIL-LOG 即時追記トリガ」であって第二の記録ストアではない**
（v6.1.0 案A / Council `council-2026-07-01T-ctldedup`）:

「単一情報源は COUNCIL-LOG」と宣言しながら手動 record を独立ストアとして温存すると、
同一発動が二重計上され CTL 統計を歪める（v6.1.0 が葬った二重書き経路の再来）。よって
**手動 record を使う時は必ず COUNCIL-LOG にも同じ発動を追記する**。追記すれば次の同期で
正規版（COUNCIL-LOG 由来の invocation_id）に一本化される。COUNCIL-LOG に追記しない手動
record は「孤児」として `council-log-sync sync --prune` の掃除対象になる（残すと二重計上源）。

1. `scripts/council-ctl.py` が存在すれば、同期を待たず 1 件だけ即記録できる。
   **ただし同時に COUNCIL-LOG へ追記すること**（§ログ要件。追記なしは二重計上源）:

   ```bash
   python3 scripts/council-ctl.py record \
     --decision-category <C1|C2|C3|C4> \
     --category <operation|judgment|conception 等> \
     --topic "<question_to_answer の抽象要約・80字以内>" \
     --judgment "<recommended の抽象表現>" \
     --confidence <judgment_confidence> \
     --consensus <consensus_mode>
   # → この発動を history/COUNCIL-LOG.md にも必ず追記する（同期で正規版へ一本化される）
   ```

   **`init` は不要**: `record` は未初期化（`~/.claude/council-data/` 不在）でも
   自動で CTL-0 コールドスタート初期化してから記録する（ctl-calculation.md §1/§8）。

2. `scripts/council-ctl.py` が無い（DH skill のみ取り込んだ利用者プロジェクト等）場合は、
   下記スキーマの invocation JSON を `~/.claude/council-data/invocations/` に直接書く
   （この経路だけで self-contained に記録できるよう全フィールドを以下に明示する。
   一次情報源は `ctl-calculation.md` §4）。ディレクトリが無ければ先に作る。

   - **ファイル名**: `<ISO8601Z のコロンをハイフン化>-<invocation_id 末尾6文字>.json`
   - **中身**（`actual_outcome.status` は `null` で作成）:

     ```json
     {
       "invocation_id": "council-<ISO8601Z>-<6hex>",
       "council_type": "business",
       "category": "<operation|judgment|conception 等>",
       "decision_category": "<C1|C2|C3|C4>",
       "topic_summary": "<抽象要約・80字以内>",
       "judgment": "<recommended の抽象表現>",
       "judgment_confidence": 0.85,
       "consensus_mode": "<auto_agree|escalate_to_human 等>",
       "ctl_at_invocation": "<記録時点の CTL>",
       "actual_outcome": {"status": null, "evaluated_at": null, "modifier_note": null}
     }
     ```

   必須フィールドが欠けたり `decision_category` が C1〜C4 以外だと、後段の `_recompute`/
   振り返り儀式で **warn skip され統計から静かに落ちる**（CTL が実態より低く出る）。
   直接書き経路を採るときはこのスキーマ厳守が CTL の正確性の前提になる。

**フィールド対応**:

| council-data | 供給元 |
|---|---|
| `decision_category` | Phase 0 / consensus-protocol の decision_category 判定（C1〜C4） |
| `category` | 重み配分用カテゴリ（operation/judgment/conception 等） |
| `topic_summary` | question_to_answer の**抽象要約**（固有名・コード断片・人物名を入れない） |
| `judgment` | recommended の抽象表現 |
| `judgment_confidence` | Judgment Agent 出力 |
| `consensus_mode` | auto_agree / escalate_to_human 等 |
| `ctl_at_invocation` | 記録時点の CTL |

**H カテゴリは記録しない**（CTL に関係なく常時人間献上のため。ctl-calculation.md §2）。

**事後評価（actual_outcome）は record とは分離する**: 記録は発動と同時に自動で行うが、
`actual_outcome`（agreed/modified/rejected）は合意プロセス完了時または振り返り儀式（F1-F3）で
埋める。事後評価は「Council の判断が正しかったか」の**証拠フィードバック＝人間ゲート**であり、
ここを自動で `agreed` 埋めにすると CTL の信頼性が崩れる（philosophy.md 第6条 人間最終承認 /
crosscut-continuous-learning の「自動 promote は実装しない」決定と整合）。`scripts/council-ctl.py`
があれば `evaluate <id> --status <...>` で埋め、stats.json と CTL が即再計算される。

## 他スキルからの呼び出し例

### layer1-autonomous-dev からの呼び出し（PR1 の唯一の統合点）

`layer1-autonomous-dev/SKILL.md` の step 4（タスク分解）直後で、複数実装案が viable な時：

```
if タスクの実装パスが ≥ 2 案 viable:
    council skill を起動
    入力:
      context: SPEC.md 該当機能 + 検討中の実装案
      options: [実装案A, 実装案B, ...]
      question_to_answer: "どの実装案を採用すべきか"
      source_skill: "layer1-autonomous-dev"
      category: "implementation"
    出力を受領 → 合意プロセス開始
```

step 5.5（Shift Left 基盤）で不可逆操作検出時も同様に起動する。

### 直接起動（人間 / L0 / L2 から）

「Council に諮って…」「合議で判断して…」等の発話でも直接起動可能。
L0 の仕様トレードオフ、L2 の跨ぎドメイン方針対立にも使える（配線は PR3）。

## 関連ドキュメント

### 参照原典（このスキル外）

- [.claude/skills/layer0-spec-architect/references/philosophy.md](../layer0-spec-architect/references/philosophy.md) §1 フラクタル原則 / §3 情報純度原則 / §5 献上哲学
- `crosscut-issue-quality-gate/SKILL.md` — Issue 品質チェック（発動契機 (b)、v5.8.0 追加）

### 参照ドキュメント（このスキル内 references/）

- [references/council-philosophy.md](references/council-philosophy.md) — Council 6 公理（design-history.md は v4.2 で 7 公理化、`council-philosophy.md` 本体への反映は v4.3 で再判断）
- [references/pre-check.md](references/pre-check.md) — Phase 0 判定ルール
- [references/orchestrator.md](references/orchestrator.md) — フラット実装と重み計算
- [references/phase-protocol.md](references/phase-protocol.md) — Phase 0→1→3 規格
- [references/judgment-agent.md](references/judgment-agent.md) — Judgment Agent 設計
- [references/consensus-protocol.md](references/consensus-protocol.md) — 合意プロセス（v4.2 で CTL 連動の `compute_consensus_mode` を追加、`category` / `decision_category` の役割分担）
- [references/output-format.md](references/output-format.md) — JSON 入出力規格（v4.2 で `actual_outcome` / `invocation_id` / `project_metadata` / `consensus_mode` 追加）
- [references/conflict-typology.md](references/conflict-typology.md) — 対立類型（PR1 はスタブ）
- [references/ctl-calculation.md](references/ctl-calculation.md) — Council Trust Level 算出規格（v4.2 新規、stats.json スキーマ・invocations/・user-scope 初期化）
- [references/design-history.md](references/design-history.md) — ブリーフ要約（v4.2 で 7 公理拡張・改訂履歴追記）
- [references/personas/business/](references/personas/business/) — 事業 Council 3 ペルソナ

### 起動時に参照する設定

- [council-weights.md](council-weights.md) — 土台重み + 状況補正（L0 対話で更新）

## バージョン

- v0.1.0（PR1 walking skeleton） — business Council / Phase 1 のみ / 単純重み付き判定
- PR2 予定: Phase 2 反駁 + 対立類型 A/C/E/G
- PR3 予定: life Council + hybrid + 類型 D/F + Phase 2 質問形式 + F1-F3 儀式連携
