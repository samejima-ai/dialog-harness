# Archeo 対話フロー

archeo-architect の 7 ステップで使う対話文型と分離規約。
**Step 3（横方向）と Step 7（縦方向）は物理的に節を分離**して記述する。両者の混同はフロー崩壊。

---

## 設計原則

- **対話コスト最小化**: 仮説提示は AI 主導、人間は「合っている / 違う / 忘れた / 意図なし」の 4 択で応答
- **自律駆動を止めない（philosophy.md §4）**: 1 セッション 5 問以上は警告。AI 質問の累計が閾値超過したら、既出仮説の確度を下げて当該 Island を `forgotten` で確定する
- **曖昧応答は重要度低と解釈**: 2 回連続曖昧応答で当該 Island を `forgotten` に格下げ（spec-architect の E1 対応と同方針）
- **判断疲労を避ける**: 1 回の応答で 5 島以上の仮説を一括提示しない。3 島ずつバッチ提示

---

## Step 1: 構造走査（AI 主導、対話なし）

人間への発話なし。AI が以下を実行：

1. 対象コードベース全体を走査
2. ファイル単位 / ディレクトリ単位で「島」候補を仮列挙
3. 各島について S/U/R 推定値と仮説生成ヒント（`intent-hypothesis-protocol.md` 参照）を内部記録

**人間への提示**: 走査完了通知のみ。「N 個の島候補を検出しました。各島の意図仮説を順次提示します」。

---

## Step 2: 意図仮説提示（AI 主導、対話なし）

人間への発話は仮説の提示のみ。応答は Step 3 で受ける。

### 仮説提示文型

```
[Island-NNN] <島の名前（AI 命名）>
- paths: <ファイルパス>
- 仮説: <inferred_intent、自然言語 1-3 文>
- 確度: <code_check | git_log_check | ai_inference>
- 根拠: <仮説生成ヒント、例: コメントなし / git log 沈黙 / 命名一貫性低>
- S/U/R: <S=N, U=N, R=N>
```

### 禁則

- 確度メタデータなしで提示しない
- 「合っているはず」での自己確定をしない（人間応答を待つ）
- 1 応答で 5 島以上を一括提示しない（3 島ずつバッチ）

---

## Step 3: 認識合わせ（横方向）— **horizontal**

**Step 3 は横方向の擦り合わせループ**。仮説 ⇄ 人間 を擦り合わせる。

### 4 値応答の収集

各島について、人間に以下のいずれかを応答してもらう：

| 値 | 意味 | 人間の発話例 | AI の次アクション |
|---|---|---|---|
| `confirmed` | AI 仮説が合っている | 「合ってる」「その通り」「OK」 | Island を確定し次の島へ |
| `corrected` | 仮説は外れている、人間が修正 | 「違う、本当は X だった」 | `corrected_intent` フィールドに修正内容を記録 |
| `forgotten` | 思い出せない | 「忘れた」「覚えてない」「うろ覚え」 | Step 5 へ持ち越し（pending 状態） |
| `absent` | 当時から意図なし | 「特に考えてなかった」「意図なし」「混沌」 | `absent-intent-protocol.md` の確定条件参照 |

### 確認文型

```
Island-NNN について、私の仮説：「<inferred_intent>」
これは:
  (1) 合っている
  (2) 違う（本当は X）
  (3) 忘れた / 思い出せない
  (4) 当時から意図なし
のどれが近いですか？
```

### 自己制限規約（質問数の上限）

- **5 問ルール**: 1 セッションで AI 発話の質問数が累計 5 問を超えたら、警告フラグを立てる
- **5 問超過時の挙動**: 残りの島について確度を下げて `forgotten` で仮確定し、Step 5 で人間に一括判定を依頼する
- **目的**: philosophy.md §4「自律駆動を止めない、開発中の質問でトークン浪費しない」と整合

### 曖昧応答の処理

- 「たぶん」「どっちでもいい」「微妙」等が **2 回連続**したら、当該島を自動的に `forgotten` に格下げ
- 格下げ後は深掘りを停止し、Step 5 で人間が `corrected` または `absent` のいずれかで確定する

---

## Step 4: 境界曖昧領域の特定（AI 主導 + 人間裁定）

島と島の境界が曖昧な箇所を AI が検出し、人間に裁定を求める。

### 提示フォーマット（差分サマリのみ）

```
[Boundary-NNN] <該当箇所、例: src/auth/middleware.ts>
候補:
  (a) Island-001 (auth-register) に帰属
      根拠: <呼び出し関係 / 命名 / コミット履歴>
  (b) Island-003 (session-management) に帰属
      根拠: <同上>
  (c) 新島として切り出し: Island-NNN (auth-middleware)
      根拠: <同上>

どれにしますか？「両方に属する」「保留」も可。
```

### 人間応答パターン

- 候補のいずれか → `human_decision: Island-XXX` または `new_island`
- 「両方に属する」 → `human_decision: both`
- 「判断保留」 → `human_decision: undecided`（次回 archeo 起動時に再判定）

---

