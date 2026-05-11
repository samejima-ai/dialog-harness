# AgentShield 参照導入規約（Wave 2 候補 4、PR #78）

**Council 採決**: `council-2026-05-11T07:00:00Z-w2qb02`（recommended B: warn のみ参照導入）
**observation**: `history/refs-draft/ecc/agentshield-spec.md`

---

## 規約

[AgentShield](https://www.npmjs.com/package/ecc-agentshield)（`ecc-agentshield` npm package）は Claude Code 設定資源向けの **静的解析セキュリティスキャナ**（102 ルール × 5 カテゴリ）。DH 自前実装は行わず、**利用者プロジェクト側で手動 install + warn のみ参照導入** とする。

### 5 カテゴリ（全採用、warn のみ）

| カテゴリ | 検出対象 |
|---|---|
| Secrets detection | hardcoded API keys / tokens / passwords |
| Permission auditing | dangerous tool combinations（Bash + Write 同時許可 / unrestricted Network 等） |
| Injection analysis | SQL / XSS / path traversal / command injection |
| Hook risk scoring | trigger × action の危険組合（PreToolUse × Bash 実行 等） |
| Configuration weaknesses | exposed endpoints / missing auth / insecure defaults |

### 棄却経路

| 経路 | DH 採用 | 棄却根拠 |
|---|---|---|
| **`--fix` 自動修復** | ✗ | philosophy 第 6 条「人間最終承認」を侵食、破壊的変更可能 |
| **`--opus --stream` 外部 LLM 経路** | ✗ | 独立性原則・観察温存と緊張、外部 LLM 呼出 |
| **DH workflow からの自動起動** | ✗ | 第 7 条 P4 介入権を事後発動化させる危険 |

---

## 利用者プロジェクトでの導入手順

```bash
# 1. 利用者プロジェクト側で手動 install（DH 側からの強制起動なし）
npm install --save-dev ecc-agentshield

# 2. baseline scan（warn のみ、--fix なし）
npx ecc-agentshield scan

# 3. 検出された脆弱性を人間レビュー → 個別対応
```

`--fix` / `--opus --stream` の使用は **本規約では推奨しない**（DH 哲学整合範囲外）。利用者プロジェクト側の判断で使用する場合、philosophy 第 6 条「人間最終承認」に基づく review プロセスを通すこと。

---

## DH 哲学整合経路

| AgentShield 機能 | DH 既存機構 | 統合方針 |
|---|---|---|
| Secrets detection | `crosscut-verifier-drift` の片鱗 | 利用者側 scan 結果を `crosscut-feedback-loop` 経由で還流 |
| Permission auditing | DH `dev-env-spec.md` permission 規約 | warn 検出を spec-architect 対話で確認 |
| Hook risk scoring | DH `.claude/hooks.json` warn-only 設計 | warn のみ採用方針と整合 |
| Configuration weaknesses | `harness-verifier/verify.py` 内部整合性検査 | 内部整合性 + 外部脆弱性の役割分担 |

---

## バージョン

- v0.1.0（Wave 2 PR #78）— warn のみ参照導入、DH 自前実装なし
- 拡張候補（Wave 3 以降）:
  - DH 自前実装是非を `v6.0.0` 候補として再諮問（philosophy 第 8 条候補確定後）
  - utilizer プロジェクト側で `ecc-agentshield` を npm install することの推奨度（minority opinion w2qb02 A 温存範囲）
