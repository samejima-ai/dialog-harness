# 履歴層スキーマ

1→5運用（同一プロダクトの反復開発）で必須となる `history/` ディレクトリの仕様。
L0対話・L1献上・独立検証の全てが参照する一次情報源。

---

## 配置

プロジェクトルート直下。`sensors/` と同階層の **Level B 生成物**。

```
project-root/
├── INDEX.md / SPEC.md / DONT.md / REGIME.md / CLAUDE.md
├── .claude/ / sensors/
└── history/                    ← 本ドキュメントが規定する領域
    ├── SUMMARY.md              # 自動生成、L0振り返り儀式で使用
    ├── INTENT.md               # WHY層（機能の意図、却下案、廃止理由）
    ├── CHANGELOG.md            # WHAT層変遷（時系列変更記録）
    ├── REGIME-LOG.md           # 判定層の事後評価
    ├── ARCH-DECISIONS.md       # HOW層判断（任意、ADR形式）
    ├── PATTERNS.md             # 失敗/成功パターン（任意、自動蓄積）
    ├── E2E-LOG.md              # E2E run 要約（任意・UIプロジェクト、append-only WARM、v5.24.0）
    └── archive/                # 古い廃止INTENT + COLD（archive/YYYY-MM/e2e/ に相A artifact・生runログ）
```

---

## ファイル責務と必須/任意

| ファイル | 書き手 | 読み手 | 形式 | 必須条件 |
|---|---|---|---|---|
| SUMMARY.md | AI（自動生成） | L0/L1/reviewer/人間 | 圧縮サマリ | LC ≥ 1 |
| INTENT.md | L0（対話で抽出） | L0/L1/reviewer | 機能ID×意図のマッピング | LC ≥ 1 |
| CHANGELOG.md | L1（献上時自動追記） | L0（次回対話時） | 時系列の機能変遷 | LC ≥ 1 |
| REGIME-LOG.md | L1（事後評価から抽出） | L0（次回判定時） | 判定×実績の対応表 | LC ≥ 1 |
| ARCH-DECISIONS.md | L1（実装時記録） | L1（次回拡張時） | ADR形式の軽量版 | 任意 |
| PATTERNS.md | reviewer（検証時抽出） | L1（実装前参照） | 罠パターン集 | 任意 |
| E2E-LOG.md | L1 / CI（run 後追記） | reindex / reviewer | append-only run 要約（WARM） | 任意（UIプロジェクト & E2E あり） |

**原則**: 履歴の更新主体はAI単独。人間は承認するのみ（`ritual-protocol.md` F3 フェーズで承認粒度を定義）。

---

## INTENT.md

### 目的

機能が「なぜこの条件で存在するのか」を記録する。1→5運用で最も失われやすい情報。

### テンプレート

```markdown
# 意図ログ

## 機能ID: F001 - カート機能

- **状態**: 現役
- **追加日**: 2026-01-15
- **意図**: 購入意思決定の中断・再開を許容するため
- **条件根拠**:
  - 上限30品 → 平均購入数の3倍を許容（離脱防止）
  - 在庫超過時エラー → UX上の即時フィードバックが目的
- **却下案**:
  - 上限なし: パフォーマンス劣化リスク
  - 在庫予約: スコープ外（DONT.md参照）
- **関連**: F002（決済）, F005（在庫）
- **確度**: 確定  <!-- 確定 / AI推定 (YYYY-MM-DD) -->

## 機能ID: F003 - お気に入り

- **状態**: 廃止 (2026-03-20)
- **廃止理由**: 利用率2%未満、カート機能で代替可能と判断
- **復活条件**: ユーザーリサーチで明確な要望が再度上がった場合
- **廃止合議**: 人間承認、AI状況データ提示
```

### 確度メタデータ

曖昧応答を AI が最適解で充当した項目には `**確度**: AI推定 (YYYY-MM-DD)` を付ける。

- AI が過去INTENT・状況データから推定した内容
- 次回儀式 F2 で「異議ないか」を一括確認（質問を分散させない）
- 次ループで訂正されたら取り消し線方式で修正

