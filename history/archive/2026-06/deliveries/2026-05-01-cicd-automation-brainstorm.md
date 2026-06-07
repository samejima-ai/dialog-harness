# BRAINSTORM — 自動化戦略の網羅的探索（L0 spec-architect 向け献上）

> **保存メモ（dialog-harness 側）**:
> - 本ファイルは下流プロジェクト（`apps/platform` / `supabase/migrations` / `scripts/lint-rls-recursion.mjs` 等を持つ Next.js + Supabase 系プロジェクト、dev_mode=github_assisted 確定済）からの献上ブレストを、DH 本体（D4 マスタスキル）側で**設計参照資料**として保管したもの。
> - DH 本体は `apps/` 等のディレクトリを持たないため、本文中のパス参照は下流プロジェクトの文脈で読むこと。
> - 採用判断は別途 DH 側の `history/INTENT.md` および `references/scaffold-checklist.md` 等に反映される（2026-05-01 サイクル、branch `claude/enhance-l0-cicd-xXM4h`）。
> - 本文中の `[SPEC.md](http://SPEC.md)` 等の自己参照リンクは送信時に自動付与された壊れたリンクだが、保管時の改変を避けるため原文ママとする。
> - **原文保管原則**: 本ファイルは下流プロジェクト発のブレスト原文を編集せず保管する（archeo-architect の意図保全原則に準ずる）。したがって、本文中には以下が含まれうる：(a) 当時の DH 計画認識（例: `crosscut-verifier-philosophy` を「v5.1.0 minor 改修で本実装」と記述）が現行ロードマップと乖離する箇所、(b) markdown 構文の不備（先頭 `||` の表記 等）、(c) 用語の表記ゆれ（`sensors/computational` 等の拡張子省略）。これらは「ブレストが書かれた時点でのスナップショット」として保持され、現行 DH の正しい状態は `docs/migration-guide-v5.x.md` および各 SKILL.md の最新版を参照すること。

---

**サイクル**: 2026-05-01 自動化ブレスト（規模分析の延長）
**献上元スキル**: 非定型対話（layer1-autonomous-dev でも layer0-spec-architect でもない、CC 主タスクの一環）
**判定**: 未判定（ブレスト段階。SPEC 化 / DONT 化 / 却下の振り分けは L0 に委ねる）
**Council 発動**: 未発動（ブレストでは判断点を確定させないため、Council は L0 が必要に応じて起動）
**前提**: 2026-05-01 規模総評で「自動テストの不在」を唯一の明確な穴として指摘。これを起点に自動化全般を網羅的に探索する。

