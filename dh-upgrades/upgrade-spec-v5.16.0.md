# Upgrade Spec v5.16.0 — Shared Skills Foundation & AI-Driven PR Cadence

**リリース予定**: 2026-05-12
**バージョン昇格**: minor（v5.15.0 → v5.16.0、後方互換維持の追加のみ）
**起点 Council**:
- `council-2026-05-12T13:32:00Z-sspr01` (scope 確定)
- `council-2026-05-12T14:30:00Z-adpp01` (運用ルール確定)

---

## §1 概要

v5.16.0 は **共有可能スキル整理 + 参照整合性確立 + AI 駆動 PR 運用の最初の実証** を 1 minor で完遂する。Council 合意の scope_lock 6 項目を 1 PR で実装し、AI 駆動開発における PR 粒度の決定基準 (AD-021) と L0 三兄弟スキルの DESIGN.md 対応マトリクス (AD-022) を確立する。

### 起点問題

v5.15.0 で DESIGN.md 機能を layer0-spec-architect に追加した結果、以下 3 つの不整合が浮上:

1. **L0 三兄弟の非対称**: spec-architect は DESIGN.md 対応、onboarding / archeo-architect は未対応（フラクタル原則違反）
2. **参照整合性の構造的欠陥**: Copilot が `../../` 相対パス誤りを 2 件検出、harness-verifier は Markdown リンク resolution チェック未実装
3. **ECC 互換配置の格上げ判定基準不在**: scaffold-checklist で観測層として書いたが、規約格上げの判定材料がない

### 解決方針

Council 合意により以下を採択:
- **AI 駆動 PR 運用**（AD-021）: semver は技術的境界のみ、1 minor 1 議題縛り廃止、PR 粒度上限は AI 検査機構が決定論的に PASS を返せる範囲
- **scope_lock 6 項目を 1 PR で実装**: 関連議題のバンドル許可（v5.16.0 で実証）

---

## §2 scope_lock 6 項目

### scope_lock #1: harness-verifier に Markdown リンク resolution チェック追加

`harness-verifier/checks/references.py` に `BACKTICK_PATH_RE` を追加し、`` `../path` `` 形式のバッククォート内相対パスも dead-link 検査対象にする。

- スコープ: `./` または `../` で始まる相対パスのみ（リポジトリルートからの説明パスや `~/` 開始は対象外、誤検出回避）
- 既存の INLINE_LINK_RE (`[text](path)`) と並列実行
- 検出件数: PR #91 で Copilot が指摘した 2 件 + 既存の 3 件（archeo-architect SKILL.md / handoff-to-evaluator.md / spec-architect deprecation-protocol.md）を新規発見

#### 関連修正（既存 dead-link）

| ファイル | 旧 | 新 |
|---|---|---|
| `layer0-archeo-architect/SKILL.md:24` | `../../history/INTENT.md` | `../../../history/INTENT.md` |
| `layer0-archeo-architect/references/handoff-to-evaluator.md:248` | `../layer0-spec-architect/...` | `../../layer0-spec-architect/...` |
| `layer0-spec-architect/references/deprecation-protocol.md:36` | `../layer1-independent-reviewer/...` | `../../layer1-independent-reviewer/...` |

### scope_lock #2: dev-env-spec.md §共有可能性 を新設し Level A 配布性 checklist を記載

`references/dev-env-spec.md` に Level A 配布性評価 checklist（6 軸 / 21 項目）を新設。新規 skill 追加 PR / 既存 skill 改修 / 格上げ・格下げ時の判定基準として運用。

- 軸 A: 不変性（プロジェクト中立）
- 軸 B: 参照整合性（dead-link 不在、機械検証可能）
- 軸 C: progressive disclosure 規約準拠
- 軸 D: 依存方向（フラクタル整合）
- 軸 E: 自己完結性（利用者プロジェクト配布性）
- 軸 F: メタ評価

機械検証可能項目は harness-verifier 全 PASS で自動充足、人間判断項目は PR レビューでカバー。

### scope_lock #3: layer0-onboarding に reverse-design ステップ追加

`layer0-onboarding/SKILL.md` 処理フロー §4.5 に reverse-design ステップを新設。UI プロジェクトの既存 src/ から色・font・spacing・rounded・shadow を grep + 集計で逆抽出し、`DESIGN.md` 初版を生成する。

- UI 検出条件: React/Vue/Svelte/HTML/CSS の存在、または `index.html` / `manifest.webmanifest` / Tailwind config の存在
- 非 UI（CLI / API サーバ / ライブラリ）では完全スキップ
- 確度メタデータ 3 段階（コード確認 / git 履歴確認 / AI 推定）を全項目に付与
- spec-architect 移行後の最初の対話で人間承認プロセスを必須化（「人間確定」への引き上げ）
- 新規 reference: `layer0-onboarding/references/reverse-design-protocol.md`

