# HANDOFF: v5.6.0 autonomous-drive 標準化 + DH AI 組織論明文化

**作成日**: 2026-05-03
**作成元**: layer0-spec-architect（本セッションで起動）
**譲渡先**: layer1-autonomous-dev
**起源**: ユーザー（ひでさん）からの明示要請「自律駆動を L0 に記録して他の開発でも容易に展開できるようにしたい、これはメタスキル開発」
**Council 諮問**: `council-2026-05-03T08:30:00Z-adrv02`（β 止揚 = deployment skill のみ新設、guardian は patch 温存、`agreed_with_modification`）

---

## スコープ判定

- **昇格**: v5.5.3 → **v5.6.0 minor**（後方互換完全維持、opt-in、philosophy.md は第 7 条追加のみ既存 6 条改訂なし）
- **同梱項目（v5.5.3 AD-022 温存項目から）**:
  - ✅ パス B（dev_mode autonomous 化）= 本体
  - ❌ destructive change detector = v5.6.x patch 候補へ温存（観測駆動）
  - ❌ ALLOWED_AUTHORS 動的化 = v5.6.x or v5.7.0 候補へ温存
- **新規同梱**:
  - ✅ philosophy.md 第 7 条新設（DH AI 組織論：4 役割属性 + サポート）
  - ✅ 人間 4 責務（H1-H4）の明文化
  - ✅ `autonomous_scope` 軸新設（full / merge_gated / custom）

## DH AI 組織論（philosophy.md 第 7 条 仮文言）

```markdown
## 第 7 条: AI 組織論（4 役割 + サポート構造）

DH の AI 組織は 4 役割属性のみで構成される：
- L0 設計 / L1 実装 / L2 統括 / Council 判断
それ以外の skill (crosscut-* 非 council 系) と sub-agent は、これら 4 役割を
補助するサポートとして位置づく。L3 運用層を新設しない原則 (§1 フラクタル)
と整合し、運用インシデントは新仕様発見として L0 へ還元する。

### 役割境界の根拠
- L0 = 未来→仕様（spec-architect）/ 過去→意図復元（archeo-architect）/ 既存→harness 化（onboarding）
- L1 = 仕様→コード（autonomous-dev）+ コード→仕様照合（independent-reviewer）
- L2 = 統括→サブドメイン分割（orchestrator）+ 統合検証（integration-verifier、L2 発動時のみ）
- Council = 4 役割いずれかから献上された判断点で合議（人間 ≒ Council 原則の機構実装）

### 「あらゆる開発に対応」の汎化性主張
4 役割の責務組み合わせと連携プロトコルで、本 DH 範囲のあらゆる開発を完遂可能。
新たな職種軸分業（FE/BE/QA 等）や層追加は採用しない（§1 フラクタル原則と整合）。

### サポートと役割の区別
- サポート skill は単独で完結せず、必ず L0/L1/L2/Council のいずれかから呼ばれる
- サポート skill 自身が献上を発生させる場合（例: feedback-loop の drift 還流）も、
  献上先は 4 役割のいずれか（多くは L0 spec-architect への差し戻し）
- crosscut prefix の意味: 「全 layer をまたぐ横断機構」のうち、Council は判断主体、
  非 council 系はサポートヘルパー
```

## 人間 4 責務（philosophy.md §6 拡張 or 第 7 条内記述）

| # | 役割 | 行為 | AI 関与 |
|---|---|---|---|
| **H1 発案** | プロジェクト方向性、新機能アイデア | 思考 | ❌ AI 不可 |
| **H2 ブレスト** | 対話で方向性を具体化（**Issue 化は AI 担当**、人間は手を動かさない） | 発話 | △ AI が応答・整理・Issue 作成 |
| **H3 事後確認・評価** | merge 済 PR の振り返り、autonomous loop の健全性監視 | 思考 | ❌ AI 不可 |
| **H4 暴走時介入** | `do-not-merge` label、`ALLOWED_AUTHORS` 縮退、circuit breaker | 発話 | △ AI は notice/warning で兆候提示まで |

**原則**: 人間 = 頭と口を動かす / AI = 手を動かす。

## 実装スコープ（autonomous-dev への指示）

### Phase A: 基礎整備（philosophy + 履歴層）

1. **`.claude/skills/layer0-spec-architect/references/philosophy.md`**
   - 第 7 条「AI 組織論」を新設（上記仮文言）
   - 既存 6 条は不変
2. **`history/INTENT.md`**
   - v5.6.0 セクション追加
   - autonomous-drive 標準化の設計意図 + DH AI 組織論明文化 + Council β 止揚採用記録
