# skill-creator Audit v5.0.0

dialog-harness/layer's v5.0.0 で追加・改修された skill に対する skill-creator 視点での独立監査結果。

- 監査日: 2026-04-27
- 監査対象: PR #18（branch: `claude/prepare-major-upgrade-vnL6E`）
- 監査基準: Anthropic skill 規約（progressive disclosure / frontmatter / naming / SKILL.md 構造）+ skill-creator skill 慣習
- AI 能力バージョン: claude-opus-4-7

総合判定: **PASS**（MEDIUM-1 fix 済 / LOW 2 件は次回改修課題として記録）

---

## 監査対象

| skill | 種別 | SKILL.md 行数 |
|---|---|---|
| `crosscut-council` | リネーム（既存） | 205（変更最小、frontmatter + description のみ） |
| `crosscut-issue-dispatcher` | 新規 | 40 |
| `crosscut-issue-implementer` | 新規 | 52 |
| `crosscut-verifier-drift` | 新規 | 51 |
| `crosscut-verifier-philosophy` | 新規（placeholder） | 50 |
| `crosscut-feedback-loop` | 新規 | 59 |

---

## PASS 項目

### 1. frontmatter 妥当性

| 項目 | 結果 |
|---|---|
| `name` と directory 名一致 | 6/6 OK |
| `description` ≤ 1024 chars | 全件（最大 731 / 最小 398） |
| `description` の when-to-use 明示 | 全件 OK |
| 第三者視点の記述 | 全件 OK |

### 2. 命名規則

| 項目 | 結果 |
|---|---|
| kebab-case | 全件 OK |
| `crosscut-` prefix の一貫性（横断機構） | 全 6 件 OK |
| Level A 第二の prefix として確立 | OK（`layerN-` と並列） |

### 3. progressive disclosure（SKILL.md と references の責務分離）

| skill | SKILL.md（entry） | references/<*>-protocol.md（detail） |
|---|---|---|
| crosscut-issue-dispatcher | 40 行 | dispatch-protocol.md（CTL 別動作詳細） |
| crosscut-issue-implementer | 52 行 | implement-protocol.md（claude-code-action 詳細・CI 連携） |
| crosscut-verifier-drift | 51 行 | verify-protocol.md（drift 種別 / 軽量 vs フル） |
| crosscut-verifier-philosophy | 50 行 | （placeholder のため不在、v5.1.0 追加予定） |
| crosscut-feedback-loop | 59 行 | feedback-protocol.md（還流マトリクス） |
| crosscut-council | 既存 12 ファイル + 新規 ctl-maturity-strategy.md | OK |

SKILL.md は 40-59 行（既存 layer 系 102-451 行の範囲内）で、entry point として適切。

### 4. SKILL.md 構造の統一

各 SKILL.md が以下のセクションを持つ：

- `## 発動条件` (when to use)
- `## 処理フロー` (how to use)
- `## 関連` (related references / templates)

placeholder の verifier-philosophy も同等の構造を持つ。

### 5. assets/ 不在の妥当性

新 5 skill は behavior protocol skill であり、テンプレート性なし → assets/ 不在は正解。

### 6. 関連参照の整合性

各 SKILL.md の「関連」セクションで参照先が実在することを確認：

```bash
$ for f in .claude/skills/crosscut-*/SKILL.md; do
    grep -oE '\.claude/skills/[a-z-]+/[a-zA-Z0-9./_-]+' "$f" | while read p; do
      [ -e "$p" ] || echo "BROKEN ref: $p in $f"
    done
  done
（broken references なし）
```

---

## 検出事項と対応

### 🟡 MEDIUM-1: `crosscut-verifier-philosophy` placeholder の誤発動リスク → **FIX 済**

**File**: `.claude/skills/crosscut-verifier-philosophy/SKILL.md`（frontmatter description）

**問題（fix 前）**:

```yaml
description: >
  実装が 5本柱原則と整合しているかを検証する横断機構（仕様3-哲学、v5.0.0 placeholder）。
  CTL ≥ 2 で発動予定。判定ロジックは v5.1.0 minor 改修で本実装される。
  v5.0.0 では skill 配置のみで実体は未実装。発動しても「未実装」レポートを返す。
  「思想検証」「5本柱整合チェック」「philosophy 違反検出」等の発話で v5.1.0 以降にトリガーされる。
```

