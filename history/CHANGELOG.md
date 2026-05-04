# CHANGELOG

DH 本体の改修履歴。各 Step の実行記録を時系列で追記する。

## v5.7.2 (in progress, target 2026-05-04)

> **記録規約**: PR draft / ready-for-review 中は `(in progress)` で記録、merge 時に `(released YYYY-MM-DD)` 化。本 v5.7.2 が **8 例目正規適用**。

**patch 昇格**。**`anthropics/claude-code-action@v0` の OIDC token 取得失敗 bug 修正**。

Issue #46（v5.8.0 候補 `crosscut-issue-quality-gate` 設計）を実装トリガーとして v5.7.1 機構の初の本番テストを実施したところ、`Failed to setup GitHub token: Error: Could not fetch an OIDC token. Did you remember to add 'id-token: write' to your workflow permissions?` で workflow が exit 1 で終了。`anthropics/claude-code-action@v0` が OIDC で token 取得を試みるが、`issue-pickup.yml` の `permissions:` ブロックに `id-token: write` が含まれていなかった。v5.7.1 で gemini-cli → Claude Code CLI 切替時の追加漏れ。

**Council 諮問なし**（自明な single-line bug fix、複数案拮抗なし、不可逆操作なし）。**後方互換完全維持**（permission 追加は既存挙動に影響しない）。

### Step 1: 履歴層

- 本セクション
- INTENT.md v5.7.2 設計意図
- REGIME-LOG.md v5.7.2 patch 判定
- ARCH-DECISIONS.md AD-030 追加（OIDC permission 追加、v5.7.1 bug 修正記録）

### Step 2: workflow + template

- `.github/workflows/issue-pickup.yml` `permissions:` に `id-token: write` 1 行追加
- `templates/github-workflows/issue-pickup.yml.template` 同上

### Step 3: 動作確認（merge 後の actual）

- Issue #46 の `in-progress` ラベルを除去 + `ready-for-ai` 再付与で再 trigger
- `claude-code-action@v0` が OIDC token 取得 → 実装本体起動 → PR 作成まで完遂を確認
- 副次目的: 本 PR 自身が **v5.7.2 fix の有効性検証 + Issue #46 (v5.8.0) の autonomous-drive 完遂** のダブルテストを兼ねる

## v5.7.1 (released 2026-05-03)

> **記録規約**: PR draft / ready-for-review 中は `(in progress)` で記録、merge 時に `(released YYYY-MM-DD)` 化（v5.5.0 で確立、本 v5.7.1 が **7 例目正規適用**）。同 PR で v5.7.0 (in progress) → (released 2026-05-03) 化を housekeeping として同梱。

**patch 昇格**。**実装エージェント方式の見直し（gemini-cli → Claude Code CLI メイン化、AD-026 訂正）**。

ユーザー要請「実装は Anthropic Claude Code CLI で実行したい、サブスクで稼働、Gemini はフォールバック」を起源として、L0 spec-architect セッションで策定された HANDOFF (`delivery/HANDOFF-v5.7.1-claude-code-pivot.md`) に基づく実装。

**新事実発見**: Anthropic Pro/Max サブスクリプション + `CLAUDE_CODE_OAUTH_TOKEN` 経由で Claude Code CLI を GitHub Actions で **追加 API 課金なし** で稼働可能。v5.7.0 AD-026「Anthropic API 回避で gemini-cli 採用」の前提が変わった → AD-029 で訂正。

**後方互換完全維持**: philosophy.md 改訂なし、既存 SKILL.md セクション番号不変、利用者プロジェクトへの強制配布なし。**Council 諮問なし**（11+7 論点全て対話で合意、複数案拮抗なし、confidence ≥ 0.7）。

### Step 1: 履歴層 + housekeeping

- 本セクション
- INTENT.md v5.7.1 設計意図
- REGIME-LOG.md v5.7.1 patch 判定
- ARCH-DECISIONS.md AD-029 追加（Claude Code CLI 採用、AD-026 訂正記録）
- v5.7.0 (in progress) → (released 2026-05-03) 化同梱

### Step 2: crosscut-issue-implementer skill 改修

- SKILL.md frontmatter description + 本文の実装エージェント記述を「Claude Code CLI メイン + gemini-cli フォールバック」へ
- references/triage-protocol.md: AI triage は gemini-cli メイン継続を明文化
- references/setup-checklist.md: `CLAUDE_CODE_OAUTH_TOKEN` 取得手順追加（Anthropic Console、Pro/Max サブスクリプション前提）

### Step 3: workflow + template

- `.github/workflows/issue-pickup.yml`: `anthropics/claude-code-action@v0` 統合 + `CLAUDE_CODE_OAUTH_TOKEN` 認証 + 失敗時 `pickup-failed` label + notice（フォールバック自動化なし、人間 P4 判断）
- `templates/github-workflows/issue-pickup.yml.template`: 同等改訂

