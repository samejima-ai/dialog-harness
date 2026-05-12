# Dialog Harness Upgrade Specification v5.0.0

**Document Type**: メタスキル自己改修指示書
**Target Reader**: layer0-spec-architect（自己改修主体）+ 改修承認者（ユーザー）
**DH Body Version Transition**: v4.2 → v5.0.0
**Compatibility**: 後方互換破壊あり（major昇格）

---

## 0. 受信エージェントへの指示

### 0.1 本指示書の読み方

本指示書は以下の順序で読解すること：

1. セクション0（本セクション）— 全体方針
2. セクション1 — 改修の目的と成功条件
3. セクション2 — 不変項目（override禁止、最重要）
4. セクション3 — 設計セクション（What & Why）
5. セクション4 — 実装セクション（How、順次実行）
6. セクション5 — 自己検証セクション（実行後の自己献上）
7. セクション6 — 検証手順（人間側）
8. セクション7 — 付録

### 0.2 改修実行の原則

- **不変項目（セクション2）に抵触する改修は即座に中断し、人間に献上すること**
- セクション3（設計）を読んでから、セクション4（実装）を実行すること
- 設計意図を理解せずに実装手順だけ実行することは禁止
- 5 本柱原則と既存履歴層規約への整合性を、各Step実行前に確認すること
- 自己改修が完了したら、セクション5の自己検証を実行し、結果を人間に献上すること

### 0.3 5 本柱との整合性確認義務

各実装Step実行前に、以下を確認する：

| 確認項目 | 内容 |
|---------|------|
| P1 フラクタル | 改修後も全プロジェクトで同一構造を保てるか |
| P2 再帰進化 | 後方互換破壊の場合、移行経路が定義されているか |
| P3 分離 | Skill責務の境界が崩れていないか |
| P4 情報メタボリズム | 履歴層への記録が漏れていないか |
| P5 人間中心 | プロジェクト固有性を尊重した設計か |

整合性違反を検知したら即座に中断、人間に献上する。

### 0.4 履歴層への記録義務

本改修の全変更を以下の履歴層ファイルに記録する：

- `history/CHANGELOG.md` — 全変更項目の追記（レベルA: 自動承認）
- `history/ARCH-DECISIONS.md` — 設計判断の記録（レベルA: 自動承認）
- `history/INTENT.md` — 新規概念（dev_mode、CTL連動仕様等）の追加（レベルB: 確認推奨）
- `history/REGIME-LOG.md` — major昇格の記録（レベルB: 確認推奨）

---

## 1. 改修目的と成功条件

### 1.1 改修の背景

DH v4.2は「対話による開発環境構築」と「自律実装・検証・統括」を確立した。
しかし以下が未確立：

- **GitHub連携を前提とした自律駆動開発の方法論**
- **dev_mode軸（local_only / github_assisted / github_autonomous）の動的判定**
- **Issue射出・実装・検証・還流の4仕様**
- **CTL連動による段階的自動化の体系**
- **Crosscut機構の命名規則統一**

本改修はこれらを v5.0.0 として確立する。

### 1.2 改修の目的

| # | 目的 | 達成手段 |
|---|------|---------|
| 1 | dev_mode軸を3軸目として確立 | 規模軸・チーム軸と並ぶ動的判定軸として組み込み |
| 2 | GitHub連携の方法論化 | 仕様1〜4の Skill 化 |
| 3 | CTL連動の段階的自動化 | 仕様1〜4 すべてに CTL条件を組み込み |
| 4 | Crosscut機構の命名統一 | `council/` → `crosscut-council/` リネーム |
| 5 | 業界BP取り込み | claude-code-action公式採用、GitHub Actions雛形整備 |
| 6 | バージョニング体系の semver化 | v4.2 → v4.2.0 → v5.0.0 |

### 1.3 成功条件

改修完了の判定基準：

- [ ] crosscut- prefix の Skill命名規則が確立し、council が `crosscut-council/` に移行されている
- [ ] dev_mode判定が L0 対話に組み込まれている（規模・チームと同列の3軸目）
- [ ] 仕様1〜4の Skill が `.claude/skills/` 配下に配置されている
- [ ] 仕様1〜4 すべてが CTL連動の条件分岐を持っている
- [ ] GitHub Actions雛形が `templates/.github/workflows/` 配下に配置されている（github_assisted以上で発動）
- [ ] mode別の branch protection / secret / コスト管理ポリシーが文書化されている
- [ ] バージョニングが semver化（v5.0.0 として記録）されている
- [ ] 既存プロジェクト（Lifecycle ≥ 1）への移行ノートが整備されている
- [ ] 自己検証セクション（セクション5）の全項目を PASS している

### 1.4 適用範囲

| 適用 | 対象 |
|------|------|
| **本指示書が改修する対象** | DH本体（配布元リポジトリ） |
| **本指示書が改修しない対象** | 既存プロジェクト内の `.claude/skills/`（プロジェクト独立性保護） |
| **追従可否の判断主体** | 各プロジェクトのオーナー（追従しないことも許容） |
| **既存プロジェクトの把握** | 配布元では把握しない。移行はプロジェクト個別判断に委ねる |

---

## 2. 不変項目（override禁止）

### 2.1 不変項目の宣言

以下の6項目は、本改修においても、また将来の改修においても、override・改変・削除を禁止する。
これらに抵触する改修要求が来た場合、即座に中断し人間に献上すること。

| # | 不変項目 | 理由 |
|---|---------|------|
| 1 | **5 本柱原則** | DHのアイデンティティ |
| 2 | **履歴層規約（A-I 9決定事項）** | データ蓄積の規範 |
| 3 | **献上プロトコル** | DHのアイデンティティ |
| 4 | **Level A skill本体の改変禁止** | DH本体の整合性、参照関係の維持 |
| 5 | **継承禁止項目の指定自体（本セクション）** | メタルール、self-referential保護 |
| 6 | **3層+1横断の構造** | 構造的アイデンティティ |

### 2.2 各不変項目の詳細

#### 2.2.1 5 本柱原則

| 本柱 | 内容 |
|------|------|
| P1 | フラクタル原則 |
| P2 | Shift Left原則（再帰進化を含む） |
| P3 | 情報純度原則（分離） |
| P4 | 人間責務の明確化（情報メタボリズム） |
| P5 | 献上哲学（人間中心） |

第6条「人間 ≒ Council 原則」は v4.2 で追加済み。本改修で第7条以降を追加する場合は major昇格案件として扱うこと。

#### 2.2.2 履歴層規約（A-I 9決定事項）

`history/` ディレクトリの構造、INTENT/CHANGELOG/REGIME-LOG/ARCH-DECISIONS/PATTERNS の役割分担、archive運用、3段階承認（A/B/C）、儀式拒否時の背景照合、これらは v4.2 時点で確立済み。本改修で変更しない。

