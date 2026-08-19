# Hitsuji — 機械的検証 sensor

L1 実装後 / 献上前に **機械的に実行可能**な検証コマンド群。
すべて exit code 0 = pass、非 0 = fail。

---

## 0. 前提

- Android プロジェクトルートは `apps/hitsuji/android/`
- Gradle wrapper (`gradlew`) を使う
- JDK 17 必須（Android Gradle Plugin 8.x 系の要請）

---

## 1. ビルド検証

### 1.1 Debug ビルド

```bash
cd apps/hitsuji/android
./gradlew assembleDebug
```

**期待**: `app/build/outputs/apk/debug/app-debug.apk` 生成。
**FAIL 条件**: コンパイルエラー / リソースエラー / Manifest merge 失敗。

### 1.2 Release ビルド（署名なしで OK）

```bash
./gradlew assembleRelease -x lintVitalRelease
```

**期待**: AAB ではなく APK 生成 OK（Phase 1 はストア配布しない）。

---

## 2. 静的解析

### 2.1 Android Lint

```bash
./gradlew lintDebug
```

**期待**: error 0 件、warning は許容。
**FAIL 条件**: lint error が 1 件以上。

レポート出力先: `app/build/reports/lint-results-debug.html`

### 2.2 Kotlin コードスタイル（ktlint）

```bash
./gradlew ktlintCheck
```

**期待**: 違反 0。
**FAIL 条件**: スタイル違反 1 件以上。

### 2.3 Detekt（静的解析）

```bash
./gradlew detekt
```

**期待**: weighted issues < 10。
**FAIL 条件**: weighted issues ≥ 50 または complexity threshold 越え。

---

## 3. テスト

### 3.1 Unit Test

```bash
./gradlew testDebugUnitTest
```

**期待**: 全テスト pass、coverage ≥ 60%（MVP）。
**FAIL 条件**: テスト失敗 1 件以上。

レポート: `app/build/reports/tests/testDebugUnitTest/index.html`

### 3.2 Instrumented Test（Room / Android 依存）

```bash
./gradlew connectedDebugAndroidTest
```

**期待**: エミュレータ or 実機接続上で全テスト pass。
**前提**: CI で Android Emulator が利用可能であること。
**MVP では**: 環境制約で省略可、ただし手動でローカル実機実行必須。

### 3.3 Coverage（JaCoCo）

```bash
./gradlew jacocoTestReport
```

**期待**: domain layer ≥ 80%、repository layer ≥ 70%、viewmodel layer ≥ 60%。

レポート: `app/build/reports/jacoco/jacocoTestReport/html/index.html`

---

## 4. 依存関係検証

### 4.1 依存関係の脆弱性スキャン

```bash
./gradlew dependencyCheckAnalyze
```

**期待**: CVSS ≥ 7 の脆弱性 0 件。
**FAIL 条件**: high severity vulnerability 検出。

### 4.2 ライセンスチェック

```bash
./gradlew checkLicenses
```

**期待**: GPL 系の混入なし（Android アプリのため LGPL/Apache/MIT 推奨）。

---

## 5. リソース・Manifest 検証

### 5.1 必須パーミッション宣言確認

```bash
grep -E "(POST_NOTIFICATIONS|RECORD_AUDIO|READ_CALENDAR|SCHEDULE_EXACT_ALARM|USE_FULL_SCREEN_INTENT)" \
  apps/hitsuji/android/app/src/main/AndroidManifest.xml
```

**期待**: 5 件すべての宣言が見つかる。
**FAIL 条件**: 1 件でも欠落。

### 5.2 minSdk / targetSdk 整合

```bash
grep -E "minSdk\s*=\s*26" apps/hitsuji/android/app/build.gradle.kts
grep -E "targetSdk\s*=\s*34" apps/hitsuji/android/app/build.gradle.kts
```

**期待**: 両方マッチ。

---

## 6. ドキュメント整合性

### 6.1 SPEC / DONT / DESIGN の trailing whitespace チェック

```bash
grep -rn ' $' apps/hitsuji/*.md apps/hitsuji/spec/*.md apps/hitsuji/sensors/*.md \
  | grep -v '^\s*$' || echo "OK"
```

**期待**: "OK" 出力。
**FAIL 条件**: trailing whitespace 検出。

### 6.2 dead link 検出（INDEX / SPEC 内の相対パス）

```bash
# INDEX.md / SPEC.md で参照される相対パスが実在するか確認
# 「未生成 / 第 2 段階予定」マーカー付きは除外
grep -E '\[.*\]\([^)]+\)' apps/hitsuji/INDEX.md apps/hitsuji/SPEC.md \
  | grep -v '未生成' \
  | grep -v 'http' \
  | # ... 詳細スクリプト化は L1 で実装
```

**期待**: 全相対リンクが存在ファイルを指す or 「未生成」マーカー付き。

### 6.3 デザイントークン直書き検出

```bash
# Kotlin コード内に HEX color literal が直書きされていないか
grep -rEn 'Color\(0x[0-9A-Fa-f]{8}\)' apps/hitsuji/android/app/src/ \
  | grep -v '/theme/Color.kt' \
  | grep -v '/theme/' \
  || echo "OK"
```

**期待**: "OK" 出力（theme/ 以下のみ HEX 直書きが許容される）。
**FAIL 条件**: theme/ 以外で HEX 直書き検出。

---

## 7. クレジット整合性

```bash
grep -E "Built with dialog-harness/layer's v[0-9]+\.[0-9]+\.[0-9]+" apps/hitsuji/README.md
grep -E "harness-credit: managed by layer0 skills" apps/hitsuji/README.md
```

**期待**: 両方マッチ。
**FAIL 条件**: クレジット欠落 / マーカー欠落。

---

## 実行順序（CI 想定）

```bash
# Phase 1: 高速 fail-fast
./gradlew ktlintCheck detekt
./gradlew lintDebug

# Phase 2: ビルド
./gradlew assembleDebug

# Phase 3: テスト
./gradlew testDebugUnitTest jacocoTestReport

# Phase 4: 重い検証
./gradlew dependencyCheckAnalyze

# Phase 5: ドキュメント整合性（shell）
bash apps/hitsuji/sensors/scripts/doc-check.sh  # L1 で実装
```

すべて pass で **computational sensor 全グリーン**。
