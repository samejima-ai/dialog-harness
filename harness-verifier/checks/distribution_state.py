"""検査: 配布物の状態（v6.18.0 C-2 で検査 8 から分離）

**欠落の型**: 実体の誤配置 — 配布先固有の状態が配布物に置かれていないか

`overwrite` 配下（skills / templates / agents）に `history/` や `*LOG*.md` が無いかを見る。
**本検査だけは宣言を読まない**（実体走査のみ）。これが「1 検査器 = 1 宣言ファイル」という
当初の分割基準が実態と合わなかった理由のひとつである。
起点は v6.17.0 F3: 「社外秘ゆえ skill 内部に閉じる」と宣言されたログが `overwrite` 分類ゆえ
配布先 2 リポへ byte 一致で配られていた（最も秘匿すべき場所が最も広く配られる場所だった）。

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
      - measured: 配布物内 state 検査の WARN が 6 cycle 連続 0 件なら降格候補
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any



def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:  # noqa: ARG001
    repo_root = skills_dir.parent.parent
    issues: list[dict[str, Any]] = []
    counts = _check_f3(repo_root, issues)
    issues.append({
        "location": ".claude/skills/",
        "message": (f"配布物の状態 — overwrite 配下 {counts['scanned']} 面を走査 / "
                    f"状態実体 {counts['state_found']} 件"),
        "severity": "METRIC",
    })
    return issues


def _check_f3(repo_root: Path, issues: list[dict[str, Any]]) -> dict[str, int]:
    """F3: 配布物に「配布先固有になりうる状態」を置かない（検査 13）。

    `overwrite:` 配下（`.claude/skills/` / `templates/` / `.claude/agents/`）に `history/`
    ディレクトリまたは `*LOG*.md` が存在したら WARN。

    これは (c) の一般形である。skill 内 COUNCIL-LOG は「社外秘ゆえ skill 内部に閉じて保管する」と
    宣言しながら、`overwrite` 分類ゆえ配布先 2 リポへ byte 一致で配られていた
    （実測 2026-09-06: kakuman 84,721 B / cc-cockpit 83,467 B）。
    **最も秘匿すべきと宣言した場所が、最も広く配られる場所だった。**

    同型の実害は SK-03 でも起きている（kakuman 固有 Council 2 件が上書きで消失）。
    「skill 内に状態を置くと上書きで消える / 意図せず配られる」を型として封じる。

    規範メタデータ:
        stage: 全段階
        review_trigger:
          - measured: 配布物内 state 検査の WARN が 6 cycle 連続 0 件なら降格候補
    """
    counts = {"scanned": 0, "state_found": 0}
    # overwrite 配下の実体（manifest を読まず固定するのは、manifest 自体が壊れていても
    # この検査は動くべきだから。分類の網羅性は検査 11 が別途見る）
    roots = [
        repo_root / ".claude" / "skills",
        repo_root / "templates",
        repo_root / ".claude" / "agents",
    ]
    for root in roots:
        if not root.is_dir():
            continue
        counts["scanned"] += 1
        rel_root = root.relative_to(repo_root).as_posix()

        for path in sorted(root.rglob("*")):
            rel = path.relative_to(repo_root).as_posix()
            if path.is_dir() and path.name == "history":
                counts["state_found"] += 1
                issues.append({
                    "location": rel + "/",
                    "message": (f"配布物（{rel_root}/）の中に history/ がある。"
                                "配布先固有の状態を配布物に置くと、上書きで消えるか意図せず配られる"
                                "（upgrade-spec-v6.17.0 §F3。skill 内 COUNCIL-LOG が実際に"
                                "配布先 2 リポへ配られていた）"),
                    "severity": "WARN",
                })
            elif path.is_file() and "LOG" in path.name and path.suffix == ".md":
                counts["state_found"] += 1
                issues.append({
                    "location": rel,
                    "message": (f"配布物（{rel_root}/）の中にログ実体 {path.name!r} がある。"
                                "ログは配布先ごとに異なる状態であり、配布物に置いてはならない"
                                "（upgrade-spec-v6.17.0 §F3）"),
                    "severity": "WARN",
                })
    return counts
