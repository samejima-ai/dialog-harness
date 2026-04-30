# REGIME-LOG

DH 本体のモード判定・major/minor 昇格の記録。

## v5.2.0（minor 昇格、後方互換維持）

- 判定日: 2026-04-29
- AI 能力バージョン: claude-opus-4-7
- 改修主体: layer0-spec-architect → layer1-autonomous-dev（M2 体制、v5.0.0/v5.1.0 と同一）
- 起源: HANDOFF「DH 自己検証機構（誤作動防止機構との統合検討用）」2026-04-29 + Council 合議（invocation_id: council-2026-04-29T21:00:00Z-d4mtr1, 4 論点一括）
- 自己検証: `delivery/SELF-VERIFICATION-v5.2.0.md`

### 非破壊追加（破壊項目なし）

| 項目 | 内容 |
|---|---|
| 5 次元論 | D1〜D5 を確立。機械可読命名は D-numbering、思想文書では meta-layer 等を併走（AD-010） |
| `harness-verifier/` | リポジトリルート直下に新規配置。DH 本体と並列の独立機構（AD-011, AD-012） |
| `harness-verifier/PHILOSOPHY.md` | 規律の自己相似性、自己検証機構の存在論を記述 |
| `harness-verifier/BOUNDARY.md` | DH 本体と本機構の境界線、5 検証項目スコープ、責務マトリクス |
| `harness-verifier/HUMAN-PROTOCOL.md` | 月次運用 + push/PR トリガー、D5 判断カテゴリ、形骸化防止メカニズム |
| `harness-verifier/glossary.yml` | 用語辞書（D1〜D5 / モード / Lifecycle / SK/RL/WF/CTL / 5 層スタック / prefix 等） |
| `harness-verifier/verify.py` + `checks/` | Python 標準ライブラリのみ、5 検査モジュール（frontmatter / references / dependency_graph / five_layer_structure / glossary） |
| `.github/workflows/harness-verify.yml` | 月次 cron + push/PR トリガー、月次レポート自動 commit |
| layer0-spec-architect SKILL.md | v5.2.0 セクション追加（次元論メモ、L0 起動フローへの影響なし）|
| バージョン記録 | INTENT / ARCH-DECISIONS / REGIME-LOG / CHANGELOG / COUNCIL-LOG |

破壊項目なし。既存 SKILL.md セクション番号、既存 references の本文、philosophy.md、crosscut-* / templates/ は不変。
利用者プロジェクトには配布されない（`harness-verifier/` は dialog-harness リポジトリ自身の保護機構）。

### 移行方針

v5.2.0 は **既存 Lifecycle ≥ 1 プロジェクトに対する強制適用なし**（v5.1.0 と同パターン）。
利用者プロジェクト側には影響しない。dialog-harness リポジトリ自身の CI のみで動作する。
v5.1.0 → v5.2.0 への upgrade は SKILL.md の v5.2.0 セクション読込で完結（個別の migration script は不要）。

### 不変項目（spec §2 遵守確認）

| 不変項目 | 遵守状況 |
|---|---|
| 5 本柱原則（P1-P5） | ○（追加のみで思想に変更なし） |
| 第 6 条（人間 ≒ Council、関係性原則） | ○（5 本柱とは別カテゴリの関係性原則として保持。第 7 条候補は v6.0.0 へ温存） |
| 履歴層規約 | ○（v5.1.0 形式を継承して v5.2.0 セクションを追記） |
| 献上プロトコル | ○（`delivery/SELF-VERIFICATION-v5.2.0.md` 経由で献上） |
| Level A skill 本体不変 | ○（layer0-spec-architect SKILL.md に追記、本体構造は不変） |
| philosophy.md 不変 | ○（v5.0.0 で確立、v5.2.0 でも非変更） |
| 3層 + 1横断構造 | ○（crosscut-* prefix そのまま、新規 skill 追加なし） |
| 既存セクション番号 | ○（SKILL.md §0〜§7.6 不変、参照ドキュメント節に v5.2.0 セクション追加のみ） |
| 独立性要請 | ○（harness-verifier は DH 本体に依存しない、依存方向は一方向） |

### モード判定（DH 本体自身、v5.0.0 から不変）

DH 本体自身の REGIME.md は本改修スコープ外（メタ案件、v5.0.0/v5.1.0 と同様）。改修体制は以下：

