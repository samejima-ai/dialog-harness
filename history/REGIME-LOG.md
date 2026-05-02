# REGIME-LOG

DH 本体のモード判定・major/minor 昇格の記録。

## v5.5.1（patch、no minor bump）

- 判定日: 2026-05-02
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer1-autonomous-dev（M2 体制、人間ひでさん指示で起動）
- 起源: v5.5.0 で温存された Phase γ 残 2 件のうち先行宣言 4 を本実装する patch（v5.5.0 CHANGELOG / INTENT.md に v5.5.x patch 候補として明記済みの項目を消化）。副次目的として gemini-review GitHub Action（PR #37/#38 で導入）の独立レビュー機能を実運用で初めてテストする
- 自己検証: `harness-verifier/verify.py` 全項目 PASS（実行記録は本 patch CHANGELOG Step 3 に簡記）
- 後方互換: 機能変更ゼロ（明文化のみ）。SKILL.md セクション番号・既存 references 本文（追記のみ）・crosscut-* / templates/ / harness-verifier/ は機能不変。`refactor-intent-map.md` の I/O 契約も不変

### 非破壊変更（破壊項目なし、機能変更なし）

| 項目 | 内容 |
|---|---|
| 先行宣言 4 本実装 | `layer0-archeo-architect/references/handoff-to-evaluator.md` のステータスヘッダ / ロードマップ表 / 先行宣言 4 セクションを本実装版へ拡充。射程外要素列挙 + 援用と全体採用の境界線 + L1/L2 禁止規約 + v6.0.0 昇格の観測トリガー + 整合性ガード を 5 サブセクションで明文化 |
| 履歴記録 | CHANGELOG.md / INTENT.md / REGIME-LOG.md（本ファイル）/ ARCH-DECISIONS.md（AD-020）に記録 |
| バージョン | 据え置き → v5.5.1（patch のみ昇格）。明文化追加で機能変更なし、minor 昇格不要 |
| 副次目的 | gemini-review GitHub Action 運用テスト（`.claude/skills/**` + `history/**` を touch、non-draft PR で発火） |

破壊項目なし。利用者プロジェクトには配布されない（v5.0.0〜v5.5.0 と同パターン）。

### Council 諮問の有無

本 patch は Council 諮問なしで実施（AD-020 §根拠参照）。理由: (a) v5.5.0 CHANGELOG / INTENT.md / ARCH-DECISIONS.md AD-019 で「先行宣言 4 を v5.5.x patch / v5.6.0 候補」として既に明示済み、(b) 本実装は明文化のみで機能変更なし、(c) 実装者 confidence ≥ 0.6（複数案拮抗なし）、(d) `crosscut-council` 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当しない。

## 2026-05-01 命名整備サイクル: Lifecycle → LC（patch、no version bump）

- 判定日: 2026-05-01
- AI 能力バージョン: claude-opus-4-7
- 改修主体: layer0-spec-architect → crosscut-council 諮問 → layer1-autonomous-dev（人間ひでさん指示で起動）
- 起源: PR #31 (CI/CD 強化計画 merge 済) で記録された保留計画「Lifecycle → LC 命名変更計画」の発動。本来の発動条件 (a)「PR #30 merge かつ PR #31 merge 両方」のうち PR #30 が未 merge（draft）のまま発動したため、`crosscut-council` で並列実行の妥当性を諮問
- Council 判定: 経営者（条件付き進行）/ 開発者（段階的進行）/ 哲学者（条件記述更新後に進行）→ 重み付き「進行可、3 条件付き」（`history/COUNCIL-LOG.md` 参照）
- 自己検証: `harness-verifier/verify.py` 全項目 PASS（実行記録は INTENT.md 実施記録に簡記）
- 後方互換: glossary.yml で旧表記を全て aliases として保持。delivery/ / docs/ / dh-upgrades/ / 既存 CHANGELOG・REGIME-LOG・ARCH-DECISIONS エントリは不変

