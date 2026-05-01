# INTENT

DH 本体の設計意図・新規概念の記録。

## 保留中の長期計画

### CI/CD 強化計画（2026-05-01 開始、保留中）

- **起源**: 下流プロジェクト（Next.js + Supabase 系、`apps/platform` 等を持つ dev_mode=github_assisted 確定済プロジェクト）からの献上ブレスト
- **保管場所**: `history/deliveries/2026-05-01-cicd-automation-brainstorm.md`
- **DH 一般化候補**: 10 カテゴリ × 多数選択肢のうち、DH 本体に一般化可能な議題を以下 5 つに集約
  1. **scaffold-checklist の CI 章追加**: `.github/workflows/ci.yml` 雛形（typecheck + lint + test の PR ゲート）を v5.1.0 標準 stack の必須生成ファイルに加える案
  2. **crosscut-* 段階稼働プロトコル**: 未稼働の dispatcher / implementer / drift / feedback-loop について dev_mode × CTL ごとの推奨稼働順を reference 化する案
  3. **「罠 → 検出器」一般化パターン**: プロジェクト固有の踏みやすい誤りを DONT.md に言語化し sensors/computational.md へ lint として載せる汎用フローを reference 化する案
  4. **自動化 LOC 予算ガイダンス**: 1 自動化 = 1 ファイル 200 行未満、自動化総量の本体 LOC × 1.5 上限等のガイダンスを philosophy or dev-env-spec に追加する案（Bus factor 軽減）
  5. **sensor 自動実行化**: markdown 手順書としての sensor を実行可能スクリプト化し VERIFICATION.md に machine-readable 結果を残す案
- **未消化の 7 質問（ブレスト原文 §5）**:
  - Q1 テストフレームワーク方針（Vitest / Playwright / Cucumber の 3 層採否）
  - Q2 自動化 LOC 上限の基準
  - Q3 crosscut-* 稼働順序
  - Q4 罠検出器の SPEC / docs / DONT 振り分け
  - Q5 production 切替と down migration（プロジェクト固有、DH 採用外）
  - Q6 Bus factor 対策と自動化増加の逆説
  - Q7 v5.2.0/v5.3.0 で送られた philosophy verifier の取り扱い（既決：v5.3.0 候補から外し継続検討）
- **保留理由**: 起点プロジェクトおよび harness 利用者側で「CI/CD で何のどこをチェックするか」の認識共有が未達。L0 spec-architect 原則「認識のズレがゼロになるまでレビューループを回す」に従い、ズレが残ったままの開発環境構築を避ける
- **次サイクル発動条件**:
  - (a) 利用者プロジェクト側で CI/CD の対象範囲（typecheck / lint / unit / E2E / drift / 罠検出 のいずれか以上）を具体化した HANDOFF が届く、または
  - (b) PR #30（v5.4.0 archeo-architect）merge 後の安定期に DH 本体側でドッグフード対象として再起動
- **PR #30 との関係**: 本計画は PR #30 と独立。両者ともに `history/INTENT.md` と他ファイルを触る場合は merge 後 rebase で整合させる。本サイクルでは PR #30 が予約した v5.4.0 を侵さないため版上げを行わない
- **当面のリリース対象**: なし（記録のみ）。実体改修は次サイクル以降の minor or 別 PR に委ねる

### Lifecycle → LC 命名変更計画（2026-05-01 開始、保留中）

- **起源**: 2026-05-01 サイクル中の対話（PR #31 上で CI/CD 動的調整を議論する過程で表面化）
- **問題**: DH 本体に 2 種類の `L` + 数字命名が共存し、文書内で衝突する
  - **Layer**: 5 層論の階層（L0 = spec-architect, L1 = autonomous-dev, L2 = orchestrator/integration-verifier）
  - **Lifecycle**: プロジェクトの成熟度（L=0 立ち上げ、L=1 機能拡張期、L=2 安定運用期、L=3+ 本番）
