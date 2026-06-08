# 業界 Layer 3 観測リスト (Observed Peers)

DH と同一階層（Harness Engineering = Layer 3）で参考になる業界先行事例の観測ログ。

## 観測の目的

- 業界の Layer 3 議論動向を観測し、DH の理論枠組みが内包しているかを反復検証する（[philosophy.md](./philosophy.md) 第 1 条 フラクタル原則の自己適用）
- DH の未定義領域に触れる概念を発見した時点で、本リストに記録 → 必要なら spec-architect 経由で philosophy / references / ARCH-DECISIONS に反映
- 競合事例ではなく**参照事例**として扱う（各事例には独自の設計選択があり、否定的に扱わない）

## 業界階層論の前提

CoDD コミュニティ（おしお氏）の整理に依拠する：

```
Layer 1: Prompt Engineering（戦術）
Layer 2: Context Engineering（戦略）
Layer 3: Harness Engineering（基盤） = 理論的最終形
```

DH は Layer 3 の内部設計を哲学・原則レベルから定義しており、Layer 3 の本格的な方法論層として位置づけられる。本観測リストは「同じ Layer 3 で異なる D 範囲を扱う事例」を中心に記録する。

## 観測項目

### CoDD (Coherence-Driven Development)

- **観測登録**: 2026-05-16（Council `coddag` 採決による初回登録）
- **URL**: https://github.com/yohey-w/codd-dev/blob/main/README_ja.md
- **マイルストーン記事**: https://zenn.dev/shio_shoppaize/articles/codd-v2-17-milestone
- **業界階層論記事（おしお氏）**: https://zenn.dev/k_k_p/articles/harness-architecture
- **位置づけ**: Layer 3（Harness Engineering）の D1〜D3 特化実装（ソースコード 〜 配布 Skill レベル）
- **核心機構**: DAG（有向非巡回グラフ）による設計書 ↔ コード ↔ テストの整合性追跡
- **コア思想**: 「設計書 ↔ コード ↔ テスト」がいつも同じ事実を語っている状態を、AI が自律的に維持する（Coherence-Driven = 整合性駆動）

#### DH との共鳴点

- 人間の役割を「目的・判断」に閉じる思想（CoDD: 要件定義と感想のみ / DH: P1-P4 責務）
- AI が整合性を自律維持する設計
- ガードレールを hook で実装（CoDD: PostToolUse の codd scan / DH: PreToolUse Hard Gate）

#### DH との差異点

- **次元範囲**: CoDD は D1〜D3 特化、DH は D1〜D5（D4 マスター Skill = 方法論の自己適用、D5 人間 = 判断主体設計まで扱う）
- **判断機構の有無**: CoDD には献上哲学・Council 機構が存在しない（人間は「起点」としてのみ存在）
- **検証方向**: CoDD の DAG verify は「攻撃」設計（積極的に整合性を検証）、DH の Hard Gate は「守備」設計（やってはいけないことを止める）— 守備・攻撃の対称性は本記事公開時点で DH 側未整備

#### DH への影響

- **吸収済**: Council `coddag`（2026-05-16）で「依存トポロジーの追跡可能性」を philosophy.md 第 1 条 派生節として吸収（[philosophy.md](./philosophy.md) §依存トポロジーの追跡可能性 を参照）
- **温存項目**: 守備（Hard Gate）⇄ 攻撃（DAG verify）の対称化検討は **AD-032 候補** として [ARCH-DECISIONS.md](../../../../history/ARCH-DECISIONS.md) に記録
- **将来検討**: 献上フロー（philosophy 第 5 条）への DAG verify 統合は本 council スコープ外、別 PR で扱う

## 観測の更新プロトコル

- 新規事例の追加は spec-architect 対話または直接 council 諮問経由で行う
- 既存事例の更新（URL 変更、位置づけ再評価等）は人間明示トリガーで実施
- 本リストは upstream DH 専有（D3 sync 対象外）、downstream プロジェクト（cookpato / kakuman 等）には伝播しない
- 観測対象の選定基準: Layer 3 の方法論層 / 哲学層を扱い、DH と異なる設計選択を持つ事例を優先

## 関連

- 親 Council: [history/COUNCIL-LOG.md](../../../../history/COUNCIL-LOG.md) 内 `council-2026-05-16T06:00:00Z-coddag` エントリ
- 人間可読版: [history/archive/2026-06/council-readable/council-2026-05-16T060000Z-coddag.md](../../../../history/archive/2026-06/council-readable/council-2026-05-16T060000Z-coddag.md)（情報代謝で COLD 移送済み）
- philosophy 接続: [philosophy.md](./philosophy.md) 第 1 条 §依存トポロジーの追跡可能性 から本リストへ参照
- ARCH-DECISIONS 連動: [history/ARCH-DECISIONS.md](../../../../history/ARCH-DECISIONS.md) AD-032 候補（Hard Gate ⇄ DAG verify 対称化検討）
