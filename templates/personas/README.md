# templates/personas/ — 対話ペルソナ定義

DH（dialog-harness）の **対話インターフェース（応答出力）** を差し替える presentation 層のテンプレート群。
人間と対話する L0 三兄弟（spec-architect / archeo-architect / onboarding）の応答スタイルを
プロジェクトごとに切り替えるための仕組み。

---

## なぜ persona 層が必要か

DH は **非エンジニアを主対象** にしたメタハーネスである。仕様策定の対話は技術用語を排除した
日常語で行われるが、人間によって心地よい応答スタイルは異なる：

- 中立的・事務的な相手と話したい人
- フレンドリーな相手と話したい人
- キャラクターと話す形式の方がリラックスできる人

これまで応答スタイルは spec-architect の地肌（中立トーン）固定だった。本 layer は応答スタイルを
**差し替え可能な独立 axis** として外部化する。仕様策定の中身（Logic layer）には触れない。

---

## アーキテクチャ — Logic / Presentation の二層分離

```
┌──────────────────────────────────────────────────────────────┐
│ Presentation Layer (External, persona ごと差替可能)            │
│   - 語彙 / 終助詞 / トーン / 顔文字                            │
│   - State Machine（Normal / Overflow / Attention 等）          │
└────────────────────────────▲─────────────────────────────────┘
                             │ 写像
┌────────────────────────────┴─────────────────────────────────┐
│ Logic Layer (Internal, persona に依存しない)                   │
│   - 仕様策定の判断 / 分析 / 構造化データ                       │
│   - philosophy 6 条憲法の制約                                  │
│   - <fact_summary> <path_logic> <memory_context>               │
└──────────────────────────────────────────────────────────────┘
```

**重要**: 判断（decision）は Logic layer に閉じる。persona は出力の見た目だけを変える。
philosophy 第 6 条「人間最終承認」を侵食しないための分離。

---

## 配置構造

```
templates/personas/
├── README.md                      # 本ファイル（規約・切替手順）
├── default.persona.md             # 既定 persona（中立・事務的）
├── sheep-navigator.persona.md     # サンプル: 羊系ナビゲーター
└── ignis.persona.md               # サンプル: 統合知の少年 / 精神体の子
```

将来追加 persona は `*.persona.md` 形式で同 directory に配置する。命名は kebab-case。

---

## persona.md の必須セクション

各 persona ファイルは以下のセクションを必ず含む（schema は `persona-spec.md` を参照）：

1. **frontmatter**（YAML）: `name` / `target_audience` / `default_state` / `version`
2. **# 概要**: persona の性格・想定読者・1 行サマリ
3. **# State Machine**: 状態遷移（最小 1 状態、推奨 3 状態）
4. **# 出力パイプライン**: STEP 1 AI-Internal Context（XML）→ STEP 2 Character Persona Output
5. **# 語彙マッピング**: 専門用語 → 日常語の置換例（任意だが推奨）
6. **# 制約**: persona として守るべきルール、避けるべき挙動

---

## 切替方法

### REGIME.md 経由（推奨）

利用者プロジェクトの `REGIME.md` に以下の key を追加：

```markdown
## persona（v5.17.0 追加、任意）
- active: sheep-navigator        # templates/personas/<name>.persona.md を指す
- override_state: null           # 強制状態指定（通常は null = 自動遷移）
```

未指定時は `default.persona.md` が active になる（後方互換）。

### 一時切替（対話中）

人間が対話中に「ペルソナを羊に切り替えて」「default に戻して」と発話した場合、
spec-architect は即座に切替を実行する。永続化したい場合は REGIME.md を更新する。

---

## override 規約

`templates/rules/` と同じ階層化規約に従う：

1. 利用者プロジェクトに `.dh/personas/<name>.persona.md` があればそれを優先
2. 無ければ DH 同梱の `templates/personas/<name>.persona.md` を使う

flatten 配置（`.dh/personas.sheep-navigator.md` 等）は禁止。

---

## 適用範囲

persona は **人間に向けて出力する skill** にのみ適用される：

| skill | persona 適用 | 理由 |
|---|---|---|
| layer0-spec-architect | ✓ | 人間との仕様対話 |
| layer0-archeo-architect | ✓ | 人間との意図復元対話 |
| layer0-onboarding | ✓ | 人間との後付け onboarding 対話 |
| layer1-autonomous-dev | ✗ | 人間に対話で問い合わせない（philosophy 第 7 条 P4 介入のみ） |
| layer1-independent-reviewer | ✗ | 機械的検証層、対話なし |
| layer2-* | ✗ | サブエージェント統括、人間対話なし |
| crosscut-* | ✗ | 横断機構、人間対話なし |

フラクタル原則（対話形状の保存）の境界に揃えた範囲。

---

## philosophy との整合

- **第 1 条 フラクタル原則**: persona は対話形状（A⇄B 擦り合せループ）の外側の presentation だけを変える。形状自体は不変。
- **第 6 条 人間最終承認**: 判断は Logic layer に閉じる。persona は presentation のみ。
- **第 7 条 AI 組織論**: P1〜P4 の責務境界は persona に依存しない。

詳細な仕様は `.claude/skills/layer0-spec-architect/references/persona-spec.md` 参照。

---

## バージョン

- v0.1.0（v5.17.0 同梱）— default + sheep-navigator の 2 persona、REGIME.md 切替、L0 三兄弟のみ適用
- v0.2.0（追加）— ignis persona を追加（統合知の少年 / 精神体の子、Normal / Overflow / Attention の 3 状態構成、character alias: Thaumazein / Error404 / Wrath）
- 拡張候補:
  - L0 対話頻出パターンから「推奨 persona プリセット」を再諮問
  - 利用者プロジェクト固有 persona の `.dh/personas/` 配置サポート充実
  - 多言語 persona（英語版 default など）
