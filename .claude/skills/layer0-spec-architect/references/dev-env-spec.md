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
- layer1-autonomous-dev
- layer1-independent-reviewer
- layer2-orchestrator
- layer2-integration-verifier

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

- **ルート直下規格ファイル**: INDEX.md, CLAUDE.md, SPEC.md, DONT.md, REGIME.md, DOMAIN-CONTEXT.md
- **sensors/**: センサー定義
- **history/**: 履歴層（Lifecycle ≥ 1）
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
- HISTORY-DIFF.md（Lifecycle ≥ 1 で必須）

#### 成果物（任意）

- src/ / tests/ 等の実装ディレクトリ（プロジェクト方針による）

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
