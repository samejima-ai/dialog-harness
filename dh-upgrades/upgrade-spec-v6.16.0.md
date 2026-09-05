# upgrade-spec v6.16.0 — コードベース自身のログ層（`logs/` 物理集約 + `logs/index.yml` 収集器設定）

> **状態: L0 起草（人間レビュー待ち）**。本仕様の実装は escalation-matrix「規範文書改変」行に従い、
> 人間レビュー通過後・実装前に Council 諮問を経る（本 spec 自体の設計判断は下記 3 諮問で確定済み。
> 実装前諮問は「spec → 実装」の写像の検証に限る）。
> 起点: ひでさん発話（2026-09-03）「今後展開するプロジェクトでは、あらゆるログを記録しておく場所を設けたい。
> 開発ログというよりかは、そのアプリやプロジェクト自体の、コードベース自体のログを貯めとく場所」
> → L0 前ブレスト（`delivery/ANALYSIS-codebase-log-store-2026-09-03.md`、PR #238）→ 判断キット 0903 / 棚卸しキット 0904
> （`delivery/DECISION-KIT-codebase-log-*.md`、PR #242 / #243）→ Council 3 諮問 → 人間「L0 昇格」（2026-09-04）。
> **一次材料**: 上記 ANALYSIS §ブレスト決定（10 問の決定 + 3 諮問の結論）。
> **版番号の注記**: `VERSION` は 6.11.0 のまま v6.12.0〜v6.15.0 の spec が存在する（判断キット Q9-A = 別 PR で先に揃える）。
> 本 spec は「v6.15.0 の次」として v6.16.0 を仮置きする。番号は VERSION 整合 PR の結果に従う。

---

## 0. 位置づけ — 開発ログの隣に、機械が吐く記録の置き場を作る

DH の配布先は既に**開発ログ**（`history/` = 人間と AI の判断の記録。INTENT / CHANGELOG / HANDOFF / SUMMARY / COUNCIL-LOG）を持つ。
本仕様が足すのは**コードベース自身のログ**（書き手が機械: センサー / CI / アプリ / hook）の置き場で、両者は別物として分離する（Q5 メモ「明確に分ける。重複は可」）。

| | 開発ログ（既存・触らない） | コードベースのログ（本仕様） |
|---|---|---|
| 書き手 | 人間と AI の**判断** | **機械** |
| 置き場 | `history/` | `logs/` |
| 代謝 | reindex-librarian（HOT → COLD） | 同じ機械に相乗り（対象ディレクトリは別） |
| DH 上の分類 | `dh-manifest.yml` never_touch | `logs/index.yml` = merge、`logs/raw/` = 既定不可侵 |

実測（2026-09-03、3 リポ）で確認した欠落は 1 つだけ: **決定論センサー（`check-*` / `lint-*` / `pnpm verify` / `scripts/test-*`）の stdout がどこにも残らない**。
他の 22 種の記録（Sentry / DB ログ表 / Actions ログ / hook 観測 / transcript 等）は既に各所に存在し、動かさない。
**本仕様の投資対象は「新しい場所を作る」ことではなく「消えている 1 種を拾う」ことである**（Council lg0903 3 軸共通認識）。

### 12-factor Logs からの意図的逸脱（Q7-A）

12-factor は「アプリはログファイルを管理せず stdout に流し、実行環境が集約する」と定める。本仕様は repo 内 `logs/` に貯めるため逸脱である。
逸脱の理由 3 点: ①小規模・単独開発で集約基盤（collector）を持たない ②読み手が AI（CC）であり、AI にとって「場所」は grep 到達可能な path である
③cc-cockpit のようなローカル専用アプリは「中から漏らさない」（SPEC C8）を規律とし外部集約と衝突する。
**逸脱の縮小**: センサー本体は stdout のまま（I-3）、集約は外側のラッパー = 実行環境側が担う。将来 collector を持つ日は `index.yml` の `store` 列を書き換えるだけで移行できる形にしておく。

### DH と配布先の分業

DH = D2 テンプレ（`logs/index.yml` 雛形 + 収集器 + 検査スクリプト + 規約 1 枚）を配布。実定義（stream の追加・retention 値）は配布先。
**skill は作らない**（Q5-A。台帳の運用に AI の判断を要する手順は無く、宣言 + 決定論検査で足りる）。

