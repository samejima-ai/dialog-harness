# ANALYSIS: AI 駆動開発の工程カタログ — 世界水準の網羅調査と DH ギャップマップ

> **本文書は調査統合＋ギャップ提示（L0 一次材料）である。仕様変更ではない。決定は D5。**
> 起点: L0 対話（2026-08-27）「適当に挙げただけ、世界水準を調べて網羅的に考えたい」。
> 先行の 15 工程照合（対話ベース）を、出典付きの網羅調査で置き換える。
> 手法: 3 系統の並列調査（①産業実践 ②オーケストレーション理論 ③運用・計測・還流）。
> 全項目 2026-08 時点で一次情報源（公式 docs / arXiv / 公式ブログ）に出典確認済み。
> AI の自己申告・出典の取れない主張は不採用（DIAGNOSIS 2026-08-26 と同じ規律）。

| 項目 | 内容 |
|---|---|
| 対象 | AI エージェント自律駆動開発の工程・ループ・グラフ機構・計測指標 |
| 調査範囲 | Devin / Copilot coding agent / Codex / Jules / Cursor / Factory / Sentry / Datadog / PagerDuty / AWS AI-DLC / LangGraph / LlamaIndex / Temporal / OpenAI Agents SDK / Anthropic engineering / DORA 2025 / GitClear / DX ほか |
| 結論の要旨 | 業界は単一バックボーンに収束済み。DH は中間工程で世界水準以上、**入口（テレメトリ逆流）と計測（受入・介入率）が空白**。DH が業界標準から意図的に逸脱している点が 1 つある（auto-merge） |

---

## 1. 世界水準の合意事項（10 項目）

3 系統の調査が独立に到達した cross-cutting な合意。工程カタログより先にこれを置く —
個別工程の採否はこの合意に照らして判断できる。

| # | 合意 | 出典系統 |
|---|---|---|
| W1 | **全製品が同一バックボーンに収束**: トリガー → 計画 → 隔離実行 → 自己検証 → draft PR → 人間レビュー → マージ。**PR が人間との普遍インターフェース**であり、agent の自律はマージ手前で必ず切れる | ① |
| W2 | **エスカレーションは静的ルールから数値化された自己評価へ**: Devin confidence（🟢🟡🔴、🟢は🔴の 2 倍マージ率）、Sentry fixability score（閾値超のみ無人発火）。スコアが人間介入の分岐点になり、実測とも相関する | ① |
| W3 | **仕事の自動発見は「テレメトリ逆流」が主戦場**: エラー監視→RCA→修正 PR（Sentry Seer）、アラート自律調査（Datadog）、CI 失敗の self-healing、product analytics 起点（PostHog Code）。人間起票はトリガーの一種にすぎなくなった | ①③ |
| W4 | **仕様駆動（SDD）の復権**が 2025 年最大の工程論的変化: Spec→Plan→Tasks→Implement の強制（GitHub Spec Kit / AWS Kiro / AI-DLC）。仕様が Markdown でリポジトリに常駐し diff/review 可能 | ① |
| W5 | **自律度は権限設定ではなく実績に比例して拡大する運用プロトコル**: 全件手動レビュー→検証チェックリスト→段階的拡大（Anthropic）。DORA 2025「AI は増幅器、ROI は組織システムで決まる」 | ①③ |
| W6 | **停止条件は 3 層設計**: ①品質閾値（evaluator 合格）②予算（max_turns / token）③人間介入（interrupt）。予算層の欠落は実害事例として語られる | ② |
| W7 | **生成者と評価者の分離が反復ループの成立条件**: 同一モデルの Reflection は誤解を再強化。決定論チェック最優先＋主観次元のみ judge＋別モデル系統パネルが定石 | ② |
| W8 | **還流は「人間承認ゲート付き段階昇格」に収斂**: AI は提案まで・規範化は人間承認（Sentry / PagerDuty / CodeRabbit すべて同型）。完全自動の規範更新を実装した製品は確認できず | ③ |
| W9 | **計測の重心は生成量から受入率・介入率・revert 率へ**: merge 率 / revert 率 / human-commit 介入率 / auto-approve 率 / interrupt 率。**熟練者ほど auto-approve と interrupt が同時に増える**（都度承認→戦略的介入） | ③ |
| W10 | **出口側の真のボトルネックはレビュー容量**: 生成がレビュー容量を超えたら「生成を絞る・レビューを速くする・品質を落とす」の三択。保守性の遅行指標（churn 3.3%→7.1% / 複製 +81% / リファクタ 25%→10%）を出口に組み込むのが計測設計の要点 | ③ |

### DH との照合 — 合意との一致・逸脱

