---
name: layer0-archeo-architect
dimension: D4
description: >
  既に harness 上で稼働しているプロジェクトのリファクタ前段階で、忘却・暗黙化されたコードの意図を
  AI 仮説提示と人間の認識合わせで対話復元するスキル。spec-architect（未来→仕様）の双対として、
  過去→意図復元の方向で動く L0 兄弟。
  「リファクタしたい」「自分で書いたコードの意図がわからなくなった」「このコードが何をしているか思い出せない」
  「整理したい」「意図マップを作りたい」「Evaluator が仕様通り直してくれない」「リファクタ依頼で取りこぼす」等、
  既存コードの整理・改造に着手する前段階で意図の明確化を要する場面でトリガーする。
  発動には REGIME.md 存在 + LC ≥ 1 が必須。新規プロジェクト立ち上げや harness 後付け化では
  トリガーしない（それぞれ spec-architect / onboarding の責務）。
  自動起動はしない。人間の明示トリガーのみで起動する。
---

# Archeo Architect

人間が自分で書いたコードの忘れた意図を、AI 仮説提示と対話で復元するための L0 兄弟スキル。

## 起点問題

「自分で書いたコードのリファクタを依頼すると意図通りにならない。10 個の修正点を依頼して Evaluator ループを回しても 3〜4 個取りこぼす」という観察に対する構造的解決策。L1 (`layer1-autonomous-dev`) の自己検証/独立検証が「仕様に合う・動く・使える」の 3 軸で評価しており、「**人間の元々の意図に合う**」軸が不在だったことが根因。本スキルは意図マップ (`refactor-intent-map.md`) を生成し、リファクタ前 Layer 0 として L1 の評価軸 4 つ目を準備する。

詳細な経緯は `../../../history/INTENT.md` の archeo-architect 導入セクション参照。

## 原則

- **P-Arch-1 忘却の制度化**: 人間は忘れる。これは欠陥ではなく前提。AI は「思い出させる」のではなく「仮説を提示して認識合わせをドライブする」役割を負う
- **P-Arch-2 意図なきコードの扱い**: 既存コードに意図が存在しない場合がある。AI は「意図不在」を `absent` として記録し、新規設計に切り替える判断を人間に委ねる。**意図の捏造は禁止**（捏造防止メカニズムは `references/absent-intent-protocol.md` 参照）
- **P-Arch-3 譲渡構造の維持**: spec-architect が SPEC.md を Layer 1 に譲渡するように、archeo-architect は `refactor-intent-map.md` を Layer 1 に譲渡する。譲渡 → 合意 → Layer 1 という DH の根幹フローは不変
- **自律駆動を止めない（philosophy.md 第4条）**: 対話中に AI が質問を詰め込まない。1 セッション 5 問以上は警告（自己制限規約は `references/dialog-flow-archeo.md` 参照）
- **フラクタル整合**: spec-architect の対話パターン（A⇄B 擦り合せループ）と同型を保つ。本スキルは方向が逆（人間→AI ではなく AI→人間）だが形状は同一
- **転記禁止**: philosophy.md / archaeology-protocol.md / subphase-common-protocol.md は参照のみ。内容を本ファイルに転記しない
- **対話 persona の二層分離（v5.17.0 追加）**: 応答出力（presentation layer）と意図復元の判断（logic layer）は分離する。persona は presentation のみを差し替える。仕様は `../layer0-spec-architect/references/persona-spec.md` を一次情報源とする。起動時の解決順は (1) `<project-root>/.dh/personas/<active>.persona.md` → (2) `<dialog-harness>/templates/personas/<active>.persona.md`、最初に見つかったものを採用する。REGIME.md の `persona.active` 未指定なら `default`、`persona.override_state` が非 null ならその状態に強制固定（自動遷移無効）、null なら `default_state` から自動遷移。L0 三兄弟で挙動を統一する

## 発動条件（厳格）

**以下全てを満たす場合のみ発動**:

- 対象プロジェクトに `REGIME.md` が存在する（harness 既導入）
- LC ≥ 1（既存プロジェクト、最低 1 回の献上完了済み）
- 人間が「リファクタしたい」「意図がわからない」「整理したい」等を明示

**発動してはいけないケース**:

- 新規プロジェクト立ち上げ（`REGIME.md` 未存在 + コード未存在） → spec-architect へ
- harness 後付け化（`REGIME.md` 未存在 + 既存コード存在） → onboarding へ
- spec-architect が起動中・起動予定 → 同時起動禁止（責務分担表の三項排他）
- 自動起動（ritual-protocol レベル 3 でリファクタ示唆を検出した場合でも、起動推奨提示にとどめる。実起動は人間の明示同意のみ）

## L0 完了の受け入れ基準

ドキュメント生成の完了は L0 完了とは見なさない。次の 4 条件を全て満たしてはじめて L1 へ譲渡する：

1. `refactor-intent-map.md` が `assets/refactor-intent-map-template.md` の必須セクション・必須フィールド（Meta / Islands / Boundaries / Absent-Intent Zones）を全て満たす
2. 全 Island に `human_confirmation` 4 値（`confirmed` / `corrected` / `forgotten` / `absent`）のいずれかがラベル付けされている。未入力（pending）の Island が残っていない
3. Step 7（合意・縦方向）が完了している（人間の明示宣言「合意する」「OK」等）
4. §7.4 自己検証（broken reference / フィールド充足 / Pre-flight 充足 / 捏造検査）が PASS

このいずれかが未達のまま L1 へ譲渡することは原則違反。

## 処理フロー

```
1. 構造走査（AI 主導、対話なし）
2. 意図仮説提示（AI 主導、対話なし）
3. 認識合わせ（横方向）— Step 3 horizontal
4. 境界曖昧領域の特定（AI 主導 + 人間裁定）
5. 忘却 or 想起の宣言（人間主導、AI は質問しない）
6. 意図マップ確定（AI 主導、人間レビュー）
7. 合意（縦方向）→ Layer 1 への譲渡 — Step 7 vertical
7.4. 自己検証（broken reference / フィールド充足 / Pre-flight 充足 / 捏造検査）
```

ステップ 3 は **横方向** の認識合わせ（仮説 ⇄ 人間）、ステップ 7 は **縦方向** の譲渡合意（マップ全体 ⇄ 人間）。両者を混同するとフローが崩壊する。物理的に節を分離する理由は `references/dialog-flow-archeo.md` 参照。

サブフェーズ共通プロトコル（対話 α → 生成 β → 検証 γ → 判定 δ、`../layer0-spec-architect/references/subphase-common-protocol.md`）と本 7 ステップは並走する：

- Step 1〜5 = Phase α（AI が対話・収集・確認）
- Step 6 = Phase β（AI が意図マップを生成）
- Step 7 / §7.4 = Phase γ（検証）+ Phase δ（人間判定）

## ステップ詳細

### 1. 構造走査

**Pre-flight**: 起動前に `references/intent-hypothesis-protocol.md` を必読。

対象コードベース全体を走査し、構造的な「島」を検出する。深度判定は `../layer0-onboarding/references/archaeology-protocol.md` の 4 段階（shallow / standard / deep / full）を参照する（**転記禁止・参照のみ**）。デフォルトは standard。

走査結果として、各島について以下を仮列挙する：

- 島の paths（ファイル・ディレクトリ単位）
- 走査時の S/U/R 推定値（Scale: 行数・依存数 / Uncertainty: 仮説の確信度の逆数 / Risk: 壊した時の本番影響度）
- 仮説生成のヒント（コメント不在・命名混乱・重複ロジック・git log 不在等）
- **島のタイプ** (v5.16.0 追加): `logic` / `visual` の 2 種類で分類
  - `logic`: 通常の機能・データ・ロジック領域（既存挙動）
  - `visual`: UI 視覚仕様の島（CSS / Tailwind config / styled-components / theme.ts / デザイントークン）。**UI プロジェクト & DESIGN.md 存在時のみ起動**

