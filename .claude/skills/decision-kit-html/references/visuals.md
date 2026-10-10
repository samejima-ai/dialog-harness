# visuals.md — 絵の型カタログ（宣言的 visual）

spec に `{"type": "...", ...}` を置くと `scripts/visuals.py` が絵に組む。手書き SVG は不要。
置き場所は 3 つ: `hero_visuals`（要旨）/ `sections[].visuals`（節）/ `questions[].visuals`（問いの中）。
全型に共通で `title`（絵の上の 1 行）と `caption`（絵の下の注記）を付けられる。見本 = `assets/example-spec.json`
（全 13 型を 1 枚に並べたもの。build して目で見てから選ぶと早い。原画・表・選択肢の画像は Q4）。

## まず「伝えたいこと」から型を選ぶ

| 伝えたいこと | 型 | 例 |
|---|---|---|
| **問いが指している実物**（図面・画面・数量表の該当箇所） | `figures`（原画） | 「3(×7)」の赤字の切り抜き + 見てほしい点 |
| 案 × 軸、書き方 × 束 などの**行列** | `table`（表） | 書き方 3 種 × 束 A〜D を ●◐○ と件数で |
| 全体が何でできているか（内訳） | `stack` | 45 件の待ちの主体 |
| 件数そのものの重み（100 件以下） | `waffle` | 1 マス = 1 件。「多い」を数えずに見せる |
| 項目どうしの大小 | `hbar` | 工種別の要望件数 |
| 増えているか減っているか | `trend` | 週ごとの未対応件数 |
| 大きな数字 2〜4 個 | `stats` | 45 件 / 28 日 / 3 問 |
| どこで止まるか・どう流れるか | `flow` | 報告 → 整理 → 判断（止まる）→ 返信（届かない） |
| 選ぶと何が変わるか | `compare` | 今 → A を選んだ後（＋ / − 付き） |
| 案ごとの得失 | `matrix` | 北極星 4 軸 × 案 A〜C を ●◐○× で |
| 段階・梯子 | `steps` | 今すぐ / 次 cycle / L0 が要る |
| どこまで進んだか | `meter` | 5 段中 2 段 |
| いつ何が起き、どこで止まったか | `timeline` | 報告 8/28 → 整理 8/29 → 27 日空白 → 今日 |
| 上のどれでもない | `html` | `{"type":"html","html":"<svg …>"}`（design.md の流れ図定型など） |

**問いの絵の既定**: 問いが実物の書き方・見え方を指す → **まず `figures`（原画）**。選択肢が 2 つ以上の軸で違う → `matrix`（自由な列・件数・束ごとの列が要るなら `table`）。選んだ後に仕組みが変わる → `compare`（または `flow`）。
事実に数が 2 つ以上ある → `hbar` / `stats`。どれも当てはまらない問い（呼び名の選択など）だけ `visual_skip` に理由を書く。

## 型ごとの欄

