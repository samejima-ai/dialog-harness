---
name: rtk-integration
dimension: D4
description: >
  Claude Code 用の rtk (Rust Token Killer) 統合スキル。
  rtk は Rust 製 CLI プロキシで、Claude Code が Bash 経由で実行する
  git / test / build / lint 出力を 60-90% 圧縮しトークン消費を大幅削減する。
  「rtk を導入したい」「rtk 入れて」「トークン節約したい」「Bash 出力を圧縮したい」
  「rtk-integration」等の発話に加え、
  症状語「git log の出力が長すぎる」「テストのログで context が膨らむ」
  「Bash の出力が長くて context を食う」「コンテキストがすぐ埋まる」「context window が足りない」
  「ビルド出力が冗長」「CLAUDE.md に rtk 設定したい」 等でも本スキルの起動を必ず検討する。
  install / uninstall / 越境パッチ適用までを自己完結で実行する。
  対象: Windows native（MSVC ビルド、rtk v0.37.1 固定）。
---

# rtk-integration

Claude Code に rtk を統合し、Bash 経由コマンドのトークン消費を 60-90% 削減するスキル。

## 原則

- **セルフコンテインド**: install に必要な全工程（バイナリ取得 / PATH 配置 / `rtk init -g` / 越境パッチ）を自己完結で実行する
- **v0.37.1 固定**: 勝手に latest を追わない
- **Windows native のみ**: macOS / Linux / WSL 向け処理は書かない
- **グローバル化は仕様**: `rtk init -g` で全 Claude Code セッションに波及するのは意図通り
- **通知のみの越境パッチ**: layer0/layer1 スキルへの追記は未導入検知通知に限定、自動導入はしない
- **可逆性**: uninstall で元に戻せる状態を維持する

## 処理フロー

```
1. 発動条件チェック（OS / 既存インストール状態）
2. rtk バイナリ取得
   2.1. GitHub Releases v0.37.1 から rtk-x86_64-pc-windows-msvc.zip を取得
   2.2. %USERPROFILE%\.local\bin\rtk\ に展開
3. PATH 追加（User scope）
   3.1. %USERPROFILE%\.local\bin\rtk を User PATH に追加
   3.2. 新規セッションで有効化されることを通知
4. rtk init -g 実行（Claude Code グローバルフック有効化）
5. 越境パッチ適用（3 ファイル）
   5.1. layer0-spec-architect/SKILL.md に通知ブロック挿入
   5.2. layer0-onboarding/SKILL.md に通知ブロック挿入
   5.3. layer1-autonomous-dev/SKILL.md に通知ブロック挿入
6. 動作確認
   6.1. rtk --version
   6.2. rtk init --show
   6.3. 任意リポジトリで rtk git status
7. 完了報告
```

## 実行コマンド

### install

Windows PowerShell で以下を実行する:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\rtk-integration\scripts\install.ps1"
```

スクリプトは以下を順次実行する:
1. rtk v0.37.1 の MSVC zip を GitHub Releases から取得
2. `%USERPROFILE%\.local\bin\rtk\` に展開
3. User scope PATH に追加（`setx PATH`）
4. `rtk init -g` 実行
5. 越境パッチを `~/.claude/skills/` 配下 3 ファイルに適用

### uninstall

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\rtk-integration\scripts\uninstall.ps1"
```

1. `rtk init --uninstall` でグローバルフック撤去
2. 越境パッチをマーカー範囲で機械的に削除
3. `%USERPROFILE%\.local\bin\rtk\` を削除
4. User scope PATH から該当パスを除去

## 対象コマンド（ホワイトリスト）

詳細は `references/commands.md` 参照。

| 分類 | 対象 |
|---|---|
| git | status / diff / log / show / blame |
| test | cargo test / pytest / go test / npm test / jest / vitest |
| build | cargo build / tsc / npm run build / vite build |
| lint | eslint / tsc --noEmit / ruff / clippy |

rtk 非対応コマンドは素通しされる（rtk 側の仕様に依存）。

## 圧縮例（イメージ）

`rtk git status` 実行時の before/after（社内リポジトリでの実測目安）:

**before（素の `git status`、約 600 tokens）:**
```
On branch master
Your branch is up to date with 'origin/master'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   src/auth/register.py
        modified:   src/auth/login.py
        modified:   tests/test_auth.py
        ... (30 行続く)
```

**after（`rtk git status`、約 120 tokens、-80%）:**
```
master ↑0 ↓0
M src/auth/{register,login}.py, tests/test_auth.py
?? docs/new-feature.md
```

冗長な hint（`use "git add"...`）を全削除、同ディレクトリ複数ファイルを `{}` 展開で集約、未追跡は `??` で 1 行化。git log / test / build / lint も同様の集約ルールが適用される（詳細 `references/commands.md`）。

## 導入先 CLAUDE.md への追記テンプレ

`references/claude-md-template.md` 参照。導入先プロジェクトの CLAUDE.md に以下の一文をコピーすることを推奨する:

> Bash で git status / diff / log / show / blame およびテスト・ビルド・リンタ系を実行するときは、rtk 経由（`rtk git status` 等）を優先する。グローバルフックで自動リライトされる想定だが、冗長な安全網として明示する。

## 越境パッチの仕様

`references/cross-skill-patch.md` 参照。以下 3 ファイルにマーカー `<!-- rtk-integration: begin -->` / `<!-- rtk-integration: end -->` で囲まれた通知ブロックを追加する:

- `~/.claude/skills/layer0-spec-architect/SKILL.md`
- `~/.claude/skills/layer0-onboarding/SKILL.md`
- `~/.claude/skills/layer1-autonomous-dev/SKILL.md`

通知内容:

> **rtk 未導入**: `/rtk-integration` を呼ぶと Claude Code の Bash 出力が 60-90% 圧縮されます（git/test/build/lint 対象、Windows native）。

未導入時のみ / セッション初回 1 回のみ。

## トラブルシュート

`references/troubleshoot.md` 参照。典型ケース:
- `rtk --version` で command not found → 新規ターミナル起動 or `refreshenv`（Chocolatey 導入環境）or PATH 手動追加
- `rtk init -g` が権限エラー → User scope でのみ動作することを確認
- 圧縮されない → `rtk init --show` でフック設置確認

## 参照ドキュメント

- `references/commands.md` — 対応コマンド一覧と各コマンドの圧縮率目安
- `references/troubleshoot.md` — 典型的な失敗ケースと対処
- `references/claude-md-template.md` — 導入先 CLAUDE.md 追記テンプレ
- `references/cross-skill-patch.md` — 越境パッチの内容と撤去手順
- `references/sha-update-protocol.md` — `$RtkVersion` bump 時の `$ExpectedSha256` 更新プロトコル（Council 諮問 `rtkSHA` 採決、philosophy 第 2 条 Shift Left + 第 6 条 人間最終承認 と整合）
