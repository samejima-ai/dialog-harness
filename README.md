<div align="right">

**日本語** ｜ [English](./README.en.md)

</div>

# dialog-harness

> **人間は頭と口を動かす。AI は手を動かす。**
>
> 対話だけで仕様を生み、AI が自律で実装し、人間は承認する — そのための憲法と機構の集合体。

`dialog-harness`（DH）は、Claude Code 上で動く **AI 自律駆動開発のためのメタフレームワーク** です。Skill / Hook / Workflow を組み合わせ、人間の関与を「発案・ブレスト・事後確認・介入」の 4 点（P1〜P4）に絞り込みます。

---

## 哲学 — 8 条憲法

| # | 条 | 一言で |
|---|---|---|
| 1 | **フラクタル原則** | 同じ「擦り合せループ」が全階層で反復する |
| 2 | **Shift Left** | 問題は可能な限り左（上流）で解く |
| 3 | **情報純度** | エージェント間通信の情報損失を前提にコスト計算する |
| 4 | **人間責務の明確化** | 人間は頭と口、AI は手。境界を侵さない |
| 5 | **献上哲学** | L1 → 人間への単方向受け渡し（A/B/C/D の 4 タイプ） |
| 6 | **人間 ≒ Council** | 人間と合議制 AI は判断機構として対称（H/C カテゴリで分離） |
| 7 | **AI 組織論** | 4 役割（L0/L1/L2/Council）＋ サポート構造のみ |
| 8 | **自律性 + 哲学ガードレール** | 観測 → 候補化 → **人間最終承認** の 3 段階を必ず経由 |

原典：[`philosophy.md`](.claude/skills/layer0-spec-architect/references/philosophy.md)

---

## 使い方

### 1. 取り込み

`.claude/skills/` を自プロジェクトに配置。`crosscut-autonomous-drive` Skill が GitHub Workflow テンプレ・ラベル・Secrets セットアップを案内します。

```bash
# 自プロジェクトのルートで
cp -r dialog-harness/.claude/skills .claude/
cp dialog-harness/.claude/hooks.json .claude/
```

### 2. 対話で仕様を生む（L0）

Claude Code に話しかけるだけで `layer0-spec-architect` が起動し、`SPEC.md` / `DONT.md` / `REGIME.md` を生成します。

```
> 妻のための献立メモアプリを作りたい。まだイメージしかない。
```

### 3. 実装を任せる（L1）

仕様が固まったら：

```
> 実装して
```

`layer1-autonomous-dev` が自律実装し、`layer1-independent-reviewer` が独立検証し、`HANDOFF.md` を献上します。

### 4. PR を流す（autonomous-drive）

`autonomous_scope: full` 構成では、Issue → 実装 → PR → CI → レビュー → auto-merge → 次 Issue が AI で連結します。人間の介入は `do-not-merge` / `human-review-needed` ラベルで即座に効きます。

---

## フロー

```mermaid
flowchart LR
    H([人間：発案 P1]):::human --> L0
    L0[L0 spec-architect<br/>対話で仕様化]:::l0 --> SPEC[(SPEC.md<br/>DONT.md<br/>REGIME.md)]
    SPEC --> L1
    L1[L1 autonomous-dev<br/>自律実装]:::l1 --> REVIEW
    REVIEW[L1 independent-reviewer<br/>独立検証]:::l1 --> PR
    PR{{PR / CI / drift / philosophy<br/>多層検証}}:::cc --> COUNCIL
    COUNCIL[Council<br/>拮抗時のみ合議]:::council --> MERGE[auto-merge]:::cc
    MERGE --> H2([人間：事後評価 P3]):::human
    H2 -.停止介入 P4.-> PR
    H -.方向修正.-> L0

    classDef human fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef l0 fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef l1 fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef cc fill:#f3e8ff,stroke:#9333ea,color:#581c87
    classDef council fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
```

人間が触るのは **発案（P1）／ブレスト（P2）／事後確認（P3）／暴走介入（P4）** の 4 点だけ。それ以外は AI が担います。

---

## Council — 判断を肩代わりして認知負荷を下げる

開発中に「A と B どっちにする？」「この変更、本当に入れていい？」という判断が連続する。人間が都度考えると認知負荷が高くなり、開発が止まる。

**Council は判断を AI に肩代わりさせる合議機構**です。人間は推薦を見て「OK」か「待って」を言うだけ。拮抗した時だけ最終判断を人間に返す。

### 3 ペルソナ独立型 — 「議論しない」設計

Council は **議論（dialogue）しません**。3 つのペルソナ（経営者・開発者・哲学者）が **互いの発言を見ずに独立して意見を出し**、システムが加重で集計します。

これは AI 特性への対応です：

