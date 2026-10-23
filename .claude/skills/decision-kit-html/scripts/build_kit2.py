"""判断キット v2 の組み立て: spec の JSON → 1 項目ずつめくる 1 ファイルの HTML。

使い方:
  python build_kit2.py <spec.json> <out.html> [--images images.json] [--image-root <folder>]... [--strict]

- 絵（visuals）は 1 項目に 1 枚以上（無ければ止める）。種類は original（原図）> mock（モック）> illustration（挿絵）> table / chart（表・グラフ）。
  原図・モックがあるのに挿絵や表しか先頭に無いときは知らせる（先頭 = いちばん大きく見える絵）。
- 文字の上限（課題・説明・質問・選択肢・理由）を超えたら知らせる。--strict では知らせがあれば exit 1。
- 画像は src にファイルのパス / data URI / "{{IMG:name}}"（--images の JSON から差し替え）を書ける。パスは spec からの相対。
  本番の画面・図面の切り抜きは repo に入れず、公開版にだけ埋め込む（--images は scratch に置く）。
"""
import base64
import json
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "template.html"

KINDS = ["original", "mock", "illustration", "table", "chart"]
# 文字の上限（タグを除いた文字数）
LIMITS = {"title": 24, "issue": 120, "explain_items": 3, "explain_each": 90, "question": 60, "option_label": 50, "why": 60, "options_min": 2, "options_max": 4}


