# spec/state-diagrams.md — 状態遷移図（Mermaid）

`spec/state-machine.ts` の図解。実装と図の整合は L1 が責任を持つ。

## トップレベル状態機械

```mermaid
stateDiagram-v2
    [*] --> boot
    boot --> opening: 初回起動
    boot --> home: 2回目以降
    opening --> home: OPENING_DONE / SKIP

    home --> drawing: REQUEST_PICKED
    home --> dex: GO_DEX
    home --> scroll: GO_SCROLL
    home --> settings: GO_SETTINGS
    home --> boot: QUIT_SESSION

    drawing --> judging: DRAWING_DONE
    drawing --> home: DRAWING_CANCEL

    judging --> reaction: JUDGEMENT_RECEIVED / FALLBACK / 10s timeout

    reaction --> home: REACTION_DISMISSED\n(addToScroll / maybeAddToDex)

    dex --> home: GO_HOME
    scroll --> home: GO_HOME
    settings --> home: GO_HOME
```

## judging（並列状態 — 重要）

```mermaid
stateDiagram-v2
    state judging {
        state api {
            [*] --> calling
            calling --> received: JUDGEMENT_RECEIVED
            calling --> received: JUDGEMENT_FALLBACK
            calling --> received: 10s timeout
            received --> [*]
        }
        --
        state waitingExperience {
            [*] --> active
            active --> interrupting: JUDGEMENT_RECEIVED / FALLBACK
            interrupting --> [*]
        }
    }
    judging --> reaction: onDone (両並列状態 final)
```

**重要不変**: `waitingExperience` が走らずに `reaction` に遷移するパスは存在しない。
SPEC.md F6（待ち時間も体験）と DONT.md A 節の哲学を満たすため、両並列状態の同時 final が必須。

## 描画キャンバス サブステート

```mermaid
stateDiagram-v2
    [*] --> idle
    idle --> stroking: STROKE_START
    stroking --> idle: STROKE_END / commitStroke

    idle --> idle: UNDO / undoLastStroke
    idle --> idle: REDO / redoStroke
    idle --> erasing: ERASE
    erasing --> idle: STROKE_END
    idle --> confirming_clear: CLEAR_ALL
    confirming_clear --> idle: CLEAR_ALL / clearAll
    confirming_clear --> idle: CANCEL

    idle --> finishing: FINISH
    finishing --> [*]
    idle --> cancelled: CANCEL
    cancelled --> [*]
```

**重要不変**:
- いつでも CANCEL で home に戻れる（DONT.md C 節「戻る常時可能」）
- `confirming_clear` は強制ではなく優しい確認（CANCEL でキャンセル可能）

## ハッピーパス（妹さん視点）

```mermaid
sequenceDiagram
    participant 妹さん
    participant App
    participant Gemini
    participant Sheets

    妹さん->>App: 起動
    App->>Sheets: 問題プール取得
    Sheets-->>App: Problem[]
    App->>妹さん: 森ホーム表示、ケロぴ「依頼があるよ！」

    妹さん->>App: 依頼を選ぶ
    App->>妹さん: 描画キャンバス
    妹さん->>App: 描く
    妹さん->>App: 「できた！」

    App->>Gemini: 絵 + 期待概念で判定要求
    Note over App,Gemini: 並行: 待ち時間ミニゲーム表示
    App->>妹さん: ミニゲーム or 解説アニメ
    妹さん->>App: ミニゲームで遊ぶ

    Gemini-->>App: 判定結果（生 JSON）
    App->>App: 3 段階に正規化
    App->>妹さん: ケロぴ大喜び！🌟（or 寄り添い💭 / 別角度🌱）

    妹さん->>App: 「うん」
    App->>App: 絵巻に追加 / 図鑑に住人追加
    App->>妹さん: 森ホームに戻る、次の依頼
```

## サッドパス（API 失敗）

```mermaid
sequenceDiagram
    participant 妹さん
    participant App
    participant Gemini

    妹さん->>App: 描いた絵を「できた！」
    App->>Gemini: 判定要求
    Note over App: 並行: 待ち時間ゲーム
    Gemini--xApp: タイムアウト / エラー
    App->>App: フォールバック判定（"encourage" 既定）
    App->>妹さん: 「ケロぴ、考え中だったみたい！\nでも素敵な絵だね、絵巻に残そう」
    Note over App,妹さん: 不正解扱いしない（DONT.md A 節）
    App->>App: 絵巻には保存
    App->>妹さん: 森ホームに戻る
```
