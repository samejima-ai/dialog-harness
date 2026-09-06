# upgrade-spec v6.17.0 — 宣言層の lock-step 清算（点検 (a)〜(h)）

> **状態: 実装中（F1 / F2 / F4 / F5 / F6 / F7 / F8 済 / F3 未）**。本仕様の実装は escalation-matrix「規範文書改変」行
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
| (e) | Level A checklist E-3 が Windows native を列挙しない | 規範と実態の不整合 | F5 | F5（検査 1 に `target_os` を追加。起草時「無し」は撤回） |
| (f) | RL が届くのに読込経路が無い + 現況索引 2 箇所 stale | 配線の欠落 | F6 | F6（RL 索引の被覆一致検査） |
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

**配布先の版識別の実測（2026-09-06 訂正）**: 当初 Council 哲学者軸の指摘を受けて
「配布先は版番号で自分を識別する、という前提は半分しか成立していない」と書いたが、
**この記述自体が誤りだった**（merge 前検証で判明）。訂正して記録する。

| 配布先 | 版の記録場所 | 内容 |
|---|---|---|
| cc-cockpit | `VERSION` + `dh-manifest.yml` + `CLAUDE.md:17` | `6.11.0` |
| kakuman-platform-v3.0 | **`REGIME.md:447-449`**（`UPDATE.md` §3 が定める正規の記録先） | `updated_to: 6.15 系（VERSION 6.11.0 のまま機能追加。DH PR #200〜#209 全反映）` / `pinned_sha: 5161cbf` |

kakuman は `VERSION` ファイルこそ持たないが、**`UPDATE.md` §3「更新後、プロジェクトの REGIME.md に
更新先バージョンと PIN を記録する」に手順どおり従っている**。初回の実測は `VERSION` ファイルの
有無だけを見て「機械可読な宣言を持たない」と誤断した（`CLAUDE.md` の自然言語 1 行は補助的な記述であって
版の記録先ではない）。

さらに重要なことに、**kakuman は独立に「6.15 系」と判定し、`VERSION 6.11.0 のまま機能追加` という
ズレそのものを 2026-08-28 の時点で記録していた**。これは本 spec が F1 で扱う drift を配布先が
先に発見していたことを意味し、D-1 で確定した VERSION = 6.15.0 を外部から裏づける。

したがって「配布時の同梱規律が要る」という当初の結論も**そのままでは成立しない** — 記録経路は
既に `UPDATE.md` §3 として存在し、機能している。残る論点は「`VERSION` ファイル自体を同梱するか、
`REGIME.md` の記録だけで足りるか」という設計判断であり、次サイクルの検討事項として残す。

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
- `dev-env-spec.md` §バージョン履歴 の**凍結**（凍結マーカー欠落 / v4.2 より後の項目の追記 = FAIL）。
  **stale 宣言は 3 点ではなく 4 点あった**（2026-09-05、Council 開発者軸の指摘）— 4 点目は
  新規則を置こうとしている当の節の中で **v4.2 のまま 2 メジャー分死んでいる**。
  二択（追いつかせる / ポインタ化して明示的に廃止）のうち**後者を採った** — v5 系以降の内容は
  `dh-upgrades/` と `history/CHANGELOG.md` が正本で、ここに再掲すると実体の二重定義になるため
  （純化 RL §2）。ゆえに検査するのは「VERSION に追いついているか」ではなく「凍結が守られているか」。
  実装 = `declaration_coverage.py` の検査 6
- `dh-upgrades/upgrade-spec-v*.md` の状態行が上記値域に含まれること（値域外 = FAIL）
- 状態行が `実装済み` を名乗る spec の版 ≤ VERSION（超過 = FAIL）
- 状態行が `L0 起草` のまま、その spec 自身の本文が実装を名乗っている（= WARN。
  「起草のまま実装が入った」の検出）

