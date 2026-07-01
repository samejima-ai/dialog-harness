# Upgrade Spec v6.1.0 — CTL 記録経路の再設計（分断の解消・単一ソース化）

**リリース予定**: TBD（本文書は設計方針の結晶化。実装は別 PR）
**バージョン昇格**: minor（v6.0.1 → v6.1.0、後方互換維持）
**起点**: ユーザー（ひでさん）指摘「今まで多くの council 判定をしてきてデータがないということはこの CTL が機能していない」→ 調査で記録経路の分断が判明 →「DH をアップデートして他のプロジェクトでも CTL が機能するように再設計・修正する」
**境界**: 本改修は **L-FULL / C カテゴリ**（記録経路の話であり、委譲境界 SPEC = `delegation-boundary.md` / `philosophy.md` / `auto-merge-boundary.md` には一切触れない）。ガバナンス検証済み（§5）。
**Council 諮問**: `council-2026-07-01T13:04:40Z-ctlrec1`（business / conception / unanimous / 案A修正 / weighted_score 7.37 / judgment_confidence 0.67、agreed_recommended）

---

## §1 問題（調査で確定した根本原因）

CTL（Council Trust Level）は「Council 発動 → 事後評価 → stats 再計算 → CTL 算出」のループで横断蓄積データから決定論的に算出される。ところが本番環境（DH 自身の `~/.claude/council-data/`）で **CTL が CTL-0 に張り付いたまま昇格しない**。約53回 Council を発動してきたのに CTL 用記録は1件だった。原因は3層：

### ① 記録の自動発火機構が存在しない（最重要）

`crosscut-council/SKILL.md` §CTL 記録は「**発動のたびに自動で**」「省略してはならない」と規定するが、`council-ctl.py record` を叩く実行主体が**手順書テキストのみ**。CC（Claude Code）に hooks 設定はゼロで、record は「Council を回す AI が手順を思い出して手で叩くか」に完全依存していた。

- COUNCIL-LOG.md（project-scope, append-only）には **53件が確実に追記**されている（`history/COUNCIL-LOG.md`）。
- 一方 user-scope `~/.claude/council-data/invocations/` には **1件**しか流れていない。
- 「書く側の経路」が二重化し、片方（CTL 用）だけ空になった。

### ② `decision_category`（CTL 必須キー）の供給が弱い

CTL 統計は `decision_category`（C1〜C4）でカテゴリ分けする（`ctl-calculation.md` §2）。ところが COUNCIL-LOG 53件のうち正式フィールドとしての `decision_category` は **2件のみ**。重み配分軸の `category`（conception/judgment/operation 等）は49件あるのに、CTL 軸だけ欠落。SKILL.md 自身が「decision_category が C1〜C4 以外だと warn skip され統計から静かに落ちる（CTL が実態より低く出る）」と警告している、まさにその状態。

### ③ 二重管理が事故の温床

`category`（重み軸）と `decision_category`（CTL 軸）は `consensus-protocol.md` §311-324 で**直交した別概念**と明記されている。両者を別々に手入力する構造ゆえ、片方だけ埋まる事故が構造的に起きる。

### 系譜：反復する同型欠陥

`history/ARCH-DECISIONS.md` **AD-004**（v4.2）で「CTL システムは判定ロジックは存在したが、各 skill の**動作分岐**に組み込まれていなかった」という同型欠陥が一度認識・修正された。だが *記録経路*（record の発火）は AD-004 の射程外で手つかずのまま残った。**「機構を作るが実行経路に接続しない」**という DH の反復パターン。本改修はこの再発自体を潰すことを設計目標に含める。

---

## §2 設計方針（Council 修正後の案A）

### 2.1 記録経路: COUNCIL-LOG を単一情報源とし同期で council-data を導出（案A）

- `history/COUNCIL-LOG.md`（全発動で確実に追記される append-only ログ）を **CTL の単一情報源**とする。
- 同期スクリプトが COUNCIL-LOG を読み、`~/.claude/council-data/invocations/` の各 invocation JSON を導出する。
- 二重書きを廃し、情報純度（単一ソース原則）を回復する。
- 過去53件のバックフィルも同一経路で可能（COUNCIL-LOG を読むだけの導出なので **可逆** — council-data を消して再同期できる）。

**却下した代替案**:
- **案B（hook-observer 経由発火）**: CC hooks は PreToolUse/PostToolUse の **tool 単位発火**で、「Council スキル発動」という抽象イベントに口がない。record を確実発火できず前提から破綻（開発者 conf 0.82 が最強く指摘）。
- **案C（両方）**: 破綻した案B を主経路の上に冗長追加するだけ。YAGNI・保守コスト増で、まさに反復欠陥を別形で温存。

