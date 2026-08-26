# UPSTREAM 採否 決定シート — kakuman-platform-v3.0

> `UPSTREAM-CANDIDATES-2026-08-26.md`（機械出力・存在差分 26 件）から、**診断書が特定した 7 機構だけ**を
> 抜き出し、事故の日付と解いた問題を一次ソースから埋めて推奨順に並べたもの。
>
> **人間が答えるのは 1 問だけ**: 「上から何件採るか」。
> 残りは自動で `保留` 扱いになり、次サイクルに持ち越す。
>
> 事故の日付・解いた問題は kakuman のソースコメントおよび `delivery/` 文書からの**転記**であり、
> AI の推定を含まない（U-5: 還流するのは機構ではなく、それを必要とした出来事）。

## 推奨カットライン: **上から 4 件**

1〜2 は Phase 2/3 のスコープを直接確定させる。3〜4 は Phase 4（観測層）と Phase 5（自動発見）の前提。
5〜7 は効果は実在するが、現サイクルの律速（人間レビュー枠）を圧迫する割に急がない。

---

## 順位表

### 1. 領域ゲートの述語化 — `check-routing-gates.mjs`

| 項目 | 内容 |
|---|---|
| **事故の日付** | 2026-08-05（`G-FEED` が `feedback` に誤反応。コメント曰く「初の実地 false positive」） |
| **解いた問題** | 変更 path が規範の該当領域なのに「通過ゲート記録」が無い献上を機械検出できなかった |
| **DH での価値** | **F-01 の直接解**。`GRAPH.yml` の edge に `predicate` を与える設計原型。機械検出できない 2 gate を空配列で**明示宣言**する形が、v7 構想の `unmechanizable` そのもの |
| **固有依存** | なし（移すのは形式のみ。`GATE_PATTERNS` の中身は kakuman 業務語彙なので持ち込まない） |
| **注記** | コメントに残る「依存追加のたびに常時発火して gate が形骸化する」は、DH のどの規範にも無い知恵 |

### 2. 規範の分割不変条件 — `check-traps-sync.mjs`

| 項目 | 内容 |
|---|---|
| **事故の日付** | 2026-08-05（cycle X-L0-CLAUDE-SLIM → 統括者モデル第 1 段） |
| **解いた問題** | 罠が「常時索引」と「ルーティング表」の**二重被覆**または**どちらにも無い宙吊り**になり、降格漏れが drift として蓄積した |
| **DH での価値** | **F-02 の直接解**。`常時 ∩ ルーティング = ∅` かつ `∪ = 全体` を `g5_false_positives`（無期限・無署名・無限成長）の置換に使う。「除外」という概念自体を消せる |
| **固有依存** | なし |
| **注記** | **1 に依存する**。Council `amrace` の開発者軸が実測で確認 — 分割不変条件は母集合が機械定義できることが前提で、述語化前に FAIL 昇格すると DH 自身の CI が止まる |

### 3. 観測層の非ゲート化 — `observe.yml`（罠 X-CI-A / X-CI-B）

| 項目 | 内容 |
|---|---|
| **事故の日付** | 2026-06（罠 X-CI-A: 課金ブロックで全 run fail → PR コメント汚染 → **Actions 無効化に至った**）／機構新設は 2026-08-20 |
| **解いた問題** | 観測層が赤や bot コメントを出すと、それ自体が購読セッションの wake event になり**自律実行を食い潰す** |
| **DH での価値** | **F-08 の直接解**。DH に観測層が無い。かつ F-03（自動発見）を入れる**前**にこれが要る — 観測層なき発見は wake event を量産する |
| **固有依存** | なし（Vercel build を「床」とする 3 層モデルのうち、床の実体だけがプロジェクト固有） |

### 4. 配置と武装の分離 — `observe.yml` の `schedule:` コメントアウト運用

| 項目 | 内容 |
|---|---|
| **事故の日付** | 事故なし（2026-08-20 の設計判断。「Actions の消費枠に直結する判断は人間側に残す」） |
| **解いた問題** | AI が cron を有効化すると消費枠の意思決定が AI 側に移ってしまう |
| **DH での価値** | **F-03 を安全に着地させる唯一の形**。`discover.yml` を `schedule:` 無効で出荷し、武装は人間が行う。philosophy 第 6 条を崩さずに「発見」を自動化できる |
| **固有依存** | なし |

