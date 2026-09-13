# L0 ステップ詳細（§3.5 / §3.6 / §4）

> v7.0.0 Phase A F10 で `SKILL.md` から**逐語移送**（SKILL.md を 500 行未満に保つ。内容は不変・リンクのみ本ディレクトリ基準に書き換え）。
> SKILL.md 側は各ステップの骨子とポインタを残す。正本の判定表は各リファレンス（subphase-selection / design-system-spec / regime-assessment）。

## §0 対話 persona ロード — ロード順・起動シナリオ別・override_state

#### ロード順（override 規約）

REGIME.md の `persona.active` で指定された persona を以下の優先順位で探索する。最初に見つかったファイルを採用する：

1. `<project-root>/.dh/personas/<active>.persona.md`（利用者プロジェクト override）
2. `<dialog-harness>/templates/personas/<active>.persona.md`（DH 同梱）

両方とも存在しない場合は default にフォールバックし、その旨を 1 行告げる。

#### 起動シナリオ別

- 既存プロジェクト（REGIME.md 存在）: `## persona` セクションを確認。`active:` 未指定なら `default` 扱い
- 新規プロジェクト（REGIME.md 未存在）: `default.persona.md` で開始。対話中に人間が「ペルソナを ◯◯ に切り替えて」と指示した場合は即時切替し、§4 のモード判定時に REGIME.md へ `persona.active` と `override_state` を反映する

#### `override_state` の適用

- `null`（既定）: persona の `default_state` で State Machine を初期化、以降は条件に従って自動遷移
- 非 null: その状態に **強制固定**。自動遷移は無効化（STEP 1 の `<system_state>` も固定値）
- 対話中に「自動切替に戻して」と発話されたら null に戻し、永続化したければ REGIME.md を更新

切替成功時は新 persona の口調で 1 行告げる（例: 羊 persona なら「これからは羊さんモードで進めますねぇ」）。
本ステップは presentation layer の初期化のみ。仕様策定の中身（logic layer）は persona に依存しない。

## §3.5 サブフェーズ選定と実行 — 起動判定・実行プロトコル・依存順・成果物配置・後方互換・事後追加

#### 起動判定

対話（ステップ 2）で得た情報から **基本 5 問** で必要サブフェーズを決定する。全問が「不要」なら本ステップは完全スキップする。

| # | 質問 | 起動判定対象 |
|---|---|---|
| S1 | データを保存する必要があるか？ DB を使うか？ | L0-2 ドメインモデル |
| S2 | 外部のシステムや API とつなぐか？ | L0-3 API 契約 |
| S3 | 画面はいくつあるか？ 遷移は複雑か？ | L0-4 状態遷移 |
| S4 | 複数ユーザーで使うか？ 権限の違いはあるか？ | L0-5 認可 |
| S5 | 時間経過や承認で状態が自動的に変わるか？ | L0-6 層間不変条件（2 以上のサブフェーズ起動時のみ） |

詳細な判定表（完全 / 簡易 / スキップ）は `subphase-selection.md` の起動判定表を参照。

#### 実行プロトコル

各サブフェーズは「対話 α → 生成 β → 検証 γ → 判定 δ」の 4 フェーズで構成される独立 AI 呼び出し単位。
共通骨格は `subphase-common-protocol.md`、各サブフェーズ固有プロトコルは以下:

- `subphase-l02-domain.md` — Zod + TypeScript ドメインモデル
- `subphase-l03-api.md` — TypeSpec API 契約
- `subphase-l04-transition.md` — XState + Mermaid 状態遷移
- `subphase-l05-authz.md` — OpenFGA 認可モデル
- `subphase-l06-invariants.md` — Gherkin 層間不変条件（Happy / Sad / Evil 三分類）

#### 依存順

L0-1 → L0-2 → (L0-3 ‖ L0-4) → L0-5 → L0-6 の順序で実行。L0-3 と L0-4 は並列可。

#### 成果物配置

起動時のみ `spec/` ディレクトリを新設し、以下を配置:

```
spec/
├── subphase-manifest.md  # 選定結果・確度・起動ログ（pre-official、Phase 2 で REGIME.md に統合予定）
├── domain.ts             # L0-2 起動時
├── api.tsp               # L0-3 完全モード時
├── api-signatures.ts     # L0-3 簡易モード時
├── state-machine.ts      # L0-4 完全モード時
├── state-diagrams.md     # L0-4（完全/簡易問わず）
├── authz.fga             # L0-5 完全モード時
├── authz-matrix.md       # L0-5 簡易モード時
└── invariants.feature    # L0-6 起動時
```

全サブフェーズがスキップのプロジェクトでは `spec/` 自体を生成しない。

#### 既存プロジェクトとの後方互換

`spec/subphase-manifest.md` が存在しない既存プロジェクトで本ステップを通過しても、従来フロー（ステップ 1→4→…→7.6）と同一挙動となる（新規起動のみ影響）。

#### 事後追加

プロジェクト進行中のサブフェーズ追加・モード昇格・判定誤り訂正は独立した AI 呼び出しで実行する。プロトコルは `subphase-selection.md` の「事後追加プロトコル」を参照。


## §3.6 DESIGN.md 生成判定 — 起動判定・対話プロトコル・生成物・検証経路・非起動条件・後方互換

#### 起動判定

1 問だけ投げる。AI 推定で「明らかに UI あり」なら投げずに仮判定（通知のみ）。

| # | 質問 | 起動判定 |
|---|---|---|
| DG1 | 「このプロジェクトは画面（UI）を持ちますか？ Web / モバイル / デスクトップのいずれでも」 | UI あり=**起動** / 非対面（CLI / API / ライブラリ）=**スキップ** |

#### 対話プロトコル（DG2〜DG4、起動時のみ）

UX 3問プロトコル（§2.5）と同じ思想で 3 問に絞る。未回答時は AI が実践デフォルトで自動補完する。

| # | 質問 | 格納先 | 未回答時のデフォルト |
|---|---|---|---|
| DG2 | ブランド・トーンを 1 行で言うと？ | DESIGN.md `## Overview` | 「クリーン、プロフェッショナル、高密度」 |
| DG3 | 「あの UI が好き」という参考はある？ | DESIGN.md `## Overview` 末尾 | UX 3問 Q3 の参考類似サービスを流用 |
| DG4 | プライマリカラー（CTA 色）は？ HEX / 色名 / 「お任せ」のいずれかで | YAML `colors.primary` | `#1A73E8`（Material Blue、WCAG AA 適合） |

詳細な対話例・自動補完根拠・YAML スキーマ・Do's and Don'ts の重要性は `design-system-spec.md` を参照。

#### 生成物

- **DESIGN.md** — プロジェクトルート直下に配置。`../assets/design-md-template.md` のテンプレートにプレースホルダー置換した実体
- **INDEX.md** に視覚仕様への 1 行参照を追加
- **CLAUDE.md** の `## 参照` に `視覚仕様: DESIGN.md` を 1 行追加

#### 検証経路（重要）

DESIGN.md の真の検証は **コードファーストの静的検査では完結しない**。philosophy 三拍子「仕様に合う・動く・使える」のうち「使える」は E2E + Vision 経路でのみ判定可能。L1 (autonomous-dev) と L1-independent-reviewer は philosophy 5 層検出スタックの第 2 層 (Playwright スクショ) と第 5 層 (Vision モデル判定) を必ず通す。§7.4 自己検証のトークン一貫性検査は第 1 層（必要条件）であり、これ単独で UX を保証しない。詳細は `design-system-spec.md` §E2E 視覚検証 参照。

#### 非起動条件

以下では DG1 を投げずに DESIGN.md スキップを確定する:

- SPEC.md に「CLI」「ライブラリ」「バッチ」「webhook ハンドラ」のみ記載
- バックエンドサービス単体運用で対面 UI を持たない（event-sourcing バックエンド単体 / API サーバ単体 等。イベント履歴ダッシュボード等の UI を持つ場合は起動する）
- DOMAIN-CONTEXT.md に「ヘッドレス」「内部 API のみ」明示

