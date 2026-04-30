# DIMENSIONS

DH の 5 次元論（D1〜D5）の運用ルールを形式化する。各次元の責務・境界・整備プロトコル・council 連携・harness-verifier との責務分離・5 本柱への対応を定める。

INTENT.md が「概念の確立経緯」、harness-verifier/PHILOSOPHY.md が「規律の自己相似性の存在論」を扱うのに対し、本ファイルは **運用ルールの宣言** を担う。

## 1. 5 次元論（D1〜D5）

INTENT.md §v5.2.0 で確立された定義を踏襲する。

| 次元 | 名称 | 実体 |
|---|---|---|
| D1 | ソースコード | プロジェクト実装ファイル群 |
| D2 | 開発環境 | D1 の足場（package.json / vite.config / sensors / SPEC.md 等）= **L0 が存在保証する全ファイル** |
| D3 | 配布 skill | 利用者プロジェクトに配置される `.claude/skills/` インスタンス |
| **D4** | **マスタ skill（メタスキル）** | **dialog-harness リポジトリ内 skill マスタ定義** |
| D5 | Meta モニタリング層 | D4 を外側から監視する **人間**（自動化禁止）|

機械可読命名は D-numbering、思想文書では meta-layer / meta-meta-layer 等の階層形容詞を併走（INTENT.md §v5.2.0）。

### 1.1 操作主体と整備主体

| 操作 | 主体 | 備考 |
|---|---|---|
| 発案・トリガー | **人間専有・不可侵** | council でも代替不能 |
| 判断・合意 | 人間（将来は council で自動化計画） | 第 6 条「人間 ≒ council」の "≒" の運用形態 |
| 実装・編集・検査・記録 | AI | layer1/layer2 の責務範囲 |

| 次元 | 構築 | 整備 |
|---|---|---|
| D1 | L1/L2 自律生成 | L1/L2 自律 |
| D2 | L0 が初期生成 | L1/L2 自律 |
| D3 | L0 が初期配置 | L1/L2 自律 |
| **D4** | **人間専有** | **council + 人間合意（不変領域）**|
| D5 | 人間そのもの | （自動化禁止） |

## 2. 各次元の責務と境界

### 2.1 D1（ソースコード）

プロジェクト実装ファイル群。**主柱: P3 情報純度** — 関数・モジュールが混合責任を持たず、副作用が局在化。副柱: P1 フラクタル / P2 Shift Left。

### 2.2 D2（開発環境）

L0 が存在保証する全ファイルを D2 と定義する（A-1 結論）。範囲:
- scaffold 系: package.json / package-lock.json / tsconfig.json / vite.config.ts / .gitignore
- 仕様系: SPEC.md / DONT.md / REGIME.md / ARCHITECTURE.md / DOMAINS.md
- 検証系: sensors / smoke test 設定 / lint / test 設定
- CI/CD 系: .github/workflows / Dockerfile / docker-compose.yml
- 履歴系: CHANGELOG.md / ARCH-DECISIONS.md / PATTERNS.md / SUMMARY.md

**主柱: P2 Shift Left** — lint / typecheck / smoke test / sensors による早期検出機構の主舞台。副柱: P3 情報純度 / P4 人間責務。

### 2.3 D3（配布 skill）

利用者プロジェクトに配置される `.claude/skills/` インスタンス。**主柱: P1 フラクタル** — 各 skill が単一責務集中、自己相似的に階層を構成。副柱: P3 情報純度 / P5 献上哲学。

### 2.4 D4（マスタ skill）

DH リポジトリ内 `.claude/skills/` の skill マスタ定義。**主柱: P4 人間責務の明確化** — D4 改修は council + 人間承認経由（§4 段階モデル）、不変領域の明示。副柱: P1 フラクタル / P5 献上哲学。

### 2.5 D5（人間）

D4 を外側から監視する人間（自動化禁止）。harness-verifier 出力 + council escalate_to_human + D4 改修判断の最終受け手。**主柱: P5 献上哲学** — 全献上の終点、最外殻。副柱: P4 人間責務 / 第 6 条。

## 3. D3/D4 境界問題と解決（A-2 結論）

### 3.1 構造的不純さの認識

