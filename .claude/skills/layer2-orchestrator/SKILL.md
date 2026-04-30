---
name: layer2-orchestrator
dimension: D4
description: >
  L2発動時のみトリガーされる統括指揮スキル（雛形）。
  **REGIME.md で L2 と判定されたプロジェクトでのみ起動する**（spec-architect の判定を経由必須）。
  「大規模プロジェクトを統括して」「複数ドメインをまとめて」等の発話だけでは独立起動せず、
  まず spec-architect を経由して REGIME.md の L2 確定を待つ。
  複数L1エージェントのサブドメイン分割・並列実行調整・統合検証の手配を行う。
  M1/M2 では絶対に起動しない（コンテキストの過剰消費を避けるため）。
  ※ 現時点は雛形。Claude Opus 4.7 の能力では M2 で吸収可能なケースが多いため、
  疑わしい場合は起動を保留し spec-architect に M2 判定の再検討を差し戻すこと。
---

# Layer 2 Orchestrator

L2判定時のマルチエージェント調整を担う統括指揮スキル。

## 発動条件（厳格）

**REGIME.md のモードが `L2` と明記されている場合のみ発動**（**L0 spec-architect の判定結果**）。

人間が「L2 体制で進めて」等と明示指示した場合も、philosophy 第6条 H4「根本設計見直し」（モード昇格は人間専管）に該当するため、**まず spec-architect に差し戻し REGIME.md を L2 で確定させてから本スキルを起動する**。spec-architect を経由せず本スキルを直接起動しない。

参考: 設計上、L2 はプロジェクト全体の 10% 未満の発動を想定（M1/M2 で吸収可能なケースが多いため）。M1/M2 で誤起動しないこと。疑わしい場合は L0 に差し戻して REGIME.md の再判定を要求する。

**発動判定は L0 の責務**: L2 はスコア計算や閾値判定を自身で行わない。L0 が認識擦り合せで判定した結果を受け取って起動する受け手。

## 責務

**L2 は与えられた配下構成でマルチエージェント統括を実行することに全集中する**。
配下構成（どのサブエージェントを起動するか）は L0 が REGIME.md / INTEGRATION.md で決定済み。L2 は構成変更を独断で行わない（必要なら L0 に差し戻し）。

詳細プロトコルは `references/sub-agent-protocol.md` を参照。

1. **指定された配下構成の受領と確認**
   - REGIME.md / INTEGRATION.md から配下 Agent 構成を読み取る
   - 指定された構成（Playwright Test Agents 起動要否・L1 並列ドメイン数・integration-verifier scope 等）を受理
   - 指定がない / 実行不可能な場合は L0 に差し戻し（構成変更を独断でしない）

2. **L1エージェント群の起動調整**
   - 指定されたドメインごとに L1（autonomous-dev）を起動
   - 並列実行可能なサブゴールは並列化
   - 各L1の完了を待機・同期

3. **Playwright Test Agents の起動（指定時のみ）**
   - REGIME.md / INTEGRATION.md で `playwright-test-agents.enabled: true` の場合のみ起動
   - 配置: `references/e2e-integration.md` 参照（Planner / Generator / Healer / Reviewer）
   - 並列実行と結果集約

4. **検証フローの手配**
   - 各L1完了後に layer1-independent-reviewer を必須起動（M2同等のL1検証）
   - 全L1が PASS したら layer2-integration-verifier を起動
   - FAIL時の差戻し判断（L1差戻し or L0仕様見直し）
   - **L2 再設計は L2 の判断範囲外**（L0 に差し戻す）

5. **献上の統括**
   - 各L1のDELIVERY.md + VERIFICATION.md、Playwright Test Agents の review.md、および INTEGRATION.md を集約
   - 体制事後評価（L2レベル）の記載

## 処理フロー（概観）

```
1. REGIME.md / INTEGRATION.md 受領 → L2確定確認 + 配下Agent構成読み取り
2. 指定された配下構成の受理（構成変更は独断でしない。不可能なら L0 差し戻し）
3. ドメイン別 SPEC / sensors の切り出し（L0 指定に従う）
4. 各ドメインで L1 起動（並列可能なものは並列）
5. 指定時のみ Playwright Test Agents 並列起動（e2e-integration.md 参照）
6. 各L1完了 → layer1-independent-reviewer 必須起動
7. 全L1 PASS → layer2-integration-verifier 起動
8. PASS → 統合献上 / FAIL → 差戻し判断（L1差戻し or L0 差し戻し）
```

## 入力

- L0 から受領: `INDEX.md`, `SPEC.md`, `DONT.md`, `REGIME.md`, `CLAUDE.md`, `.claude/`, `sensors/`
- REGIME.md に L2 判定の根拠とサブドメイン提案が含まれることを期待

## 出力

- `DOMAINS.md` — ドメイン境界・契約定義
- 各ドメイン配下の完了したL1献上物
- `delivery/INTEGRATION.md` — 統合検証結果
- 統括した献上パッケージ

## 設計原則

- **フラクタル原則**: L2⇄L1群 の指揮⇄検証パターンは L0⇄人間 / L1内 spec⇄code と同一形状。哲学は `../layer0-spec-architect/references/philosophy.md` §1 を参照
- **情報純度原則**: `references/sub-agent-protocol.md` および `../layer0-spec-architect/references/philosophy.md` §3。L2⇄L1 の自然言語通信は情報損失が発生するため、契約はドキュメントで明示
- **L2 の責務境界**: L2 は与えられた責務をこなすことに全集中する。配下 Agent 構成の判断は L0 の責務であり、L2 は行わない
- **Level A所属**: 本skillは dialog-harness-layers 本体のもの。プロジェクトごとに生成しない
- **職種軸分業は採用しない**: 分割軸は抽象度軸・責務軸・機能軸のみ

## 参照ドキュメント

- `references/sub-agent-protocol.md` — サブエージェント統括の情報純度プロトコル（L2 の原則書）
- `references/e2e-integration.md` — Playwright Test Agents 規格（L2 配下の並列 E2E Agent 群）

## 実装ステータス

**現時点は雛形のみ**。L2発動は稀（全体の<10%）であり、実際の発動は Claude Opus 4.7 の能力では M2 で吸収可能なケースが多い。発動が必要になった時点で本SKILLを本実装する。

3層設計の完全性を担保するために雛形を先行して置いている。
