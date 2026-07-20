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

echo ""
echo "PASS: council-log-sync 全テスト通過"
