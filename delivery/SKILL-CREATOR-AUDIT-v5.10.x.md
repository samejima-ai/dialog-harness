# SKILL-CREATOR-AUDIT v5.10.x — 16 スキル横断診断レポート

- **実施日**: 2026-05-08
- **対象**: dialog-harness `.claude/skills/` 配下 16 skills（v5.10.0 時点）
- **手法**: skill-creator 規約に基づく静的横断診断（4 並列フォーク）
- **手動実行モデル**: Claude Opus 4.7 (1M context)
- **前回 audit**: `delivery/SKILL-CREATOR-AUDIT-v5.0.0.md`

## 診断対象（16 skills）

| layer | skills |
|---|---|
| L0 | layer0-spec-architect, layer0-onboarding, layer0-archeo-architect |
| L1 | layer1-autonomous-dev, layer1-independent-reviewer |
| L2 | layer2-integration-verifier, layer2-orchestrator |
| crosscut | crosscut-autonomous-drive, crosscut-council, crosscut-feedback-loop, crosscut-issue-dispatcher, crosscut-issue-implementer, crosscut-issue-quality-gate, crosscut-verifier-drift, crosscut-verifier-philosophy |
| util | rtk-integration |

## 全スキル数値サマリ

| skill | lines | refs | assets | scripts | frontmatter | description | progressive disclosure | broken |
|---|---|---|---|---|---|---|---|---|
| layer0-spec-architect | 557 ⚠️ | 18 | 2 | - | PASS | CONCERN（兄弟衝突） | PASS | none |
| layer0-onboarding | 124 | 3 | 1 | - | PASS | PASS | PASS | none |
| layer0-archeo-architect | 249 | 4 | 1 | - | PASS | PASS（軽い衝突） | PASS（exemplary） | none |
| layer1-autonomous-dev | 493 | 5 | 0 ⚠️ | - | PASS | PASS | CONCERN | none |
| layer1-independent-reviewer | 214 | 0 ⚠️ | 0 ⚠️ | - | PASS | PASS（PR レビュー曖昧） | CONCERN | none |
| layer2-integration-verifier | 113 | 0 ⚠️ | 0 ⚠️ | - | PASS | PASS | CONCERN | none |
| layer2-orchestrator | 103 | 2 | 0 | - | PASS（雛形宣言○） | PASS | PASS | none |
| crosscut-autonomous-drive | 92 | 3 | 0 | - | PASS | CONCERN（trigger 本体に埋没） | PASS | none |
| crosscut-council | 240 | 11 | 0 ⚠️ | - | PASS | PASS（豪華） | CONCERN（council-weights が root） | none |
| crosscut-feedback-loop | 60 | 1 | 0 | - | PASS | CONCERN（曖昧 + dispatcher 衝突） | PASS | none |
| crosscut-issue-dispatcher | 43 | 1 | 0 | - | PASS | PASS | PASS | none |
| crosscut-issue-implementer | 161 | 5 | 0 ⚠️ | - | PASS | CONCERN（自然言語 trigger 欠落） | PASS | none |
| crosscut-issue-quality-gate | 163 | 7 | 1 | - | PASS | CONCERN（自然言語 trigger 欠落、12 軸表が 11 行） | PASS（textbook） | none |
| crosscut-verifier-drift | 52 | 1 | 0 | - | PASS | PASS（best of class） | PASS | none |
| crosscut-verifier-philosophy | 52 | 0 | 0 | - | PASS（placeholder 設計） | PASS（self-suppress） | CONCERN（placeholder 例外） | none |
| rtk-integration | 152 | 4 | 0 | 2 | PASS | PASS（symptom triggers 模範） | PASS | none |

**broken reference 総数: 0 件**（16 skill 全数）— 最大の hygiene 強み。

## 横断弱点パターン

### P0 — 修正効果が大きい構造的弱点

#### P0-1. `assets/` 不在症候群（6 skills）

該当: layer1-autonomous-dev / layer1-independent-reviewer / layer2-integration-verifier / crosscut-council / crosscut-issue-implementer / crosscut-autonomous-drive

共通症状: 出力テンプレート（DELIVERY.md / HANDOFF.md / VERIFICATION.md / INTEGRATION.md / Issue 本文規格 / council-weights）が SKILL.md 本文に inline 埋め込み or root 直下配置。

影響:
- skill-creator 規約違反（fillable templates → assets/）
- SKILL.md 肥大化（特に layer1-autonomous-dev 493 行の 60 行は inline テンプレ）
- テンプレ更新の度に SKILL.md diff が暴れる
- progressive disclosure の三段階（metadata / SKILL.md / bundled resources）が実質二段階に縮退

#### P0-2. trigger phrase 二極化（5 skills）

