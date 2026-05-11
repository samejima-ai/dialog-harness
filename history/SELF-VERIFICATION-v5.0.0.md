# SELF-VERIFICATION v5.0.0

dialog-harness/layer's v4.2 → v5.0.0 メジャーアップグレードの自己検証結果。

- 検証日: 2026-04-27
- ブランチ: `claude/prepare-major-upgrade-vnL6E`
- AI 能力バージョン: claude-opus-4-7
- 体制: M2 標準モード（L0 spec-architect → L1 autonomous-dev + layer1-independent-reviewer）
- spec 原典: `dh-upgrades/upgrade-spec-v5.0.0.md`
- 自己検証フォーマット: spec §5.5 準拠

総合判定: **PASS**（5.3.2 README バッジは「適用対象外」）

---

## 5.1 構造的整合性

### 5.1.1 ディレクトリ構造

| 項目 | 期待 | 実態 | 判定 |
|---|---|---|---|
| `.claude/skills/crosscut-council/` 存在 | ○ | ○ | PASS |
| `.claude/skills/council/` 不在 | ○ | ○ | PASS |
| `.claude/skills/crosscut-issue-dispatcher/` 存在 | ○ | ○ | PASS |
| `.claude/skills/crosscut-issue-implementer/` 存在 | ○ | ○ | PASS |
| `.claude/skills/crosscut-verifier-drift/` 存在 | ○ | ○ | PASS |
| `.claude/skills/crosscut-verifier-philosophy/` 存在 | ○ | ○ | PASS |
| `.claude/skills/crosscut-feedback-loop/` 存在 | ○ | ○ | PASS |
| `templates/.github/workflows/` に 9 yml | ○ | 9 ファイル確認 | PASS |
| `dh-upgrades/upgrade-spec-v5.0.0.md` 配置 | ○ | 1500 行配置済 | PASS |
| `history/{CHANGELOG, REGIME-LOG, ARCH-DECISIONS, INTENT}.md` 4 ファイル | ○ | 全 4 ファイルに v5.0.0 記述あり | PASS |
| `docs/migration-guide-v5.0.0.md` 存在 | ○ | ○ | PASS |
| `delivery/SELF-VERIFICATION-v5.0.0.md` 存在 | ○ | 本ファイル | PASS |

### 5.1.2 参照パス整合性

```bash
$ grep -RIn 'skills/council/' .claude/ docs/ templates/ history/ 2>/dev/null \
    | grep -v 'crosscut-council' | grep -v 'COUNCIL-LOG'
（出力なし）

$ grep -RIn '\.\./\.\./council/' .claude/ 2>/dev/null
（出力なし）
```

旧 `council/` パス参照の残骸なし。`crosscut-council/references/design-history.md` の歴史記述 2 件のみ残存（spec §4.1.3 で許容）。

判定: **PASS**

### 5.1.3 SKILL.md 最低要件（frontmatter）

5 新規 crosscut skill の SKILL.md が `name:` + `description:` を含むことを確認：

```bash
$ for f in .claude/skills/crosscut-*/SKILL.md; do
    head -5 "$f" | grep -E '^(name|description):' >/dev/null || echo "MISSING: $f"
  done
（出力なし）
```

判定: **PASS**

### 5.1.4 yml 構文妥当性

```bash
$ for f in templates/.github/workflows/*.yml; do
    python3 -c "import yaml; yaml.safe_load(open('$f'))" 2>&1
  done
（全 9 ファイル PASS）
```

判定: **PASS**

### 5.1.5 各 yml の必須コメント

| ファイル | `# Required mode:` | `# Required CTL:` |
|---|---|---|
| basic-ci.yml | ○ | ○ |
| e2e-ci.yml | ○ | ○ |
| interaction-cost.yml | ○ | ○ |
| spec-drift.yml | ○ | ○ |
| issue-dispatch.yml | ○ | ○ |
| issue-to-impl.yml | ○ | ○ |
| drift-feedback.yml | ○ | ○ |
| auto-merge.yml | ○ | ○ |
| auto-degrade.yml | ○ | ○ |

判定: **PASS**

---

## 5.2 5本柱整合（philosophy.md 6条憲法）

