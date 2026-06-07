# COLD アーカイブ層（archive ≠ delete）

情報代謝サイクルの**排泄先（分解代謝 / catabolism）**。栄養（叡智）を抜かれた抜け殻の生ログを
ここへ移送する。**delete ではない** — retrievable に保ち、結晶側（罠/RL/INTENT 等）からの
逆引き source pointer で生ログまで遡れるようにする（metabolism-regime.md §5 不変条件2）。

## 規律

- **archive ≠ delete**: 作業集合（既定ロード）から外すだけ。消さない。可逆性・監査可能性への投資を破壊しない。
- **既定ロードしない**: COLD は購読量に**乗らない**（だからディスクは無制限に太ってよい＝北極星）。必要時に明示 retrieve のみ。
- **read-only（append-only アーカイブ）**: 移送後のファイルは編集しない。内容指紋（sha256）不一致は監査フラグ。
- **構造**: `history/archive/YYYY-MM/` に移送月でまとめる（history-layer-spec.md §archive＝COLD の素地を踏襲）。

## 逆引き source pointer 形式（結晶側に付す）

```
<!-- source: cold://2026-06/SELF-VERIFICATION-v5.0.0.md#L42-88 sha256:ab12… reduction=DH -->
```

## 現状

足回り整備①で**枠のみ**作成。実移送は本番 reindex（dry_run_remaining が 0 到達後・人間承認後）で行う。
現時点で移送済みファイルは無い（Dry-run 段階）。
