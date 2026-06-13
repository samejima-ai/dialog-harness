# Autonomous-Drive Deployment Guide

L0 spec-architect 対話レベルでの autonomous-drive 機構 deployment ガイド。詳細な template 適用ロジックは `crosscut-autonomous-drive` skill が担う。

## 起動タイミング

spec-architect 処理フローの **§6 開発環境構築** で、`dev_mode: autonomous` が確定した場合のみ実行：

```
4. モード判定（dev_mode = autonomous 確定）
   ↓
5. 人間レビュー（autonomous_scope 確認）
   ↓
6. 開発環境構築
   - Level A/B 共通スキル配置
   - **Level C: AI 自律運用** ← 本ガイドの範囲
     ↓
     crosscut-autonomous-drive skill を明示起動
     ↓
     template 取得 → placeholder 置換 → 配置 → label 作成 → secrets ガイド
```

## spec-architect 対話で確定すべき値

deployment 前に対話で取得する placeholder 値：

| 項目 | 質問例 | デフォルト |
|---|---|---|
| `${ALLOWED_AUTHORS}` | 「auto-merge を信頼する author の GitHub login 名は？ 複数なら space 区切り」 | プロジェクト owner（git remote から自動抽出） |
| `${VERIFIER_JOB_NAME}` | 「構造的検証の job 名は？（auto-merge.yml の condition 4 で参照）」 | `verify`（dialog-harness 標準） |
| `${SCOPE_PATHS}` | 「gemini-review / claude-review が発火する paths は？」 | `src/**`, `tests/**`, `docs/**` 等の標準セット |
| `autonomous_scope` | dev_mode autonomous 確定後の 1 問（dialog-questions.md 参照） | `full` |
| **code-reviewer 構成** | 下記「コードレビュアー認識合わせ」で取得（どのレビュアー / 重点軸 / sensitive 範囲） | gemini のみ（claude-review は opt-in） |

これらを取得後、`crosscut-autonomous-drive` skill を起動する。

## コードレビュアー認識合わせ（v5.26.0 追加）

> DH はプロジェクト設計のメタスキルであり、CI レビュアーも「固定で卸す」のではなく
> **プロジェクト開始時に人間と認識合わせして作り込む harness 部品**として扱う。本ステップは
> Level C deployment の一部として、どのレビュアーをどの深さ・どのコスト・どの軸で動かすかを
> spec-architect 対話で擦り合わせる。ADR-001 が予約した `${PROJECT_REVIEW_AXES}` 抽出の実装場所。

deployment 実行前に、以下 3 点を提示 → 人間が選択する（**L0 が SPEC/DONT を見て候補を提案し、人間が決める**）:

### (1) どのレビュアーを使うか（任意・組合せ可）

| 選択肢 | 配備物 | 性格 | コスト |
|---|---|---|---|
| なし | — | レビュー機構を入れない | 0 |
| Copilot のみ | （GitHub 設定のみ） | 標準 Copilot review | 0（GitHub 側） |
| **gemini（仕様軸）** | `gemini-review.yml` | プロジェクト仕様軸（SPEC/DONT 契約）を独立観測 | GEMINI_API_KEY 従量 |
| **claude 単発（コード軸）** | `claude-review.yml`（pre-gate で routine skip、難度ゲートで tier1 軽量に分岐） | 汎用コードレビュー軸を高高度に。routine は安価 | サブスク枠（API 追加課金なし） |
| **claude tier 段階 Council** | `claude-review.yml` + `.claude/agents/review-*.md`（8 個） | tier1=軽量単一パス（安価）/ tier2,3=フル Council（3 ペルソナ・重い） | サブスク枠（tier2/3 は重い・1 回 10〜20 分） |

- **claude 単発と tier 段階 Council は同一 template**（`claude-review.yml.template`）。違いは agents 配備の有無 ——
  agents を配備すると tier2/3 で Council fan-out が走る。配備しなければ OC が常に単一パス（= 実質単発）。
