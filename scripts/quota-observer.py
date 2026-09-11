#!/usr/bin/env python3
"""共有枠の観測 — 異常パターン検出（v6.19.0 F2）

供給元アカウントの共有枠（1 アカウントを複数プロジェクトが食い合う枠）について、
正規化済みの観測 JSON を受け取り、異常パターンと閾値超過を検出する。

**本スクリプトは判定を持たない**（upgrade-spec-v6.19.0 I-6）。検出して数えるだけで、
自動で昇格・停止・削除をしない。是正は人間または L0。

**供給元非依存**（同 I-1 / Level A checklist A-3）。Cloudflare / Supabase 等の固有 API は
アダプタ（`.claude/skills/crosscut-quota-observer/references/adapters/*.md`）が担い、
本スクリプトは正規化 JSON だけを見る。よって供給元が変わっても本体は生き残る。

入力スキーマ（stdin または --input のファイル）:

    {
      "observed_at": "2026-09-11T03:07:42Z",
      "provider": "cloudflare",
      "plan": "free",
      "limits": {                       # 省略可。無い項目は閾値検査をスキップする
        "databases": 10,
        "rows_written_daily": 100000,
        "rows_read_daily": 5000000,
        "bytes_per_database": 524288000,
        "kv_writes_daily": 1000
      },
      "resources": [
        {"id": "81d3...", "name": "news-collector", "kind": "db", "size_bytes": 2215936}
      ],
      "daily": [
        {"date": "2026-09-10", "resource_id": "81d3...",
         "rows_read": 36705, "rows_written": 54339}
      ]
    }

使い方:

    python3 scripts/quota-observer.py --input observation.json
    cat observation.json | python3 scripts/quota-observer.py --json

exit code: 常に 0（検出は FAIL ではない。I-6「観測は判定を持たない」）。
ただし --strict を付けると検出 1 件以上で 1 を返す（CI から呼ぶ場合の opt-in）。
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict

# 閾値。upgrade-spec-v6.19.0 §F2 の表に対応する。
# I-7「常時発火する検知を作らない」に従い、定常状態で 0 件になる値に置く。
THRESHOLDS = {
    "databases": 0.80,            # 個数上限の 80%
    "rows_written_daily": 0.50,   # 日次書込の 50% が 3 日連続
    "rows_read_daily": 0.50,      # 日次読込の 50% が 3 日連続
    "bytes_per_database": 0.80,   # 単一 DB 容量の 80%
    "kv_writes_daily": 0.70,      # KV 書込の 70%
}
CONSECUTIVE_DAYS = 3

# 異常パターンの検出パラメータ
FLAT_WRITE_MIN_DAYS = 5       # 「ほぼ一定」と言うのに必要な日数
FLAT_WRITE_CV_MAX = 0.15      # 変動係数がこれ以下なら一定とみなす
FLAT_WRITE_MIN_ROWS = 1000    # 小さすぎる値でのノイズ検出を避ける下限
WRITE_OVER_READ_MIN_ROWS = 1000


def _by_resource(daily: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for row in daily:
        out[row.get("resource_id") or "(unknown)"].append(row)
    for rows in out.values():
        rows.sort(key=lambda r: r.get("date", ""))
    return dict(out)


def _name_of(resources: list[dict], rid: str) -> str:
    for r in resources:
        if r.get("id") == rid:
            return r.get("name") or rid
    return rid


def _is_known(resources: list[dict], rid: str) -> bool:
    """daily に現れるが resources に無い = 観測時点で存在しないリソース。

    供給元の analytics は削除後も履歴を保持するため、既に消したリソースの過去の挙動が
    そのまま検出に乗る。2026-09-11 の実データで実際に起きた（削除済み news-collector が
    UUID のまま出力され、人間には何のことか分からなかった）。過去の事実として検出は残すが、
    **現在の是正対象ではない**ことを出力で区別する。
    """
    return any(r.get("id") == rid for r in resources)


def detect_write_over_read(daily, resources) -> list[dict]:
    """読んだ行数より書いた行数が多い日を検出する。

    差分更新なら通常 read >= write になる。逆転は「毎回ほぼ全件を書き直している」
    バッチの signature（2026-09-11 に news-collector で実測した挙動）。
    """
    findings = []
    for rid, rows in _by_resource(daily).items():
        hits = [
            r for r in rows
            if r.get("rows_written", 0) > r.get("rows_read", 0)
            and r.get("rows_written", 0) >= WRITE_OVER_READ_MIN_ROWS
        ]
        if not hits:
            continue
        known = _is_known(resources, rid)
        findings.append({
            "pattern": "write_exceeds_read",
            "resource_id": rid,
            "resource_name": _name_of(resources, rid),
            "resource_known": known,
            "days": len(hits),
            "sample": [
                {"date": h["date"], "rows_read": h.get("rows_read", 0),
                 "rows_written": h.get("rows_written", 0)}
                for h in hits[-3:]
            ],
            "note": "読んだ行数より書いた行数が多い。差分更新ではなく全件書き直しの疑い"
                    + ("" if known else "（**観測時点で当該リソースは存在しない**。削除済みの過去挙動であり現在の是正対象ではない）"),
        })
    return findings


def detect_flat_daily_writes(daily, resources) -> list[dict]:
    """日次書込がほぼ一定の resource を検出する。

    利用者数に連動する書込は日によって揺れる。ほぼ一定なのは定期バッチが
    毎回同量を書いている形であり、write_exceeds_read と重なると全件同期の確度が上がる。
    """
    findings = []
    for rid, rows in _by_resource(daily).items():
        writes = [r.get("rows_written", 0) for r in rows]
        if len(writes) < FLAT_WRITE_MIN_DAYS:
            continue
        mean = statistics.fmean(writes)
        if mean < FLAT_WRITE_MIN_ROWS:
            continue
        cv = statistics.pstdev(writes) / mean if mean else 0.0
        if cv > FLAT_WRITE_CV_MAX:
            continue
        known = _is_known(resources, rid)
        findings.append({
            "pattern": "flat_daily_writes",
            "resource_id": rid,
            "resource_name": _name_of(resources, rid),
            "resource_known": known,
            "days": len(writes),
            "mean_rows_written": round(mean, 1),
            "coefficient_of_variation": round(cv, 4),
            "note": f"{len(writes)} 日間の日次書込がほぼ一定（変動係数 {cv:.3f}）。定期バッチが毎回同量を書いている"
                    + ("" if known else "（**観測時点で当該リソースは存在しない**。削除済みの過去挙動）"),
        })
    return findings


def _consecutive_exceed(values: list[tuple[str, float]], limit: float, ratio: float) -> list[tuple[str, float]]:
    """閾値超過が CONSECUTIVE_DAYS 日連続した最後の並びを返す。無ければ空。"""
    threshold = limit * ratio
    run: list[tuple[str, float]] = []
    best: list[tuple[str, float]] = []
    for date, v in values:
        if v >= threshold:
            run.append((date, v))
            if len(run) >= CONSECUTIVE_DAYS:
                best = list(run)
        else:
            run = []
    return best


def detect_threshold(observation: dict) -> list[dict]:
    """枠の消費率が閾値を超えたものを検出する（アカウント単位の共有枠を含む）。"""
    findings = []
    limits = observation.get("limits") or {}
    resources = observation.get("resources") or []
    daily = observation.get("daily") or []

    # 個数（アカウント単位）
    if "databases" in limits:
        count = sum(1 for r in resources if r.get("kind") == "db")
        ratio = THRESHOLDS["databases"]
        if count >= limits["databases"] * ratio:
            findings.append({
                "pattern": "threshold_databases",
                "observed": count,
                "limit": limits["databases"],
                "usage_ratio": round(count / limits["databases"], 3),
                "note": "DB 個数が上限に接近。1 ツール = 1 DB 運用では最も早く来る律速",
            })

    # 単一リソースの容量
    if "bytes_per_database" in limits:
        lim = limits["bytes_per_database"]
        for r in resources:
            size = r.get("size_bytes")
            if size is None:
                continue
            if size >= lim * THRESHOLDS["bytes_per_database"]:
                findings.append({
                    "pattern": "threshold_size",
                    "resource_id": r.get("id"),
                    "resource_name": r.get("name"),
                    "observed": size,
                    "limit": lim,
                    "usage_ratio": round(size / lim, 3),
                    "note": "単一リソースの容量が上限に接近",
                })

    # 日次の合算（アカウント単位の共有枠。個々の resource ではなく日ごとの総和で見る）
    totals: dict[str, dict[str, float]] = defaultdict(lambda: {"rows_read": 0.0, "rows_written": 0.0, "kv_writes": 0.0})
    for row in daily:
        d = row.get("date", "")
        for key in ("rows_read", "rows_written", "kv_writes"):
            if key in row:
                totals[d][key] += row[key]
    ordered = sorted(totals.items())

    for key, limit_key in (
        ("rows_written", "rows_written_daily"),
        ("rows_read", "rows_read_daily"),
        ("kv_writes", "kv_writes_daily"),
    ):
        if limit_key not in limits:
            continue
        series = [(d, v[key]) for d, v in ordered if v[key] > 0]
        hit = _consecutive_exceed(series, limits[limit_key], THRESHOLDS[limit_key])
        if hit:
            findings.append({
                "pattern": f"threshold_{key}",
                "limit": limits[limit_key],
                "consecutive_days": len(hit),
                "sample": [{"date": d, "value": v} for d, v in hit[-CONSECUTIVE_DAYS:]],
                "usage_ratio": round(hit[-1][1] / limits[limit_key], 3),
                "note": "アカウント単位の共有枠。超過すると同一アカウントの全プロジェクトが巻き込まれる",
            })
    return findings


def observe(observation: dict) -> dict:
    resources = observation.get("resources") or []
    daily = observation.get("daily") or []
    findings = (
        detect_write_over_read(daily, resources)
        + detect_flat_daily_writes(daily, resources)
        + detect_threshold(observation)
    )
    return {
        "observed_at": observation.get("observed_at"),
        "provider": observation.get("provider"),
        "plan": observation.get("plan"),
        "resource_count": len(resources),
        "findings": findings,
        "finding_count": len(findings),
        "judgment": None,  # I-6: 観測は判定を持たない。是正は人間または L0
    }


def render(result: dict) -> str:
    lines = [
        f"# 共有枠の観測 — {result.get('provider') or '(provider 未記載)'}"
        f" / plan={result.get('plan') or '(未記載)'}",
        f"- 観測時刻: {result.get('observed_at') or '(未記載)'}",
        f"- リソース数: {result['resource_count']}",
        f"- 検出: {result['finding_count']} 件",
        "",
    ]
    if not result["findings"]:
        lines.append("検出なし（定常状態）。")
        return "\n".join(lines)
    for f in result["findings"]:
        head = f["pattern"]
        if f.get("resource_name"):
            head += f" — {f['resource_name']}"
        if f.get("resource_known") is False:
            head += "（削除済み / 観測範囲外）"
        lines.append(f"## {head}")
        lines.append(f"- {f['note']}")
        for key in ("days", "consecutive_days", "mean_rows_written",
                    "coefficient_of_variation", "observed", "limit", "usage_ratio"):
            if key in f:
                lines.append(f"- {key}: {f[key]}")
        if f.get("sample"):
            lines.append(f"- sample: {json.dumps(f['sample'], ensure_ascii=False)}")
        lines.append("")
    lines.append("**本出力は観測であって判定ではない**（I-6）。是正の要否は人間または L0 が決める。")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="共有枠の異常パターン検出（判定は持たない）")
    ap.add_argument("--input", help="観測 JSON のパス。省略時は stdin")
    ap.add_argument("--json", action="store_true", help="JSON で出力する")
    ap.add_argument("--strict", action="store_true",
                    help="検出 1 件以上で exit 1（CI から呼ぶ場合の opt-in）")
    args = ap.parse_args()

    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    try:
        observation = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"入力が JSON として読めない: {e}", file=sys.stderr)
        return 2

    result = observe(observation)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return 1 if (args.strict and result["finding_count"]) else 0


if __name__ == "__main__":
    sys.exit(main())
