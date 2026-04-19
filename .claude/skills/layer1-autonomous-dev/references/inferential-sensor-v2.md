# 5層エラー処理スタック — 推論的センサー v2

L1 自己検証で用いる5層スタックの定義。各層の責務・発動順序・層間境界を規定する。
哲学的背景は `../../layer0-spec-architect/references/philosophy.md` §2（Shift Left）を参照。

---

## スタック全体像

エラー処理は**左ほど優先**。計算的解決を最優先し、推論・人間判断は最後の砦として使う。

| 層 | 名称 | 目標解決率 | 種別 | 実行コスト |
|---|---|---|---|---|
| 第0層 | 設計時発生防止 | 30% | 構造的 | 無料（設計段階で完結） |
| 第1層 | 計算的センサー | 30% | 決定論的 | 極小（1分以内） |
| 第2層 | E2E機械検証 | 20% | 決定論的 | 小（分単位） |
| 第3層 | Interaction Cost 測定 | 10% | 定量 | 小（分単位） |
| 第4層 | 推論的センサー | 7% | 確率的 | 中（LLM呼び出し） |
| 第5層 | Vision / 人間判断 | 3% | 確率的 / 人間 | 大（人間介入） |

**原則**: 下層（右）は上層（左）が完遂してから発動する。「E2E を回す前に Console エラーゼロ」「推論検証の前に型・テスト通過」を厳守する。

---

## 第0層 設計時発生防止（目標解決率 30%）

**エラーが発生する余地を設計段階で排除する**。最左・最優先。

### 手段

- **型システム**（TypeScript strict, Zod）: 不正な状態を型で表現不能にする
- **ドメインモデル**（subphase-l02-domain.md）: 不変条件をコードで表現する
- **状態機械**（XState, subphase-l04-transition.md）: 不正な遷移を到達不能にする
- **認可モデル**（OpenFGA, subphase-l05-authz.md）: 権限チェックを宣言的に定義
- **層間不変条件**（Gherkin, subphase-l06-invariants.md）: 境界条件を事前に列挙

### 参照

- `../../layer0-spec-architect/references/subphase-l02-domain.md`
- `../../layer0-spec-architect/references/subphase-l03-api.md`
- `../../layer0-spec-architect/references/subphase-l04-transition.md`
- `../../layer0-spec-architect/references/subphase-l05-authz.md`
- `../../layer0-spec-architect/references/subphase-l06-invariants.md`

### L1 での責務

L0 が生成した `spec/` 配下の成果物（domain.ts / api.tsp / state-machine.ts / authz.fga / invariants.feature）を**信頼して使う**。L1 はこれらを書き換えない。逸脱を検知したらタイプA献上。

---

## 第1層 計算的センサー（目標解決率 30%）

**決定論的に検出できる問題を機械が検出する**。

### 手段

- ビルド（`sensors/computational.md` の build コマンド）
- 型チェック（tsc --noEmit 等）
- リンター（eslint / biome / clippy 等）
- 単体テスト（vitest / jest / pytest 等）

### 成功条件

全項目 exit code 0 / エラー0件 / 全件 PASS。**1分以内完了**の制約。

### Console エラー根絶原則

第2層 E2E に進む前に、**Console エラー・型エラーをゼロ**にする。上流の汚染を残したまま下流で検出しようとすると検出精度が落ちる。

### 参照

- `../../layer0-spec-architect/references/dev-env-spec.md` の `sensors/computational.md` 規格

---

## 第2層 E2E機械検証（目標解決率 20%）

**実行時の動作を機械が自動再現する**。

### 手段

- Playwright（主流）/ Cypress / Puppeteer
- シナリオベースの操作再現
- DOM 状態・URL・ネットワーク応答のアサーション
- スクリーンショット比較

### L1 単独での実行

L1 単独（M1/M2）では Playwright テストを **L1 自身が書き、L1 自身が実行**する。独立 Agent は立てない。

### L2 配下での Playwright Test Agents

L2 発動時は専用の Agent 群を配下に並列起動する。**配置先**: `../../layer2-orchestrator/references/e2e-integration.md`

L1 はこの事実を知っていれば足りる（L2 委譲時に自動的に使われる）。

### sensors/e2e/ 規格

テストシナリオとアサーション定義は `sensors/e2e/` 配下（L0 が定義）。詳細は `../../layer0-spec-architect/references/dev-env-spec.md` を参照。

### 前提

**第1層が完全 PASS してから発動する**。ビルドが通らない状態で E2E を回さない。

---

## 第3層 Interaction Cost 測定（目標解決率 10%）

**UX を計算可能な代理指標で測る**。創造的 UX 設計（DONT.md）ではなく、定量測定のみを扱う。

### 代理指標

| 指標 | 計測方法 | 閾値例 |
|---|---|---|
| クリック数 | Playwright で主要タスクまでのクリックカウント | 3-5 回以内 |
| 遷移深度 | ルート到達までのページ数 | 3 ページ以内 |
| 完了率 | シナリオの最終ステップ到達率 | ≥ 95% |
| エラー率 | シナリオ実行中のエラー発生率 | ≤ 5% |
| 応答時間 | 主要操作のレイテンシ p95 | ≤ 30 秒 |

