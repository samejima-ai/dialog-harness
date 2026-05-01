# CHANGELOG

DH 本体の改修履歴。各 Step の実行記録を時系列で追記する。

## v5.4.0 (released 2026-05-01)

minor 昇格。**archeo-architect（意図復元 L0 兄弟スキル）を新設**し、spec-architect の双対として L0 を 3 兄弟体制に拡張。
HANDOFF「archeo-architect ブレスト → 実装」 2026-05-01 を起源とする。
後方互換維持（v5.0.0 / v5.1.0 / v5.2.0 / v5.3.0 と同パターン）。利用者プロジェクトには配布されない。

`crosscut-verifier-philosophy` 本実装は本リリース対象外（v5.4.x または v5.5.0 候補へ再々後送）。
Phase γ（L1 自己検証/独立検証への意図合致軸追加、起点問題の構造解決）は本リリース対象外（v5.5.0 候補）。

### Step 0: HANDOFF 受領と最終ブレスト

ひでさんから Claude.ai 上の archeo-architect ブレスト結晶 HANDOFF を受領。CC 側で Phase 1〜3（探索・設計・確認）を実行：

- 既存 spec-architect / onboarding の内部構造を Explore で把握
- DH 哲学ドキュメント群（DH-PHILOSOPHY-INSIGHTS / INTENT.md / DIMENSIONS.md / philosophy.md / council-philosophy.md）の参照箇所整合性検証
- Plan agent で配置案A/B 両論併記の実装計画立案
- AskUserQuestion で 4 論点を確定（配置 A / Phase γ 分離 / 動的起動オプション / minor 判定）

### Step 1: archeo-architect SK 雛形の新設

`.claude/skills/layer0-archeo-architect/` を新設、6 ファイル：

- `SKILL.md` — frontmatter `dimension: D4`、3 原則 (P-Arch-1/2/3)、7 ステップ対話フロー、§7.4 自己検証
- `assets/refactor-intent-map-template.md` — Meta / Islands / Boundaries / Absent-Intent Zones の 4 セクション、4 値必須フィールド
- `references/dialog-flow-archeo.md` — Step 1〜7 の対話文型、Step 3 horizontal vs Step 7 vertical の分離規約、5 問上限自己制限規約
- `references/intent-hypothesis-protocol.md` — 仮説生成ヒューリスティック（コメント不在 / 命名混乱 / 重複ロジック / git log 不在 / テスト不在 / マジックナンバー / TODO/FIXME / deprecated 痕跡）と確度規約 3 段階（code_check / git_log_check / ai_inference）
- `references/absent-intent-protocol.md` — `absent` 確定条件（人間明示宣言必須）と捏造防止規約（P-Arch-2 物理実装、3 メカニズム）
- `references/handoff-to-evaluator.md` — `refactor-intent-map.md` の I/O 規約（Phase γ 先行宣言版）

### Step 2: spec-architect SKILL.md 責務分担表の更新

`.claude/skills/layer0-spec-architect/SKILL.md`:
- §L0 スキル間の責務分担表に「リファクタ前 意図復元」行を追加（archeo-architect、4 行目）
- 排他ルールに 4 項目追加（archeo は再利用可能 / archeo は自動起動しない / spec-architect と同時起動禁止 / 既存ルール維持）

### Step 3: dev-env-spec.md Level A 一覧の更新

`.claude/skills/layer0-spec-architect/references/dev-env-spec.md`:
- Level A（共通スキル）一覧に `layer0-archeo-architect（再利用可能、v5.4.0 追加）` を追加

### Step 4: 履歴層更新

- `history/INTENT.md` に v5.4.0 セクションを追加（archeo-architect 設計意図 / Phase 化 / 配置論点 / v6.0.0 候補温存）
- 本 CHANGELOG.md に v5.4.0 セクション追加（本セクション）

### Step 5: 自己検証 + 献上

- harness-verifier 5 検査全 PASS（D4 整合性維持確認）
- 計算的センサー: SKILL.md / references の構文整合・broken reference なし
- archeo SK 6 ファイル + spec-architect 軽微修正の整合性確認
- ルートに draft PR を作成し、ひでさんレビュー待ち