### Step 4: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 5 検査 PASS
- `delivery/SELF-VERIFICATION-v5.7.1.md` 作成
- 本 PR は ready-for-review + `auto-merge` label で autonomous-drive loop **7 例目** として投入

## v5.7.0 (released 2026-05-03)

> **記録規約**: PR #44 (2026-05-03 merged) の `(in progress)` 状態を本 v5.7.1 patch に同梱して `(released 2026-05-03)` 化（**7 例目正規適用**）。housekeeping を独立 PR にせず同梱の運用が継続的に定着。

> **記録規約**: PR draft / ready-for-review 中は `(in progress)` で記録、merge 時に `(released YYYY-MM-DD)` 化（v5.5.0 で確立、本 v5.7.0 が 6 例目正規適用）。同 PR で v5.6.0 (in progress) → (released 2026-05-03) 化を housekeeping として同梱。

**minor 昇格**。**autonomous-drive 入口側（Issue → AI pickup → 実装開始）本格稼働 + Issue 選別機構**。

ユーザー（ひでさん）の根源要請「Bを考えよう（自前 workflow 実装）」+ 「Issue 選択は開発品質を決めると言って過言ではない」を起源として、L0 spec-architect セッションで策定された HANDOFF (`delivery/HANDOFF-v5.7.0-issue-pickup.md`) に基づく実装。

**実装方式**: gemini-cli 流用（既存 GEMINI_API_KEY、追加コスト 0、Anthropic API 回避）。
**Council 諮問**: なし（11 論点全て対話で合意、起動条件未満）。

**後方互換完全維持**: dev_mode `autonomous` + `autonomous_scope: full` のみで enable。利用者プロジェクトには配布されない（template 配置のみ）。

### Step 1: 履歴層 + housekeeping

- 本セクション
- INTENT.md v5.7.0 設計意図
- REGIME-LOG.md v5.7.0 minor 昇格
- ARCH-DECISIONS.md AD-026 (実装方式) / AD-027 (current_focus) / AD-028 (Issue 選別 3 段階フィルター)
- v5.6.0 (in progress) → (released 2026-05-03) 化同梱

### Step 2: spec-architect 拡張 - current_focus 軸新設

- meta-spec-template.md: REGIME.md テンプレに `## current_focus` セクション追加（type / target / since / priority）
- regime-assessment.md: current_focus 判定（β 半自動 + γ ブランチ命名フォールバック）追加
- dialog-questions.md: current_focus 確認質問追加
- dev-env-spec.md: Level C に current_focus と Issue pickup の連動表追加

### Step 3: crosscut-issue-implementer skill 拡張

- SKILL.md 全面改訂（claude-code-action 前提 → gemini-cli 流用、3 段階フィルター、AI triage、circuit breaker）
- references/issue-filter-spec.md 新設（label / author / 本文 / current_focus 整合の filter ロジック）
- references/triage-protocol.md 新設（gemini-cli AI triage 二次判定）
- references/circuit-breaker-spec.md 新設（日次5/月次50 + 緊急停止）

### Step 4: workflow + template

- `.github/workflows/issue-pickup.yml` 新設（dialog-harness 自身に deploy、gemini-cli base）
- `templates/github-workflows/issue-pickup.yml.template` 新設（利用者展開用、placeholder 化）
- `spec-architect/references/autonomous-drive-deployment.md` に入口側 deployment 手順追記

### Step 5: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 5 検査 PASS（新用語 + frontmatter + path 整合性）
- `delivery/SELF-VERIFICATION-v5.7.0.md` 作成
- 本 PR は ready-for-review + `auto-merge` label で autonomous-drive loop 6 例目として投入

### v5.7.x / v6.0.0 候補として温存

- gemini-cli 実装エージェントの品質観測（fail 率測定、必要なら Council 起動でフォールバック判断）
- 新 sub-skill `crosscut-issue-drafter`（ブレスト → Issue 化支援、philosophy 第 7 条 P2 強化）
- destructive change detector / circuit breaker の実機構（v5.6.0 から累計後送中）
- ALLOWED_AUTHORS 動的化

## v5.6.0 (released 2026-05-03)

> **記録規約**: PR #43 (2026-05-03 merged) の `(in progress)` 状態を本 v5.7.0 patch に同梱して `(released 2026-05-03)` 化（6 例目正規適用）。housekeeping を独立 PR にせず本 PR に同梱の運用が継続的に定着。

> **記録規約**: PR draft / ready-for-review 中は `(in progress, target YYYY-MM-DD)` で記録、merge 時に `(released YYYY-MM-DD)` 化（v5.5.0 で確立、本 v5.6.0 が 5 例目正規適用）。同 PR で v5.5.3 (in progress) → (released 2026-05-03) 化を housekeeping として同梱。

**minor 昇格**。**autonomous-drive 標準化 + DH AI 組織論明文化**。

L0 spec-architect セッションで策定された HANDOFF（`delivery/HANDOFF-v5.6.0-autonomous-drive.md`）に基づく実装。ユーザー（ひでさん）の根源要請「自律駆動を L0 に記録、メタスキル開発」と「DH AI 組織は 4 役割 + サポートのみで完遂可能」の宣言を制度化する。

