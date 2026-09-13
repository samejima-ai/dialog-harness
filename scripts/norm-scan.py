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
| `model_generation` | max(`model-recommendations.md` の最終 commit, `history/.model-generation.yml` の changed_at) が規範より新しい（v7.0.0 F7） | 決定論 |
| `measured: <条件>` | **判定しない**（人が測る条件）。列挙のみ | — |

`measured:` を機械判定しないのは、条件が自然文であり LLM 判定を要するため。
I-3（検知は決定論・蒸留や検査に LLM を使わない）に従い、**列挙して人に見せる**に留める。

## 失効済み規範の列挙（v7.0.0 Phase A F6）

規範メタデータの `status:` が `revoked` の規範（`dev-env-spec.md` §規範メタデータ §失効）が
**購読層（HOT / WARM）に残っていれば列挙する**。判定はしない — COLD へ移すかは儀式 F2.6 で人間に問う。
根拠: 環境が転回したとき append-only の記憶は成功率 0.210 で「記憶なし 0.309」より悪く、明示的失効で 0.950
（arXiv 2608.07429）。失効を宣言しても購読から外れなければ記憶は害のまま残る。
走査範囲は `review_trigger` の走査と**異なる**: `history/` は失効の適用対象（`DH-PHILOSOPHY-INSIGHTS.md` の各節）を
含むため除外せず、COLD である `history/archive/` だけを除く（REVOKED_EXCLUDE_PREFIXES）。
`revoked_at` / `superseded_by` を欠く宣言は「宣言不完全」として別枠に列挙する（黙って捨てない）。

規範メタデータ:
    stage: 全段階
    review_trigger:
      - measured: 本走査器が 6 cycle 連続で「発火 0 件」なら、規範側の時限設定が
        形骸化していないかを疑う（発火しない時限は時限ではない）
      - model_generation
      - cycles: 6
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

# 失効済み規範（F6）の走査で外すもの。review_trigger の走査より狭い:
# history/ は失効の適用対象（叡智層の各節）を含むので除外せず、COLD（既定非ロード）だけを外す。
REVOKED_EXCLUDE_PREFIXES = (
    "dh-upgrades/",     # 版ごとの移行仕様。規範ではない
    "delivery/",        # 分析・献上物。規範ではない
    "history/archive/", # COLD。既に購読から外れている（列挙する意味が無い）
)

TRIGGER_RE = re.compile(r"review_trigger", re.I)
# インライン形: `{ stage: S2, review_trigger: [measured: ..., date: 2026-11-30] }`
INLINE_RE = re.compile(r"review_trigger:\s*\[(.*?)\]", re.S)
# ブロック形:
#   review_trigger:
#     - measured: ...
#     - date: 2026-11-30
BLOCK_ITEM_RE = re.compile(r"^\s*[-*]\s*(\w+)\s*:?\s*(.*)$")

# 失効宣言（F6）。`status:` の値が revoked のものだけを拾う（active / frozen は購読対象のまま）
# 値の引用符は revoked_at / superseded_by と同様に許す（非対称にしない — 独立検証 F-5d）
STATUS_REVOKED_RE = re.compile(r"status:\s*[\"']?revoked\b")
REVOKED_AT_RE = re.compile(r"revoked_at:\s*[\"']?(\d{4}-\d{2}-\d{2})[\"']?")
# 値の終端: 空白 / , / } / 引用符 / backtick / 全角括弧・読点（`none（参照…）` を取り込まない — F-5e）
SUPERSEDED_RE = re.compile(r"superseded_by:\s*[\"']?([^\s,}\"'`（）、]+)")

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
                    "why": "世代 epoch（model-recommendations.md / .model-generation.yml の新しい方）が本規範より新しい（世代交代の疑い）"}
        return {"kind": "model_generation", "fired": False,
                "why": "世代 epoch（model-recommendations.md / .model-generation.yml の新しい方）は本規範より古い（世代交代なし）"}

    if item.startswith("measured"):
        # I-3: 自然文の条件は機械判定しない。列挙して人に見せる
        return {"kind": "measured", "fired": None,
                "why": "人が測る条件（機械判定しない・儀式 F2.6 で人間に問う）"}

    return {"kind": "unknown", "fired": None, "why": f"未知のトリガ形式: {item[:60]}"}


def model_generation_epoch(repo: Path) -> int | None:
    """世代交代の epoch = max(model-recommendations.md の最終 commit, history/.model-generation.yml の changed_at)。

    v7.0.0 Phase A F7。model-recommendations.md だけを見ると、同ファイルが更新されない限り世代交代を
    永久に検出できない（代理指標が人間の作業に依存）。儀式 F1 が機械記録する .model-generation.yml を
    併用し、どちらか新しい方を採る。LLM 判定は含まない。
    """
    rec = last_commit_epoch(
        ".claude/skills/layer0-spec-architect/references/model-recommendations.md")
    yml = repo / "history" / ".model-generation.yml"
    ymd = None
    if yml.is_file():
        try:
            m = re.search(r'^changed_at:\s*"?(\d{4}-\d{2}-\d{2})"?', yml.read_text(encoding="utf-8"), re.M)
        except OSError:
            m = None
        if m:
            try:
                ymd = int(_dt.datetime.strptime(m.group(1), "%Y-%m-%d")
                          .replace(tzinfo=_dt.timezone.utc).timestamp())
            except ValueError:
                # 形式は合うが意味が不正な日付（例 2026-13-45）。儀式 F2.6 の走査を止めない（degrade）。
                # 黙って捨てず stderr に 1 行残す（検知は決定論・判定は人間）
                import sys as _sys
                print(f"warn: history/.model-generation.yml の changed_at が不正 ({m.group(1)})。無視して続行", file=_sys.stderr)
                ymd = None
    cands = [e for e in (rec, ymd) if e]
    return max(cands) if cands else None


