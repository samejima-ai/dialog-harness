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
