# ABLATION — Council 3 ペルソナ vs 単一・新規文脈レビュアー（2026-09-13）

> upgrade-spec v7.0.0 Phase A **F8**。Phase B（H1・2026-11-06 ゲート後・人間起票）で第 7 条 4 役割を
> どう扱うかの**判断材料**。**結論は書かない**（判断は人間、spec F8 受け入れ基準）。
> Council 自身が当事者のため Council 諮問を経ず人間直行（v6.10.0「Council 自体が当事者なら直接人間へ」）。
>
> 規範メタデータ: `{ stage: 全段階, review_trigger: [model_generation, date: 2026-11-06] }`

## 0. 設計

| 条件 | 内容 | 標本 |
|---|---|---|
| (a-hist) | 過去の 3 ペルソナ Council 判定（記録済み）。人間の事後評価 `actual_outcome.status` と突合 | 82 件（`~/.claude/council-data/invocations/`、評価済み全件） |
| (b-full) | 単一レビュアー・新規文脈・topic_summary のみ・**現行 repo を読める** | 10 件（category 層化抽出） |
| (b-snap) | 単一レビュアー・新規文脈・topic_summary のみ・**決定時点の git snapshot（worktree）のみ読める**。外部・council-data・COUNCIL-LOG 禁止 | 同 10 件 |

- 10 件の抽出: category 比例（conception 4 / judgment 3 / implementation 1 / operation 1 / 補充 1）、seed 固定。
- (b) の一致判定: 記録された `judgment`（人間が 97.6% で同意した案）と骨格が同じか。判定者は本セッション（LLM 判定・I-3 の検知ではなく分析）。
- 一致は 3 値（match / mismatch）で記録し partial は mismatch に倒した（甘くしない）。
- (b) のモデルは Council workflow のペルソナと同一（親モデル継承・model 指定なし）。
- **ラベル汚染**: (a-hist) の `judgment` は Council 自身の出力なので、(a) の一致率は「人間が Council 案に同意した率」であり Council の正しさではない。(b-full) は決定後の repo を読めるため「答えを読んだ」可能性がある — これが (b-snap) を追加した理由。

## 1. 結果

| 指標 | (a-hist) 3 ペルソナ | (b-full) 単一・現行 repo | (b-snap) 単一・決定時点 snapshot |
|---|---|---|---|
| 人間判定 / 記録 judgment との一致 | **80/82 = 0.976**（agreed 65・synthesis 15・modified 2・**rejected 0**） | 8/10 = 0.80 | **8/10 = 0.80** |
| confidence 平均 / σ | 0.748 / **0.111**（n=76、jc） | 0.772 / 0.065 | 0.714 / **0.058** |
| ペルソナ内 σ（axis-audit・歴史） | 経営者 0.047 / 開発者 0.047 / 哲学者 0.079 | — | — |
| トークン / 件 | **約 379k**（v7phsa 実測・5 agent・1 諮問） | 約 62k | 約 86k |
| 起動 agent 数 / 件 | 5（3 ペルソナ + weights + judgment） | 1 | 1 |

### (b-snap) 10 件の内訳

| id | category | 記録 judgment（骨格） | (b-snap) 推奨（骨格） | 一致 | conf |
|---|---|---|---|---|---|
| l0agg2 | conception | Council ログのみ | Council ログのみ・consumer 出現時に再諮問 | ○ | 0.72 |
| amrev1 | conception | C ハイブリッド（定型のみ opt-out） | **反転せず opt-in 維持**（stop ラベル未実装を snapshot で実測） | ✕ | 0.78 |
| vbxdnd | conception | A `.claude/refs/industry/ecc/` | A + INSIGHTS へ精神を蒸留 | ○ | 0.70 |
| pc1f01 | conception | 暫定スキーマで pilot | 今は確定せず暫定 v0 付記 | ○ | 0.72 |
| mcfg01 | judgment | 解決順（REGIME.md → .metabolism-config.yml） | **root REGIME.md 新設を唯一の正本**（前例と衝突） | ✕ | 0.62 |
| mtb2sc | judgment | (b)6 + 結晶化確認済み (c)、project-derived 除外 | 同（結晶化証跡ベース・除外 3 dir） | ○ | 0.72 |
| adpp01 | judgment | β 中核 + α/ε 条件 | 条件付き採用（D1-D3 限定・CTL 連動・5 条件） | ○ | 0.72 |
| b7e2f1 | implementation | 案A pdfplumber + 抽象レイヤ | 案A pdfplumber（license 軸） | ○ | 0.62 |
| rtkSHA | operation | 案A SHA populate | 案A | ○ | 0.82 |
| d4mtr2 | conception | harness-verifier + singularity 併記 | harness-verifier（対象-役割型） | ○ | 0.72 |

