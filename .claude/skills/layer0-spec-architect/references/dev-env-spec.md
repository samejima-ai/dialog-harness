# 開発環境ドキュメント規格

AI自律開発環境を構成するRL/SK/センサーの記述フォーマットと配置規約。
モード（M1/M2/L2）に応じて構成が変化する。

---

## 用語定義

本ドキュメントおよび dialog-harness-layers 内の全ドキュメントで以下の用語を統一使用する。

### dialog-harness-layers

AI 自律開発のための設計思想とスキル群の総称（概念的グルーピング名）。
実体は `.claude/skills/` 直下に `layerN-` prefix で配置されるスキル定義ファイル群。
L0/L1/L2 の三層構造、フラクタル原則、人間⇄AI 協働プロトコル等を含む。

### Level A（共通スキル）

全プロジェクトで不変の汎用スキル。プロジェクトごとに再生成しない。
`.claude/skills/` 直下に `layerN-` prefix 付きで配置：

- layer0-spec-architect
- layer0-onboarding（使い捨て）
- layer0-archeo-architect（再利用可能、v5.4.0 追加）
- layer1-autonomous-dev
- layer1-independent-reviewer
- layer2-orchestrator
- layer2-integration-verifier

### Level A 配布性評価 checklist（v5.16.0 追加）

Level A スキル（または crosscut-* スキル）として配布する前に、以下の checklist で配布適格性を評価する。`.claude/skills/` 直下に置く skill 候補が Level A として成立するかの判定基準。新規 skill 追加時、または既存 skill の格上げ・格下げ検討時に必須評価。

#### A. 不変性（プロジェクト中立）

- [ ] **A-1 プロジェクト固有値の不在**: SKILL.md / references/ / assets/ 内にプロジェクト固有のドメイン語（業務用語・社名・商品名）を含まない
- [ ] **A-2 ドメイン独立性**: 業界（金融・医療・EC 等）に特化した記述が無いか、あっても references/ 配下の任意参照 (`domain-*.md`) に閉じている
- [ ] **A-3 stack 中立性**: 特定の言語・FW・DB 名がハードコードされていない。stack 固有手順は `scaffold-checklist.md` の対応 stack テンプレに切り出し済み

#### B. 参照整合性（dead-link 不在）

- [ ] **B-1 兄弟 skill 参照**: SKILL.md → 兄弟 skill への参照は `../<sibling-skill>/...`、references/ 配下からは `../../<sibling-skill>/...`（harness-verifier 検査 2「参照 path 有効性」で機械検証）
- [ ] **B-2 repo 内部参照**: 説明用に `.claude/skills/...` 形式のリポジトリルートからのパスを書く場合は、説明文脈（resolve 不要）であることをバッククォート前後の文脈で明確化
- [ ] **B-3 frontmatter 整合**: SKILL.md の frontmatter (name / description / model / 等) が `harness-verifier/checks/frontmatter.py` の検査をパス
- [ ] **B-4 用語辞書整合**: `harness-verifier/glossary.yml` の用語と整合（出現する重要用語が辞書に存在、または辞書から逸脱していない）

#### C. progressive disclosure 規約準拠

- [ ] **C-1 SKILL.md の役割**: 200〜600 行を目安に、起動条件 + 処理フロー + 主要ステップで完結。詳細プロトコルは references/ に切り出し
- [ ] **C-2 references/ の役割**: 必要時のみ読み込む詳細仕様・参照ドキュメント。SKILL.md から明示的に呼ばれている
- [ ] **C-3 assets/ の役割**: 埋めて使うテンプレート・素材。生のテンプレ文字列を含む
- [ ] **C-4 役割分離**: references/（読み参考）と assets/（埋めて使う）の分離が守られている

#### D. 依存方向（フラクタル整合）

- [ ] **D-1 単方向依存**: 上位 layer から下位 layer への参照のみ（L2 → L1 → L0、crosscut → 各 layer は OK、逆方向禁止）
- [ ] **D-2 兄弟 skill 間の循環なし**: SK 間参照グラフで循環が発生しない（harness-verifier 検査 3「SK 間参照の健全性」で機械検証）
- [ ] **D-3 harness-verifier 非依存**: 本 skill が harness-verifier の機能を呼び出していない（D4 検査機構と本体の独立性要請）

#### E. 自己完結性（利用者プロジェクト配布性）

- [ ] **E-1 外部ライブラリ依存ゼロ**: SKILL.md の処理フローが Python 標準ライブラリ or 利用者の既存 stack（Node/pnpm 等）だけで動く
- [ ] **E-2 認証情報不要**: GITHUB_TOKEN 等の secret を**要求する**記述は dev_mode = autonomous 専用 skill に限定
- [ ] **E-3 OS 非依存**: Linux/Mac/WSL のいずれでも動作する手順（shell-specific な記法 (zsh/bash) を断り無く使わない）

#### F. メタ評価

- [ ] **F-1 SKILL.md description の起動契機網羅**: skill description が起動契機（人間発話例・自動起動条件）を 3 例以上含む
- [ ] **F-2 LC 互換**: LC=0 (新規) / LC=1 (継続) / LC=2 (振り返り) の各局面で挙動が定義されている、または明示的に「LC=X のみ起動」と書かれている
- [ ] **F-3 dev_mode 互換**: local_only / github_assisted / autonomous の各 dev_mode で挙動が定義されている、または「dev_mode = X のみ起動」と書かれている

#### 適用ルール

- **新規 skill 追加 PR**: PR 内で本 checklist 全項目を埋め、レビューで承認後にマージ
- **既存 skill 改修**: 改修範囲に該当する項目のみ再評価。frontmatter / 参照パス変更時は最低 B-1 〜 B-4 を再評価
- **格上げ・格下げ**: layer1- prefix を crosscut- に移す等の格変更時は全項目を再評価
- **未充足項目あり**: skill description で「実験的」「PR1 walking skeleton」等と明示してマージは可能。但し未充足項目は dh-upgrades/ に申し送り

#### 検査機構との連携

| checklist 項目 | 機械検証可否 | 検査機構 |
|---|---|---|
| A-1 / A-2 / A-3 | 不可（人間判断） | — |
| B-1（インライン / バッククォート両形式） | 可 | harness-verifier 検査 2「参照 path 有効性」(v5.16.0 で BACKTICK_PATH_RE 追加) |
| B-3 | 可 | harness-verifier 検査 1「frontmatter 整合性」 |
| B-4 | 可 | harness-verifier 検査 5「用語辞書整合」 |
| D-2 | 可 | harness-verifier 検査 3「SK 間参照の健全性」 |
| 他項目 | 不可 | レビュー時の人間判断 |

機械検証可能な項目は harness-verifier 全 PASS で自動充足、人間判断項目は PR レビューでカバーする。

---

### Level B（プロジェクト固有スキル）

プロジェクト固有の開発支援スキル。
`.claude/skills/` 直下に `layerN-` prefix 以外のスキル名で配置（dialog-harness-layers 概念の外側）。

