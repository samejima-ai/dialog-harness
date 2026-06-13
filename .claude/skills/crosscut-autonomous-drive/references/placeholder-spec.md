# Placeholder 規約

`templates/github-workflows/` 配下の `*.template` ファイルで使用される placeholder 一覧と置換規約。

## Placeholder 一覧

| Placeholder | 説明 | 例 | 確定タイミング |
|---|---|---|---|
| `${ALLOWED_AUTHORS}` | auto-merge workflow が信頼する author の login 名（複数なら space 区切り） | `samejima-ai` / `alice bob carol` | spec-architect 対話で取得（dev_mode autonomous 確定後） |
| `${REPO_OWNER}` | リポジトリ所有者（user or organization） | `samejima-ai` | `git remote get-url origin` から自動抽出可能 |
| `${REPO_NAME}` | リポジトリ名 | `dialog-harness` | 同上 |
| `${VERIFIER_JOB_NAME}` | 構造的 verifier の job 名（auto-merge.yml の condition 4 で参照） | `verify`（dialog-harness 標準） | プロジェクト固有、対話で確認、デフォルト = `verify` |
| `${SCOPE_PATHS}` | gemini-review / claude-review / harness-verify が発火する paths（**複数行 YAML リスト**、要インデント注入） | 注入後イメージ:<br>`      - "src/**"`<br>`      - "tests/**"`（各行 6 スペース） | spec-architect 対話で取得 |
| `${PROJECT_REVIEW_AXES}` | このプロジェクトで特に重視するレビュー軸（claude-review OC prompt / gemini-review prompt の **block scalar 内**に注入。Markdown 箇条書き、**複数行・要インデント**、空可） | 注入後イメージ（各行 12 スペース）:<br>`            - 未検証入力の検出`<br>`            - blocking I/O の禁止` | spec-architect「コードレビュアー認識合わせ」で SPEC/DONT から抽出（v5.26.0、ADR-001/002） |
| `${SENSITIVE_PATHS_REGEX}` | claude-review routine pre-gate でフル Council に値する sensitive 変更を判定する ERE（**1 行**、bash single-quote 内に注入） | `(^\.github/)\|(^\.claude/)\|(SPEC)\|(DONT)\|(REGIME)` | spec-architect 認識合わせで取得（プロジェクト固有重要パス、v5.26.0） |

## 置換規約

- `${VAR}` 形式のみ使用（`$VAR` は使わない、誤解防止）
- 複数値は YAML or space 区切り（template 内で文脈に応じて指定）
- 未確定 placeholder が残る配置はエラー扱い（crosscut-autonomous-drive が deploy 前に検出）
- placeholder 名は SCREAMING_SNAKE_CASE 固定

### インデント規約（複数行 placeholder、v5.26.0 必須・Copilot #145 指摘）

複数行値を取る placeholder（`${SCOPE_PATHS}` / `${PROJECT_REVIEW_AXES}`）は **YAML の構造位置に依存する**ため、
置換実行者（crosscut-autonomous-drive を駆動する AI）は以下を**必ず**守る:

- **`${SCOPE_PATHS}`**: `on.pull_request.paths:` 直下に注入される。値の**各行を 6 スペースでインデント**する
  （`      - "src/**"`）。無インデント値を入れると YAML が壊れ workflow が無効化する。
- **`${PROJECT_REVIEW_AXES}`**: `direct_prompt: |`（claude）/ `prompt: |`（gemini）の **block scalar 内**、
  placeholder 行のインデント（**12 スペース**）に合わせて**各行を 12 スペースでインデント**する。
  **空のとき**は行を空にせず、正規化として 1 行 `- （重点軸の指定なし。汎用軸のみで評価）`（12 スペース込み）を注入する
  （prompt 上の空行ノイズ回避・意図明示。template 側に「未設定なら汎用軸のみ」と前置きがあるため意味は保たれる）。
  軸は **user project の SPEC/DONT 由来のみ**を入れ、template が既に列挙する汎用軸との**重複表現は除外**する（純度維持）。
- 一般則: **placeholder トークンが置かれている行頭のインデント幅を、注入値の全行頭に適用する**。
  上の例の「注入後イメージ」はインデント込みの最終形。単純な無インデント文字列をそのまま貼らない。
- 単一行 placeholder（`${ALLOWED_AUTHORS}` / `${REPO_NAME}` / `${VERIFIER_JOB_NAME}` / `${SENSITIVE_PATHS_REGEX}`）
  はインデント非依存（その場に 1 行で展開）。
- template 側コメント行ではトークン化（`${...}`）しない（複数行置換でコメントが分断され壊れるため）。
  実注入点のみ `${...}` を置く（claude-review/gemini-review template 冒頭コメント参照）。

### bash 注入の安全規約（`${SENSITIVE_PATHS_REGEX}`、v5.26.0・claude-review OC #145 指摘）

`${SENSITIVE_PATHS_REGEX}` は claude-review pre-gate で `SENSITIVE='${SENSITIVE_PATHS_REGEX}'`（**bash single-quote 内**）
に注入される。したがって:

- **値にシングルクォート `'` を含めない**（含むと bash 構文が壊れる）。paths 判定用 ERE は `^ . \ | ( ) /` 等で
  足り、`'` は不要。`'` が必要な要件が出たら placeholder 設計を見直す（現状は禁止が正）。
- ERE（grep -E）として有効な式のみ。空値禁止（pre-gate が常に何らかの sensitive 判定を持つ前提）。

### deploy 後の必須検証（v5.26.0）

placeholder 置換後、配置前に **必ず YAML 妥当性を検証**する（インデント崩れ・引用崩れの silent 失敗を防ぐ）:

```
python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1])); print('YAML OK')" .github/workflows/claude-review.yml
```

`${{ ... }}`（GitHub Actions 式）や `${LINES}` 等の shell 変数は placeholder ではない（置換対象外）。
検証で残存する `${SCREAMING_SNAKE}` のうち placeholder 一覧に載るものがあれば未置換エラー。手順は setup-checklist.md。

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
