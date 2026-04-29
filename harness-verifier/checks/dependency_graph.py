"""検証 3: SK 間依存グラフ循環

skill 間の参照（`../{skill-name}/SKILL.md` または `../{skill-name}/references/...`）
からグラフを構築する。

スコープ調整（v0.1.0）:
    DH 設計上、skill 間相互参照（layer0 ⇄ layer1 の handoff 等）は意図的な構造であり
    ファイル参照グラフ上の「循環」≠ 機能的循環。よって本検査は以下に絞る:

      (a) 未定義 skill への参照（dead link 系の派生）
      (b) skill 自身が直接自分自身を参照する (../A/ in skill A) — typo 検出

    意図された相互参照は WARN にも出さない。

責務（必達）:
    - 参照先 skill が実在しなければ FAIL
    - 自己参照（A→A）は WARN
    - skill 間の正常な相互参照は無視

責務（対象外、BOUNDARY.md §4）:
    - 機能的循環の判定（D5 領域）
    - 設計妥当性の評価（crosscut-verifier-philosophy 領域、v5.3.0 候補）
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import re


# 厳格化: skill ディレクトリ参照と認められるのは以下のみ
#   ../{skill-name}/SKILL.md
#   ../{skill-name}/references/...
#   ../{skill-name}/assets/...
SKILL_REF_RE = re.compile(
    r"\.\./([a-z][a-z0-9]*(?:-[a-z0-9]+)*)/(?:SKILL\.md|references/|assets/)"
)


def build_graph(skills_dir: Path) -> tuple[dict[str, set[str]], list[tuple[str, str, Path, int]]]:
    """( {skill: {refs}}, [(skill, self_ref, file, line_no), ...] )"""
    graph: dict[str, set[str]] = {}
    self_refs: list[tuple[str, str, Path, int]] = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name
        graph.setdefault(name, set())
        md_files = list(skill_dir.rglob("*.md"))
        for md in md_files:
            try:
                text = md.read_text(encoding="utf-8")
            except OSError:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                for match in SKILL_REF_RE.finditer(line):
                    ref = match.group(1)
                    if ref == name:
                        self_refs.append((name, ref, md, line_no))
                    else:
                        graph[name].add(ref)
    return graph, self_refs


def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:  # noqa: ARG001
    issues: list[dict[str, Any]] = []
    repo_root = skills_dir.parent.parent
    graph, self_refs = build_graph(skills_dir)

    # (a) 存在しない skill への参照
    known = set(graph.keys())
    for src in sorted(graph.keys()):
        for t in sorted(graph[src]):
            if t not in known:
                issues.append({
                    "location": f".claude/skills/{src}/",
                    "message": f"references unknown skill: ../{t}/",
                    "severity": "FAIL",
                })

    # (b) 自己参照（typo 検出）
    for skill_name, _ref, md_path, line_no in self_refs:
        issues.append({
            "location": f"{md_path.relative_to(repo_root)}:{line_no}",
            "message": f"skill {skill_name!r} references itself via ../{skill_name}/ (likely typo, use relative paths within own skill)",
            "severity": "WARN",
        })

    return issues