- gemini と claude は **視点直交**（仕様軸 vs コード軸）なので **併用が既定の推奨**。両方使うと多層防御になる。
- ⚠️ **コスト感の認識合わせ必須**: tier 段階 Council は sensitive/大規模 PR で重く（Opus OC + 3 ペルソナ）、
  人間のサブスク枠を消費する。「深さ重視なら Council、軽さ重視なら単発」を明示して人間に選ばせる。

### (2) `${PROJECT_REVIEW_AXES}` — このプロジェクトで特に重視する軸

L0 が user project の `SPEC.md` / `DONT.md` / 固有 sensors を読み、**重点コードレビュー軸の候補を箇条書きで提案** →
人間と擦り合わせて確定する。claude-review の OC プロンプト（視点直交セクション）と gemini-review prompt に注入される。

- 例（提案 → 認識合わせ）: 「SPEC に『全 I/O は schema validation 必須』とあるので、未検証入力の検出を重点軸に？」
  「DONT に『同期 fs 呼び出し禁止』とあるので、blocking I/O を重点軸に？」
- 確定値は YAML/Markdown 箇条書きで `${PROJECT_REVIEW_AXES}` に展開（各行 `- <軸>`）。
- **空でも可**: SPEC 成熟度が低ければ無理に埋めず汎用軸のみで運用（ADR-001 の観測駆動原則。空文化を避ける）。

### (3) `${SENSITIVE_PATHS_REGEX}` — フル Council に値する sensitive 変更の判定

claude-review の routine pre-gate で「この変更は重いレビューに値するか」を決める regex。プロジェクト固有の
**ハーネス中核 / CI / 仕様契約パス**を人間と擦り合わせる。

- デフォルト（DH-harnessed プロジェクト標準）: `(^\.github/)|(^\.claude/)|(SPEC)|(DONT)|(REGIME)`
- プロジェクト固有の重要ディレクトリ（例 `(^src/core/)|(^migrations/)`）を追加可能。

### 認識合わせ結果の記録

確定した reviewer 構成・`${PROJECT_REVIEW_AXES}`・`${SENSITIVE_PATHS_REGEX}` は REGIME.md の
`## autonomous_scope` セクション（`custom_config:` または `reviewers:` キー）に YAML で記録し、
`crosscut-autonomous-drive` skill に渡す。

## crosscut-autonomous-drive skill 起動方法

spec-architect から起動：

```
context: spec-architect 対話で確定した placeholder 値 + autonomous_scope
intent: "autonomous-drive deployment for ${REPO_NAME}"
expected_output: deployment 結果（配置パス / label 作成結果 / secrets 状態）
failure_handling: Type C 献上で spec-architect へ差し戻し
```

詳細プロトコルは `.claude/skills/crosscut-autonomous-drive/SKILL.md` 参照。

## 配置成果物（autonomous_scope: full の場合）

deployment 完了後、利用者プロジェクトに以下が配置される：

```
利用者プロジェクト/
├── .github/
│   └── workflows/
│       ├── auto-merge.yml       # placeholder 置換済
│       ├── gemini-review.yml    # placeholder 置換済
│       └── claude-review.yml    # ★ reviewer 認識合わせで claude を選んだ場合のみ（placeholder 置換済）
├── .claude/agents/              # ★ claude「tier 段階 Council」を選んだ場合のみ
│       └── review-*.md          #    review-fetch / difficulty / intent-gate / evidence / persona-{ceo,dev,phil} / judgment（8 個、verbatim コピー）
├── (label set: ready-for-ai / do-not-merge / human-review-needed を GitHub UI で確認)
└── (Repository Secrets: GH_REVIEW_PAT / GEMINI_API_KEY / CLAUDE_CODE_OAUTH_TOKEN を GitHub UI で設定)
```

> claude-review.yml と `.claude/agents/review-*.md` は **コードレビュアー認識合わせ（上記）で人間が
> 明示選択した場合のみ**配備される。gemini-review.yml はコード軸ではなく仕様軸を見るので両者は直交し、
> 併用が推奨。crosscut-council skill（`.claude/skills/crosscut-council/`）は通常の skills コピーで配備済み
> なので、claude tier 段階 Council の追加配備物は agents 8 個のみ。

