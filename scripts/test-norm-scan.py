#!/usr/bin/env python3
"""norm-scan（時限規範の機械列挙）の回帰テスト。

各トリガ形式に発火条件を仕込み、**検出することを実証する**。
実リポでの「発火 0 件」は、検査が空振りしていても同じ表示になるため、
それだけでは走査器が動いている証拠にならない。
"""

import datetime as _dt
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("norm_scan", HERE / "scripts" / "norm-scan.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FAIL = 0
NOW = _dt.datetime(2026, 9, 6, tzinfo=_dt.timezone.utc)
# 最終 commit を 2026-08-01 と仮定（NOW から 36 日前）
EPOCH = int(_dt.datetime(2026, 8, 1, tzinfo=_dt.timezone.utc).timestamp())


def check(name, cond, detail=""):
    global FAIL
    if cond:
        print(f"  ok: {name}")
    else:
        FAIL += 1
        print(f"FAIL: {name} {detail}", file=sys.stderr)


def decide(item, *, stage=None, model_epoch=None, file_epoch=EPOCH):
    return m.decide(item, path="x.md", file_epoch=file_epoch, now=NOW,
                    stage=stage, model_epoch=model_epoch)


print("== extract_triggers: 3 つの書式を拾う ==")
inline = "規範メタデータ: `{ stage: S2, review_trigger: [measured: 委譲漏れ, model_generation, stage_transition: S2→S3] }`"
got = m.extract_triggers(inline)
check("インライン形の 3 項目を分解する", len(got) == 3, str(got))

block = "\n".join([
    "規範メタデータ:",
    "    stage: 全段階",
    "    review_trigger:",
    "      - measured: 検査 5 が初期是正後 1 cycle で 0 件に落ちなければ、",
    "        誤検知率を再測定し、落ちないなら本検査を削る",
    "      - date: 2026-11-30",
    "",
])
got = m.extract_triggers(block)
check("ブロック形の 2 項目を拾う（継続行を畳む）", len(got) == 2, str(got))
check("継続行が別項目に割れていない",
      any("誤検知率を再測定" in g and g.startswith("measured") for g in got), str(got))

check("review_trigger が無ければ空", m.extract_triggers("# ただの文書\n") == [])

print("== date: 期限超過を検出 ==")
r = decide("date: 2026-08-01")
check("期限を過ぎたら発火", r and r["fired"] is True, str(r))
r = decide("date: 2026-12-31")
check("期限内なら未発火（判定済みとして記録する）",
      r and r["fired"] is False and "残り" in r["why"], str(r))

print("== cycles: N cycle 相当の経過を検出 ==")
r = decide("cycles: 2")      # 2 cycle = 28 日 <= 36 日
check("2 cycle 経過で発火", r and r["fired"] is True, str(r))
r = decide("cycles: 6")      # 6 cycle = 84 日 > 36 日
check("6 cycle 未達なら未発火", r and r["fired"] is False, str(r))

print("== stage_transition: lifecycle_stage の到達を検出 ==")
r = decide("stage_transition: S2→S3", stage="S3")
check("宣言先の段階に到達で発火", r and r["fired"] is True, str(r))
r = decide("stage_transition: S2→S3", stage="S2")
check("未到達なら未発火", r and r["fired"] is False, str(r))
r = decide("stage_transition: S2→S3", stage=None)
check("REGIME 不在なら判定不能として記録（黙って捨てない）",
      r and r["fired"] is None and "判定不能" in r["why"], str(r))
r = decide("stage_transition: S2->S3", stage="S3")
check("ASCII 矢印 -> も受ける", r and r["fired"] is True, str(r))

print("== model_generation: 世代交代を検出 ==")
r = decide("model_generation", model_epoch=EPOCH + 86400)
check("model-recommendations が新しければ発火", r and r["fired"] is True, str(r))
r = decide("model_generation", model_epoch=EPOCH - 86400)
check("古ければ未発火", r and r["fired"] is False, str(r))

print("== measured: 機械判定しない（I-3） ==")
r = decide("measured: 同種誤認が 12 cycle 再発なしなら降格候補")
check("measured は fired=None で列挙のみ", r and r["fired"] is None, str(r))
check("理由に「機械判定しない」が出る", r and "機械判定しない" in r["why"], str(r))

print("== 未知の形式を黙って捨てない ==")
r = decide("whenever_i_feel_like_it")
check("未知のトリガも記録する（v6.13.0 I-4 検出器は黙って捨てない）",
      r and r["kind"] == "unknown", str(r))

print("== 除外規則 ==")
check("dh-upgrades/ は除外（実装済み spec は歴史的記録）",
      any(x == "dh-upgrades/" for x in m.EXCLUDE_PREFIXES))
check("history/ は除外（履歴層）", "history/" in m.EXCLUDE_PREFIXES)
check("delivery/ は除外（分析文書）", "delivery/" in m.EXCLUDE_PREFIXES)

print("== 実リポで走る（I-5: ローカルで走る） ==")
res = m.scan(HERE, _dt.datetime.now(_dt.timezone.utc))
check("実リポを走査できる", res["scanned_files"] > 0, str(res["scanned_files"]))
check("トリガを 1 件以上抽出できている（空振りでない）",
      res["total_triggers"] > 0, str(res["total_triggers"]))
check("抽出 = 発火 + 未発火 + 判定しない（取りこぼしゼロ）",
      res["total_triggers"] == len(res["fired"]) + len(res["not_fired"]) + len(res["undecidable"]),
      str(res))

if FAIL:
    sys.exit(f"\nFAIL: {FAIL} 件")
print("\nPASS: norm-scan 回帰テスト 全通過")
