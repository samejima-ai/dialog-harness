# ANALYSIS: DH ハーネス送出性能の世界水準ベンチマーク — 何が比較でき、何が比較できないか

> **本文書は実測とその解釈である。仕様変更ではない。決定は D5。**
> 起点: ひでさん発話「DH のハーネス性能を世界基準でベンチマーク検証してください」（2026-08-30）。
> 先行の `ANALYSIS-agentic-sdlc-world-standard-2026-08-28.md` は**能力の有無**（✓/△/✕）を照合した。
> 本文書はその続きで、**実際に出た成果物を数える**。§2-C が「G2 = gh api だけで計算可能なのに未実装」
> と名指しした空白の充足にあたる。
> 計測: `scripts/harness-benchmark.py`（git のみ・LLM 判定なし）/ 回帰テスト 33 checks。

| 項目 | 内容 |
|---|---|
| 対象 | `samejima-ai/dialog-harness` の closed PR 184 件（うち agent PR 171 / merged 165） |
| 期間 | 2026-04-18 〜 2026-08-30（133.8 日） |
| 参照系 | DORA（four keys + rework rate）/ dotnet/runtime Copilot coding agent 10 ヶ月実測 |
| 結論の要旨 | **フロー指標は世界水準の上位帯。受入指標は世界水準と比較不能。** 後者は DH の品質が測れないという意味であって、高いという意味ではない |

---

## 0. 要旨

1. **フロー指標は上位帯にある**（比較可能）: merge 頻度 1.23/日、lead time 中央値 **18.5 分**、98.8% が 1 日以内。DORA が Elite クラスタを検出した年の目安（lead time 1 日未満・オンデマンド deploy）を満たす
2. **受入指標（W9）は比較してはいけない**: merge 率 96.5%（参照 67.9%）/ human-commit 介入率 1.8%（参照 45%）。数字は良く見えるが、**参照系は全 PR が人間レビューを通る系での値**で、DH は opt-out auto-merge により人間が触らないのが既定。**負例を生む制御点がプロセス上に存在しない**
3. **レビュー窓が物理的に存在しない**: PR open → merge の中央値 **13.4 分**、**31.5%（52/165）は 5 分未満**で merge されている
4. **rework rate 10.9% が唯一の使える品質指標**: 後続の fix/revert PR が当該 PR 番号を明示参照した比。**成果物から導くため負例が観測でき**、自己申告フィールドにも人間ゲートにも依存しない
5. 本セッションで 3 例目の同型パターン: **DH の自己計測は、自己申告と人間ゲートに依存する指標がすべて天井に張り付き、成果物から導く指標だけが判別力を持つ**

---

## 1. 計測方法 — `gh` 無しでどう測ったか

`scripts/pr-audit.py`（v6.15.0 F2、G2 の実装）は既に W9 を実装済みだが **`gh` CLI を要求**し、
本セッションの実行環境には `gh` が無い。代替として GitHub が公開する PR head ref を使った:

```
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'
```

これで **190 本の PR head** がローカルに揃う。DH は squash merge を使うため master 側からは
PR の元 commit 列が失われている（1 PR = 1 commit に潰れる）が、head ref にはそれが残っている。
結果、commit 単位の agent/human 判定・PR サイズ・初 commit 時刻が**全てオフラインで**取れた。

> **この差は結果を変える。** 最初に master の squash commit だけで計算したとき、
> merge 率 = 1.000 / human-commit 率 = 0.000 になった。squash が commit 単位の情報を破壊し、
> かつ「master に squash commit がある」＝「merged」なので**分母に不採用 PR が入り得なかった**ため。
> head ref を取ると merge 率 96.5% / human-commit 率 1.8% になり、不採用 6 件が可視化された。
> 計測経路が指標を作る例として記録しておく。

## 2. フロー指標 — 比較可能な部分

人間ゲートの有無に依存しないため、他組織と直接比較できる。

| 指標 | DH 実測 | 参照（DORA） |
|---|---|---|
| deployment frequency | **1.23/日**（8.6/週・165 merge / 133.8 日・稼働 46 日） | Elite = オンデマンド（1 日複数回） |
| change lead time（初 commit → merge） | **中央値 18.5 分** / p90 3.5 時間 / 1 日以内 98.8% / 1 時間以内 73.3% | Elite = 1 日未満 |
| deployment rework rate | **10.9%**（18/165） | DORA が 5 指標へ拡張時に追加。固定閾値の公表は無い |
| failed deployment recovery | **中央値 0.9 時間** / 24 時間以内 77.8% | Elite = 1 時間未満 |

**注意（DORA の読み方）**: DORA のクラスタ境界は**毎年の cluster analysis で再導出される相対値**であり、
固定閾値ではない（2022 年は Elite クラスタ自体が検出されなかった）。上記「Elite =」は
クラスタが検出された年（2021 / 2023 / 2024 断面）で広く引かれる目安であって、恒久的な合格線ではない。

