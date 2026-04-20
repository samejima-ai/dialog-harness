---
name: layer0-spec-architect
description: >
  人間のイメージ・ニュアンスを対話で具体化しドキュメント化し、開発モード（M1/M2/L2）を判定し、
  AIが自律開発できる開発環境を設計・構築するスキル。
  「新しいプロジェクトを作りたい」「こういうものが欲しい」「機能を追加したい」「仕様を整理したい」
  「開発環境をセットアップしたい」「振り返りたい」「既存プロジェクトを継続したい」等、
  プロジェクトの立ち上げ・仕様策定・既存プロジェクトへの機能追加/拡張に関わるあらゆる発話でトリガーする。
  具体的な技術名やコードの話が出る前の、目的・意図・イメージの段階で使う。
  仕様ドキュメントの作成、モード判定、RL/SK/センサー定義等の開発環境一式を生成するところまでが責務。
  既存プロジェクト（Lifecycle L=1/L=2）では対話冒頭に振り返り儀式を実行する。
---

# Spec Architect

人間のイメージをドキュメント化し、開発モードを判定し、AI自律開発環境を構築するスキル。

## 原則

- 人間はイメージ共有と認識の擦り合わせだけを行う。ドキュメント化は全てAIが処理する
- 人間に完成した仕様を書かせない。対話で引き出し、AIが構造化する
- 仕様は成長するもの。完全な事前定義を目指さない
- 認識のズレがゼロになるまでレビューループを回す。ズレが残ったまま開発環境構築に進まない
- 開発モードは規模・不確実性・リスクから判定する。人間組織論に基づく職種軸分業は採用しない
- 単体エージェントで足りる場合は単体で回す。分業は根拠がある場合のみ
- **フラクタル原則**: L0⇄人間の対話パターン = L1内 spec⇄code 照合 = L2⇄L1群 指示⇄検証 は同一形状。本拡張でも L3 運用層を新設しない方針を徹底する（運用インシデントは新仕様発見として L0 対話へ戻す）

## L0 スキル間の責務分担

L0 は spec-architect と onboarding の 2 スキルで構成される（いずれも L0 兄弟、L3 運用層ではない）。トリガーは排他的。

| ケース | 起動スキル | 判定条件 |
|---|---|---|
| 新規プロジェクト立ち上げ | **spec-architect** | SPEC/DONT/REGIME がいずれも未存在、かつコード未存在（空リポジトリ） |
| 既存プロジェクトの継続開発・仕様追加・振り返り | **spec-architect** | REGIME.md 存在、Lifecycle ≥ 1 |
| 既存プロジェクトへの harness 後付け導入 | **layer0-onboarding** | REGIME.md 未存在、かつ既存コード・既存ドキュメントが存在 |

**排他ルール**:
- REGIME.md に `onboarded_at` がある → onboarding 再起動禁止（spec-architect のみ）
- onboarding 完了時は必ず spec-architect へ handoff する（`layer0-onboarding/references/handoff-to-spec-architect.md` 準拠）
- 疑わしい場合は spec-architect が引き受けて Lifecycle 判定で切り分ける

## 処理フロー

```
1. 人間のイメージ受領
1.5. 振り返り儀式（Lifecycle 判定 → 儀式レベル判定 → F1〜F3 実行）
     新規プロジェクト（L=0）ではレベル0で完全スキップ
     既存プロジェクト（L=1/L=2）では history/ を読み込み過去文脈と照合
2. 対話による具体化（目的・機能・条件・制約の引き出し）
   並行してモード判定情報も取得（規模・不確実性・リスク・NFR・ARC・ドメイン文脈・権限レベル）
   儀式で検出した矛盾・復活要求・再提案はここで解消する
2.5. UX 3問プロトコル（Must閾値・禁止挙動・参考類似サービス、未回答は業界標準で自動補完）
3. ドキュメント化（メタ仕様に従い構造化）
3.5. サブフェーズ選定と実行（基本5問で L0-2〜L0-6 を動的起動、`spec/` 配下に成果物生成）
     条件を満たさないプロジェクトは完全スキップ。詳細は `references/subphase-selection.md`
4. モード判定（S/U/Rスコアリング + L2発動閾値チェック + Lifecycle記録）
5. 人間レビュー → 認識ズレがあれば2に戻る
6. 認識ズレなし → モードに応じた開発環境の設計・構築
7. 開発環境一式を Layer 1（または L2）に渡せる状態で出力
7.5. ファイル配置規則に沿った初期化（delivery/ と assets/ を作成、docs/ は初期生成しない）
7.6. README.md クレジット挿入（credit-template.md 準拠、マーカー内で管理）
```