### 本リリースの範囲外

- **Phase γ（L1 改修）**: layer1-autonomous-dev SKILL.md §6 / inferential-sensor-v2.md / layer1-independent-reviewer SKILL.md への意図合致軸追加。**v5.5.0 候補**として継続検討
- **Phase β（ritual-protocol 統合・glossary 用語追加）**: 本リリースに同梱しない（α 完了後の用語確定を待つ）。**v5.4.x 候補**
- **Phase δ（spec-architect 逆輸入）**: 運用データ 3 ヶ月蓄積後、Council 諮問で実施可否判定。**v6.0.0 候補**として温存

## 2026-05-01 命名整備: Lifecycle → LC（v5.3.0 patch、no version bump）

DH 本体の `Lifecycle L=N` 表記を `LC=N` に統一する命名整備。Layer (`L0/L1/L2`) と Lifecycle (`L=0/L=1/L=2`) の `L` + 数字命名衝突を解消する。`crosscut-council` 諮問の結果、経営者/開発者/哲学者の 3 ペルソナで「進行可、ただし 3 条件付き」の重み付き判定（`history/COUNCIL-LOG.md` 参照）。

機能変更なし、後方互換維持（`harness-verifier/glossary.yml` の `lifecycle:` セクションは旧表記 `L=0/L=1/L=2` `Lifecycle 0/1/2` `Lifecycle L=0/L=1/L=2` を全て alias として保持）。バージョンアップなし。

### 変更内容

- `harness-verifier/glossary.yml`: キー `L=0/1/2` を `LC=0/1/2` に変更、旧表記を aliases に保持
- `.claude/skills/` 配下 markdown 群: `Lifecycle L=N` / `Lifecycle ≥N` / `Lifecycle ≤N` / `L=N` / `Lifecycle 別` / `Lifecycle 軸` / `Lifecycle 判定` / `Lifecycle記録` / 表ヘッダ `| Lifecycle |` 等を機械置換 + 残存手動補正
- `history/INTENT.md`: 旧「Lifecycle → LC 命名変更計画（保留中）」節を「（✅ 完了）」に変更し、実施記録を追記
- `history/REGIME-LOG.md`: 本サイクルを記録
- `history/COUNCIL-LOG.md`: PR #30 open のまま進行する判定の Council 諮問を記録

### 触らなかったファイル（後方互換のため）

`delivery/` 配下の version snapshot、`dh-upgrades/upgrade-spec-v5.0.0.md`、`docs/migration-guide-v5.1.0.md`、`history/CHANGELOG.md` v5.0〜v5.3 既存エントリ、`history/REGIME-LOG.md` 既存エントリ、`history/ARCH-DECISIONS.md` 全エントリは時系列の歴史的事実として保持。

### Council 判定の前提条件 3 件

1. INTENT.md の発動条件記述を「並列実行・衝突は rebase で解消」に更新 ✓
2. PR #30 衝突 4 ファイル（`layer0-spec-architect/SKILL.md` / `dev-env-spec.md` / `INTENT.md` / `CHANGELOG.md`）は PR #30 新規行に触れず、既存 Lifecycle 言及行のみ置換 ✓
3. harness-verifier 全項目 PASS ✓

## v5.3.0 (released 2026-04-30)

minor 昇格。**1 機能完遂の自律駆動 WF を「形状単一・薄い基底」として確定**し、献上トリガー Type D（異常献上）を新設。
HANDOFF「1 機能完遂の自律駆動 WF 設計」2026-04-30 と Council 合議（`council-2026-04-30T14:30:00Z-wfsurf1` / `council-2026-04-30T14:50:00Z-wfbase1`）を起源とする。
後方互換維持（v5.0.0 / v5.1.0 / v5.2.0 と同パターン）。利用者プロジェクトには配布されない。

`crosscut-verifier-philosophy` 本実装は本リリース対象外（v5.3.x または v5.4.0 候補へ再々後送）。

### Step 0: L0 設計献上の確認

