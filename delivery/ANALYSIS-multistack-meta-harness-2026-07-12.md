# DH 汎用展開（マルチスタック）メタハーネス構成要素解析 — 現在の評価と今後の方針

- 日付: 2026-07-12
- 対象版: DH v6.2.0（master 77faa7c 時点）
- 種別: 解析レポート（タイプ A: 仕様レビュー献上 / SPEC 改変なし・記録のみ）
- 依頼: 「DH を汎用展開（マルチスタック開発環境）AI 自律駆動開発環境構築メタハーネスとして必要な構成要素を解析し、現在の評価と今後の方針を整理する。GAS / Google エコシステム / Android 端末 / MacroDroid 等の特殊環境も想定に含める」

---

## 1. 必要構成要素の解析 — 「メタハーネスに必要な 9 要素」と DH の実装対応

汎用マルチスタック AI 自律駆動開発環境を「対話から生成する」メタハーネスに必要な構成要素を 9 つに分解し、DH の現行実装を対応づける。

| # | 必要要素 | DH の実装 | 一次情報源 |
|---|---|---|---|
| A | **仕様生成層**（対話→SPEC/DONT/REGIME） | L0 四兄弟: spec-architect（新規+継続）/ onboarding（後付け 1 回限り）/ archeo-architect（意図復元）/ reindex-librarian（代謝） | `.claude/skills/layer0-*` |
| B | **スタック抽象化層** | scaffold-checklist 10 stack カタログ + A-3 stack 中立性原則（agent 本体不変・stack 差異はデータ側に閉じる） | `layer0-spec-architect/references/scaffold-checklist.md` / `dev-env-spec.md:39` |
| C | **実装実行層** | L1 autonomous-dev + independent-reviewer / L2 orchestrator + integration-verifier（L2 閾値 10 項目で発動） | `layer1-*` / `layer2-*` / `regime-assessment.md:240-257` |
| D | **判断機構** | Council 3 ペルソナ独立並列 × 加重判定（judgment であって decision でない・minority_opinion 必須保持）+ CTL 0〜3 による自律範囲の動的委譲 | `crosscut-council` / `ctl-calculation.md` / `scripts/council-ctl.py` |
| E | **検証層** | 5 層検出スタック（計算 30%→E2E 20%→IC 10%→推論 7%→Vision 3%）+ verifier-drift（CTL≥1）+ verifier-philosophy（placeholder）+ harness-verifier（D4 自己検査・非配布） | `inferential-sensor-v2.md` / `harness-verifier/` |
| F | **ガバナンス（憲法）** | philosophy 9 条。核は第 9 条「可逆性ベース委譲境界」（L-FULL / L-GATE / L-FROZEN-PHIL / L-FROZEN-META）+ 第 6 条「人間 ≒ Council 原則」内の不変条項「憲法の自己改訂禁止」 | `layer0-spec-architect/references/philosophy.md` |
| G | **配布・更新機構** | dh-manifest.yml（overwrite/merge/redeploy/never_touch の 4 分類）+ UPDATE.md 手順書 + templates placeholder 置換（autonomous-drive skill が deploy） | `dh-manifest.yml` / `UPDATE.md` / `placeholder-spec.md` |
| H | **CI / 自動駆動** | 5 workflow: harness-verify（+template-sync gate）/ claude-review（4 フェーズ Council レビュー）/ gemini-review（異ベンダー独立軸）/ auto-merge（opt-out・境界 SPEC 準拠）/ issue-pickup（Issue→AI 実装→PR） | `.github/workflows/` |
| I | **観測・学習層** | hooks 6 event 観測（warn のみ・block しない）+ continuous-learning（候補出力のみ・自動 promote 禁止）+ 情報代謝（HOT/WARM/COLD・購読量上限が最上位不変条件） | `.claude/hooks.json` / `crosscut-hook-observer` / `history/.metabolism-config.yml` |

**設計の一貫原理**: 全機構が「検出のみ・自動修正しない」「一方向依存」「人間が最外殻 D5・最終承認」に収斂。マルチスタック性は B の seam（縫い目）設計 — **stack 固有記述を scaffold-checklist の 1 節に隔離し、agent 本体には言語/FW 名を書かない** — で担保される。新 stack 追加が「データ 1 節の追加」で完結する構造は、メタハーネスとして最も価値の高い設計判断。

### seam（拡張点）の所在一覧

1. **stack 固有 → scaffold-checklist.md**（唯一の stack 記述格納場所）
2. **バックエンド追加層**（Supabase ローカル開発プロトコル。stack 直交・置換でなく追加）
3. **workflow templates + placeholder 7 種**（`${ALLOWED_AUTHORS}` 等 → autonomous-drive が展開）
4. **UI/非 UI 判定と DESIGN.md 連携**（Expo の Maestro/Detox「読み替え規約」が非 Web 検証手段の前例）
5. **personas / rules / rituals**（presentation・RL の差替層。`.dh/` override 規約）
6. **モード軸**: M1/M2/L2 × dev_mode（local_only/github_assisted/autonomous）× CTL 0-3 × autonomous_scope

