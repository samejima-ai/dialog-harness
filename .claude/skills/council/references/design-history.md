# Design History — 設計経緯の要約

Council System の設計に至るブレスト経緯と、確定事項・未確定事項を要約する。
オリジナルのブリーフ（`Council system dev brief .md`）は dialog-harness 本体に内包しない方針（ブリーフ §17）。
本ファイルは設計判断の根拠を将来の改修時に参照するためのアーカイブ。

## ブレスト概要

**実施**: 2026-04（ひで × Claude）
**目的**: 「判断時にのみ発動する合議制判定機構」を Dialog Harness の sub-skill として設計する
**背景**: 既存 MAGI 系実装（深津貴之 2022-12 / ROROSUKE / matsu_vr / Microsoft Zenn）との差別化を意識しつつ、AI自律駆動開発における判断モジュールとして再設計

## 確定事項（実装に反映済み）

### 位置づけ

- Dialog Harness の sub-skill として配置（将来切り出し可能な構造）
- L0 / L1 / L2 から横断的に呼び出される
- skill 名は `council`（ブリーフでは `interlude-council` 仮置き、実装時に短縮）

### 設計哲学（7 公理）

1〜6 は `council-philosophy.md` の §1〜§6 に格納。第 7 公理は v4.2 で追加された
harness 全体（philosophy.md 第 6 条）と Council を結ぶ補助公理として、
本ファイル内に記載する（`council-philosophy.md` への波及は v4.3 で再判断）。

1. Council 内部は非フラクタル（起点・分岐点のため）
2. 対立は構造化する（解消ではない）
3. 認識合わせと合意の分離（Council 出力は判断であって決定ではない）
4. 不完全性の受容（完璧は目指すが到達不能）
5. 実装者への信頼（縛りすぎない）
6. 人間との距離感（現段階は判断支援、理想は介入ゼロ）
7. **人間 ≒ Council 原則**: Council は人間の判断代替機構である（v4.2 で正式化）。
   判断種別を H カテゴリ（人間専管）と C カテゴリ（Council 代替可）に二分し、
   CTL に応じて自律実行範囲を動的決定する。詳細は philosophy.md 第 6 条 /
   `ctl-calculation.md` を参照。

### Council 種別

| 種別 | 構成 | 用途 | 主目的 |
|------|------|------|--------|
| 事業 Council | 経営者 / 開発者 / 哲学者 | AI 自律駆動開発、事業判断、実装判断 | 本人を超えた判断の生成 |
| 人生 Council | 男 / 父 / 開発者 | 人生のトレードオフ、健康判断、家族時間 | 本人らしい判断の再現 |
| ハイブリッド | 事業 + 人生並列 | 例外処理、常用しない | 「ちょっとした遊び」 |

### アーキテクチャ

| sub-agent | 役割 | 実装 |
|-----------|------|------|
| Pre-Check | Council 種別判定 | 決定論 |
| Orchestrator | 情報を運ぶ・重み計算 | 決定論（フラット） |
| Persona × 3 | 各視点で独立に意見生成 | LLM |
| Judgment Agent | 重み付きで単一回答を導出 | LLM（低 temp、人格なし） |

### Persona 設計

- 視点の独立性を優先（モデルの独立性は求めない）
- Temperature 配分: 経営者 0.3 / 開発者 0.2 / 哲学者 0.7
- Few-shot で人格具体化
- 出力開示ルール: 解釈 B（中庸版）—— Phase 1 では他 Persona 出力を見ない、Phase 2 では stance と質問のみ見る

### 対立類型

A（結論対立）/ B（理由対立、対立扱いせず）/ C（確信度対立）/ D（次元ずれ）/ E（前提対立 → 差し戻し + 人間献上）/ F（時間軸）/ G（メタ対立 → 人間エスカレーション）

詳細は [conflict-typology.md](conflict-typology.md)。

### 重み付け設計

2 層構造：

- **土台重み（base_weights）**: L0 対話で更新、開発者の思想・熱量を反映
- **状況補正（situational_modifier）**: カテゴリ別、時刻・締切・プロジェクト種別で動的に変化

計算式：

```
final_weight[persona] = base_weight[persona] × ethos_multiplier
                      + situational_modifier[persona]
```