- Mode: M2 標準（S=低 1, U=低 1, R=低 1, N=0、単一ドメイン、L2 閾値未達）
- 体制: L0（spec-architect）→ L1（autonomous-dev）+ layer1-independent-reviewer
- AI 能力バージョン: claude-opus-4-7
- dev_mode: github_assisted

### 次バージョン予定

- v5.3.0 候補: `crosscut-verifier-philosophy` 本実装（v5.1.0 で v5.2.0 候補とされたが v5.2.0 では D4 検査機構優先、再後送）
- v5.3.0 候補: `harness-verifier/` 第 6 検証項目「次元境界保全」追加（Council 論点 4 少数意見）
- v6.0.0 候補: philosophy.md 第 7 条「次元論と D4 の独立性」追加（major 昇格、AD-010〜AD-012 を本体哲学に格上げ）

## v5.1.0（minor 昇格、後方互換維持）

- 判定日: 2026-04-28
- AI 能力バージョン: claude-opus-4-7
- 改修主体: layer0-spec-architect → layer1-autonomous-dev（M2 体制、v5.0.0 と同一）
- 起源: PR #19 テストレビュー（シナリオ「ケロぴの森」: M2 monolith Web PWA / 中学生算数 / 絵で答える）
- 自己検証: `delivery/SELF-VERIFICATION-v5.1.0.md`

### 非破壊追加（破壊項目なし）

| 項目 | 内容 |
|---|---|
| §0 受け入れ基準 | L0 完了の 4 条件（仕様充足 / scaffold 実体 / smoke test / §7.4 PASS）を明文化。Lifecycle ≥ 1 既存プロジェクトには段階適用 |
| Pre-flight 必読化 | §1.5 / §3.5 / §4 / §6 / §7 各冒頭に「Pre-flight: X を必読」行を追加 |
| scaffold-checklist.md | references/ に新設。v5.1.0 標準 stack（Vite+TS+React+PWA）の必須生成ファイル 12 種と smoke test 4 コマンドを規定 |
| §7.4 自己検証ステップ | §7（出力）と §7.5 の間に新設。5 件のチェックボックスで broken reference / smoke test / DONT 自己照合 / Pre-flight 充足 / 受け入れ基準充足を確認 |
| credit-template バージョン | v5.0.0 → v5.1.0 |

破壊項目なし。既存 SKILL.md セクション番号・既存 references の本文・philosophy.md・crosscut-* / templates/ は不変。

### 移行方針

v5.1.0 は **既存 Lifecycle ≥ 1 プロジェクトに対する強制適用なし**。継続セッションで L0 が再起動されたタイミングで自然に取り込まれる。新規プロジェクトと、既存プロジェクトの v5.1.0 以降に追加開始する機能・フェーズに対して受け入れ基準・Pre-flight・scaffold checklist・§7.4 が適用される。
v5.0.0 → v5.1.0 への upgrade は SKILL.md の v5.1.0 セクション読込と scaffold-checklist.md の参照のみで完結（個別の migration script は不要）。

### 不変項目（spec §2 遵守確認）

| 不変項目 | 遵守状況 |
|---|---|
| 5 本柱原則（P1-P5） | ○（追加のみで思想に変更なし） |
| 履歴層規約 | ○（v5.0.0 形式を継承して v5.1.0 セクションを追記） |
| 献上プロトコル | ○（`delivery/SELF-VERIFICATION-v5.1.0.md` 経由で献上） |
| Level A skill 本体不変 | ○（layer0-spec-architect SKILL.md に追記、本体構造は不変） |
| philosophy.md 不変 | ○（v5.0.0 で確立、v5.1.0 でも非変更） |
| 3層 + 1横断構造 | ○（crosscut-* prefix そのまま、新規 skill 追加なし） |
| 既存セクション番号 | ○（§7.4 は §7 と §7.5 の間に新設、既存番号は不変） |

### モード判定（DH 本体自身、v5.0.0 から不変）

DH 本体自身の REGIME.md は本改修スコープ外（メタ案件、v5.0.0 と同様）。改修体制は以下：

- Mode: M2 標準（S=中、U=低、R=中、N=低、単一ドメイン、L2 閾値未達。範囲は v5.0.0 比で縮小）
- 体制: L0（spec-architect）→ L1（autonomous-dev）+ layer1-independent-reviewer
- AI 能力バージョン: claude-opus-4-7

