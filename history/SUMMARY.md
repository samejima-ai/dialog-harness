# history SUMMARY — HOT エントリポイント（DH 本体 / reduction_target: DH）

> 情報代謝の **HOT 結晶層への入口**。振り返り儀式・文脈ロードは、まず本ファイルを既定ロードし、
> `history/` 全体（〜17k 行）には触れない。これが購読量と history 蓄積量の線形連動（代謝天井）を断つ要。
> WARM 台帳は「直近 N 件＋要約」のみ、COLD は既定ロードしない（必要時に明示 retrieve）。
> 設定値は `history/.metabolism-config.yml`、消化カーソルは `history/.metabolism-cursor.yml`。

## HOT（結晶層・常時ロード対象・密な現役叡智）

| ファイル | 役割 |
|---|---|
| `INTENT.md` | WHY 層（設計意図の現役正本） |
| `ARCH-DECISIONS.md` | ADR（確定アーキテクチャ決定） |
| `DIMENSIONS.md` | 5 次元論（確定叡智） |
| `DH-PHILOSOPHY-INSIGHTS.md` / `PHILOSOPHY-CHANGELOG.md` | 思想結晶・変遷 |
| `PHILOSOPHY-NOTE-autonomy-with-guardrails-2026-05-11.md` | 直近設計根拠（WARM 寄り） |
| `../harness-verifier/PHILOSOPHY.md` | 6 条憲法（D4 正本） |

## WARM（append-only 監査台帳・既定は「直近 N 件＋要約」のみ・全文は retrieve 時）

| ファイル | 既定ロード方針 |
|---|---|
| `COUNCIL-LOG.md` | 直近数件＋要約のみ。全文は retrieve 時 |
| `CHANGELOG.md` | 直近 10 件＋要約のみ |
| `REGIME-LOG.md` | 直近 5 件＋要約のみ |

## COLD（情報代謝の排泄層・既定ロード対象外・retrievable）

> **除外の実現は convention レベル**: COLD を default-load から外す効果は、ハードな glob 規則ではなく
> 「本 SUMMARY を入口にし、COLD（`archive/`）を列挙しない」規律で実現される（代謝モデルは規律ベース）。
> ロード主体（振り返り儀式 F1 等）が本 SUMMARY を入口として尊重することが前提。glob 強制ではない。

### 移送済み

- **(a) 高確度（−2,584 行・移送済み 2026-06-07）**: `SELF-VERIFICATION-v5.*`（8件）/ `VERIFICATION*.md`（2件）/ `HANDOFF-v5.*`（3件）/ `L1-DELIVERY-v5.3.0.md` → **`archive/2026-06/`**。
- **(b)+(c) 第二弾（−5,260 行・移送済み 2026-06-07・Council mtb2sc・開発者ゲート適用）**: (b)中確度6件（`D4-AUDIT` / `SKILL-CREATOR-AUDIT`×2 / `ECC-SURVEY` / `self-gate-check-AD010` / `L0-WF-DESIGN`）+ (c)結晶化確認済み（`wave1/` `wave4/` `wave5/` `deliveries/` `council-readable/`）→ **`archive/2026-06/`**。逆引きは `archive/2026-06/MANIFEST.md`。
- **`wave2/` `wave3/`（−1,072 行・移送済み 2026-06-07・Council mtb2fu）**: 第二弾で hold 後、w2qb04/w3qb04 が「諮問省略＋結論 ship 済み（harness-verify.yml / templates/rituals/）」＝栄養抽出完了と再検証され hold 解除 → **`archive/2026-06/`**。

### 未移送・据え置き（理由つき）

- **`refs-draft/ecc/`（発酵層）**: 4件は skills から参照（live）、`instincts-design` のみ未結晶。COLD でも HOT 常駐でもない「発酵層」として次サイクル再問予約。
- **`project-derived-councils/`（管轄外・恒久除外）**: 利用者プロジェクト(D3)由来 Council ミラー＝還元先 project。DH-self(D4) 代謝の排泄対象ではない（他層の食料）。

> 注: `wave2/` `wave3/` は mtb2fu で移送済み（上記「移送済み」節）。w2qb04/w3qb04 の正体は「諮問省略＋結論 ship 済み」＝栄養抽出完了と判明し hold 解除。

## 要再確認リスト（摂取選択の可監査性 / metabolism-regime §3-3）

人間が「何を結晶化し何を COLD へ送るか」の摂取選択そのものを監査するためのリスト。**確度: AI 推定**。

- [ ] 結晶化候補（Council ゲート未達で保留）: 「harness-verifier 所有物編集は D5 ゲート（独立性要請）」/「PR merge 後はブランチを rebase してから継続コミット」 — `repetition_threshold` 到達まで保留
- [x] 本番 reindex 第一弾: (a) 高確度群を `archive/2026-06/` へ移送（2026-06-07・−15%）。詳細 `../delivery/REINDEX-PROD-2026-06-07.md`
- [x] 本番 reindex 第二弾: (b)+(c)結晶化確認済みを移送（2026-06-07・Council mtb2sc・−5,260行）。詳細 `../delivery/REINDEX-PROD-2026-06-07-wave2.md`
- [x] **w2qb04/w3qb04 再検証（mtb2fu）**: 正体は「諮問省略＋結論 ship 済み」と判明（沈黙した声ではない）。wave2/wave3 を移送済み。結晶化不要だった。
- [ ] **発酵層の再問**: `refs-draft/ecc/instincts-design` を次サイクルで「結晶化したか / 枯死か」再判定（緩慢な抹消を防ぐ再訪予約）

