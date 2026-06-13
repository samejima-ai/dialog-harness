# ADR-002: コードレビュアーを「対話で作り込む harness 部品」として配備可能化（v5.26.0）

## Status

Accepted（v5.26.0 で実装）。ADR-001 の後継・実装。

## Context

DH はプロジェクト設計のためのメタスキルである。CI レビュアー設定も「固定で一律に卸す」ものではなく、
**プロジェクト開始時に人間と認識合わせして作り込む harness 部品**として扱うのが DH の本質に整合する
（ユーザー方針、2026-06-13）。

これまで autonomous-drive が user project に配備するレビュアーは `gemini-review.yml`（仕様軸）のみで、
DH 本体で運用している `claude-review.yml`（4 フェーズ Council・汎用コードレビュー軸 = Copilot 代替）は
user project に配備する経路がなかった。また ADR-001 が予約した `${PROJECT_REVIEW_AXES}`（SPEC/DONT 由来の
project-specific 軸）は未実装で、既知ギャップ G-001 が open のままだった。

claude-review の Orchestrator-Conductor (OC) は元々「汎用コードレビュー軸」のみを担当し、仕様軸を
gemini に委ねる視点直交設計のため、コード軸部分は本質的に project-agnostic であり generic 化が素直である。
ただし tier2/3 で Council を回すには `.claude/agents/review-*.md`（8 個）の配備が追加で必要になる。

## Decision

1. **`templates/github-workflows/claude-review.yml.template` を新設**（DH 本体 claude-review.yml の generic 化版）。
   tier ゲート（paths フィルタ + routine pre-gate + 難度ゲート lightweight/council）を維持。placeholder:
   `${REPO_NAME}` / `${SCOPE_PATHS}` / `${SENSITIVE_PATHS_REGEX}` / `${PROJECT_REVIEW_AXES}`。

2. **レビュアー選択自体を spec-architect 対話の「コードレビュアー認識合わせ」ステップにする**
   （`autonomous-drive-deployment.md` §コードレビュアー認識合わせ）。L0 が SPEC/DONT を見て候補を提案 →
   人間が選ぶ:
   - どのレビュアーか（なし / Copilot / gemini 仕様軸 / claude 単発コード軸 / claude tier 段階 Council、組合せ可）
   - `${PROJECT_REVIEW_AXES}`（重点コードレビュー軸、SPEC/DONT 由来、空可）
   - `${SENSITIVE_PATHS_REGEX}`（フル Council に値する sensitive 範囲）
   - コスト感（tier 段階 Council は sensitive/大規模 PR で重い＝サブスク枠消費を明示認識合わせ）

3. **claude「tier 段階 Council」選択時のみ** `.claude/agents/review-*.md`（8 個）を verbatim 配備する
   （crosscut-council skill は通常 skills コピーで配備済み前提）。単発選択時は agents 非配備＝OC が常に単一パス。

4. **`${PROJECT_REVIEW_AXES}` を claude-review/gemini-review 両 template に注入**して ADR-001 を実装・G-001 を解消。
   gemini 側は既存の DH-specific default 軸に**加算**する方式（フル generic 化は残置、header 編集ガイドに委譲）。

## 検討した代替案

- **A: claude 単発のみ配備（agents 不要・軽い）** — 安いが深さ不足。tier 段階に後から上げられる柔軟性を優先し不採用（ただし「単発」選択肢として menu に残す）。
- **B: claude tier 段階 Council を full の既定配備物に固定追加** — DH メタ性に反する（固定卸し）。ユーザー方針により不採用。
- **C: 認識合わせ menu で選択式（採用）** — routine は安く・sensitive/大規模だけ Council 昇格。コスト/品質の runtime 中庸。DH の「対話で作り込む」本質に整合。

判断根拠: ユーザー方針「DH はメタスキル。CI 設定もプロジェクト開始時に任意・認識合わせして作り込むのがベスト」。

## Consequences

- user project は L0 対話でレビュアーを project 専用に作り込めるようになる（固定卸しからの脱却）。
- tier 段階 Council を選んだ project は、DH 本体と同様に sensitive/大規模 PR で重いレビュー（Opus OC + 3 ペルソナ、
  1 回 10〜20 分、サブスク枠消費）を継承する。**この trade-off は認識合わせで人間に明示必須**。
- `${PROJECT_REVIEW_AXES}` の実効値は user project の SPEC 成熟度に依存する（ADR-001 観測駆動原則）。空でも
  汎用軸のみで運用可能とし、空文化を許容する。
- claude-review.yml.template と gemini-review.yml.template に共通 placeholder `${PROJECT_REVIEW_AXES}` が入る。
- agents 8 個は verbatim 配備のため description 内の「dialog-harness」言及が user project に残るが、機能は
  project-agnostic（cosmetic 残置。churn 回避のため改名しない）。

## References

- ADR-001: `adr-001-axis-placeholder-reservation-v5.12.0.md`（本 ADR が実装する予約）
- 既知ギャップ: G-001 in `known-gaps.md`（本 ADR で resolved）
- ユーザー方針: 2026-06-13「DH メタスキル / CI レビュアーも認識合わせで作り込む」
- 配備ガイド: `layer0-spec-architect/references/autonomous-drive-deployment.md` §コードレビュアー認識合わせ
- template: `templates/github-workflows/claude-review.yml.template`
- DH 本体: `.github/workflows/claude-review.yml`（generic 化元）/ `.claude/agents/review-*.md`

## Related decisions

- opt-in 領域該当（`auto-merge-boundary.md` §opt-in 領域: autonomous-drive workflow 自身の改修）
- philosophy 不改変（第 7 条サポート枠内の deployment 拡張に閉じる）
