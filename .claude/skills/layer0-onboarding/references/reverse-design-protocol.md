# Reverse Design Protocol（v5.16.0 追加）

既存プロジェクトの harness 後付け onboarding で、既存 src/ から視覚仕様 + デザイントークンを逆抽出し `DESIGN.md` 初版を生成するプロトコル。layer0-onboarding/SKILL.md §4.4 から参照される。

DESIGN.md 規格そのものは `../../layer0-spec-architect/references/design-system-spec.md`、テンプレートは `../../layer0-spec-architect/assets/design-md-template.md` を参照（spec-architect の資産を借用、onboarding 側で再生成しない）。

---

## 原則

- **UI プロジェクトのみ起動**: 非対面（CLI / API サーバ / ライブラリ）では本プロトコル完全スキップ
- **逆抽出は AI 推定の集合体**: 全項目に確度メタデータ（AI 推定 / コード確認 / 人間確定）を付与
- **既存資産を尊重**: 既存の HEX リテラル / px 直書きを「悪い」と判定せず、まず現状を抽出する。修正は spec-architect 移行後の判断
- **テンプレート借用**: spec-architect の `design-md-template.md` を使い、onboarding 側にテンプレを複製しない（フラクタル・DRY）
- **handoff 整合**: 生成した DESIGN.md は handoff-to-spec-architect.md の引き継ぎ対象に含める

---

## UI 検出条件

以下のいずれかに該当する場合に本プロトコルを起動する。AI が SKILL.md Step 4.4.1 で機械的判定。

| 検出シグナル | 判定 |
|---|---|
| `src/` 配下に `.tsx` / `.jsx` / `.vue` / `.svelte` ファイル存在 | **UI あり** |
| `index.html` / `public/index.html` 存在 | **UI あり** |
| `manifest.webmanifest` / `manifest.json` (PWA) 存在 | **UI あり** |
| `tailwind.config.*` / `postcss.config.*` 存在 | **UI あり** |
| `.css` / `.scss` / `.less` ファイルが 5 個以上 | **UI あり** |
| 上記いずれも該当せず `bin/` `cli.*` `*.py` (CLI 構造) のみ | **UI なし → スキップ** |

迷ったら UI ありで起動する（生成コスト < 未生成による情報純度低下）。

---

## 逆抽出手順

### Step 1: 色トークンの抽出

```bash
# HEX リテラルを grep して頻度集計
grep -rEho '#[0-9A-Fa-f]{6}\b' src/ | sort | uniq -c | sort -rn | head -20

# rgb()/rgba() も同様
grep -rEho 'rgba?\([^)]+\)' src/ | sort | uniq -c | sort -rn | head -20
```

抽出した上位 5〜10 色を以下の役割に割り当てる（AI 推定）:

| 役割 | 推定基準 |
|---|---|
| `colors.primary` | CTA 系（`button`/`btn-primary`/`submit`）クラス名と共に最頻出する色 |
| `colors.background` | `body` / `html` / `:root` の `background-color`、または白系で最頻出 |
| `colors.surface` | カード系（`card`/`panel`）クラスの背景色、または background との中間色 |
| `colors.error` | `error`/`danger`/`alert` クラスと共起する赤系 |
| `colors.text-primary` | `body` / `:root` の `color`、または黒系で最頻出 |

### Step 2: タイポグラフィの抽出

```bash
# font-family 抽出
grep -rEho "font-family:\s*[^;]+" src/ | sort | uniq -c | sort -rn

# font-size 抽出（px 単位）
grep -rEho 'font-size:\s*[0-9]+px' src/ | sort | uniq -c | sort -rn

# font-weight 抽出
grep -rEho 'font-weight:\s*[0-9]+' src/ | sort | uniq -c | sort -rn
```

主要 font-family を `typography.headline-lg` / `typography.body-md` の `fontFamily` に割り当てる。font-size は h1〜h6 と本文を区別して採用。