### Judgment Agent

- 人格づけしない、temperature 0.1
- `final_decision` は常に `null`（実装者の合意プロセスが埋める）
- `judgment_confidence < 0.5` で自動人間エスカレーション

### 発動基準

- 自動発動: SPEC 矛盾検出時 / 複数案拮抗 / 不可逆操作直前 / 実装者 confidence 低
- 裁量で進める: タイポ / フォーマット / 単一パス / 明確仕様 / 定型リファクタ
- 確認を挟む: 設計の曖昧さ / 性能トレードオフ

### 重要な設計判断

1. Council System は Dialog Harness の sub-skill として開発（将来切り出し可能）
2. Orchestrator はフラット（判断機能を持たない）
3. Judgment Agent は別 sub-agent（哲学者を止揚係から解放）
4. 対立は解消せず構造化（少数意見を必ず保持）
5. `final_decision` は Council / Judgment Agent が埋めるフィールドではなく、Council 出力では常に `null`（v4.1 と同じ不変条件を維持）。CTL は「制度上の最終決定権者」を定義する仕組みであって、フィールドの記入主体を変えるものではない。H カテゴリは常に人間が決定権者となり、C カテゴリは CTL が CTL-1 以上のとき Council が `recommended` / `judgment` / `consensus_mode=auto_agree` を提示できるが、`final_decision` 自体の確定・記入は後段の実装者の合意プロセス（または事後評価）が担う（v4.2 で正式化）
6. 独立性は視点レベルで十分（モデルの独立性は求めない）
7. ハイブリッドは例外処理（常用しない）
8. Council System 自体は非フラクタル（起点・分岐点のため）
9. トリガー構造にフラクタル性がある（A⇄B 擦り合せループ）
10. Persona 間出力開示は解釈 B（stance と質問のみ）
11. Judgment Agent の出力は判断であって決定ではない
12. 実装者の裁量を尊重する
13. 認識合わせと合意は異なる概念

## PR 分割の判断

ブリーフは Phase 1（最小動作）/ 2（対立処理）/ 3（完全版）の段階実装を提案。
実装時に **Walking Skeleton** アプローチを採用：

- **PR 1（本 PR）**: business Council 1 系統を end-to-end で動かす最小形 + L1 step 4 統合 1 点
- **PR 2**: 対立類型 A/C/E/G + Phase 2 反駁
- **PR 3**: life Council + hybrid + 類型 D/F + Phase 2 質問形式 + F1-F3 儀式連携

理由: 半端に配線された skill より、1本だけ完全配線して契約検証する方が学習が早い。

## 既存 MAGI 実装との差別化

| 観点 | 既存 MAGI | Council System |
|------|-----------|---------------|
| 発動契機 | ユーザー質問 | 実装中の判断要請 |
| ペルソナ | 固定・汎用 | 文脈別 2 種（事業 / 人生） |
| 重み | 固定・平等 | 2 層動的（土台 + 状況補正） |
| 用途 | 一問一答 | 判断モジュール |
| 決着 | 多数決 | 重み付き判定 + 少数意見保持 |
| 位置 | 独立ツール | Dialog Harness の sub-skill |
| 出力の性質 | 最終回答 | 実装者が合意するための判断 |

命名は「MAGI」を避ける（→ `council`）。

## PR1 で先送りした項目

ブリーフ §13 未確定事項のうち、PR1 では以下を先送り：

- Phase 2 討論の具体的 prompt プロトコル（PR2 で `discussion-formats.md` 新設）
- 振り返り儀式（F1-F3）での Council 専用レビュー項目（PR3 で ritual-protocol.md 改修）
- COUNCIL-LOG の自動監査指標出力（PR3）
- Persona の Few-shot 例の実 COUNCIL-LOG からの抽出（実運用 10 件以上の蓄積後）

## PR1 検証時のメタ反復（Council を Council に諮る）

PR1 実装後の Walking Skeleton 検証（Test A/B）で、subagent が 3 件の不備を指摘：

1. `pre-check.md` / `orchestrator.md` に category 選択基準（`implementation` vs `conception` 等）の振り分けロジックが書かれていない
2. `invocation_id` の採番主体が SKILL.md / output-format.md で暗黙（「Pre-Check が採番」とのみ記述、採番形式と生成ロジックが未指定）
3. 「第3の道」stance（`options` 外の自由記述、哲学者が出しやすい）が返った時、`conflict_type` を `unanimous` / `simple_conflict` のどちらに分類するか規定なし

