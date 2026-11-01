# MATERIAL — claude.ai Project 文書の訂正材料（D-09 / D-11）

| 項目 | 内容 |
|---|---|
| 文書種別 | MATERIAL（訂正の根拠と適用先の提示） |
| 作成日 | 2026-10-25 |
| 起点 | HANDOFF-DH-research-reflection.md T-03 |
| 対象 | claude.ai Project 文書（DH-PHILOSOPHY-INSIGHTS / Harness Engineering 資料） |
| 正典 | repo（`philosophy.md` / `history/DIMENSIONS.md`） |

---

## 0. 原則 — どちらが正典か

D-11 は「**repo（history/DIMENSIONS.md）を正典とし、claude.ai Project の文書を直す**」と定める。
本文書は repo 側の事実を一次証拠として提示する。Project 側の文面は本セッションから読めないため、
**訂正すべき内容**を示し、**訂正作業そのものは行わない**（Project は repo 外）。

repo 内に同じ誤りがある場合は併せて指摘する（こちらは L-FULL なので修正可能）。

---

## 1. D-09 — 憲法は 9 条である

### 1.1 一次証拠

`philosophy.md` の `## 第N条` 見出しを機械的に列挙した結果（2026-10-25）:

| 条 | 見出し |
|---|---|
| 第1条 | フラクタル原則 |
| 第2条 | Shift Left 原則 |
| 第3条 | 情報純度原則 |
| 第4条 | 人間責務の明確化 |
| 第5条 | 献上哲学 |
| 第6条 | 人間 ≒ Council 原則 |
| 第7条 | AI組織論（4役割 + サポート構造） |
| 第8条 | 自律性原則 + 哲学ガードレール |
| 第9条 | 委譲境界原則（可逆性ベース） |

**9 条**。第7条は v5.x、第9条は v6.0.0（PR #147「権限委譲境界の確立（可逆性ベース・第9条新設）」）で追加。

### 1.2 「6 条憲法」表記が残る箇所

| ファイル | 行 | 区分 | 扱い |
|---|---|---|---|
| `.claude/skills/layer0-spec-architect/references/philosophy.md` | 3 | **L-FROZEN-PHIL** | 人間のみ（H-1〜H-3 と同時） |
| `history/DH-PHILOSOPHY-INSIGHTS.md` | 13 | **L-FULL** | **AI 修正可**（下記 §1.3） |
| `history/CHANGELOG.md` | 3132 | 履歴 | **修正しない**（v4.2 時点の記述として正しい） |
| `history/archive/2026-06/SELF-VERIFICATION-v5.0.0.md` | 92 | アーカイブ | 修正しない |
| `history/archive/2026-06/SKILL-CREATOR-AUDIT-v5.0.0.md` | 114 | アーカイブ | 修正しない |

> 履歴・アーカイブを直さないのは、HANDOFF 不変条件 4「記憶と文書は差分で追記する。
> 既存の台帳を全面的に書き直さない」に従う。当時の記述は当時として正しい。

### 1.3 repo 内で今回直せるもの

`history/DH-PHILOSOPHY-INSIGHTS.md:13`:

```
| `.claude/skills/layer0-spec-architect/references/philosophy.md` | DH 6 条憲法（仕様核） |
```

これは**現在の状態を説明する表**であり、履歴記述ではない。よって誤り。
L-FULL のため本サイクルで修正した（§4 参照）。

### 1.4 Project 側に伝えるべきこと

- 「6 条憲法」は**第7条・第9条の追加に追随していない旧称**である
- 現行は **9 条**
- `philosophy.md` ヘッダー自身の訂正は L-FROZEN-PHIL のため 11-06 ゲート後（v7 Phase B / B1）

---

## 2. D-09 — repo に未実装の構想

HANDOFF が「repo に未実装の構想」とする語を全文検索した（`*.md` / `*.py` / `*.yml`・
本 MATERIAL 2 本を除外・2026-10-25）。

| 語 | repo 内出現 | 判定 |
|---|---|---|
| `crosscut-metrics` | 0 件 | **未実装で正しい** |
| `HiL-Bench` | 0 件 | 同上 |
| `Fβ` | 0 件 | 同上 |
| `Ask-F1` | 0 件 | 同上 |
| `排除率` | 0 件 | 同上 |
| `L1-b` | 0 件 | 同上 |

