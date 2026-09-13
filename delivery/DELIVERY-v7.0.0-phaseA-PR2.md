# DELIVERY.md — upgrade-spec v7.0.0 Phase A / PR-2（F6 叡智層の失効セマンティクス）

## ステータス: 完了（PR-2 の範囲）/ Phase A 残り = PR-3（F3 圧縮 + 再測定・基準値計測後）

## 体制情報

- Mode: M2 / LC=1 / Cycle: v7.0.0 Phase A（PR-2）
- 自律修正回数: 0 / 上限 3（verifier FAIL なし）
- Council: 新規発動なし。`council-2026-09-13T01:40:00Z-v7phsa`（案C）が「PR-2 = F6」の着地単位を含み、F6 の内容は spec（PR #287・人間 merge）で承認済み。escalation-matrix「規範文書改変の実装前 → Council 諮問」はこの諮問で通過したものとして扱う（PR-1 と同じ扱い。別途諮問が要るなら人間判定）
- 着地条件: PR #288（PR-1）merge 後に `origin/master` から分岐。`git log origin/master..HEAD` = 0 件（先行 PR のコミットを含まない — Council 案C の運用規則を機械確認）
- AI 能力バージョン: Claude 5 系（`history/.model-generation.yml` 変更なし）

## 実装済み機能

| 項 | 内容 | 受け入れ基準（spec §F6） | 結果 |
|---|---|---|---|
| (a) 規格 | `dev-env-spec.md` §規範メタデータ に `status: active（既定）/ frozen / revoked`、`revoked_at`、`superseded_by`（後継なしは `none` を明示）の 3 行を表に追加。新設 §失効 で宣言・効力・列挙・適用対象・宣言主体を規定 | メタデータ規格に 3 フィールド | PASS |
| (b) 列挙 | `scripts/norm-scan.py` に `find_revoked_files` / `extract_revoked` / `scan_revoked` を追加。`scan()` 結果に `revoked` キー、`render()` に「失効済みで購読に残っている規範」節と「宣言不完全」フラグ。**判定はしない** | norm-scan が列挙する | PASS（実リポ 0 件。fixtures で列挙を実証） |
| (c) 儀式 | `ritual-protocol.md` F2.6 に 3.5「失効済み規範 N 件が購読に残っています。COLD へ？（一括移送 / 個別に確認 / 後で）」。宣言不完全は補完を先に問う | F2.6 に問いがある | PASS |
| (d) COLD | `metabolism-regime.md` §2 昇降格表に「HOT/WARM → COLD（失効）: 次サイクルの排泄で移送・結晶化完了の確認は失効宣言が代替」、§4 排出に例外 1 項 | reindex-librarian の COLD 移送条件 | PASS |
| (e) 適用対象 | §失効 に「罠エントリ / RL frontmatter（`> ROLE:` 群に 1 行）/ `DH-PHILOSOPHY-INSIGHTS.md` の各節」を明記。INTENT 廃止マーカーは機能の記録として残す（二重管理にしない） | INTENT.md 以外へ拡張 | PASS（規格として。実適用例は 0 — 下記） |
| (f) 時限 | §失効 と norm-scan docstring に `review_trigger: [model_generation, cycles: 6]` | 規範メタデータ | PASS |
| 付随 | `deprecation-protocol.md` 手順 3 に「廃止に伴い失効する規範は `status` を `revoked` に」/ `history-layer-spec.md` §archive に「失効規範は 2 年を待たず次サイクル」/ `ritual-protocol.md` F2.6-2 の `model_generation` 説明を F7 後の実装（yml 併用）に合わせて訂正 | — | — |
| 訂正 | spec 状態行: PR-1 が F8 / F9 を「未」と書いていたが両方着地済み → 「済」に | — | — |

## 通過ゲート記録

| ゲート | 結果 |
|---|---|
| escalation-matrix「規範文書改変の実装前 → Council 諮問」 | 通過（v7phsa 案C・上記体制情報。**人間確認事項 #1**） |
| 献上時の人間判定 | `human-review-needed`（references 5 本横断 = opt-in「3 ファイル以上」） |
| L-FROZEN 不可侵（I-1） | philosophy.md / delegation-boundary.md / auto-merge-boundary.md の diff **0 バイト** |
| Council 案C 運用規則 | `git log origin/master..HEAD` に PR-1 コミット 0 件 |

## 自己検証結果

### 計算的センサー