D3 と D4 は物理的に同じ `.claude/skills/` ディレクトリに同居する。原因は Claude skill 仕様が `.claude/skills/` 以外を skill として認識しないこと。

- D3 = 利用者プロジェクト側の `.claude/skills/`
- D4 = DH リポジトリ側の `.claude/skills/`

同じディレクトリ構造でも **配置場所で次元が変わる**。これは構造的必然であり、不純さを隠蔽せず明示する。

### 3.2 解決: frontmatter `dimension` + 思想ドキュメント明示（案 5）

Council 判定 `council-2026-04-29T22:30:00Z-d3d4b1`（agreed_recommended、judgment_confidence 0.85）により以下を採用。

**機械可読の論理識別**:
- SKILL.md frontmatter に `dimension: D3 / D4` フィールドを追加
- harness-verifier が dimension 整合性を検査（§5 拡張責務）

**思想ドキュメントによる正当化**:
- 物理同居は構造的必然（Claude skill 仕様の制約）として明示
- frontmatter は **論理層への事実記述** であり、物理層の修正ではない（哲学者 minority 統合）
- 5 次元論の本質は **論理的階層性** であって物理的純粋性ではない（Russell タイプ理論との同型は自己言及パラドックス回避であり物理分離ではない）

## 4. D4 不変原則と運用ルール（B 結論）

### 4.1 段階モデル

D4 改修を 3 段階に分け、各段階で承認経路を変える（既存セマンティックバージョニングと整合）。

| 段階 | 内容 | 承認経路 | バージョン昇格 |
|---|---|---|---|
| **patch** | typo / コメント / 死リンク修正 / 表記揺れ統一 | 実装者裁量 + harness-verifier PASS | パッチ番号 |
| **minor** | 機能追加 / 検証項目拡張 / 新規 skill 追加 / マーカー設置 / council-weights.md 更新 | council 諮問 + 人間承認（agreed_recommended）| minor 番号 |
| **major** | 5 次元論などの思想変更 / 後方互換破壊 / philosophy.md 章追加 / D5 と D4 の責務再定義 | council 諮問 + 人間承認 + 振り返り儀式（F3 四半期）での総括 | major 番号 |

### 4.2 段階判定ルール

- 判定不能時は **上位段階（minor）にフォールバック**
- council-weights.md の編集は L0 対話のみ（既存規約、minor 段階の前例）
- philosophy.md 章追加は major 必須（v6.0.0 第 7 条候補もこのカテゴリ）

## 5. D2/D3 整備プロトコル（C 結論）

### 5.1 自律 default + 例外時 council

D2/D3 整備は **自律駆動の通常運用** であり、止めないことが原則。default は L1/L2 自律、既存 council 発動基準（複数案 viable / 不可逆操作 / SPEC・DONT 矛盾 / confidence < 0.6）でのみ council 発火。

| 整備類型 | 例 | 経路 |
|---|---|---|
| default 自律整備 | 仕様明確な機能追加 / バグ修正 / リファクタ / 配布 skill instance のカスタマイズ | L1/L2 自律 |
| council 例外発動 | 複数実装案が拮抗 / SPEC.md 改修を伴う / 不可逆操作（DB マイグレーション等）/ AI confidence < 0.6 | council 諮問 → 人間承認 |
| L0 差し戻し | SPEC.md 自体の変更が必要な機能追加 / 仕様の根本不整合 | layer1-autonomous-dev → layer0-spec-architect 献上 |

### 5.2 council 連携ループ — 自律駆動を止めない

```
L1/L2 自律駆動
  │
  ├─[例外条件検出]
  │
  ↓
council 起動
  │
  ↓
council judgment + consensus_mode 自動判定
  │
  ├─ consensus_mode = auto_agree
  │   （judgment_confidence ≥ 0.5、可逆操作、SPEC 軽微差異）
  │     ↓
  │   judgment 結果を L1/L2 への指示として注入
  │     ↓
  │   ★ L1/L2 自律駆動継続（停止しない）★
  │
  └─ consensus_mode = escalate_to_human
      （judgment_confidence < 0.5、不可逆操作、SPEC 破壊的矛盾）
        ↓
      L1/L2 一時停止 → 人間献上 → 人間判断後に再開 or 中止
```

