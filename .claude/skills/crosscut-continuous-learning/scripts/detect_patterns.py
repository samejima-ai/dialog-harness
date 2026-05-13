#!/usr/bin/env python3
"""crosscut-continuous-learning: pattern 検出 + 候補出力（Wave 2 walking skeleton）

入力: harness-verifier/reports/hook-observations.jsonl
出力: delivery/CONTINUOUS-LEARNING-CANDIDATES-<timestamp>.md

設計（PR #78、Council 諮問 w2qb01 採決 B 反映）:
    - 候補出力のみ、自動 promote なし
    - CTL 0 では実行抑止（呼出側で判定、本スクリプトは CTL を確認しない素直な実装）
    - 観測ログは読み取り専用、書き換えなし（独立性原則）
    - 出力ファイルは append-only ではなく **timestamped 別ファイル**（人間レビュー単位）

使用例:
    python3 .claude/skills/crosscut-continuous-learning/scripts/detect_patterns.py

呼出側責務:
    - CTL 0 では本スクリプトを呼び出さないこと（SKILL.md §「CTL 連動」参照）
    - 出力ファイルを人間レビュー前提で扱うこと（自動採用は禁止）
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


MIN_OCCURRENCE = 3  # この件数以上繰返したパターンのみ候補化


def repo_root() -> Path:
    """Walk up from this script's parent directory looking for repo markers.

    The previous implementation started from ``Path(__file__).resolve()`` (a file
    path), wasting the first iteration on a check against the script file
    itself, and fell back to ``parents[4]`` — a fragile assumption only valid
    for the standard ``.claude/skills/<skill>/scripts/`` layout. Non-standard
    installs (user-scope ``~/.claude/skills/...`` etc.) silently dropped output
    into an unrelated ancestor directory.

    Now starts from the script's parent directory and falls back to
    ``Path.cwd()`` so output lands somewhere discoverable rather than in an
    unrelated tree. Aligned with the broader "warn-only" stance of the
    observation layer (philosophy 第 6 条).
    """
    p = Path(__file__).resolve().parent
    for _ in range(8):
        if (p / ".git").exists() or (
            (p / "harness-verifier").is_dir() and (p / ".claude" / "skills").is_dir()
        ):
            return p
        if p.parent == p:
            break
        p = p.parent
    return Path.cwd()


def load_observations(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.is_file():
        return []
    entries: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def detect_patterns(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """tool + 最初の引数 token の繰返しを検出する素朴な実装。

    将来 Wave 3 で再諮問されれば、より精緻な pattern 検出（NLP / 系列分析）に
    置き換える。Wave 2 walking skeleton ではあくまで「経路が機能する」ことを示す。
    """
    tool_signatures: Counter[tuple[str, str]] = Counter()
    sessions: dict[tuple[str, str], set[str]] = {}

    for entry in entries:
        if entry.get("event") != "PreToolUse":
            continue
        tool = entry.get("tool") or "<unknown>"
        fields = entry.get("fields") or {}
        signature_token = ""
        for key in ("command", "file_path", "params"):
            value = fields.get(key)
            if isinstance(value, str) and value:
                signature_token = value.split()[0][:64] if " " in value else value[:64]
                break
        key = (str(tool), signature_token)
        tool_signatures[key] += 1
        sessions.setdefault(key, set()).add(str(entry.get("session_id") or ""))

    patterns: list[dict[str, Any]] = []
    for (tool, token), count in tool_signatures.most_common(50):
        if count < MIN_OCCURRENCE:
            continue
        patterns.append(
            {
                "tool": tool,
                "token": token,
                "occurrence": count,
                "session_count": len(sessions.get((tool, token), set())),
            }
        )
    return patterns


def render_report(
    entries: list[dict[str, Any]], patterns: list[dict[str, Any]]
) -> str:
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    lines: list[str] = []
    lines.append(f"# Continuous Learning 候補 — {now}")
    lines.append("")
    lines.append("**重要**: 本ファイルは人間レビュー前提の候補リスト。")
    lines.append("自動採用は禁止（Council 諮問 w2qb01 採決 B 反映）。")
    lines.append("")
    lines.append("## 観測対象")
    lines.append("")
    lines.append("- 観測ログ: `harness-verifier/reports/hook-observations.jsonl`")
    if entries:
        first_ts = entries[0].get("ts", "<unknown>")
        last_ts = entries[-1].get("ts", "<unknown>")
        lines.append(f"- 観測期間: {first_ts} 〜 {last_ts}")
    else:
        lines.append("- 観測期間: 観測ログ不在（hook 未起動状態、PASS）")
    lines.append(f"- 観測件数: {len(entries)} entries")
    lines.append("")
    lines.append("## 検出パターン")
    lines.append("")
    if not patterns:
        lines.append("検出件数 0（観測データ不足、または閾値 MIN_OCCURRENCE 未満）")
        lines.append("")
    else:
        for idx, pat in enumerate(patterns, start=1):
            lines.append(f"### Pattern {idx}: `{pat['tool']}` + `{pat['token']}` 繰返")
            lines.append("")
            lines.append(f"- 出現回数: {pat['occurrence']}")
            lines.append(f"- 出現セッション: {pat['session_count']}")
            lines.append("- 候補化提案: ☐ skill / ☐ instinct / ☐ SPEC 反映 / ☐ 棄却")
            lines.append(
                "- 哲学整合性メモ: "
                "<第 6 条「人間最終承認」/ 第 7 条 P4 介入権 / 第 8 条候補との整合を記載>"
            )
            lines.append("")
    lines.append("## 人間レビュー欄")
    lines.append("")
    lines.append("- レビュー日: ")
    lines.append("- レビュー者: ")
    lines.append("- 採用候補: ")
    lines.append("- 棄却候補: ")
    lines.append("- 別 PR 化対象: ")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "crosscut-continuous-learning: hook 観測ログから instinct promotion "
            "候補を抽出（候補出力のみ、自動 promote なし）"
        )
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="観測ログ JSONL のパス（未指定時はリポジトリ既定位置）",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="出力 Markdown ファイルのパス（未指定時は delivery/ 配下）",
    )
    args = parser.parse_args(argv)

    root = repo_root()
    log_path = args.log or root / "harness-verifier" / "reports" / "hook-observations.jsonl"
    out_path = args.out or root / "delivery" / (
        "CONTINUOUS-LEARNING-CANDIDATES-"
        + time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
        + ".md"
    )

    entries = load_observations(log_path)
    patterns = detect_patterns(entries)
    report = render_report(entries, patterns)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    try:
        display = out_path.relative_to(root)
    except ValueError:
        display = out_path
    print(f"wrote {display}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
