---
name: layer0-onboarding
dimension: D4
description: >
  既存プロジェクトから仕様書を抽出したい場合、または dialog-harness-layers を後付け導入して
  AI 自律開発に移行したい場合に起動する L0 兄弟スキル（reverse-spec & 後付け harness 化）。
  「既存プロジェクトを harness 化したい」「このコードベースに dialog-harness-layers を入れたい」
  「レガシーに仕様書が欲しい」「既存コードから仕様書を抽出したい」「逆仕様化したい」
  「後付けで onboarding したい」等、既に動いているコード・既に存在するプロジェクトへの
  仕様書化または harness 導入依頼でトリガーする。
  新規プロジェクトの立ち上げ（spec-architect の責務）や、継続開発の仕様策定ではトリガーしない。
  使い捨てスキル：1 プロジェクトにつき最大 1 回のみ起動する。
  完了後は REGIME.md に onboarded_at を記録し、以降は spec-architect に引き継ぐ。
---

# Onboarding

既存プロジェクトに dialog-harness-layers を後付け導入するための使い捨て L0 兄弟スキル。

## 原則

- **使い捨て**: 1 プロジェクトにつき最大 1 回のみ起動。完了後は REGIME.md に `onboarded_at: YYYY-MM-DD` を記録し再起動禁止
- **L0 兄弟（L3 ではない）**: 運用層として新設するものではない。spec-architect と並ぶ L0 の第 2 スキル
- **非破壊**: 既存コード・既存ドキュメント・既存の開発フローを破壊しない。抽出と記述のみを行う
- **AI 協働・人間ボトルネック最小**: 人間の手を動かさない。承認のみ
- **フラクタル整合**: L0⇄人間 / L1 spec⇄code / L2⇄L1群 の同一形状を onboarding にも適用する（人間イメージ→AI 構造化→人間承認）
- **振る舞い凍結 / コード凍結の二段構え**: デフォルトは振る舞い凍結のみ。コード凍結は AI 判断 + 人間ボトルネック確認で発動

## 発動条件（厳格）

**以下全てを満たす場合のみ発動**:

- 対象プロジェクトに INDEX.md / SPEC.md / DONT.md / REGIME.md が**いずれも存在しない**
- 既存コード・既存ドキュメント・既存 git 履歴が存在する（空リポジトリではない）
- 人間が「既存プロジェクトに harness を入れたい」旨を明示

**発動してはいけないケース**:

- 上記規格ファイルのいずれかが既に存在する → spec-architect へ差し戻し（Lifecycle ≥ 1 として処理）
- REGIME.md に `onboarded_at` 記録がある → 既に onboarding 済み、再起動禁止
- 新規プロジェクト（コードが空） → spec-architect へ差し戻し

## 処理フロー

```
1. 発動条件チェック（既存ファイル・git 履歴・onboarded_at マーカー確認）
2. Archaeology（考古学的抽出）
   2.1. 深度判定（shallow / standard / deep / full）
   2.2. 人間との対話深度合意
   2.3. コード・既存ドキュメント・git log からの事実抽出
3. 凍結線の合意（Freeze Line）
   3.1. 振る舞い凍結をデフォルト提示
   3.2. AI がコード凍結が必要と判断した場合のみ人間ボトルネック確認
4. 逆仕様化（Reverse Spec）
   4.1. as-is / to-be を分離して SPEC.md を生成
   4.2. F 番号採番（既存機能を F1 から順番に）
   4.3. 確度メタデータ付与（AI 推定 / コード確認 / 人間確定）
5. DONT.md 生成（凍結線・抽出不能領域・既存バグ許容範囲）
6. REGIME.md 生成（初期 Lifecycle L=1・onboarded_at 記録・モードは暫定 M2）
7. 人間承認（SPEC/DONT/REGIME のレビュー）
8. spec-architect への引き継ぎ（handoff-to-spec-architect.md 準拠）
9. 自身の停止（onboarded_at 記録により再起動禁止）
```

## 入力

- プロジェクトルートへのアクセス
- 既存コード（src/, tests/, config 等）
- 既存ドキュメント（README.md, docs/, wiki 等）
- git log / git blame 履歴
- 人間からの深度指示（shallow / standard / deep / full）と凍結線ヒアリング

## 出力

- `SPEC.md` — 逆仕様化された機能仕様（as-is 中心、to-be は最小限）
- `DONT.md` — 凍結線と抽出不能領域
- `REGIME.md` — `onboarded_at`, `Lifecycle: L=1`, 暫定モード, Archaeology 深度記録
- `INTENT.md`（history/ 配下） — F 番号ごとの意図・条件・確度メタデータ
- `CLAUDE.md`（最小版） — 以降の spec-architect が拡張する土台
- README.md 末尾のクレジット（credit-template.md 準拠、拒否権あり）

## 抽出例（standard 深度）

既存の Python Flask アプリから抽出した SPEC.md の冒頭イメージ（確度メタデータ付き）:

```markdown
## F1. ユーザー登録
- **条件**: email 一意、パスワード 8 文字以上、bcrypt ハッシュ化
- **Priority**: critical
- **確度**: コード確認（src/auth/register.py:42-78）

## F2. ログイン
- **条件**: セッション有効期限 24h、失敗 5 回で 15 分ロック
- **Priority**: critical
- **確度**: コード確認 + git log 追認（commit a1b2c3d）

## F3. プロフィール画像アップロード
- **条件**: JPEG/PNG のみ、2MB 上限、S3 保存
- **Priority**: standard
- **確度**: AI 推定（tests/test_profile.py から推測、人間承認待ち）
```

確度 3 段階（AI 推定 / コード確認 / 人間確定）は後続の spec-architect が追認時に参照する。`Priority` は `../layer0-spec-architect/references/philosophy.md` §第3条に準拠。

## 参照ドキュメント

- `references/archaeology-protocol.md` — 考古学的抽出プロトコル（深度 shallow/standard/deep/full、対話深度判定、抽出フォーマット、機密領域の扱い）
- `references/freeze-line-spec.md` — 凍結線の二段構え規格（振る舞い凍結 / コード凍結、AI 献上フォーマット、DONT.md 記載形式、違反時の処理）
- `references/handoff-to-spec-architect.md` — 引き継ぎ規格（タイミング、REGIME.md 特記事項、INTENT.md 初期状態、spec-architect 側の責務、再起動防止）

## アセット（埋めて使うテンプレート）

- `assets/reverse-spec-template.md` — 逆仕様化テンプレート（as-is/to-be 分離、F 番号採番、INTENT.md 展開、確度メタデータ）

## Level A 所属

本 skill は dialog-harness-layers 本体のもの。プロジェクトごとに再生成しない。プロジェクト差異は抽出対象と深度指示に閉じる。

## 設計上の注意

- **spec-architect との責務分離**: onboarding は抽出のみ。新機能追加・仕様改変は spec-architect に委譲する
- **人間を疲弊させない**: 深度 deep/full の発動は人間から明示同意があった場合のみ。デフォルト standard
- **AI 推定の明示**: 確度メタデータを必ず付与。後続の spec-architect がレビュー時に追認できる状態を作る
- **再起動防止**: `onboarded_at` は REGIME.md の最上部（モード記録より先）に配置し、誤起動を物理的に防ぐ
