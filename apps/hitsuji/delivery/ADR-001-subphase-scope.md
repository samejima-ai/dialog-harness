# ADR-001: L0 サブフェーズの縮退判断（Kotlin Native プロジェクト）

| 項目 | 値 |
|---|---|
| Date | 2026-05-19 |
| Status | Accepted |
| Decider | L0 spec-architect + 人間（一次承認） |
| Project | Hitsuji (apps/hitsuji) |
| LC | 0（新規プロジェクト） |

---

## Context（背景）

dialog-harness-layers v5.17.0 の §3.5「L0 サブフェーズ起動と縮退」は、TypeScript エコシステム（Zod / TypeSpec / XState）を**標準的な記述メディア**として想定している。Hitsuji は **Android Native（Kotlin + Jetpack Compose）** であり、これらの TypeScript 系ツール群は本プロジェクトの実装スタックと整合しない。

サブフェーズ判定 5 問の結果：

| # | 質問 | 回答 |
|---|---|---|
| S1 | データ保存？ DB 使う？ | YES（Room/SQLite ローカル） |
| S2 | 外部 API とつなぐ？ | YES（Android SDK + Google Calendar API） |
| S3 | 画面 / 遷移は複雑？ | 中（4〜5 画面） |
| S4 | 複数ユーザー権限？ | NO |
| S5 | 時間経過で状態自動遷移？ | YES（通知エスカレーション） |

この結果、L0-2（ドメインモデル）/ L0-3（API 契約）/ L0-4（状態遷移）/ L0-6（不変条件）が起動候補となる。

## Decision（決定）

| サブフェーズ | 標準モード | **本プロジェクトでの採用形式** | 成果物 |
|---|---|---|---|
| L0-2 ドメインモデル | TypeScript + Zod schema / 別ファイル | **縮退：SPEC.md `## ドメインモデル` セクションに Markdown 擬似コードで記述** | `SPEC.md` 内 |
| L0-3 API 契約 | TypeSpec / OpenAPI 別ファイル | **縮退：SPEC.md `## 外部 API 連携` 表で記述（OS パーミッション列含む）** | `SPEC.md` 内 |
| L0-4 状態遷移 | XState 機械可読 JSON + Mermaid | **簡易：Mermaid 図のみで記述（XState JSON 化は省略）** | `spec/state-diagrams.md` |
| L0-5 認可 | 認可マトリクス | **スキップ：単一ユーザー前提のため不要** | — |
| L0-6 不変条件 | Gherkin (.feature) | **完全実施：Happy / Sad / Evil 3 系統で記述** | `spec/invariants.feature` |

## Rationale（根拠）

### L0-2 / L0-3 縮退の根拠

- Kotlin の `data class` および Android SDK は**型情報がコード内で自己完結**するため、TS 系で必要だった「実装言語と独立した契約記述」のメリットが薄い
- ドメインモデルが小規模（4 entity）であり、独立ファイル化のオーバーヘッドが情報密度向上を上回らない
- SPEC.md 内で擬似コード形式（Markdown コードブロック）で記述することで**一覧性を確保**
- 実装時は SPEC.md の擬似コードを参照して Kotlin `data class` を手で起こす運用

### L0-4 簡易化の根拠

- 状態遷移は **通知エスカレーション（時間ドリブン）** が主であり、XState で記述しても**機械的なシミュレーション実行が当面不要**
- Mermaid 図で**人間が読める可視化**を確保すれば、設計レビューと L1 実装ガイドとしては十分
- 将来テストハーネスで状態シミュレーションが必要になった場合、Mermaid → XState への変換は機械的に可能

### L0-5 スキップの根拠

- SPEC.md / DONT.md で**単一ユーザー前提**が明文化されている
- マルチユーザー / 権限分離は DONT 4 で明示的に排除されている
- 認可マトリクスを書く対象が存在しない

### L0-6 完全実施の根拠

- ADHD 当事者向けアプリの性質上、**通知の取りこぼし**は致命的な信頼性問題（NFR reliability=2）
- 段階エスカレーションの状態間矛盾（例：Lv.4 到達後に Lv.1 に戻る等）は **Evil 系不変条件**で守る必要あり
- Gherkin は Kotlin/Compose プロジェクトでも **kotlin-cucumber** で実行テスト化可能、無駄にならない

## Consequences（影響）

### Positive

- ✅ Markdown 中心の運用で**人間レビュー速度が向上**
- ✅ TypeScript ツール依存ゼロで**Android プロジェクトと整合**
- ✅ 不変条件 (.feature) のみ別ファイル化することで**「ここだけは厳密」の重要度が際立つ**

### Negative / トレードオフ

- ⚠️ ドメインモデルの**機械検査**（Zod ランタイムバリデーション等）は手動 Kotlin code に委ねる
- ⚠️ API 契約の**自動生成クライアント**（OpenAPI codegen）は不可、L1 で手書きの retrofit/Ktor 実装になる
- ⚠️ 状態機械の**機械的探索テスト**（model checking）は将来課題

### 再評価条件

以下のいずれかに該当した場合、本 ADR を再評価する：

- LC ≥ 2 到達後、ドメインモデルが entity 10 以上に拡張された場合
- 状態遷移パスが Lv.4 + Snooze の組合せで網羅困難になった場合
- Phase 2（クラウド同期）開始時、サーバ側 API 契約が独立記述を要する場合
- マルチユーザー化が SPEC に入った場合（L0-5 を再起動）

## References

- dialog-harness-layers SKILL.md §3.5（L0 サブフェーズ起動と縮退）
- `SPEC.md` `## ドメインモデル` `## 外部 API 連携`
- `spec/state-diagrams.md`
- `spec/invariants.feature`
- `REGIME.md` `## サブフェーズ起動結果`
