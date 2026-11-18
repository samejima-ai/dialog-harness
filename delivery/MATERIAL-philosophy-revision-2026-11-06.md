# MATERIAL — 憲法改訂の材料（H-1 / H-2 / H-3 起票用）

| 項目 | 内容 |
|---|---|
| 文書種別 | MATERIAL（AI が用意する材料・**改訂案ではない**） |
| 作成日 | 2026-10-25 |
| 起点 | HANDOFF-DH-research-reflection.md T-02 |
| 対象 | `philosophy.md`（L-FROZEN-PHIL） |
| 読み手 | 人間（ひで）— H-1 / H-2 / H-3 の起票・執筆者 |

---

## 0. 本文書の性格（先に読む）

HANDOFF の T-02 は「人間レビュー用の**差分**として用意する」と書くが、本文書は**差分を含まない**。

`delegation-boundary.md` §1 は `philosophy.md` を **L-FROZEN-PHIL** と定め、
「**2026-11-06 roll-back ゲート後に再諮問するまで AI 提案 PR も不可**」とする。
同 §2 は理由を「再帰の遮断」と明示する。適用しない差分であっても、改訂文面そのものを
AI が書けば、人間の起票は「AI 案の承認」に変質する。これは禁止の実質を空にする。

HANDOFF 自身の不変条件 1 もこの線を引いている：

> Claude Code は改訂案の材料（**現行条文の該当箇所、影響する skill と workflow の一覧**）だけを用意する。

本文書はその 2 点に限定する。改訂文面は人間が書く。

---

## 1. D-05（第4条改訂）の該当箇所

### 1.1 現行条文 — 「自律駆動を止めない」

`philosophy.md:146-148`

```
### 自律駆動を止めない

L1 は開発中に人間へ質問しない。仕様不足は即献上（タイプA）、仕様改善提案は献上時（タイプC）に回す。開発中の割り込みはトークン浪費と文脈断絶を生む。
```

### 1.2 現行条文 — 「開発中の質問禁止」

`philosophy.md:305-313`

```
#### 開発中の質問禁止

L0 対話完了後、L1/L2 実行中は Council 事後評価のための質問を
人間に発してはならない。Council 判定の適切性確認は全て事後に
まとめて行う。

例外: H カテゴリへの抵触を AI が検知した場合は、即時献上
（C1 判断献上チャネル）で中断する。これは事後評価ではなく
権限境界の問題である。
```

### 1.3 D-05 が触る範囲

D-05 は「実装**前**に照会役を 1 つ置き、質問をまとめて判断キットへ出す。実装**中**は
新たに見つかった障害だけを照会できる」とする。上記 2 箇所との関係は次の通り。

| 条文 | D-05 との関係 | 論点 |
|---|---|---|
| §自律駆動を止めない | 「開発中に質問しない」は維持される。D-05 は**実装前**に照会段を足すもの | 「開発中」の起点が L0 対話完了後か、照会段完了後かが未定義になる |
| §開発中の質問禁止 | 既に例外が 1 つある（H カテゴリ抵触 → 即時献上） | D-05 の「新たに見つかった障害」は**第 2 の例外**か、既存例外の拡張か |

> **起票時に決める点**: 既存例外（H カテゴリ）と D-05 の新例外の関係。
> 併記か、包含か。包含なら「権限境界の問題」という既存例外の理由付けが薄まる。

---

## 2. D-04（第7条・第9条改訂）の該当箇所

### 2.1 現行条文 — 第7条 auto-merge デフォルト方針

`philosophy.md:433-448`（§「auto-merge デフォルト方針（v5.9.0 で opt-in→opt-out 反転）」）

末尾に roll-back ゲートの定義がある（`philosophy.md:446`）:

```
**roll-back 評価ゲート** は 6 ヶ月後（2026-11-06）に必須で、暗黙 merge 事故 1 件以上 /
AI 判定漏れ率 5% 超 / 境界曖昧化月 2 件以上 / 二重ラベル腐敗のいずれかで opt-in モデルに
戻す手順を `auto-merge-boundary.md §roll-back プロトコル` に定義。
```

### 2.2 現行条文 — 第9条 委譲レベル

`philosophy.md:494-511`（§「第9条 委譲境界原則（可逆性ベース）」および §「4 委譲レベル」）

### 2.3 D-04 が触る範囲

D-04 は「L-FULL（可逆）は自動マージ維持。L-GATE と opt-in 領域は人間が**差分を見てから**
マージ」とする。これは第9条の 4 委譲レベルの**運用**を変えるが、レベル定義自体は変えない。

> **起票時に決める点**: 「人間が見るのは差分そのもの」という要求をどこに書くか。
> 第9条（委譲レベルの性質）か、第7条（auto-merge の運用）か。
> 現行では auto-merge の具体は `auto-merge-boundary.md`（L-FROZEN-**META**・恒久固定）に
> あり、こちらは philosophy より改訂が重い。**書く場所で改訂コストが変わる**。

