# VERIFICATION.md — upgrade-spec v7.0.0 Phase A / PR-1（独立検証）

## 判定: PASS（警告付き・差戻し推奨事項あり）

- PASS の意味: 「spec §3 の PR-1 対象 F の受け入れ基準を決定論の実行結果で全通過 ∧ 試行した反証のうち SPEC 記載の保証を破るものが無い」。正しさの証明ではない（§反証記録「この PASS が保証しない範囲」参照）。
- 反証 1 件（F-5）は SPEC に明記された保証の外側で成立した堅牢性欠陥であり、FAIL 条件（SPEC 記載の保証を破る）には該当しないため差戻し**推奨**（非ブロッキング）として §未解決・差戻し事項に提起する。

## 体制情報

- 検証者: layer1-independent-reviewer（新規文脈・実装コンテキスト非継承。本プロンプト以外の会話履歴なし）
- 対象: `git diff --cached`（未 commit・staged、45 files / +1607 −661）、branch `claude/harness-era-philosophy-7vachm`、HEAD `97d0d47`
- Mode: M2（spec §6）/ LC ≥ 1（history/ 照合あり）
- 参照した入力: `dh-upgrades/upgrade-spec-v7.0.0.md` §2・§3・§8、staged diff（`history/COUNCIL-LOG.md` は読んでいない）、`.claude/skills/layer1-independent-reviewer/SKILL.md`、`references/falsification-protocol.md`、`dev-env-spec.md` §delivery/ 配置規則、`deprecation-protocol.md`
- 読まなかったもの: `history/COUNCIL-LOG.md`、`~/.claude/council-data/`（禁止）。`delivery/DELIVERY-v7.0.0-phaseA-PR1.md` / `delivery/HANDOFF-v7.0.0-phaseA-PR1.md` / `history/CHANGELOG.md` の v7.0.0 節は §三点突き合わせ まで開いていない
- **読み順制約（F4）の初適用記録**: 処理フロー 3〜5 と反証（5.10）を確定した後に DELIVERY / HANDOFF / CHANGELOG v7 節を開いた。順序: spec → diff → 決定論実行 → 反証 → 判定確定 → DELIVERY/HANDOFF → 5.9 三点突き合わせ

## 決定論の実行結果（判定の一次根拠）

| 実行 | 結果 |
|---|---|
| `python3 harness-verifier/verify.py --strict` | exit 0・11 項目全 PASS（検査 6「hook 観測一貫性」に anchor 配線検査を含む・検査 8/9 PASS） |
| `scripts/test-*.py` 14 本 | 全 exit 0（hook-wiring §5 anchor 8 項目 / norm-scan F7 3 項目を含む） |
| `scripts/test-*.sh` 4 本 | 全 exit 0 |
| `CLAUDE_PROJECT_DIR=$PWD python3 templates/hooks/anchor-core.py` | exit 0・見出し 1 行 + 4 条を stdout 出力・HTML コメント（規範メタデータ）は出力されない |
| `.claude/settings.json` の SessionStart command 文字列をそのまま bash 実行 | 同上 4 条出力・exit 0。matcher なし（`{}`）を確認 |
| `python3 scripts/norm-scan.py` | 走査 23 / 時限トリガ 34（**発火 3** / 未発火 6 / 機械判定しない 25）。発火 3 = `dev-env-spec.md` / `layer1-independent-reviewer/SKILL.md` / `scripts/test-norm-scan.py` の `model_generation` |
| `git diff --cached --stat -- '*philosophy.md' '*delegation-boundary.md' '*auto-merge-boundary.md'` | **空（0 バイト差分）** — I-1 充足 |
| SKILL.md 行数（`wc -l`） | spec-architect 860 → **484** / council 527 → **406** / autonomous-dev 516 → **468**。全 SKILL.md で ≥ 500 行は 0 本 |
| fixtures（yaml 解析） | 17 skill × positive 8 / negative 8 = 272 発話。fixtures の skill 集合 = `disable-model-invocation` 無しの skill 集合（差分 ∅） |
| `disable-model-invocation: true` | 3 本（rtk-integration / layer0-onboarding / layer0-archeo-architect）。layer2-orchestrator / layer2-integration-verifier / crosscut-autonomous-drive は無し（spec どおり） |
| 相対リンク検査（新設 3 references + 改変 4 SKILL.md、markdown リンク + backtick パス） | dead 0 件 |
| 移送内容の照合 | council: 削除 104 行のうち逐語不一致 3 行（パス表記の `references/` 接頭辞除去のみ）/ autonomous-dev: 削除 32 行のうち 3 行（同上 + verifier-philosophy 行の意図的削除）/ spec-architect: 削除 282 行のうち逐語不一致 86 行 → CHANGELOG 側でパスを絶対化（`.claude/skills/...`）・見出しを `###`→`####` に改めた版履歴。骨格フレーズの spot-check（Stack 10 / ui-baseline / sheep-navigator / subphase-common-protocol / dev_mode 判定）は全て移送先に存在 |