def find_revoked_files(repo: Path) -> list[str]:
    """`status:` が revoked の宣言を含むファイルを git grep で列挙する（F6 の除外規則を適用）。"""
    # --untracked: 書いたばかり（未 git add）の宣言も儀式で列挙する（独立検証 F-1 untracked = 0 件）
    out = _run(["git", "grep", "-l", "--untracked", "-E", "status:[[:space:]]*[\"']?revoked",
                "--", "*.md", "*.py", "*.yml", "*.yaml"])
    files = []
    for line in out.splitlines():
        p = line.strip()
        if not p or any(p.startswith(x) for x in REVOKED_EXCLUDE_PREFIXES):
            continue
        files.append(p)
    return sorted(files)


def extract_revoked(text: str) -> list[dict]:
    """1 ファイルから失効宣言を抜き出す。**意味は解釈しない**（COLD へ移すかは人間）。

    宣言 1 件につき `{line, revoked_at, superseded_by, complete}` を返す。1 行に複数宣言があれば各々 1 件。
    範囲（window）の決め方:
    - インライン形（宣言より前の同一行に `{` があり、宣言より後ろの同一行に `}` がある）: その `{ … }`。
    - それ以外（ブロック形 / 引用ブロック形 / `{` が同一行で閉じない複数行インライン形）: 宣言行から
      空行または `}` を含む行までを 1 宣言の範囲とみなす（行数上限なし・docstring どおり「空行まで」）。
    引用ブロック（`> `）は行頭記号を剥がさなくても正規表現が同じ結果を返すため、剥がさない。
    """
    lines = text.split("\n")
    found: list[dict] = []
    for i, line in enumerate(lines):
        for st in STATUS_REVOKED_RE.finditer(line):
            lb = line.rfind("{", 0, st.start())   # 宣言より前の直近の `{`
            rb = line.find("}", st.end())         # 宣言より後ろの最初の `}`
            if lb >= 0 and rb >= 0:
                # インライン形。宣言より後ろにしか `{` が無い行や、無関係な `{}` が前にある行で
                # window が末尾 1 文字や `{}` に潰れて「宣言不完全」に誤分類しない（Copilot review #289）
                window = line[lb: rb + 1]
            else:
                block = [line[st.start():]]
                if rb < 0:
                    for nxt in lines[i + 1:]:
                        if not nxt.strip():
                            break
                        block.append(nxt)
                        if "}" in nxt:
                            break
                window = "\n".join(block)
            ra = REVOKED_AT_RE.search(window)
            sb = SUPERSEDED_RE.search(window)
            found.append({
                "line": i + 1,
                "revoked_at": ra.group(1) if ra else None,
                "superseded_by": sb.group(1) if sb else None,
                "complete": bool(ra and sb),
            })
    return found


def scan_revoked(repo: Path, files: list[str] | None = None) -> list[dict]:
    """購読層（HOT / WARM）に残っている失効済み規範を列挙する。判定はしない（F6）。

    `files` を渡せば git grep を使わない（テスト用）。渡さなければ find_revoked_files。
    """
    paths = find_revoked_files(repo) if files is None else [
        p for p in files if not any(p.startswith(x) for x in REVOKED_EXCLUDE_PREFIXES)]
    out: list[dict] = []
    for path in paths:
        f = repo / path
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue  # 読めないファイルは走査を止めない（degrade）
        for r in extract_revoked(text):
            out.append({"path": path, **r})
    return out


def scan(repo: Path, now: _dt.datetime) -> dict:
    stage = regime_stage(repo)
    model_epoch = model_generation_epoch(repo)
    results = []
    for path in find_files(repo):
        f = repo / path
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue  # 読めないファイルは走査を止めない（degrade）
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
        "revoked": scan_revoked(repo),
    }


def render(res: dict) -> str:
    lines = ["# 時限規範の再審（norm-scan）", ""]
    lines.append(f"- 走査ファイル: {res['scanned_files']} 件")
    lines.append(f"- lifecycle_stage: {res['lifecycle_stage'] or '(REGIME.md 不在 — stage_transition は skip)'}")
    lines.append(f"- 時限トリガ: {res['total_triggers']} 件"
                 f"（**発火 {len(res['fired'])}** / 未発火 {len(res['not_fired'])} / "
                 f"機械判定しない {len(res['undecidable'])}）")
    revoked = res.get("revoked", [])
    lines.append(f"- 失効済みで購読に残る規範: {len(revoked)} 件"
                 f"（宣言不完全 {sum(1 for r in revoked if not r['complete'])}）")
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
    if revoked:
        lines.append("## 失効済みで購読に残っている規範（儀式 F2.6-3.5 で「COLD へ？」と人間に問う）")
        lines.append("")
        for r in revoked:
            flag = "" if r["complete"] else "**宣言不完全** — "
            lines.append(f"- {flag}{r['path']}:{r['line']} — revoked_at: {r['revoked_at'] or '(欠落)'} / "
                         f"superseded_by: {r['superseded_by'] or '(欠落)'}")
        lines.append("")
        lines.append("失効宣言は購読から外れて初めて効く（append-only の記憶は害 — arXiv 2608.07429）。"
                     "移送は reindex-librarian の排泄経路（`metabolism-regime.md` §2 昇降格）。")
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
