# upgrade-spec v6.19.0 — 供給元の既定を Stack 層で持つ（Cloudflare 吸収 + 共有枠の観測）

> **状態: 実装中（F1 済 = PR #278、F2〜F5 未着手）**。Council 諮問通過（`council-2026-09-11T03:07:42Z-dt0911` /
> implementer_consent: agreed / 2026-09-11 人間判定）。spec 起草は PR #277、F1 の実装は PR #278。
> F2〜F5 は後続（実装順序は I-4 に従い F2 → F3 → F4/F5）。
>
> **起点**: 利用者発話（2026-09-11、L0 ブレスト）「cloudフレア MCP を繋げたのでデプロイ先を選べる
> ようにしたい。Supabase の無料枠は使い切っているので、サーバーも含めて cloudフレアをデフォルトに
> したい」（引用中の「cloudフレア」は **Cloudflare**。発話の原文表記を保存し、以降の本文では
> 固有名詞として `Cloudflare` に統一する）。判断材料は
> `delivery/DECISION-KIT-deploy-target-2026-09-11.html`（PR #276）。
>
> **Council 判定**: recommended **C（新軸を作らず Stack 層で吸収）＋ 必須 4 条件**。
> judgment_confidence 0.35 で `escalate_to_human`、人間が `agreed` で確定。最重量軸
> （哲学者 weight 5 = ΣW の 45%）が options 外の第3の道へ退避したため機構が判定を降りた構造。

---

## 0. 位置づけ — 「軸を増やすか」ではなく「既定が事実誤りを指していた」

当初案は `deploy_target` 新軸の新設だった。Council の 3 軸が独立に、この立て方そのものを退けた。

| 軸 | 指摘 | 本 spec への反映 |
|---|---|---|
| 開発者 | 共有枠は **cross-project state** であり個別プロジェクトの属性ではない。per-project 軸に押し込むのはカテゴリエラー | I-2 / F2（観測 skill が state を持つ） |
| 哲学者 | 既定を企業名に置くと軸の同一性を他者の価格表に握られる。最も重い事実は D1 の数値ではなく「2026-09-01 に日次枠の意味が変わった」こと自体 | I-3 / F3（観測日付 + 失効前提） |
| 経営者 | 論点は設計論ではなく**運用事故**（既定値が満杯の枠を指している）。軸新設の可否に従属させると、C に落ちた場合に事故が放置される | F1 を軸の議論から分離して先行 |

つまり本 spec が閉じるのは「供給元を選べない」ではなく、**既定が到達不能な供給元を指し続けている**状態である。

### 実測（2026-09-11、grep と Cloudflare API）

| 供給元 | DH 内の出現 | 実効性 |
|---|---:|---|
| Supabase | **67 行**（内訳は下記注） | 無料枠 2 アクティブプロジェクト上限（ユーザー単位・全 org 合算）が**既に満杯**。新規案件は必ず行き止まりに当たる |
| Vercel | 4 箇所（`supabase-local-dev.md` 3 / `regime-assessment.md` 1） | Hobby は**商用不可**。業務ツールの置き場として不適格 |
| Cloudflare | **0 箇所** | stack / runtime_profile / プレイブックのいずれにも不在 |