#### 2.2.3 献上プロトコル

「自走中に人間に質問しない」「仕様不足は即献上」「判断不能時は Council 経由で人間へ」「献上は DELIVERY.md / HANDOFF.md / VERIFICATION.md の規格に従う」これらの原則は本改修で変更しない。

#### 2.2.4 Level A skill本体の改変禁止

`layerN-` および `crosscut-` prefix を持つ Skill 本体（SKILL.md / references/ / assets/）は、プロジェクト側で改変禁止。改変が必要な場合は override.md で対応する。本指示書による DH本体の改修はこの制約の対象外（本体配布元での改修のため）。

#### 2.2.5 継承禁止項目の指定自体

本セクション（セクション2）の存在自体が override禁止。「override禁止項目を指定する規範」が override されると、すべての保護が崩壊する（self-referential保護）。

#### 2.2.6 3層+1横断の構造

```
Layer 0 ──── 対話＆環境構築       (layer0-)
Layer 1 ──── 自律実装＋自律検証   (layer1-)
Layer 2 ──── 自律統括＋統合検証   (layer2-)
Crosscut ──── 横断判定機構         (crosscut-)
```

この構造は本改修で `crosscut-` prefix を新規導入するが、3層+1横断の構造自体は不変。
将来の Layer 追加・削除は major昇格案件として扱うこと。

### 2.3 不変項目違反時の対応

不変項目に抵触する改修要求を検知した場合：

1. 改修を即座に中断
2. `delivery/UPGRADE-CONFLICT.md` に違反内容を記載
3. 人間に献上（Council発動条件を満たす場合は Council へ先に諮る）
4. 人間の判断を待つ
5. 「不変項目を改訂する」判断が下った場合は、major昇格案件として別途指示書を作成

不変項目を「無視」または「自動上書き」することは禁止。常に明示的な献上プロセスを経ること。

---

## 3. 設計セクション（What & Why）

本セクションは Phase 1（DHベース方法論）と Phase 2（GitHub連携モード設計）で確定した設計事項を、実装意図と共に記述する。

実装エージェントは本セクションを読了してから、セクション4の実装手順に進むこと。

### 3.1 Phase 1：DHベース方法論

#### 3.1.1 L0 定義

**確定事項**：3レベル（短／中／長）併用。

##### Level 1（短）：CLAUDE.md冒頭宣言用

> Layer 0 とは、対話を通じてプロジェクトの実行モードを動的に判定し、自律駆動可能な開発環境を射出するメタスキルである。

##### Level 2（中）：仕様書概要用

> Layer 0 は、対話を通じてプロジェクト固有性を抽出し、規模軸（M1/M2/L2）・チーム軸（T1-T5）・開発モード軸（local_only / github_assisted / github_autonomous）の3軸で実行モードを動的に判定するメタスキルである。判定結果に基づき、static層を継承して各プロジェクト固有の自律駆動環境（project層）を射出する。

##### Level 3（長）：本指示書定義用

> Layer 0 は DH（Dialog Harness）の起点であり、対話を通じてプロジェクトの自律駆動開発環境を構築するメタスキルである。L0は規模軸・チーム軸・開発モード軸の3軸で実行モードを動的に判定し、static層（業界BPとDH固有思想を継承する不変ベース）から各プロジェクト固有のproject層を射出する。L0の関与範囲は対話による思想・SPEC・モード決定に限定され、L1以降の実装・検証・判定はCouncilおよび下位エージェントに委譲される。L0完了の判定は、対象プロジェクトが選定されたモードで自律駆動可能な状態に達した時点をもって行う。

##### 設計意図

- L0 は「動的モード判定メタスキル」として定義し直すことで、新規追加される dev_mode軸 を構造的に組み込む
- 既存の規模軸・チーム軸と並列で扱うことで、判定機構の一貫性を保つ
- 「射出する」という能動的表現により、L0 が起点・分岐点であることを明示

#### 3.1.2 ベース層の生成方法

**確定事項**：リモートDH本体から全部取得 → L0対話で取捨選択 → バージョンバッジで追従。

##### フロー

```
[新規プロジェクト立ち上げ]
   ↓
[Step 1: リモートDHから全部取得]
   git clone or template展開
   ↓
[Step 2: L0対話開始]
   3軸判定（規模・チーム・開発モード）
   ↓
[Step 3: 取捨選択フェーズ]
   モード判定結果に応じて不要要素を `.claude/disabled/` へ退避
   ↓
[Step 4: project層生成]
   残った要素を継承、固有override/extendを記述
   ↓
[Step 5: バージョン記録]
   `.claude/VERSION` に DH本体バージョンを記録
   READMEにバッジ生成（DH本体ver / dev_mode / scale）
```

##### 設計意図

- 「全部取得 → 取捨選択」アプローチにより、初期段階で何が利用可能かを対話で確認可能
- 「削除」ではなく「退避」（`.claude/disabled/` へ）— 5 本柱P4（情報メタボリズム）整合
- バッジによりプロジェクトの状態が一目で判別可能

#### 3.1.3 継承モデルの物理仕様

**確定事項**：base/project物理分離は撤回。命名規則による論理的分離。

##### Skill配置

```
.claude/skills/
├─ layer0-spec-architect/         ← Level A
├─ layer0-onboarding/             ← Level A
├─ layer1-autonomous-dev/         ← Level A
├─ layer1-independent-reviewer/   ← Level A
├─ layer2-orchestrator/           ← Level A
├─ layer2-integration-verifier/   ← Level A
├─ crosscut-council/              ← Level A（NEW: 旧 council/）
└─ [project-specific-skills]/     ← Level B（プロジェクト固有）
```

##### Level A / B 識別

| Level | prefix | 性質 |
|-------|--------|------|
| Level A | `layerN-` または `crosscut-` | DH本体由来、不変 |
| Level B | prefix無し | プロジェクト固有、改変可 |

##### `@import` 不採用

- DH本体は `@import` を使わず、相対パス参照（`../../layer0-spec-architect/references/philosophy.md` 形式）で原典を指す
- on-demand loading を最大活用してコンテキスト消費を最小化
- サブスキル深層化のリスクを構造的に回避

##### 設計意図

- 既存DH構造（フラットな skill 配置）を尊重
- 命名規則のみで Level識別、物理分離による複雑化を回避
- CC公式仕様（Progressive Disclosure + on-demand loading）を最大活用

#### 3.1.4 override記法

**確定事項**：(c) Skill別ファイル + (d) CLAUDE.md内 の併用。

##### override場所

| 用途 | 方式 | 場所 |
|------|------|------|
| 特定Skillの動作変更 | (c) override.md | `.claude/skills/[skill-name]/override.md` |
| プロジェクト全体の規範 | (d) CLAUDE.md内 | `project-root/CLAUDE.md` |

