# 体制判定プロトコル

Layer 0（spec-architect）が開発モードを決定するためのスコアリングプロトコル。
規模（S）・不確実性（U）・リスク（R）の3軸で評価する。

> **S/U/R 用語対応**: `S = 規模 = Scale` / `U = 不確実性 = Uncertainty` / `R = リスク = Risk`。
> 用語の正典宣言は `harness-verifier/glossary.yml` の `score_axes` キーを参照。
> 同じ S/U/R 軸は本プロトコル（モード判定）以外でも使用される
> （例: `history/DH-PHILOSOPHY-INSIGHTS.md` §4.4 / §10.5 の判断モーメント介入閾値、
> `history/DIMENSIONS.md` §7.5 の hybrid 閾値）。射程・配点は文脈ごとに異なる。

---

## 判定原則

- 単体エージェントで足りるなら単体で回す（ワンマン優先）
- 分業は「個の能力不足」ではなく「責務の独立性」を根拠にする
- 分割軸は抽象度軸・責務軸・機能軸から選ぶ。職種軸（FE/BE/QA等）は採用しない
- 同一責務内に複数体を置くのは、生成と検証の分離または並列探索の場合に限る
- エージェント間通信は自然言語経由で必ず情報損失が発生することを前提にコスト計算する
- **フラクタル原則**: 同じS/U/R軸は全体判定にもサブドメイン判定にも適用可能

---

## 軸1：規模スコア（S）

プロジェクトの広がりを示す指標。対話で取得した情報から算出する。

| 指標 | スコア |
|---|---|
| 機能数 1〜3 | 1点 |
| 機能数 4〜10 | 2点 |
| 機能数 11〜 | 3点 |
| 画面数 0〜1（CLI・バッチ） | 0点 |
| 画面数 2〜5 | 1点 |
| 画面数 6〜 | 2点 |
| 登場人物（ユーザー種別）1種 | 0点 |
| 登場人物 2〜3種 | 1点 |
| 登場人物 4種〜 | 2点 |
| 外部連携 0 | 0点 |
| 外部連携 1〜2 | 1点 |
| 外部連携 3〜 | 2点 |

規模スコア範囲：0〜9点

## 軸2：不確実性スコア（U）

仕様の固まり具合・既知度・変更予測を示す指標。

| 指標 | スコア |
|---|---|
| イメージが鮮明（細部まで見えている） | 0点 |
| 大枠は明確、細部は曖昧 | 1点 |
| 「なんとなく」レベル | 2点 |
| 類似物を作った／使った経験あり | 0点 |
| 初めての領域 | 2点 |
| 一度作って終わり | 0点 |
| 継続的に更新する前提 | 1点 |

不確実性スコア範囲：0〜5点

## 軸3：リスクスコア（R）

失敗した場合の影響範囲を示す指標。

| 指標 | スコア |
|---|---|
| 壊れても問題なし（実験・学習用） | 0点 |
| 自分だけ使う（私的ツール） | 1点 |
| 他人に配布する（OSS・拡張機能等） | 2点 |
| 本番運用・金銭絡み | 3点 |

リスクスコア範囲：0〜3点

---

## 軸4：NFRスコア（N）

非機能要件の定量化。詳細配点・オーバーライドルールは `nfr-scoring.md` を参照。
S/U/R と並ぶ第4軸として判定フローに組み込む。

| カテゴリ | 範囲 | 備考 |
|---|---|---|
| 性能（P） | 0〜3 | レイテンシ SLO・スループット |
| 可用性（A） | 0〜3 | SLA・停止時の業務影響 |
| セキュリティ（S） | 0〜3 | PII / 決済 / 規制業界 |
| コンプライアンス（C） | 0〜3 | 法令・監査要件 |
| スケーラビリティ（L） | 0〜3 | 水平スケール・バースト対応 |

NFRスコア範囲：0〜15点

### UX 3問プロトコルとの関係

