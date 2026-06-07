# Council 諮問: `council-2026-05-13T03:35:00Z-rtkSHA`

`rtk-integration/scripts/install.ps1` の `$ExpectedSha256` default-fail 挙動 (kakuman PR #75 Copilot review 起点) について Council に諮問した記録の **人間可読 並存版**。

- **YAML 正本**: `history/COUNCIL-LOG.md` 内 `- invocation_id: "council-2026-05-13T03:35:00Z-rtkSHA"` エントリ
- **配置根拠**: `crosscut-council/references/consensus-protocol.md` §人間可読並存規約
- **発行タイミング**: 本規約確立 PR (#96) 内で retroactive 作成 (規約 §適用範囲 の例外 2 件目)

---

## 議題

`rtk-integration/scripts/install.ps1` 冒頭の `$ExpectedSha256` 定数が **空文字** のままだと default で install 失敗する挙動について、どう扱うか?

- **問題の前提 (両面)**:
  - kakuman PR #75 で Copilot が「broken-by-default」と指摘 (UX 観点)
  - DH PR #93 commit message では「**意図的セキュリティゲート** (MITM hardening、escape hatch `RTK_SKIP_VERIFY=1`)」として導入 (security 観点)
- **両者が対立** — Council 諮問が必要

### 選択肢

| 案 | 内容 | trade-off |
|---|---|---|
| **A** | rtk v0.37.1 の公式 SHA (`3b9f207e8e...`) を populate、現状の `empty → reject + escape hatch` 構造は維持 | 採用障壁解消 + MITM hardening 維持、Maintainer 責務 (SHA 更新) は手動継続 |
| **B** | empty → warn のみで install 続行、escape hatch 廃止 | UX 最良、ただし security regression |
| **C** | 現状維持 (intent 確認のみ)、Copilot 指摘 close | DH PR #93 意図通り、ただし誰も使えない状態が継続 |
| **D** | A の上位互換: SHA populate + SKILL.md / references に SHA 更新 protocol を明文化 | A の効果 + Maintainer 責務を SPEC レベルで明示化、long-term 保守性向上 |

### Option A の前提データ (確定済)

- 公式 [checksums.txt](https://github.com/rtk-ai/rtk/releases/download/v0.37.1/checksums.txt) より:
  ```
  3b9f207e8ea360d744649760788cbcf7d6ce62d8ccb8677aa3c8d1513a9d2cc2  rtk-x86_64-pc-windows-msvc.zip
  ```
- 本セッションで zip を独立 `curl -sL` で download → `sha256sum` で self-compute
- **公式値と self-computed が byte 単位で完全一致** を verify 済

---

## 発言 (3 persona、独立判定)

### 経営者 (ROI / 採用障壁、conf 0.75)

> 現状の `$ExpectedSha256 = ''` は default で install 失敗 = **採用障壁**。ユーザーが手動で `RTK_SKIP_VERIFY=1` を export しないと使えない UX 悪化。SHA を populate すれば DH PR #93 の security 構造を破壊せず採用障壁を解消できる (**一石二鳥**)。案 B (warn のみ) は MITM リスクを default で受容するため経営的に軽率に決定すべきでない。
>
> **stance**: 案 A 推奨

### 開発者 (保守性 / Shift Left、conf 0.85)

> SHA populate は **1 行変更の事務作業**。値は本セッションで公式 checksums.txt + self-compute cross-verify 済の値 (`3b9f207e8e...`) が確定済。案 B は philosophy 第 2 条 Shift Left 原則 (発生防止 > 検出) と緊張する **security regression**、案 C は技術的負債放置。案 D は良いが本 PR スコープ拡張、まず A を実装してから別 PR で D の拡張を扱うほうが漸進的。
>
> **stance**: 案 A 推奨

### 哲学者 (意味 / philosophy 第 2/6 条整合、conf 0.70)

> DH PR #93 の `empty → reject + escape hatch` は **philosophy 第 6 条「人間最終承認」の具現** として読める。Empty SHA は『Maintainer が未承認』状態を表し block する意義あり。`RTK_SKIP_VERIFY=1` は明示意思表示で第 7 条 P4 介入権の事前付与と整合。**案 A は意味論を維持しつつ Maintainer 責務を果たす**。案 B は第 2 条 (Shift Left) と第 6 条 (人間最終承認) の二重侵食、案 C は責務放置。
>
> ただし long-term は SHA 更新 protocol を `SKILL.md` / `references` で明文化したい (Option D 寄り) — minority opinion として保持、本 PR か別 PR で扱う余地あり。
>
> **stance**: 案 A 推奨 + minority (long-term D 寄り)

---

## 結果

### 重み計算 (category: `operation`)

- **base_weights** (business): 経営者 3 / 開発者 4 / 哲学者 3 (sum 10)
- **situational_modifier** (`operation`): 経営者 +1 / 開発者 0 / 哲学者 -1
- **final_weights**: **経営者 4 / 開発者 4 / 哲学者 2** (sum 10)

| stance | supporters | weight_sum | weighted_score |
|---|---|---|---|
| 案 A | 経営者 (4×0.75) + 開発者 (4×0.85) + 哲学者 (2×0.70) | 10 | 3.0 + 3.4 + 1.4 = **7.8** |

- **conflict_type**: **unanimous** (3 persona 全員独立に案 A 支持)
- **max_score_stance**: 案 A
- **judgment_confidence**: **0.78** (閾値 0.5 超で自律判定成立)

### Recommended

**案 A**: `$ExpectedSha256 = '3b9f207e8ea360d744649760788cbcf7d6ce62d8ccb8677aa3c8d1513a9d2cc2'` を populate。現状の `empty → reject + escape hatch (RTK_SKIP_VERIFY=1)` 構造は維持。SHA 値の信頼根拠は公式 GitHub Release checksums.txt + 本セッション self-compute cross-verify (公式値と完全一致)。

### Minority opinion

哲学者: long-term は SHA 更新 protocol を SKILL.md / references で明文化したい (Option D 寄り)。経営者・開発者の minor concerns (将来 `$RtkVersion` bump 時の Maintainer 責務、信頼チェーンの fragility) と整合。

### consensus_mode

**`auto_agree`** (`judgment_confidence` 0.78 > 0.5)

### human_escalated

`false`

---

## 選択 (人間判断、確定済)

**`agreed_with_modification`** — 案 A 採用 + 哲学者 minority opinion (Option D 寄り) を同 PR (#96) に併合

### `modification_note`

案 A 採用 + 哲学者 minority opinion を同 PR (`claude/fix-rtk-install-sha-TDmT8`) に併合 (Option D 格上げ実装): `references/sha-update-protocol.md` を新設し SKILL.md の参照ドキュメント節からリンク。本 cycle で long-term 課題を解消することで Maintainer 責務を SPEC レベルで明示化。

### `cascade_to`

本 PR で `install.ps1` `$ExpectedSha256` populate + `sha-update-protocol.md` 新設 + SKILL.md 参照追記を 1 commit で実施。kakuman 側は本 PR merge 後の D3 sync で自動追従 (PR #93 / #75 と同型サイクル)。

### `agreed_at`

2026-05-13T03:40:00Z

---

## 参照

- YAML 正本: `history/COUNCIL-LOG.md` 内 `council-2026-05-13T03:35:00Z-rtkSHA` エントリ
- PR: [samejima-ai/dialog-harness#96](https://github.com/samejima-ai/dialog-harness/pull/96)
- 本規約: `.claude/skills/crosscut-council/references/consensus-protocol.md` §人間可読並存規約
- 起点: [samejima-ai/kakuman-platform-v3.0#75](https://github.com/samejima-ai/kakuman-platform-v3.0/pull/75) Copilot review
- philosophy 整合: 第 2 条 Shift Left / 第 6 条 人間最終承認
