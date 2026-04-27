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

### Step 2: dev_mode 軸追加

- `layer0-spec-architect/SKILL.md` §4 モード判定に「dev_mode 軸（v5.0.0 追加）」サブセクション追加
- `references/regime-assessment.md` 末尾に「dev_mode 判定（v5.0.0 追加）」セクション追加（モード境界 / 2 段階判定プロトコル / REGIME.md 記録形式 / 昇格降格規則）
- `assets/meta-spec-template.md` の REGIME.md テンプレに `## dev_mode` セクション追加（mode / ctl / 判定根拠）
- 注記: spec §3.1.1 のチーム軸（T1-T5）は v5.0.0 では未実装。規模 + Lifecycle を proxy として運用。チーム軸 operational 化は v5.x で扱う（INTENT.md 記録）

### Step 3: 仕様 1〜4 Skill 追加

5 つの crosscut- skill を新規作成（spec §4.3）：

- `crosscut-issue-dispatcher/SKILL.md`（仕様 1：Issue 射出）
- `crosscut-issue-implementer/SKILL.md`（仕様 2：Issue → 実装、claude-code-action 公式採用注記）
- `crosscut-verifier-drift/SKILL.md`（仕様 3-drift：SPEC/ADR 乖離検証、5 層検出スタックの追加層）
- `crosscut-verifier-philosophy/SKILL.md`（仕様 3-哲学：placeholder、v5.1.0 で本実装）
- `crosscut-feedback-loop/SKILL.md`（仕様 4：種別ごとの還流先決定）

各 SKILL.md は frontmatter + 発動条件 + 処理フロー + CTL 別動作 + 関連参照のみのタイト構成。protocol references は Step 4 で追加。

`layer1-autonomous-dev/SKILL.md` および `layer1-independent-reviewer/SKILL.md` の関連スキルセクションに crosscut- 系参照を追加（spec §4.3.4 完了条件）。
