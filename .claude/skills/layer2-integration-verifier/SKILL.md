---
name: layer2-integration-verifier
dimension: D4
description: >
  L2発動時のみ起動される汎用統合検証スキル。
  複数L1ドメインの成果物が揃った後、跨ぎドメイン整合性・全体不変条件・E2E動作を検証する
  （素朴に言えば「ドメインを跨いだ整合性が壊れていないか」「全体としてちゃんと動くか」を確認する）。
  REGIME.md でモードが L2 と判定された場合に layer2-orchestrator から起動される。
  単一ドメインの成果物レビューはトリガーしない（それは layer1-independent-reviewer の責務）。
  agent本体はプロジェクト不変。プロジェクト差異は INTEGRATION.md チェックリストと統合sensorsに閉じる。
---

# Integration Verifier

L2配下のL1群成果物を横断的に検証する汎用agent。

## 設計原則

- **agent本体はプロジェクト不変**。layer1-independent-reviewer と同一骨格（フラクタル原則）
- **入力と照合対象が異なるだけ**: 対象が「単体成果物 vs SPEC」から「複数成果物 vs 統合仕様」に変わる
- 各L1ドメインの VERIFICATION.md が全てPASSであることを前提条件とする（FAIL が残っていれば先にL1差戻し）
- agent間通信は自然言語経由で情報損失が発生することを前提に、ドキュメント化された契約のみを信頼する

## 責務

- ドメイン間インターフェース契約の整合性検証
- 全体不変条件（SPEC.md のクロスドメイン制約）の検査
- E2E シナリオの動作確認
- **Playwright Test Agents の出力統合**（`../layer2-orchestrator/references/e2e-integration.md` で規格化された Planner/Generator/Healer/Reviewer の成果物を受け取り、`delivery/e2e/review.md` を INTEGRATION.md に含める）
- 不整合検出時の調停判断（どのL1に差戻すかの指示）
- 結果を INTEGRATION.md として出力

哲学的背景は `../layer0-spec-architect/references/philosophy.md` §3（情報純度原則）を参照。

## 処理フロー

```
1. 入力受領（SPEC/DOMAINS/REGIME/統合sensors/各L1のVERIFICATION.md群/成果物群）
2. 前提確認（全L1のVERIFICATION.mdがPASSか）
   → 1件でもFAIL → L2オーケストレータに差戻し（本フェーズには進まない）
3. インターフェース契約の整合性検証
4. 全体不変条件の検査
5. E2Eシナリオ実行
6. 不整合があれば調停（どのL1に差戻すか特定）
7. INTEGRATION.md 出力 → L2オーケストレータに最終判定を返す
```

## 入力

- `SPEC.md` — 全体仕様
- `DOMAINS.md` — L2が生成したドメイン境界定義
- `REGIME.md` — L2判定の根拠（規模・サブドメイン構成）
- `sensors/integration/` — 統合sensors（E2E・契約検証）
- 各ドメインの `delivery/VERIFICATION.md`
- 各ドメインの成果物パス

## 出力

- `delivery/INTEGRATION.md` — 統合検証レポート（フォーマットは `layer1-autonomous-dev/references/delivery-format.md` 参照）
- 最終判定: **PASS** または **FAIL**
- FAIL時は差戻し対象のドメインと理由を明記

## 判定ルール

- 全契約PASS かつ 全不変条件PASS かつ E2E PASS → **PASS**
- 1項目でもFAIL → **FAIL**。どのL1に差戻すか or L2再設計が必要かを判定
- 契約不整合が判定できない場合（仕様側に曖昧さ）は L0 への仕様フィードバックとして L2オーケストレータに返す

## INTEGRATION.md 出力例（イメージ）

2 ドメイン（cart / payment）で契約不整合を検出した FAIL 例:

```markdown
# INTEGRATION.md
## 判定: FAIL

## 前提確認
- cart / payment の VERIFICATION.md: 両方 PASS（個別検証は通過）

## 契約整合性
- ❌ cart → payment の注文 ID 型不整合
  - cart 側: `orderId: string (UUID v4)`
  - payment 側: `orderId: number (auto-increment)`
  - 個別 SPEC では両方 PASS だが統合時に型変換層が欠落

## 全体不変条件
- ✅ 決済完了時のカート空化: PASS
- ❌ 在庫ロック解除の冪等性: 同一 orderId で 2 回 payment 失敗した場合にロックが残留

## E2E シナリオ（Playwright Test Agents review.md 統合）
- 正常系 3 件 PASS
- 異常系「決済失敗 → カート復元」: FAIL

## 差戻し判断
- cart と payment の **両方** に差戻し。orderId 型を SPEC.md に明記のうえ型変換契約を追加
- L0 仕様フィードバックも同時発行（契約抽象度が不足）
```

単一 L1 の仕様レビュー範囲を超えるため、L2 調停として L0 にも差戻す判断が必要なケース。

## モード別起動

| モード | 起動 |
|---|---|
| M1 / M2 | 起動しない（単一L1で完結） |
| L2 | **常時必須起動**（L1群の VERIFICATION.md が全てPASS後に発動） |

## プロジェクト不変性の担保

- layer1-independent-reviewer と同じ原則:
  - agent本体を個別プロジェクト用にカスタマイズしない
  - プロジェクト差異は `sensors/integration/` と `DOMAINS.md` に閉じる
  - 特殊な統合ルールが必要な場合はチェックリスト追加で対応
