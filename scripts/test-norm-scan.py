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

quoted = "\n".join([
    "> 規範メタデータ:",
    "> ```yaml",
    "> stage: 全段階",
    "> review_trigger:",
    ">   - measured: 点検を 3 回実施し 0 件なら降ろす候補",
    ">   - date: 2027-03-06",
    "> ```",
    "",
])
got = m.extract_triggers(quoted)
check("Markdown 引用ブロック内のメタデータも拾う（v6.18.0 で実測した欠陥）",
      len(got) == 2, str(got))
check("引用内の date が正しく読める",
      any("2027-03-06" in g for g in got), str(got))

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


print("== model_generation_epoch: .model-generation.yml 併用（v7.0.0 F7） ==")
import tempfile, pathlib, datetime as _dt2
with tempfile.TemporaryDirectory() as td:
    root = pathlib.Path(td); (root / "history").mkdir()
    (root / "history" / ".model-generation.yml").write_text('current: "x"\nchanged_at: "2030-01-02"\n', encoding="utf-8")
    e = m.model_generation_epoch(root)
    want = int(_dt2.datetime(2030, 1, 2, tzinfo=_dt2.timezone.utc).timestamp())
    check("yml の changed_at が model-recommendations より新しければそれを採る", e is not None and e >= want, str(e))
    (root / "history" / ".model-generation.yml").write_text('current: "x"\nchanged_at: "2000-01-01"\n', encoding="utf-8")
    e2 = m.model_generation_epoch(root)
    check("yml が古ければ model-recommendations 側（or None）に落ちる", e2 is None or e2 > int(_dt2.datetime(2000,1,2,tzinfo=_dt2.timezone.utc).timestamp()), str(e2))
    (root / "history" / ".model-generation.yml").write_text('current: "x"\nchanged_at: "2026-13-45"\n', encoding="utf-8")
    try:
        e3 = m.model_generation_epoch(root); crashed = False
    except Exception:
        crashed = True
    check("不正日付（2026-13-45）でも crash せず degrade する", not crashed and (e3 is None or isinstance(e3, int)))
    (root / "history" / ".model-generation.yml").unlink()
    try:
        e4 = m.model_generation_epoch(root); crashed = False
    except Exception:
        crashed = True
    check("yml 不在でも例外を出さない", not crashed and (e4 is None or isinstance(e4, int)))
    # decide() レベルで「yml が新しければ発火」を観測する（spec F7 受け入れ基準の文言）
    (root / "history" / ".model-generation.yml").write_text('current: "x"\nchanged_at: "2030-01-02"\n', encoding="utf-8")
    r = decide("model_generation", model_epoch=m.model_generation_epoch(root))
    check("yml 由来の世代 epoch で model_generation が発火する", r and r.get("fired") is True, str(r))

if FAIL:
    sys.exit(f"\nFAIL: {FAIL} 件")
print("\nPASS: norm-scan 回帰テスト 全通過")
