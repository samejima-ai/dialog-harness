# コードのナレッジグラフ × ツールルーティング — DH メタスキル標準装備の前ブレスト

> L0 前ブレスト（未確定・仕様ではない）。開始 2026-09-05。
> 置き場: DH 標準（`.claude/skills/layer0-spec-architect/references/brainstorm-orchestration.md` §3）に従い
> `delivery/ANALYSIS-*.md`。先例 = `ANALYSIS-codebase-log-store-2026-09-03.md`（PR #238）。
> 本メモは節目ごとに追記する（途中で終わってよい・実装しない・SPEC / DONT / philosophy を書き換えない）。

## 問い

ひでさん（2026-09-05）:
「https://zenn.dev/helloworld/articles/bcaea69f58eae5 これは革新です。**DH メタスキルに標準装備したい**。
さらにこれに伴い **DH 自体のリファクタリングや点検も実施する**。L0 ブレストから始める」

AI 側の読み（訂正歓迎）:
- 「標準装備」= DH が配布するもの（`dh-manifest.yml` の overwrite / merge 分類のどこか）に載せ、
  新規・既存の全配布先が同じ手順で導入できる状態。個別プロジェクトに手で入れるのとは別
- 「メタスキル」= D4（`.claude/skills/` のマスタ定義）。ただし本件は skill（agent）でなく
  **tool（確定的・LLM 不使用）+ 配線規約（CLAUDE.md / .mcp.json）** の性質が強く、
  「skill にするか、rule + template にするか」自体が論点
- 「これに伴い点検」= 新機構を足す前に、足す先（GRAPH.yml / manifest / verifier / 規範メタデータ）が
  受け入れられる形か、既存の drift（VERSION 6.11.0 vs spec v6.16.0 等）を放置したまま積むのか、を見る

## 調べたこと

### F1. 記事の主張（一次: 記事本文）

- 週末ものづくり部「トークン2000分の1——オントロジー×ナレッジグラフでClaude Codeの推測を消す」2026-09-01。
  実装リポ https://github.com/shumatsumonobu/claude-cartography（MIT、★1、commit 1）
- 核心: **Claude Code は毎セッション、ファイルを読んで関係を推測し直している**。コード構造を事前に
  グラフ化して MCP 経由で渡し、推測を消す。配線は 3 ファイル = `CLAUDE.md`（質問の形 → ツールの
  ルーティング表）+ `.mcp.json`（バージョン固定）+ `.gitignore`（生成物除外）
- 著者実測: 全文読み 9,272〜142,188 tok → グラフ経由 **約 70 tok**（99.95% 減、6 コミット連続同値）。
  意味検索「トークンを検証する処理」→ `verifyToken`（類似度 0.52）。影響範囲 4 ファイル → 2 段先 22 ノード → 8 ファイル
- ルーティング表（記事 = 実装リポ CLAUDE.md）: 意味検索 / 影響範囲 / 呼び出し元 → better-code-review-graph、
  定義元・参照先・リネーム → Serena、全体構造・設計書横断 → `/graphify query`、レビュー / セキュリティ →
  better-code-review-graph。**code-review-graph は質問には使わない**（pre-commit 自動更新の役だけ）
- 記事自身が書く注意: 4 グラフに **4 つの更新経路**（自動 1 = pre-commit / 手動 3 = `graph build`+`embed` /
  `--update` / `serena project index`）、**古いグラフで動くと誤情報が蓄積**、Python 3.13 必須（3.14 でビルド失敗）、
  Windows 日本語環境で実行順序注意、VSCode 拡張セッションでは plugin 提供 MCP が読まれない（`.mcp.json` 直登録が確実）、
  Semgrep 内蔵ルールは SQLi / 秘密鍵 / eval を**全件すり抜け**

### F2. 4 OSS の一次情報（各 README、2026-09-05 観測）

