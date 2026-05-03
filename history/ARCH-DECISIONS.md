# ARCH-DECISIONS

DH 本体の設計判断の記録（ADR 軽量版）。

## v5.5.3

### AD-022: autonomous-drive 機構の出口側として label opt-in 自動 merge を新設

| 項目 | 内容 |
|---|---|
| 状況 | DH の crosscut-* 機構（v5.0.0 で導入: dispatcher / issue-implementer / feedback-loop）は autonomous-drive パイプラインの入口〜中段までを自動化していたが、最終段階の merge は人間手押しで残っていた。ユーザー（非エンジニア）からの要請「自律駆動できるようにしたい、issue label = GO サイン → AI 実装 → 自動 merge」を起点に、出口側自動化の必要性が確定 |
| 判断 | **(a) パス A 採用**: 「auto-merge workflow だけ追加」を選択。「パス B: dev_mode を `autonomous` へ引き上げ」は v5.6.0 候補として温存（観測駆動原則、数 PR 試運用後に判断）。**(b) GitHub native auto-merge ではなく workflow で直接 merge**: branch protection 設定変更不要、ロジック一元管理、運用観測（notice ログ）一元化。**(c) 4 層検証 AND** で auto-merge 条件を構成: 構造層（harness-verify）+ 意味層（gemini-review）+ 判断層（reviewDecision != CHANGES_REQUESTED）+ 承認層（label `auto-merge` + author allowlist）。**(d) `ALLOWED_AUTHORS` を workflow env に明示 hardcode**: 拡張は spec 改修扱い、L0 spec-architect 経由で REGIME.md と整合確認必須。**(e) verifier 全て「走った場合のみ必須」+ 最低 1 verifier guard**: harness-verify / gemini-review いずれも paths filter があり全 PR では走らないため、両者を「走った場合のみ SUCCESS 必須」とし永久 pending を回避。zero-check auto-merge は別途 guard 条件で防ぐ（Copilot review #42 で初版「harness-verify は paths filter なしで全 PR 走る」事実誤認を訂正）。**(f) Robustness pre-check 追加**: GH_REVIEW_PAT availability check + check_suite event 経由で SHA に複数 open PR 紐付き時の skip + warning（Copilot review #42 line 89 対応） |
| 根拠 | (a) パス A はリスク小・段階的、ユーザー体感の自律度が大幅 up（手動 merge ボタン押しが消える）、AI 自走による意図逸脱リスクを 1 層ずつ観測しながら拡大可能（観測駆動原則と整合）。(b) GitHub native auto-merge は branch protection 必須で運用ルール変更を伴う、本機構は branch protection なしでも opt-in 動作する低侵襲設計。(c) 4 層 AND は philosophy.md §3「情報純度」（Generator/Evaluator 分離）と §5「献上哲学」（自律内部完結禁止、独立観測機構の通過）を実装。(d) hardcode は allowlist の不可視拡張（誰かが secret を追加して invisible に信頼境界が広がる）を防ぐ設計判断。(e) 必須化は paths filter 起因の deadlock を防ぐ、最低 1 verifier guard で zero-check auto-merge も防ぐ。(f) PAT pre-check で fork PR / secret 欠落での red CI を防ぐ、multi-PR detect で merge target の非決定性を排除。Council 起動条件のいずれにも該当せず Council 諮問は不要 |
| 影響 | `.github/workflows/auto-merge.yml` 新設（160 line）。SK 本文・harness-verifier・利用者プロジェクトへの影響ゼロ。**opt-in 完全後方互換**（label なき PR は従来通り手動 merge）。本 patch 自身は label を付けず人間 merge で投入し、信頼運用は次 PR から開始する 4 例目運用。dev_mode は `github_assisted` のまま据え置き、autonomous 化は v5.6.0 候補として温存。**温存項目**: パス B（dev_mode autonomous 化、L0 spec-architect 経由）/ `ALLOWED_AUTHORS` の動的化（複数 contributor 体制になったら検討）/ destructive change detector（diff threshold / DELETE-heavy 検出、観測駆動で追加判断） |

## v5.5.2

### AD-021: gemini-review の diagnostics 縮退と PAT availability check 新設

