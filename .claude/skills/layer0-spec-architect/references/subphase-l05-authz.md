# L0-5: 認可モデル対話プロトコル

OpenFGA DSL によるリレーション型認可モデル定義のための対話プロトコル。
`spec/authz.fga` または `spec/authz-matrix.md` を成果物として生成する。

---

## 原則

- 役割（role）ではなく**関係（relation）**で表現する（ReBAC パラダイム）
- リソース（type）ごとに許可操作（can_read / can_write / can_delete）を列挙
- 「所有者は読み書き削除できる」のような集約ルールを継承関係で表現
- 明示的に書かれていない関係は**拒否**（デフォルトデニー）
- 共通プロトコルは `subphase-common-protocol.md` を参照

---

## 起動条件

`subphase-selection.md` の起動判定表より:

| 条件 | モード |
|---|---|
| 複数ユーザー + リソース所有権 or 共有機能あり | 完全モード（OpenFGA DSL） |
| 複数ユーザーだが権限は固定（全員管理者 or 全員一般） | 簡易モード（認可マトリクス） |
| シングルユーザー or 認可概念なし | スキップ |

**依存ルール**: L0-2 がスキップの場合、type 定義の根拠（どのエンティティに認可が必要か）が不明のため起動不可。

---

## モード定義

### 完全モード
- OpenFGA DSL で model / type / relations を記述
- 継承関係（`define writer: owner`）で権限ピラミッドを構築
- organization / team 等の中間 type も許容

### 簡易モード
- 認可マトリクス（Markdown 表）のみ
- 行: ロール、列: 操作、セル: 許可/拒否
- OpenFGA ランタイムは使わない

### スキップ
- 認可ファイルを生成しない
- L0-6 の Evil Path Scenario は書かない

---

## 対話カテゴリ

各カテゴリで 1〜3 問を投げる。共通プロトコルの「1 回のターンで 5 問を超えない」原則を守る。

### Cat-1: 主体と資源

- 認可の主体（誰が）は何ですか？（user / team / org / service account）
- 保護対象のリソースは何ですか？（L0-2 のエンティティと対応）

### Cat-2: 所有・作成者ルール

- リソースに所有者の概念はありますか？
- 作成者は自動的に所有者になりますか？

### Cat-3: 共有・委譲

- 他のユーザーへの共有（read/write 付与）はありますか？
- 組織・チーム単位でのアクセス権はありますか？

### Cat-4: 管理者・特権

- 全リソースに干渉できる管理者ロールはありますか？
- 管理者と一般ユーザーの境界は？

### Cat-5: 操作の粒度

- リソースごとに許可操作は何種類？（read / write / delete / share / comment...）
- 操作間の包含関係は？（write できるなら read も自動で可、等）

---

## 生成物フォーマット

### ファイル配置
完全モード: `spec/authz.fga`
簡易モード: `spec/authz-matrix.md`

### 冒頭コメント規約（完全モード）

```
# L0-5: Authorization Model (OpenFGA DSL)
# モード: 完全
# 生成日: YYYY-MM-DD
# 依存: spec/domain.ts の brand 型を type として参照
```

### 主要セクション構造（完全モード）

```
1. model schema 宣言
2. type user（主体）
3. type <resource>（保護対象ごとに 1 ブロック）
   - relations: 所有関係・権限関係
```

---

## TodoApp 実例（完全モード）

以下は `spec/authz.fga` の完全な例。

```
# L0-5: Authorization Model (OpenFGA DSL)

model
  schema 1.1

type user

type todo
  relations
    # TODOの所有者は作成者のみ
    define owner: [user]

    # 読み取り権限 = 所有者のみ
    define can_read: owner

    # 書き込み権限 = 所有者のみ
    define can_write: owner

    # 削除権限 = 所有者のみ
    define can_delete: owner
```

---

## 簡易モード成果物例

`spec/authz-matrix.md`:

```markdown
# 認可マトリクス（簡易モード）

| ロール \ 操作 | todo.read | todo.write | todo.delete |
|---|---|---|---|
| owner       | ✓ | ✓ | ✓ |
| admin       | ✓ | ✓ | ✓ |
| guest       | ✗ | ✗ | ✗ |

- owner: リソース作成者
- admin: システム管理者（全 todo 干渉可）
- guest: 認証済みだが所有権なし
```

OpenFGA DSL・関係グラフ・継承の概念を省略。

---

## 前サブフェーズからの入力

- **L0-1 `SPEC.md`**: 権限・ロール・共有機能の記述、マルチユーザーの明示
- **L0-2 `domain.ts`**: `UserId` / `TodoId` 等の brand 型 → `type user` / `type todo` として定義
- **L0-3 `api.tsp`**: エンドポイントごとに必要な認可（list = can_read 所有者フィルタ等）

---

## 後続サブフェーズへの出力

以下の要素が後続で参照される（`subphase-common-protocol.md` の I/O 契約表と整合）:

- **関係名**: `owner` / `can_read` / `can_write` → L0-6 の Evil Path Scenario
- **type 定義**: `user` / `todo` → L0-6 の Given 節の主体・資源表現
- **拒否規則**: 「所有者以外は can_write できない」→ L0-6 の Scenario Outline

---

## 検証フェーズ（Phase γ）

生成後、以下をクロスチェック:

| 観点 | チェック方法 |
|---|---|
| domain.ts の brand 型網羅 | `domain.ts` の brand 型が `authz.fga` の type として存在 |
| api.tsp のエンドポイント網羅 | 全エンドポイントが何らかの relation で認可を得られる |
| デフォルトデニー | 明示的に書かれていない関係でリソースにアクセスできないことを確認 |
| 継承関係の妥当性 | `can_write: owner` のような継承が SPEC.md の意図と一致 |
| 自己干渉防止 | 所有者ルールが他ユーザー干渉を防ぐ（owner は自分のみ） |

不整合検出時は Phase α に戻り、該当 Cat の追加質問を投げる。

---

## 検証コマンド

Phase 2 で `sensors/computational.md` に正式移動予定。Phase 1 では以下を推奨として記録のみ:

```bash
# OpenFGA DSL validator
fga model validate --file spec/authz.fga

# Check query の smoke test（サーバー起動後）
fga query check user:alice can_read todo:todo-1 --store-id <STORE>
```

---

## 既存の類似単層ファイルとの関係

- `permission-delegation.md`: AI への権限委譲レベル（L0-2 / L0-3）と、本 L0-5 の人間→人間の認可は**別の関心事**。混同しない
- `domain-context-dialog.md`: 業界固有の権限階層（医療・金融の厳格なロール）は DOMAIN-CONTEXT.md で引き出した後、L0-5 の relations に落とす

---

## L1 との連携

L1 autonomous-dev は `spec/authz.fga` を以下のように利用する:

- OpenFGA サーバーへ `fga model write` で投入
- 各エンドポイントで `fga query check` を呼び出して認可判定
- 認可失敗時は `api.tsp` の 403 エラーレスポンスを返す

---

## プロトコル自己評価

- OpenFGA はランタイム依存が重い（サーバー必須）。小規模プロジェクトでは簡易モードで十分
- 「所有者のみ」ルールは頻出なので、テンプレ化して対話を短縮可能
- 管理者特権（admin type）は権限拡散のリスクがある。追加時は Cat-4 で必ず確認する
