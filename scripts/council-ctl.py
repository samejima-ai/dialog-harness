#!/usr/bin/env python3
"""council-ctl — Council 事後評価ループ（CTL 昇格）の半自動ドライバ。

「Council 発動 → 事後評価 → stats 再計算 → CTL 算出」を 1 本の CLI で回す。
記事でいう Loop Engineering の Step 5「経験の還元」を回し続けるための道具。

CTL（Council Trust Level）は手で書き換える値ではなく、横断蓄積データから
決定論的に算出される。アルゴリズムは
  .claude/skills/crosscut-council/references/ctl-calculation.md
  .claude/skills/crosscut-council/references/ctl-maturity-strategy.md
が一次情報源で、本ツールの calculate_ctl() はその §3 をそのまま実装する。

データは user-scope（~/.claude/council-data/）に閉じる（プライバシー配慮）。
repo にはこのツールしか入らない。データファイルは追跡しない。

使い方:
    python3 scripts/council-ctl.py init
    python3 scripts/council-ctl.py record  --decision-category C2 \
        --category judgment --topic "ライブラリ選定のトレードオフ" \
        --judgment "選択肢 A を推奨" --confidence 0.85 --consensus auto_agree
    python3 scripts/council-ctl.py pending          # 未評価の判定を一覧（律速段階）
    python3 scripts/council-ctl.py evaluate <id> --status agreed
    python3 scripts/council-ctl.py evaluate <id> --status agreed_with_synthesis \
        --note "案 A の骨格を採用し、少数意見の CHECK を同 PR に併合"
    python3 scripts/council-ctl.py audit            # note 欠落・legacy status を検出
    python3 scripts/council-ctl.py recompute        # stats.json 再計算 + CTL 表示
    python3 scripts/council-ctl.py status           # 現在の CTL と次段階までの不足
    python3 scripts/council-ctl.py regime-block      # REGIME.md 用ブロックを出力

プライバシー: topic / judgment は抽象化した要約のみを渡すこと
（プロジェクト名・コード断片・人物名を入れない。ctl-calculation.md §4 参照）。
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import json
import os
import secrets
import sys
from pathlib import Path

# ---- パス（user-scope に閉じる） ---------------------------------------------

DATA_DIR = Path(os.environ.get("COUNCIL_DATA_DIR", Path.home() / ".claude" / "council-data"))
STATS_PATH = DATA_DIR / "stats.json"
INVOCATIONS_DIR = DATA_DIR / "invocations"
VERSION_PATH = DATA_DIR / "version.md"

DATA_VERSION = "0.1"
HARNESS_VERSION = "v5.x"

VALID_DECISION_CATEGORIES = ("C1", "C2", "C3", "C4")
# ctl-calculation.md §4 status の 4 値。agreed_with_synthesis は v6.12.0 で追加
# （止揚 = 骨格を採った上での併合。DH の推奨動作なので同意側に置く）。
VALID_STATUSES = ("agreed", "agreed_with_synthesis", "modified", "rejected")
# agreement_rate の分子に算入する status。
AGREEING_STATUSES = ("agreed", "agreed_with_synthesis")
# modifier_note を必須とする status（agreed 以外は理由が読めないと検証不能）。
NOTE_REQUIRED_STATUSES = ("agreed_with_synthesis", "modified", "rejected")


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---- CTL 算出ロジック（ctl-calculation.md §3 の忠実実装） ----------------------


def calculate_ctl(stats: dict) -> str:
    """ctl-calculation.md §3 をそのまま実装。stats から CTL-0..3 を返す。"""
    total = stats.get("total_invocations", 0)
    categories = stats.get("categories", {})

    # CTL-0: コールドスタート
    if total == 0:
        return "CTL-0"

    # CTL-3: 高度委譲（最も厳しい条件）
    if total >= 100:
        all_categories_meet = all(
            cat.get("count", 0) >= 25 and cat.get("agreement_rate", 0) >= 0.95
            for cat in categories.values()
        )
        if all_categories_meet and len(categories) >= 4:
            return "CTL-3"

    # CTL-2: 標準運用
    if total >= 30:
        majority_meet = sum(
            1
            for cat in categories.values()
            if cat.get("count", 0) >= 10 and cat.get("agreement_rate", 0) >= 0.90
        )
        if majority_meet >= 3:  # 4 カテゴリ中 3 以上
            return "CTL-2"

    # CTL-1: 初期蓄積
    if total >= 10:
        any_meet = any(
            cat.get("count", 0) >= 10 and cat.get("agreement_rate", 0) >= 0.90
            for cat in categories.values()
        )
        if any_meet:
            return "CTL-1"

    return "CTL-0"


def delegation_scope(stats: dict) -> list[str]:
    """各 decision_category が自律委譲の質的条件（count≥10 & rate≥0.90）を
    満たすかを返す。REGIME.md の delegation_scope 記録に使う。"""
    scope = []
    for name, cat in sorted(stats.get("categories", {}).items()):
        if cat.get("count", 0) >= 10 and cat.get("agreement_rate", 0) >= 0.90:
            scope.append(name)
    return scope


# ---- I/O ヘルパ --------------------------------------------------------------


def _atomic_write(path: Path, text: str) -> None:
    """tmp に書いてから os.replace で原子的に差し替える。

    直書き（write_text）は ctrl-C / 並行 record で途中状態を残し、次回 json.loads が
    全体破綻する。同一ディレクトリ内 tmp → rename なら部分書込が読まれない。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{secrets.token_hex(2)}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        # クリーンアップ失敗で元の write/replace 例外をマスクしない（握りつぶす）
        with contextlib.suppress(OSError):
            tmp.unlink(missing_ok=True)


