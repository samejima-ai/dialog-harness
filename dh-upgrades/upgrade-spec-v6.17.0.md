# upgrade-spec v6.17.0 — 宣言層の lock-step 清算（点検 (a)〜(h)）

> **状態: L0 起草（人間レビュー待ち）**。本仕様の実装は escalation-matrix「規範文書改変」行
> （`.claude/skills/crosscut-council/references/escalation-matrix.md:31`）に従い、人間レビュー通過後・
> **実装前に Council 諮問**を経る。本 spec 自体の設計判断は Council 未諮問（起草時点で意図的に未実施 —
> 諮問対象は §判断点に列挙した 5 点）。
>
> **起点**: ひでさん発話（2026-09-05）「点検清算 (a)〜(h) を L0 で仕様化して」。
> **一次材料**: `delivery/ANALYSIS-code-knowledge-graph-2026-09-05.md` §DH 点検所見（Workflow
> `wf_1842b5a4-d85`、29 エージェント / 所見 113 件 / 反証 12 件）および同 §いま出ている案 4。
> 本 spec の全数値は 2026-09-05 に再実測したもの（ブレストメモの値を引き写していない）。
>
> **版番号の注記**: `VERSION` は 6.11.0 のまま v6.12.0〜v6.16.0 の spec が存在する。この不整合を閉じるのが
> 本 spec の F1 であり、**本 spec の番号は F1 の結論に従って rename されうる**（v6.16.0 と同じ仮置き。
> 判断キット Q9-A「別 PR で先に揃える」が未着手のまま本 spec が積まれることを避ける設計は §実装順序）。

---

## 0. 位置づけ — 新機能ではなく、宣言と実体の乖離を閉じる

本 spec は DH に新しい能力を足さない。**既に持っている宣言（GRAPH.yml / dh-manifest.yml / VERSION /
upgrade-spec 状態行 / RL 索引 / 代謝 cursor）が実体から離れた 8 箇所を戻し、同じ離れ方が二度起きない
機構を置く**。

### 根本原因 — 宣言層は「宣言 → 実体」しか検査していない

点検で挙がった 8 項目は独立した 8 個の不具合ではなく、**1 つの構造的欠落の 8 つの現れ**である。

| 検査の向き | 既存の実装 | 結果 |
|---|---|---|
| **宣言 → 実体**（宣言したものが在るか） | `execution_graph.py` G-2（`node.impl` / `edge.source` のパス実在）、`glossary.py`（宣言 skill の dir 実在） | 実装済み・機能している |
| **実体 → 宣言**（在るものが宣言されているか） | `glossary.py:250-255` に skill 向けのみ存在（しかも `("layer","crosscut-")` prefix で `rtk-integration` を黙って除外） | **GRAPH.yml / dh-manifest / RL 索引には無い** |
| **宣言の鮮度**（宣言が古くなっていないか） | 無し | **VERSION / 状態行 / 代謝 cursor が止まっても誰も気づかない** |
| **宣言の実質**（宣言した根拠が本当にそれか） | G-2 は `source:` の**パス存在**しか見ない | **中身が根拠になっていない edge が PASS を通過**（F2 の HV-04） |

これは `GRAPH.yml:13-14` の不変条件 I-2「実装が正・宣言が従。乖離検出時に自動で実装を書き換えない
（検出のみ）」が、**検出側の片肺しか実装されていない**状態である。「古い地図が誤情報を蓄積する」ことを
自ら不変条件に書いた DH が、自らの地図でそれを起こしている。

### 8 項目の分類

| # | 項目 | 欠落の種別 | 是正 | 再発防止機構 |
|---|---|---|---|---|
| (a) | VERSION / GRAPH.version / 状態行 の三重不一致 | 鮮度 | F1 | F1（版整合検査 + 昇格規則） |
| (b) | GRAPH.yml に 4 skill 未登録 / edge source の実質乖離 | 実体→宣言、実質 | F2 | F2（網羅性検査 + source 実質検査） |
| (c) | COUNCIL-LOG 二重管理 + 配布先への byte 一致配布 | 実体の二重定義 | F3 | F3（配布物に配布先固有状態を置かない検査） |
| (d) | manifest 4 分類に `.mcp.json` / `.gitignore` / `.claude/agents/` が無い + Level B 同居 vs 置換の未調停 | 実体→宣言 | F4 | F4（分類の網羅検査） |
| (e) | Level A checklist E-3 が Windows native を列挙しない | 規範と実態の不整合 | F5 | —（規範改変。Council 案件） |
| (f) | RL が届くのに読込経路が無い + 現況索引 2 箇所 stale | 配線の欠落 | F6 | F6（RL 索引の件数一致検査） |
| (g) | `GH_REVIEW_PAT` 失効で全 PR の auto-merge が red / gemini-review が 4 ヶ月未起動 | 運用 + 検知の欠落 | F7 | F7（PAT 有効性検査 + workflow 沈黙検知） |
| (h) | 情報代謝が 2026-06-07 で停止（cursor 記録時点から +2,417 行） | 鮮度 | F8 | F8（cursor 停滞の決定論検知） |

### 設計方針 — 検査器を 8 本作らない

再発防止機構は 5 種類あるが、**新規スクリプトは作らず既存 2 経路に寄生させる**（`ritual-protocol.md:148-164`
「新しい常駐機構は作らず、既存の儀式に寄生する」と同型）。

- **静的な網羅性・整合性**（F1 / F2 / F4 / F6）→ `harness-verifier/checks/declaration_coverage.py` **1 本**に集約し
  `verify.py` の CHECK_REGISTRY に**検査 8** として登録する。`glossary.py:240-255` の既存双方向パターンを一般化した形であり、
  新しい検査思想を持ち込まない
- **時間経過による停滞**（F7 の workflow 沈黙 / F8 の cursor 停滞）→ `scripts/signal-scan.py` の**検知器 (e) (f)** として追加する。
  同スクリプトは既に `review_trigger` の経過日数検知（検知器 c）を持ち、「時間で腐るものを数える」枠がある

---

## 不変条件（全機能共通）

- **I-1 是正と検査は同一 PR**。検査だけ先に入れると CI が既存 drift で即 red になり、allowlist を作る誘惑が生まれる
  （v6.15.0 I-3「宣言と配線を同一 PR」の再適用）。**allowlist / 除外リストを作らない**（kakuman の
  「rls-drift allowlist 空」規律と同型）。除外が必要なら宣言側に明示行を書く（F2 の `graph_excluded` 等）
