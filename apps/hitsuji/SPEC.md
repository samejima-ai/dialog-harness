# Hitsuji — 機能仕様

## WHY（なぜ作るのか）

ADHD 傾向のある人は、注意欠損や多動的な思考から「コト（やること・約束）」を忘れやすい。
通知が散らばっていると逆に脳がパンクするため、**あちこちから集めて、ひとつの場所でしつこく教えてくれる**ツールが必要。
叱責より報酬の方が脳が動くため、**ゲーミフィケーション**で「続けたくなる」体験を提供する。

## 対象ユーザー

- ADHD 傾向の本人（最初は開発者自身、自分専用ツール）
- 単一ユーザー前提（複数人共有・権限分離は **DONT**）

---

## WHAT（機能一覧と条件）

### F1. タスク（やること）の登録と通知 — **critical**

「薬を飲む」「メール返信」「ゴミ出し」のような **アクション系**を登録し、指定時刻に通知する。

| 条件 | 値 |
|---|---|
| 登録方法 | 音声入力（primary）/ カレンダー取り込み / メッセージ取り込み / メール取り込み / 手動 1 タップ |
| 通知タイミング | 単発時刻指定 / 毎日 / 毎週 / カスタム繰り返し |
| 完了アクション | 通知から **3 タップ以内**で「完了」 / 「Snooze（5min / 15min / 1h）」 |
| 同時保持タスク数 | 上限なし（個人利用想定） |
| 過去タスク保持 | 完了 / 期限切れタスクは 90 日間保持後アーカイブ |

### F2. 予定（時刻系）の登録と通知 — **critical**

「14:00 から会議」「金曜 18:00 友達と約束」のような **時刻拘束系**を登録し、リマインドする。

| 条件 | 値 |
|---|---|
| 登録方法 | F1 と同じ（音声・カレンダー連携が主軸） |
| リマインドタイミング | 15 分前 / 5 分前 / 開始時刻（既定。タスクごとに調整可） |
| Google カレンダー双方向同期 | **読み取り** primary、書き込みは将来拡張 |

### F3. しつこい段階的エスカレーション通知 — **critical**

通知を 1 回出して終わりではなく、無視した時間に応じて**強度を上げて**追いかける。

| 段階 | 経過時間 | 挙動 |
|---|---|---|
| Lv.1 やさしく | 通知時刻 +0 分 | 通常プッシュ + 穏やかな色（プライマリブルー） |
| Lv.2 ふつう | +5 分 | 再通知 + バイブ強化 + アンバー色 |
| Lv.3 強め | +15 分 | 再通知 + 赤色 + 強いバイブ + 音量増 |
| Lv.4 アラーム | +30 分 | フルスクリーンインテント（画面占拠）+ アラーム音継続 |

- ユーザー操作（完了 / Snooze）で即時停止
- タスクごとに最大段階を設定可能（重要度に応じて Lv.2 で止める等）
- 既定は **全タスクで Lv.4 まで**（ADHD 当事者の特性に合わせた強気初期値）

### F4. 自動取り込み（α 入力経路）— **standard**

外部ソースから予定・タスクを自動取り込みする。**MVP では音声 + Google カレンダー**、他は段階的に追加。

| ソース | 優先度 | 取り込み方式 | MVP |
|---|---|---|---|
| 音声入力（"明日 10 時に薬"） | **primary** | Android `SpeechRecognizer` → NLP パース → タスク化 | ○ |
| Google カレンダー | high | Calendar Provider 読み取り or Google Calendar API | ○ |
| LINE / メッセージアプリ | medium | NotificationListenerService で受信通知から抽出 | ✗（拡張） |
| Gmail | low | Gmail API（OAuth）+ 件名・本文パターンマッチ | ✗（拡張） |

### F5. 手動登録（β 入力経路）— **critical**

1 タップ + 最小入力で即登録できる UI。

| 条件 | 値 |
|---|---|
| 登録までの操作数 | **3 タップ以内**（FAB → 入力 → 確定） |
| 入力モード | 音声 / テキスト / クイックテンプレート（"薬" "ゴミ出し" 等のショートカット） |
| 処理 | **完全非同期**（UI ブロックなし、楽観的更新） |

### F6. ゲーミフィケーション — **standard**

「続けたくなる」ための短期報酬と視覚的成長。