##### 優先順位

```
(d) project-root/CLAUDE.md  ← 最強
   >
(c) .claude/skills/[skill-name]/override.md
   >
Level A skill本体          ← 最弱（不変）
```

##### override.md フォーマット

```markdown
# Override for [skill-name]

## 適用対象
[skill-name] のどの部分をoverrideするか

## override内容
（具体的な変更内容）

## 根拠
（なぜoverrideが必要か）

## ADR参照
adrs/AD-XXX.md
```

##### 設計意図

- Level A 不変原則を保ちつつ、プロジェクト固有性を吸収する経路を確保
- ADR記録義務により、override の理由が追跡可能
- 5 本柱P4（情報メタボリズム）整合

#### 3.1.5 アップグレード指示書バージョニング

**確定事項**：semver（vX.Y.Z）採用。

##### 昇格条件

| 区分 | 条件 |
|------|------|
| メジャー（X） | 後方互換破壊を伴う変更 |
| マイナー（Y） | 後方互換を保つ機能追加 |
| パッチ（Z） | バグ修正・誤字訂正 |

##### 昇格判定主体

| 区分 | 判定主体 |
|------|--------|
| メジャー | 人間（献上対象） |
| マイナー | AI自動 |
| パッチ | AI自動 |

##### 既存DHからの移行

- v4.2 → v4.2.0 として読み替え
- 本改修により v5.0.0（major昇格、後方互換破壊あり）

##### 指示書命名

`upgrade-spec-v[X.Y.Z].md`（DH本体verと連動）

### 3.2 Phase 2：GitHub連携モード設計

#### 3.2.1 dev_mode 3段階の境界定義

**確定事項**：local_only / github_assisted / github_autonomous の3段階。

| モード | GitHub | Actions | Issue自動化 | 並列実装 | 人間関与 |
|--------|--------|---------|-----------|--------|--------|
| local_only | × | × | × | × | 全Layer |
| github_assisted | ○ | 任意 | × | 手動 | L0+承認 |
| github_autonomous | ○ | ○ | ○ | 自動 | L0のみ |

##### 設計意図

- 段階的移行を可能にし、各段階で動く状態を維持
- 「GitHub無しでも DHベースは完全動作」の原則を明示
- autonomous の理想形は「人間関与は L0 のみ」

#### 3.2.2 モード判定基準

**確定事項**：2段階判定（GitHub使用の二択 + 他軸からの自動推論）。

##### 判定フロー

```
L0対話開始
  ↓
規模軸判定（M1/M2/L2） + チーム軸判定(T1-T5)
  ↓
質問1：「GitHub使う？」
  ├─ No  → local_only確定
  └─ Yes → 規模・チームから推論
            ├─ M1+T1            → github_assisted
            ├─ M2+T2-T3         → github_assisted
            └─ M2-L2+T3-T5      → github_autonomous
  ↓
推論結果を提示してユーザー確認（1回のみ）
```

##### 設計意図

- 必須質問を1つに絞り、ユーザーの自由対話と整合
- 推論ロジックは規模・チームから決定論的に導出
- 確認1回のみで暴走防止

#### 3.2.3 モード昇格・降格

**確定事項**：手動判定 + ADR記録必須。

##### プロトコル

```
ユーザー「モード変えたい」
  ↓
L0が変更内容を確認
  ↓
ADR記録（変更前後、根拠、影響範囲）
  ↓
モード変更実行（必要なら不要要素を disabled/ へ退避、または復活）
```

##### 設計意図

- override記法と同じ思想（変更はADRに記録）
- 双方向対応（昇格・降格両方）
- 5 本柱P4（情報メタボリズム）整合

#### 3.2.4 仕様1：Issue射出

**確定事項**：CTL連動。

##### モード別動作

```
github_assisted mode:
  明示コマンド「Issueにして」
    ↓
  L1（spec-architect）が SPEC/ADR差分から最大5 Issue生成
    ↓
  ユーザー確認 → GitHub Issue作成

github_autonomous mode + CTL別:
  CTL-0 → ユーザー確認必須（assisted相当）
  CTL-1 → 軽微自動、重要は確認
  CTL-2 → 完全自動 + Council事前検証
  CTL-3 → 完全自動（事前検証も省略可能）
```

##### 暴走防止

- 1コミット最大5 Issue（暫定値、REGIME.md で上書き可能）
- CTL≥2 で Council 事前検証発動
- 異常時は人間に献上

#### 3.2.5 仕様2：Issue→実装

**確定事項**：mode別 + CTL連動。

##### モード別動作

```
github_assisted mode:
  ローカルworktreeでCC手動実行
    ↓
  PR作成 → ユーザーレビュー → Merge

github_autonomous mode + CTL別:
  CTL-0 → ローカルworktree（実質assisted）
  CTL-1 → Actions経由、PR人間レビュー必須
  CTL-2 → Actions経由、self-review pass で auto-merge
  CTL-3 → Actions経由、完全自動

実行手段：claude-code-action（Anthropic公式）を活用
（実装時点で公式リポジトリの最新バージョンを確認すること）
```

#### 3.2.6 仕様3：検証

**確定事項**：CTL連動 + 5層 + drift + 思想検証。

##### 検証構造

```
基本層（既存）：
  Shift Left基盤
  第1層 計算的センサー
  第2層 E2E機械検証
  第3層 Interaction Cost
  第4層 推論的センサー
  第5層 Vision/人間判断

追加層（本改修で新設）：
  drift検知（SPEC/ADR との乖離）
  思想検証（5 本柱整合）※ v5.0.0 では placeholder
```

##### CTL連動

| CTL | 検証構成 |
|-----|--------|
| CTL-0 | 既存5層のみ |
| CTL-1 | + drift検知 |
| CTL-2 | + 思想検証（軽量） |
| CTL-3 | + 思想検証（フル） |

##### コンテキスト管理

- Skill単位の選択実行（必要なSkillのみロード）
- references の遅延ロード
- CTL判定の早期実行

##### 思想検証の本実装時期

v5.0.0 では `crosscut-verifier-philosophy/` を placeholder として配置する。
判定ロジックの本実装は v5.1.0（マイナー昇格）で行う。

#### 3.2.7 仕様4：還流

**確定事項**：mode別 + CTL連動。

##### モード別動作

```
github_assisted mode:
  全て手動還流

github_autonomous mode + CTL別:
  CTL-0 → 手動（assisted相当）
  CTL-1 → drift自動還流、思想は人間確認
  CTL-2 → drift+思想自動還流（Council判定）
  CTL-3 → 完全自動（事後献上のみ）
```

##### 還流先の判定

