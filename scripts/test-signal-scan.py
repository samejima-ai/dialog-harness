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

print("== (f) metabolism_stall: 増分 > 購読量 budget のみで発火（v6.17.0 F8） ==")
# 数えるのは「cursor 記録時点からの増分行数」= total - line。
# cursor の line は「記録時点のファイル長」であって読み進める起点ではないため
# （先頭 append の history では line 以降が最新とは限らない）、
# 「未消化行」ではなく追記方向に依らない代理指標として扱う。
state = {
    "last_reindex_at": "2026-06-07T05:00:00Z",
    "budget_lines": 1200,
    "files": [
        {"name": "COUNCIL-LOG.md", "cursor_line": 2287, "total_lines": 3314,
         "added_lines": 1027},
        {"name": "CHANGELOG.md", "cursor_line": 1403, "total_lines": 2340,
         "added_lines": 937},
    ],
    "anomalies": [],
}
s = m.decide_metabolism_stall(state, NOW)
check("増分 1,964 行 > budget 1,200 行 → 検知", len(s) == 1, str(s))
check("body に最終 reindex からの日数が入る", s and "最終 reindex から" in s[0]["body"])
check("body に budget を行数として明記", s and "1200 行" in s[0]["body"])
check("body で代理指標であることを断る", s and "代理指標" in s[0]["body"])
check("増分 1,964 行 ≤ budget 12,000 行 → 非検知",
      m.decide_metabolism_stall(dict(state, budget_lines=12000), NOW) == [])
check("cursor 未配備（None）は検知しない", m.decide_metabolism_stall(None, NOW) == [])
check("budget 未解決（0）は検知しない",
      m.decide_metabolism_stall(dict(state, budget_lines=0), NOW) == [])
check("引数 budget_lines が state より優先",
      m.decide_metabolism_stall(state, NOW, budget_lines=12000) == [])

# 時間で発火させない。metabolism-regime「リズム（決定2・確定）」が
# 「発火条件は購読量 budget 超過。N-cycle トリガーは棄却」と確定しているため、
# 「最終 reindex から N 日」で起票すると検知器が棄却済みのリズムトリガを復活させる。
quiet = dict(state, budget_lines=12000, last_reindex_at="2020-01-01T00:00:00Z")
check("量が budget 未満なら、何年沈黙していても発火しない（決定2 の尊重）",
      m.decide_metabolism_stall(quiet, NOW) == [])
check("last_reindex_at が壊れていても落ちない",
      len(m.decide_metabolism_stall(dict(state, last_reindex_at="not-a-date"), NOW)) == 1)
# tz 無しの値は naive datetime になり、aware な now との減算が TypeError になる。
# ValueError しか捕まえていないと signal-scan 全体が落ち、
# 「検知器の個別失敗で全体を止めない」契約を (f) 自身が破る。
naive = m.decide_metabolism_stall(dict(state, last_reindex_at="2026-06-07T05:00:00"), NOW)
check("tz 無しの last_reindex_at でも落ちず日数を出す（TypeError の回帰）",
      len(naive) == 1 and "最終 reindex から 81 日" in naive[0]["body"],
      str(naive)[:160])

# cursor > 現末尾 = protocol の異常条件。黙って 0 に丸めず独立の信号にする。
anom = {"last_reindex_at": None, "budget_lines": 0, "files": [],
        "anomalies": [{"name": "INTENT.md", "cursor_line": 1023, "total_lines": 900}]}
s = m.decide_metabolism_stall(anom, NOW)
check("cursor 異常は budget 未解決でも検知", len(s) == 1, str(s))
check("cursor 異常は増分停滞とは別タイトル",
      s and s[0]["title"] != m.decide_metabolism_stall(state, NOW)[0]["title"])

print("== (f) 取得層: 増分は追記方向に依らない / budget は REGIME 優先 ==")
import tempfile, os as _os