| ツール | 実体 | 仕組み | LLM 呼出 | 更新 | 要件 | ★ / License |
|---|---|---|---|---|---|---|
| **code-review-graph** | https://github.com/tirth8205/code-review-graph | tree-sitter → SQLite（`.code-review-graph/`）。ノード = 関数/クラス/import、エッジ = call/継承/test coverage。**30 MCP tools**（`CRG_TOOLS` で絞れる） | 無し（embed は任意） | **pre-commit hook で自動**（SHA-256 差分のみ再パース） | Py 3.10+。Windows は `.exe` 直接（`cmd /c` 不要） | 31.2k / MIT |
| **better-code-review-graph** | https://github.com/n24q02m/better-code-review-graph | 上の fork。多語検索の AND 化・呼出解決・出力ページング。7 tools（`graph` `query` `review` `config` `security` `help` …）。埋め込み = **ONNX ローカル（Qwen3-Embedding-0.6B、初回 ~570MB DL）** or クラウド | 無し（埋め込みはローカルモデル） | **手動** `graph build` → `graph embed`。pre-commit 同梱なし | **Py 3.13 必須**、uv 必須 | 67 / Apache-2.0 |
| **Graphify** | https://github.com/safishamsi/graphify（PyPI 名 `graphifyy`） | コードは tree-sitter ローカル（37 文法）+ Leiden コミュニティ検出。出力 `graph.json` / `graph.html` / `GRAPH_REPORT.md` | **有り**: docs/PDF/画像の抽出・コミュニティ命名・`query`/`path`/`explain` 応答 | 手動 `--update`（増分）/ `--force` | Py 3.10+。`graphify install` が **CLAUDE.md directive + PreToolUse hook** を書く（既定 soft nudge、`--strict` で raw read を **block**）。Windows は symlink テストに Developer Mode | 115k / Apache-2.0 + MIT |
| **Serena** | https://github.com/oraios/serena | LSP 経由のシンボル操作（`find_symbol` / `find_referencing_symbols` / `rename_symbol` …）。40+ 言語 | 無し | 手動 `serena project index`（大規模変更後） | `uv tool install serena-agent` | 28.9k / MIT |

観測: 記事の「ontology」は **4 ツールの役割分担表（CLAUDE.md）** のことで、形式オントロジー（OWL 等）ではない。
**革新の実体は「ツール」より「ルーティング表 + バージョン固定 + 生成物除外の 3 点セット」**にある。

### F3. 第 5 の候補: codebase-memory-mcp（記事が引く dev.to 記事の実体）

- Martin Vogel「How I Cut My AI Coding Agent's Token Usage by 120x」2026-03-20。
  https://github.com/DeusData/codebase-memory-mcp（42.3k★、MIT）
- **単一バイナリ**（言語ランタイム不要）、tree-sitter 162 言語 + 12 言語で LSP 型解決、SQLite、
  **background watcher で自動同期**、15 tools、LLM 不要、Windows は PowerShell installer。SLSA L3 / Sigstore 署名
- 計測: 5 質問型合計 ~3,400 tok vs ~412,000 tok（121x）。Linux kernel 28M 行を 3 分で index
- → 記事の 4 本構成が抱える「4 更新経路・Python 3.13・570MB モデル DL」を **1 本・自動同期・ランタイム不要**で
  置き換えうる。ただし機能は「構造グラフ」に閉じ、Graphify の文書横断・Serena のシンボル編集は持たない

### F4. 反面教師（一次情報）

1. **Boris Cherny（Claude Code 創始者）**: 初期 Claude Code は RAG + ローカルベクタ DB を使っていたが
   agentic search の方が圧倒的に良く、単純で、セキュリティ・プライバシー・鮮度・信頼性の問題を避けられた。
   https://x.com/bcherny/status/2017824286489383315 （二次: https://zenn.dev/karamage/articles/2514cf04e0d1ac 2026-02-07）
   → 記事の手法は **Anthropic 本体が一度捨てた方向（事前索引）への回帰**である。違いは「ベクタ類似」でなく
   「構造グラフ（決定論）」を主にしている点。better-code-review-graph の意味検索部分だけは捨てられた側に近い
2. **code-review-graph 作者自身の CLAUDE.md**: 「**When the graph and the source disagree, the source wins.**
   The graph may be stale or may not model that relationship」+ 予算 **≤5 tool call / ≤800 tok** +
   「Never rely on graph output alone for non-trivial changes」。https://github.com/tirth8205/code-review-graph/blob/main/CLAUDE.md
   → 作者は「グラフは推測を消す」ではなく「グラフは索引、正本はソース」と運用している。記事の見出しより慎重
