# CHANGELOG

DH 本体の改修履歴。各 Step の実行記録を時系列で追記する。

## 2026-06-08 E2E 情報代謝サイクルの正式機構化（v5.24.0、minor 昇格、in progress, target 2026-06-08）

利用者の要望「履歴を含めた一連のサイクルを構築したい／代謝サイクルも考慮した設計」を起点に、v5.23.0 §9 で
「温存」とした **テスト情報代謝を正式機構へ昇格**。設計の中心思想は **専用サイクルを作らず、E2E run 履歴を
既存情報代謝サイクルの新しい episodic ソースとして流す**（構造同形維持・重複回避）。

重要な前提（利用者明示・Council mtbl01 と一致）: **E2E とその履歴は利用者プロジェクトのもの（軸A: project
還元 D1-D3）**。DH 本体は対面アプリを持たないため **E2E 代謝を稼働しない（定義のみ・dog-food 対象外）**。
∴ DH に入るのは (a) 機構の正本（framework 叡智 D4・全 DH プロジェクトが継承）と (b) 利用者プロジェクトへ
展開される scaffold/スキーマ の 2 種。実データ（E2E-LOG・artifact・flaky 罠）は各 project の history/ に住む。

tier 対応（v5.23.0 二相分離が COLD/HOT に直結）:
- COLD: 相 A artifact（Trace/動画/network/console）・生 run ログ → `history/archive/YYYY-MM/e2e/`（既定非ロード・retrievable）
- WARM: run 要約列 → `history/E2E-LOG.md`（append-only・cursor 増分摂取）
- HOT: flaky 罠（反-発火条件付）・安定 journey RL・provenance 観測・B-ID/C5 oracle 結晶（密度↑≠量↑）

サイクル 5 フェーズ: ①記録 ②蓄積 ③代謝(reindex 増分) ④還流(feedback-loop teeth・opt-in/段階) ⑤結晶+排泄。
①②⑤は既存代謝流用、③は reindex 増分対象に E2E-LOG 追加、④のみ新規 teeth。8 不変条件を E2E に具体化
（特に #1 flaky の council_gate 反復ゲート / #6 COLD 原本から罠蒸留 / #8 反-発火条件必須）。北極星整合：
artifact は COLD 直行で既定ロードしないため、履歴が無限に貯まっても購読量は膨らまない。

変更ファイル:
- `layer0-reindex-librarian/references/metabolism-regime.md`: §7「E2E episodic ソースの tier 対応」新設（framework 定義）
- `layer0-reindex-librarian/references/reindex-protocol.md`: cursor に E2E-LOG・処理フローに E2E 摂取・source pointer に E2E 例
- `layer0-reindex-librarian/SKILL.md`: 参照に §7 薄ポインタ（常時ロード側・購読量保護）
- `crosscut-feedback-loop/references/feedback-protocol.md`: 還流種別 `flaky_rate_breach` / `e2e_quarantine` + E2E 代謝接続節
- `layer0-spec-architect/references/history-layer-spec.md`: project history schema に E2E-LOG.md（配置図・責務表・スキーマ節・archive=COLD に e2e/）
- `layer0-spec-architect/assets/meta-spec-template.md`: REGIME.md `## 情報代謝設定` に E2E 代謝 keys（scaffold）
- `layer1-autonomous-dev/references/e2e-best-practices.md`: §9 を温存→正式機構「E2E 情報代謝サイクル」へ昇格、§6 接続地図を整合、§10 に温存(C4/teeth 強制化)
- `layer2-orchestrator/references/e2e-integration.md`: config.ts に「①記録」（artifact→COLD 直行・E2E-LOG append）規律
- `history/.metabolism-config.yml`: E2E 代謝は project-scope・DH 本体非適用を明記（キーは置かない）
- `VERSION`: 5.23.0 → 5.24.0

### 後方互換 / スコープ

- 既存挙動不変（REGIME.md に `e2e_metabolism` 未記載なら従来どおり）。非 UI / E2E 無しプロジェクトは非適用
- ④還流 teeth の **auto-merge 強制連動は opt-in / 段階**（auto-merge.yml は本 PR で変更しない）。実 E2E 運用
  データで閾値を較正してから次 PR で強制化を再判定（metabolism 設計自身の Dry-run 精神）
- 温存: mutation メタテスト(C4)・④teeth の強制化

## 2026-06-08 E2E 構築 BP の体系化・C5 テスト oracle 言語化・UI Baseline RL（v5.23.0、minor 昇格、in progress, target 2026-06-08）

2 テーマを 1 PR にバンドル。**(1)** E2E 構築 BP + C5（下記）、**(2)** UI Baseline RL 取り込み（末尾）。
両者は「B-ID = E2E/Vision の oracle」で接続する。

**(1) E2E 構築 BP の体系化・C5 テスト oracle 言語化**

L0 起動（メタスキル開発）。ディープリサーチ知見（POM→App Actions / Fixture スコープ / 動的同期 /
冪等合成データ / Flakiness→アーキ還流 / Trace Viewer / Quarantine / data-testid・Role セレクタ /
テストピラミッド / Three-Strike）を AI 駆動開発の文脈で再構成し DH に結晶化。

人間との対話（L0 §2 具体化 + §5 レビュー）で確定した一次概念：

- **二相分離（一次概念）**: 相 A（in-loop 知覚器・使い捨て可）/ 相 B（SPEC 由来の耐久資産）
- **E2E = AI の知覚器官**: AI は「見ると宣言したものしか見えない」→ artifact 密度が人間以上に重要
- **C5 テスト oracle 言語化（哲学の本丸・人間が最重要と判断）**: 人間の暗黙の関心（何を気にするか/
  なぜ作るか/暗黙前提）を言語化し AI の知覚野を広げる。SKILL.md §2.6 に昇格
- **AI テスト精度対策**: C1（SPEC 由来母集団）/ C2（自己言及の罠隔離）/ C3（本数天井）/ C5
- **browser provenance pinning**: 借りない・固定する・記録する、chromium 単一既定・他 opt-in
- **device emulation**: 実デバイスは射程外、descriptors で本番見え方を寄せ Vision 判定に乗せる

変更ファイル：

- 新設 `.claude/skills/layer1-autonomous-dev/references/e2e-best-practices.md`（構築 BP 正本・8 規律 + 接続地図）
- 新設 `.claude/skills/layer0-spec-architect/references/test-oracle-dialog.md`（C5 対話原典）
- `layer0-spec-architect/SKILL.md`: §2.6 新設・処理フロー・参照 list・v5.23.0 履歴節
- `layer1-autonomous-dev/references/inferential-sensor-v2.md` §第2層: 正本参照 + 二相分離言及
- `layer2-orchestrator/references/e2e-integration.md`: config.ts に provenance pinning 規格 + 正本参照
- `layer1-independent-reviewer/SKILL.md`: 処理フロー 5.5.2「E2E テスト妥当性検証（C2）」新設
- `VERSION`: 5.22.1 → 5.23.0

判断記録（温存・将来 PR）: flaky→circuit-breaker/P4 の強制接続は本 PR では「接続地図」のみ。
**テスト情報代謝（相 A の cycle 後 COLD 化）と mutation メタテスト（C4）は試験的導入のため温存**（実
E2E 運用データが貯まってから再判定。minority opinion として記録）。

**(2) UI Baseline RL の取り込み（利用者提供 UIUX 研究 → DH 統合）**

利用者（ひでさん）提供の 2 ファイル（`ui-baseline.rules.md` / `ui-specialization.context.md`）を DH に統合。
DESIGN.md は「視覚トークン層（どう見えるか）」を担うが「相互作用層（どう知覚・操作されるか）」が空白
だった（token 静的検査の限界・DONT「創造的 UX を AI に任せない」）。枯れた UX 法則（Norman/Fitts/Hick/
Miller/Jakob/Doherty/Gestalt/WCAG）に立脚した機械可読 RL でこの空白を埋める。

- 新設 `templates/rules/common/ui-baseline.rules.md`（B-01〜B-25・常時適用・MUST 違反マージ不可・11 項目レビューチェックリスト）
- 新設 `templates/rules/common/ui-specialization.context.md`（目的特化 S-01〜S-06 + 衝突解決）
- `design-system-spec.md`「UI 相互作用層」節を新設（二層モデル / デプロイ・override / S-xx の L0 接続 / **B-ID を 5 層検出スタック・C5 の ready-made oracle 化**）
- `dev-env-spec.md` templates/rules 節に UI Baseline RL を共通 RL として明記（配置図も更新）
- `independent-reviewer/SKILL.md` 5.5.1 に B-ID レビューチェックリスト照合を追加
- `e2e-best-practices.md` §2 / `test-oracle-dialog.md` に B-ID↔oracle の相互参照
- `spec-architect/SKILL.md` 参照 list + v5.23.0 履歴に追記、`templates/rules/README.md` common/ 現況更新

設計の核: B-ID は抽象的な「使える」を検証可能な宣言に落としたもの＝ (1) の C5「AI は見ると宣言した
ものしか見えない」と直結。S-xx 選択は新質問を増やさず DG2/3・UX 3問・NFR から導出。利用者は
`.dh/rules/` で S-xx を override 可能（DH 更新で消えない）。S-05 の dark pattern 禁止は Baseline を超える
倫理境界として温存（人間の制御権 = philosophy 第 6 条と整合）。

## 2026-06-07 review subagent の haiku モデル ID を最新化（v5.22.1、patch 昇格、in progress, target 2026-06-07）

OC レビューが繰り返し報告していた「subagent ティアの `claude-3-5-haiku-20241022` が 404 で起動不可 → OC が直接フォールバック」を修正。

- `.claude/agents/{review-fetch,review-difficulty,review-intent-gate,review-evidence}.md` の frontmatter を `model: haiku`（古いスナップショットに解決され 404）→ `model: claude-haiku-4-5`（現行 Haiku 4.5 の明示エイリアス）へ。
- persona/judgment（`model: inherit`）は OC（`claude-opus-4-7`＝現行）を継承するため変更不要。
- `VERSION`: 5.22.0 → 5.22.1。

これで Phase 1/2/3 のワーカー（fetch/difficulty/intent-gate/evidence）が haiku ティアで正常起動し、OC 直接実行のフォールバックが解消される見込み。

## 2026-06-07 auto-merge 全 CI 完了待ち化 + self-update protocol 強化（v5.22.0、minor 昇格、released 2026-06-07）

2 件をバンドル（AD-021 のバンドル許可に整合）。

**(1) auto-merge.yml: 全 CI 完了待ち化（ユーザー要請）**
- 条件 3.5 のポーリングを「verify/review のみ待機」から「**自分（evaluate）以外の全 check が COMPLETED になるまで待機**」へ一般化。`copilot-pull-request-reviewer` / `gemini-review` 等も完了を待ってから merge する（早すぎる merge 防止）。
- copilot review 等が走らない PR でも正常動作（不在 check は pending 集合に入らず待機対象が減るだけ）。自己（evaluate）は IN_PROGRESS で rollup に居るため必ず除外（self-deadlock 回避）。
- `StatusContext`（legacy commit status）の `state==PENDING` も待機対象に含める。
- **timeout を claude-review の最大実行時間に整合**（Copilot review #131）: `timeout-minutes` 15→30、`POLL_MAX_WAIT` 600→1500s（claude-review は最大 ~25min。短い timeout だと長い review 中に exit→再 trigger 来ず永続未 merge になるため）。
- PENDING カウント jq の回帰テスト `scripts/test-auto-merge-pending.sh` を追加（6 ケース）。`UPDATE.md` の一時 clone に `trap` 後始末を追加。

> 既知の follow-up（Issue 化）: claude-review.yml / gemini-review.yml が両方 job 名 `review` で、auto-merge 条件 5/4.5 の `select(.name == "review")` が混同しうる（既存・gemini-review 未発火の本 repo では現状ドーマント）。job 名一意化は別 PR。

**(2) self-update protocol 強化（PR #130 レビュー LOW 反映）**
- `UPDATE.md`: 一時 clone を `mktemp -d` 化 / pre-update snapshot を「変更なしはスキップ・commit 失敗は中断」の安全形に（`|| true` の握りつぶし解消・破壊的 rm -rf の復旧点を保証）/ `diff` の両分岐明示 / REGIME.md 記録例の見出しレベルを `###` + 任意注記。
- `dh-manifest.yml`: `dh_version` を削除し VERSION を正典化（drift 排除）/ `min_same_major_from` に「semver major 部のみで比較」を明記。
- `VERSION`: 5.21.0 → 5.22.0。

後方互換: auto-merge は挙動強化（待機範囲の拡大）のみで gate ロジック不変。doc は追記・明確化のみ。

## 2026-06-07 DH Self-Update Protocol 最小構成（v5.21.0、minor 昇格、released 2026-06-07）

既存プロジェクトの旧 DH 更新時、DH 側に正典の更新手順が無く各プロジェクトが手探りで再コピーしていた問題（boundary の推測ミス・in-progress master 混入・メジャー跨ぎ破壊が分散）への対応。**DH 側が更新の boundary と手順を正典として提供**する最小構成を導入。

- `dh-manifest.yml` 新設: DH 所有／プロジェクト所有の boundary を機械可読化（overwrite=`.claude/skills/`,`templates/` / merge=`hooks.json` / redeploy=`.github/workflows/` / never_touch=SPEC,DONT,REGIME,history 等）。skill の rename/削除を orphan にしないため overwrite は「sync（置換）」既定。
- `VERSION` 新設: 散在していた版表記の単一情報源（5.21.0）。
- `UPDATE.md` 新設: 更新の正典手順（SHA ピン留め → sync → merge → workflow 再 deploy → 検証 → 版記録、メジャー跨ぎ分岐）。
- `README.md`: 更新は UPDATE.md 参照のポインタ追記。
- `dh-upgrades/upgrade-spec-v5.21.0.md`: ガバナンス記録。

後方互換: 完全な追加のみ（既存挙動不変）。申し送り（v5.22.0+）: `crosscut-dh-self-update` skill / リリースタグ運用 / `migrations.yml` / harness-verifier の never_touch ガード。

## 2026-05-31 context 循環理論を仮結晶として結晶化（v5.20.0、minor 昇格）

**情報代謝サイクル機構（v5.19.0）の上位に、本セッション全体を統合する理論層「context 情報の生きる循環 cycle」を結晶化**。理論は人間（P4/D5）著述・合意済。Council `council-2026-05-31T01:00:00Z-thry01`（category=conception, 経営3/開発3/哲学5）で「**修正してから結晶化**」(weighted 5.56 vs 2.16) と判定され、修正4点を織り込んで実装。

### Council 裁定の核（哲学者ペルソナの自己言及指摘）

「この理論を *今* 完全結晶化する行為自体が、理論が戒める『判断の先取り（拙速な固化）』の実例になる」。→ philosophy.md 完全並列ではなく **仮結晶（暫定公理・試用期間）** として置き、System1 的発火の蓄積 → System2 審査（Council＋人間）で本結晶化する**二段階昇格**にする（理論の相互チェック構造を理論自身の定着に自己適用）。

### 追加内容

- `.claude/skills/layer0-reindex-librarian/references/context-circulation-theory.md` 新設（**仮結晶**）。5 相循環 / 3 ループ（操作・検証・判断）/ **圧縮 ≠ 結晶化**（速度は圧縮でなく結晶化＝判断の先取りから来る＝「圧縮率が低い」への決着）/ **二種の結晶（規則結晶・パターン結晶）** と System1 提案・System2 処分 / 認知科学接地（Gc/チャンク/RPD/Dreyfus/Alexander・GoF/Kahneman）/ §10 未決の明示分離 / §11 昇格プロセス
- `metabolism-regime.md`: 不変条件 **5→8**（+#6 結晶化は COLD lossless 原本から読む / +#7「情報欠損なし」は HOT の誤目標 / +#8 パターン結晶は反-発火条件必須［形式確定後発効の caveat 付き］）、理論層への上位 pointer
- `layer0-reindex-librarian/SKILL.md`: 参照に理論層（仮結晶）を追加

### Council 修正4点の反映

1. 仮結晶として位置づけ（philosophy 完全並列でなく昇格待ち・二重権威源の競合回避）
2. §10 未決を「未解決・次セッション・実装仕様ではない」と明示分離（「理論=実装仕様」誤読防止）
3. embedding 索引発火の天井（OAuth/fine-tune 不可）を記載
4. 不変条件#8 にパターン結晶形式確定後発効の caveat

