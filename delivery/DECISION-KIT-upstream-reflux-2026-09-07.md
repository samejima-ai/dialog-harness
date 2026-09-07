# 還流採否キット 0907 — kakuman → DH の還流候補 残り 4 件（Markdown 正本）

> HTML 視覚版（採用/保留 + 回答まとめコピー）: https://claude.ai/code/artifact/2d296ef6-ade6-43d0-bfdf-92fe495aa8a2
> spec: `delivery/decision-kits/2026-09-07-upstream-reflux.json`
> 記入先の正本: `delivery/UPSTREAM-DECISION-2026-08-26.md`（改訂版・PR #268）
> 判定: `history/COUNCIL-LOG.md` `council-2026-09-07T12:00:00Z-upst03`（jc 0.78）
> 上流: `samejima-ai/kakuman-platform-v3.0` @ `9bbc642`
> 局面: **人間専管**。AI は記入欄を代筆しない。

## 待ちの分類

| 主体 | 件数 | 内容 |
|---|---|---|
| 人間専管 | 4 問 + cron 1 問 | 設問 1〜4（本キット）／ signal-scan の cron |
| AI 単独可（回答後） | — | 採用分の実装（Q4 の `permissions.deny` 汎用分など） |
| 待機 | — | 回答が返るまで還流の実装は行わない |

## なぜ形式を変えたか

初版は「人間が答えるのは 1 問だけ」を設計意図とし、順位表 + カットライン 1 問に圧縮した。

| 実測 | 値 |
|---|---|
| 記入欄が空欄だった期間 | **12 日** |
| その間に別経路で着地した件数 | **3 / 7 件** |
| 先に着地した初版順位 | **3 位・4 位** |
| 残った初版順位 | **1 位** |

実装が進んだのは推奨順ではない。**順位という前提そのものが成立していなかった。**

初版が Council 実測由来で注記した「項目 2 は項目 1 に依存する（述語化前に FAIL 昇格すると CI が止まる）」も
実装で反証された — F6 は母集合を `templates/rules/common/*.md` の glob で機械定義しており、
項目 1 の述語化を前提としない。

> 順位は出来事同士を比較可能な量に還元する操作であり、比較した瞬間に「なぜそれが必要だったか」が
> 剥落する。1 問への圧縮は判断コストを下げたのではなく、**7 つの出来事を 1 つのスカラーに潰して
> 判断を不可能にした**。

## 還流済み — シートを迂回して着地した 3 件

| 初版順位 | 機構 | 経路 |
|---|---|---|
| 2 | 規範の分割不変条件 `check-traps-sync.mjs` | v6.17.0 F6 → `harness-verifier/checks/rules_index.py`（PR #258）。v6.18.0 C-2 で独立モジュール化（PR #264） |
| 3 | 観測層の非ゲート化 `observe.yml` | `.github/workflows/signal-scan.yml`（v6.15.0 F1）。**思想がファイル冒頭にそのまま書かれている** |
| 4 | 配置と武装の分離 `schedule:` コメントアウト | **思想のみ未採用**。cron は日次で有効。→ 設問 4 に統合 |

## 問い（全文は spec JSON / HTML）

| 設問 | 機構 | 初版順位 | 事故 | DH の現況（2026-09-07 実測） | 所要 |
|---|---|---|---|---|---|
| 1 | 領域ゲートの述語化 `check-routing-gates.mjs` | 1 | 2026-08-05 G-FEED の初の実地 false positive | 未着手。`GRAPH.yml` に `predicate` **0 件** | 3 分 |
| 2 | 武装解除の明示 fail `rls-drift.yml` | 5 | 2026-06-11 本番 RLS ドリフト（24 テーブル） | 機構は `upstream-scan.py` に自己適用済み。**規範化のみ未** | 2 分 |
| 3 | 購読量の CI 強制 `check-spec-size.mjs` 他 | 6 | 2026-08-20 SPEC.md 1.02MB に size センサー無し | 未着手。`scripts/` に size 検査は無い | 3 分 |
| 4 | 不可逆操作の deny 強制 `.claude/settings.json` | 7 | 事故なし（14 件を予防的に deny） | ファイルは PR #209 で存在。**`permissions` 節が無い** | 3 分 |

**設問 4 には初版の項目 4（配置と武装の分離）を統合した。** `signal-scan.yml` の cron は現在日次で
有効化されており、Actions 消費枠の意思決定が AI 側に移った状態にある。

選択肢はすべて `採用` / `保留` の 2 択。設問 4 のみ `signal-scan の cron: 現状維持 / 無効化して人間が武装する` を併記。

## 判定 — weighted_score に従わなかった

Council `upst03` / jc 0.78 / `reason_divergence`（dimension 重複なし）