### 2.2 `decision_category` は機械導出しない（Council が当初案Aから覆した核心）

当初案Aは「COUNCIL-LOG の `category` から `decision_category` を**導出規則で埋める**」を含んでいたが、**Council 全会一致で却下**された。3ペルソナが独立に同一結論へ収束：

- **開発者**: `category`（閾値軸）と `decision_category`（H/C 委譲軸）は consensus-protocol.md §311-324 で直交と明記。写像は**数学的に非全射**で損失なく作れない。
- **哲学者**（重み5・最重）: 機械導出は直交軸を折り畳み、**近似を真の分類と偽装**する。「導出で穴を塞ぐと記録は満ちるが学習は死ぬ」。CTL の存在理由（委譲精度の学習）を空洞化させる。
- **経営者**: 導出規則の精度が低いと CTL 算出の信頼性を毀損する。

**採用する設計**:
- 同期時、`decision_category` が COUNCIL-LOG に明示されていなければ **`null` で載せる**。
- `council-ctl.py` の既存 `_compute_stats`（`scripts/council-ctl.py:332-335`）は `status`/`decision_category` が不正なら **null-skip** する。null 保持はこの挙動に委ねられ、「満ちているが意味は空」な統計汚染を避ける。
- 過去53件は C1〜C4 空のまま。**必要分のみ人手で分類**して COUNCIL-LOG 側に追記する（単一ソースを保つ規律）。

### 2.3 将来分は Phase 0 で `decision_category` を必須ゲート化

- Council 発動フローの Phase 0（Pre-Check）で `decision_category`（C1〜C4 / H1〜H4）判定を**必須**にし、COUNCIL-LOG に必ず書く。
- これにより今後の発動は CTL 軸が確実に埋まる。②の欠落を構造的に予防。

### 2.4 事後評価を「問う契機」として振り返り儀式に経路化（哲学者の第3の道・必須）

- CTL 昇格の律速は record ではなく**事後評価**（agreement_rate を作る唯一の燃料）。記録が満ちても事後評価が回らねば昇格しない（経営者懸念）。
- 哲学者の第3の道を advisory でなく**必須**として組み込む: Council 発動の一定間隔ごとに人間へ「この委譲は妥当だったか」を問う軽量な事後レビューを経路化する。CTL の値でなく「問う契機」を機構が保証する。
- 実現は既存の振り返り儀式 **F1（軽量）/ F2（標準）/ F3（完全）**（`ritual-protocol.md`）に **CTL 事後評価ステップを接続**する形。`council-ctl.py pending` を儀式内で列挙し、未評価判定を人間に問う。

### 2.4b 記録経路の単一ソース化（案A・dedup、Council `council-2026-07-01T-ctldedup`）

実装中に判明: 同期版 invocation と、同一 Council 発動を指す手動 record（別採番）が
council-data に併存し**二重計上**される（本番同期で C2 count が水増しと判明）。これは
「単一情報源は COUNCIL-LOG」と宣言しながら手動 record を独立ストアとして温存した矛盾で、
v6.1.0 が葬った二重書き経路の再来（哲学者指摘）。Council 全会一致（案A / 0.77）で解消：

- **手動 record 保護を撤廃**: COUNCIL-LOG に対応する invocation は同期で**常に上書き**する。
- **`--prune`**: COUNCIL-LOG に対応しない孤児（別採番の手動 record 等）を掃除する。儀式の
  主経路コマンドを `sync --prune --recompute` にして毎回二重計上を予防。
- **手動 record を「COUNCIL-LOG 即時追記トリガ」へ再定義**（哲学者の第3の道）: 手動 record を
  使う時は必ず COUNCIL-LOG にも追記する。追記すれば同期で正規版に一本化される。第二ストア化の
  抜け道（直接 JSON 書き）を SKILL に明文化して塞ぐ。
- 却下した案B（timestamp+topic 近似照合 dedupe）: topic_summary の 80 字トランケートで照合キーが
  脆く、統計に非決定性を持ち込むため（開発者 conf 0.82 が却下）。

### 2.5 反復欠陥の再発防止（同期の発火主体を明示接続）

- 同期スクリプトを作るだけでは①と同じ轍を踏む。**発火主体を実行経路に明示接続**する：
  - local: `git commit` 前後の hook、または L0 振り返り儀式の冒頭で同期を必ず走らせる。
  - 儀式（F1/F2/F3）起動時に「同期 → pending 列挙 → 事後評価を問う」を1つの手順として固定。
- 「機構 ⊃ 実行経路への接続」を受け入れ基準に含める（機構だけ作って終わらない）。

---

## §3 他プロジェクトでの CTL 機能化（本改修の主目的）