Council 諮問 `council-2026-05-03T08:30:00Z-adrv02` で β 止揚採用：deployment skill 1 つのみ新設、guardian は v5.6.x patch 温存。

**後方互換完全維持**: philosophy.md 既存 6 条改訂なし（第 7 条追加のみ）、既存 spec-architect 対話フロー不変、利用者プロジェクトへの強制配布なし。利用者プロジェクト本体には配布されない（DH 自身の運用標準化）。

### Step 1: philosophy.md 第 7 条新設「AI 組織論（4 役割 + サポート構造）」

`.claude/skills/layer0-spec-architect/references/philosophy.md` 第 7 条追加：
- **4 役割属性**: L0 設計 / L1 実装 / L2 統括 / Council 判断
- **サポート定義**: crosscut-* 非 council 系 + sub-agent は 4 役割のいずれかから呼ばれる
- **Person 責務 (P1〜P4)**: 発案 / ブレスト / 事後確認・評価 / 暴走時介入
- **第 6 条 H カテゴリとの関係**: H = 判断種別、P = 責務種別、両者は直交 2 軸（ラベル番号は偶然一致）
- **「あらゆる開発に対応」汎化性主張**: メタスキルとして他プロジェクトへ展開可能

既存 6 条は不変。

### Step 2: spec-architect 改修（autonomous_scope 軸 + Level C 追加）

- `SKILL.md`: dev_mode `autonomous` 本格定義 + `autonomous_scope`（full / merge_gated / custom）追加、§6 開発環境構築に Level C 追記
- `references/dialog-questions.md`: 自律駆動の度合い質問追加（フルオートデフォルト）
- `references/regime-assessment.md`: dev_mode `autonomous` 発動条件 + LC 連動規則
- `references/dev-env-spec.md`: 「Level C: AI 自律運用」新設
- `assets/meta-spec-template.md`: REGIME.md テンプレに `## autonomous_scope` セクション追加
- `references/autonomous-drive-deployment.md` 新設: deployment 対話レベルガイド + crosscut-autonomous-drive 起動タイミング規定

### Step 3: template 配置 + crosscut skill 新設（β 止揚採用）

- `templates/github-workflows/` 新設
  - `gemini-review.yml.template`（dialog-harness 自身の `.github/workflows/gemini-review.yml` から汎化）
  - `auto-merge.yml.template`（同上、`auto-merge.yml` から汎化）
  - placeholder 規約: `${REPO_OWNER}` / `${REPO_NAME}` / `${ALLOWED_AUTHORS}` / `${VERIFIER_JOB_NAME}` / `${SCOPE_PATHS}`
- `.claude/skills/crosscut-autonomous-drive/` 新設（deployment 専念）
  - `SKILL.md`: サポート skill としての責務定義（template 取得 → placeholder 置換 → `.github/workflows/` 配置 → label 作成 → secrets 確認）
  - `references/placeholder-spec.md`: placeholder 一覧 + 規約
  - `references/setup-checklist.md`: label / secret / PAT 設定手順

### Step 4: 履歴層更新

- `history/CHANGELOG.md` 本セクション + v5.5.3 (released 2026-05-03) 化
- `history/INTENT.md` v5.6.0 設計意図セクション
- `history/REGIME-LOG.md` v5.6.0 minor 昇格判定（M2 / LC=2 / claude-opus-4-7）
- `history/ARCH-DECISIONS.md` AD-023（autonomous-drive 標準化）/ AD-024（philosophy 第 7 条新設）/ AD-025（autonomous_scope 軸）
- `history/COUNCIL-LOG.md` `council-2026-05-03T08:30:00Z-adrv02` エントリ append

### Step 5: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 5 検査 PASS（D4 整合性維持確認、新 skill `crosscut-autonomous-drive` の frontmatter 検査 +1 を含む）
- `delivery/SELF-VERIFICATION-v5.6.0.md` 作成（L0 §7.4 自己検証の 5 項目 + philosophy 第 7 条と既存 6 条の整合性確認 + 4 役割組織論と既存 skill 配置の整合性確認）
- 本 PR は ready-for-review + `auto-merge` label で自律 loop に投入（PR #42 で実証された経路の再運用）

### v5.6.x / v6.0.0 候補として温存

- destructive change detector（diff threshold / DELETE-heavy）
- circuit breaker（5 連続 fail 自動停止）
- ALLOWED_AUTHORS 動的化（複数 contributor 体制で必要時）
- adrv01-Ph2（独立観測機構、harness-verifier 同型 crosscut skill）
- crosscut-verifier-philosophy 本実装（v5.0.0 から累計後送中、第 7 条で組織論が確定したので連動可能）
- DH AI 組織論の汎化性主張テスト（4 役割で実 N=3 別プロジェクトをカバーできるか観測）