---

## 3. D-12（第3条の減衰見直し）の該当箇所

### 3.1 現行条文

`philosophy.md:99-117`

```
## 第3条 情報純度原則

**エージェント間通信は自然言語経由で必ず情報損失が発生する**。これを前提にコスト計算する。

### 情報純度の定義

独立した責務エージェントが受け取るコンテキストの、**当該責務にとっての信号対雑音比**。
純度が低いと誤検出・取りこぼし・過剰修正が増える。

### サブエージェント追加の4基準

新規サブエージェントを立てる判断は以下全てを満たす場合に限る：

1. **純度向上**: 分離することで受け手のコンテキスト純度が明確に上がる
2. **責務明確**: 分離後の責務が単一かつ独立
3. **入出力規格化**: ドキュメント化された契約で通信できる
4. **独立コンテキスト必然性**: 同一コンテキストでは認知バイアスが生じる（例: 実装者と独立レビュアー）

4基準のどれかを欠く分離は情報損失コストに見合わない。
```

### 3.2 D-12 の指す分割線

D-12 は「減衰させるのは『自然言語での損失を前提とする』**言い回しだけ**とし、
サブエージェント追加を抑える**中身は維持**する」とする。本文を読む限り、この線は明確に引ける。

| 部位 | D-12 の扱い | 根拠 |
|---|---|---|
| 冒頭「自然言語経由で必ず情報損失が発生する」 | 減衰対象 | 認知足場（モデルが吸収した前提） |
| §情報純度の定義（信号対雑音比） | **維持** | 環境足場（文脈隔離の根拠） |
| §サブエージェント追加の4基準 | **維持** | 環境足場（基準 4 は independent-reviewer の存在根拠そのもの） |
| 末尾「情報損失コストに見合わない」 | 文言のみ要調整 | 冒頭の前提に依存した言い回し |

### 3.3 v7 spec 側の記述との突き合わせ

`upgrade-spec-v7.0.0.md:40` の 3 層表は第3条を**まるごと**「認知足場（時限化・縮退）」に
置いている：

```
| **認知足場** | 多ペルソナ合議 / 役割分割 / 献上 4 分類 / 情報純度の損失前提 | 実測で無効か有害 → 時限化・縮退 | 第 3・5 条、第 7 条 4 役割、Council 3 ペルソナ、L2 雛形 |
```

同じ行の「内容」列は「情報純度の**損失前提**」と正しく限定しているのに、
「DH の該当」列は「第 3 条」と条単位で書いている。**D-12 はこの列のずれの修正**にあたる。

> **起票時に決める点**: 第3条の扱いは philosophy 本文ではなく v7 spec の 3 層表を
> 直せば済む可能性がある。その場合 H-3 は L-FROZEN に触れない（`dh-upgrades/` は L-FULL）。
> philosophy 本文の冒頭 1 文を直すかどうかは別判断。

---

## 4. 影響する skill と workflow の一覧

`philosophy.md` を参照する全ファイルは 100 本超あるため、**改訂対象の条を名指しで
参照しているもの**に絞る（`grep -l "第N条"`・2026-10-25 時点・`history/archive` 除く）。

### 4.1 第3条（D-12）

| ファイル | 層 |
|---|---|
| `.claude/skills/crosscut-council/references/council-philosophy.md` | crosscut |
| `.claude/skills/layer0-archeo-architect/SKILL.md` | L0 |
| `.claude/skills/layer0-onboarding/SKILL.md` | L0 |
| `.claude/skills/layer0-reindex-librarian/SKILL.md` | L0 |
| `.claude/skills/layer0-spec-architect/SKILL.md` | L0 |
| `.claude/skills/layer1-autonomous-dev/references/e2e-best-practices.md` | L1 |
| `.claude/skills/layer1-independent-reviewer/SKILL.md` | L1 |
| `.github/workflows/claude-review.yml` | CI |
| `harness-verifier/glossary.yml` | 検査 |

> 第3条は **9 本**が名指しで参照する。うち `claude-review.yml` と `glossary.yml` は
> 機械側。文言を変えると検査語彙の同期が要る。

### 4.2 第4条（D-05）

| ファイル | 層 |
|---|---|
| `.claude/skills/crosscut-council/references/council-philosophy.md` | crosscut |
| `.claude/skills/layer0-archeo-architect/SKILL.md` | L0 |
| `.claude/skills/layer0-spec-architect/SKILL.md` | L0 |
| `.claude/skills/layer0-spec-architect/references/test-oracle-dialog.md` | L0 |
| `harness-verifier/glossary.yml` | 検査 |

### 4.3 第7条（D-04）

| ファイル | 層 |
|---|---|
| `.claude/skills/crosscut-council/references/council-philosophy.md` | crosscut |

### 4.4 第9条（D-04）

| ファイル | 層 |
|---|---|
| `.claude/skills/crosscut-council/references/escalation-matrix.md` | crosscut |

