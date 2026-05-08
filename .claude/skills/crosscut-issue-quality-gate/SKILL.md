---
name: crosscut-issue-quality-gate
dimension: D4
description: >
  GitHub Issue の品質を 12 項目（A-E の 5 軸 + 7 ローマ数字補助軸）で機械検査 + AI 推論のハイブリッド検査する横断機構。
  「この Issue 品質チェックして」「ready-for-ai 付ける前に 12 軸で見て」
  「Issue 品質ゲートで弾かれた、どの軸で fail」「並列安全性軸って何見てるの」
  「dispatcher が生成した Issue 群、どれが gate 通過したか」
  「issue-quality-checklist.template.md を手動でチェックしたい」「fractal-application どの粒度で再帰検査」
  「Council 起点 Issue を gate 経由」等、ready-for-ai ラベル付与前の Issue 検査と
  並列安全性（scope / mutex / depends-on / 影響範囲衝突 4 段階フィルター）に関する発話で
  本スキルの起動を必ず検討する。
  3 つの発動契機: (a) issue-dispatcher 内部から自動通過 / (b) 人間明示「品質チェック」 / (c) Council judgment 起点 Issue。
  「Issue にして」（→ issue-dispatcher）「Issue 自動実装」（→ issue-implementer）
  「テスト品質ゲート CI 設定」（→ 別文脈）との混同を避ける。
  v5.10.0: type-aware 化（discussion ラベル分岐、規格は issue-implementer SKILL.md を一次情報源）。
---

# Issue Quality Gate

## 発動条件

本 skill は **3 つの発動契機** で起動する横断機構として設計されている：

### (a) crosscut-issue-dispatcher 内部から必ず通過
- SPEC/ADR 差分起点の Issue 生成時
- `crosscut-issue-dispatcher` の処理フロー内で automatic で呼び出される

### (b) L0 / Council / D4〜D2 献上時に明示呼び出し
- L0 spec-architect 対話セッション終了時
- Council 献上 Issue 作成時  
- D4〜D2 献上起点の Issue 作成時
- 人間対話・合議起点では明示的に skill 呼び出しが必要

### (d) GitHub Actions で ready-for-ai ラベル付与時に最終ガード
- Issue に `ready-for-ai` ラベルが付与されたタイミング
- `crosscut-issue-implementer` 起動直前の最終ガード
- workflow template: `templates/github-workflows/issue-quality-gate.yml.template`

発動契機 (c)（Issue ライフサイクル全体ガード）は本 v5.8.0 では除外（過剰負荷を避ける）。

## 12 軸品質チェック

本 skill は 12 軸で Issue 品質をチェックする。各軸は **機械検査** + **AI 推論** のハイブリッドで構成される：

| # | 軸 | 機械検査 | AI 推論 | 合格基準 |
|---|---|---|---|---|
| A | 仕様整合 | SPEC.md/DONT.md grep | 意味的整合 | プロジェクト固有 SPEC と矛盾なし |
| B | データ整合 | schema diff・migration 必須化 | 後方互換意図 | schema-evolution.md 準拠 |
| C | コード整合 | 既存抽象 grep | 重複抽象判定 | 既存抽象を再利用 |
| D | 依存整合 | package.json diff・licence-checker | メンテ状況判定 | ライセンス OK、bundle 増加 ≤10% |
| E | 品質均一化 | テスト/sensor 必須項目 grep | テスト粒度妥当性 | 既存と同等以上の規格 |
| ii | 重複検出 | 既存 Issue title/body n-gram 類似度 | 意味的重複判定 | 類似度 >0.7 の既存 Issue が無い |
| iii | セキュリティ | secrets scan・auth 関連 grep | 認可モデル整合 | OWASP top 10 観点 |
| v | 後方互換 | API/DB schema diff・semver 必須化 | 影響範囲判定 | 破壊的変更時はロールバック計画必須 |
| **vi** | **観測性統一** | 収集層: schema 統一・命名規則 grep / 提示層: dashboard 項目数・カーディナリティ閾値 | 収集と提示の二層整合性判定 | **収集層=精緻・構造化、提示層=P3 が一目で解釈可能** |
| vii | ドキュメント波及 | INDEX.md/README/ADR 更新 grep | — | 該当ドキュメントへの更新含む |
| viii | テスト粒度 | テストファイル存在・カバレッジ閾値 | TDD 妥当性 | Issue 段階で test-first 計画明示 |
| **ix** | **並列安全性** | scope/mutex/depends-on ラベル grep + in-progress Issue list 取得 | 影響範囲衝突の意味的判定 | **scope/mutex 整合、depends-on 循環なし、in-progress と影響範囲衝突なし** |

