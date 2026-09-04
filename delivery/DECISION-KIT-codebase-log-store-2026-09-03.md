# ログ層キット 0903 — コードベース自身のログ置き場の判断キット（Markdown 正本）

> HTML 視覚版（○× + 回答まとめコピー）: https://claude.ai/code/artifact/1c3b9517-a83d-4d41-b38d-86c0869fab28
> spec: `delivery/decision-kits/2026-09-03-codebase-log-store.json`
> 上流のブレストメモ: `delivery/ANALYSIS-codebase-log-store-2026-09-03.md`（PR #238）
> 局面: L0 前ブレスト（未確定・cycle ではない）。推奨は AI の見立てであって決定ではない。

## 待ちの分類

| 主体 | 件数 | 内容 |
|---|---|---|
| 人間専管 | 10 問 | Q1〜Q10（本キット） |
| AI 単独可（回答後） | 2 | 台帳初版を 3 リポ分埋める調査 / VERSION drift の差分表 |
| 待機 | — | 回答が返るまで実装・規範改訂は行わない |

## 問い（全文は spec JSON）

| Q | 問い | 所要 | 選択肢 | 推奨 |
|---|---|---|---|---|
| Q1 | 「あらゆるログ」の範囲をどこから始めるか | 5 分 | A sensor+ci / B runtime+audit / C ai-session / D 全部 | A |
| Q2 | 主な読み手を誰にするか | 2 分 | A AI（CC）/ B 人間 / C 逆流機構 | A |
| Q3 | 「場所」を何で実現するか | 5 分 | A 台帳 / B 台帳+二層 / C 物理集約のみ / D DB 集約（×横断不可） | A |
| Q4 | 生ログと蒸留物をどう扱うか | 2 分 | A 二層・librarian 相乗り / B 二層・別 skill / C 生も commit / D 蒸留しない | A |
| Q5 | DH のどこに置くか | 5 分 | A D2 テンプレ logs.yml / B telemetry-reflux.yml 統合 / C 新 skill（D4） | A |
| Q6 | dh-manifest の boundary | 2 分 | A merge 分類に logs.yml / B never_touch 列挙 / C 触らない | A |
| Q7 | 12-factor からの逸脱 | 5 分 | A 明記 + 移行可能な store 列 / B 標準準拠（実体は外部） / C 明記しない | A |
| Q8 | ブレストメモの置き場 | 2 分 | A skill 既定 docs/brainstorm・DH 本体は delivery 例外 / B delivery 統一 / C docs/brainstorm 統一 | A |
| Q9 | VERSION drift を切り離すか | 2 分 | A 別 PR で先に / B 同梱 / C 放置 | A |
| Q10 | 次に何をするか | 2 分 | A ブレスト継続（台帳初版の調査） / B L0 へ上げる / C 止める | A |

## 事実の出所

- 保管先 5 種・記録 23 種: ANALYSIS メモ §F1（各リポの `.gitignore` / SPEC / `dh-manifest.yml` を 2026-09-03 に読んだ）
- 決定論センサー出力の未蓄積: kakuman `scripts/check-*` は stdout のみ、`harness-verifier/reports/` は gitignore
- 開発観測ログ（読み手 = CC）: kakuman SPEC FX-SAMEJIMA §F
- 2 表分離・90 日 purge・`ops` 隔離事故: kakuman SPEC F4-8 使用ログ U-1 / U-2 / U-11
- telemetry-reflux TR-1〜TR-4: `templates/rules/common/telemetry-reflux.rules.md`
- upstream U-5: `dh-manifest.yml`
- 12-factor Logs / OpenTelemetry LogRecord / Claude Code hooks・telemetry: ANALYSIS メモ §F5（URL 付き）
- VERSION drift: `VERSION` = 6.11.0（PR #186）vs `dh-upgrades/upgrade-spec-v6.15.0.md`

## 決定記録

（回答が返ったら「問い / 決定 / 次に AI がすること」の表をここに追記し、ANALYSIS メモ §ブレスト決定 にも写す）
