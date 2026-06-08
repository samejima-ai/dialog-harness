# E2E統合規格 — Playwright Test Agents

L2 配下で並列起動される E2E 検証用 Agent 群の規格。
哲学的背景は `../../layer0-spec-architect/references/philosophy.md` §2（Shift Left）および §3（情報純度）を参照。

---

## 位置づけ

### 5層エラー検出スタックでの位置

本規格は **5層エラー検出スタックの第2層（E2E機械検証）** の L2 発動時における実装。
Shift Left 基盤 + 5層エラー検出スタック全体の定義は `../../layer1-autonomous-dev/references/inferential-sensor-v2.md` を参照。

### L2 配下での起動

L2 発動時（REGIME.md モード = L2）で、L0 が REGIME.md / INTEGRATION.md に Playwright Test Agents の起動を指定した場合に、layer2-orchestrator が配下の並列 Agent として起動する。

**配下構成の決定責務**: どの Agent を起動するかは **L0 の判断**（認識擦り合せで決定し REGIME.md に記載）。L2 自身は起動指定を受け取って実行する受け手。

### M1/M2 での扱い

M1/M2 では本規格の Agent 群は起動しない。L1 が単独で Playwright テストを書き、L1 自身が実行する（`sensors/e2e/` を参照）。

---

## Agent 群定義

L2 配下で並列起動される4種の Agent。各 Agent は情報純度原則（philosophy.md §3）の4基準を満たす。

### Planner Agent

**責務**: SPEC.md / DONT.md / sensors/e2e/ を読み、E2E シナリオ一覧を設計する。

- 入力: SPEC.md, DONT.md, sensors/e2e/ 既存定義, INTEGRATION.md（L0 指定）
- 出力: `delivery/e2e/plan.md` — シナリオ一覧（ID / 前提 / 操作 / 期待結果）
- 独立コンテキスト性: 実装コードに触れない。純粋に仕様からシナリオを設計する

### Generator Agent

**責務**: Planner が設計したシナリオを Playwright テストコードに変換する。

- 入力: `delivery/e2e/plan.md`, 対象アプリの URL / 起動手順, sensors/e2e/ 規格
- 出力: `tests/e2e/*.spec.ts`（Playwright テストファイル）
- 独立コンテキスト性: 仕様の再解釈をしない（Planner の出力を忠実に実装する）

### Healer Agent

**責務**: Generator が生成したテストが失敗した場合の原因特定・修復案提示。

- 入力: Playwright 実行結果（失敗スクリーンショット・スタックトレース・Console ログ）, `tests/e2e/*.spec.ts`, 実装コード
- 出力: `delivery/e2e/healing-report.md` — 失敗原因の分類（テストバグ / 実装バグ / 仕様曖昧）と修復案
- 独立コンテキスト性: 実装 Agent に同化しない。実装バグと判定したら L1 差戻しを提案する

### Reviewer Agent

**責務**: E2E 実行結果全体を独立レビューし、通過判定する。

- 入力: 全 Agent の出力, 実行ログ, スクリーンショット一式
- 出力: `delivery/e2e/review.md` — 総合判定（PASS / FAIL）と根拠
- 独立コンテキスト性: 他3 Agent の主観を排除し、結果のみで判定する

---

## 起動フロー

```
L2 統括者 (layer2-orchestrator)
  │ REGIME.md / INTEGRATION.md で E2E Agent 起動を指定されている
  │
  ├─ Playwright Test Agents 並列起動
  │   ├─ Planner Agent         → delivery/e2e/plan.md
  │   ├─ Generator Agent       → tests/e2e/*.spec.ts
  │   ├─ Healer Agent (on-fail) → delivery/e2e/healing-report.md
  │   └─ Reviewer Agent        → delivery/e2e/review.md
  │
  └─ layer2-integration-verifier が review.md を含めて最終統合検証
```

### 並列性

Planner → Generator は順次（Generator が plan.md を必要とする）。
Healer は失敗時のみ起動。Reviewer は全完了後に起動。

### L2 統括者の役割

L2 は**起動の指揮のみ**を担う。Agent 内部の判断や修正は各 Agent の責務範囲内。L2 が Agent の出力を再解釈することはしない（情報純度を保つため）。

---

## 第2層センサーとしての位置づけ

### 前提条件

Shift Left 基盤（設計時発生防止）が完遂している前提で、第1層（計算的センサー）の完遂後に発動する。Console エラーを残したまま E2E を回さない原則（Shift Left 基盤 + 5層エラー検出スタック定義を参照）。

### 後続層への接続

本規格の Agent 群が PASS したら、第3層（Interaction Cost 測定）と第4層（推論的センサー）に進む。Reviewer Agent の PASS は後続の前提条件となる。

---

## sensors/e2e/ 規格

L0 が `sensors/e2e/` 配下に定義する規格。Planner / Generator の入力となる。

### ディレクトリ構成

```
sensors/e2e/
├── scenarios.md      # シナリオ定義（ID / 前提 / 操作 / 期待結果）
├── selectors.md      # DOM セレクタの命名規約（data-testid 等）
├── fixtures/         # テストデータ・モック定義
└── config.ts         # Playwright 設定（baseURL / timeout / projects）
```

### config.ts 規格 — browser provenance pinning（v5.23.0）

「どの browser が開くか」のばらつき（CC コンテナの同梱 chromium vs ローカル実 Chrome vs CI）は
**AI の知覚器官そのもののばらつき**であり flaky 源・観測性統一の侵食になる。**「借りない・固定する・
記録する」** を config.ts で担保する。構築規律の正本は
`../../layer1-autonomous-dev/references/e2e-best-practices.md` §7（本節はその config 具体化）。