> **計数方法の注（F1 の独立検証 P7 / N2 を受けて明記）**
>
> **基準コミットは `239d249`（F1 着手前の master）。** 本 spec の是正自体が Supabase の言及行を増やすため、
> 基準を書かない計数は自分の変更で無効化される（独立検証 N2 の指摘）。
>
> 上表の Supabase「67」は次のコマンドの結果、すなわち **大小無視でマッチした「行数」**（出現回数ではない）:
>
> ```
> grep -ricr "supabase" .claude/skills/*/SKILL.md .claude/skills/*/references/*.md templates
> ```
>
> **初版は `-r` を末尾に置いていた**（PR #278 で Copilot が指摘）。GNU grep のデフォルトでは
> オプションを引数の後に置いても解釈されるため実測では exit 0 で 67 を返したが、
> `POSIXLY_CORRECT=1` を立てると `grep: -r: No such file or directory` で失敗する
> （いずれも本セッションで実測）。**再現可能性を主題にした注が環境依存のコマンドを載せていては
> 自己矛盾**なので、オプションを前方へ移した（値は同じ 67）。
>
> 内訳は `supabase-local-dev.md` 35 / `spec-architect/SKILL.md` 11 / `schema-evolution.md` 9 /
> `scaffold-checklist.md` 8 / `dialog-questions.md` 3 / `subphase-l02-domain.md` 1。
>
> **このワイルドカードはサブディレクトリと `.claude/agents/` を含まない**ため、2 ファイルを取りこぼしている
> — `references/arc-patterns/realtime-pubsub.md`（配信ゲートウェイの選択肢列挙 1 行）と
> `.claude/agents/review-difficulty.md`（`supabase/migrations/` を risk tier の path glob に使用、1 行）。
> どちらも供給元を選ばせる記述ではない。取りこぼし 2 行を足すと `.claude/` 全体の 69 行と一致する
> （`templates/` の Supabase 言及は 0 件）。
>
> **単位と対象を変えると値は変わる**（同一基準コミットでの実測）: `.claude/` 全体の**出現回数**は
> 大小区別ありで 31（`grep -ro "Supabase" .claude | wc -l`）、大小無視で 96
> （`grep -roi "supabase" .claude | wc -l`。`supabase start` 等の CLI コマンドを含むため）。
> なお 1 巡目の独立検証は大小無視を 95 と報告したが、3 巡目の再実測では GNU grep と
> Python 正規表現の 2 手法がいずれも 96 で決定論的に一致したため、**95 は計測誤り**とみるのが妥当
> （差分の原因自体は未特定）。**同じ対象を数えても報告値が食い違いうる**という事実が、
> 数値に必ずコマンドと基準コミットを添えるべき根拠になる。
>
> 数値を引用する際は計数方法・基準コミット・単位（行 / 出現回数）を添えること
> （I-3 が要求する観測記録の質）。

利用者アカウント（`c2d8bea9`）の実測: 本セッション開始時は D1 2 個で `news-collector` が
**日次 5.3 万行書込 = 無料枠 10 万行/日の 53% を単体消費**していた。利用者承認のもと
news-collector 系（D1 / Worker / Pages / KV / Access app 2 件）を削除し、現在 D1 1 個・60 KB・
日次書込 0〜1 行。**律速は書込枠から「DB 個数 10 個上限」へ移った**。

---

## 不変条件（全機能共通）

- **I-1 新軸を作らない**。供給元は `stack` 軸の内側に閉じる（Council recommended C の骨格）。
  実質 1 列しか埋まらない軸は軸ではなく stack エントリであり、GAS を Stack 11 + runtime_profile 注記で
  吸収した v6.3.0 と同型で扱う。既定は妥当性が成立する定義域（stack）にスコープし、
  `stack=Expo / GAS / Go CLI` のように供給元概念が無効なプロジェクトに既定を及ばせない
- **I-2 共有枠を per-project 属性として表現しない**。アカウント単位で共有される枠（D1 日次行読/行書、
  Workers リクエスト、KV 書込）は cross-project state であり、REGIME.md のような per-project 宣言に
  書かない。state の保持は F2 の観測 skill に閉じる
- **I-3 供給元の数値は規範に固定しない**。他者が単独で真理条件を書き換えられる値（無料枠・料金・保持期間）は
  規範ではなく**観測記録**として扱う。プレイブックに観測日付と失効前提を明記し、規範側は「観測を参照せよ」
  だけを書く
- **I-4 実装順序は 観測 → プレイブック → 規範**。規範を先に書くと、観測が規範を否定したときに
  規範改変コストが観測を抑圧する（哲学者 notes）。よって F2 → F3 → F4/F5 の順で着手する
- **I-5 Cloudflare 無しでも DH は完全動作する**。「GitHub 無しでも DH は完全動作」（v5.0.0）と同型の
  独立性原則。F2 の観測 skill は任意ロードで、不在・認証失敗時は degrade する（機能停止にしない）
- **I-6 観測は判定を持たない**。F2 は検出して数えるだけで、自動で昇格・停止・削除をしない
  （`BOUNDARY.md` I-2 と同型）。是正は人間または L0
- **I-7 常時発火する検知を作らない**。F2 の閾値は「定常状態では 0 件」を満たす値に置く。
  今日の実測（削除後は日次書込ほぼ 0）がベースライン
