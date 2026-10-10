# design.md — 判断キットの見た目（配色・絵の定型・確認手順）

テンプレート（`assets/template.html`）は **violet アクセントの明 / 暗 2 テーマ**（2026-10-04 から。それまでは暗地固定）。
判断キットは開発側の面であって業務 UI ではないので、プロジェクトの業務 UI の token ではなく、この独立した世界観
（暗い地 `#14141c` + violet アクセント）を使う（kakuman-platform の開発フィードバック機能の design-lock 由来）。

**テーマの切り替え**: 既定は利用者の OS の設定（`prefers-color-scheme`）。token は `:root`（明）に置き、暗は
`@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {…} }` と `:root[data-theme="dark"]` の 2 箇所に
**同じ値**で書く（片方だけ直すと強制指定のときだけ色がずれる）。色は必ず token 経由（`var(--…)`）で書き、
16 進を直書きしない（例外 = 原画の上に重ねる白文字・lightbox の黒地のように、画像の上で地の色に依らないもの）。

## 書体

| 役割 | フォント | 用途 |
|---|---|---|
| 見出し | Shippori Mincho B1（600 / 800） | h1 / h2 / Q の題 / 段階の数字 |
| 本文 | BIZ UDPGothic（400 / 700） | 全文 |
| 数値・ID | IBM Plex Mono（400 / 500） | FB id・件数・軸ラベル・chip |

Google Fonts から読む（artifact の CSP は fonts.googleapis.com / fonts.gstatic.com を許可）。
各 face に system fallback を必ず添える（テンプレートに書いてある）。

## 配色

| token | 値 | 用途 |
|---|---|---|
| `--ground` | `#14141c` | ページ地 |
| `--surface` / `--surface-2` | `#1c1c27` / `#252533` | パネル / 選択肢の地 |
| `--ink` / `--ink-2` / `--ink-3` | `#ecebf3` / `#aaa8c0` / `#7c7a94` | 本文 / 副文 / 注記 |
| `--accent` | `#8b7ff0` | 選択状態・推奨バッジ・閉ループの破線 |
| `--no` | `#b05a5a` | × 案・守る線・届かない経路 |

### データ色（検証済み、順序固定で使う）

`dataviz` skill の `scripts/validate_palette.js` で **dark surface `#14141c` に対し全項目 PASS** を確認した 4 色。
系列は**この順で**割り当てる（並べ替えると隣接ペアの検証が崩れる）。

| slot | token | 値 | 判断キットでの既定の意味 |
|---|---|---|---|
| 1 | `--c1` | `#9085e9` violet | 人間専管 / 主系列 |
| 2 | `--c2` | `#199e70` aqua | 報告者への 1 往復 |
| 3 | `--c3` | `#c98500` yellow | P3（DB 適用ゲート） |
| 4 | `--c4` | `#3987e5` blue | AI 単独で着手可 |
| 中立 | `--c-neutral` | `#55546a` + 斜線テクスチャ | 待機・その他（色を持たせない） |

検証コマンド（値を変えたら必ず回す。5 色目を足すなら再検証）:

```
node <dataviz>/scripts/validate_palette.js "#9085e9,#199e70,#c98500,#3987e5" --mode dark --surface "#14141c"
```

単一系列（1 本の推移・1 本の横棒）は `--c1` のみで描き、凡例を置かない（題が系列名を兼ねる）。

### 明るい地の token（light）