> **検査 4 の方式を `git log --grep` から file-local 判定へ変更（2026-09-05、Council 開発者軸の指摘を実測で確認）**:
> 起草時の設計は `git log --grep "v6.13.0"` で検出する案だったが、実測すると
> **v6.13.0 に 4 件 / v6.14.0 に 2 件 / v6.16.0 に 2 件**がヒットし、その大半は
> **当該 spec 自身の起草 commit**（`879d0b7` / `f24bcca` / `982eae0` / `c819509`）と
> 個人名の一括匿名化 sweep（`e32da99`）である。つまり導入初日から非ゼロで、
> 全 draft が実装されるまで 0 にならない = 不変条件 **I-4「常時発火する検知を作らない」に違反**する。
>
> 代替の file-local 判定（状態行が `L0 起草` **かつ**同ファイル本文が `実装済み（PR #` / `実装（PR #` を含む）は、
> 現ツリー実測で **v6.11.0 と v6.15.0 の 2 件**（いずれも真陽性 = 実装済みなのに状態行が起草のまま）に発火し、
> 偽陽性 0。recall は同等（両方式とも v6.12.0 は状態行が `Council 諮問通過` のため取りこぼす）。
> **git 履歴に依存しないので配布先でも同じ判定ができる**という副次利得もある。

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

> **【2026-09-06 撤回】起草時は「無し（checklist は人間判断項目であり機械検証対象外）」と書いたが、
> これは事実誤認だった**（Council D-5 で開発者軸が実測により反証）。`frontmatter.py:14` の
> `REQUIRED_FIELDS` は汎用ループであり、`target_os` を足す 2 行の変更で検査 1 が宣言不在を
> FAIL 化できる。**検証できないのは要求の性質であって項目の宿命ではない** — 旧 E-3「OS 非依存」は
> 動作そのものを要求しており確かに検証できなかったが、「対象 OS を宣言せよ」に改めた結果、
> 宣言の存在・値域・書式は決定論で検証可能になった。

- **検査 1（frontmatter 整合性）を拡張**: `REQUIRED_FIELDS` に `target_os` を追加し、
  宣言不在・値域外（`TARGET_OS_VALUES` = any / windows / macos / linux / wsl）・
  書式不正（`+` 区切り以外）・`any` と個別 OS の混在を FAIL にする。
  語彙を enum で固定するのは、windows / Windows / win32 の表記揺れが検証を空文化させるため
  （3 軸すべてが独立に指摘した成立条件）
- 併せて F2 の GRAPH 網羅性検査が「規格外のまま常駐する skill」の存在自体を可視化する

**検証できない残り**: 宣言と実体の一致（`target_os: any` と書いた bash 専用 skill）は検出できない。
検証しているのは「どこで動くと言ったか」であって「本当に動くか」ではない。
また `scripts/` 配下は skills を対象とする検査 1 の射程外で、`test-council-*.sh` の bash 依存は
本改訂では捕捉されない（minority_opinion に記録）。

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

- `templates/rules/common/*.md` の実ファイルと README §common の列挙が一致すること（不一致 = FAIL）。
  kakuman の `check-traps-sync.mjs` が「常時索引 ⇄ 全文」で実装した被覆一意性検査の、DH 側 RL への転用。
  **実装は件数ではなくファイル名で突き合わせる**（PR-D。件数一致は名前が入れ替わっても通ってしまうため、
  起草時の「件数一致」より厳密にした）

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
| **D-7** | **確定内容: gemini-review の停止を正として auto-merge の条件 4.5 から外す**（4 ヶ月の沈黙を「使われていない」の証拠と見る）。**ただし実装は 2026-09-06 に撤回**（下記） | F7 の続き・**再判断待ち** |

