# ADR-001: gemini-review template の軸 placeholder 化を v5.12.0 で実施

## Status

Reserved（v5.12.0 で実装予定。v5.11.0 では案 1 のみ実施）

## Context

`templates/github-workflows/gemini-review.yml.template` の prompt 部分が user project に deploy された際 project-specific 化されないギャップ（`crosscut-autonomous-drive/references/known-gaps.md` G-001）の解消において、Council `council-2026-05-09T15:00:00Z-grtmpl` が以下を判定した:

- v5.11.0 では案 1 (placeholder 拡張、最小) を採用し、`${REPO_OWNER}/${REPO_NAME}` 自動置換と permalink ベース URL 自動置換を実装する
- 案 2 (軸 placeholder 化、中) は user project の SPEC 成熟度依存で実効値が読めないため、v5.11.0 では時期尚早と判断
- 段階分割として案 2 を v5.12.0 で実施する旨を ADR で予約する（本 ADR）
- 案 3 (generic skeleton 化) は philosophy 不改変制約下では D3/D4 境界明確化の魅力が半減するため不採用

判定 confidence: 0.62（auto_agree、unanimous on core）

## Decision

v5.12.0 で以下を実施する:

1. `${PROJECT_REVIEW_AXES}` placeholder を `templates/github-workflows/gemini-review.yml.template` に導入する
2. 軸抽出ロジックを `layer0-spec-architect/SKILL.md` の対話プロトコルに追加する
3. 軸生成ソースは user project の `SPEC.md` / `DONT.md` / 固有 sensors とする
4. `crosscut-autonomous-drive/SKILL.md` の deploy フローに軸抽出 step を追加する

軸抽出ロジックの設計は v5.12.0 開発時に user project の SPEC 成熟度を観測した上で確定する（観測駆動原則）。

## Consequences

- v5.11.0 出荷時点で gemini-review.yml.template の prompt 軸は DH-specific のまま残置する（既知ギャップ G-001 として明示記録）
- v5.12.0 開発時に user project の SPEC 成熟度を観測し、軸抽出ロジックが空文化しないことを確認する
- 案 1 (v5.11.0) の placeholder 命名規約は本 ADR を意識して forward-compat 設計とする（`crosscut-autonomous-drive/references/placeholder-spec.md` 拡張規約参照）
- 本 ADR の v5.12.0 実装予定が空文化した場合、F1 振り返り儀式で棚卸しし、再判断する

## References

- Council invocation: `council-2026-05-09T15:00:00Z-grtmpl`
- 既知ギャップ: G-001 in `.claude/skills/crosscut-autonomous-drive/references/known-gaps.md`
- 関連 PR: PR #72（「視点直交」原則の構造的対称性確立）

## Related decisions

- philosophy 不改変制約（第 7 条改修は v6.0.0 以降の major 案件として保留）
- opt-in 領域該当（`crosscut-autonomous-drive/references/auto-merge-boundary.md` §opt-in 領域: autonomous-drive workflow 自身の改修）
