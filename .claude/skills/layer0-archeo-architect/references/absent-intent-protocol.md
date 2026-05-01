# 意図不在プロトコル

`human_confirmation: absent` の確定条件と捏造防止規約。
本プロトコルは原則 P-Arch-2「意図なきコードの扱い」の物理的実装である。

---

## 設計原則

- **意図不在は欠陥ではない**: 既存コードに意図が存在しない場合がある。これは欠陥ではなく「**素直に記録すべき事実**」である
- **捏造禁止**: AI が状況証拠だけで「意図不在」を確定することは原則違反。**必ず人間の明示宣言を伴う**
- **新規設計への切り替え**: `absent` 確定領域は `discard_and_redesign` 推奨の典型ケース。新規設計に切り替える判断を人間に委ねる
- **過去作者の名誉**: 過去の作者（多くの場合は現在のひでさん自身）の名誉のために意図を捏造しない。「忘れた」「意図なし」と素直に記録することが、過去作者を尊重することになる

---

## `absent` 確定の条件

以下を**全て満たす場合のみ** `human_confirmation: absent` が確定する：

1. **AI 仮説の確度が ai_inference 以下**である（code_check / git_log_check で意図が確認できる場合は `confirmed` または `corrected` のいずれかに必ず分類する）
2. **人間の明示宣言**が存在する。発話例：
   - 「特に考えてなかった」
   - 「意図なし」
   - 「混沌、当時から方針なし」
   - 「思い出せないし、当時から意図がなかった」
3. 人間の明示宣言が `Island.notes` に**発話日時付きで引用記録**されている
4. `corrected_intent` フィールドが空欄または `N/A` である（`absent` と `corrected` は排他）

### 確定不可の典型ケース

以下のケースは `absent` 確定に**該当しない**：

| ケース | 正しい分類 | 理由 |
|---|---|---|
| 人間が「忘れた」とだけ発話 | `forgotten`（Step 5 で再判定） | 「忘れた」と「当時から意図なし」は別概念 |
| AI が「コメント不在 + git log 沈黙」を理由に確定したい | `forgotten` のまま Step 5 へ | 状況証拠だけでの確定は捏造の疑い |
| 人間応答なしで AI がデフォルト確定 | エラー（Step 7 で FAIL） | 人間明示宣言が必須 |
| 人間が「どっちでもいい」と発話 | `forgotten`（曖昧応答処理） | 「どうでもいい」は重要度低シグナル、意図不在とは別 |

---

## 物理的捏造防止メカニズム

`refactor-intent-map-template.md` のテンプレート構造で、AI 単独確定を**物理的に**阻止する。

### メカニズム1: 必須フィールドのバリデーション

`Island.human_confirmation` が `absent` の場合、以下が必須：

```yaml
human_confirmation: absent
notes: |
  ひでさん発話: 「特に考えてなかった、意図なし」 (2026-05-01T13:45:00Z)
```

`notes` に発話日時付きの引用がない `absent` Island は §7.4 自己検証で FAIL。

### メカニズム2: corrected_intent の排他制約

`Island.corrected_intent` が空欄でない場合、`human_confirmation` は `corrected` でなければならない（`absent` との同居禁止）。テンプレート構造で物理的に分離する。

### メカニズム3: 自己検証チェック項目

§7.4 自己検証の「捏造検査」項目で以下をチェック：

- `human_confirmation: absent` の Island に `notes` の人間発話引用があるか
- `human_confirmation: corrected` の Island に `corrected_intent` があるか
- `human_confirmation: confirmed` で `corrected_intent` が記入されていないか
- AI が単独で `corrected` / `absent` を書いた形跡がないか（`notes` の発話タイムスタンプが session 開始前ならフラグ）

---

## Absent-Intent Zones の集約

`human_confirmation: absent` で確定した Island は、`refactor-intent-map.md` の `Absent-Intent Zones` セクションに集約される。

### 集約ルール

1. **同一目的の Island の統合**: 隣接する島で同一目的の `absent` 領域は 1 つの AbsentZone に統合する（例: legacy-config-loader / legacy-deprecated-handler）
2. **scope_paths の網羅**: 該当 Island の `paths` を全て列挙する
3. **redesign_directive の付与**:
   - `required`: 新規設計が必須（リファクタの主目的）
   - `optional`: 新規設計を推奨するが優先度低
   - `deferred`: 当面凍結、将来の archeo 再起動時に再判定（DONT.md 移送候補）

### DONT.md への移送候補

`AbsentZone.redesign_directive: deferred` の領域は、`../layer0-spec-architect/SKILL.md §処理フロー` の DONT.md 生成プロセスで移送候補として扱う。具体的な移送経路は spec-architect の Step 3 ドキュメント化に委ねる（archeo は `notes` に「DONT.md 移送候補」と明記するのみ、自身では DONT.md を書かない）。

---

## 失敗の兆候

捏造の疑いが発生する兆候：

| 兆候 | 検出方法 |
|---|---|
| `absent` Island に `notes` の発話引用なし | テンプレート必須フィールド検査 |
| `absent` Island の AI 確度が `code_check` | 不整合（コード確認できているなら意図あり） |
| 1 セッションで `absent` 比率 > 30% | 形骸化の疑い、§7.4 で警告 |
| 同一 session で `absent` Island が一括追加 | バッチ捏造の疑い、tampering 検査でフラグ |

これらの兆候は §7.4 自己検証「捏造検査」項目で機械的に検出する。検出時は §7（譲渡）に進まず、Step 5 の人間明示宣言を再収集する。

---

## 哲学的根拠

P-Arch-2「意図なきコードの扱い」は philosophy.md §3「情報純度原則」と §4「人間責務原則」の二条併用：

- **§3 情報純度**: 意図不在を「意図不在」として正確に記録することで、後続 L1 への情報純度を保つ。捏造意図を渡せば情報損失が発生する
- **§4 人間責務**: 「意図不在の判定」は人間専管。AI が単独で意図不在を宣言することは責務逸脱

これらは philosophy.md の既存条文の応用であり、本プロトコルで新規条文を追加するものではない（D4 minor 改修の範囲内）。
