# Handoff to Evaluator (L1 Evaluator 連携 I/O 規約)

archeo-architect が生成する `refactor-intent-map.md` を Layer 1 (autonomous-dev / independent-reviewer) の評価軸に統合するための I/O 規約。

**ステータス**: **Phase γ コア 3 件 + 先行宣言 4 本実装版**（v5.5.0 でコア 3 件、v5.5.1 patch で先行宣言 4 を正式化。先行宣言 5 は v5.5.x patch / v5.6.0 へ温存）。

---

## ロードマップ

| Phase | スコープ | 本ファイルのバージョン |
|---|---|---|
| α (v5.4.0) | archeo-architect SK 雛形のみ。L1 改修なし。`refactor-intent-map.md` は人間が手動参照してリファクタ指示を組み立てる | 先行宣言版 |
| β | ritual-protocol レベル 3 統合・glossary 用語追加 | 変更なし |
| γ コア 3 件 (v5.5.0) | L1 自己検証/独立検証に「意図合致軸」追加（先行宣言 1/2/3 を本実装）。`refactor-intent-map.md` を評価軸として自動参照 | 完全版（コア 3 件） |
| **γ 残 2 件のうち 先行宣言 4 (v5.5.1 patch、本リリース)** | **ストラングラー・フィグ / Branch by Abstraction の射程外を正式宣言。「援用」と「全体採用」の境界線を明文化し、L1/L2 への禁止規約と v6.0.0 昇格の観測トリガーを追加** | **拡張版（コア 3 件 + 先行宣言 4 本実装）** ← 本ファイル |
| γ 残 1 件 (v5.5.x or v5.6.0) | 先行宣言 5（失敗アンチパターン早期検出）の本実装 | 拡張 |
| δ | spec-architect への逆輸入（運用データ 3 ヶ月後） | 変更なし or 拡張 |

---

## 起点問題と解決の構造

L1 (`layer1-autonomous-dev`) の自己検証/独立検証は現状以下の 3 軸で評価する（`SKILL.md §6` / `references/inferential-sensor-v2.md` 第 4 層）：

- 仕様に合う
- 動く
- 使える

**問題**: 「人間の元々の意図に合う」軸が不在。リファクタ依頼で「動くが意図と違う」結果になる構造的原因。10 個の修正点を依頼して 3〜4 個取りこぼす起点問題はここに由来する。

**解決**: archeo の `refactor-intent-map.md` を L1 の **第 4 軸**として注入する。

```
[現状] L1 評価軸 = (仕様適合 ∩ 動作 ∩ ユーザビリティ)
[Phase γ] L1 評価軸 = (仕様適合 ∩ 動作 ∩ ユーザビリティ ∩ 意図合致)
```

意図合致軸は `refactor-intent-map.md` 不在時には起動しない（後方互換完全維持）。

---

## I/O 契約（v5.5.0 で本実装、コア 3 件）

### 入力（archeo → L1）

L1 が読み込む対象：

```
delivery/refactor-intent-map.md  # canonical filename（最新版を常にここに置く）
```

**ファイル名規約**:

- canonical filename は `delivery/refactor-intent-map.md` に固定する
- archeo を複数回起動して新版を生成する場合: 旧版を `delivery/archive/refactor-intent-map-YYYY-MM-DD.md` にアーカイブ移動し、canonical 位置（`delivery/refactor-intent-map.md`）を新版で上書きする
- L1 は `delivery/archive/` を参照しない（canonical のみ参照、選択ロジック不要）

これにより L1 側の選択アルゴリズムが不要となり、`exists("delivery/refactor-intent-map.md")` の単純チェックで済む。アーカイブは人間レビュー用の履歴であり L1 評価軸には影響しない。

### L1 側の参照ロジック（v5.5.0 で本実装、コア 3 件）

`refactor-intent-map.md` の存在チェック：

```
if exists("delivery/refactor-intent-map.md") and Meta.self_verification == "passed":
    activate_intent_evaluation_axis(map)
else:
    skip_intent_axis()  # 従来 3 軸動作（後方互換）
```

各 Island の `refactor_directive` を評価軸として参照：

