# Supabase ローカル開発環境（推奨開発オプション、v5.18.0 追加）

本番 Supabase プロジェクト（無料枠・私的データ格納用など、**消失 NG** の実データを持つインスタンス）を汚さずに、アプリ開発・スキーマ変更・データ実験を行うための**ローカル優先（local-first）開発フロー**。本番への反映は **マイグレーションファイル経由でのみ** 明示的に行う運用を推奨する。

L0 §6「開発環境の設計・構築」で、対象プロジェクトが下記「推奨発動条件」に該当する場合に本リファレンスをロードし、推奨オプションとして人間に提示する。**強制ではなく推奨**（philosophy 第 6 条「人間最終承認」準拠）。本ファイルはツール固有のプレイブックであり、必要時のみロードされる（progressive disclosure）。

---

## 推奨発動条件（いつ L0 が薦めるか）

`subphase-selection.md` の S1（「データを保存する必要がありますか？ DB 使いますか？」）で **DB 使用あり** と判定され、かつ以下のいずれかに該当する場合に推奨提示する：

- 本番 DB に **hosted Postgres / BaaS**（特に Supabase）を使う構成
- 本番インスタンスに **消失 NG の私的データ・既存レコード** が存在する（または将来存在する）
- フロントエンドが Next.js（Vercel）等で、本番 DB を直接触りながらの開発は事故リスクが高い

### 非該当（本フローを推奨しない）

- 組込 DB（SQLite 等）でファイルごと使い捨て可能
- メモリ上のみ（ステートレス、S1 = スキップ）
- 本番インスタンスが存在しない使い捨てプロトタイプ

非該当プロジェクトでは本リファレンスをロードせず、提示もしない（時間コストゼロ）。

### 提示フォーマット（曖昧回答時）

S1 で「DB 使う、たぶん Supabase」等と曖昧に答えた場合は `ritual-protocol.md` E1 対応に従い「AI 推定 + 通知型」で薦める：

> 「本番データを汚さないため、ローカル Docker 上の Supabase で開発し、本番へは migration 経由で反映する流れを推奨します。違ったら指摘してください。」

---

## 前提確認（推奨提示時に先に確認する 1〜2 問）

ローカルスタックは Docker 上の Supabase を使うため、`dev-env-spec.md` の対話原則に沿って先に環境を確認する。技術語彙を避けた問いかけは `dialog-questions.md` S1 フォローアップを参照。

| # | 確認 | 分岐 |
|---|---|---|
| 1 | OS（Windows / macOS / Linux）| Windows は WSL2 前提で進める旨を明記 |
| 2 | Docker 導入済みか（`docker --version`）| 未導入なら Docker Desktop 導入手順を先に案内（推奨フロー保留） |

Docker が無い環境では本フローを開始できない。導入待ちの間は L0 対話を進め、Docker 準備完了後に §推奨ワークフロー へ入る。

---

## 推奨ワークフロー（ローカル優先・本番は migration 経由）

「ローカルで変更 → 本番へ push」の一方向運用を徹底する。本番を直接編集しない。

### 1. Supabase CLI インストール（OS 別）

| OS | コマンド |
|---|---|
| macOS | `brew install supabase/tap/supabase` |
| Windows | `scoop bucket add supabase https://github.com/supabase/scoop-bucket.git` → `scoop install supabase` |
| Linux | Homebrew または公式リリースバイナリ |

確認: `supabase --version`

### 2. プロジェクト初期化

プロジェクトルートで `supabase init`。生成される `supabase/` ディレクトリの構成：

- `config.toml` — ローカルスタックの設定
- `migrations/` — スキーマ変更履歴（本番反映の唯一の経路）
- `seed.sql` — ローカル初期投入データ（本番には反映されない）

### 3. ローカルスタック起動

`supabase start`。起動後に表示される以下を保存する（`.env.local` で使用）：

- API URL / DB URL / Studio URL（GUI 管理画面）
- anon key / service_role key（**ローカルスタックの固定デモキー**。本番キーとは別物）

起動失敗時のチェックポイント: Docker が起動しているか / ポート競合（54321 等）。

### 4. 本番プロジェクトとのリンクとスキーマ取得（要注意）

⚠️ ここから本番に触れる。特に慎重に進める。

```bash
supabase login                              # 認証
supabase link --project-ref <本番のproject-ref>  # 本番にリンク
supabase db pull                            # 本番スキーマをローカル migration に取り込む
```

⚠️ `db pull` は **スキーマのみ** 取得する。**本番データはコピーしない**（私的データはローカルに降りてこない＝事故源にしない）。

### 5. マイグレーション運用

| 操作 | コマンド | 説明 |
|---|---|---|
| 新規変更ファイル生成 | `supabase migration new <name>` | 生成された SQL に変更を記述 |
| ローカル適用 | `supabase db reset` | DB を初期化し migration を最初から流す（seed も再投入） |
| 差分確認 | `supabase db diff` | 未追跡のスキーマ差分を検出 |
| **本番反映** | `supabase db push` | ⚠️ 本番 DB にスキーマ変更を加える。実行前に必ず §本番反映の安全規律 |

### 6. シードデータ

`supabase/seed.sql` に開発用ダミーデータを書く。`supabase db reset` 時に自動投入される。**本番には反映されない**（seed は本番反映経路に含めない）。

### 7. Next.js 接続設定（`.env.local`）

ローカルスタックの値を `.env.local` に設定する（本番値は別途 Vercel 環境変数で管理し、リポジトリに置かない）：

