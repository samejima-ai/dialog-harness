# upgrade-spec v6.14.0 — 開発日誌エージェント（観察の層を、判定の層から切り離して置く）

> **状態: L0 起草（人間レビュー待ち）**。本仕様の実装は escalation-matrix「規範文書改変」行に従い、
> 人間レビュー通過後・実装前に Council 諮問を経る。
> 起点: L0 対話（2026-08-26、ひでさん）の機能追加要求 ──
> 「開発日誌エージェント／モデル指定: haiku の最新／随所で非同期的にログや成果物を参照して
> 開発者（ユーザー）を観察する視点で開発についての日誌を綴る／日次で記録をまとめる／
> 開発日誌はメタハーネス開発（パブリックなため特定情報を含めない）とプロジェクト開発
> （各プロジェクト展開後の開発）で明確に分ける」。
> 振り返り儀式 F1〜F3 の実行結果は §1 に記す。

---

## 0. 位置づけ — DH に無いのは「観察の層」であって「振り返りの機構」ではない

DH には振り返りの機構が既に 4 つある。いずれも**過程を見て提案を出す**。日誌はそのどれでもない。

| 機構 | 局面 | 対象 | 出力 |
|---|---|---|---|
| 振り返り儀式 F1〜F3（`layer0-spec-architect`） | cycle **開始時** | 過去文脈 ⇔ 現欲求 | 照合・質問 |
| `crosscut-cycle-retrospective` | cycle **完了時** | その cycle の実行結果 | 学び + **改善提案** |
| `crosscut-continuous-learning` | 随時 | hook 観測ログのパターン | **promotion 候補** |
| `layer0-reindex-librarian` | cycle 境界 | history 蓄積 | 結晶化 + 購読量削減 |
| **本リリース: 開発日誌** | **日次** | **開発者（人間）の振る舞い** | **記録のみ**（提案・評価・スコアを出さない） |

空いていたのは「**人間を観察して、何も要求しない層**」である。既存 4 機構はすべて
機構を観察して人間に何かを要求する。日誌が提案を出し始めた瞬間、それは
`crosscut-cycle-retrospective` の劣化再実装になる。§不変条件 J-1 はこの一点を守るためにある。

さらに `delivery/DIAGNOSIS-loop-graph-engineering-2026-08-26.html` は F-08 として
**「DH に観測層が無い」**を挙げ、`delivery/UPSTREAM-DECISION-2026-08-26.md` 順位 3
（観測層の非ゲート化）をその直接解として推奨カットライン内に置いている。本リリースは
その観測層に最初の実体を与えるが、**ゲートには決してしない**（J-2）。

> **表記について**: バッククォート付きの参照はリポジトリルートからの実在パスで統一する。
> 例外は本仕様が**これから作る**パス（`history/dev-diary/` / `.claude/agents/dev-diarist.md` /
> `scripts/check-diary-safety.py` / `scripts/count-diary-references.py`）と、
> **存在しないことを指摘するために書いたパス**（`.claude/settings.json` — §8 未処理項目 1）である。

---

## 1. 振り返り儀式の実行結果（レベル 2 — 機能追加を含む対話）

### F1 過去文脈サマリ + CTL 同期 + 軸監査

- CTL 同期（`scripts/council-log-sync.py sync --prune --recompute`）: **63 件 / 評価済 58 件 /
  agreed 50 件 / rate 0.8621 → CTL-0**。`decision_category` 空欄 **5 件**（人間専管・繰越）
- 軸監査: `situational_modifier` 合計 **+1**（宣言 0）の不整合が継続。L0/D5 専管・繰越

### F2 認識ズレ検出 — 検出 2 件（いずれも本サイクル外で確定済み）

前回の L0 対話以降、**別セッション**が master へ 2 件を着地させていた。本サイクルの前提が動く。

| commit | 内容 | 本件への影響 |
|---|---|---|
| `f60ec5d`（#194） | 逆流路の観測器（v7 Phase 1）＋ 独立診断。DH v6.11.0 を **B−（思想・設計 A / 実行・配線 C）**、graph maturity 3/8 と評価 | 「宣言はある。配線がない」は役割境界の症状ではなく**グラフ全体の症状**であると再定義された。本仕様はその再定義を受けて書かれている |
| `94e8872`（#197） | stop ラベルが後付けでは効かない競合を修正（Council `amrace`） | v6.13.0 §F2 の territory の一部が先行して塞がれた |