## Step 5: 忘却 or 想起の宣言（人間主導、AI は質問しない）

Step 3 で `forgotten` だった全島について、人間が以下のいずれかを明示宣言する。AI は**質問しない**（philosophy.md §4 整合）。

### 提示フォーマット

```
以下の N 個の島が forgotten で残っています：
- Island-002, Island-005, Island-007

各島について、以下のいずれかを宣言してください：
  (1) 想起した: 「Island-N は本当は X だった」
  (2) 新規決定: 「Island-N は忘れたが、新たに X と決める」
  (3) 意図不在: 「Island-N は当時から意図がなかった」
```

### 4 値の格上げ・確定

- (1) 想起 → `corrected_intent` を記録、`human_confirmation: corrected`
- (2) 新規決定 → `corrected_intent` を新規意図として記録、`human_confirmation: corrected`、`notes` に「新規決定（過去意図ではない）」と明記
- (3) 意図不在 → `human_confirmation: absent`、`notes` に人間明示宣言を引用記録（`absent-intent-protocol.md` 必須）

### 禁則

- AI 単独で `corrected` / `absent` を確定しない（捏造防止、P-Arch-2）
- 人間が応答しないまま Step 6 に進まない（受け入れ基準 2 違反）

---

## Step 6: 意図マップ確定（AI 主導、人間レビュー）

Phase β（生成）。`assets/refactor-intent-map-template.md` に従って `delivery/refactor-intent-map.md` を生成する。

### 提示フォーマット（差分サマリのみ、全文提示しない）

```
意図マップを生成しました。サマリ：
- 検出した島: N 個
- confirmed: N
- corrected: N（うち想起 N、新規決定 N）
- absent: N
- refactor_directive 分布:
    - preserve: N
    - restructure: N
    - discard_and_redesign: N
- 境界裁定: N / M 解決
- 意図不在領域: N

詳細は delivery/refactor-intent-map.md を参照。
```

### 人間が確認するポイント

- 4 値の内訳が想定通りか
- `refactor_directive` の AI 推奨に異論がないか
- 境界裁定のうち `undecided` が許容範囲か

---

## Step 7: 合意（縦方向）→ Layer 1 への譲渡 — **vertical**

**Step 7 は縦方向の譲渡合意**。意図マップ全体 ⇄ 人間 の単一判定。

Step 3（横方向の島単位擦り合わせ）と Step 7（縦方向のマップ全体判定）を**物理的に分離**する理由：

- Step 3 は **N 個の島について N 回の応答**を受ける（横方向の繰り返し）
- Step 7 は **マップ全体について 1 回の合意**を受ける（縦方向の単一判定）
- 両者を混同すると「島ごとの合意 = マップ譲渡完了」と誤認するリスクが生じ、Step 7 がスキップされる
- DH 哲学（philosophy.md §1 フラクタル / §3 情報純度）の根幹原則を守るため、節を分離する

### 提示フォーマット

```
意図マップ全体について、以下のいずれかで応答してください：
  (1) 合意: Layer 1 に譲渡してよい
  (2) 修正要求: Island-N の応答を訂正したい（Step 3 へ戻る）
  (3) 追加発見: 新たな島を発見した（Step 1 へ戻る、再走査）
```

### 人間応答後の挙動

- (1) 合意 → §7.4 自己検証 → PASS なら `delivery/refactor-intent-map.md` を最終確定し L1 譲渡経路へ
- (2) 修正要求 → 該当 Island の Step 3 へ戻る
- (3) 追加発見 → Step 1 へ戻る（再走査）

### 譲渡経路

Phase γ（L1 改修）が完了するまで（v5.x 帯では未着手）、人間が手動で `refactor-intent-map.md` を参照しながらリファクタ依頼を組み立てる。Phase γ 以降は L1 の自己検証/独立検証が `refactor_directive` を評価軸として自動参照する（`handoff-to-evaluator.md` 参照）。

---

## 失敗の兆候（自己観測項目）

本フローが形骸化していないかの観測項目：

| 兆候 | 解釈 | 検出方法 |
|---|---|---|
| 1 セッション 5 問超過 | 自律駆動違反（philosophy.md §4） | 質問カウンタ |
| 「合っているはず」の自己確定 | P-Arch-2 違反（捏造の疑い） | `intent-hypothesis-protocol.md` の確度メタデータ未記入で検出 |
| Step 7 スキップで Layer 1 譲渡 | 譲渡構造崩壊（P-Arch-3 違反） | `refactor-intent-map.md` Meta セクションの `delivered_at` 不在で検出 |
| spec-architect と同時起動 | 対話方向の混線（責務分担表違反） | 上位の責務分担表（spec-architect SKILL.md §L0 スキル間の責務分担）で排他保証 |
| 4 値の偏り（confirmed 100%） | 形骸化の疑い（人間が雑に追認） | Summary セクションの分布で検出、L1 体制事後評価で記録 |

これらは F1 振り返り儀式と同形式で監査する（ritual-protocol.md §形骸化防止メカニズム整合）。
