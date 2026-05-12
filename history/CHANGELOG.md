# CHANGELOG

DH 本体の改修履歴。各 Step の実行記録を時系列で追記する。

## 2026-05-12 kakuman-platform-v3.0 連動: D3 同期 + COUNCIL-LOG 献上（v5.16.x 帯 chore、no DH version bump）

**PR #93 (v5.16.1, 2026-05-12 merged) で cookpato に対して実施した D3 同期と同型の作業を `samejima-ai/kakuman-platform-v3.0` に対して実施。並行して kakuman 側で蓄積された Council 判定ログを DH 側へ献上受領した**。本 chore は DH 本体の skill/spec を一切変更しないため version bump なし、`history/project-derived-councils/` 新設のみ。

### kakuman 側 (samejima-ai/kakuman-platform-v3.0)

別 PR で実施。`.claude/skills/` 配下 18 skill を DH e33f8808 から 1:1 同期し `dimension: D3` で配備 (council `d3d4b1` 規格準拠)。16 共通 skill 上書き + 2 新規 (`crosscut-hook-observer` / `crosscut-continuous-learning`) 追加。kakuman 固有 4 skill (`article-forge` / `caaf-wiring` / `news-publish` / `supabase-migration-safe`) は touch せず。

### DH 側 (本リポジトリ、本 PR)

- `history/project-derived-councils/` を新設。利用者プロジェクト由来 COUNCIL-LOG のミラー専用フォルダ
- `history/project-derived-councils/README.md` で **DH 自身の `history/COUNCIL-LOG.md` と論理的に分離する規約**を明文化:
  - F1〜F3 振り返り儀式・council-weights 再校正の対象は `history/COUNCIL-LOG.md` のみ
  - project-derived は別軸で集計、混合集計禁止
  - council `d4at01` (S/U/R 独立維持) と council `l0agg1-4` (cross-project ログ集約) の運用具現
- `history/project-derived-councils/kakuman-platform-v3.0/COUNCIL-LOG.md` に kakuman の COUNCIL-LOG.md 全文を配置 (19 エントリ、内 17 件は DH 起源コピー + 2 件は kakuman 固有: `council-x52-home-launcher-2026-05-10` / `council-2026-05-12T-ux-patterns-lib`)
- `harness-verifier/verify.py` の検査 scope は `.claude/skills/` のみで `history/` を一切スキャンしないため、`history/project-derived-councils/` への scope 拡張は不要 (BOUNDARY.md §3 と整合、scope は既に disjoint)

### 関連 council

- `council-2026-04-30T11:00:00Z-l0agg1` 〜 `l0agg4` — cross-project ログ集約設計。schema-only + 経路分離の哲学を「プロジェクト別フォルダ + ファイル配置」で擬似実現する MVP。`~/.claude/dh-data/` user-scope schema-only push の本格実装 (`l0agg4` 案 D-2) は別サイクル
- `council-2026-04-30T09:00:00Z-d4at01` — S/U/R 独立維持。利用者プロジェクトの判定統計を DH 自身の改修判定統計と混合しない論理的根拠

---

## v5.16.0 (in progress, target 2026-05-12)

**共有可能スキル整理 + 参照整合性確立 + AI 駆動 PR 運用の実証**。Council 2 件起動で合意した scope_lock 6 項目を 1 PR で実装。AI 駆動開発における PR 粒度の決定基準 (AD-021) と L0 三兄弟スキルの DESIGN.md 対応マトリクス (AD-022) を確立。

### 起点 Council

- `council-2026-05-12T13:32:00Z-sspr01` — DH スキル群の共有可能化と参照整合性確立の方向性（initial A → user_revised C 採用）
- `council-2026-05-12T14:30:00Z-adpp01` — AI スペック依存の開発スピード方針（β 中核 + α/ε 条件統合）

### scope_lock 6 項目