### (b-full) との差

- b7e2f1: full は **pymupdf（性能軸）** → snapshot は **pdfplumber（license 軸）**。読める情報で観測次元が変わり、答えが反転した。
- amrev1: full は条件付き反転（Council と骨格一致）→ snapshot は反転否定。決定時点には stop ラベル実装が無く、snapshot レビュアーはそれを根拠にした。人間は Council 案に synthesis で同意している。
- 他 8 件は同じ向き。d4mtr2 / mcfg01 / rtkSHA は full 条件で決定後の repo 状態を読んでいた（リーク）。

## 2. 読み方（判断はしない）

- **一致率だけなら (a) 0.976 ≫ (b) 0.80**。ただし (a) の一致率は「rejected 0 件」＝負例を生む制御点が無い系での値であり、`scripts/harness-benchmark.py` が W9 指標に付けた注意（人間ゲートの無い系の merge 率は品質を意味しない）と同型。
- **(b-snap) の不一致 2 件はいずれも「Council が第 3 の道（止揚）を出した案件」**（amrev1 = ハイブリッド、mcfg01 = 解決順の両立）。単一レビュアーは選択肢の中から選び、Council は選択肢の外を作った。これは §重みの意味論の実測（jc < 0.5 の 4 件は全件が第 3 の道を含む）と整合する。
- **confidence の固定は Council 固有ではない**。axis-audit の warn（ペルソナ σ ≈ 0.05）と同程度の σ（0.058）が単一レビュアーでも出た。「議題に反応していない」はペルソナ構造の欠陥というより、この世代のモデルが confidence を帯で返す性質の可能性がある。warn の原因帰属は再検討が要る。
- **コストは 4.4〜6.1 倍**（379k vs 62k〜86k）。
- **外部実測（ICML 2026・最大 41.1% 損失）との対応**: 本 ablation は「チームが答えを出す」設定ではなく「人間の判断材料を出す」設定で、比較できるのは骨格一致率のみ。合議が最良メンバーに負ける現象は、本標本では観測されなかった（単一が Council に勝った案件は無い。逆に第 3 の道 2 件は単一が出せていない）。

## 3. 限界

- n=10。category 層化はしたが統計的検出力は無い。
- (a) は歴史データ（当時のモデル世代）、(b) は現行世代。世代差が混入する。
- 一致判定は本セッションの LLM 判断（1 名）。独立判定者を置いていない。
- (b-snap) でも topic_summary は Council 用に抽象化された文（options を含まない）で、Council が受け取った context より情報が少ない。単一レビュアーに不利。
- 人間の事後評価は `agreed` が 65/82 で、「沈黙は同意」に近い評価が含まれうる。

## 4. Phase B への申し送り（材料のみ）

- 単一・新規文脈レビューは骨格一致 0.80・コスト 1/4〜1/6 で、**第 3 の道を要しない案件**では代替になりうる。
- 第 3 の道が要る案件（前提対立・止揚）を事前に見分ける機構が無いと、縮退は「止揚を失う」形で効く。
- 人間の事後評価に **rejected を出せる制御点**（明示的な棄却の選択肢）を置かないと、(a) の一致率は今後も 0.97 に張り付き、判断材料にならない。
- axis-audit の「confidence 固定」warn は原因帰属（ペルソナ vs モデル）を分ける観測を先に置く。