**核心原則**:
- auto_agree = 自律駆動を止めない（D2/D3 整備の通常運用、これが支配的）
- escalate_to_human = 自律駆動が止まる（例外的な献上、レアケース）
- yes/no の中間は禁止（philosophy 違反）

### 5.3 既存機構との接続

| 必要要件 | 既存機構 | 状態 |
|---|---|---|
| consensus_mode 自動判定 | `compute_consensus_mode`（consensus-protocol.md v4.2）| ✅ 既存 |
| council 出力に consensus_mode | `output-format.md` v4.2 | ✅ 既存 |
| L1/L2 が council 出力を内部 task に変換 | layer1-autonomous-dev/SKILL.md の council 連携フロー | ⚠️ v5.3.0 で精緻化 |
| 「auto_agree 受信時に止まらない」明文化 | 未明文化 | ⚠️ v5.3.0 で spec 化 |

## 6. 横断機構の責務分離（D 結論: 時系列順序モデル）

### 6.1 責務マトリクス

| 機構 | 主責務 | 拡張責務（v5.3.0+） | タイミング |
|---|---|---|---|
| **harness-verifier** | D4 内部整合性（5 検査）| **+council 自己検査**（council-weights.md / judgment-agent.md スキーマ）| 月次 cron + push/PR + D4 改修時 |
| **council** | D4 以下動的判断 | （変更なし）| L1/L2 自律駆動中、例外条件で発火 |
| **crosscut-verifier-drift** | SPEC/ADR ⇔ 実装 drift（Type 1）| **+Type 2 drift**（D3 instance ⇔ DH D4）| L1 検証段、PR 作成時 |
| **crosscut-feedback-loop** | drift → 設計層・実装層・L0 還流 | （変更なし）| crosscut-verifier-drift 検出後 |

### 6.2 時系列順序モデル

```
[council 判定]   →   [実装]   →   [harness-verifier 検査]
   動的・LLM           AI           静的・決定論
```

両者は順序関係で機能分離し、責務重複なし。harness-verifier は council 自身も検査することで council を D4 の一部として閉じ込め、D5 が両機構の最外殻として機能する。

### 6.3 失敗経路の集約

```
[harness-verifier FAIL] ──┐
                          ├──→ D5（人間献上、最外殻）
[council escalate_to_human]──┘
```

両者は失敗経路で同じ D5 に集約。発火条件が異なる:
- harness-verifier: 静的整合性違反（mechanical）
- council: 動的判断不能（confidence < 0.5 / 不可逆）

### 6.4 harness-verifier の位置付け

harness-verifier は **D4 派生機構**:
- 物理配置はリポジトリルート直下（D4 と並列、独立性要請）
- 論理的責務は D4 内部整合性検査（D4 仕様から派生）
- D5 ではない（D5 = 人間のみ）
- D4 の "下から支える" のではなく "外から検査する"

これは harness-verifier/PHILOSOPHY.md §3-4 の「Russell タイプ理論との同型」と整合する。

## 7. Council Hook 機構

### 7.1 マーカー（案 α: HTML コメント形式）

SKILL.md / references / SPEC.md の手順記述内に置かれる宣言的テキスト。「この手続き実行がここに到達したら council 発動を検討せよ」を AI 実装者に示す。

```html
<!-- council-hook:
     question="..."          # question_to_answer の hint（AI が文脈で具体化）
     category="..."          # implementation/operation/maintenance/judgment 等
     condition="..."         # 発動条件のテキスト記述（≥2 案 viable / 不可逆操作直前 等）
     escalation="auto"       # auto / discretion（実装者裁量）/ mandatory（必須）
-->
```

DH 既存マーカー前例（rtk-integration の `<!-- rtk-integration: begin -->` / harness-credit の `<!-- harness-credit: managed by layer0 skills. do not edit manually. -->`）と整合。

### 7.2 マーカーと動的判定の区別

- マーカーあり地点 → AI は **必ず confidence 自問する**（自問は強制、council 発動は AI 判断）
- マーカーなし地点 → AI の自律判断のみ
- マーカー漏れは F1 振り返り儀式で検出（マーカーなしで人間献上 / failed が発生したログから逆算）

### 7.3 役割マトリクス

