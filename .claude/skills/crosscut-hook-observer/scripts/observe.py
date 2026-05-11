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
    p = Path(__file__).resolve()
    for _ in range(8):
        if (p / ".git").exists() or (p / "harness-verifier").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return Path(__file__).resolve().parents[4]


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

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {"_parse_error": True, "_raw_len": len(raw) if "raw" in dir() else 0}

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

    try:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
