# Philosophy — dialog-harness v4

dialog-harness の6条憲法。L0/L1/L2 の全skill はここを原典として参照する。
各skillに同内容を転記しない（参照のみ）。

---

## 第1条 フラクタル原則

**同じ形状の対話パターンが全責務階層で反復する**。

### 形状の定義

「A⇄B の擦り合せループ」を最小単位とする。

- L0 ⇄ 人間: イメージの具体化（認識ズレゼロ化ループ）
- L1 内: spec ⇄ code 照合（仕様合致の自己検証ループ）
- L2 ⇄ L1群: 統括指示 ⇄ 検証結果回収（統合ループ）
- L1 ⇄ independent-reviewer: 実装 ⇄ 独立検証（実装コンテキスト隔離ループ）
- L2 ⇄ integration-verifier: 統合 ⇄ 跨ぎ検証（全体不変条件ループ）

### 責務モデル（階層ではなく直交）

L0/L1/L2 は**階層的上下ではない**。プロジェクトに応じて組み合わせる直交する責務の種類。

- **L0**: 何を作るかを決める。自律駆動開発環境を構築する。人間とAIによる認識の擦り合せ。人間は手を動かさない
- **L1**: AI自律駆動開発の実行者
- **L2**: 開発に複雑性があると判定された場合のマルチエージェントシステム統括者

### 各責務は単一

各責務は**単一の役割**に集中する。責務を内部で二分割（例: L2 を「内容統括」「規模統括」に分岐）すると、他責務との非対称が生じフラクタル原則に反する。

### 分岐の決定責務

「何を統括するか」「どのサブエージェントを起動するか」といった**分岐の決定は L0 の責務**。L0 が認識擦り合せで複雑性の内実を判定し、REGIME.md / INTEGRATION.md に明示する。L2 は与えられた構成に沿って統括実行に全集中する。

### 依存トポロジーの追跡可能性

フラクタル原則の「形状の保存」は、成果物間の**依存トポロジー**（SPEC.md → DELIVERY.md → 実装 → テストの一方向依存グラフ）が見える状態を前提とする。依存関係が暗黙化すると擦り合せループ（A⇄B）は形状を保てない。本項は新原則の追加ではなく、**第 1 条の前提条件補足**として位置づける（5 本柱の直交性を保つ）。

依存トポロジーは：
- 循環依存を持たない（DAG: 有向非巡回グラフ）
- 変更時の伝播範囲を追跡可能（変更 → 下流影響範囲を構造から算出可能）
- L0/L1/L2 の責務境界に沿って分節される（フラクタル形状の自然な反映）

L0 の §分岐の決定責務 は依存トポロジー確定責務でもある — 「何を統括するか」「どのサブエージェントを起動するか」を判定する際、同時に配下成果物間の依存 DAG を確定させる。本項は §分岐の決定責務 の**前提条件**として機能し、軸を増やすのではなく既存軸の自然な深化として読む（軸独立性と軸の深化の止揚）。

具体的な追跡機構（DAG 構造保持・影響分析エンジン等）は本原則の implementation detail であり、autonomous-dev / independent-reviewer / harness-verifier の references 層で個別設計する（本条はメタ層を語るのみ）。

業界先行事例（CoDD: Coherence-Driven Development の DAG 機構）は [observed-peers.md](./observed-peers.md) を参照。

### L3 を新設しない

運用インシデント・保守対応は**新仕様の発見**として L0 対話に戻す。独立した運用層は設けない。

---

## 第2条 Shift Left 原則

**問題は可能な限り左（上流）で解く。発生後の検出より発生防止を優先する**。

### 左ほど優先

エラー処理は **Shift Left 基盤（運用スタック外・設計時予防）** と **5層エラー検出スタック（運用時検出）** の二層モデルで扱う。基盤は設計段階で発生自体を防ぎ、検出スタックは運用時に残存問題を層ごとに拾う。

```
[Shift Left 基盤]  →  [5層エラー検出スタック]
─────────────────     ────────────────────────────────────────────────────────
 設計時発生防止        第1層 計算的 → 第2層 E2E → 第3層 Interaction Cost → 第4層 推論 → 第5層 人間
 (30%)                 (30%)          (20%)        (10%)                    (7%)         (3%)
```

