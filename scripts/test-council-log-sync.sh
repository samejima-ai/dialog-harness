#!/usr/bin/env bash
# council-log-sync.py の回帰テスト。
#
# COUNCIL-LOG.md → council-data 同期の正しさを、隔離した一時 COUNCIL_DATA_DIR と
# 合成 COUNCIL-LOG フィクスチャ上で end-to-end に検証する。
# ~/.claude/council-data には一切触れない。
#
# 検証項目:
#   1. パース: エントリ抽出とフィールド写像
#   2. decision_category を機械導出しない（明示のみ採用・不正値/欠落は null）
#   3. implementer_consent → actual_outcome.status 写像
#   4. 冪等性（2 回目は全件「変更なし」）
#   5. COUNCIL-LOG 対応ファイルは常に上書き + 孤児を --prune で掃除（単一ソース化 §2.4b）
#   6. council-ctl.py が同期由来 invocation を壊さず recompute できる
#   7. 可逆性（council-data を消して再同期すると同一結果）
#   8. 事後評価の保存（council-ctl.py evaluate 由来の status を同期が壊さない）
#
# 使い方: bash scripts/test-council-log-sync.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# python3 が無い環境（Windows native 等）では python にフォールバック
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
SYNC="$PY $HERE/council-log-sync.py"
CTL="$PY $HERE/council-ctl.py"

export COUNCIL_DATA_DIR="$(mktemp -d)/council-data"
LOG="$(mktemp)"
trap 'rm -rf "$COUNCIL_DATA_DIR" "$LOG" "${LOG}.heading"' EXIT

fail() { echo "FAIL: $1" >&2; exit 1; }
ok()   { echo "  ok: $1"; }

# ---- フィクスチャ: 代表的なパターンを網羅した合成 COUNCIL-LOG ----------------
cat > "$LOG" <<'EOF'
# COUNCIL-LOG (test fixture)

- invocation_id: "council-2026-01-01T00:00:00Z-aaa111"
  timestamp: "2026-01-01T00:00:00Z"
  source_skill: "layer1-autonomous-dev"
  question_to_answer: "案 A と案 B のどちらを採るか"
  council_type: "business"
  category: "conception"
  decision_category: "C2"
  judgment_confidence: 0.85
  consensus_mode: "auto_agree"
  recommended: "案 A を推奨"
  human_escalated: false
  implementer_consent: "agreed_recommended"
  agreed_at: "2026-01-01T01:00:00Z"

- invocation_id: "council-2026-01-02T00:00:00Z-bbb222"
  timestamp: "2026-01-02T00:00:00Z"
  category: "judgment"
  decision_category: "C1"
  judgment_confidence: 0.7
  recommended: "案 B を推奨"
  implementer_consent: "agreed_with_modification"
  modification_note: "少数意見を mitigation に採用"
  agreed_at: "2026-01-02T01:00:00Z"

- invocation_id: "council-2026-01-03T00:00:00Z-ccc333"
  category: "implementation"
  decision_category: "implementation"
  judgment_confidence: 0.6
  recommended: "案 C"
  implementer_consent: "agreed_recommended"
  agreed_at: "2026-01-03T01:00:00Z"

- invocation_id: "council-2026-01-04T00:00:00Z-ddd444"
  category: "conception"
  judgment_confidence: 0.5
  recommended: "案 D"
  implementer_consent: "deferred_pending_dependent"
  deferred_reason: "依存待ち"
  agreed_at: "2026-01-04T01:00:00Z"

- invocation_id: "council-2026-01-05T00:00:00Z-eee555"
  category: "conception"
  decision_category: "C2"
  judgment_confidence: 0.4
  recommended: "案 E"
  human_escalated: true
  implementer_consent: null
  # 後追記（append-only 例外条項）: 上の null 宣言に実値を単方向埋め込み。後勝ちで採るべき
  implementer_consent: "agreed_recommended"
EOF

