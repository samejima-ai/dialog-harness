# ARCH-DECISIONS

DH 本体の設計判断の記録（ADR 軽量版）。

## v5.x 温存項目

### AD-032: Hard Gate（PreToolUse 守備）⇄ 整合性検証（DAG verify 攻撃）の対称化検討 [候補]

| 項目 | 内容 |
|---|---|
| 状況 | Council `council-2026-05-16T06:00:00Z-coddag` で CoDD（Coherence-Driven Development）の DAG 概念を DH に吸収する判定（案 B + 第 4 の道 minority 併合）が unanimous で出た過程で、DH の現在の検証体系が**非対称設計**であることが指摘された。PreToolUse Hard Gate（守備、philosophy 第 6 条 人間最終承認 + 第 2 条 Shift Left 基盤）は「やってはいけないことを止める」役割を担うが、CoDD の DAG verify に相当する「整合性が取れているかを積極的に検証する」**攻撃**設計が DH には未配置。Council 内では本件を「本 council スコープ外、独立 AD 案件」として扱った。なお Council recommended 内で「AD-022 候補」と記述したのは番号衝突（AD-022 は v5.5.3 で既存）であり、実装時に最新 AD 番号確認の結果 AD-032（最新 AD-031 の次）に訂正 |
| 判断 | **候補ステータス**: 本件は philosophy 第 2 条 Shift Left 基盤（30%）+ 5 層エラー検出スタック（70%）の対称化検討案件として温存。次の振り返り儀式 F1-F3 または別 Council 諮問で取り扱う。具体実装（DAG verify 機構の autonomous-dev / independent-reviewer / harness-verifier への配置設計、5 層エラー検出スタックへの組込み、対称化の境界線確定）は本 AD の本実装 PR で扱う。本 AD 候補登録時点では実装変更ゼロ |
| 根拠 | (a) Council `coddag` の判定過程で開発者 persona が指摘（concerns 内「Hard Gate（守備）と DAG verify（攻撃）の対称化は ARCH-DECISIONS 案件」）、(b) philosophy.md 第 1 条 派生節「依存トポロジーの追跡可能性」（本 PR で同時追加）との論理的接続点を持つ、(c) Council 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当しないため候補温存で十分、(d) 業界先行事例 CoDD の DAG verify が参照事例として観測リスト（`.claude/skills/layer0-spec-architect/references/observed-peers.md`、本 PR で同時新設）に登録済 |
| 影響 | **本 AD 候補登録時点では実装変更ゼロ**。philosophy.md / 既存 6+1 条 / 4 役割組織論への影響なし。harness-verifier 全 PASS 維持。**温存項目**: 本 AD の本実装（DAG verify 機構設計、5 層スタックへの組込み、対称化の境界線確定）、philosophy 第 2 条 Shift Left 基盤の章立て再構成（もし対称化が major 案件と判定された場合）、献上フロー（philosophy 第 5 条）への DAG verify 統合（Council `coddag` 問い 2 と同根、別案件） |
| 連動 | Council `council-2026-05-16T06:00:00Z-coddag`（本 AD の起点）/ Council `council-2026-05-16T07:15:00Z-p1embd`（philosophy 第 1 条 派生節埋込み形式の sub-Council）/ philosophy.md 第 1 条 §依存トポロジーの追跡可能性（本 PR で追加、本 AD と論理的接続点を持つ）/ Council `clrdbl`（人間可読並存規約、本 AD 候補は本実装時に Council 諮問予定） |

## v5.7.2

### AD-030: `claude-code-action@v0` の OIDC token 取得に必要な `id-token: write` permission 追加

| 項目 | 内容 |
|---|---|
| 状況 | v5.7.1 で `gemini-cli` → `Claude Code CLI` に実装エージェントを切替えたが、`anthropics/claude-code-action@v0` が OIDC で token 取得を試みる仕様に対し、`issue-pickup.yml` の `permissions:` ブロックには `contents: write` / `pull-requests: write` / `issues: write` のみで `id-token: write` が未設定だった。Issue #46 (v5.8.0 候補 `crosscut-issue-quality-gate`) の autonomous-drive 起動が `claude-code-action` の初の本番テストとなり、`Failed to setup GitHub token: Error: Could not fetch an OIDC token. Did you remember to add 'id-token: write' to your workflow permissions?` で workflow が exit 1 終了し顕在化 |
| 判断 | `issue-pickup.yml` および `templates/github-workflows/issue-pickup.yml.template` の `permissions:` ブロックに `id-token: write` 1 行を追加する v5.7.2 patch を発行。Council 諮問は不要（自明な single-line bug fix、複数案拮抗なし、不可逆操作なし、SPEC 矛盾なし）。v5.7.1 (in progress) → (released 2026-05-03) 化を本 patch で housekeeping として同梱（**8 例目正規適用**） |
| 根拠 | (a) `anthropics/claude-code-action@v0` の公式仕様で `id-token: write` が必須、(b) v5.7.1 の merge 時点で実装本体の本番テストが未実施だったため bug が潜在化、(c) Issue #46 が初のトリガーで観測駆動的に顕在化、(d) 修正は 1 行追加で意味的に自明、複数代替案なし、(e) 既存挙動に影響しない（追加権限のみ、既存 workflow が要求しない権限を増やすだけ）、(f) Issue #46 の autonomous-drive 完遂のためには本 fix の merge が前提条件 |
| 影響 | `.github/workflows/issue-pickup.yml` 1 行追加、`templates/github-workflows/issue-pickup.yml.template` 1 行追加。philosophy.md / 既存 6+1 条 / 4 役割組織論への影響ゼロ。harness-verifier 全 PASS 維持。利用者プロジェクトへの強制配布なし（後方互換完全維持）。**温存項目**: 本番前テスト粒度の規格化（Issue Quality Gate 軸 viii 合格基準として後発検討）、claude-code-action SHA pin（v5.7.x、観測駆動）、gemini-cli 自動フォールバック（同上） |
| 連動 | Issue #46 の autonomous-drive 完遂 + v5.7.1 機構の動作確認のダブルテストを兼ねる。merge 後、Issue #46 の `in-progress` ラベル除去 + `ready-for-ai` 再付与で再 trigger 実施 |

## v5.8.0

### AD-031: Issue 段階品質ガード機構の独立 skill 化（12 軸 + 並列安全性）

| 項目 | 内容 |
|---|---|
| 状況 | autonomous-drive パイプラインで Issue が AI 自律駆動の初期 context となる構造上、Issue の品質 = プロジェクトの成功率。人間対話起点・Council 献上起点・D4〜D2 献上起点いずれの Issue も、品質バラつきがそのまま実装品質に伝播する。現状、SPEC/ADR 差分起点の crosscut-issue-dispatcher はあるが、Issue 段階での「12 軸チェック」を独立に通過させる横断機構は未配置。並列実行時の論理・意味・依存コンフリクト（git では検出不能な 3 種）を事前検知する必要性も確認された |
| 判断 | **12 軸品質チェック** + **並列安全性軸** を持つ独立 skill `crosscut-issue-quality-gate` を新設。**(a) dispatcher 内部通過** + **(b) 明示呼び出し** + **(d) GitHub Actions 最終ガード** の 3 発動契機。**軸 vi（観測性統一）** で Council 入力データレイヤー整合保証、**軸 ix（並列安全性）** で 4 段階フィルター（scope/mutex/depends-on/AI推論）による論理・意味・依存コンフリクト事前検知。**フラクタル原則徹底** で DH 自身も例外なく本 Gate 通過。不合格 Issue は理由ラベル（gate-failed:axis-X）付与し close せず人間差し戻し |
| 根拠 | (a) Issue 品質 = autonomous-drive 成功率の構造的因果関係、(b) 起点に依存しない横断機構としての独立性確保（crosscut-* 系の責務分離原則）、(c) Council 合議成立の前提条件として観測性データ整合が必須（philosophy.md 第 6 条「人間 ≒ Council」の実装前提）、(d) Issue 並列実行時の git 検出不能コンフリクト（論理・意味・依存）の事前回避、(e) philosophy.md 第 1 条フラクタル原則 P1 の「規律の自己相似性」実装、(f) Council 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当せず Council 諮問は不要 |
| 影響 | **新規追加**: skill 本体 + references 8 + assets 1 + dh-upgrades 1 + workflow template 1 の計 12 ファイル。**既存変更**: ARCH-DECISIONS（本項目）/ crosscut-* 4 skill / layer0-spec-architect / philosophy.md / issue-pickup.yml.template への最小参照追記。**完全後方互換**: 新 skill 不在でも DH ベースは通常動作、既存 Issue 形式変更なし、既存プロジェクトへの強制配布なし。ラベル規約（scope/mutex/refactor/freeze-period）は assets/ で配布、各プロジェクト任意採用。harness-verifier 全検査 PASS 維持 |