### 次バージョン予定

- v5.2.0 候補: `crosscut-verifier-philosophy` 本実装（5 本柱整合の自動検証）。本 v5.1.0 では L0 改善のみに範囲を絞り、philosophy verifier は別 minor で扱う
- v5.x: チーム軸（T1-T5）operational 化、stack 拡張（Next.js / Vue / Astro / SvelteKit / 純 Node CLI）

## v5.0.0（major 昇格、後方互換破壊あり）

- 判定日: 2026-04-27
- AI 能力バージョン: claude-opus-4-7
- 改修主体: layer0-spec-architect → layer1-autonomous-dev（M2 体制）
- spec 原典: `dh-upgrades/upgrade-spec-v5.0.0.md`（1500 行）
- 自己検証: `delivery/SELF-VERIFICATION-v5.0.0.md`

### 破壊項目（後方互換 break）

| 項目 | 旧 | 新 | 影響 |
|---|---|---|---|
| Level A skill 名 | `.claude/skills/council/` | `.claude/skills/crosscut-council/` | 既存プロジェクトの skill 参照が破壊。migration-guide で個別対応 |
| .gitignore 規約 | `council-workspace/` | `crosscut-council-workspace/` | 同上 |
| skill 命名規則 | `layerN-` のみ | `layerN-` + `crosscut-` | Level A 第二の prefix 確立 |
| バージョン記法 | `v4.0` 等の `vX.Y` | `v5.0.0` 等の semver 厳格 | v4.x 互換受理 |

### 非破壊追加

- L0 判定軸に dev_mode 追加（既存プロジェクトは local_only 相当として扱える）
- 5 つの crosscut skill 追加（local_only モードでは無視される）
- CTL 連動 protocol 追加（既存 CTL 計算ロジックの拡張、v4.2 互換）
- GitHub Actions 雛形 9 yml（templates/、採用は任意）
- `crosscut-council/references/ctl-maturity-strategy.md` 新規（既存 ctl-calculation.md と並列）
- philosophy.md は不変（パス参照のみ更新、思想本文は触らず）

### 移行方針

既存プロジェクト向けの移行手順は `docs/migration-guide-v5.0.0.md` を参照。

要約：
1. `.claude/skills/council/` → `.claude/skills/crosscut-council/` を git mv
2. 全 SKILL.md / references の `council/` パス参照を `crosscut-council/` に置換
3. `.gitignore` の `council-workspace/` を `crosscut-council-workspace/` に置換
4. REGIME.md に `## dev_mode` セクションを追加（local_only 相当を記録するだけで OK）
5. 必要に応じて `templates/.github/workflows/` をプロジェクトの `.github/workflows/` にコピー

DH 本体改修対象は本体配布元のみ（spec §1.4）。各既存プロジェクトの council/ 参照は本リリースでは触らない。

### 不変項目（spec §2 遵守確認）

| 不変項目 | 遵守状況 |
|---|---|
| 5 本柱原則（P1-P5） | ○ |
| 履歴層規約 | ○（history/ 4 ファイルを v5.0.0 で初期化、形式は既存準拠） |
| 献上プロトコル | ○（`delivery/SELF-VERIFICATION-v5.0.0.md` 経由で献上） |
| Level A skill 本体不変 | ○（既存 layer skill は references 追記のみ、本体ロジック不変） |
| 継承禁止項目の指定自体 | ○（spec §2 を本ファイルで明示再掲） |
| 3層 + 1横断構造 | ○（crosscut- prefix の確立により構造を命名で明示化、L3 は新設しない） |

### モード判定（DH 本体自身）

DH 本体自身の REGIME.md は本改修スコープ外（メタ案件）。改修体制は以下：

- Mode: M2 標準（S=大、U=低、R=中、N=低、単一ドメイン、L2 閾値未達）
- 体制: L0（spec-architect）→ L1（autonomous-dev）+ layer1-independent-reviewer
- AI 能力バージョン: claude-opus-4-7

### 次バージョン予定

- v5.1.0: `crosscut-verifier-philosophy` 本実装（5 本柱整合の自動検証）
- v5.x: チーム軸（T1-T5）operational 化（dev_mode 推論精度向上）