3. **MCP ツール定義のコンテキスト消費**: 1 tool あたり数百〜1,400 tok。code-review-graph 単体で 30 tools。
   Claude Code は v2.1.232+ で **tool search を既定化**（必要時のみ定義をロード）し、`MAX_MCP_OUTPUT_TOKENS` 既定 25,000。
   https://code.claude.com/docs/en/mcp → 「グラフで 70 tok」の裏で、ツール定義・discovery（~500〜2,000 tok/server）の
   固定費が乗る。記事の計測はこれを含んでいない（記事は質問 1 回の応答トークンを測っている）
4. **記事自身の保守負債**: 4 グラフ・4 更新経路、うち 3 つが手動。「古いグラフで動くと誤情報が蓄積」は著者の言。
   kakuman 生ログ停止事故（CHANGELOG 2026-06-18 / HANDOFF 06-16 で 2 ヶ月止まった = **書く先を増やすと止まる**）と同型
5. **Graphify の `--strict` hook**: PreToolUse でファイル検索 tool を **block** する。DH の hook 思想
   （`crosscut-hook-observer` = 観測専用・exit 0・block しない、philosophy 第 6 条）と正面衝突。既定 soft nudge でも
   「毎 tool call の前に 1 hook 実行」は購読量と遅延の固定費

### F5. DH の現状（実測 2026-09-05）

- 3 リポ（DH / kakuman / cc-cockpit）とも **`.mcp.json` 不在**。DH 内に MCP / ナレッジグラフ / オントロジーの先行議論は **無し**（grep 0 件）
- 最近傍の先例 = **`rtk-integration`**（外部 CLI で Bash 出力を 60-90% 圧縮 = 同じ「購読量削減」目的）。
  設計要素: バージョン固定（v0.37.1）/ install・uninstall の可逆性 / CLAUDE.md 追記テンプレ / 越境パッチはマーカー
  `<!-- rtk-integration: begin/end -->` で撤去可能 / 通知のみ・自動導入しない。**ただし Windows native 固定・prefix 無し・
  GRAPH.yml に載っていない**（nodes 30 = agent 16 / human 6 / tool 8 のどこにも無い）
- `dh-manifest.yml` の paths 分類（overwrite / merge / redeploy / never_touch）に **`.mcp.json` の行が無い**。
  `.gitignore` 追記・CLAUDE.md への追記（never_touch）も分類外
- `harness-verifier --strict` は 7 検査 PASS（README は「5 検証項目」と記載 = 文書 drift）。`check_template_sync` IN_SYNC
- `VERSION` = 6.11.0 のまま `dh-upgrades/` に v6.12.0〜v6.16.0 が存在（既知。前ブレスト F6 / 判断キット Q9-A で別 PR）
- Level A 配布性 checklist（`dev-env-spec.md` §Level A）: **E-1 外部ライブラリ依存ゼロ**（Python 標準 or 既存 stack のみ）/
  **E-3 OS 非依存（Linux/Mac/WSL）**。→ 記事の 4 本はすべて E-1 に触れ、配布先が Windows native である事実は
  E-3 の列挙（Linux/Mac/WSL）に **Windows が無い**という checklist 側の穴を露呈する（rtk が Windows 限定なのはこの逆）
- 規範メタデータ（`stage:` / `review_trigger:`）は **新規規範に必須**。純化 RL §10 では「効率型」規範は
  時限を付して常駐 = ツールルーティング表は効率型に該当しうる

### F6. 対象コードベースの形（一次: `git ls-files` 実測）

| リポ | tracked | ts/tsx | py | md | md bytes | ts bytes |
|---|---|---|---|---|---|---|
| dialog-harness | 354 | 0 | 31 | 268 | **3.7MB** | 0 |
| kakuman-platform-v3.0 | 1,683 | 840 | 12 | 408 | **10.3MB**（SPEC.md 1.4MB / CHANGELOG 0.9MB / INTENT 0.68MB） | 5.1MB |
| cc-cockpit | 387 | 130 | 4 | 181 | 2.5MB | 0.85MB |

