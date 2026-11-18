"""ファイル（Excel・Word・PowerPoint・PDF・画像）を判断キットの絵（PNG）にする。

使い方:
  python render_visual.py <file> <out.png> [--page N] [--dpi 150] [--trim | --no-trim] [--focus B3:D6] [--box 左,上,幅,高さ]

- 画像（png/jpg/webp/gif）はそのまま写す（大きすぎるときだけ長辺 1800px に縮める）
- PDF は N ページ目を PNG にする（pdftoppm）
- xlsx / xlsm / xls / csv / docx / doc / pptx / ppt / odt / ods は LibreOffice で PDF にしてから N ページ目を PNG にする
  （Excel は印刷範囲・改ページの設定どおりに出る。設定が無いと 1 ページ目が端だけのことがあるので、出来上がりを目で確かめる）
- 余白の切り落とし（trim）: 表計算（xlsx・csv 等）は既定で切る（紙の大半が白で中身が小さくなるため）。
  Word・PDF・PowerPoint は既定で切らない（紙面の割付・余白そのものが確かめる対象のため）
- 対象の強調（全体を俯瞰しつつ、対象を目立たせる）:
    focus = 表計算のセル範囲（"B3:D6" / "出面!B3:D6"）→ 写しの範囲を黄で塗り赤の太枠で囲んでから絵にする（元のファイルは触らない）
    box   = どの種類でも [左, 上, 幅, 高さ]（ページに対する %）→ 枠の外を薄く暗くし、赤枠で囲む
  focus の写しは openpyxl で作るため、図形・画像・グラフが落ちることがある。落ちて困るときは box を使う
build_kit2.py からも呼ばれる（visuals の file 欄）。
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

IMG = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
SHEET = {".xlsx", ".xlsm", ".xls", ".csv", ".ods"}
OFFICE = {".xlsx", ".xlsm", ".xls", ".csv", ".docx", ".doc", ".pptx", ".ppt", ".odt", ".ods", ".odp", ".rtf"}


def _shrink(png: Path, max_side: int = 1800) -> None:
    if shutil.which("convert"):
        subprocess.run(["convert", str(png), "-resize", f"{max_side}x{max_side}>", str(png)], check=True)


def _pdf_page(pdf: Path, out: Path, page: int, dpi: int) -> None:
    stem = out.with_suffix("")
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-f", str(page), "-l", str(page), "-singlefile", str(pdf), str(stem)],
                   check=True, capture_output=True)
    if not out.exists():
        raise RuntimeError(f"{pdf.name} の {page} ページ目が出せない（ページ数を確かめる）")


def _trim(png: Path) -> None:
    if shutil.which("convert"):
        subprocess.run(["convert", str(png), "-trim", "+repage", "-bordercolor", "white", "-border", "24", str(png)], check=True)


def _mark_cells(src: Path, focus: str, td: str) -> Path:
    """表計算の写しに、対象の範囲の塗りと太枠を付ける。"""
    from openpyxl import load_workbook
    from openpyxl.styles import Border, PatternFill, Side
    keep_vba = src.suffix.lower() == ".xlsm"
    wb = load_workbook(src, keep_vba=keep_vba)
    sheet, rng = (focus.split("!", 1) if "!" in focus else (None, focus))
    ws = wb[sheet.strip("'")] if sheet else wb.active
    if sheet:  # 対象のシートを先頭（＝1 ページ目）に回す
        wb.move_sheet(ws, offset=-wb.index(ws))
        wb.active = 0
    cells = ws[rng] if ":" in rng else ((ws[rng],),)  # 範囲 = 行のタプルのタプル / 1 セルはそろえる
    red = Side(style="thick", color="D62828")
    fill = PatternFill("solid", fgColor="FFF3B0")
    last_r, last_c = len(cells) - 1, len(cells[0]) - 1
    for i, row in enumerate(cells):
        for j, c in enumerate(row):
            c.fill = fill
            b = c.border
            c.border = Border(left=red if j == 0 else b.left, right=red if j == last_c else b.right,
                              top=red if i == 0 else b.top, bottom=red if i == last_r else b.bottom)
    out = Path(td) / src.name
    wb.save(out)
    return out


def _spotlight(png: Path, box) -> None:
    """[左, 上, 幅, 高さ]（%）の外を薄く暗くし、赤枠で囲む。"""
    out = subprocess.run(["identify", "-format", "%w %h", str(png)], check=True, capture_output=True, text=True).stdout.split()
    W, H = int(out[0]), int(out[1])
    x, y, w, h = (float(v) for v in box)
    x0, y0 = int(W * x / 100), int(H * y / 100)
    x1, y1 = int(W * (x + w) / 100), int(H * (y + h) / 100)
    lw = max(3, W // 300)
    subprocess.run(["convert", str(png), "-fill", "#00000026",
                    "-draw", f"rectangle 0,0 {W},{y0}", "-draw", f"rectangle 0,{y1} {W},{H}",
                    "-draw", f"rectangle 0,{y0} {x0},{y1}", "-draw", f"rectangle {x1},{y0} {W},{y1}",
                    "-fill", "none", "-stroke", "#D62828", "-strokewidth", str(lw),
                    "-draw", f"rectangle {x0},{y0} {x1},{y1}", str(png)], check=True)


def render(src: Path, out: Path, page: int = 1, dpi: int = 150, trim: bool | None = None,
           focus: str | None = None, box=None) -> Path:
    out = _render(src, out, page, dpi, trim, focus)
    if box:
        _spotlight(out, box)
    return out


def _render(src: Path, out: Path, page: int, dpi: int, trim, focus) -> Path:
    ext = src.suffix.lower()
    if trim is None:
        trim = ext in SHEET
    out.parent.mkdir(parents=True, exist_ok=True)
    if ext in IMG:
        shutil.copyfile(src, out if ext == ".png" else out.with_suffix(ext))
        if ext != ".png":
            subprocess.run(["convert", str(out.with_suffix(ext)), str(out)], check=True)
        _shrink(out)
        return out
    if ext == ".pdf":
        _pdf_page(src, out, page, dpi)
        if trim:
            _trim(out)
        _shrink(out)
        return out
    if ext in OFFICE:
        office = shutil.which("soffice") or shutil.which("libreoffice")
        if not office:
            raise RuntimeError("LibreOffice が無い（xlsx・docx を絵にできない）")
        with tempfile.TemporaryDirectory() as td:
            if focus:
                if ext not in {".xlsx", ".xlsm"}:
                    raise RuntimeError(f"focus（セル範囲）は xlsx・xlsm だけ。{ext} は box を使う")
                src = _mark_cells(src, focus, td)
            # 利用者の設定と混ざらないよう、毎回まっさらな設定で動かす
            subprocess.run([office, f"-env:UserInstallation=file://{td}/profile", "--headless", "--convert-to", "pdf",
                            "--outdir", str(Path(td) / "pdf"), str(src)], check=True, capture_output=True, timeout=180)
            pdf = Path(td) / "pdf" / (src.stem + ".pdf")
            if not pdf.exists():
                raise RuntimeError(f"{src.name} を PDF にできない")
            _pdf_page(pdf, out, page, dpi)
        if trim:
            _trim(out)
        _shrink(out)
        return out
    raise RuntimeError(f"{src.name}: 絵にできない種類（{ext}）")


if __name__ == "__main__":
    a = sys.argv
    if len(a) < 3:
        raise SystemExit(__doc__)
    pg = int(a[a.index("--page") + 1]) if "--page" in a else 1
    dp = int(a[a.index("--dpi") + 1]) if "--dpi" in a else 150
    tr = True if "--trim" in a else (False if "--no-trim" in a else None)
    fc = a[a.index("--focus") + 1] if "--focus" in a else None
    bx = [float(v) for v in a[a.index("--box") + 1].split(",")] if "--box" in a else None
    print(render(Path(a[1]), Path(a[2]), pg, dp, tr, fc, bx))
