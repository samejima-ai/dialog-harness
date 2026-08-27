#!/usr/bin/env bash
# council-ctl.py の回帰テスト。
#
# CTL 算出ロジック（ctl-calculation.md §3）と事後評価ループ全体を、
# 隔離した一時 COUNCIL_DATA_DIR 上で end-to-end に検証する。
# ~/.claude/council-data には一切触れない。
#
# 使い方: bash scripts/test-council-ctl.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# python3 が無い環境（Windows native 等）では python にフォールバック
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
CLI="$PY $HERE/council-ctl.py"
export COUNCIL_DATA_DIR="$(mktemp -d)"
trap 'rm -rf "$COUNCIL_DATA_DIR"' EXIT

fail() { echo "FAIL: $1" >&2; exit 1; }
assert_ctl() {
  local want="$1"
  local got
  got="$($CLI status | sed -n 's/^現在の CTL: //p' | head -1)"
  [ "$got" = "$want" ] || fail "CTL 期待 $want / 実際 $got"
  echo "  ok: $want"
}

# record を 1 件 + agreed 評価する小ヘルパ（decision_category を引数に）
record_agreed() {
  local dc="$1" status="${2:-agreed}"
  local out sid
  out="$($CLI record --decision-category "$dc" --topic "t" --judgment "j" --confidence 0.8)"
  # 「記録: council-<ts>-<suffix>」の末尾フィールド（suffix）を取る。
  # ts 自体が '-' を含むため最右マッチではなく最終フィールドで取り堅牢化。
  sid="$(echo "$out" | awk -F- '/^記録: council-/{print $NF}' | head -1)"
  # agreed 以外は --note 必須（ctl-calculation.md §4）。テストでは定型文を渡す。
  if [ "$status" = "agreed" ]; then
    $CLI evaluate "$sid" --status "$status" >/dev/null
  else
    $CLI evaluate "$sid" --status "$status" --note "test fixture: $status" >/dev/null
  fi
}

echo "== record は未初期化でも lazy-init して落ちない =="
# init を呼ばず、まっさらな dir に直接 record（発動＝自動 record の前提）
LAZY_DIR="$(mktemp -d)"
COUNCIL_DATA_DIR="$LAZY_DIR" $CLI record --decision-category C2 --topic t --judgment j --confidence 0.8 >/dev/null 2>&1 \
  || fail "未初期化 record が失敗した（lazy-init していない）"
[ -f "$LAZY_DIR/stats.json" ] || fail "lazy-init で stats.json が作られていない"
[ "$(COUNCIL_DATA_DIR="$LAZY_DIR" $CLI pending | grep -c '\[')" -eq 1 ] || fail "lazy-init 後 pending=1 でない"
rm -rf "$LAZY_DIR"
echo "  ok: 未初期化でも record が自動初期化して記録"

echo "== 破損 stats.json は invocations/ から自己修復（CTL を 0 に誤算出しない）=="
CORRUPT_DIR="$(mktemp -d)"
export COUNCIL_DATA_DIR_SAVE="$COUNCIL_DATA_DIR"
COUNCIL_DATA_DIR="$CORRUPT_DIR" $CLI init >/dev/null
# 健全な評価済み invocation を 10 件積んで CTL-1 を成立させる
for _ in $(seq 1 10); do
  out="$(COUNCIL_DATA_DIR="$CORRUPT_DIR" $CLI record --decision-category C2 --topic t --judgment j --confidence 0.8)"
  sid="$(echo "$out" | awk -F- '/^記録: council-/{print $NF}' | head -1)"
  COUNCIL_DATA_DIR="$CORRUPT_DIR" $CLI evaluate "$sid" --status agreed >/dev/null
done
# stats.json だけ破壊（invocations/ は健全）
echo "{ broken" > "$CORRUPT_DIR/stats.json"
COUNCIL_DATA_DIR="$CORRUPT_DIR" $CLI status >/dev/null 2>/dev/null || fail "破損 stats.json で status が落ちた"
HEALED="$(COUNCIL_DATA_DIR="$CORRUPT_DIR" $CLI status 2>/dev/null | sed -n 's/^現在の CTL: //p' | head -1)"
[ "$HEALED" = "CTL-1" ] || fail "破損 stats でも自己修復して CTL-1 のはず（実際 $HEALED）"
COUNCIL_DATA_DIR="$CORRUPT_DIR" $CLI recompute >/dev/null 2>/dev/null || fail "破損 stats.json で recompute が落ちた"
# パスは環境変数で渡す（-c 内の文字列リテラルだと MSYS が /tmp を Windows パスへ
# 翻訳せず、Git Bash + native python の組み合わせで FileNotFound になる）。
COUNCIL_DATA_DIR="$CORRUPT_DIR" $PY -c "import json,os,pathlib; json.load(open(pathlib.Path(os.environ['COUNCIL_DATA_DIR'])/'stats.json'))" \
  || fail "recompute 後も stats.json が不正"
