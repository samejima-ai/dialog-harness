# E2E 構築ベストプラクティス — AI 駆動開発の文脈（v5.23.0 追加）

AI 駆動開発における E2E テストの「構築」の正本。
**「どこに置き誰が回すか」**（5層スタック第2層・L2 Test Agents）は別ファイルが原典で、本ファイルは
**「堅牢な E2E をどう"構築"するか」** を担う。哲学的背景は
`../../layer0-spec-architect/references/philosophy.md` §2（Shift Left）/ §3（情報純度）/ §6（観測性統一）。

## 位置づけ（原典 / 参照宣言）

- **5層スタック第2層の原典**: `./inferential-sensor-v2.md` §第2層（E2E の位置・解決率・前提）
- **L2 配下の Test Agents 原典**: `../../layer2-orchestrator/references/e2e-integration.md`
- **本ファイルの責務**: 上記が前提とする「個々の E2E をどう書くと壊れにくく・AI の知覚器官として機能するか」の構築規律
- **C5 対話（テスト oracle 言語化）の原典**: `../../layer0-spec-architect/references/test-oracle-dialog.md`（本ファイルの相 B 母集団を L0 で確定する）

本ファイルは L1 が M1/M2 で E2E を書くときの主参照であり、L2 の Generator / Healer Agent も構築規律として参照する。

---

## 1. 二相分離 ★一次概念

AI 駆動開発の E2E は、目的の異なる **2 つの相** に明示的に分ける。混同するとスイートが肥大し、
flaky と保守負荷で自律ループの信号純度が落ちる。

| | 相 A: **in-loop 検証器** | 相 B: **SPEC 由来の耐久資産** |
|---|---|---|
| 目的 | AI が自己修正するための知覚・検証 | 次サイクル / 将来への回帰・契約 |
| 消費者 | 開発サイクル中の L1 自身（5層スタック自己検証） | 次の振り返り儀式・drift-verifier・P3 人間 |
| 寿命 | サイクル内で消費。cycle 後に破棄/退避も可 | 永続。idempotent・命名規律・Quarantine 管理 |
| artifact | リッチ・一時的（Trace/動画/network/console） | 安定・最小・SPEC 追跡可能 |
| 耐久性の根拠 | 不要（使い捨て前提） | **SPEC priority 由来**（critical journey の実行可能投影） |

### なぜ二相に分けるか

人間開発では「テスト = 未来の人間（文脈喪失者）が安全にリファクタするための記憶代替」。
DH では次のエージェントが SPEC + history から毎回**文脈を再構成**するため、耐久テスト（相 B）の役割は
「記憶代替」から「**SPEC とコードが今も一致している実行可能契約**」へシフトする。
これは静的 drift 検出（`../../crosscut-verifier-drift/SKILL.md`）の **runtime 補完**にあたる。

---

## 2. E2E は「AI の知覚器官」である（最重要原理）

人間 dev は実行中アプリを**自分の目で見て手で触る**。AI にはその経路が無い。
∴ E2E + artifact + Vision（第5層）は、AI が世界を知覚する**唯一の現実接地チャネル**。

> **AI は「見ると宣言したものしか見えない」**。
> ∴ AI の知覚の完成度は、AI 自身が書いた「何を検証するか」の宣言の精度に**律速される**。
> ∴ artifact 密度（Trace Viewer / 動画 / DOM スナップショット / network / console）は
> 人間以上に重要。AI の「デバッグ勘」はライブセッションでなく **artifact から再構成**されるため。

この原理が C5（テスト oracle の言語化）を哲学の本丸にする。詳細は test-oracle-dialog.md を参照。
UI プロジェクトでは **UI Baseline RL の B-ID**（`../../../../templates/rules/common/ui-baseline.rules.md`）が
そのまま「何を検証するか」宣言の出発点になる（B-04 状態 / B-15 即時応答 / B-16 Doherty / B-22 キーボード
= E2E 第2層、B-01/02 false affordance / B-21 コントラスト = Vision 第5層）。oracle 対応表は L0
`../../layer0-spec-architect/references/design-system-spec.md`「UI 相互作用層」を参照。

---

## 3. 相 A 構築規律（in-loop 知覚器）

### 3.1 App Actions と 実 UI の止揚

POM（Page Object Model）全廃ではなく、**操作の段階で分離**する：

