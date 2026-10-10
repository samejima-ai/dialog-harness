"""spec の {{IMG:name}} を本番の切り抜きの data URI に差し替えた、公開用の spec を書く。

使い方: python inject_images.py <spec.json> <images.json> <out.json>
  images.json = {"row_a": "data:image/jpeg;base64,...", "q1_color": "..."}（scratch に置く。repo には入れない）
  name は [A-Za-z0-9_-]+（既存の spec は q1_color / q6_tsunagi_E / row_a の形）。images.json に無い名前・
  差し替えられずに残った placeholder があれば exit 1（公開版に壊れた画像を出さない）

守る線: repo に入れる spec は placeholder のまま。本番の画面・図面の切り抜きは**公開版の HTML にだけ**埋め込む
（foot に「原図は本番の切り抜き。公開版にだけ埋め込み、repo には入れない」と書く）。そのため out は
spec と同じファイルにも、この repo の中にも書けない（scratch へ）。
1 枚は長辺 900px・JPEG 品質 70 前後に落とす（Artifact tool の上限 = 16MB。1003 は 3 枚で約 200KB）。
"""
import json
import re
import sys
from pathlib import Path

if len(sys.argv) != 4:
    raise SystemExit(__doc__)
spec_path, images_path, out_path = (Path(p).resolve() for p in sys.argv[1:4])


def repo_root_of(p: Path):
    """p を含む git repo（worktree の `.git` ファイルも可）の root。無ければ None。script の置き場所は見ない（写して使っても同じ判定）。"""
    for d in (p, *p.parents):
        if (d / ".git").exists():
            return d
    return None


if out_path == spec_path:
    raise SystemExit("out は spec と同じファイルにできません（repo の spec は placeholder のまま残す）")
root = repo_root_of(spec_path)
if root is not None and (out_path == root or root in out_path.parents):
    raise SystemExit(f"out は repo の中に書けません（本番の画像を repo に入れない）: {out_path}")

with open(spec_path, encoding="utf-8") as f:
    text = f.read()
with open(images_path, encoding="utf-8") as f:
    images = json.load(f)
missing = set()
used = set()


def rep(m):
    name = m.group(1)
    if name not in images:
        missing.add(name)
        return m.group(0)
    used.add(name)
    return images[name]


text = re.sub(r"\{\{IMG:([A-Za-z0-9_-]+)\}\}", rep, text)
if missing:
    raise SystemExit(f"missing images: {sorted(missing)}")
left = re.findall(r"\{\{IMG:[^}]*\}\}", text)
if left:
    raise SystemExit(f"unresolved placeholders (name の文字が規約外): {left}")
try:
    json.loads(text)
except json.JSONDecodeError as e:
    raise SystemExit(f"差し替え後の spec が JSON として壊れています（data URI に引用符が混ざっていないか）: {e}")
unused = sorted(set(images) - used)
if unused:
    print("unused images (not referenced by spec):", unused)
with open(out_path, "w", encoding="utf-8", newline="") as f:
    f.write(text)
print("wrote", out_path, len(text) // 1024, "KB", "images:", len(used))