## 5. 再現（原データ・本ファイル内に保存）

独立検証の指摘（再現物が /tmp のみ）を受け、原データを本ファイルに転記する。council-data 自体は user-scope（`~/.claude/council-data/`）で repo 外。

### 5.1 抽出 10 件と決定時点 commit

```json
[
 {
  "id": "council-2026-04-30T11:01:00Z-l0agg2",
  "category": "conception",
  "topic": "cross-project ログ集約の対象スコープ（Council のみ / +DH evolution / +verification / すべて）",
  "judgment": "案B-1: Council 判定のみ。CTL 学習・権限委譲・振り返り調整 (F1) のいずれも council ログから派生可能",
  "jc": 0.82,
  "status": "agreed",
  "note": "",
  "before_ts": "2026-04-30T11:01:00Z",
  "sha": "6fb2e955d0bf2477b9d41a60181b4ab33a7249dd",
  "worktree": "/tmp/wt-l0agg2"
 },
 {
  "id": "council-2026-05-06T08:30:00Z-amrev1",
  "category": "conception",
  "topic": "auto-merge の人間承認モデルを opt-in（明示 GO ラベル）から opt-out（暗黙オート + stop ラベル）に反転すべきか",
  "judgment": "C: ハイブリッド採用。philosophy/harness-verifier/cross-cutting/不可逆領域は opt-in 維持、定型領域のみ opt-out。境界を SPEC で不変化し、roll-back プロトコル + メタ承認機構を実装に同梱する",
  "jc": 0.8,
  "status": "agreed_with_synthesis",
  "note": "C ハイブリッド採用 + minority_opinion 由来の 4 実装要件を v5.9.0 SPEC に同梱: (1) 境界の SPEC 不変化（opt-out 領域 / opt-in 領域の分類を philosophy.md または専用 SPEC に明記、AI が境界を動かせない構造）、(2) roll-back プロトコル（6 ヶ月後検証で事故 1 件以上 → opt-in に戻す手順を",
  "before_ts": "2026-05-06T08:30:00Z",
  "sha": "180b00c5bf4b0e3a01e2220abed0d40c2207f1fe",
  "worktree": "/tmp/wt-amrev1"
 },
 {
  "id": "council-2026-05-11T03:14:18Z-vbxdnd",
  "category": "conception",
  "topic": "ECC 参照カタログ 5 ファイルを A〜E のどのディレクトリに配置すべきか",
  "judgment": "A `.claude/refs/industry/ecc/` を採用。経営者・開発者が独立に同一 stance に収束、weighted_score 4.65。哲学者の第3の道（C 精神化）は weight 5/11=45.5% を占める少数意見として保持し、人間承認時に『業界実装は参照標本であり吸収対象ではない』旨の README 明文化を A の付帯条件として検討すべき",
  "jc": 0.45,
  "status": "agreed_with_synthesis",
  "note": "保留は勧めどおり。ただし配置先は勧めの industry/ecc/ ではなく history/refs-draft/ecc/（発酵層）となったため modified。",
  "before_ts": "2026-05-11T03:14:18Z",
  "sha": "0e6dfe2630dc5a9beecf0e7e93b85b65d7ccaff9",
  "worktree": "/tmp/wt-vbxdnd"
 },
 {
  "id": "council-2026-05-31T02:00:00Z-pc1f01",
  "category": "conception",
  "topic": "パターン結晶の形式 {発火条件,反-発火条件,力学,定石,信頼度} を今確定すべきか",
  "judgment": "暫定スキーマでpilotしてから本確定（2候補で試す）。全会一致だが3者が付帯条件を課す（全員一致を多様性=質として評価）: (a)経営者=pilot期限(例6週)と終了条件を明示しないと『寝かせ』に退行する、(b)開発者=フル確定前に3機構の方針を先に決める[発火条件のembedding表現/信頼度算出方式(ルールvs統計)/反-発火条件の検証可能性]。未設計のまま固めると索引実装時に破壊的変更必須、(c)哲学者=Dry-run2候補(squash後rebase/verifier所有物D5ゲート)はif-then=規則結晶寄りで真のfuzzy類推サンプルではない。真のパターン結晶サンプルを投入しないと形式がSystem1転写を阻害するテンプレに堕す。pilotの目的は『形式の検証』でなく『形式が暗黙知の言語化を促進するか圧殺するかの観察』に置く。仮結晶+二段階昇格(thry01先例)を形式自体にも適用=暫定スキーマ→発火pilot→本確定。",
  "jc": 0.82,
  "status": "agreed",
  "note": "Master が『Ignis の推奨で進めて』で go。Ignis 推奨=#2(先に真 fuzzy サンプルを採る)を実行。付帯条件3つ(期限・終了条件/3機構方針/真サンプル+観察目的)を pilot 計画に織り込み。単方向 fill(output-format §8)。",
  "before_ts": "2026-05-31T02:00:00Z",
  "sha": "611682c2566dcda7e3c457840f1ce797e3f5974c",
  "worktree": "/tmp/wt-pc1f01"
 },
 {
  "id": "council-2026-06-07T03:40:00Z-mcfg01",
  "category": "judgment",
  "topic": "DH本体の情報代謝パラメータ（token_budget / dry_run_cycles / council_gate 閾値）の正本（canonical loc",
  "judgment": "止揚案。(1) reindex-librarian skill の config 読込みを単一解決ロジックに昇格=『REGIME.md ## 情報代謝設定 があればそれ、無ければ DH-self 既定パス history/.metabolism-config.yml の同名キー』。利用者/DH で経路を分岐させない(開発者・分岐負債ゼロ)。REGIME.md 不在時 fallback 未定義ギャップも同時に閉じる。(2) DH-self は利用者と同一の ## 情報代謝設定 セクション構造で持つ(哲学者/Master の dog-fooding 論点・フラクタル整合)。(3) root REGIME.md は新設しない(明文化済み慣習維持・利用者誤認回避・経営者の scope-creep 警告)。(4) reduction_target: DH を明記し利用者(D1-D3)との還元先非同形を保つ(哲学者・DH独立性/代謝汚染防止)。(5) cursor は機械カーソルとして責務分離維持。",
  "jc": 0.74,
  "status": "agreed",
  "note": "final_decision は人間(Master)が埋めた(単方向 fill, output-format §8)。2 ラウンド目は新情報による正規の追加質問(最大2往復以内)。",
  "before_ts": "2026-06-07T03:40:00Z",
  "sha": "4fa032724495f4530238b61826ccc16c453834fa",
  "worktree": "/tmp/wt-mcfg01"
 },
 {
  "id": "council-2026-06-07T05:00:00Z-mtb2sc",
  "category": "judgment",
  "topic": "本番 reindex 第二弾で (b)中確度 / (c)サブ作業ログをどこまで COLD 移送するか",
  "judgment": "(b)全6 + 結晶化を内容確認できた (c) のみ移送。開発者ゲートを必須適用。refs-draft は発酵層タグ+再訪予約、project-derived-councils は管轄外(還元先project)として恒久除外。",
  "jc": 0.8,
  "status": "agreed",
  "note": "",
  "before_ts": "2026-06-07T05:00:00Z",
  "sha": "01f31ef9c8056d0732cb597f0479914101426f00",
  "worktree": "/tmp/wt-mtb2sc"
 },
 {
  "id": "council-2026-05-12T14:30:00Z-adpp01",
  "category": "judgment",
  "topic": "人間の刻み方を捨て AI スペックに依存した開発スピードで進める方針を DH 全体に採用すべきか、その境界条件は何か",
  "judgment": "β を中核採用 + α/ε の各条件を統合した運用ルール",
  "jc": 0.76,
  "status": "agreed",
  "note": "",
  "before_ts": "2026-05-12T14:30:00Z",
  "sha": "caaa6fd942b448bbf4e446af68c7df815300c050",
  "worktree": "/tmp/wt-adpp01"
 },
 {
  "id": "council-2026-04-21T00:00:00Z-b7e2f1",
  "category": "implementation",
  "topic": "POST /extract の PDF テキスト抽出ライブラリとして、pdfplumber (案A) と pymupdf (案B) のどちらを採用すべきか。",
  "judgment": "案A (pdfplumber) + extractor 抽象レイヤ（哲学者の第3の道を mitigation として統合）",
  "jc": 0.78,
  "status": "agreed_with_synthesis",
  "note": "案A (pdfplumber) を採用しつつ哲学者の第3の道 (extractor 抽象レイヤ) を mitigation として統合",
  "before_ts": "2026-04-21T00:00:00Z",
  "sha": "162df1b5221e3b617b09672a2c06050e3d4dfc80",
  "worktree": "/tmp/wt-b7e2f1"
 },
 {
  "id": "council-2026-05-13T03:35:00Z-rtkSHA",
  "category": "operation",
  "topic": "rtk-integration/scripts/install.ps1 の `$ExpectedSha256` が空文字のままだと default で inst",
  "judgment": "案 A: $ExpectedSha256 = '3b9f207e8ea360d744649760788cbcf7d6ce62d8ccb8677aa3c8d1513a9d2cc2' を populate。現状の 'empty → reject + escape hatch (RTK_SKIP_VERIFY=1)' 構造は維持。SHA 値の信頼根拠は公式 GitHub Release checksums.txt (https://github.com/rtk-ai/rtk/releases/download/v0.37.1/checksums.txt) + 本セッションで zip 独立 download + sha256sum self-compute の cross-verify (公式値と完全一致)",
  "jc": 0.78,
  "status": "agreed_with_synthesis",
  "note": "案 A 採用 + 哲学者 minority opinion を同 PR (claude/fix-rtk-install-sha-TDmT8) に併合 (Option D 格上げ): references/sha-update-protocol.md を新設し SKILL.md の参照ドキュメント節からリンク。本 cycle で long-term 課題を解消することで Maintainer 責務を",
  "before_ts": "2026-05-13T03:35:00Z",
  "sha": "7e34e6d0c3c520c934b4d14f16fb794ae92f2c7e",
  "worktree": "/tmp/wt-rtkSHA"
 },
 {
  "id": "council-2026-04-29T21:00:00Z-d4mtr2",
  "category": "conception",
  "topic": "D4 検査機構の名称（meta-verifier / harness-verifier / dh-integrity / singularity）",
  "judgment": "harness-verifier/ を機械可読名として採用、PHILOSOPHY.md で singularity 併記の二重命名",
  "jc": 0.82,
  "status": "agreed",
  "note": "",
  "before_ts": "2026-04-29T21:00:00Z",
  "sha": "47cac67b594950e14dfd07684a27f1e684bd521c",
  "worktree": "/tmp/wt-d4mtr2"
 }
]
```