| 項目 | 内容 |
|---|---|
| 状況 | v5.5.1 PR #40 で gemini-review GitHub Action（PR #37/#38 で導入）の運用テストが完了。8 commit にわたる段階的診断（仮説 A〜F + α）の結果、真因 = settings JSON `tools.core: []` / `includeTools` filter による tool exposure 阻害（α パッチで除去済）+ PAT permission 不足（ユーザーが Read+Write 付与済）と確定。診断目的で導入された暫定機構（`continue-on-error: true` / `GEMINI_DEBUG: "true"` / Diagnostics step 2 件）が役目を完遂し、本番運用構成への縮退が必要 |
| 判断 | **(a) Diagnostics 機構の削除**: `Diagnostics — runner / docker / GitHub MCP server reachability` + `Diagnostics — gemini_review step outcome` の 2 step、`continue-on-error: true`、`GEMINI_DEBUG: "true"` env、`id: gemini_review` を削除。**(b) `GH_REVIEW_PAT` availability check 新設**: `continue-on-error` 削除により PAT 未設定時に job hard-fail する事象を防ぐため、`GEMINI_API_KEY` と同形式の早期 availability check を追加し、両 secret available 時のみ `Run Gemini PR review` / `Upload gemini-artifacts` を実行する。**(c) Artifact upload は保持**: `actions/upload-artifact@v4` step は将来 debug 用に残置（low cost、retention 7 日）。**(d) prompt の self-PR fallback 方式維持**: v5.5.2 草案では PAT owner = PR author の構造的前提で APPROVE 試行を禁止する案だったが、Copilot review #41 line 184 で「他 maintainer が同 repo に PR を作った場合に誤った検閲となる」と指摘 → revert。v5.5.1 と同じ API 応答ベース fallback 方式（APPROVE 試行 → 拒否時のみ COMMENT fallback）を維持。**(e) settings JSON の security 注追加**: `includeTools` 不在で全 tool が expose される trade-off を明文化、v5.5.x 候補として絞り込み再検討を記録 |
| 根拠 | (a) v5.5.1 PR #40 で診断機構は「役目完遂後縮退」前提で導入されており本 patch はその完遂後実施、(b) self-PR APPROVE 制約はハードコードではなく API 応答ベース fallback で扱うのが unenforced repository assumption を排除する正しい設計（Copilot review #41 で指摘されて revert）、(c) Council 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当せず Council 諮問は不要、(d) philosophy.md §5「献上哲学」の「役目を終えた機構の縮退」原則と §3「情報純度」の「fail を fail として可視化」原則と整合 |
| 影響 | **operational behavior 変更（意図的、Copilot review #41 line 13/12/14 で指摘）**: `continue-on-error: true` 削除により transient Gemini/MCP failure が以前の silent success → 本 patch 以降は **hard-fail (red CI)** になる。これは観測可能な挙動変更だが、レビュー機構の fail を fail として可視化する設計判断として意図的。PAT availability check 新設で PAT 未設定環境では従来通りクリーン skip するため、設定不備による noisy red は発生しない。`.github/workflows/gemini-review.yml` 全体で約 50 line 縮減（324 → ~275 line、PAT check step 追加分を考慮）。SK 本文・harness-verifier・利用者プロジェクトへの影響ゼロ。`includeTools` 不在による security trade-off は v5.5.x 候補として温存（tool 名の正しい形式判明後に read 系のみへ絞り込み）。本 patch 自身が gemini-review の本番運用 3 例目テストとなり、新構成の動作確認を兼ねる |

## v5.5.1

### AD-020: Phase γ 先行宣言 4 の本実装（ストラングラー / BBA 射程外の正式宣言）

