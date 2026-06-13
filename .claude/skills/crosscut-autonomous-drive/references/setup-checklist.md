# Setup Checklist

`crosscut-autonomous-drive` skill が deploy する autonomous-drive 機構の利用者プロジェクト側 setup 手順。

## 必須 Repository Secrets

| Secret 名 | 用途 | 取得元 | 必要権限 |
|---|---|---|---|
| `GH_REVIEW_PAT` | gemini-review が GitHub MCP server 経由で PR review を投稿、auto-merge.yml が PR を merge、issue-pickup.yml で Claude Code が commit/push | https://github.com/settings/personal-access-tokens で Fine-grained PAT 発行 | Repository access: 対象 repo / Permissions: **Contents: Read+Write**（v5.7.1〜、Claude Code commit 用）, Pull requests: Read+Write, **Issues: Read+Write**（v5.7.0〜、issue-pickup label 操作用）, Metadata: Read |
| `GEMINI_API_KEY` | gemini-review が Google Gemini API を呼び出して semantic レビューを実行 + issue-pickup の AI triage（v5.7.0〜）| https://aistudio.google.com/ で発行（無料 tier 可、課金カード不要） | API key 単独 |
| `CLAUDE_CODE_OAUTH_TOKEN` | issue-pickup.yml で Claude Code CLI が実装本体を実行（v5.7.1〜）+ **claude-review.yml の 4 フェーズ Council レビュー**（v5.26.0〜、anthropics/claude-code-action）| ローカル `claude setup-token` で発行（Anthropic Pro/Max サブスクリプションでログイン後） | OAuth token 単独、追加 API 課金なし |

**重要 (v5.7.1)**: issue-pickup.yml が deploy された場合、`CLAUDE_CODE_OAUTH_TOKEN` 必須。未設定だと workflow が `notice::skip` で実装を起動しない。詳細: `.claude/skills/crosscut-issue-implementer/references/setup-checklist.md`

**コードレビュアー認識合わせ (v5.26.0)**: spec-architect §コードレビュアー認識合わせで claude（単発 / tier 段階 Council）を選んだ場合のみ `claude-review.yml` を deploy する。必要 secrets は `CLAUDE_CODE_OAUTH_TOKEN` + `GH_REVIEW_PAT`（gemini と共用）。両方未設定なら claude-review はクリーンに skip。**tier 段階 Council** を選んだ場合は `.claude/agents/review-*.md`（8 個）も配備済みであること（crosscut-council skill が前提）。詳細: `layer0-spec-architect/references/autonomous-drive-deployment.md` §コードレビュアー認識合わせ

### placeholder 置換後の YAML 検証（v5.26.0 必須・claude-review OC #145 指摘）

複数行 placeholder（`${SCOPE_PATHS}` / `${PROJECT_REVIEW_AXES}`）のインデント崩れや `${SENSITIVE_PATHS_REGEX}` の
引用崩れは **silent に paths スコープ不一致 / prompt 品質劣化 / workflow 無効化** を招く。crosscut-autonomous-drive は
**配置前に必ず YAML 妥当性を検証**する:

```
python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1])); print('YAML OK')" .github/workflows/claude-review.yml
python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1])); print('YAML OK')" .github/workflows/gemini-review.yml
```

- 失敗時は配置を中止し、インデント規約（`placeholder-spec.md §インデント規約`）に従って置換値を修正する。
- `${SENSITIVE_PATHS_REGEX}` にシングルクォート `'` を含めない（bash single-quote 内注入のため。`placeholder-spec.md §bash 注入の安全規約`）。
  さらに **有効な ERE であり、かつ空文字にマッチしないこと**を deploy 側で確認する（`.*` や空交替 `||` 等
  空文字にマッチする式だと `grep -Eq` が常 true となり pre-gate が無効化＝全 PR がフル OC 化する）。
  grep の exit code で判定する（`--` で `-` 始まり pattern の option 誤認も防ぐ）:

  ```
  # printf '\n' = 空行 1 つを入力（"空文字列にマッチするか" を判定。printf '' は 0 行で常に exit 1 になり判定不能）。
  printf '\n' | grep -E -- "$SENSITIVE_PATHS_REGEX" >/dev/null 2>&1; rc=$?
  case $rc in
    0) echo "INVALID: 空文字列にマッチ＝pre-gate 無効化（regex が緩すぎる）" ;;
    1) echo "OK: 空文字列に非マッチ・ERE 有効" ;;
    2) echo "INVALID: ERE 構文エラー" ;;
  esac
  ```

