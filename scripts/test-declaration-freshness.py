#!/usr/bin/env python3
"""宣言の鮮度の回帰テスト（v6.18.0 C-2 で検査 8 のテストから分離）。

合成リポジトリツリーに各欠陥を 1 つずつ仕込み、**検出することを実証する**。
「実リポで PASS した」だけでは検査が空振りしていないことを示せない。

合成ツリーを組む道具は `scripts/_verifier_fixture.py` に集約している（複製しない）。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _verifier_fixture import Fixture, FROZEN_HISTORY, build  # noqa: E402

_fx = Fixture("declaration_freshness")
check, scenario, OK_SPECS, HERE, m = (
    _fx.check, _fx.scenario, _fx.OK_SPECS, _fx.HERE, _fx.m)

print("== 健全なツリーでは 1 件も検出しない（空振りでない基準線） ==")
td, r = scenario(specs=OK_SPECS)
check("健全ツリー = 検出 0", r == [], str(r))
td.cleanup()

print("== 1. VERSION と GRAPH.yml の不一致 ==")
td, r = scenario(graph_version="6.12.0", specs=OK_SPECS)
check("不一致を FAIL で検出",
      any(i["severity"] == "FAIL" and "GRAPH.yml" in i["location"] for i in r), str(r))
td.cleanup()
td, r = scenario(graph_version=None, specs=OK_SPECS)
check("GRAPH.yml 不在は誤検知しない", r == [], str(r))
td.cleanup()

print("== 2. 状態行が値域外 ==")
td, r = scenario(specs=(("upgrade-spec-v6.17.0.md", "だいたい実装した", "本文"),))
check("値域外を FAIL で検出", any("値域外" in i["message"] for i in r), str(r))
td.cleanup()
for good in ("L0 起草（人間レビュー待ち）", "Council 諮問通過・人間の採否判定待ち",
             "実装中（F1 済 / F2 未）", "実装済み（PR #186、VERSION 6.15.0）",
             "破棄（Council 判定で不採用）"):
    td, r = scenario(specs=(("upgrade-spec-v6.14.0.md", good, "本文"),))
    check(f"値域内は通す: {good[:14]}…", all("値域外" not in i["message"] for i in r), str(r))
    td.cleanup()

print("== 3. 未 release の spec に状態行が無い ==")
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", None, "本文"),))
check("版 > VERSION で状態行欠落 = FAIL", any("状態行が無い" in i["message"] for i in r), str(r))
td.cleanup()
td, r = scenario(specs=(("upgrade-spec-v5.8.0.md", None, "本文"),))
check("版 <= VERSION の歴史的 spec には遡及しない（I-4）", r == [], str(r))
td.cleanup()

print("== 4. 実装済みを名乗る版が VERSION を超える ==")
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", "実装済み（PR #999、VERSION 6.16.0）", "本文"),))
check("超過を FAIL で検出", any("超えている" in i["message"] for i in r), str(r))
td.cleanup()

print("== 5. L0 起草のまま本文が実装を名乗る（file-local・WARN） ==")
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", "L0 起草（人間レビュー待ち）",
                         "> **実装済み（PR #248、2026-09-05）**: F7 を実装した。"),))
check("WARN で検出", any(i["severity"] == "WARN" for i in r), str(r))
td.cleanup()
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", "L0 起草（人間レビュー待ち）",
                         "実装の順序は L0 → L1 とする。"),))
check("実装を名乗らない本文では発火しない（偽陽性 0）", r == [], str(r))
td.cleanup()
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", "実装中（F7 済 / F1 未）",
                         "> **実装済み（PR #248）**: F7 を実装した。"),))
check("状態行を実態に直せば消える", r == [], str(r))
td.cleanup()

print("== 6. dev-env-spec §バージョン履歴 の凍結 ==")
td, r = scenario(specs=OK_SPECS,
                 history="### バージョン履歴\n\n- v1.0: 二層構想\n- v4.2: 第6条\n\n### 次章\n")
check("凍結マーカー欠落 = FAIL", any("凍結マーカー" in i["message"] for i in r), str(r))
td.cleanup()
td, r = scenario(specs=OK_SPECS, history=FROZEN_HISTORY.replace(
    "- v4.2: philosophy 第6条", "- v4.2: philosophy 第6条\n- v6.15: 版整合"))
check("v4.2 より後の追記 = FAIL（宣言の二重定義を防ぐ）",
      any("v4.2 より後" in i["message"] for i in r), str(r))
td.cleanup()

print("== 常時発火しないこと（I-4）: 実リポで WARN / FAIL が 0 件 ==")
graded = _fx.real()
check("実リポで検出 0 件（是正済み）", graded == [], str(graded))

_fx.finish()