| 項目 | 内容 |
|---|---|
| 状況 | v5.5.0 の AD-019 で Phase γ コア 3 件（先行宣言 1/2/3）を本実装し、先行宣言 4（ストラングラー射程外宣言）+ 5（失敗アンチパターン早期検出）は v5.5.x patch / v5.6.0 へ温存とされた。先行宣言 4 は 4 行記述の先行宣言版で `handoff-to-evaluator.md` に存在していたが、Phase γ コア 3 件の実装過程で `handoff-to-evaluator.md` が VB6 移行事例（ストラングラー類似）と Branch by Abstraction に言及したため、L1 実装者が「先行宣言 2 → BBA 全パターン採用」と拡大解釈する誤りリスクが残置されていた |
| 判断 | 先行宣言 4 を v5.5.1 patch で本実装。`handoff-to-evaluator.md` の先行宣言 4 セクションを 4 行記述から 5 サブセクション（射程外要素の明示列挙 / 援用と全体採用の境界線 / L1/L2 禁止規約 / v6.0.0 昇格の観測トリガー / 整合性ガード）へ拡充。先行宣言 5 は引き続き温存（Phase β との一体化要件のため） |
| 根拠 | (a) v5.5.0 AD-019 で v5.5.x patch / v5.6.0 候補として既に明示済み、(b) Phase γ コア 3 件の実装で生じた拡大解釈リスクを Shift Left で防止する必要、(c) 明文化のみで機能変更ゼロ・後方互換完全維持のため patch で十分（minor 昇格不要）、(d) 観測駆動原則（`wf-baseline-rationale.md` §3）に従い v6.0.0 昇格条件を観測閾値（≥ 3 利用者プロジェクト要請）として明示することで温存範囲を限定、(e) Council 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当せず Council 諮問は不要 |
| 影響 | `layer0-archeo-architect/references/handoff-to-evaluator.md` の **4 箇所**を改修: (1) ステータスヘッダ / (2) ロードマップ表 / (3) 実装ステータス記述（Phase γ 詳細仕様 §冒頭の節）/ (4) 先行宣言 4 セクション本体（4 行 → 5 サブセクション）。SK 本文の機能変更ゼロ、既存 references の本文（追記のみ）、crosscut-* / templates/ / harness-verifier/ は機能不変。`refactor-intent-map.md` の I/O 契約不変。先行宣言 2/3 との整合性ガード（schema priority）を新設、今後の先行宣言 2 更新時に整合確認義務発生。Copilot review #39 line 14 で指摘された箇所数の事実誤認（3 → 4）を訂正済み |

## v5.5.0

以下 2 件は PR #33 ブレスト結晶 `delivery/AUTONOMOUS-DRIVE-BRAINSTORM-2026-05-02.md`（adrv01/02/03 全合意成立）を起源とする L0 設計判断 + L1 実装。確定ロードマップ「v5.5.0 = adrv01-Ph1 + Phase γ」に従い、v5.4.0 リリース翌日に L0 spec-architect で SPEC 化し、同セッション内で L1 が minor として実装。

### AD-018: AI 自己申告閾値の Council 連動明文化（adrv01-Ph1）

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF v0.1.0「自律駆動機構の哲学的座標」§2.2「拮抗判定検出主体」の Council 諮問 `council-2026-05-02T11:00:00Z-adrv01` で「(b) 独立観測機構 + 哲学者第3の道（メタ層構造）統合」が recommended、`agreed_with_modification`（段階的組み込みで止揚 Phase 1-3）。Phase 1 = AI 自己申告のみ運用（既存 Council confidence < 0.6 機構流用、コスト 0）の本実装が v5.5.0 スコープ |
| 判断 | `crosscut-council/SKILL.md §自己申告プロトコル` を新節として追加。confidence < 0.6 自己評価を Council 起動の正式トリガーとして明文化し、内部完結による回避を禁止。`pre-check.md` に scope/PR 境界 vs 新規思想 の判別シナリオ例追加（Copilot review feedback 由来）。`consensus-protocol.md` に escalated → 後付け合意のエッジケースと v5.6.0 Ph2 の hook 経路先行宣言を追加 |
| 根拠 | adrv01 Council 結果 + Council `vrfy01` 事例（category 誤選択が confidence 降下→escalation を連鎖した実例）。明文化のみで機構強化（hook 本実装）は v5.6.0 Ph2 へ温存。adrv01 の段階的組み込みで止揚パターンに整合 |
| 影響 | 既存 confidence < 0.6 機構の挙動は不変。新規実装ゼロ、明文化のみ。利用者プロジェクトには影響しない（DH 本体の規約改訂） |

### AD-019: Phase γ コア 3 件の本実装（archeo-architect 起点問題解決）

| 項目 | 内容 |
|---|---|
| 状況 | v5.4.0 で archeo-architect Phase α 雛形のみリリースされ、`handoff-to-evaluator.md` に Phase γ 詳細仕様 5 件が先行宣言された。起点問題（リファクタ依頼で 3〜4 個取りこぼす）の構造解決には L1 評価軸を「仕様適合 ∩ 動作 ∩ ユーザビリティ ∩ 意図合致」の 4 軸化が必須 |
| 判断 | 5 件中コア 3 件（先行宣言 1: 承認テスト生成プロトコル / 先行宣言 2: 自動照合ループ / 先行宣言 3: L1 意図合致軸統合）を v5.5.0 で本実装。先行宣言 4（ストラングラー射程外宣言）+ 5（失敗アンチパターン早期検出）は v5.5.x patch / v5.6.0 へ温存 |
| 根拠 | コア 3 件で起点問題は構造的に解決可能（refactor_directive: preserve / restructure / 評価軸 4 軸化の 3 領域カバー）。先行宣言 4/5 は周辺案件で minor 1 本のスコープを膨張させずに本リリースに集中できる |
| 影響 | `inferential-sensor-v2.md` 第 4 層に意図合致軸追加、`layer1-autonomous-dev/SKILL.md` §6 に承認テスト + 自動照合ループ追加、`layer1-independent-reviewer/SKILL.md` の評価軸 4 軸化、`delivery-format.md` に意図合致検証セクション追加、`handoff-to-evaluator.md` を先行宣言版から完全版（コア 3 件本実装）化。後方互換完全維持: `refactor-intent-map.md` 不在時は意図合致軸不発動 |

