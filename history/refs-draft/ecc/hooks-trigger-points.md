# ECC hooks/ トリガポイント参照カタログ（draft）

**観察対象**: `affaan-m/everything-claude-code` @ v2.0.0-rc.1 — `hooks/hooks.json` + `hooks/README.md`
**観察日**: 2026-05-11 JST
**再観察予約**: 2026-11-11
**Claude Code 公式 hook schema 準拠**: `https://json.schemastore.org/claude-code-settings.json`

---

## 1. ECC hooks の全体像

ECC は Claude Code の公式 hook 機構を最大限活用している。`hooks.json` は plugin marketplace 配布形式（`CLAUDE_PLUGIN_ROOT` 解決 → Node.js bootstrap → 個別 hook script）。

### イベントタイプ

| Event | 説明 | 制御権 |
|---|---|---|
| **PreToolUse** | ツール実行前 | block (exit 2) / warn (stderr) |
| **PostToolUse** | ツール完了後 | analyze only（block 不可） |
| **Stop** | Claude 応答完了後 | session-level 処理 |
| **SessionStart** | セッション開始時 | 初期コンテキスト読込 |
| **SessionEnd** | セッション終了時 | クリーンアップ |
| **PreCompact** | コンテキスト圧縮前 | state 保存 |

---

## 2. PreToolUse hook（一次観察、9 件）

| Hook ID | Matcher | 用途 | Exit 規約 |
|---|---|---|---|
| `pre:bash:dispatcher` | `Bash` | 品質 + tmux + push + GateGuard 統合 dispatcher | `2` block / `0` warn |
| `pre:write:doc-file-warning` | `Write` | 非標準 `.md`/`.txt` 警告（README/CLAUDE/CHANGELOG/LICENSE/SKILL/docs/skills/ は許可） | `0` warn |
| `pre:edit-write:suggest-compact` | `Edit\|Write` | 50 tool call 毎に `/compact` 提案 | `0` warn |
| `pre:observe:continuous-learning` | `*` | continuous-learning v2 用 PreToolUse 観測（async） | `0` |
| `pre:governance-capture` | `Bash\|Write\|Edit\|MultiEdit` | 秘密漏洩・policy 違反検出（`ECC_GOVERNANCE_CAPTURE=1` で有効化） | `0` |
| Dev server blocker | `Bash` | `npm run dev` 等を tmux 外で実行ブロック | `2` block |
| Tmux reminder | `Bash` | 長時間コマンドへの tmux 推奨 | `0` warn |
| Git push reminder | `Bash` | `git push` 前のレビュー促し | `0` warn |
| Pre-commit quality check | `Bash` | lint / commit message 形式 / console.log / debugger / secrets 検出 | `2` critical / `0` warn |

---

## 3. PostToolUse / Stop / Session hooks（一次観察、抜粋）

| Event | Hook | 機能 |
|---|---|---|
| **PostToolUse** | PR logger | `gh pr create` 後に PR URL + review コマンドを記録 |
| **PostToolUse** | Quality gate async | 標準準拠の非同期検証 |
| **PostToolUse** | Design check | デザイン規約照合 |
| **Stop** | Batch format / typecheck | JS/TS 改修を一括処理 |
| **Stop** | Session persist | セッション状態保存（async） |
| **Stop** | Cost tracking | API コスト集計（async） |
| **Stop** | Desktop notify | macOS/WSL 通知 |
| **SessionStart** | Load prior context | 前回コンテキスト復元 |
| **SessionStart** | Detect package manager | npm/yarn/pnpm 自動判定 |
| **SessionEnd** | Session marker | 非ブロッキング終了記録 |

---

## 4. DH との対応関係

| ECC hook | DH 対応機構 | 対応度 |
|---|---|---|
| PreToolUse `pre:bash:dispatcher`（品質ゲート） | `harness-verifier/verify.py`（D4 内部整合性検査） | 低（DH は Python 単体、ECC は Claude Code hook） |
| PreToolUse `pre:governance-capture`（秘密漏洩検出） | `harness-verifier` の一部 + AgentShield 相当不在 | 低 |
| PreToolUse `pre:observe:continuous-learning` | DH 未実装（feedback-loop は post-fact 還流のみ） | 0 |
| Stop `Cost tracking` | DH 未実装 | 0 |
| Stop `Session persist` | DH 未実装（git versioning で代替） | 低 |
| SessionStart `Load prior context` | DH 未実装（philosophy.md / SPEC 読込は spec-architect 起動時に手動） | 低 |
| PostToolUse `PR logger` | `gh pr create` 後の手動記録 | 低 |

**結論**: DH は **Claude Code hook 機構を全く使用していない**。本案件で hook 機構の参照モードを subphase-l04-transition.md に追加することは DH 拡張の自然な方向。

---

## 5. DH 方法論での生成手順

ECC `hooks/` 級の出力を DH が **ドメイン固有で生成** する手順:

1. **L0 spec-architect 対話で hook 要件抽出**: 「自動化したい繰り返しチェック」「禁止操作の防止」「観測したいイベント」を `dialog-questions.md` で聴取
2. **subphase-l04-transition.md 起動**: 「ECC hooks イベントトリガ参照モード」（Phase 2 タスク B で追加）で、ドメインに必要な hook 一覧を導出
3. **hooks.json テンプレ**: 公式 Claude Code schema 準拠で生成（`scaffold-checklist.md` に Phase 3 タスク C で規約追加）
4. **配置先**: 利用者プロジェクトの `~/.claude/hooks/hooks.json` または `.claude/settings.json` 内 `hooks` キー（ECC 互換）

---

## 6. 観測注釈

- **Claude Code 公式 schema**: ECC は `$schema: "https://json.schemastore.org/claude-code-settings.json"` を明示。DH も今後 hook 機構を採用する場合は同 schema 準拠が望ましい
- **plugin marketplace**: ECC は `CLAUDE_PLUGIN_ROOT` 解決ロジックで複数の plugin 配置パス（`~/.claude/plugins/ecc/`, `~/.claude/plugins/marketplace/ecc/` 等）に対応。DH は plugin として配布しないため、この複雑性は不要
- **opt-in governance**: `pre:governance-capture` は `ECC_GOVERNANCE_CAPTURE=1` で opt-in。DH の `human-review-needed` ラベル opt-in モデルと思想的に類似
- **block exit code**: PreToolUse のみ `exit 2` でブロック可能（PostToolUse 不可）— Claude Code hook 機構の基本制約

---

## 7. リスクと注視点

- **hook 暴走**: PreToolUse で誤ブロックすると全ツール使用不能。DH が hook を導入する場合は `harness-verify.yml` の月次 cron で hooks.json 自身を検証する必要
- **観測データ過剰収集**: `pre:observe:continuous-learning` が全ツール呼出を観測 → ストレージ膨張リスク。DH の継続学習機構設計時に scope 限定が必要

---

**TODO**（Council 議題 1 採決後）:
- 正式パス移動
- ECC `hooks.json` の全 hook 完全列挙（現状は PreToolUse 9 件 + PostToolUse/Stop/Session 抜粋）
- DH 自身に hook 機構導入する是非を別議題化（v6.0.0 候補）
