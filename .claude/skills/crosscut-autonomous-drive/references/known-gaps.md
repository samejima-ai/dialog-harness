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
