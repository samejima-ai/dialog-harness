#!/usr/bin/env python3
"""council-axis-audit — COUNCIL-LOG.md から Council の軸独立性と観測バイアスを決定論で測る。

`delivery/ANALYSIS-council-axis-independence-2026-07-26.md`（PR #171）の案 B1/B2/B3/B5 の実装。

## なぜ必要か

Council の「3 軸の独立観測」は設計上の主張であって、**測られていなかった**。
実測（2026-07-26）で判明したのは:

- 経営者 ⇄ 開発者の `stance` 一致率が 70.7%（他ペアは 29〜34%）
- しかし `dimension` 語彙の重複は全ペア 25/25 で Jaccard 0.000
- `confidence` は軸ごとに固定（σ ≈ 0.04）。原因は persona prompt の帯指定
- その結果 `weight × confidence` の実効配分が宣言配分から系統的に乖離
  （全 7 カテゴリで開発者 +4.9pt / 経営者 −1.9pt / 哲学者 −3.0pt）

**本ツールは LLM 判定を一切含まない。** 軸のバイアスを LLM に検査させると、
検査する側が同じ死角を共有する（分析文書 §3-1「死角を持つ者に死角の有無を尋ねる構造」）。
したがって検査は集計のみで行い、判断は人間（D5）に残す。

## 最重要の設計制約: 2 指標を対で読む

**`stance` 一致率だけで軸の冗長性を判定してはならない。** 上記分析の rev.1 は
一致率 70.7% だけを見て「経営者軸は冗長」と誤診し、軸の縮退を推奨した。
`dimension` を測ったら語彙が完全に分離しており、診断は覆った。

一致率が高いことには 2 つの原因がありうる:

- **異なる次元から同じ結論に達した**（＝ 情報。`conflict-typology.md` の対立類型 B）
- **同じ次元を二重に見た**（＝ 冗長。軸の再設計対象）

この 2 つは `dimension` を見なければ区別できない。よって本ツールは
**両方が閾値を超えたときにのみ**「軸冗長の疑い」を報告する。片方だけの警報は出さない。

## 使い方

    python3 scripts/council-axis-audit.py                      # 既定ログを監査
    python3 scripts/council-axis-audit.py --log path/to/LOG.md # ログを指定
    python3 scripts/council-axis-audit.py --json               # 機械可読出力

終了コードは常に 0（warn のみ・block しない。philosophy.md 第6条 人間最終承認）。
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# ---- 閾値（分析文書 §3-2 / §5 案群 B。F2/F3 で実測に応じて校正する）------------

# stance 一致率がこれを超え、かつ DIMENSION_JACCARD_MAX も超えたときのみ軸冗長を疑う
STANCE_AGREEMENT_MAX = 0.65
# dimension 語彙の Jaccard がこれを超えると観測次元の重複＝真の冗長の疑い
DIMENSION_JACCARD_MAX = 0.30
# 軸内 confidence の標準偏差がこれ未満なら「議題に反応していない」（persona 固定の疑い）
CONFIDENCE_SIGMA_MIN = 0.10
# 実効配分が宣言配分より系統的に「有利」な軸を検出する閾値（pt）。
# 乖離はゼロサム（1 軸が得れば他が失う）なので、**得ている軸のみ**を warn する。
# 失っている軸を併せて warn すると、同一現象を軸数ぶん重複報告することになる。
EFFECTIVE_WEIGHT_DRIFT_MAX_PT = 3.0

# ---- COUNCIL-LOG のパース（council-log-sync.py と同じブロック形式のみ読む）-----

_ENTRY_START = re.compile(r'^- invocation_id:\s*"?([^"\n]+)"?\s*$')
_NESTED_BLOCK = re.compile(r'^  (\w+):\s*$')
_PERSONA_LINE = re.compile(r'^\s+(\S+):\s*\{(.*)\}\s*$')
_SCALAR_FIELD = re.compile(r'^  ([a-z_]+):\s*(.*)$')


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


def parse_entries(text: str) -> list[dict]:
    """`- invocation_id:` ブロック形式のエントリから persona_summary と category を抽出する。

    persona_summary の各行は `    <軸>: { stance: "...", confidence: 0.7, dimension: "..." }`
    形式のインライン mapping。PyYAML には依存しない（council-log-sync.py と同じ独立性要請）。
    """
    entries: list[dict] = []
    cur: dict | None = None
    in_persona_summary = False

    for raw in text.splitlines():
        m_start = _ENTRY_START.match(raw)
        if m_start:
            if cur is not None:
                entries.append(cur)
            cur = {"invocation_id": _unquote(m_start.group(1)), "personas": {}}
            in_persona_summary = False
            continue
        if cur is None:
            continue

        m_block = _NESTED_BLOCK.match(raw)
        if m_block:
            in_persona_summary = m_block.group(1) == "persona_summary"
            continue

        if in_persona_summary:
            m_p = _PERSONA_LINE.match(raw)
            if m_p:
                name, body = m_p.group(1), m_p.group(2)
                rec: dict = {}
                m_s = re.search(r'stance:\s*"([^"]*)"', body)
                if m_s:
                    rec["stance"] = m_s.group(1).strip()
                m_c = re.search(r'confidence:\s*([0-9.]+)', body)
                if m_c:
                    try:
                        rec["confidence"] = float(m_c.group(1))
                    except ValueError:
                        pass
                m_d = re.search(r'dimension:\s*"([^"]*)"', body)
                if m_d:
                    rec["dimension"] = m_d.group(1).strip()
                if rec:
                    cur["personas"][name] = rec
                continue
            if not raw.startswith("    "):
                in_persona_summary = False

        m_f = _SCALAR_FIELD.match(raw)
        if m_f:
            key, val = m_f.group(1), m_f.group(2)
            if val and not val.rstrip().endswith(":"):
                cur.setdefault(key, _unquote(val))

    if cur is not None:
        entries.append(cur)
    return entries


# ---- B1: 軸独立性（stance 一致率 × dimension Jaccard を対で）-------------------


def _dimension_tokens(s: str) -> set[str]:
    """dimension 文字列をトークン集合に分解する（`/` `／` 区切り）。

    注意: 完全一致でのみ照合する。「運用コスト」と「コミュニケーションコスト」は
    別トークンとして扱う。よって Jaccard 0.0 は「語彙が違う」ことの指標であり、
    「観測している概念が違う」ことの証明ではない（分析文書 §7 の限界）。
    概念レベルの判定には LLM が必要で、それは自己参照問題に戻るため実装しない。
    """
    return {t.strip() for t in re.split(r"[/／]", s) if t.strip()}


def audit_axis_independence(entries: list[dict], axes: list[str]) -> dict:
    pairs: dict[str, dict] = {}
    for i, a in enumerate(axes):
        for b in axes[i + 1:]:
            stance_n = stance_agree = 0
            jaccards: list[float] = []
            for e in entries:
                pa, pb = e["personas"].get(a), e["personas"].get(b)
                if not pa or not pb:
                    continue
                if "stance" in pa and "stance" in pb:
                    stance_n += 1
                    if pa["stance"] == pb["stance"]:
                        stance_agree += 1
                if "dimension" in pa and "dimension" in pb:
                    ta, tb = _dimension_tokens(pa["dimension"]), _dimension_tokens(pb["dimension"])
                    if ta or tb:
                        jaccards.append(len(ta & tb) / len(ta | tb))
            rate = (stance_agree / stance_n) if stance_n else None
            jac = (sum(jaccards) / len(jaccards)) if jaccards else None
            # 2 指標が「両方」閾値超えのときのみ冗長を疑う（片方だけでは誤診する）
            redundant = (
                rate is not None and jac is not None
                and rate > STANCE_AGREEMENT_MAX and jac > DIMENSION_JACCARD_MAX
            )
            pairs[f"{a}⇄{b}"] = {
                "stance_n": stance_n,
                "stance_agreement": rate,
                "dimension_n": len(jaccards),
                "dimension_jaccard": jac,
                "redundancy_suspected": redundant,
            }
    return pairs


# ---- B2: confidence 固定の検出 -------------------------------------------------


def audit_confidence_spread(entries: list[dict], axes: list[str]) -> dict:
    out: dict[str, dict] = {}
    for ax in axes:
        vals = [
            e["personas"][ax]["confidence"]
            for e in entries
            if ax in e["personas"] and "confidence" in e["personas"][ax]
        ]
        if not vals:
            out[ax] = {"n": 0}
            continue
        sigma = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        out[ax] = {
            "n": len(vals),
            "mean": round(statistics.mean(vals), 3),
            "sigma": round(sigma, 3),
            "min": min(vals),
            "max": max(vals),
            "distinct_values": len(set(vals)),
            "pinned_suspected": len(vals) > 1 and sigma < CONFIDENCE_SIGMA_MIN,
        }
    return out


# ---- B3: 宣言配分 vs 実効配分の乖離 -------------------------------------------


def _parse_weights(weights_md: Path) -> tuple[dict, dict, dict]:
    """council-weights.md の fenced YAML から base / ethos / situational を読む。

    PyYAML に依存せず、`  <key>: <num>` の 2 段ネストだけを拾う簡易パーサ。
    council-weights.md の構造（3 ブロック × Council 種別 × 軸）に特化する。
    """
    text = weights_md.read_text(encoding="utf-8")
    blocks: dict[str, str] = {}
    for name in ("base_weights", "ethos_multiplier", "situational_modifier"):
        m = re.search(rf"^{name}:\s*$((?:\n[ \t]+.*|\n)*)", text, re.M)
        if m:
            blocks[name] = m.group(1)

    def two_level(body: str) -> dict:
        out: dict[str, dict] = {}
        cur = None
        for line in body.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            # 親キーは行末コメントを伴う（例 `  implementation:   # 実装判断`）
            m_parent = re.match(r"^  ([^\s:]+):\s*(?:#.*)?$", line)
            if m_parent:
                cur = m_parent.group(1)
                out[cur] = {}
                continue
            m_leaf = re.match(r"^    ([^\s:]+):\s*([+-]?[0-9.]+)", line)
            if m_leaf and cur:
                out[cur][m_leaf.group(1)] = float(m_leaf.group(2))
        return out

    return (
        two_level(blocks.get("base_weights", "")),
        two_level(blocks.get("ethos_multiplier", "")),
        two_level(blocks.get("situational_modifier", "")),
    )


def audit_effective_weights(
    weights_md: Path, confidence: dict, axes: list[str], council_type: str = "business"
) -> dict:
    """宣言配分（weight のみ）と実効配分（weight × 実測 confidence 平均）を比較する。

    confidence が軸固有定数として振る舞う場合、それは「第二の重み」として働き、
    council-weights.md が宣言した配分を歪める。本関数はその歪みを pt で示す。
    """
    base, ethos, situational = _parse_weights(weights_md)
    b = base.get(council_type, {})
    e = ethos.get(council_type, {})
    if not b:
        return {"error": f"base_weights.{council_type} を council-weights.md から読めなかった"}

    means = {ax: confidence.get(ax, {}).get("mean") for ax in axes}
    if any(means[ax] is None for ax in axes):
        return {"error": "confidence 平均が全軸で揃わないため実効配分を計算できない"}

    per_category: dict[str, dict] = {}
    drift: dict[str, list[float]] = {ax: [] for ax in axes}
    for cat, mod in situational.items():
        w = {ax: b.get(ax, 0) * e.get(ax, 1.0) + mod.get(ax, 0) for ax in axes}
        w = {ax: max(v, 0.0) for ax, v in w.items()}   # orchestrator.md: 負は 0 クランプ
        tw = sum(w.values())
        ew = {ax: w[ax] * means[ax] for ax in axes}
        te = sum(ew.values())
        if tw <= 0 or te <= 0:
            continue
        d = {ax: (ew[ax] / te - w[ax] / tw) * 100 for ax in axes}
        for ax in axes:
            drift[ax].append(d[ax])
        per_category[cat] = {
            "sum_weight": round(tw, 2),
            # council-weights.md は situational_modifier の合計 0 を宣言している。
            # 破れていると ΣW が 10 から動く（既知の宣言違反: judgment / conception が +1）
            "modifier_sum": round(sum(mod.get(ax, 0) for ax in axes), 2),
            "drift_pt": {ax: round(d[ax], 1) for ax in axes},
        }

    summary = {}
    for ax in axes:
        ds = drift[ax]
        if not ds:
            continue
        mean_d = sum(ds) / len(ds)
        summary[ax] = {
            "mean_drift_pt": round(mean_d, 1),
            "min_drift_pt": round(min(ds), 1),
            "max_drift_pt": round(max(ds), 1),
            "consistent_direction": all(x > 0 for x in ds) or all(x < 0 for x in ds),
            # 得ている軸のみ warn（ゼロサムゆえ失う軸は自動的に生じ、独立の異常ではない）
            "systematic_bias_suspected": (
                mean_d > EFFECTIVE_WEIGHT_DRIFT_MAX_PT and all(x > 0 for x in ds)
            ),
        }
    return {"per_category": per_category, "summary": summary}


# ---- B5: dimension 記録率 -----------------------------------------------------


def audit_dimension_coverage(entries: list[dict], axes: list[str]) -> dict:
    with_stance = sum(1 for e in entries if all("stance" in e["personas"].get(a, {}) for a in axes))
    with_dim = sum(1 for e in entries if all("dimension" in e["personas"].get(a, {}) for a in axes))
    return {
        "entries_total": len(entries),
        "all_axes_stance": with_stance,
        "all_axes_dimension": with_dim,
        "dimension_record_rate": round(with_dim / with_stance, 3) if with_stance else None,
        # B1 の dimension 側の分解能は記録率で決まる。低いと冗長判定が保留になる
        "note": "dimension 記録率が低いと B1 の冗長判定は保留になる（stance だけでは判定しない）",
    }


# ---- レポート -----------------------------------------------------------------


def render(result: dict) -> str:
    L: list[str] = []
    ok = "OK"
    warn = "WARN"

    L.append("# Council 軸独立性・観測バイアス監査")
    L.append("")
    L.append(f"- ログ: `{result['log_path']}`")
    cov = result["dimension_coverage"]
    L.append(
        f"- エントリ {cov['entries_total']} 件 / 全軸 stance {cov['all_axes_stance']} 件 "
        f"/ 全軸 dimension {cov['all_axes_dimension']} 件"
        + (f"（記録率 {cov['dimension_record_rate']:.0%}）" if cov["dimension_record_rate"] is not None else "")
    )
    L.append("")

    L.append("## B1. 軸独立性（stance 一致率 × dimension Jaccard を対で読む）")
    L.append("")
    L.append("| 軸ペア | stance 一致率 | dimension Jaccard | 判定 |")
    L.append("|---|---|---|---|")
    for pair, v in result["axis_independence"].items():
        rate = f"{v['stance_agreement']:.1%} (n={v['stance_n']})" if v["stance_agreement"] is not None else "—"
        jac = f"{v['dimension_jaccard']:.3f} (n={v['dimension_n']})" if v["dimension_jaccard"] is not None else "測定不能"
        if v["redundancy_suspected"]:
            verdict = f"{warn} 軸冗長の疑い（2 指標とも閾値超え）"
        elif v["stance_agreement"] is not None and v["stance_agreement"] > STANCE_AGREEMENT_MAX:
            verdict = f"{ok} 結論は一致するが観測次元は分離（＝類型 B・冗長ではない）"
        else:
            verdict = ok
        L.append(f"| {pair} | {rate} | {jac} | {verdict} |")
    L.append("")
    L.append(
        f"> 閾値: stance 一致率 > {STANCE_AGREEMENT_MAX} **かつ** dimension Jaccard > {DIMENSION_JACCARD_MAX} の"
        "両方を満たしたときのみ冗長と判定する。片方だけでは「異なる次元から同じ結論」と"
        "「同じ次元の二重計上」を区別できない。"
    )
    L.append("")

    L.append("## B2. confidence が議題に反応しているか")
    L.append("")
    L.append("| 軸 | n | 平均 | σ | 幅 | 相異値 | 判定 |")
    L.append("|---|---|---|---|---|---|---|")
    for ax, v in result["confidence_spread"].items():
        if not v.get("n"):
            L.append(f"| {ax} | 0 | — | — | — | — | 測定不能 |")
            continue
        verdict = f"{warn} 固定の疑い（議題に反応していない）" if v["pinned_suspected"] else ok
        L.append(
            f"| {ax} | {v['n']} | {v['mean']} | {v['sigma']} | "
            f"{v['min']}–{v['max']} | {v['distinct_values']} | {verdict} |"
        )
    L.append("")
    L.append(f"> 閾値: σ < {CONFIDENCE_SIGMA_MIN}。議題が変わっても confidence が動かないなら、")
    L.append("> それは観測の産物ではなく prompt の産物である疑いがある。")
    L.append("")

    L.append("## B3. 宣言配分 vs 実効配分（confidence が第二の重みとして働く歪み）")
    L.append("")
    eff = result["effective_weights"]
    if "error" in eff:
        L.append(f"測定不能: {eff['error']}")
    else:
        L.append("| 軸 | 平均乖離 | 範囲 | 全カテゴリ同方向 | 判定 |")
        L.append("|---|---|---|---|---|")
        for ax, v in eff["summary"].items():
            verdict = f"{warn} 系統的バイアス" if v["systematic_bias_suspected"] else ok
            L.append(
                f"| {ax} | {v['mean_drift_pt']:+}pt | "
                f"{v['min_drift_pt']:+}〜{v['max_drift_pt']:+}pt | "
                f"{'はい' if v['consistent_direction'] else 'いいえ'} | {verdict} |"
            )
        L.append("")
        L.append(
            "> 乖離はゼロサム（合計 0）である。1 軸が系統的に得ていれば他軸は必ず失う。"
            "したがって warn は**得ている軸のみ**に出す。失っている軸の負値は独立の異常ではなく、"
            "得ている軸の裏面である。"
        )
        bad = {c: v for c, v in eff["per_category"].items() if v["modifier_sum"] != 0}
        if bad:
            L.append("")
            L.append(
                f"> {warn} `situational_modifier` の合計 0 宣言違反: "
                + " / ".join(f"`{c}` ({v['modifier_sum']:+g} → ΣW {v['sum_weight']:g})" for c, v in bad.items())
                + "。`council-weights.md` §編集プロトコルにより数値の是正は L0/D5 専管。"
            )
    L.append("")

    warns = result["warnings"]
    L.append("## 総括")
    L.append("")
    if warns:
        for w in warns:
            L.append(f"- {warn}: {w}")
    else:
        L.append("- 閾値超えなし。")
    L.append("")
    L.append(
        "> 本監査は集計のみで LLM 判定を含まない。**是正の判断は人間（D5）に残る**"
        "（philosophy.md 第6条）。軸の増減・重み数値の変更は L0 対話を経ること。"
    )
    return "\n".join(L)


def collect_warnings(result: dict) -> list[str]:
    w: list[str] = []
    for pair, v in result["axis_independence"].items():
        if v["redundancy_suspected"]:
            w.append(
                f"{pair} は stance 一致率 {v['stance_agreement']:.1%} かつ "
                f"dimension Jaccard {v['dimension_jaccard']:.3f} で軸冗長の疑い"
            )
    for ax, v in result["confidence_spread"].items():
        if v.get("pinned_suspected"):
            w.append(f"{ax} の confidence が σ={v['sigma']} で固定の疑い（議題に反応していない）")
    eff = result["effective_weights"]
    for ax, v in eff.get("summary", {}).items():
        if v["systematic_bias_suspected"]:
            w.append(
                f"{ax} の実効配分が宣言配分より平均 {v['mean_drift_pt']:+}pt 系統的に有利"
                "（confidence が第二の重みとして働いている）"
            )
    for cat, v in eff.get("per_category", {}).items():
        if v["modifier_sum"] != 0:
            w.append(f"situational_modifier.{cat} の合計が {v['modifier_sum']:+g}（宣言は 0）")
    cov = result["dimension_coverage"]
    if cov["dimension_record_rate"] is not None and cov["dimension_record_rate"] < 0.5:
        w.append(
            f"dimension 記録率 {cov['dimension_record_rate']:.0%} — B1 の冗長判定の分解能が不足"
        )
    return w


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Council の軸独立性と観測バイアスを決定論で監査する")
    ap.add_argument("--log", default="history/COUNCIL-LOG.md", help="COUNCIL-LOG.md のパス")
    ap.add_argument(
        "--weights",
        default=".claude/skills/crosscut-council/council-weights.md",
        help="council-weights.md のパス",
    )
    ap.add_argument("--axes", default="経営者,開発者,哲学者", help="軸名（カンマ区切り）")
    ap.add_argument("--json", action="store_true", help="機械可読出力")
    args = ap.parse_args(argv)

    log_path = Path(args.log)
    if not log_path.is_file():
        print(f"WARN: ログが見つかりません: {log_path}（skip）", file=sys.stderr)
        return 0

    axes = [a.strip() for a in args.axes.split(",") if a.strip()]
    entries = parse_entries(log_path.read_text(encoding="utf-8"))

    conf = audit_confidence_spread(entries, axes)
    weights_path = Path(args.weights)
    result = {
        "log_path": str(log_path),
        "axes": axes,
        "dimension_coverage": audit_dimension_coverage(entries, axes),
        "axis_independence": audit_axis_independence(entries, axes),
        "confidence_spread": conf,
        "effective_weights": (
            audit_effective_weights(weights_path, conf, axes)
            if weights_path.is_file()
            else {"error": f"council-weights.md が見つかりません: {weights_path}"}
        ),
    }
    result["warnings"] = collect_warnings(result)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result))
    # 常に 0（warn のみ・block しない）
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
