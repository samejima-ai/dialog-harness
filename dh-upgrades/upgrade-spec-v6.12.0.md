# upgrade-spec v6.12.0 — 実行グラフの実体化（AD-032 本実装 第 1 段）

> **状態: L0 起草（人間レビュー待ち）**。本仕様の実装は escalation-matrix「規範文書改変」行に従い、
> 人間レビュー通過後・実装前に Council 諮問を経る（諮問議題は §争点）。
> 起点: **AD-032**（Hard Gate（守備）⇄ 整合性検証（DAG verify・攻撃）の対称化検討 [候補]、
> Council `council-2026-05-16T06:00:00Z-coddag` 由来）が「次の振り返り儀式 F1-F3 または別 Council 諮問で
> 取り扱う」と予約していた本実装トリガーの発火 +
> L0 対話決定（2026-08-25、ひでさん）: グラフの実体化に絞る / 配布規格にする / 粒度は skill・gate 単位 /
> 検査は当面 DH 本体のみ。
> 判断材料: 対話内で実施したグラフエンジニアリング定義との逐項照合（10 項目・先行 3 点・未達 1 点）。

---

## 0. 位置づけ — 新機構ではなく「既存宣言の集約」

DH は既に実行グラフとして動作している。ノード（skill / 確定的 script / human gate）、エッジ（起動関係・
条件分岐・ループ）、ステート（SPEC/REGIME/DELIVERY/HANDOFF/append-only ログ）はすべて実在する。
欠けているのは**それらを突き合わせる単一情報源**であり、定義は README の mermaid / escalation-matrix の表 /
各 SKILL.md の処理フロー / `*.workflow.mjs` / `.github/workflows/*.yml` の 5 箇所に分散している。

本リリースは新しい判定機構・新しい規範カテゴリ・新しい運用層を追加しない。分散した宣言を 1 ファイルに
集約し、宣言と実装の乖離を機械検査に載せる**置換**である。philosophy 第 1 条 §依存トポロジーの追跡可能性は
「具体的な追跡機構（DAG 構造保持・影響分析エンジン等）は本原則の implementation detail であり、
autonomous-dev / independent-reviewer / harness-verifier の references 層で個別設計する」と明示的に
委譲しており、本リリースはその委譲先の実装にあたる（**philosophy.md は改訂しない** = L-FROZEN-PHIL 不可侵）。

**不変条件（全機能共通）**:

- I-1 GRAPH.yml は**判定を持たない**。「どこで誰に諮るか」の宣言であって、判定は escalation-matrix の
  定めに従う（v6.11.0 F7-1 と同型。グラフが判定を代行し始めたら drift として検出対象）
- I-2 GRAPH.yml は**実装の上位ではない**。実装が正、宣言が従。乖離検出時に自動で実装を書き換えない
  （検出のみ・是正は L0/人間。軸監査 `council-axis-audit.py` と同じ姿勢）
- I-3 粒度は **skill / gate 単位**に固定する。SKILL.md 内部の処理ステップをノード化しない
  （二重管理による GRAPH.yml 自身の陳腐化を構造的に排除）
- I-4 ローカル自律実行ファースト。CI 専用の検査経路を作らない（`verify.py` が正、CI は同一スクリプトを呼ぶ）
- I-5 新規規範ゆえ `stage:` / `review_trigger:` を必須付与する（f5fc45 の「足したら忘れずに減らす」規則の自己適用）

## F1. GRAPH.yml — 実行グラフの単一情報源（priority: critical）

DH リポジトリルートに `GRAPH.yml` を新設する。

| 条件 | 内容 |
|---|---|
| F1-1 | `nodes` は `id` / `kind`（`agent` \| `tool` \| `human`）/ `impl`（実体パス）/ `role`（`L0`\|`L1`\|`L2`\|`council`\|`support`）を持つ。`kind` はグラフエンジニアリングの Agent/Tool/Human ノード三分類に対応し、`role` は philosophy 第 7 条の 4 役割属性に対応する（**新分類を発明せず既存 2 軸を機械可読化する**） |
| F1-2 | `edges` は `from` / `to` / `type`（`standard` \| `conditional` \| `loop`）/ `source`（宣言の出典 = ファイルパス + 節）を持つ |
| F1-3 | `type: conditional` は `condition` 必須（例 `REGIME.mode >= M2` / `judgment_confidence < 0.5` / `CTL >= 1`） |
| F1-4 | `type: loop` は **`max_iterations` 必須**（例外なし。上限のないループを宣言できない形にする） |
| F1-5 | `human` ノードは `gate`（`P1`-`P4` / `H1`-`H4`）を持ち、第 9 条の委譲レベル（`L-FULL`/`L-GATE`/`L-FROZEN-PHIL`/`L-FROZEN-META`）を `delegation` に記す |
| F1-6 | ルート直下配置のため `dev-env-spec.md` §ファイル配置規則の許可リストに `GRAPH.yml` を追加する（DESIGN.md の前例と同型の 1 行追加） |