UX は独立軸として追加せず、NFR 軸内の補足として扱う。
L0 対話ステップ 2.5（UX 3問プロトコル）で取得した Must 閾値・禁止挙動・参考類似サービスは、SPEC.md の UX制約セクションに格納され、N の A（可用性）・L（スケーラビリティ）スコアの補正情報として参照される。詳細は `../SKILL.md` ステップ 2.5 を参照。

**デフォルト**: `REGIME.md` の NFR スコアセクションに記録がない、または対話で引き出せなかった場合は **N=0**。
**オーバーライドルール 4 条件**（詳細は `nfr-scoring.md`）:

- N ≥ 9 → ARC モノリス解除強制（arc-patterns/ から人間選択）
- N ≥ 5 → ARC 切替推奨 + 2段階化検討（推奨、強制ではない）
- セキュリティ ≥ 2 → M2 以上強制
- 可用性 = 3 → REGIME.md に権限レベル明示記録必須

---

## 軸5：LC 軸（1→5運用対応）

プロジェクトが新規か継続かを示す軸。`history/` の有無と経過日数で自動判定。
S/U/R スコアには影響しないが、**振り返り儀式のレベル判定**と **L0 処理フロー分岐**に使う。

| LC | 値 | 判定条件 | 履歴層の扱い |
|---|---|---|---|
| LC=0 | 新規 | `history/` なし | 新規作成のみ、儀式完全スキップ |
| LC=1 | 拡張 | `history/` あり、CHANGELOG.md 最終更新が30日以内 | INTENT/CHANGELOG 参照を必須化、儀式デフォルト レベル1 |
| LC=2 | 保守 | `history/` あり、CHANGELOG.md 最終更新が30日超 | 全履歴参照必須、儀式デフォルト レベル2以上 |

### LC 判定ロジック

```
1. history/ 存在確認
   なし → LC=0
2. history/CHANGELOG.md 最終更新日確認
   30日以内 → LC=1
   30日超 → LC=2
```

LC 判定は AI が履歴層から自動抽出する。人間に問わない。

---

## 儀式レベル判定（LC ≥ 1 で適用）

振り返り儀式のレベル（0〜3）を LC と対話発話から決定する。

| レベル | 条件 | 処理 |
|---|---|---|
| 0 | LC=0、または前回ループから経過なし | 完全スキップ |
| 1 | LC=1、機能変更なしの対話 | SUMMARY.md のみ、1問確認 |
| 2 | 機能追加・変更・廃止を含む対話 | SUMMARY + 関連 INTENT、2〜3問 |
| 3 | LC=2、90日超、規模変動±2以上 | history/ 全層、5〜10問 |

動的格上げ/格下げ、3フェーズ実行（F1/F2/F3）、E1（曖昧応答）/E2（儀式拒否）対応の詳細は `ritual-protocol.md` を参照。

---

## Council Trust Level（CTL）（v4.2 新規）

L0 spec-architect は REGIME.md 生成・更新時に Council Trust Level（CTL）を
算出し記録する。CTL は Council の自律実行範囲を動的決定する軸であり、
philosophy.md 第 6 条「人間 ≒ Council 原則」の実装規格。

算出ロジック・stats.json スキーマ・invocations/ 構造の詳細は
`crosscut-council/references/ctl-calculation.md` を参照。

### 算出手順

1. `~/.claude/council-data/stats.json` を読み込む
   - ファイル不存在の場合: user-scope を初期化（CTL-0 で運用開始）
2. `ctl-calculation.md` の `calculate_ctl(stats)` で CTL を算出
3. REGIME.md に以下を記録（モード定義ブロックと並列）:
   - `ctl: CTL-X`
   - `ctl_calculated_at: <ISO 8601>`
   - `delegation_scope: [自律実行されるカテゴリ]`
   - `escalation_categories: [献上されるカテゴリ]`
   - `council_data_version: <stats.json の version>`

### REGIME.md への記録フォーマット

```markdown
## Council Trust Level
- ctl: CTL-2
- ctl_calculated_at: 2026-04-25T10:30:00Z
- delegation_scope: [C1, C3, C4]
- escalation_categories: [C2]
- council_data_version: 0.1
```

