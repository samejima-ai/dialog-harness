# REINDEX Dry-run 差分レポート — DH 本体（dog-fooding 初回）

> **これは Dry-run（提案のみ）。実結晶化・実 COLD 移送・ファイル削除は一切していない。**
> 本レポートは「何が叡智で何が抜け殻か」を提示するだけ。実行は人間（D5/Master）承認後の次サイクル。

| 項目 | 値 |
|---|---|
| モード | Reindex（Dry-run） |
| 還元先軸（軸A） | **DH 本体（D4）** — このリポジトリでのメタ開発 |
| 実行日 | 2026-05-31 |
| 対象 | `history/`（61 ファイル）+ `delivery/`（1 ファイル）＝計 62 ファイル |
| 実行主体 | layer0-reindex-librarian v0.1.0 |
| Council 批准 | `council-2026-05-31T00:00:00Z-mtbl01`（Dry-run 初期デフォルト） |
| 実移送 | **なし（提案のみ）** |

---

## 1. 購読量ベースライン（実測）

| 範囲 | 行数 | ファイル数 |
|---|---|---|
| `history/` トップ階層 | 10,277 | 28 |
| `history/` サブ（wave1-5 / deliveries / council-readable / project-derived-councils / refs-draft） | 6,856 | 33 |
| `delivery/` | 97 | 1 |
| **合計** | **17,230** | **62** |

現状、F1 振り返り儀式や文脈ロードがこの全体に触れると、毎サイクル最大 ~17k 行を購読する。これが「代謝天井」の実体。
（注: 本 PR で F1 入力は HOT + 関連 WARM に絞り COLD 既定除外へ変更済み。本 reindex はその tier 仕分けの初回適用。）

---

## 2. tier 仕分け提案（還元先 = DH）

### HOT（結晶層・常時ロード対象・**移送しない**）

既に密に結晶化済みの叡智。判断に効く現役 context。

| ファイル | 行 | 種別 |
|---|---|---|
| `INTENT.md` | 1,023 | WHY 層・現役 |
| `ARCH-DECISIONS.md` | 347 | ADR・現役 |
| `DIMENSIONS.md` | 340 | 5 次元論・確定叡智 |
| `DH-PHILOSOPHY-INSIGHTS.md` | 372 | 思想結晶 |
| `PHILOSOPHY-CHANGELOG.md` | 77 | 思想変遷・確定 |
| `PHILOSOPHY-NOTE-autonomy-with-guardrails-2026-05-11.md` | 164 | 直近設計根拠（WARM 寄り） |

### WARM（圧縮層・append-only 監査台帳・**移送しない / ただし全ロードしない**）

成長し続ける監査台帳。**ファイルごと archive はしない**（§5 不変条件2: COLD=archive≠delete・監査投資）。
だが購読量の主因でもあるため、**既定ロードは「SUMMARY + 直近 N 件」に絞る**（F1 §2 で実装済み）。

| ファイル | 行 | 既定ロード方針 |
|---|---|---|
| `COUNCIL-LOG.md` | 2,089 | 直近数件 + 要約のみ。全文は retrieve 時 |
| `CHANGELOG.md` | 1,374 | 直近 10 件 + 要約のみ |
| `REGIME-LOG.md` | 674 | 直近 5 件 + 要約のみ |

### COLD 候補（抜け殻・**archive 移送提案**・retrievable・delete しない）

過去サイクルの一回性 forensic。学習は既に HOT（CHANGELOG / 罠 / Council）へ結晶化済みの前提。
default-load から外すと購読量が大きく下がる。

**(a) 高確度（バージョン刻印の検証・献上・引き継ぎ forensic）— 2,584 行**

| 群 | ファイル | 行 |
|---|---|---|
| SELF-VERIFICATION | v5.0.0/v5.1.0/v5.2.0/v5.3.0/v5.5.0/v5.6.0/v5.7.0/v5.7.1（8 件） | 1,382 |
| VERIFICATION | `VERIFICATION.md` / `VERIFICATION-v5.2.0.md` | 496 |
| HANDOFF | v5.6.0/v5.7.0/v5.7.1（3 件） | 607 |
| L1-DELIVERY | `L1-DELIVERY-v5.3.0.md` | 99 |

**(b) 中確度（一回性の監査・調査・設計メモ）— 1,233 行 / 要人間確認**

