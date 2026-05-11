# 咀嚼プロトコル Wave 5 SPEC starter（ドラフト）

**起票**: 2026-05-11T20:00:00Z（Wave 4 PR #84 merged 後続）
**起票元**: spec-architect L0 経由、Wave 4 末振り返り儀式（レベル 3）の集計結果に基づく Wave 5 起票
**branch**: `claude/wave-5-prioritization-8jnio`（Wave 5 着手用、master の Wave 命名規則準拠）
**Phase**: Phase A — SPEC ドラフト起草 + 優先順位確定 + Council 諮問 agenda 提示

---

## 0. 本ファイルの位置づけ

咀嚼プロトコル Wave 5 の **Phase A 起点ファイル**。Wave 1 SPEC（PR #76 merged）+ Wave 2 SPEC（PR #77 + PR #78 merged）+ Wave 3 SPEC（PR #81 merged、第 8 条明文化）+ Wave 4 SPEC（PR #83 採決 + PR #84 完遂、minority C 再諮問 3 段階維持 + Phase γ-i フック先行実装）の到達点と minority opinion / 申し送り素材を継承し、Wave 5 で着手すべき候補群を整理して Phase B 諮問 agenda を提示する。

Wave 5 の構造的特徴は **観測駆動 Wave**。Wave 4 末で 5 観測項目が必須化されたが Wave 4 完遂直後（2026-05-11）のためすべて BL=0（観測ベースライン未蓄積）。Wave 5 は **観測機構の本格稼働（W5-Q0）+ 観測非依存の subphase 個別改修（W5-Q2）** を二本柱とし、観測依存議題（W5-Q1 / W5-Q3）は Wave 6/7 申し送りとする。

**順序の哲学**: ユーザー方針「先にガードレール、後で取込拡張」に従い、W5-Q0（観測機構稼働化 = ガードレール基盤）を W5-Q2（取込拡張本格化）の前に Wave 5 Phase A で実装着地させる。Wave 5 Phase B 諮問は W5-Q2 単独。

---

## 1. Wave 1 + 2 + 3 + 4 振り返り

### 1.1 完遂事項

| Wave | PR | 主要成果 |
|---|---|---|
| Wave 1 | #76 | 咀嚼プロトコル枠組み確立、5 hooks event 採用、skill description 監査（逐次）、templates/rules 階層化、observation/hook 観測機構整備 |
| Wave 2 Phase A | #77 | Wave 2 SPEC ドラフト、ファイル意図ベース配置規則の確立 |
| Wave 2 Phase B+C | #78 | HV 検査項目 6（hook 観測一貫性）、crosscut-continuous-learning 新設、origin/version frontmatter 規格、AgentShield 参照導入規約 |
| 移行 | #79 | PR #77 規約準拠で過去 Wave ファイル 36 件を `history/` archive |
| Wave 3 Phase A | #80 | Wave 3 SPEC ドラフト、議題 3（第 8 条本格諮問）優先 1 確定 |
| Wave 3 Phase B+C | #81 | philosophy 第 8 条明文化（候補 A 採用、3 段階モデル「観測 → 候補化 → 人間最終承認」、conf 0.55、minority C 温存） |
| Wave 4 Phase A | #82 | Wave 4 SPEC ドラフト、W4-Q1（minority C 再諮問）/ W4-Q2（subphase 改修）優先順位確定 |
| Wave 4 Phase B+C | #83 | W4-Q1 採決 A: 3 段階維持（conf 0.65、minority C 再温存）、W4-Q2 採決 B: 段階組込（conf 0.78 全会一致、Phase γ-i フック先行実装）|
| Wave 4 完遂 | #84 | Wave 4 starter archive、PHILOSOPHY-CHANGELOG W4-Q1 エントリ追加、Wave 4 末振り返り儀式観測項目 5 種を必須化 |

### 1.2 確認された経験的事実

#### B 系収束パターンの 4 サンプル目とその例外

Wave 1 Phase B（3 諮問 + 1 省略）+ Wave 2 Phase B（3 諮問 + 1 省略）+ Wave 3 Phase B（4 諮問）+ Wave 4 Phase B（2 諮問）の収束パターン：

