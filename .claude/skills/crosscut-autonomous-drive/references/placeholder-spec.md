# Placeholder 規約

`templates/github-workflows/` 配下の `*.template` ファイルで使用される placeholder 一覧と置換規約。

## Placeholder 一覧

| Placeholder | 説明 | 例 | 確定タイミング |
|---|---|---|---|
| `${ALLOWED_AUTHORS}` | auto-merge workflow が信頼する author の login 名（複数なら space 区切り） | `samejima-ai` / `alice bob carol` | spec-architect 対話で取得（dev_mode autonomous 確定後） |
| `${REPO_OWNER}` | リポジトリ所有者（user or organization） | `samejima-ai` | `git remote get-url origin` から自動抽出可能 |
| `${REPO_NAME}` | リポジトリ名 | `dialog-harness` | 同上 |
| `${VERIFIER_JOB_NAME}` | 構造的 verifier の job 名（auto-merge.yml の condition 4 で参照） | `verify`（dialog-harness 標準） | プロジェクト固有、対話で確認、デフォルト = `verify` |
| `${SCOPE_PATHS}` | gemini-review / harness-verify が発火する paths（YAML リスト） | `- "src/**"\n- "tests/**"` | spec-architect 対話で取得 |

## 置換規約

- `${VAR}` 形式のみ使用（`$VAR` は使わない、誤解防止）
- 複数値は YAML or space 区切り（template 内で文脈に応じて指定）
- 未確定 placeholder が残る配置はエラー扱い（crosscut-autonomous-drive が deploy 前に検出）
- placeholder 名は SCREAMING_SNAKE_CASE 固定

## 拡張規約

- 新規 placeholder 追加は v5.6.x patch 範疇（互換破壊なし）
- 既存 placeholder 名の変更 / 削除は major 案件（template 利用プロジェクトの再 deploy 必須）

## 利用者プロジェクトでの上書き

deploy 後、placeholder 置換結果（実値）を利用者プロジェクトの `.github/workflows/` で直接編集することは妨げない。ただし変更は spec-architect 対話で確認した内容と乖離する場合があるため、`delivery/DELIVERY.md` の deployment 記録に「project-specific override」セクションを設ける運用を推奨。
