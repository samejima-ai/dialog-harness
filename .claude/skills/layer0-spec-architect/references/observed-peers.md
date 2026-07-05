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

### claude-world-examples（Director Mode コミュニティ）

- **観測登録**: 2026-06-18（Council `council-2026-06-18T11:50:01Z-cw0rld` 採決による初回登録、全会一致 案A）
- **URL**: https://github.com/claude-world/claude-world-examples
- **コミュニティ**: claude-world.com（台湾の Claude Code コミュニティ、@lukashanren1）、MIT License
- **位置づけ**: 厳密には Layer 1〜2 寄り（Prompt / Context Engineering）の **啓蒙・テンプレ層**。Layer 3（Harness Engineering）の方法論層ではない。DH とは扱う層が異なる
- **核心機構**: Director Mode（人間=ディレクター、AI=自律チーム）思想 + 概念解説文書群 + framework 別 CLAUDE.md テンプレ 9 stack + GitHub Actions 集
- **コア思想**: 「Goals over Instructions（目的を定義し手順は委ねる）」「Team Delegation（並列エージェントへの委譲）」「Outcome Verification（結果を検証）」の Three Pillars

#### 当初発話と調査結論の乖離（後世への申し送り）

本観測の起点となった人間発話は **「アンソロピック公式 Claude テンプレートを DH メタスキルにも採用したい」** だった。しかし調査の結果、本リポジトリは **Anthropic 公式ではなく非公式コミュニティ事例** と判明した（「official」は Claude Code というツールが公式、の意）。「公式テンプレ採用」という前提で無条件取り込みに進むと judgment が歪むため、本節に乖離を明記する。後世が再び「公式テンプレ」として本事例を掘り起こさないこと。

#### DH との共鳴点

- 人間の役割を「目的・判断」に閉じる思想（claude-world: Director Mode / DH: philosophy 第 7 条 P1〜P4 責務）
- 並列エージェント活用（claude-world: Parallel Agents / DH: Council 3 ペルソナ + L2 orchestrator）
- 仕様駆動（claude-world: Spec-Driven Development / DH: L0 サブフェーズ L0-2〜L0-6）
- セッション間知識保持（claude-world: Memory System / DH: history 層 + 振り返り儀式）

#### DH との差異点

- **層の違い**: claude-world は思想を **散文の啓蒙** として提供。DH は同じ思想を **実行されるプロトコル**（対話駆動仕様抽出 / モード判定 / 重み付き Council 判定 / 振り返り儀式）として実装済み。DH の方が思想的に先行している領域が多い
- **判断機構の有無**: claude-world に Council・献上哲学・重み付き判定は存在しない
- **増分価値**: DH に対する明確な増分は **framework 別 scaffold の幅** の 1 点（DH の scaffold-checklist は v6.1.0 まで Vite+React+PWA の 1 stack のみで薄かった）

#### DH への影響

- **吸収済**: Council `cw0rld`（2026-06-18）で全会一致 案A（最小介入）。framework 別 CLAUDE.md テンプレ → `scaffold-checklist.md` の 9 stack カタログ化として **DH 形式に再構成して吸収**（原典の散文を丸ごと転記したものではない）。出典・MIT・観測経路を当該ファイルに明記
- **却下項目**: 概念文書の philosophy/references への取り込み（案B）は、思想の二重定義による drift リスクで三ペルソナとも却下。GitHub Actions/workflow 集の取り込みは DH の `templates/github-workflows` / `personas` / `rules` と機能重複のため除外
- **温存項目（未問の前提）**: 哲学者ペルソナが留保した「framework の幅の多様性を DH が本当に価値とするか」は未問の前提として記録。9 stack の各 smoke 維持責務（陳腐化追従）は scaffold-checklist のカタログ規約で「決定論的記述に限定・流行 lib は例示のみ」として最小化済み
- **副次採用候補**: CLAUDE.md アンチパターン診断の L0 §7.4 自己検証への補強（本 Council スコープ内、別途実装）

### Loop エンジニアリング / Harness エンジニアリング（henteko 氏）

- **観測登録**: 2026-06-28（Council `council-2026-06-28T11:54:06Z-de8276` 採決による初回登録、全会一致 案A）
- **URL**: https://zenn.dev/henteko/articles/f65485dac55599
- **著者**: henteko 氏（Zenn 記事、個人）
- **位置づけ**: Layer 3（Harness Engineering）の**役割論**を散文で提唱する事例。DH と同じ Layer 3 概念層に最も近接する（CoDD は D1〜D3 実装、claude-world は Layer 1〜2 啓蒙であるのに対し、本記事は Layer 3 の役割分担そのものを論じる）
- **核心機構**: AI 開発を 2 職種に分離する。(1) **Loop エンジニアリング** = 人（ドメインスペシャリスト/当事者）が Why/What を与えてゴール設定し、AI が自律で開発サイクルを高速に回し、成果物が課題を解決できているかを人がジャッジする。(2) **Harness エンジニアリング** = 新職種「Harness エンジニア」が、AI が暴走せず安全かつ超高速に loop を回すための環境（安全な検証環境・厳密な自動テスト）を構築し継続運用する
- **コア思想**: Loop と Harness は単独では不十分で、両者の協調で初めて安全かつ高速な成果が成立する。「既存技術の延長線」（Redash でのデータ整備等）と自己規定し、全く新しい概念ではないとする