- **I-2 検査は判定を持たない**。検出して数えるだけで、自動修正しない（`GRAPH.yml:13-14` I-2 / `BOUNDARY.md`）。
  是正は人間または L0
- **I-3 検知は決定論**。蒸留・検査に LLM を使わない（philosophy 第 2 条）
- **I-4 常時発火する検知を作らない**（`telemetry-reflux.rules.md:22-23` TR-4）。F1〜F6 の検査は「是正後は 0 件」が定常状態。
  0 件でない状態が定常化したら検査の設計が誤っている
- **I-5 検査はローカルで走る**（純化 RL §9 / `regime-assessment.md` §dev_mode 二軸注記）。CI にしか存在する検査を作らない。
  検査 8 は `python harness-verifier/verify.py` で単体実行できる
- **I-6 配布先に無い機構を配布先の前提にしない**。`harness-verifier/` は配布されない（`BOUNDARY.md`、DECL-16）ため、
  検査 8 は **DH 本体の自己検査**に閉じる。配布先向けの同型検査は本 spec の対象外（§実装しないもの）
- **I-7 本 spec 自身に規範メタデータを付す**。新規規範には `stage:` / `review_trigger:` が必須（`dev-env-spec.md:982`）。
  v6.16.0 が新規規範を起草しながら 0 件だった（DECL-13）ため、本 spec は各 F 項目に明記して自己適用する
- **I-8 不可逆な削除をしない**。F3 の COUNCIL-LOG 処遇は「移送・転記」であって delete ではない
  （情報代謝の COLD = archive ≠ delete と同型）

---

## F1. VERSION 昇格規則の明文化 + 宣言層 3 点の版整合（priority: critical / (a)）

### 現状（2026-09-05 実測）

| 宣言 | 値 | 最終更新 |
|---|---|---|
| `VERSION` | `6.11.0` | 2026-08-15 `3e3a8b2`（PR #186） |
| `GRAPH.yml:27` `version:` | `"6.12.0"` | 2026-08-25 PR #191 |
| `dh-upgrades/` の spec | v6.11.0 〜 v6.16.0 の 6 本 | 2026-09-05 |

VERSION 昇格なしで master に入った実装: PR #191（v6.12.0 F1/F2/F3/F5）/ #203（v6.15.0 F2）/ #206（v6.15.0 F1）/
#207（v6.15.0 F4+F5）/ #217 / #221 / #223。**「VERSION を上げる契機」の規則は DH のどこにも無い**
（`dh-manifest.yml:13` は「正典は VERSION ファイル」と場所を定めるのみ、`escalation-matrix.md:31` は改変前の諮問を定めるのみ）。

**配布先の版識別の実測（2026-09-05、Council 哲学者軸の指摘を受けて検証）**: 「配布先は DH の版番号で
自分が何を持っているかを識別する」という前提は**半分しか成立していない**。

| 配布先 | `VERSION` | `dh-manifest.yml` | 版の自己申告 |
|---|---|---|---|
| cc-cockpit | `6.11.0` | 有り | `CLAUDE.md:17`「dialog-harness v6.11.0 のテンプレートから」 |
| kakuman-platform-v3.0 | **無し** | **無し** | `CLAUDE.md:10` に自然言語で「**DH v6.8.0**」の 1 行のみ（DH 本体より 3 版古く、機械検証の経路が無い） |

kakuman は DH スキルを 20 個持ちながら**機械可読な版の宣言を 1 つも持たない**。
さらに `dh-manifest.yml:18` は互換判定を **semver の major 部のみ**で行うと明記しており、
**minor を読む機械は現在ゼロ**である。したがって VERSION 昇格規則を整えるだけでは
「配布先が自分の版を知る」問題は解けない — **配布時に `VERSION` / `dh-manifest.yml` を同梱する規律**が
別途要る（本 spec の対象外。F4 の manifest 分類と併せて次サイクルの候補とする）。
版番号に持たせるべき役割は同一性ではない（同一性は `UPDATE.md` の commit SHA ピンが既に担保している）。

**既存規則の追加実測（2026-09-05）**: `dev-env-spec.md:726` §dialog-harness-layers バージョニング規則には
**「何を major / minor と数えるか」の規則は既にある**（:731 メジャー昇格 / :740 マイナー昇格）。
欠けているのは**いつ上げるか（契機）**だけである。さらに同節 :750 §判断主体 は
「AI が変更内容から判断し、メジャー昇格時のみ人間に献上する。**マイナー昇格は自動記録**」と定めており、
**上げるべき主体は AI だと既に決まっている**。つまり本件は「規則が無い」だけでなく
**「在る規則が守られていない」**でもある。加えて同節 :761 §バージョン履歴 は **v4.2 で止まっており**、
v5 系・v6 系の 20 版以上が 1 行も記録されていない（= §0 が言う「宣言の鮮度」欠落の実例が
バージョニング規則そのものの中にある）。是正はこの 3 点（契機の明文化 / 既存の判断主体規則との接続 /
履歴の追いつき）をまとめて扱う。

状態行の実態（`> **状態:` 行 vs 実装）:

| spec | 状態行 | 実装 |
|---|---|---|
| v6.11.0 | L0 起草（人間レビュー待ち） | 実装済み（#186 / #187）。§履歴のみ追記済み = header だけ古い |
| v6.12.0 | Council 諮問通過・人間の採否判定待ち | F1/F2/F3/F5 実装済み（#191）、F4 は意図的延期。header・§履歴とも古い |
| v6.13.0 / v6.14.0 / v6.16.0 | L0 起草（人間レビュー待ち） | 未実装（**状態行と一致**） |
| v6.15.0 | L0 起草（人間レビュー待ち） | F1 / F2 / F4 / F5 実装済み。F2 のみ `:132` に注記あり、他は未記録 |

### 是正

1. **VERSION 昇格規則を明文化**する。`dev-env-spec.md` §バージョニング規則に 1 節を追加:
   - **昇格の契機** = 「その版の spec の critical 機能がすべて master に入った時点」。部分実装では上げない
   - **昇格の実行** = VERSION ファイルと `GRAPH.yml` `version:` を**同一 commit**で更新し、当該 spec の状態行を
     `実装済み（PR #N）` に書き換える
   - **状態行の値域**を固定する: `L0 起草（人間レビュー待ち）` / `Council 諮問通過・人間の採否判定待ち` /
     `実装中（F<n> 済 / F<m> 未）` / `実装済み（PR #N、VERSION x.y.z）` / `破棄（理由）`
