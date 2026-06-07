# history SUMMARY — HOT エントリポイント（DH 本体 / reduction_target: DH）

> 情報代謝の **HOT 結晶層への入口**。振り返り儀式・文脈ロードは、まず本ファイルを既定ロードし、
> `history/` 全体（〜17k 行）には触れない。これが購読量と history 蓄積量の線形連動（代謝天井）を断つ要。
> WARM 台帳は「直近 N 件＋要約」のみ、COLD は既定ロードしない（必要時に明示 retrieve）。
> 設定値は `history/.metabolism-config.yml`、消化カーソルは `history/.metabolism-cursor.yml`。

## HOT（結晶層・常時ロード対象・密な現役叡智）

| ファイル | 役割 |
|---|---|
| `INTENT.md` | WHY 層（設計意図の現役正本） |
| `ARCH-DECISIONS.md` | ADR（確定アーキテクチャ決定） |
| `DIMENSIONS.md` | 5 次元論（確定叡智） |
| `DH-PHILOSOPHY-INSIGHTS.md` / `PHILOSOPHY-CHANGELOG.md` | 思想結晶・変遷 |
| `PHILOSOPHY-NOTE-autonomy-with-guardrails-2026-05-11.md` | 直近設計根拠（WARM 寄り） |
| `../harness-verifier/PHILOSOPHY.md` | 6 条憲法（D4 正本） |

## WARM（append-only 監査台帳・既定は「直近 N 件＋要約」のみ・全文は retrieve 時）

| ファイル | 既定ロード方針 |
|---|---|
| `COUNCIL-LOG.md` | 直近数件＋要約のみ。全文は retrieve 時 |
| `CHANGELOG.md` | 直近 10 件＋要約のみ |
| `REGIME-LOG.md` | 直近 5 件＋要約のみ |

## COLD（情報代謝の排泄層・既定ロード対象外・retrievable）

> **除外の実現は convention レベル**: COLD を default-load から外す効果は、ハードな glob 規則ではなく
> 「本 SUMMARY を入口にし、COLD（`archive/`）を列挙しない」規律で実現される（代謝モデルは規律ベース）。
> ロード主体（振り返り儀式 F1 等）が本 SUMMARY を入口として尊重することが前提。glob 強制ではない。

### 移送済み

- **(a) 高確度（−2,584 行・移送済み 2026-06-07）**: `SELF-VERIFICATION-v5.*`（8件）/ `VERIFICATION*.md`（2件）/ `HANDOFF-v5.*`（3件）/ `L1-DELIVERY-v5.3.0.md` → **`archive/2026-06/`**。
- **(b)+(c) 第二弾（−5,260 行・移送済み 2026-06-07・Council mtb2sc・開発者ゲート適用）**: (b)中確度6件（`D4-AUDIT` / `SKILL-CREATOR-AUDIT`×2 / `ECC-SURVEY` / `self-gate-check-AD010` / `L0-WF-DESIGN`）+ (c)結晶化確認済み（`wave1/` `wave4/` `wave5/` `deliveries/` `council-readable/`）→ **`archive/2026-06/`**。逆引きは `archive/2026-06/MANIFEST.md`。
- **`wave2/` `wave3/`（−1,072 行・移送済み 2026-06-07・Council mtb2fu）**: 第二弾で hold 後、w2qb04/w3qb04 が「諮問省略＋結論 ship 済み（harness-verify.yml / templates/rituals/）」＝栄養抽出完了と再検証され hold 解除 → **`archive/2026-06/`**。

### 未移送・据え置き（理由つき）

- **`refs-draft/ecc/`（発酵層）**: 4件は skills から参照（live）、`instincts-design` のみ未結晶。COLD でも HOT 常駐でもない「発酵層」として次サイクル再問予約。
- **`project-derived-councils/`（管轄外・恒久除外）**: 利用者プロジェクト(D3)由来 Council ミラー＝還元先 project。DH-self(D4) 代謝の排泄対象ではない（他層の食料）。

> 注: `wave2/` `wave3/` は mtb2fu で移送済み（上記「移送済み」節）。w2qb04/w3qb04 の正体は「諮問省略＋結論 ship 済み」＝栄養抽出完了と判明し hold 解除。

## 要再確認リスト（摂取選択の可監査性 / metabolism-regime §3-3）

人間が「何を結晶化し何を COLD へ送るか」の摂取選択そのものを監査するためのリスト。**確度: AI 推定**。

- [ ] 結晶化候補（Council ゲート未達で保留）: 「harness-verifier 所有物編集は D5 ゲート（独立性要請）」/「PR merge 後はブランチを rebase してから継続コミット」 — `repetition_threshold` 到達まで保留
- [x] 本番 reindex 第一弾: (a) 高確度群を `archive/2026-06/` へ移送（2026-06-07・−15%）。詳細 `../delivery/REINDEX-PROD-2026-06-07.md`
- [x] 本番 reindex 第二弾: (b)+(c)結晶化確認済みを移送（2026-06-07・Council mtb2sc・−5,260行）。詳細 `../delivery/REINDEX-PROD-2026-06-07-wave2.md`
- [x] **w2qb04/w3qb04 再検証（mtb2fu）**: 正体は「諮問省略＋結論 ship 済み」と判明（沈黙した声ではない）。wave2/wave3 を移送済み。結晶化不要だった。
- [ ] **発酵層の再問**: `refs-draft/ecc/instincts-design` を次サイクルで「結晶化したか / 枯死か」再判定（緩慢な抹消を防ぐ再訪予約）

## 関連

- Dry-run レポート: `../delivery/REINDEX-DRYRUN-2026-06-06.md`（最新）/ `2026-05-31.md`
- 正本定義: `../.claude/skills/layer0-reindex-librarian/references/metabolism-regime.md`