### 非破壊変更（破壊項目なし、機能変更なし）

| 項目 | 内容 |
|---|---|
| 命名統一 | `Lifecycle L=N` `L=N`（Lifecycle 文脈）`Lifecycle 軸` 等を `LC=N` `LC 軸` に統一。Layer (`L0/L1/L2`) は不変 |
| 後方互換 alias | `harness-verifier/glossary.yml` の `lifecycle:` セクションで `L=0/L=1/L=2` `Lifecycle 0/1/2` `Lifecycle L=0/L=1/L=2` を旧表記 alias として保持 |
| 履歴記録 | INTENT.md 旧「保留中」節を「✅ 完了」化、実施記録を追記。CHANGELOG.md / REGIME-LOG.md（本ファイル）/ COUNCIL-LOG.md にも記録 |
| バージョン | 据え置き（v5.3.0）。命名整備のみ機能変更なし、minor 昇格不要 |

破壊項目なし。利用者プロジェクトには配布されない（DH 本体の規約改訂）。

### PR #30 との並列衝突回避

PR #30（v5.4.0 archeo-architect）は `layer0-spec-architect/SKILL.md` `dev-env-spec.md` `history/INTENT.md` `history/CHANGELOG.md` を touch する。本 PR は同 4 ファイルで PR #30 が追加する archeo 行には触れず、既存 Lifecycle 言及行のみ置換した。merge 順序が前後しても rebase で機械的に解決可能。

## v5.5.0（minor 昇格、後方互換維持）

- 判定日: 2026-05-02
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer0-spec-architect → layer1-autonomous-dev（M2 体制、v5.0.0/v5.1.0/v5.2.0/v5.3.0/v5.4.0 と同一）
- 起源: PR #33 ブレスト結晶 `delivery/AUTONOMOUS-DRIVE-BRAINSTORM-2026-05-02.md`（adrv01/02/03 全合意成立、確定ロードマップ「v5.5.0 = adrv01-Ph1 + Phase γ」）+ Council 合議（`council-2026-05-02T11:00:00Z-adrv01` / `council-2026-05-02T12:30:00Z-vrfy01`）+ AD-018/AD-019
- 自己検証: `delivery/SELF-VERIFICATION-v5.5.0.md`

### 非破壊追加（破壊項目なし）

| 項目 | 内容 |
|---|---|
| adrv01-Ph1 自己申告プロトコル | `crosscut-council/SKILL.md §自己申告プロトコル` 新節（AD-018）。confidence < 0.6 を Council 起動の正式トリガーとして明文化、内部完結禁止 |
| Council category 分類例追加 | `pre-check.md` §scope/PR 境界 vs 新規思想 の判別シナリオ（Copilot review #34 feedback、category 誤選択の Shift Left 防止）|
| escalated エッジケース | `consensus-protocol.md` §escalated 経路での合意成立（vrfy01 事例由来）+ §自己申告 hook 経路（v5.6.0 Ph2 で本実装の先行宣言）|
| Phase γ コア 3 件本実装 | `inferential-sensor-v2.md` 第4層 / `layer1-autonomous-dev/SKILL.md` §6 / `layer1-independent-reviewer/SKILL.md` / `delivery-format.md` / `handoff-to-evaluator.md` 5 ファイル改修（AD-019）|
| L1 評価軸 4 軸化 | 仕様適合 ∩ 動作 ∩ ユーザビリティ ∩ **意図合致**（refactor-intent-map.md 存在時のみ起動、後方互換完全維持）|
| バージョン記録 | INTENT / ARCH-DECISIONS / REGIME-LOG / CHANGELOG / COUNCIL-LOG（vrfy01 既追記）|

破壊項目なし。既存 SKILL.md セクション番号、既存 references の本文（追記のみ）、crosscut-* / templates/ / harness-verifier/ は機能不変。
利用者プロジェクトには配布されない（v5.0.0〜v5.4.0 と同パターン）。

