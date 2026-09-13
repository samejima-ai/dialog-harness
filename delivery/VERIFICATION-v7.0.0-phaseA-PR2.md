# VERIFICATION.md — upgrade-spec v7.0.0 Phase A / PR-2（F6 叡智層の失効セマンティクス・独立検証）

## 判定: PASS（警告付き・差戻し推奨事項あり）

- PASS の意味: 「spec §F6 の受け入れ基準 (a)〜(f) と §2 不変条件（I-1 / I-3 / I-4）を決定論の実行結果で全通過 ∧ 試行した反証のうち SPEC 記載の保証を破るものが無い」。正しさの証明ではない（§反証記録「この PASS が保証しない範囲」参照）。
- 反証で見つかった欠陥（F-5d 引用符付き値の黙殺・F-5f 複数行インライン形の退行・F-7 非 UTF-8 crash 等）は、規格文書 §失効 が定める書式（引用符なし・単一行 `{ }` / ブロック / 引用ブロック）の**外側**で起きる堅牢性欠陥であり、FAIL 条件（SPEC 記載の保証を破る）には該当しない。差戻し**推奨**（非ブロッキング）として §未解決・差戻し事項 に提起する。
- **検証途中で対象が 2 回動いた**（未 commit worktree → commit `c1451ac` → fix commit `247b7e3`）。決定論の実行結果・反証は最終 HEAD `247b7e3` で全件取り直した（§体制情報）。判定は最終 HEAD に対するもの。

## 体制情報

- 検証者: layer1-independent-reviewer（新規文脈・実装コンテキスト非継承。本プロンプト以外の会話履歴なし）
- 対象: branch `claude/harness-era-philosophy-7vachm`、`git diff origin/master...HEAD`（2 commits: `c1451ac` feat / `247b7e3` fix、13 files / +369 −5）。merge-base = `origin/master`（`a7e41c1`）= PR-1（#288）merge 後に分岐。**`git log origin/master..HEAD` に PR-1 のコミットは含まれない**（Council 案C 運用規則・機械確認）
- Mode: M2 / LC=1（history/ 照合あり）
- 参照した入力: `dh-upgrades/upgrade-spec-v7.0.0.md` §2・§F6（実装注記 (1)〜(4) 含む）・§8、対象 7 ファイル + `history/INTENT.md` / `history/REGIME-LOG.md` の diff、`.claude/skills/layer1-independent-reviewer/SKILL.md`、`references/falsification-protocol.md`、`delivery/VERIFICATION-v7.0.0-phaseA-PR1.md`（構成の参照）、`philosophy.md` 第 8 条（読取のみ・I-1 対象）
- 読まなかったもの: `history/COUNCIL-LOG.md`、`~/.claude/council-data/`（禁止）
- **読み順制約（F4）の適用記録**: 順序 = spec §2/§F6 → diff（CHANGELOG を除く）→ 決定論実行 → 反証 F-1〜F-8 / M-1〜M-7 → **判定確定** → `delivery/DELIVERY-v7.0.0-phaseA-PR2.md` / `delivery/HANDOFF-v7.0.0-phaseA-PR2.md` / `history/CHANGELOG.md` PR-2 節を開く → 三点突き合わせ。検証開始時点で DELIVERY / HANDOFF は未着（`delivery/` に PR1 の 3 本のみ）、commit `c1451ac` で着いた。CHANGELOG の diff は判定確定まで `git diff -- history/CHANGELOG.md` を発行せず開かなかった
- 対象の移動: 検証開始時は未 commit（`git diff HEAD` 11 files）。途中で `c1451ac` に commit され（+DELIVERY / HANDOFF）、さらに `247b7e3`（`extract_revoked` のインライン window 修正 + テスト 3 件。変更は `scripts/` 2 本のみ、規範文書は不変）が積まれた。反証 F-5e（`{` が宣言の後ろにだけある行）は `c1451ac` で成立していたが `247b7e3` で解消。逆に F-5f（複数行インライン形）は `c1451ac` で成立せず `247b7e3` で退行した（§反証記録）
- 復元規律: `git stash` / `git checkout --` は使わず、mutation は scratchpad の HEAD コピーから復元。一時ファイルは `git add` → 走査 → `git rm --cached` + `rm`。各試行後および最終の `git status --short` は試行前スナップショット（空）と一致。本ファイルの新規作成のみが差分