2. **現状の版を確定**する。v6.12.0 と v6.15.0 の実装済み分をどう数えるかは §判断点 D-1（人間）
3. 各 spec の状態行を実態に合わせる（v6.11.0 / v6.12.0 / v6.15.0 の 3 本）

### 再発防止機構（検査 8 の一部）

- `VERSION` と `GRAPH.yml` `version:` の一致（不一致 = FAIL）
- `dh-upgrades/upgrade-spec-v*.md` の状態行が上記値域に含まれること（値域外 = FAIL）
- 状態行が `実装済み` を名乗る spec の版 ≤ VERSION（超過 = FAIL）
- 状態行が `L0 起草` のまま、その版を commit message で名乗る commit が master に存在する（= WARN。
  「起草のまま実装が入った」の検出。`git log --grep` で決定論に判定できる）

### 規範メタデータ

```yaml
stage: 全段階
review_trigger:
  - measured: 版整合 FAIL が 6 cycle 連続 0 件なら、状態行の値域固定のみ残して検査を簡素化検討
```

---

## F2. GRAPH.yml の網羅性 + edge source の実質検査（priority: critical / (b)）

### 現状（2026-09-05 実測）

- `nodes` 30（agent 16 / human 6 / tool 8）、`.claude/skills/` 実体 20。**未登録 4 本** =
  `crosscut-continuous-learning` / `crosscut-hook-observer` / `crosscut-verifier-philosophy` / `rtk-integration`
- 逆方向（node で実体無し）は **0 件**（G-2 が効いている）
- `scripts/*.py` のうち `impl:` から参照されないもの **4 本** = `check_template_sync.py` / `pr-audit.py` /
  `reviewer-misjudgment.py` / `upstream-scan.py`
- G-5 は `execution_graph.py:235` の `startswith(("layer","crosscut"))` + `:243` の `continue` で
  未登録 dir を**計数せずに**走査対象外にする。F2-5 METRIC にも「対象外 dir 数」は出ない
- **HV-04（source の実質乖離）**: `GRAPH.yml:326-335` は `layer0-spec-architect → council-performance` と
  `→ harness-benchmark` を `source: ritual-protocol.md` で宣言するが、`ritual-protocol.md` が F1 手順で実際に
  呼ぶのは `council-log-sync.py`（:88-89）と `council-axis-audit.py`（:94-95）**のみ**。
  G-2 は `source` のパス存在しか見ないため、**この乖離は PASS を通過している**

### 是正

1. **4 skill の処遇を決める**（§判断点 D-2）。選択肢は「node として登録する」か「`graph_excluded:` に理由付きで明示宣言する」の 2 つ。
   **黙って対象外にする現状を残さない**
2. **script 4 本の処遇**も同様（tool node 化 or `graph_excluded`）
3. **HV-04 の 2 edge を是正**する。`ritual-protocol.md` に実際の呼び出しを書くか、edge の `source` を実態に合わせるか、
   edge 自体を削除するか（§判断点 D-2）
4. `execution_graph.py` の `continue` に**計数**を追加し、F2-5 METRIC に「宣言外 dir 数」を出す
   （`GRAPH.yml:384`「F1-4 が漏れを可視化する仕掛け」の自己適用。v6.13.0 I-4「検出器は黙って捨てない」）

### 再発防止機構（検査 8 の一部）

- `.claude/skills/*/` ⊆ (`nodes[].id` ∪ `graph_excluded[].id`)（違反 = FAIL）。**prefix でフィルタしない**
  （`glossary.py:250` の `managed_prefixes` が `rtk-integration` を落とした欠陥を持ち込まない）
- `scripts/*.py`（`test-*` を除く）⊆ (`nodes[].impl` ∪ `graph_excluded`)（違反 = WARN）
- **source 実質検査**: `edge.source` が `.md` のとき、その本文に `edge.to` の `impl` basename または node id が
  出現すること（不出現 = WARN）。パス存在だけを見る G-2 の補完であり、意味を判定しない決定論検査

### 規範メタデータ

```yaml
stage: 全段階
review_trigger:
  - measured: source 実質検査の WARN が 6 cycle 連続 0 件なら FAIL 昇格を検討（G-5 と同じ昇格規律）
```

---

## F3. COUNCIL-LOG 二重管理の解消（priority: high / (c)）

### 現状（2026-09-05 実測）

| ログ | 形式 | 件数 | 期間 | サイズ |
|---|---|---|---|---|
| `history/COUNCIL-LOG.md` | YAML list（`- invocation_id:`） | 70 行 / 69 ユニーク | 2026-04-29 〜 09-04 | 298,832 B |
| `.claude/skills/crosscut-council/history/COUNCIL-LOG.md` | 見出し（`## council-<id>`）+ JSON | 21 | 2026-04-21 〜 06-28 | 83,467 B |

共通 8 / root のみ 61 / **skill 内のみ 13**。どちらも他方の部分集合ではない。

- `SKILL.md:345` / `output-format.md` / `council-log-sync.py:76` はいずれも **root を単一情報源**と宣言。
  同期パーサは見出し形式を読まないため、**skill 内のみの 13 件は CTL 統計から永久に脱落**している
- skill 内ログ L11 は「社外秘情報が含まれ得るため、skill 内部に閉じて保管する」と書くが、
  `dh-manifest.yml` `overwrite: .claude/skills/` により **kakuman / cc-cockpit へ byte 一致で配布済み**（本日 `cmp` で確認）
- 意図的決定の記録は無い。`design-history.md:209` は「COUNCIL-LOG.md / CHANGELOG / ARCH-DECISIONS / DELIVERY.md の
  処遇確定」を**先送り項目**として列挙している。隣接する規範として `consensus-protocol.md:419` が
  「`.claude/skills/crosscut-council/history/` 等の skill 内 prefix は誤り」と宣言しているが、
  **その対象は `history/council-readable/` の人間可読版であって COUNCIL-LOG.md 本体ではない**（同一ディレクトリを
  指すが射程が違う。是正の根拠として引くときはこの差を潰さない）

### 是正

1. **13 件を root へ転記**する（v6.4.1 が `sync.py:358` / `output-format.md:271-276` で明文化した救済経路を使う）。
   **削除しない**（I-8）
2. 転記後、skill 内ログを**配布物から外す**。選択肢は §判断点 D-3（`.gitignore` 化 / `history/` へ移送 /
   manifest の `never_touch` へ明示）