> **D-7 の実装を撤回した（2026-09-06、merge 前検証で判明）**。確定した判断そのものではなく、
> 判断の根拠として AI が提示した**事実の前提が 2 点とも誤っていた**:
>
> 1. **`$GR` は gemini-review ではない**。`auto-merge.yml:354` の抽出は `select(.name == "review")` で、
>    DH では `claude-review.yml` と `gemini-review.yml` が**どちらも job 名 `review`** を持つ（実測）。
>    ゆえに `$GR` は生きている claude-review を拾いうる。「4 ヶ月沈黙ゆえ条件 4.5 の実体は
>    harness-verify のみ」という前提が成立しない。
> 2. **配布先で auto-merge が無言で死ぬ**。`auto-merge.yml` は配布されるが `harness-verify.yml` は
>    配布されない（`templates/github-workflows/` に無い）。条件 4.5 を `$HV` 単独にすると、
>    配布先には `verify` という名の check が存在しないため（実測: kakuman の jobs =
>    `ci-lint` / `ci-build` / `claude-review` / `review` / …）条件が恒久的に不成立になる。
>
> **本件は「check 名で gemini-review と claude-review を区別できない」という、本 PR 以前から在る
> 構造的欠陥を露呈させた**。D-7 を実装するには先にその区別を可能にする必要があり、
> それ自体が別の判断点（job 名の変更 = 配布先の CI 名にも波及）。よって D-7 は再判断に戻す。

| # | 判断点 | 選択肢 | 起票先 |
|---|---|---|---|
| **D-1** | VERSION の確定値 | (A) v6.12.0（最初の未昇格実装に合わせる）/ (B) v6.15.0（最後の実装済み spec に合わせる）/ (C) v6.17.0（本 spec で一気に揃える） | 人間 |
| **D-2** | GRAPH.yml 未登録 4 skill + script 4 本 + HV-04 の 2 edge の処遇 | 登録 / `graph_excluded` 明示 / edge 削除 | 人間（`verifier-philosophy` の凍結判断は Council 寄り） |
| **D-3** | skill 内 COUNCIL-LOG の処遇 | 13 件転記 → (i) `.gitignore` 化 / (ii) `history/` へ移送 / (iii) manifest `never_touch` へ明示 | **Council**（「社外秘」宣言と配布実態の矛盾 = 不可逆性を含む） |
| **D-4** | `rm -rf` vs Level B 同居の調停方式 | (i) manifest に DH 所有 dir を明示列挙して選択同期を正典化 / (ii) Level B を別ディレクトリへ分離（v5.0.0 の「物理分離撤回」を覆す = major 級） | **Council**（v5.0.0 と v5.21.0 の 2 決定の調停） |
| **D-5** | Level A E-3 の改訂形 | (i) Windows native を列挙に追加 / (ii) 「対象 OS を明示せよ」という宣言要求に変更 | **Council**（規範文書改変） |
| **D-6** | RL の読込経路 | (i) L1 SKILL.md へ配線（購読量増）/ (ii) 配布先 CLAUDE.md 1 行 / (iii) 随時 reference と再定義 | 人間 |
| **D-7** | gemini-review の扱い | (i) 復旧させる / (ii) 停止を正として auto-merge 条件 4.5 から外す | 人間 |

> **D-3 / D-4 / D-5 の Council 諮問を完了した（2026-09-06）**。3 件とも `consensus_mode: auto_agree`
> で、判定は下表。諮問記録は `history/COUNCIL-LOG.md` の `council-2026-09-06T09:30:01Z-c575bb`（D-3）/
> `council-2026-09-06T09:42:00Z-mfst04`（D-4）/ `council-2026-09-06T09:45:00Z-osdcl5`（D-5）。
> **判定は判断であって決定ではない**（`final_decision` は 3 件とも null）。実装は合意プロセスを経る。

