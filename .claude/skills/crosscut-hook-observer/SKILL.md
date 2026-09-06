---
name: crosscut-hook-observer
target_os: any
dimension: D4
origin: ECC-derived
origin_source: "ecc:hooks/hooks.json#PreToolUse,PostToolUse,Stop,SessionStart,SessionEnd,PreCompact"
origin_version: "ECC v2.0.0-rc.1"
chewing_translation: "T1+T3 (構造保持 + サブセット選別)"
chewing_pr: "samejima-ai/dialog-harness#76"
chewed_at: "2026-05-11T05:30:00Z"
description: >
  Claude Code 公式 hooks（.claude/settings.json の hooks キー）経由でセッションの tool call と
  session lifecycle を観測し、harness-verifier に観測ログを引き渡す bridge skill。
  PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd / PreCompact の 6 event を購読、
  exit code は常に 0 で warn のみ、block しない（philosophy.md 第 6 条「人間最終承認」準拠）。
  PreCompact は Wave 3 諮問 (council-2026-05-11T09:00:00Z-w3qb02) で追加採用。
  UserPromptSubmit / Notification / SubagentStop は Wave 4 申し送り。
  「hook 観測機構を有効化」「PreToolUse 観測ログを取得」「Claude Code hook で session
  lifecycle を観測」「harness-verifier に観測ログを渡す bridge」等の発話、または
  settings.json hooks bootstrap からの自動起動で発動。
  本 skill は **観測専用** であり、tool call を block / 改変しない（命令層と観測層の分離）。
  harness-verifier への入力提供のみが責務（DH 独立性原則に従い一方向依存: skill → 出力 →
  harness-verifier 読み取り）。
---

# crosscut-hook-observer — Claude Code hook 観測機構

ECC `hooks/hooks.json` の event-types / matcher 構文 / Node.js bootstrap 設計から
**6 event + Python bootstrap + warn-only exit**（Wave 1 で 5 event、Wave 3 で PreCompact 追加）をサブセット選別 + 翻訳して導入した。

## 配線修理の来歴（2026-08-28・Council 諮問済み）

**v5.x〜v6.15 の 3.5 ヶ月間、本 skill の観測は一度も発火していなかった**（実観測 0 件・smoke 2 行のみ）。
死因は登録先の誤り: 設定を `.claude/hooks.json` に置いていたが、**Claude Code が hooks を読むのは
settings 系ファイルのみ**（`hooks/hooks.json` は plugin 同梱専用。公式 docs 全文精査で確定）。
ECC 由来の咀嚼（T1+T3、council w1qb01/w3qb02）はイベント選別・warn-only 設計を正しく持ち込んだが、
**読み込み経路の検証を欠いた** — 咀嚼の記録があっても配線の実証がなければ動かない、の実例である。

修理（Council 案 B・reason_divergence 収束）:
- 登録を `.claude/settings.json`（厳密スキーマ準拠・非スキーマキー禁止 — 検証失敗はファイル内
  全 hook を無言で無効化する）へ移設。コマンドは `python3 ||  python` fallback（Windows 対応）
- **フィールド許可リスト化**: 旧 observe.py は payload 全量を 512 字 truncate で記録しており、
  配線が生きると応答本文・tool 入出力が追跡ファイルへ流れる設計だった。以後は内容フリーの
  計量メタデータのみ（`observe.py ALLOWED_FIELDS` が単一情報源）
- **生観測のローカル化**: `hook-observations.jsonl` は untrack + .gitignore（生 L0 はローカル蓄積、
  リポジトリには蒸留物のみ — 情報代謝・公開安全と整合。checker はログ不在でも PASS 仕様で CI 非破壊）

**申し送り**（本修理のスコープ外・次 PR の種）:
1. **生存信号（heartbeat）**: 「空に PASS」の構造は残っている。観測の最終 ts・event 別件数の
   蒸留ダイジェストを儀式経由でリポジトリへ置く（哲学者第 3 の道。毎イベント追跡は dirty 化するため不採用）
