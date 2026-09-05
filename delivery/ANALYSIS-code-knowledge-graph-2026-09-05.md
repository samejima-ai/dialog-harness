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
- 設計上の差（README 実読）: 出力に **pagination + token budget が組み込み**（`offset`/`limit`、「要求トークン × 4 byte」の決定論上限）
  = F10-7 の「影響範囲 10 万 tok」問題への構造的対策を持つ。索引は **repo 外** `~/.cache/codebase-memory-mcp/`（gitignore 不要）、
  任意で `.codebase-memory/graph.db.zst` を commit してチーム共有可。除外は `.gitignore` 階層 + `.cbmignore`。
  installer は `~/.claude.json` と project `.mcp.json` を**書き換える**（DH の hook 思想「自動導入しない」と要調整）。
  daemon がアカウント単位で常駐（最初のセッションが起動・最後が停止）
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

- 3 リポ（DH / kakuman / cc-cockpit）とも **`.mcp.json` 不在**。DH 内に **ナレッジグラフ / オントロジー / 記事の 4 ツール**の先行議論は **無し**
  （本メモ追加前の `master` = commit `982eae0` を対象に `\.mcp\.json|knowledge ?graph|ナレッジグラフ|オントロジー|serena|graphify` を grep、
  `history/archive/` 除外、2026-09-05 実測 0 件）。**訂正（同日・完全性批評 UV-08）**: 上記パターンに `MCP` の語が無かった。
  `mcp` 大小無視では 25 file 該当（gemini-review の GitHub MCP server 運用ログ / skill 内 COUNCIL-LOG の `ux4mcp`（UX MCP server 導入可否、
  主ログ未収録）/ `history/D0-METASKILL-DESIGN-DRAFT.md`「Align with MCP standards」等）。**MCP 一般の記録は有り、コードグラフ系の記録は無し**が正確
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
- tool search 既定（v2.1.232+）。**discovery cache の既定は要再確認**: 同日 2 回の公式 docs 取得で「既定 on（v2.1.238+）」と
  「既定 off・`MCP_DISCOVERY_CACHE=1` で有効化（段階展開で on の口座あり）」が食い違った（完全性批評 UV-04）。MCP 固定費の見積り前提に効く
- Windows の stdio server は必要時 `cmd /c` で自動ラップ。`--` 区切り必須
- plugin 提供 MCP と `.mcp.json` は tool 名前空間が異なる（`mcp__plugin_<name>_<server>__<tool>` vs `mcp__<server>__<tool>`）。
  記事の「VSCode 拡張で plugin MCP が読まれない」は plugin 経路固有の問題で、`.mcp.json` 経路なら回避

### F9. Anthropic 公式の設計指針（一次: Effective context engineering for AI agents）

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

### F10. 一次計測（scratchpad コピー上、リポ本体には書き込まない）

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
| `search requireAdmin`（単一識別子） | — | 2.5 KB ≈ 620 tok、3 定義を正しく列挙（`admin/actions.ts` / `lib/route-guards.ts` / `apps/master/_lib/auth.ts`） |
| `query callers_of requireAdmin` | — | 3.6 KB ≈ 890 tok、**曖昧性で再問い合わせ要求**（3 node 一致 → qualified_name 指定で再実行） |
| **`impact --files lib/route-guards.ts --depth 2`**（記事の中心機能） | — | **414 KB ≈ 103,000 tok**。272 nodes / 176 files が「影響」。同じ問いの grep 基準値: `grep -rn requireAdmin` = 46 files / 14 KB ≈ 3,600 tok |

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
7. **影響範囲は monorepo で逆転する**: 記事のサンプル（3 層構成の小さな API）では 4 ファイル → 22 ノードだったが、kakuman の
   認可ガード 1 ファイルでは 2 hop で 272 nodes / 176 files = **10 万 tok**。grep の 30 倍。code-review-graph 作者が
   「impact は deliberately conservative（recall 優先）」と書くとおりで、ハブ関数に対しては「読む量を減らす」でなく「読む量を増やす」
   道具になる。`--max-results` と `depth 1` の既定化、あるいは「差分ファイル → 影響 tests だけ」に問いを絞る運用規約が要る。
   **これは記事の「推測を消す」が monorepo の中心部では成立しないことの実測**であり、標準装備の可否を左右する

### F11. 記事・ツール側の追加事実（完全性批評 2026-09-05 が release 一覧 / pyproject から回収、本文は未読）

- **code-review-graph v2.3.8（2026-08-21）release note**: 「`watch` は 2.3.7 の最弱部で、**daemon が `ok` を返しながらグラフ更新が止まる**故障が 3 種あった」
  = 記事が `.mcp.json` で pin した **2.3.7 は無言 stale 故障を含む版**。「古いグラフは誤情報を蓄積」を記事自身の構成が抱えていた
- 上流の版追従速度: code-review-graph 2.3.4（05-25）→ 2.3.8（08-21）= 3 ヶ月 5 release。better-code-review-graph 3.21.0（記事）→ 3.24.0（現行）。
  「30 MCP tools」は版依存（v2.3.2 release は 28 → 30）。**DH の VERSION は 08-15 から凍結**（F5）— 配布 pin が上流に追随できるかは速度の問題