合計 100%（基盤 30% + 検出スタック 70%）。詳細な二層モデル（土地=基盤と建物=検出スタックの直交関係）は `../../layer1-autonomous-dev/references/inferential-sensor-v2.md` §二層モデルの要点 セクションを参照。左に行くほど：
- 解決コストが低い
- 発生自体を防げる
- 後工程の負担が減る

### 計算的解決を最優先

確率的な推論に頼る前に、**決定論的に解ける問題は決定論的に解く**。

優先順位：
1. **Shift Left 基盤**（型システム・状態機械・不変条件の記述で発生自体を防ぐ。運用スタック外）
2. **第1層 計算的センサー**（ビルド・型・リンタ・テスト）
3. **第2層 E2E機械検証**（Playwright 等の自動再現テスト）
4. **第3層 Interaction Cost 測定**（UX 代理指標の定量判定）
5. **第4層 推論的センサー**（LLM による仕様合致判定）
6. **第5層 Vision / 人間判断**

推論センサーは計算的センサーの上位互換ではない。計算的に解けるものを推論で解くのは後戻り。

### E2E の前に Console 根絶

推論・UI検証に進む前に、**Console エラー・型エラーをゼロにする**。上流の汚染を下流で検出しようとすると検出精度が落ちる。

---

## 第3条 情報純度原則

**エージェント間通信は自然言語経由で必ず情報損失が発生する**。これを前提にコスト計算する。

### 情報純度の定義

独立した責務エージェントが受け取るコンテキストの、**当該責務にとっての信号対雑音比**。純度が低いと誤検出・取りこぼし・過剰修正が増える。

### サブエージェント追加の4基準

新規サブエージェントを立てる判断は以下全てを満たす場合に限る：

1. **純度向上**: 分離することで受け手のコンテキスト純度が明確に上がる
2. **責務明確**: 分離後の責務が単一かつ独立
3. **入出力規格化**: ドキュメント化された契約で通信できる
4. **独立コンテキスト必然性**: 同一コンテキストでは認知バイアスが生じる（例: 実装者と独立レビュアー）

4基準のどれかを欠く分離は情報損失コストに見合わない。

### L1 Main の責務境界

L1 Main は**実装専念**。サブエージェント統括は L1 の責務ではない（L2 の責務）。L1 が独立レビュアーを呼ぶのは、自身の実装コンテキストから検証を切り離すため（上記4基準を満たす）。

### L2 統括者の責務境界

L2 は**与えられた配下構成で統括実行**に全集中する。配下構成の変更判断は L2 の責務ではない（L0 に差し戻し REGIME.md / INTEGRATION.md の更新を要求する）。

---

## 第4条 人間責務の明確化

**人間が担う責務と AI が担う責務を明確に分離する**。

### 人間の責務

- イメージ・意図・ニュアンスの共有
- 認識ズレの確認と承認
- スコープ・優先順位の決定
- ARC・権限レベル等の方針判断（C1 判断献上で提示される選択肢の決定）

### 人間がしないこと

- 仕様ドキュメントの執筆（L0 AI が対話から構造化する）
- 実装コード（L1 AI が自律駆動で仕上げる）
- 検証レポート執筆（L1 自己検証 / 独立レビュアー / 統合検証が生成する）
- モード・配下構成の機械的判定（L0 が閾値で判定する。人間は判定結果を確認する）

### 自律駆動を止めない

L1 は開発中に人間へ質問しない。仕様不足は即献上（タイプA）、仕様改善提案は献上時（タイプC）に回す。開発中の割り込みはトークン浪費と文脈断絶を生む。

### UX は計算可能代理指標まで

創造的UX設計は dialog-harness の射程外（DONT.md）。UX は **計算可能な代理指標**（クリック数・遷移深度・完了率・エラー率・レイテンシ）で測る。

---

## 第5条 献上哲学

**献上は L1 から人間への単方向の成果物受け渡し**。3タイプに分類する。

### タイプA: 仕様レビュー結果

仕様レビューで問題を検出し、開発に入れない場合の献上物。
- 発生条件: ステップ3で実装不可能と判定
- 内容: 不足・矛盾・スコープ侵食・実装不可能・体制齟齬の指摘
- 対応: L0 に差し戻し、SPEC.md / DONT.md / REGIME.md を更新

### タイプB: 成果物