#### 用語の注意（開発者ペルソナ付帯条件）

本記事の「**Harness エンジニアリング**」は **AI の実行環境を構築・運用する新職種**を指す。DH の「Harness（Layer 3 = Harness Engineering）」は**方法論層全体**を指す。同じ語だが指示対象が異なる（原典＝環境構築職 / DH＝方法論全体）。本エントリを参照する際はこの定義ズレを前提とし、安易に同一視しないこと。

#### DH との共鳴点

- 人間の役割を「Why/What 提供 + ジャッジ」に閉じる思想（henteko: Loop エンジニアリング / DH: philosophy 第 7 条 P1〜P4 責務 + 献上哲学）
- 「AI が暴走せず安全に」高速 loop を回す環境の必要性（henteko: Harness エンジニアリング / DH: PreToolUse Hard Gate / harness-verifier / sensors）
- 厳密な自動テスト・安全な検証環境（henteko: Harness の責務 / DH: L1 独立検証 → L2 統合検証 → drift verifier の検証スタック）
- 役割分担を「既存技術の延長線」とする視点（henteko: Redash 等 / DH: philosophy 第 1 条 フラクタル原則の既存役割の再帰適用）

#### DH との差異点

- **実装度**: henteko は役割分担を**散文の提唱**として提示。DH は同じ思想を**実行されるプロトコル**（モード判定 / Council 重み付き判定 / 振り返り儀式 / dev_mode 連動）として実装済み
- **判断機構の有無**: 本記事に Council（合議判定）・献上哲学・重み付き判定にあたる**判断機構の内部設計は存在しない**
- **Loop の主体**: 本記事は Loop も Harness も「人がやる職種」として描く。DH は **Loop（開発サイクル）を AI が回し、人間は判断主体に閉じる**設計で、人間の置き場所がさらに上流に寄っている

#### DH への影響

- **吸収済**: Council `de8276`（2026-06-28）で全会一致 案A（最小介入＝観測ログ追記のみ）。philosophy/references への概念取り込み（案B）は claude-world（cw0rld）前例と同型の「思想の二重定義 drift リスク」で見送り。とりわけ本記事は概念層が最も近接する分、無批判な取り込みの drift 危険が高いと 3 ペルソナが独立に判断したため、観測層に留める
- **温存項目（未問の前提・哲学者ペルソナ）**: 「**Loop を誰が回すか＝人間の当事者性をどこに宿すか**」を未問の問いとして温存する。本記事は Loop を人の職種とし、DH は Loop を AI に委ね人間を判断主体に閉じる。この差が単なる設計選択なのか、当事者性をどこに宿すかという倫理的賭けなのかは、職種分化の語彙が固着して前提が不可視化される前に問い直す対象として記録する
- **温存項目（断絶性の自己評価）**: 本記事の「既存技術の延長線」という自己規定を DH が無批判に受け入れると、Layer 3 の断絶性・新規性を自ら過小評価しかねない点を留保する

### Ponytail（DietrichGebert 氏 / 最小主義スキル）

- **観測登録**: 2026-07-05（Council `council-2026-07-05T10:37:44Z-pony01` 採決による初回登録、recommended B）
- **URL**: https://github.com/DietrichGebert/ponytail
- **ライセンス**: MIT License、v4.x（2026-06-12 作成、〜44k stars）
- **位置づけ**: 厳密には **Layer 1〜2**（Prompt / Context Engineering）の**実装ルール注入**事例。Layer 3（Harness Engineering）の方法論層ではない。CoDD（D1〜D3 実装）・claude-world（Layer 1〜2 啓蒙）・henteko（Layer 3 役割論）とも異なり、本事例は「AI エージェントの実装工芸に最小主義を注入する運用ルール」を扱う。DH とは層が異なるが、DH の philosophy が空白にしていた「実装時にコードを少なく書く」領域に触れる
- **核心機構**: セッション開始時に「最も怠惰なシニア開発者のように考える＝最良のコードは書かないコード」ルールセットを注入。7 段の決定ラダー（YAGNI → 既存再利用 → 標準ライブラリ → ネイティブ機能 → 既存依存 → ワンライナー → 最小限コード）+「要求されない抽象化の禁止」+「入力検証 / セキュリティ / アクセシビリティは決してバイパスしない品質ゲート」
- **コア思想**: 「The best code is the code you never wrote」。フィフティ行を見せられて何も言わず 1 行に置き換えるシニアの archetype。実測 ~54% 減コード / ~20% 安 / ~27% 速（Claude Code 実セッション計測）