### scope_lock #4: layer0-archeo-architect の意図マップに視覚 Island を追加

`layer0-archeo-architect/SKILL.md` Step 1 構造走査に `island_type: visual` の検出条件を追加。`assets/refactor-intent-map-template.md` の Island セクションに `island_type` と `design_md_impact` フィールドを追加。

- 検出シグナル: 同一トークンの直書き重複 / colors.primary の装飾流用 / フォントウェイト混在 / ダークモード未対応 等
- `design_md_impact`: `none` / `tokens_only` / `dos_and_donts` / `both` の 4 値
- DESIGN.md `## Do's and Don'ts` 違反のリファクタ意図を視覚 Island として明示化

### scope_lock #5: REGIME-LOG.md に L0 三兄弟マトリクス記録

`history/REGIME-LOG.md` に v5.16.0 セクションを追加。L0 三兄弟スキルの DESIGN.md 対応マトリクス（スキル / 対応バージョン / 起動契機 / 関連 reference）を表形式で記録。

Council 起動記録（2 件）も同セクションに含む。

### scope_lock #6: ECC 互換配置の判定基準ドキュメント化

新規 reference: `layer0-spec-architect/references/ecc-compat-criteria.md`。

- 6 軸（安定性 / 非衝突 / 使いやすさ / 検査機構連携 / フラクタル整合 / 情報純度）で格上げ可否を判定
- v5.16.0 時点の予測判定（規約格上げは v5.17.0 以降に延期、観測層は継続稼働）を記録
- scaffold-checklist.md §ECC 互換配置（観測層）からの相互参照

---

## §3 不変項目（philosophy 第 1-7 条遵守）

| 不変項目 | 遵守状況 |
|---|---|
| フラクタル原則（第 1 条） | ○（L0 三兄弟均質化、新規レイヤー追加なし、L3 運用層を新設しない） |
| Shift Left 原則（第 2 条） | ○（harness-verifier 強化は第 1 層検査機構の完全化） |
| 情報純度原則（第 3 条） | ○（observation 層と規約層の分離維持、ECC 規約は観測層に留める） |
| 人間責務（第 4 条） | ○（PR 粒度判断を AI 主導化、人間は判断・承認のみ） |
| 献上哲学（第 5 条） | ○（DELIVERY.md 系の献上経路を変更しない） |
| 人間 ≒ Council（第 6 条） | ○（Council 2 件起動、合意プロセス経由で確定） |
| AI 組織論（第 7 条） | ○（Person 責務 P1〜P4 に影響なし、autonomous-drive 機構は不変） |

---

## §4 後方互換性

- 既存 SKILL.md / references / crosscut-* の挙動は完全不変
- DESIGN.md 非生成プロジェクトは v5.15.0 と同一動作
- LC ≥ 1 既存プロジェクトでの遡及適用は不要（新規開始機能・フェーズに段階適用）
- harness-verifier の BACKTICK_PATH_RE 追加は **既存 dead-link 検出を強化する破壊変更** だが、修正対象はマージ済み既存ファイルのみで、利用者プロジェクト側への影響なし

---

## §5 関連 ADR

- **AD-021**: AI 駆動開発における PR 粒度の決定基準
- **AD-022**: L0 三兄弟スキルの DESIGN.md 対応マトリクス

---

## §6 v5.17.0 以降の申し送り

本 PR スコープ外として明示的に申し送る項目:

| 項目 | 申し送り理由 |
|---|---|
| ECC 互換配置の規約格上げ | 6 軸の判定材料がまだ揃わない（90 日観測必要、scope_lock #6 で判定基準のみ整備） |
| philosophy.md 第 4 条への PR 粒度補足追記 | philosophy 改訂は人間刻み維持の例外領域（AD-021 例外規定） |
| L1 / L2 skill 配下の reference でも `../../` 相対パス再点検 | 本 PR で 3 件修正済みだが、harness-verifier 強化により発見される dead-link は段階的に修正 |
| Level A 配布性 checklist の機械検証拡張 | 軸 A / C / E / F の人間判断項目を機械検証可能化（AI 推論ベースの自動検査機構導入） |

---

## §7 検証

- harness-verifier 全 6 検査項目 PASS
- BACKTICK_PATH_RE による新規発見 dead-link は本 PR 内で全件修正済み
- Council 起動記録は COUNCIL-LOG.md / REGIME-LOG.md に append-only で記録
- ARCH-DECISIONS.md に AD-021 / AD-022 を新規追加
