# Drift Verify Protocol

`crosscut-verifier-drift` の CTL 別動作詳細。spec §3.2.6 を本体化。

## 検証構造

既存の 5 層エラー検出スタックに対する追加層。CTL に応じて追加層の発動が決まる。

### 既存層（v4.x までで完成）

| 層 | 対象 | 発動 |
|---|---|---|
| Shift Left 基盤 | 型 / lint / フォーマット | 常時 |
| 第1層 計算的センサー | 単体 / 統合テスト | 常時 |
| 第2層 E2E 機械検証 | Playwright 等 | priority ≥ standard |
| 第3層 Interaction Cost | UX 測定 | priority ≥ standard |
| 第4層 推論的センサー | 「仕様に合う・動く・使える」 | 常時 |
| 第5層 独立検証 | layer1-independent-reviewer | M2 以上で常時 |

### 追加層（v5.0.0 で新設）

| 層 | 対象 | 発動 CTL |
|---|---|---|
| **drift 検知** | SPEC/ADR との乖離（本 skill） | **CTL ≥ 1** |
| 思想検証 | 5 本柱整合（crosscut-verifier-philosophy） | CTL ≥ 2（v5.1.0 で実装） |

## CTL 別の drift 検証構成

| CTL | drift 検証実施 | 検出時の自動還流 |
|---|---|---|
| CTL-0 | × | — |
| CTL-1 | ○（軽量チェック） | drift → 設計層 Issue 自動生成（crosscut-feedback-loop 経由） |
| CTL-2 | ○（フルチェック） | 自動還流 + crosscut-council 事前検証 |
| CTL-3 | ○（フルチェック） | 完全自動（事後献上のみ） |

## drift 種別と判定

### 種別

| 種別 | 説明 | 重大度デフォルト |
|---|---|---|
| spec_unrecorded_addition | SPEC.md に記載のない機能追加 | medium |
| adr_unapproved_removal | ADR で承認されていない削除 | high |
| dont_violation | DONT.md 抵触の機能・コード | high |
| signature_drift | API/関数シグネチャの破壊的変更が SPEC に未反映 | high |
| ux_drift | UX 制約（クリック数・応答時間）の超過 | medium |

### 判定ロジック（軽量・フル共通）

1. PR 差分を取得
2. 種別ごとに pattern matching（軽量）/ ast 解析（フル）
3. 検出時：種別 + 該当ファイル/行 + 重大度を `delivery/DRIFT-REPORT.md` に出力
4. PR コメントに drift サマリ追記
5. CTL ≥ 1 なら `crosscut-feedback-loop` を起動して還流

### 軽量 vs フル

| 項目 | 軽量（CTL-1） | フル（CTL-2/3） |
|---|---|---|
| spec_unrecorded_addition | キーワード grep | 機能境界 ast 解析 |
| dont_violation | DONT.md 文字列 grep | 意味的類似度判定 |
| signature_drift | git diff のみ | TypeScript signature diff（型情報考慮） |
| ux_drift | sensors/interaction-cost ログ参照 | 同左 + 統計的有意性チェック |

## コンテキスト管理（spec §3.2.6 補足）

drift 検証は CI 上で実行されるため、コンテキスト消費を最小化する：

- skill 単位の選択実行（必要な crosscut-verifier-* のみロード）
- references の遅延ロード
- CTL 判定を早期実行（CTL-0 なら即終了）

## CHANGELOG 記録

drift 検出時に `history/CHANGELOG.md` にレベル A 追記：

```markdown
### Drift 検出（PR #123）
- 種別: spec_unrecorded_addition (medium)
- 該当: src/handlers/auth.ts:45 (新機能 oauth_v2)
- 還流: crosscut-feedback-loop 経由で SPEC 追記 Issue #126 生成
```
