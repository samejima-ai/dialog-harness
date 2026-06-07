# REINDEX 本番実行レポート — 第一弾 (a) 高確度群 COLD 移送

> **これは本番（実移送）。Dry-run ではない。** ただし archive ≠ delete のため可逆（git 追跡・retrievable）。

| 項目 | 値 |
|---|---|
| モード | Reindex（本番・分解代謝/排泄） |
| 還元先軸 | DH 本体（D4） |
| 実行日 | 2026-06-07 |
| 承認 | Master「進めて」= Dry-run デフォルト規律の人間オーバーライドによる本番昇格 |
| 対象 | (a) 高確度群のみ（(b)(c) は据え置き） |
| 実行主体 | layer0-reindex-librarian v0.1.0 |

## 1. 実行内容（摂取→咀嚼吸収→排泄の「排泄」フェーズ）

2 サイクル連続（2026-05-31 / 2026-06-06）の Dry-run で同一判定された (a) 高確度の抜け殻 **14 ファイル / 2,584 行** を
`history/archive/2026-06/` へ `git mv` で移送した。学習・結論は既に HOT（CHANGELOG / Council / 罠）へ結晶化済みであり、
本体は forensic な抜け殻。逆引きは `history/archive/2026-06/MANIFEST.md`。

| 群 | 件数 | 行 |
|---|---|---|
| SELF-VERIFICATION-v5.* | 8 | 1,382 |
| VERIFICATION*.md | 2 | 496 |
| HANDOFF-v5.* | 3 | 607 |
| L1-DELIVERY-v5.3.0.md | 1 | 99 |
| **計** | **14** | **2,584** |

## 2. 購読量インパクト

| 範囲 | 行 |
|---|---|
| 移送前 `history/` top-level | 10,403 |
| ① で追加（SUMMARY.md + COUNCIL-LOG mcfg01 追記） | +約 92 |
| (a) 群 COLD 移送 | **−2,584** |
| 移送後 `history/` top-level | **7,911** |

抜け殻の排泄による削減は **−2,584 行（≒ 移送前比 −15% / 北極星: default-load 購読量）**。

> **削減の実現は convention レベル**（独立レビュー指摘・正確性のため明記）: COLD を default-load から
> 外す効果はハードな glob 規則で強制されているのではなく、HOT エントリポイント `history/SUMMARY.md` を
> 入口にし COLD（`archive/`）を列挙しない規律で実現される。ロード主体（F1 振り返り儀式等）が SUMMARY を
> 入口として尊重することが前提。将来、glob ベースの強制除外を入れるかは別途検討（本 PR 範囲外）。

COLD は `archive/` に retrievable で残るためディスクは減らない（北極星どおり：ディスク無制限・購読量を断つ）。
HOT エントリポイント `history/SUMMARY.md` 経由のロードでは (a) 群は既定対象外。

## 3. 不変条件の遵守

- **archive ≠ delete**: `git mv` で移送（削除なし）。retrievable・git 追跡維持。
- **吸収→排泄の順序**: (a) の学習は既に CHANGELOG/Council へ結晶化済み（抜け殻のみ排泄）。
- **逆引き source pointer**: `archive/2026-06/MANIFEST.md` に各ファイル→結晶化先（CHANGELOG 該当節）を明記。
- **read-only**: 移送後アーカイブは編集しない。
- **独自補完しない**: (b)(c) は「要確認」フラグのまま据え置き（捏造で移送判定しない）。

## 4. 据え置き（本番第二弾の判断材料）

- **(b) 中確度（1,233 行）**: D4-AUDIT / SKILL-CREATOR-AUDIT ×2 / ECC-SURVEY / self-gate-check-AD010 / L0-WF-DESIGN
- **(c) サブ作業ログ（5,145 行）**: wave1〜5 / deliveries / council-readable / project-derived-councils / refs-draft

これらは「沈黙した声の救済」(§3-5) に従い、人間確認が取れるまで移送しない。確認できれば第二弾で最大 〜−62% まで到達可能。

## 結論

- **実際の軽量化を初めて実行**: default-load 購読量を −15%（−2,584 行）削減。
- **可逆**: archive≠delete。`git revert` または `git mv` 戻しで復元可能。
- 次アクション候補: (b)(c) の移送可否を Master が確認 → 本番第二弾。