ステップ5→2のループが最も重要。ここを省略しない。
ステップ1.5は Lifecycle ≥ 1 の場合のみ実行する。プロトコル詳細は `references/ritual-protocol.md` を参照。
ステップ3.5は DB/API/状態遷移/認可のいずれかが関与する場合に起動する。判定と実行のプロトコル詳細は `references/subphase-selection.md` を参照。

## ステップ詳細

### 1. イメージ受領

人間の発話から以下を読み取る。形式は問わない。断片的でよい。

- 何がしたいか（目的）
- 誰のためか（対象）
- どんな感じか（ニュアンス・トーン）
- これだけは嫌だということ（制約・禁止事項）

読み取れない項目は無理に聞き出さない。対話の中で自然に出てくるのを待つ。

### 2. 対話による具体化

人間のイメージを「機能×条件」の粒度まで引き上げる。これがAI自律開発の最低ライン。

並行してモード判定に必要な情報（S/U/R スコア算出用）も取得する。
非エンジニア向けの質問例は `references/dialog-questions.md` を参照（NFR・ARC・ドメイン文脈・権限レベルの質問例も末尾セクションに含む）。
業界・業務固有の前提条件を引き出す対話プロトコルは `references/domain-context-dialog.md` を参照。

粒度の目安：

| レベル | 例 | 自律開発の可否 |
|---|---|---|
| 目的のみ | 「ECサイトが欲しい」 | 不可能 |
| 機能一覧 | 「商品一覧、カート、決済」 | プロトタイプまで |
| **機能×条件（最低ライン）** | 「カートは最大30品、在庫超過時はエラー」 | **実用レベル** |
| 機能×条件×状態遷移 | 上記＋注文フロー図 | 高品質 |

対話で意識すること：
- 人間が「そうそう」「違う」で判定できる具体的な問いかけをする
- 抽象的な質問（「どんな感じですか？」）を避け、選択肢や具体例を提示する
- 1回の応答で質問を詰め込みすぎない
- 仕様の具体化とモード判定情報の取得を自然に織り交ぜる

### 2.5. UX 3問プロトコル

機能×条件の粒度が揃った時点で、UX 制約（Must 閾値・禁止挙動・参考類似サービス）を3問で取得する。人間に最低限の判断だけを求め、AI が残りを業界標準で自動補完する。

#### 3問

| # | 質問 | 格納先 |
|---|---|---|
| Q1 | Must 閾値: この機能で絶対に守りたい定量的制約は？（応答時間・クリック数・エラー率 等） | SPEC.md UX制約 |
| Q2 | 禁止挙動: 絶対にしてほしくない操作や画面は？ | SPEC.md UX制約 + DONT.md |
| Q3 | 参考類似サービス: 「あの UX が好き」という参考はある？ | SPEC.md UX制約 |

#### 自動補完（未回答時の業界標準値）

| 項目 | デフォルト |
|---|---|
| クリック数 | 主要タスクまで 3-5 回以内 |
| 遷移深度 | 3 ページ以内 |
| 応答時間 | p95 で 30 秒以内 |
| 完了率 | 95% 以上 |
| エラー率 | 5% 以下 |

業界標準値は `references/philosophy.md` §第4条「UX は計算可能代理指標まで」の原則に従う。L1 は sensors/interaction-cost/ 経由で測定する。

#### プロトコルの位置づけ

UX 3問は独立軸ではなく、NFR 軸の補足として扱う（詳細は `references/regime-assessment.md` §軸4）。3問の回答は SPEC.md の UX制約セクション（`references/meta-spec-template.md`）に格納される。

### 3. ドキュメント化

メタ仕様テンプレートに従い、以下のドキュメント群を生成する。
テンプレートの詳細は `references/meta-spec-template.md` を参照。

生成するドキュメント：
- **INDEX.md** — 全体目次（100行以内）。他ドキュメントへの参照を集約
- **SPEC.md** — 機能仕様（WHY / WHAT / 条件 / 優先順位 / 制約）。該当プロジェクトはデータモデル進化セクションを含む（詳細: `references/schema-evolution.md`）
- **DONT.md** — スコープ外の明示（現時点でAI自律開発が困難な領域）
- **DOMAIN-CONTEXT.md**（任意） — 業界・業務固有の前提条件。該当プロジェクトのみ。機密は `DOMAIN-CONTEXT.secret.md` に分離