field() {
  # $1=file $2=jq-less キー抽出（python でパース）
  $PY - "$1" "$2" <<'PYEOF'
import json, sys
rec = json.load(open(sys.argv[1], encoding="utf-8"))
keys = sys.argv[2].split(".")
v = rec
for k in keys:
    v = v.get(k) if isinstance(v, dict) else None
print("null" if v is None else v)
PYEOF
}

# council-log-sync の命名規則（council-ctl.py と同一: council- プレフィックス無し）に合わせ、
# 引数の "council-" プレフィックスを剥いだファイル名を返す。
inv_file() { echo "$COUNCIL_DATA_DIR/invocations/${1#council-}.json"; }

echo "== 1. dry-run は何も書かない =="
$SYNC sync --log "$LOG" --dry-run >/dev/null
[ ! -d "$COUNCIL_DATA_DIR/invocations" ] || [ -z "$(ls -A "$COUNCIL_DATA_DIR/invocations" 2>/dev/null)" ] \
  || fail "dry-run がファイルを書いた"
ok "dry-run 非書込"

echo "== 2. 実同期で 5 エントリ生成 =="
$SYNC sync --log "$LOG" >/dev/null
n="$(ls "$COUNCIL_DATA_DIR/invocations/" | wc -l | tr -d ' ')"
[ "$n" = "5" ] || fail "生成数 期待 5 / 実際 $n"
ok "5 エントリ生成"

echo "== 3. decision_category: 明示のみ採用・不正/欠落は null =="
f="$(inv_file council-2026-01-01T00-00-00Z-aaa111)"
[ "$(field "$f" decision_category)" = "C2" ] || fail "aaa111 の C2 が採れていない"
ok "明示 C2 採用"
f="$(inv_file council-2026-01-03T00-00-00Z-ccc333)"
[ "$(field "$f" decision_category)" = "null" ] || fail "ccc333 の不正値(implementation)が null 化されていない"
ok "不正値 → null（機械導出しない）"
f="$(inv_file council-2026-01-04T00-00-00Z-ddd444)"
[ "$(field "$f" decision_category)" = "null" ] || fail "ddd444 の欠落が null になっていない"
ok "欠落 → null"

echo "== 4. implementer_consent → status 写像 =="
f="$(inv_file council-2026-01-01T00-00-00Z-aaa111)"
[ "$(field "$f" actual_outcome.status)" = "agreed" ] || fail "agreed_recommended → agreed 失敗"
ok "agreed_recommended → agreed"
f="$(inv_file council-2026-01-02T00-00-00Z-bbb222)"
[ "$(field "$f" actual_outcome.status)" = "modified" ] || fail "agreed_with_modification → modified 失敗"
ok "agreed_with_modification → modified"
f="$(inv_file council-2026-01-04T00-00-00Z-ddd444)"
[ "$(field "$f" actual_outcome.status)" = "null" ] || fail "deferred → null(未評価) 失敗"
# rejected 系（Council 推奨の人間 override 等）は rejected として統計の分母に入る
out="$($PY - "$HERE/council-log-sync.py" <<'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("s", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
assert m.normalize_consent("rejected") == "rejected"
assert m.normalize_consent("rejected_human_override") == "rejected"
print("ok")
PYEOF
)"
[ "$out" = "ok" ] || fail "rejected 系の写像失敗: $out"
ok "rejected / rejected_* → rejected"
ok "deferred → 未評価(null)"
echo "== 4b. 同一キー後追記は後勝ち（append-only null→実値の単方向埋め込み）=="
f="$(inv_file council-2026-01-05T00-00-00Z-eee555)"
# eee555 は null 宣言後に "agreed_recommended" を後追記 → 後勝ちで agreed になるべき
[ "$(field "$f" actual_outcome.status)" = "agreed" ] || fail "後追記 consent が後勝ちで採れていない（setdefault 退行）"
ok "後追記は後勝ち（CTL データ欠落を防止）"

