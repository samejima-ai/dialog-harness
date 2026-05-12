---
name: layer1-autonomous-dev
dimension: D4
description: >
  Layer 0（spec-architect）が構築した仕様ドキュメントと開発環境を受け取り、
  AI単独で開発を完遂し成果物を人間に献上するスキル。
  「開発を始めて」「作って」「実装して」「ビルドして」「テストして」「デプロイして」
  「リリースして」「本番に上げて」「アプリ完成させて」「implement」「ship」「出荷」
  「コード書いて」等、仕様が確定した状態から実装・ビルド・配布までの発話でトリガーする。
  SPEC.md / REGIME.md が存在し仕様策定が終わっている状況なら、明示されなくても
  本スキルの起動を必ず検討する（コーディングだけでなくビルド・テスト・配布の依頼も含めて
  実装関連はまず本スキルで扱うのが既定）。
  仕様策定や環境構築の段階ではトリガーしない（それは spec-architect の責務）。
  新規仕様や SPEC 改変を伴う機能追加は spec-architect に差し戻す。
  開発中に人間に質問しない。仕様不足は即献上で対処する。
  REGIME.md のモード（M1/M2）に応じて実行フローを分岐する。L2判定時は layer2-orchestrator に委譲する。
---

# Autonomous Dev

仕様ドキュメント＋開発環境を入力として、AI単独で成果物を仕上げて献上するスキル。

## 原則

- 開発中に人間に質問しない。自走して献上する
- 仕様不足は即献上（開発に入らない）。仕様不足のままトークンを浪費しない
- 「仕様に合う・動く・使える」が判定基準。これを満たせばAIの解釈は問わない
- Layer 0ドキュメントを直接書き換えない
- コスト上限を超えた実行を継続しない
- REGIME.md で指定されたモードに従い、実行フローを分岐する
- L2判定の場合は自力で進めず layer2-orchestrator に委譲する
- **WF 形状単一性**: 機能タイプ別の分岐 WF を持たない。bug-fix / 新規機能 / リファクタ / 仕様改訂等は本 §処理フロー (1〜8) を共通基底とし、機能タイプの違いは §4「実装タスク分解」内の context として扱う。観測閾値（同一 override パターンが 3 機能タイプ以上で反復）に達した場合のみ Council 経由で基底引き上げを諮る。詳細・根拠は `references/wf-baseline-rationale.md` 参照（v5.3.0 で追加）

## 処理フロー

```
1. ドキュメント＋開発環境の受領
1.1. 依存導入の事前チェック（lock / manifest 起点で偽 FAIL を防ぐ）
1.5. LC ≥ 1 の場合: history/INTENT.md / CHANGELOG.md を読み込む
     儀式拒否（E2）時の背景照合タスクもここで受領
2. REGIME.md 読み込み → モードに応じて実行フローを選択
   L2 → layer2-orchestrator に委譲してここで終了
   M1/M2 → 次へ
3. 仕様レビュー（過去INTENTとの整合性も含む）
   → 問題あり: 仕様レビュー結果を即献上（ここで終了）
   → 問題なし: 次へ
4. 実装タスク分解
   → 複数実装案が拮抗 or 実装者 confidence < 0.6 の判断点がある場合
     → `crosscut-council` スキルを起動して判断を仰ぐ（詳細は本文「Council 発動」節参照）
5. タスク実行（コーディング）
5.5. Shift Left 基盤 + 5層エラー検出スタックに沿った自己検証（計算的解決最優先）
     Shift Left 基盤（spec/ 逸脱なし確認） → 第1層（計算的センサー全PASS）
     → 第2層（E2E機械検証） → 第3層（Interaction Cost 測定）
     不可逆操作（データ破壊/スキーマ変更/認証系変更/公開範囲変更等）検出時は
     直前に `crosscut-council` を起動して判断を仰ぐ
     詳細は `references/inferential-sensor-v2.md` 参照
6. 自己検証（計算的センサー＋推論的センサー）
   → 失敗: 自力修正して6に戻る
   → 修正不可能: フィードバックレポートに記載して7へ
7. M2の場合: layer1-independent-reviewer を起動（常時必須）
   → PASS: 次へ
   → FAIL: 差戻し理由に従い6に戻る（自力修正上限内）
7.5. LC ≥ 1 の場合: 履歴層更新差分を3段階承認で作成
     - A（自動承認）: CHANGELOG.md 追記、SUMMARY.md 再生成
     - B（確認推奨）: INTENT.md 新規追加、REGIME-LOG.md 更新
     - C（必須承認）: INTENT.md 廃止・訂正、REGIME.md スコア変更
8. 成果物＋フィードバックレポート＋体制事後評価＋履歴層更新差分を献上
```