def _write_fresh_data() -> None:
    """council-data を CTL-0 で新規生成する（stats.json / invocations/ / version.md）。"""
    INVOCATIONS_DIR.mkdir(parents=True, exist_ok=True)
    stats = {
        "version": DATA_VERSION,
        "last_updated": _now(),
        "categories": {},
        "total_invocations": 0,
        "total_agreed": 0,
        "overall_agreement_rate": 0.0,
    }
    _atomic_write(STATS_PATH, json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(
        VERSION_PATH,
        "# Council Data Version\n\n"
        f"- version: {DATA_VERSION}\n"
        f"- created_at: {_now()}\n"
        f"- last_updated: {_now()}\n"
        f"- harness_version_at_creation: {HARNESS_VERSION}\n"
        "- total_projects: 0\n"
        "- notes: |\n"
        "  Council Trust Level の横断蓄積データ。\n"
        "  プロジェクト名・コード断片は記録しない（プライバシー配慮）。\n",
    )


def _ensure_initialized() -> bool:
    """未初期化なら CTL-0 でコールドスタート初期化する（ctl-calculation.md §1/§8）。

    Council 発動時の自動 record が未初期化環境でも落ちないための lazy-init。
    新規作成した場合のみ True を返す。
    """
    if STATS_PATH.exists():
        return False
    _write_fresh_data()
    return True


def _load_stats() -> dict:
    if STATS_PATH.exists():
        try:
            return json.loads(STATS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            # stats.json 破損時は invocations/ から再計算して自己修復する。
            # 健全な invocations/ があれば CTL を CTL-0 と誤算出せず正しい値を返す
            # （ctl_at_invocation / regime-block / status への波及を防ぐ）。
            print(f"warn: stats.json が破損/読込不能。invocations/ から再計算: {e}",
                  file=sys.stderr)
            return _compute_stats()
    return {"version": DATA_VERSION, "categories": {}, "total_invocations": 0}


def _iter_invocations():
    if not INVOCATIONS_DIR.exists():
        return
    for path in sorted(INVOCATIONS_DIR.glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            # 壊れた 1 ファイルで全コマンドを落とさない。警告して skip。
            print(f"warn: 破損または読込不能の invocation を skip: {path.name} ({e})",
                  file=sys.stderr)
            continue
        yield path, rec


# ---- サブコマンド ------------------------------------------------------------


def cmd_init(args) -> None:
    """ctl-calculation.md §8 の初期化ロジック。"""
    if STATS_PATH.exists() and not args.force:
        print(f"既に初期化済み: {STATS_PATH}（再初期化は --force）")
        cmd_status(args)
        return

    _write_fresh_data()
    print(f"初期化しました: {DATA_DIR}  → CTL-0（コールドスタート）")


def cmd_record(args) -> None:
    """Council 発動を 1 件記録する（actual_outcome は未評価で作成）。"""
    # 未初期化なら自動でコールドスタート初期化（発動＝自動 record が落ちない）。
    if _ensure_initialized():
        print("（council-data 未初期化のため自動初期化しました → CTL-0）", file=sys.stderr)
    dc = args.decision_category.upper()
    if dc not in VALID_DECISION_CATEGORIES:
        sys.exit(
            f"decision_category は {VALID_DECISION_CATEGORIES} のいずれか。\n"
            "H カテゴリは CTL に関係なく常時人間献上のため記録しない"
            "（ctl-calculation.md §2）。"
        )
    if not 0.0 <= args.confidence <= 1.0:
        sys.exit(
            f"--confidence は 0.0〜1.0 の範囲（judgment_confidence）。"
            f" 入力: {args.confidence}"
        )
    ts = _now()
    suffix = secrets.token_hex(3)  # 6 文字
    invocation_id = f"council-{ts}-{suffix}"
    fname = f"{ts.replace(':', '-')}-{suffix}.json"
    record = {
        "invocation_id": invocation_id,
        "council_type": args.council_type,
        "category": args.category,
        "decision_category": dc,
        "topic_summary": args.topic[:80],
        "judgment": args.judgment,
        "judgment_confidence": args.confidence,
        "consensus_mode": args.consensus,
        "ctl_at_invocation": _load_stats_ctl(),
        "actual_outcome": {"status": None, "evaluated_at": None, "modifier_note": None},
    }
    _atomic_write(INVOCATIONS_DIR / fname,
                  json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(f"記録: {invocation_id}")
    print(f"  → 事後評価が CTL の燃料です。結論が出たら:")
    print(f"     python3 scripts/council-ctl.py evaluate {suffix} --status agreed|modified|rejected")


def _load_stats_ctl() -> str:
    return calculate_ctl(_load_stats())


def cmd_pending(args) -> None:
    """未評価（律速段階）の判定を一覧する。"""
    _ensure_initialized()
    rows = [
        (path, rec)
        for path, rec in _iter_invocations()
        if not rec.get("actual_outcome", {}).get("status")
    ]
    if not rows:
        print("未評価の判定はありません。すべて事後評価済み。")
        return
    print(f"未評価 {len(rows)} 件（これらは CTL に未反映 = 評価すれば燃料になる）:\n")
    for _path, rec in rows:
        sid = rec["invocation_id"][-6:]
        print(f"  [{sid}] {rec['decision_category']}  conf={rec.get('judgment_confidence')}  "
              f"{rec.get('topic_summary', '')}")


def _find_invocation(token: str):
    """invocation_id 全体 / 末尾 6 文字 / ファイル名 のいずれかで 1 件特定。"""
    matches = []
    for path, rec in _iter_invocations():
        if (
            token == rec["invocation_id"]
            or token == rec["invocation_id"][-6:]
            or token == path.name
            or token == path.stem
        ):
            matches.append((path, rec))
    if not matches:
        sys.exit(f"該当なし: {token}（pending で末尾 6 文字を確認）")
    if len(matches) > 1:
        sys.exit(
            f"複数該当（{len(matches)} 件）: {token} を一意にしてください。"
            f" 完全 ID は {INVOCATIONS_DIR} の一覧で確認できます"
        )
    return matches[0]


def cmd_evaluate(args) -> None:
    """事後評価: actual_outcome を埋める。これが agreement_rate を作る。"""
    _ensure_initialized()
    status = args.status.lower()
    if status not in VALID_STATUSES:
        sys.exit(f"--status は {VALID_STATUSES} のいずれか")
    path, rec = _find_invocation(args.id)
    prev_outcome = rec.get("actual_outcome", {})
    prev = prev_outcome.get("status")
    # 再評価で --note 省略時は既存 note を保持（黙って消さない）。
    # 明示的に消したい場合は --note "" を渡す。
    note = prev_outcome.get("modifier_note") if args.note is None else args.note
    # agreed 以外は --note 必須（ctl-calculation.md §4 modifier_note の必須化）。
    # status だけ記録して理由を落とすと「なぜ rate が下がったか」が原理的に読めない。
    if status in NOTE_REQUIRED_STATUSES and not (note or "").strip():
        sys.exit(
            f"--note は status={status} では必須です"
            f"（判定のどこを採り、何を足したか／なぜ採らなかったかを 1 文で）。\n"
            f"  参照: .claude/skills/crosscut-council/references/ctl-calculation.md §4"
        )
    rec["actual_outcome"] = {
        "status": status,
        "evaluated_at": _now(),
        "modifier_note": note,
    }
    _atomic_write(path, json.dumps(rec, ensure_ascii=False, indent=2) + "\n")
    verb = "再評価" if prev else "評価"
    print(f"{verb}: {rec['invocation_id'][-6:]} → {status}")
    # 評価のたびに即再計算（次プロジェクトに即反映、ctl-calculation.md §6）
    _recompute(quiet=False)


def _compute_stats() -> dict:
    """invocations/ から stats を計算して返す（書き込みはしない・純粋関数）。

    評価済み（actual_outcome.status != null）のみを統計に算入する。
    未評価は CTL に未反映（pending で可視化）— 事後評価が律速、という設計を反映。
    """
    cats: dict[str, dict] = {}
    total = 0
    total_agreed = 0
    for _path, rec in _iter_invocations():
        outcome = rec.get("actual_outcome", {})
        status = outcome.get("status")
        if status not in VALID_STATUSES:
            continue  # 未評価はスキップ
        dc = rec.get("decision_category")
        if dc not in VALID_DECISION_CATEGORIES:
            continue
        c = cats.setdefault(
            dc,
            {"count": 0, "agreed": 0, "agreed_with_synthesis": 0, "modified": 0, "rejected": 0},
        )
        c["count"] += 1
        total += 1
        c[status] += 1
        if status in AGREEING_STATUSES:
            total_agreed += 1

    for c in cats.values():
        # agreement_rate = (agreed + agreed_with_synthesis) / count（ctl-calculation.md §2）。
        # 止揚（骨格を採った上での併合）は DH の推奨動作なので同意側に算入する。
        # 骨格を採らなかった modified / rejected のみが分子から外れる。
        agreeing = sum(c[s] for s in AGREEING_STATUSES)
        c["agreement_rate"] = round(agreeing / c["count"], 4) if c["count"] else 0.0

    return {
        "version": DATA_VERSION,
        "last_updated": _now(),
        "categories": cats,
        "total_invocations": total,
        "total_agreed": total_agreed,
        "overall_agreement_rate": round(total_agreed / total, 4) if total else 0.0,
    }


def _recompute(quiet: bool) -> dict:
    """invocations/ から stats.json を再構築して書き戻し、CTL を返す。"""
    _ensure_initialized()
    stats = _compute_stats()
    _atomic_write(STATS_PATH, json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    if not quiet:
        ctl = calculate_ctl(stats)
        print(f"再計算: 評価済み {stats['total_invocations']} 件 / 一致 {stats['total_agreed']} 件 "
              f"(rate {stats['overall_agreement_rate']}) → {ctl}")
    return stats


def cmd_recompute(args) -> None:
    _recompute(quiet=False)


def cmd_audit(args) -> None:
    """記録の健全性を検査する（決定論・LLM 判定なし）。

    検出するもの:
      1. modifier_note 欠落 — agreed 以外なのに理由が読めない記録
      2. 未評価 — actual_outcome.status が空（CTL に未反映）
      3. decision_category 欠落 — 統計に算入されない記録
      4. stats.json と invocations/ の件数乖離

    いずれも「なぜ agreement_rate がこの値なのか」を読めなくする要因。
    """
    _ensure_initialized()
    missing_note, unevaluated, no_dc = [], [], []
    counted = 0
    for _path, rec in _iter_invocations():
        outcome = rec.get("actual_outcome", {}) or {}
        status = outcome.get("status")
        sid = rec["invocation_id"][-6:]
        topic = (rec.get("topic_summary") or "")[:56]
        if not status:
            unevaluated.append((sid, topic))
            continue
        if rec.get("decision_category") not in VALID_DECISION_CATEGORIES:
            no_dc.append((sid, topic))
        else:
            counted += 1
        if status in NOTE_REQUIRED_STATUSES and not (outcome.get("modifier_note") or "").strip():
            missing_note.append((sid, status, topic))

    def _dump(title: str, rows: list, fmt) -> None:
        if not rows:
            return
        print(f"\n{title}（{len(rows)} 件）")
        for r in rows:
            print(f"  {fmt(r)}")

    print("=== Council 記録の健全性検査 ===")
    _dump("[1] modifier_note 欠落 — 理由が読めない",
          missing_note, lambda r: f"[{r[0]}] {r[1]:<22} {r[2]}")
    _dump("[2] 未評価 — CTL に未反映", unevaluated, lambda r: f"[{r[0]}] {r[1]}")
    _dump("[3] decision_category 欠落 — 統計に算入されない",
          no_dc, lambda r: f"[{r[0]}] {r[1]}")

    # [4] stats.json との乖離（CTL は stats.json から算出されるため直撃する）
    # _load_stats() は破損時に invocations/ から自己修復するため、
    # 乖離そのものを検出したい本コマンドでは生読みする。
    recorded = None
    if STATS_PATH.exists():
        try:
            recorded = json.loads(
                STATS_PATH.read_text(encoding="utf-8")
            ).get("total_invocations")
        except (json.JSONDecodeError, OSError) as e:
            print(f"  warn: stats.json 読込不能: {e}")
    print(f"\n[4] 件数の整合")
    print(f"  invocations/ 実体（統計算入対象）: {counted} 件")
    print(f"  stats.json total_invocations   : {recorded} 件")
    if recorded is not None and recorded != counted:
        print(f"  → 乖離 {abs(counted - recorded)} 件。`recompute` で解消する")

    total_issues = len(missing_note) + len(no_dc)
    if total_issues == 0 and (recorded == counted):
        print("\n健全。是正対象なし。")
    else:
        print(f"\n是正対象 {total_issues} 件（未評価 {len(unevaluated)} 件は別途 pending で処理）。")


# 次段階の量的しきい値（ctl-maturity-strategy.md）
_NEXT = {
    "CTL-0": ("CTL-1", 10, "いずれか 1 カテゴリで count≥10 かつ rate≥0.90"),
    "CTL-1": ("CTL-2", 30, "4 カテゴリ中 3 以上で count≥10 かつ rate≥0.90"),
    "CTL-2": ("CTL-3", 100, "全カテゴリで count≥25 かつ rate≥0.95"),
    "CTL-3": (None, None, "最上位（H 以外は全面自律・事後献上のみ）"),
}


def cmd_status(args) -> None:
    if not DATA_DIR.exists():
        print(f"未初期化（{DATA_DIR}）→ CTL-0。init してください。")
        return
    stats = _load_stats()
    ctl = calculate_ctl(stats)
    total = stats.get("total_invocations", 0)
    pending = sum(
        1 for _p, r in _iter_invocations()
        if not r.get("actual_outcome", {}).get("status")
    )
    print(f"現在の CTL: {ctl}")
    print(f"  評価済み判定: {total} 件 / 全体一致率: {stats.get('overall_agreement_rate', 0)}")
    if pending:
        print(f"  未評価: {pending} 件（CTL に未反映 — `pending` で確認 → 評価が燃料）")
    print(f"  委譲対象カテゴリ: {delegation_scope(stats) or '（なし）'}")
    print("  カテゴリ別:")
    for name in VALID_DECISION_CATEGORIES:
        c = stats.get("categories", {}).get(name)
        if c:
            print(f"    {name}: count={c['count']} agreed={c['agreed']} "
                  f"modified={c.get('modified', 0)} rate={c['agreement_rate']}")
        else:
            print(f"    {name}: （実績なし）")
    nxt, need, cond = _NEXT[ctl]
    if nxt:
        short = max(0, need - total)
        print(f"\n次段階 {nxt} まで:")
        print(f"  量: 評価済み {total}/{need} 件（あと {short} 件）")
        print(f"  質: {cond}")


def cmd_regime_block(args) -> None:
    """REGIME.md 用ブロックを出力（ctl-calculation.md §7）。"""
    _ensure_initialized()
    stats = _load_stats()
    ctl = calculate_ctl(stats)
    scope = delegation_scope(stats)
    esc = [c for c in VALID_DECISION_CATEGORIES if c not in scope]
    print("## Council Trust Level")
    print(f"- ctl: {ctl}")
    print(f"- ctl_calculated_at: {_now()}")
    print(f"- delegation_scope: [{', '.join(scope)}]")
    print(f"- escalation_categories: [{', '.join(esc)}]")
    print(f"- council_data_version: {DATA_VERSION}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init", help="council-data を初期化（CTL-0）")
    sp.add_argument("--force", action="store_true",
                    help="stats.json を再初期化（invocations/ は残る → recompute で復元可）")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("record", help="Council 発動を 1 件記録")
    sp.add_argument("--decision-category", required=True, help="C1|C2|C3|C4（H は記録不可）")
    sp.add_argument("--category", default="judgment",
                    help="重み配分用の自由文（operation/judgment/conception 等。CTL 算出は "
                         "decision_category 側で行うため本値は検証しない）")
    sp.add_argument("--council-type", default="business")
    sp.add_argument("--topic", required=True, help="抽象化した要約（80 字以内・固有名/コード断片禁止）")
    sp.add_argument("--judgment", required=True, help="抽象化した結論")
    sp.add_argument("--confidence", type=float, required=True)
    sp.add_argument("--consensus", default="auto_agree", help="auto_agree|escalate_to_human 等")
    sp.set_defaults(func=cmd_record)

    sp = sub.add_parser("pending", help="未評価（律速段階）の判定を一覧")
    sp.set_defaults(func=cmd_pending)

    sp = sub.add_parser("evaluate", help="事後評価して stats を再計算")
    sp.add_argument("id", help="invocation_id 全体 / 末尾 6 文字 / ファイル名")
    sp.add_argument("--status", required=True,
                    help="agreed|agreed_with_synthesis|modified|rejected")
    sp.add_argument("--note", default=None,
                    help="modifier_note（agreed 以外は必須）")
    sp.set_defaults(func=cmd_evaluate)

    sp = sub.add_parser("recompute", help="invocations/ から stats.json を再計算")
    sp.set_defaults(func=cmd_recompute)

    sp = sub.add_parser("audit", help="note 欠落・未評価・件数乖離を検出（決定論）")
    sp.set_defaults(func=cmd_audit)

    sp = sub.add_parser("status", help="現在の CTL と次段階までの不足を表示")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("regime-block", help="REGIME.md 用の CTL ブロックを出力")
    sp.set_defaults(func=cmd_regime_block)

    return p


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
