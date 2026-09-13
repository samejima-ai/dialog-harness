---
name: layer0-spec-architect
target_os: any
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

REGIME.md `persona.active` を `<project>/.dh/personas/` → `<DH>/templates/personas/` の順で探索し、無ければ default。
`override_state` 非 null なら State Machine を固定。ロード順・起動シナリオ別・override 規約の詳細は
`references/l0-step-details.md` §0（v7.0.0 F10 で移送）、二層モデルの正本は `references/persona-spec.md`。

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

基本 5 問（S1 データ保存 / S2 外部 API / S3 画面遷移 / S4 権限 / S5 自動状態変化）で L0-2〜L0-6 を動的起動し、
「対話 α → 生成 β → 検証 γ → 判定 δ」の独立呼び出しで `spec/` 配下に成果物を生成する。起動判定表・実行プロトコル・
依存順（L0-1 → L0-2 → (L0-3 ‖ L0-4) → L0-5 → L0-6）・成果物配置・後方互換・事後追加の詳細は
`references/l0-step-details.md` §3.5（v7.0.0 F10 で移送・内容不変）。判定表の正本は `references/subphase-selection.md`。

### 3.6. DESIGN.md 生成判定（v5.15.0 追加）

**Pre-flight (v5.15.0)**: 起動前に `references/design-system-spec.md` を必読。未読のままステップ進行は原則違反（§0 受け入れ基準 4）。

UI を伴うプロジェクトに対して `DESIGN.md`（視覚仕様 + デザイントークン）を生成する。
AGENTS.md（CLAUDE.md, 振る舞い）/ SKILL.md（個別タスク）/ DESIGN.md（外観）の **3 層分離** により、視覚仕様を CLAUDE.md に詰め込むアンチパターンを避ける。

DG1（UI の有無）1 問で起動を判定し、起動時のみ DG2〜DG4（ブランド・トーン / 参考 UI / プライマリカラー）を投げて
`DESIGN.md` を生成する。**真の検証はコードファーストでは完結せず、5 層検出スタックの第 2 層（Playwright スクショ）と
第 5 層（Vision 判定）を必ず通す。** 起動判定・対話プロトコル・生成物・非起動条件・後方互換の詳細は
`references/l0-step-details.md` §3.6（v7.0.0 F10 で移送・内容不変）。規格の正本は `references/design-system-spec.md`。

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

#### dev_mode 軸 / autonomous_scope 軸