- **I-8 本 spec 自身に規範メタデータを付す**（`dev-env-spec.md:982`）。各 F 項目に `stage:` /
  `review_trigger:` を明記する

---

## F1. Supabase 既定性の降格（priority: critical / Council 必須条件 1 / 先行実施）

**軸新設の可否から分離して最初に着手する。** これは設計変更ではなく運用事故の修正であり、
F2〜F5 の結論に依存しない。

### 現状（2026-09-11 実測）

`supabase-local-dev.md` は v5.18.0 で「本番を汚さないローカル優先開発」を規範化した。中身の大半は
供給元非依存の叡智（本番直接編集の禁止・migration 一方向・`.env.local` の gitignore）だが、
**推奨発動条件が Supabase 固有のまま既定として機能している**。利用者の無料枠は満杯（2 アクティブ上限・
ユーザー単位で全 org 合算・org を増やしても回避不可）で、この既定に従うと新規案件は着手時点で詰まる。

### 是正

1. `supabase-local-dev.md` の §推奨発動条件に**適用範囲の限定**を 1 ブロック追加する:
   - 「**既存の Supabase プロジェクトを持つ案件にのみ適用**する。新規案件の供給元既定としては用いない」
   - 無料枠の制約を**観測日付つき**で明記（`2026-09-11 観測: 2 アクティブプロジェクト上限・
     ユーザー単位で全 org 合算・paused はカウント外`）。I-3 に従い「この値は腐る」前提を併記
2. `spec-architect/SKILL.md` §6 の推奨開発オプション 1 ブロックに、供給元中立の書き方へ改める
   （「hosted Postgres / BaaS を使う構成では」を主語にし、**本文から Supabase を除去**して供給元別プレイブック表の 1 行（既存案件専用）へ隔離する）
3. `dialog-questions.md` S1 フォローアップの Supabase 前提を同様に中立化する
4. **既存 2 枠は現状のまま使い続ける**（新規追加をしないという意味で、Supabase の `paused` 化ではない）。
   削除・移行を促す記述は書かない（Supabase は PG そのもので移行不要という価値が残るため、
   `deprecation-protocol` は発動しない）
5. **`scaffold-checklist.md` §Supabase ローカル開発 にも適用範囲を明記する**（独立検証 P1 を受けて追加）。
   同節の見出しが「推奨バックエンド開発オプション」であり、上記 1〜3 で中立化した 3 ファイルから
   委譲された読み手がここに到達すると**降格が循環して打ち消される**ため。あわせて、stack カタログ
   （Stack 1〜11）が stack 軸（言語 / FW / ランタイム）を扱うもので **hosted DB / BaaS の供給元選択を含まない**こと（例外は Stack 11 = GAS。実行基盤とデータ層が Google に束縛される）を明示し、
   新規案件の供給元選択は「既定を置かず L0 対話で人間に委ねる」と書く（F4 で Stack 12 が入るまでの正直な状態）

`schema-evolution.md`（9 箇所）と `subphase-l02-domain.md`（1 箇所）は **PG の話として正しい**ため
触らない（Supabase 固有ではなく hosted Postgres 一般の記述）。

### 規範メタデータ

```yaml
stage: S0-S1
review_trigger:
  - measured: 利用者の Supabase 枠が解放された（paused 化等）場合、適用範囲の限定を再評価
  - dated: 2026-09-11 観測の無料枠条件が変わった時点で数値を更新
```

---

## F2. 共有枠の観測 skill 新設（priority: critical / Council 必須条件 2 / I-4 の第一着手）

### 現状

DH には供給元アカウントの枠残量を観測する経路がない。今日の発見（`news-collector` が単体で
日次書込枠の 53% を消費し、超過すれば同一アカウントの `minna-no-ai-bbs` も連鎖停止する構造）は
**人間が MCP で手を動かして初めて判明した**。この検出が人間の目に依存している限り、
量産するほど気づかないうちに枠が埋まる。

### 是正

新規 skill を 1 本追加する。**主目的は枠残量の見張りではなく、暴走案件の早期隔離**（経営者 notes）。

- **観測対象**: Cloudflare GraphQL Analytics API の `d1AnalyticsAdaptiveGroups`
  （`rowsRead` / `rowsWritten` / `readQueries` / `writeQueries` を date × databaseId で取得）。
  加えて REST で D1 個数・容量・KV namespace 数
