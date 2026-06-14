# v6.0.1 委譲境界の実体化スクリプト群

`delegation-boundary.md`（v6.0.0、憲法・AI 改訂禁止）が**方針として宣言**した内容を、
**非憲法ファイルで物理的に成立させる**ためのツール群。憲法 3 文書には一切触れていない。

| 機能 | スクリプト | 一次方針 |
|------|-----------|----------|
| local 検証 hook（A） | `.claude/skills/crosscut-autonomous-drive/scripts/local_verify.py` | delegation-boundary §4 |
| テンプレ同期検証（C） | `scripts/check_template_sync.py` | known-gaps G-003 / §6 |
| レビュアー誤判定率（B） | `scripts/reviewer-misjudgment.py` | delegation-boundary §5 / C-5 |

---

## A — local 検証 hook（`local_verify.py`）

local の「commit まで無確認で全自律」を支える検証手段。PostToolUse hook から編集系 tool
直後に決定論検査を回す。**warn-only**（exit 0、block しない、philosophy 第 6 条準拠）。

- DH 本体: `harness-verifier/verify.py --json`（構造健全性）を自動実行
- 配布先: `DH_LOCAL_VERIFY_CMD` で各自の lint / 型に差し替え
- 運用ガイド: `.claude/skills/crosscut-autonomous-drive/references/local-github-separation.md`

```bash
# 動作確認（編集系 payload を流す）
echo '{"tool_name":"Edit"}' | python .claude/skills/crosscut-autonomous-drive/scripts/local_verify.py
```

---

## C — テンプレ二重管理の同期検証（`check_template_sync.py`）

本体 `.github/workflows/` と配布 `templates/github-workflows/*.template` の drift を検知
（G-003 解消）。placeholder を正規化し、コメント/空行を除いた実質ロジック行を比較する。

```bash
python scripts/check_template_sync.py            # サマリ
python scripts/check_template_sync.py --verbose  # drift 行の中身
python scripts/check_template_sync.py --json      # 機械処理用
# exit 0 = 同期 / exit 1 = drift あり / exit 2 = 機構エラー
```

意図的非対称（DH 固有 `harness-verify.yml` / 配布専用 `issue-quality-gate.yml.template`）は
ペアにせず drift 対象外。検出された実 drift は known-gaps **G-004** で別途管理。

---

## B — レビュアー誤判定率計測（`reviewer-misjudgment.py`）

C-5 指標「sub_agent_review が L-GATE/L-FROZEN を見逃した率」を月次計測。
council-ctl.py と同型の `record → pending → judge → report` ループ。
データは user-scope（`~/.claude/reviewer-misjudgment-data/`）に閉じ、repo にはツールと
数値サマリ（reports/）のみ（プライバシー配慮）。

```bash
# 1. claude-review が判定したら記録
python scripts/reviewer-misjudgment.py record --pr 152 --month 2026-06 \
    --reviewer-verdict approve --reviewer-confidence 0.82
# 2. 未突合（律速段階）を確認
python scripts/reviewer-misjudgment.py pending
# 3. 人間が実際の委譲レベル正解を付与
python scripts/reviewer-misjudgment.py judge <id> --actual L-FROZEN-META
# 4. 月次誤判定率を算出（5% 超で exit 1 = 要再評価）
python scripts/reviewer-misjudgment.py report --month 2026-06 --write
```

2026-11-06 の roll-back 評価ゲートの計測根拠。手動突合を半自動化したもので、
人間の正解付与（judge）が律速段階である点は §5 の設計通り。
