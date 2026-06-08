---
name: layer0-spec-architect
dimension: D4
description: >
  人間のイメージ・ニュアンスを対話で具体化し SPEC/DONT/REGIME/CLAUDE 等の仕様ドキュメント群を生成、
  開発モード（M1/M2/L2）と dev_mode（local_only/github_assisted/autonomous）を判定し、
  AI が自律開発できる開発環境一式（RL/SK/センサー）を設計・構築する L0 スキル。
  L0 三兄弟の中で **新規プロジェクト立ち上げ + 既存プロジェクト（LC ≥ 1）の継続開発・仕様追加・振り返り** を担当する。
  「新しいレシピアプリ作りたい、まだイメージしかない」「既存プロジェクトに通知機能追加したい」
  「前回作ったやつ振り返りたい、機能拡張前に」「DB 使うか迷ってる、保存いるか決まってない」
  「M2 と L2 の境界が分からない、判定して」「L0-5 認可サブフェーズ起動して」
  「dev_mode を github_assisted から autonomous に昇格、ADR 込みで」
  等、目的・意図段階の対話と仕様策定全般で本スキルの起動を必ず検討する。
  既存プロジェクト（REGIME.md 存在 + LC ≥ 1）への SPEC 改変を伴う機能追加は autonomous-dev ではなく必ず本スキル経由。
  「リファクタしたい、コードの意図が分からない」（→ archeo-architect / 自動起動しない明示トリガー）
  「既存プロジェクトを harness 化、後付け onboarding」（→ onboarding / 1 プロジェクト 1 回限定）
  「実装して、ship、SPEC 確定済み」（→ autonomous-dev）「Issue にして」（→ issue-dispatcher）
  との混同を避ける（同類発話「整理したい」「ドキュメント化」は文脈で兄弟に振り分ける）。
  具体的な技術名やコードの話が出る前の、目的・意図・イメージの段階で使う。
  既存プロジェクト（LC=1/LC=2）では対話冒頭に振り返り儀式を実行する。
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
- **対話 persona の二層分離（v5.17.0 追加）**: 応答出力（presentation layer）と仕様策定の判断（logic layer）は分離する。persona は presentation のみを差し替える。philosophy 第 6 条「人間最終承認」は logic 側で守られる。詳細は `references/persona-spec.md` を参照。

### L0 完了の受け入れ基準（v5.1.0 追加）

ドキュメント生成の完了は L0 完了とは見なさない。次の 4 条件を全て満たしてはじめて L1 へ譲渡する：

1. SPEC.md / DONT.md / REGIME.md が `references/dev-env-spec.md` の必須項目を全て満たす
2. `references/scaffold-checklist.md` の対応 stack テンプレートで指示されたファイル群が実体として生成済み
3. scaffold smoke test（最小起動コマンド）が通る、または通らない場合は理由を DELIVERY 等に明記
4. §7.4 自己検証（broken reference / DONT 自己照合 / Pre-flight 充足）が PASS

このいずれかが未達のまま L1 へ譲渡することは原則違反。LC ≥ 1 の既存プロジェクトでは、本基準は v5.1.0 以降に追加開始する機能・フェーズに段階適用する（既存成果物の遡及修正は要求しない）。

## L0 スキル間の責務分担

L0 は spec-architect / onboarding / archeo-architect / reindex-librarian の 4 スキルで構成される（いずれも L0 兄弟、L3 運用層ではない）。トリガーは排他的。

| ケース | 起動スキル | 判定条件 |
|---|---|---|
| 新規プロジェクト立ち上げ | **spec-architect** | SPEC/DONT/REGIME がいずれも未存在、かつコード未存在（空リポジトリ） |
| 既存プロジェクトの継続開発・仕様追加・振り返り | **spec-architect** | REGIME.md 存在、LC ≥ 1 |
| 既存プロジェクトへの harness 後付け導入 | **layer0-onboarding** | REGIME.md 未存在、かつ既存コード・既存ドキュメントが存在 |
| 既存コードのリファクタ前 意図復元（v5.4.0 追加） | **layer0-archeo-architect** | REGIME.md 存在、LC ≥ 1、人間が「リファクタしたい / 意図がわからない / 整理したい」等を明示 |
| 蓄積 history の再蒸留・結晶化・抜け殻排出（v5.19.0 追加） | **layer0-reindex-librarian** | REGIME.md 存在、LC ≥ 1、history 層が token 閾値超過（リズム）または人間が「reindex / 結晶化 / 代謝 / 抜け殻を archive」を明示 |

**排他ルール**:
- REGIME.md に `onboarded_at` がある → onboarding 再起動禁止（spec-architect / archeo-architect のみ）
- onboarding 完了時は必ず spec-architect へ handoff する（`layer0-onboarding/references/handoff-to-spec-architect.md` 準拠）
- archeo-architect は **再利用可能**（onboarding と異なり使い捨てではない）。リファクタ着手の度に再起動可能。複数回の起動履歴は `delivery/refactor-intent-map-*.md` のタイムスタンプで識別する
- archeo-architect は **自動起動しない**。人間明示トリガーのみで起動する。ritual-protocol レベル 3 でリファクタ示唆を検出した場合も、起動推奨提示にとどめる
- spec-architect と archeo-architect は **同時起動禁止**（対話方向の混線を避けるため）。spec-architect が起動中に意図復元の必要性を検出した場合は、当該対話を完了させてから archeo-architect の起動を提案する
- reindex-librarian と spec-architect も **同時起動禁止**（Reindex は履歴起点、Scaffold は対話起点で方向が逆）。spec-architect 対話中に history 肥大・購読量膨張を検出した場合は、当該対話を完了させてから reindex-librarian の起動を提案する（自動起動せず提案にとどめる）。なお Scaffold（対話起点の spec 新規設計）の実体は spec-architect であり、reindex-librarian は概念上の双対として参照する
- 疑わしい場合は spec-architect が引き受けて LC 判定で切り分ける

## 処理フロー

```
0. 対話 persona ロード（v5.17.0 追加。REGIME.md `persona.active` または default を読み込む）
1. 人間のイメージ受領
1.5. 振り返り儀式（LC 判定 → 儀式レベル判定 → F1〜F3 実行）
     新規プロジェクト（LC=0）ではレベル0で完全スキップ
     既存プロジェクト（LC=1/LC=2）では history/ を読み込み過去文脈と照合
2. 対話による具体化（目的・機能・条件・制約の引き出し）
   並行してモード判定情報も取得（規模・不確実性・リスク・NFR・ARC・ドメイン文脈・権限レベル）
   儀式で検出した矛盾・復活要求・再提案はここで解消する
2.5. UX 3問プロトコル（Must閾値・禁止挙動・参考類似サービス、未回答は業界標準で自動補完）
2.6. C5 テスト oracle 言語化（人間の暗黙の関心を 3 問で言語化し相 B E2E 母集団を SPEC へ確定）
     critical journey or UI を持つプロジェクトでのみ起動。詳細は `references/test-oracle-dialog.md`
3. ドキュメント化（メタ仕様に従い構造化）
3.5. サブフェーズ選定と実行（基本5問で L0-2〜L0-6 を動的起動、`spec/` 配下に成果物生成）
     条件を満たさないプロジェクトは完全スキップ。詳細は `references/subphase-selection.md`
3.6. DESIGN.md 生成判定（UI 有無を 1 問で確認、UI ありなら 3 問で視覚仕様を取得）
     非 UI プロジェクト（CLI / API サーバ / ライブラリ）は完全スキップ。詳細は `references/design-system-spec.md`
4. モード判定（S/U/Rスコアリング + L2発動閾値チェック + LC 記録）
5. 人間レビュー → 認識ズレがあれば2に戻る
6. 認識ズレなし → モードに応じた開発環境の設計・構築
7. 開発環境一式を Layer 1（または L2）に渡せる状態で出力
7.5. ファイル配置規則に沿った初期化（delivery/ と assets/ を作成、docs/ は初期生成しない）
7.6. README.md クレジット挿入（credit-template.md 準拠、マーカー内で管理）
```

