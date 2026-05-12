# Design System Spec (DESIGN.md 規格)

UI を伴うプロジェクトで生成する `DESIGN.md` の規格・対話プロトコル・運用規律。
SKILL.md §3.6 から参照される。Google Labs 公式仕様、シニアエンジニア運用ノウハウ、
LLM コンテキスト付与に関する知見を統合し、AI コーディングエージェントに
プロジェクトの視覚的アイデンティティを伝えるための単一仕様ファイルとして規定する。

---

## 原則

- DESIGN.md は **UI を伴うプロジェクト限定** の追加ドキュメント。CLI / API サーバ / ライブラリでは生成しない
- AGENTS.md（CLAUDE.md, 振る舞い）/ SKILL.md（個別タスク）/ DESIGN.md（外観）の **3 層分離** を維持する。CLAUDE.md に視覚仕様を埋め込まない
- YAML フロントマター（機械可読の絶対値）+ Markdown 本体（人間/AI 可読の意図と運用）の **2 層構造** を遵守する
- 「盆栽運用」: 古い記述は剪定する。長大な壁は AI にも害となる
- Do's and Don'ts セクションは LLM の **アンカリング効果を正の方向に活用** する最強の道具。省略しない
- 機械可読トークン（HEX/px/rem）と意図記述（Markdown）の **両方が揃って** はじめて DESIGN.md として成立する

---

## 起動判定

L0 §3.6 で実施。SPEC.md の機能定義が出揃った時点で 1 問だけ投げる。

### トリガー質問（DG1）

> 「このプロジェクトは画面（UI）を持ちますか？ Web / モバイル / デスクトップのいずれでも」

| 回答 | 起動判定 |
|---|---|
| 持つ（Web / Mobile / Desktop / PWA / Electron 等） | **起動** — DESIGN.md を生成 |
| 持たない（純 CLI / API サーバ単独 / ライブラリ / バッチ） | **スキップ** — DESIGN.md を生成しない |
| ヘッドレス API + 別途消費側 UI あり（管理画面なし） | **判断献上** — 人間が DESIGN.md 必要性を判定 |

### AI 推定による省略

以下が SPEC.md から読み取れる場合、DG1 を投げずに「起動」と仮判定する（人間に通知のみ）:

- 「画面」「ボタン」「フォーム」「ダッシュボード」等 UI 要素の言及
- `scaffold-checklist.md` の Vite + React + PWA stack 採用
- ARC が monolith かつ機能一覧に対面 UI 機能（ログイン画面 / 検索画面等）を含む

逆に以下では「スキップ」と仮判定する:

- SPEC.md に「CLI ツール」「ライブラリ」「バックエンド API のみ」と明示
- 機能一覧が全て非対面（バッチ処理 / cron / webhook 等）

仮判定は対話の自然な流れの中で 1 回だけ確認する（「画面ありプロジェクトと理解しました。DESIGN.md を生成します」）。

---

## 対話プロトコル（DESIGN.md 3 問）

UX 3問プロトコル（SKILL.md §2.5）と同じ思想で、非デザイナーが答えやすい 3 問に絞る。
未回答時は AI が業界標準値で自動補完する。

| # | 質問 | 格納先 | 自動補完デフォルト |
|---|---|---|---|
| DG2 | ブランド・トーンを 1 行で言うと？（例: クリーン・プロフェッショナル / 親しみやすい / ミニマル・モノクローム） | `## Overview (Brand & Style)` | 「クリーン、プロフェッショナル、高密度」（実践テンプレ準拠） |
| DG3 | 「あの UI が好き」という参考はある？（既存サービス名・スクリーンショット URL でも可） | `## Overview` 末尾の参考リンク | UX 3問 Q3 の参考類似サービスを流用 |
| DG4 | プライマリカラー（CTA に使う色）は決まっている？ HEX / RGB / 色名 / 「お任せ」のいずれかで | `colors.primary`（YAML） | `#1A73E8`（Google Material Blue、実践テンプレ準拠） |

### AI 自動補完の根拠

- DG2 デフォルト: 業務アプリ・社内ツールの 80% は「クリーン・プロフェッショナル」が無難（実践テンプレ準拠）
- DG4 デフォルト: HEX `#1A73E8` は WCAG AA を白背景で満たしつつブランド固有性が低く、後から差し替えやすい
- typography / spacing / shapes の数値はすべて実践テンプレ準拠のデフォルトで埋め、後続の人間レビューで差分のみ受ける

