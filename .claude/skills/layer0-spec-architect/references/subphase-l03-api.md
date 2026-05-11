# L0-3: API 契約対話プロトコル

TypeSpec による型安全な API 契約生成のための対話プロトコル。
`spec/api.tsp` を成果物として生成する。

---

## 原則

- TypeSpec で OpenAPI / JSON Schema / gRPC 等へ後工程変換可能な契約を記述
- `domain.ts` の型名を **そのまま** Model 名として再利用（翻訳しない）
- エラーコードは文字列定数で明示し、後続 L0-6 の Scenario で参照可能にする
- HTTP ステータスと意味論（403 = 認可違反、409 = 競合、422 = バリデーション等）を一貫させる
- 認証方式は 1 つに絞る（Bearer / Cookie / API Key のいずれか）
- 共通プロトコルは `subphase-common-protocol.md` を参照

---

## 起動条件

`subphase-selection.md` の起動判定表より:

| 条件 | モード |
|---|---|
| 外部公開 API あり、または複数クライアントから呼ばれる | 完全モード（TypeSpec） |
| 内部呼び出しのみ、関数シグネチャで十分 | 簡易モード（TypeScript 関数型） |
| API 境界が存在しない（CLI ワンショット等） | スキップ |

**依存ルール**: L0-2 がスキップの場合、完全モードは起動不可（簡易モードのみ可）。L0-2 の型を参照できないため。

---

## モード定義

### 完全モード
- TypeSpec による service / namespace / interface / model 記述
- HTTP メソッド・ステータス・エラーレスポンスを網羅
- 認証方式の明示
- `domain.ts` の型を Model として再利用

### 簡易モード
- TypeScript 関数シグネチャのみ（`api-signatures.ts`）
- 戻り値 / 引数の型のみ定義
- HTTP 層を省略（直接呼び出し想定）

### スキップ
- `api.tsp` / `api-signatures.ts` を生成しない
- L0-5（認可）は起動不可、または関数単位で代替

---

## 対話カテゴリ

各カテゴリで 1〜3 問を投げる。共通プロトコルの「1 回のターンで 5 問を超えない」原則を守る。

### Cat-1: 境界と公開範囲

- この API は外部公開ですか？ 内部のみですか？
- 呼び出し側は何ですか？（ブラウザ SPA / モバイル / 他のサーバー）

### Cat-2: 認証方式

- ログイン方式は？（メール+パスワード / SSO / API Key / 匿名）
- トークンの持ち回りは？（Bearer / Cookie / ヘッダ）

### Cat-3: 主要エンドポイント

- どんな操作が必要ですか？（CRUD 以外の特殊操作は？）
- 一覧取得時のページング・ソート・フィルタは必要ですか？

### Cat-4: エラーレスポンス

- エラー時の共通形式は？（code + message / RFC 7807 / 独自）
- ビジネスロジックエラー（例: 上限超過）は HTTP 何番を返す？

### Cat-5: バージョニング

- 将来の後方互換ポリシーは？（URL に v1 / ヘッダ / なし）

---

## 生成物フォーマット

### ファイル配置
完全モード: `spec/api.tsp`
簡易モード: `spec/api-signatures.ts`

### 冒頭コメント規約

```typescript
// L0-3: API Contract (TypeSpec | Simple Signatures)
// モード: 完全 | 簡易
// 生成日: YYYY-MM-DD
// 依存: spec/domain.ts の型を参照
```

### 主要セクション構造（完全モード）

```
1. import（@typespec/http 等）
2. @service / namespace
3. Model 定義（domain.ts のミラー）
4. Request / Response Model
5. ErrorResponse 共通型
6. interface（エンドポイント群）
```

---

## TodoApp 実例（完全モード）

以下は `spec/api.tsp` の完全な例。

