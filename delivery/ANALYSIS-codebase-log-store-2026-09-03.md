# コードベース自身のログ置き場（ログ層）— DH メタスキル設計の前ブレスト

> L0 前ブレスト（未確定・仕様ではない）。開始 2026-09-03。
> 置き場について: kakuman の `l0-pre-brainstorm` は `docs/brainstorm/` を規定するが、DH 本体は
> `.gitignore` で `docs/*` を除外している（migration-guide のみ例外）。DH 側の標準
> （`brainstorm-orchestration.md` §3）に従い `delivery/ANALYSIS-*.md` に置く。
> この二重規範自体が未解決論点（後述 §未解決 U-7）。

## 問い

ひでさん（2026-09-03）:
「今後展開するプロジェクト（今リポジトリに含まれているプロジェクトも含めて）では、あらゆるログを
記録しておく場所を設けたい。**開発ログというよりかは、そのアプリやプロジェクト自体の、
コードベース自体のログを貯めとく場所**。これの設計を考える」

AI 側の読み（訂正歓迎）:
- 「開発ログ」= `history/`（INTENT / CHANGELOG / HANDOFF / SUMMARY = 人間と AI の**判断の記録**）
- 「コードベース自体のログ」= **コードが動いた・検査された・触られた結果として機械が吐く記録**。
  人間が書くものではなく、発生源がプログラムであるもの
- 「場所」= 物理ディレクトリとは限らない。「どこにあるか一意に分かる」ことが要件の核と読んだ

## 調べたこと

### F1. 3 リポジトリで「機械が吐く記録」は既に存在するが、5 つの保管先に散っている

