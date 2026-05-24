# REGIME-LOG

DH 本体のモード判定・major/minor 昇格の記録。

## v5.18.0（minor 昇格、Supabase ローカル開発の推奨オプション化）

- 判定日: 2026-05-24
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer0-spec-architect 対話セッション（L0 メタスキル開発案件、本番 Supabase 保護フローの推奨オプション化）
- 起源: フロント Next.js（Vercel）+ 本番 Supabase 無料枠（消失 NG 私的データ）構成での「本番を汚さずローカルで開発したい」要請。開発時の推奨選択肢として Supabase ローカル展開を L0 に取り込む
- L0 対話確定: 組込方式 = 「専用 reference + 軽い配線」（#107 データモデリング吸収と同方針だがツール固有プレイブックのため専用 reference 形式）、推奨発動条件 = 「保護すべき本番 Supabase/hosted Postgres 使用時」（S1 = DB 使用あり + hosted Postgres/Supabase + 消失 NG データ）
- 範囲: 新規 skill / agent なし。`references/supabase-local-dev.md` 新設 + 既存 5 ファイル（SKILL.md 本体 + reference 4 件: dialog-questions / scaffold-checklist / schema-evolution / subphase-l02-domain）への配線。後方互換 100%
- 自己検証: `harness-verifier/verify.py` 6 項目すべて PASS（frontmatter / 参照 path / SK 間参照 / 5 層構造 / 用語辞書 / hook 観測）

## v5.10.0（minor 昇格、in progress、issue-pickup.yml body_check の type-aware 化）

