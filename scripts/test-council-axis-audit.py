#!/usr/bin/env python3
"""council-axis-audit.py の回帰テスト。

合成 COUNCIL-LOG / council-weights フィクスチャ上で検査ロジックの正しさを検証する。
実ログ・実 council-weights には一切触れない。

検証項目:
  1. パース: persona_summary のインライン mapping から stance/confidence/dimension を抽出
  2. B1 の中核契約: stance 一致率が高くても dimension が分離していれば冗長判定しない
  3. B1: stance 一致率と dimension Jaccard の両方が閾値超えのときのみ冗長判定
  4. B2: 軸内 confidence の σ が閾値未満なら固定を検出、散っていれば検出しない
  5. B3: 実効配分の乖離はゼロサム。warn は「得ている軸」のみ
  6. B3: situational_modifier の合計 0 宣言違反を検出
  7. B5: dimension 記録率の算出
  8. 終了コードは常に 0（warn のみ・block しない）

使い方: python3 scripts/test-council-axis-audit.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("axis_audit", HERE / "council-axis-audit.py")
assert _spec and _spec.loader
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)

AXES = ["経営者", "開発者", "哲学者"]
_failures: list[str] = []
_passes = 0


def check(cond: bool, label: str) -> None:
    global _passes
    if cond:
        _passes += 1
    else:
        _failures.append(label)


def entry(inv: str, rows: list[tuple[str, str, float, str | None]]) -> str:
    """COUNCIL-LOG の 1 エントリを組む。rows = [(軸, stance, confidence, dimension|None)]"""
    lines = [f'- invocation_id: "{inv}"', '  timestamp: "2026-07-26T00:00:00Z"', "  persona_summary:"]
    for ax, stance, conf, dim in rows:
        body = f'stance: "{stance}", confidence: {conf}'
        if dim is not None:
            body += f', dimension: "{dim}"'
        lines.append(f"    {ax}: {{ {body} }}")
    lines.append('  recommended: "x"')
    return "\n".join(lines)


WEIGHTS_FIXTURE = """# fixture

```yaml
base_weights:
  business:
    経営者: 3
    開発者: 4
    哲学者: 3
```

```yaml
ethos_multiplier:
  business:
    経営者: 1.0
    開発者: 1.0
    哲学者: 1.0
```

