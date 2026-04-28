# sensors/computational.md — 計算的センサー

機械的に判定可能な品質ゲート。**全項目 pass** が L1 献上の前提条件。
1 サイクル ≤ 2 時間制約に収めるため、これら全体で **≤ 1 分** で実行完了すること。

## ビルド

| センサー | 閾値 | 検出コマンド |
|---|---|---|
| TypeScript 型チェック | エラー 0 | `tsc --noEmit` |
| ビルド成功 | exit 0 | `npm run build` (or `pnpm build`) |
| ビルド時間 | ≤ 1 分 | `time npm run build` |
| バンドルサイズ | ≤ 500 KB (gzip) | `vite build --mode=production` の出力監視 |

## テスト

| センサー | 閾値 | 検出コマンド |
|---|---|---|
| ユニットテスト | 全 pass | `vitest run` |
| ユニットテストカバレッジ | ≥ 70%（src/） | `vitest run --coverage` |
| E2E テスト | 全 pass | `playwright test` |
| E2E 主要シナリオ実行時間 | ≤ 30 秒 | Playwright report |

## 静的解析

| センサー | 閾値 | 検出コマンド |
|---|---|---|
| Lint エラー | 0 | `biome check .` or `eslint .` |
| Lint 警告 | 0 | 同上 |
| フォーマット崩れ | 0 | `biome format --check .` or `prettier --check .` |

## PWA / Web 品質

| センサー | 閾値 | 検出コマンド |
|---|---|---|
| Lighthouse PWA score | ≥ 90 | `lighthouse <url> --only-categories=pwa` |
| Lighthouse Performance | ≥ 80 | 同上（mobile 設定） |
| Lighthouse Accessibility | **≥ 95** | 同上（**最重要 NFR**） |
| Lighthouse Best Practices | ≥ 90 | 同上 |

## アクセシビリティ（最重要）

| センサー | 閾値 | 検出コマンド |
|---|---|---|
| axe-core 違反 | 0 | `vitest` + `@axe-core/playwright` |
| コントラスト比 (AA) | ≥ 4.5:1 | axe-core で検出 |
| キーボード操作可能性 | 全 UI 到達可能 | E2E スクリプト |
| フォーカスインジケータ | 全インタラクティブ要素 | E2E + axe |

## ファイル配置（CLAUDE.md §6 準拠）

| センサー | 検出 |
|---|---|
| ルート直下に PLAN.md / TODO.md / MEMO.md | **検出時 fail** |
| ルート直下にスクラッチファイル | 検出時 fail |
| docs/ / drafts/ / scratch/ がコミットされている | 検出時 fail（.gitignore 確認） |

## 実行順（CI 想定）

```bash
# 60 秒以内に完了する想定
npm run typecheck && \
npm run lint && \
npm run test && \
npm run build && \
npm run test:e2e:ci  # 主要シナリオのみ
```

## 失敗時の扱い

- いずれか 1 つでも fail → **L1 献上不可**、即座に修正
- 例外は無し（妹さんの体験品質に直結するため）