### F2.5 CTL 事後評価

未評価 0 件（前サイクルで 3 件を `history/COUNCIL-LOG.md` へ書き戻し済み）。質問なしで F3 へ。

### F2.6 時限規範の再審 — 発火 1 件

`delivery/ANALYSIS-model-selection-2026-08-05.md` が `claude-haiku-4-5` を
**「後継（Haiku 5）は存在せず、バジェット層の現行正解。retirement 下限 2026-10-15」**と記録している。
本仕様がモデルを固定する以上、`review_trigger: model_generation` の付与は必須（§F4-2・§7）。

### F3 履歴更新予告

本仕様がマージされた時点で `history/CHANGELOG.md` へ儀式記録（レベル 2 / 検出 2 件）を追記する。
実際の書き込みは L1 献上時（`delivery-format.md` §履歴層更新差分）。

---

## 2. 本サイクルで確定させた事実（設計の土台）

いずれも本サイクルで**実測**した。推定ではない。

| # | 事実 | 測定 |
|---|---|---|
| A-1 | `harness-verifier/reports/hook-observations.jsonl` は **2 行**。両方とも 2026-05-11 の smoke test | `wc -l` = 2、両行に `"_smoke_test": true` |
| A-2 | 実観測は **3 ヶ月半・PR 100 本超にわたって 0 件** | 上記 2 行以降の追記なし |
| A-3 | それでも harness-verifier の検査 6「hook 観測一貫性」は **PASS（検出 0 件）** | `python3 harness-verifier/verify.py` |
| A-4 | `VERSION` は **6.11.0**。v6.12.0 / v6.13.0 は仕様がマージされただけで未実装 | `cat VERSION` |
| A-5 | `dh-manifest.yml` の `never_touch` に `history/` と `delivery/` があり、`upstream.scan` は `.claude/skills/` `scripts/check-*` `scripts/lint-*` `.github/workflows/` の 4 件のみ | `dh-manifest.yml` |

**A-1〜A-3 の含意**: 空のログに対して検査が PASS を返している。「検査が通った」と読める点で
無検査より悪い（v6.13.0 I-4）。**日誌をこの素材の上に立てると、日誌もまた空のまま PASS する。**
§F3-3 はこの一点への対処である。

**A-5 の含意**: 二系統の分離は宣言ではなく**既にある機械的境界**の上に置ける（§F1-2）。

---

## 不変条件（全機能共通）

- **J-1 日誌は判定を持たない。** 観察と記録に閉じる。提案・評価・スコア・優先順位を書かない。
  `GRAPH.yml` I-1（宣言であって判定ではない）と同型の自己制約。判定を持ち始めた日誌は
  `crosscut-cycle-retrospective` と重複し、f5fc45「減らす・時限化」に反して規範量を増やす
- **J-2 日誌は誰も止めない。** 非ゲート層である。exit code は常に 0、CI を赤くしない、
  PR / Issue にコメントしない、購読セッションの wake event を作らない
  （`delivery/UPSTREAM-DECISION-2026-08-26.md` 順位 3。kakuman 罠 X-CI-A: 観測層が赤を出して
  Actions 無効化に至った実例）
- **J-3 分離は「書いてから消す」ではなく「入力を分ける」。** メタ日誌の素材源は allowlist で
  宣言し、列挙外の入力を構造的に受け取らない。事後の墨塗りを一次防壁にしない
  （消し漏れは検出できない — `delivery/ANALYSIS-norm-machine-readability-2026-08-26.md` §2 の
  ①参照可能 / ②判定可能 / ③執行可能 の三段で言えば、本件は **③まで上げる**）
- **J-4 素材の生死を宣言する。** 読んだ素材が空でも「書けた」ことにしない。日誌の各エントリに
  素材源ごとの件数を明記する（v6.13.0 I-4 silent skip 禁止の自己適用。A-3 の再演を防ぐ）
