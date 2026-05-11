# Hook 観測ログ出力規格

`harness-verifier/reports/hook-observations.jsonl` の JSONL スキーマ定義。

## 1 行 = 1 observation entry

```jsonc
{
  "ts": "2026-05-11T05:30:00Z",   // ISO 8601 UTC、observe.py 実行時刻
  "event": "PreToolUse",            // 5 event のいずれか
  "tool": "Bash",                   // tool name（PreToolUse/PostToolUse のみ、それ以外は null）
  "session_id": "abc123",           // Claude Code 提供の session UUID
  "fields": {                       // event 固有データ（512 char で truncate）
    "command": "git status",
    "exit_code": 0
  }
}
```

## event 別フィールド

| event | tool | 主要 fields |
|---|---|---|
| `PreToolUse` | Bash / Write / Edit / ... | `command`, `file_path`, `params` 等（tool 依存） |
| `PostToolUse` | 同上 | `exit_code`, `output_truncated`, `error` 等 |
| `Stop` | null | `reason`, `final_message_excerpt` |
| `SessionStart` | null | `cwd`, `env_vars_truncated` |
| `SessionEnd` | null | `duration_sec`, `tool_call_count` |

## 設計原則

### Append-only

ログは append-only。書き換え・削除は禁止。harness-verifier の D5 監視層が
「観測の連続性」を検証できることが前提（philosophy.md 5 次元 D5）。

### Truncation

各 field 値は 512 char で truncate（`MAX_FIELD_LEN`）。
list は 32 要素で truncate。
これは観測ログのサイズを抑制し、harness-verifier の読み取りコストを一定に保つため。

### Fail-open

observe.py / bootstrap.py のいかなる失敗（JSON parse error / file write error / etc）も
**exit code 0** で帰る。Claude Code セッションをブロックしない（philosophy.md 第 6 条
「人間最終承認」準拠 + harness-verifier 独立性原則）。

## harness-verifier 側の読み取り規約（Wave 2 以降の予定）

**Wave 1 段階では `harness-verifier/verify.py` に hook 観測ログの読み取り実装は含まれない**。本 PR 範囲は観測ログ JSONL の生成までで、消費側は将来実装する設計の骨格として記録する。

Wave 2 で候補 5（continuous-learning v2.1）取り込みと同時に、以下の仕様で読み取り経路を実装予定:

1. 末尾 N 行を読む（N は config 化候補、暫定 1000）
2. JSONL parse error 行は無視
3. event / tool / session_id のパターン分析を verify.py の D5 観測項目に組み込む
4. 観測結果は `harness-verifier/reports/<run-id>.md` に独立出力（observation ファイルは改変しない）

これにより skill → 観測ログ → verifier の一方向依存が保持される（独立性原則）。

Wave 1 のスコープでは観測ログは「将来の消費者に向けて蓄積される素材」として機能し、ログ自体の append-only 性質と fail-open 契約が独立性原則を予防的に保証する。

## バージョン

- v0.1.0（Wave 1）— 5 event + 基本 fields + 512 char truncate + fail-open
- 拡張候補（Wave 2 以降）:
  - field schema の event-type 別厳密化（JSON Schema 化）
  - 観測ログの rotation / archival（サイズ上限到達時）
  - continuous-learning v2.1 連携（候補 5、観測 → instinct promotion 経路）
