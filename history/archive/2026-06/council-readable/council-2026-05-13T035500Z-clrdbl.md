# Council 諮問: `council-2026-05-13T03:55:00Z-clrdbl`

Council 判定の最終出力 (`history/COUNCIL-LOG.md`) を **人間可読 form** で並存させるべきか、するならどう永続化するかを Council に諮問した **メタ council** 記録。本 council 自身が **本規約の確立 council** となる。

- **YAML 正本**: `history/COUNCIL-LOG.md` 内 `- invocation_id: "council-2026-05-13T03:55:00Z-clrdbl"` エントリ
- **配置根拠**: `crosscut-council/references/consensus-protocol.md` §人間可読並存規約 (本 council で確立した規約)
- **発行タイミング**: 本規約確立 PR (#96) 内で retroactive 作成 (規約 §適用範囲 の例外 1 件目 / 規約のメタ council 自身)
- **先例**: `council-2026-04-21T15:30:00Z-m4t4q1` (kakuman / DH 共通履歴) — Council を Council に諮るメタ反復の同型先例

---

## 議題

Council 判定の最終出力 (`history/COUNCIL-LOG.md`) は schema 準拠 **YAML (machine-readable)** で記録されているが、人間が離席復帰時に「あの判定どんな議論だっけ」と振り返るときの **判断スピード向上 = 人間可読 form の永続化** をどう扱うか?

### 発動契機

PR #96 進行中、人間が「Council の最終出力は人間可読に整備された?」と問うた。chat ログには 4 section markdown (議題 / 発言 / 結果 / 選択) があるが、commit されているのは YAML のみで、復帰時に振り返ると YAML を読み解く必要がある — gap が露呈。本 council 自身を **メタ council** として起動。

### 選択肢

| 案 | 内容 |
|---|---|
| **A** | 現状維持 (YAML のみ、復帰時は chat ログ参照) — 規約も file も追加なし |
| **B-1** | PR #96 に `history/council-readable/<id>.md` を **本件のみ** 追加、規約化はしない (漸進採用) |
| **B-2** | `crosscut-council/references/consensus-protocol.md` に **「人間可読並存規約」を追記** + 本件 markdown を併合 (規約化、cookpato / kakuman にも自動伝播) |
| **第 4 の道** | YAML エントリ内に narrative セクション (`human_readable_summary: |` 等) を追加するスキーマ拡張 — schema 変更を伴う重い変更 |

---

## 発言 (3 persona、独立判定)

### 経営者 (ROI / 機会損失 / 段階導入、conf 0.65)

> 復帰判断スピード向上は実利だが、規約化 (B-2) は cookpato / kakuman / 将来プロジェクト全てに即時影響し、規約変更コミットメントが重い。**本件のみ B-1 で 1 件試行 → 1〜2 cycle 観察 → 効果検証 → B-2 漸進採用** が経営合理的。即時 ROI が読めない規約化を本 PR で巻き込むのはスコープ膨らみリスク。
>
> **stance**: 案 B-1

### 開発者 (保守性 / Shift Left、conf 0.75)

> 各 Council ごとに「人間可読 markdown を書くか書かないか」判断が増えるとコスト膨らみ、結局書かれない council が混ざる (**情報純度のバラつき**)。**Shift Left = 規約に組み込んで自動適用** が正。markdown と YAML の二重化リスクは責務分離 (YAML = machine、markdown = human) で軽減可能。本 cycle で規約化しないと再発時のメタ判断コストが繰り返される (**現に今が 2 度目**: kakuman entry `m4t4q1` も同型メタ Council)。
>
> **stance**: 案 B-2

### 哲学者 (philosophy 第 4 条 UX 代理指標 / 第 1 条 フラクタル、conf 0.80)

> 復帰判断スピードは philosophy **第 4 条 UX 代理指標** (クリック数 / 遷移深度 / 完了率) の典型例で、これを skill SPEC レベルで担保するのは `consensus-protocol.md` の責務。本 cycle で B-2 を扱わないと **philosophy 第 1 条フラクタル原則違反** (同型問題のメタ層反復 — 既に 2 度目)。
>
> ただし minority として「**既存遡及はせず次回 council から適用**」とすることで経営者懸念 (即時 ROI 不在) を mitigate できる。
>
> **stance**: 案 B-2 + minority (B-1 漸進採用の pragmatic value)

---

## 結果

### 重み計算 (category: `conception`)

- **base_weights** (business): 経営者 3 / 開発者 4 / 哲学者 3 (sum 10)
- **situational_modifier** (`conception`、l0agg1 precedent): 経営者 0 / 開発者 -1 / 哲学者 +2
- **final_weights**: **経営者 3 / 開発者 3 / 哲学者 5** (sum 11)

| stance | supporters | weight_sum | weighted_score |
|---|---|---|---|
| 案 B-1: 本件のみ漸進採用 | 経営者 (3×0.65) | 3 | **1.95** |
| 案 B-2: 規約化 + 併合 | 開発者 (3×0.75) + 哲学者 (5×0.80) | 8 | 2.25 + 4.0 = **6.25** |

- **conflict_type**: **simple_conflict** (B-1 vs B-2)
- **max_score_stance**: 案 B-2 (6.25 > 1.95)
- **judgment_confidence**: **0.72** (中程度、minority opinion 強い)

### Recommended

**案 B-2 + 哲学者 minority pragmatic 採用**:

- `consensus-protocol.md` に「人間可読並存規約」追記 (規約化、4 section format / `history/council-readable/<id>.md` 配置 / 同 commit 規約)
- 本件 markdown 併合 (本 council 自身 + rtkSHA、retroactive 2 件は規約の例外として許容)
- **適用範囲**: 本規約確立 PR (#96) merge 後の次の council から適用、既存 council 群への遡及はしない

### Minority opinion

経営者: 「即時 ROI 不在」懸念。本 cycle で B-2 規約化と本件 markdown 併合を同時に行うことで「規約変更 + 実例 1 件」が同 PR に揃い、即時に効果検証可能になる → 経営者懸念は **新規規約の運用観察責任** として保持 (今後 1〜2 cycle の効果観察を振り返り儀式 F1-F3 で行う)。

### consensus_mode

**`auto_agree`** (`judgment_confidence` 0.72 > 0.5、人間直接諮問起点のため確定経路)

### human_escalated

`false`

---

## 選択 (人間判断、確定済)

**`agreed_recommended`** — 案 B-2 + 哲学者 minority pragmatic そのまま (consensus-protocol.md 規約追記 + 本件 markdown 併合、既存遡及せず次回 council から適用、PR #96 に追加)

### `cascade_to`

本 PR (`claude/fix-rtk-install-sha-TDmT8`) で:
1. `consensus-protocol.md` に「人間可読並存規約」セクション追加 (§人間可読並存規約)
2. `history/council-readable/council-2026-05-13T033500Z-rtkSHA.md` 作成 (retroactive 例外 2、rtkSHA の人間可読版。DH PR #105 で ISO 8601 basic format に rename)
3. `history/council-readable/council-2026-05-13T035500Z-clrdbl.md` 作成 (retroactive 例外 1、本 council のメタ自己記録。DH PR #105 で ISO 8601 basic format に rename)
4. `history/COUNCIL-LOG.md` に本 council YAML entry を append

kakuman 側は本 PR merge 後の D3 sync で `consensus-protocol.md` 規約を自動追従する。

### `agreed_at`

2026-05-13T04:30:00Z

---

## 参照

- YAML 正本: `history/COUNCIL-LOG.md` 内 `council-2026-05-13T03:55:00Z-clrdbl` エントリ
- PR: [samejima-ai/dialog-harness#96](https://github.com/samejima-ai/dialog-harness/pull/96)
- 確立された規約: `.claude/skills/crosscut-council/references/consensus-protocol.md` §人間可読並存規約
- 起点 council: `council-2026-05-13T03:35:00Z-rtkSHA` (人間が「人間可読に整備された?」と問うた具体例)
- philosophy 整合: 第 4 条 UX 代理指標 (復帰判断スピード) / 第 1 条 フラクタル原則 (同型メタ問題のレベル下げ)