| 検出 | 還流先 |
|------|------|
| 形式検証FAIL | 実装層（自己修復） |
| drift検知 | 設計層（自動Issue生成） |
| 思想検証FAIL | Council発動 → 設計層 or L0へ |

#### 3.2.8 補論：CTL成熟戦略

**確定事項**：量 + 質 のハイブリッド判定。

##### 昇格条件

| 段階 | 量 | 質 |
|------|-----|-----|
| CTL-0 → CTL-1 | Council判定 50件 | 一致率 80%+ |
| CTL-1 → CTL-2 | 判定 200件 | 一致率 90%+ + override率 < 10% |
| CTL-2 → CTL-3 | 判定 1000件 | 一致率 95%+ + override率 < 3% |

##### 判定主体

- 自動判定（量と質の機械測定）
- 振り返り儀式で必要時のみ議論
- 退行（CTL降格）も儀式で扱う

##### 横断蓄積

CTL育成データは `~/.claude/council-data/` で全プロジェクト横断管理。
2-3プロジェクト目からは初日からCTL-1〜2 でスタート可能。

#### 3.2.9 GitHub Actions雛形

**確定事項**：claude-code-action公式採用 + CTL連動。

##### 配置

```yaml
templates/.github/workflows/
├─ basic-ci.yml          # test + lint + type
├─ e2e-ci.yml            # E2E
├─ interaction-cost.yml  # UX測定
├─ spec-drift.yml        # SPEC drift検知
├─ issue-dispatch.yml    # Issue射出（仕様1）
├─ issue-to-impl.yml     # Issue→実装（仕様2、claude-code-action経由）
├─ drift-feedback.yml    # 還流（仕様4）
├─ auto-merge.yml        # auto-merge（CTL≥2 + CI全通過時のみ）
└─ auto-degrade.yml      # autonomous→assisted自動降格
```

##### 業界BP整合性

| 区分 | 例 |
|------|----|
| 採用可能 | yml構造、Matrix build、claude-code-action、Reusable workflows |
| 調整必要 | auto-merge（CTL連動）、並列度（モード連動）、PR template（DH self-review規約） |
| 採用不可 | Force push、Issue自動削除、AI single review（CTL未成熟時） |

#### 3.2.10 運用品質（branch protection / secret / コスト）

**確定事項**：mode別の使い分け。

##### モード別ポリシー

| モード | branch protection | secret | コスト監視 |
|--------|---------------|--------|---------|
| github_assisted | 業界標準 | GitHub Secrets | usage画面確認 |
| github_autonomous | 業界標準 + drift通過必須 + 思想検証通過必須 | + Council判定権限 | + CTL連動自動ブレーキ |

##### 自動降格メカニズム

`auto-degrade.yml` として独立 yml で実装。発動条件（暫定値）：

| 発動条件 | 動作 |
|---------|------|
| CI連続3回失敗 | autonomous → assisted へ降格、ADR記録 |
| override率 50%超（直近10件） | 同上 |
| API使用量上限到達 | 同上 |

発動条件は運用で調整可能。REGIME.md で上書きできる。

---

## 4. 実装セクション（How）

本セクションは設計セクション（セクション3）で確定した内容を、実装エージェントが順次実行可能な手順として記述する。

各Stepの実行前に、以下を必ず確認すること：
- セクション2（不変項目）に抵触していないか
- 5 本柱整合性（セクション0.3）

各Step完了後、`history/CHANGELOG.md` に実行記録を追記すること。

### 4.1 Step 1：Crosscut機構の命名統一

#### 4.1.1 目的

`council/` を `crosscut-council/` にリネームし、横断機構の命名規則を確立する。

#### 4.1.2 作業内容

##### 4.1.2.1 ディレクトリリネーム

```
.claude/skills/council/  →  .claude/skills/crosscut-council/
```

##### 4.1.2.2 参照パス更新

以下のファイル内の `council/` 参照を `crosscut-council/` に更新：

検索パターン：
- `../../council/` → `../../crosscut-council/`
- `.claude/skills/council/` → `.claude/skills/crosscut-council/`
- `skills/council` → `skills/crosscut-council`

更新対象ファイル（既存DH本体内）：
- `layer0-spec-architect/SKILL.md`
- `layer0-spec-architect/references/philosophy.md`
- `layer1-autonomous-dev/SKILL.md`
- `layer1-autonomous-dev/references/inferential-sensor-v2.md`
- `layer1-independent-reviewer/SKILL.md`
- `layer2-orchestrator/SKILL.md`
- `layer2-orchestrator/references/sub-agent-protocol.md`
- `layer2-integration-verifier/SKILL.md`
- `crosscut-council/SKILL.md`（旧 council/SKILL.md）
- `crosscut-council/references/*.md`

その他、リポジトリ全体で `council/` を検索し発見される全箇所を確認・更新。

##### 4.1.2.3 SKILL.md description の更新

`crosscut-council/SKILL.md` の冒頭 description に「crosscut機構」の説明を追加：

```markdown
---
name: crosscut-council
description: >
  横断判定機構（crosscut prefix）。Layer 0/1/2 のいずれにも属さず、
  全Layerから献上を受けて判定を返す。人間 ≒ Council 原則の実装主体。
  ...（既存内容を維持）
---
```

#### 4.1.3 完了条件

- [ ] `crosscut-council/` ディレクトリ存在
- [ ] `council/` ディレクトリ削除
- [ ] 全参照パス更新完了
- [ ] 旧パス `council/` の残骸なし（コメント等は除く）
- [ ] `crosscut-council/SKILL.md` の description 更新完了
- [ ] `history/CHANGELOG.md` に実行記録

#### 4.1.4 想定される競合

| 競合 | 対応 |
|------|------|
| ブランド表記 `dialog-harness/layer's` への影響 | なし（layer's は外向け表記、crosscut- は内部識別子） |
| 既存プロジェクト内の `council/` 参照 | DH本体改修対象外。プロジェクトごとに移行判断 |

### 4.2 Step 2：dev_mode軸の追加

#### 4.2.1 目的

L0 の動的判定に dev_mode軸（local_only / github_assisted / github_autonomous）を追加する。

#### 4.2.2 作業内容

##### 4.2.2.1 layer0-spec-architect/SKILL.md の更新

L0 の処理フロー（ステップ4「モード判定」）に dev_mode 判定を組み込む：

```markdown
### 4. モード判定

規模・不確実性・リスク・NFR の 4 軸でスコアリングし、L2発動閾値もチェックして開発モードと ARC・権限レベルを決定する。

**v5.0.0 追加**: dev_mode軸（local_only / github_assisted / github_autonomous）を判定する。

判定フロー：
1. 質問1：「GitHub使う？」
2. No → local_only
3. Yes → 規模・チームから推論
   - M1+T1 → github_assisted
   - M2+T2-T3 → github_assisted
   - M2-L2+T3-T5 → github_autonomous
4. 推論結果を1回のみ確認
```

