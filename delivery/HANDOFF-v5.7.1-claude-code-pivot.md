# HANDOFF: v5.7.1 実装エージェント方式の見直し（Claude Code CLI メイン化）

**作成日**: 2026-05-03
**作成元**: layer0-spec-architect（本セッションで起動）
**譲渡先**: layer1-autonomous-dev
**起源**: ユーザー要請「実装は Anthropic Claude Code CLI で実行したい、サブスクで稼働、Gemini はフォールバック」
**Council 諮問**: なし（confidence ≥ 0.7、ユーザー要望明確、複数案拮抗なし）

---

## スコープ判定

- **昇格**: v5.7.0 → **v5.7.1 patch**（後方互換完全維持、philosophy.md 改訂なし、AD 1 件追加）
- **同梱**: v5.7.0 (in progress) → (released 2026-05-03) 化（**7 例目正規適用**）
- **API 課金**: 引き続き回避（OAuth token 経路で Pro/Max サブスクリプション利用、追加課金なし）

## 7 論点 確定

| # | 論点 | 確定 |
|---|---|---|
| 1 | 昇格判定 | **v5.7.1 patch**（実装手段差し替え、SPEC 改修範囲限定）|
| 2 | OAuth token 取得 | ユーザー側で Anthropic Console から発行（保有確認済）→ Repository Secret `CLAUDE_CODE_OAUTH_TOKEN` 設定 |
| 3 | フォールバック設計 | **人間 P4 判断**（Claude Code action 失敗 → label `pickup-failed` + notice → 人間が gemini で再 trigger）|
| 4 | Circuit Breaker | 据え置き（日次 5 / 月次 50）|
| 5 | gemini-cli の継続用途 | AI triage = メイン維持、実装エージェント = フォールバック、gemini-review.yml = 変更なし |
| 6 | MVP → 完全実装 | v5.7.1 では Claude Code action 統合のみ（実装本体の MVP 卒業の入口）。完全実装は v5.7.x 別 patch、観測駆動 |
| 7 | Council 諮問 | 不要 |

## 実装スコープ Phase A〜D（全 11 項目）

### Phase A: 履歴層 + housekeeping (4 項目)

1. `history/CHANGELOG.md` v5.7.1 (in progress) + v5.7.0 (released 2026-05-03) 化（7 例目正規適用）
2. `history/INTENT.md` v5.7.1 設計意図セクション
3. `history/REGIME-LOG.md` v5.7.1 patch 判定記録
4. `history/ARCH-DECISIONS.md` AD-029 追加（Claude Code CLI 採用 + AD-026 訂正記録）

### Phase B: crosscut-issue-implementer skill 改修 (3 項目)

5. `SKILL.md` 改訂（実装エージェントを「Claude Code CLI メイン + gemini-cli フォールバック」へ。triage は gemini-cli 維持）
6. `references/triage-protocol.md` 軽微改訂（triage は gemini-cli 維持を明文化）
7. `references/setup-checklist.md` `CLAUDE_CODE_OAUTH_TOKEN` 取得手順追加（Anthropic Console、Pro/Max サブスクリプション前提）

### Phase C: workflow + template 改修 (2 項目)

8. `.github/workflows/issue-pickup.yml` 改訂
   - `anthropics/claude-code-action@v0` 統合
   - `CLAUDE_CODE_OAUTH_TOKEN` 認証
   - 失敗時 → label `pickup-failed` + notice（**フォールバック自動化はしない、人間 P4 判断**）
   - triage 部分は gemini-cli 維持
9. `templates/github-workflows/issue-pickup.yml.template` 同等改訂

### Phase D: 自己検証 + 献上 (2 項目)

10. `delivery/SELF-VERIFICATION-v5.7.1.md`
11. `python harness-verifier/verify.py` 全 5 検査 PASS

---

## 重要な実装制約

### 1. AD-026 訂正記録の扱い

AD-029 新設で AD-026 を訂正する形式。AD-026 は **削除しない**（historical 記録維持）、新 AD で「v5.7.0 当時の判断、新事実で v5.7.1 で訂正」と明記。

