#!/usr/bin/env bash
# auto-merge.yml の stop ラベル停止機構の回帰テスト（v7・Council amrace）。
#
# 対象は 2 箇所の新設ガード:
#   (1) ポーリングループ内の毎反復 stop ラベル検査
#   (2) gh pr merge 直前の最終再判定（fail-closed）
#
# 背景（PR #196 の実測、2026-08-26）: 条件 1 はループ **前** に 1 回だけ評価され、
# その後 25 分待つあいだに付いたラベルが無視されて squash merge された。
# 本テストは「後付けラベルが検出されること」を回帰として固定する。
#
# auto-merge.yml と同一の jq 式を assert する。仕様変更時は両方を同期させること
# （test-auto-merge-pending.sh と同じ規律）。
#
# 使い方: bash scripts/test-auto-merge-stop-label.sh
set -euo pipefail

WF=".github/workflows/auto-merge.yml"

# auto-merge.yml の stop ラベル抽出式（コピーを同期させること）
stop_label() {
  jq -r '[.labels[]? | select(.name == "do-not-merge" or .name == "human-review-needed" or .name == "pickup-failed")] | .[0].name // ""'
}

fail=0
assert() {
  local desc="$1" expected="$2" json="$3"
  local got; got=$(echo "$json" | stop_label)
  if [ "$got" = "$expected" ]; then
    echo "ok   - $desc (stop='${got:-なし}')"
  else
    echo "FAIL - $desc : expected='$expected' got='$got'"
    fail=1
  fi
}

echo "== stop ラベル抽出 =="
assert "ラベルなし → 進行" "" '{"labels":[]}'
assert "labels キー自体が無い → 進行" "" '{}'
assert "human-review-needed → 停止" "human-review-needed" '{"labels":[{"name":"human-review-needed"}]}'
assert "do-not-merge → 停止" "do-not-merge" '{"labels":[{"name":"do-not-merge"}]}'
assert "pickup-failed → 停止" "pickup-failed" '{"labels":[{"name":"pickup-failed"}]}'
assert "無関係ラベルのみ → 進行" "" '{"labels":[{"name":"enhancement"},{"name":"documentation"}]}'
assert "無関係 + stop 混在 → 停止" "human-review-needed" '{"labels":[{"name":"enhancement"},{"name":"human-review-needed"}]}'
assert "前方一致の別名は拾わない" "" '{"labels":[{"name":"human-review-needed-later"}]}'

echo
echo "== workflow 側の配線（欠けたら PR #196 が再演する） =="
check_wf() {
  local desc="$1" pattern="$2"
  if grep -q "$pattern" "$WF"; then echo "ok   - $desc"; else echo "FAIL - $desc"; fail=1; fi
}
check_wf "ループ内に毎反復の stop ラベル検査がある" 'LOOP_STOP='
check_wf "ループ内検査が exit する" '待機中 stop ラベル'
check_wf "merge 直前に PR を再取得する" 'FINAL_JSON=\$(gh pr view'
check_wf "再取得の失敗が fail-closed になる" 'fail-closed'
check_wf "最終 stop ラベル判定がある" 'FINAL_STOP='
check_wf "最終 draft 判定がある" 'FINAL_JSON" | jq -r .\?.isDraft'
check_wf "最終 author 判定がある" 'FINAL_AUTHOR='
check_wf "最終 reviewDecision 判定がある" 'FINAL_RD='
check_wf "merge が最終取得の TITLE を使う" 'TITLE=\$(echo "\$FINAL_JSON"'

# 最終判定が gh pr merge より前にあること（順序が逆なら意味がない）
final_line=$(grep -n 'FINAL_STOP=' "$WF" | head -1 | cut -d: -f1)
merge_line=$(grep -n 'gh pr merge' "$WF" | tail -1 | cut -d: -f1)
if [ -n "$final_line" ] && [ -n "$merge_line" ] && [ "$final_line" -lt "$merge_line" ]; then
  echo "ok   - 最終判定が gh pr merge より前にある (L$final_line < L$merge_line)"
else
  echo "FAIL - 最終判定の位置が不正 (final=$final_line merge=$merge_line)"; fail=1
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "FAIL: auto-merge stop ラベル検査に失敗あり"
  exit 1
fi
echo "PASS: auto-merge stop ラベル 全テスト通過"
