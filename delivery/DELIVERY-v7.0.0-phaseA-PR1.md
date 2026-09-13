# DELIVERY.md — upgrade-spec v7.0.0 Phase A / PR-1

## ステータス: 完了（PR-1 の範囲）/ Phase A 全体は一部未完了（PR-2 = F6、PR-3 = F3 圧縮）

## 体制情報

- Mode: M2 / LC=1 / Cycle: v7.0.0 Phase A（PR-1）
- 自律修正回数: 3 / 上限 3（verifier FAIL 3 件 → 全て同一ターンで是正: 新 reference の相対リンク / anchor-core.md の manifest 未分類 / spec 状態行の鮮度）
- Council: `council-2026-09-13T01:40:00Z-v7phsa`（C2 / implementation / 案C / jc 0.78 / reason_divergence）。consensus_mode は `escalate_to_human` と記録されたが、人間が 2026-09-13 に「すべて実行」で事前承認（D-1〜D-5 推奨案で GO）。implementer_consent: agreed
- 着地単位: 案C — **PR-1 = F1+F2+F4+F5+F7+F10 + fixtures（本 PR）** → 基準凍結（merge 後） → PR-2 = F6 → PR-3 = F3 圧縮 + 再測定。各 PR は前 PR の merge 後に master から切る
- AI 能力バージョン: Claude 5 系（`model-recommendations.md` 2026-08-05 版の参照世代。`history/.model-generation.yml` に機械記録・F7）

## 実装済み機能

| F | 内容 | 受け入れ基準 | 結果 |
|---|---|---|---|
| F1 | 不変核の再注入。`templates/hooks/anchor-core.py`（配布物・DH 本体も同一ファイルを直接実行）+ `.claude/anchor-core.md`（4 条・246 字）+ `templates/hooks/anchor-core.md`（雛形）+ `.claude/settings.json` SessionStart に 1 command | (a) SessionStart 後の文脈に 4 行 → **resume 経路で機械観測済み**（セッション再開時に hook 出力が文脈へ載ったことを 2026-09-13 04:40 UTC に確認。`test-hook-wiring.py` §5 でも stdout を機械確認）。compact 経路は人間の目視 1 回(b) md 不在で exit 0・無出力 → PASS (c) `hook_observations.py` に anchor 配線検査 → PASS（検査 6） | PASS（(a) は人間確認待ち） |
| F2 | `crosscut-verifier-philosophy` を配布除去（1 本・dir 削除・manifest・GRAPH・glossary・参照 12 箇所を廃止注記）。`rtk-integration` / `layer0-onboarding` / `layer0-archeo-architect` の **3 本**に `disable-model-invocation: true`（合計 4 本が一覧枠から消える） | manifest ⇄ GRAPH ⇄ 実在 dir の三者突合（検査 8/9）PASS | PASS |
| F3 | **fixtures のみ**（Council 案C）。`harness-verifier/fixtures/skill-triggers.yml` 17 skill × 正例 8・負例 8 = 272 発話。測定プロトコル（3 run・閾値 5pt・基準は PR-1 merge 後）をヘッダで事前宣言 | fixtures が 17 skill 分ある → PASS。基準値は **merge 後に取る**（未） | 部分（データ着地） |
| F4 | `layer1-independent-reviewer/SKILL.md` に読み順制約（3〜5 の判定確定まで DELIVERY / HANDOFF を開かない） | 記述順が満たす → PASS。本 PR の独立検証に初適用 | PASS |
| F5 | `escalation-matrix.md` §1 に「決定論検査 FAIL は LLM PASS で覆らない」行。`inferential-sensor-v2.md` §スタック全体像に一方向優越の 1 行 | 両ファイルに文言あり・feedback-loop と矛盾なし → PASS | PASS |
| F7 | `history/.model-generation.yml` 新設。`norm-scan.py` の `model_epoch` を max(model-recommendations.md commit, yml changed_at) に変更。`ritual-protocol.md` F1 に記録手順 5.5。`test-norm-scan.py` に 3 ケース | テスト PASS。**実測: 修正前 発火 0 件 → 修正後 発火 3 件**（dev-env-spec / independent-reviewer / test-norm-scan の `model_generation`。独立検証の反証 F-3 で yml を 2000 年に戻すと 3 → 0 を確認）— 代理指標欠陥が塞がったことの実証 | PASS |
| F8 | Council ablation → `delivery/ABLATION-council-2026-09-13.md`（(a-hist) 82 件 / (b-full) 10 件 / (b-snap) 10 件）。結論は書かない | 10 件 × 2 条件の結果表と σ がある → PASS | PASS |
| F9 | 環境再評価（下記） | 前回値との差分表 → 本節 | PASS |
| F10 | SKILL.md 500 行超 3 本の分割: spec-architect **860 → 485**（版履歴 228 行 → `history/CHANGELOG.md`、§0/§3.5/§3.6/§4 詳細 → `references/l0-step-details.md` 逐語移送）/ council **527 → 406**（§CTL 記録 → `references/ctl-recording.md`）/ autonomous-dev **516 → 468**（意図合致検証 → `references/intent-verification.md`） | 3 本とも < 500 行・参照検査 PASS | PASS |

