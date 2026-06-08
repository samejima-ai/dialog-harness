# Reindex 運用プロトコル

Reindex モードの実行手順・冪等性契約・Dry-run・処理済みマーカー・逆引きポインタ形式の正本。
本ファイルは「**どう回すか（how）**」を扱う。「何を正典にするか（what）」は `metabolism-regime.md` を参照。
Council mtbl01 の修正 5 点（定量ゲート基準 / 処理済みマーカー / モード guard / 逆引きポインタ形式 / Dry-run デフォルト）をここに具体化する。

---

## 1. モード切替 guard（独自補完禁止と整合・mtbl01 #3）

```
判定入力: トリガー種別（人間発話 or リズム）と入力源
  case 人間との対話「新規機能 / 継続開発 / 仕様策定」:
      → Scaffold。本スキルは起動せず layer0-spec-architect へ委譲する
  case リズム（history 層 token 超過） OR 人間明示「reindex / 結晶化 / 代謝 / 抜け殻を archive」:
      → Reindex モード起動
  case 上記いずれにも明確に該当しない（曖昧）:
      → 起動しない（spec-architect の対話で吸収させる。暗黙判断で Reindex を起動してはならない）
```

guard を通過した後にのみ §3 の処理フローへ進む。曖昧なまま結晶化・移送を行うのは独自補完であり禁止。

---

## 2. 処理済みマーカー（増分・全 rescan 禁止・冪等の生命線・mtbl01 #2）

代謝処理自身が購読量を侵さないために、reindex は**前回結晶化以降の増分だけ**を読む。これを担保するのが処理済みマーカー。

### マーカー形式

利用者プロジェクトの `history/.metabolism-cursor.yml`（COLD/HOT と同じく project ローカル、パスは REGIME.md で上書き可）に置く。
dot-file にするのは「機械専用カーソルで人間は直接編集しない」ことの明示であり、可監査性（metabolism-regime §3）は人間可読の SUMMARY.md「要再確認リスト」側で担保する（hidden で内容を隠す意図ではない）:

```yaml
# 情報代謝 処理済みマーカー（reindex が前進させる。手動編集は非推奨）
last_reindex_at: "2026-05-31T00:00:00Z"   # 最終 reindex の cycle 境界時刻
cursor:
  # line = 消化済み末尾行。checksum = 「先頭〜line までの消化済みプレフィックスのみ」の sha256
  #（全ファイル指紋ではない。append-only な history では末尾追記で全ファイル指紋が毎回変わり誤検知するため、
  #  範囲は必ず消化済みプレフィックスに限定する＝M2）
  # checksum 値は **フル 64hex の sha256**（短縮しない）。比較は前方一致ではなく **全長一致** で行う
  #（人手 baseline ↔ 機械生成の比較不一致を防ぐ。下例の `…` は紙面省略であって短縮保存ではない）
  INTENT.md:    { line: 312, checksum: "sha256:ab12…" }
  CHANGELOG.md: { line: 188, checksum: "sha256:cd34…" }
  COUNCIL-LOG.md: { line: 2088, checksum: "sha256:ef56…" }
  E2E-LOG.md:   { line: 0, checksum: null }   # UI project のみ。append-only run 要約（WARM）。新規出現時は cursor 未登録として line:0 登録（§2 規律）→ 次回先頭から摂取
reduction_target: "DH"   # この cursor が DH 還元 / project 還元 どちらの消化進捗か（軸A）
dry_run_remaining: 3      # 残り Dry-run サイクル数（0 で本番昇格、REGIME.md 初期値から減算）
                          # ロード時に負値/破損を検出したら安全側へ倒し Dry-run を強制（!=0 ではなく「>0 または不正→Dry-run」＝L1）
```

### 規律

