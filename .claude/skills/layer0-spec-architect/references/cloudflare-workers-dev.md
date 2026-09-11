# Cloudflare Workers 開発環境（v6.19.0 F3 追加）

> **この節に供給元の数値表は置かない。** 無料枠・料金・保持期間は**他者が単独で書き換えられる値**であり、
> 規範ではなく観測記録として扱う（`dh-upgrades/upgrade-spec-v6.19.0.md` I-3）。
> **この表は腐る**のではなく、腐る表をここに作らない。
>
> 数値の正本は **1 箇所だけ**ある: `.claude/skills/crosscut-quota-observer/references/adapters/cloudflare.md`
> （2026-09-11 観測 / 観測日付つき）。判断に使う前に現在値を確認すること。
>
> **実際に意味が変わった実例**: 2026-09-01、D1 無料枠の日次行読／行書の上限が「超過しても通る」から
> **「超過するとアカウントの全 D1 クエリが失敗する」**に変わった。変わったのは数値ではなく**数値の意味**である。
> 数値だけを写して持つと、この種の変化は検出できない。

Workers + D1 / R2 / KV を使う案件で、本番を汚さずにローカルで開発・スキーマ変更・データ実験を行うための
**ローカル優先（local-first）開発フロー**。本番反映はマイグレーション経由でのみ明示的に行う。

`supabase-local-dev.md` の兄弟。L0 §6「開発環境の設計・構築」で該当時のみロードする（progressive disclosure）。
**強制ではなく推奨**（philosophy 第 6 条「人間最終承認」準拠）。

---

## 適用範囲

**本フローは Cloudflare Workers を実行基盤に選んだ案件に適用する。** 供給元の選択そのものは本ファイルの
責務ではない（選択は L0 対話で人間が行う）。

- **Cloudflare 無しでも DH は完全動作する**（同 I-5）。本ファイルの不在・未ロードは機能停止ではない
- 本ファイルが扱うのは**開発フローと構造的制約**であって、供給元の優劣ではない。
  中身の大半（本番を直接編集しない / migration 一方向 / ローカルで同一ランタイムを回す）は
  **供給元非依存の叡智**で、他の edge ランタイムにも通用する

---

## 推奨発動条件（いつ L0 が薦めるか）

`subphase-selection.md` の S1（DB 使用の有無）と併せて、以下のいずれかに該当する場合に提示する：

- 実行基盤に Cloudflare Workers / Pages を使う
- データ層に D1（SQLite 互換）/ KV / R2 を使う
- 静的サイト + 軽い API という形（後述 §課金境界 の利得が大きい形）

### 非該当（提示しない）

- ローカル完結 / 組込 DB のみ / 使い捨てプロトタイプ
- **PG 固有機能に依存する設計**（→ 罠 C5。D1 では成立しない。`Hyperdrive` + 外部 PG か別供給元を検討する。
  出し分けの機械判定は同 spec F5）
- CPU 重い処理・ネイティブ依存（→ 罠 C8）

---

## 前提確認（推奨提示時に先に確認する 1〜2 問）

| # | 確認 | 目的 |
|---|---|---|
| 1 | Node.js が入っているか（`node --version`） | `wrangler` は npm 配布。未導入なら導入案内が先 |
| 2 | Cloudflare アカウントがあるか / 既存プロジェクトが同一アカウントにあるか | **枠はアカウント単位で共有**される（罠 C1）。既存があるなら §枠の確認 を先に回す |

Docker は不要（`supabase-local-dev.md` との最大の運用差）。ローカル実行は `workerd` + Miniflare で完結する。

---

## ローカル開発フロー

### 1. 導入と雛形

```bash
npm create cloudflare@latest   # 雛形生成（wrangler を devDependency に入れる）
npx wrangler --version         # v3.0 以上であること
```

`wrangler` はグローバル導入せず **プロジェクトローカル**に置く（版差で挙動が変わるため。`npx` 経由で呼ぶ）。

### 2. ローカル実行はデフォルト

```bash
npx wrangler dev               # v3.0+ ではローカルモードが既定（Miniflare + workerd）
npx wrangler dev --remote      # 明示したときだけリモート
```

**ローカルは本番と同じランタイム（`workerd`）で動く。** ここが「本番でしか再現しない」を減らす主因であり、
`runtime_profile` を `local-reproducible` と仮置きした根拠でもある（同 spec D-4 で実測確定予定）。

### 3. D1 のローカル運用

```bash
npx wrangler d1 execute <DB名> --local --command "SELECT 1"
npx wrangler d1 migrations create <DB名> <説明>
npx wrangler d1 migrations apply <DB名> --local    # ローカル
npx wrangler d1 migrations apply <DB名> --remote   # 本番（§本番反映の安全規律 を先に読む）
```

- **`--local` / `--remote` を常に明示する。** 付け忘れの既定はサブコマンドごとに異なり、
  `d1 execute` を素で打つと**本番に当たる**。CI・スクリプトでは必ず書く