> 第7条・第9条は名指し参照が **各 1 本**と少ない。ただし auto-merge の実運用は
> `auto-merge.yml` / `auto-merge-boundary.md` / `delegation-boundary.md` が担っており、
> これらは条番号ではなく機構名で参照する。D-04 の実装影響は下表が本体。

### 4.5 D-04 の実装影響（条番号を使わない参照）

| ファイル | 区分 | 役割 |
|---|---|---|
| `.github/workflows/auto-merge.yml` | L-FULL | 自動マージの実行主体。L-GATE 分岐の実装先（T-05） |
| `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md` | **L-FROZEN-META** | opt-in 領域・stop ラベル・roll-back プロトコルの定義 |
| `.claude/skills/crosscut-autonomous-drive/references/delegation-boundary.md` | **L-FROZEN-META** | L-FULL / L-GATE / L-FROZEN の定義 |

> **注意**: 下 2 本は L-FROZEN-**META**（恒久固定）であり、philosophy（段階固定）より
> 緩和余地が無い。D-04 が「L-GATE は人間がマージ」を**境界 SPEC の側**に書く設計なら、
> 11-06 ゲートを通っても AI は起票できない。

---

## 5. 現状認識の訂正材料（D-09 / D-11）

### 5.1 D-09 — 9 条である

`philosophy.md:1-3` のヘッダー:

```
# Philosophy — dialog-harness v4

dialog-harness の6条憲法。L0/L1/L2 の全skill はここを原典として参照する。
```

本文の実態は **第1条〜第9条**（`## 第N条` の見出しで確認）。第7条は v5.x、
第9条は v6.0.0（PR #147）で追加されており、ヘッダーの「6条憲法」が追随していない。

`v7.0.0 spec` は既にこのずれを B1 で把握している（`upgrade-spec-v7.0.0.md:229`:
「併せてヘッダー『6条憲法』の実態（9 条）とのずれを解消」）。

同じ表記は次の 2 本にも残る（いずれも履歴文書・**書き換え不要**）:

- `history/CHANGELOG.md:3132`（v4.2 時点の記述・当時は正しい）
- `history/archive/2026-06/` 配下 2 本（アーカイブ）

> **訂正は 1 箇所**（`philosophy.md:3`）。ただし L-FROZEN-PHIL のため人間が行う。

### 5.2 D-09 — repo に無い概念

HANDOFF が「repo に未実装の構想」とする 5 語を全文検索した（`*.md` / `*.py` / `*.yml`）。

| 語 | repo 内の出現 | 判定 |
|---|---|---|
| `crosscut-metrics` | 0 件 | 未実装で正しい |
| `HiL-Bench` | 0 件 | 同上 |
| `Fβ` | 0 件 | 同上 |
| `Ask-F1` | 0 件 | 同上 |
| `排除率` | 0 件 | 同上 |
| `L1-b` | 0 件 | 同上 |

> HANDOFF の D-09 は**全項目が正しい**。訂正先は repo ではなく claude.ai Project 文書側。

### 5.3 D-11 — D4 / D5 の正典

`history/DIMENSIONS.md` の記述（正典）:

| 次元 | 定義（DIMENSIONS.md:16-17） | 整備（同 34-35） |
|---|---|---|
| D4 | マスタ skill（DH リポジトリ内 skill マスタ定義） | **council + 人間合意（不変領域）** |
| D5 | Meta モニタリング層 = D4 を外側から監視する**人間**（自動化禁止） | （自動化禁止） |

同 `:64`:

```
### 2.5 D5（人間）

D4 を外側から監視する人間（自動化禁止）。harness-verifier 出力 + council escalate_to_human
+ D4 改修判断の最終受け手。
```

> **D-11 は正しい**。D5 ＝人間のみであり、harness-verifier はその人間が受け取る
> 出力を出す**道具**として位置づけられている（「最終受け手」は人間）。
> D4 の整備＝ council ＋人間合意、も DIMENSIONS.md の記述通り。

---

## 6. 人間が起票するときの順序（提案・拘束しない）

1. **H-3（D-12）を先に** — §3.3 の通り、v7 spec の 3 層表の修正だけで済む可能性がある。
   済むなら L-FROZEN に触れず、`dh-upgrades/` は L-FULL なので AI が実装できる。
2. **H-2（D-04）は書く場所を先に決める** — §4.5 の通り、境界 SPEC 側に書くと
   L-FROZEN-META（恒久固定）に入り、以後の改訂余地が消える。
3. **H-1（D-05）は例外の関係を先に決める** — §1.3 の通り、既存の H カテゴリ例外との
   包含関係が決まらないと条文が書けない。

---

## 7. 本文書が**しなかった**こと

- `philosophy.md` の改訂文面の起草（L-FROZEN-PHIL・§0）
- 適用可能な diff / patch の生成（同上）
- 第3条を減衰させるか否かの判断（第8条: 採否の判断を AI に持たせない）
- `auto-merge-boundary.md` / `delegation-boundary.md` への変更（L-FROZEN-META）