| 軸 | stance | conf | 重み | dimension |
|---|---|---|---|---|
| 経営者 | B | 0.82 | 4 | 機会損失 / 律速資源配分 |
| 開発者 | B | 0.82 | 4 | 可逆性 / 配布境界の整合 |
| 哲学者 | 第3の道 | 0.72 | 3 | 前提への問い |

`weighted_score` は **B（設問 4 の `permissions.deny` を AI が先行実装する）が 6.56 対 2.16** で支配的だったが採らなかった。

開発者軸は B の技術的前提を実測で確認している — `dh-manifest.yml:81-83` が `.claude/settings.json` を
**`merge` 分類**（`overwrite` ではない）と宣言しているため配布先へ raw 上書きされず、I-6 と衝突しない。
可逆性も最高である。しかし哲学者軸がその前提を否定した:

> 7 件中 3 件が既に別経路で消えている以上、残りも AI が削れば、人間が答えるべき問いは
> 消滅によって解決されたことになる。それは第 6 条の充足ではなく回避である。

**可逆なのは実装であって、問いの消滅は可逆ではない。**

**D（決定シートを廃し signal-scan の検知対象へ移す）は 3 軸が独立に否定。** `signal-scan.yml` ヘッダ自身が
記録する F8 事故（日次 cron の dedup 破れで 2026-08-28〜09-05 に同一 3 PR で 27 件の重複 Issue）が
I-4 / TR-4 違反を実証し、`dh-manifest.yml` U-4 が upstream 走査に「優劣判定はしない」を課している。

## 副産物 — 決定待ち文書は制度の外に落ちる

`scripts/norm-scan.py:58` が `delivery/` を「分析・献上物。規範ではない」として時限走査から除外しており、
**本シートは検知の死角に置かれていた**。`ANALYSIS-silent-failure-2026-09-06.md` §7 が
「本分析も静かに失われうる」と書いた予言は、**同じディレクトリの隣のファイルで既に成就していた**。

さらに走査母集合が分裂していた:

| | `norm-scan.py` | `signal-scan.py`（修正前） |
|---|---|---|
| 拡張子 | `.md` `.py` `.yml` `.yaml` | `.md` `.yml` `.yaml` |
| 除外 | `dh-upgrades/` `history/` `delivery/` | なし |

C-1 で `norm-scan` に `*.py` を足した際に `signal-scan` が取り残され、**検査モジュール 7 件
（#264 で分割した 4 本を含む）の期限宣言が滞留検知の死角**にあった。PR #268 で是正（母集合 23 → 31）。

**除外規則は意図的に共通化しない。** `norm-scan` は「現行規範の時限」を読むので `delivery/` を除外し、
`signal-scan` は「滞留」を見るので除外しない。決定待ち文書は規範ではないが腐る — これが第三のカテゴリである。

**空欄 12 日は静かな失敗の型 A/B/C のいずれでもない。** 型 A-C はすべて機構の側の不作動を見ているが、
本件は機構が正常に動作し、正しく人間に届き、それでも動かない。原因は不作動ではなく問いの形式の
誤りであり、検知器では原理的に拾えない。

## 事実の出所

- 事故の日付・解いた問題: kakuman のソースコメントおよび `delivery/` 文書からの**転記**（U-5。AI の推定を含まない）
- DH 側の現況: 2026-09-07 に `GRAPH.yml` / `scripts/` / `.claude/settings.json` / `.github/workflows/` を再走査
- 走査母集合の分裂: `scripts/norm-scan.py:85` と `scripts/signal-scan.py:91`（修正前）を突合
- 配布分類: `dh-manifest.yml:81-83`
- 一次ソース行番号: `delivery/UPSTREAM-DECISION-2026-08-26.md` §出典

## 記入後の手順

1. `scripts/upstream-scan.py --prev` で `UPSTREAM-CANDIDATES-2026-08-26.md` の採否欄へ反映
2. 採用分が Phase 2 / Phase 3 のスコープを確定させる（Council `council-2026-08-26T01:53:40Z-v7ord1` の完了条件）
3. C-3 完了時に `VERSION` を 6.18.0 へ昇格（現在 6.17.0 に据え置き）

## 決定記録（人間回答後に追記）

| 設問 | 決定 | 次に AI がすること |
|---|---|---|
| 1. 領域ゲートの述語化 | | |
| 2. 武装解除の明示 fail | | |
| 3. 購読量の CI 強制 | | |
| 4. 不可逆操作の deny 強制 | | |
| signal-scan の cron | | |

## 規範メタデータ

```yaml
stage: 全段階
review_trigger:
  - date: 2026-10-07
  - measured: 設問形式を改めた後も 30 日以上記入されなければ、順位表に代わる形式（1 件 = 1 出来事カードの Issue 化）を再問する
```