echo "== 5. 冪等性: 2 回目は全件変更なし =="
out="$($SYNC sync --log "$LOG")"
echo "$out" | grep -q "0 件 同期 / 5 件 変更なし" || fail "冪等でない: $out"
ok "冪等"

echo "== 6. COUNCIL-LOG 対応ファイルは常に上書き（案A: 単一ソース化） =="
# aaa111 を手で書き換えても、COUNCIL-LOG に対応がある以上、同期で正規版に戻る
manual="$(inv_file council-2026-01-01T00-00-00Z-aaa111)"
$PY - "$manual" <<'PYEOF'
import json, sys
p = sys.argv[1]
rec = json.load(open(p, encoding="utf-8"))
rec["judgment"] = "TAMPERED"
json.dump(rec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PYEOF
$SYNC sync --log "$LOG" >/dev/null
[ "$(field "$manual" judgment)" = "案 A を推奨" ] || fail "COUNCIL-LOG 対応ファイルが上書きされない（単一ソース化の破れ）"
ok "COUNCIL-LOG 対応は常に上書き"

echo "== 6b. 孤児（COUNCIL-LOG 非対応の手動 record）を --prune で掃除 =="
# COUNCIL-LOG に無い invocation_id の手動 record を置く（同一発動の別採番を模す）
# council-ctl.py record が作る命名（council- プレフィックス無し）で、COUNCIL-LOG に無い孤児を置く
orphan="$COUNCIL_DATA_DIR/invocations/2026-01-01T09-99-99Z-manual1.json"
cat > "$orphan" <<'JSON'
{"invocation_id":"council-2026-01-01T09:99:99Z-manual1","decision_category":"C2","actual_outcome":{"status":"agreed"}}
JSON
# prune なしでは孤児は残り、注意が出る
out="$($SYNC sync --log "$LOG")"
echo "$out" | grep -q "対応しない invocation が 1 件" || fail "孤児の注意が出ない: $out"
[ -f "$orphan" ] || fail "prune なしで孤児が消えた"
ok "prune なし: 孤児は残り注意表示"
# --prune で孤児掃除
out="$($SYNC sync --log "$LOG" --prune)"
echo "$out" | grep -q "孤児 1 件を掃除" || fail "prune が掃除しない: $out"
[ ! -f "$orphan" ] || fail "prune 後も孤児が残る"
ok "prune: 孤児を掃除（二重計上解消）"

echo "== 7. council-ctl.py が同期由来を壊さず recompute（評価済み 3 件） =="
# 手動編集した aaa111 を戻すため council-data を消して再同期（可逆性テスト兼）
rm -rf "$COUNCIL_DATA_DIR/invocations"
$SYNC sync --log "$LOG" --recompute >/dev/null
# 評価済み = agreed(C2 aaa111) + modified(C1 bbb222) + agreed(C2 eee555 後勝ち) = 3 件。
# ccc333 は dc=null で skip、ddd444 は deferred で未評価。
total="$($CTL status | sed -n 's/^ *評価済み判定: \([0-9]*\) .*/\1/p' | head -1)"
[ "$total" = "3" ] || fail "評価済み 期待 3 / 実際 $total（dc=null は算入されないはず）"
ok "recompute: 評価済み 3 件（dc=null は統計除外）"

echo "== 8. 可逆性: 消して再同期で同一結果 =="
signature() {
  # 全 invocation の (ファイル名 : decision_category : status) を安定ソートで連ねる
  cd "$COUNCIL_DATA_DIR/invocations" && for x in *.json; do
    echo "$x:$(field "$COUNCIL_DATA_DIR/invocations/$x" decision_category):$(field "$COUNCIL_DATA_DIR/invocations/$x" actual_outcome.status)"
  done | sort
}
sig1="$(signature)"
[ -n "$sig1" ] || fail "signature が空（テストヘルパ不良）"
rm -rf "$COUNCIL_DATA_DIR/invocations"
$SYNC sync --log "$LOG" >/dev/null
sig2="$(signature)"
[ "$sig1" = "$sig2" ] || fail "再同期で結果が変わった（非可逆）"
ok "可逆（再同期で同一）"

echo "== 9. 書式逸脱センサー: 見出し形式（## council-...）を warn で可視化 =="
# 見出し形式の記録（パーサ非対応 = CTL に載らない）を混ぜ、warn が出ることを確認
LOG_HEADING="${LOG}.heading"
cp "$LOG" "$LOG_HEADING"
cat >> "$LOG_HEADING" <<'MD'

## council-2026-01-02T-heading1 — 見出し形式の記録（自由 Markdown）

- **recommended**: 案 X を採用
MD
out="$($SYNC sync --log "$LOG_HEADING" --dry-run)"
echo "$out" | grep -q "見出し形式記録（## council-...）が 1 件" || fail "見出し形式の warn が出ない: $out"
echo "$out" | grep -q "council-2026-01-02T-heading1" || fail "見出し形式の id が列挙されない: $out"
# 見出し形式は同期対象にならない（エントリ数が増えない）こと
echo "$out" | grep -q "heading1.json" && fail "見出し形式が誤って同期対象になった"
ok "見出し形式センサー: warn + id 列挙 + 同期対象外"
# 見出しが無いログでは warn が出ないこと
out="$($SYNC sync --log "$LOG" --dry-run)"
echo "$out" | grep -q "見出し形式記録" && fail "見出しが無いのに warn が出た: $out"
ok "見出しなしログでは warn なし"

# --- 8. 事後評価の保存（回帰テスト・2026-08-25 追加） ---------------------------
#
# 背景（実測された欠陥）: actual_outcome は COUNCIL-LOG の implementer_consent とは
# 別軸の情報で、振り返り儀式 F2.5 が `council-ctl.py evaluate` で council-data 側に
# 書く（SKILL.md §CTL 記録「事後評価は record とは分離する」）。しかし同期が
# COUNCIL-LOG 由来の値で無条件に上書きしていたため、人間が下した評価が
# 「COUNCIL-LOG 側の古い implementer_consent（deferred_* 等 → null）」で消えていた。
# 実損害: DH 本体で評価済み 55 → 52 件。消えるのは rejected/modified（一致率を下げる
# 負例）が主なので rate は 0.8545 → 0.8846 と**上がって見える** = CTL が実態より高く
# 出る方向に壊れる。
#
# 規則: COUNCIL-LOG 由来が非 null ならそれを採る（単一情報源原則）。null のときだけ
#       既存の非 null を保存する。
$SYNC sync --log "$LOG" >/dev/null
# ddd444 は implementer_consent: deferred_pending_dependent = 導出すると status null。
# これを人間が振り返り儀式で「rejected」と事後評価した状況を作る。
$CTL evaluate "ddd444" --status rejected >/dev/null
# 再同期しても評価が消えないこと（消えていたのが本欠陥）
out="$($SYNC sync --log "$LOG")"
echo "$out" | grep -q "事後評価を保存: 1 件" || fail "保存件数が報告されない: $out"
got="$($PY - "$COUNCIL_DATA_DIR" <<'PYEOF'
import json, pathlib, sys
for f in pathlib.Path(sys.argv[1], "invocations").glob("*.json"):
    rec = json.loads(f.read_text(encoding="utf-8"))
    if rec["invocation_id"].endswith("ddd444"):
        print(rec["actual_outcome"]["status"] or "<wiped>"); break
PYEOF
)"
[ "$got" = "rejected" ] || fail "再同期で事後評価が壊れた: $got (expected rejected)"
# COUNCIL-LOG 側が非 null のエントリは従来どおり COUNCIL-LOG が勝つ（単一情報源原則）
$CTL evaluate "aaa111" --status rejected >/dev/null
$SYNC sync --log "$LOG" >/dev/null
got2="$($PY - "$COUNCIL_DATA_DIR" <<'PYEOF'
import json, pathlib, sys
for f in pathlib.Path(sys.argv[1], "invocations").glob("*.json"):
    rec = json.loads(f.read_text(encoding="utf-8"))
    if rec["invocation_id"].endswith("aaa111"):
        print(rec["actual_outcome"]["status"]); break
