# Issue Filter Spec

`crosscut-issue-implementer` の Issue 選別 3 段階フィルター詳細。

## 設計原則

ユーザー（philosophy 第 7 条 P2）の明示意図「Issue 選択は開発品質を決める」を機械化する。乱雑な Issue を全部 picking up しない、品質確保のための多段ガード。

## 一次フィルター: label opt-in

| 条件 | 判定 |
|---|---|
| Issue に label `ready-for-ai` あり | ✅ 二次フィルターへ |
| label なし | skip（workflow trigger 条件で既に弾かれる、本フィルター到達せず） |
| label `do-not-pickup` あり | ✅ 即 skip（最優先 block、人間 P4 の安全網） |

label `ready-for-ai` 付与は人間 P2 専管（philosophy 第 7 条）。AI は付与しない（dispatcher が draft 作成時のみ例外的に付与可、CTL ≥ 2 で）。

## 二次フィルター: author allowlist + 本文必須項目

### Author Allowlist

`.github/workflows/issue-pickup.yml` の env.ALLOWED_AUTHORS（space 区切り）と Issue 作成 author を照合。一致しない場合 skip + label `untrusted-author`。

### 本文必須項目

Issue 本文に以下のセクションが含まれているかチェック（heading or マーカー）：

```markdown
## 再現手順 (or Steps to reproduce)
- ...

## 期待動作 (or Expected behavior)
- ...

## 受入条件 (or Acceptance criteria)
- ...
```

**いずれか欠落** → skip + label `needs-clarification` + Issue コメントで欠落項目を通知。Issue は close せず、人間 P2 が補強して再 trigger 可。

## 三次フィルター: AI Triage（gemini-cli）

`triage-protocol.md` 参照。gemini-cli が Issue 内容を読み、以下を判定：

| 判定 | 結果 |
|---|---|
| pickup_yes | ✅ pickup 確定、Phase 4 へ |
| skip_out_of_scope | label `out-of-scope` 付与（DONT.md 抵触） |
| skip_focus_mismatch | label `focus-mismatch` 付与（current_focus と不一致） |
| skip_complexity | label `too-complex` 付与（L2 級スコープ、人間 L0 経由要請） |
| skip_other | label `needs-clarification` 付与（理由を Issue コメントで明示） |

skip 時も Issue は close しない。人間 P2 が再評価可能。

## label 命名規約

本 filter で自動付与する全 label：

- `ready-for-ai` (人間 P2 付与、AI が読む opt-in marker)
- `do-not-pickup` (人間 P4 緊急 block)
- `in-progress` (pickup 確定後 AI 付与、多重起動防止)
- `needs-clarification` (二次/三次 filter 不通過、人間差し戻し)
- `out-of-scope` (DONT.md 抵触、人間判断要請)
- `focus-mismatch` (current_focus 不一致、一時延期)
- `too-complex` (L2 級スコープ、人間 L0 起動要請)
- `untrusted-author` (allowlist 外、信頼境界)
- `circuit-broken` (Circuit Breaker 上限到達)
- `pickup-failed` (実装中の致命的エラー)

## 後方互換性

- 既存 Issue（label なし）には影響しない（trigger 条件で弾かれる）
- ALLOWED_AUTHORS 未設定の workflow では一次・二次フィルター skip + 三次のみ実行（warning 通知）
- current_focus 未設定の場合は AI triage が「全 type 受入」モードに自動 fallback
