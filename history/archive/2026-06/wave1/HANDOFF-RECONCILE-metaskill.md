# HANDOFF Section 9 齟齬解消ノート — メタスキル開発案件

**生成日時**: 2026-05-11 JST
**起点 HANDOFF**: `5fd827fa-HANDOFFDHmetaskillindustryabsorption.md`（2026-05-11 09:50 JST 生成）
**目的**: HANDOFF Section 9「ファイル齟齬」前提が DH 実態と乖離しているため、概念ラベル翻訳表と参照パス確定表を作成し、後続 Phase で参照する一次情報を確立する

---

## 1. HANDOFF が想定したファイル群 vs DH 実態の突合

| HANDOFF 想定 | 想定所在 | DH 実態 | 一致性 | 影響度 |
|---|---|---|---|---|
| `philosophy.md` | root 配下推定 | `harness-verifier/PHILOSOPHY.md`（D4 検査機構の存在論版）+ `.claude/skills/layer0-spec-architect/references/philosophy.md`（起点参考版）の **二層実装** | ⚠ 部分一致 | 中（議題2 で 2 ファイル同時更新必須化） |
| `SPEC.md` | root 配下推定 | **不在**（DH は skill 分散モデル、root 統合 SPEC は採用せず） | ✗ 不在 | 低（設計選択） |
| `DOMAINS.md` | root 配下推定 | **不在**（skill 分散） | ✗ 不在 | 低 |
| `REGIME.md` | root 配下推定 | **不在**（利用者プロジェクトの root に置かれる構造で、DH 本体は持たない） | ✗ 不在 | 低 |
| `SKILL.md` | root 配下推定 | 各 skill 配下に 16 個（16 skill × SKILL.md = 16 ファイル） | ◐ 分散配置 | 低（DH 設計通り） |
| `DELIVERY.md` | root 配下推定 | **不在**（`delivery/` ディレクトリで個別献上、統合 DELIVERY.md は採用せず） | ✗ 不在 | 低 |
| `CLAUDE.md` | root 配下推定 | **不在**（利用者プロジェクト用、DH 本体は持たない） | ✗ 不在 | 低 |
| `AGENTS.md` | root 配下推定 | **不在** | ✗ 不在 | 低 |
| `scaffold-checklist.md` | skill 配下推定 | `.claude/skills/layer0-spec-architect/references/scaffold-checklist.md` | ✓ 一致 | 低 |
| `permission-delegation.md` | skill 配下推定 | `.claude/skills/layer0-spec-architect/references/permission-delegation.md` | ✓ 一致 | 低 |
| L0 サブフェーズ独立定義 | `references/subphase-*.md` 独立ファイル想定 | ✓ **完全実装済**（v5.2.0 以降） | ✓ 一致 | 高（タスク B の自然な投入箇所） |
| └ L0-2 Domain | — | `.claude/skills/layer0-spec-architect/references/subphase-l02-domain.md` | ✓ | |
| └ L0-3 API | — | `.../references/subphase-l03-api.md` | ✓ | |
| └ L0-4 Transition | — | `.../references/subphase-l04-transition.md` | ✓ | |
| └ L0-5 Authz | — | `.../references/subphase-l05-authz.md` | ✓ | |
| └ L0-6 Invariants | — | `.../references/subphase-l06-invariants.md` | ✓ | |
| └ 共通プロトコル | — | `.../references/subphase-common-protocol.md` | ✓ | |

**結論**: HANDOFF Section 9 の「ファイル齟齬」は実は ほぼ 存在せず、HANDOFF が DH の **設計選択（skill 分散モデル）** を理解していなかったか、もしくは旧版概念モデルを引きずっていた。タスク B の前提（L0 サブフェーズ独立定義の追加）は **既に完成済の上に拡張節を足すだけ** で実装可能。

---

## 2. 概念ラベル翻訳表（HANDOFF → DH 用語）

HANDOFF が独自に導入した概念ラベルと DH 実態の対応:

| HANDOFF 用語 | DH 内出現数 | DH 対応概念 | 翻訳方針 |
|---|---|---|---|
| **CaaF**（Conversation as a Framework） | **0 件** | `dialog-questions.md` + subphase Phase α（対話フェーズ） | 議題 2 で「新規用語として導入する」or「既存 dialog-questions 概念に統合する」を Council 判定 |
| **CDD**（Conversation-Driven Development） | **0 件** | subphase-common-protocol.md の α → β → γ → δ 4 フェーズ骨格 | 同上 |
| **対話構造** | 多数 | subphase Phase α + dialog-questions.md カテゴリ | 既存実装を一次情報源として保持 |
| **フラクタル原則 P1** | philosophy.md 第 1 条 | 規律の自己相似性（L0⇄人間 / L1 内部 / L2⇄L1 群 / D4 自己検査） | DH 実装が先行、ラベルは一致 |
| **献上 Type A/B/C** | Type D 含む A/B/C/D 4 型 | `layer1-autonomous-dev/SKILL.md §8 献上` 表形式定義 | HANDOFF が古い、A/B/C/D で扱う |
| **5 次元論 D1-D5** | `history/DIMENSIONS.md` で完全定義 | D1=コード / D2=開発環境 / D3=配布 skill / D4=メタ skill / D5=人間 | HANDOFF と DH 同形、一致 |
| **3 層戦略 layer1-3** | HANDOFF Section 3-4 で言及 | DH 内の 3 層実装は未着手 | タスク A/B/C で本案件が初実装 |

---

## 3. 確定参照パス表（後続 Phase で参照する正式パス）

タスク A〜D で更新対象となる DH ファイルの確定パス:

### 議題 2（philosophy 追記）採決後 — タスク D

- `/home/user/dialog-harness/harness-verifier/PHILOSOPHY.md` — D4 メタスキル層の存在論として独占 4 軸を規範化
- `/home/user/dialog-harness/.claude/skills/layer0-spec-architect/references/philosophy.md` — 業界実装吸収方針 + 業界 5 パターン位置付け + 対話/フラクタル/献上/5次元の独占性

### タスク B（L0 サブフェーズ拡張）

- `/home/user/dialog-harness/.claude/skills/layer0-spec-architect/references/subphase-l03-api.md` — 「ECC agents 定義パターン参照モード」節追加
- `/home/user/dialog-harness/.claude/skills/layer0-spec-architect/references/subphase-l04-transition.md` — 「ECC hooks イベントトリガ参照モード」節追加
- `/home/user/dialog-harness/.claude/skills/layer0-spec-architect/references/subphase-l05-authz.md` — 「AgentShield 脆弱性パターン参照モード」節追加
- `/home/user/dialog-harness/.claude/skills/layer0-spec-architect/references/subphase-l06-invariants.md` — 「ECC Instincts 学習対象参照モード」節追加
- `/home/user/dialog-harness/.claude/skills/layer0-spec-architect/references/subphase-common-protocol.md` — Phase γ（検証）に「ECC 参照カタログ照合」観測駆動フック追加

### タスク C（ECC 互換出力仕様）

- `/home/user/dialog-harness/.claude/skills/layer0-spec-architect/references/scaffold-checklist.md` — ECC 互換配置規約節を追加

### 履歴層更新（v5.12.0 minor 候補）

- `/home/user/dialog-harness/history/CHANGELOG.md`
- `/home/user/dialog-harness/history/REGIME-LOG.md`
- `/home/user/dialog-harness/history/ARCH-DECISIONS.md`（AD-XXX 新設）
- `/home/user/dialog-harness/history/INTENT.md`

### タスク A（参照カタログ）— Council 議題 1 採決後

- 出力先 5 候補のうち Council が選択した path 配下に以下 5 ファイル:
  - `agents-catalog.md`
  - `skills-pattern.md`
  - `hooks-trigger-points.md`
  - `agentshield-spec.md`
  - `instincts-design.md`

---

## 4. 後続セッションでの参照規約

本ノートを起点として、Phase 1 以降のセッションは:

1. **HANDOFF Section 9 の「ファイル齟齬」記述を直接信用せず**、本ノートの「確定参照パス表」を一次参照とする
2. **CaaF/CDD 用語**は議題 2 採決前は使用しない。代替として「subphase Phase α 対話」「dialog-questions 構造」を使う
3. **A/B/C/D 4 型献上**を前提に判断する（HANDOFF の A/B/C 3 型記述は古い）
4. **5 次元論**は `history/DIMENSIONS.md` を一次情報源とする

---

## 5. 不明点（Council 上程対象）

- **議題 1**: ECC 参照カタログ 5 ファイルの出力先ディレクトリ（草稿 5 候補を `COUNCIL-AGENDA-metaskill-2026-05-11.md` に列挙）
- **議題 2**: philosophy.md 追記内容（独占 4 軸の文言、CaaF/CDD 新規導入の是非、業界 5 パターン位置付け文言）

両議題が Phase 1 着手の前提条件。
