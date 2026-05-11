# SELF-VERIFICATION v5.6.0

L0 spec-architect §7.4 自己検証 + harness-verifier 5 検査 + philosophy 第 7 条整合性確認。

## §7.4 自己検証チェックリスト

| # | 項目 | 結果 | 補足 |
|---|---|---|---|
| 1 | broken reference 検査 | ✅ PASS | harness-verifier §2 で 0 件検出 |
| 2 | scaffold smoke test | N/A | DH 自身は scaffold 対象外（メタスキル開発） |
| 3 | DONT 自己照合 | ✅ PASS | DH に DONT.md なし、philosophy.md 6 + 1 条との整合性は本ファイル §第 7 条整合性 で確認 |
| 4 | Pre-flight 充足 | ✅ PASS | 本セッションで ritual-protocol.md / philosophy.md / spec-architect SKILL.md / regime-assessment.md / dev-env-spec.md 等を読込済 |
| 5 | 受け入れ基準充足 | ✅ PASS | LC=2 既存プロジェクトの新規追加機能に段階適用、本要請は v5.6.0 新規追加部分にのみ適用 |

## harness-verifier 5 検査結果

| # | 検査項目 | 結果 | 検出件数 |
|---|---|---|---|
| 1 | frontmatter 整合性 | ✅ PASS | 0 |
| 2 | 参照 path 有効性 | ✅ PASS | 0 |
| 3 | SK 間参照の健全性 | ✅ PASS | 0 |
| 4 | 5 層構造保全 | ✅ PASS | 0 |
| 5 | 用語辞書整合 | ✅ PASS | 0（新 skill `crosscut-autonomous-drive` を glossary.yml に登録済） |

## philosophy.md 第 7 条と既存 6 条の整合性確認

### 既存 6 条との整合チェック

| 既存条 | 第 7 条との整合性 |
|---|---|
| 第 1 条 フラクタル原則 | ✅ 整合: 「L3 を新設しない」と整合、第 7 条は L0/L1/L2/Council 4 役割 + サポートを明示するが新層追加ではない |
| 第 2 条 Shift Left 原則 | ✅ 整合: 第 7 条のサポート skill は計算的解決の補助層として機能 |
| 第 3 条 情報純度原則 | ✅ 整合: 第 7 条のサポート skill 定義「単独で完結せず必ず 4 役割から呼ばれる」は情報純度の系（明示的な献上関係） |
| 第 4 条 人間責務の明確化 | ✅ 整合: 第 7 条 P1〜P4 は第 4 条「人間の責務」を行為レベルで具体化、矛盾なし |
| 第 5 条 献上哲学 | ✅ 整合: 第 7 条のサポート skill が献上を発生させる場合の献上先（4 役割のいずれか）を明示 |
| 第 6 条 人間 ≒ Council 原則 | ✅ 整合: 第 7 条 P カテゴリは第 6 条 H カテゴリと **直交 2 軸** として整理（H = 判断種別、P = 責務種別）、両カテゴリのラベル番号符合は偶然的 |

### 第 7 条 内部整合性

- 4 役割属性（L0/L1/L2/Council）と既存 skill 配置が一致：
  - L0: layer0-spec-architect / layer0-onboarding / layer0-archeo-architect ✅
  - L1: layer1-autonomous-dev / layer1-independent-reviewer ✅
  - L2: layer2-orchestrator / layer2-integration-verifier ✅
  - Council: crosscut-council ✅
- サポート skill: crosscut-* 非 council 系（5 既存 + autonomous-drive 新設 = 6）+ sub-agent ✅
- L3 運用層を新設しない原則と整合 ✅
- Person 責務 P1〜P4 が第 6 条 H カテゴリと番号衝突する問題は実装者裁量で解消（HANDOFF の H1-H4 → P1-P4 リネーム、Council 起動の閾値未満の判断）

## 4 役割組織論と既存 skill 配置の整合性

`harness-verifier/glossary.yml` の `members` リストと第 7 条 4 役割属性の対応：

