#!/usr/bin/env python3
"""
Claude Code hook bootstrap (PR #76, Wave 1 Phase C)

origin: ECC v2.0.0-rc.1 hooks/scripts/plugin-hook-bootstrap.js (Node.js)
chewing_translation: T2 (Node.js → Python 翻訳)

Invoked by .claude/hooks.json with one positional arg: event-type.
Reads JSON event payload from stdin, dispatches to observe.py for logging.
Always exits 0 (warn-only, never block) — philosophy.md 第 6 条準拠。
"""

import json
import os
import sys
from pathlib import Path


SUPPORTED_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "Stop",
    "SessionStart",
    "SessionEnd",
    "PreCompact",
}


def main() -> int:
    if len(sys.argv) < 2:
        return 0
    event = sys.argv[1]
    if event not in SUPPORTED_EVENTS:
        return 0

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {"_parse_error": True}

    script_dir = Path(__file__).resolve().parent
    observe = script_dir / "observe.py"
    if not observe.exists():
        return 0

    try:
        import subprocess

        subprocess.run(
            [sys.executable, str(observe), event],
            input=json.dumps(payload),
            text=True,
            check=False,
            timeout=2,
        )
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