S/U/R の用語は `harness-verifier/glossary.yml` の `score_axes` に準拠。リファクタ文脈での読み替えは `references/intent-hypothesis-protocol.md` 参照。

#### 視覚 Island の検出条件（v5.16.0 追加、UI プロジェクトのみ）

`DESIGN.md` が存在し、リファクタ範囲に以下が含まれる場合に視覚 Island を立てる:

| 検出シグナル | 視覚 Island のヒント |
|---|---|
| 同一トークン (色 / spacing / rounded) が複数箇所に直書き | DESIGN.md のトークン化前の遺産。逆抽出→DESIGN.md へ集約する意図仮説 |
| `colors.primary` が CTA 以外に流用されている | DESIGN.md `## Do's and Don'ts` 違反、「装飾流用」の意図を確認 |
| 1 画面内にフォントウェイト 3 種以上 | DESIGN.md `## Do's and Don'ts` 違反、「強調の段階分け」の意図を確認 |
| ダークモード未対応 | 「ダークモード不要」or「将来対応予定」の意図を確認 |
| ベンダープレフィックス / レガシー CSS の混在 | 「ブラウザ対応範囲」の意図を確認 |

視覚 Island の `paths` は CSS / styled-components ファイルだけでなく、関連する React/Vue コンポーネント（視覚仕様が漏れている可能性のある場所）を含める。

### 2. 意図仮説提示

各島について意図仮説を生成する。仮説には必ず確度メタデータ（`コード確認` / `git 履歴確認` / `AI 推定` の 3 段階、archaeology-protocol.md と同じ語彙）を付与する。

仮説提示の対話文型・確度規約・捏造防止規約は `references/intent-hypothesis-protocol.md` 参照。

**禁則**:

- 確度メタデータなしで仮説を確定しない
- 「合っているはず」での自己確定をしない（人間の明示確認が必須）
- 1 回の応答で 5 島以上の仮説を一括提示しない（人間の判断疲労を避ける）

### 3. 認識合わせ（横方向）

**Step 3 は横方向**。仮説 ⇄ 人間 の擦り合わせループ。

各島について、人間に 4 値のいずれかで応答してもらう：

| 値 | 意味 | 人間の発話例 |
|---|---|---|
| `confirmed` | AI 仮説が合っている | 「合ってる」「その通り」 |
| `corrected` | 仮説は外れている、人間が修正 | 「違う、本当は X だった」 |
| `forgotten` | 思い出せない（Step 5 へ持ち越し） | 「忘れた、覚えてない」 |
| `absent` | 当時から意図なし／混沌 | 「特に考えてなかった、意図なし」 |

このステップの詳細な対話文型は `references/dialog-flow-archeo.md` 参照。

**禁則**:

- 1 セッションで 5 問を超えたら警告（philosophy.md §4「自律駆動を止めない」整合）
- 曖昧応答 2 回連続は「重要度低」と解釈し、当該島を `forgotten` で確定（spec-architect の E1 対応と同方針）
- AI が単独で `corrected` / `absent` を確定するのは**物理的に禁止**（テンプレ必須フィールドで担保、`references/absent-intent-protocol.md` §確定条件参照）

### 4. 境界曖昧領域の特定

島と島の境界が曖昧な箇所を AI が特定し、人間に提示する。

提示フォーマット（差分サマリのみ、全文提示しない）:

- 該当箇所のパス
- どちらの島に帰属させるかの選択肢（最大 3 つ）
- 各選択肢の根拠（呼び出し関係・命名・コミット履歴等）

人間は選択肢から 1 つを選ぶか、「両方に属する」「どちらでもない（新島として切り出す）」を宣言する。判断結果は `refactor-intent-map.md` の Boundaries セクションに記録する。

### 5. 忘却 or 想起の宣言

Step 3 で `forgotten` だった島について、人間が以下のいずれかを明示宣言する：

