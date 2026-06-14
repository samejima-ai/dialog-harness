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


# 未引用でも token 化してよい実値（頻出語と衝突しないもののみ）。
# REPO_NAME/REPO_OWNER は prompt 内に未引用で現れる（例: "あなたは dialog-harness の..."）。
# template 側は ${REPO_NAME} が token 化されるため、本体側も未引用出現を畳まないと恒常 drift になる
# （Copilot #148 #6）。VERIFIER_JOB_NAME の "verify" は頻出語のため未引用畳みは行わない（引用時のみ）。
UNQUOTED_TOKENIZE = ("REPO_NAME", "REPO_OWNER", "ALLOWED_AUTHORS")

# 本体側で「自由形式 placeholder に対応する実値」が現れる行頭マーカー。
# template 側は ${SENSITIVE_PATHS_REGEX} 等 1 行に畳まれて FREEFORM 除外されるのに対し、
# 本体側は実値が展開されて残る。これを本体側でも除外しないと host_only が恒常化する
# （Copilot #148 #4）。SCOPE_PATHS（paths: 配下リスト）は別途ブロック状態で処理（#5）。
HOST_FREEFORM_LINE_PREFIXES = (
    "SENSITIVE=",  # claude-review pre-gate の ${SENSITIVE_PATHS_REGEX} 展開先
)

# paths: ブロック配下のリスト要素マーカー。template の ${SCOPE_PATHS} に対応するため、
# 本体側の `paths:` 直後に続く `- "..."` 行は比較から除外する（Copilot #148 #5）。
PATHS_KEY_RE = re.compile(r"^\s*paths:\s*$")
LIST_ITEM_RE = re.compile(r'^\s*-\s')

# プロンプト本文（YAML ブロックスカラ）の起点マーカー。`direct_prompt: |` 等の配下は
# AI へのレビュー指示文（自然文）で、本体は DH 仕様軸の散文、template は汎用 +
# ${PROJECT_REVIEW_AXES} 等の自由形式を持つ。両者は本質的に機械同期不能なため
# ブロックごと比較除外する（#7）。prompt 軸 drift は G-001/G-002 の prompt 軸レビューで
# 別途担保するという既定方針（本ファイル冒頭 docstring）に従う。インデント深さで範囲確定。
PROMPT_BLOCK_RE = re.compile(r"^(\s*)(direct_prompt|prompt|append_system_prompt):\s*[|>][-+]?\s*$")


def normalize_line(line: str) -> str | None:
    """1 行を正規化。比較対象外なら None を返す（コンテキスト非依存な判定のみ）。

    - コメント行（# で始まる、YAML/シェル）・空行は除外（CI 方針はロジックに宿る）
    - コード行末尾のインラインコメント（` # ...`）も除去（#7）。本体は DH 固有の詳細
      コメント、template は汎用コメントを持つため、ロジックが一致しても末尾コメント差で
      drift 誤検知する。ただし文字列リテラル内の `#`（jq 式 `#%s` 等）を壊さないため、
      クォート（' / "）を含まない行に限定して保守的に除去する。
    - 自由形式 placeholder を含む行は除外（機械正規化困難・偽陽性回避）
    - 本体側の自由形式実値展開行（SENSITIVE= 等）も除外（#4）
    - DH placeholder token / 本体実値（引用 + 一部未引用）を共通 token へ畳む
    paths: ブロック配下の除外（#5）は状態を要するため normalized_lines() 側で処理。
    """
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith("#"):
        return None

    # コード行末尾のインラインコメントを除去（#7）。クォートを含まない行に限定し、
    # ` #`（スペース + ハッシュ）以降を落とす。リテラル内 `#`（'Closes #%s' 等）は
    # クォート存在で除外され安全側に倒れる。
    if "'" not in stripped and '"' not in stripped and " #" in stripped:
        stripped = stripped.split(" #", 1)[0].rstrip()
        if not stripped:
            return None
        line = stripped

    # 自由形式 placeholder を含む行（template 側）は比較から外す
    for ph in FREEFORM_PLACEHOLDERS:
        if "${" + ph + "}" in line:
            return None

    # 本体側の自由形式実値展開行（template 側は ${...} で除外済の対応行）を外す（#4）
    for prefix in HOST_FREEFORM_LINE_PREFIXES:
        if stripped.startswith(prefix):
            return None

    norm = line

    # template 側: ${VAR} を token へ
    for ph in DH_PLACEHOLDERS:
        if ph in FREEFORM_PLACEHOLDERS:
            continue
        norm = norm.replace("${" + ph + "}", WILDCARD)

    # 本体側: 引用符で囲まれた実値を token 化（VERIFIER_JOB_NAME="verify" 等）
    for ph, values in HOST_CONCRETE_VALUES.items():
        for val in values:
            norm = norm.replace(f'"{val}"', f'"{WILDCARD}"')
            norm = norm.replace(f"'{val}'", f"'{WILDCARD}'")

    # 本体側: 未引用でも安全に畳める実値（REPO_NAME 等）を token 化（#6）
    for ph in UNQUOTED_TOKENIZE:
        for val in HOST_CONCRETE_VALUES.get(ph, []):
            norm = norm.replace(val, WILDCARD)

    return norm.strip()


def normalized_lines(path: Path) -> list[str]:
    """ファイルを正規化済みロジック行のリストにする。

    paths: ブロック配下のリスト要素は ${SCOPE_PATHS} に対応するため除外する（#5）。
    `paths:` 行を検出したら、以降の連続するリスト要素（`- ...`）をスキップし、
    インデントが浅い非リスト行が来たらブロックを抜ける。

    direct_prompt/prompt 等の YAML ブロックスカラ配下（AI 指示文の自然文）は機械同期
    不能なためブロックごと除外する（#7）。`direct_prompt: |` のインデント深さを記録し、
    それより深い行（およびブロック内空行）はスキップ、同深度以下の非空行で離脱する。
    """
    out: list[str] = []
    in_paths_block = False
    prompt_indent: int | None = None  # プロンプトブロック内なら起点行のインデント幅
    for raw in path.read_text(encoding="utf-8").splitlines():
        # プロンプトブロック内の処理（最優先・インデント深さで範囲確定）
        if prompt_indent is not None:
            if not raw.strip():
                continue  # ブロック内空行はスキップ
            indent = len(raw) - len(raw.lstrip())
            if indent > prompt_indent:
                continue  # 起点より深い = プロンプト本文 → 除外
            prompt_indent = None  # 同深度以下 → ブロック終了、通常処理へフォールスルー

        m = PROMPT_BLOCK_RE.match(raw)
        if m:
            # `direct_prompt: |` 行自体は構造として残し、配下本文を除外開始
            prompt_indent = len(m.group(1))
            n = normalize_line(raw)
            if n is not None:
                out.append(n)
            continue

        if PATHS_KEY_RE.match(raw):
            # paths: 行自体は構造ヘッダとして比較に残す（キーの有無は方針差）
            in_paths_block = True
            n = normalize_line(raw)
            if n is not None:
                out.append(n)
            continue
        if in_paths_block:
            if LIST_ITEM_RE.match(raw) or not raw.strip():
                # paths 配下のリスト要素 / 空行はスキップ（SCOPE_PATHS 相当）
                continue
            in_paths_block = False  # 非リスト行 → ブロック終了、通常処理へ
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
