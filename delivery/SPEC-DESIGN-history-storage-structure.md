# SPEC 設計案 — 履歴ストレージ構造（tier 分割 / 案D）

> 状態: **設計確定（v5.25.0 merged #137 / v5.25.1 で Council seeds 10 件吸収）**。runtime 実装・既存履歴 migration は別タスク。
> v2 残点 §8 は全て確定: §7-A=§7 温存・E2E を §7.4 移設 / 索引=単一始まり / 呼称=COLD-event・COLD-artifact / selector_note 必須。
> v5.25.1 で Council PR レビュー（`approve_with_seeds`）の 10 seeds を反映: crystallized_into/bias_flag 型正準化 / 索引分割の race・閾値定量 / event_id 桁 / archive 例示年次 / writer contract fail-fast 場合分け / runtime schema 検査 TODO / 三段降格 件数閾値 / harvest 異視座 / reversible 昇格経路 / COLD 第三形態の余地。
> 起点: Council `council-2026-06-11T05:30:00Z-hstr01`（全会一致・人間合意 `agreed_recommended`）。
> 還元先: DH 本体（D4・`reduction_target: DH`）。昇格区分: **minor**（後方互換の追加・既存 E2E 同型解の一般化・既存リンク削除なし）。
>
> **人間レビュー §5 で確定した方針（v2 反映済み）**:
> - Q1: regime 改訂 = **§7 自体を一般形にリネーム**（長期的に効果的な方）。ただしアンカー `§7` と既存参照は温存し compat-safe に実施（§7 詳細）
> - Q2: `selector_note` = **必須**（哲学者要件に忠実）。enforcement は §7-B
> - Q3: 実ファイルには触れず**設計をさらに詰める**（本 v2）。migration は別タスクで確定（§5）

---

## 0. 確定方針（再掲）

履歴の保持構造は **tier で割り当てる（案D）**。全層を一律「1ファイル蓄積」にも「1事象1ファイル」にもしない。

| tier | 物理形態 | 根拠 |
|---|---|---|
| **WARM**（生きた台帳・append 中） | **1ジャンル蓄積**（append-only 単一ファイル） | reindex cursor 増分摂取・監査連続性・書き込み安価 |
| **COLD**（reindex 排泄物・既定非ロード） | **1事象1ファイル + frontmatter** | filesystem/glob が索引・逆引きポインタが1ファイル名指し・entry 単位 retrieve |
| **索引** | frontmatter 収穫の薄いメタ map | 蓄積に緩やかに連動するがメタのみ＝本文購読量に乗らない |

北極星（既定購読量の最小化・蓄積との線形連動を断つ・disk 無制限OK）に全項を従属させる。

---

## 1. COLD frontmatter スキーマ

COLD event file の配置: `history/archive/YYYY-MM/<genre>/<event-id>.md`

`<genre>` ∈ { `council`, `changelog`, `regime`, `arch-decision`, `patterns`, `intent`, `e2e` }（WARM 台帳と 1:1）

各ファイル先頭の YAML frontmatter:

```yaml
---
genre: council                       # WARM 台帳のジャンル（必須）
event_id: hstr01                     # ジャンル内一意 ID。WARM の invocation_id 等と対応（必須）
title: "履歴ストレージ構造の設計判断"   # 索引表示用の一行（必須）
timestamp: 2026-06-11T05:30:00Z      # 元 event の発生時刻（必須）
archived_at: 2026-07-01              # COLD 移送日（必須）
reduction_target: DH                 # 軸A 還元先（DH / project）（必須）

# --- 逆引き（不変条件 #3 の entry レベル具体化）---
source_pointer: "history/COUNCIL-LOG.md @ council-2026-06-11T05:30:00Z-hstr01"   # WARM 原本への逆引き（必須）。locator は grep 可能な安定キー（invocation_id / 日付+連番 / AD-NNN）。GitHub 見出しアンカーではない（append-only 台帳では行番号より ID が訂正に強い）
crystallized_into: ["history/SUMMARY.md @ <locator>"]  # HOT 叡智の list（inline literal）。無ければ空 list [] が正準（null 禁止＝型ブレ防止）。<locator> は grep 可能な安定キー（見出しアンカーではない）

# --- 確度（既存 history-layer-spec §確度メタデータ と同形）---
confidence: 確定                     # 確定 / AI推定 (YYYY-MM-DD)

# --- 哲学者 3 要件のメタ列（後述 §3）---
harvest_status: harvested            # harvested / unharvested（要件1: 収穫漏れ救済の監査対象）
selector_note:                       # 要件2: 選別バイアス監査（誰が何を根拠に分類/収穫したか）
  by: layer0-reindex-librarian
  basis: "repetition_threshold 到達 + Council mtb..."
  bias_flag: null                    # 偏りの疑いがあれば記す（null 可）
reversible: true                     # 要件3: 後世が問い直せる（COLD→明示 retrieve 後の再評価を閉じない）
---

（本文 = 元の生ログ entry をそのまま。lossless 原本。不変条件 #6 の結晶化素材）
```

