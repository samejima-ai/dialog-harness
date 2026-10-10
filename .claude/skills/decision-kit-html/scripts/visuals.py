"""visuals.py — 判断キットの「絵」を spec の数値・語から組む（build_kit.py から呼ぶ）。

手書き SVG / HTML を毎回書かなくても、spec に `{"type": "...", ...}` を置けば絵になる。
型の一覧と使い分けは references/visuals.md。文字列欄は他の spec 欄と同じく HTML 可（信頼して埋める）。
SVG の <text> に入る欄だけはタグを落として escape する。
"""
import html as _html
import re

COLORS = ("c1", "c2", "c3", "c4")


class VisualError(ValueError):
    pass


def _plain(s) -> str:
    return _html.escape(re.sub(r"<[^>]+>", "", str(s if s is not None else "")))


def _num(v, where: str) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        raise VisualError(f"{where}: 数値ではない値 {v!r}")


def _fmt(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:.1f}"


def _color(c, i: int) -> str:
    if c in (None, ""):
        return f"var(--{COLORS[i % 4]})"
    if c == "neutral":
        return "neutral"
    if c in COLORS:
        return f"var(--{c})"
    if c in ("accent", "no"):
        return f"var(--{c})"
    raise VisualError(f"color は c1〜c4 / neutral / accent / no のみ（{c!r}）。新色は design.md の validator を通してから")


# ---------- 型ごとの描画 ----------

def _stack(v):
    items = v.get("items") or []
    unit = v.get("unit", "件")
    total = sum(_num(it.get("value"), "stack.items.value") for it in items)
    segs, legend = [], []
    for i, it in enumerate(items):
        val = _num(it.get("value"), "stack.items.value")
        col = _color(it.get("color"), i)
        tip = _plain(it.get("tip") or f"{it.get('label', '')} {_fmt(val)} {unit}")
        show = _fmt(val) if total and val / total >= 0.06 else ""
        if col == "neutral":
            segs.append(f'<div class="seg neutral" style="flex:{val}" data-tip="{tip}">{show}</div>')
            legend.append(f'<span><i class="sw neutral"></i>{it.get("label", "")}</span>')
        else:
            segs.append(f'<div class="seg" style="flex:{val};background:{col}" data-tip="{tip}">{show}</div>')
            legend.append(f'<span><i class="sw" style="background:{col}"></i>{it.get("label", "")} <b class="mono">{_fmt(val)}</b></span>')
    return f'<div class="bar">{"".join(segs)}</div><div class="legend">{"".join(legend)}</div>'


def _waffle(v):
    items = v.get("items") or []
    unit = v.get("unit", "件")
    cells, legend = [], []
    for i, it in enumerate(items):
        n = int(_num(it.get("value"), "waffle.items.value"))
        col = _color(it.get("color"), i)
        tip = _plain(it.get("tip") or f"{it.get('label', '')} {n} {unit}")
        cls = "cell neutral" if col == "neutral" else "cell"
        style = "" if col == "neutral" else f' style="background:{col}"'
        cells.extend(f'<i class="{cls}"{style} data-tip="{tip}"></i>' for _ in range(n))
        sw = '<i class="sw neutral"></i>' if col == "neutral" else f'<i class="sw" style="background:{col}"></i>'
        legend.append(f'<span>{sw}{it.get("label", "")} <b class="mono">{n}</b></span>')
    if len(cells) > 200:
        raise VisualError("waffle は 200 マスまで（それ以上は stack を使う）")
    return f'<div class="waffle">{"".join(cells)}</div><div class="legend">{"".join(legend)}</div>'


