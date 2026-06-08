---
name: layer0-reindex-librarian
dimension: D4
description: >
  蓄積した history（episodic 層）を再蒸留して叡智層（罠/RL/SPEC/DOMAINS 等）へ結晶化し、
  栄養を抜いた抜け殻を COLD アーカイブへ排出する L0 兄弟スキル＝情報代謝サイクルの実行主体。
  「履歴が重い」「history を結晶化したい」「reindex して」「振り返りの読み込みが膨らんできた」
  「叡智を蒸留して抜け殻を archive に移したい」「AI の購読量を減らしたい」「代謝サイクルを回して」
  等の発話、または history 層が token 閾値を超過したリズムトリガーで起動を検討する。
  2 モードを持つ: Scaffold（対話起点で spec を新規設計＝spec-architect が担う既存機能の呼称）/
  Reindex（履歴起点で spec を再蒸留＝本スキルの新規分）。書き込みは L0/D4 成果物（SPEC/DOMAINS/DONT
  および DH 本体 framework 叡智）に限定し、L1/L2 成果物や生 history は書き換えない。
  最上位不変条件は「AI 購読量（既定ロード量）の上限維持」——repo/COLD のディスクサイズ増は許容するが、
  購読量と history 蓄積量の線形連動を断つことが目的。初回および規定サイクルは Dry-run（差分レポートのみ・
  実結晶化しない）で起動する。「実装して/ship」（→ autonomous-dev）「新規/継続の対話設計」（→ spec-architect）
  「コードの意図復元・リファクタ前段」（→ archeo-architect）「後付け harness 化」（→ onboarding）とは責務が異なる。
  自動で生 history を削除しない（COLD=archive≠delete）。人間明示トリガーまたはリズム超過でのみ起動。
---

# Reindex Librarian（情報代謝サイクルの実行主体）

蓄積した history を再蒸留して叡智を密に結晶化し、抜け殻を COLD へ排出する L0 兄弟スキル。
「episodic な生ログ → 結晶化された叡智」という構築代謝（anabolism）と、
「栄養を抜かれた抜け殻 → COLD アーカイブ」という分解代謝（catabolism）の両方を回し、
**情報代謝サイクルを完成させる**。DH 定義では情報代謝の停止＝組織の唯一の死であり、本スキルは最適化ではなく生存要件。

## 原則

- **結晶化＝何を正典叡智にするかの決定＝ L0 発案権の行使**。よって reindex はネイティブに L0（横断しない）
- **食べる（摂取）→ 咀嚼吸収（構築代謝）→ 排泄（分解代謝）の三拍子で初めて速くなる**。結晶化だけでは叡智が増えるが生ログも残り、むしろ重くなる
- **最上位不変条件は AI 購読量（既定ロード量）の上限**。結晶化は密度↑であって量↑ではない。詳細は §最上位不変条件
- **代謝自体が購読量を侵さない**。reindex は前回結晶化以降の増分（WARM delta）だけ読み、COLD を再 scan しない。sparse + 冪等
- **独自補完しない**（CLAUDE.md / philosophy 準拠）。reindex は「そこにある生ログの蒸留」であって、無い叡智の捏造ではない
- **lossy 圧縮を雑に回さない**。早すぎる結晶化＝偽 convention の固定化を防ぐため HOT 昇格は Council ゲートを必須にする（§ガバナンス）

## レイヤー帰属（決定1・確定）

レイヤー帰属は「権限・所有」で決まり「データの到達範囲」では決まらない。reindex は履歴を**広く読む**が、
**書く**のは L0/D4 成果物（spec-design ＝発案権の行使）＝ L0 専権。データは横断するが権限は動かない。
横断スキルにすると非 L0 が spec を書き換える穴が開きレイヤーモデルが崩れるため、本スキルは横断しない。

## 2 モード（同一 L0 行為・入力源が違うだけ）

| モード | 入力源 | 行為 | guard（起動条件） |
|---|---|---|---|
| **Scaffold** | 人間との対話 | spec を新規設計 | 新規/継続の対話設計要求 → 実体は `layer0-spec-architect` に委譲（本スキルは概念上の双対として参照のみ） |
| **Reindex** | 蓄積した history | spec を再蒸留 | history 層が token 閾値超過（リズム）/ 人間が「reindex」「結晶化」「代謝」を明示 |

**モード切替 guard（独自補完禁止と整合・Council 指摘 #3）**:

```
入力源を判定:
  人間との対話で「新規機能・継続開発・仕様策定」 → Scaffold（= spec-architect へ委譲、本スキルは起動しない）
  蓄積 history が token 閾値超過 OR 人間が "reindex/結晶化/代謝/抜け殻を archive" を明示 → Reindex モード起動
  どちらにも該当しない（曖昧） → 起動しない（spec-architect の対話で吸収させる）
```

guard が曖昧判定のまま Reindex を起動してはならない（暗黙判断の禁止）。詳細プロトコルは `references/reindex-protocol.md`。

## 二軸フラクタル（philosophy 第1条の深掘り）

情報代謝は 2 つの直交する軸でフラクタルに反復する。詳細は `references/metabolism-regime.md` §二軸。

- **還元先軸**: DH 本体 D4 叡智 ⇄ 固有プロジェクト D1-D3 叡智。流入 history は「何に還元されるか」で二分される。咀嚼吸収する対象は「いまどちらの開発をしているか」で切り替わる（DH メタ開発中は DH 還元型、固有プロジェクト開発中は project 還元型）
- **時間軸**: 短い操作ループ（clean-state-per-attempt）⇄ 長い履歴結晶化。同一の純度回復（期待⇔現実の擦り合わせ）を 2 つの時間スケールで反復

## 三拍子（摂取／咀嚼吸収／排泄）

| 拍子 | 対象 | 操作 | 行き先 |
|---|---|---|---|
| 食べる（摂取） | 流入した生 history（WARM delta のみ） | 作業集合に取り込む | — |
| 咀嚼吸収（構築代謝 / anabolism） | その層に**還元される**栄養 | 罠/RL/DOMAINS/invariants/SPEC へ密に結晶化（成功→RL・convention / 失敗→DONT 罠） | HOT 叡智層 |
| **排泄（分解代謝 / catabolism）** | 栄養を抜かれた**抜け殻**（結晶化完了後のみ） | 作業集合から外す（**delete せず** retrievable に保つ・逆引き source pointer 付き） | COLD アーカイブ |

**排泄の罠（必読）**: ①排泄 ≠ delete（COLD=archive≠delete）。②「自層が吸収しなかったデータ」は排泄物ではなく**他層の食料**。排泄判定は「結晶化が完了したか」で決まり「還元先が自層か」では決まらない。③順序は吸収→然る後に排泄（未消化を先に排泄すると栄養喪失）。

## 最上位不変条件: AI 購読量の上限（Council mtbl01 北極星）

- 最小化対象は **AI が毎サイクル既定でロードする購読量**。**非対象**は repo/COLD のディスクサイズ（無制限 OK）
- 目的は購読量と history 蓄積量の**線形連動を断つ**こと（episodic は COLD で太る、購読量はフラット/減少）
- 結晶化は密度↑であって量↑ではない。**HOT 自体が budget を超えたら再圧縮（罠の統合・陳腐 WARM の COLD 降格）が発火**
- 叡智も常時全ロードしない（progressive disclosure）。購読量は「HOT 総バイト数」でなく「そのタスクで実際に読む量」で測る
- 代謝処理自身も購読量を侵さない（増分のみ読む・全 rescan 禁止・冪等）

## 処理フロー（Reindex モード・Dry-run デフォルト）

```
0. リズム判定（token 閾値超過 or 明示トリガー。未超過なら起動しない）
1. 還元先軸の確定（DH メタ開発か / 固有プロジェクト開発か → 咀嚼吸収対象を決定）
2. 増分の特定（処理済みマーカー = cursor/checksum/timestamp の続きから WARM delta のみ。COLD は読まない）
3. 摂取選択（何を食べるか）— §摂取選択基準（references）に従い、結晶化候補を選別
4. 咀嚼吸収（構築代謝）— 反復パターンを叡智へ結晶化【提案】。HOT 昇格は Council ゲート
5. 排泄（分解代謝）— 結晶化完了済み抜け殻を COLD へ移送指示 + source pointer 付与
6. 出力 = Dry-run なら差分レポートのみ（実結晶化・実移送はしない）。本番なら結晶化提案 + 移送を実行
7. 処理済みマーカーを前進（冪等性の担保）
```

**Dry-run デフォルト（Council 指摘 #5）**: 初回および REGIME.md `metabolism.dry_run_cycles` で指定された初期サイクル数は Dry-run（差分レポートのみ）。誤結晶化→COLD 誤移送の P4 復元工数を未然に抑える。本番昇格は人間承認後。

## リズム（決定2・確定）

