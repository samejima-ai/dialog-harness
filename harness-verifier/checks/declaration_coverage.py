"""検査 8: 宣言被覆（v6.17.0）

既存 7 検査は「宣言 → 実体」（宣言したものが在るか）だけを見ており、
以下 3 種の欠落が構造的に検出できなかった（upgrade-spec v6.17.0 §0）:

    - 実体 → 宣言: 在るものが宣言されているか
    - 宣言の鮮度: 宣言が現在の実体に追いついているか
    - 宣言の実質: 宣言が指す source が実際にその内容を持つか

本モジュールはその受け皿である。**F1（版整合）分のみ実装済み**で、
F2 / F4 / F6 分は後続 PR で本モジュールに追加する（器を先に置く）。

F1（版整合）の検査項目:
    1. VERSION == GRAPH.yml の version:（不一致 = FAIL）
    2. upgrade-spec の状態行が値域内（値域外 = FAIL）
    3. VERSION より大きい版の spec は状態行を持つ（欠落 = FAIL）
       ※ VERSION 以下の歴史的 spec には遡及適用しない（I-4: 常時発火する検知を作らない）
    4. `実装済み` を名乗る spec の版 <= VERSION（超過 = FAIL）
    5. 状態行が `L0 起草` のまま本文が実装を名乗る（= WARN。file-local 判定）
    6. dev-env-spec.md §バージョン履歴 の凍結（マーカー欠落 / v4.2 超の追記 = FAIL）

検査 5 を `git log --grep` にしない理由（Council vrsn01 / 開発者軸の指摘を実測で確認）:
    grep 方式は v6.13.0 に 4 件 / v6.14.0 に 2 件 / v6.16.0 に 2 件を返すが、
    その大半は **当該 spec 自身の起草 commit** と個人名の一括匿名化 sweep である。
    導入初日から非ゼロで、全 draft が実装されるまで 0 にならない
    = 不変条件 I-4「常時発火する検知を作らない」に違反する。
    file-local 判定は真陽性のみに発火し、かつ git 履歴に依存しないので配布先でも同じ判定ができる。

規範メタデータ:
    stage: 全段階
    review_trigger:
      - measured: 検査 5（WARN）が初期是正後 1 cycle で 0 件に落ちなければ、
        誤検知率を再測定し、落ちないなら本検査を削る（Council vrsn01 mitigation 9）
      - measured: 版整合 FAIL が 6 cycle 連続 0 件なら、状態行の値域固定のみ残して簡素化を検討
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# 状態行の値域（dev-env-spec.md §状態行の値域 が正本。ここは機械表現）
STATE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("draft", r"^L0 起草（人間レビュー待ち）$"),
    ("council", r"^Council 諮問通過・人間の採否判定待ち$"),
    ("in_progress", r"^実装中（.+?）$"),
    ("done", r"^実装済み（PR #[\d\s/#]+、VERSION \d+\.\d+\.\d+）$"),
    ("dropped", r"^破棄（.+?）$"),
)

STATE_LINE_RE = re.compile(r"^>\s*\*\*状態:\s*(.+?)\*\*", re.M)
SPEC_NAME_RE = re.compile(r"^upgrade-spec-v(\d+)\.(\d+)\.(\d+)\.md$")
# 本文が実装を名乗る行（検査 5 の file-local 判定）
IMPL_CLAIM_RE = re.compile(r"実装済み（PR[\s#-]|実装（PR[\s#-]", re.M)
HISTORY_FREEZE_MARKER = "凍結マーカー"
HISTORY_ITEM_RE = re.compile(r"^- v(\d+)\.(\d+):", re.M)


def _ver(text: str) -> tuple[int, int, int] | None:
    m = re.match(r"^\s*(\d+)\.(\d+)\.(\d+)\s*$", text)
    return (int(m[1]), int(m[2]), int(m[3])) if m else None


def _classify(state: str) -> str | None:
    for name, pat in STATE_PATTERNS:
        if re.match(pat, state.strip()):
            return name
    return None


def run(*, skills_dir: Path, glossary_path: Path) -> list[dict[str, Any]]:
    repo_root = skills_dir.parent.parent
    issues: list[dict[str, Any]] = []

    # --- 1. VERSION == GRAPH.yml version ---
    version_path = repo_root / "VERSION"
    graph_path = repo_root / "GRAPH.yml"
    version_txt = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else ""
    version = _ver(version_txt)
    if version is None:
        issues.append({
            "location": "VERSION",
            "message": f"VERSION が semver として読めない: {version_txt!r}",
            "severity": "FAIL",
        })
        return issues  # 以降の比較基準が立たないので打ち切る

    if graph_path.is_file():
        gm = re.search(r'^version:\s*"?(\d+\.\d+\.\d+)"?', graph_path.read_text(encoding="utf-8"), re.M)
        if not gm:
            issues.append({
                "location": "GRAPH.yml",
                "message": "GRAPH.yml に version: 宣言が無い",
                "severity": "FAIL",
            })
        elif gm[1] != version_txt:
            issues.append({
                "location": "GRAPH.yml",
                "message": (f"GRAPH.yml version={gm[1]} が VERSION={version_txt} と不一致。"
                            f"昇格は同一 commit で両方更新する（dev-env-spec §昇格の実行）"),
                "severity": "FAIL",
            })

    # --- 2-5. upgrade-spec の状態行 ---
    spec_dir = repo_root / "dh-upgrades"
    for path in sorted(spec_dir.glob("upgrade-spec-v*.md")) if spec_dir.is_dir() else []:
        nm = SPEC_NAME_RE.match(path.name)
        if not nm:
            continue
        spec_ver = (int(nm[1]), int(nm[2]), int(nm[3]))
        rel = f"dh-upgrades/{path.name}"
        text = path.read_text(encoding="utf-8")
        sm = STATE_LINE_RE.search(text)

        if not sm:
            # 3. VERSION より大きい版だけ状態行を必須にする（歴史的 spec に遡及しない）
            if spec_ver > version:
                issues.append({
                    "location": rel,
                    "message": ("未 release の spec（版 > VERSION）に状態行が無い。"
                                "`> **状態: ...**` を置く（dev-env-spec §状態行の値域）"),
                    "severity": "FAIL",
                })
            continue

        state = sm[1].strip()
        kind = _classify(state)
        if kind is None:
            issues.append({
                "location": rel,
                "message": f"状態行が値域外: {state!r}（dev-env-spec §状態行の値域 の 5 値のみ）",
                "severity": "FAIL",
            })
            continue

        # 4. 実装済みを名乗る版 <= VERSION
        if kind == "done" and spec_ver > version:
            issues.append({
                "location": rel,
                "message": (f"`実装済み` を名乗る spec の版 v{nm[1]}.{nm[2]}.{nm[3]} が "
                            f"VERSION={version_txt} を超えている"),
                "severity": "FAIL",
            })

        # 5. L0 起草のまま本文が実装を名乗る（file-local 判定）
        if kind == "draft" and IMPL_CLAIM_RE.search(text):
            issues.append({
                "location": rel,
                "message": ("状態行が `L0 起草` のまま本文が実装を名乗っている。"
                            "状態行を実態に合わせる（実装中 / 実装済み）"),
                "severity": "WARN",
            })

    # --- 6. dev-env-spec §バージョン履歴 の凍結 ---
    dev_env = skills_dir / "layer0-spec-architect" / "references" / "dev-env-spec.md"
    if dev_env.is_file():
        text = dev_env.read_text(encoding="utf-8")
        m = re.search(r"^###\s*バージョン履歴.*?$(.*?)(?=^###\s|\Z)", text, re.M | re.S)
        if m:
            body = m[1]
            if HISTORY_FREEZE_MARKER not in body:
                issues.append({
                    "location": "dev-env-spec.md §バージョン履歴",
                    "message": ("凍結マーカーが無い。v5 系以降の正本は dh-upgrades/ と history/CHANGELOG.md であり、"
                                "ここに再掲すると実体の二重定義になる"),
                    "severity": "FAIL",
                })
            late = [f"v{a}.{b}" for a, b in HISTORY_ITEM_RE.findall(body) if (int(a), int(b)) > (4, 2)]
            if late:
                issues.append({
                    "location": "dev-env-spec.md §バージョン履歴",
                    "message": (f"凍結後に v4.2 より後の項目が追記されている: {', '.join(late)}。"
                                f"版ごとの内容は dh-upgrades/ が正本"),
                    "severity": "FAIL",
                })

    issues.append({
        "location": "VERSION",
        "message": (f"F1 版整合 — VERSION={version_txt} / "
                    f"upgrade-spec {len(list(spec_dir.glob('upgrade-spec-v*.md'))) if spec_dir.is_dir() else 0} 本を検査。"
                    f"F2 / F4 / F6 分は後続 PR で本モジュールに追加予定"),
        "severity": "METRIC",
    })
    return issues