### 詰め込み禁止

DG1〜DG4 は **2 ターン以内** に投げ切る。1 ターン目で DG1（UI 有無）、2 ターン目で DG2+DG3+DG4 をまとめて。
それ以上の細部質問（individual color / individual padding 等）は L0 では行わない。
詳細な差分は人間レビュー（SKILL.md §5）で受ける。

---

## 公式構造（Google Labs Spec 準拠）

### 2 層構造

1. **YAML フロントマター（機械可読）** — `---` で囲まれたファイル冒頭。デザイントークン（HEX, px, rem 等の絶対値）
2. **Markdown 本体（人間/AI 可読）** — トークンを「いつ・なぜ・どのように」適用するかの哲学・運用ルール

### 標準セクション順序

Markdown 本体は以下の順序で `##` (h2) を並べる。不要セクションは省略可。

1. `## Overview (Brand & Style)` — ブランドの個性・感情的トーン
2. `## Colors` — プライマリ / セカンダリ / セマンティック（成功・エラー等）の意図と用途
3. `## Typography` — フォントファミリー・ウェイト・行間の運用
4. `## Layout & Spacing` — 余白基準・グリッド戦略・ゲシュタルト要因の活用
5. `## Elevation & Depth` — 影（Shadow）・Z インデックス階層
6. `## Shapes` — 角丸（Border radius）ルール
7. `## Components` — ボタン / 入力フォーム等の UI 要素別スタイリング
8. `## Do's and Don'ts` — 視覚的境界制約・アクセシビリティルール（必須）

---

## YAML フロントマターの推奨スキーマ

実践テンプレ（`assets/design-md-template.md`）の YAML を最小スキーマとする。トークンキーの追加は許容、既存キーの改名は禁止。

```yaml
colors:        # 必須。primary, background, surface, error, text-primary を最低含む
typography:    # 必須。少なくとも headline-lg と body-md
spacing:       # 必須。base + sm/md/lg/xl の 4px グリッド
rounded:       # 推奨。sm/md/full
components:    # 推奨。最低 button-primary
```

トークン参照記法は `{colors.primary}` 形式。これは Markdown 本体および L1 実装側 CSS-in-JS / Tailwind config 等から参照される。

---

## Do's and Don'ts の力（重要）

LLM の「アンカリング効果」を **正の方向に利用** する最強のセクション。
他のセクションが「こうしてほしい」を書くのに対し、Do's and Don'ts は「ここから外れないこと」を書く。

### 推奨記述パターン

```markdown
## Do's and Don'ts
- **Do**: インタラクティブなカードには微細なシャドウを用いて、クリック可能であることを示すこと
- **Do**: すべてのテキストは WCAG 2.1 AA 規格のコントラスト比（4.5:1 以上）を満たすこと
- **Don't**: 1 つの画面内に 3 つ以上の異なるフォントウェイトを混在させないこと
- **Don't**: エラー以外の通常の警告や情報表示に `colors.error` を使用しないこと
```

### なぜ最強か

LLM はデフォルトで「無難なよくある UI」に収束する性質がある（学習データ平均化）。
Do's and Don'ts は AI のデフォルト出力を **意図的に破壊** してプロジェクト固有の方向に導く。
過剰なコンテキスト（カラーパレット 30 色等）は AI の探索を阻害するが、Do's and Don'ts は **収束を強める方向のアンカリング** であり、UI 規約の遵守という目的と一致する。

---

## 意図（Why）のコード化

YAML フロントマターの JSON 風数値は機械可読だが、**「なぜそうするか」が欠落** する。
Markdown 本体には必ず意図を 1〜2 行で添える:

| トークン | 数値だけ（ダメ例） | 意図付き（OK 例） |
|---|---|---|
| `colors.primary` | `"#1A73E8"` | "プライマリは最も重要な CTA にのみ使用。装飾の背景には使わない（ユーザーの視線誘導を 1 つに絞る）" |
| `spacing.sm` vs `xl` | `8px` / `32px` | "関係性が密な要素間は sm、異なるセクション間は xl。ゲシュタルト要因（近接の要因）で UI 上の意味を表現する" |
| `rounded.md` | `8px` | "インタラクティブ要素全てに適用。わずかに柔らかい印象。完全直角は法定文書系のみ、`rounded.full` はバッジ・アバター限定" |

