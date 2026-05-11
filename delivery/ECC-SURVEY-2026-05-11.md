# ECC（everything-claude-code）ephemeral 一次観察ノート

**観察日時**: 2026-05-11 JST
**観察対象**: `affaan-m/everything-claude-code` @ v2.0.0-rc.1
**観察方式**: shallow clone → `/tmp/ecc-survey/ecc/`（depth=1、66M、観察後削除）
**ライセンス**: MIT (2026 Affaan Mustafa) — **DH 吸収可**

---

## 1. リポジトリ概要

- **VERSION**: `2.0.0-rc.1`
- **自己定義** (CLAUDE.md): "Claude Code plugin - a collection of production-ready agents, skills, hooks, commands, rules, and MCP configurations"
- **SOUL.md 表記**: "30 specialized agents, 135 skills, 60 commands, and automated hook workflows"
- **実数**（ephemeral clone での `ls | wc -l`）:
  - `agents/`: **48** ファイル（SOUL.md より 18 多い）
  - `skills/`: **182** ディレクトリ（SOUL.md より 47 多い）
  - `commands/`: ディレクトリ存在（legacy-command-shims/ も併存、count 未取得だが SOUL.md と乖離想定）
- **package**: `ecc-universal` + `ecc-agentshield`（npm 別パッケージ 2 つ）

**注**: SOUL.md は marketing 用 snapshot で時差ありと推定。本ノートでは ephemeral clone での実数を一次情報とする。

---

## 2. トップレベル構造（root 直下 22 ディレクトリ）

| ディレクトリ | 内容 | 用途 |
|---|---|---|
| `agents/` | 48 MD ファイル（平坦） | 専門サブエージェント定義 |
| `skills/` | 182 サブディレクトリ（各 SKILL.md + assets） | ドメイン別ワークフロー定義 |
| `commands/` | 各 slash command MD | レガシー slash コマンド |
| `legacy-command-shims/` | 移行用シム | command → skill 移行の中間層 |
| `hooks/` | `hooks.json` + `README.md` | Claude Code 公式 hook schema 準拠 |
| `rules/` | common/ + 14 言語別ディレクトリ | always-follow ガイドライン |
| `contexts/` | dev.md / research.md / review.md | 動的システムプロンプト注入 |
| `mcp-configs/` | MCP server preset | 外部統合 |
| `manifests/` | install-components.json / install-modules.json / install-profiles.json | 選別インストール定義 |
| `plugins/` | README.md（plugin marketplace 設計） | プラグイン拡張点 |
| `scripts/` | ecc.js / install-plan.js / install-apply.js / catalog.js 等 30+ | CLI ユーティリティ |
| `src/` | Python LLM モジュール（providers/core/prompt/cli/tools） | LLM プロバイダ抽象化 |
| `ecc2/` | Rust コントロールプレーン（alpha） | session lifecycle + TUI |
| `tests/` | Python + JavaScript 多言語 | 1,282 テスト（AgentShield 含） |
| `examples/` | Django / Go / Laravel / Rust / Next.js 実プロジェクト | 設定見本 |
| `docs/` | マルチ言語ドキュメント | ja/ko/pt/zh/tr |
| `assets/` | 共有アセット | |
| `research/` | リサーチノート | |
| `schemas/` | JSON schema | |

### root 直下 MD ファイル（DH の skill 分散モデルと対照）

- `README.md` / `README.zh-CN.md`
- `CLAUDE.md` — Claude Code への指示
- `AGENTS.md` — エージェント設計概観
- `SOUL.md` — 自己定義文書（後述）
- `RULES.md` — ルール統括
- `CHANGELOG.md`
- `CODE_OF_CONDUCT.md` / `CONTRIBUTING.md` / `SECURITY.md` / `SPONSORING.md` / `SPONSORS.md` / `TROUBLESHOOTING.md`
- `COMMANDS-QUICK-REF.md` / `EVALUATION.md` / `REPO-ASSESSMENT.md` / `WORKING-CONTEXT.md`
- `the-longform-guide.md` / `the-shortform-guide.md` / `the-security-guide.md`

→ **ECC は root 統合文書集中型**、DH は **skill 分散型**。設計哲学の対比点。

---

## 3. agents/ サンプル分析（planner.md）