| token | 値 | 用途 |
|---|---|---|
| `--ground` / `--surface` / `--surface-2` | `#f6f5fa` / `#ffffff` / `#efedf7` | ページ地 / パネル / 選択肢の地 |
| `--ink` / `--ink-2` / `--ink-3` | `#1c1a2b` / `#4a4763` / `#66637f` | 本文 / 副文 / 注記（白地で AA） |
| `--accent` / `--on-accent` | `#5a4ccf` / `#ffffff` | 選択・推奨の線とバッジ / その上の文字 |
| `--c1`〜`--c4` | `#6d5fe0` / `#0f7d58` / `#9a6400` / `#2a6fc4` | 暗の 4 色と同じ色相を白地向けに暗く（順序と意味は同じ） |
| `--seg-ink` | 明 `#ffffff` / 暗 `#0d0d14` | 色の棒・ピルの上の数字 |
| `--ok` / `--ok-soft` / `--on-ok` | 明 `#0f7d58` / 暗 `#199e70`（上の文字 明 `#fff` / 暗 `#0d0d14`） | 回答済みの状態色（データ色 c2 と同じ値だが、意味は UI の状態） |

明の 4 色は暗の検証済み 4 色の色相を保って明度を下げたもの（2026-10-04 実測: 白地 `#ffffff` に対し 4.8〜5.1:1、
`--ground` に対し 4.4〜4.7:1、白い数字を載せても同じ比）。`dataviz` の validator で白地の検証を回してから値を変える
（暗の 4 色の順序と意味の対応は崩さない）。

## 原画・表・回答の面

- **原画（`figures`）**: 角丸 8px・1px の枠・地は `--surface-2`。右下に「拡大」の小札。caption は本文色、
  「見てほしい点」は accent の左線 + `--accent-soft` の囲み。押すとページ内の `<dialog>`（`showModal`）で全画面表示、
  Esc / × / 背景で閉じてフォーカスを元の画像へ返す。外部ライブラリは使わない（artifact の sandbox で動く）
- **表（`table`）**: `.tbl-wrap`（横スクロール・フォーカス可）に入れる。強調列・行は `--accent-soft`、行は左に accent の線。
  ●◐○ は matrix と同じ記号（`--c1`）
- **選択肢**（2026-10-10 改訂）: 選んだ案 = `--accent` の塗り + `--on-accent` の文字 + 右端の ✓（未選択は空の丸）。
  推奨 = 灰の小さな札「AI推奨」だけ（枠も地も変えない）。紫を「人が選んだ」だけに使い、推奨が選ばれているように見せない。
  matrix の推奨行も灰（`--surface-2`）
- **回答の状態**: `--ok`（明 `#0f7d58` / 暗 `#199e70`、上の文字 `--on-ok`）= 回答済み。見出しの札・カードの左線・問いの地図・
  回答バーの進み。未回答は点線の札（`--ink-3`）。答えた問いは画面の外に出ると 1 行に畳む（`html { overflow-anchor: none }`
  にして、画面より上で縮んだ分は JS が scrollBy で戻す。Safari にスクロール位置の自動補正が無いため）
- **▸ 詳しく**: 事実・決まったら を `<details class="q-more">` に入れる。summary は accent の文字で「詳しく（事実 n · 決まったら）」
- **用語の (i)**: 用語に accent の点線の下線 + 18px の丸い (i)（押せる範囲は疑似要素で 38px）。開いた説明は `--surface-2` の地 +
  accent の左線で、その用語を含むブロックの下に出る
- **回答バー**: 画面下に固定（`env(safe-area-inset-*)` で iPhone の下端を避ける）。「回答まとめをコピー」は塗りの主ボタン、
  「次の未回答へ」は静かなボタン。520px 未満では進みの棒を 2 段目へ回し、ボタンを等幅に
- **375px**: `.wrap` の左右 16px、問いのカード 16px。grid は `minmax(0, 1fr)` / `minmax(min(Npx, 100%), 1fr)` で書き、
  長い URL は `overflow-wrap: anywhere` で折る（ページの横スクロールを出さない）

## 絵の定型（手書きするとき）

**まず `references/visuals.md` の宣言的 visual（13 型）で描く**。以下は visual で描けない図を
`{"type":"html"}` / `html` 欄で手書きするときの定型（宣言的 visual もこの規則で描いている）。
絵は「仕組みが見える」ものだけ置く。飾りの図は置かない。

