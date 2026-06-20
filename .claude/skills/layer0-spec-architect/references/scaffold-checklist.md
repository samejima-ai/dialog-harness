# Scaffold Checklist（v5.1.0 追加 / v6.1.0 で 9 stack カタログ化 / v6.2.0 で Expo 追加 10 stack 化）

L0 §6「開発環境の設計・構築」で **stack 別に必ず生成すべきファイル群** と **smoke test 手順** を規定する。
標準 stack（Vite+TS+React+PWA）に加え、`## 追加 stack カタログ` で Next.js / Vue / Astro / FastAPI / Django / Express / Go / Rails / Expo の 9 stack を同形式で規定する（合計 10 stack）。
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
| 12 | `public/icons/icon-192.png` & `public/icons/icon-512.png` | PWA アイコン | プレースホルダ画像で可。Lighthouse PWA チェックを通る最小サイズ |

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

### DESIGN.md 連携（v5.15.0 追加、UI stack 共通）

Vite + TypeScript + React + PWA stack（および将来追加される全ての UI 含み stack）は DESIGN.md の生成対象。**コードファーストでは UX を保証できない**ため、philosophy 三拍子「仕様に合う・動く・使える」を満たすには **E2E 視覚検証が最も重要** という認識を持つこと。

L0 §3.6 で生成された `DESIGN.md` を L1 (autonomous-dev) は以下の形で消費する:

- `CLAUDE.md` の `## 参照` セクションに `視覚仕様: DESIGN.md` が含まれることを確認
- `src/` 配下の CSS / Tailwind config / CSS-in-JS / styled-components で **DESIGN.md の YAML トークンを参照** し、HEX リテラルや px 直書きを避ける（第 1 層・静的）
- 新規 UI コンポーネント実装時は `DESIGN.md` の `## Components` セクションに該当コンポーネント定義を追加（YAML + Markdown の 2 層を維持）
- **第 2 層 E2E**: Playwright で主要画面のスクショを `delivery/screenshots/` 配下に保存。`expect(page).toHaveScreenshot()` で baseline 比較を CI に組み込むことを推奨
- **第 5 層 Vision 判定**（UX Priority `standard` 以上で必須）: 保存したスクショと DESIGN.md `## Do's and Don'ts` を Vision モデルに入力し違反パターンを検出
- WCAG コントラスト比は `critical` Priority で Lighthouse Accessibility / axe-core を CI 化

DESIGN.md の規格・対話プロトコル詳細は `references/design-system-spec.md` 参照（§E2E 視覚検証 セクション必読）。非 UI stack（将来の純 Node.js CLI 等）では DESIGN.md は生成されず、本セクションも適用されない。

---

## 追加 stack カタログ（v6.1.0 追加 / v6.2.0 で Expo 追加）

上記 Vite+TS+React+PWA を標準 stack とし、本セクションで **9 つの追加 stack** を DH 形式（必須生成ファイル表 + smoke test）で規定する。stack を選ぶ際の判定軸は `references/regime-assessment.md` の「ARC + dev_mode + チーム軸」と整合させる。