## 仕様合致（spec §3・F ごと）

| F | 受け入れ基準（spec） | 検証方法 | 判定 |
|---|---|---|---|
| F1 (a) | SessionStart 後の文脈に 4 行が現れる（手動確認） | `claude --debug` は本環境で実行不能。代替として settings.json の command 文字列をそのまま実行し stdout に 4 条が出ることを確認 | **PASS（実行同値・文脈への実搭載は人間の目視待ち）** |
| F1 (b) | hook 不在・ファイル不在でも通常動作 | test-hook-wiring §5「md 不在でも exit 0・無出力」PASS + 反証 F-6（コメントのみ md → 空出力 exit 0） | **PASS** |
| F1 (c) | `hook_wiring.py` が anchor 配線を検査項目に持つ | `harness-verifier/checks/hook_wiring.py` は存在しない。検査は `hook_observations.py::_check_anchor`（verify 検査 6）+ `scripts/test-hook-wiring.py` §5 に実装。反証 F-1 / F-2 で FAIL 化を実証 | **PASS（spec 記載のファイル名と実装が不一致 → 提起 #7）** |
| F1 本文 | anchor-core.md は philosophy 引用のみ・≤ 250 字 | 4 条本文 213 字 / 見出し込み 257 字。文言は spec 起草案と一致（見出しに「第 2・6・8・9 条の」を追記）。verify の上限は 400 字 / 8 行 | **PASS（見出し込みで 250 字超 → 提起 #8）** |
| F1 配線 | SessionStart に matcher なしで追加 | settings.json 解析: `[{}]` + hooks 2 command | **PASS** |
| F2 | manifest と GRAPH の node が整合（検査 8・9 PASS） | 検査 8/9 PASS。`crosscut-verifier-philosophy/` dir 不在・manifest / GRAPH / glossary から除去。フラグ 3 本、非フラグ 3 本とも spec どおり。INTENT に `**廃止**` マーカーあり | **PASS（残存言及 2 箇所 → 提起 #6）** |
| F3（PR-1 分） | fixtures が 17 skill 分ある | 17 × 8/8。ヘッダに 3 run・5pt 閾値・基準取得時期を事前宣言 | **PASS** |
| F4 | SKILL.md の記述順が制約を満たす（目視） | 処理フロー 2 に制約 4 行、3〜5 の前、5.4 / 5.9 は後。本検証で実適用 | **PASS** |
| F5 | 両ファイルに文言、feedback-loop 還流表と矛盾なし | escalation-matrix §1 に行追加、inferential-sensor-v2 §スタック全体像に 1 段落。feedback-loop 還流表は formal_fail → 実装層（即時修復）で、決定論 FAIL を LLM PASS で覆す経路は無い | **PASS** |
| F7 | test-norm-scan に「yml が新しければ発火」ケース | 3 check 追加（epoch 関数の単体レベル）。発火自体は反証 F-3 で実証（yml を 2000 年に戻すと発火 3 → 0） | **PASS（テストは `decide`/`scan` の発火を直接観測していない・第 3 check は恒真 → 提起 #4、不正日付で crash → 提起 #1）** |
| F8 | 10 件 × 2 条件の結果表と σ がある / 結論は書かない | `delivery/ABLATION-council-2026-09-13.md` §1 に (a-hist)/(b-full)/(b-snap) の表 + (b-snap) 10 件内訳 + σ。§2 は「判断はしない」と明記 | **PASS（形式充足。数値は council-data 非参照のため独立再現不能 → 保証範囲外。提起 #9）** |
| F9 | 前回値との差分を必須出力 | REGIME-LOG に B−（変化なし）記載。差分表の所在は DELIVERY §F9（三点突き合わせで存在確認） | **PASS** |
| F10 | 3 本とも < 500 行・参照検査 PASS | 484 / 406 / 468。verify 検査 2・3 PASS、dead link 0。D-4 は CHANGELOG 移送（spec 選択肢 1）。SKILL.md に「版履歴は CHANGELOG」の 1 行あり | **PASS（spec-architect は余裕 16 行）** |
| I-1 | L-FROZEN 3 文書 0 バイト | `git diff --cached --stat` 空 | **PASS** |
| I-4 | 追加規範に review_trigger | anchor-core.md / anchor-core.py / fixtures / reviewer SKILL 追記 / ABLATION に付与（norm-scan が列挙） | **PASS** |
| I-6 | anchor を hook-observer に同居させない | `templates/hooks/anchor-core.py` 単独。hook-observer skill 配下は無変更 | **PASS** |

