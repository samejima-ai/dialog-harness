# Council 諮問: `council-2026-05-16T06:00:00Z-coddag`

CoDD (Coherence-Driven Development) の **DAG (有向非巡回グラフ) 概念** を Dialog Harness (DH) が今後咀嚼すべきか、するならどの位置づけで吸収するかを諮問した council 記録。

- **YAML 正本**: `history/COUNCIL-LOG.md` 内 `- invocation_id: "council-2026-05-16T06:00:00Z-coddag"` エントリ
- **発動契機**: ローカルブレスト議案 `BRAINSTORMCoDDDAGvsDH.md` を Issue #98 として起票後、人間が「Council による判定意見を生成して、今後の DH に咀嚼するべきか問う」と発話
- **source_skill**: `human_direct_invocation` (L0 仕様トレードオフ枠、philosophy 第 1 条 フラクタル原則 / 第 2 条 Shift Left との整合検証)
- **先例**: `council-2026-05-13T03:55:00Z-clrdbl` (conception category の precedent、本規約 §人間可読並存規約 の確立 council)

---

## 議題

CoDD の DAG (依存関係の構造保持 + 変更伝播追跡) 概念を DH に吸収すべきか。吸収するなら 5 本柱との関係をどう位置づけるか。

### 発動契機

ブレスト議案で以下が明らかになった:

1. **CoDD と DH の思想的共鳴**: 人間の役割を「目的・判断」に閉じる点で同型。CoDD = Wave 順 (依存順序) / DH = L0→L1→L2 フラクタル。整合性担保が CoDD = DAG / DH = P1 擦り合せ。
2. **CoDD の構造的不在**: D4 (マスター Skill = 方法論の自己適用) / D5 (人間 = 判断主体設計) が CoDD には不在。献上哲学・Council が無い。
3. **既存 DH 原則での吸収可能性検証**:
   - P2 シフトレフトでは吸収不可 — 問いの次元が違う (「いつ」 vs 「何が」)
   - P1 フラクタルでは部分的吸収のみ — P1 は「擦り合せが起きること」を語るが「依存連鎖を知る仕組み」を定義していない
4. **非対称性の発見**: DH の PreToolUse Hard Gate (守備) のみで、整合性検証 (攻撃) が未設計。これは意図的か空白か。

### 選択肢

| 案 | 内容 | コスト | optionality |
|---|---|---|---|
| **A** | 新規原則 (P6 相当) として独立追加 | 重 (philosophy 本体 + 全 downstream sync) | 高 |
| **B** | P1 フラクタル原則の派生概念として吸収 (「追跡可能性 = 形状保存メカニズム」として明文化) | 中 (philosophy 第 1 条への小拡張 + references 層配置) | 中 |
| **C** | 実装詳細として棄却 (メソドロジーの原則レベルには不要) | 軽 (現状維持) | 低 (検出 gap を放置) |
| **第 4 の道** | 哲学を変えずに業界 Layer 3 観測リストに加える (CoDD を参照事例化) | 軽 (DOMAINS.md or philosophy.md 末尾に観測節新設) | 中 |

---

## 発言 (3 persona、独立判定)

### 経営者 (ROI / 機会損失、conf 0.65)

> A (新規 P6) は philosophy 本体改修 + D3 sync 経由で cookpato / kakuman 等全 downstream に伝播するため、変更コスト・コミュニケーションコストが重い。経営判断として 6-12 ヶ月スパンの即時 ROI は読みづらい。
>
> 一方 C (棄却) は CoDD という業界 Layer 3 シグナルを取りこぼし、DH のポジショニング不利化リスク。CoDD が業界収束した場合の事後追従コストは A の事前投資より高くなりうる。
>
> **B は references 層配置で済むため即時 ROI 中立、optionality 保全。** 投資判断として B が経営合理的。
>
> **stance**: 案 B
> **dimension**: ROI / 機会損失
> **concerns**:
> - B 採用後の references 文書化コスト未定
> - CoDD が業界収束した時の遅延感が出るリスク
> - downstream への D3 sync で規約変更コミュニケーション必要

### 開発者 (保守性 / Shift Left、conf 0.78)

> ブレストの「P2 シフトレフトでは DAG を吸収できない、問いの次元が違う」は技術的に正確。P2 = 検証タイミング (when)、DAG = 依存トポロジー (what) で次元が直交する。
>
> P1 フラクタル原則は「形状の保存と擦り合せ」を語るが、「依存トポロジーの可視化機構」までは定義していない。これは P1 の **補集合的派生** として位置づけるのが論理整合的。
>
> A (新規 P6) はメソドロジーの単一責任原則違反 — philosophy 5 本柱の直交性を崩す。C (棄却) はブレストで検出された gap を放置することになり philosophy 第 2 条 Shift Left 違反 (検出された問いの先延ばし)。
>
> 実装機構 (DAG 本体) は autonomous-dev / independent-reviewer / harness-verifier の references 層に配置可能 — Shift Left 基盤 (30%) の延長として整合する。問い 3 の「攻撃設計 (DAG verify) 不在」は ARCH-DECISIONS 案件として独立扱いが正。
>
> **stance**: 案 B
> **dimension**: 保守性 / Shift Left
> **concerns**:
> - DAG 機構の具体実装は別途設計必要 (本 council のスコープ外)
> - harness-verifier との scope 切り分け要再確認 (BOUNDARY.md §3)
> - Hard Gate (守備) と DAG verify (攻撃) の対称化は ARCH-DECISIONS 案件 (AD-022 候補)

