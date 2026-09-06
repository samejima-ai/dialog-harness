#!/usr/bin/env python3
"""共通 RL の現況被覆の回帰テスト（v6.18.0 C-2 で検査 8 のテストから分離）。

合成リポジトリツリーに各欠陥を 1 つずつ仕込み、**検出することを実証する**。
「実リポで PASS した」だけでは検査が空振りしていないことを示せない。

合成ツリーを組む道具は `scripts/_verifier_fixture.py` に集約している（複製しない）。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _verifier_fixture import Fixture, FROZEN_HISTORY, build  # noqa: E402

_fx = Fixture("rules_index")
check, scenario, OK_SPECS, HERE, m = (
    _fx.check, _fx.scenario, _fx.OK_SPECS, _fx.HERE, _fx.m)

print("== 健全なツリーでは 1 件も検出しない（空振りでない基準線） ==")
td, r = scenario(specs=OK_SPECS)
check("健全ツリー = 検出 0", r == [], str(r))
td.cleanup()

print("== 10. F6: 共通 RL の現況被覆 ==")
RL_README = ("# rules\n\n"
             "## common/ の現況\n\n"
             "- `ui-baseline.rules.md`（v5.23.0）— UI Baseline RL。"
             "利用者は `.dh/rules/common/ui-baseline.rules.md` で override 可\n"
             "- `<lang>/`: 存在しない\n\n"
             "## バージョン\n")

td, r = scenario(specs=OK_SPECS,
                 rules=(("ui-baseline.rules.md", "# UI\n"),
                        ("telemetry-reflux.rules.md", "# TR\n")),
                 rules_readme=RL_README)
check("README に列挙されない RL を FAIL で検出",
      any(i["severity"] == "FAIL" and "telemetry-reflux.rules.md" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS,
                 rules=(("ui-baseline.rules.md", "# UI\n"),),
                 rules_readme=RL_README)
check("実在と列挙が一致すれば通る（override 例の .dh/ パスを拾わない）", r == [], str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS,
                 rules=(),
                 rules_readme=RL_README)
check("README が実在しない RL を列挙 = FAIL（削除・改名への追随）",
      any(i["severity"] == "FAIL" and "実在しない" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS,
                 rules=(("ui-baseline.rules.md", "# UI\n"),),
                 rules_readme="# rules\n\n## 配置\n\nなし\n")
check("§common/ の現況 が無い = FAIL（現況 SSOT の欠落）",
      any(i["severity"] == "FAIL" and "見つからない" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS)
check("RL を持たないツリーでは skip（配布先で壊れない）", r == [], str(r))
td.cleanup()

print("== 常時発火しないこと（I-4）: 実リポで WARN / FAIL が 0 件 ==")
graded = _fx.real()
check("実リポで検出 0 件（是正済み）", graded == [], str(graded))

_fx.finish()
