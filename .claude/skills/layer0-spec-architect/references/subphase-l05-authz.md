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

## 業界叡智参照モード（Phase γ-i 連携、CTL ≥ 1、W5-Q2 採決追加）

Wave 5 W5-Q2 採決 (`council-2026-05-11T12:15:00Z-w5qb02`、B 段階組込、conf 0.72) で確定した subphase 個別の業界叡智参照モード。`subphase-common-protocol.md` Phase γ-i フック起動時に L0-5 (認可) は以下の業界叡智ソースを参照する。**観測駆動、候補出力のみ、自動採用なし**（philosophy 第 8 条 3 段階モデル準拠）。

### 参照ソース

| ソース | 配置 | 主な参照観点 |
|---|---|---|
| AgentShield 脆弱性パターン | `history/refs-draft/ecc/agentshield-spec.md` | 102 ルール × 5 カテゴリ (Secrets / Permission / Injection / Hook risk / Configuration) |
| AgentShield 参照導入規約 | `templates/rules/common/agentshield-reference.md` | 利用者プロジェクト側の警告参照規約（Wave 2 PR #78 で追加）|

### 照合観点（Phase γ-i フックが Phase γ 検証時に追加）

認可モデル設計が以下の業界慣例と整合しているかを照合：

| # | 観点 | 業界叡智ソース | match_type |
|---|---|---|---|
| 1 | 認可 relation の組み合わせに Permission auditing で警告される危険組合 (例: 全 user に can_write 付与) がないか | AgentShield §3 Permission auditing | contradictory 検知用 |
| 2 | リソース上の所有者 (owner) 関係に Secrets detection で警告される直書きパターンがないか | AgentShield §3 Secrets detection | contradictory 検知用 |
| 3 | 認可マトリクスの管理者特権定義が Configuration weaknesses (insecure defaults) に該当しないか | AgentShield §3 Configuration weaknesses | redundant 検知用 |
| 4 | 認可拒否時のエラー応答が Injection analysis (path traversal 等) の脆弱性入口を提供しないか | AgentShield §3 Injection analysis | complementary |

### 候補リスト出力例

```yaml
industry_wisdom_match_candidates:
  - source: "AgentShield §3 Permission auditing"
    aspect: "dangerous tool combinations (Bash + Write 同時許可相当)"
    spec_draft_reference: "authz.fga §type todo / define can_write"
    match_type: "contradictory"
    suggestion: "guest ロールに can_write を付与すると AgentShield Permission auditing 相当の警告対象、設計再考候補"
    confidence: 0.75
```

### 第 8 条 3 段階モデル準拠

- **観測**: `authz.fga` / `authz-matrix.md` ドラフトと `agentshield-spec.md` の照合
- **候補化**: `industry_wisdom_match_candidates` リストとして Phase δ 差分サマリに含める
- **人間最終承認**: Phase δ でユーザー承認（自動採用なし、philosophy 第 6 条準拠）

### CTL 連動

- **CTL 0**: 本セクション inactive（観察温存、候補化も抑止）
- **CTL ≥ 1**: active、候補出力のみ

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

## マルチテナンシー隔離戦略（v5.17.0 追加）

複数組織・複数顧客が同一システムを利用する形態（B2B SaaS / 社内マルチ部門システム等）で、データの論理的・物理的隔離をどの粒度で行うかを決定する判断軸。L0-5 の認可モデルと表裏一体で設計する。

### Cat-6: マルチテナンシー（新規追加）

L0-5 起動時に以下を確認する：

- 複数組織（テナント）が同じシステムを使うか？
- テナント間でデータが**絶対に**混ざってはいけない要件はあるか？（規制 / 契約上の要請）
- テナントごとに DB スキーマや設定が異なる可能性はあるか？

### 3 つの隔離戦略

| 戦略 | データ配置 | 認可表現（OpenFGA） | 適用場面 |
|---|---|---|---|
| **共有スキーマ + tenant_id 列** | 全テナントが同一テーブル、行レベルで `tenant_id` 区別 | `type organization` を中間 type 化、`define member: [user]` + `define can_read: member from organization` | テナント数多、コスト最優先、規制緩 |
| **スキーマ分離（schema-per-tenant）** | PostgreSQL schema 単位で分離、アプリ層で search_path 切替 | 認可は共有スキーマと同型だが、DB connection 層で物理境界を併設 | 中規模、規制やや厳、テナント別カスタマイズ可能性 |
| **DB 分離（database-per-tenant）** | テナントごとに独立 DB（コンテナ・インスタンス分離も可） | OpenFGA store も別建てが推奨 | 厳格な規制（医療 HIPAA / 金融 PCI DSS）、テナント別 SLA、テナント数少 |

