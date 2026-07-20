#!/usr/bin/env python3
"""council-log-sync — COUNCIL-LOG.md を単一情報源として council-data を導出する同期器。

CTL（Council Trust Level）記録経路の分断を解消する（upgrade-spec-v6.1.0）。

## なぜ必要か

`council-ctl.py record` は「Council 発動＝自動記録（毎回必須）」と規定されるが、
それを強制する実行主体が存在せず、手順書依存で空文化していた（発動 53 回に対し
CTL 用 user-scope 記録は 1 件）。一方 `history/COUNCIL-LOG.md`（project-scope,
append-only）には全発動が確実に追記されている。本ツールは COUNCIL-LOG を**単一
情報源**とし、そこから `~/.claude/council-data/invocations/` の invocation JSON を
決定論的に導出する。これにより「書く側の経路」の二重化を解消する。

## Council 判定で確定した設計制約

- **decision_category は機械導出しない**（`council-2026-07-01T-ctlrec1`）: COUNCIL-LOG に
  明示された値（C1〜C4 / H1〜H4）があればそれを使い、無ければ `null` で載せる。重み配分軸の
  `category`（conception/judgment 等）から `decision_category`（委譲軸）へ写像してはならない
  （両者は consensus-protocol.md §311-324 で直交と明記。写像は非全射で、埋めると
  「満ちているが意味は空」な統計になり CTL 算出が偽の確信を生む）。
- **可逆**: 本ツールは COUNCIL-LOG を読むだけの導出。council-data を消して再同期できる。
- **COUNCIL-LOG 単一ソース化**（`council-2026-07-01T-ctldedup`, 案A）: COUNCIL-LOG に対応する
  invocation は同期で**常に上書き**する（旧 marker 保護は撤廃）。COUNCIL-LOG に対応しない
  invocation（別採番の手動 record 等）は同一発動の二重計上源になりうるため `--prune` で掃除する。
  手動 record を使う時は必ず COUNCIL-LOG にも追記する運用（SKILL §CTL 記録）。`_source` marker は
  監査用の由来印として残すが、上書き可否の判定には使わない。

## actual_outcome.status への写像（implementer_consent 由来）

| implementer_consent           | status  | 根拠 |
|-------------------------------|---------|------|
| agreed_recommended            | agreed  | 推奨採用 |
| agreed_with_modification      | modified| 部分同意（consensus-protocol §119）|
| escalated / deferred_* / null | (未評価)| 結論未定・agreement を作らない → status=null |

未評価（status=null）は既存 _compute_stats の null-skip に委ねられ、統計に算入されない
（CTL の「未評価は pending に溜まり燃料にならない」設計と整合）。

## 使い方

    python3 scripts/council-log-sync.py sync                 # 既定 COUNCIL-LOG を同期
    python3 scripts/council-log-sync.py sync --dry-run       # 生成予定を出すだけ（書かない）
    python3 scripts/council-log-sync.py sync --log <path>    # 別の COUNCIL-LOG を指定
    python3 scripts/council-log-sync.py sync --recompute     # 同期後に stats.json も再計算
    python3 scripts/council-log-sync.py sync --prune         # 同一ログ内の別採番 record を掃除
                                                             # ※他プロジェクト由来も消える。下記警告参照

同期後の CTL 反映・事後評価は council-ctl.py に委ねる:
    python3 scripts/council-ctl.py recompute
    python3 scripts/council-ctl.py pending
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys
from pathlib import Path

# ---- パス（council-ctl.py と同一の user-scope に閉じる） ----------------------

DATA_DIR = Path(os.environ.get("COUNCIL_DATA_DIR", Path.home() / ".claude" / "council-data"))
INVOCATIONS_DIR = DATA_DIR / "invocations"

# 既定の COUNCIL-LOG（DH 本体一次情報源）。--log で上書き可。
DEFAULT_LOG = Path(__file__).resolve().parent.parent / "history" / "COUNCIL-LOG.md"

DATA_VERSION = "0.1"

# 同期由来 invocation の由来印（監査用）。上書き可否の判定には使わない（案A・単一ソース化）。
SYNC_MARKER = "council-log-sync"

# 記録として透過してよい decision_category の値域。C1-C4 に加え H1-H4 も**値として透過保持**する
# （H を null 化すると「H だった」履歴が失われ監査で H 発生を追えなくなる）。ただし CTL 統計への
# 算入は council-ctl.py の _compute_stats が C1-C4 のみに限定するため、H は記録に残るが統計には
# 入らない（SKILL §CTL 記録の「H は CTL 非記録」方針と実害なく整合）。C/H 以外の不正値のみ null 化。
VALID_DECISION_CATEGORIES = ("C1", "C2", "C3", "C4", "H1", "H2", "H3", "H4")

# implementer_consent → actual_outcome.status（未定義/None は未評価= None）
CONSENT_TO_STATUS = {
    "agreed_recommended": "agreed",
    "agreed_with_modification": "modified",
    # 表記ゆれ（利用プロジェクト側の語彙。同一軸の正規化であって軸間写像ではない）
    "agreed": "agreed",
    "approved": "agreed",
    "agreed_minority_opinion": "agreed",
    # escalated / deferred_pending_dependent / null は結論未定 → 未評価（None）
}

# 条件・置換を伴う同意は「推奨そのままではない」= modified 相当。接尾辞が可変
# （_with_3_conditions / _with_6_conditions / _with_substitution / _under_purity_caveat 等）
# のため完全一致テーブルでは網羅できず、接頭辞 + マーカーで正規化する。
#
# なぜ機械導出禁止（council-2026-07-01T-ctlrec1）に抵触しないか:
#   却下されたのは category（重み軸）→ decision_category（委譲軸）という**直交する別軸**への
#   写像。ここは implementer_consent → status の**同一軸内の表記ゆれ正規化**であり、
#   「同意したが推奨そのままではない」という原文の意味を保存する方向にしか動かさない。
_CONDITIONAL_MARKERS = ("_with_", "_under_")


def normalize_consent(consent: str | None) -> str | None:
    """implementer_consent を actual_outcome.status へ正規化する。

    完全一致 → 条件付き同意（modified）→ 未評価（None）の順で判定する。
    """
    if not consent:
        return None
    v = consent.strip()
    if v in CONSENT_TO_STATUS:
        return CONSENT_TO_STATUS[v]
    # agreed_* / approved_* に条件・置換マーカーが付くものは modified
    if v.startswith(("agreed", "approved")) and any(m in v for m in _CONDITIONAL_MARKERS):
        return "modified"
    # 上記以外の agreed_* 派生は素直な同意として扱う
    if v.startswith(("agreed", "approved")):
        return "agreed"
    return None


def _now() -> str:
    # Date.now 相当は council-ctl.py 側の評価時刻で持つ。同期は生成時刻を持たない
    # （再同期で不変にするため。synced_at はファイル mtime で十分）。
    return ""


# ---- COUNCIL-LOG パーサ（subset YAML・依存ゼロ） ------------------------------
#
# COUNCIL-LOG のエントリは `^- invocation_id: "..."` で始まり、以降 `^  <key>: <value>`
# がフィールドとして続くブロック形式。PyYAML を入れない（独立性要請・情報純度）。
# 必要なトップレベルスカラーフィールドのみを抽出する。ネスト（persona_summary 等）は
# 同期に使わないので読み飛ばす。


_ENTRY_START = re.compile(r'^- invocation_id:\s*"?([^"\n]+)"?\s*$')
_FIELD = re.compile(r'^  ([a-z_]+):\s*(.*)$')


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


def parse_council_log(text: str) -> list[dict]:
    """COUNCIL-LOG.md からエントリの必要フィールドを抽出する。

    トップレベル（2 スペース字下げ）のスカラーフィールドのみ拾う。ネストブロックや
    より深い字下げ行はフィールド値としては読まない（entry 境界の判定だけ維持）。
    """
    entries: list[dict] = []
    cur: dict | None = None
    for raw in text.splitlines():
        m_start = _ENTRY_START.match(raw)
        if m_start:
            if cur is not None:
                entries.append(cur)
            cur = {"invocation_id": _unquote(m_start.group(1))}
            continue
        if cur is None:
            continue
        m_field = _FIELD.match(raw)
        if m_field:
            key, val = m_field.group(1), m_field.group(2)
            # ネスト親（値が空でコロン終わり）は無視。スカラーのみ格納。
            if val == "" or val.rstrip().endswith(":"):
                continue
            # 同一キーが二重定義された場合は**後勝ち**で上書きする。COUNCIL-LOG は
            # append-only 例外条項で「null 宣言済みフィールドへの単方向埋め込み」を許容する
            # （output-format.md §後追記）。実値が後の行で追記されうるため、先勝ち(setdefault)だと
            # 後追記の implementer_consent 等を取り落とし status=null で CTL データが欠落する。
            cur[key] = _unquote(val)
    if cur is not None:
        entries.append(cur)
    return entries


# ---- invocation への変換（council-ctl.py スキーマ厳守） -----------------------


def _norm_decision_category(raw: str | None) -> str | None:
    """decision_category を機械導出せず、明示された C/H 値のみ採用。

    不正値（"implementation" 等、category が誤って入ったもの）や欠落は None。
    None は _compute_stats の null-skip に委ねられる。
    """
    if raw is None:
        return None
    v = raw.strip()
    return v if v in VALID_DECISION_CATEGORIES else None


def _filename_for(invocation_id: str) -> str:
    """council-ctl.py と同じ命名規則: <ISO8601Z のコロン→ハイフン>-<末尾6文字>.json。

    invocation_id は "council-<ts>-<suffix>" 形式。**council-ctl.py cmd_record と同一の命名規則**
    （`<ts のコロン→ハイフン>-<suffix>.json`、`council-` プレフィックス無し）に揃える。これにより
    同一 invocation_id の手動 record ファイルと同期版が**同一ファイル名**になり、上書きで一本化される
    （揃えないと別名で共存し二重計上源になる — 独立レビュー問題1）。

    先頭の "council-" を剥がしてから、残りの ts 部のコロンをハイフン化する。
    """
    body = invocation_id[len("council-"):] if invocation_id.startswith("council-") else invocation_id
    return f"{body.replace(':', '-')}.json"


def entry_to_invocation(entry: dict) -> dict:
    """COUNCIL-LOG エントリ 1 件を council-data invocation JSON に変換する。"""
    consent = entry.get("implementer_consent")
    status = normalize_consent(consent)

    outcome = {
        "status": status,
        "evaluated_at": entry.get("agreed_at") if status else None,
        "modifier_note": entry.get("modification_note"),
    }

    return {
        "invocation_id": entry["invocation_id"],
        "council_type": entry.get("council_type", "business"),
        "category": entry.get("category"),
        "decision_category": _norm_decision_category(entry.get("decision_category")),
        "topic_summary": (entry.get("question_to_answer") or "")[:80],
        "judgment": entry.get("recommended"),
        "judgment_confidence": _to_float(entry.get("judgment_confidence")),
        "consensus_mode": entry.get("consensus_mode"),
        "ctl_at_invocation": entry.get("ctl"),
        "actual_outcome": outcome,
        # 同期由来の目印。再同期で上書きしてよいファイルを限定するため。
        "_source": SYNC_MARKER,
    }


def _to_float(v):
    if v is None:
        return None
    with contextlib.suppress(ValueError, TypeError):
        return float(v)
    return None


# ---- I/O（council-ctl.py の _atomic_write と同型） ----------------------------


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import secrets

    tmp = path.with_name(f".{path.name}.{os.getpid()}.{secrets.token_hex(2)}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        with contextlib.suppress(OSError):
            tmp.unlink(missing_ok=True)


def _iter_local_invocations():
    """council-data/invocations/ の既存ファイルを (path, record) で列挙する。"""
    if not INVOCATIONS_DIR.exists():
        return
    for path in sorted(INVOCATIONS_DIR.glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            rec = {}
        yield path, rec


# ---- サブコマンド ------------------------------------------------------------


def cmd_sync(args) -> None:
    """COUNCIL-LOG を単一情報源として council-data を導出する（案A: 単一ソース化）。

    Council 諮問 council-2026-07-01T-ctldedup（unanimous 案A）で確定:
    同期版（_source=sync）は COUNCIL-LOG に従い常に上書きする（marker 保護は撤廃）。
    手動 record（別採番・COUNCIL-LOG 未反映）は同一発動の二重計上源になりうるため、
    --prune で掃除する。手動 record の正しい使い方は「即記録すると同時に COUNCIL-LOG へ
    追記する」であり、追記されれば同期で正規版に一本化される（SKILL §CTL 記録）。
    """
    log_path = Path(args.log) if args.log else DEFAULT_LOG
    if not log_path.exists():
        sys.exit(f"COUNCIL-LOG が見つかりません: {log_path}")

    log_text = log_path.read_text(encoding="utf-8")

    # 書式逸脱センサー（2026-07-20）: 見出し形式（`## council-...`）の記録はパーサが読めず
    # CTL に載らない。silent 素通りさせず warn で可視化する（検出のみ・削除/自動変換しない）。
    heading_records = re.findall(r"^#{2,}\s+(council-[\w:.\-]+)", log_text, re.M)
    if heading_records:
        print(f"  警告: 同期対象外の見出し形式記録（## council-...）が {len(heading_records)} 件あります"
              f"（CTL に載りません）。output-format.md §8 のブロック形式へ転記してください:")
        for h in heading_records:
            print(f"    - {h}")

    entries = parse_council_log(log_text)
    if not entries:
        print(f"エントリなし: {log_path}")
        return

    # COUNCIL-LOG 由来の正規ファイル名集合（prune の生存判定に使う）。
    canonical_names = {_filename_for(e["invocation_id"]) for e in entries}

    written = unchanged = 0
    evaluated = 0
    null_dc = 0
    for entry in entries:
        inv = entry_to_invocation(entry)
        if inv["actual_outcome"]["status"]:
            evaluated += 1
        if inv["decision_category"] is None:
            null_dc += 1

        dest = INVOCATIONS_DIR / _filename_for(inv["invocation_id"])
        payload = json.dumps(inv, ensure_ascii=False, indent=2) + "\n"

        # 冪等: 内容が同一なら書かない（mtime を無駄に更新しない）。
        if dest.exists():
            with contextlib.suppress(OSError):
                if dest.read_text(encoding="utf-8") == payload:
                    unchanged += 1
                    continue

        if args.dry_run:
            written += 1
            continue
        _atomic_write(dest, payload)
        written += 1

    # --- prune: COUNCIL-LOG に対応しない孤児（手動 record 由来含む）を掃除 ---
    orphans = [
        (path, rec) for path, rec in _iter_local_invocations()
        if path.name not in canonical_names
    ]
    pruned = 0
    if args.prune:
        for path, _rec in orphans:
            if args.dry_run:
                pruned += 1
                continue
            with contextlib.suppress(OSError):
                path.unlink()
                pruned += 1

    verb = "生成予定" if args.dry_run else "同期"
    print(f"{verb}: {len(entries)} エントリ中 "
          f"{written} 件 {verb} / {unchanged} 件 変更なし")
    print(f"  うち事後評価済み(status非null): {evaluated} 件 / "
          f"decision_category=null: {null_dc} 件（明示なしは導出せず null 保持）")
    if args.prune:
        print(f"  prune: COUNCIL-LOG 非対応の孤児 {pruned} 件を掃除"
              f"（手動 record の二重計上を解消・案A）")
    elif orphans:
        print(f"  参考: このログに対応しない invocation が {len(orphans)} 件あります")
        print(f"    council-data は user-scope でプロジェクト横断（philosophy 第 6 条）ゆえ、"
              f"他プロジェクト由来ならこれは正常です。")
        print(f"    --prune はこれらを**全件削除**します。同一ログ内の別採番 record を掃除する"
              f"目的でのみ、削除対象を確認した上で使ってください。")

    if args.dry_run:
        print("  （--dry-run: 何も書き込んでいません）")
        return

    if args.recompute:
        _invoke_recompute()


def _invoke_recompute() -> None:
    """council-ctl.py recompute を同一プロセス内で呼ぶ（import 経由）。"""
    ctl = Path(__file__).resolve().parent / "council-ctl.py"
    if not ctl.exists():
        print("  （council-ctl.py 不在のため recompute skip。手動で recompute してください）",
              file=sys.stderr)
        return
    import importlib.util

    spec = importlib.util.spec_from_file_location("council_ctl", ctl)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    mod._recompute(quiet=False)  # noqa: SLF001 — CTL 表示は _recompute 内で行う


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("sync", help="COUNCIL-LOG → council-data を同期")
    sp.add_argument("--log", default=None, help="COUNCIL-LOG.md のパス（既定: DH history/）")
    sp.add_argument("--dry-run", action="store_true", help="生成予定を出すだけ（書かない）")
    sp.add_argument("--recompute", action="store_true", help="同期後に stats.json を再計算")
    sp.add_argument("--prune", action="store_true",
                    help="COUNCIL-LOG に対応しない孤児 invocation（手動 record 二重計上等）を削除")
    sp.set_defaults(func=cmd_sync)

    return p


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