| 決定 | Council 判定（2026-09-06） | jc | 必須随伴条件 | PR |
|---|---|---|---|---|
| **D-3** | **(ii) `history/` へ移送**。保守性軸（`council-log-sync.py:181` の `_ENTRY_START` が `^- invocation_id:` 固定ゆえ見出し形式は構造的にパース不能）と前提への問い軸（「最も秘匿すべきと宣言した場所が最も広く配られる場所だった」）が共有トークン 0 で収斂 | 0.71 | (a) skill 内ログ L11 の「社外秘ゆえ skill 内部に閉じる」記述の訂正 (b) 旧パス参照箇所（`SKILL.md` / `output-format.md` 等）の追随修正 (c) **`never_touch` と `overwrite` の優先順位規則の明文化** — 経営者軸「例外パスの解決規則が未定義」と開発者軸「`never_touch` を強制するコードが存在しない（`dh-manifest.yml:96` の自認）」が別次元から指した同一の構造的欠落で、どの選択肢を採っても残る | PR-F |
| **D-4** | **(i) manifest に DH 所有 dir を明示列挙して選択同期を正典化**。ROI / 保守性 / 前提への問い の 3 次元が共有トークン 0 で全会一致（reason_divergence） | 0.85 | (a) **網羅性センサー**: DH 実在の `.claude/skills/` 直下 dir 集合 == manifest overwrite 列挙 の決定論突合（不一致 = FAIL）。3 軸独立で「無ければ問題の先送り」と指摘された成立条件 (b) **I-1 との整理を spec 本文に明記**: 列挙は「除外リスト（allowlist）」ではなく「所有の宣言（ownership declaration）」と語を分ける (c) 二重宣言の単一情報源を `GRAPH.yml` nodes 側に固定し manifest 列挙は導出／突合に位置づける (d) 同期手順は「列挙 dir 単位の `rm -rf && cp -r`」とし v5.21.0 の orphan 除去目的を dir 単位で保つ | PR-C |
| **D-5** | **(ii) 宣言要求へ改訂**。ただし単なる文言差し替えではなく **frontmatter への機械可読キー化（`target_os`）を成立条件**とする。値の語彙を enum で固定し `frontmatter.py:14` の `REQUIRED_FIELDS` に追加して検査 1 で宣言不在を FAIL 化する | 0.82 | **§F5 の「再発防止機構: 無し」は事実誤認として撤回**（`frontmatter.py` の `REQUIRED_FIELDS` は汎用ループで 2 行の変更で機械検証できることを実測で確認）。3 軸すべてが独立に機械可読キー化を必須条件として挙げた — 伴わなければ「description 自由文への記載＝適合」の自己認証に堕し、E-3 は空文から**偽証可能な空文**へ移るだけ | PR-G |

> **D-5 の非対称性の正当化**（哲学者軸の問いに対する判定の応答）: 本 spec は「宣言と実体の乖離を閉じる」
> ものだが、E-3 だけは乖離を閉じる手段として実体側でなく**宣言側を動かしている**。判定はこれを
> 非対称の例外ではなく**破綻した規範の誠実化**として正当化した — 他 7 項目は実体を規範に寄せれば
> 閉じるが、E-3 の元の要求「OS 非依存」は機械検証不可かつ達成不能（`install.ps1` は PowerShell 専用、
> `test-council-*.sh` は bash 専用が既存配布物に実在）という二重の破綻を抱えており、
> **閉じる先が実体側に存在しない**。

> **3 判定に共通して残った留保**（いずれも minority_opinion / 本文に記録済み）: 「静かな失敗」
> — 配られない・動かない・記録されないという失敗が誰も困らせないまま持続する構造は、
> どの判定でも解消されない。痛まない乖離を検知する経路は本 spec 完了後も未整備である。


---

## 実装順序と PR 分割

I-1（是正と検査は同一 PR）を守りつつ、依存順に分ける。

| 順 | PR | 内容 | 依存 |
|---|---|---|---|
| 1 | **PR-A** | F1（VERSION 規則 + 3 点の版整合 + 版整合検査） | 無し。**本 spec 自身の版番号確定を含むため最初** |
| 2 | **PR-B** | F2（GRAPH 是正 + 網羅性検査 + source 実質検査 + G-5 計数） | PR-A（検査 8 の器を PR-A で作る） |
| 3 | **PR-C** | F4（manifest 分類 + UPDATE.md 手順 + 分類網羅検査） | PR-A（済）、D-4 の Council（**済 2026-09-06**） |
| 4 | **PR-D** | F6（RL 配線 + README SSOT + 被覆一致検査） | PR-A、D-6 |
| 5 | **PR-E** | F7 + F8（`check_pat` 有効性 + signal-scan 検知器 (e)(f)） | 無し（並行可） |
| 6 | **PR-F** | F3（COUNCIL-LOG 転記 + 配布除外 + 配布物 state 検査） | D-3 の Council（**済 2026-09-06**） |
| 7 | **PR-G** | F5（E-3 改訂 + target_os frontmatter 化） | D-5 の Council（**済 2026-09-06**） |