---

## 不変条件（全機能共通）

- **I-1 開発ログとコードベースのログを混ぜない**。`history/` と `logs/` は別ディレクトリ・別規範。hook 観測（`hook-observations.jsonl`）は開発ログ側に留める。重複記録は可、dedup キーだけ決める
- **I-2 `index.yml` は「読まれる設定」であって「読まれる文書」ではない**（Council lg3p01）。収集器が毎 run 読み、検査スクリプトが機械検証する。**ラッパーがハードコード path で動く抜け道を作らない**（作った瞬間、手書き台帳に退化する）
- **I-3 センサー本体を改変しない**。収集は外側のラッパーが行い、stdout / stderr / exit code をそのまま透過する（観測層が命令層を壊さない）
- **I-4 生 = ローカル、蒸留 = commit**。`logs/raw/` のみ gitignore（`logs/` 丸ごと ignore は子の再 include が効かない）。生ログと export を committed 領域へ持ち込まない
- **I-5 ログを機能の入力にしない**。`logs/` を DROP してもコードベースが完全に動く（kakuman F4-8 U-1 のステートレス判定基準）
- **I-6 個人に紐づく列・PII を段階 1 に入れない**（X-NORTHSTAR-A / X-OBS-PII 同型）。段階 1 は sensor + ci（PII none）に閉じる
- **I-7 読み手のいない stream を増やさない**。stream の追加は「読む儀式」への接続と同時に行う（TR-4「常時発火する検知は形骸化」と同型）。段階の昇格は**読まれた実績**を条件とし、3 ヶ月で一度も読まれなければ縮小する
- **I-8 宣言と配線を同一 PR で行う**（v6.15.0 I-3 と同型）。`index.yml` 雛形・ラッパー・検査スクリプト・`pnpm verify` / CI への配線 diff・GRAPH.yml ノードを同じ PR に含める
- **I-9 検知は決定論**。蒸留・検査に LLM を使わない（第 2 条）

---

## F1. `logs/` ディレクトリ規約 + `logs/index.yml` 雛形（priority: critical / D2 テンプレ）

| 条件 | 内容 |
|---|---|
| F1-1 | `templates/rules/common/log-ledger.rules.md` を新設（telemetry-reflux.rules.md と同型の「枠だけ」規約）。冒頭に §0 の逸脱理由 3 点 + 移行条件、不変条件 I-1〜I-9 を転記 |
| F1-2 | `logs/index.yml` 雛形。stream 1 件 = 必須 5 列 **`id` / `store` / `path` / `reader` / `retention`** + 任意 2 列 `pii`（段階 1 は `none` 固定）/ `source`。`store` の値域 = `local` / `db` / `saas` / `home`。**列上限（7）を index.yml 自身の header に書き、検査で数える**（列の増殖で台帳に戻るのを機械で止める） |
| F1-3 | `store: local` の行だけがラッパーの書込先。`db` / `saas` / `home` の行は**所在の宣言のみ**（export しない・path 実在検査の対象外。外部到達性は検査しない） |
| F1-4 | ディレクトリ: `logs/index.yml`（tracked）/ `logs/raw/<stream-id>/`（gitignore）/ `logs/reports/`（tracked・蒸留物）。`.gitignore` には `logs/raw/` のみ書く |
| F1-5 | dedup キー = `<stream-id>` + `<ts>` + `<session_id または CI の run_id>`。命名権は index.yml の `id` のみ（別の場所で id を再定義しない） |

## F2. 収集器（ラッパー）`scripts/log-tee.py`（priority: critical / lg3p01 B）

| 条件 | 内容 |
|---|---|
| F2-1 | 単一実装・shell 非依存（`python3 \|\| python` の二段 fallback、既存 hook と同型）。cc-cockpit（Windows）を含む 3 リポで同じ 1 本が動く |
| F2-2 | 使い方: `log-tee.py --stream <id> -- <command...>`。index.yml を読み、`<id>` の `store: local` を確認してから `logs/raw/<id>/<ts>-<dedup>.log` に stdout + stderr を tee し、**元コマンドの exit code をそのまま返す**（I-3） |
| F2-3 | raw ファイル先頭に**機械 header 1 行**（JSON: stream id / store / ts / dedup key / command）。後日 header から index.yml を再生成する経路（Council 哲学者案 C）への on-ramp |
| F2-4 | index.yml に無い `--stream` は失敗させる（I-2 の実効化 = 宣言なしに書けない）。ただしラッパー自身の失敗で元コマンドを止めない（記録失敗は warn、判断 ＞ 記録） |
| F2-5 | 配線（同 PR、I-8）: DH = `scripts/test-*.py` の呼出経路、kakuman = `pnpm verify` の既定経路、cc-cockpit = `pnpm run lint` / `test`。CI step にも同じラッパーを噛ませ、`run_id` を dedup に使う |

