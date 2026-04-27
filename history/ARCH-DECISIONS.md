# ARCH-DECISIONS

DH 本体の設計判断の記録（ADR 軽量版）。

## v5.0.0

### AD-001: crosscut- prefix の導入

| 項目 | 内容 |
|---|---|
| 状況 | council/ は「全 Layer 横断」の判定機構だが、命名が層構造を示していなかった |
| 判断 | `crosscut-` prefix を Level A skill の第二の命名規則として確立し、`council/` を `crosscut-council/` にリネーム |
| 根拠 | spec §3.1.3 / §4.1。3 層 + 1 横断の構造を命名で明示化、フラクタル原則 P1 に整合 |
| 影響 | 後方互換破壊（major 昇格）。既存プロジェクト側の参照は migration-guide で個別対応 |

### AD-002: dev_mode 軸の追加

| 項目 | 内容 |
|---|---|
| 状況 | 既存軸（規模 S / 不確実性 U / リスク R / NFR N / Lifecycle）に GitHub 連携前提の判定軸が無かった |
| 判断 | dev_mode 軸（local_only / github_assisted / github_autonomous）を 3 軸目の動的判定軸として追加 |
| 根拠 | spec §3.2.1〜§3.2.3。GitHub 無しでも DH ベースは完全動作の原則を保ちつつ段階的移行を可能にする |
| 影響 | regime-assessment.md / REGIME.md テンプレ拡張。後方互換あり（既存プロジェクトは local_only 相当として扱える） |

### AD-003: 仕様 1〜4 を crosscut- skill 化

| 項目 | 内容 |
|---|---|
| 状況 | GitHub 連携の 4 仕様（Issue 射出・実装・検証・還流）は L0/L1/L2 のいずれにも純粋には属さず、横断的に発動する |
| 判断 | 仕様 1〜4 を `crosscut-issue-dispatcher` / `crosscut-issue-implementer` / `crosscut-verifier-drift` / `crosscut-verifier-philosophy` (placeholder) / `crosscut-feedback-loop` の 5 skill として配置 |
| 根拠 | spec §4.3。3 層 + 1 横断構造の維持、責務分離（P3）、各 skill の同型構造によるフラクタル原則発現 |
| 影響 | 新規 skill 5 件追加。layer1-* から参照を追加、既存 layer 機構は不変 |

### AD-004: CTL 連動条件分岐の組み込み

| 項目 | 内容 |
|---|---|
| 状況 | CTL システム（v4.2 で追加）は判定ロジックは存在したが、各 skill の動作分岐に組み込まれていなかった |
| 判断 | 仕様 1〜4 すべての protocol references で CTL-0/1/2/3 の段階的自動化を明文化 |
| 根拠 | spec §3.2.4〜§3.2.7、§4.4。再帰進化原則 P2 を CTL 育成戦略として実装 |
| 影響 | 各 crosscut- skill 配下に protocol.md を追加。CTL 育成戦略は ctl-maturity-strategy.md として独立 |

### AD-005: claude-code-action 公式採用

| 項目 | 内容 |
|---|---|
| 状況 | Issue → 実装の自動化手段として複数選択肢があった |
| 判断 | Anthropic 公式の claude-code-action を採用、GitHub Actions 雛形に組み込み |
| 根拠 | spec §3.2.5、§3.2.9。業界 BP 取り込み、保守性、エコシステム整合性 |
| 影響 | templates/.github/workflows/issue-to-impl.yml の依存。バージョンは `<latest>` プレースホルダ（実装時点で公式リポジトリ確認） |

### AD-007: docs/ ディレクトリの限定許可

| 項目 | 内容 |
|---|---|
| 状況 | リポジトリは "skill-only policy" (PR #3) で `docs/` を gitignore 済み。spec §5.4.2 が `docs/migration-guide-v5.0.0.md` を v5.0.0 配布物として要求 |
| 判断 | `docs/` 全体の gitignore は維持しつつ、配布対象の migration guide のみを許可（`!docs/migration-guide-*.md`） |
| 根拠 | 設計ドラフト（drafts policy）と配布ドキュメント（migration guide）は性質が異なる。最小例外で skill-only policy の精神を保つ |
| 影響 | `.gitignore` 1 行追加。今後の v6.0.0 以降の migration guide も同パターンで許可される |

### AD-006: README バッジ作業のスキップ（適用対象外）

| 項目 | 内容 |
|---|---|
| 状況 | spec §4.6.2.4 で README に v5.0.0 バッジを追加する指示があるが、リポジトリルートに README.md が存在しない |
| 判断 | README バッジ追加作業はスキップ。SKILL.md バージョン履歴 / credit-template.md / REGIME-LOG.md でバージョン更新を完結させる |
| 根拠 | スキルは SKILL.md の frontmatter + 本文が標準。README は人間向けプロジェクト紹介で本案件のスコープ外。SELF-VERIFICATION §5.3.2 で「適用対象外」明記 |
| 影響 | バージョン更新は他経路で完結。README 整備は別案件として保留 |
