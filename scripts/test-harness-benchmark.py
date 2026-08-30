#!/usr/bin/env python3
"""harness-benchmark.py の回帰テスト。合成フィクスチャのみ。実 repo の値は固定しない。

検証項目:
  1. is_agent_commit: trailer / author 名 / 両方欠落 の 3 経路
  2. normalize_state: camelCase(gh) と snake_case(REST) の両方を同形に畳む
  3. flow_metrics: lead time は「初 commit → merge」であって PR open 起点ではない
  4. flow_metrics: 負の lead time（時刻逆転）を捨てる
  5. rework_metrics: **明示参照のみ**を数える（同時期の無関係な fix を拾わない）
  6. rework_metrics: 観測窓の外は数えない / #12 が #1 に誤マッチしない（単語境界）
  7. rework_metrics: 1 PR につき最初の 1 件だけ数える（二重計上しない）
  8. acceptance_metrics: comparable=False を必ず立て、参照値を判定に使わない
  9. review_window: 下限未満の比率
 10. warnings_for: 制御点不在の検出 / rework は常に主指標として提示
 11. 終了コードは常に 0
 12. slice_period: 境界は [since, until)。未 merge の扱い
 13. fetch_merged_from_master が **body を返す**（落とすと rework が過小計上される回帰）
 14. render_compare: 複数計測の横並び。優劣を判定しない

使い方: python3 scripts/test-harness-benchmark.py
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("hb", HERE / "harness-benchmark.py")
assert _spec and _spec.loader
hb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hb)

_failures: list[str] = []
_passes = 0


def check(cond: bool, label: str) -> None:
    global _passes
    if cond:
        _passes += 1
    else:
        _failures.append(label)


def pr(n, *, merged=None, created=None, first=None, title="feat: x", body="",
       agent=True, human=0):
    return {"number": n, "title": title, "body": body, "created_at": created,
            "merged_at": merged, "first_commit": first, "agent_pr": agent,
            "human_commits": human}


# ---- 1. is_agent_commit -------------------------------------------------------

check(hb.is_agent_commit({"author": "鮫島あい", "body": "Co-authored-by: Claude <x@y>"}),
      "1: trailer があれば agent（author 名が人間でも）")
check(hb.is_agent_commit({"author": "Claude", "body": ""}), "1: author 名 Claude は agent")
check(hb.is_agent_commit({"author": "claude[bot]", "body": ""}), "1: claude[bot] は agent")
check(not hb.is_agent_commit({"author": "samejima-ai", "body": "ふつうの本文"}),
      "1: trailer も agent 名も無ければ human")
check(not hb.is_agent_commit({"author": "Your Name", "body": ""}),
      "1: **未設定 author は human 側へ倒す**（介入率が過大 = 安全側）")

# ---- 2. normalize_state -------------------------------------------------------

gh = hb.normalize_state({"number": 7, "title": "t", "createdAt": "2026-01-01T00:00:00Z",
                         "mergedAt": "2026-01-01T01:00:00Z"})
rest = hb.normalize_state({"number": 7, "title": "t", "created_at": "2026-01-01T00:00:00Z",
                           "merged_at": "2026-01-01T01:00:00Z"})
check(gh == rest, "2: gh(camelCase) と REST(snake_case) が同形に畳まれる")
check(hb.normalize_state({"number": 1, "title": "t"})["merged_at"] is None,
      "2: 欠落フィールドは None")

# ---- 3-4. flow_metrics --------------------------------------------------------

f = hb.flow_metrics([
    pr(1, created="2026-01-01T00:00:00Z", first="2026-01-01T00:00:00Z", merged="2026-01-01T02:00:00Z"),
    pr(2, created="2026-01-02T00:00:00Z", first="2026-01-02T00:00:00Z", merged="2026-01-02T00:30:00Z"),
])
check(f["n"] == 2, "3: merged 数")
check(f["lead_median_min"] == 75.0, "3: lead は初 commit 起点（120 分と 30 分 → 中央値 75）")

f2 = hb.flow_metrics([
    pr(1, first="2026-01-01T00:00:00Z", merged="2026-01-01T01:00:00Z"),
    pr(2, first="2026-01-02T05:00:00Z", merged="2026-01-02T00:00:00Z"),   # 時刻逆転
])
check(f2["lead_median_min"] == 60.0, "4: **負の lead time を捨てる**（時刻逆転を混ぜない）")
check(hb.flow_metrics([])["n"] == 0, "3: 空入力で落ちない")

# ---- 5-7. rework_metrics ------------------------------------------------------

base = [
    pr(10, merged="2026-01-01T00:00:00Z", title="feat: 機構"),
    pr(11, merged="2026-01-02T00:00:00Z", title="fix: #10 の取りこぼし", body=""),
]
r = hb.rework_metrics(base)
check(r["reworked"] == 1 and r["rework_rate"] == 0.5, "5: 明示参照した fix を手戻りとして数える")
check(r["recovery_median_h"] == 24.0, "5: 復旧時間 = merge 差分（24h）")

r2 = hb.rework_metrics([
    pr(10, merged="2026-01-01T00:00:00Z", title="feat: 機構"),
    pr(11, merged="2026-01-02T00:00:00Z", title="fix: 別件の修正", body="無関係"),
])
check(r2["reworked"] == 0, "5: **番号を参照しない fix は数えない**（同時期でも拾わない）")

r3 = hb.rework_metrics([
    pr(10, merged="2026-01-01T00:00:00Z"),
    pr(11, merged="2026-03-01T00:00:00Z", title="fix: #10 の修正"),
])
check(r3["reworked"] == 0, "6: 観測窓（14 日）の外は数えない")

r4 = hb.rework_metrics([
    pr(1, merged="2026-01-01T00:00:00Z"),
    pr(2, merged="2026-01-02T00:00:00Z", title="fix: #12 の修正"),
])
check(r4["reworked"] == 0, "6: **#12 が #1 に誤マッチしない**（単語境界）")

r5 = hb.rework_metrics([
    pr(10, merged="2026-01-01T00:00:00Z"),
    pr(11, merged="2026-01-02T00:00:00Z", title="fix: #10 を直す"),
    pr(12, merged="2026-01-03T00:00:00Z", title="fix: #10 をさらに直す"),
])
check(r5["reworked"] == 1, "7: 1 PR につき最初の 1 件だけ（二重計上しない）")

check(hb.rework_metrics([])["rework_rate"] is None, "5: 空入力で 0 除算しない")

# ---- 8. acceptance_metrics ----------------------------------------------------

a = hb.acceptance_metrics([
    pr(1, merged="2026-01-01T00:00:00Z", agent=True, human=0),
    pr(2, merged="2026-01-02T00:00:00Z", agent=True, human=2),
    pr(3, merged=None, agent=True),
    pr(4, merged="2026-01-03T00:00:00Z", agent=False),
])
check(a["agent_prs"] == 3 and a["non_agent_prs"] == 1, "8: agent/非 agent の切り分け")
check(a["merge_rate"] == round(2 / 3, 4), "8: merge 率 = merged / agent 全体（closed 込み）")
check(a["human_commit_rate"] == 0.5, "8: human-commit 率 = merged のうち人間 commit 有り")
check(a["comparable"] is False,
      "8: **comparable=False を必ず立てる**（人間ゲートの有無でプロセスが違う）")
check("reference_display_only" in a and "reference" not in a,
      "8: 参照値は display_only 名で持ち、判定入力に見せない")
check(hb.acceptance_metrics([])["merge_rate"] is None, "8: 空入力で 0 除算しない")

# ---- 9. review_window ---------------------------------------------------------

w = hb.review_window([
    pr(1, created="2026-01-01T00:00:00Z", merged="2026-01-01T00:01:00Z"),   # 1 分
    pr(2, created="2026-01-01T00:00:00Z", merged="2026-01-01T01:00:00Z"),   # 60 分
])
check(w["under_floor"] == 0.5 and w["under_floor_n"] == 1, "9: 下限未満の比率")
check(w["median_min"] == 30.5, "9: 中央値")
check(hb.review_window([])["n"] == 0, "9: 空入力で落ちない")

# ---- 10. warnings_for ---------------------------------------------------------

m = hb.measure([pr(i, merged=f"2026-01-{i:02d}T00:00:00Z", created=f"2026-01-{i:02d}T00:00:00Z",
                   first=f"2026-01-{i:02d}T00:00:00Z", agent=True, human=0) for i in range(1, 13)])
ws = hb.warnings_for(m)
check(any("human-commit" in x for x in ws), "10: 介入率ゼロを検出")
check(any("レビュー窓" in x for x in ws), "10: レビュー窓の不在を検出")
check(any("rework rate" in x for x in ws),
      "10: **rework を常に主指標として提示**（負例が観測できる唯一の指標）")

m2 = hb.measure([pr(1, merged="2026-01-01T00:00:00Z", first="2026-01-01T00:00:00Z",
                    created="2026-01-01T00:00:00Z", agent=True, human=1),
                 pr(2, merged=None, agent=True), pr(3, merged=None, agent=True)])
check(not any("負例を生む制御点" in x for x in hb.warnings_for(m2)),
      "10: 不採用 PR が複数あれば merge 率の WARN を出さない（誤警報しない）")

# ---- 11. 終了コード -----------------------------------------------------------

with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "states.json"
    p.write_text(json.dumps([{"number": 1, "title": "feat: x",
                              "created_at": "2026-01-01T00:00:00Z",
                              "merged_at": "2026-01-01T01:00:00Z"}]), encoding="utf-8")
    for extra in ([], ["--json"]):
        r = subprocess.run([sys.executable, str(HERE / "harness-benchmark.py"),
                            "--states", str(p), *extra], capture_output=True, text=True)
        check(r.returncode == 0, f"11: 終了コード 0（{extra or '既定'}）")

# ---- 12. slice_period ---------------------------------------------------------

rows = [pr(1, merged="2026-01-01T00:00:00Z"), pr(2, merged="2026-02-01T00:00:00Z"),
        pr(3, merged="2026-03-01T00:00:00Z"), pr(4, merged=None)]
check([r["number"] for r in hb.slice_period(rows, "2026-02-01", None)] == [2, 3],
      "12: since は境界を含む（>= since）")
check([r["number"] for r in hb.slice_period(rows, None, "2026-02-01")] == [1, 4],
      "12: until は境界を含まない（< until）")
check([r["number"] for r in hb.slice_period(rows, "2026-02-01", "2026-03-01")] == [2],
      "12: [since, until) の半開区間")
check([r["number"] for r in hb.slice_period(rows, None, None)] == [1, 2, 3, 4],
      "12: 未指定なら素通し")
check(4 not in [r["number"] for r in hb.slice_period(rows, "2026-01-01", None)],
      "12: **since 指定時は未 merge を落とす**（期間に属さないため）")

# ---- 13. fetch_merged_from_master の body 回帰 --------------------------------
# 実バグ: body を落としたまま出荷し、kakuman の rework が 3.7% -> 0.9% に過小計上された。
# 原因は取得層にあり判定層のテストでは捕まらなかったため、_git を差し替えて契約を固定する。

_real_git = hb._git
try:
    hb._git = lambda args: ("fix: 修正 (#11)\x012026-01-02T00:00:00Z\x01#10 の取りこぼしを直す\x02"
                            "feat: 機構 (#10)\x012026-01-01T00:00:00Z\x01本文\x02")
    got = hb.fetch_merged_from_master("origin/master")
    check(set(got) == {10, 11}, "13: PR 番号を拾う")
    check(got[11].get("body") == "#10 の取りこぼしを直す",
          "13: **body を返す**（落とすと rework の明示参照判定が title しか見えなくなる）")
    check(got[10]["merged_at"] == "2026-01-01T00:00:00Z", "13: merge 時刻を拾う")
    merged = [{"number": n, **v} for n, v in got.items()]
    check(hb.rework_metrics(merged)["reworked"] == 1,
          "13: body 込みなら rework が検出される（過小計上しない）")
    stripped = [{k: v for k, v in m.items() if k != "body"} for m in merged]
    check(hb.rework_metrics(stripped)["reworked"] == 0,
          "13: body を落とすと検出できない = このバグの再現")
finally:
    hb._git = _real_git

# ---- 14. render_compare -------------------------------------------------------

ma = hb.measure([pr(1, merged="2026-01-01T00:00:00Z", first="2026-01-01T00:00:00Z",
                    created="2026-01-01T00:00:00Z", agent=True)], "A")
mb = hb.measure([pr(2, merged="2026-01-01T00:00:00Z", first="2026-01-01T00:00:00Z",
                    created="2026-01-01T00:00:00Z", agent=True, human=1)], "B")
check(ma["label"] == "A" and mb["label"] == "B", "14: measure が label を保持する")
out = hb.render_compare([ma, mb])
check("| A | B |" in out, "14: label が見出しになる")
check("rework rate" in out and "介入率" in out, "14: 主要指標が行になる")
check("優劣を判定しない" in out, "14: **優劣を判定しない旨を必ず添える**")
check(hb.render_compare([ma]).count("|") > 0, "14: 1 件でも落ちない")

print(f"passed: {_passes}")
if _failures:
    for x in _failures:
        print(f"FAIL: {x}", file=sys.stderr)
    raise SystemExit(1)
print("ALL PASS")
