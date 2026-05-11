# 咀嚼プロトコル Wave 4 SPEC starter（ドラフト）

**起票**: 2026-05-11T18:00:00Z（Wave 3 PR #81 merged 後続）
**起票元**: spec-architect L0 経由、Wave 3 PR #81 merged（第 8 条明文化、conf 0.55 接近採決、minority C 温存）の後続として Wave 4 起票
**branch**: `claude/chew-protocol-spec-wave4`（master の Wave 命名規則準拠、旧 branch `claude/integrate-dialogharness-2XsY3` は PR #74 close の歴史的アーティファクトとして remote 残置）
**Phase**: Phase A — SPEC ドラフト起草 + 優先順位確定 + Council 諮問 agenda 提示

---

## 0. 本ファイルの位置づけ

咀嚼プロトコル Wave 4 の **Phase A 起点ファイル**。Wave 1 SPEC（PR #76 merged）+ Wave 2 SPEC（PR #77 + PR #78 merged）+ Wave 3 SPEC（PR #81 merged、第 8 条明文化）の到達点と minority opinion / 申し送り素材を継承し、Wave 4 で着手すべき候補群を整理して Phase B 諮問 agenda を提示する。

Wave 4 の最重要議題は **議題 W4-Q1「第 8 条 3 段階モデル vs 4 段階モデルの再諮問（Wave 3 minority opinion C の再評価）」** および **議題 W4-Q2「L0 対話パイプラインへの ECC 参照モード組込（HANDOFF 旧タスク B の Wave 4 着地）」** の 2 件。

前者は Wave 3 第 8 条 conf 0.55 接近採決の経験的揺らぎを踏まえた **哲学ガードレールの強度判断**、後者は Wave 1-3 で D3/D4 に着地した業界叡智（hooks / continuous-learning / AgentShield 参照）を **L0 対話 → 仕様生成パイプラインに具体的に流し込む機構** の起点。

**順序の哲学**: ユーザー方針「先にガードレール、後で取込拡張」に従い、W4-Q1（哲学）を W4-Q2（取込実装）より先に諮問する。Phase B 諮問順序は W4-Q1 → W4-Q2 を厳守。

---

## 1. Wave 1 + 2 + 3 振り返り

### 1.1 完遂事項

| Wave | PR | 主要成果 |
|---|---|---|
| Wave 1 | #76 | 咀嚼プロトコル枠組み確立、5 hooks event 採用、skill description 監査（逐次）、templates/rules 階層化、observation/hook 観測機構 |
| Wave 2 Phase A | #77 | Wave 2 SPEC ドラフト、ファイル意図ベース配置規則の確立 |
| Wave 2 Phase B+C | #78 | HV 検査項目 6（hook 観測一貫性）、crosscut-continuous-learning 新設、origin/version frontmatter 規格、AgentShield 参照導入規約 |
| 移行 | #79 | PR #77 規約準拠で過去 Wave ファイル 36 件を `history/` archive |
| Wave 3 Phase A | #80 | Wave 3 SPEC ドラフト、議題 3（第 8 条本格諮問）優先 1 確定 |
| Wave 3 Phase B+C | #81 | philosophy 第 8 条明文化（候補 A 採用、3 段階モデル「観測 → 候補化 → 人間最終承認」、conf 0.55、minority C 温存） |

### 1.2 確認された経験的事実

#### B 系収束パターンと部分破綻

Wave 1 Phase B（3 諮問 + 1 省略）+ Wave 2 Phase B（3 諮問 + 1 省略）+ Wave 3 Phase B（4 諮問）の多くが B 系（保守的・人間最終承認尊重）に向かったが、例外として **w1qb03 = A**（言語先取りなし）および **w3qb01 = A**（第 8 条 3 段階モデル明文化、conf 0.55 接近採決）が存在する。w3qb01 の A 採用は `history/wave3/COUNCIL-DECISION-wave3-phaseB-2026-05-11T09:00:00Z.md` で記録された通り **純粋な B 系収束パターンの部分破綻** を示しており、Wave 4 で minority C 再諮問が経験的に妥当となる根拠でもある。