**自然言語 trigger 欠落**:
- crosscut-autonomous-drive — "deploy して"・"有効化して" は本文 §起動条件 にあり frontmatter に届かない
- crosscut-issue-implementer — automation 経由前提で human-driven trigger ゼロ
- crosscut-issue-quality-gate — 同上、"Issue 品質チェック" "ready-for-ai 付けていい" 等の自然語なし

**過剰汎化**:
- crosscut-feedback-loop — "還流"・"フィードバック" の汎用性が高すぎ + dispatcher と衝突

**Best of class（参考実装）**:
- crosscut-verifier-drift — quoted trigger "drift チェック" / "SPEC 逸脱検出" / "実装が仕様から離れていないか確認"
- rtk-integration — symptom triggers パターン "git log の出力が長すぎる" / "コンテキストがすぐ埋まる" / "context window が足りない"

### P1 — 中程度の弱点

- **P1-1. L0 兄弟 trigger 衝突**: 「整理したい」「仕様を整理したい」「ドキュメント化したい」「振り返りたい」が spec-architect / onboarding / archeo-architect の 3 skill 間で重複。disambiguation が paragraph 中盤に埋もれる
- **P1-2. layer0-spec-architect 557 行 over-budget**: 主因は version history 75 行（v3.1〜v5.2.0）と Pre-flight 必読文 5 回反復。両者とも history/ 移管 or §0 集約で削減可
- **P1-3. layer1-independent-reviewer に references/ 不在**: 214 行に preserve 一次/二次条件 / restructure 照合 / クレジット判定 / 配置規則 を inline で抱える。reference 化候補多数
- **P1-4. content 重複の双方向参照**: crosscut-issue-implementer ⇔ crosscut-issue-quality-gate の「Issue 本文必須セクション規格」が両方で記述（前者を一次情報源と宣言しつつ）。desync リスク

### P2 — 軽微 / 整合性問題

- **P2-1. version history bloat**: layer0-spec-architect / layer1-autonomous-dev / crosscut-issue-implementer / crosscut-issue-quality-gate / crosscut-autonomous-drive の本文に v5.x.x 紀伝が滞留
- **P2-2. layer2-orchestrator 雛形/本実装境界曖昧**
- **P2-3. crosscut-issue-quality-gate の「12 軸」が 11 行表示**（A〜E + ii〜ix で F / i / iv / x / xi / xii が欠落）
- **P2-4. crosscut-verifier-philosophy 内部不整合**（「5 本柱」と「6 条」が同 SKILL.md 内に共存）
- **P2-5. workflow path 命名不統一**（`templates/.github/workflows/` vs `templates/github-workflows/`）

## 弱点スキル優先順位（Phase 2 trigger eval 対象）

description 改善で trigger 精度に直接効く順:

1. **crosscut-issue-implementer** — automation 経由前提で human trigger 欠落
2. **crosscut-issue-quality-gate** — 同上
3. **crosscut-feedback-loop** — 「還流」「フィードバック」が汎用すぎ、dispatcher と衝突
4. **layer0-spec-architect** — L0 兄弟との trigger 衝突
5. **crosscut-autonomous-drive** — trigger が本文に埋没

## 修正アプローチ案（Phase 3 以降）

### A. description 改善（短期、自動化可）

trigger eval 設計（should-trigger / should-not-trigger 各 8〜10）を上記 5 skill に対して作成し、`scripts/run_loop.py` で自動最適化。所要: 1 skill あたり ~30 分。

### B. 構造リファクタ（中期、手作業）

P0-1 / P1-3 / P2-1 を一括で対処する Issue：
- assets/ 整備（DELIVERY/HANDOFF/VERIFICATION/INTEGRATION/Issue 規格/council-weights を assets/ に切り出し）
- layer1-independent-reviewer の references/ 新設
- version history 一斉移管（CHANGELOG.md への集約）
- L0 兄弟の disambiguation 構造を upfront 化

### C. 内部不整合修正（短期、手作業）

P2-3（12 軸表）/ P2-4（5 本柱 vs 6 条）/ P2-5（workflow path）は単発修正。Issue 化候補。

## Phase 2 完了: trigger eval 設計

5 skill 分の trigger eval（各 18 件、計 90 件）を `skill-audit-workspace/eval-sets/` に保存:
- crosscut-issue-implementer.json (should-trigger 9 + should-not-trigger 9)
- crosscut-issue-quality-gate.json (同上)
- crosscut-feedback-loop.json (同上)
- layer0-spec-architect.json (同上)
- crosscut-autonomous-drive.json (同上)

各 eval は near-miss を意識した設計（兄弟 skill との混同を狙う should-not-trigger を多数含む）。

## Phase 3 試行と切り替え: run_loop.py → 手動改善