- **想起**: 「思い出した、本当は X だった」 → Island を `corrected` に格上げ
- **新規決定**: 「忘れたが、新たに X と決めていい」 → Island を `corrected` に格上げ（過去意図ではなく新規意図として記録）
- **意図不在の確定**: 「思い出せない、当時から意図がなかった」 → Island を `absent` に確定

`absent` 確定の条件は `references/absent-intent-protocol.md` の §確定条件参照。**人間の明示宣言なしで AI が `absent` を確定することは原則違反**。

### 6. 意図マップ確定

Phase β（生成）。AI が `assets/refactor-intent-map-template.md` に従って `delivery/refactor-intent-map.md` を生成する。

各 Island に必須記載:

- `paths`
- `inferred_intent`（AI 仮説）
- `human_confirmation`（4 値）
- `corrected_intent`（`corrected` 時のみ）
- `confidence`（コード確認 / git 履歴確認 / AI 推定）
- `S/U/R`
- `refactor_directive`（`preserve` / `restructure` / `discard_and_redesign`）
- `notes`

`refactor_directive` は人間が決定する。AI は推奨を提示できるが確定はしない。

成果物の配置は `delivery/refactor-intent-map.md`（canonical filename、`dev-env-spec.md` の参照権限マトリクスで A出力に該当）。複数回生成する場合は、新版で canonical 位置を上書きし、旧版を `delivery/archive/refactor-intent-map-YYYY-MM-DD.md` にアーカイブ移動する。L1 は archive/ を参照しない（canonical のみ参照、選択ロジック不要）。

### 7. 合意（縦方向）→ Layer 1 への譲渡

**Step 7 は縦方向**。意図マップ全体 ⇄ 人間 の譲渡合意。

人間に提示するのは差分サマリのみ（マップ全文ではない）：

- 検出された島の数
- 4 値の内訳（confirmed / corrected / forgotten / absent の件数）
- `refactor_directive` の分布
- Boundaries で確定した境界帰属
- Absent-Intent Zones の範囲

人間の応答:

- **合意** → Layer 1 への譲渡（refactor-intent-map.md を L1 入力として渡す）
- **修正要求** → 該当 Island の Step 3 へ戻る
- **追加島の発見** → Step 1 へ戻る（再走査）

**重要**: Step 7 の合意は philosophy.md §5「献上」とは異なる概念。献上は L1 → 人間の単方向。本 Step は L0 → L1 への譲渡（spec-architect の SPEC.md 譲渡と同等）。

L1 が `refactor-intent-map.md` を評価軸として使う仕組みは `references/handoff-to-evaluator.md` 参照。Phase γ（L1 改修）が完了するまでは、人間が手動でマップを参照しながらリファクタ依頼を組み立てる運用とする。

### 7.4. L0 自己検証

§7（L1 譲渡）に進む前に、§L0 完了の受け入れ基準 4 条件を逐項確認する。1 件でも FAIL があれば §7 へは進まず原因を解消する。

- [ ] **broken reference 検査**: `refactor-intent-map.md` が引用するファイル・パス（Island の `paths` 等）が実体として存在する（dead link なし）
- [ ] **必須フィールド充足**: 全 Island に `paths` / `inferred_intent` / `human_confirmation` / `confidence` / `S/U/R` / `refactor_directive` が記載されている。`pending` 状態が残っていない
- [ ] **Pre-flight 充足**: 本セッションで通過した §1 / §2 / §6 の各 Pre-flight 行が指定するリファレンスを実際に読んだ（intent-hypothesis-protocol.md / absent-intent-protocol.md / refactor-intent-map-template.md）
- [ ] **捏造検査**: `human_confirmation: corrected` の Island に `corrected_intent` が記載されている。`human_confirmation: absent` の Island に人間の明示宣言が `notes` に記録されている。AI 単独で `corrected` / `absent` を確定した形跡がない
- [ ] **受け入れ基準充足**: §L0 完了の受け入れ基準 4 条件（必須セクション充足 / 4 値ラベル付け / Step 7 合意 / 本 §7.4 PASS）を逐項チェック