| Wave | 諮問件数 | A 採決 | B 採決 | 接近採決 |
|---|---|---|---|---|
| Wave 1 | 3 | w1qb03 のみ（言語先取りなし= A） | w1qb01-02 | 0 件 |
| Wave 2 | 3 | 0 件 | w2qb01-03 | 0 件 |
| Wave 3 | 3 | w3qb01（第 8 条 3 段階明文化、A 採決、conf 0.55 接近採決）| w3qb02-03 | 1 件（w3qb01）|
| Wave 4 | 2 | w4qb01（minority C 再諮問結果、A: 3 段階維持、conf 0.65）| w4qb02（段階組込、conf 0.78）| 0 件（w4qb01 は明確判定、conf gap 1.81） |

**Wave 4 W4-Q1 の意義**: Wave 3 で接近採決（conf 0.55）だった哲学者 stance C の conf が Wave 4 で 0.85 → 0.55 に下落し、weighted score gap が 0.10 → 1.81 へ拡大して明確判定（A: 3 段階維持、conf 0.65）に至った。これは「観測駆動による哲学者 conf 補正」という DH 哲学（philosophy §3 情報純度 + 第 8 条 3 段階）の動作証拠であり、PHILOSOPHY-CHANGELOG W4-Q1 エントリ §意義で記録済。

T3（サブセット選別）+ ガードレール語彙化が DH 哲学の自然な帰結として動作する **4 サンプル目** を蓄積。Wave 5 ではこの収束パターンが観測機構稼働後にどう変化するかを観測対象とする。

### 1.3 Wave 4 末振り返り儀式の観測項目集計（2026-05-11T20:00:00Z 時点）

Wave 4 末振り返り儀式（spec-architect L0 主催、本 starter 起票セッション）で集計した 5 観測項目の結果：

| # | 観測項目（Wave 4 starter §8） | 集計値（2026-05-11） | データ蓄積判定 | 起源議題 |
|---|---|---|---|---|
| 1 | Council 経由率（3 段階運用時に Council を経由した判断割合） | **0/0 = 算出不能**（Wave 4 採決後 Council 起動 0 件） | ベースライン未蓄積 | W4-Q1 D 案吸収 |
| 2 | 3 段階運用実績（観測→候補化→人間最終承認 各段階通過件数） | **0 / 0 / 0**（hook 観測 0 / continuous-learning 候補出力 0 / 該当承認 0） | ベースライン未蓄積 | W4-Q1 |
| 3 | minority C 再評価データ蓄積 | **判定不能**（≤ 20% 閾値の母数 = 0）| 閾値判定不可 | W4-Q1 |
| 4 | 業界叡智参照を経た SPEC の unedited merged 率 | **N/A**（Phase γ-i 起動 0 回 → 該当 SPEC merged 0 件）| ベースライン未蓄積 | W4-Q2 哲学者 concerns |
| 5 | Phase γ-i フック起動回数 / 候補採用率 / 却下率 | **0 / 0% / 0%** | ベースライン未蓄積 | W4-Q2 |

**集計総括**: Wave 4 完遂が 2026-05-11、本 starter 起票セッションが Wave 4 完遂後の最初の判断発生機会。5 項目すべて運用データ未蓄積。これは想定通り（Wave 3 starter §1.3 でも「Phase A 起票時点で評価できない、運用データ蓄積待ち」前例あり）。Wave 5 は **観測ベースラインを BL=0 / 起算日 = 2026-05-11 として記録する** Wave と位置づけ、W5-Q0（観測機構稼働化）で観測サイクル開始 → Wave 5 末で観測 1 サイクル経過の母数を蓄積する。

#### 観測データの取得経路（メタスキル開発による自己観測で完結）

DH 第 1 条フラクタル原則により、観測データは **実プロジェクト不要**、本リポジトリの DH メタスキル開発セッション（= Claude Code 利用）自体を観測対象として取得可能：

| データ種別 | 物理ファイル | 取得経路 | メタ取得可否 |
|---|---|---|---|
| A. hook 観測ログ | `harness-verifier/reports/hook-observations.jsonl` | `.claude/hooks.json` → `crosscut-hook-observer` 経由（PreToolUse/PostToolUse/Stop/SessionStart/SessionEnd/PreCompact の 6 event） | ✅ メタ取得可（W5-Q0 で稼働化）|
| B. 候補出力ログ | `delivery/CONTINUOUS-LEARNING-CANDIDATES-<timestamp>.md` | `crosscut-continuous-learning` skill が A を読み込み pattern 検出 | ✅ A 蓄積後に自動取得 |
| C. 判断/フック起動カウンタ | `history/COUNCIL-LOG.md` + Phase γ-i フックの起動ログ | Wave 5/6/7… の自然進行 + subphase 起動を含む L0 対話 | ✅ Wave 進行で自然取得 |

