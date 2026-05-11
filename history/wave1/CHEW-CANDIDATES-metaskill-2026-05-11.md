# ECC 咀嚼候補リスト — Phase 0.5（素材具体化）

**作成日時**: 2026-05-11T04:14:26Z
**位置付け**: Council 議題 0（`council-2026-05-11T03:49:01Z-4go7g1`）採決結果に基づく Phase 0.5 成果物。哲学者の C 精神（具体例 5-10 件抽出）を B（咀嚼プロトコル SPEC 化）の第 1 ステップとして実施。
**起点**:
- `delivery/ECC-SURVEY-2026-05-11.md`（ECC ephemeral 一次観察ノート）
- `delivery/refs-draft/ecc/` 配下 5 ファイル（agents-catalog / skills-pattern / hooks-trigger-points / agentshield-spec / instincts-design）
- ユーザー核心メッセージ: 「私の哲学をベースにエンジニアの叡智を咀嚼して取り込む」
**後続**: 本リストを Step 2「咀嚼プロトコル SPEC 化」議題（v5.12.x 候補）の入力素材として使用

---

## 評価軸

各候補は以下の構造で評価する:

| 項目 | 内容 |
|---|---|
| **Source** | ECC 内のソース位置（ファイル/セクション） |
| **DH embedding target** | DH 内のどの L0/L1 対話 step または検証 step に組み込むか |
| **咀嚼角度** | DH 哲学のフィルターで何を抽出し、何を捨てるか（業界そのまま採用ではない） |
| **動機 (a) プラグマティック** | L0/L1 対話・検証選択肢の拡大価値 |
| **動機 (b) 認識論的** | エンジニアの思考様式の取り込み価値 |
| **採否評価** | ★1〜★5（咀嚼 SPEC で取り込み優先度） |
| **DH 哲学との緊張** | 取り込みに際して哲学的歯止めが必要か |

---

## 候補 1: agent definition の `Use PROACTIVELY` トリガー語彙

| 項目 | 内容 |
|---|---|
| **Source** | ECC `agents/planner.md` frontmatter `description: "... Use PROACTIVELY when users request feature implementation ..."` |
| **DH embedding target** | `.claude/skills/*/SKILL.md` description 規約（dev-env-spec.md または skill description 慣習として） |
| **咀嚼角度** | DH skill description は既に「発動条件」を持つが、「PROACTIVELY」「Automatically activated for X」のような **AI 自動起動を明示する動詞語彙** は未確立。DH の skill 自動起動判定（philosophy.md 第 7 条 AI 組織論）の精度向上素材として取り込み。**DH 哲学のフィルター**: 「PROACTIVELY」はそのまま使わず、DH 流に「自動的に検討する」「明示されなくても起動を必ず検討する」等の語彙に翻訳（既に DH の skill 群はこの語彙を一部使用済 — 既存実装の言語化裏付けに使える） |
| **動機 (a)** | L0 対話「skill description にトリガー語彙を含めるか?」選択肢を dialog-questions.md に追加 |
| **動機 (b)** | エンジニアは AI の自動起動判定を **明示的な動詞** で構造化する思考様式（曖昧な期待ではなく契約として語彙化） |
| **採否評価** | ★★★★ |
| **DH 哲学との緊張** | 軽微（既に DH 流の語彙が一部存在）。咀嚼の方向性: 「ECC 由来であることを意識した上で DH 流に翻訳済」を明示 |

---

## 候補 2: skill SKILL.md frontmatter の `origin` / `version` 拡張

| 項目 | 内容 |
|---|---|
| **Source** | ECC `skills/continuous-learning-v2/SKILL.md` frontmatter（`origin: ECC`, `version: 2.1.0`） |
| **DH embedding target** | `dev-env-spec.md` の skill metadata 規格 |
| **咀嚼角度** | DH skill には現状 `version` 管理の慣習がない（skill 全体は DH バージョン v5.x.x に同期）。`origin` タグは「業界由来」を明示する用語として機能。**DH 哲学のフィルター**: `origin: dialog-harness` を全 DH 内製 skill に明示し、`origin: ECC-derived` などの外来由来を区別。これは「私の哲学をベース」（ユーザー）の構造的実装 |
| **動機 (a)** | L0 対話「skill の出処を明示するか?」選択肢、特に `.claude/refs/industry/{ecc, ...}/` から取り込んだ pattern に必須化 |
| **動機 (b)** | エンジニアは skill/library の **系譜・進化を frontmatter で追跡** する思考様式（依存関係の透明化） |
| **採否評価** | ★★★ |
| **DH 哲学との緊張** | 軽微。DH skill 管理に追加負担あり、ただし「業界由来 vs DH 内製」境界の規範化として価値 |