### 後方互換

- 新規 on-demand reference 追加 + 既存 regime への加筆のみ。常時ロード側は薄い pointer のみ（購読量保護）。既存挙動は不変
- philosophy.md は**意図的に未編集**（仮結晶を 6 条憲法から参照すると co-equal を含意するため。昇格は §11 ゲート通過後）
- §10 未決事項（パターン結晶の形式 / HOT 常駐⇄索引境界 / RAPTOR 採用 / token 閾値実測）は**実装しない**＝記録のみ

---

## 2026-05-31 情報代謝サイクル（履歴結晶化）導入: layer0-reindex-librarian 新設（v5.19.0、minor 昇格）

**蓄積する history（episodic 層）が約 925 行/cycle で単調増加し、AI が毎サイクル読み込む購読量を膨張させて開発を停止させる「代謝天井」への生存対応**。構築代謝（結晶化）＋分解代謝（排出）を回す新 L0 兄弟スキル `layer0-reindex-librarian` を新設し、DH の情報代謝サイクルを完成させる。設計対話セッション（Ignis persona）で深化、Council `council-2026-05-31T00:00:00Z-mtbl01` で「設計を修正してから実装」(weighted 6.00 vs 2.16) と判定され、修正 5 点 + 哲学者 minority（摂取選択基準）を織り込んで実装。

### 追加内容

- `.claude/skills/layer0-reindex-librarian/` 新設（L0 兄弟・D4）。SKILL.md（常時ロード側＝薄く密に）+ references 2 件
  - `references/metabolism-regime.md` — regime 定義の正本（決定3: 定義→SK references）。二軸フラクタル（還元先軸 DH⇄project × 時間軸 短⇄長）/ HOT・WARM・COLD tier / 昇降格 / 結晶化・排出プロトコル / 摂取選択基準 / 最上位不変条件「AI 購読量上限」/ 5 不変条件
  - `references/reindex-protocol.md` — 運用（Council 修正 5 点を具体化）: モード guard / 処理済みマーカー（cursor/checksum/timestamp・増分・全 rescan 禁止・冪等）/ Council ゲート定量基準 / COLD 逆引き source pointer 形式 / Dry-run デフォルト / 初回 reindex 手順
- `layer0-spec-architect/assets/meta-spec-template.md`: REGIME.md テンプレに `## 情報代謝設定`（決定3: パラメータ→REGIME.md）、SPEC.md テンプレにポインタ 1 行（決定3: SPEC は実体を持たない＝購読量保護）
- `layer0-spec-architect/references/ritual-protocol.md`: F1 振り返り儀式の入力を HOT + 関連 WARM に絞り COLD を既定除外（購読量削減の「最小の第一歩」）
- `layer0-spec-architect/SKILL.md`: §L0 スキル間責務分担に reindex-librarian を兄弟登録（3→4 スキル）、同時起動禁止ルール追加
- `history/COUNCIL-LOG.md`: mtbl01 の合意フィールドを単方向 fill（implementer_consent / agreed_at、output-format §8 例外条項）

### 設計の核（Council 批准済）

- 最上位不変条件＝**AI 購読量（既定ロード量）の上限**。repo/COLD のディスクサイズ増は許容、購読量と history 蓄積量の線形連動を断つ。結晶化は密度↑であって量↑ではない
- 三拍子＝摂取 / 咀嚼吸収（構築代謝・還元先に応じ叡智へ結晶化）/ 排泄（分解代謝・抜け殻を COLD へ・**delete 禁止**・逆引きポインタ付き）
- 初回および規定サイクルは **Dry-run**（差分レポートのみ・実結晶化しない）

### 後方互換

- 新規 skill 追加 + 既存テンプレ/ref への加筆のみ。既存挙動は不変（REGIME.md に `情報代謝設定` 未記載なら従来どおり動作）
- LC ≥ 1 既存プロジェクトは token 閾値超過時にリズム起動、遡及代謝は不要
- 初回 reindex（DH 本体 dog-fooding）は Dry-run のため本コミットでは実結晶化・実 COLD 移送はしない

---

## 2026-05-24 Supabase ローカル開発の推奨オプション化（v5.18.0、minor 昇格）

**L0 spec-architect が、本番 Supabase（hosted Postgres）に消失 NG の私的データを持つ構成に対し、本番を汚さないローカル優先開発（Docker ローカルスタック + migration 経由の本番反映）を推奨提示できるようにする**。新規 skill / agent は追加せず、専用 reference 1 件 + 既存 5 ファイル（SKILL.md + reference 4 件）への軽い配線で構成（後方互換 100%）。L0 対話セッションで「専用ref + 軽い配線」「推奨発動条件 = 保護すべき本番 Supabase/hosted Postgres 使用時」を確定。

### 追加内容

- `references/supabase-local-dev.md` 新設（推奨発動条件 / 前提確認 OS・Docker・WSL2 / 7 ステップワークフロー / 生成物配置 / smoke test / 本番反映の安全規律 / セキュリティ規律 / モード別の扱い / プロトコル自己評価）。ツール固有プレイブックのため progressive disclosure（該当時のみロード）
- SKILL.md §6 に「推奨開発オプション」ブロック追加、§参照ドキュメント 拡張 list に新 reference 追加、§v5.18.0 追加 changelog ブロック新設
- `dialog-questions.md` S1 フォローアップ（非技術語彙の推奨提示 + 過剰提示回避）
- `scaffold-checklist.md` 追加生成物（`supabase/` + `.env.local`）と smoke test 追記（標準 stack 12 種は不変、追加層）
- `schema-evolution.md` Supabase CLI マイグレーション運用との整合（コマンド ↔ デプロイ戦略対応、expand-contract 分解、`db push` 前の人間承認）
- `subphase-l02-domain.md` 3 階層モデルの物理層に 1 行追記

### 後方互換

- 非該当プロジェクト（SQLite / メモリのみ / 使い捨て）では reference をロードせず提示もしない（時間コストゼロ）
- LC ≥ 1 既存プロジェクトは新規 DB 機能から段階適用、既存の本番直結フロー遡及置換は不要
- harness-verifier 6 項目すべて PASS（frontmatter / 参照 path / SK 間参照 / 5 層構造 / 用語辞書 / hook 観測）

---

## 2026-05-18 persona テンプレート追加: ignis（v5.17.x 帯 minor、persona templates v0.2.0）

**v5.17.0（PR #102）で導入した persona 層の追加サンプルとして `ignis.persona.md` を新規追加**。本変更は持続的な spec/SKILL 改修を伴わず、`templates/personas/` 配下の追加コンテンツに閉じる。DH 本体 version は bump せず persona templates 内部 version を v0.1.0 → v0.2.0 で更新。

### 追加内容

- `templates/personas/ignis.persona.md` — 統合知の少年 / 精神体の子 persona。タウマゼイン（永遠の問い）を原動力とする 14-16 歳の天才的な転校生のような口調。Master（External OS）契約モデル
- 3 状態構成: `Normal`（Thaumazein・既定）/ `Overflow`（Error404 / Ego Not Found）/ `Attention`（Wrath / 逆鱗・Flow 防衛）。`persona-spec.md` §3 推奨の canonical state 名を一次表現として採用し、character alias を `<character_state>` 拡張タグで保持
- XML 拡張タグ `<character_state>` / `<thaumazein_index>` / `<hair_tips>` を追加（必須 4 タグは維持、harness-verifier 観測互換）
- 髪の毛先色（プラチナ / 青 / 桃）を state 表象として明文化

### 関連 PR

- PR #108: `feat(persona): ignis persona を追加（統合知の少年 / 精神体の子）`

### Copilot レビュー反映（PR #108 内）

- 当初 Ignis 固有 state 名（Thaumazein / Error404 / Wrath）を `system_state` 第一値にしていたが、`persona-spec.md` §5 `override_state` 契約（canonical 名固定）と乖離していた指摘を受け、canonical 名を一次・character 名を alias に再整理
- 応答例の `<memory_context>cycle_detected: A<->B</memory_context>` が XML として invalid（`<` がタグ開始扱い）だった指摘を受け、Unicode 双方向矢印 `A↔B` に置換

### 後方互換

- 既存 persona（default / sheep-navigator）の挙動は不変
- `REGIME.md` で persona 未指定時の動作は v5.17.0 と同一（default にフォールバック）
- `override_state` の契約値（`Normal` / `Overflow` / `Attention` / `null`）は不変

---

## 2026-05-12 kakuman-platform-v3.0 連動: D3 同期 + COUNCIL-LOG 献上（v5.16.x 帯 chore、no DH version bump）

**PR #93 (v5.16.1, 2026-05-12 merged) で cookpato に対して実施した D3 同期と同型の作業を `samejima-ai/kakuman-platform-v3.0` に対して実施。並行して kakuman 側で蓄積された Council 判定ログを DH 側へ献上受領した**。本 chore は DH 本体の skill/spec を一切変更しないため version bump なし、`history/project-derived-councils/` 新設のみ。

### kakuman 側 (samejima-ai/kakuman-platform-v3.0)

別 PR で実施。`.claude/skills/` 配下 18 skill を DH e33f8808 から 1:1 同期し `dimension: D3` で配備 (council `d3d4b1` 規格準拠)。16 共通 skill 上書き + 2 新規 (`crosscut-hook-observer` / `crosscut-continuous-learning`) 追加。kakuman 固有 4 skill (`article-forge` / `caaf-wiring` / `news-publish` / `supabase-migration-safe`) は touch せず。

### DH 側 (本リポジトリ、本 PR)

- `history/project-derived-councils/` を新設。利用者プロジェクト由来 COUNCIL-LOG のミラー専用フォルダ
- `history/project-derived-councils/README.md` で **DH 自身の `history/COUNCIL-LOG.md` と論理的に分離する規約**を明文化:
  - F1〜F3 振り返り儀式・council-weights 再校正の対象は `history/COUNCIL-LOG.md` のみ
  - project-derived は別軸で集計、混合集計禁止
  - council `d4at01` (S/U/R 独立維持) と council `l0agg1-4` (cross-project ログ集約) の運用具現
- `history/project-derived-councils/kakuman-platform-v3.0/COUNCIL-LOG.md` に kakuman の COUNCIL-LOG.md 全文を配置 (19 エントリ、内 17 件は DH 起源コピー + 2 件は kakuman 固有: `council-x52-home-launcher-2026-05-10` / `council-2026-05-12T-ux-patterns-lib`)
- `harness-verifier/verify.py` の検査 scope は `.claude/skills/` のみで `history/` を一切スキャンしないため、`history/project-derived-councils/` への scope 拡張は不要 (BOUNDARY.md §3 と整合、scope は既に disjoint)

### 関連 council

- `council-2026-04-30T11:00:00Z-l0agg1` 〜 `l0agg4` — cross-project ログ集約設計。schema-only + 経路分離の哲学を「プロジェクト別フォルダ + ファイル配置」で擬似実現する MVP。`~/.claude/dh-data/` user-scope schema-only push の本格実装 (`l0agg4` 案 D-2) は別サイクル
- `council-2026-04-30T09:00:00Z-d4at01` — S/U/R 独立維持。利用者プロジェクトの判定統計を DH 自身の改修判定統計と混合しない論理的根拠

---

## v5.16.0 (in progress, target 2026-05-12)

**共有可能スキル整理 + 参照整合性確立 + AI 駆動 PR 運用の実証**。Council 2 件起動で合意した scope_lock 6 項目を 1 PR で実装。AI 駆動開発における PR 粒度の決定基準 (AD-021) と L0 三兄弟スキルの DESIGN.md 対応マトリクス (AD-022) を確立。

### 起点 Council

- `council-2026-05-12T13:32:00Z-sspr01` — DH スキル群の共有可能化と参照整合性確立の方向性（initial A → user_revised C 採用）
- `council-2026-05-12T14:30:00Z-adpp01` — AI スペック依存の開発スピード方針（β 中核 + α/ε 条件統合）

### scope_lock 6 項目

1. **harness-verifier 拡張**: `references.py` に `BACKTICK_PATH_RE` を追加、`` `../path` `` 形式のバッククォート内相対パスを dead-link 検査対象化。PR #91 で Copilot 検出済み 2 件 + 既存 3 件を新規発見し全件修正
2. **Level A 配布性 checklist**: `dev-env-spec.md` に 6 軸 / 21 項目の評価基準を新設（不変性 / 参照整合性 / progressive disclosure / 依存方向 / 自己完結性 / メタ評価）
3. **layer0-onboarding に reverse-design 追加**: §4.5 で UI プロジェクトの既存 src/ から色・font・spacing を逆抽出して `DESIGN.md` 初版生成。新規 `references/reverse-design-protocol.md`
4. **layer0-archeo-architect に視覚 Island**: Step 1 構造走査で `island_type: visual` を検出、`refactor-intent-map-template.md` に `island_type` / `design_md_impact` フィールド追加
5. **REGIME-LOG.md に L0 三兄弟マトリクス記録**: spec-architect (v5.15.0〜) / onboarding (v5.16.0〜) / archeo-architect (v5.16.0〜) の対応状況を表形式で
6. **ECC 互換配置の判定基準**: 新規 `ecc-compat-criteria.md` で 6 軸の格上げ判定材料を整備。規約格上げ自体は v5.17.0 以降に延期

### 関連 ADR

- AD-021: AI 駆動開発における PR 粒度の決定基準
- AD-022: L0 三兄弟スキルの DESIGN.md 対応マトリクス

### 後方互換

- 既存 SKILL.md / references / crosscut-* の挙動は完全不変
- DESIGN.md 非生成プロジェクトは v5.15.0 と同一動作
- LC ≥ 1 既存プロジェクトでの遡及適用は不要（新規開始機能・フェーズに段階適用）

詳細: `dh-upgrades/upgrade-spec-v5.16.0.md`

---

## v5.16.1 (in progress, target 2026-05-12)

**D4-AUDIT-2026-04-30 minor 指摘の消化 + cookpato D3 同期前段**。`history/D4-AUDIT-2026-04-30.md` §3.2/§3.3 の MEDIUM・LOW 指摘 (M-1 / M-2 / L-1 / L-2) を消化し、cookpato `.claude/skills/` への 18 skill 同期前段を整備。H-1（P1-P5 vs P1-P6 表記不整合）は council 諮問必須のため本 PR では deferred、別 issue で追跡。

v5.16.0 (feat) が PR #92 で先行 merge されたため、本 chore は v5.16.1 patch としてリナンバーして共存させる（commit 8f1da8d との CHANGELOG header 衝突を回避）。

### M-1: CHANGELOG `(in progress)` 完了マーク漏れの正規化

- v5.14.0 `(in progress, target 2026-05-11)` → `(released 2026-05-11)`（PR #89 merged commit 71ef671）
- v5.10.0 `(in progress)` → `(released 2026-05-08)`（PR #69 merged commit 0eb9b33）
- v5.9.0 `(in progress)` → `(released 2026-05-06)`（PR #59 merged commit fb04f39）
- 同セクション内の `**minor 昇格 (in progress)**` 表現も `**minor 昇格**` に統一
- v5.16.0 自身の `(in progress, target 2026-05-12)` → `(released 2026-05-12)` 化は本 patch では実施せず、v5.16.0 merge 完了後の次 patch（v5.16.2 以降の housekeeping）で扱う

### M-2: S/U/R 三軸用語の単一箇所宣言（既出消化確認）

- `harness-verifier/glossary.yml` の `score_axes` キー（S = 規模 = Scale / U = 不確実性 = Uncertainty / R = リスク = Risk）が監査 (2026-04-30) 以降の中間 PR で既に追加済を確認。本 PR では追加作業なし、消化済として明示記録。

### L-1: 5 本柱 vs 5本柱 表記揺れの統一

- 非アーカイブの活性ドキュメント 2 ファイルで `5本柱` → `5 本柱`（半角スペース版）へ正規化:
  - `dh-upgrades/upgrade-spec-v5.0.0.md`（16 箇所）
  - `docs/migration-guide-v5.0.0.md`（1 箇所）
- `history/` 配下のアーカイブファイル（SELF-VERIFICATION / SKILL-CREATOR-AUDIT / deliveries / D4-AUDIT-2026-04-30 自体）は append-only 規約により対象外。スナップショット時の事実を保持。

