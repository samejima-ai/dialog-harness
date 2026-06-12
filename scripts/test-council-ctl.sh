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
CLI="python3 $HERE/council-ctl.py"
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
  sid="$(echo "$out" | sed -n 's/^記録: council-.*-//p' | head -1)"
  $CLI evaluate "$sid" --status "$status" >/dev/null
}

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

echo "== C2 を 10 件 agreed（rate 1.0）→ CTL-1 =="
# 上の未評価 1 件をまず評価して片付ける
$CLI evaluate "$($CLI pending | sed -n 's/^  \[\([a-f0-9]*\)\].*/\1/p' | head -1)" --status agreed >/dev/null
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

echo
echo "PASS: council-ctl 回帰テスト 全通過"
