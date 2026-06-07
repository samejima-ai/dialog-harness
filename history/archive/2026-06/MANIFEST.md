# COLD 移送マニフェスト — 2026-06 / 本番 reindex 第一弾（(a) 高確度群）

**移送日**: 2026-06-07
**根拠**: `delivery/REINDEX-DRYRUN-2026-05-31.md` / `delivery/REINDEX-DRYRUN-2026-06-06.md`（2 サイクル連続で同一の (a) 高確度群を抜け殻と判定）
**承認**: Master の本番昇格承認（Dry-run デフォルト規律の人間オーバーライド）
**性質**: archive ≠ delete。retrievable・read-only・git 追跡維持。default-load から外す（購読量を断つ）。

## 移送したファイル（14 件 / 2,584 行 / −15% default-load）

過去サイクルの一回性 forensic（バージョン刻印の自己検証・献上・引き継ぎ記録）。
**学習・結論は既に HOT 側（`history/CHANGELOG.md` / `history/COUNCIL-LOG.md` / 罠）へ結晶化済み**であり、
本体はその抜け殻。逆引きが必要な場合は下記 retrieve 先から辿る。

| ファイル | 行 | 種別 | 結晶化先（逆引き先・retrieve はここ→本ファイル） |
|---|---|---|---|
| `SELF-VERIFICATION-v5.0.0.md` | 255 | 自己検証 | `CHANGELOG.md` v5.0.0 節 |
| `SELF-VERIFICATION-v5.1.0.md` | 178 | 自己検証 | `CHANGELOG.md` v5.1.0 節 |
| `SELF-VERIFICATION-v5.2.0.md` | 270 | 自己検証 | `CHANGELOG.md` v5.2.0 節 |
| `SELF-VERIFICATION-v5.3.0.md` | 154 | 自己検証 | `CHANGELOG.md` v5.3.0 節 |
| `SELF-VERIFICATION-v5.5.0.md` | 173 | 自己検証 | `CHANGELOG.md` v5.5.0 節 |
| `SELF-VERIFICATION-v5.6.0.md` | 118 | 自己検証 | `CHANGELOG.md` v5.6.0 節 |
| `SELF-VERIFICATION-v5.7.0.md` | 112 | 自己検証 | `CHANGELOG.md` v5.7.0 節 |
| `SELF-VERIFICATION-v5.7.1.md` | 122 | 自己検証 | `CHANGELOG.md` v5.7.1 節 |
| `VERIFICATION.md` | 165 | 独立検証 | `CHANGELOG.md` / `COUNCIL-LOG.md` |
| `VERIFICATION-v5.2.0.md` | 331 | 独立検証 | `CHANGELOG.md` v5.2.0 節 |
| `HANDOFF-v5.6.0-autonomous-drive.md` | 211 | 引き継ぎ | `CHANGELOG.md` v5.6.0 節 / `REGIME-LOG.md` |
| `HANDOFF-v5.7.0-issue-pickup.md` | 248 | 引き継ぎ | `CHANGELOG.md` v5.7.0 節 / `REGIME-LOG.md` |
| `HANDOFF-v5.7.1-claude-code-pivot.md` | 148 | 引き継ぎ | `CHANGELOG.md` v5.7.1 節 / `REGIME-LOG.md` |
| `L1-DELIVERY-v5.3.0.md` | 99 | 献上 | `CHANGELOG.md` v5.3.0 節 |

## 旧パス表記についての注意（retrievable 整合）

移送した各ファイルの**本文中に出てくる相対パス（`delivery/...` / `history/...` 等）は、作成当時の履歴表記**であり、
移送後の現行レイアウトとは一致しないことがある（read-only アーカイブなので本文は書き換えない）。
**現行の retrieve 起点は本 MANIFEST** とする。各ファイルへ辿る際は上表の「結晶化先（逆引き先）」列を正とし、
本文中の旧パスは当時のスナップショットとして読む。

## 規律

- **read-only**: 移送後は編集しない（append-only アーカイブ）。
- **retrievable**: 疑義が出たら本ディレクトリのファイルを明示 retrieve。default-load には戻さない（COLD→HOT 常時昇格の禁止）。
- **逆引き source pointer 形式**（結晶側に付す場合）: `<!-- source: cold://2026-06/<file>#Lxx-yy sha256:… reduction=DH -->`

## 据え置き（今回移送しない）

- **(b) 中確度** / **(c) サブ作業ログ**: Dry-run レポートで「要人間確認」フラグ。「沈黙した声の救済」(§3-5) に従い、確認が取れるまで移送しない。

---

# 第二弾 追記（2026-06-07・Council mtb2sc・開発者ゲート適用）

第二弾は (b) 中確度 + (c) 結晶化確認済みサブログを移送。**開発者ゲート（内容 grep で COUNCIL-LOG 結晶化を全件確認）**を通過した分のみ。

## 移送（5,260 行）

| 群 | 内容 | 結晶化先（逆引き） |
|---|---|---|
| (b) 中確度 6件 | `D4-AUDIT-2026-04-30` / `SKILL-CREATOR-AUDIT-v5.0.0` / `SKILL-CREATOR-AUDIT-v5.10.x` / `ECC-SURVEY-2026-05-11` / `self-gate-check-AD010` / `L0-WF-DESIGN-2026-04-30` | ADR / CHANGELOG / skills |
| `wave1/` | w1qb01-03 結晶化済み確認。CHEW/RITUAL/AUDIT/HANDOFF 等 forensic | `COUNCIL-LOG.md`（w1qb01-03 / metaskill 2件） |
| `wave4/` `wave5/` | w5qb02 結晶化済み確認。COMPLETION/RITUAL forensic | `COUNCIL-LOG.md`（w5qb02） |
| `deliveries/` | brainstorm 1件 | `CHANGELOG.md` |
| `council-readable/` | Council 可読レンダリング4件（rtkSHA 含め全件結晶化確認） | `COUNCIL-LOG.md` |

## 第二弾フォローアップ（mtb2fu・wave2/wave3 移送）

第二弾で hold した wave2/wave3 を再検証して移送（1,072 行）。`w2qb04`/`w3qb04` の正体は「諮問省略（confidence ≥ 0.7 で Council スキップ）」であり、結論は ship 済み（`w2qb04`→`.github/workflows/harness-verify.yml` / `w3qb04`→`templates/rituals/wave-end-retrospective.template.md`）と検証。他決定 `w2qb01-03`/`w3qb01-03` は COUNCIL-LOG 結晶化済み。→ 栄養抽出完了として hold 解除。

| 群 | 行 | 逆引き |
|---|---|---|
| `wave2/` | 618 | `COUNCIL-LOG.md`（w2qb01-03）/ ship: harness-verify.yml（w2qb04 諮問省略） |
| `wave3/` | 454 | `COUNCIL-LOG.md`（w3qb01-03）/ ship: templates/rituals/（w3qb04 諮問省略） |

## 据え置き（移送しない・理由つき）

| 対象 | 行 | 理由 |
|---|---|---|
| `refs-draft/ecc/` | 557 | 4件は skills から参照（live）、`instincts-design` のみ未結晶＝**発酵層**（次サイクル再問予約）。 |
| `project-derived-councils/` | 1,200 | **管轄外・恒久除外**。利用者プロジェクト(D3)由来 Council ミラー＝還元先 project。DH-self(D4) 代謝の排泄対象ではない（他層の食料）。 |