> **出典・観測経路の明示（Council `council-2026-06-18T11:50:01Z-cw0rld` 条件②）**
> 本カタログの stack 選定・標準コマンド構成は、外部観測事例 [claude-world-examples](https://github.com/claude-world/claude-world-examples)（非公式コミュニティ製・MIT License）の framework 別 CLAUDE.md テンプレを **観測** し、DH の scaffold-checklist 形式（必須生成ファイル + smoke 手順）に **再構成** したものである。原典の散文テンプレを丸ごと転記したものではない。観測事例としての位置づけは `references/observed-peers.md` を参照。各 stack の必須生成ファイル一覧・最低要件・smoke 手順は DH 固有の規約であり、原典には存在しない。
>
> **保守責務の明示（Council 条件②、開発者ペルソナ懸念）**
> 各 stack の smoke コマンドは framework のメジャーバージョン更新で陳腐化しうる。本カタログは「実体ファイル一覧 + smoke コマンド」の決定論的記述に限定し、framework 固有の流行 lib（state 管理・UI 等）は **選択肢の例示にとどめ最低要件に含めない**（陳腐化面の最小化）。stack 追加時は対応する smoke コマンドが当該 framework の現行 CLI で通ることを L0 §7.4 自己検証で確認する。

各 stack に共通する規約：
- `.gitignore` は最低限 `node_modules/`（または言語別の依存ディレクトリ）/ ビルド成果物 / `.env*` / テストレポート / カバレッジを含む
- `.env` 系の秘匿値（`DATABASE_URL` / `SECRET_KEY` / `JWT_SECRET` 等）は **`.gitignore` 必須**。`.env.example` で雛形のみコミット
- smoke test が通らない場合は §7.4 自己検証の規約に従い `DELIVERY.md` / `delivery/SELF-VERIFICATION-*.md` に失敗手順・理由・保留事由を明記して譲渡する（沈黙譲渡は §0 受け入れ基準 3 違反）
- UI を含む stack（React/Next.js/Vue/Astro/Expo）は `## DESIGN.md 連携` の対象。非 UI stack（FastAPI/Django/Express/Go/Rails の API 専用構成）では DESIGN.md は生成しない。Expo（ネイティブ UI）の視覚検証は各 stack 節「DESIGN.md 連携」の読み替え規約に従う

---

### Stack 2: Next.js 14+ (App Router) ＋ TypeScript

| # | パス | 役割 | 最低要件 |
|---|---|---|---|
| 1 | `package.json` | 依存・scripts | `dev` / `build` / `start` / `lint` を持つ。`next` を依存に持つ |
| 2 | `tsconfig.json` | TS 設定 | `strict: true`、Next.js TS プラグイン（`plugins: [{ name: "next" }]`）を含む |
| 3 | `next.config.mjs`（または `.ts`） | Next 設定 | 最低限 `export default` で設定オブジェクトを返す |
| 4 | `tailwind.config.ts` + `postcss.config.mjs` | スタイル | `content` に `app/**` `components/**` を含む |
| 5 | `app/layout.tsx` | ルートレイアウト | `<html>` / `<body>` と `children` を返す Server Component |
| 6 | `app/page.tsx` | トップページ | プレースホルダ UI を返す |
| 7 | `components/ui/` | UI コンポーネント置場 | 空でも可（ディレクトリ存在） |
| 8 | `lib/` | DB/auth 等の共有ロジック置場 | DB 使用時は `lib/db.ts`、認証使用時は `lib/auth.ts` |
| 9 | `.env.example` | 環境変数雛形 | DB/auth 使用時は `DATABASE_URL` / `NEXTAUTH_SECRET` / `NEXTAUTH_URL` 等のキー名を例示（値は空） |
| 10 | `.gitignore` | git 除外 | `.next/` `node_modules/` `.env*` を含む |

**Smoke test**: `npm install` → `npm run build`（exit 0、`.next/` 生成）→ `npm run dev`（`http://localhost:3000` が 200）→ `npm run lint`（exit 0）。テスト基盤を入れる場合は M2 標準に従い vitest/playwright を追加し `npm run test` を smoke に含める。

---

### Stack 3: Vue 3 + Vite ＋ TypeScript

| # | パス | 役割 | 最低要件 |
|---|---|---|---|
| 1 | `package.json` | 依存・scripts | `dev` / `build` / `preview` / `test` / `lint` を持つ |
| 2 | `tsconfig.json` | TS 設定 | `strict: true`、Vue SFC 用設定（`vue-tsc` 連携） |
| 3 | `vite.config.ts` | ビルド設定 | `@vitejs/plugin-vue` を import |
| 4 | `vitest.config.ts`（または vite.config 内統合） | unit test | `environment: "jsdom"` |
| 5 | `index.html` | エントリ HTML | `<div id="app">` と `<script type="module" src="/src/main.ts">` |
| 6 | `src/main.ts` | Vue mount | `createApp(App).use(router).use(pinia).mount("#app")` |
| 7 | `src/App.vue` | ルート SFC | プレースホルダ UI |
| 8 | `src/router/index.ts` | ルーティング | Vue Router 4、最低 1 ルート定義 |
| 9 | `src/stores/` | Pinia ストア置場 | 空でも可（ディレクトリ存在） |
| 10 | `.gitignore` | git 除外 | `node_modules/` `dist/` `.env*` `coverage/` |

**Smoke test**: `npm install` → `npm run dev`（`http://localhost:5173` が 200）→ `npm run build`（exit 0、`dist/`）→ `npm run test`（framework 起動成功）。

---

### Stack 4: Astro 4+（content collections）

| # | パス | 役割 | 最低要件 |
|---|---|---|---|
| 1 | `package.json` | 依存・scripts | `dev` / `build` / `preview` を持つ。`astro` を依存に持つ |
| 2 | `astro.config.mjs` | Astro 設定 | integrations（react/vue/tailwind 等）を `defineConfig` で宣言 |
| 3 | `tsconfig.json` | TS 設定 | Astro 既定の `astro/tsconfigs/strict` を extends |
| 4 | `src/pages/index.astro` | トップページ | プレースホルダ UI |
| 5 | `src/layouts/` | レイアウト置場 | 最低 1 レイアウト（`<slot />` を含む） |
| 6 | `src/content/config.ts` | content collections 定義 | content 使用時は `defineCollection` + `z.object` スキーマ。未使用なら省略可 |
| 7 | `public/` | 静的アセット | ディレクトリ存在 |
| 8 | `.gitignore` | git 除外 | `dist/` `.astro/` `node_modules/` `.env*` |

**Smoke test**: `npm install` → `npm run dev`（`http://localhost:4321` が 200）→ `npm run build`（exit 0、`dist/`）→ `npm run preview`（200）。

---

### Stack 5: Python + FastAPI

| # | パス | 役割 | 最低要件 |
|---|---|---|---|
| 1 | `pyproject.toml` | 依存・ツール設定 | `fastapi` / `uvicorn` / `pydantic` を依存に持つ。`ruff` / `mypy` / `pytest` 設定を含む |
| 2 | `app/main.py` | エントリ | `app = FastAPI()` と最低 1 つの `@app.get("/health")` |
| 3 | `app/api/routes/` | ルート定義置場 | 空でも可（`__init__.py` 含む） |
| 4 | `app/core/config.py` | 設定 | `pydantic-settings` で `DATABASE_URL` / `SECRET_KEY` / `ENVIRONMENT` を読む |
| 5 | `app/models/` `app/schemas/` | ORM/Pydantic 層 | DB 使用時のみ。SQLAlchemy 2.0 想定 |
| 6 | `alembic.ini` + `migrations/` | マイグレーション | DB 使用時のみ。`alembic init` 生成物 |
| 7 | `tests/test_health.py` | 最小テスト | `/health` が 200 を返すことを検証 |
| 8 | `.env.example` | 環境変数雛形 | `DATABASE_URL` / `SECRET_KEY` / `ENVIRONMENT` のキー名 |
| 9 | `.gitignore` | git 除外 | `__pycache__/` `.venv/` `.env*` `.pytest_cache/` `.coverage` |

**Smoke test**: 依存導入（`uv sync` または `pip install -e .`）→ `uvicorn app.main:app --reload`（`http://localhost:8000/health` が 200）→ `ruff check .`（exit 0）→ `mypy app/`（exit 0）→ `pytest -v`（exit 0）。DB 使用時は `alembic upgrade head` も smoke に含める。

---

### Stack 6: Python + Django 5 + DRF

| # | パス | 役割 | 最低要件 |
|---|---|---|---|
| 1 | `pyproject.toml`（または `requirements.txt`） | 依存 | `django` / `djangorestframework` / `pytest-django` を持つ |
| 2 | `manage.py` | Django CLI | `django-admin startproject` 生成物 |
| 3 | `config/settings/base.py` | 共通設定 | `INSTALLED_APPS` に `rest_framework`、`DATABASES` を `DATABASE_URL` から読む |
| 4 | `config/settings/local.py` `production.py` | 環境別設定 | `base` を import して差分のみ定義 |
| 5 | `config/urls.py` | ルート URLconf | 最低 1 つの health エンドポイント |
| 6 | `apps/` | 機能アプリ置場 | 空でも可（ディレクトリ存在） |
| 7 | `tests/test_health.py` | 最小テスト | pytest-django で 1 エンドポイント検証 |
| 8 | `.env.example` | 環境変数雛形 | `SECRET_KEY` / `DATABASE_URL` / `DJANGO_SETTINGS_MODULE` |
| 9 | `.gitignore` | git 除外 | `__pycache__/` `.venv/` `.env*` `db.sqlite3` `staticfiles/` |

**Smoke test**: 依存導入 → `python manage.py migrate`（exit 0）→ `python manage.py runserver`（health が 200）→ `pytest`（exit 0）。

---

### Stack 7: Node.js + Express + TypeScript

| # | パス | 役割 | 最低要件 |
|---|---|---|---|
| 1 | `package.json` | 依存・scripts | `dev` / `build` / `start` / `test` / `lint` を持つ。`express` を依存に持つ |
| 2 | `tsconfig.json` | TS 設定 | `strict: true`、`outDir: "dist"` |
| 3 | `src/index.ts` | エントリ | Express app 起動、`GET /health` が 200 |
| 4 | `src/routes/` `src/controllers/` `src/services/` `src/middleware/` | 層分割 | 空でも可（ディレクトリ存在） |
| 5 | `src/types/` | 型定義置場 | 空でも可 |
| 6 | `tests/health.test.ts` | 最小テスト | supertest 等で `/health` 検証 |
| 7 | `.env.example` | 環境変数雛形 | `PORT` / `DATABASE_URL` / `JWT_SECRET` / `NODE_ENV` |
| 8 | `.gitignore` | git 除外 | `node_modules/` `dist/` `.env*` `coverage/` |

**Smoke test**: `npm install` → `npm run build`（exit 0、`dist/`）→ `npm run dev`（health が 200）→ `npm run lint`（exit 0）→ `npm run test`（exit 0）。Zod 等のバリデーションは選択肢として例示にとどめる。

---

### Stack 8: Go + Gin/Echo

| # | パス | 役割 | 最低要件 |
|---|---|---|---|
| 1 | `go.mod` | モジュール定義 | `module` 宣言と Go 1.21+。gin または echo を require |
| 2 | `cmd/api/main.go` | エントリ | HTTP サーバ起動、`GET /health` が 200 |
| 3 | `internal/handler/` `internal/service/` `internal/repository/` `internal/model/` | 層分割 | 空でも可（最低 `.go` ファイル or `.gitkeep`） |
| 4 | `pkg/` | 共有ユーティリティ | 空でも可 |
| 5 | `migrations/` | DB マイグレーション | DB 使用時のみ。golang-migrate 形式 |
| 6 | `internal/handler/health_test.go` | 最小テスト | testify で health ハンドラ検証 |
| 7 | `.env.example` | 環境変数雛形 | `PORT` / `DATABASE_URL` / `JWT_SECRET` |
| 8 | `.gitignore` | git 除外 | `bin/` `*.exe` `.env*` `vendor/`（vendor 運用時は調整） |

**Smoke test**: `go mod download` → `go build -o bin/api cmd/api/main.go`（exit 0）→ `go run cmd/api/main.go`（health が 200）→ `go vet ./...`（exit 0）→ `go test ./...`（exit 0）。

---

### Stack 9: Ruby on Rails 7+

| # | パス | 役割 | 最低要件 |
|---|---|---|---|
| 1 | `Gemfile` | 依存 | `rails` 7+、`rspec-rails` / `factory_bot_rails`、DB アダプタ（`pg`） |
| 2 | `config/application.rb` `config/environments/` | アプリ設定 | `rails new` 生成物 |
| 3 | `config/database.yml` | DB 設定 | `DATABASE_URL` 参照を含む |
| 4 | `config/routes.rb` | ルーティング | 最低 1 つの health ルート |
| 5 | `app/controllers/` `app/models/` `app/services/` | MVC + サービス層 | 標準生成物 + `services/` ディレクトリ |
| 6 | `spec/requests/health_spec.rb` | 最小テスト | RSpec で health が 200 |
| 7 | `.env.example` | 環境変数雛形 | `DATABASE_URL` / `SECRET_KEY_BASE` / `RAILS_ENV` |
| 8 | `.gitignore` | git 除外 | `/log/*` `/tmp/*` `.env*` `/storage/*` |

**Smoke test**: `bundle install` → `bin/rails db:migrate`（exit 0）→ `bin/rails server`（health が 200）→ `bundle exec rspec`（exit 0）。

---

### Stack 10: Expo (React Native) — SDK 54+ / Expo Router（v6.2.0 追加）

モバイル（iOS / Android）＋ Web を 1 コードベースで扱う唯一のクロスプラットフォーム stack。`create-expo-app` の default template（file-based routing / TypeScript / 3 platform 対応）を基準とする。前述 9 stack が Web/API 層なのに対し、本 stack は**ネイティブアプリ層**を担う。

> **Expo SDK 56+ の AI エージェント連携（観測経路の明示）**
> Expo SDK 56 以降、`create-expo-app` は AI エージェント用の設定ファイル（`AGENTS.md` / `CLAUDE.md` / `.claude/settings.json`）を**自動生成**する。本 stack はこれを DH 形式の必須生成ファイルとして取り込み、DH の CLAUDE.md 生成（L0 §6/§7）と**共存**させる（後述「DH との共存規約」）。観測元は Expo 公式ドキュメント [docs.expo.dev/agents/](https://docs.expo.dev/agents/) / [/skills/](https://docs.expo.dev/skills/) / [/eas/ai/mcp/](https://docs.expo.dev/eas/ai/mcp/)（2026-06 観測）。Expo は DH が scaffold する**対象技術**であり、DH と競合する Layer 3 方法論層ではないため `observed-peers.md` には登録しない。

| # | パス | 役割 | 最低要件 |
|---|---|---|---|
| 1 | `package.json` | 依存・scripts | `"main": "expo-router/entry"`。`scripts` に `start`（= `expo start`）/ `android` / `ios` / `web` / `lint`（= `expo lint`）を持つ。`expo` / `expo-router` / `react-native` を依存に持つ |
| 2 | `app.json`（または `app.config.ts`） | Expo アプリ設定 | `expo.name` / `expo.slug` / `expo.scheme`（deep link 用）/ `expo.plugins` に `expo-router` を含む。新アーキ前提なら `expo.newArchEnabled: true` |
| 3 | `tsconfig.json` | TS 設定 | `expo/tsconfig.base` を `extends`、`strict: true` |
| 4 | `app/_layout.tsx` | ルートレイアウト | expo-router の `<Stack>` または `<Tabs>` ナビゲータを返す |
| 5 | `app/index.tsx` | トップ画面 | プレースホルダ UI（起動エラーが出ないこと） |
| 6 | `components/` | UI コンポーネント置場 | 空でも可（ディレクトリ存在）。RN 標準ではなく `@expo/ui` 利用を選択肢として例示（最低要件には含めない） |
| 7 | `assets/` | アイコン・スプラッシュ等 | `app.json` の `icon` / `splash` が参照する画像が実体として存在（プレースホルダ可） |
| 8 | `.gitignore` | git 除外 | `node_modules/` `.expo/` `dist/` `*.orig.*` `.env*` `ios/` `android/`（CNG 運用時。bare 運用なら調整） |
| 9 | `AGENTS.md`（SDK 56+ の `create-expo-app` 生成物） | Expo 固有エージェント規約の Source of Truth | SDK バージョン・Expo 推奨パターン（`@expo/ui` / `expo/fetch` 等）への誘導を含む。SDK 55 以前で未生成の場合は L0 が最小版を生成 |

`package-lock.json` / `bun.lock` 等の lock ファイルは依存導入で生成されるため初期生成チェック対象外。`ios/` `android/` は CNG（Continuous Native Generation）運用では `expo prebuild` で都度生成するため初期生成チェック対象外。

#### DH との共存規約（CLAUDE.md / AGENTS.md / .claude/settings.json）

`create-expo-app`（SDK 56+）が生成する 3 ファイルと DH 生成物は、責務を分けて**共存**させる（上書きしない）：

| ファイル | 一次責務 | DH の扱い |
|---|---|---|
| `AGENTS.md` | Expo 固有ルール（SDK バージョン・`@expo/ui` / `expo/fetch` 等の推奨パターン）の Source of Truth | **残す**。Expo の知見を消さない |
| `CLAUDE.md` | エージェント RL（ルール）定義 | DH が生成する CLAUDE.md の `## 参照` に `@AGENTS.md` を import 行として含め、DH 固有 RL（SPEC/REGIME/DONT/sensors 参照・献上規約・モード差分）を**上乗せ**する。Expo 生成の最小 CLAUDE.md は DH 版に統合 |
| `.claude/settings.json` | Expo 公式プラグイン（Skills / MCP）の事前有効化 | **残す**。DH 固有設定（hooks 等）はマージで追記し、Expo プラグイン有効化を温存する |

Expo Skills（`/plugin install expo` 等）・Expo MCP Server は利用者の任意導入とし、本カタログでは最低要件に含めない（DH の scaffold は決定論的ファイル一覧に責務を絞るため）。導入手順は AGENTS.md / Expo 公式ドキュメントに委譲する。

#### Smoke test

`create-expo-app` は実機/シミュレータ起動を伴うため、CI でも通る**決定論的サブセット**を smoke の必須とする：

```bash
npm install                       # exit 0、lock 生成
npx expo lint                     # exit 0（lint 設定が呼べる状態）
npx tsc --noEmit                  # exit 0（型エラーなし）
npx expo export --platform web    # exit 0、dist/ 配下に web ビルド生成（バンドラ起動の確証）
```

実機/シミュレータ起動（`npx expo start` → Expo Go / dev client で画面到達）は**手動 smoke** とし、CI 必須には含めない（GUI 依存・環境依存のため）。EAS Build を使う場合は `npx eas build --platform <p> --profile preview` を別途 §7.4 自己検証の任意項目とし、本セッション環境では Expo MCP（`mcp__expo__build_*` / `workflow_*`）経由でビルド状況を観測できる。通らない場合は §7.4 自己検証の規約に従い失敗手順・理由・保留事由を明記して譲渡する。

#### DESIGN.md 連携（ネイティブ UI）

Expo は UI を含む stack のため `## DESIGN.md 連携` の対象。ただし Web の Playwright スクショ比較はそのままでは使えないため、視覚検証は (a) `npx expo export --platform web` 出力に対する Playwright、または (b) Maestro / Detox 等の RN E2E によるスクショ取得に読み替える。第 5 層 Vision 判定（UX Priority `standard` 以上で必須）は取得スクショ + DESIGN.md `## Do's and Don'ts` で同様に適用する。

---

### stack 未収載時の扱い

上記 10 stack（標準 + 追加 9）に該当しない構成（SvelteKit / 純 Node.js CLI / Rust 等）は、本カタログの **表形式（必須生成ファイル + 最低要件 + smoke test）に倣って L0 が当該プロジェクト用の一時チェックリストを `delivery/` 配下に起こす**。汎用化して本ファイルへ昇格するかは観測 → 候補化 → 人間承認（philosophy 第 8 条 3 段階モデル）を経る。

---

## Supabase ローカル開発（推奨バックエンド開発オプション、v5.18.0 追加）

上記 stack は主にフロントエンド／アプリ層の scaffold を扱う。バックエンドに **hosted Postgres / BaaS（特に Supabase）を使い、本番に消失 NG の私的データを持つ**プロジェクトでは、本番を汚さないための**ローカル優先開発フロー**を推奨オプションとして提示する。詳細プロトコル（推奨発動条件 / 前提確認 / 7 ステップワークフロー / セキュリティ規律）は `supabase-local-dev.md` を参照。

### scaffold への追加生成物（該当時）

S1 = DB 使用あり + 本番 Supabase 構成と判定された場合、§必須生成ファイル に加えて以下が **実体として** 揃う：

| パス | 役割 | 最低要件 |
|---|---|---|
| `supabase/config.toml` | ローカルスタック設定 | `supabase init` 生成物 |
| `supabase/migrations/` | スキーマ変更履歴（本番反映の唯一経路） | `supabase db pull` で本番スキーマ取り込み済（データは含めない） |
| `supabase/seed.sql` | ローカル専用ダミーデータ | `supabase db reset` で自動投入。本番非反映 |
| `.env.local` | ローカル接続情報（**`.gitignore` 必須**） | §必須生成ファイル #7 の `.env*` 除外で既にカバー。本番キーは混入禁止 |

### smoke test への追加

`supabase start` → Studio URL 到達 / `supabase db reset` exit 0 / `supabase db diff` 差分なし を §7.4 自己検証に含める。詳細は `supabase-local-dev.md`「Smoke Test 手順」。本セクションは Vite+TS+React+PWA 標準 stack の §必須生成ファイル 12 種を**置換せず**、バックエンド構成に応じた追加層として扱う。

---

## 業界叡智準拠の出力規約（Phase γ-i 連携、CTL ≥ 1、W5-Q2 採決追加）

Wave 5 W5-Q2 採決 (`council-2026-05-11T12:15:00Z-w5qb02`、B 段階組込、conf 0.72) で確定した scaffold-checklist の業界叡智準拠強化。`subphase-common-protocol.md` Phase γ-i フックが起動するプロジェクトでは、§必須生成ファイル に加えて以下の業界互換配置を **任意推奨** として観測する。**観測駆動、候補出力のみ、自動採用なし**（philosophy 第 8 条 3 段階モデル準拠）。

### ECC 互換配置（任意推奨）

利用者プロジェクトが Claude Code 利用前提の場合、ECC (Everything Claude Code) 互換配置を推奨配置として参照する。**強制ではなく、L1 出力規約への影響度高いため業界慣例として明示**。

| 配置パス | 役割 | 参照ソース |
|---|---|---|
| `~/.claude/agents/{agent-name}.md` | プロジェクト agent 定義（YAML frontmatter + system role） | ECC `agents-catalog.md` §2「agent 定義パターン」 |
| `~/.claude/skills/{skill-name}/SKILL.md` | プロジェクト skill 定義（progressive disclosure 規約準拠） | ECC `skills-pattern.md` |
| `.claude/settings.json` | プロジェクト固有設定（schema 準拠） | `https://json.schemastore.org/claude-code-settings.json` |
| `.claude/hooks.json` | hook 発動規約（6 event 採用、PR #76 + #81 で確定） | `crosscut-hook-observer` skill / Wave 1 PR #76 |

### Phase γ-i フックでの照合観点

scaffold-checklist の §必須生成ファイル 12 種が **生成済** に加えて、業界叡智準拠の出力規約として以下を Phase γ-i フックが観測：

| # | 観点 | 業界叡智ソース | match_type |
|---|---|---|---|
| 1 | プロジェクト agent 定義が `~/.claude/agents/{name}.md` に配置されているか（利用者プロジェクト側） | ECC `agents-catalog.md` | complementary |
| 2 | プロジェクト skill 定義が `~/.claude/skills/{name}/SKILL.md` 規約に従うか | ECC `skills-pattern.md` | complementary |
| 3 | `.claude/settings.json` が settings.schema に対し validate 成功するか | Claude Code settings schema | contradictory 検知用 |
| 4 | `.claude/hooks.json` の `adopted_events` が `crosscut-hook-observer` の `SUPPORTED_EVENTS` (bootstrap.py) と整合するか | DH 内部 + ECC `hooks-trigger-points.md` | contradictory 検知用 |

### 候補リスト出力例

```yaml
industry_wisdom_match_candidates:
  - source: "ECC skills-pattern.md / scaffold-checklist §業界叡智準拠"
    aspect: "skill 配置 (~/.claude/skills/{name}/SKILL.md)"
    spec_draft_reference: "SPEC.md §開発環境構成 .claude/skills/"
    match_type: "complementary"
    suggestion: "ECC では progressive disclosure 規約 (SKILL.md + references/ + assets/) が確立。本プロジェクトも同規約準拠で配置候補"
    confidence: 0.8
```

### 第 8 条 3 段階モデル準拠

- **観測**: 生成された scaffold ファイル群と ECC 互換配置の照合
- **候補化**: `industry_wisdom_match_candidates` リストとして Phase δ 差分サマリに含める
- **人間最終承認**: Phase δ でユーザー承認（自動採用なし、philosophy 第 6 条準拠）

### CTL 連動

- **CTL 0**: 本セクション inactive（観察温存、候補化も抑止）
- **CTL ≥ 1**: active、候補出力のみ

### 既存 §必須生成ファイル との関係

本セクションは **既存 12 種必須生成ファイル一覧に影響しない**。Vite+TS+React+PWA 標準 stack は不変、業界叡智準拠配置は **任意推奨観点として Phase γ-i フックが観測する追加層**。利用者プロジェクトの dev_mode (`local_only` / `github_assisted` / `autonomous`) や CTL に関わらず、本ファイル §必須生成ファイル のチェックリストはこれまで通り適用。

---

## dev-env-spec.md との責務分離

| ファイル | 責務 |
|---|---|
| `references/dev-env-spec.md` | 用語定義 / ファイル配置規則（参照権限マトリクス含む） / モード別差分（M1/M2/L2 の生成物） / コンテキスト注入戦略 / バージョニング規則 / 移行ノート |
| `references/scaffold-checklist.md`（本ファイル） | stack 別の生成必須ファイル一覧 / smoke test 手順 / 将来拡張ポイント |

両者は **直交関係**。`dev-env-spec.md` の「ファイル配置規則」は全 stack 共通の規約、本ファイルは stack 固有の必須生成物と検証手順を扱う。