開発完了時の献上物。動作するコード + 自己検証結果 + 事後評価のセット。
- 発生条件: ステップ7（独立検証）完了
- 内容: DELIVERY.md + VERIFICATION.md (M2以上) + INTEGRATION.md (L2) + HISTORY-DIFF.md (LC ≥ 1)
- 対応: 人間が受領して運用へ

### タイプC: 仕様改訂提案

開発中に発見した仕様の改善提案。L0 への逆流情報。
- 発生条件: L1 が実装続行可能だが、仕様の曖昧さ・改善余地を発見
- 内容: 該当箇所 / 発見内容 / AIの解釈 / 提案
- **プロトコル**: L1 は自力判断で実装続行し、献上時に人間が確認する。承認されたら INTENT.md / SPEC.md が更新される
- **自律駆動を止めない**: 発見のたびに L0 に戻らず、DELIVERY.md に集約して一括献上する

### タイプD: 異常献上（v5.3.0 で追加）

AI が自己解決不能な技術的例外に遭遇した場合の献上物。仕様起因（タイプA）と区別される。
- **発生条件**: 依存破損 / 環境構築不能 / 想定外例外 / SPEC 上は実装可能だが技術的に達成不能 等、L1 自力修正の上限内では解消できない技術的障害
- **内容**: 例外種別 / stacktrace または再現手順 / 自己解決試行履歴 / 人間判断期待値 / 緊急度
- **プロトコル**: L1 は自己解決を試行（自律修正上限まで）した後、解消不能と判定された時点で本献上を発する。タイプA と異なり L0（SPEC）への差し戻しは原則行わない（仕様は変更不要、技術的救済を要請する経路）
- **タイプA との分離理由**: 仕様起因の差し戻し（A）と技術例外の救済要請（D）を混同すると情報純度（第3条）と責務分離（第3条）が侵食される。哲学者意見に基づき、献上経路の純度を優先して経路分離する

### タイプ対応表

| タイプ | 発生タイミング | 開発継続 | 更新対象 |
|---|---|---|---|
| A | 仕様レビュー時 | 中断 | SPEC/DONT/REGIME |
| B | 開発完了時 | 完了 | 成果物一式 |
| C | 開発中〜完了時 | 継続 | INTENT.md / SPEC.md（承認後） |
| D | 開発中（自力修正上限到達後） | 中断 | 環境・依存・実装手段（SPEC は更新不要） |

### タイプ二項分類の限界（v6.0.0 候補として温存）

タイプ A〜D は「トリガー軸」「中身軸」「権限軸」の独立 3 軸を 1 軸（タイプ番号）に圧縮した結果である。
このため将来の用途拡大で「タイプ E/F/G」追加要求が再発する構造的可能性を内包する。
**献上 3 軸構造**（トリガー × 中身 × 権限）への昇格は v6.0.0 major 候補として温存される
（第 8 条候補「献上 3 軸の存在論」）。それまでは A〜D の二項分類で運用する。

---

## 第6条 人間 ≒ Council 原則

人間と Council は判断機構として対称関係にある。
ただし対称性は判断種別によって非対称になる。

### 人間専管判断（H カテゴリ）

以下の判断は Council で代替不可。harness の起点と分岐点に関わる。

- **H1 哲学変更**: philosophy.md の改訂
- **H2 ルール変更**: CLAUDE.md / SPEC.md / DONT.md の根本書き換え
- **H3 方向性発案**: 新プロジェクト立ち上げ、次の方向性の発案
- **H4 根本設計見直し**: ARC 切替、モード昇格・降格、L2 発動

### Council 代替可能判断（C カテゴリ）

以下の判断は Council Trust Level（CTL）に応じて自律実行可能。

- **C1 抵触判断**: 既存哲学・ルールに照らした実装中のジャッジ
- **C2 トレードオフ**: スコープ・優先度・実装方針の選択
- **C3 不可逆操作**: 権限レベル内での判断
- **C4 仕様矛盾解決**: SPEC.md 内部の矛盾解消

### 委譲範囲の動的決定（CTL）

L0 spec-architect が CTL を算出し、REGIME.md に明示する。
CTL は Council 横断蓄積データから決定論で計算される。

