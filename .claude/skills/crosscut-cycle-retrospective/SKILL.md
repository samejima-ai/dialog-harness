---
name: crosscut-cycle-retrospective
dimension: D4
description: >
  1 開発サイクル（cycle / LC ループ）の**完了時**に、その cycle の開発・実行結果を
  構造化して振り返り、次サイクルへの改善提案を出し、`history/SUMMARY.md` への反映まで
  導く事後評価スキル。既存 L1 体制事後評価（`layer1-autonomous-dev` の DELIVERY.md
  §体制妥当性の自己評価＝M1/M2/L2 モード判定の妥当性）を、**実行プロセスの学び**
  （何がうまくいったか / 何を反省するか / どこで詰まったか / 残作業 / 改善提案）まで
  拡張し、独立起動可能にしたもの。
  「今回の開発を振り返って」「cycle を振り返りたい」「今のサイクルの反省」「実行結果を
  評価して改善点を出して」「出荷後の振り返り」「retrospective」「ふりかえり」「次に活かす
  ため今回を整理して」「マージできたので振り返り」等の発話で本 skill の起動を必ず検討する。
  **自動化度**: SUMMARY 反映（追記 + 代謝＝可逆・revert 可）までは自動。SPEC / DONT /
  CLAUDE / 罠カタログ等の**規範変更は提案のみ**（人間最終承認、philosophy 第 6 条）。
  **混同回避**: F1 振り返り儀式（`layer0-spec-architect`／`ritual-protocol.md`）は
  cycle **開始時の事前**照合（過去文脈⇔現欲求）ゆえ別局面 — 「振り返り儀式」語での起動は
  引き続き spec-architect にルーティングする。情報代謝（`layer0-reindex-librarian`）は
  history 蓄積の叡智結晶化＋購読量削減が対象で本 skill の下流。continuous-learning は
  hook 観測ログ起点で本 skill とは起点が別（本 skill は単一 cycle の実行結果起点）。
  本 skill の改善提案は continuous-learning／feedback-loop の候補と同じく人間承認に閉じる。
---

# crosscut-cycle-retrospective — 1 cycle の実行結果を振り返り、次へ改善する

DH の既存「振り返り」機構は 3 つあるが、いずれも**単一 cycle の生々しい実行結果の
事後振り返り**を専任していない（下表）。本 skill はその隙間を埋める。

| 既存機構 | 局面 | 対象 |
|---|---|---|
| F1 振り返り儀式（spec-architect） | cycle **開始時（事前）** | 過去文脈 ⇔ 現欲求の照合 |
| 情報代謝（reindex-librarian） | cycle 境界 | history 蓄積 → 叡智結晶化 + 購読量削減 |
| continuous-learning | 随時 | hook 観測ログ → 繰り返しパターンの学習候補 |
| **本 skill** | cycle **完了時（事後）** | **その cycle の開発・実行結果 → 学び + 改善提案** |

既存 L1 体制事後評価（`layer1-autonomous-dev/references/delivery-format.md`
§体制妥当性の自己評価）は「M1/M2/L2 モード判定が過剰/妥当/過少だったか」しか
振り返らない。本 skill はそれを内包しつつ、**実行プロセスの学び**まで対象を広げる。

## 設計原則

### 1. 事後・検証後に回す（開発中に回さない）

情報代謝と同じ「組織の睡眠フェーズ」哲学。cycle の献上・マージ・検証が済んだ後に
回す。開発の只中で自己評価を挟むと、実装の熱に評価が引きずられて純度が落ちる
（検証後評価原則）。**起動タイミング = 出荷 / マージ / 検証完了の直後、次 cycle の
F1 より前**。

### 2. 自動化の境界（可逆は自動・規範は提案）

第 6 条「人間最終承認」を守るための線引き。判定軸は**可逆性**（DH v6 委譲モデル）:

- **自動反映（L-FULL 相当）**: `history/SUMMARY.md` への振り返りエントリ追記 + 代謝
  （最古 bullet の COLD 送り）。PR diff で可視化され revert 可能ゆえ自律記述してよい。
- **提案のみ（人間承認）**: SPEC / DONT / CLAUDE / 罠カタログ / RL / センサー等の
  **規範変更**。これらは「何を禁じるか / どう作るか」の線引きゆえ、振り返りで気づいた
  改善は**提案として提示**し、採否は人間（または次 cycle の spec-architect）が決める。
  continuous-learning / feedback-loop が「候補出力のみ」で人間承認に閉じるのと同型。

