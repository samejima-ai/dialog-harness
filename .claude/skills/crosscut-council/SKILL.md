---
name: crosscut-council
dimension: D4
description: >
  横断判定機構（crosscut prefix）。Layer 0/1/2 のいずれにも属さず、全 Layer から献上を受けて判定を返す。
  人間 ≒ Council 原則（philosophy.md 第6条）の実装主体。
  実装中に発生する判断点で AI 自身が発動する**合議制判定機構（Council / 合議）の sub-skill**。
  3 ペルソナの並列独立意見生成と重み付き判定でトレードオフ判断・結論対立・
  不可逆操作・SPEC 矛盾・複数実装案の拮抗に対する判断支援を提供する。
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
  PR1 スコープ: business Council（経営者/開発者/哲学者）固定、Phase 1 のみ、単純重み付き判定。
---

# Council System (合議制判定機構)

実装中に発生する判断要請を受理し、3 視点の重み付き判定で単一の推奨を導く sub-skill。
Dialog Harness 本体から**独立**した構造で設計され、将来切り出し可能。

## 原則

- **Council 内部は非フラクタル**: 起点・分岐点としての決断機構であり、フラクタル原則の**内部的例外**。トリガー構造（Council を呼ぶ側）は `philosophy.md` §1 のフラクタル原則に従う（A⇄B の擦り合せループが全階層で反復）
- **Orchestrator はフラット**: 情報を流し応答を集約するのみ。判断機能を持たない。重みの適用は決定論的計算
- **判断 ≠ 決定**: Judgment Agent の出力は Council の最終判断。**決定は実装者の合意プロセスを経て成立**する
- **final_decision は常に null**: Council は決して決定を埋めない。実装者が合意プロセスで方針化するか、人間に献上する
- **対立は構造化する**: 対立は合意のために討論する価値がある差異。解消は目的ではない、見える化が目的
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
[対立度判定] PR1 は簡略版: 全会一致 / 単純対立 の2値のみ
  → 完全な類型 A-G 判定は PR2 で実装（references/conflict-typology.md 参照）
  ↓
[Phase 2] PR1 ではスキップ（PR2 で追加）
  ↓
[Phase 3] Judgment Agent による重み付き単一回答の導出
  → temperature 0.1、人格なし（references/judgment-agent.md）
  → 全会一致時は多様性（プルラリティ）として質を評価
  ↓
[出力] JSON（final_decision は常に null）
  ↓
[ログ] history/COUNCIL-LOG.md に追記
  ↓
[合意プロセス] 実装者が理解→質問→方針決定（references/consensus-protocol.md）
```

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
- conflict_type（PR1 は `unanimous` / `simple_conflict` のみ）
- final_weights（適用された重み配分）
- judgment_confidence
- implementer_consent（後追記、合意プロセス完了時）
- human_escalated（bool）

COUNCIL-LOG は append-only。編集不可。振り返り儀式（F1-F3、PR3 で連携）で監査する。

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