### 哲学者 (philosophy 第 1 条フラクタル / 第 2 条 Shift Left / 長期意味、conf 0.75)

> ブレストの「Hard Gate (守備) vs DAG verify (攻撃) の非対称性」は philosophy の盲点を突いている。これは P1 フラクタル原則の「形状の擦り合せループ」の **前提条件** — 「形状の依存関係が見える状態」を暗黙にしてきた構造的欠落。
>
> A (新規 P6 独立化) は哲学の数を増やし本質を見えにくくする — **philosophy 内のフラクタル違反** (同型問題のメタ層反復、clrdbl 諮問と同型 trap)。B (P1 派生) で「追跡可能性 = 形状保存メカニズム」として **止揚 (アウフヘーベン)** するのが正。
>
> ただし第 4 の道 minority として: CoDD を業界 Layer 3 観測リストに加える (philosophy.md §背景観測 / DOMAINS.md / または独立な OBSERVED-PEERS.md) — 哲学を変えずに観測経路を増やす。「業界のコンセンサスを観測し、DH の理論枠組みが内包しているかを反復検証する」哲学的反復 (philosophy 第 1 条フラクタルの自己適用)。
>
> 問い 2 (献上フローへの DAG verify 統合) は P3 情報純度原則の前処理として整合 — 整合性の取れていない情報はそもそも献上できないという制約は philosophy 第 5 条 献上哲学のサブ条件として自然。
>
> CoDD の D4/D5 不在は CoDD の **正当な選択** (D1-D3 特化機構として最適化) であり、否定的に扱わないこと。
>
> **stance**: 案 B + minority 第 4 の道 (観測リスト追加)
> **dimension**: philosophy 第 1 条フラクタル / 第 2 条 Shift Left / 長期意味
> **concerns**:
> - 派生概念の明文化を後回しにすると同型問題の再発 (philosophy 内フラクタル違反)
> - 観測リスト未整備のまま業界収束が進むと事後追従コスト増
> - CoDD への評価が方法論競合に流れないこと (CoDD は Layer 3 の D1-D3 配備事例、DH は方法論層)

---

## 結果

### 重み計算 (category: `conception`)

- **base_weights** (business): 経営者 3 / 開発者 4 / 哲学者 3 (sum 10)
- **situational_modifier** (`conception`、clrdbl precedent): 経営者 0 / 開発者 -1 / 哲学者 +2
- **final_weights**: **経営者 3 / 開発者 3 / 哲学者 5** (sum 11)

| stance | supporters | weight_sum | weighted_score |
|---|---|---|---|
| 案 A: 新規 P6 として追加 | (なし) | 0 | 0 |
| 案 B: P1 派生として吸収 | 経営者 (3×0.65) + 開発者 (3×0.78) + 哲学者 (5×0.75) | 11 | 1.95 + 2.34 + 3.75 = **8.04** |
| 案 C: 実装詳細として棄却 | (なし) | 0 | 0 |

- **conflict_type**: **unanimous** (3 persona が独立に B に収斂)
- **多様性 (プルラリティ) 評価**: 3 つの異なる評価軸 (ROI / 保守性 / 哲学) が同じ結論に到達 → 判断の **robustness** を示す
- **max_score_stance**: 案 B (8.04)
- **judgment_confidence**: **0.74** (中-高、unanimous で安定、ただし哲学者 minority 第 4 の道が併合候補)
- **third_way_excluded**: `[]` (第 4 の道は併合可能な minority opinion として `recommended` / `minority_opinion` に転載済。哲学者は scores 側に一意に出現させ、`output-format.md` §weight_calculation の 1 persona 1 位置の不変条件を保つ)

### Recommended

**案 B (P1 フラクタル原則の派生概念として「追跡可能性 (traceability)」を明文化) + 哲学者 第 4 の道 minority 併合 (CoDD を業界観測リストに追加)**

具体的アクション (本 council 採決後、実装者が合意プロセスで方針化):

