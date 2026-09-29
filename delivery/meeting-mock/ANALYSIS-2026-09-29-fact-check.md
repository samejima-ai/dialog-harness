# ANALYSIS 2026-09-29 — 外部サービスの事実確認（R1 / R3 / R4）

判断材料であり、仕様の変更は含まない。調査日 2026-09-29、一次ソースで確認。

## R1 Gemini モデルと料金（有料枠）

| 用途 | モデル ID | 単価 | 要件書との差 |
|---|---|---|---|
| 文字起こし | `gemini-3.5-transcribe-live` | 音声入力 $3.50/1M tok（約 $0.005/分）・テキスト出力 $21.00/1M tok（約 $0.004/分） | 一致 |
| 文書更新・モック | `gemini-3.5-flash-lite`（Stable） | 入力 $0.30・出力 $2.50 /1M tok | **一致**（AI が「Flash の価格帯」と疑ったのは誤り。3.5 Flash は $1.50 / $9.00） |
| キャッシュ | Flash-Lite の context caching | $0.03/1M tok ＋ 保存 $1.00/1M tok/時（有料枠のみ） | 要件書に記載なし |

文字起こし Live の仕様:
- 1 接続あたり連続 10 分まで（要件書どおり）。session resumption は**未確認**なので、重複区間を設けて切り替える設計を維持する
- 話者の区別は Live では非対応（区別できるのは非ストリーミングの `gemini-3.5-transcribe`）
- 途中結果 = `interim_input_transcription`、確定結果 = `input_transcription`
- 入力音声は 16bit PCM・16kHz・mono・little-endian（`audio/pcm;rate=16000`）、100ms ごとに送る
- custom_vocabulary（固有名詞の登録）と VAD（発話区間の検出）に対応。単語ごとの時刻は返らない

## R3 json-render（`@json-render/core` / `@json-render/react` 0.21.0、Apache-2.0）

| 項目 | 事実 | 要件書への影響 |
|---|---|---|
| 形式 | **フラットな要素マップ**。`{root, elements:{id:{type, props, children:[子id]}}}` | §7.3「children を持つ木構造」を書き換える |
| 逐次表示 | JSONL で 1 行ずつ JSON Patch（RFC 6902）を送る（SpecStream） | FR-05「途中から順に表示」は patch 列で実現する |
| 編集 | patch / merge / diff モード | 「変更は必要な部品だけ」（§12）と相性がよい。前の案に対する patch を出させる |
| カタログ | zod で props を型付けする（`defineCatalog`）。`catalog.prompt()` でプロンプトを生成 | FR-09 の型定義を zod に揃える |
| 依存 | core は zod ^4、react は react ^19.2.3。AI SDK は不要 | 技術構成に追記 |

## R4 有料枠の判別とデータ利用

- API キーから有料枠か無料枠かをプログラムで判別する方法は**見つからなかった**。確認手段は AI Studio の Billing Tier 列
- 無料枠では、入出力が製品改善に使われ、人間が読む可能性がある。有料枠では使われない（不正検知のため一定期間ログ保存）
- 影響: §12「有料枠キー以外を拒否するスイッチ」は機械判定では作れない。設定で自己申告させ、起動時に警告を出す運用に格下げする案（Q8 で社内のみと決まったため、P2 までに決めればよい）

## 費用見積もりへの影響

単価は正しかったので、会議モード約 1.4 ドル／時・開発モード約 4.3 ドル／時の見積もりは変わらない。カタログ部分（約 4k トークンと仮定）をキャッシュすると、その入力費は約 1/10 になる。

## 出典

- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite
- https://ai.google.dev/gemini-api/docs/live-api/live-transcribe
- https://ai.google.dev/gemini-api/terms
- https://ai.google.dev/gemini-api/docs/billing
- https://github.com/vercel-labs/json-render
- https://registry.npmjs.org/@json-render/core
