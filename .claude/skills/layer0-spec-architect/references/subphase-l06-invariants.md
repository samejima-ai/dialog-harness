# L0-6: 層間不変条件対話プロトコル

ドメイン × API × 遷移 × 認可が同時に満たすべき条件を Gherkin で明文化する。
`spec/invariants.feature` を成果物として生成する。Happy / Sad / Evil の三分類で網羅する。

---

## 原則

- **Happy Path**: 正常系。仕様通りに動く確認。量は最小限（機能ごとに 1〜2 本）
- **Sad Path**: 予期される異常系（セッション切れ / バリデーション失敗 / 外部 API タイムアウト等）
- **Evil Path**: 悪意ある操作（他人のリソース操作 / 権限昇格 / 上限回避等）。L0-5 が起動している場合のみ
- L0-2〜L0-5 で定義した**名称（状態名・エラーコード・関係名）をそのまま**参照する
- 単層では表現できない「層をまたぐ」条件のみ記述（単層完結の条件は各サブフェーズのテストで担保）
- 共通プロトコルは `subphase-common-protocol.md` を参照

---

## 起動条件

`subphase-selection.md` の起動判定表より:

| 条件 | 挙動 |
|---|---|
| L0-2〜L0-5 のうち **2 つ以上が起動** | 完全モードで起動（三分類すべて） |
| L0-5 がスキップ | Evil Path Scenario を書かない |
| L0-2〜L0-5 の起動が 0〜1 個 | L0-6 は**起動しない**（層間を語る対象がないため） |

**単独起動禁止**: L0-6 はそれ単独で意味を持たない。必ず他サブフェーズの起動を前提とする。

---

## モード定義

### 完全モード（唯一のモード）
- Happy / Sad / Evil の三分類すべてを網羅
- 各 Feature は「何の不変条件を守るか」を冒頭記述
- Scenario の Given-When-Then は他サブフェーズ成果物の語彙を使用

### スキップ
- `invariants.feature` を生成しない
- L1 側で層間検証は行わない（各サブフェーズ単体検証のみ）

---

## 対話カテゴリ

各カテゴリで 1〜3 問を投げる。共通プロトコルの「1 回のターンで 5 問を超えない」原則を守る。
起動時点で L0-2〜L0-5 の成果物が揃っているため、**対話は極小**で済むケースが多い。

### Cat-1: Happy Path の代表シナリオ

- 「この機能が動けば最低限 OK」というシナリオを 2〜3 個挙げてください
- 各機能の正常完了条件は？

### Cat-2: Sad Path の発動条件

- セッション / ネットワーク / 外部 API の失敗時、何が起きるべきですか？
- バリデーション違反時のエラー形式は？（L0-3 のエラーレスポンスと一致）

### Cat-3: Evil Path の脅威モデル（L0-5 起動時のみ）

- 悪意あるユーザーが試みそうな操作は？（他人のリソース操作 / ID 推測 / 上限回避）
- 認可が破れたら最悪何が起きますか？

### Cat-4: トランザクション境界

- 複数の操作が同時に成功 / 失敗すべき塊はありますか？
- ロールバック条件は？

### Cat-5: 自動遷移の検証

- 時間経過の自動遷移（L0-4 の `DUE_DATE_PASSED` 等）が正しく発火する条件は？

---

## 生成物フォーマット

### ファイル配置
`spec/invariants.feature`

### 冒頭コメント規約

```gherkin
# L0-6: Cross-Layer Invariants (Gherkin)
# モード: 完全
# 生成日: YYYY-MM-DD
# 依存: L0-2〜L0-5 の成果物すべて
# ドメイン×API×遷移×認可が同時に満たすべき条件
```

### 主要セクション構造

```
1. Feature: ログイン / 認証系（L0-3 + L0-4 が起動時）
2. Feature: 所有権・Evil Path（L0-5 起動時）
3. Feature: ドメイン制約（L0-2 の集約上限）
4. Feature: 状態遷移（L0-4 起動時）
5. Feature: トランザクション境界
```

---

## TodoApp 実例（完全モード）

以下は `spec/invariants.feature` の完全な例。