---

### 5. 武装解除の明示 fail — `rls-drift.yml`

| 項目 | 内容 |
|---|---|
| **事故の日付** | **2026-06-11**（本番 RLS ドリフト。24 テーブルで RLS 無効。migration 外の手動 DDL 由来で `schema_migrations` に痕跡が残らず、静的 lint では原理的に検出不能） |
| **解いた問題** | secret 不在でセンサーが武装解除されたまま、静かに green を装う |
| **DH での価値** | 規範として立てる価値はある。ただし **`upstream-scan.py` に自己適用済み**（配布先不在・manifest 不読・`gate≠human` で `exit 1`）なので、追加で得るのは「規範化」の分だけ |
| **固有依存** | 検出器本体は Supabase Management API 依存。**移すのは規律のみ** |

### 6. 購読量の CI 強制 — `check-spec-size.mjs` / `check-claude-md-size.mjs`

| 項目 | 内容 |
|---|---|
| **事故の日付** | 2026-08-20（`docs/SCALE-ASSESSMENT-2026-08-20.html` §R1。CLAUDE.md 25KB には size センサーがあるのに、**その 40 倍の SPEC.md 1.02MB には同等の機構が無かった**） |
| **解いた問題** | 購読量の上限が convention 止まりで、実際の肥大を機械が止められない |
| **DH での価値** | DH の代謝機構（HOT/WARM/COLD）は自認どおり「convention レベル・glob 強制ではない」。これを `exit 1` に変えられる |
| **固有依存** | なし（閾値はプロジェクト固有だが機構は不変） |
| **注記** | `check-claude-md-size` のコメント「byte 値は規範でなく**配置違反の代理指標**。対処は量を削るでなく配置を直す」は、DH の純化 RL 由来の概念が現地で実装された形 = **既に一度 DH → kakuman を下った思想の、実装だけの還流** |

### 7. 不可逆操作の deny 強制 — `.claude/settings.json`

| 項目 | 内容 |
|---|---|
| **事故の日付** | 事故なし（`rm -rf` / `db reset` / `push --force` / `git clean` 等 14 件を予防的に deny） |
| **解いた問題** | philosophy 第 9 条 L-GATE（不可逆操作は事前ゲート）が宣言だけで機械強制されていない |
| **DH での価値** | **F-04 の一部**。DH 本体には `.claude/settings.json` が存在しない。宣言した委譲レベルを自分に適用していない状態 |
| **固有依存** | Supabase コマンドは kakuman 固有。**汎用分（git / rm / gh）のみ移す** |

---

## 記入欄（人間）

```
採用件数: 上から ____ 件      （推奨: 4）
```

記入後、`scripts/upstream-scan.py --prev` で `UPSTREAM-CANDIDATES-2026-08-26.md` の採否欄へ反映する。
採用分が Phase 2 / Phase 3 のスコープを確定させる（Council `council-2026-08-26T01:53:40Z-v7ord1` の完了条件）。

## 出典

| 機構 | 一次ソース |
|---|---|
| 1 | `scripts/check-routing-gates.mjs` L1-14, L22（G-FEED の false positive 注記） |
| 2 | `scripts/check-traps-sync.mjs` L2, L12-13 |
| 3 | `.github/workflows/observe.yml` L1-20（罠 X-CI-A / X-CI-B） |
| 4 | `.github/workflows/observe.yml` L17-20 |
| 5 | `scripts/check-prod-rls-drift.mjs` L1-6 ／ `.github/workflows/rls-drift.yml` L1-15 |
| 6 | `scripts/check-spec-size.mjs` L1-5 ／ `scripts/check-claude-md-size.mjs` L1-4 |
| 7 | `.claude/settings.json` permissions.deny ／ `CLAUDE.md` L50 |

いずれも `samejima-ai/kakuman-platform-v3.0` @ `9bbc642`。