| 諮問 | recommended | confidence |
|---|---|---|
| w1qb01（5 event 採用 vs 全 9 event） | B: 5 event + PreCompact 棄却 | — |
| w1qb02（skill description 一括 vs 逐次） | B: 逐次 | — |
| w1qb03（言語先取り） | A: 言語先取りなし | — |
| w2qb01（continuous-learning 自動度） | B: 候補出力のみ、人間最終承認 | — |
| w2qb02（AgentShield 採用範囲） | B: 5 カテゴリ warn のみ参照導入 | — |
| w2qb03（frontmatter 適用タイミング） | B: 逐次適用 | — |
| w3qb01（第 8 条候補数） | **A: 3 段階モデル明文化** | **0.55（接近採決）** |
| w3qb02（hooks 残候補 + continuous-learning CTL 連動） | B: PreCompact のみ採用、他 3 event は Wave 4 申し送り、continuous-learning は候補出力のみ継続 | 0.79 |

T3（サブセット選別）+ ガードレール語彙化が DH 哲学の自然な帰結として動作する **3 サンプル目** を蓄積。同時に **Wave 3 conf 0.55 は接近採決** であり、minority opinion C（4 段階モデル拡張）が Wave 4 再諮問に値するという経験的根拠も確立した。

#### 接近採決の意味

w3qb01 conf 0.55 は B 系収束パターンの強度に対して **揺らぎの存在を示すシグナル**。Wave 4 で minority C を再諮問することは:

1. Wave 3 採用結果（A 採用）を覆す可能性を哲学者重み 5 で残す
2. 業界叡智の取込拡張（W4-Q2）が進む前に、ガードレールの強度を最終確認する
3. ユーザー方針「私の哲学ありき」「専門家叡智で固めて私の哲学を行使」と整合

の 3 点で正当性を持つ。

### 1.3 Wave 3 末振り返りの観測項目（Wave 4 で評価）

| 観測項目 | 評価対象 | 発生 minority opinion |
|---|---|---|
| crosscut-continuous-learning 候補出力経路の運用実績 | w2qb01 minority A（CTL 連動自動度） | 候補出力が自動 promote 防止できているか観察 |
| 第 8 条 3 段階モデル稼働実績 | w3qb01 採用版 | 観測 → 候補化 → 人間最終承認の各段階で漏れがないか |
| 17 skill description 監査逐次進捗 | w1qb02 minority A（一括） | 進捗 ≤ 50% で Wave 4 一括再諮問 |
| 17 skill frontmatter 監査逐次進捗 | w2qb03 minority A（一括） | 進捗 ≤ 50% で Wave 4 一括再諮問 |
| ECC 14 言語 L0 対話頻出度 | w1qb03 minority A（3 言語先取り） | 頻出 3 言語が L0 対話確定の場合は推奨プリセット化 |
| AgentShield npm install 推奨実績 | w2qb02 minority A（utilizer 側手動 install 推奨可） | 利用者側の実 install 観察 |
| Wave 1 ECC-SURVEY 6 ヶ月再観察予約 | 2026-11-11 予定 | ECC 進化追従 |

これらは **Wave 4 Phase A 起票時点で評価できない**（運用データ蓄積待ち）。Wave 4 Phase B / 後続セッションで再評価し、再諮問の起票判断材料とする。

---

## 2. Wave 4 候補一覧と優先順位

### 2.1 優先 1: 議題 W4-Q1（minority opinion C 再諮問: 3 段階 vs 4 段階モデル）

Wave 3 PR #81 で明文化された philosophy 第 8 条「自律性原則 + 哲学ガードレール」が conf 0.55 接近採決であった経験的揺らぎを踏まえ、minority opinion C（4 段階モデル拡張）を再諮問する。

#### 背景

Wave 3 で確定した条文:

> **第 8 条 自律性原則 + 哲学ガードレール**
>
> AI 自律性の拡張は、観測 → 候補化 → 人間最終承認 の **3 段階** を経由するものとする。各段階の自動化レベルは CTL に連動し、CTL 0 では候補出力すら抑止する（観察温存）。自律拡張の各機構（continuous-learning / instinct promotion / 自動 Issue 化 / 自動 PR merge 等）は、本条の 3 段階を経由しない経路を持たないことを設計時に検証する。

Wave 3 minority opinion C は、この 3 段階に「Council 採決」を明示的に挿入して **4 段階モデル** とする案:

> AI 自律性の拡張は、観測 → 候補化 → **Council 採決** → 人間最終承認 の 4 段階を経由するものとする。

#### 候補

- **A**: 3 段階モデル維持（Wave 3 採用版を再確認、minority C は温存継続として Wave 5/6 に申し送り）
- **B**: 4 段階モデルへ拡張（minority C 採用、第 8 条改訂、Council 採決を明示的段階化）
- **C**: ハイブリッド（CTL 連動で 3 段階 / 4 段階を切替、CTL 0-1 = 4 段階で Council 必須、CTL 2+ = 3 段階で Council 任意）

#### Council 諮問の重み配分

`category: conception` を適用（Wave 3 第 8 条諮問と同一規約）。`crosscut-council/council-weights.md` の規約に従い:

- base_weights.business: 経営者 3 / 開発者 4 / 哲学者 3
- situational_modifier.conception: 経営者 0 / 開発者 -1 / 哲学者 +2
- **final_weights = 経営者 3 / 開発者 3 / 哲学者 5**

#### 判定基準

- conf ≥ 0.70: 採決確定、Wave 4 Phase C で実装
- conf 0.55 < x < 0.70: 採用候補に応じて Phase C で部分実装、minority は Wave 5 再諮問温存
- conf ≤ 0.55: Wave 3 接近採決の再現 → Wave 5 で再々諮問、本 Wave では第 8 条改訂を保留

#### 哲学者視点の予想論点

- ユーザー語彙「私の哲学ありき」「専門家叡智で固めて私の哲学を行使する」は、Council 採決を明示段階化する案 B 側を強く支持し得る
- 一方、Wave 3 で 3 段階モデルが既に「人間最終承認」を明示しているため、案 A 側からは「Council 採決は人間最終承認の前段で重複」との反論が想定される
- ハイブリッド案 C は CTL 連動を新たに哲学条文に組込む点で「条文の薄さ」原則からの逸脱リスク

### 2.2 優先 2: 議題 W4-Q2（L0 対話パイプラインへの ECC 参照モード組込）

ユーザー不満 3 点（実践での自立駆動の甘さ / Copilot レビュー耐性出力品質 / 多様な開発対応）の **核心解決議題**。HANDOFF `5fd827fa-HANDOFFDHmetaskillindustryabsorption.md` の旧タスク B を Wave 4 着地として実装。

#### 背景

Wave 1-3 で ECC 由来要素は以下に着地済:

- `.claude/hooks.json`（公式 schema、5 event）+ `.claude/skills/crosscut-hook-observer/` — D3 配布 / D4 機構
- `.claude/skills/crosscut-continuous-learning/` — D3 配布、pattern 検出 → 候補出力（自動 promote 禁止）
- `templates/rules/common/agentshield-reference.md` — 利用者プロジェクト用参照導入規約
- `philosophy.md` 第 8 条 — D4 規範化

しかし **L0 spec-architect の対話 → 仕様生成パイプライン** に業界叡智を組込む機構は未実装。具体的には:

| サブフェーズ | 業界叡智参照モード追加内容 | 未実装 |
|---|---|---|
| `subphase-l03-api.md` | ECC agents 定義パターン参照モード（YAML frontmatter 規格、tools/model 指定） | 未実装 |
| `subphase-l04-transition.md` | ECC hooks イベントトリガ参照モード（PreToolUse/PostToolUse/Stop の典型適用先） | 未実装 |
| `subphase-l05-authz.md` | AgentShield 脆弱性パターン参照モード（102 ルール × 1,282 テストのカテゴリ） | 未実装 |
| `subphase-l06-invariants.md` | ECC Instincts 学習対象参照モード（Framework/Security/API パターン分類） | 未実装 |
| `subphase-common-protocol.md` | Phase γ（検証）に「業界叡智照合」観測駆動フック | 未実装 |
| `scaffold-checklist.md` | 業界叡智準拠の出力規約（ECC 互換配置: `~/.claude/agents/`, `~/.claude/skills/{name}/SKILL.md` 等） | 未実装 |

