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

## 決定記録（2026-09-04 ひでさん回答）

| 問い | 決定 | 次に AI がすること |
|---|---|---|
| Q1 範囲 | A sensor + ci から（将来 5 種全部） | 棚卸しキット 0904 で段階 1 の初期集合を確定 |
| Q2 読み手 | A AI（CC）主。人間は明示指示時に HTML | 形式 = JSONL（OTel 最小形）+ 蒸留 md。人間向け UI は作らない |
| Q3 形 | C 物理集約のみ・台帳なし → **Council 諮問** `lg0903`: 推奨 D（物理集約 + `logs/index.yml` 1 枚に Q5〜7 の宣言を同一化）、jc 0.38 ゆえ人間判断へ | 残判断点 = 索引の性格を **Q3′** として同キットに追加 |
| Q4 生 / 蒸留 | A 二層・reindex-librarian 相乗り | `logs/raw/` のみ gitignore、蒸留は tracked |
| Q5 DH 上の位置 | A D2 テンプレ + 検査スクリプト、skill 無し。**開発ログとコードベースのログを明確に分ける** | `history/`（判断）と `logs/`（機械）の分離表を ANALYSIS メモに記載 |
| Q6 manifest | A merge 分類。「違和感あれば教えて」 | 違和感なし。パスだけ `logs/index.yml` に揃える（ANALYSIS メモ §Q6） |
| Q7 12-factor | A 逸脱明記 + store 列 | D2 テンプレ冒頭に逸脱理由 3 点 + 移行条件（L0 で起草） |
| Q8 メモ置き場 | B `delivery/ANALYSIS-*` に統一、kakuman も移す。矛盾に注意 | kakuman 側は skill 2 ファイル（AI 不可侵）の改訂が先。順序を ANALYSIS メモ §Q8 に記載。**本 cycle では移動していない** |
| Q9 VERSION drift | A 別 PR で先に | VERSION vs upgrade-spec の対応表を別 PR で献上（未着手） |
| Q10 次の一手 | A ブレスト継続、HTML で選択できるように | 棚卸しキット 0904 を公開: https://claude.ai/code/artifact/add88e1f-1f58-493a-b062-99523af63caa |

回答原文:

```
Q1 A（メモ: 将来的には5種全部を対象にしたい）/ Q2 A（メモ: あくまで開発のメインは AI。人間は明示的に指示をした時に HTML で読めるようにすればいいだけ）/ Q3 C（メモ: council にも問う）/ Q4 A / Q5 A（メモ: 重複してもいいけど、DH としての開発のログとアプリのログは明確に分けなくてはいけない）/ Q6 A（メモ: 正直よくわからんから何か違和感あったら教えて）/ Q7 A / Q8 B（メモ: カクマンプラットフォーム側のコードベースで矛盾が起こらないようにだけ気をつけて）/ Q9 A / Q10 A（メモ: 同様に HTML 化して選択できるように）
```