## 動作・使用確認

- 起動（hook 実行）: PASS（上表）
- エラーハンドリング: md 不在 / コメントのみ md → 無出力 exit 0（PASS）。yml 不正日付 → norm-scan が ValueError で exit 1（**degrade しない**。反証 F-5）
- 使用（利用者視点）: `.dh/anchor-core.md` と `.claude/anchor-core.md` が両方あると `.claude` 側が優先される（CANDIDATES 順）。spec は利用者プロジェクト = `.dh/` と規定しており、両立時の優先は未規定（提起 #13）

## 配置規則（5.5）/ 履歴整合性（5.8）/ クレジット（5.6）

- delivery/: `ABLATION-council-2026-09-13.md` は dev-env-spec §delivery/ 配置規則の許可リスト外だが spec F8 が出力先として明示（spec 優先・違反としない）。`DELIVERY-*.md` / `HANDOFF-*.md` の版サフィックス命名は既存慣行（v6.12.0）と同一
- ルート直下の作業メモ混入: なし（`git status --short`）
- 5.8: `crosscut-verifier-philosophy` は過去 INTENT（v5.x「本実装」計画、v6.0.0「大統合」候補）と逆向きだが、INTENT に `**廃止**: 2026-09-13 — 理由` を追記済み・deprecation-protocol の記録要件（INTENT 追記）充足。CHANGELOG 側は「1 本廃止・F2」とのみ記し skill 名を持たない（提起 #10）
- 5.6: README.md 無変更・DH 本体は対象外

## 反証記録（Falsification・5.10）

| # | 類型 | 試行 | 期待 | 結果 | 復帰確認 |
|---|---|---|---|---|---|
| F-1 | B（test-the-tests） | `.claude/anchor-core.md` に 300 字追記（本文 566 字） | verify 検査 6 FAIL / test-hook-wiring FAIL | verify exit 1「不変核が大きすぎる: 566 字 / 6 行」、test-hook-wiring FAIL 1 件 | `git checkout --` 後、worktree == index を diff で確認 |
| F-2 | B | settings.json の SessionStart から anchor 行を除去 | 検査 6 FAIL（md あり・配線なし） | verify exit 1「anchor-core.md があるが … 呼んでいない」、test-hook-wiring FAIL 1 件 | 同上 |
| F-3 | A（挙動） | `history/.model-generation.yml` の changed_at を 2000-01-01 に | model_generation の発火が消える | 発火 **3 → 0**（未発火 9）。発火 3 件は全て yml 由来と実証。ただし未発火メッセージは依然「model-recommendations.md は本規範より古い」（提起 #5） | 同上 |
| F-4 | B（ミューテーション） | `norm-scan.py::model_generation_epoch` を yml 無視に改変 | test-norm-scan FAIL | FAIL 1 件（「yml の changed_at が … 新しければそれを採る」）exit 1 | 同上 |
| F-5 | A（異常系） | changed_at を `"2026-13-45"`（形式一致・意味不正） | degrade（skip / 警告） | **反証成立**: `ValueError` traceback・exit 1。儀式 F2.6 の norm-scan が停止する。SPEC 明示の保証ではないため差戻し推奨（提起 #1） | 同上 |
| F-6 | A（境界） | (i) md が HTML コメントのみ (ii) `.dh/` と `.claude/` 両方存在 | (i) 無出力 exit 0 (ii) 規定なし | (i) 0 バイト exit 0（degrade OK）(ii) `.claude` が優先 | tmp dir で実施・repo 無変更 |
| F-7 | C（Oracle） | SKILL.md 3 本の行数・移送内容の逐語照合・dead link | < 500 / 欠落なし / 0 | 484・406・468 / 骨格フレーズ全件移送先に存在 / dead 0 | 読取のみ |
| 静的 | B | `test-norm-scan.py` 第 3 check `... is None or True` | — | **恒真アサーション**（例外時は uncaught で crash するため検出はされるが、check として無意味）（提起 #4） | — |

