# 既存 17 skill description 監査チェックリスト — Wave 1

**作成日時**: 2026-05-11T05:30:00Z
**起点 PR**: [PR #76](https://github.com/samejima-ai/dialog-harness/pull/76)（Wave 1 Phase C）
**Council 採決根拠**: `council-2026-05-11T05:00:00Z-w1qb02`（recommended B: 逐次修正、Wave 1 内では監査チェックリストのみ作成）
**規約根拠**: `dev-env-spec.md` §「skill description トリガー語彙規約」

---

## 監査軸

各 skill の `SKILL.md` frontmatter `description:` を以下 4 軸で監査:

| 軸 | 内容 | 合格条件 |
|---|---|---|
| **A. 自動起動契約語彙** | 「自動的に検討する」「明示されなくても起動を必ず検討する」等の動詞契約が含まれるか | 少なくとも 1 つ存在 |
| **B. 禁止語彙の不在** | `Use PROACTIVELY` / `Automatically activated for X` 等の ECC 固有英語が含まれていないか | 含まれない |
| **C. 兄弟 skill との disambiguation** | 類似 skill との発動条件分離が明文化されているか | 「……との混同を避ける」「→ <skill>」形式の参照あり |
| **D. trigger 例の具体性** | 自然言語 trigger 例が複数列挙されているか | ≥ 3 例 |

---

## 監査対象 17 skill

監査結果は本ファイルの末尾に追記する形で逐次更新（各 skill の次回更新時）。

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
| 16 | `.claude/skills/crosscut-hook-observer/SKILL.md` | ✓ | ✓ | ✓ | ✓ | PR #76（Wave 1 新設、規約準拠） |
| 17 | `.claude/skills/rtk-integration/SKILL.md` | ? | ? | ? | ? | — |

凡例:
- `✓`: 合格
- `✗`: 修正必要
- `?`: 未監査
- `-`: 該当なし

---

## 監査プロトコル

### 各 skill 次回更新時の作業手順

1. `SKILL.md` frontmatter `description:` を読む
2. 上記 A/B/C/D 軸で評価
3. 不合格軸を本ファイルの該当行に記録、修正案を本ファイルに併記
4. 同 PR 内で `SKILL.md` を修正 + 本ファイルの該当行を `✓` に更新
5. PR 番号を「監査済 PR / 修正済 PR」列に記録

### 既存 skill の自然観察データ（PR #69, v5.10.0 由来）

`history/SKILL-CREATOR-AUDIT-v5.10.x.md`（v5.10.x 監査記録、Wave 2 で archive 移動）で
16 skill 横断診断が既に実施済。下記弱点パターンは Wave 2 以降の逐次修正で参照素材になる:

- **P0-2 trigger phrase 二極化**（5 skill: 自然言語 trigger 欠落 + 過剰汎化）
- **P1 L0 兄弟 trigger 衝突** / spec-architect 557 行 over-budget
- **issue-implementer ⇔ issue-quality-gate 規格双方向重複**

Wave 1 で新設の `crosscut-hook-observer` は本規約準拠で作成済（# 16 行）。

---

## Wave 2 末振り返り儀式での観測項目

Council 諮問 w1qb02 の minority opinion（哲学者 C: Wave 1 内一括実施）に応じて、
Wave 2 末の振り返り儀式で以下を観測:

- 17 skill 中、`✓` マークが付いた件数（修正完了率）
- 16 skill 既存診断パターン（P0-2 / P1）が逐次修正で解消された件数
- 残り未修正 skill が Wave 2 内で更新機会を得られなかった理由

進捗が ≤ 50% の場合は **Wave 3 で一括修正を再諮問**（諮問 4 候補）。
