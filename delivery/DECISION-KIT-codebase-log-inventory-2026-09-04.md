# ログ棚卸しキット 0904 — 3 リポの記録 22 種 + 欠落 1 の A/B/C（Markdown 正本）

> HTML 視覚版（A/B/C + 回答まとめコピー）: https://claude.ai/code/artifact/add88e1f-1f58-493a-b062-99523af63caa
> spec: `delivery/decision-kits/2026-09-04-codebase-log-inventory.json`
> 起点: ログ層キット 0903 Q10-A「台帳初版（3 リポ分）を調査で埋めてから判断する」+ メモ「同様に HTML 化して選択できるように」
> 局面: L0 前ブレスト（未確定・cycle ではない）。推奨は AI の見立てであって決定ではない。

## 問いの形

1 行 = 1 記録 = 1 問。A = 段階 1 で対象（最初に「場所」へ載せる）/ B = 後段で対象（5 種全部に広げるとき）/ C = 対象外（ログではない / 正が別にある / 動かさない）。
推奨の規則: sensor・ci = A ／ runtime・audit・蒸留物 = B ／ 正が別にある・ログでない = C。

## 一覧（推奨つき）

| Q | 保管先 | 記録 | 発生源 | 種別 | PII | 推奨 |
|---|---|---|---|---|---|---|
| Q0 | 欠落 | 決定論センサーの出力（check-* / lint-* / verify） | kakuman 16 本 / cc-cockpit / DH | sensor | none | A |
| Q1 | SaaS | Sentry | kakuman | runtime | pseudonymous | B |
| Q2 | SaaS | Vercel ログ | kakuman | runtime | unknown | B |
| Q3 | SaaS | GitHub Actions ログ | 3 リポ | ci | none | A |
| Q4 | DB | samejima_activity_log | kakuman public | audit | pseudonymous | B |
| Q5 | DB | underlay_usage_events / _sessions | kakuman ops | runtime | 本体 none / 対応表 personal | B |
| Q6 | DB | freee-monitor sync ログ | kakuman | runtime | unknown | B |
| Q7 | DB | expense_ocr_metrics | kakuman | runtime | none | B |
| Q8 | DB | cc-cockpit SQLite | cc-cockpit | runtime + ai-session | none | C（transcript の派生） |
| Q9 | gitignore | *.log | kakuman | runtime / tooling | unknown | B |
| Q10 | gitignore | harness-verifier/reports/（丸ごと） | kakuman | sensor | none | A |
| Q11 | gitignore | *.log | cc-cockpit | runtime / tooling | unknown | B |
| Q12 | gitignore | coverage/ | cc-cockpit | sensor | none | A |
| Q13 | gitignore | playwright-report/ + test-results/ | cc-cockpit | sensor | none | A |
| Q14 | gitignore | .cc-cockpit/（セッション報告） | cc-cockpit | 成果物 | unknown | C（ログでない） |
| Q15 | gitignore | hook-observations.jsonl | DH（kakuman 同名） | ai-session | none | B |
| Q16 | committed | PERF_AUDIT.md | kakuman | sensor（手動） | none | B |
| Q17 | committed | docs/PROJECT-*ASSESSMENT*.html | kakuman | 評価文書 | none | C（成果物） |
| Q18 | committed | harness-verifier/reports/YYYY-MM.md | DH | sensor（月次蒸留） | none | B |
| Q19 | committed | delivery/ANALYSIS-* | DH | sensor + 分析 | none | B |
| Q20 | home | ~/.claude/projects/**/*.jsonl | 3 リポ共通 | ai-session | personal | C（読み取り専用・C11） |
| Q21 | home | subagents/agent-*.jsonl | 3 リポ共通 | ai-session | personal | C |
| Q22 | home | ~/.claude/council-data/invocations/*.json | user-scope | audit | none | C（COUNCIL-LOG の派生） |

推奨内訳: A 5 / B 12 / C 6。

## 未確認（判断に影響しない）

- Q6 freee-monitor sync ログの表名（SPEC FX-SAMEJIMA §F の言及のみ）
- Q9 / Q11 の `*.log` の書き手

## 決定記録

（回答が返ったら「Q / 決定 / 段階 1 の初期集合」をここに追記し、ANALYSIS メモ §ブレスト決定 にも写す）
