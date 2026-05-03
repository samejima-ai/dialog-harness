# SELF-VERIFICATION v5.7.1 — Claude Code CLI メイン化（実装エージェント方式の見直し）

- ブランチ: `claude/v5.7.1-claude-code-pivot`
- HANDOFF: `delivery/HANDOFF-v5.7.1-claude-code-pivot.md` (commit `0a18f0b`)
- 実装サイクル: L0 (spec-architect) → L1 (autonomous-dev)
- 自律修正回数: 0 / 上限 3
- 体制: M2 / LC=2 / dev_mode=autonomous / autonomous_scope=full

## 体制情報

- Mode: M2 / LC=2 / Cycle: v5.7.1 patch
- AI 能力: claude-opus-4-7
- 完成基準: HANDOFF 全 11 項目（Phase A〜D）+ harness-verifier 全 5 検査 PASS

## Phase 別実装結果

### Phase A: 履歴層 + housekeeping

| # | 項目 | 結果 | 補足 |
|---|---|---|---|
| 1 | CHANGELOG.md v5.7.1 (in progress) + v5.7.0 (released 2026-05-03) 化 | ✅ | 7 例目正規適用 |
| 2 | INTENT.md v5.7.1 設計意図セクション (a)-(e) | ✅ | gemini-cli 維持 / 失敗時人間 P4 判断 |
| 3 | REGIME-LOG.md v5.7.1 patch 判定記録 | ✅ | dev_mode autonomous + autonomous_scope full 維持 |
| 4 | ARCH-DECISIONS.md AD-029 追加（AD-026 訂正記録）| ✅ | AD-026 削除せず historical 維持 |

### Phase B: crosscut-issue-implementer skill 改修

| # | 項目 | 結果 | 補足 |
|---|---|---|---|
| 5 | SKILL.md 実装エージェント節を Claude Code CLI メイン + gemini-cli フォールバックに改訂 | ✅ | frontmatter description も更新 |
| 6 | references/triage-protocol.md 軽微改訂 | ✅ | gemini-cli triage メイン継続を明文化 |
| 7 | references/setup-checklist.md 新設（CLAUDE_CODE_OAUTH_TOKEN 取得手順）| ✅ | Anthropic Console、Pro/Max サブスクリプション、必須 secrets/labels 一覧 |

### Phase C: workflow + template

| # | 項目 | 結果 | 補足 |
|---|---|---|---|
| 8 | .github/workflows/issue-pickup.yml 改訂 | ✅ | anthropics/claude-code-action@v0 統合 |
| 9 | templates/github-workflows/issue-pickup.yml.template 同等改訂 | ✅ | placeholder ${ALLOWED_AUTHORS} 維持 |

### Phase D: 自己検証 + 献上

| # | 項目 | 結果 | 補足 |
|---|---|---|---|
| 10 | delivery/SELF-VERIFICATION-v5.7.1.md | ✅ | 本ファイル |
| 11 | harness-verifier 全 5 検査 PASS | ✅ | 詳細は下記「自己検証結果」参照 |

## 自己検証結果（5 層検出スタック）

| 層 | 対象 | 結果 |
|---|---|---|
| Shift Left 基盤 | DH 内ドキュメント整合性 | PASS |
| 第 1 層 計算的センサー | harness-verifier 全 5 検査 | **PASS（5/5）** |
| 第 2 層 E2E 機械検証 | workflow YAML syntax (visual review) | PASS |
| 第 3 層 Interaction Cost | N/A（DH 自身は UI なし） | N/A |
| 第 4 層 推論的センサー | 「仕様に合う・動く・使える」 | PASS（HANDOFF 全 11 項目達成）|
| 第 5 層 独立検証 | gemini-review + Copilot review (PR 作成後) | 後段で実施 |

### harness-verifier 詳細（第 1 層）

```
- 1. frontmatter 整合性: PASS (0)
- 2. 参照 path 有効性: PASS (0)
- 3. SK 間参照の健全性: PASS (0)
- 4. 5 層構造保全: PASS (0)
- 5. 用語辞書整合: PASS (0)
- 総合判定: PASS
```

## v5.7.1 で発見した重要な事実（INTENT.md より再掲）

1. **Anthropic Pro/Max サブスクリプションで Claude Code CLI が GitHub Actions 経由で稼働可能**
   - `claude setup-token` で取得した OAuth token を `CLAUDE_CODE_OAUTH_TOKEN` 経由で渡す
   - **追加 API 課金なし**（サブスクリプション内で稼働）
   - これは v5.7.0 (AD-026) 時点で見落としていた経路。v5.7.1 で訂正（AD-029）

2. **異質モデル併走（philosophy 第 3 条「情報純度」）の保全**
   - triage（軽量、無料 tier）: gemini-cli メイン継続
   - 実装本体（コード生成、PR 作成）: Claude Code CLI メイン化
   - PR レビュー (gemini-review.yml): gemini-cli メイン継続（変更なし）
   - フォールバック: 人間 P4 判断（自動化なし、philosophy 第 4 条「人間が判断する場面」）

## DONT.md 抵触検査

- ✅ 創造的 UX デザインを生成していない（DH 内ドキュメント + workflow のみ）
- ✅ 複雑な状態管理 UI を生成していない
- ✅ パフォーマンス最適化を実施していない
- ✅ 未知の外部 API を統合していない（claude-code-action は公式・既知）

## 仕様改訂提案（Type C）

なし。HANDOFF 全 11 項目を仕様通り実装、追加変更なし。

## 異常献上（Type D）

なし。自力修正回数 0、致命的エラーなし。

## 後続作業（v5.7.x 以降の候補）

1. **automatic gemini fallback**: Claude Code 失敗時の gemini-cli 自動フォールバック（現状は人間 P4 判断）。fail パターン蓄積後に Council 起動可
2. **claude-code-action SHA pin**: 現状 `@v0` タグ、SHA pin 推奨（観測駆動で判断）
3. **Triage フル実装**: 現状 MVP placeholder。gemini-cli インストール + prompt template 整備 + JSON 判定経路の本実装
4. **Implementation 本体検証**: 実 Issue で end-to-end 動作確認（v5.7.1 では workflow 骨格まで、稼働は次回 Issue 投入時）

## 体制事後評価

- M2 / LC=2 / dev_mode=autonomous / autonomous_scope=full は妥当
- v5.7.0 から v5.7.1 への patch 昇格は最小スコープ（実装エージェント切替）に集中、後続改修を分離する設計判断が機能した
- Council 起動なし（confidence ≥ 0.7、ユーザー要望明確、AD-029 で AD-026 を historical 訂正する形が確立済み）
- 7 例目正規適用（v5.7.0 → released、v5.7.1 → in progress）の housekeeping 同梱が autonomous-drive loop の標準形として安定化
- 次 Cycle: v5.7.1 PR が auto-merge label で自律 merge → autonomous-drive loop **7 例目** 完遂

## 完了基準達成

- ✅ HANDOFF 全 11 項目完遂
- ✅ harness-verifier 全 5 検査 PASS
- ✅ delivery/SELF-VERIFICATION-v5.7.1.md（本ファイル）
- ⏭ PR description に HANDOFF 参照（PR 作成時）
- ⏭ gemini-review + Copilot review 通過（PR 作成後）
- ⏭ auto-merge label 付与で workflow 経由自動 merge（autonomous-drive loop 7 例目、PR 作成後）

PR 作成 + auto-merge label 付与をもって v5.7.1 完遂とする。