- code-review-graph 側も `~/.claude.json`（user scope）に書く（README「Configure `~/.claude.json` to execute the `.exe` directly」）。F3 の installer 書換は 2 ツール共通
- better-code-review-graph `pyproject.toml`: `requires-python = "==3.13.*"`、`litellm>=1.98.0`（1.83〜1.87 の security advisory を注記）、`semgrep<1.162`。
  **Python 版の三重不一致**: 利用者機 3.14.3（kakuman REGIME:1068）/ DH CI 3.11（harness-verify.yml:60）/ ツール要件 ==3.13.*
- 記事の削減率の分母: code-review-graph README は `context_savings` を「labelled as estimated」、検証 tokenizer は OpenAI `cl100k_base`（Claude tokenizer ではない）。
  F10-3 の推測を裏付ける方向（未確定）
- Boris Cherny 投稿の本文（2026-02-01、検索スニペット経由）: "Early versions of Claude Code used RAG + a local vector db, but we found pretty quickly that agentic
  search generally works better. It is also simpler and doesn't have the same issues around security, privacy, staleness, and reliability."
  返信スレッド（Daniel San「RAG + embeddings + AST + tree-sitter. The quality was excellent」x.com/dani_avila7/status/2018766464933613871）は未読 = 反証の反証が存在する
- Anthropic 第一者の代替: Claude Code の **LSP plugin**（`typescript-lsp` / `pyright-lsp`、「jump to definitions, find references, type errors」= Serena の第一者版、
  cloud session では起動しない）、costs docs「**Prefer CLI tools when available** … more context-efficient than MCP servers because they don't add any per-tool listing」
  「CLAUDE.md は 200 行未満、アーキテクチャ説明は skill へ」。DH / kakuman / cc-cockpit に `LSP|language server|code intelligence` の記述は 0 file

## DH 点検所見（Workflow `wf_1842b5a4-d85`、2026-09-05、29 エージェント / 所見 113 件 / 反証 12 件）

> 方法: 7 領域（skills / 宣言層 / 配布面・hooks / history・delivery / verifier・scripts / L0 規範 / 配布先 2 リポ）を並列精読 → 重複除去 →
> severity 上位 12 件を 2 レンズで反証（reproduce = 証拠 file:line の実在と導出妥当性 / intentional = 意図的決定の記録有無）。
> 反証者の既定は「確信できなければ refuted」ゆえ、**REFUTED の大半は「事実は成立・結論や枠づけが過大」型**で、訂正版を採用した。
> 未反証 101 件は「未検証」印で保持（journal: `subagents/workflows/wf_1842b5a4-d85/journal.jsonl`）。**すべて所見であって是正決定ではない**。

### 反証済み 12 件

