# Cloudflare アダプタ（共有枠の観測）

> **この表は腐る。** 本ファイルの数値は **2026-09-11 に一次情報で観測**した値であり、
> 供給元が単独で書き換えられる。実際 **2026-09-01 に D1 の日次枠の意味が変わった**
> （超過しても通っていたものが、超過で全クエリ失敗に変わった）。
> 規範ではなく**観測記録**として扱うこと（`dh-upgrades/upgrade-spec-v6.19.0.md` I-3）。
> 判断に使う前に現在値を確認する。

## 枠（2026-09-11 観測 / Workers Free）

| 資源 | 無料枠 | 備考 |
|---|---|---|
| D1 データベース数 | **10** | 有料 $5/月 で 50,000 |
| D1 単一 DB 容量 | **500 MB** | 有料で 10 GB |
| D1 アカウント合計容量 | 5 GB | 有料で 1 TB |
| D1 日次行読込 | **500 万 / 日** | **アカウント単位で共有** |
| D1 日次行書込 | **10 万 / 日** | **アカウント単位で共有** |
| D1 Time Travel | 7 日 | 有料で 30 日。**DB 削除で復元不可になる** |
| KV 読込 | 10 万 / 日 | |
| KV 書込 | **1,000 / 日** | 無料枠で最も狭い |
| Workers リクエスト | 10 万 / 日 | 静的アセットは無制限・帯域無料 |
| R2 | 10 GB / egress 無料 | |

**最重要**: 日次枠は**アカウント単位で共有**される。DB を増やしても枠は増えない。
2026-09-01 以降、超過するとアカウントの**全 D1 クエリが失敗**する（`minna-no-ai-bbs` のような
無関係なプロジェクトも巻き込まれる）。これが本 skill の存在理由。

## 取得手順

### 1. 日次消費（GraphQL Analytics API）

`cloudflare.request()` で `/graphql` に POST する（Cloudflare MCP の `execute` から実行可能）。

```graphql
query($a:String!,$from:Date!,$to:Date!){
  viewer{ accounts(filter:{accountTag:$a}){
    d1AnalyticsAdaptiveGroups(limit:100, filter:{date_geq:$from,date_leq:$to}, orderBy:[date_DESC]){
      dimensions{ date databaseId }
      sum{ readQueries writeQueries rowsRead rowsWritten }
    }}}
}
```

variables は `{a: <accountId>, from: <YYYY-MM-DD>, to: <YYYY-MM-DD>}`。7 日分を目安に取る
（`flat_daily_writes` の検出に最低 5 日必要）。

### 2. リソース一覧（REST）

| 対象 | パス |
|---|---|
| D1 | `GET /accounts/{account_id}/d1/database?per_page=50` → `name` / `uuid` / `file_size` |
| KV | `GET /accounts/{account_id}/storage/kv/namespaces` |
| Workers | `GET /accounts/{account_id}/workers/scripts` |
| Pages | `GET /accounts/{account_id}/pages/projects` |

### 3. プラン判定

`GET /accounts/{account_id}/subscriptions` は**トークンのスコープ外になることがある**
（2026-09-11 の実測では `Authentication error`）。取れない場合は `plan` を `"unknown"` にし、
`limits` は無料枠を仮置きして**その旨を出力に残す**。過大な枠を仮定して見逃すより、
過小に見積もって誤検出するほうが安全側。

## 正規化 JSON への変換

```json
{
  "observed_at": "<ISO8601Z>",
  "provider": "cloudflare",
  "plan": "free",
  "limits": {
    "databases": 10,
    "rows_written_daily": 100000,
    "rows_read_daily": 5000000,
    "bytes_per_database": 524288000,
    "kv_writes_daily": 1000
  },
  "resources": [
    {"id": "<uuid>", "name": "<name>", "kind": "db", "size_bytes": <file_size>},
    {"id": "<id>", "name": "<title>", "kind": "kv"}
  ],
  "daily": [
    {"date": "<YYYY-MM-DD>", "resource_id": "<databaseId>",
     "rows_read": <rowsRead>, "rows_written": <rowsWritten>}
  ]
}
```

対応関係：

| 正規化キー | Cloudflare 側 |
|---|---|
| `resources[].id` / `kind: "db"` | D1 の `uuid` |
| `resources[].size_bytes` | D1 の `file_size` |
| `daily[].resource_id` | GraphQL の `dimensions.databaseId` |
| `daily[].rows_read` / `rows_written` | GraphQL の `sum.rowsRead` / `sum.rowsWritten` |

## 罠

| # | 内容 |
|---|---|
| C1 | 日次枠は**アカウント共有**。1 案件の暴走で全 D1 クエリが止まる |
| C2 | 容量はハード上限。到達すると書込が失敗する |
| C3 | **DB 間 JOIN 不可**。横断集計には別途エクスポート経路が要る |
| C4 | **Worker 外のプロセスから接続不可**。管理ツール・バッチが CF 内に閉じる |
| C5 | Time Travel は **DB が存在する間のみ**有効。削除すると 7 日以内でも復元不可 |
| C6 | `subscriptions` はトークンスコープ外になりうる（上記 3 参照） |
| C7 | **cron が空でも書込は発生しうる**。2026-09-11 の実測では cron 未設定の Worker が日次 5.4 万行を書いていた（呼び出し元が Cloudflare の外にあった）。「cron が無いから定期処理は無い」と読まないこと |

## degrade

MCP 未認証・API 到達不能・権限不足のいずれでも**エラーを返して終わる**。
DH の動作は止めない（`upgrade-spec-v6.19.0` I-5）。
「観測できなかった」を「枠に余裕がある」と読み替えてはならない。

## 出典（2026-09-11 取得）

- [D1 Pricing](https://developers.cloudflare.com/d1/platform/pricing/) / [D1 Limits](https://developers.cloudflare.com/d1/platform/limits)
- [D1 無料枠の日次制限強制化（2026-09-01）](https://developers.cloudflare.com/changelog/post/2026-09-01-d1-free-tier-limit-enforcement/)
- [Workers Pricing](https://developers.cloudflare.com/workers/platform/pricing/) / [Static Assets 課金](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations)
- [Time Travel](https://developers.cloudflare.com/d1/reference/time-travel/)