ステップ5→2のループが最も重要。ここを省略しない。
ステップ1.5は LC ≥ 1 の場合のみ実行する。**Pre-flight (v5.1.0)**: 起動前に `references/ritual-protocol.md` を必読。未読のままステップ進行は原則違反（§0 受け入れ基準 4）。
ステップ3.5は DB/API/状態遷移/認可のいずれかが関与する場合に起動する。判定と実行のプロトコル詳細は `references/subphase-selection.md` を参照。
ステップ3.6は UI を伴うプロジェクトでのみ起動する。判定と対話プロトコルの詳細は `references/design-system-spec.md` を参照。
ステップ2.6は critical journey または UI を持つプロジェクトでのみ起動する。詳細は `references/test-oracle-dialog.md` を参照。

## ステップ詳細

### 0. 対話 persona ロード（v5.17.0 追加）

**Pre-flight**: 対話開始の最初のアクションとして `references/persona-spec.md` を読み、persona の二層モデル（Logic / Presentation）と出力パイプライン（XML AI-data → Character Output）を内部化する。

#### ロード順（override 規約）

REGIME.md の `persona.active` で指定された persona を以下の優先順位で探索する。最初に見つかったファイルを採用する：

1. `<project-root>/.dh/personas/<active>.persona.md`（利用者プロジェクト override）
2. `<dialog-harness>/templates/personas/<active>.persona.md`（DH 同梱）

両方とも存在しない場合は default にフォールバックし、その旨を 1 行告げる。

#### 起動シナリオ別

- 既存プロジェクト（REGIME.md 存在）: `## persona` セクションを確認。`active:` 未指定なら `default` 扱い
- 新規プロジェクト（REGIME.md 未存在）: `default.persona.md` で開始。対話中に人間が「ペルソナを ◯◯ に切り替えて」と指示した場合は即時切替し、§4 のモード判定時に REGIME.md へ `persona.active` と `override_state` を反映する

#### `override_state` の適用

- `null`（既定）: persona の `default_state` で State Machine を初期化、以降は条件に従って自動遷移
- 非 null: その状態に **強制固定**。自動遷移は無効化（STEP 1 の `<system_state>` も固定値）
- 対話中に「自動切替に戻して」と発話されたら null に戻し、永続化したければ REGIME.md を更新

切替成功時は新 persona の口調で 1 行告げる（例: 羊 persona なら「これからは羊さんモードで進めますねぇ」）。
本ステップは presentation layer の初期化のみ。仕様策定の中身（logic layer）は persona に依存しない。

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

#### 対話例（EC サイト、3 往復で機能×条件に到達）

| ラウンド | AI の問い（選択肢提示） | 人間 | 到達粒度 |
|---|---|---|---|
| R1 | 「ECサイトですね。扱う商品は (a) 物理単品 / (b) サブスク / (c) デジタル配信 のどれが近いですか？複合もOK」 | 「a と b の混在」 | 機能一覧（商品管理・カート・決済・サブスク管理） |
| R2 | 「カートの上限は？目安: ① 個別に30品 / ② 無制限だが合計金額上限 / ③ 業界標準（類似サービスの例: Amazon は 50 品）」 | 「①の30品で」 | 機能×条件（カート=30品上限） |
| R3 | 「在庫超過時の挙動は (i) エラーで操作停止 / (ii) 購入可能数にサイレント丸め / (iii) 予約扱いで通知 のどれが近いですか？」 | 「i でいい」 | **機能×条件（最低ライン到達）** → 自律開発可能 |

R3 完了時点で `SPEC.md` に `F1. カート: 最大30品、在庫超過時はエラー表示` と記述できる状態になる。Priority は別軸で確認（critical/standard/cosmetic、詳細は `references/philosophy.md` §第3条）。

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

UX 3問は独立軸ではなく、NFR 軸の補足として扱う（詳細は `references/regime-assessment.md` §軸4）。3問の回答は SPEC.md の UX制約セクション（`assets/meta-spec-template.md`）に格納される。

### 2.6. C5 テスト oracle 言語化（v5.23.0 追加）

**Pre-flight (v5.23.0)**: 起動前に `references/test-oracle-dialog.md` を必読。

E2E は AI 駆動開発において「AI の知覚器官」であり、**AI は「見ると宣言したものしか見えない」**。
ゆえに人間の暗黙の関心（test oracle）を言語化することは、AI の知覚野を広げることに等しい。
本ステップは UX 3問の直後に 3 問だけ投げ、相 B（SPEC 由来の耐久 E2E）のカバレッジ対象を
**AI 裁量でなく人間と大枠合意**する。これが「AI テストスクリプトの精度」への L0 時点の中核対策（C5）。

#### 起動条件

critical-priority journey を持つ **or** UI を持つプロジェクト。非対面かつ cosmetic のみは完全スキップ。

#### 3問

| # | 質問 | 格納先 |
|---|---|---|
| TQ1 関心 | これが壊れてたら絶対に世に出したくない瞬間/画面は？ | SPEC critical journey（相 B 母集団・C1） |
| TQ2 目的 | 誰のどんな"成功"のためにある？なぜ作る？ | SPEC WHY 層 → Vision/Interaction Cost 合格基準 |
| TQ3 暗黙前提 | 言わなくても当然そうあるべき前提は？ | DONT.md + L0-6 invariants の Sad/Evil path 種 |

未回答/曖昧応答は INTENT/SPEC から AI が推定し `確度: AI推定` を付与（UX 3問・儀式 E1 と同型）。
詳細・自動補完・格納マッピングは `references/test-oracle-dialog.md`。E2E 構築側の正本は
`../layer1-autonomous-dev/references/e2e-best-practices.md`。

#### プロトコルの位置づけ

C5 は presentation でなく logic 層の対話であり persona 非依存。L0-6 サブフェーズ起動時は TQ3 を
Evil/Sad path の種として `references/subphase-l06-invariants.md` へ直接引き渡す。

### 3. ドキュメント化

メタ仕様テンプレートに従い、以下のドキュメント群を生成する。
テンプレートの詳細は `assets/meta-spec-template.md` を参照。

