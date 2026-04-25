# CTL（Council Trust Level）算出規格

Council の信頼度を横断蓄積データから決定論的に算出する規格。
L0 spec-architect が REGIME.md 生成・更新時に呼び出す。

CTL の意図と人間 ≒ Council 原則は philosophy.md 第 6 条を参照。

## 1. 算出の入力

- `~/.claude/council-data/stats.json`: カテゴリ別累積実績
- `~/.claude/council-data/invocations/`: 個別判定ログ（時系列）
- `~/.claude/council-data/version.md`: Council data バージョン

ファイル不存在の場合は CTL-0 で初期化（コールドスタート）。

## 2. stats.json のスキーマ

```json
{
  "version": "0.1",
  "last_updated": "2026-04-25T10:30:00Z",
  "categories": {
    "C1": {
      "count": 45,
      "agreed": 41,
      "modified": 4,
      "agreement_rate": 0.9111
    },
    "C2": {
      "count": 23,
      "agreed": 20,
      "modified": 3,
      "agreement_rate": 0.8696
    },
    "C3": {
      "count": 12,
      "agreed": 11,
      "modified": 1,
      "agreement_rate": 0.9167
    },
    "C4": {
      "count": 34,
      "agreed": 31,
      "modified": 3,
      "agreement_rate": 0.9118
    }
  },
  "total_invocations": 114,
  "total_agreed": 103,
  "overall_agreement_rate": 0.9035
}
```

`categories` キーは `decision_category`（philosophy.md 第 6 条 / `consensus-protocol.md`
の引数定義）。重み配分用の既存 `category`（operation/judgment/conception 等）は
ここには含まれない（CTL 統計はあくまで H/C 軸の判断委譲精度を学習するためのもの）。

H カテゴリ（H1〜H4）は CTL に関わらず常に escalate_to_human のため、
`stats.json` には含めない（記録不要）。

## 3. CTL 判定ロジック

```python
def calculate_ctl(stats):
    """
    Args:
        stats: ~/.claude/council-data/stats.json をパースしたオブジェクト
               ファイル不存在時は {"total_invocations": 0, "categories": {}}

    Returns: "CTL-0" / "CTL-1" / "CTL-2" / "CTL-3"
    """
    total = stats.get("total_invocations", 0)
    categories = stats.get("categories", {})

    # CTL-0: コールドスタート
    if total == 0:
        return "CTL-0"

    # CTL-3: 高度委譲（最も厳しい条件）
    if total >= 100:
        all_categories_meet = all(
            cat.get("count", 0) >= 25 and cat.get("agreement_rate", 0) >= 0.95
            for cat in categories.values()
        )
        if all_categories_meet and len(categories) >= 4:
            return "CTL-3"

    # CTL-2: 標準運用
    if total >= 30:
        majority_meet = sum(
            1 for cat in categories.values()
            if cat.get("count", 0) >= 10 and cat.get("agreement_rate", 0) >= 0.90
        )
        if majority_meet >= 3:  # 4 カテゴリ中 3 以上が条件達成
            return "CTL-2"

    # CTL-1: 初期蓄積
    if total >= 10:
        any_meet = any(
            cat.get("count", 0) >= 10 and cat.get("agreement_rate", 0) >= 0.90
            for cat in categories.values()
        )
        if any_meet:
            return "CTL-1"

    # 上記いずれにも該当しない場合
    return "CTL-0"
```

`stats.get("categories", {})` でガードしているのは、stats.json が欠損・破損して
`categories` キーが無いケースでも安全にコールドスタート扱いに落とすため。

| CTL | 判定条件（要約） | 委譲範囲 |
|---|---|---|
| CTL-0 | total == 0、または上記条件いずれも未達 | C カテゴリも全件献上 |
| CTL-1 | total ≥ 10、いずれか 1 カテゴリで count ≥ 10 かつ agreement_rate ≥ 0.90 | 該当カテゴリのみ自律 |
| CTL-2 | total ≥ 30、4 カテゴリ中 3 以上で count ≥ 10 かつ agreement_rate ≥ 0.90 | 大半のカテゴリ自律 |
| CTL-3 | total ≥ 100、全カテゴリで count ≥ 25 かつ agreement_rate ≥ 0.95 | H 以外を全面自律 |