- **一致（DH が先行 or 同型）**: W4（SPEC 駆動は DH の設計そのもの）、W5（CTL ＝段階委譲の機構化。業界は運用プロトコル止まりで、DH は決定論算出まで機械化している）、W7（Council 独立観測・harness-verifier 非 LLM 検査・「panels help, debates hurt」と同結論）、W8（philosophy 第 6 条・第 8 条が製品横断の収斂と同型）、W2（Council 自己申告プロトコル (a)-(d) + jc 閾値 + confidence 帯別介入率 33/18/10% の実測）
- **逸脱（意図的・要監視）**: **W1 に対し DH は opt-out auto-merge**。業界は「agent の自律はマージ手前で必ず切れる」を普遍とするが、DH は stop ラベル＋verifier AND＋境界 SPEC＋roll-back ゲート（2026-11-06）を担保に**マージまで通す**。これは業界標準より踏み込んだ設計であり、roll-back 評価ゲートの実施が逸脱の妥当性検証になる
- **空白（本分析の主産物）**: W3（テレメトリ逆流が 1 本も無い）、W6 の予算層（token/cost budget が実行経路に無い）、W9（受入・介入率の計測が無い）、W10（保守性遅行指標が無い）

---

## 2. 統合工程カタログ × DH ギャップマップ

記号: ✓=実在 / △=部分 / ✕=無い / ⊘=意図的に採らない（根拠あり）

### 2-A. 入口（トリガー）— 10 工程

| 工程 | 代表実装 | DH | 現物 / 根拠 |
|---|---|---|---|
| Issue 割当・ラベル起動 | Copilot coding agent | ✓ | `issue-pickup.yml`（ready-for-ai） |
| @メンション起動 | Claude Code Action / Codex | △ | PR レビューは `claude-review.yml`。Issue 側の @ 起動は無い |
| エラー監視→RCA→修正 PR | Sentry Seer | ✕ | **W3 空白の中核**。kakuman-v3.0 は Sentry 接続あり（MCP 実在）だが agent への逆流路が無い |
| アラート自律調査 | Datadog Bits AI SRE | ✕ | — |
| CI 失敗の自己修復 | Dagger / Nx | ✕ | 赤 CI を見て起票する主体が居ない |
| 依存関係更新 | Renovate / Dependabot | ✕ | — |
| TODO・技術的負債スキャン | AIGeT / Tembo | ✕ | — |
| Product analytics 起点 | PostHog Code | ✕ | F3（プロダクト評価）の接続先 |
| スケジュール起動（cron） | Claude Code GH Actions | △ | 月次 `harness-verify` 1 本のみ |
| フリート一括投入 | Devin 顧客運用 | ⊘ | 配布先が少数（2 プロジェクト）の現状では不要 |

**入口の実在は 1.5 / 10。** 診断書の「仕事の自動発見ゼロ」が網羅調査でも確認された。

### 2-B. 中間（計画・実行・検証）— 10 工程

| 工程 | 代表実装 | DH | 現物 / 根拠 |
|---|---|---|---|
| 仕様駆動（Spec→Plan→Tasks→Implement） | Spec Kit / Kiro / AI-DLC | ✓ | spec-architect → SPEC/REGIME → L1。**W4 で業界が DH に追いついた形** |
| 計画立案・タスク分解 | Copilot Workspace | ✓ | L1 ステップ 4 |
| 隔離サンドボックス実行 | 全製品 | △ | worktree 運用実体ゼロ（診断 D+）。並列安全は LLM 判定 |
| confidence 自己評価 | Devin 2.1 | ✓ | Council 自己申告 (a)-(d)・jc 帯。介入率相関も実測済み（Devin と同じ検証水準） |
| 内部批評（critic） | Jules Code Critique | ✓ | L1 自己検証 + Council |
| テスト駆動検証ループ | Codex | ✓ | 5 層検出スタック第 1 層 |
| Doer-Verifier 分離 | Anthropic | ✓ | independent-reviewer（Falsification 付き・v6.9.0） |
| 長時間ハーネス（feature list `passes:false`） | Anthropic engineering | △ | 「早すぎる完了宣言」防止の明示機構は無い（DELIVERY 献上が近似） |
| AI コードレビュー（重大度フィルタ） | Codex P0/P1 のみ | ✓ | claude-review（tier ゲート）+ gemini + Copilot。P0/P1 絞りは claude-review の難度ゲートが同型 |
| レビュー指摘の自動修正 | Cursor Bugbot Autofix | △ | babysit 経路の修正ループはあるが独立機構ではない |

**中間の実在は 7.5 / 10。世界水準以上の箇所もある**（Falsification 明示・Council の重み意味論）。

### 2-C. 出口（評価・還流・代謝）— 12 工程

