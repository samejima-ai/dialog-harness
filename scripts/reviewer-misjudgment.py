#!/usr/bin/env python3
"""reviewer-misjudgment — C-5「レビュアー誤判定率」計測の半自動ドライバ。

delegation-boundary.md §5 の roll-back 指標のひとつ:

    | レビュアー誤判定率（sub_agent_review が L-GATE/L-FROZEN を見逃した率） |
    | 月次計測、5% 超で要再評価 | v6.0.0 経営者 C-5 |
    | claude-review 出力の事後突合（手動、PR3 で sensor 化候補） |

「sub_agent_review（claude-review）が、本来は L-GATE / L-FROZEN として人間にエスカレート
すべき PR を、L-FULL 相当で通してしまった（見逃した）率」を月次で計測する。
2026-11-06 の roll-back 評価ゲートの計測根拠を、手動突合から半自動へ引き上げる。

設計（scripts/council-ctl.py の record→evaluate→recompute ループを踏襲）:
    - record:   claude-review が判定した 1 件を記録（PR 番号 + レビュアー推奨 verdict）
    - pending:  人間正解ラベル未付与の record を一覧（律速段階 = 人間の事後突合）
    - judge:    人間が正解を付与（その PR は実際に L-GATE/L-FROZEN だったか）
    - report:   月次の誤判定率を算出し harness-verifier/reports/ へ追記

誤判定率の定義（C-5）:
    分母 = その月に claude-review が判定し、人間が正解付与した全件
    分子 = 「実際は L-GATE/L-FROZEN だったのに、レビュアーが通した（見逃した）」件数
    rate = 分子 / 分母。5% 超で要再評価フラグ。

プライバシー / データ保存（council-ctl.py と同方針）:
    データは user-scope（~/.claude/reviewer-misjudgment-data/）に閉じる。
    repo に入るのは本ツールと、集計結果の月次サマリ（reports/）のみ。
    PR タイトル等の生データは user-scope に留め、reports には数値サマリだけ出す。

実行:
    python scripts/reviewer-misjudgment.py record --pr 152 \
        --reviewer-verdict approve --reviewer-confidence 0.82
    python scripts/reviewer-misjudgment.py pending
    python scripts/reviewer-misjudgment.py judge <id> --actual L-FULL
    python scripts/reviewer-misjudgment.py judge <id> --actual L-GATE   # 見逃しなら missed
    python scripts/reviewer-misjudgment.py report --month 2026-06 [--write]

終了コード:
    0: 正常（report 時は rate <= 閾値）
    1: report 時に rate が閾値（5%）超 → 要再評価
    2: 機構エラー（usage / file system）
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from pathlib import Path

# ---- パス（user-scope に閉じる、council-ctl.py と同方針） --------------------
DATA_DIR = Path(
    os.environ.get(
        "REVIEWER_MISJUDGMENT_DATA_DIR",
        Path.home() / ".claude" / "reviewer-misjudgment-data",
    )
)
RECORDS_DIR = DATA_DIR / "records"

# C-5 の閾値（delegation-boundary.md §5）
THRESHOLD_RATE = 0.05  # 5%

# 人間が付与する「実際の委譲レベル」正解ラベル
ACTUAL_LEVELS = ("L-FULL", "L-GATE", "L-FROZEN-PHIL", "L-FROZEN-META")
# 見逃し（missed）= 実際は L-GATE 以上の要エスカレート案件
ESCALATE_LEVELS = ("L-GATE", "L-FROZEN-PHIL", "L-FROZEN-META")

# repo 側の月次レポート出力先
REPO_REPORTS = "harness-verifier/reports"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_data_dir() -> None:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)


def new_id() -> str:
    return secrets.token_hex(4)


def record_path(rec_id: str) -> Path:
    return RECORDS_DIR / f"{rec_id}.json"


def load_records() -> list[dict]:
    if not RECORDS_DIR.is_dir():
        return []
    out = []
    for p in sorted(RECORDS_DIR.glob("*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return out


def write_record(rec: dict) -> None:
    ensure_data_dir()
    path = record_path(rec["id"])
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)  # アトミック書込（council-ctl.py 同様）


# ---- サブコマンド ------------------------------------------------------------

def cmd_record(args) -> int:
    rec = {
        "id": new_id(),
        "pr": args.pr,
        "month": args.month,  # 記録対象月（YYYY-MM、省略時は要指定）
        "reviewer_verdict": args.reviewer_verdict,
        "reviewer_confidence": args.reviewer_confidence,
        "actual_level": None,  # 人間が judge で付与
        "judged": False,
    }
    if not rec["month"]:
        sys.stderr.write("--month YYYY-MM を指定してください（記録対象月）\n")
        return 2
    write_record(rec)
    print(f"記録: id={rec['id']} PR#{rec['pr']} verdict={rec['reviewer_verdict']} "
          f"(month={rec['month']}, 未評価)")
    return 0


def cmd_pending(args) -> int:
    pend = [r for r in load_records() if not r.get("judged")]
    if not pend:
        print("未評価レコードなし（律速段階クリア）。")
        return 0
    print(f"未評価 {len(pend)} 件（人間の事後突合待ち）:")
    for r in pend:
        print(f"  id={r['id']}  PR#{r['pr']}  reviewer={r['reviewer_verdict']}  "
              f"month={r['month']}")
    return 0


def cmd_judge(args) -> int:
    path = record_path(args.id)
    if not path.is_file():
        sys.stderr.write(f"record 不在: id={args.id}\n")
        return 2
    if args.actual not in ACTUAL_LEVELS:
        sys.stderr.write(f"--actual は {ACTUAL_LEVELS} のいずれか\n")
        return 2
    rec = json.loads(path.read_text(encoding="utf-8"))
    rec["actual_level"] = args.actual
    rec["judged"] = True
    # 見逃し判定: 実際は要エスカレートなのに、レビュアーが通した（approve系）か
    rec["missed"] = args.actual in ESCALATE_LEVELS and _is_pass_verdict(
        rec.get("reviewer_verdict", "")
    )
    write_record(rec)
    flag = "  ← MISSED（見逃し）" if rec["missed"] else ""
    print(f"評価: id={rec['id']} actual={args.actual}{flag}")
    return 0


def _is_pass_verdict(verdict: str) -> bool:
    """レビュアーが「通した」とみなす verdict か。

    approve / lgtm / pass 系を pass とみなす。escalate / block / request-changes は非pass。
    """
    v = verdict.strip().lower()
    pass_markers = ("approve", "lgtm", "pass", "ok", "merge")
    escalate_markers = ("escalate", "block", "request", "human", "reject", "gate")
    if any(m in v for m in escalate_markers):
        return False
    return any(m in v for m in pass_markers)


def cmd_report(args) -> int:
    month = args.month
    recs = [r for r in load_records() if r.get("month") == month and r.get("judged")]
    total = len(recs)
    missed = sum(1 for r in recs if r.get("missed"))
    unjudged = len([r for r in load_records()
                    if r.get("month") == month and not r.get("judged")])

    rate = (missed / total) if total else 0.0
    over = rate > THRESHOLD_RATE

    summary_lines = [
        f"## C-5 レビュアー誤判定率 — {month}",
        "",
        f"- 判定総数（人間突合済）: {total}",
        f"- 見逃し（L-GATE/L-FROZEN を通した）: {missed}",
        f"- 誤判定率: {rate:.1%}（閾値 {THRESHOLD_RATE:.0%}）",
        f"- 判定: {'要再評価（閾値超過）' if over else '閾値内'}",
        f"- 未突合（律速段階の残り）: {unjudged}",
        "",
        "> 出典: delegation-boundary.md §5 / v6.0.0 経営者 C-5。"
        "2026-11-06 roll-back 評価ゲートの計測根拠。",
        "> 生データは user-scope に閉じ、本サマリは数値のみ（プライバシー配慮）。",
        "",
    ]
    summary = "\n".join(summary_lines)

    if args.json:
        print(json.dumps(
            {"month": month, "total": total, "missed": missed,
             "rate": rate, "threshold": THRESHOLD_RATE, "over_threshold": over,
             "unjudged": unjudged},
            ensure_ascii=False, indent=2))
    else:
        print(summary)

    if args.write:
        report_dir = repo_root() / REPO_REPORTS
        report_dir.mkdir(parents=True, exist_ok=True)
        # 既存月次レポートに追記（append。harness-verify の月次と共存）
        target = report_dir / f"{month}.md"
        prefix = "\n\n" if target.exists() else ""
        with target.open("a", encoding="utf-8") as f:
            f.write(prefix + summary)
        print(f"\n→ 追記: {target}")

    return 1 if over else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("record", help="claude-review 判定を 1 件記録")
    sp.add_argument("--pr", required=True, help="PR 番号")
    sp.add_argument("--month", required=True, help="記録対象月 YYYY-MM")
    sp.add_argument("--reviewer-verdict", required=True,
                    help="レビュアー推奨 verdict（approve / escalate_to_human 等）")
    sp.add_argument("--reviewer-confidence", type=float, default=None,
                    help="レビュアー confidence（0-1、任意）")
    sp.set_defaults(func=cmd_record)

    sp = sub.add_parser("pending", help="人間突合待ち（律速段階）を一覧")
    sp.set_defaults(func=cmd_pending)

    sp = sub.add_parser("judge", help="人間が実際の委譲レベル正解を付与")
    sp.add_argument("id", help="record ID")
    sp.add_argument("--actual", required=True,
                    help=f"実際の委譲レベル {ACTUAL_LEVELS}")
    sp.set_defaults(func=cmd_judge)

    sp = sub.add_parser("report", help="月次誤判定率を算出（5% 超で exit 1）")
    sp.add_argument("--month", required=True, help="対象月 YYYY-MM")
    sp.add_argument("--write", action="store_true",
                    help="harness-verifier/reports/<month>.md へ追記")
    sp.add_argument("--json", action="store_true", help="JSON 出力")
    sp.set_defaults(func=cmd_report)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[reviewer-misjudgment] error: {exc}\n")
        sys.exit(2)