## v5.3.0

以下 3 件は HANDOFF「1 機能完遂の自律駆動 WF 設計」2026-04-30 を起源とする L0 設計判断 + L1 実装。
v5.2.0 リリース後に L0 で確定し、L1（layer1-autonomous-dev）が同日 v5.3.0 minor として実装。
後方互換維持（v5.0.0 / v5.1.0 / v5.2.0 と同パターン）。`crosscut-verifier-philosophy` 本実装は v5.3.x または v5.4.0 へ再後送。

### AD-015: 1 機能完遂 WF を「形状単一・薄い基底 + 観測駆動の厚化」とする

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF 論点 1（WF 基底テンプレート）で、bug-fix / 新規機能 / リファクタ / 仕様改訂等の機能タイプ別に WF 群を多様化するか、単一形状を保つか、最初から薄い基底だけ用意して厚化は観測に任せるかが拮抗。Council で案 N（多様化しない=哲学者）が weighted_score 3.25、案 H（Hybrid 薄い基底+観測駆動）が 4.65 で拮抗判定 |
| 判断 | 案 H 中核 + 案 N の運用原則化の統合採用。基底 WF は **layer1-autonomous-dev SKILL.md §処理フロー（1〜8）が現に基底**であり、これ以上の機能タイプ別 override / 分岐 WF を追加しない。機能タイプは context として動的注入され、分岐は §4「実装タスク分解」内の判断点として吸収。観測閾値（同一 override パターンが 3 機能タイプ以上で繰り返し発生）に達した場合のみ、Council 経由で基底側引き上げを再諮問する |
| 根拠 | Council 合議（invocation_id: council-2026-04-30T14:50:00Z-wfbase1, judgment_confidence 0.75）で recommended。理由: (a) 哲学者の「フラクタル原則 P1 は WF 形状の単一性を要求する」少数意見を運用原則として組み込むことで、機能タイプ軸分業（職種軸分業と同型の罠）を構造的に予防、(b) 案 H の「観測ベース厚化」は早期 over-engineering を回避し YAGNI 原則と整合、(c) 既存処理フローが thin baseline を充足している事実から差分実装ゼロで運用開始可能、(d) 第 3 の道「単一 WF + 動的 context 注入」は v6.0.0 major 候補として温存、(e) Phase 3 で WF 単一化が確定したため論点 3（WF 選択責任）は構造的に消失し、新規ディスパッチャ等は不要 |
| 影響 | 既存 `layer1-autonomous-dev/SKILL.md §処理フロー` の不変化を v5.3.0 で明文化（「§処理フローが現行 WF の基底であり機能タイプ別分岐を含めない」と原則節に追記）。`references/` に `wf-baseline-rationale.md` を新設し、観測閾値・厚化トリガー・Council 再諮問条件を記録。L1 実装スコープは差分が極小（原則節 1 段落 + reference 1 件のみ） |

