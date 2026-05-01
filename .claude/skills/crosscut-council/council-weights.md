# Council Weights — 重み配分設定

この文書は Council の重み配分を人間が編集可能な形で保持する。
Orchestrator は本文書の fenced YAML ブロックのみを機械パースする。
Markdown 本文は人間向けの文脈説明であり、機械パースしない。

## 編集プロトコル

- **更新タイミング**: 振り返り儀式 F1-F3（L0 対話）で人間承認を経て更新
- **更新者**: L0 が対話で抽出・提案 → 人間承認 → L0 が本ファイルを書き換える
- **実装者による直接編集は禁止**: 本ファイルの変更は重み配分の変更であり、開発者の思想・熱量を反映する判断。L0 経由でのみ更新する
- **変更履歴**: 履歴層（LC ≥ 1）では `history/CHANGELOG.md` に記録する

## 重みの計算式

```
final_weight[persona] = base_weight[persona] × ethos_multiplier
                      + situational_modifier[category][persona]
```

Orchestrator が決定論で計算する（詳細: `references/orchestrator.md`）。

## base_weights（土台重み）

開発者の思想・熱量を反映する。各 Council で合計が 10 になるように配分する。

```yaml
base_weights:
  business:
    経営者: 3
    開発者: 4
    哲学者: 3
  life:
    男: 3
    父: 3
    開発者: 4  # PR3 で有効化
```

## ethos_multiplier（熱量係数）

各 Persona の熱量・コミット度合い。デフォルトは 1.0（標準）。
プロジェクト特性に応じて L0 対話で調整する。

```yaml
ethos_multiplier:
  business:
    経営者: 1.0
    開発者: 1.0
    哲学者: 1.0
```

## situational_modifier（状況補正）

カテゴリ別の重み補正。発動元スキルが `category` として指定した値で引く。
合計は 0（ニュートラル補正）。特定カテゴリで特定視点を強化する時に正値、弱める時に負値。

デフォルト値はブリーフ §7.3 の推奨配分。

```yaml
situational_modifier:
  implementation:   # 実装判断
    経営者: -1
    開発者: +2
    哲学者: -1
  operation:        # 運用判断
    経営者: +1
    開発者: 0
    哲学者: -1
  maintenance:      # 保守判断
    経営者: 0
    開発者: +1
    哲学者: -1
  issue_triage:     # 問題分類
    経営者: +2
    開発者: 0
    哲学者: -2
  error_handling:   # エラー対応
    経営者: -2
    開発者: +3
    哲学者: -1
  judgment:         # 判断一般
    経営者: +1
    開発者: 0
    哲学者: 0
  conception:       # 構想・新規
    経営者: 0
    開発者: -1
    哲学者: +2
```

## 計算例

`category = implementation`、business Council の場合：

```
final_weight[経営者] = 3 × 1.0 + (-1) = 2
final_weight[開発者] = 4 × 1.0 + 2   = 6
final_weight[哲学者] = 3 × 1.0 + (-1) = 2
```

（ブリーフ §7.3 の implementation 配分 `経営者 2, 開発者 6, 哲学者 2` と一致）

## 未指定カテゴリの扱い

category が上記マップに存在しない場合、Orchestrator は `judgment`（判断一般）を適用する。
COUNCIL-LOG に `category_fallback: true` を記録し、F1 で棚卸しする。

## PR1 における制限

- life Council の値は保持するが使用しない（PR3 で有効化）
- ethos_multiplier は 1.0 固定（PR3 で L0 対話連携）
- situational_modifier の動的カスタマイズは PR3 で実装