→ **DH は文書コードベース**（tree-sitter 系の利得はほぼ無い）。kakuman は **md が ts の 2 倍**。
記事の手法が効く「コード側の推測読み」より、この 3 リポでは「**文書側の grep 到達**」の方が購読量の支配項。

### F7. DH / kakuman には既に「手書きオントロジー」と「手動ナレッジグラフ航法」がある

- DH: `GRAPH.yml`（実行グラフ nodes 30 / edges 42、G-1〜G-5 で機械検査）/ `harness-verifier/glossary.yml`（用語辞書）/
  `dh-manifest.yml`（境界宣言）= **ノード・エッジ・用語・境界**の 3 種が YAML で在り、`execution_graph.py` が整合を検査する
- kakuman `CLAUDE.md`: 「ルーティング表（領域ゲート）」= **触る領域 → gate ID → 罠 ID → SPEC アンカー → 検証**（18 行）。
  「巨大 docs は全文 Read しない。Grep でアンカー（`FX-XXX`）を特定してから部分読み」（L149）。
  lock-step センサー `lint:traps` / `lint:routing-gates` / `lint:test-reach`
- → 記事の「質問の形 → ツール」表と kakuman の「触る領域 → gate → 必読」表は **同じ形（ルーティング表）で対象が違う**
  （ツール選択 vs 規範到達）。DH の純化 RL §7 は後者を「ゲート強制 3 段があるときのみ許容」と規定済み

### F8. Claude Code 公式仕様で押さえる点（https://code.claude.com/docs/en/mcp）

- `.mcp.json` = project scope、**VCS に commit してチーム共有**が公式推奨。初回は trust dialog（`claude -p` 等の非対話では無確認）
- tool search 既定（v2.1.232+）、discovery cache 既定 on（v2.1.238+）
- Windows の stdio server は必要時 `cmd /c` で自動ラップ。`--` 区切り必須
- plugin 提供 MCP と `.mcp.json` は tool 名前空間が異なる（`mcp__plugin_<name>_<server>__<tool>` vs `mcp__<server>__<tool>`）。
  記事の「VSCode 拡張で plugin MCP が読まれない」は plugin 経路固有の問題で、`.mcp.json` 経路なら回避

### F10. Anthropic 公式の設計指針（一次: Effective context engineering for AI agents）

https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

- 取得戦略を **事前取得（embedding ベース）** と **just-in-time 取得（軽量な識別子 = ファイルパス・保存クエリ・
  リンクだけ持ち、実行時に tool で読む）** に分け、Claude Code は **ハイブリッド**: 「CLAUDE.md は素朴に前置き、
  glob / grep で just-in-time に読み、**古い索引の問題を回避**する」
- 「最もよく見る失敗モードの 1 つは、**機能を広く覆いすぎたり、どのツールを使うか曖昧な判断点を生む、肥大した
  ツールセット**」。ツールは自己完結・誤りに頑健・用途が極めて明確であること
- 「context は**限界効用が減る有限資源**」（context rot）
- 「フォルダ階層・命名規約・タイムスタンプは、人間にも agent にも、情報をいつどう使うかの重要な信号」
- → 記事の手法は Anthropic の指針と **部分的に整合**（識別子だけ持ち実行時に引く = グラフの ID 参照は just-in-time の一形）
  し、**部分的に衝突**（事前索引の鮮度 / 4 サーバ 40+ tools の「肥大したツールセット」/ ツール選択の曖昧点を
  CLAUDE.md の表で解消しようとしている点は、まさに指針が失敗モードと呼ぶ状態の対症療法）。
  「フォルダ階層・命名が信号」は kakuman の FX-* アンカー / 罠 ID / gate ID の設計と同じ主張（案 C の根拠）

### F9. 一次計測（scratchpad コピー上、リポ本体には書き込まない）

対象 = `git ls-files` で複製した cc-cockpit / kakuman（`.git` 初期化のみ）。ツール = `uvx --from code-review-graph==2.3.7`
（記事と同版、この環境は Python 3.11 / uv あり）。トークンは bytes/4 の概算。