- **arrange（前提状態への到達）= App Actions**: アプリ内部状態（store / window / API）を
  プログラムから直接セットし、不要な UI セットアップをバイパスする。速い＋内部状態を surface 化
  ＝ Shift Left（L0-2 ドメインモデル / L0-4 状態機械の明示化と整合）。
- **act / assert（検証対象本体）= 実 UI 経路**: 「使える」を Vision 第5層で判定するには UI を通す必要がある。
  検証したい操作そのものは UI でやる。

> 原則: **「準備は速く（App Actions）、検証は本物で（実 UI）」**。

### 3.2 動的同期（ハードコード待機の禁止）

`sleep` / `waitForTimeout` 等の固定時間待機は環境遅延に脆く flaky の主因。
**web-first assertions**（要素の可視性・ネットワーク idle まで自律再試行するアサーション）で
システム状態の準備完了とテストを動的に同期させる。固定 sleep は構築規律違反。

### 3.3 Fixture スコープ制御

- ワーカー間で一度だけ生成・共有する重いセットアップ = `scope: 'worker'`
- 各テストごとに完全分離・破棄するデータ = test スコープ

テスト間の状態共有は最大のアンチパターン。完全ステートレスにすることが**並列安全性の前提**
（`../../crosscut-issue-quality-gate/SKILL.md` の並列安全性軸と接続）。

### 3.4 冪等な合成データ（Synthetic Data）

本番 DB クローンはデータ状態変化で flaky を誘発する。テストごとに必要なデータを
API / factory から動的にシードし、終了時に確実にクリーンアップして環境を元に戻す**冪等性**を保証する。

### 3.5 device emulation（本番の見え方に寄せる）

実デバイス（実 iPhone 等のデバイスファーム）は DH 射程外。
代わりに **Playwright device descriptors**（viewport / deviceScaleFactor / userAgent / mobile）で
本番の見え方をエミュレートする。対象端末は DESIGN.md のレスポンシブ断面 / SPEC から導出し、
Vision 第5層判定をその端末解像度のスクショで回す
（`../../layer0-spec-architect/references/design-system-spec.md` §E2E 視覚検証と連結）。

### 3.6 artifact 密度（= AI の知覚器官の解像度）

失敗時に単なるログでなく **Trace Viewer 相当の完全タイムライン**（各ステップの DOM スナップショット・
network・console・動画）を必ず残す。ローカル再現できない原因の特定を AI が artifact から再構成するため。
相 A の artifact はリッチ・一時的でよい。

---

## 4. 相 B 耐久規律（SPEC 由来の耐久資産）

### 4.1 SPEC critical journey の実行可能投影（C1）

何を耐久 E2E に残すかは AI 裁量でなく **SPEC.md の critical-priority journey + L0-6 invariants
（Gherkin Happy/Sad/Evil）から導出**する（`../../layer0-spec-architect/references/subphase-l06-invariants.md`）。
母集団を SPEC に固定することで過剰生成と精度不足の両方を抑える。対象は L0 の C5 で人間と大枠合意する。

### 4.2 セレクタ規律

CSS クラス / XPath など実装詳細依存のセレクタは UI 変更で即破綻する。
**`data-testid` 等のテスト専用属性、またはアクセシビリティ（Role）ベースのセレクタ**を用いる。

### 4.3 ピラミッド本数天井（C3）

あらゆるシナリオを E2E でカバーすると保守コストが爆発する（アイスクリームコーン）。
E2E は critical journey に限定し、残りは unit / 統合 / 契約テストへ Shift-Left する。
SPEC Priority と連動した**本数の天井**を `sensors/e2e/` に置く（critical=全層 / standard=第1〜3層 /
cosmetic=第1層のみ。e2e-integration.md §優先度と実行範囲と一致）。

### 4.4 Quarantine（隔離運用）

flaky なテストがパイプラインをブロックしないよう自動で隔離し、アラート疲労を防ぐ。
隔離は「実装 / テスト / 仕様のどこかに構造歪み」のシグナルであり、一定期間内に修正または削除する
運用ルールを徹底する。隔離台帳は §6 の還流入力になる。

---

## 5. AI テスト精度対策（C1 / C2 / C3 と自己言及の罠）

AI が書くテストには 2 つの失敗様式があり、根に自己言及の罠がある：