### 2. claude-code-action のバージョン

- 公式 `anthropics/claude-code-action@v0` を採用（最新 stable）
- workflow 内で SHA pin 推奨（supply-chain hardening）、ただし v5.7.1 では @v0 タグのまま、deployment 時に SHA pin

### 3. 認証フロー

```yaml
# issue-pickup.yml
- uses: anthropics/claude-code-action@v0
  with:
    claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    # API key 経路は使用しない（追加課金回避）
```

`CLAUDE_CODE_OAUTH_TOKEN` 未設定時は `notice::skip` で red CI にしない（fork PR や secret 欠落環境での安全網、gemini-review.yml と同形式）。

### 4. gemini-cli の継続用途明確化

| 用途 | エージェント |
|---|---|
| AI triage（軽量、Issue 内容判定）| **gemini-cli** メイン継続 |
| 実装本体（コード生成、PR 作成）| **Claude Code CLI** メイン、gemini-cli はフォールバック（人間 P4 判断） |
| PR レビュー（gemini-review.yml）| **gemini-cli** メイン継続（変更なし） |

### 5. フォールバック発動条件

Claude Code action が失敗した場合：
- workflow log に `pickup-failed` label を Issue に自動付与
- Issue コメントで「Claude Code 実装失敗。人間が `do-not-pickup` で block するか、gemini-cli で再 trigger するか判断要請」を notice
- **自動 gemini フォールバックは実装しない**（philosophy 第 4 条「人間が判断する場面」と整合）

### 6. 後方互換完全維持

- 既存 LC ≥ 1 プロジェクト: 強制適用なし
- v5.7.0 以前の `issue-pickup.yml` (gemini-cli 前提) は既存プロジェクトでそのまま動作
- 新規プロジェクト + v5.7.1 以降の deploy で Claude Code CLI 経路採用

### 7. harness-verifier 全 PASS 維持

- skill 改修で frontmatter 整合性
- 新用語不要（既存用語の組み合わせのみ）
- 5 層構造保全（issue-implementer は「サポート」枠維持）

---

## 失敗時の判断

- **Claude Code CLI が無料 tier 内で稼働しない場合** → ユーザー P4 判断（OAuth token 確認、Pro/Max サブスクリプション要件再確認）
- **harness-verifier FAIL 時** → 修正試行 → なお NG なら Type C 献上
- **Council 起動候補** → 通常想定外、起動条件抵触なし

## 完了基準

- 全 11 項目（Phase A〜D）完遂
- harness-verifier 全 5 検査 PASS
- `delivery/SELF-VERIFICATION-v5.7.1.md` 完了
- PR description に本 HANDOFF 参照記述
- gemini-review + Copilot review 通過
- **auto-merge label 付与で workflow 経由自動 merge**（autonomous-drive loop 7 例目）

## 副次目的

- dialog-harness 自身の `.github/workflows/issue-pickup.yml` が **Claude Code CLI base** で稼働開始
- 次の v5.7.x で実装本体を完成させれば、Claude Code が実装エージェントとして稼働するフル自律 loop が DH 自身で動く
- ユーザーの「実装は Claude Code で L1 実行を基本とする」方針が制度化

## 進行方針

- **作業ブランチ**: `claude/v5.7.1-claude-code-pivot`
- **PR 戦略**: Phase 単位で commit、全完了後 1 PR で集約 + auto-merge label 付与
- **Pre-flight**: HANDOFF 全文 + crosscut-issue-implementer SKILL.md 現状 + 既存 issue-pickup.yml + claude-code-action 公式 README

L0 譲渡完了。autonomous-dev 起動を待つ。

---

## 引用: ユーザーの根源洞察

> 「実装は Anthropic Claude Code CLI で実行したい。リモート繋げてたらサブスクリプションのやつで稼働できないか？Gemini はフォールバックにする」
> 「実装は Claude Code で L1 実行を基本とする」

これは **「自前開発・低コスト」と「品質最重視」の両立**。Pro/Max サブスクリプション + OAuth token 経路の発見で、API 課金を回避しつつ Claude Code の実装品質を享受可能になった。