#### 哲学的整合性

本議題は **第 8 条 3 段階モデルに完全に乗る**:

- **観測**: `history/ECC-SURVEY-2026-05-11.md` + `history/refs-draft/ecc/` 配下 5 ファイル（Wave 1 で archive 済）
- **候補化**: L0 対話中に subphase が業界叡智を参照、候補を SPEC 生成材料として提示
- **人間最終承認**: spec-architect 対話の末尾で SPEC 確定（ユーザー承認、philosophy 第 6 条）

業界叡智は **生成材料** であって最終出力ではない。最終出力は常にユーザー承認後の SPEC。第 8 条違反はない。

#### 候補

- **A**: フル組込（subphase-l03〜l06 + common-protocol + scaffold-checklist の **6 ファイル全改修**、Wave 4 Phase C で一括着地）
- **B**: 段階組込（**common-protocol Phase γ の業界叡智照合フックのみ Wave 4 で先行追加**、subphase 5 ファイルは Wave 5 で個別改修）
- **C**: 最小組込（**scaffold-checklist の出力規約強化のみ**、subphase / common-protocol は不変、Wave 5/6 で subphase 改修判断）

#### Council 諮問の重み配分

`category: implementation` 推奨（条文改修なし、機構実装）。`crosscut-council/council-weights.md` の規約に従い:

- base_weights.business: 経営者 3 / 開発者 4 / 哲学者 3
- situational_modifier.implementation: 経営者 -1 / 開発者 +2 / 哲学者 -1
- **final_weights = 経営者 2 / 開発者 6 / 哲学者 2**

#### 判定基準

- conf ≥ 0.65: 採決確定、Wave 4 Phase C で実装
- conf 0.50-0.65: 採用候補に応じて Phase C で部分実装
- conf ≤ 0.50: Wave 5 で再諮問、本 Wave では subphase 改修を保留

#### 経営者・開発者視点の予想論点

- **経営者**: ユーザー 3 不満の核心解決議題 → 候補 A 強く支持
- **開発者**: subphase 6 ファイル全改修は scope 大 → 候補 B（段階組込）で実装コスト分散を推奨する可能性
- **哲学者**: 業界叡智の組込度が深まるほど DH 哲学の独占性が希釈されるリスク → 候補 C（最小組込）を支持し得る

#### 部分採用シナリオ

採決結果次第で **W4-Q2 候補 B（段階組込）** に着地した場合の Wave 4 Phase C 実装範囲:

- `subphase-common-protocol.md` の Phase γ に「業界叡智照合フック」節を新規追加（推定 30-50 行）
- フックは観測駆動（CTL 連動）、出力は「候補リスト」のみで自動採用なし（第 8 条 3 段階 / 4 段階準拠）
- subphase-l03〜l06 + scaffold-checklist は Wave 5 申し送り

### 2.3 議題間の依存関係

```
W4-Q1（哲学ガードレール）採決
      ↓
（Phase B 順序厳守）
      ↓
W4-Q2（L0 対話パイプライン組込）採決
```

W4-Q1 で 4 段階モデル（候補 B）が採用された場合、W4-Q2 の「業界叡智照合フック」は 4 段階準拠で実装する必要が生じる（観測 → 候補化 → **Council 採決** → 人間最終承認）。W4-Q1 が 3 段階維持（候補 A）の場合、W4-Q2 は 3 段階準拠で実装。

したがって **Phase B 諮問順序 W4-Q1 → W4-Q2 を厳守し、W4-Q1 採決確定後に W4-Q2 を諮問する**。

---

## 3. Phase B 諮問順序と進行

### 3.1 諮問順序（厳守）