def _hbar(v):
    items = v.get("items") or []
    unit = v.get("unit", "")
    mx = v.get("max") or max((_num(it.get("value"), "hbar.items.value") for it in items), default=1) or 1
    rows = []
    for it in items:
        val = _num(it.get("value"), "hbar.items.value")
        w = max(0.0, min(100.0, val / mx * 100))
        cls = "hb-fill hl" if it.get("hl") else "hb-fill"
        note = f'<span class="hb-note">{it["note"]}</span>' if it.get("note") else ""
        rows.append(
            f'<div class="hb-row"><div class="hb-label">{it.get("label", "")}</div>'
            f'<div class="hb-track"><div class="{cls}" style="width:{w:.1f}%"></div></div>'
            f'<div class="hb-val mono">{_fmt(val)}{unit}</div>{note}</div>')
    return f'<div class="hbar">{"".join(rows)}</div>'


def _trend(v):
    pts = v.get("points") or []
    if not 2 <= len(pts) <= 12:
        raise VisualError("trend は 2〜12 点")
    unit = v.get("unit", "")
    ys = [_num(p.get("y"), "trend.points.y") for p in pts]
    lo = min(0.0, min(ys))
    hi = max(ys) or 1
    W, H, L, R, T, B = 400, 190, 34, 16, 26, 30
    def X(i): return L + (W - L - R) * (i / (len(pts) - 1))
    def Y(y): return T + (H - T - B) * (1 - (y - lo) / ((hi - lo) or 1))
    grid = []
    for k in range(4):
        gy = lo + (hi - lo) * k / 3
        grid.append(f'<line class="grid" x1="{L}" x2="{W - R}" y1="{Y(gy):.1f}" y2="{Y(gy):.1f}"/>'
                    f'<text x="{L - 6}" y="{Y(gy) + 4:.1f}" text-anchor="end">{_fmt(gy)}</text>')
    path = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(y):.1f}" for i, y in enumerate(ys))
    dots, labels = [], []
    for i, (p, y) in enumerate(zip(pts, ys)):
        last = i == len(pts) - 1
        dots.append(f'<circle cx="{X(i):.1f}" cy="{Y(y):.1f}" r="{6 if last else 5}" fill="var(--c1)" stroke="var(--ground)" stroke-width="2"/>')
        if len(pts) <= 8 or last:
            labels.append(f'<text class="{"lbl-mono-strong" if last else "lbl-strong"}" x="{X(i):.1f}" y="{Y(y) - 11:.1f}" text-anchor="middle">{_fmt(y)}{_plain(unit) if last else ""}</text>')
        labels.append(f'<text x="{X(i):.1f}" y="{H - 8}" text-anchor="middle">{_plain(p.get("x", ""))}</text>')
    return (f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{_plain(v.get("title", "推移"))}">'
            f'{"".join(grid)}<line class="axis" x1="{L}" x2="{W - R}" y1="{Y(lo):.1f}" y2="{Y(lo):.1f}"/>'
            f'<path d="{path}" fill="none" stroke="var(--c1)" stroke-width="2"/>{"".join(dots)}{"".join(labels)}</svg>')


def _flow(v):
    nodes = v.get("nodes") or []
    edges = v.get("edges") or []
    parts = []
    for i, n in enumerate(nodes):
        kind = n.get("kind", "normal")
        if kind not in ("normal", "strong", "dim", "stop"):
            raise VisualError(f"flow.nodes.kind は normal/strong/dim/stop（{kind!r}）")
        pill = ""
        if n.get("n") is not None:
            pill = f'<span class="fl-pill" style="background:{_color(n.get("c"), 0)}">{_plain(n["n"])}</span>'
        sub = f'<div class="fl-sub">{n["sub"]}</div>' if n.get("sub") else ""
        parts.append(f'<div class="fl-node {kind}">{pill}<div class="fl-label">{n.get("label", "")}</div>{sub}</div>')
        if i < len(nodes) - 1:
            e = edges[i] if i < len(edges) else "solid"
            if isinstance(e, str):
                e = {"style": e}
            st = e.get("style", "solid")
            if st not in ("solid", "loop", "no"):
                raise VisualError(f"flow.edges.style は solid/loop/no（{st!r}）")
            lab = f'<span class="fl-elab">{e["label"]}</span>' if e.get("label") else ""
            parts.append(f'<div class="fl-edge {st}" aria-hidden="true"><span class="fl-line"></span>{lab}</div>')
    back = f'<div class="fl-back">↺ {v["loop_back"]}</div>' if v.get("loop_back") else ""
    return f'<div class="flowh">{"".join(parts)}</div>{back}'


