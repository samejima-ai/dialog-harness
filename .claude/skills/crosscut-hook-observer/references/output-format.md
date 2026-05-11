# Hook 観測ログ出力規格

`harness-verifier/reports/hook-observations.jsonl` の JSONL スキーマ定義。

## 1 行 = 1 observation entry

```jsonc
{
  "ts": "2026-05-11T05:30:00Z",   // ISO 8601 UTC、observe.py 実行時刻
  "event": "PreToolUse",            // 6 event のいずれか (Wave 3 で PreCompact 追加)
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
| `PreCompact` | null | `trigger`, `transcript_size`（context 圧縮前の状態スナップショット） |

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

## harness-verifier 側の読み取り規約（Wave 2 で実装、検査項目 6「hook 観測一貫性」）

**Wave 2 で `harness-verifier/checks/hook_observations.py` を新設**し、`hook-observations.jsonl` を読み取り専用で消費する:

1. 末尾 1000 行を読む（`TAIL_LINES_LIMIT`）
2. JSONL parse error 行をカウント、検出件数を FAIL として報告
3. 必須フィールド（`ts` / `event`）欠落をカウント
4. 不正な `event` 値（6 event 以外）をカウント
5. 観測結果は `harness-verifier/reports/<YYYY-MM>.md` の検査項目 6 として独立出力（observation ファイルは改変しない）

これにより skill → 観測ログ → verifier の一方向依存が保持される（独立性原則）。

### fail-open 契約

- 観測ログファイル不在 → PASS（hook 未起動状態を許容）
- ファイル読取エラー → FAIL として報告するが、verify.py 自体は exit 0 で完走
- 個別 check 例外は `verify.py` 側で catch、他 check の実行を停止しない

## バージョン

- v0.1.0（Wave 1）— 5 event + 基本 fields + 512 char truncate + fail-open
- v0.2.0（Wave 3 PR #81）— PreCompact event 追加で 6 event (council-w3qb02 B 採決)
- 拡張候補（Wave 2 以降）:
  - field schema の event-type 別厳密化（JSON Schema 化）
  - 観測ログの rotation / archival（サイズ上限到達時）
  - continuous-learning v2.1 連携（候補 5、観測 → instinct promotion 経路）
