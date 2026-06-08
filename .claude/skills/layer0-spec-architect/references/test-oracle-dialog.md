# C5: テスト oracle 言語化プロトコル（v5.23.0 追加）

L0 対話で **人間の暗黙の関心（test oracle）を言語化**し、AI が書く E2E の「何を検証するか」宣言の
精度を上げるためのプロトコル。SKILL.md §2.6 から起動される。
哲学的背景は `philosophy.md` 第4条（人間=イメージ/意図/ニュアンス共有、AI=構造化）/ 第1条（認識ズレゼロ化ループ）。

---

## なぜ最重要か（DH 哲学の本丸）

E2E 構築の最重要原理（`../../layer1-autonomous-dev/references/e2e-best-practices.md` §2）：

> **AI は「見ると宣言したものしか見えない」**。AI の知覚の完成度は、AI 自身が書いた
> 「何を検証するか」の宣言の精度に**律速される**。

ゆえに：

> 人間の暗黙の関心（test oracle）を**言語化する**こと
> = AI の**知覚宣言を拡張する**こと
> = **AI の知覚野そのものを広げる**こと。

人間が「何を気にするか」を握っている限り、AI はそれを言語化して初めて検証できる。
C5 はその言語化の擦り合わせ対話そのもの。SPEC.md WHY 層・INTENT.md（WHY 現役正本）と地続き。

---

## 起動条件

- critical-priority journey を持つ **or** UI を持つプロジェクト
- 実行位置: SKILL.md §2.5（UX 3問）の直後
- 非対面（CLI / API サーバ / ライブラリ）かつ cosmetic のみ → **完全スキップ**（時間コストゼロ）

---

## 3問（UX 3問と同型）

| # | 問い（人間の感覚を引き出す） | 抽出する oracle | 格納先 → テストへの作用 |
|---|---|---|---|
| **TQ1 関心** | 「これが壊れてたら**絶対に世に出したくない**瞬間 / 画面は？」 | 失敗モードの oracle | SPEC critical journey + assert 優先順位（相 B 母集団＝C1） |
| **TQ2 目的** | 「これは**誰のどんな"成功"**のためにある？なぜ作る？」 | 成功の oracle | SPEC WHY 層 → Vision 判定 / Interaction Cost 合格基準の根拠 |
| **TQ3 暗黙前提** | 「**言わなくても当然そうあるべき**、と思ってる前提は？（例: 日本語が化けない / 二重送信されない / 深夜でも動く）」 | 暗黙要件の oracle | DONT.md + L0-6 invariants の Sad/Evil path 種 |

### TQ1-3 の本質

言語化された各項目が、そのまま **AI が書くテストの「何を見るか」宣言**になる。
oracle の解像度がテストの精度を律速する（`e2e-best-practices.md` §5 の精度対策の根本）。

---

## 自動補完（未回答 / 曖昧応答時）

曖昧応答（「どうだろう」「どっちでもいい」等）は `ritual-protocol.md` E1 / UX 3問と同じ扱い：

1. AI が INTENT.md・SPEC・DOMAIN-CONTEXT から最適解を推定して充当
2. 「〇〇と推定しました。違ったら次回教えてください」と**通知のみ**（再質問しない）
3. 対象項目に `確度: AI推定 (YYYY-MM-DD)` を付与し、SUMMARY.md「要再確認リスト」に追加
4. 曖昧応答 2 回連続なら深掘り停止（重要度低シグナル）

C5 は presentation でなく logic 層の対話であり、persona に依存しない。

---

## 格納先マッピング（まとめ）

```
TQ1 関心    → SPEC.md critical journey（相 B E2E 母集団 / C1）
TQ2 目的    → SPEC.md WHY 層 → sensors/interaction-cost/ 合格基準・Vision 判定基準
TQ3 暗黙前提 → DONT.md + spec/invariants.feature（L0-6・Sad/Evil）
```

- L0-6 サブフェーズ（`subphase-l06-invariants.md`）が起動するプロジェクトでは、TQ3 を Evil/Sad path の
  種として直接引き渡す。
- 耐久 E2E（相 B）の**カバレッジ対象は本 C5 で人間と大枠合意**する（AI 裁量に委ねない）。これが
  「AI テストスクリプトの精度」への L0 時点の対策の中核（C5）。
- **UI プロジェクトでは B-ID チェックリストを oracle の出発点に使う**: UI Baseline RL
  （`../../../../templates/rules/common/ui-baseline.rules.md`）の B-01〜B-25 は抽象的な「使える」を検証可能な
  宣言に落としたもの。TQ1（関心）/ TQ3（暗黙前提）の言語化を B-ID で具体化できる（接続は
  `design-system-spec.md`「UI 相互作用層」§B-ID は 5 層検出スタックの ready-made oracle）。

---

## §7.4 自己検証への寄与

C5 の出力（SPEC critical journey / WHY / invariants 種）は、L0 完了後に L1 が相 B E2E を
SPEC から導出するための一次入力。C5 を経たプロジェクトでは、相 B E2E の母集団が SPEC に
トレース可能であること（journey ↔ SPEC priority の対応）を broken-reference 検査と並んで確認する。
