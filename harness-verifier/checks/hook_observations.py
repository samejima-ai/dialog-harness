"""検証 6: hook 観測一貫性（v5.12.x Wave 2 追加）

`harness-verifier/reports/hook-observations.jsonl` を **読み取り専用** で消費し、
crosscut-hook-observer が生成した観測ログの形式整合性を検査する。

独立性原則:
    - 本検査は観測ログを書き換えない（append-only 維持）
    - 本検査は skill 内部（.claude/skills/crosscut-hook-observer/）に依存しない
    - 観測ログが存在しないこと自体は PASS（hook 未起動状態を許容、fail-open）

検出対象:
    - JSONL 形式違反行（parse error）
    - 必須フィールド欠落（ts / event / 等）
    - 不正な event 値（6 event 以外、Wave 3 で PreCompact 追加）
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SUPPORTED_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "Stop",
    "SessionStart",
    "SessionEnd",
    "PreCompact",
}
REQUIRED_FIELDS = ["ts", "event"]
TAIL_LINES_LIMIT = 1000


def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:  # noqa: ARG001
    """hook-observations.jsonl の形式整合性を検査する。

    Returns:
        issues: 検出された問題のリスト（空なら PASS）
    """
    repo_root = skills_dir.parent.parent
    log_path = repo_root / "harness-verifier" / "reports" / "hook-observations.jsonl"

    if not log_path.is_file():
        return []

    try:
        text = log_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [
            {
                "location": str(log_path.relative_to(repo_root)),
                "message": f"failed to read observation log: {exc}",
                "severity": "FAIL",
            }
        ]

    lines = text.splitlines()
    tail = lines[-TAIL_LINES_LIMIT:] if len(lines) > TAIL_LINES_LIMIT else lines

    issues: list[dict[str, Any]] = []
    parse_errors = 0
    missing_field_errors = 0
    unknown_event_errors = 0

    for idx, line in enumerate(tail, start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            parse_errors += 1
            continue

        for field in REQUIRED_FIELDS:
            if field not in entry:
                missing_field_errors += 1
                break

        event = entry.get("event")
        if event is not None and event not in SUPPORTED_EVENTS:
            unknown_event_errors += 1

    rel_path = log_path.relative_to(repo_root)
    if parse_errors > 0:
        issues.append(
            {
                "location": str(rel_path),
                "message": f"JSONL parse error on {parse_errors} line(s) (out of {len(tail)} tail lines)",
                "severity": "FAIL",
            }
        )
    if missing_field_errors > 0:
        issues.append(
            {
                "location": str(rel_path),
                "message": f"missing required field on {missing_field_errors} entry(s) (required: {REQUIRED_FIELDS})",
                "severity": "FAIL",
            }
        )
    if unknown_event_errors > 0:
        issues.append(
            {
                "location": str(rel_path),
                "message": f"unknown event value on {unknown_event_errors} entry(s) (allowed: {sorted(SUPPORTED_EVENTS)})",
                "severity": "FAIL",
            }
        )

    return issues