| `refactor_directive` | L1 評価時の挙動 |
|---|---|
| `preserve` | 該当 paths のコード変更を**禁止**（`assertion: no_modification`）。検出時は FAIL |
| `restructure` | 該当 paths のリファクタを**許可**。ただし `inferred_intent` または `corrected_intent` の保持を必須条件とする |
| `discard_and_redesign` | 該当 paths の新規設計を**許可**。意図保存制約は解除（`AbsentZone` 由来） |

`Boundaries` の `human_decision` も参照：

- `Island-XXX` 単独帰属 → 当該 Island の `refactor_directive` に従う
- `both` → 両 Island の制約を AND で適用（より厳しい方を採用）
- `new_island` → 新島の `refactor_directive` に従う
- `undecided` → 当該境界に触れる変更を**保留**（人間判定要請）

### 出力（L1 → DELIVERY.md）

L1 が `delivery/DELIVERY.md` に追記するセクション（v5.5.0 で本実装）：

```markdown
## 意図合致検証（archeo-architect 由来、Phase γ で追加）

参照した意図マップ: delivery/refactor-intent-map.md (delivered_at: <timestamp>)

| Island | refactor_directive | 実装結果 | 判定 |
|---|---|---|---|
| Island-001 | preserve | 変更なし | PASS |
| Island-002 | restructure | 再構造化（意図保持） | PASS |
| Island-003 | discard_and_redesign | 新規設計 | PASS |
| ... | ... | ... | ... |

意図逸脱検出: 0 件 / N 件
```

意図逸脱検出があった場合は `failure: intent_drift` として L1 自力修正を試行する。修正不能なら Type C 献上（仕様改訂提案）または Type D 献上（技術例外）に分類する。

---

## 改修対象ファイル（v5.5.0 で実施済み、コア 3 件）

v5.5.0 で改修した L1 側ファイル（先行宣言 1/2/3 を本実装）：

| パス | 修正内容 | 状態 |
|---|---|---|
| `../../layer1-autonomous-dev/references/inferential-sensor-v2.md` | 第 4 層推論センサーに「意図合致軸」追加。`refactor-intent-map.md` 存在時のみ起動する条件分岐 | ✅ v5.5.0 実施 |
| `../../layer1-autonomous-dev/SKILL.md` §6 自己検証 | 承認テスト生成ステップ + 自動照合ループステップ追加（refactor_directive: preserve / restructure 領域） | ✅ v5.5.0 実施 |
| `../../layer1-independent-reviewer/SKILL.md` | 評価軸を 3 軸 → 4 軸（仕様適合 ∩ 動作 ∩ ユーザビリティ ∩ 意図合致）に拡張 | ✅ v5.5.0 実施 |
| `../../layer1-autonomous-dev/references/delivery-format.md` | DELIVERY.md 構造に「意図合致検証」セクション追加 | ✅ v5.5.0 実施 |
| 本ファイル | 先行宣言版 → コア 3 件本実装版へ拡充 | ✅ v5.5.0 実施 |

---

## Phase γ 詳細仕様（業界知見統合）

業界根拠: Council 諮問 `council-2026-05-01T10:30:00Z-archeo01` の agreed_recommended（哲学者の第 4 の道採用、Phase γ 伏線追加）。AI を活用したレガシーコード・リファクタリング業界知見（フェザーズ「レガシー = テストなし」/ ファウラー「外部振る舞い不変」/ VB6 事例の自動照合ループ）と archeo 哲学（P-Arch-1 忘却の制度化）の関係性を本ファイルで明文化する。

**実装ステータス（v5.5.1 時点）**: コア 3 件（先行宣言 1/2/3）を v5.5.0 で本実装、先行宣言 4 を v5.5.1 patch で本実装。残 1 件（先行宣言 5）は v5.5.x patch / v5.6.0 へ温存。

### 先行宣言 1: 承認テスト生成プロトコル（refactor_directive: preserve 領域）

**業界根拠**: フェザーズ「レガシーコードとはテストのないコードである」/ Approval Testing カノン / Qodo 等のテスト生成ツール群。

