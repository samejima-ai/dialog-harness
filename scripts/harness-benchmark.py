#!/usr/bin/env python3
"""harness-benchmark — DH ハーネスの送出性能を世界水準の指標で決定論計測する。

`scripts/pr-audit.py`（W9 受入監査）の姉妹。pr-audit が **gh CLI** を要求するのに対し、
本ツールは **git だけ**で動く。鍵は GitHub が公開する `refs/pull/*/head`:

    git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'

これで全 PR の**元 commit 列**（squash merge で master からは失われる）がローカルに揃い、
commit 単位の agent/human 判定・PR サイズ・初 commit 時刻がオフラインで取れる。

## 測る指標

**フロー（DORA 系）** — 人間ゲートの有無に依存しない。他組織と比較可能:
  - deployment frequency : master への merge 頻度（DH は repo 配布ゆえ merge ≒ リリース）
  - change lead time     : PR ブランチ初 commit → merge
  - deployment rework rate: merge 後 N 日以内に、その PR 番号を明示参照する fix/revert が入った比
                           （DORA が 5 指標へ拡張した際に追加した「rework rate」に対応）
  - failed deployment recovery time: 上記 rework までの経過時間

**受入（W9 系）** — `--states` を渡したときのみ。**解釈に注意**（下記）:
  - merge 率 / revert 率 / human-commit 介入率

## 最重要の解釈上の制約: W9 は人間ゲートのある系でしか意味を持たない

参照系（dotnet/runtime）の merge 67.9% / human-commit 45% は、**全 PR が人間レビューを
通る**プロセスの下での値である。DH は opt-out auto-merge（stop ラベル不在なら自動 merge）を
意図的に採っており、人間が触らないのが既定である。したがって DH 側の merge 率が高く
human-commit 率が低いことは「品質が高い」ことを意味しない — **負例を生む制御点が
プロセス上に存在しない**ことを意味する。両者を直接比較して優劣を言ってはならない。

本ツールはこの区別を出力上も維持する: フロー指標には参照値を併記するが、
W9 指標には **「比較不能」と明示**し、参照値を判定に使わない（Goodhart 回避、pr-audit I-4 と同型）。

対照的に rework rate は**成果物（後続 PR の明示参照）から導くため負例が観測できる**。
自己申告フィールドにも人間ゲートにも依存しない唯一の品質指標であり、本ツールの主産物である。

**LLM 判定を一切含まない。** 集計のみ。終了コードは常に 0（warn のみ・block しない）。

## 比較しないと、値が何を意味するか決まらない

単独の rework 10.9% は高いのか低いのか決まらない。**比較対象を 2 方向で取れる**:

- **横断（別プロジェクト）**: 同じハーネスを積んだ別 repo で同じ計測を回す。
  ドメインが違っても値が一致する指標は**ハーネスの性質**、ばらつく指標は
  **プロジェクトの性質**を拾っている（＝指標として働いている）
- **時系列（自己比較）**: `--since` / `--until` で期間を切る。外部ベースライン不要で
  「改善しているか」に答えられる。dotnet/runtime 自身もこの形で成功率の推移を出している

`--compare` は `--json` の出力を複数受け取り、横並びの表にする。

## 使い方

    git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'   # 前提
    python3 scripts/harness-benchmark.py
    python3 scripts/harness-benchmark.py --states prs.json   # W9 も出す
    python3 scripts/harness-benchmark.py --json

    # 横断: 別 repo でも同じツールが動く（cwd をその repo にする）
    cd ../other-repo && python3 ../dh/scripts/harness-benchmark.py \
        --base origin/main --label other --json > other.json

    # 時系列: 期間で切る
    python3 scripts/harness-benchmark.py --since 2026-06-01 --until 2026-07-15 --json > q2.json

    # 横並び
    python3 scripts/harness-benchmark.py --compare dh.json other.json q2.json

`--states` は `[{"number":1,"title":"...","created_at":"...","merged_at":"..."|null}, ...]`。
gh なら `gh pr list --state closed --limit 500 --json number,title,createdAt,mergedAt`、
GitHub MCP なら list_pull_requests の出力をそのまま渡せる（camelCase / snake_case 両対応）。
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from datetime import datetime, timedelta

# agent commit の判定（pr-audit.py と同一規約）
CLAUDE_TRAILER = re.compile(r"Co-authored-by:.*Claude", re.I)
AGENT_AUTHOR_NAMES = {"claude", "claude[bot]"}
FIX_TITLE = re.compile(r"^(fix|revert)", re.I)
PR_SUFFIX = re.compile(r"\(#(\d+)\)\s*$")

# rework の観測窓（日）。DORA の rework rate に窓の定義は無いため、本ツールの運用定義。
REWORK_WINDOW_DAYS = 14

# フロー指標の参照値。**表示のみ・判定に使わない。**
# DORA のクラスタ境界は年ごとの cluster analysis で再導出され固定閾値ではない
# （2022 年は Elite クラスタ自体が出現しなかった）。広く引かれる下記は 2023/2024 断面の目安。
FLOW_REFERENCE = {
    "lead_time_elite": "1 日未満",
    "deploy_freq_elite": "オンデマンド（1 日複数回）",
    "rework_rate_note": "DORA は rework rate を 5 指標へ拡張時に追加。固定閾値は公表されていない",
}
# W9 参照値（dotnet/runtime 10 ヶ月・878 PR / 535 merged）。**比較不能**として併記のみ。
W9_REFERENCE = {"merge_rate": 0.679, "revert_rate": 0.006, "human_commit_rate": 0.45}


def _git(args: list[str]) -> str:
    return subprocess.run(["git"] + args, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


# ---- 判定層（純粋関数・オフラインテスト対象）--------------------------------


def is_agent_commit(c: dict) -> bool:
    """trailer あり、または author 名が agent。pr-audit の (i)/(ii) と同規約。"""
    if CLAUDE_TRAILER.search(c.get("body") or ""):
        return True
    return (c.get("author") or "").strip().lower() in AGENT_AUTHOR_NAMES


def normalize_state(p: dict) -> dict:
    """gh(camelCase) / GitHub REST(snake_case) 双方の PR 状態を 1 形式へ。"""
    return {
        "number": p.get("number"),
        "title": p.get("title") or "",
        "body": p.get("body") or "",
        "created_at": p.get("created_at") or p.get("createdAt"),
        "merged_at": p.get("merged_at") or p.get("mergedAt"),
    }


def flow_metrics(prs: list[dict]) -> dict:
    """merge 済み PR 群からフロー指標を出す。prs は merged_at と first_commit を持つ。"""
    merged = sorted([p for p in prs if p.get("merged_at") and p.get("first_commit")],
                    key=lambda p: p["merged_at"])
    if not merged:
        return {"n": 0}
    lead = []
    for p in merged:
        d = (parse_dt(p["merged_at"]) - parse_dt(p["first_commit"])).total_seconds() / 60
        if d >= 0:
            lead.append(d)
    span_days = (parse_dt(merged[-1]["merged_at"]) - parse_dt(merged[0]["merged_at"])).total_seconds() / 86400
    active = {p["merged_at"][:10] for p in merged}
    srt = sorted(lead)
    return {
        "n": len(merged),
        "first_merge": merged[0]["merged_at"],
        "last_merge": merged[-1]["merged_at"],
        "span_days": round(span_days, 1),
        "per_day": round(len(merged) / span_days, 2) if span_days else None,
        "per_week": round(len(merged) / (span_days / 7), 1) if span_days else None,
        "active_days": len(active),
        "lead_median_min": round(statistics.median(lead), 1) if lead else None,
        "lead_mean_min": round(statistics.mean(lead), 1) if lead else None,
        "lead_p90_min": round(srt[int(0.9 * len(srt))], 1) if lead else None,
        "lead_under_1h": round(sum(1 for x in lead if x < 60) / len(lead), 4) if lead else None,
        "lead_under_1d": round(sum(1 for x in lead if x < 1440) / len(lead), 4) if lead else None,
    }


def rework_metrics(prs: list[dict], window_days: int = REWORK_WINDOW_DAYS) -> dict:
    """後続の fix/revert PR が当該 PR 番号を**明示参照**した場合のみ手戻りと数える。

    ファイル重複による推定（loose）は、小規模 repo でコア file を共有するだけで
    成立してしまい過大計上になる。明示参照は下界だが誤検出がほぼ無い。
    """
    merged = sorted([p for p in prs if p.get("merged_at")], key=lambda p: p["merged_at"])
    win = timedelta(days=window_days)
    hits = []
    for i, p in enumerate(merged):
        t = parse_dt(p["merged_at"])
        for q in merged[i + 1:]:
            dt_q = parse_dt(q["merged_at"])
            if dt_q - t > win:
                break
            if not FIX_TITLE.match(q["title"]):
                continue
            if re.search(rf'#{p["number"]}\b', (q["title"] or "") + "\n" + (q.get("body") or "")):
                hits.append({"pr": p["number"], "fix": q["number"],
                             "hours": round((dt_q - t).total_seconds() / 3600, 1)})
                break
    hrs = [h["hours"] for h in hits]
    srt = sorted(hrs)
    return {
        "window_days": window_days,
        "denominator": len(merged),
        "reworked": len(hits),
        "rework_rate": round(len(hits) / len(merged), 4) if merged else None,
        "recovery_median_h": round(statistics.median(hrs), 1) if hrs else None,
        "recovery_p90_h": round(srt[int(0.9 * len(srt))], 1) if hrs else None,
        "recovery_under_24h": round(sum(1 for x in hrs if x < 24) / len(hrs), 4) if hrs else None,
        "pairs": hits,
    }


def acceptance_metrics(prs: list[dict]) -> dict:
    """W9。**比較不能**の注記付きでのみ出す（人間ゲートの有無でプロセスが違うため）。"""
    agent = [p for p in prs if p.get("agent_pr")]
    merged = [p for p in agent if p.get("merged_at")]
    human = [p for p in merged if p.get("human_commits", 0) > 0]
    return {
        "agent_prs": len(agent),
        "non_agent_prs": len(prs) - len(agent),
        "merged": len(merged),
        "closed_unmerged": len(agent) - len(merged),
        "merge_rate": round(len(merged) / len(agent), 4) if agent else None,
        "human_commit_prs": len(human),
        "human_commit_rate": round(len(human) / len(merged), 4) if merged else None,
        "comparable": False,
        "incomparable_reason": (
            "参照系は全 PR が人間レビューを通る。DH は opt-out auto-merge で人間が触らないのが既定ゆえ、"
            "負例を生む制御点がプロセス上に存在しない。高い merge 率・低い human-commit 率は"
            "品質ではなく制御点の不在を示す"
        ),
        "reference_display_only": W9_REFERENCE,
    }


def review_window(prs: list[dict], floor_min: float = 5.0) -> dict:
    """PR open → merge。人間が diff を読む時間が物理的にあったかの下限チェック。"""
    xs = []
    for p in prs:
        if p.get("merged_at") and p.get("created_at"):
            d = (parse_dt(p["merged_at"]) - parse_dt(p["created_at"])).total_seconds() / 60
            if d >= 0:
                xs.append(d)
    if not xs:
        return {"n": 0}
    return {
        "n": len(xs),
        "median_min": round(statistics.median(xs), 1),
        "floor_min": floor_min,
        "under_floor": round(sum(1 for x in xs if x < floor_min) / len(xs), 4),
        "under_floor_n": sum(1 for x in xs if x < floor_min),
    }


# ---- 取得層（git・テストでは呼ばない）----------------------------------------


def fetch_pr_refs() -> set[int]:
    out = _git(["for-each-ref", "refs/remotes/origin/pr", "--format=%(refname:short)"])
    return {int(r.rsplit("/", 1)[1]) for r in out.split() if r.rsplit("/", 1)[1].isdigit()}


def fetch_pr_commits(number: int, base: str = "origin/master") -> list[dict] | None:
    r = subprocess.run(["git", "log", f"{base}..origin/pr/{number}",
                        "--format=%H\x01%an\x01%aI\x01%b\x02"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return None
    out = []
    for rec in r.stdout.split("\x02"):
        rec = rec.strip("\n")
        if not rec.strip():
            continue
        parts = (rec.split("\x01") + [""] * 4)[:4]
        out.append({"sha": parts[0], "author": parts[1], "date": parts[2], "body": parts[3]})
    return out


def fetch_merged_from_master(base: str = "origin/master") -> dict[int, dict]:
    """master の squash commit から PR 番号・merge 時刻・**本文**を得る（--states 不在時の代替）。

    **body を必ず拾う。** squash merge の commit body には PR 本文が入っており、
    rework の「先行 PR 番号を明示参照」判定はそこを読む。body を落とすと参照が
    title 内に書かれた分しか見えず、**rework が系統的に過小計上される**
    （実測: kakuman で body 込み 3.7% → title のみ 0.9%）。
    """
    out: dict[int, dict] = {}
    log = _git(["log", base, "--format=%s\x01%aI\x01%b\x02"])
    for rec in log.split("\x02"):
        rec = rec.strip("\n")
        if not rec.strip():
            continue
        parts = (rec.split("\x01") + [""] * 3)[:3]
        m = PR_SUFFIX.search(parts[0])
        if m:
            out[int(m.group(1))] = {"title": parts[0], "merged_at": parts[1], "body": parts[2]}
    return out


def build(states_path: str | None, base: str) -> list[dict]:
    refs = fetch_pr_refs()
    if not refs:
        sys.stderr.write(
            "PR head ref がありません。先に実行してください:\n"
            "  git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'\n")
        return []
    if states_path:
        raw = json.load(open(states_path, encoding="utf-8"))
        states = {s["number"]: s for s in (normalize_state(p) for p in raw) if s["number"]}
    else:
        states = {n: normalize_state({"number": n, **v})
                  for n, v in fetch_merged_from_master(base).items()}

    prs = []
    for n, s in states.items():
        cs = fetch_pr_commits(n, base) if n in refs else None
        rec = dict(s)
        if cs:
            rec["first_commit"] = min(c["date"] for c in cs)
            rec["n_commits"] = len(cs)
            rec["agent_pr"] = any(is_agent_commit(c) for c in cs)
            rec["human_commits"] = sum(1 for c in cs if not is_agent_commit(c))
        else:
            rec["first_commit"] = None
            rec["agent_pr"] = False
            rec["human_commits"] = 0
        prs.append(rec)
    return prs


# ---- 出力 -------------------------------------------------------------------


def slice_period(prs: list[dict], since: str | None, until: str | None) -> list[dict]:
    """merge 日で期間を切る。境界は [since, until)。未 merge は since 指定時に落とす。"""
    out = []
    for p in prs:
        d = (p.get("merged_at") or "")[:10]
        if since and (not d or d < since):
            continue
        if until and d and d >= until:
            continue
        out.append(p)
    return out


def measure(prs: list[dict], label: str = "this") -> dict:
    agent = [p for p in prs if p.get("agent_pr")]
    return {
        "label": label,
        "prs_total": len(prs),
        "flow": flow_metrics(agent),
        "rework": rework_metrics([p for p in agent if p.get("merged_at")]),
        "acceptance": acceptance_metrics(prs),
        "review_window": review_window(agent),
    }


def render(m: dict) -> str:
    def pct(v):
        return f"{v*100:.1f}%" if v is not None else "n/a"
    f, r, a, w = m["flow"], m["rework"], m["acceptance"], m["review_window"]
    L = ["# DH ハーネス送出性能 — 世界水準ベンチマーク", "",
         f"- 対象 PR {m['prs_total']} 件（うち agent PR {a['agent_prs']}）", ""]
    L += ["## 1. フロー指標（人間ゲートの有無に依存しない = 比較可能）", "",
          "| 指標 | 実測 | 参照（DORA・目安） |", "|---|---|---|"]
    if f.get("n"):
        L += [f"| deployment frequency | {f['per_day']}/日（{f['per_week']}/週・"
              f"{f['n']} merge / {f['span_days']} 日・稼働 {f['active_days']} 日） | {FLOW_REFERENCE['deploy_freq_elite']} |",
              f"| change lead time（初 commit → merge） | 中央値 {f['lead_median_min']} 分 / "
              f"p90 {f['lead_p90_min']} 分 / 1 日以内 {pct(f['lead_under_1d'])} | {FLOW_REFERENCE['lead_time_elite']} |"]
    L += [f"| deployment rework rate | {pct(r['rework_rate'])}（{r['reworked']}/{r['denominator']}・"
          f"{r['window_days']} 日窓・明示参照のみ） | {FLOW_REFERENCE['rework_rate_note']} |",
          f"| failed deployment recovery | 中央値 {r['recovery_median_h']} 時間 / "
          f"24 時間以内 {pct(r['recovery_under_24h'])} | — |", ""]
    L += ["## 2. 受入指標（W9）— **比較不能**", "",
          "| 指標 | 実測 | 参照 (dotnet/runtime) |", "|---|---|---|",
          f"| merge 率 | {pct(a['merge_rate'])}（{a['merged']}/{a['agent_prs']}） | {pct(W9_REFERENCE['merge_rate'])} |",
          f"| human-commit 介入率 | {pct(a['human_commit_rate'])}（{a['human_commit_prs']}/{a['merged']}） | {pct(W9_REFERENCE['human_commit_rate'])} |",
          "", f"> **{a['incomparable_reason']}。** 参照値は併記のみで判定に使わない。", ""]
    if w.get("n"):
        L += ["## 3. レビュー窓（制御点が実在したかの下限チェック）", "",
              f"- PR open → merge 中央値 **{w['median_min']} 分**",
              f"- 人間が diff を読む下限を {w['floor_min']:.0f} 分と置くと、"
              f"**{pct(w['under_floor'])}（{w['under_floor_n']}/{w['n']}）はレビュー不可能な速さで merge されている**", ""]
    L += ["## 総括", ""]
    for x in warnings_for(m):
        L += [f"- WARN: {x}"]
    L += ["", "> 集計のみ・LLM 判定なし。是正の判断は人間（D5）に残る（philosophy.md 第 6 条）。"]
    return "\n".join(L)


def render_compare(ms: list[dict]) -> str:
    """複数の計測結果を横並びにする。**判定はしない** — 差を見せるだけ。"""
    def pct(v):
        return f"{v*100:.1f}%" if v is not None else "n/a"
    def num(v, unit=""):
        return f"{v}{unit}" if v is not None else "n/a"
    heads = [m.get("label") or "?" for m in ms]
    L = ["# ハーネス送出性能の比較", "",
         "| 指標 | " + " | ".join(heads) + " |",
         "|---|" + "---|" * len(ms)]
    rows = [
        ("agent PR 数", lambda m: str(m["acceptance"]["agent_prs"])),
        ("観測期間（日）", lambda m: num(m["flow"].get("span_days"))),
        ("deployment frequency", lambda m: num(m["flow"].get("per_day"), "/日")),
        ("change lead time 中央値", lambda m: num(m["flow"].get("lead_median_min"), " 分")),
        ("lead time 1 日以内", lambda m: pct(m["flow"].get("lead_under_1d"))),
        ("deployment rework rate", lambda m: pct(m["rework"]["rework_rate"])),
        ("復旧時間 中央値", lambda m: num(m["rework"].get("recovery_median_h"), " 時間")),
        ("human-commit 介入率", lambda m: pct(m["acceptance"]["human_commit_rate"])),
    ]
    for name, f in rows:
        L.append(f"| {name} | " + " | ".join(f(m) for m in ms) + " |")
    L += ["",
          "> **読み方**: ドメインが違っても値が揃う指標は**ハーネスの性質**、ばらつく指標は"
          "**プロジェクトの性質**を拾っている（＝判別力がある）。",
          "> 本表は差を示すだけで優劣を判定しない — 比較先のプロセス（人間ゲートの有無）が"
          "違えば受入指標は元から比較不能である（§2）。"]
    return "\n".join(L)


def warnings_for(m: dict) -> list[str]:
    out = []
    a, w, r = m["acceptance"], m["review_window"], m["rework"]
    if a["merge_rate"] is not None and a["merge_rate"] >= 0.95 and a["closed_unmerged"] <= 1:
        out.append(f"merge 率 {a['merge_rate']*100:.1f}% で不採用がほぼ無い — "
                   "負例を生む制御点がプロセス上にあるかを人間が確認すること")
    if a["human_commit_rate"] is not None and a["human_commit_rate"] < 0.05:
        out.append(f"human-commit 介入率 {a['human_commit_rate']*100:.1f}% — "
                   "人間が agent の diff に手を入れた形跡がほぼ無い")
    if w.get("n") and w["under_floor"] > 0.2:
        out.append(f"PR の {w['under_floor']*100:.0f}% が {w['floor_min']:.0f} 分未満で merge — "
                   "レビュー窓が物理的に存在しない")
    if r["rework_rate"] is not None:
        out.append(f"rework rate {r['rework_rate']*100:.1f}% は**負例が観測できる唯一の品質指標** — "
                   "自己申告にも人間ゲートにも依存しないため、ここを主指標に置くのが妥当")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="DH ハーネス送出性能の決定論計測",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--states", default=None, help="PR 状態 JSON（gh / GitHub MCP の出力）")
    ap.add_argument("--base", default="origin/master", help="基準ブランチ")
    ap.add_argument("--label", default="this", help="比較表での見出し名")
    ap.add_argument("--since", default=None, help="この日以降に merge された PR のみ（YYYY-MM-DD）")
    ap.add_argument("--until", default=None, help="この日より前に merge された PR のみ（YYYY-MM-DD）")
    ap.add_argument("--compare", nargs="+", default=None,
                    help="--json 出力を複数受け取り横並びにする（計測はしない）")
    ap.add_argument("--json", action="store_true", help="機械可読出力")
    args = ap.parse_args()

    if args.compare:
        ms = []
        for f in args.compare:
            try:
                ms.append(json.load(open(f, encoding="utf-8")))
            except (OSError, ValueError) as e:
                sys.stderr.write(f"読めません {f}: {e}\n")
        if ms:
            print(render_compare(ms))
        return 0

    try:
        prs = build(args.states, args.base)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        sys.stderr.write(f"取得失敗（git が必要）: {e}\n")
        return 0
    if not prs:
        return 0

    prs = slice_period(prs, args.since, args.until)
    if not prs:
        sys.stderr.write("期間内に PR がありません\n")
        return 0
    m = measure(prs, args.label)
    print(json.dumps({**m, "warnings": warnings_for(m)}, ensure_ascii=False, indent=2)
          if args.json else render(m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