| 柱 | 確認項目 | 判定 |
|---|---|---|
| P1 フラクタル原則 | L3 運用層を新設していないか / crosscut- は横断機構として L0/L1/L2 の上位ではなく直交軸 | PASS |
| P2 Shift Left 原則 | drift 検知の追加層は計算時/CI 時に前倒し検出する設計 | PASS |
| P3 情報純度原則 | 5 crosscut skill の責務分離、各 SKILL.md は単一責務 | PASS |
| P4 人間責務 | 履歴層 4 ファイル全て v5.0.0 で記録、ARCH-DECISIONS で意思決定追跡可 | PASS |
| P5 献上哲学 | 自走中に人間質問せず、対話は仕様確認のみ。本献上は SELF-VERIFICATION 経由 | PASS |
| 第6条 人間 ≒ Council | CTL システム（既存 v4.2）は不変、ctl-maturity-strategy.md で育成戦略を明文化 | PASS |

判定: **PASS（全項目）**

### 5.2.1 philosophy.md 不変性

`layer0-spec-architect/references/philosophy.md` の本文（5本柱原典 + 第6条）は v5.0.0 で不変。`council/` → `crosscut-council/` のパス参照のみ更新（5 箇所）。

```bash
$ git diff 2766334..HEAD -- .claude/skills/layer0-spec-architect/references/philosophy.md
（パス置換のみ、思想本文の改変なし）
```

判定: **PASS**

---

## 5.3 後方互換性（意図せぬ破壊の混入チェック）

### 5.3.1 spec で承認された破壊的変更（許容）

| 破壊項目 | spec 出典 | 移行手段 |
|---|---|---|
| `council/` → `crosscut-council/` リネーム | §4.1 | docs/migration-guide-v5.0.0.md §手順 1 |
| `.gitignore` の `council-workspace/` リネーム | §4.1.2.4 | 同 §手順 3 |
| バージョン記法 `vX.Y` → `vX.Y.Z` | §4.6 | v4.x 互換受理を credit-template.md に明記 |

### 5.3.2 意図せぬ破壊が混入していないかの確認

| 検査項目 | 結果 |
|---|---|
| Level A skill 本体ロジック | 不変（layer0-* / layer1-* / layer2-* の本体は references 追記のみ） |
| 5 層エラー検出スタック | 不変（drift / 思想を「追加層」として位置付け、既存層は触らない） |
| 履歴層スキーマ | 不変（spec §5.3 内の history-layer-spec.md 形式に準拠） |
| Council ペルソナ重み | 不変（council-weights.md / personas/ は触らない） |
| Lifecycle 軸 | 不変（dev_mode は別軸として並列追加） |
| meta-spec-template.md の既存セクション | 不変（dev_mode セクションを追加挿入のみ） |
| meta-spec-template.md の REGIME.md テンプレ既存フィールド | 不変 |

判定: **PASS**

### 5.3.3 README バッジ（spec §4.6.2.4）— 適用対象外

spec §4.6.2.4 は v5.0.0 のバージョンバッジを README.md に追加するよう指示するが、リポジトリルートに `README.md` が存在しない（"skill-only repository" 方針、PR #3）。

代替記録：
- `assets/credit-template.md`: バージョン記法 semver 化（v5.0.0 例を更新）
- `layer0-spec-architect/SKILL.md`: バージョン履歴セクションに v5.0.0 エントリ追加
- `history/REGIME-LOG.md`: major 昇格記録

判定: **適用対象外**（FAIL ではない、AD-006 で記録）

### 5.3.4 docs/ の gitignore 例外

skill-only policy（PR #3）で `docs/` は gitignore されているが、配布対象 migration guide は spec §5.4.2 で必須。`.gitignore` に `!docs/migration-guide-*.md` 例外を追加（AD-007）。

判定: **PASS**（最小例外で対応）

---

## 5.4 既存プロジェクト影響（migration-guide 整備）

### 5.4.1 migration-guide-v5.0.0.md の網羅性

| 内容 | 含まれているか |
|---|---|
| 必須移行手順 1〜5（リネーム / パス置換 / .gitignore / REGIME.md 追記 / 確認） | ○ |
| 任意移行手順 1〜5（dev_mode 昇格 / crosscut skill 利用 / yml コピー / claude-code-action ピン止め / CTL 育成） | ○ |
| 後退手順（v5.0.0 不採用） | ○ |
| トラブルシューティング Q1〜Q5 | ○ |

判定: **PASS**

### 5.4.2 DH 本体改修対象スコープの遵守