```gherkin
# L0-6: Cross-Layer Invariants (Gherkin)
# ドメイン×API×遷移×認可が同時に満たすべき条件

Feature: ログイン認証の整合性
  画面状態・API認可・セッションが一致していること

  Scenario: 未ログイン状態でTODO APIは呼べない
    Given ユーザーが "loggedOut" 状態
    When GET /todos を呼ぶ
    Then 401 Unauthorized が返る

  Scenario: セッション切れで画面も強制ログアウト
    Given ユーザーが "loggedIn" 状態
    And セッションが期限切れ
    When 任意のAPIを呼ぶ
    Then 401 が返り、画面は "loggedOut" に遷移

---

Feature: TODO所有権の整合性
  他人のTODOは見えない・触れない（Evil Path）

  Scenario: 他人のTODOの読み取り拒否
    Given ユーザーAがTODO "todo-X" を所有
    And ユーザーBがログイン中
    When ユーザーBが GET /todos/todo-X を呼ぶ
    Then 403 Forbidden が返る
    And DBには変化なし

  Scenario: 他人のTODO一覧には含まれない
    Given ユーザーAがTODO "todo-X" を所有
    And ユーザーBがログイン中
    When ユーザーBが GET /todos を呼ぶ
    Then レスポンスに "todo-X" は含まれない

  Scenario: 他人のTODOの更新拒否
    Given ユーザーAがTODO "todo-X" を所有
    And ユーザーBがログイン中
    When ユーザーBが PATCH /todos/todo-X を呼ぶ
    Then 403 Forbidden が返る
    And DBには変化なし

---

Feature: TODO数上限の整合性
  ドメイン制約（USER_TODO_LIMIT=100）がAPIで強制されること

  Scenario: 100件未満なら作成可能
    Given ユーザーAが99件のTODOを所有
    When POST /todos でTODOを作成
    Then 201 Created が返る
    And ユーザーAのTODOは100件になる

  Scenario: 100件に達したら作成拒否
    Given ユーザーAが100件のTODOを所有
    When POST /todos でTODOを作成
    Then 403 Forbidden が返る
    And エラーコードは "TODO_LIMIT_EXCEEDED"
    And DBには追加されない

---

Feature: 状態遷移の整合性
  ステータスの遷移がFSM定義に従うこと

  Scenario: expiredへの手動遷移は不可
    Given ユーザーAがpending状態のTODOを所有
    When PATCH /todos/todo-X で status=expired を送信
    Then 400 Bad Request が返る
    And TODOのstatusは変化しない

  Scenario: 締切超過で自動的にexpired
    Given TODOがpending状態でdueDateが過去
    When スケジューラが実行される
    Then TODOのstatusは "expired" になる

---

Feature: トランザクション境界
  複数操作の原子性

  Scenario: 作成時のDB保存とイベント発火は原子的
    When POST /todos でTODOを作成
    Then DBへのINSERTとイベント通知は同一トランザクション
    And 一方が失敗したら両方ロールバック
```

---

## 前サブフェーズからの入力

- **L0-1 `SPEC.md`**: 不変条件の出典（条件節・制約節）
- **L0-2 `domain.ts`**: 状態名・enum 値・集約上限（`USER_TODO_LIMIT` → "100件に達したら"）
- **L0-3 `api.tsp`**: エンドポイント・HTTP ステータス・エラーコード（`TODO_LIMIT_EXCEEDED`）
- **L0-4 `state-machine.ts`**: 状態名・遷移イベント（`pending` / `DUE_DATE_PASSED`）
- **L0-5 `authz.fga`**: 関係名（`owner` / `can_read`）→ Evil Path Scenario の論拠

---

## 後続サブフェーズへの出力

L0-6 は L0 の最終サブフェーズ。後続の L0 サブフェーズは存在しない。
出力は **L1 の独立検証（layer1-independent-reviewer）が網羅検証**する。

---

## 検証フェーズ（Phase γ）

生成後、以下をクロスチェック:

| 観点 | チェック方法 |
|---|---|
| 三分類の網羅 | Happy / Sad / Evil すべてが少なくとも 1 本存在（L0-5 未起動時は Evil 免除） |
| 名称の一貫性 | 状態名・エラーコード・関係名が L0-2〜L0-5 の表記と完全一致 |
| 単層完結 Scenario の排除 | 単一サブフェーズでテスト可能な内容は含まない（層間のみ） |
| Given 節の根拠 | Given の状態が L0-4 の FSM に存在する状態のみ |
| Then 節の検証可能性 | 曖昧表現（「適切に」「うまく」）が含まれていない |