- **読む範囲は cursor の続き〜現末尾（WARM delta）のみ**。cursor より前は消化済みとして読まない。**COLD は再 scan しない**
- **checksum の対象は「先頭〜`line` の消化済みプレフィックスのみ」**（M2）。末尾への正常な append では指紋は変わらない。プレフィックス指紋が不一致なら「cursor 以前が改変された（履歴改竄/訂正）」を意味するので、その範囲だけ部分再読込し原因を差分レポートに記録する。全 rescan はしない
- **新規 history ファイルの出現時（cursor 未登録・M3）**: 全 rescan 禁止の例外ではなく「新規 WARM の初回摂取」として扱う。`{ line: 0, checksum: null }` で cursor に登録し、次回 reindex で先頭から取り込む（既存ファイルの再 scan ではないので不変条件と衝突しない）。登録時は差分レポートに「新規 history ファイル検出」を記録
- **dry_run 判定の安全側（L1）**: §3 step 6 は `dry_run_remaining > 0` で Dry-run。ロード時に負値・非数・欠落を検出したら **Dry-run を強制**（破損で本番に倒れない）。正常な減算でのみ 0 に到達し本番昇格する
- **冪等性**: 同じ history 状態に対し reindex を二度走らせても、安定した叡智を再蒸留して揺れない。マーカーが前進済みなら何もしない（no-op）。再結晶化が既存 HOT を上書き提案する場合は差分のみ提示
- マーカーの前進は処理フロー §3 の最終ステップでのみ行う（途中失敗時は前進させない＝再実行で安全に再開）

---

## 2.5. config 解決順（REGIME.md ⇄ DH-self 既定パス・単一ロジック・Council mcfg01）

代謝パラメータ（`token_budget` / `dry_run_cycles` / `council_gate` 閾値）の読込みは、利用者プロジェクトと DH 本体で
**経路を分岐させず**、次の単一解決ロジックで引く。これにより「REGIME.md 不在時の fallback 未定義」を塞ぎ、
skill 側の条件分岐負債を作らない（開発者 0.78）。

```
config を解決する（reduction 先に依らず同一ロジック）:
  1. REGIME.md `## 情報代謝設定` が存在すればそれを正本とする   ← 利用者プロジェクト（reduction=project / D1-D3）
  2. 無ければ DH-self 既定パス `history/.metabolism-config.yml`   ← DH 本体（reduction=DH / D4）
  （パスは REGIME.md / config 内 `metabolism.paths` で上書き可）
```

- **構造同形・還元先非同形**: 1 と 2 は **同一スキーマ**（同じ `## 情報代謝設定` キー構造）。違いは `reduction_target` のみ
  （DH=D4 還元 / project=D1-D3 還元）。DH は利用者と「同じ道を歩む」が、学習の還元先だけが非同形（代謝汚染の防止）。
- **root REGIME.md を DH 本体に新設しない**: DH は「root REGIME.md を持たない」慣習（`delivery/REGIME-CONFIRM-metaskill.md` §1）を
  保つため、器は REGIME.md ではなく DH-self 既定ファイルとする。利用者が DH の REGIME.md を誤って雛形視するのを防ぐ。
- **設定とカーソルの責務分離**: config（人間が決める設定値）と cursor（機械が自動前進させる処理済みマーカー §2）は
  **別ファイル**に保つ。同居させない（reindex の自動書込みが人手設定を破壊する不可逆リスクを避ける）。

---

## 3. 処理フロー（Reindex モード）

```
0. リズム判定: token 閾値（REGIME.md metabolism.token_budget）超過 or 明示。未満なら no-op で終了
1. 還元先軸の確定: DH メタ開発 / 固有プロジェクト開発 → 咀嚼吸収対象（軸A）を決定
2. 増分特定: 処理済みマーカーの cursor 続きから WARM delta を読む（§2）
3. 摂取選択: metabolism-regime §摂取選択基準で結晶化候補を選別（反復性 / 還元先明確 / 可監査）
4. 咀嚼吸収（構築代謝）: 候補を叡智へ結晶化【提案生成】
   - 成功反復 → RL/convention、失敗反復 → DONT 罠、設計根拠 → INTENT/DOMAINS
   - HOT 昇格は §4 Council ゲートを通す
5. 排泄（分解代謝）: 結晶化完了済み抜け殻を COLD へ移送【指示生成】 + 逆引きポインタ付与（§5）
6. 出力分岐:
   - Dry-run（dry_run_remaining > 0 or 初回）: 差分レポートのみ生成（delivery/REINDEX-DRYRUN-<ts>.md）。実結晶化・実移送はしない。dry_run_remaining を 1 減算
   - 本番（dry_run_remaining == 0）: 結晶化提案を HOT へ反映（Council ゲート通過分）+ 抜け殻を COLD へ移送
7. 処理済みマーカーを前進（cursor / checksum / last_reindex_at 更新）= 冪等性の確定
```

cycle 境界（献上後・次 L0 前）でのみ実行する。開発中は割り込まない（検証後評価原則）。

### E2E episodic ソースの摂取（v5.24.0）