| AI の弱点 | Council の対処 |
|---|---|
| context が混ざると意見が引きずられる（雷同・追従） | 各ペルソナを独立 context で実行、出力後に集計 |
| 議論プロセスでノイズが累積する | 議論せず、初動の意見だけを採用 |
| 多数派形成のバイアス | 重み（weight）で意見の質を担保、少数意見は `minority_opinion` で保存 |

→ **「合議だが議論ではない」**。各 AI の純度の高い意見だけを集めて加重判定する。

### Council が引き受ける判断の例

- 実装方針 A vs B vs C のトレードオフ
- リリースバージョンの判定（minor 昇格か major か）
- 既存の承認モデルを変更してよいか
- 不可逆な操作に踏み込んでよいか

### 加重判定の式

```
weighted_score(stance) = Σ (各ペルソナの weight × confidence)
                            ← その stance を支持したペルソナのみ集計

最大 weighted_score を持つ stance が recommended。
judgment_confidence が閾値（≈ 0.5）以上なら auto_agree、未満なら escalate_to_human。
```

### パターン①：全員一致 → 圧倒的多数

auto-merge を opt-in（明示 GO）から opt-out（沈黙 = 承認）に変えるかの判定（`amrev1`）：

| ペルソナ | weight | × | confidence | = | score | 投票 |
|---|---:|---|---:|---|---:|---|
| 経営者 | 3 | × | 0.70 | = | **2.10** | C |
| 開発者 | 3 | × | 0.82 | = | **2.46** | C |
| 哲学者 | 5 | × | 0.55 | = | **2.75** | C |
| **合計** | **11** | | | | **7.31** | **C 一色** |

3 者全員が C に集約 → C の weighted_score が全 weight の 100% を占有 → `auto_agree` → **人間は結果を確認するだけ**。

```yaml
conflict_type: "unanimous"
judgment_confidence: 0.80
recommended: >
  C: ハイブリッド採用。philosophy / harness 領域は opt-in 維持、
  定型領域のみ opt-out。境界を SPEC で不変化する。
consensus_mode: "auto_agree"
human_escalated: false
```

### パターン②：意見が割れた → 加重で機械的に解決

自律駆動 WF の基底構造を「案H: Hybrid（薄く始めて観測で厚化）」「案N: WF 多様化しない（形状単一化）」のどちらにするか（`wfbase1`）：

| ペルソナ | weight | × | confidence | = | score | 投票 |
|---|---:|---|---:|---|---:|---|
| 経営者 | 3 | × | 0.70 | = | 2.10 | **案 H** |
| 開発者 | 3 | × | 0.85 | = | 2.55 | **案 H** |
| 哲学者 | **5** | × | 0.65 | = | 3.25 | **案 N** |

**stance ごとの集計：**

| stance | 支持者 | weighted_score |
|---|---|---:|
| **案 H** | 経営者 + 開発者 | **4.65** ← 勝ち |
| 案 N | 哲学者（単独） | 3.25 |

哲学者は単独で weight 最大（5）だが、経営者 + 開発者の合計（4.65）が上回り **案 H 採用**。
`judgment_confidence: 0.75`（閾値超）→ `auto_agree` → **人間は結果を確認するだけ**。

ただし哲学者の少数意見は `minority_opinion` に保存され、運用原則として組み込まれます（「WF 形状単一性を最優先、override は観測駆動で最小限」）。

> **多数決ではなく加重評価** — 哲学者の weight が最大なのは「conception カテゴリでは長期影響が最重要」という事前ルール（`council-weights.md`）から決まる。重みは判定ごとに固定で、AI が動かせない。

### パターン③：confidence が低下 → 人間にエスカレーション

もし `judgment_confidence` が閾値（通常 0.5）を下回ると、`consensus_mode: escalate_to_human` となり判断が人間に戻ります。これは主に以下で発生：

- いずれかのペルソナが options 外の「第3の道」を提示した（例：`vrfy01` で哲学者が V-1 を拡張する提案）
- H カテゴリ（哲学変更・ルート設計変更等）に該当する判定
- いずれかペルソナの confidence が著しく低い

`minority_opinion` フィールドに少数意見が保存され、人間は両論を見て止揚（β 統合）するか、片方を採用するかを決めます。

> 普段は Council に任せ、本当に割れた時だけ人間が出る。
> AI に意見を肩代わりさせ、人間は最終判断に集中する。

全判定は [`history/COUNCIL-LOG.md`](history/COUNCIL-LOG.md) に append-only で蓄積され、透明性と振り返りを保証します。

---

## 主要な Skill