### AD-016: 献上トリガー第 4 種「Type D（異常献上）」を追加する

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF 論点 2（献上トリガー 4 種の関係）で、現行の Type A（仕様レビュー結果）/ Type B（成果物）/ Type C（仕様改訂提案）に対し、AI 自己解決不能な技術的例外（依存破損 / env 不能 / 想定外例外等）の献上経路が暗黙のままだった。Council で案 D（Type D 新設）が weighted_score 4.5 で recommended、哲学者は「第 3 の道: 献上 3 軸構造（トリガー × 中身 × 権限）の哲学化」を主張 |
| 判断 | philosophy.md §5（または現行 5 本柱規定の関連節）に Type D を minor 追加する。発動条件は **AI 自己解決不能な技術的例外**（依存破損・env 不能・想定外例外）に限定し、Type A（仕様起因）から経路分離する。哲学者の献上 3 軸構造は philosophy 第 8 条候補（第 7 条＝次元論と D4 の独立性 と並列の「献上 3 軸の存在論」）として温存し、v6.0.0 major 昇格時に併合検討 |
| 根拠 | Council 合議（invocation_id: council-2026-04-30T14:30:00Z-wfsurf1, judgment_confidence 0.72）で recommended。理由: (a) Type A（仕様改訂）と Type D（技術例外）は本質的に異なる経路（前者は L0 への差し戻し、後者は人間判断要請）であり混同は P3 責務分離違反、(b) 現状でも Type A に詰め込まれ実運用しているが暗黙化は philosophy P4 情報純度違反、(c) minor 追加で済むため major 昇格不要、(d) 哲学者の懸念（5 年スパンで Type E/F/G 追加要求が再発する罠）は 3 軸構造を v6.0.0 候補として温存することで構造的に応答 |
| 影響 | `layer1-autonomous-dev/SKILL.md §8 献上`の表に Type D 行を追加。`references/delivery-format.md` に Type D フォーマット節を追加（発動条件・必須項目・人間アクション期待値）。philosophy.md §5 に Type D 言及を 1 段落追加（哲学者意見の温存記述含む）。v6.0.0 候補として `history/INTENT.md` に「献上 3 軸構造」を温存記載 |

### AD-017: WF 選択責任は新規プロトコル不要、既存メカニズムで吸収

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF 論点 3（WF 選択責任）は当初「ユーザー指示を受けた時にどの WF を起動するか誰が決めるか」を問うていた。AD-015 により WF が単一形状で確定したため、選択問題自体が構造的に消失した |
| 判断 | 新規ディスパッチャ WF / 選択責任プロトコルを設計しない。残課題の 3 種（i 機能タイプ誤認 / ii モード判定誤り / iii 権限・CTL 誤り）は既存メカニズムで吸収する：(i) 既存 Type C（仕様改訂提案）、(ii) 既存「体制事後評価」、(iii) AD-016 の Type D（異常献上）。本判断は Council 起動せず実装者裁量で決定し、ユーザー承認 (Phase 4 「Phase 5 へ進む」) で確定 |
| 根拠 | (a) AD-015 の論理的帰結として WF 選択問題が消失、(b) 残課題 3 種が既存救済経路に 1:1 でマッピング可能、(c) Council 起動条件（philosophy §6 / `crosscut-council` 発動基準）「複数案拮抗・confidence < 0.6・不可逆操作」のいずれにも該当しない、(d) 実装者 confidence 0.75、(e) 「明確な仕様に基づく素直な実装」に該当 |
| 影響 | 設計差分ゼロ。WF 選択責任に関する spec/skill 改修は発生しない。本 AD は decision の不在（=「設計しない」）を明示記録するための meta-AD として機能（後年の再諮問抑止が目的） |

## v5.2.0

### AD-010: 5 次元論（D1〜D5）の導入と D-numbering 採用

| 項目 | 内容 |
|---|---|
| 状況 | DH の検証機構（5 層検出スタック / crosscut-verifier-drift / §7.4 自己検証等）が、それぞれどの抽象階層を対象にしているかが暗黙のままで、責務重複・責務漏れ判定が困難だった |
| 判断 | 5 次元論を導入：D1（ソースコード）/ D2（開発環境）/ D3（配布 skill インスタンス）/ D4（マスタ skill = メタスキル）/ D5（Meta モニタリング層 = 人間）。機械可読命名は D-numbering、思想文書では meta-layer / meta-meta-layer 等の階層形容詞を併走させる二重命名 |
| 根拠 | Council 合議（invocation_id: council-2026-04-29T21:00:00Z-d4mtr1, 論点 1）で D-numbering を recommended（judgment_confidence 0.78）。理由: (a) 既存 M1/M2/L0/L1/L2/CTL と prefix 衝突なし、(b) 短く grep 性能良好、(c) 案 b の T-numbering は既存予約のチーム軸 T1-T5 と衝突する致命的問題、(d) 案 c 階層形容詞は冗長で表記揺れリスク。哲学者の「関係性を呼び起こす命名は思想的支柱」少数意見を二重命名で吸収 |
| 影響 | layer0-spec-architect SKILL.md に v5.2.0 セクション追加、harness-verifier/PHILOSOPHY.md / BOUNDARY.md で 5 次元定義を明示。既存 skill の用語使用には影響なし |

### AD-011: D4 検査機構を DH 本体外（リポジトリルート直下）に独立配置