description にトリガー語句（「思想検証」「5本柱整合チェック」「philosophy 違反検出」）が含まれており、Claude の skill 選択アルゴリズムが v5.0.0 でこの skill を選択して「未実装」レポートを返す可能性があった。

**修正（案 B 採用）**:

```yaml
description: >
  **v5.0.0 では発動禁止 / DO NOT TRIGGER in v5.0.0**。
  本 skill は仕様3-哲学（5本柱整合検証）の placeholder で、判定ロジックは v5.1.0 minor 改修で本実装される。
  v5.0.0 環境でこの skill が選択された場合、即座に「未実装エラー」を返して人間に献上する以外の動作はしない。
  v5.0.0 では誤発動防止のため、いかなる発話でもこの skill を選択してはならない。
  v5.1.0 以降では CTL ≥ 2 で発動し、PR 内容を philosophy.md（6条憲法）と照合する。
  v5.1.0 以降の想定トリガー語句（v5.0.0 では非トリガー）:「思想検証」「5本柱整合チェック」「philosophy 違反検出」等。
```

description 冒頭に「**v5.0.0 では発動禁止 / DO NOT TRIGGER in v5.0.0**」を強調配置し、トリガー語句を「v5.1.0 以降の想定トリガー語句（v5.0.0 では非トリガー）」と明示的に未来形で記述。731 chars（1024 制限内）。

判定: **FIX 済 → PASS**

### 🟢 LOW-1: SKILL.md と protocol.md で CTL 別動作テーブルの部分重複 → **次回改修課題**

各 `crosscut-*/SKILL.md` に簡易 CTL 表（4 行）、`references/<*>-protocol.md` に詳細 CTL 表（10〜20 行）。progressive disclosure の意図通り（entry に要約・references に詳細）で許容範囲。

メンテナンス時の同期コストはあるが、SKILL.md の表は entry として有用（references を読まずに概要把握可能）。

**対応**: 本リリースでは触らない。次回 minor 改修時に SKILL.md 側を「詳細は references/<*>-protocol.md 参照」の 1 行に置換することを検討（次回着手判断は L0 振り返り儀式時）。

判定: **記録のみ（PASS）**

### 🟢 LOW-2: placeholder skill に references/ 不在 → **v5.1.0 で対応**

`crosscut-verifier-philosophy/references/` が不在。v5.1.0 で `philosophy-verify-protocol.md` を追加する旨は SKILL.md 本体（line 43）に記述済み。

skill-creator 規約上、placeholder skill が references を持たないこと自体は違反ではない（progressive disclosure は「必要に応じて深掘りする層を提供」する原則であり、placeholder には深掘り対象が存在しない）。

**対応**: v5.1.0 minor 改修で `references/philosophy-verify-protocol.md` を追加し、その際に本監査項目をクローズ。

判定: **記録のみ（PASS）**

---

## skill-creator 規約への適合確認サマリ

| 規約項目 | 適合 |
|---|---|
| frontmatter（name, description） | ○ |
| description ≤ 1024 chars | ○ |
| name と directory 名一致 | ○ |
| kebab-case 命名 | ○ |
| SKILL.md は entry point として簡潔 | ○ |
| 詳細は references/ に分離（progressive disclosure） | ○ |
| assets/ はテンプレート専用 | ○（不要 = 不在） |
| 関連参照の broken link 無し | ○ |
| placeholder skill の誤発動防止 | ○（MEDIUM-1 fix 後） |

---

## 総合判定

**PASS**

skill-creator 視点での新規 5 skill + 既存 1 skill リネームは Anthropic skill 規約に適合。MEDIUM-1 は本監査での fix で解消、LOW-1 / LOW-2 は次回改修課題として記録（本リリースの merge ブロックには該当しない）。

本監査は L1 自己検証（`delivery/SELF-VERIFICATION-v5.0.0.md`）と独立した skill-creator 専用視点での確認であり、両者がいずれも PASS であることを以て v5.0.0 の skill 開発側面の正常完結を認める。

最終承認は人間判断（spec §6 哲学的整合性最終判断 + サンプルプロジェクト試運転）に委ねる。

---

## 参照

- 上位検証: `delivery/SELF-VERIFICATION-v5.0.0.md`（spec §5.5 準拠の総合自己検証）
- 仕様原典: `dh-upgrades/upgrade-spec-v5.0.0.md`
- 設計判断: `history/ARCH-DECISIONS.md`（AD-001〜AD-007）