`council_data_version` は `~/.claude/council-data/version.md` の `version` 値および
`stats.json` の `version` 値とリテラルが一致する（`v` 接頭辞は付けない）。

### CTL とモード（M1/M2/L2）の関係

CTL とモードは独立した軸。組み合わせ例:

| モード | CTL | 含意 |
|---|---|---|
| M1 + CTL-0 | 単体実行、Council 全件献上 | 新規ユーザー |
| M2 + CTL-2 | 標準実行、Council 大半が自律 | 慣れたユーザー |
| L2 + CTL-3 | 統括実行、Council 全面自律 | 熟練ユーザー、大規模プロジェクト |

### CTL-3 の例外

CTL-3 ではほぼ全ての C カテゴリが Council 自律。ただし以下は例外として
常に escalate_to_human:

- conflict_type が E（前提対立）または G（メタ対立）
- council_type が "life"（人生 Council）
- H カテゴリ抵触検知時（H1 哲学変更 / H2 ルール変更 / H3 方向性発案 / H4 根本設計見直し）

詳細は `crosscut-council/references/consensus-protocol.md` の `compute_consensus_mode` を参照。

---

## モード定義（3層設計）

### M1 単体モード（実験）

Layer 0 → Layer 1（自己検証のみ）で完結。

- 構成：Layer 0 → Layer 1（単体）
- 検証：L1自己検証（計算的センサー中心。推論的センサーは自己検証で兼用）
- 独立検証agent：**起動しない**
- 所要トークン：最小
- 適用：実験・学習・使い捨てツール・自分だけ使う小物

### M2 標準モード（通常パス・全体の90%以上）

Layer 0 → Layer 1 ＋ layer1-independent-reviewer による独立検証。

- 構成：Layer 0 → Layer 1 ＋ layer1-independent-reviewer（常時必須）
- 検証：L1自己検証（計算的＋推論的）＋ 独立検証（実装コンテキスト隔離）
- 所要トークン：中
- 適用：他人配布・本番運用・業務利用・個人ツール含む大半のケース
- **+25%コストで3〜5倍の損失リスク回避**が合意済みの根拠

### L2 統括指揮発動（稀・全体の<10%）

Layer 0 → **Layer 2統括指揮 → 複数Layer 1並列 → layer2-integration-verifier統合検証**。

- 構成：L0 → L2オーケストレータ → L1群（ドメイン分割・並列実行）＋ 各L1に layer1-independent-reviewer ＋ layer2-integration-verifier ＋ 必要に応じ Playwright Test Agents
- 検証：各L1の独立検証 ＋ 跨ぎドメイン整合性・全体不変条件・E2E検証
- 所要トークン：大
- 適用：L2発動閾値を超えるプロジェクトのみ

**配下Agent構成の決定責務は L0**: どのサブエージェントを起動するか（Playwright Test Agents 起動要否・L1 並列ドメイン数・integration-verifier の検証範囲等）は、L0 が認識擦り合せで決定し REGIME.md / INTEGRATION.md に明示する。L2 は与えられた構成で統括実行に全集中する（構成変更は L0 差し戻し）。原則書は `../../layer2-orchestrator/references/sub-agent-protocol.md` を参照。

---

## L2発動閾値（Claude Opus 4.7 基準）

いずれか1つでも超えたら L2：

| 閾値 | 値 | 系統 |
|---|---|---|
| SPEC.md トークン数 | >15k トークン（≒60ページ） | 規模系 |
| 成果物ファイル数 | >80ファイル | 規模系 |
| 成果物総行数 | >10k行 | 規模系 |
| 独立ドメイン数 | ≥5 | 規模系 |
| 並行可能サブゴール数 | ≥3 | 規模系 |
| L1 1サイクルの想定時間 | >2時間 | 規模系 |
| UI画面数 | ≥10 | 内容系 |
| E2Eシナリオ数 | ≥20 | 内容系 |
| インタラクション深度 | ≥5 段 | 内容系 |
| 層間不変条件数 | ≥15 | 内容系 |

