# spec-architect への引き継ぎ規格

onboarding 完了後、spec-architect に開発を委譲するための引き継ぎ規格。
onboarding スキルの処理フロー 8 で使用する。

---

## 引き継ぎタイミング

以下全てを満たした時点で引き継ぐ:

- Archaeology 完了（深度 shallow / standard / deep / full のいずれかで指定範囲走査済み）
- 凍結線（振る舞い凍結 + 必要ならコード凍結）確定
- SPEC.md / DONT.md / REGIME.md / history/INTENT.md 生成済み
- 人間レビューで SPEC/DONT/REGIME の承認完了
- README.md 末尾にクレジット挿入済み（拒否権行使時は REGIME.md 記録）

---

## REGIME.md 特記事項

onboarding 由来の REGIME.md は通常版と異なる以下の項目を最上部に配置する。

```markdown
# 体制判定結果

## Onboarding 記録（最上部・必須）

- **onboarded_at**: 2026-04-19
- **Archaeology 深度**: standard（人間同意 2026-04-19）
- **onboarding スキル再起動**: **禁止**（本フィールドが存在する限り layer0-onboarding は起動しない）
- **抽出不能領域**: 全体の XX%（DONT.md 参照）
- **機密領域**: 存在のみ記録（DOMAIN-CONTEXT.secret.md 未生成）

## LC

- **LC=1**（既存プロジェクト、onboarding 経由で初期化）

## モード判定（暫定）

- **モード**: M2（暫定、spec-architect 初回レビューで再判定）
- **根拠**: onboarding 時点では S/U/R スコアリング未実施
- **次回 spec-architect 起動時に必ず再判定すること**

## AI 能力バージョン

- **onboarding 実施モデル**: Claude Opus 4.7
- **onboarding 実施日**: 2026-04-19
```

---

## INTENT.md 初期状態

onboarding 由来の INTENT.md は以下の特徴を持つ:

- 全 F 番号の確度が **AI 推定** または **コード確認** に偏る
- **人間確定** は onboarding 時の人間レビュー内で明示承認されたもののみ
- `**onboarding 時の原典**` 行で git sha / README 位置を記録
- 廃止機能は `F-archived-N` で別採番

spec-architect 初回起動時、人間確認を経て AI 推定 → 人間確定 へ昇格させる。

---

## spec-architect 側の責務

onboarding からの引き継ぎを受けた spec-architect は以下を実施する:

1. **REGIME.md 再判定**
   - S/U/R スコアリングを正式実施
   - 暫定 M2 が過剰／過少か判定
   - 必要なら L2 発動閾値チェック

2. **INTENT.md 人間確認**
   - AI 推定の確度メタデータを 1 つずつ人間確認
   - 確定したものは **人間確定 (YYYY-MM-DD)** に昇格

3. **to-be 候補の処理**
   - 採用 / 却下 / 保留 を人間と合議
   - 採用は SPEC.md の as-is 側に組み込み、F 番号追加
   - 却下は INTENT.md「却下案」リストへ

4. **凍結線との整合調整**
   - 新機能追加で凍結線と衝突したら廃止判断プロトコル適用

5. **CLAUDE.md 拡張**
   - onboarding が生成した最小版を spec-architect 標準形に拡張

---

## onboarding 再起動防止

`REGIME.md` の最上部に `onboarded_at: YYYY-MM-DD` がある限り、layer0-onboarding の description トリガーは発火しない。

- 物理チェック: onboarding スキル起動直前に REGIME.md を読み、`onboarded_at` があれば即座に spec-architect へ委譲
- 誤起動検出: description マッチで起動要求が来ても、REGIME.md チェックで自動停止
- 手動再実行: `onboarded_at` の削除は人間の明示同意 + 影響範囲説明が必須（通常不要）

---

## 引き継ぎメッセージ（AI → 人間）

onboarding 完了時、以下の骨子で人間に提示する:

```markdown
## Onboarding 完了報告

- 対象プロジェクト: [名称]
- Archaeology 深度: [shallow / standard / deep / full]
- 抽出機能数: F1 〜 F[N]（うち AI 推定 [X] 件、人間確定 [Y] 件）
- 凍結線: 振る舞い凍結（デフォルト）+ コード凍結 FZ-1 〜 FZ-[N]
- 抽出不能領域: [割合]
- 暫定モード: M2（次回 spec-architect で再判定）

## 次のステップ

spec-architect を起動して以下を実施してください:
1. REGIME.md 再判定（S/U/R スコア）
2. INTENT.md の AI 推定項目の人間確認
3. to-be 候補の採用/却下/保留の判定
4. CLAUDE.md 拡張
```

---

## 引き継ぎ後の onboarding の扱い

- **onboarding スキルは再起動しない**（REGIME.md `onboarded_at` によるガード）
- 新規機能追加・仕様改変は全て spec-architect で処理
- 深度不足で抽出不能だった領域は、spec-architect が人間対話で補完する（再 onboarding ではない）