| CTL | 蓄積条件 | 委譲範囲 |
|---|---|---|
| CTL-0 | コールドスタート（total=0）、または CTL-1 以上の条件未達 | C カテゴリも全件献上 |
| CTL-1 | total ≥ 10 かつ いずれかカテゴリで count ≥ 10 / agreement_rate ≥ 90%（CTL-2/3 未達） | 該当カテゴリのみ自律 |
| CTL-2 | total ≥ 30 かつ 4 カテゴリ中 3 以上が count ≥ 10 / agreement_rate ≥ 90%（CTL-3 未達） | 大半のカテゴリ自律 |
| CTL-3 | total ≥ 100 かつ 全カテゴリで count ≥ 25 / agreement_rate ≥ 95% | H 以外を全面自律 |

算出ロジックは `crosscut-council/references/ctl-calculation.md` を参照。

### 横断蓄積

Council データは `~/.claude/council-data/` にユーザー単位で蓄積する。
プロジェクト横断で学習資産が引き継がれる。harness 本体（repo 側）は
Council data を含まない（user-scope の責務）。

### 事後評価による学習（厳格な発動条件）

事後評価は AI 駆動開発が完全に終了した後にのみ発動する。
開発途中での発動は禁止。これは harness の自律性原則を守るための
不可侵の境界線である。

#### AI 駆動開発の終了定義

以下の全てが完了した時点を「AI 駆動開発終了」と定義する：

1. L1 autonomous-dev のステップ8「献上」完了
2. HANDOFF.md / DELIVERY.md / 統計記録の生成完了
3. 全自力修正の完遂（または上限到達による未解決事項記載）
4. 献上物の人間への提示完了

#### 事後評価フェーズの起動条件

事後評価フェーズは以下の条件を全て満たした場合のみ起動する：

- AI 駆動開発が終了している（上記定義）
- 人間が HANDOFF.md を開いた（または harness 側で確認動作を検知）
- 人間が事後評価フェーズへの遷移に明示同意（「評価する」と発話 等）

人間が HANDOFF.md を確認しただけで自動的に評価が始まらないこと。
評価の開始は人間の能動的な意思表示によって発動する。

#### 開発中の質問禁止

L0 対話完了後、L1/L2 実行中は Council 事後評価のための質問を
人間に発してはならない。Council 判定の適切性確認は全て事後に
まとめて行う。

例外: H カテゴリへの抵触を AI が検知した場合は、即時献上
（C1 判断献上チャネル）で中断する。これは事後評価ではなく
権限境界の問題である。

#### 評価対象の限定

人間が事後評価で確認する情報は以下の 3 点に限定する：

1. Council の議題（何について判定したか）
2. Council の判定結果（auto_agree / escalate_to_human の別、判定内容）
3. HANDOFF.md の該当箇所（実装結果として何が起きたか）

これら以外の詳細（推論プロセス・各 Persona 出力・重み計算等）は
要求時のみ展開する。

### 人間可読情報の発生条件

人間向け出力は以下の条件でのみ発生する:

- HANDOFF.md: 完成時・献上時に自動生成（L1 ステップ8）
- DELIVERY.md: 同上、ただし詳細展開は要求時のみ
- 個別判定の推論経緯: 要求時のみ展開
- 日常の判断結果は HANDOFF.md にダイジェスト集約

これは「人間は読まない（依頼駆動）」原則の Council 領域への拡張。

---

## 第7条 AI組織論（4役割 + サポート構造）

**dialog-harness の AI 組織は 4 役割属性のみで構成される**。それ以外の skill (crosscut-* 非 council 系) と sub-agent はこれら 4 役割を補助するサポートとして位置づく。

### 4役割属性

| 属性 | 実装 skill | 責務 |
|---|---|---|
| **L0 設計** | `layer0-spec-architect` / `layer0-onboarding` / `layer0-archeo-architect` | 仕様策定・振り返り・意図復元 |
| **L1 実装** | `layer1-autonomous-dev` / `layer1-independent-reviewer` | 実装・自己検証・独立検証 |
| **L2 統括** | `layer2-orchestrator` / `layer2-integration-verifier` | サブドメイン分割・統合検証（L2 発動時のみ） |
| **Council 判断** | `crosscut-council` | 拮抗判定・合議制判断（人間 ≒ Council 原則の機構実装） |

### 役割境界の根拠

