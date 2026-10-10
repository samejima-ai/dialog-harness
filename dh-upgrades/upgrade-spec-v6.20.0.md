# upgrade-spec v6.20.0 — 判断キット（decision-kit-html）の DH 配布への昇格

> **状態: 実装中（F1 済 / VERSION 6.20.0 への昇格は未実施）**。人間決定 2026-10-10（利用者発話「DH にも反映して」→
> 反映の形 3 択に「DH の配布スキルに昇格」と回答）。Council 諮問なし（配布物を増やすか否かは委任の範囲 = 人間の判断で、
> 技術の得失の比較を要する判断点が無い）。
>
> **起点**: kakuman-platform-v3.0 の project skill `decision-kit-html`（2026-09-02 初版。2026-10-10 に
> 判断キット改訂キット 1010 の回答で「答える人の認知負荷を下げる」を最上位に改訂 = samejima-ai/kakuman-platform-v3.0#1078）。
> DH 自身も判断キットを `delivery/decision-kits/` で使ってきた（0903 / 0904 / 0907。0911 は HTML のみ）が、生成器はリポジトリに無く
> kakuman の skill を借りていた。

## F1 decision-kit-html を owned_skills に加える（priority: standard）

### 現状（2026-10-10 実測）

- DH の `delivery/decision-kits/*.json` は 3 本。spec 形式は kakuman の skill に依存し、DH 内に生成器（`build_kit.py`・テンプレート）が無い
- 判断キットの規律（人に出す問いは 委任の範囲 / 好み / 現場の知識 の 3 種だけ・技術の比較は Council の判定を推奨に・
  回答まとめ = 貼り戻すと実行が走るプロンプト）は philosophy 第 6 条（人間最終承認）と `crosscut-council` の
  「final_decision は常に null」を、人に答えてもらう面として具体化したもの = プロジェクト不変の機構

### 是正

1. `.claude/skills/decision-kit-html/` を置く（SKILL.md + assets / references / scripts）。kakuman 版から
   プロジェクト固有の語（人名・固有の検査コマンド・デプロイ先・固有の仕様番号）を抜き、プロジェクト差異は spec と
   回答まとめの「実行の規則」に閉じる（agent 本体はプロジェクト不変）
2. `dh-manifest.yml` の `owned_skills` と `GRAPH.yml` の nodes に加える（検査 12 の三者突合）。
   起動経路 `decision-kit-html → crosscut-council`（技術の判断点を先に Council へ）を edges に宣言
3. `harness-verifier/fixtures/skill-triggers.yml` に正例 8・負例 8
4. description は v7.0.0 F3 の目安（≤ 300 字・何をするか / いつ使うか / 使わない境界）で書く（218 字）。
   トリガー語の列挙は SKILL.md §起動条件

### 受け入れ基準

- `verify.py --strict` 全 PASS（検査 7 G-5 の未宣言経路 0・検査 8 宣言の網羅）/ `scripts/test-*` PASS
- `build_kit.py assets/example-spec.json <out> --strict` が WARN 0

### 配布先への影響

- 配布先（例: kakuman）で同名の project skill を持つ場合、次回の DH 同期で **DH 所有へ移る**（`owned_skills` の dir 単位置換）。
  kakuman 側は frontmatter の `harness_origin: project → dh`、CLAUDE.md の Doc-ARC 表（dh 20 / project 6 → dh 21 / project 5）を
  同期 PR で改める（CLAUDE.md は L-GATE-HARNESS = 人間承認）。以後の改訂は DH 側で行う
- kakuman 版にあった運用規約（PR の Vercel 緑で AI マージ・history 3 本・COUNCIL-LOG の書式）は DH 版の SKILL.md には持たない
  （利用者プロジェクトの CLAUDE.md / REGIME が持つ）

### 規範メタデータ

`{ stage: 全段階, review_trigger: [model_generation, measured: 判断キットの回答で推奨が覆った率が 6 cycle 連続 0（= 人が読まずに承認している疑い）] }`
