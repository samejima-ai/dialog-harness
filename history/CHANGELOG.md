# CHANGELOG

DH 本体の改修履歴。各 Step の実行記録を時系列で追記する。

## v5.2.0 (in progress)

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

## v5.1.0 (in progress)

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

## v5.0.0 (in progress)

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