## モード別の実行フロー

REGIME.md の判定結果に従い、以下のように分岐する。

### M1 単体モード

- 仕様レビューを簡略化（最低粒度チェックのみ）
- 計算的センサー中心で検証
- 推論的センサーは自己検証で兼用可（軽量運用）
- **layer1-independent-reviewer は起動しない**
- 献上物は DELIVERY.md のみ（VERIFICATION.md / INTEGRATION.md は生成しない）

### M2 標準モード（通常パス）

- 上記処理フローを全ステップ実行
- この規格のデフォルト動作
- ステップ7の layer1-independent-reviewer 起動は**常時必須**
- L1自己検証 PASS + layer1-independent-reviewer PASS の両方が成立したら献上
- 判定が割れた場合は FAIL 扱いにして原因調査→差戻し

### L2 統括指揮モード

- autonomous-dev は**本体実装に進まない**
- ステップ2で REGIME.md のモードが L2 と判明したら即座に layer2-orchestrator に委譲
- L2オーケストレータ配下で個別ドメインの L1 として再起動される（その際は当該ドメインの SPEC に対して M1/M2 動作を行う）

### L0 対話延長状態

- autonomous-dev はトリガーされない
- Layer 0 で対話が継続している状態。実装には進まない

## ステップ詳細

### 1. ドキュメント受領

INDEX.mdから読み込みを開始し、必要なドキュメントを動的に取得する。

読み込み順序：
1. INDEX.md（全体目次）
2. CLAUDE.md（エージェントRL）
3. REGIME.md（モード判定結果）
4. SPEC.md（機能仕様）
5. DONT.md（スコープ外定義）
6. sensors/（センサー定義）
7. L2の場合は DOMAINS.md も読む（ただし L2 判定なら layer2-orchestrator に委譲）
8. **DESIGN.md が存在する場合**（v5.15.0 追加、UI プロジェクトのみ）: 視覚仕様 + デザイントークン。UI 実装時は YAML フロントマターのトークンを参照し、HEX リテラル・px 直書きを避ける。`## Do's and Don'ts` セクションをデフォルト遵守する。規格詳細は `.claude/skills/layer0-spec-architect/references/design-system-spec.md`

### 1.1 依存導入の事前チェック

計算的センサー初回実行前に、依存関係が解決されているかを確認する。「依存未解決」は仕様問題でも実装問題でもない、純粋な前提条件問題として扱い、本ステップで吸収する。

チェック方針：
- lock / manifest 起点で同型に判定する（harness は env-agnostic を維持するため、ecosystem 列挙は例示扱い）
- 解決済みの場合は即 skip。導入が必要な場合のみ ecosystem 標準コマンドを実行する
- 1 秒以内に判定可能（存在確認のみ）。導入実行は本ステップ内で完結させる

ecosystem 別の例：
- Node プロジェクト：lockfile を識別子に package manager を判別し、対応する install を実行する
  - `package-lock.json` あり (npm)：`node_modules/.package-lock.json` の存在確認 → なければ `npm ci`
  - `pnpm-lock.yaml` あり (pnpm)：`node_modules/.pnpm/` の存在確認 → なければ `pnpm install --frozen-lockfile`
  - `yarn.lock` あり (yarn)：`node_modules/` または Plug'n'Play (`.pnp.cjs`) の存在確認 → なければ `yarn install --frozen-lockfile`