詳細は `ritual-protocol.md` E1対応（曖昧応答の扱い）を参照。

### 訂正記述（取り消し線方式）

証跡保存のため上書きせず、取り消し線で残す。

```markdown
## 機能ID: F001 - カート機能

- **条件根拠**:
  - 上限30品 → 平均購入数の3倍を許容（離脱防止）
  - ~~在庫超過時エラー → 在庫管理側との競合状態回避~~
  - **【訂正 2026-04-18】** 在庫超過時エラー → UX上の即時フィードバックが目的。
    - 訂正理由: F005実装時に在庫管理側のロック機構を確認、競合状態の問題はそちらで解決済みと判明
    - 検出: layer1-independent-reviewer
    - 合議: 人間承認（2026-04-18）
```

---

## CHANGELOG.md

### テンプレート

```markdown
# 変更履歴

## 2026-04-18 (LC=1 拡張)

### 追加
- F010 通知機能（INTENT.md参照）

### 変更
- F001 カート上限 30→50（INTENT.md F001 v2参照）

### 廃止
- F003 お気に入り（INTENT.md F003参照）

### 体制
- 判定: M2
- 事後評価: 妥当
- REGIME-LOG.md 参照

### 儀式記録（本サイクルの振り返り儀式）
- レベル: 2（動的格上げ: 1→2, 理由=却下案再提案検出）
- スキップ: なし
- 検出件数: 矛盾1, 復活要求0, 再提案1
```

### 記述ルール

- 献上サイクル単位で追記（上書きしない）
- 追加／変更／廃止の3カテゴリで分類
- 各項目は INTENT.md の該当機能IDへの参照を必ず含める
- 「儀式記録」セクションは `ritual-protocol.md` の形骸化防止メカニズムのため必須

---

## REGIME-LOG.md

### テンプレート

```markdown
# 判定履歴

## 第3回 (2026-04-18)

- **判定**: M2 (S=4, U=1, R=2)
- **LC**: LC=1（拡張）
- **実績**: 妥当
- **根拠**: layer1-independent-reviewer が2件指摘、自力修正1回ループ
- **儀式レベル**: 2（動的格上げあり: 1→2、却下案再提案検出）
- **儀式拒否**: なし  <!-- ありの場合は連続回数も記録 -->
- **次回示唆**: 同規模なら M2 継続。F010 追加で独立ドメイン 4→5 に近づいたため L2 閾値に注意
```

### 記述ルール

- 献上のたびに追記
- 「体制事後評価」（`layer1-autonomous-dev/references/delivery-format.md`）から該当情報を抽出して記録
- 儀式拒否（`ritual-protocol.md` E2対応）は連続回数を明示（5回連続で SUMMARY.md に警告常設）

---

## SUMMARY.md

### 目的

履歴全体の圧縮版。L0 対話開始時に AI がロードする「過去文脈」の実質的エントリポイント。

### テンプレート（自動生成）

```markdown
# 履歴サマリ（自動生成 / 最終更新: 2026-04-18）

## 現役機能の意図概略
- F001 カート: 購入中断対応 / 30品上限 / UX即時フィードバック
- F002 決済: ...

## 廃止機能（直近6ヶ月）
- F003 お気に入り (2026-03-20): 利用率低

## 直近の体制傾向
- 過去3回中: M2 妥当 2回, M2 過剰 1回 → M1 降格余地あり

## 直近の訂正
- F001 在庫超過エラーの意図訂正 (2026-04-18)

## 要再確認リスト（確度=AI推定の項目）
- F008 通知音量 30% の根拠: AI推定 (2026-04-10) - 次回儀式で確認

## 注意事項
- F010 追加で L2 閾値接近
- 直近 5 回のうち 3 回儀式スキップ（警告閾値未達）
```

### 自動生成トリガー（β-2確定）

イベント駆動ハイブリッド方式：

1. **L1 献上時**: 履歴更新の延長で SUMMARY.md を自動再生成（差分反映）
2. **L0 対話開始時**: `SUMMARY.md 最終更新日 < history/ 内の他ファイル最新更新日` なら再生成、それ以外は使い回し

