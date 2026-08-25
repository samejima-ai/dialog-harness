"""検査 7: 実行グラフ（GRAPH.yml）と実装の整合

upgrade-spec-v6.12.0 の F2。既存 `dependency_graph.py` が skill 間の**参照**リンク
（dead link / 自己参照）を見るのに対し、本検査は**起動**グラフを見る。両者は別責務。

検査項目:
    G-1 すべての loop エッジが max_iterations を持つ            → FAIL
    G-2 すべての impl / source パスが実在する                    → FAIL
    G-3 すべての conditional エッジが condition を持つ           → FAIL
    G-4 loop を除いた部分グラフが DAG である（循環なし）         → FAIL
    G-5 実装側に存在する起動経路が GRAPH.yml に宣言されている    → WARN（初版）

G-5 が WARN 止まりである理由（upgrade-spec F2-2 / Council 66e3d9 争点 2）:
    実装側の起動記述は自然文を含み誤検出が避けられない。いきなり FAIL にすると DH 自身の
    CI が停止し開発が止まる。FAIL 昇格は「6 cycle 連続で誤検出 0 件」を条件に別途判断する。

    ただし 3 軸が独立に到達したとおり、**空文化を決めるのは判定強度ではなく計数されるか
    否か**である。よって本検査は WARN 件数と誤検出件数を必ず出力する（F2-5）。誤検出の
    判定そのものは人間に残す（GRAPH.yml の `g5_false_positives:` に人間が記録し、本検査は
    それを数えるだけ）。測定主体 = verify.py / 記録先 = harness-verifier/reports/<YYYY-MM>.md。

責務（対象外）:
    - グラフが「正しい設計か」の評価（I-1: 本ファイルは判定を持たない）
    - 実装の自動修正（I-2: 実装が正・宣言が従。検出のみ・是正は L0/人間）

外部依存ゼロ（BOUNDARY.md §独立性要請）。PyYAML は使わず subset パーサで読む。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import re


# GRAPH.yml が取る形は「トップレベルのスカラー」＋「nodes / edges の flat dict リスト」に
# 限定する（glossary.py と同じ subset YAML 方針）。一般 YAML を実装しない。
_SCALAR = re.compile(r"^([a-z_][a-z0-9_]*):\s*(.*)$")
_ITEM_START = re.compile(r"^  - ([a-z_][a-z0-9_]*):\s*(.*)$")
_ITEM_FIELD = re.compile(r"^    ([a-z_][a-z0-9_]*):\s*(.*)$")
_LIST_ITEM = re.compile(r"^  - (.*)$")

# 起動を示す語。SKILL.md 本文でこれらと skill id が同一行に現れたら「起動経路の記述」とみなす。
_INVOKE_WORDS = ("起動", "委譲", "呼び出", "呼ぶ", "発動")
# 明示的な否定。同一行にあれば起動経路として数えない（誤検出の主要因）。
_NEGATIONS = ("しない", "せず", "禁止", "不要", "避け", "ではない", "対象外", "混同")


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] in ("'", '"'):
        quote = v[0]
        end = v.find(quote, 1)
        if end != -1:
            return v[1:end]
    # 行末コメントを剥がす（GRAPH.yml も注釈を常用する）
    v = re.sub(r"\s+#.*$", "", v).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


def parse_graph(text: str) -> dict[str, Any]:
    """GRAPH.yml の subset を読む。トップレベルスカラー + nodes/edges + 文字列リスト。"""
    doc: dict[str, Any] = {}
    section: str | None = None
    current: dict[str, str] | None = None

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        m_scalar = _SCALAR.match(raw)
        if m_scalar:
            key, val = m_scalar.group(1), m_scalar.group(2)
            if current is not None and section:
                doc.setdefault(section, []).append(current)
                current = None
            if val.strip() == "":
                section = key
                doc.setdefault(section, [])
            else:
                section = None
                doc[key] = _unquote(val)
            continue

        if section is None:
            continue

        m_item = _ITEM_START.match(raw)
        if m_item:
            if current is not None:
                doc.setdefault(section, []).append(current)
            current = {m_item.group(1): _unquote(m_item.group(2))}
            continue

        m_field = _ITEM_FIELD.match(raw)
        if m_field and current is not None:
            current[m_field.group(1)] = _unquote(m_field.group(2))
            continue

        m_list = _LIST_ITEM.match(raw)
        if m_list and current is None:
            doc.setdefault(section, []).append(_unquote(m_list.group(1)))

    if current is not None and section:
        doc.setdefault(section, []).append(current)
    return doc


def _path_of(source: str) -> str:
    """source は "path#section" 形式を許す。実在検査はパス部のみ。"""
    return source.split("#", 1)[0].strip()


def _check_g1_g3(edges: list[dict[str, str]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for idx, e in enumerate(edges):
        label = f"edges[{idx}] {e.get('from', '?')} -> {e.get('to', '?')}"
        etype = e.get("type")
        if etype not in ("standard", "conditional", "loop"):
            issues.append({
                "location": f"GRAPH.yml {label}",
                "message": f"type が不正: {etype!r}（standard / conditional / loop のいずれか）",
                "severity": "FAIL",
            })
            continue
        if etype == "loop" and not e.get("max_iterations"):
            issues.append({
                "location": f"GRAPH.yml {label}",
                "message": "G-1: loop エッジに max_iterations がない。"
                           "上限のないループを宣言してはならない（F1-4）",
                "severity": "FAIL",
            })
        if etype == "conditional" and not e.get("condition"):
            issues.append({
                "location": f"GRAPH.yml {label}",
                "message": "G-3: conditional エッジに condition がない（F1-3）",
                "severity": "FAIL",
            })
    return issues


def _check_g2(repo_root: Path, nodes: list[dict[str, str]], edges: list[dict[str, str]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for idx, n in enumerate(nodes):
        impl = n.get("impl")
        if not impl:
            issues.append({
                "location": f"GRAPH.yml nodes[{idx}] {n.get('id', '?')}",
                "message": "G-2: impl（実体パス）がない",
                "severity": "FAIL",
            })
            continue
        if not (repo_root / impl).exists():
            issues.append({
                "location": f"GRAPH.yml nodes[{idx}] {n.get('id', '?')}",
                "message": f"G-2: impl のパスが実在しない: {impl}",
                "severity": "FAIL",
            })
    for idx, e in enumerate(edges):
        src = e.get("source")
        label = f"edges[{idx}] {e.get('from', '?')} -> {e.get('to', '?')}"
        if not src:
            issues.append({
                "location": f"GRAPH.yml {label}",
                "message": "G-2: source（宣言の出典）がない",
                "severity": "FAIL",
            })
            continue
        if not (repo_root / _path_of(src)).exists():
            issues.append({
                "location": f"GRAPH.yml {label}",
                "message": f"G-2: source のパスが実在しない: {_path_of(src)}",
                "severity": "FAIL",
            })
    return issues


def _check_g4(nodes: list[dict[str, str]], edges: list[dict[str, str]]) -> list[dict[str, Any]]:
    """loop を除いた部分グラフが DAG か（philosophy 第 1 条 §依存トポロジーの追跡可能性）。"""
    ids = {n.get("id") for n in nodes if n.get("id")}
    adj: dict[str, list[str]] = {i: [] for i in ids}
    issues: list[dict[str, Any]] = []

    for idx, e in enumerate(edges):
        f, t = e.get("from"), e.get("to")
        label = f"edges[{idx}] {f} -> {t}"
        for endpoint, side in ((f, "from"), (t, "to")):
            if endpoint not in ids:
                issues.append({
                    "location": f"GRAPH.yml {label}",
                    "message": f"G-2: {side} が nodes に未定義: {endpoint!r}",
                    "severity": "FAIL",
                })
        if e.get("type") == "loop":
            continue  # loop は意図された循環。DAG 判定から除外する
        if f in adj and t in ids:
            adj[f].append(t)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = dict.fromkeys(adj, WHITE)
    cycle: list[str] = []

    def visit(node: str, path: list[str]) -> bool:
        color[node] = GRAY
        for nxt in adj.get(node, []):
            if color.get(nxt) == GRAY:
                cycle.extend([*path, node, nxt])
                return True
            if color.get(nxt) == WHITE and visit(nxt, [*path, node]):
                return True
        color[node] = BLACK
        return False

    for node in sorted(adj):
        if color[node] == WHITE and visit(node, []):
            issues.append({
                "location": "GRAPH.yml edges",
                "message": "G-4: loop を除いた部分グラフに循環がある: " + " -> ".join(cycle),
                "severity": "FAIL",
            })
            break
    return issues


def _check_g5(
    skills_dir: Path, nodes: list[dict[str, str]], edges: list[dict[str, str]],
    false_positives: set[str],
) -> tuple[list[dict[str, Any]], int, int]:
    """実装側の起動記述のうち GRAPH.yml に未宣言のものを WARN で列挙する。

    返り値: (issues, 検出件数, 誤検出として除外した件数)
    """
    skill_ids = {n["id"] for n in nodes if n.get("id", "").startswith(("layer", "crosscut"))}
    declared = {(e.get("from"), e.get("to")) for e in edges}

    issues: list[dict[str, Any]] = []
    detected = 0
    excluded = 0

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name not in skill_ids:
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        try:
            lines = skill_md.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue

        seen: set[str] = set()
        for lineno, line in enumerate(lines, start=1):
            if not any(w in line for w in _INVOKE_WORDS):
                continue
            if any(neg in line for neg in _NEGATIONS):
                continue
            for target in skill_ids:
                if target == skill_dir.name or target in seen:
                    continue
                if target not in line:
                    continue
                if (skill_dir.name, target) in declared:
                    continue
                key = f"{skill_dir.name}->{target}"
                seen.add(target)
                if key in false_positives:
                    excluded += 1
                    continue
                detected += 1
                issues.append({
                    "location": f"{skill_dir.name}/SKILL.md:{lineno}",
                    "message": f"G-5: 未宣言の起動経路の疑い: {key}"
                               "（誤検出なら GRAPH.yml の g5_false_positives に記録する）",
                    "severity": "WARN",
                })
    return issues, detected, excluded


def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:  # noqa: ARG001
    repo_root = skills_dir.parent.parent
    graph_path = repo_root / "GRAPH.yml"

    # F2-4: GRAPH.yml 不在のリポジトリでは skip（利用者プロジェクトで壊れない・後方互換）
    if not graph_path.is_file():
        return []

    try:
        doc = parse_graph(graph_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [{"location": "GRAPH.yml", "message": f"読み取り失敗: {exc}", "severity": "ERROR"}]

    nodes = [n for n in doc.get("nodes", []) if isinstance(n, dict)]
    edges = [e for e in doc.get("edges", []) if isinstance(e, dict)]
    false_positives = {f for f in doc.get("g5_false_positives", []) if isinstance(f, str)}

    if not nodes or not edges:
        return [{
            "location": "GRAPH.yml",
            "message": "nodes / edges が読めない（subset YAML 形式を満たしていない可能性）",
            "severity": "FAIL",
        }]

    issues: list[dict[str, Any]] = []
    issues += _check_g1_g3(edges)
    issues += _check_g2(repo_root, nodes, edges)
    issues += _check_g4(nodes, edges)

    g5_issues, detected, excluded = _check_g5(skills_dir, nodes, edges, false_positives)
    issues += g5_issues

    # F2-5: 計数を必ず出力する。「数えられない WARN は最初から飾りである」。
    # severity=METRIC は verify.py の PASS/FAIL 判定に影響しない（FAIL/ERROR/WARN 以外）。
    issues.append({
        "location": "GRAPH.yml g5-metrics",
        "message": f"G-5 計数 — 検出 {detected} 件 / 人間が誤検出と判定済み {excluded} 件 / "
                   f"nodes {len(nodes)} / edges {len(edges)}。"
                   "FAIL 昇格条件は「6 cycle 連続で検出 0 件」（誤検出除外後）",
        "severity": "METRIC",
    })
    return issues