| ID | 所見（訂正版） | 反証 | 本テーマとの関係 |
|---|---|---|---|
| **SK-03** | COUNCIL-LOG が二重管理かつ二方向分岐: `history/COUNCIL-LOG.md`（YAML、69 ID、正本宣言）と `.claude/skills/crosscut-council/history/COUNCIL-LOG.md`（見出し形式、21 ID、うち 12 は skill 内にしか無い、CTL 統計から脱落）。後者は「社外秘含み得るため skill 内に閉じる」と書きながら manifest overwrite で kakuman / cc-cockpit へ byte-identical 配布。kakuman 固有 Council 2 件が消失した実害あり。意図的決定の記録なし（design-history は「処遇確定を先送り」） | 生存（2/2） | **配布先固有の状態を skill dir 内に置く設計は不可**（3 案共通の前提）。「索引の二重管理は腐る」の DH 内実例 |
| **SK-06** | rtk-integration は外部 CLI をローカル導入して Claude Code に統合する唯一の先例。借りられる骨格 = 版 + SHA256 pin（空なら install 拒否、escape は env のみ）/ マーカー囲い + 正規表現撤去 / install 冪等 / uninstall 全撤去 / 版 bump の SHA 更新規約（Council rtkSHA）。**ただし** CLAUDE.md 配線は「現行スキルはそこまで管理しない」と追随放棄、対象は `~/.claude/skills/`（user scope）、Windows 固定 | 訂正採用 | KG skill の雛形になるが、書込先と OS の前提は真似られない |
| **SK-07** | rtk で真似すべきでない点は 4 + 1 に縮む: (a) user-scope 固定で DH の project-scope 配布と経路不一致（配布先では `SKILL.md:59` のコマンドが解決しない）(b′) 越境パッチは sync の届かない場所に着地し「DH 更新に一切追従しない残留物」になる（3 リポとも marker 0 件 = 未適用）(c′) `rtk init -g` はコマンドを**リライトする非観測 hook**で、DH 横断規範「hook は warn-only」に対する既存の逸脱先例 (d) CLAUDE.md 追記の追随放棄 (e) 「CLAUDE.md 不変ルール #7」参照先不在 | 訂正採用 | Graphify 型 block hook を「先例がある」と正当化する経路を塞ぐ材料 |
| **DECL-01** | GRAPH.yml agent 16 に対し skill 実体 20。未掲載 4 本（hook-observer / continuous-learning / verifier-philosophy / rtk-integration）は G-5 の `startswith(("layer","crosscut"))` + `continue` で計数されず走査対象外、「実体 ⊆ 宣言」を検査する経路が無い。**既知**（`DIAGNOSIS-loop-graph-engineering-2026-08-26.html:540-544` に記録済み、是正決定なし）。glossary.py も同じ prefix フィルタで rtk を黙って対象外 | 部分（意図性なし・骨格維持） | 「実行グラフの単一情報源」が既に実体と食い違う = **手書きオントロジーの drift 実例** |
| **DECL-05** | `dh-manifest.yml` は `.mcp.json` / `.gitignore` / `.claude/agents/` を 4 分類のどこにも置かず、:51 の既定規則で never_touch。DH が版固定 `.mcp.json` を配ると **初回 pin が更新経路を持たずに凍結**。同型 drift 現存: cc-cockpit は `.claude/agents/` を「DH 所有」と自己申告、DH は known-gaps G-003 に登録済み | 生存 | U-3 の核心。案 A は「凍結を仕様化」、案 B は merge 1 行、案 C は第 1 段で触らない |
| **DECL-06** | `.mcp.json` の分類候補は 5 通り（overwrite / merge / redeploy / never_touch / 雛形 overwrite + 実体 never_touch）。**merge が最近傍**（settings.json 同型、v6.16.0 F6-1 `logs/index.yml` 先例）。「kakuman は Sentry MCP 接続済み」は DH テンプレ例文の誤読（リポ内に MCP 宣言なし、将来仮定の論） | 訂正採用 | U-3 の選択肢 |
| **DECL-10** | VERSION は 2026-08-15（6.11.0）で不変。以後 GRAPH.yml（自身の `version: "6.12.0"` と食い違う）/ pr-audit / signal-scan / council-performance / harness-benchmark が昇格なしで master へ。CHANGELOG は #188〜#209 の見出しごと不在。**VERSION を上げる契機の規則が DH に無い**。据え置きの決定記録なし（Q9-A「別 PR で先に」は選択済・未着手） | 生存（2/2） | 新 upgrade-spec を積む案 B / C は drift の上に 1 段積む |
| **DECL-11** | upgrade-spec の「状態:」header が実態と食い違う: v6.11.0（header のみ古い）/ v6.12.0（header と §履歴の両方が「判定待ち」のまま実装済み）/ v6.15.0（F1・F4・F5 実装済み未記録）。v6.13 / 14 / 16 は起草のみ（一致）。**状態行の更新規則が存在しない**（spec 改訂 PR では更新・実装 PR では非更新） | 生存（2/2） | 同上 |
| **DECL-14** | UPDATE.md §2(a) `rm -rf .claude/skills && cp -r` を文字どおり実行すると kakuman の固有 skill 7 dir が消える。kakuman は同期 #6〜#13 一貫して「選択同期」（記録済みの回避策）。drift の所在は DH 宣言層: v5.0.0「Level B は同じ `.claude/skills/` に命名規則で同居」と v5.21.0「overwrite はディレクトリごと置換」が**別々に意図的に確定し、調停記録なし**。prefix 無し `rtk-integration` は prefix allowlist を破る | 生存（2/2） | 案 B / C の新 skill dir は**人間が同期対象に足さないと届かない** |
| **TP-01** | 純化 RL: 効率型規範の常駐は §10 で「§1① 枠 + 時限メタデータ」だが、時限は **SHOULD**（§10 は MUST 外、dev-env-spec は「任意メタデータ」、欠落センサー無し、配布先採用 0 件）。最近傍先例 G-AGENT は Council f5fc45 で**生成規格から凍結（非常駐・任意採用・実測待ち）**。→ DH 既定の出発点は「**非常駐**（rules テンプレ / skill references 所有 + 再評価条件）」、常駐は M2 以上の裁量で §1① + 時限 + add-demote-check が条件 | 訂正採用 | U-5 の答えの骨格。kakuman CLAUDE.md は 28,660 B で §8 WARN 超（FAIL まで 4,108 B） |
| **TP-02** | 「質問の形 → ツール」行は diff から機械検出できず段 3 の検出力ゼロ、だが「構造的に不成立」ではなく **G-UX-SNS 先例と同じ扱い**（kakuman は `GATE_PATTERNS: []` で表に置き「段 2 自己申告 + 独立レビューで担保」と明文化済み）。hook-observer が tool 名を記録しており新型センサーの入力は既にある | 訂正採用 | ルーティング表へ載せる選択肢は残る（検出力の性質を明記すれば） |
| **TP-03** | Graphify `install` の**既定書込先は `~/.claude/`**（user profile）。プロジェクト CLAUDE.md（never_touch・純化 RL 対象）に書くのは `--project` 時のみ。`graphify uninstall` は存在。実際の manifest 衝突は `--project` が書く `.claude/skills/graphify/`（overwrite = rsync --delete で DH 更新時に消失）と `.claude/settings.json`（merge） | 訂正採用 | F4-5 の「正面衝突」は条件付きに弱める。衝突の実体は skills dir と settings.json |

### 未反証の主要所見（high / 抜粋。全 101 件は journal）

**テーマ直結**
- **HV-04**: GRAPH.yml は `layer0-spec-architect → council-performance / harness-benchmark` の edge を `source: ritual-protocol.md` で宣言するが、同文書が呼ぶのは
  council-log-sync と council-axis-audit のみ。G-2 は source の**パス存在**しか見ないため PASS を通過 = **DH の手書きグラフで「古いグラフの誤情報蓄積」が既に起きている**
