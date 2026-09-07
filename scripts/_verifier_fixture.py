"""検査モジュールの回帰テスト用 共通 fixture（v6.18.0 C-2）。

検査 8 を欠落の型で 4 モジュールへ分割した際、テストも分割した。
**合成ツリーを組む build / 判定する check / 実行する scenario をここに集約する** —
各テストへ複製すると分割コストがテストへ転嫁される（Council `splt02` 必須随伴条件 3）。

使い方:

    from _verifier_fixture import Fixture
    fx = Fixture("declaration_freshness")   # checks/ 配下のモジュール名
    check, scenario, OK_SPECS = fx.check, fx.scenario, fx.OK_SPECS
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

FROZEN_HISTORY = ("### バージョン履歴（v4.2 で凍結）\n\n"
                  "> **凍結マーカー**: ここに v4.2 より後を追記しないこと。\n\n"
                  "- v1.0: 二層構想\n- v4.2: philosophy 第6条\n\n### 次章\n")

OK_SPECS = (("upgrade-spec-v6.11.0.md", "実装済み（PR #186 / #187、VERSION 6.15.0）", "本文"),
            ("upgrade-spec-v6.17.0.md", "実装中（F1 済 / F2 未）", "本文"))


class Fixture:
    """1 つの検査モジュールを対象にした合成ツリー実験の道具立て。"""

    def __init__(self, module_name: str):
        path = HERE / "harness-verifier" / "checks" / f"{module_name}.py"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"{path} を単体ロードできない")
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.module_name = module_name
        self.failures = 0
        self.OK_SPECS = OK_SPECS
        self.HERE = HERE

    def check(self, name, cond, detail=""):
        if cond:
            print(f"  ok: {name}")
        else:
            self.failures += 1
            print(f"FAIL: {name} {detail}", file=sys.stderr)

    def run(self, root: Path):
        skills = root / ".claude" / "skills"
        out = self.m.run(skills_dir=skills, glossary_path=root / "harness-verifier" / "glossary.yml")
        return [i for i in out if i.get("severity") != "METRIC"]

    def scenario(self, **kw):
        td = tempfile.TemporaryDirectory()
        build(Path(td.name), **kw)
        return td, self.run(Path(td.name))

    def real(self):
        """実リポに対して走らせる（I-4: 常時発火しないことの確認用）。"""
        out = self.m.run(skills_dir=HERE / ".claude" / "skills",
                         glossary_path=HERE / "harness-verifier" / "glossary.yml")
        return [i for i in out if i.get("severity") != "METRIC"]

    def finish(self):
        if self.failures:
            sys.exit(f"\nFAIL: {self.failures} 件")
        print(f"\nPASS: {self.module_name} 回帰テスト 全通過")


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
