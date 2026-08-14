# ANALYSIS: エージェントチーム・オーケストレーション導入の設計材料 — L0 前ブレスト成果

> **本文書はブレスト成果（判断材料）である。仕様変更ではない。**
> SPEC 化・規範への反映は L0 spec-architect 対話で行う（escalation-matrix「規範文書改変」行に従い、
> 実装前 Council 諮問 + 献上時人間判定の対象）。決定は D5。

| 項目 | 内容 |
|---|---|
| 起点 | ひでさん「L0 前ブレストを開始する。DH にエージェントチームによるオーケストレーションを導入する。SNS で最新情報をキャッチアップして DH に合う、私好みの物を選びたい」（2026-08-14） |
| 手法 | Web/SNS リサーチ（2026-08 時点の英語圏・日本語圏）＋ DH 選好軸との突合 ＋ ブレスト内の人間選択 |
| ブレスト決定 | **主軸 = Workflow 背骨 + Agent Teams 限定併用** / **導入層 = Council・review 基盤、L2 orchestrator 実装体、L0 ブレスト対話支援**（並列 L1 worktree は温存・観測駆動） |

---

## 1. 地形図（2026-08 時点）

「マルチエージェント」は 3 階層 + 2 外部系統に分化した。

### Claude Code ネイティブ 3 階層

| 階層 | 実体 | 制御フロー | DH 現在地 |
|---|---|---|---|
| Subagents | 単一セッション内・結果のみ報告 | モデル駆動 | **導入済み**（leaf workers / Council 3 ペルソナ / review workers） |
| Agent Teams | 独立インスタンス群。リード + チームメイトが共有タスクリスト + Mailbox で直接通信 | モデル駆動 | 未導入 |
| Workflow | スクリプトが制御フローを保持し各ステップをサブエージェントへ委譲 | **決定論** | 未導入 |

**Agent Teams**（v2.1.32、`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`）の要点:

- 協調機構は**全部ローカルファイル**（`~/.claude/teams/{team}/config.json`・`~/.claude/tasks/{team}/` の JSON、ファイルロック競合防止）。cat/grep/jq で観測可能・中央サーバーなし
- チームメイト同士がリード非経由で直接メッセージ可。**人間もチームメイトへ直接割り込める**（Shift+Up/Down 監視・直接指示）— subagent の 3 課題（不透明・割り込み不可・多役割協調不能）への回答
- 設計思想は Orchestrator-Workers / Parallelization / Evaluator-Optimizer の統合（Anthropic「Building a C compiler」系譜）
- 制約: **Research Preview**（破壊的変更あり）・**セッション再開不可**・トークンはチームメイト数に比例・Pro プランではレート制限に頻発、実質 Max 前提

**Workflow** の要点:

- `agent()` / `parallel()` / `pipeline()`、JSON schema による構造化出力強制、journal による再開キャッシュ。`Date.now()` すら禁止する決定論の徹底
- コンテキスト経済: スクリプトが計画を保持するためメインコンテキストは最終結果のみを見る → 数百エージェント規模までスケール
- 定石化した品質パターン: **敵対的検証**（懐疑論者を複数当て反論させ生存主張のみ報告）・**判事パネル**・**多角的視点検証** — **DH が Council / falsification-protocol として手書きしてきた思想と同型**

### 外部系統

- 外部オーケストレーター（Gas Town / Claude Squad / Conductor / Vibe Kanban / DevSwarm 等 9 種前後）: 共通プリミティブは **git worktree 分離**（2026-08 に複数 CLI が同週標準化、「並列 1 体 = 1 worktree」がテーブルステークス化）。Gas Town は API 課金 $200+/月の報告
- 汎用フレームワーク（LangGraph / CrewAI / AG2 / OpenAI Agents SDK）: 別実装スタック + API 課金の世界。LangGraph が企業本番の主流

### 反面教師（SNS 撤退談）

tmux 階層オーケストレーション（親分/若頭/若衆）自作者の撤退記: 「AI に仕事をさせるための仕組みの保守」自体が負債化 → Agent Teams リリースで自作機構が不要化 → 「サブエージェント + スキル整備」へ回帰。**自作オーケストレーション層は Claude Code 本体の進化に轢かれる**。

## 2. 選好軸の仮説（repo からの推定・ブレストで異論なし）

1. ローカル自律実行ファースト（CI にしか存在しない検査を作らない）
2. サブスク運用（API 従量課金を避ける、Pro/Max 枠内）
3. 人間主権と観測性（append-only ログ・ブラックボックス嫌い）
4. 情報純度（独立コンテキスト・相互参照禁止）
5. 決定論を好む（LLM 判定の排除・「満ちているが意味は空」への警戒）
6. 機構は増やすより減らす（時限化・観測駆動・「追加せず実測待ち」）