生成するドキュメント：
- **INDEX.md** — 全体目次（100行以内）。他ドキュメントへの参照を集約
- **SPEC.md** — 機能仕様（WHY / WHAT / 条件 / 優先順位 / 制約）。該当プロジェクトはデータモデル進化セクションを含む（詳細: `references/schema-evolution.md`）
- **DONT.md** — スコープ外の明示（現時点でAI自律開発が困難な領域）
- **DOMAIN-CONTEXT.md**（任意） — 業界・業務固有の前提条件。該当プロジェクトのみ。機密は `DOMAIN-CONTEXT.secret.md` に分離
- **DESIGN.md**（任意） — 視覚仕様（デザイントークン + 運用ルール）。UI を伴うプロジェクトのみ。生成判定は §3.6 で実施

### 3.5. サブフェーズ選定と実行

**Pre-flight (v5.1.0)**: 起動前に `references/subphase-selection.md` を必読。未読のままステップ進行は原則違反（§0 受け入れ基準 4）。

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

### 3.6. DESIGN.md 生成判定（v5.15.0 追加）

**Pre-flight (v5.15.0)**: 起動前に `references/design-system-spec.md` を必読。未読のままステップ進行は原則違反（§0 受け入れ基準 4）。

UI を伴うプロジェクトに対して `DESIGN.md`（視覚仕様 + デザイントークン）を生成する。
AGENTS.md（CLAUDE.md, 振る舞い）/ SKILL.md（個別タスク）/ DESIGN.md（外観）の **3 層分離** により、視覚仕様を CLAUDE.md に詰め込むアンチパターンを避ける。

#### 起動判定

1 問だけ投げる。AI 推定で「明らかに UI あり」なら投げずに仮判定（通知のみ）。

| # | 質問 | 起動判定 |
|---|---|---|
| DG1 | 「このプロジェクトは画面（UI）を持ちますか？ Web / モバイル / デスクトップのいずれでも」 | UI あり=**起動** / 非対面（CLI / API / ライブラリ）=**スキップ** |

#### 対話プロトコル（DG2〜DG4、起動時のみ）

UX 3問プロトコル（§2.5）と同じ思想で 3 問に絞る。未回答時は AI が実践デフォルトで自動補完する。

| # | 質問 | 格納先 | 未回答時のデフォルト |
|---|---|---|---|
| DG2 | ブランド・トーンを 1 行で言うと？ | DESIGN.md `## Overview` | 「クリーン、プロフェッショナル、高密度」 |
| DG3 | 「あの UI が好き」という参考はある？ | DESIGN.md `## Overview` 末尾 | UX 3問 Q3 の参考類似サービスを流用 |
| DG4 | プライマリカラー（CTA 色）は？ HEX / 色名 / 「お任せ」のいずれかで | YAML `colors.primary` | `#1A73E8`（Material Blue、WCAG AA 適合） |

詳細な対話例・自動補完根拠・YAML スキーマ・Do's and Don'ts の重要性は `references/design-system-spec.md` を参照。

#### 生成物

- **DESIGN.md** — プロジェクトルート直下に配置。`assets/design-md-template.md` のテンプレートにプレースホルダー置換した実体
- **INDEX.md** に視覚仕様への 1 行参照を追加
- **CLAUDE.md** の `## 参照` に `視覚仕様: DESIGN.md` を 1 行追加

#### 検証経路（重要）

DESIGN.md の真の検証は **コードファーストの静的検査では完結しない**。philosophy 三拍子「仕様に合う・動く・使える」のうち「使える」は E2E + Vision 経路でのみ判定可能。L1 (autonomous-dev) と L1-independent-reviewer は philosophy 5 層検出スタックの第 2 層 (Playwright スクショ) と第 5 層 (Vision モデル判定) を必ず通す。§7.4 自己検証のトークン一貫性検査は第 1 層（必要条件）であり、これ単独で UX を保証しない。詳細は `references/design-system-spec.md` §E2E 視覚検証 参照。

#### 非起動条件

以下では DG1 を投げずに DESIGN.md スキップを確定する:

- SPEC.md に「CLI」「ライブラリ」「バッチ」「webhook ハンドラ」のみ記載
- バックエンドサービス単体運用で対面 UI を持たない（event-sourcing バックエンド単体 / API サーバ単体 等。イベント履歴ダッシュボード等の UI を持つ場合は起動する）
- DOMAIN-CONTEXT.md に「ヘッドレス」「内部 API のみ」明示

#### 既存プロジェクトとの後方互換

`DESIGN.md` 不在のプロジェクトはこれまで通り動作する（生成義務なし）。
LC ≥ 1 プロジェクトへの後付け追加は事後追加プロトコル（`references/design-system-spec.md` §運用規律）参照。

### 4. モード判定

**Pre-flight (v5.1.0)**: 起動前に `references/regime-assessment.md` を必読（dev_mode 判定セクション含む）。未読のままステップ進行は原則違反（§0 受け入れ基準 4）。

規模・不確実性・リスク・NFR の 4 軸でスコアリングし、L2発動閾値もチェックして開発モードと ARC・権限レベルを決定する。
判定プロトコルの詳細は `references/regime-assessment.md` を参照。
NFR スコアリング（5カテゴリ × 0-3 点、オーバーライド4条件）は `references/nfr-scoring.md` を参照。
ARC パターン選択（monolith / realtime-pubsub / event-sourcing）は `references/arc-patterns/` 配下 3 ファイルを参照。
権限レベル（L0-2 / L0-3）と介入チャネル（C1/C2/C3）は `references/permission-delegation.md` を参照。

判定アウトプット：
- **REGIME.md** — モード判定結果（スコア・モード・dev_mode・根拠・AI能力バージョン・L2の場合はサブドメイン構成）

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

#### dev_mode 軸（v5.0.0 追加 / v5.6.0 で `autonomous` 本格化）

GitHub 連携前提の自律駆動を 3 段階で表現する追加軸。規模・チーム軸と並列で動的判定する。
詳細プロトコルは `references/regime-assessment.md` の「dev_mode 判定」セクション参照。

| dev_mode | GitHub | Actions | Issue 自動化 | 並列実装 | 自動 merge | 人間関与 |
|---|---|---|---|---|---|---|
| local_only | × | × | × | × | × | 全 Layer |
| github_assisted | ○ | 任意 | × | 手動 | × | L0 + 承認 |
| autonomous | ○ | ○ | ○ | 自動 | ○（scope 依存）| P1〜P4 のみ |

旧名 `github_autonomous` は v5.6.0 で `autonomous` にリネーム（autonomous_scope 軸との整合）。後方互換: 既存 REGIME.md で `github_autonomous` 記述は `autonomous` + `autonomous_scope: full` と等価扱い（自動マイグレーションは行わない、新規プロジェクトから新名を使用）。

判定フロー：
1. 質問1：「GitHub 使う？」
2. No → `local_only` 確定
3. Yes → 規模 + LC から推論（v5.6.0 時点）
   - M1 → `github_assisted`
   - M2, LC ≤ 1 → `github_assisted`
   - M2-L2, LC ≥ 1 → `autonomous`（質問 2 で `autonomous_scope` 確認）
4. 推論結果を 1 回のみ確認、ユーザー裁量で昇格・降格可

dev_mode 昇格・降格は手動 + ADR 記録必須（spec §3.2.3）。「GitHub 無しでも DH ベースは完全動作」が原則。