- **発火条件**: history 層が指定 token 量（購読量 budget）を超過した時点。N-cycle トリガーは棄却
- **タイミング哲学**: 開発中に回さない。cycle 境界（献上後・次 L0 前）で回す。**結晶化＝組織の睡眠フェーズ**（記憶の固定化）。検証後評価原則と完全整合
- 具体閾値は project 固有パラメータ（`## 情報代謝設定`）。**単一解決順**: REGIME.md `## 情報代謝設定` があればそれ（利用者プロジェクト）、無ければ DH-self 既定パス `history/.metabolism-config.yml`（DH 本体・root REGIME.md を持たない慣習を維持）。詳細は `references/reindex-protocol.md` §2.5

## ガバナンス（8 不変条件 + Council ゲート）

雑に回すと毒になる。以下を不変条件として守る（詳細・定量基準は `references/metabolism-regime.md` §5）。コア 5 を常時ロード側に置き、理論層由来 #6–#8 は展開せず参照に留める（progressive disclosure ＝購読量保護）。

1. **早すぎる結晶化を防ぐ**。HOT 昇格は Council 判定をゲートにする（自動カウンタで上げない）。定量基準は REGIME.md
2. **COLD ＝ archive ≠ delete**。retrievable に保つ
3. **叡智に source pointer**（逆引き）。疑義が出たら生ログまで遡れる。形式は `references/reindex-protocol.md`
4. **代謝自体のコストを抑える**（毎 cycle 全行にかけない・sparse・冪等）
5. **独自補完しない**（TBD を捏造で埋めない）

※ 理論層追加 #6（COLD lossless 原本から読む）/ #7（情報欠損なしは HOT の誤目標）/ #8（パターン結晶は反-発火条件必須・形式確定後発効）は `references/context-circulation-theory.md §8` および `references/metabolism-regime.md §5` を参照（常時ロードしない）。

## 参照ドキュメント

- `references/context-circulation-theory.md` — **理論層（仮結晶 / 暫定公理）**。なぜこの代謝なのかの全体理論（5 相循環 / 3 ループ / **圧縮 ≠ 結晶化** / **二種の結晶＝規則結晶・パターン結晶** / 8 不変条件 / 認知科学接地）。philosophy.md の系（昇格待ち）。on-demand。「圧縮率が低い」への答え＝速度は圧縮でなく結晶化（判断の先取り）から来る、はここ §5
- `references/metabolism-regime.md` — regime 定義の正本（二軸 / HOT・WARM・COLD tier / 還元先 routing / 昇降格条件 / 結晶化・排出プロトコル / 摂取選択基準 / 購読量 KPI / 8 不変条件 / Council ゲート定量基準 / **§7 E2E episodic ソースの tier 対応**）。決定3 の正本化先（定義＝SK references）。上記理論の実装拘束部分
  - E2E run 履歴は専用サイクルを作らず本 regime の新 episodic ソースとして流す（artifact→COLD 直行 / E2E-LOG→WARM / flaky 罠→HOT）。**project 還元（D1-D3）専用・DH 本体は非稼働**。構築側は `../layer1-autonomous-dev/references/e2e-best-practices.md` §9
- `references/reindex-protocol.md` — 運用プロトコル（モード guard / 処理済みマーカー形式 / 増分・全 rescan 禁止・冪等契約 / Dry-run / COLD 逆引きポインタ形式 / 初回 reindex 手順）
- 参照原典: `../layer0-spec-architect/references/philosophy.md`（第1条フラクタル / 第3条情報純度 / forgetting is a feature）、`../layer0-spec-architect/references/history-layer-spec.md`（history 層スキーマ・archive ＝ COLD の素地）、`../crosscut-council/SKILL.md`（HOT 昇格ゲート）

## L0 三兄弟＋本スキルの境界

spec-architect（未来→仕様・対話起点 Scaffold の実体）/ archeo-architect（過去→意図復元・リファクタ前段）/
onboarding（後付け harness 化・1 回限り）/ **reindex-librarian（蓄積 history→ 叡智再蒸留・代謝の実行主体）**。
本スキルは spec-architect と同時起動しない（対話方向の混線を避ける）。Reindex は履歴起点、Scaffold は対話起点。

## バージョン

- v0.1.0（新設・情報代謝サイクル walking skeleton） — Reindex モード / 二軸フラクタル / 三拍子 / 購読量上限不変条件 / Dry-run デフォルト / Council ゲート。初回 reindex は Dry-run。Council 批准: `history/COUNCIL-LOG.md` `council-2026-05-31T00:00:00Z-mtbl01`
