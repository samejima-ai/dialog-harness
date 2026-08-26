#!/usr/bin/env python3
"""upstream-scan — 逆流路の観測器（v7 Phase 1）

配布先リポジトリに在って DH 本体に無い要素を**存在差分のみ**で列挙し、人間が採否を
記入する候補 md を出力する。Council `council-2026-08-26T01:53:40Z-v7ord1`（C2 /
reason_divergence / jc 0.82）の判定と、3 軸が独立に付した実装条件に従う。

## なぜ必要か

`dh-manifest.yml` の `paths:` 4 分類はすべて DH → 配布先の下り。DH 本体は製品を
持たず運用圧を受ける面が無いため、配布先が本番事故の代償で育てた機構が根に還流
しない（delivery/PLAN-v7-reconstruction-2026-08-26.html §構造診断）。本ツールは
その上りの観測部だけを担う。**判断も採択もしない。**

## 不変条件（dh-manifest.yml §upstream と同一。破ったら本ツールの存在意義が消える）

- U-1 配布先に対して**読み取り専用**。配布先へは 1 バイトも書かない
- U-2 出力は候補 md のみ。DH の他ファイルを書き換えない
- U-3 採択は人間ゲート。`gate: human` 以外なら実行を拒否する
- U-4 **判定を持ち込まない**。存在差分のみで、同名要素の内容比較・優劣判定はしない
- U-5 還流するのは機構ではなく**それを必要とした出来事**。事故の日付と解いた問題を
      必須欄に置く（機械には書けないので空欄で出し、未記入件数を計数する）

## 門ではなく観測（kakuman 罠 X-CI-B の形式を借用）

本ツールは非ゲート。候補が何件出ようと exit 0 を返す。exit 1 を返すのは
**センサー自身が武装解除されている場合のみ**（配布先が無い / manifest が読めない /
gate が human でない）。「対象が無いので候補 0 件」を静かに緑で装わない
（kakuman rls-drift.yml の規律）。

## 使い方

    python3 scripts/upstream-scan.py --target ../kakuman-platform-v3.0
    python3 scripts/upstream-scan.py --target ../foo --prev delivery/UPSTREAM-CANDIDATES-2026-08-26.md

`--prev` を渡すと前回 md の人間記入欄（事故の日付 / 解いた問題 / 固有依存 / 採否）を
候補パスで引き継ぐ。人間の判断を再走査で消さないための経路。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from fnmatch import fnmatch
from pathlib import Path

BLANK = "—"

# 人間が埋める欄（機械は決して埋めない・U-4/U-5）
HUMAN_COLUMNS = ["事故の日付", "それが解いた問題", "固有依存", "採否"]
# 採否欄に書ける語。これ以外は「未記入」として計数する
VERDICTS = {"採択", "却下", "保留"}


# --------------------------------------------------------------------------
# dh-manifest.yml の upstream ブロックを読む（標準ライブラリのみ・execution_graph.py と同方針）
# --------------------------------------------------------------------------
def parse_upstream(text: str) -> dict:
    """`upstream:` トップレベルブロックだけを読む最小パーサ。

    受理する形は dh-manifest.yml が実際に持つ形（2 段のリストと 1 段のスカラ）に限る。
    未知の入れ子は黙って捨てず ValueError にする（静かな武装解除を作らない）。
    """
    out: dict = {"scan": [], "never_upstream": [], "gate": None}
    lines = text.splitlines()
    i = 0
    while i < len(lines) and lines[i].rstrip() != "upstream:":
        i += 1
    if i == len(lines):
        raise ValueError("dh-manifest.yml に upstream: ブロックが無い")
    i += 1

    key: str | None = None
    for line in lines[i:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:  # 次のトップレベルキー = upstream ブロックの終端
            break
        stripped = line.strip()
        m_item = re.match(r'^-\s+"?([^"#]+?)"?\s*(?:#.*)?$', stripped)
        if m_item and key in ("scan", "never_upstream"):
            out[key].append(m_item.group(1).strip())
            continue
        m_kv = re.match(r"^([a-z_]+):\s*(.*?)\s*(?:#.*)?$", stripped)
        if m_kv:
            key, val = m_kv.group(1), m_kv.group(2).strip().strip('"')
            if key == "gate":
                out["gate"] = val
            elif key in ("scan", "never_upstream"):
                if val:
                    raise ValueError(f"upstream.{key} はリストで書く（インライン値: {val}）")
            else:
                raise ValueError(f"upstream に未知のキー: {key}")
            continue
        raise ValueError(f"upstream ブロックの解釈不能な行: {line!r}")
    return out


# --------------------------------------------------------------------------
# 存在差分（U-4: 内容は一切見ない）
# --------------------------------------------------------------------------
def split_glob(entry: str) -> tuple[str, str]:
    """scan エントリを (ディレクトリ, 名前 glob) に割る。

    glob は**宣言側**（dh-manifest.yml）が持つ。スクリプトは判定せず適用するだけ（U-4）。
    """
    e = entry.rstrip("/")
    base = e.rsplit("/", 1)[-1]
    if any(ch in base for ch in "*?["):
        return e[: -len(base)].rstrip("/"), base
    return e, "*"


def diff_root(entry: str, dh: Path, target: Path) -> list[dict]:
    """scan エントリ直下で「配布先に在って DH に無い」要素を列挙する。"""
    root, pattern = split_glob(entry)
    t_dir, d_dir = target / root, dh / root
    if not t_dir.is_dir():
        return []
    dh_names = {p.name for p in d_dir.iterdir()} if d_dir.is_dir() else set()
    found = []
    for p in sorted(t_dir.iterdir()):
        if p.name.startswith(".") or p.name in dh_names or not fnmatch(p.name, pattern):
            continue
        if p.is_dir():
            kind = "skill" if root.endswith("skills") else "dir"
        else:
            kind = p.suffix.lstrip(".") or "file"
        found.append({"path": f"{root}/{p.name}" + ("/" if p.is_dir() else ""), "kind": kind, "root": root})
    return found


def excluded(path: str, never: list[str]) -> bool:
    """never_upstream に触れる候補は列挙すらしない。"""
    p = path.rstrip("/")
    return any(p == n.rstrip("/") or n.startswith(p + "/") or p.startswith(n.rstrip("/") + "/") for n in never)


# --------------------------------------------------------------------------
# 前回 md からの人間記入欄の引き継ぎ
# --------------------------------------------------------------------------
def load_prev(md: str) -> dict[str, dict]:
    carried: dict[str, dict] = {}
    for line in md.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 7:
            continue
        key = cells[0].strip("`")
        carried[key] = dict(zip(HUMAN_COLUMNS, cells[3:7]))
    return carried


def render(rows: list[dict], label: str, target: Path, today: str, gate: str) -> tuple[str, dict]:
    counts = {"候補": len(rows), "採択": 0, "却下": 0, "保留": 0, "未記入": 0, "事故日未記入": 0}
    for r in rows:
        counts[r["採否"] if r["採否"] in VERDICTS else "未記入"] += 1
        if r["事故の日付"] == BLANK:
            counts["事故日未記入"] += 1

    body = [
        f"# UPSTREAM 候補 — {label}",
        "",
        "> 逆流路（v7 Phase 1）の観測出力。**判断ではなく候補提示**であり、採択は人間ゲート",
        "> （`dh-manifest.yml` §upstream `gate: human`）。本ファイルの人間記入欄を埋めることが",
        "> Phase 1 の完了条件であり、その結果が Phase 2/3 のスコープを確定させる。",
        "",
        f"- 走査日: {today}",
        f"- 配布先: `{target}`",
        f"- 判定方式: **存在差分のみ**（内容比較・優劣判定はしない = U-4）",
        f"- gate: `{gate}`",
        "",
        "## 計数",
        "",
        "| 指標 | 件数 |",
        "|---|---|",
        f"| 候補 | {counts['候補']} |",
        f"| 採択 | {counts['採択']} |",
        f"| 却下 | {counts['却下']} |",
        f"| 保留 | {counts['保留']} |",
        f"| 採否未記入 | {counts['未記入']} |",
        f"| 事故の日付が未記入 | {counts['事故日未記入']} |",
        "",
        "> 採否未記入が 0 になった時点で本サイクルの Phase 1 は完了する。**候補が列挙された",
        "> ことは完了ではない**（計数されない観測層への退化を 3 軸が独立に警告した）。",
        "",
        "## 候補",
        "",
        "> 「事故の日付」「それが解いた問題」は機械には書けないので空欄で出す。**還流すべきは",
        "> 機構ではなく、機構を必要とした出来事である**（U-5）。日付と痛みを剥いだ機構だけを",
        "> 親に積むことは、事故を経ていない規範の自己増殖にあたる。",
        "",
        "| 候補 | 種別 | 出自 | " + " | ".join(HUMAN_COLUMNS) + " |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        body.append(
            f"| `{r['path']}` | {r['kind']} | {r['provenance']} | "
            + " | ".join(r[c] for c in HUMAN_COLUMNS)
            + " |"
        )
    if not rows:
        body.append("| （候補なし） | — | — | — | — | — | — |")
    body += [
        "",
        "## 記入要領",
        "",
        "- **事故の日付**: その機構を生んだ出来事の日付（`2026-06-11` 等）。無いなら `事故なし` と書く",
        "- **それが解いた問題**: 1 文。何が壊れて、この機構が何を止めたか",
        "- **固有依存**: 配布先固有の前提（DB / 特定 SaaS / 業務語彙）の有無。`なし` / 具体名",
        "- **採否**: `採択` / `却下` / `保留` のいずれか。それ以外は未記入として計数される",
        "",
        "> 採択したものは DH 語彙へ移植する。**移すのは形式だけで、配布先固有の内容は持ち込まない**",
        "> （「agent 本体はプロジェクト不変・差異は入力データに閉じる」の逆流への適用）。",
        "",
        "---",
        "",
        "生成: `scripts/upstream-scan.py` ／ 判定根拠: Council `council-2026-08-26T01:53:40Z-v7ord1`",
    ]
    return "\n".join(body) + "\n", counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="配布先→DH の逆流候補を存在差分で列挙する（観測のみ）")
    ap.add_argument("--target", required=True, help="配布先リポジトリのパス（読み取り専用）")
    ap.add_argument("--dh-root", default=".", help="DH 本体のルート（既定: カレント）")
    ap.add_argument("--label", default=None, help="候補 md の見出し（既定: 配布先ディレクトリ名）")
    ap.add_argument("--out", default=None, help="出力先（既定: delivery/UPSTREAM-CANDIDATES-<日付>.md）")
    ap.add_argument("--prev", default=None, help="前回の候補 md。人間記入欄を引き継ぐ")
    ap.add_argument("--today", default=None, help="走査日の上書き（テスト用）")
    ap.add_argument("--dry-run", action="store_true", help="書かずに標準出力へ")
    a = ap.parse_args(argv)

    dh, target = Path(a.dh_root).resolve(), Path(a.target).resolve()

    # --- 武装検査（黙って緑にしない・rls-drift の規律） ---
    if not target.is_dir():
        print(f"FAIL: 配布先が存在しない: {target}", file=sys.stderr)
        return 1
    manifest = dh / "dh-manifest.yml"
    if not manifest.is_file():
        print(f"FAIL: dh-manifest.yml が無い: {manifest}", file=sys.stderr)
        return 1
    try:
        up = parse_upstream(manifest.read_text(encoding="utf-8"))
    except ValueError as e:
        print(f"FAIL: dh-manifest.yml §upstream を読めない: {e}", file=sys.stderr)
        return 1
    if up["gate"] != "human":
        print(f"FAIL: upstream.gate が human でない（{up['gate']!r}）。採択の人間ゲートは U-3 の不変条件", file=sys.stderr)
        return 1
    if not up["scan"]:
        print("FAIL: upstream.scan が空。走査対象が無い状態で候補 0 件を返さない", file=sys.stderr)
        return 1

    today = a.today or _dt.date.today().isoformat()
    label = a.label or target.name
    carried = load_prev(Path(a.prev).read_text(encoding="utf-8")) if a.prev else {}

    rows = []
    for root in up["scan"]:
        for c in diff_root(root, dh, target):
            if excluded(c["path"], up["never_upstream"]):
                continue
            prev = carried.get(c["path"], {})
            rows.append(
                {
                    **c,
                    "provenance": f"`{label}`",
                    **{col: prev.get(col, BLANK) or BLANK for col in HUMAN_COLUMNS},
                }
            )

    md, counts = render(rows, label, target, today, up["gate"])

    if a.dry_run:
        print(md)
    else:
        out = Path(a.out) if a.out else dh / "delivery" / f"UPSTREAM-CANDIDATES-{today}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(f"書き出し: {out}")

    print(
        f"候補 {counts['候補']} 件 / 採択 {counts['採択']} / 却下 {counts['却下']} / "
        f"保留 {counts['保留']} / 採否未記入 {counts['未記入']} / 事故日未記入 {counts['事故日未記入']}"
    )
    return 0  # 門ではなく観測。候補件数で exit code を変えない


if __name__ == "__main__":
    raise SystemExit(main())
