# INTENT

DH 本体の設計意図・新規概念の記録。

## v5.24.0：E2E 情報代謝サイクルの正式機構化 (in progress)

v5.23.0 §9 で「温存」としたテスト情報代謝を、利用者要望（履歴を含む一連のサイクル + 代謝考慮設計）を受けて
正式機構へ昇格。

### 設計意図の核

**(a) 専用サイクルを作らない**: DH には完成度の高い情報代謝サイクル（北極星=購読量上限 / HOT・WARM・COLD /
Council ゲート / 8 不変条件 / cursor 増分 / source pointer）が既にある。E2E のために別サイクルを新設するのは
重複であり構造同形を壊す。∴ **E2E run 履歴を既存代謝の新しい episodic ソースとして流す**のが正解。

**(b) E2E は project のもの（利用者明示・Council mtbl01 と一致）**: run 履歴・flaky・artifact は「このアプリの
この画面」に閉じた事実＝ project 還元（D1-D3）。正本は利用者プロジェクトの REGIME.md `## 情報代謝設定`。
**DH 本体は対面アプリを持たないため E2E 代謝を稼働しない（定義のみ・dog-food 対象外）**。一般代謝は dog-food
するが E2E はしない、という非対称をはっきり持つ。DH に入るのは「機構の正本(D4)」と「project への scaffold」のみ。

**(c) 二相分離が COLD/HOT に直結**: v5.23.0 の相 A（in-loop 知覚器・使い捨て）/ 相 B（耐久資産）が、そのまま
COLD（artifact・生 run ログ）/ HOT（flaky 罠・安定 journey RL・oracle 結晶）に対応する。設計が一貫する。

**(d) 北極星（購読量上限）を E2E で守る最大の急所**: E2E は毎 CI 実行で大量データを生む。これを素朴に貯めると
購読量が線形膨張する（代謝天井）。∴ **artifact は COLD 直行で既定ロードせず**、蒸留された flaky 罠だけが HOT に
乗る。履歴（disk）は無限に太ってよいが、購読量は密度↑（量↑でない）に保つ。E2E はこの原則の最も厳しい試金石。

**(e) 8 不変条件の E2E 具体化**: #1 単発 flaky を罠にしない（council_gate 反復ゲート）/ #6 罠は生 run ログ
（COLD lossless 原本）から蒸留・E2E-LOG の lossy 要約からは結晶化しない / #8 flaky 罠は反-発火条件必須
（誤発火が debug 困難な flaky で特に重要）。

### サイクルと teeth

5 フェーズ（記録→蓄積→代謝→還流→結晶+排泄）のうち④還流だけが新規 teeth（flaky 率超過→auto-merge 停止 /
circuit-breaker / Quarantine→設計層）。v5.23.0「接続地図のみ」の本体化だが、**強制連動は opt-in/段階**に留める
（実 E2E 運用データで閾値を較正してから＝metabolism 自身の Dry-run 精神・auto-merge-boundary の慎重さ）。

### 温存

- **mutation メタテスト(C4)**: 重いため温存。
- **④teeth の強制化**: auto-merge 自動停止の強制連動は次 PR で運用データ較正後に再判定。

## v5.23.0：E2E 構築 BP の体系化・AI 駆動 E2E の在り方 (in progress)

L0 起動（メタスキル開発）。「E2E を DH の文脈で体系化して取り入れたい」を起点に、人間（ひでさん）との
ブレストで **AI 駆動開発における E2E の真の在り方**を言語化した。人間開発の BP（テストピラミッド等）は
「書く=高 / 回す=安」という人間前提に立つが、AI 駆動ではこの前提が崩れる。

### 設計意図の核

**(a) E2E = AI の知覚器官**: 人間 dev は実行中アプリを目で見て手で触るが AI にはその経路が無い。
E2E + artifact + Vision が AI の唯一の現実接地チャネル。ゆえに **AI は「見ると宣言したものしか見えない」**、
AI の知覚は「何を検証するか」宣言の精度に律速される。これが後述 C5 を哲学の本丸にする。

**(b) 二相分離（一次概念）**: 相 A（in-loop 知覚器・自己修正用・使い捨て可）/ 相 B（SPEC 由来の耐久資産・
回帰契約）。人間の「テスト=記憶代替」に対し、DH では次エージェントが SPEC+history から文脈を再構成するため
耐久テストの役割は「SPEC とコードの実行可能契約」＝ drift の runtime 補完へシフトする。

**(c) C5 テスト oracle 言語化（人間が最重要と判断）**: 人間の暗黙の関心（何を気にするか/なぜ作るか/
暗黙前提）を言語化すること = AI の知覚宣言を拡張すること = AI の知覚野を広げること。第4条（人間=意図共有/
AI=構造化）・第1条（認識ズレゼロ化ループ）をテスト設計に適用したもの。SKILL.md §2.6 に昇格。

**(d) AI テスト精度問題と自己言及の罠**: AI は低信号テストを過剰生成しうる/間違ったものを検証しうる。
根に「実装した AI が・テストを書き・自分で通ったと判定する」自己言及の罠（第3条 独立性で隔離）。
対策 C1（SPEC 由来母集団）/ C2（生成と判定の隔離）/ C3（本数天井）/ C5（L0 で人間と大枠合意）。

**(e) browser provenance pinning**: 「どの browser が開くか」のばらつき（CC コンテナ vs ローカル実 Chrome
vs CI）は AI の知覚器官そのもののばらつき＝ flaky 源・観測性統一（第6条）の侵食。「借りない・固定する・
記録する」で統一。カノニカルエンジン = 同梱 chromium 単一既定、webkit/firefox は SPEC 宣言時のみ opt-in。

### 温存（minority opinion・将来 PR 再判定）

- **テスト情報代謝**: 相 A を cycle 後に COLD 退避/削除し相 B を結晶化する「テスト版 HOT/WARM/COLD」。
  情報代謝の射程にテストを含める新しい一歩だが、本導入自体が試験的なため実 E2E 運用データが貯まるまで温存。
- **flaky→circuit-breaker/P4 の強制接続**: 本 PR では「接続地図」のみ明記、強制連動は次 PR。
- **mutation メタテスト（C4）**: AI テスト精度を変異注入で測る。重いため温存。

## v5.23.0：UI Baseline RL（相互作用層）の取り込み (in progress)

利用者（ひでさん）提供の UIUX 研究 2 ファイルを DH に統合。同一 PR の E2E/C5 と「B-ID = oracle」で接続する。

### 設計意図の核

**(a) DESIGN.md の空白を埋める**: 既存の DESIGN.md は「視覚トークン層（色/font/余白＝どう見えるか）」のみを
担い、「相互作用層（signifier/認知負荷/feedback/操作機構/a11y＝どう知覚・操作されるか）」が空白だった。
design-system-spec.md 自身が「token 静的検査だけで UX は保証できない」と認め、DONT.md は「創造的 UX を
AI に任せない」と禁止していた。UI Baseline RL は **枯れた UX 法則に立脚した機械可読 RL** でこの空白を埋め、
「AI に任せない」を「AI に枯れたルールブックを持たせる」へ前進させる。

**(b) 二層モデル + 目的特化**: 視覚トークン層（DESIGN.md・プロジェクト固有）× 相互作用層（基底 = B-01〜
B-25 常時適用 / 特化 = S-01〜S-06 目的別）。基底は目的非依存の最低保証、特化は画面単位で 1 目的を選び
上乗せ。安全境界（各 S の「緩めてはならない」＋ a11y floor B-22〜B-25）は目的に関わらず侵食不可。

**(c) B-ID = ready-made oracle（E2E/C5 との接続）**: B-ID は抽象的な「使える」を検証可能な宣言に落とした
もの。これは同 PR (1) の C5「AI は見ると宣言したものしか見えない」と同型で、B-ID がそのまま 5 層検出
スタック（第1=静的/第2=E2E/第3=計測/第5=Vision）の oracle になる。UI プロジェクトの C5 対話は B-ID を
出発点に暗黙の関心を言語化できる。これが 2 テーマを 1 PR にバンドルした理由。

**(d) S-xx 選択は質問を増やさない**: DG2/3（ブランド・参考）・UX 3問（主要ユーザー・Must 閾値）・NFR から
主目的を AI が推定し S-01〜S-06 に対応づける（フラクタル原則：対話で確定、新規質問は増やさない）。

### 配置と provenance

- 配置: `templates/rules/common/`（言語横断 RL、agentshield と同列）。利用者プロジェクトへ deploy される
  ため、テンプレ自体は self-contained に保ち、DH 配線説明は skill reference 側（design-system-spec.md）に集約。
- ORIGIN: external（利用者提供）。各ファイル冒頭の blockquote に明示。`.dh/rules/` で override 可能。

### 温存（倫理境界）

- **S-05 の dark pattern 禁止・ユーザー制御権**は Baseline を超える倫理境界として明記温存。anticipatory/
  persuasive 設計は理論先行で失敗例も多く、先回り過剰はエージェンシーを損なう。philosophy 第 6 条
  「人間最終承認・人間 ≒ Council」と整合させ、行動変容系 UI でも中断・解除・拒否の容易性を健全性指標に置く。
- **言語別 UI rule（`<lang>/`）への展開**は現状不要（UI 相互作用は言語横断）。必要が生じたら README の
  override 規約に従い追加。

## v5.9.0 候補：auto-merge 人間承認モデルの opt-in→opt-out 反転 (in progress)

PR #33 が 4 日間放置されている事例を起点に、auto-merge の人間承認モデル（v5.5.3 で導入された label opt-in モデル）を opt-out モデルに反転する設計判断。Council 諮問 `council-2026-05-06T08:30:00Z-amrev1`（business / category=conception / phase_3 / unanimous / judgment_confidence=0.80）で **C ハイブリッド採用** が weighted_score 7.31（全 weight 11、100%）で全会一致。

### 設計意図の核

**(a) opt-out 反転の根拠**: 人間（ひでさん）の発言「人間は多少のことは無関心なので基本オートでよい。対話の中でタグ付けするかどうかを重要度によって聞くようにして、基本は暗黙的にオートである」を起点とする流速最適化。opt-in モデルでは PR #33 のように人間が `auto-merge` ラベル付与を忘れて PR が滞留する事例を構造的に許容していた。opt-out モデルでは沈黙が暗黙承認となり流速が劇的改善する。

**(b) C ハイブリッド採用（A 全面 opt-out でも B 維持でもない）**: philosophy/harness-verifier/cross-cutting/不可逆領域は opt-in 維持（人間の能動的同意が必要）、定型領域のみ opt-out。哲学者の懸念「opt-in が体現していた『同意の能動性』が opt-out で失われる」「5 年スパンで『無関心 = 委譲』が『無関心 = 思考停止』に滑落する重力」を「境界を SPEC で不変化することで止揚」する。

**(c) 4 実装要件（minority_opinion 由来）**:

| # | 要件 | 実装 |
|---|------|------|
| 1 | 境界の SPEC 不変化 | `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md` を一次情報源化、AI が境界を動かせない |
| 2 | roll-back プロトコル | 6 ヶ月後評価ゲート（2026-11-06）、評価指標 4 項目（暗黙 merge 事故 / AI 判定漏れ率 5% 超 / 境界曖昧化 月 2 件 / 二重ラベル腐敗）で 1 件でも閾値超過なら opt-in 復帰 |
| 3 | 既存 `auto-merge` ラベル廃止 | 二重ラベル方式の腐敗回避、deployment では作成しない、issue-pickup 自動付与削除 |
| 4 | メタ承認機構 | PR1 placeholder 実装（手動運用）、月次「AI 判定漏れ率」5% 超で roll-back ゲート起動 |

**(d) opt-in 領域 8 項目**: philosophy 改修 / harness-verifier 自己改修 / 不可逆操作 / DONT.md 抵触 / Council `judgment_confidence < 0.5` / 複数 SPEC 横断改修（3 ファイル以上）/ autonomous-drive workflow 自身の改修 / 境界 SPEC 自身の改修（メタ自己参照）。

**(e) opt-out 領域**: 単一機能追加 / bug fix / typo 修正 / format 修正 / documentation 更新（history/, delivery/）/ 単一 skill SPEC 追記（1 ファイル内）/ リファクタ（動作不変）/ monthly report 自動生成。

**(f) Council 入力構造の自己参照**: 本判定自体が「philosophy 改修を伴う conception カテゴリ」であり、哲学者 weight が最大（5/11）の状況で「自己の権限縮退を自己決定する構造」の倫理的捻れを抱える。哲学者は confidence 0.55 で他ペルソナより低めだが C ハイブリッドに収束、minority_opinion で「沈黙が承認に化ける制度設計が招く認知負債」「P4 介入権の事後発動による質的劣化」を指摘し、これらを 4 実装要件として SPEC に同梱することで止揚した。

### roll-back 評価ゲート（2026-11-06）

| 評価指標 | 閾値 | 出典 |
|----------|------|------|
| 暗黙 merge 事故件数 | 1 件以上で要再評価 | 哲学者懸念 |
| AI 判定漏れ率 | 5% 超で要再評価 | メタ承認機構 |
| 境界曖昧化事例 | 月 2 件以上で要再評価 | 経営者懸念 |
| 二重ラベル腐敗 | 1 件で即 roll-back | 開発者懸念 |

評価指標すべて閾値未満なら継続、1 年後（2027-05-06）に再評価ゲート。

### 関連

