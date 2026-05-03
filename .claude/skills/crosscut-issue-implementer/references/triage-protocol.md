# AI Triage Protocol

`crosscut-issue-implementer` の三次フィルター（AI triage）詳細プロトコル。**triage は gemini-cli メイン継続**（v5.7.1 以降も変更なし）— 軽量処理 + 無料 tier 活用 + 異質モデル併走（philosophy 第 3 条）の観点から、実装本体を Claude Code CLI に切り替えた v5.7.1 でも triage 部分は gemini-cli のまま維持する。

## 設計原則

- 二次フィルター（label + 本文必須項目）通過後の品質確認層
- gemini-cli が SPEC.md / DONT.md / REGIME.md `current_focus` と Issue 内容を照合
- 判定 = pickup_yes / skip_<理由> の二値、skip 時は理由 label を自動付与
- **v5.7.1 で実装本体は Claude Code CLI に変更されたが、triage は gemini-cli 維持**（理由: 軽量、無料 tier、異質モデル併走による情報純度保全）

## Triage 入力

gemini-cli に渡す情報：

```
INPUT:
  issue:
    title: <Issue title>
    body: <Issue body>
    labels: [...]
    author: <author login>
  spec:
    spec_md: <SPEC.md 全文 or 該当セクション>
    dont_md: <DONT.md 全文 or 該当セクション>
  regime:
    current_focus:
      type: <bug-fix / feature / etc>
      target: <branch>
      priority: <critical / standard / low>
    autonomous_scope: full / merge_gated / custom
  context:
    branch_name: <現在ブランチ命名 (γ フォールバック用)>
    recent_commits: <直近 5 commit>
```

## Triage 判定ロジック

```
JUDGMENT:
  Step 1: scope check
    - Issue が SPEC.md 範囲内か？
    - Issue が DONT.md に抵触していないか？
    NO → return skip_out_of_scope
  
  Step 2: focus check
    - Issue label `type:*` と current_focus.type が一致するか？
    - label 未指定なら Issue 本文から推論
    NO → return skip_focus_mismatch
  
  Step 3: complexity check
    - Issue が L2 級スコープか？（複数ドメイン横断 / 大規模リファクタ）
    YES → return skip_complexity (人間 L0 起動要請)
  
  Step 4: clarity check
    - 本文の再現手順 / 期待動作 / 受入条件が AI 実装可能なレベルか？
    NO → return skip_other (label `needs-clarification`)
  
  Step 5: 全 PASS
    → return pickup_yes
```

## gemini-cli 実装パターン

```bash
# Issue 取得
gh issue view $ISSUE_NUMBER --json title,body,labels,author > /tmp/issue.json

# context 構築
cat /tmp/issue.json SPEC.md DONT.md REGIME.md > /tmp/triage-input.txt

# gemini-cli triage
echo "$TRIAGE_PROMPT" | gemini --yolo --prompt-file /tmp/triage-input.txt --output-format json > /tmp/triage-output.json

# 結果 parse
TRIAGE_VERDICT=$(jq -r '.verdict' /tmp/triage-output.json)

case "$TRIAGE_VERDICT" in
  pickup_yes) ... pickup へ ;;
  skip_out_of_scope) gh issue edit $ISSUE_NUMBER --add-label "out-of-scope"; exit 0 ;;
  skip_focus_mismatch) gh issue edit $ISSUE_NUMBER --add-label "focus-mismatch"; exit 0 ;;
  skip_complexity) gh issue edit $ISSUE_NUMBER --add-label "too-complex"; exit 0 ;;
  *) gh issue edit $ISSUE_NUMBER --add-label "needs-clarification"; exit 0 ;;
esac
```

## Triage Prompt 雛形

```
あなたは dialog-harness の Issue triage エージェントです。
以下の Issue を読み、pickup 可否を判定してください。

判定基準:
1. SPEC.md 範囲内か / DONT.md に抵触していないか (skip_out_of_scope 候補)
2. Issue type が REGIME.md current_focus と一致するか (skip_focus_mismatch 候補)
3. L2 級スコープではないか (skip_complexity 候補)
4. 本文の再現手順 / 期待動作 / 受入条件が実装可能レベルか (skip_other 候補)

出力形式 (JSON):
{
  "verdict": "pickup_yes" | "skip_out_of_scope" | "skip_focus_mismatch" | "skip_complexity" | "skip_other",
  "reasoning": "判定理由 (1-2 文)",
  "confidence": 0.0 - 1.0,
  "estimated_files_changed": 数値,
  "estimated_complexity": "trivial" | "small" | "medium" | "large"
}

confidence < 0.5 の場合は skip_other を返し、Issue コメントで人間に判断を求める。
```

## 観測ポイント

triage の精度は v5.7.0 / v5.7.1 運用初期の核心観測項目（v5.7.1 でも triage 機構は変更なし）：

- false positive（pickup_yes だが実装失敗）
- false negative（skip だが本来は pickup 可能だった）
- 平均 confidence
- gemini-cli token 使用量（無料 tier RPD 圧迫）

統計を `.gemini/triage-stats.json` に蓄積、観測駆動で prompt や閾値を調整。fail 率高い場合は Council 起動可（adrv01-Ph1 自己申告経由）でフォールバック判断。
