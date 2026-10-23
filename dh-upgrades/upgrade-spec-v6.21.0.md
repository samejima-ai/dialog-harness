# upgrade-spec v6.21.0 — 判断キット（decision-kit-html）を v2（1 項目ずつめくる型）に替える

> **状態: 実装中（F1 済 = 本 PR で skill を差し替え）**。VERSION 6.21.0 への昇格は `dev-env-spec.md` §昇格の実行 に従い人間判定で別に行う。
> 人間決定 2026-10-23（kakuman-platform の認識合わせキット kit-format-1023 の回答 K6 = B「人が共通のスキルを先に変える」+
> 利用者発話「スキルを更新して」）。Council 諮問なし（型の好みと配布の範囲 = 人間の判断で、技術の得失の比較を要する判断点が無い）。
>
> **起点**: samejima-ai/kakuman-platform-v3.0#1457（`docs/decision-kit-v2/` = 入れ替える中身一式 + 提案文）。

## 決まったこと（kit-format-1023 の回答）

| 項目 | 決定 |
|---|---|
| K1 受け取り方 | 原図 ＞ モック ＞ 挿絵 ＞ 表・グラフ。できる限り視覚的に |
| K2 並べ方 | **1 項目ずつめくる**（1 つずつ集中して理解 → 判断を素早く） |
| K3 項目の中 | 左に絵・右に文字（スマホは縦）。複雑な項目は「解説」と「選ぶ」に分けて札を付ける |
| K4 絵 | 1 項目に必ず 1 枚 |
| K5 文字 | 欄ごとの上限 + 細かい事実は「▸ 詳しく」に畳む |
| K6 置く所 | 人（の指示）で共通のスキルを先に変える = 本 spec |
| K7 今までの型 | 次から新しい型だけ（v1 の生成器は外す） |

## F1 decision-kit-html を v2 に差し替える（priority: standard）

### 是正

1. `SKILL.md` を v2 に置き換える。description は v7.0.0 F3 の目安（≤ 300 字）に収め、トリガー語は §起動条件 へ
2. 足す: `assets/template.html`（v2）・`assets/example-spec.json`（v2 の見本 7 項目）・`references/spec-schema.md`（v2）・
   `scripts/build_kit2.py`（絵の無い項目で止める・文字の上限を知らせる・`--images` で画像を公開版にだけ埋め込む）
3. 外す（K7）: `scripts/build_kit.py`・`scripts/visuals.py`・`scripts/add_decisions.py`・`scripts/inject_images.py`
   （`build_kit2.py --images` が代わる）・`references/visuals.md`・`references/design.md`。過去のキットを組み直すときは git の履歴から取る
4. `scripts/check_layout.js` は v2 に合わせて直して残す（PC 1440 / スマホ 390 × 明暗、全ページを「次へ」でめくって判定）
5. `harness-verifier/fixtures/skill-triggers.yml` の正例に v2 の起動語を 2 つ足す（解説も込で選ばせて / モックで認識合わせ）

### 受け入れ基準

- `verify.py --strict` 全 PASS / `scripts/test-*` PASS
- `build_kit2.py assets/example-spec.json <out> --images <仮の画像> --strict` が WARN 0
- `check_layout.js` が 1440 / 390 明 / 390 暗 の全ページで はみ出し 0・console error 0

### 配布先への影響

- 次回の DH 同期で、配布先の `.claude/skills/decision-kit-html/` は dir 単位で置き換わる（v1 の生成器は消える）。
  配布先の `delivery/` 等に v1 の spec が残っていても、組み直しは要らない（過去のキットは出来上がった HTML が正）
- kakuman の `docs/decision-kit-v2/` は同期後「DH 本体へ移した」と書いて残す（重複を作らない、提案文 §反映までの間）
- Claude.ai の Skills は人の作業（同じ中身の zip を上げ、今の `decision-kit-html` を置き換える。名前は同じ）

### 規範メタデータ

`{ stage: 全段階, review_trigger: [model_generation, measured: 判断キットの回答で推奨が覆った率が 6 cycle 連続 0（= 人が読まずに承認している疑い）] }`
