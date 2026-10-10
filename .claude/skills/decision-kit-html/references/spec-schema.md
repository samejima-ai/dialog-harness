# spec-schema.md — 判断キット spec（JSON）の全項目

`scripts/build_kit.py <spec.json> <out.html>` が読む。文字列欄は **HTML 可**（テンプレートが信頼して
そのまま埋める）。JSON なので HTML 属性は single quote で書く（`<span class='mono'>`）。

## トップレベル

| 欄 | 型 | 必須 | 説明 |
|---|---|---|---|
| `key` | string | ✔ | localStorage のキー。キットごとに一意（`fb-question-path-0902` 等）。同じ key で再 publish すると前回の選択が残る |
| `title` | string | ✔ | `<title>` と h1。名前であって説明ではない（「質問経路キット 0902」） |
| `eyebrow` | string | | h1 の上の小見出し（プロジェクト · 領域 · 日付） |
| `lede` | string | | h1 直下の 2〜3 文。件数はここに |
| `meta` | string[] | | `<span>…</span>` の列。起点・実測日・前提・Markdown 正本 |
| `hero_visuals` | Visual[] | ✔(実質) | 要旨の絵 2〜3 枚（`stack` / `waffle` / `trend` / `stats` / `timeline`）。`references/visuals.md` |
| `hero_html` | string | | 手書きの要旨パネル（hero_visuals で描けないときだけ。両方あれば visuals が先） |
| `sections` | Section[] | | 問いの**前**に置く節（流れ図・段階図・守る線・答える順番） |
| `questions_section` | `{eyebrow,h2,sub}` | | 問い一覧の見出し |
| `questions` | Question[] | ✔ | 問いの列。順序 = 表示順 |
| `after_sections` | Section[] | | 問いの**後**に置く節（運用手順・観測指標・新着判定・AI 単独リスト） |
| `foot` | string | | 前提と限界（推奨は AI の見立て / 実機未確認 / 数値の出所） |
| `summaryTitle` | string | | 回答まとめの 1 行目（既定 = title + " — 回答"）。**プロンプトの冒頭**として書く（§回答まとめ） |
| `summaryFooter` | string | | 回答まとめの末尾。**実行の規則 / 回答ごとにすること / 問いなしで先にやること / 作る順番**（§回答まとめ） |
| `glossary` | object | | `{"用語": "1〜2 行の説明"}`（80 字以内、HTML 可）。要旨・各節・各問いで最初に出た所の横に (i) が付き、押すとその場の下に開く。選択肢の中にだけ出る用語は選択肢の上の「用語:」行に出る。本文に無い用語・長すぎる説明は `--strict` で WARN（2026-10-10） |

文字列欄のどこにでも `{{IMG:name}}`（name = `[A-Za-z0-9_-]+`）を置ける。repo に入れる spec は placeholder のまま、
公開用の spec は `scripts/inject_images.py <spec> <images.json> <out>` で scratch に作り（repo の中には書けない）、
build はその出力から（本番の画面・図面の切り抜きを repo に入れないため）。**既定の置き場は `figures` 型の `img`**（下の Visual）。
手書き html に `<img src='{{IMG:row_a}}' alt='…' style='max-width:100%'>` と書く形（2026-10-04 以前のキット）も引き続き動くが、
拡大・見てほしい点・phone で 1 列 が付かないので新しいキットでは使わない。

## Section

| 欄 | 説明 |
|---|---|
| `eyebrow` | `01 · どこで止まるか` の形 |
| `h2` | 節の題（動詞で終える） |
| `sub` | 節の副文（1〜3 文、`.sub`） |
| `visuals` | Visual[]。sub の直後に描く（`flow` / `timeline` / `steps` / `meter` 等） |
| `html` | 本文 HTML（visuals の後。`.guards` / `.tbl-wrap` / 手書き SVG など） |

## Question