- **混同の実例**: 「L=2 のプロジェクトで L2 が起動する」のような文に Layer 2 起動条件と Lifecycle 2 が同時に登場し、読み手が文脈で判別する負担が生じる
- **改名提案**: `Lifecycle L=N` → `LC=N`（`LC` = LifeCycle 略記）
  - Layer は `L0/L1/L2` のまま維持
  - Lifecycle は `LC=0/LC=1/LC=2/LC=3` に統一
- **影響範囲（暫定推定）**:
  - `philosophy.md` Lifecycle 言及箇所
  - `references/regime-assessment.md` Lifecycle 判定章
  - `references/dev-env-spec.md` Lifecycle 別構成
  - 各 SKILL.md の振り返り儀式条件（特に `layer0-spec-architect/SKILL.md`）
  - `DIMENSIONS.md` Lifecycle 章（あれば）
  - `references/scaffold-checklist.md` Lifecycle 別生成物
- **保留理由**: 本 PR (#31) と並行 PR #30（v5.4.0 archeo-architect）はどちらも上記ファイル群の一部を触る、または触る可能性がある。命名変更は全 grep 系の横断改修であり、両 PR が merge される前に流すと conflict が大量発生する
- **次サイクル発動条件**:
  - (a) PR #30 merge **かつ** PR #31 merge の両方が完了し、master が安定状態になった後
  - (b) 命名変更を「`Lifecycle` → `LC` 一括置換 + 用語表更新 + 後方互換注記」に絞り込んだ単独 PR として独立ブランチで実施
- **PR スコープの予測**: 単独 PR、minor 昇格不要（命名整備のみ、機能変更なし）。CHANGELOG にメモ程度。
- **当面のリリース対象**: なし（記録のみ）

### scaffold-checklist CI 章 構造ドラフト（2026-05-01 起稿、保留中）

CI/CD 強化計画 (1) の解像度を上げる**構造案**。`references/scaffold-checklist.md` への実装はまだ行わず、ここに叩き台として保管する。本節以降は LC 命名変更計画（前節）の決定に従い `LC=N` 表記を先行採用する。

#### 設計原則

1. **L0 は型と最小実装を渡す**: `.github/workflows/ci.yml` の最小 YAML を雛形として配布する。L1 が中身を埋める（テスト本体・キャッシュ最適化）
2. **動的判定**: CI 構成は `(LC, dev_mode, stack)` の関数として決まる。`dev_mode = local_only` では物理的に CI 不在
3. **三段構えの第 2 段専用**: 第 1 段（IDE / pre-commit）と第 3 段（AI reviewer）は別責務。CI 章は機械化可能なものだけを扱う
4. **scaffold-checklist の §0 受け入れ基準を継承**: 「実体ファイルが存在しなければならない」原則を CI YAML にも適用

#### 動的構成テーブル（dev_mode = `github_assisted` 以上）

| LC | 検査セット | 実体ファイル要件 | jobs 数 |
|---|---|---|---|
| `LC=0`（立ち上げ初期） | typecheck のみ（PR ゲートとせず通知のみ） | `.github/workflows/typecheck.yml`（最小 15 行） | 1 |
| `LC=1`（機能拡張期） | typecheck + lint + unit test（PR ゲート） | `.github/workflows/ci.yml`（30〜50 行） | 3 |
| `LC=2`（安定運用期） | + drift 検出 + 罠検出器 + E2E（夜間 schedule） | `.github/workflows/ci.yml` + `.github/workflows/nightly.yml` | 5+ |
| `LC=3+`（本番運用） | + security scan + perf budget + canary | 上記 + `.github/workflows/release.yml` | 8+ |

`dev_mode = local_only` では本テーブルは適用されず、代わりに `git hooks/pre-commit` のみ規定（別章として将来追加）。

#### LC=1 雛形（最低共通解の例示）

```yaml
# .github/workflows/ci.yml （L0 が配布する最小骨格）
name: CI
on:
  pull_request:
    branches: [master, main]
jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm typecheck
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm test
```

備考: scaffold-checklist v5.1.0 標準 stack の `package.json` `scripts.dev/build/test` 規約と整合する。`pnpm typecheck` `pnpm lint` の存在は同 stack で既に必須生成物に内包されているため追加要件なし。

#### スタック別差分（将来 minor で）

scaffold-checklist 既存の「将来拡張ポイント」表（Next.js / Vue 3 / Node CLI / Astro / SvelteKit）と並走して、各 stack の CI 雛形差分を minor で追加：

| stack | 主な差分 |
|---|---|
| Next.js (App Router) | `pnpm build` を job に追加（Edge runtime ビルド検証）、Vercel preview deploy 連携 |
| Vue 3 + Vite | Vue 系 lint plugin の有無、E2E は Cypress も選択肢 |
| Node CLI | jsdom 不要、`pnpm pack` の job 追加 |
| Astro | `astro check` の job、image optimization 検証 |
| SvelteKit | `svelte-check` の job、adapter-auto の build 検証 |

#### 振り返り儀式での連動

`spec-architect` の振り返り儀式（`ritual-protocol.md` 規定）に LC 遷移検出ステップを追加し、検出時に本ドラフトの動的構成テーブルと現行 `.github/workflows/` を diff して人間に提示する流れを構築する。これは別 reference（仮称 `references/ci-evolution-protocol.md`）として将来追加する想定。

#### Smoke Test との関係

scaffold-checklist 既存の **smoke test 手順**（`pnpm install / dev / build / test`）が CI で機械的に走る形になる。`§7.4 自己検証` の「scaffold smoke test」と CI の `test` job は同じスクリプトを呼ぶため、L0 自己検証と CI の検査内容が二重化されない。

#### 残課題（次サイクル以降）

- 現行 `.gitignore` に `.github/workflows/*.yml` の lint 規約がない → CI YAML 自身の linter（`actionlint` 等）採否の判断
- `secrets` の扱い（ベースは secrets 不要だが、E2E で外部 API key が必要なケースの規約）
- self-hosted runner の使用可否規約
- workflow キャッシュ戦略の標準化（`actions/cache` 採否）

### crosscut-verifier-drift の CI 降下診断（2026-05-01、保留中）

CI/CD 強化計画 (2)「crosscut-* 段階稼働プロトコル」の解像度を上げる**診断結果**。現行 `crosscut-verifier-drift` skill（`.claude/skills/crosscut-verifier-drift/`）は CTL ≥ 1 で発動する追加層 verifier だが、その内部処理を「第 2 段（CI、AI 不要）」「第 3 段（AI reviewer）」に切り分けたときの分担を診断する。

#### 現行 drift verifier の 5 種別

| # | 種別 | 軽量モード (CTL-1) | フルモード (CTL-2/3) |
|---|---|---|---|
| 1 | `spec_unrecorded_addition` | キーワード grep | 機能境界 ast 解析 |
| 2 | `adr_unapproved_removal` | （未明記、grep 想定） | （未明記、意味判定想定） |
| 3 | `dont_violation` | DONT.md 文字列 grep | 意味的類似度判定 |
| 4 | `signature_drift` | git diff のみ | TypeScript signature diff（型情報考慮） |
| 5 | `ux_drift` | sensors/interaction-cost ログ参照 | 同左 + 統計的有意性チェック |

#### CI 降下可否マトリクス（診断結果）

| # | 種別 | 軽量 → CI? | フル → CI? | 残る AI 判定 |
|---|---|---|---|---|
| 1 | `spec_unrecorded_addition` | **○** SPEC.md 内の機能 ID と diff 内のシンボル名を grep 比較 | △ 「機能境界」は意味判定 → AI 残置 | 「機能の境界が同一か」 |
| 2 | `adr_unapproved_removal` | **○** 削除行と ADR 内の決定 ID を grep 比較 | △ 「等価変更か破壊的削除か」は AI | 「削除の意味的影響」 |
| 3 | `dont_violation` | **○** DONT.md の禁止パターン（正規表現化前提）と diff を照合 | × 意味的類似度は AI 必須 | 「DONT に書かれていないが趣旨に反するか」 |
| 4 | `signature_drift` | **◎** TS なら `tsc --noEmit` + api-extractor、Rust なら `cargo public-api` で完全機械化 | **◎** 同上 | なし（完全 CI 化可能） |
| 5 | `ux_drift` | **◎** sensors ログ + Lighthouse CI で完全機械化 | **◎** 統計検定スクリプト | なし（完全 CI 化可能） |

凡例: **◎** 完全機械化可、**○** 軽量部分のみ機械化可、△ 一部機械化、× 機械化不可（AI 残置）

#### 機械化に必要な前提条件（書式規約整備）

軽量モードを CI に降ろすには、以下の書式規約が前提条件として整備されていなければならない（現状未整備または不完全）：

| 規約 | 要件 | 現状 |
|---|---|---|
| SPEC.md の機能 ID 規約 | `FUNC-001` 形式等の機械可読 ID を機能ごとに付与 | 不明（プロジェクト依存） |
| ADR の決定 ID 規約 | `ADR-NNN` 形式の決定 ID と「決定／却下」状態の機械可読化 | 不明（プロジェクト依存） |
| DONT.md の禁止パターン規約 | 禁止項目に正規表現またはキーワードを併記（例: 「`console.log(` 禁止」） | 不明（多くは自然文） |
| sensors/interaction-cost ログ形式 | UX メトリクス JSON 出力規約 | sensors/interaction-cost.md で規定（既存） |

→ **drift verifier の CI 降下は、SPEC/ADR/DONT の書式規約整備を伴う構造改修**であり、軽率な機械化は誤検出を量産する。

#### 提案する二段化構造（次サイクル以降の改修像）

```
PR push
  ↓
[第 2 段 CI]
  ├── scripts/drift-check-lightweight.sh （pure shell, AI 不要）
  │     ├── signature_drift（tsc --noEmit + api-extractor diff）
  │     ├── ux_drift（Lighthouse CI + sensors ログ照合）
  │     ├── spec_unrecorded_addition（軽量 grep）
  │     ├── adr_unapproved_removal（軽量 grep）
  │     └── dont_violation（軽量 grep、正規表現規約済の場合のみ）
  │     → delivery/DRIFT-REPORT-LIGHT.md
  ↓
[第 3 段 AI reviewer]
  ├── crosscut-verifier-drift skill 起動（CC runtime）
  │     ├── 機能境界 ast 解析（spec_unrecorded_addition フル）
  │     ├── 意味的類似度判定（dont_violation フル）
  │     ├── ADR 意味判定（adr_unapproved_removal フル）
  │     └── DRIFT-REPORT-LIGHT.md の擬陽性／真陽性判定
  │     → delivery/DRIFT-REPORT.md（最終）
  ↓
[crosscut-feedback-loop へ還流]
```

利点:
- CI 段で擬陽性を含めた**早期検出**、AI 段で擬陽性除去と意味判定（context 節約）
- CTL-0 プロジェクト（drift skill 不発動）でも CI 段の軽量チェックは独立して走る選択肢が生じる
- skill が CC runtime 不在の環境でも、CI 段の最低限は機能する

#### 残課題

- 現行 `templates/.github/workflows/spec-drift.yml` は「skill 起動を CI 上で行う前提」のテンプレで、CI runtime に CC を要求する。本診断の二段化案を採るなら、このテンプレを `spec-drift-lightweight.yml`（pure shell）と `spec-drift-full.yml`（CC runtime 必要）に分離する必要がある
- DONT.md の正規表現化は全プロジェクトに義務付けるか、「機械検査用 DONT 拡張規約」として opt-in にするかの判断が残る
- v5.0.0 既存仕様の改修となるため、minor 昇格 + Council 諮問の対象
- 本診断は読み取りのみで `crosscut-verifier-drift` 本体には変更を加えていない。実装は別 PR

## v5.3.0 で追加された概念

### 1 機能完遂の自律駆動 WF を「形状単一・薄い基底」として確定

HANDOFF「1 機能完遂の自律駆動 WF 設計」2026-04-30 を起源とする L0 設計判断。
論点 1（WF 基底）/ 論点 2（献上トリガー 4 種）/ 論点 3（WF 選択責任）の 3 件を
Council 合議 (`council-2026-04-30T14:30:00Z-wfsurf1` / `council-2026-04-30T14:50:00Z-wfbase1`) と
実装者裁量（論点 3）で確定し、AD-015 / AD-016 / AD-017 に記録した。

設計意図の核：

**(a) 機能タイプ別 WF 群を作らない**。bug-fix / 新規機能 / リファクタ / 仕様改訂等は
`.claude/skills/layer1-autonomous-dev/SKILL.md` §4「実装タスク分解」内で扱う context 差異であって、独立 WF を生成する分業軸ではない。
これは philosophy.md §1 フラクタル原則 P1（同型再帰）が要求する「形状単一性」を運用原則として
組み込む判断である。職種別分業（フロント/バック/SRE 等）が職能のサイロ化を生むのと同型に、
機能タイプ別 WF 群は 5 年スパンで「タイプ N+1 の追加要求」を再発させる罠を持つ。
当面は単一 WF + 動的 context 注入で吸収し、観測（同一 override パターンの 3 機能タイプ以上での
反復）が閾値を超えた場合のみ Council 経由で基底側引き上げを再諮問する。

**(b) 既存 §処理フローが thin baseline を充足している**。
`layer1-autonomous-dev/SKILL.md §処理フロー（1〜8）` は HANDOFF が要求する「薄い基底」を
既に満たしている。新規 WF テンプレートを追加しない判断は、既存実装への信頼の表明であり、
かつ YAGNI 原則と整合する。

**(c) 献上経路を 4 分類化して情報純度を上げる**。
従来 Type A（仕様レビュー結果）に詰め込まれていた「AI 自己解決不能な技術的例外」を
Type D（異常献上）として分離する。仕様起因（Type A → L0 差し戻し）と
技術例外（Type D → 人間判断要請）は本質的に異なる救済経路であり、混同は P3 責務分離違反。

**(d) WF 選択責任は問題化しない**。
WF が単一形状で確定したため、「どの WF を起動するか」という選択問題が構造的に消失する。
残課題（機能タイプ誤認 / モード誤判定 / 権限・CTL 誤り）はすべて既存メカニズム
（Type C / 体制事後評価 / Type D）で吸収可能。新規ディスパッチャ等は不要。

### v6.0.0 候補として温存される思想拡張

論点 1 で哲学者が提示した第 3 の道「**単一 WF + 動的 context 注入**」を、現行 v5.3.0 の
運用原則を超える形での実装案として v6.0.0 major 候補に温存する。これは context engineering
の中核に WF 設計を据え直す思想転換であり、minor 改修では実装し得ない。

論点 2 で哲学者が提示した「**献上 3 軸構造**（トリガー × 中身 × 権限）」を philosophy 第 8 条
候補（第 7 条＝次元論と D4 の独立性 と並列の「献上 3 軸の存在論」）として温存する。
Type D 単純追加は二項分類の罠（Type E/F/G の追加要求が将来再発する可能性）を構造的に
解消できないため、3 軸構造への昇格を v6.0.0 major 昇格時に併合検討する。

## v5.2.0 で追加された概念

### 5 次元論（D1〜D5）の確立

dialog-harness は従来「メタスキル」「ユーザーハーネス」等の語彙で自身を語ってきたが、
個別の検証機構（5 層検出スタック / crosscut-verifier-drift / §7.4 自己検証等）が
それぞれどの抽象階層を対象にしているかが暗黙のままだった。

PR #19 後の HANDOFF（DH 自己検証機構ブレスト、2026-04-29）と Council 合議
（invocation_id: council-2026-04-29T21:00:00Z-d4mtr1）を経て、5 次元論を確立する：

| 次元 | 名称 | 実体 |
|---|---|---|
| D1 | ソースコード | プロジェクト実装ファイル群 |
| D2 | 開発環境 | D1 の足場（package.json / vite.config / sensors / SPEC.md 等） |
| D3 | 配布 skill | 利用者プロジェクトに配置される `.claude/skills/` インスタンス |
| **D4** | **マスタ skill（メタスキル）** | **dialog-harness リポジトリ内 skill マスタ定義** |
| D5 | Meta モニタリング層 | D4 を外側から監視する人間（自動化禁止） |

機械可読命名は D-numbering（D1〜D5）を使用。思想文書では `meta-layer` / `meta-meta-layer`
等の階層形容詞を併走させる二重命名を採用（DH の二層性 = 仕様核 + 対話的成長領域 と整合）。

### D4 検査機構（harness-verifier）の独立配置

DH 本体は v5.1.0 まで D2 / D3 の検証機構を完備していたが、**D4 自身の整合性検査は不在**だった
（靴屋の靴問題）。フラクタル原則 P1 の自然な拡張として「規律の自己相似性」を導入し、
DH が自身に課す規律と同等の規律を自身に課す。

ただし D4 検査機構を `.claude/skills/` 配下の crosscut-* skill として実装すると
**自己言及パラドックス**（自身が壊れたら自身を検査できない循環）が生じる。
これを構造的に回避するため、**DH 本体と並列のリポジトリルート直下に独立配置**する：

```
dialog-harness/
├── .claude/skills/    # DH 本体（D4）
└── harness-verifier/  # D4 検査機構（独立）
```

### 自己言及パラドックスの構造的回避（D5 を人間で止める）

D4 検査機構（harness-verifier）の検査結果を **自動的に DH 本体へフィードバックする回路は意図的に作らない**。
そこを自動化すると、D4 と D5 の間に新たな自己言及ループが発生し、再びパラドックスに陥る。
D5（人間）は機械が代替できない判定者として最外殻に固定される。
これは Russell タイプ理論・Gödel 不完全性定理と同型の構造判断であり、
philosophy.md 第 6 条「人間 ≒ Council」原則とも整合する。

将来 v6.0.0 で major 昇格する際、philosophy.md 第 7 条「次元論と D4 の独立性」として
本体に組み込む候補（v5.2.0 では PHILOSOPHY.md に閉じる）。

## v5.1.0 で追加された概念

### L0 charter 達成可能性の確保

PR #19 テストレビュー（シナリオ「ケロぴの森」）で、L0（spec-architect）の charter「AI 自律駆動開発が可能な開発環境の構築」が達成されないまま L1 へ譲渡され得る状態が判明した。SPEC.md / DONT.md / REGIME.md のドキュメント生成だけが完了し、scaffold（package.json 等の実行可能ファイル）が一切生成されない状態でも、従来の L0 完了判定では PASS となっていた。

v5.1.0 はこの欠陥を「**完了基準の再定義**」と「**Pre-flight 必読化**」と「**実行可能性の機械チェック（§7.4）**」の 3 軸で解消する。L0 完了 = ドキュメント生成 + scaffold 実体 + smoke test + 自己検証 PASS。これを下回る状態で L1 譲渡することは原則違反として明文化された。

### Pre-flight 必読化（読まずに進行禁止）

従来の SKILL.md は「詳細は references/X.md を参照」という参照表現にとどまっていた。v5.1.0 では主要ステップ（§1.5 / §3.5 / §4 / §6 / §7）の冒頭に「**Pre-flight: 起動前に X を必読**」を 1 行ずつ追加した。これは spec §0 受け入れ基準 4 とリンクし、Pre-flight 充足は §7.4 で逐項チェックされる。

「参照」と「必読」の差は運用上致命的。AI が SKILL.md だけを読んで進む（references を読み飛ばす）パターンを排除する目的で、命令形 + 違反明記 + 自己検証チェック項目化、の 3 点セットで運用する。

### Scaffold checklist（stack 別の生成必須リスト）

dev-env-spec.md は「ファイル配置規則」（全 stack 共通の規約）を扱うが、stack 固有の必須生成ファイルリストと smoke test 手順は不在だった。v5.1.0 では references/scaffold-checklist.md を新設し、「v5.1.0 標準 stack = Vite + TypeScript + React + PWA」の必須生成ファイル 12 種と smoke test 4 コマンドを規定する。

将来 minor で stack 追加（Next.js / Vue / Astro / SvelteKit / 純 Node CLI 等）するための「将来拡張ポイント」も併記。stack 選択軸は ARC + dev_mode + チーム軸（v5.x で追加予定）と整合させる。

### §7.4 自己検証ステップ

L0 完了判定の機械チェック化。broken reference / scaffold smoke test / DONT 自己照合 / Pre-flight 充足 / 受け入れ基準充足の 5 項目をチェックボックス形式で配置。FAIL があれば §7（出力）に進まず原因解消する。shell script 雛形は配置せず、L0 が ls / grep / cat 等の手作業で確認する粒度に絞ることで、人間運用の前提（人間は手を動かさない）を破らない。

5 項目は §0 受け入れ基準 4 条件と一対一に対応するように設計され、「自己検証で何をチェックすべきか」の暗黙仕様を明示化した。

## v5.0.0 で追加された概念

### dev_mode 軸

GitHub 連携前提の自律駆動開発を 3 段階で表現する軸。

| モード | 位置づけ |
|---|---|
| local_only | GitHub 不使用。DH ベースのみで完結 |
| github_assisted | GitHub Issue / PR は使うが、自動化は限定的。人間レビュー必須 |
| github_autonomous | claude-code-action 経由で自律実装、CTL 育成と連動して段階的に人間関与を縮小 |

理想形は github_autonomous + CTL-3 で「人間関与は L0 のみ」。

### CTL 連動の段階的自動化

仕様 1〜4 すべてに CTL-0/1/2/3 の動作分岐を組み込み、Council 判定の蓄積に応じて自動化度が上がる仕組み。CTL 昇格は量（判定件数）+ 質（一致率・override 率）のハイブリッド判定。退行（CTL 降格）も儀式で扱う。

### crosscut- prefix（Level A 第二の命名規則）

`layerN-` prefix と並列の Level A 識別子。3 層（L0/L1/L2）のいずれにも属さず、全層から呼ばれる横断機構を示す。

| Level A prefix | 意味 |
|---|---|
| `layerN-` | 特定 Layer 専属 skill |
| `crosscut-` | 全 Layer 横断 skill |

### 4 仕様（GitHub 連携の方法論化）

| 仕様 | skill | 役割 |
|---|---|---|
| 仕様 1 | crosscut-issue-dispatcher | SPEC/ADR 差分から Issue 生成 |
| 仕様 2 | crosscut-issue-implementer | Issue → CC 実装起動（claude-code-action 経由可） |
| 仕様 3 | crosscut-verifier-drift / -philosophy | drift 検知 + 思想検証（philosophy は v5.1.0 placeholder） |
| 仕様 4 | crosscut-feedback-loop | 検証結果を設計層・実装層・L0 に還流 |

4 仕様は同型構造（CTL 連動 / mode 別動作 / 還流ポイント明示）を持ち、5 本柱 P1（フラクタル原則）を skill レベルで発現する。