設計判断:
- frontmatter は **メタのみ**。本文（生ログ）は別。索引収穫は frontmatter だけを読むので本文購読量に乗らない。
- `event_id` は WARM 台帳の既存 ID（COUNCIL-LOG の `invocation_id` 末尾、CHANGELOG の日付+連番 等）を流用。新採番機構は作らない。
- 必須キーが欠けた COLD file は索引収穫時に `selector_note.bias_flag: "schema-incomplete"` を立てて拾う（沈黙させない）。

---

## 2. 索引収穫プロトコル（index harvest）

### 索引ファイル
`history/archive/COLD-INDEX.md`（単一・薄いメタ map）。肥大時は genre 別 `COLD-INDEX-<genre>.md` に分割。
**索引の索引は作らない**（代謝天井の再発回避）。索引自体が budget を脅かしたら古い行を `COLD-INDEX-archive-YYYY.md` に降格。

### 収穫（reindex が COLD 移送時に実行）
1. WARM → COLD 移送する各 event について、event file を書き出す（frontmatter + 本文）。
2. **frontmatter だけを読んで**（本文は読まない＝購読量保護・冪等の増分処理）索引へ 1 行追記。
3. 索引行スキーマ（パイプ区切り・1 event = 1 行）:
   ```
   | genre | event_id | timestamp | title | harvest_status | source_pointer | path |
   ```
4. 追記は append-only。cursor（`.metabolism-cursor.yml`）で続きから増分のみ処理（全 rescan 禁止）。

### retrieve（AI が履歴参照時）
1. 既定では `history/SUMMARY.md`（HOT 入口）のみロード。COLD-INDEX は**既定ロードしない**。
2. 「必要な物を補足」したい時だけ COLD-INDEX（メタのみ・低購読量）を読み、対象 `event_id` を特定。
3. その **単一 event file だけ** を Read（glob/path で名指し）。→ entry 単位 retrieve が成立。

これがユーザー要求「履歴参照時に必要な物を補足できるようにしたい」の実装経路。

---

## 3. 哲学者 3 要件の組み込み（minority_opinion・重み5）

3 要件はいずれも既存 regime に**器がある**。新規実体は `selector_note` メタ列のみ。

| 要件 | 既存の器 | 本案での具体化 |
|---|---|---|
| (1) 収穫漏れの「二度目の沈黙」防止 | §2 #2「COLD=archive≠delete」/ §3-5「沈黙した声の救済」 | `harvest_status: unharvested` を持つ COLD file は **delete せず glob 全走査で必ず再到達可能**。reindex は `unharvested` を定期的に SUMMARY「要再確認リスト」へ再掲（沈黙の固定化を防ぐ再訪予約） |
| (2) 選別装置の設計者バイアス監査 | §3「摂取選択基準」/ §3-3「摂取選択の可監査性」 | frontmatter `selector_note`（by / basis / bias_flag）を**必須化**。誰が何を根拠に分類・収穫したかを entry レベルで監査可能に |
| (3) 後世の問い直し可逆性 | 既存「禁止: COLD→HOT **常時**昇格」（"常時"であって明示 retrieve 後の再評価は許容） | `reversible: true` を保証。COLD 構造は後世が分類を問い直し、明示 retrieve 後に WARM/HOT へ再昇格する経路を閉じない |