「いずれか1つでも超えたら L2」のロジックは維持。系統（規模系 / 内容系）は分析時の参考情報であり、判定マトリクスにはしない（フラクタル原則：L2 は単一責務）。

**AI能力バージョンを必ず REGIME.md に記録する**。将来モデルの能力向上に伴い閾値は緩和可能。

### 発動判定および配下構成決定は L0 の責務

L2 発動の判定は本表の閾値で L0 が行う。発動後の **L2 配下 Agent 構成**（Playwright Test Agents 起動要否・L1 並列ドメイン数・integration-verifier 検証範囲等）も L0 が認識擦り合せで決定し、REGIME.md / INTEGRATION.md に明示する。L2 自身は構成を判断しない（与えられた構成で実行に全集中）。

---

## 判定ルール

### 一次判定（S+U+R 合計）

| 合計点 | モード |
|---|---|
| 0〜3点 | M1 単体モード |
| 4点〜 | M2 標準モード |

**T1〜T5の細分類は廃止**。合計点では M1/M2 のみ決定し、L2 昇格は閾値で別判定する。

### オーバーライドルール

| 条件 | 上書き結果 |
|---|---|
| L2発動閾値のいずれかを超える | **L2 に昇格** |
| R ≥ 2（他人配布以上） | **M2 以上を強制**（M1は選ばない） |
| U ≥ 3 | **L0 対話ループ延長**（暫定M1でブレスト継続、仕様確定後に再判定） |
| N ≥ 9 | **ARC モノリス解除強制**（arc-patterns/ から人間判断献上） |
| N ≥ 5 | ARC 切替推奨 + 2段階化検討（推奨、強制ではない） |
| セキュリティ（N の S）≥ 2 | **M2 以上を強制**（R ≥ 2 と同一結果、単独発火も可） |
| 可用性（N の A）= 3 | REGIME.md に **権限レベル明示記録を必須化** |

オーバーライドの優先順位（N 軸統合版）：
1. L2発動閾値 → L2 確定
2. U ≥ 3 → L0 対話延長（モード確定を保留）
3. N ≥ 9 → ARC モノリス解除（判定モードは別ルールで決定）
4. N ≥ 5 → ARC 切替推奨（強制ではない）
5. R ≥ 2 → M2 以上を強制
6. N の S ≥ 2 → M2 以上を強制（5 と同一結果に収束）
7. N の A = 3 → 権限レベル記録必須化

ルール 5・6 は同じ結果（M2 強制）に収束するため衝突しない。ルール 3 は ARC を上書きするが M2/L2 判定自体は上書きしない。

**T5は独立モードではない**。L0 対話フェーズの深度延長として扱う（人間⇄AIの認識ズレゼロ化ループ）。

---

## 判定フロー

```
1. 対話から S, U, R, N を算出（N 未収集なら N=0 で開始）
2. L2発動閾値を超える？
   YES → L2 確定（サブドメイン分割設計へ）
   NO  → 3 へ
3. U >= 3 ?
   YES → L0 対話延長。確定保留。仕様が煮詰まったら 1 に戻る
   NO  → 4 へ
4. N >= 9 ?
   YES → ARC モノリス解除。arc-patterns/ から人間選択を献上（判定モードは別ルールで決定）
   NO  → 5 へ
5. N >= 5 ?
   YES → ARC 切替推奨を提示、2段階化検討（強制ではない）
   NO  → 6 へ
6. S + U + R で一次判定（0〜3=M1 / 4〜=M2）
7. R >= 2 または N の S ≥ 2 ?
   YES → M2 に引き上げ
   NO  → 判定確定
8. N の A = 3 ?
   YES → REGIME.md に権限レベル明示記録を必須化
9. REGIME.md に出力（AI能力バージョン / N スコア / ARC / 権限レベルを記録）
```

---

## L2の場合のサブドメイン再分割（フラクタル適用）

L2判定の場合、全体判定と同じS/U/R軸を各サブドメインに再適用する：