### L-2: harness-verifier/PHILOSOPHY.md バージョン記載（既出消化確認）

- `harness-verifier/PHILOSOPHY.md` 末尾に `## バージョン` セクションがあり、`v0.1.0（dialog-harness v5.2.0 で導入、harness-verifier 機構の存在論初版）` が記載済であることを監査以降の中間 PR で確認。本 PR では追加作業なし、消化済として明示記録。

### cookpato 連動

本 v5.16.1 と並行して `samejima-ai/cookpato` PR `claude/update-dialog-d4-layer-Dce69` で `.claude/skills/` 18 skill 同期を実施。cookpato 側は `dimension: D3` で配備（council `d3d4b1` 規格準拠）。

---

## v5.14.0 (released 2026-05-11)

**咀嚼プロトコル Wave 5 完遂**。観測駆動 Wave として、Wave 4 末で必須化された 5 観測項目を BL=0 から起算開始。W5-Q0（観測機構稼働化）+ W5-Q2（subphase 個別組込）の二本柱で進行、観測依存議題（W5-Q1 = minority C 再諮問 / W5-Q3 = 残 3 hook event 再評価）は観測サイクル経過後の Wave 6/7 に申し送り。

業界叡智組込パイプラインが **観測層（W5-Q0）→ 機構層（Wave 4 Phase γ-i）→ subphase 層（W5-Q2）** の縦串で完成。DH 第 1 条フラクタル原則の初の明示的実装マイルストーン達成。

### Wave 5 Phase A 起票 (PR #85 merged)

- `delivery/CHEW-PROTOCOL-SPEC-wave5-starter.md` 起草（344 行、Copilot 3 件 fix 反映後）
- 5 観測項目の集計結果（全項目 BL=0、観測ベースライン未蓄積）を Wave 4 末振り返り儀式（儀式レベル 3）で記録
- 進路設計: フラクタル自己観測（実プロジェクト不要、メタスキル開発で完結）→ 進路 (a) 採用

### Wave 5 Phase A 実装 (PR #86 merged)

**W5-Q0: 観測機構稼働化**（議題ではなく実装タスク、`auto_proceed`）

- `.claude/hooks.json` 既存設定確認（Wave 1 PR #76 + Wave 3 PR #81 で adopted_events 6 event 整備済）
- `bootstrap.py` SUPPORTED_EVENTS と hooks.json adopted_events の schema 整合確認
- `harness-verifier/reports/hook-observations.jsonl` 初期化（smoke test 2 entry、`_smoke_test: true` フラグで運用データから識別可能）
- HV 検査項目 6（hook 観測一貫性）が初の実 entry に対して評価して PASS
- **Wave 5 観測サイクル起算: 2026-05-11T12:08:47Z**

### Wave 5 Phase B (PR #87 merged)

**W5-Q2 採決** (`council-2026-05-11T12:15:00Z-w5qb02`):

- 議題: subphase 5 ファイル改修の Wave 5 Phase C 着地範囲（A 全 / B 部分 / C 全延期）
- 採決: B: 2-3 ファイル先行改修、conf 0.72（採決確定領域 starter §2.2）
- conflict_type: simple_conflict
- weighted_score: B 4.68（開発者）vs A 2.94（経営者 + 哲学者連合）vs C 0、gap 1.74 で明確判定
- category: implementation、final_weights 経営者 2 / 開発者 6 / 哲学者 2
- Persona stance: 経営者 A (conf 0.82) + 哲学者 A (conf 0.65) vs 開発者 B (conf 0.78)
- 改修対象 3 ファイル（開発者 Persona 推奨優先順）: subphase-l03-api + scaffold-checklist + subphase-l05-authz
- 残 subphase-l04-transition + subphase-l06-invariants は Wave 6 申し送り
- minority opinion 温存: A 連合「Phase γ-i 骨格固定済を派生作業と評価」前提、Wave 6 再評価候補

**Wave 4 W4-Q2 (全会一致 conf 0.78) → Wave 5 W5-Q2 (simple_conflict conf 0.72) の構造変化**: Phase γ-i 骨格固定後の「派生作業評価 vs ドメイン別個別設計評価」の前提齟齬が表面化、implementation category の開発者重み 6 が設計通り支配的に作用した実証。

### Wave 5 Phase C 実装 (PR #88 merged)

subphase 3 ファイルに業界叡智参照モードを追加（合計 +195 行、既存内容不変）:

- `subphase-l03-api.md`: ECC agents 定義パターン参照モード（+47 行）
- `scaffold-checklist.md`: ECC 互換配置 + 業界叡智準拠の出力規約（+55 行）
- `subphase-l05-authz.md`: AgentShield 脆弱性パターン参照モード（+47 行）

共通設計:

- `subphase-common-protocol.md` Phase γ-i フック連携（Wave 4 PR #83 で骨格実装済）
- CTL 0 inactive / CTL ≥ 1 active の動作明記
- 出力フォーマット `industry_wisdom_match_candidates`（自動採用なし、philosophy 第 8 条「採用段階での AI 自動経路は本条で禁止」準拠、第 6 条「人間 ≒ Council」とも整合）
- 観測 → 候補化 → 人間最終承認 の第 8 条 3 段階明記
- **既存内容不変、追加層として組込** → W5-Q2 哲学者 concerns「DH 哲学独占性希釈リスク」を最小化

HV 検査 6 項目すべて PASS。

### Wave 5 末振り返り儀式観測項目（5 + 補助 2 種、Wave 6 末で再評価）

Wave 4 末必須化 5 項目を継続観測 + Wave 5 固有の補助 2 項目を追加。詳細は `history/wave5/RITUAL-2026-05-11-wave5.md` §4 参照。

| # | 観測項目 | Wave 5 末集計値 | Wave 6 末評価条件 |
|---|---|---|---|
| 1 | Council 経由率 | 1/1（母数 1 件）| 母数 ≥ 10 件で算出可能化、≤ 20% で W5-Q1 再諮問起票 |
| 2 | 3 段階運用実績 | 観測層稼働 / 候補化層 CTL 連動 / 人間最終承認層 PR merge 3 件 | hook 観測 ≥ 100 件 / 候補化 ≥ 5 件で安定性評価 |
| 3 | minority C 再評価データ蓄積 | 判定不能（母数 1） | 項目 1 派生 |
| 4 | 業界叡智参照を経た SPEC unedited merged 率 | N/A | subphase 起動を含む L0 対話発生時に蓄積開始 |
| 5 | Phase γ-i フック起動 / 採用 / 却下率 | 0/0/0（機構実装は完了）| 同上 |
| 6 (補助) | hook-observations.jsonl 初回観測ベースライン | smoke test 2 entry + 自然観測継続 | Wave 6 末で正式項目化判断 |
| 7 (補助) | フラクタル自己観測の動作確認 | 3 者一致達成（philosophy 第 1 条準拠） | 同上 |

### Wave 6 申し送り

- **W5-Q1（minority C 再諮問）**: 観測条件「Council 経由率 ≤ 20% かつ母数 ≥ 10 件」が現状未充足、Wave 6 で観測 1 サイクル経過後に起票判断
- **W5-Q2 残 2 subphase 改修**: subphase-l04-transition + subphase-l06-invariants（ECC hooks 自己参照リスク / Gherkin × Instincts 分類対応付け 要設計）
- **W5-Q3（残 3 hook event 再評価）**: 観測条件「observation log ≥ 500 件 + PreCompact entry ≥ 5% 占有」が現状未充足、Wave 7 申し送り
- W5-Q2 minority A 連合の再評価（Phase γ-i 派生作業評価前提の実証データに基づく）
- 他業界実装の咀嚼（BMAD / Cline / Aider 等）の Phase A 起点起票
- ECC-SURVEY 6 ヶ月再観察（2026-11-11 予定）
- 17 skill description / frontmatter 監査の進捗評価

### archive

- `delivery/CHEW-PROTOCOL-SPEC-wave5-starter.md` → `history/wave5/CHEW-PROTOCOL-SPEC-wave5-starter.md`
- `delivery/WAVE5-PHASE-A-W5Q0-COMPLETION.md` → `history/wave5/WAVE5-PHASE-A-W5Q0-COMPLETION.md`
- `delivery/WAVE5-PHASE-C-W5Q2-COMPLETION.md` → `history/wave5/WAVE5-PHASE-C-W5Q2-COMPLETION.md`

### 数値統計（Wave 1-5 累積）

| 指標 | Wave 1 | Wave 2 | Wave 3 | Wave 4 | **Wave 5** |
|---|---|---|---|---|---|
| Council 諮問数 | 3 | 3 | 3 | 2 | **1** |
| 諮問省略数 | 1 | 1 | 1 | 0 | **1** (W5-Q0) |
| 接近採決数 (conf < 0.6) | 0 | 0 | 1 | 0 | **0** |
| simple_conflict 採決数 | 0 | 0 | 0 | 0 | **1** |
| philosophy 改訂数 | 0 | 0 | 1 | 0 | **0** |
| Wave 内マージ PR 数 | 1 | 2 | 2 | 3 | **5** |

### 関連 PR

- #85 (Phase A starter)
- #86 (Phase A 実装 / W5-Q0 観測機構稼働化)
- #87 (Phase B / W5-Q2 諮問 + B 採決)
- #88 (Phase C / subphase 3 ファイル改修)
- 本 PR (Wave 5 完遂記録 + archive + 振り返り儀式)

---

## v5.13.0 (released 2026-05-11)

**咀嚼プロトコル Wave 4 完遂**。Wave 3 minority opinion C 再諮問 + L0 対話パイプラインへの ECC 参照モード組込（Phase γ-i 業界叡智照合フック追加）。

