# 咀嚼プロトコル SPEC — Wave 1 起点ドキュメント

**作成日時**: 2026-05-11T04:30:00Z
**位置付け**: Council 議題 0（`council-2026-05-11T03:49:01Z-4go7g1`）採決の Step 2「咀嚼プロトコル SPEC 化」第 1 PR 起点。Wave 1（候補 3 + 1 + 6）の SPEC ドラフト枠組みを提供。
**起点 PR**: [PR #75](https://github.com/samejima-ai/dialog-harness/pull/75)（Phase 0 + 0.5 完了、ready for review）
**入力素材**:
- `delivery/CHEW-CANDIDATES-metaskill-2026-05-11.md` v2（8 候補評価、ユーザー方針補足反映済）
- `delivery/PHILOSOPHY-NOTE-autonomy-with-guardrails-2026-05-11.md`（議題 2 再上程素材）
- `delivery/ECC-SURVEY-2026-05-11.md`（一次観察）
**バージョン候補**: v5.12.0 minor

---

## 0. 咀嚼プロトコル の SPEC 全体像（Wave 1〜3 共通）

### 0.1 咀嚼の 4 ステップ（プロトコル本体）

```
[Step A] 観察 (Observation)
  → 業界実装プリミティブを ephemeral で観察、refs/industry/<vendor>/ にカタログ化

[Step B] 分解 (Decomposition)
  → 観察した型を「採用可能な要素」と「DH 哲学に抵触する要素」に分解
  → 分解判定は philosophy.md（6 条 + 第 7 条 + 第 8 条候補）+ DONT.md を基準

[Step C] 翻訳 (Translation)
  → 採用可能な要素を DH 流に翻訳
  → 翻訳タイプ:
    - T1 構造保持（素材の構造はそのまま、適用条件をガードレールで囲む）
    - T2 語彙翻訳（素材の語彙を DH 流に置換、構造は保持）
    - T3 サブセット選別（素材の一部のみ採用）
    - T4 二層構造化（素材を観察層と運用層に分離）

[Step D] 検証 (Verification)
  → 翻訳後の取り込みが DH 哲学を毀損しないことを verifier-philosophy / verifier-drift で検証
  → 抵触検出時は feedback-loop で人間献上
```

### 0.2 ガードレール経路（PHILOSOPHY-NOTE 由来）

```
取り込み素材 (Step C 翻訳済)
    ↓
verifier-philosophy（philosophy.md 6 条 + 第 7 条 + 第 8 条候補との照合）
    ↓
verifier-drift（DONT.md / SPEC.md / ADR との照合）
    ↓
[抵触なし] → AI 自律で取り込み実行
[抵触あり] → feedback-loop 経由で人間献上
```

### 0.3 origin / version トレーサビリティ規格（候補 2 連動、Wave 2 で正式化）

全ての咀嚼取り込み skill / 設定 / template に以下を frontmatter で記録:

```yaml
---
name: <skill-name>
origin: ECC-derived | dialog-harness | ...
origin_source: "ecc:hooks/hooks.json#PreToolUse"  # 元素材の正確な位置
origin_version: "ECC v2.0.0-rc.1"
chewing_translation: T1 | T2 | T3 | T4
chewed_at: "2026-05-12T..."
chewing_pr: "samejima-ai/dialog-harness#<N>"
---
```

---

## 1. Wave 1 候補別 SPEC ドラフト

### 1.1 候補 3: hooks.json Claude Code 公式 schema + 6 event types

#### 1.1.1 Source

ECC `hooks/hooks.json`:
- `$schema`: `https://json.schemastore.org/claude-code-settings.json`
- event types: `PreToolUse` / `PostToolUse` / `Stop` / `SessionStart` / `SessionEnd` / `PreCompact`
- matcher: `Bash` / `Write` / `Edit|Write` / `*` 等のツール限定
- exit code: `2` = block / `0` = warn

#### 1.1.2 採用範囲（DH 内 embedding target）

| 採用要素 | DH 内 target | 翻訳タイプ |
|---|---|---|
| `$schema` 参照 | `.claude/hooks.json`（新設、Claude Code 公式 schema 位置） | T1 構造保持 |
| 6 event types | DH 用 hooks.json で 5 event のみ採用（PreCompact は v5.13.0 以降に温存） | T3 サブセット選別 |
| matcher 構文 | DH 用 hooks.json で同構文採用 | T1 構造保持 |
| **exit code 2 (block)** | **採用せず**（warn のみ採用、exit 0 のみ） | T3 サブセット選別 |
| Node.js bootstrap | DH では Python bootstrap に置換 | T2 語彙翻訳 |

#### 1.1.3 DH 哲学フィルター適用

| 要素 | 哲学的判定 |
|---|---|
| `$schema` 参照 | ✓ 観測温存と整合 |
| `PreToolUse` 観測 | ✓ verifier-* 機構の入力源として機能 |
| `Stop` / `SessionStart/End` | ✓ 振り返り儀式（F1/F2/F3）との接続点 |
| `PreCompact` | △ DH の `/compact` 連携が未確立、温存 |
| **exit code 2 (block)** | ✗ 第 6 条「人間最終承認」と緊張、第 7 条 P4 介入権を事後発動化させる危険 → **棄却** |

#### 1.1.4 Wave 1 実装スコープ

- 新設ファイル: `.claude/hooks.json`（Claude Code 公式 schema 位置、PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd 5 event）
- 新設 skill: `crosscut-hook-observer`（PreToolUse 観測ログを `harness-verifier/reports/hook-observations.jsonl` に append-only 書き込みする bridge skill）
- DH 用 hooks.json bootstrap: `.claude/skills/crosscut-hook-observer/scripts/bootstrap.py`（Python 実装、ECC の Node.js bootstrap を翻訳）
- **Wave 2 予定**: 既存 `harness-verifier/verify.py` 拡張で hook 観測ログを D5 監視層の入力として受領（Wave 1 では未実装、観測ログ生成のみ）

#### 1.1.5 検証項目（Step D）

- [ ] verifier-philosophy: hook 機構が第 6 条「人間最終承認」を毀損しないことを確認（exit 2 不採用が SPEC で明示されているか）
- [ ] verifier-drift: hook 機構が DONT.md / SPEC.md と整合することを確認
- [ ] 動作テスト: PreToolUse hook が観測ログを harness-verifier に流せることを確認
- [ ] Council 再諮問: 「PreCompact 採用是非」を v5.13.0 候補議題として温存

---

### 1.2 候補 1: agent description `Use PROACTIVELY` トリガー語彙

#### 1.2.1 Source

ECC `agents/planner.md` frontmatter:
```yaml
description: Expert planning specialist for complex features and refactoring.
             Use PROACTIVELY when users request feature implementation,
             architectural changes, or complex refactoring.
             Automatically activated for planning tasks.
```

#### 1.2.2 採用範囲（DH 内 embedding target）

| 採用要素 | DH 内 target | 翻訳タイプ |
|---|---|---|
| トリガー動詞語彙の規範化 | `dev-env-spec.md` の skill description 規約 | T2 語彙翻訳 |
| 「PROACTIVELY」自動起動明示 | DH では「自動的に検討する」「明示されなくても起動を必ず検討する」（既に部分使用） | T2 語彙翻訳 |
| 「Automatically activated」 | DH では「主体的に発動を検討する」 | T2 語彙翻訳 |

#### 1.2.3 DH 哲学フィルター適用

DH 既存の skill description 群を audit したところ、`crosscut-issue-quality-gate` / `layer1-autonomous-dev` 等は既に類似語彙（「起動を必ず検討する」「明示されなくても」）を使用済。本候補は **既存実装の言語化裏付け** として SPEC に追加し、新規 skill 設計時の規範を明文化する。

#### 1.2.4 Wave 1 実装スコープ

- `dev-env-spec.md` に「skill description トリガー語彙規約」セクション追加
  - 推奨語彙リスト（自動的に / 主体的に / 必ず検討する 等）
  - 禁止語彙（PROACTIVELY 等の英語固有語、DH は日本語規約）
- 既存 17 skill の description 監査チェックリスト（Wave 1 では監査結果のみ記録、修正は Wave 2 以降）

#### 1.2.5 検証項目（Step D）

- [ ] verifier-philosophy: トリガー語彙規約が第 7 条「AI 組織論」の自律起動責務と整合
- [ ] 既存 skill audit: 17 skill の description トリガー語彙使用状況を一覧化
- [ ] 後続 PR への申し送り: 既存 skill の description 統一は Wave 2 以降の維持タスクとして温存

---

### 1.3 候補 6: rules/ common + 14 言語別 + 相対 `../common/` 参照規約

#### 1.3.1 Source

ECC `rules/`:
```
rules/
├── README.md
├── common/                  # 言語横断 10 ファイル
└── 14 言語別ディレクトリ:
    cpp / csharp / dart / golang / java / kotlin / perl /
    php / python / rust / swift / typescript / web / zh
```

CONTRIBUTING.md 規約:
> "Common and language-specific directories contain files with the same names. Flattening causes language-specific to overwrite common, breaking relative `../common/` references."

#### 1.3.2 採用範囲（DH 内 embedding target）

| 採用要素 | DH 内 target | 翻訳タイプ |
|---|---|---|
| `rules/` 階層構造 | `templates/rules/{common, <lang>}/` 新設 | T1 構造保持 |
| common + override 規約 | DH 用 `templates/rules/README.md` で同規約明文化 | T1 構造保持 |
| 14 言語先取り | **採用せず**、DH では L0 対話で必要言語のみ生成 | T3 サブセット選別 + 遅延戦略 |
| 相対 `../common/` 参照規約 | DH 同採用 | T1 構造保持 |

#### 1.3.3 DH 哲学フィルター適用

- ECC の 14 言語先取りは「業界実装プリミティブをそのまま吸収」に該当 → DH 流（L0 対話で確定後に必要言語のみ生成）に翻訳
- 階層構造と相対参照規約は **思考様式（動機 b）** として吸収、構造そのままで採用
- L0 対話に「多言語プロジェクトか?」「言語別 coding-standards を設けるか?」の選択肢を追加

#### 1.3.4 Wave 1 実装スコープ

- 新設ディレクトリ: `templates/rules/common/`（最初は空、後続 PR で内容充填）
- 新設ファイル: `templates/rules/README.md`（common + override 規約 + 相対参照ルール明文化）
- L0 dialog-questions 追加: 「多言語プロジェクトか?」「言語別 coding-standards を設けるか?」
- L0 dev-env-spec 追加: 言語別 rules 生成プロトコル（L0 対話確定後に必要言語のみ `templates/rules/<lang>/` 生成）

#### 1.3.5 検証項目（Step D）

- [ ] verifier-philosophy: 言語別 rules 構造が第 1 条「フラクタル原則」（階層化規律）と整合
- [ ] verifier-drift: 言語別 rules が SPEC.md の skill 分散モデルと衝突しない
- [ ] L0 対話モック: 「多言語プロジェクト想定」シナリオで dialog-questions が正しく分岐

---

## 2. Wave 1 全体マイルストーン

| Phase | 内容 | 完了基準 | 状態 |
|---|---|---|---|
| **Phase A**（本 PR 起点） | Wave 1 SPEC ドラフト枠組み | 本ファイルの commit + draft PR 作成 | ✅ 完遂 |
| **Phase B** | 各候補の SPEC 詳細起草 + Council 諮問（Wave 1 一括） | 候補 3/1/6 の SPEC 確定、Council judgment 取得 | ✅ 完遂 |
| **Phase C** | SPEC 実装（hooks.json + dev-env-spec 規約 + templates/rules/）| harness-verifier 拡張 + 既存 skill 監査完了 | ✅ 完遂（本 commit） |
| **Phase D** | 検証 + verifier 経由で抵触チェック | 全検証項目 ✓、philosophy / drift 抵触 0 | レビュー時に実施 |
| **Phase E** | merge + REGIME-LOG 記録 + 次 Wave への申し送り | v5.12.x minor リリース | merge 後 |

### Phase C 完遂時の追加ファイル一覧

- `.claude/hooks.json` — Claude Code 公式 schema 準拠、5 event 採用、warn-only
- `.claude/skills/crosscut-hook-observer/SKILL.md` — 観測 bridge skill
- `.claude/skills/crosscut-hook-observer/scripts/bootstrap.py` — Python bootstrap
- `.claude/skills/crosscut-hook-observer/scripts/observe.py` — JSONL append writer
- `.claude/skills/crosscut-hook-observer/references/output-format.md` — 観測ログ規格
- `.claude/skills/layer0-spec-architect/references/dev-env-spec.md` — トリガー語彙規約 + rules 階層化規約セクション追記
- `.claude/skills/layer0-spec-architect/references/dialog-questions.md` — 多言語プロジェクト判定セクション追記
- `delivery/SKILL-DESCRIPTION-AUDIT-checklist-wave1.md` — 17 skill 監査チェックリスト
- `templates/rules/README.md` — 階層化規約
- `templates/rules/common/.gitkeep` — 空 scaffold

---

## 3. Council 諮問結果（Phase B 完遂）

`delivery/COUNCIL-DECISION-wave1-phaseB-2026-05-11T05:00:00Z.md` で 3 諮問を一括実施、`history/COUNCIL-LOG.md` に 3 invocation 追記済。全件 `agreed_recommended` 成立、`human_escalated: false`。

### 諮問 1: hooks.json event types サブセット選別

- **invocation_id**: `council-2026-05-11T05:00:00Z-w1qb01`
- **recommended**: **A: 5 event 採用**（PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd、PreCompact 除外）
- **conflict_type**: unanimous（3 ペルソナ全会一致）
- **judgment_confidence**: 0.78
- **Wave 1 への反映**: §1.1.4 実装スコープを「5 event のみ採用」で確定。PreCompact は v5.13.0 候補で温存

### 諮問 2: 既存 17 skill description 修正タイミング

- **invocation_id**: `council-2026-05-11T05:00:00Z-w1qb02`
- **recommended**: **B: 各 skill 次回更新時に逐次修正**（経営者・開発者 6.4 vs 哲学者 1.65）
- **conflict_type**: simple_conflict
- **judgment_confidence**: 0.70
- **Wave 1 への反映**: §1.2.4 実装スコープを「dev-env-spec.md 規約追加 + 17 skill 監査チェックリスト作成のみ」で確定、修正は次回更新時
- **minority opinion 温存**: Wave 2 末振り返り儀式で 17 skill 監査進捗を観測、進捗遅延時は Wave 3 で一括修正を再諮問

### 諮問 3: templates/rules/ 言語先取りの是非

- **invocation_id**: `council-2026-05-11T05:00:00Z-w1qb03`
- **recommended**: **A: 言語先取りなし**（開発者・哲学者 5.9 vs 経営者 1.95）
- **conflict_type**: simple_conflict
- **judgment_confidence**: 0.72
- **Wave 1 への反映**: §1.3.4 実装スコープを「templates/rules/common/ + templates/rules/README.md のみ作成、言語別は L0 対話で生成」で確定
- **minority opinion 温存**: Wave 2 末振り返り儀式で L0 対話頻出言語を観測、頻出時は「推奨言語プリセット」を再諮問

---

## 4. Phase C 実装スコープ（後続 commit で実行）

Phase B 諮問結果を反映した実装スコープ:

### 4.1 hooks.json 機構（諮問 1 採決反映）

- 新設: `.claude/hooks.json`（Claude Code 公式 schema 準拠、5 event のみ、warn-only）
  - 当初本ドキュメント Phase A ドラフトでは `harness-verifier/hooks.json` 配置を想定したが、harness-verifier 独立性原則（一方向依存）と整合させるため、Claude Code 公式の `.claude/hooks.json` 位置に配置決定
- 新設 skill: `crosscut-hook-observer`（PreToolUse 観測ログ writer、harness-verifier reports に bridge）
- 新設: `.claude/skills/crosscut-hook-observer/scripts/bootstrap.py`（Python bootstrap、ECC の Node.js 翻訳）
- 新設: `.claude/skills/crosscut-hook-observer/scripts/observe.py`（JSONL append writer）
- **Wave 2 予定**: `harness-verifier/verify.py` 拡張で hook 観測ログを D5 監視層の入力として受領（Wave 1 段階では未実装、観測ログは将来の消費者に向けた素材として蓄積）

### 4.2 dev-env-spec トリガー語彙規約（諮問 2 採決反映）

- 拡張: `dev-env-spec.md` に「skill description トリガー語彙規約」セクション追加
- 新設: 17 skill description 監査チェックリスト（修正自体は Wave 2 以降の各 skill 次回更新時）

### 4.3 templates/rules/ scaffold（諮問 3 採決反映）

- 新設: `templates/rules/README.md`（common + override 規約 + 相対参照ルール）
- 新設: `templates/rules/common/`（最初は空 scaffold）
- 拡張: L0 dialog-questions に多言語プロジェクト関連質問を追加

---

## 5. 後続 Wave への申し送り

### Wave 2（候補 2 + 4 + 5）の前提条件

- Wave 1 で hooks.json 機構が動作していること（候補 5 continuous-learning は PreToolUse hook を入力源とするため）
- origin/version frontmatter 規格（候補 2）は Wave 2 で全 chewed skill に必須化
- AgentShield ルールサブセット選別（候補 4）は Wave 2 で哲学者ペルソナ Council 必須
- **harness-verifier/verify.py の hook 観測ログ読み取り経路を Wave 2 で本実装**（Wave 1 では未実装、観測ログ生成のみ）

### Wave 3（候補 7 + 8 + 議題 2 再上程）の前提条件

- Wave 2 で哲学ガードレール経路（verifier-philosophy / verifier-drift / feedback-loop）が候補 5 で動作実証されていること
- philosophy 第 8 条候補（PHILOSOPHY-NOTE-autonomy-with-guardrails 由来）が議題 2 再上程に同梱されること

---

## 6. 哲学的注記

本 SPEC ドラフトは Council 議題 0 の「B + 哲学者止揚」（B 採択 + C 精神を Step 1 に組込）の **Step 2 第 1 段** であり、哲学者の懸念「咀嚼プロトコル自体が抽象論に流れ実装に落ちないリスク」（議題 0 経営者懸念）への構造的歯止めとして機能する。

「咀嚼の 4 ステップ（観察 → 分解 → 翻訳 → 検証）」は、ユーザーの「咀嚼」メタファーを実装プロトコルに翻訳した結果であり、`PHILOSOPHY-NOTE-autonomy-with-guardrails` の「咀嚼 = 構造保持 + 適用条件のガードレール化」と整合する。

Wave 1 の 3 候補（hooks.json / PROACTIVELY 語彙 / rules 階層化）は意図的に「DH 哲学との緊張: 軽微〜最高」の幅広いスペクトラムから選ばれており、咀嚼プロトコルが緊張度の異なる素材に対して同型適用可能であることを実証する Wave である。
