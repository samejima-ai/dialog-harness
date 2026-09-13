# 意図合致検証（v5.5.0 Phase γ コア 3 件）

> v7.0.0 Phase A F10 で `SKILL.md` §6 自己検証 から移送（SKILL.md を 500 行未満に保つ）。内容は不変。

**起動条件** (`../../layer0-archeo-architect/references/handoff-to-evaluator.md` §I/O 契約 L64-68 と同期):

```
exists("delivery/refactor-intent-map.md") AND map.Meta.self_verification == "passed"
```

両条件成立時のみ第 4 軸「意図合致」を起動する。`refactor-intent-map.md` 不在 / archeo 自己検証 FAIL のいずれかなら本ステップは完全スキップ（後方互換完全維持、3 軸動作）。

各 Island の `refactor_directive` と Boundaries の `human_decision` を **AND 結合**で評価する（archeo handoff contract 準拠、§79-84）:

##### preserve 領域 — `assertion: no_modification` 一次条件 + 承認テスト二次条件（先行宣言 1 本実装）

業界根拠: フェザーズ「レガシーコードとはテストのないコードである」/ Approval Testing カノン。

`refactor_directive: preserve` の Island は upstream 規約で「現状維持（リファクタ対象外）」= `assertion: no_modification`（archeo handoff §73-76 / refactor-intent-map-template.md §61-64）。検証は二段階：

**一次条件: コード変更ゼロの assertion 検査**

1. preserve Island の paths について `git diff` を実行
2. 変更行数 > 0（行追加・削除・編集のいずれか）→ **即 FAIL**（構造変更だけでもダメ、振る舞い同等でも禁止）
3. 変更ゼロ → 一次条件 PASS、二次条件へ

**二次条件: 既存テスト + 承認テストの振る舞い検証**（一次条件 PASS 時のみ実行）

1. 既存テストがある領域では既存テスト全件 PASS を確認
2. 既存テスト不足分のみ承認テストで補完: 現状のコードの入出力を `delivery/approval-tests/<island-id>.baseline.json` として基準データ化
3. 既存テストおよび承認テスト全件 PASS で二次条件 PASS

二次条件は「将来の仕様変更時の振る舞い記録」として運用される（一次条件で構造変更が禁止されているため、本来は冗長だが、preserve 領域に依存する他箇所の変更が間接的影響を与えないかの保険）。一次条件 / 二次条件のいずれか FAIL → **`failure: intent_drift`** として Type C 献上。

ツール選択（Qodo / Byteable 等）は L1 実装者の裁量。

##### restructure 領域 — 自動照合ループ（先行宣言 2 本実装）

業界根拠: VB6 価格エンジン移行事例（14 ヶ月で 8,064 回の自動照合ラン、0.007% 不一致検出、420 万ドル損失防止） / Branch by Abstraction パターン。

`refactor_directive: restructure` の Island は、**新旧並行実行 + 結果照合**で意図保持を機械的に検証する：

1. リファクタ前の実装を「旧」、後の実装を「新」として両方を残す（Branch by Abstraction）
2. 抽象化レイヤー越しに同入力を両者に流し、結果を比較し `delivery/reconciliation-logs/<island-id>.log` に記録
3. 不一致率の閾値（デフォルト 0.01%）を超えたら **`failure: intent_drift`** として Type C 献上
4. 並行実行期間（L1 実装者裁量、典型は 1〜2 週間）後、新実装に切替

L2 統合検証との接続: 複数 Island に渡る restructure では `layer2-integration-verifier` が照合結果を集約する（L2 発動時のみ、PR 範囲外）。

##### discard_and_redesign 領域

`AbsentZone.redesign_directive` に従う。意図保存制約は解除されているため承認テスト・自動照合は不要。

##### 判定の集約

意図合致軸の判定は `delivery/DELIVERY.md` に「意図合致検証」セクションとして記録する（フォーマット: `delivery-format.md` §意図合致検証 参照）。
