"""harness-verifier check modules.

各モジュールは `run(skills_dir: Path, glossary_path: Path) -> list[dict]` を export する。
返り値の dict は最低 `location` / `message` / `severity` (FAIL/WARN/ERROR/METRIC) を持つ。
METRIC は計数の機械出力専用で PASS/FAIL 判定に影響しない（v6.12.0 F2-5）。
"""