項目 1-3 は Wave 進行で自然蓄積。項目 4-5 は subphase L0-3/4/5/6 起動を含む L0 対話（新規 crosscut-* skill 策定 or 既存 skill 改修）が必要で、Wave 5 以降の自然発生に依存。

---

## 2. Wave 5 候補一覧と優先順位

### 2.1 W5-Q0: 観測機構稼働化（議題ではなく実装タスク、Phase A 着地）

Wave 4 末で必須化された 5 観測項目のうち項目 1-3 を Wave 5 末以降に蓄積開始可能にするため、`.claude/hooks.json` を本リポジトリで有効化し、`crosscut-hook-observer` skill 経由の観測サイクルを能動的に開始する。

#### 背景

Wave 1 PR #76 で hook 観測機構（`.claude/skills/crosscut-hook-observer/`）と HV 検査項目 6（hook 観測一貫性）が整備されたが、利用者プロジェクト側の `.claude/hooks.json` 有効化セッションが未発生のため、`harness-verifier/reports/hook-observations.jsonl` が物理的に未生成。

DH 第 1 条フラクタル原則（DH を使って DH を改良する）により、観測者 = 被観測者の自己観測で観測サイクルは完結する。本リポジトリ自身のメタスキル開発セッション（本 starter 起票以降の全 Claude Code 利用）を観測対象とすることで、実プロジェクト不要で観測データ蓄積が開始可能。

#### 実装内容

1. `.claude/hooks.json` を本リポジトリに新設（または既存設定の有効化確認）
2. `.claude/skills/crosscut-hook-observer/scripts/bootstrap.py` の `SUPPORTED_EVENTS` 定義（および `.claude/hooks.json` の `adopted_events`、PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd / PreCompact の 6 event、Wave 3 PR #81 で PreCompact 追加済）が hooks.json schema に整合していることを確認
3. `harness-verifier/reports/hook-observations.jsonl` を append-only で初期化（exit code 常 0 / warn のみ / block しない、philosophy 第 6 条「人間最終承認」準拠）
4. 初回観測（本 starter 起票セッションの SessionStart / Stop event）が hook-observations.jsonl に記録されることを smoke test として確認

#### 諮問判定: 諮問省略

- 緊張度 **軽微**（観測機構稼働化は philosophy 本体に変更なし、Wave 1 で整備済機構の有効化）
- tradeoff 不在（CTL 連動で観測層稼働は philosophy 第 8 条 3 段階の前提条件）
- 観測層 = 第 8 条 3 段階モデルの第 1 段（観測）= 稼働化は第 8 条準拠そのもの
- chewing protocol §3 諮問判定 `confidence ≥ 0.7` 基準を満たす
- **implementer_consent: auto_proceed**

### 2.2 W5-Q2: subphase 個別改修（諮問議題、優先 1）

Wave 4 W4-Q2 採決 B（段階組込、conf 0.78 全会一致）の Wave 5 申し送り直接後続。`subphase-l03-api.md` / `subphase-l04-transition.md` / `subphase-l05-authz.md` / `subphase-l06-invariants.md` + `scaffold-checklist.md` の **5 ファイル改修** で業界叡智参照モードを subphase レベルで本格組込する。

#### 背景

Wave 4 W4-Q2 では `subphase-common-protocol.md` Phase γ に「業界叡智照合フック (Phase γ-i)」が先行追加されたが、各 subphase 個別の業界叡智参照モード（ECC agents 定義パターン / hooks イベントトリガ / AgentShield 脆弱性パターン / Instincts 学習対象 / scaffold 出力規約）は Wave 5 申し送りとなった。

