"""回答が返ったあと（と出荷が進むたび）、spec の sections の先頭に「決定記録」の節を足す。再実行すると同じ節を置き換える。

使い方: python add_decisions.py <spec.json> <decisions.json>
  decisions.json = {
    "date": "2026-10-03",
    "h2": "回答は 10-03 に返り、…",                      # 省略可（既定 = "<date> に決まったこと"）
    "sub": "利用者の回答（8 問）。メモ: …",              # 省略可
    "rows": [["Q1 カードの並び", "A", "cycle X-L1-…（局所、migration ゼロ）", "#958"],
             ["Q6 DB の変更の進め方", "A", "migration 2 本の下書き + 巻き戻す試験", "未着手"]]
  }                                                         # 列 = 問い / 決定 / AI がすること / PR か状態

そのあと **inject_images.py（本番の画像があるとき）→ build_kit.py --strict → 同じ `url` へ再 publish**（URL が保たれる。
repo の spec から直接 build すると placeholder のまま公開される）。Markdown 正本の §決定記録 も同じ表で揃える。
出荷のたびに最後の列を PR 番号へ直す（「AI がすること」を出荷前の予定のまま残さない）。

書き方の約束: 「決定」の列は人の答えをそのまま出すので HTML をエスケープする。ほかの列と h2 / sub は AI が書くので
HTML 可（リンク・<code>）。spec 全体を indent=2 で書き直すので、手で整形した spec は差分が全体に出る。
"""
import html
import json
import re
import sys

if len(sys.argv) != 3:
    raise SystemExit(__doc__)
spec_path, dec_path = sys.argv[1:3]
with open(spec_path, encoding="utf-8") as f:
    spec = json.load(f)
with open(dec_path, encoding="utf-8") as f:
    dec = json.load(f)

rows = dec["rows"]
if not rows or any(len(r) != 4 for r in rows):
    raise SystemExit("rows は [問い, 決定, AI がすること, PR か状態] の 4 列")


def plain(s):
    return re.sub(r"<[^>]+>", "", str(s)).strip()


# 出荷に進んだ数 = 最後の列（タグを除いた字）が PR 番号（#…）か「済」で始まるもの。PR が出ただけでマージ前のものも含む
started = sum(1 for r in rows if plain(r[3]).startswith(("#", "済")))


def cell(s, escape=False):
    return f"<td><b>{html.escape(str(s))}</b></td>" if escape else f"<td>{s}</td>"


trs = "".join(f"<tr>{cell(q)}{cell(k, escape=True)}{cell(a)}{cell(pr)}</tr>" for q, k, a, pr in rows)
table = (
    "<div class='tbl-wrap'><table><thead><tr><th>問い</th><th>決定</th><th>AI がすること</th><th>PR / 状態</th></tr></thead>"
    f"<tbody>{trs}</tbody></table></div>"
)
section = {
    "eyebrow": f"00 · 決定記録（{dec['date']} 追記）",
    "h2": dec.get("h2") or f"{dec['date']} に決まったこと",
    "sub": dec.get("sub", "下の問いは当時のまま残す（選択は保存されない）。"),
    "visuals": [{"type": "meter", "title": f"{len(rows)} 問のうち PR に進んだもの（PR 番号か 済）", "value": started, "max": len(rows), "unit": "問"}],
    "html": table,
}
sections = [s for s in spec.get("sections", []) if not str(s.get("eyebrow", "")).startswith("00 · 決定記録") and s.get("eyebrow") != "決定記録"]
spec["sections"] = [section] + sections
with open(spec_path, "w", encoding="utf-8", newline="") as f:
    json.dump(spec, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"decision section written: {len(rows)} rows, {started} started")
