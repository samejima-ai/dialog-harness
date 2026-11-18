# GATE-METRICS — 2026-11-06 roll-back 評価ゲート（2026-10-25 時点・closed PR 150 件（#89〜#292））

`auto-merge-boundary.md §roll-back プロトコル` の 4 指標。LLM 判定を含まない。
走査: closed PR 150 件（うち merged 148 件）。

## 4 指標

| 指標 | 実測 | 閾値 | 検知 |
|---|---|---|---|
| 暗黙 merge 事故件数 | 0 件（記録）/ 要突合 16 件 | 1 件以上で要再評価 | 人間（機械は候補提示のみ） |
| AI 判定漏れ率 | 1.4%（2/148） | 5% 超で要再評価 | メタ承認機構 |
| 境界曖昧化事例 | 0 件（記録） | 月 2 件以上で要再評価 | 人間 |
| 二重ラベル腐敗 | 0 件 | 1 件でも即 roll-back | 機械 |

## 閾値超過

- なし（記録ベース）

> **記録ベースの限界**: 「暗黙 merge 事故 0 件」は *そう記録されていない* という意味で
> あり、*起きていない* という意味ではない。既知の反例として PR #196 がある — 
> REGIME-LOG 記録 #1 は Actions ログを一次証拠に「stop ラベル付与後も auto-merge が
> squash merge した」と記す。これは実体として暗黙 merge 事故だが、記録上の区分は
> 「AI 判定漏れ」であり、暗黙 merge 事故としては数えられていない。
> **ゲート判断の前に、この 1 件を暗黙 merge 事故として数えるかを人間が決める必要がある**
> （数えるなら閾値「1 件以上」に該当する）。

## AI 判定漏れの内訳

- 記録番号: #1, #2
- 対象 PR: #196, #280

## 暗黙 merge — 人間が突合すべき候補一覧

stop ラベルが付いたまま merge された PR。**事故件数ではない。**

- **偽陽性**: 人間が確認して自ら merge した場合も同じ形になる
- **偽陰性**: ラベル未付与のまま merge された型（記録 #2 の PR #280）は現れない
- **実行者で切り分けられない**: `auto-merge.yml` は `secrets.GH_REVIEW_PAT`
  （人間アカウントの PAT）で merge するため、auto-merge も人間 merge も
  `mergedBy` が同一に見える。記録 #1 の PR #196 が実例

下記は Actions ログと 1 件ずつ突合するための候補である。

- #289 feat(v7.0.0 Phase A / PR-2): 叡智層の失効セマンティクス — 規範単位の status/revoked_at/superseded_by・norm-scan 失効列挙・儀式 F2.6-3.5・失効→次サイクル COLD
- #288 feat(v7.0.0 Phase A / PR-1): 認知足場を剥がす前に環境足場を締める — 不変核の再注入・休眠 skill 退避・決定論優越・世代検知修正・SKILL.md 分割
- #278 fix(l0): Supabase 既定性の降格 — v6.19.0 F1（既定が到達不能な供給元を指していた）
- #270 feat(verifier): 検査が守っているものを消しても緑だった — 走査面の欠落を塞ぐ（v6.18.0 C-4）
- #248 feat(version,signal,ci): 版番号に契機を与え、走らなくなったものを検知する — v6.17.0 PR-A + PR-E + D-7
- #208 chore(ctl): .council-ctl.json 初回投入（L-GATE・人間マージ専用）
- #199 chore(privacy): 公開リポジトリ全体の個人名を一括匿名化（25 ファイル・90 箇所）
- #198 spec(l0): upgrade-spec v6.14.0 起草 — 開発日誌エージェント（観察の層を判定の層から切り離す）
- #196 ci(harness-verify): scripts/** を検査対象に含め、test-* を CI で実行する
- #193 spec(l0): upgrade-spec v6.13.0 起草 — 宣言と配線のあいだを閉じる（役割境界の機械化）
- #166 feat(layer0): runtime_profile 軸新設 + GAS を 11 番目の正規 stack として追加（v6.3.0）
- #161 feat(ctl): CTL 記録経路を再設計し分断を解消（v6.1.0）
- #147 feat(philosophy)!: 権限委譲境界の確立（可逆性ベース・第9条新設）（v6.0.0）
- #131 feat(auto-merge): 全CI完了待ち化 + self-update protocol強化 (v5.22.0)
- #129 fix(auto-merge): verifier の pending を待機する race ガード追加 (Issue #125)
- #116 tune claude-review ARC + codify review-loop termination boundary

候補 16 件。突合の結果 事故と判明したものを REGIME-LOG へ
`## auto-merge メタ承認機構 — 暗黙 merge 事故記録 #N` として append する。

## 要人間ラベル付与

次の 2 指標は §評価指標 が検知主体を人間（事後監視）と定める。
本レポートの数値は REGIME-LOG への append 記録の計数であり、
**未記録の事象は 0 件として現れる**。ゲート判断の前に人間の棚卸しが要る。

- 暗黙 merge 事故件数 — 事後発覚した『気づいたら merge』の有無
- 境界曖昧化事例 — philosophy 周辺の判定揺らぎの有無

## 判断

本レポートは 11-06 ゲートの**判断材料**であり、判断そのものではない
（第 8 条: 採否の判断を AI に持たせない）。起票可否は人間が決める。