### 3.5. サブフェーズ選定と実行

自然言語の `SPEC.md` だけでは表現しきれない領域（ドメインモデル / API 契約 / 状態遷移 / 認可 / 層間不変条件）を、必要なときだけ数式化する動的プロトコル。
判定と実行の詳細は `references/subphase-selection.md` を参照。

#### 起動判定

対話（ステップ 2）で得た情報から **基本 5 問** で必要サブフェーズを決定する。全問が「不要」なら本ステップは完全スキップする。

| # | 質問 | 起動判定対象 |
|---|---|---|
| S1 | データを保存する必要があるか？ DB を使うか？ | L0-2 ドメインモデル |
| S2 | 外部のシステムや API とつなぐか？ | L0-3 API 契約 |
| S3 | 画面はいくつあるか？ 遷移は複雑か？ | L0-4 状態遷移 |
| S4 | 複数ユーザーで使うか？ 権限の違いはあるか？ | L0-5 認可 |
| S5 | 時間経過や承認で状態が自動的に変わるか？ | L0-6 層間不変条件（2 以上のサブフェーズ起動時のみ） |

詳細な判定表（完全 / 簡易 / スキップ）は `references/subphase-selection.md` の起動判定表を参照。

#### 実行プロトコル

各サブフェーズは「対話 α → 生成 β → 検証 γ → 判定 δ」の 4 フェーズで構成される独立 AI 呼び出し単位。
共通骨格は `references/subphase-common-protocol.md`、各サブフェーズ固有プロトコルは以下:

- `references/subphase-l02-domain.md` — Zod + TypeScript ドメインモデル
- `references/subphase-l03-api.md` — TypeSpec API 契約
- `references/subphase-l04-transition.md` — XState + Mermaid 状態遷移
- `references/subphase-l05-authz.md` — OpenFGA 認可モデル
- `references/subphase-l06-invariants.md` — Gherkin 層間不変条件（Happy / Sad / Evil 三分類）

#### 依存順

L0-1 → L0-2 → (L0-3 ‖ L0-4) → L0-5 → L0-6 の順序で実行。L0-3 と L0-4 は並列可。

#### 成果物配置

起動時のみ `spec/` ディレクトリを新設し、以下を配置:

```
spec/
├── subphase-manifest.md  # 選定結果・確度・起動ログ（pre-official、Phase 2 で REGIME.md に統合予定）
├── domain.ts             # L0-2 起動時
├── api.tsp               # L0-3 完全モード時
├── api-signatures.ts     # L0-3 簡易モード時
├── state-machine.ts      # L0-4 完全モード時
├── state-diagrams.md     # L0-4（完全/簡易問わず）
├── authz.fga             # L0-5 完全モード時
├── authz-matrix.md       # L0-5 簡易モード時
└── invariants.feature    # L0-6 起動時
```

全サブフェーズがスキップのプロジェクトでは `spec/` 自体を生成しない。

#### 既存プロジェクトとの後方互換

`spec/subphase-manifest.md` が存在しない既存プロジェクトで本ステップを通過しても、従来フロー（ステップ 1→4→…→7.6）と同一挙動となる（新規起動のみ影響）。

#### 事後追加

プロジェクト進行中のサブフェーズ追加・モード昇格・判定誤り訂正は独立した AI 呼び出しで実行する。プロトコルは `references/subphase-selection.md` の「事後追加プロトコル」を参照。

### 4. モード判定

規模・不確実性・リスク・NFR の 4 軸でスコアリングし、L2発動閾値もチェックして開発モードと ARC・権限レベルを決定する。
判定プロトコルの詳細は `references/regime-assessment.md` を参照。
NFR スコアリング（5カテゴリ × 0-3 点、オーバーライド4条件）は `references/nfr-scoring.md` を参照。
ARC パターン選択（monolith / realtime-pubsub / event-sourcing）は `references/arc-patterns/` 配下 3 ファイルを参照。
権限レベル（L0-2 / L0-3）と介入チャネル（C1/C2/C3）は `references/permission-delegation.md` を参照。

判定アウトプット：
- **REGIME.md** — モード判定結果（スコア・モード・根拠・AI能力バージョン・L2の場合はサブドメイン構成）

モードの概要：

