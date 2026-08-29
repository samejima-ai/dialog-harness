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
# dimension 語彙の Jaccard がこれを超えると観測次元の重複＝真の冗長の疑い。
# **`conflict-typology.md` §判定ロジック の DIMENSION_OVERLAP_MAX と同値でなければならない。**
# 同じ現象（次元の重複）を分類器と監査で別基準にすると、監査が「冗長なし」と言う一方で
# 分類器が `unanimous` を出す不整合が生じる。変更するときは両方を同時に変える（B6 が検出する）。
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


# ---- B6: conflict_type 分類の整合性（v6.7.0）-----------------------------------


def classify_conflict(personas: dict, axes: list[str]) -> str | None:
    """`conflict-typology.md` §判定ロジック の決定論分類を再現する。

    分類器（Council 実行時）と監査（本ツール）が同じ規則を持つことを保証するための再実装。
    どちらかの閾値だけを動かすと B6 が不整合として検出する。
    """
    rows = [personas.get(ax) for ax in axes]
    if any(not r or "stance" not in r for r in rows):
        return None
    if len({r["stance"] for r in rows}) != 1:
        return "simple_conflict"
    dims = [r.get("dimension") for r in rows]
    if any(not d for d in dims):
        return "unanimous"      # dimension 欠落は判定不能 → 保守的
    for i, a in enumerate(dims):
        for b in dims[i + 1:]:
            ta, tb = _dimension_tokens(a), _dimension_tokens(b)
            if not (ta or tb):
                continue
            if len(ta & tb) / len(ta | tb) > DIMENSION_JACCARD_MAX:
                return "unanimous"
    return "reason_divergence"


_STANCE_AGREED = ("unanimous", "reason_divergence")
# conflict_type の値域（output-format.md §5 / §8）。PR2 で類型 A-G が入る予定
_CONFLICT_TYPE_DOMAIN = ("unanimous", "reason_divergence", "simple_conflict")


def audit_classification(entries: list[dict], axes: list[str]) -> dict:
    """記録された conflict_type と、dimension から再計算した分類の一致を検査する。

    **本監査は stance を正規化できない**（`options` が COUNCIL-LOG に無いエントリでは
    `conflict-typology.md` §stance の正規化 を再現できない）。したがって検出結果を
    2 つの診断に**分けて**報告する。混ぜると原因の異なる問題が同じ warn になる:

    - `threshold_mismatches`: 記録も再計算もどちらも「stance 一致」側なのに
      `unanimous` / `reason_divergence` が食い違う → **閾値ずれ**（本監査の本来の検出目的）
    - `normalization_gap`: 記録は「stance 一致」側だが再計算は `simple_conflict`
      → **stance 文字列の完全一致と実践の乖離**（各軸が同じ選択肢に自分の条件を付記している）。
      閾値の問題ではないので閾値を動かして直してはならない

    v6.7.0 以前の `unanimous` は「次元を問わない一致」を意味したため、
    再計算が `reason_divergence` になるケースは遡及照合しない（append-only・再解釈しない）。
    """
    threshold_mismatches: list[dict] = []
    normalization_gap: list[dict] = []
    out_of_domain: list[dict] = []
    checked = 0
    legacy = 0
    for e in entries:
        recorded = e.get("conflict_type")
        if not recorded:
            continue
        expected = classify_conflict(e["personas"], axes)
        if expected is None:
            continue
        if recorded not in _CONFLICT_TYPE_DOMAIN:
            # 値域外の ad-hoc な値（実例: converged_with_gate / converged_aufhebung）。
            # 分類の食い違いではなく記録の逸脱なので、閾値ずれと混ぜない
            out_of_domain.append({"invocation_id": e["invocation_id"], "recorded": recorded})
            continue
        if recorded == "unanimous" and expected == "reason_divergence":
            legacy += 1
            continue
        if recorded in _STANCE_AGREED and expected == "simple_conflict":
            normalization_gap.append({
                "invocation_id": e["invocation_id"],
                "recorded": recorded,
            })
            continue
        checked += 1
        if recorded != expected:
            threshold_mismatches.append({
                "invocation_id": e["invocation_id"],
                "recorded": recorded,
                "expected": expected,
            })
    return {
        "checked": checked,
        "legacy_unanimous_skipped": legacy,
        "threshold_mismatches": threshold_mismatches,
        "normalization_gap": normalization_gap,
        "out_of_domain": out_of_domain,
        "note": (
            "threshold_mismatches は分類器と本監査の DIMENSION_JACCARD_MAX のずれを示す。"
            "normalization_gap は stance 完全一致規則と実践の乖離を示し、options の記録で解消する"
        ),
    }


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