| 型 | 欄 | 注 |
|---|---|---|
| `stack` | `items[{label, value, color?, tip?}]`, `unit` | color = `c1`〜`c4` / `neutral`（省略時は順に c1→c4）。全体の 6% 未満の区分は数字を書かず凡例へ |
| `waffle` | `items[{label, value, color?}]`, `unit` | 合計 200 マスまで（超えたら stack） |
| `hbar` | `items[{label, value, hl?, note?}]`, `unit`, `max?` | 単一系列 = c1。`hl:true` の行だけ濃く（強調したい 1〜2 本） |
| `trend` | `points[{x, y}]`, `unit` | 2〜12 点。8 点以下は全点に値、それ以上は最新のみ |
| `stats` | `items[{n, l, c?}]` | `c` = `no`（悪い数字）/ `accent`（今日の数字）/ c1〜c4 |
| `flow` | `nodes[{label, sub?, kind?, n?, c?}]`, `edges[]`, `loop_back?` | kind = `normal` / `strong`（AI がやる・強調）/ `dim`（無い・まだ）/ `stop`（止まる所）。edges[i] は i→i+1 の線で `"solid"` / `"loop"`（破線 accent = 提案・閉ループ）/ `"no"`（赤点線 = 届かない）か `{style, label}`。`n` は箱の左上の件数ピル。mobile では縦積みに変わる |
| `compare` | `before{title, items[]}`, `after{title, items[]}` | item の先頭 `"+ "` = 増える（緑）/ `"- "` = 消える（赤） |
| `matrix` | `axes[]`, `rows[{k, label, marks[]}]`, `rec?` | marks = `2`●強い / `1`◐中 / `0`○弱い / `-1`×損なう / `null` —。`rec` = 推奨案の k（行が灰で強調される。紫は選んだ案だけの色） |
| `steps` | `items[{t, m, body, now?, later?}]` | now = 今すぐ動く段（紫枠）/ later = L0 が要る段（破線） |
| `meter` | `value`, `max`, `unit` | 1 本の進捗 |
| `timeline` | `events[{date, label, kind?}]`, `gap?` | kind = `normal` / `now` / `stop`（止まった点・赤）/ `future`（破線）。`gap` = 空白期間の注記（赤） |
| `figures` | `items[{img, caption, note?, tag?, alt?}]`, `cols?` | 原画。`img` = `{{IMG:name}}`（公開版は inject_images.py が data URI に差し替える）か data URI。`caption` = 何を見る切り抜きか 1 行（無いと `--strict` で WARN）、`note` = 「見てほしい点」の囲み、`tag` = 束・画面名の小札。`cols` = 1〜4（既定 = 枚数と 3 の小さい方）。PC は cols 列、タブレットは 2 列まで、phone（560px 未満）は 1 列。押すとページ内で拡大（Esc / × / 背景で閉じる）。placeholder のまま build すると壊れた画像でなく「原画 name」の箱が出る |
| `table` | `columns[]`, `rows[]`, `hl_col?`, `hl_row?`, `legend?`, `row_head?` | 表。columns の要素は文字か `{label, align}`（align = `right` で数字列）。rows の要素はセルの列か `{cells[], hl}`。セルが `●` `◐` `○` `×` `—` の 1 字なら記号に描く（凡例は自動。`legend: ["よく出る","ときどき","出ない"]` で語を替え、`false` で消す）。`hl_col` = 列の添字か見出し、`hl_row` = 行の添字か 1 列目の文字。1 列目は行見出し（`row_head: false` で外す）。横スクロールの箱に入るので phone でもページははみ出さない |

## 原画（figures）の選び方

- **原画が先**: 問いが図面・画面・帳票の「この書き方」を指すなら、文字で説明する前にその部分を切り抜いて出す
- **1 つの点に 1 枚**。2 つの書き方を比べるなら 2 枚。全体図を 1 枚で出して「この辺」と言わない
- caption は「何を見るか」（「番号 3 の横の赤い (×7)」）。`note` は判断に効く点だけ（無ければ省く）
- 1 問 6 枚まで（超えると `--strict` で WARN）。repo の spec は `{{IMG:name}}` のまま、本物は公開版にだけ
- 架空の見本は小さな SVG の data URI で作る（`assets/example-spec.json`）。本物の図面・顧客の画像を見本にしない
- **見え方の好みを聞く問い**は、今の画面（tag「今」）+ 案ごとの試作画面（tag「A」「B」…）の撮影を 1 つの `figures` に並べる。
  caption は「選ぶとどう見えるか」を 1 行、`note` は今の画面の困りごとだけに付ける（先例 = kakuman-platform の 2026-10-10 判断キット改訂キット。本パッケージには同梱しない）

## 守ること

- 色は design.md の検証済み 4 色 + 中立だけ（visuals.py が他の値を ERROR にする）。意味は design.md §データ色
- 1 つの絵に 1 つの主張。2 つの量は 2 枚に分ける（trend は 1 軸のみ）
- 数字は実測値だけ。見積もり・仮の値は `caption` に「見積もり」と書く
- matrix の ●◐○ は AI の見立て。事実で裏づけられない軸は入れない（`caption` に根拠の所在を書く）
- 絵は畳まない（事実・決まったら は ▸詳しく に畳まれるが、絵は 1〜2 枚とも常に見える）。だから絵だけで違いが分かるように描く
- 飾りの絵を置かない。「この絵が無いと判断に何が足りなくなるか」に答えられない絵は消す