2. **許可リストの見直し契機**: 新 tool・新フィールド追加時の ALLOWED_FIELDS 再審（規範メタデータの
   review_trigger 相当を observe.py コメントに付す）
3. **自己購読の遮断**: ローカル生ログを将来のセッションが context として読む経路は開かない
   （購読量上限の思想。読むのは蒸留プロセスのみ）
4. 性能: PreToolUse/PostToolUse は python 二重起動が毎 tool call 走る。実測で痛ければ
   settings.json の 2 エントリ削除で 4 event へ縮退可能（可逆）
DH 独自の hook 観測機構。

## 設計原則

### 1. 観測専用（命令層と観測層の分離）

本 skill は tool call の事前検出（PreToolUse）と事後ログ（PostToolUse）、
session lifecycle 通知（Stop / SessionStart / SessionEnd）、context 圧縮前イベント（PreCompact）を **観測** するのみ。

- **exit code は常に 0**: block は行わない
- **tool call の改変なし**: hook output は stdout に書かれず、observation-log にのみ追記
- **DH philosophy 第 6 条「人間最終承認」準拠**: 自動 block は人間判断の代替にならない

### 2. ECC との咀嚼差分

| 要素 | ECC | DH（咀嚼後） |
|---|---|---|
| event types | 6（5 + PreCompact） | **6**（Wave 3 諮問 w3qb02 で PreCompact 追加採用、Council w1qb01 の初期 5 件から +1） |
| exit code | 2=block / 0=warn 両方使用 | **0 のみ**（warn 専用） |
| bootstrap | Node.js (`scripts/hooks/plugin-hook-bootstrap.js`) | **Python** (`scripts/bootstrap.py`) |
| matcher 構文 | `Bash` / `Write` / `*` / `Bash\|Write\|Edit` 等 | **同構文採用**（T1 構造保持） |
| 観測ログ出力先 | continuous-learning v2 等の skill 別フィードバック層 | **harness-verifier**（一方向依存） |

### 3. harness-verifier との関係（独立性原則準拠）

```
Claude Code セッション
    ↓ hook 発火
.claude/settings.json hooks キー (event → command)
    ↓ subprocess
crosscut-hook-observer/scripts/bootstrap.py
    ↓ event-type 分岐
crosscut-hook-observer/scripts/observe.py
    ↓ append-only
harness-verifier/reports/hook-observations.jsonl
    ↑ 読み取りのみ
harness-verifier/checks/hook_observations.py（検査項目 6「hook 観測一貫性」、Wave 2 で実装）
    ↑
harness-verifier/verify.py（独立検証層、DH 本体に依存しない）
```

**Wave 2 で消費側を本実装** (`harness-verifier/checks/hook_observations.py`): JSONL parse error / 必須フィールド欠落 / 不正 event 値を検出。観測ログ不在は PASS（fail-open）。

**矢印方向の重要性**:
- skill → harness-verifier reports は「観測ログを書く」だけの一方向（Wave 1）
- harness-verifier → 観測ログ は「読み取りのみ」の一方向（Wave 2、独立性原則準拠）
- bootstrap.py が落ちても harness-verifier の動作は影響を受けない（fail-open）
- harness-verifier が観測ログ消費に失敗しても skill 動作は影響を受けない（独立性双方向）

## 起動経路

### 自動起動（hook 経路）

`.claude/settings.json` の hooks キー経由で Claude Code が直接起動。
本 skill は **subprocess として起動される**ため、SKILL.md 自体は documentation の役割を担う。

### 明示起動

「hook 観測機構を有効化」「観測ログを確認」等の発話で発動し、以下を実施:

1. `.claude/settings.json` hooks の状態確認（6 event 全て登録済か: PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd / PreCompact）
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
- v0.2.0（Wave 3 PR #81）— PreCompact event 追加で 6 event 観測 (council-w3qb02 B 採決)
- Wave 2 予定: continuous-learning v2.1 観測機構との連携（候補 5 取り込み）
- v5.13.0 候補: PreCompact event の採否再諮問（DH の `/compact` 連携 SPEC 確定後）