不整合検出時は Phase α に戻り、該当 Cat の追加質問を投げる。

---

## 検証コマンド

Phase 2 で `sensors/computational.md` に正式移動予定。Phase 1 では以下を推奨として記録のみ:

```bash
# Gherkin 構文チェック
npx @cucumber/cucumber --dry-run spec/invariants.feature

# Scenario 数の集計
grep -c "^  Scenario:" spec/invariants.feature
```

---

## 既存の類似単層ファイルとの関係

- `spec-review-checklist.md`（Phase 3 で連携予定）: L1 独立検証時に `invariants.feature` の全 Scenario を走査し、実装で満たされているか確認する
- `schema-evolution.md`: データモデル進化による Feature 文言の更新責務は L0-2 改訂時に発火

---

## L1 との連携

L1 autonomous-dev は `spec/invariants.feature` を以下のように利用する:

- 実装完了後、Gherkin を E2E テストのスケルトンとして利用（Cucumber / Playwright-cucumber）
- L1 独立検証（`layer1-independent-reviewer`）は全 Scenario を網羅的にレビューし、実装との乖離を報告
- 失敗した Scenario は `DELIVERY.md` の「層間不変条件チェック」セクションに記録

---

## 不変条件の配置プロトコル: アプリ層 vs DB 層 vs 状態機械（v5.17.0 追加）

不変条件（ビジネスルール）は単一層で表現するだけでは不十分。同じルールを **多層で冗長に表現** することで、どれか一層が破られても他層が防波堤となる「多層防御」を構築する。`invariants.feature` で記述する Scenario は、この多層配置の整合性検査に位置付ける。

### 3 つの配置層と責務

| 層 | 担当 | 検出タイミング | 不可逆性 |
|---|---|---|---|
| **アプリ層**（Zod / TypeScript） | L0-2 `domain.ts` で型・バリデーション・enum | リクエスト受領時 | 修正容易（コード変更で済む） |
| **DB 層**（CHECK / FK / UNIQUE / NOT NULL） | L1 migration で物理制約付与 | INSERT / UPDATE 時に物理的に弾く | **最後の砦**、スキーマ変更要 |
| **状態機械**（L0-4 `state-machine.ts`） | XState で許可遷移を列挙 | 状態遷移発火時 | コード変更で対応可 |

各層は独立に同じ不変条件を表現する。例: `Todo.status` が `["pending","completed","expired"]` のみという不変条件は、L0-2 で Zod enum / L0-4 で XState の states / DB 層で `CHECK (status IN ('pending','completed','expired'))` の 3 箇所で表現する。

### DB レベル制約のチェックリスト

L0-2 で定義された制約を DB 層に必ず反映させる対応表（Phase γ クロスチェックで使用）：

| L0-2 表現 | DB 層対応 |
|---|---|
| `z.string().min(1)` | `NOT NULL` + `CHECK (length(col) >= 1)` |
| `z.string().email()` | `CHECK (col ~* '^.+@.+\..+$')` または独立 email_format 関数 |
| `z.enum(["a","b","c"])` | `CHECK (col IN ('a','b','c'))` または ENUM 型 |
| `UserId` (brand 型) | 対応する `users` テーブルへの FK + `NOT NULL` |
| `USER_TODO_LIMIT = 100` の集約上限 | アプリ層のみで強制（DB トリガーは保守困難、推奨しない） |
| `UNIQUE` 性（email 重複禁止等） | `UNIQUE INDEX` |

集約上限（COUNT 系制約）は DB トリガーで強制可能だが、保守困難 + 性能影響大のためアプリ層強制が推奨。Evil Path Scenario で「上限を超える操作」が L0-3 の API 層で 403 を返すことを確認する。

### 状態遷移の統治パターン

L0-4 で定義された状態遷移を「不正な状態への遷移」から守るパターン：

