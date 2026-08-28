#!/usr/bin/env python3
"""local_verify — local 環境の編集後検証 hook（delegation-boundary §4 の実体化）。

delegation-boundary.md §4「local / github の分離 — 権限差ではなく検証手段差」を
物理的に成立させるための hook スクリプト。local で「commit まで無確認で走る」
全自律を支える検証手段（lint + 型 + 構造健全性）を、編集系 tool の直後に回す。

設計原則（philosophy.md 第 6 条 / crosscut-hook-observer と同じ哲学）:
    - **warn-only**: 検出しても exit code は常に 0。tool call を block しない。
      自動 block は人間最終承認の代替にならない（第 6 条）。検出結果は stderr に
      出して AI 自身に気付かせ、commit 前に直す機会を与えるに留める。
    - **観測層との分離**: crosscut-hook-observer は「観測専用」で検証しない。
      本スクリプトは「検証専用」で観測しない。命令層・観測層・検証層を分ける。
    - **決定論優先（第 2 条 / C-4）**: 確率的レビューではなく決定論検査を回す。
      DH 本体では harness-verifier/verify.py（構造健全性）。配布先では各自の
      lint / 型チェックに差し替える（DH_LOCAL_VERIFY_CMD で外部化）。

呼び出し（.claude/settings.json hooks の PostToolUse に追加）:
    python3 .claude/skills/crosscut-autonomous-drive/scripts/local_verify.py

stdin に Claude Code hook の event payload(JSON) を受け取る。
編集系 tool（Write / Edit / MultiEdit / NotebookEdit）以外では即 exit 0。

検証コマンドの決定（優先順）:
    1. 環境変数 DH_LOCAL_VERIFY_CMD（配布先プロジェクトが自分の lint/型に差し替え）
       例: DH_LOCAL_VERIFY_CMD="npm run -s typecheck && npm run -s lint"
    2. リポジトリに harness-verifier/verify.py があれば DH 本体とみなし、それを実行
    3. どちらも無ければ「検証手段なし」として exit 0（何もしない）

終了コード:
    常に 0（warn-only）。検証 FAIL は stderr の [local-verify] 行で通知するのみ。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# 編集系 tool のみ検証対象（読み取り系・Bash 等では回さない）
EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# verify.py 自体の暴走を防ぐ上限（秒）
VERIFY_TIMEOUT_SEC = 60


def repo_root() -> Path:
    """このスクリプトの位置から repo ルートを辿る。

    .claude/skills/crosscut-autonomous-drive/scripts/local_verify.py
    → parents[4] が repo ルート。
    """
    return Path(__file__).resolve().parents[4]


def read_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError):
        return {}


def tool_name(payload: dict) -> str:
    """hook payload から tool 名を取り出す。

    Claude Code の PostToolUse payload は tool_name キーで tool を渡す。
    キー名の差異に備え、複数候補を見る。
    """
    for key in ("tool_name", "toolName", "tool"):
        val = payload.get(key)
        if isinstance(val, str) and val:
            return val
    return ""


def warn(msg: str) -> None:
    """warn-only 通知。stderr に [local-verify] プレフィックスで出す。"""
    sys.stderr.write(f"[local-verify] {msg}\n")


def run_verify_command(cmd: str, cwd: Path) -> tuple[int, str]:
    """検証コマンドを shell で実行し (exit_code, 末尾出力) を返す。"""
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=VERIFY_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return 124, f"検証コマンドが {VERIFY_TIMEOUT_SEC}s でタイムアウト"
    except OSError as exc:
        return 2, f"検証コマンド起動失敗: {exc}"
    tail = (proc.stdout + proc.stderr).strip().splitlines()
    return proc.returncode, "\n".join(tail[-10:])


def run_harness_verify(root: Path) -> tuple[int, str]:
    """DH 本体の harness-verifier/verify.py を --json で回す。"""
    verify_py = root / "harness-verifier" / "verify.py"
    python = sys.executable or "python3"
    try:
        proc = subprocess.run(
            [python, str(verify_py), "--json"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=VERIFY_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return 124, f"verify.py が {VERIFY_TIMEOUT_SEC}s でタイムアウト"
    except OSError as exc:
        return 2, f"verify.py 起動失敗: {exc}"

    # --json 出力から FAIL 件数を抽出（壊れていても exit code で判断）
    summary = ""
    try:
        data = json.loads(proc.stdout)
        failed = [
            c.get("name", "?")
            for c in data.get("checks", [])
            if c.get("status") == "FAIL"
        ]
        if failed:
            summary = "FAIL: " + ", ".join(failed)
    except (json.JSONDecodeError, AttributeError, TypeError):
        summary = (proc.stdout + proc.stderr).strip().splitlines()[-1:]
        summary = summary[0] if summary else ""
    return proc.returncode, summary


def main() -> int:
    payload = read_payload()
    tool = tool_name(payload)

    # 編集系 tool のときだけ検証する（それ以外は素通り）。
    # tool 名が取れない（空 = payload 空/壊れ/キー名差異）場合も素通りにする:
    # 想定外 payload で毎回 verify が走るとノイズ・負荷になるため安全側に倒す（Copilot #148 指摘）。
    if tool not in EDIT_TOOLS:
        return 0

    root = repo_root()

    # 優先 1: 配布先が指定した検証コマンド
    custom = os.environ.get("DH_LOCAL_VERIFY_CMD", "").strip()
    if custom:
        code, tail = run_verify_command(custom, root)
        if code != 0:
            warn(f"検証 FAIL (exit {code}) — commit 前に確認を推奨:")
            if tail:
                warn(tail)
        return 0  # warn-only

    # 優先 2: DH 本体（harness-verifier/verify.py がある）
    if (root / "harness-verifier" / "verify.py").is_file():
        code, summary = run_harness_verify(root)
        if code != 0:
            warn(f"harness-verify FAIL (exit {code}) — 構造健全性の退行:")
            if summary:
                warn(summary)
        return 0  # warn-only

    # 優先 3: 検証手段なし → 何もしない
    return 0


if __name__ == "__main__":
    # warn-only 契約: 例外が出ても hook を壊さないため必ず 0 で抜ける
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — hook は決して落とさない
        sys.stderr.write(f"[local-verify] internal error (ignored): {exc}\n")
        sys.exit(0)
