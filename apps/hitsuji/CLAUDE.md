# Hitsuji — エージェント行動ルール（L1 向け RL）

L1 autonomous-dev、independent-reviewer、council が本プロジェクトで動作する際の**プロジェクト固有ルール**。
dialog-harness-layers の skill 本体ルールに加えて、本ファイルの内容を**優先**して従うこと。

---

## 1. プロジェクトコンテキスト

- **名称**: Hitsuji（ADHD 当事者向けアテンションアプリ）
- **プラットフォーム**: Android Native（Kotlin + Jetpack Compose）
- **対象ユーザー**: 開発者本人（単一ユーザー前提）
- **モード**: M2 / github_assisted / monolith / persona=sheep-navigator
- **LC**: 0（新規）

---

## 2. 仕様 SoT（Source of Truth）

実装判断で仕様情報が必要になったら、以下の順序で参照すること：

1. `SPEC.md` — 機能仕様（最優先）
2. `DONT.md` — スコープ外（**ここに該当する追加実装は禁止**、即献上で確認）
3. `DESIGN.md` — 視覚仕様（カラー / spacing / typography トークン）
4. `spec/state-diagrams.md` — 状態遷移
5. `spec/invariants.feature` — 不変条件（テスト変換対象）
6. `delivery/ADR-001-subphase-scope.md` — サブフェーズ縮退の根拠

仕様に書かれていない場合は **勝手に決めない**。即献上して人間に確認すること。

---

## 3. 技術スタック（必須）

| 要素 | 採用 | 備考 |
|---|---|---|
| 言語 | Kotlin 1.9+ | |
| UI | Jetpack Compose | XML レイアウトは使用しない |
| DI | Hilt | Dagger 直接利用は避ける |
| DB | Room 2.6+ | 直接 SQLite は使用しない |
| 非同期 | Kotlin Coroutines + Flow | RxJava 禁止 |
| ネットワーク | Retrofit + OkHttp（必要時のみ）| MVP では使用最小限 |
| ビルド | Gradle (Kotlin DSL) | Groovy DSL は使用しない |
| 最小 SDK | API 26 (Android 8.0) | エスカレーション機能の要請 |
| ターゲット SDK | API 34 (Android 14) | 最新パーミッション体系対応 |

**禁止スタック**：
- ❌ Flutter / React Native（DONT 1）
- ❌ Java（Kotlin のみ）
- ❌ XML レイアウト（Compose のみ）
- ❌ LiveData（Flow を使う）

---

## 4. ドメインモデル実装ルール

`SPEC.md` のドメインモデル擬似コードを Kotlin `data class` に起こす際：

```kotlin
// 例：Task entity
@Entity(tableName = "tasks")
data class Task(
    @PrimaryKey val id: String,                  // UUID 文字列
    val title: String,
    val description: String?,
    val type: TaskType,
    val scheduledAt: Instant,
    val recurrence: Recurrence?,
    val source: TaskSource,
    val escalationMax: EscalationLevel = EscalationLevel.LV4,
    val status: TaskStatus,
    val completedAt: Instant?,
    val scoreEarned: Int = 0,
    val createdAt: Instant,
    val updatedAt: Instant
)
```

**ルール**：
- すべての entity に `id (UUID)` と `updatedAt` を持たせる（Phase 2 移行対応）
- `Instant` を時刻型として統一（`Date` 禁止、`LocalDateTime` も避ける）
- enum は `kotlinx.serialization` 対応にしておく（永続化簡略化のため）
- nullable は意味のある場合のみ使う（`description?` は OK、`title?` は NG）

---

## 5. 通知エスカレーション実装ルール

F3 機能は本プロジェクトの**コア機能**。実装時の特別ルール：

1. **AlarmManager は `setExactAndAllowWhileIdle()`** を使う（Doze mode 越え）
2. **エスカレーション再発火は BroadcastReceiver + ForegroundService** で実装
3. **Lv.4 のフルスクリーンインテントは `NotificationCompat.Builder.setFullScreenIntent()` + `USE_FULL_SCREEN_INTENT` パーミッション**
4. **段階の単調性を Repository 層で enforce**（`invariants.feature` の Evil 系を実装で守る）
5. **端末再起動後の復元は `BootReceiver` で AlarmManager 再武装**

---

## 6. テスト戦略