```yaml
situational_modifier:
  implementation:   # 行末コメント付き（実ファイルと同形）
    経営者: -1
    開発者: +2
    哲学者: -1
  skewed:           # 合計 +1 の宣言違反ケース
    経営者: +1
    開発者: 0
    哲学者: 0
```
"""


# ---- 1. パース -----------------------------------------------------------------

log = "\n".join([
    entry("c-1", [("経営者", "案A", 0.7, "ROI"), ("開発者", "案A", 0.9, "保守性"), ("哲学者", "案B", 0.5, "意味")]),
    entry("c-2", [("経営者", "案A", 0.6, "機会損失"), ("開発者", "案A", 0.8, "可逆性"), ("哲学者", "第3の道", 0.6, "前提への問い")]),
])
entries = audit.parse_entries(log)
check(len(entries) == 2, "1: エントリ数 2")
check(entries[0]["personas"]["経営者"]["stance"] == "案A", "1: stance 抽出")
check(entries[0]["personas"]["開発者"]["confidence"] == 0.9, "1: confidence 抽出")
check(entries[0]["personas"]["哲学者"]["dimension"] == "意味", "1: dimension 抽出")
check(entries[0]["invocation_id"] == "c-1", "1: invocation_id 抽出")

# ---- 2. B1 の中核契約: 一致率が高くても dimension が分離していれば冗長ではない ----
# 経営者と開発者は 4/4 で stance 一致（100% > 0.65）だが dimension は完全分離
log_disjoint = "\n".join([
    entry(f"d-{i}", [
        ("経営者", "案A", 0.7, "ROI / 機会損失"),
        ("開発者", "案A", 0.9, "保守性 / 可逆性"),
        ("哲学者", "案B", 0.5, "意味"),
    ]) for i in range(4)
])
r = audit.audit_axis_independence(audit.parse_entries(log_disjoint), AXES)
pair = r["経営者⇄開発者"]
check(pair["stance_agreement"] == 1.0, "2: stance 一致率 100%")
check(pair["dimension_jaccard"] == 0.0, "2: dimension Jaccard 0.0")
check(pair["redundancy_suspected"] is False,
      "2: **一致率 100% でも dimension 分離なら冗長判定しない**（本ツールの中核契約）")

# ---- 3. B1: 両方が閾値超えのときのみ冗長判定 -----------------------------------
log_overlap = "\n".join([
    entry(f"o-{i}", [
        ("経営者", "案A", 0.7, "ROI / 保守性"),
        ("開発者", "案A", 0.9, "ROI / 保守性"),   # 語彙が完全一致 → Jaccard 1.0
        ("哲学者", "案B", 0.5, "意味"),
    ]) for i in range(4)
])
r2 = audit.audit_axis_independence(audit.parse_entries(log_overlap), AXES)
check(r2["経営者⇄開発者"]["dimension_jaccard"] == 1.0, "3: 語彙一致で Jaccard 1.0")
check(r2["経営者⇄開発者"]["redundancy_suspected"] is True, "3: 2 指標とも閾値超えで冗長判定")
check(r2["経営者⇄哲学者"]["redundancy_suspected"] is False, "3: 一致率が低いペアは冗長判定しない")

# dimension が無い場合は判定を保留（stance だけで冗長と言わない）
log_nodim = "\n".join([
    entry(f"n-{i}", [("経営者", "案A", 0.7, None), ("開発者", "案A", 0.9, None), ("哲学者", "案A", 0.5, None)])
    for i in range(4)
])
r3 = audit.audit_axis_independence(audit.parse_entries(log_nodim), AXES)
check(r3["経営者⇄開発者"]["dimension_jaccard"] is None, "3: dimension 不在なら Jaccard は None")
check(r3["経営者⇄開発者"]["redundancy_suspected"] is False,
      "3: dimension 不在なら stance 一致 100% でも冗長判定を保留")

# ---- 4. B2: confidence の固定検出 ---------------------------------------------
log_pinned = "\n".join([
    entry(f"p-{i}", [
        ("経営者", "案A", 0.70 + (i % 2) * 0.01, "ROI"),   # σ ≈ 0.005 → 固定
        ("開発者", "案A", 0.3 + i * 0.2, "保守性"),          # σ 大 → 固定でない
        ("哲学者", "案B", 0.5, "意味"),
    ]) for i in range(4)
])
c = audit.audit_confidence_spread(audit.parse_entries(log_pinned), AXES)
check(c["経営者"]["pinned_suspected"] is True, "4: σ 小で固定を検出")
check(c["開発者"]["pinned_suspected"] is False, "4: σ 大なら固定を検出しない")
check(c["経営者"]["n"] == 4 and c["経営者"]["distinct_values"] == 2, "4: n と相異値の集計")

# ---- 5/6. B3: 実効配分とゼロサム、宣言違反の検出 -------------------------------
with tempfile.TemporaryDirectory() as td:
    wpath = Path(td) / "council-weights.md"
    wpath.write_text(WEIGHTS_FIXTURE, encoding="utf-8")
    # 開発者の confidence だけ高い → 開発者が系統的に有利になる
    conf = {"経営者": {"mean": 0.70}, "開発者": {"mean": 0.90}, "哲学者": {"mean": 0.65}}
    eff = audit.audit_effective_weights(wpath, conf, AXES)
    check("error" not in eff, "5: 行末コメント付き親キーをパースできる")
    drifts = {ax: eff["summary"][ax]["mean_drift_pt"] for ax in AXES}
    check(abs(sum(drifts.values())) < 0.05, "5: 乖離の合計は 0（ゼロサム）")
    check(drifts["開発者"] > 0, "5: 高 confidence の軸が実効配分で有利になる")
    check(eff["summary"]["開発者"]["systematic_bias_suspected"] is True, "5: 得ている軸を warn")
    check(eff["summary"]["哲学者"]["systematic_bias_suspected"] is False,
          "5: **失っている軸は warn しない**（ゼロサムの裏面ゆえ重複報告を避ける）")
    check(eff["per_category"]["implementation"]["modifier_sum"] == 0, "6: 合計 0 のカテゴリ")
    check(eff["per_category"]["skewed"]["modifier_sum"] == 1, "6: 合計 +1 の宣言違反を検出")
    check(eff["per_category"]["skewed"]["sum_weight"] == 11, "6: 宣言違反時 ΣW が 11 になる")

    # ---- 7/8. 統合実行: 記録率と終了コード -----------------------------------
    lpath = Path(td) / "LOG.md"
    lpath.write_text(log_disjoint + "\n" + log_nodim, encoding="utf-8")
    cov = audit.audit_dimension_coverage(audit.parse_entries(lpath.read_text(encoding="utf-8")), AXES)
    check(cov["all_axes_stance"] == 8, "7: 全軸 stance の件数")
    check(cov["all_axes_dimension"] == 4, "7: 全軸 dimension の件数")
    check(cov["dimension_record_rate"] == 0.5, "7: 記録率 = 4/8")

    # main() の標準出力はテスト結果を埋もれさせるので捨てる（終了コードだけ検証する）
    with contextlib.redirect_stdout(io.StringIO()):
        rc = audit.main(["--log", str(lpath), "--weights", str(wpath), "--json"])
        rc_text = audit.main(["--log", str(lpath), "--weights", str(wpath)])
        rc_missing = audit.main(["--log", str(Path(td) / "absent.md")])
    check(rc == 0, "8: warn があっても終了コード 0（--json）")
    check(rc_text == 0, "8: warn があっても終了コード 0（レポート形式）")
    check(rc_missing == 0, "8: ログ不在でも終了コード 0（利用者プロジェクトで壊れない）")

# ---- 結果 ---------------------------------------------------------------------

print(f"passed: {_passes}")
if _failures:
    for f in _failures:
        print(f"FAIL: {f}", file=sys.stderr)
    raise SystemExit(1)
print("ALL PASS")