→ 哲学者の警告「索引が収穫しなかった entry は本当に救済されているのか」への構造的回答 =
**索引（収穫されたもの）とは独立に、filesystem（全 COLD file）が常に一次の真実源**。索引はあくまで高速入口であって、唯一の到達経路ではない。

---

## 4. 改訂対象ファイルと差分方針

### (a) `.claude/skills/layer0-reindex-librarian/references/metabolism-regime.md`
> **【v2 更新】本項の旧方針（§6.5 新節挿入）は §7-A に置換された。** Q1 決定により **§7 自体を一般形にリネーム**（アンカー §番号 7 温存・現 E2E 本文を §7.4 配下へ移設）する。構造は §7-A の改訂スケルトン参照。

- **§7 見出しを一般化**し、§7.0 一般原則 / §7.1 COLD-event / §7.2 COLD-artifact / §7.3 還元先 / §7.4 E2E 適用例（現 §7 本文を内容不変で移設）に再編。
- 本設計案 §1（frontmatter スキーマ）・§2（索引収穫）は §7.1 配下に framework 定義として記載。
- 不変条件 §5 に **#9 収穫漏れ救済・#10 選別バイアス監査・#11 問い直し可逆性** を追加（本案 §3 / §7-B / §7-D）。

### (b) `.claude/skills/layer0-spec-architect/references/history-layer-spec.md`
project 向けの履歴層スキーマ。COLD 物理形態を反映。

- **§配置**: `archive/` ツリーに `<genre>/<event-id>.md` 形態と `COLD-INDEX.md` を追記。
- **§archive/「archive 配下の構造」**: 現状の `INTENT-F003.md`（機能ID単位）を `<genre>/<event-id>.md` + frontmatter に一般化（廃止 INTENT は `intent` genre の一例に）。
- **新節「COLD frontmatter スキーマ / 索引収穫」**: 正本 `metabolism-regime.md §7.1` への pointer 1 行 + project 具体（既存 §7 E2E と同じ薄いポインタ方式＝SPEC 肥大回避）。

### (c) versioning / 検証
- **minor 昇格**（後方互換追加・既存リンク削除なし・identity 保持）。spec-architect §参照ドキュメントの「リンク単位保持」制約に抵触しない。
- 改訂後に **harness-verifier の broken-reference 検査**（`harness-verifier/checks/references.py` / バッククォート path 含む）を通すこと。新規 pointer はすべて実在パスに張る。
- `history/CHANGELOG.md` に minor として記録（reduction_target: DH）。

---

## 5. やらないこと（スコープ外・別タスク）

- **runtime 実装**: reindex-librarian の収穫ロジック実装は別タスク。**TODO（runtime PR 必須）**: `selector_note` 必須化は
  writer contract に依拠するため、runtime PR は `reindex-librarian` 側に **schema 検査テスト**（必須キー欠落で fail）を必ず伴うこと（enforcement の時間差を埋める）。
- **既存履歴の migration**: 現 COLD（`archive/2026-06/*` のフラット配置）の `<genre>/` 再編 + frontmatter 後付けは別 PR。本案では「新規 COLD 移送分から段階適用・既存は遡及しない」（LC ≥ 1 の段階適用原則）。
- **WARM 台帳の分割**: WARM は単一台帳のまま（案C を全層展開しない＝索引が新たな代謝天井になる罠の回避）。

---

## 6. 認識ズレ確認ポイント（人間レビュー §5・v1）— 確定済み

1. ~~§6.5 新節挿入 vs §7 リネーム~~ → **§7 リネームに確定**（Q1・詳細 §7-A）
2. 索引の開始形（単一 vs genre 別）→ **単一 `COLD-INDEX.md` 始まりに確定**（§8-2・肥大時 genre 別分割）
3. `selector_note` 必須 → **必須に確定**（Q2・enforcement §7-B）
4. 既存 archive 遡及 migration → **しない（別 PR）に確定**（Q3・§5 / §7-F）

---

## 7. 設計詰め v2（人間レビュー後の深掘り）

### 7-A. §7 一般化の構造（compat-safe rename）＋ COLD 二形態の止揚【重要】