## v5.5.3 (released 2026-05-03)

> **記録規約**: PR #42 で merge され、本 v5.6.0 patch（PR 想定）に同梱する形で `(in progress)` → `(released 2026-05-03)` 化。5 例目正規適用に該当。本 PR ハンドリング規約の確立（v5.5.0 起源）後、housekeeping を本リリースに同梱して独立 PR を増やさない運用が定着しつつある（v5.5.2 → v5.5.3 にて 1 例、本 v5.5.3 → v5.6.0 にて 2 例目）。

patch 昇格。**autonomous-drive 機構の出口側として label opt-in による PR 自動 merge workflow を新設**。

DH の crosscut-issue-implementer から続く autonomous-drive 機構（issue → AI 実装 → 多層レビュー → 自動 merge）の最終段階。今までは人間が merge ボタンを手押ししていた部分を、明示的な opt-in（label `auto-merge`）+ 多層検証（harness-verify + gemini-review + reviewDecision）通過時のみ自動化する。

**Operational behavior 追加（opt-in、後方互換完全維持）**: label が無い PR は従来通り手動 merge を要する（既定挙動の変更なし）。label 付与時のみ条件評価 → 全 pass で自動 merge。利用者プロジェクトには配布されない。

### Step 1: auto-merge.yml workflow 新設

`.github/workflows/auto-merge.yml`（160 line）。trigger event:
- `pull_request`: labeled / unlabeled / opened / synchronize / ready_for_review / reopened
- `pull_request_review`: submitted / dismissed
- `check_suite`: completed

評価条件（全て満たす場合のみ squash merge）:

| # | 条件 | 目的 |
|---|---|---|
| 1 | label `auto-merge` 付き | 明示的な人間の GO サイン（opt-in） |
| 2 | non-draft | 編集途中を merge しない |
| 3 | author が `ALLOWED_AUTHORS` (env) に含まれる | 信頼境界（現状: `samejima-ai` のみ） |
| 4 | `harness-verify` (job: verify) が走った場合 SUCCESS、走らなかった場合（paths 外）skip 扱い | 構造的検証通過（paths filter 起因の永久 pending 回避） |
| 4.5 | 最低 1 つの verifier (harness-verify or gemini-review) が SUCCESS で走っている | zero-check auto-merge を防ぐ guard |
| 5 | `gemini-review` (job: review) が走った場合 SUCCESS、走らなかった場合（paths 外）skip 扱い | 異質モデル独立 critic の通過 |
| 6 | `reviewDecision` が CHANGES_REQUESTED でない | 指摘解消待ちで block |
| 7 | PR state が OPEN | closed / merged を再 merge しない |

非該当 PR は notice 出力で skip（red CI にしない）、merge 時は `--squash --delete-branch`。

加えて pre-check として `GH_REVIEW_PAT` availability check を実装（fork PR / secret 欠落環境で red CI を防ぐ）。check_suite event 経由で SHA に複数 open PR が紐付く場合は merge target 曖昧として skip + warning（非決定性回避）。

### Step 2: 設計判断の記録

| 判断 | 理由 |
|---|---|
| GitHub native auto-merge ではなく workflow で直接 merge | branch protection 設定変更不要、ロジック一元管理、運用観測（notice ログ）が一元化 |
| PAT (`GH_REVIEW_PAT`) を使用 | workflow の auto GITHUB_TOKEN は別 workflow を trigger できない（無限ループ防止）が、本 workflow は別 workflow を起動しない用途 + PAT で post-merge 動作観測を統一 |
| `ALLOWED_AUTHORS` env に明示 hardcode | spec 改修扱い、変更時は L0 spec-architect 経由で REGIME.md と整合確認、不可視拡張防止 |
| harness-verify / gemini-review 両者を「走った場合のみ必須」+ 最低 1 verifier guard | 両 workflow とも paths filter があり全 PR では走らない。永久 pending を回避しつつ zero-check auto-merge も防ぐ（Copilot review #42 で初版「harness-verify は paths filter なし」事実誤認を訂正） |
| GH_REVIEW_PAT availability pre-check + multi-PR 検出 skip | fork PR / secret 欠落で red CI 化を防ぐ + check_suite head SHA に複数 PR 紐付き時の非決定性回避（Copilot review #42 line 89 対応） |

### Step 3: 履歴層更新

- `history/CHANGELOG.md` 本セクション
- `history/INTENT.md` v5.5.3 セクション追加（autonomous-drive パイプラインとの位置づけ）
- `history/REGIME-LOG.md` v5.5.3 patch 判定記録
- `history/ARCH-DECISIONS.md` AD-022 追加
- v5.5.2 (in progress) → (released 2026-05-03) 化（同梱）

### Step 4: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 PASS（D4 整合性維持）
- 本 PR 自身は `auto-merge` label を付けない運用（初回投入の動作確認は人間 merge で実施、信頼運用は次 PR から開始）
- 次 PR で初めて auto-merge label を試験投入し、workflow が期待通り条件評価 → merge 実行することを確認する 4 例目運用