### 判定フロー

```
1. テナント数 N の見込みは？
   N ≥ 100  → 共有スキーマ + tenant_id（コスト効率優先）
   N < 100  → 2 へ
2. 規制要件（HIPAA / PCI DSS / 業界規制）でテナント間データ物理分離が必須か？
   YES → DB 分離
   NO  → 3 へ
3. テナント別カスタムスキーマ / 別バージョン稼働の要件は？
   YES → スキーマ分離（または DB 分離）
   NO  → 共有スキーマ + tenant_id
```

### 各戦略の TodoApp 拡張例

#### 共有スキーマ + tenant_id

```typescript
// domain.ts: 全エンティティに tenant_id 必須化
export const Todo = z.object({
  id: TodoId,
  tenantId: OrganizationId,  // 全行に tenant_id（NULL 不可）
  ownerId: UserId,
  // ...
});
```

```
# authz.fga
type organization
  relations
    define member: [user]
    define admin: [user]

type todo
  relations
    define tenant: [organization]
    define owner: [user]
    define can_read: owner or admin from tenant
```

#### DB 分離

各テナントに独立 DB を割り当て、テナント内のリソース認可は `spec/authz.fga` で従来通り表現する（owner / role / 共有関係等）。**ただし** 「どのユーザーがどのテナント DB に接続できるか」（user → tenant のメンバーシップ認可）は DB 分離だけでは保証されない点に注意：

- DB 分離は **テナント選択後** のクロステナント読みを物理的に防ぐ（cross-tenant read-after-select）
- **テナント選択自体の認可**（routing authorization）は別途必要。以下のいずれかで明示する：
  - `spec/authz.fga` 内に `type tenant` + `define member: [user]` / `define admin: [user]` を保持し、connection routing 層が check に基づいて DB 接続を切替
  - 認可マトリクス `spec/authz-matrix.md` の routing セクションに user→tenant の許可表を記述
  - いずれを採用するかは `SPEC.md` マルチテナンシーセクションで明示

`SPEC.md` の「マルチテナンシー」セクション記述例：

```markdown
## マルチテナンシー
- 戦略: DB 分離（database-per-tenant）
- 理由: HIPAA 準拠の物理分離要求
- ルーティング: subdomain → tenant_id → DB connection string mapping
- ルーティング認可: spec/authz.fga の `type tenant` + `define member` を check してから DB 接続切替
- スキーマ進化: 全テナント DB に対する zero-downtime migration が要件
```

### NFR / 規制との連動

- NFR S (Security) ≥ 2 + 複数テナント → スキーマ分離以上を推奨
- NFR C (Compliance) ≥ 2 + 規制業界 → DB 分離を強く推奨
- DOMAIN-CONTEXT.md の業界文脈と必ず突き合わせる（医療 / 金融 / 公共は規制要件が厳格）

### 検証フェーズ追補

Phase γ クロスチェック表に以下を追加：

| 観点 | チェック方法 |
|---|---|
| テナント分離戦略の明示 | SPEC.md または authz.fga 内で 3 戦略のいずれかが選択済み |
| 認可と隔離戦略の整合 | DB 分離選択時に user→tenant の routing 認可（`type tenant` + `define member` または routing 認可マトリクス）が明示されている、共有スキーマ時に全エンティティに `tenant_id` が定義済み |
| 規制業界での整合 | DOMAIN-CONTEXT.md に規制記述があれば、戦略選択が NFR C スコアと矛盾しない |

---

## プロトコル自己評価

- OpenFGA はランタイム依存が重い（サーバー必須）。小規模プロジェクトでは簡易モードで十分
- 「所有者のみ」ルールは頻出なので、テンプレ化して対話を短縮可能
- 管理者特権（admin type）は権限拡散のリスクがある。追加時は Cat-4 で必ず確認する
- マルチテナンシー戦略の誤選択は事後修正が極めて困難（DB 分離 ↔ 共有スキーマ間の移行は実質的な再構築）。Cat-6 を軽視しない