L0 (spec-architect) で 5 phase 完了（論点 1 / 2 / 3 + 認識ズレ確認 + 落とし込み）。
献上物: `delivery/L0-WF-DESIGN-2026-04-30.md`。AD-015 / AD-016 / AD-017 で実装スコープを確定。

### Step 1: philosophy.md §5 に Type D 追加

`.claude/skills/layer0-spec-architect/references/philosophy.md`:
- §タイプD（異常献上）節を追加（タイプC の後）
- §タイプ対応表に Type D 行を追加
- §タイプ二項分類の限界（v6.0.0 候補）を追加（第 8 条候補「献上 3 軸の存在論」温存記述）

### Step 2: layer1-autonomous-dev SKILL.md 三点修正

`.claude/skills/layer1-autonomous-dev/SKILL.md`:
- §原則に「WF 形状単一性」原則を 1 項目追加
- §8 献上の表を 2 種 → 4 種に拡張（Type A / B / C / D）
- §DELIVERY.md 抜粋（イメージ）に Type D 行を追加

### Step 3: delivery-format.md に Type D 節と表更新

`.claude/skills/layer1-autonomous-dev/references/delivery-format.md`:
- §献上物タイプ一覧表に Type D 行を追加
- §タイプA と D の差異を明示
- §献上物タイプD（異常献上）節を新設（プロトコル / 構造 / 記述ルール）

### Step 4: wf-baseline-rationale.md 新設

`.claude/skills/layer1-autonomous-dev/references/wf-baseline-rationale.md` を新設：
- 採用方針（基底 WF / 機能タイプ別 WF 群を作らない理由 / 厚化閾値 / 観測対象外）
- 第 3 の道（v6.0.0 候補）の温存記述
- 関連レコードへのリンク（AD / INTENT / COUNCIL / philosophy）

### Step 5: 履歴層更新

- `history/ARCH-DECISIONS.md` の「v5.3.0 候補」→「v5.3.0」確定昇格
- `history/INTENT.md` の同上
- `history/REGIME-LOG.md` に v5.3.0 セクション追加
- 本 CHANGELOG.md に v5.3.0 セクション追加（本セクション）

### Step 6: 自己検証 + 独立検証 + 献上

- harness-verifier 5 検査全 PASS（D4 整合性維持確認）
- 計算的センサー: SKILL.md / references の構文整合・broken reference なし
- 推論的センサー: 「仕様に合う・動く・使える」3 観点で自己評価 PASS
- 独立検証 (layer1-independent-reviewer) スコープ: SK/RL/WF 規約整合
- 献上物: `delivery/SELF-VERIFICATION-v5.3.0.md` + `delivery/L1-DELIVERY-v5.3.0.md`

## v5.2.0 (released 2026-04-30)

minor 昇格。次元論（D1〜D5）導入と D4 検査機構（`harness-verifier/`）の独立配置。
HANDOFF「DH 自己検証機構（誤作動防止機構との統合検討用）」2026-04-29 と
Council 合議（invocation_id: council-2026-04-29T21:00:00Z-d4mtr1, 4 論点一括）を起源とする。
後方互換維持。利用者プロジェクトには配布されない。

`crosscut-verifier-philosophy` の本実装は本リリース対象外（v5.3.0 候補へ再後送）。

### Step 0: Council 合議

L0 対話中にユーザー指示で `crosscut-council` を起動、4 論点を一括諮問：

1. 次元論の命名統一（案 a: D-numbering / 案 b: T-numbering / 案 c: 階層形容詞）
2. D4 検査機構の名称（meta-verifier / harness-verifier / dh-integrity / singularity）
3. バージョン昇格区分（v5.2.0 minor / v6.0.0 major / v5.2.0 + v5.3.0 後送）
4. 検証スコープ 5 項目の D4 対象妥当性

3 ペルソナ並列独立発言 → 重み付き Judgment Agent 出力で全論点 final_decision: null、
合意プロセスで agreed_recommended 確定（implementer_consent 後追記済）。

### Step 1: harness-verifier/ スキャフォールド

リポジトリルート直下に新規ディレクトリを配置：