**PR-A は他のすべてに先行する**。判断キット Q9-A（2026-09-04 にひでさんが「別 PR で先に揃える」を選択、未着手）が
本 spec の PR-A に相当する。

---

## モード判定・実装体制

- **M2**（標準モード）。DH 本体の規範改変であり、L1 実装後に `layer1-independent-reviewer` の独立検証を通す
- **dev_mode**: `autonomous`（DH 本体は既存どおり）。ただし **auto-merge は F7 の PAT 再発行まで機能しない**ため、
  本 spec 実装期間中の PR は人間 merge になる
- **CTL**: D-3 / D-4 / D-5 の 3 諮問を 2026-09-06 に完了（3 件とも `auto_agree`）。同期後の CTL は **CTL-2**（評価済み 144 件 / 一致 134 件 / rate 0.9306）。なお `.council-ctl.json` の投影は CTL-1 のままで更新経路が走っていない（申し送り）

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

- 2026-09-06: **PR-D 実装**（F6）。D-6 の確定（配布先 CLAUDE.md に 1 行）に従い、
  `dev-env-spec.md` に **G-RULES 標準行**を新設した（既存の G-MODEL 行と同型 —
  「L0 は CLAUDE.md 生成時に正本参照を標準で 1 行含める」という先例をそのまま踏襲）。
  L1 SKILL.md に配線しない理由（D-6 が (i) を採らなかった理由）を明記した:
  DH 側の読込順序に足すと全 cycle で 6 本が常時購読対象になり購読量が増えるが、
  RL が効くべきなのは配布先の実装時であり、配布先 CLAUDE.md の 1 行なら効く場所で確実に読まれる。
  併せて現況の SSOT を `templates/rules/README.md` §common/ の現況 に一本化し、
  `dev-env-spec.md` の配置 tree（3 本を落としていた）を README 参照 1 行に置換した（純化 RL §2 の自己適用）。
  **実測で spec の数値を訂正**: spec は README の列挙を 3 本・欠落 3 本としていたが、
  実際は列挙 4 本・欠落 2 本（`claude-md-purity.rules.md` / `telemetry-reflux.rules.md`）だった
  — `agentshield-reference.md` は列挙済み。欠落を塞いで 6 本すべてを列挙した。
  再発防止として検査 8 に **検査 10（F6 RL 現況被覆）** を追加。件数ではなく**ファイル名で突き合わせる**
  （件数一致は名前が入れ替わっても通ってしまう）。初版は README 本文中のバッククォート付き `.md` を
  すべて拾い、override 例の `.dh/rules/common/...` や他 skill の参照先まで RL 扱いして 4 件の偽陽性を
  出したため、箇条書き見出し位置（`^- \`<name>.md\``）に限定して精度を上げた。
  検証: 検査 10 の回帰テスト 5 ケース追加（列挙漏れ / 実在しない列挙 / 現況節の欠落を検出、
  RL を持たないツリーでは skip = 配布先で壊れない、override 例の `.dh/` パスを拾わない）/
  `harness-verifier --strict` 8 検査 PASS（実ファイル 6 本 = README 列挙 6 本）/
  回帰テスト 5 本（declaration-coverage / execution-graph / signal-scan / hook-wiring /
  council-axis-audit）全通過。
  **申し送り**: `.dh/rules/` は L0 が環境構築時に配置する override 先として複数の RL が宣言するが
  （`claude-md-purity.rules.md:75` / `minimalism-ladder.rules.md:89`）、`dh-manifest.yml` に
  `rules` の記載は無い（配布は `templates/` の overwrite に含まれる形）。この配置経路の
  manifest 明示は F4（PR-C・D-4 の Council 待ち）の分類網羅で扱う。