3. `history/COUNCIL-LOG.md` の重複 1 件（`coddag` ×2）を解消

### 再発防止機構（検査 8 の一部）

- **配布物に「配布先固有になりうる状態」を置かない検査**: `overwrite:` 配下（`.claude/skills/` / `templates/`）に
  `history/` ディレクトリまたは `*LOG*.md` が存在する場合 WARN。
  これは (c) の一般形であり、「skill 内に状態を置くと上書きで消える / 意図せず配られる」という
  SK-03 の実害（kakuman 固有 Council 2 件の消失）を型として封じる

### 規範メタデータ

```yaml
stage: 全段階
review_trigger:
  - measured: 配布物内 state 検査の WARN が 6 cycle 連続 0 件なら降格候補
```

---

## F4. dh-manifest 分類の網羅化 + Level B 同居の調停（priority: critical / (d)）

### 現状（2026-09-05 実測）

- `paths` 4 分類（overwrite / merge / redeploy / never_touch）に **`.mcp.json` / `.gitignore` / `.claude/agents/` の行が無い**。
  `:51`「上記以外はすべて never_touch（明示列挙しない＝既定で不可侵）」により既定 never_touch に落ちる
  = **DH が配っても更新経路を持たない**（`.claude/agents/` は DH と cc-cockpit で 10 ファイル byte 同一なのに
  cc-cockpit は「DH 所有」と自己申告し、DH 側は known-gaps G-003 に登録済み = 既に drift 化している）
- **`rm -rf` と Level B 同居の衝突**: `UPDATE.md:60` の `rm -rf .claude/skills && cp -r` を文字どおり実行すると、
  kakuman の固有 skill **7 dir**（`article-forge` / `caaf-wiring` / `decision-kit-html` / `feedback-triage` /
  `l0-pre-brainstorm` / `news-publish` / `supabase-migration-safe`）が消える。
  kakuman の実運用は同期 #6〜#13 一貫して「選択同期」= **正典手順が使われていない**
- 両側とも意図的決定である: v5.0.0 が「Level B は同じ `.claude/skills/` に命名規則で論理分離」（`upgrade-spec-v5.0.0.md:245,258,264-266`）、
  v5.21.0 が「overwrite はディレクトリごと置換」（`upgrade-spec-v5.21.0.md:39-40`）。**両者を調停した記録が無い**
- prefix ベースの allowlist は **DH 配布の `rtk-integration`（prefix 無し）で破れる**

### 是正

1. **未分類 3 パスを分類する**（§判断点 D-4）。`.mcp.json` は本 spec のスコープでは「実体は配らない」ため
   分類行の追加のみで足りる（コードグラフ導入の可否は本 spec の対象外 = §実装しないもの）
2. **`rm -rf` を Level B 保全型の手順に置換する**。DH 所有 dir を列挙して同期する形（kakuman が実運用で
   到達している「選択同期」を正典に昇格させる）。prefix 判定ではなく **manifest 側の明示列挙**で決める
   （`dh-manifest.yml:72-76`「絞りは宣言側の責務であり、スクリプトに判定を持たせない」と同型）
3. `UPDATE.md:73-75` の注記（「カスタムがある場合のみ事前に退避」）を、Level B が**規格上の同居**であることに
   合わせて書き直す

### 再発防止機構（検査 8 の一部）

- **manifest 分類の網羅検査**: リポジトリ直下および `.claude/` 直下の実在パスが 4 分類 ∪ `unclassified_ok:` の
  いずれかに属すること（属さない = WARN）。「明示列挙しない = 既定で不可侵」は運用としては成立するが、
  **DH が配布したいものが黙って不可侵に落ちる**事故（本項の `.claude/agents/`）を検出できない

### 規範メタデータ

```yaml
stage: 全段階
review_trigger:
  - stage_transition: DH が新しい配布面（新ディレクトリ）を持つとき
  - measured: 分類網羅 WARN が 6 cycle 連続 0 件なら降格候補
```

---

## F5. Level A checklist の OS 現実整合（priority: high / (e) / 規範文書改変）

### 現状

- `dev-env-spec.md:65` **E-3 OS 非依存**: 「Linux/Mac/WSL のいずれでも動作する手順」= **Windows native を列挙しない**
- 一方、配布先 2 リポは Windows native（cc-cockpit `CLAUDE.md:3`「対象 OS は Windows」、kakuman は
  `REGIME.md:1068` に python3 3.14.3 / Windows の smoke 記録）
- DH 配布の `rtk-integration` は `SKILL.md:14,25`「Windows native のみ / macOS・Linux・WSL 向け処理は書かない」= **E-3 と正面不整合のまま常駐**

つまり checklist が現実と食い違っており、**逸脱が既に常駐している**。E-3 を守れば rtk は配布できず、
rtk を許すなら E-3 は空文である。

### 是正

E-3 を「Linux / Mac / WSL / **Windows native**」に改める、または「対象 OS を SKILL.md に明示すること」という
**宣言要求**に変える（§判断点 D-5）。**規範文書改変ゆえ実装前 Council 諮問が必須**（escalation-matrix:31）。

### 再発防止機構

無し（checklist は人間判断項目であり機械検証対象外 —`dev-env-spec.md` §検査機構との連携が A/E 系を「不可」と分類済み）。
代わりに F2 の GRAPH 網羅性検査が「規格外のまま常駐する skill」の存在自体は可視化する。

### 規範メタデータ

```yaml
stage: S0-S1     # 環境構築・scaffold 段階で効く規範
review_trigger:
  - stage_transition: 配布先の対象 OS 構成が変わったとき
  - model_generation
```

---

## F6. RL の読込経路修理 + 現況 SSOT 一本化（priority: high / (f)）

### 現状（2026-09-05 実測）

- `templates/rules/common/` の実ファイルは **6 本**（`agentshield-reference.md` / `claude-md-purity.rules.md` /
  `minimalism-ladder.rules.md` / `telemetry-reflux.rules.md` / `ui-baseline.rules.md` / `ui-specialization.context.md`）
- `templates/rules/README.md` §common 現況が列挙するのは **3 本**（minimalism-ladder / ui-baseline / ui-specialization）。
  `claude-md-purity` / `telemetry-reflux` / `agentshield-reference` が欠落