| 欄 | 型 | 説明 |
|---|---|---|
| `id` | string | `Q1`… 表示と localStorage と chip の連結キー |
| `title` | string | 動詞で終える問い（HTML 可） |
| `short` | string | 回答まとめに出す短い題（無ければ title からタグを落として使う） |
| `time` | string | `1 分 · 確認` / `2 分` / `5 分` / `10 分` / `ヒアリング 30 分`。**数字は 1 つだけ**（問いの地図の幅に使う。「2 回目」等を混ぜない） |
| `fbs` | string | FB id・報告者・日付（mono で表示） |
| `quote` | string | 報告の原文（要約に必要な範囲、全文転載しない） |
| `visuals` | Visual[] | 問いの絵 1〜2 枚（quote の直後、事実・選択肢の上）。実物を指す問いは **`figures`（原画）が先**、行列は `table` / `matrix`、仕組みは `compare` / `flow`、数は `hbar` |
| `visual_skip` | string | 絵を置かない理由（これが無く visuals も無いと `--strict` で止まる） |
| `factsLabel` | string | 既定「事実」。実測日を入れたいとき（「事実（本日実測）」） |
| `facts` | string[] | 3〜5 行。`<b>` で強調可。推測を書かない。**「▸ 詳しく」に畳まれる**（常には見えない） |
| `optionsLabel` | string | 既定「選択肢」/ multi なら「選択肢（複数可）」 |
| `options` | Option[] | 2〜4 |
| `multi` | bool | 複数選択可 |
| `extra` | string | 選択肢の下に置く HTML（値のヒアリング表など） |
| `recWhy` | string | 推奨の理由 1 文（任意）。選択肢の下に「推奨 A（…）— 理由」の帯で出る。`rec` が「推奨」で始まる案があれば帯は自動で出る（理由なしでも） |
| `after` | string | 「決まったら」= cycle 候補 / gate / scope / migration・P3 / 所要。facts と一緒に「▸ 詳しく」に畳まれる |
| `note` | bool | `false` でメモ欄を消す（既定は表示） |

## Option

| 欄 | 説明 |
|---|---|
| `k` | `A` / `B` / `C` / `D` |
| `label` | 10 秒で違いが分かる 1〜2 文（HTML 可、`<b>` で要点） |
| `rec` | `推奨` / `次点` / `×規律` / `×逆行` など。×は `disabled` と併用 |
| `disabled` | true で選べない（理由を `rec` に） |
| `example` | 任意。案を選ぶと何がどうなるかの 1 行の例（「3(×7) → 数量 7」）。ラベルの下に小さく出る。**回答まとめには出ない** |
| `img` | 任意。案の小さな絵（`{{IMG:name}}` か data URI）。最大 180×72px。`imgAlt` で代替文字（既定 = label） |

推奨（`rec` が「推奨」で始まる案）は灰の小さな札「AI推奨」で出す（「推奨」の 2 字を「AI推奨」に読み替えて表示。まとめの文字は変わらない）。**選ばれた状態にはしない**（選ぶのは人）。紫の塗り + ✓ は人が選んだ案だけ。

## Visual

`{"type": "<型>", "title"?: "…", "caption"?: "…", …型ごとの欄}`。型は `stack` / `waffle` / `hbar` / `trend` /
`stats` / `flow` / `compare` / `matrix` / `steps` / `meter` / `timeline` / **`figures`（原画）/ `table`（表）** / `html`。欄の一覧 = `references/visuals.md`、
全型の実例 = `assets/example-spec.json`。

### 原画と表（2026-10-04 追加）

```json
{"type": "figures", "cols": 2, "items": [
  {"img": "{{IMG:d_memo}}", "tag": "束 D", "caption": "別紙の赤「3(×7)」", "note": "括弧は番号の右肩。数量なのか大きさなのか"}]}
{"type": "table", "hl_col": "束 A", "legend": ["よく出る", "ときどき", "出ない"],
 "columns": ["書き方", "束 A", "束 C", {"label": "件数", "align": "right"}],
 "rows": [["右肩に (×n)", "●", "○", 41], {"cells": ["値が空の行", "◐", "●", 17], "hl": true}]}
```

手書きの `<figure><img src='{{IMG:…}}'>` の格子や `<table>` を spec に書く代わりにこの 2 型を使う。

## 最小例

```json
{
  "key": "example-0902",
  "title": "○○キット 0902",
  "lede": "…",
  "hero_visuals": [{"type": "stack", "title": "N 件の内訳", "items": [{"label": "…", "value": 3}, {"label": "…", "value": 5}]}],
  "questions": [
    {
      "id": "Q1", "title": "○○を△△するか", "short": "○○", "time": "2 分",
      "visuals": [{"type": "matrix", "rec": "A", "axes": ["速い", "簡単", "わかりやすい", "使いたくなる"],
                   "rows": [{"k": "A", "label": "…", "marks": [2, 2, 1, 1]},
                            {"k": "B", "label": "…", "marks": [1, 0, 2, 1]}]}],
      "facts": ["<b>実測</b>: …", "…"],
      "options": [
        {"k": "A", "label": "…", "rec": "推奨"},
        {"k": "B", "label": "…"},
        {"k": "C", "label": "…", "rec": "×規律", "disabled": true}
      ],
      "after": "A なら cycle 候補 X-…（局所、migration ゼロ）"
    }
  ]
}
```