```typespec
// L0-3: API Contract (TypeSpec)
// domain.ts の型を入力として、AIが生成

import "@typespec/http";
using TypeSpec.Http;

@service({ title: "TodoApp API" })
namespace TodoApp;

// ===== Models =====
model User {
  id: string;  // UserId
  email: string;
  createdAt: utcDateTime;
}

model Todo {
  id: string;  // TodoId
  ownerId: string;
  title: string;
  body: string;
  status: "pending" | "completed" | "expired";
  dueDate: utcDateTime | null;
  createdAt: utcDateTime;
  updatedAt: utcDateTime;
}

model CreateTodoRequest {
  title: string;
  body?: string;
  dueDate?: utcDateTime;
}

model UpdateTodoRequest {
  title?: string;
  body?: string;
  status?: "pending" | "completed";  // expiredへの手動遷移は不可(L0-4で定義)
  dueDate?: utcDateTime;
}

model ErrorResponse {
  code: string;
  message: string;
}

// ===== Endpoints =====
@route("/auth")
interface Auth {
  @post login(@body body: { email: string; password: string }): {
    @statusCode _: 200;
    token: string;
  } | { @statusCode _: 401; @body error: ErrorResponse };
}

@route("/todos")
interface Todos {
  // 自分のTODOのみ取得（L0-5で強制）
  @get list(): Todo[];

  @get read(@path id: string): Todo | { @statusCode _: 404; @body error: ErrorResponse };

  @post create(@body body: CreateTodoRequest): {
    @statusCode _: 201;
    @body todo: Todo;
  } | { @statusCode _: 403; @body error: ErrorResponse };  // 100件上限エラー

  @patch update(@path id: string, @body body: UpdateTodoRequest): Todo
    | { @statusCode _: 403; @body error: ErrorResponse }   // 他人のTODO
    | { @statusCode _: 404; @body error: ErrorResponse };

  @delete remove(@path id: string): { @statusCode _: 204 }
    | { @statusCode _: 403; @body error: ErrorResponse }
    | { @statusCode _: 404; @body error: ErrorResponse };
}
```

---

## 簡易モード成果物例

```typescript
// L0-3: API Contract (Simple Signatures)
// モード: 簡易
// 生成日: YYYY-MM-DD

import type { Todo, User } from "./domain";

export type CreateTodoInput = { title: string; body?: string; dueDate?: Date };
export type UpdateTodoInput = Partial<Pick<Todo, "title" | "body" | "status" | "dueDate">>;

export interface TodoApi {
  list(): Promise<Todo[]>;
  read(id: string): Promise<Todo | null>;
  create(input: CreateTodoInput): Promise<Todo>;
  update(id: string, input: UpdateTodoInput): Promise<Todo>;
  remove(id: string): Promise<void>;
}
```

HTTP 層・認証・エラーコードを省略。関数型のみ。

---

## 前サブフェーズからの入力

- **L0-1 `SPEC.md`**: WHAT 節の機能（エンドポイント候補）、条件節（エラー条件・上限値）
- **L0-2 `domain.ts`**: 型名・enum 値・集約上限値を Model 名として再利用

---

## 後続サブフェーズへの出力

以下の要素が後続で参照される（`subphase-common-protocol.md` の I/O 契約表と整合）:

- **エンドポイント一覧**: `Todos.list` / `Todos.create` 等 → L0-5 の認可対象、L0-6 の When 節
- **エラーコード**: `TODO_LIMIT_EXCEEDED` 等の文字列定数 → L0-6 の制約 Scenario
- **HTTP ステータス**: 403 / 404 等の意味論 → L0-6 の Evil Path Scenario

---

## 検証フェーズ（Phase γ）

生成後、以下をクロスチェック:

| 観点 | チェック方法 |
|---|---|
| domain.ts の型網羅 | `domain.ts` のエンティティ型が `api.tsp` の Model に存在 |
| enum 値の一致 | `TodoStatus` の値が `api.tsp` のユニオン型で同一表記 |
| エラーコード整合 | SPEC.md の上限値違反エラーが `api.tsp` の ErrorResponse として定義 |
| 認証方式一貫 | 全エンドポイントで同じ認証方式が適用されている |
| HTTP メソッド妥当性 | GET は副作用なし、POST は作成、PATCH は部分更新、DELETE は削除 |

不整合検出時は Phase α に戻り、該当 Cat の追加質問を投げる。

---

## 業界叡智参照モード（Phase γ-i 連携、CTL ≥ 1、W5-Q2 採決追加）

