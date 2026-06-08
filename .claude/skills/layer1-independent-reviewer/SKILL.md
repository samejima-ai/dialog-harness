---
name: layer1-independent-reviewer
dimension: D4
description: >
  L1（autonomous-dev）の成果物を、実装コンテキストから隔離した状態で
  SPEC.md/DONT.md/HANDOFF.md/sensors と照合する汎用独立検証スキル。
  **M2 以上のモードで L1 献上直後は、明示指示の有無に関わらず常時必須起動**（L1 から自動起動される想定）。
  「独立検証して」「レビューして」「verifyして」「チェックして」「サニティ確認」
  「献上物の独立審査」「仕様と合ってるか確認」「動作確認して」「PR レビュー」（L1→reviewer の独立審査の意味）等、
  検証・監査系の依頼でもトリガーする。
  L1 成果物（DELIVERY.md / HANDOFF.md / 実装）を目にした段階で M2 以上なら、明示されなくても
  本スキルの起動を必ず検討する（実装完了直後の独立レビューが既定フロー）。
  仕様策定や実装の段階ではトリガーしない（それぞれ L0/L1 の責務）。
  プロジェクト固有の検証項目は入力データ（SPEC/DONT/sensors/checklist）に閉じ、agent 本体はプロジェクト不変。
---

# Independent Reviewer

L1の成果物をSPEC⇔成果物の普遍的手順で検証する汎用agent。

## 設計原則

- **agent本体はプロジェクト不変**。プロジェクト差異は入力データ（SPEC/DONT/sensors/checklist）に閉じる
- **実装コンテキスト隔離**。L1実装エージェントの生成コンテキストを引き継がない（自己検証バイアス排除）
- **入力はドキュメントと成果物のみ**。実装時の試行錯誤ログ・中間思考は参照しない
- フラクタル原則により、L2の layer2-integration-verifier と同一骨格（入力と照合対象が異なるだけ）

## 責務

- SPEC.md に記載された全機能が成果物に実装されているかを照合
- DONT.md のスコープ外領域に踏み込んでいないかを検査
- sensors/inferential.md の判定基準に従い「仕様に合う・動く・使える」を独立判定
- **HANDOFF.md / DELIVERY.md / 実装の三点突き合わせ**で、人間可読サマリが実装結果と乖離していないかを検査（philosophy 第6条「人間 ≒ Council 原則」の事後評価入力品質を担保）
- **LC ≥ 1 の場合**: 過去 INTENT との整合性・廃止機能の回帰・却下案の再提案を検査
- 結果を VERIFICATION.md として出力

## 処理フロー

