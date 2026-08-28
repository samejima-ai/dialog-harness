#!/usr/bin/env python3
"""signal-scan — テレメトリ逆流の最小実装（v6.15.0 F1・Council v615im B 骨格）。

リポジトリ自身が発する信号を決定論で検知し、Issue **候補**として起票する。
LLM 判定を含まない（I-2）。`ready-for-ai` は付けない — 候補の昇格は人間の判断
（I-1・philosophy 第 8 条「観測 → 候補化 → 人間最終承認」）。

検知器（F1-1・初版 4 本固定）:
  (a) red_ci          : master の workflow が直近 2 run 連続で failure
  (b) stale_pr        : open PR が STALE_DAYS 日超・stop ラベル無し・非 draft
  (c) review_trigger  : `review_trigger` を宣言するファイルが最終 commit から
                        REVIEW_TRIGGER_DAYS 日超（v1 近似 — cycle 数の機械計数は
                        将来拡張。日数は再確認の下限として機能する）
  (d) ctl_pending     : CTL 未評価（pending）が PENDING_MAX 件超

安全弁:
  - 重複起票禁止（F1-3）: open の `signal-detected` Issue と同一タイトルなら skip
  - 起票上限（F1-4）: 1 run あたり MAX_ISSUES 件（既定 3）
  - dry-run: `--dry-run` で起票せず判定結果のみ表示

閾値（Council v615im で確定・env で上書き可）:
  STALE_DAYS=7 / PENDING_MAX=10 / REVIEW_TRIGGER_DAYS=90 / MAX_ISSUES=3
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys

STALE_DAYS = int(os.environ.get("STALE_DAYS", "7"))
PENDING_MAX = int(os.environ.get("PENDING_MAX", "10"))
REVIEW_TRIGGER_DAYS = int(os.environ.get("REVIEW_TRIGGER_DAYS", "90"))
MAX_ISSUES = int(os.environ.get("MAX_ISSUES", "3"))
LABEL = "signal-detected"
STOP_LABELS = {"do-not-merge", "human-review-needed", "pickup-failed"}


def _now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


# ---- 取得層（CI / ローカルでのみ実行。テストでは呼ばない） -------------------


def fetch_master_runs(limit: int = 40) -> list[dict]:
    raw = _run(["gh", "run", "list", "--branch", "master", "--limit", str(limit),
                "--json", "workflowName,conclusion,createdAt,event"])
    return json.loads(raw)


def fetch_open_prs() -> list[dict]:
    raw = _run(["gh", "pr", "list", "--state", "open",
                "--json", "number,title,labels,createdAt,isDraft"])
    return json.loads(raw)


def fetch_review_trigger_files() -> list[dict]:
    """review_trigger を宣言するファイルと、その最終 commit 時刻（epoch 秒）。"""
    ls = _run(["git", "grep", "-l", "review_trigger", "--",
               "*.md", "*.yml", "*.yaml"]).split()
    out = []
    for f in ls:
        ts = _run(["git", "log", "-1", "--format=%ct", "--", f]).strip()
        if ts:
            out.append({"path": f, "last_commit_epoch": int(ts)})
    return out


def fetch_pending_count() -> int:
    """council-ctl.py pending の件数（未初期化環境では 0 扱い）。"""
    try:
        out = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "council-ctl.py"),
             "pending"], capture_output=True, text=True, encoding="utf-8").stdout
    except FileNotFoundError:
        return 0
    for line in out.splitlines():
        if "未評価" in line and "件" in line:
            digits = "".join(ch for ch in line.split("未評価")[1].split("件")[0]
                             if ch.isdigit())
            return int(digits) if digits else 0
    return 0


def fetch_open_signal_titles() -> set[str]:
    raw = _run(["gh", "issue", "list", "--state", "open", "--label", LABEL,
                "--json", "title"])
    return {i["title"] for i in json.loads(raw)}


# ---- 判定層（純粋関数・オフラインテスト対象） --------------------------------


def decide_red_ci(runs: list[dict]) -> list[dict]:
    """workflow ごとに新しい順で見て、直近 2 run が連続 failure なら signal。"""
    by: dict[str, list[str]] = {}
    for r in sorted(runs, key=lambda x: x.get("createdAt") or "", reverse=True):
        name = r.get("workflowName") or "?"
        c = r.get("conclusion")
        if c:  # 実行中は判定に使わない
            by.setdefault(name, []).append(c)
    sigs = []
    for name, cs in sorted(by.items()):
        if len(cs) >= 2 and cs[0] == "failure" and cs[1] == "failure":
            sigs.append({
                "detector": "red_ci", "target": name,
                "title": f"[signal:red_ci] {name} が master で連続 failure",
                "body": (f"検知器: red_ci\n対象 workflow: {name}\n"
                         f"実測: 直近 2 run が連続 failure\n"
                         f"根拠: `gh run list --branch master`"),
            })
    return sigs


def decide_stale_prs(prs: list[dict], now: _dt.datetime,
                     stale_days: int = STALE_DAYS) -> list[dict]:
    sigs = []
    for p in prs:
        if p.get("isDraft"):
            continue
        labels = {l.get("name") for l in p.get("labels") or []}
        if labels & STOP_LABELS:
            continue  # 意図的に止められている PR は対象外（F1-1b）
        created = _dt.datetime.fromisoformat(
            (p.get("createdAt") or "").replace("Z", "+00:00"))
        age = (now - created).days
        if age > stale_days:
            n = p["number"]
            sigs.append({
                "detector": "stale_pr", "target": f"#{n}",
                "title": f"[signal:stale_pr] PR #{n} が {age} 日間 open のまま",
                "body": (f"検知器: stale_pr\n対象: PR #{n} 「{p.get('title')}」\n"
                         f"実測: open {age} 日（閾値 {stale_days} 日・stop ラベル無し）\n"
                         f"根拠: `gh pr list --state open`"),
            })
    return sigs


def decide_review_trigger(files: list[dict], now: _dt.datetime,
                          max_days: int = REVIEW_TRIGGER_DAYS) -> list[dict]:
    sigs = []
    for f in files:
        age = (now - _dt.datetime.fromtimestamp(
            f["last_commit_epoch"], _dt.timezone.utc)).days
        if age > max_days:
            sigs.append({
                "detector": "review_trigger", "target": f["path"],
                "title": f"[signal:review_trigger] {f['path']} の再確認期限（{age} 日）",
                "body": (f"検知器: review_trigger（v1 近似 = 最終 commit からの日数）\n"
                         f"対象: `{f['path']}`\n"
                         f"実測: 最終 commit から {age} 日（閾値 {max_days} 日）\n"
                         f"規範メタデータ `review_trigger` の宣言に基づく再確認候補"),
            })
    return sigs


def decide_pending(count: int, limit: int = PENDING_MAX) -> list[dict]:
    if count > limit:
        return [{
            "detector": "ctl_pending", "target": "council-data",
            "title": f"[signal:ctl_pending] CTL 未評価が {count} 件滞留",
            "body": (f"検知器: ctl_pending\n実測: pending {count} 件（閾値 {limit} 件）\n"
                     f"未評価は CTL の燃料にならない。`python3 scripts/council-ctl.py pending` で一覧"),
        }]
    return []


def dedup_and_cap(signals: list[dict], open_titles: set[str],
                  cap: int = MAX_ISSUES) -> tuple[list[dict], int]:
    """重複除去（F1-3）→ 上限（F1-4）。返り値: (起票対象, 重複 skip 数)。"""
    fresh = [s for s in signals if s["title"] not in open_titles]
    return fresh[:cap], len(signals) - len(fresh)


def format_issue_body(sig: dict) -> str:
    return (f"{sig['body']}\n\n---\n"
            f"本 Issue は **候補**である（`ready-for-ai` は付いていない）。\n"
            f"昇格の判断は人間が行う（philosophy 第 8 条 / v6.15.0 I-1）。\n"
            f"起票: `scripts/signal-scan.py`（決定論・LLM 判定なし）")


# ---- 実行 --------------------------------------------------------------------


def ensure_label() -> None:
    subprocess.run(["gh", "label", "create", LABEL,
                    "--description", "signal-scan による候補起票（人間が昇格判断）",
                    "--color", "d4c5f9", "--force"],
                   capture_output=True, text=True)


def create_issue(sig: dict) -> None:
    _run(["gh", "issue", "create", "--title", sig["title"],
          "--body", format_issue_body(sig), "--label", LABEL])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="起票せず判定のみ表示")
    args = ap.parse_args()

    now = _now()
    signals: list[dict] = []
    # 検知器の個別失敗で全体を止めない（1 本の取得失敗は warn して続行）
    for name, fn in [
        ("red_ci", lambda: decide_red_ci(fetch_master_runs())),
        ("stale_pr", lambda: decide_stale_prs(fetch_open_prs(), now)),
        ("review_trigger", lambda: decide_review_trigger(fetch_review_trigger_files(), now)),
        ("ctl_pending", lambda: decide_pending(fetch_pending_count())),
    ]:
        try:
            signals += fn()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"warn: 検知器 {name} の取得失敗（skip）: {e}", file=sys.stderr)

    try:
        open_titles = fetch_open_signal_titles()
    except (subprocess.CalledProcessError, FileNotFoundError):
        open_titles = set()

    to_file, dup = dedup_and_cap(signals, open_titles)
    print(f"検知 {len(signals)} 件 / 重複 skip {dup} 件 / 起票対象 {len(to_file)} 件"
          f"（上限 {MAX_ISSUES}）")
    for s in to_file:
        print(f"  - {s['title']}")

    if args.dry_run:
        print("（--dry-run: 起票していません）")
        return
    if to_file:
        ensure_label()
        for s in to_file:
            create_issue(s)
            print(f"起票: {s['title']}")


if __name__ == "__main__":
    main()