| サブフェーズ | 業界叡智参照モード追加内容 | Wave 4 状態 | Wave 5 着地候補 |
|---|---|---|---|
| `subphase-l03-api.md` | ECC agents 定義パターン参照モード（YAML frontmatter 規格、tools/model 指定） | 未実装 | W5-Q2 候補 A/B 対象 |
| `subphase-l04-transition.md` | ECC hooks イベントトリガ参照モード（PreToolUse/PostToolUse/Stop の典型適用先） | 未実装 | W5-Q2 候補 A/B 対象 |
| `subphase-l05-authz.md` | AgentShield 脆弱性パターン参照モード（102 ルール × 1,282 テストのカテゴリ） | 未実装 | W5-Q2 候補 A/B 対象 |
| `subphase-l06-invariants.md` | ECC Instincts 学習対象参照モード（Framework/Security/API パターン分類） | 未実装 | W5-Q2 候補 A/B 対象 |
| `scaffold-checklist.md` | 業界叡智準拠の出力規約（ECC 互換配置: `~/.claude/agents/`, `~/.claude/skills/{name}/SKILL.md` 等） | 未実装 | W5-Q2 候補 A/B 対象 |

#### 候補

- **A**: 5 ファイル一括改修（Wave 5 Phase C で完遂、W4-Q2 採決 B の Wave 5 完結着地）
- **B**: 2-3 ファイル先行改修（subphase-l03-api + scaffold-checklist など外部結合度高い順、残 2-3 ファイルは Wave 6 申し送り）
- **C**: 全延期（Wave 5 では subphase 改修なし、Wave 6 で再起票）

#### Council 諮問の重み配分

`category: implementation` 適用（W4-Q2 と同一カテゴリ、subphase ファイル改修で条文改修なし）。`.claude/skills/crosscut-council/council-weights.md` の規約に従い：

- base_weights.business: 経営者 3 / 開発者 4 / 哲学者 3
- situational_modifier.implementation: 経営者 -1 / 開発者 +2 / 哲学者 -1
- **final_weights = 経営者 2 / 開発者 6 / 哲学者 2**

#### 判定基準

- conf ≥ 0.65: 採決確定、Wave 5 Phase C で実装
- conf 0.50-0.65: 採用候補に応じて Phase C で部分実装
- conf ≤ 0.50: Wave 6 で再諮問、本 Wave では subphase 改修を保留

#### 経営者・開発者・哲学者視点の予想論点

- **経営者**: W4-Q2 採決 B の Wave 5 着地でユーザー 3 不満（自立駆動 / Copilot 耐性 / 多様な開発対応）の核心解決完結 → 候補 A 強く支持
- **開発者**: 5 ファイル改修は L0 対話中核に影響する scope 中だが、Phase γ-i フックが先行実装済で骨格固定 → 候補 A 採用可能、ただし Wave 5 内テスト範囲が広がるため候補 B（分割）も推奨し得る
- **哲学者**: Wave 4 W4-Q2 採決時の concerns「業界叡智組込深化による DH 哲学独占性希釈リスク」を Wave 5 末観測項目 4（業界叡智参照を経た SPEC の unedited merged 率）で監視する条件で候補 A を支持。候補 C は W4-Q2 採決 B を実質撤回するため明確に反対

#### 部分採用シナリオ

採決結果が **W5-Q2 候補 B（2-3 ファイル先行改修）** の場合の Wave 5 Phase C 実装範囲（推奨優先順）：

1. `subphase-l03-api.md`（最も外部結合度高い、ECC agents 定義パターン参照モード）
2. `scaffold-checklist.md`（出力規約強化、L1 への影響度高）
3. `subphase-l05-authz.md`（AgentShield 脆弱性カテゴリ、セキュリティ補強）

残 `subphase-l04-transition.md` + `subphase-l06-invariants.md` は Wave 6 申し送り。

### 2.3 議題間の依存関係

```
W5-Q0（観測機構稼働化、Phase A 着地、議題なし）
      ↓
（W5-Q0 完遂で観測サイクル開始）
      ↓
W5-Q2（subphase 5 ファイル改修、Phase B 諮問 + Phase C 実装）
      ↓
（Wave 5 末で観測 1 サイクル経過、項目 1-3 母数蓄積）
      ↓
Wave 6 で W5-Q1（minority C 再諮問）の起票判断
Wave 7 で W5-Q3（残 3 hook event 再評価）の起票判断
```

W5-Q0 と W5-Q2 は依存なし（並列実装可能）だが、Phase A で W5-Q0 を先行着地させることで Wave 5 内の観測サイクルを最大化する。

---

## 3. Phase B 諮問順序と進行

### 3.1 諮問順序

