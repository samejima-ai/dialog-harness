# council-ctl — CTL 昇格ループのドライバ

「Council 発動 → **事後評価** → stats 再計算 → CTL 算出」を 1 本の CLI で回す道具。
CTL（Council Trust Level）は手で書き換える値ではなく、横断蓄積データから
決定論的に算出される。**CTL を上げる = この事後評価ループを回し続けること**
＝ Loop Engineering の Step 5「経験の還元」を回すこと。

## 記録経路（v6.1.0 — 単一情報源は COUNCIL-LOG）

CTL の記録（`invocations/`）は **`history/COUNCIL-LOG.md` を単一情報源として
`council-log-sync.py` が同期で導出する**。個別 `record` を毎回手で叩く手順書依存は
v6.1.0 で廃した（発火を強制する主体が無く空文化した — 発動 53 回に対し記録 1 件だった）。

```bash
# COUNCIL-LOG → council-data 同期 + 孤児掃除 + CTL 再計算（主経路）
python3 scripts/council-log-sync.py sync --prune --recompute

# 生成予定を確認するだけ（書かない）
python3 scripts/council-log-sync.py sync --dry-run
```

**発火主体**: L0 振り返り儀式（F1 ステップ 4）が同期の主たる発火点
（`layer0-spec-architect/references/ritual-protocol.md` §F1 / §F2.5）。儀式は
「同期 → `pending` 列挙 → 未評価を人間に問う」を 1 手順として固定する。儀式外で
手動同期したい時は上記コマンドを直接叩く。`record`（下記）は同期を待たず 1 件だけ
即記録したい場合の任意補助で、同期由来ファイルとは区別され上書きされない。

詳細な設計は `dh-upgrades/upgrade-spec-v6.1.0.md`。

- 一次情報源: `.claude/skills/crosscut-council/references/ctl-calculation.md` /
  `ctl-maturity-strategy.md`。`council-ctl.py` の `calculate_ctl()` は §3 の忠実実装。
- データは **user-scope（`~/.claude/council-data/`）に閉じる**（プライバシー配慮）。
  repo はツールのみ追跡し、データは追跡しない。
  テスト時は `COUNCIL_DATA_DIR` 環境変数で隔離先を上書きできる。

## 基本ループ

```bash
# 0) 初回だけ初期化（CTL-0 コールドスタート）
python3 scripts/council-ctl.py init

# 1) Council を発動したら記録する（count の素）
#    --topic / --judgment は抽象要約のみ（固有名・コード断片・人物名を入れない）
python3 scripts/council-ctl.py record \
    --decision-category C2 \
    --topic "ライブラリ選定のトレードオフ" \
    --judgment "選択肢 A を推奨" \
    --confidence 0.85

# 2) ★律速段階★ 結論が出たら必ず事後評価する（agreement_rate の素）
python3 scripts/council-ctl.py pending                 # 未評価を一覧
python3 scripts/council-ctl.py evaluate <末尾6文字> --status agreed   # agreed|modified|rejected
#   └─ 評価のたびに stats.json を即再計算し CTL を表示

# 3) 今どこにいるか・次段階まで何が足りないか
python3 scripts/council-ctl.py status

# 4) REGIME.md に貼る CTL ブロックを出力
python3 scripts/council-ctl.py regime-block
```

## なぜ「事後評価」が肝なのか

`record` しただけでは CTL は **絶対に上がらない**。未評価の判定は `pending` に
溜まるだけで、`agreement_rate`（質シグナル）を一切作らないため統計に算入されない。
昇格は「量（件数）×質（一致率）」のハイブリッド条件で、質は事後評価でしか生まれない。
だから **発動より評価をサボらないこと** が CTL を上げる唯一の燃料になる。

| 昇格 | 量 | 質 |
|---|---|---|
| CTL-0 → 1 | 評価済み ≥ 10 | いずれか 1 カテゴリで count≥10 & rate≥0.90 |
| CTL-1 → 2 | ≥ 30 | 4 カテゴリ中 3 以上が count≥10 & rate≥0.90 |
| CTL-2 → 3 | ≥ 100 | 全カテゴリ count≥25 & rate≥0.95 |

`rejected` を積むと `rate` が下がり、上の質条件を割って **降格**する（CTL は即時退行）。
H カテゴリは CTL に関係なく常時人間献上のため、本ツールでは記録できない。

## decision_category

`C1`〜`C4` のみ（`H` は記録不可）。意味は `consensus-protocol.md` / philosophy.md 第 6 条参照。

## テスト

```bash
bash scripts/test-council-ctl.sh   # 隔離 dir で CTL-0→1→2→3 と降格まで end-to-end 検証
```