- **TP-05**: `templates/rules/common/` の 6 RL は 3 リポで md5 一致で**届いている**が、L1 読込順序（`layer1-autonomous-dev/SKILL.md:107-115`）に無く、
  純化 RL §5 の `.dh/rules/common/` も `.claude/rules/` も 3 リポとも不在、CLAUDE.md からの参照も無し = **届くが購読配線が無い**。案 A の隠れた前提
- **L0R-07**: dev-env-spec「コンテキスト注入戦略」は強制 2 チャネル（CLAUDE.md + INDEX.md）しかモデル化せず、**MCP tool 定義（1 tool 550〜1,400 tok の常駐）という第 3 の強制注入チャネルが規格外**
- **L0R-02**: 第 3 条「サブエージェント追加 4 基準」は Council ux4mcp（2026-05-29）で MCP 導入判断に借用済み。ただし基準 4「独立コンテキスト必然性」は MCP に翻訳不能
- **L0R-03**: 「メタスキルに標準装備」= `.claude/skills/**` の規範改変 → escalation-matrix「規範文書改変」行で**実装前 Council 諮問 + 献上時人間判定**、第 8 条の 3 段階自己宣言を frontmatter に要する。利用者の一文は着手承認であって内容確定ではない
- **L0R-09 / TP-17**: Level A checklist E-1（外部ライブラリ依存ゼロ）に記事の 4 本は全面抵触、E-3（Linux/Mac/WSL）は Windows native を列挙しない。rtk が既に逸脱常駐
- **DP-08**: kakuman の**エッジ（アンカー参照）は未検査**: SPEC 内部リンク 439 本 / 105 種のうち 8 が `<a id>` に未解決（F1-2 / F1-5 / FX-2 / FX-R / FX-T …）、
  CLAUDE.md ルーティング表「必読」21 参照のうち 9 が anchor 無し（見出し grep 到達のみ）、10 が複数候補（FX-NOTIF 6 / F4-8 17 / FX-M 7）
- **DP-09 / DP-02**: SPEC.md 1,407,185 B = `check-spec-size` FAIL 閾値の 98.2%（WARN 超過済）、CLAUDE.md 自己申告「約 119 万 byte」は +18% で **WARN 実発火中**。
  CLAUDE.md 28,660 B（WARN 20KB 超、400 B 超 18 行）= 手書き数値は書いた瞬間から腐る、の実例
- **DP-12**: pre-commit 基盤（husky / lefthook / lint-staged）は両配布先の package.json に無し。kakuman は Actions repo 無効（required = Vercel のみ）→ グラフ自動更新の足場が無い
- **HD-10 / HD-11**: DH の代謝思想（購読量最小化・薄い索引 → 名指し Read）は KG の目的関数と一致。context-circulation-theory は「圧縮 ≠ 結晶化」「生ログへのベクトル検索は筋が悪い」
  「HOT 常駐 ⇄ 索引境界は未決」と位置づけ、tree-sitter 構造索引は「第 3 の型」で未整理

**点検のみ（DH 自体のリファクタ候補）**
- **HD-01 / HD-02**: 情報代謝が **2026-06-07 で停止**（cursor 未前進、未消化 WARM ≈ 2,417 行、`dry_run_remaining` 未減算）。SUMMARY「直近 cycle 振り返り」は 08-05 で止まり CHANGELOG 9 件 / COUNCIL 12 件が未反映
- **HD-06**: `delivery/` 33 エントリ中 dev-env-spec 配置規則に適合する名前は 5 件のみ（ANALYSIS- / DECISION-KIT- / PROPOSAL- / PLAN- / DIAGNOSIS- 28 件が規則外。規則側が実運用に遅れている）
- **HD-09**: INTENT の (in progress) 7 見出しのうち v6.0.0 / v5.9.0 は CHANGELOG で released 済み
- **HD-16**: `history/project-derived-councils/kakuman` は 2026-05-12 のスナップショット（約 85 件遅れ）
- **HV-01 / HV-02 / HV-03**: harness-verifier「5 検証項目」vs 実装 7 が README / docstring / HUMAN-PROTOCOL / BOUNDARY / gemini-review ×2 の 6 箇所。G-5「WARN 止まり」設計は `--strict` CI で FAIL 昇格
- **HV-05**: scripts 10 本のうち test / GRAPH / workflow / skill の 4 経路が揃うのは signal-scan のみ。reviewer-misjudgment.py は完全孤児で `harness-verifier/reports` へ越境書込
- **HV-08**: glossary.yml に「ナレッジグラフ / MCP / オントロジー / ルーティング表」無し、第 1〜6 条止まり（第 7〜9 条は未収録）、`dev_modes.github_autonomous` 旧語
- **SK-02 / SK-08 / SK-09**: description の版番号 drift（verifier-philosophy「v5.1.0 で本実装」を 5 skill が引用、orchestrator は Opus 4.7 と Opus 5 混在）。verifier-philosophy は 6 回後送で凍結 / 廃止決定なし
- **SK-10**: 配布先 60 SKILL.md 全件 `dimension: D4`（D3 区別が機能していない）
- **TP-14 / TP-06**: workflow テンプレが 2 系統並存（`templates/.github/workflows/` 10 本 raw と `templates/github-workflows/` 6 本 .template）、rules README 索引は 6 本中 4 本
- **TP-12**: kakuman に `.claude/agents/` 未配布（3 リポ中最大のコードベースが leaf worker 無し）
- **DP-18**: kakuman settings.json permissions に旧 `council/history` パスが残存
- **運用（本セッションで実測）**: repository secret `GH_REVIEW_PAT` 失効で auto-merge `evaluate` が全 PR で red（`check_pat` は存在のみ検査し有効性を見ない → 「skip で red にしない」設計が破れる）。
  `gemini-review.yml` は 2026-05-09 以降 **4 ヶ月未起動**（paths に `delivery/**` を含むのに以後の delivery PR で走っていない）= auto-merge 条件 4.5 は実質 harness-verify のみで成立