##### 4.2.2.2 references/regime-assessment.md の更新

dev_mode判定プロトコルを追加：

```markdown
## dev_mode 判定（v5.0.0 追加）

### 質問1
「GitHub使う？」

### 判定マトリクス
| 規模 | チーム | dev_mode |
|-----|-------|---------|
| M1 | T1 | github_assisted |
| M2 | T2-T3 | github_assisted |
| M2-L2 | T3-T5 | github_autonomous |
（GitHub使わない場合は全て local_only）

### REGIME.md への記録
dev_mode セクションに判定結果を記録
```

##### 4.2.2.3 REGIME.md テンプレート更新

`assets/meta-spec-template.md` の REGIME.md テンプレートに dev_mode セクションを追加：

```markdown
## dev_mode

- mode: github_assisted   # local_only / github_assisted / github_autonomous
- ctl: 0                  # CTL段階（0-3）
- 判定根拠: GitHub利用、規模M2、チームT2
```

#### 4.2.3 完了条件

- [ ] L0処理フローに dev_mode判定が組み込まれている
- [ ] regime-assessment.md に判定プロトコル記載
- [ ] REGIME.md テンプレートに dev_mode セクション追加
- [ ] `history/CHANGELOG.md` 記録

### 4.3 Step 3：仕様1〜4のSkill追加

#### 4.3.1 目的

GitHub連携の4仕様を Level A skill として追加する。

#### 4.3.2 新規Skill配置

```
.claude/skills/
├─ crosscut-issue-dispatcher/      ← 仕様1：Issue射出
│   ├─ SKILL.md
│   └─ references/
├─ crosscut-issue-implementer/     ← 仕様2：Issue→実装
│   ├─ SKILL.md
│   └─ references/
├─ crosscut-verifier-drift/        ← 仕様3拡張：drift検知
│   ├─ SKILL.md
│   └─ references/
├─ crosscut-verifier-philosophy/   ← 仕様3拡張：思想検証（v5.0.0 placeholder）
│   ├─ SKILL.md
│   └─ references/
└─ crosscut-feedback-loop/         ← 仕様4：還流
    ├─ SKILL.md
    └─ references/
```

##### 命名規則の根拠

仕様1〜4は特定Layerに属さず、全Layerに干渉する横断機能（Council発動・全層への影響）。よって `crosscut-` prefix を採用する。

#### 4.3.3 各SkillのSKILL.md骨子

##### crosscut-issue-dispatcher（仕様1）

```markdown
---
name: crosscut-issue-dispatcher
description: >
  SPEC/ADR差分から GitHub Issue を生成する横断機構。
  github_assisted以上のモードで発動。CTL連動で自動化度が変化。
  「Issueにして」「Issue射出して」「タスク分解して」等でトリガー。
  local_onlyモードでは無効。
---

# Issue Dispatcher

## 発動条件
- REGIME.md の dev_mode が github_assisted 以上
- 明示コマンド or commit hook（CTL連動）

## 処理フロー
1. SPEC/ADR差分を取得
2. CTL確認 → 動作モード決定
3. Issue分解（最大5、REGIME.md で上書き可能）
4. CTL≥2 の場合：crosscut-council 事前検証
5. GitHub Issue 作成
6. CHANGELOG.md 記録

## 関連ドキュメント
- references/dispatch-protocol.md（CTL別動作詳細）
```

##### crosscut-issue-implementer（仕様2）

```markdown
---
name: crosscut-issue-implementer
description: >
  GitHub Issue を起点に CC実装を起動する横断機構。
  ローカルworktree or GitHub Actions経由（claude-code-action）で実行。
  CTL連動で実行手段と並列度が変化。
---

# Issue Implementer

## 発動条件
- Issue assigned or label `ready-for-ai` 付与
- REGIME.md の dev_mode + CTL に応じた実行モード

## 処理フロー
1. Issue内容を読込
2. 実行モード決定（CTL別）
3. 実装実行
   - CTL-0/1: ローカルworktree
   - CTL-2/3: GitHub Actions経由
4. PR作成
5. self-review実行
6. CHANGELOG.md 記録

## claude-code-action 採用注記
本実装は Anthropic公式の claude-code-action を活用する。
実装時点で公式リポジトリの最新バージョンを確認すること。
```

##### crosscut-verifier-drift（仕様3拡張）

```markdown
---
name: crosscut-verifier-drift
description: >
  実装が SPEC/ADR から逸脱していないかを検証する横断機構。
  CTL≥1 で発動。CI上で自動実行。
---

# Drift Verifier

## 発動条件
- PR作成時の CI実行
- REGIME.md の CTL ≥ 1

## 処理フロー
1. PR差分取得
2. SPEC.md/ADR との照合
3. drift検出時の報告
4. crosscut-feedback-loop へ還流要求
```

##### crosscut-verifier-philosophy（仕様3拡張、placeholder）

```markdown
---
name: crosscut-verifier-philosophy
description: >
  実装が 5 本柱原則と整合しているかを検証する横断機構（placeholder）。
  CTL≥2 で発動。判定ロジックは v5.1.0 で実装予定。
  v5.0.0 では skill配置のみ、実体は未実装。
---

# Philosophy Verifier (Placeholder)

## v5.0.0 ステータス
- skill配置のみ
- 判定ロジック未実装
- v5.1.0 で本実装予定

## 将来仕様（v5.1.0）
1. PR内容を 5 本柱原則と照合
2. 違反検出時の Council発動
```

##### crosscut-feedback-loop（仕様4）

```markdown
---
name: crosscut-feedback-loop
description: >
  検証層で発覚した問題を設計層・実装層・L0 へ還流する横断機構。
  drift・思想違反・形式FAIL の種別ごとに還流先を判定。
  CTL連動で自動化度が変化。
---

# Feedback Loop

## 発動条件
- 検証層からの還流要求
- REGIME.md の dev_mode + CTL

## 処理フロー
1. 検出種別を確認
2. 還流先を決定
   - 形式FAIL → 実装層（自己修復）
   - drift → 設計層（自動Issue生成）
   - 思想FAIL → Council発動 → 設計層 or L0
3. 還流先へ通知
4. CHANGELOG.md 記録
```

#### 4.3.4 完了条件

- [ ] 5つの crosscut- skill が `.claude/skills/` に配置
- [ ] 各SKILL.md の description 設定済み
- [ ] crosscut-verifier-philosophy は placeholder状態（中身は v5.1.0）
- [ ] 既存 layer1-autonomous-dev / layer1-independent-reviewer から新skillへの参照追加
- [ ] `history/CHANGELOG.md` 記録

### 4.4 Step 4：CTL連動の組み込み

#### 4.4.1 目的

仕様1〜4 すべてに CTL条件分岐を組み込む。