| 検査 | 結果 |
|---|---|
| `python3 harness-verifier/verify.py --strict` | **総合 PASS**（11 項目全 PASS・FAIL 0） |
| `scripts/test-*.py` 14 本 + `test-*.sh` 4 本 | **全 PASS**（norm-scan に F6 12 項目を新設: インライン / 引用ブロック / 宣言不完全 / active・frozen 非誤認 / 除外規則 / 実リポ / render） |
| `python3 scripts/norm-scan.py` | 走査 23 / 時限トリガ 39（発火 2 / 未発火 12 / 機械判定しない 25）/ **失効済み 0 件**（宣言不完全 0）。総数 34（HEAD）→ 39 = +5: dev-env-spec §失効 の `model_generation` + `cycles: 6`（2）/ norm-scan.py docstring の同 2 項（2）/ test-norm-scan.py の fixture 文字列 `review_trigger: [model_generation]`（1） |
| `git grep -E "status:[[:space:]]*revoked"` | 実リポに literal 出現 0（列挙 0 件が空振りでない根拠。走査器・テスト・規格文書は `status` と `revoked` を隣接させない書き方で自己誤列挙を避けた） |

### 推論的センサー

- 仕様に合う: spec §F6 の (a)〜(f) を逐項充足。走査範囲は spec の「HOT/WARM」を「`history/archive/`（COLD）だけ除外」と読んだ（`review_trigger` の走査は `history/` 全体を除外するが、失効の適用対象 `DH-PHILOSOPHY-INSIGHTS.md` が `history/` にあるため除外集合を分けた。spec §F6 実装注記 (1)）。
- 動く: fixtures で列挙・不完全検出・除外を実証。
- 使える: 経路は 宣言（人間）→ 列挙（機械）→ 問い（儀式）→ 移送（reindex 次サイクル）。**実行主体が居るか**（PR-1 の示唆）: 宣言主体 = 人間の一言承認 / 列挙主体 = norm-scan（F2.6-1 で既に走る）/ 問い主体 = F2.6-3.5 / 移送主体 = reindex-librarian 排泄。移送は reindex の Dry-run 規則に従う（初回は提示のみ）。

### 独立検証（M2 必須）

`delivery/VERIFICATION-v7.0.0-phaseA-PR2.md`（layer1-independent-reviewer・新規文脈・F4 読み順制約）。

## 仕様改訂提案（タイプC）

1. **走査範囲の非対称**: `review_trigger` は `history/` を全除外、失効列挙は `history/archive/` のみ除外。理由は上記だが、二つの除外集合を持つことは読者に重い。次に `review_trigger` 側の除外を見直す機会（叡智層の節に `review_trigger` を付ける運用が始まったとき）に統一を検討。
2. **`superseded_by: none` の明示**: spec は `<path#anchor>` のみだったが「書き忘れ」と「後継なし」を区別するため `none` を許した。

## 未解決事項

- **第一適用例なし**: 実リポで失効させた規範は 0 件。何を失効させるかは採用判断（第 8 条・不変核 2）ゆえ人間。候補があれば F2.6-3 の「廃止」選択時に `status` を `revoked` にすれば経路が回る。
- **移送の実行**: reindex-librarian は Dry-run 既定（初回・規定サイクルは提示のみ）。失効 → COLD の初回移送は Dry-run レポートに載るところまで。本移送は人間承認後。
- `model_generation` 発火数の変化 3（PR-1 時点）→ 1（#288 merge 後の HEAD）→ 2（本 PR）: merge で `layer1-independent-reviewer/SKILL.md` と `test-norm-scan.py` の最終 commit（09-13 10:03 UTC）が世代 epoch（`.model-generation.yml` の 09-13 00:00 UTC）より新しくなり発火が消えた（設計どおり）。本 PR の +1 は dev-env-spec §失効 の宣言で、同ファイルの最終 commit（09-06）が世代 epoch より古いため即発火する。commit されれば消える。世代 epoch の粒度が「日」であることの帰結で、儀式 F2.6 の判断には影響しない。

## 体制事後評価

- M2 妥当。verifier FAIL 0・独立検証 1 回。Council 発動なしは妥当（着地単位は諮問済み・内容は人間承認済み spec の実装）。
- 次回への示唆: 規格文書に「書式の例」を書くと走査器が例を実物と誤認する。走査対象語を隣接させない書き方（`status` と `revoked` を分ける）で回避したが、走査器側に「規格文書の例外」を持たせない方針は維持（allowlist を作らない = v6.17.0 I-1）。

## 履歴層更新差分

| レベル | 対象 | 内容 |
|---|---|---|
| A（自動） | `history/CHANGELOG.md` | v7.0.0 Phase A PR-2 節を追加。PR-1 節の見出しを「merge 済み」に |
| B（確認推奨） | `history/INTENT.md` | v7.0.0 節に「失効は購読からの離脱で効く」を追記。見出しを PR-2 に |
| B（確認推奨） | `history/REGIME-LOG.md` | PR-2 の体制記録（Council なし・着地条件の機械確認） |
| C（必須承認） | — | INTENT の廃止・訂正なし |