```dotenv
# ローカル Supabase（supabase start の出力値）
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=<ローカル anon key>
# service_role key はサーバ専用。クライアントに露出させない
SUPABASE_SERVICE_ROLE_KEY=<ローカル service_role key>
```

---

## 生成物・配置（dev-env-spec.md 整合）

`dev-env-spec.md`「ファイル配置規則」と整合させる。

| パス | 区分 | 注記 |
|---|---|---|
| `supabase/config.toml` | ルート直下許可（設定ファイル / ツール config） | `supabase init` 生成物。`db/` 等の実装ディレクトリと同格のツール config として許可 |
| `supabase/migrations/` | 同上 | スキーマ変更履歴（本番反映の唯一経路）。コミット対象 |
| `supabase/seed.sql` | 同上 | ローカル専用。コミット対象（ダミーデータのみ） |
| `.env.local` | 設定ファイル（**`.gitignore` 必須**）| `scaffold-checklist.md` の `.gitignore` 最低要件 `.env*` で既にカバー |

### セキュリティ規律（重要）

- **本番 service_role key / 本番 DB URL を絶対にコミットしない**（`.env.local` は gitignore、本番値は Vercel 等の環境変数で管理）
- `.env.local` に書くローカルキーは `supabase start` の固定デモキーであり秘匿不要だが、本番キーとの取り違えを避けるためファイルを分離する
- 機密素材は `dev-env-spec.md`「assets/ 参照規約」に従い `.gitignore` 対象とする

---

## Smoke Test 手順（scaffold-checklist.md 整合）

`scaffold-checklist.md` の smoke test と同じ位置づけ。L0 §7.4 自己検証「scaffold smoke test」で以下を確認する：

```bash
supabase start            # Docker スタックが起動し Studio URL が到達可能
supabase db reset         # migration + seed が exit 0 で適用される
supabase db diff          # 差分なし（migration とローカルスキーマが一致）
```

通らない場合は `dev-env-spec.md` の規律に従い、失敗手順・理由・保留事由を `delivery/SELF-VERIFICATION-*.md` または `DELIVERY.md` に明記したうえで譲渡する（沈黙したまま L1 へ渡さない）。

---

## 本番反映の安全規律（schema-evolution.md 整合）

`supabase db push` は本番スキーマを変更する不可逆寄りの操作。`schema-evolution.md` のデプロイ戦略と整合させる：

- **push 前に必ず差分確認**: `supabase db diff` で本番に加わる変更をレビューし、人間承認を得る（philosophy 第 6 条）
- **expand-contract と整合**: 破壊的変更（列削除・型変更）は `schema-evolution.md` の expand-contract（expand → backfill → switch-read → contract）に分解し、1 migration に破壊を集中させない
- **後方互換性ポリシー**: 本番運用中・外部クライアント依存ありなら `schema-evolution.md` の full-compat / read-compat / breaking 判定に従う
- migration は append-only に近い扱い（適用済 migration の事後改変は本番との乖離を生む）

---

## L0 サブフェーズ・既存リファレンスとの連携

| 連携先 | 接続点 |
|---|---|
| `subphase-selection.md` | S1（DB 使用判定）が本フローの推奨発動条件の起点 |
| `subphase-l02-domain.md` | 論理モデル（`spec/domain.ts`）→ 物理モデル（migration SQL）の橋渡し。3 階層整合の物理層を Supabase migration が担う |
| `schema-evolution.md` | 本番反映時の互換性ポリシー・デプロイ戦略。`db push` の安全規律 |
| `scaffold-checklist.md` | バックエンド開発オプションとして smoke test / 生成物を整合 |
| `dialog-questions.md` | S1 フォローアップで非技術語彙の推奨提示 |

---

## 検証センサーへの連携

`sensors/computational.md` に以下を含めることを推奨（プロジェクト方針による）：

- `supabase db diff --schema public` が差分ゼロ（migration とスキーマの一致）を CI で検査
- migration の本番ドライラン（ステージング project への適用テスト、`schema-evolution.md`「検証センサーへの連携」と同型）

`sensors/inferential.md` に以下：

- 進行中の破壊的変更が expand-contract のどの段階にあるか
- `db push` 前のレビューで本番データへの影響が評価されたか

---

## モード別の扱い

| モード | 扱い |
|---|---|
| M1 単体 | 推奨はするが過剰にならない範囲。ローカルスタック + migration 運用は M1 でも本番保護に有効 |
| M2 標準 | 標準的に推奨。smoke test を §7.4 自己検証に組込 |
| L2 | 複数ドメインで共有する場合は migration の所有境界を `DOMAINS.md` と整合させる |
| dev_mode = autonomous | `db push` は不可逆寄り操作のため、autonomous_scope = full でも本番反映は人間承認チャネル（philosophy 第 7 条 P3/P4）を経由することを推奨 |

LC ≥ 1 既存プロジェクトでは、新規開始する DB 機能から段階適用する（既存の本番直結フローの遡及置換は要求しない。事後追加プロトコルで任意導入可）。

---

## プロトコル自己評価

体制事後評価で以下を蓄積する：

- 推奨発動条件が過剰提示（SQLite / メモリのみのプロジェクトにまで提示）になっていないか
- `db pull` がスキーマのみで本番データを降ろしていないことを実運用で守れているか
- `db push` 前の差分確認・人間承認が省略されていないか（本番事故の最大リスク源）
- `.env.local` / 本番キーの分離が守られ、本番 service_role key の混入コミットが発生していないか
- Docker 未導入環境での導入案内が L0 対話の妨げになっていないか（保留運用が機能しているか）