**archeo 哲学との接続**: P-Arch-1（忘却の制度化）と P-Arch-3（譲渡構造維持）の系。承認テスト = 「振る舞いの記憶を外部化する」（archeo マップ = 「意図の記憶を外部化する」と同根）。

**Phase γ で本実装する仕様**:

`refactor_directive: preserve` の Island は、L1 が変更する前に**承認テストで現状を凍結**する。プロトコル：

1. L1 は preserve Island の paths について、現状のコードを実行して入出力を **基準データ** として記録（`delivery/approval-tests/<island-id>.baseline.json`）
2. リファクタ後のコードを同入力で実行し、出力差分を機械的に検証
3. 差分検出時は L1 自力修正を試行、修正不能なら **意図逸脱 (intent_drift)** として Type C 献上
4. 既存テストがある領域では既存テストを優先し、不足分のみ承認テストで補完

**ツール統合は射程外**: Qodo / Byteable 等のツール選択は L1 実装者の裁量。プロトコルのみ規定する。

**本実装時の改修対象**:
- `../../layer1-autonomous-dev/SKILL.md` §6 に承認テスト生成ステップ追加
- `delivery/approval-tests/` ディレクトリの配置規則を `dev-env-spec.md` に追加

### 先行宣言 2: 自動照合ループ（refactor_directive: restructure 領域）

**業界根拠**: VB6 価格エンジン移行事例（14 ヶ月で 8,064 回の自動照合ラン、1,240 万件のイベント比較で 0.007% の不一致検出、420 万ドルの見積もり不整合を未然防止） / ストラングラー・フィグパターン。

**archeo 哲学との接続**: P-Arch-3（譲渡構造維持）の系。意図保持の **物理的検証**メカニズム。

**Phase γ で本実装する仕様**:

`refactor_directive: restructure` の Island は、L1 が**新旧並行実行 + 結果照合**で意図保持を機械的に検証する。プロトコル：

1. リファクタ前の実装を「旧」、後の実装を「新」として両方を残す（Branch by Abstraction パターン）
2. 抽象化レイヤー越しに同入力を両者に流し、結果を比較
3. 不一致率の閾値（デフォルト 0.01%）を超えたら **意図逸脱** として Type C 献上
4. 並行実行期間（L1 実装者裁量、典型は 1〜2 週間）後、新実装に切替

**L2 統合検証との接続**: 複数 Island に渡る restructure では `layer2-integration-verifier` が照合結果を集約する（L2 発動時のみ）。

**本実装時の改修対象**:
- `../../layer1-autonomous-dev/SKILL.md` §6 に自動照合ループステップ追加
- `../../layer2-integration-verifier/SKILL.md` に集約プロトコル追加（L2 のみ）
- `delivery/reconciliation-logs/` ディレクトリの配置規則追加

### 先行宣言 3: 意図合致軸の L1 評価軸統合（**起点問題の構造解決**）

**業界根拠**: ファウラー「外部から見た振る舞いを保ったまま、内部構造を理解しやすく、修正が容易なものへと改善する」 / Code Smells カノン（intent-hypothesis-protocol.md §Code Smells カノンとの対応 と整合）。

**archeo 哲学との接続**: 起点問題（取りこぼし 3〜4 個）の構造解決。L1 評価軸 3 軸（仕様適合・動作・ユーザビリティ）に「**意図合致軸**」を第 4 軸として注入する。

**Phase γ で本実装する仕様**:

`../../layer1-autonomous-dev/references/inferential-sensor-v2.md` 第 4 層推論センサーに以下を追加：

```
[現状] L1 評価軸 = (仕様適合 ∩ 動作 ∩ ユーザビリティ)
[Phase γ] L1 評価軸 = (仕様適合 ∩ 動作 ∩ ユーザビリティ ∩ 意図合致)

意図合致 = 全 Island の refactor_directive に従う実装結果である
  preserve: 承認テスト全件 PASS（先行宣言 1）
  restructure: 不一致率 < 閾値（先行宣言 2）
  discard_and_redesign: AbsentZone.redesign_directive に従う
```

`refactor-intent-map.md` 不在のプロジェクトでは意図合致軸は起動しない（後方互換完全維持）。