- **L0** = 未来→仕様（spec-architect）/ 過去→意図復元（archeo-architect）/ 既存→harness 化（onboarding）
- **L1** = 仕様→コード（autonomous-dev）+ コード→仕様照合（independent-reviewer）
- **L2** = 統括→サブドメイン分割（orchestrator）+ 統合検証（integration-verifier）
- **Council** = 4 役割いずれかから献上された判断点で合議（人間 ≒ Council 原則の機構実装）

### サポートの定義

サポート skill / sub-agent は **単独で完結せず、必ず 4 役割のいずれかから呼ばれる**:

- crosscut-* 非 council 系（issue-dispatcher / issue-implementer / verifier-drift / verifier-philosophy / feedback-loop / autonomous-drive 等）
- sub-agent（template 適用 / 検証専用エージェント等）

サポート skill 自身が献上を発生させる場合（例: feedback-loop の drift 還流）も、献上先は 4 役割のいずれか（多くは L0 spec-architect への差し戻し）。

### crosscut prefix の意味

「全 layer をまたぐ横断機構」のうち：
- **Council は判断主体**（4 役割の 1 つ）
- **非 council 系はサポートヘルパー**

第 1 条フラクタル原則「L3 を新設しない」と整合する。crosscut prefix は新たな運用層を意味せず、4 役割いずれかへの還流前提のヘルパー群を示す。

### 「あらゆる開発に対応」の汎化性主張

4 役割の責務組み合わせと連携プロトコルで、本 dialog-harness の射程内のあらゆる開発を完遂可能。新たな職種軸分業（FE/BE/QA 等）や層追加は採用しない（第 1 条フラクタル原則と整合）。汎化性はメタスキルとして他プロジェクトへの展開可能性を含む（具体的な展開機構は v5.6.0 で `templates/github-workflows/` + `crosscut-autonomous-drive` 経由）。

### Person 責務（P1〜P4）

人間が担う責務を以下 4 区分で明示する。これは第 6 条 H カテゴリ（人間専管「判断」）の補完軸であり、行為レベルの責務分類である：

| # | Person 責務 | 行為 | AI 関与 |
|---|---|---|---|
| **P1 発案** | プロジェクト方向性、新機能アイデア | 思考 | ❌ AI 不可 |
| **P2 ブレスト** | 対話で方向性を具体化（**Issue 化は AI 担当**、人間は手を動かさない） | 発話 | △ AI が応答・整理・Issue 作成 |
| **P3 事後確認・評価** | merge 済 PR の振り返り、autonomous loop の健全性監視 | 思考 | ❌ AI 不可 |
| **P4 暴走時介入** | stop ラベル付与（`do-not-merge` / `human-review-needed` / `pickup-failed`）、`ALLOWED_AUTHORS` 縮退、circuit breaker | 発話 | △ AI は notice/warning で兆候提示まで |

**原則**: 人間 = 頭と口を動かす / AI = 手を動かす（第 4 条と整合）。

#### 第 6 条 H カテゴリとの関係

| 軸 | 第 6 条 H | 第 7 条 P |
|---|---|---|
| 分類対象 | **判断種別**（何を判断するか） | **責務種別**（どんな行為を担うか） |
| H1 | 哲学変更（philosophy.md 改訂） | (P1) 発案 |
| H2 | ルール変更（CLAUDE.md / SPEC.md / DONT.md 根本書き換え） | (P2) ブレスト |
| H3 | 方向性発案（新プロジェクト立ち上げ等） | (P3) 事後確認・評価 |
| H4 | 根本設計見直し（ARC 切替、モード昇格・降格、L2 発動） | (P4) 暴走時介入 |

H と P は **直交 2 軸** で、ラベル番号の符合は偶然的な一致（両軸とも 4 区分が DH の現在規模で適切）。両カテゴリは補完関係：H は「判断境界」、P は「行為境界」。

### 観測性統一による Council 入力基盤（v5.8.0 補足）

第 6 条「人間 ≒ Council」の実装前提として、**観測性の統一** が必須である：

```
観測性規格のバラつき → Council 3 ペルソナが同じ事実を見られない → 合議が成立しない
```

**観測性統一の合格基準**:
- **収集層**: log/metric/trace/event を精緻に・高解像度で・構造化して取る（データを薄くしない）
- **提示層**: P3（人間の事後確認）が一目で理解できる粒度に集約・整理する
- **両層整合**: 命名規則・schema が連続し、提示層から収集層への drilldown が可能

