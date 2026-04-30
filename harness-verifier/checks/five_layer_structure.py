"""検証 4: 5 層構造保全

`layer1-autonomous-dev/references/inferential-sensor-v2.md` 内の 5 層名定義と、
他 skill が引用する 5 層名の整合を検査する。

D4 解釈（BOUNDARY.md §6 参照）:
    DH 本体内の 5 層検出スタック記述に矛盾がないこと。
    具体的には canonical な 5 層名（glossary.yml の five_layer_stack で定義）を
    引用する全箇所が、定義と一致する表記を使っていること。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import re

from .glossary import load_glossary


# 「N 層」「Layer N」「第 N 層」等の引用パターン
LAYER_REFERENCE_RE = re.compile(r"(?:第)?[1-5１-５]\s*層|Layer\s*[1-5]|layer[_-]?[1-5]", re.IGNORECASE)


def collect_md_files(skills_dir: Path) -> list[Path]:
    return sorted(skills_dir.rglob("*.md"))


def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    repo_root = skills_dir.parent.parent

    glossary = load_glossary(glossary_path)
    five_layer = glossary.get("five_layer_stack", {})
    if not five_layer:
        issues.append({
            "location": str(glossary_path.relative_to(repo_root)),
            "message": "glossary.five_layer_stack is empty or missing",
            "severity": "FAIL",
        })
        return issues

    canonical_names: set[str] = set()
    for layer_key, layer_def in five_layer.items():
        if isinstance(layer_def, dict):
            name = layer_def.get("name", "")
            if name:
                canonical_names.add(name)
            for alias in layer_def.get("aliases", []) or []:
                canonical_names.add(alias)

    canonical_lower = {n.lower() for n in canonical_names}

    # 定義ソース存在確認
    sensor_v2 = skills_dir / "layer1-autonomous-dev" / "references" / "inferential-sensor-v2.md"
    if not sensor_v2.is_file():
        issues.append({
            "location": str(sensor_v2.relative_to(repo_root)),
            "message": "5 層スタック定義ソース inferential-sensor-v2.md が見つからない",
            "severity": "FAIL",
        })

    # canonical 名から「単語っぽい trigger 語」を抽出して検出
    # 例: "計算的センサー" / "computational-sensor" / "推論的センサー" / "E2E 機械検証" 等
    canonical_trigger_terms: set[str] = set()
    for layer_def in five_layer.values():
        if not isinstance(layer_def, dict):
            continue
        for token in [layer_def.get("name", ""), *(layer_def.get("aliases", []) or [])]:
            if not token:
                continue
            # 名前から記号・空白を除去した部分文字列を trigger として登録
            canonical_trigger_terms.add(token.lower().replace("　", "").replace(" ", ""))
            # 別名の主要構成要素も登録（例: "computational-sensor" → "computational"）
            for fragment in re.split(r"[\s\-_/]+", token.lower()):
                if len(fragment) >= 4:
                    canonical_trigger_terms.add(fragment)

    # 5 層検出スタック「らしさ」のヒント語（同行に出現すると検査対象になる）
    # これが無ければ Layer 0/1/2（DH レイヤー番号）の話と判定して検査スキップ
    five_layer_context_re = re.compile(
        r"(検出スタック|sensor|センサー|計算的|推論的|interaction\s*cost|"
        r"Shift\s*Left|機械検証|E2E|単体テスト|統合テスト)",
        re.IGNORECASE,
    )
    structured_ref_re = re.compile(
        r"(第\s*[1-5１-５]\s*層\s*[:：]|Layer\s*[1-5]\s*[:：]|layer[_-][1-5]\s*[:：])",
        re.IGNORECASE,
    )

    for md in collect_md_files(skills_dir):
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            if not structured_ref_re.search(line):
                continue
            # ★ 5 層検出スタック文脈でない場合は検査対象外（DH の Layer 0/1/2 番号は別物）
            if not five_layer_context_re.search(line):
                continue
            line_norm = line.lower().replace("　", "").replace(" ", "")
            if any(trig in line_norm for trig in canonical_trigger_terms):
                continue
            issues.append({
                "location": f"{md.relative_to(repo_root)}:{line_no}",
                "message": "5 層検出スタックへの構造化言及だが glossary.five_layer_stack の canonical 名/別名に一致しない",
                "severity": "WARN",
            })

    return issues