**DH 側の代理定義**（正直に明示する）:

- **deployment = master への merge**。DH は repo として配布されるハーネスであり、別立ての deploy 工程が無い。merge ≒ リリース
- **lead time = PR ブランチの初 commit → merge**。DORA は commit → 本番稼働。AI 実装ではブランチ作成が着手時刻にほぼ一致するため、実測はタスク所要時間に近い
- **稼働 46 日 / 133.8 日**。1 人運用ゆえ非稼働日が多い。稼働日のみで見ると中央値 3 merge/日

## 3. 受入指標（W9）— **比較不能**

| 指標 | DH 実測 | 参照 (dotnet/runtime) |
|---|---|---|
| merge 率 | 96.5%（165/171） | 67.9%（535/878） |
| revert 率 | 0.0%（0/165） | 0.6%（3/535・人間ベースライン 0.8% を下回る） |
| human-commit 介入率 | 1.8%（3/165） | 45% |

**この 3 行を「DH の勝ち」と読んではならない。**

参照系の 67.9% / 45% は、**全 PR が人間レビューを通り、人間が不採用にでき、人間が直接 commit を
積める**プロセスの下で観測された値である。67.9% という数字は、32.1% が人間によって落とされた
という**制御点の働きの記録**であり、45% は人間が手を入れた記録である。

DH は `auto-merge.yml` により **opt-out**（stop ラベルが無ければ自動 squash merge）を採る。
これは `ANALYSIS-agentic-sdlc-world-standard-2026-08-28` §1 が「W1 に対する意図的逸脱」として
既に記録しているとおり、業界標準（agent の自律はマージ手前で必ず切れる）からの明示的な離脱である。
その帰結として、**不採用と人間介入を生む制御点がプロセス上に存在しない**。

したがって:

- merge 率 96.5% は「96.5% が良かった」ではなく「**落とす主体が居ない**」
- human-commit 率 1.8% は「直す必要が無かった」ではなく「**直す人が見ていない**」

`harness-benchmark.py` はこの区別を出力上も維持する（`comparable: false` を立て、参照値を
`reference_display_only` として判定に使わない）。指標を良い方向へ読む圧力に対する機械的な歯止めである。

### 3-1. 制御点の不在は直接観測できる

| レビュー窓（PR open → merge） | 件数 | 比率 |
|---|---|---|
| 2 分未満 | 39 | 23.6% |
| 5 分未満 | 52 | **31.5%** |
| 15 分未満 | 91 | 55.2% |
| 1 時間未満 | 131 | 79.4% |
| 中央値 | — | **13.4 分** |

人間が diff を読む下限を 5 分と置けば、**約 3 分の 1 の PR は人間レビューを経ていない**（中央値 13.4 分の
PR も、その間に CI 完走を待っていることを踏まえると実質のレビュー時間はさらに短い）。
これは欠陥ではなく設計どおりの動作である — auto-merge は stop ラベル不在を暗黙承認とみなす。
ただし**その設計の下では W9 指標は情報を持たない**、というのが本節の結論である。

## 4. rework rate — 唯一「負例が観測できる」品質指標

後続の fix/revert PR が、先行 PR の番号を**本文で明示参照**した場合のみ手戻りと数える。

| 版 | 定義 | 値 |
|---|---|---|
| loose（上界） | merge 後 14 日以内に同一ファイルを触る fix/revert がある | 46.1%（76/165） |
| **strict（採用）** | 後続 fix/revert が**当該 PR 番号を明示参照** | **10.9%（18/165）** |

loose を採らない理由: 小規模 repo では大半の PR が同じコアファイル（`SKILL.md` / `SPEC.md` /
`GRAPH.yml`）に触れるため、ファイル重複はほぼ自動的に成立し過大計上になる。
strict は下界だが誤検出がほぼ無い。**真値は 10.9%〜46.1% の間**にあり、下界を採用値とする。

- 修復時間: 中央値 **0.9 時間** / p90 46.6 時間 / 24 時間以内 77.8%
- 連鎖の実例: `#123 #124 #126 #127 #128 → #129`（5 PR をまとめて 1 fix が修復。数時間内）

**この指標が特別な理由**: merge 率も human-commit 率も CTL の agreement_rate も、
「人間または AI が記録したフィールド」または「人間ゲートの通過記録」に依存する。
rework rate は**後から実際に fix PR が出たという事実**から導かれる。誰の申告も要らず、
auto-merge であろうと人間レビューであろうと同じように観測できる。
DH の品質を語る主指標はここに置くのが妥当である。

## 5. 本セッションで 3 例目 — 同型パターンの一般化