> **重要**: 本文書は **「ブレスト = 決定前の選択肢羅列」** であり、[SPEC.md](http://SPEC.md) / [DONT.md](http://DONT.md) への直接反映を意図しない。L0 spec-architect が対話を通じて取捨選択し、確定したものだけが [INTENT.md](http://INTENT.md) → [SPEC.md](http://SPEC.md) に昇格する。

---

## 1. 現状の自動化マップ（事実確認）

### 1.1 既に自動化されているもの

| 領域 | 仕組み | 行数 | 起動契機 |
|---|---|---:|---|
| RLS recursion lint | `scripts/lint-rls-recursion.mjs` | 153 | `pnpm lint:rls`（手動） |
| 内部ルーティング lint | `scripts/lint-internal-routing.mjs` | 155 | `pnpm lint:routing`（手動） |
| News ingest | `scripts/ingest-news-articles.mjs` | 271 | `pnpm news:ingest`（手動） |
| DB 型生成 | Supabase introspection → `database.types.ts` | 自動 | `supabase gen types`（手動） |
| Turbo タスク並列化 | `turbo.json` | 設定 | `pnpm dev/build/lint/typecheck` |
| Harness skill 起動 | Claude Code の Skill メカニズム | — | description マッチで自動 |
| Sensor 検証 | `sensors/[computational.md](http://computational.md)` `sensors/[inferential.md](http://inferential.md)` | 170 | layer1-autonomous-dev の献上前ゲート |
| Council 起動 | `crosscut-council` skill | — | confidence < 0.6 / trade-off 検出時 |

### 1.2 自動化されていない / 半自動なもの

| 領域 | 現状 | 痛みの程度 |
|---|---|---|
| **ユニット/結合テスト** | `"test": "echo 'no tests yet' && exit 0"` | 🔴 高（回帰検出が人間 review 依存） |
| **E2E テスト** | `scripts/e2e-probe-*.mjs` 9本（手動探査ツール） | 🟡 中（CI で回らない） |
| **CI/CD パイプライン** | `.github/workflows/` 未確認（要調査） | 🟡 中 |
| **Migration validation** | RLS lint のみ。down migration / blue-green なし | 🟡 中（v3.0 再構築期は許容範囲） |
| **Drift 検出（SPEC ↔ 実装）** | `crosscut-verifier-drift` skill 存在するが未稼働 | 🟡 中 |
| **Schema ↔ Zod 整合検証** | 手動（`gen:types` 後の目視） | 🟡 中 |
| **Doc-ARC L1→L2 参照方向 lint** | 規約は [CLAUDE.md](http://CLAUDE.md) にあるが自動検証なし | 🟢 低 |
| **history/ アーカイブ** | 手動。クォーター戦略未確立 | 🟢 低（現時点） |
| **authz-matrix ↔ middleware ↔ RLS 三角整合** | 手動。3 箇所同期は腐りやすい | 🟡 中 |
| **Bundle size / 依存予算** | 計測なし | 🟢 低（規模小） |
| **Secret scanning** | git-secrets 等の導入なし | 🟡 中 |
| **Pre-commit hook** | 設定なし | 🟢 低（Council/sensor で代替） |

### 1.3 既に harness 側で用意されている自動化スキル（未稼働）

| スキル | 機能 | 稼働条件 |
|---|---|---|
| `crosscut-issue-dispatcher` | SPEC/ADR 差分から GitHub Issue を自動生成 | `dev_mode >= github_assisted` |
| `crosscut-issue-implementer` | Issue → AI 実装起動（worktree or Actions） | `dev_mode >= github_assisted` |
| `crosscut-feedback-loop` | 検証層で発覚した問題を SPEC/ADR/L0 へ還流 | CTL 連動 |
| `crosscut-verifier-drift` | 実装の SPEC 逸脱を CI で検出 | CTL ≥ 1 |
| `crosscut-verifier-philosophy` | 5本柱整合検証 | **v5.0.0 では発動禁止**（v5.1.0 minor 改修で本実装） |

`[REGIME.md](http://REGIME.md)` を確認すると本リポジトリは `dev_mode = github_assisted` 確定済（前サイクル `20260429_dh_v5_1_0_[sync.md](http://sync.md)`）なので、**dispatcher/implementer/feedback-loop/drift の 4 つは即時稼働可能**な状態にある。

---

## 2. ブレスト：自動化候補の網羅

各カテゴリで**選択肢を併記**し、トレードオフのみ示す。決定は L0 に委ねる。

### 2.1 テスト自動化（最優先候補）

#### 選択肢 A: Vitest + React Testing Library で薄く始める
- **対象**: Zod schema validation、`packages/supabase/src/utils/`、`apps/platform/lib/`
- **量**: 50〜150 ケース（schemas 32 ファイル × 2〜3 ケース）
- **得**: ビルド時間 +10〜30 秒、回帰検出が型レベルで効く
- **失**: UI コンポーネントは別途 RTL 必要
- **harness 整合**: `sensors/[computational.md](http://computational.md)` を Vitest で形式化できる

#### 選択肢 B: Playwright で E2E を CI に乗せる
- **対象**: 既存 `scripts/e2e-probe-*.mjs` を Playwright spec に翻訳
- **量**: 9 シナリオ
- **得**: ユーザー観点の回帰検出が強い
- **失**: 実行 5〜15 分、Supabase シードが必要、flaky 化リスク
- **harness 整合**: `sensors/[inferential.md](http://inferential.md)` の自動化版になり得る

#### 選択肢 C: Cucumber/Gherkin で `spec/invariants.feature` を実行可能化
- **対象**: 既存 253 行の `.feature` ファイル
- **量**: 既存記述を step definition で実装
- **得**: SPEC が直接実行可能になる（最も harness 哲学に合致）
- **失**: TypeScript Cucumber は周辺ツールが弱い、学習コスト
- **harness 整合**: ◎（SPEC ↔ test の 1:1 対応が成立）

#### 選択肢 D: 何もしない（人間 review + sensor で十分とする）
- **得**: 現状維持、追加メンテなし
- **失**: 規模拡大で破綻、AI 駆動成熟度 S+ への到達不可
- **harness 整合**: ✗（sensor が静的解析依存になり、動作回帰を捉えられない）

#### 仮の組み合わせ
A + C が harness 哲学に最も合致。B は段階導入（v3.1 以降）。

### 2.2 CI/CD パイプライン

#### 選択肢 A: GitHub Actions で typecheck + lint:rls + lint:routing を PR ゲート化
- **量**: workflow 1〜2 ファイル
- **得**: 既存 lint 資産が PR で自動執行、人間 review 負荷軽減
- **失**: GitHub minutes 消費（小規模なら無視できる）

#### 選択肢 B: A に加えて Supabase migration の dry-run を PR で実行
- **得**: migration の構文エラー / 衝突を事前検出
- **失**: Supabase shadow DB 設定が必要、CI 時間 +30〜60 秒

#### 選択肢 C: A + B + Vercel preview deploy の自動化
- **得**: PR ごとにレビュー可能な URL
- **失**: Vercel preview の cookie 分離（罠F）への教育が必要

#### 選択肢 D: GitLab / Cloud Build / Buildkite に変える
- **失**: GitHub Issues 連携の harness（dispatcher/implementer）を捨てることになる → 却下推奨

#### 仮の組み合わせ
A → B → C の段階導入。A は即実装可能。

### 2.3 Drift 検出の稼働化

`crosscut-verifier-drift` を稼働させる場合の選択肢。

#### 選択肢 A: PR 作成時に [SPEC.md](http://SPEC.md) ↔ 実装の差分検出を自動実行
- **検出対象**: SPEC 記載の機能 ID（F1-1 等）が実装に存在するか、authz-matrix ↔ middleware の整合
- **実装**: GitHub Action + harness skill 起動
- **得**: 仕様書腐敗の早期発見
- **失**: false positive のチューニング期間が必要

#### 選択肢 B: 週次バッチで drift レポートを自動生成
- **得**: PR 単位より低負荷、週次の振り返りに直結
- **失**: 検出遅延（1週間）

#### 選択肢 C: 手動起動（`/drift-check` 相当）
- **得**: 発動コスト最低
- **失**: 忘れる、稼働率が下がる

#### 仮の組み合わせ
A を main 派、B を保険として併用。

### 2.4 Schema/型同期の自動化

#### 選択肢 A: pre-push hook で `supabase gen types` を強制実行
- **得**: `database.types.ts` の腐敗を防止
- **失**: hook 設定が個人環境依存（罠化リスク）

#### 選択肢 B: CI で `database.types.ts` の再生成 → diff があれば fail
- **得**: 環境依存ゼロ、自動執行
- **失**: ローカル DB 接続情報を CI に渡す必要 / shadow DB 利用

#### 選択肢 C: Zod ↔ DB 整合 lint を自作
- **対象**: `packages/supabase/src/schemas/data-layer/*` と `database.types.ts` の field 名対応を機械検証
- **得**: 罠A（モノにコトを混ぜる）の自動検出に近づく
- **失**: 書く必要がある（200〜400 行）

#### 仮の組み合わせ
B + C。A は個人差があり harness 哲学に合わない。

### 2.5 Doc-ARC 自動執行

#### 選択肢 A: L1→L2 単方向参照の lint
- **検出**: L2 (`apps/*/docs/*.md`) からの相対参照が L1（root） を指す方向のみ許可、L2 間直接参照は禁止
- **実装**: 100〜150 行の `.mjs` lint
- **得**: 規約の自動執行、新人（人間/AI）の誤りを早期検出
- **失**: 文字列マッチングなので false positive あり

#### 選択肢 B: [INDEX.md](http://INDEX.md) 自動更新
- **検出**: [SPEC.md](http://SPEC.md) / [DONT.md](http://DONT.md) / docs/* の見出しから [INDEX.md](http://INDEX.md) を再生成
- **得**: INDEX 腐敗の防止
- **失**: 手書き部分との衝突管理

#### 選択肢 C: Dead link 検出
- **検出**: `.md` 内のリンクが実在ファイルを指すか
- **得**: ドキュメント腐敗の指標
- **失**: 既存 markdownlint 系ツールで代替可

#### 仮の組み合わせ
A は独自実装、B/C は OSS ツールで代替推奨。

### 2.6 authz-matrix の三角整合

`spec/[authz-matrix.md](http://authz-matrix.md)` ↔ `apps/platform/middleware.ts` ↔ `supabase/migrations/*_rls.sql` は **3 箇所で同じ事実を表現**しているため、腐敗しやすい。

#### 選択肢 A: [authz-matrix.md](http://authz-matrix.md) を SSOT にし、middleware と RLS を生成
- **得**: 一次情報絶対主義に整合
- **失**: 生成器の実装コスト大（500 行超見込み）

#### 選択肢 B: 3 箇所の照合 lint を書く（生成しない、検証のみ）
- **得**: 既存実装を温存、検証だけ自動化
- **失**: パターンマッチングの精度限界

#### 選択肢 C: テストで間接的に整合を担保
- **得**: 生成器・lint が不要
- **失**: テストカバレッジに穴があれば検出失敗

#### 仮の組み合わせ
B が現実的。A は長期の理想。

### 2.7 history/ アーカイブ戦略

11日で 4,381 行。6ヶ月で 70K 行に達する見込み。

#### 選択肢 A: クォーター単位で `history/_archive/{YYYY-Q#}/` へ移動
- **得**: 能動 history が常に小さい
- **失**: アーカイブされた決定への参照が壊れるリスク

#### 選択肢 B: 1 ファイル制限 + ローテーション（[COUNCIL-LOG-2026Q2.md](http://COUNCIL-LOG-2026Q2.md) 等）
- **得**: 参照は安定、ファイル分割で grep 性能維持
- **失**: 横断 grep が複雑化

#### 選択肢 C: 何もしない（grep / search で吸収）
- **得**: 設計コストゼロ
- **失**: 1年で破綻

#### 仮の組み合わせ
B を 2026-Q3 までに実装。

### 2.8 Migration ライフサイクル

#### 選択肢 A: down migration を全 migration に必須化
- **得**: 本番運用で必須
- **失**: 開発初期は冗長、v3.0 ブートストラップ期には合わない

#### 選択肢 B: production 切替時点（v3.1 等）から down 必須化
- **得**: 開発期は気軽に、本番期から厳格化
- **失**: 切替タイミングの定義が必要

#### 選択肢 C: forward-only + blue-green でカバー
- **得**: down migration の複雑性回避
- **失**: blue-green インフラ必要

#### 仮の組み合わせ
B + C。production 切替時に L0 で再議論。

### 2.9 sensor 自動実行

現在 `sensors/[computational.md](http://computational.md)` `sensors/[inferential.md](http://inferential.md)` は markdown で記述された手順書。layer1-autonomous-dev が献上前に「読んで実行する」運用。

#### 選択肢 A: sensor を実行可能スクリプト化
- **得**: 自動執行、CI 統合
- **失**: markdown の説明性が失われる
- **対案**: scripts と併用（markdown は説明、scripts は実行）

#### 選択肢 B: sensor の実行結果を `delivery/[VERIFICATION.md](http://VERIFICATION.md)` に machine-readable で残す
- **得**: 献上の信頼性向上
- **失**: フォーマット制約

#### 仮の組み合わせ
A + B。

### 2.10 Issue 駆動開発の稼働化

`crosscut-issue-dispatcher` / `crosscut-issue-implementer` を稼働させる場合。

#### 選択肢 A: [SPEC.md](http://SPEC.md) commit → Issue 自動生成（dispatcher）
- **トリガー**: [SPEC.md](http://SPEC.md) の特定セクション追加で `ready-for-ai` ラベル付き Issue を生成
- **得**: 仕様 → 実装の流れが完全自動化
- **失**: 暴走リスク（SPEC 一文の追加で巨大 Issue 群が生成される懸念）

#### 選択肢 B: Issue assigned → AI 実装起動（implementer）
- **トリガー**: Copilot/Claude にアサイン → worktree で実装
- **得**: 実装の完全自動化
- **失**: blast radius 制御が必須

#### 選択肢 C: feedback-loop 稼働
- **トリガー**: drift / sensor fail → SPEC への問題還流 Issue 自動作成
- **得**: 仕様の自己修復ループ
- **失**: 還流先判定ロジックの精度

#### 仮の組み合わせ
A → C → B の順で慎重に稼働。B は CTL 監視必須。

---

## 3. 横断的検討事項

### 3.1 自動化と Council の関係

**懸念**: 自動化が進むと Council 起動条件（trade-off / confidence < 0.6）に達する判断点が減る → Council ログが薄くなる → 決定の追跡可能性が下がる。

**対案**: 自動化された判断は machine-decided として `[COUNCIL-LOG.md](http://COUNCIL-LOG.md)` に区別記録。

### 3.2 自動化と 罠A〜H の関係

罠A〜H は **「人間/AI が踏みやすい誤り」** を言語化したもの。自動化はこれらの **能動的検出器** を提供すべき：

| 罠 | 対応する自動化 |
|---|---|
| 罠A: モノにコトのカラム | Zod ↔ DB 整合 lint（2.4 C） |
| 罠B: データ空 → RLS/Auth 疑い | RLS coverage test（新規） |
| 罠C: GUI スキーマ変更 | migration-only lint（新規 / 既存 supabase CLI でカバー可） |
| 罠D: クロスアプリ `<Link>` | `lint-internal-routing.mjs` で既に対応済 |
| 罠E: middleware return 漏れ | middleware の return path coverage lint（新規） |
| 罠F: Vercel Preview cookie | 検出不要（仕様）。ドキュメント徹底のみ |
| 罠G: transpilePackages 漏れ | next.config.mjs ↔ workspace dep lint（新規） |
| 罠H: 安易な `"use client"` | RSC/CC lint（既存 ESLint plugin で代替可） |

**含意**: 罠を全て自動化検出器に翻訳できれば、`[DONT.md](http://DONT.md)` の規範性が機械執行レベルに到達する。

### 3.3 1M context window との関係

CC が 1M トークン context を持つ現状、**自動化の動機が弱まる**側面がある：
- 人間 review でカバーできる量が増えた
- harness skill の lazy-load で context は圧迫されない
- → 「自動化しないと回らない」ボトルネックが見えにくい

**対案**: 自動化の動機を **「context 消費削減」ではなく「セッション横断の組織記憶」** に置く。
- 自動化は「次のセッションが新規の AI でも同じ判断を再現できる」ための装置
- これは context window では絶対にカバーできない（セッション境界を超える）

### 3.4 自動化のメンテコスト

自動化を増やすと **harness 自体のメンテコスト**が増える。15K LOC の skill に加えて：
- script: +1,500〜3,000 行見込み
- workflow: +200〜500 行
- test: +2,000〜5,000 行

合計で **20〜25K 行の harness/automation 層**となる。プロジェクト本体（コード 18K 行）と同等以上。Bus factor = 1 のもと、これは現実的か？

**対案**: 自動化は **「人間が理解可能な単位で小さく」**。1 自動化 = 1 ファイル（200 行未満）を原則とし、複雑化したら廃止。

---

## 4. 仮の優先順序（参考案、L0 が再判定する）

| Tier | 自動化項目 | 根拠 | 想定工数 |
|---|---|---|---:|
| **T1: 即時** | GitHub Actions で typecheck + lint:rls + lint:routing | 既存資産活用、ROI 最大 | 0.5 day |
| **T1: 即時** | Vitest 導入（Zod schemas のみ） | 罠A 対策、テスト体験の最初の一歩 | 1 day |
| **T2: 短期** | Migration dry-run on PR | RLS bug 早期検出 | 1 day |
| **T2: 短期** | `database.types.ts` drift 検出 | 罠A 対策 | 0.5 day |
| **T2: 短期** | crosscut-verifier-drift 稼働化 | harness の既存資産活用 | 1 day |
| **T3: 中期** | Playwright で e2e-probe を CI 化 | 動作回帰検出 | 3 day |
| **T3: 中期** | invariants.feature を Cucumber 実行可能化 | SPEC = test の理想型 | 5 day |
| **T3: 中期** | history/ クォーターアーカイブ | 6ヶ月後の破綻防止 | 1 day |
| **T4: 長期** | crosscut-issue-dispatcher / implementer 稼働 | Issue 駆動の完全自動化 | 検討含めて 5 day |
| **T4: 長期** | authz-matrix 三角整合 lint | 罠 RLS 系の根本対策 | 3 day |
| **T5: 評価のみ** | down migration 必須化 | production 切替時に再議論 | — |

---

## 5. L0 spec-architect への質問事項

ブレストの過程で **L0 が判断すべき分岐点**が以下のとおり浮上した。

### Q1. テストフレームワーク方針
- A: Vitest + Playwright + Cucumber（3層）
- B: Vitest + Playwright（Cucumber 不採用）
- C: Vitest のみ（最小）

→ harness 哲学（SPEC = 実行可能）を取るなら C → A の段階移行が筋。確認したい。

### Q2. 自動化の総量上限
- 自動化レイヤー（automation-layer）の LOC 上限を決めるべきか？
- 案: コード本体 LOC × 1.5 を上限とする等。

### Q3. crosscut-* skill 群の稼働タイミング
- dispatcher / implementer / drift / feedback-loop はいつ稼働させるか？
- 全部一気か、段階的か。段階なら順序は？

### Q4. 罠 A〜H の自動化検出器化を [SPEC.md](http://SPEC.md) に記載するか
- [DONT.md](http://DONT.md) は禁止の言語化。検出器の設計は [SPEC.md](http://SPEC.md) / docs/ どちらに入れるべきか。

### Q5. production 切替時期と down migration 必須化の関係
- v3.1（production 切替）の時期予定は？
- それまでは forward-only でよいか。

### Q6. Bus factor 軽減と自動化の関係
- 自動化を増やすと harness メンテで Bus factor がさらに 1 に集中する逆説。
- 対策として、自動化の文書化を harness 側 references に必ず残す方針でよいか。

### Q7. v5.1.0 の `crosscut-verifier-philosophy` 本実装後の扱い
- 5本柱整合検証が稼働すると、本ブレストの内容も検証対象になる。
- 哲学レベルの自動化は別途 L0 で再ブレストすべきか。

---

## 6. 本献上の取り扱い指示

- 本文書は **ブレスト** であり、[SPEC.md](http://SPEC.md) / [DONT.md](http://DONT.md) への直接マージを禁ずる
- L0 spec-architect は対話を通じて以下のいずれかに振り分けること:
  - **採用** → `[INTENT.md](http://INTENT.md)` に登録 → [SPEC.md](http://SPEC.md) に昇格
  - **却下** → `[INTENT.md](http://INTENT.md)` の「却下案」セクションに記録
  - **保留** → 次サイクル以降に再評価
- 採用された自動化は CTL（Confidence-To-Launch）連動で稼働範囲を制御
- 本ブレストファイル自体は `history/deliveries/` に保存し、後世の参照対象とする

---

## 7. 補遺：自動化の「効きどころ」マップ

```
[Spec]  [SPEC.md](http://SPEC.md) ──── [drift verifier] ──── [実装]
   │                                           │
   │                                           │
[Council]                                  [Test]
   │                                           │
   │                                           │
[INTENT] ─── [issue dispatcher] ── [issue implementer]
   │                                           │
   │                                           │
[履歴] ─── [feedback loop] ─── [sensor failure]
```

矢印が現在「人手」で繋がっている部分が自動化の余地。本ブレストの提案はこの矢印群を機械化することに収束する。

---

**END OF BRAINSTORM**

次サイクル: 本献上を受けて L0 spec-architect が対話を起動 → [INTENT.md](http://INTENT.md) 更新 → [SPEC.md](http://SPEC.md) 昇格分の確定。
