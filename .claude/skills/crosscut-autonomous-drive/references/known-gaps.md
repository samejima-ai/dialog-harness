# 既知ギャップ表

`crosscut-autonomous-drive` 配下の workflow / template / placeholder 機構に関して認識している局所的な未解消ギャップを構造化記録する。各ギャップは「設計上の保留」として明示し、解消予定 minor または ADR を併記する。

記録なき先送りは哲学違反だが、明示記録された保留は構造的対称性の意図を保ったまま観測駆動原則と両立できる（council-2026-05-09T15:00:00Z-grtmpl 哲学者意見より）。

## 運用ルール

- 各エントリは一意の ID（`G-<3 桁番号>`）を持つ
- 解消時は `status: resolved` に更新し、解消 PR / commit を併記
- 新規ギャップは末尾に append（既存 ID は再利用しない）
- F1 振り返り儀式（週次）で棚卸し対象

## エントリスキーマ

```yaml
- id: G-XXX
  title: <短いタイトル>
  affected_files: [<ファイルパス>]
  detected_at: <ISO 8601 日時>
  detected_by: <検出契機: Council ID / 振り返り儀式 / 等>
  description: <ギャップの内容>
  scope: <局所違反 / 構造的不整合 / 等>
  resolution_planned: <minor 番号 / ADR 番号 / 未定>
  status: open | resolved
```

## ギャップ一覧

### G-001: gemini-review.yml.template prompt 軸の DH-specific 残存

```yaml
id: G-001
title: gemini-review.yml.template の prompt 軸（review の評価軸列挙）が user project に deploy された際 project-specific 化されない
affected_files:
  - templates/github-workflows/gemini-review.yml.template
detected_at: 2026-05-09T15:00:00Z
detected_by: council-2026-05-09T15:00:00Z-grtmpl
description: |
  gemini-review.yml.template の prompt 部分（philosophy 6 条 / Council 起動 /
  harness-verifier 整合 等の review 軸列挙）が DH-specific のまま固定されており、
  user project に deploy された際 project-specific 化されない。permalink ベース
  URL の hardcoded（${REPO_OWNER}/${REPO_NAME} 未適用部）も同種の局所違反。
  v5.11.0 の案 1 (placeholder 拡張) で permalink/repo 名側は解消するが、
  prompt 軸側（review の評価軸そのもの）は v5.12.0 の案 2 (軸 placeholder 化)
  まで DH-specific のまま残置する。
scope: 局所違反（PR #72「視点直交」原則の構造的対称性に対する）
resolution_planned: v5.12.0 の案 2 (軸 placeholder 化、`adr-001-axis-placeholder-reservation-v5.12.0.md` で予約)
resolved_at: 2026-06-13T01:00:00Z
resolved_by: v5.26.0（ADR-002）— `${PROJECT_REVIEW_AXES}` placeholder を gemini-review.yml.template / claude-review.yml.template に注入。spec-architect「コードレビュアー認識合わせ」が SPEC/DONT から重点軸を抽出。
residual: prompt 内の DH-specific *default* 軸列挙（philosophy 6 条等）は残置し、加算的に project 軸を注入する方式とした。default 文言のフル generic 化（案 2 完全形）は別案件として header 編集ガイドに委譲。
status: resolved
```

### G-002: gemini-review prompt と MCP includeTools の不整合（add_comment_to_pending_review）

```yaml
id: G-002
title: gemini-review.yml / .yml.template の prompt が `add_comment_to_pending_review` の不使用を明示する一方、MCP `includeTools` に当該 tool が残存
affected_files:
  - .github/workflows/gemini-review.yml
  - templates/github-workflows/gemini-review.yml.template
detected_at: 2026-05-09T14:30:00Z
detected_by: copilot-pull-request-reviewer (PR #73 review、line 320 / 318)
description: |
  gemini-review の prompt は単一 verdict body 方針（line comment 不使用）を採用しているが、
  MCP server 側の `includeTools` リストに `add_comment_to_pending_review` が残存しており、
  モデルが prompt 制約に反して line comment を打ち得る状態。方針を強制したいなら
  `includeTools` から該当 tool を外す、prompt 側の禁止を撤回する、いずれかで整合させる必要がある。
  PR #72 で導入された prompt 方針の整合性問題（局所違反）。本 PR (#73) のスコープ
  (Council 判定記録 + v5.11.0 SPEC 準備) を超えるため記録のみとし、実対応は別途検討する。
scope: 局所違反（prompt 仕様と実 tool 露出の整合性）
resolution_planned: 別 PR / Issue で対応（v5.11.0 minor 範疇、Council 諮問不要の素直対応）
resolved_at: 2026-06-14T00:00:00Z
resolved_by: |
  PR #153 で本体・template 両方の `includeTools` から `add_comment_to_pending_review` を削除。
  prompt の「line comment は使用しない（単一 verdict body に集約）」方針を tool 露出レベルで強制し、
  モデルが方針に反して line comment を打ち得る状態を解消。`pull_request_review_write`（verdict 投稿）は
  方針上必要なため残す。drift は IN_SYNC 維持。
residual: なし。
status: resolved
```

### G-003: 配備 workflow / agents の二真実源 drift（本体 ↔ template ↔ user project）

