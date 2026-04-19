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

## プロトコル自己評価

- Happy Path を書きすぎる傾向がある。機能数 × 1〜2 本が上限目安。多すぎたら各サブフェーズのテストに振り分け
- Evil Path は L0-5 とセットで意味を持つ。L0-5 スキップ時に無理に書かない
- 「トランザクション境界」の Scenario は技術的詳細に寄るため、非エンジニア対話では引き出しにくい。AI が提案型で挿入し、人間は承認のみで可
- Gherkin は日本語混在でも動作するが、キーワード（Given / When / Then 等）は英語維持が推奨（parser 互換性のため）
