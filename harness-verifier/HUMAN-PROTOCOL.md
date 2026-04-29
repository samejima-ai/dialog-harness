# HUMAN-PROTOCOL — 人間介在プロトコル

D5（人間）が本機構の検出結果を判定する運用手順。
本機構は判断せず、検出のみを D5 に献上する（`philosophy.md` 第 5 条 献上哲学）。

---

## 1. 月次定期実行

| 項目 | 値 |
|---|---|
| トリガー | GitHub Actions cron `0 0 1 * *`（毎月 1 日 00:00 UTC = 09:00 JST） |
| ワークフロー | `.github/workflows/harness-verify.yml` |
| 実行内容 | `python harness-verifier/verify.py` |
| 出力 | `harness-verifier/reports/YYYY-MM.md` を自動 commit |

加えて push/PR トリガー：
- `.claude/skills/**` への変更を含む push
- `harness-verifier/**` への変更を含む push
- master / main へ向かう PR

push/PR トリガー時は report ファイルは生成せず、PR / commit のチェックステータスとしてのみ結果を返す（report は月次のみ git に積層）。

---

## 2. レポートフォーマット

`reports/YYYY-MM.md` は以下の構造を持つ：

```markdown
# harness-verifier report YYYY-MM

- 実行日時: ISO 8601
- 実行コミット: <SHA>
- AI 能力バージョン: claude-opus-4-7（参考、本機構自身は LLM 非使用）
- 総合判定: PASS | FAIL

## 検査項目別結果

### 1. frontmatter 整合性
- 結果: PASS | FAIL
- 検出件数: N
- 詳細:
  - <skill-path>: <issue 内容>

### 2. 参照 path 有効性
（同形式）

### 3. SK 間依存グラフ循環
（同形式）

### 4. 5 層構造保全
（同形式）

### 5. 用語辞書整合
（同形式）

## D5 判定欄（人間記入）

- 判定日: YYYY-MM-DD
- 判定者: <name>
- 判断:
  - 承認: 全 PASS、改修不要
  - 修正指示: 個別検出項目への対応指示
  - Council 招集: 思想的整合への影響あり、`crosscut-council` 起動
- 補足:
```

D5 判定欄は **人間が後追記** する。本機構自身は記入しない。

---

## 3. D5 の判断カテゴリ

人間が取り得る判断は 4 種類：

| カテゴリ | 条件 | 行動 |
|---|---|---|
| 承認 | 全 PASS | レポートに「承認」を記入、commit |
| 軽微修正 | 単項目の表記揺れ・dead link 等 | 該当 skill を直接修正、レポートに修正 commit を参照 |
| 重要修正 | 構造的不整合（依存循環・5 層構造矛盾等） | L0 を起動して仕様策定からやり直し |
| Council 招集 | 思想的影響あり、複数案拮抗、major 級含意 | `crosscut-council` を起動、結果を本機構の改訂判断に反映 |

---

## 4. エスカレーションパス

```
[本機構が FAIL 検出]
    ↓
[GitHub Actions ジョブ失敗通知（メール）]
    ↓
[D5（人間）が reports/YYYY-MM.md を確認]
    ↓
判断分岐：
  - 承認 → 何もしない、次月へ
  - 軽微修正 → 直接修正
  - 重要修正 → L0 起動
  - Council 招集 → crosscut-council 起動
```

**エスカレーション中も本機構は停止しない**。
次月の cron が走り、修正反映後は PASS に戻る想定。
3 ヶ月連続で同じ FAIL が解消されない場合、PHILOSOPHY.md の改訂を D5 判断で検討する。

---

## 5. 「内部に閉じない」原則

本機構は **DH 本体内部だけで完結する自動修正回路を持たない**。
検出結果は必ず **D5（人間）の目を通す** ことで、外部に開かれた状態を保つ。

これは自己言及パラドックスの構造的回避（`PHILOSOPHY.md` §3）の運用版。

### 禁止事項

- 本機構が DH 本体 skill を自動修正してはならない
- 本機構が GitHub Issue / PR を自動作成してはならない（`crosscut-issue-dispatcher` の責務）
- 本機構が `crosscut-feedback-loop` を呼び出してはならない（依存方向逆流）

### 許容事項

- D5（人間）が本機構の検出結果を見て、手動で `crosscut-issue-dispatcher` / `crosscut-council` / L0 を起動する
- D5 が直接 DH 本体 skill を修正する
- D5 が本機構自身（`harness-verifier/` 配下）を修正する

---

## 6. 形骸化防止

本機構が形骸化（毎月 PASS で誰も読まない状態）を防ぐ仕組み：

### 6.1 連続 PASS 監視

12 ヶ月連続 PASS が続いた場合、D5 は以下のいずれかを実施する：

- 検証項目の追加検討（5 項目 → 6 項目以上、第 6 項目候補は「次元境界保全」）
- 検証粒度の精緻化（既存項目の検出深度を上げる）
- 用語辞書の拡充（`glossary.yml` のエントリ追加）

### 6.2 連続 FAIL 監視

3 ヶ月連続で同じ FAIL が解消されない場合、D5 は以下のいずれかを実施する：

- 該当検証項目のスコープ縮小（検出ロジックが過剰）
- DH 本体 skill の構造改修（FAIL の根本原因解消）
- PHILOSOPHY.md / BOUNDARY.md の改訂（責務再定義）

### 6.3 監査記録

D5 判定の履歴は `reports/YYYY-MM.md` に蓄積される。
12 ヶ月以上の蓄積後、年次振り返りで本機構自体の有効性を D5 が評価する。

---

## 7. 起動禁止条件

本機構の自動実行を **停止すべき** 状況：

| 状況 | 対応 |
|---|---|
| dialog-harness 自体の major 昇格中（v5.x → v6.0.0） | major 完了まで一時停止、D5 判断で再開 |
| philosophy.md の改訂中 | 改訂完了まで一時停止 |
| `harness-verifier/` 自身の改訂中 | 改訂 PR がマージされるまで一時停止 |

停止中は cron を skip するが、`reports/YYYY-MM.md` に「skipped: <理由>」を記録する。

---

## 8. v0.1.0 の制限

本機構の初版（dialog-harness v5.2.0 で導入）は以下を **未実装** とする：

- 検証項目の追加（v0.2.0 候補：「次元境界保全」）
- 推論的検証（v5.3.0 で `crosscut-verifier-philosophy` が担当）
- 自動レポート生成の精緻化（diff ベースの増分検出等）

これらは v0.2.0 以降で D5 判断により段階的に追加する。
