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
            "fields": _truncate({k: v for k, v in payload.items() if k not in ("tool_name", "tool", "session_id")}),
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
