# Dialog Harness v4.2 → v5.0.0 Migration Guide

dialog-harness/layer's を v4.2 から v5.0.0 へ移行する既存プロジェクト向けの手順書。

## 概要

v5.0.0 は GitHub 連携を前提とした自律駆動の段階的拡張を導入する **major** リリース。後方互換破壊を含む。

主要変更：

1. **`council/` → `crosscut-council/` リネーム**（破壊的）
2. **L0 判定軸に `dev_mode` 追加**（非破壊、既存 REGIME.md は local_only 相当として動作）
3. **5 つの crosscut skill 追加**（仕様 1〜4 の Skill 化）
4. **CTL 連動の段階的自動化**（4 仕様すべてに組み込み）
5. **GitHub Actions 雛形配置**（templates/.github/workflows/）
6. **semver 厳格化**（v5.0.0 以降）

詳細仕様は `dh-upgrades/upgrade-spec-v5.0.0.md` を参照。

---

## 必須移行手順（破壊的変更への対応）

既存プロジェクトが v5.0.0 ベースの harness を使い続けるために必要な作業。

### 手順 1: skill ディレクトリのリネーム

```bash
# プロジェクトルートで実行
git mv .claude/skills/council .claude/skills/crosscut-council
```

### 手順 2: パス参照の置換

プロジェクト内のファイルで `council/` への参照を `crosscut-council/` へ置換：

```bash
# 検出（移行漏れチェック）
grep -RIn 'skills/council/' .claude/ 2>/dev/null | grep -v 'crosscut-council' | grep -v 'COUNCIL-LOG'
grep -RIn '\.\./council/' .claude/ 2>/dev/null | grep -v 'crosscut-council'

# 一括置換（dry-run の上で実施）
sed -i 's|skills/council/|skills/crosscut-council/|g' \
  $(grep -rl 'skills/council/' .claude/ 2>/dev/null | grep -v 'crosscut-council')
```

`COUNCIL-LOG.md` などの歴史ファイル名は変更しない（v5.0.0 spec §4.1.3 で許容）。

### 手順 3: .gitignore の更新

`council-workspace/` を `crosscut-council-workspace/` に置換。

```diff
-.claude/skills/council-workspace/
+.claude/skills/crosscut-council-workspace/
```

### 手順 4: REGIME.md の dev_mode セクション追加

既存 REGIME.md の末尾に以下を追記：

```markdown
## dev_mode
- mode: local_only           # 当面は local_only のまま運用可能
- ctl: 0                     # CTL 値を継続（既存値があればそれを記録）
- 判定根拠: 既存プロジェクトの v5.0.0 移行（GitHub 連携は段階的に検討）
```

GitHub 連携を始める場合は `github_assisted` に昇格、ARCH-DECISIONS に根拠を記録。

### 手順 5: 移行確認

```bash
# council/ 残骸が無いこと
grep -RIn 'skills/council/' .claude/ 2>/dev/null | grep -v 'crosscut-council' | grep -v 'COUNCIL-LOG'

# crosscut-council/SKILL.md が存在すること
test -f .claude/skills/crosscut-council/SKILL.md && echo OK
```

両コマンドが空 / OK を返せば移行完了。

---

## 任意移行手順（v5.0.0 新機能の採用）

必須ではないが、v5.0.0 の新機能を活用する場合に実施。

### 任意 1: dev_mode 昇格

`local_only` → `github_assisted` または `github_autonomous` への昇格手順：

1. REGIME.md の `dev_mode.mode` を変更
2. `history/ARCH-DECISIONS.md` に昇格根拠を記録（規模・チーム・運用状況）
3. CTL を再評価（昇格初期は CTL-0 から始めて慣らす）

判定プロトコルの詳細は `.claude/skills/layer0-spec-architect/references/regime-assessment.md` の `## dev_mode 判定` セクション参照。

### 任意 2: 仕様 1〜4（crosscut skill）の利用

5 つの crosscut skill が新たに利用可能：