- `harness-verifier/README.md` — 概要、5 次元論サマリ、5 検証項目、独立性原則、実行方法
- `harness-verifier/PHILOSOPHY.md` — 規律の自己相似性、自己検証機構の存在論（singularity 別名併記）
- `harness-verifier/BOUNDARY.md` — DH 本体との境界線、責務マトリクス、依存方向、5 層構造保全の D4 解釈
- `harness-verifier/HUMAN-PROTOCOL.md` — 月次運用、レポートフォーマット、D5 判断カテゴリ、エスカレーション、形骸化防止
- `harness-verifier/glossary.yml` — 用語辞書（version 0.1.0、12 カテゴリ）

### Step 2: Python 検査本体

Python 標準ライブラリのみ（外部依存ゼロ、独立性要請の担保）：

- `harness-verifier/verify.py` — メインスクリプト、`--report` / `--strict` / `--json` / `--commit-sha` フラグ対応
- `harness-verifier/checks/__init__.py` — モジュールパッケージ
- `harness-verifier/checks/frontmatter.py` — 検証 1: SKILL.md frontmatter（name kebab-case + ディレクトリ名一致 + description 30-1024 chars）
- `harness-verifier/checks/references.py` — 検証 2: Markdown インラインリンクの dead link 検出（拡張子フィルタ + アンカー除去）
- `harness-verifier/checks/dependency_graph.py` — 検証 3: 未定義 skill 参照と自己参照検出（意図的相互参照は許容）
- `harness-verifier/checks/five_layer_structure.py` — 検証 4: 5 層検出スタックの canonical 名整合（5 層検出スタック文脈フィルタで誤検出回避）
- `harness-verifier/checks/glossary.py` — 検証 5: 簡易 YAML パーサ + forbidden_uses 検出 + crosscut/layern prefix members の実体整合

### Step 3: GitHub Actions ワークフロー

`.github/workflows/harness-verify.yml` を新設：

- cron `0 0 1 * *`（毎月 1 日 09:00 JST）で月次レポート自動 commit
- push / pull_request の `.claude/skills/**` または `harness-verifier/**` 変更で trigger
- `--strict` モードで CI 厳格判定、月次のみ `--report` でファイル生成
- `permissions: contents: write` で月次レポート自動 commit を許可

### Step 4: SKILL.md v5.2.0 セクション追加

`.claude/skills/layer0-spec-architect/SKILL.md` の参照ドキュメント節に v5.2.0 セクションを追加。
次元論サマリと harness-verifier 配置・スコープを記述。L0 起動フローには影響しない（情報依存しない設計）。
既存 §0〜§7.6 のセクション番号は不変、v5.1.0 セクションも不変、その上に積層。

### Step 5: 履歴層更新

- `history/INTENT.md`: v5.2.0 セクション追加（5 次元論確立 / D4 検査機構の独立配置 / 自己言及パラドックスの構造的回避）
- `history/ARCH-DECISIONS.md`: AD-010（5 次元論導入と D-numbering 採用）/ AD-011（DH 本体外への独立配置）/ AD-012（harness-verifier 命名判断）/ AD-013（v5.2.0 minor 昇格と philosophy verifier 後送）追加
- `history/REGIME-LOG.md`: v5.2.0 minor 昇格記録（不変項目遵守確認、改修体制、次バージョン予定 v5.3.0/v6.0.0）
- `history/CHANGELOG.md`: 本セクション
- `history/COUNCIL-LOG.md`: 4 invocation entry を追加（invocation_id 共通鍵、implementer_consent: agreed_recommended 後追記）

### Step 6: §7.4 自己検証 + 献上

`delivery/SELF-VERIFICATION-v5.2.0.md` 配置。
broken reference / DONT 自己照合 / Pre-flight 充足 / 受け入れ基準充足 / harness-verifier smoke test の 5 チェック実行。
本案件はメタスキル本体改修（D4 改修）であるため、scaffold-checklist.md の Vite+TS+React+PWA stack は適用対象外（D2 検査の責務、本案件の対象次元と異なる）。

### Step 7: 独立検証 (layer1-independent-reviewer) FAIL → C-1/C-2/C-3 修正

