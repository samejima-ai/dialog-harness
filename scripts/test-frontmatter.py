#!/usr/bin/env python3
"""harness-verifier 検査 1（frontmatter 整合性）の回帰テスト。

合成ツリーに各欠陥を 1 つずつ仕込み、**検出することを実証する**。
「実リポで PASS した」だけでは検査が空振りしていないことを示せない。

v6.17.0 F5（Council D-5）で追加した `target_os` の検証が主対象。
E-3 は旧「OS 非依存」では機械検証不可だったが、「対象 OS を宣言せよ」に改めたことで
宣言の存在・値域・書式が決定論で検証できるようになった。
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "frontmatter", HERE / "harness-verifier" / "checks" / "frontmatter.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FAIL = 0

DESC = ("テスト用 skill の説明文。起動契機を 3 例以上含む必要があるため、"
        "「テストして」「検証して」「確認して」等の発話でトリガーする想定。")


def check(name, cond, detail=""):
    global FAIL
    if cond:
        print(f"  ok: {name}")
    else:
        FAIL += 1
        print(f"FAIL: {name} {detail}", file=sys.stderr)


def run(*, name="layer1-test-skill", target_os="any", extra=""):
    """合成ツリーを 1 skill だけ作って検査 1 を回す。"""
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    skills = root / ".claude" / "skills"
    d = skills / name
    d.mkdir(parents=True)
    fm = ["---", f"name: {name}"]
    if target_os is not None:
        fm.append(f"target_os: {target_os}")
    fm.append(f"description: >")
    fm.append(f"  {DESC}")
    if extra:
        fm.append(extra)
    fm += ["---", "", "# 本文", ""]
    (d / "SKILL.md").write_text("\n".join(fm), encoding="utf-8")
    issues = m.run(skills_dir=skills, glossary_path=root / "glossary.yml")
    td.cleanup()
    return [i for i in issues if i.get("severity") != "METRIC"]


print("== 健全なツリーでは 1 件も検出しない（空振りでない基準線） ==")
check("健全ツリー = 検出 0", run() == [], str(run()))

print("== target_os の宣言不在（E-3・v6.17.0 F5） ==")
r = run(target_os=None)
check("宣言不在を FAIL で検出",
      any(i["severity"] == "FAIL" and "target_os" in i["message"] for i in r), str(r))

print("== target_os の値域 ==")
for good in ("any", "windows", "macos", "linux", "wsl", "linux+macos+wsl", "windows+wsl"):
    r = run(target_os=good)
    check(f"値域内は通す: {good}", r == [], str(r))

r = run(target_os="win32")
check("未知の値を FAIL で検出（表記揺れが検証を空文化させない）",
      any("未知の値" in i["message"] for i in r), str(r))

r = run(target_os="Windows")
check("大文字表記を FAIL で検出",
      any(i["severity"] == "FAIL" for i in r), str(r))

r = run(target_os="any+windows")
check("'any' と個別 OS の混在を FAIL で検出",
      any("単独で使う" in i["message"] for i in r), str(r))

r = run(target_os="linux macos")
check("区切りが '+' でない書式を FAIL で検出",
      any("書式が不正" in i["message"] for i in r), str(r))

print("== 既存の検証を壊していないこと ==")
r = run(name="Bad_Name")
check("kebab-case 違反は引き続き FAIL",
      any("kebab-case" in i["message"] for i in r), str(r))

print("== 常時発火しないこと（I-4）: 実リポで FAIL が 0 件 ==")
real = m.run(skills_dir=HERE / ".claude" / "skills",
             glossary_path=HERE / "harness-verifier" / "glossary.yml")
graded = [i for i in real if i.get("severity") != "METRIC"]
check("実リポで検出 0 件（全 skill に target_os を付与済み）", graded == [], str(graded))

if FAIL:
    sys.exit(f"\nFAIL: {FAIL} 件")
print("\nPASS: 検査 1（frontmatter 整合性 / target_os）回帰テスト 全通過")