1. **W5-Q2 単独**: subphase 5 ファイル改修範囲の採決

W5-Q0 は諮問省略（§2.1 implementer_consent: auto_proceed）。W5-Q1 / W5-Q3 は Wave 6/7 申し送り（観測サイクル経過待ち）。

### 3.2 Phase B 実装担当

`crosscut-council` Phase 1（SDK 独立呼出版、v5.10.0 PR #63 以降）を発動。3 ペルソナ（経営者 / 開発者 / 哲学者）並列独立判定 + 重み付き判定で `judgment_confidence` を算出。

### 3.3 Phase C 実装担当

- W5-Q2 採決結果が **A: 5 ファイル一括**: 5 ファイルすべてを Wave 5 Phase C で改修、harness-verifier --strict PASS 確認
- W5-Q2 採決結果が **B: 2-3 ファイル先行**: §2.2 部分採用シナリオの推奨優先順で着地、残は Wave 6 申し送り
- W5-Q2 採決結果が **C: 全延期**: Phase C 実装なし、Wave 6 で再起票

### 3.4 Wave 5 完遂条件

- W5-Q0 が Phase A で実装着地（`.claude/hooks.json` 有効化 + hook-observations.jsonl 初回 entry 確認）
- W5-Q2 採決済（または明示的に Wave 6 申し送り）
- 採決結果が `history/COUNCIL-LOG.md` に記録済
- Phase C 実装が PR merged 状態
- `history/CHANGELOG.md` に v5.14.x 系として Wave 5 完遂を記録
- Wave 5 末振り返り儀式観測項目（§8）の集計実施

---

## 4. Wave 6/7 申し送り

### 4.1 議題候補（観測サイクル経過後に起票判断）

#### Wave 6 候補

- **W5-Q1 → Wave 6 着地**: minority C 再諮問（3 段階 vs 4 段階 / ハイブリッド）
  - 起票条件: Wave 5 末で Council 経由率 ≤ 20% が確認された場合
  - 母数閾値: COUNCIL-LOG.md エントリで Wave 5 起算 ≥ 10 件
  - Wave 4 W4-Q1 minority C 温存条件と同一規約
- W5-Q2 候補 B（部分採用）採用時の subphase 残 2-3 ファイル改修
- ECC-SURVEY 6 ヶ月再観察（2026-11-11 予定）の更新
- 17 skill description / frontmatter 監査の進捗評価

#### Wave 7 候補

- **W5-Q3 → Wave 7 着地**: 残 3 hook event 再評価（UserPromptSubmit / Notification / SubagentStop）
  - 起票条件: w3qb02 minority A 再諮問条件「observation log ≥ 500 件 + PreCompact entry ≥ 5% 占有」充足時
  - 母数閾値: hook-observations.jsonl entry ≥ 500 件
- 他業界実装の咀嚼（BMAD / Cline / Aider 等）の Phase A 起点起票
- 業界別 rules / 言語別 patterns の本格取込（ECC rules/ 14 言語別 + common 10 ファイル準拠）

### 4.2 v6.0.0 温存項目（継続）

- 献上 3 軸構造（トリガー × 中身 × 権限）
- cookpato A3「タイムゾーン履歴記憶」を philosophy 第 9 条候補に昇格
- guardian 機構（destructive change detector / circuit breaker）の観測駆動追加（v5.6.x patch 想定）
- ALLOWED_AUTHORS 動的化（複数 contributor 体制）

### 4.3 不文律の明文化候補

- フラクタル自己適用（DH が DH に DH を適用）の規律化 — **Wave 5 で W5-Q0 が初の明示的フラクタル自己観測実装となる**、philosophy 第 9 条候補
- auto-merge opt-out 4 実装要件（roll-back protocol / メタ承認機構 / 既存ラベル廃止 / 境界 SPEC 不変化）の v5.9.0 Council 後の残課題回収

---

## 5. 本ファイルの archive 予定

Wave 5 Phase C 完了後、Wave 4 starter（PR #84 で archive）の方針に倣い `delivery/CHEW-PROTOCOL-SPEC-wave5-starter.md` を `history/wave5/CHEW-PROTOCOL-SPEC-wave5-starter.md` に移動する。

---

## 6. 参照ファイル一覧

### 6.1 Wave 1-4 SPEC starter

