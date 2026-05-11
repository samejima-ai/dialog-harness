# Wave 末振り返り儀式テンプレート

**規格根拠**: Council 諮問 `council-2026-05-11T09:00:00Z-w3qb04`（諮問省略、`confidence ≥ 0.7`）、Wave 3 Phase C で初配置。

## 用法

Wave 完遂時に `history/wave<N>/RITUAL-<YYYY-MM-DD>-wave<N>.md` として本テンプレートをコピー、各セクションを埋めて記録する。Wave 1 の `history/wave1/RITUAL-2026-05-11-metaskill.md` は本テンプレート不在の時期に個別形式で記録されたが、Wave 3 以降は本テンプレート準拠とする。

placeholder `<...>` を実際の値で置換。不要セクションは削除可（観測対象が存在しない場合）。

---

# Wave <N> 末振り返り儀式 — <YYYY-MM-DD>

**Wave**: <N>
**実施日**: <YYYY-MM-DD>
**起票元**: <PR #X (Wave N Phase C+D+E merged)>
**規格根拠**: `templates/rituals/wave-end-retrospective.template.md`（Wave 3 PR #81 で導入）

---

## 1. Wave 完遂事項

| Phase | PR | 主要成果 |
|---|---|---|
| Phase A | <PR#> | <内容> |
| Phase B | <PR#> | <Council 諮問 N 件採決> |
| Phase C | <PR#> | <SPEC 実装> |
| Phase D | レビュー | <verifier-philosophy / verifier-drift 抵触 0> |
| Phase E | merge | <v5.X.Y minor リリース> |

## 2. Council 諮問結果サマリ

| invocation_id | recommended | confidence | category | weights | conflict_type |
|---|---|---|---|---|---|
| `council-wNqb01` | <stance ID>: <概要> | <0.XX> | <conception/judgment/operation> | <X/Y/Z> | <tradeoff/simple_conflict> |
| `council-wNqb02` | ... | ... | ... | ... | ... |

### 収束パターン

- 全諮問の収束方向（B 系収束 / 接近採決 / 混在）
- Wave 1 / 2 / 3 / ... との比較

## 3. minority opinion 温存項目

| 諮問 | minority stance | 温存条件 | 再諮問予定 Wave |
|---|---|---|---|
| `council-wNqb01` | <stance>: <概要> | <データ駆動条件> | Wave <N+M> |

## 4. 観測項目（次 Wave 末で評価）

Wave 末で「実観測データに基づいて再判断」する項目を列挙:

- <観測項目 1>: <評価条件>
- <観測項目 2>: <評価条件>

## 5. 次 Wave 申し送り素材

次 Wave で着手すべき残候補・新規候補:

1. <候補 X>: <理由>
2. <minority opinion 再評価>: <Wave M で再諮問>
3. <ECC / 業界素材再観察>: <予約日>

## 6. philosophy 改訂記録（該当時のみ）

philosophy.md 改訂があった Wave のみ記入:

- 改訂条文: <第 N 条>
- Council 採決: `council-wNqb-<...>`
- minority opinion 温存条件
- 関連 PR
- 詳細: `history/PHILOSOPHY-CHANGELOG.md` 参照

## 7. 哲学的注記

Wave <N> 全体を通じて観測された:
- 咀嚼プロトコル T1/T2/T3 の適用比率
- ガードレール語彙化の進捗
- 第 8 条 3 段階モデルの運用実績（Wave 3 以降）
- B 系収束 / 接近採決のパターン分析

## 8. 数値統計（任意）

| 指標 | Wave 1 | Wave 2 | Wave 3 | ... |
|---|---|---|---|---|
| Council 諮問数 | 3 | 3 | 3 | ... |
| 諮問省略数 | 1 | 1 | 1 | ... |
| `agreed_recommended` 率 | 100% | 100% | 100% | ... |
| 接近採決数 (confidence < 0.6) | 0 | 0 | 1 (w3qb01) | ... |
| philosophy 改訂数 | 0 | 0 | 1 (第 8 条) | ... |
| 観測ログ entry 数 | <件数> | <件数> | <件数> | ... |
| Council 経由率（第 8 条運用後） | — | — | <%> | ... |

---

**承認**: <人間レビュー者名 / 日付>
**次 Wave 着手予定**: <YYYY-MM-DD>