**書かないもの**: SKILL.md 内部の手順、Council の Phase 内訳、CI job の内部ステップ（I-3）。

## F2. execution_graph 検査（priority: critical）

`harness-verifier/checks/execution_graph.py` を新設する。既存 `dependency_graph.py`（skill 間の**参照**リンク検査）
とは別責務 — 本検査は**起動**グラフを見る。

| ID | 検査 | 判定 |
|---|---|---|
| G-1 | すべての `loop` エッジが `max_iterations` を持つ | **FAIL** |
| G-2 | すべての `impl` / `source` パスが実在する | **FAIL** |
| G-3 | すべての `conditional` エッジが `condition` を持つ | **FAIL** |
| G-4 | `loop` を除いた部分グラフが DAG である（循環なし） | **FAIL** |
| G-5 | 実装側に存在する起動経路が GRAPH.yml に宣言されている（未宣言起動の検出） | **WARN**（初版） |

- F2-1 G-1〜G-4 は GRAPH.yml 内部で完結する決定論検査（LLM 不使用・第 2 条 計算的解決最優先）
- F2-2 **G-5 は初版 WARN 止まり**とする。実装側の起動記述は自然文を含み誤検出が避けられないため、
  いきなり FAIL にすると DH 自身の CI が停止し開発が止まる。FAIL 昇格は「6 cycle 連続で誤検出 0 件」を
  条件に別途判断する（v6.11.0 C-1 と同型の段階導入）
- F2-3 `verify.py` の検査群に登録し、`--strict` で G-5 WARN も FAIL 扱いにできるようにする
- F2-4 GRAPH.yml 不在のリポジトリでは本検査を **skip**（利用者プロジェクトで壊れない・後方互換）

## F3. ループ上限の宣言化（priority: standard）

F1-4 を既存のループエッジに適用し、上限が未定義のまま走る経路を潰す。

- F3-1 `crosscut-feedback-loop` に**還流回数の上限**を明記する（同一 drift に対する還流は最大 3 回、
  既存の L1 自力修正上限と同値。超過時は人間献上に切り替え）。auto-merge-boundary §review 応答ループの
  終端境界と同型の書き方に揃え、新しい概念を作らない
- F3-2 既知のループ（L1 自力修正 3 / judgment retry 2 / review churn 終端 / circuit-breaker / feedback-loop）を
  GRAPH.yml の `loop` エッジとして宣言し、`max_iterations` に既存値を転記する（値の新規決定は行わない）
- F3-3 転記時に上限が**見つからない**ループが他にあれば、それは発見であって仕様漏れ。GRAPH.yml に
  書けないので L0 に差し戻して上限を決める（F1-4 が漏れを可視化する仕掛け）

## F4. 配布規格（priority: standard）

人間決定「配布規格にする」に基づき、雛形と書き方規格を利用者プロジェクトへ配る。

- F4-1 `templates/graph/GRAPH.template.yml`（雛形）+ `layer0-spec-architect/references/graph-spec.md`（書き方規格）を新設
- F4-2 L0 §6「開発環境の設計・構築」の M2 標準生成構成に GRAPH.yml を追加する（M1 は任意）
- F4-3 **検査は配らない**（人間決定）。`harness-verifier` は D4 = DH 本体専用の独立機構であり、
  利用者プロジェクト（D2/D3）側の検査経路（`crosscut-verifier-drift` への組込み）は実使用の観測後に判断する。
  検査ロジックを 2 系統に分裂させ永続的に同期させる負債を、観測なしに背負わない
- F4-4 配布規格には**取り下げの teeth** を付す（§F5 の時限メタデータ）

## F5. 時限メタデータ（priority: critical）

I-5 の実装。新規規範に `stage:` / `review_trigger:` を付す（`dev-env-spec.md` §規範メタデータ）。