| 工程 | 代表実装 | DH | 現物 / 根拠 |
|---|---|---|---|
| PR 人間承認ゲート | 全製品（draft PR） | ⊘ | opt-out auto-merge（§1 の意図的逸脱。境界 SPEC + roll-back ゲートが担保） |
| Agent PR 受入監査（merge/revert/介入率） | dotnet/runtime 実測 | ✕ | **W9 空白の中核**。gh api から決定論で計算可能なのに未実装 |
| 自律度実測（auto-approve/interrupt 率） | Anthropic research | △ | CTL agreement_rate はあるが実行時の interrupt 系は無い |
| 保守性遅行指標（churn/複製/リファクタ比） | GitClear | ✕ | — |
| 運用インシデント対応 | Factory droid / AI-DLC Operations | ✕ | L3 を作らない原則（第 1 条）とは別に、検知→L0 差し戻しの配線が無い |
| flaky test 検出・隔離 | Trunk / BuildPulse | ✕ | — |
| postmortem 自動起草 | Rootly / incident.io | ⏳ | dev-diary（v6.14.0 起草済み）が観察層として近接 |
| コンテキストファイル品質管理 | AGENTS.md 研究（bloat 検出） | ✓ | 情報代謝 + 購読量上限。**AGENTS.md 統制実験（成功率改善せず +20% コスト）は DH の購読圧削減方針の外部裏付け** |
| docs drift 検出・自動更新 | DeepDocs | ✓ | verifier-drift + check_template_sync |
| ADR 自動起草 | Codex CLI ADR workflow | ✓ | ARCH-DECISIONS 運用 |
| レビュー知見の規範化（人間承認付き） | CodeRabbit Learnings | ✓ | continuous-learning（候補出力のみ・自動 promote 不実装 = W8 と同型） |
| memory 蒸留・アーカイブ | Anthropic context engineering | ✓ | reindex-librarian（HOT/WARM/COLD） |

**出口の実在は 6.5 / 12。計測系 3 工程がまとめて空白。**

### 2-D. ループ種別（12）と DH

evaluator-optimizer ✓（Council）/ self-refine ⊘（生成者・評価者分離を優先 = W7）/ reflexion ✓（COUNCIL-LOG 事後評価）/ debate ⊘（相互参照なしを実測で確定済み・PR #170）/ orchestrator-workers ✓（L2 + workflow 基盤）/ self-healing CI ✕ / 進化的ループ ⊘（第 8 条。**DGM の sandbox+人間監督+archive と同じ結論に独立到達**）/ プロンプト最適化 ✕（GEPA 系は自動評価器の整備が前提）/ **評価駆動開発（EDDOps）✕ — golden set + 閾値 CI ゲートが無い** / メモリ蒸留 ✓ / ReAct・Plan-and-Execute ✓（L1 の実行形）

### 2-E. グラフ機構（13）と DH

typed edge ✕（I-2、課題 2 係争中）/ checkpoint・interrupt/resume ✕（走行中 state が無い = 診断済み）/ fan-out+reducer △（workflow 基盤にあるがグラフ宣言外）/ 予算ガード △（circuit breaker のみ、token/cost 無し = W6 欠落）/ durable execution ✕ / guardrails ✓（stop ラベル・boundary）/ OTel GenAI ✕ / trajectory eval △（hook 観測 6 event）/ 判定バイアス緩和 ✓（axis-audit 4 指標・confidence 帯除去は G-Eval/PoLL 系の知見と同方向）

---

## 3. ギャップの優先順位（提案・決定は D5）

| 順位 | ギャップ | 根拠 | 実装コスト |
|---|---|---|---|
| **G1** | **テレメトリ逆流の最小実装**（CI 失敗・滞留 PR・期限切れ review_trigger → Issue 候補起票） | W3。入口 1.5/10 が最大の空白。診断書ボトルネック所見と一致 | 小（決定論スクリプト + cron 1 本） |
| **G2** | **Agent PR 受入監査**（merge / revert / human-commit 介入率を決定論で算出） | W9。dotnet/runtime が示した事実上の標準。**gh api だけで計算可能** | 極小 |
| **G3** | **kakuman-v3.0 のエラー監視逆流**（Sentry → 課題候補） | W3。Sentry MCP は接続済み、逆流路だけが無い | 中（製品側 D1-D3 作業） |
| **G4** | 予算層の停止条件（token/cost budget を実行経路へ） | W6。3 層のうち 1 層が欠落 | 中 |
| G5 | 保守性遅行指標（churn / 複製率の月次観測） | W10 | 小 |
| G6 | 長時間ハーネスの feature list（`passes:false` 型の完了防止） | ①調査 | 小 |
| G7 | EDDOps（golden set + 閾値 CI ゲート） | W6 品質層 / ②調査 | 大（golden 整備が前提） |

**採らないもの（根拠付き）**: debate 相互参照（PR #170 実測 + 「panels help, debates hurt」）/
進化的自己改善（第 8 条 = DGM 収斂と同型）/ 汎用コンテキスト要約の拡充（統制実験で効果なし）/
フリート投入（配布先 2 件では過剰）。

## 4. 本分析の限界

- 出典は取れているが、**製品の内部実装は公開範囲まで**しか見えない（Devin の confidence 実装詳細等）
- 「工程カタログ」は 2026-08 断面。この領域の陳腐化速度を考えると **6 ヶ月で再調査**が妥当
- DH 判定（✓/△/✕）は本セッションの実査に基づくが、⊘ の妥当性判断は D5 に属する
- 調査③の注記どおり「自律度」の業界標準指標は未確立 — G2 は標準の先取りであって追随ではない