1. **W4-Q1**: minority C 再諮問（哲学先）
2. **W4-Q2**: L0 対話パイプライン組込（取込後、W4-Q1 結果を前提に実装範囲を確定）

### 3.2 Phase B 実装担当

`crosscut-council` Phase 1（SDK 独立呼出版、v5.10.0 PR #63 以降）を発動。3 ペルソナ（経営者 / 開発者 / 哲学者）並列独立判定 + 重み付き判定で `judgment_confidence` を算出。

### 3.3 Phase C 実装担当

- W4-Q1 採決結果が「3 段階維持」: `philosophy.md` 改修なし、`history/PHILOSOPHY-CHANGELOG.md` に「W4-Q1 で minority C を再諮問、3 段階維持を確認」を追記
- W4-Q1 採決結果が「4 段階拡張」: `harness-verifier/PHILOSOPHY.md` + `.claude/skills/layer0-spec-architect/references/philosophy.md` の二層実装に第 8 条改訂を反映、`history/PHILOSOPHY-CHANGELOG.md` 追記
- W4-Q1 採決結果が「ハイブリッド」: 上記 + `.claude/skills/crosscut-council/references/ctl-maturity-strategy.md` に CTL 連動規約追加
- W4-Q2 採決結果に応じて subphase / common-protocol / scaffold-checklist を改修

### 3.4 Wave 4 完遂条件

- W4-Q1 + W4-Q2 の 2 議題が採決済（または明示的に Wave 5 申し送り）
- 採決結果が `history/COUNCIL-LOG.md` に記録済
- Phase C 実装が PR merged 状態
- `history/CHANGELOG.md` に v5.13.x として Wave 4 完遂を記録

---

## 4. Wave 5 申し送り

### 4.1 議題候補

- W4-Q2 段階組込（候補 B）採用時の subphase 5 ファイル個別改修
- 他業界実装の咀嚼（BMAD / Cline / Aider 等）の Phase A 起点起票
- 業界別 rules / 言語別 patterns の本格取込（ECC rules/ 14 言語別 + common 10 ファイル準拠）
- ECC-SURVEY 6 ヶ月再観察（2026-11-11 予定）の更新
- 17 skill description / frontmatter 監査の進捗評価
- Wave 1 で棄却 + Wave 3 で PreCompact のみ採用となった残 3 hook event（UserPromptSubmit / Notification / SubagentStop）の Wave 4 / 5 申し送り再評価（`crosscut-hook-observer` SKILL.md 起源）

### 4.2 v6.0.0 温存項目（継続）

- 献上 3 軸構造（トリガー × 中身 × 権限）
- cookpato A3「タイムゾーン履歴記憶」を philosophy 第 9 条候補に昇格
- guardian 機構（destructive change detector / circuit breaker）の観測駆動追加（v5.6.x patch 想定）
- ALLOWED_AUTHORS 動的化（複数 contributor 体制）

### 4.3 不文律の明文化候補

- フラクタル自己適用（DH が DH に DH を適用）の規律化
- auto-merge opt-out 4 実装要件（roll-back protocol / メタ承認機構 / 既存ラベル廃止 / 境界 SPEC 不変化）の v5.9.0 Council 後の残課題回収

---

## 5. 本ファイルの archive 予定

Wave 4 Phase C 完了後、PR #79 の archive 方針に倣い `history/wave4/CHEW-PROTOCOL-SPEC-wave4-starter.md` に移動。同時に `delivery/CHEW-PROTOCOL-SPEC-wave3-starter.md` も `history/wave3/` に archive（Wave 3 完了済のため繰越 archive 対象）。

---

## 6. 参照ファイル一覧

### 6.1 Wave 1-3 SPEC starter

- `history/wave1/CHEW-PROTOCOL-SPEC-wave1-starter.md`
- `history/wave2/CHEW-PROTOCOL-SPEC-wave2-starter.md`
- `delivery/CHEW-PROTOCOL-SPEC-wave3-starter.md`（archive 予定）

### 6.2 Wave 3 PHILOSOPHY 関連