| 対象 | メタデータ |
|---|---|
| GRAPH.yml 規格（DH 本体） | `{ stage: 全段階, review_trigger: [cycles: 6, measured: 宣言と実装の乖離が 6 cycle 連続 0 件なら G-5 の FAIL 昇格を検討] }` |
| 配布規格（templates/graph/） | `{ stage: S0-S2, review_trigger: [measured: 利用者プロジェクトでの実生成が 2 件に満たない, date: 2027-02-28] }` — **空振りなら配布を取り下げる**（畳む条件を先に書く） |
| F3-1 の還流上限 | `{ stage: 全段階, review_trigger: [measured: 上限到達が 12 cycle 発生しなければ緩和候補] }` |

## 争点（Council 諮問の議題・実装前ゲート）

本仕様は以下 3 点で判断が拮抗する。実装前に Council へ諮る（escalation-matrix「規範文書改変」行）。

1. **配布規格化と f5fc45 の衝突**: 人間決定は「配る」だが、`templates/` への規格追加は
   f5fc45「減らす・時限化」原則と正面から衝突する（規範量が増える）。F5 の取り下げ teeth（実生成 2 件未満で
   撤回）で緩和できるか、それとも DH 本体限定に戻すべきか
2. **G-5 の判定強度**: 未宣言起動の検出を初版 WARN に落とす（F2-2）ことは、DH 自身が名指しした失敗様式
   「手順書依存の空文化」の再演にならないか。WARN のまま誰も見なければ GRAPH.yml は飾りになる
3. **GRAPH.yml のルート配置**: `dev-env-spec.md` の配置規則（ルート直下は INDEX/SPEC/DONT/REGIME/CLAUDE/
   DOMAINS/README + UI 時の DESIGN のみ）を 1 行広げる妥当性。`.claude/` 配下や `spec/` 配下との比較

## DONT（本リリースのスコープ外）

- **philosophy.md の改訂**（第 1 条は既に追跡可能性を要求済み・条文は動かさない。L-FROZEN-PHIL）
- AD-032 の残余: 5 層エラー検出スタックへの DAG verify 組込み / 守備（Hard Gate）⇄ 攻撃の**対称化の境界線確定**
  — 本リリースは「攻撃側の機構を配置する」までとし、対称化の哲学的整理は次サイクルへ温存
- SKILL.md 内部処理のノード化（I-3）
- 利用者プロジェクト側の検査実装（F4-3・観測駆動）
- GRAPH.yml による実行時ルーティング（宣言であって実行基盤ではない。実行は v6.11.0 の Workflow が担う）
- CLAUDE.md へのエージェントルーティング標準行（**G-AGENT 凍結中**・f5fc45。GRAPH.yml は CLAUDE.md 規格に触れない）
- escalation-matrix の判定内容の変更（配線の宣言化のみ。促し先は 1 つも動かさない）

## 前提の記録（v6.11.0 C-1 の未達）

v6.11.0 は C-1 で「F2〜F5 の実行基盤は F1 の 3 発動で正規化ギャップ 0 件が確認されるまで opt-in」と
定めたが、本起草時点（2026-08-25）の軸監査は**正規化ギャップ 11 件**（すべて v6.11.0 F1-3 の options 記録
機械強制より前の記録）であり、**3 発動の観測は未達**である。本リリースは Workflow 実行基盤に依存しないため
C-1 の縛りの対象外だが、前リリースの受け入れ基準が未確認のまま次を積む事実を記録に残す。

## モード判定・実装体制

- DH 本体の継続開発（LC ≥ 1）・**M2**（R ≥ 2 = 他人配布によりオーバーライド。L2 発動閾値はいずれも未超過）
- AI 能力バージョン: Claude Opus 5
- CTL: **CTL-0**（2026-08-25 事後評価 7 件反映後 rate 0.8545 < 0.90）。C カテゴリも全件人間献上
- 実装順序: F1 → F5 → F2 → F3 → F4（宣言 → 時限 → 検査 → 既存ループ転記 → 配布）
- 実装前ゲート: **Council 諮問**（§争点 3 点を議題とする）
- 献上時ゲート: 人間判定（同行）
- 検証: harness-verifier 全 PASS + G-1〜G-4 の FAIL 動作を意図的な壊れ値で確認 + 反証記録
  （`falsification-protocol.md` 準拠。「この PASS が保証しない範囲」欄を含む）

## 履歴

- 2026-08-25: L0 起草（AD-032 予約の発火 + 振り返り儀式 F1-F3 + L0 対話決定に基づく）。人間レビュー待ち