| 計測 | cc-cockpit（ts 130） | kakuman（ts 840 + sql 189） |
|---|---|---|
| `build`（全量） | **2.8 s**、157 files、1,270 nodes / 14,607 edges | **8.3 s**、1,152 files、5,160 nodes / 44,994 edges |
| `update`（1 ファイル touch 後の増分） | **0.5 s** | **0.7 s** |
| `.code-review-graph/` サイズ | **26 MB** | **88 MB** |
| `architecture` 出力 | 3.2 KB ≈ **790 tok**（14 communities） | 2.8 KB ≈ **710 tok**（15 communities） |
| `search "validate task request"`（多語） | 2.1 KB ≈ 515 tok、`validateTaskRequest` を**正しく発見**（keyword mode） | — |
| `search "require admin employee"`（多語） | — | **0 件**（`requireAdmin` は存在する。多語 = 部分文字列 AND でない = fork が直した既知欠陥） |
| `communities` 出力（全 member 列挙） | **233 KB ≈ 58,000 tok** | **840 KB ≈ 210,000 tok** |
| `detect-changes` 出力 | 0.4 KB ≈ 100 tok。`context_savings: {estimated: true, saved_tokens: 60,646}` | 同 ≈ 100 tok。`saved_tokens: 211,655, estimated: true` |

読み取り（判定ではない）:
1. **鮮度維持は安価**: 全量 build が 10 秒未満、増分 1 秒未満。pre-commit に載せても開発体験を壊さない（記事の「手動更新 3 本」問題は
   ツール選定の問題であって原理的でない）
2. **「約 70 tok」は命令の選び方の話**: 絞った問い（`architecture` / `detect-changes` / 単語一致 `search`）は 100〜800 tok に収まるが、
   列挙系（`communities`）は **MAX_MCP_OUTPUT_TOKENS 既定 25,000 を 2〜8 倍超える**。MCP 経由なら切り詰められて情報が落ちる。
   ルーティング表に「使わない tool」を書くことの意味はここにある（= Anthropic 指針の「肥大ツールセット」対策の対症療法）
3. **記事の削減率の出所（推測・要確認）**: `detect-changes` が返す `saved_tokens` は `estimated: true` = ツールの自己申告推定値。
   記事の「全文読み 9,272〜142,188 tok」がこの推定由来なら、分母は実測でない。著者記事にはそこまで書かれていない
4. **コミュニティ検出は環境依存**: `igraph` 不在で「directory-based」に退化（kakuman は `apps/platform` 3,108 nodes が 1 community）。
   この状態の `architecture` は `ls -R` の要約と大差ない。Python 依存の追加（igraph）で改善するが E-1 からさらに遠のく
5. **DB は commit 不可サイズ**（26〜88 MB）。`.gitignore` 必須は記事どおり。マシンごとに build する運用 = 「生 = ローカル、蒸留 = commit」
   の既存規範（hook-observations / v6.16.0 I-4）と同型
6. 「関数名が不明でも見つかる」（記事の意味検索）は **埋め込み前提**（better-code-review-graph の 570 MB モデル or code-review-graph の
   `embed`）。埋め込み無しの keyword mode では grep と同じ限界に戻る（kakuman の 0 件がその実例）

## 選択肢（暫定・Workflow の 3 独立設計 + 反証結果で更新予定）

