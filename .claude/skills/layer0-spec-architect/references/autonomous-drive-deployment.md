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
| `${SCOPE_PATHS}` | 「gemini-review が発火する paths は？」 | `src/**`, `tests/**`, `docs/**` 等の標準セット |
| `autonomous_scope` | dev_mode autonomous 確定後の 1 問（dialog-questions.md 参照） | `full` |

これらを取得後、`crosscut-autonomous-drive` skill を起動する。

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
│       └── gemini-review.yml    # placeholder 置換済
├── (label set: ready-for-ai / auto-merge / do-not-merge を GitHub UI で確認)
└── (Repository Secrets: GH_REVIEW_PAT / GEMINI_API_KEY を GitHub UI で設定)
```

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