Wave 5 W5-Q2 採決 (`council-2026-05-11T12:15:00Z-w5qb02`、B 段階組込、conf 0.72) で確定した subphase 個別の業界叡智参照モード。`subphase-common-protocol.md` Phase γ-i フック起動時に L0-3 (API 契約) は以下の業界叡智ソースを参照する。**観測駆動、候補出力のみ、自動採用なし**（philosophy 第 8 条 3 段階モデル準拠）。

### 参照ソース

| ソース | 配置 | 主な参照観点 |
|---|---|---|
| ECC agents 定義パターン | `history/refs-draft/ecc/agents-catalog.md` | YAML frontmatter (name / description / tools / model) 規格、PROACTIVE トリガー文言、本文 system role 定義 |
| Claude Code settings schema | `https://json.schemastore.org/claude-code-settings.json` | `.claude/settings.json` の permission / env / hook 設定との連動可否（参照のみ、外部 URL）|

### 照合観点（Phase γ-i フックが Phase γ 検証時に追加）

API 契約上の agent / endpoint / authentication 設計が以下の業界慣例と整合しているかを照合：

| # | 観点 | 業界叡智ソース | match_type |
|---|---|---|---|
| 1 | API agent の `tools` 列挙が読み取り専用パターンに沿うか | ECC agents-catalog §2「agent 定義パターン」 | complementary |
| 2 | agent の `description` がトリガー文言 (PROACTIVELY 等) を持つか | 同上 | complementary |
| 3 | API endpoint の認証方式 (Bearer / Cookie / API Key) が settings.schema の permission 区分と一貫するか | ECC agents-catalog + settings schema | contradictory 検知用 |
| 4 | エラーレスポンス共通型が ECC agents の出力規約と相反しないか | ECC agents-catalog §2「本文構造」出力規約 | redundant 検知用 |

### 候補リスト出力例

```yaml
industry_wisdom_match_candidates:
  - source: "ECC agents-catalog.md §2"
    aspect: "agent 定義の YAML frontmatter (tools/model 指定)"
    spec_draft_reference: "api.tsp §interface Auth"
    match_type: "complementary"
    suggestion: "ECC では認証系 agent に tools: [\"Read\"] のみ列挙する慣例あり、Bearer エンドポイントの読み取り権限境界として参照候補"
    confidence: 0.7
```

### 第 8 条 3 段階モデル準拠

- **観測**: `api.tsp` / `api-signatures.ts` ドラフトと `agents-catalog.md` の照合
- **候補化**: `industry_wisdom_match_candidates` リストとして Phase δ 差分サマリに含める
- **人間最終承認**: Phase δ でユーザー承認（自動採用なし、philosophy 第 6 条準拠）

### CTL 連動

- **CTL 0**: 本セクション inactive（観察温存、候補化も抑止）
- **CTL ≥ 1**: active、候補出力のみ

---

## 検証コマンド

Phase 2 で `sensors/computational.md` に正式移動予定。Phase 1 では以下を推奨として記録のみ:

```bash
# TypeSpec コンパイル
npx @typespec/compiler compile spec/api.tsp

# OpenAPI 生成（必要時）
npx @typespec/compiler compile spec/api.tsp --emit @typespec/openapi3
```

---

## 既存の類似単層ファイルとの関係

- `schema-evolution.md`: API の互換性ポリシー（URL バージョニング / ヘッダ / Breaking change ガード）は L0-3 のバージョニング Cat-5 と直結
- `arc-patterns/realtime-pubsub.md`: リアルタイム通信系では L0-3 に WebSocket / SSE エンドポイントが加わる

---

## L1 との連携

L1 autonomous-dev は `spec/api.tsp` を以下のように利用する:

- `tsp compile` で OpenAPI 生成 → コントローラ雛形を生成
- Model 定義は `domain.ts` の Zod スキーマと二重定義にせず、`z.infer` 型を優先
- エラーコードは enum / 定数として実装コードに import

---

## プロトコル自己評価

- TypeSpec は OSS 実証度がやや低い（2026-04 時点）。実装精度が低い場合は OpenAPI YAML 直書きに格下げ可
- 完全モードでも全エンドポイントを列挙せず、主要 3〜5 本だけでも価値を生む。「完全」=「全列挙」ではない
- 認証方式の確定は後回しにできない。Cat-2 を最優先で投げる
