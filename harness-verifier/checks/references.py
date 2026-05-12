"""検証 2: 参照 path 有効性

全 SKILL.md / references/*.md / assets/*.md 内の Markdown リンクを追跡し、
リンク切れ（dead link）を検出する。

検出対象:
    - [text](path) 形式の Markdown インラインリンクで、path が相対パスのもの
    - `path` 形式のバッククォート内の相対パス（v5.16.0 追加、./ または ../ 開始のもの）
    - 検査対象拡張子は TRACKED_EXTS（.md / .yml / .yaml / .json / .ts / .py / .feature / .tsp / .fga）
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import re


# Markdown インラインリンク [text](path)
INLINE_LINK_RE = re.compile(r"\[([^\]\n]+)\]\(([^)\n]+)\)")

# 検査対象拡張子（単一情報源）
TRACKED_EXTS = {".md", ".yml", ".yaml", ".json", ".ts", ".py", ".feature", ".tsp", ".fga"}

# バッククォート内の相対パス参照（v5.16.0 追加）
# 検出条件: ./ または ../ で始まり、TRACKED_EXTS の拡張子で終わる
# スコープを ./ ../ 開始に限定する理由:
#   - リポジトリルートからの説明パス (`.claude/skills/...`) は source file からの相対では解決不可能で別機構が必要
#   - ~/ 開始のホームディレクトリ参照、<timestamp> 等のプレースホルダー、* グロブは実在チェック対象外
#   - Copilot が PR #91 で指摘した dead-backtick-link ケース (../layer1-...) は本パターンで完全カバーされる
# 将来拡張: リポジトリルートからの説明パスを resolve するモードは別 minor で検討
_BACKTICK_EXT_PATTERN = "|".join(re.escape(ext.lstrip(".")) for ext in sorted(TRACKED_EXTS))
BACKTICK_PATH_RE = re.compile(
    r"`("
    r"\.{1,2}/[^`\s]+"
    rf"\.(?:{_BACKTICK_EXT_PATTERN})"
    r"(?:#[^`]*)?"
    r")`"
)

# 外部リンク判定
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "ftp://")


def is_external(path: str) -> bool:
    return path.startswith(EXTERNAL_PREFIXES)


def has_tracked_ext(path: str) -> bool:
    p = Path(path.split("#", 1)[0])  # アンカー除去
    return p.suffix.lower() in TRACKED_EXTS


def resolve_link(source_file: Path, link: str) -> Path:
    """source_file から見た相対 link の絶対パスを返す（アンカー除去済み）"""
    target = link.split("#", 1)[0].strip()
    if target.startswith("/"):
        # 絶対パスは検査対象外（CI 環境で意味が変わるため）
        return Path("/__skipped_absolute__")
    return (source_file.parent / target).resolve()


def collect_md_files(skills_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for pattern in ("*/SKILL.md", "*/references/**/*.md", "*/assets/**/*.md"):
        paths.extend(skills_dir.glob(pattern))
    return sorted(set(paths))


def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:  # noqa: ARG001
    issues: list[dict[str, Any]] = []
    repo_root = skills_dir.parent.parent

    for md_path in collect_md_files(skills_dir):
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError as exc:
            issues.append({
                "location": str(md_path.relative_to(repo_root)),
                "message": f"failed to read: {exc}",
                "severity": "ERROR",
            })
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in INLINE_LINK_RE.finditer(line):
                link = match.group(2).strip()
                if is_external(link) or link.startswith("#") or not link:
                    continue
                if not has_tracked_ext(link):
                    continue
                resolved = resolve_link(md_path, link)
                if str(resolved) == "/__skipped_absolute__":
                    continue
                if not resolved.exists():
                    issues.append({
                        "location": f"{md_path.relative_to(repo_root)}:{line_no}",
                        "message": f"dead link (inline): {link} (resolved: {resolved})",
                        "severity": "FAIL",
                    })

            for match in BACKTICK_PATH_RE.finditer(line):
                link = match.group(1).strip()
                if is_external(link) or not link:
                    continue
                resolved = resolve_link(md_path, link)
                if str(resolved) == "/__skipped_absolute__":
                    continue
                if not resolved.exists():
                    issues.append({
                        "location": f"{md_path.relative_to(repo_root)}:{line_no}",
                        "message": f"dead link (backtick): `{link}` (resolved: {resolved})",
                        "severity": "FAIL",
                    })

    return issues