- 全試行後の `git status --short` は試行前スナップショットと **完全一致**（diff 空）。本ファイル（VERIFICATION）の新規作成のみが差分
- **この PASS が保証しない範囲**:
  - F1 (a) 実セッションの文脈に 4 行が実際に搭載されること（`claude --debug` 未実行・人間確認事項）
  - F8 ABLATION の数値の正しさ（`~/.claude/council-data/` を参照しないため再現不能。再現用 `/tmp/ablation-*.json*` はセッション揮発）
  - F3 routing 基準値（PR-1 merge 後に取る設計・未計測）
  - `python` フォールバック側（`|| python ...`）の動作（python3 のみ実行）
  - 利用者プロジェクト（`.dh/anchor-core.md`）での配布経路（`templates/` overwrite の実配布は未試行）
  - description 圧縮（F3 本体）/ F6 / Phase B は本 PR の対象外

## 三点突き合わせ（5.9: DELIVERY / HANDOFF / CHANGELOG v7 節 vs 実装 vs 検証結果）

| # | 記載 | 実装・検証結果 | 乖離 |
|---|---|---|---|
| T-1 | DELIVERY F7「発火 3 件（dev-env-spec / independent-reviewer / **anchor**）」 | 発火 3 = dev-env-spec / independent-reviewer / **`scripts/test-norm-scan.py`**。`.claude/anchor-core.md` は未発火 | **事実誤り**（第 3 件の同定） |
| T-2 | DELIVERY 自己検証「発火 3 / 未発火 2 / 機械判定しない 21」 | 発火 3 / 未発火 6 / 判定しない 25（計 34） | 計数不一致（測定時点の差と推定。記載を現状に更新要） |
| T-3 | HANDOFF「使っていない skill **4 本**を一覧から外し … 1 本廃止」/ DELIVERY §F9「4 skill 退避・1 除去」/ CHANGELOG「4 本退避・1 本廃止」 | `disable-model-invocation` は **3 本**。一覧から消えたのは 3 + 除去 1 = 4 | 人間可読サマリが 1 本多い（spec §F2「フラグ 4 本 = 1,775 字」の内部矛盾が伝播） |
| T-4 | DELIVERY F1「4 条・257 字」 | 257 字（見出し込み）で一致。spec の ≤ 250 字への言及なし | 軽微（提起 #8） |
| T-5 | DELIVERY F1 (a)「手動確認は未実施」/ HANDOFF「人間確認をお願いしたい 1 点」 | 本検証でも実セッション確認不能 | 一致（正直な申告） |
| T-6 | DELIVERY F10「860 → 485」 | `wc -l` = 484 | 1 行差（無害） |
| T-7 | DELIVERY「test-*.py 14 本 + test-*.sh 4 本 全 PASS」/ verify 11 項目 PASS | 独立再実行で全 PASS | 一致 |
| T-8 | DELIVERY 仕様改訂提案 1（`scripts/anchor-core.py` を作らず templates 直接実行） | 実装と一致。spec §F1 本文は未改訂 | 一致（spec 追随は人間判定待ち。`hook_wiring.py` の名称不一致は提案に含まれていない） |
| T-9 | DELIVERY F2「参照 12 箇所を廃止注記」 | BOUNDARY.md L33 の crosscut 系列表、feedback-loop description L6「philosophy verifier」が未注記 | 網羅漏れ 2 箇所 |
| T-10 | DELIVERY F8 / ABLATION「結論は書かない」 | ABLATION §4「申し送り」に「代替になりうる」等の解釈文。spec 条件 (b)「topic_summary + options」に対し ABLATION §3 は options 非提示と自認 | 軽微な乖離（判断材料の枠内だが条件設計が spec と異なる） |
| T-11 | DELIVERY 履歴層 C「INTENT の廃止・訂正なし。ただし … 廃止マーカーを記載」 | INTENT に `**廃止**` 行あり | 文言の自己矛盾（「廃止なし」と「廃止マーカー記載」） |
| T-12 | REGIME-LOG「F2.7 … 詳細は DELIVERY §F9」/ spec §8「F9 の差分表が DELIVERY にある」 | DELIVERY §F9 に 9 行の差分表あり・B− 変化なし | 一致 |
| T-13 | HANDOFF §3「Council 判定 1 件」 | Council 記録は読んでいない（COUNCIL-LOG 非参照）。`.council-ctl.json` は timestamp のみ変更 | 検証対象外（保証範囲外） |

