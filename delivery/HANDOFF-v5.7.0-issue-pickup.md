# HANDOFF: v5.7.0 autonomous-drive 入口側設計 + Issue 選別機構

**作成日**: 2026-05-03
**作成元**: layer0-spec-architect（本セッションで起動）
**譲渡先**: layer1-autonomous-dev
**起源**: ユーザー（ひでさん）の明示要請「Bを考えよう（自前 workflow 実装）」+ 重要観点「Issue 選択は開発品質を決めると言って過言ではない」
**Council 諮問**: なし（11 論点全て対話で合意、Council 起動条件未満）

---

## スコープ判定

- **昇格**: v5.6.0 → **v5.7.0 minor**（後方互換完全維持、opt-in、philosophy.md 改訂なし）
- **同梱項目**:
  - autonomous-drive 入口側 (Issue → AI pickup → 実装開始) 本格稼働
  - Issue 選別機構（label + author allowlist + 本文必須項目 + current_focus 整合 + AI triage の多段フィルター）
  - REGIME.md `current_focus` 軸新設
- **API 課金境界**: Anthropic API 回避、**gemini-cli 流用**（既存 GEMINI_API_KEY、追加コスト 0）

## 11 論点 確定（前 L0 セッションで合意済）

| # | 論点 | 確定 |
|---|---|---|
| 1 | 実装方式 | **gemini-cli 流用**（Anthropic API 回避） |
| 2 | Filter 設計 | label `ready-for-ai` + author allowlist + 本文必須項目 |
| 3 | コンテキスト判定 | REGIME.md `current_focus` (β 半自動: spec-architect 対話で更新) + γ ブランチ命名フォールバック |
| 4 | 必要性判断主体 | label opt-in + AI triage（完全自動） |
| 5 | ブレスト → Issue 化 | 既存 issue-dispatcher 拡張、新 sub-skill `crosscut-issue-drafter` v5.7.x 温存 |
| 6 | 品質ガード | L1 即献上 (Type A) + label `needs-clarification` |
| 7 | 多重起動防止 | workflow concurrency + label `in-progress` 自動付与 |
| 8 | 失敗時挙動 | 24h timeout + 自動 release + notice |
| 9 | 配置層 | D2 template + D4 reference + 既存 `crosscut-issue-implementer` skill 拡張 |
| 10 | dev_mode 連動 | `autonomous` + `autonomous_scope: full` のみ enable |
| 11 | API 課金境界 | GEMINI_API_KEY (無料 tier) + 日次 5 / 月次 50 上限 + circuit breaker |

## 実装スコープ Phase A〜E（全 17 項目）

### Phase A: 履歴層更新 + housekeeping (5 項目)

1. `history/CHANGELOG.md` v5.7.0 (in progress) エントリ追加 + v5.6.0 (released YYYY-MM-DD) 化同梱（**6 例目正規適用**）
2. `history/INTENT.md` v5.7.0 設計意図セクション
3. `history/REGIME-LOG.md` v5.7.0 minor 昇格判定
4. `history/ARCH-DECISIONS.md` AD-026 (実装方式: gemini-cli) / AD-027 (current_focus 軸新設) / AD-028 (Issue 選別 3 段階フィルター)
5. `history/COUNCIL-LOG.md` 必要時のみ append（Council 起動条件未満なら省略）

### Phase B: spec-architect 拡張 - current_focus 軸新設 (4 項目)

6. `assets/meta-spec-template.md` REGIME.md テンプレに `## current_focus` セクション追加
7. `references/regime-assessment.md` current_focus 判定（β 半自動）+ 更新規約 + γ branch 命名フォールバック追加
8. `references/dialog-questions.md` current_focus 確認質問追加（spec-architect 対話で更新するパターン例）
9. `references/dev-env-spec.md` Level C に current_focus と Issue pickup の連動表追加

### Phase C: crosscut-issue-implementer skill 拡張 (4 項目)

10. `SKILL.md` 全面改訂
    - workflow 起動条件 (label `ready-for-ai`)
    - 3 段階フィルター（label / author / 本文 / current_focus 整合）
    - AI triage 二次判定プロトコル（gemini-cli が Issue 内容を読み pickup 可否判定）
    - circuit breaker（日次/月次上限）
    - 失敗時の挙動（24h timeout / 即献上）
11. `references/issue-filter-spec.md` 新設（filter ロジックの詳細仕様）
12. `references/triage-protocol.md` 新設（AI triage 二次判定のプロトコル + gemini-cli 実装パターン）
13. `references/circuit-breaker-spec.md` 新設（日次5/月次50 上限 + 緊急停止 + P4 暴走時介入経路）

### Phase D: workflow + template (3 項目)