### 先行宣言 4: ストラングラー・フィグ / Branch by Abstraction の射程外宣言（v5.5.1 で本実装）

業界知見の **ストラングラー・フィグパターン**（Strangler Fig）と **Branch by Abstraction パターン**（BBA）は archeo の射程外（リファクタ「実行戦略」レベル）であり、archeo の射程である「意図復元」レベル（L0）とは抽象階層が異なる。本宣言は v5.5.1 patch で正式化される（先行宣言版から本実装版へ昇格）。

#### (a) 射程外要素の明示列挙

以下の要素は **archeo / Phase γ いずれの責務にも含まれない**。これらの設計・採用が必要な場合は、別 SK / 別 minor で別途設計する：

| パターン | 射程外サブ要素 |
|---|---|
| ストラングラー・フィグ | (i) ルーティング層の設計 / (ii) ファサード経由の **トラフィック比率制御**（0%→10%→50%→100% 等の段階的シフト）/ (iii) 旧実装の体系的 decommissioning 計画 / (iv) フォールバック戦略 / (v) カナリアリリース併用 |
| Branch by Abstraction | (i) 抽象化レイヤーのインターフェース設計（の体系化）/ (ii) feature flag 経由のトラフィック比率制御 / (iii) 切替後の旧実装 cleanup の体系化 |

**用語注**: 「段階的切替」は本宣言において **トラフィック比率を段階的にシフトする** こと（0%→10%→50%→100% / カナリア展開 / 部分ユーザー先行展開等）を指す。先行宣言 2 §第 4 項の「並行実行期間後の cutover」（並列実行を経て**ある時点で 100% を一度に切替**）は段階的切替には該当しない（後述 (b) の「採用しているもの」に分類）。

#### (b) 「援用」と「全体採用」の境界線

先行宣言 2（自動照合ループ）は VB6 価格エンジン移行事例（ストラングラー類似）と Branch by Abstraction に **言及するが、それは部分概念の援用であり全体パターンの採用ではない**。境界を以下に厳密化する：

| 文脈 | 採用しているもの | 採用していないもの |
|---|---|---|
| 自動照合ループ（先行宣言 2） | (i)「新旧実装の並行実行 + 結果比較で意図保持を機械的に検証」という照合メカニズム / (ii) 並行実行期間後の **一度の cutover**（先行宣言 2 §第 4 項） | ルーティング層 / ファサード / トラフィック比率の段階的シフト（カナリア / 部分ユーザー先行）/ 旧実装の体系的 decommissioning 計画 |
| Branch by Abstraction 言及（先行宣言 2 §第 1 項） | (i)「抽象化レイヤー越しに新旧両者へ同入力を流す」という概念的同型 / (ii) 並列実行→ある時点での cutover という単純切替 | feature flag によるトグル / トラフィック比率の段階的シフト / 切替後の旧実装 cleanup の体系化（個別 cleanup は L1 裁量、体系化は射程外） |

この区別を明文化することで、L1 実装者が「先行宣言 2 → ストラングラー / BBA 全パターン採用」と拡大解釈する誤りをガードする。同時に、先行宣言 2 §第 4 項の cutover が本宣言で **明示的に scope 内**であることを宣言する（Copilot review #39 line 217 で指摘された境界曖昧性を解消）。

#### (c) L1 / L2 への禁止規約

- **L1 (autonomous-dev) 禁止**: `refactor-intent-map.md` のみを判断材料とし、ストラングラー/BBA パターンの「実行責任」を archeo 由来情報から導出してはならない。例: 「Island-002 が restructure だから自動的に feature flag を導入する」「複数 Island に渡るから自動的にルーティング層を作る」等は禁止。
- **L2 (integration-verifier) 禁止**: restructure 領域の照合結果集約のみを行い、ストラングラー的な段階的切替の実行制御を発火させない。
- **共通**: これらのパターンを採用したいプロジェクトは、本宣言を理由に「採用してはならない」とされるわけではない。**archeo / Phase γ 由来の自動導出としては禁止**であり、別 SK / 別 PR / 別 minor で別途設計する経路を取ること。

#### (d) v6.0.0 昇格の観測トリガー