## 直近 cycle 振り返り（crosscut-cycle-retrospective・直近 3 件保持、超過分は `archive/` へ）

- 2026-09-06（cycle: v6.17.0 宣言層清算 PR-B + PR-D / M2 / L0 起点「DH スキルベースで更新したい・人間判断不要なものは ship まで自律駆動」）: PR #253 を出荷（#252 は #253 の squash merge に同梱され重複クローズ）— F2（GRAPH.yml 網羅性 + edge source 実質検査）と F6（RL 読込経路 + 現況 SSOT 一本化）。**うまくいった**: ①判断確定済み（D-2 / D-6）と Council 待ち（D-3/D-4/D-5）を着手前に仕分け、自律駆動の境界を人間に提示してから実装に入った = 「人間判断不要なものだけ」の指示を機械的に満たせた ②検査を足すたびに**合成ツリーで検出能力を実証**（欠陥を仕込めば検出・健全なら 0 件）してから ship = 「実リポで PASS」だけでは空振りを示せないという PR-A の規律を継承 ③新規検査 2 本とも初版が偽陽性を出したが、I-4「常時発火する検知を作らない」に照らして精度調整してから ship（検査 9 は層 prefix 略記と self-loop、検査 10 は箇条書き見出し位置に限定）④独立検証が「検査を意図的に壊してテストが落ちるか」「実リポに欠陥を注入して検出するか」まで踏み込み、空振り検査でないことを外部から追認した。**反省**: ①**PR-B と PR-D を積み重ねブランチにしたまま両方 PR 化した** → #253 の squash merge が PR-B のコミットを同梱し、#252 が「マージすると PR-D を巻き戻す」状態になって重複クローズになった。依存 PR を出すなら後続は先行のマージを待つか、最初から 1 PR に束ねるべきだった ②spec の実測値を 2 箇所で訂正することになった（F6 の README 列挙は 3 本でなく 4 本 / 欠落は 3 本でなく 2 本）= 起草時の実測が甘く、実装時に再実測して初めて判明 ③Copilot レビューで「説明が実装とずれている」（件数一致 vs ファイル名突合）を指摘された = **本 PR の主題である「宣言と実体の乖離」を自分の説明文で再演していた** ④返信に誤った commit SHA を書いて訂正コメントを足した。**体制**: M2 妥当（独立検証で仕様逸脱 0 件・修正ループはレビュー是正 1 往復のみ）。Council 発動 0 回は妥当（D-2 / D-6 は確定済み・D-2 逸脱分は申し送りで明示）。**環境**: GitHub MCP の PAT 失効（`AUTH_HEADER_REJECTED`）で MCP 経由の GitHub 操作が全滅、`gh` CLI（別 OAuth トークン）にフォールバックして完遂。PAT 再発行は spec §実装しないもので人間専管。**P3** = D-3/D-4/D-5 の Council 諮問（PR-C/F/G の前提）/ D-7 再判断（check 名で gemini-review と claude-review を区別できない構造的欠陥の解消が先）/ edge 削除で起動元を失った `council-performance` / `harness-benchmark` 2 node の `graph_excluded` 移動可否 / GitHub MCP の PAT 再発行。
- 2026-08-05（cycle: モデル選定 2026-08 世代更新〜時限化機構設計材料 / M2 / L0 メタハーネス対話起点）: PR #176-#179 を出荷 — 選定基準の世代更新（Opus 5/Sonnet 5/GPT-5.6/Gemini 3.6）+ サブスク運用基準、leaf worker 機械配線（Haiku 固定 frontmatter）、Council 諮問 f5fc45 → G-MODEL 標準行 + G-AGENT 時限付き凍結、ライフサイクル別「減らす・時限化」設計材料。verify --strict 全 PASS。**うまくいった**: ①一次情報優先（ローカル正本 → 4 並列 web 調査）で二次ソースの価格乖離まで検出できた ②「判断材料 → 人間承認 → 実装」の 2 段分離が全 PR で機能（決定はすべて人間・実装は即日）③Council が表面合意（2 対 1）を jc 0.45 で降ろして人間へ献上し、第 3 の道が recommended の形に統合された = 機構が設計どおり機能した実例。**反省**: ①ローカル verify の exit code をパイプ越しに誤読し PASS と誤認 → CI で FAIL 発覚（検証 exit は直接取得すべき）②DH 展開形態（DH+ハーネスがプロジェクトルートに統合）の前提を誤答し人間指摘 2 回で訂正 = 展開トポロジの正本確認不足 ③#178 の PR タイトルと実 diff の不一致（記録のみの PR に実装を示唆する題）。**体制**: M2 妥当（修正ループ小・未解決なし）。Council 発動 1 回は妥当（人間明示 + 発動者の自己申告 confidence 0.55 — judgment_confidence 0.45 とは別指標）。**改善提案（人間承認待ち・下記）**。P3 = 時限化機構 D1-D5 の決定 / gemini 3.6 Flash の実 invoke 確認 / council-weights ΣW=11 是正（F1 棚卸し・既存）/ meta_diagnosis フィールドの正式スキーマ化検討。

## 関連

- Dry-run レポート: `../delivery/REINDEX-DRYRUN-2026-06-06.md`（最新）/ `2026-05-31.md`
- 正本定義: `../.claude/skills/layer0-reindex-librarian/references/metabolism-regime.md`
