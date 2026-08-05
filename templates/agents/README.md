# templates/agents/ — ローカル開発用 leaf worker 雛形

ローカル Claude Code 開発セッションで、モデル使い分け基準
（`../../.claude/skills/layer0-spec-architect/references/model-recommendations.md`
§ローカル Claude Code（サブスクリプション）運用）を**機械的に効かせる**ための
subagent 定義雛形。

## なぜ必要か（配線の原理）

基準ドキュメントだけでは使い分けは適用されない。subagent のモデル解決順は

```
CLAUDE_CODE_SUBAGENT_MODEL 環境変数 → Task 起動時の model パラメータ
→ agent 定義 frontmatter の model → inherit（= メインセッションのモデル）
```

であり、**frontmatter に `model:` が無い限り、委譲されてもメインのモデル
（例: Opus 5）のまま実行される**。本雛形は frontmatter に `claude-haiku-4-5` を
固定することで、宣言でなく定義として基準を適用する（決定論優先、philosophy 第 2 条）。

## 同梱雛形

| ファイル | 役割 | モデル |
|---|---|---|
| `explore-worker.md` | コードベース探索・検索・多ファイル読みのファンアウト。結論（パス:行 + 要約）だけ返す | Haiku 4.5 固定 |
| `digest-worker.md` | 分類・抽出・整形・要約（入力→構造化出力の 1 ホップ変換） | Haiku 4.5 固定 |

## 導入方法

```sh
mkdir -p .claude/agents
cp templates/agents/explore-worker.md templates/agents/digest-worker.md .claude/agents/
```

L0（spec-architect）scaffold 時は M1 以上の全モードで配布を推奨（コスト中立・枠消費削減のみ）。
採用後は当該プロジェクトの所有物（`templates/` の一般規約どおり。雛形本体の改修は L0 案件）。

## CLAUDE.md ルーティング行（補助・任意）

frontmatter 配線だけでも委譲時には効くが、**委譲判断そのもの**を促すには
CLAUDE.md のルーティング表に 1 行置く:

```
| 探索・検索・分類・整形など単発の leaf 作業 | explore-worker / digest-worker へ Task 委譲（Haiku 固定）。実装・設計判断は委譲しない | G-xx |
```

## 注意

- **長い多段エージェントループに Haiku worker を使わない**（単発〜数ホップ限定。
  Terminal-Bench 系ベンチで Haiku は長ループが苦手）。実装・生成系の委譲は
  `inherit` のまま（メイン水準を維持）にする
- モデル ID はフル ID（`claude-haiku-4-5`）で固定する（エイリアス解決の
  CLI バージョン差を回避）。世代更新時は model-recommendations.md の改訂に追従して
  本雛形の `model:` を更新する
