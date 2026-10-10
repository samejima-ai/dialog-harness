#!/usr/bin/env python3
"""build_kit.py — 判断キット spec(JSON) + テンプレートから 1 枚の HTML を組む。

使い方:
  python .claude/skills/decision-kit-html/scripts/build_kit.py <spec.json> <out.html>

spec.json の骨格（references/spec-schema.md に全項目）:
  {
    "key": "fb-question-path-0902",      # localStorage のキー。キットごとに一意
    "title": "…", "eyebrow": "…", "lede": "…",
    "meta": ["<span>…</span>", …],        # 上部メタ行（HTML 可）
    "hero_visuals": [ {"type": "stack", …}, {"type": "trend", …} ],  # 要旨の絵（宣言的、references/visuals.md）
    "hero_html": "…",                     # 手書きの要旨パネル（hero_visuals で足りないときだけ）
    "sections": [ {"eyebrow": "01 · …", "h2": "…", "sub": "…", "visuals": [ … ], "html": "…"}, … ],
    "questions_section": {"eyebrow": "…", "h2": "…", "sub": "…"},
    "questions": [ { "id": "Q1", "title": "…", "short": "…", "time": "5 分", "fbs": "…",
                     "quote": "…", "visuals": [ {"type": "matrix", …} ], "facts": ["…"], "options": [{"k":"A","label":"…","rec":"推奨"}],
                     "after": "…", "multi": false, "extra": "<table…>" }, … ],
    "after_sections": [ … 同じ形 … ],
    "foot": "…", "summaryTitle": "…", "summaryFooter": "…",
    "glossary": {"P3": "本番の DB に変更を当てる作業。人が行い、AI は行わない"}   # 用語 → 1〜2 行
  }

2026-10-04 追加: visual の `figures`（原画、押すと拡大）/ `table`（表）、option の `example`（1 行の例）/
`img`（小さな絵、`{{IMG:name}}` 可）、question の `recWhy`（推奨の理由）。読み方・回答バー・キー操作は
テンプレートが自動で付ける。回答まとめの行の形は変えない（references/spec-schema.md §回答まとめの形式）。

2026-10-10 追加（判断キット改訂キット 1010）: top-level の `glossary`（用語 → 1〜2 行の説明）。各ブロック（要旨・節・
問い）で最初に出た用語の横に (i) が付き、押すとその場の下に開く。事実・決まったら はテンプレートが「▸ 詳しく」に畳み、
答えた問いは 1 行に畳む（spec の書き方は変わらない）。

出力は <title> と <style> から始まる本文のみ（Artifact 側が <html><head> を包む）。
ローカルで見るときは `--standalone` を付けると doctype + body を巻く。

絵の点検: 要旨に絵が無い / 絵の無い問いがある と WARN を出す（`visual_skip: "理由"` で意図的に外せる）。
用語の点検: glossary の用語が (i) の付く所（lede・要旨の絵・節・問い）に無い / 説明が長すぎる（{GLOSS_MAX} 字超）と WARN。
`--strict` を付けると WARN 1 件以上で exit 1（publish 前の既定）。
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals import VisualError, img_tag, render_many  # noqa: E402

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"
GLOSS_MAX = 80  # 用語の説明は 1〜2 行（スマホで 3 行を超えない長さ）
if __doc__:  # python -OO では None
    __doc__ = __doc__.replace("{GLOSS_MAX}", str(GLOSS_MAX))


def _plain_text(spec: dict) -> str:
    """テンプレートが用語の (i) を付ける所（lede・hero_visuals・節・問いのカード）の、表示される文字だけを 1 本にする。
    JSON のキーや型名・hero_html / meta / foot（(i) が付かない所）は入れない。"""
    def vis(v):
        try:
            return render_many(v)
        except VisualError:
            return ""
    parts = [spec.get("lede", ""), vis(spec.get("hero_visuals"))]
    for sec in spec.get("sections", []) + spec.get("after_sections", []):
        parts += [sec.get("eyebrow", ""), sec.get("h2", ""), sec.get("sub", ""), vis(sec.get("visuals")), sec.get("html", "")]
    for q in spec.get("questions", []):
        parts += [q.get("title", ""), q.get("fbs", ""), q.get("quote", ""), vis(q.get("visuals") or q.get("visual")),
                  q.get("extra", ""), q.get("recWhy", ""), q.get("after", "")] + list(q.get("facts") or [])
        for o in q.get("options", []):
            parts += [o.get("label", ""), o.get("example", "")]
    text = " ".join(str(x) for x in parts if x)
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S)
    return htmllib.unescape(re.sub(r"<[^>]+>", " ", text))


def _has_term(text: str, term: str) -> bool:
    """英数字の用語は語の途中に当てない（テンプレートの findTerm と同じ規則）。"""
    left = r"(?<![A-Za-z0-9])" if re.match(r"[A-Za-z0-9]", term) else ""
    right = r"(?![A-Za-z0-9])" if re.search(r"[A-Za-z0-9]$", term) else ""
    return re.search(left + re.escape(term) + right, text) is not None


def section_html(s: dict) -> str:
    parts = ["<section>"]
    if s.get("eyebrow"):
        parts.append(f'<div class="eyebrow">{s["eyebrow"]}</div>')
    if s.get("h2"):
        parts.append(f"<h2>{s['h2']}</h2>")
    if s.get("sub"):
        parts.append(f'<p class="sub">{s["sub"]}</p>')
    parts.append(render_many(s.get("visuals")))
    parts.append(s.get("html", ""))
    parts.append("</section>")
    return "\n".join(parts)


def hero_html(spec: dict) -> str:
    vis = render_many(spec.get("hero_visuals"))
    if vis:
        vis = f'<div class="hero-viz">{vis}</div>'
    return vis + spec.get("hero_html", "")


def lint(spec: dict) -> list:
    """絵の予算を点検する。返り値 = WARN 文の列。"""
    warns = []
    if not (spec.get("hero_visuals") or spec.get("hero_html")):
        warns.append("要旨に絵が無い（hero_visuals に stack / waffle / stats / timeline のどれかを置く）")
    for q in spec.get("questions", []):
        if not (q.get("visuals") or q.get("visual") or q.get("visual_skip")):
            warns.append(f"{q.get('id')}: 絵が無い（選択肢の比較なら matrix、今→提案なら compare / flow。"
                         f"本当に要らなければ visual_skip に理由）")
    # 新しい欄（figures / table）だけに掛かる点検。既存の spec はこれらを使っていないので WARN は増えない
    places = [("要旨", spec.get("hero_visuals"))]
    places += [(s.get("eyebrow") or "節", s.get("visuals")) for s in spec.get("sections", []) + spec.get("after_sections", [])]
    places += [(q.get("id"), q.get("visuals") or q.get("visual")) for q in spec.get("questions", [])]
    for where, vs in places:
        if isinstance(vs, dict):
            vs = [vs]
        for v in vs or []:
            if v.get("type") == "figures":
                for i, it in enumerate(v.get("items") or []):
                    if not it.get("caption"):
                        warns.append(f"{where}: figures.items[{i}] に caption が無い（何を見る切り抜きかを 1 行で）")
                if len(v.get("items") or []) > 6:
                    warns.append(f"{where}: figures が {len(v['items'])} 枚（1 つの点に 1 枚。6 枚を超えたら問いを分ける）")
    gl = spec.get("glossary")
    if gl is not None:
        if not isinstance(gl, dict):
            warns.append("glossary は {用語: 説明} の object で書く")
        else:
            text = _plain_text(spec)
            for term, desc in gl.items():
                if not _has_term(text, term):
                    warns.append(f"glossary「{term}」が (i) の付く所（lede・要旨の絵・節・問い）に無い（表記を揃えるか消す。hero_html / meta / foot には付かない）")
                plain = re.sub(r"<[^>]+>", "", str(desc or ""))
                if not plain.strip():
                    warns.append(f"glossary「{term}」の説明が空")
                elif len(plain) > GLOSS_MAX:
                    warns.append(f"glossary「{term}」の説明が {len(plain)} 字（{GLOSS_MAX} 字以内 = 1〜2 行に。詳しくは facts へ）")
    return warns


def build(spec: dict) -> str:
    tpl = TEMPLATE.read_text(encoding="utf-8")
    qs = spec.get("questions_section", {})
    questions = []
    for q in spec.get("questions", []):
        q = dict(q)
        try:
            q["visualHtml"] = render_many(q.pop("visuals", None) or q.pop("visual", None))
            opts = []
            for o in q.get("options", []):
                o = dict(o)
                if o.get("img"):
                    o["imgHtml"] = img_tag(o.pop("img"), o.get("imgAlt") or re.sub(r"<[^>]+>", "", str(o.get("label", ""))), "opt-img")
                opts.append(o)
            q["options"] = opts
        except VisualError as e:
            raise VisualError(f"{q.get('id')}: {e}")
        questions.append(q)
    kit_data = {
        "key": spec.get("key", "kit"),
        "title": spec.get("title", ""),
        "questions": questions,
        "summaryTitle": spec.get("summaryTitle"),
        "summaryFooter": spec.get("summaryFooter"),
        "glossary": spec.get("glossary") if isinstance(spec.get("glossary"), dict) else {},
    }
    rep = {
        "{{TITLE}}": spec.get("title", ""),
        "{{EYEBROW}}": spec.get("eyebrow", ""),
        "{{LEDE}}": spec.get("lede", ""),
        "{{META}}": "".join(spec.get("meta", [])),
        "{{HERO}}": hero_html(spec),
        "{{SECTIONS}}": "\n".join(section_html(s) for s in spec.get("sections", [])),
        "{{Q_EYEBROW}}": qs.get("eyebrow", "決めること"),
        "{{Q_H2}}": qs.get("h2", "問い"),
        "{{Q_SUB}}": qs.get("sub", ""),
        "{{AFTER_SECTIONS}}": "\n".join(section_html(s) for s in spec.get("after_sections", [])),
        "{{FOOT}}": spec.get("foot", ""),
    }
    out = tpl
    for k, v in rep.items():
        out = out.replace(k, v)
    data = json.dumps(kit_data, ensure_ascii=False).replace("</", "<\\/")
    out = out.replace("/*__KIT_DATA__*/{}/*__END_KIT_DATA__*/", data)
    return out


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    spec = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    try:
        html = build(spec)
    except VisualError as e:
        print(f"ERROR visual: {e}", file=sys.stderr)
        sys.exit(1)
    warns = lint(spec)
    for w in warns:
        print(f"WARN {w}", file=sys.stderr)
    if "--standalone" in sys.argv:
        html = ('<!doctype html><html><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width"></head><body style="margin:0">'
                + html + "</body></html>")
    Path(args[1]).write_text(html, encoding="utf-8")
    print(f"built {args[1]} ({len(html.encode('utf-8'))} bytes, {len(spec.get('questions', []))} questions, {len(warns)} warn)")
    if warns and "--strict" in sys.argv:
        sys.exit(1)


if __name__ == "__main__":
    main()