DH を配布した利用者プロジェクトでも CTL が機能するために：

- **council-data は user-scope**（`~/.claude/council-data/`）に閉じる（プライバシー・`ctl-calculation.md` §9）。プロジェクトを跨いで横断蓄積される設計は不変。
- **単一ソース = 各プロジェクトの COUNCIL-LOG**: 利用者プロジェクトでも Council 発動は COUNCIL-LOG（project-scope）に追記される。同期スクリプトがそれを読んで user-scope の council-data へ流す。
- **`council-ctl.py` が無い利用者プロジェクト**でも、SKILL.md §CTL 記録の「直接書き経路」（invocation JSON を直接書くフォールバック）は維持する。同期スクリプトはこの経路の**確実な実行主体**を提供する位置づけ。
- 結果、利用者プロジェクトは「Council を回す → 儀式で同期＋事後評価を問われる → CTL が育つ」ループに乗る。

---

## §4 実装スコープ（本文書 = 方針。実装は別 PR）

本 v6.1.0 spec は**設計方針の結晶化まで**。実装は後続 PR で以下を行う（見積り）：

| # | 実装項目 | 対象 | 委譲レベル |
|---|---|---|---|
| I-1 | 同期スクリプト新設（COUNCIL-LOG → council-data 導出、decision_category は null 保持） | `scripts/council-log-sync.py`（新規） | L-FULL |
| I-2 | 同期の発火主体を実行経路に接続 | hook 設定 or 儀式手順 | L-FULL |
| I-3 | Phase 0 で decision_category 必須ゲート化 | `crosscut-council/references/pre-check.md` / `output-format.md` | L-FULL（枠内 SPEC 改変） |
| I-4 | 振り返り儀式に CTL 事後評価ステップ接続 | `layer0-spec-architect/references/ritual-protocol.md` | L-FULL（枠内 SPEC 改変） |
| I-5 | 過去53件の必要分を人手分類してバックフィル | COUNCIL-LOG 追記 + 再同期 | L-GATE 相当（発話確認推奨・データ一括生成） |
| I-6 | SKILL.md §CTL 記録の「手順書依存」記述を「同期経路が保証」へ改訂 | `crosscut-council/SKILL.md` | L-FULL（枠内 SPEC 改変） |

**独立レビュー（C-3）**: I-3/I-4/I-6 は SPEC/DONT 改変を含むため `claude-review.yml`（独立コンテキスト sub_agent review）を必ず通す。

---

## §5 ガバナンス検証（v6.0.0 委譲境界との照合）

`delegation-boundary.md` の4委譲レベルに照合済み：

| 変更 | レベル | 判定 |
|---|---|---|
| 同期スクリプト / hook / `council-ctl.py` 改修 | **L-FULL** | コード・設定、revert 可能。全自律 ✅ |
| SKILL.md / pre-check.md / ritual-protocol.md の枠内改訂 | **L-FULL** | SPEC 通常改変（枠内）、PR diff で可視化・revert 可能 ✅ |
| 過去分バックフィル | **L-GATE 相当** | user-scope データ一括生成。可逆だが統計汚染リスクゆえ発話確認推奨 ⚠️ |
| `decision_category` の**定義**変更 | **L-FROZEN-PHIL** | **該当しない**（今回は定義不変、記録経路のみ） |

本改修は「何を人間が握るか」の線引き（委譲境界 SPEC）に**一切触れない**。したがって H カテゴリではなく C カテゴリとして起票してよい（§Council 諮問で確定）。第2条（計算的解決優先）とも整合 — 決定論で導出できる部分を確実に記録する方向。

---

## §6 後方互換性

- `council-ctl.py` の CTL 算出ロジック（`calculate_ctl` / `_compute_stats`）は**不変**。同期スクリプトはその入力（invocations/）を埋めるだけ。
- 既存の invocation JSON（手動 record 分）はそのまま有効。同期はそれに追加する形。
- `decision_category` null のエントリは既存 null-skip 挙動で統計から除外される（既存挙動、破壊なし）。
- 利用者プロジェクトで同期スクリプト不在でも、SKILL.md の直接書き経路フォールバックは維持され従来通り動作。

---

## §7 evaluation（本改修の効果測定）

実装後、以下で機能回復を確認する：

- `council-ctl.py status` で `total_invocations` が同期後に COUNCIL-LOG 件数に追随すること。
- Phase 0 ゲート化以降の新規発動で `decision_category` が非 null で記録されること。
- 振り返り儀式で `pending` が列挙され、事後評価が実施されること（律速段階が回る）。
- 一定期間後、いずれかの decision_category で count≥10 & rate≥0.90 を満たし **CTL-1 へ昇格**すること（機能回復の最終指標）。