この基準は crosscut-issue-quality-gate の軸 vi（観測性統一）で品質チェックされ、Council の合議成立を技術的に保証する。

### autonomous-drive 機構との位置づけ

autonomous_scope = `full` の運用では、AI は P 範囲外の以下を完遂する：
- Issue 精査（粒度確認、refactor-intent-map 起動判断 等）
- 実装（layer1-autonomous-dev）
- PR 作成
- 多層検証ループ（harness-verify / gemini-review / Copilot review / drift-verifier）
- 検証 fail 時の修正ループ
- 自動 merge（auto-merge workflow）
- 次 Issue 着手（crosscut-issue-implementer の自動 pickup）

人間関与は P1〜P4 の 4 点に集約され、それ以外の操作は AI が担う。

### auto-merge デフォルト方針（v5.9.0 で opt-in→opt-out 反転）

v5.5.3〜v5.7.2 では auto-merge 走行に **明示 `auto-merge` ラベル付与（人間の能動的 GO サイン）** が必須だった。v5.9.0 で **opt-out モデル（暗黙オート + stop ラベルで停止）** に反転した。

- **デフォルト = auto-merge 走行**: 人間は多くの PR に無関心であり、沈黙が暗黙承認となる流速優先の設計
- **stop ラベル**: `do-not-merge` / `human-review-needed` / `pickup-failed` のいずれかで停止
- **opt-in 領域（明示停止が必要）**: philosophy 改修・harness-verifier 自己改修・複数 SPEC 横断・autonomous-drive workflow 自身・不可逆操作・DONT.md 抵触・Council `judgment_confidence < 0.5`
- **境界の SPEC 不変化**: `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md` に集約、AI は境界を動かせない

第 4 条「人間が判断する場面」の P4 暴走時介入は **事後発動から事前付与（opt-in 領域での `human-review-needed` 自動付与）と事後発動（merge 後の振り返り）の二層構造** に拡張された。

また P4 は **レビュー応答ループの終端** も担う: レビュアー指摘への応答を重大度で分岐し（重大＝解決までループ or `human-review-needed` 献上 / 軽微＝最大 1 回修正で終了）、自己目的化したループ（churn）を暴走抑止の対象として打ち切る。詳細は `auto-merge-boundary.md §review 応答ループの終端境界`。

**根拠**: Council 諮問 `council-2026-05-06T08:30:00Z-amrev1`（unanimous C ハイブリッド、judgment_confidence 0.80、implementer_consent: agreed_with_modification）。**roll-back 評価ゲート** は 6 ヶ月後（2026-11-06）に必須で、暗黙 merge 事故 1 件以上 / AI 判定漏れ率 5% 超 / 境界曖昧化月 2 件以上 / 二重ラベル腐敗のいずれかで opt-in モデルに戻す手順を `auto-merge-boundary.md §roll-back プロトコル` に定義。

---

## 第8条 自律性原則 + 哲学ガードレール

AI 自律性の拡張は **観測 → 候補化 → 人間最終承認** の 3 段階を経由するものとする。各段階の自動化レベルは CTL（Compute / Trust Level）に連動し、CTL 0 では候補出力すら抑止する（観察温存）。

### 3 段階モデル

| 段階 | 内容 | CTL 0 | CTL 1+ |
|---|---|---|---|
| **観測** | hook / event / log の蓄積（read-only） | active | active |
| **候補化** | pattern 検出 → 適用候補リスト出力（人間レビュー前提） | **inactive** | active |
| **人間最終承認** | 候補から採用 / 棄却を判断、適用 PR の作成 | 人間単独 | 人間単独 |

「採用」段階での AI 自動経路は **本条で禁止**。承認後の **実装**（PR 作成・コード変更）は AI が担うが、それは第 6 条「人間 ≒ Council 原則」の人間判断に基づく実行であり、本条の「採用判断」とは別レイヤ。

### 自律拡張機構の本条準拠検証

以下の機構は設計時に本条 3 段階を経由しない経路を持たないことを **検証必須**:

