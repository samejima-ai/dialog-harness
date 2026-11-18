"""判断キット v2 の組み立て: spec の JSON → 1 項目ずつめくる 1 ファイルの HTML。

使い方:
  python build_kit2.py <spec.json> <out.html> [--images images.json] [--image-root <folder>]... [--strict]

- 絵（visuals）は 1 項目に 1 枚以上（無ければ止める）。種類は
  original（現物）> template（様式）> mock（モック）> illustration（挿絵）> table / chart（表・グラフ）。
  上の種類があるのに下の種類を先頭にすると知らせる（先頭 = いちばん大きく見える絵）。
- 現物・様式・挿絵は src（画像）か file（xlsx・docx・pptx・pdf・画像）。file は render_visual.py で PNG にして埋め込む（page でページ、trim で余白の切り落とし）。
  確かめる対象は全体を見せたまま強調する: focus = 表計算のセル範囲（塗り＋赤枠）/ box = [左,上,幅,高さ]%（外を暗く＋赤枠）。
  現物（target=exists）で file を使うのに focus も box も無いときは知らせる（どこを見るのか分からないため）。
- 確認の項目は target を書く:
    "exists" = 確かめる物がもうある → 先頭の絵は現物（original）でなければ止める
    "new"    = まだ無い（これから作る）→ 先頭の絵は様式（template）か挿絵・モック。現物を先頭にすると止める
  様式には source（どの既定の様式・見本か）を書く。無ければ知らせる。
- 文字の上限（課題・説明・質問・選択肢・理由）を超えたら知らせる。--strict では知らせがあれば exit 1。
- 画像は src にファイルのパス / data URI / "{{IMG:name}}"（--images の JSON から差し替え）を書ける。パスは spec からの相対。
  本番の画面・図面の切り抜きは repo に入れず、公開版にだけ埋め込む（--images は scratch に置く）。
"""
import base64
import json
import mimetypes
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "template.html"

KINDS = ["original", "template", "mock", "illustration", "table", "chart"]
PICTURE = ("original", "template", "illustration")  # 画像で見せる種類（src か file が要る）
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

    render_dir = Path(tempfile.mkdtemp(prefix="kit2-render-"))

    def fix_file(file: str, page: int, where: str, trim=None, focus=None, box=None) -> str:
        """xlsx・docx・pdf・画像 → PNG → data URI。置き場の決まりは fix_src と同じ。"""
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from render_visual import render
        p = (spec_path.parent / file).resolve()
        roots = [spec_path.parent.resolve()] + [Path(r).resolve() for r in image_roots]
        if not any(p.is_relative_to(r) for r in roots):
            errors.append(f"{where}: file は spec の置き場か --image-root の中だけ（{file}）")
            return ""
        if not p.exists():
            errors.append(f"{where}: file が無い {file}")
            return ""
        try:
            out = render(p, render_dir / f"{len(list(render_dir.iterdir()))}.png", page, trim=trim, focus=focus, box=box)
        except Exception as e:  # 絵にできないときは止める（黙って抜かない）
            errors.append(f"{where}: {file} を絵にできない（{e}）")
            return ""
        return data_uri(out)

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
            errors.append(f"{where}: 絵が無い（1 項目に必ず 1 枚。現物 > 様式 > モック > 挿絵 > 表・グラフ）")
        for n, v in enumerate(vs):
            if v.get("kind") not in KINDS:
                errors.append(f"{where}: 絵の種類 {v.get('kind')} は使えない（{' / '.join(KINDS)}）")
            if v.get("kind") in PICTURE and not (v.get("src") or v.get("file")):
                errors.append(f"{where}: 絵 {n + 1}（{v.get('kind')}）に src か file が無い")
            if v.get("kind") in PICTURE and v.get("file") and not v.get("src"):
                v["src"] = fix_file(v["file"], int(v.get("page", 1)), f"{where} 絵 {n + 1}", v.get("trim"), v.get("focus"), v.get("box"))
                v["file"] = Path(v["file"]).name  # 公開版に出すのはファイル名だけ（置き場のパスは出さない）
            elif v.get("kind") in PICTURE or (v.get("kind") == "mock" and v.get("src")):
                v["src"] = fix_src(v.get("src", ""), f"{where} 絵 {n + 1}")
            if v.get("kind") == "template" and not v.get("source"):
                warns.append(f"{where}: 絵 {n + 1}（様式）に source が無い（どの既定の様式・見本かを書く）")
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
        for n, v in enumerate(vs):
            if it.get("target") == "exists" and v.get("kind") == "original" and v.get("file") and not (v.get("focus") or v.get("box")) and not v.get("whole"):
                warns.append(f"{where}: 絵 {n + 1}（現物）に focus / box が無い。全体の中で対象を強調する（全体そのものを見るなら whole: true）")
        # 確認の項目: ある物は現物を、無い物は様式・見本を先頭に
        tgt = it.get("target")
        first = vs[0].get("kind") if vs else None
        if tgt not in (None, "exists", "new"):
            errors.append(f"{where}: target は exists か new（今 {tgt}）")
        if tgt == "exists" and first != "original":
            errors.append(f"{where}: 確かめる物がある（target=exists）のに先頭の絵が現物でない（{first}）。現物を先頭に")
        if tgt == "new" and first not in ("template", "illustration", "mock"):
            errors.append(f"{where}: まだ無い物（target=new）の先頭は 様式 か 挿絵・モック（今 {first}）")
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
