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
status: open
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
status: open
```