```
crosscut prefix members:
  - crosscut-council                  → Council 判断（4 役割の 1 つ）
  - crosscut-issue-dispatcher         → サポート（L0/L1 補助）
  - crosscut-issue-implementer        → サポート（L1 補助、Issue 起点で起動）
  - crosscut-verifier-drift           → サポート（L1 自己検証層補完）
  - crosscut-verifier-philosophy      → サポート（5 + 1 本柱整合検証、v5.0.0 から後送中）
  - crosscut-feedback-loop            → サポート（検証層 → 設計/実装/L0 還流）
  - crosscut-autonomous-drive (NEW)   → サポート（autonomous-drive deployment）

layer prefix members:
  - layer0-* (3 skill)                → L0 設計
  - layer1-* (2 skill)                → L1 実装
  - layer2-* (2 skill)                → L2 統括
```

第 7 条で定義した「4 役割属性 + サポート構造」と、既存 skill 配置 + 新 skill `crosscut-autonomous-drive` の追加は完全整合。

## v5.5.3 → v5.6.0 の同梱 housekeeping

- v5.5.3 (in progress, target 2026-05-03) → (released 2026-05-03) 化を CHANGELOG.md で実施
- 5 例目正規適用（v5.5.0 で確立、v5.5.1/v5.5.3 → v5.6.0 で 4 例目 / 本 v5.6.0 自身で 5 例目）
- housekeeping を独立 PR にせず本 PR に同梱（PR 数削減）

## 配置成果物

### Phase A
- `philosophy.md` 第 7 条新設（既存 6 条不変、+95 line）
- `history/CHANGELOG.md` v5.6.0 (in progress) + v5.5.3 (released) 化
- `history/INTENT.md` v5.6.0 設計意図セクション追加
- `history/REGIME-LOG.md` v5.6.0 minor 昇格判定追加
- `history/ARCH-DECISIONS.md` AD-023/024/025 追加
- `history/COUNCIL-LOG.md` adrv02 エントリ append

### Phase B
- `layer0-spec-architect/SKILL.md` dev_mode autonomous + autonomous_scope + Level C 追記
- `layer0-spec-architect/references/dialog-questions.md` autonomous_scope 質問追加
- `layer0-spec-architect/references/regime-assessment.md` autonomous_scope 判定 + dev_mode 旧名対応 追加
- `layer0-spec-architect/references/dev-env-spec.md` Level C 新設
- `layer0-spec-architect/assets/meta-spec-template.md` autonomous_scope セクション追加

### Phase C
- `templates/github-workflows/auto-merge.yml.template` 新設（dialog-harness の auto-merge.yml から汎化、ALLOWED_AUTHORS placeholder 化）
- `templates/github-workflows/gemini-review.yml.template` 新設（同上、placeholder なし版）
- `.claude/skills/crosscut-autonomous-drive/SKILL.md` 新設
- `.claude/skills/crosscut-autonomous-drive/references/placeholder-spec.md` 新設
- `.claude/skills/crosscut-autonomous-drive/references/setup-checklist.md` 新設
- `.claude/skills/layer0-spec-architect/references/autonomous-drive-deployment.md` 新設
- `harness-verifier/glossary.yml` crosscut prefix members に `crosscut-autonomous-drive` 追加

### Phase D
- 本ファイル `delivery/SELF-VERIFICATION-v5.6.0.md`

## 既知の温存項目（v5.6.x patch 候補）

- destructive change detector / circuit breaker（Council `adrv02` β 止揚で温存確定）
- ALLOWED_AUTHORS 動的化（複数 contributor 体制で必要時）
- adrv01-Ph2（独立観測機構）— 第 7 条で組織論確定、連動して本実装可能
- crosscut-verifier-philosophy 本実装（v5.0.0 から累計後送中、第 7 条で 7 本柱整合検証として再構成可能）

## 結論

✅ **v5.6.0 implementation 完了、harness-verifier 全 PASS、philosophy 整合性 PASS**。
本 PR を `auto-merge` label 付与で autonomous-drive 機構経由の自動 merge へ投入する。

体制事後評価: M2 (LC=2) は妥当。L2 発動閾値（NFR 3 項目同時 critical）には到達せず。philosophy.md 第 7 条新設で 4 役割組織論が明文化されたため、次サイクル以降は新規プロジェクト立ち上げで dev_mode `autonomous` + `autonomous_scope: full` のフル autonomous-drive 運用が可能となる。
