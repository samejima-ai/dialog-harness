# upgrade-spec v6.22.0 — 判断キットの出口を「全体の絵」に分け、実行後の報告を照合報告（shougou-houkoku）にし、前段の本質問答（honshitsu-mondou）を入れる

> **状態: 実装中（F1・F2・F3 済 = 本 PR で skill を差し替え / 新設）**。VERSION 6.22.0 への昇格は `dev-env-spec.md` §昇格の実行 に従い人間判定で別に行う。
> 人間決定 2026-11-18（利用者発話「判断キットや報告のスキルを更新、導入したい」+ 選択「claude.ai 側の版に揃える」「DH 配布で新設」）。
> Council 諮問なし（型の好みと配布の範囲 = 人間の判断で、技術の得失の比較を要する判断点が無い）。
>
> **起点**: 利用者の claude.ai 個人スキル `decision-kit-html`（v3 = 本質問答 kit-deguchi-1118 / zentai-e-kata-1118、v2.1・v2.2 = 2026-10-26）と
> `shougou-houkoku`（v1 = 本質問答 houkoku-1118）。DH の v2（v6.21.0）より先に進んでいたので、DH を正本に戻す。

## 決まったこと

| 項目 | 決定 |
|---|---|
| 判断キットの出口 | 回答が返ったらすぐ実行しない。答えを全部合わせた「全体の絵」を見せ、「これで実行／ここを詰める」の 1 問で 2 本に分ける（揃えてから任せる） |
| 全体の絵の型 | 成果物の種類でなく判断対象（見せ方 / 数と段取り / 仕組み）で構図を選ぶ。前の版があれば前 → 今を並べる |
| 感覚の問い | `feel: true` の問いは未回答を推奨で進めず、全体の絵で印を付ける |
| 絵の種類 | 現物 ＞ 様式 ＞ モック ＞ 挿絵 ＞ 表・グラフ。確認の項目は `target`（exists = 現物 / new = 様式）。`file` で xlsx・docx・pptx・pdf・画像を PNG に |
| キットの置き場 | 案件ごとのキット用 1 本に上書きする（数を増やさない）。残すのは決定記録だけ |
| 報告 | HTML の報告書（Artifact）をやめ、照合報告 = 約束（全体の絵）と出来た物を本文の一枚で並べ、違いに印・聞くのは「直す物はどれか」だけ |

## F1 decision-kit-html を v3 にする（priority: standard）

### 是正

1. `SKILL.md` を v3 に置き換える（description ≤ 300 字、トリガー語は §起動条件）。v3 の本文は claude.ai 版と同じ。DH 版の違いは
   frontmatter（`target_os` / `dimension`）・§起動条件・`check_layout.js` の手順と参照・固有名（人名・提出先）を一般名に、の 4 点。加えて、feel が無くても推奨と食い違うメモがあれば全体の絵を出す（claude.ai 版の穴を埋めた）・見本 spec のまとめを v3 の形に・render_visual.py は Linux / macOS 向けと明記
2. `assets/template.html`・`assets/example-spec.json`・`scripts/build_kit2.py` を claude.ai 版に揃える（`target` / `template` / `file` / `focus` / `box` / `whole` の点検）
3. 足す: `scripts/render_visual.py`（xlsx・docx・pptx・pdf・画像 → PNG。LibreOffice → pdftoppm）
4. `references/spec-schema.md` を揃え、claude.ai 版で崩れていた `phases` の注釈を直し、`feel` を載せる（組み立ては読まない）
5. `scripts/check_layout.js` は残す（claude.ai 版には無い。node が無い環境では目で見る）
6. `harness-verifier/fixtures/skill-triggers.yml` の正例に 1 つ足す（全体の絵を見てから任せたい）

## F2 shougou-houkoku を新設する（priority: standard）

### 是正

1. `.claude/skills/shougou-houkoku/SKILL.md` を足す（claude.ai 版 v1 を DH の frontmatter に。固有のスキル名〔現場の報告書・日報など〕は「各プロジェクトの文書スキル」に一般化）
2. `dh-manifest.yml` の overwrite 一覧・`GRAPH.yml`（node + decision-kit-html → shougou-houkoku の 1 辺。直す物の次の周は人の「直す」を通るので戻り辺は置かない = G-4）に載せる
3. `harness-verifier/fixtures/skill-triggers.yml` に正例 5・負例 5

## F3 honshitsu-mondou を新設する（priority: standard）

> 人間決定 2026-11-18 追加（利用者発話「本質問答のスキルも DH に入れて」）。起点 = claude.ai の個人スキル honshitsu-mondou。

### 是正

1. `.claude/skills/honshitsu-mondou/SKILL.md` を足す（DH の frontmatter・§起動条件。「この相手について」は既定に、個人の決まり〔AI を使う案を出さない〕は
   「相手が使うと言っていない手段を勧めない」に一般化、渡し先の個人スキル〔要件定義・モック〕は layer0-spec-architect に）
2. `dh-manifest.yml`・`GRAPH.yml`（node + 本質問答 → layer0-spec-architect / decision-kit-html の 2 辺）・`skill-triggers.yml`（正例 5・負例 5）

### 受け入れ基準（F1・F2・F3 共通）

- `verify.py --strict` 全 PASS / `scripts/test-*` PASS
- `build_kit2.py assets/example-spec.json <out> --images <仮の画像> --strict` が WARN 0
- `check_layout.js` が 1440 / 390 明 / 390 暗 の全ページで はみ出し 0

### 配布先への影響

- 次回の DH 同期で、配布先の `.claude/skills/decision-kit-html/` は dir 単位で置き換わり、`shougou-houkoku/` が増える
- 配布先の運用ルールに「最後に HTML の報告書を Artifact で」と書いてある所は、照合報告に直す（配布先の作業）
- Claude.ai の Skills は人の作業（DH 版と同じ中身の zip を上げ直すかは任意。名前は同じ）

### 規範メタデータ

`{ stage: 全段階, review_trigger: [model_generation, measured: 照合報告で「直す候補」が 3 cycle 連続 0 なのに後から直しが入った（= 違いの見立てが甘い疑い）] }`
