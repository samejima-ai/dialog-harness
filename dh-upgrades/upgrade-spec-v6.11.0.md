# upgrade-spec v6.11.0 — エージェントオーケストレーション実行基盤（Workflow 背骨 + 議論型協調層）

> **状態: L0 起草（人間レビュー待ち）**。本仕様の実装は escalation-matrix「規範文書改変」行に従い、
> 人間レビュー通過後・実装前に Council 諮問を経る。
> 起点: L0 前ブレスト成果 `delivery/ANALYSIS-agent-orchestration-2026-08-14.md`（PR #184 merged）+
> L0 対話決定（2026-08-15、ひでさん）: 全層同時 1 リリース / Teams は抽象契約 + 時限付き随時層 / 記録 teeth 含む。

---

## 0. 位置づけ — 新機構ではなく実行基盤の置換

前 cycle（f5fc45）で確定した「減らす・時限化」原則との整合: 本リリースは**新しい判定機構・新しい規範カテゴリを追加しない**。
DH が既に規範として持つオーケストレーションの設計図（Council フェーズプロトコル / review OC+workers / 反証 fan-out / L2 雛形）に、
決定論の実行基盤（Workflow）を与える**置換**である。議論型協調層（実装: Agent Teams）のみ新規だが、抽象契約 + 時限付き随時層に閉じる。

**不変条件（全機能共通）**:

- I-1 オーケストレーション実行基盤は**判定を持たない**。judgment は Council・決定は人間/合意プロセス（final_decision null 維持、escalation-matrix 整合）
- I-2 ローカル自律実行ファースト。CI 専用の実行経路を作らない
- I-3 G-AGENT 凍結（f5fc45）尊重: CLAUDE.md 規格行に触れない
- I-4 情報純度: Workflow journal は実行側の内部成果物。independent-reviewer の入力に**含めない**（実装コンテキスト隔離の維持）
- I-5 サブスク運用: 並列度は既定値上限内（§F7）。超過運用は ADR 必須

## F1. Council fan-out の Workflow 化（priority: critical）

`crosscut-council/references/workflows/council-fanout.workflow.mjs` を新設し、`crosscut-council/SKILL.md` §処理フロー（Phase 0 → 重み計算 → Phase 1 → 対立度判定 → Phase 3 → ログ/CTL）の実行基盤として配線する。

| 条件 | 内容 |
|---|---|
| F1-1 | Phase 0 Pre-Check・重み計算は**スクリプト内の決定論 JS**（LLM 不使用の現行規約を構造化） |
| F1-2 | Phase 1 は `agent()` × 3 並列。スクリプト構造が相互出力の非参照を**強制**（プロンプトに他ペルソナ出力を含める経路が存在しない） |
| F1-3 | persona 出力は schema 強制: `stance`（options への正規化フィールド併記）/ `dimension` **必須** / `confidence` 0.0-1.0 / `reason` / `premise` / `concerns` |
| F1-4 | Phase 3 judgment は判定 agent + スクリプト側で weighted_score を**決定論検算**。confidence 帯（conflict_type / gap_ratio 由来）を検算し、帯外は retry 最大 2 → `judgment_failed` |
| F1-5 | COUNCIL-LOG §8 ブロックをスクリプトが生成（必須フィールドの欠落を構造的に排除）。追記 + CTL 同期は既存クロージング手順を維持 |
| F1-6 | 挙動同一性の受け入れ基準: 導入後最初の 3 発動が §8 スキーマ準拠 + `council-axis-audit.py` の正規化ギャップ **0 件** + jc が帯内。並走比較は行わない（コスト過剰） |

**記録 teeth**（L0 決定・軸監査 WARN 根因対策）: F1-3/F1-5 により options 正規化・dimension 記録率 100%・帯検算が機械強制になる。
手順書依存の空文化（v6.1.0 CTL 分断と同型）の構造的封じ。

## F2. review パイプラインの Workflow 化（priority: standard）

既存 review 規範（fetch / difficulty / intent-gate / evidence / persona×3 / judgment）を workflow スクリプト化する。

- F2-1 既存 `review-*` サブエージェント定義を `agentType` で再利用（プロンプト資産を書き換えない）
- F2-2 既存 output-format §3/§4 スキーマを schema 強制
- F2-3 `pipeline()` 主体（バリアは dedup 等、全結果を要する箇所のみ）
- F2-4 ローカル実行可能をもって受け入れ（I-2。CI からも同一スクリプトを呼べる形にする）

## F3. 反証 fan-out の Workflow 化（priority: standard）

independent-reviewer 処理フロー 5.10 の反証試行（A/B/C 類型 × critical 機能）を workflow で並列化する。

