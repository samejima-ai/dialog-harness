#!/usr/bin/env python3
"""test-upstream-scan — scripts/upstream-scan.py の不変条件テスト。

検証するのは U-1〜U-5（dh-manifest.yml §upstream）と「門ではなく観測」の 2 性質。
実行: python3 scripts/test-upstream-scan.py
"""

from __future__ import annotations

import importlib.util
import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

_spec = importlib.util.spec_from_file_location("uscan", Path(__file__).parent / "upstream-scan.py")
uscan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(uscan)

FAILED: list[str] = []


def check(cond: bool, label: str) -> None:
    print(f"  {'ok' if cond else 'NG'}: {label}")
    if not cond:
        FAILED.append(label)


MANIFEST = """manifest_schema: 1
paths:
  overwrite:
    - ".claude/skills/"
upstream:
  scan:
    - ".claude/skills/"
    - "scripts/check-*"
  never_upstream:
    - ".claude/skills/layer0-spec-architect/references/philosophy.md"
    - "VERSION"
  gate: human
verify_after_update: true
"""


def build(tmp: Path, gate: str = "human") -> tuple[Path, Path]:
    dh, tg = tmp / "dh", tmp / "tg"
    for base in (dh, tg):
        (base / ".claude" / "skills").mkdir(parents=True)
        (base / "scripts").mkdir(parents=True)
    (dh / "dh-manifest.yml").write_text(MANIFEST.replace("gate: human", f"gate: {gate}"), encoding="utf-8")

    # DH と配布先の双方に在る（= 候補にならない）
    for base in (dh, tg):
        (base / ".claude" / "skills" / "crosscut-council").mkdir()
        (base / "scripts" / "check-common.mjs").write_text("x", encoding="utf-8")
    # 配布先のみ（= 候補）
    (tg / ".claude" / "skills" / "grown-skill").mkdir()
    (tg / "scripts" / "check-new.mjs").write_text("x", encoding="utf-8")
    # 配布先のみだが glob 外（= 候補にならない）
    (tg / "scripts" / "backfill-orders.mjs").write_text("x", encoding="utf-8")
    # never_upstream に触れる（= 列挙すらしない）
    (tg / ".claude" / "skills" / "layer0-spec-architect").mkdir()
    (tg / "VERSION").write_text("9.9.9", encoding="utf-8")
    return dh, tg


def run(dh: Path, tg: Path, *extra: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = uscan.main(["--target", str(tg), "--dh-root", str(dh), "--today", "2026-01-01", *extra])
    return rc, out.getvalue(), err.getvalue()


def snapshot(root: Path) -> dict[str, float]:
    return {str(p.relative_to(root)): p.stat().st_mtime_ns for p in sorted(root.rglob("*"))}


print("== upstream-scan ==")

# --- 存在差分・glob・never_upstream ---
with tempfile.TemporaryDirectory() as t:
    dh, tg = build(Path(t))
    before = snapshot(tg)
    rc, out, _ = run(dh, tg, "--dry-run")
    check(rc == 0, "正常系は exit 0")
    check("`.claude/skills/grown-skill/`" in out, "配布先のみの skill が候補になる")
    check("`scripts/check-new.mjs`" in out, "glob に合致するファイルが候補になる")
    check("crosscut-council" not in out, "DH に在る要素は候補にならない（存在差分のみ）")
    check("backfill-orders" not in out, "glob 外のファイルは候補にならない（宣言側で絞る）")
    check("layer0-spec-architect" not in out, "U-3: never_upstream は列挙すらしない")
    check("| 候補 | 2 |" in out, "計数が候補件数と一致する")
    check("| 採否未記入 | 2 |" in out, "採否未記入が計数される")
    check("| 事故の日付が未記入 | 2 |" in out, "U-5: 事故の日付の未記入が計数される")
    check(snapshot(tg) == before, "U-1: 配布先を 1 バイトも書き換えない")

# --- 人間記入欄の引き継ぎ ---
with tempfile.TemporaryDirectory() as t:
    dh, tg = build(Path(t))
    prev = Path(t) / "prev.md"
    prev.write_text(
        "| 候補 | 種別 | 出自 | 事故の日付 | それが解いた問題 | 固有依存 | 採否 |\n"
        "|---|---|---|---|---|---|---|\n"
        "| `scripts/check-new.mjs` | mjs | `tg` | 2026-06-11 | RLS ドリフトを検出した | なし | 採択 |\n",
        encoding="utf-8",
    )
    rc, out, _ = run(dh, tg, "--dry-run", "--prev", str(prev))
    check("2026-06-11" in out and "RLS ドリフトを検出した" in out, "前回の人間記入欄を引き継ぐ")
    check("| 採択 | 1 |" in out, "引き継いだ採否が計数に反映される")
    check("| 事故の日付が未記入 | 1 |" in out, "引き継ぎ後は未記入件数が減る")

# --- 武装検査（黙って緑にしない） ---
with tempfile.TemporaryDirectory() as t:
    dh, tg = build(Path(t), gate="auto")
    rc, _, err = run(dh, tg, "--dry-run")
    check(rc == 1 and "gate" in err, "U-3: gate が human でなければ FAIL")

with tempfile.TemporaryDirectory() as t:
    dh, tg = build(Path(t))
    shutil.rmtree(tg)
    rc, _, err = run(dh, tg, "--dry-run")
    check(rc == 1 and "配布先が存在しない" in err, "配布先不在を候補 0 件で緑にしない")

with tempfile.TemporaryDirectory() as t:
    dh, tg = build(Path(t))
    (dh / "dh-manifest.yml").write_text("manifest_schema: 1\n", encoding="utf-8")
    rc, _, err = run(dh, tg, "--dry-run")
    check(rc == 1 and "upstream" in err, "manifest に upstream が無ければ FAIL")

# --- 門ではなく観測 ---
with tempfile.TemporaryDirectory() as t:
    dh, tg = build(Path(t))
    for i in range(5):
        (tg / "scripts" / f"check-extra{i}.mjs").write_text("x", encoding="utf-8")
    rc, out, _ = run(dh, tg, "--dry-run")
    check(rc == 0, "候補が増えても exit code は 0（門ではなく観測）")
    check("| 候補 | 7 |" in out, "追加分が候補に載る")

# --- U-2: DH 側は出力先以外を書き換えない ---
with tempfile.TemporaryDirectory() as t:
    dh, tg = build(Path(t))
    before = snapshot(dh)
    out_path = dh / "delivery" / "OUT.md"
    rc, _, _ = run(dh, tg, "--out", str(out_path))
    after = snapshot(dh)
    added = set(after) - set(before)
    check(rc == 0 and out_path.is_file(), "出力先に書き出す")
    check(all(a.startswith("delivery") for a in added), "U-2: 出力先以外に DH を書き換えない")
    check({k: v for k, v in after.items() if k in before} == before, "U-2: 既存ファイルを改変しない")

print()
if FAILED:
    print(f"FAIL: {len(FAILED)} 件 — " + " / ".join(FAILED))
    sys.exit(1)
print("PASS: upstream-scan 全テスト通過")
