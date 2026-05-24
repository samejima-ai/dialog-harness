# L0-2: ドメインモデル対話プロトコル

Zod + TypeScript による型安全なドメインモデル生成のための対話プロトコル。
`spec/domain.ts` を成果物として生成する。

---

## 原則

- Zod でランタイム検証と TypeScript 型定義を同時に得る
- 値オブジェクトを brand 型で区別する（`UserId` と `TodoId` が混ざらない）
- 不正状態を型で表現不可にする（sum type / enum の活用）
- nullable は `z.nullable()` で明示（Option 型相当）
- 集約上限値は定数として明示する（実装で検証、型では表現しない）
- 共通プロトコルは `subphase-common-protocol.md` を参照

---

## 起動条件

`subphase-selection.md` の起動判定表より:

| 条件 | モード |
|---|---|
| DB 使用あり | 完全モード |
| メモリ上のみだが複雑なデータ構造あり | 簡易モード |
| データ永続化なし（ステートレス） | スキップ |

---

## モード定義

### 完全モード
- 値オブジェクト（brand 型）
- エンティティ（Zod object）
- 集約上限値（定数）
- sum type による状態表現
- nullable の明示

### 簡易モード
- フラットな型定義のみ
- 値オブジェクト・集約の概念は省略
- `z.object()` + 基本型のみ

### スキップ
- `domain.ts` を生成しない
- 後続サブフェーズ（L0-3 等）での型参照を無効化

---

## 対話カテゴリ

各カテゴリで 1〜3 問を投げる。共通プロトコルの「1 回のターンで 5 問を超えない」原則を守る。

### Cat-1: エンティティ識別

- 主要なエンティティ（データの塊）は何ですか？
- それぞれにはどんな情報が含まれていますか？
- エンティティ同士の関係は？（1:N、N:N 等）

### Cat-2: 値オブジェクト

- ID やメールアドレスなど、他の文字列と混ざってほしくない型は？
- 金額・日付・座標など、生の数値や文字列で扱いたくないものは？

### Cat-3: nullable（Option 型）

- 「あってもなくてもよい」フィールドは？
- 初期状態では未設定で、後から埋まるフィールドは？

### Cat-4: 集約制約

- 1 ユーザー / 1 組織あたりの上限値は？（「TODO は 100 件まで」等）
- 文字列長・配列要素数の上限は？
- 最小値・必須項目は？

### Cat-5: 状態表現

- 複数の状態を取るエンティティは？
- その状態は互いに排他的ですか？（一つしか取らない）

---

## 生成物フォーマット

### ファイル配置
`spec/domain.ts`

### 冒頭コメント規約

```typescript
// L0-2: Domain Model (Zod + TypeScript)
// モード: 完全 | 簡易
// 生成日: YYYY-MM-DD
// AI 生成、人間はレビューのみ
```

### 主要セクション構造

```
1. import（Zod）
2. 値オブジェクト（brand 型）
3. エンティティ（Zod object）
4. sum type（enum）
5. 集約制約（定数）
6. 型エクスポート（z.infer）
```

---

## TodoApp 実例（完全モード）

以下は `spec/domain.ts` の完全な例。

```typescript
// L0-2: Domain Model (Zod + TypeScript)
// AIが生成、人間はレビューのみ

import { z } from "zod";

// ===== 値オブジェクト =====
export const UserId = z.string().uuid().brand<"UserId">();
export const TodoId = z.string().uuid().brand<"TodoId">();
export const Email = z.string().email();

// ===== エンティティ =====
export const User = z.object({
  id: UserId,
  email: Email,
  createdAt: z.date(),
});

// TODOの状態（sum type = 不正状態を表現不可にする）
export const TodoStatus = z.enum(["pending", "completed", "expired"]);

export const Todo = z.object({
  id: TodoId,
  ownerId: UserId,              // 不変条件: 所有者のみ操作可（L0-5で強制）
  title: z.string().min(1).max(100),
  body: z.string().max(1000).default(""),
  status: TodoStatus,
  dueDate: z.date().nullable(),  // nullable = Option型相当
  createdAt: z.date(),
  updatedAt: z.date(),
});

// ===== 集約制約 =====
// 1ユーザーあたりのTODO数 <= 100（SPEC条件）
// → 実装時にチェック、ここでは意図のみ記述
export const USER_TODO_LIMIT = 100;

export type User = z.infer<typeof User>;
export type Todo = z.infer<typeof Todo>;
export type TodoStatus = z.infer<typeof TodoStatus>;
```