def plain(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "")


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def main(argv):
    if len(argv) < 3:
        raise SystemExit(__doc__)
    spec_path, out_path = Path(argv[1]), Path(argv[2])
    strict = "--strict" in argv
    image_roots = [argv[i + 1] for i, a in enumerate(argv) if a == "--image-root" and i + 1 < len(argv)]
    images = {}
    if "--images" in argv:
        i = argv.index("--images")
        if i + 1 >= len(argv):
            raise SystemExit("--images の後に JSON のパスが要る")
        images = json.loads(Path(argv[i + 1]).read_text(encoding="utf-8"))
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    errors, warns = [], []

    def fix_src(src: str, where: str) -> str:
        if not src:
            return src
        m = re.fullmatch(r"\{\{IMG:([A-Za-z0-9_-]+)\}\}", src)
        if m:
            if m.group(1) not in images:
                errors.append(f"{where}: 画像 {m.group(1)} が --images に無い")
                return ""
            return images[m.group(1)]
        if src.startswith("data:") or src.startswith("https://") or src.startswith("http://"):
            return src
        p = (spec_path.parent / src).resolve()
        # 公開する HTML に埋め込むので、spec の置き場（か --image-root）の外のファイルは読まない（../.env 等を出さない）
        roots = [spec_path.parent.resolve()] + [Path(r).resolve() for r in image_roots]
        if not any(p.is_relative_to(r) for r in roots):
            errors.append(f"{where}: 画像は spec の置き場か --image-root の中だけ（{src}）")
            return ""
        if not p.exists():
            errors.append(f"{where}: 画像のファイルが無い {src}")
            return ""
        mime = mimetypes.guess_type(str(p))[0] or ""
        if not mime.startswith("image/"):
            errors.append(f"{where}: 画像のファイルではない {src}（{mime or '種類不明'}）")
            return ""
        return data_uri(p)

    for k in ("title", "summaryTitle", "summaryFooter", "items"):
        if k not in spec:
            errors.append(f"spec に {k} が無い")
    ids = set()
    for it in spec.get("items", []):
        where = it.get("id", "?")
        if where in ids:
            errors.append(f"{where}: id が重なっている")
        ids.add(where)
        vs = it.get("visuals") or []
        if not vs:
            errors.append(f"{where}: 絵が無い（1 項目に必ず 1 枚。原図 > モック > 挿絵 > 表・グラフ）")
        for n, v in enumerate(vs):
            if v.get("kind") not in KINDS:
                errors.append(f"{where}: 絵の種類 {v.get('kind')} は使えない（{' / '.join(KINDS)}）")
            if v.get("kind") in ("original", "illustration") and not v.get("src"):
                errors.append(f"{where}: 絵 {n + 1}（{v.get('kind')}）に src が無い")
            if v.get("kind") in ("original", "illustration") or (v.get("kind") == "mock" and v.get("src")):
                v["src"] = fix_src(v.get("src", ""), f"{where} 絵 {n + 1}")
            if v.get("kind") == "mock" and not (v.get("html") or v.get("url")):
                errors.append(f"{where}: モックは html か url が要る")
            if v.get("kind") == "table" and not (v.get("columns") and v.get("rows")):
                errors.append(f"{where}: 表は columns と rows が要る")
            if v.get("kind") == "chart" and not v.get("bars"):
                errors.append(f"{where}: グラフは bars が要る")
            if not v.get("caption"):
                warns.append(f"{where}: 絵 {n + 1} に説明（caption）が無い")
        kinds = [v.get("kind") for v in vs if v.get("kind") in KINDS]
        if kinds and vs[0].get("kind") in KINDS and KINDS.index(kinds[0]) > min(KINDS.index(k) for k in kinds):
            warns.append(f"{where}: 先頭の絵が {kinds[0]}。より上の種類（{min(kinds, key=KINDS.index)}）を先頭に")
        # 文字の上限
        if len(plain(it.get("title", ""))) > LIMITS["title"]:
            warns.append(f"{where}: 見出しが長い（{LIMITS['title']} 字まで）")
        for f in ("issue", "question"):
            if not it.get(f):
                errors.append(f"{where}: {f} が無い")
            elif len(plain(it[f])) > LIMITS[f]:
                warns.append(f"{where}: {f} が長い（{len(plain(it[f]))} / {LIMITS[f]} 字）。細かい事実は more（▸ 詳しく）へ")
        ex = it.get("explain") or []
        if not ex:
            errors.append(f"{where}: explain が無い")
        if len(ex) > LIMITS["explain_items"]:
            warns.append(f"{where}: 説明が {len(ex)} つ（{LIMITS['explain_items']} つまで）。残りは more へ")
        for e in ex:
            if len(plain(e)) > LIMITS["explain_each"]:
                warns.append(f"{where}: 説明の 1 つが長い（{len(plain(e))} / {LIMITS['explain_each']} 字）")
        opts = it.get("options") or []
        if not (LIMITS["options_min"] <= len(opts) <= LIMITS["options_max"]):
            warns.append(f"{where}: 選択肢は {LIMITS['options_min']}〜{LIMITS['options_max']} 個（今 {len(opts)}）")
        for o in opts:
            if len(plain(o.get("label", ""))) > LIMITS["option_label"]:
                warns.append(f"{where} {o.get('k')}: 選択肢が長い（{LIMITS['option_label']} 字まで）")
            if len(plain(o.get("why", ""))) > LIMITS["why"]:
                warns.append(f"{where} {o.get('k')}: 理由が長い（{LIMITS['why']} 字まで）")
        if it.get("rec") and it["rec"] not in [o.get("k") for o in opts]:
            errors.append(f"{where}: rec {it['rec']} が選択肢に無い")
        if not it.get("rec"):
            warns.append(f"{where}: AI推奨（rec）が無い")

    for m in warns:
        print("WARN", m)
    for m in errors:
        print("ERROR", m)
    if errors or (strict and warns):
        raise SystemExit(1)
    html = TEMPLATE.read_text(encoding="utf-8")
    # < を全部 JSON のエスケープ（バックスラッシュ u003c）に（モックの html に <!-- や </script が入っても、キットの script が閉じたり壊れたりしない）
    payload = json.dumps(spec, ensure_ascii=False).replace("<", "\\u003c")
    html = html.replace("{{TITLE}}", plain(spec["title"])[:60]).replace("/*SPEC*/", payload)
    out_path.write_text(html, encoding="utf-8")
    print(f"built {out_path} ({len(html)} bytes, {len(spec['items'])} items, {len(warns)} warn)")


if __name__ == "__main__":
    main(sys.argv)