#### 4.4.2 作業内容

##### 4.4.2.1 各 crosscut-* skill 内の CTL分岐実装

各 skill の references/ に CTL別動作プロトコルを記述：

```
crosscut-issue-dispatcher/references/dispatch-protocol.md
crosscut-issue-implementer/references/implement-protocol.md
crosscut-verifier-drift/references/verify-protocol.md
crosscut-feedback-loop/references/feedback-protocol.md
```

各プロトコル内のCTL分岐表は、設計セクション 3.2.4〜3.2.7 の内容をコピー。

##### 4.4.2.2 CTL育成戦略の明文化

実装エージェントは既存の `crosscut-council/references/ctl-calculation.md` を確認した上で、以下を判断する：

- 既存 ctl-calculation.md に CTL育成戦略の記載がある場合 → 追記
- 既存に記載がない場合 → 新規 `ctl-maturity-strategy.md` として作成

新規作成時の内容：

```markdown
# CTL Maturity Strategy

## 昇格条件
| 段階 | 量 | 質 |
|------|-----|-----|
| CTL-0 → CTL-1 | Council判定 50件 | 一致率 80%+ |
| CTL-1 → CTL-2 | 判定 200件 | 一致率 90%+ + override率 < 10% |
| CTL-2 → CTL-3 | 判定 1000件 | 一致率 95%+ + override率 < 3% |

## 判定主体
- 自動判定（量・質の機械測定）
- 振り返り儀式で必要時のみ議論

## 横断蓄積
~/.claude/council-data/ で全プロジェクト横断管理

## 退行
override率悪化時は儀式で議論、CTL降格を判断
```

#### 4.4.3 完了条件

- [ ] 4つの protocol.md（仕様1〜2、3-drift、4） 配置完了
- [ ] CTL育成戦略の文書化完了（既存追記 or 新規作成）
- [ ] `history/CHANGELOG.md` 記録

### 4.5 Step 5：GitHub Actions雛形配置

#### 4.5.1 目的

仕様1〜4を実装するための GitHub Actions yml ファイル群を雛形として配置する。

#### 4.5.2 配置場所

実装エージェントは既存DH配布構造を確認し、判断する：

- `templates/` ディレクトリが既存 → そこに配置
- 既存しない → 新規追加（配置規則 dev-env-spec.md にも追記）

```
templates/.github/workflows/
├─ basic-ci.yml
├─ e2e-ci.yml
├─ interaction-cost.yml
├─ spec-drift.yml
├─ issue-dispatch.yml
├─ issue-to-impl.yml
├─ drift-feedback.yml
├─ auto-merge.yml
└─ auto-degrade.yml
```

#### 4.5.3 各 yml の骨子

##### basic-ci.yml

```yaml
name: Basic CI
on: [pull_request]
jobs:
  test-lint-type:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install
      - run: npm test
      - run: npm run lint
      - run: npm run typecheck
```

##### issue-to-impl.yml（claude-code-action公式採用）

```yaml
# Required: claude-code-action の最新バージョンを公式リポジトリで確認すること
name: Issue to Implementation
on:
  issues:
    types: [labeled]
jobs:
  implement:
    if: github.event.label.name == 'ready-for-ai'
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@<latest>
        with:
          api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          issue-number: ${{ github.event.issue.number }}
```

##### auto-merge.yml（CTL≥2 + CI全通過）

```yaml
name: Auto Merge
on:
  pull_request_review:
    types: [submitted]
jobs:
  auto-merge:
    if: |
      contains(github.event.pull_request.labels.*.name, 'ctl-2-or-higher') &&
      github.event.review.state == 'approved'
    runs-on: ubuntu-latest
    steps:
      - run: gh pr merge --auto --squash ${{ github.event.pull_request.number }}
```

##### auto-degrade.yml（自動降格）

```yaml
name: Auto Degrade autonomous → assisted
on:
  workflow_run:
    workflows: ["Basic CI"]
    types: [completed]
jobs:
  check-and-degrade:
    if: github.event.workflow_run.conclusion == 'failure'
    runs-on: ubuntu-latest
    steps:
      - name: Check consecutive failures
        run: |
          # 直近3回連続失敗をチェック
          # 該当時は REGIME.md の dev_mode を assisted に変更
          # ADR記録を作成
          # 詳細実装は本Step実行時に決定
```

#### 4.5.4 mode別の発動制御

各 yml 冒頭にコメントで発動条件を明記：

```yaml
# Required mode: github_assisted or higher
# Required CTL: 0+ (basic CI), 2+ (auto-merge)
```

実装はワークフロー内の `if` 条件で制御。

#### 4.5.5 完了条件

- [ ] 9つの yml ファイルが templates/.github/workflows/ に配置
- [ ] 各 yml の発動条件コメント記載
- [ ] auto-degrade.yml の発動条件文書化
- [ ] templates/ 配置規則の dev-env-spec.md への追記（新規追加の場合）
- [ ] `history/CHANGELOG.md` 記録

### 4.6 Step 6：バージョン更新

#### 4.6.1 目的

DH本体を v4.2 → v5.0.0 に更新し、major昇格を記録する。

#### 4.6.2 作業内容

##### 4.6.2.1 バージョン記録

`assets/credit-template.md` の表記を v5.0.0 に更新。

##### 4.6.2.2 SKILL.md バージョン履歴追加

`layer0-spec-architect/SKILL.md` のバージョン履歴セクションに追記：

```markdown
- v5.0.0: dev_mode軸追加 + crosscut-リネーム + 仕様1〜4 Skill化 + CTL連動仕様 + GitHub Actions雛形 + 業界BP取り込み（claude-code-action公式採用）+ 運用品質ポリシー（mode別 業界標準/DH強化）
```

##### 4.6.2.3 後方互換破壊の記録

`history/REGIME-LOG.md` に major昇格の記録：

```markdown
## v5.0.0 メジャー昇格（後方互換破壊）

### 破壊項目
- council/ → crosscut-council/ リネーム（参照パス全更新）

### 移行方針
- DH本体配布元のみ自動移行
- 既存プロジェクトは手動移行（プロジェクトオーナーの判断）

### 移行手順（既存プロジェクト向け）
1. .claude/skills/council/ を .claude/skills/crosscut-council/ にリネーム
2. プロジェクト内の council/ 参照を全て crosscut-council/ に更新
3. ADR記録（移行日・実行内容）
```

##### 4.6.2.4 README バッジ更新

DH本体配布元 README に v5.0.0 バッジを追加：

```markdown
[![DH](https://img.shields.io/badge/Dialog_Harness-v5.0.0-blue)](...)
```

#### 4.6.3 完了条件