詳細な判定基準・実装例・層×軸マトリクスは `references/twelve-axes.md` を参照。

### 軸 vi 補足: 観測性の二層モデル

軸 vi は **観測性の二層モデル** で評価する：

- **収集層 (Raw)**: log / metric / trace / event を精緻に・高解像度で・構造化して取る。後追い分析と LLM 推論のため、データは薄くしない
- **提示層 (Presentation)**: 収集データを P3（人間の事後確認）が一目で理解できる粒度に集約・整理する

両層が **同じ命名規則・同じ schema 系** で繋がっていることが Council 入力基盤としての必須条件。

### 軸 ix 補足: 並列安全性の 4 段階フィルター

Issue 並列実行時のコンフリクトは git で検出可能な物理コンフリクトの他に、**論理・意味・依存** の 3 種が存在する。本軸はこれを 4 段階フィルターで事前検知する：

```
[1] scope ラベル (機械的) ← 基本ガード、workflow concurrency 分割
       ↓
[2] mutex ラベル (機械的) ← 明示排他、共有抽象を保護
       ↓
[3] depends-on 宣言 (機械的) ← 論理依存を表現、順序保証
       ↓
[4] AI 推論 ← (2)(3) の見落としを意味的に検知（in-progress Issue との影響範囲衝突）
```

## 処理フロー

1. **前提チェック**: Issue の基本構造（title/body 存在、必須セクション）確認 — **type-aware (v5.10.0)**: `discussion` ラベル有無で必須セクション規格が分岐（下記 §Issue Type 分岐ルール）
2. **12 軸検査実行**: 機械検査 → AI 推論の順番で各軸を評価
3. **並列安全性チェック**: 軸 ix の 4 段階フィルターを実行
4. **合格判定**: 全 12 軸が合格基準を満たすかチェック
5. **結果処理**:
   - **合格**: `ready-for-ai` ラベル付与を許可
   - **不合格**: 理由ラベル（`gate-failed:axis-A` / `gate-failed:axis-vi` 等）を付与し、Issue は close せず人間差し戻し

### Issue Type 分岐ルール（v5.10.0 追加）

dialog-harness の Issue は philosophy 第 5 条（献上哲学）の起票元類型に従い 2 系統に分類される。本 Quality Gate と `issue-pickup.yml` body_check は同一の type 分岐ルールに従う（規格は `crosscut-issue-implementer/SKILL.md §Issue 本文必須セクション規格` を一次情報源とする）：

| Type | ラベル条件 | 必須セクション | 想定起票元 |
|---|---|---|---|
| **bug-style** | `discussion` ラベル**なし** | `## 再現手順` / `## 期待動作` / `## 受入条件` （3 セクション） | 利用者の bug 報告（philosophy 第 7 条 P1/P2）|
| **discussion-style** | `discussion` ラベル**あり** | `## L0 spec-architect 対話記録` / `## 実装スコープ` （2 セクション） | L0 起票・SPEC 改訂提案（philosophy 第 7 条 P3/P4）|

**12 軸との直交性**: 12 軸チェック（軸 i〜xii）自体は type 中立で、両 type に同様に適用される。type 分岐は前提チェック (step 1) の必須セクション検査にのみ影響する。具体的には:

