# Hitsuji

ADHD 傾向のある人向け「コトの忘れもの」防止アテンションアプリ（Android Native）。

## Overview

注意欠損や多動的思考から「やること」「約束」を忘れてしまう ADHD 当事者向けの
アテンションアプリ。音声入力やカレンダー連携で**簡単に登録**でき、段階的に
強くなる**しつこい通知**で確実に思い出させる。完了するとスコアと連続日数で
**ゲーム感覚**に続けられる、ふんわり羊系の UX。

- **対象**: ADHD 傾向の本人（自分専用、シングルユーザー）
- **プラットフォーム**: Android（Kotlin + Jetpack Compose）
- **データ保管**: Phase 1 = 端末ローカル、Phase 2 = クラウド同期（将来）
- **入力**: 音声 primary + Google カレンダー + メッセージ取り込み + 手動 1 タップ
- **出力**: 統一プッシュ通知、段階的エスカレーション（やさしい→赤→アラーム）

## 主な機能

- F1. タスク（やること）の登録と通知
- F2. 予定（時刻系）の登録と通知
- F3. しつこい段階的エスカレーション通知（Lv.1〜Lv.4）
- F4. 自動取り込み（音声 / カレンダー / メッセージ / Gmail）
- F5. 手動登録（3 タップ以内、完全非同期）
- F6. ゲーミフィケーション（スコア + 連続日数 + バッジ）
- F7. データ保管フェーズ進化（ローカル → クラウド）

詳細は [`SPEC.md`](./SPEC.md) を参照。

## ドキュメント

- [`INDEX.md`](./INDEX.md) — 全体目次
- [`SPEC.md`](./SPEC.md) — 機能仕様
- [`DONT.md`](./DONT.md) — スコープ外定義
- [`REGIME.md`](./REGIME.md) — モード判定（M2 / github_assisted / monolith）
- [`DESIGN.md`](./DESIGN.md) — 視覚仕様

## 開発状況

- **Phase**: L0 仕様策定完了、L1 実装着手前
- **AI モード**: M2 標準モード（自律実装 + 独立検証）
- **GitHub 運用**: github_assisted（手動 merge）

---

Built with dialog-harness/layer's v5.17.0 · Claude Opus 4.7 · 2026-05-19

<!-- harness-credit: managed by layer0 skills. do not edit manually. -->
