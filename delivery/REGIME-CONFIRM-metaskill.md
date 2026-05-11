# REGIME 現状確認 — メタスキル開発案件

**確認日時**: 2026-05-11 JST
**確認対象**: DH 本体の REGIME / dev_mode / autonomous_scope / CTL

---

## 1. DH 本体の REGIME 構造

DH 本体には root レベルの `REGIME.md` は存在しない（DH は **方法論を提供する側** であり、`REGIME.md` は **利用者プロジェクトの root に置かれる構造**）。DH 自身の改修体制は以下:

- **改修バージョン**: v5.10.0 in progress / v5.9.0 in progress（並行）
- **次期 minor 候補**: v5.11.0（cookpato A1-A5 統合）/ v5.12.0（本案件 = ECC 吸収メタスキル化）
- **AI 能力バージョン**: claude-opus-4-7
- **体制**: L0（spec-architect、本案件で起動中）→ Council → 後続セッションで L1 委譲

---

## 2. autonomous-drive 稼働状況

DH 自身で autonomous-drive が **本番稼働中**:

### `.github/workflows/` 実装

- `issue-pickup.yml` — AI triage + Issue 選別 + Claude Code CLI 実行（v5.10.0 で type-aware body_check 化）
- `gemini-review.yml` — PR レビュー（v5.5.2 stable、transient fail detection + PAT check）
- `auto-merge.yml` — 4 層条件 AND 自動 merge（v5.9.0 で opt-in → opt-out 反転中）
- `harness-verify.yml` — DH 自己検証（月次 cron + PR trigger）

### Templates

- `templates/github-workflows/` 4 テンプレート: issue-pickup / gemini-review / auto-merge / issue-quality-gate

### 適用実績

- 利用者プロジェクト 7 例目正規適用中（cookpato 等）

### 実装エージェント

- メイン: Claude Code CLI（v5.7.1 で gemini-cli から pivot、AD-029）
- フォールバック: gemini-cli

---

## 3. 本案件における dev_mode / autonomous_scope 想定

本案件は DH 本体の改修であり、利用者プロジェクトの dev_mode 判定とは異なる。改修自体の体制は:

- **dev_mode**: `autonomous` 相当（GitHub Actions / Council / autonomous-drive が稼働している環境で改修）
- **autonomous_scope**: 本案件は **`full` ではなく `opt-in`**（philosophy.md 改修 = philosophy 領域は v5.9.0 Council 判定により opt-in 維持決定）
- **`human-review-needed` ラベル**: 本案件で改修対象となる `harness-verifier/PHILOSOPHY.md` への変更は必須ラベル

### 影響する v5.9.0 Council 判定（amrev1）

auto-merge を opt-in → opt-out に反転したが、以下は **opt-in 維持**:

- philosophy.md 領域
- harness-verifier 領域
- 境界 SPEC 領域

→ 本案件のタスク D（PHILOSOPHY 追記）は **opt-in 領域該当**、`human-review-needed` ラベル必須、人間最終承認経由。

---

## 4. CTL（Continuous Trust Level）想定

- DH 本体: CTL 2 相当（既存 v5.x の運用実績豊富、本案件は追加のみ・破壊なし）
- 本案件改修: 振り返り儀式レベル 3 必須（LC=2）

---

## 5. 検証

```
$ git branch --show-current
claude/integrate-dialogharness-2XsY3

$ git status --short
（clean）

$ ls .claude/skills/ | wc -l
16

$ grep -E "^## (v5\.[5-9]|v5\.1[0-9])" history/REGIME-LOG.md
v5.10.0（in progress）
v5.9.0（in progress）
v5.7.2 / v5.7.1 / v5.7.0 / v5.6.0 / v5.5.3 / v5.5.2 / v5.5.1 / v5.5.0
```

---

## 6. 結論

- DH 本体 v5.10.0/v5.9.0 並行進行中、本案件は v5.12.0 候補として独立着手可
- `human-review-needed` ラベルでの opt-in 維持運用が前提
- 振り返り儀式レベル 3（F1/F2/F3）は `RITUAL-2026-05-11-metaskill.md` で完了済
- Phase 0 残作業（ECC 観察 + Council 議題草稿 + 参照カタログ雛形）に進行可
