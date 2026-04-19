# rtk 対応コマンド一覧

rtk v0.37.1 が圧縮対応する主要コマンド。rtk-integration が狙う主戦場のホワイトリスト。

## 圧縮率目安（rtk 公式実測）

| 分類 | コマンド | 圧縮率目安 | 備考 |
|---|---|---|---|
| git | `git status` | **-80%** | 毎サイクル頻発するので体感最大 |
| git | `git diff` | -70〜85% | ファイル数に比例して効果増 |
| git | `git log` | -80〜90% | 長期ログほど効く |
| git | `git show` | -70% | コミット詳細 |
| git | `git blame` | -60% | ファイル長に依存 |
| test | `cargo test` | **-90%** | Rust プロジェクトで最大効果 |
| test | `pytest` | -85% | Python テスト |
| test | `go test` | -85% | Go テスト |
| test | `npm test` / `jest` / `vitest` | -80% | JS テスト |
| build | `cargo build` | -85% | warning 大量時に効く |
| build | `tsc` / `tsc --noEmit` | -75% | TypeScript 型チェック |
| build | `npm run build` / `vite build` | -70% | フロント |
| lint | `eslint` | -75% | 複数ファイル対象で効く |
| lint | `ruff` | -70% | Python lint |
| lint | `clippy` | -80% | Rust lint |

## 非対象・素通し

- Claude Code ネイティブの Read / Glob / Grep（rtk をバイパスする設計）
- docker / kubectl / aws CLI（rtk は対応しているが本スキルのホワイトリストでは除外）
- 対話的コマンド（vim / less 等）

## 使い方

グローバルフック有効時は `git status` と打つだけで自動的に `rtk git status` にリライトされる。明示的に `rtk git status` と打っても同じ結果。

フック無効時 or 明示的に rtk を通したいとき:

```bash
rtk git status
rtk cargo test
rtk eslint src/
```