14. `.github/workflows/issue-pickup.yml` 新設（dialog-harness 自身に deploy）
    - trigger: `issues.labeled` (label `ready-for-ai` 付与時)
    - Pre-check: GEMINI_API_KEY + GH_REVIEW_PAT availability
    - Filter: 本文必須項目 + author allowlist + current_focus 整合
    - AI triage: gemini-cli 経由で Issue 内容判定
    - Pickup: branch 作成 + label `in-progress` 自動付与
    - 実装: gemini-cli が repo を clone + 実装 + commit
    - PR 作成: gh pr create + ready-for-review + (autonomous_scope: full なら) `auto-merge` label 自動付与
    - 後段: 既存 gemini-review.yml + auto-merge.yml が引き継ぎ
    - Circuit breaker: 日次/月次上限超過で workflow 全停止
15. `templates/github-workflows/issue-pickup.yml.template` 新設（利用者プロジェクト展開用、placeholder 化）
16. `.claude/skills/layer0-spec-architect/references/autonomous-drive-deployment.md` に入口側 deployment 手順を追記（既存 reference の拡張）

### Phase E: 自己検証 + 献上 (1 項目)

17. `delivery/SELF-VERIFICATION-v5.7.0.md`（§7.4 + harness-verifier 全 PASS + philosophy 第 7 条 P2 整合性確認 + gemini-cli 実装エージェント運用方針確認）

---

## 重要な実装制約

### 1. gemini-cli を「実装エージェント」として使用する未踏領域