- `history/wave1/CHEW-PROTOCOL-SPEC-wave1-starter.md`
- `history/wave2/CHEW-PROTOCOL-SPEC-wave2-starter.md`
- `history/wave3/CHEW-PROTOCOL-SPEC-wave3-starter.md`
- `history/wave4/CHEW-PROTOCOL-SPEC-wave4-starter.md`

### 6.2 Wave 3-4 PHILOSOPHY 関連

- `harness-verifier/PHILOSOPHY.md`（第 8 条本文）
- `.claude/skills/layer0-spec-architect/references/philosophy.md`（起点参考版）
- `history/PHILOSOPHY-CHANGELOG.md`（Wave 3 第 8 条追加 + Wave 4 W4-Q1 3 段階維持再確認の 2 エントリ）
- `history/PHILOSOPHY-NOTE-autonomy-with-guardrails-2026-05-11.md`

### 6.3 Wave 1-4 Council 採決履歴

- `history/COUNCIL-LOG.md`（全 Council 採決履歴、append-only、Wave 4 完遂時点 1640 行）

### 6.4 Council 規約

- `.claude/skills/crosscut-council/council-weights.md`（L0 編集権、本 Wave では編集なし）

### 6.5 W5-Q0 関連（観測機構稼働化）

- `.claude/skills/crosscut-hook-observer/SKILL.md`（hook 観測機構本体）
- `.claude/hooks.json`（W5-Q0 で新設または有効化確認）
- `harness-verifier/reports/hook-observations.jsonl`（W5-Q0 完遂で初回 entry 生成）
- `harness-verifier/checks/hook_observations.py`（HV 検査項目 6）

### 6.6 W5-Q2 改修対象（5 ファイル）

- `.claude/skills/layer0-spec-architect/references/subphase-l03-api.md`
- `.claude/skills/layer0-spec-architect/references/subphase-l04-transition.md`
- `.claude/skills/layer0-spec-architect/references/subphase-l05-authz.md`
- `.claude/skills/layer0-spec-architect/references/subphase-l06-invariants.md`
- `.claude/skills/layer0-spec-architect/references/scaffold-checklist.md`

### 6.7 W5-Q2 関連（Wave 4 で実装済の基盤）

- `.claude/skills/layer0-spec-architect/references/subphase-common-protocol.md`（Wave 4 PR #83 で Phase γ-i フック追加済）

---

## 7. 起票時点の未確定事項（Phase B 採決後の解消ログ）

| 未確定事項（起票時点） | Phase B 採決後の解消結果 |
|---|---|
| W5-Q2 採決結果（A フル / B 部分 / C 全延期） | **B 採決: 2-3 ファイル先行改修**（conf 0.72、採決確定領域）。`subphase-l03-api.md` + `scaffold-checklist.md` + `subphase-l05-authz.md` の 3 ファイル先行、残 `subphase-l04-transition.md` + `subphase-l06-invariants.md` は Wave 6 申し送り。`council-2026-05-11T12:15:00Z-w5qb02` |
| W5-Q2 採決結果が B の場合の改修対象 2-3 ファイル選定 | **3 ファイル選定**: subphase-l03-api（外部結合度最高）+ scaffold-checklist（L1 影響度最高）+ subphase-l05-authz（AgentShield カテゴリ最小スコープ）。開発者 Persona 推奨優先順準拠 |
| Wave 5 Phase B 実施日時 | **2026-05-11T12:15:00Z 〜 12:15:30Z 実施完了**（W5-Q2 単独諮問、§3.1 規約通り）|
| Wave 5 Phase C 実装担当 | **本 PR (Wave 5 Phase C) で 3 ファイル改修実装完了**: `subphase-l03-api.md` + `scaffold-checklist.md` + `subphase-l05-authz.md` にそれぞれ「業界叡智参照モード」セクション追加、Phase γ-i フック連携 + CTL 連動 + 第 8 条 3 段階モデル準拠。HV 検査 6 項目すべて PASS。残 `subphase-l04-transition.md` + `subphase-l06-invariants.md` は Wave 6 申し送り |
| W5-Q0 完遂後の初回 hook 観測 entry 件数（smoke test 結果） | **SessionStart + Stop の 2 entry**（PR #86 で hook-observations.jsonl 物理生成、HV 検査 6 項目 PASS、観測サイクル起算 2026-05-11T12:08:47Z）|

---

## 8. Wave 5 末振り返り儀式観測項目

