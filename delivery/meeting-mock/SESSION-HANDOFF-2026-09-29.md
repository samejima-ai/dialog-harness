# セッション引き継ぎ 2026-09-29 — 会議モック可視化ツール L0

ローカル PC の Claude Code でこの続きを始めるときに、最初に読ませるメモ。

## 始め方

ローカルの Claude Code で、このフォルダを開いて次のように話しかける:

> delivery/meeting-mock/SESSION-HANDOFF-2026-09-29.md を読んで、L0 ブレストの続きから再開して

## 今の状態

| 段階 | 状態 |
|---|---|
| S1 企画・S2 要件 | 済み（判断キット 0929 の Q1〜Q10、開発フロー判断キットの Q1〜Q13 に回答済み） |
| S3 情報設計〜S5 ビジュアル方針 | 済み（画面一覧・比率・切替・トーン・強調色） |
| S6 プロトタイプ | モック v2 まで作成 |
| S7 確認 | **v2 への感想待ち** |
| S8 確定 | 未着手（SPEC・REGIME の確定、CLAUDE.md・センサー・雛形の生成） |

## ファイルの場所

| ファイル | 中身 |
|---|---|
| `INDEX.md` | 目次 |
| `SPEC.md` | 機能仕様 v0.3（F0〜F12） |
| `DONT.md` | スコープ外と禁止挙動 |
| `REGIME.md` | 開発体制（ドラフト。M2 見込み） |
| `DESIGN.md` | 視覚仕様（青 #1D5FD8、本文 20px） |
| `delivery/meeting-mock/2026-09-29-L0-DECISION-KIT.md` | 判断キット 0929 の問いと決定記録 |
| `delivery/meeting-mock/2026-09-29-L0-FLOW-KIT.md` | 開発フロー判断キットの問いと決定記録 |
| `delivery/meeting-mock/ANALYSIS-2026-09-29-fact-check.md` | Gemini・json-render の事実確認 |
| `delivery/meeting-mock/ANALYSIS-2026-09-29-cloudflare.md` | Cloudflare で動かせるかの調査 |
| `delivery/meeting-mock/board-mock-v2.html` | 触れるモック（最新）。ブラウザで直接開ける |
| `delivery/meeting-mock/*.html`（l0-modes / l0-flow） | 判断キットの HTML |

## 未決の判断（次に決めること）

1. **実行場所**: ローカル（Node.js）か Cloudflare（Durable Objects ＋ R2 ＋ Access）か
2. Cloudflare の場合、既存の Cloudflare プロジェクトと同じアカウントか（同じなら作る前に枠を観測する）
3. **実装順**: 最初の使い方が開発の会議なので、P0 → P1a → **P1b** → P2 → P3 → P4 に組み替えるか（AI 推奨）
4. モック v2 の感想（S7）

## ローカルと Cloudflare の比較（2026-09-29 のチャットより）

| 軸 | ローカル | Cloudflare | 理由 |
|---|---|---|---|
| 素早い開発 | ● | ◐ | Cloudflare は Durable Objects・R2・Access の分だけ序盤の作業が 3〜5 割増し（AI 推定） |
| 開発中の確認の手軽さ | ○ | ● | ローカルは更新のたびに取得・起動。Cloudflare は URL を開き直すだけ |
| 煩わしくない環境 | ○ | ● | ローカルは会議 PC に Node.js・.env・起動コマンドが要る |
| 動作速度 | ● | ● | 待ち時間の大半は Gemini の生成と集約窓。経由による増加は数十ミリ秒（推定） |
| 費用 | ● 0 ドル | ◐ 約 5 ドル／月 | Gemini 利用料は同じ |
| 安全面 | ● 社内で完結 | ◐ | Cloudflare はログイン必須、経由先が 1 社増える |

AI 推奨: Cloudflare。ただし P0 で「Durable Object から Gemini Live に接続し 10 分切替まで動くか」「設置地域の罠（User location is not supported）が出ないか」を短く検証し、通らなければローカルへ切り替える。中核処理（ドキュメント更新・モック生成・画面）は共通化する。

## 注意点

- このフォルダには dialog-harness（DH）本体のファイルも入っている。新リポジトリへ移すときに仕分ける（開発フロー判断キット Q1-C）。`scripts/` は移さない（Q2-A）
- `.github/workflows/` は DH 本体用。新リポジトリへは持っていかない
- 元のブランチ: `samejima-ai/dialog-harness` の `ccr-a72b57e5-jrlhni`（master へマージしない）