## 決定論の実行結果（判定の一次根拠・HEAD `247b7e3`）

| 実行 | 結果 |
|---|---|
| `python3 harness-verifier/verify.py --strict` | exit 0・**総合判定: PASS**（11 項目全 PASS・FAIL 0） |
| `for t in scripts/test-*.py` 14 本 | 全 exit 0（`test-norm-scan.py` は ok 44 行・F6 節 14 check 含む） |
| `for t in scripts/test-*.sh` 4 本 | 全 exit 0 |
| `python3 scripts/norm-scan.py` | 走査 23 / 時限トリガ 39（発火 **0** / 未発火 14 / 機械判定しない 25）/ **失効済みで購読に残る規範: 0 件（宣言不完全 0）**。未 commit 時点では発火 2（`dev-env-spec.md` の `model_generation` ×2、最終 commit 09-06 < 世代 epoch 09-13）→ commit 後 0（DELIVERY の予告どおり） |
| `python3 scripts/norm-scan.py --json` | top-level keys に `revoked` あり（`scanned_files / total_triggers / fired / not_fired / undecidable / lifecycle_stage / revoked`）。`revoked: []` |
| `git diff origin/master...HEAD --stat -- '*philosophy.md' '*delegation-boundary.md' '*auto-merge-boundary.md'` | **空（0 バイト）** — I-1 充足 |
| `git log origin/master..HEAD` | 2 commits（`c1451ac`, `247b7e3`）。merge-base = `origin/master` → PR-1 コミット 0 件 |
| `git grep -n -E "status:[[:space:]]*revoked" -- '*.md' '*.py' '*.yml' '*.yaml'` | **0 件**（exit 1）。走査器・テスト・規格文書 4 本が自己誤列挙されないことの根拠（F-6） |
| 相対リンク・§ 参照の実在（F-8） | `dev-env-spec.md` L1081 `## 規範メタデータ` / L1100 `### 失効` / `metabolism-regime.md` L57 `## 2.` + L65 `### 昇降格` + L104 `### 排出` / `ritual-protocol.md` L175 `3.5.`（F2.6 内）+ L182 `4. 非対称原則` / `history-layer-spec.md` の `../../layer0-reindex-librarian/references/metabolism-regime.md` 解決可 / `philosophy.md` L450 `## 第8条` / `history/DH-PHILOSOPHY-INSIGHTS.md` 実在 / `templates/rules/common/*.md` 5 本に `> ROLE:` 行あり — dead 0 |
| `status: frozen` の既存例（G-AGENT・`dev-env-spec.md` 1 箇所） | `extract_revoked(実ファイル)` = `[]`（F-4） |

## 仕様合致（spec §F6 受け入れ基準 (a)〜(f)）

