"""検査: 宣言の鮮度（v6.18.0 C-2 で検査 8 から分離）

**欠落の型**: 鮮度 — 宣言が現在の実体に追いついているか

VERSION / GRAPH.yml の `version:` / upgrade-spec の状態行 / dev-env-spec §バージョン履歴 が
互いに、そして実体に追いついているかを見る。v6.17.0 F1 が塞いだ
「版番号が実装から離れていても誰も気づかない」型の欠落。

## 分割の経緯

Council `council-2026-09-06T15:00:00Z-splt02`（jc 0.85 / 3 軸全会一致）。
検査 8 は v6.17.0 で 6 → 13 項目に増え **672 行**に肥大した。3 軸が独立に同一のバグ
（dict 重複キーによる F4 METRIC の消失・PR #263 で是正）を発見し、
**肥大が実際に見落としを生んだ実証**となったため分割した。

分割基準は当初の申し送りにあった「1 検査器 = 1 宣言ファイル」**ではない**。
F1 は 4 ファイル、F4 は 2 ファイルを読み、F3 は宣言を読まない（実体走査のみ）ため、
宣言ファイル単位では切れないことが実測で判明した。採った基準は
**「1 検査器 = 1 つの欠落の型」**（実体→宣言 / 鮮度 / 実質 / 実体の誤配置）である。

規範メタデータ:
    stage: 全段階
    review_trigger:
      - measured: 版整合 FAIL が 6 cycle 連続 0 件なら、状態行の値域固定のみ残して簡素化を検討
      - measured: 検査 5（WARN）が初期是正後 1 cycle で 0 件に落ちなければ誤検知率を再測定し、
        落ちないなら本検査を削る（Council vrsn01 mitigation 9）
"""

from __future__ import annotations

import re
from pathlib import Path

from typing import Any

try:  # verify.py 経由（パッケージとして読み込まれる正規経路）
    from ._declaration_util import surface_missing
except ImportError:  # 単体ロード（scripts/test-*.py が spec_from_file_location で読む）
    import importlib.util as _ilu

    _p = Path(__file__).with_name("_declaration_util.py")
    _s = _ilu.spec_from_file_location("_declaration_util", _p)
    if _s is None or _s.loader is None:
        raise ImportError(f"_declaration_util.py を単体ロードできない: {_p}")
    _m = _ilu.module_from_spec(_s)
    _s.loader.exec_module(_m)
    surface_missing = _m.surface_missing


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

# 検査 5b: 実装側（live 面）が「この版のこの項目は着地した」と名乗っているのに、
# 当の spec の状態行が起草のままである、を捕まえる。
# 検査 5 は spec **自身の本文**しか見ないので、着地の主張が実装側にあると素通りする
# （実測 2026-09-07: v6.13.0 F5 は norm-scan.py として着地済みなのに状態行は `L0 起草` のままだった）。
#
# 語は「着地 / 実装済 / で実装」。偽陽性は語を削るのではなく**後続の否定先読み**で潰す
# （「予定 / 候補 / したい / すべき / する」が続けば主張ではない）。
#
# 初版は否定先読みと同時に「で実装」も削ってしまい、`… を norm-scan.py で実装した` のような
# 真の着地主張を取り落としていた（PR #270 の Copilot 指摘で判明。8 例で実測したところ
# 先読みだけで偽陽性は 0 になり、語を削る必要は無かった）。
# 単なる引用（`observe.py`「v6.14.0 F2 と同旨」/ `（v6.13.0 F5-3）`）は
# そもそも着地語を含まないので、いずれの版でも拾わない。
LANDED_CLAIM_RE = re.compile(
    r"v(\d+)\.(\d+)\.(\d+)\s+F\d+[^\n]*?(?:着地|実装済|で実装)(?!.*(?:予定|候補|したい|すべき|する))")
# live 面 = 実装の側。設計文書（dh-upgrades / delivery / history）と test-* は除く。
LIVE_DIRS = ("scripts", ".claude", "harness-verifier", "templates")

HISTORY_FREEZE_MARKER = "凍結マーカー"

