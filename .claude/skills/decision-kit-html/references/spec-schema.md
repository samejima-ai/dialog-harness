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
      "visuals": [                     // 1 枚以上（先頭がいちばん大きく見える）。原図 > モック > 挿絵 > 表・グラフ
        { "kind": "original", "src": "{{IMG:faces}}", "caption": "…" },
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
- `mock.html` は sandbox の iframe（スクリプト可・外へ出られない）で出す。大きいときは別の Artifact にして `url` で開く
- 回答まとめの行の形 = `ID 見出し: K（選択肢の先頭 40 字）` / `  メモ: …` / `ID 見出し: 未回答`
