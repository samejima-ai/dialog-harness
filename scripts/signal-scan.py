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
  (f) metabolism_stall  : cursor 記録時点からの **増分行数** > 購読量 budget
                          （REGIME.md `## 情報代謝設定` → 無ければ
                          `.metabolism-config.yml` の `token_budget`。名前に反して
                          「default-load 行数の近似上限」）。
                          **時間で発火させない** — metabolism-regime「リズム（決定2・確定）」が
                          「発火条件は購読量 budget 超過。N-cycle トリガーは棄却」と
                          明示しており、日数トリガはこの決定に反する。
                          cursor > 現末尾（reindex-protocol の異常条件）は別信号
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
  WORKFLOW_SILENCE_DAYS=60（v6.17.0 F7）/ (f) の閾値は購読量 budget（行数）を正本とする
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

    `last_run_epoch=None` は **「取得に成功したうえで run が 1 件も無い」場合に限る**。
    判定側はこのとき「ファイルが存在した期間」で代替評価する（新設直後の誤検知を避ける）。

    取得失敗（403 / 429 / 一時障害 / 想定外 payload）は **None に落とさず送出**する。
    None に潰すと `file_epoch` へフォールバックして「沈黙」と誤検知するため
    （= 聞けなかったことと、聞いた結果 0 件だったことを混同しない）。
    送出された例外は main が拾い、検知器 (e) 全体を warn + skip する。
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
        # 取得失敗は握り潰さない（上の docstring 参照）。json / payload の異常は
        # ValueError に正規化して main の except に乗せる。
        arr = json.loads(_run(["gh", "run", "list", "--workflow", fn, "--limit", "1",
                               "--json", "createdAt"]))
        if not isinstance(arr, list):
            raise ValueError(f"gh run list の payload が list でない（{fn}）")
        if arr:
            created = arr[0].get("createdAt") if isinstance(arr[0], dict) else None
            if not created:
                raise ValueError(f"gh run list の payload に createdAt が無い（{fn}）")
            last = int(_dt.datetime.fromisoformat(
                created.replace("Z", "+00:00")).timestamp())
        else:
            last = None  # 取得は成功したが run が 1 件も無い
        # `root` を渡された以上 git も root で叩く（cwd 依存だと別リポの mtime を読む）
        ts = _run(["git", "-C", root, "log", "-1", "--format=%ct", "--",
                   f".github/workflows/{fn}"]).strip()
        out.append({
            "name": fn,
            "last_run_epoch": last,
            "file_epoch": int(ts) if ts else None,
        })
    return out


def _resolve_budget_lines(root: str, hist: str) -> int:
    """購読量 budget（行数）の解決。① 配布先 REGIME.md → ② DH-self config。

    `token_budget` は名前に反して「default-load **行数**の近似上限」
    （`.metabolism-config.yml` の注記「token ではなく default-load 行数の近似上限として運用」）。
    配布先は REGIME.md `## 情報代謝設定` が正本なので先に見る。
    """
    regime_p = os.path.join(root, "REGIME.md")
    if os.path.exists(regime_p):
        with open(regime_p, encoding="utf-8") as fh:
            sec = re.search(r"^#+\s*情報代謝設定\b(.*?)(?=^#{1,3}\s|\Z)", fh.read(), re.M | re.S)
        if sec:
            b = re.search(r"token_budget\D{0,20}?(\d+)", sec.group(1))
            if b:
                return int(b.group(1))
    config_p = os.path.join(hist, ".metabolism-config.yml")
    if os.path.exists(config_p):
        with open(config_p, encoding="utf-8") as fh:
            b = re.search(r"^\s*token_budget:\s*(\d+)", fh.read(), re.M)
        if b:
            return int(b.group(1))
    return 0