## 設計 3 案の比較（独立設計 → 統合者の比較表を要約。判定ではない）

| 案 | 中身 | 最初に詰む場所 | philosophy 緊張 | 最小実験 |
|---|---|---|---|---|
| **A. tool-routing RL + `.mcp.json` 雛形**（skill 無し・1 本・L0 の 1 問） | `templates/rules/common/tool-routing.rules.md`（効率型・時限メタ）+ `templates/mcp/.mcp.json.template`（1 server・版固定・`CRG_TOOLS` で ≤8 tools）+ dialog-questions に 1 問 + 配布先 CLAUDE.md 0〜1 行（人間） | **RL の読込経路が現状不成立**（TP-05）。7 本目の RL を置いても読まれず購読量は 1 tok も減らない。直すと既存 6 RL も初めて配線され「最小」でなくなる | 第 2 条 tension（鮮度・予算を規約 = 推論で守らせる）、第 6 条は `enabledMcpjsonServers` 明示が条件（非対話で無確認起動） | Step0 hook-observations で Read/Grep 基線（現状 3 リポとも実データ 0）→ 代表 5 問 A/B → 損益分岐 k* = 固定費 ÷ (A−B)。**表だけ与えた場合の効果がゼロなら案の存在意義が消える** |
| **B. `crosscut-code-graph` skill**（rtk 同型・1 本 + tool-agnostic profile） | SKILL.md + stdlib installer / uninstaller / 決定論 verify（版固定・stale・CLAUDE.md 行 lock-step）+ profile 2 種（code-review-graph / codebase-memory-mcp）+ manifest `merge` に `.mcp.json` + GRAPH 2 node 3 edge + Level A **E-4「外部 CLI 許容条件」**新設 + upgrade-spec v6.17.0 | **保守負債と配布経路**: 規範 7 箇所増を既知 drift（DECL-01/05/10/11）の上に積む。kakuman は選択同期ゆえ新 skill dir は人間が足さないと届かない（DECL-14）。次に第 3 条: F10-7 で純度が逆転 | 第 7 条 tension（人間直呼びが主 = G-5 圏外）、第 9 条 tension（公式 installer の `~/.claude.json` 書換）、**manifest U-5 と向きが逆**（事故前に DH から機構を下ろす） | 10 問 A/B（profile 既定 ≤8 tools・depth1・communities 非公開）で正答率 / 実 `/cost` / 予算超過 / stale 誤答 + `.mcp.json` 有無 × 30/8 tools の開始直後 context。**Windows 根拠が 3 案中最も薄い**（hook 実走証拠は sandbox 生成の 2 行のみ） |
| **C. 規範グラフ（norm-graph）**（手書き ID 体系の決定論導出・stateless） | `crosscut-norm-graph/scripts/norm_graph.py`（stdlib・LLM 不使用）`where <ID>` / `refs <ID>` / `check`。抽出規約は配布先 REGIME.md 宣言（script に regex を埋めない）。**永続化しない**（kakuman 1.75 MB を 29 ms で導出・実測、DH 2 ms）。kakuman の check-traps-sync 4 不変条件 + check-routing-gates + check-spec-size を 1 検査器に一般化。コードグラフは第 2 段で配布先が選ぶ | **宣言側の置き場と人間ゲート直列**（第 6 条）: REGIME.md（never_touch）に置くと cc-cockpit のように bullet ID しか無いリポは既定値無しで動かない、skill 内 config は overwrite で消える、`.dh/` は 3 リポとも不在。必読列 anchor ID 化 = L-GATE-HARNESS | 第 2・9 条は 3 案中最も fits（決定論・原状回復対象すら無し）。第 3 条 tension（description 常駐 +1）。**純化 RL §6 の留保**（常駐 → 随時に進化すれば純化論の土台が崩れる）を現実化する装置 = 効果が出れば純化 RL 自身の再諮問条件 | ≤200 行プロトタイプを stdout のみで 3 リポへ（**一部実測済み**: kakuman nodes 1,429 / edges 306 / 29 ms、INDEX→SPEC 61/61 解決、必読 21 ID 中 10 が複数候補、`where G-NOTIF.必読` 応答 45 B）+ check-traps-sync parity + Windows 起動 <1 s / cp932 |

**全案共通の前提（反証を生き残った所見から）**: ① 配布先固有の状態を skill dir 内に置く設計は不可（SK-03）② kakuman は選択同期（DECL-14）③ `.mcp.json` は未分類 = 既定 never_touch（DECL-05）
④ GRAPH.yml は実体 → 宣言方向の検査を持たない（DECL-01）⑤ VERSION / 状態行 drift（DECL-10 / 11）の上に spec を積む。