## F3. 検査スクリプト `scripts/check-log-ledger.py`（priority: critical / lg3p01 付帯）

| 条件 | 内容 |
|---|---|
| F3-1 | **初便は schema 検査に絞る**: 必須 5 列の存在 / 列上限 / `store` 値域 / `store: local` 行の `path` 実在（fresh clone では `logs/raw/` が無いため「親ディレクトリが作成可能」で代替、mkdir で形骸化させない） |
| F3-2 | retention 超過の検出は **dry-run（候補列挙）のみ**。実削除は機能フラグ off で出荷し、次 cycle 以降に人間承認で有効化（DH 初の破壊的自動機械ゆえ可逆性ラダーを守る） |
| F3-3 | `pii` 欄は初版で**検査対象にしない**（none で埋まる儀式化 = TR-4 の再来を避ける。none 以外の値を取る stream が現れた時点で検査対象化） |
| F3-4 | harness-verifier の月次経路に相乗りせず、`pnpm verify` 相当のローカル決定論検査として置く（配布先の `scripts/check-*` 命名規約 = `dh-manifest.yml` upstream scan の対象） |

## F4. 段階 1 の初期集合 = センサー出力 1 stream（priority: critical / lginv1 C）

| 条件 | 内容 |
|---|---|
| F4-1 | 段階 1 で `store: local` にするのは **`sensor-verify` 1 stream のみ**（決定論センサーの stdout + exit code）。棚卸し 22 種の他の行は index.yml に所在行として載せる（`store: db / saas / home`） |
| F4-2 | CI 側（GitHub Actions）の同一センサー実行は**別 stream にせず**、`sensor-verify` の `source` に発生源 2 つ（local / ci）を併記する |
| F4-3 | E2E（playwright 等）の結果は「test の stdout は `sensor-verify` に含まれる」と定義で吸収する。html report は CI artifact の保持（7 日）に任せる |
| F4-4 | `logs/raw/` の rotate 規則を index.yml と同時に決める（typecheck / build の stdout は 1 run 数百 KB になりうる）。初期値は判断点 1 |
| F4-5 | 段階 2（5 種全部への拡張）の昇格条件 = **蒸留 1 回完走 + 参照された実績 1 件**。3 ヶ月で一度も読まれなければ拡張せず縮小する（I-7、経営者少数意見の吸収） |

## F5. 蒸留と読み手の接続（priority: high / Q4-A + I-7）

| 条件 | 内容 |
|---|---|
| F5-1 | 蒸留物 = `logs/reports/YYYY-MM.md`。内容は決定論集計のみ（run 数 / FAIL 数 / 失敗したセンサー名と回数 / 最終 run の日時）。LLM 要約はしない（I-9） |
| F5-2 | 蒸留の実行主体は reindex-librarian の代謝リズムに相乗り（Q4-A）。ただし対象は `logs/raw/` に限り、`history/` の代謝規則（HOT / COLD）は流用しない（I-1） |
| F5-3 | **読み手の接続（I-7 の実効化）**: L0 振り返り儀式（`ritual-protocol.md` F1）の既定ロードに「`logs/reports/` の直近 1 本」を加える。献上前センサー通過（L1 §6）の記録として `logs/raw/` の最新 run を参照できる。これが「読まれた実績」の計測点 |

## F6. DH 側の配線（priority: high / I-8）

