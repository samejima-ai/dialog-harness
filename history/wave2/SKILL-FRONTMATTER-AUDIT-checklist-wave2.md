# 既存 17 skill origin/version frontmatter 監査チェックリスト — Wave 2

**作成日時**: 2026-05-11T07:30:00Z
**起点 PR**: [PR #78](https://github.com/samejima-ai/dialog-harness/pull/78)（Wave 2 Phase C）
**Council 採決根拠**: `council-2026-05-11T07:00:00Z-w2qb03`（recommended B: 逐次修正、Wave 2 内では監査チェックリストのみ作成）
**規約根拠**: `dev-env-spec.md` §「origin/version frontmatter 規格」（Wave 2 候補 2、PR #78）
**Wave 1 同型**: `delivery/SKILL-DESCRIPTION-AUDIT-checklist-wave1.md` と同パターン

---

## 監査軸

各 skill の `SKILL.md` frontmatter を以下 4 軸で監査:

| 軸 | 内容 | 合格条件 |
|---|---|---|
| **A. origin フィールド** | `origin: ECC-derived / DH-native / external` のいずれかが明示 | 存在 |
| **B. origin_source / origin_version**（ECC-derived 限定） | 元素材の参照ポインタと version 固定 | ECC-derived なら両方存在 |
| **C. chewing_translation / chewing_pr** | T1/T2/T3 翻訳タイプと取り込み PR 番号 | ECC-derived なら両方存在 |
| **D. chewing_council_ref**（諮問あり時） | 関連 Council invocation_id | 諮問起点 skill なら存在 |

---

## 監査対象 17 skill

監査結果は各 skill の次回更新時に追記（逐次修正方針、Wave 1 と同パターン）。

| # | Skill | A | B | C | D | 監査済 PR / 修正済 PR |
|---|---|---|---|---|---|---|
| 1 | `.claude/skills/layer0-spec-architect/SKILL.md` | ? | ? | ? | ? | — |
| 2 | `.claude/skills/layer0-onboarding/SKILL.md` | ? | ? | ? | ? | — |
| 3 | `.claude/skills/layer0-archeo-architect/SKILL.md` | ? | ? | ? | ? | — |
| 4 | `.claude/skills/layer1-autonomous-dev/SKILL.md` | ? | ? | ? | ? | — |
| 5 | `.claude/skills/layer1-independent-reviewer/SKILL.md` | ? | ? | ? | ? | — |
| 6 | `.claude/skills/layer2-orchestrator/SKILL.md` | ? | ? | ? | ? | — |
| 7 | `.claude/skills/layer2-integration-verifier/SKILL.md` | ? | ? | ? | ? | — |
| 8 | `.claude/skills/crosscut-council/SKILL.md` | ? | ? | ? | ? | — |
| 9 | `.claude/skills/crosscut-issue-dispatcher/SKILL.md` | ? | ? | ? | ? | — |
| 10 | `.claude/skills/crosscut-issue-implementer/SKILL.md` | ? | ? | ? | ? | — |
| 11 | `.claude/skills/crosscut-issue-quality-gate/SKILL.md` | ? | ? | ? | ? | — |
| 12 | `.claude/skills/crosscut-verifier-drift/SKILL.md` | ? | ? | ? | ? | — |
| 13 | `.claude/skills/crosscut-verifier-philosophy/SKILL.md` | ? | ? | ? | ? | — |
| 14 | `.claude/skills/crosscut-feedback-loop/SKILL.md` | ? | ? | ? | ? | — |
| 15 | `.claude/skills/crosscut-autonomous-drive/SKILL.md` | ? | ? | ? | ? | — |
| 16 | `.claude/skills/crosscut-hook-observer/SKILL.md` | ✓ | ✓ | ✓ | ✓ | PR #76（Wave 1、5 フィールド先取り） |
| 17 | `.claude/skills/rtk-integration/SKILL.md` | ? | ? | ? | ? | — |

凡例:
- `✓`: 合格
- `✗`: 修正必要
- `?`: 未監査
- `-`: 該当なし（DH-native のため不要）

---

## Wave 2 で先取り適用済の新設 skill（17 skill 対象外）

| Skill | origin | chewing 経路 | 適用 PR |
|---|---|---|---|
| `crosscut-continuous-learning` | ECC-derived | T3 + ガードレール語彙化、Council w2qb01 | PR #78 |

新設 skill は **規約準拠で作成済**。本監査チェックリストの対象は既存 17 skill のみ。

---

## 監査プロトコル（Wave 1 同型）

### 各 skill 次回更新時の作業手順

1. `SKILL.md` frontmatter を読む
2. 上記 A/B/C/D 軸で評価
3. 不合格軸を本ファイルの該当行に記録、修正案を本ファイルに併記
4. 同 PR 内で `SKILL.md` を修正 + 本ファイルの該当行を `✓` に更新
5. PR 番号を「監査済 PR / 修正済 PR」列に記録

### Wave 1 監査との関係

`delivery/SKILL-DESCRIPTION-AUDIT-checklist-wave1.md`（description 語彙監査）と並行運用。各 skill の次回更新時に両軸を同時に整える。

### Wave 2 末振り返り儀式での観測項目

Council 諮問 w2qb03 の minority opinion（経営者 A: Wave 2 内一括実施）に応じて、Wave 2 末の振り返り儀式で以下を観測:

- 17 skill 中、`✓` マークが付いた件数（修正完了率）
- Wave 1 description 監査と Wave 2 frontmatter 監査の合計進捗
- 残り未修正 skill が Wave 2 内で更新機会を得られなかった理由

進捗が ≤ 50% の場合は **Wave 3 で一括修正を再諮問**（minority opinion 温存先）。
