# Hitsuji — 独立検証チェックリスト

`layer1-independent-reviewer` が L1 献上時に**機械的に走査する観点リスト**。
`computational.md` + `inferential.md` の上位に位置するメタチェックリスト。

各項目は「pass / fail / unclear」で記録すること。

---

## A. 献上物の完備性

- [ ] **A1.** `delivery/DELIVERY-<feature>.md` が存在する
- [ ] **A2.** `delivery/HANDOFF-<feature>.md` が存在する（次作業の引き継ぎ）
- [ ] **A3.** PR が作成済み、説明文に SPEC との対応関係が明記されている
- [ ] **A4.** commit message に session URL が含まれている
- [ ] **A5.** `delivery/REVIEW-<feature>.md`（本検証結果出力先）の置き場が確保されている

---

## B. 機械検証 (computational.md) の合格

- [ ] **B1.** `./gradlew assembleDebug` が成功
- [ ] **B2.** `./gradlew lintDebug` で error 0 件
- [ ] **B3.** `./gradlew ktlintCheck` で違反 0
- [ ] **B4.** `./gradlew detekt` で weighted issues < 50
- [ ] **B5.** `./gradlew testDebugUnitTest` で全テスト pass
- [ ] **B6.** coverage が目標値以上（domain ≥ 80%, repository ≥ 70%, viewmodel ≥ 60%）
- [ ] **B7.** AndroidManifest.xml に 5 つの必須パーミッションが宣言されている
- [ ] **B8.** minSdk=26, targetSdk=34 で設定されている
- [ ] **B9.** クレジットマーカーが README.md に保持されている

---

## C. SPEC 整合 (Layer 1)

- [ ] **C1.** F1 タスク登録と通知が動作する
- [ ] **C2.** F2 予定登録と通知が動作する
- [ ] **C3.** F3 段階エスカレーション通知が Lv.1〜Lv.4 まで動作する
- [ ] **C4.** F5 手動登録が 3 タップ以内で完了する
- [ ] **C5.** F7 データがローカル Room に永続化される
- [ ] **C6.** ドメインモデル（Task / NotificationState / ScoreLedger / Streak）が SPEC 通り実装されている
- [ ] **C7.** パーミッション請求が段階的・目的説明付きで実装されている
- [ ] **C8.** 拒否時の機能縮退が SPEC 通り実装されている

---

## D. DONT 違反検査 (Layer 2)

- [ ] **D1.** 広告 SDK が含まれていない
- [ ] **D2.** ログイン / アカウント機能の痕跡がない
- [ ] **D3.** クラウド送信処理がない（Phase 1）
- [ ] **D4.** キャラ常駐 UI が画面にない
- [ ] **D5.** ペナルティ / 減点 UI がない
- [ ] **D6.** iOS / Flutter / React Native コードが混入していない
- [ ] **D7.** 確認ダイアログの濫用がない（3 階層深い画面遷移もない）
- [ ] **D8.** 物理物追跡 / NFC / IoT 連携の痕跡がない

---

## E. DESIGN 整合 (Layer 3)

- [ ] **E1.** カラー HEX 直書きが theme/ 配下以外に存在しない
- [ ] **E2.** spacing 数値が `Hitsuji.spacing.*` トークン経由で参照されている
- [ ] **E3.** typography が `MaterialTheme.typography` 経由で参照されている
- [ ] **E4.** 通知段階の色が DESIGN.md の段階別カラー（blue/amber/red）に準拠
- [ ] **E5.** コーナー半径が DESIGN.md `{radius.*}` に従う
- [ ] **E6.** アニメーション duration が 500ms 以下
- [ ] **E7.** Do's and Don'ts に対する明らかな違反がない

---

## F. 不変条件 (Layer 4)

`spec/invariants.feature` の各 Evil シナリオが**最低でも該当 Repository / ViewModel の unit test として実装されている**こと。

- [ ] **F1.** COMPLETED → NOTIFYING 戻り禁止のテストがある
- [ ] **F2.** スコア二重加算拒否のテストがある
- [ ] **F3.** ARCHIVED からの状態復活拒否のテストがある
- [ ] **F4.** 段階降格禁止のテストがある
- [ ] **F5.** 過去時刻タスクが NOTIFYING にならないテストがある
- [ ] **F6.** SCHEDULE_EXACT_ALARM 拒否時の SecurityException 処理テストがある
- [ ] **F7.** 重複タスクのマージ処理テストがある
- [ ] **F8.** 連続日数の負値防止テストがある

---

## G. 哲学整合 (Layer 5)

- [ ] **G1.** ADHD 当事者特性（即応性・低認知負荷・短期報酬）を尊重した UX か
- [ ] **G2.** 叱責 / ペナルティ的 UX が混入していない
- [ ] **G3.** 「シンプル」「無駄が嫌い」Must を満たしている（不要画面なし）
- [ ] **G4.** 完全非同期で UI ブロックがない（StrictMode で確認）
- [ ] **G5.** persona=sheep-navigator がコード（識別子・log・comment）にリークしていない
- [ ] **G6.** dialog-harness クレジットが README.md 末尾に保持されている
- [ ] **G7.** 人間最終承認原則が守られた献上フローになっている

---

## H. ドキュメント整合

- [ ] **H1.** SPEC.md と実装の差分が DELIVERY.md に明記されている
- [ ] **H2.** 新規 ADR が必要な決定があれば `delivery/ADR-NNN-*.md` で記録されている
- [ ] **H3.** HANDOFF.md に次作業の起点が明記されている
- [ ] **H4.** README.md / INDEX.md にプロジェクト構造の最新が反映されている
- [ ] **H5.** 第 2 段階で生成されたファイルへの dead link がない

---

## 検証結果フォーマット

レビュー終了時に `delivery/REVIEW-<feature>.md` を以下の形式で出力：

```markdown
# Review: <feature>

| カテゴリ | pass / fail / unclear | コメント |
|---|---|---|
| A. 完備性 | pass | 全項目クリア |
| B. 機械検証 | pass | coverage 76%（目標達成） |
| C. SPEC 整合 | fail | F3 Lv.4 が未実装 |
| D. DONT 違反 | pass | |
| E. DESIGN 整合 | fail | theme/ 外で HEX 直書き 2 箇所 |
| F. 不変条件 | pass | 8 件全て unit test 実装済 |
| G. 哲学整合 | pass | |
| H. ドキュメント | pass | |

## 総合判定

- 状態: **差し戻し**（critical fail = C）
- 修正必須: F3 Lv.4 実装、theme/ 外 HEX 直書き 2 箇所
- 修正後の再献上を待つ
```

---

## 不変ルール

- レビュアーは**実装コンテキストを引き継がない**。`SPEC.md` / `DONT.md` / `HANDOFF.md` / 本チェックリストのみを根拠に判定する
- 「実装者の意図」を推察して甘くしない。曖昧なら unclear として人間献上
- レビュアー自身が修正コミットを書かない（差し戻しのみ、修正は L1 が再実行）