`dev_mode`（local_only / github_assisted / autonomous）は「GitHub 使う？」1 問 + 規模と LC からの推論で判定し、
`autonomous` 確定時のみ質問 2 で `autonomous_scope`（full / merge_gated / custom）を確認する。昇格・降格は手動 + ADR。
3 段階の対応表・判定フロー・autonomous_scope の意味・Person 責務との接続は `references/l0-step-details.md` §4
（v7.0.0 F10 で移送・内容不変）。判定プロトコルの正本は `references/regime-assessment.md` §dev_mode 判定。

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
- **CLAUDE.md / .claude/settings.json** — プロジェクト統括者（純化された常駐 + ルーティング表）+ 設定。規格は `references/dev-env-spec.md` §CLAUDE.md（v6.8.0 で RL 平置きから再定義）
- **.claude/skills/** — プロジェクト固有のSK（検証agent本体は含まない）
- **sensors/** — センサー定義（計算的＋推論的）
- **テスト基盤** — ビルド・テスト・リンターの設定（1分以内制約）

**推奨開発オプション（v5.18.0 追加 / v6.19.0 で供給元中立化）**: S1 で DB 使用ありと判定され、本番に **hosted Postgres / BaaS** を使い消失 NG の私的データを持つ構成では、本番を汚さないローカル優先開発（ローカルスタック + migration 経由の本番反映）を推奨提示する。**推奨しているのは開発フローであって供給元ではない。** 強制ではなく推奨（philosophy 第 6 条）。

供給元別のプレイブックは該当時のみロードする（progressive disclosure）。**適用範囲と根拠の数値は各プレイブックの §適用範囲 が一次情報源**であり、本表には複製しない（供給元が単独で書き換えられる値を規範側に固定しないため）:

| 供給元 | プレイブック | 適用範囲 |
|---|---|---|
| Supabase | `references/supabase-local-dev.md` | **既存プロジェクトを持つ案件のみ**（同ファイル §適用範囲 を参照） |
| Cloudflare Workers | `references/cloudflare-workers-dev.md` | Workers / D1 / KV / R2 を使う案件（同ファイル §適用範囲 を参照）。**数値表を持たず観測記録を参照する構成**（v6.19.0 F3） |

**新規案件の供給元選択に既定は置かない。** stack カタログ（`references/scaffold-checklist.md`）は stack 軸（言語 / FW / ランタイム）を扱うもので、**hosted DB / BaaS の供給元選択は含まない**。例外は 2 つ — **Stack 11（GAS）** と **Stack 12（Cloudflare Workers、v6.19.0 F4 追加）** で、いずれも実行基盤とデータ層が単一供給元に束縛される stack である。**この 2 つは「供給元を選ぶ軸」ではなく「束縛を受け入れた stack」として並ぶ**ため、Stack 12 の追加は Cloudflare を既定にしない。供給元選択は L0 対話で人間に委ねる。

**枠の観測（v6.19.0 F4 配線）**: Stack 12 を選んだ場合、**新規に DB を作る前に `crosscut-quota-observer` で現在の枠消費率を提示する**。日次枠はアカウント単位で共有されるため、1 案件の追加が無関係な既存プロジェクトを止めうる。**新規質問は増やさない** — 提示するのは観測結果であって規範ではない。観測 skill 不在・未認証なら degrade し、「観測できなかった」をそのまま伝える（「枠に余裕がある」と読み替えない）。

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
├── CLAUDE.md           # プロジェクト統括者（v6.8.0）
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
- [ ] **CLAUDE.md アンチパターン診断**（v6.1.0 追加）: 生成した `CLAUDE.md` が以下 5 つのアンチパターンに該当しない（claude-world 観測を DH 文脈で再構成、`references/observed-peers.md` §claude-world-examples 参照）。該当時は FAIL 扱いで §7 へ進む前に修正する
  - **曖昧**: 「適切に」「きれいに」「ベストプラクティスで」等の判定不能な抽象指示。具体的なコマンド・閾値・条件に書き換える
  - **コマンド欠落**: ビルド・テスト・lint の実行コマンドが書かれていない（AI が毎回推測する状態）。`scaffold-checklist.md` の対応 stack の smoke コマンドと整合させる
  - **権限境界の未定義**: 自律実行可 / 確認必須の境界が書かれていない、または REGIME.md の dev_mode / autonomous_scope と CLAUDE.md が不整合
  - **矛盾**: CLAUDE.md 内の記述同士、または SPEC.md / DONT.md / REGIME.md との間に矛盾がある（DONT 自己照合で拾えない CLAUDE.md 固有の矛盾）
  - **陳腐化の放置**: 既に存在しないファイル・廃止した手順・旧バージョン前提の記述が残っている（broken reference 検査で拾えない散文レベルの陳腐化）
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
- `references/l0-step-details.md` — §3.5 / §3.6 / §4 の詳細（v7.0.0 F10 で SKILL.md から逐語移送）
- `references/ritual-protocol.md` — 振り返り儀式プロトコル（4レベル判定・F1〜F3・E1/E2対応）

### 拡張（業務システム運用・社内版LINE型射程対応）

- `references/nfr-scoring.md` — NFR スコアリング規格（5 カテゴリ × 0-3 点、オーバーライド 4 条件、N=0 後方互換）
- `references/arc-patterns/monolith.md` — ARC デフォルト（単一デプロイ単位、AI 自走完遂の標準形）
- `references/arc-patterns/realtime-pubsub.md` — リアルタイム pub/sub パターン（社内版LINE型、大量同時接続）
- `references/arc-patterns/event-sourcing.md` — イベントソーシング（監査必須、時系列復元、スキーマ進化完全準拠）
- `references/schema-evolution.md` — データモデル進化プロトコル（互換性ポリシー / デプロイ戦略 / upcasting）
- `references/supabase-local-dev.md` — Supabase ローカル開発環境（v5.18.0 追加 / v6.19.0 で適用範囲を限定。本番保護のローカル優先フロー / migration 経由の本番反映 / セキュリティ規律。**S1 = DB 使用あり + 既存の Supabase プロジェクトがある案件でのみロード**。新規案件の供給元既定としては用いない — 同ファイル §適用範囲）
- `references/cloudflare-workers-dev.md` — Cloudflare Workers 開発環境（v6.19.0 F3 追加。ローカル優先フロー（`wrangler dev` は既定でローカル・Docker 不要）/ 設計上の罠カタログ C1〜C11 / 静的と動的の課金境界 / smoke test。**Workers・D1 を使う案件でのみロード**。**無料枠の数値表を持たない** — 正本は `crosscut-quota-observer/references/adapters/cloudflare.md`）
- `references/permission-delegation.md` — 段階的権限委譲（L0-2/L0-3、介入チャネル C1/C2/C3、判断献上 5 カテゴリ）
- `references/domain-context-dialog.md` — ドメイン文脈対話プロトコル（DOMAIN-CONTEXT.md、機密分離、5 対話カテゴリ）
- `references/design-system-spec.md` — DESIGN.md 規格と対話プロトコル（v5.15.0 追加、UI プロジェクトのみ起動。Google Labs 公式仕様準拠、Do's and Don'ts によるアンカリング正方向活用、3 問プロトコル DG2〜DG4）
- `assets/design-md-template.md` — DESIGN.md 実践テンプレート（v5.15.0 追加、YAML トークン + Markdown 本体 + Components 拡張ガイド）
- `references/test-oracle-dialog.md` — C5 テスト oracle 言語化プロトコル（v5.23.0 追加、§2.6 から起動。critical journey or UI プロジェクトのみ。TQ1-3 で人間の暗黙の関心を言語化し相 B E2E 母集団を SPEC へ確定）
- `references/brainstorm-orchestration.md` — L0 ブレスト・対話支援の実行基盤（v6.11.0 F5 追加。多角調査 fan-out の標準形 3 段・議論型協調層の使用判断 3 条件・degrade 経路。成果は判断材料であり判定を含まない）
- `../../../templates/rules/common/ui-baseline.rules.md` — UI Baseline RL（v5.23.0 追加、UI プロジェクトの相互作用層・常時適用。B-01〜B-25 + レビューチェックリスト。適用経路は `references/design-system-spec.md`「UI 相互作用層」）
- `../../../templates/rules/common/ui-specialization.context.md` — UI Specialization Context（v5.23.0 追加、目的特化 S-01〜S-06 + 衝突解決。S-xx 選択は §3.6 / UX 3問 / NFR と連動、`.dh/rules/` で override 可）

### 版履歴

v3.1〜v6.3.0 の版ごとの追加記録は `history/CHANGELOG.md` §layer0-spec-architect SKILL.md 版履歴 へ移送（v7.0.0 F10）。本節に戻さない。
