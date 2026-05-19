---
name: hitsuji-design
version: 0.1.0
target_platform: android
generated_at: 2026-05-19
colors:
  primary: "#5B8DEF"        # Lv.1 やさしく - 落ち着いたブルー
  primary_container: "#DDE7FB"
  on_primary: "#FFFFFF"
  on_primary_container: "#0B2A6B"

  secondary: "#7AC9A1"      # 完了・成功 - ミントグリーン
  on_secondary: "#FFFFFF"

  warning: "#F5A623"        # Lv.2 ふつう - アンバー
  on_warning: "#3A2400"

  danger: "#E5484D"         # Lv.3 強め / Lv.4 アラーム - 赤
  on_danger: "#FFFFFF"

  surface: "#FAFAF7"        # ふんわり羊色（オフホワイト）
  surface_variant: "#F0EFE8"
  on_surface: "#1E1E1B"
  on_surface_variant: "#4A4A45"

  outline: "#D6D4CC"
  accent_score: "#FFB84D"   # スコア・バッジのアクセント
  accent_streak: "#9B7BFF"  # 連続日数のアクセント

typography:
  font_family_display: "Noto Sans JP, Roboto, sans-serif"
  font_family_body: "Noto Sans JP, Roboto, sans-serif"
  display_lg: { size: 32, weight: 700, line_height: 40 }
  display_md: { size: 24, weight: 700, line_height: 32 }
  title: { size: 20, weight: 600, line_height: 28 }
  body: { size: 16, weight: 400, line_height: 24 }
  body_emphasis: { size: 16, weight: 600, line_height: 24 }
  caption: { size: 13, weight: 400, line_height: 18 }
  score_number: { size: 40, weight: 800, line_height: 48 }  # スコア表示の主役

spacing:
  xs: 4
  sm: 8
  md: 16
  lg: 24
  xl: 32
  xxl: 48

radius:
  card: 16
  button: 12
  chip: 999       # pill 形状
  fab: 28

elevation:
  card_resting: 1
  card_pressed: 4
  fab: 6
  notification_full_screen: 8

motion:
  duration_fast: 120        # ms
  duration_normal: 240
  duration_emphasis: 400
  easing_standard: "cubic-bezier(0.4, 0.0, 0.2, 1)"
  easing_emphasized: "cubic-bezier(0.05, 0.7, 0.1, 1.0)"
---

# Hitsuji — Design System

## Overview

**ブランド・トーン**: ふんわり優しい羊系のあたたかさと、ADHD 当事者向けの**視認性の強さ**を両立する。
情報密度はあえて控えめにし、**今この瞬間にやるべきこと**だけが目に飛び込んでくる設計を目指す。
ゲーミフィケーション要素（スコア・連続日数・バッジ）は**派手すぎず、しかし達成感は確実に伝わる**程度に視覚化する。

**参考**: お任せ。北欧系のクリーンさ + Material 3 の規範性を踏襲。

---

## Color Tokens

### プライマリパレット

- `{colors.primary}` `#5B8DEF` — メイン CTA、Lv.1 通知、未完了タスクのアクセント
- `{colors.primary_container}` `#DDE7FB` — プライマリの背景帯
- `{colors.secondary}` `#7AC9A1` — 完了状態、成功フィードバック

### 通知エスカレーション色（F3 機能と直結）

| 段階 | カラートークン | HEX |
|---|---|---|
| Lv.1 やさしく | `{colors.primary}` | `#5B8DEF` |
| Lv.2 ふつう | `{colors.warning}` | `#F5A623` |
| Lv.3 強め | `{colors.danger}` | `#E5484D` |
| Lv.4 アラーム | `{colors.danger}` + フルスクリーン | `#E5484D` + 背景占拠 |

通知段階の色遷移は**段階的に派手になる**設計。視覚的にも「やばい」が伝わる。

### ゲーミフィケーション色

- `{colors.accent_score}` `#FFB84D` — スコア数字、バッジ獲得時のグロー
- `{colors.accent_streak}` `#9B7BFF` — 連続日数のフレーム、ストリーク炎アイコン

### Surface（背景）

- `{colors.surface}` `#FAFAF7` — メイン背景。純白ではなく、ふんわり羊色（オフホワイト）
- `{colors.surface_variant}` `#F0EFE8` — カード背景

---

## Typography

- 日本語第一の `Noto Sans JP`、欧文混在は `Roboto` フォールバック
- スコア数字（`{typography.score_number}`）は意図的に大きく重く（40pt / 800）。**達成感の可視化**
- 通知タイトルは `{typography.title}` 20pt / 600。一目で読める

---

## Spacing & Radius

8 の倍数システム。`{spacing.md}` (16) を基準単位とする。
角丸は**やわらかさ重視**：カード 16px、ボタン 12px、チップ pill 形状（999）。

---

## Components

### 1. TaskCard（タスク 1 件の表示）

- 背景: `{colors.surface_variant}`
- 角丸: `{radius.card}` 16px
- パディング: `{spacing.md}` 16px
- タイトル: `{typography.title}`
- 状態によって左端の縦バーの色が変わる：
  - PENDING: `{colors.primary}`
  - NOTIFYING / ESCALATING: 段階別カラー（warning / danger）
  - COMPLETED: `{colors.secondary}` + タイトル取り消し線
  - SNOOZED: `{colors.outline}`