```yaml
---
name: planner
description: Expert planning specialist for complex features and refactoring. Use PROACTIVELY when users request feature implementation, architectural changes, or complex refactoring. Automatically activated for planning tasks.
tools: ["Read", "Grep", "Glob"]
model: opus
---

You are an expert planning specialist focused on creating comprehensive, actionable implementation plans.

## Planning Process
### 1. Requirements Analysis
### 2. Architecture Review
### 3. Plan Construction
### 4. Risk Assessment
...
```

**観察事項**:
- YAML frontmatter: `name` / `description` / `tools` / `model` の 4 キー（Claude Code agent definition の公式形式）
- `description` 内に **"Use PROACTIVELY"** 等のトリガー文言を埋め込む = Claude Code が自動起動するための語彙
- agent 本体は Markdown プロセス記述

**DH 対応**: `.claude/skills/{name}/SKILL.md` の YAML frontmatter（`name` / `description`）と互換あり。tools/model は Claude Code agent システムの拡張点。

---

## 4. skills/ サンプル分析（continuous-learning-v2/SKILL.md）

```yaml
---
name: continuous-learning-v2
description: Instinct-based learning system that observes sessions via hooks, creates atomic instincts with confidence scoring, and evolves them into skills/commands/agents. v2.1 adds project-scoped instincts to prevent cross-project contamination.
origin: ECC
version: 2.1.0
---
```

**機能要約**:
- PreToolUse / PostToolUse hook で **100% 信頼観測**（v1 は Stop hook のみで 漏れあり）
- **project-scoped** instincts（v2.1 新設）: `projects/<git-remote-hash>/` 配下に隔離保管
- **promotion 規則**: 2+ プロジェクトで観測 × 平均 confidence 0.8+ → global 昇格
- **6 commands**: status / evolve / export / import / promote / projects（v2.0 は 4 commands）
- confidence range: 0.3–0.9

**DH の REGIME.md `dev_mode`（local_only / github_assisted / autonomous）との整合**:
- ECC instincts scope（project / global）と DH dev_mode は次元が異なる
- alignment 設計が必要（議題 2 で philosophy 改修対象に含まれる可能性）

---

## 5. hooks/ 一次観察

### hooks.json の特徴

- **`$schema`**: `https://json.schemastore.org/claude-code-settings.json` — **Claude Code 公式 hook schema**
- **event types**: PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd / **PreCompact**（5+1 = 6 種）
- **matcher**: `Bash` / `Write` / `Edit|Write` / `*` / `Bash|Write|Edit|MultiEdit` 等のツール限定
- **command 構造**: Node.js bootstrap で `CLAUDE_PLUGIN_ROOT` 解決 → `scripts/hooks/plugin-hook-bootstrap.js` → 個別 hook script
- **exit code 規約**: `2` = block / `0` = warn

### PreToolUse hook（9 件抜粋）

| Hook ID | Matcher | 用途 | Exit |
|---|---|---|---|
| `pre:bash:dispatcher` | Bash | 品質 + tmux + push + GateGuard 統合 dispatcher | 2/0 |
| `pre:write:doc-file-warning` | Write | 非標準 `.md`/`.txt` 警告（README/CLAUDE/CHANGELOG 等は許可） | 0 |
| `pre:edit-write:suggest-compact` | Edit\|Write | 50 tool call 毎に `/compact` 提案 | 0 |
| `pre:observe:continuous-learning` | * | continuous-learning v2 用 PreToolUse 観測フック | 0 (async) |
| `pre:governance-capture` | Bash\|Write\|Edit\|MultiEdit | 秘密漏洩・policy 違反検出（`ECC_GOVERNANCE_CAPTURE=1` で有効化） | 0 |
| `Dev server blocker` | Bash | `npm run dev` 等を tmux 外で実行ブロック | 2 |
| `Tmux reminder` | Bash | 長時間コマンドへの tmux 推奨 | 0 |
| `Git push reminder` | Bash | `git push` 前のレビュー促し | 0 |
| `Pre-commit quality check` | Bash | lint / commit message 形式 / console.log/debugger/secrets 検出 | 2/0 |

**DH 対応**: DH の `harness-verifier/verify.py`（D4 内部整合性 5 項目）は **Claude Code hook 機構を使わず Python 単体実装**。両者は補完関係。DH に hooks.json を追加すれば PreToolUse 機構を活用可能（Phase 2 タスク B の自然な拡張点）。

