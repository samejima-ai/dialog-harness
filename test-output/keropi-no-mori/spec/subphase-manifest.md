# spec/subphase-manifest.md — サブフェーズ選定結果

L0 ステップ 3.5 で決定したサブフェーズ起動状況。Phase 2 で REGIME.md に統合予定（pre-official）。

## 基本 5 問の判定結果

| # | 質問 | 答え | 起動 |
|---|---|---|---|
| S1 | データを保存する必要があるか？ DB を使うか？ | ✅ Yes（妹の絵 / 進捗 / 図鑑 / 問題プール / ケロぴ状態） | **L0-2 起動** |
| S2 | 外部のシステムや API とつなぐか？ | ✅ Yes（Google Sheets API + Gemini API） | **L0-3 起動** |
| S3 | 画面はいくつあるか？ 遷移は複雑か？ | ✅ Yes（7-8 画面、待ち時間サブ状態あり） | **L0-4 起動** |
| S4 | 複数ユーザーで使うか？ 権限の違いはあるか？ | ❌ No（n=1） | **L0-5 スキップ** |
| S5 | 時間経過や承認で状態が自動的に変わるか？ | △ 限定的（季節感は Phase 1.2 以降） | **L0-6 簡易モード起動**（2 以上のサブフェーズ起動条件 ✅） |

## 起動サブフェーズ一覧

| サブフェーズ | モード | 成果物 | 確度 |
|---|---|---|---|
| **L0-2 ドメインモデル** | 完全 | `spec/domain.ts`（Zod + TypeScript） | 高 |
| **L0-3 API 契約** | 簡易 | `spec/api-signatures.ts` | 高（外部 API 利用のみ、自前 API 設計なし） |
| **L0-4 状態遷移** | 完全 | `spec/state-machine.ts` + `spec/state-diagrams.md` | 高 |
| **L0-5 認可** | スキップ | — | — |
| **L0-6 層間不変条件** | 簡易 | `spec/invariants.feature`（Happy / Sad / Evil 各 1 シナリオ） | 中（妹さん体験の核を不変条件化） |

## 依存順

```
L0-1 (機能仕様, SPEC.md) ✅ 完了
   ↓
L0-2 (ドメインモデル) ⬇ 起動
   ↓
L0-3 (API 契約) ‖ L0-4 (状態遷移) ⬇ 並列起動
   ↓
L0-6 (層間不変条件) ⬇ 起動
```

L0-5（認可）はスキップのため依存順から外れる。

## 起動ログ

| 日時 | サブフェーズ | アクション |
|---|---|---|
| 2026-04-28 | L0-2 | 完全モードで起動。Problem / Drawing / Judgement / Reaction / Character / Dex / Scroll / Session を定義 |
| 2026-04-28 | L0-3 | 簡易モードで起動。Sheets fetch + Gemini call の signature 化 |
| 2026-04-28 | L0-4 | 完全モードで起動。Top-level + drawing sub-machine + waiting sub-machine |
| 2026-04-28 | L0-6 | 簡易モードで起動。Happy（描いて喜ぶ）/ Sad（API 失敗）/ Evil（不適切な入力）の 3 シナリオ |

## 事後追加の予定

| サブフェーズ | トリガー | 想定タイミング |
|---|---|---|
| L0-5 認可 | 複数家族メンバー（親 / 妻 / 自分）で進捗管理が必要になったら起動 | Phase 1.5 以降 |
| L0-6 完全モード昇格 | Phase 2.0（他教科拡張）で不変条件が増えたら | Phase 2 立ち上げ時 |

事後追加は独立 AI 呼び出しで実行（共通 skill `references/subphase-selection.md` 「事後追加プロトコル」準拠）。