- **J-5 新しい常駐機構を作らない。** 既存の実行点（日次 1 回の workflow、任意で SessionEnd hook）に
  寄生する。監視デーモン・常駐 watcher を新設しない
- **J-6 宣言と計数器は同一 PR で着地させる。** 日誌自身に付ける `review_trigger:` を数える経路を
  同じ PR に含める（v6.13.0 I-5 の継承）。v6.13.0 F5 の走査器**には依存しない**
  ── 依存させると本件が v6.13.0 の実装待ちで宙吊りになり、「宣言だけ着地」の再演になる
- **J-7 `philosophy.md` / `auto-merge-boundary.md` に触れない**（L-FROZEN-PHIL / L-FROZEN-META）

---

## F1. 二系統の構造的分離（priority: critical）

要求「メタハーネス開発とプロジェクト開発で明確に分ける」を、運用規律ではなく**配置**で担保する。

| 条件 | 内容 |
|---|---|
| F1-1 | **メタ日誌**の書き込み先は DH リポジトリ内 `history/dev-diary/` に限る。DH は公開リポジトリであり、ここに書かれたものは公開されるという前提で設計する |
| F1-2 | **プロジェクト日誌**の書き込み先は各配布先プロジェクトの `history/dev-diary/` に限る。`dh-manifest.yml` `never_touch: history/` により **DH 更新はこれを書き換えない**（A-5） |
| F1-3 | 逆流もしない。`dh-manifest.yml` の `upstream.scan` に日誌パスを**追加しない**。これは不作為ではなく**明示的な宣言**として仕様に書く（将来 scan を広げる者への停止札） |
| F1-4 | 両系統を 1 プロセスで同時に扱わない。実行単位は**リポジトリ単位**。1 回の実行が参照するリポジトリは 1 つ |
| F1-5 | メタ日誌の素材源 allowlist（§F3-2）に、配布先プロジェクトの作業ツリー・環境変数・ローカル絶対パスを**含めない** |

**なぜ配置で分けるか**: 「特定情報を書かないよう気をつける」は AI の記憶に依存した規律であり、
本サイクルが繰り返し観測してきた「記憶に依存した規律は落ちる」形そのもの。F1-1〜F1-4 の下では
プロジェクト側の情報がメタ日誌に混入する経路が**そもそも存在しない**。F2 はその上に置く二次防壁であり、
一次防壁ではない。

---

## F2. 公開安全の執行（priority: critical）

F1 が塞げない残余（メタ開発の過程そのものに含まれる個人情報・秘密）に、**止まる**経路を与える。

| 条件 | 内容 |
|---|---|
| F2-1 | 生成後・コミット前に決定論スキャンを通す（`scripts/check-diary-safety.py`）。検出対象: メールアドレス書式 / ローカル絶対パス（`/home/*` `/Users/*`）/ 秘密鍵・トークンらしき文字列 / allowlist 外のリポジトリ名・ホスト名 |
| F2-2 | **fail closed**。1 件でも検出したらコミットしない。下書きを `harness-verifier/reports/` に残して人間へ回す |
| F2-3 | **自動墨塗りをしない**。「消して通す」経路を作らない。消し漏れが検出不能である以上、自動修正は安全性を上げずに検査の信頼だけを上げる |
| F2-4 | スキャンは **LLM 判定を含まない**。純パターン照合に閉じる（LLM に安全判定させると検査側が生成側と同じ死角を共有する — 儀式 F1 軸監査が LLM 判定を排した理由と同一） |
| F2-5 | 本スキャンの適用対象は**日誌のみ**。他の生成物へ広げない。常時発火する検査は形骸化する（kakuman が実地で得た知見 — `delivery/UPSTREAM-DECISION-2026-08-26.md` 順位 1 の注記） |
| F2-6 | F2 は **F3 の前提条件**。安全器が着地する前に素材を読ませて書かせてはならない |

---

## F3. 素材と発火（priority: high）

要求「随所で非同期的にログや成果物を参照して」「日次で記録をまとめる」への配線。

### 解釈（人間確認を経ていない前提。§8 で明示）

