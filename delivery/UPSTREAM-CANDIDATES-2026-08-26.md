# UPSTREAM 候補 — kakuman-platform-v3.0

> 逆流路（v7 Phase 1）の観測出力。**判断ではなく候補提示**であり、採択は人間ゲート
> （`dh-manifest.yml` §upstream `gate: human`）。本ファイルの人間記入欄を埋めることが
> Phase 1 の完了条件であり、その結果が Phase 2/3 のスコープを確定させる。

- 走査日: 2026-08-26
- 配布先: `/home/user/kakuman-platform-v3.0`
- 判定方式: **存在差分のみ**（内容比較・優劣判定はしない = U-4）
- gate: `human`

## 計数

| 指標 | 件数 |
|---|---|
| 候補 | 26 |
| 採択 | 0 |
| 却下 | 0 |
| 保留 | 0 |
| 採否未記入 | 26 |
| 事故の日付が未記入 | 26 |

> 採否未記入が 0 になった時点で本サイクルの Phase 1 は完了する。**候補が列挙された
> ことは完了ではない**（計数されない観測層への退化を 3 軸が独立に警告した）。

## 候補

> 「事故の日付」「それが解いた問題」は機械には書けないので空欄で出す。**還流すべきは
> 機構ではなく、機構を必要とした出来事である**（U-5）。日付と痛みを剥いだ機構だけを
> 親に積むことは、事故を経ていない規範の自己増殖にあたる。

| 候補 | 種別 | 出自 | 事故の日付 | それが解いた問題 | 固有依存 | 採否 |
|---|---|---|---|---|---|---|
| `.claude/skills/article-forge/` | skill | `kakuman-platform-v3.0` | — | — | — | — |
| `.claude/skills/caaf-wiring/` | skill | `kakuman-platform-v3.0` | — | — | — | — |
| `.claude/skills/feedback-triage/` | skill | `kakuman-platform-v3.0` | — | — | — | — |
| `.claude/skills/l0-pre-brainstorm/` | skill | `kakuman-platform-v3.0` | — | — | — | — |
| `.claude/skills/news-publish/` | skill | `kakuman-platform-v3.0` | — | — | — | — |
| `.claude/skills/supabase-migration-safe/` | skill | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/check-claude-md-size.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/check-gate-cache.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/check-prod-rls-drift.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/check-routing-gates.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/check-spec-size.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/check-traps-sync.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/lint-admin-guards.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/lint-global-env.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/lint-icons.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/lint-internal-routing.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/lint-migrations.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/lint-ops-schema-private.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/lint-rls-recursion.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/lint-soft-delete-filter.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `scripts/lint-test-reachability.mjs` | mjs | `kakuman-platform-v3.0` | — | — | — | — |
| `.github/workflows/README.md` | md | `kakuman-platform-v3.0` | — | — | — | — |
| `.github/workflows/ci.yml` | yml | `kakuman-platform-v3.0` | — | — | — | — |
| `.github/workflows/news-ingest.yml` | yml | `kakuman-platform-v3.0` | — | — | — | — |
| `.github/workflows/observe.yml` | yml | `kakuman-platform-v3.0` | — | — | — | — |
| `.github/workflows/rls-drift.yml` | yml | `kakuman-platform-v3.0` | — | — | — | — |

## 記入要領

- **事故の日付**: その機構を生んだ出来事の日付（`2026-06-11` 等）。無いなら `事故なし` と書く
- **それが解いた問題**: 1 文。何が壊れて、この機構が何を止めたか
- **固有依存**: 配布先固有の前提（DB / 特定 SaaS / 業務語彙）の有無。`なし` / 具体名
- **採否**: `採択` / `却下` / `保留` のいずれか。それ以外は未記入として計数される

> 採択したものは DH 語彙へ移植する。**移すのは形式だけで、配布先固有の内容は持ち込まない**
> （「agent 本体はプロジェクト不変・差異は入力データに閉じる」の逆流への適用）。

---

生成: `scripts/upstream-scan.py` ／ 判定根拠: Council `council-2026-08-26T01:53:40Z-v7ord1`
