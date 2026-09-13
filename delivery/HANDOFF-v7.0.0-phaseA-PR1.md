# 開発成果サマリー

**プロジェクト**: dialog-harness 本体（メタハーネス自己開発）
**完了日時**: 2026-09-13
**モード**: M2

---

## 1. できたもの

- compaction 後に憲法の要点 4 行が自動で再提示されるようになった（SessionStart hook）
- 使っていない skill 3 本を一覧から外し、6 版放置されていた placeholder skill（crosscut-verifier-philosophy）を 1 本廃止した
- 大きすぎた skill 本体 3 本を 500 行未満に分割した（内容は移動のみ）
- 独立レビュアーが「作った側の自己評価」を読む前に自分の判定を出す順序にした
- 「機械検査の FAIL は AI の PASS で覆らない」を配線表に明文化した
- モデル世代交代を機械で記録し、時限規範の再審が実際に発火するようにした（修正前 0 件 → 3 件）
- Council（3 ペルソナ）と単一レビュアーの比較実験を 10 件 × 2 条件で行い、判断材料として記録した

## 2. 動作確認方法

```
python3 harness-verifier/verify.py --strict
for t in scripts/test-*.py; do python3 "$t"; done
CLAUDE_PROJECT_DIR=$PWD python3 templates/hooks/anchor-core.py
```

新規セッションを起動すると冒頭に不変核 4 行が載る（人間確認をお願いしたい 1 点）。

## 3. Council 判定ダイジェスト

開発中に Council による自律判定が **1 件** ありました。

- ✅ 自動進行: 0 件
- ⚠️ 人間判断を仰いだ: 1 件（着地単位 → 案C「description 圧縮は基準値を先に取ってから」。「すべて実行」の事前承認で採用）

## 4. 残課題

- F3 の基準値計測（この PR の merge 後・3 run）→ その後 PR-3 で description 圧縮
- F6 失効セマンティクス（PR-2）
- Phase B（philosophy 2 分割・第 7 条）は 2026-11-06 ゲート後に人間起票

## 5. 事後評価について

Council 判定 1 件の妥当性を評価すると CTL の精度が上がります。
評価する場合は「評価する」、後回しは「保留」、不要なら「スキップ」と返答してください。

[評価する] [保留] [スキップ]