## 通過ゲート記録

| ゲート | 結果 |
|---|---|
| escalation-matrix「規範文書改変の実装前 → Council 諮問」 | 通過（v7phsa・F8 は Council 当事者ゆえ人間直行） |
| 献上時の人間判定 | 本 PR に `human-review-needed`（3 ファイル以上横断 + harness-verifier/** 改修 = opt-in 領域） |
| L-FROZEN 不可侵（I-1） | philosophy.md / delegation-boundary.md / auto-merge-boundary.md の diff **0 バイト**（`git diff --cached --stat` で確認） |

## 自己検証結果

### 計算的センサー

| 検査 | 結果 |
|---|---|
| `python3 harness-verifier/verify.py --strict` | **総合 PASS**（11 項目全 PASS。途中 FAIL 3 件は是正済み） |
| `scripts/test-*.py` 14 本 + `test-*.sh` 4 本 | **全 PASS**（hook-wiring §5 anchor 8 項目・norm-scan F7 3 項目を新設） |
| `templates/hooks/anchor-core.py` 実行 | DH 本体: 4 行出力・exit 0 / md 不在: 無出力・exit 0 |
| `python3 scripts/norm-scan.py` | 発火 3 / 未発火 6 / 機械判定しない 25（修正前は発火 0 / 4 / 21。本 PR で規範メタデータを 4 件追加したため総数増） |
| fixtures 妥当性 | 17 skill・272 発話・各 8/8 |

### 推論的センサー

- 仕様に合う: spec §3 の F1/F2/F4/F5/F7/F10 の受け入れ基準を逐項充足。F3 は Council 案C により「fixtures 先行・圧縮は PR-3」へ範囲変更（spec 本文を同 PR で改訂）。
- 動く: verifier / テスト / anchor 実行で確認。
- 使える: F1 の (a)「新規セッションで 4 行が文脈に載る」は本環境で確認不能 → **人間確認事項**。

### 独立検証（M2 必須）

`delivery/VERIFICATION-v7.0.0-phaseA-PR1.md`（layer1-independent-reviewer・新規文脈・F4 読み順制約を初適用）。

## F9 環境再評価（前回 2026-08-26 B− との差分）

同じ物差し（ループ 6 軸 / 4 原則 / グラフ 10 特徴 / 成熟度 8 段階）。**総合は B− のまま**（等級は動かない。動いたのは下位項目）。

| 軸 | 前回 | 今回 | 差分 |
|---|---|---|---|
| Automations | C+ | C+ | 変化なし（anchor は仕事の発見ではない） |
| Worktrees | D+ | D+ | 変化なし |
| Skills | A− | A− | 一覧枠から 3 skill 退避（フラグ）・1 除去、3 本を 500 行未満に、routing 測定 fixtures 着地。等級据え置き（基準値未計測） |
| Connectors | C− | C− | 変化なし |
| Sub-agents | B | B | reviewer 読み順制約（生成文脈の遮断を明文化）。ablation で Council vs 単一を初めて実測 |
| Memory / State | A− | A− | `.model-generation.yml`（世代の機械記録）と compaction 後の再注入（状態の再錨止）を追加 |
| 特徴 4「edge を契約として扱う」 | ✕ | △ | F5「決定論 FAIL は LLM PASS で覆らない」は契約の宣言。**評価器はまだ無い** |
| 特徴 9「budget と authority を状態へ」 | △ | △ | 変化なし |
| 成熟度 | 3/8 | 3/8 | 変化なし |

## 仕様改訂提案（タイプC）

1. **F1 の配置**: spec は `scripts/anchor-core.py` + `templates/hooks/anchor-core.py` の二重コピーを想定していたが、`templates/` は配布物（overwrite）なので **`templates/hooks/anchor-core.py` 1 本を DH 本体でも直接実行**する形にした（コピー同期の drift を作らない）。spec §F1 の記述を本 PR で追随改訂済み（`hook_wiring.py` → `hook_observations.py` も同時に是正・要人間判定）。
2. **F3 本文の矛盾**（Council 3 軸が独立に指摘）: 「献上時に 1 回計測して基準凍結」では圧縮前の基準が生まれない。本 PR で spec §F3 を「圧縮前に fixtures → merge 後に基準 3 run → 圧縮 → 再測定」へ改訂済み。
3. **axis-audit の warn の原因帰属**: ablation で単一レビュアーも confidence σ ≈ 0.06 だった。「ペルソナが役柄を採点している」warn はモデル性質の可能性がある。Phase B 前に原因を分ける観測を提案。

## 未解決事項

- F1(a) 注入の目視確認: **resume 経路は機械観測済み**（2026-09-13 04:40 UTC、本セッション再開時の `SessionStart:resume` hook 出力として不変核 4 行が文脈に載った）。`startup` / `clear` / `compact` 経路は未観測（同じ matcher なし配線なので同挙動の想定。人間の目視は `compact` 直後 1 回で足りる）。
- F3 基準値の計測（PR-1 merge 後・3 run）。`/context` による一覧枠の実消費（等級 C 由来の 4.5〜6.5 倍の実数化）も人間側で 1 回。
- Council の `consensus_mode: escalate_to_human`（jc 0.78 なのに）の算出条件は未調査。人間事前承認で進めたが、算出ロジックの確認を P3 に。

## 体制事後評価

- M2 妥当。独立検証 1 回（PASS 警告付き・指摘 13 件のうち実装側 10 件を同ターン是正、人間確認 3 件を未解決に残す）、修正ループは verifier FAIL 3 件（全て自力で同ターン是正）。Council 発動 1 回は妥当（規範文書改変の実装前・escalation-matrix 該当）。L2 閾値には遠い。
- 判断献上履歴（C2）: v7phsa 1 件（案C 採用）。
- 割り込み: なし（人間への質問 0）。
- 次回への示唆: (1) description 圧縮は基準値なしで着手しない（Council の指摘どおり）。(2) 「配線済み・中身なし」型の欠陥（PreCompact 観測・model_generation 代理指標）は「実行主体が居るか」を点検項目に加えると早く見つかる。

## 履歴層更新差分

| レベル | 対象 | 内容 |
|---|---|---|
| A（自動） | `history/CHANGELOG.md` | v7.0.0 Phase A PR-1 節を追加 + spec-architect 版履歴の移送先節（F10） |
| B（確認推奨） | `history/INTENT.md` | 「v7.0.0：現行モデル世代向けメタハーネス刷新」節を追加 |
| B（確認推奨） | `history/REGIME-LOG.md` | v7.0.0 Phase A の体制記録（M2 / 儀式レベル 3 / Council v7phsa / 世代更新） |
| B（確認推奨） | `history/COUNCIL-LOG.md` | v7phsa 追記済み（クロージング手順で同期・CTL-1 維持） |
| C（必須承認） | — | INTENT の廃止・訂正なし。ただし D-2（verifier-philosophy 除去）は deprecation-protocol の「廃止決定時の記録」に該当 → INTENT 節に廃止マーカーを記載（要人間確認） |