| 案 | 内容 | 成立条件 | 代償 | 反面教師 |
|---|---|---|---|---|
| **A. 最小（rule + template）** | DH は skill を作らず、`templates/rules/common/tool-routing.rules.md`（質問の形 → ツール表の書き方 + 「ソースが勝つ」+ 予算）と `.mcp.json` 雛形（バージョン固定）を配布。導入は L0 対話で選ぶ。ツールは 1 本から | manifest に `.mcp.json` の分類を 1 行足す。純化 RL §10 効率型として時限メタデータを付す | 導入・鮮度維持は各プロジェクトの手作業。「標準装備」というより「標準の書き方」 | Boris Cherny（索引は鮮度で腐る）— 手動更新 3 本を DH が推奨すると腐敗を配布することになる |
| **B. skill 化（rtk 同型）** | `crosscut-code-graph`（仮）: install / uninstall / 鮮度検査 / CLAUDE.md 配線（マーカー撤去可）/ verify。GRAPH.yml に tool node、manifest に `.mcp.json` 分類、upgrade-spec 起草 | Level A checklist E-1/E-3 の読み替え（外部 CLI 依存を許す条件を明文化）。Windows native で動くこと | skill 1 本 + 規範 4 箇所（GRAPH / manifest / verifier / dev-env-spec）が増える。rtk と同じく「導入 skill」が **導入後に読まれない**（使用中は tool の側）| rtk-integration 自身: GRAPH.yml 未登録・Windows 固定・E-3 不整合のまま常駐 = 先例が既に規範外 |
| **C. DH 固有（文書オントロジー先行）** | tree-sitter より先に、GRAPH.yml / glossary / manifest / 罠 ID / gate ID / SPEC アンカーを**機械問い合わせ可能**にする決定論スクリプト（LLM 不使用、第 2 条）。「このパスを触るとき読む節はどこか」を 1 コマンドで返す。コードグラフは第 2 段で配布先が選ぶ | 既存 YAML 3 本 + kakuman の lint:* が既に材料。新規外部依存ゼロ（E-1 充足） | 記事の「革新」（コード側）を直接は取り込まない。手書きオントロジーの保守は人間（増えると止まる） | kakuman 生ログ停止（書く先を増やすと止まる）— 索引の手書き層を増やすと同じ末路 |
| **D. 観測登録のみ（今は入れない）** | `observed-peers.md` に 5 ツールを観測事例として登録し、Claude Code 本体の tool search / 公式機能の進化を待つ。配布先が個別に試すのは自由 | 無し | 記事の効果を DH 配布先で得られない。「革新」を見送る判断の説明責任 | Anthropic 自身が「agentic search で足りる」と結論した側の事実 |
| **E. 配布先個別導入（DH は触らない）** | kakuman だけ `.mcp.json` + CLAUDE.md 1 行で試す。DH には結果を upstream-scan で還流 | dh-manifest upstream U-5「還流するのは機構でなく出来事」に従い、事故 or 効果の記録を持って DH に上げる | 標準装備にならない（が、DH の v7 逆流路の設計思想には最も忠実） | — |

## いま出ている案

（Workflow の 3 独立設計 + 反証を待ってから記述。推奨は書くが決定は書かない）

## 未解決の論点

- U-1 「メタスキルに標準装備」の実体は skill（agent）か tool + rule か。記事の中身は後者
- U-2 記事の 4 本構成を標準にするか、1 本（codebase-memory-mcp / code-review-graph）から始めるか
- U-3 `.mcp.json` の manifest 分類（merge が近いが、バージョン固定値を DH が持つなら overwrite 寄り。配布先固有 server が混ざる前提なら merge）
- U-4 Level A checklist E-1 / E-3 と「外部 CLI 依存・Windows native」の整合（rtk が既に逸脱している）
- U-5 記事のルーティング表（ツール選択）を CLAUDE.md に置くと純化 RL §3 到達可能性基準で常駐に値するか（効率型 → §10 で時限付き常駐か、rules テンプレへ）
- U-6 DH 自身（文書コードベース）には何が効くのか。コードグラフは効かない。文書側は Graphify（LLM 呼出）か案 C か
- U-7 グラフ鮮度の担保: pre-commit（code-review-graph）/ watcher（codebase-memory-mcp）/ 手動（他）。純化 RL §9「CI にしか無い検査を作らない」との整合
- U-8 hook 思想: Graphify の PreToolUse nudge/block を DH は許容するか（第 6 条 block 禁止と衝突）
- U-9 前ブレスト U-7 と同じ: DH のブレスト置き場（`delivery/ANALYSIS-*`）と kakuman の `docs/brainstorm/` の二重規範

## ブレスト決定

（人間が「これで行く」と言ったことだけ書く。現時点なし）

## 次にやるなら

- Workflow 結果（DH 点検所見 + 3 設計案 + 反証）を本メモ §DH 点検 / §選択肢 に反映
- F9 一次計測の結果を追記
- 論点が出揃ったら「L0 に上げられそうです」と 1 回だけ提案する（人間の明示指示があるまで L0 へ上げない）
