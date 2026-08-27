#!/usr/bin/env python3
"""pr-audit — agent PR の受入・介入を決定論で計測する（v6.15.0 F2）。

世界水準の事実上の標準指標（ANALYSIS-agentic-sdlc-world-standard-2026-08-28 §W9、
dotnet/runtime 実測が参照系）を、gh CLI + git log だけで算出する。LLM 判定を含まない。

指標（F2-1）:
  - merge 率        : agent 発 PR のうち merged / (merged + closed-unmerged)
  - revert 率       : merged agent PR のうち、その後 master で revert された比
  - human-commit 率 : merged agent PR のうち、人間の直接 commit が積まれた比
  - 種別別受入率    : conventional-commit prefix（feat/fix/docs/...）別の merge 率

agent PR の判定（spec 判断点 4 の実装確定）:
  spec は「author が ALLOWED_AUTHORS」を提案したが、本リポジトリでは人間 PR も agent PR も
  同一アカウント（git user）で作られるため author では分離できない。代わりに
  **commit 単位の 2 条件の OR** で判定する（実データ検証: PR #198/#199 は trailer 無しで
  authors に login "claude" を持つ = cloud セッション直 commit。PR #200 は trailer 併用）:
    (i)  commit body に trailer `Co-Authored-By: Claude`
    (ii) commit の authors[] に login "claude"
  PR 内に agent commit が 1 つ以上 → agent PR。agent PR 内の**非** agent commit →
  human commit（介入）。両条件を欠く agent commit は human 側に誤算入される
  （介入率が過大 = 安全側）。

参照値（F2-2・目標値ではない）:
  dotnet/runtime 10 ヶ月実測 — merge 67.9% / revert 0.6% / human-commit 介入 45%

使い方:
    python3 scripts/pr-audit.py                    # 直近 100 PR を集計して stdout へ
    python3 scripts/pr-audit.py --limit 200
    python3 scripts/pr-audit.py --out delivery/PR-AUDIT-2026-08.md
    python3 scripts/pr-audit.py --json             # 機械可読出力

CTL の agreement_rate（判断への同意）とは別軸（F2-4）。混ぜない。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

CLAUDE_TRAILER = re.compile(r"Co-Authored-By:.*Claude", re.I)
REVERT_PR = re.compile(r"^Revert\b.*\(#(\d+)\)|^Revert\s+\"[^\"]*\(#(\d+)\)\"", re.M)
TYPE_PREFIX = re.compile(r"^([a-z]+)(?:\(|!|:)")

# 参照値（dotnet/runtime、ANALYSIS §2-C）。表示のみ・判定に使わない（I-4 Goodhart 回避）
REFERENCE = {"merge_rate": 0.679, "revert_rate": 0.006, "human_commit_rate": 0.45}


def _gh(args: list[str]) -> str:
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def _git(args: list[str]) -> str:
    return subprocess.run(["git"] + args, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


# ---- 取得層（テストでは呼ばない） ------------------------------------------


def fetch_prs(limit: int) -> list[dict]:
    """closed（merged 含む）PR を commit メッセージ付きで取得する。

    一括 `--json commits` は GraphQL の node 上限（commits×authors）を limit 60 程度で
    超過するため（実測: "exceeds the maximum limit of 500,000"）、一覧と commit 取得を
    分離し PR 単位で引く。
    """
    raw = _gh(["pr", "list", "--state", "closed", "--limit", str(limit),
               "--json", "number,title,mergedAt"])
    prs = json.loads(raw)
    for p in prs:
        c = _gh(["pr", "view", str(p["number"]), "--json", "commits"])
        p["commits"] = json.loads(c).get("commits") or []
    return prs


def fetch_reverted_pr_numbers() -> set[int]:
    """master の Revert commit から、revert された PR 番号を決定論で抽出する。"""
    log = _git(["log", "origin/master", "--grep", "^Revert", "--format=%s"])
    nums: set[int] = set()
    for m in REVERT_PR.finditer(log):
        nums.add(int(m.group(1) or m.group(2)))
    return nums


# ---- 判定層（純粋関数・オフラインテスト対象） --------------------------------


def _is_agent_commit(c: dict) -> bool:
    """(i) Claude trailer あり、または (ii) authors に login 'claude'。"""
    if CLAUDE_TRAILER.search(c.get("messageBody") or ""):
        return True
    return any((a.get("login") or "").lower() == "claude"
               for a in c.get("authors") or [])


def is_agent_pr(pr: dict) -> bool:
    """PR 内に agent commit が 1 つ以上あれば agent PR。"""
    return any(_is_agent_commit(c) for c in pr.get("commits") or [])


def has_human_commit(pr: dict) -> bool:
    """agent PR 内の非 agent commit = 人間の直接介入。"""
    return any(not _is_agent_commit(c) for c in pr.get("commits") or [])


def classify_type(title: str) -> str:
    m = TYPE_PREFIX.match(title)
    return m.group(1) if m else "other"


def compute(prs: list[dict], reverted: set[int]) -> dict:
    """指標の一括算出。入力は fetch 層の形式（テストでは fixture を渡す）。"""
    agent = [p for p in prs if is_agent_pr(p)]
    merged = [p for p in agent if p.get("mergedAt")]
    closed = [p for p in agent if not p.get("mergedAt")]
    rev = [p for p in merged if p["number"] in reverted]
    human = [p for p in merged if has_human_commit(p)]

    by_type: dict[str, dict] = {}
    for p in agent:
        t = classify_type(p.get("title") or "")
        d = by_type.setdefault(t, {"merged": 0, "closed": 0})
        d["merged" if p.get("mergedAt") else "closed"] += 1
    for d in by_type.values():
        tot = d["merged"] + d["closed"]
        d["merge_rate"] = round(d["merged"] / tot, 4) if tot else None

    n = len(agent)
    return {
        "agent_prs": n,
        "non_agent_prs": len(prs) - n,
        "merged": len(merged),
        "closed_unmerged": len(closed),
        "merge_rate": round(len(merged) / n, 4) if n else None,
        "reverted": len(rev),
        "revert_rate": round(len(rev) / len(merged), 4) if merged else None,
        "human_commit_prs": len(human),
        "human_commit_rate": round(len(human) / len(merged), 4) if merged else None,
        "by_type": by_type,
        "reference": REFERENCE,
    }


def render_markdown(stats: dict, period: str) -> str:
    def pct(v):
        return f"{v * 100:.1f}%" if v is not None else "n/a"
    lines = [
        f"# PR-AUDIT {period} — agent PR 受入監査（決定論・LLM 判定なし）",
        "",
        "> 生成: `scripts/pr-audit.py`（v6.15.0 F2）。指標は観測値であり目標値ではない（I-4）。",
        "> agent PR 判定 = commit の Claude trailer または authors login `claude`（OR）。",
        "",
        "| 指標 | 実測 | 参照値 (dotnet/runtime) |",
        "|---|---|---|",
        f"| agent PR 数（分析対象） | {stats['agent_prs']}（非 agent {stats['non_agent_prs']}） | — |",
        f"| merge 率 | {pct(stats['merge_rate'])} ({stats['merged']}/{stats['agent_prs']}) | 67.9% |",
        f"| revert 率 | {pct(stats['revert_rate'])} ({stats['reverted']}/{stats['merged']}) | 0.6% |",
        f"| human-commit 介入率 | {pct(stats['human_commit_rate'])} ({stats['human_commit_prs']}/{stats['merged']}) | 45% |",
        "",
        "## 種別別受入率",
        "",
        "| type | merged | closed | merge 率 |",
        "|---|---|---|---|",
    ]
    for t, d in sorted(stats["by_type"].items(), key=lambda kv: -kv[1]["merged"]):
        lines.append(f"| {t} | {d['merged']} | {d['closed']} | {pct(d['merge_rate'])} |")
    lines += [
        "",
        "> CTL agreement_rate（判断への同意）とは別軸（F2-4）。",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=100, help="集計対象の closed PR 数（既定 100）")
    ap.add_argument("--out", default=None, help="markdown の出力先（省略時 stdout）")
    ap.add_argument("--json", action="store_true", help="JSON で出力")
    ap.add_argument("--period", default="latest", help="レポート見出しの期間表記")
    args = ap.parse_args()

    try:
        prs = fetch_prs(args.limit)
        reverted = fetch_reverted_pr_numbers()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        sys.exit(f"取得失敗（gh / git が必要）: {e}")

    stats = compute(prs, reverted)
    if args.json:
        out = json.dumps(stats, ensure_ascii=False, indent=2)
    else:
        out = render_markdown(stats, args.period)

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(out)
        print(f"書き出し: {args.out}")
    else:
        print(out)


if __name__ == "__main__":
    main()