### 移行方針

v5.5.0 は **既存 LC ≥ 1 プロジェクトに対する強制適用なし**（v5.1.0 / v5.2.0 / v5.3.0 / v5.4.0 と同パターン）。
利用者プロジェクト側には影響しない。dialog-harness リポジトリ自身の SK/RL 規約のみで動作する。
v5.4.0 → v5.5.0 への upgrade は SKILL.md の v5.5.0 セクション読込で完結（個別の migration script は不要）。
**Phase γ 意図合致軸は `delivery/refactor-intent-map.md` 存在時のみ起動**（後方互換完全維持）。archeo を一度も起動していないプロジェクトには一切影響しない。

### 不変項目（spec §2 遵守確認）

| 不変項目 | 遵守状況 |
|---|---|
| 5 本柱原則（P1-P5） | ○（特に P3 情報純度・P5 献上哲学を補強する方向の改訂）|
| 第 6 条 人間 ≒ Council 原則 | ○（adrv01-Ph1 が第 6 条の Phase 1 実装、自己申告 = 一次入力 + Council = 二次検証）|
| 履歴層規約 | ○（INTENT/ARCH-DECISIONS/REGIME-LOG/CHANGELOG/COUNCIL-LOG 既存形式準拠）|
| 献上プロトコル | ○（Type A/B/C/D 不変、意図合致逸脱時は intent_drift として Type C/D に分類）|
| Level A skill 本体不変 | ○（追記のみ、本体ロジック不変）|
| 継承禁止項目の指定自体 | ○ |
| 3 層 + 1 横断構造 | ○（新規 skill 追加なし、Phase γ コア 3 件は既存 skill への追記）|

### β止揚運用の制度化（vrfy01 由来）

Council `vrfy01` で「V-1 狭義 + 第3の道（検証を v5.5.0 SPEC 化に内包）」の止揚採用（`agreed_with_modification`）を実施。adrv01 と同じ「段階的組み込みで止揚」パターンの再採用。残ドリフト検査が SPEC 化過程で「既存機構の SPEC ↔ 実装照合」として自然に内包され、`delivery/SELF-VERIFICATION-v5.5.0.md` に運用記録を残す。adrv01-Ph2（v5.6.0 独立観測機構）への自然な前段としても整合。

### モード判定（DH 本体自身）

DH 本体自身の REGIME.md は本改修スコープ外（メタ案件）。改修体制は以下：

- Mode: M2 標準（S=2、U=1、R=2、N=0、合計 5、L2 閾値未達）
- LC: LC=1（v5.4.0 リリースから 1 日経過、CHANGELOG 更新 < 30 日）
- dev_mode: github_assisted（PR 駆動、worktree 隔離、merge 前 review）
- 体制: L0（spec-architect）→ L1（autonomous-dev）+ layer1-independent-reviewer + crosscut-council 諮問
- AI 能力バージョン: claude-opus-4-7（1M context）
- Council 起動回数: 2 件（adrv01 in PR #33, vrfy01 in PR #34）

### 次バージョン予定

- v5.5.x patch: Phase γ 先行宣言 4（ストラングラー射程外宣言）+ 5（失敗アンチパターン早期検出）の本実装、`crosscut-verifier-philosophy` 本実装の再々々後送（v5.6.0 候補）
- v5.6.0: adrv01-Ph2（独立観測機構新設、新規 crosscut-* skill = harness-verifier 同型）
- v6.0.0 候補: adrv01-Ph3（哲学者法廷モデル）+ adrv02-Ph2（ハイブリッド段階移行 + subagent isolation）+ 第 3 の道 + crosscut-verifier-philosophy 大統合 + 第 7 条昇格

## v5.3.0（minor 昇格、後方互換維持）

