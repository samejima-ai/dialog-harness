#!/usr/bin/env python3
"""norm-scan — 時限規範（review_trigger）の機械列挙器（v6.13.0 F5 / v6.18.0 C-1）。

`review_trigger:` メタデータを持つ規範を **grep ベースで機械列挙**し、発火判定して出力する。
**LLM 判定を含まない**（`ritual-protocol.md` §F2.6-1 の規定）。

## なぜ必要か

v6.17.0 は 7 つの新規規範すべてに `review_trigger:` を付した（I-7）。しかし
**それを読む主体がどこにも無い**ため、時限メタデータは名目にとどまっていた
（同 spec §申し送り が自認）。これは v6.17.0 F6 が塞いだ「配布できるが読まれない RL」と
同型の構造であり、`delivery/ANALYSIS-silent-failure-2026-09-06.md` の分類でいう
**型 C（配線されているが通電していない）** の実例である。

本走査器は「宣言されたものを読む主体」を与える。**判定はしない**（F5-3）:
発火した規範を列挙するだけで、残す・降格・廃止の判断は人間（儀式 F2.6-3）。

## 発火判定（F5-3 の 5 種）

| トリガ | 判定 | 決定論か |
|---|---|---|
| `date: YYYY-MM-DD` | 当日を過ぎていれば発火 | 完全に決定論 |
| `cycles: N` | 最終 commit から N cycle 相当を経過（1 cycle = CYCLE_DAYS 日の近似） | 近似 |
| `stage_transition: Sx→Sy` | REGIME.md の lifecycle_stage が Sy 側にあるか | REGIME 不在なら skip |
| `model_generation` | `model-recommendations.md` の最終 commit が規範より新しい | 決定論 |
| `measured: <条件>` | **判定しない**（人が測る条件）。列挙のみ | — |

`measured:` を機械判定しないのは、条件が自然文であり LLM 判定を要するため。
I-3（検知は決定論・蒸留や検査に LLM を使わない）に従い、**列挙して人に見せる**に留める。

規範メタデータ:
    stage: 全段階
    review_trigger:
      - measured: 本走査器が 6 cycle 連続で「発火 0 件」なら、規範側の時限設定が
        形骸化していないかを疑う（発火しない時限は時限ではない）
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path

# 1 cycle の近似日数。`cycles: N` の機械判定に使う。
# cycle 数の厳密計数は history/SUMMARY.md の cycle 記録に依存するため v1 では日数近似とする
# （signal-scan 検知器 (c) が同じ近似を採っている。新しい閾値を発明しない）。
CYCLE_DAYS = 14

# 走査対象から外すもの: 版ごとの移行仕様（歴史的記録）・履歴層・分析文書。
# **除外理由はここに書く**（allowlist を作らない = v6.17.0 I-1 と同じ規律）。
EXCLUDE_PREFIXES = (
    "dh-upgrades/",   # 版ごとの移行仕様。実装済み spec の review_trigger は歴史的記録
    "history/",       # 履歴層。過去の記録であって現行規範ではない
    "delivery/",      # 分析・献上物。規範ではない
)

TRIGGER_RE = re.compile(r"review_trigger", re.I)
# インライン形: `{ stage: S2, review_trigger: [measured: ..., date: 2026-11-30] }`
INLINE_RE = re.compile(r"review_trigger:\s*\[(.*?)\]", re.S)
# ブロック形:
#   review_trigger:
#     - measured: ...
#     - date: 2026-11-30
BLOCK_ITEM_RE = re.compile(r"^\s*[-*]\s*(\w+)\s*:?\s*(.*)$")

DATE_RE = re.compile(r"date:\s*(\d{4}-\d{2}-\d{2})")
CYCLES_RE = re.compile(r"cycles:\s*(\d+)")
STAGE_TR_RE = re.compile(r"stage_transition:\s*(S\d)\s*(?:→|->)\s*(S\d)")


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=False,
                              encoding="utf-8", errors="replace").stdout
    except OSError:
        return ""


def find_files(repo: Path) -> list[str]:
    """review_trigger を含むファイルを git grep で列挙する（除外規則を適用）。"""
    out = _run(["git", "grep", "-l", "review_trigger", "--", "*.md", "*.py", "*.yml", "*.yaml"])
    files = []
    for line in out.splitlines():
        p = line.strip()
        if not p or any(p.startswith(x) for x in EXCLUDE_PREFIXES):
            continue
        files.append(p)
    return sorted(files)


def last_commit_epoch(path: str) -> int | None:
    out = _run(["git", "log", "-1", "--format=%ct", "--", path]).strip()
    return int(out) if out.isdigit() else None


def extract_triggers(text: str) -> list[str]:
    """1 ファイルから review_trigger の項目を文字列として抜き出す。

    インライン形とブロック形の両方を拾う。**意味は解釈しない**（decide が判定する）。
    """
    # Markdown 引用（`> `）の中に規範メタデータを書く慣行があるため、行頭の引用記号を剥がす。
    # 剥がさないとインデント計算に `> ` が混じり、ブロック形が認識されない
    # （実測: v6.18.0 の点検規範を引用ブロックに書いたところ 1 件も拾えなかった）。
    text = re.sub(r"^(\s*)>\s?", r"\1", text, flags=re.M)

    items: list[str] = []
    for m in INLINE_RE.finditer(text):
        for part in m.group(1).split(","):
            s = part.strip()
            if s:
                items.append(s)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if not re.search(r"review_trigger:\s*$", line):
            continue
        base = len(line) - len(line.lstrip())
        current: list[str] = []
        for nxt in lines[i + 1:]:
            if not nxt.strip():
                break
            indent = len(nxt) - len(nxt.lstrip())
            if indent <= base:
                break
            if BLOCK_ITEM_RE.match(nxt):
                if current:
                    items.append(" ".join(current))
                current = [nxt.strip().lstrip("-*").strip()]
            elif current:
                # 継続行（`- measured: ...` の折り返し）を直前の項目へ畳む。
                # これを新項目と誤認すると 1 項目が複数に割れ、しかも
                # 折り返し部分だけを見て「未知のトリガ形式」と誤判定する
                current.append(nxt.strip())
            else:
                break
        if current:
            items.append(" ".join(current))
    return items


def regime_stage(repo: Path) -> str | None:
    """REGIME.md の lifecycle_stage を読む。無ければ None（stage_transition は skip）。"""
    r = repo / "REGIME.md"
    if not r.is_file():
        return None
    m = re.search(r"lifecycle_stage:\s*(S\d)", r.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def decide(item: str, *, path: str, file_epoch: int | None, now: _dt.datetime,
           stage: str | None, model_epoch: int | None) -> dict | None:
    """1 トリガ項目の発火判定。発火しなければ None。判定できないものは fired=None で返す。"""
    m = DATE_RE.search(item)
    if m:
        due = _dt.datetime.strptime(m.group(1), "%Y-%m-%d").replace(tzinfo=_dt.timezone.utc)
        if now >= due:
            return {"kind": "date", "fired": True,
                    "why": f"期限 {m.group(1)} を経過（{(now - due).days} 日超過）"}
        return {"kind": "date", "fired": False,
                "why": f"期限 {m.group(1)} まで残り {(due - now).days} 日"}

    m = CYCLES_RE.search(item)
    if m and file_epoch:
        n = int(m.group(1))
        days = (now - _dt.datetime.fromtimestamp(file_epoch, _dt.timezone.utc)).days
        if days >= n * CYCLE_DAYS:
            return {"kind": "cycles", "fired": True,
                    "why": f"{n} cycle 相当（{n * CYCLE_DAYS} 日）を経過 — 最終更新から {days} 日"}
        return {"kind": "cycles", "fired": False,
                "why": f"{n} cycle 相当まで残り {n * CYCLE_DAYS - days} 日"}

    m = STAGE_TR_RE.search(item)
    if m:
        if stage is None:
            return {"kind": "stage_transition", "fired": None,
                    "why": "REGIME.md に lifecycle_stage が無く判定不能（skip）"}
        if stage == m.group(2):
            return {"kind": "stage_transition", "fired": True,
                    "why": f"lifecycle_stage が {m.group(2)} に到達（宣言 {m.group(1)}→{m.group(2)}）"}
        return {"kind": "stage_transition", "fired": False,
                "why": f"lifecycle_stage は {stage}（宣言は {m.group(1)}→{m.group(2)}）"}

    if "model_generation" in item:
        if model_epoch and file_epoch and model_epoch > file_epoch:
            return {"kind": "model_generation", "fired": True,
                    "why": "model-recommendations.md が本規範より新しい（世代交代の疑い）"}
        return {"kind": "model_generation", "fired": False,
                "why": "model-recommendations.md は本規範より古い（世代交代なし）"}

    if item.startswith("measured"):
        # I-3: 自然文の条件は機械判定しない。列挙して人に見せる
        return {"kind": "measured", "fired": None,
                "why": "人が測る条件（機械判定しない・儀式 F2.6 で人間に問う）"}

    return {"kind": "unknown", "fired": None, "why": f"未知のトリガ形式: {item[:60]}"}


def scan(repo: Path, now: _dt.datetime) -> dict:
    stage = regime_stage(repo)
    model_epoch = last_commit_epoch(
        ".claude/skills/layer0-spec-architect/references/model-recommendations.md")
    results = []
    for path in find_files(repo):
        f = repo / path
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        items = extract_triggers(text)
        if not items:
            continue
        epoch = last_commit_epoch(path)
        for item in items:
            d = decide(item, path=path, file_epoch=epoch, now=now,
                       stage=stage, model_epoch=model_epoch)
            if d is None:
                continue
            results.append({"path": path, "trigger": item[:120], **d})
    return {
        "scanned_files": len(find_files(repo)),
        "total_triggers": len(results),
        "fired": [r for r in results if r["fired"] is True],
        "not_fired": [r for r in results if r["fired"] is False],
        "undecidable": [r for r in results if r["fired"] is None],
        "lifecycle_stage": stage,
    }


def render(res: dict) -> str:
    lines = ["# 時限規範の再審（norm-scan）", ""]
    lines.append(f"- 走査ファイル: {res['scanned_files']} 件")
    lines.append(f"- lifecycle_stage: {res['lifecycle_stage'] or '(REGIME.md 不在 — stage_transition は skip)'}")
    lines.append(f"- 時限トリガ: {res['total_triggers']} 件"
                 f"（**発火 {len(res['fired'])}** / 未発火 {len(res['not_fired'])} / "
                 f"機械判定しない {len(res['undecidable'])}）")
    lines.append("")
    if res["fired"]:
        lines.append("## 発火（儀式 F2.6-3 で人間に問う）")
        lines.append("")
        for r in res["fired"]:
            lines.append(f"- **{r['path']}** — [{r['kind']}] {r['why']}")
            lines.append(f"  - 宣言: `{r['trigger']}`")
        lines.append("")
    else:
        lines.append("発火した時限規範はありません。")
        lines.append("")
    if res["not_fired"]:
        lines.append("## 未発火（判定済み・まだ期限内）")
        lines.append("")
        for r in res["not_fired"]:
            lines.append(f"- {r['path']} — [{r['kind']}] {r['why']}")
        lines.append("")
    if res["undecidable"]:
        lines.append("## 機械判定しない（人が測る / 判定不能）")
        lines.append("")
        for r in res["undecidable"]:
            lines.append(f"- {r['path']} — [{r['kind']}] {r['why']}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**判定はしない**（v6.13.0 F5-3）。残す / 降格 / 廃止の判断は人間が行う。")
    lines.append("降格・廃止は追加より軽い手続きでよい（`ritual-protocol.md` §F2.6-4 非対称原則）。")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="時限規範（review_trigger）の機械列挙")
    ap.add_argument("--json", action="store_true", help="機械可読出力")
    ap.add_argument("--fired-only", action="store_true", help="発火分のみ出力")
    args = ap.parse_args()

    repo = Path(_run(["git", "rev-parse", "--show-toplevel"]).strip() or ".")
    now = _dt.datetime.now(_dt.timezone.utc)
    res = scan(repo, now)
    if args.fired_only:
        res["undecidable"] = []
    print(json.dumps(res, ensure_ascii=False, indent=2) if args.json else render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
