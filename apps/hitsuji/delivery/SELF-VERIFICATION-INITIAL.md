# Self-Verification — Hitsuji 第 2 段階初期検証

L0 spec-architect が第 2 段階終了時に実施する §7.4 自己検証チェックリスト。

| 日付 | 検証者 | 結果 |
|---|---|---|
| 2026-05-19 | L0 spec-architect (Claude Opus 4.7) | **PASS（条件付き）** |

---

## §7.4 チェック項目

### A. 必須ファイル存在

- [x] `SPEC.md` 存在 + WHY/WHAT/条件/優先順位を含む
- [x] `DONT.md` 存在 + スコープ外明示
- [x] `REGIME.md` 存在 + Mode/dev_mode/ARC/NFR スコア記載
- [x] `DESIGN.md` 存在 + YAML フロントマター + 必須コンポーネント定義
- [x] `INDEX.md` 存在
- [x] `README.md` 存在 + クレジット
- [x] `CLAUDE.md` 存在 + プロジェクト固有 RL 明文化

### B. サブフェーズ成果物

- [x] `spec/subphase-manifest.md` — 起動判定ログ
- [x] `spec/state-diagrams.md` — 状態遷移 Mermaid
- [x] `spec/invariants.feature` — 不変条件（Happy 5 / Sad 5 / Evil 8 / 横断 3）
- [x] `delivery/ADR-001-subphase-scope.md` — 縮退判断 ADR

### C. センサー類

- [x] `sensors/computational.md` — 機械検証コマンド（Gradle / lint / test / coverage / 各種）
- [x] `sensors/inferential.md` — 5 層エラー検出スタック
- [x] `sensors/review-checklist.md` — A〜H 観点チェックリスト

### D. Android scaffold

- [x] `android/settings.gradle.kts`
- [x] `android/build.gradle.kts`
- [x] `android/gradle.properties`
- [x] `android/.gitignore`
- [x] `android/app/build.gradle.kts`
- [x] `android/app/src/main/AndroidManifest.xml`（5 必須パーミッション + Lv.4 系 + Boot 系）
- [x] `android/app/src/main/java/com/hitsuji/HitsujiApp.kt`
- [x] `android/app/src/main/java/com/hitsuji/MainActivity.kt`
- [x] `android/app/src/main/res/values/strings.xml` `themes.xml`
- [x] `android/README.md`

### E. SPEC ↔ 実装スキャフォールド整合

- [x] パーミッション宣言（Manifest）が SPEC.md の API 連携表と一致
  - `RECORD_AUDIO` ✓
  - `READ_CALENDAR` ✓
  - `POST_NOTIFICATIONS` ✓
  - `SCHEDULE_EXACT_ALARM` + `USE_EXACT_ALARM` ✓
  - `USE_FULL_SCREEN_INTENT` ✓
- [x] minSdk=26 / targetSdk=34 が CLAUDE.md の規定と一致
- [x] 依存ライブラリ（Compose / Hilt / Room / WorkManager / Coroutines）が CLAUDE.md の技術スタックと一致

### F. ドキュメント整合性

- [x] INDEX.md の参照が「生成済」と「第 2 段階予定」を区別している
- [x] SPEC.md 末尾の参照リストが「生成済」と「予定」を区別している（第 2 段階で全部生成済に更新する必要あり → 後述）
- [x] README.md にクレジットマーカーが保持されている
- [x] persona=sheep-navigator がコードに混入していない（grep 確認）

### G. DONT 違反検査（spec-architect 段階）

- [x] 広告 SDK 依存なし
- [x] ログイン / アカウント関連の placeholder なし
- [x] クラウド送信処理なし（Phase 1）
- [x] iOS / Flutter / RN コード混入なし

### H. dialog-harness 規範整合

- [x] REGIME.md が M2 / github_assisted / monolith / Claude Opus 4.7 を記載
- [x] LC=0 の新規プロジェクトとして適切
- [x] persona.active と override_state が REGIME.md に記録
- [x] 横断機構の state（inactive / on-demand / manual）が subphase-manifest.md に明記

---

## 検出された軽微な未完項目

### 1. SPEC.md 末尾参照リストの状態更新（pending）

第 1 段階の段階で「(未生成 / 第 2 段階予定)」マーカーを付けたが、第 2 段階で実際に生成完了したファイルがある。
→ **対応**: 第 2 段階完了後に SPEC.md の参照リストの状態マーカーを「生成済」に更新する（本コミットで実施）

### 2. Gradle wrapper の未配置

`gradlew` / `gradle/wrapper/gradle-wrapper.jar` は本 scaffold には含めていない（バイナリは git 経由配布が標準だが、L1 が `gradle wrapper --gradle-version 8.7` で初期化することを `android/README.md` に明記済み）。
→ **対応**: L1 が初回ビルド前に wrapper を初期化する。HANDOFF として android/README.md に記載済。

### 3. Compose Theme の DESIGN.md トークン適用

`MainActivity.kt` の `HitsujiTheme` は placeholder の `MaterialTheme` をラップするだけ。DESIGN.md のカラートークン適用は L1 の最初のタスク。
→ **対応**: L1 の初回 PR で `theme/Color.kt` `theme/Spacing.kt` `theme/Type.kt` を実装すべき旨を CLAUDE.md §8 に明記済。

---

## 総合判定

**PASS（条件付き）**

第 2 段階の成果物は全て揃い、SPEC ↔ scaffold ↔ sensors の整合は確保された。
上記の「軽微な未完項目」3 件は L1 の初回タスクスコープに引き継ぎ可能であり、第 2 段階完了の障害にならない。

### 次フェーズへの引き継ぎ

L1 autonomous-dev が起動する際の最初のタスク：

1. Gradle wrapper 初期化（`gradle wrapper --gradle-version 8.7`）
2. `theme/` パッケージで DESIGN.md トークンの Kotlin 実装
3. F1 タスク登録 + F5 手動登録（FAB → 入力 → 確定）の MVP 実装
4. F3 段階エスカレーション通知の Lv.1〜Lv.4 実装
5. F7 Room データベース + Repository 層
6. `invariants.feature` の Evil 系 8 シナリオを Repository 層 unit test に変換

L1 完了後は `layer1-independent-reviewer` が `sensors/review-checklist.md` A〜H 観点で独立検証する。

---

## 自己検証完了日時

2026-05-19 — L0 spec-architect (Claude Opus 4.7)