UI project では `history/E2E-LOG.md`（run 要約・WARM）が cursor 追跡対象に加わる（上記マーカー例）。
step 3 摂取選択では **flaky の反復**（`council_gate.repetition_threshold` 回以上）を罠候補、**安定 journey** を
RL 候補として選別する。flaky 罠の結晶化は **#6 に従い生 run ログ（COLD lossless 原本）から**蒸留し、
E2E-LOG の lossy 要約からは結晶化しない。相 A artifact は最初から COLD 直行（reindex の摂取対象外＝既定非ロード）。
tier 対応の正本は `metabolism-regime.md` §7、構築側は
`../../layer1-autonomous-dev/references/e2e-best-practices.md` §9。

---

## 4. Council ゲート定量基準（早すぎる結晶化の防止・mtbl01 #1）

HOT 昇格（WARM→HOT）は自動カウンタで上げず、Council 判定をゲートにする。Council 起動の**定量トリガー**は REGIME.md の project 固有値で引く:

```yaml
# REGIME.md ## 情報代謝設定 から参照される定量基準（例示・project が値を持つ）
metabolism:
  council_gate:
    repetition_threshold: 3        # 同一パターンが N 回反復したら結晶化候補（単発は候補にしない）
    cross_type_threshold: 3        # 同一 override が M 機能タイプ以上で反復したら Council 諮問（既存ルールの一般化）
    min_age_days: 7                # 候補化から X 日経過するまで HOT 昇格しない（偶然の固定化防止）
```

reindex は候補を検出するだけ。HOT へ実際に昇格させるかは Council judgment → 合意プロセス → 人間最終承認の経路で決まる（philosophy 第6条）。

---

## 5. COLD 逆引き source pointer 形式（腐敗防止・mtbl01 #4）

結晶化した叡智（罠/RL/INTENT 等）には、元の COLD episodic への逆引きポインタを必ず付す。retrieve 時に腐敗しない安定参照にする:

```
<!-- source: cold://2026-05/DELIVERY-v5.3.0.md#L42-88 sha256:ab12… reduction=DH -->
```

E2E flaky 罠の例（生 run ログへ逆引き・reduction=project）:

```
<!-- source: cold://2026-06/e2e/run-2026-06-08T0613Z-checkout.jsonl#L12-31 sha256:9f01… reduction=project -->
```

- `cold://<相対パス>` は COLD アーカイブ内の安定パス（移送時に確定、以後不変）
- `#Lxx-yy` は該当行範囲、`sha256:` は移送時点の内容指紋（腐敗検出用）
- `reduction=` は還元先（DH / project）。retrieve 時にどちらの層の文脈かを失わない
- COLD 側ファイルは移送後 read-only（append-only アーカイブ）。指紋不一致は監査フラグ
- **付与粒度（L3）**: ポインタは**結晶エントリ単位**で付す（罠 1 件 / RL 1 条 / INTENT 1 機能ごとに 1 本）。ファイル末尾一括ではなく当該エントリ直近に置く
- **Markdown table への付与（L3）**: 表セル内の HTML コメントは一部レンダラで除去され得るため、表形式の罠には**表の直前/直後の行**にポインタを置くか、脚注参照（`[^src-001]`）方式で表外に逃がす。セル内 `<!-- -->` 直書きは避ける

COLD アーカイブ構造は既存 `history/archive/YYYY-MM/` を踏襲する（`history-layer-spec.md` §archive＝COLD の素地）。

---

## 6. 初回 reindex 手順（DH 本体・dog-fooding）

DH 本体 repo 自身も代謝対象を持つ（`history/` の DH 還元型）。初回は**必ず Dry-run**:

1. 還元先軸 = DH（このリポジトリでのメタ開発）に固定
2. 既存 history のうち罠/Council/INTENT は既に結晶化済みである前提を置く（再結晶化で揺らさない＝冪等）
3. 抜け殻候補（古い SELF-VERIFICATION / HANDOFF / VERIFICATION 等の一回性詳細）を検出
4. Dry-run 差分レポート（`delivery/REINDEX-DRYRUN-<ts>.md`）を生成 = COLD 移送候補と結晶化候補を**提示のみ**
5. 人間が差分レポートを承認したら、次サイクル以降で dry_run_remaining を減らし本番移送へ

初回から本結晶化・本移送はしない（誤結晶化→COLD 誤移送の P4 復元工数を未然に抑える）。