# ---- B7: 実行方式（execution_mode / degrade_reason）----------------------------
#
# （Council `council-2026-08-29T23:00:00Z-wfdflt`、案B = 記録 teeth）。
# 「原則 Workflow」を実効化するための**観測**であって強制ではない。本監査は WARN のみを出し、
# CI を落とさない（degrade は仕様 C-2 の正当な経路であり、潰すと機構が停止する）。
#
# 三値で扱う: workflow / manual / 欠落=unknown。**欠落を manual に畳まない**
# （workflow 側の記入漏れを degrade と誤認するため）。既存エントリへの遡及記入は禁止ゆえ、
# 導入前のエントリは恒久的に unknown のまま残る。degrade 率は宣言済み母集団でのみ算出する。

DEGRADE_RATE_MAX = 0.30          # 宣言済み母集団での degrade 率の警戒閾値
OBSERVATION_WINDOW = 10          # 再諮問の観測窓（SKILL.md §実行方式の「10 発動」と同値契約）
VALID_DEGRADE_REASONS = {
    "tool_unavailable",
    "judgment_failed",
    "pre_check_failed",
    "workflow_failed",
    "other",
}
# 実行基盤だけが書くフィールド。手動 degrade の自己申告を機械側から突合するための目印
# （2026-08-29 の実測で、この 3 フィールドの有無だけで実行方式を識別できることが確認済み。
#  components は persona_summary より深い字下げのため本パーサでは拾わず、残り 2 つを使う）
_WORKFLOW_ONLY_FIELDS = ("weight_calculation_retry_count", "confidence_band")


def _degrade_reason_key(raw: str | None) -> str | None:
    """degrade_reason の先頭列挙値だけを取り出す（後続の自由記述は集計に使わない）。"""
    if raw is None:
        return None
    v = raw.strip()
    if not v or v == "null":
        return None
    head = re.split(r"[\s:：（(]", v, maxsplit=1)[0].strip().strip('"')
    return head if head in VALID_DEGRADE_REASONS else "unlisted"