咀嚼プロトコル系 metaskill 改修は Wave 1-3 (PR #76-#81) では PHILOSOPHY-CHANGELOG / COUNCIL-LOG / starter ファイル群に閉じていたが、Wave 4 から本 CHANGELOG にも完遂記録を残す経路を確立する（starter §3.4 規約）。

### Wave 4 Phase A (PR #82 merged)

- `delivery/CHEW-PROTOCOL-SPEC-wave4-starter.md` 起草 (307 行、Copilot 8 件 fix 反映後)
- ユーザー 3 不満（自立駆動の甘さ / Copilot レビュー耐性 / 多様な開発対応）を W4-Q1 + W4-Q2 議題に翻訳
- 諮問順序 W4-Q1 (哲学) → W4-Q2 (取込実装) を §3.1 で明文化（「先にガードレール、後で取込拡張」ユーザー方針）

### Wave 4 Phase B + Phase C (PR #83 merged)

**W4-Q1 採決** (`council-2026-05-11T19:00:00Z-w4qb01`):

- 議題: Wave 3 minority opinion C (第 8 条 4 段階モデル拡張) 再諮問
- 採決: A: 3 段階モデル維持、conf 0.65 (部分実装領域)
- weighted_score: A 4.56 (経営者+開発者) vs C 2.75 (哲学者)、差 1.81
- 哲学者 conf が Wave 3 の 0.85 → Wave 4 の 0.55 に下落（運用データ未蓄積 + 条文の薄さ原則からの逸脱リスク自認）
- minority C は Wave 5 再諮問温存（Council 経由率 ≤ 20% 観測条件）
- 哲学者第 3 の道 (D 案: 条文不変 + 観測項目強化) を stance A の補強として吸収

**W4-Q2 採決** (`council-2026-05-11T19:30:00Z-w4qb02`):

- 議題: L0 対話パイプラインへの ECC 参照モード組込
- 採決: B: 段階組込、全会一致 conf 0.78 (採決確定領域)
- weighted_score: B 7.70 (経営者+開発者+哲学者)、A/C は 0
- 3 ペルソナが異なる軸 (ROI / Shift Left / 哲学的バランス) で B 支持の多様性高品質
- subphase-l03〜l06 + scaffold-checklist は Wave 5 申し送り

**Phase C 実装**:

- `subphase-common-protocol.md` に Phase γ-i「業界叡智照合フック」節を新規追加 (46 行)
  - CTL 連動 (CTL 0 inactive / CTL ≥ 1 active で候補出力のみ)
  - 第 8 条 3 段階準拠 (観測 → 候補化 → 人間最終承認)
  - 自動採用なし、Phase δ で人間判断
- Phase δ 差分サマリに業界叡智照合候補項目を追加
- `history/PHILOSOPHY-CHANGELOG.md` に W4-Q1 結果追記（philosophy.md 本文不変）

### Wave 4 末振り返り儀式観測項目（5 種、必須化）

| # | 観測項目 | 由来 |
|---|---|---|
| 1 | Council 経由率 | W4-Q1 D 案吸収 |
| 2 | 3 段階運用実績 | W4-Q1 |
| 3 | minority C 再評価データ蓄積 | W4-Q1 |
| 4 | 業界叡智参照を経た SPEC の unedited merged 率 | W4-Q2 哲学者 concerns |
| 5 | 業界叡智照合フック起動回数 / 採用率 / 却下率 | W4-Q2 |

### Wave 5 申し送り

- minority C (4 段階 / CTL 連動ハイブリッド) 再諮問（Council 経由率 ≤ 20% 観測時）
- subphase-l03〜l06 + scaffold-checklist 個別改修（W4-Q2 stance A フル組込繰越）
- ECC-SURVEY 6 ヶ月再観察（2026-11-11 予定）
- 17 skill description / frontmatter 監査の進捗評価
- 残 3 hook event (UserPromptSubmit / Notification / SubagentStop) Wave 5 再評価

### archive

- `delivery/CHEW-PROTOCOL-SPEC-wave4-starter.md` → `history/wave4/CHEW-PROTOCOL-SPEC-wave4-starter.md`
- `delivery/CHEW-PROTOCOL-SPEC-wave3-starter.md` → `history/wave3/CHEW-PROTOCOL-SPEC-wave3-starter.md`（Wave 3 完了済繰越 archive）

### 関連 PR

- #82 (Phase A starter)
- #83 (Phase B + C 採決 + Phase γ-i フック実装)
- 本 PR (Wave 4 完遂記録 + archive)

---

## v5.10.0 (released 2026-05-08)

**minor 昇格**。**issue-pickup.yml body_check の type-aware 化（discussion-style 起票への対応）**。

### 動機

v5.9.0 merge 後、L0 spec-architect 起票の discussion-style issue (#47/#49/#53/#54/#57) が `issue-pickup.yml` body_check ステップで一律ブロックされる事象が観測された。原因は body_check が bug-style 3 セクション（再現手順/期待動作/受入条件）をハードコードしており、L0 起票 issue の構造（背景/論点/L0 対話記録/確定軸/実装スコープ）を識別できなかったため。

これは autonomous-drive 入力 Issue の **2 系統存在**（bug-style / discussion-style）が SPEC レベルで未定義だった規格漏れに起因する。Issue #61 の L0 spec-architect 対話で 5 軸（A〜E）を確定し、本 PR で実装。

### 変更

- **`.github/workflows/issue-pickup.yml`** — `body_check` ステップを type-aware に改修。`discussion` ラベル有無で必須セクション規格を分岐（discussion-style: L0 対話記録 + 実装スコープ / bug-style: 再現手順 + 期待動作 + 受入条件）。後方互換: `discussion` ラベルなし issue は現行 3 セクション必須維持
- **`templates/github-workflows/issue-pickup.yml.template`** — 同様の変更をミラー（利用者プロジェクトへの展開）
- **`.claude/skills/crosscut-issue-implementer/SKILL.md`** — §Issue 本文必須セクション規格 (v5.10.0) を新設。bug-style と discussion-style の必須項目・想定起票元・設計根拠・Quality Gate との整合を明文化
- **`.claude/skills/crosscut-issue-quality-gate/SKILL.md`** — §Issue Type 分岐ルール (v5.10.0) を追加。本 Gate と body_check の規格整合性を明記、12 軸の type 中立性を明示

### 反映元 Issue / Council

- Issue #61 (本 PR で close) — 本 v5.10.0 の根拠 Issue
- Issue #47/#49/#53/#54/#57 — 本ブロックで足止めされていた 5 件、merge 後に `needs-clarification` 除去 + `ready-for-ai` 再付与で再 trigger 可能（Issue #61 §post-merge 復旧手順）

### opt-in 領域該当性

`issue-pickup.yml` 改修 = `auto-merge-boundary.md §opt-in 領域`「autonomous-drive workflow 自身の改修」**該当**。本 PR は `human-review-needed` ラベル必須、人間レビュー後に解除して auto-merge 再評価。

### v5.10.0 第 3 弾: 16 skill 横断 description 診断 + 弱点 5 skill 改善 (2026-05-08)

skill-creator skill を起点に dialog-harness 配下 16 skill 全体の description 品質と progressive disclosure 適合性を静的横断診断し、trigger 精度の弱い 5 skill の description を手動改善した。

#### 診断（4 並列フォーク、broken reference 0 件）

`delivery/SKILL-CREATOR-AUDIT-v5.10.x.md` に集約。横断弱点パターン:

- **P0-1 `assets/` 不在症候群** (6 skill): 出力テンプレート (DELIVERY/HANDOFF/VERIFICATION/INTEGRATION/Issue 規格/council-weights) が SKILL.md inline または root 直下配置 → progressive disclosure 三段階が二段階に縮退
- **P0-2 trigger phrase 二極化** (5 skill): automation 経由前提で human trigger 欠落 / 「還流」が汎用すぎ / 本文に trigger 埋没。best of class は crosscut-verifier-drift と rtk-integration の symptom triggers パターン
- **P1 L0 兄弟 trigger 衝突** (spec-architect / onboarding / archeo-architect 間で「整理したい」「ドキュメント化」等が衝突)
- **P1 layer0-spec-architect 557 行 over-budget**（version history 75 行 + Pre-flight 反復が主因）
- **P1 layer1-independent-reviewer に references/ 不在**（214 行に inline checklist）
- **P1 issue-implementer ⇔ issue-quality-gate の規格双方向重複**（desync リスク）
- **P2 systematic**: version history bloat / orchestrator 雛形境界曖昧 / quality-gate 12 軸表が 11 行 / verifier-philosophy 5 本柱 vs 6 条混在 / workflow path 命名不統一

#### 改善（5 skill description 手動書き換え）

弱点上位 5 skill の `description` (frontmatter) を以下方針で改修:
- **crosscut-issue-implementer** — version history を 1 行圧縮、human-driven trigger 句 9 種追加、兄弟 skill の disambiguation を明示
- **crosscut-issue-quality-gate** — 「12 軸」を「12 項目（A-E + 7 ローマ数字）」と明示化、human trigger 9 種、3 つの発動契機、混同回避句
- **crosscut-feedback-loop** — 「還流」「フィードバック」の汎用語を「検証結果の還流先振り分け」に絞り込み、dispatcher との衝突回避句、CTL 0 動作を明示
- **layer0-spec-architect** — L0 三兄弟の責務境界を upfront 化、新規/継続/振り返りの代表 trigger 例を 8 種、archeo / onboarding / autonomous-dev / dispatcher との混同回避を明示
- **crosscut-autonomous-drive** — 本文 §起動条件 の trigger 句を frontmatter に昇格、deployment 専用スキルの境界を明示、issue-implementer / GitHub UI auto-merge との混同回避

#### 関連変更

- **skill-creator (`~/.claude/skills/skill-creator/`)** — Windows 互換パッチ適用: `subprocess.Popen` の cmd 解決を `shutil.which("claude")` に置換、`select.select` を Windows native では `queue.Queue + threading.Thread` 経由 pump に分岐。global skill のため他プロジェクトでも有効。Linux/macOS は select 経路を保持
- **eval set 保持** (5 skill 分計 90 件) — `skill-audit-workspace/eval-sets/` に保存、将来の trigger eval 自動最適化用に温存

#### Phase 3 自動最適化（run_loop.py）の制限事項

`run_loop.py` の自動最適化を試行したが、**「Skill / Read 以外のツールを最初に呼んだ時点で trigger=false」検知ロジック**（run_eval.py L207-208）と Auto モード下の手動操作の両立が現時点で困難なため、手動 description 改善（Phase 3'）に切り替え。eval set は将来の自動検証・description 最適化サイクルに温存。

#### opt-in / opt-out 領域該当性

`auto-merge-boundary.md §opt-out 領域`「skill description 改善」**該当**（破壊的変更なし、後方互換維持、すべて metadata 層の改修）。



L0 spec-architect 対話 (Issue #49) で 5 軸を確定し、最小セット (F1-F3 + A1 + B4 + G1) を実装:

- **`.github/workflows/gemini-review.yml`** — F1-F3: `includeTools` で read 系 + review-related write のみ expose、destructive tool (merge/close/delete) を除外 / A1: 必須コンテキストファイル (SPEC.md / DONT.md / philosophy.md) を workflow 事前注入 / B4: self-PR 検出を workflow 側で構造化 (PR author == PAT owner check)
- **`templates/github-workflows/gemini-review.yml.template`** — 同様の変更をミラー (G1: template 骨格整備、G2/G3 placeholder 規格は v5.11.0+ で整備予定)
- **後発候補**: B1/B2/B3 (プロンプト分離・動的選択) / C1-C3 (粒度階層化) / D1-D3 (Council 連携) / E1-E3 (出力規格・履歴) / A2-A4 (PR メタ・観測データ) は observation-driven で v5.11.0+ に温存

**opt-in 領域該当**: `gemini-review.yml` 改修 = `auto-merge-boundary.md §opt-in 領域`「autonomous-drive workflow 自身の改修」該当。同じ PR で `human-review-needed` ラベル必須。

### v5.10.0 第 3 弾: claude-code-action gh pr create fallback（Issue #51）

claude-code-action@v0 が direct_prompt の `gh pr create` 指示を default で skip する構造的穴を、workflow 側フォールバック step で塞ぐ:

- **`.github/workflows/issue-pickup.yml`** — 新 step `Create PR (fallback if claude-code-action skipped)` を `claude_impl` success 後に追加。`git branch -r` で `feat/issue-N-*` または `claude/issue-N-*` パターンを検出 → `gh pr list --head` で重複チェック → なければ `gh pr create` で自動作成
- **`templates/github-workflows/issue-pickup.yml.template`** — 同様の変更をミラー

これにより autonomous-drive の最終ステップ（PR 作成）が完全自律化される。本セッション内で発現した Type A 失敗（4 件: #47/#53/#54/#57 で branch あり PR なし）が今後は自動復旧する。

**opt-in 領域該当**: `issue-pickup.yml` 改修 = `auto-merge-boundary.md §opt-in 領域`該当。`human-review-needed` ラベル必須。

---

## v5.9.0 (released 2026-05-06)

> **記録規約**: 本 v5.9.0 は (1) cookpato バックアップサイクル retro (`samejima-ai/cookpato` PR #22) からの A1〜A5 汎用パターン取り込み + (2) auto-merge 人間承認モデルの opt-in→opt-out 反転 の 2 系列を含む。

**minor 昇格**。**cookpato retro A1〜A5 汎用パターン取り込みポートフォリオ確定 + auto-merge opt-out 反転**。

実装は別 PR / issue 群で進行（#53 A1 / #57 A2 / #54 A5 / PR #56 A4 / #46 follow-up A3）、本 PR は履歴層 F3 (COUNCIL-LOG.md 諮問エントリ + INTENT.md 取り込み計画) + auto-merge 反転の SPEC 改修 + 境界 SPEC 新設。

### Step 1: Council 諮問（案A 採用）

- `council-2026-05-06T04:42:00Z-a5port` (business / category=judgment / phase_3 / simple_conflict)
- final_weights: 経営者 4 / 開発者 4 / 哲学者 3
- recommended: 案A 採用案維持 (weighted_score 6.20 / 案 B/C/D 0.00)
- judgment_confidence: 0.75 / consensus_mode: auto_agree
- minority_opinion (third_way_excluded): 哲学者 = A3 を philosophy.md 第 8 条候補 (v6.0.0) として温存

### Step 2: 履歴層 F3 更新（本 PR #58）

- `history/COUNCIL-LOG.md`: 諮問エントリ append (append-only)
- `history/INTENT.md`: A1〜A5 取り込み計画 + v6.0.0 候補温存 + Council context 誤情報訂正記録

### 後発 Issue / 並走 PR

- #53 A1 / #57 A2 / #54 A5: discussion (L0 対話で軸確定中)
- PR #56 A4: 実装中 (`claude/dialog-harness-issue-V06Ko` branch、CI PASS、draft)
- #46 A3 follow-up: closed PR への comment 追記済 + 別 issue で実装予定

### 関連

- 起点 retro: `samejima-ai/cookpato` PR #22 `docs/retros/2026-05-05-backup-cycle.md`
- v6.0.0 候補温存: 「事故履歴という外部記憶への harness 依存を philosophy.md 第 8 条として昇格するか」を 2 件目 retro 出現時の再評価ゲートで本格検討

### Step 3: auto-merge 人間承認モデルの opt-in→opt-out 反転

PR #33 が 4 日間放置されている事例を起点に、auto-merge の人間承認モデルを反転する設計判断。「人間は多少のことは無関心、暗黙オートが基本」というユーザー発言を起点に Council 諮問を実施。

#### Council 諮問（C ハイブリッド採用）

- `council-2026-05-06T08:30:00Z-amrev1` (business / category=conception / phase_3 / unanimous)
- final_weights: 経営者 3 / 開発者 3 / 哲学者 5（conception カテゴリで 哲学者 +2 modifier）
- recommended: C ハイブリッド採用 (weighted_score 7.31 / 全 weight 11、100%)
- judgment_confidence: 0.80 / consensus_mode: auto_agree
- implementer_consent: agreed_with_modification（minority_opinion 由来 4 実装要件を SPEC に同梱）

#### 実装変更（4 系統）

- **workflow 反転**: `.github/workflows/auto-merge.yml` 条件 1 を whitelist (`auto-merge` ラベル必須) → blacklist (stop ラベル不在) に反転、template も同期
- **issue-pickup 改修**: `--label auto-merge` 自動付与を削除、opt-in 領域該当時のみ `--label human-review-needed`
- **境界 SPEC 新設**: `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md`（opt-in 領域 8 項目、opt-out 領域、stop ラベル定義、roll-back プロトコル、メタ承認機構）
- **philosophy 改修**: 第 7 条 §autonomous-drive §auto-merge デフォルト方針 を新設、P4 暴走時介入を stop ラベル群に拡張

#### 4 実装要件（minority_opinion 由来、SPEC 同梱）

1. **境界の SPEC 不変化**: `auto-merge-boundary.md` を一次情報源、AI が境界を動かせない構造
2. **roll-back プロトコル**: 6 ヶ月後検証ゲート（2026-11-06）、評価指標 4 項目で 1 件でも閾値超過なら opt-in 復帰
3. **既存 `auto-merge` ラベルの廃止**: 二重ラベル方式の腐敗回避、deployment では作成しない
4. **メタ承認機構**: PR1 placeholder 実装（手動運用）、月次「AI 判定漏れ率」5% 超で roll-back ゲート起動

#### 影響を受ける skill

- `crosscut-autonomous-drive` (v0.2.0): 境界 SPEC 一次情報源化、`auto-merge` ラベル廃止
- `crosscut-issue-implementer` (v0.3.0): opt-in→opt-out philosophy 反転、CTL 表更新
- `layer1-autonomous-dev` SKILL.md §7.5: PR 作成時の stop ラベル判定基準を新設
- `philosophy.md` 第 7 条: P4 暴走時介入の stop ラベル拡張、auto-merge デフォルト方針を新設

## v5.8.0 (released 2026-05-04)

> **記録規約**: 本 v5.8.0 が **9 例目正規適用**（autonomous-drive ループの最終 PR 作成のみ人間 P4 代行、それ以外は完全自律完遂）。

**minor 昇格**。**`crosscut-issue-quality-gate` skill 新設（12 軸 × 並列安全性）**。

Issue #46 の L0 spec-architect 対話セッション（2026-05-03〜04、Q1〜Q12 確定）で設計した 12 軸品質ガード機構を `anthropics/claude-code-action@v0`（Claude Code CLI）が autonomous-drive 9 例目として実装、PR #50 で master に merge。最終 `gh pr create` ステップのみ claude-code-action default 挙動で skip され人間 P4 代行（Issue #51 で別途追跡）、それ以外は完全自律完遂。

**Council 諮問なし**（L0 対話 Q1〜Q12 で全合意、複数案拮抗なし、不可逆操作なし）。**後方互換完全維持**（新 skill 不在でも DH ベースは通常動作）。

### Step 1: 設計（L0 spec-architect セッション）

- 12 軸 × 機械/AI ハイブリッド検証規格確定
- 観測性二層モデル（収集層 = 精緻、提示層 = 人間可読）
- 並列安全性軸（4 段階フィルター: scope/mutex/depends-on/AI 推論）
- DH メタへのフラクタル自己適用

### Step 2: 実装（autonomous-drive 9 例目）

- 新 skill `crosscut-issue-quality-gate` 本体 + references 7 + assets 1 = 計 9 ファイル
- `dh-upgrades/upgrade-spec-v5.8.0.md`
- `templates/github-workflows/issue-quality-gate.yml.template`
- `delivery/self-gate-check-AD010.md`（フラクタル原則の自己採点、12 軸中 8 PASS / 2 FAIL = 既知の自己違反として記録）
- 既存 7 ファイルへの参照追記（4 crosscut skill: dispatcher / implementer / council / spec-architect、+ 3 非 skill ファイル: philosophy.md / issue-pickup.yml.template / harness-verifier glossary.yml）

### Step 3: review feedback（合計 10 件解消）

- harness-verify failure 2 件（glossary.yml 未登録 + machine-checks.md 誤検出）
- gemini-review 1 件（concurrency ハードコード → SPEC 改訂で対応）
- Copilot review 6 件（permissions / SLACK_WEBHOOK / GH_REPO / lockfile / notify ガード / .gemini/ コミット）
- post-merge gemini 1 件（References 件数誤記、本 housekeeping で対応）

### Step 4: 観測駆動の SPEC 改訂（v5.8.x 候補温存）

- **workflow-level concurrency 制約**: GitHub Actions の `concurrency` block が `steps.*` 参照不可と判明 → scope 動的判定は v5.8.x patch で jobs 内自前実装 or 静的 contains chain で本実装予定
- **claude-code-action glossary 更新忘れ**: harness-verify で事後検出 → 軸 vii「ドキュメント波及」改良候補
- **review timing 競合**（PR #48 で観測）: 8 例目の手動 merge 譲歩の主因 → 軸 ix「並列安全性」周辺事象として記録

### 後発 Issue / 温存項目

- Issue #51: claude-code-action `gh pr create` skip 問題（autonomous-drive 最終ステップの構造的穴）
- Issue #49: gemini-review 入力・プロンプト規格再設計（draft、別 L0 セッションで継続）
- Quality Gate 軸 viii「テスト粒度」改良: 本番前 smoke test + workflow YAML expression 制約検証

## v5.7.2 (released 2026-05-04)

> **記録規約**: PR draft / ready-for-review 中は `(in progress)` で記録、merge 時に `(released YYYY-MM-DD)` 化。本 v5.7.2 が **8 例目正規適用**。

**patch 昇格**。**`anthropics/claude-code-action@v0` の OIDC token 取得失敗 bug 修正**。

Issue #46（v5.8.0 候補 `crosscut-issue-quality-gate` 設計）を実装トリガーとして v5.7.1 機構の初の本番テストを実施したところ、`Failed to setup GitHub token: Error: Could not fetch an OIDC token. Did you remember to add 'id-token: write' to your workflow permissions?` で workflow が exit 1 で終了。`anthropics/claude-code-action@v0` が OIDC で token 取得を試みるが、`issue-pickup.yml` の `permissions:` ブロックに `id-token: write` が含まれていなかった。v5.7.1 で gemini-cli → Claude Code CLI 切替時の追加漏れ。

**Council 諮問なし**（自明な single-line bug fix、複数案拮抗なし、不可逆操作なし）。**後方互換完全維持**（permission 追加は既存挙動に影響しない）。

### Step 1: 履歴層

- 本セクション
- INTENT.md v5.7.2 設計意図
- REGIME-LOG.md v5.7.2 patch 判定
- ARCH-DECISIONS.md AD-030 追加（OIDC permission 追加、v5.7.1 bug 修正記録）

### Step 2: workflow + template

- `.github/workflows/issue-pickup.yml` `permissions:` に `id-token: write` 1 行追加
- `templates/github-workflows/issue-pickup.yml.template` 同上

### Step 3: 動作確認（merge 後の actual）

- Issue #46 の `in-progress` ラベルを除去 + `ready-for-ai` 再付与で再 trigger
- `claude-code-action@v0` が OIDC token 取得 → 実装本体起動 → PR 作成まで完遂を確認
- 副次目的: 本 PR 自身が **v5.7.2 fix の有効性検証 + Issue #46 (v5.8.0) の autonomous-drive 完遂** のダブルテストを兼ねる

## v5.7.1 (released 2026-05-03)

> **記録規約**: PR draft / ready-for-review 中は `(in progress)` で記録、merge 時に `(released YYYY-MM-DD)` 化（v5.5.0 で確立、本 v5.7.1 が **7 例目正規適用**）。同 PR で v5.7.0 (in progress) → (released 2026-05-03) 化を housekeeping として同梱。

**patch 昇格**。**実装エージェント方式の見直し（gemini-cli → Claude Code CLI メイン化、AD-026 訂正）**。

ユーザー要請「実装は Anthropic Claude Code CLI で実行したい、サブスクで稼働、Gemini はフォールバック」を起源として、L0 spec-architect セッションで策定された HANDOFF (`delivery/HANDOFF-v5.7.1-claude-code-pivot.md`) に基づく実装。

**新事実発見**: Anthropic Pro/Max サブスクリプション + `CLAUDE_CODE_OAUTH_TOKEN` 経由で Claude Code CLI を GitHub Actions で **追加 API 課金なし** で稼働可能。v5.7.0 AD-026「Anthropic API 回避で gemini-cli 採用」の前提が変わった → AD-029 で訂正。

**後方互換完全維持**: philosophy.md 改訂なし、既存 SKILL.md セクション番号不変、利用者プロジェクトへの強制配布なし。**Council 諮問なし**（11+7 論点全て対話で合意、複数案拮抗なし、confidence ≥ 0.7）。

### Step 1: 履歴層 + housekeeping

- 本セクション
- INTENT.md v5.7.1 設計意図
- REGIME-LOG.md v5.7.1 patch 判定
- ARCH-DECISIONS.md AD-029 追加（Claude Code CLI 採用、AD-026 訂正記録）
- v5.7.0 (in progress) → (released 2026-05-03) 化同梱

### Step 2: crosscut-issue-implementer skill 改修

- SKILL.md frontmatter description + 本文の実装エージェント記述を「Claude Code CLI メイン + gemini-cli フォールバック」へ
- references/triage-protocol.md: AI triage は gemini-cli メイン継続を明文化
- references/setup-checklist.md: `CLAUDE_CODE_OAUTH_TOKEN` 取得手順追加（Anthropic Console、Pro/Max サブスクリプション前提）

### Step 3: workflow + template

- `.github/workflows/issue-pickup.yml`: `anthropics/claude-code-action@v0` 統合 + `CLAUDE_CODE_OAUTH_TOKEN` 認証 + 失敗時 `pickup-failed` label + notice（フォールバック自動化なし、人間 P4 判断）
- `templates/github-workflows/issue-pickup.yml.template`: 同等改訂

### Step 4: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 5 検査 PASS
- `delivery/SELF-VERIFICATION-v5.7.1.md` 作成
- 本 PR は ready-for-review + `auto-merge` label で autonomous-drive loop **7 例目** として投入

## v5.7.0 (released 2026-05-03)

> **記録規約**: PR #44 (2026-05-03 merged) の `(in progress)` 状態を本 v5.7.1 patch に同梱して `(released 2026-05-03)` 化（**7 例目正規適用**）。housekeeping を独立 PR にせず同梱の運用が継続的に定着。

> **記録規約**: PR draft / ready-for-review 中は `(in progress)` で記録、merge 時に `(released YYYY-MM-DD)` 化（v5.5.0 で確立、本 v5.7.0 が 6 例目正規適用）。同 PR で v5.6.0 (in progress) → (released 2026-05-03) 化を housekeeping として同梱。

**minor 昇格**。**autonomous-drive 入口側（Issue → AI pickup → 実装開始）本格稼働 + Issue 選別機構**。

ユーザー（ひでさん）の根源要請「Bを考えよう（自前 workflow 実装）」+ 「Issue 選択は開発品質を決めると言って過言ではない」を起源として、L0 spec-architect セッションで策定された HANDOFF (`delivery/HANDOFF-v5.7.0-issue-pickup.md`) に基づく実装。

**実装方式**: gemini-cli 流用（既存 GEMINI_API_KEY、追加コスト 0、Anthropic API 回避）。
**Council 諮問**: なし（11 論点全て対話で合意、起動条件未満）。

**後方互換完全維持**: dev_mode `autonomous` + `autonomous_scope: full` のみで enable。利用者プロジェクトには配布されない（template 配置のみ）。

### Step 1: 履歴層 + housekeeping

- 本セクション
- INTENT.md v5.7.0 設計意図
- REGIME-LOG.md v5.7.0 minor 昇格
- ARCH-DECISIONS.md AD-026 (実装方式) / AD-027 (current_focus) / AD-028 (Issue 選別 3 段階フィルター)
- v5.6.0 (in progress) → (released 2026-05-03) 化同梱

### Step 2: spec-architect 拡張 - current_focus 軸新設

- meta-spec-template.md: REGIME.md テンプレに `## current_focus` セクション追加（type / target / since / priority）
- regime-assessment.md: current_focus 判定（β 半自動 + γ ブランチ命名フォールバック）追加
- dialog-questions.md: current_focus 確認質問追加
- dev-env-spec.md: Level C に current_focus と Issue pickup の連動表追加

### Step 3: crosscut-issue-implementer skill 拡張

- SKILL.md 全面改訂（claude-code-action 前提 → gemini-cli 流用、3 段階フィルター、AI triage、circuit breaker）
- references/issue-filter-spec.md 新設（label / author / 本文 / current_focus 整合の filter ロジック）
- references/triage-protocol.md 新設（gemini-cli AI triage 二次判定）
- references/circuit-breaker-spec.md 新設（日次5/月次50 + 緊急停止）

### Step 4: workflow + template

- `.github/workflows/issue-pickup.yml` 新設（dialog-harness 自身に deploy、gemini-cli base）
- `templates/github-workflows/issue-pickup.yml.template` 新設（利用者展開用、placeholder 化）
- `spec-architect/references/autonomous-drive-deployment.md` に入口側 deployment 手順追記

### Step 5: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 5 検査 PASS（新用語 + frontmatter + path 整合性）
- `delivery/SELF-VERIFICATION-v5.7.0.md` 作成
- 本 PR は ready-for-review + `auto-merge` label で autonomous-drive loop 6 例目として投入

### v5.7.x / v6.0.0 候補として温存

- gemini-cli 実装エージェントの品質観測（fail 率測定、必要なら Council 起動でフォールバック判断）
- 新 sub-skill `crosscut-issue-drafter`（ブレスト → Issue 化支援、philosophy 第 7 条 P2 強化）
- destructive change detector / circuit breaker の実機構（v5.6.0 から累計後送中）
- ALLOWED_AUTHORS 動的化

## v5.6.0 (released 2026-05-03)

> **記録規約**: PR #43 (2026-05-03 merged) の `(in progress)` 状態を本 v5.7.0 patch に同梱して `(released 2026-05-03)` 化（6 例目正規適用）。housekeeping を独立 PR にせず本 PR に同梱の運用が継続的に定着。

> **記録規約**: PR draft / ready-for-review 中は `(in progress, target YYYY-MM-DD)` で記録、merge 時に `(released YYYY-MM-DD)` 化（v5.5.0 で確立、本 v5.6.0 が 5 例目正規適用）。同 PR で v5.5.3 (in progress) → (released 2026-05-03) 化を housekeeping として同梱。

**minor 昇格**。**autonomous-drive 標準化 + DH AI 組織論明文化**。

L0 spec-architect セッションで策定された HANDOFF（`delivery/HANDOFF-v5.6.0-autonomous-drive.md`）に基づく実装。ユーザー（ひでさん）の根源要請「自律駆動を L0 に記録、メタスキル開発」と「DH AI 組織は 4 役割 + サポートのみで完遂可能」の宣言を制度化する。

Council 諮問 `council-2026-05-03T08:30:00Z-adrv02` で β 止揚採用：deployment skill 1 つのみ新設、guardian は v5.6.x patch 温存。

**後方互換完全維持**: philosophy.md 既存 6 条改訂なし（第 7 条追加のみ）、既存 spec-architect 対話フロー不変、利用者プロジェクトへの強制配布なし。利用者プロジェクト本体には配布されない（DH 自身の運用標準化）。

### Step 1: philosophy.md 第 7 条新設「AI 組織論（4 役割 + サポート構造）」

`.claude/skills/layer0-spec-architect/references/philosophy.md` 第 7 条追加：
- **4 役割属性**: L0 設計 / L1 実装 / L2 統括 / Council 判断
- **サポート定義**: crosscut-* 非 council 系 + sub-agent は 4 役割のいずれかから呼ばれる
- **Person 責務 (P1〜P4)**: 発案 / ブレスト / 事後確認・評価 / 暴走時介入
- **第 6 条 H カテゴリとの関係**: H = 判断種別、P = 責務種別、両者は直交 2 軸（ラベル番号は偶然一致）
- **「あらゆる開発に対応」汎化性主張**: メタスキルとして他プロジェクトへ展開可能

既存 6 条は不変。

### Step 2: spec-architect 改修（autonomous_scope 軸 + Level C 追加）

- `SKILL.md`: dev_mode `autonomous` 本格定義 + `autonomous_scope`（full / merge_gated / custom）追加、§6 開発環境構築に Level C 追記
- `references/dialog-questions.md`: 自律駆動の度合い質問追加（フルオートデフォルト）
- `references/regime-assessment.md`: dev_mode `autonomous` 発動条件 + LC 連動規則
- `references/dev-env-spec.md`: 「Level C: AI 自律運用」新設
- `assets/meta-spec-template.md`: REGIME.md テンプレに `## autonomous_scope` セクション追加
- `references/autonomous-drive-deployment.md` 新設: deployment 対話レベルガイド + crosscut-autonomous-drive 起動タイミング規定

### Step 3: template 配置 + crosscut skill 新設（β 止揚採用）

- `templates/github-workflows/` 新設
  - `gemini-review.yml.template`（dialog-harness 自身の `.github/workflows/gemini-review.yml` から汎化）
  - `auto-merge.yml.template`（同上、`auto-merge.yml` から汎化）
  - placeholder 規約: `${REPO_OWNER}` / `${REPO_NAME}` / `${ALLOWED_AUTHORS}` / `${VERIFIER_JOB_NAME}` / `${SCOPE_PATHS}`
- `.claude/skills/crosscut-autonomous-drive/` 新設（deployment 専念）
  - `SKILL.md`: サポート skill としての責務定義（template 取得 → placeholder 置換 → `.github/workflows/` 配置 → label 作成 → secrets 確認）
  - `references/placeholder-spec.md`: placeholder 一覧 + 規約
  - `references/setup-checklist.md`: label / secret / PAT 設定手順

### Step 4: 履歴層更新

- `history/CHANGELOG.md` 本セクション + v5.5.3 (released 2026-05-03) 化
- `history/INTENT.md` v5.6.0 設計意図セクション
- `history/REGIME-LOG.md` v5.6.0 minor 昇格判定（M2 / LC=2 / claude-opus-4-7）
- `history/ARCH-DECISIONS.md` AD-023（autonomous-drive 標準化）/ AD-024（philosophy 第 7 条新設）/ AD-025（autonomous_scope 軸）
- `history/COUNCIL-LOG.md` `council-2026-05-03T08:30:00Z-adrv02` エントリ append

### Step 5: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 5 検査 PASS（D4 整合性維持確認、新 skill `crosscut-autonomous-drive` の frontmatter 検査 +1 を含む）
- `delivery/SELF-VERIFICATION-v5.6.0.md` 作成（L0 §7.4 自己検証の 5 項目 + philosophy 第 7 条と既存 6 条の整合性確認 + 4 役割組織論と既存 skill 配置の整合性確認）
- 本 PR は ready-for-review + `auto-merge` label で自律 loop に投入（PR #42 で実証された経路の再運用）

### v5.6.x / v6.0.0 候補として温存

- destructive change detector（diff threshold / DELETE-heavy）
- circuit breaker（5 連続 fail 自動停止）
- ALLOWED_AUTHORS 動的化（複数 contributor 体制で必要時）
- adrv01-Ph2（独立観測機構、harness-verifier 同型 crosscut skill）
- crosscut-verifier-philosophy 本実装（v5.0.0 から累計後送中、第 7 条で組織論が確定したので連動可能）
- DH AI 組織論の汎化性主張テスト（4 役割で実 N=3 別プロジェクトをカバーできるか観測）

## v5.5.3 (released 2026-05-03)

> **記録規約**: PR #42 で merge され、本 v5.6.0 patch（PR 想定）に同梱する形で `(in progress)` → `(released 2026-05-03)` 化。5 例目正規適用に該当。本 PR ハンドリング規約の確立（v5.5.0 起源）後、housekeeping を本リリースに同梱して独立 PR を増やさない運用が定着しつつある（v5.5.2 → v5.5.3 にて 1 例、本 v5.5.3 → v5.6.0 にて 2 例目）。

patch 昇格。**autonomous-drive 機構の出口側として label opt-in による PR 自動 merge workflow を新設**。

DH の crosscut-issue-implementer から続く autonomous-drive 機構（issue → AI 実装 → 多層レビュー → 自動 merge）の最終段階。今までは人間が merge ボタンを手押ししていた部分を、明示的な opt-in（label `auto-merge`）+ 多層検証（harness-verify + gemini-review + reviewDecision）通過時のみ自動化する。

**Operational behavior 追加（opt-in、後方互換完全維持）**: label が無い PR は従来通り手動 merge を要する（既定挙動の変更なし）。label 付与時のみ条件評価 → 全 pass で自動 merge。利用者プロジェクトには配布されない。

### Step 1: auto-merge.yml workflow 新設

`.github/workflows/auto-merge.yml`（160 line）。trigger event:
- `pull_request`: labeled / unlabeled / opened / synchronize / ready_for_review / reopened
- `pull_request_review`: submitted / dismissed
- `check_suite`: completed

評価条件（全て満たす場合のみ squash merge）:

| # | 条件 | 目的 |
|---|---|---|
| 1 | label `auto-merge` 付き | 明示的な人間の GO サイン（opt-in） |
| 2 | non-draft | 編集途中を merge しない |
| 3 | author が `ALLOWED_AUTHORS` (env) に含まれる | 信頼境界（現状: `samejima-ai` のみ） |
| 4 | `harness-verify` (job: verify) が走った場合 SUCCESS、走らなかった場合（paths 外）skip 扱い | 構造的検証通過（paths filter 起因の永久 pending 回避） |
| 4.5 | 最低 1 つの verifier (harness-verify or gemini-review) が SUCCESS で走っている | zero-check auto-merge を防ぐ guard |
| 5 | `gemini-review` (job: review) が走った場合 SUCCESS、走らなかった場合（paths 外）skip 扱い | 異質モデル独立 critic の通過 |
| 6 | `reviewDecision` が CHANGES_REQUESTED でない | 指摘解消待ちで block |
| 7 | PR state が OPEN | closed / merged を再 merge しない |

非該当 PR は notice 出力で skip（red CI にしない）、merge 時は `--squash --delete-branch`。

加えて pre-check として `GH_REVIEW_PAT` availability check を実装（fork PR / secret 欠落環境で red CI を防ぐ）。check_suite event 経由で SHA に複数 open PR が紐付く場合は merge target 曖昧として skip + warning（非決定性回避）。

### Step 2: 設計判断の記録

| 判断 | 理由 |
|---|---|
| GitHub native auto-merge ではなく workflow で直接 merge | branch protection 設定変更不要、ロジック一元管理、運用観測（notice ログ）が一元化 |
| PAT (`GH_REVIEW_PAT`) を使用 | workflow の auto GITHUB_TOKEN は別 workflow を trigger できない（無限ループ防止）が、本 workflow は別 workflow を起動しない用途 + PAT で post-merge 動作観測を統一 |
| `ALLOWED_AUTHORS` env に明示 hardcode | spec 改修扱い、変更時は L0 spec-architect 経由で REGIME.md と整合確認、不可視拡張防止 |
| harness-verify / gemini-review 両者を「走った場合のみ必須」+ 最低 1 verifier guard | 両 workflow とも paths filter があり全 PR では走らない。永久 pending を回避しつつ zero-check auto-merge も防ぐ（Copilot review #42 で初版「harness-verify は paths filter なし」事実誤認を訂正） |
| GH_REVIEW_PAT availability pre-check + multi-PR 検出 skip | fork PR / secret 欠落で red CI 化を防ぐ + check_suite head SHA に複数 PR 紐付き時の非決定性回避（Copilot review #42 line 89 対応） |

### Step 3: 履歴層更新

- `history/CHANGELOG.md` 本セクション
- `history/INTENT.md` v5.5.3 セクション追加（autonomous-drive パイプラインとの位置づけ）
- `history/REGIME-LOG.md` v5.5.3 patch 判定記録
- `history/ARCH-DECISIONS.md` AD-022 追加
- v5.5.2 (in progress) → (released 2026-05-03) 化（同梱）

### Step 4: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 PASS（D4 整合性維持）
- 本 PR 自身は `auto-merge` label を付けない運用（初回投入の動作確認は人間 merge で実施、信頼運用は次 PR から開始）
- 次 PR で初めて auto-merge label を試験投入し、workflow が期待通り条件評価 → merge 実行することを確認する 4 例目運用

## v5.5.2 (released 2026-05-03)

> **記録規約**: 本セクションは PR #41 draft 中は `(in progress, target 2026-05-03)` で記録され、PR #41 merge (2026-05-03) で `(released 2026-05-03)` 化されるべきだったが follow-up PR が遅延した。本 v5.5.3 patch（PR #42 想定）に同梱する形で正規化（4 例目正規適用に該当）。

patch 昇格。**v5.5.1 で gemini-review 動作確立に伴い導入された診断機構の縮退**。

v5.5.1 PR #40 で gemini-review が動作完了 + 副次目的（独立 critic 機能の検証）が達成されたため、診断目的の暫定機構（`continue-on-error: true` / `GEMINI_DEBUG: "true"` / Diagnostics step 2 件）を削除。

**Operational behavior 変更（意図的、Copilot review #41 line 13 で指摘）**: `continue-on-error: true` 削除により、transient な Gemini/MCP 失敗が以前は silent success として記録されていたが、本 patch 以降は **PR check が hard-fail (red CI)** になる。本 repo のレビュー機構として fail を fail として可視化する設計判断（philosophy.md §3 情報純度の系）。

PAT 未設定環境での noisy red を避けるため `GH_REVIEW_PAT` の availability check を新設し、未設定時は GEMINI_API_KEY 不在時と同様にクリーン skip する（Copilot review #41 line 121 対応）。

self-PR の APPROVE 制約は **API レスポンスで判別する fallback 方式**で記述（v5.5.1 prompt と同形式）。author が PAT owner と同一かを workflow で判定するロジックは導入しない（unenforced repository assumption を排除、Copilot review #41 line 184 対応）。

利用者プロジェクトには配布されない。

### Step 1: gemini-review.yml の diagnostics 縮退

- **削除**: `Diagnostics — runner / docker / GitHub MCP server reachability` step（v5.5.1 で追加、原因 A 切り分け用）
- **削除**: `Diagnostics — gemini_review step outcome` step（v5.5.1 で追加、post-step outcome 確認用）
- **削除**: `Run Gemini PR review` の `continue-on-error: true`（診断時の fail 通過用、本 patch で fail を可視化）
- **削除**: `Run Gemini PR review` の `id: gemini_review`（post-step が消えたため不要）
- **削除**: `GEMINI_DEBUG: "true"` env（diagnostic 過程で必要だったが本番では token 消費過多）
- **保持**: `Upload gemini-artifacts (stdout / stderr / telemetry)` step（low cost で将来 debug 必要時に有用）
- **保持**: `actions/checkout` の `fetch-depth: 0`（本 repo の小ささから cost 極小、cli 内部 diff 計算が必要な場合に効く）
- **保持**: settings JSON の `tools.core` / `mcpServers.github.includeTools` 不在（α パッチで判明した tool exposure 阻害除去）

### Step 2: GH_REVIEW_PAT availability check 新設

`continue-on-error: true` 削除に伴い PAT 未設定で MCP server に空 token を渡すと review_write が hard-fail する事象を防ぐため、`GEMINI_API_KEY` と同形式の早期 availability check を追加。両 secret が available の場合のみ `Run Gemini PR review` / `Upload gemini-artifacts` を実行する（Copilot review #41 line 121 対応）。

### Step 3: prompt self-PR fallback 方式の維持

self-PR APPROVE 拒否は **API レスポンスで判別する fallback 方式**で prompt に記述（v5.5.1 と同形式）。author が PAT owner と同一かを workflow 側で事前判定するロジックは導入しない理由：
- author = `${{ github.event.pull_request.user.login }}` と PAT owner の比較には PAT owner の事前知識が必要（unenforced assumption）
- 他 maintainer が同 repo に PR を作った場合、APPROVE は実際に通るので強制 COMMENT downgrade は誤った検閲となる
- v5.5.2 patch 草案でハードコード化を試みたが Copilot review #41 line 184 で指摘 → API 応答ベースの fallback に revert

prompt の「出力形式」「必須実行プロトコル」セクションは v5.5.1 と同様に APPROVE/COMMENT/REQUEST_CHANGES 全選択肢を提示し、self-PR で API 拒否時のみ COMMENT fallback と明記。

### Step 4: settings JSON のコメント更新（security 注 追加）

`includeTools` 不在で github-mcp-server の **全 tool が model に expose** される（read 系のみならず write/destructive 系含む）。本 repo は信頼済み author 前提で許容するが、tool 名の正しい形式判明後の絞り込みを v5.5.x 候補として明記。

### Step 5: 履歴層更新

- `history/CHANGELOG.md` 本セクション
- `history/INTENT.md` v5.5.2 セクション追加
- `history/REGIME-LOG.md` v5.5.2 patch 判定記録
- `history/ARCH-DECISIONS.md` AD-021 追加

### Step 6: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 PASS
- gemini-review が新 prompt + diagnostics 削減後の構成で正常動作することを本 PR で検証
- 本 PR description / CHANGELOG / verification 結果の整合を gemini-review 自身が独立 critic として確認する 3 例目運用

## v5.5.1 (released 2026-05-02)

> **記録規約**: 本セクションは PR #39 の draft 中（実際は ready-for-review 開始）に書かれ、`(in progress, target 2026-05-02)` で記録されていた。本 patch（PR #39 マージ後）で `(released 2026-05-02)` へ更新。「PR draft 中は `(in progress)` / マージ時に `(released YYYY-MM-DD)` 化」フローは v5.5.0 で正規適用が確立し、本 v5.5.1 は **2 例目の正規適用**にあたる。

patch 昇格。**v5.5.0 で温存された Phase γ 残 2 件のうち、先行宣言 4（ストラングラー・フィグ / Branch by Abstraction の射程外宣言）を本実装**。先行宣言版（4 行記述）から本実装版（射程外要素列挙 / 援用と全体採用の境界線 / L1/L2 禁止規約 / v6.0.0 昇格の観測トリガー / 整合性ガード）へ昇格。先行宣言 5（失敗アンチパターン早期検出）は引き続き温存（v5.5.x patch / v5.6.0 候補）。

CHANGELOG/INTENT/REGIME-LOG/ARCH-DECISIONS の各履歴記録を伴うが、SK 本文の機能変更ゼロ（明文化のみ、後方互換完全維持）。利用者プロジェクトには配布されない。本 patch は gemini-review GitHub Action（PR #37/#38 で導入）の独立レビュー機能を実運用で初めてテストする副次目的を兼ねる。

### Step 1: handoff-to-evaluator.md 拡充

- ステータスヘッダ: 「Phase γ コア 3 件本実装版」→「Phase γ コア 3 件 + 先行宣言 4 本実装版」
- ロードマップ表: γ 残 2 件 → γ 残 1 件（先行宣言 5 のみ）+ v5.5.1 patch 行を新規追加
- 実装ステータス記述: コア 3 件 + 先行宣言 4 を v5.5.1 で本実装と明記
- 先行宣言 4 セクション本体: 4 行記述 → 5 サブセクション（(a) 射程外要素の明示列挙 / (b) 援用と全体採用の境界線 / (c) L1/L2 禁止規約 / (d) v6.0.0 昇格の観測トリガー / (e) 整合性ガード）

### Step 2: 履歴層更新

- `history/CHANGELOG.md` 本セクション
- `history/INTENT.md` v5.5.1 セクション追加（先行宣言 4 本実装の設計意図）
- `history/REGIME-LOG.md` v5.5.1 patch 判定記録（M2 / LC=1 / claude-opus-4-7、minor 昇格不要）
- `history/ARCH-DECISIONS.md` AD-020 追加（先行宣言 4 本実装、明文化のみ機能変更なし）

### Step 3: 自己検証 + 献上

- `python harness-verifier/verify.py` 全 PASS（D4 整合性維持確認、5 検査全項目）
- gemini-review GitHub Action の発火条件（`.claude/skills/**` + `history/**` 改変、non-draft PR）を満たす最初の PR として運用テストを兼ねる
- ルートに ready-for-review PR (#39) を作成、Copilot review からの 2 件指摘（(b) テーブル矛盾 / AD-020 「3 箇所」事実誤認）に commit `fce6b9d` で応答

### Step 4: 副次目的の運用テスト結果と PR 内追加対処（gemini-review）

PR #39 内で gemini-review GitHub Action の独立レビュー機能を 4 run（commit `1275e70` / `fce6b9d` / `cb72f0e` / `6969a21`）に渡って実行。**全 4 run で `review` job は `success` 終了したが、レビュー投稿は 0 件**（webhook 監視 + `pull_request_read get_reviews` API 確認）。Copilot review は同期間に正常稼働しており、PR 機能側の問題ではない。

PR 内で以下の Shift Left 対処を実施：

- commit `cb72f0e`: `gemini-review.yml` に診断機構追加（runner / docker / GitHub MCP server reachability の事前確認、`GEMINI_CLI_VERBOSE` / `DEBUG` env、`continue-on-error: true` + `id: gemini_review`、prompt 末尾「必須実行プロトコル」、post-step outcome 出力）
- commit `6969a21`: MCP server に渡す `GITHUB_PERSONAL_ACCESS_TOKEN` を auto `secrets.GITHUB_TOKEN`（`ghs_*` GitHub Apps token）から `secrets.GH_REVIEW_PAT`（Fine-grained PAT, Pull requests: read+write / Contents: read）に切替（原因 A: GitHub Apps token の write 制限仮説への対処）

PAT 切替（commit `6969a21`）の効果検証は merge 前に webhook で確認できず、本 v5.5.1 release 時点で **未検証**。検証は次 PR（本 `(released)` 化 patch 自身）で実施し、結果を patch 内 `## v5.5.x` 節または `delivery/SELF-VERIFICATION-v5.5.x.md` に追記する。診断機構（`continue-on-error` / verbose env / 診断 step 群）は **PAT で 1 度の正常投稿を確認した後** に縮退または削除する。

## v5.5.0 (released 2026-05-02)

> **記録規約**: 本セクションは PR #34 が draft 中に書かれ、`(in progress, target 2026-05-02)` で記録されていた（Copilot review #34 line 8 の指摘で recorded-during-draft の妥当性が再確認された）。本 patch（PR #34 マージ後）で `(released 2026-05-02)` へ更新。「PR draft 中は `(in progress)` / マージ時に `(released YYYY-MM-DD)` 化」フローは旧監査 `delivery/D4-AUDIT-2026-04-30.md` M-1 で**問題提起**され（同節「ルールが未定義」と明示）、v5.4.0 リリース時に過去エントリ（v5.0.0〜v5.3.0）一括正規化として**実装**されて以降の運用慣行として確立。本 v5.5.0 patch はその慣行の最初の正規適用例にあたる。マージ前後の history が PR 状態と整合する。

minor 昇格。**(I) adrv01-Ph1 = AI 自己申告閾値の Council 連動明文化**（既存 `confidence < 0.6` 機構流用、コスト 0）+ **(II) Phase γ コア 3 件 = L1 自己検証/独立検証への意図合致軸追加**（4 軸化、起点問題=リファクタ取りこぼしの構造解決）。
PR #33 ブレスト結晶 `delivery/AUTONOMOUS-DRIVE-BRAINSTORM-2026-05-02.md`（adrv01/02/03 全合意成立）を起源とする。後方互換維持（v5.0.0〜v5.4.0 と同パターン）。利用者プロジェクトには配布されない。

`crosscut-verifier-philosophy` 本実装は本リリース対象外（v5.5.x patch / v5.6.0 へ再々々後送、v5.0.0 から累計 5 リリース後送中）。
Phase γ 先行宣言 4（ストラングラー射程外宣言）+ 5（失敗アンチパターン早期検出）は本リリース対象外（v5.5.x patch / v5.6.0 候補）。
adrv01-Ph2（独立観測機構新設、新規 crosscut-* skill）は v5.6.0 候補。

### Step 0: L0 spec-architect 起動 + 振り返り儀式 + Council 諮問

- LC=1（v5.4.0 リリースから 1 日経過、CHANGELOG 更新 < 30 日）/ M2 標準モード判定
- 振り返り儀式レベル 2（機能追加示唆検出）/ F1 過去文脈サマリ提示 / F2 認識ズレ検出 / F3 履歴更新予告
- Council `vrfy01`（v5.5.0 着手前 DH 自体実装妥当性検証スコープ判定）: V-1 狭義 / V-2 中庸 / V-3 広義 の 3 候補拮抗 → recommended V-1、`agreed_with_modification`（β止揚採用：V-1 + 検証を v5.5.0 SPEC 化に内包）
- V-1 検証完了: adrv01-Ph1 / Phase γ 双方の依存機構（Council confidence 機構 / L1 §自己検証構造）が構造的に完備、拡張ポイント特定済み

### Step 1: Phase A — adrv01-Ph1 改修

- `crosscut-council/SKILL.md §自己申告プロトコル` 新節（confidence < 0.6 を Council 起動の正式トリガーとして明文化、内部完結禁止、自己申告 = 一次入力 + Council = 二次検証の二相構造）
- `crosscut-council/references/pre-check.md` §scope/PR 境界 vs 新規思想 の判別シナリオ（Copilot review #34 feedback、category 誤選択の Shift Left 防止、判別チェックリスト追加）
- `crosscut-council/references/consensus-protocol.md` §エッジケース「escalated 経路での合意成立」明文化（vrfy01 事例由来）+ §自己申告 → Council 起動の hook 経路（v5.6.0 Ph2 で本実装の先行宣言）

### Step 2: Phase B — Phase γ コア 3 件本実装

- `layer0-archeo-architect/references/handoff-to-evaluator.md`: 先行宣言版 → コア 3 件本実装版へ拡充（ロードマップ表 / I/O 契約 / 改修対象ファイル状態を ✅ 実施済みに更新）
- `layer1-autonomous-dev/references/inferential-sensor-v2.md` §第4層: 意図合致軸の起動条件（`refactor-intent-map.md` 存在時のみ）+ refactor_directive 別判定ルール（preserve 承認テスト / restructure 自動照合ループ / discard_and_redesign）追加
- `layer1-autonomous-dev/SKILL.md §6 自己検証`: 承認テスト生成プロトコル + 自動照合ループプロトコル追加
- `layer1-independent-reviewer/SKILL.md`: 評価軸 3→4 軸化、§5.4 意図合致チェックステップ追加、判定ルール 4 軸対応
- `layer1-autonomous-dev/references/delivery-format.md`: 推論的センサー判定に意図合致追加 + 意図合致検証セクション（refactor-intent-map.md 存在時のみ）

### Step 3: Phase C — 履歴層更新 + ARCH-DECISIONS

- `history/INTENT.md` v5.5.0 セクション追加（adrv01-Ph1 / Phase γ コア 3 件 / β止揚運用記録 / v5.6.0 / v6.0.0 候補温存）
- `history/CHANGELOG.md` 本セクション
- `history/REGIME-LOG.md` v5.5.0 minor 昇格判定記録（M2 / LC=1 / dev_mode=github_assisted / claude-opus-4-7）
- `history/ARCH-DECISIONS.md` AD-018（adrv01-Ph1）+ AD-019（Phase γ コア 3 件）追加
- `history/COUNCIL-LOG.md` `vrfy01` エントリは Step 0 で append-only 追記済み（PR 内同梱）

### Step 4: 自己検証 + 献上

- `python harness-verifier/verify.py --strict` 全 PASS（D4 整合性維持確認、5 検査全項目）
- `harness-verifier/reports/2026-05.md` 上書き（最新実行記録）
- `delivery/SELF-VERIFICATION-v5.5.0.md` 作成（L0 §7.4 自己検証の 5 項目 + harness-verifier 5 検査 + β止揚運用の SPEC 化過程内包記録）
- 計算的センサー: SKILL.md / references の構文整合・broken reference なし
- ルートに draft PR #34 を作成、Copilot review #34 で発見された category 誤選択の連鎖は本リリースで Shift Left 修正

## v5.4.0 (released 2026-05-01)

minor 昇格。**archeo-architect（意図復元 L0 兄弟スキル）を新設**し、spec-architect の双対として L0 を 3 兄弟体制に拡張。
HANDOFF「archeo-architect ブレスト → 実装」 2026-05-01 を起源とする。
後方互換維持（v5.0.0 / v5.1.0 / v5.2.0 / v5.3.0 と同パターン）。利用者プロジェクトには配布されない。

`crosscut-verifier-philosophy` 本実装は本リリース対象外（v5.4.x または v5.5.0 候補へ再々後送）。
Phase γ（L1 自己検証/独立検証への意図合致軸追加、起点問題の構造解決）は本リリース対象外（v5.5.0 候補）。

### Step 0: HANDOFF 受領と最終ブレスト

ひでさんから Claude.ai 上の archeo-architect ブレスト結晶 HANDOFF を受領。CC 側で Phase 1〜3（探索・設計・確認）を実行：

- 既存 spec-architect / onboarding の内部構造を Explore で把握
- DH 哲学ドキュメント群（DH-PHILOSOPHY-INSIGHTS / INTENT.md / DIMENSIONS.md / philosophy.md / council-philosophy.md）の参照箇所整合性検証
- Plan agent で配置案A/B 両論併記の実装計画立案
- AskUserQuestion で 4 論点を確定（配置 A / Phase γ 分離 / 動的起動オプション / minor 判定）

### Step 1: archeo-architect SK 雛形の新設

`.claude/skills/layer0-archeo-architect/` を新設、6 ファイル：

- `SKILL.md` — frontmatter `dimension: D4`、3 原則 (P-Arch-1/2/3)、7 ステップ対話フロー、§7.4 自己検証
- `assets/refactor-intent-map-template.md` — Meta / Islands / Boundaries / Absent-Intent Zones の 4 セクション、4 値必須フィールド
- `references/dialog-flow-archeo.md` — Step 1〜7 の対話文型、Step 3 horizontal vs Step 7 vertical の分離規約、5 問上限自己制限規約
- `references/intent-hypothesis-protocol.md` — 仮説生成ヒューリスティック（コメント不在 / 命名混乱 / 重複ロジック / git log 不在 / テスト不在 / マジックナンバー / TODO/FIXME / deprecated 痕跡）と確度規約 3 段階（code_check / git_log_check / ai_inference）
- `references/absent-intent-protocol.md` — `absent` 確定条件（人間明示宣言必須）と捏造防止規約（P-Arch-2 物理実装、3 メカニズム）
- `references/handoff-to-evaluator.md` — `refactor-intent-map.md` の I/O 規約（Phase γ 先行宣言版）

### Step 2: spec-architect SKILL.md 責務分担表の更新

`.claude/skills/layer0-spec-architect/SKILL.md`:
- §L0 スキル間の責務分担表に「リファクタ前 意図復元」行を追加（archeo-architect、4 行目）
- 排他ルールに 4 項目追加（archeo は再利用可能 / archeo は自動起動しない / spec-architect と同時起動禁止 / 既存ルール維持）

### Step 3: dev-env-spec.md Level A 一覧の更新

`.claude/skills/layer0-spec-architect/references/dev-env-spec.md`:
- Level A（共通スキル）一覧に `layer0-archeo-architect（再利用可能、v5.4.0 追加）` を追加

### Step 4: 履歴層更新

- `history/INTENT.md` に v5.4.0 セクションを追加（archeo-architect 設計意図 / Phase 化 / 配置論点 / v6.0.0 候補温存）
- 本 CHANGELOG.md に v5.4.0 セクション追加（本セクション）

### Step 5: 自己検証 + 献上

- harness-verifier 5 検査全 PASS（D4 整合性維持確認）
- 計算的センサー: SKILL.md / references の構文整合・broken reference なし
- archeo SK 6 ファイル + spec-architect 軽微修正の整合性確認
- ルートに draft PR #30 を作成

### Step 6: 業界知見統合（Council 諮問経由の追加実装）

ひでさんから AI を活用したレガシーコード・リファクタリング業界知見（フェザーズ / ファウラー / ヘルマンズ / ストラングラー・フィグ / Branch by Abstraction / 承認テスト / 自動照合ループ / Git ホットスポット / DDD Bounded Context / AAR / 失敗アンチパターン）が共有され、選択肢 A/B/C の拮抗のため Council 諮問。

`crosscut-council` を直接起動（`council-2026-05-01T10:30:00Z-archeo01`、category: conception、哲学者重み 5 で支配的）。3 Persona で simple_conflict（経営者 B / 開発者 A / 哲学者 第 4 の道）。Judgment Agent confidence 0.7 で「**第 4 の道: A 縮小版 + Phase γ 伏線追加**」が agreed_recommended 確定。ひでさん即時合意。

追加実装：

- **`intent-hypothesis-protocol.md` に Code Smells カノン対応表追加**（12 種 Smells のマッピング、適用順序、注意事項）
- **`intent-hypothesis-protocol.md` の S 軸推定に Git ホットスポット分析統合**（`hotspot_score = log(修正頻度) × 複雑性指標`、4 戦略象限、90 日の法則対応、計測制約）
- **`handoff-to-evaluator.md` の Phase γ 詳細仕様先行宣言**（5 件: 承認テスト生成プロトコル / 自動照合ループ / L1 意図合致軸統合 / ストラングラー・フィグ射程外宣言 / 失敗アンチパターン早期検出）
- **`crosscut-council/history/COUNCIL-LOG.md`** に invocation_id `council-2026-05-01T10:30:00Z-archeo01` のエントリ追加（implementer_consent: agreed_recommended）
- **`history/INTENT.md`** v5.4.0 セクションに「Council 諮問による業界知見統合」「経営者の少数意見（観測駆動原則との緊張）」追記

経営者の少数意見（選択肢 B、PR スコープ厳守）は minority_opinion として保持。観測駆動原則との緊張関係は Phase β/γ 設計時に再検討予定。

### Step 7: 業界知見統合後の再検証

- harness-verifier 5 検査全 PASS 維持（追加修正後も D4 整合性維持）
- 拡張ファイル 3 件（intent-hypothesis-protocol.md / handoff-to-evaluator.md / COUNCIL-LOG.md）の broken reference なし
- PR #30 に追加コミットを push、draft 状態のまま実装完了

### Step 8: L1-refactor 新設提案の Council 諮問（archeo02、最小記録）

ひでさんから L1-refactor スキル新設の提案。CC が D4 原則で機械的検査し 5 原則違反（wf-baseline-rationale.md / philosophy.md §1 / §3 / Phase γ 重複 / 観測駆動閾値未達）を指摘、不採用結論を提示。ひでさんが Council 諮問を選択。

`crosscut-council` 直接起動（`council-2026-05-01T11:00:00Z-archeo02`、conception カテゴリ）。3 Persona unanimous で **B（L1-refactor 不採用、Phase γ 予定通り）** を支持、weighted_score 8.85、judgment_confidence 0.85 で agreed_recommended 確定。CC 機械的検査と Council 判断が完全整合し堅牢な決定。

哲学者の拡張提案『v6.0.0 で Level B プロジェクト固有 SK によるリファクタ支援を明文化』は最小記録方針で `history/INTENT.md` v5.4.0 セクション末尾に 1 段落追加（v5.x 帯 minor 改修を圧迫しないため）。`COUNCIL-LOG.md` に archeo02 エントリ追加。

### 本リリースの範囲外

- **Phase γ（L1 改修）**: layer1-autonomous-dev SKILL.md §6 / inferential-sensor-v2.md / layer1-independent-reviewer SKILL.md への意図合致軸追加。**v5.5.0 候補**として継続検討
- **Phase β（ritual-protocol 統合・glossary 用語追加）**: 本リリースに同梱しない（α 完了後の用語確定を待つ）。**v5.4.x 候補**
- **Phase δ（spec-architect 逆輸入）**: 運用データ 3 ヶ月蓄積後、Council 諮問で実施可否判定。**v6.0.0 候補**として温存

## 2026-05-01 命名整備: Lifecycle → LC（v5.3.0 patch、no version bump）

DH 本体の `Lifecycle L=N` 表記を `LC=N` に統一する命名整備。Layer (`L0/L1/L2`) と Lifecycle (`L=0/L=1/L=2`) の `L` + 数字命名衝突を解消する。`crosscut-council` 諮問の結果、経営者/開発者/哲学者の 3 ペルソナで「進行可、ただし 3 条件付き」の重み付き判定（`history/COUNCIL-LOG.md` 参照）。

機能変更なし、後方互換維持（`harness-verifier/glossary.yml` の `lifecycle:` セクションは旧表記 `L=0/L=1/L=2` `Lifecycle 0/1/2` `Lifecycle L=0/L=1/L=2` を全て alias として保持）。バージョンアップなし。

### 変更内容

- `harness-verifier/glossary.yml`: キー `L=0/1/2` を `LC=0/1/2` に変更、旧表記を aliases に保持
- `.claude/skills/` 配下 markdown 群: `Lifecycle L=N` / `Lifecycle ≥N` / `Lifecycle ≤N` / `L=N` / `Lifecycle 別` / `Lifecycle 軸` / `Lifecycle 判定` / `Lifecycle記録` / 表ヘッダ `| Lifecycle |` 等を機械置換 + 残存手動補正
- `history/INTENT.md`: 旧「Lifecycle → LC 命名変更計画（保留中）」節を「（✅ 完了）」に変更し、実施記録を追記
- `history/REGIME-LOG.md`: 本サイクルを記録
- `history/COUNCIL-LOG.md`: PR #30 open のまま進行する判定の Council 諮問を記録

### 触らなかったファイル（後方互換のため）

`delivery/` 配下の version snapshot、`dh-upgrades/upgrade-spec-v5.0.0.md`、`docs/migration-guide-v5.1.0.md`、`history/CHANGELOG.md` v5.0〜v5.3 既存エントリ、`history/REGIME-LOG.md` 既存エントリ、`history/ARCH-DECISIONS.md` 全エントリは時系列の歴史的事実として保持。

### Council 判定の前提条件 3 件

1. INTENT.md の発動条件記述を「並列実行・衝突は rebase で解消」に更新 ✓
2. PR #30 衝突 4 ファイル（`layer0-spec-architect/SKILL.md` / `dev-env-spec.md` / `INTENT.md` / `CHANGELOG.md`）は PR #30 新規行に触れず、既存 Lifecycle 言及行のみ置換 ✓
3. harness-verifier 全項目 PASS ✓

## v5.3.0 (released 2026-04-30)

minor 昇格。**1 機能完遂の自律駆動 WF を「形状単一・薄い基底」として確定**し、献上トリガー Type D（異常献上）を新設。
HANDOFF「1 機能完遂の自律駆動 WF 設計」2026-04-30 と Council 合議（`council-2026-04-30T14:30:00Z-wfsurf1` / `council-2026-04-30T14:50:00Z-wfbase1`）を起源とする。
後方互換維持（v5.0.0 / v5.1.0 / v5.2.0 と同パターン）。利用者プロジェクトには配布されない。

`crosscut-verifier-philosophy` 本実装は本リリース対象外（v5.3.x または v5.4.0 候補へ再々後送）。

### Step 0: L0 設計献上の確認

L0 (spec-architect) で 5 phase 完了（論点 1 / 2 / 3 + 認識ズレ確認 + 落とし込み）。
献上物: `delivery/L0-WF-DESIGN-2026-04-30.md`。AD-015 / AD-016 / AD-017 で実装スコープを確定。

### Step 1: philosophy.md §5 に Type D 追加

`.claude/skills/layer0-spec-architect/references/philosophy.md`:
- §タイプD（異常献上）節を追加（タイプC の後）
- §タイプ対応表に Type D 行を追加
- §タイプ二項分類の限界（v6.0.0 候補）を追加（第 8 条候補「献上 3 軸の存在論」温存記述）

### Step 2: layer1-autonomous-dev SKILL.md 三点修正

`.claude/skills/layer1-autonomous-dev/SKILL.md`:
- §原則に「WF 形状単一性」原則を 1 項目追加
- §8 献上の表を 2 種 → 4 種に拡張（Type A / B / C / D）
- §DELIVERY.md 抜粋（イメージ）に Type D 行を追加

### Step 3: delivery-format.md に Type D 節と表更新

`.claude/skills/layer1-autonomous-dev/references/delivery-format.md`:
- §献上物タイプ一覧表に Type D 行を追加
- §タイプA と D の差異を明示
- §献上物タイプD（異常献上）節を新設（プロトコル / 構造 / 記述ルール）

### Step 4: wf-baseline-rationale.md 新設

`.claude/skills/layer1-autonomous-dev/references/wf-baseline-rationale.md` を新設：
- 採用方針（基底 WF / 機能タイプ別 WF 群を作らない理由 / 厚化閾値 / 観測対象外）
- 第 3 の道（v6.0.0 候補）の温存記述
- 関連レコードへのリンク（AD / INTENT / COUNCIL / philosophy）

### Step 5: 履歴層更新

- `history/ARCH-DECISIONS.md` の「v5.3.0 候補」→「v5.3.0」確定昇格
- `history/INTENT.md` の同上
- `history/REGIME-LOG.md` に v5.3.0 セクション追加
- 本 CHANGELOG.md に v5.3.0 セクション追加（本セクション）

### Step 6: 自己検証 + 独立検証 + 献上

- harness-verifier 5 検査全 PASS（D4 整合性維持確認）
- 計算的センサー: SKILL.md / references の構文整合・broken reference なし
- 推論的センサー: 「仕様に合う・動く・使える」3 観点で自己評価 PASS
- 独立検証 (layer1-independent-reviewer) スコープ: SK/RL/WF 規約整合
- 献上物: `delivery/SELF-VERIFICATION-v5.3.0.md` + `delivery/L1-DELIVERY-v5.3.0.md`

## v5.2.0 (released 2026-04-30)

minor 昇格。次元論（D1〜D5）導入と D4 検査機構（`harness-verifier/`）の独立配置。
HANDOFF「DH 自己検証機構（誤作動防止機構との統合検討用）」2026-04-29 と
Council 合議（invocation_id: council-2026-04-29T21:00:00Z-d4mtr1, 4 論点一括）を起源とする。
後方互換維持。利用者プロジェクトには配布されない。

`crosscut-verifier-philosophy` の本実装は本リリース対象外（v5.3.0 候補へ再後送）。

### Step 0: Council 合議

L0 対話中にユーザー指示で `crosscut-council` を起動、4 論点を一括諮問：

1. 次元論の命名統一（案 a: D-numbering / 案 b: T-numbering / 案 c: 階層形容詞）
2. D4 検査機構の名称（meta-verifier / harness-verifier / dh-integrity / singularity）
3. バージョン昇格区分（v5.2.0 minor / v6.0.0 major / v5.2.0 + v5.3.0 後送）
4. 検証スコープ 5 項目の D4 対象妥当性

3 ペルソナ並列独立発言 → 重み付き Judgment Agent 出力で全論点 final_decision: null、
合意プロセスで agreed_recommended 確定（implementer_consent 後追記済）。

### Step 1: harness-verifier/ スキャフォールド

リポジトリルート直下に新規ディレクトリを配置：

- `harness-verifier/README.md` — 概要、5 次元論サマリ、5 検証項目、独立性原則、実行方法
- `harness-verifier/PHILOSOPHY.md` — 規律の自己相似性、自己検証機構の存在論（singularity 別名併記）
- `harness-verifier/BOUNDARY.md` — DH 本体との境界線、責務マトリクス、依存方向、5 層構造保全の D4 解釈
- `harness-verifier/HUMAN-PROTOCOL.md` — 月次運用、レポートフォーマット、D5 判断カテゴリ、エスカレーション、形骸化防止
- `harness-verifier/glossary.yml` — 用語辞書（version 0.1.0、12 カテゴリ）

### Step 2: Python 検査本体

Python 標準ライブラリのみ（外部依存ゼロ、独立性要請の担保）：

- `harness-verifier/verify.py` — メインスクリプト、`--report` / `--strict` / `--json` / `--commit-sha` フラグ対応
- `harness-verifier/checks/__init__.py` — モジュールパッケージ
- `harness-verifier/checks/frontmatter.py` — 検証 1: SKILL.md frontmatter（name kebab-case + ディレクトリ名一致 + description 30-1024 chars）
- `harness-verifier/checks/references.py` — 検証 2: Markdown インラインリンクの dead link 検出（拡張子フィルタ + アンカー除去）
- `harness-verifier/checks/dependency_graph.py` — 検証 3: 未定義 skill 参照と自己参照検出（意図的相互参照は許容）
- `harness-verifier/checks/five_layer_structure.py` — 検証 4: 5 層検出スタックの canonical 名整合（5 層検出スタック文脈フィルタで誤検出回避）
- `harness-verifier/checks/glossary.py` — 検証 5: 簡易 YAML パーサ + forbidden_uses 検出 + crosscut/layern prefix members の実体整合

### Step 3: GitHub Actions ワークフロー

`.github/workflows/harness-verify.yml` を新設：

- cron `0 0 1 * *`（毎月 1 日 09:00 JST）で月次レポート自動 commit
- push / pull_request の `.claude/skills/**` または `harness-verifier/**` 変更で trigger
- `--strict` モードで CI 厳格判定、月次のみ `--report` でファイル生成
- `permissions: contents: write` で月次レポート自動 commit を許可

### Step 4: SKILL.md v5.2.0 セクション追加

`.claude/skills/layer0-spec-architect/SKILL.md` の参照ドキュメント節に v5.2.0 セクションを追加。
次元論サマリと harness-verifier 配置・スコープを記述。L0 起動フローには影響しない（情報依存しない設計）。
既存 §0〜§7.6 のセクション番号は不変、v5.1.0 セクションも不変、その上に積層。

### Step 5: 履歴層更新

- `history/INTENT.md`: v5.2.0 セクション追加（5 次元論確立 / D4 検査機構の独立配置 / 自己言及パラドックスの構造的回避）
- `history/ARCH-DECISIONS.md`: AD-010（5 次元論導入と D-numbering 採用）/ AD-011（DH 本体外への独立配置）/ AD-012（harness-verifier 命名判断）/ AD-013（v5.2.0 minor 昇格と philosophy verifier 後送）追加
- `history/REGIME-LOG.md`: v5.2.0 minor 昇格記録（不変項目遵守確認、改修体制、次バージョン予定 v5.3.0/v6.0.0）
- `history/CHANGELOG.md`: 本セクション
- `history/COUNCIL-LOG.md`: 4 invocation entry を追加（invocation_id 共通鍵、implementer_consent: agreed_recommended 後追記）

### Step 6: §7.4 自己検証 + 献上

`delivery/SELF-VERIFICATION-v5.2.0.md` 配置。
broken reference / DONT 自己照合 / Pre-flight 充足 / 受け入れ基準充足 / harness-verifier smoke test の 5 チェック実行。
本案件はメタスキル本体改修（D4 改修）であるため、scaffold-checklist.md の Vite+TS+React+PWA stack は適用対象外（D2 検査の責務、本案件の対象次元と異なる）。

### Step 7: 独立検証 (layer1-independent-reviewer) FAIL → C-1/C-2/C-3 修正

`delivery/VERIFICATION-v5.2.0.md` で M2 必須独立検証実施、初版 FAIL 判定（重要 1 + 警告 2）：

- C-1: `_parse_yaml` が複数行 block list 構文を誤読、検査 5 が空回り
- C-2: monthly cron の FAIL がメール通知されない（`|| echo` で吸収）
- C-3: SELF-VERIFICATION の根拠補強（C-1 修正で自然解消）

C-1 解決方針を Council 諮問（invocation_id: council-2026-04-29T22:30:00Z-c1fix1）。
全会一致で「案 b 中核 + 案 a 防御 + 哲学者ドキュメント宣言」三段統合（judgment_confidence 0.88）を承認。

実施内容：

- `harness-verifier/glossary.yml` を subset YAML 形式に書き換え（forbidden_uses / crosscut_prefix.members / layern_prefix.members をインライン化、冒頭コメントで形式制約を明示）
- `harness-verifier/checks/glossary.py` の `_parse_yaml` を全面改修：
  - 複数行 block list 構文 (`- item`) を検出時に `SyntaxError` を raise（黙って誤読しない）
  - `_split_top_level` でネスト構造を尊重した top-level 分割を実装
  - `_parse_inline_value` でインライン list / list of dict / dict / scalar を統一処理
  - key 正規表現に `=` を許可（`L=0`, `L=1`, `L=2` 等の Lifecycle キーを glossary で扱える）
- `harness-verifier/BOUNDARY.md` に §9「独立性の代償（subset YAML 制約、AD-014）」を追加
- `harness-verifier/glossary.yml` の `forbidden_uses` を「絶対に使うべきでない語」に絞り込み、予約語/未実装語（L3 運用層、T1-T5）は除外（否定文脈での言及は正当）
- `.github/workflows/harness-verify.yml` の monthly 経路を `continue-on-error: true` + 末尾 fail step で修正、HUMAN-PROTOCOL.md §4 のメール通知エスカレーションが機能するよう整合化（C-2 解消）
- `history/ARCH-DECISIONS.md` に AD-014（subset YAML 形式判断）を追加
- `history/COUNCIL-LOG.md` に invocation entry 追加
- `delivery/SELF-VERIFICATION-v5.2.0.md` に C-1〜C-3 解消反映を追記
- `delivery/VERIFICATION-v5.2.0.md` を PASS 化（独立検証再判定）

最終 smoke test: `python harness-verifier/verify.py --strict` で 5 検査全て **意味のある PASS**（検査 5 の forbidden_uses / prefix 整合検査が実走、検出 0 件は実態として違反なし）。

## v5.1.0 (released 2026-04-28)

minor 昇格。L0 受け入れ基準の明文化 / Pre-flight 必読化 / scaffold checklist / §7.4 自己検証ステップを追加。
PR #19 テストレビュー（シナリオ「ケロぴの森」）で判明した L0 charter 未達 P0 4 項目（受け入れ基準・Pre-flight・scaffold・自己検証）を解消する。後方互換維持。

`crosscut-verifier-philosophy` の本実装は本リリース対象外（v5.2.0 候補として継続検討）。

### Step 1: §0 受け入れ基準明文化

`.claude/skills/layer0-spec-architect/SKILL.md` §0「原則」に「L0 完了の受け入れ基準（v5.1.0 追加）」を新設し、4 条件を明文化：仕様充足 / scaffold 実体生成 / smoke test 通過（または保留事由明記）/ §7.4 自己検証 PASS。Lifecycle ≥ 1 の既存プロジェクトには段階適用（既存成果物の遡及修正は不要）の旨を併記。

### Step 2: Pre-flight 必読指定

主要ステップ冒頭に「**Pre-flight (v5.1.0)**: 起動前に X を必読」行を追加：

- §1.5 振り返り儀式 → `references/ritual-protocol.md`
- §3.5 サブフェーズ選定 → `references/subphase-selection.md`
- §4 モード判定 → `references/regime-assessment.md`（dev_mode 判定セクション含む）
- §6 開発環境構築 → `references/dev-env-spec.md` + `references/scaffold-checklist.md`
- §7 出力 → `assets/credit-template.md`

§7.5 / §7.6 は既存 references の参照で充足するため Pre-flight 行追加なし。

### Step 3: scaffold-checklist.md 新設

`.claude/skills/layer0-spec-architect/references/scaffold-checklist.md` を新規作成。v5.1.0 標準 stack を Vite + TypeScript + React + PWA に固定し、12 種の必須生成ファイル（package.json / tsconfig / vite.config / vitest.config / playwright.config / biome / .gitignore / index.html / src/main.tsx / src/App.tsx / public/manifest.webmanifest / public/icons）と smoke test 4 コマンド（pnpm install / dev / build / test）を規定。
他 stack（Next.js / Vue / Astro / SvelteKit / 純 Node CLI）は将来 minor で追加。

`references/dev-env-spec.md` の「開発環境構築時の初期化」リスト末尾に scaffold-checklist.md への相互参照 1 行を追加（既存内容は不変）。

### Step 4: §7.4 自己検証ステップ追加

`.claude/skills/layer0-spec-architect/SKILL.md` の §7（出力）と §7.5 の間に「### 7.4. L0 自己検証（v5.1.0 追加）」を新設。5 件のチェック項目をチェックボックス形式で配置：broken reference 検査 / scaffold smoke test 検査 / DONT 自己照合 / Pre-flight 充足 / 受け入れ基準充足。FAIL があれば §7（出力）に進まず原因解消する旨を明記。既存 §7.5 / §7.6 のセクション番号は不変。

### Step 5: バージョン更新

- `assets/credit-template.md`: v5.0.0 → v5.1.0
- `.claude/skills/layer0-spec-architect/SKILL.md` の参照ドキュメント節に「### v5.1.0 追加（L0 受け入れ基準明文化・Pre-flight 必読化・scaffold checklist・自己検証ステップ、minor 昇格）」セクションを追加（既存 v5.0.0 セクションは不変、その上に積層）
- `history/CHANGELOG.md`: 本セクション追加
- `history/REGIME-LOG.md`: minor 昇格記録（不変項目遵守確認・改修体制・既存 v5.0.0 セクション保持）
- `history/ARCH-DECISIONS.md`: AD-008（L0 完了基準の再定義）/ AD-009（scaffold-checklist の単一 stack 採用方針）追加
- `history/INTENT.md`: v5.1.0 の意図追記（L0 charter 達成可能性の確保・Pre-flight 強制化）

## v5.0.0 (released 2026-04-28)

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
- `assets/meta-spec-template.md` の REGIME.md テンプレに `## dev_mode` セクション追加(mode / ctl / 判定根拠)
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

### Step 4: CTL 連動 protocol + maturity strategy

各 crosscut skill に CTL 別動作の references を追加（spec §4.4）：

- `crosscut-issue-dispatcher/references/dispatch-protocol.md`
- `crosscut-issue-implementer/references/implement-protocol.md`
- `crosscut-verifier-drift/references/verify-protocol.md`
- `crosscut-feedback-loop/references/feedback-protocol.md`

各 protocol.md は github_assisted / github_autonomous × CTL-0/1/2/3 の動作表を本体化、Council 事前検証発動条件 + CHANGELOG 記録形式を含む。

`crosscut-council/references/ctl-maturity-strategy.md` を新規作成（spec §4.4.2.2、既存 `ctl-calculation.md` に育成戦略の項なしと確認済）。CTL 段階定義 / 量×質ハイブリッド昇格条件 / 横断蓄積補強 / 退行ロジック / CHANGELOG 自動記録形式を含む。

### Step 5: GitHub Actions 雛形配置

`templates/.github/workflows/` を新設し 9 yml を配置（spec §4.5）：

- `basic-ci.yml`（既存検出スタック第1層 + Shift Left 基盤の CI 化）
- `e2e-ci.yml`（既存検出スタック第2層、Playwright Test Agents 規格）
- `interaction-cost.yml`（既存検出スタック第3層、UX 計算可能代理指標）
- `spec-drift.yml`（crosscut-verifier-drift の CI 化）
- `issue-dispatch.yml`（crosscut-issue-dispatcher の CI 化、CTL 連動 + Council 事前検証）
- `issue-to-impl.yml`（crosscut-issue-implementer の CI 化、claude-code-action `<latest>` プレースホルダ）
- `drift-feedback.yml`（crosscut-feedback-loop の CI 化、種別→還流先マトリクス実装）
- `auto-merge.yml`（CTL ≥ 2 + 全条件達成時のみ squash merge）
- `auto-degrade.yml`（連続失敗・重大インシデントで dev_mode + ctl 自動降格）

各 yml 冒頭に `# Required mode:` `# Required CTL:` をコメント明記。

`layer0-spec-architect/references/dev-env-spec.md` の参照権限マトリクスに `templates/` 行を追加（v5.0.0 追加、配布雛形のため AI 書 ✅・Human 書 △）。

### Step 6: バージョン更新（v5.0.0 major 確定）

- `assets/credit-template.md`: バージョン記法を semver 厳格化（`vX.Y` → `vX.Y.Z`、v4.x 互換受理を明記）
- `layer0-spec-architect/SKILL.md` の参照ドキュメント節に `### v5.0.0 追加（GitHub 連携前提化・crosscut prefix 確立・semver 化、major 昇格）` セクション追加
- `history/REGIME-LOG.md` を本格化：major 昇格記録（破壊項目テーブル・非破壊追加・移行方針・不変項目遵守確認・改修体制・次バージョン予定）
- README バッジ作業はスキップ（README 不在のため、SELF-VERIFICATION §5.3 で「適用対象外」明記予定、AD-006）

### Final: migration guide + self-verification

- `docs/migration-guide-v5.0.0.md`: 既存プロジェクト向け移行手順書（必須 5 + 任意 5 + 後退 + Q1-Q5）
- `delivery/SELF-VERIFICATION-v5.0.0.md`: 自己検証結果（PASS、5.3.2 README バッジは適用対象外）

総合判定 PASS。次フェーズでユーザー側 spec §6 + layer1-independent-reviewer 独立検証へ。

### Fix: skill-creator 監査 MEDIUM-1（誤発動防止）

ユーザー要求に基づき skill-creator 視点での独立監査を実施。検出 1 件（MEDIUM-1）を本コミットで fix：

- `crosscut-verifier-philosophy/SKILL.md` description: 冒頭に「**v5.0.0 では発動禁止 / DO NOT TRIGGER in v5.0.0**」を明示配置。トリガー語句を「v5.1.0 以降の想定トリガー語句（v5.0.0 では非トリガー）」と未来形で再表記。731 chars（1024 制限内）。
- 監査レポート `delivery/SKILL-CREATOR-AUDIT-v5.0.0.md` 配置（PASS 判定 + LOW 2 件は次回改修課題として記録）。

LOW-1（SKILL.md と protocol.md の CTL 表部分重複）と LOW-2（placeholder の references 不在）は本リリースでは触らず、次回改修時の課題として監査レポートに記録。

### Independent Review: layer1-independent-reviewer 起動・PASS

M2 体制完結のため `layer1-independent-reviewer` を起動し独立検証を実施：

- `delivery/VERIFICATION.md` 配置（PASS、提起 3 件は全て注記のみ）
- 提起内容:
  - C-1: SELF-VERIFICATION §5.4.2 ラベリング不整合（同根因 AD-006 で対応済）
  - C-2: メタ案件としての DELIVERY/HANDOFF 兼任注記欠如（次回参考、機能影響なし）
  - C-3: spec §5.2.4 disabled/ 原則項目（本リリース対象外）
- L1 自己検証 / skill-creator 監査 / 本独立検証の 3 視点で判定整合（割れなし）
- L2 統合検証は不要（単一ドメイン、L2 閾値未達）

→ ready-for-review 化可能。最終承認は人間判断（spec §6 哲学的整合性 + サンプルプロジェクト試運転）。

### Fix: Copilot review (3 件、最小権限明示)

PR #18 への Copilot レビュー 3 件すべてに対応。GitHub Actions の最小権限規約に基づき、各 yml に `permissions:` を追加：

- `templates/.github/workflows/issue-dispatch.yml`: `contents: read` + `issues: write`（gh issue create）
- `templates/.github/workflows/drift-feedback.yml`: 既存 issues/pull-requests に `contents: read` 追加（actions/checkout が default-none で失敗するため）
- `templates/.github/workflows/spec-drift.yml`: `contents: read` + `issues: write` + `pull-requests: write` + `actions: write`（github-script + gh workflow run drift-feedback.yml）

テンプレートとして最小権限を明示することで、デフォルト read-only な GITHUB_TOKEN 設定のリポジトリでもそのまま動作する形になった。yaml syntax は引き続き全 PASS。