def fetch_metabolism_state(root: str = REPO_ROOT) -> dict | None:
    """情報代謝の cursor / 予算を読む。未配備なら None（検知器を skip）。

    **cursor の `line: N` は「記録時点のファイル長」であって「読み進める起点」とは限らない**。
    先頭 append の history では line 番号の続きが時系列の続きにならず、cursor 自身が
    「line は読み進める起点ではない」と明記している（kakuman `.metabolism-cursor.yml`）。
    DH 本体も cursor が追う 4 本中 3 本が先頭 append である（2026-09-05 実測）。

    ゆえに本検知器は「どの行が未消化か」を特定しない。数えるのは
    **記録時点からの増分行数**（現末尾 − line）だけで、これは追記方向に依らない。
    byte 数や「未消化」の主張はしない（どの行が未読かは line からは決まらないため）。

    `cursor > 現末尾` は protocol の異常条件（cursor 以前の改変）。黙って 0 にせず
    `anomalies` として持ち上げる。
    """
    hist = os.path.join(root, "history")
    cursor_p = os.path.join(hist, ".metabolism-cursor.yml")
    if not os.path.exists(cursor_p):
        return None
    with open(cursor_p, encoding="utf-8") as fh:
        cursor_text = fh.read()

    m = re.search(r'^last_reindex_at:\s*"?([0-9T:+\-]+Z?)"?', cursor_text, re.M)

    files: list[dict] = []
    anomalies: list[dict] = []
    for name, line in re.findall(r"^\s{2}([\w.\-]+\.md):\s*\{\s*line:\s*(\d+)",
                                 cursor_text, re.M):
        path = os.path.join(hist, name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            total = sum(1 for _ in fh)
        cur = int(line)
        if cur > total:
            anomalies.append({"name": name, "cursor_line": cur, "total_lines": total})
            continue
        files.append({"name": name, "cursor_line": cur, "total_lines": total,
                      "added_lines": total - cur})
    return {
        "last_reindex_at": m.group(1) if m else None,
        "budget_lines": _resolve_budget_lines(root, hist),
        "files": files,
        "anomalies": anomalies,
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
                            budget_lines: int | None = None) -> list[dict]:
    """cursor 記録時点からの増分が購読量 budget を超えたら候補起票（v6.17.0 F8）。

    判定はせず数えるだけ（I-2）。reindex を走らせるかは人間 / L0 が決める。

    **発火条件を「量」に限る根拠**: metabolism-regime「リズム（決定2・確定）」は
    「発火条件: history 層が指定 token 量（購読量 budget）を超過した時点。
    **N-cycle トリガーは棄却**」と確定している。「最終 reindex から N 日」で
    発火させると、この決定が棄却したリズムトリガを検知器が復活させることになる。
    したがって日数は body に併記するだけで trip 条件にしない。

    増分行数は追記方向に依らない代理指標であり、「未消化量そのもの」ではない
    （cursor の line は先頭 append のファイルでは読み進める起点にならない。
    厳密な消化済み範囲の判定は reindex-protocol の責務）。
    """
    if not state:
        return []
    sigs = []

    if state.get("anomalies"):
        detail = ", ".join(f"{a['name']}（cursor {a['cursor_line']} 行 > 現末尾 {a['total_lines']} 行）"
                           for a in state["anomalies"])
        sigs.append({
            "detector": "metabolism_stall", "target": "cursor-anomaly",
            "title": "[signal:metabolism_stall] 代謝 cursor が現末尾を超えている",
            "body": (f"検知器: metabolism_stall（cursor 異常）\n対象: {detail}\n"
                     f"意味: cursor より前が改変された可能性がある（reindex-protocol の異常条件）。\n"
                     f"増分の計数はこのファイルについて信頼できないため除外した。"),
        })

    budget = budget_lines if budget_lines is not None else state.get("budget_lines") or 0
    if not state.get("files") or budget <= 0:
        return sigs

    total_added = sum(f["added_lines"] for f in state["files"])
    if total_added <= budget:
        return sigs

    since = ""
    if state.get("last_reindex_at"):
        try:
            last = _dt.datetime.fromisoformat(
                state["last_reindex_at"].replace("Z", "+00:00"))
            since = f"最終 reindex から {(now - last).days} 日 / "
        except ValueError:
            since = ""
    detail = "\n".join(
        f"  - {f['name']}: cursor 記録時 {f['cursor_line']} 行 → 現末尾 {f['total_lines']} 行"
        f"（+{f['added_lines']} 行）" for f in state["files"])
    sigs.append({
        "detector": "metabolism_stall", "target": "history",
        "title": "[signal:metabolism_stall] 情報代謝が停滞（増分が購読量 budget 超）",
        "body": (f"検知器: metabolism_stall\n対象: `history/`\n"
                 f"実測: {since}cursor 記録時点から **+{total_added} 行**"
                 f"（閾値 = 購読量 budget {budget} 行）\n"
                 f"{detail}\n"
                 f"根拠: `history/.metabolism-cursor.yml` の line（記録時点のファイル長）と現末尾の差。\n"
                 f"      budget は REGIME.md `## 情報代謝設定` → "
                 f"`history/.metabolism-config.yml` の順で解決（reindex-protocol §2.5）。\n"
                 f"注記: 増分行数は追記方向に依らない**代理指標**であり「未消化量」そのものではない"
                 f"（cursor の line は先頭 append のファイルでは読み進める起点にならない）。\n"
                 f"      日数は参考値であって trip 条件ではない"
                 f"（regime「リズム（決定2）」= N-cycle トリガーは棄却）。\n"
                 f"対応: `layer0-reindex-librarian` を起動して代謝を再開する"
                 f"（本検知器は数えるだけで代謝を実行しない = I-2）"),
    })
    return sigs


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

    # dedup が効かないまま起票すると、まさに v6.17.0 F8 で是正した「重複 Issue の山」を
    # 再生産する。open タイトルを読めなかったときは起票せず判定表示だけで終える（fail-safe）。
    dedup_ok = True
    try:
        open_titles = fetch_open_signal_titles()
    except (subprocess.CalledProcessError, OSError, ValueError) as e:
        print(f"warn: open Issue のタイトル取得に失敗（{e}）。"
              f"重複判定ができないため本 run は起票しない（次の cron で再試行）。",
              file=sys.stderr)
        open_titles, dedup_ok = set(), False

    to_file, dup = dedup_and_cap(signals, open_titles)
    fresh = [x for x in signals if x["title"] not in open_titles]
    dropped = fresh[len(to_file):]
    print(f"検知 {len(signals)} 件 / 重複 skip {dup} 件 / 起票対象 {len(to_file)} 件"
          f"（上限 {MAX_ISSUES}）")
    for s in to_file:
        print(f"  - {s['title']}")
    # 上限で落ちた分は黙って消さない（次 run に持ち越されることを人間が知れるように）
    for s in dropped:
        print(f"  - （上限で持ち越し）{s['title']}")

    if args.dry_run:
        print("（--dry-run: 起票していません）")
        return
    if not dedup_ok:
        print("（重複判定不能: 起票していません）")
        return
    if to_file:
        ensure_label()
        for s in to_file:
            create_issue(s)
            print(f"起票: {s['title']}")


if __name__ == "__main__":
    main()
