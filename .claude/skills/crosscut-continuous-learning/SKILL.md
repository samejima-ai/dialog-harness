---
name: crosscut-continuous-learning
dimension: D4
origin: ECC-derived
origin_source: "ecc:continuous-learning/"
origin_version: "ECC v2.0.0-rc.1"
chewing_translation: "T3+ガードレール語彙化"
chewing_pr: "samejima-ai/dialog-harness#78"
chewing_council_ref: "council-2026-05-11T07:00:00Z-w2qb01"
chewed_at: "2026-05-11T07:30:00Z"
description: >
  `harness-verifier/reports/hook-observations.jsonl` を読み込み、PreToolUse /
  PostToolUse の繰り返しパターンから「instinct promotion 候補」を抽出して
  `delivery/CONTINUOUS-LEARNING-CANDIDATES-<timestamp>.md` に出力する観測層
  skill。Council 諮問 (w2qb01) により **自動 promote は実装しない** ことが
  確定し、本 skill は **候補出力のみ** を担う。適用判断は人間最終承認に閉じる
  （philosophy 第 6 条準拠）。
  「continuous-learning」「instinct promotion」「観測パターンから skill 候補
  抽出」「hook 観測ログから何が繰り返されているか分析」「Wave 2 末振り返り
  儀式で観測経路を確認」等の発話で本 skill の起動を必ず検討する。
  CTL 0 では skill 自体を inactive（観察温存・人間最終承認の厳格適用）。
  CTL ≥ 1 で active、候補出力経路のみ。自動 promote は philosophy 第 7 条
  「AI 組織論」の P4 介入権を事後発動化させる危険があるため、Wave 2 では
  実装しない（Wave 3 で再諮問予定）。
  本 skill は harness-verifier の観測ログを **読み取り専用** で消費する
  上流依存型 skill であり、観測ログを書き換えない（独立性原則・append-only
  維持）。
---

# crosscut-continuous-learning — 観測ログから instinct promotion 候補を抽出

ECC `continuous-learning/` の **「観測 → pattern 検出 → 候補化 → promote」**
4 段階のうち、**「観測 → pattern 検出 → 候補化」** までを T3（サブセット選別）
+ ガードレール語彙化で取り込んだ DH 独自の continuous-learning 機構。

「promote」段階は Council 諮問 w2qb01 により **本 skill では実装しない**。
適用判断は人間最終承認に閉じる（philosophy 第 6 条準拠）。

## 設計原則

### 1. 候補出力のみ（promote 不実装）

ECC `continuous-learning v2.1` の自動 promote 経路は **DH では棄却**:
- philosophy 第 6 条「人間最終承認」を侵食
- philosophy 第 7 条 P4 介入権を事後発動化させる
- 観測データ不足の段階で自動経路を開くリスク

本 skill の出力は `delivery/CONTINUOUS-LEARNING-CANDIDATES-<timestamp>.md`
への **候補リスト** のみ。実際の skill 化 / instinct 化は人間レビューを経た
別 PR で実施する。

### 2. CTL 連動の active/inactive

| CTL | 動作 |
|---|---|
| **CTL 0**（local_only） | **inactive**（観察温存・人間最終承認の厳格適用） |
| CTL 1（github_assisted） | active、候補出力のみ |
| CTL 2+（autonomous） | active、候補出力のみ（CTL 1 と同等、自動 promote は Wave 3 候補） |

CTL 0 での inactive 化は哲学者ペルソナ意見（w2qb01 confidence 0.85）の
反映であり、philosophy 第 8 条候補「自律性原則 + 哲学ガードレール」の
語彙化前に自動経路を開かない予防的措置。

### 3. 観測ログとの一方向依存（独立性原則準拠）

```
harness-verifier/reports/hook-observations.jsonl
    ↑ 読み取りのみ（append-only 維持、書き換えなし）
crosscut-continuous-learning/scripts/detect_patterns.py
    ↓ 候補出力
delivery/CONTINUOUS-LEARNING-CANDIDATES-<YYYY-MM-DDTHH:MM:SSZ>.md
    ↑ 人間レビュー
（次 Wave PR で採用された候補のみ skill / instinct に昇格）
```

矢印方向の意味:
- 本 skill → 観測ログ は **読み取りのみ**（一方向）
- 本 skill → 候補出力ファイル は **書き込みのみ**（append-only）
- 観測ログを本 skill が書き換えることはない（harness-verifier 独立性原則）

## 起動経路

### 明示起動（推奨）

「continuous-learning を走らせて」「観測パターン抽出して」「instinct promotion 候補リスト出して」等の発話で起動。CTL 確認後、CTL 0 なら inactive 旨を返して停止。

### 振り返り儀式経路（Wave 2 末以降）

Wave 2 末 / Wave 3 末の振り返り儀式（F1/F2/F3）で「観測経路の運用実績確認」項目から自動起動。出力は `delivery/CONTINUOUS-LEARNING-CANDIDATES-*.md`、人間レビュー前提。

### 自動起動（Wave 3 候補、本 Wave では未実装）

cron / hook 経由の定期実行は **Wave 2 では実装しない**。Wave 3 で再諮問予定（minority opinion w2qb01 A の温存先）。

## 出力形式

`delivery/CONTINUOUS-LEARNING-CANDIDATES-<timestamp>.md`:

```markdown
# Continuous Learning 候補 — <timestamp>

## 観測対象
- 観測ログ: harness-verifier/reports/hook-observations.jsonl
- 観測期間: <start_ts> 〜 <end_ts>
- 観測件数: N entries

## 検出パターン

### Pattern 1: <tool> + <command_pattern> 繰返
- 出現回数: M
- 出現セッション: K session
- 候補化提案: skill / instinct / SPEC 反映 / 棄却
- 哲学整合性メモ: <第 6 条 / 第 7 条 / 第 8 条候補との整合>

## 人間レビュー欄
- レビュー日:
- レビュー者:
- 採用候補: [Pattern N, ...]
- 棄却候補: [Pattern N, ...]
- 別 PR 化対象: [Pattern N → PR #X]
```

詳細は [references/output-format.md](references/output-format.md)

## 関連 skill

- `crosscut-hook-observer/` — 観測ログ生成側（本 skill の入力源）
- `harness-verifier/` — 観測ログ消費の独立検証層（並列の読み手）
- `crosscut-feedback-loop/` — 採用候補の還流先（次 PR で skill / SPEC 化される際の経路）

## バージョン

- v0.1.0（Wave 2 walking skeleton）— 候補出力経路のみ、自動 promote なし、CTL 0 inactive
- Wave 3 候補:
  - minority opinion w2qb01 A（CTL 連動段階的自動度）の再諮問
  - cron 経由定期実行（運用実績観測後）
  - 採用候補の skill / instinct 自動昇格（philosophy 第 8 条候補確定後）
