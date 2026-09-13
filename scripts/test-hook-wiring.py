#!/usr/bin/env python3
"""hook 配線の回帰テスト（オフライン・Claude Code 不要）。

v6.15.x 配線修理の 3 保証を検査する:
  1. 登録: hooks が settings 系（.claude/settings.json）にあり、厳密スキーマ形
     （非スキーマキーは全 hook を無言で無効化する実例があるため、既知キーのみ許す）
  2. 実在: settings が参照するスクリプトが存在し、bootstrap の SUPPORTED_EVENTS と
     settings のイベント集合が一致する（宣言と配線の同期）
  3. 内容フリー: 機微フィールド（応答本文・tool 入出力等）が観測 JSONL に漏れない
     （allowlist を実 payload で end-to-end 検証。書いた行は検証後に除去）
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / ".claude" / "settings.json"
BOOTSTRAP = ROOT / ".claude" / "skills" / "crosscut-hook-observer" / "scripts" / "bootstrap.py"
OBSERVE = ROOT / ".claude" / "skills" / "crosscut-hook-observer" / "scripts" / "observe.py"

FAIL = 0


def check(name, cond, detail=""):
    global FAIL
    if cond:
        print(f"  ok: {name}")
    else:
        FAIL += 1
        print(f"FAIL: {name} {detail}", file=sys.stderr)


print("== 1. 登録（settings 構造） ==")
check("settings.json が存在（hooks.json では読まれない・公式仕様）", SETTINGS.exists())
data = json.loads(SETTINGS.read_text(encoding="utf-8"))
check("トップレベルは既知キーのみ（非スキーマキーは全 hook を殺す）",
      set(data.keys()) <= {"$schema", "hooks", "permissions", "env", "model",
                           "disableAllHooks", "cleanupPeriodDays"},
      str(set(data.keys())))
hooks = data.get("hooks", {})
check("hooks キーが存在", bool(hooks))
for ev, arr in hooks.items():
    for m in arr:
        check(f"{ev}: エントリ構造（hooks 配列）", isinstance(m.get("hooks"), list))
        for h in m["hooks"]:
            check(f"{ev}: type=command", h.get("type") == "command")
            check(f"{ev}: python3||python fallback（Windows 対応）",
                  "python3" in h["command"] and "|| python " in h["command"],
                  h["command"][:60])
            check(f"{ev}: $CLAUDE_PROJECT_DIR 使用（cwd 非依存・公式推奨）",
                  "$CLAUDE_PROJECT_DIR" in h["command"])

print("== 2. 実在と同期 ==")
check("bootstrap.py 実在", BOOTSTRAP.exists())
check("observe.py 実在", OBSERVE.exists())
src = BOOTSTRAP.read_text(encoding="utf-8")
m = re.search(r"SUPPORTED_EVENTS\s*=\s*\{([^}]*)\}", src)
supported = set(re.findall(r'"(\w+)"', m.group(1))) if m else set()
observer_events = {ev for ev, arr in hooks.items()
                   if any("hook-observer" in h["command"] for mm in arr for h in mm["hooks"])}
check("settings のイベント集合 == bootstrap.SUPPORTED_EVENTS（宣言と配線の同期）",
      observer_events == supported, f"settings={observer_events} bootstrap={supported}")
check("local_verify.py の既存配線を失っていない（delegation-boundary §4）",
      any("local_verify.py" in h["command"]
          for mm in hooks.get("PostToolUse", []) for h in mm["hooks"]))

print("== 3. 内容フリー（allowlist end-to-end） ==")
obs_src = OBSERVE.read_text(encoding="utf-8")
check("ALLOWED_FIELDS が定義されている", "ALLOWED_FIELDS" in obs_src)
for banned in ("last_assistant_message", "tool_input", "tool_response",
               "transcript_path", "cwd", "custom_instructions", "compact_summary"):
    check(f"許可リストに {banned} が無い",
          not re.search(rf'"\s*{banned}\s*"', obs_src.split("ALLOWED_FIELDS")[1].split("}")[0]))

# end-to-end: 機微 payload を流し、観測先を一時ディレクトリに隔離して検証
with tempfile.TemporaryDirectory() as td:
    # observe.py は repo マーカーを遡って書くため、隔離 repo を偽装する
    fake = Path(td)
    (fake / ".git").mkdir()
    (fake / "hv" / "s").mkdir(parents=True)
    import shutil
    shutil.copy(OBSERVE, fake / "hv" / "s" / "observe.py")
    shutil.copy(BOOTSTRAP, fake / "hv" / "s" / "bootstrap.py")
    payload = {
        "session_id": "t-e2e", "tool_name": "Bash",
        "tool_input": {"command": "SECRET_CMD_MARKER"},
        "tool_response": "SECRET_OUT_MARKER",
        "last_assistant_message": "SECRET_MSG_MARKER",
        "transcript_path": "/home/SECRET_PATH_MARKER",
        "duration_ms": 42, "stop_hook_active": False,
    }
    r = subprocess.run([sys.executable, str(fake / "hv" / "s" / "bootstrap.py"), "PostToolUse"],
                       input=json.dumps(payload), text=True, capture_output=True)
    check("bootstrap exit 0（観測専用の不変条件）", r.returncode == 0, r.stderr[:120])
    out = fake / "harness-verifier" / "reports" / "hook-observations.jsonl"
    check("観測行が書かれた", out.exists())
    line = out.read_text(encoding="utf-8") if out.exists() else ""
    for mk in ("SECRET_CMD_MARKER", "SECRET_OUT_MARKER", "SECRET_MSG_MARKER", "SECRET_PATH_MARKER"):
        check(f"機微値 {mk} が漏れていない", mk not in line)
    check("計量メタは残る（duration_ms=42）", '"duration_ms": 42' in line, line[:160])
    rec = json.loads(line) if line else {}
    check("dropped カウントが自己申告される", rec.get("dropped", 0) >= 4, str(rec.get("dropped")))

print("== 4. 旧経路の不在 ==")
check("旧 .claude/hooks.json が存在しない（死んだ登録経路の残骸を残さない）",
      not (ROOT / ".claude" / "hooks.json").exists())


print("== 5. 不変核 anchor（v7.0.0 Phase A F1） ==")
ANCHOR_SCRIPT = ROOT / "templates" / "hooks" / "anchor-core.py"
ANCHOR_MD = ROOT / ".claude" / "anchor-core.md"
check("anchor-core.py 実在（templates/hooks・配布物）", ANCHOR_SCRIPT.exists())
check("anchor-core.md 実在（DH 本体の不変核）", ANCHOR_MD.exists())
ss_cmds = [h.get("command", "") for m in hooks.get("SessionStart", []) for h in m.get("hooks", [])]
check("SessionStart が anchor-core.py を呼ぶ（stdout が文脈に載る唯一の注入点）",
      any("anchor-core.py" in c for c in ss_cmds))
if ANCHOR_SCRIPT.exists():
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    r = subprocess.run([sys.executable, str(ANCHOR_SCRIPT)], capture_output=True, text=True, env=env)
    check("anchor exit 0", r.returncode == 0, r.stderr[:120])
    check("anchor が不変核 4 条を出力する", r.stdout.count("\n") >= 4 and "第 9 条" in r.stdout, r.stdout[:80])
    check("anchor が HTML コメント（規範メタデータ）を出力しない", "<!--" not in r.stdout)
    body = re.sub(r"<!--.*?-->", "", ANCHOR_MD.read_text(encoding="utf-8"), flags=re.S).strip()
    check("不変核は 400 字 / 8 行以内", len(body) <= 400 and len(body.splitlines()) <= 8, f"{len(body)} chars")
    with tempfile.TemporaryDirectory() as td:
        r2 = subprocess.run([sys.executable, str(ANCHOR_SCRIPT)], capture_output=True, text=True,
                            env=dict(os.environ, CLAUDE_PROJECT_DIR=td))
        check("md 不在でも exit 0・無出力（degrade）", r2.returncode == 0 and r2.stdout == "")

if FAIL:
    sys.exit(f"\nFAIL: {FAIL} 件")
print("\nPASS: hook-wiring 回帰テスト 全通過")
