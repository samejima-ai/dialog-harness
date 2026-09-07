#!/usr/bin/env python3
"""配布物の状態の回帰テスト（v6.18.0 C-2 で検査 8 のテストから分離）。

合成リポジトリツリーに各欠陥を 1 つずつ仕込み、**検出することを実証する**。
「実リポで PASS した」だけでは検査が空振りしていないことを示せない。

合成ツリーを組む道具は `scripts/_verifier_fixture.py` に集約している（複製しない）。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _verifier_fixture import Fixture, FROZEN_HISTORY, build  # noqa: E402

_fx = Fixture("distribution_state")
check, scenario, OK_SPECS, HERE, m = (
    _fx.check, _fx.scenario, _fx.OK_SPECS, _fx.HERE, _fx.m)

print("== 健全なツリーでは 1 件も検出しない（空振りでない基準線） ==")
td, r = scenario(specs=OK_SPECS)
check("健全ツリー = 検出 0", r == [], str(r))
td.cleanup()

print("== 13. F3: 配布物に配布先固有の状態を置かない ==")
td, r = scenario(specs=OK_SPECS, skill_dirs=("crosscut-council",),
                 state_in_dist=(".claude/skills/crosscut-council/history/COUNCIL-LOG.md",))
check("配布物内の history/ を WARN で検出",
      any(i["severity"] == "WARN" and i["location"].endswith("history/") for i in r), str(r))
check("配布物内のログ実体を WARN で検出",
      any(i["severity"] == "WARN" and "COUNCIL-LOG.md" in i["location"] for i in r), str(r))
td.cleanup()

GRAPH_CC = ("nodes:" + chr(10)
            + "  - id: crosscut-council" + chr(10)
            + "    impl: .claude/skills/crosscut-council/SKILL.md" + chr(10))
td, r = scenario(specs=OK_SPECS, skill_dirs=("crosscut-council",), graph_body=GRAPH_CC)
check("配布物に状態が無ければ通る（移送後の定常状態）", r == [], str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS, skill_dirs=("crosscut-council",),
                 state_in_dist=("templates/rules/CHANGELOG.md",))
check("templates/ 配下のログ実体も検出（skills だけを見ているのではない）",
      any(i["severity"] == "WARN" and "CHANGELOG.md" in i["location"] for i in r), str(r))
td.cleanup()

print("== 常時発火しないこと（I-4）: 実リポで WARN / FAIL が 0 件 ==")
graded = _fx.real()
check("実リポで検出 0 件（是正済み）", graded == [], str(graded))

_fx.finish()