---

## 候補 3: `hooks.json` Claude Code 公式 schema + 6 event types

| 項目 | 内容 |
|---|---|
| **Source** | ECC `hooks/hooks.json`（`$schema: https://json.schemastore.org/claude-code-settings.json`、PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd / PreCompact） |
| **DH embedding target** | (1) `layer0-spec-architect/references/dev-env-spec.md` の hook 設計選択肢 / (2) `harness-verifier/` の D5 監視層拡張 |
| **咀嚼角度** | DH `harness-verifier/verify.py` は D4 内部整合性 5 項目を **Python 単体実装**で hook 機構未使用。Claude Code 公式 hook を embed することで D5 監視層に「event-driven 観測層」を追加可能。**DH 哲学のフィルター**: 「観測温存」原則と整合（観測のみ、編集しない）。exit code 2 の block 機能は DH の「人間最終承認」と緊張する可能性があり、warn (exit 0) のみ採用。ECC の `pre:write:doc-file-warning` のような **発生防止より検出温存** に翻訳 |
| **動機 (a)** | L0 対話「Claude Code 公式 hook を使うか?」「どの event type を観測するか?」選択肢、L1 検証で「PreToolUse 観測ログを harness-verifier に流すか?」 |
| **動機 (b)** | エンジニアは **event-driven 観測 + exit code 規約** で副作用を構造化する思考様式（observability の標準パターン） |
| **採否評価** | ★★★★★ |
| **DH 哲学との緊張** | exit code 2 (block) は哲学第 6 条「人間最終承認」と緊張、warn のみ採用が安全。**取り込み優先度最高** |

---

## 候補 4: AgentShield 静的解析パターン（102 ルール × 1,282 テスト）

| 項目 | 内容 |
|---|---|
| **Source** | ECC `ecc-agentshield` package（独立 npm パッケージ、`/security-scan` slash command で起動、対象: CLAUDE.md / settings.json / mcp-servers.json / hooks / agents / skills） |
| **DH embedding target** | (1) `layer1-independent-reviewer` の検証チェックリスト / (2) `crosscut-verifier-philosophy` または新設の `crosscut-verifier-security` |
| **咀嚼角度** | DH `harness-verifier/` は D4 内部整合性 5 項目のみで、業界標準の脆弱性パターン（秘密漏洩 / コマンド注入 / pickle 復元 / SQL インジェクション 等）は未組込。**DH 哲学のフィルター**: 102 ルール全部取り込みは過剰、DH 文脈で意味を持つルール（settings.json secret 検出 / hooks 内 shell injection / mcp-servers.json の credential 漏洩 等）の **サブセット 10-20 件選別**。1,282 テスト全部取り込みは harness CI 負荷を非線形に増やすため、ルール選別後に対応テストのみ移植 |
| **動機 (a)** | L1 検証対話「AgentShield 由来ルール群を参照するか?」選択肢、L0 「security 検査の標準ルールを採用するか?」 |
| **動機 (b)** | エンジニアは **数値で測定可能な脆弱性パターン**（例: 「102 ルール × 1,282 テスト × 98% カバレッジ」）を蓄積し再利用する思考様式 |
| **採否評価** | ★★★★ |
| **DH 哲学との緊張** | 軽微（観測温存と整合）。サブセット選別の判定基準が SPEC 化に必須 |

---

## 候補 5: continuous-learning-v2.1 PreToolUse / PostToolUse 観測機構（学習 instinct）