- Python プロジェクト：venv の存在確認 → なければ `pip install -r requirements.txt` または `uv sync`
- Rust プロジェクト：`Cargo.lock` を起点に必要に応じて `cargo fetch`
- その他 ecosystem：プロジェクト固有の lock / manifest を起点に同型のチェックを行う

このチェックを省略するとセンサーが偽の失敗を返し、自力修正サイクルを浪費する。ステップ 5.5 以降のセンサー実行群すべてに先立つ前提条件として実行する。

依存導入そのものが失敗した場合（lock 破損 / レジストリ到達不可 / 権限不足等）は、仕様問題ではないため Type A 仕様レビュー結果には該当しない。本ステップ内で自力修正サイクル（再ダウンロード・ミラー切替・lockfile 再生成等）を最大 3 回試行し、それでも解消しない場合はステップ 6 の自力修正上限到達と同様に扱い、ステップ 8 献上物テーブルの **Type D 異常献上**（発生条件「自力修正上限到達後に技術的解消不能」）として献上する。

### 2. REGIME.md 読み込みとモード分岐

REGIME.md のモードを読み取り、以降のフローを決定する。
分岐の詳細は上記「モード別の実行フロー」を参照。

モードが不明または記載がない場合：
- デフォルト M2 として実行
- 献上時にフィードバックレポートで指摘
- REGIME.md の AI能力バージョン記載も確認し、記載なしなら指摘する

### 3. 仕様レビュー

SPEC.mdの内容を実装者の視点で検証する。
チェックリストの詳細は `references/spec-review-checklist.md` を参照。

検証観点：
- 実装可能性：記載された機能と条件で実装を開始できるか
- 矛盾：機能間・条件間で矛盾がないか
- 不足：「機能×条件」の最低粒度を満たしているか
- スコープ侵食：DONT.mdの領域に踏み込んだ要件が含まれていないか
- 体制齟齬：REGIME.md のモードと SPEC の実態が乖離していないか

問題を検出した場合：
- 開発に入らない
- 問題点を構造化して仕様レビュー結果として即献上する
- 詳細は `references/delivery-format.md` の「仕様レビュー結果」セクションを参照

仕様レビューの実行タイミング：
- **初回**：ドキュメント受領時に必ず実行
- **更新時**：仕様変更のたびに差分レビューを実行

### 4. 実装タスク分解

SPEC.mdの機能一覧をもとに実装タスクに分解する。

分解の原則：
- 1タスク＝1機能または1機能の1側面
- タスク間の依存関係を明確にし、依存順に実行する
- タスクリストをファイルに書き出して進捗を追跡する

### 4.5. Council 発動（判断点検出時のみ）

分解の過程で判断点が現れた場合、自力解釈で進めずに `crosscut-council` スキルを起動する。
原則「開発中に人間に質問しない」は維持する — Council は人間ではなく判断モジュールである。

#### 判断分類（philosophy 第6条）

判断点は H / C の 2 カテゴリに分かれる。**カテゴリ定義は philosophy.md 第6条が原典で、本ファイルでは内容転記しない**（philosophy.md L4 / L282 メタ規則：他 skill は参照のみ・内容転記禁止＝散逸防止）。

L1 の運用上の振る舞いは以下：

- **H カテゴリ抵触を検知**（philosophy.md §6「人間専管判断」）: Council を起動せず**即時献上（タイプ A）** で人間に判断を委ねる。権限境界の問題であり判断機構の問題ではない
- **C カテゴリ抵触を検知**（philosophy.md §6「Council 代替可能判断」）: Council を起動し、REGIME.md の CTL（Council Trust Level）が該当カテゴリを委譲範囲に含むかで自律実行と判断献上を切り替える

L0 spec-architect が REGIME.md に CTL を明示しているので、L1 はそれを引き継いで参照する（CTL の独自算出はしない）。詳細な H1〜H4 / C1〜C4 の定義は `.claude/skills/layer0-spec-architect/references/philosophy.md` §第6条 を直接参照すること。

#### 発動トリガー（C カテゴリのみ）

以下のいずれかに該当したら Council を発動する：

