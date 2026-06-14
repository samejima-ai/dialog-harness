# delegation boundary — 権限委譲の不変境界（可逆性ベース）

> v6.0.0 で導入。dialog-harness 自身の権限構造を「重大事象のみ人間が判断、9 割は AI 自律」へ
> 反転するにあたり、**AI が動かせない不変境界**を定義する。`auto-merge-boundary.md`（PR 単位の
> merge 境界）の上位概念にあたる「**harness 全体の委譲境界**」であり、両者は同型で連結する。

Council 諮問 `council-2026-06-14T-delgbd`（business / category=conception / phase_1 / unanimous /
案C ハイブリッド境界 SPEC / weighted_score 7.80 / judgment_confidence 0.72）の判定と、その 6 必須
制約条件・哲学者 minority_opinion（段階性）に基づく。

---

## 0. 線の引き方 — 可逆性が唯一の判定軸

委譲してよいかは**「原状回復できるか」だけ**で決める。権限の重大さ・領域の格ではなく、**revert /
修正で原状回復が原理的に可能か**を問う。これは Council 3 ペルソナ（経営者=リスク / 開発者=可逆性 /
哲学者=倫理）が独立に同じ結論へ収束した唯一の軸である。

```
原状回復が可能 → 委譲（実行 → 出力後修正で拾う）
原状回復が原理的に不能 → 委譲しない（事前ゲート / 人間専管で固定）
```

「9 割は推奨でいい」という観測は **可逆領域に限って**「だから委譲してよい」を含意する。
無関心は同意ではない（哲学者）。沈黙が承認に化けてよいのは、後から取り消せる出力に限られる。

---

## 1. 委譲レベルの 4 分類

| レベル | 領域 | 委譲 | 拾い方 | 根拠 |
|--------|------|------|--------|------|
| **L-FULL 全自律** | コード / テスト / docs / `history/` / `delivery/` / **SPEC.md・DONT.md の通常改変（枠内）** | 実行 → PR 作成まで無言で走る | **出力後修正**（PR diff を人間が見て修正 / revert） | revert で原状回復可能 |
| **L-GATE 事前ゲート** | 不可逆操作（DB migration / データ削除 / `git push --force` 保護ブランチ / secrets 削除 / 外部 API 破壊変更） | **PR 作成前に発話確認**し `human-review-needed` 付与 | 事前に止める | revert 不能（開発者 concern②） |
| **L-FROZEN-PHIL 段階固定** | `philosophy.md`（憲法）の改訂 + **DONT.md の禁止境界の定義変更**（H2・「何を禁じるか」の線引き変更） | **人間専管**（2026-11-06 roll-back ゲート後に再諮問するまで AI 提案 PR も不可） | 人間が起票 | 段階性 / 委譲線変更（哲学者 minority + 利用者判断） |
| **L-FROZEN-META 不変固定** | 委譲境界 SPEC 自身：**本ファイル `delegation-boundary.md`** + `auto-merge-boundary.md`（+ `philosophy.md` は L-FROZEN-PHIL として AI 起票禁止を共有・段階固定ゆえ別区分） | **人間専管・恒久固定** | 人間のみ | 「止める基準そのもの」（哲学者）／自己改訂禁止 |

> **L-FROZEN-PHIL と L-FROZEN-META は共に AI 起票禁止（§2 の 3 文書）。差は緩和余地**: philosophy.md
> （L-FROZEN-PHIL）はゲート後に L-GATE へ緩和されうる段階固定、本ファイルと auto-merge-boundary.md
> （L-FROZEN-META）は恒久固定。§2 が 3 文書を一括で「L-FROZEN」と呼ぶのは「AI 起票禁止」の共通性を指し、
> 緩和余地の差（恒久 vs 段階）で 2 区分に分かれる。

### L-FULL の拡張点（v6.0.0 の核心反転）

v5.9.0 までは `SPEC.md` / `DONT.md` 改変は opt-in 領域（事前ゲート）だった。v6.0.0 で **通常改変（枠内）を
L-FULL へ移す**。理由: 機能追加・修正に伴う仕様追記や既存禁止境界の枠内での個別項目追加は PR diff として
可視化され revert 可能（可逆領域）であり、可逆性ベースの線引きでは全自律側に属す。ただし下記 §3 の
churn 防止・squash 前提・独立レビュー担保を満たすこと。**DONT.md の禁止境界そのものの定義変更**（「何を AI に
禁じるか」の線引きを動かす書き換え）は L-FULL ではなく L-FROZEN-PHIL（H2・委譲線の変更ゆえ人間専管）。

### L-FROZEN-PHIL と L-FROZEN-META の違い