| 項目 | 内容 |
|---|---|
| **Source** | ECC `skills/continuous-learning-v2/SKILL.md`（PreToolUse/PostToolUse hook で 100% 観測、project-scoped + global、2+ project × 0.8+ confidence で promotion） |
| **DH embedding target** | (1) 新設 skill `crosscut-instinct-learning`（または `layer0-instinct-learning`） / (2) 既存「振り返り儀式」（F1/F2/F3）との接続層 |
| **咀嚼角度** | DH には自動学習機構なし（明示的な振り返り儀式のみ）。**ユーザー方針補足（2026-05-11T04:18Z, PR #75）**: 「AI の自立駆動学習は支持。哲学・原則に抵触・逸脱するもののみ人間関与」。**咀嚼結果（更新）**: ECC の auto promotion ロジックは **そのまま採用**（哲学的緊張を過剰評価していた前回判断を撤回）。ただし promotion / instinct 適用前に `crosscut-verifier-philosophy` + `crosscut-verifier-drift`（philosophy.md / DONT.md / SPEC との抵触検出）を必須通過させ、抵触検出時のみ `crosscut-feedback-loop` 経由で人間献上にフォールバック。これは「AI 自律駆動 + 哲学ガードレール」の二層構造で、ECC の学習機構と DH の独占 4 軸（観測温存・人間最終承認）を **統合（止揚）** する設計。`instinct` という用語は DH 内既存語彙との衝突要確認（continuous-learning v2.1 由来であることを `origin: ECC-derived` で明示） |
| **動機 (a)** | L0 対話「セッション学習機構を組み込むか?」選択肢。CTL 連動で抵触検出感度を調整（CTL-0: strict / CTL-3: relaxed） |
| **動機 (b)** | エンジニアは **観測 → 抽象化 → promotion** の段階的学習設計の思考様式 + DH は **抵触検出時のみ人間関与** という最小介入原則を統合した思考様式 |
| **採否評価** | **★★★★**（前回 ★★★ から昇格、ユーザー方針補足を反映） |
| **DH 哲学との緊張** | **中**（前回「大」から低下）。`crosscut-verifier-philosophy` + `crosscut-verifier-drift` を経由する設計により、自律性と哲学ガードレールの両立が可能。ただし「抵触・逸脱」の判定基準を SPEC で厳密化することが必須 |

---

## 候補 6: `rules/common/` + 14 言語別ディレクトリ + 相対 `../common/` 参照規約

| 項目 | 内容 |
|---|---|
| **Source** | ECC `rules/` 構造（common/ + cpp/csharp/dart/golang/java/kotlin/perl/php/python/rust/swift/typescript/web/zh）と CONTRIBUTING.md の "flattening causes language-specific to overwrite common" 規約 |
| **DH embedding target** | `templates/` 配下に `rules/{common, <lang>}` ディレクトリ新設、または layer0-spec-architect で「多言語プロジェクトか? 言語別規約を設けるか?」対話 |
| **咀嚼角度** | DH には言語別 coding-standards 未整備（既存 templates/ は GitHub Actions 等のメタ規約のみ）。**DH 哲学のフィルター**: ECC の 14 言語先取りは過剰、DH では **L0 対話で実プロジェクトの言語が確定してから関連 rules のみ生成** する遅延戦略。「flatten 防止」の構造的設計（common + override + 相対参照）は philosophy として吸収可能 |
| **動機 (a)** | L0 対話「多言語プロジェクトか?」「言語別 coding-standards を設けるか?」選択肢 |
| **動機 (b)** | エンジニアは **規則の階層化 + override + 相対参照** で言語横断保守する思考様式 |
| **採否評価** | ★★★★ |
| **DH 哲学との緊張** | 軽微。DH 既存 templates/ への自然な拡張 |

---

## 候補 7: `manifests/install-components.json` / `install-modules.json` / `install-profiles.json` 選別インストール機構