判定の実装参考（擬似コード）：

```
latest_history = max(mtime of INTENT.md, CHANGELOG.md, REGIME-LOG.md, ARCH-DECISIONS.md, PATTERNS.md)
if mtime(SUMMARY.md) < latest_history:
    regenerate SUMMARY.md
else:
    reuse existing SUMMARY.md
```

---

## ARCH-DECISIONS.md（任意）

ADR（Architecture Decision Record）形式の軽量版。L1 が実装時に HOW レベルの判断を記録する。

```markdown
# 設計判断ログ

## AD-001: 通知ライブラリ選定 (2026-04-18)

- **文脈**: F010 通知機能実装
- **選択肢**: A. ネイティブWebSocket / B. socket.io / C. SSE
- **決定**: B. socket.io
- **根拠**: 再接続処理とフォールバックが標準装備。実装時間短縮
- **トレードオフ**: 依存パッケージサイズ増（+120KB）
- **関連**: F010 (INTENT.md)
```

---

## PATTERNS.md（任意）

layer1-independent-reviewer が検証時に発見した罠パターンを蓄積。L1 が次回実装前に参照する。

```markdown
# パターン集

## 罠パターン

### P-001: 在庫チェックの二重実装
- **発見日**: 2026-03-15
- **検出**: layer1-independent-reviewer
- **症状**: 機能AとBで独立に在庫チェック → 整合性バグ
- **対策**: 在庫チェックは F005（在庫管理）経由のみ許可

## 成功パターン

### S-001: INTENT-first 開発
- **発見日**: 2026-04-01
- **文脈**: F010 実装前に INTENT.md を先に書いた
- **効果**: 実装中の仕様解釈ブレがゼロ、レビュー指摘ゼロ
```

---

## E2E-LOG.md（任意・UIプロジェクト・v5.24.0 追加）

### 目的

E2E テストの **run 要約**を append-only で蓄積する WARM 層。情報代謝サイクルの新しい episodic ソースであり、
reindex がここから flaky 反復・安定 journey を増分摂取して罠/RL に結晶化する（専用サイクルは作らない）。
定義の正本は `../../layer0-reindex-librarian/references/metabolism-regime.md` §7、構築規律は
`../../layer1-autonomous-dev/references/e2e-best-practices.md` §9。

### 性質（購読量保護の要）

- **WARM**: 既定では全文ロードしない。reindex が cursor 続きの delta のみ増分摂取する
- **相 A artifact は本ファイルに書かない**: Trace/動画/network/console は COLD 直行
  （`history/archive/YYYY-MM/e2e/`）。E2E-LOG には**ポインタ（cold:// パス）と要約のみ**を残す
- **append-only**: run のたびに 1 エントリ追記。上書き・編集しない（証跡保存）

### テンプレート（run 要約 1 エントリ）

```markdown
# E2E run ログ（append-only / reindex 増分摂取対象）

## run 2026-06-08T06:13Z (CI #1421, commit a1b2c3d)
- provenance: chromium 124.0 (playwright v1.44.0, container sha256:9f01…)  <!-- §7 借りない・固定する・記録する -->
- 結果: 42 passed / 1 failed / 2 flaky / 18.3s
- flaky: checkout-flow（3 回中 1 回 fail・viewport=375 のみ／他環境では安定）
  - artifact: cold://2026-06/e2e/run-2026-06-08T0613Z-checkout.jsonl  <!-- 相 A 生ログは COLD 直行 -->
- quarantine: なし
```

### 代謝での扱い（tier・昇降格）

- reindex が **flaky の反復**（`council_gate.repetition_threshold` 回以上・`min_age_days` 経過）を検出 →
  Council ゲート経由で **flaky 罠（HOT・反-発火条件付）**に結晶化。罠は生 run ログ（COLD 原本）から蒸留する（#6）
- **安定 journey** は RL 候補（SPEC critical journey の実行可能投影＝相 B）
- flaky 率超過・隔離台帳は `crosscut-feedback-loop`（`flaky_rate_breach` / `e2e_quarantine`）へ還流
- 結晶化完了済みの古い run 要約は cycle 境界で COLD（`archive/YYYY-MM/e2e/`）へ排泄（source pointer 付）