### Step 3: spacing の抽出

```bash
# padding / margin の px 値を集計
grep -rEho '(padding|margin)(-[a-z]+)?:\s*[0-9]+px' src/ | grep -oE '[0-9]+px' | sort | uniq -c | sort -rn | head -10
```

頻出値を `spacing.base` / `sm` / `md` / `lg` / `xl` に割り当てる。`4px` の倍数になっていれば DESIGN.md 標準に合致、ずれていれば AI が「8 倍数推奨へのリファクタ候補」と注記（DONT.md ではなく DESIGN.md コメント内）。

### Step 4: shape / elevation の抽出

```bash
# border-radius
grep -rEho 'border-radius:\s*[0-9]+(px|%|rem)?' src/ | sort | uniq -c | sort -rn

# box-shadow
grep -rEho 'box-shadow:\s*[^;]+' src/ | sort | uniq -c | sort -rn
```

`rounded.sm` / `md` / `full`、`elevation.card` / `hover` に割り当てる。

### Step 5: Tailwind / CSS-in-JS の場合の特別処理

| stack | 抽出元 | 補足 |
|---|---|---|
| Tailwind CSS | `tailwind.config.*` の `theme.extend` セクション | 既にトークン化されているため最も信頼できる |
| styled-components / Emotion | `theme.ts` / `theme.tsx` の export | 既存テーマがあればそれを最優先で借用 |
| CSS Variables | `:root` の `--variable` 定義 | 既にトークン化されているため借用 |
| 生 CSS | 各ファイルから grep | 集計結果から最頻値を採用、確度「AI 推定」 |

---

## 生成プロトコル

### Step 1: テンプレート読み込み

`../../layer0-spec-architect/assets/design-md-template.md` の YAML フロントマター + Markdown 本体構造を借用する。

### Step 2: プレースホルダ置換

| プレースホルダ | 置換ソース |
|---|---|
| `<<<YYYY-MM-DD>>>` | 当日日付 |
| `<<<#1A73E8>>>` (primary) | Step 1 で抽出した primary 候補 |
| `<<<#1557B0>>>` (primary-hover) | primary を 10% darken（HSL の L チャンネル -10%）|
| その他色トークン | Step 1 の抽出値 |
| typography 値 | Step 2 の抽出値 |
| spacing 値 | Step 3 の抽出値 |
| rounded / elevation 値 | Step 4 の抽出値 |
| `<<<クリーン、プロフェッショナル、高密度>>>` | 「（reverse-extracted from existing code, 人間レビュー待ち）」 |
| `<<<例: Linear / Notion / Google Workspace>>>` | 削除（reverse-design では参考類似サービスは推定不可能） |

### Step 3: バージョン注記の挿入

YAML フロントマター内の先頭コメント（`---` の直後）に以下を追加:

```yaml
---
# DESIGN.md v0.1 (extracted from existing code on YYYY-MM-DD)
# Source: layer0-onboarding reverse-design-protocol v5.16.0
# Note: 全項目 AI 推定。spec-architect 移行後の人間承認で確度を引き上げる
colors:
  ...
---
```

### Step 4: Markdown 本体の生成

`## Overview (Brand & Style)` は AI が以下のテンプレートで埋める:

```markdown
## Overview (Brand & Style)

本プロジェクトの UI は既存 src/ からの逆抽出によると **<<<トーン推定>>>** の方向性。
（reverse-extracted on YYYY-MM-DD by layer0-onboarding、確度: AI 推定）

**参考類似サービス**: 既存コードからは推定不可能。spec-architect 移行後に人間との対話で確定する。
```

`<<<トーン推定>>>` は抽出した色のトーンから AI が推定:
- グレースケール中心 + 1 〜 2 色アクセント → 「クリーン・プロフェッショナル」
- 彩度高めの複数色 → 「親しみやすい・カラフル」
- 黒/白中心 → 「ミニマル・モノクローム」

