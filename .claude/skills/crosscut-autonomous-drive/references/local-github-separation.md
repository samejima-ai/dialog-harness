# local / github 運用分離 — 実装ガイド

`delegation-boundary.md` §4「local / github の分離 — 権限差ではなく検証手段差」を
**実際に効かせる**ための運用手順。§4 は憲法（L-FROZEN-META、AI 改訂禁止）ゆえ方針のみを
定める。本ファイルはその方針を物理的に成立させる **実装・運用の一次情報源**（非憲法・L-FULL）。

> 一次方針: `delegation-boundary.md` §4 / §6
> 本ファイル: §4 を成立させる hook・squash 運用の how（方針には踏み込まない）

---

## 1. 分離の本質（おさらい）

権限委譲度は local / github で**同一**（どちらも L-FULL 全自律）。違いは**検証手段にのみ**宿る。

| 環境 | 検証手段 | 全自律の範囲 | 制約 |
|------|----------|--------------|------|
| **local** | hook（PostToolUse）+ lint + 型 | commit まで無確認で走る | **squash 前提**（C-2） |
| **github** | sub_agent_review（claude / gemini）+ 軽量機械 CI | PR 作成 → auto-merge | §6 CI スリム化方針 |

local が「commit まで無確認」で走れるのは、commit が **revert / amend / squash 可能な可逆操作**
だから。push して公的空間に出た時点で sub_agent_review を必ず通す。

---

## 2. local 検証層の実体 — `local_verify.py`

§4 の「local: hook（PostToolUse）+ lint + 型」を担うスクリプト。

- **場所**: `.claude/skills/crosscut-autonomous-drive/scripts/local_verify.py`
- **接続**: `.claude/hooks.json` の `PostToolUse` に observer と**併記**（観測層と検証層の分離）
- **契約**: **warn-only**（exit code 常に 0）。tool call を block しない。
  検出結果は stderr の `[local-verify]` 行で AI 自身に通知し、commit 前に直す機会を与える。
  philosophy.md 第 6 条「自動 block は人間最終承認の代替にならない」準拠。
- **対象 tool**: `Write` / `Edit` / `MultiEdit` / `NotebookEdit` の直後のみ。それ以外は素通り。

### 検証コマンドの決定（優先順）

| 順 | 条件 | 実行内容 |
|----|------|----------|
| 1 | 環境変数 `DH_LOCAL_VERIFY_CMD` が設定 | その shell コマンド（配布先の lint / 型に差し替え） |
| 2 | `harness-verifier/verify.py` が存在（= DH 本体） | `verify.py --json`（構造健全性・第 2 条 第 1 層 計算的センサー） |
| 3 | どちらも無い | 何もしない（exit 0） |

### 配布先プロジェクトでの差し替え

DH 本体の検証は「DH 構造健全性」固有なので、配布先では自分の決定論検査に差し替える。
`DH_LOCAL_VERIFY_CMD` を環境（`.env` / shell rc / CI 外の local 設定）に置く:

```bash
# 例: TypeScript プロジェクト
DH_LOCAL_VERIFY_CMD="npm run -s typecheck && npm run -s lint"
```

```bash
# 例: Python プロジェクト
DH_LOCAL_VERIFY_CMD="ruff check . && mypy ."
```

決定論検査だけを置くこと（第 2 条 / C-4）。確率的レビュー（LLM）を local hook に混ぜない
— それは push 後の sub_agent_review の領域。

---

## 3. squash 前提の運用（C-2）

local の「commit まで無確認」が公的履歴を汚さない前提が **squash**。

### 原則

- 自律走行中の試行錯誤 commit 列（WIP・revert 往復・typo fix）は **PR 化（push）時に
  squash で 1 つの論理単位へ畳む**。
- 誤 commit が git 履歴に永続しない = local commit の可逆性が保たれる = §4 が成立する。

### 実務手順

1. **local 走行中**: hook の warn を見ながら、commit は気軽に刻んでよい（無確認・全自律）。
   `wip:` `fixup:` 等の粗い commit が並んでよい。
2. **PR 化（push）時**: squash で論理単位に畳む。実現手段はいずれか:
   - GitHub の **Squash and merge**（auto-merge.yml は merge 時 squash を前提に設計）
   - push 前の `git rebase -i`（**ただし対話モードはこの harness では不可** — `git reset --soft`
     + 再 commit で代替）
3. **PR 本文**: squash 後の 1 論理単位を Summary / Why / Test plan で説明（CLAUDE.md テンプレ）。

### squash で畳む際の注意（Windows / この環境）

- 対話的 rebase（`git rebase -i`）はこの環境で不可。`git reset --soft <base>` →
  再 commit で squash 相当を実現する。
- `history/archive/` にコロン入りファイル名があり Windows で checkout 不能。
  `git reset --hard` は途中失敗するため `git reset --mixed` を使う
  （メモリ `reference_windows_colon_filenames` 参照）。

---

## 4. github 側（push 後）— 検証手段の切替

push した瞬間に検証手段が hook → sub_agent_review + 軽量機械 CI に切り替わる。

| 段階 | 検証主体 | ファイル |
|------|----------|----------|
| push / PR open | claude-review（4 フェーズ Council） | `.github/workflows/claude-review.yml` |
| push / PR open | gemini-review（仕様軸） | `.github/workflows/gemini-review.yml` |
| push / PR open | 決定論 CI（harness-verify / 型 / lint / test） | `.github/workflows/harness-verify.yml` 他 |
| 全 green | auto-merge（決定論 7 条件 AND → squash merge） | `.github/workflows/auto-merge.yml` |

§6 の CI スリム化方針: **決定論は CI に残し、判断は sub_agent へ**。
local hook（決定論）と sub_agent_review（判断）は責務が重ならない。

---

## 5. 関連

- `delegation-boundary.md` §4 / §6 — 一次方針（憲法・AI 改訂禁止）
- `.claude/skills/crosscut-autonomous-drive/scripts/local_verify.py` — local 検証層の実体
- `.claude/hooks.json` — observer（観測層）と local_verify（検証層）の接続
- `.claude/skills/crosscut-hook-observer/SKILL.md` — 観測層（検証しない）との分離設計
- `scripts/check_template_sync.py` — github 側テンプレ二重管理の同期検証（G-003 解消）