### 2. FAB（タスク登録）

- 位置: 右下、画面端から `{spacing.lg}` 24px
- 背景: `{colors.primary}`
- アイコン: `+ マイクアイコン`（音声入力 primary を示す）
- タップで音声入力が即起動。長押しでテキスト入力モード切替
- `{elevation.fab}` 6dp

### 3. NotificationBanner（通知バナー）

- フルブリードのバナー
- 段階別の背景色（Lv.1〜Lv.4）
- 「完了」「Snooze」ボタン 2 つだけ（**1 タップで完了**を確保）
- Lv.4 ではフルスクリーンインテント（画面占拠）

### 4. ScoreDisplay（スコア表示・ホーム上部）

- 背景: グラデーション `{colors.surface}` → `{colors.accent_score}` の薄い帯
- スコア数字: `{typography.score_number}` 40pt / 800、色 `{colors.accent_score}`
- 横に「+10」アニメーション（タスク完了時に飛び込む）

### 5. StreakBadge（連続日数）

- ピル形状（`{radius.chip}` 999）
- 背景: `{colors.accent_streak}` の薄いトーン
- アイコン: 炎 emoji or 羊アイコン
- 「N 日連続！」と中央に大きく

### 6. NavigationBar

- 3 タブ構成（「今日」「統計」「設定」）
- ボトムナビ、Material 3 規範
- 選択中タブは `{colors.primary}`

---

## Motion

- 通常遷移: `{motion.duration_normal}` 240ms
- 通知エスカレーション時の色変化: `{motion.duration_emphasis}` 400ms、`{motion.easing_emphasized}`
- スコア +10 のフライイン: `{motion.duration_fast}` 120ms で飛び込み、`{motion.duration_normal}` 240ms でフェード
- バッジ獲得時はパーティクル + スケールアニメ（最大 400ms）

ADHD 当事者向けに**アニメーションは短く、しかし達成感のあるものは派手目に**。連続使用での酔いを避ける。

---

## Do's and Don'ts

### ✅ Do

- **タスクのタイトルは画面の主役**。`{typography.title}` 以上のサイズで表示する
- **通知段階は色で一目わかる**ように、必ず段階別カラートークンを使う
- **完了ボタンは 1 タップで完了**できる位置・サイズ（最低 48dp タップ領域）
- **スコア表示は常にホーム上部に固定**（達成感の即時フィードバック）
- **羊らしいやわらかい角丸**（最低 12px）を全コンポーネントで保つ
- **音声入力ボタンは FAB として常時アクセス可能**にする

### ❌ Don't

- **HEX 値をコードに直書きしない**。必ず `{colors.primary}` 等のトークン参照を使う
- **px 値をコードに直書きしない**。必ず `{spacing.md}` 等のトークン参照を使う
- **画面遷移を 3 階層以上深くしない**（ユーザー Must「無駄が嫌い」）
- **通知段階を色変化なしで音量のみで強化しない**（視覚的主張が必須）
- **ペナルティ色（赤）を完了状態に使わない**（赤＝危険・通知強化、緑＝完了の役割固定）
- **広告・課金・他者比較ランキング系の UI を作らない**（DONT.md 違反）
- **キャラクター（羊）を全画面に常駐させない**（情報密度の阻害、無駄複雑回避）
- **アニメーションを 500ms 以上にしない**（ADHD 当事者の待機ストレス回避）

---

## トークン参照ルール

すべてのコード（Kotlin / Compose）で **YAML フロントマターで定義したトークン**を参照すること。

- 色: `MaterialTheme.colorScheme.primary` 等に上記 token をマッピング
- spacing: `Modifier.padding(Hitsuji.spacing.md.dp)` 等の dp 化
- typography: `MaterialTheme.typography` への割当

実装側で `#FFFFFF` や `16.dp` をリテラル記述するのは **§7.4 自己検証で検出される違反**。

---

## E2E 視覚検証

本プロジェクトは Android Native のため、**Vision モデルでのスクリーンショット判定** を MVP では実施しない（Playwright は Web 対象）。
代替として **Android Espresso + 視覚回帰スナップショットテスト**（Paparazzi 等）の導入を Phase 2 で検討する。
MVP では**手動視認**で Do's and Don'ts 違反を確認する。

---

## 拡張ガイド

新しいコンポーネントを追加する際：

1. YAML フロントマターのトークンを必ず参照する（新規 HEX / px の直書きを増やさない）
2. 状態（pressed / disabled / focused）の色変化を `surface_variant` / `outline` で表現する
3. 動きは `{motion.duration_normal}` 以下、emphasis 時のみ 400ms 上限
4. ADHD 当事者特性（短期報酬・視覚主張・低認知負荷）を必ず考慮する

---

## 参照

- 機能仕様: `SPEC.md`
- スコープ外: `DONT.md`
- 通知エスカレーション状態遷移: `spec/state-diagrams.md`（第 2 段階で生成）
