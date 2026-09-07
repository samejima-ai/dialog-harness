# Hitsuji — Android Project Scaffold

L0 spec-architect が配置した Android プロジェクト骨組み。L1 autonomous-dev がここから本実装を進める。

## 構成（現時点）

```
android/
├── settings.gradle.kts        # ルート、:app モジュール宣言
├── build.gradle.kts           # プラグイン宣言（適用は :app で）
├── gradle.properties          # JVM 引数 + AndroidX 等
├── .gitignore
└── app/
    ├── build.gradle.kts       # Compose / Hilt / Room / WorkManager 依存
    └── src/main/
        ├── AndroidManifest.xml      # 5 必須パーミッション宣言
        ├── java/com/hitsuji/
        │   ├── HitsujiApp.kt        # @HiltAndroidApp placeholder
        │   └── MainActivity.kt      # Compose Activity placeholder
        └── res/values/
            ├── strings.xml          # app_name のみ
            └── themes.xml           # 最低限の theme
```

## L1 が次に追加する想定

```
app/src/main/java/com/hitsuji/
├── domain/
│   ├── Task.kt
│   ├── NotificationState.kt
│   ├── ScoreLedger.kt
│   ├── Streak.kt
│   └── enums/
├── data/
│   ├── db/
│   │   ├── HitsujiDatabase.kt
│   │   └── dao/
│   └── repository/
├── notification/
│   ├── EscalationReceiver.kt
│   ├── BootReceiver.kt
│   ├── EscalationForegroundService.kt
│   └── NotificationChannels.kt
├── feature/
│   ├── home/
│   ├── register/
│   ├── stats/
│   └── settings/
├── theme/
│   ├── Color.kt           # DESIGN.md トークンの実装
│   ├── Spacing.kt
│   └── Type.kt
└── di/
    └── AppModule.kt
```

## ビルド

```bash
cd apps/hitsuji/android
./gradlew assembleDebug
```

※ Gradle wrapper (`gradlew` / `gradle-wrapper.jar`) は L1 が `gradle wrapper --gradle-version 8.7` で初期化する。

## 参照

- L1 行動ルール: `../CLAUDE.md`
- 機能仕様: `../SPEC.md`
- 視覚仕様: `../DESIGN.md`
- 機械検証コマンド: `../sensors/computational.md`