1. **philosophy.md 第 1 条 フラクタル原則** に派生節を追加 — 「形状の保存」前提として「依存トポロジーの追跡可能性」を明文化。新規 P6 化はしない (5 本柱の直交性を保つ)
2. **実装機構 (DAG 本体)** は autonomous-dev / independent-reviewer / harness-verifier の **references 層**に配置候補。具体設計は本 council スコープ外 (別 ADR 案件)
3. **問い 3 の「攻撃設計」不在** は ARCH-DECISIONS の独立案件として記録 (AD-022 候補: 「Hard Gate (守備) と整合性検証 (攻撃) の対称化検討」)
4. **問い 2 の献上フロー統合** は philosophy 第 5 条 献上哲学のサブ条件として位置づけ可能 — Type A/B/C 献上の前提条件に「DAG 整合性 = 情報純度の前処理」を加える方向で検討
5. **第 4 の道 minority 採用**: DOMAINS.md または philosophy.md 末尾に「業界 Layer 3 観測リスト」セクションを新設、CoDD を最初の項目として記録 (経営者 concerns の「業界収束時の遅延感」を mitigate)

### Minority opinion

- **哲学者 第 4 の道**: 哲学を変えずに業界 Layer 3 観測経路を増やす方策 — recommended に併合済
- **経営者 concerns**: B 採用後の references 文書化コストが未定 → 次の振り返り儀式 F1-F3 で運用観察責任として保持
- **開発者 concerns**: DAG 機構の具体実装 / Hard Gate との非対称化 は本 council スコープ外、ARCH-DECISIONS 案件として独立扱い

### consensus_mode

**`auto_agree`** (`judgment_confidence` 0.74 > 0.5、人間直接諮問起点)

### human_escalated

`false` (但し合意プロセスで実装者が判断保留する権利は保持)

---

## 選択 (人間判断、確定済)

**`agreed_recommended`** — 案 B + 第 4 の道 minority をそのまま採用。咀嚼吸収プラン (`/root/.claude/plans/council-playful-steele.md`) を緻密化し、本 PR (#99) 内で 3-commit cycle として実行する。

### 採決の補足: AD 番号訂正

Council recommended 内で「AD-022 候補」と記述したのは、実装時に最新 AD 番号を確認した結果、AD-022 は既存 (v5.5.3 autonomous-drive 出口側 label opt-in 自動 merge) と判明した。実番号は **AD-032** (最新 AD-031 の次) に訂正する。

### 採決の補足: 観測リスト配置

Council 内では「DOMAINS.md または philosophy.md 末尾」の or 表現にしていたが、人間判断 (Q2) で `.claude/skills/layer0-spec-architect/references/observed-peers.md` (L0 references 層、D3 sync 対象外、upstream DH 専有) に確定。

### 採決の補足: 派生節埋込み形式

Council `coddag` recommended は「P1 派生として明文化」までを定義し、philosophy.md 第 1 条への具体的な埋込み形式は本採決の sub-scope。人間判断 (Q1)「咀嚼のための Council 起動」に従い、新規 sub-Council `p1embed` を本 PR 内 commit B で発動・採決して埋込み形式を確定する (案 α: 新規小節として独立追加 / 案 β: 既存「分岐の決定責務」を拡張 / 案 γ: 別ファイル切出し)。

### `implementer_consent`

`agreed_recommended`

### `agreed_at`

2026-05-16T07:00:00Z

### `cascade_to`

本 PR (#99 / `claude/council-judgment-generation-My87x`) で 3-commit cycle として咀嚼吸収完遂:

1. **commit A**: 本 closure (本 markdown 確定 + COUNCIL-LOG.md coddag entry の `implementer_consent` / `agreed_at` / `cascade_to` 更新)
2. **commit B**: sub-Council `p1embed` 発動・採決 (philosophy 第 1 条派生節の埋込み形式判定)
3. **commit C**: philosophy.md 第 1 条派生節追加 + `references/observed-peers.md` 新設 (CoDD 初回登録) + `ARCH-DECISIONS.md` AD-032 候補追加

問い 2 (献上フロー第 5 条への DAG verify 統合) は本 PR スコープ外、将来別 PR で扱う。

---

## 参照

- YAML 正本: `history/COUNCIL-LOG.md` 内 `council-2026-05-16T06:00:00Z-coddag` エントリ
- Issue: [samejima-ai/dialog-harness#98](https://github.com/samejima-ai/dialog-harness/issues/98)
- 起点ブレスト: `BRAINSTORMCoDDDAGvsDH.md` (ローカル、Issue #98 本文に embed)
- 先例 council: `council-2026-05-13T03:55:00Z-clrdbl` (conception category 重み precedent、人間可読並存規約の確立)
- philosophy 整合: 第 1 条 フラクタル原則 (派生先) / 第 2 条 Shift Left (検出 gap の先延ばし禁止) / 第 3 条 情報純度 (献上前処理候補) / 第 5 条 献上哲学 (DAG verify の位置づけ)
- ARCH-DECISIONS 候補: **AD-032** (Hard Gate 守備 ⇄ 整合性検証 攻撃 の対称化検討、本 council スコープ外、AD-022 は既存ゆえ番号訂正)
