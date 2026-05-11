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

### 2026-05-11: 第 8 条 minority opinion C 再諮問 → 3 段階維持再確認（Wave 4 W4-Q1）

- **改訂日時**: 2026-05-11T19:05:00Z
- **変更条文**: なし（philosophy.md 本文は不変）
- **諮問内容**: Wave 3 w3qb01 で温存された minority C「4 段階モデル拡張」を Wave 4 で再諮問
- **Council 採決**: `council-2026-05-11T19:00:00Z-w4qb01`
  - recommended: A（3 段階モデル維持、Wave 3 採用版を再確認）
  - confidence: 0.65（starter §2.1 判定基準: conf 0.55 < x < 0.70 → 部分実装領域）
  - weighted_score: A 4.56 (経営者 + 開発者) vs C 2.75 (哲学者)、差 1.81
  - category: conception（council-weights.md §situational_modifier.conception、weights 3/3/5、Wave 3 と同一規約）
- **Wave 3 との対比**:
  - Wave 3 w3qb01: 哲学者 stance C conf 0.85、weighted_score 差 0.10 で接近採決 conf 0.55
  - Wave 4 W4-Q1: 哲学者 stance C conf 0.55 に下落（運用データ未蓄積 + 条文の薄さ原則からの逸脱リスク自認）、weighted_score 差 1.81 で明確判定 conf 0.65
- **minority opinion 温存（継続）**: 哲学者 C 案「4 段階拡張（CTL 連動ハイブリッド）」
  - 温存条件: Wave 4 末で「Council 経由率」「3 段階運用実績」観測、Council 経由率 ≤ 20% 時 Wave 5 で C 案または B 案（純粋 4 段階）を再諮問
  - 接続性: philosophy 第 7 条 P3 責務分離との整合は変わらず保持
- **吸収された D 案**: 哲学者第 3 の道「条文不変 + Wave 4 末振り返り儀式観測項目強化」を stance A の補強として採用
  - Wave 4 末振り返り儀式観測項目（必須）: 「Council 経由率」「3 段階運用実績」「minority C 再評価データ蓄積」
- **部分実装の中身**:
  1. philosophy.md 第 8 条改訂なし
  2. 本ファイルに W4-Q1 結果追記（本エントリ）
  3. Wave 4 末振り返り儀式観測項目を必須化（spec-architect L0 が振り返り儀式で確認）
  4. minority C は Wave 5 再諮問温存
- **関連 PR**: #82 (Phase A SPEC starter) / Wave 4 Phase B PR（本変更）
- **意義**: minority opinion 温存機構が Wave 4 で機能した最初の実証。Wave 3 の接近採決 → Wave 4 の明確判定の変遷自体が「観測駆動による哲学者 conf 補正」という DH 哲学（philosophy §3 情報純度 + 観測駆動）の動作証拠

---

## 改訂統計（Wave 4 W4-Q1 採決後時点）

| 改訂回数 | Wave | 改訂条文 | 採決種別 |
|---|---|---|---|
| 1 | Wave 3 | 第 8 条 新設 | A 採決（接近 conf 0.55） |
| — | Wave 4 W4-Q1 | （なし、3 段階維持再確認） | A 採決（明確 conf 0.65） |

Wave 4 で本格的な改訂は未発生（W4-Q1 は A 採決で条文不変）。改訂頻度 ≥ 2 件/Wave 観測時、minority opinion w3qb03 A（自動 emit 化）を再諮問する判定材料とする。