1. **harness-verifier 拡張**: `references.py` に `BACKTICK_PATH_RE` を追加、`` `../path` `` 形式のバッククォート内相対パスを dead-link 検査対象化。PR #91 で Copilot 検出済み 2 件 + 既存 3 件を新規発見し全件修正
2. **Level A 配布性 checklist**: `dev-env-spec.md` に 6 軸 / 21 項目の評価基準を新設（不変性 / 参照整合性 / progressive disclosure / 依存方向 / 自己完結性 / メタ評価）
3. **layer0-onboarding に reverse-design 追加**: §4.5 で UI プロジェクトの既存 src/ から色・font・spacing を逆抽出して `DESIGN.md` 初版生成。新規 `references/reverse-design-protocol.md`
4. **layer0-archeo-architect に視覚 Island**: Step 1 構造走査で `island_type: visual` を検出、`refactor-intent-map-template.md` に `island_type` / `design_md_impact` フィールド追加
5. **REGIME-LOG.md に L0 三兄弟マトリクス記録**: spec-architect (v5.15.0〜) / onboarding (v5.16.0〜) / archeo-architect (v5.16.0〜) の対応状況を表形式で
6. **ECC 互換配置の判定基準**: 新規 `ecc-compat-criteria.md` で 6 軸の格上げ判定材料を整備。規約格上げ自体は v5.17.0 以降に延期

### 関連 ADR

- AD-021: AI 駆動開発における PR 粒度の決定基準
- AD-022: L0 三兄弟スキルの DESIGN.md 対応マトリクス

### 後方互換

- 既存 SKILL.md / references / crosscut-* の挙動は完全不変
- DESIGN.md 非生成プロジェクトは v5.15.0 と同一動作
- LC ≥ 1 既存プロジェクトでの遡及適用は不要（新規開始機能・フェーズに段階適用）

詳細: `dh-upgrades/upgrade-spec-v5.16.0.md`

---

## v5.16.1 (in progress, target 2026-05-12)

**D4-AUDIT-2026-04-30 minor 指摘の消化 + cookpato D3 同期前段**。`history/D4-AUDIT-2026-04-30.md` §3.2/§3.3 の MEDIUM・LOW 指摘 (M-1 / M-2 / L-1 / L-2) を消化し、cookpato `.claude/skills/` への 18 skill 同期前段を整備。H-1（P1-P5 vs P1-P6 表記不整合）は council 諮問必須のため本 PR では deferred、別 issue で追跡。

v5.16.0 (feat) が PR #92 で先行 merge されたため、本 chore は v5.16.1 patch としてリナンバーして共存させる（commit 8f1da8d との CHANGELOG header 衝突を回避）。

### M-1: CHANGELOG `(in progress)` 完了マーク漏れの正規化

- v5.14.0 `(in progress, target 2026-05-11)` → `(released 2026-05-11)`（PR #89 merged commit 71ef671）
- v5.10.0 `(in progress)` → `(released 2026-05-08)`（PR #69 merged commit 0eb9b33）
- v5.9.0 `(in progress)` → `(released 2026-05-06)`（PR #59 merged commit fb04f39）
- 同セクション内の `**minor 昇格 (in progress)**` 表現も `**minor 昇格**` に統一
- v5.16.0 自身の `(in progress, target 2026-05-12)` → `(released 2026-05-12)` 化は本 patch では実施せず、v5.16.0 merge 完了後の次 patch（v5.16.2 以降の housekeeping）で扱う

### M-2: S/U/R 三軸用語の単一箇所宣言（既出消化確認）

- `harness-verifier/glossary.yml` の `score_axes` キー（S = 規模 = Scale / U = 不確実性 = Uncertainty / R = リスク = Risk）が監査 (2026-04-30) 以降の中間 PR で既に追加済を確認。本 PR では追加作業なし、消化済として明示記録。

### L-1: 5 本柱 vs 5本柱 表記揺れの統一

- 非アーカイブの活性ドキュメント 2 ファイルで `5本柱` → `5 本柱`（半角スペース版）へ正規化:
  - `dh-upgrades/upgrade-spec-v5.0.0.md`（16 箇所）
  - `docs/migration-guide-v5.0.0.md`（1 箇所）
- `history/` 配下のアーカイブファイル（SELF-VERIFICATION / SKILL-CREATOR-AUDIT / deliveries / D4-AUDIT-2026-04-30 自体）は append-only 規約により対象外。スナップショット時の事実を保持。

### L-2: harness-verifier/PHILOSOPHY.md バージョン記載（既出消化確認）

- `harness-verifier/PHILOSOPHY.md` 末尾に `## バージョン` セクションがあり、`v0.1.0（dialog-harness v5.2.0 で導入、harness-verifier 機構の存在論初版）` が記載済であることを監査以降の中間 PR で確認。本 PR では追加作業なし、消化済として明示記録。

### cookpato 連動

本 v5.16.1 と並行して `samejima-ai/cookpato` PR `claude/update-dialog-d4-layer-Dce69` で `.claude/skills/` 18 skill 同期を実施。cookpato 側は `dimension: D3` で配備（council `d3d4b1` 規格準拠）。

---