- **配布はできている**が**読まれる経路が無い**: `layer1-autonomous-dev/SKILL.md` の読込順序 1〜8 に `templates/rules` は無く、
  純化 RL §5 が想定する `.dh/rules/common/` も `.claude/rules/` も **3 リポとも不在**、
  配布先 CLAUDE.md からの参照も 0 件
- `minimalism-ladder.rules.md:87` は「L1 autonomous-dev 実装ステップで本 RL を読み込み」と宣言するが、SKILL 側に配線が無い

つまり **6 本の RL は 3 リポに byte 一致で届いているが、誰も読んでいない**。

### 是正

1. **読込経路を 1 つ選んで配線する**（§判断点 D-6）。選択肢:
   - (i) `layer1-autonomous-dev/SKILL.md` の読込順序に `templates/rules/common/*.rules.md` を追加（DH 側・L-FULL）。
     既存 6 本すべてが初めて配線され、**購読量が増える方向**
   - (ii) 配布先 CLAUDE.md の `## 参照` に 1 行（配布先ごと・人間承認）
   - (iii) 読まれないことを受け入れ、RL を「随時参照される reference」と再定義して宣言側を実態に合わせる
2. **現況の SSOT を README 1 箇所に絞る**。`dev-env-spec.md:938-942` の配置 tree は「README 参照」1 行にする
   （純化 RL §2 二重定義禁止の自己適用）

### 再発防止機構（検査 8 の一部）

- `ls templates/rules/common/*.md` の件数と README §common の列挙件数が一致すること（不一致 = FAIL）。
  kakuman の `check-traps-sync.mjs` が「常時索引 ⇄ 全文」で実装した被覆一意性検査の、DH 側 RL への転用

### 規範メタデータ

```yaml
stage: 全段階
review_trigger:
  - measured: 読込経路 (iii) を選んだ場合、RL が 3 cycle 連続で 1 度も参照されなければ配布自体の要否を再問
```

---

## F7. CI 運用の再発防止（priority: critical / (g)）

### 現状（2026-09-05 実測）

- **`GH_REVIEW_PAT` が失効**。`auto-merge` の `evaluate` job が `HTTP 401: Bad credentials`
  （`https://api.github.com/graphql`）で exit 1。本日の PR #247 の 3 head すべてで再現。
  前日 09-04 の run #587 は success ゆえ、失効はこの間に発生
- `check_pat` step は `[ -z "$GH_REVIEW_PAT_PROBE" ]` = **secret の存在だけを見て有効性を見ない**。
  結果、workflow 自身が掲げる「非該当 PR は notice 出力で skip（red CI にしない）」という設計方針が
  **失効時に破れて全 PR が red になる**
- **`gemini-review` が 2026-05-09 以降 4 ヶ月間 1 度も起動していない**。`paths` に `delivery/**` `history/**`
  `dh-upgrades/**` `templates/**` を含むのに、以後の該当 PR で走っていない。
  結果、auto-merge の条件 4.5（「harness-verify / gemini-review の最低 1 つが SUCCESS」）は
  **実質 harness-verify のみで成立している**

### 是正

1. **`GH_REVIEW_PAT` の再発行**（**人間専管**。AI は secrets に触れない = auto-merge-boundary の opt-in 領域。
   本 spec の実装対象外 = §実装しないもの）
2. `check_pat` に**有効性検査**を足す: `gh api user` を叩き、401 なら `::notice::` + `available=false` で skip する
   （red にしない）。存在検査と同じ step 内で完結し、新しい依存を増やさない
3. **gemini-review 未起動の原因調査**。`paths` は該当しているため、原因候補は (i) `GEMINI_API_KEY` 欠落による
   pre-check skip (ii) Actions の workflow 単位無効化 (iii) 別の early-return。調査結果に応じて是正するか、
   起動しない状態を正として **auto-merge 条件 4.5 から gemini-review を外す**（§判断点 D-7）

### 再発防止機構（signal-scan 検知器 (e)）

- **workflow 沈黙検知**: `.github/workflows/*.yml` のうち、`pull_request` トリガを持ちながら
  直近 N 日（既定 60）に 1 度も run が無いものを候補として起票する。
  「red を検知する」既存検知器 (a) の裏返しで、**走らなくなったことは red にならないので誰も気づかない**という
  本項の実害を型として封じる

> **実装済み（PR-E、2026-09-05）**: `check_pat` の使用可能性検査と検知器 (e) `decide_workflow_silence` を実装。
> PR #248 の実 run で **`evaluate` が red → success に変わり、修正が本番で機能することを確認済み**（PAT は失効のまま）。
>
> 独立レビューの指摘で設計を 2 点改めた:
> - **探査先は `user` ではなく `repos/$GH_REPO`**: `user` は認証しか見ないため、SSO 未認可・権限剥奪の PAT を
>   通してしまい後段で 403 になる。repo を叩けば認証と認可を 1 回で見られる
> - **失敗時は `::notice::` ではなく `::warning::`**: red を消しただけでは「誰も気づかない」状態になり、
>   **本 spec が塞ごうとしている欠落そのものを本 step が再演する**（実 run のログで notice が埋もれることを確認）。
>   非ブロッキングだが可視な信号にする。非 0 の内訳（401 / 403 / 5xx）は区別できないため断定せず、
>   `gh` の stderr を 1 行に整形して添える
>
> `bash -e` 下で 3 経路（secret 空 / 有効 / 無効）すべてが step を落とさないことを stub で実証済み。
> **PAT の再発行（是正 1）と gemini-review の原因調査（是正 3）は未了** — 前者は人間専管（§実装しないもの）、
> 後者は D-7 の判断待ち。実装したのは「同じことが起きても red にせず、しかし気づける」機構のみ。
>
> **未対応の指摘（申し送り）**: `gemini-review.yml` も同じ `-z` のみの検査で同型の失効モードに晒されている。
> 本 PR で直さないのは D-7（gemini-review を復旧させるか停止を正とするか）が未決で、
> 廃止するなら修正が無駄になるため。D-7 の決定後に同じ形を適用する。

### 規範メタデータ

```yaml
stage: S2-S4
review_trigger:
  - measured: 沈黙検知が 6 cycle 連続 0 件なら閾値 N を延ばして頻度を下げる
```

---

## F8. 代謝停滞の決定論検知（priority: high / (h)）

### 現状（2026-09-05 実測）

