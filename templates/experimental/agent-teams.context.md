# Agent Teams — 議論型協調層の実装固有情報（時限付き随時層）

```yaml
lifecycle:
  norm_type: 効率型            # 純化 RL 型階層（claude-md-purity v0.3.0 §10）
  status: experimental          # Research Preview（破壊的変更あり）
  review_by: 2026-11-30         # 再評価条件: Agent Teams の GA 化 or この日付のいずれか早い方
  on_expiry: warn               # 期限超過を検出したローダーは WARN を出し L0 振り返り儀式へ回付する（形骸化防止 teeth・upgrade-spec v6.11.0 C-4）
  owner: dh-upgrades/upgrade-spec-v6.11.0.md F6
```

> **本ファイルは DH 規範ではない**。規範（`.claude/skills/**`）が定義するのは抽象契約
> 「独立コンテキストの複数エージェントが、直接メッセージ可能・人間割込可能・ローカル観測可能な協調層」
> のみであり（F6-1/F6-3）、実装固有の env 変数・バージョン・設定手順は全て本ファイルに隔離する。
> Research Preview の破壊的変更は本ファイルの更新だけで吸収し、規範を汚さない。
>
> **読む前に lifecycle.review_by を確認せよ**。期限超過なら記載内容は陳腐化している前提で扱い、
> WARN を残して L0 振り返り儀式で再評価する（GA 化していれば規範への昇格を、廃止されていれば本ファイルの削除を諮る）。

## 有効化（2026-08 時点の観測）

- Claude Code v2.1.32 以降の実験的機能。`settings.json` の env に `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- チーム設定: `~/.claude/teams/{team-name}/config.json` / 共有タスクリスト・Mailbox: `~/.claude/tasks/{team-name}/`（全てローカルファイル。cat/grep/jq で観測可能）
- リード = タスク分解・委託・統合専任（Delegate Mode: Shift+Tab）。チームメイトは独立インスタンスで相互に直接メッセージ可
- 人間の割込: Shift+Up/Down でチームメイト選択 → 直接指示

## 既知の制約（2026-08 時点）

- Research Preview: 破壊的変更・突然の仕様変更がありうる
- セッション再開（resume）非対応
- トークン消費はチームメイト数に比例。Pro プランではレート制限に頻発 — Max プラン前提
- teammate 上限 ≤ 3（DH 側規律、F7-2。超過は ADR 必須）

## degrade 経路（C-2・必須）

レート制限・機能変更・env 未設定で協調層が使用不能な場合、**subagent 直列にフォールバックして完遂する**。
機能（相互メッセージ・人間割込）は失われるが、作業は停止しない。degrade 発生は成果物に 1 行記録する。