- 2026-09-06: **PR-B 実装**（F2）。D-2 の確定に従い、GRAPH.yml に未登録だった 4 skill を処遇し
  （`crosscut-hook-observer` / `crosscut-continuous-learning` / `rtk-integration` を node 登録、
  `crosscut-verifier-philosophy` は発動禁止 placeholder ゆえ新設 `graph_excluded` に理由付きで宣言）、
  未参照 script 4 本（`check_template_sync` / `pr-audit` / `reviewer-misjudgment` / `upstream-scan`）を
  `graph_excluded` に「実行グラフの経路ではなく検査器・分析器」として宣言した。
  検査 8 に F2 分（検査 7 skill 網羅 = FAIL / 検査 8 script 網羅 = WARN / 検査 9 source 実質 = WARN）を追加し、
  `execution_graph.py` G-5 の **prefix フィルタを除去**（`startswith(("layer","crosscut"))` が
  `rtk-integration` を黙って落としていた。`glossary.py:250` と同型の欠陥）+ 宣言外 dir の計数を追加した。
  **HV-04 の是正は edge 削除を選んだ**: `layer0-spec-architect → council-performance` /
  `→ harness-benchmark` の 2 edge は `source: ritual-protocol.md` を宣言するが、同 protocol の F1 手順が
  実際に呼ぶのは `council-log-sync.py`（:88-89）と `council-axis-audit.py`（:94-95）のみで、
  この 2 本を呼ぶ手順は存在しない（2026-09-06 実測。他の呼び出し元も `delivery/` の実行例のみで 0 件）。
  I-2「実装が正・宣言が従」に従い宣言側を落とした。
  副作用として prefix フィルタ除去で G-5 の検出が 0 → 3 件に増えたが、一次情報で確認して
  **3 件とも誤検出**と判定し `g5_false_positives` に理由付きで記録した
  （「auto-merge を有効化して」というユーザー発話例 / `council-axis-audit.py` の出力を人間に提示する
  観測窓の記述 / 「auto-merge ラベル自動付与は廃止」という否定文脈）。
  検査 9 は初版が実リポで 2 件の偽陽性を出したため、**層 prefix を落とした略記**（SKILL.md 本文の
  「L1（autonomous-dev）」表記）を一致とみなし、**self-loop を対象外**にして精度を上げた
  （I-4「常時発火する検知を作らない」の担保）。
  併せて `harness-verifier/README.md` の検証項目表が見出し「8 検証項目」に対し 5 行しか無かったのを
  8 行に是正した — **本 PR の主題である「実体 → 宣言」の欠落が README 自身にあった**。
  検証: 検査 8 回帰テストに F2 分 11 ケースを追加（欠陥を仕込めば検出・健全なら 0 件を合成ツリーで実証）/
  `harness-verifier --strict` 8 検査 PASS（検出 0 件・宣言外 dir 0 件）/
  `test-execution-graph` / `test-signal-scan` / `test-hook-wiring` 全通過。
  **申し送り**: edge 削除の結果 `council-performance` / `harness-benchmark` の 2 tool node は起動元を
  持たなくなった。`graph_excluded` への移動が筋だが、D-2 の確定文言（source を実態に合わせる）を
  超える判断のため本 PR では node を残した。次サイクルの判断対象。
- 2026-09-05: **PR-E 実装**（ひでさん「マージして進める」）。F7（`check_pat` 有効性検査 + 検知器 (e) workflow_silence）と
  F8（検知器 (f) metabolism_stall）を実装。加えて実装中に発見した 2 件を同梱:
  (i) **signal-scan の dedup が毎日外れる欠陥**（タイトルに測定値を含むため。実害 = 重複 Issue 27 件）→ タイトルを同一性のみに是正。
  検知器を足す前に直さないと増殖が加速するため、I-4 の実装面の担保として同 PR に含めた。
  (ii) **`signal-scan.yml` が `check_template_sync.py` の `WORKFLOW_PAIRS` に未登録**（5 組目のペアが黙って未検査）→ 登録。
  本 PR が `signal-scan.yml` と template の両方を編集するため、未検査のままだと片側だけ変えても検出されない。
  この (ii) は §0 の「実体 → 宣言」欠落の同型例であり、F2 / F4 が扱う欠落と同じ型が `check_template_sync` にもあったことを示す。
  検証: `check_template_sync` 5 ペア IN_SYNC / `test-signal-scan.py` 全通過（新規 17 assert）/ `harness-verifier --strict` 7 検査 PASS。