## v5.5.2 (released 2026-05-03)

> **記録規約**: 本セクションは PR #41 draft 中は `(in progress, target 2026-05-03)` で記録され、PR #41 merge (2026-05-03) で `(released 2026-05-03)` 化されるべきだったが follow-up PR が遅延した。本 v5.5.3 patch（PR #42 想定）に同梱する形で正規化（4 例目正規適用に該当）。

patch 昇格。**v5.5.1 で gemini-review 動作確立に伴い導入された診断機構の縮退**。

v5.5.1 PR #40 で gemini-review が動作完了 + 副次目的（独立 critic 機能の検証）が達成されたため、診断目的の暫定機構（`continue-on-error: true` / `GEMINI_DEBUG: "true"` / Diagnostics step 2 件）を削除。

**Operational behavior 変更（意図的、Copilot review #41 line 13 で指摘）**: `continue-on-error: true` 削除により、transient な Gemini/MCP 失敗が以前は silent success として記録されていたが、本 patch 以降は **PR check が hard-fail (red CI)** になる。本 repo のレビュー機構として fail を fail として可視化する設計判断（philosophy.md §3 情報純度の系）。

PAT 未設定環境での noisy red を避けるため `GH_REVIEW_PAT` の availability check を新設し、未設定時は GEMINI_API_KEY 不在時と同様にクリーン skip する（Copilot review #41 line 121 対応）。

self-PR の APPROVE 制約は **API レスポンスで判別する fallback 方式**で記述（v5.5.1 prompt と同形式）。author が PAT owner と同一かを workflow で判定するロジックは導入しない（unenforced repository assumption を排除、Copilot review #41 line 184 対応）。

利用者プロジェクトには配布されない。

### Step 1: gemini-review.yml の diagnostics 縮退

- **削除**: `Diagnostics — runner / docker / GitHub MCP server reachability` step（v5.5.1 で追加、原因 A 切り分け用）
- **削除**: `Diagnostics — gemini_review step outcome` step（v5.5.1 で追加、post-step outcome 確認用）
- **削除**: `Run Gemini PR review` の `continue-on-error: true`（診断時の fail 通過用、本 patch で fail を可視化）
- **削除**: `Run Gemini PR review` の `id: gemini_review`（post-step が消えたため不要）
- **削除**: `GEMINI_DEBUG: "true"` env（diagnostic 過程で必要だったが本番では token 消費過多）
- **保持**: `Upload gemini-artifacts (stdout / stderr / telemetry)` step（low cost で将来 debug 必要時に有用）
- **保持**: `actions/checkout` の `fetch-depth: 0`（本 repo の小ささから cost 極小、cli 内部 diff 計算が必要な場合に効く）
- **保持**: settings JSON の `tools.core` / `mcpServers.github.includeTools` 不在（α パッチで判明した tool exposure 阻害除去）

### Step 2: GH_REVIEW_PAT availability check 新設

`continue-on-error: true` 削除に伴い PAT 未設定で MCP server に空 token を渡すと review_write が hard-fail する事象を防ぐため、`GEMINI_API_KEY` と同形式の早期 availability check を追加。両 secret が available の場合のみ `Run Gemini PR review` / `Upload gemini-artifacts` を実行する（Copilot review #41 line 121 対応）。

### Step 3: prompt self-PR fallback 方式の維持

self-PR APPROVE 拒否は **API レスポンスで判別する fallback 方式**で prompt に記述（v5.5.1 と同形式）。author が PAT owner と同一かを workflow 側で事前判定するロジックは導入しない理由：
- author = `${{ github.event.pull_request.user.login }}` と PAT owner の比較には PAT owner の事前知識が必要（unenforced assumption）
- 他 maintainer が同 repo に PR を作った場合、APPROVE は実際に通るので強制 COMMENT downgrade は誤った検閲となる
- v5.5.2 patch 草案でハードコード化を試みたが Copilot review #41 line 184 で指摘 → API 応答ベースの fallback に revert

prompt の「出力形式」「必須実行プロトコル」セクションは v5.5.1 と同様に APPROVE/COMMENT/REQUEST_CHANGES 全選択肢を提示し、self-PR で API 拒否時のみ COMMENT fallback と明記。

### Step 4: settings JSON のコメント更新（security 注 追加）

`includeTools` 不在で github-mcp-server の **全 tool が model に expose** される（read 系のみならず write/destructive 系含む）。本 repo は信頼済み author 前提で許容するが、tool 名の正しい形式判明後の絞り込みを v5.5.x 候補として明記。

### Step 5: 履歴層更新

- `history/CHANGELOG.md` 本セクション
- `history/INTENT.md` v5.5.2 セクション追加
- `history/REGIME-LOG.md` v5.5.2 patch 判定記録
- `history/ARCH-DECISIONS.md` AD-021 追加

