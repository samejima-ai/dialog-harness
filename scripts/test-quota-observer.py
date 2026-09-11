#!/usr/bin/env python3
"""quota-observer（共有枠の異常パターン検出）の回帰テスト。

各パターンに発火条件を仕込み、**検出することを実証する**。あわせて健全な入力で
**0 件になることも実証する**（I-7「常時発火する検知を作らない」）。実リポでの
「検出 0 件」は、検出器が空振りしていても同じ表示になるため、それだけでは
動いている証拠にならない。

陽性ケースの中核は 2026-09-11 に Cloudflare GraphQL Analytics API から実測した
news-collector の 7 日分であり、合成値ではない。この挙動を人間が目で見つけたことが
F2 の起点なので、同じデータを検出できなければ機構の意味がない。
"""

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("quota_observer", HERE / "scripts" / "quota-observer.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FAIL = 0

# Cloudflare 無料枠（2026-09-11 観測）。値の正本はアダプタ側で、ここは検査用の固定値。
FREE_LIMITS = {
    "databases": 10,
    "rows_written_daily": 100_000,
    "rows_read_daily": 5_000_000,
    "bytes_per_database": 524_288_000,
    "kv_writes_daily": 1_000,
}

# 実測値: news-collector（81d3ca1a）2026-09-04〜10
NEWS_COLLECTOR = [
    ("2026-09-04", 39_423, 55_667),
    ("2026-09-05", 37_864, 54_054),
    ("2026-09-06", 36_069, 52_409),
    ("2026-09-07", 33_403, 50_899),
    ("2026-09-08", 34_864, 52_587),
    ("2026-09-09", 36_415, 53_756),
    ("2026-09-10", 36_705, 54_339),
]
# 実測値: minna-no-ai-bbs（0c8b0c93）同期間。読み中心・書込ほぼ 0 の健全な形
BBS = [
    ("2026-09-04", 324, 1),
    ("2026-09-05", 324, 1),
    ("2026-09-06", 325, 1),
    ("2026-09-07", 326, 1),
    ("2026-09-08", 327, 1),
    ("2026-09-09", 328, 1),
    ("2026-09-10", 362, 0),
]


def check(name, cond, detail=""):
    global FAIL
    if cond:
        print(f"  ok: {name}")
    else:
        FAIL += 1
        print(f"  NG: {name}" + (f" — {detail}" if detail else ""))


def daily(rid, rows):
    return [{"date": d, "resource_id": rid, "rows_read": r, "rows_written": w} for d, r, w in rows]


def obs(resources, daily_rows, limits=None):
    return {
        "observed_at": "2026-09-11T03:07:42Z",
        "provider": "cloudflare",
        "plan": "free",
        "limits": FREE_LIMITS if limits is None else limits,
        "resources": resources,
        "daily": daily_rows,
    }


def patterns(result):
    return {f["pattern"] for f in result["findings"]}


def main():
    print("== 陽性: 実測した news-collector の挙動を検出できるか ==")
    r = m.observe(obs(
        [{"id": "81d3", "name": "news-collector", "kind": "db", "size_bytes": 2_215_936},
         {"id": "0c8b", "name": "minna-no-ai-bbs", "kind": "db", "size_bytes": 61_440}],
        daily("81d3", NEWS_COLLECTOR) + daily("0c8b", BBS),
    ))
    p = patterns(r)
    check("write_exceeds_read を検出", "write_exceeds_read" in p, str(p))
    check("flat_daily_writes を検出", "flat_daily_writes" in p, str(p))
    check("日次書込の閾値超過を検出", "threshold_rows_written" in p, str(p))
    wer = [f for f in r["findings"] if f["pattern"] == "write_exceeds_read"]
    check("検出対象は news-collector のみ（bbs は巻き込まない）",
          len(wer) == 1 and wer[0]["resource_name"] == "news-collector",
          str([f.get("resource_name") for f in wer]))
    check("7 日すべてで read < write を捉える", wer and wer[0]["days"] == 7, str(wer))

    print("== 陰性: 健全な入力で 0 件になるか（I-7） ==")
    r = m.observe(obs([{"id": "0c8b", "name": "minna-no-ai-bbs", "kind": "db", "size_bytes": 61_440}],
                      daily("0c8b", BBS)))
    check("健全な resource 単独では検出 0 件", r["finding_count"] == 0, str(r["findings"]))

    print("== 陰性: news-collector 削除後の実状（2026-09-11 時点）で 0 件か ==")
    r = m.observe(obs([{"id": "0c8b", "name": "minna-no-ai-bbs", "kind": "db", "size_bytes": 61_440}],
                      [{"date": "2026-09-11", "resource_id": "0c8b", "rows_read": 35, "rows_written": 0}]))
    check("削除後のベースラインで検出 0 件", r["finding_count"] == 0, str(r["findings"]))

    print("== write_exceeds_read の下限（ノイズ除去） ==")
    small = [("2026-09-0%d" % i, 10, 20) for i in range(1, 8)]
    r = m.observe(obs([{"id": "x", "name": "tiny", "kind": "db"}], daily("x", small)))
    check("書込が下限未満なら逆転していても検出しない",
          "write_exceeds_read" not in patterns(r), str(patterns(r)))

    print("== flat_daily_writes の境界 ==")
    flat = [("2026-09-0%d" % i, 9_000, 5_000) for i in range(1, 8)]
    r = m.observe(obs([{"id": "x", "name": "flat", "kind": "db"}], daily("x", flat)))
    check("完全に一定なら検出", "flat_daily_writes" in patterns(r), str(patterns(r)))
    spiky = [("2026-09-01", 9_000, 1_000), ("2026-09-02", 9_000, 9_000), ("2026-09-03", 9_000, 2_000),
             ("2026-09-04", 9_000, 8_000), ("2026-09-05", 9_000, 1_500), ("2026-09-06", 9_000, 7_000),
             ("2026-09-07", 9_000, 3_000)]
    r = m.observe(obs([{"id": "x", "name": "spiky", "kind": "db"}], daily("x", spiky)))
    check("日によって揺れるなら検出しない", "flat_daily_writes" not in patterns(r), str(patterns(r)))
    short = [("2026-09-0%d" % i, 9_000, 5_000) for i in range(1, 4)]
    r = m.observe(obs([{"id": "x", "name": "short", "kind": "db"}], daily("x", short)))
    check("日数が足りなければ一定でも検出しない",
          "flat_daily_writes" not in patterns(r), str(patterns(r)))

    print("== 閾値: 個数 ==")
    r = m.observe(obs([{"id": f"d{i}", "name": f"db{i}", "kind": "db"} for i in range(8)], []))
    check("8 個（上限 10 の 80%）で検出", "threshold_databases" in patterns(r), str(patterns(r)))
    r = m.observe(obs([{"id": f"d{i}", "name": f"db{i}", "kind": "db"} for i in range(7)], []))
    check("7 個では検出しない", "threshold_databases" not in patterns(r), str(patterns(r)))

    print("== 閾値: 連続日数（3 日連続で発火 / 2 日では発火しない） ==")
    over = 60_000  # 上限 100k の 60% > 50%
    three = [("2026-09-01", 0, over), ("2026-09-02", 0, over), ("2026-09-03", 0, over)]
    r = m.observe(obs([{"id": "x", "name": "x", "kind": "db"}], daily("x", three)))
    check("3 日連続で検出", "threshold_rows_written" in patterns(r), str(patterns(r)))
    two = [("2026-09-01", 0, over), ("2026-09-02", 0, over), ("2026-09-03", 0, 1_000)]
    r = m.observe(obs([{"id": "x", "name": "x", "kind": "db"}], daily("x", two)))
    check("2 日で途切れれば検出しない", "threshold_rows_written" not in patterns(r), str(patterns(r)))

    print("== 閾値: アカウント単位の合算（1 本ずつは閾値未満でも合計で超える） ==")
    half = 30_000  # 単独では 30% だが 2 本合計で 60%
    rows = (daily("a", [("2026-09-0%d" % i, 0, half) for i in range(1, 4)])
            + daily("b", [("2026-09-0%d" % i, 0, half) for i in range(1, 4)]))
    r = m.observe(obs([{"id": "a", "name": "a", "kind": "db"}, {"id": "b", "name": "b", "kind": "db"}], rows))
    check("共有枠は合算で判定する（per-project ではない / I-2）",
          "threshold_rows_written" in patterns(r), str(patterns(r)))

    print("== 閾値: 容量と KV ==")
    r = m.observe(obs([{"id": "x", "name": "big", "kind": "db", "size_bytes": 430_000_000}], []))
    check("単一 DB 容量 82% で検出", "threshold_size" in patterns(r), str(patterns(r)))
    r = m.observe(obs([{"id": "x", "name": "small", "kind": "db", "size_bytes": 100_000_000}], []))
    check("容量 19% では検出しない", "threshold_size" not in patterns(r), str(patterns(r)))
    kv = [{"date": "2026-09-0%d" % i, "resource_id": "k", "kv_writes": 800} for i in range(1, 4)]
    r = m.observe(obs([{"id": "k", "name": "kv", "kind": "kv"}], kv))
    check("KV 書込 80%（上限 1000）で検出", "threshold_kv_writes" in patterns(r), str(patterns(r)))

    print("== degrade: limits が欠けていても落ちない（I-5） ==")
    r = m.observe({"provider": "unknown", "resources": [{"id": "x", "name": "x", "kind": "db"}],
                   "daily": daily("x", NEWS_COLLECTOR)})
    check("limits なしでも例外を出さない", isinstance(r["finding_count"], int))
    check("limits なしでは閾値検出が出ない",
          not any(p.startswith("threshold_") for p in patterns(r)), str(patterns(r)))
    check("limits なしでもパターン検出は動く", "write_exceeds_read" in patterns(r), str(patterns(r)))
    r = m.observe({})
    check("空入力でも落ちない", r["finding_count"] == 0)

    print("== 削除済みリソース（実データで判明: analytics は削除後も履歴を保持する） ==")
    # resources に無い id が daily に現れる = 観測時点では存在しないリソース
    r = m.observe(obs([{"id": "0c8b", "name": "minna-no-ai-bbs", "kind": "db", "size_bytes": 61_440}],
                      daily("81d3", NEWS_COLLECTOR) + daily("0c8b", BBS)))
    gone = [f for f in r["findings"] if f.get("resource_id") == "81d3"]
    check("削除済みでも過去挙動は検出する", bool(gone), str(patterns(r)))
    check("resource_known: False が立つ",
          gone and all(f["resource_known"] is False for f in gone), str(gone))
    check("note に「現在の是正対象ではない」が入る",
          any("是正対象ではない" in f["note"] for f in gone), str([f["note"] for f in gone]))
    check("render の見出しに削除済みが出る", "削除済み / 観測範囲外" in m.render(r))
    # 存在するリソースは True
    live = [f for f in r["findings"] if f.get("resource_id") == "0c8b"]
    check("存在するリソースには False を立てない",
          all(f.get("resource_known") is not False for f in live), str(live))

    print("== I-6: 観測は判定を持たない ==")
    r = m.observe(obs([{"id": "81d3", "name": "news-collector", "kind": "db"}],
                      daily("81d3", NEWS_COLLECTOR)))
    check("judgment は常に null", r["judgment"] is None)
    check("render が判定を持たない旨を明示", "判定ではない" in m.render(r))

    print()
    if FAIL:
        print(f"FAIL: {FAIL} 件")
        return 1
    print("all ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
