#!/usr/bin/env python3
"""check_template_sync — 本体 workflow と配布 template の二真実源 drift 検証（G-003 解消）。

known-gaps.md G-003「DH 本体 workflow/agents と template/配備物の同期保証が CI にない
（二真実源 drift）」に対する決定論的な検知機構。

delegation-boundary.md §6 の CI スリム化方針（どの検査をどこに帰属させるか）が
本体 `.github/workflows/` と配布 `templates/github-workflows/*.template` で食い違わない
ことを保証する。本体を改修して template への伝播を忘れた（またはその逆）を検知する。

設計方針:
    - **完全一致は求めない**。本体は DH 固有の実値・詳細コメントを持ち、template は
      placeholder と汎用コメントを持つため行単位の完全一致は非現実的。
    - 代わりに **正規化後の実質差分**を測る:
        1. template の DH placeholder を「ワイルドカード token」へ正規化
        2. 本体の対応実値も同じ token へ正規化
        3. コメント行・空行を除去（CI 方針はコメントではなくステップ構造に宿る）
        4. 残った「実質ロジック行」集合を比較し、片側のみに在る行を drift として報告
    - **意図的な非対称を許容**: 本体のみ(harness-verify.yml 等 DH 固有・非配布)、
      template のみ(issue-quality-gate.yml.template) はペアにしないだけでエラーにしない。
    - drift があれば exit 1、無ければ exit 0（CI / local hook どちらからも使える）。

placeholder 正規化の真実源:
    .claude/skills/crosscut-autonomous-drive/references/placeholder-spec.md の一覧表。
    GitHub Actions 式 `${{ ... }}` や shell 変数 `${LINES}` 等は placeholder ではない
    （同 spec line 60）。本スクリプトは下記 DH_PLACEHOLDERS のみを正規化対象とする。

実行:
    python scripts/check_template_sync.py [--json] [--verbose]

終了コード:
    0: drift なし（ペア化された全ファイルが正規化後一致）
    1: drift あり（片側のみに実質ロジック行が存在）
    2: 検証機構自体のエラー（ファイル不在等）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# placeholder-spec.md の一覧表に載る DH placeholder（正規化対象）。
# ${{ ... }}（Actions 式）や ${LINES} 等の shell 変数は対象外（spec line 60）。
DH_PLACEHOLDERS = (
    "ALLOWED_AUTHORS",
    "REPO_OWNER",
    "REPO_NAME",
    "VERIFIER_JOB_NAME",
    "SCOPE_PATHS",
    "PROJECT_REVIEW_AXES",
    "SENSITIVE_PATHS_REGEX",
)

# 本体側でこれら placeholder に対応する「実値」。本体は dialog-harness 自身なので確定値を持つ。
# 正規化では本体実値 → 共通 token に畳む（template 側 ${VAR} も同 token へ畳む）。
HOST_CONCRETE_VALUES = {
    "ALLOWED_AUTHORS": ["samejima-ai"],
    "REPO_OWNER": ["samejima-ai"],
    "REPO_NAME": ["dialog-harness"],
    "VERIFIER_JOB_NAME": ["verify"],
    # SCOPE_PATHS / PROJECT_REVIEW_AXES / SENSITIVE_PATHS_REGEX は複数行・自由形式で
    # 実値の機械正規化が困難。これらを含む行は「placeholder 由来行」として比較から除外する
    # （drift 判定の偽陽性を避ける。これらの drift は別途 prompt 軸レビューで担保: G-001/G-002）。
}

# 正規化後の共通 token
WILDCARD = "<<DH_PLACEHOLDER>>"

# 複数行・自由形式 placeholder（行ごと比較除外）
FREEFORM_PLACEHOLDERS = ("SCOPE_PATHS", "PROJECT_REVIEW_AXES", "SENSITIVE_PATHS_REGEX")

# 本体 ↔ template のペア定義。意図的非対称（DH 固有 / template 固有）はここに載せない。
# (本体ファイル名, template ファイル名)
WORKFLOW_PAIRS = [
    ("auto-merge.yml", "auto-merge.yml.template"),
    ("claude-review.yml", "claude-review.yml.template"),
    ("gemini-review.yml", "gemini-review.yml.template"),
    ("issue-pickup.yml", "issue-pickup.yml.template"),
]

# ペア化しない（意図的非対称）— 記録のみ、drift 判定対象外
HOST_ONLY = ["harness-verify.yml"]  # DH 生命線・非配布（harness-verify.yml line 5-6）
TEMPLATE_ONLY = ["issue-quality-gate.yml.template"]  # 配布専用・本体に常設不要


def repo_root() -> Path:
    """scripts/check_template_sync.py → parents[1] が repo ルート。"""
    return Path(__file__).resolve().parents[1]


def normalize_line(line: str) -> str | None:
    """1 行を正規化。比較対象外なら None を返す。

    - コメント行（# で始まる、YAML/シェル）・空行は除外（CI 方針はロジックに宿る）
    - 自由形式 placeholder を含む行は除外（機械正規化困難・偽陽性回避）
    - DH placeholder token / 本体実値を共通 token へ畳む
    """
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith("#"):
        return None

    # 自由形式 placeholder を含む行（template 側）は比較から外す
    for ph in FREEFORM_PLACEHOLDERS:
        if "${" + ph + "}" in line:
            return None

    norm = line

    # template 側: ${VAR} を token へ
    for ph in DH_PLACEHOLDERS:
        if ph in FREEFORM_PLACEHOLDERS:
            continue
        norm = norm.replace("${" + ph + "}", WILDCARD)

    # 本体側: 実値を token へ（VERIFIER_JOB_NAME="verify" 等、"verify" は頻出語なので
    # 値が引用符/特定キー文脈にある場合のみ畳む簡易規則）
    for ph, values in HOST_CONCRETE_VALUES.items():
        for val in values:
            # 引用符で囲まれた実値（"samejima-ai" 等）を token 化
            norm = norm.replace(f'"{val}"', f'"{WILDCARD}"')
            norm = norm.replace(f"'{val}'", f"'{WILDCARD}'")

    return norm.strip()


def normalized_lines(path: Path) -> list[str]:
    """ファイルを正規化済みロジック行のリストにする。"""
    out: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        n = normalize_line(raw)
        if n is not None:
            out.append(n)
    return out


def diff_pair(host_lines: list[str], tmpl_lines: list[str]) -> dict:
    """正規化後の集合差分。順序非依存（行の出現有無で drift を測る）。

    マルチセット差分: 本体のみ / template のみに在る行を返す。
    完全同期なら双方空。
    """
    from collections import Counter

    host_c = Counter(host_lines)
    tmpl_c = Counter(tmpl_lines)

    host_only = list((host_c - tmpl_c).elements())
    tmpl_only = list((tmpl_c - host_c).elements())
    return {
        "host_only": sorted(host_only),
        "template_only": sorted(tmpl_only),
        "in_sync": not host_only and not tmpl_only,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="本体 workflow と配布 template の二真実源 drift 検証（G-003）"
    )
    parser.add_argument("--json", action="store_true", help="JSON で stdout に出力")
    parser.add_argument(
        "--verbose", action="store_true", help="drift 行の中身を全て表示"
    )
    args = parser.parse_args(argv)

    root = repo_root()
    host_dir = root / ".github" / "workflows"
    tmpl_dir = root / "templates" / "github-workflows"

    if not host_dir.is_dir() or not tmpl_dir.is_dir():
        sys.stderr.write(
            f"[template-sync] ディレクトリ不在: {host_dir} / {tmpl_dir}\n"
        )
        return 2

    results = []
    has_drift = False

    for host_name, tmpl_name in WORKFLOW_PAIRS:
        host_path = host_dir / host_name
        tmpl_path = tmpl_dir / tmpl_name
        if not host_path.is_file() or not tmpl_path.is_file():
            results.append(
                {
                    "pair": f"{host_name} ↔ {tmpl_name}",
                    "status": "MISSING",
                    "detail": f"host={host_path.is_file()} tmpl={tmpl_path.is_file()}",
                }
            )
            has_drift = True
            continue

        d = diff_pair(normalized_lines(host_path), normalized_lines(tmpl_path))
        status = "IN_SYNC" if d["in_sync"] else "DRIFT"
        if not d["in_sync"]:
            has_drift = True
        results.append(
            {
                "pair": f"{host_name} ↔ {tmpl_name}",
                "status": status,
                "host_only_count": len(d["host_only"]),
                "template_only_count": len(d["template_only"]),
                "host_only": d["host_only"],
                "template_only": d["template_only"],
            }
        )

    report = {
        "overall": "DRIFT" if has_drift else "IN_SYNC",
        "pairs": results,
        "host_only_files": HOST_ONLY,
        "template_only_files": TEMPLATE_ONLY,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"=== template sync 検証（G-003） — overall: {report['overall']} ===")
        for r in results:
            line = f"  [{r['status']}] {r['pair']}"
            if r["status"] == "DRIFT":
                line += (
                    f"  (本体のみ {r['host_only_count']} 行 / "
                    f"template のみ {r['template_only_count']} 行)"
                )
            print(line)
            if args.verbose and r.get("status") == "DRIFT":
                for hl in r["host_only"]:
                    print(f"      - 本体のみ: {hl}")
                for tl in r["template_only"]:
                    print(f"      + tmpl のみ: {tl}")
        print(f"  意図的非対称（drift 対象外）:")
        print(f"    本体のみ: {', '.join(HOST_ONLY)}")
        print(f"    tmpl のみ: {', '.join(TEMPLATE_ONLY)}")
        if has_drift:
            print(
                "\n  → DRIFT 検出。本体と template の CI 方針が乖離。"
                "--verbose で差分行を確認し、片側の変更を他方へ同期すること。"
            )

    return 1 if has_drift else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[template-sync] internal error: {exc}\n")
        sys.exit(2)