この修正範囲を Council 自身に諮るメタ反復を実施（invocation_id: `council-2026-04-21T15:30:00Z-m4t4q1`）。
全会一致で **案1（1, 2 は PR1 内で最小追記、3 は conflict-typology.md に PR2 予告メモ）** を推奨（judgment_confidence 0.85）。
実装者も合意し、本ファイル含む 4 ファイルに最小追記を実行してマージ。

哲学者 minority_opinion: 「Council を Council に諮る」というメタ反復自体が本 System の自己言及性を示している。PR1 の Walking Skeleton が自己自身を評価対象にできることの実証例として記録する。

## 参照

- 設計時の構成資料: ブリーフ（dialog-harness 本体外、ひで保管）
- 実装後の参照: 本ファイル + `council-philosophy.md` + 各 references/*.md

---

## v4.2 改訂履歴（2026-04-25）

### 6 公理から 7 公理への拡張

「設計哲学（6 公理）」を 7 公理に拡張。第 7 公理として「人間 ≒ Council 原則」を
追加（本ファイル冒頭の確定事項を参照）。

`council-philosophy.md` 本体の改訂は v4.2 では行わない（既存 §1〜§7 を維持）。
philosophy.md 第 6 条が新規原典の役割を担い、v4.2 では design-history.md のみで
公理拡張を反映する。`council-philosophy.md` への波及は v4.3 で再判断する。

### 確定事項の追加

- CTL（Council Trust Level）の 4 段階（CTL-0〜CTL-3）を `ctl-calculation.md` に
  規定。L0 spec-architect が REGIME.md 生成時に算出して記録する
- 横断蓄積メカニズム（`~/.claude/council-data/`）を user-scope に新設。
  プロジェクト横断で学習資産が引き継がれる
- 事後評価フェーズの厳格な分離: AI 駆動開発終了後にのみ発動し、人間の能動的な
  意思表示を経て初めて評価が始まる（philosophy.md 第 6 条参照）
- 評価方式: harness が HANDOFF.md で人間に問いかけ、議題・判定結果・実装結果の
  3 点に限定して確認する
- H カテゴリ抵触時は即時献上（権限境界として処理）。H1 哲学変更 / H2 ルール変更 /
  H3 方向性発案 / H4 根本設計見直し は CTL に関わらず常に escalate_to_human

### compute_consensus_mode の拡張

`consensus-protocol.md` の `compute_consensus_mode` を CTL 連動版に拡張。
シグネチャに `ctl` と `stats` を追加し、H カテゴリ即時献上ルールと
CTL ごとの閾値調整ロジックを導入。

### 重要な設計判断（5 番）の修正

「重要な設計判断」リスト 5 番を以下に書き換え:

- 旧: `final_decision は常に人間（現段階は判断支援）`
- 新: `final_decision フィールドは Council 出力では常に null（v4.1 不変条件を維持）。CTL は「制度上の最終決定権者」を定義し、H カテゴリは人間、C カテゴリは CTL ≥ CTL-1 で Council 自律実行（recommended / consensus_mode を提示）。フィールドの記入は後段の合意プロセスが担う`

この再整理により、`output-format.md` §4 の「`final_decision` は常に null」「Judgment Agent
が埋めることは哲学違反」（`council-philosophy.md` §3）と矛盾せず、CTL は判断委譲の
**決定論フィルタ**として位置づけ直された。

### v4.2 で先送りした項目（v4.3 候補）

- philosophy 第 7 条（データ存在意義の二分原則 / データ生命性原則）
- COUNCIL-LOG.md / CHANGELOG / ARCH-DECISIONS / DELIVERY.md の処遇確定
- AI 用データ配置の二分規格
- CTL 境界値の自己進化メカニズム（メタ Council 化）
- H4 の濃淡整理（ARC 切替のみ Council 助言、他は決定論）
- プロジェクト特性軸（S/U/R/N）でのカテゴリ別精度分割
- `council-philosophy.md` への 7 公理目反映（design-history.md と同期）