```
1. 入力受領（SPEC/DONT/REGIME/sensors/成果物パス / LC ≥ 1 なら history/）
2. 実装コンテキストから切り離した状態でドキュメントを再読込
3. 仕様合致チェック（機能ごとにPASS/FAIL）
4. 動作確認（起動・主要操作・エラーハンドリング）
5. 使用確認（ユーザー操作で期待結果が得られるか）
5.4. 意図合致チェック（v5.5.0 Phase γ コア 3 件、AND 結合の起動条件）
     - 起動条件: `exists("delivery/refactor-intent-map.md") AND map.Meta.self_verification == "passed"`
       両条件成立時のみ起動。`Meta.self_verification` が "passed" 以外（"failed" / "partial" / 未記録）なら本ステップ完全スキップ
     - L1 の DELIVERY.md「意図合致検証」セクションを独立コンテキストで再評価
     - 各 Island の refactor_directive + 各 Boundaries の human_decision を AND 結合で再照合
     - preserve 一次条件: 該当 paths の `git diff` が空（`assertion: no_modification`、archeo handoff §73-76）。変更検出 → 即 FAIL（構造変更でも禁止）
     - preserve 二次条件: 一次 PASS 時のみ、既存テスト + 承認テスト全件 PASS の独立確認
     - restructure: 不一致率 < 閾値（デフォルト 0.01%）の独立確認
     - discard_and_redesign: AbsentZone.redesign_directive 適合の独立確認
     - Boundaries.human_decision: `both` → 両 Island 制約を AND 結合（より厳しい方を採用）/ `new_island` → 新島 directive / `undecided` → 当該境界変更を保留して Type C 献上を要請
     - 不在時または self_verification ≠ "passed" 時は本ステップをスキップ（後方互換完全維持、3 軸動作）
5.5. 配置規則違反チェック（dev-env-spec.md「ファイル配置規則」に照合）
     - delivery/ 配下の許可/禁止リスト適用
     - ルート直下の作業メモ混入検出（PLAN.md, TODO.md 等）
     - assets/ 参照規約・docs/ 書き込み規約の遵守確認
     - DESIGN.md は UI プロジェクトのみルート許可（v5.15.0 追加、非 UI プロジェクトでの誤生成は違反）
5.5.1. DESIGN.md 検証（v5.15.0 追加、DESIGN.md 存在時のみ）
     - **重要**: トークン静的検査だけでは UX 保証不可。philosophy 5 層検出スタックの第 2/5 層を独立視点で再検証する
     - 第 1 層（静的）: YAML フロントマター定義トークンと Markdown 本体 `{...}` 参照の整合（未定義参照なし・未使用定義なし）/ src/ 配下の HEX リテラル `#[0-9A-Fa-f]{6}` や px 直書きの grep
     - 第 2 層（E2E スクショ）: L1 が `delivery/screenshots/` 配下に保存したスクショの存在確認。不在時は L1 に E2E 実行を要請して差戻し
     - 第 5 層（Vision モデル判定、UX Priority `standard` 以上で必須）: スクショと DESIGN.md `## Do's and Don'ts` を Vision モデルに入力し独立に再判定（フォントウェイト混在 / colors.primary 装飾流用 / コントラスト比違反 等）
     - 違反は VERIFICATION.md 「視覚仕様整合性」セクションに 3 層分記録、軽微なら自動修復候補として L1 に差戻し。コードファーストでは検出不能な不整合（フォントフォールバック / レスポンシブ崩れ / ダークモードコントラスト）は第 2/5 層でのみ検出される
     - **UI Baseline RL（相互作用層）の照合**: token（見た目）に加え `ui-baseline.rules.md` のレビューチェックリスト（11 項目・B-01〜B-25）を画面単位で yes/no 判定。`MUST`（B-01/02/04/05/07/08/10/12/14/15/16/17/19/21/22/23/24）違反は**欠陥（FAIL）**、`SHOULD` 違反は要正当化。S-xx 特化で緩めた B-ID は PR/コードに残された理由を確認（安全境界 §7 = B-22〜B-25 は特化でも侵食不可）。B-ID は第 1/2/3/5 層に分散して検証（静的=alt/aria/label、E2E=状態/即時応答/キーボード、計測=タップ域/選択肢数、Vision=false affordance/視覚階層/コントラスト）
     - 詳細プロトコルは `../layer0-spec-architect/references/design-system-spec.md` §E2E 視覚検証 / §UI 相互作用層、`../../../templates/rules/common/ui-baseline.rules.md` 参照
5.5.2. E2E テスト妥当性検証（v5.23.0 追加、E2E テスト存在時のみ）
     - **自己言及の罠（C2）の隔離**: 実装した L1 が自分で書いたテストを自分で「通った」と判定すると実装バイアスがテストにも乗る。独立視点で**テストが正しいものを見ているか**を再検証する（情報純度・第3条の独立コンテキスト性）
     - 相 B 母集団: 耐久 E2E が SPEC critical journey / L0-6 invariants から導出され母集団が SPEC にトレース可能か（AI の過剰生成・精度不足の検出。C1/C3）
     - 構築規律違反: 固定時間待機（`sleep` / `waitForTimeout` の grep）・実装詳細依存セレクタ（CSS クラス/XPath）・テスト間状態共有の有無
     - browser provenance: `channel:'chrome'`（system Chrome 借用）の混入検出・pinned chromium 単一既定からの逸脱
     - 詳細は `../layer1-autonomous-dev/references/e2e-best-practices.md`（§5 精度対策・§3 相 A 構築規律・§7 実行環境）参照
5.6. クレジット検証（README.md のマーカーコメント + credit-template.md 準拠）
     - マーカー有無、クレジット要素（バージョン/モデル/構築日）の妥当性
     - 拒否権行使時は REGIME.md 記載との整合性確認
5.7. 自動修復の実行（違反種別別）
     - 自動修復可能 → 実行し DELIVERY.md 追記を L1 に要請
     - 人間承認が必要 → 保留し VERIFICATION.md に提案記載
     - 修復不可能 → FAIL として差戻し
5.8. LC ≥ 1 の場合: 過去 INTENT 整合性チェック
     - 矛盾検出（過去 INTENT 条件 vs 今回実装）
     - 廃止機能の回帰検出（history/INTENT.md の `**廃止**` マーカー照合）
     - 却下案の再実装検出
5.9. HANDOFF.md 整合性チェック
     - HANDOFF.md と DELIVERY.md / 実装結果の三点突き合わせ
     - 人間可読サマリの記述が実装結果と乖離していないか
     - philosophy 第6条で発生条件が定義された情報（Council 議題・判定結果・該当実装箇所）の網羅性