- `history/.metabolism-cursor.yml` の `last_reindex_at` は **2026-06-07T05:00:00Z**（約 3 ヶ月停止）
- `dry_run_remaining: 3` のまま（本番 reindex を 2 回実施済みなのに減算されていない = protocol カウンタと実態の乖離）
- cursor 記録時点からの増分（cursor の `line` = 記録時のファイル長 vs 現末尾）:

| ファイル | cursor line | 現在行数 | 増分 |
|---|---|---|---|
| `COUNCIL-LOG.md` | 2,287 | 3,314 | **+1,027** |
| `CHANGELOG.md` | 1,403 | 2,340 | **+937** |
| `INTENT.md` | 1,023 | 1,383 | **+360** |
| `REGIME-LOG.md` | 674 | 767 | **+93** |
| 合計 | | | **+2,417 行** |

- **この 2,417 行は「未消化行」ではなく代理指標**である。cursor が追う 4 本のうち 3 本
  （`CHANGELOG.md` / `INTENT.md` / `REGIME-LOG.md`）は**先頭 append**（新しい記録が上に載る）で、
  そこでは cursor の `line: N` は「記録時点のファイル長」であって「先頭から N 行が消化済み」を意味しない
  （kakuman の `.metabolism-cursor.yml` が「line は読み進める起点ではない」と明記しているのと同じ性質）。
  ゆえに**どの行が未読かは line からは決まらない**。
  一方で「記録時点から何行増えたか」は追記方向に依らずに決まるので、停滞の代理指標として数えられる
- 購読量 budget は `token_budget: 12000` だが、これは名前に反して **`default-load` 行数の近似上限**
  （`.metabolism-config.yml` の注記）。解決順は ① 配布先 `REGIME.md` `## 情報代謝設定` → ② DH-self config
- その budget は設定されているが、**超過判定を実行する経路が無い**（人間が思い出したときだけ reindex が走る）
- `SUMMARY.md` の「直近 cycle 振り返り」も 2026-08-05 の 1 件で停止（規定は直近 3 件保持）

### 実装中に判明した根本原因（2026-09-05 実測・spec 起草時には未把握）

**(h) の「停止」は運用の怠慢ではなく、protocol の guard が構造的に通らない状態だった。**

1. **DH の history は追記方向が混在している**。`CHANGELOG.md` / `INTENT.md` / `REGIME-LOG.md` は
   **先頭 append**（新しい記録が上）、`COUNCIL-LOG.md` のみ **末尾 append**（実測: 各ファイルの
   先頭と末尾の日付を比較）。
2. **`reindex-protocol.md` §2 の M2 は末尾 append を前提にしている**。checksum の対象を
   「先頭〜line の消化済みプレフィックス」に限る設計理由が
   「append-only な history では**末尾追記で**全ファイル指紋が毎回変わり誤検知するため」と
   明記されている。先頭 append のファイルでは**新しい記録が毎回プレフィックスを書き換える**ので、
   この guard は正常な追記を「cursor 以前の改変」と判定する。
3. **実測: 記録済み checksum は 4 本とも現ファイルと一致しない**。プレフィックス（末尾改行あり／なし）・
   全文の 3 通りで sha256 を計算したが、いずれも記録値と不一致（`COUNCIL-LOG.md` は末尾 append だが
   冒頭に訂正記録が挿入されたため同様に不一致）。
4. `reindex-protocol.md` §1 は「guard を通過した後にのみ §3 の処理フローへ進む。曖昧なまま
   結晶化・移送を行うのは独自補完であり禁止」と定めるため、**現状 reindex は起動しても
   guard で停止する**。これが 2026-06-07 以降動いていない理由。

**この是正は本 PR の対象外**（`.claude/skills/**` = L-FROZEN-META / escalation-matrix「規範文書改変」）。
protocol 側を直すか cursor を貼り直すかは Council 諮問 + 人間判断を要する。ここでは事実の記録に留める。

### 是正

`layer0-reindex-librarian` を起動して代謝を再開する（**本 spec の実装対象外** — 既存機構の運用であって仕様変更ではない。
§実装しないもの）。ただし上記のとおり **guard の是正が先** であり、それを踏まずに reindex を回すと
「曖昧なまま結晶化」に該当する。本 spec が担うのは**停滞を検知する機構**のみ。

### 再発防止機構（signal-scan 検知器 (f)）

- **代謝停滞検知**: `history/.metabolism-cursor.yml` の cursor 記録時点からの増分行数（現末尾 − `line`）を数え、
  購読量 budget（行数）を超えたら候補として起票する。`last_reindex_at` からの経過日数も併記する。
  **判定はせず数えるだけ**（I-2）。body には「増分行数は代理指標であって未消化量そのものではない」旨を明記する
- **cursor > 現末尾は別信号**として持ち上げる（cursor 以前が改変された = reindex-protocol の異常条件）。
  黙って 0 に丸めない
- 既存検知器 (c)（`review_trigger` の経過日数）と同じ「時間で腐るものを数える」枠に入る

> **実装済み（PR-E、2026-09-05）**: 検知器 (f) `decide_metabolism_stall` を実装。実リポで
> 増分 2,417 行 vs 購読量 budget 12,000 行 → **閾値未満ゆえ非検知**。
> つまり **regime の宣言する発火条件では reindex はまだ「回すべき時」ではない**。
> (h) が問題なのは「回っていないこと」ではなく上記 guard で**回せないこと**であり、
> 検知器 (f) はその区別を保ったまま量だけを数える。**代謝の実行（reindex）は未了**（§実装しないもの）。
>
> **時間トリガを入れなかった理由**: 一度は「最終 reindex から N 日」を trip 条件に加えたが、
> `metabolism-regime`「リズム（決定2・確定）」が
> 「発火条件: history 層が指定 token 量（購読量 budget）を超過した時点。**N-cycle トリガーは棄却**」
> と確定しているため撤回した。検知器が既存の確定事項を上書きしてはならない
> （閾値を (h) が発火するよう選ぶのは、標本に合わせた閾値の後付けでもある）。日数は body に参考値として併記する。
>
> **初版実装の誤りと是正（自己レビューで検出）**: 初版は「未消化 = `lines[N:]`」として bytes/4 で
> 約 65,142 tok と算出し `token_budget` 超と報告していた。誤りが 3 点あった —
> ① DH の history は 4 本中 3 本が**先頭 append** なので `lines[N:]` は最古の行を数えていた
> ② `token_budget` は tok ではなく**行数**の上限（config 自身が明記）
> ③ 配布先の正本である `REGIME.md` `## 情報代謝設定` を読んでいなかった。
> 是正後は追記方向に依らない増分行数のみを数え、budget は REGIME → config の順で解決する。
> 回帰テストに「先頭 append でも末尾 append でも同じ増分」「REGIME が config より優先」を追加。
>
> **実装中に発見した追加欠陥と是正（spec 起草時には未把握）**: signal-scan は日次 cron だが、
> 既存 3 検知器のタイトルが測定値（`PR #1 が 18 日間 open のまま`）を含むため日付が変わるたびに
> タイトルが変わり、F1-3「open の同一タイトルなら skip」の dedup が毎日外れていた。
> 実害 = 同一 3 PR について **27 件の重複 Issue**（#210〜#246、2026-08-28〜09-05）。
> 検知器を 2 本足すとこの増殖が加速するため、PR-E で**タイトルを信号の同一性のみで構成し
> 測定値を body へ移す**是正を同梱した（不変条件 I-4「常時発火する検知を作らない」の実装面での担保）。
> 回帰テストに「同じ信号は測定値が変わってもタイトルが変わらない」不変条件を追加。
> **旧タイトルの 27 件は自動では閉じない**（AI が他人の Issue を一括 close しない）— 人間の棚卸し対象。