- **`.github/reviews/` を user project の `.gitignore` に追加推奨**（二重防御）。claude-review OC は Channel A artifact を
  `.github/reviews/` に Write し Actions Artifacts として回収する設計で PR ブランチには commit しないが、
  ローカル実行等での誤 commit を防ぐ。

## 必須 GitHub Labels

v5.9.0 で opt-in→opt-out モデルに反転（`auto-merge` ラベル廃止）。`autonomous_scope` に応じて以下の **stop labels** + **ready-for-ai** を作成:

| Label | autonomous_scope | 役割 |
|---|---|---|
| `do-not-merge` | full のみ（必須）| auto-merge workflow を block する stop label（opt-out の主軸）|
| `human-review-needed` | full のみ（必須）| 人間レビュー要請を明示する stop label（do-not-merge と同等扱い）|
| `ready-for-ai` | 全 scope | crosscut-issue-implementer が picking up する Issue マーカー |

ラベルは GitHub UI（Settings → Labels → New label）で作成、または gh CLI で：

```
gh label create do-not-merge --color d73a4a --description "Block auto-merge (opt-out stop label)"
gh label create human-review-needed --color d73a4a --description "Request human review (opt-out stop label)"
gh label create ready-for-ai --color a2eeef --description "Issue ready for AI implementation"
```

境界 SPEC（不変仕様）は `references/auto-merge-boundary.md` を一次情報源とする。

## Branch Protection（任意）

auto-merge workflow は branch protection なしでも動作するが、追加 hardening として以下推奨:

- `master` / `main` への直接 push を禁止（PR 経由のみ）
- Required status checks: `verify`（harness-verify or 等価）
- Require linear history: 任意

## 動作確認手順

opt-out モデルでは「stop label が無く required checks が success」で自動 merge される。
動作確認は以下の 2 シナリオで実施:

### シナリオ A: 自動 merge 経路

1. 適当な軽量変更（例: README.md の typo 修正）で PR を作成
2. PR を ready-for-review に切替（draft でないことを確認）
3. **stop labels（`do-not-merge` / `human-review-needed`）を付与しない**
4. required checks（`verify` 等）が success で完了することを確認
5. workflow run の `evaluate` job が `success` で完了し、`::notice::` 出力で skip 理由が無いことを確認
6. PR が自動 merge され、branch が削除されることを確認

### シナリオ B: stop label による block

1. 別の軽量変更で PR を作成
2. PR に `do-not-merge`（または `human-review-needed`）label を付与
3. workflow run が **skip**（`::notice::stop label detected ...`）することを確認
4. label を外すと再度 evaluate が走り、merge 経路へ復帰することを確認

## 失敗時のチェック

- `evaluate` job が red → 通常はログに具体的な skip 理由が `::notice::` で出力される
- Secrets 未設定 → `::notice::GH_REVIEW_PAT 未設定...` で skip
- Author allowlist 外 → workflow の `env.ALLOWED_AUTHORS` を確認
- `verify` job 未走行 → harness-verify の paths filter を確認

## 暴走時の介入（Person 責務 P4）

- `do-not-merge` label を付与 → auto-merge workflow が block
- Repository Secrets から `GH_REVIEW_PAT` を一時削除 → workflow 全体が skip
- 緊急の場合: workflow file 自体を `disabled` 化（GitHub Actions 設定 or workflow `if:` 条件）

これらは **人間 P4 専管**。AI は notice/warning で兆候を提示するまで（philosophy.md 第 7 条）。