**発見した矛盾**: 現 §7 の COLD は E2E の **生 artifact**（Trace/動画/network/console・jsonl）であり、`archive/YYYY-MM/e2e/` に置かれ WARM(E2E-LOG) から `cold://` ポインタで参照される。これは markdown でも frontmatter でもない。一方、本案の一般形 COLD は **markdown + frontmatter の 1事象1ファイル**。§7 を素朴に「一般形」にすると両者が衝突する。

**止揚**: COLD には **2 つの物理サブ形態**があると定義し、両方を一般形が包摂する。

| COLD サブ形態 | 中身 | 物理形 | 索引 | 逆引き | 例 |
|---|---|---|---|---|---|
| **(i) COLD-event** | 離散した叙述的 episodic | markdown + frontmatter（1事象1ファイル） | `COLD-INDEX`（frontmatter 収穫） | frontmatter `source_pointer` | council / changelog / regime / arch-decision / intent(廃止) |
| **(ii) COLD-artifact** | 不透明な生 artifact（trace/動画/bin/jsonl） | 生ファイルのまま（変換しない） | WARM 台帳側のポインタ列（索引収穫しない） | WARM entry の `cold://` ポインタ | E2E 相 A artifact |

→ **E2E は (ii) の正準例**として §7 にそのまま残る（v5.24.0 実体を 1 文字も壊さない）。council/changelog 等は (i)。一般形は「episodic は還元先と形態で COLD のサブ形態を選ぶ」ことだけを規定する。これで「一般化＝E2E の上位概念化」が矛盾なく成立する。

**§7 改訂スケルトン（アンカー温存）**:
```
## 7. episodic ソースの tier 対応（一般形）   ← 見出し一般化。§番号7 は不変＝既存 "§7" 参照は生きる
  7.0 一般原則: WARM=1ジャンル単一台帳 / COLD=2サブ形態(下記) / 索引=frontmatter収穫の薄いメタmap
  7.1 COLD サブ形態 (i) COLD-event（frontmatter スキーマ=本案§1 / 索引収穫=本案§2）
  7.2 COLD サブ形態 (ii) COLD-artifact（生 artifact・ポインタ参照・索引収穫しない）
  7.3 還元先（軸A）— 既存記述を継承
  7.4 E2E 適用例（= 現 §7 本文 tier 表 + 8不変条件具体化を 7.4 配下へ移設、内容不変）  ← (ii) の正準例
```
既存の `history-layer-spec.md §E2E-LOG`・`e2e-best-practices.md §9` 等からの「§7」参照は、§7 が存続するため**有効のまま**（broken-ref を出さない）。

### 7-B. selector_note 必須化の enforcement

書き手（reindex-librarian）を一次強制点にする。静的検査は二次防御。

1. **writer contract（一次）/ 自己生成 = fail-fast**: reindex が自ら COLD-event を書き出す時、`selector_note.by` / `.basis` / `harvest_status` / `reversible` は必須。満たせないなら**書き出さず停止**（差分レポートに記録）。
2. **既存ファイル発見 = mark-and-continue**: 過去の不完全な既存 file で欠落を検出した場合のみ、削除も放置もせず `selector_note.bias_flag: "schema-incomplete"` を立て、SUMMARY「要再確認リスト」へ再掲（沈黙させない＝要件1と連動）。※ 自己生成 fail-fast と既存発見 mark-and-continue は両立する別経路。
3. **静的検査（二次・任意）**: COLD-event md の frontmatter 必須キー検査。配置先は harness-verifier ではなく **reindex の self-check**（harness-verifier は D4 framework 整合が責務で、COLD entry schema は代謝処理の責務＝層を混ぜない）。

### 7-C. event_id の名前空間と衝突規則

- **キー = (genre, event_id)**。path `archive/YYYY-MM/<genre>/<event-id>.md` が genre で分離するため、genre 跨ぎの id 文字列再利用は衝突しない。
- **採番は流用**: council=`invocation_id` 末尾 / changelog=`YYYY-MM-DD`+連番 / regime=回次 / arch-decision=`AD-NNN`。新採番機構は作らない。
- **桁・区切り**: 同一 genre・同日で複数発生する連番は **zero-padded 2 桁**・区切り `-`（例 `2026-06-11-01.md` / `-02.md`）。2 桁で足りなくなったら桁を増やす。path 衝突回避の正準規則。

### 7-D. harvest_status のライフサイクル（要件1 の精密化）