- 判定日: 2026-05-07
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer0-spec-architect 対話セッション（v5.9.0 merge 後の autonomous-drive 起動失敗観測を起点）
- 起源: 5 issues (#47/#49/#53/#54/#57) が `body_check` で一律ブロックされる事象。L0 spec-architect 起票の discussion-style issue が bug-style 形式を前提とした body_check に弾かれていた **規格漏れ**
- L0 譲渡: Issue #61 で 5 軸 (A〜E) 確定 → 本 PR で実装
- 自己検証: workflow YAML syntax / `harness-verifier/verify.py --strict` 全項目 PASS
- Council 諮問: なし（軸が明確で拮抗していないため、judgment_confidence > 0.7、Council 不要と判断）

### 非破壊変更（後方互換維持）

| ファイル | 変更内容 |
|---|---|
| `.github/workflows/issue-pickup.yml` | `body_check` ステップを type-aware 化。`discussion` ラベル有無で必須セクションを分岐 |
| `templates/github-workflows/issue-pickup.yml.template` | 同様の変更を mirror |
| `.claude/skills/crosscut-issue-implementer/SKILL.md` | §Issue 本文必須セクション規格 (v5.10.0) 新設 |
| `.claude/skills/crosscut-issue-quality-gate/SKILL.md` | §Issue Type 分岐ルール (v5.10.0) 追加 |
| `history/CHANGELOG.md` / `history/REGIME-LOG.md` | v5.10.0 セクション追加 |

破壊的変更なし。`discussion` ラベルなし issue は現行の 3 セクション必須を維持。

### opt-in 領域該当性

`issue-pickup.yml` 改修 = `auto-merge-boundary.md §opt-in 領域`「autonomous-drive workflow 自身の改修」該当。本 PR は `human-review-needed` ラベル必須、人間レビュー後に解除して auto-merge 再評価。

### dev_mode

不変。`autonomous` + `autonomous_scope: full` の運用継続。

### post-merge 復旧手順（既存ブロック 5 issues）

```bash
for ISSUE in 47 49 53 54 57; do
  gh issue edit $ISSUE --remove-label needs-clarification
  gh issue edit $ISSUE --remove-label ready-for-ai
  gh issue edit $ISSUE --add-label ready-for-ai  # 再 trigger
done
```

### v5.10.0 第 2 弾: gemini-review 入力・プロンプト規格再設計（Issue #49、PR #67）

- 判定日: 2026-05-08
- 改修主体: layer0-spec-architect 対話 (Issue #49) で 5 軸 (A〜E) を確定 → 最小セット F1-F3 + A1 + B4 + G1 を実装
- 起源: PR #34 〜 #48 の運用観測。Issue #46 (Quality Gate, v5.8.0) 完成と並ぶ「PR 段階の品質ガード」再設計
- L0 譲渡: Issue #49 で完了
- Council 諮問: なし（軸が明確で拮抗していないため、judgment_confidence > 0.7）
- bot 実装失敗 → 手動実装 (Issue #61 と同型の workflow file push 拒否ケース): claude-code-action GitHub App は workflow file への push 権限を持たないため、Type B 失敗となった bot 実装内容を Windows ローカルから L0 確定軸に沿って再実装

#### 非破壊変更（後方互換維持）

| ファイル | 変更内容 |
|---|---|
| `.github/workflows/gemini-review.yml` | F1-F3 (includeTools 絞り込み) + A1 (context 事前注入 step) + B4 (self-PR 検出 step) |
| `templates/github-workflows/gemini-review.yml.template` | 同様の変更を mirror (G1 template 骨格) |

破壊的変更なし。`includeTools` で expose する tool 名は github-mcp-server v0.27.0 の命名前提で、実運用観測で必要に応じて調整。

#### opt-in 領域該当性

`gemini-review.yml` 改修 = `auto-merge-boundary.md §opt-in 領域`該当。`human-review-needed` ラベル必須。

### v5.10.0 第 3 弾: claude-code-action gh pr create fallback（Issue #51、PR #68）

- 判定日: 2026-05-08
- 改修主体: layer0-spec-architect 対話 (Issue #51) で 4 軸 (A〜D) を確定 → 手動実装
- 起源: PR #50 (9 例目完遂時) の観測 + 本セッション内で再発 (#47/#53/#54/#57 が同じ穴で Type A 失敗)
- L0 譲渡: Issue #51 で完了
- Council 諮問: なし（軸が明確で拮抗していないため）
- bot 実装失敗 → 手動実装 (Issue #61, #49 と同型の workflow file push 拒否)

#### 非破壊変更（後方互換維持）

| ファイル | 変更内容 |
|---|---|
| `.github/workflows/issue-pickup.yml` | 新 step `Create PR (fallback if claude-code-action skipped)` を claude_impl success 後に追加 |
| `templates/github-workflows/issue-pickup.yml.template` | 同様の変更を mirror |

#### opt-in 領域該当性

`issue-pickup.yml` 改修 = `auto-merge-boundary.md §opt-in 領域`該当。`human-review-needed` ラベル必須。

---

## v5.9.0（minor 昇格、in progress、auto-merge opt-in→opt-out 反転 + cookpato retro A1〜A5 取り込み）

- 判定日: 2026-05-06
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer0-spec-architect 対話セッション（auto-merge 反転論点の初出）→ Council 諮問 → SPEC 改修
- 起源: PR #33（v5.4.0 後の docs/brainstorm draft PR）が 4 日間放置されている事例の発見と、ユーザー発言「人間は多少のことは無関心、暗黙オートが基本」を起点とする
- L0 譲渡: 対話セッション内で完結（philosophy 改修を伴うため Council 諮問必須）
- 自己検証: workflow YAML syntax / `harness-verifier/verify.py --strict` 全項目 PASS（実行予定）
- Council 諮問: `council-2026-05-06T08:30:00Z-amrev1`（business / category=conception / phase_3 / unanimous / judgment_confidence=0.80 / consensus_mode=auto_agree / implementer_consent=agreed_with_modification）

### 非破壊変更 + 1 件の破壊的変更（opt-in→opt-out 反転、roll-back プロトコル付き）

| 項目 | 内容 | 影響種別 |
|---|---|---|
| auto-merge.yml 条件 1 反転 | whitelist (`auto-merge` ラベル必須) → blacklist (stop ラベル不在) | **破壊的変更**（既存 PR で `auto-merge` ラベル付与運用していた利用者プロジェクトは挙動変化、roll-back プロトコルでカバー） |
| issue-pickup.yml 改修 | `--label auto-merge` 自動付与削除、opt-in 領域該当時のみ `--label human-review-needed` | 非破壊（autonomous_scope: full 既存プロジェクトは新挙動を享受） |
| 境界 SPEC 新設 | `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md` | 新規（opt-in 領域 8 項目、stop ラベル定義、roll-back プロトコル、メタ承認機構） |
| philosophy 改修 | 第 7 条 §autonomous-drive §auto-merge デフォルト方針 を新設、P4 暴走時介入を stop ラベル群に拡張 | 非破壊（追記、既存条文不変） |
| 既存 `auto-merge` ラベル廃止 | deployment では作成しない、自動付与削除 | 非破壊（残存しても merge 判定に影響しない、stop ラベル方式で代替） |
| cookpato retro A1〜A5 取り込み | 既存 PR/Issue 群（#53/#54/#55/#56/#57/#46）で進行 | 非破壊（個別 PR レベル） |
| バージョン | v5.8.0 → v5.9.0（minor 昇格）。新機能追加 + autonomous-drive 機構の哲学反転 | — |

### dev_mode 判定（変更なし）

REGIME.md の `dev_mode` は `github_assisted` のまま据え置き。本 minor は autonomous-drive 機構の哲学反転であり、DH 本体自身の dev_mode 昇格は伴わない。`autonomous_scope` 軸も既存通り（`full` / `merge_gated` / `custom`）、ただし stop ラベル運用方針が `autonomous_scope` 別に変更（詳細は `crosscut-issue-implementer/SKILL.md §CTL との関係`）。

### Council 諮問の根拠

本判定は philosophy.md 改修を伴う conception カテゴリのため Council 諮問が必須（philosophy 第 6 条「Council 起動条件」）。3 ペルソナ（経営者 weight 3 / 開発者 weight 3 / 哲学者 weight 5）が unanimous で C ハイブリッドに収束、weighted_score 7.31 / 全 weight 11（100%）で支配的。哲学者 confidence 0.55 で 4 実装要件（境界 SPEC 不変化 / roll-back プロトコル / `auto-merge` ラベル廃止 / メタ承認機構）が minority_opinion として SPEC に同梱。implementer_consent=agreed_with_modification。

### roll-back 評価ゲート（2026-11-06）

評価指標 4 項目（暗黙 merge 事故件数 1 件以上 / AI 判定漏れ率 5% 超 / 境界曖昧化月 2 件以上 / 二重ラベル腐敗 1 件）のいずれかで Council 再諮問 → 必要に応じて opt-in モデル復帰。詳細は `auto-merge-boundary.md §roll-back プロトコル`。

## v5.7.2（patch 昇格、OIDC permission bug fix）

- 判定日: 2026-05-04
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer0-spec-architect 対話セッション内で発見 → 同セッションで実装
- 起源: Issue #46 (`crosscut-issue-quality-gate` 設計、v5.8.0 候補) を実装トリガーに v5.7.1 の `claude-code-action@v0` 経路の初の本番テスト → OIDC token error で顕在化
- L0 譲渡: 本 patch は単純 single-line bug fix で HANDOFF 不要、対話セッション内で完結
- 自己検証: workflow YAML syntax 確認、`harness-verifier/verify.py` 全項目 PASS
- Council 諮問: なし（自明な single-line bug fix、複数案拮抗なし、不可逆操作なし、SPEC 矛盾なし）

### 非破壊変更（破壊項目なし、後方互換完全維持）

| 項目 | 内容 | 影響種別 |
|---|---|---|
| `id-token: write` permission 追加 | `issue-pickup.yml` + `issue-pickup.yml.template` の `permissions:` ブロックに 1 行追加 | 非破壊（既存挙動に影響しない、追加権限のみ） |
| v5.7.1 release 化同梱 | (in progress) → (released 2026-05-03) 化を housekeeping として同梱（**8 例目正規適用**） | 非破壊（記録のみ） |

### 副次目的

- 本 patch 自身が **Issue #46 の autonomous-drive 完遂前提条件** + **v5.7.1 機構の動作確認** のダブルテストを兼ねる
- merge 後、Issue #46 の `in-progress` ラベル除去 + `ready-for-ai` 再付与で再 trigger を実施

## v5.7.1（patch 昇格、AD-026 訂正）

- 判定日: 2026-05-03
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer0-spec-architect → layer1-autonomous-dev で実装
- 起源: ユーザー要請「実装は Claude Code CLI で、サブスクで稼働、Gemini はフォールバック」+ 新事実「`CLAUDE_CODE_OAUTH_TOKEN` 経路で API 課金回避可能」
- L0 譲渡: `delivery/HANDOFF-v5.7.1-claude-code-pivot.md`
- 自己検証: `harness-verifier/verify.py` 全項目 PASS、`delivery/SELF-VERIFICATION-v5.7.1.md`
- Council 諮問: なし

### 非破壊変更（破壊項目なし、後方互換完全維持）

| 項目 | 内容 | 影響種別 |
|---|---|---|
| 実装エージェント方式変更 | crosscut-issue-implementer の実装エージェントを gemini-cli → Claude Code CLI メイン + gemini フォールバックへ。`CLAUDE_CODE_OAUTH_TOKEN` (Pro/Max サブスクリプション) で稼働、追加 API 課金なし | 非破壊（v5.7.0 deploy 済プロジェクトは旧 workflow 維持可、新規 deploy で新方式採用） |
| AD-026 訂正 | AD-029 新設で「v5.7.0 当時の判断、新事実発見で訂正」を記録。AD-026 自体は削除せず historical 維持 | 非破壊（記録のみ） |
| gemini-cli 用途整理 | AI triage = メイン継続、実装フォールバック、PR レビュー = メイン継続 | 非破壊（既存用途維持 + 新フォールバック追加） |
| Claude Code 失敗時挙動 | label `pickup-failed` + notice → 人間 P4 判断（自動フォールバックなし）| 新規（philosophy 第 4 条 + 第 7 条 P4 整合）|
| 履歴記録 | CHANGELOG / INTENT / REGIME-LOG（本ファイル）/ ARCH-DECISIONS (AD-029) に記録 | 非破壊 |
| 同梱 housekeeping | v5.7.0 (in progress) → (released 2026-05-03) 化（**7 例目正規適用**）| 非破壊 |
| バージョン | v5.7.0 → v5.7.1（patch 昇格）。philosophy.md 改訂なし、実装手段の差し替えのみ、SPEC 改修範囲は限定的 | — |

破壊項目なし。利用者プロジェクトには強制配布されない（v5.0.0〜v5.7.0 と同パターン）。

### Council 諮問の有無

本 patch は Council 諮問なしで実施（理由）: (a) 11+7 論点全て対話で合意、(b) 複数案拮抗なし（OAuth token 経路の発見でユーザー要望が一意に確定）、(c) 実装者 confidence ≥ 0.7、(d) `crosscut-council` 起動条件のいずれにも該当しない。**ただし autonomous-dev が実装中に gemini フォールバック発動条件で confidence < 0.6 を検出した場合は独自 Council 起動可**（adrv01-Ph1 自己申告プロトコル経由）。

## v5.7.0（minor 昇格、後方互換維持）

- 判定日: 2026-05-03
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer0-spec-architect（本セッションで起動）→ layer1-autonomous-dev で実装
- 起源: ユーザー（ひでさん）の明示要請「Bを考えよう」+ 「Issue 選択は開発品質を決める」観点。v5.6.0 INTENT 温存項目の本格仕様化
- L0 譲渡: `delivery/HANDOFF-v5.7.0-issue-pickup.md`
- 自己検証: `harness-verifier/verify.py` 全項目 PASS、`delivery/SELF-VERIFICATION-v5.7.0.md`
- Council 諮問: なし（11 論点全て対話で合意）

### 非破壊変更（破壊項目なし、後方互換完全維持）

| 項目 | 内容 | 影響種別 |
|---|---|---|
| autonomous-drive 入口側本格稼働 | crosscut-issue-implementer skill 全面改訂 + `.github/workflows/issue-pickup.yml` 新設 + template 配置 | opt-in 新機能（dev_mode `autonomous` + `autonomous_scope: full` 選択時のみ） |
| Issue 選別 3 段階フィルター | label opt-in / author allowlist / 本文必須項目 / current_focus 整合 / AI triage | 非破壊（既存 issue-implementer は claude-code-action 前提だったが未稼働、本改訂で実機構化） |
| current_focus 軸新設 | REGIME.md フィールド追加 + spec-architect 4 ファイル拡張 | 非破壊（既存 REGIME.md には影響なし、新規プロジェクト追加 + 既存も任意更新） |
| gemini-cli 実装エージェント化 | 既存 GEMINI_API_KEY 流用、Anthropic API 回避 | 新規（追加コスト 0、ただし未踏領域、観測駆動で品質判断） |
| Circuit Breaker | 日次 5 / 月次 50 Issue 上限、上限到達で workflow 全停止 | 新規（暴走防止、philosophy 第 7 条 P4 機構） |
| 履歴記録 | CHANGELOG / INTENT / REGIME-LOG / ARCH-DECISIONS (AD-026/027/028) に記録 | 非破壊 |
| 同梱 housekeeping | v5.6.0 (in progress) → (released 2026-05-03) 化（6 例目正規適用） | 非破壊 |
| バージョン | v5.6.0 → v5.7.0（minor 昇格）。新機能追加 + autonomous-drive 完成形 | — |

破壊項目なし。利用者プロジェクトには配布されない（v5.0.0〜v5.6.0 と同パターン）。`templates/github-workflows/issue-pickup.yml.template` は配布候補だが、deploy は spec-architect 対話で明示確認後のみ。

### dev_mode 判定（変更あり）

dialog-harness 本体: `dev_mode: github_assisted` のまま据え置き（autonomous-drive deploy せず、本 minor は他プロジェクトへの展開機構整備）。本 minor で **dialog-harness 自身に issue-pickup.yml をデプロイ**するため、merge 後は実質 `autonomous` 相当に昇格する（次 v5.7.x 開発から Issue 起点ループ稼働）。dev_mode の formal な昇格は v5.7.x で REGIME.md 改訂により実施判断。

### Council 諮問の有無

本 minor は Council 諮問なしで実施（11 論点全て対話で合意、起動条件未満）。理由: (a) 複数案拮抗なし（gemini-cli 採用は実装方式の素直選択、API 回避要望から決定）、(b) 実装者 confidence ≥ 0.6（β 止揚相当の選択肢が明確）、(c) `crosscut-council` 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当しない。**ただし実装中に gemini-cli 品質懸念が顕在化した場合は autonomous-dev が独自 Council 起動可**（adrv01-Ph1 自己申告プロトコル経由）。

## v5.6.0（minor 昇格、後方互換維持）

- 判定日: 2026-05-03
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer0-spec-architect（本セッションで起動）→ crosscut-council 諮問（`council-2026-05-03T08:30:00Z-adrv02`、β 止揚で `agreed_with_modification`）→ layer1-autonomous-dev で実装
- 起源: ユーザー（ひでさん）の明示要請「自律駆動を L0 に記録、メタスキル開発」+ DH AI 組織論の宣言（4 役割属性 + サポート構造）
- L0 譲渡: `delivery/HANDOFF-v5.6.0-autonomous-drive.md`
- 自己検証: `harness-verifier/verify.py` 全項目 PASS、`delivery/SELF-VERIFICATION-v5.6.0.md`

### 非破壊変更（破壊項目なし、後方互換完全維持）

| 項目 | 内容 | 影響種別 |
|---|---|---|
| philosophy.md 第 7 条新設 | AI 組織論（4 役割 + サポート + Person 責務 P1-P4）を既存 6 条と並列に追加。既存条改訂なし | 非破壊（新規追加のみ） |
| autonomous-drive 標準化 | `templates/github-workflows/` 新設 + `crosscut-autonomous-drive` skill 新設（β 止揚採用、deployment 専念） | opt-in 新機能（dev_mode autonomous 選択時のみ） |
| dev_mode `autonomous` 本格定義 | v5.0.0 で列挙のみだった `autonomous` を `autonomous_scope`（full / merge_gated / custom）軸で本格定義 | 非破壊（既存 dev_mode 値は不変） |
| spec-architect 改修 | dialog-questions / regime-assessment / dev-env-spec / meta-spec-template に Level C / autonomous_scope 質問・テンプレ追加 | 非破壊（既存対話フロー不変、新規プロジェクトでのみ追加質問発生） |
| 履歴記録 | CHANGELOG / INTENT / REGIME-LOG（本ファイル）/ ARCH-DECISIONS（AD-023/024/025）/ COUNCIL-LOG（adrv02）に記録 | 非破壊 |
| 同梱 housekeeping | v5.5.3 (in progress, target 2026-05-03) → (released 2026-05-03) 化を本 PR 同梱 | 非破壊（履歴記述の正規化のみ、5 例目正規適用） |
| バージョン | v5.5.3 → v5.6.0（minor 昇格）。philosophy 第 7 条新設 + 利用者プロジェクト展開機構の追加で minor 相当 | — |

破壊項目なし。利用者プロジェクトには配布されない（v5.0.0〜v5.5.3 と同パターン）。autonomous-drive deployment は利用者プロジェクトに配布する template であって、`crosscut-autonomous-drive` skill 自体は D4 マスタ skill に留まる。

### Council 諮問の有無

本 minor は Council 諮問あり：`council-2026-05-03T08:30:00Z-adrv02`（skill 新設の可否、judgment カテゴリ、business 種別、`agreed_with_modification`）。F2 観測駆動原則の緩和判断（v5.5.3 AD-022 の「数 PR 試運用後判断」を 1 例のみで標準化要請へ移行）は実装者裁量で進行（複数案拮抗ではなく、メタスキル開発の優先度判断、Council 起動条件未満）。philosophy.md 第 7 条新設の HANDOFF H1-H4 ラベル衝突解消（→ P1-P4 リネーム）も実装者裁量で進行（confidence 0.7、明確な解あり、Council 起動の閾値未満）。

### dev_mode 判定（変更あり）

REGIME.md の `dev_mode` は `github_assisted` のまま据え置き（dialog-harness 本体の運用は v5.5.3 まで通り）。本 minor は **「他プロジェクトが dev_mode `autonomous` を選択可能にする」標準化** であり、DH 本体自身を `autonomous` に引き上げるものではない。`autonomous_scope` 軸は dev_mode `autonomous` 選択時にのみ意味を持つ。



## v5.5.3（patch、no minor bump）

- 判定日: 2026-05-03
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer1-autonomous-dev（M2 体制、人間ひでさん指示で起動）
- 起源: ユーザー要請「自律駆動できるようにしたい、issue の自動取得で GO サインがある issue だけを対象に」を起点に、autonomous-drive 機構の出口側（auto-merge）を実装するパス A 採用判断
- 自己検証: `harness-verifier/verify.py` 全項目 PASS
- 後方互換: 完全維持（label opt-in、label なき PR は従来通り手動 merge）

### 変更項目（opt-in 新機能 1 件 + 非破壊変更）

| 項目 | 内容 | 影響種別 |
|---|---|---|
| `.github/workflows/auto-merge.yml` 新設 | label `auto-merge` 付き PR を多層検証通過後に squash merge する workflow（160 line） | **opt-in 新機能**（label なし PR は影響なし、後方互換完全維持） |
| 履歴記録 | CHANGELOG / INTENT / REGIME-LOG / ARCH-DECISIONS に v5.5.3 + AD-022 追加 | 非破壊（明文化のみ） |
| v5.5.2 housekeeping | 前 PR #41 merge 後の `(in progress)` → `(released)` 化を同梱（独立 PR 不要化） | 非破壊（履歴記述の正規化のみ） |
| バージョン | 据え置き → v5.5.3（patch のみ昇格）。新機能だが opt-in 完全後方互換、minor 昇格不要 | — |

利用者プロジェクトには配布されない（v5.0.0〜v5.5.2 と同パターン）。

### dev_mode 判定（変更なし）

REGIME.md の `dev_mode` は `github_assisted` のまま。本 patch は出口側自動化のみで、issue 作成 → AI 実装 → auto-merge のフル自動化（パス B）は v5.6.0 候補として温存。観測駆動原則に従い数 PR 試運用 → 問題なければ L0 spec-architect 経由で `autonomous` へ昇格判断する。

### Council 諮問の有無

本 patch は Council 諮問なしで実施（AD-022 §根拠参照）。理由: (a) ユーザー（人間）からの明示要請（パス A 承認）、(b) 後方互換完全維持（opt-in 設計）、(c) 実装者 confidence ≥ 0.6（複数案拮抗なし、パス A/B 選択は人間判断で確定）、(d) `crosscut-council` 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当しない。

## v5.5.2（patch、no minor bump）

- 判定日: 2026-05-03
- AI 能力バージョン: claude-opus-4-7（1M context）
- 改修主体: layer1-autonomous-dev（M2 体制、人間ひでさん指示で起動）
- 起源: v5.5.1 PR #40 で gemini-review 動作確立に伴い導入された診断機構（`continue-on-error: true` / `GEMINI_DEBUG: "true"` / Diagnostics 2 step）の縮退。並行して `continue-on-error` 削除の副作用として PAT 未設定環境で job hard-fail する事象を防ぐため `GH_REVIEW_PAT` availability check を新設
- 自己検証: `harness-verifier/verify.py` 全項目 PASS
- 後方互換: 機能ロジックは不変。**ただし `continue-on-error: true` 削除は observable な operational behavior 変更**（transient Gemini/MCP failure が silent success → hard-fail (red CI) に変わる、Copilot review #41 line 12 で指摘 → 意図的設計判断として明文化）

### 変更項目（operational behavior 変更 1 件 + 非破壊変更）

| 項目 | 内容 | 影響種別 |
|---|---|---|
| `continue-on-error` 削除 | `Run Gemini PR review` の soft-fail 設定を削除。transient Gemini/MCP failure が以前の silent success → 本 patch 以降は **hard-fail (red CI)** | **operational 変更**（意図的、philosophy.md §3 情報純度の系） |
| `GH_REVIEW_PAT` availability check 新設 | 上記副作用対策。PAT 未設定なら GEMINI_API_KEY 不在時と同様に notice 出力でクリーン skip | 非破壊（Robustness 強化） |
| Diagnostics step 削除 | `Diagnostics — runner / docker / GitHub MCP server reachability` + `Diagnostics — gemini_review step outcome` の 2 step（v5.5.1 PR #40 で診断目的で追加、役目完遂） | 非破壊 |
| `GEMINI_DEBUG` 削除 | env 削除（debug log は token 消費過多、必要時のみ手動 enable） | 非破壊 |
| `id: gemini_review` 削除 | post-step が消えたため不要 | 非破壊 |
| Prompt self-PR fallback 方式 | v5.5.1 と同様「APPROVE/COMMENT/REQUEST_CHANGES 全選択肢、self-PR API 拒否時に COMMENT fallback」を維持。v5.5.2 草案でハードコード化を試みたが Copilot review #41 line 184 で指摘 → revert | 非破壊（草案を撤回） |
| Settings JSON コメント | `includeTools` 不在の security trade-off を明文化、v5.5.x 候補として絞り込み再検討を記録 | 非破壊（明文化のみ） |
| Artifact upload | 保持（将来 debug 用、low cost） | 非破壊 |
| バージョン | 据え置き → v5.5.2（patch のみ昇格）。operational 変更は minor 昇格相当ではない（fail の可視化は新機能追加ではなく既存機能の正常化と位置づける） | — |

利用者プロジェクトには配布されない（v5.0.0〜v5.5.1 と同パターン）。

### Council 諮問の有無

本 patch は Council 諮問なしで実施（AD-021 §根拠参照）。理由: (a) v5.5.1 PR #40 で診断機構は明示的に「役目完遂後縮退」前提で導入された、(b) 本 patch は明確な仕様（v5.5.1 末で「diagnostics 縮退は別 PR で実施」と CHANGELOG に予告済）の素直実装、(c) 実装者 confidence ≥ 0.6（複数案拮抗なし）、(d) `crosscut-council` 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当しない。

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
| 先行宣言 4 本実装 | `layer0-archeo-architect/references/handoff-to-evaluator.md` の **4 箇所**（ステータスヘッダ / ロードマップ表 / 実装ステータス記述 / 先行宣言 4 セクション本体）を本実装版へ拡充。射程外要素列挙 + 援用と全体採用の境界線 + L1/L2 禁止規約 + v6.0.0 昇格の観測トリガー + 整合性ガード を 5 サブセクションで明文化 |
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

---

## v5.16.0（2026-05-12 開発開始）

### L0 三兄弟スキルの DESIGN.md 対応マトリクス（v5.16.0 で均質化、AD-022）

v5.15.0 で layer0-spec-architect に DESIGN.md 生成機能を追加した時点では、L0 三兄弟（spec-architect / onboarding / archeo-architect）の対応が非対称だった。v5.16.0 でフラクタル原則に従い均質化する。

| スキル | DESIGN.md 対応 | 起動契機 | 関連 reference |
|---|---|---|---|
| **layer0-spec-architect** | ✅ 完全対応 (v5.15.0〜) | 新規 / 継続 / 振り返り。§3.6 で DG1〜DG4 対話 | `references/design-system-spec.md` / `assets/design-md-template.md` |
| **layer0-onboarding** | ✅ 完全対応 (v5.16.0〜) | harness 後付け onboarding 時。§4.5 で reverse-design ステップ（既存 src/ から逆抽出） | `references/reverse-design-protocol.md` |
| **layer0-archeo-architect** | ✅ 完全対応 (v5.16.0〜) | リファクタ前の意図復元時。Step 1 構造走査で `visual` Island を検出、Step 2 で視覚意図仮説を提示 | `assets/refactor-intent-map-template.md` の `island_type` / `design_md_impact` フィールド |

### 関連 AD

- AD-021: AI 駆動開発における PR 粒度の決定基準
- AD-022: L0 三兄弟スキルの DESIGN.md 対応マトリクス

### 改修体制

- Mode: M2 標準（S=中、U=低、R=低、N=低、単一ドメイン、L2 閾値未達）
- 体制: L0（spec-architect）→ Council（業務 3 ペルソナ）→ scope_lock 6 項目を 1 PR で実装
- AI 能力バージョン: claude-opus-4-7（v5.15.0 と同じ）
- PR 粒度方針: AD-021 採用、AI スペック依存型（人間刻みを廃止）

### Council 起動記録

- `council-2026-05-12T13:32:00Z-sspr01` — DH スキル群の共有可能化と参照整合性確立の方向性（A→C 改訂で合意）
- `council-2026-05-12T14:30:00Z-adpp01` — AI スペック依存の開発スピード方針（β 中核 + α/ε 条件統合で合意）

詳細は `history/COUNCIL-LOG.md` 参照。