### 規範メタデータ

```yaml
stage: S4          # 保守段階の規範（代謝は S4 の機構）
review_trigger:
  - measured: 停滞検知の起票後 2 cycle 以内に reindex が走らない状態が 2 回続いたら、閾値でなく運用の設計を再問
```

---

## 実装しないもの（明示的スコープ外・出典付き）

| 除外 | 理由 |
|---|---|
| **コードのナレッジグラフ標準装備**（`.mcp.json` 配布 / KG skill / 規範グラフ） | 本 spec は点検清算に閉じる。KG は `delivery/ANALYSIS-code-knowledge-graph-2026-09-05.md` §いま出ている案 2「E → F/A → C の実測 → B の判断」の順序に従い、配布先での一次計測（出来事）を経てから別 spec で扱う。`dh-manifest.yml:69-70` U-5「還流するのは機構ではなくそれを必要とした出来事」 |
| **`GH_REVIEW_PAT` の再発行** | 人間専管（secrets）。AI は触れない |
| **代謝の実行（reindex）** | 既存機構（`layer0-reindex-librarian`）の運用であって仕様変更ではない。本 spec は検知のみ |
| **配布先向けの宣言層検査** | `harness-verifier/` は配布されない（I-6）。配布先の同型検査（kakuman の `check-*`）は既に存在し、その DH への還流は `UPSTREAM-DECISION-2026-08-26.md` 順位 1・2 の採否欄（26 件とも未記入）で別途扱う |
| **`crosscut-verifier-philosophy` の本実装** | v5.0.0 から 6 回後送された別案件（SK-08）。本 spec は「凍結 or 廃止の決定が無い」ことを F2 の `graph_excluded` 宣言で可視化するに留める |
| **`.claude/agents/` の kakuman への配布** | TP-12 は配布の欠落を指摘するが、配布判断は L0 対話（配布先の REGIME）の領分 |

---

## 判断点（人間レビュー / 実装前 Council で確定するもの）

> **確定状況（2026-09-05、ひでさん発話）**: D-1 / D-2 / D-6 / D-7 の 4 件は下表のとおり確定した。
> D-3 / D-4 / D-5 は Council 諮問が先で未着手。**確定は着手の承認であって規範改変の内容確定ではない**
> （`escalation-matrix.md:31` — `.claude/skills/**` / `VERSION` / `templates/**` の改変は実装前 Council 諮問 +
> 献上時の人間判定を別途要する）。D-1 の実装（PR-A）は VERSION と `dev-env-spec.md` の両方に触るため、
> 本 spec の起草時点で必要な Council 諮問を通してから着手する。

| 決定 | 確定内容（2026-09-05） | 影響する PR |
|---|---|---|
| **D-1** | **VERSION = 6.15.0**。F1 が定める新規則（その版の critical が全部 master に入った時点で昇格）を実態に当てた帰結。v6.12.0 の critical（F1/F2/F5）も v6.15.0 の critical（F1/F2）も master 済み。副作用として未実装のまま追い越された v6.13.0 / v6.14.0 は、実装時に番号を付け替える（**spec 番号 = 起草時の予約であって release 番号ではない**旨を F1 に明記する） | PR-A |
| **D-2** | **skill 4 本は node 登録・script 4 本は `graph_excluded` に理由付きで明示**。script は実行グラフの経路ではなく検査器なので性質が違う。HV-04 の 2 edge は `source` を実態（`council-log-sync.py` / `council-axis-audit.py`）に合わせる | PR-B |
| **D-6** | **配布先 CLAUDE.md に 1 行**で参照させる。DH 側の毎サイクル購読量を増やさず、RL が効くべき場所（配布先 CLAUDE.md を書く時）で確実に読まれる。純化 RL 自身の「常駐は grep 到達前に踏むものだけ」とも整合 | PR-D |
| **D-7** | **gemini-review の停止を正として auto-merge の条件 4.5 から外す**。4 ヶ月の沈黙を「使われていない」の証拠と見る。条件が実質 1 本なのに 2 本あるように見える現状（宣言と実態の乖離）を解消する。今後の再沈黙は検知器 (e) が拾う | F7 の続き |

| # | 判断点 | 選択肢 | 起票先 |
|---|---|---|---|
| **D-1** | VERSION の確定値 | (A) v6.12.0（最初の未昇格実装に合わせる）/ (B) v6.15.0（最後の実装済み spec に合わせる）/ (C) v6.17.0（本 spec で一気に揃える） | 人間 |
| **D-2** | GRAPH.yml 未登録 4 skill + script 4 本 + HV-04 の 2 edge の処遇 | 登録 / `graph_excluded` 明示 / edge 削除 | 人間（`verifier-philosophy` の凍結判断は Council 寄り） |
| **D-3** | skill 内 COUNCIL-LOG の処遇 | 13 件転記 → (i) `.gitignore` 化 / (ii) `history/` へ移送 / (iii) manifest `never_touch` へ明示 | **Council**（「社外秘」宣言と配布実態の矛盾 = 不可逆性を含む） |
| **D-4** | `rm -rf` vs Level B 同居の調停方式 | (i) manifest に DH 所有 dir を明示列挙して選択同期を正典化 / (ii) Level B を別ディレクトリへ分離（v5.0.0 の「物理分離撤回」を覆す = major 級） | **Council**（v5.0.0 と v5.21.0 の 2 決定の調停） |
| **D-5** | Level A E-3 の改訂形 | (i) Windows native を列挙に追加 / (ii) 「対象 OS を明示せよ」という宣言要求に変更 | **Council**（規範文書改変） |
| **D-6** | RL の読込経路 | (i) L1 SKILL.md へ配線（購読量増）/ (ii) 配布先 CLAUDE.md 1 行 / (iii) 随時 reference と再定義 | 人間 |
| **D-7** | gemini-review の扱い | (i) 復旧させる / (ii) 停止を正として auto-merge 条件 4.5 から外す | 人間 |