def _compare(v):
    def col(side, cls):
        d = v.get(side) or {}
        lis = []
        for it in d.get("items") or []:
            s = str(it)
            mark = ""
            if s.startswith("+ "):
                mark, s = '<b class="cmp-plus">＋</b>', s[2:]
            elif s.startswith("- ") or s.startswith("− "):
                mark, s = '<b class="cmp-minus">−</b>', s[2:]
            lis.append(f"<li>{mark}{s}</li>")
        return f'<div class="cmp-col {cls}"><div class="cmp-h">{d.get("title", "")}</div><ul>{"".join(lis)}</ul></div>'
    return (f'<div class="cmp">{col("before", "before")}'
            f'<div class="cmp-arrow" aria-hidden="true">→</div>{col("after", "after")}</div>')


_MARK = {2: ("full", "強"), 1: ("half", "中"), 0: ("empty", "弱"), -1: ("x", "×")}


def _dot(m) -> str:
    if m is None or m == "":
        return '<span class="mx-na">—</span>'
    m = int(m)
    cls, word = _MARK.get(m, _MARK[0])
    if cls == "x":
        return f'<span class="mx-x" title="{word}">×</span>'
    return f'<span class="mx-dot {cls}" title="{word}"></span>'


def _matrix(v):
    axes = v.get("axes") or []
    rows = v.get("rows") or []
    rec = v.get("rec")
    head = "".join(f"<th>{a}</th>" for a in axes)
    body = []
    for r in rows:
        marks = r.get("marks") or []
        if len(marks) != len(axes):
            raise VisualError(f"matrix.rows[{r.get('k')}].marks の数が axes と違う")
        cls = ' class="mx-rec"' if rec and r.get("k") == rec else ""
        body.append(f'<tr{cls}><td class="id">{_plain(r.get("k", ""))}</td><td>{r.get("label", "")}</td>'
                    + "".join(f'<td class="mx-c">{_dot(m)}</td>' for m in marks) + "</tr>")
    legend = ('<div class="legend"><span><span class="mx-dot full"></span>強い</span>'
              '<span><span class="mx-dot half"></span>中</span><span><span class="mx-dot empty"></span>弱い</span>'
              '<span><span class="mx-x">×</span>損なう</span></div>')
    return (f'<div class="tbl-wrap"><table class="mx"><thead><tr><th></th><th>案</th>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>{legend}')


def _stats(v):
    cells = []
    for i, it in enumerate(v.get("items") or []):
        style = f' style="color:{_color(it["c"], i)}"' if it.get("c") else ""
        cells.append(f'<div class="stat"><div class="n"{style}>{it.get("n", "")}</div><div class="l">{it.get("l", "")}</div></div>')
    return f'<div class="stat-row">{"".join(cells)}</div>'


def _steps(v):
    cells = []
    for it in v.get("items") or []:
        now = " now" if it.get("now") else (" later" if it.get("later") else "")
        cells.append(f'<div class="step{now}"><div class="t">{it.get("t", "")}</div>'
                     f'<div class="m">{it.get("m", "")}</div><div class="step-b">{it.get("body", "")}</div></div>')
    return f'<div class="steps">{"".join(cells)}</div>'


def _meter(v):
    val = _num(v.get("value"), "meter.value")
    mx = _num(v.get("max", 100), "meter.max") or 1
    unit = v.get("unit", "")
    w = max(0.0, min(100.0, val / mx * 100))
    return (f'<div class="meter"><div class="meter-track"><div class="meter-fill" style="width:{w:.1f}%"></div></div>'
            f'<div class="meter-lab mono">{_fmt(val)} / {_fmt(mx)}{unit}</div></div>')