| 項 | 受け入れ基準 | 検証方法 | 判定 |
|---|---|---|---|
| (a) | メタデータ規格に `status` / `revoked_at` / `superseded_by` の 3 フィールド | `dev-env-spec.md` §規範メタデータ 表に 3 行追加（L1092-1094）。`status` の値域 `active（既定）/ frozen / revoked`、`revoked_at` は revoked 時必須、`superseded_by` は `<path#anchor>` または `none`（実装注記 (2)）。新設 §失効 に宣言 / 効力 / 列挙 / 適用対象 / 宣言主体 | **PASS** |
| (b) | norm-scan が「revoked なのに HOT/WARM に残る規範」を列挙する（判定はしない） | `scan()` に `revoked` キー、`render()` に「失効済みで購読に残っている規範」節。反証 F-1: tracked 一時ファイル（`templates/rules/common/` + `history/` 本体）の宣言 3 件 + ブロック形 1 件を列挙、`history/archive/` / `delivery/` / `dh-upgrades/` は除外（F-3）。F-2: `revoked_at` 欠落 → 「**宣言不完全**」別枠。出力に判定語なし（「COLD へ？と人間に問う」） | **PASS** |
| (c) | 儀式 F2.6 に「失効済み N 件が購読に残っています。COLD へ？」の問い | `ritual-protocol.md` F2.6 に 3.5 追加: 「失効済み規範 N 件が購読（HOT / WARM）に残っています。COLD へ移送しますか？（一括移送 / 個別に確認 / 後で）」。宣言不完全は補完を先に問う。判定はしない | **PASS**（語句は spec と同義・非逐語。提起 #13） |
| (d) | reindex-librarian の COLD 移送条件に「revoked は次サイクルで COLD」 | `metabolism-regime.md` §2 昇降格表に `HOT / WARM → COLD（失効）` 行（次サイクルの排泄で移送・結晶化完了の確認は失効宣言が代替・`superseded_by` を逆引きに残す・宣言不完全なら移送しない）+ §4 排出に例外 1 項。`history-layer-spec.md` §archive「2 年を待たず」+ `deprecation-protocol.md` 手順 3（実装注記 (3)） | **PASS** |
| (e) | 適用対象を INTENT.md 以外（罠エントリ / RL frontmatter / DH-PHILOSOPHY-INSIGHTS.md の各節）へ拡張 | §失効「適用対象」に 3 種を明記（RL は `> ROLE:` 群に 1 行 — 実 RL 5 本に `> ROLE:` 行あり）。走査は `history/` 本体を含む（`REVOKED_EXCLUDE_PREFIXES` に `history/` なし、F-1 で `history/zz-tmp-insights.md` を列挙）。INTENT 廃止マーカーは機能記録として残す（二重管理回避） | **PASS**（規格として。実適用例 0 = 実装注記 (4)・人間判断） |
| (f) | 規範メタデータ `review_trigger: [model_generation, cycles: 6]` | `dev-env-spec.md` L1102（§失効 直下）+ `norm-scan.py` docstring L46-47。norm-scan が `dev-env-spec.md — [cycles] 6 cycle 相当まで残り 78〜84 日` として列挙 | **PASS** |
| I-1 | L-FROZEN 3 文書 0 バイト | 上表 | **PASS** |
| I-3 | 失効列挙に LLM 判定なし | `find_revoked_files`（git grep）/ `extract_revoked`（正規表現）/ `scan_revoked` のみ。判定語・LLM 呼出なし | **PASS** |
| I-4 | 追加規範に `review_trigger`（`model_generation` 必須） | 正本 §失効 と norm-scan docstring に付与。衛星 4 文書（ritual 3.5 / metabolism / deprecation / history-layer）は正本を指すのみで自前の時限なし | **PASS**（提起 #11） |
| 実装注記 (1)〜(4) | history/ 含む・`none` 明示・deprecation / history-layer 追記・第一適用例なし | 上記各行 + spec 側にも同注記が追記済み（spec diff）。実リポ列挙 0 件が空振りでないことは F-1（実走査で 4 件）+ F-6（自己一致 0）で実証 | **PASS** |

## 動作・使用確認

- 起動: `norm-scan.py` plain / `--json` / `--fired-only` とも exit 0。JSON の `revoked` は `--fired-only` でも保持
- エラーハンドリング: 存在しないパス / ディレクトリを `scan_revoked(files=[...])` に渡しても crash せず `[]`（F-7）。非 UTF-8 ファイルは `UnicodeDecodeError` で crash（F-7・提起 #6。`scan()` と同型の既存パターン）
- 使用（儀式の経路）: 宣言（人間）→ 列挙（norm-scan・F2.6-1 で既に走る）→ 問い（F2.6-3.5）→ 移送（reindex 次サイクル・Dry-run 既定）。**未追跡（未 `git add`）の宣言は git grep に見えない**（F-1 untracked = 0 件）。儀式が commit 前の作業ツリーで走る場合、書いたばかりの宣言は列挙されない（提起 #7）
- 規格 §失効 の書式「インライン・ブロック・引用ブロックのいずれでも可」は F-5b / F-5c / F-1 ブロック形で列挙を確認

## 配置規則（5.5）/ 履歴整合性（5.8）/ クレジット（5.6）

- delivery/: `DELIVERY-* / HANDOFF-* / VERIFICATION-*` の版サフィックス命名は PR-1 と同一慣行。ルート直下の作業メモ混入なし（`git status --short` 空）
- 5.8: INTENT は追記のみ（廃止・訂正なし）。REGIME-LOG は PR-2 節を追加。過去 INTENT との矛盾・廃止機能の回帰・却下案の再提案: 検出なし。F6 は v6.13.0 F5（norm-scan「判定しない」）と同じ規律を継承しており逆向きの実装ではない
- 5.6: README.md 無変更・DH 本体は対象外