- サブドメインごとに S/U/R を算出 → 各サブドメインを M1 / M2 で運用
- サブドメイン間のインターフェース契約を SPEC.md に明記
- 各サブドメインの VERIFICATION.md は layer1-independent-reviewer が生成
- 全サブドメインPASS 後に layer2-integration-verifier が統合検証

これにより「L2配下の各L1は再帰的にM1/M2で回る」形になり、設計の根本構造が規模に依存しない。

---

## 判定結果の記述例

### 例1：Chrome拡張（タブマネージャー）

- 機能数 4〜10 → 2点
- 画面数 2〜5（ポップアップ＋オプション） → 1点
- 登場人物 1種 → 0点
- 外部連携 0 → 0点
- S = 3点
- イメージが鮮明 → 0点
- 類似物使用経験あり → 0点
- 継続更新前提 → 1点
- U = 1点
- 他人に配布する → 2点
- R = 2点
- 合計 6点 → 一次判定 M2
- L2閾値超過なし
- R >= 2 → M2 確定
- **判定：M2 標準モード**

L1（autonomous-dev）＋ layer1-independent-reviewer の構成で運用。
職種軸分業（FE/BE/QA/PM の4人体制）は採用しない。

### 例2：使い捨てのCSV変換スクリプト

- S = 1点, U = 0点, R = 0点
- 合計 1点 → **M1 単体モード**
- L1自己検証のみで献上

### 例3：「なんとなくSaaSが欲しい」

- 機能数 不明（11〜と仮定） → 3点
- 画面数 不明（6〜と仮定） → 2点
- 登場人物 不明（複数種と仮定） → 2点
- 外部連携 不明（複数と仮定） → 2点
- S = 9点（L2閾値の独立ドメイン数 ≥5 にも該当しそう）
- U = 5点
- R = 3点
- U >= 3 → **L0 対話延長**（仕様を練り直してから再判定）
- 暫定 M1 で小さく試作しながら仕様を固めるのも可

仕様が煮詰まった時点で S/U/R を再算出し、L2閾値超過ならL2、それ以外ならM2に落ち着く想定。

---

## 権限レベル判定（`permission-delegation.md` 参照）

REGIME.md に以下を記録する。未記載時のデフォルトは **L0-2**。

- 権限レベル: L0-2（デフォルト） / L0-3（昇格、Layer 0 対話で明示同意が必要）
- L0-4 は**不採用**（自己矛盾のため射程外）
- 可用性 A = 3 の場合は権限レベルの明示記録が**必須**（未記載は REGIME.md 不完全扱い）
- 外部 API 課金上限・介入チャネル（C1/C2/C3）の実装状況も記録する

昇格条件:
- Layer 0 対話で人間が明示同意
- R = 3 のプロジェクトでは L0-3 昇格を原則認めない（本番事故リスク回避）

判断献上（C1）の発動カテゴリは `permission-delegation.md` の 5 カテゴリ（Cat-A スコープ境界 / Cat-B 権限超過 / Cat-C 外部依存 / Cat-D 倫理／コンプライアンス / Cat-E 破壊的変更）に従う。

---

## dev_mode 判定（v5.0.0 追加 / v5.6.0 で `autonomous` 本格化）

GitHub 連携前提の自律駆動を 3 段階で表現する追加軸。規模・チーム軸と並列の動的判定軸として L0 対話で取得する。

### モード境界

| モード | GitHub | Actions | Issue 自動化 | 並列実装 | 自動 merge | 人間関与範囲 |
|---|---|---|---|---|---|---|
| `local_only` | × | × | × | × | × | 全 Layer |
| `github_assisted` | ○ | 任意 | × | 手動 | × | L0 + 承認 |
| `autonomous` | ○ | ○ | ○ | 自動 | ○（scope 依存）| **P1〜P4 のみ**（philosophy.md §7 Person 責務） |

旧名 `github_autonomous` は v5.6.0 で `autonomous` にリネーム（autonomous_scope 軸との整合）。後方互換は §dev_mode 旧名対応 参照。

### 判定プロトコル（2 段階判定）