## 4. 個別判定ログ（invocations/）の構造

各 Council 発動を 1 ファイルとして記録する。

```
~/.claude/council-data/invocations/
├── 2026-04-25T10-30-00Z-abc123.json
├── 2026-04-25T11-15-00Z-def456.json
└── ...
```

ファイル名は `<ISO8601Z (コロン→ハイフン)>-<invocation_id 末尾 6 文字>.json` 形式。

各ファイルの内容:

```json
{
  "invocation_id": "council-2026-04-25T10:30:00Z-abc123",
  "council_type": "business",
  "category": "judgment",
  "decision_category": "C1",
  "topic_summary": "ライセンス選定のトレードオフ判断",
  "judgment": "選択肢 A を推奨",
  "judgment_confidence": 0.85,
  "consensus_mode": "auto_agree",
  "ctl_at_invocation": "CTL-2",
  "actual_outcome": {
    "status": "agreed",
    "evaluated_at": "2026-04-25T18:00:00Z",
    "modifier_note": null
  }
}
```

`category` は重み配分用、`decision_category` は判断委譲用（v4.2）。両者は直交。
詳細は `consensus-protocol.md` の「category と decision_category の役割分担」節を参照。

### プライバシー配慮

`invocations/` にはプロジェクト名・コード断片・人物名を直接記録しない。
`topic_summary` は抽象化された要約のみ（80 字以内推奨）。
`judgment` も結論を抽象表現にして、再現可能な判定識別性のみ保つ。

## 5. stats.json の更新トリガー

- **事後評価完了時**: 該当 invocation の `actual_outcome` を更新し、
  カテゴリ別の `count` / `agreed` / `modified` / `agreement_rate` を再計算する
- **古いデータの扱い**: `count` に上限を設けない。全件保持で長期学習を可能にする
  （プライバシー配慮で詳細は記録しないため、長期保持しても容量問題は発生しにくい）

## 6. CTL 再計算のタイミング

- L0 spec-architect 起動時（REGIME.md 生成・更新時）
- 事後評価完了直後（次プロジェクトに即反映）
- ユーザーが明示要求した時（「CTL を再計算して」）

## 7. CTL の REGIME.md 記録フォーマット

REGIME.md に以下のブロックを記録する:

```markdown
## Council Trust Level
- ctl: CTL-2
- ctl_calculated_at: 2026-04-25T10:30:00Z
- delegation_scope: [C1, C3, C4]   # 自律実行される decision_category
- escalation_categories: [C2]       # 献上される decision_category
- council_data_version: 0.1
```

`council_data_version` は `~/.claude/council-data/version.md` の `version` 値および
`stats.json` の `version` 値とリテラルが一致する（`v` 接頭辞は付けない）。

`delegation_scope` / `escalation_categories` は CTL-1 のカテゴリ別判定で
特に重要。CTL-2/CTL-3 では大半が自律になり、CTL-0 では空欄に近い。

## 8. user-scope の初期化ロジック

L0 spec-architect 起動時に以下を実施:

1. `~/.claude/council-data/` の存在確認
2. 不存在の場合は新規作成
   - `stats.json`: 空のテンプレートを生成（`categories` は空オブジェクト、`total_invocations: 0`）
   - `invocations/`: 空ディレクトリ作成
   - `version.md`: 初期版を生成
3. CTL-0 で運用開始

`version.md` の初期版テンプレート:

```markdown
# Council Data Version

- version: 0.1
- created_at: <ISO 8601>
- last_updated: <ISO 8601>
- harness_version_at_creation: v4.2
- total_projects: 0
- notes: |
  Council Trust Level の横断蓄積データ。
  プロジェクト名・コード断片は記録しない（プライバシー配慮）。
```

## 9. 同期と引き継ぎ

- repo 側（github.com/samejima-ai/dialog-harness）の更新で `council-data/` に
  影響しない（user-scope に閉じる）
- ユーザーが PC を変更した場合、`council-data/` を手動コピーで引き継ぐ
- 自動同期は実装しない（プライバシー配慮）
