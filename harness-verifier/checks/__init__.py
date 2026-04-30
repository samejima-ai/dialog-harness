"""harness-verifier check modules.

各モジュールは `run(skills_dir: Path, glossary_path: Path) -> list[dict]` を export する。
返り値の dict は最低 `location` / `message` / `severity` (FAIL/WARN/ERROR) を持つ。
"""