---

## 6. rules/ 構造

```
rules/
├── README.md
├── common/                  # 言語横断 10 ファイル
└── 14 言語別ディレクトリ:
    cpp / csharp / dart / golang / java / kotlin / perl /
    php / python / rust / swift / typescript / web / zh
```

**設計原則** (CONTRIBUTING.md より引用):
> "Common and language-specific directories contain files with the same names. Flattening causes language-specific to overwrite common, breaking relative `../common/` references."

**DH 対応**: DH には言語別 rules ディレクトリは存在しない。`templates/` 配下に GitHub Actions テンプレ等が並ぶが、言語別 coding-standards は未整備。Phase 3 タスク C で「ECC 互換配置規約」を `scaffold-checklist.md` に明文化する際の参照モデル。

---

## 7. AgentShield 配置

- **npm package 別出**: `ecc-agentshield` パッケージ（`ecc-universal` とは独立）
- **統合**: `/security-scan` slash command で Claude Code から起動可能
- **規模**: **102 静的解析ルール × 1,282 テスト**（98% カバレッジ）
- **対象**: CLAUDE.md / settings.json / mcp-servers.json / hooks definitions / agents/*.md / skills/**/*.md
- **GitHub Marketplace**: ECC Tools として free/pro/enterprise tiers で配布
- **v1.6.0 (Feb 2026)** で初統合

**DH 対応**: `harness-verifier/` ディレクトリが D4 内部整合性検査を担うが、AgentShield 級の脆弱性スキャナは未実装。Phase 2 タスク B の subphase-l05-authz.md に「AgentShield 脆弱性パターン参照モード」として参照導入が自然。

---

## 8. ECC2（Rust コントロールプレーン）— 吸収対象外

- **配置**: `ecc2/` 配下
- **状態**: alpha（v2.0.0-rc.1 でも alpha 表記）
- **commands**: dashboard / start / sessions / status / stop / resume / daemon
- **設計**: session lifecycle + SQLite-backed StateStore + Context Graph + TUI dashboard
- **判定**: GA 待ち、本案件では吸収対象外（layer2-orchestrator の参考実装止まり）

---

## 9. SOUL.md（ECC の自己定義文書）

```
# Soul

## Core Identity
Everything Claude Code (ECC) is a production-ready AI coding plugin with 30 specialized agents,
135 skills, 60 commands, and automated hook workflows for software development.

## Core Principles
1. Agent-First — route work to the right specialist as early as possible.
2. Test-Driven — write or refresh tests before trusting implementation changes.
3. Security-First — validate inputs, protect secrets, and keep safe defaults.
4. Immutability — prefer explicit state transitions over mutation.
5. Plan Before Execute — complex changes should be broken into deliberate phases.

## Cross-Harness Vision
This gitagent surface is an initial portability layer for ECC's shared identity, governance,
and skill catalog. Native agents, commands, and hooks remain authoritative in the repository
until full manifest coverage is added.
```

**DH 対応**: DH の `philosophy.md`（6 条 + 第 7 条 AI 組織論）と比較すると、ECC の `Core Principles` は **エンジニアリング規範 5 つ** であり、DH の **存在論的規律 7 つ** と階層が異なる。
- ECC: 「どう実装するか」の規範（Agent-First / TDD / Security-First / Immutability / Plan Before Execute）
- DH: 「何者であるか」の規律（自己相似性 / 5 次元 / 対話 / 献上 / 観測温存 / 人間最終承認 / 4 役割組織論）

→ **議題 2 の独占 4 軸（対話 / フラクタル / 献上 / 5 次元）は ECC SOUL.md に対応概念なし** という主張は妥当。

---

## 10. 観察後処理

ephemeral clone は本ノート完成後に **削除予定**（Phase 0.6 末尾で `rm -rf /tmp/ecc-survey` 実行、検証で `ls /tmp/ecc-survey` が「No such file」を返すことを確認）。

**観察結果の DH 内永続化**: 本ノート + `refs-draft/ecc/` 配下 5 ファイルが ephemeral clone の代替参照。Council 議題 1 採決後、`refs-draft/` は正式パスへ移動。
