---
name: crosscut-verifier-philosophy
dimension: D4
description: >
  **v5.0.0 では発動禁止 / DO NOT TRIGGER in v5.0.0**。
  本 skill は仕様3-哲学（5 本柱整合検証）の placeholder で、判定ロジックは v5.1.0 minor 改修で本実装される。
  v5.0.0 環境でこの skill が選択された場合、即座に「未実装エラー」を返して人間に献上する以外の動作はしない。
  v5.0.0 では誤発動防止のため、いかなる発話でもこの skill を選択してはならない。
  v5.1.0 以降では CTL ≥ 2 で発動し、PR 内容を philosophy.md（6条憲法）と照合する。
  v5.1.0 以降の想定トリガー語句（v5.0.0 では非トリガー）:「思想検証」「5 本柱整合チェック」「philosophy 違反検出」等。
---

# Philosophy Verifier (Placeholder)

## v5.0.0 ステータス

- skill 配置のみ
- 判定ロジック未実装
- 発動された場合は「未実装」レポートを返し、`crosscut-feedback-loop` を経由せず人間に献上

## v5.1.0 で実装予定の仕様

### 発動条件
- PR 作成時の CI 実行
- REGIME.md の CTL ≥ 2

### 処理フロー（予定）
1. PR 内容を `philosophy.md` の 6条憲法と照合
   - フラクタル原則（P1）違反: L3 運用層を新設していないか
   - Shift Left 原則（P2）違反: エラー発生防止の前倒しを怠っていないか
   - 情報純度原則（P3）違反: skill 責務の分離が崩れていないか
   - 人間責務（P4）違反: 履歴層への記録が漏れていないか
   - 献上哲学（P5）違反: 自走中に人間に質問していないか
   - 人間 ≒ Council 第6条違反: CTL 委譲範囲外で自律実行していないか
2. 違反検出時の `crosscut-council` 発動
3. judgment_confidence < 0.5 の場合は人間エスカレーション

### CTL 別動作（予定）

| CTL | 動作 |
|---|---|
| CTL-0/1 | 発動しない（drift のみ） |
| CTL-2 | 軽量チェック（明白な違反のみ）、Council 経由で還流 |
| CTL-3 | フルチェック（パターン照合 + Council フル発動） |

詳細は v5.1.0 で `references/philosophy-verify-protocol.md` として配置予定。

## 関連

- `layer0-spec-architect/references/philosophy.md` — 6条憲法（判定原典）
- `crosscut-council/SKILL.md` — 違反検出時の判定機構
- `crosscut-feedback-loop/SKILL.md` — 還流先（v5.1.0 で接続）