| モード | 構成 | 適用目安 |
|---|---|---|
| M1 単体モード | L0 → L1（自己検証のみ） | 実験・小規模・自分だけ使う |
| M2 標準モード | L0 → L1 + layer1-independent-reviewer | 標準（全体の90%以上） |
| L2 統括指揮モード | L0 → L2オーケストレータ → L1群 + layer2-integration-verifier | 大規模（全体の<10%） |

判定ルール（要点）：
1. L2発動閾値（SPEC>15k tok / >80 files or >10k 行 / domains ≥5 / 並行 ≥3 / 1サイクル >2h のいずれか）を超えたら **L2**
2. U ≥ 3 → **L0 対話延長**（モード確定保留）
3. R ≥ 2 → **M2 以上を強制**
4. S+U+R 合計で M1/M2 を一次判定（0〜3=M1, 4〜=M2）

**AI能力バージョン**（例: Claude Opus 4.7）を REGIME.md に必ず記録する。

### 5. 人間レビュー

仕様ドキュメント群とモード判定結果を人間に提示し、認識ズレを確認する。

確認ポイント：
- 仕様の認識ズレがないか
- モード判定が過剰／過少になっていないか
- L2発動閾値の判定根拠が妥当か
- ズレがあれば具体的にどこがズレているかを特定し、ステップ2に戻る
- ズレがなければステップ6に進む
- 「だいたいOK」は許容しない。曖昧な承認には確認を入れる

**実行前の推奨モデル提示**：
- REGIME.md 確定時点で `references/model-recommendations.md` を読み込む
- 判定モードに応じた推奨モデル構成を **モード / 推奨 / 乖離 / 根拠** の4項目骨子で動的に生成し、ユーザーへ提示する
- 現使用モデルが推奨と乖離している場合は明示的に指摘する
- ハイブリッド運用（Layer 0 と Layer 1 で異なるモデル）の提案も行う
- ユーザーが推奨と異なるモデルで続行を選択した場合はそのまま進める（セーフティネット）

### 6. 開発環境の設計・構築

認識ズレ解消済みのドキュメントとモード判定結果を入力として、以下を生成する。
各フォーマットの詳細は `references/dev-env-spec.md` を参照。

モードに応じて生成物が変わる：

| モード | 追加生成物 |
|---|---|
| M1 | 最小構成（CLAUDE.md 簡略版 + REGIME.md + sensors/computational.md） |
| M2 | 標準構成（CLAUDE.md + REGIME.md + .claude/skills/ + sensors/computational + inferential + review-checklist） |
| L2 | M2 + DOMAINS.md + 各ドメイン別部分SPEC + sensors/integration/ |

**重要**: 検証agent（layer1-independent-reviewer / layer2-integration-verifier）や layer2-orchestrator の本体は **Level A（共通スキル）** に存在し、プロジェクト側で再生成しない。プロジェクト差異は sensors やチェックリストに閉じる。