- **PR レビュー**ではなく**実装作業**を gemini-2.5-pro で実行
- gemini-review (PR #43) で実用域を実証済だが、「実装」は「レビュー」より格段に重い処理
- 失敗確率高い、観測駆動で品質判断
- **実装段階で品質悪い場合は autonomous-dev が独自 Council 起動可**（adrv01-Ph1 自己申告プロトコル経由）
  - 候補案: ローカル Claude Code セッションへのフォールバック / Copilot Workspace 切替 / 一時的 Anthropic API 限定使用

### 2. issue-pickup.yml workflow 設計の核

```yaml
# 概略フロー
on:
  issues:
    types: [labeled]

jobs:
  pickup:
    if: github.event.label.name == 'ready-for-ai'
    steps:
      - check_secrets (GEMINI_API_KEY + GH_REVIEW_PAT availability)
      - check_circuit_breaker (日次/月次上限)
      - filter (label + author allowlist + 本文必須項目 + current_focus 整合)
      - ai_triage (gemini-cli が Issue 内容を読んで pickup 可否判定)
      - pickup_or_skip (skip 時は notice + 即終了)
      - branch_create + label `in-progress` 自動付与
      - implementation (gemini-cli が repo + Issue を読み実装 + commit)
      - pr_create (gh pr create + ready-for-review + auto-merge label 付与)
      - 後段は既存 gemini-review.yml + auto-merge.yml が引き継ぎ
```

### 3. current_focus 設計の詳細（β 半自動 + γ フォールバック）

**β 半自動更新**:
- spec-architect 対話で「今このプロジェクトで何に集中？」を確認 → AI が REGIME.md を更新
- 例: ユーザー「v5.7.0 のバグを直したい」→ spec-architect が `current_focus.type: bug-fix` と更新
- 更新は L0 spec-architect の責務（philosophy 第 4 条 + 第 7 条 P カテゴリと整合）

**γ ブランチ命名フォールバック**:
- REGIME.md `current_focus` 未設定の場合、ブランチ命名から推論
  - `fix/*` → `bug-fix`
  - `feat/*` → `feature`
  - `refactor/*` → `refactor`
- フォールバックは AI triage 内で実行、人間に確認を求めない

**REGIME.md `current_focus` フィールド**:
```yaml
## current_focus
- type: bug-fix          # bug-fix / feature / refactor / docs / chore
- target: master         # 対象ブランチ
- since: 2026-05-03
- priority: critical     # critical / standard / low
```

### 4. AI triage 二次判定プロトコル

gemini-cli が Issue 内容を読み pickup 可否を判定:

```
INPUT:
  - Issue title + body
  - REGIME.md current_focus
  - SPEC.md (実装範囲)
  - DONT.md (スコープ外)

JUDGMENT:
  - pickup_yes: Issue が SPEC 範囲内 + current_focus 整合 + 本文充足
  - skip_label: 「needs-clarification」付与（本文不足）+ Issue close せず人間差し戻し
  - skip_out_of_scope: 「out-of-scope」付与（DONT.md 抵触）+ 人間判断要請
  - skip_focus_mismatch: 「focus-mismatch」付与（current_focus と category 不一致）+ 一時延期
```

### 5. Circuit Breaker 設計

- **日次上限**: 5 Issue/日 (UTC 0:00 リセット)
- **月次上限**: 50 Issue/月 (1 日 0:00 UTC リセット)
- 上限到達時: 新規 pickup 全停止 + Issue に label `circuit-broken` + notice 通知
- 解除: 翌日/翌月の自然解除、または P4 が手動で解除（label 削除 + workflow 再有効化）
- 統計: `.gemini/issue-pickup-stats.json` (artifact upload で観測可能)

### 6. 後方互換完全維持

- dev_mode `autonomous` + `autonomous_scope: full` 以外では本機構は起動しない
- 利用者プロジェクトへの強制配布なし（template 配置のみ、起動は spec-architect 対話で確認）
- 既存 issue-implementer skill の DSL/フォーマットは下位互換（拡張のみ）

### 7. harness-verifier 全 PASS 維持

- issue-implementer skill 改修で frontmatter 検査の整合性
- 新用語 (`current_focus`, `triage`, `circuit_breaker`, `pickup`, `release` 等) を `harness-verifier/glossary.yml` に追加
- 新 references の path 有効性
- 5 層構造保全（D4 解釈、issue-implementer skill が 4 役割の「サポート」枠に正しく位置づくこと）

---

## 失敗時の判断

- **gemini-cli 実装品質不足を検出した場合** → autonomous-dev が **Council 起動**（adrv02 と同形式）。候補案:
  - α: gemini-cli を継続使用 + prompt engineering 改善
  - β: ローカル Claude Code セッションへのフォールバック（手動運用継続）
  - γ: Copilot Workspace 切替検討
- **harness-verifier FAIL 時** → 修正試行 → なお NG なら Type C 献上
- **暴走兆候を自身で検出した場合** → adrv01-Ph1 自己申告プロトコル経由

## 完了基準

- 全 17 項目（Phase A〜E）完遂
- harness-verifier 全 5 検査 PASS
- `delivery/SELF-VERIFICATION-v5.7.0.md` 完了
- PR description に本 HANDOFF への参照記述
- gemini-review + Copilot review 通過
- **auto-merge label 付与で workflow 経由自動 merge**（autonomous-drive loop 6 例目）

## 副次目的

- **dialog-harness 自身に issue-pickup.yml をデプロイ** → v5.7.x 以降の DH 開発から「Issue → 自動実装 → 自動 merge」のフル自律 loop が稼働開始
- 「対話で決めたもの → Issue → 自動実装」のパターン（ユーザー指摘）が dialog-harness 自身で動く

## 進行方針

- **作業ブランチ**: `claude/v5.7.0-l0-handoff` （HANDOFF を Phase 0 commit、Phase A〜E は autonomous-dev が PR 戦略を判断）
- **PR 戦略**: 全 Phase 完了後に 1 PR で集約 + auto-merge label 付与（v5.6.0 PR #43 と同型）
- **Pre-flight**: 必要な reference (philosophy.md / spec-architect SKILL.md / regime-assessment.md / issue-implementer SKILL.md / harness-verifier 等) を実装前に読む
- **同梱 housekeeping**: v5.6.0 (in progress) → (released YYYY-MM-DD) 化（6 例目正規適用）

## L0 自己検証 (§7.4) の事前確認

- [x] broken reference 検査: 本 HANDOFF が引用するファイル・パスは全て存在
- [x] DONT 自己照合: DH に DONT.md は無いが philosophy 7 条との整合性は別途確認（特に第 4 条「人間がしないこと」+ 第 7 条 P2 「ブレスト→Issue 化は AI」と整合）
- [x] Pre-flight 充足: 本セッションで読んだ refs に従い進行（前 v5.6.0 セッション継続）
- [x] 受け入れ基準充足: §0 受け入れ基準 4 条件は LC=2 既存プロジェクト + 新規追加機能なので段階適用、本要請は v5.7.0 新規追加部分にのみ適用

---

**実装開始時の Pre-flight**:
- 本 HANDOFF 全文を読む
- crosscut-issue-implementer/SKILL.md の現状確認（既存スキル拡張のため）
- gemini-review.yml の構造を参考にして issue-pickup.yml の base 設計
- harness-verifier 全 5 検査の現状ベースライン記録
- v5.6.0 の (in progress) 化対象 (CHANGELOG.md) を v5.7.0 PR で同梱して (released) 化

**完了基準**:
- 全 17 項目の Phase A〜E 完遂
- harness-verifier 全 5 検査 PASS
- `delivery/SELF-VERIFICATION-v5.7.0.md` 完了
- PR description に本 HANDOFF への参照記述
- gemini-review + Copilot review 通過
- 自動 merge（label `auto-merge` 付与で workflow 経由）

L0 譲渡完了。autonomous-dev 起動を待つ。

---

## 引用: ユーザーの根源洞察（記録のため）

> 「Issue 選択は開発品質を決めると言って過言ではない」
> 「色んな場所でブレストしたものを Issue 化していくイメージ」
> 「非エンジニアだから AI の方が確実に優秀」
> 「それこそこの流れで決めたものを Issue に上げて進めるイメージだよね」

これらは philosophy.md 第 4 条 + 第 7 条 P カテゴリ + autonomous-drive 機構の設計思想と完全整合。本 v5.7.0 はその思想を「Issue 起点」という具体機構に落とし込む実装である。