`D4-AUDIT-2026-04-30`(270) / `SKILL-CREATOR-AUDIT-v5.0.0`(176) / `SKILL-CREATOR-AUDIT-v5.10.x`(201) / `ECC-SURVEY-2026-05-11`(221) / `self-gate-check-AD010`(219) / `L0-WF-DESIGN-2026-04-30`(146)

**(c) サブディレクトリ（wave 作業ログ等）— 5,145 行 / 要人間確認**

`wave1`(1,617) / `wave2`(618) / `wave3`(454) / `wave4`(319) / `wave5`(1,084) / `deliveries`(415) / `council-readable`(592) / `project-derived-councils`(46)

> (b)(c) は「独自補完しない」（§5-5）に従い**断定せず要確認**でフラグ。摂取選択基準 §3-5（沈黙した声の救済）に基づき、確認が取れるまで移送しない。

---

## 3. 購読量インパクト投影（Dry-run 計算）

| シナリオ | default-load 行（概算） | 削減率 |
|---|---|---|
| 現状（全 history） | 17,230 | — |
| (a) 高確度のみ COLD 移送 | 14,646 | **−15%** |
| (a)+(b) 移送 | 13,413 | **−22%** |
| (a)+(b)+(c) 全移送 + 台帳の SUMMARY 化 | 〜6,500（HOT+要約） | **〜−62%** |

COLD は archive に retrievable で残るのでディスクは減らない（北極星どおり：ディスク無制限・購読量を断つ）。

---

## 4. 結晶化候補（構築代謝）

DH 本体は罠/Council/INTENT が既に高度に結晶化済み（HANDOFF 前提）。本初回では**新規結晶化候補は最小**。
反復パターンとして観測（次サイクルで Council ゲート経由検討）:

- 「verify を通すために検証側所有物を編集してよいか」の判断が複数回出現 → **罠/RL 候補**: 「harness-verifier 所有物編集は D5 ゲート（独立性要請）」。ただし反復回数が `council_gate.repetition_threshold` 未達なら候補保留
- squash merge 後の未 rebase によるコンフリクト（本セッションで発生）→ **罠候補**: 「PR merge 後はブランチを rebase してから継続コミット」

> いずれも単発〜少数のため、HOT 昇格は Council ゲート（mtbl01 設計）を経るまで**候補のまま保留**。自動昇格しない。

---

## 5. 実行（本番昇格）時の手順案 — **承認後のみ**

1. `history/archive/2026-05/` を作成し、COLD 確定分を移送（**delete せず**）
2. 移送ファイルへ逆引き不要（元が forensic）だが、結晶側（CHANGELOG 等）に `<!-- source: cold://2026-05/... -->` を付与
3. `history/.metabolism-cursor.yml` をベースライン生成（各台帳の現末尾行 + プレフィックス checksum、`reduction_target: DH`、`dry_run_remaining` を REGIME 値から）
4. `history/SUMMARY.md` を新規生成（**現状 DH 本体に SUMMARY.md が無い** = HOT エントリポイント欠如。これが F1 の HOT ロードを効かせる鍵）

---

## 6. 検出された構造的ギャップ（要 Master 判断）

1. **DH 本体に `REGIME.md ## 情報代謝設定` が無い**（DH はフレームワーク本体で標準 REGIME.md を持たない）。本 Dry-run は framework デフォルト（token_budget 12000 等）で算定。DH 本体用の代謝パラメータをどこに正本化するか要決定
2. **`history/SUMMARY.md` 不在** = HOT 結晶エントリポイントが無い。F1 の購読量削減を実効化するには SUMMARY.md 生成が前提（**本 Dry-run の範囲外＝意図的に未生成**。生成は承認後の本番 reindex／次 PR で実施。§5 手順案 4 と相互参照）
3. (b)(c) の COLD 判定は人間確認待ち（独自補完しない）

---

## 結論

- 抜け殻の高確度分だけで **2,584 行（−15%）**、台帳の SUMMARY 化まで含めれば **〜−62%** の購読量削減余地を実測で確認
- **本レポートは提案のみ。ファイルは1つも移動・削除していない**
- 次アクション: Master が (b)(c) の COLD 判定と §6 ギャップ（SUMMARY 生成 / DH 用代謝パラメータ正本化）を承認 → 次サイクルで本番 reindex