- F3-1 反証記録 schema 強制: `対象` / `類型` / `試行内容` / `結果`（反証不成立 / 反証成立 / 提起）
- F3-2 「この PASS が保証しない範囲」欄の生成を必須出力に含める（falsification-protocol §4 準拠）
- F3-3 B 類型（ミューテーション）は worktree 隔離オプションで実行し原状復帰を構造保証。preserve 領域では B 類型を起動しない（既存規約維持）

## F4. L2 orchestrator 実装体（priority: standard）

`layer2-orchestrator` に「実行基盤」節を追加し、雛形を実体化する。

- F4-1 サブドメイン分割後の L1 群起動・統合検証手配は Workflow で駆動
- F4-2 跨ぎドメインの**協調・調整が議論を要する**場面のみ議論型協調層（§F6 抽象契約）を使用
- F4-3 L2 発動条件は不変（REGIME 判定経由のみ・M1/M2 では起動しない）
- F4-4 orchestrator は判定しない: 方針対立は Council → 解消不能は人間（escalation-matrix 既存行のとおり）

## F5. L0 ブレスト・対話支援（priority: standard）

`layer0-spec-architect/references/brainstorm-orchestration.md` を新設する。

- F5-1 ブレスト時の多角調査 fan-out（Workflow: 並列リサーチ → 構造化 → 統合）の標準形を定義
- F5-2 議論型協調層は「多役割の対立的検討が本体」の場面に限定（使用判断基準を 3 行で明文化）
- F5-3 persona 層（presentation）と干渉しない。ブレスト成果は判断材料であり判定を含まない（I-1）

## F6. 議論型協調層 — 抽象契約 + 時限付き随時層（priority: standard）

- F6-1 DH 規範が定義するのは**抽象契約のみ**: 「独立コンテキストの複数エージェントが、直接メッセージ可能・人間割込可能・ローカル観測可能な協調層」
- F6-2 実装体（Agent Teams）の固有情報（env 変数・バージョン・設定手順・既知の制約）は `templates/experimental/agent-teams.context.md` に分離し、**時限メタデータ**を付す: 再評価条件 = GA 化 or 2026-11-30 のいずれか早い方（lifecycle_stage / 純化 RL 型階層の時限化機構を自己適用）
- F6-3 DH 規範ファイル（`.claude/skills/**`）から env 変数名・バージョン依存記述を排除する
- F6-4 degrade 経路: 協調層が使用不能（レート制限・機能変更）の場合、subagent 直列にフォールバックして完遂する（機能は落ちるが停止しない）

## F7. 横断規律（priority: critical）

- F7-1 escalation-matrix に 1 行追加: 「オーケストレーション実行基盤（Workflow / 議論型協調層）は判定を持たない実行機構であり、判定はマトリクスの定めに従う」
- F7-2 並列度の既定上限: Council fan-out = 3+1 / review ≤ 8 / 反証 = critical 機能 × 3 試行 / 協調層 teammate ≤ 3。超過は ADR 必須（I-5）
- F7-3 journal・共有タスクリストの扱い: 実行側内部成果物。reviewer 入力から除外（I-4）。delivery/ には成果物のみを置く（配置規則維持）

## DONT（本リリースのスコープ外）

- 並列 L1（worktree 分離での複数機能同時実装）— 温存・観測駆動（ブレスト決定）
- 外部オーケストレーター（Gas Town / Claude Squad 等)の導入
- CLAUDE.md へのエージェントルーティング標準行（G-AGENT 凍結中・f5fc45）
- council-weights.md の数値是正（ΣW=11 問題は D5 専管・別件）
- Agent Teams 固有仕様の SPEC 直接参照（F6-1 に反する）
- 新しい判定カテゴリ・新しい重み軸の発明

## モード判定・実装体制

- DH 本体の継続開発（LC ≥ 1）・**M2**（independent-reviewer 必須起動）
- 実装順序（1 リリース内の内部シーケンス）: F1 → F7 → F2 → F3 → F4 → F5 → F6（F1 の挙動同一性確認を最初に固める）
- 実装前ゲート: **Council 諮問**（escalation-matrix「規範文書改変」行。本仕様全体を議題とする）
- 献上時ゲート: 人間判定（同行）
- 検証: harness-verifier 全 PASS + F1-6 受け入れ基準 + 各 F の条件逐項確認（VERIFICATION.md、反証記録含む）

## 実装条件（Council 諮問 `council-2026-08-15T10:32:00Z-v6110c` の反映、実装前ゲート通過）

3 軸 reason_divergence 案B（条件付き GO、jc 0.80）。以下 4 条件を仕様に追補する:

- **C-1 ハードゲート**: F1 + F7 の完了と F1-6 受け入れ基準 PASS を後続 F（F2 以降）着手の必須条件とする。不通過時は即 revert + L0 差し戻し（部分続行しない）
- **C-2 degrade 経路の一般化**: F6-4 を全 Workflow（F1-F5）に拡張する。Workflow tool 非対応環境、および judgment_failed（帯外 retry 2 超過）時は、**従来経路（subagent 手動フロー）で完遂**し人間に warn を残す。実行基盤の不在・失敗は機能停止ではなく従来動作への回帰である
- **C-3 器外の観測点**: 実行基盤の機械化が判定の質（多様性・独立性）に与える影響を、軸監査 + 振り返り儀式の定点観測対象に加える。persona 出力 schema に自由記述 `notes` フィールドを設け、**schema に収まらない異見の受け皿**を構造的に残す（記録の完全性が発散性を殺さないための弁）
- **C-4 時限の teeth**: F6 の時限メタデータ（GA 化 or 2026-11-30）には期限超過検出の WARN を付し、形骸化を防ぐ

## 既知の限界（独立検証 2026-08-15 の提起を受けた仕様追補）

M2 独立検証（反証プロトコル準拠）が FAIL で差し戻した内容のうち、**実装で解消したもの**と
**仕様側の限界として明示するもの**を区別して記録する。前者は VERIFICATION 相当の記録に、後者は本節に残す。

- **L-1 F2-2 の到達水準**: review パイプラインの schema 強制は **JSON 構造化のみ**であり、
  フィールド単位（output-format §3/§4 準拠）の強制には至っていない。既存 review-* agent が
  output-format を自ら参照するため実害は限定的だが、F1 と同水準の構造強制は**次サイクル**とする。
  仕様 F2-2 の文言はこの限界に読み替える
- **L-2 F2-3 の実装形**: `pipeline()` ではなく `parallel()` バリア + 逐次 await で実装した。
  段間で全結果を要する（persona は evidence 全体を見る）ためバリアが正当だが、仕様文言との差分として記録する
- **L-3 Workflow script の契約検証**: `export const meta` + top-level `return` は素の Node では
  検証できず（runtime が前処理する前提）、本リリースでは「meta 分離 + async 関数ラップ」の
  同条件シミュレーションで構文検証した。runtime 準拠の lint / 最小実行スモークは**次サイクル**
- **L-4 難度ゲート**: 既存 claude-review.yml の tier1 = lightweight（Council を回さない）分岐は
  F2 スクリプトに未実装（difficulty を計算するが分岐に使わない）。常時フル合議になるため、
  ゲート実装までは CI 側の既存分岐を残すこと

## C-1 ハードゲートの運用形（独立検証 P-9 を受けた確定）

C-1 は「F1-6 受け入れ基準 PASS を F2 以降着手の条件」と定めたが、F1-6 は **merge 後の実発動でしか
観測できない**ため、単一リリースでの実装完了とは構造的に両立しない。運用形を次のとおり確定する:

- **実装（コード配置）は 1 リリースで完了してよい**。C-1 が縛るのは**実運用開始**である
- F2〜F5 の実行基盤は、**F1 の 3 発動で正規化ギャップ 0 件が確認されるまで opt-in**（既定は従来経路）とする
- 観測結果は L0 振り返り儀式で確認し、不通過なら該当スクリプトを revert する

## C-3 の実装状況（部分・次サイクルへ申し送り）

persona 出力の `notes` 自由記述欄（schema 外異見の受け皿）は実装済み。
一方「軸監査 + 振り返り儀式の定点観測対象に加える」は**未実装**であり、`ritual-protocol.md` /
`council-axis-audit.py` への接続は次サイクルで行う（機械化が判定の多様性に与える影響の定点観測）。

## 履歴

- 2026-08-15: L0 起草（ブレスト PR #184 + L0 対話決定に基づく）。人間レビュー待ち
- 2026-08-15: 人間レビュー通過（PR #185 マージ）→ Council 諮問 `v6110c`（案B 条件付き GO）→ 条件 4 件を追補し実装着手
- 2026-08-15: 実装（PR #186 merged）→ M2 独立検証 **FAIL**（反証成立 2 件 + C-1/C-3 未成立 + 提起 10 件）
  → 反証成立分を修正（空帯 cap の lo 補正 / scores 空ガード / YAML エスケープ / 丸め・tie・tokenizer の正典一致 /
  retry 正典統一 / 重みハードコード解消）、残りを §既知の限界・§C-1 運用形・§C-3 実装状況として明示化