3. **`history/REGIME-LOG.md`**
   - v5.6.0（minor 昇格、後方互換維持）判定記録
4. **`history/ARCH-DECISIONS.md`**
   - AD-023: autonomous-drive 標準化（パス B 採用、Council β 止揚で deployment skill のみ新設）
   - AD-024: philosophy.md 第 7 条新設（DH AI 組織論）
   - AD-025: `autonomous_scope` 軸新設（full / merge_gated / custom）
5. **`history/COUNCIL-LOG.md`**
   - `council-2026-05-03T08:30:00Z-adrv02` エントリ append（implementer_consent: agreed_with_modification）
6. **`history/CHANGELOG.md`**
   - v5.6.0 (in progress, target 2026-05-03 or 翌日) エントリ追加
   - v5.5.3 (in progress) → (released YYYY-MM-DD) 化を **同梱**（4 例目正規適用、housekeeping）

### Phase B: spec-architect 改修（L0 対話の autonomous_scope 軸追加）

7. **`.claude/skills/layer0-spec-architect/SKILL.md`**
   - §dev_mode 軸 セクション拡張
     - dev_mode `autonomous` の本格定義（github_autonomous の発展形）
     - `autonomous_scope`（full / merge_gated / custom）の追加
   - §処理フロー §6 開発環境構築に「Level C: AI 自律運用」追記
8. **`.claude/skills/layer0-spec-architect/references/dialog-questions.md`**
   - 自律駆動の度合い質問追加：
     ```
     Q: 自律駆動の度合いを選択してください
        (1) フルオート [デフォルト推奨]
            人間 = H1〜H4 のみ。AI = Issue 精査〜自動 merge〜次 Issue 着手まで完全自走
        (2) 中度: 自動 merge は無効、PR review/approve は人間が実施
        (3) カスタム: 個別に設定（dev-env-spec.md Level C 詳細表）
     ```
9. **`.claude/skills/layer0-spec-architect/references/regime-assessment.md`**
   - §dev_mode 判定 セクションに `autonomous` の発動条件を本格定義
   - LC との連動規則（local_only LC=0 → github_assisted LC≥1, M1 → autonomous/merge_gated LC≥1, M2 → autonomous/full は CTL 観測値）
10. **`.claude/skills/layer0-spec-architect/references/dev-env-spec.md`**
    - 「Level C: AI 自律運用」新設
    - autonomous-drive 標準化に必要な template / secret / label の説明
11. **`.claude/skills/layer0-spec-architect/assets/meta-spec-template.md`**
    - REGIME.md テンプレに `## autonomous_scope` セクション追加

### Phase C: template 配置 + crosscut skill 新設（β 止揚採用）

12. **`templates/github-workflows/` ディレクトリ新設**
    - `gemini-review.yml.template`
    - `auto-merge.yml.template`
    - placeholder 規約: `${REPO_OWNER}` `${REPO_NAME}` `${ALLOWED_AUTHORS}` `${VERIFIER_JOB_NAME}` `${SCOPE_PATHS}`
    - dialog-harness 自身の `.github/workflows/` から汎化（プロジェクト固有値を placeholder 化）
13. **`.claude/skills/crosscut-autonomous-drive/` 新設**（**β 止揚: deployment 専念**）
    - `SKILL.md`（frontmatter + サポート skill としての責務定義）
      - 責務:
        - template 取得（`templates/github-workflows/` 配下から）
        - placeholder 置換（spec-architect 対話で確定した値で）
        - 配置（`.github/workflows/` 配下にコピー）
        - label 作成（`auto-merge`, `ready-for-ai`, `do-not-merge` 等）
        - secrets 確認（`GH_REVIEW_PAT` / `GEMINI_API_KEY` の有無 + 権限ガイド）
      - 起動経路: spec-architect が dev_mode `autonomous` 判定時に明示起動指示
      - 献上経路: 失敗時は L0 spec-architect へ Type C/D 献上
    - `references/placeholder-spec.md`（placeholder 一覧 + 規約）
    - `references/setup-checklist.md`（label / secret / PAT 設定手順）
    - `assets/` 配下に必要なら追加 asset
14. **`.claude/skills/layer0-spec-architect/references/autonomous-drive-deployment.md` 新設**
    - autonomous-drive deployment の対話レベルガイド
    - `crosscut-autonomous-drive` skill の起動タイミング規定
    - L0 → L1 への譲渡（spec-architect が決定 → autonomous-dev が template 適用 → crosscut-autonomous-drive を呼び出す）

### Phase D: 自己検証 + 献上