- 判定日: 2026-04-30
- AI 能力バージョン: claude-opus-4-7
- 改修主体: layer0-spec-architect → layer1-autonomous-dev（M2 体制、v5.0.0/v5.1.0/v5.2.0 と同一）
- 起源: HANDOFF「1 機能完遂の自律駆動 WF 設計」2026-04-30 + Council 合議（invocation_id: `council-2026-04-30T14:30:00Z-wfsurf1` / `council-2026-04-30T14:50:00Z-wfbase1`）+ AD-015/AD-016/AD-017
- 自己検証: `delivery/SELF-VERIFICATION-v5.3.0.md`

### 非破壊追加（破壊項目なし）

| 項目 | 内容 |
|---|---|
| WF 形状単一性 | layer1-autonomous-dev SKILL.md §原則に明文化（AD-015）。機能タイプ別 WF 群を作らない運用原則 |
| 献上トリガー Type D | 異常献上（AI 自己解決不能な技術的例外）を新設（AD-016）。philosophy.md §5 / SKILL.md §8 / delivery-format.md に追加 |
| WF 選択責任 | 設計差分ゼロ（AD-017）。WF 単一化により問題消失、既存メカニズム（Type C / 体制事後評価 / Type D）で吸収 |
| `references/wf-baseline-rationale.md` | layer1-autonomous-dev に新設。観測閾値・厚化トリガー・第 3 の道（v6.0.0 候補）の温存記述 |
| philosophy.md §5 | Type D 節と Type 二項分類の限界（v6.0.0 候補）を追加。第 8 条候補「献上 3 軸の存在論」を温存 |
| バージョン記録 | INTENT / ARCH-DECISIONS / REGIME-LOG / CHANGELOG / COUNCIL-LOG（既存記載）|

破壊項目なし。既存 SKILL.md セクション番号、既存 references の本文、crosscut-* / templates/ / harness-verifier/ は不変。
利用者プロジェクトには配布されない（`harness-verifier/` 同様、本リリースは DH 本体の規約改訂）。

### 移行方針

v5.3.0 は **既存 Lifecycle ≥ 1 プロジェクトに対する強制適用なし**（v5.1.0 / v5.2.0 と同パターン）。
利用者プロジェクト側には影響しない。dialog-harness リポジトリ自身の SK/RL 規約のみで動作する。
v5.2.0 → v5.3.0 への upgrade は SKILL.md の v5.3.0 セクション読込で完結（個別の migration script は不要）。

### 不変項目（spec §2 遵守確認）

| 不変項目 | 遵守状況 |
|---|---|
| 5 本柱原則（P1-P5） | ○（特に P1 フラクタル原則を強化する方向の改訂） |
| 履歴層規約 | ○（INTENT/ARCH-DECISIONS/REGIME-LOG/CHANGELOG 既存形式準拠） |
| 献上プロトコル | ○（Type A/B/C を不変、Type D は明示拡張） |
| Level A skill 本体不変 | ○（layer1-autonomous-dev SKILL.md は §原則 + §8 表 + §DELIVERY 抜粋への追記のみ、本体ロジック不変） |
| 継承禁止項目の指定自体 | ○ |
| 3 層 + 1 横断構造 | ○（新規 skill 追加なし） |

### モード判定（DH 本体自身）

DH 本体自身の REGIME.md は本改修スコープ外（メタ案件）。改修体制は以下：

- Mode: M2 標準（S=小、U=低、R=低、N=低、単一ドメイン、L2 閾値未達）
- 体制: L0（spec-architect）→ L1（autonomous-dev）+ layer1-independent-reviewer
- AI 能力バージョン: claude-opus-4-7

### 次バージョン予定

- v5.3.x または v5.4.0: `crosscut-verifier-philosophy` 本実装（v5.1.0 / v5.2.0 から再々後送）
- v6.0.0 候補: 第 3 の道（単一 WF + 動的 context 注入）/ 献上 3 軸構造 / 次元論の philosophy.md 第 7 条昇格

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