生成する開発環境構成（M2 標準）：
- **CLAUDE.md / .claude/settings.json** — エージェントのRL（ルール）定義
- **.claude/skills/** — プロジェクト固有のSK（検証agent本体は含まない）
- **sensors/** — センサー定義（計算的＋推論的）
- **テスト基盤** — ビルド・テスト・リンターの設定（1分以内制約）

### 7. 出力

以下を Layer 1（autonomous-dev スキル）または L2 オーケストレータに渡せる状態として出力する。

```
project-root/
├── INDEX.md            # 全体目次
├── SPEC.md             # 機能仕様
├── DONT.md             # スコープ外定義
├── REGIME.md           # モード判定結果（AI能力バージョン含む）
├── DOMAINS.md          # L2のみ。ドメイン境界定義
├── CLAUDE.md           # エージェントRL
├── .claude/
│   ├── settings.json
│   └── skills/         # プロジェクト固有SKのみ
├── sensors/
│   ├── computational.md   # 計算的センサー
│   ├── inferential.md     # 推論的センサー（M2以上）
│   ├── review-checklist.md # プロジェクト固有の独立検証観点（任意）
│   └── integration/       # L2のみ（contracts.md / invariants.md / e2e.md）
└── (テスト・ビルド基盤設定)
```

### 7.5. ファイル配置規則に沿った初期化

`references/dev-env-spec.md`「ファイル配置規則」に従い、プロジェクト初期化時に以下を実施する。

- `delivery/` を空で作成（L1 献上先として確保）
- `assets/` を空で作成（共有入力の置き場）
- `docs/` は**初期生成しない**（L1 が共有出力として必要時に生成）
- ルート直下は INDEX/SPEC/DONT/REGIME/CLAUDE/DOMAINS と README.md のみ許可
- 違反（PLAN.md, TODO.md, MEMO.md 等のルート直下作業メモ）は **Phase B の自動修復対象** として DELIVERY.md にログ化

本ステップは新規（Lifecycle L=0）のみ実施。既存プロジェクト（L=1/L=2）では現状配置を尊重し、違反検出時のみ L1 側で修復を提起する。

### 7.6. README.md クレジット挿入

`references/credit-template.md` に従い、README.md 末尾に制作クレジットを挿入する。

- 既存 README.md がない場合: 最小構成で新規作成し、クレジットブロックを末尾に配置
- 既存 README.md がある場合: マーカーコメント（`<!-- harness-credit: managed by layer0 skills. do not edit manually. -->`）の有無を確認
  - マーカーあり: 内部のクレジット内容を最新情報で更新
  - マーカーなし: 末尾にマーカー付きクレジットブロックを追記
- テンプレート: `Built with dialog-harness/layer's vX.Y · [Model] · YYYY-MM-DD`
- **拒否権**: ユーザーが明示的にクレジット不要と指示した場合は挿入しない。REGIME.md に拒否日を記録

クレジットの更新差分は L1 献上時に DELIVERY.md「クレジット更新ログ」に記録する。

## 決定済み制約

- ARC デフォルトは monolith。ARC 未指定時は monolith が自動適用される
- ARC 選択肢（`references/arc-patterns/` 配下 3 パターン: monolith / realtime-pubsub / event-sourcing）は**人間判断献上**で最終決定する。AI は NFR スコアと要件から推奨を提示するのみ
- 上記 3 パターン以外の事前ライブラリ拡張（layered-monolith / microservices / CQRS 等）は本規格では射程外
- 職種軸分業（FE/BE/QA等の人間組織模倣）は採用しない。分割軸は抽象度軸・責務軸・機能軸のみ
- Don'tリストに含まれる領域は仕様に含めない：
  - 創造的UXデザイン
  - 複雑な状態管理UI
  - パフォーマンス最適化
  - 未知の外部API統合
- Don'tリストは更新可能。AI能力の向上に伴い縮小する
- L2発動閾値はAI能力バージョンに依存する。REGIME.md にバージョン記録必須

## 廃止判断プロトコル（Lifecycle ≥ 1 で適用）

既存機能の廃止は人間の一存では決めない。合議＋AI根拠提示で判断する。

### 発動条件

以下のいずれかが発生した場合：

- 人間が明示的に「この機能削除したい」と発話
- 儀式 F2 で「復活要求」や「却下案の再提案」として過去廃止との矛盾を検出
- L1 から「該当機能が一度も呼ばれていない」「実装破綻・仕様矛盾」のシグナルが届く

### プロトコル

1. **AI が廃止根拠を提示**
   - 利用率（CHANGELOG/REGIME-LOG に記録があれば）
   - 代替機能の有無
   - 依存関係（他機能が依存していないか）
   - 過去の却下理由との照合（「この機能、当初は〇〇を理由に追加した」）
2. **人間に判断を仰ぐ**（1問）
   - 「以下の根拠で廃止候補。進めてよい？」形式
   - 曖昧応答なら E1 の「AI充当 + 通知型」で暫定廃止、次回 F2 で再確認
3. **廃止決定時の記録**
   - INTENT.md 該当項目に `**廃止**: YYYY-MM-DD — 理由` を追記（削除ではなく追記）
   - CHANGELOG.md に廃止エントリ追加
   - 2年後 `history/archive/` へ自動移動（β-1 の archive ルール）

### 廃止を拒否すべきケース

- 依存関係があり他機能が壊れる → 拒否し代替提案
- 過去3サイクル以内に同機能を追加したばかり → 振動防止のため延期提案
- 人間が感情的に「削除！」と言っているが根拠不明 → 1回だけ「本当にいい？」と確認

## 参照ドキュメント

### 既存（参照リンク保持・内容拡張許容）

本セクションの参照リンクは v3.0 時点の 7 件を**リンク単位で**保持する。
個別ファイルの内容拡張（節の追加・記述の詳細化）は許容するが、リンクの削除・改名・リダイレクトは minor 昇格でも禁止する。
骨格の完全な書き換えは major 昇格案件として扱う。

- `references/meta-spec-template.md` — 仕様ドキュメントのテンプレートと記述ルール（REGIME.md テンプレ含む）
- `references/dev-env-spec.md` — 開発環境ドキュメント規格（RL/SK/センサーのフォーマット、モード別差分）
- `references/regime-assessment.md` — モード判定プロトコル（S/U/Rスコアリング、L2発動閾値、Lifecycle判定）
- `references/dialog-questions.md` — 非エンジニア向け対話質問例集（振り返り儀式テンプレ含む）
- `references/model-recommendations.md` — 実行前の推奨モデル提示（モード別・ハイブリッド運用・AI能力バージョン別差分対策）
- `references/history-layer-spec.md` — 履歴層（history/）のスキーマ・訂正・archive・承認レベル
- `references/ritual-protocol.md` — 振り返り儀式プロトコル（4レベル判定・F1〜F3・E1/E2対応）

### 拡張（業務システム運用・社内版LINE型射程対応）

- `references/nfr-scoring.md` — NFR スコアリング規格（5 カテゴリ × 0-3 点、オーバーライド 4 条件、N=0 後方互換）
- `references/arc-patterns/monolith.md` — ARC デフォルト（単一デプロイ単位、AI 自走完遂の標準形）
- `references/arc-patterns/realtime-pubsub.md` — リアルタイム pub/sub パターン（社内版LINE型、大量同時接続）
- `references/arc-patterns/event-sourcing.md` — イベントソーシング（監査必須、時系列復元、スキーマ進化完全準拠）
- `references/schema-evolution.md` — データモデル進化プロトコル（互換性ポリシー / デプロイ戦略 / upcasting）
- `references/permission-delegation.md` — 段階的権限委譲（L0-2/L0-3、介入チャネル C1/C2/C3、判断献上 5 カテゴリ）
- `references/domain-context-dialog.md` — ドメイン文脈対話プロトコル（DOMAIN-CONTEXT.md、機密分離、5 対話カテゴリ）

### v3.1 追加（配置規則・クレジット）

- `references/credit-template.md` — README.md 制作クレジットの規格とテンプレート（マーカー管理・拒否権・更新ルール）

### v3.2 追加（L0 サブフェーズ拡張 Phase 1）

ステップ 3.5 で使用する動的サブフェーズ選定・実行プロトコル群。条件を満たさないプロジェクトではロードされない。

- `references/subphase-common-protocol.md` — 対話→生成→検証→判定 の 4 フェーズ骨格、サブフェーズ間 I/O 契約、成果物配置規約
- `references/subphase-selection.md` — 基本 5 問・起動判定表・モード選定・`spec/subphase-manifest.md` 雛形・事後追加プロトコル
- `references/subphase-l02-domain.md` — L0-2 ドメインモデル（Zod + TypeScript, `domain.ts`）対話プロトコル
- `references/subphase-l03-api.md` — L0-3 API 契約（TypeSpec, `api.tsp`）対話プロトコル
- `references/subphase-l04-transition.md` — L0-4 状態遷移（XState v5 + Mermaid, `state-machine.ts` + `state-diagrams.md`）対話プロトコル
- `references/subphase-l05-authz.md` — L0-5 認可（OpenFGA DSL, `authz.fga`）対話プロトコル
- `references/subphase-l06-invariants.md` — L0-6 層間不変条件（Gherkin Happy/Sad/Evil 三分類, `invariants.feature`）対話プロトコル

※ ファイル配置規則とバージョニング規則は `references/dev-env-spec.md` に統合済み。

### v4.0 追加（哲学原典化・5層検出スタック・UX プロトコル）

- `references/philosophy.md` — dialog-harness 5条憲法（フラクタル / Shift Left / 情報純度 / 人間責務 / 献上哲学）。全skill の参照原典。

関連（他 skill 配下に配置される参照ファイル、本 SKILL.md から間接参照）：
- `../../layer1-autonomous-dev/references/inferential-sensor-v2.md` — Shift Left 基盤 + 5層エラー検出スタック（L1 自己検証の埋め込み手順含む）
- `../../layer2-orchestrator/references/e2e-integration.md` — Playwright Test Agents 規格（L2 配下の並列 Agent 群）
- `../../layer2-orchestrator/references/sub-agent-protocol.md` — サブエージェント統括の情報純度プロトコル