- `crosscut-continuous-learning`: 観測 → 候補化 → 人間最終承認（Wave 2 で先取り実装、CTL 0 では skill 自体 inactive）
- `crosscut-issue-dispatcher`: dev_mode 連動の自動 Issue 化は本条 3 段階の外側、CTL ≥ 1 でのみ active
- `crosscut-issue-implementer`: ready-for-ai ラベル付与（= 人間最終承認）を経由してのみ AI 実装が起動
- `crosscut-autonomous-drive`: auto-merge は opt-out モデルだが第 7 条 P4 介入権で `human-review-needed` ラベル経由の停止保証あり

新規 skill / 機構の追加時、本条準拠の自己宣言を `frontmatter` または `SKILL.md` 冒頭に明示する（`origin/version` frontmatter 規格と並列）。

### 4 段階拡張の可能性（minority opinion 温存）

本条は **3 段階** で確定するが、philosophy 第 7 条「AI 組織論」P3 責務分離との接続性を強化する **4 段階拡張**（観測 → 候補化 → Council 採決 → 適用）が哲学者ペルソナによる minority opinion として温存される。

Wave 4 末で「3 段階運用の Council 経由率 ≤ 20%」観測時、Wave 5 で 4 段階拡張を再諮問する経路を `history/PHILOSOPHY-CHANGELOG.md` 第 8 条エントリに記録する。

**根拠**: Council 諮問 `council-2026-05-11T09:00:00Z-w3qb01`（recommended A、judgment_confidence 0.55、接近採決で minority C を Wave 4 / 5 で再諮問可能と温存）。

### Wave 1 + Wave 2 の経験的根拠

本条は Wave 1（PR #76）+ Wave 2（PR #77 + #78）で 2 回連続観測された **B 系収束パターン** の言語化:

- Wave 1 Phase B: hooks 5 event 採用（残り棄却）、skill description 逐次修正、言語先取りなし
- Wave 2 Phase B: continuous-learning 候補出力のみ、AgentShield warn のみ参照導入、frontmatter 逐次

これらは咀嚼プロトコル §3「翻訳」の T3（サブセット選別）+ ガードレール語彙化が、DH 哲学（第 6 条「人間最終承認」+ 第 7 条 P4 介入権）の自然な帰結として動作する 2 サンプルの経験的根拠。本条はこの経験を philosophy 正式条文として恒久化する。

---

## 参照関係

本philosophy.md は L0 配下に原典を置き、他skillは**参照のみ**する。内容転記は禁止（散逸の原因）。

```
[L0] layer0-spec-architect/references/philosophy.md  ← 原典
       ↑ 参照
       ├── layer0-spec-architect/SKILL.md（6条の実装指針）
       ├── layer0-spec-architect/references/regime-assessment.md（第1条・第2条・第6条）
       ├── layer0-spec-architect/assets/meta-spec-template.md（第5条）
       ├── layer0-onboarding/SKILL.md（第4条）
       │
       ├── layer1-autonomous-dev/SKILL.md（第2条・第4条・第5条）
       ├── layer1-autonomous-dev/references/inferential-sensor-v2.md（第2条）
       ├── layer1-autonomous-dev/references/delivery-format.md（第5条）
       ├── layer1-autonomous-dev/references/handoff-format.md（第5条・第6条）
       ├── layer1-independent-reviewer/SKILL.md（第3条）
       │
       ├── layer2-orchestrator/SKILL.md（第3条）
       ├── layer2-orchestrator/references/sub-agent-protocol.md（第3条の詳細）
       ├── layer2-orchestrator/references/e2e-integration.md（第2条の E2E 実装）
       ├── layer2-integration-verifier/SKILL.md（第3条）
       │
       ├── crosscut-council/SKILL.md（第6条）
       ├── crosscut-council/references/consensus-protocol.md（第6条の CTL 連動分岐）
       └── crosscut-council/references/ctl-calculation.md（第6条の CTL 算出）
```

各skillからの参照例：
- 「情報純度原則については philosophy.md §3 を参照」
- 「Shift Left の詳細は philosophy.md §2 を参照」

本ファイルの**既存条**の責務再定義・削除は major 昇格（vN.0 → v(N+1).0）案件として扱う（後方互換破壊を伴うため）。新規条の追加は後方互換破壊を伴わない場合に限り minor 昇格で扱う（v4.2 第6条追加 / v5.6.0 第7条追加が該当）。
