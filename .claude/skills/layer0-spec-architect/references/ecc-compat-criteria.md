# ECC 互換配置 判定基準（v5.16.0 追加）

ECC (Everything Claude Code) 互換配置を **観測層** から **出力規約** に格上げするための判定基準。
v5.16.0 では基準だけドキュメント化し、規約格上げは v5.17.0 候補として継続検討（Council `council-2026-05-12T13:32:00Z-sspr01` revised C 採用、scope_lock #6）。

スキャフォールド側（観測層）は `references/scaffold-checklist.md` §ECC 互換配置 を参照。本ファイルは規約格上げの是非を判定する材料を提供する。

---

## 原則

- **観測層 = scaffold-checklist.md**: Phase γ-i フックで候補リスト出力、自動採用なし、人間最終承認（philosophy 第 8 条「自律性原則 + 哲学ガードレール」の 3 段階モデル（観測 / 候補化 / 人間最終承認）に準拠）
- **規約格上げの意味**: 「候補出力」から「scaffold 必須生成ファイル」への昇格。L1 が DESIGN.md と同じ強制参照対象として扱う
- **慎重に進める理由**: ECC は外部規約。DH 自身の internal-only 規約と混ぜると独立性原則（D4 / harness-verifier）に違反するリスク
- **CTL 連動**: CTL ≥ 1 で active、CTL 0 では本判定自体が非該当（観測層も inactive）

---

## 判定軸（6 軸、全充足で格上げ可）

### 軸 1: 安定性（version drift 耐性）

- [ ] **1-1**: ECC `agents-catalog.md` / `skills-pattern.md` / `hooks-trigger-points.md` のスキーマが過去 90 日で破壊変更を含まない
- [ ] **1-2**: ECC 側の release cadence が semver に準拠している
- [ ] **1-3**: ECC スキーマの後方互換ポリシーが明文化されている（migration guide 必須）

判定基準: 3 項目全充足で安定性 OK。1 項目でも失えば格上げ保留。

### 軸 2: DH 内部 schema との非衝突

- [ ] **2-1**: ECC の `~/.claude/agents/{name}.md` frontmatter が DH `harness-verifier/checks/frontmatter.py` の検査と整合する（必須キー / 型 / enum 値）
- [ ] **2-2**: ECC の `~/.claude/skills/{name}/SKILL.md` 構造が DH progressive disclosure 規約（SKILL.md + references/ + assets/）と整合
- [ ] **2-3**: ECC `.claude/hooks.json` の adopted_events が DH `crosscut-hook-observer` の SUPPORTED_EVENTS と矛盾しない

判定基準: 3 項目全充足で非衝突 OK。衝突あれば DH 側 schema の修正 or ECC 側へのフィードバック必要。

### 軸 3: 利用者プロジェクトでの使いやすさ

- [ ] **3-1**: ECC 互換配置を採用しても DH の既存 stack（Vite + React + PWA scaffold）が壊れない
- [ ] **3-2**: ECC 互換配置の deployment 手順が `crosscut-autonomous-drive` 経由で自動化可能
- [ ] **3-3**: 利用者プロジェクトが ECC 互換配置を opt-in / opt-out できる（強制しない）

判定基準: 3 項目全充足で使いやすさ OK。

### 軸 4: 検査機構との連携

- [ ] **4-1**: ECC 互換配置の規約準拠を `harness-verifier` の検査項目として組み込める（既存 6 検査項目に追加 or 拡張）
- [ ] **4-2**: ECC 互換配置が DH の `dev_mode` (local_only / github_assisted / autonomous) で差別化できる
- [ ] **4-3**: ECC 互換配置の違反を `crosscut-verifier-drift` で検出可能

判定基準: 3 項目中 2 項目以上充足で連携 OK（4-3 は v5.x 以降でも可）。

### 軸 5: フラクタル整合（philosophy 第 1 条）

- [ ] **5-1**: ECC 互換配置を採用しても L0 / L1 / L2 の責務分担が変わらない
- [ ] **5-2**: ECC 互換配置が crosscut-* の横断レイヤーに自然に乗る（新規レイヤー追加なし）
- [ ] **5-3**: ECC 互換配置が L3 運用層を新設する誘発要因にならない

判定基準: 3 項目全充足。1 項目でも違反すれば philosophy 改訂議論（人間刻み、別 minor）。

### 軸 6: 情報純度（philosophy 第 3 条）

- [ ] **6-1**: ECC 互換配置を採用しても DH 配布物の情報純度が下がらない（外部規約への依存が DH のメッセージを薄めない）
- [ ] **6-2**: ECC 互換配置の文書記述が DH 独自規約と明確に区別できる（reference / 配置パス / 文体）
- [ ] **6-3**: ECC 規約変更時の DH 側追随コストが許容範囲（minor 1 つで吸収可能）

判定基準: 3 項目全充足。1 項目でも違反すれば観測層のままに留める。

---

## 判定結果の記録

格上げ判定を実施したら、以下の形式で `history/REGIME-LOG.md` に記録する:

```markdown
### ECC 互換配置 格上げ判定（YYYY-MM-DD）

- 軸 1 安定性: PASS / FAIL（詳細: ...）
- 軸 2 非衝突: PASS / FAIL
- 軸 3 使いやすさ: PASS / FAIL
- 軸 4 検査機構連携: PASS / FAIL
- 軸 5 フラクタル整合: PASS / FAIL
- 軸 6 情報純度: PASS / FAIL
- **総合判定**: 格上げ可（v5.X.0 で規約化） / 保留（観測層継続）

判定者: <人間 / Council>
判定根拠: <1〜3 文>
```

総合判定が「格上げ可」の場合、別 Council を起動して規約化の具体プロトコルを決議する（minor 単発 PR）。

---

## v5.16.0 時点の予測判定

本ドキュメント作成時点（2026-05-12）での予測判定は以下:

- 軸 1 安定性: 未調査（ECC リポジトリの release cadence を 90 日観測必要）
- 軸 2 非衝突: 部分 PASS（frontmatter は OK、SUPPORTED_EVENTS は scaffold-checklist で観測中）
- 軸 3 使いやすさ: 未調査（実プロジェクトでの opt-in 試行必要）
- 軸 4 検査機構連携: 部分 PASS（既存 6 検査項目を拡張可能だが要設計）
- 軸 5 フラクタル整合: 暫定 PASS（観測層では問題なし）
- 軸 6 情報純度: 暫定 PASS（scaffold-checklist の文脈分離で対応中）

**v5.16.0 時点の結論**: 6 軸の判定材料がまだ揃わないため、規約格上げは v5.17.0 以降に延期。観測層（scaffold-checklist.md §ECC 互換配置）は継続稼働。

---

## 関連参照

- `scaffold-checklist.md` §ECC 互換配置（任意推奨） — 観測層のフック規約
- `philosophy.md` 第 8 条「自律性原則 + 哲学ガードレール」3 段階モデル — 観測 / 候補化 / 人間最終承認
- `history/ECC-SURVEY-2026-05-11.md` — ECC 規約サーベイ記録（Wave 4 〜 5）
- `history/refs-draft/ecc/` — ECC 規約のローカルキャッシュ（agents-catalog / hooks-trigger-points / skills-pattern 等）
