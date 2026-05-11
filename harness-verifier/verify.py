"""harness-verifier — D4 検査機構メインスクリプト

DH 本体（D4: メタスキル層）の内部整合性を 5 項目で検査する。
Python 標準ライブラリのみで動作（外部依存ゼロ、独立性要請の担保）。

実行:
    python harness-verifier/verify.py [--report PATH] [--strict]

終了コード:
    0: 全 PASS
    1: 1 件以上の FAIL
    2: 検査機構自体のエラー（usage error / file system error 等）

設計原則:
    - 本機構は DH 本体（D4）に一切依存しない（独立性要請）
    - 検出のみ行い、自動修正・自動 Issue 作成は行わない（D5 領域）
    - 出力は人間可読 Markdown + 機械可読 exit code
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path
from typing import Any

# 検査モジュール群
from checks import (
    dependency_graph,
    five_layer_structure,
    frontmatter,
    glossary as glossary_check,
    hook_observations,
    references,
)


CHECK_REGISTRY: list[tuple[str, Any]] = [
    ("frontmatter 整合性", frontmatter),
    ("参照 path 有効性", references),
    ("SK 間参照の健全性", dependency_graph),
    ("5 層構造保全", five_layer_structure),
    ("用語辞書整合", glossary_check),
    ("hook 観測一貫性", hook_observations),
]


def find_repo_root(start: Path) -> Path:
    """harness-verifier/ の親ディレクトリ = リポジトリルートを特定する"""
    current = start.resolve()
    for parent in [current, *current.parents]:
        if (parent / ".claude" / "skills").is_dir() and (parent / "harness-verifier").is_dir():
            return parent
    raise RuntimeError(
        "repository root not found (looking for sibling .claude/skills + harness-verifier)"
    )


def render_report(results: list[dict[str, Any]], commit_sha: str | None) -> str:
    """月次レポート形式の Markdown を組み立てる"""
    now = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    overall = "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL"

    lines: list[str] = []
    lines.append(f"# harness-verifier report {now[:7]}")
    lines.append("")
    lines.append(f"- 実行日時: {now}")
    lines.append(f"- 実行コミット: {commit_sha or 'unknown'}")
    lines.append("- AI 能力バージョン: claude-opus-4-7（参考、本機構自身は LLM 非使用）")
    lines.append(f"- 総合判定: {overall}")
    lines.append("")
    lines.append("## 検査項目別結果")
    lines.append("")

    for idx, result in enumerate(results, start=1):
        lines.append(f"### {idx}. {result['name']}")
        lines.append("")
        lines.append(f"- 結果: {result['status']}")
        lines.append(f"- 検出件数: {len(result['issues'])}")
        if result["issues"]:
            lines.append("- 詳細:")
            for issue in result["issues"]:
                location = issue.get("location", "<unknown>")
                message = issue.get("message", "")
                lines.append(f"  - `{location}`: {message}")
        lines.append("")

    lines.append("## D5 判定欄（人間記入）")
    lines.append("")
    lines.append("- 判定日: ")
    lines.append("- 判定者: ")
    lines.append("- 判断:")
    lines.append("- 補足: ")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="harness-verifier: DH D4 internal consistency checker"
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="月次レポート出力パス（指定時のみファイル書き込み）",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="WARN を FAIL として扱う（CI 厳格モード）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 形式で stdout に出力（機械処理用）",
    )
    parser.add_argument(
        "--commit-sha",
        type=str,
        default=None,
        help="レポートに記録する commit SHA",
    )
    args = parser.parse_args(argv)

    repo_root = find_repo_root(Path(__file__).parent)
    skills_dir = repo_root / ".claude" / "skills"
    glossary_path = repo_root / "harness-verifier" / "glossary.yml"

    if not skills_dir.is_dir():
        print(f"ERROR: skills directory not found: {skills_dir}", file=sys.stderr)
        return 2
    if not glossary_path.is_file():
        print(f"ERROR: glossary not found: {glossary_path}", file=sys.stderr)
        return 2

    results: list[dict[str, Any]] = []
    has_internal_error = False
    for name, module in CHECK_REGISTRY:
        try:
            issues = module.run(skills_dir=skills_dir, glossary_path=glossary_path)
        except Exception as exc:  # noqa: BLE001 — 個別 check の障害を全体停止につなげない
            issues = [
                {
                    "location": module.__name__,
                    "message": f"check raised exception: {type(exc).__name__}: {exc}",
                    "severity": "ERROR",
                }
            ]
        status = "PASS"
        for issue in issues:
            sev = issue.get("severity", "FAIL")
            if sev == "ERROR":
                has_internal_error = True
                status = "FAIL"
                break
            if sev == "FAIL":
                status = "FAIL"
                break
            if sev == "WARN" and args.strict:
                status = "FAIL"
                break
        results.append({"name": name, "status": status, "issues": issues})

    overall_pass = all(r["status"] == "PASS" for r in results)

    if args.json:
        print(json.dumps({"overall": "PASS" if overall_pass else "FAIL", "results": results}, ensure_ascii=False, indent=2))
    else:
        rendered = render_report(results, args.commit_sha)
        print(rendered)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(results, args.commit_sha), encoding="utf-8")

    if has_internal_error:
        return 2
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