`## Colors` `## Typography` `## Layout & Spacing` 等の各セクションは抽出値の用途を AI が推定して記述する。例:

```markdown
## Colors

- **Primary**: 既存 src/ で `button-primary` クラスと共起する `#1A73E8` を採用（確度: AI 推定、出現 47 箇所）
- **Surface vs Background**: `:root` の background は `#FFFFFF`、`card` クラスの背景は `#F8F9FA`（確度: コード確認）
- ...
```

`## Do's and Don'ts` は **空欄ではなく** AI 推定で初版を埋める（スタンダードな項目を 4〜6 件記載）。spec-architect 移行後の人間レビューで追加・削除する想定。

---

## 確度メタデータの 3 段階

archaeology-protocol.md と同じ 3 段階を採用:

| 確度 | 判定基準 |
|---|---|
| **コード確認** | grep 結果が 5 箇所以上で一致、または `tailwind.config.*` / `theme.ts` から直接借用 |
| **AI 推定** | 既存コードから推測したが確認件数が少ない、または用途のマッピングが AI 判断 |
| **人間確定** | reverse-design 時点では不可能（spec-architect 移行後の人間承認で初めて到達） |

各トークン / セクションに確度を付与し、YAML コメントまたは Markdown 本体に明示する。

---

## 抽出例（standard 深度の Web React アプリ）

既存の React + CSS Modules プロジェクトから抽出した DESIGN.md 初版の YAML フロントマターイメージ:

```yaml
---
# DESIGN.md v0.1 (extracted from existing code on 2026-05-12)
# Source: layer0-onboarding reverse-design-protocol v5.16.0
# Note: 全項目 AI 推定。spec-architect 移行後の人間承認で確度を引き上げる

colors:
  primary: "#1A73E8"             # 既存 src/ で button-primary クラスと共起、47 箇所（確度: コード確認）
  primary-hover: "#1557B0"       # primary の L -10%（確度: AI 推定 / 自動算出）
  secondary: "#5F6368"           # text-secondary 用に出現、18 箇所（確度: コード確認）
  background: "#FFFFFF"          # :root background-color（確度: コード確認）
  surface: "#F8F9FA"             # .card クラスの background-color（確度: コード確認）
  error: "#D93025"               # .error / .alert と共起、6 箇所（確度: コード確認）
  text-primary: "#202124"        # :root の color（確度: コード確認）
  text-secondary: "#5F6368"      # .meta クラスの color、12 箇所（確度: AI 推定）

typography:
  headline-lg:
    fontFamily: "Inter, system-ui, sans-serif"  # h1〜h2 で確認（確度: コード確認）
    fontSize: 32px               # h1 の最頻出値（確度: コード確認）
    fontWeight: 700              # （確度: AI 推定）
    lineHeight: 1.2              # （確度: AI 推定 / デフォルト値採用）
  ...
---
```

---

## handoff への組込

handoff-to-spec-architect.md の引き継ぎチェックリストに以下を追加:

- DESIGN.md が生成済み（UI プロジェクトの場合）
- DESIGN.md の確度メタデータが付与済み
- 「人間確定」が一切ないことを spec-architect が認識（移行後の最初の対話で必ず承認プロセスを実施）

spec-architect は LC ≥ 1 振り返り儀式（§1.5）で DESIGN.md を再評価し、人間との対話で確度を「人間確定」に引き上げる。

---

## 非起動条件の明示

以下では本プロトコル全体を起動しない（DESIGN.md を生成しない）:

- 既存プロジェクトが CLI / API サーバ / ライブラリのみ（UI 検出条件のいずれも非該当）
- 既存プロジェクトに既に DESIGN.md が存在する（onboarding は再生成しない、spec-architect 移行後に更新）
- 人間が明示的に「視覚仕様は要らない」と指示した（REGIME.md に拒否日を記録）
