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

print("== 5b. 実装側の着地主張 ⇄ spec の状態行（v6.18.0 C-4） ==")
# 検査 5 は spec 自身の本文しか見ないため、着地の主張が実装側にあると素通りする。
# 実測（2026-09-07）: v6.13.0 F5 は norm-scan.py として着地済みなのに状態行は `L0 起草` のままで、
# 既存 11 検査のどれも検出しなかった。

DRAFT = (("upgrade-spec-v6.16.0.md", "L0 起草（人間レビュー待ち）", "本文"),)
LANDED = ("scripts/norm-scan.py", '"""走査器（v6.16.0 F5 / v6.18.0 C-1 で着地）。"""\n')

td, r = scenario(specs=DRAFT, source_docs=(LANDED,))
check("draft の spec の着地を実装側が名乗ったら WARN",
      any(i["severity"] == "WARN" and "着地を名乗っている" in i["message"] for i in r), str(r))
td.cleanup()

# 状態行を実態に直せば消える（= 是正で 0 になる。I-1「是正と検査は同一 PR」が成立する形）
td, r = scenario(specs=(("upgrade-spec-v6.16.0.md", "実装中（F5 済 / F1-F4 未）", "本文"),),
                 source_docs=(LANDED,))
check("状態行を実態に直せば消える", r == [], str(r))
td.cleanup()

# 偽陽性を出さない条件（緩い正規表現だと拾ってしまうもの）
for label, body in (
    ("単なる引用（同旨）", '# v6.16.0 F2 公開安全と同旨\n'),
    ("項番の引用のみ", '    lines.append("判定はしない（v6.16.0 F5-3）")\n'),
    ("予定の記述", '# v6.16.0 F5 は次サイクルで実装する予定\n'),
):
    td, r = scenario(specs=DRAFT, source_docs=(("scripts/x.py", body),))
    check(f"偽陽性を出さない: {label}", r == [], str(r))
    td.cleanup()

# 設計文書側の記述は対象外（dh-upgrades / delivery / history では参照が正常に現れる）
td, r = scenario(specs=DRAFT,
                 source_docs=(("delivery/ANALYSIS-x.md", "v6.16.0 F5 で着地した\n"),))
check("設計文書（delivery/）の記述は対象外", r == [], str(r))
td.cleanup()

# 状態行が draft でない版の着地主張は無視する
td, r = scenario(version="6.16.0", graph_version="6.16.0",
                 specs=(("upgrade-spec-v6.16.0.md", "実装済み（PR #1、VERSION 6.16.0）", "本文"),),
                 source_docs=(LANDED,))
check("実装済みを名乗る spec には発火しない", r == [], str(r))
td.cleanup()

print("== 走査面の欠落を「静かな PASS」にしない（v6.18.0 C-4） ==")
# 実測（2026-09-07）: DH 本体で GRAPH.yml を消すと 6 検査が 1 件も出さずに --strict が
# exit 0 で通っていた。検査が守っているはずのものを消しても緑になるなら、その緑は
# 何も保証していない。v6.13.0 I-4「検出器は黙って捨てない」の自己適用。
#
# 一方 I-6（配布先など機構を持たないツリーで壊れない）は維持する必要がある。
# ゆえに DH 本体では FAIL、配布先では METRIC skip、という二段で検証する。

for what, kw in (
    ("GRAPH.yml", dict(graph_version=None, specs=OK_SPECS)),
    ("dh-upgrades/", dict(upgrades_dir=False)),
):
    td, r = scenario(dh_core=True, **kw)
    check(f"DH 本体で {what} が無ければ FAIL",
          any(i["severity"] == "FAIL" and "走査面を確保できなかった" in i["message"] for i in r), str(r))
    td.cleanup()
    td, r = scenario(dh_core=False, **kw)
    check(f"配布先で {what} が無くても誤検知しない（I-6 維持）", r == [], str(r))
    td.cleanup()

# §バージョン履歴 のアンカーが外れる 3 経路。見出しレベル変更・改名・節削除のいずれでも
# 旧実装は黙って PASS していた（凍結が守られているかを一切見ないまま緑）。
for label, hist in (
    ("見出しレベルを ## に変更", FROZEN_HISTORY.replace("### バージョン履歴", "## バージョン履歴", 1)),
    ("見出しを改名（履歴 → 沿革）", FROZEN_HISTORY.replace("バージョン履歴", "バージョン沿革", 1)),
    ("節ごと削除", "## 別の節\n\n本文\n"),
):
    td, r = scenario(dh_core=True, specs=OK_SPECS, history=hist)
    check(f"アンカーが外れたら FAIL: {label}",
          any(i["severity"] == "FAIL" and "走査面を確保できなかった" in i["message"] for i in r), str(r))
    td.cleanup()

# 走査面が在るのに検査自身が黙るのを防ぐ = 健全ツリーでは余計な FAIL を出さない
td, r = scenario(dh_core=True, specs=OK_SPECS)
check("DH 本体の健全ツリーでは走査面 FAIL を出さない（偽陽性 0）", r == [], str(r))
td.cleanup()

print("== 常時発火しないこと（I-4）: 実リポで WARN / FAIL が 0 件 ==")
graded = _fx.real()
check("実リポで検出 0 件（是正済み）", graded == [], str(graded))

_fx.finish()
