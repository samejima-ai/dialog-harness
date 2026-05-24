# .github/reviews/ — claude-review 構造化アーティファクト

`claude-review.yml`（4 フェーズ Council 高高度レビュー）が PR ごとに生成する構造化レビュー記録の置き場。
情報代謝 3 層構造（philosophy.md 第 3 条「情報純度」の応用）でレビュー成果を保存する。

- ファイル名: `pr-<番号>-<head_sha>.md`
- 永続化方式: workflow 実行中に OC が Write し、`actions/upload-artifact` で回収（retention 30 日）。
  **PR ブランチには commit しない**（merge/branch state に踏み込まない原則）。
- 本ディレクトリ・本ファイルは harness-verifier の検査スコープ外（verify.py は `.claude/skills/` と
  `glossary.yml` のみ対象）。

## 3 層構造

| 層 | 内容 | 純度 | 宛先 |
|---|---|---|---|
| HIGH | レビュー結論・採否 verdict・確定検証結果 | ゼロノイズ | 人間 + 将来 AI |
| MEDIUM | 各ペルソナの評価過程・トレードオフ・weight 要約 | 圧縮 | 人間サマリー |
| LOW（種） | minority_opinion 全文・棄却された代替案・不採用懸念・COUNCIL-LOG エントリ | ノイズ許容 | 将来 AI 専用 |

**ゼロノイズにするのは HIGH 層だけ**。LOW 層は意図的に低純度の「種」（将来別 PR で効く伏線）を抱える。
ノイズの宛先は将来 AI であって人間ではない（対人間チャネルは高純度を維持）。

## 3 チャネルとの対応

| チャネル | 宛先 | 内容 |
|---|---|---|
| インライン PR レビューコメント | 開発者（即時） | HIGH のみ |
| 人間向け merge 判断サマリー（PR コメント） | 人間 | HIGH + MEDIUM |
| 本アーティファクト | 将来 AI | フル 3 層（LOW=種 はここだけ） |

## frontmatter

```yaml
pr: <番号>
head_sha: <sha>
reviewer: claude-review
tier: <difficulty tier 1/2/3>
category: <maintenance|error_handling|conception|judgment>
invocation_id: council-<ISO8601Z>-<6char>
judgment_confidence: <0.0-1.0>
consensus_mode: <auto_agree|escalate_to_human>
human_escalation_required: <bool>
generated_at: <ISO8601Z>
```