- 2026-09-06: **merge 前検証で 5 件の実在欠陥を是正**（150 エージェント / 6 レンズ）。反証層は 48 件すべてを
  棄却したが、**複数の独立レンズが収束した指摘を一次情報で自分で確かめ直したところ 5 件が実在した**
  （反証側に「迷ったら refuted に倒す」と指示した偏りが効いていた）。是正:
  ① **D-7 の実装を撤回**（前提 2 点が誤り・配布先の auto-merge を無言で殺す。上記 §判断点 D-7 参照）
  ② v6.11.0 の状態行の VERSION 誤記（6.15.0 → **6.11.0**。PR #186 = `3e3a8b2` が実際に上げた値）
  ③ v6.12.0 / v6.15.0 の状態行を `実装中` → `実装済み` へ（自分で定めた §昇格の実行 step 3 と矛盾していた）
  ④ 存在しない「リリース手順のチェックリスト」への参照を規範から除去（Council 条件 (8) は未了と明記）
  ⑤ `harness-verifier/README.md` の「5 検証項目」→「8 検証項目」（本 PR の主題である宣言の鮮度欠落を自分で拡大していた）
  加えて **§F1「配布先の版識別」の記述自体が誤りだった**ことを訂正 — kakuman は `REGIME.md:447` に
  `updated_to: 6.15 系` / `pinned_sha` を `UPDATE.md` §3 の手順どおり記録しており、
  しかも独立に「6.15 系」と判定していた（D-1 の外部裏づけになる）。
- 2026-09-05: **PR-A 実装**（F1）。実装前 Council 諮問 `council-2026-09-05T23:40:00Z-vrsn01`
  （`escalation-matrix.md:31` に従う。3 軸とも stance B / dimension の共有トークン 0 = 冗長ではなく
  異なる次元からの一致 / weighted_score 8.58 / jc 0.78 / consensus_mode `escalate_to_human`）を通し、
  判定が付した **9 条件をすべて実装に反映**した。VERSION 6.11.0 → 6.15.0、`GRAPH.yml` を同一 commit で追随、
  `dev-env-spec.md:726` の**既存節を書き換え**（新節を作らず正典の二重化を避ける）、
  状態行 4 本を実態に是正、§バージョン履歴を v4.2 で凍結、`UPDATE.md` に一度きりの読み替え表、
  検査 8「宣言被覆」を新設（WARN は `git log --grep` でなく file-local 判定）。
  検査の**検出能力は合成ツリーで実証**（`scripts/test-declaration-coverage.py`、健全ツリー 0 件を基準線に
  6 欠陥をそれぞれ検出・偽陽性 0）。`implementer_consent` は null のまま = 合意プロセスは人間に残る。
- 2026-09-05: **PR-E 自己レビュー是正**。検知器 (f) の初版が 3 重に誤測していたのを修正（追記方向 / budget の単位 /
  budget の解決順）。併せて一度加えた時間トリガを `metabolism-regime`「リズム（決定2・確定）」との矛盾ゆえ撤回。
  その過程で **(h) の根本原因**（reindex-protocol §2 M2 の prefix checksum が先頭 append と非互換で
  guard が構造的に通らない。記録済み checksum は 4 本とも現ファイルと不一致）を実測で特定し §F8 に記録。
  protocol の是正は L-FROZEN-META ゆえ本 spec の対象外（Council + 人間）。
- 2026-09-05: L0 起草（本ファイル）。起点 = ひでさん「点検清算 (a)〜(h) を L0 で仕様化して」。
  一次材料 = `delivery/ANALYSIS-code-knowledge-graph-2026-09-05.md` §DH 点検所見。全数値は同日再実測。
  Council 未諮問（D-3 / D-4 / D-5 が実装前諮問の対象）