---

## 2. 現在の評価

### 2.1 強み（メタハーネスとして完成度が高い部分）

| 評価 | 領域 | 根拠 |
|---|---|---|
| ◎ | ガバナンス理論 | 可逆性を唯一の委譲判定軸とする第 9 条は、自律度とガバナンスの両立を「領域の格」でなく原理で解いた。憲法 3 文書の自己改訂禁止（起票ゲート）で再帰を遮断 |
| ◎ | 判断機構 | Council の独立並列 + 加重判定 + minority_opinion 保持 + CTL 昇格ループは、判断の外部化としてほぼ完結。claude-review の tier 段階昇格（haiku→sonnet→opus）でコスト設計も済んでいる |
| ◎ | 情報代謝 | 「購読量上限 ≠ ディスク上限」の分離により長期運用の context スケーラビリティを構造的に解決。実運用実績あり（2026-06 に −8,900 行超の結晶化・排泄） |
| ○ | スタック抽象化 | A-3 中立性 + 10 stack カタログ + 未収載時プロトコル（delivery/ 一時チェックリスト→観測→昇格）。ただしカバレッジは非対称（後述） |
| ○ | 検証層 | 5 層スタック + 二真実源 drift の CI gate 化（G-004 で実 drift を検出→修復した実績）。自己検査（harness-verifier）の物理分離も理論整合 |
| △ | 配布・更新 | boundary は機械可読化済みだが実行系が未整備（後述、最弱領域） |

### 2.2 弱点（深刻度順）

1. **配布ストーリーが最弱リンク**。インストーラ不在（README の手動 `cp -r`）、リリースタグ 0 個（PIN が commit SHA 手選び）、placeholder 置換が LLM の手順実行（決定論スクリプト不在・YAML 破壊リスク）、`crosscut-dh-self-update` は v5.22.0 申し送りのまま未実装。**「ハーネスを生み出すハーネス」の生成物搬出経路が、DH 自身の規律（決定論優先・Shift Left）を満たしていない**。
2. **第三の真実源が無検証**。`check_template_sync.py` は本体↔template の二真実源のみ検証。deploy 済み利用者プロジェクト側の workflows / review agents との drift は検知機構ゼロ（known-gaps G-003 が自認）。利用者が増えるほど静かに崩れる構造。
3. **manifest 自身の drift**。`min_same_major_from: "5.0.0"` のまま VERSION=6.2.0。v5→v6 が major 跨ぎである事実が manifest に反映されていない。
4. **template 2 系統の重複**。`templates/github-workflows/*.template`（placeholder 方式）と `templates/.github/workflows/*.yml`（mode/CTL ヘッダ方式）で `auto-merge.yml` / `claude-review.yml` が名前重複し、sync 検証は前者のみ。正典がどちらか manifest 上不明。
5. **stack カバレッジの非対称**。rich な pitfalls 記述は Vite 標準と Expo のみ。他 8 stack は「ファイル表 + smoke 1 段落」の thin 記述（陳腐化回避の意図的判断だが、L1 の実装品質は実質 pitfalls の厚みに律速される）。hosted DB も Supabase のみ。
6. **「機構は作るが実行経路に繋がない」反復パターン**。upgrade-spec-v6.1.0 が自己診断済み（CTL 発動 53 回に対し記録 1 件）。同型リスクが redeploy の手動性・版数の手動記入に通底。
7. **never_touch ガード未実装**。破壊的 `rm -rf` 更新の安全網が人間の手順遵守に依存（v5.22.0 申し送り）。
8. **実行環境前提の暗黙固定**。10 stack すべてが「ローカル CLI で決定論 smoke が回る + GitHub Actions が実行環境に届く」を暗黙前提とする。この前提を破る環境（§3）への軸が存在しない。

### 2.3 総合評価

**「対話→ハーネス生成→自律駆動」の中核ループ（A〜F, H, I）は理論・実装ともに高水準で、自己適用（dog-food）の実績も伴う。一方、メタハーネスの「メタ」たる所以＝他プロジェクトへの汎用展開（G）だけが手工業段階に留まっており、ここが v6.x 系の主戦場になる**。マルチスタック対応は seam 設計が正しいため、課題は「軸の追加」（§3 runtime_profile）と「データの厚み」（pitfalls 還流）に帰着する。

---

## 3. 特殊環境への拡張解析 — GAS / Google エコシステム / Android / MacroDroid

現行 DH にこれらへの言及はほぼゼロ（Android は Expo 文脈のみ）。純粋な未踏領域だが、scaffold-checklist:327-329 の「stack 未収載時プロトコル」が正規の入口として既に定義されている。

