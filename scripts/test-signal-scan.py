#!/usr/bin/env python3
"""signal-scan.py の回帰テスト（オフライン・gh/git 不要）。

取得層は呼ばず、判定層の純粋関数に fixture を渡して検証する（v6.15.0 I-2 / F1）。
"""

import datetime as dt
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "signal_scan", Path(__file__).parent / "signal-scan.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FAIL = 0
NOW = dt.datetime(2026, 8, 28, 0, 0, 0, tzinfo=dt.timezone.utc)


def check(name, cond, detail=""):
    global FAIL
    if cond:
        print(f"  ok: {name}")
    else:
        FAIL += 1
        print(f"FAIL: {name} {detail}", file=sys.stderr)


print("== (a) red_ci: 連続 failure のみ検知 ==")
runs = [
    {"workflowName": "verify", "conclusion": "failure", "createdAt": "2026-08-27T10:00:00Z"},
    {"workflowName": "verify", "conclusion": "failure", "createdAt": "2026-08-27T09:00:00Z"},
    {"workflowName": "review", "conclusion": "failure", "createdAt": "2026-08-27T10:00:00Z"},
    {"workflowName": "review", "conclusion": "success", "createdAt": "2026-08-27T09:00:00Z"},
    {"workflowName": "single", "conclusion": "failure", "createdAt": "2026-08-27T10:00:00Z"},
]
s = m.decide_red_ci(runs)
check("連続 2 failure（verify）だけ検知", [x["target"] for x in s] == ["verify"], str(s))
check("直近 success を挟む（review）は非検知", all(x["target"] != "review" for x in s))
check("1 run のみ（single）は非検知", all(x["target"] != "single" for x in s))
runs2 = [
    {"workflowName": "w", "conclusion": None, "createdAt": "2026-08-27T11:00:00Z"},
    {"workflowName": "w", "conclusion": "failure", "createdAt": "2026-08-27T10:00:00Z"},
    {"workflowName": "w", "conclusion": "failure", "createdAt": "2026-08-27T09:00:00Z"},
]
check("実行中（conclusion null）は無視して連続判定",
      len(m.decide_red_ci(runs2)) == 1)

print("== (b) stale_pr: 閾値・stop ラベル・draft ==")
prs = [
    {"number": 1, "title": "old", "createdAt": "2026-08-10T00:00:00Z",
     "labels": [], "isDraft": False},                                   # 18 日 → 検知
    {"number": 2, "title": "fresh", "createdAt": "2026-08-25T00:00:00Z",
     "labels": [], "isDraft": False},                                   # 3 日 → 非検知
    {"number": 3, "title": "held", "createdAt": "2026-08-01T00:00:00Z",
     "labels": [{"name": "human-review-needed"}], "isDraft": False},    # stop → 非検知
    {"number": 4, "title": "draft", "createdAt": "2026-08-01T00:00:00Z",
     "labels": [], "isDraft": True},                                    # draft → 非検知
]
s = m.decide_stale_prs(prs, NOW, stale_days=7)
check("18 日 open のみ検知", [x["target"] for x in s] == ["#1"], str(s))
check("stop ラベル付きは対象外（意図的な保留）", all("#3" != x["target"] for x in s))

print("== (c) review_trigger: 日数近似 ==")
old_epoch = int((NOW - dt.timedelta(days=120)).timestamp())
new_epoch = int((NOW - dt.timedelta(days=10)).timestamp())
files = [{"path": "a.md", "last_commit_epoch": old_epoch},
         {"path": "b.md", "last_commit_epoch": new_epoch}]
s = m.decide_review_trigger(files, NOW, max_days=90)
check("120 日経過のみ検知", [x["target"] for x in s] == ["a.md"], str(s))

print("== (d) ctl_pending: 閾値超のみ ==")
check("11 件 > 10 → 検知", len(m.decide_pending(11, limit=10)) == 1)
check("10 件 = 閾値 → 非検知（超のみ）", m.decide_pending(10, limit=10) == [])

print("== dedup + cap ==")
sigs = [{"detector": "d", "target": str(i), "title": f"[signal:d] t{i}", "body": "x"}
        for i in range(5)]
to_file, dup = m.dedup_and_cap(sigs, open_titles={"[signal:d] t0", "[signal:d] t3"}, cap=3)
check("重複 2 件を skip", dup == 2)
check("上限 3 件に切る（残 3 件がちょうど収まる）",
      [s["title"] for s in to_file] == ["[signal:d] t1", "[signal:d] t2", "[signal:d] t4"])

print("== Issue 本文の不変条件 ==")
body = m.format_issue_body(sigs[0])
check("候補である旨（ready-for-ai を付けない）を明記",
      "候補" in body and "ready-for-ai" in body)
check("決定論であることを明記", "LLM 判定なし" in body)

print("== 検知器 4 本の固定（F1-1） ==")
names = {"decide_red_ci", "decide_stale_prs", "decide_review_trigger", "decide_pending"}
check("判定関数が 4 本とも存在", all(hasattr(m, n) for n in names))

if FAIL:
    sys.exit(f"\nFAIL: {FAIL} 件")
print("\nPASS: signal-scan 回帰テスト 全通過")
