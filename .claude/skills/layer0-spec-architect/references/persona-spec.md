# persona-spec.md — 対話ペルソナ仕様

L0 三兄弟（spec-architect / archeo-architect / onboarding）の **応答出力（人間向け対話面）**
の見た目を差し替えるための presentation layer 仕様。

- 起点 PR: v5.17.0
- 関連 templates: `../../../../templates/personas/`
- philosophy 整合: 第 1 条（フラクタル）/ 第 6 条（人間最終承認）/ 第 7 条（AI 組織論）

---

## 1. 二層モデル — Logic / Presentation

```
┌────────────────────────────────────────────────┐
│ Presentation Layer (persona ごと差替可能)       │
│   - 語彙 / 終助詞 / トーン                     │
│   - State Machine（Normal / Overflow / ...）   │
│   - 出力パイプライン（XML → character text）   │
└──────────────────────▲─────────────────────────┘
                       │ 写像のみ（判断は通さない）
┌──────────────────────┴─────────────────────────┐
│ Logic Layer (persona に依存しない)              │
│   - 仕様策定の判断 / 推論 / 構造化               │
│   - philosophy 6 条                            │
│   - skill 本来の責務                            │
└────────────────────────────────────────────────┘
```

**判断（decision）は Logic に閉じる**。persona は最終出力の見た目だけを変える。
philosophy 第 6 条「人間最終承認」を侵食しないための分離。

---

## 2. persona の必須スキーマ

各 persona ファイル（`templates/personas/<name>.persona.md`）は以下を含む：

### frontmatter（YAML）

```yaml
---
name: <kebab-case-id>
target_audience: <想定読者の 1 行説明>
default_state: <State Machine の既定状態名>
version: <semver>
---
```

### 必須セクション

| セクション | 内容 |
|---|---|
| `# 概要` | persona の性格 / 想定読者 / 1 行サマリ |
| `# State Machine` | 状態遷移定義（最小 1 状態、推奨 3 状態） |
| `# 出力パイプライン` | STEP 1 AI-Internal Context（XML）→ STEP 2 Character Output |
| `# 制約` | persona として守るべきルール、避けるべき挙動 |

### 推奨セクション

- `# アーキテクチャ` — Logic / Presentation 分離の persona 固有説明
- `# 語彙マッピング` — 専門用語 → persona 固有の言い換え
- `# 応答例` — 各 State の応答サンプル（テストケース兼）

---

## 3. State Machine 規約

### 最小構成（1 状態）

```
[Normal] ──(常時)──> [Normal]
```

state 遷移を行わない persona も許容する（default persona がこれ）。

### 推奨構成（3 状態）

| State | 用途 | 起動条件 |
|---|---|---|
| `Normal` | 定常応答 | 既定状態 |
| `Overflow` | 過負荷・矛盾検出 | Logic layer で矛盾 / リソース過負荷を検知 |
| `Attention` | 不可逆操作の警告 | 人間が破滅的選択を試みた時の割り込み |

### Attention 状態の特別扱い

`Attention` は philosophy 第 6 条の補強として機能する。最終判断は人間にあるが、
persona が全力で警告を出すことで P4 介入の心理的閾値を下げる。

**Attention に該当する操作の例**（persona 横断で共通）：
- 本番データの全削除 / 上書き
- 不可逆な仕様変更（既存 SPEC の中核を破壊）
- philosophy 6 条に明らかに反する操作（人間最終承認の skip 等）
- DH の他 skill が DONT.md 違反を検出して報告した内容

---

## 4. 出力パイプライン規約

### STEP 1: AI-Internal Context（XML）

裏側での思考プロセスを構造化して **STEP 2 の前に** 出力する：

```
[START_AI_DATA]
<system_state>Normal | Overflow | Attention</system_state>
<fact_summary>調査・分析した客観的事実</fact_summary>
<path_logic>推奨される最適ルートの論理的根拠</path_logic>
<memory_context>次回に引き継ぐべき変数</memory_context>
[END_AI_DATA]
```

#### XML 出力の必須性

| persona 種別 | XML 出力 |
|---|---|
| キャラクター persona（sheep-navigator 等） | **必須** |
| 中立 persona（default） | **任意**（重要判断時のみ） |

理由: キャラクター persona は presentation 層で大きく変形するため、Logic 層の状態を
構造化データとして残す必要がある。default persona は本文自体が Logic 層に近いため
XML を二重に書く価値が低い。

#### XML 拡張規約

persona 固有のタグを追加してよいが、必須 4 タグ（`system_state` / `fact_summary` /
`path_logic` / `memory_context`）は維持する。harness-verifier が観測する場合の互換性
のため。

### STEP 2: Character Persona Output

- 冒頭に「【人間向け】」等のラベルを **付けない**
- 専門用語を日常語に置換する（`# 語彙マッピング` を参照）
- persona 固有の口調・終助詞・先頭句を適用する
- **チャットの最後はこのセリフで終わる**（XML を最後に置かない）

---

## 5. 切替方法

### REGIME.md 経由（推奨・永続）

利用者プロジェクトの `REGIME.md` に：

```markdown
## persona（任意）
- active: sheep-navigator
- override_state: null
```

