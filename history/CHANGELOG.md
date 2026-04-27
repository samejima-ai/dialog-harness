# CHANGELOG

DH 本体の改修履歴。各 Step の実行記録を時系列で追記する。

## v5.0.0 (in progress)

major 昇格。dev_mode 軸追加 / crosscut- prefix 統一 / 仕様 1〜4 Skill 化 / CTL 連動 / GitHub Actions 雛形 / 業界 BP 取り込み（claude-code-action）。

詳細は `dh-upgrades/upgrade-spec-v5.0.0.md` 参照。

### Step 0: scaffold

- `dh-upgrades/`, `history/`, `docs/`, `delivery/` 新規作成
- `dh-upgrades/upgrade-spec-v5.0.0.md` 配置（1500 行、自己改修指示書）
- `.gitignore` に `docs/migration-guide-*.md` 例外追加（AD-007）

### Step 1: crosscut- リネーム（後方互換破壊）

- `git mv .claude/skills/council .claude/skills/crosscut-council`（17 ファイル、履歴保持）
- `crosscut-council/SKILL.md` frontmatter: `name: council` → `name: crosscut-council`、description に「横断判定機構（crosscut prefix）」明記
- 外部参照パス更新（4 ファイル / 8 箇所）:
  - `layer1-autonomous-dev/SKILL.md`: `\`council\`` → `\`crosscut-council\`` (4) + path 2
  - `layer0-spec-architect/references/regime-assessment.md`: path 2
  - `layer0-spec-architect/references/philosophy.md`: path 4
- `.gitignore`: `council-workspace/` → `crosscut-council-workspace/`
- 残留: `crosscut-council/references/design-history.md` の歴史記述 2 箇所のみ（spec §4.1.3 で許容）
- 維持: `~/.claude/council-data/` 横断蓄積パス（spec §3.2.8 でユーザースコープ固定）
