# templates/rules/ — 階層化規約

**起点 PR**: PR #76（Wave 1 候補 6）
**origin**: ECC-derived（everything-claude-code v2.0.0-rc.1 `rules/` 階層構造 + `CONTRIBUTING.md` の override 規約）
**chewing translation**: T1 + T3（構造保持 + サブセット選別: 言語先取りなし）
**Council 採決**: `council-2026-05-11T05:00:00Z-w1qb03`（recommended A: 言語先取りなし、L0 対話で必要言語のみ生成）

---

## 配置構造（DH 流遅延戦略）

```
templates/rules/
├── README.md           # 本ファイル（階層化規約）
├── common/             # 言語横断 rules（空 scaffold、後続 PR で内容充填）
└── <lang>/             # L0 対話で必要言語のみ生成
    ├── ...
    └── ... (specific files)
```

ECC は 14 言語（cpp / csharp / dart / golang / java / kotlin / perl / php / python / rust / swift / typescript / web / zh）を先取り配置するが、**DH では `common/` のみを scaffold し、`<lang>/` は L0 対話確定後に必要言語のみ生成** する。

これは philosophy 第 1 条「フラクタル原則」（対話で確定する DH の規律）と、咀嚼プロトコル T3「サブセット選別」（業界実装プリミティブをそのまま吸収しない）の組合せ。

---

## override 規約（ECC 由来、構造保持）

`common/` と `<lang>/` に **同名ファイル** が存在する場合、`<lang>/` は `common/` の同名ファイルを override する。読み込み順序:

1. まず `common/<file>` を読む
2. `<lang>/<file>` が存在すればその内容で上書き

### 重要: flatten 配置の禁止

```
# ✓ 正しい階層
templates/rules/
├── common/
│   └── coding-style.md
└── python/
    └── coding-style.md  # python 文脈で common/coding-style.md を override

# ✗ 禁止: flatten 配置
templates/rules/
├── common.coding-style.md
└── python.coding-style.md  # ← 相対 ../common/ 参照が壊れる
```

flatten 配置は ECC `CONTRIBUTING.md` で明示的に禁止されている:

> "Common and language-specific directories contain files with the same names. Flattening causes language-specific to overwrite common, breaking relative `../common/` references."

DH もこの規約を継承する（T1 構造保持）。

---

## 相対参照ルール

`<lang>/<file>` から `common/` を参照する場合は **相対パス `../common/<file>`** を使用する。絶対パス（`templates/rules/common/<file>`）は **禁止**。

理由: `templates/rules/` 自体が将来 `~/.claude/templates/rules/` 等の異なる絶対位置に配置される可能性があり、相対参照のみが移動耐性を持つ。

---

## L0 対話との接続

L0 spec-architect の `dialog-questions.md` に以下の質問が追加されている（PR #76 同梱）:

- 「使う技術が 1 つだけ？ それとも複数の技術を組み合わせる？」（多言語プロジェクト判定）
- 「コーディングの決まりを言語別に分けたい？」（言語別 rules 採用判定）

これらの回答に基づき、L0 が `templates/rules/<lang>/` を生成する。

---

## common/ の現況

- `agentshield-reference.md`（Wave 2、PR #78）— セキュリティ静的解析の参照導入規約
- `ui-baseline.rules.md`（v5.23.0）— UI Baseline RL（相互作用層・常時適用、B-01〜B-25）。UI を伴うプロジェクトで共通 RL として読み込む。適用経路は DH 側 `.claude/skills/layer0-spec-architect/references/design-system-spec.md`「UI 相互作用層」
- `ui-specialization.context.md`（v5.23.0）— UI 目的特化（S-01〜S-06 + 衝突解決）。利用者は `.dh/rules/common/ui-specialization.context.md` で override 可
- `<lang>/`: 存在しない（L0 対話確定後に必要言語のみ生成）

Wave 2 末振り返り儀式で「L0 対話で頻出した言語」を観測し、頻出する場合は **「推奨言語プリセット」を再諮問**（Council 諮問 w1qb03 の minority opinion 経営者 B: 3 言語先取り、`python / typescript / go`）。

---

## バージョン

- v0.1.0（Wave 1）— 規約のみ scaffold、内容は後続 PR で充填
- 拡張候補（Wave 2 以降）:
  - `common/` 内に最初の言語横断 rule を配置（coding-style / commit-message / pr-template 等）
  - L0 対話の頻出データから「推奨言語プリセット」を再諮問