| 要素 | 仕様 |
|---|---|
| スコア | タスク完了 +10pt、定時完了（通知 +5 分以内）+5pt ボーナス |
| 連続日数（ストリーク） | 1 日 1 件以上完了で +1 日、0 件の日でリセット |
| バッジ | 連続 3 日 / 7 日 / 30 日 / 100 日、累計 100pt / 1000pt / 10000pt 等のマイルストーン |
| 表示 | ホーム画面に「今日のスコア」「連続日数」「次のバッジまで」を常時表示 |
| ペナルティ | **なし**（叱責は逆効果、未完了でも 0pt 加算するだけ） |

### F7. データ保管（フェーズ進化型）— **critical**

| フェーズ | 保管先 | 移行条件 |
|---|---|---|
| Phase 1（MVP） | **端末ローカル**（Room / SQLite） | デフォルト |
| Phase 2（将来） | **クラウド同期オプション**（Firebase / 自前サーバ） | ユーザーが明示的に有効化 |

データモデルは Phase 2 への移行を想定し、UUID + updated_at を最初から保持する（**schema-evolution.md** 準拠）。

---

## UX 制約（Must 閾値）

| 項目 | 値 | 根拠 |
|---|---|---|
| タスク登録完了までの操作数 | **3 タップ以内** | ユーザー Must（無駄が嫌い） |
| 通知タップから完了までの操作数 | **1 タップ** | ADHD 当事者の即応性 |
| 画面表示までの応答時間 | p95 **300 ms 以内** | 「待ち時間嫌い」、Android Vitals 基準 |
| バックグラウンド処理 | **完全非同期**（UI ブロックなし） | ユーザー Must |
| 主要タスクへの到達クリック数 | **3 クリック以内** | 業界標準 |
| 完了率 | **95% 以上** | 業界標準 |

---

## ドメインモデル（L0-2 縮退記述）

> Kotlin Native プロジェクトのため、TypeScript/Zod ではなく Kotlin の `data class` を想定した概念モデルを Markdown で記述する。詳細は ADR-001 参照。

### Task（タスク・予定の統合エンティティ）

```
Task {
  id: UUID                  // 不変
  title: String             // 必須、表示用
  description: String?      // 任意
  type: TaskType            // [TASK | EVENT]  TASK=やること, EVENT=時刻拘束
  scheduled_at: Instant     // 通知/予定時刻
  recurrence: Recurrence?   // 繰り返し（null=単発）
  source: TaskSource        // [VOICE | CALENDAR | MESSAGE | EMAIL | MANUAL]
  escalation_max: EscalationLevel  // 既定 LV4
  status: TaskStatus        // [PENDING | NOTIFYING | ESCALATING | COMPLETED | SNOOZED | EXPIRED | ARCHIVED]
  completed_at: Instant?
  score_earned: Int         // 完了時のみ確定
  created_at: Instant
  updated_at: Instant       // schema-evolution 対応
}
```

### NotificationState（通知エスカレーション状態）

```
NotificationState {
  task_id: UUID
  current_level: EscalationLevel  // [LV1 | LV2 | LV3 | LV4]
  next_fire_at: Instant
  fired_count: Int
}
```

### ScoreLedger（ゲーミフィケーション台帳）

```
ScoreLedger {
  id: UUID
  task_id: UUID
  points: Int
  earned_at: Instant
  reason: ScoreReason       // [COMPLETION | ONTIME_BONUS | STREAK_MILESTONE | BADGE_UNLOCK]
}
```

### Streak（連続日数）

```
Streak {
  current_days: Int
  longest_days: Int
  last_completion_date: LocalDate
}
```

---

## 外部 API 連携（L0-3 縮退記述）