- **出力**: databaseId 別の日次消費と、アカウント合計の枠消費率。**判定はしない**（I-6）
- **異常検出の主眼**: 「読んだ行数より書いた行数が多い」「7 日間の日次書込がほぼ一定」の 2 パターン
  — これが今日 `news-collector` の全件書き直しを言い当てた signature であり、
  合成ケースで検出力を実証してから ship する（v6.17.0 の規律を継承）
- **閾値**（I-7 に従い定常 0 件になる値）:

  | 指標 | 閾値 | 位置づけ |
  |---|---|---|
  | D1 個数 | 8 個（無料上限 10 の 80%） | 第一トリガー。1 ツール = 1 DB（DB 間 JOIN 不可の必然）なので最も先に来る |
  | 日次行書込 | 5 万行（50%）が 3 日連続 | 書込の重い案件の混入検出 |
  | 日次行読込 | 250 万行（50%）が 3 日連続 | 実際にはほぼ到達しない |
  | 単一 DB 容量 | 400 MB（無料 1DB 上限 500 MB の 80%） | DB 分割または昇格の判断点 |
  | KV 書込 | 700/日（無料 1,000/日 の 70%） | 無料枠で最も狭い |

- **degrade（I-5）**: cloudflareMCP 未認証・API 到達不能・skill 不在のいずれでも DH は通常動作する。
  観測不能は warn として可視化し、機能停止にしない
- **配置**: Level A。prefix と命名は §判断点 D-2（`dev-env-spec.md` §Level A 配布性 checklist
  6 軸 21 項目で評価してから確定する）

### 再発防止機構

観測 skill が存在しても呼ばれなければ今日の事故は再演する。よって **L0 対話の新規ツール立ち上げ時に
現在の枠消費率を提示する**ことを F4 の Stack 12 節に 1 行で配線する（規範側は観測を参照するだけ・I-3）。

### 規範メタデータ

```yaml
stage: 全段階
review_trigger:
  - measured: 異常検出が 6 cycle 連続 0 件なら signature の設計を再評価（I-7）
  - measured: degrade が常態化していれば認証経路の問題として feedback-loop へ還流
```

---

## F3. cloudflare-workers-dev.md プレイブック新設（priority: high / Council 必須条件 3）

### 是正

`references/cloudflare-workers-dev.md` を `supabase-local-dev.md` の兄弟として新設する
（progressive disclosure: 該当時のみロード）。

冒頭に**観測日付と失効前提を明記**する（I-3・哲学者必須条件）:

> この節の数値は 2026-09-11 に一次情報で観測した値である。**供給元が単独で書き換えられるため、
> この表は腐る。** 実際 2026-09-01 に D1 の日次枠の意味が変わった（超過時に無視 → 全クエリ失敗）。
> 数値を判断に使う前に F2 の観測 skill で現在値を確認すること。

内容:

- ローカル開発フロー（`wrangler` / miniflare での D1 ローカルモード、`migrations apply --local`）
- 2026-09-11 観測の枠（無料: Workers 10 万 req/日・D1 10 DB / 1DB 500MB / 合計 5GB / 日次 500 万行読・
  10 万行書・Time Travel 7 日、KV 10 万読・1,000 書/日、R2 10GB。有料 $5/月: 50,000 DB / 1DB 10GB /
  月 250 億行読 / Time Travel 30 日。静的アセットはリクエスト無制限・帯域無料。商用利用可）
- **罠カタログ**（D1 固有）:

  | # | 罠 |
  |---|---|
  | C1 | 日次枠は**アカウント共有**。DB を増やしても枠は増えず、1 案件の暴走で全 D1 クエリが停止する |
  | C2 | 10 GB（無料 500 MB）は**ハード上限**。到達すると書込が失敗する |
  | C3 | **DB 間 JOIN 不可**。横断集計は別途エクスポート経路が必要 |
  | C4 | **Worker 外のプロセスから接続不可**。管理ツール・バッチが CF 内に閉じる |
  | C5 | PG 固有機能（jsonb 演算子 / PL-pgSQL / PostGIS / LISTEN-NOTIFY）は持ち込めない |
  | C6 | 書込 ~50 tps 程度で天井 |
  | C7 | Time Travel は **DB が存在する間のみ**有効。DB を削除すると 7 日以内でも復元不可 |
  | C8 | `nodejs_compat` は 2026-08-04 以降の compatibility date で既定 ON。ただし CPU 重い処理・ネイティブ依存は不向き |