Wave 4 末で必須化された 5 観測項目（Wave 4 starter §8）を Wave 5 末でも継続観測する。Wave 5 では W5-Q0 完遂により観測機構が稼働するため、**項目 1-3 は Wave 5 起算で hook 観測機構稼働により自然蓄積が始まる**。**項目 4-5 は subphase L0-3/4/5/6 を起動する L0 対話（新規 crosscut-* skill 策定 or 既存 skill 改修等）が発生すれば蓄積開始**（§1.3「観測データの取得経路」表と整合）：

1. **Council 経由率**（W4-Q1 D 案吸収継承）— Wave 5 起算の COUNCIL-LOG.md エントリ件数 + Council 経由判断の割合。Wave 6 で W5-Q1（minority C 再諮問）起票判断材料
2. **3 段階運用実績**（W4-Q1 継承）— hook-observations.jsonl entry 件数 / continuous-learning 候補出力件数 / 該当承認件数の 3 段階通過カウント
3. **minority C 再評価データ蓄積**（W4-Q1 継承）— Council 経由率 ≤ 20% 観測時の Wave 6 再諮問可否判定
4. **業界叡智参照を経た SPEC の unedited merged 率**（W4-Q2 哲学者 concerns 継承）— DH 哲学独占性希釈リスク監視
5. **業界叡智照合フック起動回数 / 候補リスト採用率 / 却下率**（W4-Q2 継承）— Phase γ-i フック運用実績

### Wave 5 固有の追加観測項目

W5-Q0 完遂で観測機構が初稼働するため、Wave 5 末では以下 2 項目を **Wave 5 限定の補助観測項目** として追加する：

6. **hook-observations.jsonl 初回観測ベースライン**（W5-Q0 完遂後の entry 件数 / event 種別分布 / SessionStart-Stop 対応関係の整合性）
7. **フラクタル自己観測の動作確認**（DH メタスキル開発セッション = 観測対象 = 観測実施者 の 3 者一致が崩れていないか、philosophy 第 1 条フラクタル原則準拠）

項目 6-7 は Wave 6 以降の標準観測項目への昇格候補。Wave 5 末で項目 6 が想定通り蓄積されていれば項目 7 とともに Wave 6 振り返り儀式観測項目に追加する。

---

## 9. 哲学的注記

Wave 5 は咀嚼プロトコルの **観測駆動 Wave**：

- Wave 1: 枠組み確立（観察 + 候補抽出）
- Wave 2: 候補実装（HV + skill + 規約）
- Wave 3: 哲学言語化（B 系収束 2 サンプルを第 8 条として明文化）
- Wave 4: minority opinion 温存機構の初実証（W4-Q1 で Wave 3 接近採決 → Wave 4 明確判定への conf 推移を観測）+ 業界叡智組込の Phase γ-i フック先行実装
- **Wave 5: 観測機構の本格稼働 + 業界叡智組込の subphase 個別本格化**

W5-Q0（観測機構稼働化）は議題ではなく実装タスクだが、**DH 第 1 条フラクタル原則を初めて明示的に実装するマイルストーン**。観測者 = 被観測者 = 観測実施者の 3 者一致は DH 哲学の核心であり、Wave 5 で実体化される。

W5-Q2（subphase 5 ファイル改修）は W4-Q2 採決 B の Wave 5 完結着地で、ユーザー 3 不満（自立駆動の甘さ / Copilot レビュー耐性 / 多様な開発対応）の核心解決を完遂する。哲学者 concerns（DH 哲学独占性希釈リスク）は Wave 5 末観測項目 4 で監視継続。

`category: implementation` 適用（経営者 2 / 開発者 6 / 哲学者 2）は W4-Q2 と同一カテゴリで、実装議題における素直な配分。Wave 4 W4-Q2 が全会一致 conf 0.78 で採決された経験を踏まえ、Wave 5 W5-Q2 でも開発者重み優位の判定が期待される。

minority opinion 温存（W5-Q1 = Wave 6 / W5-Q3 = Wave 7）は観測駆動原則の厳格適用で、Wave 4 W4-Q1 で経験した「観測未蓄積で再諮問 → 哲学者 conf 下落 → 明確判定」の構造を再現しないための判断。観測サイクル経過後の再諮問が DH 第 8 条 3 段階モデルの精神に整合する。