LLM は意図付きトークンを参照することで、**未知の UI を作る際にも推論可能** になる（例: 「新規モーダルの ok ボタン色は？」→「CTA → primary」と判断できる）。

---

## 運用規律

### 盆栽アプローチ

- 長大な壁（The Wall of Text）は害。トークン数が増えるほど LLM の注意が散る
- 古い記述は **容赦無く剪定** する。「使われなくなった legacy color」を残さない
- 1 ファイル 200〜400 行を目安とし、超過時は L0 振り返り儀式（§1.5）で削減対象に挙げる

### コードと共に更新する

- DESIGN.md の変更は **同一 PR 内で CSS / Tailwind config / コンポーネント実装と一緒にコミット** する
- 外部 Wiki / Notion / Figma 単独管理は禁止（同期コストが運用で死ぬ）
- リポジトリのルートに配置し、ソースコードとバージョンを完全一致させる

### L1 側との連携

- L1 (autonomous-dev) は UI 実装時に **`@DESIGN.md` を強制参照** する
- CLAUDE.md の「参照」セクションに `視覚仕様: DESIGN.md` を 1 行追記する
- L1 自己検証で「DESIGN.md トークンを直接書き換える HEX リテラル」が src/ に混入していないか確認する（任意センサー、§4.4 inferential 候補）

### LC ≥ 1 での扱い

既存プロジェクト（LC ≥ 1）への DESIGN.md 後付け追加は事後追加プロトコル準拠:

1. 人間が「視覚的一貫性が崩れている / AI 出力 UI がバラバラ」と宣言
2. AI が現状の src/ から色・font・spacing を **逆抽出**（archeo-architect 起動も検討）
3. 抽出結果を DG2〜DG4 への AI 推定回答として提示
4. 人間レビュー → DESIGN.md 初版生成

逆抽出による初版生成時は YAML フロントマターに `# v0.1 (extracted from existing code on YYYY-MM-DD)` 注記を入れる。

---

## INDEX.md / CLAUDE.md / DONT.md との関係

### INDEX.md

DESIGN.md 生成時のみ、INDEX.md に 1 行追加する:

```markdown
## 視覚仕様（UI プロジェクトのみ）
→ DESIGN.md
```

非 UI プロジェクトでは行ごと省略。

### CLAUDE.md

`## 参照` セクションに 1 行追加:

```markdown
## 参照
- 仕様: INDEX.md
- 視覚仕様: DESIGN.md   ← 追加
- 体制: REGIME.md
...
```

### DONT.md

DESIGN.md と DONT.md は禁止事項の **抽象レベルで棲み分け** る:

- **DESIGN.md の Do's and Don'ts**: 視覚レベルの禁止（フォントウェイト混在禁止 / colors.error の流用禁止 / 角丸半径の不統一禁止 等）。トークン参照を含む具体的なスタイリングルール
- **DONT.md**: 機能レベルの禁止（パフォーマンス最適化を仕様に含めない / 創造的 UX デザインを AI に任せない 等）。SPEC.md と直交するスコープ外定義

両者は **重複転記しない**。視覚仕様の禁止は DESIGN.md に閉じる。UX 3問プロトコル（SKILL.md §2.5 Q2）で得た機能レベルの禁止挙動のみ DONT.md に転記する（既存ルール、本仕様で変更なし）。

---

## §7.4 自己検証への組込

L0 自己検証チェックリストに以下 1 項目を追加（UI プロジェクトのみ）:

- [ ] **DESIGN.md トークン一貫性検査**: YAML フロントマターで定義したトークンキーが Markdown 本体の `{colors.primary}` 等の参照と整合する（未定義参照なし・未使用定義なし）

検査は `grep -oE '{[a-z.-]+}' DESIGN.md` 等の手作業で十分。shell script 雛形は配置しない。

---

## E2E 視覚検証が最も重要（コードファーストの限界）

**前提**: dialog-harness の判定基準は philosophy 三拍子「**仕様に合う・動く・使える**」。DESIGN.md トークン整合検査（grep ベースの静的検査）は **第 1 層に毛が生えた程度** の検査でしかなく、これだけで UX を保証することはできない。コードファーストの検査では「画面が実際にユーザーの目にどう映るか」を検証できない。

**真の検証経路**: philosophy 5 層検出スタック（`philosophy.md` §第2条 Shift Left 原則、`../../layer1-autonomous-dev/references/inferential-sensor-v2.md`）の第 2/3/5 層に DESIGN.md を必ず乗せる:

