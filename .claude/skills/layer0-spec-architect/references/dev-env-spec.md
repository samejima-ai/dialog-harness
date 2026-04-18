# 開発環境ドキュメント規格

AI自律開発環境を構成するRL/SK/センサーの記述フォーマットと配置規約。
モード（M1/M2/L2）に応じて構成が変化する。

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

## .claude/skills/（プロジェクト固有SK）

プロジェクト固有の開発スキル。エージェントが必要に応じて動的に読み込む。

**重要な配置原則 — Level A と Level B の区別**:

- **Level A（ハーネス自身）**: 汎用スキル（layer0-spec-architect, layer1-autonomous-dev, layer1-independent-reviewer, layer2-integration-verifier, layer2-orchestrator）はハーネスリポジトリ側にのみ存在する。プロジェクト側で再生成・コピーしない
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
- .claude/skills/ （プロジェクト固有のみ。検証agent本体はハーネス側で持つ）
- sensors/computational.md
- sensors/inferential.md
- sensors/review-checklist.md（layer1-independent-reviewer がプロジェクト固有項目を参照する場合）

layer1-independent-reviewer の扱い：
- skill本体は**ハーネス側 Level A** に存在するため、プロジェクトでは再生成しない
- プロジェクト固有の検証観点が必要な場合のみ `sensors/review-checklist.md` を追加

### L2 統括指揮モード（稀・全体の<10%）

M2の構成に加え、L2オーケストレータと統合検証の定義を追加する。

追加生成物：
- DOMAINS.md（ドメイン境界の定義。L2オーケストレータが生成）
- 各ドメイン配下の部分 SPEC（SPEC.md から切り出し）
- sensors/integration/ 配下の統合sensors（contracts.md, invariants.md, e2e.md）

layer2-orchestrator / layer2-integration-verifier の扱い：
- skill本体は**ハーネス側 Level A** に存在するため、プロジェクトでは再生成しない
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