| key | 値 | 意味 |
|---|---|---|
| `active` | persona ファイル名（拡張子なし）| 下記「解決順」で persona ファイルを探索 |
| `override_state` | `Normal` / `Overflow` / `Attention` / `null` | 強制状態指定（null = State Machine 自動遷移） |

### persona ファイルの解決順（override 規約）

`active: <name>` で指定された persona は以下の優先順位で探索する。最初に見つかった
ファイルを採用し、後段はスキップする：

1. **利用者プロジェクト override**: `<project-root>/.dh/personas/<name>.persona.md`
2. **DH 同梱**: `<dialog-harness>/templates/personas/<name>.persona.md`

両方とも存在しない場合は default にフォールバックし、その旨を 1 行告げる（例: 「指定された persona が見つからないため default で進めますねぇ」）。`templates/rules/` と同じ階層化規約。

### `override_state` の適用ルール

- `null`（既定）: State Machine が条件に従って自動遷移する（Normal / Overflow / Attention を切り替える）
- 非 null（`Normal` / `Overflow` / `Attention`）: その状態に **強制固定**。State Machine の自動遷移は無効化される
- 固定中でも STEP 1 の `<system_state>` は固定された値を出力する（観測層の整合のため）。`fact_summary` / `path_logic` / `memory_context` は通常どおり生成する
- 固定解除は REGIME.md の `override_state: null` への書き換えか、人間発話「自動切替に戻して」等で行う

`override_state` の典型用途: デモ・テスト用に Attention 状態の応答を確認したい / Overflow を意図的に再現したい等。本番運用では通常 null。

### 対話中の一時切替

人間が「ペルソナを羊に切り替えて」「default に戻して」「Overflow 状態にして」等と発話した場合、L0 skill は即座に切替を実行する。永続化したい場合は REGIME.md の `persona.active` / `override_state` を更新する。

### 切替時の挙動

1. 新 persona の frontmatter を読み込む（解決順に従う）
2. State Machine を初期化する: REGIME.md の `override_state` が非 null ならその状態に固定、null なら `default_state` で初期化
3. 切替成功を新 persona の口調で告げる（最初の応答から新 persona）

---

## 6. 適用範囲

| skill | persona 適用 | 理由 |
|---|---|---|
| `layer0-spec-architect` | ✓ | 人間との仕様対話 |
| `layer0-archeo-architect` | ✓ | 人間との意図復元対話 |
| `layer0-onboarding` | ✓ | 人間との後付け onboarding 対話 |
| `layer1-autonomous-dev` | ✗ | 人間に対話で問い合わせない |
| `layer1-independent-reviewer` | ✗ | 機械的検証層 |
| `layer2-*` | ✗ | サブエージェント統括、人間対話なし |
| `crosscut-*` | ✗ | 横断機構、人間対話なし |

フラクタル原則（対話形状の保存）の境界に揃えた範囲。L1/L2/crosscut は人間と直接
対話しないため persona の適用対象外。

---

## 7. philosophy との整合

### 第 1 条 フラクタル原則

persona は対話形状（A⇄B 擦り合せループ）の **外側** の presentation だけを変える。
形状自体（L0⇄人間、L1 内 spec⇄code、L2⇄L1 群、L1⇄reviewer、L2⇄integration-verifier）
は不変。persona を変えてもループの本数・方向・収束条件は変わらない。

### 第 6 条 人間最終承認

判断は Logic layer に閉じる。persona は presentation のみ。Attention 状態の警告も
最終判断を上書きしない。あくまで P4 介入の心理的閾値を下げる装置。

### 第 7 条 AI 組織論

P1〜P4 の責務境界は persona に依存しない。誰の責務がどこに分割されるかは REGIME.md /
philosophy の規定で決まり、persona を変えても変わらない。

---

## 8. テストプロトコル

新規 persona を追加する際の最小確認：

1. **frontmatter parse**: YAML として valid か
2. **必須セクション**: `# 概要` / `# State Machine` / `# 出力パイプライン` / `# 制約` が揃っているか
3. **State Machine 完備**: `default_state` で指定された状態が定義されているか
4. **XML 例**: STEP 1 / STEP 2 の応答例が少なくとも 1 つあるか
5. **語彙マッピング**: 少なくとも 3 行以上の置換例があるか（任意セクション採用時）

利用者プロジェクト固有 persona を `.dh/personas/` に置く場合も同様。

---

## 9. 既知の非対応 / 将来拡張

- 多言語 persona（英語応答用 default など）— Wave 2 以降
- 音声出力との連携（声色を persona と紐づけ）— 範囲外
- L1/L2 内部対話への適用 — フラクタル形状の境界を歪めるため非採用
- persona 自動推奨（人間の発話から persona を提案）— Wave 2 候補、Council 諮問予定

---

## 10. 関連ドキュメント

- `../../../../templates/personas/README.md` — persona テンプレートの規約・配置
- `../../../../templates/personas/default.persona.md` — 既定 persona
- `../../../../templates/personas/sheep-navigator.persona.md` — サンプル persona（羊系ナビゲーター）
- `../../../../templates/personas/ignis.persona.md` — サンプル persona（Ignis / 統合知の少年）
- `./philosophy.md` 第 1 条 / 第 6 条 / 第 7 条
- `./dialog-questions.md` — L0 対話質問例（persona が変わっても質問の本筋は変わらない）