### layer

dialog-harness-layers の階層単位：

- Layer 0: 仕様策定層（spec-architect / onboarding）
- Layer 1: 実装検証層（autonomous-dev / independent-reviewer）
- Layer 2: 統括指揮層（orchestrator / integration-verifier）

### 外向けブランド表記

README.md 等のクレジットでは `dialog-harness/layer's` を使用する。
これはブランド表記であり、パス参照では使用しない。

---

## CLAUDE.md（エージェントRL）

エージェントの行動ルール。プロジェクトルートに配置。
コンテキストに強制読み込みされる。

### 記述フォーマット

```markdown
# [プロジェクト名] — エージェントルール

## 原則
- [このプロジェクト全体に適用されるルール]

## コーディング規約
- [言語固有のルール]
- [命名規則]
- [ファイル構成ルール]

## 禁止事項
- [絶対にやってはいけないこと]

## 参照
- 仕様: INDEX.md
- 体制: REGIME.md
- センサー: sensors/
- スキル: .claude/skills/
```

### 記述ルール
- 200行以内に収める（超える場合は参照ファイルに分離）
- 命令形で書く（「〜すること」ではなく「〜する」）
- 理由も添える（「なぜこのルールが必要か」をルールの直後に1行で）

---

## ファイル配置規則（厳格）

### 基本原則

プロジェクトは **所有と参照を別軸** で管理する。
「誰が書くか」と「誰が読むか」は必ずしも一致しない。

### 人間運用の前提

dialog-harness-layers は以下を前提に設計される：

1. **人間は手を動かさない**: ファイル退避・整理は全て AI が実行する
2. **人間は読まない**: 人間向けドキュメントは依頼駆動でのみ生成する
3. **人間は必要な時だけ動く**: 承認・判断・指摘のみが人間の責務

この前提に反する規格は運用で死ぬ。規格設計時は「人間に追加作業を強いていないか」を常に検証する。

### 参照権限マトリクス

| 領域 | ディレクトリ | AI読 | AI書 | Human読 | Human書 |
|---|---|---|---|---|---|
| A領域（規格） | ルート直下規格ファイル, sensors/, history/, .claude/ | ✅ | ✅ | ✅ | ❌ |
| A出力 | delivery/ | ✅ | ✅ | ✅ | ❌ |
| 共有入力 | assets/ | ✅ | ❌ | ✅ | ✅ |
| 共有出力 | docs/ | ❌* | ✅** | ✅ | ❌ |
| 実装共有 | src/, app/, etc | ✅ | ✅ | ✅ | ✅ |
| 配布雛形（v5.0.0 追加） | templates/ | ✅ | ✅ | ✅ | △※ |

*docs/ は生成時のみAIが書く。既存 docs/ の AI 読込は人間の明示依頼時のみ。
**docs/ への書き込みは人間の明示依頼時のみ。自走中に勝手に生成しない。
※ templates/ は dialog-harness-layers が配布する CI/CD 雛形等の置き場。プロジェクトが採用するときに `cp -R templates/.github/ .github/` 等でコピーして利用する。雛形本体の改修は L0 案件として扱い、プロジェクト側からの直接編集はしない（採用後は当該プロジェクトの所有物となる）。

### ディレクトリ定義

#### A領域（AI処理の入出力）

