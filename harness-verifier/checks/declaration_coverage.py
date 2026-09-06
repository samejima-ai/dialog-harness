"""検査 8: 宣言被覆（v6.17.0）

既存 7 検査は「宣言 → 実体」（宣言したものが在るか）だけを見ており、
以下 3 種の欠落が構造的に検出できなかった（upgrade-spec v6.17.0 §0）:

    - 実体 → 宣言: 在るものが宣言されているか
    - 宣言の鮮度: 宣言が現在の実体に追いついているか
    - 宣言の実質: 宣言が指す source が実際にその内容を持つか

本モジュールはその受け皿である。**F1（版整合）/ F2（宣言網羅・source 実質）/ F4（manifest 分類網羅）/
F6（RL 現況の被覆）分を実装済み**で、v6.17.0 の受け皿はこれで揃った。

F1（版整合）の検査項目:
    1. VERSION == GRAPH.yml の version:（不一致 = FAIL）
    2. upgrade-spec の状態行が値域内（値域外 = FAIL）
    3. VERSION より大きい版の spec は状態行を持つ（欠落 = FAIL）
       ※ VERSION 以下の歴史的 spec には遡及適用しない（I-4: 常時発火する検知を作らない）
    4. `実装済み` を名乗る spec の版 <= VERSION（超過 = FAIL）
    5. 状態行が `L0 起草` のまま本文が実装を名乗る（= WARN。file-local 判定）
    6. dev-env-spec.md §バージョン履歴 の凍結（マーカー欠落 / v4.2 超の追記 = FAIL）

F4（manifest 分類網羅）の検査項目:
    11. リポジトリ直下 / `.claude/` 直下の実在パスが 4 分類 ∪ owned_skills ∪
        unclassified_ok のいずれかに属す（属さない = WARN）
    12. `paths.owned_skills` == `.claude/skills/` 実在 dir（不一致 = FAIL）
        Council D-4 必須随伴条件 (a)。列挙漏れは「配布されないまま誰も困らない」静かな失敗になる

F6（RL 現況の被覆）の検査項目:
    10. templates/rules/common/*.md ⇄ README §common/ の現況 の列挙が一致（不一致 = FAIL）
        件数ではなくファイル名で突き合わせる（件数一致は名前が入れ替わっても通る）

F2（宣言網羅・source 実質）の検査項目:
    7. .claude/skills/*/ ⊆ (nodes[].id ∪ graph_excluded[].id)（違反 = FAIL）
       prefix でフィルタしない（glossary.py:250 の managed_prefixes が rtk-integration を
       落とした欠陥を持ち込まない）
    8. scripts/*.py（test-* 除く）⊆ (nodes[].impl ∪ graph_excluded[].path)（違反 = WARN）
    9. source 実質検査: edge.source が .md のとき、その本文に edge.to の impl basename
       または node id が出現すること（不出現 = WARN）。パス存在しか見ない G-2 の補完であり、
       意味は判定しない決定論検査

検査 5 を `git log --grep` にしない理由（Council vrsn01 / 開発者軸の指摘を実測で確認）:
    grep 方式は v6.13.0 に 4 件 / v6.14.0 に 2 件 / v6.16.0 に 2 件を返すが、
    その大半は **当該 spec 自身の起草 commit** と個人名の一括匿名化 sweep である。
    導入初日から非ゼロで、全 draft が実装されるまで 0 にならない
    = 不変条件 I-4「常時発火する検知を作らない」に違反する。
    file-local 判定は真陽性のみに発火し、かつ git 履歴に依存しないので配布先でも同じ判定ができる。

規範メタデータ:
    stage: 全段階
    review_trigger:
      - measured: 検査 5（WARN）が初期是正後 1 cycle で 0 件に落ちなければ、
        誤検知率を再測定し、落ちないなら本検査を削る（Council vrsn01 mitigation 9）
      - measured: 版整合 FAIL が 6 cycle 連続 0 件なら、状態行の値域固定のみ残して簡素化を検討
      - measured: source 実質検査（検査 9・WARN）が 6 cycle 連続 0 件なら FAIL 昇格を検討
        （G-5 と同じ昇格規律。upgrade-spec-v6.17.0 §F2 規範メタデータ）
      - measured: 検査 10（F6）が 6 cycle 連続 0 件なら、RL の増減自体が止まっている可能性を疑い
        配布の要否を再問（upgrade-spec-v6.17.0 §F6 規範メタデータ）
      - stage_transition: DH が新しい配布面（新ディレクトリ）を持つとき、検査 11 の
        unclassified_ok を見直す（upgrade-spec-v6.17.0 §F4 規範メタデータ）
      - measured: 検査 11（WARN）が 6 cycle 連続 0 件なら降格候補
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:  # verify.py 経由（パッケージとして読み込まれる正規経路）
    from .execution_graph import parse_graph
except ImportError:  # 単体ロード（scripts/test-declaration-coverage.py が spec_from_file_location で読む）
    import importlib.util as _ilu

    _path = Path(__file__).with_name("execution_graph.py")
    _spec = _ilu.spec_from_file_location("_execution_graph", _path)
    # spec / loader は None を返しうる。ここで潰さないと後段が AttributeError になり、
    # 「なぜ検査 7-9 が動かないのか」が読めない失敗になる。原因の分かる例外に変換する。
    if _spec is None or _spec.loader is None:
        raise ImportError(f"execution_graph.py を単体ロードできない: {_path}")
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    parse_graph = _mod.parse_graph

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
HISTORY_FREEZE_MARKER = "凍結マーカー"
HISTORY_ITEM_RE = re.compile(r"^- v(\d+)\.(\d+):", re.M)


def _ver(text: str) -> tuple[int, int, int] | None:
    m = re.match(r"^\s*(\d+)\.(\d+)\.(\d+)\s*$", text)
    return (int(m[1]), int(m[2]), int(m[3])) if m else None


def _classify(state: str) -> str | None:
    for name, pat in STATE_PATTERNS:
        if re.match(pat, state.strip()):
            return name
    return None


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

    if graph_path.is_file():
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
    spec_dir = repo_root / "dh-upgrades"
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

        # 5. L0 起草のまま本文が実装を名乗る（file-local 判定）
        if kind == "draft" and IMPL_CLAIM_RE.search(text):
            issues.append({
                "location": rel,
                "message": ("状態行が `L0 起草` のまま本文が実装を名乗っている。"
                            "状態行を実態に合わせる（実装中 / 実装済み）"),
                "severity": "WARN",
            })

    # --- 6. dev-env-spec §バージョン履歴 の凍結 ---
    dev_env = skills_dir / "layer0-spec-architect" / "references" / "dev-env-spec.md"
    if dev_env.is_file():
        text = dev_env.read_text(encoding="utf-8")
        m = re.search(r"^###\s*バージョン履歴.*?$(.*?)(?=^###\s|\Z)", text, re.M | re.S)
        if m:
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

    # --- 7-9. F2: 宣言の網羅性 + source の実質 ---
    f2_counts = _check_f2(repo_root, skills_dir, graph_path, issues)

    # --- 11-12. F4: manifest 分類網羅 + owned_skills の実在一致 ---
    f4_counts = _check_f4(repo_root, skills_dir, graph_path, issues)

    # --- 10. F6: 共通 RL の現況被覆 ---
    f6_counts = _check_f6(repo_root, issues)

    issues.append({
        "location": "VERSION",
        "message": (f"F1 版整合 — VERSION={version_txt} / "
                    f"upgrade-spec {len(list(spec_dir.glob('upgrade-spec-v*.md'))) if spec_dir.is_dir() else 0} 本を検査。"
                    f"v6.17.0 の宣言被覆は F1/F2/F4/F6 で揃った"),
        "severity": "METRIC",
    })
    issues.append({
        "location": "GRAPH.yml",
        "message": (f"F2 宣言網羅 — skill {f2_counts['skills']} 件 "
                    f"(node {f2_counts['skill_nodes']} / excluded {f2_counts['skill_excluded']}) / "
                    f"script {f2_counts['scripts']} 件 "
                    f"(impl {f2_counts['script_impls']} / excluded {f2_counts['script_excluded']}) / "
                    f"source 実質検査 {f2_counts['sources_checked']} edge"),
        "severity": "METRIC",
    })
    issues.append({
        "location": "dh-manifest.yml",
        "message": (f"F4 manifest 分類網羅 — 分類済み {f4_counts['classified']} パス / "
                    f"未分類 {f4_counts['unclassified']} パス / "
                    f"owned_skills {f4_counts['owned_skills']} 件"),
        "severity": "METRIC",
    })
    issues.append({
        "location": "templates/rules/README.md",
        "message": (f"F6 RL 現況被覆 — 実ファイル {f6_counts['rl_files']} 本 / "
                    f"README 列挙 {f6_counts['rl_listed']} 本"),
        "severity": "METRIC",
    })
    return issues


def _check_f2(
    repo_root: Path, skills_dir: Path, graph_path: Path, issues: list[dict[str, Any]]
) -> dict[str, int]:
    """F2: 実体 → 宣言 の網羅性（検査 7/8）と source の実質（検査 9）。

    GRAPH.yml 不在のリポジトリでは skip する（execution_graph.py F2-4 と同じ後方互換規律）。
    """
    counts = {
        "skills": 0, "skill_nodes": 0, "skill_excluded": 0,
        "scripts": 0, "script_impls": 0, "script_excluded": 0,
        "sources_checked": 0,
    }
    if not graph_path.is_file():
        return counts

    try:
        doc = parse_graph(graph_path.read_text(encoding="utf-8"))
    except OSError:
        return counts

    nodes = [n for n in doc.get("nodes", []) if isinstance(n, dict)]
    edges = [e for e in doc.get("edges", []) if isinstance(e, dict)]
    excluded = [x for x in doc.get("graph_excluded", []) if isinstance(x, dict)]

    node_ids = {n["id"] for n in nodes if n.get("id")}
    node_impls = {n["impl"] for n in nodes if n.get("impl")}
    excluded_ids = {x["id"] for x in excluded if x.get("id")}
    excluded_paths = {x["path"] for x in excluded if x.get("path")}

    # --- 検査 7: skill dir ⊆ (nodes ∪ graph_excluded)。prefix でフィルタしない ---
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if not d.is_dir() or not (d / "SKILL.md").is_file():
                continue
            counts["skills"] += 1
            if d.name in node_ids:
                counts["skill_nodes"] += 1
            elif d.name in excluded_ids:
                counts["skill_excluded"] += 1
            else:
                issues.append({
                    "location": f".claude/skills/{d.name}/",
                    "message": (f"skill {d.name!r} が GRAPH.yml の nodes にも graph_excluded にも無い。"
                                "実体があるものは登録するか、理由付きで除外を宣言する"
                                "（upgrade-spec-v6.17.0 §F2。黙って対象外にしない）"),
                    "severity": "FAIL",
                })

    # --- 検査 8: scripts/*.py（test-* 除く）⊆ (nodes[].impl ∪ graph_excluded[].path) ---
    scripts_dir = repo_root / "scripts"
    if scripts_dir.is_dir():
        for f in sorted(scripts_dir.glob("*.py")):
            if f.name.startswith("test-"):
                continue
            counts["scripts"] += 1
            rel = f"scripts/{f.name}"
            if rel in node_impls:
                counts["script_impls"] += 1
            elif rel in excluded_paths:
                counts["script_excluded"] += 1
            else:
                issues.append({
                    "location": rel,
                    "message": (f"script {f.name!r} が GRAPH.yml の nodes[].impl にも "
                                "graph_excluded[].path にも無い。tool node 化するか除外理由を宣言する"),
                    "severity": "WARN",
                })

    # --- 検査 9: source 実質検査 ---
    # edge.source が .md のとき、その本文に edge.to の impl basename または node id が
    # 出現することを見る。G-2 は source の**パス存在**しか見ないため、実体のない宣言
    # （HV-04: ritual-protocol.md が呼んでいない council-performance への edge）が
    # PASS を通過していた。意味は判定しない — 名前が本文にあるかだけを見る決定論検査。
    impl_by_id = {n["id"]: n.get("impl", "") for n in nodes if n.get("id")}
    for e in edges:
        src, to, frm = e.get("source", ""), e.get("to", ""), e.get("from", "")
        if not src.endswith(".md") or not to:
            continue
        # self-loop は「自分の中の繰り返し」であり、本文が自分の名を呼ぶ形にならない
        # （例: circuit-breaker-spec.md は日次上限を述べるが skill 名は書かない）。
        # 名前の出現で測る本検査の対象外にする。
        if frm == to:
            continue
        src_path = repo_root / src
        if not src_path.is_file():
            continue  # パス実在は G-2 の担当（二重報告しない）
        counts["sources_checked"] += 1
        try:
            body = src_path.read_text(encoding="utf-8")
        except OSError:
            continue
        if _mentions(body, to, impl_by_id.get(to, "")):
            continue
        issues.append({
            "location": src,
            "message": (f"source 実質乖離: edge {frm}->{to} の出典に宣言されているが、"
                        f"本文が {to!r} を指す記述を持たない。"
                        "実装に無い経路を宣言していないか確認する"
                        "（G-2 はパス存在しか見ない。upgrade-spec-v6.17.0 §F2 HV-04）"),
            "severity": "WARN",
        })

    return counts


# 層 prefix（SKILL.md 本文では「L1（autonomous-dev）」のように略記される）
_LAYER_PREFIX_RE = re.compile(r"^(?:layer[012]|crosscut)-")


def _mentions(body: str, node_id: str, impl: str) -> bool:
    """本文が node_id を指す記述を持つか（決定論・意味は判定しない）。

    3 通りの書かれ方を許容する:
      1. node id そのもの（`layer1-autonomous-dev`）
      2. 層 prefix を落とした略記（`autonomous-dev`）— SKILL.md 本文の通常表記
      3. impl の basename（`verify.py` 等。skill の `SKILL.md` は識別子にならないので除く）
    """
    if node_id in body:
        return True
    short = _LAYER_PREFIX_RE.sub("", node_id)
    if short and short != node_id and short in body:
        return True
    basename = Path(impl).name if impl else ""
    return bool(basename and basename != "SKILL.md" and basename in body)


def _check_f6(repo_root: Path, issues: list[dict[str, Any]]) -> dict[str, int]:
    """F6: 共通 RL の実ファイルと README §common/ の現況 の列挙が一致するか（検査 10）。

    `templates/rules/common/` の 6 本は配布先に byte 一致で届いているが、README の現況節が
    4 本しか列挙しておらず、どれが届いているのかを宣言側から知れない状態だった
    （upgrade-spec-v6.17.0 §F6 実測）。kakuman の `check-traps-sync.mjs` が
    「常時索引 ⇄ 全文」で実装した被覆一意性検査の、DH 側 RL への転用。

    件数ではなくファイル名で突き合わせる（件数一致は名前が入れ替わっても通ってしまう）。
    """
    counts = {"rl_files": 0, "rl_listed": 0}
    common = repo_root / "templates" / "rules" / "common"
    readme = repo_root / "templates" / "rules" / "README.md"
    if not common.is_dir() or not readme.is_file():
        return counts  # 配布先など RL を持たないツリーでは skip（後方互換）

    actual = {f.name for f in common.glob("*.md")}
    counts["rl_files"] = len(actual)

    text = readme.read_text(encoding="utf-8")
    m = re.search(r"^##\s*common/ の現況\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        issues.append({
            "location": "templates/rules/README.md",
            "message": ("§common/ の現況 が見つからない。共通 RL の現況 SSOT はこの節であり、"
                        "dev-env-spec 側は本 README を参照する（upgrade-spec-v6.17.0 §F6）"),
            "severity": "FAIL",
        })
        return counts

    # 各項目の**先頭**のバッククォート名だけを RL 名とみなす。本文中の説明パス
    # （`.dh/rules/common/...` での override 例、他 skill の参照先等）を拾わないため、
    # 「- `<name>.md`」という箇条書きの見出し位置に限定する。
    listed = set(re.findall(r"^-\s+`([^`/]+\.md)`", m[1], re.M))
    counts["rl_listed"] = len(listed)

    for name in sorted(actual - listed):
        issues.append({
            "location": f"templates/rules/common/{name}",
            "message": (f"共通 RL {name!r} が README §common/ の現況 に列挙されていない。"
                        "配布はされるが宣言側から存在を知れない（F6 が塞いだ欠落の再発）"),
            "severity": "FAIL",
        })
    for name in sorted(listed - actual):
        issues.append({
            "location": "templates/rules/README.md",
            "message": (f"README §common/ の現況 が実在しない RL {name!r} を列挙している。"
                        "削除・改名に追随する"),
            "severity": "FAIL",
        })
    return counts


def _parse_manifest_paths(text: str) -> dict[str, list[str]]:
    """dh-manifest.yml の `paths:` 配下を {分類名: [値, ...]} で返す。

    GRAPH.yml 用の parse_graph はネストされた dict を読めないため、manifest 専用の
    最小パーサを持つ。読むのは「`paths:` の直下 2 段」だけで、それ以上の構造は扱わない
    （I-3 決定論・LLM 不使用。正規表現とインデント数えのみ）。
    """
    out: dict[str, list[str]] = {}
    in_paths = False
    current: str | None = None
    for raw in text.splitlines():
        if raw.startswith("paths:"):
            in_paths = True
            continue
        if not in_paths:
            continue
        # インデント 0 の非空行で paths ブロックは終わり
        if raw.strip() and not raw.startswith(" ") and not raw.startswith("#"):
            break
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 2 and stripped.endswith(":"):
            current = stripped[:-1]
            out[current] = []
        elif indent >= 4 and stripped.startswith("- ") and current:
            val = stripped[2:].split("#", 1)[0].strip().strip('"').strip("'")
            if val:
                out[current].append(val)
    return out


def _check_f4(repo_root: Path, skills_dir: Path, graph_path: Path,
              issues: list[dict[str, Any]]) -> dict[str, int]:
    """F4: dh-manifest の分類網羅（検査 11）と owned_skills の GRAPH 一致（検査 12）。

    検査 11: リポジトリ直下および `.claude/` 直下の実在パスが 4 分類 ∪ owned_skills ∪
        unclassified_ok のいずれかに属すること（属さない = WARN）。
        「明示列挙しない = 既定で不可侵」は運用として成立するが、**DH が配布したいものが
        黙って不可侵に落ちる**事故（v6.17.0 が (d) として検出した `.claude/agents/`）を
        検出できない。

    検査 12: `paths.owned_skills` == `.claude/skills/` 実在 dir（不一致 = FAIL）。
        Council D-4 必須随伴条件 (a)。列挙漏れは「静かな失敗」（配布されないまま誰も困らない）
        になるため、GRAPH.yml nodes を単一情報源として決定論で突合する（同 (c)）。
    """
    counts = {"classified": 0, "unclassified": 0, "owned_skills": 0}
    manifest = repo_root / "dh-manifest.yml"
    if not manifest.is_file():
        return counts  # 配布先など manifest を持たないツリーでは skip（I-6）

    paths = _parse_manifest_paths(manifest.read_text(encoding="utf-8"))
    if not paths:
        issues.append({
            "location": "dh-manifest.yml",
            "message": "paths: 配下の分類が読めない（4 分類の宣言が失われている可能性）",
            "severity": "FAIL",
        })
        return counts

    # --- 検査 12: owned_skills ⇄ 実在 skill dir ---
    owned = set(paths.get("owned_skills", []))
    counts["owned_skills"] = len(owned)
    if skills_dir.is_dir():
        actual = {d.name for d in skills_dir.iterdir()
                  if d.is_dir() and (d / "SKILL.md").is_file()}
        for name in sorted(actual - owned):
            issues.append({
                "location": f".claude/skills/{name}/",
                "message": (f"skill {name!r} が dh-manifest.yml の paths.owned_skills に無い。"
                            "列挙漏れは「配布されないまま誰も困らない」静かな失敗になる"
                            "（upgrade-spec-v6.17.0 §F4 / Council D-4 必須随伴条件 a）"),
                "severity": "FAIL",
            })
        for name in sorted(owned - actual):
            issues.append({
                "location": "dh-manifest.yml",
                "message": (f"paths.owned_skills が実在しない skill {name!r} を列挙している。"
                            "削除・改名に追随する"),
                "severity": "FAIL",
            })

    # --- 検査 11: 分類網羅 ---
    classified: set[str] = set()
    for key in ("overwrite", "merge", "redeploy", "never_touch", "unclassified_ok"):
        classified.update(paths.get(key, []))

    def _covered(rel: str) -> bool:
        """rel（"docs/" や ".claude/agents/" 形式）がいずれかの分類に含まれるか。"""
        if rel in classified or rel.rstrip("/") in classified:
            return True
        # never_touch の "history/" のような dir 宣言は任意の階層で有効
        return any(c.endswith("/") and rel.startswith(c) for c in classified)

    targets: list[str] = []
    for entry in sorted(repo_root.iterdir()):
        if entry.name == ".git":
            continue
        targets.append(entry.name + ("/" if entry.is_dir() else ""))
    claude_dir = repo_root / ".claude"
    if claude_dir.is_dir():
        for entry in sorted(claude_dir.iterdir()):
            targets.append(".claude/" + entry.name + ("/" if entry.is_dir() else ""))

    for rel in targets:
        if rel in (".claude/",):
            continue  # .claude/ 自体は直下の各要素で判定する
        if _covered(rel):
            counts["classified"] += 1
        else:
            counts["unclassified"] += 1
            issues.append({
                "location": rel,
                "message": (f"{rel!r} が dh-manifest.yml の 4 分類にも unclassified_ok にも属さない。"
                            "既定 never_touch に落ちるため、DH が配布したいものが黙って不可侵になる"
                            "（upgrade-spec-v6.17.0 §F4）"),
                "severity": "WARN",
            })

    return counts