---

## 簡易モード成果物例

```typescript
// L0-2: Domain Model (Simple Mode)
// モード: 簡易
// 生成日: YYYY-MM-DD

import { z } from "zod";

export const Todo = z.object({
  id: z.string(),
  title: z.string(),
  status: z.enum(["pending", "completed", "expired"]),
  dueDate: z.date().nullable(),
});

export type Todo = z.infer<typeof Todo>;
```

値オブジェクト・集約上限・所有権の概念を省略。

---

## 前サブフェーズからの入力

- **L0-1 `SPEC.md`**: WHAT 節から名詞（エンティティ候補）、条件節から上限値・バリデーション、制約節からドメイン特性を抽出

---

## 後続サブフェーズへの出力

以下の要素が後続で参照される（`subphase-common-protocol.md` の I/O 契約表と整合）:

- **型名**: `User`, `Todo` 等 → L0-3 の Model、L0-5 の type 定義で参照
- **enum 値**: `TodoStatus` の ["pending", "completed", "expired"] → L0-4 の状態名、L0-6 の Given 節
- **集約上限**: `USER_TODO_LIMIT` → L0-3 のエラーコード、L0-6 の制約 Scenario
- **brand 型**: `UserId`, `TodoId` → L0-5 の認可対象

---

## 検証フェーズ（Phase γ）

生成後、以下をクロスチェック:

| 観点 | チェック方法 |
|---|---|
| SPEC.md 名詞の網羅 | SPEC.md WHAT 節の名詞が `domain.ts` のエンティティ/値オブジェクトに存在 |
| 命名一貫性 | エンティティ名・フィールド名が SPEC.md の表記と一致（翻訳語彙のブレなし） |
| 集約上限の整合 | SPEC.md の「条件」節の数値が `USER_TODO_LIMIT` 等の定数に反映 |
| nullable の妥当性 | SPEC.md で「任意」と書かれたフィールドが `.nullable()` または `.default()` |
| **機能間相互作用の記述** | **永続化機能の場合、SPEC.md の「機能間相互作用」セクションで共有レイヤ一覧・副作用マトリクス・同時刻整合性ルールが記述済み** |

**機能間相互作用チェック詳細**:
- 永続化レイヤへの書き込みを行う機能では必須チェック
- 共有キーが 2 つ以上ある場合は副作用マトリクス記述を確認
- ステートレスな表示系・計算系のみは省略可

不整合検出時は Phase α に戻り、該当 Cat の追加質問を投げる。

---

## 検証コマンド

Phase 2 で `sensors/computational.md` に正式移動予定。Phase 1 では以下のコマンドを推奨として記録のみ:

```bash
# 型チェック
npx tsc --noEmit spec/domain.ts

# Zod スキーマの整合性（簡易 smoke test）
node -e "const {Todo} = require('./spec/domain.ts'); console.log(Todo.safeParse({}).error)"
```

---

## 既存の類似単層ファイルとの関係

- `schema-evolution.md`: データモデル進化プロトコル（互換性ポリシー）。L0-2 の生成後、`SPEC.md` のデータモデル進化セクションと整合する必要がある。
- `domain-context-dialog.md`: 業界・業務固有の前提。L0-2 の値オブジェクト（Email の形式制約等）を引き出す際に参照する。

---

## L1 との連携

L1 autonomous-dev は `spec/domain.ts` を以下のように利用する:

- そのまま `import { Todo, User } from "./spec/domain"` 可能
- Zod スキーマによるランタイム検証を API 入力バリデーションで利用
- `z.infer` で得た型を関数シグネチャで利用

---

## 業界叡智参照: 概念モデリング 3 階層 + DDD（v5.17.0 追加）

教科書的データモデリング知識を Phase α 対話と Phase γ 検証に補助情報として組み込む。AI が背景で参照し、必要時に Cat-1 の追加質問として顕在化させる。

### 概念 → 論理 → 物理の 3 階層

| 階層 | DH 上の所在 | 担当 |
|---|---|---|
| 概念モデル | `SPEC.md` WHAT 節（名詞群と関係性の自然言語表現） | L0 対話 |
| 論理モデル | `spec/domain.ts`（Zod スキーマ + brand 型 + 集約制約） | L0-2 |
| 物理モデル | DB マイグレーション / インデックス / パーティション定義 | L1 + `schema-evolution.md` |

3 階層が一直線で繋がる状態を維持する。論理層の `domain.ts` が物理層に渡る際、`schema-evolution.md` 「適用対象」判定でスキーマ進化プロトコル準拠が必要か判定する。物理層が hosted Postgres / Supabase の場合、本番を汚さないローカル優先の開発・migration 運用を推奨する（`supabase-local-dev.md` 参照、v5.18.0 追加）。

### DDD と境界づけられたコンテキスト

**判断基準**: L0-2 Phase β で生成する `domain.ts` が単一巨大モデルに膨れる場合（エンティティ数 ≥ 15 or 機能ドメイン ≥ 3）、機能境界で分割を検討する（L1 は L0-2 の成果物を消費する側であり、境界分割の意思決定は L0-2 内で完結する）。

- 分割の単位例: `販売` / `サポート` / `課金` 等のビジネス機能
- 分割形式: `spec/domain/<context>.ts` 配下に複数ファイル化（L0-6 invariants は境界をまたぐ条件のみ記述する）
- 境界をまたぐ参照は ID（brand 型）経由のみ。直接エンティティ参照は禁止
- L2 発動閾値（domains ≥ 5）に近づいたら L2 判定の根拠データとして利用する

### ER モデルとカーディナリティの明示

Cat-1 「エンティティ同士の関係は？」の応答を **1:1 / 1:N / N:N** の 3 値で記録する。多対多（N:N）は中間テーブル（join entity）を `domain.ts` に明示する：

```typescript
// N:N の例: User と Project の関係（中間エンティティ ProjectMember）
export const ProjectMember = z.object({
  userId: UserId,
  projectId: ProjectId,
  role: z.enum(["owner", "member", "viewer"]),
  joinedAt: z.date(),
});
```

中間テーブルに関係固有の属性（`role` / `joinedAt`）が乗る場合、それは独立エンティティに昇格する設計シグナル。

### 検証フェーズ追補

Phase γ クロスチェック表に以下を追加：

| 観点 | チェック方法 |
|---|---|
| 3 階層整合 | `SPEC.md` WHAT 節の名詞 ≡ `domain.ts` エンティティ ≡（該当時）schema-evolution.md の進化対象 |
| カーディナリティ明示 | 関係性が 1:1 / 1:N / N:N のいずれかで `domain.ts` 上に表現済み（N:N は中間 entity 化） |
| 境界分割の閾値 | エンティティ数 ≥ 15 or 機能ドメイン ≥ 3 で境界分割案を Phase δ 差分サマリに含める |

---

## プロトコル自己評価

- Cat-1〜5 で 5 問の質問を用意しているが、実際は 2〜3 問で決まるケースが多い。冗長な質問を避ける
- 値オブジェクト（brand 型）の概念は非エンジニアに伝わりにくい。「混ざってほしくない型」という表現で補う
- 簡易モードは「あとで完全モードに昇格可能」と明示する（事後追加プロトコル参照）
- 3 階層モデルは「概念 → 論理 → 物理」の対応関係が頭の中で繋がっていない人間が多い。AI が階層図を Phase α 冒頭に提示すると効果的