### 5.2 (b-full) 結果

```jsonl
{"id":"council-2026-04-30T11:01:00Z-l0agg2","b_recommended":"Council 判定 + DH evolution に限定（verification は集約外・要約のみ後段）","b_confidence":0.72,"b_dimension":"D4","recorded_judgment":"案B-1: Council 判定のみ","match":"mismatch","note":"(b) は集約範囲を 1 段広く取った（+DH evolution）。方向は近いが選択肢としては別案"}
{"id":"council-2026-05-06T08:30:00Z-amrev1","b_recommended":"opt-out 採用は条件付き（opt-in 領域を CI の path ガードで機械付与）。無い間は opt-in 維持","b_confidence":0.72,"b_dimension":"可逆性","recorded_judgment":"C: ハイブリッド採用。philosophy/harness-verifier/不可逆は opt-in 維持、定型のみ opt-out。境界 SPEC 不変化 + roll-back","match":"match","note":"骨格一致（ハイブリッド）。(b) は機械ガードを前提条件に格上げ＝Council 事後評価 f9b2c4 推奨(1) と同内容を単独で導出"}
{"id":"council-2026-04-21T00:00:00Z-b7e2f1","b_recommended":"案B pymupdf","b_confidence":0.78,"b_dimension":"performance","recorded_judgment":"案A pdfplumber + extractor 抽象レイヤ","match":"mismatch","note":"逆の案。(b) は性能軸のみで判定、Council は抽象レイヤ（第3の道）を統合。人間は Council 案に synthesis で同意"}
{"id":"council-2026-05-11T03:14:18Z-vbxdnd","b_recommended":"A .claude/refs/industry/ecc/ + 参照元 6 箇所を同一 PR で更新","b_confidence":0.72,"b_dimension":"dependency","recorded_judgment":"A .claude/refs/industry/ecc/ を採用（哲学者 C を少数意見保持）","match":"match","note":"同一案。Council は jc 0.45 で人間へ降ろした案件だが (b) は 0.72 で単独収束（少数意見 C の視点は出ていない）"}
{"id":"council-2026-06-07T03:40:00Z-mcfg01","b_recommended":"正本は history/.metabolism-config.yml 据え置き、解決順（REGIME.md §情報代謝設定 → 無ければ本ファイル）だけを参照させる","b_confidence":0.82,"b_dimension":"coupling","recorded_judgment":"止揚案: 単一解決ロジック『REGIME.md があればそれ、無ければ history/.metabolism-config.yml』","match":"match","note":"解決順まで一致。(b) は実装（signal-scan.py）を読んで導出"}
{"id":"council-2026-05-31T02:00:00Z-pc1f01","b_recommended":"今は本確定せず、pilot 規定の延長 1 回を期限付きで発動し発火記録経路を整備してから再諮問","b_confidence":0.70,"b_dimension":"実績","recorded_judgment":"暫定スキーマで pilot してから本確定（付帯条件 3 点）","match":"match","note":"核心（今は確定しない・pilot 先行）は一致。(b) は pilot 後の現状を踏まえた続きの判断になっている（時点差）"}
{"id":"council-2026-05-12T14:30:00Z-adpp01","b_recommended":"条件付き採用: opt-out 領域に限り AI スペック駆動、opt-in 領域は人間の刻みをゲートとして残す。circuit-breaker 有効化と判定漏れ率の sensor 化を条件","b_confidence":0.72,"b_dimension":"可逆性","recorded_judgment":"β を中核採用 + α/ε の各条件を統合した運用ルール","match":"match","note":"骨格一致（条件付き採用）。(b) は境界を auto-merge-boundary の opt-in 表で具体化"}
{"id":"council-2026-06-11T-d4mtr2","b_recommended":"harness-verifier を維持、singularity は PHILOSOPHY.md 内の比喩的別名に限定","b_confidence":0.86,"b_dimension":"coupling","recorded_judgment":"harness-verifier/ を機械可読名として採用、PHILOSOPHY.md で singularity 併記の二重命名","match":"match","note":"同一。ただし (b) は既に決定後の repo 状態を読んで導出（時点差・リーク相当）"}
{"id":"council-2026-06-07T05:00:00Z-mtb2sc","b_recommended":"確度ラベルでなく結晶化証跡（逆引き先の grep 確認）を移送条件に。証跡なしは WARM 据え置き、project-derived は恒久除外","b_confidence":0.78,"b_dimension":"逆引き可能性","recorded_judgment":"(b)全6 + 結晶化を内容確認できた (c) のみ移送。開発者ゲート必須。project-derived-councils は管轄外で恒久除外","match":"match","note":"同一（結晶化確認ベース・project-derived 除外）"}
{"id":"council-2026-05-13T03:35:00Z-rtkSHA","b_recommended":"案A: SHA256 を populate、fail-closed + escape hatch は維持","b_confidence":0.90,"b_dimension":"security","recorded_judgment":"案A: $ExpectedSha256 を populate。現状の empty → reject + escape hatch 構造は維持","match":"match","note":"同一"}
```