#### 既存プロジェクトとの後方互換

`DESIGN.md` 不在のプロジェクトはこれまで通り動作する（生成義務なし）。
LC ≥ 1 プロジェクトへの後付け追加は事後追加プロトコル（`design-system-spec.md` §運用規律）参照。


## §4 モード判定 — dev_mode 軸・autonomous_scope 軸

#### dev_mode 軸（v5.0.0 追加 / v5.6.0 で `autonomous` 本格化）

GitHub 連携前提の自律駆動を 3 段階で表現する追加軸。規模・チーム軸と並列で動的判定する。
詳細プロトコルは `regime-assessment.md` の「dev_mode 判定」セクション参照。

| dev_mode | GitHub | Actions | Issue 自動化 | 並列実装 | 自動 merge | 人間関与 |
|---|---|---|---|---|---|---|
| local_only | × | × | × | × | × | 全 Layer |
| github_assisted | ○ | 任意 | × | 手動 | × | L0 + 承認 |
| autonomous | ○ | ○ | ○ | 自動 | ○（scope 依存）| P1〜P4 のみ |

旧名 `github_autonomous` は v5.6.0 で `autonomous` にリネーム（autonomous_scope 軸との整合）。後方互換: 既存 REGIME.md で `github_autonomous` 記述は `autonomous` + `autonomous_scope: full` と等価扱い（自動マイグレーションは行わない、新規プロジェクトから新名を使用）。

判定フロー：
1. 質問1：「GitHub 使う？」
2. No → `local_only` 確定
3. Yes → 規模 + LC から推論（v5.6.0 時点）
   - M1 → `github_assisted`
   - M2, LC ≤ 1 → `github_assisted`
   - M2-L2, LC ≥ 1 → `autonomous`（質問 2 で `autonomous_scope` 確認）
4. 推論結果を 1 回のみ確認、ユーザー裁量で昇格・降格可

dev_mode 昇格・降格は手動 + ADR 記録必須（spec §3.2.3）。「GitHub 無しでも DH ベースは完全動作」が原則。

#### autonomous_scope 軸（v5.6.0 追加）

dev_mode が `autonomous` の場合のみ意味を持つ。autonomous-drive 機構（PR 作成 / 多層検証 / 自動 merge / 次 Issue 着手）の運用粒度を 3 値で表現する。

| autonomous_scope | 自動 merge | PR review/approve | P3 (事後確認) のタイミング |
|---|---|---|---|
| **full**（デフォルト） | 有効（`auto-merge` label opt-in + 多層検証通過時） | AI（または gemini-review/Copilot 等の独立 critic）| merge 後に P3 |
| merge_gated | **無効**（人間 approve 必須）| 人間が実施 | merge 前に P3 |
| custom | 部分有効（`dev-env-spec.md` Level C 詳細表で指定） | 個別設定 | 個別設定 |

**判定フロー**（dev_mode = `autonomous` 確定後の質問 2）：

```
Q: 自律駆動の度合いを選択してください
   (1) フルオート [デフォルト推奨] = autonomous_scope: full
       人間 = P1〜P4 のみ。AI = Issue 精査〜自動 merge〜次 Issue 着手まで完全自走
   (2) 中度 = autonomous_scope: merge_gated
       自動 merge は無効、PR review/approve は人間が実施（P3 を merge 前に倒す）
   (3) カスタム = autonomous_scope: custom
       個別に設定（dev-env-spec.md Level C 詳細表で指定）
```

**Person 責務（P1〜P4）**: philosophy.md 第 7 条参照。autonomous_scope = `full` 時、人間関与は以下 4 点に集約：
- P1 発案 / P2 ブレスト（Issue 化は AI）/ P3 事後確認・評価 / P4 暴走時介入

`autonomous_scope` の昇格・降格は手動 + ADR 記録必須。デフォルト = `full` で、ユーザー要請時のみ `merge_gated` / `custom` を選択。
