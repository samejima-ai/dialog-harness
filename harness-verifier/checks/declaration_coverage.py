"""検査: 宣言の網羅（実体 → 宣言）（v6.18.0 C-2 で検査 8 から分離）

**欠落の型**: 実体→宣言 — 在るものが宣言されているか / 宣言の実質

既存 7 検査は「宣言 → 実体」（宣言したものが在るか）だけを見ており、逆向きを見ていなかった。
skill / script が `GRAPH.yml` に、実在パスが `dh-manifest.yml` に宣言されているかを見る。
併せて `edge.source` が本当に `edge.to` を指しているか（宣言の実質）も見る —
G-2 は source の**パス存在**しか見ないため、実体のない宣言が PASS を通過していた。

## 分割の経緯

Council `council-2026-09-06T15:00:00Z-splt02`（jc 0.85 / 3 軸全会一致）。
検査 8 は v6.17.0 で 6 → 13 項目に増え **672 行**に肥大した。3 軸が独立に同一のバグ
（dict 重複キーによる F4 METRIC の消失・PR #263 で是正）を発見し、
**肥大が実際に見落としを生んだ実証**となったため分割した。

分割基準は当初の申し送りにあった「1 検査器 = 1 宣言ファイル」**ではない**。
F1 は 4 ファイル、F4 は 2 ファイルを読み、F3 は宣言を読まない（実体走査のみ）ため、
宣言ファイル単位では切れないことが実測で判明した。採った基準は
**「1 検査器 = 1 つの欠落の型」**（実体→宣言 / 鮮度 / 実質 / 実体の誤配置）である。

規範メタデータ:
    stage: 全段階
    review_trigger:
      - measured: source 実質検査（WARN）が 6 cycle 連続 0 件なら FAIL 昇格を検討
      - stage_transition: DH が新しい配布面（新ディレクトリ）を持つとき unclassified_ok を見直す
      - measured: 分類網羅 WARN が 6 cycle 連続 0 件なら降格候補
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:  # verify.py 経由（パッケージとして読み込まれる正規経路）
    from ._declaration_util import read_graph, skill_ids_from_graph
except ImportError:  # 単体ロード（scripts/test-*.py が spec_from_file_location で読む）
    import importlib.util as _ilu

    _p = Path(__file__).with_name("_declaration_util.py")
    _s = _ilu.spec_from_file_location("_declaration_util", _p)
    if _s is None or _s.loader is None:
        raise ImportError(f"_declaration_util.py を単体ロードできない: {_p}")
    _m = _ilu.module_from_spec(_s)
    _s.loader.exec_module(_m)
    read_graph, skill_ids_from_graph = _m.read_graph, _m.skill_ids_from_graph

# 層 prefix（SKILL.md 本文では「L1（autonomous-dev）」のように略記される）
_LAYER_PREFIX_RE = re.compile(r"^(?:layer[012]|crosscut)-")


def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:  # noqa: ARG001
    repo_root = skills_dir.parent.parent
    graph_path = repo_root / "GRAPH.yml"
    issues: list[dict[str, Any]] = []

    f2 = _check_f2(repo_root, skills_dir, graph_path, issues)
    f4 = _check_f4(repo_root, skills_dir, graph_path, issues)

    issues.append({
        "location": "GRAPH.yml",
        "message": (f"宣言網羅 — skill {f2['skills']} 件 "
                    f"(node {f2['skill_nodes']} / excluded {f2['skill_excluded']}) / "
                    f"script {f2['scripts']} 件 "
                    f"(impl {f2['script_impls']} / excluded {f2['script_excluded']}) / "
                    f"source 実質検査 {f2['sources_checked']} edge"),
        "severity": "METRIC",
    })
    issues.append({
        "location": "dh-manifest.yml",
        "message": (f"分類網羅 — 分類済み {f4['classified']} パス / "
                    f"未分類 {f4['unclassified']} パス / "
                    f"owned_skills {f4['owned_skills']} 件"
                    f"（GRAPH 宣言 {f4['graph_skills']} 件と突合）"),
        "severity": "METRIC",
    })
    return issues


def _check_f2(
    repo_root: Path, skills_dir: Path, graph_path: Path, issues: list[dict[str, Any]]
) -> dict[str, int]:
    """F2: 実体 → 宣言 の網羅性（検査 7/8）と source の実質（検査 9）。

    GRAPH.yml 不在のリポジトリでは skip する（execution_graph.py F2-4 と同じ後方互換規律）。
    """
    counts = {
        "skills": 0, "skill_nodes": 0, "skill_excluded": 0,
        "scripts": 0, "script_impls": 0, "script_excluded": 0,
        "sources_checked": 0,
    }
    if not graph_path.is_file():
        return counts

    doc = read_graph(graph_path)   # 共通ヘルパ経由（fallback の複製を作らない）
    if not doc:
        return counts

    nodes = [n for n in doc.get("nodes", []) if isinstance(n, dict)]
    edges = [e for e in doc.get("edges", []) if isinstance(e, dict)]
    excluded = [x for x in doc.get("graph_excluded", []) if isinstance(x, dict)]

    node_ids = {n["id"] for n in nodes if n.get("id")}
    node_impls = {n["impl"] for n in nodes if n.get("impl")}
    excluded_ids = {x["id"] for x in excluded if x.get("id")}
    excluded_paths = {x["path"] for x in excluded if x.get("path")}

    # --- 検査 7: skill dir ⊆ (nodes ∪ graph_excluded)。prefix でフィルタしない ---
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if not d.is_dir() or not (d / "SKILL.md").is_file():
                continue
            counts["skills"] += 1
            if d.name in node_ids:
                counts["skill_nodes"] += 1
            elif d.name in excluded_ids:
                counts["skill_excluded"] += 1
            else:
                issues.append({
                    "location": f".claude/skills/{d.name}/",
                    "message": (f"skill {d.name!r} が GRAPH.yml の nodes にも graph_excluded にも無い。"
                                "実体があるものは登録するか、理由付きで除外を宣言する"
                                "（upgrade-spec-v6.17.0 §F2。黙って対象外にしない）"),
                    "severity": "FAIL",
                })

    # --- 検査 8: scripts/*.py（test-* 除く）⊆ (nodes[].impl ∪ graph_excluded[].path) ---
    scripts_dir = repo_root / "scripts"
    if scripts_dir.is_dir():
        for f in sorted(scripts_dir.glob("*.py")):
            if f.name.startswith("test-"):
                continue
            counts["scripts"] += 1
            rel = f"scripts/{f.name}"
            if rel in node_impls:
                counts["script_impls"] += 1
            elif rel in excluded_paths:
                counts["script_excluded"] += 1
            else:
                issues.append({
                    "location": rel,
                    "message": (f"script {f.name!r} が GRAPH.yml の nodes[].impl にも "
                                "graph_excluded[].path にも無い。tool node 化するか除外理由を宣言する"),
                    "severity": "WARN",
                })

    # --- 検査 9: source 実質検査 ---
    # edge.source が .md のとき、その本文に edge.to の impl basename または node id が
    # 出現することを見る。G-2 は source の**パス存在**しか見ないため、実体のない宣言
    # （HV-04: ritual-protocol.md が呼んでいない council-performance への edge）が
    # PASS を通過していた。意味は判定しない — 名前が本文にあるかだけを見る決定論検査。
    impl_by_id = {n["id"]: n.get("impl", "") for n in nodes if n.get("id")}
    for e in edges:
        src, to, frm = e.get("source", ""), e.get("to", ""), e.get("from", "")
        if not src.endswith(".md") or not to:
            continue
        # self-loop は「自分の中の繰り返し」であり、本文が自分の名を呼ぶ形にならない
        # （例: circuit-breaker-spec.md は日次上限を述べるが skill 名は書かない）。
        # 名前の出現で測る本検査の対象外にする。
        if frm == to:
            continue
        src_path = repo_root / src
        if not src_path.is_file():
            continue  # パス実在は G-2 の担当（二重報告しない）
        counts["sources_checked"] += 1
        try:
            body = src_path.read_text(encoding="utf-8")
        except OSError:
            continue
        if _mentions(body, to, impl_by_id.get(to, "")):
            continue
        issues.append({
            "location": src,
            "message": (f"source 実質乖離: edge {frm}->{to} の出典に宣言されているが、"
                        f"本文が {to!r} を指す記述を持たない。"
                        "実装に無い経路を宣言していないか確認する"
                        "（G-2 はパス存在しか見ない。upgrade-spec-v6.17.0 §F2 HV-04）"),
            "severity": "WARN",
        })

    return counts


def _mentions(body: str, node_id: str, impl: str) -> bool:
    """本文が node_id を指す記述を持つか（決定論・意味は判定しない）。

    3 通りの書かれ方を許容する:
      1. node id そのもの（`layer1-autonomous-dev`）
      2. 層 prefix を落とした略記（`autonomous-dev`）— SKILL.md 本文の通常表記
      3. impl の basename（`verify.py` 等。skill の `SKILL.md` は識別子にならないので除く）
    """
    if node_id in body:
        return True
    short = _LAYER_PREFIX_RE.sub("", node_id)
    if short and short != node_id and short in body:
        return True
    basename = Path(impl).name if impl else ""
    return bool(basename and basename != "SKILL.md" and basename in body)


def _parse_manifest_paths(text: str) -> dict[str, list[str]]:
    """dh-manifest.yml の `paths:` 配下を {分類名: [値, ...]} で返す。

    GRAPH.yml 用の parse_graph はネストされた dict を読めないため、manifest 専用の
    最小パーサを持つ。読むのは「`paths:` の直下 2 段」だけで、それ以上の構造は扱わない
    （I-3 決定論・LLM 不使用。正規表現とインデント数えのみ）。
    """
    out: dict[str, list[str]] = {}
    in_paths = False
    current: str | None = None
    for raw in text.splitlines():
        if raw.startswith("paths:"):
            in_paths = True
            continue
        if not in_paths:
            continue
        # インデント 0 の非空行で paths ブロックは終わり
        if raw.strip() and not raw.startswith(" ") and not raw.startswith("#"):
            break
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 2 and stripped.endswith(":"):
            current = stripped[:-1]
            out[current] = []
        elif indent >= 4 and stripped.startswith("- ") and current:
            val = stripped[2:].split("#", 1)[0].strip().strip('"').strip("'")
            if val:
                out[current].append(val)
    return out


def _check_f4(repo_root: Path, skills_dir: Path, graph_path: Path,
              issues: list[dict[str, Any]]) -> dict[str, int]:
    """F4: dh-manifest の分類網羅（検査 11）と owned_skills の GRAPH 一致（検査 12）。

    検査 11: リポジトリ直下および `.claude/` 直下の実在パスが 4 分類 ∪ owned_skills ∪
        unclassified_ok のいずれかに属すること（属さない = WARN）。
        「明示列挙しない = 既定で不可侵」は運用として成立するが、**DH が配布したいものが
        黙って不可侵に落ちる**事故（v6.17.0 が (d) として検出した `.claude/agents/`）を
        検出できない。

    検査 12: `paths.owned_skills` を **GRAPH.yml nodes（単一情報源）と実在 dir の両方**へ
        突合する（不一致 = FAIL）。Council D-4 必須随伴条件 (a) と (c)。

        (c) が「単一情報源は GRAPH.yml nodes」と定めるため、owned_skills は第一に
        GRAPH nodes（+ graph_excluded）と一致していなければならない。実在 dir との突合も
        併せて行うのは、GRAPH 自体が実体から離れる可能性を検査 7 だけに委ねないため
        （検査 7 は「実体 → GRAPH」を見る。ここは「GRAPH → manifest」を見る）。
        三者が閉じることで、列挙漏れという「静かな失敗」（配布されないまま誰も困らない）を塞ぐ。
    """
    counts = {"classified": 0, "unclassified": 0, "owned_skills": 0, "graph_skills": 0}
    manifest = repo_root / "dh-manifest.yml"
    if not manifest.is_file():
        return counts  # 配布先など manifest を持たないツリーでは skip（I-6）

    paths = _parse_manifest_paths(manifest.read_text(encoding="utf-8"))
    if not paths:
        issues.append({
            "location": "dh-manifest.yml",
            "message": "paths: 配下の分類が読めない（4 分類の宣言が失われている可能性）",
            "severity": "FAIL",
        })
        return counts

    # --- 検査 12: owned_skills ⇄ GRAPH nodes（単一情報源）⇄ 実在 skill dir ---
    owned = set(paths.get("owned_skills", []))
    counts["owned_skills"] = len(owned)

    # (c) 単一情報源は GRAPH.yml nodes。まずそちらと突合する。
    if graph_path.is_file():
        doc = read_graph(graph_path)
        # skill node の判定は共通ヘルパに集約（prefix で絞らない理由も同ヘルパに記載）
        declared = skill_ids_from_graph(doc)
        counts["graph_skills"] = len(declared)

        for name in sorted(declared - owned):
            issues.append({
                "location": "dh-manifest.yml",
                "message": (f"GRAPH.yml が skill {name!r} を宣言しているのに "
                            "paths.owned_skills に無い。列挙漏れは「配布されないまま誰も困らない」"
                            "静かな失敗になる（Council D-4 必須随伴条件 a / 単一情報源は GRAPH nodes = 同 c）"),
                "severity": "FAIL",
            })
        for name in sorted(owned - declared):
            issues.append({
                "location": "dh-manifest.yml",
                "message": (f"paths.owned_skills の {name!r} が GRAPH.yml に無い。"
                            "owned_skills は GRAPH nodes からの導出であり、単独で増やさない（同 c）"),
                "severity": "FAIL",
            })

    # 実在 dir とも突合する（GRAPH 自体が実体から離れる可能性を検査 7 だけに委ねない）
    if skills_dir.is_dir():
        actual = {d.name for d in skills_dir.iterdir()
                  if d.is_dir() and (d / "SKILL.md").is_file()}
        for name in sorted(actual - owned):
            issues.append({
                "location": f".claude/skills/{name}/",
                "message": (f"skill {name!r} が dh-manifest.yml の paths.owned_skills に無い。"
                            "列挙漏れは「配布されないまま誰も困らない」静かな失敗になる"
                            "（upgrade-spec-v6.17.0 §F4 / Council D-4 必須随伴条件 a）"),
                "severity": "FAIL",
            })
        for name in sorted(owned - actual):
            issues.append({
                "location": "dh-manifest.yml",
                "message": (f"paths.owned_skills が実在しない skill {name!r} を列挙している。"
                            "削除・改名に追随する"),
                "severity": "FAIL",
            })

    # --- 検査 11: 分類網羅 ---
    classified: set[str] = set()
    for key in ("overwrite", "merge", "redeploy", "never_touch", "unclassified_ok"):
        classified.update(paths.get(key, []))

    def _covered(rel: str) -> bool:
        """rel（"docs/" や ".claude/agents/" 形式）がいずれかの分類に含まれるか。"""
        if rel in classified or rel.rstrip("/") in classified:
            return True
        # never_touch の "history/" のような dir 宣言は任意の階層で有効
        return any(c.endswith("/") and rel.startswith(c) for c in classified)

    targets: list[str] = []
    for entry in sorted(repo_root.iterdir()):
        if entry.name == ".git":
            continue
        targets.append(entry.name + ("/" if entry.is_dir() else ""))
    claude_dir = repo_root / ".claude"
    if claude_dir.is_dir():
        for entry in sorted(claude_dir.iterdir()):
            targets.append(".claude/" + entry.name + ("/" if entry.is_dir() else ""))

    for rel in targets:
        if rel in (".claude/",):
            continue  # .claude/ 自体は直下の各要素で判定する
        if _covered(rel):
            counts["classified"] += 1
        else:
            counts["unclassified"] += 1
            issues.append({
                "location": rel,
                "message": (f"{rel!r} が dh-manifest.yml の 4 分類にも unclassified_ok にも属さない。"
                            "既定 never_touch に落ちるため、DH が配布したいものが黙って不可侵になる"
                            "（upgrade-spec-v6.17.0 §F4）"),
                "severity": "WARN",
            })

    return counts
