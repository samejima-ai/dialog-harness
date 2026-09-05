#!/usr/bin/env python3
"""signal-scan — テレメトリ逆流の最小実装（v6.15.0 F1・Council v615im B 骨格）。

リポジトリ自身が発する信号を決定論で検知し、Issue **候補**として起票する。
LLM 判定を含まない（I-2）。`ready-for-ai` は付けない — 候補の昇格は人間の判断
（I-1・philosophy 第 8 条「観測 → 候補化 → 人間最終承認」）。

検知器（(a)-(d) = v6.15.0 F1 初版 / (e)-(f) = v6.17.0 F7・F8）:
  (a) red_ci            : master の workflow が直近 2 run 連続で failure
  (b) stale_pr          : open PR が STALE_DAYS 日超・stop ラベル無し・非 draft
  (c) review_trigger    : `review_trigger` を宣言するファイルが最終 commit から
                          REVIEW_TRIGGER_DAYS 日超（v1 近似 — cycle 数の機械計数は
                          将来拡張。日数は再確認の下限として機能する）
  (d) ctl_pending       : CTL 未評価（pending）が PENDING_MAX 件超
  (e) workflow_silence  : pull_request トリガを持つ workflow が
                          WORKFLOW_SILENCE_DAYS 日超 1 度も起動していない
                          （red は検知器 (a) が拾うが、**走らなくなったことは red に
                          ならないので誰も気づかない**。v6.17.0 F7 の実害:
                          gemini-review が 2026-05-09 以降 4 ヶ月沈黙し、auto-merge の
                          条件 4.5 が実質 harness-verify のみで成立していた）
  (f) metabolism_stall  : 情報代謝の未消化分（cursor 位置 → 現末尾）が
                          `.metabolism-config.yml` の token_budget を超過
                          （v6.17.0 F8。判定はせず数えるだけ = I-2）

安全弁:
  - 重複起票禁止（F1-3）: open の `signal-detected` Issue と同一タイトルなら skip
    **タイトルは信号の同一性のみで構成し、測定値（日数・件数）を含めない**
    （v6.17.0 F8 の是正。旧版は `PR #1 が 18 日間 open` のように測定値を含めたため
    日次 cron で毎日タイトルが変わり dedup が外れ、2026-08-28〜09-05 に同一 3 PR で
    27 件の重複 Issue を生んでいた。測定値は body に置く）
  - 起票上限（F1-4）: 1 run あたり MAX_ISSUES 件（既定 3）
  - dry-run: `--dry-run` で起票せず判定結果のみ表示

閾値（(a)-(d) は Council v615im で確定・env で上書き可）:
  STALE_DAYS=7 / PENDING_MAX=10 / REVIEW_TRIGGER_DAYS=90 / MAX_ISSUES=3
  WORKFLOW_SILENCE_DAYS=60（v6.17.0 F7）/ (f) の閾値は token_budget を正本とする
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys

STALE_DAYS = int(os.environ.get("STALE_DAYS", "7"))
PENDING_MAX = int(os.environ.get("PENDING_MAX", "10"))
REVIEW_TRIGGER_DAYS = int(os.environ.get("REVIEW_TRIGGER_DAYS", "90"))
WORKFLOW_SILENCE_DAYS = int(os.environ.get("WORKFLOW_SILENCE_DAYS", "60"))
MAX_ISSUES = int(os.environ.get("MAX_ISSUES", "3"))
LABEL = "signal-detected"
STOP_LABELS = {"do-not-merge", "human-review-needed", "pickup-failed"}
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


def fetch_pr_workflows(root: str = REPO_ROOT) -> list[dict]:
    """`pull_request` トリガを持つ workflow と、その最終 run / 最終 commit 時刻。

    最終 run が無い（1 度も走っていない）workflow は `last_run_epoch=None` を返し、
    判定側が「ファイルが存在した期間」で代替評価する（新設直後の誤検知を避けるため
    基準時刻を持たせる）。
    """
    wf_dir = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(wf_dir):
        return []
    out = []
    for fn in sorted(os.listdir(wf_dir)):
        if not fn.endswith((".yml", ".yaml")):
            continue
        with open(os.path.join(wf_dir, fn), encoding="utf-8") as fh:
            text = fh.read()
        # `on:` 直下の 2 スペースインデント（pull_request / pull_request_target）
        if not re.search(r"^\s{2}pull_request(_target)?:", text, re.M):
            continue
        try:
            raw = _run(["gh", "run", "list", "--workflow", fn, "--limit", "1",
                        "--json", "createdAt"])
            arr = json.loads(raw)
            last = int(_dt.datetime.fromisoformat(
                arr[0]["createdAt"].replace("Z", "+00:00")).timestamp()) if arr else None
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError, KeyError):
            last = None
        ts = _run(["git", "log", "-1", "--format=%ct", "--",
                   f".github/workflows/{fn}"]).strip()
        out.append({
            "name": fn,
            "last_run_epoch": last,
            "file_epoch": int(ts) if ts else None,
        })
    return out


def fetch_metabolism_state(root: str = REPO_ROOT) -> dict | None:
    """情報代謝の cursor / config を読む。未配備なら None（検知器を skip）。

    cursor の各エントリ（`  <name>.md: { line: N, ... }`）が指す行以降を「未消化」とし、
    その byte 数を数える。tokens への換算は `bytes / 4`（DH 内の概算慣行）。
    """
    hist = os.path.join(root, "history")
    cursor_p = os.path.join(hist, ".metabolism-cursor.yml")
    config_p = os.path.join(hist, ".metabolism-config.yml")
    if not os.path.exists(cursor_p):
        return None
    with open(cursor_p, encoding="utf-8") as fh:
        cursor_text = fh.read()
    config_text = ""
    if os.path.exists(config_p):
        with open(config_p, encoding="utf-8") as fh:
            config_text = fh.read()

    m = re.search(r'^last_reindex_at:\s*"?([0-9T:+\-]+Z?)"?', cursor_text, re.M)
    b = re.search(r"^\s*token_budget:\s*(\d+)", config_text, re.M)

    files = []
    for name, line in re.findall(r"^\s{2}([\w.\-]+\.md):\s*\{\s*line:\s*(\d+)",
                                 cursor_text, re.M):
        path = os.path.join(hist, name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
        undigested = lines[int(line):]
        files.append({
            "name": name,
            "cursor_line": int(line),
            "total_lines": len(lines),
            "undigested_lines": len(undigested),
            "undigested_bytes": sum(len(x.encode("utf-8")) for x in undigested),
        })
    return {
        "last_reindex_at": m.group(1) if m else None,
        "token_budget": int(b.group(1)) if b else 0,
        "files": files,
    }


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
                # タイトルは同一性のみ（測定値 age を含めない = dedup が外れないため）
                "title": f"[signal:stale_pr] PR #{n} が滞留（open 期間が閾値超）",
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
                "title": f"[signal:review_trigger] {f['path']} の再確認期限を超過",
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
            "title": "[signal:ctl_pending] CTL 未評価が閾値超で滞留",
            "body": (f"検知器: ctl_pending\n実測: pending {count} 件（閾値 {limit} 件）\n"
                     f"未評価は CTL の燃料にならない。`python3 scripts/council-ctl.py pending` で一覧"),
        }]
    return []


def decide_workflow_silence(workflows: list[dict], now: _dt.datetime,
                            max_days: int = WORKFLOW_SILENCE_DAYS) -> list[dict]:
    """走らなくなった workflow を検知する（v6.17.0 F7）。

    検知器 (a) red_ci は「走って落ちた」を拾うが、「そもそも走っていない」は
    red にならないため誰も気づかない。基準時刻は最終 run、無ければ workflow
    ファイルの最終 commit（新設直後の誤検知を避ける）。
    """
    sigs = []
    for w in workflows:
        ref = w.get("last_run_epoch") or w.get("file_epoch")
        if not ref:
            continue  # 基準時刻が取れない = 判定しない（黙って落とさず skip）
        age = (now - _dt.datetime.fromtimestamp(ref, _dt.timezone.utc)).days
        if age <= max_days:
            continue
        never = w.get("last_run_epoch") is None
        kind = "1 度も起動していない" if never else "最終起動から経過"
        sigs.append({
            "detector": "workflow_silence", "target": w["name"],
            # タイトルは同一性のみ（age を含めない）
            "title": f"[signal:workflow_silence] {w['name']} が長期間起動していない",
            "body": (f"検知器: workflow_silence\n対象: `.github/workflows/{w['name']}`"
                     f"（`pull_request` トリガあり）\n"
                     f"実測: {kind} {age} 日（閾値 {max_days} 日）\n"
                     f"意味: red CI は検知器 (a) が拾うが、**走らなくなったことは red に"
                     f"ならない**ため検知経路が無かった。paths filter / secret 欠落 /"
                     f" Actions 無効化のいずれかを疑う。\n"
                     f"根拠: `gh run list --workflow {w['name']} --limit 1`"),
        })
    return sigs


def decide_metabolism_stall(state: dict | None, now: _dt.datetime,
                            token_budget: int | None = None) -> list[dict]:
    """情報代謝の未消化分が token_budget を超えたら候補起票（v6.17.0 F8）。

    判定はせず数えるだけ（I-2）。reindex を走らせるかは人間 / L0 が決める。
    """
    if not state or not state.get("files"):
        return []
    budget = token_budget if token_budget is not None else state.get("token_budget") or 0
    if budget <= 0:
        return []  # 予算未設定のプロジェクトでは検知しない
    total_bytes = sum(f["undigested_bytes"] for f in state["files"])
    total_lines = sum(f["undigested_lines"] for f in state["files"])
    est_tokens = total_bytes // 4
    if est_tokens <= budget:
        return []

    since = ""
    if state.get("last_reindex_at"):
        try:
            last = _dt.datetime.fromisoformat(
                state["last_reindex_at"].replace("Z", "+00:00"))
            since = f"最終 reindex から {(now - last).days} 日 / "
        except ValueError:
            since = ""
    detail = "\n".join(
        f"  - {f['name']}: cursor {f['cursor_line']} 行 → 現末尾 {f['total_lines']} 行"
        f"（未消化 {f['undigested_lines']} 行）" for f in state["files"])
    return [{
        "detector": "metabolism_stall", "target": "history",
        # タイトルは同一性のみ（測定値を含めない）
        "title": "[signal:metabolism_stall] 情報代謝が停滞（未消化が token_budget 超）",
        "body": (f"検知器: metabolism_stall\n対象: `history/`（reduction_target = DH）\n"
                 f"実測: {since}未消化 {total_lines} 行 / 約 {est_tokens:,} tok"
                 f"（bytes/4 概算・閾値 token_budget = {budget:,} tok）\n"
                 f"{detail}\n"
                 f"根拠: `history/.metabolism-cursor.yml` の cursor 位置と各ファイルの現末尾\n"
                 f"対応: `layer0-reindex-librarian` を起動して代謝を再開する"
                 f"（本検知器は数えるだけで代謝を実行しない = I-2）"),
    }]


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
        ("workflow_silence", lambda: decide_workflow_silence(fetch_pr_workflows(), now)),
        ("metabolism_stall", lambda: decide_metabolism_stall(fetch_metabolism_state(), now)),
    ]:
        try:
            signals += fn()
        # OSError（FileNotFoundError / PermissionError 等）と ValueError
        # （UnicodeDecodeError / fromisoformat の失敗）まで拾う。v6.17.0 F8 で
        # 追加した検知器 (e)(f) はファイルを直接読むため、旧 except（CalledProcessError /
        # FileNotFoundError のみ）では「個別失敗で全体を止めない」契約が破れていた。
        except (subprocess.CalledProcessError, OSError, ValueError) as e:
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