- **(i) 過剰生成**: 低信号テスト大量生成 → スイート肥大・実装詳細ロックイン・リファクタ阻害 → C3 で抑える
- **(ii) 精度不足**: 「間違ったものを検証」or「重要を見落とす」→ 偽の安心 → C1 / C5 で母集団を SPEC に固定
- **(根) 自己言及の罠**: 実装した AI が・テストを書き・自分で「通った」と判定する。実装バイアスがテストにも乗る。
  これは第3条情報純度・independent-reviewer が実装コンテキストから隔離される理由と**同型**。

### C2 生成と判定の隔離

- L2: Planner / Generator / Reviewer Agent が既に分離（e2e-integration.md）。
- M1/M2: L1 単独のため同化リスク。**independent-reviewer がレビュー観点に「テスト自体の妥当性」**
  （テストが正しいものを見ているか・自己言及の罠に陥っていないか）を含める
  （`../../layer1-independent-reviewer/SKILL.md`）。

---

## 6. 接続地図（強制は将来 PR ── 本 PR では地図のみ）

以下は DH 既存機構との**接続点の宣言**。これらは §9「E2E 情報代謝サイクル」（v5.24.0）で正式機構として
本体化された（記録→蓄積→代謝→還流→結晶+排泄）。**強制連動（auto-merge.yml 改変）は依然 opt-in / 段階**で、
実 E2E 運用データが貯まってから閾値を較正する（e2e-integration.md の「実装は発動時」と同じ慎重さ）。

| 接続 | 効果 | 接続先 |
|---|---|---|
| flaky 率超過 → auto-merge 停止 + `human-review-needed` 自動付与 | 偽陽性 merge の構造的阻止 | `../../crosscut-autonomous-drive/references/auto-merge-boundary.md`（opt-in 領域） |
| Three-Strike（再試行上限）→ churn 打ち切り | 修正空回りの自己目的化を終端・token 燃焼停止 | `../../crosscut-issue-implementer/references/circuit-breaker-spec.md` / P4 暴走介入 |
| flaky 率の metric 化 → 合議の地盤 | 3 ペルソナが「この検証は信頼できるか」を同じ事実で見る | philosophy §6 観測性統一 |
| Quarantine 台帳 → 設計層へ還流 | 隔離＝構造歪みシグナルを L0/設計に逆流 | `../../crosscut-feedback-loop/references/feedback-protocol.md` |
| browser provenance → 観測性統一 | どの browser が生んだ事実かを Council が見られる | philosophy §6 |

> 設計原理: browser / 環境がばらつけば AI の知覚がばらつく。flaky は「事実のちらつき」であり、
> 第6条観測性統一（同じ事実を全ペルソナが見る）を直接侵食する。

---

## 7. 実行環境の統一（browser provenance pinning）

「どの browser が開くか」のばらつき（CC コンテナ上の同梱 chromium vs ローカル実 Chrome vs CI）は、
**AI の知覚器官そのもののばらつき**であり、flaky の主要因と第6条（観測性統一）の直結点。
統一手法は **「借りない・固定する・記録する」**：

| 原則 | 具体 |
|---|---|
| **借りない** | system Chrome（`channel:'chrome'`）を使わない → **Playwright 同梱の pinned chromium**。CC・ローカル・CI で同一バイナリ |
| **固定する①** | Playwright バージョンを lockfile で完全固定（同梱 browser は PW バージョンに紐づく） |
| **固定する②** | **公式 Playwright コンテナ**（`mcr.microsoft.com/playwright:vX.Y.Z`・バージョン一致）で実行 → フォント/レンダリングまで同一 → スクショ drift が消える＝ Vision 判定の地盤。headless 既定、headed は人間デバッグのみ opt-in（engine は同一） |
| **複数デバイス＝config 化** | `projects` に device descriptors のマトリクスとして宣言。ばらつきでなく宣言された設計にする（§3.5 と統合） |
| **記録する** | 各 run で browser version + engine + container digest を trace/report に刻む（observability・§6 接続地図） |

### カノニカルエンジン方針（v5.23.0 確定）

- **既定 = 同梱 chromium 単一**（本番の多くは Chrome/Edge 系エンジン）。コスト・flaky 面で AI 駆動に最適。
- **webkit / firefox は opt-in**: SPEC が「クロスブラウザが critical」と宣言した時のみ `projects` マトリクスを拡張。
  多エンジン既定にすると実行時間・保守・flaky コストが約 3 倍化し自律ループの信号純度が下がるため、既定にしない。

具体的な config（pinned chromium / projects マトリクス / 公式コンテナ runner / provenance 記録）は
`../../layer2-orchestrator/references/e2e-integration.md` の `sensors/e2e/config.ts` 規格を参照。

