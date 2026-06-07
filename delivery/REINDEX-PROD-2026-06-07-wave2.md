# REINDEX 本番実行レポート — 第二弾 (b)+(c) COLD 移送（開発者ゲート適用）

> **本番（実移送）。archive ≠ delete（git mv・可逆・retrievable）。**
> 起動文脈: 人間「自律駆動で進めて / council≒人間合意」（philosophy 第6条 人間≒Council 原則）。
> Dry-run で「要人間確認」とした (b)(c) を **Council 合議（mtb2sc）で確定**し自律実行。

| 項目 | 値 |
|---|---|
| モード | Reindex（本番・排泄） |
| 還元先軸 | DH 本体（D4） |
| 実行日 | 2026-06-07 |
| 承認 | Council mtb2sc judgment ≒ 人間合意（第6条） |
| 実行主体 | layer0-reindex-librarian v0.1.0 |

## 1. Council 判定（mtb2sc）と開発者ゲート

3 ペルソナ（経4/開4/哲3）の収束 + **開発者ゲート（内容 grep で COUNCIL-LOG 結晶化を全件確認・未結晶ゼロのバッチのみ移送）**。
ゲートが実際に **未結晶の声**を捕捉した（「沈黙した声の救済」が機能）:

- `wave2-phaseB` に `w2qb04`、`wave3-phaseB` に `w3qb04` が **COUNCIL-LOG 未結晶** → wave2/wave3 を据え置き
- `refs-draft/ecc/instincts-design` のみ未結晶（他4件は skills から参照=live）→ **発酵層**
- `project-derived-councils` は利用者プロジェクト(D3)由来＝**管轄外で恒久除外**

## 2. 移送（5,260 行）

| 群 | 行 | 逆引き |
|---|---|---|
| (b) 中確度 6件 | 1,233 | ADR / CHANGELOG / skills |
| (c) `wave1/` `wave4/` `wave5/` `deliveries/` `council-readable/` | 4,027 | `COUNCIL-LOG.md`（w1qb/w5qb/rtkSHA 結晶化確認済み） |
| **計** | **5,260** | → `history/archive/2026-06/` |

## 3. 据え置き（理由つき）

| 対象 | 行 | 理由 |
|---|---|---|
| `wave2/` `wave3/` | 1,072 | 未結晶の Council 決定 `w2qb04`/`w3qb04` を含む。**吸収（結晶化）が先**。要再確認リストに登録。 |
| `refs-draft/ecc/` | 557 | 発酵層（`instincts-design` 未結晶 + live 参照4）。次サイクル再問予約。 |
| `project-derived-councils/` | 1,200 | 管轄外・恒久除外（還元先 project・他層の食料）。 |

## 4. 累積効果（第一弾＋第二弾）

| 範囲 | 行 |
|---|---|
| 代謝前 `history/`（top-level 10,403 + サブ 6,856） | 17,259 |
| 第一弾 COLD 移送（(a)） | −2,584 |
| 第二弾 COLD 移送（(b)+(c)） | −5,260 |
| **COLD 移送 累計** | **−7,844** |
| 移送後 `history/` top-level（HOT/WARM のみ） | **6,722 行** |

HOT エントリポイント `history/SUMMARY.md` 経由の既定ロードは、top-level の HOT/WARM（WARM は「直近 N 件＋要約」）に絞られ、
archive（7,844 行）+ 据え置き（2,829 行）は既定ロード対象外。**実効購読量は代謝前 17,259 行から HOT/WARM 中心へ収束**（dry-run 投影の 〜−62% 圏）。
COLD は `archive/` に retrievable で残る（北極星: ディスク無制限・購読量を断つ）。

## 5. 不変条件の遵守

- **archive ≠ delete**: `git mv`（26 rename・追跡維持・可逆）。
- **吸収→排泄の順序**: ゲートで未結晶（w2qb04/w3qb04/instincts-design）を検出し、吸収前の排泄を**停止**。
- **逆引き source pointer**: `archive/2026-06/MANIFEST.md` 第二弾節に明記。
- **他層の食料を排泄しない**: project-derived-councils（還元先 project）を恒久除外。
- **沈黙した声の救済**: 据え置き理由を SUMMARY に明示、未結晶決定と発酵層を**再訪予約**（緩慢な抹消の防止）。

## 6. 次

- **吸収（結晶化）**: `w2qb04` / `w3qb04` を COUNCIL-LOG へ結晶化 → 完了後 wave2/wave3 を移送可。
- **発酵層 再問**: `instincts-design` の結晶化/枯死を次サイクルで再判定。
