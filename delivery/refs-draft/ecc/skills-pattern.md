# ECC skills/ パターン参照カタログ（draft）

**観察対象**: `affaan-m/everything-claude-code` @ v2.0.0-rc.1
**観察日**: 2026-05-11 JST
**再観察予約**: 2026-11-11
**ライセンス**: MIT
**正式パス確定待ち**: Council 議題 1 採決後

---

## 1. 規模

- **skills/** 配下: **182 サブディレクトリ**（SOUL.md は "135 skills" 表記、実数 182、差分 47 は時差）
- 各 skill: `SKILL.md` 必須 + 任意の `assets/` / `agents/` / `hooks/` / `scripts/` 等

---

## 2. カテゴリ分類（一次観察）

| カテゴリ | 代表 skill | 件数推定 |
|---|---|---|
| Architecture | `hexagonal-architecture` / `design-system` / `architecture-decision-records` / `backend-patterns` | 5+ |
| 言語別パターン | `android-clean-architecture` / `golang-patterns`（推定）等 | 多数 |
| Testing | `ai-regression-testing` / `agent-eval` / `agentic-engineering` / `benchmark` | 5+ |
| Agent 開発 | `agent-harness-construction` / `agent-introspection-debugging` / `autonomous-agent-harness` / `autonomous-loops` | 5+ |
| Domain | `accessibility` / `api-design` / `api-connector-builder` / `agent-payment-x402` | 多数 |
| 学習機構 | `continuous-agent-loop` / `continuous-learning` / `continuous-learning-v2` | 3 |
| Content | `article-writing` / `brand-voice` | 2+ |
| Tools | `clickhouse-io` / `claude-devfleet` / `bun-runtime` | 多数 |
| その他 | `agent-sort` / `ai-first-engineering` / `blueprint` / `browser-qa` / `canary-watch` / `ck` / `click-path-audit` / `code-tour` / `carrier-relationship-management` | 多数 |

---

## 3. SKILL.md フォーマット（continuous-learning-v2 一次観察）

### YAML frontmatter

```yaml
---
name: continuous-learning-v2
description: Instinct-based learning system that observes sessions via hooks,
             creates atomic instincts with confidence scoring, and evolves them
             into skills/commands/agents. v2.1 adds project-scoped instincts to
             prevent cross-project contamination.
origin: ECC
version: 2.1.0
---
```

**観察事項**:
- `name` / `description` は Claude Code 公式 skill schema 準拠
- `origin: ECC` で出自を明示
- `version` で semver 管理

### 本文構造

- "When to Activate" — トリガー条件リスト
- "What's New in vX.Y" — バージョン差分テーブル
- プロセス記述（番号付きフェーズ / コード例）
- Git Checkpoints / コマンド一覧

---

## 4. DH との対応関係

| ECC skill | DH 概念 | 対応度 |
|---|---|---|
| `continuous-learning-v2` | DH には対応 skill なし（feedback-loop は近い） | 0（新規吸収候補） |
| `autonomous-agent-harness` | `crosscut-autonomous-drive` + `layer1-autonomous-dev` | 高 |
| `agent-harness-construction` | `layer0-spec-architect`（harness 構築フェーズ） | 中 |
| `tdd-workflow`（前 Explore 報告） | DH 未実装、`crosscut-verifier-drift` の片鱗あり | 低 |
| `security-review`（前 Explore 報告） | `harness-verifier` + `crosscut-verifier-philosophy` | 中 |
| `architecture-decision-records` | `history/ARCH-DECISIONS.md`（DH 既実装） | 高 |

---

## 5. DH 方法論での生成手順

ECC `skills/` 級の出力を DH が **ドメイン固有で生成** する手順:

1. **L0 spec-architect 対話で skill 要件抽出**: `dialog-questions.md` の「自動化したい繰り返しタスク」「特殊ドメイン」カテゴリで聴取
2. **subphase-l02-domain.md + subphase-l03-api.md**: ドメインモデル + API 契約から skill 候補を導出
3. **SKILL.md テンプレ**: YAML frontmatter（name/description/version）+ 本文構造（When to Activate / Process / Outputs）を `scaffold-checklist.md` に Phase 3 タスク C で規約化
4. **配置先**: 利用者プロジェクトの `~/.claude/skills/{name}/SKILL.md` または `.claude/skills/{name}/SKILL.md`

---

## 6. 観測注釈

- **continuous-learning-v2 の進化系譜**: v1（Stop hook のみ）→ v2.0（PreToolUse/PostToolUse で 100% 観測）→ v2.1（project-scoped + global promotion） — DH 内に該当する継続学習機構はない（HANDOFF Section 3 で「Instincts は DH 設計に組込検討」と言及）
- **`autonomous-agent-harness` skill**: ECC が「harness」概念を skill 化している点は DH と思想的に共鳴。ただし ECC は実装ライブラリ的、DH は方法論層
- **マルチドメイン対応**: ECC は healthcare-emr / defi-amm / customs-trade-compliance / energy-procurement 等の業界ドメイン skill を持つ。DH はドメイン中立を保ち、業界 skill は利用者プロジェクトの D3 として生成
- **agent-eval skill**: Pattern extraction via Haiku, confidence scoring → DH の crosscut-issue-quality-gate 12 軸と機能類似

---

**TODO**（Council 議題 1 採決後）:
- 正式パス移動
- 全 182 skills の name / description サマリ表（カテゴリ別代表例のみで完全化保留）
- ECC manifests/（install-components.json / install-modules.json / install-profiles.json）解析を Phase 3 タスク C で参照
