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



# --- v7.0.0 Phase A F1: 不変核 anchor の配線検査 ---
ANCHOR_MD_CANDIDATES = (".claude/anchor-core.md", ".dh/anchor-core.md")
ANCHOR_SCRIPT = "templates/hooks/anchor-core.py"
ANCHOR_MAX_CHARS = 400   # 不変核は 3〜4 条・250 字目安。膨らむと compaction 耐性の利点が消える
ANCHOR_MAX_LINES = 8


def _check_anchor(repo_root: Path) -> list[dict[str, Any]]:
    """anchor-core.md（不変核）と SessionStart hook の配線が対応しているかを見る。

    - md があるのに settings.json の SessionStart が anchor-core.py を呼んでいない → FAIL（注入されない）
    - settings が anchor-core.py を呼ぶのに md も script も無い → WARN（配線だけ残った）
    - md の本文（HTML コメント除く）が上限超過 → FAIL（不変核は小さく保つ。arXiv 2608.12426 k*=2〜4）
    LLM 判定は含まない。
    """
    import re as _re

    issues: list[dict[str, Any]] = []
    md_path = next((repo_root / c for c in ANCHOR_MD_CANDIDATES if (repo_root / c).is_file()), None)
    settings = repo_root / ".claude" / "settings.json"
    wired = False
    if settings.is_file():
        try:
            doc = json.loads(settings.read_text(encoding="utf-8"))
            for entry in (doc.get("hooks", {}) or {}).get("SessionStart", []) or []:
                for h in entry.get("hooks", []) or []:
                    if "anchor-core.py" in str(h.get("command", "")):
                        wired = True
        except (OSError, json.JSONDecodeError):
            pass

    if md_path is not None and not wired:
        issues.append({
            "location": str(md_path.relative_to(repo_root)),
            "message": "anchor-core.md があるが .claude/settings.json の SessionStart が anchor-core.py を呼んでいない（不変核が再注入されない）",
            "severity": "FAIL",
        })
    if wired and not (repo_root / ANCHOR_SCRIPT).is_file():
        issues.append({
            "location": ".claude/settings.json",
            "message": f"SessionStart が anchor-core.py を呼ぶが {ANCHOR_SCRIPT} が無い",
            "severity": "FAIL",
        })
    if wired and md_path is None:
        issues.append({
            "location": ".claude/settings.json",
            "message": "SessionStart が anchor-core.py を呼ぶが anchor-core.md が無い（配線だけ残っている。出力は空で無害）",
            "severity": "WARN",
        })
    if md_path is not None:
        try:
            body = _re.sub(r"<!--.*?-->", "", md_path.read_text(encoding="utf-8"), flags=_re.S).strip()
        except OSError:
            body = ""
        n_lines = len([ln for ln in body.splitlines() if ln.strip()])
        if len(body) > ANCHOR_MAX_CHARS or n_lines > ANCHOR_MAX_LINES:
            issues.append({
                "location": str(md_path.relative_to(repo_root)),
                "message": (f"不変核が大きすぎる: {len(body)} 字 / {n_lines} 行"
                            f"（上限 {ANCHOR_MAX_CHARS} 字 / {ANCHOR_MAX_LINES} 行。3〜4 条に絞る）"),
                "severity": "FAIL",
            })
    return issues


def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:  # noqa: ARG001
    """hook-observations.jsonl の形式整合性を検査する。

    Returns:
        issues: 検出された問題のリスト（空なら PASS）
    """
    repo_root = skills_dir.parent.parent
    log_path = repo_root / "harness-verifier" / "reports" / "hook-observations.jsonl"

    anchor_issues = _check_anchor(repo_root)

    if not log_path.is_file():
        return anchor_issues

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

    return anchor_issues + issues
