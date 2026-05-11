---
name: crosscut-hook-observer
dimension: D4
origin: ECC-derived
origin_source: "ecc:hooks/hooks.json#PreToolUse,PostToolUse,Stop,SessionStart,SessionEnd"
origin_version: "ECC v2.0.0-rc.1"
chewing_translation: "T1+T3 (構造保持 + サブセット選別)"
chewing_pr: "samejima-ai/dialog-harness#76"
chewed_at: "2026-05-11T05:30:00Z"
description: >
  Claude Code 公式 hooks.json schema 経由で Claude Code セッションの tool call と
  session lifecycle を観測し、harness-verifier に観測ログを引き渡す bridge skill。
  PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd の 5 event を購読、
  exit code は常に 0 で warn のみ、block しない（philosophy.md 第 6 条「人間最終承認」準拠）。
  Council 諮問 (council-2026-05-11T05:00:00Z-w1qb01) により PreCompact は除外、
  v5.13.0 候補で温存。
  「hook 観測機構を有効化」「PreToolUse 観測ログを取得」「Claude Code hook で session
  lifecycle を観測」「harness-verifier に観測ログを渡す bridge」等の発話、または
  hooks.json bootstrap からの自動起動で発動。
  本 skill は **観測専用** であり、tool call を block / 改変しない（命令層と観測層の分離）。
  harness-verifier への入力提供のみが責務（DH 独立性原則に従い一方向依存: skill → 出力 →
  harness-verifier 読み取り）。
---

# crosscut-hook-observer — Claude Code hook 観測機構

ECC `hooks/hooks.json` の event-types / matcher 構文 / Node.js bootstrap 設計から
**5 event + Python bootstrap + warn-only exit** をサブセット選別 + 翻訳して導入した
DH 独自の hook 観測機構。

## 設計原則

### 1. 観測専用（命令層と観測層の分離）

本 skill は tool call の事前検出（PreToolUse）と事後ログ（PostToolUse）、
session lifecycle 通知（Stop / SessionStart / SessionEnd）を **観測** するのみ。

- **exit code は常に 0**: block は行わない
- **tool call の改変なし**: hook output は stdout に書かれず、observation-log にのみ追記
- **DH philosophy 第 6 条「人間最終承認」準拠**: 自動 block は人間判断の代替にならない

### 2. ECC との咀嚼差分

| 要素 | ECC | DH（咀嚼後） |
|---|---|---|
| event types | 6（5 + PreCompact） | **5**（PreCompact 除外、Council w1qb01 採決） |
| exit code | 2=block / 0=warn 両方使用 | **0 のみ**（warn 専用） |
| bootstrap | Node.js (`scripts/hooks/plugin-hook-bootstrap.js`) | **Python** (`scripts/bootstrap.py`) |
| matcher 構文 | `Bash` / `Write` / `*` / `Bash\|Write\|Edit` 等 | **同構文採用**（T1 構造保持） |
| 観測ログ出力先 | continuous-learning v2 等の skill 別フィードバック層 | **harness-verifier**（一方向依存） |

### 3. harness-verifier との関係（独立性原則準拠）

```
Claude Code セッション
    ↓ hook 発火
.claude/hooks.json (event → command)
    ↓ subprocess
crosscut-hook-observer/scripts/bootstrap.py
    ↓ event-type 分岐
crosscut-hook-observer/scripts/observe.py
    ↓ append-only
harness-verifier/reports/hook-observations.jsonl

    [Wave 2 以降の予定]
        ↑ 読み取りのみ
    harness-verifier/verify.py の hook-observations 消費機構（独立検証層、DH 本体に依存しない）
```

**Wave 1 のスコープ**: 観測ログ JSONL の生成までを実装する（skill → ログ書き込み）。harness-verifier 側の読み取り・解析実装は Wave 2 候補（候補 5 continuous-learning と同時に着手）。Wave 1 段階では JSONL は将来の消費者に向けた素材として蓄積される。

**矢印方向の重要性**:
- skill → harness-verifier reports は「観測ログを書く」だけの一方向（Wave 1 で実装済）
- harness-verifier 側からの読み取り経路は Wave 2 で実装予定、その際も skill 内部には依存しない（独立性原則）
- bootstrap.py が落ちても harness-verifier の動作は影響を受けない（fail-open）

## 起動経路

### 自動起動（hook 経路）

`.claude/hooks.json` 経由で Claude Code が直接起動。
本 skill は **subprocess として起動される**ため、SKILL.md 自体は documentation の役割を担う。

### 明示起動

「hook 観測機構を有効化」「観測ログを確認」等の発話で発動し、以下を実施:

1. `.claude/hooks.json` の状態確認（5 event 全て登録済か）
2. `harness-verifier/reports/hook-observations.jsonl` の末尾 N 件を表示
3. 観測機構が動作していない場合の診断（permission / Python path / 書き込み権限）

## 観測ログ形式

`harness-verifier/reports/hook-observations.jsonl` に JSONL 形式で append-only:

```jsonl
{"ts": "2026-05-11T05:30:00Z", "event": "PreToolUse", "tool": "Bash", "session_id": "abc123", "fields": {"command": "<truncated>"}}
{"ts": "2026-05-11T05:30:01Z", "event": "PostToolUse", "tool": "Bash", "session_id": "abc123", "fields": {"exit_code": 0}}
```

詳細は [references/output-format.md](references/output-format.md)

## 関連 skill

- `harness-verifier/` — 観測ログの消費側、読み取り専用
- `crosscut-feedback-loop` — 観測ログから検出された抵触を還流する下流機構（候補 5
  continuous-learning との接続点、Wave 2 で本実装）

## バージョン

- v0.1.0（Wave 1 walking skeleton）— 5 event 観測 + Python bootstrap + 一方向依存
- Wave 2 予定: continuous-learning v2.1 観測機構との連携（候補 5 取り込み）
- v5.13.0 候補: PreCompact event の採否再諮問（DH の `/compact` 連携 SPEC 確定後）