`delivery/VERIFICATION-v5.2.0.md` で M2 必須独立検証実施、初版 FAIL 判定（重要 1 + 警告 2）：

- C-1: `_parse_yaml` が複数行 block list 構文を誤読、検査 5 が空回り
- C-2: monthly cron の FAIL がメール通知されない（`|| echo` で吸収）
- C-3: SELF-VERIFICATION の根拠補強（C-1 修正で自然解消）

C-1 解決方針を Council 諮問（invocation_id: council-2026-04-29T22:30:00Z-c1fix1）。
全会一致で「案 b 中核 + 案 a 防御 + 哲学者ドキュメント宣言」三段統合（judgment_confidence 0.88）を承認。

実施内容：

- `harness-verifier/glossary.yml` を subset YAML 形式に書き換え（forbidden_uses / crosscut_prefix.members / layern_prefix.members をインライン化、冒頭コメントで形式制約を明示）
- `harness-verifier/checks/glossary.py` の `_parse_yaml` を全面改修：
  - 複数行 block list 構文 (`- item`) を検出時に `SyntaxError` を raise（黙って誤読しない）
  - `_split_top_level` でネスト構造を尊重した top-level 分割を実装
  - `_parse_inline_value` でインライン list / list of dict / dict / scalar を統一処理
  - key 正規表現に `=` を許可（`L=0`, `L=1`, `L=2` 等の Lifecycle キーを glossary で扱える）
- `harness-verifier/BOUNDARY.md` に §9「独立性の代償（subset YAML 制約、AD-014）」を追加
- `harness-verifier/glossary.yml` の `forbidden_uses` を「絶対に使うべきでない語」に絞り込み、予約語/未実装語（L3 運用層、T1-T5）は除外（否定文脈での言及は正当）
- `.github/workflows/harness-verify.yml` の monthly 経路を `continue-on-error: true` + 末尾 fail step で修正、HUMAN-PROTOCOL.md §4 のメール通知エスカレーションが機能するよう整合化（C-2 解消）
- `history/ARCH-DECISIONS.md` に AD-014（subset YAML 形式判断）を追加
- `history/COUNCIL-LOG.md` に invocation entry 追加
- `delivery/SELF-VERIFICATION-v5.2.0.md` に C-1〜C-3 解消反映を追記
- `delivery/VERIFICATION-v5.2.0.md` を PASS 化（独立検証再判定）

最終 smoke test: `python harness-verifier/verify.py --strict` で 5 検査全て **意味のある PASS**（検査 5 の forbidden_uses / prefix 整合検査が実走、検出 0 件は実態として違反なし）。

## v5.1.0 (released 2026-04-28)

minor 昇格。L0 受け入れ基準の明文化 / Pre-flight 必読化 / scaffold checklist / §7.4 自己検証ステップを追加。
PR #19 テストレビュー（シナリオ「ケロぴの森」）で判明した L0 charter 未達 P0 4 項目（受け入れ基準・Pre-flight・scaffold・自己検証）を解消する。後方互換維持。

`crosscut-verifier-philosophy` の本実装は本リリース対象外（v5.2.0 候補として継続検討）。

### Step 1: §0 受け入れ基準明文化

`.claude/skills/layer0-spec-architect/SKILL.md` §0「原則」に「L0 完了の受け入れ基準（v5.1.0 追加）」を新設し、4 条件を明文化：仕様充足 / scaffold 実体生成 / smoke test 通過（または保留事由明記）/ §7.4 自己検証 PASS。Lifecycle ≥ 1 の既存プロジェクトには段階適用（既存成果物の遡及修正は不要）の旨を併記。

### Step 2: Pre-flight 必読指定

主要ステップ冒頭に「**Pre-flight (v5.1.0)**: 起動前に X を必読」行を追加：

- §1.5 振り返り儀式 → `references/ritual-protocol.md`
- §3.5 サブフェーズ選定 → `references/subphase-selection.md`
- §4 モード判定 → `references/regime-assessment.md`（dev_mode 判定セクション含む）
- §6 開発環境構築 → `references/dev-env-spec.md` + `references/scaffold-checklist.md`
- §7 出力 → `assets/credit-template.md`