## 未解決・差戻し事項（提起のみ・訂正は L1 / L0）

差戻し推奨（L1・非ブロッキング。PASS 判定は維持）:

1. **norm-scan の不正日付 crash（反証 F-5）**: `model_generation_epoch` の `strptime` を try/except で包み、不正時は yml 側を無視して warn（degrade）。yml は儀式 F1 で AI が書くため入力妥当性は保証されない。DH 既存規律（anchor「失敗時 exit 0」、儀式「スクリプト不在なら skip」）と揃える
2. **DELIVERY F7 の事実誤り（T-1）と計数（T-2）**: 発火 3 件目は `scripts/test-norm-scan.py`。数値を現状（3 / 6 / 25）に更新
3. **「4 本退避」→ 3 本（T-3）**: HANDOFF / DELIVERY §F9 / CHANGELOG v7 節。spec §F2「フラグ 4 本」も表（3 本）と矛盾（L0 側）
4. **test-norm-scan 第 3 check の恒真**（`or True`）を `try/except` で例外の有無を判定する形に。併せて「yml が新しければ **発火** する」を `scan()` / `decide()` レベルで観測する check を 1 件追加（spec 受け入れ基準の文言に合わせる）
5. **norm-scan の why 文言**: 「model-recommendations.md が本規範より新しい」は F7 後の実態（max(…, yml)）と不一致。発火理由に yml 由来か commit 由来かを出すと儀式 F2.6 の問いが具体化する
6. **verifier-philosophy の残存言及**: `harness-verifier/BOUNDARY.md` L33、`crosscut-feedback-loop/SKILL.md` description L6

spec 追随（L0・人間判定）:

7. spec §F1 (c) の `hook_wiring.py` は存在せず、実装は `hook_observations.py`（検査 6）。§F1 の `scripts/anchor-core.py` も未作成（DELIVERY 提案 1 と同旨）。spec 本文の追随または実装側のファイル名整理を人間が選ぶ
8. anchor-core.md は見出し込み 257 字（spec ≤ 250 字）。verify の上限 400 字は spec の 250 を強制しない。閾値をどちらに揃えるか（4 条本文のみ 213 字なら充足）
9. F8: 条件 (b) に options を渡していない（spec は「topic_summary + options のみ」）。再現用 JSON が `/tmp`（揮発）。Phase B 材料として使うなら `delivery/` か `history/` に固定を推奨
10. CHANGELOG の廃止エントリに skill 名（`crosscut-verifier-philosophy`）を明記（deprecation-protocol「CHANGELOG に廃止エントリ」）。DELIVERY 履歴層 C 行の文言整理（T-11）

人間確認:

11. F1 (a): 新規セッション / compact 直後の文脈に不変核 4 行が載ることの目視（DELIVERY / HANDOFF と同旨）
12. `hook_observations.py`（検査名「hook 観測一貫性」）に注入側の anchor 検査を同居させた命名の是非（I-6 は skill 同居の禁止であり検査器の同居は違反ではない。命名だけの提起）
13. `.dh/anchor-core.md` と `.claude/anchor-core.md` 両立時の優先順（現状 `.claude` 優先）を spec に明記するか
14. spec-architect SKILL.md は 484 行（余裕 16 行）。次の追記で 500 行に戻る蓋然性が高い
