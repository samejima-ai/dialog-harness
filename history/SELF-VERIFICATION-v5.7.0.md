# SELF-VERIFICATION v5.7.0

L0 spec-architect §7.4 自己検証 + harness-verifier 全 PASS + philosophy 第 7 条 P2 整合性確認。

## §7.4 自己検証チェックリスト

| # | 項目 | 結果 | 補足 |
|---|---|---|---|
| 1 | broken reference 検査 | ✅ PASS | harness-verifier §2 で 0 件検出 |
| 2 | scaffold smoke test | N/A | DH 自身は scaffold 対象外（メタスキル開発） |
| 3 | DONT 自己照合 | ✅ PASS | DH に DONT.md なし、philosophy 7 条との整合性は本ファイル §第 7 条整合性 で確認 |
| 4 | Pre-flight 充足 | ✅ PASS | HANDOFF 全文 + spec-architect SKILL.md + crosscut-issue-implementer SKILL.md + gemini-review.yml 構造を読了 |
| 5 | 受け入れ基準充足 | ✅ PASS | LC=2 既存プロジェクト + 新規追加機能なので段階適用、本要請は v5.7.0 新規追加部分にのみ適用 |

## harness-verifier 5 検査結果

| # | 検査項目 | 結果 | 検出件数 |
|---|---|---|---|
| 1 | frontmatter 整合性 | ✅ PASS | 0 |
| 2 | 参照 path 有効性 | ✅ PASS | 0 |
| 3 | SK 間参照の健全性 | ✅ PASS | 0 |
| 4 | 5 層構造保全 | ✅ PASS | 0 |
| 5 | 用語辞書整合 | ✅ PASS | 0（既存 glossary に新 skill / 新用語の追加不要、issue-implementer 改訂は frontmatter description のみ更新） |

## philosophy.md 第 7 条 P カテゴリとの整合性確認

### Person 責務 P1〜P4 と autonomous-drive 入口側の対応

| Person 責務 | v5.7.0 入口側での具体動作 |
|---|---|
| **P1 発案** (思考) | 新機能 / バグ修正のアイデア、AI 不可 |
| **P2 ブレスト** (発話) | AI と対話 → AI が Issue 作成 + label `ready-for-ai` 付与（人間は手を動かさない、philosophy 第 7 条「人間 = 頭と口、AI = 手」と整合） |
| **P3 事後確認・評価** (思考) | 自動 merge 完了後の振り返り、AI 不可 |
| **P4 暴走時介入** (発話) | `do-not-pickup` / `do-not-merge` label 付与、`circuit-broken` 解除、`ALLOWED_AUTHORS` 縮退、AI は notice/warning で兆候提示まで |

入口側（本 v5.7.0）+ 出口側（v5.5.3 + v5.6.0）で **P1〜P4 の 4 場面に人間関与が完全集約**。これは philosophy 第 4 条「人間がしないこと」+ 第 7 条「AI 組織論」の制度化完成。

### サポート skill としての位置づけ確認

- `crosscut-issue-implementer` skill は「サポート skill」枠（philosophy 第 7 条）
- 起動経路: workflow 経由で active 化（人間 P2 が label 付与 → workflow trigger）
- 献上経路: 失敗時は L0 spec-architect への Type C/D 献上（gemini-cli 品質懸念の場合）
- 4 役割（L0/L1/L2/Council）への補助的位置づけと整合

## 4 層検証 AND との連動（v5.5.3 から継承）

| 層 | 出口側 (v5.5.3〜v5.6.0) | 入口側 (v5.7.0) |
|---|---|---|
| 構造層 | harness-verify SUCCESS | issue-pickup の filter (二次: 本文必須項目) |
| 意味層 | gemini-review SUCCESS | issue-pickup の AI triage (gemini-cli) |
| 判断層 | reviewDecision != CHANGES_REQUESTED | issue-pickup の current_focus 整合 |
| 承認層 | label `auto-merge` + author allowlist | label `ready-for-ai` + author allowlist |

入口側 4 層検証 + 出口側 4 層検証 = **8 層 AND** で品質ガード。

## 配置成果物