§7.5 / §7.6 は既存 references の参照で充足するため Pre-flight 行追加なし。

### Step 3: scaffold-checklist.md 新設

`.claude/skills/layer0-spec-architect/references/scaffold-checklist.md` を新規作成。v5.1.0 標準 stack を Vite + TypeScript + React + PWA に固定し、12 種の必須生成ファイル（package.json / tsconfig / vite.config / vitest.config / playwright.config / biome / .gitignore / index.html / src/main.tsx / src/App.tsx / public/manifest.webmanifest / public/icons）と smoke test 4 コマンド（pnpm install / dev / build / test）を規定。
他 stack（Next.js / Vue / Astro / SvelteKit / 純 Node CLI）は将来 minor で追加。

`references/dev-env-spec.md` の「開発環境構築時の初期化」リスト末尾に scaffold-checklist.md への相互参照 1 行を追加（既存内容は不変）。

### Step 4: §7.4 自己検証ステップ追加

`.claude/skills/layer0-spec-architect/SKILL.md` の §7（出力）と §7.5 の間に「### 7.4. L0 自己検証（v5.1.0 追加）」を新設。5 件のチェック項目をチェックボックス形式で配置：broken reference 検査 / scaffold smoke test 検査 / DONT 自己照合 / Pre-flight 充足 / 受け入れ基準充足。FAIL があれば §7（出力）に進まず原因解消する旨を明記。既存 §7.5 / §7.6 のセクション番号は不変。

### Step 5: バージョン更新

- `assets/credit-template.md`: v5.0.0 → v5.1.0
- `.claude/skills/layer0-spec-architect/SKILL.md` の参照ドキュメント節に「### v5.1.0 追加（L0 受け入れ基準明文化・Pre-flight 必読化・scaffold checklist・自己検証ステップ、minor 昇格）」セクションを追加（既存 v5.0.0 セクションは不変、その上に積層）
- `history/CHANGELOG.md`: 本セクション追加
- `history/REGIME-LOG.md`: minor 昇格記録（不変項目遵守確認・改修体制・既存 v5.0.0 セクション保持）
- `history/ARCH-DECISIONS.md`: AD-008（L0 完了基準の再定義）/ AD-009（scaffold-checklist の単一 stack 採用方針）追加
- `history/INTENT.md`: v5.1.0 の意図追記（L0 charter 達成可能性の確保・Pre-flight 強制化）

## v5.0.0 (released 2026-04-28)

major 昇格。dev_mode 軸追加 / crosscut- prefix 統一 / 仕様 1〜4 Skill 化 / CTL 連動 / GitHub Actions 雛形 / 業界 BP 取り込み（claude-code-action）。

詳細は `dh-upgrades/upgrade-spec-v5.0.0.md` 参照。

### Step 0: scaffold

- `dh-upgrades/`, `history/`, `docs/`, `delivery/` 新規作成
- `dh-upgrades/upgrade-spec-v5.0.0.md` 配置（1500 行、自己改修指示書）
- `.gitignore` に `docs/migration-guide-*.md` 例外追加（AD-007）

### Step 1: crosscut- リネーム（後方互換破壊）

- `git mv .claude/skills/council .claude/skills/crosscut-council`（17 ファイル、履歴保持）
- `crosscut-council/SKILL.md` frontmatter: `name: council` → `name: crosscut-council`、description に「横断判定機構（crosscut prefix）」明記
- 外部参照パス更新（4 ファイル / 8 箇所）:
  - `layer1-autonomous-dev/SKILL.md`: `\`council\`` → `\`crosscut-council\`` (4) + path 2
  - `layer0-spec-architect/references/regime-assessment.md`: path 2
  - `layer0-spec-architect/references/philosophy.md`: path 4
- `.gitignore`: `council-workspace/` → `crosscut-council-workspace/`
- 残留: `crosscut-council/references/design-history.md` の歴史記述 2 箇所のみ（spec §4.1.3 で許容）
- 維持: `~/.claude/council-data/` 横断蓄積パス（spec §3.2.8 でユーザースコープ固定）

