# DH Upgrade Specification v5.8.0

## 概要

| 項目 | 内容 |
|---|---|
| バージョン | v5.8.0 |
| 種別 | minor |
| リリース日 | 2026-05-04 (予定) |
| 主要機能 | crosscut-issue-quality-gate 新設 |
| 後方互換性 | 完全維持 |

## 新機能

### crosscut-issue-quality-gate skill 新設

**概要**: Issue の品質を 12 軸でチェックする横断機構

**主要機能**:
- 12 軸品質チェック（機械検査 + AI 推論ハイブリッド）
- 並列安全性機構（論理・意味・依存コンフリクト事前検知）
- Council 観測性連携（軸 vi で入力データレイヤー整合保証）
- フラクタル原則適用（DH 自身も Quality Gate 通過）

**発動契機**:
- (a) crosscut-issue-dispatcher 内部から必ず通過
- (b) L0/Council/D4〜D2 献上時に明示呼び出し  
- (d) GitHub Actions で ready-for-ai ラベル付与時に最終ガード

## アーキテクチャ判断

### AD-031: Issue 段階品質ガード機構の独立 skill 化

| 項目 | 内容 |
|---|---|
| 状況 | autonomous-drive パイプラインで Issue が AI 自律駆動の初期 context となる構造上、Issue の品質 = プロジェクトの成功率。人間対話起点・Council 献上起点・D4〜D2 献上起点いずれの Issue も、品質バラつきがそのまま実装品質に伝播する。現状、SPEC/ADR 差分起点の crosscut-issue-dispatcher はあるが、Issue 段階での独立チェック機構は未配置 |
| 判断 | **12 軸品質チェック** + **並列安全性軸** を持つ独立 skill `crosscut-issue-quality-gate` を新設。(a) dispatcher 内部通過 + (b) 明示呼び出し + (d) GitHub Actions 最終ガードの 3 発動契機。**軸 vi（観測性統一）** で Council 入力データレイヤー整合保証、**軸 ix（並列安全性）** で 4 段階フィルター（scope/mutex/depends-on/AI推論）による論理・意味・依存コンフリクト事前検知。**フラクタル原則徹底** で DH 自身も例外なく本 Gate 通過 |
| 根拠 | (a) Issue 品質 = autonomous-drive 成功率の構造的因果、(b) 起点に依存しない横断機構としての独立性確保、(c) Council 合議成立の前提条件として観測性データ整合が必須、(d) Issue 並列実行時の git 検出不能コンフリクト（論理・意味・依存）の事前回避、(e) philosophy.md 第 1 条フラクタル原則の「規律の自己相似性」実装、(f) Council 起動条件（複数案拮抗・confidence < 0.6・不可逆操作・SPEC 矛盾）のいずれにも該当せず Council 諮問は不要 |
| 影響 | 新規 skill 1 件 + references 7 件 + assets 1 件 + dh-upgrades 1 件 + workflow template 1 件の追加。既存 7 ファイル（ARCH-DECISIONS / 4 crosscut-* SKILL / spec-architect SKILL / philosophy.md / issue-pickup.yml.template）への必要最小限参照追記。ラベル規約（scope/mutex/refactor/freeze-period）配布。philosophy.md / harness-verifier / 既存 skill 機能への影響ゼロ。**完全後方互換**: 新 skill 不在でも DH ベースは通常動作、既存 Issue 形式変更なし、既存プロジェクトへの強制配布なし |

## 新規ファイル（11件）

### Skill 本体
- `.claude/skills/crosscut-issue-quality-gate/SKILL.md`

### References（7件）
- `.claude/skills/crosscut-issue-quality-gate/references/twelve-axes.md`
- `.claude/skills/crosscut-issue-quality-gate/references/machine-checks.md`
- `.claude/skills/crosscut-issue-quality-gate/references/ai-judgment-rubric.md`
- `.claude/skills/crosscut-issue-quality-gate/references/activation-protocol.md`
- `.claude/skills/crosscut-issue-quality-gate/references/council-observability-link.md`
- `.claude/skills/crosscut-issue-quality-gate/references/parallel-safety.md`
- `.claude/skills/crosscut-issue-quality-gate/references/fractal-application.md`

### Assets
- `.claude/skills/crosscut-issue-quality-gate/assets/issue-quality-checklist.template.md`

### DH Upgrades  
- `dh-upgrades/upgrade-spec-v5.8.0.md`（本ファイル）

### Templates
- `templates/github-workflows/issue-quality-gate.yml.template`

## 既存ファイル変更（7件）

### History
- `history/ARCH-DECISIONS.md`: AD-031 追記

### Skill Updates
- `.claude/skills/crosscut-issue-dispatcher/SKILL.md`: 発動契機 (a) 参照追加
- `.claude/skills/crosscut-issue-implementer/SKILL.md`: 発動契機 (d) 参照追加  
- `.claude/skills/layer0-spec-architect/SKILL.md`: 発動契機 (b) L0 起点参照追加
- `.claude/skills/crosscut-council/SKILL.md`: 発動契機 (b) Council 起点参照追加

