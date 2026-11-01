#!/usr/bin/env python3
"""gate-metrics.py の回帰テスト（オフライン・gh/git 不要）。

取得層（fetch_prs / read_regime_log）は呼ばず、判定層の純粋関数に fixture を
渡して検証する（pr-audit のテスト方針を踏襲。CI では gh 認証が保証されない）。
"""

import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "gate_metrics", Path(__file__).parent / "gate-metrics.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FAIL = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAIL
    if cond:
        print(f"  ok: {name}")
    else:
        FAIL += 1
        print(f"FAIL: {name} {detail}", file=sys.stderr)


def pr(number: int, *, merged: bool = True, labels: list[str] | None = None,
       title: str = "t", merged_by: str = "github-actions[bot]") -> dict:
    return {
        "number": number,
        "title": title,
        "mergedAt": "2026-09-11T11:20:15Z" if merged else None,
        "labels": [{"name": n} for n in (labels or [])],
        "mergedBy": {"login": merged_by} if merged else None,
    }


LOG_TWO_MISJUDGE = """
## auto-merge メタ承認機構 — AI 判定漏れ記録 #1（2026-08-26）

- **対象**: PR #196（`ci(harness-verify): ...`）

## auto-merge メタ承認機構 — AI 判定漏れ記録 #2（2026-09-11）

- **対象**: PR #280（`feat(quota): ...`）
"""


# ---- ラベル判定 -------------------------------------------------------------

check("旧 auto-merge ラベルを検出", m.has_legacy_label(pr(1, labels=["auto-merge"])))
check("旧ラベル無しは非検出", not m.has_legacy_label(pr(1, labels=["feat"])))
check("stop ラベル human-review-needed を検出",
      m.has_stop_label(pr(1, labels=["human-review-needed"])))
check("stop ラベル do-not-merge を検出", m.has_stop_label(pr(1, labels=["do-not-merge"])))
check("無関係ラベルは stop でない", not m.has_stop_label(pr(1, labels=["docs"])))

# ---- 二重ラベル腐敗 ---------------------------------------------------------

corrupt = m.find_legacy_label_corruption([
    pr(10, labels=["auto-merge"]),
    pr(11, labels=["feat"]),
    pr(12, merged=False, labels=["auto-merge"]),  # 未 merge は該当しない
])
check("二重ラベル腐敗は merged のみ数える", [p["number"] for p in corrupt] == [10],
      f"got {corrupt}")

# ---- 暗黙 merge の機械検知部分集合 -------------------------------------------

check("bot merge は実行者で判別できる",
      m.merge_actor_is_distinguishable(pr(1, merged_by="github-actions[bot]")))
check("PAT merge は実行者で判別できない（PR #196 の形）",
      not m.merge_actor_is_distinguishable(pr(1, merged_by="samejima-ai")))
check("実行者不明も判別できない", not m.merge_actor_is_distinguishable(pr(1, merged_by="")))

sub = m.merged_with_stop_label([
    pr(20, labels=["human-review-needed"]),
    pr(21, labels=[]),                                                 # ラベル無し
    pr(22, merged=False, labels=["do-not-merge"]),                     # 未 merge
    pr(23, labels=["human-review-needed"], merged_by="samejima-ai"),
])
check("stop ラベル付き merged を候補として列挙（実行者で絞らない）",
      [p["number"] for p in sub] == [20, 23], f"got {sub}")
check("候補に判別可否フラグが付く",
      sub[1]["actor_distinguishable"] is False, f"got {sub}")

# ---- REGIME-LOG の記録計数 ---------------------------------------------------

ids = m.count_records(LOG_TWO_MISJUDGE, m.MISJUDGE_HEADING)
check("判定漏れ記録を 2 件数える", sorted(ids) == [1, 2], f"got {ids}")
check("暗黙 merge 記録は未記録なら 0 件",
      m.count_records(LOG_TWO_MISJUDGE, m.IMPLICIT_HEADING) == [])
check("境界曖昧化記録は未記録なら 0 件",
      m.count_records(LOG_TWO_MISJUDGE, m.AMBIGUITY_HEADING) == [])
check("対象 PR 番号を抽出", sorted(m.recorded_target_prs(LOG_TWO_MISJUDGE)) == [196, 280],
      f"got {m.recorded_target_prs(LOG_TWO_MISJUDGE)}")

# ---- compute の統合 ---------------------------------------------------------

prs = [pr(n) for n in range(1, 41)]  # merged 40 件
stats = m.compute(prs, LOG_TWO_MISJUDGE)
check("merged 件数", stats["merged_prs"] == 40, f"got {stats['merged_prs']}")
check("判定漏れ率 = 2/40 = 5.0%", abs(stats["misjudgment"]["rate_pct"] - 5.0) < 1e-9,
      f"got {stats['misjudgment']['rate_pct']}")
check("人間観測指標に needs_human_label が立つ",
      stats["implicit_merge"]["needs_human_label"]
      and stats["boundary_ambiguity"]["needs_human_label"])

# 母数 0 でも落ちない
empty = m.compute([], "")
check("merged 0 件で rate は None", empty["misjudgment"]["rate_pct"] is None)

# ---- 閾値判定 ---------------------------------------------------------------

check("5.0% ちょうどは『超』でないので非該当",
      not any("判定漏れ率" in v for v in m.verdict(stats)),
      f"got {m.verdict(stats)}")

over = m.compute([pr(n) for n in range(1, 21)], LOG_TWO_MISJUDGE)  # 2/20 = 10%
check("10% は閾値超過として列挙", any("判定漏れ率" in v for v in m.verdict(over)),
      f"got {m.verdict(over)}")

leg = m.compute([pr(1, labels=["auto-merge"])], "")
check("二重ラベル 1 件で即 roll-back 事由",
      any("二重ラベル腐敗" in v for v in m.verdict(leg)), f"got {m.verdict(leg)}")

# ---- レンダリング -----------------------------------------------------------

md = m.render_markdown(stats, "2026-11-06")
check("markdown に 4 指標が出る",
      all(k in md for k in ["暗黙 merge 事故件数", "AI 判定漏れ率",
                            "境界曖昧化事例", "二重ラベル腐敗"]))
check("markdown に要人間ラベル付与節がある", "## 要人間ラベル付与" in md)
check("markdown は判断を下さないと明記", "判断そのものではない" in md)

print(f"\n{'FAILED: ' + str(FAIL) if FAIL else 'all passed'}")
sys.exit(1 if FAIL else 0)