HISTORY_ITEM_RE = re.compile(r"^- v(\d+)\.(\d+):", re.M)


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

    if not graph_path.is_file():
        surface_missing(issues, repo_root, "GRAPH.yml", "GRAPH.yml")
    else:
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
    draft_specs: dict[tuple[int, int, int], str] = {}
    spec_dir = repo_root / "dh-upgrades"
    if not spec_dir.is_dir():
        surface_missing(issues, repo_root, "dh-upgrades/", "dh-upgrades/（upgrade-spec の置き場）")
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

        if kind in ("draft", "council"):
            draft_specs[spec_ver] = state

        # 5. L0 起草のまま本文が実装を名乗る（file-local 判定）
        if kind == "draft" and IMPL_CLAIM_RE.search(text):
            issues.append({
                "location": rel,
                "message": ("状態行が `L0 起草` のまま本文が実装を名乗っている。"
                            "状態行を実態に合わせる（実装中 / 実装済み）"),
                "severity": "WARN",
            })

    # --- 5b. 実装側の着地主張 ⇄ spec の状態行 ---
    if draft_specs:
        for ver_key, rel in _scan_landed_claims(repo_root):
            if ver_key in draft_specs:
                issues.append({
                    "location": rel,
                    "message": (f"実装側が v{'.'.join(map(str, ver_key))} の項目の着地を名乗っているが、"
                                f"`dh-upgrades/upgrade-spec-v{'.'.join(map(str, ver_key))}.md` の状態行は "
                                f"`{draft_specs[ver_key]}` のまま。状態行を実態に合わせる"
                                f"（値域は dev-env-spec §状態行の値域）"),
                    "severity": "WARN",
                })

    # --- 6. dev-env-spec §バージョン履歴 の凍結 ---
    dev_env = skills_dir / "layer0-spec-architect" / "references" / "dev-env-spec.md"
    if not dev_env.is_file():
        surface_missing(issues, repo_root, "dev-env-spec.md", "dev-env-spec.md")
    else:
        text = dev_env.read_text(encoding="utf-8")
        m = re.search(r"^###\s*バージョン履歴.*?$(.*?)(?=^###\s|\Z)", text, re.M | re.S)
        # アンカーが外れたら黙って skip しない。見出しに空白 1 個を入れるだけで
        # この検査が無効化し --strict が緑で通ることを実測した（2026-09-07）。
        if not m:
            surface_missing(issues, repo_root, "dev-env-spec.md §バージョン履歴",
                            "§バージョン履歴 の見出し（`### バージョン履歴...`）")
        else:
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
        "message": (f"鮮度 — VERSION={version_txt} / "
                    f"upgrade-spec {len(list(spec_dir.glob('upgrade-spec-v*.md'))) if spec_dir.is_dir() else 0} 本を検査"),
        "severity": "METRIC",
    })
    return issues


def _ver(text: str) -> tuple[int, int, int] | None:
    m = re.match(r"^\s*(\d+)\.(\d+)\.(\d+)\s*$", text)
    return (int(m[1]), int(m[2]), int(m[3])) if m else None


def _classify(state: str) -> str | None:
    for name, pat in STATE_PATTERNS:
        if re.match(pat, state.strip()):
            return name
    return None


def _scan_landed_claims(repo_root: Path):
    """live 面から「vX.Y.Z F<n> ... 着地/実装済/で実装」の主張を拾う。

    返すのは (版 tuple, 相対パス) の列。設計文書と test-* は対象外 —
    そこでは「v6.14.0 F2 と同旨」のような参照が正常に現れるため。
    """
    seen = set()
    for d in LIVE_DIRS:
        base = repo_root / d
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in (".py", ".md", ".yml", ".yaml"):
                continue
            if path.name.startswith("test-"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, ValueError):
                continue
            for a, b, c in ((m[1], m[2], m[3]) for m in LANDED_CLAIM_RE.finditer(text)):
                key = (int(a), int(b), int(c))
                rel = path.relative_to(repo_root).as_posix()
                if (key, rel) not in seen:
                    seen.add((key, rel))
                    yield key, rel