| 利用者 | 役割 |
|---|---|
| AI 実装者（layer1-autonomous-dev 等）| 手順なぞり中にマーカー検出 → confidence 自問 → 低ければ council 発動 |
| harness-verifier | マーカー設置の網羅性検査（dimension と併用、D4 整合性） |
| 人間レビュアー | skill の判断分岐構造を可視化、設計時のレビュー対象 |
| F1-F3 振り返り儀式 | マーカー位置と実発火の整合性監査 |

### 7.4 漸進ロードマップ（A-3 Q1 結論: 案 B）

3 アプローチを段階的に導入し、各段階の運用データを次段の設計根拠とする。

| バージョン | 導入アプローチ | 次段移行 signal |
|---|---|---|
| **v5.3.0** | アプローチ 1: マーカー機構（案 α HTML コメント）| マーカー漏れ事例月 1 件以上 → v5.4.0 へ |
| **v5.4.0** | アプローチ 3: 次元境界跨ぎ検知（frontmatter `dimension: D4` 編集試行）| マーカー乱発で誤発火率 > 30% → v5.5.0 へ |
| **v5.5.0** | アプローチ 2: S/U/R 三軸スコア発火 | 完成（v5.5.0 で全機構稼働）|

各段階で signal 条件と learning structure を v5.3.0 PR で明文化（council `hk1stg` の minority 統合）。

### 7.5 閾値設定主体（A-3 Q2 結論: 案 C hybrid）

v5.5.0 で導入する S/U/R 三軸スコアの閾値は **hybrid モデル**:

```
1. L0 対話で初期値を確定（council-weights.md 等に固定値）
   ↓
2. 運用 1-3 ヶ月後の振り返り儀式 F2/F3 で運用データを基に
   council が再校正案を提示
   ↓
3. 人間承認で更新（auto_agree ではなく、儀式での明示承認）
   ↓
4. 古い閾値は decay で重みを下げる（initial / decay_rate / cutoff の 3 値固定）
```

**第 6 条「人間 ≒ council」の "≒" の核心実装**:
- 提案 = council（実証ベース、運用データ駆動）
- 承認 = 人間（不可侵、儀式で明示）
- 能力ベースで対等、権限の種類で切り分け

decay パラメータ自体のメタ閾値問題は Russell タイプ理論の有限段打ち切りと同型 — L0 対話のスコープ限定で対処。

## 8. 5 次元論と 5 本柱の対応（F 結論）

### 8.1 主柱 + 副柱マトリクス

5 次元（D1-D5）と 5 本柱（P1-P5）は **直交軸** の関係。次元は対象、本柱は適用される原則。各次元には強く効く主柱が 1 つあり、副次的に他柱も影響する。

| 次元 | 主柱 | 主柱の現れ方 | 副柱（順位順） |
|---|---|---|---|
| **D1（ソースコード）**| **P3 情報純度** | 関数・モジュールが混合責任を持たず、副作用が局在化 | P1 フラクタル / P2 Shift Left |
| **D2（開発環境）**| **P2 Shift Left** | lint / typecheck / smoke test / sensors による早期検出機構の主舞台 | P3 情報純度 / P4 人間責務 |
| **D3（配布 skill）**| **P1 フラクタル** | 各 skill が単一責務集中、自己相似的に階層を構成 | P3 情報純度 / P5 献上哲学 |
| **D4（マスタ skill）**| **P4 人間責務の明確化** | D4 改修は council + 人間承認経由（§4 段階モデル）、不変領域の明示 | P1 フラクタル / P5 献上哲学 |
| **D5（人間）**| **P5 献上哲学** | 全 escalate / harness-verifier FAIL / D4 改修判断の最終受け手、最外殻として「献上の終点」 | P4 人間責務 / 第 6 条 |

### 8.2 第 6 条「人間 ≒ council」の位置付け

第 6 条は次元の対応表の項目ではなく、**次元間の関係性原則**。具体的には D5（人間）と council（D4 以下の動的判断機構）の関係性を定義する meta 原則。

A-3 Q2（hybrid 閾値）の確定はこの "≒" の核心実装と位置付けられる。

### 8.3 第 7 条候補（v6.0.0）

