# ANALYSIS 2026-09-29 — Cloudflare で動かせるか / GitHub は必要か

判断材料であり、仕様の変更は含まない。調査日 2026-09-29。

## 事実（一次情報）

| 項目 | 結果 | 出典 |
|---|---|---|
| 外向き WebSocket | Worker / Durable Object から wss:// へ接続できる（`new WebSocket()` または `fetch` + Upgrade） | developers.cloudflare.com/workers/runtime-apis/websockets/ |
| 2 時間の接続保持 | Durable Object は WebSocket や I/O が続く間、経過時間の上限なし。CPU は 1 回の受信あたり 30 秒（受信ごとにリセット） | developers.cloudflare.com/durable-objects/platform/limits/ |
| 休止（Hibernation） | 外向き WebSocket は対象外。常時音声を受けるので、いずれにしても効かない | developers.cloudflare.com/durable-objects/best-practices/websockets/ |
| 費用 | 受信メッセージは 20 通で 1 リクエスト。10 会議（各 2 時間）で約 3.6 万リクエスト・9,000 GB-s。Workers Paid の含まれる枠内で **約 5 ドル／月** | developers.cloudflare.com/workers/platform/pricing/ ・ durable-objects/platform/pricing/ |
| 無料プラン | SQLite 型 Durable Object が使える。1 日 10 万リクエスト・13,000 GB-s。1 会議 900 GB-s なので数値上は収まる。ただし無料プランの CPU 10ms 上限が DO に掛かるかは**未確認** | 同上 |
| 保存 | R2 の無料枠（10GB・書込 100 万回/月）で十分 | developers.cloudflare.com/r2/pricing/ |
| 社内限定 | Cloudflare Access 無料プラン 50 ユーザー（公式ブログ。現行の料金ページでは**未確認**） | blog.cloudflare.com/teams-plans/ |
| GitHub | デプロイに不要。`wrangler deploy` で手元から出せる。Git 連携は任意 | developers.cloudflare.com/workers/ci-cd/builds/ |
| 既知の罠 | Gemini が提供されていない地域のデータセンターで動くと「User location is not supported」になる報告あり | github.com/google-gemini/generative-ai-js/issues/151 |

## 現行 SPEC（ローカル）から変わる点

| 項目 | ローカル（現行） | Cloudflare |
|---|---|---|
| 会議 PC の準備 | Node.js の導入と起動コマンド | ブラウザで URL を開くだけ |
| 使える場所 | 会議 PC 1 台 | 社内の誰の PC・タブレットからでも |
| 保存 | PC のフォルダ | R2。F8「フォルダを開く」はダウンロードに置き換え |
| ログイン | 不要（DONT D5） | **必須**（Cloudflare Access）。無いと誰でも Gemini の費用を使える |
| 会議内容の経路 | PC → Google | PC → Cloudflare → Google（経由先が 1 社増える） |
| 月額 | 0 ドル（Gemini 利用料のみ） | 約 5 ドル＋Gemini 利用料 |
| 構成 | Node.js ＋ ws | Workers ＋ Durable Object ＋ R2 ＋ Access（ARC は monolith のまま） |
| DH の罠 | — | C1（枠はアカウント単位で共有）。既存プロジェクトと同じアカウントなら、作る前に枠の観測が要る |
