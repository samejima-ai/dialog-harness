# ECC agents/ 参照カタログ（draft）

**観察対象**: `affaan-m/everything-claude-code` @ v2.0.0-rc.1
**観察日**: 2026-05-11 JST
**再観察予約**: 2026-11-11（6 ヶ月後、REGIME-LOG 経由）
**ライセンス**: MIT（DH 吸収可、ただし本ファイルは参照標本として保持のみ）
**正式パス確定待ち**: Council 議題 1 採決後に `refs-draft/` から正式パスへ移動

---

## 1. 規模と分類

ECC `agents/` 配下に **48 ファイル** が平坦配置（命名規則: `{name}.md`）。

### カテゴリ分類（一次観察）

| カテゴリ | 代表ファイル | 件数推定 |
|---|---|---|
| 計画・建築 | `planner.md` / `architect.md` / `tdd-guide.md` / `chief-of-staff.md` / `type-design-analyzer.md` | 5 |
| コード品質 | `code-reviewer.md` / `security-reviewer.md` / `code-simplifier.md` / `refactor-cleaner.md` | 4 |
| 言語別レビュアー | `cpp-reviewer.md` / `csharp-reviewer.md` / `flutter-reviewer.md` / `database-reviewer.md` 等 | 10+ |
| ビルド解決 | `build-error-resolver.md` / `cpp-build-resolver.md` / `dart-build-resolver.md` 等 | 7+ |
| 特殊ドメイン | `a11y-architect.md` / `harness-optimizer.md` / `loop-operator.md` / `e2e-runner.md` | 5+ |
| 開発ツール | `code-explorer.md` / `docs-lookup.md` / `doc-updater.md` / `conversation-analyzer.md` / `comment-analyzer.md` / `pr-test-analyzer.md` / `silent-failure-hunter.md` | 7 |
| GAN ワークフロー | `gan-planner.md` / `gan-generator.md` / `gan-evaluator.md` | 3 |
| その他 | `code-architect.md` 等 | 残 |

---

## 2. agent 定義パターン（planner.md 一次観察）

### YAML frontmatter 構造

```yaml
---
name: planner
description: Expert planning specialist for complex features and refactoring.
             Use PROACTIVELY when users request feature implementation,
             architectural changes, or complex refactoring.
             Automatically activated for planning tasks.
tools: ["Read", "Grep", "Glob"]
model: opus
---
```

**観察事項**:
- `name`: agent 識別子（kebab-case）
- `description`: トリガー文言（"Use PROACTIVELY when..." 等で自動起動誘導）
- `tools`: 利用可能ツール限定（読取系のみが典型）
- `model`: opus / sonnet / haiku 指定

### 本文構造

- システムロール定義（"You are an expert ... specialist focused on ..."）
- プロセス（番号付きフェーズ）
- 出力規約（テーブル形式 / 確認チェックリスト等）

---

## 3. DH との対応関係

| ECC agent | DH 概念 | 対応度 |
|---|---|---|
| `planner` | `layer0-spec-architect`（SPEC 作成前の計画フェーズ） | 中（粒度差: ECC は特定タスク、DH は holistic SPEC） |
| `architect` | `layer0-spec-architect` の architecture 判定 | 高 |
| `chief-of-staff` | `layer2-orchestrator` | 中（ECC は stateless、DH は L2 判定後起動） |
| `loop-operator` | `crosscut-council` + `harness-verifier` | 中（実行ループ安全監視） |
| `code-reviewer` | `layer1-independent-reviewer` | 高 |
| `security-reviewer` | `crosscut-verifier-philosophy` + `harness-verifier` | 中 |
| `gan-planner` / `gan-generator` / `gan-evaluator` | 対応なし（GAN ワークフローは DH 未実装） | 0 |
| `harness-optimizer` | `harness-verifier`（D4 内部整合性検査）と対比 | 低（名前は類似だが ECC harness-optimizer は ECC 自身の最適化） |

---

## 4. DH 方法論での生成手順（メタスキル化の核心）

ECC `agents/` 級の出力を DH が **ドメイン固有で生成** する手順:

1. **L0 spec-architect で対話**: 利用者プロジェクトのドメイン特性を `dialog-questions.md` カテゴリで聴取
2. **subphase-l03-api.md 起動**: 「ECC agents 定義パターン参照モード」（Phase 2 タスク B で追加）で、observed ドメインに必要な agent 一覧を生成
3. **agent YAML frontmatter テンプレ**: `name` / `description` / `tools` / `model` を Claude Code 公式形式で出力（DH の scaffold-checklist.md に Phase 3 タスク C で規約追加）
4. **配置先**: 利用者プロジェクトの `~/.claude/agents/{name}.md` または `.claude/agents/{name}.md`（ECC 互換）

---

## 5. 観測注釈

- **SOUL.md 表記との乖離**: SOUL.md は "30 specialized agents" と記載するが、実数 48。差分 18 は marketing snapshot との時差と推定（v1.x → v2.x への成長）
- **agents/ vs skills/ の役割分担**: agents/ = 短期タスク specialist、skills/ = 長期ワークフロー / domain knowledge
- **opus model 指定**: 計画・建築系の agent は `model: opus` 明示が多い（精度優先）。DH も layer0 / Council は opus 想定
- **tools 限定**: `["Read", "Grep", "Glob"]` 等の読取専用が多い。これは Claude Code agent sandbox 設計の典型

---

## 6. 後続更新時の注意

- 次回観察時（2026-11-11）に ECC が v3.x に上がっている可能性 → カタログ全面再生成必須
- ECC `agents/` の追加 / 削除を git log で確認可能（shallow clone でも `git log -- agents/` で観察可）
- DH 側の対応関係表（§3）は DH のバージョンアップで変動するため、各回観察時に再評価

---

**TODO**（Council 議題 1 採決後）:
- 正式パス移動（`refs-draft/` → 確定先）
- 全 48 agents の name / description サマリ表を完全化（現状はカテゴリ別代表例のみ）
- ECC `agent.yaml` メタデータ参照（`/tmp/ecc-survey/ecc/agent.yaml` 観察未完）