def audit_execution_mode(entries: list[dict]) -> dict:
    declared = {"workflow": 0, "manual": 0}
    unknown = 0
    reasons: dict[str, int] = {}
    mismatches: list[dict] = []
    manual_without_reason: list[str] = []

    for e in entries:
        mode = (e.get("execution_mode") or "").strip() or None
        # 機械推定: 実行基盤だけが書くフィールドが 1 つでもあれば workflow 由来とみなす
        estimated = "workflow" if any(f in e for f in _WORKFLOW_ONLY_FIELDS) else "manual"
        if mode not in declared:
            unknown += 1
            continue
        declared[mode] += 1
        if mode != estimated:
            mismatches.append(
                {"invocation_id": e["invocation_id"], "declared": mode, "estimated": estimated}
            )
        if mode == "manual":
            key = _degrade_reason_key(e.get("degrade_reason"))
            if key is None:
                manual_without_reason.append(e["invocation_id"])
            else:
                reasons[key] = reasons.get(key, 0) + 1

    declared_total = declared["workflow"] + declared["manual"]
    return {
        "entries_total": len(entries),
        "declared_total": declared_total,
        "workflow": declared["workflow"],
        "manual": declared["manual"],
        "unknown": unknown,
        # 宣言済み母集団でのみ算出。unknown を分母に入れると導入前エントリで恒久的に薄まる。
        # **閾値判定は丸め前の生値（_degrade_rate_raw）で行う** — 表示用に丸めた値で比較すると
        # 0.3004 → 0.300 のように境界直上が下振れして WARN を取り逃す
        # （council-fanout.workflow.mjs の tie 判定と同じ規律: 丸め前の生値で比べる）
        "degrade_rate": round(declared["manual"] / declared_total, 3) if declared_total else None,
        "_degrade_rate_raw": (declared["manual"] / declared_total) if declared_total else None,
        "degrade_reasons": reasons,
        "manual_without_reason": manual_without_reason,
        "declaration_mismatch": mismatches,
        "observation_window": OBSERVATION_WINDOW,
        "window_reached": declared_total >= OBSERVATION_WINDOW,
        "note": (
            "degrade 率は観測値であって権限の入力ではない（CTL 算出式・.council-ctl.json に接続しない）。"
            "unknown は導入前エントリまたは記入漏れ。遡及記入は禁止（推定を実測へ昇格させないため）"
        ),
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

    cls = result["classification"]
    L.append("## B6. conflict_type 分類の整合性（分類器 ⇄ 監査の閾値共有）")
    L.append("")
    L.append(f"- 照合 {cls['checked']} 件 / 閾値ずれ {len(cls['threshold_mismatches'])} 件")
    if cls["legacy_unanimous_skipped"]:
        L.append(
            f"- 遡及照合しない {cls['legacy_unanimous_skipped']} 件"
            "（v6.7.0 以前の `unanimous` は次元を問わない一致を意味した）"
        )
    for m in cls["threshold_mismatches"]:
        L.append(f"- {warn} `{m['invocation_id']}`: 記録 `{m['recorded']}` / 再計算 `{m['expected']}`")
    if cls["out_of_domain"]:
        L.append("")
        L.append(
            f"- {warn} **値域外の conflict_type {len(cls['out_of_domain'])} 件**: "
            + ", ".join(f"`{m['recorded']}`" for m in cls["out_of_domain"])
            + "。値域は `unanimous` / `reason_divergence` / `simple_conflict`"
            "（`output-format.md` §5）。ad-hoc な値は集計から静かに落ちる。"
        )
    if cls["normalization_gap"]:
        L.append("")
        L.append(
            f"- {warn} **正規化ギャップ {len(cls['normalization_gap'])} 件**: "
            "記録は stance 一致だが、完全一致で再計算すると `simple_conflict` になる。"
            "各軸が同じ選択肢に自分の条件を付記しているケース。"
            "**閾値の問題ではない** — `options` を §8 に記録すれば本監査も正規化でき解消する "
            "（`conflict-typology.md` §stance の正規化）。"
        )
        L.append(
            "  - 該当: "
            + ", ".join(f"`{m['invocation_id'][-8:]}`" for m in cls["normalization_gap"][:12])
            + ("…" if len(cls["normalization_gap"]) > 12 else "")
        )
    L.append("")

    ex = result["execution_mode"]
    L.append("## B7. 実行方式（既定 = Workflow / degrade の観測）")
    L.append("")
    L.append(
        f"- 宣言済み {ex['declared_total']} 件（workflow {ex['workflow']} / manual {ex['manual']}）"
        f" / 未宣言 unknown {ex['unknown']} 件"
        + (f" — degrade 率 {ex['degrade_rate']:.0%}" if ex["degrade_rate"] is not None else " — degrade 率は算出不能（宣言 0 件）")
    )
    if ex["degrade_reasons"]:
        L.append(
            "- degrade_reason 内訳: "
            + ", ".join(f"`{k}` {v} 件" for k, v in sorted(ex["degrade_reasons"].items()))
        )
    if ex["manual_without_reason"]:
        L.append("")
        L.append(
            f"- {warn} **degrade_reason 欠落の manual {len(ex['manual_without_reason'])} 件**: "
            "理由が無い degrade は「なぜ既定が使われなかったか」に答えず、観測値として使えない。"
            "列挙値（tool_unavailable / judgment_failed / pre_check_failed / workflow_failed / other）"
            "を先頭に置くこと（`output-format.md` §execution_mode の規約）。"
        )
    if ex["declaration_mismatch"]:
        L.append("")
        L.append(
            f"- {warn} **宣言と推定の乖離 {len(ex['declaration_mismatch'])} 件**: "
            "自己申告の `execution_mode` と、実行基盤だけが書くフィールド"
            f"（{' / '.join(f'`{f}`' for f in _WORKFLOW_ONLY_FIELDS)}）の有無から推定した値が食い違う。"
            "名ばかりの `workflow` 記入は観測値を汚す。"
        )
        L.append(
            "  - 該当: "
            + ", ".join(
                f"`{m['invocation_id'][-8:]}`（宣言 {m['declared']} / 推定 {m['estimated']}）"
                for m in ex["declaration_mismatch"][:12]
            )
            + ("…" if len(ex["declaration_mismatch"]) > 12 else "")
        )
    L.append("")
    L.append(
        f"> 観測窓は宣言済み {ex['observation_window']} 発動（現在 {ex['declared_total']} 件"
        f"{'・到達' if ex['window_reached'] else '・未到達'}）。到達時点、または 2026-10-31 の早い方で "
        "degrade 率と内訳を人間に提示する（`SKILL.md` §実行方式）。"
        "**degrade 率は観測値であって権限の入力ではない** — CTL 算出式にも `.council-ctl.json` にも接続しない（I-1）。"
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
    cls = result["classification"]
    if cls["threshold_mismatches"]:
        w.append(
            f"conflict_type の閾値ずれ {len(cls['threshold_mismatches'])} 件 — "
            "分類器（conflict-typology.md）と本監査の DIMENSION_JACCARD_MAX が不一致の可能性"
        )
    if cls["out_of_domain"]:
        w.append(
            f"値域外の conflict_type {len(cls['out_of_domain'])} 件 — "
            "ad-hoc な値は集計から静かに落ちる（output-format.md §5 の値域を使うこと）"
        )
    if cls["normalization_gap"]:
        w.append(
            f"正規化ギャップ {len(cls['normalization_gap'])} 件 — "
            "stance 完全一致では simple_conflict になる記録が stance 一致として残っている。"
            "options を §8 に記録すれば本監査も正規化できる（閾値の問題ではない）"
        )
    ex = result["execution_mode"]
    if ex["manual_without_reason"]:
        w.append(
            f"degrade_reason 欠落の manual {len(ex['manual_without_reason'])} 件 — "
            "理由なき degrade は原因究明装置として機能しない"
        )
    if ex["declaration_mismatch"]:
        w.append(
            f"execution_mode の宣言と推定の乖離 {len(ex['declaration_mismatch'])} 件 — "
            "自己申告が実行基盤フィールドの有無と食い違う"
        )
    if (
        ex["_degrade_rate_raw"] is not None
        and ex["declared_total"] >= OBSERVATION_WINDOW
        and ex["_degrade_rate_raw"] > DEGRADE_RATE_MAX   # 丸め前の生値で比較（境界の取り逃しを防ぐ）
    ):
        w.append(
            f"degrade 率 {ex['degrade_rate']:.0%}（宣言済み {ex['declared_total']} 件）が閾値 "
            f"{DEGRADE_RATE_MAX:.0%} 超 — 記録 teeth では起動が変わっていない。"
            "打つ手は CI FAIL 化ではなく起動経路の自動化（Council `wfdflt` 開発者 notes 3）"
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
        "classification": audit_classification(entries, axes),
        "execution_mode": audit_execution_mode(entries),
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
