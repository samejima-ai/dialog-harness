# Circuit Breaker Spec

経済的暴走防止 + 品質劣化防止のための上限機構。philosophy.md 第 7 条 P4「暴走時介入」の AI 兆候提示の実装。

## 上限値（v5.7.0 デフォルト）

| 軸 | 上限 | リセット周期 |
|---|---|---|
| 日次 Issue pickup | 5 件/日 | UTC 0:00 |
| 月次 Issue pickup | 50 件/月 | 月初 1 日 0:00 UTC |
| 同時実行数 | 1（concurrency） | workflow 終了 |

これらは観測駆動で調整。dialog-harness の使用実績データを蓄積後、必要なら v5.7.x patch で値変更。

## 統計記録

`.gemini/issue-pickup-stats.json` に append-only で記録：

```json
{
  "version": "v5.7.0",
  "issues": [
    {
      "issue_number": 50,
      "pickup_at": "2026-05-03T10:00:00Z",
      "verdict": "pickup_yes",
      "result": "merged|failed|in-progress",
      "completion_at": "2026-05-03T10:30:00Z"
    },
    ...
  ]
}
```

`actions/upload-artifact` で 7 日 retention で保存（gemini-review.yml と同形式）。

## Workflow 内での counter

```bash
# 日次 counter
TODAY=$(date -u +%Y-%m-%d)
TODAY_COUNT=$(jq --arg d "$TODAY" '[.issues[] | select(.pickup_at | startswith($d))] | length' .gemini/issue-pickup-stats.json)

if [ "$TODAY_COUNT" -ge 5 ]; then
  echo "::warning::Daily Circuit Breaker triggered (5/day)"
  gh issue edit $ISSUE_NUMBER --add-label "circuit-broken"
  echo "::notice::Pickup skipped due to circuit breaker. Will retry tomorrow."
  exit 0
fi

# 月次 counter
MONTH=$(date -u +%Y-%m)
MONTH_COUNT=$(jq --arg m "$MONTH" '[.issues[] | select(.pickup_at | startswith($m))] | length' .gemini/issue-pickup-stats.json)

if [ "$MONTH_COUNT" -ge 50 ]; then
  echo "::warning::Monthly Circuit Breaker triggered (50/month)"
  gh issue edit $ISSUE_NUMBER --add-label "circuit-broken"
  echo "::notice::Pickup skipped due to circuit breaker. Will retry next month."
  exit 0
fi
```

## 緊急停止（P4 暴走時介入）

人間 P4 が手動で停止する経路：

1. **Repository Secrets から GEMINI_API_KEY を一時削除** → workflow 全体が pre-check で skip
2. **Repository Settings → Actions → Disable workflow** → 完全停止
3. **Issue に label `do-not-pickup` 付与** → 該当 Issue のみ block（他 Issue は通常通り）
4. **Issue を close** → workflow trigger 条件で除外（state: open のみ pickup）

これらは **人間 P4 専管** (philosophy 第 7 条)。AI は notice/warning で兆候を提示するまで。

## 解除

| 解除方法 | 効果 |
|---|---|
| 翌日待ち（自然解除） | 日次 counter 自然リセット |
| 月初待ち（自然解除） | 月次 counter 自然リセット |
| 人間が `circuit-broken` label を削除 | 強制解除（ただし統計上はカウント維持） |
| 統計 ファイル を 手動 reset | 統計初期化（推奨しない、観測データ消失） |

## 観測駆動での閾値調整

v5.7.x patch 候補：

- 実運用 1 ヶ月で日次平均 pickup 数が 3 以下 → 日次 5 → 10 へ緩和検討
- 月次 50 で詰まる場合 → 100 へ緩和、または重要 Issue priority 機構導入
- 同時実行 1 で並列性不足 → 2 へ拡大検討（gemini API quota 影響注意）

調整は autonomous-dev が運用観測データを基に Type C 献上で SPEC 改訂提案。