- **L-FROZEN-PHIL（philosophy）は段階固定**: 2026-11-06 の roll-back 評価ゲート（v5.9.0 auto-merge 反転の
  経験的検証）が完了し、Council 再諮問で承認されれば **L-GATE へ緩和される可能性がある**（AI 提案 PR + 人間 merge）。
  今回広げないのは、v5.9.0 反転の検証が未完のまま次の不可逆段を踏まないため（第 8 条 観測フェーズの尊重）。
- **L-FROZEN-META（境界 SPEC 自身）は恒久固定**: 委譲線を定義するファイル自身を AI が動かせると、AI が
  自分の権限を自分で広げられる（自己参照の崩壊）。これは roll-back ゲートに関わらず**恒久的に人間専管**。

---

## 2. 憲法の自己改訂禁止（第 6 条本文へ刻む不変条項）

**dialog-harness は、自らの委譲境界を定義する文書を自ら改訂できない。**

- `philosophy.md`（憲法 = 何が H カテゴリ＝人間専管かを定義する）
- `delegation-boundary.md`（本ファイル = 委譲線を定義する）
- `auto-merge-boundary.md`（PR 単位の merge 境界を定義する）

これら 3 文書の改訂は AI が提案 PR すら作らない（L-FROZEN）。理由は再帰の遮断にある:

```
AI が「何を人間が握るか」を定義する文書を改訂できる
  → AI が「止める基準そのもの」を書き換えられる
  → merge ブロックを人間が握っていても、止め忘れ 1 回で基準が変質し
    その後は「revert すべきと判断する基準」が既に変わっている
  → 可逆性が原理的に成立しない（revert しても元の判断軸へ戻れない）
```

merge ブロックは「止め忘れ」に脆弱である（哲学者）。可逆性が成立しない領域では、merge ゲートではなく
**起票ゲート**（PR を作る段階で人間専管）で止める。これが第 8 条「採用判断は AI 禁止」の哲学的延長である
（第 9 条で憲章化）。

---

## 3. L-FULL 運用の必須制約条件（Council 6 条件）

L-FULL（全自律）を安全に運用するための不変制約。1 つでも欠けると委譲は情報損失コストに見合わない。

| # | 制約 | 出典 | 実装 |
|---|------|------|------|
| C-1 | **境界改訂権は人間専管・SPEC 不変化 + roll-back 閾値で機械監視** | 経営者 | §1 L-FROZEN-META / §5 監視 |
| C-2 | **opt-in 縮小は revert 不能な不可逆操作のみに限定。local 全自律は squash 前提** | 開発者 | §1 L-GATE / §4 local |
| C-3 | **境界 SPEC 改訂判定の独立性を別途担保**（self-review の罠回避） | 開発者 | §3.1 |
| C-4 | **決定論検査（harness-verify / 型 / lint / test）を確率的 sub_agent_review で置換しない** | 開発者 | §6 CI |
| C-5 | **レビュアー誤判定率の月次計測を roll-back 指標へ追加** | 経営者 | §5 監視 |
| C-6 | **「憲法の自己改訂禁止」を第 6 条本文へ明文化し第 8 条の哲学的延長に位置づける** | 哲学者 | §2 / philosophy 第 6・9 条 |

### 3.1 独立性の担保（C-3 — self-review の罠）

L-FULL で AI が SPEC/DONT を改変する PR を作るとき、**実装した AI 自身がレビュアーを兼ねると第 3 条
（実装者 ≠ 独立レビュアー）が崩壊する**。担保策:

- SPEC/DONT 改変 PR は `claude-review.yml`（独立コンテキストの sub_agent review）を**必ず通す**
  （paths フィルタに SPEC/DONT を含める）。実装コンテキストを持たない別 agent が照合する。
- レビュアーが L-GATE / L-FROZEN 該当を検知したら、その PR を昇格させ `human-review-needed` を付与する。
- 境界該当の判定が曖昧なときは**重大側（より人間寄り）に倒す**（fail-safe、第 6 条 人間最終承認）。

---

## 4. local / github の分離 — 権限差ではなく検証手段差

**権限委譲度は local / github で同一（どちらも L-FULL 全自律）。** 違いは検証手段にのみ宿る。

| 環境 | 検証手段 | 全自律の範囲 | 制約 |
|------|----------|--------------|------|
| **local** | hook（PreToolUse / PostToolUse）+ lint + 型 | commit まで無確認で走る | **squash 前提**（誤 commit を git 履歴に永続させない・C-2） |
| **github** | sub_agent_review（claude-review / gemini-review）+ 軽量機械 CI | PR 作成 → auto-merge まで | §6 の CI スリム化方針に従う |

- local が「commit まで無確認」で走れるのは、commit が**ローカルで revert/amend/squash 可能**な可逆操作だから。
  push して公的空間（他者・将来の目に触れる）に出た時点で sub_agent_review を必ず通す。