- [ ] credit-template.md 更新
- [ ] SKILL.md バージョン履歴追記
- [ ] history/REGIME-LOG.md に major昇格記録
- [ ] README バッジ更新
- [ ] `history/CHANGELOG.md` 最終記録

### 4.7 実装Step実行順序

```
Step 1（crosscut-リネーム）
   ↓
Step 2（dev_mode軸追加）
   ↓
Step 3（仕様1〜4 Skill追加）
   ↓
Step 4（CTL連動組み込み）
   ↓
Step 5（GitHub Actions雛形）
   ↓
Step 6（バージョン更新）
```

各Stepは前のStepの完了を前提とする。並列実行不可。
各Step完了時に `history/CHANGELOG.md` に記録すること。

---

## 5. 自己検証セクション

実装エージェントは Step 1〜6 の全実装完了後、本セクションの全項目を実行する。
全項目PASSで「自己検証完了」とし、結果を人間に献上すること。

各項目FAILの場合、修復可能なら自己修復を試み、不可能なら人間に献上する。

検証はCC のファイル操作（view/grep等）で実行可能。シェル実行は補助手段として利用可。

### 5.1 構造的整合性チェック

#### 5.1.1 ディレクトリ構造の検証

期待される配置：

- `.claude/skills/crosscut-council/` 存在
- `.claude/skills/council/` 削除済み
- `.claude/skills/crosscut-issue-dispatcher/` 存在
- `.claude/skills/crosscut-issue-implementer/` 存在
- `.claude/skills/crosscut-verifier-drift/` 存在
- `.claude/skills/crosscut-verifier-philosophy/` 存在
- `.claude/skills/crosscut-feedback-loop/` 存在
- `templates/.github/workflows/` 存在

#### 5.1.2 参照パス整合性

旧 `council/` 参照の残骸チェック：

- `skills/council/` の grep 結果が空（コメント等の歴史記述は許容）
- `../../council/` の grep 結果が空

#### 5.1.3 SKILL.md の存在と最低要件

各 crosscut- skill の SKILL.md について：
- frontmatter（`name`, `description`）が存在
- description に発動条件が明記されている
- description に CTL連動の言及がある（仕様1〜4 のみ）

#### 5.1.4 GitHub Actions yml の構文検証

- yml構文に明らかなエラーがない
- 各yml の冒頭に発動条件コメントが記載

### 5.2 5 本柱整合チェック

#### 5.2.1 P1（フラクタル原則）

- [ ] 全プロジェクトで Skill構造が同一形状を保てるか
- [ ] 仕様1〜4 が CTL連動で同型構造を持っているか
- [ ] crosscut- prefix の追加で 3層+1横断 構造が維持されているか

#### 5.2.2 P2（Shift Left / 再帰進化）

- [ ] dev_mode の段階的移行経路が定義されているか（local_only → assisted → autonomous）
- [ ] CTL の段階的成熟経路が定義されているか
- [ ] 後方互換破壊（crosscut-リネーム）の移行手順が文書化されているか

#### 5.2.3 P3（情報純度 / 分離）

- [ ] crosscut機構と layer機構の責務分離が明確か
- [ ] override禁止項目（Level A本体）が保護されているか
- [ ] mode別の動作差分が明示されているか

#### 5.2.4 P4(人間責務 / 情報メタボリズム）

- [ ] 全変更が history/CHANGELOG.md に記録されているか
- [ ] major昇格が history/REGIME-LOG.md に記録されているか
- [ ] override は ADR記録必須として方法論化されているか
- [ ] 退避領域（disabled/）が「削除しない」原則を実装しているか

#### 5.2.5 P5（献上哲学 / 人間中心）

- [ ] L0 関与のみで autonomous が成立する設計になっているか
- [ ] 不変項目違反時の即献上プロトコルが組み込まれているか
- [ ] CTL未成熟段階で人間ガードが残されているか

#### 5.2.6 第6条（人間 ≒ Council 原則）

- [ ] crosscut-council の役割が「人間と同格・代替可能」として記述されているか
- [ ] CTL育成戦略が「人間からCouncilへの段階的委譲」として設計されているか

### 5.3 後方互換性チェック

#### 5.3.1 既存プロジェクトへの影響評価

- [ ] DH本体配布元のみ自動移行する設計になっているか
- [ ] 既存プロジェクト（v4.2 ベース）の移行手順が文書化されているか
- [ ] 移行を選択しないプロジェクトの動作保証はどうなっているか

#### 5.3.2 後方互換破壊項目の明示

major昇格に該当する破壊項目：
- [ ] `council/` → `crosscut-council/` リネーム

これ以外に意図しない後方互換破壊が混入していないか確認：
- 既存 SKILL.md の description 改変
- 既存 references の削除
- 既存 yml の改変（v5.0.0 では新規追加のみ）

#### 5.3.3 既存ドキュメント整合性

- [ ] philosophy.md の変更がないこと（不変項目）
- [ ] dev-env-spec.md への追記が「拡張」であって「改変」でないこと
- [ ] regime-assessment.md への追記が既存判定ロジックを破壊していないこと

### 5.4 既存プロジェクトへの影響確認

#### 5.4.1 既存プロジェクトの把握方針

DH本体配布元では既存プロジェクトを把握しない。
移行はプロジェクト個別判断に委ねる方針を確定する。

#### 5.4.2 移行ガイド文書の整備

`docs/migration-guide-v5.0.0.md` を新規作成：

```markdown
# Migration Guide: v4.2 → v5.0.0

## 破壊的変更
- council/ → crosscut-council/ リネーム

## 移行手順
1. DH本体を最新化
2. プロジェクト内のリネーム実行
3. 参照パス更新
4. ADR記録

## 任意機能（v5.0.0 で追加）
- dev_mode 軸の利用（GitHub連携自律駆動）
- 仕様1〜4 の活用
- CTL育成
（任意機能は採用しなくても v5.0.0 互換）
```

- [ ] migration-guide-v5.0.0.md 作成完了
- [ ] DH本体 README からリンク

### 5.5 自己検証完了報告

全項目PASS時、`delivery/SELF-VERIFICATION-v5.0.0.md` を作成：

```markdown
# Self Verification: DH v5.0.0 Upgrade

## 検証日時
[ISO 8601]

## 検証結果
- 5.1 構造的整合性: PASS / FAIL
- 5.2 5 本柱整合: PASS / FAIL
- 5.3 後方互換性: PASS / FAIL
- 5.4 既存プロジェクト影響: PASS / FAIL

## FAIL項目（あれば）
- [項目]: [理由] / [自己修復可否]

## 献上推奨
- [人間判断が必要な項目があれば記載]
```

FAIL があれば人間に献上、PASSなら次のセクション6へ進む。

---

## 6. 検証手順（人間側）

実装エージェントの自己検証完了後、改修承認者（ユーザー）が最終確認するための手順。

### 6.1 受領確認

