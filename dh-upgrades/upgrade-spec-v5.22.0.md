# Upgrade Spec v5.22.0 — auto-merge 全 CI 完了待ち化 + self-update protocol 強化

**リリース予定**: 2026-06-07
**バージョン昇格**: minor（v5.21.0 → v5.22.0、後方互換維持）
**起点**: ユーザー要請「auto-merge を見直して、各 CI 処理（copilot review 含む／copilot review なしの場合も反応）が終わってから auto-merge が動くように」+ PR #130 レビュー LOW 反映
**境界**: `.github/workflows/auto-merge.yml` 変更 = opt-in 領域（`human-review-needed` 必須・人間レビュー後 merge）

---

## §1 概要

2 議題を 1 PR にバンドル（AD-021 のバンドル許可に整合）。

### (1) auto-merge.yml: 全 CI 完了待ち化

**起点問題**: Issue #125 修正（PR #129）後も、auto-merge の条件 3.5 ポーリングは `verify` / `review` の完了だけを待っていた。そのため `copilot-pull-request-reviewer` 等の CI が**まだ走っている最中でも merge が成立**しうる（PR #130 が copilot review 完了前に auto-merge された）。

**解決**: 条件 3.5 を「**自分（evaluate）以外の全 check が COMPLETED になるまで待機**」へ一般化。

- `verify` / `review` に加え `copilot-pull-request-reviewer` / `gemini-review` / その他すべての CI 完了を待つ。
- **copilot review 等が走らない PR でも正常動作**: 不在 check は `statusCheckRollup` に現れない＝pending 集合に入らないため、待機対象が減るだけ（「無い場合も反応する」）。
- **自己（"evaluate"）は必ず除外**: 実行中の evaluate 自身が IN_PROGRESS で rollup に居るため、除外しないと self-deadlock になる。
- `StatusContext`（legacy commit status）の `state == PENDING` も待機対象に含める。
- `timeout-minutes` 10→15、`POLL_MAX_WAIT` 300→600s（copilot review 等を吸収）。

### (2) self-update protocol 強化（v5.21.0 のレビュー LOW 反映）

PR #130 の OC / Copilot レビュー LOW（advisory）を反映:

- `UPDATE.md`: 一時 clone を `mktemp -d` 化（固定 `/tmp/dh` の衝突回避）/ pre-update snapshot を「変更なしはスキップ・commit 失敗は中断」の安全形へ（`|| true` の握りつぶしを解消し破壊的 `rm -rf` の復旧点を保証）/ `diff` の両分岐を明示 / REGIME.md 記録例の見出しレベルを `###` + 任意注記。
- `dh-manifest.yml`: `dh_version` を削除し `VERSION` を単一情報源化（drift 排除）/ `min_same_major_from` に「semver major 部のみで比較」を明記。

---

## §2 後方互換性

- auto-merge は **待機範囲の拡大のみ**で merge gate（条件 4/5/4.5/6）のロジックは不変。挙動は「より慎重に待つ」方向で、誤 merge を増やさない。
- doc / manifest は追記・明確化・重複排除のみ。既存挙動への副作用なし。

---

## §3 検証

- auto-merge.yml: YAML parse / `bash -n` / PENDING カウント jq を 5 ケースで単体検証
  （全完了 / copilot pending / copilot 無し / 自己 evaluate のみ / StatusContext 混在）。
- 実地検証: 本機構は次回以降の PR で copilot review 完了まで待機することを観測する（merge ログの notice で確認可能）。

---

## §4 申し送り（v5.22.x / v5.23.0 以降）

| 項目 | 理由 |
|---|---|
| `crosscut-dh-self-update` skill | 「DH を更新して」起動の更新自動化（v5.21.0 §申し送り 継続）|
| リリースタグ運用 / `migrations.yml` | ピン留め容易化・メジャー跨ぎ移行索引 |
| harness-verifier の `never_touch` ガード / VERSION↔manifest 整合 CI | 構造検査の追加 |
| copilot review の conclusion を merge gate に含めるか | 現状は「完了待ち」のみ（advisory）。FAILURE を block 対象にするかは別途判断 |
| **job 名衝突の解消（Copilot review #131）** | `claude-review.yml` / `gemini-review.yml` が両方 job 名 `review`。auto-merge 条件 5/4.5 の `select(.name == "review")` が gemini ではなく claude を拾いうる（本 repo は gemini-review 未発火でドーマント）。job 名一意化（gemini→`gemini-review` 等）+ selector 更新を別 PR で。Issue 化済み |

---

## §5 関連

- `.github/workflows/auto-merge.yml` 条件 3.5 — 全 CI 完了待ちポーリング
- Issue #125 / PR #129 — race 修正（本変更の前段）
- `dh-upgrades/upgrade-spec-v5.21.0.md` — self-update protocol 最小構成（本強化の対象）
- `UPDATE.md` / `dh-manifest.yml` / `VERSION` — self-update 成果物
