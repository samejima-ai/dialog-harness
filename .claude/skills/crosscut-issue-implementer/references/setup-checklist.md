# Setup Checklist

`crosscut-issue-implementer` を稼働させるための事前準備チェックリスト。dev_mode `autonomous` + `autonomous_scope: full` の利用者プロジェクトで実施する。

## 必須 Repository Secrets

| Secret 名 | 用途 | 取得元 | 必須 |
|---|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | 実装本体（Claude Code CLI、anthropics/claude-code-action）| Anthropic Console / Pro/Max サブスクリプション | ◎（v5.7.1〜）|
| `GEMINI_API_KEY` | AI triage（gemini-cli）+ PR レビュー（gemini-review.yml）| Google AI Studio | ◎ |
| `GH_REVIEW_PAT` | git push / PR 作成 / label 操作（GitHub Actions の標準 GITHUB_TOKEN では不足）| GitHub Settings → Developer settings → Personal access tokens (Fine-grained) | ◎ |

## CLAUDE_CODE_OAUTH_TOKEN 取得手順（v5.7.1 で追加）

### 前提

- Anthropic **Pro / Max サブスクリプション** が必要（無料プラン不可）
- API key 経路（`ANTHROPIC_API_KEY`）は v5.7.1 では使用しない（追加 API 課金が発生するため）
- サブスクリプション内で稼働するため**追加 API 課金なし**

### 取得手順

1. Claude Code CLI をローカル環境にインストール（Anthropic 公式ガイド参照）
2. `claude` コマンドで対話起動 → Pro/Max サブスクリプションでログイン
3. ターミナルで以下を実行：
   ```bash
   claude setup-token
   ```
4. 表示された OAuth token をコピー
5. GitHub リポジトリ → Settings → Secrets and variables → Actions → New repository secret
6. Name: `CLAUDE_CODE_OAUTH_TOKEN`、Value: コピーした token
7. 保存

### 確認

設定が完了したら、`ready-for-ai` label を test Issue に付与して `.github/workflows/issue-pickup.yml` を起動し、Pre-check ステップが「Required secrets not set: ...」notice を出さずに次ステップへ進むこと（実体は CLAUDE_CODE_OAUTH_TOKEN + GEMINI_API_KEY + GH_REVIEW_PAT の 3 secrets を `$GITHUB_OUTPUT` の `available=true` で確認）。

未設定時は `notice::Required secrets not set: <list>` で skip（red CI にしない、gemini-review.yml と同形式）。

## GEMINI_API_KEY 取得手順

1. Google AI Studio (`https://aistudio.google.com/`) にアクセス
2. 「Get API key」→ 新規作成
3. GitHub Secrets に `GEMINI_API_KEY` として登録

無料 tier（RPD 制限あり）で十分。triage 用途は軽量。

## GH_REVIEW_PAT 取得手順

1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Generate new token
3. Repository access: Only select repositories（対象 repo 選択）
4. Permissions:
   - **Contents**: Read and write（git push 用）
   - **Pull requests**: Read and write（PR 作成 + label 用）
   - **Issues**: Read and write（label 操作 + comment 用）
5. Generate → token をコピー → GitHub Secrets に `GH_REVIEW_PAT` として登録

## 必須 Labels

`autonomous-drive` deployment 時に `crosscut-autonomous-drive` skill が **基本 3 種**（`ready-for-ai` / `auto-merge` / `do-not-merge`）を自動作成する。残り **8 種**（`in-progress` / `pickup-failed` / `out-of-scope` / `focus-mismatch` / `needs-clarification` / `too-complex` / `circuit-broken` / `do-not-pickup`）は本 skill 稼働時に workflow が初回付与時に GitHub 標準動作で自動作成する（事前作成不要）か、手動でも作成可。

| Label 名 | 色 | 用途 | 作成主体 |
|---|---|---|---|
| `ready-for-ai` | green | Issue pickup 起動トリガー | crosscut-autonomous-drive deployment |
| `auto-merge` | green | autonomous_scope: full で自動付与、後段 auto-merge.yml が処理 | crosscut-autonomous-drive deployment |
| `do-not-merge` | red | 人間 block 用 | crosscut-autonomous-drive deployment |
| `in-progress` | yellow | pickup 中（issue-pickup.yml が自動付与） | issue-pickup.yml 初回付与 |
| `pickup-failed` | red | 実装失敗（人間 P4 判断要請） | issue-pickup.yml 失敗時 |
| `out-of-scope` | gray | triage skip 理由 | issue-pickup.yml triage |
| `focus-mismatch` | gray | triage skip 理由 | issue-pickup.yml triage |
| `needs-clarification` | gray | 二次フィルター skip 理由 | issue-pickup.yml filter |
| `too-complex` | gray | triage skip 理由（L2 級） | issue-pickup.yml triage |
| `circuit-broken` | red | Circuit Breaker 上限超過 | issue-pickup.yml CB |
| `do-not-pickup` | red | Issue pickup 永久 block 用 | 手動付与 |

### v5.7.1 時点の制約

- `crosscut-autonomous-drive/SKILL.md` および `references/setup-checklist.md` の deployment 仕様は **v5.7.0 までの 3 secrets (`GH_REVIEW_PAT` / `GEMINI_API_KEY`) + 3 labels** を前提に書かれている
- v5.7.1 で必要になった **CLAUDE_CODE_OAUTH_TOKEN** と本表の追加 8 labels への対応は **v5.7.x の課題**として継続管理（observation-driven、本 PR スコープ外）
- **暫定対応**: v5.7.1 では `crosscut-autonomous-drive` 経由の自動 deployment 後に、本 checklist を見て手動で `CLAUDE_CODE_OAUTH_TOKEN` を追加する運用とする

## 関連ドキュメント

- `../SKILL.md` — 本 skill 全体仕様
- `triage-protocol.md` — AI triage 詳細（gemini-cli 経路）
- `implement-protocol.md` — 実装本体プロトコル（v5.7.1 で Claude Code CLI 化）
- `circuit-breaker-spec.md` — 経済的暴走防止機構
- `issue-filter-spec.md` — 3 段階フィルター詳細
- `../../layer0-spec-architect/references/autonomous-drive-deployment.md` — deployment ガイド全体

## バージョン

- v0.1.0 (v5.7.1 で新設、Claude Code CLI 採用に伴う `CLAUDE_CODE_OAUTH_TOKEN` 取得手順を明文化)