実装エージェントから以下が献上されていることを確認：

- [ ] `delivery/SELF-VERIFICATION-v5.0.0.md`（自己検証結果）
- [ ] `history/CHANGELOG.md` の更新差分
- [ ] `history/REGIME-LOG.md` の major昇格記録
- [ ] `docs/migration-guide-v5.0.0.md`

### 6.2 哲学的整合性の最終判断

ユーザーが以下を最終判断する：

- [ ] dev_mode軸の追加が DHの思想と整合しているか
- [ ] crosscut- prefix の導入が 3層+1横断構造を強化しているか
- [ ] 仕様1〜4 の同型構造が 5 本柱P1（フラクタル）を発現しているか
- [ ] CTL連動が 5 本柱P2（再帰進化）を発現しているか

### 6.3 動作確認

#### 6.3.1 サンプルプロジェクトでの試運転

新規プロジェクト（サンプル用リポジトリ）でのL0対話実行：

1. リモートDH v5.0.0 から clone
2. L0対話開始（質問1：GitHub使う？）
3. dev_mode判定が正常動作するか
4. 取捨選択フェーズが正常動作するか

#### 6.3.2 既存プロジェクトでの移行試運転

既存プロジェクト1件での移行手順試行：

1. migration-guide に従って手動移行
2. council/ → crosscut-council/ リネーム実行
3. 参照パス更新
4. 既存機能が正常動作するか

### 6.4 承認判断

| 結果 | アクション |
|------|---------|
| 全PASS | v5.0.0 リリース承認、配布元 main へ merge |
| 一部FAIL（軽微） | 修正依頼、再献上待ち |
| 重大FAIL | 改修中断、Council発動 |

---

## 7. 付録

### 7.1 決定事項ログ（対話履歴サマリ）

本指示書の各設計判断は、以下の対話セッションで確定した：

#### Phase 1：DHベース方法論

| 論点 | 確定値 | 確定根拠 |
|------|-------|---------|
| L0定義 | 3レベル併用 | 「動的モード判定メタスキル」として再定義 |
| ベース層生成 | 全部取得→取捨選択→バッジ | プロジェクト独立性確保 |
| 継承モデル | 命名規則による論理的分離（base/project物理分離撤回） | 既存DH構造との整合 |
| override記法 | (c) override.md + (d) CLAUDE.md併用 | Level A不変原則 |
| バージョニング | semver（vX.Y.Z）+ AI判定+人間承認 | 業界BP整合 |

#### Phase 2：GitHub連携モード設計

| 論点 | 確定値 | 確定根拠 |
|------|-------|---------|
| dev_mode 3段階 | local_only / github_assisted / github_autonomous | 段階的移行 |
| モード判定 | 2段階判定（GitHub二択+他軸推論） | ユーザーの自由対話と整合 |
| モード昇格・降格 | 手動 + ADR必須 | override記法と同型 |
| 仕様1（Issue射出） | CTL連動 | autonomous理想実現 |
| 仕様2（Issue→実装） | mode別+CTL連動 | claude-code-action活用 |
| 仕様3（検証） | CTL連動+5層+drift+思想 | 既存5層+業界BP+DH独自 |
| 仕様4（還流） | mode別+CTL連動 | 仕様1〜3 と同型 |
| CTL成熟戦略 | 量+質ハイブリッド | 振り返り儀式で扱う |
| GitHub Actions雛形 | claude-code-action公式採用+CTL連動 | 業界BP取り込み |
| 運用品質 | mode別（業界標準/DH強化） | 思想と業界BPの統合 |

### 7.2 不変項目の参照原典

本指示書の不変項目（セクション2）の参照先：

- 5 本柱原則 → `.claude/skills/layer0-spec-architect/references/philosophy.md`
- 履歴層規約 → `.claude/skills/layer0-spec-architect/references/history-layer-spec.md`
- 献上プロトコル → `.claude/skills/layer1-autonomous-dev/references/delivery-format.md`
- 3層+1横断構造 → 本指示書セクション 2.2.6

### 7.3 用語集

| 用語 | 定義 |
|------|------|
| L0 / Layer 0 | 対話＆環境構築層 |
| L1 / Layer 1 | 自律実装＋自律検証層 |
| L2 / Layer 2 | 自律統括＋統合検証層 |
| Crosscut | 全Layer横断の機構 |
| Level A | DH本体由来の不変Skill（layerN- / crosscut- prefix） |
| Level B | プロジェクト固有Skill（prefix無し） |
| dev_mode | 開発モード判定軸（local_only / github_assisted / github_autonomous） |
| CTL | Council Trust Level（0-3） |
| 献上 | エージェントが完成物または問題を判定主体に提示する行為 |
| 認識合わせ | 主観の擦り合わせ（合意とは異なる） |
| 合意 | 判定結果の受領と方針化 |

### 7.4 関連ドキュメント

#### DH本体内
- `.claude/skills/layer0-spec-architect/SKILL.md`
- `.claude/skills/layer0-spec-architect/references/philosophy.md`
- `.claude/skills/layer0-spec-architect/references/dev-env-spec.md`
- `.claude/skills/layer0-spec-architect/references/regime-assessment.md`
- `.claude/skills/crosscut-council/SKILL.md`（旧 council/）
- `.claude/skills/crosscut-council/references/ctl-calculation.md`

#### v5.0.0 で新規追加
- `.claude/skills/crosscut-issue-dispatcher/SKILL.md`
- `.claude/skills/crosscut-issue-implementer/SKILL.md`
- `.claude/skills/crosscut-verifier-drift/SKILL.md`
- `.claude/skills/crosscut-verifier-philosophy/SKILL.md`（placeholder）
- `.claude/skills/crosscut-feedback-loop/SKILL.md`
- `.claude/skills/crosscut-council/references/ctl-maturity-strategy.md`（既存追記または新規）
- `templates/.github/workflows/*.yml`
- `docs/migration-guide-v5.0.0.md`

### 7.5 改修後の DH ロードマップ（現時点の構想）

以下は現時点の構想であり、確定事項ではない。実際の進捗で変更され得る。

| バージョン | 内容 |
|----------|------|
| v5.1.0（マイナー） | crosscut-verifier-philosophy 本実装（思想検証ロジック） |
| v5.2.0（マイナー） | M0モード追加（M1未満の軽量タスク用） |
| v5.3.0（マイナー） | Platform層自動生成機能 |
| v6.0.0（メジャー） | 次の major 改修（未定） |

### 7.6 本指示書のバージョン

- 文書バージョン: v5.0.0
- 作成日: 対話完了時点
- 作成者: layer0-spec-architect（メタスキル）+ 改修承認者（ユーザー）
- 対象DH本体バージョン: v4.2 → v5.0.0

---

**End of Upgrade Specification v5.0.0**