| Layer | Skill | 役割 |
|---|---|---|
| **L0** | `layer0-spec-architect` | 新規仕様策定・継続開発・振り返り |
| L0 | `layer0-archeo-architect` | 既存コードの意図復元（リファクタ前段） |
| L0 | `layer0-onboarding` | 既存プロジェクトの harness 後付け化 |
| **L1** | `layer1-autonomous-dev` | 自律実装 |
| L1 | `layer1-independent-reviewer` | 独立検証 |
| **L2** | `layer2-orchestrator` | サブドメイン分割（複雑時のみ） |
| L2 | `layer2-integration-verifier` | 跨ぎ整合性検証 |
| **Council** | `crosscut-council` | 拮抗時の合議判定（3 ペルソナ加重） |
| support | `crosscut-autonomous-drive` | auto-merge / Workflow テンプレ展開 |
| support | `crosscut-issue-dispatcher` / `crosscut-issue-implementer` / `crosscut-issue-quality-gate` | Issue 自動生成・自動実装・品質ゲート |
| support | `crosscut-verifier-drift` | SPEC ↔ 実装の drift 検出 |
| support | `crosscut-feedback-loop` | 検証結果の還流ルーティング |

---

## 動作要件

- [Claude Code](https://claude.ai/code)（CLI / Web / IDE 拡張）
- Python 3（hook bootstrap 用）
- Git / GitHub（`autonomous` モード時）

---

## 環境設定（人間が手を動かす範囲）

セキュリティ上の理由で **AI が代行できない設定** があります。これは「AI ができないことを人間がする」（philosophy 第 4 条）の具体例です。
**非エンジニアでも、Claude Code に直接聞けばステップを教えてくれます。**

### 必須項目

| 項目 | なぜ AI がやれないか | AI のサポート |
|---|---|---|
| Claude Code のインストール | OS への実行権限・ブラウザ認証が必要 | インストール手順を対話で案内 |
| GitHub アカウント / Repo 作成 | 認証が個人に紐づく | 手順説明・初期化ガイド |
| Personal Access Token 発行 | 秘密鍵の生成権限は人間専属 | スコープ選択・発行画面の案内 |
| Repository Secrets 設定 | Settings 編集に admin 権限が必須 | 必要 Secret 名と取得元を説明 |
| GitHub Labels 作成 | autonomous-drive が要求 | `crosscut-autonomous-drive` Skill が一括作成手順を案内 |

### `autonomous` モードで必要な Secrets

| Secret 名 | 用途 |
|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | GitHub Actions 上で Claude Code を起動 |
| `GH_REVIEW_PAT` | auto-merge / gemini-review workflow が PR 操作に使用 |
| `GEMINI_API_KEY` | gemini-review（任意 / fallback） |

### autonomous-drive 用のラベル

| ラベル | 役割 |
|---|---|
| `ready-for-ai` | Issue を AI 着手対象にする GO サイン |
| `do-not-merge` | auto-merge を停止（P4 介入） |
| `human-review-needed` | 人間レビューを必須化（P4 介入） |
| `pickup-failed` | 自動 pickup の中断記録 |

### 「分からないことは AI に聞く」が前提

DH は **非エンジニアのための対話型ハーネス** です。上記の設定で詰まったら、Claude Code に直接こう聞けば OK：

```
> GH_REVIEW_PAT の発行手順を教えて
> Repository Secrets の設定画面はどこ？
> autonomous-drive のラベルを一括作成して
```

`crosscut-autonomous-drive` Skill がガイド役を担います。手を動かすのは人間ですが、考える内容は AI が肩代わりします。

---

## 協力者募集

DH は **「人間が手を動かさずに済む開発」を本気で追求する** 実験プロジェクトです。以下のような方を歓迎します。

- **AI 自律開発の境界線を一緒に押し広げたい人**
- **メタフレームワーク設計（Skill / Hook / Workflow）に興味がある人**
- **哲学と工学の両面で議論したい人** — 8 条憲法は Council 諮問で改訂され続けています
- **自プロジェクトに DH を導入し、振り返り（retro）を還流してくれる人**

### 入り方

1. Issue / Discussion に「触ってみた」「ここが詰まった」「こう変えたい」を投げる
2. `templates/rituals/wave-end-retrospective.template.md` で振り返りを書いて PR を出す
3. Council 諮問（`history/COUNCIL-LOG.md`）の判定に異論があれば、minority opinion を立てる

> AI ができないことを人間がする。人間がしなくていいことを AI がする。
> だから **人間 ≒ Council** — 判断機構として対称になる。（philosophy [第 4 条](.claude/skills/layer0-spec-architect/references/philosophy.md) × [第 6 条](.claude/skills/layer0-spec-architect/references/philosophy.md)）

---

## ライセンス・参照

- 哲学原典：[`.claude/skills/layer0-spec-architect/references/philosophy.md`](.claude/skills/layer0-spec-architect/references/philosophy.md)
- 改修履歴：[`history/CHANGELOG.md`](history/CHANGELOG.md)
- 設計意図：[`history/INTENT.md`](history/INTENT.md)
- 移行ガイド：[`docs/`](docs/)