| 項目 | 内容 |
|---|---|
| 状況 | DH は生成物（D2/D3）の検証機構を完備していたが D4 自身の整合性検査が不在（靴屋の靴問題）。フラクタル原則 P1 の自然な拡張として「規律の自己相似性」を実装する必要があった。`.claude/skills/` 配下の crosscut-* skill として実装する案（crosscut-verifier-self-static 新設）と、DH 本体外に独立配置する案が拮抗 |
| 判断 | リポジトリルート直下 `harness-verifier/` に独立配置する。`.claude/skills/` 配下には置かない。`crosscut-verifier-drift` の拡張案も却下 |
| 根拠 | DH 内部 skill として実装すると自己言及パラドックス（自身が壊れたら自身を検査できない循環）が生じる。論理階層が一段違う（D4 vs D4 を検査する機構＝メタメタ層）ため Russell タイプ理論・Gödel 不完全性定理と同型の構造的回避が必要。HANDOFF §4.1 の特異点メタファに従う。Council 出力（案A: DH 内部 skill 新設）よりも哲学者の「特異点扱い」少数意見が、ユーザー確定の独立性要請（C: 一切影響されない独立性）と整合 |
| 影響 | 新規ディレクトリ `harness-verifier/` を作成。DH 本体（`.claude/skills/`）の挙動は完全不変。本機構は DH 本体に **読み取り専用** で依存（逆方向の依存は禁止） |

### AD-012: D4 検査機構の名称を `harness-verifier/` とする命名判断

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF 仮称 `self-monitoring/` は「self-」誤読リスク（自己が自己を監視＝独立性要請に反する読み）を持つ。命名候補: meta-verifier / harness-verifier / dh-integrity / singularity 等が拮抗 |
| 判断 | ディレクトリ名・機械可読名は `harness-verifier/` を採用。PHILOSOPHY.md 冒頭で「別名: singularity（特異点メタファ）」を併記する二重命名 |
| 根拠 | Council 合議（invocation_id 同上, 論点 2）で recommended（judgment_confidence 0.82）。理由: (a) `crosscut-verifier-drift` / `verifier-philosophy` と命名形式が同型でフラクタル原則 P1 整合、(b) 動詞由来（verifier）でファイル群の責務が明示、(c) grep 性能良好、(d) 外部説明コスト最小。哲学者の「singularity を命名で宣言する」少数意見は PHILOSOPHY.md 内で吸収 |
| 影響 | ディレクトリ名・コード・grep 対象では `harness-verifier` で統一。PHILOSOPHY.md においてのみ singularity 表記を保持 |

### AD-014: harness-verifier の glossary.yml を subset YAML 形式に限定する

| 項目 | 内容 |
|---|---|
| 状況 | 独立検証 (VERIFICATION-v5.2.0.md) で C-1 として、`harness-verifier/checks/glossary.py` の `_parse_yaml` が複数行 block list 構文 `- item` を誤読し、検査 5（用語辞書整合）が空回りしていた事象が判明。`forbidden_uses` の最初の要素消失、`crosscut_prefix.members` / `layern_prefix.members` の空 dict 化を確認 |
| 判断 | `glossary.yml` を **subset YAML 形式** に限定する。block list 構文を使用禁止とし、インライン list / list of dict のみ許容。パーサが block list 構文を検出した時点で `SyntaxError` を raise（黙って誤読しない）。BOUNDARY.md §9 に「独立性の代償」として明文化 |
| 根拠 | Council 合議（invocation_id: council-2026-04-29T22:30:00Z-c1fix1）で recommended（judgment_confidence 0.88）。3 ペルソナ全会一致で「案 b（インラインリスト書き換え）」を支持、開発者が「+ 案 a の防御コード」を補強、哲学者が「+ ドキュメント宣言」を補強する三段統合に着地。案 c（PyYAML 採用）は哲学者が「独立性要請の最初の妥協、5 本柱 P3（情報純度）侵食」と却下、本案件のスコープを越える BOUNDARY.md 改訂を要するため後送。subset YAML 制約により (i) C-1 即解消、(ii) 将来の偽陽性を構造的予防、(iii) 独立性要請の哲学的根拠強化を同時達成 |
| 影響 | `harness-verifier/glossary.yml` を subset YAML 形式に書き換え（forbidden_uses / members をインライン化）。`harness-verifier/checks/glossary.py` の `_parse_yaml` に block list 検出 → SyntaxError 機構を追加、加えてインライン list of dict 完全対応を含む全面改修（ネスト dict / quote 保持 / top-level split）。BOUNDARY.md §9「独立性の代償」を追加。glossary.yml 冒頭コメントで形式制約を明示。少数意見として「subset YAML が glossary 肥大化時に破綻したら PyYAML 採用を Council 再諮問」を温存 |