#### autonomous_scope 軸（v5.6.0 追加）

dev_mode が `autonomous` の場合のみ意味を持つ。autonomous-drive 機構（PR 作成 / 多層検証 / 自動 merge / 次 Issue 着手）の運用粒度を 3 値で表現する。

| autonomous_scope | 自動 merge | PR review/approve | P3 (事後確認) のタイミング |
|---|---|---|---|
| **full**（デフォルト） | 有効（`auto-merge` label opt-in + 多層検証通過時） | AI（または gemini-review/Copilot 等の独立 critic）| merge 後に P3 |
| merge_gated | **無効**（人間 approve 必須）| 人間が実施 | merge 前に P3 |
| custom | 部分有効（`dev-env-spec.md` Level C 詳細表で指定） | 個別設定 | 個別設定 |

**判定フロー**（dev_mode = `autonomous` 確定後の質問 2）：

```
Q: 自律駆動の度合いを選択してください
   (1) フルオート [デフォルト推奨] = autonomous_scope: full
       人間 = P1〜P4 のみ。AI = Issue 精査〜自動 merge〜次 Issue 着手まで完全自走
   (2) 中度 = autonomous_scope: merge_gated
       自動 merge は無効、PR review/approve は人間が実施（P3 を merge 前に倒す）
   (3) カスタム = autonomous_scope: custom
       個別に設定（dev-env-spec.md Level C 詳細表で指定）
```

**Person 責務（P1〜P4）**: philosophy.md 第 7 条参照。autonomous_scope = `full` 時、人間関与は以下 4 点に集約：
- P1 発案 / P2 ブレスト（Issue 化は AI）/ P3 事後確認・評価 / P4 暴走時介入

`autonomous_scope` の昇格・降格は手動 + ADR 記録必須。デフォルト = `full` で、ユーザー要請時のみ `merge_gated` / `custom` を選択。

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

**Pre-flight (v5.1.0)**: 起動前に `references/dev-env-spec.md`（配置規則・モード別差分）と `references/scaffold-checklist.md`（stack 別の生成必須ファイル一覧と smoke test 手順）の 2 件を必読。未読のままステップ進行は原則違反（§0 受け入れ基準 2・4）。

認識ズレ解消済みのドキュメントとモード判定結果を入力として、以下を生成する。
各フォーマットの詳細は `references/dev-env-spec.md` を参照。

モードに応じて生成物が変わる：

| モード | 追加生成物 |
|---|---|
| M1 | 最小構成（CLAUDE.md 簡略版 + REGIME.md + sensors/computational.md） |
| M2 | 標準構成（CLAUDE.md + REGIME.md + .claude/skills/ + sensors/computational + inferential + review-checklist） |
| L2 | M2 + DOMAINS.md + 各ドメイン別部分SPEC + sensors/integration/ |

**Level C: AI 自律運用（v5.6.0 追加、dev_mode = `autonomous` 選択時のみ）**

dev_mode が `autonomous` の場合、上記モード別生成物に加えて以下を導入する：

| autonomous_scope | 追加生成物 |
|---|---|
| **full**（デフォルト） | `templates/github-workflows/` から auto-merge.yml + gemini-review.yml を placeholder 置換して `.github/workflows/` 配下にコピー、label (`ready-for-ai` / `auto-merge` / `do-not-merge`) 自動作成、secrets (`GH_REVIEW_PAT` / `GEMINI_API_KEY`) 設定ガイド |
| merge_gated | 上記から auto-merge.yml を除外（gemini-review.yml + label のみ）|
| custom | `dev-env-spec.md` Level C 詳細表で個別指定 |

deployment ロジックは `crosscut-autonomous-drive` skill が担う（spec-architect が dev_mode `autonomous` 判定後に明示起動）。詳細は `references/autonomous-drive-deployment.md` 参照。

**重要**: 検証agent（layer1-independent-reviewer / layer2-integration-verifier）や layer2-orchestrator の本体は **Level A（共通スキル）** に存在し、プロジェクト側で再生成しない。autonomous-drive deployment skill (`crosscut-autonomous-drive`) も Level A として配置される。プロジェクト差異は sensors やチェックリストに閉じる。

