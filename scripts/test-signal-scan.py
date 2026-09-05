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

print("== (e) workflow_silence: 沈黙検知（v6.17.0 F7） ==")
old_run = int((NOW - dt.timedelta(days=120)).timestamp())
new_run = int((NOW - dt.timedelta(days=3)).timestamp())
old_file = int((NOW - dt.timedelta(days=200)).timestamp())
wfs = [
    {"name": "gemini-review.yml", "last_run_epoch": old_run, "file_epoch": old_file},
    {"name": "auto-merge.yml", "last_run_epoch": new_run, "file_epoch": old_file},
    {"name": "never-ran.yml", "last_run_epoch": None, "file_epoch": old_file},
    {"name": "brand-new.yml", "last_run_epoch": None,
     "file_epoch": int((NOW - dt.timedelta(days=5)).timestamp())},
    {"name": "no-basis.yml", "last_run_epoch": None, "file_epoch": None},
]
s = m.decide_workflow_silence(wfs, NOW, max_days=60)
targets = [x["target"] for x in s]
check("120 日沈黙（gemini-review）を検知", "gemini-review.yml" in targets, str(targets))
check("3 日前に走った（auto-merge）は非検知", "auto-merge.yml" not in targets)
check("未起動だがファイルが 200 日前（never-ran）を検知", "never-ran.yml" in targets)
check("未起動だが新設 5 日（brand-new）は非検知＝誤検知しない",
      "brand-new.yml" not in targets)
check("基準時刻が取れない（no-basis）は判定しない", "no-basis.yml" not in targets)

print("== (e) 取得失敗を「run 0 件」と混同しない（PR #248 Copilot 指摘の回帰） ==")
# 取得失敗を last_run_epoch=None に潰すと file_epoch へフォールバックして
# 「沈黙」と誤検知する。聞けなかったことと、聞いた結果 0 件だったことを混同しない。
import subprocess as _sp
_orig_run = m._run


def _stub(gh_behavior):
    def run(cmd):
        if cmd[0] == "gh":
            if gh_behavior == "fail":
                raise _sp.CalledProcessError(1, cmd)
            return gh_behavior
        return "1700000000\n"          # git log の最終 commit epoch
    return run


try:
    m._run = _stub("fail")
    try:
        m.fetch_pr_workflows()
        check("gh 取得失敗は例外を送出する（None に潰さない）", False, "例外が出なかった")
    except _sp.CalledProcessError:
        check("gh 取得失敗は例外を送出する（None に潰さない）", True)

    m._run = _stub('[{"foo": 1}]')
    try:
        m.fetch_pr_workflows()
        check("createdAt 欠落の payload は ValueError", False, "例外が出なかった")
    except ValueError:
        check("createdAt 欠落の payload は ValueError（main の except に乗る）", True)

    m._run = _stub("[]")
    wf = m.fetch_pr_workflows()
    check("run 0 件のときだけ last_run_epoch=None",
          bool(wf) and all(w["last_run_epoch"] is None for w in wf), str(wf)[:120])
    check("その場合も file_epoch は入る（判定側の代替基準）",
          bool(wf) and all(w["file_epoch"] == 1700000000 for w in wf))
finally:
    m._run = _orig_run

print("== (f) metabolism_stall: 未消化が token_budget 超（v6.17.0 F8） ==")
state = {
    "last_reindex_at": "2026-06-07T05:00:00Z",
    "token_budget": 12000,
    "files": [
        {"name": "COUNCIL-LOG.md", "cursor_line": 2287, "total_lines": 3314,
         "undigested_lines": 1027, "undigested_bytes": 92000},
        {"name": "CHANGELOG.md", "cursor_line": 1403, "total_lines": 2340,
         "undigested_lines": 937, "undigested_bytes": 80000},
    ],
}
s = m.decide_metabolism_stall(state, NOW)
check("未消化 43,000 tok > budget 12,000 → 検知", len(s) == 1, str(s))
check("body に最終 reindex からの日数が入る", s and "最終 reindex から" in s[0]["body"])
check("body に token_budget を明記", s and "12,000 tok" in s[0]["body"])
small = dict(state, files=[dict(state["files"][0], undigested_bytes=1000)])
check("未消化 250 tok ≤ budget → 非検知", m.decide_metabolism_stall(small, NOW) == [])
check("cursor 未配備（None）は検知しない", m.decide_metabolism_stall(None, NOW) == [])
check("token_budget 未設定（0）は検知しない",
      m.decide_metabolism_stall(dict(state, token_budget=0), NOW) == [])

print("== タイトル安定性（v6.17.0 F8 の是正・dedup が外れないこと） ==")
# 実害: 日次 cron で age が毎日変わり、タイトル一致の dedup が外れて
# 2026-08-28〜09-05 に同一 3 PR で 27 件の重複 Issue を生んだ。
# 不変条件: 同じ信号は、測定値が変わってもタイトルが変わらない。
pr = [{"number": 1, "title": "x", "createdAt": "2026-08-10T00:00:00Z",
       "labels": [], "isDraft": False}]
t1 = m.decide_stale_prs(pr, NOW, stale_days=7)[0]["title"]
t2 = m.decide_stale_prs(pr, NOW + dt.timedelta(days=30), stale_days=7)[0]["title"]
check("stale_pr: 30 日後も同一タイトル", t1 == t2, f"{t1!r} != {t2!r}")

rt = [{"path": "a.md", "last_commit_epoch": old_epoch}]
r1 = m.decide_review_trigger(rt, NOW, max_days=90)[0]["title"]
r2 = m.decide_review_trigger(rt, NOW + dt.timedelta(days=30), max_days=90)[0]["title"]
check("review_trigger: 30 日後も同一タイトル", r1 == r2, f"{r1!r} != {r2!r}")

check("ctl_pending: 件数が変わっても同一タイトル",
      m.decide_pending(11, limit=10)[0]["title"]
      == m.decide_pending(99, limit=10)[0]["title"])

w1 = m.decide_workflow_silence(wfs, NOW, max_days=60)[0]["title"]
w2 = m.decide_workflow_silence(wfs, NOW + dt.timedelta(days=30), max_days=60)[0]["title"]
check("workflow_silence: 30 日後も同一タイトル", w1 == w2, f"{w1!r} != {w2!r}")

big = dict(state, files=[dict(state["files"][0], undigested_bytes=200000)])
check("metabolism_stall: 測定値が変わっても同一タイトル",
      m.decide_metabolism_stall(state, NOW)[0]["title"]
      == m.decide_metabolism_stall(big, NOW)[0]["title"])

print("== 検知器 6 本の固定（F1-1 + v6.17.0 F7/F8） ==")
names = {"decide_red_ci", "decide_stale_prs", "decide_review_trigger", "decide_pending",
         "decide_workflow_silence", "decide_metabolism_stall"}
check("判定関数が 6 本とも存在", all(hasattr(m, n) for n in names))

if FAIL:
    sys.exit(f"\nFAIL: {FAIL} 件")
print("\nPASS: signal-scan 回帰テスト 全通過")
