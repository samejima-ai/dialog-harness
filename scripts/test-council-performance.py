#!/usr/bin/env python3
"""council-performance.py の回帰テスト。

合成 COUNCIL-LOG フィクスチャ上で計測ロジックの正しさを検証する。
実ログには参照系の回帰 1 件でのみ触れる（値を固定しない）。

検証項目:
  1. パース: §8 ブロック形式のみを読む（見出し形式は数えない）
  2. normalize_consent: ctl-calculation.md §語尾語彙 の写像を再現する
  3. outcome: agreed_with_synthesis は CTL 上は成功だが本ツールでは非成功クラス
  4. agreement_rate（CTL 定義）と無修正採択率（厳格版）が同じログから別々に出る
  5. 負例 0 件のとき「下がる経路が無い」WARN を出す
  6. Brier / skill score: 完全予測器と無情報予測器で期待値どおりになる
  7. AUC: 完全分離で 1.0、逆転で 0.0、同値で 0.5
  8. キャリブレーション系統誤差の符号（過信が +）
  9. 記録率の低いフィールドを計測可能性の WARN として出す
 10. 終了コードは常に 0（warn のみ・block しない）

使い方: python3 scripts/test-council-performance.py
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("council_perf", HERE / "council-performance.py")
assert _spec and _spec.loader
perf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(perf)

_failures: list[str] = []
_passes = 0


def check(cond: bool, label: str) -> None:
    global _passes
    if cond:
        _passes += 1
    else:
        _failures.append(label)


def entry(iid: str, *, confidence=None, consent="agreed_recommended", conflict="unanimous",
          dcat="C2", cat="judgment", escalated=False, extra="") -> str:
    lines = [f'- invocation_id: "{iid}"', '  timestamp: "2026-01-01T00:00:00Z"']
    if cat:
        lines.append(f'  category: "{cat}"')
    if dcat:
        lines.append(f'  decision_category: "{dcat}"')
    if conflict:
        lines.append(f'  conflict_type: "{conflict}"')
    if confidence is not None:
        lines.append(f"  judgment_confidence: {confidence}")
    lines.append(f'  human_escalated: {"true" if escalated else "false"}')
    if consent is not None:
        lines.append(f'  implementer_consent: "{consent}"')
    if extra:
        lines.append(extra)
    return "\n".join(lines) + "\n"


def log_of(*entries: str) -> str:
    return "# COUNCIL-LOG\n\n## 見出し形式の記録（対象外であるべき）\n\n本文。\n\n" + "\n".join(entries)


# ---- 1. パース ----------------------------------------------------------------

parsed = perf.parse(log_of(entry("a"), entry("b")))
check(len(parsed) == 2, "1: §8 ブロック形式のみを数える（見出し形式を混入させない）")
check(parsed[0]["id"] == "a" and parsed[1]["id"] == "b", "1: invocation_id を順に読む")
check(perf.parse("# COUNCIL-LOG\n\n本文のみ\n") == [], "1: エントリ 0 件のログで空リストを返す")

# ---- 2. normalize_consent -----------------------------------------------------

cases = {
    "agreed_recommended": "agreed",
    "agreed": "agreed",
    "agreed_with_modification": "agreed_with_synthesis",
    "agreed_recommended_with_revision": "agreed_with_synthesis",
    "agreed_recommended_with_3_conditions": "agreed_with_synthesis",
    "agreed_with_caveat": "agreed_with_synthesis",
    "agreed_with_minority": "agreed_with_synthesis",
    "agreed_with_substitution": "modified",
    "agreed_with_override": "modified",
    "rejected": "rejected",
    "rejected_in_favor_of_b": "rejected",
    "escalated": "unevaluated",
    "deferred_to_next_wave": "unevaluated",
    None: "unrecorded",
}
for raw, want in cases.items():
    check(perf.normalize_consent(raw) == want, f"2: normalize_consent({raw!r}) → {want}")

# _substitution / _override は _with_ より優先される（骨格が動いた側に倒す）
check(perf.normalize_consent("agreed_recommended_with_substitution") == "modified",
      "2: **_substitution は _with_ より優先**（骨格の移動を with_synthesis に埋もれさせない）")

# ---- 3. outcome ---------------------------------------------------------------

check(perf.outcome({"consent": "agreed"}) == 1.0, "3: agreed は成功")
check(perf.outcome({"consent": "agreed_with_synthesis"}) == 0.0,
      "3: **agreed_with_synthesis は CTL 上は成功だが本ツールでは非成功**（判別力を残す）")
check(perf.outcome({"consent": "modified"}) == 0.0, "3: modified は非成功")
check(perf.outcome({"consent": "rejected"}) == 0.0, "3: rejected は非成功")
check(perf.outcome({"consent": "unevaluated"}) is None, "3: 未評価は母数から外す")
check(perf.outcome({"consent": "unrecorded"}) is None, "3: 未記録は母数から外す")

# ---- 4. 2 本の率が同じログから別々に出る --------------------------------------

m = perf.measure(perf.parse(log_of(
    entry("a", consent="agreed_recommended"),
    entry("b", consent="agreed_recommended"),
    entry("c", consent="agreed_with_modification"),
    entry("d", consent="agreed_with_modification"),
)))
check(m["ctl_agreement_rate"] == 1.0, "4: CTL 定義では 4/4 = 1.000")
check(m["strict_adoption_rate"] == 0.5, "4: 無修正採択率では 2/4 = 0.500")
check(m["ctl_pool"] == 4 and m["strict_pool"] == 4, "4: 母数は同じ（分子の定義だけが違う）")

# 未評価は両方の母数から落ちる
m_unev = perf.measure(perf.parse(log_of(
    entry("a", consent="agreed_recommended"), entry("b", consent="escalated"),
)))
check(m_unev["ctl_pool"] == 1 and m_unev["strict_pool"] == 1,
      "4: 未評価エントリは両方の母数から落ちる（合意を作っていないため）")

# ---- 5. 負例ゼロの WARN -------------------------------------------------------

many_agreed = perf.measure(perf.parse(log_of(*[entry(f"e{i}") for i in range(12)])))
check(many_agreed["ctl_negatives"] == 0, "5: 負例 0 件を数える")
check(any("負例 0 件" in w for w in perf.warnings_for(many_agreed)),
      "5: **負例 0 件かつ母数 10 以上で WARN**（指標に下がる経路が無い）")

few = perf.measure(perf.parse(log_of(*[entry(f"e{i}") for i in range(5)])))
check(not any("負例 0 件" in w for w in perf.warnings_for(few)),
      "5: 母数不足では負例ゼロで WARN しない（誤警報しない）")

with_neg = perf.measure(perf.parse(log_of(
    *[entry(f"e{i}") for i in range(11)], entry("z", consent="rejected"),
)))
check(not any("負例 0 件" in w for w in perf.warnings_for(with_neg)),
      "5: 負例が 1 件でもあれば WARN を出さない")

# ---- 6. Brier / skill score ---------------------------------------------------

perfect = perf.measure(perf.parse(log_of(
    entry("a", confidence=1.0, consent="agreed_recommended"),
    entry("b", confidence=0.0, consent="agreed_with_modification"),
)))
check(abs(perfect["calibration"]["brier"]) < 1e-9, "6: 完全予測器の Brier は 0")
check(perfect["calibration"]["skill_score"] == 1.0, "6: 完全予測器の skill score は 1.0")

flat = perf.measure(perf.parse(log_of(
    entry("a", confidence=0.5, consent="agreed_recommended"),
    entry("b", confidence=0.5, consent="agreed_with_modification"),
)))
check(abs(flat["calibration"]["skill_score"]) < 1e-9,
      "6: **ベースレートと同じ値を返す予測器の skill score は 0**（無情報の基準線）")

worse = perf.measure(perf.parse(log_of(
    entry("a", confidence=0.0, consent="agreed_recommended"),
    entry("b", confidence=1.0, consent="agreed_with_modification"),
)))
check(worse["calibration"]["skill_score"] < 0, "6: 逆向きの予測器は skill score が負")
check(any("skill score" in w for w in perf.warnings_for(worse)), "6: 負の skill score で WARN")

# ---- 7. AUC -------------------------------------------------------------------

check(perf.auc([0.9, 0.8], [0.4, 0.3]) == 1.0, "7: 完全分離で AUC 1.0")
check(perf.auc([0.3, 0.4], [0.8, 0.9]) == 0.0, "7: 完全逆転で AUC 0.0")
check(perf.auc([0.5, 0.5], [0.5, 0.5]) == 0.5, "7: 全同値で AUC 0.5（タイは 0.5 勝ち）")
check(perf.auc([], [0.5]) is None and perf.auc([0.5], []) is None,
      "7: 片側が空なら None（0 除算しない）")

# ---- 8. 系統誤差の符号 --------------------------------------------------------

over = perf.measure(perf.parse(log_of(
    entry("a", confidence=0.95, consent="agreed_recommended"),
    entry("b", confidence=0.95, consent="agreed_with_modification"),
)))
check(over["calibration"]["bias"] > 0, "8: **過信のとき bias は正**（平均 conf > 実測成功率）")
check(any("過信" in w for w in perf.warnings_for(over)), "8: 閾値超えの過信で WARN")

under = perf.measure(perf.parse(log_of(
    entry("a", confidence=0.30, consent="agreed_recommended"),
    entry("b", confidence=0.30, consent="agreed_recommended"),
)))
check(under["calibration"]["bias"] < 0, "8: 過小評価のとき bias は負")
check(any("過小評価" in w for w in perf.warnings_for(under)), "8: 閾値超えの過小評価で WARN")

# ---- 9. 記録率 ----------------------------------------------------------------

sparse = perf.measure(perf.parse(log_of(
    *[entry(f"e{i}", confidence=0.8, dcat=None) for i in range(10)],
)))
cov = {r["field"]: r for r in sparse["coverage"]}
check(cov["judgment_confidence"]["n"] == 10, "9: 記録済みフィールドの記録率は 100%")
check(cov["decision_category"]["n"] == 0, "9: 欠落フィールドの記録率は 0%")
check(any("decision_category" in w and "計測可能性" in w for w in perf.warnings_for(sparse)),
      "9: **低記録率は性能ではなく計測可能性の WARN として出す**")

# ---- 10. 終了コード -----------------------------------------------------------

with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "LOG.md"
    p.write_text(log_of(entry("a", confidence=0.1, consent="rejected")), encoding="utf-8")
    for extra in ([], ["--json"]):
        r = subprocess.run([sys.executable, str(HERE / "council-performance.py"), "--log", str(p), *extra],
                           capture_output=True, text=True)
        check(r.returncode == 0, f"10: WARN が出ても終了コード 0（{extra or '既定'}）")
    missing = subprocess.run([sys.executable, str(HERE / "council-performance.py"),
                              "--log", str(Path(td) / "none.md")], capture_output=True, text=True)
    check(missing.returncode == 0, "10: ログ不在でも終了コード 0（block しない）")
    empty = Path(td) / "empty.md"
    empty.write_text("# COUNCIL-LOG\n\n本文のみ\n", encoding="utf-8")
    r_empty = subprocess.run([sys.executable, str(HERE / "council-performance.py"), "--log", str(empty)],
                             capture_output=True, text=True)
    check(r_empty.returncode == 0, "10: エントリ 0 件でも終了コード 0")

# 実ログでの回帰: 値は固定せず、構造の整合のみ確認する
real_log = HERE.parent / "history" / "COUNCIL-LOG.md"
if real_log.is_file():
    rm = perf.measure(perf.parse(real_log.read_text(encoding="utf-8")))
    check(sum(rm["consents"].values()) == rm["n"], "実ログ: consent の内訳合計がエントリ総数に一致")
    check(rm["strict_pool"] <= rm["n"], "実ログ: 母数がエントリ総数を超えない")
    check(all(0.0 <= r["clean_adoption"] <= 1.0 for rows in rm["signals"].values() for r in rows),
          "実ログ: 全シグナル群の率が [0,1] に収まる")

# ---- 結果 ---------------------------------------------------------------------

print(f"passed: {_passes}")
if _failures:
    for f in _failures:
        print(f"FAIL: {f}", file=sys.stderr)
    raise SystemExit(1)
print("ALL PASS")