rm -rf "$CORRUPT_DIR"
echo "  ok: 破損 stats を invocations/ から自己修復（CTL-1 維持）＋recompute で永続化"

echo "== init → CTL-0 =="
$CLI init >/dev/null
assert_ctl "CTL-0"

echo "== H カテゴリは記録拒否 =="
if $CLI record --decision-category H --topic t --judgment j --confidence 0.8 >/dev/null 2>&1; then
  fail "H カテゴリが記録できてしまった"
fi
echo "  ok: H は記録不可"

echo "== confidence 範囲外は記録拒否 =="
if $CLI record --decision-category C2 --topic t --judgment j --confidence 1.2 >/dev/null 2>&1; then
  fail "confidence 1.2 が記録できてしまった"
fi
if $CLI record --decision-category C2 --topic t --judgment j --confidence -0.1 >/dev/null 2>&1; then
  fail "confidence -0.1 が記録できてしまった"
fi
echo "  ok: confidence は 0.0〜1.0 のみ"

echo "== 破損 JSON は skip して落ちない =="
echo "{ broken json" > "$COUNCIL_DATA_DIR/invocations/9999-99-99T99-99-99Z-badbad.json"
$CLI status >/dev/null 2>/dev/null || fail "破損ファイルで status が落ちた"
rm -f "$COUNCIL_DATA_DIR/invocations/9999-99-99T99-99-99Z-badbad.json"
echo "  ok: 破損ファイルを skip"

echo "== 未評価は CTL に未反映（pending 律速）=="
$CLI record --decision-category C2 --topic t --judgment j --confidence 0.8 >/dev/null
assert_ctl "CTL-0"   # 記録しただけでは上がらない
[ "$($CLI pending | grep -c '\[')" -eq 1 ] || fail "pending が 1 件でない"
echo "  ok: 記録のみでは CTL-0、pending=1"

echo "== 再評価で --note 省略時は既存 note を保持 =="
PSID="$($CLI pending | sed -n 's/^  \[\([a-f0-9]*\)\].*/\1/p' | head -1)"
$CLI evaluate "$PSID" --status modified --note "境界条件を調整" >/dev/null
$CLI evaluate "$PSID" --status agreed >/dev/null   # --note 省略で再評価
NOTE="$(grep -h modifier_note "$COUNCIL_DATA_DIR"/invocations/*"$PSID".json | head -1)"
echo "$NOTE" | grep -q "境界条件を調整" || fail "再評価で modifier_note が消えた: $NOTE"
$CLI evaluate "$PSID" --status agreed --note "" >/dev/null   # 明示的に空へ
NOTE2="$(grep -h modifier_note "$COUNCIL_DATA_DIR"/invocations/*"$PSID".json | head -1)"
echo "$NOTE2" | grep -q '""' || fail "--note \"\" で note を空にできない: $NOTE2"
echo "  ok: note 省略=保持 / --note \"\"=明示クリア"

echo "== C2 を 10 件 agreed（rate 1.0）→ CTL-1 =="
# 上の判定（既に agreed 済み）に加えて 9 件で C2=10 件
for _ in $(seq 1 9); do record_agreed C2; done   # 合計 10 件 agreed
assert_ctl "CTL-1"

echo "== C1/C3/C4 も各 10 件 agreed・total≥30 → CTL-2 =="
for dc in C1 C3 C4; do
  for _ in $(seq 1 10); do record_agreed "$dc"; done
done
assert_ctl "CTL-2"

echo "== 各カテゴリ count≥25・rate≥0.95・total≥100 → CTL-3 =="
# 現状 C2=10, C1=C3=C4=10。各カテゴリを 25 件以上、全体 100 件以上へ。
for dc in C1 C2 C3 C4; do
  for _ in $(seq 1 16); do record_agreed "$dc"; done   # 各 +16 → 26 件
done
assert_ctl "CTL-3"

echo "== reject で rate 低下 → CTL-3 維持できず降格 =="
# C2 に reject を積んで rate を 0.95 未満へ落とすと CTL-3 条件（全カテゴリ rate≥0.95）が崩れる
for _ in $(seq 1 5); do record_agreed C2 rejected; done
got="$($CLI status | sed -n 's/^現在の CTL: //p' | head -1)"
[ "$got" != "CTL-3" ] || fail "reject 後も CTL-3 のまま（質条件が効いていない）"
echo "  ok: reject で CTL-3 から落ちた（現在 $got）"

