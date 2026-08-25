#!/usr/bin/env python3
"""execution_graph.py の回帰テスト。

upgrade-spec v6.12.0 §検証「G-1〜G-4 の FAIL 動作を意図的な壊れ値で確認」の実装。

検査器が「通ること」ではなく「**壊れた入力を落とすこと**」を確認する。落とせない検査は
検査ではない（今日 council-log-sync の回帰テストで採った姿勢と同型）。

隔離した一時ディレクトリ上で合成 GRAPH.yml を組み立てて実行し、本物のリポジトリには触らない。

使い方: python3 scripts/test-execution-graph.py
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location(
    "execution_graph", REPO / "harness-verifier" / "checks" / "execution_graph.py"
)
eg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eg)

failures: list[str] = []


def ok(msg: str) -> None:
    print(f"  ok: {msg}")


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"FAIL: {msg}", file=sys.stderr)


BASE_NODES = """graph_schema: 1
version: "test"

nodes:
  - id: alpha
    kind: agent
    role: L0
    impl: GRAPH.yml
  - id: beta
    kind: agent
    role: L1
    impl: GRAPH.yml
  - id: gamma
    kind: tool
    role: support
    impl: GRAPH.yml
"""


def build_repo(tmp: Path, edges_yaml: str, extra: str = "") -> Path:
    """検査に必要な最小構造（.claude/skills + GRAPH.yml）を作る。"""
    root = tmp / "repo"
    (root / ".claude" / "skills").mkdir(parents=True, exist_ok=True)
    (root / "GRAPH.yml").write_text(BASE_NODES + edges_yaml + extra, encoding="utf-8")
    return root


def run_check(root: Path) -> list[dict]:
    return eg.run(skills_dir=root / ".claude" / "skills", glossary_path=root / "unused.yml")


def codes(issues: list[dict], prefix: str) -> list[dict]:
    return [i for i in issues if prefix in i.get("message", "")]


with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)

    # --- 健全な入力は PASS（偽陽性を出さないこと） -----------------------------
    healthy = build_repo(tmp / "healthy", """
edges:
  - from: alpha
    to: beta
    type: standard
    source: GRAPH.yml
  - from: beta
    to: gamma
    type: conditional
    condition: "何らかの条件"
    source: GRAPH.yml
  - from: gamma
    to: alpha
    type: loop
    condition: "戻り"
    max_iterations: 3
    source: GRAPH.yml
""")
    issues = run_check(healthy)
    graded = [i for i in issues if i.get("severity") in ("FAIL", "ERROR")]
    if graded:
        fail(f"健全な入力で FAIL が出た: {graded}")
    else:
        ok("健全な入力は PASS（偽陽性なし）")

    # --- G-1: loop に max_iterations が無い → FAIL ----------------------------
    g1 = build_repo(tmp / "g1", """
edges:
  - from: alpha
    to: beta
    type: loop
    condition: "上限を書き忘れたループ"
    source: GRAPH.yml
""")
    hits = codes(run_check(g1), "G-1")
    if not hits or hits[0]["severity"] != "FAIL":
        fail("G-1: max_iterations 欠落を FAIL にできない")
    else:
        ok("G-1: 上限のないループを FAIL にする")

    # --- G-2: 実在しないパス → FAIL ------------------------------------------
    g2 = build_repo(tmp / "g2", """
edges:
  - from: alpha
    to: beta
    type: standard
    source: does/not/exist.md
""")
    hits = codes(run_check(g2), "G-2")
    if not hits or hits[0]["severity"] != "FAIL":
        fail("G-2: 実在しない source を FAIL にできない")
    else:
        ok("G-2: dead path を FAIL にする")

    # --- G-3: conditional に condition が無い → FAIL ---------------------------
    g3 = build_repo(tmp / "g3", """
edges:
  - from: alpha
    to: beta
    type: conditional
    source: GRAPH.yml
""")
    hits = codes(run_check(g3), "G-3")
    if not hits or hits[0]["severity"] != "FAIL":
        fail("G-3: condition 欠落を FAIL にできない")
    else:
        ok("G-3: 条件のない分岐を FAIL にする")

    # --- G-4: loop 以外で循環 → FAIL ------------------------------------------
    g4 = build_repo(tmp / "g4", """
edges:
  - from: alpha
    to: beta
    type: standard
    source: GRAPH.yml
  - from: beta
    to: gamma
    type: standard
    source: GRAPH.yml
  - from: gamma
    to: alpha
    type: standard
    source: GRAPH.yml
""")
    hits = codes(run_check(g4), "G-4")
    if not hits or hits[0]["severity"] != "FAIL":
        fail("G-4: 循環を FAIL にできない")
    else:
        ok("G-4: loop を除いた循環を FAIL にする")

    # --- G-4 の裏: 同じ循環でも loop 宣言なら PASS -----------------------------
    g4ok = build_repo(tmp / "g4ok", """
edges:
  - from: alpha
    to: beta
    type: standard
    source: GRAPH.yml
  - from: beta
    to: alpha
    type: loop
    condition: "意図された戻り"
    max_iterations: 2
    source: GRAPH.yml
""")
    if codes(run_check(g4ok), "G-4"):
        fail("G-4: loop 宣言済みの戻りを誤って循環と判定した")
    else:
        ok("G-4: loop 宣言された戻りは循環と見なさない")

    # --- 未定義ノードへのエッジ → FAIL ----------------------------------------
    undef = build_repo(tmp / "undef", """
edges:
  - from: alpha
    to: nowhere
    type: standard
    source: GRAPH.yml
""")
    hits = [i for i in run_check(undef) if "nodes に未定義" in i.get("message", "")]
    if not hits:
        fail("未定義ノードへのエッジを FAIL にできない")
    else:
        ok("未定義ノードへのエッジを FAIL にする")

    # --- F2-4: GRAPH.yml 不在なら skip（利用者プロジェクトで壊れない） ---------
    absent = tmp / "absent"
    (absent / ".claude" / "skills").mkdir(parents=True)
    if run_check(absent) != []:
        fail("GRAPH.yml 不在で skip していない（後方互換が壊れる）")
    else:
        ok("F2-4: GRAPH.yml 不在なら skip（後方互換）")

    # --- F2-5: 計数が必ず出る（METRIC は判定に影響しない） --------------------
    metrics = [i for i in run_check(healthy) if i.get("severity") == "METRIC"]
    if len(metrics) != 1 or "G-5 計数" not in metrics[0]["message"]:
        fail(f"F2-5: 計数の機械出力が無い: {metrics}")
    else:
        ok("F2-5: G-5 の計数を必ず出力する（METRIC は PASS/FAIL に影響しない）")

    # --- 本物の GRAPH.yml が現に PASS すること --------------------------------
    real = run_check(REPO)
    real_bad = [i for i in real if i.get("severity") in ("FAIL", "ERROR")]
    if real_bad:
        fail(f"本物の GRAPH.yml が FAIL: {real_bad}")
    else:
        ok("本物の GRAPH.yml は PASS")

print("")
if failures:
    print(f"FAILED: {len(failures)} 件", file=sys.stderr)
    sys.exit(1)
print("PASS: execution_graph 全テスト通過")