「随所で非同期的に」を**実行の常駐**ではなく**参照先の分散**と読む。すなわち、複数の情報源に
非同期に堆積したログ・成果物を横断して読むが、**実行は日次 1 回に集約する**（J-5）。
常駐 watcher を新設する読みも可能だが、それは新機構であり f5fc45 と衝突する。

| 条件 | 内容 |
|---|---|
| F3-1 | 日次ロールアップは GitHub Actions の `schedule:` 1 本。ただし**配置と武装の分離**（`delivery/UPSTREAM-DECISION-2026-08-26.md` 順位 4）に従い、**初回着地では `schedule:` をコメントアウトし `workflow_dispatch` のみ**とする。手動実行を数日回して J-2 が守れることを確認してから武装する |
| F3-2 | メタ側の素材源 allowlist（**すべて読み取り専用**）: `git log` / merged PR・Issue（公開分）/ `delivery/` / `dh-upgrades/` / `history/COUNCIL-LOG.md` / `harness-verifier/reports/` |
| F3-3 | **`hook-observations.jsonl` は死んでいる前提で設計する**（A-1〜A-3）。素材が空でも日誌は成立し、出力に「hook 観測: 0 件」と明記する（J-4）。**この配線の是正を本リリースの前提条件にしない** |
| F3-4 | 随時追記（SessionEnd hook への寄生）は**任意・既定 off**。F3-3 の配線が実際に生きたことを確認するまで有効化しない |
| F3-5 | 1 日分の日誌は 1 ファイル `history/dev-diary/YYYY-MM-DD.md`。追記ではなく日ごとの新規作成（append-only な素材と、日単位で確定する記録を混ぜない） |

---

## F4. 観察者の視点（priority: medium）

| 条件 | 内容 |
|---|---|
| F4-1 | 視点は**固定の観察者ペルソナ**。Council ペルソナ（`.claude/skills/crosscut-council/references/personas/`）を流用しない ── Council ペルソナは**判定軸**であり、J-1 と正面から衝突する |
| F4-2 | モデルは `claude-haiku-4-5`。表記は `.claude/agents/*.md` の既存 frontmatter に合わせる（`review-fetch` 等と同形式）。実体は `.claude/agents/dev-diarist.md` として既存 leaf worker 群と同じ場所・同じ形で置く |
| F4-3 | 記述規律: 開発者を**三人称で観察**する。断定を避け、**観測できた事実と観測できなかった事実を並べて書く**。「良かった / 悪かった」を書かない（J-1） |
| F4-4 | 日誌は**素材に無いことを書かない**。補完・推測・外部知識での上書きをしない（`digest-worker` の規律と同一） |

**なぜ Haiku か**（要求の追認）: 本エージェントの仕事は素材 → 記述の 1 ホップ変換であり、
判定を含まない（J-1）。DH の既存 leaf worker（`digest-worker` / `explore-worker` / `review-fetch`）が
すべて Haiku 固定であるのと同じ理由による。日次実行で毎日走る以上、単価も設計条件に入る。

---

## F5. 日誌自身の時限（priority: medium）

「足す機構」に「減らす機構」を同梱する（Council `f5fc45`）。日誌は規範ではないが、
**誰にも読まれない生成物は規範と同じく purity を下げる**。

| 条件 | 内容 |
|---|---|
| F5-1 | 日誌機構自身に `review_trigger:` を付ける。`cycles: 6` および `measured: 直近 6 cycle で日誌への被参照が 0 件なら廃止を検討` |
| F5-2 | その計数器 `scripts/count-diary-references.py` を**同一 PR に含める**（J-6）。`history/dev-diary/` 配下のファイル名が他文書から参照された件数を機械集計する。LLM 判定を含まない |
| F5-3 | `review_trigger: model_generation`（§1 F2.6 発火分）。`claude-haiku-4-5` は後継不在・retirement 下限 2026-10-15 |

---

## 実装順序（固定）

**F1 → F2 → F3 → F4 → F5**。

- F1（配置）が先。分離されていない場所へ書き始めてから分けるのは、書いたものを消す作業になる
- F2 は F3 の前提（F2-6）。安全器なしに素材を読ませない
- F4 は F3 の後。素材が確定していない状態でペルソナを書くと、素材に無いことを書く設計になる
- F5 は最後だが**同一 PR**（J-6）。別 PR に送った時点で「宣言だけ着地」になる

