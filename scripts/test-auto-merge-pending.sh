#!/usr/bin/env bash
# auto-merge.yml 条件 3.5「全 CI 完了待ち」の PENDING カウント jq の回帰テスト（v5.22.0）。
#
# auto-merge.yml の evaluate step が使う jq 式と同一のものを assert する。
# 仕様変更時はこのテストも更新する（OC review #131 L10: ad-hoc 検証の再現可能化）。
#
# 使い方: bash scripts/test-auto-merge-pending.sh
set -euo pipefail

# auto-merge.yml 条件 3.5 と同一の PENDING カウント式（コピーを同期させること）
pending_count() {
  jq -r '
    [ .statusCheckRollup[]?
      | select((.name // .context) != "evaluate")
      | select(
          (.__typename == "CheckRun"      and .status != "COMPLETED") or
          (.__typename == "StatusContext"  and .state  == "PENDING")
        )
    ] | length'
}

fail=0
assert() {
  local desc="$1" expected="$2" json="$3"
  local got; got=$(echo "$json" | pending_count)
  if [ "$got" = "$expected" ]; then
    echo "ok   - $desc (pending=$got)"
  else
    echo "FAIL - $desc : expected=$expected got=$got"
    fail=1
  fi
}

# 全 check 完了（copilot 含む）+ 自己 evaluate は IN_PROGRESS → 0（proceed）
assert "all complete + self evaluate excluded" 0 \
  '{"statusCheckRollup":[{"__typename":"CheckRun","name":"review","status":"COMPLETED"},{"__typename":"CheckRun","name":"verify","status":"COMPLETED"},{"__typename":"CheckRun","name":"copilot-pull-request-reviewer","status":"COMPLETED"},{"__typename":"CheckRun","name":"evaluate","status":"IN_PROGRESS"}]}'

# copilot review だけ pending → 1（待機）= ユーザー要請の核
assert "copilot still pending -> wait" 1 \
  '{"statusCheckRollup":[{"__typename":"CheckRun","name":"review","status":"COMPLETED"},{"__typename":"CheckRun","name":"copilot-pull-request-reviewer","status":"IN_PROGRESS"},{"__typename":"CheckRun","name":"evaluate","status":"IN_PROGRESS"}]}'

# copilot 無し・review 完了 → 0（proceed）= 「無い場合も反応する」
assert "no copilot, review done -> proceed" 0 \
  '{"statusCheckRollup":[{"__typename":"CheckRun","name":"review","status":"COMPLETED"},{"__typename":"CheckRun","name":"evaluate","status":"IN_PROGRESS"}]}'

# 自己 evaluate のみ（他不在）→ 0（proceed、後段 4.5 が zero-check skip）= self-deadlock 回避
assert "only self evaluate -> no deadlock" 0 \
  '{"statusCheckRollup":[{"__typename":"CheckRun","name":"evaluate","status":"IN_PROGRESS"}]}'

# StatusContext(legacy) pending 混在 → 1（待機）
assert "StatusContext PENDING counted" 1 \
  '{"statusCheckRollup":[{"__typename":"CheckRun","name":"review","status":"COMPLETED"},{"__typename":"StatusContext","context":"ci/ext","state":"PENDING"}]}'

# 未知 status は安全側（待つ）= negative 形の保守性（L2）
assert "unknown CheckRun status -> wait (conservative)" 1 \
  '{"statusCheckRollup":[{"__typename":"CheckRun","name":"verify","status":"WAITING"},{"__typename":"CheckRun","name":"evaluate","status":"IN_PROGRESS"}]}'

if [ "$fail" -eq 0 ]; then echo "ALL PASS"; else echo "SOME FAILED"; exit 1; fi