### Step 6: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 PASS
- gemini-review が新 prompt + diagnostics 削減後の構成で正常動作することを本 PR で検証
- 本 PR description / CHANGELOG / verification 結果の整合を gemini-review 自身が独立 critic として確認する 3 例目運用

## v5.5.1 (released 2026-05-02)

> **記録規約**: 本セクションは PR #39 の draft 中（実際は ready-for-review 開始）に書かれ、`(in progress, target 2026-05-02)` で記録されていた。本 patch（PR #39 マージ後）で `(released 2026-05-02)` へ更新。「PR draft 中は `(in progress)` / マージ時に `(released YYYY-MM-DD)` 化」フローは v5.5.0 で正規適用が確立し、本 v5.5.1 は **2 例目の正規適用**にあたる。

patch 昇格。**v5.5.0 で温存された Phase γ 残 2 件のうち、先行宣言 4（ストラングラー・フィグ / Branch by Abstraction の射程外宣言）を本実装**。先行宣言版（4 行記述）から本実装版（射程外要素列挙 / 援用と全体採用の境界線 / L1/L2 禁止規約 / v6.0.0 昇格の観測トリガー / 整合性ガード）へ昇格。先行宣言 5（失敗アンチパターン早期検出）は引き続き温存（v5.5.x patch / v5.6.0 候補）。

CHANGELOG/INTENT/REGIME-LOG/ARCH-DECISIONS の各履歴記録を伴うが、SK 本文の機能変更ゼロ（明文化のみ、後方互換完全維持）。利用者プロジェクトには配布されない。本 patch は gemini-review GitHub Action（PR #37/#38 で導入）の独立レビュー機能を実運用で初めてテストする副次目的を兼ねる。

### Step 1: handoff-to-evaluator.md 拡充

- ステータスヘッダ: 「Phase γ コア 3 件本実装版」→「Phase γ コア 3 件 + 先行宣言 4 本実装版」
- ロードマップ表: γ 残 2 件 → γ 残 1 件（先行宣言 5 のみ）+ v5.5.1 patch 行を新規追加
- 実装ステータス記述: コア 3 件 + 先行宣言 4 を v5.5.1 で本実装と明記
- 先行宣言 4 セクション本体: 4 行記述 → 5 サブセクション（(a) 射程外要素の明示列挙 / (b) 援用と全体採用の境界線 / (c) L1/L2 禁止規約 / (d) v6.0.0 昇格の観測トリガー / (e) 整合性ガード）

### Step 2: 履歴層更新

- `history/CHANGELOG.md` 本セクション
- `history/INTENT.md` v5.5.1 セクション追加（先行宣言 4 本実装の設計意図）
- `history/REGIME-LOG.md` v5.5.1 patch 判定記録（M2 / LC=1 / claude-opus-4-7、minor 昇格不要）
- `history/ARCH-DECISIONS.md` AD-020 追加（先行宣言 4 本実装、明文化のみ機能変更なし）