### 3.0 何が崩れるか — 暗黙前提の破れ 3 点

| 暗黙前提 | 破る環境 | 影響 |
|---|---|---|
| 決定論的ローカル smoke test が回る | GAS（ローカルランタイム無）/ MacroDroid（実機必須） | scaffold-checklist の smoke 章が定義不能 |
| 成果物は git 中心で版管理できる | MacroDroid（アプリ内資産。export JSON 経由でのみ版管理可） | drift 検証・auto-merge の対象が「実体の写し」になる |
| GitHub Actions CI が実行環境に届く | GAS（要 OAuth）/ Android 実機 / MacroDroid | 5 層検出スタックの第 2 層（E2E）チャネル欠落、auto-merge の SUCCESS 条件が痩せる |

### 3.1 GAS（Google Apps Script）— 適合度: 中〜高

clasp によって git 中心開発が成立するため、**正規 stack 化が最も現実的**。

- **必須生成ファイル案**: `.clasp.json`（dev script ID）/ `appsscript.json` / `src/`（TypeScript）/ `package.json`（clasp, @types/google-apps-script, esbuild or tsc）/ `.claspignore` / `.gitignore`（`.clasprc.json` 必須除外 = 認証情報）
- **smoke test の再定義**: 第 1 層（tsc + lint + **GAS API をモック分離した純粋ロジックの unit test**）はローカルで決定論的に成立。「push 検証」は `clasp push` → dev 用 script への配置成功を smoke とする（実行検証は E2E 側へ送る）
- **層分離規約が必須**: 「GAS グローバル API に触る薄い adapter 層」と「純粋ロジック層」の分離を最低要件に置く。これが無いと第 1 層検出率 30% が確保できない
- **E2E**: doGet/doPost の Web アプリなら Playwright がそのまま届く（既存 5 層スタックと接続可能）。Sheets 連携はテスト専用スプレッドシート fixture
- **CI**: OAuth refresh token（`.clasprc.json` 相当）を Repository Secret 化すれば Actions から clasp 可。「人間がやる範囲」表に **GCP project / OAuth 同意 / Script Properties 設定** を追加する必要
- **DONT 罠候補**: 6 分実行制限 / quota / simple trigger（onEdit 等）の権限制約 / Script Properties にすべき値のハードコード / トリガー重複登録の非冪等性 / V8 と Rhino の差異

### 3.2 Google エコシステム（Sheets / Drive / Calendar をバックエンドとする構成）— 適合度: 高

Supabase ローカル開発層（`supabase-local-dev.md`）と**同型の「追加バックエンド層」**として設計可能。stack を置換せず直交追加する前例がそのまま使える。

- `google-workspace-dev.md` 相当の追加層: 認証方式（OAuth / service account）の選定規約、テスト用 fixture（専用シート/フォルダ）、本番データ保護規約（Supabase 層の「本番消失 NG」規約と同型）
- **MCP との親和性が既に高い**: Claude Code セッションから Google Drive / Calendar MCP を直接操作できるため、AI の知覚チャネル（E2E 代替）として「実データ読み取り検証」が構成可能。これは他 BaaS に無い優位
- 人間専管 secrets: OAuth 同意画面 / API 有効化 / service account 鍵発行

### 3.3 Android 端末 / MacroDroid — 適合度: 低〜中（device-bound 領域）

- **MacroDroid**: 成果物 = macro export（JSON）。開発ループは「AI が JSON を生成・静的検証（schema/制約 lint = 第 1 層）→ git 管理 → **実機 import は人間**（P 責務の新形態: 配置作業）→ 実機動作確認は人間 or テレメトリ」
- **テレメトリ還流の設計余地**: MacroDroid の HTTP Request action / webhook trigger を使い、実行ログを GAS endpoint や Sheets に送る「観測チャネル」を harness 側で scaffold できる。これにより第 5 層（人間 100%）から第 3 層相当（計測ベース）へ部分的に引き下げ可能
- **Android 一般**（Expo 以外のネイティブ/Termux 系）: 実機 E2E は Maestro 読み替え（Expo 節の前例を流用）。adb 接続前提の smoke は「device-bound」プロファイルとして要求水準を明示的に緩和する
- **可逆性判定（第 9 条）との整合が良い**: マクロ import は revert 可能な可逆操作なので L-FULL 側に置ける。実機に不可逆な副作用を持つ操作（通知送信・API 発火を伴うマクロの有効化）だけ L-GATE。既存の委譲境界理論がそのまま適用できる
- 現実的な運用モード: M1（自己検証のみ）+ 出力後修正モデル。M2 の independent-reviewer は静的検証範囲に限定

### 3.4 統合提案 — `runtime_profile` 軸の新設

