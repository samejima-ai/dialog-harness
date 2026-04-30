"""検証 1: frontmatter 整合性

全 SKILL.md の YAML frontmatter から必須フィールド（name / description）を検査する。
skill-creator 規約に基づき、name は kebab-case、description は 30-1024 chars。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import re


REQUIRED_FIELDS = ["name", "description"]
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
DESCRIPTION_MIN = 30
DESCRIPTION_MAX = 1024


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """SKILL.md の先頭 YAML frontmatter を簡易パースする。

    厳密な YAML 仕様は実装しない。`key: value` 形式と複数行の継続行のみ扱う。
    frontmatter 不在時は None を返す。
    """
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm: dict[str, str] = {}
    current_key: str | None = None
    for idx, line in enumerate(lines[1:], start=1):
        stripped = line.rstrip()
        if stripped.strip() == "---":
            return fm
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", stripped)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            fm[key] = value
            current_key = key
        elif current_key is not None and stripped.startswith((" ", "\t")):
            # 継続行: 既存値に空白区切りで連結
            fm[current_key] = (fm[current_key] + " " + stripped.strip()).strip()
    # 終端 --- が見つからなかった場合
    return None


def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:  # noqa: ARG001
    issues: list[dict[str, Any]] = []
    skill_md_paths = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_md_paths:
        issues.append({
            "location": str(skills_dir),
            "message": "no SKILL.md found under skills directory",
            "severity": "FAIL",
        })
        return issues

    for skill_path in skill_md_paths:
        try:
            text = skill_path.read_text(encoding="utf-8")
        except OSError as exc:
            issues.append({
                "location": str(skill_path),
                "message": f"failed to read: {exc}",
                "severity": "ERROR",
            })
            continue

        fm = parse_frontmatter(text)
        if fm is None:
            issues.append({
                "location": str(skill_path.relative_to(skills_dir.parent.parent)),
                "message": "frontmatter (--- ... ---) missing or unterminated",
                "severity": "FAIL",
            })
            continue

        for field in REQUIRED_FIELDS:
            if field not in fm or not fm[field].strip():
                issues.append({
                    "location": str(skill_path.relative_to(skills_dir.parent.parent)),
                    "message": f"required frontmatter field missing: {field}",
                    "severity": "FAIL",
                })

        name = fm.get("name", "").strip()
        if name:
            if not NAME_PATTERN.match(name):
                issues.append({
                    "location": str(skill_path.relative_to(skills_dir.parent.parent)),
                    "message": f"frontmatter name not kebab-case: {name!r}",
                    "severity": "FAIL",
                })
            expected_name = skill_path.parent.name
            if name != expected_name:
                issues.append({
                    "location": str(skill_path.relative_to(skills_dir.parent.parent)),
                    "message": f"frontmatter name {name!r} does not match directory name {expected_name!r}",
                    "severity": "FAIL",
                })

        description = fm.get("description", "").strip()
        if description:
            length = len(description)
            if length < DESCRIPTION_MIN:
                issues.append({
                    "location": str(skill_path.relative_to(skills_dir.parent.parent)),
                    "message": f"description too short ({length} < {DESCRIPTION_MIN} chars)",
                    "severity": "WARN",
                })
            elif length > DESCRIPTION_MAX:
                issues.append({
                    "location": str(skill_path.relative_to(skills_dir.parent.parent)),
                    "message": f"description too long ({length} > {DESCRIPTION_MAX} chars)",
                    "severity": "FAIL",
                })

    return issues