| Skill | 役割 | 起動タイミング |
|---|---|---|
| `crosscut-issue-dispatcher` | SPEC/ADR 差分から Issue 生成 | commit hook / 明示コマンド |
| `crosscut-issue-implementer` | Issue → 実装起動 | Issue assigned / label 付与 |
| `crosscut-verifier-drift` | SPEC/ADR 乖離検出 | PR 作成時 CI |
| `crosscut-verifier-philosophy` | 5 本柱整合検証（v5.1.0 では placeholder のまま、v5.2.0 候補として継続検討） | placeholder |
| `crosscut-feedback-loop` | 検出 → 還流 | 検証 FAIL / drift / 思想違反検出時 |

`local_only` では発動しない。`github_assisted` 以上で利用可能。

### 任意 3: GitHub Actions 雛形のコピー

dialog-harness 配布元の `templates/.github/workflows/` をプロジェクトの `.github/workflows/` にコピー：

```bash
# 配布元の templates/ を取得（手動またはスクリプト）
mkdir -p .github/workflows
cp -R <dh-source>/templates/.github/workflows/*.yml .github/workflows/
```

各 yml の冒頭コメント（`# Required mode:` `# Required CTL:`）を確認し、プロジェクトの REGIME.md と整合する yml のみ採用する。

採用後、各 yml の `Replace with ...` プレースホルダをプロジェクトのコマンドに差し替える。

### 任意 4: `claude-code-action` のバージョンピン止め

`templates/.github/workflows/issue-to-impl.yml` の `<latest>` プレースホルダを公式リポジトリの最新版（vX.Y.Z）にピン止めする：

```yaml
- uses: anthropics/claude-code-action@v1.2.3  # 例。実装時点で公式リポジトリ確認
```

### 任意 5: CTL 育成戦略の運用

`crosscut-council/references/ctl-maturity-strategy.md` に従って CTL 育成を開始：

- 量条件: Council 判定 ≥ 10 件 で CTL-0 → CTL-1 検討
- 質条件: 一致率 ≥ 0.85, override ≤ 0.15, reject ≤ 0.05
- 横断蓄積（`~/.claude/council-data/stats.json`）でプロジェクト内件数を補える

CTL 変動は L0 振り返り儀式（F1/F2/F3）で判定。

---

## 後退手順（v5.0.0 の不採用）

v5.0.0 の新機能を使わずに v4.2 互換で運用したい場合：

1. 必須移行手順 1〜5 のみ実施（リネーム + REGIME.md の dev_mode を local_only で記録）
2. 任意移行手順 1〜5 はすべてスキップ
3. crosscut skill 5 件は配置されているが、`local_only` モードでは発動しない

これで実質的に v4.2 と同じ動作になる。

---

## トラブルシューティング

### Q1. `crosscut-council` を呼ぶと「スキルが見つかりません」と言われる

A1. `.claude/skills/crosscut-council/SKILL.md` の `name:` フィールドが `name: crosscut-council` になっているか確認。リネーム時に SKILL.md frontmatter の更新が漏れている可能性。

### Q2. `~/.claude/council-data/` というディレクトリが残っているが消すべき？

A2. 残してください。これは**ユーザースコープの横断蓄積パス**で、プロジェクトを跨いだ Council 統計を保持する。spec §3.2.8 で固定。skill ディレクトリ名のリネームとは無関係。

### Q3. CI 上で drift 検証が常に PASS する

A3. CTL ≥ 1 で発動。REGIME.md の `dev_mode.ctl` を確認。`local_only` モードでも CTL は記録するが、CI 上の drift 検証は `github_assisted` 以上が前提。

### Q4. 既存の `~/.claude/council-data/stats.json` が壊れる？

A4. 壊れません。crosscut-council 内部の参照は同じ統計ファイルを引き続き読み書きする。

### Q5. v5.0.0 を採用すると既存の Layer skill 動作が変わる？

A5. 変わりません。`layer0-spec-architect` / `layer1-autonomous-dev` / `layer1-independent-reviewer` 等の本体ロジックは v4.2 から不変。v5.0.0 の追加は references の追記と関連スキルセクションへの crosscut 系参照追加のみ。

---

## 参照

- `dh-upgrades/upgrade-spec-v5.0.0.md` — v5.0.0 仕様原典（1500 行）
- `history/REGIME-LOG.md` — major 昇格記録
- `history/ARCH-DECISIONS.md` — AD-001〜AD-007 の設計判断
- `history/INTENT.md` — v5.0.0 で追加された概念の意図
- `delivery/SELF-VERIFICATION-v5.0.0.md` — 配布元の自己検証結果