適合評価: Workflow ◎（軸 1/3/4/5 に全部合う）/ Agent Teams ◯（軸 1/3 に合うが軸 2/5 と緊張・実験的）/ 外部オーケストレーター △（worktree 分離のみ価値、保守負債が軸 6 に反する）/ 汎用フレームワーク ✕（別スタック + API 課金）。

## 3. ブレスト決定（2026-08-14・ひでさん選択）

- **主軸**: Workflow 背骨 + Agent Teams 限定併用 — 定型フロー（Council fan-out・review・反証 fan-out）は決定論 Workflow、議論が本体の場面（ブレスト・L2 跨ぎドメイン協調）だけ Agent Teams
- **導入層**（3 つ選択）: ① Council / review 基盤 ② L2 orchestrator 実装体 ③ L0 ブレスト・対話支援
- **温存**: 並列 L1（worktree 分離）は選択せず — 統合検証と分離規律の設計が先。観測駆動で再訪
- 論拠: DH は既にオーケストレーションの**設計図**（Council フェーズプロトコル・review OC+workers・L2 雛形）を規範として持つ。足りないのは**実行基盤**だけであり、設計図を外部ツールに合わせて書き換えるのではなく、設計図をそのまま写せる実行基盤を選ぶ

## 4. L0 対話へ持ち込む論点（SPEC 化すべき問い）

1. **Research Preview を規範が参照する形式**: Agent Teams は破壊的変更がありうる。SPEC は抽象契約（「議論型協調層」）のみ定義し、Teams 固有の設定・env は随時レイヤー（プロジェクト側・時限メタデータ付き）に置くか
2. **判定地図との整合**: オーケストレーターは**判定を持たない実行機構**に限定する明文化（final_decision null の維持・escalation-matrix との非衝突）。リード agent が「判定者」化する drift をどう検出するか
3. **コストガバナンス**: Max 枠内の並列度上限・チームメイト数の既定値・レート制限時の degrade 経路（Teams → subagent fallback）
4. **Workflow スクリプトの所有と置き場**: DH 規範（`.claude/skills/**` 配下の references？）か、`templates/` 配布物か、プロジェクト成果物か。規範化するなら escalation-matrix「規範文書改変」行の対象
5. **移行順序**: 最小リスクは Council 3 ペルソナ fan-out の Workflow 化（既存規範の実行基盤置換・挙動同一性を COUNCIL-LOG で検証可能）→ review パイプライン → 反証 fan-out → L2 実装体の順を仮案とする
6. **CTL との関係**: Workflow 化で Council 発動の摩擦が下がる → 発動数増 → CTL 蓄積加速の見込み。ログ記録経路（journal → COUNCIL-LOG 同期）の設計
7. **L1 独立検証の情報純度**: Workflow の journal・共有タスクリストが「実装コンテキスト隔離」を破らないか（reviewer が journal を読めてしまう構造の可否）

## 5. Sources

- [Shipyard: Multi-agent orchestration for Claude Code in 2026](https://shipyard.build/blog/claude-code-multi-agent/)（3 階層の整理）
- [The Prompt Shelf: Claude Code Multi-Agent Orchestration 6 Patterns](https://thepromptshelf.dev/blog/claude-code-multi-agent-orchestration-patterns-2026/)
- [alexop.dev: Claude Code Workflows — Deterministic Multi-Agent Orchestration](https://alexop.dev/posts/claude-code-workflows-deterministic-orchestration/)
- [Qiita: Claude Code の実装から読み解く Agent Teams の設計思想](https://qiita.com/Dinn/items/6c0dd5107d4ce6c4b300)
- [Zenn: Claude Code Agent Teams をどう使うか — サブエージェントの課題から考える](https://zenn.dev/storehero/articles/f21d49387577bb)
- [Zenn: Agent Teams の始め方 — Subagents との違いと注意点](https://zenn.dev/toono_f/articles/claude-code-agent-teams-guide)
- [Augment Code: 9 Open-Source Agent Orchestrators (2026)](https://www.augmentcode.com/tools/open-source-agent-orchestrators)
- [Digital Applied: Worktree Isolation Became Table Stakes for Agent CLIs](https://www.digitalapplied.com/blog/agent-cli-worktree-isolation-parallel-coding-agents)
- [QubitTool: 2026 AI Agent Framework Showdown](https://qubittool.com/blog/ai-agent-framework-comparison-2026)
- [claudecode.co.jp: なぜ私は Claude Code と AI オーケストレータを使わなくなったのか](https://claudecode.co.jp/info/claude-code-ai)（撤退談）