| 保管先 | kakuman-platform-v3.0 | cc-cockpit | dialog-harness |
|---|---|---|---|
| **外部 SaaS** | Sentry（FX-OBSERVABILITY、PII 契約 X-OBS-PII）/ Vercel ログ | — | GitHub Actions ログ |
| **DB** | `samejima_activity_log`（public・append-only）/ `underlay_usage_*`（`ops` スキーマ・PostgREST 不到達）/ freee-monitor sync ログ / `expense_ocr_metrics` | SQLite `data/*.db`（`usage_daily` 等） | — |
| **repo 内・gitignore** | `*.log` / `harness-verifier/reports/` 丸ごと | `*.log` / `coverage/` / `playwright-report/` / `test-results/` / `.cc-cockpit/`（セッション報告） | `harness-verifier/reports/hook-observations.jsonl`（生観測） |
| **repo 内・committed** | `PERF_AUDIT.md` / `docs/PROJECT-*ASSESSMENT*.html`（手動・単発） | — | `harness-verifier/reports/YYYY-MM.md`（月次蒸留）/ `delivery/ANALYSIS-*.md`（scripts/*.py の出力） |
| **ホーム配下（repo 外）** | `~/.claude/projects/**/*.jsonl`（CC transcript） | 同左（cc-cockpit はこれを**読み取り専用**で主データ源にする、SPEC C11） | 同左 |

観測: **決定論センサー（`scripts/check-*` / `lint-*`）の出力は stdout に流れて消える**。
CI 上で走った結果は GitHub Actions のログ保持期間（既定 90 日）で失われる。
「コードベースが検査された記録」は現状どのプロジェクトにも**蓄積されていない**。

### F2. kakuman には「開発観測ログ」という概念が既に言語化されている

SPEC FX-SAMEJIMA §F（`samejima_activity_log`）:
「閲覧 = 開発者（CC）参照前提。人間 UI は提供しない（Supabase 直読み / MCP で CC が観測 =
harness 観測ログ / freee-monitor sync ログと同じ**『開発観測ログ』の位置づけ**）」

→ **読み手が AI（CC）であるログ**という分類が実地で生まれている。これは 12-factor の想定
（読み手 = 運用者 / 分析基盤）と異なる。本ブレストの対象は、この「AI が読むための、
コードベース由来の記録」に近いと推定。

### F3. kakuman F4-8 使用ログは「ログを足すと何が起きるか」の実測済み先例

- 罠 X-UNDERLAY-B (3)「DB・保存・ログイン機能を足さない」を**観測ログの追記のみ限定解除**
- 判定基準を構造化: 「**ログ表を DROP しても機能が完全に動く**」= 観測と保存機能を分ける線
- 監視への転化防止: 本体表（匿名）と対応表（`session_id → employee_id`）を**2 表に分離**、
  対応表は 90 日で先に消す（X-NORTHSTAR-A「個人単位の利用率・ランキング・未利用者リストを作らない」）
- **事故**: 当初 `check_is_admin()` 読み口 = 22 名中 11 名が閲覧可 → 「開発管理者専用」になって
  いなかった → U-11 で `ops` スキーマへ隔離（Exposed schemas 未登録 = PostgREST 不到達）

→ ログの設計論点は「どこに置くか」より **「誰が読めるか」「いつ消えるか」「個人に紐づくか」** が先に来る。

### F4. DH には「観測 → 候補 → 人間承認」の逆流路が既にあり、ログはその上流

- `templates/rules/common/telemetry-reflux.rules.md`（v6.15.0 F4）: 逆流源を `telemetry-reflux.yml` で
  **宣言**する枠。不変条件 TR-1 候補のみ / TR-2 検知は決定論 / TR-3 閾値は目標値でない /
  TR-4 常時発火する検知は形骸化
- `scripts/signal-scan.py`（v6.15.0 F1）: red_ci / stale_pr / review_trigger / ctl_pending の 4 検知器。
  **入力は GitHub API**（PR / Actions）であって、リポジトリ内のログではない
- `crosscut-hook-observer`: hook 観測を `hook-observations.jsonl` に append-only、**生は gitignore・
  蒸留物のみ commit**（Council hook 修理・案 B）
- `dh-manifest.yml` upstream U-5: 還流するのは機構ではなく**それを必要とした出来事**（事故の日付と解いた問題）

→ DH は「信号の宣言」「信号の検知」「観測の蒸留」を別々に持つが、**「信号の素材（ログ）が
どこにあるか」を宣言する層が無い**。telemetry-reflux.yml は「何を監視するか」であって
「何が記録されているか」の台帳ではない。

### F5. 一次情報: 業界標準は「アプリはログファイルを管理しない」

- **12-factor Logs**: "A twelve-factor app never concerns itself with routing or storage of its output
  stream. It should not attempt to write to or manage logfiles." 各プロセスは stdout に書き、
  実行環境が集約・保管する。https://12factor.net/logs
- **OpenTelemetry LogRecord**: Timestamp / ObservedTimestamp / TraceId / SpanId / SeverityText /
  SeverityNumber / Body / Resource / InstrumentationScope / Attributes / EventName。
  `EventName` を持つ LogRecord = Event（構造化ログの標準形）。
  https://opentelemetry.io/docs/specs/otel/logs/data-model/
- **Claude Code の telemetry**: `CLAUDE_CODE_ENABLE_TELEMETRY=1` + `OTEL_LOGS_EXPORTER=otlp|console`。
  events = `claude_code.user_prompt` / `tool_result` / `tool_decision` / `api_request` / `api_error` 等。
  相関キー `session.id` / `prompt.id` / `tool_use_id`。**file exporter は無い**（otlp / console / none）。
  https://code.claude.com/docs/en/monitoring-usage
- **Claude Code hooks**: 全 event が `session_id` / `prompt_id` / `cwd` / `transcript_path` を受け、
  シェルで任意ファイルに追記できる。`${CLAUDE_PROJECT_DIR}` placeholder あり。
  `transcript_path` は非同期書込で遅延しうる（注記あり）。
  https://code.claude.com/docs/en/hooks

→ 「repo 内にログを貯める」は業界標準に対する**意図的逸脱**になる。逸脱するなら理由
（小規模・単独開発・読み手が AI・実行環境が個人 PC で集約基盤を持たない）を明記する必要がある。
逆に、標準に従うなら「場所」= 集約先（OTel collector / Sentry / DB）+ repo 内は**台帳だけ**になる。

### F6. 観測（訂正対象）: DH の `VERSION` は `6.11.0` だが、v6.12.0〜v6.15.0 の upgrade-spec と
v6.15.0 起源の scripts / templates が既に main に存在する

`git log -- VERSION` の最終更新は v6.11.0（#186）。`upgrade-spec-v6.15.0.md` は「L0 起草
（人間レビュー待ち）」だが `signal-scan.py` / `telemetry-reflux.rules.md` は v6.15.0 F1/F4 として
実装済み。本ブレストと無関係だが、**ログ層を「v6.x のどこに乗せるか」を語る前提として版が
ずれている**ので記録しておく。

## 選択肢

| 案 | 内容 | 成立条件 | 代償 | 反面教師 |
|---|---|---|---|---|
| **A. 物理集約（repo 内ディレクトリ）** | `logs/`（or `.dh/log/`）に全ログを JSONL で貯める。gitignore。 | ローカル単独開発・小規模。全発生源がファイルに書ける | DB ログ（kakuman）は来ない。マシンを跨ぐと消える。**12-factor 違反**（F5）。「あらゆる」を 1 箇所に置くと PII 混在（F3 X-OBS-PII と衝突） | 12-factor Logs。kakuman F4-8 の「読み口 11/22 名」事故（集めた瞬間に誰が読めるかが問題化） |
| **B. 台帳型（manifest）** | `logs.yml`（or `LOGS.md`）に「ログ ID / 発生源 / 保管先 / 形式 / 保持期間 / PII 区分 / 読み手 / 消しても機能が動くか」を**宣言**。実体は各所のまま | 宣言の drift を機械検査できる（`scripts/check-*` の慣行に載る） | 実体は散ったまま。台帳を書く手間が 1 本増える | kakuman 生ログ停止事故（CHANGELOG 2026-06-18 / HANDOFF 06-16 で 2 ヶ月停止 = **書く先を増やすと止まる**） |
| **C. DB 集約（`ops` スキーマ相当）** | kakuman の `ops` 隔離を規範化し、全ログを DB の非公開スキーマへ | DB を持つプロジェクトのみ | cc-cockpit（SQLite・ローカル）/ DH（DB 無し）に横展開できない。**横断機構にならない** | — |
| **D. 外部集約（OTel collector / Sentry）** | 12-factor 準拠。repo は何も持たない | collector を常駐させる運用 | 費用・PII 送出面の拡大（X-OBS-PII）。ローカル専用アプリ（cc-cockpit C8「中から漏らさない」）と衝突 | Sentry Session Replay 常時録画を止めた経緯（X-OBS-PII (2)） |
| **E. 二層 + 台帳（A' + B）** | 既存パターン「**生 = ローカル gitignore JSONL / 蒸留 = committed md**」（hook-observations.jsonl → reports/YYYY-MM.md）を一般化し、B の台帳で全保管先（DB / SaaS / ローカル / ホーム）を一覧化。JSONL は OTel LogRecord の最小サブセット（ts / event / severity / body / attrs / session.id） | DH は枠（台帳テンプレ + JSONL 形式 + 検査スクリプト）だけ持ち、実定義は各プロジェクト（telemetry-reflux と同型） | 「二層」を守る規律コスト（蒸留を誰がいつやるか = 代謝問題の再演） | history 代謝（reindex-librarian が必要になった経緯 = 生を貯めるだけでは購読量が線形に膨らむ） |

## いま出ている案

**推奨（判定ではない）: E を「台帳（B）から始めて、物理（A'）は後」の順で。**

理由:
1. F1 のとおり、いま欠けているのは**保管先ではなく所在の一覧**。DB / SaaS / ローカル / ホームに
   散っていること自体は（読み手が AI なら）致命的でない。致命的なのは「AI が『このプロジェクトに
   どんなログがあるか』を知る手段が無い」こと
2. 台帳は telemetry-reflux.yml と**同じ宣言型**なので、DH に既にある「枠だけ持つ・実定義は
   プロジェクト」の構造に乗る。D4 を触らず D2 テンプレとして配布できる（最小主義ラダー整合）
3. F3 の実測から、ログの論点は「読める人 / 消える時期 / 個人紐づけ」が先。台帳にこの 3 列を
   **必須欄**にすれば、A' で物理集約する前に PII と監視転化の線が引ける
4. 物理集約（A'）は「決定論センサーの出力が消えている」（F1 観測）という**具体的な欠落 1 点**から
   始めれば足りる。「あらゆるログ」を最初から 1 箇所に集めるのは TR-4「常時発火する検知は形骸化」
   の同型（貯めるだけのログは読まれない）

**台帳の列案（たたき台）**

| 列 | 例 | なぜ要るか |
|---|---|---|
| `id` | `sensor-output` | 一意参照（telemetry-reflux の `id` と相互参照） |
| `source` | `scripts/check-*` / `apps/server/host.ts` / Sentry SDK | 発生源 = コードのどこか |
| `kind` | runtime / sensor / ci / ai-session / audit | 種別（F1 の行に対応） |
| `store` | `local:.dh/log/*.jsonl` / `db:ops.*` / `saas:sentry` / `home:~/.claude/projects` | 保管先の種類 + パス |
| `format` | jsonl(otel-min) / md / sqlite | 読み手（AI）がパーサを選べる |
| `reader` | ai / human / reflux | **読み手が誰か**（F2 の「開発観測ログ」区分） |
| `retention` | 90d / 1y / forever / ci-90d | **いつ消えるか**（F3 の対応表 90 日と同じ規律） |
| `pii` | none / pseudonymous / personal | X-OBS-PII / X-NORTHSTAR-A の線引き |
| `droppable` | true / false | 「消しても機能が動くか」（F3 のステートレス判定基準） |
| `committed` | false / distilled-only / true | 生 / 蒸留の二層をどう扱うか |

## 未解決の論点

- **U-1 「あらゆるログ」の範囲**: F1 の 5 行（runtime / sensor / ci / ai-session / audit）のうち、
  どこまでを本設計に含めるか。特に **CC transcript（ホーム配下・読み取り専用）**を「コードベースの
  ログ」に数えるか。数えるなら cc-cockpit がその読み手として既に存在する
- **U-2 読み手**: AI（CC）/ 人間 / 逆流機構（signal-scan）のどれを主とするか。読み手が形式を決める
- **U-3 生 / 蒸留の二層**: 蒸留を誰が・いつやるか。reindex-librarian に統合するか、別 skill か
- **U-4 DH 上の位置**: D2（L0 が存在保証するファイル群）に `logs.yml` を足すのか、
  `telemetry-reflux.yml` に統合するのか（「監視する信号」と「存在する記録」は別概念だが同居は可能）
- **U-5 `dh-manifest.yml` の boundary**: `.dh/log/` 相当を `never_touch` に足すか（プロジェクト状態ゆえ）
- **U-6 12-factor からの逸脱理由**: 明記するなら何か（小規模 / 読み手 AI / 集約基盤なし）。
  将来 collector を持ったとき台帳の `store` を書き換えるだけで移行できる形にしておくか
- **U-7 ブレストメモの置き場**: DH は `docs/*` gitignore ゆえ `delivery/ANALYSIS-*`、kakuman は
  `docs/brainstorm/`。l0-pre-brainstorm を DH 昇格するとき（kakuman ブレスト 2026-08-24 の決定）
  どちらを採るか
- **U-8 VERSION drift**（F6）: 本件の版位置を語る前に `VERSION` と upgrade-spec の対応を揃えるか

## ブレスト決定

**2026-09-04 ひでさん — ログ層キット 0903（10 問）の回答**（HTML: https://claude.ai/code/artifact/1c3b9517-a83d-4d41-b38d-86c0869fab28 、回答原文は `delivery/DECISION-KIT-codebase-log-store-2026-09-03.md` §決定記録）

| Q | 決定 | ひでさんメモ |
|---|---|---|
| Q1 範囲 | **A** sensor + ci から始める | 将来的には 5 種全部を対象にしたい |
| Q2 読み手 | **A** AI（CC）主 | 開発のメインは AI。人間は明示指示時に HTML で読めればよい |
| Q3 形 | **C** 物理集約のみ・台帳を作らない | **council にも問う** → 諮問 `council-2026-09-04T10:05:00Z-lg0903`（下記） |
| Q4 生 / 蒸留 | **A** 二層（生ローカル gitignore / 蒸留 commit・reindex-librarian 相乗り） | — |
| Q5 DH 上の位置 | **A** D2 テンプレ（yml + 検査スクリプト、skill は作らない） | **DH として開発ログとアプリ（コードベース）のログは明確に分ける**。重複は可 |
| Q6 manifest | **A** 宣言ファイルを merge 分類へ、実体は列挙しない | 「よくわからん。違和感あったら教えて」→ 下記 §Q6 の注記 |
| Q7 12-factor | **A** 逸脱を明記し store 列で将来移行可能に | — |
| Q8 メモ置き場 | **B** `delivery/ANALYSIS-*` に統一（kakuman 側も移す） | kakuman 側のコードベースで矛盾が起こらないよう注意 → 下記 §Q8 の実行条件 |
| Q9 VERSION drift | **A** 本件と切り離し別 PR で先に | — |
| Q10 次の一手 | **A** ブレスト継続（棚卸しを調査で埋める） | 同様に HTML 化して選択できるように → 棚卸しキット 0904 |

### Q3 の Council 諮問結果（`council-2026-09-04T10:05:00Z-lg0903`、C2 / conception、judgment_confidence 0.38 = **人間エスカレーション圏**）

- **骨格の推奨 = D**: 物理集約を主とし（人間の C の意図 = 実体が 1 箇所に貯まる、を保つ）、**独立した台帳ファイルは作らない**。Q5/Q6/Q7 の「logs.yml」は `logs/` 内の 1 枚（`logs/index.yml`）に同一化して衝突を解消する。生 JSONL は `logs/raw/` のみ gitignore（`logs/` 丸ごと ignore は子の再 include が効かない）、蒸留 md は tracked。DB / SaaS / transcript は store 列で「repo 外」を宣言するだけで export を committed 領域へ持ち込まない
- **3 軸の共通認識**: ① 実害として失われているのは sensor/ci の stdout 1 種だけで、物理集約で 100% 埋まる ② 手書き台帳は腐る（CHANGELOG/HANDOFF 2 ヶ月停止の実害） ③ Q3-C と Q5〜7 の衝突は人間の意図の矛盾ではなく、**判断キットが logs.yml を前提に設問を組んだ産物**
- **残る人間判断点（Council が降りた 1 点）= その 1 枚の性格**: (D-1) 手書きの最小索引・列 3 つ以下〔経営者〕/ (D-2) 収集器が読む設定 + 検査スクリプトを同 PR で出荷〔開発者・B 相当〕/ (D-3) 各 stream の機械 header から生成する生成物、`database.types.ts` 同型〔哲学者・第3の道・重み 5 だが options 外ゆえ非加算〕→ キット 0903 に **Q3′** として追加
- 少数意見（保持）: 開発者 = export は raw 限定 / dedup キー（session_id + ts + sensor id）/ 検査スクリプト同 PR 出荷。哲学者 = 「台帳を消す」でも「人間を台帳側へ引き戻す」でもなく「台帳を手書きしない」。repo 外記録の所在は既存ルーティング表の行として持つ方が一貫する

### Q5 メモの反映 — 開発ログとコードベースのログの分離（DH 規範の線）

| | 開発ログ（既存） | コードベースのログ（本件） |
|---|---|---|
| 書き手 | 人間と AI の**判断** | **機械**（センサー / CI / アプリ / hook） |
| 置き場 | `history/`（INTENT / CHANGELOG / HANDOFF / SUMMARY / COUNCIL-LOG） | `logs/`（raw = ローカル / 蒸留 = commit / index.yml） |
| 代謝 | reindex-librarian（HOT → COLD） | 同じ機械に相乗り（Q4-A）。ただし対象ディレクトリは別 |
| DH 上の分類 | `dh-manifest.yml` never_touch `history/` | `logs/index.yml` = merge、`logs/raw/` = 既定不可侵 |
| 交差 | hook-observations.jsonl（AI セッションの観測）は**開発ログ側**に留める | 重複記録は可（ひでさん）。dedup キーだけ決める |

### Q6 の注記（違和感の有無）

構造的な違和感は無い。1 点だけ: Q3 の Council 結果により宣言ファイルは `logs.yml`（ルート）ではなく **`logs/index.yml`** になるので、merge 分類に書くパスもそれに揃える。`logs/` 丸ごとを never_touch に列挙する必要は無い（明示列挙しない = 既定で不可侵）。

### Q8-B の実行条件（kakuman 側の矛盾回避）

kakuman で `docs/brainstorm/` を参照している箇所は 09-04 実測で **SPEC.md 4 箇所・REGIME.md 1 箇所・`docs/brainstorm/README.md`・`.claude/skills/l0-pre-brainstorm/SKILL.md` 4 箇所・`.claude/skills/feedback-triage/SKILL.md` 1 箇所・history / delivery の記録 8 箇所**。このうち **`.claude/skills/**` の 2 ファイルは L-FROZEN-META（AI 不可侵）**ゆえ AI は書き換えられない。順序: ① 人間が 2 skill の記録先を `delivery/ANALYSIS-*` に改訂（または DH 昇格版 skill が降りてくる）→ ② AI が 6 ファイルを `delivery/` へ移し、SPEC 4 リンクと REGIME 1 行を更新、`docs/brainstorm/README.md` を転送先案内に置換（history / delivery の過去記録は書き換えない）。①前に AI だけで②をやると skill と実態が食い違うので、**本 cycle では kakuman 側は動かしていない**。

### 開いたままの論点（更新）

- Q3′（索引 1 枚の性格）— キット 0903 に追加、人間回答待ち
- Q9-A の実行（VERSION と upgrade-spec の対応表）— 別 PR
- 棚卸しキット 0904（22 種 + 欠落 1、A/B/C）— 人間回答待ち

## 次にやるなら（09-04 更新）

- Q3′ と棚卸しキット 0904 の回答が揃えば、段階 1 の初期集合（sensor + ci）と `logs/index.yml` の形が決まり、L0（upgrade-spec 起草）へ上げられる材料が揃う（上げるのは人間の明示指示のみ）

（初回の記述）

- U-1 / U-2 の答えが出れば、F1 の表を「台帳の初版」として 3 プロジェクト分埋めるのは調査だけで
  できる（実装ではない）
- 「決定論センサーの出力が消えている」（F1 観測）は、台帳の有無と独立に、
  `pnpm verify` 相当の出力を JSONL 1 本に追記するだけで止血できる（L0 へ上げる場合の最小スコープ候補）