### Phase A
- `history/CHANGELOG.md` v5.7.0 (in progress) + v5.6.0 (released 2026-05-03) 化
- `history/INTENT.md` v5.7.0 設計意図セクション
- `history/REGIME-LOG.md` v5.7.0 minor 昇格判定
- `history/ARCH-DECISIONS.md` AD-026/027/028

### Phase B
- `spec-architect/assets/meta-spec-template.md` REGIME.md テンプレに `## current_focus` セクション追加
- `spec-architect/references/regime-assessment.md` current_focus 判定（β 半自動 + γ フォールバック）追加
- `spec-architect/references/dialog-questions.md` current_focus 質問追加
- `spec-architect/references/dev-env-spec.md` Level C に current_focus と Issue pickup の連動表追加

### Phase C
- `crosscut-issue-implementer/SKILL.md` 全面改訂（claude-code-action → gemini-cli base）
- `crosscut-issue-implementer/references/issue-filter-spec.md` 新設（3 段階フィルター詳細）
- `crosscut-issue-implementer/references/triage-protocol.md` 新設（gemini-cli triage プロトコル）
- `crosscut-issue-implementer/references/circuit-breaker-spec.md` 新設（日次5/月次50）

### Phase D
- `.github/workflows/issue-pickup.yml` 新設（dialog-harness 自身に deploy、gemini-cli MVP）
- `templates/github-workflows/issue-pickup.yml.template` 新設（利用者展開用、placeholder 化）
- `spec-architect/references/autonomous-drive-deployment.md` に入口側 deployment 手順追記

### Phase E
- 本ファイル `delivery/SELF-VERIFICATION-v5.7.0.md`

## v5.7.0 MVP の境界（重要）

`.github/workflows/issue-pickup.yml` は **MVP（minimum viable product）** として実装：
- ✅ 完全実装: secrets check / circuit breaker / 一次・二次フィルター（label / author / 本文） / artifact upload
- ⚠️ MVP placeholder: 三次 AI triage (gemini-cli) / 実装本体（branch 作成 + gemini-cli 実装 + commit + PR）
- 📅 v5.7.x patch で完全実装予定: gemini-cli インストール + prompt template 整備 + 実装本体 + PR 作成

これは「観測駆動」原則と「gemini-cli を実装エージェントに使う未踏領域」への慎重対応：
- まず骨格を merge して filter 機構を稼働可能化（Issue label 付与で in-progress 自動化、人間に notice 通知）
- 実装本体の品質懸念は v5.7.x patch で実機運用しながら段階的に解消
- 失敗時は autonomous-dev が Council 起動可（adrv01-Ph1 自己申告）

## 既知の温存項目（v5.7.x patch 候補）

- gemini-cli 実装本体の MVP → 完全実装（branch 作成 + clone + 実装 + commit + PR 作成）
- AI triage の MVP → 完全実装（gemini-cli prompt + JSON parse + label 自動付与）
- Statistics 記録（merge commit による append-only 統計、Circuit Breaker の精度向上）
- 新 sub-skill `crosscut-issue-drafter`（ブレスト → Issue 化支援、philosophy 第 7 条 P2 強化）
- destructive change detector / circuit breaker の機能拡張（v5.6.0 から継続後送）
- ALLOWED_AUTHORS 動的化

## 結論

✅ **v5.7.0 implementation 完了 (MVP 範疇)、harness-verifier 全 PASS、philosophy 第 7 条 P カテゴリ整合性 PASS**。
本 PR を `auto-merge` label 付与で autonomous-drive loop 6 例目として投入する。

体制事後評価: M2 (LC=2) は妥当。L2 発動閾値には到達せず。philosophy.md 第 7 条 + autonomous-drive 機構（出口 + 入口）の制度化により、次サイクル以降は dev_mode `autonomous` + `autonomous_scope: full` を選択すれば「Issue → AI pickup → 実装 → 多層レビュー → 自動 merge → 次 Issue」のフル自律 loop が稼働可能（ただし v5.7.0 MVP の段階では実装本体は人間トリガーが必要、v5.7.x patch で完全自動化予定）。

副次目的: **dialog-harness 自身に issue-pickup.yml がデプロイされ、入口側機構が骨格レベルで稼働開始**。次の v5.7.x で実装本体を充実させれば、ユーザー指摘「対話 → Issue → 自動実装」のパターンが DH 自身で完全動作する。
