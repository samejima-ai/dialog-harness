# Handoff to Evaluator (L1 Evaluator 連携 I/O 規約)

archeo-architect が生成する `refactor-intent-map.md` を Layer 1 (autonomous-dev / independent-reviewer) の評価軸に統合するための I/O 規約。

**ステータス**: Phase α では先行宣言版（仕様の事前公開）。**Phase γ で本実装**される。

---

## ロードマップ

| Phase | スコープ | 本ファイルのバージョン |
|---|---|---|
| **α** (本リリース) | archeo-architect SK 雛形のみ。L1 改修なし。`refactor-intent-map.md` は人間が手動参照してリファクタ指示を組み立てる | **先行宣言版**（本ファイル） |
| β | ritual-protocol レベル 3 統合・glossary 用語追加 | 変更なし |
| γ | L1 自己検証/独立検証に「意図合致軸」追加。`refactor-intent-map.md` を評価軸として自動参照 | **完全版に拡充**（+50〜80 行） |
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

## I/O 契約（先行宣言）

### 入力（archeo → L1）

L1 が読み込む対象：

```
delivery/refactor-intent-map.md  # archeo の最新成果物
```

複数バージョンが存在する場合（`refactor-intent-map-YYYY-MM-DD.md`）は、`Meta.delivered_at` が最新の 1 ファイルのみ参照する。

### L1 側の参照ロジック（Phase γ で本実装）

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

L1 が `delivery/DELIVERY.md` に追記するセクション（Phase γ で正式化）：

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

## 改修対象ファイル（Phase γ で実施、本リリースでは未着手）

Phase γ で改修する L1 側ファイル（**本リリースでは触らない**、先行宣言のみ）：

| パス | 修正内容 | 行数感 |
|---|---|---|
| `../../layer1-autonomous-dev/references/inferential-sensor-v2.md` | 第 4 層推論センサーに「意図合致軸」追加。`refactor-intent-map.md` 存在時のみ起動する条件分岐 | 10〜15 行 |
| `../../layer1-autonomous-dev/SKILL.md` §6 自己検証 | 推論的センサー実行時、Islands.refactor_directive を評価軸として参照する 1 行追加 | 3〜5 行 |
| `../../layer1-independent-reviewer/SKILL.md` | 独立検証時に同 map を参照、「意図保存軸」の独立判定を追加 | 5〜10 行 |
| 本ファイル | I/O 規約を先行宣言版から完全版に拡充 | +50〜80 行 |

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
