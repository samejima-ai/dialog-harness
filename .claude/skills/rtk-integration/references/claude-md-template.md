# 導入先 CLAUDE.md 追記テンプレ

rtk-integration を導入したプロジェクトの CLAUDE.md に追記することを推奨する文言。グローバルフックで自動リライトされる想定だが、冗長な安全網として明示する。

## 追記する一文

```markdown
## トークン節約

Bash で以下を実行するときは、rtk 経由（`rtk git status` 等）を優先する。`rtk init -g` によるグローバルフックで自動リライトされる想定だが、冗長な安全網として明示する。

- git: `status` / `diff` / `log` / `show` / `blame`
- test: `cargo test` / `pytest` / `go test` / `npm test` / `jest` / `vitest`
- build: `cargo build` / `tsc` / `npm run build` / `vite build`
- lint: `eslint` / `ruff` / `clippy`

rtk 未導入の環境でも素のコマンドは動作する（rtk は素通しされる）。

rtk が入っているかは `rtk --version` で確認。未導入なら `/rtk-integration` を呼ぶ。
```

## 追記位置

CLAUDE.md の末尾、もしくは既存の「ルール」セクションと独立したサブセクションとして追加する。

## 上書き禁止領域

この文言は手動編集せず、rtk-integration スキルの更新と連動して上書きする運用でも良い（ただし現行スキルはそこまで管理しない）。