### AD-013: バージョン昇格を v5.2.0 minor とし philosophy verifier 本実装は v5.3.0 へ後送

| 項目 | 内容 |
|---|---|
| 状況 | 次元論導入 + D4 検査機構実装は (a) v5.2.0 minor / (b) v6.0.0 major / (c) v5.2.0 minor で次元論+D4 機構、philosophy verifier は v5.3.0 へ後送、の 3 案で拮抗 |
| 判断 | (c) v5.2.0 minor で次元論導入 + D4 検査機構（harness-verifier/）実装、`crosscut-verifier-philosophy` 本実装は v5.3.0 へ後送 |
| 根拠 | Council 合議（invocation_id 同上, 論点 3）で recommended（judgment_confidence 0.70）。理由: (a) 後方互換完全維持（新規ディレクトリ追加のみ、既存 SKILL.md / references / crosscut-* 不変）、(b) AD-008 / AD-009 の前例（後方互換維持で minor）と整合、(c) 開発者の semver 厳格論と経営者のリリース文脈説明可能性を両立。哲学者の「次元論導入は major 級の自己同定更新」少数意見は v6.0.0 で philosophy.md 第 7 条として吸収する候補として保持 |
| 影響 | v5.1.0 → v5.2.0、後方互換維持。`crosscut-verifier-philosophy/` placeholder は v5.2.0 でも未実装のまま、v5.3.0 候補として継続検討 |

## v5.1.0

### AD-008: L0 完了の定義をドキュメント生成完了から「scaffold smoke test 通過 + 受け入れ基準充足」へ再定義

| 項目 | 内容 |
|---|---|
| 状況 | PR #19 テストレビュー（シナリオ「ケロぴの森」）で L0 が SPEC.md / DONT.md / REGIME.md の生成は完遂したが、L1 が即座に開発開始できる scaffold が一切生成されず、参照ファイル 8 種も未読のまま L0 完了と判定されていた。L0 charter「AI 自律駆動開発が可能な開発環境の構築」が達成不能 |
| 判断 | L0 完了の定義を「ドキュメント生成完了」から「§0 受け入れ基準 4 条件すべて充足（仕様充足 / scaffold 実体生成 / smoke test 通過または保留事由明記 / §7.4 自己検証 PASS）」に再定義する |
| 根拠 | 5 本柱原則 P3（責務分離）と P4（情報純度）に整合。L0 が「実行可能な開発環境を作る」という charter を満たさないまま L1 へ譲渡することは責務不履行であり、人間 ≒ Council 原則（philosophy.md 第6条）の観点でも検証層の前段で受け入れ基準を確定する必要がある |
| 影響 | SKILL.md §0 に受け入れ基準セクションを追加。Lifecycle ≥ 1 既存プロジェクトには段階適用とし、既存成果物の遡及修正は要求しない（後方互換維持） |

### AD-009: scaffold-checklist の単一 stack（Vite+TS+React+PWA）採用方針

| 項目 | 内容 |
|---|---|
| 状況 | scaffold-checklist.md を新設するにあたり、複数 stack を初期から網羅するか単一 stack に絞るかを判断する必要があった |
| 判断 | v5.1.0 では Vite + TypeScript + React + PWA の **1 stack に絞る**。他 stack（Next.js / Vue / Astro / SvelteKit / 純 Node CLI）は将来 minor で追加 |
| 根拠 | (a) PR #19 テストレビュー対象が M2 monolith Web PWA で本 stack に直結する、(b) scaffold-checklist は「実体ファイルの厳密な必須リスト」が責務であり、stack ごとに必須要件が異なるため網羅は本リリース範囲を逸脱、(c) 利用者数が多い stack を一つ確定させてから stack 別の最小要件パターンを抽出するほうが将来 minor の品質が上がる |
| 影響 | 他 stack を使う既存プロジェクトでは scaffold-checklist の対象外となるが、§0 受け入れ基準 2「対応 stack テンプレートで指示されたファイル群」と表現することで「対応 stack なし → 該当条項は適用対象外」と扱える。将来 minor で stack 追加時は scaffold-checklist 内の「将来拡張ポイント」表に従う |

## v5.0.0

### AD-001: crosscut- prefix の導入

