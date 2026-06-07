# REINDEX Dry-run 差分レポート — DH 本体（2026-06-06・増分サイクル）

> **これは Dry-run（提案のみ）。実結晶化・実 COLD 移送・ファイル削除は一切していない。**
> 前回 `delivery/REINDEX-DRYRUN-2026-05-31.md` の提案は **未実行のまま有効**（cursor も archive も未生成＝本番未昇格）。
> 本レポートは冪等則に従い、前回提案を揺らさず **増分（WARM delta）だけ** を摂取して差分を提示する。

| 項目 | 値 |
|---|---|
| モード | Reindex（Dry-run・増分） |
| 還元先軸（軸A） | **DH 本体（D4）** — このリポジトリでのメタ開発 |
| 実行日 | 2026-06-06 |
| 前回 reindex | 2026-05-31（提案のみ・未実行） |
| 実行主体 | layer0-reindex-librarian v0.1.0 |
| 実移送 | **なし（提案のみ）** |

---

## 0. 冪等チェック（前回からの状態差）

cursor（`history/.metabolism-cursor.yml`）が無いため初回扱いだが、前回 Dry-run レポートが残っているので
それを基準に「前回末尾以降の増分」だけを読む（全 rescan 禁止・`reindex-protocol.md` §2「処理済みマーカー」の規律）。

| 範囲 | 前回(05-31) | 今回(06-06) | delta |
|---|---|---|---|
| `history/` top-level | 10,277 行 / 28 ファイル | **10,403 行 / 28 ファイル** | **+126 行** |
| `history/` サブ（wave1-5 等 9 ディレクトリ） | 6,856 行 | 6,856 行 | **±0** |
| 合計 (top+sub) | 17,133 | **17,259** | **+126** |

**増分の内訳（WARM delta・摂取済み）**:

| ファイル | delta | 中身 | 還元先 | 判定 |
|---|---|---|---|---|
| `COUNCIL-LOG.md` | +97 | Council 記録 2 件（`thry01` context-circulation-theory 仮結晶化批准 / `pc1f01` パターン結晶形式確定） | DH | **既に構造化済み台帳**。append のみ。新規結晶化候補なし |
| `CHANGELOG.md` | +29 | v5.x forensic 追記（independent-review 注記 / Copilot 最小権限 fix） | DH | forensic 台帳。COLD 寄りだが台帳は丸ごと archive しない |

→ **新規結晶化候補ゼロ・前回提案の変更なし＝冪等が成立**。増分は 2 つの append-only 台帳が伸びただけ。
これは regime が予測する病理そのもの（**購読量と history 蓄積量の線形連動＝代謝天井**）が 6 日で +126 行進行した実測。

---

## 1. tier 仕分け（前回から変更なし・再掲は要点のみ）

前回レポート §2 の仕分けをそのまま維持（揺らさない）。

- **HOT（移送しない・現役叡智）**: `INTENT.md` / `ARCH-DECISIONS.md` / `DIMENSIONS.md` / `DH-PHILOSOPHY-INSIGHTS.md` / `PHILOSOPHY-CHANGELOG.md` / `PHILOSOPHY-NOTE-...`
- **WARM（移送しない／全ロードしない・append-only 監査台帳）**: `COUNCIL-LOG.md`(2,186) / `CHANGELOG.md`(1,403) / `REGIME-LOG.md`(674) — 既定ロードは SUMMARY + 直近 N 件に絞る
- **COLD 候補(a) 高確度（−2,584 行）**: SELF-VERIFICATION ×8 / VERIFICATION ×2 / HANDOFF ×3 / L1-DELIVERY ×1 — バージョン刻印の一回性 forensic
- **COLD 候補(b) 中確度（−1,233 行・要確認）**: D4-AUDIT / SKILL-CREATOR-AUDIT ×2 / ECC-SURVEY / self-gate-check-AD010 / L0-WF-DESIGN
- **COLD 候補(c) サブ作業ログ（−5,145 行・要確認）**: wave1-5 / deliveries / council-readable / project-derived-councils / refs-draft

> (b)(c) は「独自補完しない」(§5-5) と「沈黙した声の救済」(§3-5) に従い **断定せず要確認** のまま。移送しない。

---

## 2. 購読量インパクト投影（前回と同一・実測ベース）

| シナリオ | default-load 行（概算） | 削減率 |
|---|---|---|
| 現状（全 history） | 17,259 | — |
| (a) 高確度のみ COLD 移送 | 14,675 | **−15%** |
| (a)+(b) 移送 | 13,442 | **−22%** |
| (a)+(b)+(c) 全移送 + 台帳 SUMMARY 化 | 〜6,500（HOT+要約） | **〜−62%** |

COLD は archive に retrievable で残る（北極星: ディスク無制限・購読量を断つ）。

---

## 3. 結晶化候補（構築代謝）

前回検出分から **新規追加なし**（増分は構造化済み Council/CHANGELOG 台帳のみで反復パターン未発生）。
前回フラグ済みの 2 件（harness-verifier 所有物編集の D5 ゲート / merge 後 rebase 罠）は引き続き
反復回数が `council_gate.repetition_threshold` 未達のため **候補保留**（自動昇格しない）。

---

## 4. 構造的ギャップ（前回から未解消・要 Master 判断）

本番（実移送）に進むには、前回 §6 のギャップが未解消のまま残っている:

1. **DH 本体に `REGIME.md ## 情報代謝設定` が無い** — token_budget / dry_run_cycles / council_gate 閾値の正本化先が未決
2. **`history/SUMMARY.md` 不在** — HOT 結晶エントリポイントが無く、購読量削減を実効化できない（生成は本番 reindex で）
3. **`history/.metabolism-cursor.yml` 不在** — 増分・冪等の起点が未設置（ベースライン生成は本番昇格時）
4. **`history/archive/`（COLD）不在** — 排泄先が無い

---

## 結論

- 前回 Dry-run（−15%〜−62% の削減余地）は **依然有効・未実行**。本サイクルで覆る所見なし＝冪等成立
- 6 日で台帳が **+126 行**増加し、代謝天井（購読量↔蓄積量の線形連動）が実測で進行中
- **ファイルは1つも移動・削除していない**
- 本番（実軽量化）に進むには §4 の 4 ギャップ（REGIME 代謝設定 / SUMMARY.md / cursor / archive）整備への Master 承認が必要
