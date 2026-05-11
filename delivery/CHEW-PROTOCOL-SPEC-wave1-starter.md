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
| `$schema` 参照 | `harness-verifier/hooks.json`（新設） | T1 構造保持 |
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

- 新設ファイル: `harness-verifier/hooks.json`（Claude Code schema 準拠、PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd 5 event）
- 新設 skill: `crosscut-hook-observer`（PreToolUse 観測ログを harness-verifier に流す bridge skill）
- 既存 `harness-verifier/verify.py` 拡張: hook 観測ログを D5 監視層の入力として受領
- DH 用 hooks.json bootstrap: `harness-verifier/hooks/bootstrap.py`（Python 実装、ECC の Node.js bootstrap を翻訳）

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

| Phase | 内容 | 完了基準 |
|---|---|---|
| **Phase A**（本 PR 起点） | Wave 1 SPEC ドラフト枠組み | 本ファイルの commit + draft PR 作成 |
| **Phase B** | 各候補の SPEC 詳細起草 + Council 諮問（Wave 1 一括） | 候補 3/1/6 の SPEC 確定、Council judgment 取得 |
| **Phase C** | SPEC 実装（hooks.json + dev-env-spec 規約 + templates/rules/）| harness-verifier 拡張 + 既存 skill 監査完了 |
| **Phase D** | 検証 + verifier 経由で抵触チェック | 全検証項目 ✓、philosophy / drift 抵触 0 |
| **Phase E** | merge + REGIME-LOG 記録 + 次 Wave への申し送り | v5.12.x minor リリース |

本 PR は Phase A まで完遂、Phase B 以降は後続 commit / 追加 PR 分割を Council 諮問結果に応じて判断。

---

## 3. Council 諮問予定（Phase B）

Wave 1 SPEC 詳細起草時に以下を Council に上程:

### 諮問 1: hooks.json の event types サブセット選別

- options: 5 event 採用（PreCompact 除外） / 6 event 全採用 / 3 event 最小採用
- category: implementation
- decision_category: C2 / C3

### 諮問 2: 既存 17 skill の description 修正タイミング

- options: Wave 2 で一括修正 / 各 skill の次回更新時に逐次修正 / Wave 1 内で実施
- category: maintenance

### 諮問 3: templates/rules/ 言語先取りの是非

- options: 言語先取りなし（DH 流遅延戦略） / よく使う 3 言語のみ先取り（python / typescript / go） / ECC 14 言語全部先取り
- category: conception

これらは Phase B 開始時に新規 invocation_id で起動。

---

## 4. 後続 Wave への申し送り

### Wave 2（候補 2 + 4 + 5）の前提条件

- Wave 1 で hooks.json 機構が動作していること（候補 5 continuous-learning は PreToolUse hook を入力源とするため）
- origin/version frontmatter 規格（候補 2）は Wave 2 で全 chewed skill に必須化
- AgentShield ルールサブセット選別（候補 4）は Wave 2 で哲学者ペルソナ Council 必須

### Wave 3（候補 7 + 8 + 議題 2 再上程）の前提条件

- Wave 2 で哲学ガードレール経路（verifier-philosophy / verifier-drift / feedback-loop）が候補 5 で動作実証されていること
- philosophy 第 8 条候補（PHILOSOPHY-NOTE-autonomy-with-guardrails 由来）が議題 2 再上程に同梱されること

---

## 5. 哲学的注記

本 SPEC ドラフトは Council 議題 0 の「B + 哲学者止揚」（B 採択 + C 精神を Step 1 に組込）の **Step 2 第 1 段** であり、哲学者の懸念「咀嚼プロトコル自体が抽象論に流れ実装に落ちないリスク」（議題 0 経営者懸念）への構造的歯止めとして機能する。

「咀嚼の 4 ステップ（観察 → 分解 → 翻訳 → 検証）」は、ユーザーの「咀嚼」メタファーを実装プロトコルに翻訳した結果であり、`PHILOSOPHY-NOTE-autonomy-with-guardrails` の「咀嚼 = 構造保持 + 適用条件のガードレール化」と整合する。

Wave 1 の 3 候補（hooks.json / PROACTIVELY 語彙 / rules 階層化）は意図的に「DH 哲学との緊張: 軽微〜最高」の幅広いスペクトラムから選ばれており、咀嚼プロトコルが緊張度の異なる素材に対して同型適用可能であることを実証する Wave である。