- 静的アセットと Workers の課金境界（Functions を呼ばないリクエストは無料・無制限。SSR や middleware が
  全ルートに乗る構成は「Pages の見た目をした Workers 課金」になる）

### 規範メタデータ

```yaml
stage: S0-S2
review_trigger:
  - dated: 2026-12-11（観測から 3 ヶ月）に数値の再観測。失効前提の実効性をここで測る
  - measured: 罠カタログに載っていない事故が起きたら追記（罠は実害からのみ増やす）
```

---

## F4. Stack 12: Cloudflare Workers + Hono + D1/R2（priority: high / Council recommended C の骨格）

### 是正

`scaffold-checklist.md` の追加 stack カタログに Stack 12 を DH 形式で追加する（11 → 12 stack 化）。

- **必須生成ファイル**: `wrangler.toml`（`compatibility_date` 明記）/ `src/index.ts` /
  `migrations/0001_init.sql` / `package.json` / `tsconfig.json` / `.dev.vars.example` /
  `public/` / `.gitignore`（`.dev.vars` / `.wrangler` を除外）
- **最低要件**: 純粋ロジック層と Cloudflare binding 接触層の**層分離**（Stack 11 = GAS で最低要件化した
  規約を継承。ローカルで決定論検査できる面を確保する）
- **決定論 smoke**: `tsc --noEmit` / lint / `wrangler d1 migrations apply <db> --local` /
  `vitest`（miniflare 環境）。`wrangler dev` の起動確認まで
- **runtime_profile**: `local-reproducible`（miniflare でローカル再現可能）。§判断点 D-4 で実測確認
- **L0 対話への配線**: 本 stack を選んだ場合、F2 の観測 skill で**現在の枠消費率を提示する**
  （新規質問は増やさない。I-3 に従い規範は観測を参照するだけ）

### 規範メタデータ

```yaml
stage: S1
review_trigger:
  - measured: smoke が認証を要求するなら runtime_profile を cloud-managed へ訂正（+ ADR）
```

---

## F5. D1 / Hyperdrive+PG の機械判定分岐表（priority: high / Council 必須条件 4）

### 現状

L0 対話での出し分け基準を「消失許容度」という主観語に置くと、判定が AI 推論依存になる。

### 是正

`cloudflare-workers-dev.md` に**機械判定可能な 3 条件**の分岐表を置く。1 つでも該当すれば
Hyperdrive + 外部 Postgres を選ぶ。

| # | 条件 | 判定方法 |
|---|---|---|
| 1 | 消失が許容できないデータを持つか | Time Travel 無料 7 日では不足するデータか（顧客・請求・現場記録 等）を L0 の 1 問で確認 |
| 2 | 単一 DB が 500 MB を超える見込みか | 想定レコード数 × 平均行長の概算 |
| 3 | DB 間 JOIN または Worker 外からの接続が要るか | 横断集計ダッシュボード / 管理バッチ / PG 固有機能（jsonb 演算子・PL-pgSQL・PostGIS・LISTEN-NOTIFY）の要否 |

いずれも非該当なら D1（軽量・再生成可能な設定・マスタ・収集ログが大多数）。
Hyperdrive は無料プランでも利用可（2026-09-11 観測: 10 万クエリ/日）。

### 規範メタデータ

```yaml
stage: S0
review_trigger:
  - measured: D1 と Hyperdrive+PG の採用比率を観測し、PG 側が過半を占めるなら供給元設計を再評価
    （経営者 concern: 2 プロファイル並立は保守対象を 2 系統に増やす）
```

---

## 判断点（人間専管・AI は代筆しない）

