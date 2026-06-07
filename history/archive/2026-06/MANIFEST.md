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

## 規律

- **read-only**: 移送後は編集しない（append-only アーカイブ）。
- **retrievable**: 疑義が出たら本ディレクトリのファイルを明示 retrieve。default-load には戻さない（COLD→HOT 常時昇格の禁止）。
- **逆引き source pointer 形式**（結晶側に付す場合）: `<!-- source: cold://2026-06/<file>#Lxx-yy sha256:… reduction=DH -->`

## 据え置き（今回移送しない）

- **(b) 中確度** / **(c) サブ作業ログ**: Dry-run レポートで「要人間確認」フラグ。「沈黙した声の救済」(§3-5) に従い、確認が取れるまで移送しない。