**案をまたいで取り込める部品**: 「グラフとソースが食い違えばソースが勝つ + 予算 ≤5 call / ≤800 tok」の 1 行（3 案とも同一物、常駐は罠索引型 1 行・実体は RL）/
tool-routing.rules.md は A・B 共有、C の norm-graph.rules.md と 1 本に統合可 / RL 現況リストの SSOT 一本化 + 件数一致センサー（独立 PR 可）/
「宣言側に判定・regex を置く」規律（dh-manifest U-4 と同型）/ hook で block・nudge しない不変条件 / Windows 共通部品（`python3 || python`、`PYTHONUTF8=1`、導入時手動 smoke）/
E-3 への Windows native 追記は 3 案とも要求 → 規範文書改変ゆえ**独立 PR + Council 諮問で先に** / 案 E（kakuman 個別導入 → upstream 還流）を A/B/C の前段に置くと U-5 に整合。

## 選択肢（更新版）

| 案 | 内容 | 成立条件 | 代償 | 反面教師 |
|---|---|---|---|---|
| **A. 最小（rule + 雛形）** | 上表 | RL 読込経路の修理（DH 側 L1 SKILL.md か配布先 CLAUDE.md 1 行）| 自動化ゼロ・書く先 4〜5 箇所増・センサー無し | 「書く先を増やすと止まる」— 同型が DH 内で進行中（RL 現況 2 箇所 stale） |
| **B. skill 化（rtk 同型）** | 上表 | Level A E-4 新設（Council）/ Windows 実走証拠 / 自動鮮度 | 規範 7 箇所増・導入後に読まれない skill・DH 自身で dogfood 不可 | rtk 自身（規範外常駐）/ Boris Cherny（回避しない） |
| **C. 規範グラフ先行** | 上表 | 抽出規約の置き場（REGIME ブロック）/ 必読列 anchor ID 化（人間） | 規範 4〜5 箇所増・意味検索を捨てる・記事のコード側は第 1 段で取り込まない | kakuman 手書きメタデータ乖離（今日も WARN 発火）— 永続グラフを作れば 5 枚目の手書き地図 |
| **D. 観測登録のみ** | `observed-peers.md` に登録し公式機能（tool search / LSP plugin）の進化を待つ | 無し | 記事の効果を見送る説明責任 | Anthropic 自身の結論 |
| **E. 配布先個別導入** | kakuman だけ 1 本 + CLAUDE.md 1 行で試し、事故 or 効果の記録を upstream-scan で DH へ | U-5「還流するのは出来事」に従う | 標準装備にならない（v7 逆流路には最も忠実） | — |
| **F. CLI 経路（非 MCP）**（新・完全性批評 MM-06） | code-review-graph 等を **Bash から CLI で呼ぶ**（F10 の一次計測と同じ経路）。`.mcp.json` 分類・tool 定義常駐・承認プロンプト・plugin 名前空間の問題が全て消える | Bash allow（kakuman settings.json 型）/ rtk 同型の Windows・SHA 問題を引き継ぐ | 出力サイズ制御を呼び手が担う（`--max-results` / depth）/ Claude が「使う」判断は規約依存 | Anthropic costs docs「Prefer CLI tools when available」が根拠側。rtk 先例が既存 |
| **G. 第一者 LSP plugin**（新・MM-04） | Claude Code 公式 `typescript-lsp` / `pyright-lsp`（定義 / 参照 / 型診断 = Serena の機能重複部分） | plugin 経路（cloud session では起動しない）/ `typescript-language-server` は両配布先 package.json に無し | 構造グラフ（影響範囲・コミュニティ）は持たない | — |
| **H. サブエージェント scoped MCP**（新・MM-07） | KG server を `explore-worker` の frontmatter `mcpServers:` に閉じ、main context の tool 定義費を 0 にする | kakuman に `.claude/agents/` を配布（TP-12 解消が先）/ worker に「ソースが勝つ」規律追記 | worker 経由の間接化 | — |

## いま出ている案（推奨であって決定ではない。選好軸の仮説を明示）

選好軸（訂正歓迎）: ①購読量（実際に読む量）の削減 ②鮮度が腐らない ③DH の既存負債を増やさない ④Windows native で動く ⑤人間最終承認・観測専用 hook を崩さない。

1. **「標準装備」の実体は 4 ツールではなく 3 点**: 「グラフとソースが食い違えばソースが勝つ + 予算」の 1 行 / 1 本・版固定・**自動鮮度**のツール /
   使わない tool の列挙。記事の 4 本構成（4 更新経路、Py3.13、570 MB、LLM 呼出）は DH が配布しない。理由 = F4-2（作者自身の運用）、F10-2/7、F11（2.3.7 の無言 stale 故障）
2. **順序は E → (F or A) → C の実測 → B の判断**。DH から先に機構を下ろす（B）のは manifest U-5「還流するのは機構でなく出来事」と向きが逆。
   kakuman で 1 本を **CLI 経路（F）**か `.mcp.json` 1 server で試し、hook-observations の Read/Grep 基線（現状 0 件）と A/B の一次計測を「出来事」として持って DH に上げる。
   F を先に挙げる理由: MCP tool 定義の常駐費・`.mcp.json` 分類・非対話無確認ロード（U-20）の 3 論点が消え、rtk と同型で DH に前例がある
