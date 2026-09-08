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

__all__ = ["parse_graph", "read_graph", "skill_ids_from_graph",
           "is_dh_core", "surface_missing"]


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


# --- 走査面の欠落を「静かな PASS」にしないための道具（v6.18.0 C-4） -------------
#
# 宣言系検査は「入力が無ければ skip」で書かれている。これは I-6（配布先など機構自体を
# 持たないツリーで壊れない）のための正当な分岐である。**問題は skip が不可視なこと**。
#
# 実測（2026-09-07）: DH 本体で `GRAPH.yml` を消すと 6 検査が 1 件も出さずに
# `--strict` が exit 0 で通る。`dev-env-spec.md` §バージョン履歴 の見出しに半角空白を
# 1 個入れるだけでも検査 6 が黙って無効化し、やはり exit 0 になる。
# 検査が守っているはずのものを消しても緑になるなら、その緑は何も保証していない。
#
# 方針（v6.13.0 I-4「検出器は黙って捨てない」の自己適用）:
#   - **DH 本体**（走査面が在るはずのツリー）で入力が欠けたら **FAIL**
#   - それ以外（配布先など）では **METRIC で skip を可視化**して続行（I-6 を壊さない）


def is_dh_core(repo_root: Path) -> bool:
    """このツリーが DH 本体か。

    マーカーは `harness-verifier/checks/`（**検査の実体そのもの**）1 つに絞る。理由は 2 つ:

    - 配布先はこれを持たない。`harness-verifier/reports/` だけを持つ配布先（cc-cockpit 実例）を
      本体と誤認しない。
    - **このマーカーを消すと検査自体が動かなくなる**ので、「マーカーを消して走査面の
      欠落判定だけ黙らせる」という抜け道が原理的に作れない。
      `dh-upgrades/` のような被検査対象をマーカーにすると、それを消すだけで
      「消えたことを検出する仕組み」も一緒に黙る（自己参照の穴）。
    """
    return (repo_root / "harness-verifier" / "checks").is_dir()


def surface_missing(issues: list, repo_root: Path, location: str, what: str) -> None:
    """走査面が取れなかったことを必ず記録する。

    DH 本体なら FAIL（在るはずのものが無い）、配布先なら METRIC（skip したと明示）。
    どちらでも「黙って PASS」にはしない。
    """
    if is_dh_core(repo_root):
        issues.append({
            "location": location,
            "message": (f"{what} が見つからず、この検査は走査面を確保できなかった。"
                        f"DH 本体では在るはずのものなので FAIL とする"
                        f"（走査面の欠落を静かな PASS にしない = v6.13.0 I-4 の自己適用）"),
            "severity": "FAIL",
        })
    else:
        issues.append({
            "location": location,
            "message": f"skip — {what} が無いツリーのため本検査は走らなかった（配布先では正常・I-6）",
            "severity": "METRIC",
        })
