# harness-verifier

DH 本体（D4: メタスキル層）の内部整合性を検査する独立機構。

**別名**: singularity（HANDOFF §4.1 の特異点メタファ。`PHILOSOPHY.md` 参照）

## 位置づけ

dialog-harness リポジトリは「ユーザーハーネスを生成するメタスキル」として 5 つの次元を持つ：

| 次元 | 名称 | 実体 |
|---|---|---|
| D1 | ソースコード | プロジェクトの実装ファイル群 |
| D2 | 開発環境 | 1 を成立させる足場（package.json / vite.config / sensors / SPEC.md 等） |
| D3 | 配布 skill | 利用者プロジェクトに配置される `.claude/skills/` インスタンス |
| **D4** | **マスタ skill（メタスキル）** | **`~/.claude/skills/layerN-*` + `crosscut-*` のマスタ定義** |
| D5 | Meta モニタリング層 | D4 を外側から監視する人間（自動化禁止） |

`harness-verifier/` は **D4 を検査する機構** として、DH 本体（D4 内部）に依存せず独立配置される。
D5（人間）が最外殻として `harness-verifier/` の出力を判定する。

## 5 検証項目

| # | 項目 | 内容 |
|---|---|---|
| 1 | frontmatter 整合性 | 全 SKILL.md の name / description 必須フィールドの linter 検査 |
| 2 | 参照 path 有効性 | references/ 内および skill 間相対パスの dead link 検出 |
| 3 | SK 間参照の健全性 | 関連スキル参照の未知 skill 参照および直接自己参照の検出 |
| 4 | 5 層構造保全 | `inferential-sensor-v2.md` 内の 5 層名と他 skill 引用の整合検査 |
| 5 | 用語辞書整合 | `glossary.yml` 定義語が DH 全 skill で正しく使われているか |

## 独立性原則

`harness-verifier/` は **DH 本体（D4）のいかなる skill にも依存しない**。
DH 本体側 skill（layerN-* / crosscut-*）の改修によって `harness-verifier/` の挙動が壊れることがあってはならない。
依存方向は一方向のみ：`harness-verifier/` → 読み取り → DH 本体。逆方向の依存は禁止。

## 実行

### 月次定期実行

GitHub Actions cron `0 0 1 * *`（毎月 1 日 00:00 UTC = 09:00 JST）で自動実行。
結果は `reports/YYYY-MM.md` に commit される。

### 手動実行

```
python harness-verifier/verify.py
```

スクリプトは Python 標準ライブラリのみで動作（外部依存なし）。

### push/PR トリガー

`.claude/skills/**` または `harness-verifier/**` への変更を含む push/PR で自動実行。

## FAIL 時の挙動

- GitHub Actions のジョブが失敗（メール通知）
- `reports/YYYY-MM.md` に検出内容が記録される
- D5（人間）が判断する。`harness-verifier/` 自身は何も決定しない

## 関連ドキュメント

- [PHILOSOPHY.md](PHILOSOPHY.md) — 規律の自己相似性、自己検証機構の存在論
- [BOUNDARY.md](BOUNDARY.md) — DH 本体と本機構の境界線
- [HUMAN-PROTOCOL.md](HUMAN-PROTOCOL.md) — 人間介在プロトコル
- [glossary.yml](glossary.yml) — 用語辞書

## バージョン

v0.1.0（dialog-harness v5.2.0 で導入）