- `harness-verifier/PHILOSOPHY.md`（第 8 条本文）
- `.claude/skills/layer0-spec-architect/references/philosophy.md`（起点参考版）
- `history/PHILOSOPHY-CHANGELOG.md`
- `history/PHILOSOPHY-NOTE-autonomy-with-guardrails-2026-05-11.md`

### 6.3 Wave 1-3 Council 採決履歴

- `history/COUNCIL-LOG.md`（全 Council 採決履歴、append-only）

### 6.4 Council 規約

- `.claude/skills/crosscut-council/council-weights.md`（L0 編集権、本 Wave では編集なし）

### 6.5 L0 サブフェーズ（W4-Q2 改修対象候補）

- `.claude/skills/layer0-spec-architect/references/subphase-l03-api.md`
- `.claude/skills/layer0-spec-architect/references/subphase-l04-transition.md`
- `.claude/skills/layer0-spec-architect/references/subphase-l05-authz.md`
- `.claude/skills/layer0-spec-architect/references/subphase-l06-invariants.md`
- `.claude/skills/layer0-spec-architect/references/subphase-common-protocol.md`
- `.claude/skills/layer0-spec-architect/references/scaffold-checklist.md`

---

## 7. 起票時点の未確定事項（Phase B 採決後の解消ログ）

| 未確定事項（起票時点） | Phase B 採決後の解消結果 |
|---|---|
| W4-Q1 採決後の第 8 条本文最終形（3 段階 / 4 段階 / ハイブリッド） | **A 採決: 3 段階モデル維持**（conf 0.65、部分実装領域）。philosophy.md 改修なし、PHILOSOPHY-CHANGELOG に追記、Wave 4 末観測項目 3 種を必須化、minority C は Wave 5 温存。`council-2026-05-11T19:00:00Z-w4qb01` |
| W4-Q2 採決後の subphase 改修範囲（A フル / B 段階 / C 最小） | **B 採決: 段階組込**（conf 0.78、全会一致、採決確定）。`subphase-common-protocol.md` Phase γ に業界叡智照合フック (Phase γ-i) を新規追加、subphase-l03〜l06 + scaffold-checklist は Wave 5 申し送り。`council-2026-05-11T19:30:00Z-w4qb02` |
| Wave 4 Phase B 実施日時 | **2026-05-11T19:00:00Z 〜 19:35:00Z 実施完了**（W4-Q1 → W4-Q2 順序厳守、§3.1 規約通り） |
| Wave 4 Phase C 実装担当 | **本 PR (Wave 4 Phase B+C 統合) で実装**: Phase γ-i フック追加 (`subphase-common-protocol.md`) + COUNCIL-LOG 追記 + PHILOSOPHY-CHANGELOG 追記。subphase 個別改修は Wave 5 申し送り |

## 8. Wave 4 末振り返り儀式観測項目（Phase B 採決で必須化）

W4-Q1 + W4-Q2 採決の合流結果として、Wave 4 末振り返り儀式（spec-architect L0 が主催）で **以下 5 項目を必須観測** する:

1. **Council 経由率**（W4-Q1 D 案吸収）— 3 段階運用時に Council を実際に経由した判断の割合、minority C 再諮問の Wave 5 起票判断材料
2. **3 段階運用実績**（W4-Q1）— 観測 → 候補化 → 人間最終承認の各段階での通過件数、漏れ検出
3. **minority C 再評価データ蓄積**（W4-Q1）— Council 経由率 ≤ 20% 観測時の Wave 5 再諮問可否
4. **業界叡智参照を経た SPEC の unedited merged 率**（W4-Q2 哲学者 concerns）— DH 哲学独占性希釈リスク監視
5. **業界叡智照合フック起動回数 / 候補リスト採用率 / 却下率**（W4-Q2）— Phase γ-i フック運用実績

Phase B 諮問結果を本ファイルに反映済。Phase C 実装完了後 `history/wave4/` に archive 予定（`delivery/CHEW-PROTOCOL-SPEC-wave3-starter.md` も Wave 3 完了済繰越 archive 対象）。