## 回答の面（テンプレートが自動で付ける）

- **読み方**（上部、たためる）: 見る → 選ぶ → コピー の 3 段と、問いの数・所要の合計
- **用語の (i)**: `glossary` があれば自動で付く（上の表）
- **回答バー**（画面の下に固定、safe-area 対応）: 「回答 3/7」・進み・「次の未回答へ」（全部答えたら「まとめを見る」）・「回答まとめをコピー」
- **キー**: 今の問い（触った / フォーカスのある / 画面の一番上の問い）で `1`〜`4` か `A`〜`D` = その案を選ぶ（もう一度で外す）、`Enter` = 次の問いへ。メモ欄の入力中は効かない
- **コピー**: クリックの中で `navigator.clipboard.writeText` → だめなら隠し textarea を選んで `execCommand('copy')` → それもだめならまとめを選択して Ctrl/⌘+C を案内。押したボタンが 2 秒「コピーしました」になる
- **カードの並び**: 問い（見出しに 未回答 / ✓回答済み の札）→ 原画・絵 → 選択肢 → AI推奨の帯 → ▸ 詳しく（事実・決まったら）→ メモ
- **選んだ案**: 紫の塗り + 白文字 + ✓（未選択は空の丸、複数選択は四角）
- **答えた問い**: 左の線と札が緑の「✓ 回答済み」になり、画面の外に出ると 1 行（Qn・題・あなたの答え・メモ）に畳まれる。
  押すか「開く」で戻る。再読み込みしたときも答えた問いは畳んだ状態で始まる。畳んだ問いにはキーの 1〜4 が効かない（見えないまま答えを変えない）。
  問いの地図のタイルも緑の ✓

## 回答まとめの形式（コピーされる文字列）

```
<summaryTitle>

Q1 <short>: A（<label の先頭 40 字>）
  メモ: <メモ欄の内容>
Q2 <short>: 未回答
…
<summaryFooter>
```

貼り戻された回答は、Markdown 正本の §決定記録 に「問い / 決定 / 次 cycle で AI がすること」の表で写す。
**この行の形は変えない**（`Qn <short>: X（label 先頭 40 字）` / `  メモ: …` / `Qn <short>: 未回答`）。option の `example` / `img` はまとめに入らない。

### 回答まとめはプロンプト（2026-10-01 作業のループ 1001 から）

貼り戻される文字列だけが AI に届くので、`summaryTitle` を「この回答どおりに自律駆動で実行してください。処理できる
ものを全て完了し、最後に HTML の報告書を Artifact で出してください」の形にし、`summaryFooter` に Markdown の
4 節を持たせる（全文の型 = `SKILL.md` §回答まとめ = プロンプト）:

| 節 | 書くこと |
|---|---|
| `## 実行の規則` | 作業場所 / 1 件 = 1 PR と PR 前の検査 / 独立レビューと Copilot / マージ権限（「この回答が承認」、migration は AI がマージしない）/ 本番 DB は読むだけ / 安全判定で止まったら報告 / フィード投稿の可否 / SPEC 枠内 + history 3 本 / 未回答は推奨・メモ優先 / 変えない決定（PR 番号） |
| `## 回答ごとにすること` | `Qn A: … B: … C: …` — **選ばれなかった案も**。cycle 名・gate・局所 / 横断・migration の有無 |
| `## 問いなしで先にやること` | 応急（起きている障害）。済んでいれば PR 番号 |
| `## 作る順番` | ① → ② → …（依存順。migration の適用をまたぐものは「適用後」） |

JSON の中では改行を `\n` で書く。型 = `SKILL.md` §回答まとめ = プロンプト。

### 決定記録の節（回答後）

`scripts/add_decisions.py <spec.json> <decisions.json>` が `sections` の先頭に `00 · 決定記録（<date> 追記）` の節
（`meter` + 4 列の表 = 問い / 決定 / AI がすること / PR か状態）を足す。再実行で同じ節を置き換えるので、出荷のたびに
最後の列を PR 番号に直す → `inject_images.py`（本番の画像があるとき）→ `build_kit.py --strict` → 同じ `url` へ再 publish する。