`wf-baseline-rationale.md` §3「観測駆動でのみ拡張」原則と整合する形で、本宣言の v6.0.0 昇格条件を明示する：

- **昇格トリガー**: ≥ 3 異なる利用者プロジェクトでストラングラー/BBA パターンの archeo 連動採用要請が観測された場合、v6.0.0 候補として `crosscut-council` に再諮問する
- **現状**: 観測ゼロ。仮説扱い、温存
- **再諮問時の論点**: (i) 採用要請の真因が「意図復元の不足」か「実行戦略の不在」か、(ii) 後者であれば archeo 拡張ではなく新規 SK 新設が適切ではないか

#### (e) 整合性ガード（schema priority）

本宣言（先行宣言 4）と先行宣言 2/3 の記述に矛盾がある場合は **本宣言が優先**する。ただし「並行実行期間後の cutover」（先行宣言 2 §第 4 項）は (b) で明示的に scope 内であり、本宣言と先行宣言 2 は cutover の扱いについて整合している（矛盾ではない）。

先行宣言 2 内の「Branch by Abstraction パターン」言及（本ファイル §先行宣言 2 §第 1 項）は本宣言 (b) の境界線で限定解釈される（並列実行 + cutover は採用、feature flag / トラフィック比率制御 / 体系的 cleanup は不採用）。先行宣言 2 を更新する際は本宣言 (a)/(b) との整合を確認すること。

### 先行宣言 5: 失敗アンチパターンの早期検出

業界ガイドの失敗アンチパターン（**UI 層からの着手 39% 失敗** / **セマンティック境界欠如 32% 失敗** / **DB 共有の罠** / **90 日の法則 92% 失敗**）に対する archeo の対応：

| アンチパターン | archeo の対応（Phase α 実装済み） | Phase γ で強化される対応 |
|---|---|---|
| UI 層からの着手 | 直接対応なし | refactor-intent-map.md の Summary に「推奨着手順序」フィールド追加 |
| セマンティック境界欠如 | Boundaries セクションで明示 | DDD Bounded Context との接続（`../../layer0-spec-architect/references/subphase-l02-domain.md` との連携、v6.0.0 候補） |
| DB 共有の罠 | 射程外 | 射程外（L1 実装パターン） |
| 90 日の法則 | Git ホットスポット上位 10% を初期対話対象に優先 | 射程外（プロジェクト管理） |

---

## 後方互換性

`refactor-intent-map.md` 不在のプロジェクトでは L1 §6/§7 が従来動作（3 軸評価）。Phase γ 改修は条件分岐で完全に隔離される。

archeo を一度も起動していないプロジェクトには一切の影響がない（philosophy.md §1 フラクタル原則の「最小骨で導入」原則と整合）。

---

## Phase α 段階での運用（人間手動運用）

Phase γ 未着手の現段階では、人間が `refactor-intent-map.md` を手動で参照してリファクタ依頼を組み立てる：

1. archeo を起動して `delivery/refactor-intent-map.md` を生成
2. 人間がマップを読み、Island ごとの `refactor_directive` を確認
3. 人間が L1 (autonomous-dev) に対して「Island-001 は preserve（触るな）、Island-002 は restructure（意図保持で再構造化）、...」と明示指示
4. L1 は通常の 3 軸評価で実装する

この運用は手間がかかるが、起点問題（取りこぼし 3〜4 個）が完全には解消されない。**Phase γ で構造解決される**。

Phase α 単独運用での取りこぼし削減効果は、人間がマップを参照する規律に依存する。L1 の評価軸に統合されないため、人間の指示の精度が直接効く。

---

## v6.0.0 候補（温存）

`refactor_directive` の値域拡張（`partial_restructure` / `merge` / `split` 等）は v6.0.0 候補として温存する。Phase α では 3 値（preserve / restructure / discard_and_redesign）のみ運用し、観測駆動で拡張可否を判定する（`wf-baseline-rationale.md` §3「観測駆動でのみ拡張」原則と整合）。

AI 組織応用（`refactor-intent-map.md` を AI エージェント間引き継ぎに活用）も v6.0.0 候補。テンプレートに「拡張余地」コメントのみ残す。
