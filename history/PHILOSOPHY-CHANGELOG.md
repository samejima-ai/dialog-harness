# philosophy.md 改訂履歴

`.claude/skills/layer0-spec-architect/references/philosophy.md`（DH 6→7→8 条憲法）の改訂を **append-only** に記録する。

## 運用規約

- **追記タイミング**: philosophy.md を変更する PR 内で、本ファイルに新規エントリを **手動追記** する（Wave 3 諮問 `council-2026-05-11T09:00:00Z-w3qb03` 採決 B により、自動 emit 機構は不採用）
- **追記者**: philosophy.md を変更する PR の実装者
- **追記内容**: 改訂日時 / 変更条文 / 変更概要 / Council 採決 invocation_id / minority opinion 温存条件 / 関連 PR
- **削除禁止**: 本ファイルは append-only、過去エントリの編集・削除は禁止（philosophy の append-only 性質と整合）

## 改訂規約根拠

- 諮問 `council-2026-05-11T09:00:00Z-w3qb03`（Wave 3 Phase B、recommended B: 手動運用）
- Wave 4 末で改訂頻度 ≥ 2 件/Wave 観測時、minority opinion A（自動 emit 化）を再諮問

---

## エントリ

### 2026-05-11: 第 8 条「自律性原則 + 哲学ガードレール」追加（Wave 3）

- **改訂日時**: 2026-05-11T09:00:00Z
- **変更条文**: 第 8 条 新設
- **変更概要**: AI 自律性の拡張に「観測 → 候補化 → 人間最終承認」の 3 段階モデルを明文化。CTL 0 では候補化段階も inactive（観察温存）。自律拡張機構（continuous-learning / issue-dispatcher / issue-implementer / autonomous-drive）の本条準拠検証規約を含む。
- **Council 採決**: `council-2026-05-11T09:00:00Z-w3qb01`
  - recommended: A（3 段階明文化）
  - confidence: 0.55（接近採決、`judgment-agent.md` §「差 < 0.5 → 0.4-0.6」規則適用）
  - weighted_score: A 4.35 (経営者 + 開発者) vs C 4.25 (哲学者)、差 0.10
  - category: conception（council-weights.md §situational_modifier.conception、weights 3/3/5）
- **minority opinion 温存**: 哲学者 C 案「4 段階拡張（観測 → 候補化 → Council 採決 → 適用）」
  - 温存条件: Wave 4 末で「3 段階運用の Council 経由率 ≤ 20%」観測時、Wave 5 で 4 段階拡張を再諮問
  - 接続性: philosophy 第 7 条 P3 責務分離と整合
- **経験的根拠**: Wave 1 + Wave 2 の B 系収束 2 サンプル
  - Wave 1 PR #76: hooks 5 event / skill description 逐次 / 言語先取りなし
  - Wave 2 PR #77 + #78: continuous-learning 候補出力 / AgentShield warn のみ / frontmatter 逐次
- **関連 PR**: #80 (Phase A SPEC starter) / #81 (Phase B + C 採決・実装)
- **関連 commit**: 本 commit で philosophy.md 第 8 条追加 + 本ファイル新設

---

## 改訂統計（Wave 3 末時点）

| 改訂回数 | Wave | 改訂条文 |
|---|---|---|
| 1 | Wave 3 | 第 8 条 新設 |

Wave 4 で改訂発生時に本表を追記。改訂頻度 ≥ 2 件/Wave 観測時、minority opinion w3qb03 A（自動 emit 化）を再諮問する判定材料とする。