---

## 8. 人間開発との差（要約）

| 観点 | 人間開発 | AI 駆動開発（DH） |
|---|---|---|
| コスト曲線 | 書く=高 / 回す=安（1→N で human attention 償却） | 書く=ほぼ無料。希少資源は信号純度・保守・flaky |
| E2E の意味 | 念のためのリグレッション網 | **AI の知覚器官**（唯一の現実接地） |
| flaky | リトライで流せる煩わしさ | 自律ループの毒（偽陰性 churn / 偽陽性 merge） |
| テストの役割 | 未来の人間の記憶代替 | SPEC とコードの実行可能契約（drift の runtime 補完） |
| 何を残すか | 開発者の判断 | SPEC priority 由来（C1 / C5 で人間と大枠合意） |

---

## 9. E2E 情報代謝サイクル（v5.24.0 正式機構化）

E2E の実行結果・履歴を、**既存の情報代謝サイクルの新しい episodic ソース**として流す（専用サイクルは作らない）。
v5.23.0 で「温存」とした「テスト版 HOT/WARM/COLD」を、二相分離（§1）が COLD/HOT に直結することを根拠に
正式機構へ昇格させたもの。定義の正本は `../../layer0-reindex-librarian/references/metabolism-regime.md` §7、
project history への置き場は `../../layer0-spec-architect/references/history-layer-spec.md` §E2E-LOG.md、
還流は `../../crosscut-feedback-loop/references/feedback-protocol.md`。

### 還元先と稼働主体

- **既定 project 還元（D1-D3）**: run 履歴・flaky パターン・artifact は「このアプリ」に閉じた事実。
  正本は**利用者プロジェクトの REGIME.md `## 情報代謝設定`**。DH 本体は対面アプリを持たないため**稼働しない**（定義のみ）。

### サイクル 5 フェーズ（既存代謝フェーズへ E2E を流す）

| # | フェーズ | 内容 | 既存機構との関係 |
|---|---|---|---|
| ① | 記録 | run → 構造化レコード。相 A artifact = COLD 直行 / 要約 = `history/E2E-LOG.md` へ append | 新規（記録規律） |
| ② | 蓄積 | append-only・cursor 管理（全部はロードしない＝購読量保護） | 既存 cursor 流用 |
| ③ | 代謝 | cycle 境界で reindex が増分読み → flaky 反復＝罠候補 / 安定 journey＝RL 候補（council_gate） | reindex 増分対象に E2E-LOG 追加 |
| ④ | 還流 | flaky 率超過・Quarantine → feedback-loop（auto-merge 停止 / circuit-breaker / 設計層） | **teeth・opt-in/段階** |
| ⑤ | 結晶+排泄 | 罠/RL を HOT へ（Council ゲート）/ 抜け殻 run ログ → COLD（source pointer 付） | 既存 構築/分解代謝 |

①②⑤は既存代謝の流用、③は reindex の増分対象に E2E-LOG を足すだけ、**④だけが新規の teeth**。
④の強制連動（auto-merge.yml 改変）は **opt-in / 段階導入**（metabolism 設計自身が推奨する Dry-run 精神。
§6 接続地図で予告した teeth の本体化だが、実 E2E 運用データが貯まるまで閾値は固定しない）。

### tier 対応（再掲・正本は metabolism-regime §7）

- COLD: 相 A artifact・生 run ログ（retrievable・既定非ロード・disk 無制限 OK）
- WARM: `history/E2E-LOG.md` の run 要約列（reindex が増分摂取）
- HOT: flaky 罠（反-発火条件付）・安定 journey RL・provenance 観測・B-ID/C5 oracle 結晶（密度↑≠量↑）

> 北極星整合: E2E は毎 CI で大量データを生むが artifact は COLD 直行で既定ロードしない。
> 蒸留された flaky 罠だけが HOT に乗るので、履歴が無限に貯まっても購読量は膨らまない。

## 10. 温存（将来候補・本 PR では実装しない）

- **mutation 的メタテスト（C4）**: AI が書いたテストが本当に bug を捕まえるかを変異注入で測る。重いため温存。
- **④ teeth の強制化**: flaky 率閾値による auto-merge 自動停止の**強制**連動は opt-in 止まり。
  実 E2E 運用データで閾値を較正してから次 PR で強制化を再判定（Dry-run → 本番昇格の代謝精神）。