def _fixture(root, cursor_line, body_lines, regime=None, config=None):
    hist = _os.path.join(root, "history")
    _os.makedirs(hist, exist_ok=True)
    with open(_os.path.join(hist, ".metabolism-cursor.yml"), "w", encoding="utf-8") as fh:
        fh.write('last_reindex_at: "2026-06-07T05:00:00Z"\ncursor:\n'
                 f'  CHANGELOG.md: {{ line: {cursor_line}, checksum: "sha256:x" }}\n')
    with open(_os.path.join(hist, "CHANGELOG.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(body_lines) + "\n")
    if config is not None:
        with open(_os.path.join(hist, ".metabolism-config.yml"), "w", encoding="utf-8") as fh:
            fh.write(f"metabolism:\n  token_budget: {config}\n")
    if regime is not None:
        with open(_os.path.join(root, "REGIME.md"), "w", encoding="utf-8") as fh:
            fh.write(f"## 情報代謝設定\n\n- token_budget: {regime}\n\n## 次章\n")


with tempfile.TemporaryDirectory() as td:
    # 100 行 → 130 行。先頭に 30 行足しても末尾に 30 行足しても増分は +30。
    head = _fixture
    a = _os.path.join(td, "a"); b = _os.path.join(td, "b")
    old = [f"L{i}" for i in range(100)]
    head(a, 100, ["NEW"] * 30 + old, config=12000)          # 先頭 append
    head(b, 100, old + ["NEW"] * 30, config=12000)          # 末尾 append
    sa = m.fetch_metabolism_state(a)
    sb = m.fetch_metabolism_state(b)
    check("先頭 append でも増分 +30 行", sa["files"][0]["added_lines"] == 30, str(sa))
    check("末尾 append でも増分 +30 行（方向に依らない）",
          sb["files"][0]["added_lines"] == 30, str(sb))
    check("config の token_budget を行数 budget として読む", sa["budget_lines"] == 12000)

with tempfile.TemporaryDirectory() as td:
    _fixture(td, 100, [f"L{i}" for i in range(120)], regime=800, config=12000)
    st = m.fetch_metabolism_state(td)
    check("REGIME.md `## 情報代謝設定` が config より優先（配布先が正本）",
          st["budget_lines"] == 800, str(st["budget_lines"]))

with tempfile.TemporaryDirectory() as td:
    _fixture(td, 200, [f"L{i}" for i in range(100)], config=12000)
    st = m.fetch_metabolism_state(td)
    check("cursor > 現末尾は anomalies へ（増分計数から除外）",
          st["files"] == [] and len(st["anomalies"]) == 1, str(st))

with tempfile.TemporaryDirectory() as td:
    check("cursor 未配備なら None（検知器 skip）", m.fetch_metabolism_state(td) is None)

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

big = dict(state, files=[dict(state["files"][0], added_lines=99999)])
check("metabolism_stall: 増分が変わっても同一タイトル",
      m.decide_metabolism_stall(state, NOW)[0]["title"]
      == m.decide_metabolism_stall(big, NOW)[0]["title"])

print("== 安全弁: 重複判定ができない run では起票しない（v6.17.0 F8 の再発防止） ==")
# 27 件の重複 Issue を生んだのは「タイトルが毎日変わる」ことだったが、
# open タイトルを読めない run で起票すれば同じ山ができる。読めなければ起票しない。
_saved = {n: getattr(m, n) for n in
          ("fetch_master_runs", "fetch_open_prs", "fetch_review_trigger_files",
           "fetch_pending_count", "fetch_pr_workflows", "fetch_metabolism_state",
           "fetch_open_signal_titles", "ensure_label", "create_issue")}
_filed = []
try:
    m.fetch_master_runs = lambda *a, **k: []
    m.fetch_open_prs = lambda: [{"number": 1, "title": "old",
                                 "createdAt": "2020-01-01T00:00:00Z",
                                 "labels": [], "isDraft": False}]
    m.fetch_review_trigger_files = lambda: []
    m.fetch_pending_count = lambda: 0
    m.fetch_pr_workflows = lambda *a, **k: []
    m.fetch_metabolism_state = lambda *a, **k: None
    m.ensure_label = lambda: None
    m.create_issue = lambda sig: _filed.append(sig["title"])

    argv = sys.argv
    sys.argv = ["signal-scan.py"]
    try:
        def _boom():
            raise _sp.CalledProcessError(1, ["gh", "issue", "list"])
        m.fetch_open_signal_titles = _boom
        m.main()
        check("タイトル取得に失敗した run は 1 件も起票しない", _filed == [], str(_filed))

        m.fetch_open_signal_titles = lambda: set()
        m.main()
        check("取得できた run では通常どおり起票する", len(_filed) == 1, str(_filed))
    finally:
        sys.argv = argv
finally:
    for n, f in _saved.items():
        setattr(m, n, f)

print("== 検知器 6 本の固定（F1-1 + v6.17.0 F7/F8） ==")
names = {"decide_red_ci", "decide_stale_prs", "decide_review_trigger", "decide_pending",
         "decide_workflow_silence", "decide_metabolism_stall"}
check("判定関数が 6 本とも存在", all(hasattr(m, n) for n in names))

if FAIL:
    sys.exit(f"\nFAIL: {FAIL} 件")
print("\nPASS: signal-scan 回帰テスト 全通過")