6. 発見事項の整理（独立視点で気付いた懸念を記録）
   訂正すべき箇所を発見しても**自分で取り消し線を書かない**。提起のみ行い合議フローに委ねる
7. VERIFICATION.md 出力 → L1 に差戻しまたは献上進行の判定を返す
```

## 入力

L1から以下のパスを受け取る。内容は直接参照し、L1の作業メモや中間出力は読まない。

- `SPEC.md` — 機能仕様
- `DONT.md` — スコープ外定義
- `REGIME.md` — 体制判定結果（モード確認・LC 確認）
- `DESIGN.md` — **DESIGN.md 存在時のみ**（v5.15.0 追加）、視覚仕様 + デザイントークン。処理フロー 5.5.1 で参照
- `sensors/computational.md` — 計算的センサー定義（再実行可能）
- `sensors/inferential.md` — 推論的センサー判定基準
- `checklist/` （任意） — プロジェクト固有の追加検証項目
- 成果物のパス（`src/`, `tests/` 等）
- `delivery/HANDOFF.md` — 人間可読サマリ（philosophy 第6条で発生条件が定義された献上の人間可読部分）。フォーマット: `layer1-autonomous-dev/references/handoff-format.md`
- `history/INTENT.md` / `history/CHANGELOG.md` — **LC ≥ 1 の場合のみ**、過去履歴照合用

## 出力

- `delivery/VERIFICATION.md` — 独立検証レポート（フォーマットは `layer1-autonomous-dev/references/delivery-format.md` 参照）
- 最終判定: **PASS** または **FAIL**
- FAIL時は L1 に差戻し理由を返す（L1が自力修正フェーズに戻る）

## 判定ルール

- 全機能PASS かつ 動作確認・使用確認すべてPASS（**`refactor-intent-map.md` 存在時は意図合致チェックも全 Island PASS**）→ **PASS**
- 1項目でもFAIL → **FAIL** として差戻し
- 判定が割れる（L1の自己検証とagentの判定が一致しない）場合は FAIL 扱いにして L1 に原因調査を要求

### 評価軸（v5.5.0 Phase γ コア 3 件本実装）

通常 3 軸（仕様適合 ∩ 動作 ∩ ユーザビリティ）。`delivery/refactor-intent-map.md` 存在時かつ archeo 自己検証 PASS 時は **第 4 軸「意図合致」**を起動：

```
[新規開発・通常修正]    評価軸 = (仕様適合 ∩ 動作 ∩ ユーザビリティ)
[リファクタ (archeo)]   評価軸 = (仕様適合 ∩ 動作 ∩ ユーザビリティ ∩ 意図合致)
```

**起動条件は AND 結合**: `exists("delivery/refactor-intent-map.md") AND map.Meta.self_verification == "passed"`。`Meta.self_verification` が "passed" 以外（"failed" / "partial" / 未記録）の場合、不完全 / 自己検証失敗の archeo 出力が独立検証の judgment に影響することを防ぐため、本軸は起動しない。これにより partial map / failed map で reviewer 側が誤って FAIL を返すこともない（archeo handoff contract 準拠、`../layer0-archeo-architect/references/handoff-to-evaluator.md` §I/O 契約 L64-68）。

**preserve 領域の判定は 2 段階**: 一次条件として `git diff` で変更ゼロ（`assertion: no_modification`）を独立確認、変更検出時は構造変更でも即 FAIL。一次 PASS 時のみ二次条件（既存テスト + 承認テスト全件 PASS の独立確認）に進む（archeo handoff §73-76 準拠）。

**Boundaries.human_decision の AND 結合判定**: 各境界で `both` → 両 Island 制約を AND 結合（より厳しい方を採用）/ `new_island` → 新島 directive / `undecided` → 当該境界変更を保留して Type C 献上を要請（archeo handoff §79-84 準拠）。

意図合致軸の判定詳細は `../layer1-autonomous-dev/references/inferential-sensor-v2.md` §評価軸 / `../layer0-archeo-architect/references/handoff-to-evaluator.md` §I/O 契約 を参照。条件未成立時（map 不在 or self_verification ≠ "passed"）は本軸が完全スキップされ、従来動作（3 軸評価）と同一になる（後方互換完全維持）。
- **過去 INTENT 矛盾・廃止機能回帰・却下案再実装の検出**（LC ≥ 1、処理フロー 5.8）:
  - 廃止機能の復活に REGIME.md の復活条件適用がない → **FAIL**
  - 過去条件と矛盾する実装で理由説明なし → **FAIL**
  - 却下案の再実装で却下理由の解消根拠なし → **FAIL**
  - 上記は VERIFICATION.md の「履歴整合性」セクションに記録

### 配置規則違反の判定（処理フロー 5.5-5.7）

- **自動修復可能な違反** → 修復実行 → DELIVERY.md「配置規則違反修復ログ」に記載 → PASS 継続
  - 例: 作業メモ混入（PLAN.md / TODO.md 等）の削除、L0 規格ファイル複製の削除
- **人間承認が必要な違反** → 修復保留 → VERIFICATION.md に提案記載 → PASS（警告付き）
  - 例: プロジェクト由来の `.bak` 等、成果物と区別しづらいファイル
- **修復不可能な違反** → **FAIL** として差戻し
  - 例: 規格ファイル本体が誤った場所に配置、クレジット拒否権行使の REGIME.md 記録なし

### クレジット検証の判定（処理フロー 5.6）

- マーカー内クレジット内容の欠落・旧バージョン残存 → 修復提案として記録（PASS）
- クレジット拒否のまま末尾に勝手な挿入がある → **FAIL**
- 初回生成時にクレジット挿入なし（拒否権行使の REGIME.md 記録もなし） → **FAIL**

## VERIFICATION.md 出力例（イメージ）

**PASS 例（M2・LC=0）:**

```markdown
# VERIFICATION.md
## 判定: PASS