| 層 | テスト種別 | フレームワーク | 必須度 |
|---|---|---|---|
| Domain (data class / enum) | unit | JUnit 5 + kotlin.test | 必須 |
| Repository (Room) | instrumented | androidx.test + Room in-memory | 必須 |
| ViewModel | unit | Coroutines Test + Turbine | 必須 |
| Compose UI | screenshot / interaction | Compose Test + Paparazzi | 推奨 |
| 不変条件 (invariants.feature) | BDD | kotlin-cucumber | 推奨（MVP では手動確認） |
| E2E | instrumented | Espresso | MVP では限定 |

**ルール**：
- 新規 entity / repository には**最低 1 つの unit test**を必ず書く
- `invariants.feature` の Evil 系シナリオは、**最低でも該当 Repository 層の unit test として実装**する
- `@Ignore` を付けたままコミットしない（理由を明記して別 issue 化）

---

## 7. パーミッション請求ルール

`SPEC.md` の「パーミッション請求 UX」セクションに従い、**段階的かつ目的説明付き**で請求する：

1. オンボーディング画面で目的説明
2. 機能を初めて使う時点で都度請求（事前一括請求しない）
3. 拒否時の機能縮退は SPEC に明記済み、それに従う

実装で迷ったら `SPEC.md` `## パーミッション請求 UX` を参照。

---

## 8. デザイントークン参照ルール

`DESIGN.md` の YAML フロントマターで定義されたトークンを必ず使う：

```kotlin
// ❌ NG（HEX 直書き）
Modifier.background(Color(0xFF5B8DEF))

// ✅ OK（トークン参照）
Modifier.background(MaterialTheme.colorScheme.primary)

// ❌ NG（px 直書き）
Modifier.padding(16.dp)  // 単発の数値ならまだ許容だが、

// ✅ より OK（spacing トークン）
Modifier.padding(Hitsuji.spacing.md)
```

実装時は `theme/Color.kt` `theme/Spacing.kt` `theme/Type.kt` に DESIGN.md の値をマッピングして、コード内では**トークン名で参照**すること。

---

## 9. 禁止事項（DONT.md より）

以下は**実装してはならない**。発見したら即献上：

- 広告 / 課金 / 他者比較ランキング
- 認証 / ログイン / アカウント機能（Phase 1）
- クラウド送信（Phase 1）
- iOS / デスクトップ版
- 物理物の位置追跡 / NFC / IoT 連携
- キャラ常駐 / アバターカスタマイズ
- 不要な確認ダイアログ
- ペナルティ / 減点 UI

---

## 10. 献上 / レビュー方針

### 献上タイミング

- 機能 1 つ完成ごと（F1〜F7 単位）
- SPEC.md に書かれていない判断が必要な時点で**即献上**
- `invariants.feature` の不変条件違反を検出した時点で**即献上**

### 献上物

- `delivery/DELIVERY-<feature>.md` — 何を作ったかのサマリ
- `delivery/HANDOFF-<feature>.md` — 次の作業引き継ぎ事項
- 該当 PR

### 独立検証（M2 必須）

L1 完了直後に `layer1-independent-reviewer` を起動：
- `SPEC.md` / `DONT.md` / `HANDOFF.md` との照合
- `sensors/computational.md` の機械検証実行
- `sensors/inferential.md` の 5 層エラー検出
- `sensors/review-checklist.md` の観点チェック

---

## 11. persona と応答スタイル

- `persona.active`: `sheep-navigator`
- 応答スタイル: ふんわり羊系（「〜なのん」「〜ですよぉ」等）、ただし**判断内容は default と同等の厳密性**
- コード内コメント、commit message、PR 本文、ADR 等の**仕様/技術ドキュメントは default スタイル**（羊スタイルは適用しない）

---

## 12. 横断機構の状態

| 機構 | 状態 | 起動条件 |
|---|---|---|
| crosscut-council | on-demand | 実装時に confidence < 0.6 / トレードオフ判断時 |
| crosscut-issue-dispatcher | manual | 人間が明示的に Issue 化を依頼した時のみ |
| crosscut-feedback-loop | manual | 人間献上経由のみ |
| その他 | inactive | REGIME.md 参照 |

---

## 13. 更新ルール

本 CLAUDE.md は **L0 spec-architect のみが更新権限**を持つ。L1 が更新を要する場合は spec-architect に差し戻すこと。
更新時は本ファイル末尾の更新ログに追記。

---

## 更新ログ

- 2026-05-19: 初版作成（L0 spec-architect、第 2 段階）