PYEOF
)"
[ "$got2" = "agreed" ] || fail "COUNCIL-LOG 非 null が上書きされない: $got2 (expected agreed)"
ok "事後評価の保存: 再同期で evaluate 由来の status が消えない"

# 8b. invocation_id ガード（Copilot review #190）: ファイル名と中身が不一致なら取り込まない
#     council-data は「スクリプトが無いプロジェクトは invocation JSON を直接書く」手書き経路が
#     認められている領域（SKILL.md §CTL 記録 2.）ゆえ、名前と中身の不一致は現実に起こりうる。
#     別 invocation の評価を誤って取り込むと、偽の agreement が CTL に混入する。
$PY - "$COUNCIL_DATA_DIR" <<'PYEOF'
import json, pathlib, sys
for f in pathlib.Path(sys.argv[1], "invocations").glob("*ddd444.json"):
    rec = json.loads(f.read_text(encoding="utf-8"))
    rec["invocation_id"] = "council-2099-01-01T00:00:00Z-zzz999"   # 中身だけ別 invocation に差し替え
    rec["actual_outcome"] = {"status": "agreed", "evaluated_at": None, "modifier_note": None}
    f.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PYEOF
out="$($SYNC sync --log "$LOG")"
echo "$out" | grep -q "invocation_id が不一致" || fail "不一致の warn が出ない: $out"
echo "$out" | grep -q "zzz999" || fail "不一致の中身 id が列挙されない: $out"
got3="$($PY - "$COUNCIL_DATA_DIR" <<'PYEOF'
import json, pathlib, sys
for f in pathlib.Path(sys.argv[1], "invocations").glob("*ddd444.json"):
    rec = json.loads(f.read_text(encoding="utf-8"))
    print(rec["actual_outcome"]["status"] or "<none>"); break