3. **案 C は DH の形に最も合う**（DH は文書コードベース、購読量の支配項は SPEC / 罠 / gate の航法、29 ms 実測、stateless で鮮度問題が構造的に無い、第 2・9 条に最も fits）が、
   価値の核心（必読列 anchor ID 化・CLAUDE.md 1 行）が kakuman の L-GATE-HARNESS に掛かる。**UPSTREAM-DECISION-2026-08-26 の順位 1・2（check-routing-gates 述語化 / check-traps-sync 分割）の採否欄（26 件とも未記入）を埋める作業と同じ問い**なので、そこで一緒に人間へ
4. **点検の清算は KG と切り離して先に**（ひでさんの「これに伴い DH 自体のリファクタ・点検」への答え）。独立 PR 候補（いずれも人間承認）:
   (a) Q9-A: VERSION ↔ GRAPH.yml `version` ↔ upgrade-spec 状態行の整合 + VERSION 昇格規則 1 行（DECL-10/11）
   (b) GRAPH.yml に 4 skill 登録 or 「載せない」宣言 + 「実体 ⊆ 宣言」検査（DECL-01、HV-04 の source 実質検査も）
   (c) COUNCIL-LOG 二重管理の処遇（skill 内 12 件の転記 or 廃止、配布からの除外）（SK-03）
   (d) manifest: `.mcp.json` / `.gitignore` / `.claude/agents/` / Level B 同居 vs 置換の調停（DECL-05/14）— 1 回で決める
   (e) Level A E-3 に Windows native（規範文書改変 → Council）
   (f) RL 読込経路の修理 + RL 現況 SSOT 一本化（TP-05/06）
   (g) `GH_REVIEW_PAT` 再発行（人間）+ `check_pat` の有効性検査 + gemini-review 未起動の原因調査
   (h) 代謝の再開（HD-01/02、reindex-librarian）

## 未解決の論点（更新）

- U-1 「メタスキルに標準装備」の実体は skill（agent）か tool + rule か。**現時点の見立て: tool + rule（1 行 + 1 本 + 使わない tool）**。skill 化は B の実測後
- U-2 記事の 4 本構成を標準にするか、1 本から始めるか → **1 本から**（3 案とも一致）。1 本目の選定基準の優先順は人間: 自動更新 / 版固定の可否（uvx 型 ○ / 単一バイナリ型 × → attestation）/ tool 数（15 vs 30）/ 出力予算内蔵（codebase-memory-mcp ○）/ installer が `~/.claude.json` を書くか
- U-3 `.mcp.json` の manifest 分類: A「雛形 overwrite + 実体 never_touch 既定 = pin 凍結を仕様化」/ B「merge 1 行」/ C「触らない」/ F「不要」。`.gitignore` / `.claude/agents/` も同じ未分類 → 1 回で決めるか個別か
- U-4 Level A E-1 / E-3 と外部 CLI・Windows native → E-4「外部 CLI 許容条件」新設案 + E-3 Windows 追記（Council）
- U-5 記事のルーティング表を CLAUDE.md に置くか → **DH 既定は非常駐**（TP-01 訂正版。G-AGENT 凍結先例）。常駐は M2 以上の裁量 + 時限 + add-demote-check。kakuman は WARN 超で余地 4,108 B
- U-6 DH 自身への適用 → コードグラフは効かない（ts 0）。文書側は案 C。Graphify は LLM 呼出（第 2 条）と cc-cockpit「表示のためにモデルを呼ばない」で不採用寄り
- U-7 鮮度: pre-commit（clone ごと再 install・untracked）/ watcher（アカウント単位 daemon 常駐 — cc-cockpit 常駐アプリと干渉？）/ verify の stale 検出。純化 RL §9 に従いローカル。v2.3.8 の「daemon が ok を返しながら停止」故障を踏まえ heartbeat 検知の要否
- U-8 hook: Graphify 型 nudge / block は 3 案とも不採用（DH 横断規範）。ただし rtk `init -g` が非観測 hook の既存逸脱先例（SK-07 c′）
- U-9 ブレスト置き場の二重規範（DH `delivery/ANALYSIS-*` vs kakuman `docs/brainstorm/`）— 前ブレスト U-7 と同じ
- U-10 RL 読込経路の修理先: DH 側 L1 SKILL.md 読込順序（L-FULL、既存 6 RL も配線され購読量増）か、配布先 CLAUDE.md 1 行（人間承認）か
- U-11 GRAPH.yml に外部 tool ノードを持つか（現行 8 本は全て DH 内 impl、G-2 は実在検査）。持たないなら I-3 隣に「外部 tool は載せない」1 行
- U-12 点検清算 (a)〜(h) を KG 案と切り離すか同梱するか、順序（Q9-A を先に閉じないと spec の版番号が置けない）
- U-13 `observed-peers.md:150`「downstream には伝播しない」宣言 vs 実態（overwrite で 3 リポ md5 一致）
- U-14 discovery cache 既定（F8 訂正）と tool search 既定化の版・閾値の来歴（issue #31002 は built-in tools が v2.1.69 から deferred、MCP は「descriptions が context の 10% 超」時のみと記す）→ MCP 固定費の見積り前提
- U-15 Python 版の三重不一致（利用者機 3.14.3 / DH CI 3.11 / ツール ==3.13.*）を uv 管理の別 Python で吸収するか、E-1 の読み替え条件に落とすか
- U-16 hook-observations は tool 名 + duration のみ（内容フリー allowlist）で byte を持たない → 基線計測に byte を足すかはプライバシー規約との調整。代替 = 公式 `/context` `/usage` Attribution（DH 内で言及 0）
- U-17 kakuman の hooks は Windows で「一度も発火しておらず」（REGIME:457-458、python3 単独指定）→ **Windows で Python が Claude Code 経由で動いた一次証拠が無い**。案 B / C の Windows 成立見込みは下方修正
- U-18 プロンプトキャッシュ: MCP server の on/off・hook の可変出力・グラフ更新に伴う tool 定義変化は「tool definitions changed」でキャッシュ全再読込を起こす（costs docs）。「70 tok の応答」に隠れた固定費
- U-19 セキュリティ / サプライチェーン: `uvx --from pkg==ver` はハッシュ固定なし、PyPI `graphifyy` と `graphify` の名前乖離、570 MB モデルの出所、DH 直下に LICENSE 不在（第三者設定の表示義務）
- U-20 cc-cockpit は `claude` をサブプロセス起動する（CLAUDE.md 落とし穴 6）。committed `.mcp.json` が非対話で無確認ロードされるなら **`.mcp.json` の commit = 起動される任意コードの配布**で、cc-cockpit 落とし穴 3「LAN 露出は RCE と等価」と同じ重さ