| # | 判断点 | 状態 |
|---|---|---|
| D-1 | $5/月（Workers Paid）への昇格 | **人間決定済み（2026-09-11）: 当面無料を維持**。経営者軸の異見（「無料枠の閾値管理は無料ではない。注意コスト月 1 時間 > $5。有料は観測作業の買取費」）は minority として温存し、F2 の観測 skill が実測を出した時点で再判断する |
| D-2 | 観測 skill の prefix・命名・配置 | 未判断。`dev-env-spec.md` §Level A 配布性 checklist（6 軸 21 項目）で評価してから確定 |
| D-3 | `news-collector` の外部呼び出し元 | **未特定**。cron schedules は空だったのに日次 5.4 万行の書込があった ＝ 呼び出し元が Cloudflare の外にある。Worker 削除済みのため呼び出し元はエラーを受け続ける。特定と停止が必要 |
| D-4 | Stack 12 の runtime_profile | `local-reproducible` を仮置き。miniflare での決定論 smoke が認証なしに exit 0 まで通るかを実測して確定（開発者 premise） |
| D-5 | Judgment Agent の `weight_note` が規格から 2 点逸脱する | **(a) カテゴリの誤記**: 本 spec の諮問（dt0911）で `category: "conception"` に対し `weight_note` が「カテゴリ: implementation」と書いた（PR #277 で Copilot が検出）。**判定への影響はない** — `final_weights` 3/3/5 は `council-weights.md` の conception 補正（base 3/4/3 に 経営者 0 / 開発者 −1 / 哲学者 +2）の適用結果と一致し、過去の conception エントリ（`claude-md-purity`）も 3/3/5、implementation なら 2/6/2 になるため（ブリーフ §7.3）。**(b) 字数規定の超過**: `output-format.md:89` は `weight_note` を「100 字以内」と規定するが、dt0911 の実値は **186 字**。これは本追記固有ではなく機構の恒常的逸脱で、COUNCIL-LOG 全体の `weight_note` 44 件中 **29 件（66%）が 100 字超**（2026-09-11 実測）。(a)(b) いずれも COUNCIL-LOG は append-only ゆえ当該記録は改変せず事実として保存する。再演を防ぐなら `judgment-agent.md` の prompt または `council-fanout.workflow.mjs` で、カテゴリを args の `category` から機械代入し、字数を schema 強制する（本 spec の範囲外・別 PR）。なお `persona_summary.note` には字数規定が無く（§8 に該当行なし）、`council-log-skill-archive.md` の 360 字畳み込みルールは **archive → COUNCIL-LOG への転記時**に限った規約である（同ファイル冒頭「転記時の畳み方」。COUNCIL-LOG の `note` 124 件中 50 件が 360 字超という実測もこれを裏づける） |

---

## 実装しないもの

- **`deploy_target` 新軸の新設**（当初案 A / Council recommended C により却下）。
  哲学者の第3の道（既定を制約プロファイルに置き、軸名を「供給元制約（依存姿勢）」とする案）は
  minority_opinion として `COUNCIL-LOG.md` に温存。供給元を跨ぐ構成（Hyperdrive+PG）が Stack 層で
  表現しきれなくなった時点が再問の契機
- **Cloudflare を規範の既定値にすること**（I-1）。既定は stack の定義域に閉じ、
  供給元既定は `supabase-local-dev.md` / `cloudflare-workers-dev.md` の推奨発動条件の提示順序で表す
- **$5/月への昇格**（D-1 の人間決定により当面無料）
- **Supabase の廃止**（F1 のとおり凍結。`deprecation-protocol` は発動しない）
- **既存の PG 前提記述の書き換え**（`schema-evolution.md` / `subphase-l02-domain.md` は
  hosted Postgres 一般として正しい）
- **配布先向けの同型観測**（`harness-verifier/` と同じく、F2 は利用者プロジェクトが呼ぶ skill であって
  DH 本体の自己検査ではない。DH 自身は Cloudflare を使わない）

---

## Council 記録

- `council-2026-09-11T03:07:42Z-dt0911` — business / conception / C2 / phase_3 / workflow
- final_weights: 経営者 3 / 開発者 3 / 哲学者 5（ΣW 11）
- conflict_type: `simple_conflict`。weighted_score C 2.34 / A 2.16（gap 率 0.016 の拮抗）
- 哲学者 weight 5 は options 外（第3の道）ゆえ `third_way_excluded`。ΣW の 45% ≥ 30% により
  confidence 帯上限を 0.50 へ切下げ → judgment_confidence 0.35 → `escalate_to_human`
- implementer_consent: `agreed`（2026-09-11 人間判定）
- 詳細は `history/COUNCIL-LOG.md`