### Philosophy Update
- `.claude/skills/layer0-spec-architect/references/philosophy.md`: 軸 vi = Council 入力基盤の明文化（第 6 条補足）

### Workflow Integration
- `templates/github-workflows/issue-pickup.yml.template`: concurrency group の方針更新（軸 ix 要求）

### concurrency 制約注記（PR #50 review feedback で v5.8.0 内に確定）

軸 ix の理想形は「同 scope の Issue は直列、別 scope は並列」だが、**GitHub Actions の workflow-level `concurrency` block は `steps.*` 参照不可**（YAML パース時点で評価）のため、Issue ラベルから動的に scope を抽出した group 名を組み立てることが完全実装できない。

v5.8.0 の対処：
- `issue-pickup.yml.template` の concurrency は **Issue 番号ベース（v5.7.x 互換）** に後退
- scope 別並列制御は **v5.8.x patch で本実装予定**（jobs 内自前実装 or 静的 contains chain による expression）
- 本制約は Quality Gate 軸 viii「テスト粒度」の改良候補（workflow YAML expression 制約検証を本番前 smoke test に組み込む）として記録

これは observation-driven の SPEC 改訂事例（実装してみて初めて GitHub Actions 制約が判明）。

## 12 軸詳細

| # | 軸 | 機械検査 | AI 推論 | 合格基準サマリ |
|---|---|---|---|---|
| A | 仕様整合 | SPEC.md/DONT.md grep | 意味的整合 | プロジェクト固有 SPEC と矛盾なし、DONT 違反なし |
| B | データ整合 | schema diff・migration 必須化 | 後方互換意図 | schema-evolution.md 準拠、破壊的変更なし or 移行計画明示 |
| C | コード整合 | 既存抽象 grep（同名 export 検出） | 重複抽象判定 | 既存抽象を再利用、新規抽象作成は理由必須 |
| D | 依存整合 | package.json diff・licence-checker・bundle size | メンテ状況判定 | ライセンス OK、bundle 増加 ≤10%、最終 commit <12ヶ月 |
| E | 品質均一化 | テスト/sensor 必須項目 grep | テスト粒度妥当性 | 既存と同等以上のテスト/sensor 規格 |
| ii | 重複検出 | 既存 Issue title/body の n-gram 類似度 | 意味的重複判定 | 類似度 >0.7 の既存 Issue が無い、または diff 明示 |
| iii | セキュリティ | secrets scan・auth 関連 grep | 認可モデル整合 | OWASP top 10 観点、認可表との整合 |
| v | 後方互換 | API/DB schema diff・semver 必須化 | 影響範囲判定 | 破壊的変更時はロールバック計画必須 |
| **vi** | **観測性統一** | 収集層: schema 統一・命名規則 grep / 提示層: dashboard 項目数・カーディナリティ閾値 | 収集と提示の二層整合性判定 | **収集層=精緻・構造化、提示層=P3 が一目で解釈可能、両層で命名規則統一** |
| vii | ドキュメント波及 | INDEX.md/README/ADR 更新 grep | — | 該当ドキュメントへの更新含む |
| viii | テスト粒度 | テストファイル存在・カバレッジ閾値 | TDD 妥当性 | Issue 段階で test-first 計画明示 |
| **ix** | **並列安全性** | scope/mutex/depends-on ラベル grep + in-progress Issue list 取得 | 影響範囲衝突の意味的判定 | **scope/mutex 整合、depends-on 循環なし、in-progress と影響範囲衝突なし、refactor:major 検出時は freeze 推奨** |

## 並列安全性（軸 ix）詳細

### 4 段階フィルター

```
[1] scope ラベル (機械的) ← 基本ガード、workflow concurrency 分割
       ↓
[2] mutex ラベル (機械的) ← 明示排他、共有抽象を保護
       ↓
[3] depends-on 宣言 (機械的) ← 論理依存を表現、順序保証
       ↓
[4] AI 推論 ← (2)(3) の見落としを意味的に検知（in-progress Issue との影響範囲衝突）
```

### ラベル規約

| ラベル種別 | 例 | 用途 |
|---|---|---|
| `scope:*` | `scope:db` / `scope:frontend` / `scope:auth` / `scope:docs` | 基本並列ガード（concurrency group） |
| `mutex:*` | `mutex:auth-model` / `mutex:state-machine` | 共有抽象の明示排他 |
| `refactor:*` | `refactor:major` / `refactor:minor` | Big Refactor 特例 |
| `freeze-period` | （単独） | リリース直前の全凍結 |

### Big Refactor 特例

`refactor:major` 付与時は他全 Issue に `do-not-pickup` 自動付与で一時 freeze。

## 観測性統一（軸 vi）詳細

### 二層モデル