## P3（事後確認・評価）への引き継ぎ

deployment 完了後、最初の autonomous loop 試運用で以下を観測する（philosophy.md 第 7 条 P3）：

- gemini-review が PR review を投稿するか
- auto-merge workflow が opt-in 動作するか
- harness-verify or 等価な構造的 verifier が paths filter で発火するか
- destructive change detector / circuit breaker（v5.6.x patch 候補）の必要性

観測結果は `delivery/SELF-VERIFICATION-*.md` または DELIVERY.md に記録、必要に応じて Type C 献上で SPEC/REGIME 更新提案。

## 後方互換性

- `dev_mode: autonomous` が選ばれない限り本機構は起動しない
- 既存 LC ≥ 1 プロジェクト（dev_mode が github_assisted のまま）には強制適用なし
- 利用者が autonomous_scope を後から `full` に変更したい場合は、spec-architect 対話で明示要請 → 本機構を起動

## 関連 skill / reference

- `crosscut-autonomous-drive/SKILL.md` — deployment ヘルパー本体
- `crosscut-autonomous-drive/references/placeholder-spec.md` — placeholder 一覧
- `crosscut-autonomous-drive/references/setup-checklist.md` — 利用者プロジェクト側 setup 手順
- `dev-env-spec.md` Level C — autonomous_scope 別の deploy 機能表
- `philosophy.md` 第 7 条 — DH AI 組織論（4 役割 + サポート構造、Person 責務 P1〜P4）

---

## 入口側 deployment 手順（v5.7.0 追加）

`autonomous_scope: full` の運用で `crosscut-issue-implementer` の workflow（issue-pickup.yml）も deploy する。出口側（gemini-review.yml + auto-merge.yml）と一緒に配置する。

### 配置成果物（autonomous_scope: full、v5.7.0 拡張）

```
利用者プロジェクト/
├── .github/workflows/
│   ├── auto-merge.yml             # v5.6.0 から
│   ├── gemini-review.yml          # v5.6.0 から
│   └── issue-pickup.yml           # v5.7.0 で追加（placeholder 置換済）
├── label set:
│   ├── ready-for-ai               # 入口 GO サイン (v5.7.0 で必須化)
│   ├── auto-merge                 # 出口 GO サイン
│   ├── do-not-merge               # 出口 block
│   ├── do-not-pickup              # 入口 block (v5.7.0 追加)
│   └── (filter 結果 label 群、v5.7.0 で AI が自動付与):
│       in-progress / needs-clarification / out-of-scope /
│       focus-mismatch / too-complex / circuit-broken / pickup-failed /
│       untrusted-author
├── REGIME.md:
│   └── ## current_focus セクション (v5.7.0 で必須化、Issue pickup 判定で参照)
└── Repository Secrets:
    ├── GH_REVIEW_PAT (v5.5.1 から)
    └── GEMINI_API_KEY (v5.5.0 から、v5.7.0 で「実装」用途にも転用)
```

### Spec-architect 対話で取得すべき値（v5.7.0 拡張）

| 項目 | 用途 |
|---|---|
| `${ALLOWED_AUTHORS}` (auto-merge + issue-pickup 共通) | 信頼境界 |
| `current_focus.type / target / since / priority` | Issue pickup judging |
| autonomous_scope | full / merge_gated / custom |

### Person 責務との対応（v5.7.0 入口側追加）

`autonomous_scope: full` 時の人間関与は以下 4 場面に集約（philosophy 第 7 条 P1〜P4）：

- **P1 発案**: 新機能 / バグ修正のアイデアを思考
- **P2 ブレスト**: AI と対話して具体化、AI が Issue 作成 + label `ready-for-ai` 付与（人間は方向性を伝えるのみ、Issue 化は AI）
- **P3 事後確認・評価**: 自動 merge 完了後に PR を振り返り
- **P4 暴走時介入**: `do-not-merge` / `do-not-pickup` label 付与、`circuit-broken` 解除

入口側 deploy で完成: 「対話 → Issue → 自動 pickup → 実装 → PR → 多層検証 → 自動 merge → 次 Issue」のフル自律 loop。