#### 質問1：GitHub 利用の有無

L0 対話の 2.0〜2.5 ターン目で 1 回だけ質問する：

> 「GitHub を使いますか？（Issue・PR・Actions の運用を含む）」

- **No** → `local_only` 確定（追加質問なし）
- **Yes** → 質問2 へ

#### 質問2：規模 + LC からの推論（ユーザー確認）

判定マトリクス（v5.0.0 時点）：

| 規模 | LC | 推論 dev_mode |
|---|---|---|
| M1 | * | `github_assisted` |
| M2 | LC=0 | `github_assisted` |
| M2 | LC≥1 | `github_assisted`（運用実績で `github_autonomous` 昇格判断） |
| L2 | * | `github_autonomous`（並列実装が前提） |

推論結果を提示してユーザー確認（1 回のみ）：

> 「dev_mode は `[推論結果]` を推奨します。理由：[規模 + LC の根拠]。このまま採用しますか？」

ユーザーが推奨と異なる選択をした場合はそのまま採用し、ADR に根拠を記録する（spec §3.2.3）。

### チーム軸（T1-T5）について

spec §3.1.1 / §3.2.2 では dev_mode 推論にチーム軸（T1: 個人 〜 T5: 大規模分散チーム）を含める設計だが、v5.0.0 時点では既存軸（規模・LC）のみで運用する。チーム軸の operational 化は v5.x の minor 改修で扱う予定（INTENT.md 参照）。

### REGIME.md への記録

REGIME.md の `## dev_mode` セクションに以下を記録：

```markdown
## dev_mode

- mode: github_assisted   # local_only / github_assisted / github_autonomous
- ctl: 0                  # CTL段階（0-3）。crosscut-council/references/ctl-calculation.md 参照
- 判定根拠: GitHub 利用、規模 M2、LC=1
```

### 昇格・降格（手動 + ADR 記録必須）

dev_mode の変更は人間判断による。昇格・降格いずれも `history/ARCH-DECISIONS.md` に記録（変更前後 / 根拠 / 影響範囲）。
自動降格メカニズム（CI 連続失敗 等）は `templates/.github/workflows/auto-degrade.yml` で実装（spec §3.2.10）。

### 「GitHub 無しでも DH ベースは完全動作」の原則

`local_only` を選択しても DH の自律駆動性能は劣化しない。GitHub 連携は段階的拡張オプションであり、必須ではない。

---

## プロトコルの自己評価

判定精度を継続改善するため、献上後のフィードバックで以下を蓄積する。
詳細は Layer 1 の `references/delivery-format.md` 「体制事後評価」セクションを参照。

- 過剰判定：M2選択したがM1で足りた、L2昇格したがM2で足りた、など
- 過少判定：M1選択したがM2が必要だった、M2選択したがL2が必要だった、など
- オーバーライド妥当性：強制ルールが有効に働いたか
- L2発動閾値の妥当性：AI能力向上に伴う閾値緩和の可否
- 権限レベル妥当性：L0-2 で十分だったか、L0-3 への昇格が正解だったか
- C1 判断献上の頻度（多すぎ＝仕様不足、少なすぎ＝スコープ逸脱の見落とし）

蓄積データから判定表の閾値を調整する。

---

## autonomous_scope 判定（v5.6.0 追加、dev_mode = autonomous の場合のみ）

`dev_mode` が `autonomous` に決定したら、autonomous-drive 機構の運用粒度を 3 値で取得する。

### scope 境界

| autonomous_scope | 自動 merge | PR review/approve | P3（事後確認）の位置 | Person 責務範囲 |
|---|---|---|---|---|
| **`full`**（デフォルト） | 有効（`auto-merge` label opt-in + 多層検証通過時） | AI / 独立 critic | merge 後 | P1〜P4 のみ |
| `merge_gated` | 無効（人間 approve 必須） | 人間 | merge 前 | P1〜P4 + PR review |
| `custom` | 部分有効（dev-env-spec.md Level C 詳細指定） | 個別 | 個別 | 個別 |