## v5.7.1

### AD-029: 実装エージェントを Claude Code CLI へ切替（AD-026 訂正）

| 項目 | 内容 |
|---|---|
| 状況 | v5.7.0 で AD-026「gemini-cli を実装エージェント採用（Anthropic API 回避）」が確定、当時のユーザー要望「自前開発で低コスト、API 課金避けたい」に応じた判断だった。本 patch で **新事実発見**: Anthropic Pro/Max サブスクリプション + `CLAUDE_CODE_OAUTH_TOKEN` 経由で `anthropics/claude-code-action` を **追加 API 課金なし** で稼働可能（OAuth token は Anthropic Console から発行）。前提変化により最良案が gemini-cli → Claude Code CLI に移行 |
| 判断 | **(a) Claude Code CLI をメイン実装エージェントに採用**: `anthropics/claude-code-action@v0` + `CLAUDE_CODE_OAUTH_TOKEN` 認証。**(b) gemini-cli 用途を分離維持**: AI triage（軽量、無料 tier）+ 実装フォールバック（人間 P4 判断発動）+ PR レビュー（gemini-review.yml、変更なし）。**(c) AD-026 historical 維持**: 削除せず、本 AD-029 で訂正記録。**(d) フォールバック自動化なし**: Claude Code 失敗時は label `pickup-failed` + notice → 人間 P4 判断（philosophy 第 4 条 + 第 7 条 P4 整合）。**(e) 認証方式の限定**: `CLAUDE_CODE_OAUTH_TOKEN` のみ使用、`ANTHROPIC_API_KEY` 経路（従量課金）は使用しない |
| 根拠 | (a) ユーザー方針「実装は Claude Code で L1 実行を基本とする」+ 「サブスクで稼働、API 課金避けたい」と整合、(b) Claude Code は実装品質で gemini-2.5-pro を上回る（DH での実証済み運用、autonomous-drive 出口側で自身が動作）、(c) 異質モデル併走（philosophy.md §3 情報純度）は triage / 実装フォールバック / PR レビューの 3 場面で gemini を維持することで保全、(d) 自動フォールバックは観測駆動で v5.7.x 以降に判断（fail パターン蓄積後）、(e) 後方互換: v5.7.0 で deploy 済プロジェクトは旧 workflow のまま動作可、(f) Council 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当せず Council 諮問は不要 |
| 影響 | `crosscut-issue-implementer/SKILL.md` 改訂（実装エージェント記述更新）、`references/setup-checklist.md` `CLAUDE_CODE_OAUTH_TOKEN` 取得手順追加、`.github/workflows/issue-pickup.yml` + template に `claude-code-action@v0` 統合。philosophy.md / 既存 6+1 条 / 4 役割組織論への影響ゼロ。harness-verifier 全 PASS 維持（新用語不要、既存用語の組み合わせのみ）。**訂正対象**: AD-026 (gemini-cli 採用) は historical 記録維持、本 AD-029 で「前提変化により訂正」を明示。**温存項目**: 実装本体の MVP → 完全実装（v5.7.x）、gemini 自動フォールバック導入（観測駆動、v5.7.x or v5.8.0）、claude-code-action SHA pin（supply-chain hardening、v5.7.x） |

## v5.7.0

### AD-026: gemini-cli を実装エージェントとして採用（Anthropic API 回避）

| 項目 | 内容 |
|---|---|
| 状況 | v5.6.0 で温存された「パス B（crosscut-issue-implementer workflow 実装）」を本格仕様化するにあたり、実装エージェントの選定が必要。既存 skill (v5.0.0) は claude-code-action（Anthropic API 課金あり）前提だったが未稼働。ユーザー要望「自前開発で低コスト、API 課金避けたい」 |
| 判断 | gemini-cli を実装エージェントとして転用採用。既存 GEMINI_API_KEY（v5.5.1 で導入、PR レビュー用途で稼働中）を流用。追加コスト 0。Anthropic API は使用しない |
| 根拠 | (a) ユーザー要望「自前開発・低コスト・できるだけ API 避ける」と整合、(b) gemini-2.5-pro が PR レビュー用途で実用域実証済（PR #43）、(c) 段階的進行原則: 失敗したら Copilot Workspace 切替や一時的 Anthropic API 使用へ昇格判断（観測駆動）、(d) Council 起動条件のいずれにも該当せず Council 諮問は不要 |
| 影響 | `crosscut-issue-implementer/SKILL.md` から claude-code-action 言及削除、gemini-cli base 設計へ全面改訂。`.github/workflows/issue-pickup.yml` は gemini-cli を呼び出す形式。**未踏領域**: PR レビューから「実装」への拡張は未検証、品質懸念あり、実装段階で品質悪い場合は autonomous-dev が独自 Council 起動可（adrv01-Ph1 自己申告経由）。フォールバック候補: ローカル Claude / Copilot Workspace / 一時的 Anthropic API |

### AD-027: REGIME.md `current_focus` 軸新設（β 半自動 + γ ブランチ命名フォールバック）

