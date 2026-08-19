# Hitsuji — 状態遷移図（L0-4 簡易モード）

縮退判断により Mermaid 図のみで記述。XState JSON 機械化は対象外（ADR-001 参照）。

---

## 1. Task 状態遷移

タスクのライフサイクル全体を表す。`TaskStatus` enum と一致。

```mermaid
stateDiagram-v2
    [*] --> PENDING : 登録（音声/カレンダー/手動）

    PENDING --> NOTIFYING : scheduled_at 到達
    PENDING --> COMPLETED : 事前完了（早期実行）
    PENDING --> EXPIRED : 24h 超過、無通知（オフライン等）

    NOTIFYING --> ESCALATING : Lv.1 通知後 5min 経過、操作なし
    NOTIFYING --> COMPLETED : 完了タップ
    NOTIFYING --> SNOOZED : Snooze タップ

    ESCALATING --> ESCALATING : Lv.N → Lv.N+1（5/15/30min 閾値）
    ESCALATING --> COMPLETED : 完了タップ
    ESCALATING --> SNOOZED : Snooze タップ
    ESCALATING --> EXPIRED : Lv.4 到達後 1h 経過、操作なし

    SNOOZED --> NOTIFYING : Snooze 時間経過

    COMPLETED --> ARCHIVED : 完了から 90 日経過
    EXPIRED --> ARCHIVED : 期限切れから 90 日経過

    ARCHIVED --> [*]
```

### 不変条件（本図に対応するもの）

- `COMPLETED` から `NOTIFYING` への戻りは**禁止**（完了したものを再通知しない）
- `ARCHIVED` から他状態への戻りは**禁止**（履歴は不変）
- `ESCALATING` から `PENDING` への戻りは**禁止**（時間軸の単調性）

---

## 2. 通知エスカレーション段階遷移

`NotificationState.current_level` の遷移。F3 機能と直結。

```mermaid
stateDiagram-v2
    [*] --> LV1 : NOTIFYING 状態に入る

    LV1 --> LV2 : +5 分、ユーザー操作なし
    LV2 --> LV3 : +15 分（LV1 から累計）
    LV3 --> LV4 : +30 分（LV1 から累計）

    LV1 --> Completed : 完了タップ
    LV2 --> Completed : 完了タップ
    LV3 --> Completed : 完了タップ
    LV4 --> Completed : 完了タップ

    LV1 --> Snoozed : Snooze
    LV2 --> Snoozed : Snooze
    LV3 --> Snoozed : Snooze
    LV4 --> Snoozed : Snooze

    LV4 --> LV4 : +5 分、繰り返し（FullScreenIntent + Alarm）

    Completed --> [*]
    Snoozed --> [*]

    note right of LV1
        色: primary blue (#5B8DEF)
        バイブ: 標準
    end note

    note right of LV2
        色: warning amber (#F5A623)
        バイブ: 強化
    end note

    note right of LV3
        色: danger red (#E5484D)
        バイブ: 強 + 音量増
    end note

    note right of LV4
        色: danger + Full-screen intent
        アラーム継続
    end note
```

### タスクごとの最大段階制限

`Task.escalation_max` で Lv.1〜Lv.4 を選択可能。
例：軽微な習慣タスク → Lv.2 で停止 / 服薬通知 → Lv.4 まで。

### 不変条件

- 段階は**単調増加**のみ（LV3 → LV2 への降格は禁止）
- `Snooze` 後に `NOTIFYING` に戻る際、`current_level` は **LV1 から再開**（リセット仕様）
- `Task.escalation_max` を超える段階には到達できない

---

## 3. 入力ソース → タスク化フロー

`TaskSource` enum 別の登録経路。

```mermaid
flowchart TD
    VOICE[音声入力<br/>SpeechRecognizer] --> NLP[NLP パース<br/>"明日10時 薬"]
    CAL[Google Calendar<br/>CalendarContract] --> NORMALIZE[正規化]
    MSG[通知リスナー<br/>LINE/メッセージ] -.MVP外.-> NORMALIZE
    MAIL[Gmail API] -.MVP外.-> NORMALIZE
    MANUAL[手動 1 タップ<br/>FAB] --> NORMALIZE

    NLP --> NORMALIZE
    NORMALIZE --> TASK[Task 生成<br/>UUID + scheduled_at]
    TASK --> SCHEDULE[AlarmManager.setExactAndAllowWhileIdle]
    SCHEDULE --> NOTIFY[通知発火]
```

### 不変条件

- すべての入力経路は最終的に **同一の Task entity** に正規化される（`source` で由来は記録）
- 重複検知：同一 `title` + `scheduled_at` ±1 分以内は **マージ**

---

## 4. ゲーミフィケーション状態（Score + Streak）

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> ScoreGained : Task COMPLETED
    ScoreGained --> CheckStreak : +10pt or +15pt 加算

    CheckStreak --> StreakIncrement : 今日まだ完了 0 件
    CheckStreak --> Idle : 今日既に完了あり

    StreakIncrement --> StreakMilestone : 連続日数が 3/7/30/100 のどれかに到達
    StreakIncrement --> Idle : マイルストーン外

    StreakMilestone --> BadgeUnlock : バッジ獲得演出
    BadgeUnlock --> Idle

    Idle --> StreakReset : 日付変更 + 前日完了 0 件
    StreakReset --> Idle : streak.current_days = 0
```

### 不変条件

- 1 タスク完了で**スコアは 1 回のみ**加算（重複加算禁止）
- 連続日数は **1 日 1 回のみ**増加（同日 2 件完了でも +1）
- マイルストーン到達時のバッジは**冪等**（重複バッジ生成禁止）

---

## 5. データフェーズ移行（Phase 1 → Phase 2）

```mermaid
stateDiagram-v2
    [*] --> Phase1_Local : 初回起動

    Phase1_Local --> Phase1_Local : 通常運用<br/>Room/SQLite ローカル
    Phase1_Local --> MigrationPrep : ユーザーがクラウド同期を有効化

    MigrationPrep --> Phase2_Cloud : OAuth 認証成功 + 初回 sync 完了
    MigrationPrep --> Phase1_Local : キャンセル / 認証失敗

    Phase2_Cloud --> Phase2_Cloud : 通常運用<br/>ローカル + クラウド両系
    Phase2_Cloud --> Phase1_Local : ユーザーがクラウド無効化（ローカル維持）

    note right of Phase1_Local
        全データは端末のみ
        オフライン完結
    end note

    note right of Phase2_Cloud
        ローカル primary + クラウド sync
        eventual consistency 許容
    end note
```

### 不変条件

- フェーズ移行は**ユーザー明示操作**のみ（自動移行禁止）
- ローカル data は移行後も**消えない**（クラウドはミラー）
- Phase 2 → Phase 1 ダウングレード時、ローカルデータは保持