def _timeline(v):
    ev = v.get("events") or []
    items = []
    for e in ev:
        kind = e.get("kind", "normal")
        if kind not in ("normal", "now", "stop", "future"):
            raise VisualError(f"timeline.events.kind は normal/now/stop/future（{kind!r}）")
        items.append(f'<li class="tl-ev {kind}"><span class="tl-dot"></span><span class="tl-d mono">{e.get("date", "")}</span>'
                     f'<span class="tl-l">{e.get("label", "")}</span></li>')
    gap = f'<div class="tl-gap">{v["gap"]}</div>' if v.get("gap") else ""
    return f'<ol class="tl">{"".join(items)}</ol>{gap}'


# ---------- 原画（figures）と表（table） ----------

_IMG_PH = re.compile(r"^\{\{IMG:([A-Za-z0-9_-]+)\}\}$")


def img_tag(src, alt: str, cls: str) -> str:
    """<img> を組む。repo の spec のまま（{{IMG:name}} が残っている）なら壊れた画像でなく placeholder の箱を出す。"""
    src = str(src or "").strip()
    m = _IMG_PH.match(src)
    if m:
        return (f'<span class="{cls} img-ph" role="img" aria-label="{_plain(alt)}">原画 <code>{_html.escape(m.group(1))}</code>'
                f'<small>公開版にだけ埋め込む（inject_images.py）</small></span>')
    if not src:
        raise VisualError("img が空")
    return f'<img class="{cls}" src="{_html.escape(src, quote=True)}" alt="{_plain(alt)}" loading="lazy" decoding="async">'


def _figures(v):
    items = v.get("items") or []
    if not items:
        raise VisualError("figures.items が空")
    try:
        cols = int(v.get("cols") or min(len(items), 3))
    except (TypeError, ValueError):
        raise VisualError(f"figures.cols は 1〜4 の整数（{v.get('cols')!r}）")
    if not 1 <= cols <= 4:
        raise VisualError(f"figures.cols は 1〜4（{cols}）")
    figs = []
    for i, it in enumerate(items):
        if not isinstance(it, dict) or not it.get("img"):
            raise VisualError(f"figures.items[{i}] に img が無い")
        cap = it.get("caption", "")
        alt = it.get("alt") or cap or f"原画 {i + 1}"
        img = img_tag(it["img"], alt, "fig-img")
        if not img.startswith('<span'):
            img = (f'<button type="button" class="fig-zoom" data-zoom aria-label="拡大して見る: {_plain(alt)}">'
                   f'{img}<span class="fig-zoom-hint" aria-hidden="true">拡大</span></button>')
        tag = f'<span class="fig-tag mono">{_plain(it["tag"])}</span>' if it.get("tag") else ""
        capt = f'<figcaption class="fig-cap">{tag}{cap}</figcaption>' if (cap or tag) else ""
        note = (f'<div class="fig-note"><span class="fig-note-h">見てほしい点</span>{it["note"]}</div>'
                if it.get("note") else "")
        figs.append(f'<figure class="fig">{img}{capt}{note}</figure>')
    return f'<div class="figs" data-cols="{cols}" style="--cols:{cols}">{"".join(figs)}</div>'


_TMARK = {"●": ("full", "強い"), "◐": ("half", "中"), "○": ("empty", "弱い"), "×": ("x", "損なう"), "—": ("na", "該当なし")}


def _tcell(c) -> str:
    s = "" if c is None else str(c)
    t = s.strip()
    if t in _TMARK:
        cls, word = _TMARK[t]
        if cls == "x":
            return f'<span class="mx-x" title="{word}">×</span><span class="sr">{word}</span>'
        if cls == "na":
            return '<span class="mx-na">—</span>'
        return f'<span class="mx-dot {cls}" title="{word}"></span><span class="sr">{word}</span>'
    return s


