#!/usr/bin/env python3
"""pr-audit.py の回帰テスト（オフライン・gh/git 不要）。

取得層（fetch_*）は呼ばず、判定層の純粋関数に fixture を渡して検証する
（v6.15.0 実装注意点(2): CI では gh 認証が保証されないため）。
"""

import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "pr_audit", Path(__file__).parent / "pr-audit.py")
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


def c(body: str) -> dict:
    return {"messageBody": body}


AGENT_C = c("feat: x\n\nCo-Authored-By: Claude Opus 5 <noreply@anthropic.com>")
HUMAN_C = c("fix typo by hand")

CLOUD_C = {"messageBody": "no trailer here\n\nClaude-Session: https://...",
           "authors": [{"login": "claude", "name": "Claude"}]}

print("== agent PR 判定（trailer OR claude author） ==")
check("trailer あり → agent", m.is_agent_pr({"commits": [AGENT_C]}))
check("trailer なし → 非 agent", not m.is_agent_pr({"commits": [HUMAN_C]}))
check("混在 → agent", m.is_agent_pr({"commits": [HUMAN_C, AGENT_C]}))
check("commits 空 → 非 agent", not m.is_agent_pr({"commits": []}))
check("大文字小文字ゆれを許容",
      m.is_agent_pr({"commits": [c("co-authored-by: claude <x>")]}))
check("trailer 無し + authors login claude → agent（PR #198/#199 型）",
      m.is_agent_pr({"commits": [CLOUD_C]}))
check("authors が人間のみ → 非 agent",
      not m.is_agent_pr({"commits": [{"messageBody": "x",
                                      "authors": [{"login": "samejima-ai"}]}]}))

print("== human commit（介入）判定 ==")
check("全部 trailer → 介入なし", not m.has_human_commit({"commits": [AGENT_C, AGENT_C]}))
check("混在 → 介入あり", m.has_human_commit({"commits": [AGENT_C, HUMAN_C]}))

print("== revert 抽出 ==")
log = 'Revert "feat(x): y (#123)"\nfeat(z): unrelated (#124)\nRevert v6 change (#125)\n'
nums = {int(g1 or g2) for g1, g2 in
        ((mm.group(1), mm.group(2)) for mm in m.REVERT_PR.finditer(log))}
check("引用形式 (#123) を拾う", 123 in nums, str(nums))
check("非引用形式 (#125) を拾う", 125 in nums, str(nums))
check("Revert でない行は拾わない", 124 not in nums, str(nums))

print("== 種別分類 ==")
check("feat(scope):", m.classify_type("feat(council): x") == "feat")
check("fix:", m.classify_type("fix: y") == "fix")
check("feat!:", m.classify_type("feat!: breaking") == "feat")
check("prefix なし → other", m.classify_type("日本語タイトル") == "other")

print("== compute 統合 ==")
prs = [
    {"number": 1, "title": "feat(a): m1", "mergedAt": "2026-01-01T00:00:00Z", "commits": [AGENT_C]},
    {"number": 2, "title": "feat(b): m2", "mergedAt": "2026-01-02T00:00:00Z", "commits": [AGENT_C, HUMAN_C]},
    {"number": 3, "title": "fix(c): closed", "mergedAt": None, "commits": [AGENT_C]},
    {"number": 4, "title": "docs: human pr", "mergedAt": "2026-01-03T00:00:00Z", "commits": [HUMAN_C]},
    {"number": 5, "title": "fix(d): m3-reverted", "mergedAt": "2026-01-04T00:00:00Z", "commits": [AGENT_C]},
]
s = m.compute(prs, reverted={5, 99})
check("agent PR 数 = 4（#4 は人間 PR）", s["agent_prs"] == 4, str(s))
check("非 agent = 1", s["non_agent_prs"] == 1)
check("merged = 3 / closed = 1", s["merged"] == 3 and s["closed_unmerged"] == 1)
check("merge_rate = 0.75", s["merge_rate"] == 0.75)
check("revert = 1 件（#5、#99 は対象外） rate 1/3", s["reverted"] == 1 and s["revert_rate"] == round(1/3, 4))
check("human-commit = 1 件（#2） rate 1/3", s["human_commit_prs"] == 1 and s["human_commit_rate"] == round(1/3, 4))
check("種別: feat merged 2", s["by_type"]["feat"]["merged"] == 2)
check("種別: fix merge_rate 0.5", s["by_type"]["fix"]["merge_rate"] == 0.5)

print("== markdown 出力 ==")
md = m.render_markdown(s, "2026-01")
check("参照値を含む（目標値でなく比較用）", "67.9%" in md and "dotnet/runtime" in md)
check("I-4 の明記", "目標値ではない" in md)
check("種別表を含む", "| feat |" in md)

print("== 空入力の安全性 ==")
z = m.compute([], set())
check("ゼロ除算なし", z["merge_rate"] is None and z["revert_rate"] is None)

if FAIL:
    sys.exit(f"\nFAIL: {FAIL} 件")
print("\nPASS: pr-audit 回帰テスト 全通過")