1. **テーブル駆動**: `allowed_transitions` テーブルで（from_state, to_state）の許可ペアを列挙。アプリ層は遷移要求時にこのテーブルを参照
2. **enum + 関数強制**: `transition(current_state, event) -> new_state | error` の関数で網羅、enum 外への遷移は型エラー
3. **イベントソーシング**（ARC = event-sourcing 時）: 状態は派生（イベント列の畳み込み）、遷移は append-only のイベント追記で表現。不正遷移は **aggregate が command 段階で reject** し、不正な event をイベントストリームに append させない（事前防止）。CompensatingEvent は既に記録済みの**正当だが事後的に誤りと判明した事実**の訂正に用いる別概念で、不正遷移防止には使わない

非エンジニア対話では (2) の enum + 関数強制が直感的。Evil Path Scenario「pending から expired への手動遷移は不可」は (2) で表現される。

### 監査ログ・履歴管理の選択基準

NFR C (Compliance) ≥ 2 または S (Security) ≥ 2 の場合、変更履歴の保存が要件化される。選択肢：

| パターン | 仕組み | 適用場面 |
|---|---|---|
| **シャドウテーブル** | `users` と並行に `users_history` を持ち、UPDATE 時に旧行を append | 特定エンティティのみ詳細履歴が必要、クエリ高速 |
| **Row Versioning** | 全行に `version` / `valid_from` / `valid_to` を持つ Temporal Table | 全エンティティで一律監査、時系列クエリ多用 |
| **Generic Audit Log** | 単一 `audit_log` テーブルに（table, row_id, operation, before, after, who, when）を JSON で記録 | 監査対象が多種多様、頻度低 |
| **Event Sourcing 統合** | ARC = event-sourcing 時、イベント自体が完全な監査ログ | event-sourcing 採用時の自然選択 |

判定軸: 履歴クエリ頻度 / 監査対象エンティティ数 / 規制要件の厳しさ / ARC 選択。

### Cat-6: 不変条件配置（新規追加）

L0-6 起動時に以下を確認する（既存 Cat-1〜5 に追加）：

- 同じ制約を **アプリ層と DB 層の両方** で表現すべきものは？
- 「絶対に破られてはいけない」最後の砦の不変条件は？（→ DB 層で物理制約必須）
- 監査履歴の保存要件は？（規制 / 内部ガバナンス / トラブルシューティング）

### Phase γ クロスチェック追補

| 観点 | チェック方法 |
|---|---|
| 多層配置の整合（DB 強制可能なもの） | L0-2 の enum / nullable / FK / UNIQUE 性が DB 制約（CHECK / NOT NULL / FOREIGN KEY / UNIQUE INDEX）として L1 migration に反映予定であることを `invariants.feature` の Scenario で表現 |
| 集約上限の整合（アプリ層強制） | L0-2 の `USER_TODO_LIMIT` 等の集約上限は L0-3 API 層で強制される旨（403 + エラーコード）を `invariants.feature` Scenario で表現。DB 層強制（トリガー）は要求しない |
| 監査要件の明示 | NFR C ≥ 2 or S ≥ 2 の場合、SPEC.md に監査ログパターンが選択済み |
| 状態遷移の網羅 | L0-4 の状態遷移表が `invariants.feature` の Sad/Evil Path で網羅されている |

### AD-032 候補（DAG verify 対称化）との接続

ARCH-DECISIONS.md AD-032 候補で温存中の「Hard Gate（守備） ⇄ DAG verify（攻撃）対称化」検討は、本セクションの「多層防御」と同型概念。Hard Gate がツール呼び出し時の守りなら、DAG verify は不変条件の能動的検証側に位置する。AD-032 本実装時に本セクションは検査基盤データの出所となる（現時点では候補温存、本セクションは独立して機能）。

---

## プロトコル自己評価

- Happy Path を書きすぎる傾向がある。機能数 × 1〜2 本が上限目安。多すぎたら各サブフェーズのテストに振り分け
- Evil Path は L0-5 とセットで意味を持つ。L0-5 スキップ時に無理に書かない
- 「トランザクション境界」の Scenario は技術的詳細に寄るため、非エンジニア対話では引き出しにくい。AI が提案型で挿入し、人間は承認のみで可
- Gherkin は日本語混在でも動作するが、キーワード（Given / When / Then 等）は英語維持が推奨（parser 互換性のため）
- 多層防御は「同じことを 3 箇所で書く」冗長性に見えるが、これは意図的な防波堤設計。「DRY 原則違反」と誤解される可能性があり、SPEC.md コメントで意図を明示する