`run_loop.py` をパッチ後の skill-creator で試行したが、以下の理由で自動最適化を断念し手動改善に切り替え:

### Windows 互換パッチ（適用済み、global side effect）

`~/.claude/skills/skill-creator/scripts/run_eval.py` および `improve_description.py`:
- `subprocess.Popen(["claude", ...])` → `shutil.which("claude")` で `claude.cmd` を解決、Windows native で正常起動
- `select.select` → Windows では `queue.Queue + threading.Thread` 経由の chunked stdout pump に分岐
- Linux/macOS は select 経路を保持（後方互換）

### trigger 検知ロジックの制限事項

run_eval.py L207-208 は「最初のツール呼び出しが Skill / Read 以外なら即 false」という保守的仕様。
TodoWrite や Bash を先に呼ぶ典型ワークフローで全件 false が返る（rtk-integration の最強 description でも 0%）。
この仕様自体は eval として正しいが、Auto モード下の skill 改善ループで活用するには改修が必要。

## Phase 3' 完了: 5 skill description 手動改善

弱点 5 skill の `description` を以下方針で書き換え（frontmatter のみ、SKILL.md 本文は不変）:

| skill | 主な改善点 |
|---|---|
| crosscut-issue-implementer | version history 1 行圧縮、human-driven trigger 9 種追加、兄弟 skill 4 種の混同回避 |
| crosscut-issue-quality-gate | 「12 軸」→「12 項目（A-E + 7 ローマ数字）」明示、human trigger 9 種、3 発動契機、混同回避 |
| crosscut-feedback-loop | 汎用語「還流」絞り込み、dispatcher 衝突回避、CTL 0 動作明示 |
| layer0-spec-architect | L0 三兄弟責務境界 upfront、代表 trigger 8 種、archeo/onboarding/autonomous-dev/dispatcher 混同回避 |
| crosscut-autonomous-drive | 本文 trigger 句を frontmatter 昇格、deployment 専用境界明示、issue-implementer / git auto-merge 混同回避 |

各 skill の description は本セッション中に system reminder の skill list に反映済み（即時有効化を確認）。

## Phase 4 完了: history 反映

- `history/CHANGELOG.md` v5.10.0 第 3 弾エントリ追記
- 本ファイル `delivery/SKILL-CREATOR-AUDIT-v5.10.x.md` を成果物として保持
- skill-creator Windows パッチも本セッションで適用、他プロジェクトでも利用可

## 残課題（次フェーズ Issue 化候補）

### A. 構造リファクタ（assets/ 整備）

`assets/` 不在 6 skill の出力テンプレートを切り出し:
- layer1-autonomous-dev/assets/ → DELIVERY.md / HANDOFF.md template
- layer1-independent-reviewer/assets/ + references/ → VERIFICATION.md template + 検証 checklist
- layer2-integration-verifier/assets/ → INTEGRATION.md template
- crosscut-council/assets/ → council-weights を assets/ へ移動
- crosscut-issue-implementer/assets/ → Issue 本文必須セクション規格を assets template に切り出し（quality-gate との重複解消）
- crosscut-autonomous-drive/assets/ → workflow placeholder spec を assets/ へ昇格

### B. 内部不整合修正（単発 Issue）

- crosscut-issue-quality-gate: 12 軸表の欠落（F / i / iv / x / xi / xii）を補完または「12 項目」を 11 項目に訂正
- crosscut-verifier-philosophy: 「5 本柱」と「6 条」の用語統一
- workflow path 命名不統一: `templates/.github/workflows/spec-drift.yml` を `templates/github-workflows/` に統一

### C. layer0-spec-architect 557 行 over-budget 削減

- 本文 version history（v3.1〜v5.2.0）75 行を `history/CHANGELOG.md` に統合 + 削除
- Pre-flight 必読文 5 回反復を §0 集約 + 各セクションは 1 行参照

### D. trigger eval 自動最適化の再活性化

- run_eval.py の検知ロジック改修（最初のツール呼び出し縛りを緩和、Bash や TodoWrite を許容範囲に追加）
- run_loop.py を 5 skill 分のフルランで自動最適化、改善後 description との比較


---

## 付録: 4 並列フォーク診断ログ

各フォークの完全レポートは本体会話のフォーク完了通知に記録。集約は本ファイル。

- L0 グループ（spec-architect / onboarding / archeo-architect）
- L1/L2 グループ（autonomous-dev / independent-reviewer / integration-verifier / orchestrator）
- crosscut 前半（autonomous-drive / council / feedback-loop / issue-dispatcher）
- crosscut 後半 + util（issue-implementer / issue-quality-gate / verifier-drift / verifier-philosophy / rtk-integration）