echo "== regime-block が出力できる =="
$CLI regime-block | grep -q '^- ctl: ' || fail "regime-block に ctl 行がない"
echo "  ok: regime-block"

# ---- v6.12.0: agreed_with_synthesis（止揚）と modifier_note 必須化 ------------

echo "== agreed 以外は --note 必須 =="
SYN_DIR="$(mktemp -d)"
syn_record() {
  local out
  out="$(COUNCIL_DATA_DIR="$SYN_DIR" $CLI record --decision-category C2 \
    --topic t --judgment j --confidence 0.8)"
  echo "$out" | awk -F- '/^記録: council-/{print $NF}' | head -1
}
COUNCIL_DATA_DIR="$SYN_DIR" $CLI init >/dev/null
SID="$(syn_record)"
for st in agreed_with_synthesis modified rejected; do
  if COUNCIL_DATA_DIR="$SYN_DIR" $CLI evaluate "$SID" --status "$st" >/dev/null 2>&1; then
    fail "--note なしで $st が通ってしまった"
  fi
done
# 空白のみの note も拒否する（形だけ埋める抜け道を塞ぐ）
if COUNCIL_DATA_DIR="$SYN_DIR" $CLI evaluate "$SID" --status modified --note "   " >/dev/null 2>&1; then
  fail "空白のみの --note が通ってしまった"
fi
# agreed だけは --note 省略可
COUNCIL_DATA_DIR="$SYN_DIR" $CLI evaluate "$SID" --status agreed >/dev/null \
  || fail "agreed が --note なしで落ちた"
echo "  ok: agreed 以外は note 必須 / agreed は省略可"

echo "== agreed_with_synthesis は agreement_rate の分子に入る =="
# C2 を 10 件: agreed 5 + agreed_with_synthesis 5 → rate 1.0 で CTL-1 が成立するはず。
# 旧仕様（止揚を modified 扱い）なら rate 0.5 に落ち CTL-0 のままになる。
SYN2_DIR="$(mktemp -d)"
COUNCIL_DATA_DIR="$SYN2_DIR" $CLI init >/dev/null
for i in $(seq 1 10); do
  out="$(COUNCIL_DATA_DIR="$SYN2_DIR" $CLI record --decision-category C2 \
    --topic t --judgment j --confidence 0.8)"
  sid="$(echo "$out" | awk -F- '/^記録: council-/{print $NF}' | head -1)"
  if [ "$((i % 2))" -eq 0 ]; then
    COUNCIL_DATA_DIR="$SYN2_DIR" $CLI evaluate "$sid" --status agreed_with_synthesis \
      --note "骨格を採用し少数意見を併合" >/dev/null
  else
    COUNCIL_DATA_DIR="$SYN2_DIR" $CLI evaluate "$sid" --status agreed >/dev/null
  fi
done
GOT="$(COUNCIL_DATA_DIR="$SYN2_DIR" $CLI status | sed -n 's/^現在の CTL: //p' | head -1)"
[ "$GOT" = "CTL-1" ] || fail "止揚 5 件込みで rate 1.0 → CTL-1 のはず（実際 $GOT）"
COUNCIL_DATA_DIR="$SYN2_DIR" $CLI status | grep -q 'rate=1.0' \
  || fail "agreed_with_synthesis が分子に算入されていない"
echo "  ok: 止揚は同意側に算入（rate 1.0 / CTL-1）"

echo "== audit が note 欠落と件数乖離を検出する =="
# 既存記録の note を直接消して legacy 記録（v6.12.0 以前）を再現する
COUNCIL_DATA_DIR="$SYN2_DIR" $PY -c "
import json, os, pathlib
d = pathlib.Path(os.environ['COUNCIL_DATA_DIR']) / 'invocations'
p = sorted(d.glob('*.json'))[0]
rec = json.loads(p.read_text(encoding='utf-8'))
rec['actual_outcome']['status'] = 'modified'
rec['actual_outcome']['modifier_note'] = None
p.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
"
COUNCIL_DATA_DIR="$SYN2_DIR" $CLI audit | grep -q 'modifier_note 欠落' \
  || fail "audit が note 欠落を検出しなかった"
COUNCIL_DATA_DIR="$SYN2_DIR" $CLI audit | grep -q '是正対象 1 件' \
  || fail "audit の是正対象件数が 1 でない"
rm -rf "$SYN_DIR" "$SYN2_DIR"
echo "  ok: audit が legacy note 欠落を検出"

echo
echo "PASS: council-ctl 回帰テスト 全通過"