| 項目 | 内容 |
|---|---|
| 状況 | council/ は「全 Layer 横断」の判定機構だが、命名が層構造を示していなかった |
| 判断 | `crosscut-` prefix を Level A skill の第二の命名規則として確立し、`council/` を `crosscut-council/` にリネーム |
| 根拠 | spec §3.1.3 / §4.1。3 層 + 1 横断の構造を命名で明示化、フラクタル原則 P1 に整合 |
| 影響 | 後方互換破壊（major 昇格）。既存プロジェクト側の参照は migration-guide で個別対応 |

### AD-002: dev_mode 軸の追加

| 項目 | 内容 |
|---|---|
| 状況 | 既存軸（規模 S / 不確実性 U / リスク R / NFR N / Lifecycle）に GitHub 連携前提の判定軸が無かった |
| 判断 | dev_mode 軸（local_only / github_assisted / github_autonomous）を 3 軸目の動的判定軸として追加 |
| 根拠 | spec §3.2.1〜§3.2.3。GitHub 無しでも DH ベースは完全動作の原則を保ちつつ段階的移行を可能にする |
| 影響 | regime-assessment.md / REGIME.md テンプレ拡張。後方互換あり（既存プロジェクトは local_only 相当として扱える） |

### AD-003: 仕様 1〜4 を crosscut- skill 化

| 項目 | 内容 |
|---|---|
| 状況 | GitHub 連携の 4 仕様（Issue 射出・実装・検証・還流）は L0/L1/L2 のいずれにも純粋には属さず、横断的に発動する |
| 判断 | 仕様 1〜4 を `crosscut-issue-dispatcher` / `crosscut-issue-implementer` / `crosscut-verifier-drift` / `crosscut-verifier-philosophy` (placeholder) / `crosscut-feedback-loop` の 5 skill として配置 |
| 根拠 | spec §4.3。3 層 + 1 横断構造の維持、責務分離（P3）、各 skill の同型構造によるフラクタル原則発現 |
| 影響 | 新規 skill 5 件追加。layer1-* から参照を追加、既存 layer 機構は不変 |

### AD-004: CTL 連動条件分岐の組み込み

| 項目 | 内容 |
|---|---|
| 状況 | CTL システム（v4.2 で追加）は判定ロジックは存在したが、各 skill の動作分岐に組み込まれていなかった |
| 判断 | 仕様 1〜4 すべての protocol references で CTL-0/1/2/3 の段階的自動化を明文化 |
| 根拠 | spec §3.2.4〜§3.2.7、§4.4。再帰進化原則 P2 を CTL 育成戦略として実装 |
| 影響 | 各 crosscut- skill 配下に protocol.md を追加。CTL 育成戦略は ctl-maturity-strategy.md として独立 |

### AD-005: claude-code-action 公式採用

| 項目 | 内容 |
|---|---|
| 状況 | Issue → 実装の自動化手段として複数選択肢があった |
| 判断 | Anthropic 公式の claude-code-action を採用、GitHub Actions 雛形に組み込み |
| 根拠 | spec §3.2.5、§3.2.9。業界 BP 取り込み、保守性、エコシステム整合性 |
| 影響 | templates/.github/workflows/issue-to-impl.yml の依存。バージョンは `<latest>` プレースホルダ（実装時点で公式リポジトリ確認） |

### AD-007: docs/ ディレクトリの限定許可

| 項目 | 内容 |
|---|---|
| 状況 | リポジトリは "skill-only policy" (PR #3) で `docs/` を gitignore 済み。spec §5.4.2 が `docs/migration-guide-v5.0.0.md` を v5.0.0 配布物として要求 |
| 判断 | `docs/` 全体の gitignore は維持しつつ、配布対象の migration guide のみを許可（`!docs/migration-guide-*.md`） |
| 根拠 | 設計ドラフト（drafts policy）と配布ドキュメント（migration guide）は性質が異なる。最小例外で skill-only policy の精神を保つ |
| 影響 | `.gitignore` 1 行追加。今後の v6.0.0 以降の migration guide も同パターンで許可される |

### AD-006: README バッジ作業のスキップ（適用対象外）

| 項目 | 内容 |
|---|---|
| 状況 | spec §4.6.2.4 で README に v5.0.0 バッジを追加する指示があるが、リポジトリルートに README.md が存在しない |
| 判断 | README バッジ追加作業はスキップ。SKILL.md バージョン履歴 / credit-template.md / REGIME-LOG.md でバージョン更新を完結させる |
| 根拠 | スキルは SKILL.md の frontmatter + 本文が標準。README は人間向けプロジェクト紹介で本案件のスコープ外。SELF-VERIFICATION §5.3.2 で「適用対象外」明記 |
| 影響 | バージョン更新は他経路で完結。README 整備は別案件として保留 |