### UX 3問プロトコルとの接続

L0 が SPEC.md で Must 閾値（UX 3問 Q1）を定義する。L1 はこれを sensors/interaction-cost/ 経由で測定する。閾値未達成は第2層 E2E の失敗として扱う。

### sensors/interaction-cost/ 規格

`sensors/interaction-cost/` 配下に閾値定義と測定スクリプトを配置（L0 が定義）。

### 境界

本層は **計算可能な代理指標** に閉じる。定性的な「使いやすさ」は第5層で人間が判断する。

---

## 第4層 推論的センサー（目標解決率 7%）

**LLM が仕様合致を確率的に判定する**。

### 手段

- SPEC.md と実装の照合（「仕様に合う・動く・使える」の3条件）
- DONT.md 領域への逸脱検出
- エッジケース列挙と実装との突合

### 実行条件

**第0〜3層が全て完遂してから発動する**。計算的に解ける問題を推論で解かない（情報損失と誤検出のコストが高い）。

### 自己検証 vs 独立検証

- **M1**: L1 自身が自己検証で兼用（軽量運用）
- **M2 以上**: L1 自己検証 + layer1-independent-reviewer の両方（独立コンテキスト隔離）
- **L2**: 上記 + layer2-integration-verifier による跨ぎドメイン検証

### 参照

- `../../layer1-independent-reviewer/SKILL.md`
- `../../layer2-integration-verifier/SKILL.md`

---

## 第5層 Vision / 人間判断（目標解決率 3%）

**機械も推論も捕らえ切れない問題の最後の砦**。

### 手段

- Vision モデルによるスクリーンショット判定（ブランドトーン・視覚整合性）
- 人間レビュー（L0 対話ループに差し戻し）
- C1 判断献上（permission-delegation.md の5カテゴリ）

### 使いどころ

- 創造的UX判定（DONT.md 領域）
- ブランドトーン・感情的印象
- 倫理・コンプライアンス最終判断
- 破壊的変更の承認

### 境界

本層は**稀にしか使わない**。3%を超えて発動する場合、第0〜4層の再設計を検討する。

---

## 層間の責務境界

### 前提条件の厳守

各層は**前の層が完遂してから発動する**。逆走は禁止。

```
第0層（設計） → 第1層（計算的） → 第2層（E2E） → 第3層（UX計量） → 第4層（推論） → 第5層（人間）
```

### Console エラー根絶原則

第1層でビルド・型・リンタ・テストが全 PASS してから第2層に進む。Console エラーを残したまま E2E を回すと：
- エラーの原因が第1層か第2層か区別できない
- 推論センサーの検出精度が落ちる
- 人間レビュー時にノイズが増える

### 計算的解決最優先

推論で解ける問題は計算的に解けない問題に限る。計算的に解けるのに推論で解くのは後戻り。

---

## L1 自己検証フローへの埋め込み

`../SKILL.md` のステップ5（タスク実行）とステップ6（自己検証）の間に、本スタックに沿った検証を挿入する。

### 埋め込み手順（ステップ5.5）

```
5.5.1. 第0層確認: spec/ 配下を逸脱していないか（書き換え禁止）
5.5.2. 第1層実行: sensors/computational.md の全項目 PASS
       → FAIL: 自力修正（最大3回）→ 依然 FAIL なら未解決事項として献上
5.5.3. 第1層 PASS 後、第2層実行: sensors/e2e/ シナリオ全 PASS
       → FAIL: 自力修正（最大3回）→ 依然 FAIL なら未解決事項として献上
5.5.4. 第2層 PASS 後、第3層実行: sensors/interaction-cost/ 閾値達成確認
       → 閾値未達成は FAIL 扱い
5.5.5. 第3層 PASS 後、既存ステップ6（sensors/inferential.md）へ進む
```

### 既存ステップとの関係

- 既存ステップ番号は変更しない（後方互換維持）
- 5.5 として挿入する形で追加のみ
- sensors/computational.md / sensors/inferential.md は既存のまま、新設は sensors/e2e/ と sensors/interaction-cost/

### センサー未整備時の挙動

プロジェクトに sensors/e2e/ または sensors/interaction-cost/ が存在しない場合：
- M1: スキップ可（軽量運用）
- M2 以上: DELIVERY.md に「センサー未整備」として記録し、L0 に改善提案（タイプC献上）として戻す

---

## 解決率の根拠と運用

目標解決率（30/30/20/10/7/3）は設計目安。プロジェクトごとに事後評価で測定し、蓄積する。

### 事後評価

DELIVERY.md の体制事後評価に、各層でのエラー検出件数を記録する（該当時のみ）：
- 第0層で発生防止できた件数（実装中に型エラーで弾かれた等）
- 第1〜3層で機械検出された件数
- 第4層で推論検出された件数
- 第5層で人間が検出した件数

比率が目標から大きくズレる場合、L0 が sensors 定義を見直す。

### AI 能力バージョンとの連動

第0層の解決率は AI 能力に依存する（型推論・状態機械設計の精度）。REGIME.md の AI 能力バージョン記録を基準点として、将来モデルでの比率調整を行う。
