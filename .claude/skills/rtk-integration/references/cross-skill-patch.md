# 越境パッチ仕様

rtk-integration が `~/.claude/skills/` 配下の既存 L0/L1 スキルに追加する通知ブロックの正式仕様。

## 対象ファイル

- `~/.claude/skills/layer0-spec-architect/SKILL.md`
- `~/.claude/skills/layer0-onboarding/SKILL.md`
- `~/.claude/skills/layer1-autonomous-dev/SKILL.md`

## 挿入位置

各ファイルの **末尾**（本文全セクションの後）に、マーカーコメントで囲んで追加する。

## 挿入内容

```markdown

<!-- rtk-integration: begin -->
## rtk 未導入検知（rtk-integration スキルが提供）

スキル起動直後、セッション初回のみ以下を実行する:

1. `rtk --version` を実行
2. コマンドが存在しない、または exit code が非ゼロの場合、以下を 1 回だけ通知する:

   > **rtk 未導入**: `/rtk-integration` を呼ぶと Claude Code の Bash 出力が 60-90% 圧縮されます（git/test/build/lint 対象、Windows native）。

3. 導入済み、またはセッション内で既に通知済みの場合は沈黙する

この検知は通知のみであり、自動導入や設定ファイル編集は一切行わない。
<!-- rtk-integration: end -->
```

## 制約

- **通知のみ**: `rtk init` や hook 編集等の自動導入コマンドは含めない（CLAUDE.md 不変ルール #7）
- **セッション初回 1 回のみ**: 同一セッション内で複数回通知しない
- **未導入時のみ**: `rtk --version` が成功したら沈黙
- **マーカー必須**: `<!-- rtk-integration: begin -->` / `<!-- rtk-integration: end -->` で囲む（撤去可能性の担保）

## 撤去手順（uninstall.ps1 が実施）

1. 対象 3 ファイルを読み込む
2. 正規表現 `(?s)\r?\n?<!-- rtk-integration: begin -->.*?<!-- rtk-integration: end -->\r?\n?` でマッチ範囲を削除
3. 元に書き戻す

マーカー範囲外のコンテンツは一切変更しない。

## 冪等性

同じ install.ps1 を 2 度実行しても同じ結果になる（既にマーカーがあれば再追加しない）。