| 項目 | 内容 |
|---|---|
| **Source** | ECC `manifests/` 配下 3 ファイル（components: 最小単位 / modules: 中粒度 / profiles: ユースケース別） |
| **DH embedding target** | `layer0-onboarding`（既存プロジェクトへの harness 後付け、1 プロジェクト 1 回限定スキル） |
| **咀嚼角度** | DH harness は現状「全 skill 入り」前提（17 skill 全配備）で、選別配備機構なし。**DH 哲学との緊張**: DH の skill 群は相互依存的（layer0/1/2 + crosscut が連動して動作する設計）であり、components 単位での切り出しは構造を破壊する可能性。**咀嚼結果**: components/modules/profiles 階層化は **L0 対話 dev_mode（local_only / github_assisted / autonomous）の細分化** として翻訳、または skill レベルではなく **CTL レベルでの段階的有効化**（CTL-0 で minimum skill set, CTL-1 で +github 連携, CTL-2 で +Council, CTL-3 で +autonomous-drive）として再構成 |
| **動機 (a)** | L0 onboarding 対話「harness のどの部分を入れるか?」選択肢、または既存 dev_mode 軸の細分化 |
| **動機 (b)** | エンジニアは **最小コア → 拡張モジュール → ユースケースプロファイル** で配布粒度を設計する思考様式 |
| **採否評価** | ★★★ |
| **DH 哲学との緊張** | **中**。DH skill 群の相互依存性を破壊しない範囲での咀嚼が必要 |

---

## 候補 8: `SOUL.md` 自己定義文書 + 5 Core Principles 形式

| 項目 | 内容 |
|---|---|
| **Source** | ECC `SOUL.md`（Core Identity + 5 Core Principles: Agent-First / TDD / Security-First / Immutability / Plan Before Execute + Cross-Harness Vision） |
| **DH embedding target** | `harness-verifier/PHILOSOPHY.md` 補論、または `philosophy.md` 二層実装の整理参照 |
| **咀嚼角度** | DH の `philosophy.md` は **存在論的規律 7 条**（自己相似性 / 5 次元 / 対話 / 献上 / 観測温存 / 人間最終承認 / 4 役割組織論）。ECC の SOUL.md は **エンジニアリング規範 5 つ**（実装層）。**両者は階層が異なる** — 議題 2 の独占 4 軸（対話 / フラクタル / 献上 / 5 次元）の正当性を裏付ける素材として使用可能。**咀嚼結果**: ECC 5 原則をそのまま philosophy.md に追加するのは哲学違反。むしろ「DH には philosophy 7 条 + 補論として実装層 N 原則がありうるか?」の問いを SPEC 化議題で開く |
| **動機 (a)** | L0 対話「DH 流の実装層 Core Principles を持たせるか?」選択肢（philosophy 改修議題と直交） |
| **動機 (b)** | エンジニアは **自己定義文書（SOUL.md / IDENTITY.md）** で identity を明文化する思考様式 |
| **採否評価** | ★★ |
| **DH 哲学との緊張** | **大**。議題 2（philosophy.md 追記）と直接重複領域。咀嚼 SPEC 議題でも本候補は「philosophy 改修と分離」を維持し、議題 2 再上程時の参照素材として保留 |

---

## 候補横断の構造的観察

### A. 採否評価分布（v2、ユーザー方針補足反映）

| 評価 | 件数 | 候補番号 |
|---|---|---|
| ★★★★★ | 1 | 候補 3（hooks.json） |
| ★★★★ | **4** | 候補 1（PROACTIVELY 語彙）/ 候補 4（AgentShield）/ **候補 5（continuous-learning、★★★ から昇格）** / 候補 6（rules 階層化） |
| ★★★ | 2 | 候補 2（origin/version frontmatter）/ 候補 7（manifests） |
| ★★ | 1 | 候補 8（SOUL.md） |

→ **8 候補中 7 件が ★★★ 以上**で咀嚼 SPEC で取り込み価値あり。候補 8 のみ ★★ で議題 2（philosophy.md 追記）と直接重複領域のため、議題 2 再上程時の参照素材として保留。候補 5 は ★★★ → ★★★★ に昇格（ユーザー方針補足「AI 自律駆動 + 哲学ガードレール」を反映、Wave 2 に繰り上げ）。

### B. DH 哲学との緊張分布（v2、ユーザー方針補足反映）

| 緊張度 | 件数 | 候補番号 | 必要な咀嚼深度 |
|---|---|---|---|
| 軽微 | 4 | 候補 1, 2, 4, 6 | DH 流語彙翻訳、サブセット選別 |
| 中 | **2** | 候補 7, **5（前回「大」から低下）** | skill 相互依存性 / 哲学ガードレール経路の SPEC 化 |
| 大 | 1 | 候補 8 | 議題 2 と直接重複、議題 2 再上程時に統合判断 |
| 最高 | 1 | 候補 3 | exit code 2 (block) の取捨選択 |