---

## 受け入れ基準

| # | 基準 | 測り方 |
|---|---|---|
| C-1 | メタ日誌が 7 日分生成され、F2 スキャンが**全件 0 検出**で通過する | `scripts/check-diary-safety.py` の exit code と検出件数 |
| C-2 | 全エントリに**素材源ごとの件数**が明記されている（J-4） | 生成物の grep。`hook 観測: 0 件` が明記されていること |
| C-3 | 観測期間中に CI が 1 度も赤にならず、PR / Issue コメントが **0 件**（J-2） | Actions の run 結果と PR タイムライン |
| C-4 | `review_trigger:` の計数器が**同一 PR に存在する**（J-6） | `scripts/count-diary-references.py` の有無と実行結果 |
| C-5 | プロジェクト日誌のパスが `dh-manifest.yml` の `upstream.scan` に**含まれていない**（F1-3） | `dh-manifest.yml` の diff |

C-1〜C-5 はいずれも**機械で測れる**。測れない基準は置かない（v6.13.0 I-5 の趣旨）。

---

## 7. 人間専管の切り分け

| 対象 | 委譲レベル | AI の可否 |
|---|---|---|
| `.claude/skills/layer0-spec-architect/references/philosophy.md` | **L-FROZEN-PHIL** | 提案 PR も不可（2026-11-06 まで） |
| `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md` | **L-FROZEN-META** | 提案 PR も不可 |
| `dh-manifest.yml` の `upstream.scan` 変更 | L0/D5 専管 | 提案のみ（本件は**変更しない**ことの宣言に留まる） |
| `.claude/agents/dev-diarist.md` 新設（F4） | L-FULL | **可**（人間レビュー必須） |
| `scripts/check-diary-safety.py` / `count-diary-references.py`（F2 / F5） | L-FULL | **可**（人間レビュー必須） |
| 日誌 workflow の `schedule:` **武装**（F3-1） | **人間判断** | 配置は可・武装は不可（配置と武装の分離） |
| `decision_category` 空欄 5 件の付与 / `council-weights.md` の数値是正 | 人間専管・L0/D5 専管 | 繰越（本件と独立） |

---

## 8. リスク・申し送り

- **A-4 のリスク（最大）**: `VERSION` は 6.11.0 で、v6.12.0 / v6.13.0 は**未実装**。本仕様を積むと
  仕様 3 本が実装を待つ状態になる。加えて v6.11.0 の受け入れ基準 C-1（正規化ギャップ 0 件）は
  **未達 11 件**であり、しかも**それを数える計数器は存在しない**（`scripts/` に該当なし）。
  ── 本仕様は v6.13.0 の F1〜F5 に技術的依存を持たない（J-6 で自前計数器を持つ設計にしたため）ので
  並行実装は可能だが、**律速は人間レビュー枠**である。実装順の決定は人間に委ねる
- **解釈リスク**: §F3 の「随所で非同期的に」の読み（参照先の分散 ⊃ 実行の常駐ではない）は
  **人間確認を経ていない AI 解釈**である。常駐 watcher を意図していた場合、F3-1 は要再設計
- **未処理項目 1（本サイクル発見）**: `.claude/hooks.json` は `$schema` に
  `claude-code-settings.json` を宣言しているが、`.claude/settings.json` は存在しない。
  実観測 0 件（A-2）という実測はこの配線が機能していないことを示す。**本サイクルでは是正しない**
  （スコープ外。widening は本サイクルが繰り返し戒めてきた形）が、記録する。
  `README.en.md:139` の `cp dialog-harness/.claude/hooks.json .claude/` も同じ配置を配布先へ再生産している
- **未処理項目 2（前サイクルから継続）**: `.github/workflows/harness-verify.yml` の paths フィルタに
  `dh-upgrades/` と `history/` が含まれず、**仕様起草 PR には検証が 1 つも走らない**
  （#196 で `scripts/**` は追加されたが、この 2 つは未追加のまま）。本 PR もこれに該当する
- **未処理項目 3（継続）**: `decision_category` 空欄 5 件 / `situational_modifier` 合計 +1