15. **harness-verifier 全 5 検査 PASS** 確認
    - 新 skill `crosscut-autonomous-drive` の frontmatter 整合性検査が +1
    - 新 reference / template の参照 path 有効性確認
    - 5 層構造保全（D4 解釈、新 skill が「サポート」枠に正しく位置づくこと）
    - 用語辞書整合（`autonomous_scope`, `H1-H4`, 「サポート skill」等の新用語追加）
16. **`delivery/SELF-VERIFICATION-v5.6.0.md`** 作成
    - L0 §7.4 自己検証の 5 項目
    - philosophy.md 第 7 条と既存 6 条の整合性確認
    - 4 役割組織論と既存 skill 配置の整合性確認

## 設計判断の Council 経由

- **adrv02 (`council-2026-05-03T08:30:00Z-adrv02`)**: skill 新設の可否 → `agreed_with_modification`（β 止揚: deployment skill 1 つのみ、guardian は patch 温存）

## 失敗モード設計（H4 暴走防止）

v5.6.0 では以下を設計するが、本実装は v5.6.x patch 候補：

- label `do-not-merge` 付与で auto-merge 永久 block（既存 auto-merge.yml で実装可能、優先度高）
- `ALLOWED_AUTHORS` 縮退プロトコル（手動、文書化のみ）
- circuit breaker（5 連続 fail で auto-merge 自動停止、v5.6.x で実装）
- destructive change detector（diff threshold / DELETE-heavy detect、v5.6.x で実装）

最低限 `do-not-merge` label の handling は v5.6.0 で auto-merge.yml に追加する。

## 後方互換性

- 既存 LC ≥ 1 プロジェクト: 強制適用なし（v5.0.0〜v5.5.3 と同パターン）
- philosophy.md 第 7 条新設: 既存 6 条改訂なし、追加のみ
- spec-architect 改修: 新規プロジェクト立ち上げ対話の質問追加のみ、既存対話フロー不変
- autonomous-drive deployment: opt-in（dev_mode `autonomous` 選択時のみ）
- 利用者プロジェクトへの強制配布なし

## v5.6.x / v6.0.0 候補として温存

- destructive change detector（diff threshold / DELETE-heavy）
- circuit breaker（5 連続 fail 自動停止）
- ALLOWED_AUTHORS 動的化（複数 contributor 体制で必要時）
- adrv01-Ph2（独立観測機構、harness-verifier 同型 crosscut skill）
- crosscut-verifier-philosophy 本実装（v5.0.0 から累計後送中、第 7 条で組織論が確定したので連動可能）
- パス B'（autonomous_scope: full の本格運用後に dev_mode 階層を REGIME に正式統合）
- DH AI 組織論の汎化性主張テスト（4 役割で実 N=3 別プロジェクトをカバーできるか観測）

## L0 → L1 譲渡時の制約

- 本要請は **dev_mode 引き上げ + メタスキル開発** であり、慎重な実装を要する
- autonomous-dev は本 HANDOFF を基に PR 構成を計画（複数 commit / 1 PR or 複数 PR）
- philosophy.md 改訂部分は特に慎重に（既存 6 条との整合性、用語の意味のブレなし）
- Council 諮問結果（adrv02）は autonomous-dev も実装中に再諮問の必要性を判断する権利を持つ
- 失敗時は Type C 献上（L0 への差し戻し）

## L0 自己検証 (§7.4) の事前確認

- [ ] broken reference 検査: 本 HANDOFF が引用するファイル・パスが実体存在
- [ ] DONT 自己照合: DH に `DONT.md` は無いが philosophy.md 6 条との整合性は別途確認
- [ ] Pre-flight 充足: 本セッションで読んだ refs（ritual-protocol.md など）に従い進行
- [ ] 受け入れ基準充足: §0 受け入れ基準 4 条件は LC=2 既存プロジェクト + 新規追加機能なので段階適用、本要請は v5.6.0 新規追加部分にのみ適用

---

**実装開始時の Pre-flight**:
- 本 HANDOFF 全文を読む
- philosophy.md 第 7 条仮文言を refine（autonomous-dev 自身の judgment 範囲）
- harness-verifier 全 5 検査の現状ベースライン記録（commit 前に実行）
- v5.5.3 の `(in progress)` 化対象 (CHANGELOG.md) を v5.6.0 PR で同梱して `(released)` 化

**完了基準**:
- 全 16 項目の Phase A〜D 完遂
- harness-verifier 全 5 検査 PASS
- `delivery/SELF-VERIFICATION-v5.6.0.md` 完了
- PR description に本 HANDOFF への参照記述
- gemini-review + Copilot review 通過
- 自動 merge（label `auto-merge` 付与で workflow 経由）

L0 譲渡完了。autonomous-dev 起動を待つ。