### Step 3: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 PASS（D4 整合性維持確認、5 検査全項目）
- gemini-review GitHub Action の発火条件（`.claude/skills/**` + `history/**` 改変、non-draft PR）を満たす最初の PR として運用テストを兼ねる
- ルートに ready-for-review PR (#39) を作成、Copilot review からの 2 件指摘（(b) テーブル矛盾 / AD-020 「3 箇所」事実誤認）に commit `fce6b9d` で応答

### Step 4: 副次目的の運用テスト結果と PR 内追加対処（gemini-review）

PR #39 内で gemini-review GitHub Action の独立レビュー機能を 4 run（commit `1275e70` / `fce6b9d` / `cb72f0e` / `6969a21`）に渡って実行。**全 4 run で `review` job は `success` 終了したが、レビュー投稿は 0 件**（webhook 監視 + `pull_request_read get_reviews` API 確認）。Copilot review は同期間に正常稼働しており、PR 機能側の問題ではない。

PR 内で以下の Shift Left 対処を実施：

- commit `cb72f0e`: `gemini-review.yml` に診断機構追加（runner / docker / GitHub MCP server reachability の事前確認、`GEMINI_CLI_VERBOSE` / `DEBUG` env、`continue-on-error: true` + `id: gemini_review`、prompt 末尾「必須実行プロトコル」、post-step outcome 出力）
- commit `6969a21`: MCP server に渡す `GITHUB_PERSONAL_ACCESS_TOKEN` を auto `secrets.GITHUB_TOKEN`（`ghs_*` GitHub Apps token）から `secrets.GH_REVIEW_PAT`（Fine-grained PAT, Pull requests: read+write / Contents: read）に切替（原因 A: GitHub Apps token の write 制限仮説への対処）

PAT 切替（commit `6969a21`）の効果検証は merge 前に webhook で確認できず、本 v5.5.1 release 時点で **未検証**。検証は次 PR（本 `(released)` 化 patch 自身）で実施し、結果を patch 内 `## v5.5.x` 節または `delivery/SELF-VERIFICATION-v5.5.x.md` に追記する。診断機構（`continue-on-error` / verbose env / 診断 step 群）は **PAT で 1 度の正常投稿を確認した後** に縮退または削除する。

## v5.5.0 (released 2026-05-02)

> **記録規約**: 本セクションは PR #34 が draft 中に書かれ、`(in progress, target 2026-05-02)` で記録されていた（Copilot review #34 line 8 の指摘で recorded-during-draft の妥当性が再確認された）。本 patch（PR #34 マージ後）で `(released 2026-05-02)` へ更新。「PR draft 中は `(in progress)` / マージ時に `(released YYYY-MM-DD)` 化」フローは旧監査 `delivery/D4-AUDIT-2026-04-30.md` M-1 で**問題提起**され（同節「ルールが未定義」と明示）、v5.4.0 リリース時に過去エントリ（v5.0.0〜v5.3.0）一括正規化として**実装**されて以降の運用慣行として確立。本 v5.5.0 patch はその慣行の最初の正規適用例にあたる。マージ前後の history が PR 状態と整合する。

minor 昇格。**(I) adrv01-Ph1 = AI 自己申告閾値の Council 連動明文化**（既存 `confidence < 0.6` 機構流用、コスト 0）+ **(II) Phase γ コア 3 件 = L1 自己検証/独立検証への意図合致軸追加**（4 軸化、起点問題=リファクタ取りこぼしの構造解決）。
PR #33 ブレスト結晶 `delivery/AUTONOMOUS-DRIVE-BRAINSTORM-2026-05-02.md`（adrv01/02/03 全合意成立）を起源とする。後方互換維持（v5.0.0〜v5.4.0 と同パターン）。利用者プロジェクトには配布されない。

`crosscut-verifier-philosophy` 本実装は本リリース対象外（v5.5.x patch / v5.6.0 へ再々々後送、v5.0.0 から累計 5 リリース後送中）。
Phase γ 先行宣言 4（ストラングラー射程外宣言）+ 5（失敗アンチパターン早期検出）は本リリース対象外（v5.5.x patch / v5.6.0 候補）。
adrv01-Ph2（独立観測機構新設、新規 crosscut-* skill）は v5.6.0 候補。

### Step 0: L0 spec-architect 起動 + 振り返り儀式 + Council 諮問

- LC=1（v5.4.0 リリースから 1 日経過、CHANGELOG 更新 < 30 日）/ M2 標準モード判定
- 振り返り儀式レベル 2（機能追加示唆検出）/ F1 過去文脈サマリ提示 / F2 認識ズレ検出 / F3 履歴更新予告
- Council `vrfy01`（v5.5.0 着手前 DH 自体実装妥当性検証スコープ判定）: V-1 狭義 / V-2 中庸 / V-3 広義 の 3 候補拮抗 → recommended V-1、`agreed_with_modification`（β止揚採用：V-1 + 検証を v5.5.0 SPEC 化に内包）
- V-1 検証完了: adrv01-Ph1 / Phase γ 双方の依存機構（Council confidence 機構 / L1 §自己検証構造）が構造的に完備、拡張ポイント特定済み

### Step 1: Phase A — adrv01-Ph1 改修

- `crosscut-council/SKILL.md §自己申告プロトコル` 新節（confidence < 0.6 を Council 起動の正式トリガーとして明文化、内部完結禁止、自己申告 = 一次入力 + Council = 二次検証の二相構造）
- `crosscut-council/references/pre-check.md` §scope/PR 境界 vs 新規思想 の判別シナリオ（Copilot review #34 feedback、category 誤選択の Shift Left 防止、判別チェックリスト追加）
- `crosscut-council/references/consensus-protocol.md` §エッジケース「escalated 経路での合意成立」明文化（vrfy01 事例由来）+ §自己申告 → Council 起動の hook 経路（v5.6.0 Ph2 で本実装の先行宣言）

### Step 2: Phase B — Phase γ コア 3 件本実装

- `layer0-archeo-architect/references/handoff-to-evaluator.md`: 先行宣言版 → コア 3 件本実装版へ拡充（ロードマップ表 / I/O 契約 / 改修対象ファイル状態を ✅ 実施済みに更新）
- `layer1-autonomous-dev/references/inferential-sensor-v2.md` §第4層: 意図合致軸の起動条件（`refactor-intent-map.md` 存在時のみ）+ refactor_directive 別判定ルール（preserve 承認テスト / restructure 自動照合ループ / discard_and_redesign）追加
- `layer1-autonomous-dev/SKILL.md §6 自己検証`: 承認テスト生成プロトコル + 自動照合ループプロトコル追加
- `layer1-independent-reviewer/SKILL.md`: 評価軸 3→4 軸化、§5.4 意図合致チェックステップ追加、判定ルール 4 軸対応
- `layer1-autonomous-dev/references/delivery-format.md`: 推論的センサー判定に意図合致追加 + 意図合致検証セクション（refactor-intent-map.md 存在時のみ）

### Step 3: Phase C — 履歴層更新 + ARCH-DECISIONS

- `history/INTENT.md` v5.5.0 セクション追加（adrv01-Ph1 / Phase γ コア 3 件 / β止揚運用記録 / v5.6.0 / v6.0.0 候補温存）
- `history/CHANGELOG.md` 本セクション
- `history/REGIME-LOG.md` v5.5.0 minor 昇格判定記録（M2 / LC=1 / dev_mode=github_assisted / claude-opus-4-7）
- `history/ARCH-DECISIONS.md` AD-018（adrv01-Ph1）+ AD-019（Phase γ コア 3 件）追加
- `history/COUNCIL-LOG.md` `vrfy01` エントリは Step 0 で append-only 追記済み（PR 内同梱）

### Step 4: 自己検証 + 献上

- `python harness-verifier/verify.py --strict` 全 PASS（D4 整合性維持確認、5 検査全項目）
- `harness-verifier/reports/2026-05.md` 上書き（最新実行記録）
- `delivery/SELF-VERIFICATION-v5.5.0.md` 作成（L0 §7.4 の 5 項目 + harness-verifier 5 検査 + β止揚運用の SPEC 化過程内包記録）
- 計算的センサー: SKILL.md / references の構文整合・broken reference なし
- ルートに draft PR #34 を作成、Copilot review #34 で発見された category 誤選択の連鎖は本リリースで Shift Left 修正

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
- ルートに draft PR #30 を作成

### Step 6: 業界知見統合（Council 諮問経由の追加実装）

ひでさんから AI を活用したレガシーコード・リファクタリング業界知見（フェザーズ / ファウラー / ヘルマンズ / ストラングラー・フィグ / Branch by Abstraction / 承認テスト / 自動照合ループ / Git ホットスポット / DDD Bounded Context / AAR / 失敗アンチパターン）が共有され、選択肢 A/B/C の拮抗のため Council 諮問。

`crosscut-council` を直接起動（`council-2026-05-01T10:30:00Z-archeo01`、category: conception、哲学者重み 5 で支配的）。3 Persona で simple_conflict（経営者 B / 開発者 A / 哲学者 第 4 の道）。Judgment Agent confidence 0.7 で「**第 4 の道: A 縮小版 + Phase γ 伏線追加**」が agreed_recommended 確定。ひでさん即時合意。

追加実装：

- **`intent-hypothesis-protocol.md` に Code Smells カノン対応表追加**（12 種 Smells のマッピング、適用順序、注意事項）
- **`intent-hypothesis-protocol.md` の S 軸推定に Git ホットスポット分析統合**（`hotspot_score = log(修正頻度) × 複雑性指標`、4 戦略象限、90 日の法則対応、計測制約）
- **`handoff-to-evaluator.md` の Phase γ 詳細仕様先行宣言**（5 件: 承認テスト生成プロトコル / 自動照合ループ / L1 意図合致軸統合 / ストラングラー・フィグ射程外宣言 / 失敗アンチパターン早期検出）
- **`crosscut-council/history/COUNCIL-LOG.md`** に invocation_id `council-2026-05-01T10:30:00Z-archeo01` のエントリ追加（implementer_consent: agreed_recommended）
- **`history/INTENT.md`** v5.4.0 セクションに「Council 諮問による業界知見統合」「経営者の少数意見（観測駆動原則との緊張）」追記

経営者の少数意見（選択肢 B、PR スコープ厳守）は minority_opinion として保持。観測駆動原則との緊張関係は Phase β/γ 設計時に再検討予定。

### Step 7: 業界知見統合後の再検証

- harness-verifier 5 検査全 PASS 維持（追加修正後も D4 整合性維持）
- 拡張ファイル 3 件（intent-hypothesis-protocol.md / handoff-to-evaluator.md / COUNCIL-LOG.md）の broken reference なし
- PR #30 に追加コミットを push、draft 状態のまま実装完了

### Step 8: L1-refactor 新設提案の Council 諮問（archeo02、最小記録）

ひでさんから L1-refactor スキル新設の提案。CC が D4 原則で機械的検査し 5 原則違反（wf-baseline-rationale.md / philosophy.md §1 / §3 / Phase γ 重複 / 観測駆動閾値未達）を指摘、不採用結論を提示。ひでさんが Council 諮問を選択。

`crosscut-council` 直接起動（`council-2026-05-01T11:00:00Z-archeo02`、conception カテゴリ）。3 Persona unanimous で **B（L1-refactor 不採用、Phase γ 予定通り）** を支持、weighted_score 8.85、judgment_confidence 0.85 で agreed_recommended 確定。CC 機械的検査と Council 判断が完全整合し堅牢な決定。

哲学者の拡張提案『v6.0.0 で Level B プロジェクト固有 SK によるリファクタ支援を明文化』は最小記録方針で `history/INTENT.md` v5.4.0 セクション末尾に 1 段落追加（v5.x 帯 minor 改修を圧迫しないため）。`COUNCIL-LOG.md` に archeo02 エントリ追加。

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