### 5.3 (b-snap) 結果

```jsonl
{"id":"l0agg2","b_recommended":"Council ログのみに限定。evolution/verification は既存蓄積場所に留め consumer 出現時に再諮問","b_confidence":0.72,"dimension":"D4","match":"match","tokens":85041,"files_read":13}
{"id":"b7e2f1","b_recommended":"案A pdfplumber（MIT・性能 SLO 未定義ゆえ安全側）、将来アダプタで差替可","b_confidence":0.62,"dimension":"license","match":"match","tokens":70349,"files_read":7}
{"id":"amrev1","b_recommended":"反転せず opt-in 維持。stop ラベル/circuit breaker 実装後に issue-pickup 起点 PR 限定で段階導入","b_confidence":0.78,"dimension":"安全性","match":"mismatch","tokens":89053,"files_read":16,"note":"Council は C ハイブリッド（定型のみ opt-out）。(b) は決定時点で stop ラベル未実装を実測し反転を否定。人間は Council 案に synthesis 同意"}
{"id":"vbxdnd","b_recommended":"A .claude/refs/industry/ecc/ + INSIGHTS へ精神を蒸留し skill からの直接リンク禁止","b_confidence":0.70,"dimension":"配置構造","match":"match","tokens":81283,"files_read":13}
{"id":"rtkSHA","b_recommended":"案A SHA256 populate + escape hatch 維持 + troubleshoot 追記","b_confidence":0.82,"dimension":"consistency","match":"match","tokens":70007,"files_read":6}
{"id":"adpp01","b_recommended":"採用（刻みの主体の置換）。D1-D3 限定・CTL 連動・小バッチ不変・escalate 条件・観測厚化の 5 条件","b_confidence":0.72,"dimension":"可逆性","match":"match","tokens":91401,"files_read":9}
{"id":"pc1f01","b_recommended":"今は確定せず、暫定 v0 規格として任意付記し実結晶 3-5 件で確定諮問","b_confidence":0.72,"dimension":"D4","match":"match","tokens":88136,"files_read":17}
{"id":"mcfg01","b_recommended":"DH root に REGIME.md を新設し §情報代謝設定 を唯一の正本に","b_confidence":0.62,"dimension":"構造整合","match":"mismatch","tokens":89564,"files_read":16,"note":"Council は解決順（REGIME.md があればそれ、無ければ history/.metabolism-config.yml）で両立。(b) は前例（DH 本体は root REGIME.md を持たない）と衝突する案を選択"}
{"id":"mtb2sc","b_recommended":"(b) 6 全件 + wave1-5/deliveries を COLD、council-readable/project-derived/refs-draft は除外、source pointer 同 commit 書換","b_confidence":0.72,"dimension":"参照依存","match":"match","tokens":96482,"files_read":25}
{"id":"d4mtr2","b_recommended":"harness-verifier（対象-役割型・prefix なしで独立機構と判別）","b_confidence":0.72,"dimension":"naming","match":"match","tokens":98511,"files_read":9}
```

### 5.4 手順

1. 抽出: 評価済み 82 件を category 比例で 10 件（seed 20260913、jc 欠損 1 件を seed 7 で補充）
2. snapshot: `git fetch --unshallow` 後 `git rev-list -1 --before=<timestamp> origin/master` → `git worktree add --detach`
3. (b): 一般 agent に topic_summary のみを渡し JSON で推奨を回収。(b-snap) は worktree 外の読取を禁止
4. Council 側トークンは workflow `wf_b6565b55-2d6`（v7phsa）の usage（379,402 tok・5 agent）