```yaml
id: G-003
title: DH 本体 workflow/agents と template/配備物の同期保証が CI にない（二真実源 drift）
affected_files:
  - .github/workflows/claude-review.yml
  - templates/github-workflows/claude-review.yml.template
  - templates/github-workflows/gemini-review.yml.template
  - .claude/agents/review-*.md
detected_at: 2026-06-13T01:00:00Z
detected_by: claude-review OC (PR #145 Council review、LOW 4/5 phil/ceo) + copilot
description: |
  v5.26.0 で claude-review を template 化したことで、DH 本体 `.github/workflows/claude-review.yml` と
  `templates/.../claude-review.yml.template` が二真実源になった（gemini-review/auto-merge も同種）。
  本体側を改修しても template に伝播する保証が CI にない。加えて `.claude/agents/review-*.md` は user project へ
  verbatim 配備されるため、DH 本体更新時に user project 側 agents/template の整合が静かに崩れる。
  併せて PR #145 で見送った 2 件の workflow hardening も、本体↔template を同期して直すべき項目として束ねる:
    (a) LOW 3: claude-review allowed_tools の `Bash(gh pr review:*)` が COMMENT-only ハードルールを構造的に
        強制できない（subcommand 制限 glob or wrapper 切り出し。引数順序の都合で単純 glob 化は要検証）。
    (b) LOW 6: pre-gate の `git diff --numstat | awk` が `set -euo pipefail` 下で巨大/rename PR の pipefail で
        落ち得る（`|| echo 0` fail-safe）。本体・template の同一箇所を同期修正する。
scope: 構造的不整合（二真実源の同期保証欠如）
resolution_planned: 未定（drift 検知 CI もしくは generator 化。本体側に version stamp ヘッダ + setup-checklist 照合手順の追加を検討。F1 振り返り儀式で棚卸し）
resolved_at: 2026-06-14T00:00:00Z
resolved_by: v6.0.1 — `scripts/check_template_sync.py` で drift 検知機構を設置（resolution_planned の「drift 検知」案を採用）。placeholder 正規化 + コメント/空行除去後の実質ロジック行をマルチセット比較し、本体↔template の片側のみに在る行を drift として exit 1 で検知。意図的非対称（DH 固有 harness-verify.yml / 配布専用 issue-quality-gate.yml.template）はペア除外。
residual: 検知機構の設置が G-003 のスコープ。**検知された実 drift の修正は G-004 へ分離**（auto-merge の CI ポーリング待機ロジック等が本体のみに存在）。(a) claude-review allowed_tools の glob 化、(b) pre-gate awk の pipefail fail-safe も G-004 で本体↔template 同期修正する。
status: resolved
```

### G-004: 本体 ↔ template の実 drift（G-003 検知機構が初回検出）

```yaml
id: G-004
title: check_template_sync.py が検出した本体↔template の実機能 drift（auto-merge 待機ロジック等）
affected_files:
  - .github/workflows/auto-merge.yml
  - templates/github-workflows/auto-merge.yml.template
  - .github/workflows/claude-review.yml
  - templates/github-workflows/claude-review.yml.template
  - .github/workflows/gemini-review.yml
  - templates/github-workflows/gemini-review.yml.template
  - .github/workflows/issue-pickup.yml
  - templates/github-workflows/issue-pickup.yml.template
detected_at: 2026-06-14T00:00:00Z
detected_by: scripts/check_template_sync.py 初回実行（G-003 解消で設置した検知機構）
description: |
  G-003 で設置した同期検証が、本体のみに存在し template に伝播していない実機能を検出:
    - auto-merge: 本体に CI ポーリング待機ロジック（POLL_MAX_WAIT=1500 / 25min 待機・
      pending check 検出後リトライ）が実装済みだが template に無い（実害大。配布先の
      auto-merge が check 完了を待たずに判定し得る）。
    - gemini-review: 本体にファイル注入の notice ログ等があるが template に無い。
    - claude-review / issue-pickup: 各数行の drift（要精査、一部は正規化漏れの偽陽性可能性）。
  これらは G-003 の resolution（検知機構設置）とは別作業。template 改変は配布先の
  再 deploy を要する（placeholder-spec.md: 既存挙動変更は major 寄り）ため、1 ファイルずつ
  本体↔template を慎重に突合して同期する。併せて G-003 residual の (a)(b) も本案件で対応。
scope: 構造的不整合（二真実源の実 drift。検知済・未修正）
resolution_planned: 別 PR で本体↔template を 1 ファイルずつ同期。`check_template_sync.py --verbose` を突合の起点にする。偽陽性（正規化漏れ）は同スクリプトの正規化規則を改善して切り分ける
resolved_at: 2026-06-14T00:00:00Z
resolved_by: |
  PR #153（Issue #149/#150/#151）で全 4 ペアを IN_SYNC まで同期:
    - auto-merge: 条件 3.5 の CI 完了ポーリングループ + timeout-minutes:30 + PR_FIELDS 変数化を
      template に伝播（配布バグ解消・Issue #125 race の配布先再現を止めた）。
    - gemini-review / issue-pickup: notice ログ・PR_BODY 文言を本体に揃えて同期。
    - claude-review (a) allowed_tools / (b) pre-gate awk pipefail: 本体↔template 完全一致を確認
      （IN_SYNC が glob 差・pipefail 差の不在を実証）。
  偽陽性の切り分けは check_template_sync.py の正規化改善で対応（末尾インラインコメント除去 #7・
  direct_prompt ブロックスカラ除外 #7）。併せて harness-verify.yml に CI gate を追加し、
  以降の drift は exit 1 で検知される（G-003 の CI 強制力も本 PR で達成）。
residual: なし（全 4 ペア IN_SYNC + CI gate 稼働）。
status: resolved
```