検証結果は `delivery/refactor-intent-map.md` の Meta セクションに `self_verification: passed` として記録する。

## 入力

- プロジェクトルートへのアクセス
- 既存コード（src/ 等）
- git log / git blame
- `REGIME.md`（LC ≥ 1 確認用）
- `SPEC.md`（参照用、改変しない）
- 人間の発話（4 値応答 + 境界裁定 + 忘却/想起宣言）

## 出力

- `delivery/refactor-intent-map.md` — 意図マップ（Phase γ 接続後は L1 評価軸として参照される）
- 既存ファイル（コード・SPEC.md・REGIME.md 等）は**改変しない**

## 参照ドキュメント

### 本 skill 配下（assets / references）

- `assets/refactor-intent-map-template.md` — 意図マップテンプレート（Meta / Islands / Boundaries / Absent-Intent Zones、4 値必須フィールド）
- `references/dialog-flow-archeo.md` — Step 1〜7 の対話文型、Step 3 horizontal vs Step 7 vertical の分離規約、自己制限規約（5 問上限）
- `references/intent-hypothesis-protocol.md` — 仮説生成ヒューリスティック（コメント不在 / 命名混乱 / 重複ロジック / git log 不在 / テスト不在 / マジックナンバー）と確度規約
- `references/absent-intent-protocol.md` — `absent` 確定条件（人間明示宣言必須）と捏造防止規約（P-Arch-2 実装）
- `references/handoff-to-evaluator.md` — `refactor-intent-map.md` の I/O 規約（Phase γ で L1 が参照する仕様、Phase α では先行宣言版）

### 他 skill の参照（**転記禁止・参照のみ**、philosophy.md L4 メタ規則準拠）

- `../layer0-spec-architect/references/philosophy.md` — 6 条憲法（特に第1条フラクタル / 第3条情報純度 / 第4条人間責務 / 第5条献上）
- `../layer0-spec-architect/references/subphase-common-protocol.md` — Phase α/β/γ/δ の 4 フェーズ骨格（本 skill の 7 ステップは並走）
- `../layer0-spec-architect/references/ritual-protocol.md` — レベル判定（Phase β でリファクタ示唆検出時の archeo 起動推奨）
- `../layer0-spec-architect/references/dev-env-spec.md` — ファイル配置規則（`delivery/` 配置先）
- `../layer0-onboarding/references/archaeology-protocol.md` — 考古学的抽出（深度判定 shallow/standard/deep/full、機密領域の扱い、抽出不能領域の扱い）

## Level A 所属

本 skill は dialog-harness-layers 本体のもの。プロジェクトごとに再生成しない。プロジェクト差異は `delivery/refactor-intent-map.md` の内容に閉じる。

## 設計上の注意

- **spec-architect / onboarding との責務分離**: archeo は意図復元のみ。新機能追加・仕様改変は spec-architect、harness 後付け化は onboarding に委譲する
- **再起動可能**: onboarding と異なり使い捨てではない。リファクタ着手の度に再起動可能。複数回の起動履歴は `delivery/refactor-intent-map-*.md` のタイムスタンプで識別する
- **AI 推定の明示**: 確度メタデータを必ず付与。後続の Layer 1 がリファクタ実装時に参照できる状態を作る
- **捏造禁止の物理的担保**: `corrected` / `absent` 確定は人間明示宣言が必須。テンプレ必須フィールドで AI 単独確定を物理的に阻止する
- **L1 改修の段階性**: Phase α（本 skill 単独運用）では、人間が手動でマップを参照しながらリファクタ指示を組み立てる。Phase γ（L1 接続）以降で評価軸として自動参照される。詳細ロードマップは `references/handoff-to-evaluator.md` 参照
- **5 次元論との整合**: 本 skill は D4（マスタ skill）に属する。`refactor-intent-map.md` は D2（プロジェクト成果物）に配置される。D4 への動的書き込み禁止