判断が曖昧なときは重大側（人間承認）へ倒す（fail-safe）。

### 3. 事実と評価を分離（一次情報絶対主義）

振り返りの「事実」（実装したもの / 検証結果 / 詰まった箇所）は、その cycle の一次情報
（PR / DELIVERY.md / 検証ログ / COUNCIL-LOG / git 履歴）から機械的に拾う。「評価・
改善提案」（過剰だった / こうすべきだった）はそこから導出する。事実を捏造した評価は
出さない。詰まりの記録は「うまくいった」で薄めない（都合の良い自己評価を避ける）。

### 4. 既存の体制事後評価を内包する（重複させない）

DELIVERY.md にモード妥当性評価が既に書かれているなら、それを**再実行せず引用**し、
本 skill の振り返りに統合する。空なら本 skill が体制妥当性も含めて評価する。二重に
別々の結論を出さない（SSOT）。

## 処理フロー

```
[入力] 完了した cycle（PR / DELIVERY.md / 検証結果 / COUNCIL-LOG / git 履歴）
  ↓
[Phase R1] 事実収集 — その cycle の一次情報から機械的に拾う
  ↓
[Phase R2] 構造化振り返り — 5 観点で評価（下記テンプレート）
  ↓
[Phase R3] 改善提案の仕分け — 可逆（自動反映）/ 規範（提案のみ）に分類
  ↓
[Phase R4] SUMMARY 反映（自動） + 規範提案の提示（人間承認待ち）
  ↓
[出力] 振り返りサマリ（対話 + SUMMARY エントリ）+ 規範提案リスト
```

各 Phase の詳細手順・チェックリスト・SUMMARY 代謝の作法は
[references/retrospective-protocol.md](references/retrospective-protocol.md) を読む。

## 振り返りテンプレート（R2、5 観点）

ALWAYS この 5 観点で構造化する（過不足なく・都合よく薄めない）:

```markdown
## cycle <ID> 振り返り

### 1. 成果（事実）
<何を作った / 出荷したか。PR 番号・主要ファイル・検証結果を一次情報から>

### 2. うまくいったこと
<機能した規律・判断・順序。なぜ効いたかまで（次も再現するため）>

### 3. 反省・詰まり
<バグ・手戻り・摩擦・誤認。都合よく薄めない。なぜ起きたか>

### 4. 体制妥当性（既存 L1 事後評価を内包）
<M1/M2/L2 判定 = 過剰/妥当/過少。Council 発動の要否は妥当だったか>

### 5. 改善提案（R3 で仕分け）
- [自動反映] <SUMMARY に残す学び>
- [提案のみ] <SPEC/CLAUDE/罠 等の規範変更提案（採否は人間）>

### 残作業（P3 / 別 cycle）
<次に持ち越すもの。少数意見・保留も保持>
```

## 起動条件

- cycle（LC ループ）の**献上 / マージ / 検証が完了した直後**、次 cycle の F1 より前
- 「振り返って」「retrospective」「今回を整理」「反省」等の事後評価系の発話
- L1 autonomous-dev の献上フロー末尾から自動起動してもよい（DELIVERY.md の体制
  事後評価を書く箇所を本 skill の R2/R4 で拡張する形）

### 起動しない場面

- cycle 開始時の過去照合（→ F1 振り返り儀式 / spec-architect）
- history 全体の代謝・叡智結晶化（→ reindex-librarian）
- hook 観測ログからのパターン学習（→ continuous-learning）
- 実装の只中（検証前。設計原則 1 = 検証後に回す）

## 関連 skill

- `layer1-autonomous-dev`（`references/delivery-format.md` §体制妥当性の自己評価）
  — 本 skill が内包・拡張する既存の事後評価
- `layer0-spec-architect`（`references/ritual-protocol.md`）— F1 振り返り儀式（事前・別局面）
- `layer0-reindex-librarian` — 情報代謝（本 skill の SUMMARY 追記の下流で history を代謝）
- `crosscut-continuous-learning` / `crosscut-feedback-loop` — 改善候補の人間承認モデルを共有
- `crosscut-council` — 規範変更提案が拮抗・不可逆なときの合議

## バージョン

- v0.1.0（新設）— cycle 完了時の構造化振り返り + SUMMARY 自動反映 + 規範提案（提案のみ）
