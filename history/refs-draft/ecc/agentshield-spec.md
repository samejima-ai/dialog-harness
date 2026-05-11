# AgentShield 仕様参照カタログ（draft）

**観察対象**: `ecc-agentshield` npm package（ECC v2.0.0-rc.1 連携、v1.6.0 Feb 2026 で初統合）
**観察日**: 2026-05-11 JST
**再観察予約**: 2026-11-11
**npm package**: `ecc-agentshield`（`ecc-universal` とは独立）
**GitHub Marketplace**: ECC Tools（free / pro / enterprise tiers）

---

## 1. 概要

AgentShield は Claude Code 設定資源（agents / skills / hooks / MCP / CLAUDE.md / settings.json）に対する **静的解析セキュリティスキャナ**。ECC とは別パッケージで配布され、Claude Code から `/security-scan` slash command で起動可能。

- **規模**: **102 静的解析ルール × 1,282 テスト**（98% カバレッジ）
- **実装言語**: Node.js（npm package）
- **実装規模推定**: 500-1000 LOC コア + テスト多数

---

## 2. スキャン対象

| 対象 | 検出対象 |
|---|---|
| `CLAUDE.md` | 危険な指示パターン / secrets 直書き |
| `settings.json` / `~/.claude/settings.json` | 不適切な permission / env var leak |
| `mcp-servers.json` / `mcp-configs/` | 不正な MCP server endpoint / auth weakness |
| `hooks.json` / `hooks definitions` | hook trigger × action の危険組合 |
| `agents/*.md` | agent definition の権限肥大 / トリガー文言の prompt injection 余地 |
| `skills/**/*.md` | skill 内の危険 command / 不適切な tools 列挙 |

---

## 3. 脆弱性カテゴリ（102 ルールの粗分類）

| カテゴリ | 内容 |
|---|---|
| Secrets detection | hardcoded API keys / tokens / passwords |
| Permission auditing | dangerous tool combinations（例: Bash + Write の同時許可 / unrestricted Network） |
| Injection analysis | SQL injection / XSS / path traversal / command injection |
| Hook risk scoring | trigger（PreToolUse など）× action（Bash 実行 / file delete）の危険組合 |
| Configuration weaknesses | exposed endpoints / missing auth / insecure defaults |

---

## 4. 実行モード

```bash
npx ecc-agentshield scan                    # Baseline
npx ecc-agentshield scan --fix              # Auto-remediate
npx ecc-agentshield scan --opus --stream    # Opus + streaming advisories
```

- `--fix`: 自動修復（破壊的変更を含む可能性、人間 review 推奨）
- `--opus --stream`: Opus model で AI advisory を streaming 出力

---

## 5. DH との対応関係

| AgentShield 機能 | DH 対応機構 | 対応度 |
|---|---|---|
| 静的解析セキュリティスキャン | `harness-verifier/verify.py`（D4 内部整合性 5 項目） | 低（DH は内部整合性のみ、AgentShield は脆弱性検査） |
| Secrets detection | DH 未実装 | 0 |
| Permission auditing | DH 未実装 | 0 |
| Hook risk scoring | DH は hook 機構を採用していないため適用外 | N/A |
| `/security-scan` slash command | DH 未実装 | 0 |
| MCP config audit | `crosscut-verifier-drift` の片鱗 | 低 |

**結論**: AgentShield 級の脆弱性スキャナは DH に不在。本案件で subphase-l05-authz.md に「AgentShield 脆弱性パターン参照モード」として参照導入することは妥当。

---

## 6. DH 方法論での生成手順

AgentShield 級の出力を DH が **ドメイン固有で生成** する手順:

1. **L0 spec-architect 対話で脆弱性要件抽出**: 「保護したい資産」「禁止操作」「権限境界」を `dialog-questions.md` の DONT カテゴリで聴取
2. **subphase-l05-authz.md 起動**: 「AgentShield 脆弱性パターン参照モード」（Phase 2 タスク B で追加）で、ドメイン固有の脆弱性パターン一覧を導出
3. **DONT.md / authz.fga 生成**: 既存 L0-5 サブフェーズの出力に AgentShield 102 ルールを参照しながらドメイン固有ルールを追加
4. **検証方法**: 利用者プロジェクトに `ecc-agentshield` を npm install して `/security-scan` で実行、または DH 自前の D4 verify.py 拡張

---

## 7. 観測注釈

- **ECC 本体と別パッケージ**: AgentShield は `ecc-agentshield` で配布、`ecc-universal`（ECC 本体）とは独立して進化。DH 吸収時も「本体機能と別レイヤ」として扱う妥当性高
- **102 ルール × 1,282 テスト**: ルールあたり平均 12 テスト → high coverage（98% claim）。DH が自前で同等を作る場合はテスト数の確保が課題
- **`--opus --stream`**: Opus model を使った AI advisory は重い処理。DH の Council 機構（重み付き判定 + 物理分離 SDK 呼出）と思想的に類似
- **GitHub Marketplace**: ECC Tools として商用化済（free / pro / enterprise）。DH は方法論 OSS、商用化方針未確定

---

## 8. リスクと注視点

- **`--fix` 自動修復の危険性**: 破壊的変更可能 → DH 方法論では `human-review-needed` ラベル相当の human approval が必須
- **102 ルールの更新追従**: AgentShield 自身がアップデートされる度に DH カタログも更新必要 → 6 ヶ月毎の再観察で対応
- **ライセンス**: `ecc-agentshield` の license 確認未完（本ファイルでは ECC 本体 MIT としか確認できていない、npm package metadata 要確認）

---

**TODO**（Council 議題 1 採決後）:
- 正式パス移動
- AgentShield npm package の license 確認（`npm view ecc-agentshield license`）
- 102 ルールのカテゴリ別分布を完全化（現状は粗分類のみ）
- DH 自前の脆弱性スキャナ実装是非を別議題化（v6.0.0 候補）