- ローカル DB の実体は `.wrangler/state` 配下の SQLite ファイル。**`.gitignore` に入れる**
- **データは既定で実行間に永続する**（wrangler v3+）。空の DB を前提にするテストは
  `DROP TABLE` から始めるか `--persist-to` で場所を分ける
- Pages プロジェクトでローカル D1 を使うには `preview_database_id` の設定が要る。
  なお **Pages からリモート D1 に対して開発することはできない**
- ORM がマイグレーションをサブディレクトリに書く場合（Drizzle 等）は `migrations_pattern` を設定する。
  `wrangler d1 migrations create` は top-level にしか書かないため、生成は ORM 側のコマンドで行う
- 外部キー制約に触る migration では `PRAGMA defer_foreign_keys = true` を先に呼ぶ

### 4. 設定ファイル

`wrangler.jsonc`（または `.toml`）に binding を宣言する。**`database_id` は秘匿情報ではない**が、
API トークンは別（→ §セキュリティ規律）。

`compatibility_date` は**明示して固定する**。`nodejs_compat` は 2026-08-04 以降の
compatibility date で既定 ON になったため、新規案件でフラグを足す必要はない（罠 C8）。

---

## 枠の確認（数値はここに持たない）

```bash
# 観測 skill がある場合（推奨）
#   .claude/skills/crosscut-quota-observer/ の手順で現在値を取得する
python3 .claude/skills/crosscut-quota-observer/scripts/quota-observer.py --input observation.json
```

- 観測 skill が**無い**場合は §出典 の一次情報を直接見る（degrade。同 I-5）
- **「枠が見えない」を「枠が空いている」と読み替えない。** 観測不能はそのまま観測不能として扱う
- 新規に DB を作る前、および量産フェーズでは**先に残量を見る**。
  枠はアカウント共有のため、**無関係な既存プロジェクトを巻き込んで止める**（罠 C1）

---

## 設計上の罠カタログ

**規範ではなく構造の記録**。数値は現在値を §枠の確認 で取ること。
罠は**実害からのみ増やす**（推測で増やさない）。

| # | 罠 | 設計への影響 |
|---|---|---|
| C1 | **日次の行読／行書はアカウント単位で共有**。DB を増やしても枠は増えない | 1 案件の暴走で**同一アカウントの全 D1 クエリが停止**する。2026-09-11 に単一プロジェクトが日次書込枠の 53% を消費した実測がある。量産するなら観測が前提 |
| C2 | 単一 DB の容量は**ハード上限** | 到達すると書込が失敗する。ログ・履歴系を無制限に貯める設計を置かない |
| C3 | **DB 間 JOIN 不可** | 「1 ツール = 1 DB」で分けると横断集計ができない。必要ならエクスポート経路を別に設計する |
| C4 | **Worker 外のプロセスから接続不可** | 管理ツール・バッチ・BI が Cloudflare 内に閉じる。`psql` 相当の直結を前提にした運用は組めない |
| C5 | **PG 固有機能を持ち込めない**（`jsonb` 演算子 / PL-pgSQL / PostGIS / `LISTEN`-`NOTIFY`） | D1 は SQLite 互換。PG 前提のスキーマは**移植ではなく再設計**になる。該当するなら Hyperdrive + 外部 PG（同 spec F5 の分岐表） |
| C6 | 書込スループットに天井がある | **具体値は未検証**（同 spec の「~50 tps」は一次情報で確認できていない）。高頻度書込を設計に置くなら**実測してから決める**。数値を引用しないこと |
| C7 | **Time Travel は DB が存在する間のみ**有効 | DB を削除すると保持期間内でも復元できない。削除は不可逆操作として扱う（人間承認） |
| C8 | CPU 重い処理・ネイティブ依存は不向き | `nodejs_compat` が既定 ON でも Node の全部が動くわけではない。画像処理・暗号の重い処理は別手段 |
| C9 | **Workers Cache を有効にすると、通常無料のリクエストも課金対象になる** | 静的アセットへのリクエストと Worker 間呼び出しは通常無料だが、キャッシュ有効時は標準レートで課金される。「速くするために入れたら課金が増えた」が起きる |
| C10 | **cron が空でも書込は発生しうる** | 呼び出し元が Cloudflare の外にあると設定画面からは見えない。2026-09-11 の実測では cron 未設定の Worker が日次 5.4 万行を書いていた。「cron が無いから定期処理は無い」と読まない |
| C11 | D1 は基盤側の更新で再起動しうる（`D1 DB reset because its code was updated.`） | **リトライ可能な一過性エラーが正常系に存在する**。1 回の失敗で落ちる書き方をしない |

---

## 静的アセットと Workers の課金境界

**Functions / Worker を呼ばないリクエストは無料・無制限。** 逆に言えば：

- **SSR や middleware が全ルートに乗る構成は、静的サイトの見た目をした Workers 課金**になる。
  「Pages だから安い」のではなく「Worker を呼ばないから安い」
- 無料枠の日次リクエスト数は **Pages Functions と Workers で同一の枠を食い合う**
- したがって設計判断は「静的に出せるものを静的に出す」。
  これは性能最適化ではなく**枠の設計**であり、C1 と同じ理由で他プロジェクトに波及する

