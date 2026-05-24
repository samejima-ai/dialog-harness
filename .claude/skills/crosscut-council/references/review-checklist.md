# review-checklist — claude-review Phase 1-c プロトコル

claude-review.yml の OC（Orchestrator-Conductor）が Phase 1-c で本プロトコルに従い、PR ごとの
**検証チェックリストを動的生成**し、各項目を **RL 内 / RL 外** に分類する。Council 評価（Phase 3-b）が
何を見るかを PR の性質に合わせて確定する段階であり、評価そのものではない。

本ファイルは crosscut-council の reference であり、Council 規格（[output-format.md](output-format.md) /
[council-weights.md](../council-weights.md) / [pre-check.md](pre-check.md) /
[judgment-agent.md](judgment-agent.md) / [orchestrator.md](orchestrator.md)）と
[philosophy.md](../../layer0-spec-architect/references/philosophy.md) を一次情報源とする。

## 入力

- review-fetch の bundle（title/body/diff/changed_files/linked_issues）
- review-difficulty の tier 判定（difficulty tier 1/2/3, touched_sensitive）

## チェックリスト動的生成

汎用コードレビュー軸（claude-review の担当）の観点から、この PR で検証すべき項目を列挙する。
固定リストではなく、変更内容に応じて取捨する。代表観点:

- 正当性 / バグ（ロジック誤り、off-by-one、null/未定義、競合、リソースリーク）
- エラー処理 / edge case（例外未処理、境界値、失敗パス）
- コードスタイル / 命名 / 可読性 / 重複
- 汎用 code smell（dead code、マジックナンバー、密結合）
- セキュリティ標準パターン（injection、機密混入、安全でない既定値）
- 言語 / FW イディオム
- テスト網羅（変更に対するテストの有無・妥当性）

difficulty tier や touched_sensitive に応じて重点を移す（例: auth/payment 接触ならセキュリティ観点を厚く）。
dialog-harness の仕様軸（philosophy.md 6 条の適合判定そのもの、SPEC/DONT 契約）は **対象外**——
それは gemini-review が独立観測する。視点直交が claude-review の存在意義。

## RL 内 / RL 外 分類（β案）

各チェックリスト項目を以下に分類する。RL（Rule）= CLAUDE.md / .claude/settings.json / skill 規約 /
直交スコープ等の既存ルール群。

- **RL 内（方向性の「適用」）**: 既存ルールに根拠を持つ検証項目。AI が自走して評価・指摘してよい。
  philosophy.md 第 6 条の C 区分（C1 抵触判断 / C2 トレードオフ）に対応。
- **RL 外（方向性の「発明」）**: どの既存ルールにも根拠を持たない **新しい評価軸** を導入する項目。
  これは「適用」ではなく「発明」であり、philosophy.md 第 6 条の H 区分（H1 哲学変更 / H3 方向性発案）
  ＝人間専権に該当する。AI は自走で確定せず **人間へ献上**（Type A 型）する。

「適用」と「発明」の区別が本プロトコルの肝である。既存軸に照らした判断は適用（自走可）、
評価軸そのものの創造は発明（人間専権）。この線引きが崩れると AI は何も自走できなくなる。

## 出力（OC が後続フェーズへ渡す）

```json
{
  "checklist": [
    {"item": "検証観点", "classification": "RL_in | RL_out",
     "rule_basis": "RL 内の場合の根拠 / RL 外の場合は null"}
  ],
  "rl_out_items": ["RL 外＝人間献上対象の新評価軸（あれば）"],
  "review_category": "maintenance | error_handling | conception | judgment"
}
```

`rl_out_items` が非空のとき、OC は Phase 4 で human_escalation_required を立て、Channel C に
献上ブロックを出す（`human-review-needed` ラベル要請）。空なら自走で Council 評価へ進む。

`review_category` は Council の weight 計算に渡す（[council-weights.md](../council-weights.md) の
situational_modifier 用）。マッピング: 一般＝maintenance / sensitive 接触＝error_handling /
新評価軸＝conception / 意図曖昧＝judgment。未確定は judgment（category_fallback: true）。
