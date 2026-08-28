#!/usr/bin/env python3
"""
Hook observation writer (PR #76, Wave 1 Phase C)

Appends a JSONL observation entry to harness-verifier/reports/hook-observations.jsonl.
Called by bootstrap.py with positional arg = event-type, stdin = JSON payload.

Always exits 0 — warn-only, never block.
"""

import json
import os
import sys
import time
from pathlib import Path


def repo_root() -> Path:
    """Walk up from this script's parent directory looking for repo markers.

    The previous implementation started from ``Path(__file__).resolve()`` (a file
    path), which wasted the first iteration on a check against the script file
    itself, and fell back to ``parents[4]`` — a fragile assumption that only
    holds for the standard ``.claude/skills/<skill>/scripts/`` layout. For
    non-standard installs (e.g. ``~/.claude/skills/...`` user-scope), the
    fallback silently landed in an unrelated ancestor directory.

    Now starts from the script's parent directory and falls back to
    ``Path.cwd()`` so that, when no repo marker is found, logs land somewhere
    discoverable rather than buried in an unrelated tree. Aligns with
    philosophy 第 6 条 "warn-only, never block" — never raises.
    """
    p = Path(__file__).resolve().parent
    for _ in range(8):
        if (p / ".git").exists() or (p / "harness-verifier").is_dir():
            return p
        if p.parent == p:
            break
        p = p.parent
    return Path.cwd()


MAX_FIELD_LEN = 512

# フィールド許可リスト（v6.15.x hook 配線修理・Council 諮問済み）。
#
# 旧実装は payload 全フィールドを 512 字 truncate で記録していた。配線が生きると
# last_assistant_message（応答本文）/ tool_input / tool_response（ファイル内容・コマンド断片）が
# 観測ファイルへ流れる —— 内容を含む観測は公開リポジトリ・配布の両文脈で漏出経路になる
# （chore(privacy) #199 / council-data プライバシー規約 / v6.14.0 F2 公開安全と同旨）。
# 以後は **内容フリーの計量メタデータのみ** を記録する（allowlist 方式・未知キーは既定で落ちる）。
#
# 論文根拠（ANALYSIS-agentic-sdlc-world-standard / 調査⑤）: 軌跡診断に効くのは
# 行動列・duration・成否・イベント種であり、内容そのものは L0 生ログ（transcript）側に既に在る。
ALLOWED_FIELDS = {
    "hook_event_name",     # 冗長だが照合用
    "permission_mode",     # default/plan/acceptEdits/... （内容を含まない）
    "stop_hook_active",    # Stop ループ検知（公式推奨のガード対象）
    "source",              # SessionStart: startup/resume/clear/compact/fork
    "reason",              # SessionEnd: clear/resume/logout/prompt_input_exit/other
    "trigger",             # PreCompact: manual/auto
    "duration_ms",         # PostToolUse: 実行時間（軌跡診断の一次計量）
    "agent_type",          # subagent 文脈
    "prompt_id",           # ターン相関 id（内容を含まない）
    "_parse_error",        # 自己診断
    "_read_error",
    "_raw_len",
    "_smoke_test",         # 既存 smoke エントリとの互換
    "_wave",
    "_purpose",
}


def _truncate(value: object) -> object:
    if isinstance(value, str) and len(value) > MAX_FIELD_LEN:
        return value[:MAX_FIELD_LEN] + "...[truncated]"
    if isinstance(value, dict):
        return {k: _truncate(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_truncate(v) for v in value[:32]]
    return value


def main() -> int:
    if len(sys.argv) < 2:
        return 0
    event = sys.argv[1]

    raw = ""
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {"_parse_error": True, "_raw_len": len(raw)}
    except Exception:
        payload = {"_read_error": True}

    try:
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": event,
            "tool": payload.get("tool_name") or payload.get("tool"),
            "session_id": payload.get("session_id"),
            # 許可リスト外のキーは記録しない（内容フリー保証。dropped 数だけ残す）
            "fields": _truncate({k: v for k, v in payload.items() if k in ALLOWED_FIELDS}),
            "dropped": len([k for k in payload if k not in ALLOWED_FIELDS
                            and k not in ("tool_name", "tool", "session_id")]),
        }
        log_dir = repo_root() / "harness-verifier" / "reports"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "hook-observations.jsonl"
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
