#!/usr/bin/env python3
"""宣言の網羅（実体 → 宣言）の回帰テスト（v6.18.0 C-2 で検査 8 のテストから分離）。

合成リポジトリツリーに各欠陥を 1 つずつ仕込み、**検出することを実証する**。
「実リポで PASS した」だけでは検査が空振りしていないことを示せない。

合成ツリーを組む道具は `scripts/_verifier_fixture.py` に集約している（複製しない）。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _verifier_fixture import Fixture, FROZEN_HISTORY, build  # noqa: E402

_fx = Fixture("declaration_coverage")
check, scenario, OK_SPECS, HERE, m = (
    _fx.check, _fx.scenario, _fx.OK_SPECS, _fx.HERE, _fx.m)

print("== 健全なツリーでは 1 件も検出しない（空振りでない基準線） ==")
td, r = scenario(specs=OK_SPECS)
check("健全ツリー = 検出 0", r == [], str(r))
td.cleanup()

print("== 7. F2: skill が nodes にも graph_excluded にも無い（FAIL） ==")
GRAPH_2SKILL = ("nodes:\n"
                "  - id: layer1-autonomous-dev\n"
                "    impl: .claude/skills/layer1-autonomous-dev/SKILL.md\n")
td, r = scenario(specs=OK_SPECS, graph_body=GRAPH_2SKILL,
                 skill_dirs=("layer1-autonomous-dev", "rtk-integration"))
check("未登録 skill を FAIL で検出（prefix でフィルタしない）",
      any(i["severity"] == "FAIL" and "rtk-integration" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS,
                 graph_body=GRAPH_2SKILL + ("graph_excluded:\n"
                                            "  - id: rtk-integration\n"
                                            "    path: .claude/skills/rtk-integration/\n"
                                            "    reason: テスト\n"),
                 skill_dirs=("layer1-autonomous-dev", "rtk-integration"))
check("graph_excluded に理由付きで宣言すれば通る", r == [], str(r))
td.cleanup()

print("== 8. F2: script が impl にも graph_excluded にも無い（WARN） ==")
GRAPH_SCRIPT = "nodes:\n  - id: signal-scan\n    impl: scripts/signal-scan.py\n"
td, r = scenario(specs=OK_SPECS, graph_body=GRAPH_SCRIPT,
                 script_files=("signal-scan.py", "pr-audit.py"))
check("未宣言 script を WARN で検出",
      any(i["severity"] == "WARN" and "pr-audit.py" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS, graph_body=GRAPH_SCRIPT,
                 script_files=("signal-scan.py", "test-signal-scan.py"))
check("test-* は対象外（回帰テストを宣言対象にしない）", r == [], str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS,
                 graph_body=GRAPH_SCRIPT + ("graph_excluded:\n"
                                            "  - id: pr-audit\n"
                                            "    path: scripts/pr-audit.py\n"
                                            "    reason: 分析器\n"),
                 script_files=("signal-scan.py", "pr-audit.py"))
check("graph_excluded の path 宣言で通る", r == [], str(r))
td.cleanup()

print("== 9. F2: source 実質検査（HV-04 の再現） ==")
GRAPH_EDGE = ("nodes:\n"
              "  - id: layer0-spec-architect\n"
              "    impl: .claude/skills/layer0-spec-architect/SKILL.md\n"
              "  - id: council-performance\n"
              "    impl: scripts/council-performance.py\n"
              "edges:\n"
              "  - from: layer0-spec-architect\n"
              "    to: council-performance\n"
              "    type: standard\n"
              "    source: ritual-protocol.md\n")
td, r = scenario(specs=OK_SPECS, graph_body=GRAPH_EDGE,
                 source_docs=(("ritual-protocol.md",
                               "# 儀式\n\nF1 では council-log-sync.py を走らせる。\n"),))
check("source が edge.to を指さない = WARN（HV-04 の再現）",
      any(i["severity"] == "WARN" and "実質乖離" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS, graph_body=GRAPH_EDGE,
                 source_docs=(("ritual-protocol.md",
                               "# 儀式\n\nF1 では council-performance.py を走らせる。\n"),))
check("impl basename が本文にあれば通る", r == [], str(r))
td.cleanup()

GRAPH_EDGE_SKILL = ("nodes:\n"
                    "  - id: layer2-orchestrator\n"
                    "    impl: .claude/skills/layer2-orchestrator/SKILL.md\n"
                    "  - id: layer1-autonomous-dev\n"
                    "    impl: .claude/skills/layer1-autonomous-dev/SKILL.md\n"
                    "edges:\n"
                    "  - from: layer2-orchestrator\n"
                    "    to: layer1-autonomous-dev\n"
                    "    type: standard\n"
                    "    source: orchestrator.md\n")
td, r = scenario(specs=OK_SPECS, graph_body=GRAPH_EDGE_SKILL,
                 source_docs=(("orchestrator.md",
                               "# L2\n\nドメインごとに L1（autonomous-dev）を起動する。\n"),))
check("層 prefix を落とした略記も一致とみなす（偽陽性 0）", r == [], str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS, graph_body=GRAPH_EDGE_SKILL,
                 source_docs=(("orchestrator.md", "# L2\n\n各ドメインを順に処理する。\n"),))
check("skill を指す記述が無ければ WARN（SKILL.md の basename では通さない）",
      any(i["severity"] == "WARN" and "実質乖離" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS, graph_body=(
                     "nodes:\n"
                     "  - id: crosscut-issue-implementer\n"
                     "    impl: .claude/skills/crosscut-issue-implementer/SKILL.md\n"
                     "edges:\n"
                     "  - from: crosscut-issue-implementer\n"
                     "    to: crosscut-issue-implementer\n"
                     "    type: loop\n"
                     "    max_iterations: 10\n"
                     "    source: circuit-breaker-spec.md\n"),
                 source_docs=(("circuit-breaker-spec.md",
                               "# CB\n\n日次上限に達したら翌日再試行する。\n"),))
check("self-loop は対象外（本文が自分の名を呼ぶ形にならない）", r == [], str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS, graph_body=GRAPH_EDGE, source_docs=())
check("source が不在なら検査 9 は黙る（パス実在は G-2 の担当）", r == [], str(r))
td.cleanup()

print("== 11-12. F4: manifest 分類網羅 + owned_skills の実在一致 ==")
MANIFEST_OK = ("paths:\n"
               "  overwrite:\n"
               "    - \"templates/\"\n"
               "  owned_skills:\n"
               "    - \"layer1-autonomous-dev\"\n"
               "  merge:\n"
               "    - \".claude/settings.json\"\n"
               "  redeploy: []\n"
               "  never_touch:\n"
               "    - \"history/\"\n"
               "  unclassified_ok:\n"
               "    - \"VERSION\"\n"
               "    - \"GRAPH.yml\"\n"
               "    - \"dh-upgrades/\"\n"
               "    - \".claude/skills/\"\n"
               "    - \"dh-manifest.yml\"\n"
               "    - \".claude/\"\n")

td, r = scenario(specs=OK_SPECS, manifest=MANIFEST_OK,
                 skill_dirs=("layer1-autonomous-dev", "rtk-integration"))
# assertion は location と message の両方で切り分ける。message だけを見ると、同じ合成ツリーが
# 検査 7（GRAPH 未登録）で出す "rtk-integration" 入りの FAIL に相乗りしてしまい、
# **検査 12 を完全に無効化してもこのテストが通る**（独立検証 2026-09-06 で実測）。
check("owned_skills 列挙漏れを FAIL で検出（静かな失敗を防ぐ）",
      any(i["severity"] == "FAIL"
          and i["location"].startswith(".claude/skills/rtk-integration")
          and "owned_skills" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS,
                 manifest=MANIFEST_OK.replace('    - "layer1-autonomous-dev"\n',
                                              '    - "layer1-autonomous-dev"\n    - "rtk-integration"\n'),
                 graph_body=("nodes:" + chr(10) + "  - id: layer1-autonomous-dev" + chr(10) + "    impl: .claude/skills/layer1-autonomous-dev/SKILL.md" + chr(10) + "  - id: rtk-integration" + chr(10) + "    impl: .claude/skills/rtk-integration/SKILL.md" + chr(10)),
                 skill_dirs=("layer1-autonomous-dev", "rtk-integration"))
check("owned_skills が実在と一致すれば通る（prefix でフィルタしない）",
      r == [], str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS,
                 manifest=MANIFEST_OK.replace('    - "layer1-autonomous-dev"\n',
                                              '    - "layer1-autonomous-dev"\n    - "ghost-skill"\n'),
                 skill_dirs=("layer1-autonomous-dev",))
check("実在しない skill の列挙を FAIL で検出（削除・改名への追随）",
      any(i["severity"] == "FAIL" and "ghost-skill" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS,
                 manifest=MANIFEST_OK.replace('    - "dh-upgrades/"\n', ""),
                 skill_dirs=("layer1-autonomous-dev",))
check("未分類パスを WARN で検出（黙って never_touch に落ちるのを防ぐ）",
      any(i["severity"] == "WARN" and "dh-upgrades" in i["location"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS, skill_dirs=("layer1-autonomous-dev",))
check("manifest を持たないツリーでは skip（配布先で壊れない）",
      all("manifest" not in i["location"] for i in r), str(r))
td.cleanup()

# D-4 条件 (c): 単一情報源は GRAPH.yml nodes。owned_skills を GRAPH とも突合する。
GRAPH_1SKILL = ("nodes:" + chr(10)
                + "  - id: layer1-autonomous-dev" + chr(10)
                + "    impl: .claude/skills/layer1-autonomous-dev/SKILL.md" + chr(10))
td, r = scenario(specs=OK_SPECS, manifest=MANIFEST_OK, graph_body=GRAPH_1SKILL,
                 skill_dirs=("layer1-autonomous-dev",))
check("GRAPH / owned_skills / 実在 dir が揃えば通る（三者一致）", r == [], str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS,
                 manifest=MANIFEST_OK.replace('  owned_skills:' + chr(10), '  owned_skills:' + chr(10) + '    - "phantom"' + chr(10)),
                 graph_body=GRAPH_1SKILL, skill_dirs=("layer1-autonomous-dev",))
check("GRAPH に無い skill を owned_skills が持てば FAIL（単独で増やさない）",
      any(i["severity"] == "FAIL" and "GRAPH.yml に無い" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS, manifest=MANIFEST_OK,
                 graph_body=GRAPH_1SKILL + ("  - id: extra-skill" + chr(10)
                                            + "    impl: .claude/skills/extra-skill/SKILL.md" + chr(10)),
                 skill_dirs=("layer1-autonomous-dev", "extra-skill"))
check("GRAPH が宣言する skill が owned_skills に無ければ FAIL",
      any(i["severity"] == "FAIL" and "GRAPH.yml が skill" in i["message"] for i in r), str(r))
td.cleanup()

td, r = scenario(specs=OK_SPECS, manifest=MANIFEST_OK,
                 graph_body=(GRAPH_1SKILL
                             + "  - id: human-P1" + chr(10)
                             + "    impl: .claude/skills/layer0-spec-architect/references/philosophy.md" + chr(10)),
                 skill_dirs=("layer1-autonomous-dev",))
check("human gate ノードを skill と誤認しない（prefix でなく SKILL.md 完全一致で判定）",
      r == [], str(r))

print("== dict リテラルの重複キー（v6.18.0 で実際に F4 METRIC を消していた） ==")
# 672 行に肥大した run() の中で、issues.append({...}) を機械的に連結した結果、
# 1 つの dict に "location" / "message" が 2 度現れ、F4 の METRIC が F3 の値に
# 上書きされて出力から消えていた。Python は重複キーを黙って後勝ちにするため、
# 構文エラーにも実行時エラーにもならない。**型 A（宣言と実体の乖離）の一種**で、
# ラベルには「F4 分類網羅」とあるのに計数行が無い状態が続いていた。
import ast as _ast

_src = (HERE / "harness-verifier" / "checks" / "declaration_coverage.py").read_text(encoding="utf-8")
_dups = []
for _node in _ast.walk(_ast.parse(_src)):
    if isinstance(_node, _ast.Dict):
        _keys = [k.value for k in _node.keys if isinstance(k, _ast.Constant)]
        _d = {k for k in _keys if _keys.count(k) > 1}
        if _d:
            _dups.append((_node.lineno, _d))
check("dict リテラルに重複キーが無い（後勝ちで値が黙って消える）",
      _dups == [], str(_dups))

print("== 常時発火しないこと（I-4）: 実リポで WARN / FAIL が 0 件 ==")
graded = _fx.real()
check("実リポで検出 0 件（是正済み）", graded == [], str(graded))

_fx.finish()