個別 stack 追加より先に、**REGIME.md に実行環境プロファイル軸を新設する**のが構造的な解になる。stack 軸（言語/FW）と直交する第 2 軸として:

| profile | 定義 | smoke 要求 | E2E チャネル | 例 |
|---|---|---|---|---|
| `local-reproducible` | ローカル CLI で全再現可 | 現行どおり必須 | Playwright 等 | 既存 10 stack |
| `cloud-managed` | 実行環境がマネージドクラウド | 第 1 層 + push 成功まで | HTTP 経由 or MCP 読み取り | GAS, Workspace 連携 |
| `device-bound` | 実機でのみ実行可 | 静的検証のみ必須 | テレメトリ or 人間 | MacroDroid, ネイティブ実機 |

これは Expo が導入した「DESIGN.md 読み替え規約」「決定論 smoke サブセット」の**一般化**であり、DH の既存判断（stack 差異はデータ側・要求水準の読み替えは明文規約で）と一貫する。smoke/E2E/CI/auto-merge SUCCESS 条件の要求水準を profile で読み替えることで、5 層検出スタックの目標解決率も profile 別に再配分できる（device-bound では第 1 層比重を上げ、第 5 層の人間関与を明示的に予算化する）。

---

## 4. 今後の方針（優先度付き）

DH の統治規約に従い、SPEC 改変を伴う項目は L0 spec-architect 経由（+必要に応じ Council 諮問）、stack カタログ昇格は第 8 条 3 段階モデル（観測→候補化→人間承認）を前提とする。

### P0 — 配布健全化（v6.x minor 群・最優先）

最弱リンクの解消。すべて既存申し送りの実行であり新規論点が少ない。

1. `dh-manifest.yml` の major 跨ぎ反映（`min_same_major_from` 更新 + v6 系 upgrade-spec への導線）— 軽微・即時
2. template 2 系統の正典整理（重複名の解消 or manifest への系統宣言 + `check_template_sync.py` の対象拡張）
3. リリースタグ運用の開始（SHA 手選び PIN の廃止）
4. placeholder 置換の決定論スクリプト化（LLM 手順実行 → 検証可能なツールへ。第 2 条「計算的解決を推論より優先」の自己適用）
5. `crosscut-dh-self-update` 実装 + never_touch 機械ガード（v5.22.0 申し送りの回収）

### P1 — 展開先 drift 検知（第三真実源問題）

deploy 済みプロジェクト側に「DH 版数 + 配置物 hash」を記録する軽量レジストリ（REGIME.md 追記で足りる）を置き、update 時に差分検出する。G-003 の構造的解消。利用者が増える前に着手する価値が最も高い。

### P2 — 特殊環境対応（本レポート §3）

1. **`runtime_profile` 軸の SPEC 化**（L0 起動・conception カテゴリとして Council 諮問が妥当）— 個別 stack より先
2. **GAS stack の一時チェックリスト起こし**（delivery/ 配下・未収載時プロトコル準拠）→ 実プロジェクト 1 件で dog-food → カタログ昇格判定
3. **`google-workspace-dev.md` 追加バックエンド層**（Supabase 層と同型設計）
4. **MacroDroid は観測温存から開始**: device-bound profile の試金石として、テレメトリ還流（webhook→Sheets/GAS）の観測チャネル設計を 1 件試行してから規約化（N=1 帰納の罠は Issue #70 と同じ扱い）

### P3 — stack カタログの厚み（継続・還流駆動）

thin 8 stack への pitfalls 充実は実プロジェクト retro 還流を待つのが DH 流（cookpato A1-A5 前例）。先回りで書かない。claude-world 等の外部観測吸収（#155, #158 前例）で補完する。

### 判断が必要な論点（人間 P1/P2 マター）

- `runtime_profile` 軸新設の採否と粒度（3 値で足りるか）
- GAS を「11 番目の正規 stack」に据える意思の有無（dog-food 先プロジェクトの有無に依存）
- リリースタグ運用の開始タイミング（P0-3。配布利用者が現れる前が損益分岐）

---

## 付録: 調査ソース

- スタック抽象化: `layer0-spec-architect/references/scaffold-checklist.md` / `regime-assessment.md` / `dev-env-spec.md`
- 配布機構: `dh-manifest.yml` / `UPDATE.md` / `crosscut-autonomous-drive/`（placeholder-spec / auto-merge-boundary / known-gaps）/ `scripts/check_template_sync.py`
- 検証・ガバナンス: `harness-verifier/`（PHILOSOPHY / BOUNDARY / HUMAN-PROTOCOL）/ `.github/workflows/` 5 本 / `philosophy.md` 9 条 / `crosscut-council` + `ctl-calculation.md`
- 履歴・意図: `history/INTENT.md` / `history/SUMMARY.md` / `dh-upgrades/`
