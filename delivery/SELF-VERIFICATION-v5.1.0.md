# SELF-VERIFICATION v5.1.0

dialog-harness/layer's v5.0.0 → v5.1.0 マイナーアップグレードの自己検証結果。

- 検証日: 2026-04-28
- ブランチ: `claude/prepare-major-upgrade-vnL6E`
- AI 能力バージョン: claude-opus-4-7
- 体制: M2 標準モード（L0 spec-architect → L1 autonomous-dev + layer1-independent-reviewer）
- 起源: PR #19 テストレビュー（シナリオ「ケロぴの森」）の P0 4 項目
- 自己検証フォーマット: v5.0.0 準拠

総合判定: **PASS**

---

## 1. 構造的整合性

### 1.1 新設ファイルの存在

| 項目 | 期待 | 実態 | 判定 |
|---|---|---|---|
| `.claude/skills/layer0-spec-architect/references/scaffold-checklist.md` | ○ | 78 行配置済 | PASS |
| `docs/migration-guide-v5.1.0.md` | ○ | 配置済 | PASS |
| `delivery/SELF-VERIFICATION-v5.1.0.md` | ○ | 本ファイル | PASS |

### 1.2 SKILL.md セクション追加

| セクション | 期待 | 実態 | 判定 |
|---|---|---|---|
| §0 「L0 完了の受け入れ基準（v5.1.0 追加）」 | ○ | line 32 付近に挿入確認 | PASS |
| §1.5 Pre-flight 行（処理フロー注記内） | ○ | `ritual-protocol.md` 必読を明記 | PASS |
| §3.5 Pre-flight 行 | ○ | `subphase-selection.md` 必読を明記 | PASS |
| §4 Pre-flight 行 | ○ | `regime-assessment.md` 必読を明記 | PASS |
| §6 Pre-flight 行 | ○ | `dev-env-spec.md` + `scaffold-checklist.md` 必読を明記 | PASS |
| §7 Pre-flight 行 | ○ | `credit-template.md` 必読を明記 | PASS |
| §7.4 L0 自己検証ステップ | ○ | §7 と §7.5 の間に新設、5 件チェックボックス配置 | PASS |
| 参照ドキュメント節「v5.1.0 追加」エントリ | ○ | v5.0.0 セクションの上に積層 | PASS |

### 1.3 既存セクション番号の不変

§7.5 / §7.6 / 既存 v5.0.0 / v4.x 履歴節すべて section 番号と内容は不変。§7.4 を §7 と §7.5 の間に新設したため番号衝突なし。

判定: **PASS**

### 1.4 SKILL.md frontmatter 妥当性

```bash
$ head -16 .claude/skills/layer0-spec-architect/SKILL.md
```

frontmatter（name + description）は変更なし。description 文字数は v5.0.0 から不変、1024 文字制限内。

判定: **PASS**

### 1.5 history 4 ファイルの v5.1.0 セクション

| ファイル | v5.1.0 セクションの内容 | 判定 |
|---|---|---|
| `history/CHANGELOG.md` | v5.1.0 (in progress) + Step 1-5 サマリ | PASS |
| `history/REGIME-LOG.md` | minor 昇格記録 + 不変項目遵守確認 + 次バージョン予定 | PASS |
| `history/ARCH-DECISIONS.md` | AD-008（L0 完了基準再定義）+ AD-009（単一 stack 採用） | PASS |
| `history/INTENT.md` | L0 charter 達成可能性 / Pre-flight 必読化 / scaffold checklist / §7.4 の意図記述 | PASS |

判定: **PASS**

---

## 2. 5本柱整合性

| 柱 | 影響 | 判定 |
|---|---|---|
| P1 フラクタル原則 | L0 受け入れ基準は L1/L2 の検証基準と同型構造（仕様 → 実体 → smoke → 自己検証）を保つ | PASS |
| P2 再帰進化 | テストレビュー指摘 → minor 改修の流れは Lifecycle ≥ 1 の正常進化フロー | PASS |
| P3 責務分離 | scaffold-checklist.md は dev-env-spec.md と直交（stack 別 vs 共通規約） | PASS |
| P4 情報純度 | Pre-flight 必読化により references 読み飛ばしを構造的に排除 | PASS |
| P5 献上哲学 | §7.4 自己検証 PASS が L1 譲渡の前提となり、検証層への負担が前段で削減される | PASS |
| 第6条（人間 ≒ Council） | philosophy.md 不変。本改修は L0 内部の構造改善であり Council 経路には非影響 | PASS |

`philosophy.md` は本改修で **完全不変**。

判定: **PASS**

---

## 3. 後方互換性

### 3.1 既存 SKILL.md セクション本文の不変

既存 §1-§7 / §7.5 / §7.6 / 「決定済み制約」/ 「廃止判断プロトコル」/ 既存「参照ドキュメント」配下 v3.x〜v5.0.0 履歴節すべて本文不変。新規追加は以下のみ：

- §0 内に「L0 完了の受け入れ基準」サブセクション
- §1.5（処理フロー注記）/ §3.5 / §4 / §6 / §7 各冒頭に Pre-flight 行 1 行ずつ
- §7.4 全体（§7 と §7.5 の間に新設）
- 参照ドキュメント節に「v5.1.0 追加」セクション

判定: **PASS**

### 3.2 不変項目（spec §2 遵守）

| 不変項目 | 実態 |
|---|---|
| `references/philosophy.md` | 完全不変 |
| `.claude/skills/crosscut-*/` | 完全不変（v5.0.0 で確立） |
| `templates/.github/workflows/*.yml` | 完全不変 |
| `dh-upgrades/upgrade-spec-v5.0.0.md` | 完全不変 |
| 既存 SKILL.md セクション番号 | 不変（§7.4 は新規番号、§7.5 以降の番号は不変） |

