# ECC Instincts（continuous-learning-v2.1）設計参照カタログ（draft）

**観察対象**: `affaan-m/everything-claude-code` @ v2.0.0-rc.1 — `skills/continuous-learning-v2/SKILL.md`
**観察日**: 2026-05-11 JST
**再観察予約**: 2026-11-11
**現行 version**: v2.1.0（origin: ECC）

---

## 1. 概要

Instincts は ECC の **継続学習機構**。Claude Code セッションを PreToolUse / PostToolUse hook で観測し、信頼度スコア付き「atomic instinct」を生成、複数プロジェクトで観測されたものは global skill として promote する。

### 進化系譜

| Version | 観測方式 | scope | promotion | commands |
|---|---|---|---|---|
| v1 | Stop hook（session end） | global のみ | なし | 4（status / evolve / export / import） |
| v2.0 | PreToolUse / PostToolUse（100% 観測） | global のみ | なし | 4 |
| **v2.1** | PreToolUse / PostToolUse | **project-scoped + global** | **2+ プロジェクト × 平均 confidence 0.8+** | **6**（+promote / projects） |

---

## 2. 学習機構フロー

```
Observation Hook (PreToolUse/PostToolUse)
         ↓
Background Haiku Agent (Pattern Analysis)
         ↓
Instinct Generation (confidence: 0.3–0.9)
         ↓
Project Scoping (git remote URL / repo path → hash ID)
         ↓
Global Promotion (2+ projects × 0.8+ avg confidence)
         ↓
Skill Clustering (/evolve command で skills/commands/agents へ昇格)
```

### Instinct 記録形式

```
~/.claude/projects/{git-remote-hash}/instincts/{id}.json
{
  "id": "inst_abc123",
  "pattern": "React useEffect dependencies always include ...",
  "confidence": 0.85,
  "evidence_count": 12,
  "last_seen": "2026-05-11T...",
  "scope": "project | global"
}
```

---

## 3. Commands

| Command | 機能 |
|---|---|
| `/instinct-status` | 学習済 instincts の表示 |
| `/evolve` | instincts をクラスタリングして skills/commands/agents に昇格提案 |
| `/promote {id}` | 手動 global 昇格 |
| `/projects` | プロジェクト別 scope 一覧 |
| `/export` | パターン export（実装コード非含、メタデータのみ） |
| `/import` | 他環境からのパターン import |

---

## 4. 学習対象（暗黙的）

| カテゴリ | scope 想定 | 例 |
|---|---|---|
| Framework conventions | project | React useEffect deps / Django QuerySet patterns |
| Security practices | global | 「常に input 検証」「secrets を env で扱う」 |
| API patterns | global | REST 命名 / GraphQL schema 規約 |
| Build / Test workflow | project | npm script 命名 / pytest fixture 規約 |

---

## 5. DH との対応関係

| Instincts 機能 | DH 対応機構 | 対応度 |
|---|---|---|
| PreToolUse / PostToolUse 観測 | DH は hook 機構未採用 | 0 |
| 信頼度スコア（0.3-0.9） | `crosscut-council` の `judgment_confidence`（0.0-1.0） | 中（概念類似、用途異） |
| Global promotion 規則 | DH 未実装 | 0 |
| `/evolve` skill clustering | DH 未実装、`crosscut-feedback-loop` が片鱗 | 低 |
| Project-scoped vs global | DH `REGIME.md` の dev_mode（local_only / github_assisted / autonomous） | 低（scope 次元異） |
| Local storage (`~/.claude/projects/`) | DH は git versioning で代替 | 低 |
| Privacy preserving（実装コード非 export） | DH は SPEC / 履歴を export 前提（philosophy 第 1 条「観測温存」） | 低（思想異） |

**結論**: Instincts 級の継続学習機構は DH に不在。DH の `crosscut-feedback-loop`（検証結果還流）は **post-fact 還流** のみで、**観測-学習-promote** の動的サイクルは未実装。

---

## 6. DH 方法論での生成手順

Instincts 級の出力を DH が **ドメイン固有で生成** する手順:

1. **L0 spec-architect 対話で学習要件抽出**: 「繰り返し起きる判断パターン」「プロジェクト固有の暗黙知」を `dialog-questions.md` の観測温存カテゴリで聴取
2. **subphase-l06-invariants.md 起動**: 「ECC Instincts 学習対象参照モード」（Phase 2 タスク B で追加）で、ドメイン固有の学習対象一覧（不変条件として固定すべき / 学習すべき）を導出
3. **学習機構配置**:
   - 利用者プロジェクトの `.claude/hooks/` 配下に PreToolUse 観測 hook を生成（ECC 互換）
   - または利用者プロジェクトの `.github/workflows/` 配下に observation collector を生成（GitHub Actions 経由、`autonomous_scope: full` 対応）
4. **昇格 / 還流先**: DH の `history/INTENT.md` に観測温存、必要なら Council 経由で philosophy 第 8 条候補へ昇格（cookpato A3 タイムゾーン履歴の前例）

---

## 7. 観測注釈

- **`origin: ECC`**: SKILL.md frontmatter で出自明示 → 他 harness への portability 担保
- **Background Haiku Agent**: Pattern analysis は Haiku model で実行（コスト最適化）。DH の Council は Opus 想定で機構の重さが異なる
- **`projects/{hash}/`**: git remote URL を hash 化して project scope を作る設計は DH の `.claude/skills/` 配下プロジェクト構造とは独立
- **cross-project contamination 防止**: v2.1 の主目的。React パターンが Python project に漏れる問題への対処
- **DH との思想衝突**: DH は「観測温存（philosophy 第 5 条想定）」と「人間最終承認（第 6 条）」で **AI 自動 promote は警戒** する設計。Instincts の global promotion 2+ × 0.8+ confidence は AI 自動判定で global 昇格 → DH 採用時は Council 経由必須

---

## 8. リスクと注視点

- **観測データのプライバシー**: Instincts は local storage 限定（`~/.claude/`）だが、`/export` で他環境に持ち出し可能。DH 採用時は export 経路の制限が必要
- **promotion 暴走**: 2+ projects × 0.8+ avg confidence は緩い閾値 → 危険なパターンが global 昇格する余地。DH 採用時は Council 経由でメタ承認機構（v5.9.0 Council `amrev1` で要件化済）が必須
- **DH との階層整合**: Instincts は D3（配布 skill）相当、DH は D4（メタ skill）。Instincts を D4 として吸収する場合は階層整合性の議論が必要（議題 2 で扱う可能性あり）

---

## 9. 吸収優先度（HANDOFF 表 5 との照合）

- HANDOFF: 「HIGH（DH の feedback-loop / learning 機構の学習データ源として高価値）」
- 一次観察: HIGH 維持（DH の post-fact 還流のみの片肺を補完する novel contribution）
- **ただし**: 採用時は Council メタ承認機構必須（philosophy 第 6 条 + v5.9.0 Council 4 実装要件との整合）

---

**TODO**（Council 議題 1 採決後）:
- 正式パス移動
- continuous-learning-v2.1 SKILL.md 全文の精読（現状は frontmatter + 表のみ）
- DH 自前の継続学習機構導入是非を別議題化（v6.0.0 候補、`crosscut-feedback-loop` 拡張案として）
- 「観測温存（philosophy 第 5 条想定）」と「自動 promotion」の哲学的衝突を議題化