「次元論と D4 の独立性」を philosophy.md 第 7 条として組み込む候補（INTENT.md / harness-verifier/PHILOSOPHY.md §6 で予告済）。これは 5 次元論自体を philosophy に組み込む meta 原則であり、第 6 条と同じく「次元間関係性原則」のカテゴリ。

v5.2.0 では本ファイル DIMENSIONS.md と harness-verifier/PHILOSOPHY.md に閉じ、v6.0.0 で major 昇格時に philosophy.md 本体へ昇格させる。

## 9. Council 判定履歴

本ファイルの内容を確定した council 判定:

| invocation_id | 論点 | 結論 | confidence |
|---|---|---|---|
| `council-2026-04-29T22:30:00Z-d3d4b1` | A-2: D3/D4 境界 | 案 5: frontmatter `dimension` + 思想ドキュメント明示 | 0.85 |
| `council-2026-04-30T04:25:00Z-hk1stg` | A-3 Q1: Hook 統合方針 | 案 B: 漸進的（v5.3.0 → v5.4.0 → v5.5.0）+ signal 条件明文化 | 0.85 |
| `council-2026-04-30T04:35:00Z-thrsh2` | A-3 Q2: 閾値設定主体 | 案 C: hybrid（事前定義 + 儀式承認校正 + decay）| 0.88 |

3 件全て agreed_recommended（auto_agree）で確定。COUNCIL-LOG への永続化は v5.3.0 実装 PR で実施。

## 10. 既存ドキュメントとの整合性

### 10.1 重複なく補完する関係

| ドキュメント | 役割 | 本ファイルとの関係 |
|---|---|---|
| `history/INTENT.md` | 概念の確立経緯（v5.2.0 §で 5 次元論を導入） | 経緯 → 運用ルールへ展開（本ファイルが運用層） |
| `harness-verifier/PHILOSOPHY.md` | 規律の自己相似性、singularity の存在論 | harness-verifier 視点 → 全機構視点（本ファイルが横断視点） |
| `.claude/skills/layer0-spec-architect/references/philosophy.md` | DH 6 条憲法（5 本柱 + 第 6 条）| §8 主柱マトリクスで参照 |
| `harness-verifier/BOUNDARY.md` | DH 本体と本機構の境界線 | §6 責務マトリクスで参照 |

本ファイルの D1-D5 定義は INTENT.md §v5.2.0 を踏襲、5 本柱定義は philosophy.md §第 1-5 条を踏襲、harness-verifier 位置付けは PHILOSOPHY.md §3-4 と整合。

### 10.2 修正対象として記録

- **HANDOFF §1.1（外部ドキュメント）**: 「D5 = 人間 + harness-verifier」表記は本ファイル §2.5（D5 = 人間のみ）に整合させて訂正対象。harness-verifier は §6.4 のとおり D4 派生機構として独立位置付け。

## 11. 残タスク（v5.3.0 以降）

| タスク | 起票元 | 対応バージョン |
|---|---|---|
| Council Hook マーカー（案 α）の v5.3.0 実装 | §7.1 / §7.4 | v5.3.0 |
| L1/L2 SKILL.md への council 連携フロー精緻化 | §5.3 | v5.3.0 |
| 「auto_agree 受信時に止まらない」spec 化 | §5.3 | v5.3.0 |
| harness-verifier に council 自己検査拡張（council-weights.md / judgment-agent.md スキーマ）| §6.1 | v5.3.0/v5.4.0 |
| 次元境界跨ぎ検知（frontmatter `dimension: D4` 編集試行）の harness-verifier 実装 | §7.4 | v5.4.0 |
| crosscut-verifier-drift に Type 2 drift（D3 ⇔ D4）拡張 | §6.1 | v5.4.0 候補 |
| S/U/R 三軸スコア + hybrid 閾値の実装 | §7.5 | v5.5.0 |
| philosophy.md 第 7 条「次元論と D4 の独立性」追加 | §8.3 | v6.0.0 |
| council-weights.md `situational_modifier.conception` 合計 +1 違反 | §10.2 補足 | F2 振り返り儀式（任意、棚卸し対象から除外可）|
| マーカー設置の決定権限 | §7（B 案 minor 段階で吸収済）| v5.3.0 PR で運用ルール明文化 |

## バージョン

v0.1.0（dialog-harness v5.2.0 で導入、DIMENSIONS.md 初版）