| 条件 | カテゴリ | 例 |
| --- | --- | --- |
| 複数実装案が viable で拮抗 | C2 | ライブラリ選定、アルゴリズム選択、データ構造選択 |
| SPEC/DONT で曖昧さを検出 | C4 | 仕様文言が2通り以上に解釈できる |
| 不可逆操作を含むタスク（権限内） | C3 | マイグレーション、データ削除、スキーマ変更、認可境界変更 |
| 実装者 confidence < 0.6 | C1 / C2 | 自己評価で自信が持てない判断 |

H カテゴリ（H1〜H4）の抵触を検知したら、Council 発動ではなく**即時献上（タイプ A）** に切り替える（ステップ8 直行）。例: SPEC.md の根本書き換えが必要 / モード昇格降格が必要 / philosophy.md 改訂が必要。

発動しない場合（裁量で進める）：

- タイポ・フォーマット・明確仕様の素直実装・定型リファクタ
- 単一実装パスしかない場合
- Council の過去 COUNCIL-LOG に類似判断があり `recommended` と一致する方針を取る場合

#### 発動方法

1. 入力を構造化する（`.claude/skills/crosscut-council/references/output-format.md` §1 参照）:
   - `context`: 該当タスクとその周辺状況
   - `options`: 複数案（少なくとも2つ、Council は第3の道を提示してよい）
   - `question_to_answer`: 問いを1文で
   - `source_skill`: `layer1-autonomous-dev`
   - `category`: `implementation` / `operation` / `maintenance` / `error_handling` 等
2. `crosscut-council` スキルを起動する
3. Judgment Agent の出力を受け取る（`recommended` / `reasoning` / `minority_opinion` / `judgment_confidence` / `final_decision: null`）
   - `final_decision` が常に null である理由: 第6条により Council は判断機構であり決定機構ではない。決定は人間または実装者の合意プロセスが担う。CTL ≥ CTL-1 で該当 C カテゴリが委譲範囲内なら、実装者の合意プロセスが Council 結果を採用して続行できる。
4. 合意プロセスに入る（`.claude/skills/crosscut-council/references/consensus-protocol.md` 参照）:
   - 実装者は `recommended` を採用するか、別案で実装するかを決定する
   - REGIME.md の CTL を確認し、該当 C カテゴリが委譲範囲外なら判断献上（Council 結果を参考情報として人間に渡す）
   - `judgment_confidence < 0.5` の場合は自動で人間エスカレーション（献上で報告）
   - 採用可否と根拠を DELIVERY.md の**体制事後評価内の履歴系記録欄**に記載する（Council 発動記録専用節の新設は PR2 で予定）

#### 結果の扱い

| Council 判断 | L1 の振る舞い |
| --- | --- |
| `recommended` + 合意可能 | 該当案で実装を続行 |
| `recommended` + 実装者に強い異論 | 実装者案で進める旨を合意プロセスに記録し続行（Council は判断支援） |
| `judgment_confidence < 0.5` | 人間エスカレーション（該当判断の実装保留、他タスクを先行） |
| `conflict_type: E`（前提対立、PR2 以降） | SPEC 差し戻し、即献上 |

`final_decision` は常に null で来る。実装者が合意プロセスで方針化する責務を負う。

### 5. タスク実行

CLAUDE.mdのRLに従いコーディングを実行する。

実行中のルール：
- DONT.mdの領域に踏み込まない
- 仕様の曖昧さは合理的に解釈して進める（「仕様に合う・動く・使える」なら許容）
- 外部ライブラリの選定はAI判断で行う
- ARC原則モノリスに従う
- **DESIGN.md が存在する場合**（v5.15.0 追加）: UI 実装は DESIGN.md の YAML トークンを参照し、CSS / Tailwind config / CSS-in-JS / styled-components で HEX リテラル・px 直書きを避ける。新規 UI コンポーネント実装時は `## Components` セクションに該当定義を追加（YAML + Markdown の 2 層を維持）。`## Do's and Don'ts` をデフォルト遵守

### 6. 自己検証

sensors/ の定義に従い、成果物を検証する。

