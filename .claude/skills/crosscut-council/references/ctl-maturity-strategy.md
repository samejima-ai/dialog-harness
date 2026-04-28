# CTL Maturity Strategy

CTL 昇格・降格のプロトコル。spec §4.4.2.2 を本体化。

## CTL 段階定義

| CTL | 委譲範囲 | 自律実行可能カテゴリ |
|---|---|---|
| CTL-0 | なし | 全件人間献上 |
| CTL-1 | C2（ライブラリ選定等） | 軽微判断のみ |
| CTL-2 | C2 + C4（曖昧性解消） | 大半の判断、不可逆操作は事前検証 |
| CTL-3 | C1-C4（不可逆 C3 含む） | 全件自律、事後献上のみ |

H カテゴリは CTL に関係なく常時人間献上。

## 昇格条件（量 + 質ハイブリッド）

CTL-N → CTL-(N+1) への昇格は**量・質両方の条件を満たす**こと。

### 量的条件

| 昇格 | 必要件数 |
|---|---|
| CTL-0 → CTL-1 | Council 判定 ≥ 10 件（プロジェクト内） |
| CTL-1 → CTL-2 | Council 判定 ≥ 30 件 |
| CTL-2 → CTL-3 | Council 判定 ≥ 100 件 |

### 質的条件

| 指標 | 閾値 |
|---|---|
| 一致率（Council 推奨 = 実装者採用 / 人間最終承認） | ≥ 0.85 |
| override 率（Council 推奨と異なる選択 / 全件） | ≤ 0.15 |
| reject 率（人間が Council 判断を否決した割合） | ≤ 0.05 |
| confidence 中央値 | ≥ 0.7 |

### 横断蓄積による補強（v4.2 で導入）

`~/.claude/council-data/stats.json` に**全プロジェクト横断の統計**を蓄積。
プロジェクト内件数が量的条件を満たさなくても、横断統計で同種カテゴリの実績が十分なら昇格判断材料に加える（プロジェクト内件数の 50% を補える上限）。

## 判定主体

CTL 昇格・降格判定は L0 spec-architect が振り返り儀式（F2 / F3）で実行する：

- F1（軽量）: 量的条件のみ自動チェック
- F2（標準）: 量 + 質の自動判定 + 人間確認
- F3（完全）: 上記 + 過去の judgment ログレビュー + ARCH-DECISIONS 記録

## 退行ロジック（CTL 降格）

以下のいずれかで CTL-N → CTL-(N-1) を発動：

| トリガー | 条件 |
|---|---|
| 連続 reject | 直近 5 件の Council 判断が連続して人間 reject |
| 重大インシデント | 不可逆操作で SPEC 違反、データ損失、ロールバック発生 |
| 一致率低下 | 直近 30 件の一致率が < 0.7 |
| 自動降格 trigger | `templates/.github/workflows/auto-degrade.yml` の発動条件と連動 |

降格は即時。記録は `history/REGIME-LOG.md` に minor 改修として残す。

## CHANGELOG への自動記録

CTL 変動は `history/CHANGELOG.md` にレベル B（確認推奨）で追記：

```markdown
### CTL 変動（YYYY-MM-DD）
- 旧: CTL-1
- 新: CTL-2
- 理由: 量条件 35 件達成、質条件すべて閾値超過（一致率 0.89, override 0.11, confidence 中央値 0.74）
- 主体: L0 振り返り儀式 F2
```

## 関連

- `ctl-calculation.md` — 重み計算ロジック（compute_consensus_mode）
- `consensus-protocol.md` — Council 判定の合意プロセス
- `../../layer0-spec-architect/references/regime-assessment.md` §dev_mode 判定 — CTL を REGIME.md に記録するフォーマット
- `../../layer0-spec-architect/references/ritual-protocol.md` — F1/F2/F3 振り返り儀式の実行プロトコル
