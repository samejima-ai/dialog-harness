# continuous-learning 候補出力規格

`detect_patterns.py` が生成する `delivery/CONTINUOUS-LEARNING-CANDIDATES-<timestamp>.md` の Markdown スキーマ定義。

## 全体構造

```markdown
# Continuous Learning 候補 — <ISO8601 UTC timestamp>

**重要**: 本ファイルは人間レビュー前提の候補リスト。
自動採用は禁止（Council 諮問 w2qb01 採決 B 反映）。

## 観測対象
- 観測ログ: `harness-verifier/reports/hook-observations.jsonl`
- 観測期間: <first_ts> 〜 <last_ts>
- 観測件数: N entries

## 検出パターン

### Pattern N: <tool> + <token> 繰返

- 出現回数: M
- 出現セッション: K
- 候補化提案: ☐ skill / ☐ instinct / ☐ SPEC 反映 / ☐ 棄却
- 哲学整合性メモ: <第 6 条 / 第 7 条 / 第 8 条候補との整合>

## 人間レビュー欄

- レビュー日:
- レビュー者:
- 採用候補:
- 棄却候補:
- 別 PR 化対象:
```

## 設計原則

### 1. 人間レビュー前提（自動採用禁止）

ファイル冒頭に「本ファイルは人間レビュー前提」「自動採用は禁止」を明記。AI agent が自動採用しないための **規約的歯止め** で、Council 諮問 w2qb01 採決 B（候補出力のみ、人間最終承認）を実装的に表現する。

### 2. timestamped 別ファイル（append-only ではない）

`hook-observations.jsonl`（観測層）は append-only だが、本ファイルは **人間レビュー単位** で別ファイル。レビュー完了後の archive は人間判断で `history/` に移動可能。

### 3. 候補化提案の 4 選択肢

| 選択肢 | 内容 |
|---|---|
| skill | 既存または新設 skill として実装 |
| instinct | 直感層（観測由来のヒューリスティック）として組込 |
| SPEC 反映 | SPEC.md / DONT.md / ADR への規約追加 |
| 棄却 | 候補としては記録するが採用しない |

instinct 化は **Wave 2 では実装経路が存在しない**（哲学者ペルソナ w2qb01 confidence 0.85 の反映）。Wave 3 で第 8 条候補確定後に再諮問予定。

### 4. 哲学整合性メモ欄（必須記入項目）

各 Pattern に対して philosophy 6 条 + 第 7 条 + 第 8 条候補との整合性を **人間レビュー時に記入** する欄を提供する。これは philosophy ガードレールが pattern 化の段階から組み込まれることを担保する。

## 閾値とパラメータ

| 名前 | 値 | 意味 |
|---|---|---|
| `MIN_OCCURRENCE` | 3 | この件数以上繰返したパターンのみ候補化（ノイズ抑制） |
| `most_common(50)` | 50 | 上位 50 パターンのみ報告（人間レビュー負荷上限） |
| `signature_token 長` | 64 | tool 引数のトークン化長（プライバシ・サイズ抑制） |

将来 Wave 3 で再諮問されればより精緻な pattern 検出（NLP / 系列分析）に置き換わる候補。

## バージョン

- v0.1.0（Wave 2 walking skeleton）— tool + signature_token の繰返検出のみ
- Wave 3 候補:
  - 系列パターン検出（A → B → C の繰返）
  - session 横断の共通パターン
  - 哲学整合性メモの AI 補助記入（philosophy verifier 連携）