### Step 2: dev_mode 軸追加

- `layer0-spec-architect/SKILL.md` §4 モード判定に「dev_mode 軸（v5.0.0 追加）」サブセクション追加
- `references/regime-assessment.md` 末尾に「dev_mode 判定（v5.0.0 追加）」セクション追加（モード境界 / 2 段階判定プロトコル / REGIME.md 記録形式 / 昇格降格規則）
- `assets/meta-spec-template.md` の REGIME.md テンプレに `## dev_mode` セクション追加（mode / ctl / 判定根拠）
- 注記: spec §3.1.1 のチーム軸（T1-T5）は v5.0.0 では未実装。規模 + Lifecycle を proxy として運用。チーム軸 operational 化は v5.x で扱う（INTENT.md 記録）

### Step 3: 仕様 1〜4 Skill 追加

5 つの crosscut- skill を新規作成（spec §4.3）：

- `crosscut-issue-dispatcher/SKILL.md`（仕様 1：Issue 射出）
- `crosscut-issue-implementer/SKILL.md`（仕様 2：Issue → 実装、claude-code-action 公式採用注記）
- `crosscut-verifier-drift/SKILL.md`（仕様 3-drift：SPEC/ADR 乖離検証、5 層検出スタックの追加層）
- `crosscut-verifier-philosophy/SKILL.md`（仕様 3-哲学：placeholder、v5.1.0 で本実装）
- `crosscut-feedback-loop/SKILL.md`（仕様 4：種別ごとの還流先決定）

各 SKILL.md は frontmatter + 発動条件 + 処理フロー + CTL 別動作 + 関連参照のみのタイト構成。protocol references は Step 4 で追加。

`layer1-autonomous-dev/SKILL.md` および `layer1-independent-reviewer/SKILL.md` の関連スキルセクションに crosscut- 系参照を追加（spec §4.3.4 完了条件）。

### Step 4: CTL 連動 protocol + maturity strategy

各 crosscut skill に CTL 別動作の references を追加（spec §4.4）：

- `crosscut-issue-dispatcher/references/dispatch-protocol.md`
- `crosscut-issue-implementer/references/implement-protocol.md`
- `crosscut-verifier-drift/references/verify-protocol.md`
- `crosscut-feedback-loop/references/feedback-protocol.md`

各 protocol.md は github_assisted / github_autonomous × CTL-0/1/2/3 の動作表を本体化、Council 事前検証発動条件 + CHANGELOG 記録形式を含む。

`crosscut-council/references/ctl-maturity-strategy.md` を新規作成（spec §4.4.2.2、既存 `ctl-calculation.md` に育成戦略の項なしと確認済）。CTL 段階定義 / 量×質ハイブリッド昇格条件 / 横断蓄積補強 / 退行ロジック / CHANGELOG 自動記録形式を含む。

### Step 5: GitHub Actions 雛形配置

`templates/.github/workflows/` を新設し 9 yml を配置（spec §4.5）：

- `basic-ci.yml`（既存検出スタック第1層 + Shift Left 基盤の CI 化）
- `e2e-ci.yml`（既存検出スタック第2層、Playwright Test Agents 規格）
- `interaction-cost.yml`（既存検出スタック第3層、UX 計算可能代理指標）
- `spec-drift.yml`（crosscut-verifier-drift の CI 化）
- `issue-dispatch.yml`（crosscut-issue-dispatcher の CI 化、CTL 連動 + Council 事前検証）
- `issue-to-impl.yml`（crosscut-issue-implementer の CI 化、claude-code-action `<latest>` プレースホルダ）
- `drift-feedback.yml`（crosscut-feedback-loop の CI 化、種別→還流先マトリクス実装）
- `auto-merge.yml`（CTL ≥ 2 + 全条件達成時のみ squash merge）
- `auto-degrade.yml`（連続失敗・重大インシデントで dev_mode + ctl 自動降格）

各 yml 冒頭に `# Required mode:` `# Required CTL:` をコメント明記。

