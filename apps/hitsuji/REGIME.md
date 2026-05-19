# Hitsuji — REGIME（モード判定結果）

## 判定結果サマリ

| 項目 | 値 |
|---|---|
| **Mode** | M2（標準モード） |
| **dev_mode** | github_assisted |
| **ARC** | monolith |
| **AI 能力バージョン** | Claude Opus 4.7 |
| **LC（Lifecycle Count）** | 0（新規プロジェクト） |
| **persona.active** | sheep-navigator |

---

## S / U / R スコアリング

| 軸 | スコア | 根拠 |
|---|---|---|
| **S（Scale, 規模）** | 1 | Android アプリ 1 個、機能 7 個、SPEC < 5k トークン、files < 80 想定 |
| **U（Uncertainty, 不確実性）** | 2 | 音声入力の認識精度・通知エスカレーションの UX 微調整に試行錯誤要素あり |
| **R（Risk, リスク）** | 1 | 個人専用ツール、ローカルデータ、不可逆操作なし、外部 API は読み取り primary |

**合計**: S + U + R = 4 → **M2 確定**（4〜=M2 の基準を満たす）

### L2 発動閾値チェック

| 閾値 | 本プロジェクト | 判定 |
|---|---|---|
| SPEC > 15k tok | < 5k tok | ✗ |
| files > 80 / 行 > 10k | < 80 想定 | ✗ |
| domains ≥ 5 | 1（タスク + 通知 + ゲーミフィ統合）| ✗ |
| 並行作業 ≥ 3 | 1 | ✗ |
| 1 サイクル > 2h | < 2h 想定 | ✗ |

→ **L2 発動なし**、M2 で進める。

### M2 強制判定

- R ≥ 2 による M2 強制：該当せず（R=1）
- U ≥ 3 による対話延長：該当せず（U=2、対話で十分具体化済み）

---

## NFR スコア

| カテゴリ | スコア | 備考 |
|---|---|---|
| 応答性 (latency) | 3 | UI p95 300ms、非同期処理必須 |
| 信頼性 (reliability) | 2 | 通知の取りこぼし許容率 < 1% |
| 保守性 (maintainability) | 2 | Phase 2 クラウド移行視野でスキーマ進化対応 |
| 規模 (scale) | 0 | 1 ユーザー専用 |
| セキュリティ | 1 | Phase 1 ローカル、Phase 2 で再評価 |
| **合計** | **8** | 中位（特別な NFR オーバーライドなし） |

---

## ARC 選定

**monolith** を採用。

| 根拠 | 詳細 |
|---|---|
| 単一デプロイ単位 | Android APK 1 つ |
| 単一ユーザー | 自分専用、分散不要 |
| ローカル先行 | Phase 1 でサーバ側コンポーネントなし |
| AI 自走完遂可能 | 標準 monolith パターンで開発完結 |

`realtime-pubsub` / `event-sourcing` パターンは本プロジェクトには不要。

---

## dev_mode 軸

### 選定結果: **github_assisted**

| 項目 | 値 |
|---|---|
| GitHub 利用 | ○ |
| GitHub Actions | 任意（CI ビルドは段階的に追加） |
| Issue 自動化 | ✗ |
| 並列実装 | 手動 |
| 自動 merge | ✗ |
| 人間関与 | L0 + 承認 |

### 根拠

- 個人ツールだが履歴遡及・PC 復元のため GitHub は使う
- 自分専用なので自動 merge / Issue 自動化は過剰
- ユーザー Must「シンプル」を尊重し、autonomous_scope = full は避ける

### 昇格余地

LC ≥ 1 到達後、運用が安定したら `autonomous`（autonomous_scope: merge_gated）への昇格を検討可能。
昇格時は ADR で記録必須。

---

## サブフェーズ起動結果（§3.5）

基本 5 問の判定：

| # | 質問 | 回答 | 起動 |
|---|---|---|---|
| S1 | データ保存？ DB 使う？ | YES（Room/SQLite ローカル）| L0-2 候補 |
| S2 | 外部 API とつなぐ？ | YES（Android SDK + Google Calendar）| L0-3 候補 |
| S3 | 画面 / 遷移は複雑？ | 中（4〜5 画面）| L0-4 起動 |
| S4 | 複数ユーザー権限？ | NO | L0-5 **スキップ** |
| S5 | 時間経過で状態自動遷移？ | YES（通知エスカレーション）| L0-6 起動 |

### 縮退判断

技術スタックが Kotlin Native のため、TypeScript エコシステム前提のサブフェーズ規定（Zod / TypeSpec / XState）の一部を縮退実施：

| サブフェーズ | モード | 成果物 |
|---|---|---|
| L0-2 ドメインモデル | **縮退（SPEC.md 内記述）** | SPEC.md `## ドメインモデル` セクション |
| L0-3 API 契約 | **縮退（SPEC.md 内記述）** | SPEC.md `## 外部 API 連携` セクション |
| L0-4 状態遷移 | **簡易（Mermaid のみ）** | `spec/state-diagrams.md` |
| L0-5 認可 | **スキップ** | — |
| L0-6 不変条件 | **完全実施** | `spec/invariants.feature` |

詳細は `delivery/ADR-001-subphase-scope.md` 参照。

---

## DESIGN.md 起動判定（§3.6）

UI ありプロジェクト → **DESIGN.md 起動確定**。
詳細は `DESIGN.md` 参照。

---

## persona

```yaml
persona:
  active: sheep-navigator
  override_state: null
```

ユーザー指定により羊系ナビゲーター persona で対話進行。
仕様策定の判断（Logic layer）は default と同等、応答出力（Presentation layer）のみ羊スタイル。

---

## 推奨モデル（実行前提示）

| Layer | 推奨 | 根拠 |
|---|---|---|
| L0 / 仕様策定対話 | Claude Opus 4.7 | 対話深度・要件抽出能力で最上位 |
| L1 / 実装 | Claude Opus 4.7 or Sonnet 4.6 | Kotlin + Compose のドメイン知識、コスト効率次第 |
| L1 独立検証 | Claude Sonnet 4.6 / Haiku 4.5 | 機械検証主体のためコスト軽減可 |

現在使用モデル: Claude Opus 4.7 → **推奨と整合**。

---

## 更新履歴

- 2026-05-19: 初版作成（L0 spec-architect 起動、Hitsuji プロジェクト立ち上げ、persona=sheep-navigator）