- **ルート直下規格ファイル**: INDEX.md, CLAUDE.md, SPEC.md, DONT.md, REGIME.md, DOMAIN-CONTEXT.md, DESIGN.md（UI プロジェクトのみ、v5.15.0 追加）
- **sensors/**: センサー定義
- **history/**: 履歴層（LC ≥ 1）
- **.claude/**: スキル定義

#### A出力（delivery/）

AI が生成する献上物のみ。規格ファイル以外の混入禁止。

#### 共有入力（assets/）

開発に必要な素材のみ置く。

- .docx / .pdf / .xlsx / .png / モックアップ / 参考資料
- SPEC.md / DOMAIN-CONTEXT.md から明示参照されたファイルのみ AI が読む
- 全走査禁止。孤立ファイルは検出対象

#### 共有出力（docs/）

人間が「くれ」と言った時だけ AI が生成する人間用手順書。

- SETUP.md（環境構築手順）
- OPERATIONS.md（運用マニュアル）
- 各種業務手順書
- 常備しない。依頼駆動で生える
- SPEC.md の F 番号には含めない（運用補助物として扱う）

### ルート直下の許可リスト

以下のみ許可：

- A領域の規格ファイル（INDEX.md, SPEC.md, ...）
- README.md（プロジェクト紹介 + クレジット）
- LICENSE（任意）
- 設定ファイル（package.json, tsconfig.json, .env.example 等）
- 実装ディレクトリ（src/, app/, components/, lib/, db/, public/ 等）

### ルート直下の禁止リスト

- AI-Output（必ず delivery/ 配下）
- 規格外 Markdown（PHASE*.md, TODO.md, PLAN.md, NOTES.md, SETUP.md 等）
- 入力素材（.docx / .pdf / .xlsx / .png 等）→ assets/ へ
- 人間向け手順書 → docs/ へ

### delivery/ 配置規則

delivery/ 配下に置けるのは以下のみ：

#### 規格ファイル

- DELIVERY.md（全モード必須）
- VERIFICATION.md（M2 以上で必須）
- INTEGRATION.md（L2 のみ）
- HISTORY-DIFF.md（LC ≥ 1 で必須）

#### 成果物（任意）

- src/ / tests/ 等の実装ディレクトリ（プロジェクト方針による）

#### Phase γ 由来の検証データ（v5.5.0 追加、`refactor-intent-map.md` 存在時のみ）

- `delivery/refactor-intent-map.md` — archeo-architect 出力の意図マップ（canonical 配置、`layer0-archeo-architect/references/handoff-to-evaluator.md` §I/O 契約準拠）
- `delivery/archive/refactor-intent-map-YYYY-MM-DD.md` — 旧版意図マップのアーカイブ（archeo 再起動時、L1 は参照しない）
- `delivery/approval-tests/<island-id>.baseline.json` — preserve Island 用承認テスト基準データ（先行宣言 1 由来、`layer1-autonomous-dev/SKILL.md §6 意図合致検証` 参照）
- `delivery/reconciliation-logs/<island-id>.log` — restructure Island 用新旧並行実行照合ログ（先行宣言 2 由来、同上）
- `delivery/intent-archive/` — 意図合致検証の中間生成物（任意、プロジェクト方針による）

これらは `refactor-intent-map.md` 存在時のみ生成される（archeo を一度も起動していないプロジェクトには現れない）。`layer1-independent-reviewer` §5.5 配置規則チェックは本ディレクトリ群を許可リストに含める（`refactor-intent-map.md` の同梱が条件）。

#### UI プロジェクトの視覚検証データ（v5.15.0 追加、DESIGN.md 存在時のみ）

- `delivery/screenshots/` — Playwright で取得した主要画面のスクリーンショット保存先（philosophy 5 層検出スタック第 2 層 E2E の成果物）。L1-autonomous-dev §6 自己検証で生成、L1-independent-reviewer 5.5.1 で第 5 層 Vision モデル判定の入力として消費
- `delivery/screenshots/baseline/` — baseline 比較を導入している場合の基準スクショ（任意、プロジェクト方針による）
- `delivery/screenshots/diff/` — baseline 比較の差分画像（任意、CI で生成）

これらは `DESIGN.md` 存在時のみ生成される（DESIGN.md がないプロジェクトには現れない）。`layer1-independent-reviewer` §5.5 配置規則チェックは本ディレクトリ群を許可リストに含める（DESIGN.md の同梱が条件）。

#### dialog-harness 自プロジェクト用 meta-skill 開発の進行中スコープ（v5.12.0 追加、本 repo 専用例外）

**本カテゴリは `dialog-harness` リポジトリ自身（規約の発信元）にのみ適用される例外規則であり、利用者プロジェクトには配布されない。** dialog-harness が ECC 等の業界素材を咀嚼してメタスキル群を成長させる過程で生じるドキュメント群は、**ファイルの意図に応じて `delivery/` または `history/` のいずれかに配置する**。「規約発信元の例外だから全部 delivery/ に置く」のではなく、**履歴記録か進行中作業文書か** の意図で振り分ける。

##### `delivery/` に置くもの（進行中の短期作業文書）

「現在の Wave / 現在の Layer 引継ぎ」で参照される、**スコープが閉じれば歴史に移る**性質のファイル:

- `delivery/CHEW-PROTOCOL-SPEC-wave*-starter.md` — 進行中 Wave の SPEC ドラフト（Wave 完遂後は `history/` へ archive）
- `delivery/HANDOFF-*.md` / `delivery/HANDOFF-RECONCILE-*.md` — Layer 間引継ぎ（次 Layer の入力として参照中、完了後は `history/` へ）
- `delivery/REGIME-CONFIRM-*.md` — 現在の REGIME 確認ノート（最新版のみ delivery/、過去版は `history/` へ）

##### `history/` に置くもの（採決済 / 完了済の歴史記録、append-only）

採決・完了後の不変記録で、**後続作業から参照されるが書き換えない**性質のファイル:

- `history/COUNCIL-LOG.md`（既存）— Council 採決の総合ログ
- `history/wave*/COUNCIL-DECISION-*.md` — Wave 別の Council 採決記録（詳細版）
- `history/wave*/CHEW-CANDIDATES-*.md` / `history/wave*/COUNCIL-AGENDA-*.md` — 採決完了後の候補・agenda
- `history/wave*/CHEW-PROTOCOL-SPEC-wave*-starter.md` — Wave 完遂後の SPEC archive
- `history/PHILOSOPHY-NOTE-*.md` — philosophy.md 第 N 条候補の素材ノート（philosophy.md に統合された後も保管）
- `history/ECC-SURVEY-*.md` / `history/refs-draft/` — 業界素材の観察スナップショット（時点記録）
- `history/SKILL-CREATOR-AUDIT-*.md` / `history/SKILL-DESCRIPTION-AUDIT-checklist-*.md` — skill 群の監査記録
- `history/SELF-VERIFICATION-*.md` / `history/D4-AUDIT-*.md` / `history/RITUAL-*.md` — 振り返り / 検証記録
- `history/L0-WF-DESIGN-*.md` / `history/L1-DELIVERY-*.md` — 設計・リリース記録

##### Wave 完遂時の移動規約

Wave merge 後（次 Wave 開始前）に以下を実行:

1. `delivery/CHEW-PROTOCOL-SPEC-wave<N>-starter.md` を `history/wave<N>/` に移動
2. 同 Wave で生成された `delivery/HANDOFF-*-wave<N>-*.md` も `history/wave<N>/` に移動
3. `delivery/` には次 Wave 進行中スコープのみ残す

##### 移行措置（既存ファイル）

本規約は v5.12.0 で導入されたが、それ以前から `delivery/` に存在する以下のファイル群は **次回 minor リリースで `history/` へ移動する別 PR で順次整理する**:

- 過去 Wave の `delivery/CHEW-PROTOCOL-SPEC-wave1-starter.md`
- 過去の `delivery/COUNCIL-DECISION-*.md` / `delivery/PHILOSOPHY-NOTE-*.md`
- 過去の監査・検証記録

本 PR (#77) では Wave 2 進行中スコープに該当する SPEC starter のみ delivery/ に新規配置し、既存ファイルの大規模移動は別 PR で扱う（破壊的変更を 1 PR に集中させない）。

##### 根拠

- dialog-harness 自身は規約の **発信元** であり、自プロジェクトの meta-skill 開発で「規約 vs 実装」のメタ作業を行う特殊文脈にある
- ただし「規約発信元の例外」だから無秩序に蓄積するのではなく、**作業文書 vs 歴史記録** の意図に応じて配置先を分ける
- 咀嚼プロトコル（議題 0 採決 `council-2026-05-11T03:49:01Z-4go7g1`）は Wave 単位で SPEC → 採決 → 実装 → 検証を反復するため、Wave 進行中は `delivery/`、Wave 完遂後は `history/wave<N>/` に蓄積する
- これらは利用者プロジェクトの L1/L2 開発フローには関与しないため、配布対象外（`harness-verifier/BOUNDARY.md` の配布境界と整合）

##### 禁止（本例外でも維持）

- 進行管理ファイル（PLAN.md / PHASE*.md / TODO.md 等）は本例外でも禁止のまま
- 利用者プロジェクト側で本カテゴリのファイルを `delivery/` に配置することは禁止（dialog-harness 専用例外）
- Wave 完遂後に SPEC starter / HANDOFF を `delivery/` に残したまま次 Wave を始めることは禁止（履歴と進行中の混在を避ける）

#### 禁止

- PLAN.md / PHASE*.md / TODO.md 等の進行管理ファイル
- 作業メモ・中間思考ログ
- 規格外のあらゆるドキュメント

進行管理が必要と感じた時、それは **仕様発見**。L0 対話に戻し、SPEC.md の機能分解見直し or REGIME.md のサブドメイン再判定を検討する。

### assets/ 参照規約

AI は assets/ 配下を **明示参照されたファイルのみ** 読む：

- SPEC.md / DOMAIN-CONTEXT.md にパス記載があるもの
- 全走査禁止
- 孤立ファイルは sensors で検出

機密素材は `.gitignore` 対象：

```gitignore
assets/*.secret.*
```

### docs/ 書き込み規約

AI は docs/ への書き込みを **人間の明示依頼時のみ** 行う：

- 自走中に勝手に生成しない
- 生成物は delivery/DELIVERY.md で一覧化
- SPEC.md の F 番号には含めない（運用補助物として扱う）

### 違反検出と自動修復

違反検出時は AI が自動修復する（人間は承認のみ）。

| 違反 | 自動修復 |
|---|---|
| ルート直下の .docx/.pdf/.xlsx/.png | assets/ へ移動 |
| ルート直下の SETUP.md 等手順書 | docs/ へ移動 |
| ルート直下の PHASE*.md / PLAN.md | 内容分析→SPEC.md 吸収 or 削除提案 |
| delivery/ の規格外ファイル | 削除 |
| assets/ の孤立ファイル | 削除提案（人間一括承認） |

修復ログは `delivery/DELIVERY.md` の「配置規則違反修復ログ」セクションに記載。

### 開発環境構築時の初期化

layer0-spec-architect は新規プロジェクトで以下を初期化する：

- ルート直下規格ファイル（既存通り）
- sensors/, history/, .claude/
- delivery/（空、.gitkeep 配置）
- assets/（空、.gitkeep 配置）
- docs/ は **初期生成しない**（依頼駆動で生える）
- stack 別の **scaffold（実体ファイル）の生成必須リストと smoke test 手順** は `references/scaffold-checklist.md` を参照（v5.1.0 追加）

---

## .claude/skills/（プロジェクト固有SK）

プロジェクト固有の開発スキル。エージェントが必要に応じて動的に読み込む。

**重要な配置原則 — Level A と Level B の区別**:

- **Level A（dialog-harness-layers 本体）**: 汎用スキル（layer0-spec-architect, layer0-onboarding, layer1-autonomous-dev, layer1-independent-reviewer, layer2-integration-verifier, layer2-orchestrator）は dialog-harness-layers 配布元にのみ存在する。プロジェクト側で再生成・コピーしない
- **Level B（このプロジェクト）**: プロジェクト固有のスキルのみを置く。検証agentの本体はここには置かない（agent本体はプロジェクト不変。差異はチェックリスト/sensorsに閉じる）

### 配置規約

```
.claude/skills/
├── [プロジェクト固有skill-name]/
│   ├── SKILL.md       # スキル定義（必須）
│   └── references/    # 参照ドキュメント（任意）
```

### SKILL.md フォーマット

```markdown
---
name: [skill-name]
description: >
  [このスキルが何をするか、いつトリガーするか]
---

# [スキル名]

## 処理フロー
[ステップを順に記述]

## 入力
[このスキルが必要とする情報]

## 出力
[このスキルが生成するもの]
```

### 設計原則
- 1スキル1責務
- SKILL.md は500行以内（超える場合はreferences/に分離）
- Progressive Disclosure: メタデータ→SKILL.md本体→参照ドキュメントの3段階読み込み

---

## sensors/（センサー定義）

Layer 1がself-checkに使う判定基準と、独立検証agent・統合検証agentが参照する判定基準。

### computational.md（計算的センサー）

決定論的で高速な検証。1分以内に完了する制約。

```markdown
# 計算的センサー

## ビルド
- コマンド: [ビルドコマンド]
- 成功条件: exit code 0
- 制約: 1分以内

## 型チェック
- コマンド: [型チェックコマンド]
- 成功条件: エラー0件

## リンター
- コマンド: [リンターコマンド]
- 成功条件: エラー0件（warningは許容）

## テスト
- コマンド: [テストコマンド]
- 成功条件: 全件pass
- 制約: 1分以内
```

### inferential.md（推論的センサー）

LLMによる確率的判定。仕様合致の自己評価に使う。

```markdown
# 推論的センサー

## 仕様合致チェック
以下の観点でSPEC.mdと実装を照合する。

### チェック項目
- [ ] SPEC.mdに記載された全機能が実装されているか
- [ ] 各機能の条件が満たされているか
- [ ] 制約に違反していないか
- [ ] DONT.mdのスコープ外領域に踏み込んでいないか

### 判定基準
- 全項目クリア → 献上可能
- 1項目でも未クリア → 自力修正を試みる → 修正不可能ならフィードバックレポートに記載

## 「動く」チェック
- アプリケーションが起動するか
- 主要な操作パスが動作するか

## 「使える」チェック
- ユーザーの操作で期待した結果が得られるか
- エラーハンドリングが機能するか
```

### sensors/e2e/（M1/M2/L2 共通、第2層）

5層エラー検出スタック第2層（E2E機械検証）のシナリオ定義。L1 単独（M1/M2）では L1 自身が参照し、L2 発動時は Playwright Test Agents（`../../layer2-orchestrator/references/e2e-integration.md`）が参照する。

```
sensors/e2e/
├── scenarios.md      # シナリオ定義（ID / 前提 / 操作 / 期待結果 / Priority）
├── selectors.md      # DOM セレクタ命名規約（data-testid 等）
├── fixtures/         # テストデータ・モック定義
└── config.ts         # Playwright 設定（baseURL / timeout / browsers）
```

scenarios.md のテンプレートは `../../layer2-orchestrator/references/e2e-integration.md` §sensors/e2e/規格 を参照。

Priority と実行範囲の対応（Shift Left 基盤は全 Priority 共通で常時整備される前提、階数に加算しない）：
- critical → 第1〜5層すべてを使用（本 E2E 含む）
- standard → 第1〜3層まで使用（本 E2E 含む）
- cosmetic → 第1層のみ使用（本 E2E はスキップ）

### sensors/interaction-cost/（M1/M2/L2 共通、第3層）

5層エラー検出スタック第3層（Interaction Cost 測定）の UX 代理指標閾値。L0 対話ステップ 2.5（UX 3問プロトコル）の回答から生成される。

```
sensors/interaction-cost/
├── thresholds.md     # UX 3問プロトコル Q1 の Must 閾値
└── measurements.ts   # 測定スクリプト（Playwright から呼び出し）
```

thresholds.md のテンプレートは `../../layer2-orchestrator/references/e2e-integration.md` §sensors/interaction-cost/規格 を参照。
未指定時の業界標準値: クリック 3-5 回・遷移 3 以内・応答 30 秒以内・完了率 95%・エラー率 5%。

### sensors/integration/（L2のみ）

L2発動時の統合検証用 sensors。layer2-integration-verifier が参照する。

```
sensors/integration/
├── contracts.md        # ドメイン間インターフェース契約
├── invariants.md       # 全体不変条件
└── e2e.md              # E2Eシナリオ定義
```

---

## モード別の構成差分

モードに応じて生成する構成が変わる。REGIME.md の判定結果に従い、必要な構成のみ生成する。

### M1 単体モード

最小構成。

生成物：
- CLAUDE.md（簡略版、100行以内）
- REGIME.md
- sensors/computational.md のみ
- sensors/inferential.md は**任意**（自己検証で兼用可）
- .claude/skills/ はプロジェクト固有スキルがある場合のみ生成

省略可能な理由：
- 実装規模が小さく、推論的センサーのオーバーヘッドが相対的に大きい
- 単一エージェントで完結するため、SK分離の恩恵が少ない
- 独立検証agentを起動しないので review-checklist は不要

### M2 標準モード

標準構成。以下を全て生成する。

生成物：
- CLAUDE.md
- REGIME.md
- .claude/settings.json
- .claude/skills/ （プロジェクト固有のみ。検証agent本体は Level A 側で持つ）
- sensors/computational.md
- sensors/inferential.md
- sensors/review-checklist.md（layer1-independent-reviewer がプロジェクト固有項目を参照する場合）

layer1-independent-reviewer の扱い：
- skill本体は **Level A** に存在するため、プロジェクトでは再生成しない
- プロジェクト固有の検証観点が必要な場合のみ `sensors/review-checklist.md` を追加

### L2 統括指揮モード（稀・全体の<10%）

M2の構成に加え、L2オーケストレータと統合検証の定義を追加する。

追加生成物：
- DOMAINS.md（ドメイン境界の定義。L2オーケストレータが生成）
- 各ドメイン配下の部分 SPEC（SPEC.md から切り出し）
- sensors/integration/ 配下の統合sensors（contracts.md, invariants.md, e2e.md）

layer2-orchestrator / layer2-integration-verifier の扱い：
- skill本体は **Level A** に存在するため、プロジェクトでは再生成しない
- プロジェクト差異は DOMAINS.md と sensors/integration/ に閉じる

### L0 対話延長（モード確定保留状態）

実装に進まない前段状態。Layer 0の対話を厚くする運用のみ生成する。
**独立モードではなく、M1/M2/L2 確定までの一時的な状態**。

生成物：
- DIALOG-LOG.md（対話履歴の構造化記録）
- REGIME.md（状態として「L0対話延長中」と明記）

仕様が煮詰まったら S/U/R を再算出し、M1/M2/L2 のいずれかに確定する。

---

## コンテキスト注入戦略

### 強制読み込み（常にコンテキストに含める）
- CLAUDE.md
- INDEX.md

### 動的読み込み（必要に応じてエージェントが参照）
- SPEC.md（INDEX.mdから参照）
- DONT.md
- REGIME.md
- sensors/*
- .claude/skills/*
- DOMAINS.md（L2のみ）

### 原則
- 強制読み込みは合計300行以内に抑える
- 動的読み込みファイルへのパスはINDEX.mdに明記する
- エージェントが「何を読めばよいか」を判断できるよう、INDEX.mdの目次を正確に保つ
- REGIME.md はモード分岐判断に使うため、Layer 1 起動時に必ず読み込む

---

## ARCパターン別追加センサー

REGIME.md の ARC 選択に応じて、sensors/ 配下に追加する項目が変わる。
パターン別の詳細は `arc-patterns/{monolith,realtime-pubsub,event-sourcing}.md` の「追加センサー項目」セクションを参照。

### monolith（デフォルト）
- 追加センサーは不要。`sensors/computational.md` と `sensors/inferential.md` のデフォルト構成で充足

### realtime-pubsub
- `sensors/computational.md` に追記: 接続ゲートウェイのロードテスト、ブローカー障害時のフェイルオーバー検証
- `sensors/inferential.md` に追記: 配信レイテンシ p95 の SLO 充足、再接続時の重複排除、接続中ユーザ数と subscriber 数の整合

### event-sourcing
- `sensors/computational.md` に追記: イベントスキーマ互換性チェック、プロジェクション再構築のドライラン
- `sensors/inferential.md` に追記: aggregate 境界と整合性境界の一致、訂正イベントの追記性、最終整合性前提の UI 設計、監査要件充足

### 追加センサーの作成タイミング
ARC が monolith 以外に確定した時点で Layer 0 が sensors/ に該当項目を追記する。
ARC 変更時は sensors/ の再評価が必須（旧パターンの項目は残し、新パターンの項目を追記する）。

---

## プロジェクト固有規約の grep ベースセンサー

CLAUDE.md / SPEC.md に定量的な規約がある場合、grep ベースの簡易センサーで自動検出できる。コストが極小で、推論センサーの取りこぼしを補う相補的な検証手法として位置づける。

### パターン：規約 grep センサー

プロジェクト固有の定量的規約（例：「最小サイズ N×N px」「禁止クラス X」）を grep で機械的に検出するセンサーパターン。L1 実装者が CLAUDE.md の定量規約を参照して grep 式を記述する。

#### 例（Tailwind プロジェクトでのタッチターゲット 44px 規約）

```bash
# NG パターン: w-1〜w-10 / h-1〜h-10 が連続している箇所（44px 未満候補）
# 許容例外はホワイトリストファイルで除外
rg --type tsx 'w-(?:[1-9]|10) h-(?:[1-9]|10)' src/components \
  | grep -v -f .lint-touch-target-allowlist
```

#### センサーへの組み込み方

- **計算的センサーに追加**: `sensors/computational.md` に `npm run lint:rules` 等として追加
- **実行時間制約**: 1 秒以内に完了する制約を守る
- **検出時の出力**: 違反検出時はファイル名と該当行を出力
- **発動条件**: CLAUDE.md / SPEC.md に定量的な規約が記述されている場合のみ
- **対象外**: 定性的な規約（「使いやすくする」等）は対象外

#### 運用上の注意点

- **人手前提**: grep 式の記述は L1 実装者が行う。完全自動生成は想定しない
- **例外管理**: 許容例外は `.lint-[規約名]-allowlist` 等のホワイトリストファイルで管理
- **相補的位置づけ**: crosscut-verifier-drift（SPEC ↔ 実装差分）とは独立したセンサーカテゴリ
- **M1 対応**: M1 でも定量規約がある場合は 1 行の grep は過剰にならない

---

## dialog-harness-layers バージョニング規則

dialog-harness-layers 本体のバージョン管理規則。プロジェクト固有のバージョニングには適用しない。

### メジャー昇格（vN.0 → v(N+1).0）

以下のいずれかに該当する場合：

- 新しい階層の追加（L3 等）※ 現在禁止原則により起きない想定
- 既存 Layer の責務再定義
- フラクタル骨格の変更
- 既存プロジェクトへの後方互換破壊

### マイナー昇格（vN.X → vN.(X+1)）

以下に該当する場合：

- 既存 Layer への新スキル追加
- 配置規則・運用規則の追加
- 検証項目の追加
- 後方互換を保つ拡張

### 判断主体

AI が変更内容から判断し、メジャー昇格時のみ人間に献上する。マイナー昇格は自動記録。

### user-scope との同期

dialog-harness-layers は 2 系統で流通する：

- **配布元（repo 側）**: `dialog-harness` リポジトリ（github.com/samejima-ai/dialog-harness）の `.claude/skills/` 配下（正本）
- **利用者環境（user-scope 側）**: `~/.claude/skills/` 配下にフラット展開されたインストール版

repo 側でバージョン昇格（メジャー／マイナー問わず）を行った場合、user-scope 側への反映は **利用者責務** とする。AI は同期漏れを検出しても自動修復しない（利用者のローカル改変を保護するため）。同期時は skill 本体のみコピーし、`.claude/settings.local.json` 等の環境固有ファイルは除外する。

### バージョン履歴

- v1.0: 二層構想
- v2.0: 検証エージェント
- v3.0: 三層構想＋オーケストレーション
- v3.1: onboarding + 配置規則 + クレジット規格
- v3.2: Archaeology 深度の英語語彙化 + L0 責務分担表 + 参照保持規格の明確化
- v4.0: philosophy.md 5条原典化 + 5層エラー検出スタック + Playwright Test Agents 規格 + SPEC.md 拡張（UX制約・Priority critical/standard/cosmetic） + L0 対話 UX 3問プロトコル + sub-agent-protocol.md（v4.0 リリース時点では旧呼称「処理」で定義されていたが v4.1 で「検出」に改称。以下の歴史記述は最終呼称に正規化して記載する）
- v4.1: Shift Left 基盤 + 5層エラー検出スタック二層モデルへの呼称統一（スタック名の「処理」→「検出」改称、旧「設計時発生防止 層」を Shift Left 基盤として運用スタック外に再配置、第3層 Interaction Cost FAIL の独立カウント化、philosophy.md の配分図を 30/30/20/10/7/3 に修正、土地=基盤・建物=検出スタックの直交二層モデルを明文化）
- v4.2: philosophy 第6条追加（人間 ≒ Council 原則）+ Council Trust Level（CTL）導入 + `~/.claude/council-data/` 横断蓄積 + 事後評価フェーズの厳格な分離 + HANDOFF.md 新設（非エンジニア向け献上物、既存 history/SUMMARY.md と命名分離）+ design-history.md の 6 公理→7 公理拡張 + compute_consensus_mode の CTL 連動拡張

### v3.2 → v4.0 移行ノート

既存プロジェクトを v4.0 harness で扱う際の互換性：

- **SPEC.md の `優先順位: 高/中/低`** はそのまま受理可能。v4.0 の Priority とは以下のマッピングで扱う:
  - 高 → critical（第1〜5層すべて使用、Shift Left 基盤は全 Priority 共通で常時整備）
  - 中 → standard（第1〜3層まで使用）
  - 低 → cosmetic（第1層のみ使用）
- **REGIME.md の `mode: L2`** はそのまま読める。L2 配下構成の明示欄が追加されたが、未記載の場合は L0 差し戻しで補完する
- **sensors/e2e/ と sensors/interaction-cost/** が新設されたが、未整備の場合は DELIVERY.md で L0 に改善提案（タイプC献上）として戻す
- **L1 自己検証フローのステップ 5.5** は追加のみ。既存ステップ番号は変更しない

### v4.1 → v4.2 移行ノート

既存プロジェクトを v4.2 harness で扱う際の互換性:

- **既存 REGIME.md** に CTL 記録がない場合、CTL-0 として運用
  （L0 spec-architect 起動時に `## Council Trust Level` ブロックを自動補完）
- **`~/.claude/council-data/`** が未作成の場合、L0 spec-architect が
  自動生成（コールドスタート、`stats.json` は空テンプレート）
- **既存 DELIVERY.md** はそのまま読める。HANDOFF.md は v4.2 で新規生成のみ
  （既存 delivery/ に HANDOFF.md がない場合、次回献上時に追加生成）
- **既存 history/SUMMARY.md**（L0 振り返り儀式 / 圧縮履歴サマリ）は v4.2 で
  変更なし。HANDOFF.md とは別ファイル・別役割（命名衝突回避）
- **既存 Council 設計**: design-history.md は 6 公理 → 7 公理に拡張。
  council-philosophy.md（§1〜§7）は v4.2 では変更しない。philosophy.md 第 6 条を
  新規原典とし、council scope への波及は v4.3 で再判断
- **compute_consensus_mode のシグネチャ変更**: 引数に `ctl` と `stats` を追加。
  既存呼び出し側は CTL-0 / 空 stats で呼べば従来通り「全件献上」相当の挙動
- **後方互換破壊**: なし

---

## Level C: AI 自律運用（v5.6.0 追加、dev_mode = autonomous の場合のみ）

`dev_mode` が `autonomous` に決定したプロジェクトに対して、autonomous-drive 機構（PR 作成 / 多層検証 / 自動 merge / 次 Issue 着手）を deploy する。各 `autonomous_scope` 値ごとに有効化される機能：

### autonomous_scope: full（デフォルト）

- `templates/github-workflows/auto-merge.yml.template` を `.github/workflows/auto-merge.yml` に配置（placeholder 置換後）
- `templates/github-workflows/gemini-review.yml.template` を `.github/workflows/gemini-review.yml` に配置（placeholder 置換後）
- label 自動作成: `ready-for-ai` / `auto-merge` / `do-not-merge`
- Repository Secrets 設定ガイド表示: `GH_REVIEW_PAT`（Pull requests: Read+Write） / `GEMINI_API_KEY`（Google AI Studio 発行）
- ALLOWED_AUTHORS 確認（hardcode、変更時は spec 改修扱い）

### autonomous_scope: merge_gated

- `gemini-review.yml` のみ配置（auto-merge.yml はスキップ）
- label: `ready-for-ai` のみ自動作成
- Repository Secrets: `GEMINI_API_KEY` のみ必須、`GH_REVIEW_PAT` は任意
- 人間 approve が PR merge 前に必須

### autonomous_scope: custom

- 個別指定。spec-architect 対話で各機能を on/off 確認：
  - auto-merge workflow 配置（y/n）
  - gemini-review workflow 配置（y/n）
  - destructive change detector（v5.6.x patch 候補、未実装）
  - circuit breaker（v5.6.x patch 候補、未実装）
  - label セット個別カスタマイズ
- REGIME.md の `## autonomous_scope` セクションに `custom_config:` を YAML で記録

### deployment 実行主体

`crosscut-autonomous-drive` skill（v5.6.0 で新設）が template 適用を担う。spec-architect が dev_mode `autonomous` 判定後に明示起動する。詳細は `autonomous-drive-deployment.md` 参照。

### Person 責務との対応

`autonomous_scope: full` 時、人間関与は `philosophy.md` 第 7 条 Person 責務 P1〜P4 に集約：
- P1 発案 / P2 ブレスト（Issue 化は AI）/ P3 事後確認・評価 / P4 暴走時介入

---

## Level C 拡張: current_focus と Issue pickup の連動表（v5.7.0 追加）

`autonomous_scope: full` の運用で `crosscut-issue-implementer` workflow（issue-pickup.yml）が稼働する場合、Issue pickup の判定で REGIME.md `## current_focus` フィールドを参照する。

### Issue label と current_focus.type の対応

| Issue label | current_focus.type 整合判定 | 挙動 |
|---|---|---|
| `type:bug` | `bug-fix` と一致 → pickup 候補 | 一致時のみ AI triage 進行 |
| `type:feature` | `feature` と一致 → pickup 候補 | 同上 |
| `type:refactor` | `refactor` と一致 → pickup 候補 | 同上 |
| `type:docs` | `docs` と一致 → pickup 候補 | 同上 |
| `type:chore` | `chore` と一致 → pickup 候補 | 同上 |
| 不一致 | label `focus-mismatch` 自動付与、Issue は close せず一時延期 | current_focus 変更で再 pickup 候補化 |
| label 未指定 | AI triage で Issue 本文から推論、current_focus と照合 | 推論不能なら label `needs-clarification` 付与 |

### dev_mode との関係

| dev_mode | autonomous_scope | issue-pickup.yml | current_focus 参照 |
|---|---|---|---|
| local_only | — | × | 不要 |
| github_assisted | — | × | 任意（記録のみ） |
| autonomous | full | ✅ deploy | ✅ active 機能（pickup 判定で参照） |
| autonomous | merge_gated | △ deploy 可（PR は手動 merge） | ✅ active |
| autonomous | custom | 個別指定 | 個別 |

### deployment 経路

`crosscut-autonomous-drive` skill が `templates/github-workflows/issue-pickup.yml.template` を placeholder 置換して `.github/workflows/issue-pickup.yml` に配置する。`autonomous_scope` 別の deploy 対象は `autonomous-drive-deployment.md` で詳述。

---

## skill description トリガー語彙規約（Wave 1 候補 1、PR #76）

**origin**: ECC-derived（everything-claude-code v2.0.0-rc.1 `agents/*.md` frontmatter の `Use PROACTIVELY when ... Automatically activated for ...` 規約）
**chewing translation**: T2（語彙翻訳、構造保持）
**chewing council ref**: `council-2026-05-11T05:00:00Z-w1qb02`（既存 17 skill description の修正タイミングは「逐次」採決）

### 規約

新規 skill の `SKILL.md` frontmatter `description:` には、AI の自動起動判定を **明示的な日本語動詞** で構造化する。曖昧な期待（「〜できます」「〜のためのスキル」）ではなく契約として語彙化する。

### 推奨語彙（自動起動契約を形成するもの）

| 語彙 | 用途 | 例 |
|---|---|---|
| 「**自動的に検討する**」 | hook 経路や条件成立時の自動発動 | 「hook 経路の発火時に本 skill 起動を自動的に検討する」 |
| 「**明示されなくても起動を必ず検討する**」 | 文脈成立時の主体起動 | 「LC ≥ 1 + REGIME.md 存在時は、明示されなくても起動を必ず検討する」 |
| 「**主体的に発動を検討する**」 | 周辺条件成立での裁量起動 | 「『迷っている』発話を検出した場合、主体的に発動を検討する」 |
| 「**……の発話で本スキルの起動を必ず検討する**」 | trigger 句の正規形 | 既存 17 skill で広く採用済 |

### 禁止語彙

| 禁止 | 理由 |
|---|---|
| `Use PROACTIVELY` | ECC 固有の英語語彙。DH は日本語規約 |
| `Automatically activated for X` | 同上 |
| 「〜できるツールです」「〜を提供します」 | 自動起動契約として弱い、case studies 系の弱発火語彙 |

### 採用例（既存 skill から抜粋）

- `crosscut-autonomous-drive`: 「……等、autonomous-drive 機構の利用者プロジェクトへの配置・workflow テンプレ展開・ラベル/Secrets セットアップに関する発話で本スキルの起動を必ず検討する」
- `layer1-autonomous-dev`: 「明示されなくても本スキルの起動を必ず検討する（コーディングだけでなくビルド・テスト・配布の依頼も含めて……）」
- `crosscut-hook-observer`（Wave 1 新設）: 「hooks.json bootstrap からの自動起動で発動」

### 既存 17 skill 監査タイミング

Council 諮問 `council-2026-05-11T05:00:00Z-w1qb02` の判決により、既存 17 skill の description 監査・修正は **各 skill の次回更新時に逐次** 実施する。

監査チェックリスト: `delivery/SKILL-DESCRIPTION-AUDIT-checklist-wave1.md`（Wave 1 で作成、修正は各 skill 次回更新時に組み込み）。Wave 2 末の振り返り儀式で監査進捗を観測項目化。

---

## templates/rules/ 階層化規約（Wave 1 候補 6、PR #76）

**origin**: ECC-derived（everything-claude-code v2.0.0-rc.1 `rules/` の common + 14 言語別配置 + 相対 `../common/` 参照規約）
**chewing translation**: T1 + T3（構造保持 + サブセット選別：言語先取りなし）
**chewing council ref**: `council-2026-05-11T05:00:00Z-w1qb03`（言語先取りは A: 遅延戦略）

### 規約

`templates/rules/` に **common 規約のみ** scaffold 配置し、言語別 rules は **L0 対話で確定後に必要言語のみ生成** する（DH 流遅延戦略、philosophy 第 1 条フラクタル原則と整合）。

### 配置

```
templates/rules/
├── README.md             # 階層化規約 + override 規則 + 相対参照ルール
└── common/               # 言語横断 rules
    ├── .gitkeep
    ├── agentshield-reference.md           # AgentShield 参照導入規約（Wave 2）
    ├── ui-baseline.rules.md               # UI Baseline RL（v5.23.0、UI 相互作用層・常時適用）
    └── ui-specialization.context.md       # UI 目的特化 S-01〜S-06（v5.23.0、.dh/rules/ で override 可）
```

L0 対話で「多言語プロジェクトか?」「言語別 coding-standards を設けるか?」を確認後、必要な言語の `templates/rules/<lang>/` を生成。詳細は `dialog-questions.md` の「多言語プロジェクト判定」セクション参照。

UI を伴うプロジェクトでは、`common/ui-baseline.rules.md`（相互作用層 RL・常時適用）と `common/ui-specialization.context.md`（目的特化）を共通 RL として開発環境に含める。視覚トークン層（DESIGN.md）との二層関係・B-ID の 5 層検出スタック oracle 化・S-xx 選択の L0 接続は `design-system-spec.md`「UI 相互作用層」を参照。

### 命名衝突回避（ECC 由来規約）

`common/` と `<lang>/` に同名ファイルが存在する場合、`<lang>/` が `common/` を override する。**flatten 配置は禁止**（相対 `../common/` 参照が壊れる）。

詳細は `templates/rules/README.md` 参照。

---

## origin/version frontmatter 規格（Wave 2 候補 2、PR #78）

**origin**: ECC-derived（everything-claude-code v2.0.0-rc.1 `agents/*.md` / `skills/**/SKILL.md` の frontmatter 慣例）
**chewing translation**: T1（構造保持）+ DH 拡張（chewing_translation / chewing_pr / chewing_council_ref フィールド追加）
**chewing council ref**: `council-2026-05-11T07:00:00Z-w2qb03`（既存 17 skill への適用タイミングは「逐次」採決）

### 規約

ECC からの咀嚼で取り込まれた / 取り込まれる skill の `SKILL.md` frontmatter には、素材出自と咀嚼経路を明示する以下のフィールドを **必須** とする:

```yaml
---
name: <kebab-case-skill-name>
dimension: D4
origin: <ECC-derived | DH-native | external>
origin_source: "<ecc:path | url | reference>"
origin_version: "<source version, e.g. ECC v2.0.0-rc.1>"
chewing_translation: "<T1 | T2 | T3 | T1+T3 | T3+ガードレール語彙化 | ...>"
chewing_pr: "<repo#PR_number>"
chewing_council_ref: "<council-ID, optional>"
chewed_at: "<ISO8601 UTC>"
description: ...
---
```

### フィールド意味

| フィールド | 必須 | 意味 |
|---|---|---|
| `origin` | ✓ | 素材出自分類（ECC-derived / DH-native / external） |
| `origin_source` | ECC-derived のみ ✓ | 元素材の参照ポインタ（ecc:path / URL / 参照） |
| `origin_version` | ECC-derived のみ ✓ | 元素材の version 固定（drift verifier 接続点） |
| `chewing_translation` | ECC-derived のみ ✓ | T1/T2/T3 タイプまたは複合表示 |
| `chewing_pr` | ECC-derived のみ ✓ | 取り込み PR 番号 |
| `chewing_council_ref` | 諮問あり時 ✓ | Council invocation_id |
| `chewed_at` | ECC-derived のみ ✓ | 取り込み日時（ISO8601 UTC） |

DH-native skill（origin = DH-native）では `origin_source` 以降は不要（または `chewing_translation: "DH-native"`）。

### 翻訳タイプ語彙

| タイプ | 意味 |
|---|---|
| **T1** | 構造保持（素材構造をそのまま採用） |
| **T2** | 語彙翻訳（Node.js → Python 等の言語翻訳） |
| **T3** | サブセット選別（素材の一部のみ採用、残りは棄却 / 温存） |
| **T1+T3** | 構造保持 + サブセット選別の組合せ |
| **T3+ガードレール語彙化** | サブセット選別 + 適用条件のガードレール明文化（Wave 2 中心戦略） |

複合は `+` で連結。新規パターンは Wave N の Phase B 諮問で確定する。

### 既存 skill への適用タイミング（諮問 w2qb03 採決）

Council 諮問 `council-2026-05-11T07:00:00Z-w2qb03` の判決により、既存 17 skill への frontmatter 適用は **各 skill の次回更新時に逐次** 実施する（Wave 1 諮問 w1qb02 と同型）。

監査チェックリスト: `delivery/SKILL-FRONTMATTER-AUDIT-checklist-wave2.md`。Wave 2 末振り返り儀式で進捗 ≤ 50% なら Wave 3 で一括修正再諮問（minority opinion A 温存先）。

### Wave 1 + Wave 2 で先取り適用済の skill

- `crosscut-hook-observer`（Wave 1 PR #76、5 フィールド適用）
- `crosscut-continuous-learning`（Wave 2 PR #78、7 フィールド適用、chewing_council_ref 含む）

---

## AgentShield 参照導入規約（Wave 2 候補 4、PR #78）

**origin**: ECC-derived（everything-claude-code v2.0.0-rc.1 周辺、`ecc-agentshield` npm package として独立配布、observation: `delivery/refs-draft/ecc/agentshield-spec.md`）
**chewing translation**: T3 + ガードレール語彙化
**chewing council ref**: `council-2026-05-11T07:00:00Z-w2qb02`（哲学者重み増強で `--fix` / `--opus --stream` 経路を棄却）

### 規約

AgentShield（`ecc-agentshield` npm package、102 静的解析ルール × 5 カテゴリ）は DH 自前実装を行わず、**利用者プロジェクト側で手動 install + warn のみ参照導入** とする。

### 採否

| カテゴリ | DH 採用 | 経路 |
|---|---|---|
| Secrets detection | ✓ | warn のみ参照 |
| Permission auditing | ✓ | warn のみ参照 |
| Injection analysis | ✓ | warn のみ参照 |
| Hook risk scoring | ✓ | warn のみ参照 |
| Configuration weaknesses | ✓ | warn のみ参照 |
| **`--fix` 自動修復経路** | ✗ | **棄却**（第 6 条「人間最終承認」侵食） |
| **`--opus --stream` 外部 LLM 経路** | ✗ | **棄却**（独立性原則・観察温存と緊張） |

### 利用者プロジェクトでの導入手順（推奨、自動連携なし）

```bash
# 利用者プロジェクト側で手動 install（DH 側からの強制起動なし）
npm install --save-dev ecc-agentshield
npx ecc-agentshield scan  # warn のみ、--fix なし
```

DH 側 workflow / hooks による自動起動は **行わない**（minority opinion w2qb02 A の温存範囲）。

### DH 自前実装の不存在

Council 諮問 w2qb02 採決により、DH 側に 102 ルールの自前実装は **行わない**。Wave 3 で `v6.0.0` 候補として再評価予定（philosophy 第 8 条候補確定後）。

詳細は `templates/rules/common/agentshield-reference.md` 参照。

---

## philosophy.md 改訂時の手動 CHANGELOG 運用（Wave 3 候補 7、PR #81）

**Council 採決**: `council-2026-05-11T09:00:00Z-w3qb03`（recommended B: 手動運用、自動 emit は不採用）

### 規約

`.claude/skills/layer0-spec-architect/references/philosophy.md` を変更する PR では、同 PR 内で `history/PHILOSOPHY-CHANGELOG.md` に新規エントリを **手動追記** する。

### 追記項目

1. 改訂日時（ISO8601 UTC）
2. 変更条文（第 N 条 新設 / 第 N 条 改訂）
3. 変更概要（1-3 文）
4. Council 採決 invocation_id
5. weighted_score / confidence / category / weights
6. minority opinion 温存条件（該当時）
7. 経験的根拠（観測サンプル数等）
8. 関連 PR

### append-only 性質

過去エントリの編集・削除は **禁止**。philosophy の append-only 性質と整合する。誤記訂正は新規エントリ「<元エントリ ID> の訂正」として追記する。

### 自動 emit 化の再諮問条件（minority opinion w3qb03 A）

Wave 4 末で `history/PHILOSOPHY-CHANGELOG.md` の改訂頻度が **≥ 2 件/Wave** 観測された場合、Wave 5 で自動 emit 化（commit hook or PR action）を再諮問する。手動運用負荷の実観測データに基づく判断。

---

## Wave 末振り返り儀式テンプレート（Wave 3 候補 8、PR #81）

**Council 採決**: `council-2026-05-11T09:00:00Z-w3qb04`（諮問省略、`confidence ≥ 0.7`）

### 規約

Wave 完遂時、`templates/rituals/wave-end-retrospective.template.md` をコピーして `history/wave<N>/RITUAL-<YYYY-MM-DD>-wave<N>.md` を作成し、振り返り儀式を実施する。

### Wave 1 の例外

Wave 1 の `history/wave1/RITUAL-2026-05-11-metaskill.md` は本テンプレート不在の時期に個別形式で記録された。Wave 2 は振り返り儀式記録ファイル自体が不在（PR #79 archive 整理時に確認）。Wave 3 以降は本テンプレート準拠とする。

詳細は `templates/rituals/wave-end-retrospective.template.md` 参照。