#### DH との共鳴点

- 「書かないコード」＝最も可逆（消す対象すら存在しない）→ philosophy 第 9 条「委譲境界原則（可逆性ベース）」と深く共鳴
- YAGNI・過剰抽象の抑制 → 第 3 条 情報純度（依存トポロジー DAG の縮小）
- 品質ゲート非バイパス → 第 2 条 Shift Left / 5 層検出スタックと非衝突

#### DH との差異点

- **層の違い**: Ponytail は本質的に **プロンプト注入**（Layer 1〜2）。DH は Layer 3 の方法論層。原典散文の丸取りは category error（claude-world / henteko と同型の思想二重定義 drift リスク）
- **常時 active / Ultra**: 原典は毎レスポンス常時 active、Ultra モードで「**要件そのものに異議を唱える**」。後者は DH 第 4 条「開発中に質問しない」・第 7 条 P1「発案は人間専管」と衝突
- **尺度の違い**: 原典は「量（行数）」を規範化。DH は「可逆性」を尺度に綴じ直す

#### DH への影響

- **吸収済（DH 形式に再構成）**: Council `pony01`（2026-07-05）で recommended B（D2/D3 scaffold 組み込み）。哲学者の第 3 の道を織り込んだ止揚案 **B′** で確定。決定ラダーを `templates/rules/common/minimalism-ladder.rules.md` として **DH 形式に再構成**（原典散文は転記せず、可逆性尺度・REGIME 調律・批判精神の Council 再定置を追加）。出典・MIT・観測経路を当該ファイルに明記
- **却下項目**: philosophy への条追加（案 C = D4 昇格）は Council で否決（実装工芸であり統治原則ではない、不変資産への越境・保守硬直）。常時 active 注入・Ultra「要件異議」モード・原典散文の丸取りは棄却（当該 rule ファイル §棄却経路 に明記）
- **温存項目（哲学者 minority・重み 5）**: 「最良のコードは書かないコード」を全ドメインへ default 配布すると、探索・研究・prototype 領域の投機的コードという萌芽を刈り、多様な当事者性を均質化しうる。→ B′ で「固定命令でなく REGIME が締緩を調律できる条件付きルール」として解いた。ただし「量を可逆性の proxy と取り違え DH 本来の尺度を隠蔽しないか」は未問の前提として温存
- **将来検討**: L0 対話での「ドメイン特性 → ラダー強度」判定質問の `dialog-questions.md` 追加。Ponytail 原典のメジャー更新時に決定ラダーの差分を再観測

## 観測の更新プロトコル

- 新規事例の追加は spec-architect 対話または直接 council 諮問経由で行う
- 既存事例の更新（URL 変更、位置づけ再評価等）は人間明示トリガーで実施
- 本リストは upstream DH 専有（D3 sync 対象外）、downstream プロジェクト（cookpato / kakuman 等）には伝播しない
- 観測対象の選定基準: Layer 3 の方法論層 / 哲学層を扱い、DH と異なる設計選択を持つ事例を優先

## 関連

- 親 Council（CoDD）: [history/COUNCIL-LOG.md](../../../../history/COUNCIL-LOG.md) 内 `council-2026-05-16T06:00:00Z-coddag` エントリ
- 親 Council（claude-world）: [history/COUNCIL-LOG.md](../../../../history/COUNCIL-LOG.md) 内 `council-2026-06-18T11:50:01Z-cw0rld` エントリ
- 親 Council（Ponytail）: [history/COUNCIL-LOG.md](../../../../history/COUNCIL-LOG.md) 内 `council-2026-07-05T10:37:44Z-pony01` エントリ
- Ponytail 吸収先: [templates/rules/common/minimalism-ladder.rules.md](../../../../templates/rules/common/minimalism-ladder.rules.md)（決定ラダーの DH 形式再構成先）
- 人間可読版: [history/archive/2026-06/council-readable/council-2026-05-16T060000Z-coddag.md](../../../../history/archive/2026-06/council-readable/council-2026-05-16T060000Z-coddag.md)（情報代謝で COLD 移送済み）
- philosophy 接続: [philosophy.md](./philosophy.md) 第 1 条 §依存トポロジーの追跡可能性 から本リストへ参照
- scaffold 連動: [scaffold-checklist.md](./scaffold-checklist.md) §追加 stack カタログ（claude-world 観測の吸収先）
- ARCH-DECISIONS 連動: [history/ARCH-DECISIONS.md](../../../../history/ARCH-DECISIONS.md) AD-032 候補（Hard Gate ⇄ DAG verify 対称化検討）