検証コマンド（v5.0.0 成果物の意図せぬ破壊なし）:

```bash
$ git diff origin/master -- .claude/skills/crosscut-*/ templates/ \
    .claude/skills/layer0-spec-architect/references/philosophy.md \
    dh-upgrades/upgrade-spec-v5.0.0.md
（出力なしを期待）
```

判定: **PASS**

### 3.3 Lifecycle ≥ 1 既存プロジェクトへの動作影響

受け入れ基準は v5.1.0 以降に新規開始するプロジェクトと、既存プロジェクトで v5.1.0 以降に追加開始する機能・フェーズに段階適用。既存成果物の遡及修正は要求しない。継続セッションで L0 が再起動されるタイミングで自然に新基準を取り込む（migration script 不要）。

判定: **PASS**

---

## 4. 受け入れ基準の自己適用検証

本 v5.1.0 改修自体が §0 受け入れ基準 4 条件を満たすかの自己宣言。本改修は DH 本体メタ案件であり通常プロジェクト構造とは異なるため、各条件は本改修文脈に翻訳して評価する。

| 条件 | 翻訳 | 実態 | 判定 |
|---|---|---|---|
| 1. 仕様充足 | 本改修の改修指示書（プラン）の必須項目（§0/Pre-flight/scaffold/§7.4）が全て実装されたか | Step 1-5 + Final で全項目実装 | PASS |
| 2. scaffold 実体 | 本改修で「実体ファイル」が生成されたか（プラン記述だけでなく） | scaffold-checklist.md / migration-guide-v5.1.0.md / 本ファイルが実体配置済 | PASS |
| 3. smoke test | 本改修の smoke 相当（後述 5 章 Verification 7 件） | grep / ls / git diff の 7 件すべて期待通り | PASS（5 章参照） |
| 4. §7.4 自己検証 | 本ファイル自体が §7.4 相当の自己検証 | 1〜4 章で broken reference / DONT 自己照合相当を実施 | PASS |

判定: **PASS**

---

## 5. Verification 7 件（プラン §Verification 準拠）

すべてのコマンドはリポジトリルート（`/home/user/dialog-harness`）で実行する想定。

| # | コマンド（リポジトリルートで実行） | 期待 | 実態 | 判定 |
|---|---|---|---|---|
| 1 | `ls .claude/skills/layer0-spec-architect/references/scaffold-checklist.md delivery/SELF-VERIFICATION-v5.1.0.md` | 両者存在 | 両者存在 | PASS |
| 2 | `grep -E '受け入れ基準\|§7.4\|Pre-flight' .claude/skills/layer0-spec-architect/SKILL.md` | 複数行 hit | 「L0 完了の受け入れ基準」「§7.4 自己検証」「Pre-flight (v5.1.0)」hit | PASS |
| 3 | `grep 'v5.1.0' .claude/skills/layer0-spec-architect/assets/credit-template.md` | hit | 必須要素テーブル `v5.1.0` hit | PASS |
| 4 | `grep -l 'v5.1.0' history/*.md` | 4 ファイル全て | CHANGELOG / REGIME-LOG / ARCH-DECISIONS / INTENT すべて hit | PASS |
| 5 | `git diff origin/master -- .claude/skills/crosscut-*/ templates/ .claude/skills/layer0-spec-architect/references/philosophy.md dh-upgrades/upgrade-spec-v5.0.0.md` | 出力なし | 出力なし | PASS |
| 6 | `head -16 .claude/skills/layer0-spec-architect/SKILL.md`（frontmatter 妥当性） | name + description 不変 | 不変確認 | PASS |
| 7 | 本 4 章の自己適用検証 | 4 条件 PASS | 4 条件 PASS | PASS |

7 件すべて **PASS**。

---

## 6. 提起事項（次バージョン候補）

### 6.1 v5.2.0 候補: `crosscut-verifier-philosophy` 本実装

placeholder のまま v5.0.0 / v5.1.0 を経過。spec §3 整合性検証ロジックの本実装は次の minor で扱う。本 v5.1.0 では発動禁止のまま。

### 6.2 v5.x 候補: scaffold-checklist の stack 拡張

Next.js / Vue / Astro / SvelteKit / 純 Node CLI を順次追加。stack 選択軸は ARC + dev_mode + チーム軸（v5.x で operational 化）と整合させる。

### 6.3 v5.0.0 検証漏れの補完（本リリースで対処）

`docs/migration-guide-v5.0.0.md` は v5.0.0 のリリース時にローカル生成されたが、`.gitignore` の `docs/` パターンが ディレクトリ ignore のため `!docs/migration-guide-*.md` の例外が効かず、untracked のまま残存していた（v5.0.0 SELF-VERIFICATION の構造的整合性 5.1.1 で「存在 PASS」と判定されたが、実態はローカル file system のみ存在）。

本 v5.1.0 で `.gitignore` を `docs/` → `docs/*` へ変更し、`!docs/migration-guide-*.md` を機能させた。同 commit で `docs/migration-guide-v5.0.0.md` も tracked 化し、v5.0.0 の意図された配布物状態を達成する。AD-007 の意図はそのまま継承。

### 6.4 提起なし（本リリース範囲）

LOW 提起なし。本改修は P0 4 項目に範囲を絞り、shell script 雛形配置・README バッジ作業・stack 拡張は意図的にスコープアウト。