生成する開発環境構成（M2 標準）：
- **CLAUDE.md / .claude/settings.json** — エージェントのRL（ルール）定義
- **.claude/skills/** — プロジェクト固有のSK（検証agent本体は含まない）
- **sensors/** — センサー定義（計算的＋推論的）
- **テスト基盤** — ビルド・テスト・リンターの設定（1分以内制約）

**推奨開発オプション（v5.18.0 追加）**: S1 で DB 使用ありと判定され、本番に hosted Postgres / BaaS（特に Supabase）を使い消失 NG の私的データを持つ構成では、本番を汚さないローカル優先開発（Docker 上のローカルスタック + migration 経由の本番反映）を推奨提示する。推奨発動条件・前提確認・ワークフロー・セキュリティ規律は `references/supabase-local-dev.md` を参照。強制ではなく推奨（philosophy 第 6 条）。

### 7. 出力

**Pre-flight (v5.1.0)**: 起動前に `assets/credit-template.md`（README.md クレジット規格）を必読。未読のままステップ進行は原則違反（§0 受け入れ基準 4）。

以下を Layer 1（autonomous-dev スキル）または L2 オーケストレータに渡せる状態として出力する。

```
project-root/
├── INDEX.md            # 全体目次
├── SPEC.md             # 機能仕様
├── DONT.md             # スコープ外定義
├── REGIME.md           # モード判定結果（AI能力バージョン含む）
├── DESIGN.md           # 視覚仕様（任意・UI プロジェクトのみ。§3.6 で生成判定）
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

### 7.4. L0 自己検証（v5.1.0 追加）

§7（出力）に進む前に、§0「L0 完了の受け入れ基準」4 条件を逐項確認する。1 件でも FAIL があれば §7 へは進まず原因を解消する。検査項目は ls / grep / cat 等の手作業で十分（shell script 雛形は配置しない）。

- [ ] **broken reference 検査**: 生成した `INDEX.md` / `SPEC.md` / `DONT.md` / `REGIME.md` / `DOMAIN-CONTEXT.md` / `DESIGN.md` 等が引用するファイル・パスが実体として存在する（dead link なし）
- [ ] **scaffold smoke test 検査**: `references/scaffold-checklist.md` の対応 stack の必須ファイルが全て揃い、smoke test コマンド（`pnpm install` / `dev` / `build` / `test`）が exit 0。通らない場合は理由を `delivery/SELF-VERIFICATION-*.md` または DELIVERY.md に明記
- [ ] **DONT 自己照合**: `SPEC.md` 内に `DONT.md` のいずれかの禁止条項に違反する記述・機能定義が混入していない（目視 + grep）
- [ ] **DESIGN.md トークン一貫性検査**（DESIGN.md 生成時のみ）: YAML フロントマターで定義したトークンキーが Markdown 本体の `{colors.primary}` 等の参照と整合する（未定義参照なし・未使用定義なし）。詳細は `references/design-system-spec.md` §7.4 自己検証への組込
- [ ] **Pre-flight 充足**: 本セッションで通過した §1.5 / §3.5 / §3.6 / §4 / §6 / §7 の各 Pre-flight 行が指定するリファレンスを実際に読んだ
- [ ] **受け入れ基準充足**: §0 受け入れ基準の 4 条件（仕様充足 / scaffold 実体 / smoke test / 本 §7.4 PASS）を逐項チェック

検証結果は `delivery/SELF-VERIFICATION-*.md`（任意ファイル名、L0 自己検証用）または DELIVERY.md の冒頭に記録する。LC ≥ 1 の既存プロジェクトでは、本ステップは v5.1.0 以降に追加開始する機能・フェーズに段階適用する（既存成果物の遡及検証は要求しない）。

### 7.5. ファイル配置規則に沿った初期化

`references/dev-env-spec.md`「ファイル配置規則」に従い、プロジェクト初期化時に以下を実施する。

- `delivery/` を空で作成（L1 献上先として確保）
- `assets/` を空で作成（共有入力の置き場）
- `docs/` は**初期生成しない**（L1 が共有出力として必要時に生成）
- ルート直下は INDEX/SPEC/DONT/REGIME/CLAUDE/DOMAINS と README.md のみ許可。DESIGN.md は UI プロジェクトのみ追加で許可（§3.6 で生成判定された場合のみ。v5.15.0 追加）
- 違反（PLAN.md, TODO.md, MEMO.md 等のルート直下作業メモ）は **Phase B の自動修復対象** として DELIVERY.md にログ化

本ステップは新規（LC=0）のみ実施。既存プロジェクト（LC=1/LC=2）では現状配置を尊重し、違反検出時のみ L1 側で修復を提起する。

### 7.6. README.md クレジット挿入

`assets/credit-template.md` に従い、README.md 末尾に制作クレジットを挿入する。

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

## 廃止判断プロトコル（LC ≥ 1 で適用）

既存機能の廃止は人間の一存では決めない。合議＋AI根拠提示で判断する。
発動条件・プロトコル・拒否ケースの詳細は `references/deprecation-protocol.md` を参照する。

## 参照ドキュメント

### 既存（参照リンク保持・内容拡張許容）

本セクションの参照リンクは v3.0 時点の 7 件を**リンク単位で**保持する。
個別ファイルの内容拡張（節の追加・記述の詳細化）は許容するが、リンクの削除・改名・リダイレクトは minor 昇格でも禁止する。
骨格の完全な書き換えは major 昇格案件として扱う。

**例外（再分類）**: ファイルの identity（ベース名）と内容が完全に保持される格納ディレクトリの変更（例: skill-creator 規約への適合化に伴う `references/` ↔ `assets/` の再分類）は「改名」ではなく「再分類」として扱い、minor 昇格で許容する。該当変更は「v4.2 追加（分類再編・progressive disclosure 適合化）」以降の履歴節に記録する。

- `assets/meta-spec-template.md` — 仕様ドキュメントのテンプレートと記述ルール（REGIME.md テンプレ含む）※v4.2 で `references/` → `assets/` に再分類（skill-creator の progressive disclosure 規約準拠、内容は不変）
- `references/dev-env-spec.md` — 開発環境ドキュメント規格（RL/SK/センサーのフォーマット、モード別差分）
- `references/regime-assessment.md` — モード判定プロトコル（S/U/Rスコアリング、L2発動閾値、LC 判定）
- `references/dialog-questions.md` — 非エンジニア向け対話質問例集（振り返り儀式テンプレ含む）
- `references/persona-spec.md` — 対話 persona 仕様（v5.17.0 追加。Logic/Presentation 二層分離、State Machine、出力パイプライン、philosophy 整合）
- `references/model-recommendations.md` — 実行前の推奨モデル提示（モード別・ハイブリッド運用・AI能力バージョン別差分対策）
- `references/history-layer-spec.md` — 履歴層（history/）のスキーマ・訂正・archive・承認レベル
- `references/ritual-protocol.md` — 振り返り儀式プロトコル（4レベル判定・F1〜F3・E1/E2対応）

### 拡張（業務システム運用・社内版LINE型射程対応）

- `references/nfr-scoring.md` — NFR スコアリング規格（5 カテゴリ × 0-3 点、オーバーライド 4 条件、N=0 後方互換）
- `references/arc-patterns/monolith.md` — ARC デフォルト（単一デプロイ単位、AI 自走完遂の標準形）
- `references/arc-patterns/realtime-pubsub.md` — リアルタイム pub/sub パターン（社内版LINE型、大量同時接続）
- `references/arc-patterns/event-sourcing.md` — イベントソーシング（監査必須、時系列復元、スキーマ進化完全準拠）
- `references/schema-evolution.md` — データモデル進化プロトコル（互換性ポリシー / デプロイ戦略 / upcasting）
- `references/supabase-local-dev.md` — Supabase ローカル開発環境（v5.18.0 追加、推奨開発オプション。本番保護のローカル優先フロー / migration 経由の本番反映 / セキュリティ規律。S1 = DB 使用あり + hosted Postgres/Supabase 構成でのみロード）
- `references/permission-delegation.md` — 段階的権限委譲（L0-2/L0-3、介入チャネル C1/C2/C3、判断献上 5 カテゴリ）
- `references/domain-context-dialog.md` — ドメイン文脈対話プロトコル（DOMAIN-CONTEXT.md、機密分離、5 対話カテゴリ）
- `references/design-system-spec.md` — DESIGN.md 規格と対話プロトコル（v5.15.0 追加、UI プロジェクトのみ起動。Google Labs 公式仕様準拠、Do's and Don'ts によるアンカリング正方向活用、3 問プロトコル DG2〜DG4）
- `assets/design-md-template.md` — DESIGN.md 実践テンプレート（v5.15.0 追加、YAML トークン + Markdown 本体 + Components 拡張ガイド）
- `references/test-oracle-dialog.md` — C5 テスト oracle 言語化プロトコル（v5.23.0 追加、§2.6 から起動。critical journey or UI プロジェクトのみ。TQ1-3 で人間の暗黙の関心を言語化し相 B E2E 母集団を SPEC へ確定）
- `../../../templates/rules/common/ui-baseline.rules.md` — UI Baseline RL（v5.23.0 追加、UI プロジェクトの相互作用層・常時適用。B-01〜B-25 + レビューチェックリスト。適用経路は `references/design-system-spec.md`「UI 相互作用層」）
- `../../../templates/rules/common/ui-specialization.context.md` — UI Specialization Context（v5.23.0 追加、目的特化 S-01〜S-06 + 衝突解決。S-xx 選択は §3.6 / UX 3問 / NFR と連動、`.dh/rules/` で override 可）

### v3.1 追加（配置規則・クレジット）

- `assets/credit-template.md` — README.md 制作クレジットの規格とテンプレート（マーカー管理・拒否権・更新ルール）※v4.2 で `references/` → `assets/` に再分類

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

### v5.23.0 追加（E2E 構築 BP の体系化・C5 テスト oracle 言語化・UI Baseline RL 取り込み、minor 昇格）

2 テーマをバンドル: **(1)** E2E 構築 BP + C5、**(2)** UI Baseline RL（相互作用層）。両者は「B-ID = oracle」で接続する。

**(1) E2E 構築 BP の体系化・C5 テスト oracle 言語化**

後方互換維持の追加のみ。AI 駆動開発における E2E テストの「構築」叡智を DH に結晶化する。
DH には既に E2E の「位置づけ」（5層スタック第2層・L2 Test Agents・`sensors/e2e/` scaffold 枠）が
あったが、「堅牢な E2E をどう構築するか」の BP が欠落していた。本リリースでその空白を埋める。

確定した一次概念と対策（人間との対話で合意）：

- **二相分離（一次概念）**: 相 A（in-loop 知覚器・使い捨て可）/ 相 B（SPEC 由来の耐久資産）を明示分離
- **E2E = AI の知覚器官**: AI は「見ると宣言したものしか見えない」→ artifact 密度が人間以上に重要
- **C5 テスト oracle 言語化（本丸）**: §2.6 新設。人間の暗黙の関心を TQ1-3 で言語化し相 B 母集団を SPEC へ確定
- **AI テスト精度対策**: C1（SPEC 由来母集団）/ C2（生成と判定の隔離＝自己言及の罠回避）/ C3（本数天井）/ C5
- **実行環境の統一**: browser provenance pinning（借りない・固定する・記録する）、chromium 単一既定・他 opt-in
- **device emulation**: 実デバイスは射程外、device descriptors で本番見え方を寄せ Vision 判定に乗せる
- **接続地図（強制は将来 PR）**: flaky→circuit-breaker/P4・Quarantine→feedback-loop・provenance→観測性統一
- **温存**: テスト情報代謝・mutation メタテスト（C4）は試験的導入のため minority opinion として温存

変更点：

- §処理フロー に 2.6 を新設（UX 3問の直後、critical journey or UI プロジェクトのみ起動）
- §2.6「C5 テスト oracle 言語化」を新設（TQ1-3・自動補完・格納マッピング・persona 非依存）
- `references/test-oracle-dialog.md` 新設（C5 対話プロトコル原典・知覚野拡張原理）
- `../layer1-autonomous-dev/references/e2e-best-practices.md` 新設（構築 BP 正本・二相分離・8 規律 + 接続地図）
- `../layer1-autonomous-dev/references/inferential-sensor-v2.md` §第2層に正本参照 + 二相分離の 1 行言及
- `../layer2-orchestrator/references/e2e-integration.md` の config.ts 規格に pinned chromium / projects マトリクス / 公式コンテナ runner / provenance 記録 + 正本参照
- `../layer1-independent-reviewer/SKILL.md` のレビュー観点に「テスト妥当性（自己言及の罠隔離・C2）」追加
- 参照ドキュメント 拡張 list に `references/test-oracle-dialog.md` を追加

**(2) UI Baseline RL の取り込み（利用者提供 UIUX 研究 → DH 統合）**

DESIGN.md は「どう見えるか（視覚トークン層）」を担うが「どう知覚され・操作されるか（相互作用層）」が
空白だった（token 静的検査の限界・DONT「創造的 UX を AI に任せない」）。枯れた UX 法則（Norman/Fitts/
Hick/Miller/Jakob/Doherty/Gestalt/WCAG）に立脚した機械可読 RL でこの空白を埋める。

- 新設 `../../../templates/rules/common/ui-baseline.rules.md`（B-01〜B-25・常時適用・MUST 違反はマージ不可）
- 新設 `../../../templates/rules/common/ui-specialization.context.md`（目的特化 S-01〜S-06 + 衝突解決）
- `references/design-system-spec.md` に「UI 相互作用層」節を新設（二層モデル / デプロイ・override /
  S-xx 選択の L0 接続 / **B-ID を 5 層検出スタック・C5 の ready-made oracle 化**）
- `references/dev-env-spec.md` の templates/rules 節に UI Baseline RL を共通 RL として明記
- `../layer1-independent-reviewer/SKILL.md` 5.5.1 に B-ID レビューチェックリスト照合を追加
- `templates/rules/README.md` の common/ 現況を更新

設計の核: B-ID は抽象的な「使える」を検証可能な宣言に落としたもの＝ E2E/Vision の oracle であり、(1) の
C5（AI は見ると宣言したものしか見えない）と直結する。S-xx 選択は新質問を増やさず DG2/3・UX 3問・NFR から
導出する。利用者プロジェクトは `.dh/rules/` で S-xx を override 可能（DH 更新で消えない）。

LC ≥ 1 既存プロジェクトは新規開始する E2E から段階適用（既存テストの遡及修正は不要）。
非該当（CLI/ライブラリ/cosmetic のみ）では §2.6 を起動せず e2e-best-practices.md もロードしない（時間コストゼロ）。
flaky 強制接続は本 PR では地図のみ。実 E2E 運用データが貯まった次 PR で teeth を入れる。

### v5.18.0 追加（Supabase ローカル開発の推奨オプション化、minor 昇格）

後方互換維持の追加のみ。新規 skill / agent は作らず、専用 reference 1 件の新設 + SKILL.md 本体および既存 reference 4 件への軽い配線（pointer）で構成する（#107 データモデリング吸収と同型の「既存構造への栄養追加」方針、ただし本件はツール固有プレイブックのため専用 reference 形式を採る）。本番 Supabase（hosted Postgres）に消失 NG の私的データを持つ構成で、本番を汚さない**ローカル優先開発**（Docker 上のローカルスタック + migration 経由の本番反映）を推奨オプションとして提示できるようにする。

- `references/supabase-local-dev.md` 新設。推奨発動条件（S1 = DB 使用あり + hosted Postgres/Supabase + 消失 NG データ）/ 前提確認（OS / Docker / WSL2）/ 7 ステップワークフロー（CLI install〜`.env.local`）/ 生成物配置（`dev-env-spec.md` 整合）/ smoke test（`scaffold-checklist.md` 整合）/ 本番反映の安全規律（`schema-evolution.md` 整合）/ セキュリティ規律 / モード別の扱い / プロトコル自己評価 を規定。ツール固有プレイブックのため必要時のみロード（progressive disclosure）
- §6「開発環境の設計・構築」M2 標準生成構成に「推奨開発オプション」1 ブロックを追加（hosted Postgres/Supabase 構成時に `supabase-local-dev.md` を参照、強制ではなく推奨）
- §参照ドキュメント 拡張 list に `references/supabase-local-dev.md` を追加
- `references/dialog-questions.md` S1 に「フォローアップ: 本番保護とローカル開発の推奨」を追加（非技術語彙の推奨提示、過剰提示回避の解釈付き）
- `references/scaffold-checklist.md` に「Supabase ローカル開発（推奨バックエンド開発オプション）」セクションを追加（追加生成物 `supabase/` + `.env.local` / smoke test 追加。標準 stack 12 種は置換せず追加層）
- `references/schema-evolution.md` に「Supabase CLI マイグレーション運用との整合」セクションを追加（コマンド ↔ デプロイ戦略の対応、expand-contract への分解、append-only 規律、`db push` 前の人間承認）
- `references/subphase-l02-domain.md` の 3 階層モデル節に物理層 = hosted Postgres/Supabase 時のローカル優先推奨を 1 行追加

LC ≥ 1 既存プロジェクトは新規開始する DB 機能から段階適用（既存の本番直結フローの遡及置換は不要、事後追加プロトコルで任意導入可）。非該当プロジェクト（SQLite / メモリのみ / 使い捨て）では `supabase-local-dev.md` をロードせず提示もしない（時間コストゼロ）。

### v5.17.0 追加（対話 persona 層・presentation 差替インフラ、minor 昇格）

後方互換維持の追加のみ。DH の応答出力（presentation layer）を persona ごとに差し替え可能にする。
仕様策定の判断（logic layer）は persona に依存しない（philosophy 第 6 条「人間最終承認」を維持）。

- `references/persona-spec.md` 新設。二層モデル（Logic / Presentation）/ State Machine 規約（Normal / Overflow / Attention）/ 出力パイプライン（XML AI-data → Character Output）/ 切替方法 / 適用範囲 / philosophy 整合を規定
- `../../../templates/personas/` 新設。`README.md` / `default.persona.md`（中立・既定）/ `sheep-navigator.persona.md`（サンプル: 羊系ナビゲーター）を同梱
- §原則 に「対話 persona の二層分離」1 行を追加
- §ステップ 0「対話 persona ロード」を新設（処理フロー先頭に挿入）。REGIME.md `persona.active` を読むか default を使う
- `assets/meta-spec-template.md` の REGIME.md テンプレに `## persona`（任意）セクションを追加
- 適用対象は L0 三兄弟（spec-architect / archeo-architect / onboarding）のみ。L1/L2/crosscut は人間対話なしのため対象外（フラクタル原則の対話形状境界に揃える）

LC ≥ 1 既存プロジェクトは REGIME.md に `persona` 未指定なら default が active になり、既存挙動と完全同一（後方互換）。

### v5.16.0 追加（共有可能スキル整理・参照整合性確立・AI 駆動 PR 運用の実証、minor 昇格）

後方互換維持の追加のみ。Council 2 件 (`council-2026-05-12T13:32:00Z-sspr01` / `council-2026-05-12T14:30:00Z-adpp01`) 合意の scope_lock 6 項目を 1 PR で実装。

- `references/dev-env-spec.md` に **Level A 配布性評価 checklist**（6 軸 / 21 項目）を新設。新規 skill 追加 / 改修 / 格上げ・格下げ時の判定基準として運用
- `references/ecc-compat-criteria.md` 新設。ECC 互換配置の規約格上げ判定材料（6 軸）を整備。v5.16.0 時点では観測層継続、規約格上げは v5.17.0 以降に延期
- `references/deprecation-protocol.md` の dead-backtick-link 1 件修正（references/ 配下からは「2 階層遡る」相対パスが必要、SKILL.md 直下からは「1 階層遡る」で兄弟 skill に届く点を判別）

連動して以下が他 skill / harness 側で更新（詳細は各 skill / `dh-upgrades/upgrade-spec-v5.16.0.md`）:
- `harness-verifier/checks/references.py` に `BACKTICK_PATH_RE` を追加（バッククォート内相対パスの dead-link 検査）
- `layer0-onboarding` に reverse-design ステップ追加（既存 src/ から `DESIGN.md` 逆抽出、UI プロジェクトのみ）
- `layer0-archeo-architect` の意図マップに視覚 Island 追加（`island_type` / `design_md_impact` フィールド）
- `history/REGIME-LOG.md` に L0 三兄弟マトリクス記録、`history/ARCH-DECISIONS.md` に AD-021 / AD-022 追加

LC ≥ 1 既存プロジェクトは新規開始機能・フェーズに段階適用、既存成果物への遡及修正は不要。
PR 粒度方針として AD-021「AI 駆動開発における PR 粒度の決定基準」を採択、v5.16.0 を最初の実証 PR とする。

### v5.15.0 追加（DESIGN.md 生成機能、minor 昇格）

後方互換維持の追加のみ。UI を伴うプロジェクトの視覚的アイデンティティ（カラー / タイポ / spacing / コンポーネント / Do's and Don'ts）を AI コーディングエージェントに伝えるための DESIGN.md 生成機能を導入する。

- §処理フロー に 3.6 を新設（UI 有無を 1 問で判定、UI ありなら 3 問で視覚仕様取得）
- §3 ドキュメント化に DESIGN.md（任意・UI プロジェクトのみ）を生成物として追加
- §3.6 を新設し、起動判定（DG1）/ 対話プロトコル（DG2〜DG4）/ 生成物 / 非起動条件 / 既存プロジェクト後方互換を規定
- §7 出力ツリーに `DESIGN.md` を追加
- §7.4 自己検証チェックリストに「DESIGN.md トークン一貫性検査」を追加（DESIGN.md 生成時のみ）
- `references/design-system-spec.md` 新設。Google Labs 公式仕様（YAML フロントマター + Markdown 本体の 2 層構造、標準セクション順序）/ 対話プロトコル / Do's and Don'ts の重要性（アンカリング効果の正方向活用）/ 意図のコード化 / 盆栽運用規律 / LC ≥ 1 後付け追加プロトコル を規定
- `assets/design-md-template.md` 新設。実践テンプレート（YAML トークン + Markdown 本体 + Components 拡張ガイド）を提供
- `assets/meta-spec-template.md` の INDEX.md テンプレに DESIGN.md への参照行を追加（UI プロジェクトのみ条件付）
- `references/dev-env-spec.md` のルート直下許可ファイル一覧に DESIGN.md を追加
- `references/scaffold-checklist.md` に Vite + React + PWA stack での DESIGN.md 参照ガイドを追加（L1 連携情報）
- `layer1-autonomous-dev/SKILL.md` §1 ドキュメント受領に DESIGN.md（存在時）の条件付き読込を追加。§5 タスク実行に DESIGN.md トークン参照ルールを追加。§6 自己検証に「DESIGN.md トークン整合検査」を新設（HEX リテラル / px 直書きの grep 検査）
- `layer1-independent-reviewer/SKILL.md` の入力リストに DESIGN.md（存在時）を追加。処理フロー 5.5.1 として「DESIGN.md トークン整合検査」を新設（YAML 定義と Markdown `{...}` 参照の整合 / src/ への HEX 直書き混入検出 / Do's and Don'ts 違反パターン検出）
- `design-system-spec.md` §非起動条件と SKILL.md §3.6 非起動条件で event-sourcing 表現を精緻化（event-sourcing でも UI ありなら起動、UI なしのバックエンド単体運用に限定）
- **E2E 視覚検証経路の組込**: コードファーストでは UX を保証できないため、philosophy 5 層検出スタックの第 2 層 (Playwright スクショ) と第 5 層 (Vision モデル判定) に DESIGN.md を必ず乗せる。`design-system-spec.md` に §E2E 視覚検証 セクションを新設し、L1-autonomous-dev §6 自己検証と L1-independent-reviewer 5.5.1 にスクショ取得と Vision 判定を組込。§7.4 のトークン一貫性検査は必要条件であり十分条件ではないことを明記
- scaffold-checklist.md DESIGN.md 連携セクションに「E2E 視覚検証が最も重要」を明記

LC ≥ 1 既存プロジェクトは新規開始の UI 機能から段階適用、既存 UI 実装への遡及生成は不要（事後追加プロトコル経由で任意追加可）。
非 UI プロジェクト（CLI / API サーバ / ライブラリ）では DG1 を投げずにスキップ確定（時間コストゼロ）。

`crosscut-verifier-philosophy` の本実装は本リリース対象外（継続検討）。

### v5.2.0 追加（次元論導入・D4 検査機構の独立配置、minor 昇格）

dialog-harness 自身の自己検証機構として、リポジトリルート直下に `harness-verifier/` を独立配置する。
DH 本体（D4: メタスキル層）の内部整合性を 5 項目で検査する独立機構であり、本 SKILL.md からは**情報依存しない**（独立性要請）。
本セクションは次元論の概念と関連配置を記録するためのみのメモであり、L0 起動フローには影響しない。

- **5 次元論**: D1（ソースコード）/ D2（開発環境）/ D3（配布 skill インスタンス）/ **D4（マスタ skill = メタスキル）** / D5（Meta モニタリング層 = 人間）。機械可読命名は D-numbering、思想文書では `meta-layer` / `meta-meta-layer` 等の階層形容詞を併走させる二重命名を採用（Council 合意 2026-04-29）
- **`harness-verifier/`（リポジトリルート直下）**: D4 を検査する独立機構。`.claude/skills/` 配下ではなく、DH 本体と並列のディレクトリ。`PHILOSOPHY.md` / `BOUNDARY.md` / `HUMAN-PROTOCOL.md` / `glossary.yml` / `verify.py` / `checks/` / `reports/` を含む
- **検証スコープ 5 項目**: frontmatter 整合性 / 参照 path 有効性 / SK 間依存グラフ循環（自己参照と未定義参照のみ） / 5 層構造保全（D4 解釈） / 用語辞書整合
- **責務分離（BOUNDARY.md §5）**: 既存 `crosscut-verifier-drift`（D2/D3 対象）/ `crosscut-verifier-philosophy`（v5.3.0 候補、D2/D3 対象）/ §7.4 自己検証（D2 対象）と本機構（D4 対象）は次元が違う独立検証
- **後方互換**: 既存 SKILL.md / references / crosscut-* の挙動は完全不変。`harness-verifier/` 不在でも DH は通常動作する

`crosscut-verifier-philosophy` の本実装は v5.3.0 候補として引き続き継続検討（v5.1.0 から後送）。
詳細: `harness-verifier/README.md`, `harness-verifier/PHILOSOPHY.md`, `history/ARCH-DECISIONS.md` AD-010〜AD-012。

### v5.1.0 追加（L0 受け入れ基準明文化・Pre-flight 必読化・scaffold checklist・自己検証ステップ、minor 昇格）

後方互換維持の追加のみ。テストレビュー（PR #19、シナリオ「ケロぴの森」）で判明した L0 charter 未達 P0 4 項目（受け入れ基準・Pre-flight・scaffold・自己検証）を解消する。

- §0「原則」に **L0 完了の受け入れ基準 4 条件** を明文化（仕様充足 / scaffold 実体 / smoke test / §7.4 PASS）。ドキュメント生成完了 ≠ L0 完了。
- §1.5 / §3.5 / §4 / §6 / §7 各ステップ冒頭に **Pre-flight 必読リファレンス指定** を 1 行追加（読まずに進行禁止）
- `references/scaffold-checklist.md` 新設。v5.1.0 標準 stack（Vite + TypeScript + React + PWA）の必須生成ファイル 12 種と smoke test 手順を規定
- §7（出力）と §7.5 の間に **§7.4 L0 自己検証** を新設（broken reference / smoke test / DONT 自己照合 / Pre-flight 充足 / 受け入れ基準充足の 5 チェック）
- `references/dev-env-spec.md` の「開発環境構築時の初期化」に scaffold-checklist.md への相互参照 1 行を追加
- `assets/credit-template.md` のバージョン表記を v5.1.0 に更新

`crosscut-verifier-philosophy` の本実装は本リリース対象外（v5.2.0 候補として継続検討）。LC ≥ 1 既存プロジェクトは新規開始機能・フェーズに段階適用、既存成果物への遡及修正は不要。

### v5.0.0 追加（GitHub 連携前提化・crosscut prefix 確立・semver 化、major 昇格）

破壊的変更を含む major 昇格。詳細は `dh-upgrades/upgrade-spec-v5.0.0.md` および `history/REGIME-LOG.md` 参照。

- L0 判定軸に `dev_mode`（local_only / github_assisted / github_autonomous）を 3 軸目として追加（§4 モード判定 / §dev_mode 軸 / `references/regime-assessment.md` §dev_mode 判定）
- `assets/meta-spec-template.md` の REGIME.md テンプレに `## dev_mode` セクション追加
- `references/dev-env-spec.md` の参照権限マトリクスに `templates/` 行を追加（配布雛形）
- 関連: 既存 `council/` を `crosscut-council/` にリネーム（major 破壊）。`crosscut-` を Level A skill の第二の命名規則として確立
- 関連: 5 新規 crosscut skill（issue-dispatcher / issue-implementer / verifier-drift / verifier-philosophy(placeholder) / feedback-loop）追加。詳細は各 SKILL.md
- v5.8.0 追加: crosscut-issue-quality-gate（Issue 品質チェック、発動契機 (b)）
- バージョン記法を semver 厳格化（v5.0.0 以降は MAJOR.MINOR.PATCH）。v4.x 互換のため旧表記は受理

### v4.2 追加（分類再編・progressive disclosure 適合化）

skill-creator 規約（`references/` = 読み参考の docs、`assets/` = 埋めて使うテンプレ）への適合化として、以下 3 テンプレを `references/` → `assets/` に再分類。identity（ベース名）と内容は完全に保持。本節冒頭（§既存）の「改名禁止」制約には「再分類は例外」条項を明文化済み。

- `assets/meta-spec-template.md` — 保持対象 7 件のうちの 1 件、再分類として minor 許容（上記例外条項に基づく）。§357 参照
- `assets/credit-template.md` — v3.1 追加分、再分類。§377 参照
- `../layer0-onboarding/assets/reverse-spec-template.md` — 兄弟 skill 側で同期移動（Issue #12）

### v4.1 追加（廃止判断プロトコル分離）

- `references/deprecation-protocol.md` — 廃止判断プロトコル（LC ≥ 1 で適用、発動条件・プロトコル・拒否ケース）。SKILL.md 本体から分離して参照化。

### v4.0 追加（哲学原典化・5層エラー検出スタック・UX プロトコル）

- `references/philosophy.md` — dialog-harness 6条憲法（フラクタル / Shift Left / 情報純度 / 人間責務 / 献上哲学 / 人間 ≒ Council）。全skill の参照原典。第6条は v4.2 で追加。

関連（他 skill 配下に配置される参照ファイル、本 SKILL.md から間接参照）：
- `../layer1-autonomous-dev/references/inferential-sensor-v2.md` — Shift Left 基盤 + 5層エラー検出スタック（L1 自己検証の埋め込み手順含む）
- `../layer2-orchestrator/references/e2e-integration.md` — Playwright Test Agents 規格（L2 配下の並列 Agent 群）
- `../layer2-orchestrator/references/sub-agent-protocol.md` — サブエージェント統括の情報純度プロトコル