---

## 生成物・配置（`dev-env-spec.md` 整合）

| 生成物 | 配置 | 備考 |
|---|---|---|
| `wrangler.jsonc` | リポジトリ直下 | binding 宣言・`compatibility_date` 固定 |
| `migrations/` | リポジトリ直下 | `wrangler d1 migrations create` の出力。**コミットする** |
| `.wrangler/` | リポジトリ直下 | ローカル state（SQLite 実体）。**`.gitignore` に入れる** |
| `.dev.vars` | リポジトリ直下 | ローカル用シークレット。**`.gitignore` に入れる** |

---

## Smoke Test 手順（`scaffold-checklist.md` 整合）

§7.4 自己検証に以下を含める。**すべて認証なしでローカル完結**すること（1 分以内制約）。

```bash
npx wrangler d1 migrations apply <DB名> --local            # exit 0
npx wrangler d1 execute <DB名> --local --command "SELECT 1" # exit 0
npx wrangler dev &                                          # Ready on http://127.0.0.1:8787 到達
```

認証やネットワークを要する検査は smoke に入れない（`local-reproducible` を壊すため）。

---

## 本番反映の安全規律（`schema-evolution.md` 整合）

- **`--remote` を伴う操作は不可逆寄り**として扱う。`dev_mode = autonomous` / `autonomous_scope = full` でも
  人間承認チャネル（philosophy 第 7 条 P3/P4）を経由する
- 反映順序は **ローカルで apply → smoke 通過 → 本番 apply**。逆順を作らない
- **DB の削除は Time Travel を無効化する**（罠 C7）。削除は承認必須
- 本番 apply の前に §枠の確認 を通す。枠が埋まっている状態での apply は、
  **無関係なプロジェクトを巻き込んだ失敗**になりうる

---

## セキュリティ規律

- **API トークンをリポジトリに置かない。** `wrangler secret put` / `.dev.vars`（gitignore 済み）を使う
- トークンのスコープは最小にする。ただし**スコープを絞ると観測が落ちる**ことがある
  （`subscriptions` が読めず plan 判定が `unknown` になる実測がある）。**落ちたことが見える**状態を保つ
- `.wrangler/state` には実データが入りうる。gitignore の確認を scaffold 時に行う

---

## モード別の扱い

| モード | 扱い |
|---|---|
| M1 単体 | 推奨はするが過剰にならない範囲。ローカル実行 + migration 運用は M1 でも本番保護に有効 |
| M2 標準 | 標準的に推奨。smoke test を §7.4 自己検証に組込 |
| L2 | 複数ドメインで DB を分ける場合、**罠 C3（DB 間 JOIN 不可）が境界設計を拘束する**。`DOMAINS.md` と整合させる |
| dev_mode = autonomous | `--remote` 系は人間承認チャネル経由 |

LC ≥ 1 の既存プロジェクトでは、新規開始する機能から段階適用する（既存フローの遡及置換は要求しない）。

---

## 規範メタデータ

```yaml
stage: S0-S2
review_trigger:
  - dated: 2026-12-11（観測から 3 ヶ月）に一次情報の再確認。
      本ファイルは数値を持たないため再観測の対象は観測記録側（adapters/cloudflare.md）だが、
      「数値を持たない構成が実際に腐敗を防げたか」をここで測る
  - measured: 罠カタログに載っていない事故が起きたら追記（罠は実害からのみ増やす）
```

## プロトコル自己評価

体制事後評価で以下を蓄積する：

- 推奨発動条件が過剰提示（ローカル完結プロジェクトにまで提示）になっていないか
- **数値を持たない構成が機能したか** — 利用者が「枠はいくつか」を知るために §枠の確認 を回したか、
  それとも一次情報を見ずに記憶で答えたか。後者が起きるなら分離の設計が間違っている
- `--local` / `--remote` の明示が守られ、本番への誤爆が発生していないか
- 罠カタログが**実害からのみ**増えているか（推測で増やしていないか）
- 静的／動的の境界が設計判断として機能したか（Worker を呼ばない経路を実際に確保できたか）

---

## 出典（2026-09-11 取得）

- [D1 Local development](https://developers.cloudflare.com/d1/best-practices/local-development/) / [Migrations](https://developers.cloudflare.com/d1/reference/migrations/) / [Debug D1（エラー一覧）](https://developers.cloudflare.com/d1/observability/debug-d1/)
- [D1 無料枠の日次制限強制化（2026-09-01）](https://developers.cloudflare.com/changelog/post/2026-09-01-d1-free-tier-limit-enforcement/)
- [Workers Pricing](https://developers.cloudflare.com/workers/platform/pricing/) / [Workers Cache（課金）](https://developers.cloudflare.com/workers/cache/) / [Pages Functions Pricing](https://developers.cloudflare.com/pages/functions/pricing/)
- [Compatibility flags（nodejs_compat）](https://developers.cloudflare.com/workers/configuration/compatibility-flags/)