| 層 | 検査内容 | DESIGN.md との対応 |
|---|---|---|
| 第 1 層 計算的 | HEX リテラル / px 直書きの grep、YAML トークンキーと `{...}` 参照の整合 | 静的検査（必要条件、十分条件ではない）|
| **第 2 層 E2E (Playwright)** | 実画面起動 + スクリーンショット取得 + baseline 比較 | **DESIGN.md トークンが実画面に反映されているか** を機械検証 |
| 第 3 層 Interaction Cost | クリック数 / 遷移深度 / 応答時間（UX 3問の Must 閾値） | 「使える」の定量代理指標 |
| 第 4 層 推論的センサー | SPEC.md と画面の照合 | 「仕様に合う」「動く」の判定 |
| **第 5 層 Vision モデル判定** | スクリーンショットを Vision モデルで読み、DESIGN.md `## Overview` のブランドトーン・`## Do's and Don'ts` 違反を判定 | **DESIGN.md の意図通りの見た目になっているか** の最終確認 |

### 必須経路

- 第 1 層通過後に **必ず第 2 層 E2E でスクショ取得**（Playwright の `expect(page).toHaveScreenshot()` または `page.screenshot()` で保存）
- UX Priority が `standard` 以上の機能は **第 5 層 Vision 判定** を必ず通す（Vision モデルにスクショと DESIGN.md `## Do's and Don'ts` を入力し、違反パターンを検出）
- `critical` Priority の機能は加えて **WCAG コントラスト比測定**（Lighthouse Accessibility / axe-core）を CI 化する

### コードファーストでは検出できない不整合の例

- フォント読み込み失敗で system-ui にフォールバックしているのにコード上は `Inter` 指定 → スクショで判別可能
- ダークモード切替時にコントラスト比 4.5:1 を割っている → Vision / 計測のみ判別可能
- `colors.primary` を CTA 以外に流用してしまった（コードでは正しいトークン名でも、運用上 Do's and Don'ts 違反）→ Vision 判定でのみ検出可能
- レスポンシブ崩れで spacing が破綻 → スクショ比較でのみ検出可能

### L1 への要請

L1-autonomous-dev は実装完了時、`pnpm run test:e2e` 等で Playwright を起動し DESIGN.md の影響範囲（主要画面）の **スクショを delivery/screenshots/ 配下に保存** すること。L1-independent-reviewer は処理フロー 5.5.1 でこのスクショを Vision モデル経由で DESIGN.md と照合する。

詳細プロトコルは `../../layer1-autonomous-dev/references/inferential-sensor-v2.md` の第 2/5 層を参照。

---

## 非起動条件の明示

以下では DG1 を投げずに DESIGN.md スキップを確定する:

- SPEC.md に「CLI」「ライブラリ」「バッチ」「webhook ハンドラ」のみ記載
- バックエンドサービス単体運用で対面 UI を持たない（例: event-sourcing バックエンド、API サーバ単体、メッセージブローカー）。event-sourcing でもイベント履歴ダッシュボード等の UI を持つ場合は **起動** する
- DOMAIN-CONTEXT.md に「ヘッドレス」「内部 API のみ」明示
- M1 単体モード × 1 機能未満（実験プロトタイプ）

迷ったら DG1 を投げる（時間コスト 30 秒未満）。

---

## バージョニング

DESIGN.md 自体のバージョンは YAML フロントマター内（`---` 区切りの内側）の先頭にコメントで記録する。frontmatter はファイル先頭の `---` から始まる必要があるため、コメントを `---` の前に置かないこと（テンプレ `assets/design-md-template.md` と同じ順序）:

```yaml
---
# DESIGN.md v0.1 generated by layer0-spec-architect on YYYY-MM-DD
# Source: dialog-harness/layer's DESIGN.md spec v5.15.0+
colors:
  ...
---
```

minor 更新（トークン追加）は v0.X、major 更新（既存トークン削除・改名）は v1.X 以降に昇格。
更新時は CHANGELOG.md（プロジェクトの方）に 1 行追記する。

---

## 参考文献

- Google Labs Design System Spec（公式 DESIGN.md 構造の原典）
- LLM コンテキスト過多のアンカリング効果（Crossover Effect 研究）
- Material Design / Apple HIG / Tailwind CSS 既定値（DG4 自動補完の根拠）

実践テンプレートの完全形は `assets/design-md-template.md` を参照。
