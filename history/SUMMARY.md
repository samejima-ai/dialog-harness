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

## COLD 候補（**未移送**・Dry-run 段階・既定ロード対象外にしたい抜け殻）

過去サイクルの一回性 forensic。学習は既に HOT へ結晶化済みの前提。本番 reindex（承認後）で `archive/` へ移送予定。

- **高確度（−2,584 行）**: `SELF-VERIFICATION-v5.*`（8件）/ `VERIFICATION*.md`（2件）/ `HANDOFF-v5.*`（3件）/ `L1-DELIVERY-v5.3.0.md`
- **中確度（要確認）**: `D4-AUDIT-*` / `SKILL-CREATOR-AUDIT-*`（2件）/ `ECC-SURVEY-*` / `self-gate-check-AD010` / `L0-WF-DESIGN-*`
- **サブ作業ログ（要確認）**: `wave1`〜`wave5` / `deliveries` / `council-readable` / `project-derived-councils` / `refs-draft`

## 要再確認リスト（摂取選択の可監査性 / metabolism-regime §3-3）

人間が「何を結晶化し何を COLD へ送るか」の摂取選択そのものを監査するためのリスト。**確度: AI 推定**。

- [ ] 結晶化候補（Council ゲート未達で保留）: 「harness-verifier 所有物編集は D5 ゲート（独立性要請）」/「PR merge 後はブランチを rebase してから継続コミット」 — `repetition_threshold` 到達まで保留
- [ ] COLD 中確度・サブ作業ログ（(b)(c)）の移送可否 — 「沈黙した声の救済」(§3-5) に従い、人間確認が取れるまで移送しない
- [ ] 本番昇格（dry_run_remaining: 3 → 0）の承認タイミング

## 関連

- Dry-run レポート: `../delivery/REINDEX-DRYRUN-2026-06-06.md`（最新）/ `2026-05-31.md`
- 正本定義: `../.claude/skills/layer0-reindex-librarian/references/metabolism-regime.md`