> **D-09 は全項目が正しい。** これらを「DH にある機構」として記述している Project 文書が
> あれば、それは構想であって実装ではない旨に直す。
>
> 併せて: `排除率` が 0 件ということは、HANDOFF の D-13（排除率を適合率側と再現率側に
> 分ける）は**既存指標の改良ではなく新規実装**である。T-15 の見積りに影響する。

### 2.1 実装されている近縁機構（取り違え注意）

| 構想（未実装） | repo にある近縁機構 | 違い |
|---|---|---|
| `crosscut-metrics` | `scripts/pr-audit.py` / `scripts/harness-benchmark.py` | skill ではなくスクリプト。常駐しない |
| `HiL-Bench` | `scripts/harness-benchmark.py` | 人間介入のベンチではなく harness 自体のベンチ |
| レビュアー誤判定率の自動化 | `scripts/reviewer-misjudgment.py` | **実装済み**。ただし人間の正解付与が律速（半自動） |

---

## 3. D-11 — D4 / D5 の正典定義

### 3.1 一次証拠（`history/DIMENSIONS.md`）

`:16-17`（5 次元論の表）:

```
| **D4** | **マスタ skill（メタスキル）** | **dialog-harness リポジトリ内 skill マスタ定義** |
| D5 | Meta モニタリング層 | D4 を外側から監視する **人間**（自動化禁止）|
```

`:34-35`（整備経路の表）:

```
| **D4** | **人間専有** | **council + 人間合意（不変領域）**|
| D5 | 人間そのもの | （自動化禁止） |
```

`:64`（§2.5 の本文）:

```
D4 を外側から監視する人間（自動化禁止）。harness-verifier 出力 + council escalate_to_human
+ D4 改修判断の最終受け手。**主柱: P5 献上哲学** — 全献上の終点、最外殻。
```

### 3.2 確定事項

| 項目 | 正典の定義 | HANDOFF D-11 の記述 | 一致 |
|---|---|---|---|
| D5 | **人間そのもの**（自動化禁止） | 「D5 ＝人間のみ」 | ○ |
| D5 と harness-verifier | harness-verifier は D5 が受け取る**出力を出す側**。人間が「最終受け手」 | 「harness-verifier は道具」 | ○ |
| D4 の整備 | **council + 人間合意**（不変領域） | 「D4 の整備＝Council ＋人間合意」 | ○ |

> **D-11 は全項目が正しい。**

### 3.3 repo 側の整合性確認

`history/DH-PHILOSOPHY-INSIGHTS.md` の D4 / D5 用法を全数確認した（`:113` `:116` `:155`
`:173` `:177` `:181` `:213` `:214` `:219` `:253` `:331` `:336`）。

- D5 は一貫して「人間」「最終監督者」として使われる（`:214`「D5（最終監督者） | 不変」）
- D4 は一貫して「設計層 / 不変領域」として使われる（`:213`）

> **repo 側に D-11 の誤りは無い。** 訂正対象は Project 文書のみ。

### 3.4 Project 側に伝えるべきこと

- **D5 を「harness-verifier を含む層」と書いていたら誤り。** D5 は人間そのもの。
  harness-verifier は D4 内部整合性を検査する**道具**で、その出力の受け手が D5
- **D4 を「AI が自律改修する層」と書いていたら誤り。** D4 改修は council 諮問 + 人間承認

---

## 4. 本サイクルで repo に適用した訂正

| ファイル | 変更 | 根拠 |
|---|---|---|
| `history/DH-PHILOSOPHY-INSIGHTS.md:13` | 「DH 6 条憲法（仕様核）」→ 9 条である旨に訂正 | §1.3 |

L-FROZEN 配下は 1 バイトも変更していない（HANDOFF 不変条件 1）。

---

## 5. 本文書が**しなかった**こと

- claude.ai Project 文書そのものの編集（repo 外・本セッションから到達しない）
- `philosophy.md:3` の訂正（L-FROZEN-PHIL・人間が H-1〜H-3 と同時に行う）
- 履歴 / アーカイブ文書の「6 条憲法」表記の書き換え（不変条件 4）