PYEOF
)"
[ "$got3" = "<none>" ] || fail "不一致ファイルから評価を誤って取り込んだ: $got3"
ok "invocation_id ガード: 名前と中身が不一致なら取り込まず warn"

# 8c. 行末コメント（COUNCIL-LOG がファイル全体で使う書式）を剥がして値を読むこと。
#     剥がさないと `implementer_consent: "agreed"  # 人間合意…` が丸ごと値になり、
#     normalize_consent が None を返して**人間の事後評価が静かに落ちる**。
LOG_CMT="${LOG}.cmt"
cat > "$LOG_CMT" <<'MD'
- invocation_id: "council-2026-02-01T00:00:00Z-cmt111"
  category: "conception"
  decision_category: "C2"
  judgment_confidence: 0.7
  recommended: "案 C"
  implementer_consent: "agreed_recommended"  # 2026-02-01 人間決定「推奨で進めて良い」
  agreed_at: "2026-02-01T01:00:00Z"
MD
rm -rf "$COUNCIL_DATA_DIR"
$SYNC sync --log "$LOG_CMT" >/dev/null
got4="$($PY - "$COUNCIL_DATA_DIR" <<'PYEOF'
import json, pathlib, sys
for f in pathlib.Path(sys.argv[1], "invocations").glob("*cmt111.json"):
    rec = json.loads(f.read_text(encoding="utf-8"))
    print(f"{rec['actual_outcome']['status']}|{rec['decision_category']}|{rec['judgment_confidence']}")
    break
PYEOF
)"
[ "$got4" = "agreed|C2|0.7" ] || fail "行末コメント付きの値が読めない: $got4 (expected agreed|C2|0.7)"
ok "行末コメント: 値の後ろの注釈を剥がして読む"
rm -f "$LOG_CMT"



echo ""
echo "PASS: council-log-sync 全テスト通過"