`layer0-spec-architect/references/dev-env-spec.md` の参照権限マトリクスに `templates/` 行を追加（v5.0.0 追加、配布雛形のため AI 書 ✅・Human 書 △）。

### Step 6: バージョン更新（v5.0.0 major 確定）

- `assets/credit-template.md`: バージョン記法を semver 厳格化（`vX.Y` → `vX.Y.Z`、v4.x 互換受理を明記）
- `layer0-spec-architect/SKILL.md` の参照ドキュメント節に `### v5.0.0 追加（GitHub 連携前提化・crosscut prefix 確立・semver 化、major 昇格）` セクション追加
- `history/REGIME-LOG.md` を本格化：major 昇格記録（破壊項目テーブル・非破壊追加・移行方針・不変項目遵守確認・改修体制・次バージョン予定）
- README バッジ作業はスキップ（README 不在のため、SELF-VERIFICATION §5.3 で「適用対象外」明記予定、AD-006）

### Final: migration guide + self-verification

- `docs/migration-guide-v5.0.0.md`: 既存プロジェクト向け移行手順書（必須 5 + 任意 5 + 後退 + Q1-Q5）
- `delivery/SELF-VERIFICATION-v5.0.0.md`: 自己検証結果（PASS、5.3.2 README バッジは適用対象外）

総合判定 PASS。次フェーズでユーザー側 spec §6 + layer1-independent-reviewer 独立検証へ。

### Fix: skill-creator 監査 MEDIUM-1（誤発動防止）

ユーザー要求に基づき skill-creator 視点での独立監査を実施。検出 1 件（MEDIUM-1）を本コミットで fix：

- `crosscut-verifier-philosophy/SKILL.md` description: 冒頭に「**v5.0.0 では発動禁止 / DO NOT TRIGGER in v5.0.0**」を明示配置。トリガー語句を「v5.1.0 以降の想定トリガー語句（v5.0.0 では非トリガー）」と未来形で再表記。731 chars（1024 制限内）。
- 監査レポート `delivery/SKILL-CREATOR-AUDIT-v5.0.0.md` 配置（PASS 判定 + LOW 2 件は次回改修課題として記録）。

LOW-1（SKILL.md と protocol.md の CTL 表部分重複）と LOW-2（placeholder の references 不在）は本リリースでは触らず、次回改修時の課題として監査レポートに記録。

### Independent Review: layer1-independent-reviewer 起動・PASS

M2 体制完結のため `layer1-independent-reviewer` を起動し独立検証を実施：

- `delivery/VERIFICATION.md` 配置（PASS、提起 3 件は全て注記のみ）
- 提起内容:
  - C-1: SELF-VERIFICATION §5.4.2 ラベリング不整合（同根因 AD-006 で対応済）
  - C-2: メタ案件としての DELIVERY/HANDOFF 兼任注記欠如（次回参考、機能影響なし）
  - C-3: spec §5.2.4 disabled/ 原則項目（本リリース対象外）
- L1 自己検証 / skill-creator 監査 / 本独立検証の 3 視点で判定整合（割れなし）
- L2 統合検証は不要（単一ドメイン、L2 閾値未達）

→ ready-for-review 化可能。最終承認は人間判断（spec §6 哲学的整合性 + サンプルプロジェクト試運転）。

### Fix: Copilot review (3 件、最小権限明示)

PR #18 への Copilot レビュー 3 件すべてに対応。GitHub Actions の最小権限規約に基づき、各 yml に `permissions:` を追加：

- `templates/.github/workflows/issue-dispatch.yml`: `contents: read` + `issues: write`（gh issue create）
- `templates/.github/workflows/drift-feedback.yml`: 既存 issues/pull-requests に `contents: read` 追加（actions/checkout が default-none で失敗するため）
- `templates/.github/workflows/spec-drift.yml`: `contents: read` + `issues: write` + `pull-requests: write` + `actions: write`（github-script + gh workflow run drift-feedback.yml）

テンプレートとして最小権限を明示することで、デフォルト read-only な GITHUB_TOKEN 設定のリポジトリでもそのまま動作する形になった。yaml syntax は引き続き全 PASS。
