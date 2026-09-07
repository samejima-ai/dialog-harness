# Hitsuji — 推論的検証 sensor（5 層エラー検出スタック）

機械的検証で捉えられない**意味的・設計的な逸脱**を独立検証者（layer1-independent-reviewer）が推論で検出する観点群。

---

## Layer 1: SPEC 整合（Specification Alignment）

実装が SPEC.md の機能定義から逸脱していないか。

### 検出観点

| # | 観点 | チェック方法 |
|---|---|---|
| 1.1 | F1〜F7 各機能が実装されているか | 機能ごとに UI / Repository / Domain の存在確認 |
| 1.2 | 優先度 critical の機能が完成しているか | F1, F2, F3, F5, F7 を最優先で検査 |
| 1.3 | UX 制約（3 タップ以内 / p95 300ms）を満たしているか | UI フロー目視 + パフォーマンス計測 |
| 1.4 | パーミッション請求順序が SPEC 通りか | オンボーディング / 各機能初回起動を実機確認 |
| 1.5 | ドメインモデルの必須フィールドが揃っているか | data class 定義と SPEC の擬似コード比較 |

### FAIL 条件

- critical 機能の 1 つでも実装欠落 → **即献上**
- SPEC に書かれた optional フィールドの誤った必須化（例：`description?` が必須になっている）
- パーミッション請求順序の SPEC との不一致

---

## Layer 2: DONT 違反（Anti-Scope Detection）

DONT.md に明記された「作らない」要素が紛れ込んでいないか。

### 検出観点

| # | 観点 | チェック方法 |
|---|---|---|
| 2.1 | 広告 SDK が組み込まれていないか | `build.gradle.kts` の依存検査 |
| 2.2 | ログイン / アカウント機能の痕跡がないか | コード grep（"login" "signin" "auth" 等） |
| 2.3 | クラウド送信処理がないか（Phase 1） | Retrofit / OkHttp の外部 URL 接続検査 |
| 2.4 | キャラ常駐 UI が画面に存在しないか | Compose screenshot 目視 |
| 2.5 | ペナルティ / 減点 UI がないか | Score 加算ロジックと UI 検査 |
| 2.6 | iOS / Flutter / React Native コードが混入していないか | プロジェクト構造検査 |
| 2.7 | 確認ダイアログの濫用がないか | ダイアログ件数とフロー妥当性 |

### FAIL 条件

- DONT 違反 1 件でも検出 → **必ず献上**、勝手に修正しない

---

## Layer 3: DESIGN 整合（Visual Token Consistency）

DESIGN.md のトークンが正しく参照されているか。

### 検出観点

| # | 観点 | チェック方法 |
|---|---|---|
| 3.1 | カラー HEX 直書きが theme/ 以外にないか | grep `Color(0x...)` |
| 3.2 | spacing 数値が `Hitsuji.spacing.*` 参照になっているか | `.dp` の直書き頻度 |
| 3.3 | typography が `MaterialTheme.typography` 経由か | Text コンポーネントの style 指定検査 |
| 3.4 | 通知段階の色が DESIGN.md の段階別カラーに準拠しているか | NotificationCompat.Builder の color 指定 |
| 3.5 | コーナー半径が DESIGN.md の `{radius.*}` に従っているか | RoundedCornerShape の数値検査 |
| 3.6 | アニメーション duration が 500ms 以下か | animateDpAsState / transition の duration |

### FAIL 条件

- theme/ 外での HEX 直書き → **要修正**
- 通知段階色の DESIGN との不一致 → **要修正**（ユーザー認知の生命線）

---

## Layer 4: 不変条件違反（Invariant Violation）

`spec/invariants.feature` の Evil 系シナリオが守られているか。

### 検出観点

