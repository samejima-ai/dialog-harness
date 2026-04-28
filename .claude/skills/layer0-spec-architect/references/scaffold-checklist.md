# Scaffold Checklist（v5.1.0 追加）

L0 §6「開発環境の設計・構築」で **stack 別に必ず生成すべきファイル群** と **smoke test 手順** を規定する。
`references/dev-env-spec.md` がディレクトリ配置・参照権限マトリクス・モード別差分（M1/M2/L2）を扱うのに対し、本ファイルは **stack 単位の実体ファイル一覧と smoke 手順** に責務を絞る。

**§0 受け入れ基準 2 番との対応**: 本ファイルの対応 stack テンプレートで指示されたファイル群が実体として生成されていない状態で L1 へ譲渡することは原則違反。

---

## v5.1.0 標準 stack: Vite + TypeScript + React + PWA

M2 monolith Web PWA の既定 stack として固定。他 stack は将来 minor で追加（後述）。

### 必須生成ファイル

`§6` 完了時点で以下が **実体として** 存在しなければならない。`SPEC.md` への記載や TODO コメントだけでは充足とみなさない。

| # | パス | 役割 | 最低要件 |
|---|---|---|---|
| 1 | `package.json` | 依存・scripts | `scripts.dev` / `scripts.build` / `scripts.test` を全て持つ。`type: "module"`。`name` / `version` を持つ |
| 2 | `tsconfig.json` | TS 設定 | `strict: true`、`jsx: "react-jsx"`、`moduleResolution: "bundler"` |
| 3 | `vite.config.ts` | ビルド設定 | `@vitejs/plugin-react` を最低限 import、`vite-plugin-pwa` を含めるか TODO 注記で明示 |
| 4 | `vitest.config.ts` | unit test | `environment: "jsdom"`、setup ファイルがあれば設定 |
| 5 | `playwright.config.ts` | E2E（M2 標準） | `baseURL` を `http://localhost:5173` 等に固定、`testDir: "tests/e2e"` |
| 6 | `biome.json`（または `eslint.config.js` + `.prettierrc` の等価セット） | lint/format | `pnpm run lint` から呼べる状態 |
| 7 | `.gitignore` | git 除外 | 最低限 `node_modules/` `dist/` `.env*` `playwright-report/` `coverage/` を含む |
| 8 | `index.html` | エントリ HTML | `<div id="root">` と `<script type="module" src="/src/main.tsx">` を含む |
| 9 | `src/main.tsx` | React mount | `createRoot(document.getElementById("root")).render(<App />)` |
| 10 | `src/App.tsx` | 最小 App | プレースホルダ UI が描画される（空画面で起動エラーが出ないこと） |
| 11 | `public/manifest.webmanifest` | PWA manifest | `name` / `short_name` / `start_url: "/"` / `display: "standalone"` / `icons: [...]` |
| 12 | `public/icons/icon-192.png` & `icon-512.png` | PWA アイコン | プレースホルダ画像で可。Lighthouse PWA チェックを通る最小サイズ |

`pnpm-lock.yaml` は `pnpm install` で生成されるため初期生成チェック対象外。

### Smoke Test 手順

`§7.4 自己検証`「scaffold smoke test」で以下のいずれも通ることを確認する：

```bash
pnpm install              # exit 0、lock 生成
pnpm run dev &            # 起動エラーなし、http://localhost:5173 が 200 を返す
pnpm run build            # exit 0、dist/ 配下に index.html が生成
pnpm run test             # exit 0（テスト 0 件でも構わない、framework 起動が成功すること）
```

通らない場合は **DELIVERY.md（L1 献上時）または delivery/SELF-VERIFICATION-*.md（L0 自己検証時）** に「失敗した手順」「失敗理由」「保留事由」を明記したうえで譲渡する。沈黙したまま L1 へ渡すことは §0 受け入れ基準 3 に違反する。

### Lighthouse PWA 確認（任意・cosmetic 以上で推奨）

UX Priority が `standard` 以上のプロジェクトでは `pnpm run build && pnpm run preview` 後に Lighthouse PWA カテゴリが Installable 判定になることを目視確認する。`critical` プロジェクトでは sensors/computational に CI 化を追記する。

---

## 将来拡張ポイント

本 v5.1.0 では Vite+TS+React+PWA の **1 stack に絞る**。以下は v5.x 以降の minor で追加：

| stack | 想定追加バージョン | 注記 |
|---|---|---|
| Next.js (App Router) | v5.x | App Router 既定、Server Components 含む |
| Vue 3 + Vite | v5.x | Composition API 既定 |
| 純 Node.js CLI | v5.x | tsx/tsup ベース、commander/yargs |
| Astro | v5.x | content collections 前提 |
| SvelteKit | v5.x | adapter-auto |

stack を選ぶ際の判定軸は `references/regime-assessment.md` の「ARC + dev_mode + チーム軸」と整合させる予定（v5.x で追記）。

---

## dev-env-spec.md との責務分離

| ファイル | 責務 |
|---|---|
| `references/dev-env-spec.md` | 用語定義 / ファイル配置規則（参照権限マトリクス含む） / モード別差分（M1/M2/L2 の生成物） / コンテキスト注入戦略 / バージョニング規則 / 移行ノート |
| `references/scaffold-checklist.md`（本ファイル） | stack 別の生成必須ファイル一覧 / smoke test 手順 / 将来拡張ポイント |

両者は **直交関係**。`dev-env-spec.md` の「ファイル配置規則」は全 stack 共通の規約、本ファイルは stack 固有の必須生成物と検証手順を扱う。
