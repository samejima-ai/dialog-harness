# Placeholder 規約

`templates/github-workflows/` 配下の `*.template` ファイルで使用される placeholder 一覧と置換規約。

## Placeholder 一覧

| Placeholder | 説明 | 例 | 確定タイミング |
|---|---|---|---|
| `${ALLOWED_AUTHORS}` | auto-merge workflow が信頼する author の login 名（複数なら space 区切り） | `samejima-ai` / `alice bob carol` | spec-architect 対話で取得（dev_mode autonomous 確定後） |
| `${REPO_OWNER}` | リポジトリ所有者（user or organization） | `samejima-ai` | `git remote get-url origin` から自動抽出可能 |
| `${REPO_NAME}` | リポジトリ名 | `dialog-harness` | 同上 |
| `${VERIFIER_JOB_NAME}` | 構造的 verifier の job 名（auto-merge.yml の condition 4 で参照） | `verify`（dialog-harness 標準） | プロジェクト固有、対話で確認、デフォルト = `verify` |
| `${SCOPE_PATHS}` | gemini-review / claude-review / harness-verify が発火する paths（YAML リスト） | `- "src/**"\n- "tests/**"` | spec-architect 対話で取得 |
| `${PROJECT_REVIEW_AXES}` | このプロジェクトで特に重視するレビュー軸（claude-review OC prompt / gemini-review prompt に注入。Markdown 箇条書き、空可） | `- 未検証入力の検出\n- blocking I/O の禁止` | spec-architect「コードレビュアー認識合わせ」で SPEC/DONT から抽出（v5.26.0、ADR-001/002） |
| `${SENSITIVE_PATHS_REGEX}` | claude-review routine pre-gate でフル Council に値する sensitive 変更を判定する ERE | `(^\.github/)\|(^\.claude/)\|(SPEC)\|(DONT)\|(REGIME)` | spec-architect 認識合わせで取得（プロジェクト固有重要パス、v5.26.0） |

## 置換規約

- `${VAR}` 形式のみ使用（`$VAR` は使わない、誤解防止）
- 複数値は YAML or space 区切り（template 内で文脈に応じて指定）
- 未確定 placeholder が残る配置はエラー扱い（crosscut-autonomous-drive が deploy 前に検出）
- placeholder 名は SCREAMING_SNAKE_CASE 固定

## 拡張規約

- 新規 placeholder 追加は v5.6.x patch 範疇（互換破壊なし）
- 既存 placeholder 名の変更 / 削除は major 案件（template 利用プロジェクトの再 deploy 必須）

### Forward-compat 命名規約（v5.11.0 追加、ADR-001 関連 / v5.26.0 で `${PROJECT_REVIEW_AXES}` 実装済み）

`${PROJECT_REVIEW_AXES}` は ADR-001 で予約され、**v5.26.0 で claude-review/gemini-review template に実装**された
（ADR-002、G-001 解消）。新規 placeholder の命名は以下に準拠する:

- SCREAMING_SNAKE_CASE 固定（既定）
- ドメイン prefix を導入:
  - `PROJECT_*` — user project の SPEC.md / DONT.md / 固有 sensors 由来（spec-architect 対話で抽出）
  - `REPO_*` — git remote から自動抽出可能なメタ情報
  - `WORKFLOW_*` — workflow 内部固有（job 名・step 名等）
  - `VERIFIER_*` — verifier job 固有
  - `ALLOWED_*` — auto-merge 信頼境界（authors / paths 等）
  - `SCOPE_*` — gemini-review / harness-verify 等の発火範囲
- 既存 placeholder の prefix 不一致は許容（後方互換維持のため改名しない）
- 新規 placeholder は本規約に従う

詳細背景は `adr-001-axis-placeholder-reservation-v5.12.0.md`（同一 references ディレクトリ配下）を参照。

## 利用者プロジェクトでの上書き

deploy 後、placeholder 置換結果（実値）を利用者プロジェクトの `.github/workflows/` で直接編集することは妨げない。ただし変更は spec-architect 対話で確認した内容と乖離する場合があるため、`delivery/DELIVERY.md` の deployment 記録に「project-specific override」セクションを設ける運用を推奨。