## 反証記録（Falsification・5.10）

| # | 類型 | 試行 | 期待 | 結果（HEAD `247b7e3`） | 復帰確認 |
|---|---|---|---|---|---|
| F-1 | A（挙動） | `templates/rules/common/zz-tmp.rules.md` に完全宣言（インライン）+ ブロック形、`history/zz-tmp-insights.md` に完全宣言を置き `git add` | 列挙される | **untracked では 0 件**、tracked で **4 件**（history 本体 1 + rules 3）。render 「失効済みで購読に残る規範: 4 件（宣言不完全 1）」 | `git rm --cached` + `rm` → status 一致 |
| F-2 | A | 同ファイルに `revoked_at` 欠落の宣言 | 「宣言不完全」別枠 | `complete: False`、render で `**宣言不完全** — …:8 — revoked_at: (欠落)` | 同上 |
| F-3 | A | `history/archive/2026-06/` / `delivery/` / `dh-upgrades/` に同じ宣言を tracked で配置 | 列挙されない | 3 本とも非列挙（COLD / 献上物 / 移行仕様の除外規則） | 同上 |
| F-4 | A | `dev-env-spec.md` 実ファイル（G-AGENT `status: frozen`）と `status: revoked_pending / unrevoked / active` | 失効と誤認しない | `[]`。`\b` により `revoked_pending` も非一致 | 読取のみ |
| F-5a | A（書式ゆれ） | 1 行に 2 宣言 | 2 件 | **1 件**（`search` が最初のみ。under-count・提起 #3） | — |
| F-5b/c | A | `{}` 無しブロック形 / 引用ブロック形 | 列挙 | 両方 complete で列挙 | — |
| F-5d | A | `status: "revoked"`（値に引用符） | 列挙 or 不完全 | **`[]` — 黙って落ちる**。git grep パターンと `STATUS_REVOKED_RE` が引用符非対応。一方 `revoked_at` / `superseded_by` は引用符を許す（テスト自身が `revoked_at: "2026-09-01"`）。規格 §失効 の書式は引用符なしのため SPEC 保証外（提起 #2） | — |
| F-5e | A | `- status: revoked, revoked_at: …, superseded_by: none（参照 {x}）`（`{` が宣言の後ろだけ） | complete | `c1451ac`: **不完全に誤分類**（`rfind` = −1 → window が末尾 1 文字）→ `247b7e3` で解消し complete。ただし `superseded_by` = `none（参照`（終端が全角括弧で止まらない・提起 #4） | — |
| F-5f | A | 複数行インライン `` `{ status: revoked,`` ↵ `` revoked_at: …, superseded_by: none }` `` | complete | `c1451ac`: complete → **`247b7e3` で退行: 不完全に誤分類**（`lb >= 0` かつ同行に `}` 無し → 行末で打ち切り、ブロック経路へ落ちない）（提起 #1） | — |
| F-5g | A | ブロック形で `revoked_at` が 9 行目 | complete | 不完全（`i + 8` 上限。docstring「空行まで」と不一致・提起 #5） | — |
| F-5k | A | 閉じ `}` 無しインライン | 行末まで読む | complete（`247b7e3` の新規 check と一致） | — |
| F-6 | C（Oracle） | 走査器 / テスト / 規格文書 4 本が `status:[[:space:]]*revoked` に自己一致しないか | 0 件 | **0 件**（`status` と `revoked` を隣接させない書き方。実リポ 0 件が空振りでない根拠） | 読取のみ |
| F-7 | A（異常系） | `scan_revoked(files=["nope.md"])` / `["d"]`（ディレクトリ）/ 非 UTF-8 ファイル | crash しない | 不在・ディレクトリは `[]`。**非 UTF-8 は `UnicodeDecodeError` で crash**（`OSError` のみ捕捉）。到達条件は「git grep が一致する非 UTF-8 の md/py/yml」に限られ実リポに該当なし（提起 #6） | tmp dir |
| F-8 | C | 新設 §失効・F2.6-3.5・§2 昇降格 等の相対リンク / § 参照の実在 | dead 0 | dead 0（§決定論 表） | 読取のみ |
| M-1 | B（ミューテーション） | `REVOKED_EXCLUDE_PREFIXES` に `history/` を追加 | test FAIL | FAIL 2 件 | HEAD コピーから復元・diff 一致 |
| M-2 | B | `complete` を常時 True | test FAIL | FAIL 1 件 | 同上 |
| M-3 | B | `scan()` から `revoked` キーを削除 | test FAIL | FAIL 1 件 | 同上 |
| M-4 | B | `extract_revoked` の `> ` strip を除去 | test FAIL | **exit 0（生存）** — 等価ミュータント: `extract_revoked` はインデントを使わないため strip は結果に影響しない no-op。テストの弱さではなくコードの冗長（提起 #8） | 同上 |
| M-5 | B | `STATUS_REVOKED_RE` を `(revoked\|frozen)` に | test FAIL | FAIL 2 件（G-AGENT 誤認検出） | 同上 |
| M-6 | B | `247b7e3` の修正を戻す（`rfind("{")` を全域に） | test FAIL | FAIL 1 件（新規 check「宣言より後ろにしか { が無い行」） | 同上 |
| M-7 | B | ブロック window を 8 → 1 行 | test FAIL | FAIL 1 件（引用ブロック形） | 同上 |
| 静的 | B | 恒真 / over-mock / 自己整合の検出 | — | 「実リポの走査結果に revoked が載る」は `isinstance(list)` のみ（弱いが M-3 で FAIL 化を確認）。`find_revoked_files`（git grep 経路）はテストが `files=` で迂回しており未観測 → F-1 で実走査を補った | — |

- 全試行後の `git status --short` は試行前スナップショット（空）と**完全一致**。`scripts/norm-scan.py` / `scripts/test-norm-scan.py` は HEAD コピーと `diff -q` 一致。本ファイルの新規作成のみが差分
- **この PASS が保証しない範囲**:
  - 儀式 F2.6-3.5 の問いが実セッションで実際に発せられること（手順書の記述確認のみ。儀式は LLM 実行）
  - reindex-librarian の排泄が `status: revoked` を実際に COLD へ移送すること（`metabolism-regime.md` の規則追記のみ。移送コードは存在せず Dry-run 既定・初回移送は未実行）
  - 規格 §失効 の書式外の宣言（引用符付き値・複数行 `{ }`・1 行複数宣言・9 行超ブロック・全角括弧直後）が正しく列挙されること（F-5 で欠陥を確認済み・提起 #1〜#5）
  - 未追跡ファイルの宣言（git grep 非対象・提起 #7）
  - 非 UTF-8 ファイル（提起 #6）
  - `history/DH-PHILOSOPHY-INSIGHTS.md` の**実際の節**に宣言を置いた場合の挙動（一時ファイルを `history/` 直下に置いて代替。同ファイル自体は改変していない）
  - Council 諮問 `v7phsa` が PR-2 の規範文書改変を包含すること（COUNCIL-LOG 非参照・人間判定事項）
  - DELIVERY の「総数 34 → 39 = +5」の内訳（origin/master 側の再走査は行っていない。docstring hunk に `model_generation` + `cycles: 6` の 2 行追加は確認）
  - F3 / Phase B は本 PR の対象外

## 三点突き合わせ（5.9: DELIVERY / HANDOFF / CHANGELOG PR-2 節 vs 実装 vs 検証結果）

| # | 記載 | 実装・検証結果 | 乖離 |
|---|---|---|---|
| T-1 | DELIVERY L42 / CHANGELOG「`test-norm-scan.py`（F6 **12** 項目）」 | `c1451ac` で 11 check、`247b7e3` で +3 = **14 check** | **計数不一致**（12 はどの時点とも一致しない） |
| T-2 | DELIVERY は fix commit `247b7e3`（Copilot review #289 対応・`extract_revoked` window 修正）に言及なし。CHANGELOG も同様 | HEAD に含まれる | 献上物が最終 HEAD を反映していない（提起 #9） |
| T-3 | DELIVERY L10 / L33「`git log origin/master..HEAD` = 0 件」 | commit 後は 2 件（PR-2 自身）。**PR-1 コミット 0 件**の意味では一致 | 文言が commit 前の状態（提起 #9） |
| T-4 | DELIVERY L43「発火 2 / 未発火 12」 | commit 後は発火 0 / 未発火 14（DELIVERY L65 自身が「commit されれば消える」と予告） | 予告どおり。数値は commit 前（提起 #9） |
| T-5 | DELIVERY L43「走査 23 / 39 / 25」・「失効済み 0（宣言不完全 0）」 | 一致 | なし |
| T-6 | DELIVERY L44「`git grep … status:[[:space:]]*revoked` 実リポ 0」 | F-6 で 0 件 | 一致 |
| T-7 | DELIVERY (b)「実リポ 0 件。fixtures で列挙を実証」 | F-1 で実走査（git grep 経路）でも列挙を確認 | 一致（本検証が経路を補強） |
| T-8 | DELIVERY L9 / L30「人間確認事項 **#1**」 | DELIVERY に番号付き人間確認事項リストなし（§未解決事項 は無番号） | 参照先不在（提起 #10） |
| T-9 | DELIVERY L23 付随「`ritual-protocol.md` F2.6-2 の `model_generation` 説明を F7 後の実装に訂正」 | diff に該当行あり（yml 併用） | 一致 |
| T-10 | DELIVERY L24 / CHANGELOG / spec 状態行「F8 / F9 を『済』に訂正」 | spec diff で確認。PR-1 VERIFICATION も F8 / F9 を PASS としており整合 | 一致 |
| T-11 | DELIVERY L59 仕様改訂提案 2「`superseded_by: none`」 | spec §F6 実装注記 (2) として spec 側に反映済み | 一致 |
| T-12 | DELIVERY L76「PR-1 節の見出しを『merge 済み』に」 | CHANGELOG diff で確認 | 一致 |
| T-13 | DELIVERY L79「INTENT の廃止・訂正なし」 | INTENT diff は追記のみ | 一致 |
| T-14 | HANDOFF L13「失効済み N 件が残っています。退避しますか？」/ L25「『失効済みで購読に残る規範: 0 件』が出れば配線済み」 | render 文言と一致（出力 6 行目・`head -8` 内） | 一致（平易化） |
| T-15 | HANDOFF L29「Council 自律判定 0 件」/ REGIME-LOG「Council 新規発動なし」 | Council 記録は読んでいない | 検証対象外（保証範囲外） |
| T-16 | REGIME-LOG「規範文書 5 本の改変 → `human-review-needed`」 | 5 本（dev-env-spec / ritual / metabolism / deprecation / history-layer）一致 | 一致 |
| T-17 | CHANGELOG「`scripts/test-*` 18 本 PASS」 | 14 + 4 = 18・全 exit 0 | 一致 |
| T-18 | DELIVERY L70「規格文書の例外を走査器に持たせない（allowlist を作らない）」 | `REVOKED_EXCLUDE_PREFIXES` は接頭辞 3 件・理由併記。allowlist なし | 一致 |

## 未解決・差戻し事項（提起のみ・訂正は L1 / L0）

差戻し推奨（L1・非ブロッキング。PASS 判定は維持）:

1. **複数行インライン形の退行（F-5f）**: `247b7e3` で `lb >= 0` かつ同行に `}` が無い場合に行末で打ち切るため、`{ status: revoked,` ↵ `revoked_at: …, superseded_by: … }` が「宣言不完全」に誤分類される（`c1451ac` では complete）。同行に `}` が無ければ次行以降（空行または `}` まで）へ window を継ぐ。テストに複数行 `{ }` を 1 件追加
2. **引用符付き値の黙殺（F-5d）**: `status: "revoked"` は git grep パターン・`STATUS_REVOKED_RE` とも非一致で**黙って落ちる**（「黙って捨てない」規律と不整合）。`revoked_at` / `superseded_by` 側は引用符を許しており非対称。走査器で `"?revoked"?` を許すか、規格 §失効 に「値は引用符なし」を明記するかを L1 が選ぶ（後者なら `revoked_at` の引用符許容も揃える）
3. **1 行複数宣言（F-5a）**: `search` が最初の 1 件のみ → under-count。`finditer` で宣言ごとに window を切る
4. **`superseded_by` の終端（F-5e 変種）**: `[^\s,}\"]+` は全角括弧・句読点で止まらず `none（参照` を取り込む。終端集合に `（）、。` 等を追加するか、規格に「値の直後は空白か `}`」と明記
5. **ブロック形の 8 行上限（F-5g）**: docstring「宣言行から空行まで」と実装 `lines[i+1:i+8]` が不一致。上限到達時は理由を出すか docstring を実態に合わせる
6. **非 UTF-8 crash（F-7）**: `read_text` の `UnicodeDecodeError` を捕捉（`errors="replace"` または except）。`scan()` 側も同型
7. **未追跡ファイルの宣言が不可視（F-1 untracked = 0）**: `git grep` は追跡ファイルのみ。儀式 F2.6 が commit 前の作業ツリーで走ると書いたばかりの宣言が列挙されない。`--untracked` を付けるか、規格 §失効 に「宣言は commit 後に列挙される」を明記（`find_files` の `review_trigger` 走査も同じ既存挙動）
8. **等価ミュータント（M-4）**: `extract_revoked` の `> ` strip は結果に影響しない no-op。コメント「引用ブロック内の宣言も拾う（extract_triggers と同じ理由）」は誤解を招く。削除するか「インデント非依存のため不要だが対称性のため残す」に改める
9. **献上物の最終 HEAD 追随（T-1〜T-4）**: DELIVERY / CHANGELOG の「F6 12 項目」→ 14、fix commit `247b7e3`（Copilot #289）の記載、`git log origin/master..HEAD = 0 件` → 「PR-1 コミット 0 件（2 commits）」、norm-scan 発火 2 → 0（commit 後）
10. **DELIVERY「人間確認事項 #1」の参照先不在（T-8）**: 番号付きリストを置くか、§未解決事項 の該当項目を指す

spec 追随 / L0（人間判定）:

11. **I-4 の衛星文書**: ritual 3.5 / metabolism §2 行 / deprecation 手順 3 / history-layer §archive は自前の `review_trigger` を持たず正本 §失効 を指す。集約自体は妥当だが、衛星側に「時限は `dev-env-spec.md` §失効 に従う」の 1 行があると norm-scan の網羅性が読める（I-4 の解釈を人間が確定）
12. **走査範囲の二重化**（DELIVERY 提案 1 と同旨）: `review_trigger` は `history/` 全除外、失効列挙は `history/archive/` のみ除外。spec §F6 実装注記 (1) で spec 側に記録済み。統一の時期を人間が決める
13. **儀式 F2.6-3.5 の問い文言**は spec（「失効済み N 件が購読に残っています。COLD へ？」）と語句が異なるが同義。spec を実装文言に合わせるか、そのままか

人間確認:

14. **第一適用例**: 実リポで `status: revoked` の規範は 0 件。何を失効させるかは採用判断（第 8 条）。候補があれば F2.6-3 の「廃止」で宣言し、初回は reindex Dry-run に載るところまで
15. **Council 諮問の扱い**: escalation-matrix「規範文書改変の実装前 → Council」を `v7phsa`（案C）で通過扱いとした点（DELIVERY 自認・PR-1 と同じ扱い）。別途諮問が要るかは人間判定
16. **移送の実行主体**: `metabolism-regime.md` の規則追記のみで、`status: revoked` を読んで COLD へ動かすコードは無い（reindex-librarian は LLM 実行の skill）。次サイクルで実際に移送されるかは儀式実行時の目視

---

## 実装側の是正記録（事後追記・検証者の本文は不変）

独立検証の差戻し推奨のうち実装側 #1〜#10 を同ターンで是正（本 PR 3 commit 目）。#1 複数行インライン形は「同一行で `{ … }` が閉じる場合のみインライン、それ以外は宣言行から空行または `}` までのブロック」に統一 / #2 `status` の値の引用符を許容（git grep パターンも同様）/ #3 `search` → `finditer` / #4 `superseded_by` の終端に全角括弧・読点・backtick を追加 / #5 ブロック形の 8 行上限を撤廃（空行まで）/ #6 `UnicodeDecodeError` を `scan()` / `scan_revoked()` 両方で degrade / #7 `git grep --untracked` / #8 no-op の `> ` strip を除去し docstring に理由を記載 / #9・#10 DELIVERY / CHANGELOG の計数・参照を訂正。各項に回帰テストを追加（F6 節 14 → 20 check）。#11〜#13 は DELIVERY §仕様改訂提案、#14〜#16 は DELIVERY §未解決事項 H-1〜H-3。是正後: `verify.py --strict` PASS / test 18 本 PASS / 実リポの失効列挙 0 件（`--untracked` でも自己一致なし）。