def _table(v):
    cols = v.get("columns") or []
    rows = v.get("rows") or []
    if not cols or not rows:
        raise VisualError("table は columns と rows が要る")
    labels, aligns = [], []
    for c in cols:
        if isinstance(c, dict):
            labels.append(c.get("label", ""))
            aligns.append(c.get("align", ""))
        else:
            labels.append(str(c))
            aligns.append("")
    hl_col = v.get("hl_col")
    if isinstance(hl_col, str):
        hl_col = labels.index(hl_col) if hl_col in labels else None
        if hl_col is None:
            raise VisualError(f"table.hl_col {v.get('hl_col')!r} が columns に無い")
    hl_row = v.get("hl_row")
    rowhead = v.get("row_head", True)

    def cls(j, extra=""):
        cs = [x for x in (extra, "hl-col" if j == hl_col else "",
                          f"al-{aligns[j]}" if aligns[j] in ("right", "center") else "") if x]
        return f' class="{" ".join(cs)}"' if cs else ""

    head = "".join(f'<th scope="col"{cls(j)}>{lab}</th>' for j, lab in enumerate(labels))
    body, used_mark = [], False
    for i, r in enumerate(rows):
        cells, hl = (r.get("cells") or [], bool(r.get("hl"))) if isinstance(r, dict) else (r, False)
        if len(cells) != len(labels):
            raise VisualError(f"table.rows[{i}] のセル数 {len(cells)} が columns {len(labels)} と違う")
        if isinstance(hl_row, int) and i == hl_row:
            hl = True
        elif isinstance(hl_row, str) and _plain(cells[0]) == _plain(hl_row):
            hl = True
        tds = []
        for j, c in enumerate(cells):
            used_mark = used_mark or str(c if c is not None else "").strip() in _TMARK
            if j == 0 and rowhead:
                tds.append(f'<th scope="row"{cls(j, "rh")}>{_tcell(c)}</th>')
            else:
                tds.append(f'<td{cls(j, "mk" if str(c).strip() in _TMARK else "")}>{_tcell(c)}</td>')
        trc = ' class="hl"' if hl else ""
        body.append(f'<tr{trc}>{"".join(tds)}</tr>')
    legend = ""
    lg = v.get("legend", True)
    if used_mark and lg:
        words = list(lg) + ["", "", "", ""] if isinstance(lg, list) else ["強い", "中", "弱い", "損なう"]
        marks = ['<span class="mx-dot full"></span>', '<span class="mx-dot half"></span>',
                 '<span class="mx-dot empty"></span>', '<span class="mx-x">×</span>']
        legend = '<div class="legend">' + "".join(
            f"<span>{m}{w}</span>" for m, w in zip(marks, words[:4]) if w) + "</div>"
    return (f'<div class="tbl-wrap" tabindex="0" role="region" aria-label="{_plain(v.get("title") or "表")}（横にスクロールできます）">'
            f'<table class="dt"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>{legend}')


RENDER = {
    "stack": _stack, "waffle": _waffle, "hbar": _hbar, "trend": _trend, "flow": _flow,
    "compare": _compare, "matrix": _matrix, "stats": _stats, "steps": _steps,
    "meter": _meter, "timeline": _timeline, "figures": _figures, "table": _table,
}


def render(v: dict) -> str:
    t = v.get("type")
    if t == "html":
        body = v.get("html", "")
    elif t in RENDER:
        body = RENDER[t](v)
    else:
        raise VisualError(f"未知の visual type {t!r}（使えるのは {', '.join(sorted(RENDER))} / html）")
    title = f'<figcaption class="viz-t">{v["title"]}</figcaption>' if v.get("title") else ""
    cap = f'<div class="caption">{v["caption"]}</div>' if v.get("caption") else ""
    return f'<figure class="viz viz-{t}">{title}{body}{cap}</figure>'


def render_many(vs) -> str:
    if not vs:
        return ""
    if isinstance(vs, dict):
        vs = [vs]
    return "".join(render(v) for v in vs)
