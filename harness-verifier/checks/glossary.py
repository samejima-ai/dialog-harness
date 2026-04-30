"""検証 5: 用語辞書整合

glossary.yml 定義語（forbidden_uses 含む）が DH 全 skill で正しく使われているかを検査。

検出対象:
    - forbidden_uses に列挙された禁則語が SKILL.md / references で使われていたら FAIL
    - crosscut_prefix.members / layern_prefix.members に列挙されない skill が見つかったら FAIL
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import re


# 簡易 YAML パーサ（標準ライブラリ縛り、subset YAML 専用）
#
# 設計判断（AD-014, BOUNDARY.md §独立性の代償）:
#   harness-verifier の独立性要請（外部依存ゼロ）の代償として、glossary.yml は
#   "subset YAML" 形式に限定する。一般の YAML 1.1/1.2 を網羅実装すると保守困難性が
#   増し、再帰バグ（C-1 のような偽陽性）が周期的に発生するため。
#
# 対応構文（subset YAML）:
#     - key: value         （key-value）
#     - key:               （次行 indent でネスト dict 開始）
#         sub_key: value
#     - インラインリスト: [a, b, c] / ["a", "b"]
#     - インライン list of dict: [{key: val}, {key: val}]
#     - 複数行（block）にまたがるリスト構文 `- item` は **使用禁止**
#       検出時は明示的に SyntaxError を発生させる（黙って誤読しない）
#
# 対応外:
#     - YAML 1.2 anchor (&) / merge (<<) / multi-document (---) / block scalar (| / >)


def load_glossary(path: Path) -> dict[str, Any]:
    """glossary.yml を subset YAML 形式でパースする。形式違反時は SyntaxError"""
    text = path.read_text(encoding="utf-8")
    return _parse_yaml(text, source=str(path))


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _split_top_level(s: str, sep: str = ",") -> list[str]:
    """ネスト構造（[]、{}）を尊重しつつトップレベル sep で分割する"""
    parts: list[str] = []
    depth = 0
    current = []
    in_quote: str | None = None
    for ch in s:
        if in_quote is not None:
            current.append(ch)
            if ch == in_quote:
                in_quote = None
            continue
        if ch in ('"', "'"):
            in_quote = ch
            current.append(ch)
            continue
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        last = "".join(current).strip()
        if last:
            parts.append(last)
    return parts


def _parse_inline_value(value: str) -> Any:
    """インライン値（scalar / list / dict）をパースする"""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_inline_value(p) for p in _split_top_level(inner, ",")]
    if value.startswith("{") and value.endswith("}"):
        inner = value[1:-1].strip()
        if not inner:
            return {}
        result: dict[str, Any] = {}
        for kv in _split_top_level(inner, ","):
            colon = kv.find(":")
            if colon < 0:
                continue
            key = _strip_quotes(kv[:colon]).strip()
            val = kv[colon + 1:].strip()
            result[key] = _parse_inline_value(val)
        return result
    return _coerce(value)


def _parse_yaml(text: str, source: str = "<glossary>") -> dict[str, Any]:
    lines = text.splitlines()
    root: dict[str, Any] = {}
    # スタックは (indent, container, last_key) のタプル
    stack: list[tuple[int, Any, str | None]] = [(-1, root, None)]

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # ★ 複数行リスト構文（block list）の使用禁止チェック（AD-014）
        if stripped.startswith("- "):
            raise SyntaxError(
                f"{source}:{line_no}: block list syntax (`- item`) is forbidden in subset YAML. "
                f"Use inline list form instead: `key: [a, b, c]` or `key: [{{key: val}}, ...]`. "
                f"See harness-verifier/BOUNDARY.md '独立性の代償' and AD-014."
            )

        indent = len(raw) - len(raw.lstrip(" "))

        # スタックを現在 indent まで巻き戻す
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            stack = [(-1, root, None)]
        parent_indent, parent, parent_key = stack[-1]
        container = parent

        # "key: value" 形式
        # value 部にインラインリスト/dict が来てもよいよう、最初の : だけで分割
        colon = stripped.find(":")
        if colon < 0:
            continue
        key = stripped[:colon].strip()
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_=-]*$", key):
            continue
        value = stripped[colon + 1:].strip()

        if not isinstance(container, dict):
            continue

        if value == "":
            container[key] = {}
            stack.append((indent, container[key], None))
            stack[-2] = (parent_indent, parent, key)
        else:
            container[key] = _parse_inline_value(value)
            stack[-1] = (parent_indent, parent, key)

    return root


def _coerce(value: str) -> Any:
    value = _strip_quotes(value.strip())
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() == "null" or value == "~":
        return None
    if re.match(r"^-?\d+$", value):
        try:
            return int(value)
        except ValueError:
            return value
    if re.match(r"^-?\d+\.\d+$", value):
        try:
            return float(value)
        except ValueError:
            return value
    return value


def collect_md_files(skills_dir: Path) -> list[Path]:
    return sorted(skills_dir.rglob("*.md"))


def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    repo_root = skills_dir.parent.parent

    try:
        glossary = load_glossary(glossary_path)
    except Exception as exc:  # noqa: BLE001
        issues.append({
            "location": str(glossary_path.relative_to(repo_root)),
            "message": f"failed to parse glossary: {type(exc).__name__}: {exc}",
            "severity": "ERROR",
        })
        return issues

    # 1) 禁則語の使用検出
    forbidden = glossary.get("forbidden_uses", []) or []
    for entry in forbidden:
        if not isinstance(entry, dict):
            continue
        term = entry.get("term", "")
        reason = entry.get("reason", "")
        if not term:
            continue
        # 単語境界で検査（部分一致による誤検出回避）
        # ハイフンを含む term はそのまま、英数字単独語は word boundary で囲む
        if re.match(r"^[A-Za-z0-9_-]+$", term):
            pattern = re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(term)}(?![A-Za-z0-9_-])")
        else:
            pattern = re.compile(re.escape(term))

        for md in collect_md_files(skills_dir):
            # glossary.yml 自身は除外（定義箇所なので当然出現する）
            if md == glossary_path:
                continue
            try:
                text = md.read_text(encoding="utf-8")
            except OSError:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    issues.append({
                        "location": f"{md.relative_to(repo_root)}:{line_no}",
                        "message": f"forbidden term used: {term!r} (reason: {reason})",
                        "severity": "FAIL",
                    })

    # 2) crosscut_prefix.members / layern_prefix.members と実ディレクトリの整合
    skill_dirs = {p.name for p in skills_dir.iterdir() if p.is_dir()}
    crosscut_def = glossary.get("crosscut_prefix", {}) or {}
    layern_def = glossary.get("layern_prefix", {}) or {}
    declared = set()
    for members in (crosscut_def.get("members") or [], layern_def.get("members") or []):
        if isinstance(members, list):
            declared.update(members)

    if declared:
        # 宣言にあって実体が無い
        for name in sorted(declared - skill_dirs):
            issues.append({
                "location": str(glossary_path.relative_to(repo_root)),
                "message": f"glossary declares skill {name!r} but directory does not exist",
                "severity": "FAIL",
            })
        # 実体があって宣言に無い（未管理 skill）
        managed_prefixes = ("layer", "crosscut-")
        for name in sorted(skill_dirs - declared):
            if name.startswith(managed_prefixes):
                issues.append({
                    "location": f".claude/skills/{name}/",
                    "message": f"skill {name!r} exists but not declared in glossary members",
                    "severity": "WARN",
                })

    return issues