## ブレスト決定

> 人間が「これで行く」と言ったことだけを書く（AI の推奨は書かない）。

- **2026-09-05 ひでさん「点検清算 (a)〜(h) を L0 で仕様化して」** → §いま出ている案 4 の (a)〜(h) を L0 昇格。
  成果物 = **`dh-upgrades/upgrade-spec-v6.17.0.md`**（状態: L0 起草・人間レビュー待ち。版番号は同 spec の F1 の結論に従って rename されうる）。
  **KG 標準装備そのものは L0 に上げていない**（同 spec §実装しないもの で明示除外。順序は §いま出ている案 2 の
  「E → F/A → C の実測 → B の判断」のまま、配布先での一次計測を経てから別 spec）

### L0 昇格後の対応関係

| ブレスト側 (a)〜(h) | spec 側 | 実装前の追加ゲート |
|---|---|---|
| (a) VERSION / 状態行 drift | F1 | — |
| (b) GRAPH 網羅性・edge source | F2 | D-2（verifier-philosophy の凍結判断は Council 寄り） |
| (c) COUNCIL-LOG 二重管理 | F3 | **Council D-3** |
| (d) manifest 分類・Level B 同居 | F4 | **Council D-4** |
| (e) Level A E-3 | F5 | **Council D-5** |
| (f) RL 読込経路・現況 SSOT | F6 | — |
| (g) PAT 失効・gemini-review 沈黙 | F7 | PAT 再発行は人間専管（spec 対象外） |
| (h) 代謝停止 | F8 | 代謝の実行は reindex-librarian の運用（spec 対象外） |

仕様化の過程で、8 項目が独立した 8 個の不具合ではなく **1 つの構造的欠落（宣言層に「実体 → 宣言」方向と
「宣言の鮮度」の検査が無い）の 8 つの現れ**であることが判明した。ゆえに spec は検査器を 8 本作らず、
静的整合を harness-verifier 検査 8 に、時間経過を signal-scan 検知器 (e)(f) に集約している。

## 次にやるなら

- **実機観測セット**（利用者の Windows 機。sandbox では代替不能）: `claude --version` / `python --version` / `uv --version` / `/mcp` / `/context` / `/usage`（Attribution の MCP 行・Prompt cache 行）/ `~/.claude.json` の mcpServers / 実 hook-observations の行数
- 未読一次の回収: code-review-graph v2.3.8 release note 本文 / Graphify `install` ソース（書込先・block 手段・`--strict` の一回性）/ Boris スレッド返信（Daniel San）/ arXiv 2602.23368「Keyword search is all you need」/ Serena docs / codebase-memory-mcp installer.ps1 / Claude Code settings-reference・permissions・prompt-caching・env-vars
- F10 の Windows / cp932 再計測、better-code-review-graph（埋め込み有り）と codebase-memory-mcp の同条件計測
- 案 C プロトタイプの残り 3 点（check-traps-sync parity / 5 gate 分の grep 航法 call 数比較 / Windows 起動時間）
- ~~点検清算 (a)〜(h) の PR 分割案~~ → **完了**。`upgrade-spec-v6.17.0.md` §実装順序と PR 分割（PR-A〜PR-G、PR-A が全先行）
- ~~「L0 に上げられそうか」~~ → **点検清算は 2026-09-05 に L0 昇格済み**（§ブレスト決定）。KG 標準装備は E / F の一次計測（出来事）が無い段階では引き続き上げない（U-5）
- spec の判断点 D-1〜D-7 を人間へ。うち D-3 / D-4 / D-5 は**実装前 Council 諮問**が必要（escalation-matrix「規範文書改変」行）。判断キット形式にするなら `decision-kit-html` 先例
- `GH_REVIEW_PAT` の再発行（人間専管）。再発行までは DH 全 PR の auto-merge が止まり、人間 merge が要る
