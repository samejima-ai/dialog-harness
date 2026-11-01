#!/usr/bin/env python3
"""gate-metrics — 2026-11-06 roll-back 評価ゲートの 4 指標を集計する（v7.0.0 Phase 0 / T-01）。

`auto-merge-boundary.md §roll-back プロトコル` が定める **4 指標**を、gh CLI + git log +
`history/REGIME-LOG.md` の append 記録だけで算出する。LLM 判定を含まない（I-3 の継承）。

指標（出典: auto-merge-boundary.md §評価指標）:
  - 暗黙 merge 事故件数   : 1 件以上で要再評価 — 人間が事後発覚として記録したもの
  - AI 判定漏れ率         : 5% 超で要再評価   — opt-in 領域を AI が未検知で PR 化した比
  - 境界曖昧化事例        : 月 2 件以上で要再評価
  - 二重ラベル腐敗        : 旧 `auto-merge` ラベル残存 PR の auto-merge は 1 件で即 roll-back

人間観測が一次の指標について:
  §評価指標 の検知主体は 暗黙 merge 事故 = 「人間（事後監視）+ メタ承認機構」、
  境界曖昧化 = 「人間（事後監視）」である。本ツールはこれらを**捏造しない**。
  REGIME-LOG に append された記録を決定論で数え、未記録分は「要人間ラベル付与」として
  母数と共に提示する。数値が埋まらないことを欠損として可視化するのが本ツールの役割。

二重ラベル腐敗のみ機械検知が可能:
  v5.9.0 で workflow は `auto-merge` ラベルを参照しなくなった。よって「旧ラベルが残存した
  まま merge された PR」は gh のラベル履歴から決定論で列挙できる。

使い方:
    python scripts/gate-metrics.py                      # 集計して stdout へ
    python scripts/gate-metrics.py --limit 200
    python scripts/gate-metrics.py --out delivery/GATE-METRICS-2026-11-06.md
    python scripts/gate-metrics.py --json

pr-audit.py（受入・介入の計測）とは別軸。pr-audit は「agent PR がどう受け入れられたか」、
本ツールは「auto-merge opt-out 反転が壊れていないか」を見る。混ぜない。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGIME_LOG = REPO_ROOT / "history" / "REGIME-LOG.md"

# 旧 auto-merge ラベル（v5.9.0 で廃止）。残存 merge は即 roll-back 事由。
LEGACY_LABEL = "auto-merge"
# stop ラベル（auto-merge-boundary.md §stop ラベル定義）
STOP_LABELS = {"human-review-needed", "do-not-merge"}

# REGIME-LOG の記録見出し。append-only の節題を決定論で拾う。
MISJUDGE_HEADING = re.compile(r"^##\s*auto-merge メタ承認機構 — AI 判定漏れ記録\s*#(\d+)", re.M)
IMPLICIT_HEADING = re.compile(r"^##\s*auto-merge メタ承認機構 — 暗黙 merge 事故記録\s*#(\d+)", re.M)
AMBIGUITY_HEADING = re.compile(r"^##\s*auto-merge メタ承認機構 — 境界曖昧化記録\s*#(\d+)", re.M)
# 記録節に含まれる対象 PR 番号
TARGET_PR = re.compile(r"\*\*対象\*\*:\s*PR\s*#(\d+)")

THRESHOLDS = {
    "implicit_merge": "1 件以上で要再評価",
    "misjudgment_rate": "5% 超で要再評価",
    "boundary_ambiguity": "月 2 件以上で要再評価",
    "legacy_label": "1 件でも即 roll-back",
}


def _gh(args: list[str]) -> str:
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


# ---- 取得層（テストでは呼ばない） ------------------------------------------


def fetch_prs(limit: int) -> list[dict]:
    """closed（merged 含む）PR をラベル付きで取得する。"""
    raw = _gh(["pr", "list", "--state", "closed", "--limit", str(limit),
               "--json", "number,title,mergedAt,labels,mergedBy"])
    return json.loads(raw)


def read_regime_log() -> str:
    return REGIME_LOG.read_text(encoding="utf-8") if REGIME_LOG.exists() else ""


# ---- 判定層（純粋関数・オフラインテスト対象） --------------------------------


def label_names(pr: dict) -> set[str]:
    return {(l.get("name") or "") for l in pr.get("labels") or []}


def is_merged(pr: dict) -> bool:
    return bool(pr.get("mergedAt"))


def merge_actor_is_distinguishable(pr: dict) -> bool:
    """merge 実行者から auto-merge と人間の手 merge を **判別できる** か。

    実測（2026-10-25・PR #196）: 本リポジトリでは判別できない。`auto-merge.yml` は
    `secrets.GH_REVIEW_PAT`（人間アカウントの PAT）で `gh pr merge` するため、
    auto-merge による merge も `mergedBy.login = samejima-ai` として記録される。
    記録 #1 の PR #196 は Actions ログ上 auto-merge が merge した事故だが、
    API 上は人間 merge と完全に同一に見える。

    よって merge 実行者による事故判別は**本リポジトリでは成立しない**。
    bot login が明示されている場合のみ判別可能とする（将来 GITHUB_TOKEN 運用に
    変わった場合に効く）。
    """
    login = ((pr.get("mergedBy") or {}).get("login") or "")
    return login.endswith("[bot]")


def has_legacy_label(pr: dict) -> bool:
    """旧 `auto-merge` ラベルが残存しているか。"""
    return LEGACY_LABEL in label_names(pr)


def has_stop_label(pr: dict) -> bool:
    return bool(label_names(pr) & STOP_LABELS)


def find_legacy_label_corruption(prs: list[dict]) -> list[dict]:
    """旧ラベル残存のまま merge された PR を列挙する（即 roll-back 事由）。"""
    return [{"number": p["number"], "title": p.get("title", "")}
            for p in prs if is_merged(p) and has_legacy_label(p)]


def count_records(log: str, heading: re.Pattern[str]) -> list[int]:
    """REGIME-LOG に append された記録番号を列挙する。"""
    return [int(m.group(1)) for m in heading.finditer(log)]


def recorded_target_prs(log: str) -> list[int]:
    return [int(m.group(1)) for m in TARGET_PR.finditer(log)]


def merged_with_stop_label(prs: list[dict]) -> list[dict]:
    """stop ラベルが付いたまま merge された PR＝**人間が突合すべき候補一覧**。

    記録 #1（PR #196）がこの形。ただしこれは事故の検知ではなく**棚卸し対象の絞り込み**
    である。理由は 2 つ:

    1. 偽陽性: 人間が内容を確認した上で自ら merge した場合も同じ形になる
       （ラベルが設計通り働いた例）。実測 2026-10-25 では 14 件の大半がこれ。
    2. 偽陰性: ラベル未付与のまま merge された #280 型は痕跡が残らず、
       この一覧には現れない。

    さらに `merge_actor_is_distinguishable()` の通り、本リポジトリでは merge 実行者から
    auto-merge と人間 merge を切り分けられない。よって**本関数の出力を事故件数として
    扱ってはならない**。人間が 1 件ずつ Actions ログと突合するための候補に留める。
    """
    return [{"number": p["number"], "title": p.get("title", ""),
             "actor_distinguishable": merge_actor_is_distinguishable(p)}
            for p in prs if is_merged(p) and has_stop_label(p)]


def compute(prs: list[dict], log: str) -> dict:
    """4 指標を算出する。人間観測が一次の指標は記録数と欠損を分けて返す。"""
    merged = [p for p in prs if is_merged(p)]

    misjudge_records = count_records(log, MISJUDGE_HEADING)
    implicit_records = count_records(log, IMPLICIT_HEADING)
    ambiguity_records = count_records(log, AMBIGUITY_HEADING)

    legacy = find_legacy_label_corruption(prs)
    stop_merged = merged_with_stop_label(prs)

    # AI 判定漏れ率: 分母は「agent が PR 化した opt-out 判定 PR」。
    # 現運用では全 merged PR が opt-out 判定を経ているため merged 総数を母数に置く。
    denom = len(merged)
    misjudge_n = len(misjudge_records)
    rate = (misjudge_n / denom * 100) if denom else None

    return {
        "scanned_prs": len(prs),
        "merged_prs": denom,
        "implicit_merge": {
            "recorded": len(implicit_records),
            "review_worklist": stop_merged,
            "actor_distinguishable": False,
            "threshold": THRESHOLDS["implicit_merge"],
            "needs_human_label": True,
        },
        "misjudgment": {
            "recorded": misjudge_n,
            "denominator": denom,
            "rate_pct": rate,
            "record_ids": sorted(misjudge_records),
            "target_prs": sorted(set(recorded_target_prs(log))),
            "threshold": THRESHOLDS["misjudgment_rate"],
        },
        "boundary_ambiguity": {
            "recorded": len(ambiguity_records),
            "threshold": THRESHOLDS["boundary_ambiguity"],
            "needs_human_label": True,
        },
        "legacy_label": {
            "count": len(legacy),
            "prs": legacy,
            "threshold": THRESHOLDS["legacy_label"],
        },
    }


def verdict(stats: dict) -> list[str]:
    """閾値超過を列挙する。判断そのものは下さない（人間の 11-06 判断材料）。"""
    out: list[str] = []
    if stats["implicit_merge"]["recorded"] >= 1:
        out.append("暗黙 merge 事故: 記録 1 件以上 — 要再評価")
    if stats["legacy_label"]["count"] >= 1:
        out.append("二重ラベル腐敗: 1 件以上 — 即 roll-back 事由")
    r = stats["misjudgment"]["rate_pct"]
    if r is not None and r > 5.0:
        out.append(f"AI 判定漏れ率: {r:.1f}% > 5% — 要再評価")
    if stats["boundary_ambiguity"]["recorded"] >= 2:
        out.append("境界曖昧化: 2 件以上 — 要再評価")
    return out


def render_markdown(stats: dict, period: str) -> str:
    m = stats["misjudgment"]
    im = stats["implicit_merge"]
    amb = stats["boundary_ambiguity"]
    leg = stats["legacy_label"]
    rate = f"{m['rate_pct']:.1f}%" if m["rate_pct"] is not None else "—"

    lines = [
        f"# GATE-METRICS — 2026-11-06 roll-back 評価ゲート（{period}）",
        "",
        "`auto-merge-boundary.md §roll-back プロトコル` の 4 指標。LLM 判定を含まない。",
        f"走査: closed PR {stats['scanned_prs']} 件（うち merged {stats['merged_prs']} 件）。",
        "",
        "## 4 指標",
        "",
        "| 指標 | 実測 | 閾値 | 検知 |",
        "|---|---|---|---|",
        f"| 暗黙 merge 事故件数 | {im['recorded']} 件（記録）/ 要突合 {len(im['review_worklist'])} 件 | {im['threshold']} | 人間（機械は候補提示のみ） |",
        f"| AI 判定漏れ率 | {rate}（{m['recorded']}/{m['denominator']}） | {m['threshold']} | メタ承認機構 |",
        f"| 境界曖昧化事例 | {amb['recorded']} 件（記録） | {amb['threshold']} | 人間 |",
        f"| 二重ラベル腐敗 | {leg['count']} 件 | {leg['threshold']} | 機械 |",
        "",
    ]

    v = verdict(stats)
    lines += ["## 閾値超過", ""]
    lines += [f"- {x}" for x in v] if v else ["- なし（記録ベース）"]
    lines += [
        "",
        "> **記録ベースの限界**: 「暗黙 merge 事故 0 件」は *そう記録されていない* という意味で",
        "> あり、*起きていない* という意味ではない。既知の反例として PR #196 がある — ",
        "> REGIME-LOG 記録 #1 は Actions ログを一次証拠に「stop ラベル付与後も auto-merge が",
        "> squash merge した」と記す。これは実体として暗黙 merge 事故だが、記録上の区分は",
        "> 「AI 判定漏れ」であり、暗黙 merge 事故としては数えられていない。",
        "> **ゲート判断の前に、この 1 件を暗黙 merge 事故として数えるかを人間が決める必要がある**",
        "> （数えるなら閾値「1 件以上」に該当する）。",
        "",
    ]

    lines += [
        "## AI 判定漏れの内訳",
        "",
        f"- 記録番号: {', '.join('#' + str(i) for i in m['record_ids']) or 'なし'}",
        f"- 対象 PR: {', '.join('#' + str(i) for i in m['target_prs']) or 'なし'}",
        "",
        "## 暗黙 merge — 人間が突合すべき候補一覧",
        "",
        "stop ラベルが付いたまま merge された PR。**事故件数ではない。**",
        "",
        "- **偽陽性**: 人間が確認して自ら merge した場合も同じ形になる",
        "- **偽陰性**: ラベル未付与のまま merge された型（記録 #2 の PR #280）は現れない",
        "- **実行者で切り分けられない**: `auto-merge.yml` は `secrets.GH_REVIEW_PAT`",
        "  （人間アカウントの PAT）で merge するため、auto-merge も人間 merge も",
        "  `mergedBy` が同一に見える。記録 #1 の PR #196 が実例",
        "",
        "下記は Actions ログと 1 件ずつ突合するための候補である。",
        "",
    ]
    sub = im["review_worklist"]
    lines += [f"- #{p['number']} {p['title']}" for p in sub] if sub else ["- 候補なし"]
    lines += ["", f"候補 {len(sub)} 件。突合の結果 事故と判明したものを REGIME-LOG へ",
              "`## auto-merge メタ承認機構 — 暗黙 merge 事故記録 #N` として append する。", ""]

    if leg["prs"]:
        lines += ["## 二重ラベル腐敗の該当 PR", ""]
        lines += [f"- #{p['number']} {p['title']}" for p in leg["prs"]]
        lines.append("")

    lines += [
        "## 要人間ラベル付与",
        "",
        "次の 2 指標は §評価指標 が検知主体を人間（事後監視）と定める。",
        "本レポートの数値は REGIME-LOG への append 記録の計数であり、",
        "**未記録の事象は 0 件として現れる**。ゲート判断の前に人間の棚卸しが要る。",
        "",
        "- 暗黙 merge 事故件数 — 事後発覚した『気づいたら merge』の有無",
        "- 境界曖昧化事例 — philosophy 周辺の判定揺らぎの有無",
        "",
        "## 判断",
        "",
        "本レポートは 11-06 ゲートの**判断材料**であり、判断そのものではない",
        "（第 8 条: 採否の判断を AI に持たせない）。起票可否は人間が決める。",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="2026-11-06 ゲート 4 指標の集計")
    ap.add_argument("--limit", type=int, default=100, help="集計対象の closed PR 数（既定 100）")
    ap.add_argument("--out", default=None, help="markdown の出力先（省略時 stdout）")
    ap.add_argument("--json", action="store_true", help="JSON で出力")
    ap.add_argument("--period", default="latest", help="レポート見出しの期間表記")
    args = ap.parse_args()

    prs = fetch_prs(args.limit)
    stats = compute(prs, read_regime_log())

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    md = render_markdown(stats, args.period)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(f"wrote {out}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