- **借りない**: `channel:'chrome'`（system Chrome）を使わず Playwright 同梱の pinned chromium を使う
- **固定する**: Playwright バージョンを lockfile で固定し、公式コンテナ
  `mcr.microsoft.com/playwright:vX.Y.Z`（バージョン一致）で実行（フォント/レンダリングまで同一＝
  Vision 第5層判定の地盤）。headless 既定、headed は人間デバッグのみ
- **カノニカルエンジン = 同梱 chromium 単一**（既定）。webkit/firefox は SPEC が「クロスブラウザ critical」と
  宣言した時のみ `projects` マトリクス拡張で opt-in（多エンジン既定は実行/保守/flaky コスト 3 倍化）
- **複数デバイス = config 化**: `projects` に device descriptors（viewport/deviceScaleFactor/userAgent/mobile）の
  マトリクスとして宣言。対象端末は DESIGN.md レスポンシブ断面 / SPEC から導出
- **記録する**: 各 run で browser version + engine + container digest を trace/report に刻む（provenance）

Generator / Healer Agent はこの config 規律と e2e-best-practices.md §3（相 A 構築規律）に従って
テストを生成・修復する。

### 代謝サイクルへの記録（v5.24.0）

run 後、各 run は **相 A artifact を COLD（`history/archive/YYYY-MM/e2e/`）直行**で保存し、
**run 要約（provenance + pass/fail/flaky/duration + artifact への cold:// ポインタ）を
`history/E2E-LOG.md` に append** する。これが E2E 情報代謝サイクル（`../../layer1-autonomous-dev/references/e2e-best-practices.md` §9）の
①記録フェーズ。E2E-LOG は WARM として reindex が増分摂取し、flaky 反復を罠に結晶化する。
artifact 本体は既定ロードしない（購読量保護）。**project 還元（D1-D3）専用**で、DH 本体では稼働しない。

### scenarios.md テンプレート

```markdown
# E2E シナリオ

## S1: [シナリオ名]
- 前提: [初期状態・認証状態]
- 操作:
  1. [ユーザー操作1]
  2. [ユーザー操作2]
- 期待結果:
  - [DOM 状態 / URL / Console 状態]
  - [ネットワーク応答]
- 優先度: critical / standard / cosmetic
```

### 優先度と実行範囲

SPEC.md の Priority と対応する（`../../layer0-spec-architect/assets/meta-spec-template.md` の Priority 定義参照）。Priority は検出スタック（建物）の使用階数を決める。Shift Left 基盤（土地）は Priority に関わらず常に整備される前提で、階数に加算しない。

- critical: 第1〜5層すべてを使用（本 E2E 含む）
- standard: 第1〜3層まで使用（本 E2E 含む）
- cosmetic: 第1層のみ使用（本 E2E はスキップ）

---

## sensors/interaction-cost/ 規格

L0 が `sensors/interaction-cost/` 配下に定義する Interaction Cost（第3層）閾値。

### ディレクトリ構成

```
sensors/interaction-cost/
├── thresholds.md     # UX 3問プロトコル Q1 の Must 閾値
└── measurements.ts   # 測定スクリプト（Playwright から呼び出し）
```

### thresholds.md テンプレート

```markdown
# Interaction Cost 閾値

## UX 3問プロトコル Q1 回答由来

- クリック数: [X 回以内]
- 遷移深度: [Y ページ以内]
- 応答時間 p95: [Z 秒以内]
- 完了率: [P % 以上]
- エラー率: [Q % 以下]

## 業界標準値（未指定時のデフォルト）

- クリック数: 3-5 回以内
- 遷移深度: 3 ページ以内
- 応答時間 p95: 30 秒以内
- 完了率: 95% 以上
- エラー率: 5% 以下
```

### 測定と判定

Playwright テスト内で measurements.ts の関数を呼び、thresholds.md との突合結果を `delivery/e2e/interaction-cost.md` に出力。閾値未達成は**第3層 Interaction Cost FAIL として独立カウント**し、その時点で全体としても FAIL とする（上位層の判定に混ぜない）。

---

## Agent 間通信

### 契約の明示

各 Agent は**ドキュメント化された契約**でのみ通信する（philosophy.md §3）。自然言語通信は情報損失前提。

| 通信 | 契約ドキュメント |
|---|---|
| Planner → Generator | delivery/e2e/plan.md |
| Generator → Healer | tests/e2e/*.spec.ts + Playwright実行結果 |
| Healer → L1 差戻し | delivery/e2e/healing-report.md |
| 全 Agent → Reviewer | 各自の出力ファイル |
| Reviewer → L2 統括者 | delivery/e2e/review.md |

### 再解釈の禁止

各 Agent は**前の Agent の出力を再解釈しない**。不明点があれば L2 統括者経由で L0 に差し戻す（REGIME.md / INTEGRATION.md の更新要求）。

---

## integration-verifier との連携

本規格の Reviewer Agent が PASS したら、layer2-integration-verifier が全ドメインの統合検証を行う。Reviewer の review.md は integration-verifier への入力の一つ。

詳細は `../../layer2-integration-verifier/SKILL.md` を参照。

---

## 実装ステータス

現時点では規格定義。実装は L2 発動プロジェクトが実際に現れた時点で行う。L2 発動は稀（全体の <10%）であり、Claude Opus 4.7 の能力では M2 で吸収可能なケースが多い。

規格を先行して置くことでフラクタル骨格の完全性を担保する。