spec §1.4 に従い、本リリースは DH 本体配布元のみを改修対象とする。各既存プロジェクトの個別改修は migration guide 経由で owner 判断とする。

判定: **PASS**

---

## 5.5 不変項目（spec §2）遵守確認

| 不変項目 | 遵守 |
|---|---|
| 1. 5本柱原則（P1-P5） | ○ |
| 2. 履歴層規約 | ○（history/ 4 ファイル v5.0.0 セクション初期化） |
| 3. 献上プロトコル | ○（本 SELF-VERIFICATION で献上） |
| 4. Level A skill 本体不変 | ○（layer skill は references / 関連スキルセクション追記のみ） |
| 5. 継承禁止項目の指定自体 | ○（spec §2 を REGIME-LOG.md §不変項目で明示再掲） |
| 6. 3層 + 1横断構造 | ○（crosscut- prefix で構造を命名で明示化、L3 新設なし） |

判定: **PASS（6項目すべて）**

---

## 5.6 コミット履歴（7 コミット、Step 単位）

| Step | Hash | メッセージ |
|---|---|---|
| 0 | fac81a3 | chore: scaffold dh-upgrades/, history/, docs/, delivery/ for v5.0.0 work |
| 1 | 899bc8f | feat(crosscut): rename council/ to crosscut-council/ (v5.0.0 step 1) |
| 2 | 8493e14 | feat(layer0): add dev_mode axis to regime assessment (v5.0.0 step 2) |
| 3 | 3994d7e | feat(crosscut): add 5 crosscut skills for GitHub integration (v5.0.0 step 3) |
| 4 | cb9fbc6 | feat(crosscut): add CTL-conditional protocols and maturity strategy (v5.0.0 step 4) |
| 5 | ebf40dc | feat(templates): add GitHub Actions workflow templates (v5.0.0 step 5) |
| 6 | 8b36285 | chore(version): bump DH to v5.0.0 (v5.0.0 step 6) |

最終: 本コミット（docs: add migration guide and self-verification for v5.0.0）

---

## 5.7 残課題・既知の制約

### 5.7.1 v5.1.0 で対応予定

- `crosscut-verifier-philosophy` の本実装（v5.0.0 では placeholder）
- 思想 FAIL の自動還流（feedback-protocol.md で接続箇所は確保済み）

### 5.7.2 v5.x で対応予定

- チーム軸（T1-T5）の operational 化（spec §3.1.1 / §3.2.2 で言及あるが v5.0.0 では未実装、規模 + Lifecycle を proxy として運用）
- README.md 整備（skill-only policy の見直し含む別案件）

### 5.7.3 サンプルプロジェクトでの試運転（spec §6 該当部）

本献上では spec §6 の「サンプルプロジェクト試運転」は実施していない。次フェーズでユーザー側で実行されることを前提とする。

---

## 5.8 体制事後評価

- M2 体制は適切。判断点（C2/C4）の発生は dispatch-protocol.md / feedback-protocol.md の設計時に 2 件発生したが、いずれも spec で承認された範囲内で `crosscut-council` 起動条件未達と判断、自走で解決
- L2 発動閾値（SPEC > 15k tok / >80 files / domains ≥ 5 / 並行 ≥ 3 / 1サイクル > 2h）には到達せず（実態: 1500 行 spec / 12 編集ファイル / 単一ドメイン / 7 step 直列 / 各 step 5〜15 分）
- 次回以降の同種改修も M2 で吸収可能

## 5.9 layer1-independent-reviewer による独立検証

本献上後、`layer1-independent-reviewer` を起動して `delivery/VERIFICATION.md` を別途生成すること（spec § / SKILL.md §7 常時必須）。本ファイルは L1 自己検証であり、独立検証ではない。

---

## 総合判定

**PASS**

- 構造的整合性: PASS
- 5本柱整合: PASS
- 後方互換性（意図せぬ破壊の混入チェック）: PASS
- 既存プロジェクト影響（migration-guide 整備）: PASS
- 不変項目遵守: PASS（6項目）

唯一の例外：spec §4.6.2.4 README バッジは「適用対象外」（README.md 不在のため）。SELF-VERIFICATION FAIL ではない。

最終承認は人間判断（spec §6 哲学的整合性最終判断 + サンプルプロジェクト試運転）に委ねる。