### 承認レベル

run 要約の追記は **レベル A（自動承認・通知のみ）**。flaky 罠の HOT 昇格は Council ゲート + 人間最終承認（レベル C 相当）。

---

## archive/

### 対象

廃止機能 INTENT のうち、廃止日から **2年経過**したもの。
加えて **E2E の COLD 排泄物**（相 A artifact・生 run ログ・結晶化完了済みの古い run 要約）を
`archive/YYYY-MM/e2e/` に retrievable で保持する（archive≠delete・disk 無制限 OK・既定非ロード）。

### 対象外（本体に残す）

- 現役機能 INTENT
- 訂正履歴（取り消し線記録）
- CHANGELOG.md 本体（時系列全体）
- REGIME-LOG.md 本体
- ARCH-DECISIONS.md 本体

### 移動タイミング（β-1確定）

- **固定 N 年** = **2年**（デフォルト）
- N は REGIME.md の「履歴層設定」セクションで上書き可能
- L1 献上時に自動チェックし、対象があれば `history/archive/YYYY-MM/` 配下へ移動

### archive 配下の構造

```
history/archive/
├── 2024-04/
│   └── INTENT-F003.md   # 廃止済みINTENT、機能ID単位
├── 2024-05/
│   └── INTENT-F007.md
└── ...
```

---

## LC 軸との対応

LC の詳細判定は `regime-assessment.md` を参照。履歴層との関係のみここで規定。

| LC | 履歴層の扱い |
|---|---|
| LC=0（新規） | 履歴層は新規作成のみ。儀式レベル 0（スキップ） |
| LC=1（拡張） | INTENT / CHANGELOG 参照を必須化。儀式はデフォルト レベル 1 |
| LC=2（保守） | 全履歴層参照必須、reviewer で整合性検証。儀式デフォルト レベル 2 |

---

## 履歴更新の承認 3段階

L1 献上時に履歴層の更新差分を `DELIVERY.md` に提示する。承認レベル別に分類する。

| レベル | 対象 | 人間対応 |
|---|---|---|
| A（自動承認） | CHANGELOG追記、ARCH-DECISIONS追記、PATTERNS追記 | スキップ可、通知のみ |
| B（確認推奨） | INTENT 新規追加、REGIME-LOG 事後評価 | 一覧確認、無修正で承認可 |
| C（必須承認） | INTENT 廃止マーキング、却下案追加、LC 変更、取り消し線訂正 | 個別承認、修正可能 |

### 判定基準

- **A**: 履歴層内で完結する追記、過去判断と矛盾しない
- **B**: 新規記録だが将来判断に影響、破棄しても復元容易
- **C**: 過去判断の上書き/否定、または将来制約となる記録

承認設定は REGIME.md の「履歴更新承認設定」セクションで変更可能（例: レベル B を自動承認化）。

---

## REGIME.md の履歴層関連セクション

`meta-spec-template.md` の REGIME.md テンプレートに以下が追加される。

```markdown
## 履歴層設定

- archive 移動年数: 2 年（デフォルト）
- 儀式拒否連続警告閾値: 5 回
- 儀式スキップ連続警告閾値: 5 回

## 履歴更新承認設定

- レベルA（自動承認）: スキップ
- レベルB（確認推奨）: 通知のみ、デフォルト承認
- レベルC（必須承認）: 必ず確認
```

---

## フラクタル原則との整合

履歴層追加により各層に「現在⇄過去」の照合パターンが同形に入る。

| 層 | 既存のフラクタル | 履歴層追加後 |
|---|---|---|
| L0⇄人間 | 欲求⇄構造化 | + 過去INTENT ⇄ 現欲求 |
| L1内 | spec⇄code | + 過去pattern ⇄ 現実装 |
| L2⇄L1群 | 指示⇄検証 | + 過去判定 ⇄ 現規模 |

全層で構造が一致するため、将来の L3 拡張等でも同一パターンで適用可能。