- Council: `council-2026-05-06T08:30:00Z-amrev1` (history/COUNCIL-LOG.md)
- 境界 SPEC: `.claude/skills/crosscut-autonomous-drive/references/auto-merge-boundary.md`
- 起点事例: PR #33（4 日間放置の docs/brainstorm draft PR）
- 影響範囲: `.github/workflows/auto-merge.yml` + template / `.github/workflows/issue-pickup.yml` + template / `crosscut-autonomous-drive` SKILL.md / `crosscut-issue-implementer` SKILL.md / `layer1-autonomous-dev` SKILL.md §7.5 / `philosophy.md` 第 7 条

## v5.8.x / v5.9.0 候補：cookpato retro A1〜A5 取り込みポートフォリオ (discussion 段階)

cookpato（妻専用献立メモ PWA、`samejima-ai/cookpato`）のバックアップ機能サイクル振り返り（PR #22、`docs/retros/2026-05-05-backup-cycle.md`）から DH 本体取り込み候補 5 件 (A1〜A5) を抽出。Council 諮問 `council-2026-05-06T04:42:00Z-a5port` (business / category=judgment / phase_3 / simple_conflict / judgment_confidence=0.75) で **案A (採用案維持)** が weighted_score 6.20 で支配的採用。

### 設計意図の核

**(a) 案A 採用ポートフォリオ振り分け** (最終確定):

| 提案 | 取り込み先 | Issue/PR | バージョン |
|---|---|---|---|
| A1 事故起点プローブ | `dialog-questions.md` | #53 (A1 単独に書き換え済) | v5.8.1 patch or v5.9.0 minor |
| A2 機能間相互作用セクション | `meta-spec-template.md` | #57 (新規作成) | v5.9.0 minor |
| A3 R+1 オーバーライド | #46 軸 vi 観測性データソース拡張 | #46 (closed) へ follow-up コメント + 別 issue | v5.8.x patch or v5.9.0 minor |
| A4 L1 依存導入チェック | `layer1-autonomous-dev/SKILL.md` | #55 / PR #56 (CI PASS、draft) | v5.8.1 patch |
| A5 grep 規約センサー | `dev-env-spec.md` パターン例 | #54 (A5 単独に書き換え済) | v5.9.0 minor |

**(b) 哲学者少数意見の v6.0.0 候補温存** (Council third_way_excluded で保持): 哲学者ペルソナは「**A1 と A3 はともに『沈黙する前提の言語化』カテゴリで同型**」(対象がユーザー記憶 vs プロジェクト履歴と異なるだけ) と指摘し、規則化の前に **philosophy.md 第 8 条候補 (v6.0.0)** として「**事故履歴という外部記憶への harness 依存**」を昇格すべきと主張。N=1 問題 (cookpato 単一事例から普遍規則を抽出する帰納的飛躍) への対処として、**2 件目 retro 出現時に再評価ゲート** を設ける。

**(c) Council context 誤情報の事後訂正記録** (情報純度違反、philosophy.md §3): 諮問時 context に「v5.8.0 候補 = #46 (discussion 中、未着手)」と記述したが実際は **v5.8.0 既リリース (2026-05-04)、#46 closed**。判定 (案A) は前提変更後も妥当性を保つためバージョン表記のみ訂正、案A 維持。本訂正経緯は `COUNCIL-LOG` の `modification_note` に記録。

**(d) F2 重複候補 3 件の整理**:
- A1 ↔ `ritual-protocol.md` F2 認識ズレ検出: cookpato 事故は過去 INTENT 空のため F2 では拾えなかった → A1 はその穴埋めとして設計
- A3 ↔ #46 Quality Gate 軸 vi 観測性: SSOT 維持のため #46 follow-up に統合 (二重化回避)
- A5 ↔ `crosscut-verifier-drift`: 対象差異 (SPEC↔実装 vs CLAUDE.md規約↔実装) で補強カテゴリとして相補