### 判定プロトコル

dev_mode = `autonomous` 確定後に 1 問のみ：
```
Q: 自律駆動の度合いを選択してください
   (1) フルオート [デフォルト]
   (2) 中度 (merge は人間)
   (3) カスタム
```
→ デフォルト = `full`、ユーザー裁量で `merge_gated` / `custom` に降格可。

### dev_mode 旧名対応（後方互換）

v5.0.0〜v5.5.x で記録された REGIME.md は `dev_mode: github_autonomous` のままで動作する（`autonomous` + `autonomous_scope: full` と等価扱い）。新規プロジェクトでは新名 `autonomous` を使用する。明示的な migration は要求しない（philosophy.md 第 5 条「タイプ二項分類の限界」と同様、運用慣行で吸収）。

### Person 責務範囲との対応

`autonomous_scope: full` を選択した場合の人間関与は philosophy.md 第 7 条 Person 責務 P1〜P4 に集約：
- P1 発案 / P2 ブレスト（Issue 化は AI）/ P3 事後確認・評価 / P4 暴走時介入

`merge_gated` では P3 を merge 前に倒すため、PR review/approve も人間関与に追加。`custom` は dev-env-spec.md Level C で個別指定。

### ADR 記録要請

`autonomous_scope` の昇格・降格（例: `merge_gated` → `full`）は手動 + ADR 記録必須（dev_mode 変更と同形式）。観測駆動: 数 PR の運用観測後に降格 / 昇格を判断（v5.5.3 AD-022 の観測駆動原則を継承）。

---

## current_focus 判定（v5.7.0 追加、autonomous-drive 入口側 Issue pickup で参照）

REGIME.md の `## current_focus` セクションは、autonomous-drive 入口側（Issue → AI pickup）で「pickup すべき Issue か」を判定する基準として使われる。

### フィールド規約

```yaml
## current_focus
- type: bug-fix          # bug-fix / feature / refactor / docs / chore
- target: master         # 対象ブランチ
- since: 2026-05-03      # 開始日
- priority: critical     # critical / standard / low
```

### β 半自動更新（推奨パス）

spec-architect が対話で「今このプロジェクトで何に集中？」を確認し、AI が REGIME.md を更新する。philosophy.md 第 4 条「モード判定は L0」+ 第 7 条 P1/P2「人間 = 頭と口、AI = 手」と整合：

- 例: ユーザー「v5.7.0 のバグを直したい」→ spec-architect が `current_focus.type: bug-fix` と更新
- 例: ユーザー「次は新機能の v5.8.0 に集中したい」→ `current_focus.type: feature` + `since: <today>` 更新
- 更新タイミング: 新規機能着手時、フェーズ切替時、振り返り儀式時

### γ ブランチ命名フォールバック

REGIME.md `current_focus` 未設定時、ブランチ命名から自動推論する（人間に確認しない）：

| ブランチ命名 | 推論 type |
|---|---|
| `fix/*` `bugfix/*` `hotfix/*` | bug-fix |
| `feat/*` `feature/*` | feature |
| `refactor/*` `chore/refactor/*` | refactor |
| `docs/*` | docs |
| `chore/*` | chore |

優先順位: REGIME.md 値 > ブランチ命名推論。両者が衝突する場合は REGIME.md 値を採用。

### Issue pickup 時の照合

`crosscut-issue-implementer` の AI triage 段階で参照（詳細は `crosscut-issue-implementer/references/triage-protocol.md`）：

- Issue label `type:bug` + current_focus.type: `bug-fix` → 整合 → pickup 候補
- Issue label `type:feature` + current_focus.type: `bug-fix` → 不整合 → skip + label `focus-mismatch` 自動付与
- Issue label 未指定 + current_focus.type: `bug-fix` → AI が Issue 本文から推論

### 後方互換性

- 既存 REGIME.md に `current_focus` セクションがない場合 → 全 Issue を pickup 対象として扱う（filter 前提なし）
- 利用者プロジェクトへの遡及適用なし、新規追加のみ