| # | 観点 | invariants.feature の対応 |
|---|---|---|
| 4.1 | Task の状態遷移が単調か（COMPLETED → NOTIFYING 戻りなし）| シナリオ「COMPLETED から NOTIFYING への戻りを禁止」|
| 4.2 | スコアの二重加算が起きないか | シナリオ「スコアの二重加算を拒否」|
| 4.3 | ARCHIVED からの状態復活がないか | シナリオ「ARCHIVED からの状態復活を禁止」|
| 4.4 | エスカレーション段階の降格がないか | シナリオ「段階の降格を禁止」|
| 4.5 | 過去時刻タスクが NOTIFYING に上がらないか | シナリオ「過去時刻のタスクを誤って NOTIFYING にしない」|
| 4.6 | パーミッション拒否時に SecurityException が安全に処理されるか | シナリオ「SCHEDULE_EXACT_ALARM 不可状態」|
| 4.7 | 重複タスクのマージが機能するか | シナリオ「同一タイトル + 同一時刻の重複登録」|
| 4.8 | 連続日数が負値にならないか | シナリオ「連続日数の負の値を防ぐ」|

### FAIL 条件

- Evil 系シナリオが Repository / ViewModel 層の unit test として実装されていない → **要追加**
- 実装にて Evil シナリオが再現可能（テストで invariant violation を引き起こせる）→ **即献上、要修正**

---

## Layer 5: 哲学整合（Philosophy Alignment）

dialog-harness-layers v5 philosophy.md の 6 条憲法および本プロジェクトの**ADHD 当事者向け哲学**との整合。

### 検出観点

| # | 観点 | チェック方法 |
|---|---|---|
| 5.1 | UX が ADHD 当事者特性（即応性・低認知負荷・短期報酬）を尊重しているか | UI フロー目視 + ユーザビリティ評価 |
| 5.2 | 叱責 / ペナルティ的 UX が混入していないか | エラーメッセージ / 通知文面の文言検査 |
| 5.3 | 「シンプル」「無駄が嫌い」の Must を満たしているか | 不要画面 / 不要設定の検査 |
| 5.4 | 完全非同期で UI ブロックがないか | StrictMode 検査 + 主要操作の応答計測 |
| 5.5 | persona=sheep-navigator の応答スタイルがコードにリーク**していない**か | 識別子 / コメント / log message に「〜なのん」等が**入っていない**こと |
| 5.6 | dialog-harness クレジットが README.md 末尾に保持されているか | grep |
| 5.7 | 人間の最終承認原則（philosophy 第 6 条）が守られているか | M2 ルール：献上 → 独立検証 → 人間 merge |

### FAIL 条件

- ペナルティ UX 混入 → **即修正**
- persona がコードに混入 → **即修正**（仕様コード分離違反）
- 非同期化されていない重い処理 → **即修正**

---

## 推論検証の実行手順

`layer1-independent-reviewer` が L1 献上を受けた際の手順：

1. **入力読み込み**: `SPEC.md` / `DONT.md` / `DESIGN.md` / `spec/*` / `delivery/HANDOFF-*.md`
2. **Layer 1 → 5 を順次実行**: 上位レイヤーで FAIL したら下位も走査して fix list を作る
3. **観点ごとに verdict**: pass / fail / unclear（unclear は人間献上）
4. **総合判定**:
   - 全 layer pass → **承認**、merge 可
   - critical fail（Layer 1〜2）→ **差し戻し**、L1 で修正
   - non-critical fail（Layer 3〜5）→ **条件付き承認 + 追加 issue**
5. **`delivery/REVIEW-<feature>.md` に結果出力**

---

## 不確実性の扱い（unclear 判定）

| 状況 | 対応 |
|---|---|
| SPEC が曖昧で判断不能 | L0 spec-architect に差し戻し |
| 判断にトレードオフがある | crosscut-council を起動 |
| AI の信頼度 < 0.6 | 人間献上、判断保留 |
| 検証ツール自体の不備 | sensors の更新を提案 |

判定を**強行しない**。曖昧なら必ず unclear として記録すること。
