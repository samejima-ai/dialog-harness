#!/usr/bin/env python3
"""harness-verifier 検査 8（宣言被覆・F1 / F2 / F3 / F4 / F6）の回帰テスト。

合成リポジトリツリーに各欠陥を 1 つずつ仕込み、**検出することを実証する**。
「実リポで PASS した」だけでは検査が空振りしていないことを示せない。
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "declaration_coverage", HERE / "harness-verifier" / "checks" / "declaration_coverage.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FAIL = 0
FROZEN_HISTORY = ("### バージョン履歴（v4.2 で凍結）\n\n"
                  "> **凍結マーカー**: ここに v4.2 より後を追記しないこと。\n\n"
                  "- v1.0: 二層構想\n- v4.2: philosophy 第6条\n\n### 次章\n")


def check(name, cond, detail=""):
    global FAIL
    if cond:
        print(f"  ok: {name}")
    else:
        FAIL += 1
        print(f"FAIL: {name} {detail}", file=sys.stderr)


def build(root: Path, *, version="6.15.0", graph_version="6.15.0",
          specs=(), history=FROZEN_HISTORY, graph_body=None,
          skill_dirs=(), script_files=(), source_docs=(),
          rules=(), rules_readme=None, manifest=None, state_in_dist=()):
    """合成ツリーを組む。

    graph_body を渡すと GRAPH.yml の nodes / edges / graph_excluded を差し替える（F2 用）。
    skill_dirs / script_files は「実体」を、source_docs は edge.source の中身を作る。
    """
    skills = root / ".claude" / "skills"
    (skills / "layer0-spec-architect" / "references").mkdir(parents=True)
    (root / "VERSION").write_text(version + "\n", encoding="utf-8")
    for name in skill_dirs:
        d = skills / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    if script_files:
        (root / "scripts").mkdir(exist_ok=True)
        for name in script_files:
            (root / "scripts" / name).write_text("# script\n", encoding="utf-8")
    if rules or rules_readme is not None:
        common = root / "templates" / "rules" / "common"
        common.mkdir(parents=True, exist_ok=True)
        for name, rl_body in rules:
            (common / name).write_text(rl_body, encoding="utf-8")
        if rules_readme is not None:
            (root / "templates" / "rules" / "README.md").write_text(rules_readme, encoding="utf-8")
    for rel, doc_body in source_docs:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(doc_body, encoding="utf-8")
    if manifest is not None:
        (root / "dh-manifest.yml").write_text(manifest, encoding="utf-8")
    for rel in state_in_dist:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text("# state" + chr(10), encoding="utf-8")
    if graph_version is not None:
        gb = graph_body if graph_body is not None else "nodes: []\n"
        (root / "GRAPH.yml").write_text(gb + f'version: "{graph_version}"\n', encoding="utf-8")
    (skills / "layer0-spec-architect" / "references" / "dev-env-spec.md").write_text(
        "# dev-env-spec\n\n" + history, encoding="utf-8")
    up = root / "dh-upgrades"
    up.mkdir()
    for name, state, body in specs:
        head = f"> **状態: {state}**。\n\n" if state is not None else ""
        (up / name).write_text(f"# {name}\n\n{head}{body}\n", encoding="utf-8")
    return skills


def run(root: Path):
    skills = root / ".claude" / "skills"
    out = m.run(skills_dir=skills, glossary_path=root / "harness-verifier" / "glossary.yml")
    return [i for i in out if i.get("severity") != "METRIC"]


def scenario(**kw):
    td = tempfile.TemporaryDirectory()
    build(Path(td.name), **kw)
    return td, run(Path(td.name))


OK_SPECS = (("upgrade-spec-v6.11.0.md", "実装済み（PR #186 / #187、VERSION 6.15.0）", "本文"),
            ("upgrade-spec-v6.17.0.md", "実装中（F1 済 / F2 未）", "本文"))

print("== 健全なツリーでは 1 件も検出しない（空振りでない基準線） ==")
td, r = scenario(specs=OK_SPECS)
check("健全ツリー = 検出 0", r == [], str(r))
td.cleanup()

print("== 1. VERSION と GRAPH.yml の不一致 ==")
td, r = scenario(graph_version="6.12.0", specs=OK_SPECS)
check("不一致を FAIL で検出",
      any(i["severity"] == "FAIL" and "GRAPH.yml" in i["location"] for i in r), str(r))
td.cleanup()
td, r = scenario(graph_version=None, specs=OK_SPECS)
check("GRAPH.yml 不在は誤検知しない", r == [], str(r))
td.cleanup()

print("== 2. 状態行が値域外 ==")
td, r = scenario(specs=(("upgrade-spec-v6.17.0.md", "だいたい実装した", "本文"),))
check("値域外を FAIL で検出", any("値域外" in i["message"] for i in r), str(r))
td.cleanup()
for good in ("L0 起草（人間レビュー待ち）", "Council 諮問通過・人間の採否判定待ち",
             "実装中（F1 済 / F2 未）", "実装済み（PR #186、VERSION 6.15.0）",
             "破棄（Council 判定で不採用）"):
    td, r = scenario(specs=(("upgrade-spec-v6.14.0.md", good, "本文"),))
    check(f"値域内は通す: {good[:14]}…", all("値域外" not in i["message"] for i in r), str(r))
    td.cleanup()

print("== 3. 未 release の spec に状態行が無い ==")
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", None, "本文"),))
check("版 > VERSION で状態行欠落 = FAIL", any("状態行が無い" in i["message"] for i in r), str(r))
td.cleanup()
td, r = scenario(specs=(("upgrade-spec-v5.8.0.md", None, "本文"),))
check("版 <= VERSION の歴史的 spec には遡及しない（I-4）", r == [], str(r))
td.cleanup()

print("== 4. 実装済みを名乗る版が VERSION を超える ==")
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", "実装済み（PR #999、VERSION 6.16.0）", "本文"),))
check("超過を FAIL で検出", any("超えている" in i["message"] for i in r), str(r))
td.cleanup()

print("== 5. L0 起草のまま本文が実装を名乗る（file-local・WARN） ==")
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", "L0 起草（人間レビュー待ち）",
                         "> **実装済み（PR #248、2026-09-05）**: F7 を実装した。"),))
check("WARN で検出", any(i["severity"] == "WARN" for i in r), str(r))
td.cleanup()
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", "L0 起草（人間レビュー待ち）",
                         "実装の順序は L0 → L1 とする。"),))
check("実装を名乗らない本文では発火しない（偽陽性 0）", r == [], str(r))
td.cleanup()
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", "実装中（F7 済 / F1 未）",
                         "> **実装済み（PR #248）**: F7 を実装した。"),))
check("状態行を実態に直せば消える", r == [], str(r))
td.cleanup()

print("== 6. dev-env-spec §バージョン履歴 の凍結 ==")
td, r = scenario(specs=OK_SPECS,
                 history="### バージョン履歴\n\n- v1.0: 二層構想\n- v4.2: 第6条\n\n### 次章\n")
check("凍結マーカー欠落 = FAIL", any("凍結マーカー" in i["message"] for i in r), str(r))
td.cleanup()
td, r = scenario(specs=OK_SPECS, history=FROZEN_HISTORY.replace(
    "- v4.2: philosophy 第6条", "- v4.2: philosophy 第6条\n- v6.15: 版整合"))
check("v4.2 より後の追記 = FAIL（宣言の二重定義を防ぐ）",
      any("v4.2 より後" in i["message"] for i in r), str(r))
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
real = m.run(skills_dir=HERE / ".claude" / "skills",
             glossary_path=HERE / "harness-verifier" / "glossary.yml")
graded = [i for i in real if i.get("severity") != "METRIC"]
check("実リポで検出 0 件（是正済み）", graded == [], str(graded))

if FAIL:
    sys.exit(f"\nFAIL: {FAIL} 件")
print("\nPASS: 検査 8（宣言被覆・F1 / F2 / F3 / F4 / F6）回帰テスト 全通過")