### 1. 積み上げ棒（分類の内訳）

```html
<div class="bar">
  <div class="seg" style="flex:14;background:var(--c1)" data-tip="人間専管 14 件">14</div>
  <div class="seg" style="flex:5;background:var(--c2)" data-tip="…">5</div>
  <div class="seg" style="flex:1;background:var(--c3)" data-tip="…"></div>   <!-- 1 件は数字を書かない -->
  <div class="seg neutral" style="flex:1" data-tip="…"></div>
</div>
<div class="legend"><span><i class="sw" style="background:var(--c1)"></i>人間専管</span>…</div>
```

- 1 本だけ。合計が題に出る（「45 件の待ちの主体」）
- 小さい区分（幅 10px 未満）は数字を書かず、tooltip と凡例で伝える（`min-width:10px` はテンプレート既定）
- 2px の隙間は `gap:2px` で入る

### 2. 推移（時系列 4〜8 点）

- `viewBox="0 0 400 190"`、y 軸は 4 目盛り、x はデータ点の位置に直接ラベル
- 線 2px + 点 r=5（最新は r=6）、値は点の上に直接ラベル（全点に書いてよいのは 8 点以下のとき）
- 1 軸のみ。2 つの量を並べたいときは 2 枚に分ける

### 3. 流れ図（どこで止まるか / 今 vs 提案）

- `<svg class="chart flow" viewBox="0 0 960 H">`、箱は `rx="8"`、`class="box"`（通常）/ `box-strong`（強調）/ `box-dim`（無い・弱い経路）
- 矢印は `marker-end="url(#ah)"`（`defs` に `ah` = 灰 / `ah2` = accent を置く）
- 線の意味: 実線 = 今ある経路 / **破線 accent** = 閉ループ・提案 / **赤の点線** = 届かない・切れている
- 件数は pill（`pill-1..4` + `pill-t`）で箱の左に
- 横幅 760px 未満で横スクロール（`.flow-wrap`）、縦書きは使わない

### 4. 段階図（梯子）

- 3 段を横に並べた `.steps` グリッドを流用するか、SVG で階段状に。各段に「必要なもの / 深さ / 触れる規律」を 1 行ずつ
- 今すぐ動く段は `box-strong`、L0 が要る段は `box-dim`

### 守る線（規律の一覧）

絵ではないが定型。`.guards` グリッドに `.guard`（左に赤線）。1 枚 = 「何をしない」+「なぜ」の 2 行。

## 確認（1 度だけ）

```
cd <scratchpad>
python <skill>/scripts/build_kit.py spec.json kit.html --standalone --strict   # 絵の予算も点検
NODE_PATH=$(npm root -g) node <skill>/scripts/check_layout.js kit.html .        # 1100 明 / 375 明・暗
```

`check_layout.js` は PC 1100px（明）/ mobile 375px（明・暗）でページ全体の横はみ出しと console の error を機械判定し
（横スクロール容器の中身は除外）、`shot-1100-light.png` / `shot-375-light.png` / `shot-375-dark.png` / `shot-375-q1.png` を撮る
（chromium CLI の `--window-size` は最小幅の制約で 375px を再現できないので Playwright を使う。`playwright` が無ければ
`playwright-core` + `CHROME_PATH=<chrome.exe>` で動く）。スクショで見るのは 4 点だけ:
①ラベルの衝突（棒の数字、流れ図の文字が箱からはみ出していないか）②絵が読めるか（mobile で matrix の
案の名前が 1 字ずつ折れていないか、流れ図が縦積みになっているか）③選択肢が 1 行で読めるか ④暗い地で原画・表・推奨の線が見分けられるか。
直したら再 build → publish（スクショは撮り直さなくてよい）。

publish 用の HTML は `--standalone` を付けない（Artifact 側が `<html><head>` を包む）。