**(e) A1 実装時の哲学者フォロー脚注**: A1 を `dialog-questions.md` に追加する際、A1/A3 同型カテゴリ (沈黙前提の言語化) を明示的に脚注化し、第 8 条昇格議論への伏線とする (詳細は #53 issue body)。

### v6.0.0 候補温存

「**事故履歴という外部記憶への harness 依存を philosophy.md 第 8 条として昇格するか**」を哲学者第3の道として保持。2 件目 retro 出現時 (or v5.9.x マイナー安定後) に再評価ゲートで本格検討する。

### 関連

- 起点 retro: `samejima-ai/cookpato` PR #22 `docs/retros/2026-05-05-backup-cycle.md`
- Issues: #53 (A1) / #54 (A5) / #55 (A4) / #57 (A2) / #46 (A3 follow-up コメント)
- PR: #56 (A4 実装中、CI PASS、draft)
- Council: `council-2026-05-06T04:42:00Z-a5port` (history/COUNCIL-LOG.md)

## Issue #70（Seam 監査センサー）観測温存 (2026-05-09)

`samejima-ai/kakuman-platform-v3.0` 単一事例（N=1）を起点とした「Architectural Fitness Function / Seam 監査センサー」（条件発動型）の L0 spec-architect 取り込み提案。本提案は **観測温存** とし、autonomous-drive の即時 implementation 経路には載せない。

### 温存判断の根拠

**(a) N=1 帰納的飛躍リスク**: cookpato A1/A3 と同型の N=1 問題（単一プロジェクト事例から普遍規則を抽出する帰納的飛躍）。ただし Architectural Fitness Function (Neal Ford) と Seam (Michael Feathers) は業界で確立した概念であるため、cookpato 提案より「沈黙する前提の言語化」の未踏度は低い。

**(b) 過剰設計誘発リスク**: 監査観点 5 項目（データ取得層集約 / 整形変換分離 / 設定外出し / エラー共通化 / キャッシュ差し込み点明示）を無条件適用すると YAGNI / Premature Abstraction を誘発するため、条件発動型の閾値設計（規模 S ≥ 5 + DB 前提 + 寿命 6 ヶ月超 = フル監査 / S ≤ 2 = スキップ等）が前提になる。閾値の妥当性検証には複数事例が必要。

**(c) スタック非依存性の実装難度**: Seam は実装言語・FW のイディオム依存度が高く（Next.js の `_lib/` 抽出 vs Rails の concern vs FastAPI の dependency injection）、観点をスタック非依存の抽象語で記述しつつ判定例を `REGIME.md` の `stack` に応じて差し替える設計が、テンプレ翻訳負債なしに到達できるか不明。

### 再評価ゲート（案 Y 採用）

**条件**: Lifecycle ≥ 1 のプロジェクトで Seam 退化（観点 1〜5 のいずれかが「コピペ増加」「Seam 破壊」として観測される）が **N=1 で再現** したら即再評価。

cookpato A1/A3 の「2 件目事例で再評価」（案 X）より緩和した条件を採用する根拠は、**Architectural Fitness Function / Seam が業界で確立した概念**であり「沈黙する前提の言語化」未踏領域カテゴリには該当しないため。Lifecycle ≥ 1 の退化検出は新規開発時の初期 Seam 設計よりも実需要シグナルとして強い。

### Council 諮問の不要性判定

`philosophy.md` §6「人間 ≒ Council」起動条件のいずれにも該当しない:

- 複数案拮抗なし（観測温存で一致）
- 不可逆操作なし（記録のみ、コード変更なし）
- SPEC 矛盾なし（既存 sensors 体系を変更しない）
- `judgment_confidence < 0.5` ではない

ゆえに本記録のみで処理（Council 諮問は不要）。

### 関連

- Issue: `samejima-ai/dialog-harness#70`（label `discussion` 付与、`ready-for-ai` 除去で autonomous-drive 経路から外す）
- 起票元: `samejima-ai/kakuman-platform-v3.0` 検証セッション
- 業界概念: Architectural Fitness Function (Neal Ford "Building Evolutionary Architectures") / Seam (Michael Feathers "Working Effectively with Legacy Code")
- 関連 sensors: `crosscut-verifier-drift`（SPEC↔実装乖離、責務境界の差別化が再評価時論点）/ `inferential.md`（仕様合致、責務分離が再評価時論点）

## v5.7.2 で追加された概念

### `claude-code-action@v0` の OIDC permission bug 修正

v5.7.1 で `gemini-cli` → `Claude Code CLI` に実装エージェントを切り替えた際、`anthropics/claude-code-action@v0` が要求する `id-token: write` permission を `issue-pickup.yml` に追加し忘れていた single-line bug。Issue #46 の autonomous-drive 起動で初の本番テストとなり顕在化。

#### 設計意図の核

**(a) 観測駆動の bug 検出**: v5.7.1 merge 時点では実装本体（`claude-code-action`）の本番テストが行われておらず、bug が潜在化。Issue #46 が初のトリガー。「観測駆動原則」が実証された事例として記録（philosophy.md §1 フラクタル原則 + §3 情報純度の応用）。

**(b) 自明な single-line fix**: 修正は workflow `permissions:` ブロックに `id-token: write` 1 行追加のみ。複数案拮抗なし、不可逆操作なし、SPEC 矛盾なし → Council 諮問は不要（philosophy.md §6「人間 ≒ Council」起動条件のいずれにも該当せず）。

**(c) v5.7.1 release 化を同梱**: 本 patch は v5.7.1 の bug 修正であり、merge と同時に v5.7.1 (in progress) → (released 2026-05-03) 化を housekeeping として同梱（**8 例目正規適用**）。

**(d) Issue Quality Gate との連動**: Issue #46（v5.8.0 候補 `crosscut-issue-quality-gate`）の autonomous-drive 完遂を本 patch の動作検証として兼ねる。Quality Gate 完成後に「v5.7.1 release 時に本 bug を事前検知できなかった理由」を遡及採点する材料として記録（軸 viii テスト粒度・本番前テスト粒度の改善案件）。

**(e) 後方互換完全維持**: permission 追加は既存挙動に影響しない（既存 workflow が要求しない権限を増やすだけ）。利用者プロジェクトへの強制配布なし。

#### 改修内容

- `.github/workflows/issue-pickup.yml` 1 行追加
- `templates/github-workflows/issue-pickup.yml.template` 1 行追加
- 履歴層 4 ファイル更新（CHANGELOG / INTENT / REGIME-LOG / ARCH-DECISIONS AD-030）

#### 温存項目（v5.7.x / v5.8.0 候補）

- **本番前テスト粒度の規格化**: Issue #46 完了後、Issue Quality Gate 軸 viii の合格基準として「本番前テストで `claude-code-action` を含む全 step を smoke test する手順」を加える検討
- **claude-code-action SHA pin**: v5.7.1 で温存中、v5.7.x で観測駆動判断
- **gemini-cli 自動フォールバック**: 同上、観測駆動判断

## v5.7.1 で追加された概念

### 実装エージェント方式の見直し（Claude Code CLI メイン化、AD-026 訂正）

ユーザー要請「実装は Claude Code CLI で、サブスクで稼働、Gemini はフォールバック」を起源として、v5.7.0 AD-026 (gemini-cli 採用) の判断見直しを実施する patch リリース。

#### 設計意図の核

**(a) 新事実発見による前提変化**: v5.7.0 当時「Anthropic API 回避」のために gemini-cli を採用したが、Anthropic Pro/Max サブスクリプション + `CLAUDE_CODE_OAUTH_TOKEN` 経由で Claude Code CLI を **追加 API 課金なし** で GitHub Actions で稼働可能と判明。前提変化により最良案が gemini-cli → Claude Code CLI に移行。

**(b) AD-026 historical 維持での訂正記録**: AD-026 は削除せず、AD-029 で「v5.7.0 当時の判断、新事実発見で v5.7.1 で訂正」と historical 記録維持。philosophy.md 第 5 条「献上哲学」のタイプ C（仕様改訂提案）の audit trail を尊重。

**(c) gemini-cli の継続用途明確化**: 完全切替ではなく役割分担：
- AI triage（Issue 内容判定）: gemini-cli **メイン継続**（軽量、無料 tier 余裕）
- 実装本体（コード生成、PR 作成）: Claude Code CLI **メイン**、gemini-cli **フォールバック**
- PR レビュー (gemini-review.yml): gemini-cli **メイン継続**（変更なし）
これにより gemini と Claude の異質モデル併走（philosophy.md §3 情報純度）が維持される。

**(d) フォールバック発動は人間 P4 判断**: Claude Code action 失敗時に gemini-cli への自動フォールバックは実装しない。label `pickup-failed` 付与 + notice 通知 → 人間 P4 が判断（gemini で再 trigger or 別アプローチ or 一時停止）。philosophy.md 第 4 条「人間が判断する場面」+ 第 7 条 P4「暴走時介入」と整合。

**(e) 後方互換完全維持**: philosophy.md 改訂なし、既存 SKILL.md セクション番号不変、利用者プロジェクトへの強制配布なし。v5.7.0 で deploy 済の利用者プロジェクトは旧 issue-pickup.yml (gemini-cli 前提) のまま動作可、新規 deploy で Claude Code CLI 経路採用。

#### 改修内容

- `crosscut-issue-implementer/SKILL.md` 改訂（実装エージェント記述更新）
- `references/triage-protocol.md` 軽微改訂（triage は gemini 維持を明文化）
- `references/setup-checklist.md` `CLAUDE_CODE_OAUTH_TOKEN` 取得手順追加
- `.github/workflows/issue-pickup.yml` claude-code-action 統合
- `templates/github-workflows/issue-pickup.yml.template` 同等改訂
- 履歴層 4 ファイル (CHANGELOG / INTENT / REGIME-LOG / ARCH-DECISIONS AD-029)

#### v5.7.x / v5.8.0 候補として温存

- 実装本体の MVP → 完全実装（branch / clone / 実装 / commit / PR 作成）。v5.7.0 で MVP 投入、v5.7.1 で action 切替、次の v5.7.x で完全実装する 3 段階設計
- gemini-cli 自動フォールバックの導入判断（observation で fail パターン蓄積後）
- claude-code-action SHA pin（supply-chain hardening、v5.7.x で対応）
- 既存 v5.7.0 deploy プロジェクトの migration ガイド（v5.8.0 で template + 手順整備）

## v5.7.0 で追加された概念

### autonomous-drive 入口側本格稼働 + Issue 選別機構

ユーザー（ひでさん）の根源要請「Bを考えよう」+ 「Issue 選択は開発品質を決めると言って過言ではない」を起源として、v5.6.0 で温存された「パス B（crosscut-issue-implementer workflow 実装）」を本格仕様化する minor リリース。L0 spec-architect セッションで策定された HANDOFF (`delivery/HANDOFF-v5.7.0-issue-pickup.md`) に従い L1 autonomous-dev で実装。

#### 設計意図の核

**(a) gemini-cli 流用による Anthropic API 回避**: ユーザー要望「自前開発で低コスト、API 課金避けたい」を満たすため、既存 GEMINI_API_KEY を実装エージェント用途に転用。追加コスト 0、ただし PR レビューから「実装」への拡張は未踏領域で品質懸念あり。Council 起動可能性を保留しつつ観測駆動で運用判断。

**(b) Issue 選別 3 段階フィルター**: 「全 Issue を picking up」は NG（ユーザー明示）。
- 一次: label `ready-for-ai` opt-in（人間 P2 の明示 GO サイン）
- 二次: author allowlist + 本文必須項目（再現手順 / 期待動作 / 受入条件）
- 三次: AI triage（gemini-cli が Issue 内容を読んで pickup 可否判定、SPEC/DONT/current_focus と照合）
philosophy 第 3 条情報純度 + 第 7 条 P2 ブレスト責務との整合。

**(c) current_focus 軸新設による開発集中の保護**: 「master のバグ修正中なら新機能 Issue を pickup しない」(ユーザー観点) を機械可読化。REGIME.md `current_focus` フィールド (type / target / since / priority) で表現、β 半自動更新（spec-architect 対話）+ γ ブランチ命名フォールバック（fix/* feat/* refactor/*）。philosophy 第 4 条「モード判定は L0」と整合（自動推論ではなく対話で更新）。

**(d) Circuit Breaker による経済的暴走防止 (P4 機構)**: 日次 5 / 月次 50 Issue 上限を workflow に hardcode、上限到達で workflow 全停止 + label `circuit-broken` 付与 + notice 通知。GEMINI_API_KEY は無料 tier で API 課金は発生しないが、Issue 多発時の rate limit 圧迫を防ぐ。philosophy 第 7 条 P4「暴走時介入」の AI 兆候提示の実装。

**(e) bootstrap パターン**: v5.7.0 自身は手動セッションで実装（L0 → HANDOFF → L1 → PR）。merge 後に dialog-harness 自身に issue-pickup.yml がデプロイされ、v5.7.x 以降の DH 開発は「Issue → 自動実装 → 自動 merge」のフル自律 loop へ移行する。これがユーザー指摘「対話 → Issue → 自動実装」のパターン実装。

**(f) 後方互換完全維持**: dev_mode `autonomous` + `autonomous_scope: full` 以外では本機構は起動しない。利用者プロジェクトへの強制配布なし（template 配置のみ、起動は spec-architect 対話で確認）。

#### 改修内容

- `spec-architect/SKILL.md` 等 4 ファイル: current_focus 軸追加（β 半自動 + γ フォールバック）
- `crosscut-issue-implementer/SKILL.md` 全面改訂 + references 3 件新設（issue-filter / triage / circuit-breaker）
- `.github/workflows/issue-pickup.yml` 新設（dialog-harness 自身に deploy）
- `templates/github-workflows/issue-pickup.yml.template` 新設（利用者展開用）
- `harness-verifier/glossary.yml` 新用語追加 (`current_focus`, `triage`, `circuit_breaker`, `pickup`, `release`)

#### Person 責務 (P1〜P4) との対応強化

| 段階 | 主体 | 行為 |
|---|---|---|
| Issue 着想 | 人間 P1 | 発案（思考） |
| Issue 化 | AI (P2 補助) | 対話で具体化 → AI が Issue 作成 |
| 一次 GO サイン | 人間 P2 | label `ready-for-ai` 付与（発話レベル） |
| 二次選別 | AI (issue-implementer) | filter + AI triage |
| 実装 | AI (gemini-cli) | branch 作成 + 実装 + PR |
| レビュー | AI (gemini-review + Copilot) | 多層 critic |
| Merge | AI (auto-merge) | 自動 |
| 事後評価 | 人間 P3 | 振り返り |
| 暴走介入 | 人間 P4 | `do-not-merge` / `circuit-broken` 解除 |

人間関与は P1〜P4 の 4 場面に集約（philosophy 第 7 条と整合）、AI が手を動かす全工程を自動化。

#### v5.7.x / v6.0.0 候補として温存

- gemini-cli 実装エージェントの品質観測 → fail 率測定で必要なら Council 起動でフォールバック判断（ローカル Claude / Copilot Workspace / 一時的 Anthropic API）
- 新 sub-skill `crosscut-issue-drafter`（ブレスト → Issue 化支援、philosophy 第 7 条 P2 強化）
- destructive change detector / circuit breaker の実機構（v5.6.0 から累計後送中）
- ALLOWED_AUTHORS 動的化（複数 contributor 体制で必要時）
- adrv01-Ph2（独立観測機構）— 第 7 条 + Issue 選別機構の運用観測データを蓄積
- crosscut-verifier-philosophy 本実装

## v5.6.0 で追加された概念

### autonomous-drive 標準化 + DH AI 組織論明文化（メタスキル開発）

ユーザー（ひでさん）の根源要請「自律駆動を L0 に記録、メタスキル開発」と「DH AI 組織は L0 設計 / L1 実装 / L2 統括 / Council 判断 の 4 役割属性 + サポート だけで、あらゆる開発に対応できる」の宣言を制度化する minor リリース。L0 spec-architect セッションで策定された HANDOFF（`delivery/HANDOFF-v5.6.0-autonomous-drive.md`）に従い L1 autonomous-dev で実装。

#### 設計意図の核

**(a) DH AI 組織論の明文化（philosophy.md 第 7 条新設）**: 4 役割属性（L0/L1/L2/Council）+ サポート（crosscut-* 非 council 系 + sub-agent）の構造を philosophy.md の正式条として制度化。L3 運用層を新設しない原則（第 1 条フラクタル）と整合し、運用インシデントは L0 へ還元する設計を明示する。第 6 条 H カテゴリ（判断種別）と第 7 条 P カテゴリ（責務種別）は直交 2 軸として整理。HANDOFF で「H1〜H4」と仮ラベル化されていた人間 4 責務は philosophy 第 6 条 H カテゴリとの番号衝突を避けるため `P1〜P4` にリネーム（実装者裁量、Council 起動の閾値未満）。

**(b) autonomous-drive 機構の標準化**: v5.5.3 で dialog-harness 自身に実装した autonomous-drive 機構（gemini-review.yml + auto-merge.yml）を template 化し、利用者プロジェクトに展開可能にする。`templates/github-workflows/` に placeholder 化テンプレートを配置、`crosscut-autonomous-drive` skill が deployment ロジックを担う（β 止揚採用、Council `adrv02`）。

**(c) `autonomous_scope` 軸の正式定義**: dev_mode `autonomous`（v5.0.0 で列挙のみ）に対して `autonomous_scope`（full / merge_gated / custom）を細分化軸として追加。デフォルト = full（人間 = P1〜P4 のみ、AI = Issue 精査〜次 Issue 着手まで完全自走）。

**(d) Council β 止揚採用（adrv02）**: skill 新設の可否について Council 諮問を実施。経営者（案 A 推奨）/ 開発者（案 B 寄り）/ 哲学者（案 A + 第 3 の道）の対立を「deployment skill のみ新設、guardian は v5.6.x patch で観測駆動追加」で β 止揚。`agreed_with_modification` で確定。

**(e) 観測駆動原則の緩和（F2 即着手判断）**: v5.5.3 AD-022 の「数 PR 試運用後にパス B 移行」原則は、本日 PR #42 自動 merge の 1 例のみで標準化要請に踏み切った。理由: メタスキル開発は単一プロジェクトでの試運用観測より、複数プロジェクトへの展開可能性確保が先決。観測は v5.6.x patch で並行継続。

**(f) フラクタル原則 (第 1 条) との整合**: 4 役割 + サポート構造は L3 運用層新設を伴わず、第 1 条と整合する。サポート skill は単独で完結せず必ず 4 役割のいずれかから呼ばれるため、判断機能や責務階層を持たない。

**(g) 後方互換完全維持**: philosophy.md 既存 6 条改訂なし、既存 spec-architect 対話フロー不変、利用者プロジェクトへの強制配布なし、autonomous-drive 機構は dev_mode `autonomous` 選択時のみ opt-in。

#### 改修内容

- `philosophy.md` 第 7 条新設（既存 6 条不変、新規追加のみ）
- `spec-architect/SKILL.md` + 4 references + 1 asset の `dev_mode autonomous` / `autonomous_scope` / Level C 追加
- `templates/github-workflows/` 配置 + `crosscut-autonomous-drive` skill 新設
- 履歴層 5 ファイル更新

#### Person 責務（P1〜P4）と第 6 条 H カテゴリの関係

| 軸 | 第 6 条 H | 第 7 条 P |
|---|---|---|
| 分類対象 | 判断種別 | 責務種別 |
| 例 | H3 方向性発案（哲学変更等の判断） | P1 発案（プロジェクト方向性のアイデア提示） |

両軸は直交補完。H は「判断境界」、P は「行為境界」。両軸とも 4 区分は DH の現在規模で適切（汎化性主張の実 N 観測は v5.6.x 候補）。

#### v5.6.x / v6.0.0 候補として温存

- destructive change detector（diff threshold / DELETE-heavy detect、観測駆動で追加判断）
- circuit breaker（5 連続 fail 自動停止）
- ALLOWED_AUTHORS 動的化（複数 contributor 体制で必要時）
- adrv01-Ph2（独立観測機構、harness-verifier 同型 crosscut skill）— 第 7 条で組織論が確定したので連動して本実装可能
- crosscut-verifier-philosophy 本実装（v5.0.0 から累計後送中、第 7 条 + 既存 6 条で 7 本柱整合検証として再構成可能）
- DH AI 組織論の汎化性主張テスト（4 役割で実 N=3 別プロジェクトをカバーできるか観測）

## 保留中の長期計画

### CI/CD 強化計画（2026-05-01 開始、保留中）

- **起源**: 下流プロジェクト（Next.js + Supabase 系、`apps/platform` 等を持つ dev_mode=github_assisted 確定済プロジェクト）からの献上ブレスト
- **保管場所**: `history/deliveries/2026-05-01-cicd-automation-brainstorm.md`
- **DH 一般化候補**: 10 カテゴリ × 多数選択肢のうち、DH 本体に一般化可能な議題を以下 5 つに集約
  1. **scaffold-checklist の CI 章追加**: `.github/workflows/ci.yml` 雛形（typecheck + lint + test の PR ゲート）を v5.1.0 標準 stack の必須生成ファイルに加える案
  2. **crosscut-* 段階稼働プロトコル**: 未稼働の dispatcher / implementer / drift / feedback-loop について dev_mode × CTL ごとの推奨稼働順を reference 化する案
  3. **「罠 → 検出器」一般化パターン**: プロジェクト固有の踏みやすい誤りを DONT.md に言語化し sensors/computational.md へ lint として載せる汎用フローを reference 化する案
  4. **自動化 LOC 予算ガイダンス**: 1 自動化 = 1 ファイル 200 行未満、自動化総量の本体 LOC × 1.5 上限等のガイダンスを philosophy or dev-env-spec に追加する案（Bus factor 軽減）
  5. **sensor 自動実行化**: markdown 手順書としての sensor を実行可能スクリプト化し VERIFICATION.md に machine-readable 結果を残す案
- **未消化の 7 質問（ブレスト原文 §5）**:
  - Q1 テストフレームワーク方針（Vitest / Playwright / Cucumber の 3 層採否）
  - Q2 自動化 LOC 上限の基準
  - Q3 crosscut-* 稼働順序
  - Q4 罠検出器の SPEC / docs / DONT 振り分け
  - Q5 production 切替と down migration（プロジェクト固有、DH 採用外）
  - Q6 Bus factor 対策と自動化増加の逆説
  - Q7 v5.2.0/v5.3.0 で送られた philosophy verifier の取り扱い（既決：v5.3.0 候補から外し継続検討）
- **保留理由**: 起点プロジェクトおよび harness 利用者側で「CI/CD で何のどこをチェックするか」の認識共有が未達。L0 spec-architect 原則「認識のズレがゼロになるまでレビューループを回す」に従い、ズレが残ったままの開発環境構築を避ける
- **次サイクル発動条件**:
  - (a) 利用者プロジェクト側で CI/CD の対象範囲（typecheck / lint / unit / E2E / drift / 罠検出 のいずれか以上）を具体化した HANDOFF が届く、または
  - (b) PR #30（v5.4.0 archeo-architect）merge 後の安定期に DH 本体側でドッグフード対象として再起動
- **PR #30 との関係**: 本計画は PR #30 と独立。両者ともに `history/INTENT.md` と他ファイルを触る場合は merge 後 rebase で整合させる。本サイクルでは PR #30 が予約した v5.4.0 を侵さないため版上げを行わない
- **当面のリリース対象**: なし（記録のみ）。実体改修は次サイクル以降の minor or 別 PR に委ねる

### Lifecycle → LC 命名変更（2026-05-01、✅ 完了）

> **完了サマリ（2026-05-01 追記）**: 本計画は branch `claude/rename-lifecycle-to-lc-2026-05-01` で実施。`crosscut-council` 諮問の結果「PR #30 open のまま並列実行・衝突は rebase で解消」という判定で進行を確定（`history/COUNCIL-LOG.md` 参照）。具体的な実施内容は本節末尾「実施記録」を参照。

#### 元計画（2026-05-01 起稿時、保留中状態の記録）

- **起源**: 2026-05-01 サイクル中の対話（PR #31 上で CI/CD 動的調整を議論する過程で表面化）
- **問題**: DH 本体に 2 種類の `L` + 数字命名が共存し、文書内で衝突する
  - **Layer**: 5 層論の階層（L0 = spec-architect, L1 = autonomous-dev, L2 = orchestrator/integration-verifier）
  - **Lifecycle**: プロジェクトの成熟度（L=0 立ち上げ、L=1 機能拡張期、L=2 安定運用期、L=3+ 本番）
- **混同の実例**: 「L=2 のプロジェクトで L2 が起動する」のような文に Layer 2 起動条件と Lifecycle 2 が同時に登場し、読み手が文脈で判別する負担が生じる
- **改名提案**: `Lifecycle L=N` → `LC=N`（`LC` = LifeCycle 略記）
  - Layer は `L0/L1/L2` のまま維持
  - Lifecycle は `LC=0/LC=1/LC=2/LC=3` に統一
- **影響範囲（暫定推定）**:
  - `philosophy.md` Lifecycle 言及箇所
  - `references/regime-assessment.md` Lifecycle 判定章
  - `references/dev-env-spec.md` Lifecycle 別構成
  - 各 SKILL.md の振り返り儀式条件（特に `layer0-spec-architect/SKILL.md`）
  - `DIMENSIONS.md` Lifecycle 章（あれば）
  - `references/scaffold-checklist.md` Lifecycle 別生成物
- **保留理由**: 本 PR (#31) と並行 PR #30（v5.4.0 archeo-architect）はどちらも上記ファイル群の一部を触る、または触る可能性がある。命名変更は全 grep 系の横断改修であり、両 PR が merge される前に流すと conflict が大量発生する
- **次サイクル発動条件**:
  - (a) PR #30 merge **かつ** PR #31 merge の両方が完了し、master が安定状態になった後
  - (b) 命名変更を「`Lifecycle` → `LC` 一括置換 + 用語表更新 + 後方互換注記」に絞り込んだ単独 PR として独立ブランチで実施
- **PR スコープの予測**: 単独 PR、minor 昇格不要（命名整備のみ、機能変更なし）。CHANGELOG にメモ程度。
- **当面のリリース対象**: なし（記録のみ）

#### 実施記録（2026-05-01）

- **発動契機**: ひでさんからの「LC 命名変更に進む」指示。本来の発動条件 (a)「PR #30 merge **かつ** PR #31 merge の両方完了」のうち PR #30 が未 merge のため、`crosscut-council` を諮問した
- **Council 判定**: 経営者（条件付き進行）/ 開発者（段階的進行）/ 哲学者（条件記述更新後に進行）の 3 ペルソナで重み付き総合「進行可」判定。前提 3 条件を提示
  1. INTENT.md の発動条件記述を「並列実行・衝突は rebase で解消」に更新（**本節がこれに該当**）
  2. 衝突 4 ファイル（spec-architect SKILL / dev-env-spec / INTENT / CHANGELOG）は PR #30 で追加された新規行に触れず、既存 Lifecycle 言及行のみ置換
  3. 全置換完了後に harness-verifier を回し整合性を確認
- **置換規則**:
  - `Lifecycle L=N` → `LC=N`
  - `Lifecycle ≥ N` → `LC ≥ N`、`Lifecycle ≤ N` → `LC ≤ N`
  - `L=N`（単独で Lifecycle 文脈の場合）→ `LC=N`
  - `Lifecycle 0/1/2` → `LC=0/LC=1/LC=2`
  - `Lifecycle` 単独語（DH 概念として）→ `LC`
  - `Layer L0/L1/L2` は**変更しない**（5 層論用）
  - glossary.yml `lifecycle:` セクションのキー `L=0/1/2` → `LC=0/1/2`、aliases に旧表記を全て含める形で後方互換維持
- **触ったファイル群**:
  - `harness-verifier/glossary.yml`（キー rename + 後方互換 alias）
  - `.claude/skills/` 配下の markdown 群（sed による機械置換 + 残存の手動補正）
  - `history/INTENT.md`（本節の追記）
  - `history/CHANGELOG.md`（v5.3.x patch エントリ追加）
  - `history/REGIME-LOG.md`（本サイクル記録）
  - `history/COUNCIL-LOG.md`（本 Council 諮問記録）
- **触らなかったファイル群（後方互換のため）**:
  - `delivery/SELF-VERIFICATION-v5.0.0.md` 〜 `v5.2.0.md`、`L1-DELIVERY-v5.3.0.md`、`VERIFICATION*.md`（バージョン別スナップショット、歴史的記録）
  - `dh-upgrades/upgrade-spec-v5.0.0.md`（過去のアップグレード計画）
  - `docs/migration-guide-v5.1.0.md`（公開済み移行ガイド）
  - `history/CHANGELOG.md` の v5.0〜v5.3 既存エントリ、`REGIME-LOG.md` の既存エントリ、`ARCH-DECISIONS.md` の全エントリ（時系列ログの歴史的事実は不変）
- **PR #30 との衝突対処**: 本 PR は `layer0-spec-architect/SKILL.md` と `dev-env-spec.md` を **置換のみ**（新規行追加なし）。PR #30 はこれらに新規行追加（archeo-architect 行）。merge 順序が前後しても rebase で機械的に解決できる
- **バージョン**: 据え置き（v5.3.0 のまま）。命名整備のみ、機能変更なし
- **検証**: `harness-verifier/verify.py` を実行し全項目 PASS を確認（実行記録は `delivery/` 配下ではなく本節に簡記）

### scaffold-checklist CI 章 構造ドラフト（2026-05-01 起稿、保留中）

CI/CD 強化計画 (1) の解像度を上げる**構造案**。`references/scaffold-checklist.md` への実装はまだ行わず、ここに叩き台として保管する。本節以降は LC 命名変更計画（前節）の決定に従い `LC=N` 表記を先行採用する。

#### 設計原則

1. **L0 は型と最小実装を渡す**: `.github/workflows/ci.yml` の最小 YAML を雛形として配布する。L1 が中身を埋める（テスト本体・キャッシュ最適化）
2. **動的判定**: CI 構成は `(LC, dev_mode, stack)` の関数として決まる。`dev_mode = local_only` では物理的に CI 不在
3. **三段構えの第 2 段専用**: 第 1 段（IDE / pre-commit）と第 3 段（AI reviewer）は別責務。CI 章は機械化可能なものだけを扱う
4. **scaffold-checklist の §0 受け入れ基準を継承**: 「実体ファイルが存在しなければならない」原則を CI YAML にも適用

#### 動的構成テーブル（dev_mode = `github_assisted` 以上）

| LC | 検査セット | 実体ファイル要件 | jobs 数 |
|---|---|---|---|
| `LC=0`（立ち上げ初期） | typecheck のみ（PR ゲートとせず通知のみ） | `.github/workflows/typecheck.yml`（最小 15 行） | 1 |
| `LC=1`（機能拡張期） | typecheck + lint + unit test（PR ゲート） | `.github/workflows/ci.yml`（30〜50 行） | 3 |
| `LC=2`（安定運用期） | + drift 検出 + 罠検出器 + E2E（夜間 schedule） | `.github/workflows/ci.yml` + `.github/workflows/nightly.yml` | 5+ |
| `LC=3+`（本番運用） | + security scan + perf budget + canary | 上記 + `.github/workflows/release.yml` | 8+ |

`dev_mode = local_only` では本テーブルは適用されず、代わりに `git hooks/pre-commit` のみ規定（別章として将来追加）。

#### LC=1 雛形（最低共通解の例示）

```yaml
# .github/workflows/ci.yml （L0 が配布する最小骨格）
name: CI
on:
  pull_request:
    branches: [master, main]
jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm typecheck
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm test
```

備考: scaffold-checklist v5.1.0 標準 stack の `package.json` `scripts.dev/build/test` 規約と整合する。`pnpm typecheck` `pnpm lint` の存在は同 stack で既に必須生成物に内包されているため追加要件なし。

#### スタック別差分（将来 minor で）

scaffold-checklist 既存の「将来拡張ポイント」表（Next.js / Vue 3 / Node CLI / Astro / SvelteKit）と並走して、各 stack の CI 雛形差分を minor で追加：

| stack | 主な差分 |
|---|---|
| Next.js (App Router) | `pnpm build` を job に追加（Edge runtime ビルド検証）、Vercel preview deploy 連携 |
| Vue 3 + Vite | Vue 系 lint plugin の有無、E2E は Cypress も選択肢 |
| Node CLI | jsdom 不要、`pnpm pack` の job 追加 |
| Astro | `astro check` の job、image optimization 検証 |
| SvelteKit | `svelte-check` の job、adapter-auto の build 検証 |

#### 振り返り儀式での連動

`spec-architect` の振り返り儀式（`ritual-protocol.md` 規定）に LC 遷移検出ステップを追加し、検出時に本ドラフトの動的構成テーブルと現行 `.github/workflows/` を diff して人間に提示する流れを構築する。これは別 reference（仮称 `references/ci-evolution-protocol.md`）として将来追加する想定。

#### Smoke Test との関係

scaffold-checklist 既存の **smoke test 手順**（`pnpm install / dev / build / test`）が CI で機械的に走る形になる。`§7.4 自己検証` の「scaffold smoke test」と CI の `test` job は同じスクリプトを呼ぶため、L0 自己検証と CI の検査内容が二重化されない。

#### 残課題（次サイクル以降）

- 現行 `.gitignore` に `.github/workflows/*.yml` の lint 規約がない → CI YAML 自身の linter（`actionlint` 等）採否の判断
- `secrets` の扱い（ベースは secrets 不要だが、E2E で外部 API key が必要なケースの規約）
- self-hosted runner の使用可否規約
- workflow キャッシュ戦略の標準化（`actions/cache` 採否）

### crosscut-verifier-drift の CI 降下診断（2026-05-01、保留中）

CI/CD 強化計画 (2)「crosscut-* 段階稼働プロトコル」の解像度を上げる**診断結果**。現行 `crosscut-verifier-drift` skill（`.claude/skills/crosscut-verifier-drift/`）は CTL ≥ 1 で発動する追加層 verifier だが、その内部処理を「第 2 段（CI、AI 不要）」「第 3 段（AI reviewer）」に切り分けたときの分担を診断する。

#### 現行 drift verifier の 5 種別

| # | 種別 | 軽量モード (CTL-1) | フルモード (CTL-2/3) |
|---|---|---|---|
| 1 | `spec_unrecorded_addition` | キーワード grep | 機能境界 ast 解析 |
| 2 | `adr_unapproved_removal` | （未明記、grep 想定） | （未明記、意味判定想定） |
| 3 | `dont_violation` | DONT.md 文字列 grep | 意味的類似度判定 |
| 4 | `signature_drift` | git diff のみ | TypeScript signature diff（型情報考慮） |
| 5 | `ux_drift` | sensors/interaction-cost ログ参照 | 同左 + 統計的有意性チェック |

#### CI 降下可否マトリクス（診断結果）

| # | 種別 | 軽量 → CI? | フル → CI? | 残る AI 判定 |
|---|---|---|---|---|
| 1 | `spec_unrecorded_addition` | **○** SPEC.md 内の機能 ID と diff 内のシンボル名を grep 比較 | △ 「機能境界」は意味判定 → AI 残置 | 「機能の境界が同一か」 |
| 2 | `adr_unapproved_removal` | **○** 削除行と ADR 内の決定 ID を grep 比較 | △ 「等価変更か破壊的削除か」は AI | 「削除の意味的影響」 |
| 3 | `dont_violation` | **○** DONT.md の禁止パターン（正規表現化前提）と diff を照合 | × 意味的類似度は AI 必須 | 「DONT に書かれていないが趣旨に反するか」 |
| 4 | `signature_drift` | **◎** TS なら `tsc --noEmit` + api-extractor、Rust なら `cargo public-api` で完全機械化 | **◎** 同上 | なし（完全 CI 化可能） |
| 5 | `ux_drift` | **◎** sensors ログ + Lighthouse CI で完全機械化 | **◎** 統計検定スクリプト | なし（完全 CI 化可能） |

凡例: **◎** 完全機械化可、**○** 軽量部分のみ機械化可、△ 一部機械化、× 機械化不可（AI 残置）

#### 機械化に必要な前提条件（書式規約整備）

軽量モードを CI に降ろすには、以下の書式規約が前提条件として整備されていなければならない（現状未整備または不完全）：

| 規約 | 要件 | 現状 |
|---|---|---|
| SPEC.md の機能 ID 規約 | `FUNC-001` 形式等の機械可読 ID を機能ごとに付与 | 不明（プロジェクト依存） |
| ADR の決定 ID 規約 | `ADR-NNN` 形式の決定 ID と「決定／却下」状態の機械可読化 | 不明（プロジェクト依存） |
| DONT.md の禁止パターン規約 | 禁止項目に正規表現またはキーワードを併記（例: 「`console.log(` 禁止」） | 不明（多くは自然文） |
| sensors/interaction-cost ログ形式 | UX メトリクス JSON 出力規約 | sensors/interaction-cost.md で規定（既存） |

→ **drift verifier の CI 降下は、SPEC/ADR/DONT の書式規約整備を伴う構造改修**であり、軽率な機械化は誤検出を量産する。

#### 提案する二段化構造（次サイクル以降の改修像）

```
PR push
  ↓
[第 2 段 CI]
  ├── scripts/drift-check-lightweight.sh （pure shell, AI 不要）
  │     ├── signature_drift（tsc --noEmit + api-extractor diff）
  │     ├── ux_drift（Lighthouse CI + sensors ログ照合）
  │     ├── spec_unrecorded_addition（軽量 grep）
  │     ├── adr_unapproved_removal（軽量 grep）
  │     └── dont_violation（軽量 grep、正規表現規約済の場合のみ）
  │     → delivery/DRIFT-REPORT-LIGHT.md
  ↓
[第 3 段 AI reviewer]
  ├── crosscut-verifier-drift skill 起動（CC runtime）
  │     ├── 機能境界 ast 解析（spec_unrecorded_addition フル）
  │     ├── 意味的類似度判定（dont_violation フル）
  │     ├── ADR 意味判定（adr_unapproved_removal フル）
  │     └── DRIFT-REPORT-LIGHT.md の擬陽性／真陽性判定
  │     → delivery/DRIFT-REPORT.md（最終）
  ↓
[crosscut-feedback-loop へ還流]
```

利点:
- CI 段で擬陽性を含めた**早期検出**、AI 段で擬陽性除去と意味判定（context 節約）
- CTL-0 プロジェクト（drift skill 不発動）でも CI 段の軽量チェックは独立して走る選択肢が生じる
- skill が CC runtime 不在の環境でも、CI 段の最低限は機能する

#### 残課題

- 現行 `templates/.github/workflows/spec-drift.yml` は「skill 起動を CI 上で行う前提」のテンプレで、CI runtime に CC を要求する。本診断の二段化案を採るなら、このテンプレを `spec-drift-lightweight.yml`（pure shell）と `spec-drift-full.yml`（CC runtime 必要）に分離する必要がある
- DONT.md の正規表現化は全プロジェクトに義務付けるか、「機械検査用 DONT 拡張規約」として opt-in にするかの判断が残る
- v5.0.0 既存仕様の改修となるため、minor 昇格 + Council 諮問の対象
- 本診断は読み取りのみで `crosscut-verifier-drift` 本体には変更を加えていない。実装は別 PR

### 外部 CI/CD 知見との整合分析（2026-05-01 調査、保留中）

CI/CD 強化計画 (1)〜(5) の延長として、ひでさんが集めた **AI 主導型 CI/CD アーキテクチャに関する 2026 年時点の業界知見**を DH 既存原則と突き合わせた整合分析。本節は調査結果のスナップショットであり、採用判断は行わない。

#### 入力源と要点（ひでさん経由）

提供された AI 主導型 CI/CD ガイドの要点を 5 領域に整理：

1. **ハーネス・エンジニアリング**: モデル知能より周辺インフラ（セッション管理／コンテキスト供給／ツール制限／ガードレール）の設計が成否を分ける
2. **動的ルーティングとマルチエージェント**: Coordinator-first routing、PEV (Plan-Execute-Verify) ループ、用途別サブエージェント分離（Explore/Plan/Execute/Verify）、Git worktree による隔離
3. **決定論的ガードレール**: Pre-Tool Hook（破壊的操作の強制終了）、Post-Tool Hook（生成直後の lint/SAST フィードバック）でプロンプト指示だけでは不十分な確率的 AI を制約
4. **テストピラミッド 2.0 + DevSecOps シフトレフト**: AI 生成テスト・Record & Playback・SAST/DAST/SCA/Secret scanning の PR ゲート組み込み
5. **アンチパターン**: コンテキスト肥大化／Generator-Evaluator 同一化／過剰権限によるサプライチェーン攻撃／DORA バッチサイズ増大による安定性低下

#### DH 既存原則との一致点（外部証拠による補強）

DH の多くの設計判断は本調査の業界知見と一致しており、外部証拠で正当性が補強される：

| DH の原則 / 機構 | 外部知見の対応概念 | 補強される点 |
|---|---|---|
| **「dialog-harness」という命名** | ハーネス・エンジニアリング | 命名自体が業界用語と直結。DH の存在意義を外部用語で説明可能になる |
| `references/` の遅延ロード機構（SKILL.md description / `name` ヒット時のみ詳細展開） | Progressive Disclosure（段階的開示） | コンテキスト肥大化アンチパターンへの予防が組み込み済 |
| `layer1-autonomous-dev` と `layer1-independent-reviewer` の分離 | Generator/Evaluator 分離 | 「同一 AI に評価させると過大評価」アンチパターンへの予防が組み込み済 |
| `history/INTENT.md` `history/CHANGELOG.md` `delivery/DELIVERY.md` 等のファイルベース記憶 | MEMORY.md / progress.txt パターン | セッションリセット耐性が組み込み済 |
| `crosscut-council` の 3 ペルソナ独立判定 | コーディネーター + 専門エージェント分離 | 単一 AI の盲点問題に対する組織的対処 |
| v5.3.0「1 機能完遂の自律駆動 WF」原則 | DORA 2024/2025: AI でバッチサイズ増大 → 変更失敗率悪化 | DH の小スコープ強制が DORA メトリクスの裏付けで正当化される |
| `regime-assessment.md` の M1/M2/L2 動的判定 | Coordinator-first routing | 自然言語推論による振り分けが既に枠組みとして存在 |
| `sensors/computational.md` `sensors/inferential.md` の段階検証 | テストピラミッド 2.0 の段階構造 | 第 1〜5 層の哲学が業界用語と整合 |

→ **DH の哲学は 2026 年業界ベストプラクティスと独立に到達しており、命名（ハーネス）まで一致**している。これは v5.x 系の哲学的安定性の傍証として `history/DH-PHILOSOPHY-INSIGHTS.md` に補強記録する価値がある（次サイクル対応候補）。

#### DH に欠けている／弱い領域

外部知見と突き合わせて、DH 現行に**実装が薄い／無い領域**を 4 件特定：

| # | 領域 | 外部の対策 | DH 現状 | 強化候補 |
|---|---|---|---|---|
| α | 機械的 Pre-Tool Hook | 破壊的操作（`rm -rf`、本番 DB 接続）を CI / runtime レベルで強制終了 | DONT.md の規範記述のみ。機械的ガードなし | sensors/computational.md に Pre-Tool 規約節を追加。`crosscut-issue-implementer` 起動時の hook として組み込み |
| β | Post-Tool 自動フィードバック | 生成直後に lint/SAST/typecheck → AI に結果フィードバック | layer1-autonomous-dev の自己検証で間接的に実装 | **第 2 段 CI（scaffold-checklist CI 章）** で機械的補強。本 PR の (3) と統合可能 |
| γ | OIDC / 短寿命トークン規約 | GitHub Actions OIDC で本番デプロイ／npm publish 時に長寿命トークンを排除 | dev_mode = github_full_auto で言及はあるが具体規約なし | `dev-env-spec.md` に dev_mode 別の secrets/トークン規約を追加 |
| δ | DORA メトリクス計装 | Lead Time / Deploy Freq / Change Failure Rate / MTTR の自動計測 | 計測機構なし | `history/DORA-METRICS.md`（仮）として LC=2 以上で必須化を検討 |

→ いずれも CI/CD 強化計画 (1)〜(5) の**追加候補 (6)〜(9)** として記録する：

- **(6) 機械的 Pre-Tool Hook 規約**（α）
- **(7) Post-Tool 自動フィードバック ↔ CI 第 2 段の連結**（β、(3) と一体化）
- **(8) OIDC / 短寿命トークン規約**（γ）
- **(9) DORA メトリクス計装規約**（δ）

#### 重要な警告事例: Cline CLI 事件（2026）

外部調査で言及された **Cline CLI が 2026 年に GitHub Issues 経由のプロンプトインジェクションで CI 環境を乗っ取られ、npm パッケージが乗っ取られた事件** は、DH の `crosscut-issue-implementer` 設計に対する直接的警告：

- **設計時の前提**: `crosscut-issue-implementer` は GitHub Issue を起点に CC 実装を起動する横断機構（仕様2、v5.0.0）
- **同型のリスク**: Issue 本文・コメントが AI への入力となるため、攻撃者が Issue にプロンプトインジェクションを仕込み、CI 環境で任意コード実行・パッケージ乗っ取りに繋げる可能性
- **DH 既存の対策**:
  - `dev_mode = local_only` では `crosscut-issue-*` 全般が無効（本リスクは発生しない）
  - `github_assisted` では実行手段が worktree 主体で隔離される
  - `github_full_auto` では Actions 経由となり、本リスクが顕在化
- **追加すべき対策**（強化候補 (6) (8) と統合）:
  - Issue 本文を AI に渡す前のサニタイザ規約（`<system>` 等の特殊タグ・大量 ASCII art の検出）
  - OIDC + 短寿命トークン強制（npm publish / 本番 deploy で長寿命トークン禁止）
  - 重要操作前の人間承認ゲート（manual approval を `github_full_auto` でも必須化）
- **記録先**: `crosscut-issue-implementer/SKILL.md` または専用 reference に「外部事例: Cline 2026 事件」として追記する候補（次サイクル）

#### crosscut-* skill との対応マッピング

| 外部知見の概念 | DH 対応 skill | 対応状況 |
|---|---|---|
| Coordinator-first routing | `layer0-spec-architect`（モード判定 + dev-env 構築） | 既実装 |
| PEV ループ | spec-architect → autonomous-dev → independent-reviewer | 既実装（v4.x 確立） |
| Explore subagent | Claude Code の Explore agent（DH 外） | DH 直接対応なし、利用は推奨 |
| Pre-Tool Hook | sensors/computational + DONT.md（規範のみ） | **機械的実装なし**（強化候補 α） |
| Post-Tool Hook | layer1-autonomous-dev §7.4 自己検証 + 第 2 段 CI | **CI 連結が未確立**（強化候補 β） |
| Generator/Evaluator 分離 | autonomous-dev / independent-reviewer | 既実装 |
| Record & Playback | （対応なし） | scaffold-checklist 拡張候補（v5.x minor） |
| OIDC / 短寿命トークン | （対応なし） | dev-env-spec 拡張候補（強化候補 γ） |
| DORA メトリクス | （対応なし） | 追加層候補（強化候補 δ） |
| プロンプトインジェクション対策 | crosscut-issue-dispatcher / implementer の自動起動制限 | **入力サニタイズ層なし**（Cline 事件への対応） |

#### 残課題

- 本節の量が膨らんだため、次サイクルで `history/research/2026-05-01-ai-cicd-survey.md` 等の独立ファイルに切り出す検討（`history/research/` は新規ディレクトリのため別途構造判断が必要）
- 強化候補 (6)〜(9) のうち **(7) Post-Tool 自動フィードバック ↔ CI 第 2 段** は本 PR の (3) scaffold-checklist CI 章 構造ドラフトと**直接統合可能**。次サイクルで一体化した形で再起動する余地あり
- Cline 事件の一次情報（公式 incident report URL）は本サイクルでは未確認。次サイクルで `crosscut-issue-implementer` 改修に着手する際に出典付きで補完すること
- 本調査の範囲は AI 主導型 CI/CD に偏っており、伝統的な CI/CD（言語ランタイム別最小構成、actionlint 等の defacto ツール、solo dev 向け推奨パターン）は別途調査余地あり

## v5.5.3 で追加された概念

### autonomous-drive 機構の出口側として label opt-in 自動 merge を新設

DH の crosscut-issue-implementer から続く autonomous-drive 機構（issue → AI 実装 → 多層レビュー → 自動 merge）の最終段階を本 patch で実装。今までは人間が merge ボタンを手押しする箇所だったが、明示的な opt-in（label `auto-merge`）+ 多層検証通過時のみ自動化することで、ユーザーの手介入を「issue 作成（GO サイン）」と「検証 fail 時の判断」の 2 点に限定する方向性へ進む。

#### 設計意図の核

**(a) autonomous-drive パイプラインの完成形**: v5.0.0 で導入した crosscut-* 機構（dispatcher / issue-implementer / feedback-loop）は入口〜中段までを autonomous 化していたが、最終段階の merge は手動だった。本 patch で出口も自動化し、issue 起点〜merge 完了までの autonomous loop を構造的に閉じる（philosophy.md §6 H3「方向性発案」相当の人間専管判断は issue 作成時に集約される設計）。

**(b) 段階的引き上げの選択（パス A 採用）**: 当初の選択肢として「パス A: auto-merge workflow だけ追加」と「パス B: dev_mode を `autonomous` に引き上げ（spec-architect 経由）」があったが、観測駆動原則（`wf-baseline-rationale.md` §3）に従いパス A を先に運用 → 数 PR で問題なければパス B 昇格を判断する。本 patch はパス A の実装。

**(c) 多層検証による信頼境界の構築**: auto-merge 条件は単一の checkbox ではなく、以下の 4 層 AND で構成される：
- **構造層**: harness-verify SUCCESS（D4 整合性、5 検査）
- **意味層**: gemini-review SUCCESS（異質モデル独立 critic、走った場合のみ）
- **判断層**: reviewDecision != CHANGES_REQUESTED（人間 / Copilot / gemini いずれかの REQUEST_CHANGES が立てば block）
- **承認層**: label `auto-merge` 付き + author allowlist（明示的 opt-in + 信頼境界）

各層が独立して fail を表明できる設計で、philosophy.md §3「情報純度」（Generator/Evaluator 分離）と §5「献上哲学」（自律内部完結禁止、独立観測機構の通過）を実装。

**(d) Workflow env への明示 hardcode による author allowlist**: `ALLOWED_AUTHORS` を **workflow env に hardcode** する形を採用（外部 secret や別 config file に逃さない、Copilot review #42 line 363 で初版の heading 矛盾「ハードコードを避けた」を訂正）。理由: contributor の追加は spec 改修扱いとし、L0 spec-architect 経由で REGIME.md との整合確認を必須化する設計判断。これにより allowlist の不可視拡張（誰かが secret を追加して invisible に信頼境界が広がる）を防ぐ。

**(e) verifier 全て「走った場合のみ必須」+ 最低 1 verifier guard**: harness-verify と gemini-review はいずれも paths filter で発火しない PR が存在する（harness-verify は `.claude/skills/**` `harness-verifier/**` `.github/workflows/harness-verify.yml` のみ、gemini-review は `.claude/skills/**` `harness-verifier/**` `history/**` 等）。両 verifier を「走った場合のみ SUCCESS 必須」とし、永久 pending を回避。ただし両 verifier 共に paths filter 外の PR は **zero-check** で auto-merge されてしまうため、**最低 1 つの verifier が SUCCESS で走っていること**を別途 guard 条件として追加（Copilot review #42 line 145 で初版「harness-verify は paths filter なしで全 PR 走る」事実誤認を訂正、line 89 の robustness 指摘も含めて統合修正）。

#### 改修内容

- `.github/workflows/auto-merge.yml` 新設（160 line）

#### 同梱: v5.5.2 (in progress) → (released 2026-05-03) 化

PR #41 merge 後の `(released)` 化 follow-up PR が遅延していたため、本 PR に housekeeping として同梱。独立 PR を増やさず、4 例目正規適用として記録。

#### v5.5.x / v5.6.0 候補として温存

- **パス B: dev_mode autonomous 化**: 本パッチ（パス A）で数 PR 試運用 → 問題なければ L0 spec-architect 経由で REGIME.md `dev_mode: github_assisted` → `autonomous` 引き上げ。issue 作成 → AI 実装 → auto-merge までフル自動化（v5.6.0 候補）
- **`ALLOWED_AUTHORS` の動的化**: 現在 hardcode だが、複数 contributor 体制になったら repository variable 化を検討（現状不要、philosophy.md §6 H3「方向性発案」原則と整合）
- **destructive change detector**: diff の line count threshold / DELETE-heavy diff 検出による追加 guard（v5.5.x 候補、観測駆動で追加判断）

## v5.5.2 で追加された概念

### gemini-review の diagnostic 機構縮退と PAT availability check 新設

v5.5.1 PR #40 で gemini-review GitHub Action（PR #37/#38 で導入、v5.5.1 で動作確立）の運用テストが完了。診断旅程で導入した暫定機構（`continue-on-error: true` / `GEMINI_DEBUG: "true"` / 2 件の Diagnostics step）を本 patch で削除し、本番運用構成へ縮退する。並行して、`continue-on-error` 削除の副作用として PAT 未設定環境で job が hard-fail する事象を防ぐため、`GH_REVIEW_PAT` の availability check を新設する。

#### 設計意図の核

**(a) 診断機構の役割完遂と縮退**: v5.5.1 PR #40 で 8 commit にわたり実施した段階的診断（仮説 A〜F + α）の結果、真因 = settings JSON `tools.core: []` / `includeTools` filter による tool exposure 阻害（α パッチで除去）+ PAT permission 不足（ユーザーが Read+Write 付与）と確定。診断機構はもう機能不要（philosophy.md §5 献上哲学の「役目を終えた機構の縮退」原則と整合）。

**(b) Operational behavior 変更の意図的可視化**: `continue-on-error: true` 削除により、transient な Gemini/MCP 失敗が **silent success → hard-fail (red CI)** に変わる。これは observable な behavior 変更（Copilot review #41 で指摘）であり、本 patch の意図的設計判断。レビュー機構の fail を fail として可視化することで、philosophy.md §3 情報純度の系（「観測されない fail は存在しないのと同じ」を排除）を実装する。

**(c) PAT availability check の必要性**: `continue-on-error` 削除に伴い、PAT 未設定で MCP server に空 token を渡すと review_write が API レベルで「Resource not accessible」を返し job が red になる。`GEMINI_API_KEY` と同形式の早期 availability check を `GH_REVIEW_PAT` にも適用し、いずれかが未設定なら notice 出力でクリーン skip する。

**(d) self-PR APPROVE は API 応答ベース fallback で扱う**: PR author と PAT owner が同一の場合 APPROVE は API が拒否するが、これを workflow 側でハードコードする案（v5.5.2 patch 草案）は Copilot review #41 で「他 maintainer が同 repo に PR を作った場合に誤った検閲となる」と指摘 → revert。prompt は v5.5.1 と同じ「APPROVE/COMMENT/REQUEST_CHANGES 全選択肢、self-PR で API 拒否時のみ COMMENT fallback」方式を維持。author の事前判定は unenforced repository assumption に依存するため避ける。

**(e) tool exposure と security の trade-off の明文化**: α パッチで `includeTools` filter を削除した結果、github-mcp-server の **全 tool（write/destructive 含む）が model に expose** される状態が継続。本 repo は信頼済み author 前提で許容するが、settings JSON コメントに security 注を明記し、v5.5.x 候補として「tool 名の正しい形式判明後の read 系絞り込み」を温存する。

**(f) artifact upload は保持**: 将来 debug 必要時の即応性を考え `actions/upload-artifact@v4` step は残す（cost 極小、retention 7 日）。これは「diagnostic」ではなく「永続的観測機構」と位置付け直す。

#### 改修内容

- `.github/workflows/gemini-review.yml`: diagnostics 2 step 削除 / `continue-on-error` / `GEMINI_DEBUG` / `id: gemini_review` 削除 / **`Check GH_REVIEW_PAT availability` step 新設** / `Run Gemini PR review` と `Upload gemini-artifacts` の if 条件を両 secret available に拡張 / prompt の self-PR セクションを fallback 方式へ簡素化 / settings JSON コメントに security 注追加

#### v5.5.x / v5.6.0 候補として温存

- **`includeTools` を正しい tool 名で復元**: github-mcp-server v0.27.0+ の正確な tool 名（toolset 命名規則）が判明したら read 系のみへ絞り込み（destructive tool の expose を排除）
- **CodeRabbit / 他 AI レビュアーとの併走比較**: gemini-review が異質モデルとして機能した実績を踏まえ、複数 AI reviewer の独立配置を検討
- **gemini-review の利用者プロジェクト template 化**: dialog-harness 自身の運用が安定したら template 化を検討（v5.5.0 から候補温存中）

## v5.5.1 で追加された概念

### Phase γ 先行宣言 4 本実装: ストラングラー・フィグ / Branch by Abstraction の射程外正式宣言

v5.5.0 で温存された Phase γ 残 2 件のうち、先行宣言 4 を v5.5.1 patch で本実装。先行宣言版（4 行記述）から本実装版（射程外要素列挙 + 援用と全体採用の境界線 + L1/L2 禁止規約 + v6.0.0 昇格の観測トリガー + 整合性ガード）へ昇格。

#### 設計意図の核

**(a) 「射程外」を明示宣言する哲学的必要性**: archeo は「意図復元」（L0 = 過去→意図）の射程であり、ストラングラー・フィグ / Branch by Abstraction は「リファクタ実行戦略」（L1/L2 = 未来→実装の段階制御）の射程である。両者は抽象階層が異なる。Phase γ コア 3 件の実装過程で `handoff-to-evaluator.md` が VB6 移行事例（ストラングラー類似）と Branch by Abstraction に言及したため、L1 実装者が「先行宣言 2 → BBA 全パターン採用」と拡大解釈する誤りリスクが生じた。本宣言で境界線を明文化することで Shift Left 防止する。

**(b) 「援用」と「全体採用」の区別の制度化**: 先行宣言 2 は VB6 事例の「結果照合メカニズム」と BBA の「抽象化レイヤー越しの並列実行」を **概念として援用**しているが、ストラングラー全体（ルーティング層 / facade / 段階的トラフィック切替 / decommissioning）や BBA 全体（feature flag / 段階的切替プロトコル / 旧実装 cleanup）は **採用していない**。この区別を本宣言 (b) で表形式で厳密化する。

**(c) L1 / L2 への禁止規約の明文化**: archeo 由来情報からストラングラー/BBA パターンを **自動導出してはならない**ことを禁止規約として制度化。例: 「Island-002 が restructure だから自動的に feature flag を導入する」「複数 Island に渡るから自動的にルーティング層を作る」等は archeo 起点では禁止し、別 SK / 別 minor で別途設計する経路に振り分ける。

**(d) 観測駆動原則との整合**: `wf-baseline-rationale.md` §3「観測駆動でのみ拡張」原則に従い、本宣言の v6.0.0 昇格条件を「≥ 3 異なる利用者プロジェクトでストラングラー/BBA パターンの archeo 連動採用要請が観測された場合」と明示。現状（観測ゼロ）では仮説扱いとして温存。

**(e) 整合性ガード（schema priority）**: 本宣言（先行宣言 4）と先行宣言 2/3 の記述に矛盾がある場合は本宣言が優先する schema priority を制度化。今後先行宣言 2 を更新する際の整合確認義務を発生させる。

#### 改修内容

- `layer0-archeo-architect/references/handoff-to-evaluator.md`: ステータスヘッダ更新 / ロードマップ表 v5.5.1 行追加 / 先行宣言 4 セクション本体を本実装版に拡充

#### 5 件中 1 件が引き続き温存（v5.5.x patch / v5.6.0 候補）

- **先行宣言 5: 失敗アンチパターン早期検出** — Phase β（ritual-protocol レベル 3 統合）と一体化して v5.5.x patch / v5.6.0 へ後送（v5.5.0 から継続温存）

#### 副次的副作用: gemini-review GitHub Action の運用テスト

PR #37 (gemini-review 導入) / PR #38 (model pin) で導入された gemini-review GitHub Action の独立レビュー機能を、本 patch PR が初めて実運用でテストする。`.claude/skills/**` + `history/**` 改変 + non-draft PR の発火条件を満たし、gemini-review がレビュー指摘を返した場合は本 PR 内で応答する自動往復ループを実証する。テスト結果は `delivery/SELF-VERIFICATION-v5.5.1.md` に記録予定。

## v5.5.0 で追加された概念

### adrv01-Ph1: AI 自己申告閾値の Council 連動明文化

PR #33 ブレスト結晶 `delivery/AUTONOMOUS-DRIVE-BRAINSTORM-2026-05-02.md` で確定したロードマップ「v5.5.0 = adrv01-Ph1 + Phase γ」の adrv01-Ph1 部分を本リリースで本実装。HANDOFF v0.1.0「自律駆動機構の哲学的座標」§2.2「拮抗判定検出主体」の Council 結果（`council-2026-05-02T11:00:00Z-adrv01`、`agreed_with_modification` 段階的組み込みで止揚）の Phase 1 部分。

#### 設計意図の核

**(a) 既存機構の流用、コスト 0**: `crosscut-council/SKILL.md` L16/L47/L68 で既に定義されている「自己評価 confidence < 0.6」の三箇所を Council 起動の正式トリガーとして明文化するのみ。新規実装ゼロ、機構強化（hook 本実装）は v5.6.0 adrv01-Ph2 へ温存。

**(b) 自己申告 = 一次入力 + Council = 二次検証**: 実装者の自己 confidence は内側からしか見えない（self-感知の特性）が、判断の正当性は外側からの観測で補強する必要がある（philosophy.md §3 情報純度・§5 献上哲学）。Council は「自己申告 + 重み付き判定」の二相構造で情報純度を確保する。

**(c) 内部完結による回避の禁止**: 自己 confidence < 0.6 検出時に「自己評価しただけ」「自分で考えてみる」等で内部完結させてはならず、該当条件を検出した時点で本 skill を起動する義務を負う（明文化）。

**(d) Council `vrfy01` 事例による補強**: 本リリースの開発過程で、L0 spec-architect の振り返り儀式 F2 から発生した Council 諮問 `vrfy01` で `category: conception` の誤選択（Copilot review #34 で指摘）が哲学者重みを過剰にして escalation 経路に乗せた連鎖を発見。`pre-check.md` に「scope/PR 境界 vs 新規思想」の判別シナリオ例を追加し、`consensus-protocol.md` に「escalated 経路での合意成立」エッジケースを明文化することで再発防止を Shift Left で実装。

#### 改修内容

- `crosscut-council/SKILL.md §自己申告プロトコル` 新節（`confidence < 0.6` を Council 起動の正式トリガーとして明文化、内部完結禁止）
- `crosscut-council/references/pre-check.md` §scope/PR 境界 vs 新規思想 の判別シナリオ（Copilot review feedback、category 誤選択の Shift Left 防止）
- `crosscut-council/references/consensus-protocol.md` §エッジケース「escalated 経路での合意成立」+ §自己申告 → Council 起動の hook 経路（v5.6.0 Ph2 で本実装の先行宣言）

#### v5.6.0 / v6.0.0 候補として温存される拡張

- **adrv01-Ph2**（v5.6.0 候補）: 独立観測機構（harness-verifier 同型の新規 crosscut-* skill）。autonomous-dev 出力 / 試行回数 / 往復パターンの客観観測、stats.json への自己申告イベントスキーマ拡張、`crosscut-feedback-loop` への自己申告イベント還流ルート新設
- **adrv01-Ph3**（v6.0.0 候補）: 階層構造として止揚 — 自己申告 = 一次入力、独立機構 = 申告事実の検証メタ層（哲学者法廷モデル）

### Phase γ コア 3 件: L1 評価軸 4 軸化（起点問題の構造解決）

v5.4.0 archeo-architect Phase α でリリースされた `handoff-to-evaluator.md` 先行宣言 5 件のうち、コア 3 件（先行宣言 1: 承認テスト生成プロトコル / 先行宣言 2: 自動照合ループ / 先行宣言 3: L1 意図合致軸統合）を本リリースで本実装。

#### 設計意図の核

**(a) 起点問題の構造解決**: ひでさんの起点問題「自分で書いたコードのリファクタを依頼すると意図通りにならない、10 個の修正点を依頼して 3〜4 個取りこぼす」を構造的に解決する。L1 (`layer1-autonomous-dev`) の自己検証/独立検証は v5.4.0 まで「仕様適合・動作・ユーザビリティ」の 3 軸評価で「意図合致軸」が不在だった。archeo の `delivery/refactor-intent-map.md` を L1 評価軸の **第 4 軸**として注入する。

```
[v5.4.0 まで] L1 評価軸 = (仕様適合 ∩ 動作 ∩ ユーザビリティ)
[v5.5.0]      L1 評価軸 = (仕様適合 ∩ 動作 ∩ ユーザビリティ ∩ 意図合致)
```

**(b) refactor_directive 別の検証メカニズム**: 各 Island の `refactor_directive` に応じて 3 系統の検証を実行：

- **preserve**: 承認テスト生成プロトコル（フェザーズ「レガシー = テストなし」/ Approval Testing カノン由来）。現状コードの入出力を `delivery/approval-tests/<island-id>.baseline.json` として基準データ化、リファクタ後との差分検出
- **restructure**: 自動照合ループ（VB6 価格エンジン移行事例 8,064 回ラン / 0.007% 不一致検出 / 420 万ドル損失防止 / Branch by Abstraction 由来）。新旧並行実行 + 結果照合で不一致率 < 閾値（デフォルト 0.01%）を機械的に検証
- **discard_and_redesign**: `AbsentZone.redesign_directive` 適合確認、意図保存制約は解除

**(c) 後方互換完全維持**: `refactor-intent-map.md` 不在時は意図合致軸が完全スキップされ、従来 3 軸動作と同一になる。LC ≥ 1 既存プロジェクトには遡及適用なし。archeo を一度も起動していないプロジェクトには一切影響しない。

**(d) archeo Phase α からの双対完成**: archeo（過去→意図復元、L0）と autonomous-dev / independent-reviewer（未来→実装、L1）の双対構造が、Phase γ コア 3 件で「意図譲渡 → 評価軸内蔵」として完成する。philosophy.md §1 フラクタル原則 P1 の自然な拡張（spec-architect → L1 の譲渡構造と同型）。

#### 改修内容

- `layer0-archeo-architect/references/handoff-to-evaluator.md`: 先行宣言版 → コア 3 件本実装版へ拡充
- `layer1-autonomous-dev/references/inferential-sensor-v2.md` §第4層: 意図合致軸の起動条件 + 判定ルール追加
- `layer1-autonomous-dev/SKILL.md §6 自己検証`: 承認テスト生成 + 自動照合ループプロトコル追加
- `layer1-independent-reviewer/SKILL.md`: 評価軸 3→4 軸化、§5.4 意図合致チェック追加
- `layer1-autonomous-dev/references/delivery-format.md`: 意図合致検証セクション追加（refactor-intent-map.md 存在時のみ）

#### 5 件中 2 件温存（v5.5.x patch / v5.6.0 候補）

- **先行宣言 4: ストラングラー・フィグ / Branch by Abstraction の射程外宣言** — v5.5.x patch で `handoff-to-evaluator.md` に簡記、本格的な L1 / L2 リファクタ実行プロトコル化は v6.0.0 候補
- **先行宣言 5: 失敗アンチパターン早期検出** — Phase β（ritual-protocol レベル 3 統合）と一体化して v5.5.x patch / v5.6.0 へ後送

### β止揚運用の制度化（Council `vrfy01` から派生）

PR #33 adrv01 の「段階的組み込みで止揚」パターンを本リリースの Council `vrfy01`（v5.5.0 着手前検証スコープ判定）で再採用し、「V-1 狭義 + 第3の道（検証を v5.5.0 SPEC 化に内包）」の止揚運用を実施。残ドリフト検査が SPEC 化過程で「既存機構の SPEC ↔ 実装照合」として自然に内包され、独立フェーズ化による情報損失を回避する運用パターンを `delivery/SELF-VERIFICATION-v5.5.0.md` に記録。adrv01-Ph2（v5.6.0 独立観測機構）への自然な前段としても整合。

### v6.0.0 候補として温存される思想拡張

- **adrv01-Ph3 哲学者法廷モデル**: 階層構造として止揚（自己申告 = 一次入力、独立機構 = 申告事実の検証メタ層）。adrv01-Ph2 の運用観測データ蓄積後に再評価
- **adrv02-Ph2 ハイブリッド段階移行**: subagent isolation 統合の本実装。「context 共有 vs context 分離」評価軸での本格運用
- **第3の道 + crosscut-verifier-philosophy 大統合**: 哲学整合検証の本実装と autonomous-drive 機構の統合判定機構化（v5.0.0 から複数 minor 後送中、v6.0.0 major で大統合）
- **L1-refactor スキル新設（Level B）**: archeo01 哲学者拡張提案、プロジェクト固有 SK によるリファクタ支援の本実装

## v5.4.0 で追加された概念

### archeo-architect の追加（spec-architect の双対、L0 兄弟）

ひでさん起点問題「自分で書いたコードのリファクタを依頼すると意図通りにならない。10 個の修正点を依頼して Evaluator ループを回しても 3〜4 個取りこぼす」の構造解決として、リファクタ前 Layer 0 を担う `layer0-archeo-architect` を新設した。HANDOFF「archeo-architect ブレスト → 実装」 2026-05-01 を起源とする。

#### 設計意図の核

**(a) spec-architect の双対**: spec-architect が「人間イメージ → 未来仕様」（未来志向）であるのに対し、archeo-architect は「既存コード → 意図復元」（過去志向）である。両者は **対話の方向が逆だが、構造は同型**（philosophy.md §1 フラクタル原則 P1 の自然な拡張）。

L0 は v5.0.0 までは spec-architect 単独、v5.0.0 で onboarding を「使い捨て後付け化」として追加して兄弟スキル 2 つになり、v5.4.0 で archeo-architect を「再利用可能な意図復元」として追加して兄弟スキル 3 つになった。3 兄弟は責務分担表で**排他**に分離される（spec-architect SKILL.md §L0 スキル間の責務分担表）。

**(b) 起点問題の構造的根因**: L1 (`layer1-autonomous-dev`) の自己検証/独立検証が「仕様適合・動作・ユーザビリティ」の 3 軸で評価しており、「**人間の元々の意図に合う**」軸が不在だった。archeo の出力 `refactor-intent-map.md` を L1 評価軸の第 4 軸として注入することで、3〜4 個取りこぼし問題が構造的に解消する。

ただし L1 改修は v5.4.0 では実施しない（**Phase α と分離**、後述）。本リリースでは archeo SK 雛形のみ提供し、人間が手動で `refactor-intent-map.md` を参照しながらリファクタ指示を組み立てる運用を可能にする。

**(c) 3 原則の制度化**: 3 原則を `archeo-architect/SKILL.md §原則` に明記する。

- **P-Arch-1 忘却の制度化**: 人間は忘れる。これは欠陥ではなく前提。AI は仮説提示で認識合わせをドライブする
- **P-Arch-2 意図なきコードの扱い**: 既存コードに意図が存在しない場合がある。AI は `absent` として記録する。**捏造は禁止**（テンプレ必須フィールドで物理的に阻止）
- **P-Arch-3 譲渡構造の維持**: spec-architect が SPEC.md を L1 に譲渡するように、archeo は `refactor-intent-map.md` を L1 に譲渡する

**(d) Phase 化による段階導入**: archeo の完全実装は 4 Phase に分割する：

| Phase | スコープ | リリース |
|---|---|---|
| α | archeo SK 雛形のみ。人間が手動でマップ参照 | **v5.4.0（本リリース）** |
| β | ritual-protocol レベル 3 統合・glossary 用語追加 | v5.4.x または v5.5.0 |
| γ | L1 自己検証/独立検証への意図合致軸追加（**起点問題の構造解決**） | v5.5.0 候補 |
| δ | spec-architect への逆輸入（運用データ 3 ヶ月後） | v6.0.0 候補（温存） |

**(e) 自動起動禁止**: 本 skill は人間明示トリガーのみで起動する。ritual-protocol レベル 3 でリファクタ示唆を検出した場合も、起動推奨提示にとどめる（philosophy.md §6 H3「方向性発案」相当の人間専管判断と整合）。

#### 議論済みで本リリースで決着しなかった論点

- **配置案 A（独立 SK） vs 案 B（spec-architect 派生モード）**: 案 A 採用。理由は対話方向の反転（spec=人間→AI、archeo=AI→人間）と責務単一性。Plan agent / ハンドオフがいずれも案 A 推奨で、Explore agent の案 B 推奨（既存 spec-architect の多軸モード分岐への統合）は今回採用しない。理由詳細は HANDOFF「archeo-architect ブレスト → 実装」§配置案A・B 両論併記参照
- **D4 改修レベル**: minor 確定。新規 SK 追加 + 後方互換維持 + philosophy.md 章追加なし。onboarding 追加時 (v5.0.0) と同形式
- **1→5 フェーズでの起動**: オプション + 動的起動。標準装備化はしない（新規プロジェクトでの不要起動を避けるため）

### Council 諮問による業界知見統合（追加実装、Council 経由）

PR #30 draft 期間中にひでさんから AI を活用したレガシーコード・リファクタリング業界知見が共有され、Council 諮問 (`council-2026-05-01T10:30:00Z-archeo01`, conception カテゴリ、哲学者重み 5) で「**第 4 の道: 選択肢 A 縮小版 + Phase γ 伏線追加**」が agreed_recommended 確定。本 PR に追加実装：

- **`intent-hypothesis-protocol.md` に Code Smells カノン対応表追加** — ファウラー / ヘルマンズの 12 種 Smells（Long Method / Duplicate Code / Large Class / Feature Envy / Shotgun Surgery / Divergent Change / Dead Code / Magic Number / Comments / Speculative Generality / Temporary Field / Refused Bequest）と本プロトコルの既存 8 ヒントのマッピング。仮説生成の信頼性向上と人間との対話精度向上に資する
- **Git ホットスポット分析の S 軸統合** — Adam Tornhill「Your Code as a Crime Scene」に基づき `hotspot_score = log(修正頻度) × 複雑性指標` を S 軸に補正。アンチパターン「90 日の法則」（92% 失敗率）への対応として、上位 10% を archeo セッションの初期対話対象に優先する戦略
- **`handoff-to-evaluator.md` の Phase γ 詳細仕様 5 件先行宣言** — (1) 承認テスト生成プロトコル（フェザーズ「テストなし = レガシー」を P-Arch-1 の系として実装）、(2) 自動照合ループ（VB6 事例 8,064 回ラン / 0.007% 不一致検出と同形）、(3) L1 意図合致軸統合（**起点問題の構造解決**）、(4) ストラングラー・フィグ / Branch by Abstraction の射程外宣言、(5) 失敗アンチパターン早期検出。Phase γ (v5.5.0 候補) で本実装

### 経営者の少数意見（保持記録）

Council で経営者は選択肢 B（PR スコープ厳守、観測駆動を 1〜2 ヶ月優先）を主張し、minority_opinion として保持された。本 minority は観測駆動原則（INTENT.md v5.3.0、`wf-baseline-rationale.md` §3）の側面で妥当性が高い：「Phase α 単独運用での取りこぼし削減効果を観測してから業界知見を選別取込する方が、効果測定の対照群として精度が高い」という主張。

哲学者の「5 年スパンで業界 best practice と整合する harness になるか」論で吸収され重み付き計算で minority に留まったが、**観測駆動原則との緊張関係**は本 v5.4.0 リリース後の Phase β/γ 設計時に再検討する。具体的には、Phase β 着手時に「業界知見取込前 vs 取込後」の比較データが必要なら、Phase α リリース直後の archeo セッション（複数件）を取込前データとして保存する運用を検討する。

### v6.0.0 候補として温存される思想拡張

`refactor-intent-map.md` の Islands スキーマを **AI 組織応用**（AI エージェント間引き継ぎへの拡張）に活用する案を v6.0.0 候補として温存する。v5.x 帯では「コードベース内の意図復元」に限定し、テンプレートに「拡張余地」コメントのみ残す（捏造防止規約と整合させるため、AI 組織応用は別の合議が必要）。

`refactor_directive` の値域拡張（`partial_restructure` / `merge` / `split` 等）も v6.0.0 候補として温存する。Phase α では 3 値（preserve / restructure / discard_and_redesign）のみで運用し、観測駆動で拡張可否を判定する（`wf-baseline-rationale.md` §3「観測駆動でのみ拡張」原則と整合）。

ストラングラー・フィグ / Branch by Abstraction を L1 / L2 のリファクタ実行プロトコルとして体系化する案、および DDD Bounded Context との Boundaries 統合（`subphase-l02-domain.md` との連携）も v6.0.0 候補（業界知見の本格的吸収を minor 範囲外とする判断、Council 哲学者の射程区分判定）。

**L1-refactor スキル新設の v6.0.0 拡張提案** — Council 諮問 `council-2026-05-01T11:00:00Z-archeo02`（ひでさん提案、CC 機械的検査で 5 原則違反指摘、Council 諮問で 3 ペルソナ unanimous B 採用）の哲学者拡張提案として、「v6.0.0 で **Level B プロジェクト固有 SK によるリファクタ支援** を明文化する」を温存。DH 本体（Level A、D4）は形状単一を保ち、機能タイプ特化はプロジェクト側（Level B）で吸収する設計。v5.x 帯で実装しない（archeo Phase β / γ / δ 他の minor 改修を圧迫しないため）。

## v5.3.0 で追加された概念

### 1 機能完遂の自律駆動 WF を「形状単一・薄い基底」として確定

HANDOFF「1 機能完遂の自律駆動 WF 設計」2026-04-30 を起源とする L0 設計判断。
論点 1（WF 基底）/ 論点 2（献上トリガー 4 種）/ 論点 3（WF 選択責任）の 3 件を
Council 合議 (`council-2026-04-30T14:30:00Z-wfsurf1` / `council-2026-04-30T14:50:00Z-wfbase1`) と
実装者裁量（論点 3）で確定し、AD-015 / AD-016 / AD-017 に記録した。

設計意図の核：

**(a) 機能タイプ別 WF 群を作らない**。bug-fix / 新規機能 / リファクタ / 仕様改訂等は
`.claude/skills/layer1-autonomous-dev/SKILL.md` §4「実装タスク分解」内で扱う context 差異であって、独立 WF を生成する分業軸ではない。
これは philosophy.md §1 フラクタル原則 P1（同型再帰）が要求する「形状単一性」を運用原則として
組み込む判断である。職種別分業（フロント/バック/SRE 等）が職能のサイロ化を生むのと同型に、
機能タイプ別 WF 群は 5 年スパンで「タイプ N+1 の追加要求」を再発させる罠を持つ。
当面は単一 WF + 動的 context 注入で吸収し、観測（同一 override パターンの 3 機能タイプ以上での
反復）が閾値を超えた場合のみ Council 経由で基底側引き上げを再諮問する。

**(b) 既存 §処理フローが thin baseline を充足している**。
`layer1-autonomous-dev/SKILL.md §処理フロー（1〜8）` は HANDOFF が要求する「薄い基底」を
既に満たしている。新規 WF テンプレートを追加しない判断は、既存実装への信頼の表明であり、
かつ YAGNI 原則と整合する。

**(c) 献上経路を 4 分類化して情報純度を上げる**。
従来 Type A（仕様レビュー結果）に詰め込まれていた「AI 自己解決不能な技術的例外」を
Type D（異常献上）として分離する。仕様起因（Type A → L0 差し戻し）と
技術例外（Type D → 人間判断要請）は本質的に異なる救済経路であり、混同は P3 責務分離違反。

**(d) WF 選択責任は問題化しない**。
WF が単一形状で確定したため、「どの WF を起動するか」という選択問題が構造的に消失する。
残課題（機能タイプ誤認 / モード誤判定 / 権限・CTL 誤り）はすべて既存メカニズム
（Type C / 体制事後評価 / Type D）で吸収可能。新規ディスパッチャ等は不要。

### v6.0.0 候補として温存される思想拡張

論点 1 で哲学者が提示した第 3 の道「**単一 WF + 動的 context 注入**」を、現行 v5.3.0 の
運用原則を超える形での実装案として v6.0.0 major 候補に温存する。これは context engineering
の中核に WF 設計を据え直す思想転換であり、minor 改修では実装し得ない。

論点 2 で哲学者が提示した「**献上 3 軸構造**（トリガー × 中身 × 権限）」を philosophy 第 8 条
候補（第 7 条＝次元論と D4 の独立性 と並列の「献上 3 軸の存在論」）として温存する。
Type D 単純追加は二項分類の罠（Type E/F/G の追加要求が将来再発する可能性）を構造的に
解消できないため、3 軸構造への昇格を v6.0.0 major 昇格時に併合検討する。

## v5.2.0 で追加された概念

### 5 次元論（D1〜D5）の確立

dialog-harness は従来「メタスキル」「ユーザーハーネス」等の語彙で自身を語ってきたが、
個別の検証機構（5 層検出スタック / crosscut-verifier-drift / §7.4 自己検証等）が
それぞれどの抽象階層を対象にしているかが暗黙のままだった。

PR #19 後の HANDOFF（DH 自己検証機構ブレスト、2026-04-29）と Council 合議
（invocation_id: council-2026-04-29T21:00:00Z-d4mtr1）を経て、5 次元論を確立する：

| 次元 | 名称 | 実体 |
|---|---|---|
| D1 | ソースコード | プロジェクト実装ファイル群 |
| D2 | 開発環境 | D1 の足場（package.json / vite.config / sensors / SPEC.md 等） |
| D3 | 配布 skill | 利用者プロジェクトに配置される `.claude/skills/` インスタンス |
| **D4** | **マスタ skill（メタスキル）** | **dialog-harness リポジトリ内 skill マスタ定義** |
| D5 | Meta モニタリング層 | D4 を外側から監視する人間（自動化禁止） |

機械可読命名は D-numbering（D1〜D5）を使用。思想文書では `meta-layer` / `meta-meta-layer`
等の階層形容詞を併走させる二重命名を採用（DH の二層性 = 仕様核 + 対話的成長領域 と整合）。

### D4 検査機構（harness-verifier）の独立配置

DH 本体は v5.1.0 まで D2 / D3 の検証機構を完備していたが、**D4 自身の整合性検査は不在**だった
（靴屋の靴問題）。フラクタル原則 P1 の自然な拡張として「規律の自己相似性」を導入し、
DH が自身に課す規律と同等の規律を自身に課す。

ただし D4 検査機構を `.claude/skills/` 配下の crosscut-* skill として実装すると
**自己言及パラドックス**（自身が壊れたら自身を検査できない循環）が生じる。
これを構造的に回避するため、**DH 本体と並列のリポジトリルート直下に独立配置**する：

```
dialog-harness/
├── .claude/skills/    # DH 本体（D4）
└── harness-verifier/  # D4 検査機構（独立）
```

### 自己言及パラドックスの構造的回避（D5 を人間で止める）

D4 検査機構（harness-verifier）の検査結果を **自動的に DH 本体へフィードバックする回路は意図的に作らない**。
そこを自動化すると、D4 と D5 の間に新たな自己言及ループが発生し、再びパラドックスに陥る。
D5（人間）は機械が代替できない判定者として最外殻に固定される。
これは Russell タイプ理論・Gödel 不完全性定理と同型の構造判断であり、
philosophy.md 第 6 条「人間 ≒ Council」原則とも整合する。

将来 v6.0.0 で major 昇格する際、philosophy.md 第 7 条「次元論と D4 の独立性」として
本体に組み込む候補（v5.2.0 では PHILOSOPHY.md に閉じる）。

## v5.1.0 で追加された概念

### L0 charter 達成可能性の確保

PR #19 テストレビュー（シナリオ「ケロぴの森」）で、L0（spec-architect）の charter「AI 自律駆動開発が可能な開発環境の構築」が達成されないまま L1 へ譲渡され得る状態が判明した。SPEC.md / DONT.md / REGIME.md のドキュメント生成だけが完了し、scaffold（package.json 等の実行可能ファイル）が一切生成されない状態でも、従来の L0 完了判定では PASS となっていた。

v5.1.0 はこの欠陥を「**完了基準の再定義**」と「**Pre-flight 必読化**」と「**実行可能性の機械チェック（§7.4）**」の 3 軸で解消する。L0 完了 = ドキュメント生成 + scaffold 実体 + smoke test + 自己検証 PASS。これを下回る状態で L1 譲渡することは原則違反として明文化された。

### Pre-flight 必読化（読まずに進行禁止）

従来の SKILL.md は「詳細は references/X.md を参照」という参照表現にとどまっていた。v5.1.0 では主要ステップ（§1.5 / §3.5 / §4 / §6 / §7）の冒頭に「**Pre-flight: 起動前に X を必読**」を 1 行ずつ追加した。これは spec §0 受け入れ基準 4 とリンクし、Pre-flight 充足は §7.4 で逐項チェックされる。

「参照」と「必読」の差は運用上致命的。AI が SKILL.md だけを読んで進む（references を読み飛ばす）パターンを排除する目的で、命令形 + 違反明記 + 自己検証チェック項目化、の 3 点セットで運用する。

### Scaffold checklist（stack 別の生成必須リスト）

dev-env-spec.md は「ファイル配置規則」（全 stack 共通の規約）を扱うが、stack 固有の必須生成ファイルリストと smoke test 手順は不在だった。v5.1.0 では references/scaffold-checklist.md を新設し、「v5.1.0 標準 stack = Vite + TypeScript + React + PWA」の必須生成ファイル 12 種と smoke test 4 コマンドを規定する。

将来 minor で stack 追加（Next.js / Vue / Astro / SvelteKit / 純 Node CLI 等）するための「将来拡張ポイント」も併記。stack 選択軸は ARC + dev_mode + チーム軸（v5.x で追加予定）と整合させる。

### §7.4 自己検証ステップ

L0 完了判定の機械チェック化。broken reference / scaffold smoke test / DONT 自己照合 / Pre-flight 充足 / 受け入れ基準充足の 5 項目をチェックボックス形式で配置。FAIL があれば §7（出力）に進まず原因解消する。shell script 雛形は配置せず、L0 が ls / grep / cat 等の手作業で確認する粒度に絞ることで、人間運用の前提（人間は手を動かさない）を破らない。

5 項目は §0 受け入れ基準 4 条件と一対一に対応するように設計され、「自己検証で何をチェックすべきか」の暗黙仕様を明示化した。

## v5.0.0 で追加された概念

### dev_mode 軸

GitHub 連携前提の自律駆動開発を 3 段階で表現する軸。

| モード | 位置づけ |
|---|---|
| local_only | GitHub 不使用。DH ベースのみで完結 |
| github_assisted | GitHub Issue / PR は使うが、自動化は限定的。人間レビュー必須 |
| github_autonomous | claude-code-action 経由で自律実装、CTL 育成と連動して段階的に人間関与を縮小 |

理想形は github_autonomous + CTL-3 で「人間関与は L0 のみ」。

### CTL 連動の段階的自動化

仕様 1〜4 すべてに CTL-0/1/2/3 の動作分岐を組み込み、Council 判定の蓄積に応じて自動化度が上がる仕組み。CTL 昇格は量（判定件数）+ 質（一致率・override 率）のハイブリッド判定。退行（CTL 降格）も儀式で扱う。

### crosscut- prefix（Level A 第二の命名規則）

`layerN-` prefix と並列の Level A 識別子。3 層（L0/L1/L2）のいずれにも属さず、全層から呼ばれる横断機構を示す。

| Level A prefix | 意味 |
|---|---|
| `layerN-` | 特定 Layer 専属 skill |
| `crosscut-` | 全 Layer 横断 skill |

### 4 仕様（GitHub 連携の方法論化）

| 仕様 | skill | 役割 |
|---|---|---|
| 仕様 1 | crosscut-issue-dispatcher | SPEC/ADR 差分から Issue 生成 |
| 仕様 2 | crosscut-issue-implementer | Issue → CC 実装起動（claude-code-action 経由可） |
| 仕様 3 | crosscut-verifier-drift / -philosophy | drift 検知 + 思想検証（philosophy は v5.1.0 placeholder） |
| 仕様 4 | crosscut-feedback-loop | 検証結果を設計層・実装層・L0 に還流 |

4 仕様は同型構造（CTL 連動 / mode 別動作 / 還流ポイント明示）を持ち、5 本柱 P1（フラクタル原則）を skill レベルで発現する。