→ ユーザー方針補足「AI 自律駆動学習を支持、哲学・原則抵触時のみ人間関与」により、候補 5 の咀嚼角度が単純化（auto promotion 採用 + verifier-philosophy/drift 経由 + feedback-loop 抵触時献上）。緊張度「大」候補は議題 2 関連の候補 8 のみ。

### C. 動機 (a) プラグマティック / 動機 (b) 認識論的の分布

ほぼ全候補が両動機を満たす。動機 (a) のみ強い候補 = 7（manifests）、動機 (b) のみ強い候補 = 8（SOUL.md）。**両動機が補強的に作用する候補が大半** という観察は、ユーザーの「咀嚼」概念が両動機の統合体であることを裏付ける。

### D. embedding target の分布

| Target Layer | 候補番号 |
|---|---|
| L0 dialog-questions / dev-env-spec | 1, 2, 3, 5, 6, 7, 8 |
| L1 verifier / independent-reviewer | 3, 4 |
| harness-verifier 拡張 | 3, 4, 8 |
| crosscut-* skill 新設 | 4 |

→ **L0 対話への embedding が中心**（7/8 候補）、ユーザー動機 (a)「Layer0,1 の環境構築対話時の選択肢」と整合。

---

## 後続 Step（咀嚼プロトコル SPEC 化議題、v5.12.x 候補）

本リストを入力素材として、咀嚼 SPEC で以下を策定:

1. **取り込み優先順位の確定**: 全 8 候補を 3 wave に分割（v2、候補 5 昇格反映）
   - Wave 1（v5.12.x 第 1 PR）: 候補 3（hooks.json）+ 候補 1（PROACTIVELY 語彙）+ 候補 6（rules 階層化）
   - Wave 2（v5.12.x 第 2 PR）: 候補 2（origin/version）+ 候補 4（AgentShield サブセット）+ **候補 5（continuous-learning + 哲学ガードレール、ユーザー方針補足を反映）**
   - Wave 3（v5.13.0 候補）: 候補 7（manifests CTL 翻訳）+ 候補 8（議題 2 と統合）
2. **参照形態の規格**: 各候補について「template 複写 / 設計パターン embed / 読み専用参照」のいずれを採るかを決定
3. **更新追随戦略**: ECC v2.0.0-rc.1 の rc 段階での型固定問題への対応（version pin / 6 ヶ月再観察予約 等）
4. **咀嚼判定基準の明文化**: 「DH 哲学のフィルター」を恣意的に適用しないための SPEC レベル基準（例: 「DH 既存原則と緊張する候補は哲学者ペルソナ Council 必須」「業界そのまま採用は禁止、必ず DH 流に翻訳・再構成」）
5. **議題 1/2 への戻り判断材料**: Wave 1 確定後、議題 1（配置先）と議題 2（philosophy.md 追記）の前提条件が揃ったかを再評価

---

## 哲学的注記

本リストは哲学者の C 精神（具体例 5-10 件抽出）の実装であり、経営者の「咀嚼プロトコルが抽象論に流れるリスク」への先回り防御でもある。

候補 3（hooks.json）が ★★★★★ かつ「DH 哲学との緊張: 最高」という二重評価を受けたことは、**取り込み価値が高い候補ほど咀嚼深度が必要**という規則性を示唆する。これは「咀嚼」メタファーの本質（消化液で素材を分解する深さは、素材の栄養価に比例する）と整合する。

候補 5（continuous-learning）と候補 8（SOUL.md）が緊張度「大」で評価 ★★★ / ★★ なのは、**議題 2 と直接交差する領域は議題 2 の再上程まで咀嚼判断を保留する** べきというフィードバックでもある。これは議題 0 採決の「議題 1/2 を保留」推奨と整合する。

ユーザー核心メッセージの「人間的分業 ≠ AI 最適分業」は、特に候補 5（continuous-learning の自動 promotion）への評価で具体的に作用した: ECC の人間的分業前提（学習を自動化）を DH の AI 最適分業（人間最終承認による意識的学習）に翻訳する咀嚼が必須となる。
