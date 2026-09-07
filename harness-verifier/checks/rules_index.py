"""検査: 共通 RL の現況被覆（v6.18.0 C-2 で検査 8 から分離）

**欠落の型**: 実体→宣言 — 配布される RL が索引に載っているか

`templates/rules/common/*.md` の実ファイルと README §common/ の現況 の列挙が一致するかを見る。
**件数ではなくファイル名で突き合わせる**（件数一致は名前が入れ替わっても通ってしまう）。
起点は v6.17.0 F6: RL 6 本が 3 リポに byte 一致で届いているのに読込経路がどこにも無く、
しかも README が 4 本しか列挙していなかった（届くが誰も知らない）。

## 分割の経緯

Council `council-2026-09-06T15:00:00Z-splt02`（jc 0.85 / 3 軸全会一致）。
検査 8 は v6.17.0 で 6 → 13 項目に増え **672 行**に肥大した。3 軸が独立に同一のバグ
（dict 重複キーによる F4 METRIC の消失・PR #263 で是正）を発見し、
**肥大が実際に見落としを生んだ実証**となったため分割した。

分割基準は当初の申し送りにあった「1 検査器 = 1 宣言ファイル」**ではない**。
F1 は 4 ファイル、F4 は 2 ファイルを読み、F3 は宣言を読まない（実体走査のみ）ため、
宣言ファイル単位では切れないことが実測で判明した。採った基準は
**「1 検査器 = 1 つの欠落の型」**（実体→宣言 / 鮮度 / 実質 / 実体の誤配置）である。

規範メタデータ:
    stage: 全段階
    review_trigger:
      - measured: 6 cycle 連続 0 件なら、RL の増減自体が止まっている可能性を疑い配布の要否を再問
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any



def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:  # noqa: ARG001
    repo_root = skills_dir.parent.parent
    issues: list[dict[str, Any]] = []
    counts = _check_f6(repo_root, issues)
    issues.append({
        "location": "templates/rules/README.md",
        "message": (f"RL 現況被覆 — 実ファイル {counts['rl_files']} 本 / "
                    f"README 列挙 {counts['rl_listed']} 本"),
        "severity": "METRIC",
    })
    return issues


def _check_f6(repo_root: Path, issues: list[dict[str, Any]]) -> dict[str, int]:
    """F6: 共通 RL の実ファイルと README §common/ の現況 の列挙が一致するか（検査 10）。

    `templates/rules/common/` の 6 本は配布先に byte 一致で届いているが、README の現況節が
    4 本しか列挙しておらず、どれが届いているのかを宣言側から知れない状態だった
    （upgrade-spec-v6.17.0 §F6 実測）。kakuman の `check-traps-sync.mjs` が
    「常時索引 ⇄ 全文」で実装した被覆一意性検査の、DH 側 RL への転用。

    件数ではなくファイル名で突き合わせる（件数一致は名前が入れ替わっても通ってしまう）。
    """
    counts = {"rl_files": 0, "rl_listed": 0}
    common = repo_root / "templates" / "rules" / "common"
    readme = repo_root / "templates" / "rules" / "README.md"
    if not common.is_dir() or not readme.is_file():
        return counts  # 配布先など RL を持たないツリーでは skip（後方互換）

    actual = {f.name for f in common.glob("*.md")}
    counts["rl_files"] = len(actual)

    text = readme.read_text(encoding="utf-8")
    m = re.search(r"^##\s*common/ の現況\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        issues.append({
            "location": "templates/rules/README.md",
            "message": ("§common/ の現況 が見つからない。共通 RL の現況 SSOT はこの節であり、"
                        "dev-env-spec 側は本 README を参照する（upgrade-spec-v6.17.0 §F6）"),
            "severity": "FAIL",
        })
        return counts

    # 各項目の**先頭**のバッククォート名だけを RL 名とみなす。本文中の説明パス
    # （`.dh/rules/common/...` での override 例、他 skill の参照先等）を拾わないため、
    # 「- `<name>.md`」という箇条書きの見出し位置に限定する。
    listed = set(re.findall(r"^-\s+`([^`/]+\.md)`", m[1], re.M))
    counts["rl_listed"] = len(listed)

    for name in sorted(actual - listed):
        issues.append({
            "location": f"templates/rules/common/{name}",
            "message": (f"共通 RL {name!r} が README §common/ の現況 に列挙されていない。"
                        "配布はされるが宣言側から存在を知れない（F6 が塞いだ欠落の再発）"),
            "severity": "FAIL",
        })
    for name in sorted(listed - actual):
        issues.append({
            "location": "templates/rules/README.md",
            "message": (f"README §common/ の現況 が実在しない RL {name!r} を列挙している。"
                        "削除・改名に追随する"),
            "severity": "FAIL",
        })
    return counts