| # | 指標 | 値 | 負例の生成経路 |
|---|---|---|---|
| 1 | Council `agreement_rate`（CTL 入力） | **1.000** | `modified` / `rejected` が 67 発動で 0 件 |
| 2 | agent PR `merge 率` / `human-commit 率` | **96.5% / 1.8%** | 落とす主体・直す主体がプロセス上に不在 |
| 3 | Council 無修正採択率 | 0.788 | 記録された結果の切り方から導く（判別する） |
| 4 | deployment rework rate | 10.9% | 後続 PR の実在から導く（判別する） |

**規則性**: DH の自己計測は、**自己申告フィールドと人間ゲートに依存する指標がすべて天井に張り付き、
成果物（diff・後続 PR）から導く指標だけが判別力を持つ**。

これは偶然ではない。DH は「人間の関与を減らす」ことに成功しており、その成功が
**人間の関与を測定基盤にしていた指標を無効化している**。自律度を上げるほど、
自律度を評価する従来指標が使えなくなる、という構造がある。

`ANALYSIS-agentic-sdlc-world-standard-2026-08-28` §W9 は「計測の重心は生成量から受入率・介入率・
revert 率へ」と業界動向をまとめたが、**その 3 つはいずれも人間ゲートを前提とする指標**である。
DH のように人間ゲートを外した系では、業界がいま重心を置いている指標が丸ごと使えない。

## 6. 提案（提案に留め、判断は D5）

1. **rework rate を主指標に昇格させる** — `harness-benchmark.py` が既に算出する。月次 `harness-verify` に載せれば継続観測になる。**目標値化はしない**（Goodhart 回避 = pr-audit I-4 と同じ規律。fix PR に先行 PR 番号を書かなくなるだけで下がる指標である点に特に注意）
2. **W9 を「参照系と比較しない指標」として明示的に降格する** — 廃止ではない。opt-in 領域（`auto-merge-boundary.md`）に該当した PR だけを母集団にすれば、その部分集合では人間ゲートが実在するため W9 が意味を回復する。**母集団を分ける**のが正しい直し方
3. **レビュー窓を観測項目に加える** — 5 分未満 merge 比率は、auto-merge 境界が想定どおり効いているかの直接指標になる。opt-in 領域の PR がこの比率に混ざっていたら境界の破れである
4. **2026-11-06 の auto-merge roll-back ゲートに本実測を入力する** — 先行分析が「逸脱の妥当性検証」と位置づけたゲート。rework 10.9% / revert 0% / 修復中央値 0.9h が、その判断材料の一次データになる

## 7. 限界

- **n=165、単一 repo、単一運用者**。DORA の母集団（多組織サーベイ）や dotnet/runtime（878 PR・多人数）と統計的性質が違う。帯の当てはめは目安であって順位づけではない
- **lead time はブランチ作成起点**。仕様検討（L0 対話）の時間は含まない。DH の実作業の相当部分が対話にあることを踏まえると、実際のリードタイムはこれより長い
- **rework strict は下界**。10.9% と 46.1% の間のどこが真値かは、本文書では決めていない
- **revert 0% は運用の反映**でもある。DH は revert より前方修正（fix PR）を採るため、revert 率は品質ではなく修復様式を示す。dotnet/runtime の 0.6% と同列に置けない
- 「AI 自律開発ハーネス」の性能を測る**業界標準ベンチマークは存在しない**（先行分析 §4 の注記どおり、自律度の標準指標は未確立）。本文書は既存の SDLC 指標を転用したものであって、確立された benchmark suite への提出ではない

## 8. 再現手順

```
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'
python3 scripts/harness-benchmark.py --states <PR 状態 JSON>
python3 scripts/harness-benchmark.py --json
python3 scripts/test-harness-benchmark.py     # 33 checks
```

`--states` は `gh pr list --state closed --json number,title,body,createdAt,mergedAt` または
GitHub MCP `list_pull_requests` の出力（camelCase / snake_case 両対応）。
省略時は master の squash commit から merged PR のみを復元する（**不採用 PR が見えないため
merge 率は使えない** — §1 の教訓）。

## 出典

- [Ten Months with Copilot Coding Agent in dotnet/runtime — .NET Blog](https://devblogs.microsoft.com/dotnet/ten-months-with-cca-in-dotnet-runtime/)（878 PR / 535 merged = 67.9%、revert 3/535 = 0.6%、人間ベースライン 0.8%）
- [DORA | DORA's software delivery performance metrics](https://dora.dev/guides/dora-metrics-four-keys/)（four keys + rework rate への拡張）
- [DORA | A history of DORA's software delivery metrics](https://dora.dev/insights/dora-metrics-history/)（クラスタは年ごとに再導出・2022 年は Elite 不在）
- [DORA | Accelerate State of DevOps Report 2024](https://dora.dev/research/2024/dora-report/)
- 先行分析: `delivery/ANALYSIS-agentic-sdlc-world-standard-2026-08-28.md`（W1 / W9 / G2）
- 境界仕様: `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md`