---

## 実装順序と PR 分割

I-1（是正と検査は同一 PR）を守りつつ、依存順に分ける。

| 順 | PR | 内容 | 依存 |
|---|---|---|---|
| 1 | **PR-A** | F1（VERSION 規則 + 3 点の版整合 + 版整合検査） | 無し。**本 spec 自身の版番号確定を含むため最初** |
| 2 | **PR-B** | F2（GRAPH 是正 + 網羅性検査 + source 実質検査 + G-5 計数） | PR-A（検査 8 の器を PR-A で作る） |
| 3 | **PR-C** | F4（manifest 分類 + UPDATE.md 手順 + 分類網羅検査） | PR-A、D-4 の Council |
| 4 | **PR-D** | F6（RL 配線 + README SSOT + 件数一致検査） | PR-A、D-6 |
| 5 | **PR-E** | F7 + F8（`check_pat` 有効性 + signal-scan 検知器 (e)(f)） | 無し（並行可） |
| 6 | **PR-F** | F3（COUNCIL-LOG 転記 + 配布除外 + 配布物 state 検査） | D-3 の Council |
| 7 | **PR-G** | F5（E-3 改訂） | D-5 の Council |

**PR-A は他のすべてに先行する**。判断キット Q9-A（2026-09-04 にひでさんが「別 PR で先に揃える」を選択、未着手）が
本 spec の PR-A に相当する。

---

## モード判定・実装体制

- **M2**（標準モード）。DH 本体の規範改変であり、L1 実装後に `layer1-independent-reviewer` の独立検証を通す
- **dev_mode**: `autonomous`（DH 本体は既存どおり）。ただし **auto-merge は F7 の PAT 再発行まで機能しない**ため、
  本 spec 実装期間中の PR は人間 merge になる
- **CTL**: 変更なし。D-3 / D-4 / D-5 の 3 諮問を要する

---

## 申し送り

- **本 spec 自身が点検対象の再演になっていないか**: 本 spec は新規規範（F1 の昇格規則 / F2〜F4・F6 の検査 /
  F7・F8 の検知器）を 7 つ足す。`Council f5fc45`「減らす・時限化」の圧に対しては、**全項目に
  `review_trigger` を付し（I-7）、6 cycle 連続 0 件で降格候補にする**ことで相殺を図っている。
  ただし**失効判定を実行する走査器（v6.13.0 F5）は未着地**であり、時限メタデータを付けても現状は誰も読まない。
  この構造は F6 の「配布できるが読まれない RL」と同型であり、v6.13.0 F5 が着地するまで本 spec の時限は名目にとどまる
- **検査 8 の肥大**: F1 / F2 / F4 / F6 を 1 ファイルに集約するが、4 種類の異なる宣言を 1 検査器が読むことになる。
  肥大したら分割する（判定基準は「1 検査器 = 1 宣言ファイル」に割る）
- **DH は配布先を dogfood できない**: 本 spec の検査はすべて DH 本体の自己検査であり、
  配布先で同型の drift が起きても検出しない（I-6）。配布先側の検査は kakuman が既に持つ（`check-traps-sync` 等）ため、
  その還流（`UPSTREAM-DECISION-2026-08-26.md` 順位 1・2）が次の論点になる
- **(g) の観測**: PAT 失効は本 spec 起草中に実際に発生し、`evaluate` が red のまま PR が滞留した。
  これは `dh-manifest.yml` U-5 が要求する「機構を必要とした出来事」そのものであり、F7 の検知器はこの日付を根拠に持つ

---

## 履歴

- 2026-09-05: **PR-E 実装**（ひでさん「マージして進める」）。F7（`check_pat` 有効性検査 + 検知器 (e) workflow_silence）と
  F8（検知器 (f) metabolism_stall）を実装。加えて実装中に発見した 2 件を同梱:
  (i) **signal-scan の dedup が毎日外れる欠陥**（タイトルに測定値を含むため。実害 = 重複 Issue 27 件）→ タイトルを同一性のみに是正。
  検知器を足す前に直さないと増殖が加速するため、I-4 の実装面の担保として同 PR に含めた。
  (ii) **`signal-scan.yml` が `check_template_sync.py` の `WORKFLOW_PAIRS` に未登録**（5 組目のペアが黙って未検査）→ 登録。
  本 PR が `signal-scan.yml` と template の両方を編集するため、未検査のままだと片側だけ変えても検出されない。
  この (ii) は §0 の「実体 → 宣言」欠落の同型例であり、F2 / F4 が扱う欠落と同じ型が `check_template_sync` にもあったことを示す。
  検証: `check_template_sync` 5 ペア IN_SYNC / `test-signal-scan.py` 全通過（新規 17 assert）/ `harness-verifier --strict` 7 検査 PASS。
- 2026-09-05: **PR-E 自己レビュー是正**。検知器 (f) の初版が 3 重に誤測していたのを修正（追記方向 / budget の単位 /
  budget の解決順）。併せて一度加えた時間トリガを `metabolism-regime`「リズム（決定2・確定）」との矛盾ゆえ撤回。
  その過程で **(h) の根本原因**（reindex-protocol §2 M2 の prefix checksum が先頭 append と非互換で
  guard が構造的に通らない。記録済み checksum は 4 本とも現ファイルと不一致）を実測で特定し §F8 に記録。
  protocol の是正は L-FROZEN-META ゆえ本 spec の対象外（Council + 人間）。
- 2026-09-05: L0 起草（本ファイル）。起点 = ひでさん「点検清算 (a)〜(h) を L0 で仕様化して」。
  一次材料 = `delivery/ANALYSIS-code-knowledge-graph-2026-09-05.md` §DH 点検所見。全数値は同日再実測。
  Council 未諮問（D-3 / D-4 / D-5 が実装前諮問の対象）