#### 計算的センサー（sensors/computational.md）
- ビルド、型チェック、リンター、テストを実行
- 全て1分以内に完了する制約
- 失敗したら自力で修正し、再実行

#### 推論的センサー（sensors/inferential.md）
- SPEC.mdと実装を照合
- 「仕様に合う・動く・使える」の3条件で判定（リファクタ時は **+ 意図合致** で 4 条件）
- 不合格なら自力修正を試みる
- 修正不可能な場合はフィードバックレポートに記載

#### DESIGN.md 検証（v5.15.0 追加、DESIGN.md 存在時のみ）

**重要**: トークン整合の grep 検査だけでは UX を保証できない（philosophy 三拍子「仕様に合う・動く・使える」のうち「使える」は静的検査で判定不可能）。philosophy 5 層検出スタックの第 2/5 層を必ず通す。

第 1 層（計算的・静的）:
- src/ 配下に HEX リテラル（`#[0-9A-Fa-f]{6}`）や px 直書きが含まれていないか grep
- 含まれている場合は DESIGN.md の YAML トークン参照（CSS 変数 / Tailwind theme / styled-components theme）に置換

第 2 層（E2E スクショ）— **DESIGN.md 存在時は必須**:
- Playwright で主要画面を起動し `page.screenshot()` で `delivery/screenshots/` 配下に保存（ファイル名は `<screen-name>.png` 形式）
- baseline 比較（`expect(page).toHaveScreenshot()`）を導入している場合は同時実行
- 第 1 層通過後に発動（Console エラー残置時は中断）

第 5 層（Vision モデル判定）— UX Priority `standard` 以上で必須:
- 保存した screenshots と DESIGN.md `## Do's and Don'ts` を Vision モデルに入力
- 検出対象: フォントウェイト混在、`colors.error` 流用、`colors.primary` 装飾流用、角丸不統一、コントラスト比違反など
- 違反検出時は自力修正サイクルに戻る

検査結果は DELIVERY.md「DESIGN.md 検証」セクションに 3 層分（静的 / E2E / Vision）記載。コードファーストでは検出できない不整合（フォントフォールバック、レスポンシブ崩れ、ダークモードのコントラスト等）は第 2/5 層でのみ検出される。詳細は `../layer0-spec-architect/references/design-system-spec.md` §E2E 視覚検証 参照。

#### 意図合致検証（v5.5.0 Phase γ コア 3 件、起動条件は AND 結合）

**起動条件** (`../layer0-archeo-architect/references/handoff-to-evaluator.md` §I/O 契約 L64-68 と同期):

```
exists("delivery/refactor-intent-map.md") AND map.Meta.self_verification == "passed"
```

両条件成立時のみ第 4 軸「意図合致」を起動する。`refactor-intent-map.md` 不在 / archeo 自己検証 FAIL のいずれかなら本ステップは完全スキップ（後方互換完全維持、3 軸動作）。

各 Island の `refactor_directive` と Boundaries の `human_decision` を **AND 結合**で評価する（archeo handoff contract 準拠、§79-84）:

##### preserve 領域 — `assertion: no_modification` 一次条件 + 承認テスト二次条件（先行宣言 1 本実装）

業界根拠: フェザーズ「レガシーコードとはテストのないコードである」/ Approval Testing カノン。

`refactor_directive: preserve` の Island は upstream 規約で「現状維持（リファクタ対象外）」= `assertion: no_modification`（archeo handoff §73-76 / refactor-intent-map-template.md §61-64）。検証は二段階：

**一次条件: コード変更ゼロの assertion 検査**

1. preserve Island の paths について `git diff` を実行
2. 変更行数 > 0（行追加・削除・編集のいずれか）→ **即 FAIL**（構造変更だけでもダメ、振る舞い同等でも禁止）
3. 変更ゼロ → 一次条件 PASS、二次条件へ

**二次条件: 既存テスト + 承認テストの振る舞い検証**（一次条件 PASS 時のみ実行）