| 連携先 | 用途 | 必要パーミッション / 認証 | MVP |
|---|---|---|---|
| Android `SpeechRecognizer` | 音声入力 | `RECORD_AUDIO` (runtime, dangerous) | ○ |
| Android `CalendarContract` | カレンダー読み取り | `READ_CALENDAR` (runtime, dangerous) | ○ |
| Android `NotificationManager` | プッシュ通知発行 | `POST_NOTIFICATIONS` (Android 13+ runtime, dangerous) | ○ |
| Android `AlarmManager`（exact） | エスカレーション再発火（厳密時刻） | Android 12+: `SCHEDULE_EXACT_ALARM` (special access) / Android 13+ では `USE_EXACT_ALARM`（install-time、ヘルスケア・アラーム系のユースケースのみ許容） | ○ |
| Android Full-screen intent | Lv.4 アラーム時の画面占拠 | `USE_FULL_SCREEN_INTENT`（Android 14+ で user toggle 可、初回確認 UX が必要） | ○ |
| Android `WorkManager` | バックグラウンドジョブ（取り込みポーリング等） | 標準。長時間処理は `FOREGROUND_SERVICE` + `FOREGROUND_SERVICE_DATA_SYNC` 等を併用 | ○ |
| Android `Vibrator` / `VibratorManager` | 段階別バイブ | （標準、`VIBRATE`） | ○ |
| Google Calendar API（REST） | クラウド予定取得（端末カレンダーで足りない場合のみ）| OAuth 2.0 (`GoogleSignIn` + Calendar scope) | △（高度同期時） |
| `NotificationListenerService` | LINE 等の受信通知抽出 | `BIND_NOTIFICATION_LISTENER_SERVICE`（システム grant、設定アプリで個別許可必須） | ✗（拡張） |
| Gmail API | メール本文からのタスク抽出 | OAuth 2.0 (Gmail.readonly scope) | ✗（拡張） |

### パーミッション請求 UX

初回起動時に **段階的かつ目的説明付き**で請求する（ADHD 当事者向け UX として、不意打ち権限ダイアログは避ける）：

1. アプリ起動 → オンボーディング画面で「Hitsuji は通知でやることを思い出させます」と説明
2. `POST_NOTIFICATIONS`（通知許可）を最初に請求 — これがないと機能が成立しない
3. `RECORD_AUDIO` は **音声入力ボタンを初めて押した時**に請求（事前請求しない）
4. `READ_CALENDAR` は **カレンダー連携をオンにした時**に請求
5. `SCHEDULE_EXACT_ALARM` / `USE_FULL_SCREEN_INTENT` は **エスカレーション設定画面**で意義を説明してから請求

権限拒否時の挙動：
- `POST_NOTIFICATIONS` 拒否 → アプリ本来機能不全のため、設定遷移を促す画面表示
- `RECORD_AUDIO` 拒否 → 音声入力 UI を disable、テキスト入力にフォールバック
- `READ_CALENDAR` 拒否 → カレンダー連携を disable、手動登録のみ
- exact alarm / full-screen intent 拒否 → エスカレーション最大段階を Lv.3 に制限

---

## 優先順位（critical / standard / cosmetic）

| 優先度 | 機能 |
|---|---|
| critical | F1, F2, F3, F5, F7 |
| standard | F4, F6 |
| cosmetic | （DESIGN.md でのアニメーション・トランジション類） |

---

## 非機能要件（NFR スコアと整合）

| カテゴリ | スコア | 要求 |
|---|---|---|
| 応答性 (latency) | 3 | UI 操作 p95 300ms、登録は非同期化 |
| 信頼性 (reliability) | 2 | 通知の取りこぼし許容率 < 1%、端末再起動後も復元 |
| 保守性 (maintainability) | 2 | Phase 2 でクラウド移行可能なスキーマ進化対応 |
| 規模 (scale) | 0 | 自分専用 1 ユーザー |
| セキュリティ | 1 | ローカル先行、Phase 2 でクラウド時に E2E 検討 |

---

## 制約・前提

- **Android 一択**（iOS / デスクトップは DONT）
- **Wear OS 連携は将来視野**（MVP には含めない）
- **オフライン動作を MVP の必須要件とする**（音声認識のみクラウド経由を許容）
- **データ保管は Phase 1 ローカルのみ**（Phase 2 移行は明示的なユーザー選択）

---

## 参照

### 本 PR で生成済み

- 視覚仕様: `DESIGN.md`
- スコープ外定義: `DONT.md`
- モード判定: `REGIME.md`
- 全体目次: `INDEX.md`
- 状態遷移図: `spec/state-diagrams.md`
- 不変条件: `spec/invariants.feature`
- サブフェーズ判定: `spec/subphase-manifest.md`
- 縮退判断: `delivery/ADR-001-subphase-scope.md`
- エージェント RL: `CLAUDE.md`
- センサー類: `sensors/computational.md` / `sensors/inferential.md` / `sensors/review-checklist.md`
- 自己検証結果: `delivery/SELF-VERIFICATION-INITIAL.md`
- Android scaffold: `android/`