| 階層 | 目的 | 合格基準 |
|---|---|---|
| **収集層** | 後追い分析・LLM 推論用 | 精緻・構造化・高解像度、データを薄くしない |
| **提示層** | P3 一目理解用 | ダッシュボード項目数≤8、カーディナリティ上限、業務粒度 |

### Council 連携

観測性規格のバラつき = Council 3 ペルソナが同じ事実を見られない = 合議が成立しない、の構造的因果を回避。軸 vi は **Council 入力データレイヤー** 整合保証として機能。

## フラクタル原則適用

### DH メタ自己適用

- DH 自身の Issue 化（dh-upgrades 派生 Issue 含む）も例外なく本 Gate 通過
- 本 Issue #46 自身が完成後に Gate を通すべきだった最初の事例として参照
- 完成後の自己適用テスト: `delivery/self-gate-check-AD010.md` 出力

### 既知の減点項目

本 Issue 初版での軸 A / viii 自己違反を最初の減点項目として記録:
- 軸 A: 必須セクション（再現手順 / 期待動作 / 受入条件）欠如
- 軸 viii: test-first 計画未明示

## 移行ガイド

### 既存プロジェクトへの影響

**影響ゼロ**: 
- 既存 workflow は変更なしで動作継続
- 既存 Issue 形式は変更不要  
- 後方互換性完全維持

**任意導入**:
- v5.8.0 以降の新規 Issue から本 Gate 適用開始
- 段階的導入（一部軸のみ有効化）も可能
- プロジェクト固有設定で軸別有効/無効制御

### 推奨導入手順

1. **Phase 1**: 基本軸のみ（A, ii, iii）
2. **Phase 2**: 品質軸追加（E, vii, viii）  
3. **Phase 3**: 高度軸追加（B, C, D, v, vi, ix）

### 必要な準備

1. **ラベル作成**: scope/mutex/refactor ラベルをプロジェクトに追加
2. **設定ファイル**: `.github/issue-quality-checklist.yml` をカスタマイズ
3. **workflow 更新**: `issue-pickup.yml` の concurrency を scope ベースに変更（任意）

## 検証要件

### harness-verifier 検査

- frontmatter 検査: 新 skill の YAML frontmatter 構文確認  
- 参照 path 検査: references/ 内リンクの整合性確認
- 依存グラフ循環検査: 新 skill 追加による循環依存なし確認
- 5 層構造検査: D4 配置の適切性確認
- 用語辞書検査: 新用語の glossary.yml 整合確認

### 機能検証

- 12 軸チェックの実行確認
- 3 発動契機での正常動作確認  
- 並列安全性機構の動作確認
- フラクタル適用（DH 自身への適用）確認

## リスク評価

### 低リスク

- **新機能追加のみ**: 既存機能の変更なし
- **opt-in 設計**: 使わない限り影響なし
- **後方互換**: 既存環境で問題発生なし

### 潜在リスク

- **AI 推論負荷**: 大量 Issue 処理時の性能懸念 → 機械検査メインで軽減
- **複雑性増加**: 12 軸設定の学習コスト → 段階導入・template で軽減  
- **誤検知リスク**: AI 判定の精度懸念 → confidence 閾値・人間判断で軽減

### 軽減策

- 機械検査を優先し、AI 推論は補助的に使用
- 段階導入とプロジェクト固有設定でカスタマイズ性確保
- 緊急バイパス機構で運用継続性保証

## 成功指標

### 定量指標

- Issue 品質向上: Gate 通過後の implementation 成功率向上
- 並列作業効率: コンフリクト事前回避による開発速度向上
- 観測性統一: Council 合意率向上（同じ事実の共有）

### 定性指標  

- 開発者体験: Issue 作成時の品質向上実感
- プロジェクト管理: 品質ばらつき減少実感
- 組織学習: フラクタル原則による規律内在化

## 今後の拡張

### v5.8.x候補

- AI モデル選択制（claude/gpt/gemini）
- カスタム軸の追加機構
- パフォーマンス最適化

### v5.9.0候補  

- Issue テンプレート自動生成
- Council との完全統合
- 多言語プロジェクト対応

### v6.0.0候補

- 軸体系の根本見直し（観測駆動）
- philosophy.md との統合的再構成
- 業界固有軸の標準化

## まとめ

v5.8.0 は dialog-harness における Issue 品質管理の標準化を達成する重要なマイルストーンである。12 軸品質チェック・並列安全性機構・Council 観測性連携・フラクタル原則適用により、AI 自律駆動開発の基盤品質を向上させる。

完全な後方互換性を保ちつつ、段階的導入により既存プロジェクトへの負荷を最小化。DH 自身への適用により、規律の自己相似性（フラクタル原則）を実装し、「靴屋の靴問題」を回避する。

本リリースにより、dialog-harness は単なるツールセットから、品質保証機構を内包した **開発方法論プラットフォーム** へと進化する。