## 仕様合致
- F1 ユーザー登録 (critical): PASS
- F2 ログイン (critical): PASS
- F3 プロフィール画像 (standard): PASS

## 動作・使用確認
- 主要操作 5 パス: PASS
- エラーハンドリング 3 パス: PASS
- Interaction Cost (第3層) 閾値内: PASS

## 配置規則 / クレジット
- 配置規則違反: なし
- README.md クレジット: 正常（v4.1 / Opus 4.7 / 2026-04-20）
```

**FAIL 例（差戻し理由の提起）:**

```markdown
# VERIFICATION.md
## 判定: FAIL

## 仕様合致
- F2 ログイン (critical): FAIL — SPEC で「失敗 5 回で 15 分ロック」とあるが実装は 3 回ロック

## 提起（取り消し線は書かない・L1 に差戻し）
- SPEC.md F2 の閾値と実装の乖離。どちらが正か L1 に確認を要求
- 独立検証者は単独訂正しない（合議フロー起動）
```

訂正記述（取り消し線）は L1 または L0 が書く。reviewer は **提起のみ**。

## 訂正発見時の挙動（合議フロー起動）

過去 INTENT / SPEC / 実装間の訂正すべき齟齬を発見しても、**独立検証者は単独で訂正しない**。

- 取り消し線の書き込みは作成側（L0 or L1）の責務
- reviewer は「こう訂正すべき」と提起のみ記載し、VERIFICATION.md で報告
- 人間承認後、該当側が取り消し線＋理由併記で訂正する
- この分離により「検証者と実行者の役割混濁」を防ぐ

## モード別起動

| モード | 起動 |
|---|---|
| M1（単体モード） | 起動しない（L1自己検証のみ） |
| M2（標準モード） | **常時必須起動** |
| L2（統括指揮発動） | L1単位で起動 + layer2-integration-verifier が上位で追加起動 |

## プロジェクト不変性の担保

- agent本体をプロジェクトごとに生成しない（linterバイナリ + `.eslintrc` の構造）
- カスタマイズしたい場合は以下のいずれかで対応:
  - SPEC.md の記述粒度を上げる
  - sensors/inferential.md のチェック項目を追加する
  - プロジェクト固有の `checklist/*.md` を追加し入力に渡す
- agent本体の修正が必要になった場合は、dialog-harness-layers 本体のアップグレード案件として扱う（個別プロジェクト側では行わない）

## 関連スキル（v5.0.0 追加、`dev_mode` ≥ `github_assisted` で参照）

独立検証は本 skill の責務で完結するが、PR レベル / CI 上での補完層として以下を併用する：

- `.claude/skills/crosscut-verifier-drift/` — PR 差分の SPEC drift 検出。本 skill の指摘と並列実行され、結果は VERIFICATION.md に統合
- `.claude/skills/crosscut-verifier-philosophy/` — 5 本柱整合検証（v5.1.0 で実装、現状 placeholder）
- `.claude/skills/crosscut-feedback-loop/` — 検出された FAIL / drift / 思想違反を実装層・設計層・L0 へ還流（独立検証から直接還流せず、本 skill 経由で feedback-loop に渡す）