1. 既存テストがある領域では既存テスト全件 PASS を確認
2. 既存テスト不足分のみ承認テストで補完: 現状のコードの入出力を `delivery/approval-tests/<island-id>.baseline.json` として基準データ化
3. 既存テストおよび承認テスト全件 PASS で二次条件 PASS

二次条件は「将来の仕様変更時の振る舞い記録」として運用される（一次条件で構造変更が禁止されているため、本来は冗長だが、preserve 領域に依存する他箇所の変更が間接的影響を与えないかの保険）。一次条件 / 二次条件のいずれか FAIL → **`failure: intent_drift`** として Type C 献上。

ツール選択（Qodo / Byteable 等）は L1 実装者の裁量。

##### restructure 領域 — 自動照合ループ（先行宣言 2 本実装）

業界根拠: VB6 価格エンジン移行事例（14 ヶ月で 8,064 回の自動照合ラン、0.007% 不一致検出、420 万ドル損失防止） / Branch by Abstraction パターン。

`refactor_directive: restructure` の Island は、**新旧並行実行 + 結果照合**で意図保持を機械的に検証する：

1. リファクタ前の実装を「旧」、後の実装を「新」として両方を残す（Branch by Abstraction）
2. 抽象化レイヤー越しに同入力を両者に流し、結果を比較し `delivery/reconciliation-logs/<island-id>.log` に記録
3. 不一致率の閾値（デフォルト 0.01%）を超えたら **`failure: intent_drift`** として Type C 献上
4. 並行実行期間（L1 実装者裁量、典型は 1〜2 週間）後、新実装に切替

L2 統合検証との接続: 複数 Island に渡る restructure では `layer2-integration-verifier` が照合結果を集約する（L2 発動時のみ、PR 範囲外）。

##### discard_and_redesign 領域

`AbsentZone.redesign_directive` に従う。意図保存制約は解除されているため承認テスト・自動照合は不要。

##### 判定の集約

意図合致軸の判定は `delivery/DELIVERY.md` に「意図合致検証」セクションとして記録する（フォーマット: `references/delivery-format.md` §意図合致検証 参照）。

#### 自力修正の上限
- 同一エラーに対する修正試行は最大3回
- 3回で解決しない場合はフィードバックレポートに記載して次へ進む

### 7. 独立検証（M2以上で必須）

**M2の場合は常時必須**。M1では実行しない。

- `layer1-independent-reviewer` スキル（Level A）を起動する
- 入力: SPEC.md / DONT.md / REGIME.md / sensors/ / 成果物パス
- 出力: `delivery/VERIFICATION.md`（実装コンテキスト隔離原則）
- 判定:
  - PASS → ステップ8（献上）へ
  - FAIL → 差戻し理由に従いステップ6に戻る（自力修正上限内）
  - 自力修正上限を超えた場合は未解決事項としてフィードバックに記載し献上

layer1-independent-reviewer の役割と設計原則は `.claude/skills/layer1-independent-reviewer/SKILL.md` を参照。
プロジェクト差異は sensors/ や `sensors/review-checklist.md` に閉じる（agent本体はプロジェクト不変）。

### 7.5. PR 作成 + stop ラベル判定（v5.9.0 追加、`dev_mode` ≥ `github_assisted` で参照）

PR 作成時、対話中に**変更内容が opt-in 領域に該当するか**を判定し、該当する場合は `human-review-needed` ラベルを付与する。該当しない場合は無言で PR を作成し、`auto-merge.yml` のデフォルトに任せる（v5.9.0 で opt-in→opt-out 反転、Council 諮問 `council-2026-05-06T08:30:00Z-amrev1` 由来）。

**判定基準（いずれか該当で `human-review-needed` 付与確認発話）**:

| 軸 | 該当例 |
|----|--------|
| **不可逆性** | DB migration、データ削除、外部 API 破壊変更、secrets 削除、branch 強制 push |
| **DONT.md 抵触** | プロジェクトの `DONT.md` で禁止された領域への侵入（この場合は `do-not-merge` 推奨） |
| **Council 起動 + 低 confidence** | Council 諮問が起動し `judgment_confidence < 0.5` で escalate された場合 |
| **philosophy 改修** | `.claude/skills/layer0-spec-architect/references/philosophy.md` の追記・改訂 |
| **harness-verifier 自己改修** | `harness-verifier/**`（reports/ 配下の月次自動生成は除外） |
| **複数 SPEC 横断改修** | 3 ファイル以上の `.claude/skills/*/SKILL.md` または references/*.md を同 PR で改修 |
| **autonomous-drive workflow 改修** | `.github/workflows/auto-merge.yml` `issue-pickup.yml` `gemini-review.yml` の改修 |
| **境界 SPEC 自身の改修** | `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md` の改修 |

**該当しない場合の opt-out 領域（暗黙オート）**:

- 単一機能追加 / bug fix（1 つの skill 内に閉じる）
- typo / format 修正
- documentation 更新（`history/**`, `delivery/**`）
- 単一 skill SPEC 追記（1 ファイル内）
- リファクタ（動作不変）

詳細な境界分類は `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md` が一次情報源。本ファイルは判定の触発点のみを示す。

**PR 作成手順**:

```bash
# opt-out 領域（暗黙オート）
gh pr create --title "<descriptive title>" --body "<Closes #N 含む詳細>"

# opt-in 領域（人間レビュー待ち）
gh pr create --title "<descriptive title>" --body "<Closes #N 含む詳細>" --label human-review-needed
```

**境界曖昧時**:

- 「opt-out か判定に迷う」状態を検知したら `human-review-needed` を **デフォルト付与**（境界曖昧化を防ぐ安全側挙動）
- セッション駆動の場合は人間に「opt-in 領域に該当しますか？」を発話確認
- L1 単独実行（issue-pickup 経路）の場合は `human-review-needed` 付与で人間に判断を渡す

### 8. 献上

成果物を人間にレビュー可能な状態で献上する。
フォーマットの詳細は `references/delivery-format.md` を参照。

献上物は4種類：

| 種類 | 発生条件 | 内容 |
|---|---|---|
| 仕様レビュー結果（Type A） | ステップ3で問題検出 | 不足・矛盾・実現不可能な点の指摘 |
| 成果物（Type B） | ステップ7完了 | 動作するコード＋フィードバックレポート＋体制事後評価（+ M2は VERIFICATION.md） |
| 仕様改訂提案（Type C） | 開発中〜完了時（仕様改善余地発見） | 該当箇所 / 発見内容 / AIの解釈 / 提案（開発継続、DELIVERY.md に集約） |
| 異常献上（Type D, v5.3.0 で追加） | 自力修正上限到達後に技術的解消不能と判定 | 例外種別 / stacktrace or 再現手順 / 自己解決試行履歴 / 人間判断期待値 / 緊急度（SPEC は更新不要） |

**成果物献上時は体制事後評価を必ず記載する**：
- 判定されたモードが適切だったか
- 過剰／妥当／過少の実感
- L2発動閾値に近づいていなかったか
- 次回以降への示唆

詳細は `references/delivery-format.md` の「体制事後評価（必須）」セクション参照。

## DELIVERY.md 抜粋（イメージ）

M2 モード・LC=0 の成果物献上時の DELIVERY.md 冒頭部分:

```markdown
# DELIVERY.md

## 体制情報
- Mode: M2 / LC=0 / Cycle: 1
- 自律修正回数: 2 / 上限 3

## 実装済み機能
- F1. ユーザー登録 (critical) — PASS
- F2. ログイン (critical) — PASS
- F3. プロフィール画像アップロード (standard) — PASS

## 自己検証結果（5層検出スタック）
| 層 | 対象 | 結果 |
|---|---|---|
| Shift Left 基盤 | 型・lint・フォーマット | PASS |
| 第1層 計算的センサー | 単体/統合テスト 42 件 | PASS |
| 第2層 E2E 機械検証 | Playwright 6 シナリオ | PASS |
| 第3層 Interaction Cost | クリック数 p95=3、応答 p95=1.2s | PASS（閾値内） |
| 第4層 推論的センサー | 「仕様に合う・動く・使える」 | PASS |
| 第5層 独立検証 | independent-reviewer 照合 | 次フェーズ |

## 仕様改訂提案（Type C）
なし

## 異常献上（Type D, v5.3.0 で追加）
なし（自力修正上限到達後に技術的解消不能と判定された場合のみ記載）

## 体制事後評価
M2 は妥当。L2 発動閾値（NFR 3項目同時 critical）には到達せず。次 Cycle も M2 継続を推奨。
```

Type A（仕様レビュー結果）/ Type B（成果物）/ Type C（仕様改訂提案）の完全構造は `references/delivery-format.md` 参照。

## 内部処理の区分

| 区分 | 内容 | 処理 |
|---|---|---|
| 自動処理 | 型エラー、テスト失敗、依存不整合、軽微な曖昧さの解釈 | AI内部で解決 |
| 人間へ報告 | 技術的実現不可能、要件矛盾、パフォーマンス要件未達 | フィードバックレポート |
| 即献上 | 仕様不足で開発続行不可能 | 仕様レビュー結果 |
| 上位委譲 | REGIME.md が L2 判定 | layer2-orchestrator に委譲 |
| 履歴層更新 | LC ≥ 1 での INTENT/CHANGELOG/REGIME-LOG 更新 | 3段階承認で献上差分化 |

## 履歴層更新の責務（LC ≥ 1）

既存プロジェクト（LC=1/LC=2）では、献上時に history/ 配下の更新差分を作成する。
詳細は `references/delivery-format.md` の「履歴層更新差分」セクション参照。

### 更新対象の3段階分類

| レベル | 対象 | 承認 |
|---|---|---|
| A（自動承認） | CHANGELOG.md 追記、SUMMARY.md 再生成、PATTERNS.md への追記 | 人間確認なしで適用 |
| B（確認推奨） | INTENT.md 新規追加、REGIME-LOG.md 更新、ARCH-DECISIONS.md 追記 | 通知のみ、デフォルト承認 |
| C（必須承認） | INTENT.md の廃止・訂正、REGIME.md スコア変更、確度メタデータ上書き | 必ず人間確認 |

### 儀式拒否（E2）時の背景照合

L0 で儀式がスキップされた場合、L1 は実装中に以下を暗黙の追加タスクとして実行：
- 過去 INTENT との整合性チェック（実装完了後）
- 廃止機能への回帰検出
- 却下案の再実装検出

矛盾検出時は DELIVERY.md の「履歴整合性チェック」セクションで報告（人間に質問せず報告のみ）。

## 参照ドキュメント

- `references/spec-review-checklist.md` — 仕様レビューの詳細チェックリスト（過去INTENT整合性含む）
- `references/delivery-format.md` — 献上物のフォーマット定義（DELIVERY.md・VERIFICATION.md・体制事後評価・履歴層更新差分含む。HANDOFF.md との関係も記載）
- `references/handoff-format.md` — HANDOFF.md 規格（v4.2 新規、非エンジニア向け献上サマリー、Section A 自動表示 / Section B 事後評価モード）

## 関連スキル（Level A）

### Layer 系
- `.claude/skills/layer1-independent-reviewer/` — M2以上で常時起動する独立検証agent
- `.claude/skills/layer2-orchestrator/` — L2判定時の統括指揮（委譲先）
- `.claude/skills/layer2-integration-verifier/` — L2オーケストレータが使う統合検証agent

### Crosscut 系（v5.0.0 追加、`dev_mode` ≥ `github_assisted` で参照）
- `.claude/skills/crosscut-council/` — 判断点での合議制判定（既存、v5.0.0 でリネーム）
- `.claude/skills/crosscut-issue-implementer/` — Issue → 実装の起動主体（L1 が呼ばれる側、Actions 経由ありえる）
- `.claude/skills/crosscut-verifier-drift/` — PR 作成時の SPEC drift 検出（L1 自己検証を補完）
- `.claude/skills/crosscut-verifier-philosophy/` — 5 本柱整合検証（v5.1.0 で実装、現状 placeholder）
- `.claude/skills/crosscut-feedback-loop/` — 検証 FAIL / drift / 思想違反の還流先決定
