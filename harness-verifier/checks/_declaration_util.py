"""宣言系検査の共通ヘルパ（v6.18.0 C-2）。

検査 8 を「1 検査器 = 1 つの欠落の型」で分割するにあたり、複数モジュールが共有する
最小限の道具だけをここに置く（Council `council-2026-09-06T15:00:00Z-splt02` 必須随伴条件 2）。

**素朴なコピペ分割を禁ずるための器である。** `parse_graph` の単体ロード fallback は 14 行あり、
これを各モジュールへ複製すると分割の益を重複コストが食う。1 箇所に集約する。

置いてよいもの: 2 つ以上のモジュールが実際に使う道具のみ。
置いてはいけないもの: 特定の検査だけが使うロジック（それは当該モジュールに閉じる）。
"""

from __future__ import annotations

import re
from pathlib import Path

try:  # verify.py 経由（パッケージとして読み込まれる正規経路）
    from .execution_graph import parse_graph
except ImportError:  # 単体ロード（scripts/test-*.py が spec_from_file_location で読む）
    import importlib.util as _ilu

    _path = Path(__file__).with_name("execution_graph.py")
    _spec = _ilu.spec_from_file_location("_execution_graph", _path)
    # spec / loader は None を返しうる。ここで潰さないと後段が AttributeError になり、
    # 「なぜ宣言系検査が動かないのか」が読めない失敗になる。原因の分かる例外に変換する。
    if _spec is None or _spec.loader is None:
        raise ImportError(f"execution_graph.py を単体ロードできない: {_path}")
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    parse_graph = _mod.parse_graph

__all__ = ["parse_graph", "read_graph", "skill_ids_from_graph"]


def read_graph(graph_path: Path) -> dict:
    """GRAPH.yml を読む。不在・読み取り失敗なら空 dict（配布先で壊れない = I-6）。"""
    if not graph_path.is_file():
        return {}
    try:
        return parse_graph(graph_path.read_text(encoding="utf-8"))
    except OSError:
        return {}


def skill_ids_from_graph(doc: dict) -> set[str]:
    """GRAPH.yml が skill として宣言している id の集合。

    skill node の判定は `impl` が `.claude/skills/<id>/SKILL.md` であること。
    **prefix で絞らない** — human gate（impl が skill 配下の philosophy.md 等を指す）を
    巻き込むうえ、`rtk-integration` のような prefix を持たない skill を落とす
    （`glossary.py:250` の managed_prefixes / `execution_graph.py` G-5 と同型の欠陥）。
    """
    ids = {
        n["id"] for n in doc.get("nodes", [])
        if isinstance(n, dict) and n.get("id")
        and str(n.get("impl", "")) == f".claude/skills/{n['id']}/SKILL.md"
    }
    ids |= {
        x["id"] for x in doc.get("graph_excluded", [])
        if isinstance(x, dict) and x.get("id")
        and str(x.get("path", "")) == f".claude/skills/{x['id']}/"
    }
    return ids
