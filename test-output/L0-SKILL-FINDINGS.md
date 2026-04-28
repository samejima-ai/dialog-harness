# L0 Spec-Architect Skill — Test Findings & Improvement Proposals

> **L0 の役割**: L1（autonomous-dev）発動時に **AI 自律駆動開発が可能な開発環境** を構築すること。
> 本ドキュメントはこの役割の達成度を実テストで評価し、不足要素と SKILL.md 改善提案を構造化したものである。

---

## 0. 重要原則の再確認

L0 が「成功」したと言えるための受け入れ基準（Acceptance Criteria）:

> **L1 を起動した瞬間、対話・人間介入なしに `pnpm install && pnpm run dev` 等の標準コマンドで開発が始められる状態。**

ドキュメントが揃っているだけでは不十分。L1 が即座にコードを書き始められなければ L0 の役割は未達成である。

---

## 1. テストコンテキスト

| 項目 | 値 |
|---|---|
| **テスト日** | 2026-04-28 |
| **対象 skill** | `layer0-spec-architect` |
| **harness バージョン** | v4.2（コミット 2766334 時点） |
| **対象ブランチ** | `claude/test-upgrade-branch-YSzSo` |
| **対象 PR** | [#19](https://github.com/samejima-ai/dialog-harness/pull/19) |
| **テストシナリオ** | "ケロぴの森"（中学生向け絵で答える算数学習ゲーム）の対話 → 環境構築 |
| **Lifecycle 判定** | L=0（新規プロジェクト、ritual スキップ） |
| **モード判定結果** | M2 標準 / S=1, U=2, R=1 / NFR=5/15 / ARC=monolith |
| **実行モデル（L0）** | Claude Opus 4.7 (1M context) |
| **生成成果物の場所** | `test-output/keropi-no-mori/`（17 ファイル） |

---

## 2. 3 軸評価サマリ

| 軸 | 評価 | 判定 |
|---|---|---|
| **規模** | モード判定（M2）と ARC（monolith）は妥当。ただし実装可能性の検証は未実施 | ◯ 妥当 |
| **種類** | ドキュメント・サブフェーズ成果物は完備。**ビルド可能な scaffold が欠落** | △ 部分達成 |
| **手段** | 8 つの参照ファイルすべて未読のまま進行。SKILL.md 本体の知識のみで作業 | ✕ プロトコル違反 |

---

## 3. 受け入れ基準とのギャップ（具体的に何が足りないか）

### 3.1 🔴 Critical Gap — L1 が即着手できない原因

L1 起動時、以下のいずれか 1 つでも欠けると `pnpm run dev` 等の標準コマンドが成立しない。

| # | 不足ファイル | 影響 | 検出根拠 |
|---|---|---|---|
| C1 | `package.json` | `npm/pnpm install` 不可 | CLAUDE.md / sensors/computational.md が `pnpm run *` を参照 |
| C2 | `tsconfig.json` | spec/*.ts が型チェックされない | SKILL.md §6 「TypeScript strict」記載 |
| C3 | `vite.config.ts` | ビルド・開発サーバー起動不可 | CLAUDE.md §2 確定スタックで Vite 採用 |
| C4 | `vitest.config.ts` | ユニットテスト実行不可 | sensors/computational.md がテスト pass 必達 |
| C5 | `playwright.config.ts` | E2E テスト実行不可 | sensors/computational.md が E2E pass 必達 |
| C6 | `biome.json` または ESLint config | lint 実行不可 | sensors/computational.md が lint 0 警告必達 |
| C7 | `.gitignore` | `node_modules/` が誤って追跡される | 標準衛生 |
| C8 | `index.html`（Vite エントリ） | PWA 配信不能 | Vite ビルド要件 |
| C9 | `src/main.tsx` または相当 | アプリエントリポイント無し | L1 が「どこから始める？」不明 |
| C10 | `public/manifest.webmanifest` | PWA 動作不能 | SPEC.md F0 「Web PWA」要件 |

### 3.2 🟡 Major Gap — broken reference / 設計の不整合

| # | 不足 | 影響 | 検出根拠 |
|---|---|---|---|
| M1 | `assets/judgment-prompt.md` | Gemini 判定プロンプトのテンプレートが存在せず、`api-signatures.ts` のコメントが broken reference | SPEC.md F5 / CLAUDE.md / inferential.md / api-signatures.ts が参照 |
| M2 | `.claude/skills/` がプレースホルダのみ | プロジェクト固有 SK の設計が未着手 | M2 標準では本ディレクトリにプロジェクト固有 skill を置く規定 |
| M3 | `DOMAIN-CONTEXT.md` 未生成 | 教育心理・学習困難児への配慮等が SPEC 外で散逸する可能性 | 教育系 / アクセシビリティ最重要案件では検討が望ましい |

### 3.3 🟠 Minor Gap — プロトコル準拠不足

| # | 不足 | 検出根拠 |
|---|---|---|
| m1 | `references/regime-assessment.md` 未読のまま S/U/R 算出 | SKILL.md §4「判定プロトコルの詳細は references を参照」 |
| m2 | `references/nfr-scoring.md` 未読のまま NFR 算出 | SKILL.md §4「NFR スコアリングは references を参照」 |
| m3 | `references/model-recommendations.md` 未読のままモデル推奨提示 | SKILL.md §5「REGIME 確定時点で model-recommendations.md を読み込む」明示違反 |
| m4 | `references/subphase-l02-domain.md` 等 5 ファイル未読のまま spec/* 生成 | SKILL.md §3.5「各サブフェーズ固有プロトコルは下記」明示違反 |
| m5 | `references/permission-delegation.md` 未読のまま L0-2 / C2 設定 | SKILL.md §4「権限レベルは references を参照」 |
| m6 | `references/philosophy.md` 未読のまま 4 本柱を引用 | SKILL.md「全 skill の参照原典」明示違反、記憶ベースで構成 |
| m7 | `references/dev-env-spec.md` 未読のまま環境構築 | **3.1 の Critical Gap が発生した直接原因の可能性** |
| m8 | `assets/meta-spec-template.md` 未読のままドキュメント生成 | SKILL.md §3「メタ仕様テンプレートに従い」明示違反 |

---

## 4. 根本原因分析

### 4.1 なぜ参照ファイルを読まなかったのか

以下の 3 つが複合した:

1. **SKILL.md 本体の自己完結性が高すぎた**: SKILL.md だけでも「それっぽい」出力が作れる情報量がある。実行モデル（Opus 4.7）が SKILL.md を読んだ時点で十分と判断し、references/ への遷移トリガーが弱かった。

2. **「読め」が指示文として弱い**: SKILL.md 各所で「詳細は references/* を参照」と書かれているが、これは命令ではなく示唆。命令形（「ステップ X の前に必ず Y.md を読み込む」）でないため、実行モデルが省略を選択しうる。

3. **参照ファイルの存在検証フェーズが無い**: skill 起動時に references/ の存在を確認するステップが SKILL.md にない。読まなくても進行できる構造になっている。

### 4.2 なぜ scaffold（package.json 等）を生成しなかったのか

1. **SKILL.md §6 の「テスト基盤」記述が抽象的**: 「ビルド・テスト・リンターの設定（1 分以内制約）」とのみ記載。**何を生成するか**ではなく**何を守るか**を書いている。
2. **`references/dev-env-spec.md` 未読**: ここに具体的な scaffold 仕様があった可能性が高いが未確認。
3. **「ドキュメント生成」と「scaffold 生成」の重み付けが暗黙**: SKILL.md は INDEX/SPEC/DONT 等の文書生成を詳細に書く一方、scaffold は §7 の「テスト・ビルド基盤設定」と一行で済ませている。実行モデルは詳細な指示の方を優先した。

### 4.3 構造的な観察

> **「動くものを引き継ぐ」のではなく「仕様を引き継ぐ」設計に偏っている。**

現状の SKILL.md は L0 → L1 の引き継ぎを *仕様文書の引き継ぎ* として強く設計しているが、本来の charter「**AI 自律駆動開発が可能な開発環境の構築**」は *実行可能な作業環境の引き継ぎ* を要求する。両者の重なりが不十分なまま「ドキュメント完了 = L0 完了」と解釈されやすい。

---

## 5. SKILL.md 改善提案

優先度別に列挙。`P0` は今回のテストで露呈した致命的問題を防ぐ最小改善。

### 5.1 P0: 受け入れ基準の明文化

**変更箇所**: SKILL.md 冒頭または §「原則」直下

**追加内容案**:

```markdown
## L0 完了の受け入れ基準（Acceptance Criteria）

L0 は以下のすべてを満たした時点でのみ完了とみなす。1 つでも欠ければ未完了。

1. 仕様 3 点（SPEC.md / DONT.md / REGIME.md）が生成されている
2. CLAUDE.md / .claude/settings.json が生成されている
3. M2 以上では sensors/{computational, inferential, review-checklist}.md が生成されている
4. 起動したサブフェーズの spec/ 成果物がすべて生成されている
5. **L1 が `pnpm install && pnpm run dev` で開発を開始できる scaffold が生成されている**（package.json / tsconfig / ビルド設定 / lint 設定 / .gitignore / エントリポイント）
6. 文書中で参照する全ファイルが存在する（broken reference ゼロ）
7. README.md にクレジットマーカーが入っている

特に 5 と 6 は計算的に検証可能。L0 終了前に自動チェックを推奨。
```

### 5.2 P0: 参照ファイル読み込みの命令化

**変更箇所**: SKILL.md 各ステップに「Pre-flight check」を追加

**追加内容案（ステップ単位の Pre-flight）**:

| ステップ | 開始前に必ず読む |
|---|---|
| 1.5 振り返り儀式 | `references/ritual-protocol.md` |
| 2 対話による具体化 | `references/dialog-questions.md` / `references/domain-context-dialog.md` |
| 3 ドキュメント化 | `assets/meta-spec-template.md` / `references/philosophy.md` |
| 3.5 サブフェーズ実行 | 起動する各サブフェーズの `references/subphase-l0X-*.md` |
| 4 モード判定 | `references/regime-assessment.md` / `references/nfr-scoring.md` / `references/permission-delegation.md` |
| 5 人間レビュー前 | `references/model-recommendations.md`（v4.2 で既に明示済、強化推奨） |
| 6 環境構築 | `references/dev-env-spec.md` |
| 7.5 ファイル配置 | `references/dev-env-spec.md`「ファイル配置規則」 |
| 7.6 クレジット | `assets/credit-template.md` |

各ステップの冒頭に `**Pre-flight: 以下を読まずに進行禁止 — [ファイル一覧]**` を明示。

### 5.3 P0: scaffold 生成チェックリストの追加

**新規ファイル**: `references/dev-env-spec.md`（既存）に追記、または `references/scaffold-checklist.md` 新設

**内容案（M2 monolith の場合）**:

```markdown
## M2 monolith Web PWA scaffold 必須生成物

ステップ 6 で必ず生成する。テンプレートは technologyStack に応じて分岐。

### Vite + TypeScript + React 系の場合（既定）

- `package.json`（最低: vite, typescript, vitest, playwright, biome）
- `tsconfig.json`（strict: true, target: ES2022）
- `tsconfig.node.json`（vite.config 用）
- `vite.config.ts`（PWA plugin 含む）
- `vitest.config.ts`
- `playwright.config.ts`
- `biome.json` または `.eslintrc.json` + `.prettierrc`
- `.gitignore`（node_modules, dist, .env*, coverage, playwright-report 等）
- `.env.example`（必要な API キーの placeholder）
- `index.html`（Vite エントリ）
- `public/manifest.webmanifest`（PWA）
- `src/main.tsx` または `src/main.ts`（アプリエントリ、L1 が拡張する出発点）
- `src/App.tsx`（最小コンポーネント）
- `tests/.gitkeep`
- `README.md` にビルド・テスト・lint コマンドを記載

### 生成方針

L0 が「動く最小骨格」まで作る。L1 はビジネスロジックと UI を埋める。
最小骨格の判定基準: `pnpm install && pnpm run build && pnpm run test && pnpm run lint` がエラーなく通る。
```

### 5.4 P1: 自己検証ステップの追加

**変更箇所**: SKILL.md §7 と §7.5 の間に新設

**追加内容案**:

```markdown
### 7.4 L0 出力の自己検証（必須）

ステップ 7 完了後、以下を実行して L0 の達成度を計算的に検証する。

1. **broken reference 検査**: 生成した全 .md ファイルから `(./.../*.md)` 形式のリンクを抽出し、対象が存在することを確認
2. **scaffold smoke test**:
   - `pnpm install` が exit 0 で完了
   - `pnpm run typecheck` が exit 0
   - `pnpm run build` が exit 0
   - `pnpm test --run` が exit 0（最小サンプルテストで OK）
3. **DONT.md 自己照合**: SPEC.md / CLAUDE.md / sensors の文言から、DONT.md A 節の禁則ワードが含まれていないことを確認

いずれか fail なら L0 は完了とみなさない。修復後に再検査。
```

### 5.5 P1: 「ドキュメント vs 動作」の重み付け明文化

**変更箇所**: SKILL.md §「原則」

**追加内容案**:

```markdown
- **ドキュメントだけでは L0 完了ではない**。L0 の charter は「L1 が autonomous に開発を始められる環境の構築」であり、文書一式は必要条件だが十分条件ではない。L1 起動時の `pnpm run dev` 成立を以て L0 完了とする。
```

### 5.6 P2: skill 出力の monorepo 配置（テスト容易性）

L0 skill 自体のテストを継続的に行うため、`test-output/` 配下に skill のテストフィクスチャを置く運用を SKILL.md or テスト規格として明文化。今回 (II) で配置したパターンを正式化。

---

## 6. 即時対応すべき修復項目（次の skill 改善 PR に含める）

### 6.1 v4.2 → v4.3（patch / minor）で必要な変更

- [ ] SKILL.md §「原則」に受け入れ基準ブロック追加
- [ ] SKILL.md 各ステップに Pre-flight check 行追加
- [ ] SKILL.md §6 から `references/dev-env-spec.md` への参照を **必読指定** に強化
- [ ] `references/dev-env-spec.md` に scaffold 必須生成物リスト追加（5.3 案）
- [ ] SKILL.md §7.4 自己検証ステップ新設
- [ ] SKILL.md §「原則」に「ドキュメント完了 ≠ L0 完了」原則追加
- [ ] SKILL.md ステップ 5 のモデル推奨提示を「必読」から「必行（生成出力に含む）」に強化

### 6.2 既存機能との後方互換性

- 既存の Lifecycle ≥ 1 プロジェクトは影響を受けない（L0 再起動時の差分対応）
- 新規（L=0）プロジェクトでは scaffold 必須生成物が増える → L1 起動時の前提が安定化
- 既存テスト（layer1-independent-reviewer の照合）は壊れない

---

## 7. テストフィクスチャとしての本データの再利用

本テストで生成された `test-output/keropi-no-mori/` は以下の用途に再利用可能:

1. **SKILL.md 改善後のリグレッション検証**: 改善版 skill でケロぴの森対話を再実行し、scaffold が生成されるかを検証
2. **layer1-autonomous-dev skill の入力フィクスチャ**: 改善後、L1 を実際に起動して `pnpm run dev` が動くまでを確認するテストの入力
3. **layer1-independent-reviewer skill の照合フィクスチャ**: review-checklist.md が L1 成果物を正しく独立検証できるかのテスト入力
4. **council skill の判定例題**: 「scaffold は L0 / L1 どちらの責務か」の合議判定の素材

---

## 8. 提案する次のアクション

| アクション | 担当 | タイミング |
|---|---|---|
| **本ドキュメントを別ブランチでレビュー** | 人間 | 即時（このセッション後） |
| **改善 PR の起票**（5.6 の P0 項目） | 後続セッション | レビュー結果を反映 |
| **`references/dev-env-spec.md` の scaffold 仕様追記** | 後続セッション | P0 PR と同時 |
| **改善版 skill でケロぴの森を再実行** | 後続セッション | P0 PR マージ後 |
| **L1 を実走させて `pnpm run dev` 成立を確認** | 後続セッション | scaffold 改善後 |

---

## 9. 補足: 本テストで良かった点（後退させてはいけないもの）

将来の改善で失わないよう記録:

- **対話の自然さ**: 中学生 n=1 ペルソナへの寄り添い、選択肢提示の粒度、選択肢ベースの認識合わせは機能した
- **哲学の引き出し**: 「絵 = 理解の証拠」「学習者ではなく救助者」「待ち時間も体験に変える」など、人間と協創的に発見できた
- **ネーミングの再提案**: 「キモイ」フィードバックから「ケロぴの森」を引き出すループは健全
- **DONT.md の網羅性**: A 心理面〜F 開発プロセスまで 6 セクション、妹さん体験防御として強い
- **サブフェーズ選定**: 5 問プロトコルは判断容易、L0-5 スキップの妥当性も明確
- **Mermaid / Gherkin の併用**: state-diagrams.md と invariants.feature は L1 の実装ガイドとして実用的
- **判定 3 段階の正規化**: domain.ts の `ReactionKind` 型と invariants の文言禁則が連動

これらは v4.2 SKILL.md の対話設計が実機能した証拠であり、改善時に削減・希薄化してはいけない。

---

## 10. 結論

**v4.2 layer0-spec-architect skill は「仕様策定スキル」としては十分機能した。しかし「AI 自律駆動開発が可能な開発環境の構築」という charter には届いていない。**

ギャップの主因は以下 2 点:
1. **scaffold 生成が SKILL.md §6 で抽象的にしか規定されていない**
2. **参照ファイル読み込みが命令化されておらず、SKILL.md 本体の自己完結度が高すぎる**

P0 改善（受け入れ基準の明文化 + Pre-flight check + scaffold チェックリスト + 自己検証ステップ）を v4.3 で実施すれば、L0 の charter を達成可能と見込む。

本ドキュメントは別ブランチでのレビューを経て、改善 PR の入力資料として使用される想定である。

---

**Generated**: 2026-04-28
**Source PR**: [samejima-ai/dialog-harness#19](https://github.com/samejima-ai/dialog-harness/pull/19)
**Skill version**: v4.2 (commit 2766334)
**Test scenario**: ケロぴの森（M2 monolith Web PWA / n=1 / 中学生算数 / 絵で答える）
