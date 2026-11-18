# 判断キット v2 の spec（JSON）

```jsonc
{
  "key": "survey-split-1023",          // キットの名前（英数とハイフン）
  "title": "…",                        // ページの表題（何を決めるか 1 行）
  "lede": "…",                         // 要旨 1〜2 行（HTML 可）
  "meta": ["起点 = …", "実測 = …"],    // 出所（HTML 可）
  "items": [
    {
      "id": "Q1",                      // 回答まとめに出る記号
      "title": "…",                    // 見出し（24 字まで）
      "phases": false,                 // true = 「解説」と「選ぶ」の 2 枚に分ける（複雑な項目）
      "target": "exists",              // 確認の項目: exists = もうある（先頭は現物）/ new = まだ無い（先頭は様式・挿絵・モック）。確認でなければ省く
      "feel": true,                    // 感覚が効く問い・提出物に関わる問い。未回答を推奨で進めず、全体の絵で印を付ける（組み立ては読まない）
      "visuals": [                     // 1 枚以上（先頭がいちばん大きく見える）。現物 > 様式 > モック > 挿絵 > 表・グラフ
        { "kind": "original", "src": "{{IMG:faces}}", "caption": "…" },
        { "kind": "original", "file": "in/出面.xlsx", "focus": "出面!A3:H3", "caption": "いまの出面表（赤枠 = 列の見出し）" },
        { "kind": "original", "file": "in/図面.pdf", "page": 2, "box": [40, 20, 30, 25], "caption": "北面（赤枠 = 3 階の手すり）" },          // file = xlsx・docx・pptx・pdf・画像 → PNG
        { "kind": "template", "file": "tpl/お知らせ.docx", "source": "nichi-format 同梱テンプレ", "caption": "これから作る形（中身は仮）", "trim": false },
        { "kind": "mock", "url": "https://claude.ai/artifact/…", "src": "{{IMG:shot}}", "caption": "…" },
        { "kind": "mock", "html": "<div>…触れる見本…</div>", "caption": "…" },
        { "kind": "illustration", "src": "il.png", "caption": "見本（AI が描いた）…" },
        { "kind": "table", "columns": ["…"], "rows": [["…"]], "caption": "…" },
        { "kind": "chart", "bars": [{ "label": "…", "value": 3 }], "unit": " 件", "caption": "…" }
      ],
      "issue": "…",                    // 課題（120 字まで）
      "explain": ["…", "…"],           // 説明（3 つまで・各 90 字まで、HTML 可）
      "more": "…",                     // ▸ 詳しく（任意。出所・細かい事実）
      "question": "…",                 // 質問（60 字まで、動詞で終える）
      "multi": false,                  // true = 複数選べる
      "rec": "A",                      // AI推奨（options の k）
      "options": [
        { "k": "A", "label": "…", "why": "…" },              // label 50 字・why 60 字まで
        { "k": "C", "label": "…", "why": "×理由", "disabled": true }
      ]
    }
  ],
  "summaryTitle": "…の回答です。この回答どおりに…",       // まとめのプロンプトの頭
  "summaryFooter": "## 実行の規則\n…\n## 回答ごとにすること\n…\n## 作る順番\n…"
}
```

- `src` = ファイルのパス（spec からの相対）/ data URI / `{{IMG:name}}`（`--images` の JSON から差し替え）/ http(s)
- `file` = spec からの相対（か --image-root の中）。`page` は 1 始まり。`trim` は省くと 表計算 = 切る / それ以外 = 切らない。公開版にはファイル名だけが出る
- `focus` = xlsx・xlsm のセル範囲（"A3:H3" / "シート名!A3:H3"）。`box` = [左, 上, 幅, 高さ]（ページに対する %）。現物で file を使うときはどちらか（全体そのものを見るなら `whole: true`）
- `template` は `source`（どの既定の様式・見本か）を必ず書く
- `mock.html` は sandbox の iframe（スクリプト可・外へ出られない）で出す。大きいときは別の Artifact にして `url` で開く
- 回答まとめの行の形 = `ID 見出し: K（選択肢の先頭 40 字）` / `  メモ: …` / `ID 見出し: 未回答`