| 項目 | 内容 |
|---|---|
| 状況 | ユーザー観点「master のバグ修正中なら新機能 Issue を pickup しない」を機械可読化する必要。Issue pickup 時の「コンテキスト依存判定」が品質を決める |
| 判断 | REGIME.md に新フィールド `## current_focus` を追加（type / target / since / priority）。**β 半自動更新**（spec-architect 対話で「今このプロジェクトで何に集中？」を確認 → AI が更新）+ **γ ブランチ命名フォールバック**（fix/* feat/* refactor/* から推論、REGIME.md 値が優先） |
| 根拠 | (a) philosophy.md 第 4 条「モード判定は L0」と整合（自動推論ではなく対話で更新）、(b) β 半自動は人間 P1/P2 の発話起点で更新、AI が REGIME.md を編集する形 = 人間 = 頭と口、AI = 手 の原則と整合、(c) γ フォールバックは REGIME.md 未設定時の救済、(d) Issue 選別 3 段階フィルターの 3 段階目「current_focus 整合」で参照される、(e) Council 起動条件未満 |
| 影響 | `meta-spec-template.md` REGIME.md テンプレに `## current_focus` セクション追加。`regime-assessment.md` に判定プロトコル追加。`dialog-questions.md` に質問追加。`dev-env-spec.md` Level C に Issue pickup 連動表追加。既存 LC ≥ 1 プロジェクトへの遡及適用なし、新規 + 任意更新。utilizer プロジェクトへ配布されない（spec-architect 対話で記録される機械可読軸） |

### AD-028: Issue 選別 3 段階フィルター（label / author + 本文 / AI triage）

| 項目 | 内容 |
|---|---|
| 状況 | ユーザー明示「全 Issue を picking up は NG」「Issue 選択は開発品質を決める」。乱雑な Issue から品質ある Issue を選別する機構が必要 |
| 判断 | 3 段階フィルター採用: **一次** label `ready-for-ai` opt-in（人間 P2 の明示 GO サイン）、**二次** author allowlist + 本文必須項目（再現手順 / 期待動作 / 受入条件）、**三次** AI triage（gemini-cli が Issue 内容を読んで pickup 可否判定、SPEC/DONT/current_focus と照合）。各段階で skip 時の理由 label を自動付与（`needs-clarification` / `out-of-scope` / `focus-mismatch`）+ Issue は close せず人間差し戻し |
| 根拠 | (a) ユーザー観点「label 回避 / 取得」両対応 = opt-in 設計、(b) philosophy 第 3 条情報純度（各段階で独立した判定）+ 第 7 条 P2 ブレスト責務（人間が GO サイン、AI が選別実行）と整合、(c) 完全自動を目指すユーザー要望と整合（一次 GO サイン後は AI が完遂）、(d) 失敗時の救済経路（label 付与で人間に差し戻し、Issue は残る） |
| 影響 | `crosscut-issue-implementer/SKILL.md` 改訂 + `references/issue-filter-spec.md` / `triage-protocol.md` / `circuit-breaker-spec.md` 新設。`.github/workflows/issue-pickup.yml` で実装。Circuit Breaker（日次 5 / 月次 50）で経済的暴走防止（philosophy 第 7 条 P4）。**温存項目**: 新 sub-skill `crosscut-issue-drafter`（ブレスト → Issue 化支援）/ destructive change detector / ALLOWED_AUTHORS 動的化 |

## v5.6.0

以下 3 件は L0 spec-architect セッションで策定された HANDOFF（`delivery/HANDOFF-v5.6.0-autonomous-drive.md`）に基づく設計判断 + L1 autonomous-dev による実装。Council 諮問 `council-2026-05-03T08:30:00Z-adrv02` で β 止揚採用（`agreed_with_modification`）。

### AD-023: autonomous-drive 標準化（メタスキル展開機構の追加）

| 項目 | 内容 |
|---|---|
| 状況 | dialog-harness 本体で v5.5.3 まで autonomous-drive 機構（gemini-review.yml + auto-merge.yml）が稼働、PR #42 で自動 merge の自己テスト成功。ユーザー要請「自律駆動を L0 に記録、他の開発でも容易に展開できるようにしたい、メタスキル開発」を起源として、本機構を template 化し利用者プロジェクトに展開可能にする必要が生じた。v5.5.3 AD-022 で温存された「パス B（dev_mode autonomous 化）」の本格仕様化案件 |
| 判断 | **(a) パス B 本格採用**: dev_mode `autonomous` を本格定義 + `autonomous_scope` 軸（full / merge_gated / custom）追加、デフォルト = full。**(b) 配置層**: D2（`templates/github-workflows/`）+ D3（`.claude/skills/crosscut-autonomous-drive/`）+ D4（`spec-architect/references/autonomous-drive-deployment.md`）の 3 層構成。**(c) Council β 止揚採用**: deployment skill 1 つのみ新設、guardian（destructive change detector / circuit breaker）は v5.6.x patch で観測駆動追加。**(d) 観測駆動原則の緩和**: v5.5.3 AD-022 の「数 PR 試運用後判断」原則を 1 例（PR #42）のみで標準化要請へ移行（メタスキル開発は複数プロジェクト展開可能性確保が先決） |
| 根拠 | (a) v5.0.0 で列挙のみだった `autonomous` を本格化することで、ユーザー要請「issue 取得→精査→実行→PR→検証→自動 merge→次 issue」のフルループが標準化される。(b) D2 template だけでは利用者プロジェクトへの展開ロジックが分散、D4 skill だけでは配布物が不在 → 3 層構成で配布物 + 展開ロジック + 対話ガイドを揃える。(c) Council 諮問結果（`adrv02`）の β 止揚採用で skill 化のメリット（再利用性・拡張性・第 7 条整合）と YAGNI 精神（最小実装）を両立、guardian は観測駆動で後追加判断。(d) F2（認識ズレ検出）でユーザーが「即着手 OK」と判断、観測駆動原則の緩和は明示的に F2 で記録、観測継続は v5.6.x patch で並行 |
| 影響 | `templates/github-workflows/` 新設 + `crosscut-autonomous-drive` skill 新設 + `spec-architect/SKILL.md` + 4 references + 1 asset の改修。利用者プロジェクト本体には強制配布されない（DH 自身の運用標準化、autonomous-drive 機構は dev_mode `autonomous` 選択時のみ opt-in）。harness-verifier 5 検査の対象に新 skill `crosscut-autonomous-drive` が追加（frontmatter 検査 +1）。**温存項目**: destructive change detector / circuit breaker（v5.6.x patch 観測駆動）/ ALLOWED_AUTHORS 動的化（複数 contributor 体制で必要時）/ 第 7 条と連動した crosscut-verifier-philosophy 本実装（v5.0.0 から累計後送中、第 7 条確定で 7 本柱整合検証として再構成可能） |

### AD-024: philosophy.md 第 7 条「AI 組織論（4 役割 + サポート構造）」新設

| 項目 | 内容 |
|---|---|
| 状況 | ユーザー宣言「DH の AI 組織は L0 設計 / L1 実装 / L2 統括 / Council 判断 の 4 役割属性 + サポート だけで、あらゆる開発に対応できる」を philosophy.md の正式条として制度化する必要が生じた。既存 6 条には 4 役割の組織論が明示されていなかった（第 1 条フラクタル原則で L0/L1/L2 は言及されるが、Council を含む 4 役割としての明示はなく、サポート skill の位置づけも暗黙的だった） |
| 判断 | **(a) 第 7 条新設、既存 6 条改訂なし**: minor 範疇で philosophy.md に第 7 条を追加（v4.2 第 6 条追加と同形式）。既存 6 条の責務再定義・削除は major 案件のため避ける。**(b) 4 役割属性 + サポート構造の明文化**: L0/L1/L2/Council を 4 役割として明示、crosscut-* 非 council 系 + sub-agent をサポートとして位置づけ。**(c) Person 責務 P1〜P4 の追加**: 人間 4 責務（発案 / ブレスト / 事後確認・評価 / 暴走時介入）を philosophy.md 内に明記。HANDOFF の仮ラベル「H1-H4」は第 6 条 H カテゴリと番号衝突するため `P1-P4`（Person responsibilities）にリネーム（実装者裁量、Council 起動の閾値未満）。**(d) H と P は直交 2 軸**: H = 判断種別、P = 責務種別、両者は補完関係（番号符合は偶然） |
| 根拠 | (a) 既存 6 条改訂は major 案件、minor 範囲では追加のみ。(b) 4 役割の明文化は組織論の汎化性主張（「あらゆる開発に対応」）を制度化するために必須、サポート skill の位置づけ明文化は v5.0.0 で導入された crosscut-* 群の責務体系を整理する。(c) HANDOFF の H1-H4 を P1-P4 にリネームすることで第 6 条との混乱を回避、用語純度を確保（philosophy.md 第 3 条情報純度の系）。(d) 直交 2 軸として整理することで、両カテゴリを統合せずに済む（統合すると major 範囲になり既存 6 条改訂を伴う）。Council 起動条件のいずれにも該当せず Council 諮問は不要（リネーム判断は実装者 confidence 0.7、明確な解あり） |
| 影響 | `philosophy.md` 末尾に第 7 条追加（既存 6 条不変）。各 skill の参照経路は不変（philosophy.md 末尾参照節に第 7 条を関連付け追記）。harness-verifier 5 検査の用語辞書整合に新用語（`autonomous_scope` / `P1〜P4` / 「サポート skill」/ 「4 役割属性」/ 「メタスキル」）が追加される可能性あり、verify.py 実行時に確認。**温存項目**: 「献上 3 軸構造」（philosophy.md §5 タイプ二項分類の限界、v6.0.0 候補）と第 7 条の関係再整理（major 候補）/ 第 7 条と既存 6 条の統合的な体系整理（major 候補）|

### AD-025: `autonomous_scope` 軸の正式定義（full / merge_gated / custom）

| 項目 | 内容 |
|---|---|
| 状況 | dev_mode `autonomous`（v5.0.0 で列挙のみ）に対して、autonomous-drive 機構の運用粒度を細分化する軸が必要。ユーザー要請「デフォルトはフルオートで OK、人間 = P1〜P4 のみ」を REGIME.md の機械可読軸として制度化する |
| 判断 | `autonomous_scope` 軸新設（full / merge_gated / custom の 3 値）、REGIME.md 必須フィールド化。**デフォルト = full**（人間 = P1〜P4 のみ、AI = Issue 精査〜次 Issue 着手まで完全自走）。`merge_gated` は自動 merge 無効（PR review/approve は人間が実施、P3 を merge 前に倒す）、`custom` は dev-env-spec.md の Level C 詳細表で個別指定 |
| 根拠 | (a) dev_mode 単独では autonomous の運用粒度が表現不能（手動 merge を残すかどうかの 2 値以上の選択肢が必要）。(b) full をデフォルトとすることで、ユーザー要請「フルオートでいい」を即時反映。(c) `merge_gated` は段階的引き上げパス（local_only → github_assisted → autonomous/merge_gated → autonomous/full）の中間段階として機能。(d) `custom` は将来の拡張点（destructive detector / circuit breaker 等の細粒度設定）を保持 |
| 影響 | `meta-spec-template.md` の REGIME.md テンプレに `## autonomous_scope` セクション追加、`spec-architect/references/regime-assessment.md` に判定ロジック追加、`dialog-questions.md` に質問追加、`dev-env-spec.md` の Level C に `autonomous_scope` 別の有効化機能表追加。既存 REGIME.md（LC ≥ 1 プロジェクト）への遡及適用なし、v5.6.0 以降に新規プロジェクト立ち上げ時のみ追加。利用者プロジェクトには配布されない（spec-architect の対話で記録される機械可読軸であり、配布物ではない） |

## v5.5.3

### AD-022: autonomous-drive 機構の出口側として label opt-in 自動 merge を新設

| 項目 | 内容 |
|---|---|
| 状況 | DH の crosscut-* 機構（v5.0.0 で導入: dispatcher / issue-implementer / feedback-loop）は autonomous-drive パイプラインの入口〜中段までを自動化していたが、最終段階の merge は人間手押しで残っていた。ユーザー（非エンジニア）からの要請「自律駆動できるようにしたい、issue label = GO サイン → AI 実装 → 自動 merge」を起点に、出口側自動化の必要性が確定 |
| 判断 | **(a) パス A 採用**: 「auto-merge workflow だけ追加」を選択。「パス B: dev_mode を `autonomous` へ引き上げ」は v5.6.0 候補として温存（観測駆動原則、数 PR 試運用後に判断）。**(b) GitHub native auto-merge ではなく workflow で直接 merge**: branch protection 設定変更不要、ロジック一元管理、運用観測（notice ログ）一元化。**(c) 4 層検証 AND** で auto-merge 条件を構成: 構造層（harness-verify）+ 意味層（gemini-review）+ 判断層（reviewDecision != CHANGES_REQUESTED）+ 承認層（label `auto-merge` + author allowlist）。**(d) `ALLOWED_AUTHORS` を workflow env に明示 hardcode**: 拡張は spec 改修扱い、L0 spec-architect 経由で REGIME.md と整合確認必須。**(e) verifier 全て「走った場合のみ必須」+ 最低 1 verifier guard**: harness-verify / gemini-review いずれも paths filter があり全 PR では走らないため、両者を「走った場合のみ SUCCESS 必須」とし永久 pending を回避。zero-check auto-merge は別途 guard 条件で防ぐ（Copilot review #42 で初版「harness-verify は paths filter なしで全 PR 走る」事実誤認を訂正）。**(f) Robustness pre-check 追加**: GH_REVIEW_PAT availability check + check_suite event 経由で SHA に複数 open PR 紐付き時の skip + warning（Copilot review #42 line 89 対応） |
| 根拠 | (a) パス A はリスク小・段階的、ユーザー体感の自律度が大幅 up（手動 merge ボタン押しが消える）、AI 自走による意図逸脱リスクを 1 層ずつ観測しながら拡大可能（観測駆動原則と整合）。(b) GitHub native auto-merge は branch protection 必須で運用ルール変更を伴う、本機構は branch protection なしでも opt-in 動作する低侵襲設計。(c) 4 層 AND は philosophy.md §3「情報純度」（Generator/Evaluator 分離）と §5「献上哲学」（自律内部完結禁止、独立観測機構の通過）を実装。(d) hardcode は allowlist の不可視拡張（誰かが secret を追加して invisible に信頼境界が広がる）を防ぐ設計判断。(e) 必須化は paths filter 起因の deadlock を防ぐ、最低 1 verifier guard で zero-check auto-merge も防ぐ。(f) PAT pre-check で fork PR / secret 欠落での red CI を防ぐ、multi-PR detect で merge target の非決定性を排除。Council 起動条件のいずれにも該当せず Council 諮問は不要 |
| 影響 | `.github/workflows/auto-merge.yml` 新設（160 line）。SK 本文・harness-verifier・利用者プロジェクトへの影響ゼロ。**opt-in 完全後方互換**（label なき PR は従来通り手動 merge）。本 patch 自身は label を付けず人間 merge で投入し、信頼運用は次 PR から開始する 4 例目運用。dev_mode は `github_assisted` のまま据え置き、autonomous 化は v5.6.0 候補として温存。**温存項目**: パス B（dev_mode autonomous 化、L0 spec-architect 経由）/ `ALLOWED_AUTHORS` の動的化（複数 contributor 体制になったら検討）/ destructive change detector（diff threshold / DELETE-heavy 検出、観測駆動で追加判断） |

## v5.5.2

### AD-021: gemini-review の diagnostics 縮退と PAT availability check 新設

| 項目 | 内容 |
|---|---|
| 状況 | v5.5.1 PR #40 で gemini-review GitHub Action（PR #37/#38 で導入）の運用テストが完了。8 commit にわたる段階的診断（仮説 A〜F + α）の結果、真因 = settings JSON `tools.core: []` / `includeTools` filter による tool exposure 阻害（α パッチで除去済）+ PAT permission 不足（ユーザーが Read+Write 付与済）と確定。診断目的で導入された暫定機構（`continue-on-error: true` / `GEMINI_DEBUG: "true"` / Diagnostics step 2 件）が役目を完遂し、本番運用構成への縮退が必要 |
| 判断 | **(a) Diagnostics 機構の削除**: `Diagnostics — runner / docker / GitHub MCP server reachability` + `Diagnostics — gemini_review step outcome` の 2 step、`continue-on-error: true`、`GEMINI_DEBUG: "true"` env、`id: gemini_review` を削除。**(b) `GH_REVIEW_PAT` availability check 新設**: `continue-on-error` 削除により PAT 未設定時に job hard-fail する事象を防ぐため、`GEMINI_API_KEY` と同形式の早期 availability check を追加し、両 secret available 時のみ `Run Gemini PR review` / `Upload gemini-artifacts` を実行する。**(c) Artifact upload は保持**: `actions/upload-artifact@v4` step は将来 debug 用に残置（low cost、retention 7 日）。**(d) prompt の self-PR fallback 方式維持**: v5.5.2 草案では PAT owner = PR author の構造的前提で APPROVE 試行を禁止する案だったが、Copilot review #41 line 184 で「他 maintainer が同 repo に PR を作った場合に誤った検閲となる」と指摘 → revert。v5.5.1 と同じ API 応答ベース fallback 方式（APPROVE 試行 → 拒否時のみ COMMENT fallback）を維持。**(e) settings JSON の security 注追加**: `includeTools` 不在で全 tool が expose される trade-off を明文化、v5.5.x 候補として絞り込み再検討を記録 |
| 根拠 | (a) v5.5.1 PR #40 で診断機構は「役目完遂後縮退」前提で導入されており本 patch はその完遂後実施、(b) self-PR APPROVE 制約はハードコードではなく API 応答ベース fallback で扱うのが unenforced repository assumption を排除する正しい設計（Copilot review #41 で指摘されて revert）、(c) Council 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当せず Council 諮問は不要、(d) philosophy.md §5「献上哲学」の「役目を終えた機構の縮退」原則と §3「情報純度」の「fail を fail として可視化」原則と整合 |
| 影響 | **operational behavior 変更（意図的、Copilot review #41 line 13/12/14 で指摘）**: `continue-on-error: true` 削除により transient Gemini/MCP failure が以前の silent success → 本 patch 以降は **hard-fail (red CI)** になる。これは観測可能な挙動変更だが、レビュー機構の fail を fail として可視化する設計判断として意図的。PAT availability check 新設で PAT 未設定環境では従来通りクリーン skip するため、設定不備による noisy red は発生しない。`.github/workflows/gemini-review.yml` 全体で約 50 line 縮減（324 → ~275 line、PAT check step 追加分を考慮）。SK 本文・harness-verifier・利用者プロジェクトへの影響ゼロ。`includeTools` 不在による security trade-off は v5.5.x 候補として温存（tool 名の正しい形式判明後に read 系のみへ絞り込み）。本 patch 自身が gemini-review の本番運用 3 例目テストとなり、新構成の動作確認を兼ねる |

## v5.5.1

### AD-020: Phase γ 先行宣言 4 の本実装（ストラングラー / BBA 射程外の正式宣言）

| 項目 | 内容 |
|---|---|
| 状況 | v5.5.0 の AD-019 で Phase γ コア 3 件（先行宣言 1/2/3）を本実装し、先行宣言 4（ストラングラー射程外宣言）+ 5（失敗アンチパターン早期検出）は v5.5.x patch / v5.6.0 へ温存とされた。先行宣言 4 は 4 行記述の先行宣言版で `handoff-to-evaluator.md` に存在していたが、Phase γ コア 3 件の実装過程で `handoff-to-evaluator.md` が VB6 移行事例（ストラングラー類似）と Branch by Abstraction に言及したため、L1 実装者が「先行宣言 2 → BBA 全パターン採用」と拡大解釈する誤りリスクが残置されていた |
| 判断 | 先行宣言 4 を v5.5.1 patch で本実装。`handoff-to-evaluator.md` の先行宣言 4 セクションを 4 行記述から 5 サブセクション（射程外要素の明示列挙 / 援用と全体採用の境界線 / L1/L2 禁止規約 / v6.0.0 昇格の観測トリガー / 整合性ガード）へ拡充。先行宣言 5 は引き続き温存（Phase β との一体化要件のため） |
| 根拠 | (a) v5.5.0 AD-019 で v5.5.x patch / v5.6.0 候補として既に明示済み、(b) Phase γ コア 3 件の実装で生じた拡大解釈リスクを Shift Left で防止する必要、(c) 明文化のみで機能変更ゼロ・後方互換完全維持のため patch で十分（minor 昇格不要）、(d) 観測駆動原則（`wf-baseline-rationale.md` §3）に従い v6.0.0 昇格条件を観測閾値（≥ 3 利用者プロジェクト要請）として明示することで温存範囲を限定、(e) Council 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当せず Council 諮問は不要 |
| 影響 | `layer0-archeo-architect/references/handoff-to-evaluator.md` の **4 箇所**を改修: (1) ステータスヘッダ / (2) ロードマップ表 / (3) 実装ステータス記述（Phase γ 詳細仕様 §冒頭の節）/ (4) 先行宣言 4 セクション本体（4 行 → 5 サブセクション）。SK 本文の機能変更ゼロ、既存 references の本文（追記のみ）、crosscut-* / templates/ / harness-verifier/ は機能不変。`refactor-intent-map.md` の I/O 契約不変。先行宣言 2/3 との整合性ガード（schema priority）を新設、今後の先行宣言 2 更新時に整合確認義務発生。Copilot review #39 line 14 で指摘された箇所数の事実誤認（3 → 4）を訂正済み |

## v5.5.0

以下 2 件は PR #33 ブレスト結晶 `delivery/AUTONOMOUS-DRIVE-BRAINSTORM-2026-05-02.md`（adrv01/02/03 全合意成立）を起源とする L0 設計判断 + L1 実装。確定ロードマップ「v5.5.0 = adrv01-Ph1 + Phase γ」に従い、v5.4.0 リリース翌日に L0 spec-architect で SPEC 化し、同セッション内で L1 が minor として実装。

### AD-018: AI 自己申告閾値の Council 連動明文化（adrv01-Ph1）

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF v0.1.0「自律駆動機構の哲学的座標」§2.2「拮抗判定検出主体」の Council 諮問 `council-2026-05-02T11:00:00Z-adrv01` で「(b) 独立観測機構 + 哲学者第3の道（メタ層構造）統合」が recommended、`agreed_with_modification`（段階的組み込みで止揚 Phase 1-3）。Phase 1 = AI 自己申告のみ運用（既存 Council confidence < 0.6 機構流用、コスト 0）の本実装が v5.5.0 スコープ |
| 判断 | `crosscut-council/SKILL.md §自己申告プロトコル` を新節として追加。confidence < 0.6 自己評価を Council 起動の正式トリガーとして明文化し、内部完結による回避を禁止。`pre-check.md` に scope/PR 境界 vs 新規思想 の判別シナリオ例追加（Copilot review feedback 由来）。`consensus-protocol.md` に escalated → 後付け合意のエッジケースと v5.6.0 Ph2 の hook 経路先行宣言を追加 |
| 根拠 | adrv01 Council 結果 + Council `vrfy01` 事例（category 誤選択が confidence 降下→escalation を連鎖した実例）。明文化のみで機構強化（hook 本実装）は v5.6.0 Ph2 へ温存。adrv01 の段階的組み込みで止揚パターンに整合 |
| 影響 | 既存 confidence < 0.6 機構の挙動は不変。新規実装ゼロ、明文化のみ。利用者プロジェクトには影響しない（DH 本体の規約改訂） |

### AD-019: Phase γ コア 3 件の本実装（archeo-architect 起点問題解決）

| 項目 | 内容 |
|---|---|
| 状況 | v5.4.0 で archeo-architect Phase α 雛形のみリリースされ、`handoff-to-evaluator.md` に Phase γ 詳細仕様 5 件が先行宣言された。起点問題（リファクタ依頼で 3〜4 個取りこぼす）の構造解決には L1 評価軸を「仕様適合 ∩ 動作 ∩ ユーザビリティ ∩ 意図合致」の 4 軸化が必須 |
| 判断 | 5 件中コア 3 件（先行宣言 1: 承認テスト生成プロトコル / 先行宣言 2: 自動照合ループ / 先行宣言 3: L1 意図合致軸統合）を v5.5.0 で本実装。先行宣言 4（ストラングラー射程外宣言）+ 5（失敗アンチパターン早期検出）は v5.5.x patch / v5.6.0 へ温存 |
| 根拠 | コア 3 件で起点問題は構造的に解決可能（refactor_directive: preserve / restructure / 評価軸 4 軸化の 3 領域カバー）。先行宣言 4/5 は周辺案件で minor 1 本のスコープを膨張させずに本リリースに集中できる |
| 影響 | `inferential-sensor-v2.md` 第 4 層に意図合致軸追加、`layer1-autonomous-dev/SKILL.md` §6 に承認テスト + 自動照合ループ追加、`layer1-independent-reviewer/SKILL.md` の評価軸 4 軸化、`delivery-format.md` に意図合致検証セクション追加、`handoff-to-evaluator.md` を先行宣言版から完全版（コア 3 件本実装）化。後方互換完全維持: `refactor-intent-map.md` 不在時は意図合致軸不発動 |

## v5.3.0

以下 3 件は HANDOFF「1 機能完遂の自律駆動 WF 設計」2026-04-30 を起源とする L0 設計判断 + L1 実装。
v5.2.0 リリース後に L0 で確定し、L1（layer1-autonomous-dev）が同日 v5.3.0 minor として実装。
後方互換維持（v5.0.0 / v5.1.0 / v5.2.0 と同パターン）。`crosscut-verifier-philosophy` 本実装は v5.3.x または v5.4.0 へ再後送。

### AD-015: 1 機能完遂 WF を「形状単一・薄い基底 + 観測駆動の厚化」とする

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF 論点 1（WF 基底テンプレート）で、bug-fix / 新規機能 / リファクタ / 仕様改訂等の機能タイプ別に WF 群を多様化するか、単一形状を保つか、最初から薄い基底だけ用意して厚化は観測に任せるかが拮抗。Council で案 N（多様化しない=哲学者）が weighted_score 3.25、案 H（Hybrid 薄い基底+観測駆動）が 4.65 で拮抗判定 |
| 判断 | 案 H 中核 + 案 N の運用原則化の統合採用。基底 WF は **layer1-autonomous-dev SKILL.md §処理フロー（1〜8）が現に基底**であり、これ以上の機能タイプ別 override / 分岐 WF を追加しない。機能タイプは context として動的注入され、分岐は §4「実装タスク分解」内の判断点として吸収。観測閾値（同一 override パターンが 3 機能タイプ以上で繰り返し発生）に達した場合のみ、Council 経由で基底側引き上げを再諮問する |
| 根拠 | Council 合議（invocation_id: council-2026-04-30T14:50:00Z-wfbase1, judgment_confidence 0.75）で recommended。理由: (a) 哲学者の「フラクタル原則 P1 は WF 形状の単一性を要求する」少数意見を運用原則として組み込むことで、機能タイプ軸分業（職種軸分業と同型の罠）を構造的に予防、(b) 案 H の「観測ベース厚化」は早期 over-engineering を回避し YAGNI 原則と整合、(c) 既存処理フローが thin baseline を充足している事実から差分実装ゼロで運用開始可能、(d) 第 3 の道「単一 WF + 動的 context 注入」は v6.0.0 major 候補として温存、(e) Phase 3 で WF 単一化が確定したため論点 3（WF 選択責任）は構造的に消失し、新規ディスパッチャ等は不要 |
| 影響 | 既存 `layer1-autonomous-dev/SKILL.md §処理フロー` の不変化を v5.3.0 で明文化（「§処理フローが現行 WF の基底であり機能タイプ別分岐を含めない」と原則節に追記）。`references/` に `wf-baseline-rationale.md` を新設し、観測閾値・厚化トリガー・Council 再諮問条件を記録。L1 実装スコープは差分が極小（原則節 1 段落 + reference 1 件のみ） |

### AD-016: 献上トリガー第 4 種「Type D（異常献上）」を追加する

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF 論点 2（献上トリガー 4 種の関係）で、現行の Type A（仕様レビュー結果）/ Type B（成果物）/ Type C（仕様改訂提案）に対し、AI 自己解決不能な技術的例外（依存破損 / env 不能 / 想定外例外等）の献上経路が暗黙のままだった。Council で案 D（Type D 新設）が weighted_score 4.5 で recommended、哲学者は「第 3 の道: 献上 3 軸構造（トリガー × 中身 × 権限）の哲学化」を主張 |
| 判断 | philosophy.md §5（または現行 5 本柱規定の関連節）に Type D を minor 追加する。発動条件は **AI 自己解決不能な技術的例外**（依存破損・env 不能・想定外例外）に限定し、Type A（仕様起因）から経路分離する。哲学者の献上 3 軸構造は philosophy 第 8 条候補（第 7 条＝次元論と D4 の独立性 と並列の「献上 3 軸の存在論」）として温存し、v6.0.0 major 昇格時に併合検討 |
| 根拠 | Council 合議（invocation_id: council-2026-04-30T14:30:00Z-wfsurf1, judgment_confidence 0.72）で recommended。理由: (a) Type A（仕様改訂）と Type D（技術例外）は本質的に異なる経路（前者は L0 への差し戻し、後者は人間判断要請）であり混同は P3 責務分離違反、(b) 現状でも Type A に詰め込まれ実運用しているが暗黙化は philosophy P4 情報純度違反、(c) minor 追加で済むため major 昇格不要、(d) 哲学者の懸念（5 年スパンで Type E/F/G 追加要求が再発する罠）は 3 軸構造を v6.0.0 候補として温存することで構造的に応答 |
| 影響 | `layer1-autonomous-dev/SKILL.md §8 献上`の表に Type D 行を追加。`references/delivery-format.md` に Type D フォーマット節を追加（発動条件・必須項目・人間アクション期待値）。philosophy.md §5 に Type D 言及を 1 段落追加（哲学者意見の温存記述含む）。v6.0.0 候補として `history/INTENT.md` に「献上 3 軸構造」を温存記載 |

### AD-017: WF 選択責任は新規プロトコル不要、既存メカニズムで吸収

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF 論点 3（WF 選択責任）は当初「ユーザー指示を受けた時にどの WF を起動するか誰が決めるか」を問うていた。AD-015 により WF が単一形状で確定したため、選択問題自体が構造的に消失した |
| 判断 | 新規ディスパッチャ WF / 選択責任プロトコルを設計しない。残課題の 3 種（i 機能タイプ誤認 / ii モード判定誤り / iii 権限・CTL 誤り）は既存メカニズムで吸収する：(i) 既存 Type C（仕様改訂提案）、(ii) 既存「体制事後評価」、(iii) AD-016 の Type D（異常献上）。本判断は Council 起動せず実装者裁量で決定し、ユーザー承認 (Phase 4 「Phase 5 へ進む」) で確定 |
| 根拠 | (a) AD-015 の論理的帰結として WF 選択問題が消失、(b) 残課題 3 種が既存救済経路に 1:1 でマッピング可能、(c) Council 起動条件（philosophy §6 / `crosscut-council` 発動基準）「複数案拮抗・confidence < 0.6・不可逆操作」のいずれにも該当しない、(d) 実装者 confidence 0.75、(e) 「明確な仕様に基づく素直な実装」に該当 |
| 影響 | 設計差分ゼロ。WF 選択責任に関する spec/skill 改修は発生しない。本 AD は decision の不在（=「設計しない」）を明示記録するための meta-AD として機能（後年の再諮問抑止が目的） |

## v5.2.0

### AD-010: 5 次元論（D1〜D5）の導入と D-numbering 採用

| 項目 | 内容 |
|---|---|
| 状況 | DH の検証機構（5 層検出スタック / crosscut-verifier-drift / §7.4 自己検証等）が、それぞれどの抽象階層を対象にしているかが暗黙のままで、責務重複・責務漏れ判定が困難だった |
| 判断 | 5 次元論を導入：D1（ソースコード）/ D2（開発環境）/ D3（配布 skill インスタンス）/ D4（マスタ skill = メタスキル）/ D5（Meta モニタリング層 = 人間）。機械可読命名は D-numbering、思想文書では meta-layer / meta-meta-layer 等の階層形容詞を併走させる二重命名 |
| 根拠 | Council 合議（invocation_id: council-2026-04-29T21:00:00Z-d4mtr1, 論点 1）で D-numbering を recommended（judgment_confidence 0.78）。理由: (a) 既存 M1/M2/L0/L1/L2/CTL と prefix 衝突なし、(b) 短く grep 性能良好、(c) 案 b の T-numbering は既存予約のチーム軸 T1-T5 と衝突する致命的問題、(d) 案 c 階層形容詞は冗長で表記揺れリスク。哲学者の「関係性を呼び起こす命名は思想的支柱」少数意見を二重命名で吸収 |
| 影響 | layer0-spec-architect SKILL.md に v5.2.0 セクション追加、harness-verifier/PHILOSOPHY.md / BOUNDARY.md で 5 次元定義を明示。既存 skill の用語使用には影響なし |

### AD-011: D4 検査機構を DH 本体外（リポジトリルート直下）に独立配置

| 項目 | 内容 |
|---|---|
| 状況 | DH は生成物（D2/D3）の検証機構を完備していたが D4 自身の整合性検査が不在（靴屋の靴問題）。フラクタル原則 P1 の自然な拡張として「規律の自己相似性」を実装する必要があった。`.claude/skills/` 配下の crosscut-* skill として実装する案（crosscut-verifier-self-static 新設）と、DH 本体外に独立配置する案が拮抗 |
| 判断 | リポジトリルート直下 `harness-verifier/` に独立配置する。`.claude/skills/` 配下には置かない。`crosscut-verifier-drift` の拡張案も却下 |
| 根拠 | DH 内部 skill として実装すると自己言及パラドックス（自身が壊れたら自身を検査できない循環）が生じる。論理階層が一段違う（D4 vs D4 を検査する機構＝メタメタ層）ため Russell タイプ理論・Gödel 不完全性定理と同型の構造的回避が必要。HANDOFF §4.1 の特異点メタファに従う。Council 出力（案A: DH 内部 skill 新設）よりも哲学者の「特異点扱い」少数意見が、ユーザー確定の独立性要請（C: 一切影響されない独立性）と整合 |
| 影響 | 新規ディレクトリ `harness-verifier/` を作成。DH 本体（`.claude/skills/`）の挙動は完全不変。本機構は DH 本体に **読み取り専用** で依存（逆方向の依存は禁止） |

### AD-012: D4 検査機構の名称を `harness-verifier/` とする命名判断

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF 仮称 `self-monitoring/` は「self-」誤読リスク（自己が自己を監視＝独立性要請に反する読み）を持つ。命名候補: meta-verifier / harness-verifier / dh-integrity / singularity 等が拮抗 |
| 判断 | ディレクトリ名・機械可読名は `harness-verifier/` を採用。PHILOSOPHY.md 冒頭で「別名: singularity（特異点メタファ）」を併記する二重命名 |
| 根拠 | Council 合議（invocation_id 同上, 論点 2）で recommended（judgment_confidence 0.82）。理由: (a) `crosscut-verifier-drift` / `verifier-philosophy` と命名形式が同型でフラクタル原則 P1 整合、(b) 動詞由来（verifier）でファイル群の責務が明示、(c) grep 性能良好、(d) 外部説明コスト最小。哲学者の「singularity を命名で宣言する」少数意見は PHILOSOPHY.md 内で吸収 |
| 影響 | ディレクトリ名・コード・grep 対象では `harness-verifier` で統一。PHILOSOPHY.md においてのみ singularity 表記を保持 |

### AD-014: harness-verifier の glossary.yml を subset YAML 形式に限定する

| 項目 | 内容 |
|---|---|
| 状況 | 独立検証 (VERIFICATION-v5.2.0.md) で C-1 として、`harness-verifier/checks/glossary.py` の `_parse_yaml` が複数行 block list 構文 `- item` を誤読し、検査 5（用語辞書整合）が空回りしていた事象が判明。`forbidden_uses` の最初の要素消失、`crosscut_prefix.members` / `layern_prefix.members` の空 dict 化を確認 |
| 判断 | `glossary.yml` を **subset YAML 形式** に限定する。block list 構文を使用禁止とし、インライン list / list of dict のみ許容。パーサが block list 構文を検出した時点で `SyntaxError` を raise（黙って誤読しない）。BOUNDARY.md §9 に「独立性の代償」として明文化 |
| 根拠 | Council 合議（invocation_id: council-2026-04-29T22:30:00Z-c1fix1）で recommended（judgment_confidence 0.88）。3 ペルソナ全会一致で「案 b（インラインリスト書き換え）」を支持、開発者が「+ 案 a の防御コード」を補強、哲学者が「+ ドキュメント宣言」を補強する三段統合に着地。案 c（PyYAML 採用）は哲学者が「独立性要請の最初の妥協、5 本柱 P3（情報純度）侵食」と却下、本案件のスコープを越える BOUNDARY.md 改訂を要するため後送。subset YAML 制約により (i) C-1 即解消、(ii) 将来の偽陽性を構造的予防、(iii) 独立性要請の哲学的根拠強化を同時達成 |
| 影響 | `harness-verifier/glossary.yml` を subset YAML 形式に書き換え（forbidden_uses / members をインライン化）。`harness-verifier/checks/glossary.py` の `_parse_yaml` に block list 検出 → SyntaxError 機構を追加、加えてインライン list of dict 完全対応を含む全面改修（ネスト dict / quote 保持 / top-level split）。BOUNDARY.md §9「独立性の代償」を追加。glossary.yml 冒頭コメントで形式制約を明示。少数意見として「subset YAML が glossary 肥大化時に破綻したら PyYAML 採用を Council 再諮問」を温存 |

### AD-013: バージョン昇格を v5.2.0 minor とし philosophy verifier 本実装は v5.3.0 へ後送

| 項目 | 内容 |
|---|---|
| 状況 | 次元論導入 + D4 検査機構実装は (a) v5.2.0 minor / (b) v6.0.0 major / (c) v5.2.0 minor で次元論+D4 機構、philosophy verifier は v5.3.0 へ後送、の 3 案で拮抗 |
| 判断 | (c) v5.2.0 minor で次元論導入 + D4 検査機構（harness-verifier/）実装、`crosscut-verifier-philosophy` 本実装は v5.3.0 へ後送 |
| 根拠 | Council 合議（invocation_id 同上, 論点 3）で recommended（judgment_confidence 0.70）。理由: (a) 後方互換完全維持（新規ディレクトリ追加のみ、既存 SKILL.md / references / crosscut-* 不変）、(b) AD-008 / AD-009 の前例（後方互換維持で minor）と整合、(c) 開発者の semver 厳格論と経営者のリリース文脈説明可能性を両立。哲学者の「次元論導入は major 級の自己同定更新」少数意見は v6.0.0 で philosophy.md 第 7 条として吸収する候補として保持 |
| 影響 | v5.1.0 → v5.2.0、後方互換維持。`crosscut-verifier-philosophy/` placeholder は v5.2.0 でも未実装のまま、v5.3.0 候補として継続検討 |

## v5.1.0

### AD-008: L0 完了の定義をドキュメント生成完了から「scaffold smoke test 通過 + 受け入れ基準充足」へ再定義

| 項目 | 内容 |
|---|---|
| 状況 | PR #19 テストレビュー（シナリオ「ケロぴの森」）で L0 が SPEC.md / DONT.md / REGIME.md の生成は完遂したが、L1 が即座に開発開始できる scaffold が一切生成されず、参照ファイル 8 種も未読のまま L0 完了と判定されていた。L0 charter「AI 自律駆動開発が可能な開発環境の構築」が達成不能 |
| 判断 | L0 完了の定義を「ドキュメント生成完了」から「§0 受け入れ基準 4 条件すべて充足（仕様充足 / scaffold 実体生成 / smoke test 通過または保留事由明記 / §7.4 自己検証 PASS）」に再定義する |
| 根拠 | 5 本柱原則 P3（責務分離）と P4（情報純度）に整合。L0 が「実行可能な開発環境を作る」という charter を満たさないまま L1 へ譲渡することは責務不履行であり、人間 ≒ Council 原則（philosophy.md 第6条）の観点でも検証層の前段で受け入れ基準を確定する必要がある |
| 影響 | SKILL.md §0 に受け入れ基準セクションを追加。Lifecycle ≥ 1 既存プロジェクトには段階適用とし、既存成果物の遡及修正は要求しない（後方互換維持） |

### AD-009: scaffold-checklist の単一 stack（Vite+TS+React+PWA）採用方針

| 項目 | 内容 |
|---|---|
| 状況 | scaffold-checklist.md を新設するにあたり、複数 stack を初期から網羅するか単一 stack に絞るかを判断する必要があった |
| 判断 | v5.1.0 では Vite + TypeScript + React + PWA の **1 stack に絞る**。他 stack（Next.js / Vue / Astro / SvelteKit / 純 Node CLI）は将来 minor で追加 |
| 根拠 | (a) PR #19 テストレビュー対象が M2 monolith Web PWA で本 stack に直結する、(b) scaffold-checklist は「実体ファイルの厳密な必須リスト」が責務であり、stack ごとに必須要件が異なるため網羅は本リリース範囲を逸脱、(c) 利用者数が多い stack を一つ確定させてから stack 別の最小要件パターンを抽出するほうが将来 minor の品質が上がる |
| 影響 | 他 stack を使う既存プロジェクトでは scaffold-checklist の対象外となるが、§0 受け入れ基準 2「対応 stack テンプレートで指示されたファイル群」と表現することで「対応 stack なし → 該当条項は適用対象外」と扱える。将来 minor で stack 追加時は scaffold-checklist 内の「将来拡張ポイント」表に従う |

## v5.0.0

### AD-001: crosscut- prefix の導入

| 項目 | 内容 |
|---|---|
| 状況 | council/ は「全 Layer 横断」の判定機構だが、命名が層構造を示していなかった |
| 判断 | `crosscut-` prefix を Level A skill の第二の命名規則として確立し、`council/` を `crosscut-council/` にリネーム |
| 根拠 | spec §3.1.3 / §4.1。3 層 + 1 横断の構造を命名で明示化、フラクタル原則 P1 に整合 |
| 影響 | 後方互換破壊（major 昇格）。既存プロジェクト側の参照は migration-guide で個別対応 |

### AD-002: dev_mode 軸の追加

| 項目 | 内容 |
|---|---|
| 状況 | 既存軸（規模 S / 不確実性 U / リスク R / NFR N / Lifecycle）に GitHub 連携前提の判定軸が無かった |
| 判断 | dev_mode 軸（local_only / github_assisted / github_autonomous）を 3 軸目の動的判定軸として追加 |
| 根拠 | spec §3.2.1〜§3.2.3。GitHub 無しでも DH ベースは完全動作の原則を保ちつつ段階的移行を可能にする |
| 影響 | regime-assessment.md / REGIME.md テンプレ拡張。後方互換あり（既存プロジェクトは local_only 相当として扱える） |

### AD-003: 仕様 1〜4 を crosscut- skill 化

| 項目 | 内容 |
|---|---|
| 状況 | GitHub 連携の 4 仕様（Issue 射出・実装・検証・還流）は L0/L1/L2 のいずれにも純粋には属さず、横断的に発動する |
| 判断 | 仕様 1〜4 を `crosscut-issue-dispatcher` / `crosscut-issue-implementer` / `crosscut-verifier-drift` / `crosscut-verifier-philosophy` (placeholder) / `crosscut-feedback-loop` の 5 skill として配置 |
| 根拠 | spec §4.3。3 層 + 1 横断構造の維持、責務分離（P3）、各 skill の同型構造によるフラクタル原則発現 |
| 影響 | 新規 skill 5 件追加。layer1-* から参照を追加、既存 layer 機構は不変 |

### AD-004: CTL 連動条件分岐の組み込み

| 項目 | 内容 |
|---|---|
| 状況 | CTL システム（v4.2 で追加）は判定ロジックは存在したが、各 skill の動作分岐に組み込まれていなかった |
| 判断 | 仕様 1〜4 すべての protocol references で CTL-0/1/2/3 の段階的自動化を明文化 |
| 根拠 | spec §3.2.4〜§3.2.7、§4.4。再帰進化原則 P2 を CTL 育成戦略として実装 |
| 影響 | 各 crosscut- skill 配下に protocol.md を追加。CTL 育成戦略は ctl-maturity-strategy.md として独立 |

### AD-005: claude-code-action 公式採用

| 項目 | 内容 |
|---|---|
| 状況 | Issue → 実装の自動化手段として複数選択肢があった |
| 判断 | Anthropic 公式の claude-code-action を採用、GitHub Actions 雛形に組み込み |
| 根拠 | spec §3.2.5、§3.2.9。業界 BP 取り込み、保守性、エコシステム整合性 |
| 影響 | templates/.github/workflows/issue-to-impl.yml の依存。バージョンは `<latest>` プレースホルダ（実装時点で公式リポジトリ確認） |

### AD-007: docs/ ディレクトリの限定許可

| 項目 | 内容 |
|---|---|
| 状況 | リポジトリは "skill-only policy" (PR #3) で `docs/` を gitignore 済み。spec §5.4.2 が `docs/migration-guide-v5.0.0.md` を v5.0.0 配布物として要求 |
| 判断 | `docs/` 全体の gitignore は維持しつつ、配布対象の migration guide のみを許可（`!docs/migration-guide-*.md`） |
| 根拠 | 設計ドラフト（drafts policy）と配布ドキュメント（migration guide）は性質が異なる。最小例外で skill-only policy の精神を保つ |
| 影響 | `.gitignore` 1 行追加。今後の v6.0.0 以降の migration guide も同パターンで許可される |

### AD-006: README バッジ作業のスキップ（適用対象外）

| 項目 | 内容 |
|---|---|
| 状況 | spec §4.6.2.4 で README に v5.0.0 バッジを追加する指示があるが、リポジトリルートに README.md が存在しない |
| 判断 | README バッジ追加作業はスキップ。SKILL.md バージョン履歴 / credit-template.md / REGIME-LOG.md でバージョン更新を完結させる |
| 根拠 | スキルは SKILL.md の frontmatter + 本文が標準。README は人間向けプロジェクト紹介で本案件のスコープ外。SELF-VERIFICATION §5.3.2 で「適用対象外」明記 |
| 影響 | バージョン更新は他経路で完結。README 整備は別案件として保留 |

### AD-021: AI 駆動開発における PR 粒度の決定基準（v5.16.0）

| 項目 | 内容 |
|---|---|
| 状況 | v5.15.0 PR (#91) で Copilot レビュー 5+4 件指摘が全て妥当に機能した実証データ取得。Council `council-2026-05-12T14:30:00Z-adpp01` で「人間刻みではなく AI スペック依存の開発スピード」方針の是非を諮問 |
| 判断 | β 中核採用 (semver 維持、1 minor スコープを AI レビュー可能上限まで拡張) + α/ε 条件統合。7 項目の運用ルールを採択 |
| 根拠 | philosophy 第 1/3/4 条。3 ペルソナ全員が現状維持 (δ) を却下し AI スペック依存方向を支持。重み付き判定で β=4.68 / ε=1.50 / α=1.44。判定 confidence 0.76 |
| 影響 | (1) semver は技術的境界のみ (major/minor/patch) (2) 1 minor 1 議題縛り廃止 (3) PR 粒度上限は harness-verifier 全 PASS + Copilot 妥当率 80%+ で定義 (4) AI 能力バージョンを判定基準として明示 (5) 例外領域 = major bump / philosophy.md 改訂 / 破壊的影響 (6) PR 粒度判断ゲート = Council 起動 (7) scope_lock 不在で 5 ファイル超変更は Council 推奨。v5.16.0 を最初の実証 PR とする |

### AD-022: L0 三兄弟スキルの DESIGN.md 対応マトリクス（v5.16.0）

| 項目 | 内容 |
|---|---|
| 状況 | v5.15.0 で DESIGN.md 機能を layer0-spec-architect に追加完了。layer0-onboarding (既存プロジェクトの harness 後付け) と layer0-archeo-architect (リファクタ前の意図復元) は未対応で L0 三兄弟が非対称 |
| 判断 | v5.16.0 で三兄弟均質化。onboarding に reverse-design ステップ (既存 src/ から色・font・spacing 逆抽出して DESIGN.md 初版生成)、archeo-architect の意図マップに視覚 Island (リファクタ前の視覚仕様意図復元) を追加 |
| 根拠 | philosophy 第 1 条フラクタル原則: L0 三兄弟は同一形状の責務、関心事 (DESIGN.md) は形状に乗るべき横軸。第 5 条献上哲学: 利用者プロジェクトに片足対応を献上することは情報純度違反。Council `council-2026-05-12T13:32:00Z-sspr01` revised C 採用 |
| 影響 | layer0-onboarding/SKILL.md と references/ に reverse-design 手順追加。layer0-archeo-architect の意図マップスキーマに visual_intent_island フィールド追加。L0 三兄弟対応マトリクスを REGIME-LOG.md に記録 |
