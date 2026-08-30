#!/usr/bin/env python3
"""council-performance — COUNCIL-LOG.md から判定支援機構の「性能」を決定論で測る。

`scripts/council-axis-audit.py` の双対。axis-audit が **入力側**（3 軸が独立に観測
できているか）を測るのに対し、本ツールは **出力側**（出た判定がその後どうなったか）
を測る。

## なぜ必要か

Council には結果側の指標が `agreement_rate`（CTL 算出の入力）1 本しかなく、
それは v6.12.0 で分子が `agreed + agreed_with_synthesis` に拡張された結果、
**負例が構造的にほぼ空**になっている。実測（2026-08-30）で判明したのは:

- 67 発動中 `rejected` が 0 件、`modified`（骨格差し替え）も 0 件
  → CTL 定義の agreement_rate = 100%。**下がる経路が事実上存在しない**
- したがって agreement_rate は「機構が良い」ことの証拠にならない。
  自律権限（CTL）の入力がこれ 1 本なのは、常に 1 を返す関数で昇格を決めるに等しい

本ツールは同じログから **判別力のある**指標を取る:

- `judgment_confidence` を予測、「無修正で採られたか」を結果とした
  **Brier score / skill score / AUC / 信頼度ビン別実測**
- 事前シグナル（`conflict_type` / `human_escalated` / `decision_category`）が
  結果を予測するか（＝ 機構が自分の弱い判定を事前に見分けられているか）
- 記録の完全性（測れないフィールドは性能の欠落ではなく**計測可能性**の欠落）

## 測っていないもの（重要）

`implementer_consent` は **正解ではなく受容**である。判定が現実に妥当だったかを
記録する field はログに存在しない。したがって本ツールが出すのは
**「機構の推奨が採られる率」と「自信の当たり具合」**であって、判断の正しさではない。
この区別を消すと、合意率の高さを精度の高さと読み違える（`agreement_rate` が
まさにその形で使われている）。

**本ツールは LLM 判定を一切含まない。** 集計のみで行い、判断は人間（D5）に残す。

## 使い方

    python3 scripts/council-performance.py                      # 既定ログを計測
    python3 scripts/council-performance.py --log path/to/LOG.md # ログを指定
    python3 scripts/council-performance.py --json               # 機械可読出力

終了コードは常に 0（warn のみ・block しない。philosophy.md 第6条 人間最終承認）。
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

DEFAULT_LOG = Path(__file__).resolve().parent.parent / "history" / "COUNCIL-LOG.md"

# ---- 閾値 ---------------------------------------------------------------

# confidence の系統誤差（平均 confidence − 実測成功率）がこれを超えると過信/過小の疑い
CALIBRATION_BIAS_MAX = 0.10
# AUC がこれを下回ると judgment_confidence が結果を判別していない疑い
AUC_MIN = 0.60
# skill score（ベースレート予測器に対する Brier の改善率）がこれを下回ると警告
SKILL_SCORE_MIN = 0.0
# 必須フィールドの記録率がこれを下回ると計測可能性の警告
COVERAGE_MIN = 0.80

# CTL 算出が使う agreement_rate の分子（ctl-calculation.md §status の 4 値）
CTL_AGREED_STATUSES = {"agreed", "agreed_with_synthesis"}


# ---- パース -------------------------------------------------------------


def split_entries(text: str) -> list[str]:
    """§8 ブロック形式（`- invocation_id:` 始まり）のみを読む。見出し形式は対象外。"""
    return re.split(r"^(?=- invocation_id:)", text, flags=re.M)[1:]


def scalar(block: str, name: str) -> str | None:
    m = re.search(rf"^  {re.escape(name)}:\s*(.*)$", block, re.M)
    if not m:
        return None
    v = re.sub(r"\s+#.*$", "", m.group(1)).strip().strip('"').strip("'")
    return None if v in ("", "null", "None") else v


def number(block: str, name: str) -> float | None:
    v = scalar(block, name)
    if v is None:
        return None
    m = re.match(r"-?\d+(?:\.\d+)?", v)
    return float(m.group(0)) if m else None


def normalize_consent(raw: str | None) -> str:
    """implementer_consent の語尾語彙を ctl-calculation.md §語尾語彙 に従って正規化する。

    返す 4 値は CTL の status と同じ語彙。`agreed_with_synthesis` は
    「骨格は採ったが何かを足した」であり、CTL 上は成功に算入されるが、
    本ツールは **無修正採択とは別クラス**として扱う（判別力を残すため）。
    """
    if raw is None:
        return "unrecorded"
    v = raw.strip()
    if v.startswith("rejected"):
        return "rejected"
    if v.startswith(("escalated", "deferred")):
        return "unevaluated"
    if re.search(r"_(substitution|override)", v):
        return "modified"
    if re.search(r"_(with_|under_|condition|caveat|minority|modification|follow_up|revision)", v):
        return "agreed_with_synthesis"
    if v.startswith("agreed"):
        return "agreed"
    return "unrecorded"


def invocation_id(block: str) -> str | None:
    """`- invocation_id:` は 2 スペース字下げでない先頭行にあるため scalar() では読めない。"""
    m = re.match(r"- invocation_id:\s*(.*)", block)
    if not m:
        return None
    v = re.sub(r"\s+#.*$", "", m.group(1)).strip().strip('"').strip("'")
    return v or None


def parse(text: str) -> list[dict]:
    out = []
    for b in split_entries(text):
        raw_consent = scalar(b, "implementer_consent")
        out.append(
            {
                "id": invocation_id(b),
                "timestamp": scalar(b, "timestamp"),
                "agreed_at": scalar(b, "agreed_at"),
                "category": scalar(b, "category"),
                "decision_category": scalar(b, "decision_category"),
                "conflict_type": scalar(b, "conflict_type"),
                "confidence": number(b, "judgment_confidence"),
                "escalated": scalar(b, "human_escalated") == "true",
                "consent": normalize_consent(raw_consent),
                "minority": scalar(b, "minority_opinion") is not None,
                "follow_ups": number(b, "follow_up_questions_count"),
                "has_persona": "persona_summary" in b,
                "has_dimension": "dimension:" in b,
                "has_options": scalar(b, "options") is not None,
                "execution_mode": scalar(b, "execution_mode"),
            }
        )
    return out


# ---- 指標 ---------------------------------------------------------------


def outcome(e: dict) -> float | None:
    """無修正採択 = 1 / 何かを足した・差し替えた・却下 = 0 / 未評価 = None。"""
    if e["consent"] == "agreed":
        return 1.0
    if e["consent"] in ("agreed_with_synthesis", "modified", "rejected"):
        return 0.0
    return None


def auc(pos: list[float], neg: list[float]) -> float | None:
    if not pos or not neg:
        return None
    wins = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in pos for b in neg)
    return wins / (len(pos) * len(neg))


def rate(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "n/a"


def measure(entries: list[dict]) -> dict:
    n = len(entries)
    consents = Counter(e["consent"] for e in entries)

    # --- CTL 定義の agreement_rate（比較のため同じログから再計算する） ---
    ctl_pool = [e for e in entries if e["consent"] in CTL_AGREED_STATUSES | {"modified", "rejected"}]
    ctl_agreed = [e for e in ctl_pool if e["consent"] in CTL_AGREED_STATUSES]
    ctl_rate = len(ctl_agreed) / len(ctl_pool) if ctl_pool else None
    ctl_negatives = len(ctl_pool) - len(ctl_agreed)

    # --- 厳格版（無修正採択のみを成功とする） ---
    scored = [e for e in entries if outcome(e) is not None]
    strict_rate = sum(outcome(e) for e in scored) / len(scored) if scored else None

    # --- キャリブレーション ---
    cal = [e for e in scored if e["confidence"] is not None]
    calib = None
    if cal:
        base = sum(outcome(e) for e in cal) / len(cal)
        brier = sum((e["confidence"] - outcome(e)) ** 2 for e in cal) / len(cal)
        brier_base = sum((base - outcome(e)) ** 2 for e in cal) / len(cal)
        pos = [e["confidence"] for e in cal if outcome(e) == 1.0]
        neg = [e["confidence"] for e in cal if outcome(e) == 0.0]
        bins = []
        for lo, hi in [(0.0, 0.70), (0.70, 0.80), (0.80, 0.90), (0.90, 1.01)]:
            g = [e for e in cal if lo <= e["confidence"] < hi]
            if g:
                bins.append(
                    {
                        "lo": lo,
                        "hi": min(hi, 1.0),
                        "n": len(g),
                        "predicted": statistics.mean(e["confidence"] for e in g),
                        "observed": sum(outcome(e) for e in g) / len(g),
                    }
                )
        calib = {
            "n": len(cal),
            "base_rate": base,
            "mean_confidence": statistics.mean(e["confidence"] for e in cal),
            "bias": statistics.mean(e["confidence"] for e in cal) - base,
            "brier": brier,
            "brier_baseline": brier_base,
            "skill_score": (1 - brier / brier_base) if brier_base else None,
            "auc": auc(pos, neg),
            "bins": bins,
        }

    # --- 事前シグナルの予測力 ---
    def by(keyfn) -> list[dict]:
        groups: dict[str, list[dict]] = {}
        for e in scored:
            groups.setdefault(str(keyfn(e)), []).append(e)
        rows = []
        for k, g in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            cf = [e["confidence"] for e in g if e["confidence"] is not None]
            rows.append(
                {
                    "value": k,
                    "n": len(g),
                    "clean_adoption": sum(outcome(e) for e in g) / len(g),
                    "mean_confidence": statistics.mean(cf) if cf else None,
                }
            )
        return rows

    signals = {
        "conflict_type": by(lambda e: e["conflict_type"] or "(未記録)"),
        "human_escalated": by(lambda e: "escalated" if e["escalated"] else "auto"),
        "decision_category": by(lambda e: e["decision_category"] or "(未記録)"),
        "category": by(lambda e: e["category"] or "(未記録)"),
        "minority_opinion": by(lambda e: "あり" if e["minority"] else "なし"),
    }

    # --- リードタイム ---
    lead = []
    for e in entries:
        if e["timestamp"] and e["agreed_at"]:
            try:
                a = datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
                b = datetime.fromisoformat(e["agreed_at"].replace("Z", "+00:00"))
            except ValueError:
                continue
            delta = (b - a).total_seconds() / 60
            if delta >= 0:
                lead.append(delta)

    # --- 記録の完全性 ---
    fields = [
        ("judgment_confidence", lambda e: e["confidence"] is not None),
        ("decision_category", lambda e: e["decision_category"] is not None),
        ("conflict_type", lambda e: e["conflict_type"] is not None),
        ("persona_summary", lambda e: e["has_persona"]),
        ("dimension", lambda e: e["has_dimension"]),
        ("options", lambda e: e["has_options"]),
        ("execution_mode", lambda e: e["execution_mode"] is not None),
        ("timestamp", lambda e: e["timestamp"] is not None),
    ]
    coverage = [{"field": f, "n": sum(1 for e in entries if fn(e)), "total": n} for f, fn in fields]

    return {
        "n": n,
        "consents": dict(consents),
        "ctl_agreement_rate": ctl_rate,
        "ctl_pool": len(ctl_pool),
        "ctl_negatives": ctl_negatives,
        "strict_adoption_rate": strict_rate,
        "strict_pool": len(scored),
        "calibration": calib,
        "signals": signals,
        "lead_time": {
            "n": len(lead),
            "median_min": statistics.median(lead) if lead else None,
            "within_24h": sum(1 for x in lead if x < 1440) / len(lead) if lead else None,
        },
        "coverage": coverage,
    }


def warnings_for(m: dict) -> list[str]:
    w = []
    if m["ctl_negatives"] == 0 and m["ctl_pool"] >= 10:
        w.append(
            f"CTL の agreement_rate が負例 0 件で {rate(m['ctl_pool'], m['ctl_pool'])} — "
            "下がる経路が構造的に存在しない。自律権限（CTL）の唯一の入力がこの指標であることを人間が確認すること"
        )
    c = m["calibration"]
    if c:
        if abs(c["bias"]) > CALIBRATION_BIAS_MAX:
            direction = "過信" if c["bias"] > 0 else "過小評価"
            w.append(f"judgment_confidence の系統誤差 {c['bias']:+.3f}（{direction}の疑い）")
        if c["auc"] is not None and c["auc"] < AUC_MIN:
            w.append(
                f"judgment_confidence の判別力 AUC={c['auc']:.3f} < {AUC_MIN} — "
                "自信が結果を予測していない（帯指定の産物の疑い）"
            )
        if c["skill_score"] is not None and c["skill_score"] < SKILL_SCORE_MIN:
            w.append(
                f"skill score {c['skill_score']:+.3f} — 常にベースレートを答える予測器に劣る"
            )
    for row in m["coverage"]:
        if row["total"] and row["n"] / row["total"] < COVERAGE_MIN:
            w.append(
                f"{row['field']} の記録率 {rate(row['n'], row['total'])} < {int(COVERAGE_MIN*100)}% — "
                "性能ではなく計測可能性の欠落"
            )
    return w


# ---- 出力 ---------------------------------------------------------------


def render(m: dict, log: Path) -> str:
    L: list[str] = []
    p = L.append
    p("# Council 判定支援機構 性能計測")
    p("")
    p(f"- ログ: `{log}`")
    p(f"- §8 ブロック形式エントリ {m['n']} 件（見出し形式の記録は対象外）")
    p("")

    p("## P1. 採択（結果側の唯一の観測）")
    p("")
    p("| implementer_consent（正規化） | 件数 | 比率 |")
    p("|---|---|---|")
    for k, v in sorted(m["consents"].items(), key=lambda kv: -kv[1]):
        p(f"| {k} | {v} | {rate(v, m['n'])} |")
    p("")
    if m["ctl_agreement_rate"] is not None:
        p(
            f"- **CTL 定義の agreement_rate = {m['ctl_agreement_rate']:.3f}**"
            f"（分子 = agreed + agreed_with_synthesis、母数 {m['ctl_pool']} 件、負例 {m['ctl_negatives']} 件）"
        )
    if m["strict_adoption_rate"] is not None:
        p(
            f"- **無修正採択率 = {m['strict_adoption_rate']:.3f}**"
            f"（骨格に何も足されずそのまま採られた率、母数 {m['strict_pool']} 件）"
        )
    p("")
    p(
        "> この 2 本は同じログの同じ field から出る。**乖離の大きさがそのまま"
        "「agreement_rate が何を測っていないか」の量**である。"
        "`implementer_consent` は受容の記録であって正解の記録ではない — "
        "判定が現実に妥当だったかを保持する field はログに存在しない。"
    )
    p("")

    c = m["calibration"]
    if c:
        p("## P2. キャリブレーション（judgment_confidence は当たっているか）")
        p("")
        p(f"- 対象 {c['n']} 件 / 実測ベースレート {c['base_rate']:.3f}")
        p(
            f"- 平均 confidence {c['mean_confidence']:.3f} → **系統誤差 {c['bias']:+.3f}**"
            f"（閾値 ±{CALIBRATION_BIAS_MAX}）"
        )
        skill = (
            f" → skill score **{c['skill_score']:+.3f}**"
            if c["skill_score"] is not None
            else " → skill score: 算出不能（結果が一方向に揃いベースレート予測器の Brier が 0）"
        )
        p(f"- Brier score **{c['brier']:.4f}** / ベースレート予測器 {c['brier_baseline']:.4f}{skill}")
        if c["auc"] is not None:
            p(f"- 判別力 **AUC = {c['auc']:.3f}**（0.5 = ランダム、閾値 {AUC_MIN}）")
        else:
            p("- 判別力 AUC: 算出不能（成功群と非成功群のどちらかが空）")
        p("")
        p("| confidence ビン | n | 予測平均 | 実測無修正採択率 |")
        p("|---|---|---|---|")
        for b in c["bins"]:
            p(f"| {b['lo']:.2f}–{b['hi']:.2f} | {b['n']} | {b['predicted']:.3f} | {b['observed']:.3f} |")
        p("")

    p("## P3. 事前シグナルは結果を予測するか")
    p("")
    p(
        "> 「機構が自分の弱い判定を事前に見分けられているか」を測る。"
        "見分けられているなら、シグナル間で無修正採択率が分かれる。"
    )
    labels = {
        "conflict_type": "conflict_type（対立類型）",
        "human_escalated": "human_escalated（人間へ上げたか）",
        "decision_category": "decision_category（委譲軸）",
        "category": "category（重み軸）",
        "minority_opinion": "minority_opinion の有無",
    }
    for key, rows in m["signals"].items():
        p("")
        p(f"**{labels.get(key, key)}**")
        p("")
        p("| 値 | n | 無修正採択率 | 平均 confidence |")
        p("|---|---|---|---|")
        for r in rows:
            mc = f"{r['mean_confidence']:.3f}" if r["mean_confidence"] is not None else "–"
            p(f"| {r['value']} | {r['n']} | {r['clean_adoption']:.3f} | {mc} |")
    p("")

    lt = m["lead_time"]
    if lt["n"]:
        p("## P4. 所要")
        p("")
        p(
            f"- 判定 → 合意 リードタイム n={lt['n']} / 中央値 {lt['median_min']:.0f} 分 / "
            f"24 時間以内 {lt['within_24h'] * 100:.1f}%"
        )
        p("")

    p("## P5. 計測可能性（記録の完全性）")
    p("")
    p("| フィールド | 記録率 |")
    p("|---|---|")
    for row in m["coverage"]:
        p(f"| {row['field']} | {rate(row['n'], row['total'])} ({row['n']}/{row['total']}) |")
    p("")
    p(
        "> 記録率の低いフィールドは、機構の性能が低いのではなく**性能を測る手段が無い**ことを示す。"
        "是正は記録側（`output-format.md` §8）に対して行う。"
    )
    p("")

    p("## 総括")
    p("")
    w = warnings_for(m)
    if w:
        for x in w:
            p(f"- WARN: {x}")
    else:
        p("- WARN なし")
    p("")
    p(
        "> 本計測は集計のみで LLM 判定を含まない。**是正の判断は人間（D5）に残る**"
        "（philosophy.md 第6条）。指標定義の変更は L0 対話を経ること。"
    )
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="COUNCIL-LOG から判定支援機構の性能を測る")
    ap.add_argument("--log", type=Path, default=DEFAULT_LOG, help="COUNCIL-LOG.md のパス")
    ap.add_argument("--json", action="store_true", help="機械可読出力")
    args = ap.parse_args()

    if not args.log.exists():
        print(f"ログが見つかりません: {args.log}", file=sys.stderr)
        return 0

    entries = parse(args.log.read_text(encoding="utf-8"))
    if not entries:
        print(f"§8 ブロック形式のエントリが 0 件です: {args.log}", file=sys.stderr)
        return 0

    m = measure(entries)
    if args.json:
        print(json.dumps({**m, "warnings": warnings_for(m)}, ensure_ascii=False, indent=2))
    else:
        print(render(m, args.log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