§4 排出原則「対象は結晶化完了済みの抜け殻のみ（吸収→排泄）」を踏まえ、`harvest_status` は 2 値で **沈黙した声を可視化**する：

| 値 | 意味 | COLD 入りの経路 |
|---|---|---|
| `harvested` | 栄養抽出（結晶化）完了済みの正規の抜け殻 | §4 の正規順序（吸収→排泄） |
| `unharvested` | 栄養抽出されず COLD 入り（AI が「重要でない」と判断＝§3-5 沈黙した声候補） | 例外経路。delete 禁止・glob 全走査で再到達可能・要再確認リストへ周期再掲 |

- **不変条件 #6 整合**: 結晶化は COLD lossless 原本（本文）から読む。frontmatter は索引・監査用メタであって結晶化素材ではない（lossy-on-lossy 回避）。
- `unharvested` は §3-2「判定不能は WARM 留置（捨てない）」とは別物（判定不能は WARM、明示的に非価値判定されたものだけ unharvested で COLD）。可逆性(#11)が安全網。
- **同視座反復の緩和（哲学者 seed）**: `unharvested` を打刻するのも再訪するのも同じ AI だと「同じ盲点で二度沈黙させる」リスクがある。要再確認リストの周期再掲では **異視座（人間 / 別モデル / 別 persona）を 1 件以上含める**運用を推奨し、その旨を `selector_note.basis` 任意欄に残す（「後世が安心しすぎる罠」の緩和）。

### 7-E. 索引の肥大対策（代謝天井の再発防止・精密化）

- 開始は単一 `archive/COLD-INDEX.md`。
- **分割閾値（定量）**: `token_budget × 0.5`（行数近似）または 1 索引 500 行のいずれか先着で **genre 別分割** → `COLD-INDEX-<genre>.md`。この時 `COLD-INDEX.md` は「どの genre 索引が存在するか」の**ディレクトリ（≈7 行・genre 数で上限）**に縮退する。
- **書き込み race 規約**: COLD-INDEX は reindex の cycle 境界 **single-writer**（並行 writer なし＝§4 リズム sparse）。分割は一時ファイルへ全書き後 **atomic rename**（部分書き込み混在を防止）。
- **禁止: event 単位の「索引の索引」**（再帰的肥大＝代謝天井の再発）。genre ディレクトリは genre 数で有界なので可。
- 古い索引行は `COLD-INDEX-archive-YYYY.md` へ降格（索引自身も代謝対象）。**降格トリガーは時間軸 YYYY と件数（archive 索引が上記閾値超過）の双方**（ジャンル偏在時の判断負債を回避）。
- retrieve（分割後）: SUMMARY → COLD-INDEX(genre ディレクトリ) → 該当 `COLD-INDEX-<genre>` → 単一 event file。各段が低購読量。

### 7-F. 既存 archive との共存（no-migration の精密化）

- 現 `archive/2026-06/*.md`（フラット・frontmatter 無し・genre dir 無し）は**そのまま温存**。本スキーム以前の産物。
- COLD-INDEX は**新スキームの file のみ**索引化。旧フラット file は既存 `archive/2026-06/MANIFEST.md`（逆引き）で到達——**filesystem = 一次の真実源**（要件1）は旧 file にも適用＝delete されないため救済は維持。
- 旧 file の `<genre>/` 再編 + frontmatter 後付けは**別 PR の migration タスク**（本案スコープ外）。新規 COLD 移送分から段階適用（LC ≥ 1 段階適用原則）。

---

## 8. v2 時点の残・認識ズレ確認ポイント

1. **§7 一般化の構造**（7-A）: 「§番号 7 を保持しつつ見出しを一般化＋現 E2E 本文を §7.4 配下へ移設」で良いか（既存 "§7" 参照を全て生かす狙い）。
2. **索引の開始形**: 単一 `COLD-INDEX.md` 始まり（肥大時に genre 分割）で良いか。最初から genre 別にするか。
3. **COLD 二形態の命名**: `COLD-event` / `COLD-artifact` の呼称で確定して良いか（regime 用語辞書 `glossary.yml` に追加対象）。
4. **selector_note 静的検査の配置**: reindex self-check（7-B-3）で良いか。harness-verifier 側に寄せたいか。