| 条件 | 内容 |
|---|---|
| F6-1 | `dh-manifest.yml` `paths.merge` に `logs/index.yml` を追加（DH 雛形 + 配布先の実定義、settings.json と同分類）。`logs/raw/` `logs/reports/` は列挙しない（明示列挙しない = 既定で不可侵） |
| F6-2 | `GRAPH.yml` に `log-tee`（kind: tool）/ `check-log-ledger`（kind: tool）ノードと、`layer1-autonomous-dev → log-tee`（献上前センサー通過）/ `log-tee → layer0-reindex-librarian`（蒸留）のエッジを同 PR で宣言 |
| F6-3 | `.claude/skills/layer0-spec-architect/references/dev-env-spec.md` の templates/rules 節に log-ledger.rules.md を共通 RL として 1 行追記。`scaffold-checklist.md` の共通規約に `logs/` 3 点（index.yml / raw gitignore / reports）を追加 |
| F6-4 | 配布先への適用は `.gitignore` + `package.json`（verify 経路）+ CI を触るため **kakuman では scope:cross-cutting のフル検証**（X-LANE-C）。3 リポ同時ではなく DH → cc-cockpit → kakuman の順に 1 リポずつ |

---

## 実装しないもの（明示的スコープ外・出典付き）

- **独立した台帳文書（手書き logs.yml / README 索引）** — Council lg0903 / lg3p01。telemetry-reflux.yml が 3 リポで 0 件実体化・CHANGELOG 2 ヶ月停止の実測「読み手のいない宣言は書かれない」
- **skill の新設**（`crosscut-log-ledger` 等）— Q5-A。宣言 + 決定論検査で足りる。最小主義ラダー「書かないものが最も可逆」
- **DB / SaaS / transcript の export 取り込み** — 守る線（ops 隔離・2 表分離は「誰が読めるか」の構造解、transcript は読み取り専用 SPEC C11）
- **人間向け UI / ダッシュボード** — Q2-A。人間は明示指示時に HTML で読めればよい（判断キットの経路で足りる）
- **LLM による蒸留・検知** — I-9
- **retention の実削除（初版）** — F3-2。dry-run 先行
- **機械生成物としての index.yml（Council 哲学者案 C）** — 生成元となる stream が未実体化。F2-3 の header 行で on-ramp だけ残す
- **hook-observations.jsonl との統合** — I-1。開発ログ側に留める
- **Q10（kakuman に harness-verifier ツールが無い）** — ログ層の外。DH 資産の配布範囲の別議題

## 判断点（人間レビューで確定するもの）

1. F4-4 `logs/raw/` の rotate 初期値 — 提案: **stream ごと直近 30 run または 50 MB の小さい方**（超過分は dry-run 候補に載せる）
2. F5-2 蒸留の契機 — 提案: **cycle 完了時（retrospective と同時）+ 月次**のどちらでも走る冪等スクリプト。cron は DH 本体のみ
3. F3-3 `pii` 欄の検査対象化の時期 — 提案: 段階 2 の起動時
4. 版番号 — v6.16.0 仮置き。Q9-A（VERSION 整合 PR）を先に通すか、本 spec と同梱するか
5. 「Council で決めて」の委任で推奨がそのまま決定になった 3 諮問（lg0903 / lg3p01 / lginv1）を、本 spec の人間レビューで**改めて目視承認**するか（哲学者軸の懸念: 第 6 条の形式化の兆候）

> 実装順序（提案）: PR-A = F1 + F2 + F3 + F6（DH 本体・雛形と道具）→ PR-B = cc-cockpit 適用（Windows で F2-1 を実証）→ PR-C = kakuman 適用（cross-cutting）→ F5 は PR-A に含めるが読み手接続（F5-3）は ritual-protocol 改訂ゆえ規範文書改変として個別に献上。

## 申し送り

- 段階 2（5 種全部）: 棚卸し表の `store: db / saas / home` 行を段階 1 の所在行として持ち越し、昇格条件（F4-5）を満たした時点で再諮問
- telemetry-reflux（v6.15.0 F4）との接続: `logs/reports/` の FAIL 数を signal-scan の検知器 (e)「ローカルセンサー連続 FAIL」として追加可能な形にしておく（宣言のみ、実装は段階 2）
- Q8-B（ブレストメモの置き場を `delivery/ANALYSIS-*` に統一）: kakuman 側は skill 2 本（AI 不可侵）の人間改訂が先。l0-pre-brainstorm の DH 昇格と同時に扱う
- Q9-A（VERSION drift）: 別 PR。VERSION vs upgrade-spec の状態欄の対応表を先に献上
- Q10: kakuman に harness-verifier（verify.py / 月次 reports）を配布するかは DH 資産の配布範囲の議題として別建て
