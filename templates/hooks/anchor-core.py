#!/usr/bin/env python3
"""anchor-core — SessionStart hook: 不変核を stdout へ出し、文脈に再注入する。

upgrade-spec v7.0.0 Phase A F1。compaction 後に規範が静かに落ちる（違反率 0% → 30%、組織ポリシー型は
安全規範の 8.3 倍の速さで減衰、約 47 トークンの再注入で 0% へ復帰 — arXiv 2606.22528）ことへの対策。

Claude Code の hook のうち、stdout が Claude の文脈に載るのは SessionStart（matcher: startup / resume /
clear / compact）等に限られる（PreCompact は情報提供のみで注入不可・公式仕様）。よって本 hook は
SessionStart に配線し、compaction 直後にも通常起動にも同じ数行を再提示する。

## 設計制約

- **注入する内容は philosophy.md の引用のみ**。改訂は人間専管（L-FROZEN-PHIL）。本 hook は憲法を
  書き換えない — 読み上げるだけ。
- **観測層と分離する**（I-6）: `crosscut-hook-observer` は「観測専用・注入しない」を憲章に持つため、
  本 hook はそこに同居させない。
- **LLM 判定なし・失敗時は exit 0 で無出力**（degrade）。ファイル不在・読込失敗でも DH は通常動作する。
- **小さく保つ**: 不変核は 3〜4 条。膨らませば compaction 耐性の利点が消える（同時拘束数 k*=2〜4 —
  arXiv 2608.12426）。harness-verifier 検査 6 が上限（行数・文字数）を見張る。

## 配置

- DH 本体 / 利用者プロジェクト共通: `templates/hooks/anchor-core.py`（`templates/` は DH 配布物・overwrite）
- 不変核の本文: DH 本体は `.claude/anchor-core.md`、利用者プロジェクトは `.dh/anchor-core.md`。
  **両方あれば `.claude/` 側が優先**（CANDIDATES の順。利用者プロジェクトは通常 `.dh/` のみ持つ）
  （never_touch 領域 = プロジェクト所有。雛形は `templates/hooks/anchor-core.md`）
- 配線: `.claude/settings.json` の `SessionStart` に 1 command 追加（matcher なし = 全 source）

規範メタデータ: `{ stage: 全段階, review_trigger: [model_generation, measured: 再注入後も規範違反が観測される] }`
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

CANDIDATES = (".claude/anchor-core.md", ".dh/anchor-core.md")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def load_anchor(root: Path) -> str:
    """最初に見つかった anchor-core.md を返す。無ければ空文字。HTML コメント（規範メタデータ）は除く。"""
    for rel in CANDIDATES:
        p = root / rel
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue  # 読取失敗は degrade として次候補を試す（Copilot review #288）
        return COMMENT_RE.sub("", text).strip()
    return ""


def main() -> int:
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    text = load_anchor(root)
    if text:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