- squash 前提の含意: 自律走行中の試行錯誤 commit 列は、PR 化（push）時に squash で 1 つの論理単位へ畳む。
  誤 commit・WIP・revert 往復が公的履歴を汚さない（開発者 concern④）。

---

## 5. roll-back 監視（v5.9.0 指標 + v6.0.0 追加）

v6.0.0 の委譲拡大は **2026-11-06 の roll-back 評価ゲート**（auto-merge-boundary.md と同一日）で
v5.9.0 反転と合わせて評価する。指標:

| 指標 | 閾値 | 出典 | 検知主体 |
|------|------|------|----------|
| 暗黙 merge 事故件数 | 1 件以上で要再評価 | v5.9.0 哲学者懸念 | 人間（事後監視） |
| AI 判定漏れ率（L-FULL 判定すべきを L-GATE 見落とし / 逆も） | 5% 超で要再評価 | v5.9.0 メタ承認機構 | メタ承認機構（手動） |
| 境界曖昧化事例 | 月 2 件以上で要再評価 | v5.9.0 経営者懸念 | 人間（事後監視） |
| **レビュアー誤判定率**（sub_agent_review が L-GATE/L-FROZEN を見逃した率） | 月次計測、5% 超で要再評価 | **v6.0.0 経営者 C-5** | claude-review 出力の事後突合（手動、PR3 で sensor 化候補） |

いずれか閾値超過で roll-back ゲートを起動し、**L-FULL へ移した SPEC/DONT 改変を L-GATE へ戻す**等の
段階的縮退を検討する（philosophy.md 改修を伴う場合は L-FROZEN-PHIL ゆえ人間専管で起票）。

評価指標すべて閾値未満なら継続、1 年後（2027-06-14）に再評価ゲート。本ファイルに `evaluation_history`
セクションを append-only で残す。

---

## 6. CI スリム化方針 — 決定論は残し、判断は sub_agent へ

「CI を削除して sub_agent_review に転換」の正確な内実は **判断の集約であって、決定論検査の廃止ではない**
（C-4）。第 2 条「計算的解決を最優先」に従い、決定論で解ける検査を確率的レビューで置換してはならない。

| 検査 | 帰属 | 残す / 移す | 根拠 |
|------|------|-----------|------|
| 型チェック / lint / test | **CI に残す**（第 2 条 第 1 層 計算的センサー） | 残す | 決定論・低コスト・C-4 |
| `harness-verify.py`（構造健全性） | **CI に残す**（D4 本体の生命線・auto-merge 条件 4 のゲート） | 残す | 決定論・代替不能・C-4 |
| コード品質（命名 / 重複 / 簡潔性） | **sub_agent**（claude-review 4 フェーズ） | 移す（既存） | 推論的判断 |
| 仕様合致（SPEC/DONT 整合） | **sub_agent**（gemini-review 仕様軸） | 移す（既存） | 推論的判断 |
| Council 判断（拮抗 / 不可逆 / 矛盾） | **sub_agent**（review-persona-* + review-judgment） | 移す（既存） | 合議判断 |

sub_agent_review 基盤（claude-review.yml 4 フェーズ + `.claude/agents/review-*.md` 8 個 + gemini-review）
は v5.26.0 で既に完成・稼働中。v6.0.0 は新規構築せず、**CI に残す決定論検査の範囲を明文化**するに留まる。

---

## 7. 実装で参照する箇所

| ファイル | 参照内容 |
|---------|---------|
| `philosophy.md` 第 6 条 | §2「憲法の自己改訂禁止」を本文へ刻む |
| `philosophy.md` 第 9 条（新設） | §0 可逆性ベースの委譲境界原則を憲章化 |
| `auto-merge-boundary.md` | PR 単位 merge 境界の上位概念として本ファイルへ接続（opt-in 領域 ⊇ L-GATE+L-FROZEN）。`auto-merge-boundary.md` が独自に課す件数依存制約（例: 3 ファイル以上の references/*.md 横断改修は opt-in）は、可逆性原則の例外ではなく **レビュー可視性・Council 負荷を理由とする PR 単位の上乗せ制約**であり、本ファイルの 4 委譲レベル（可逆性ベース）の上に auto-merge 層が追加する運用ゲートとして委ねる |
| `.github/workflows/claude-review.yml` | §3.1 SPEC/DONT 改変 PR の独立レビュー（paths フィルタ） |
| REGIME.md / `dev-env-spec.md` | §4 local/github 検証手段差・squash 前提 |
| `autonomous-drive-deployment.md` | §6 CI スリム化方針の deployment ガイド |

---

## 8. evaluation_history（append-only）

| 日付 | 評価結果 | 次回評価日 | 備考 |
|------|---------|-----------|------|
| 2026-06-14 | v6.0.0 として初導入（案C ハイブリッド境界 SPEC、段階性: H 拡張はゲート後） | 2026-11-06 | Council `council-2026-06-14T-delgbd` |