- 軸 ix（並列安全性）: type 中立。`scope:*` / `mutex:*` ラベルは両 type で同様に検査
- 軸 vi（観測性）: type 中立。Council 入力データの整合性は両 type で保証必要
- 他軸も同様

詳細な必須セクション規格は `crosscut-issue-implementer/SKILL.md` の §Issue 本文必須セクション規格 を参照（重複定義を避けるため、本 SKILL.md ではルールの存在のみ記述）。

## Council 連携

観測性規格のバラつき = Council 3 ペルソナが同じ事実を見られない = 合議が成立しない、という構造的因果。

本 skill の軸 vi は **Council 判定の入力データレイヤー** 整合保証であり、philosophy.md 第 6 条「人間 ≒ Council」の実装上の前提条件として機能する。

詳細は `references/council-observability-link.md` を参照。

## 並列安全性機構

軸 ix は Issue 並列実行時の **論理・意味・依存** コンフリクトを事前検知し、以下のラベルを活用した制御を行う：

| ラベル種別 | 例 | 用途 |
|---|---|---|
| `scope:*` | `scope:db` / `scope:frontend` | 基本並列ガード（concurrency group） |
| `mutex:*` | `mutex:auth-model` / `mutex:state-machine` | 共有抽象の明示排他 |
| `refactor:*` | `refactor:major` / `refactor:minor` | Big Refactor 特例 |
| `freeze-period` | （単独） | リリース直前の全凍結 |

詳細は `references/parallel-safety.md` を参照。

## DH メタ自己適用（フラクタル原則）

DH 自身の Issue 化（`dh-upgrades` の upgrade-spec から派生する Issue 含む）も例外なく本 Gate を通過する。

本 Issue #46 自身が **「Gate 完成後に Gate を通すべきだった最初の事例」** として参照される。完成後の自己適用テストとして、本 Issue を遡及的に 12 軸チェックリストで採点する `delivery/self-gate-check-AD010.md` を出力する。

詳細は `references/fractal-application.md` を参照。

## 関連ドキュメント

### このスキル内 references/

- [references/twelve-axes.md](references/twelve-axes.md) — 12 軸の合格基準と判定例（層×軸マトリクス含む）
- [references/machine-checks.md](references/machine-checks.md) — 機械検査 grep/lint/script 規格
- [references/ai-judgment-rubric.md](references/ai-judgment-rubric.md) — AI 推論 rubric
- [references/activation-protocol.md](references/activation-protocol.md) — (a)(b)(d) 発動契機詳細
- [references/council-observability-link.md](references/council-observability-link.md) — 軸 vi が Council 入力データ基盤
- [references/parallel-safety.md](references/parallel-safety.md) — 軸 ix 並列安全性（4 段階フィルター）
- [references/fractal-application.md](references/fractal-application.md) — DH メタへの自己適用

### このスキル内 assets/

- [assets/issue-quality-checklist.template.md](assets/issue-quality-checklist.template.md) — プロジェクト固有テンプレ

### このスキル外

- `crosscut-issue-dispatcher/SKILL.md` — 発動契機 (a) 通過点として参照
- `crosscut-issue-implementer/SKILL.md` — 発動契機 (d) 通過確認として参照
- `layer0-spec-architect/SKILL.md` — 発動契機 (b) L0 起点として参照
- `crosscut-council/SKILL.md` — 発動契機 (b) Council 起点として参照
- `templates/github-workflows/issue-quality-gate.yml.template` — 発動契機 (d) 用 workflow
- `templates/github-workflows/issue-pickup.yml.template` — concurrency group を scope ラベルベースに変更

## バージョン

- **v0.1.0 (v5.8.0 で新設)**: 12 軸品質チェック + 並列安全性機構 + Council 連携
- 既存 skill の挙動・既存 Issue 形式に破壊的変更なし
- 新規 skill 不在でも DH ベースは通常動作（後方互換）