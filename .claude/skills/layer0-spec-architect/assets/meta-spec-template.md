# メタ仕様テンプレート

仕様ドキュメントの記述ルールとテンプレート。
全てのプロジェクト仕様はこのフォーマットに従う。

---

## INDEX.md テンプレート

100行以内。プロジェクト全体の目次として機能する。
エージェントはまずこのファイルを読み、必要な詳細ドキュメントを動的に読み込む。

```markdown
# [プロジェクト名]

## 目的
[1-3行で「なぜこれを作るか」「誰のためか」]

## 機能一覧
- [機能A] → 詳細: SPEC.md#機能A
- [機能B] → 詳細: SPEC.md#機能B
- ...

## スコープ外
→ DONT.md

## 開発体制
→ REGIME.md

## 開発環境
→ CLAUDE.md, .claude/skills/, sensors/

## ドメイン文脈（任意・該当プロジェクトのみ）
→ DOMAIN-CONTEXT.md
（機密情報は DOMAIN-CONTEXT.secret.md に分離。Git 管理外）

## 視覚仕様（任意・UI プロジェクトのみ）
→ DESIGN.md
```

---

## SPEC.md テンプレート

機能仕様の本体。「機能×条件」の粒度を最低ラインとする。

```markdown
# 機能仕様

## WHY（目的）
[このシステムが存在する理由。ビジネス上の価値。]

## WHAT（機能定義）

### [機能名A]

#### 概要
[この機能が何をするかを1-3行で]

#### 条件
- [条件1]: [具体的な数値や挙動の記述]
- [条件2]: [具体的な数値や挙動の記述]

#### Priority
[critical / standard / cosmetic]

Priority は**運用時の検出スタック（建物）**で何階まで使うかを決める。**Shift Left 基盤（土地）は Priority に関わらず常に整備される前提**であり、階数に加算しない。

- **critical**: 第1〜5層すべてを使用（第1層計算的センサー + 第2層 E2E + 第3層 Interaction Cost + 第4層推論的 + 第5層人間判断）
- **standard**: 第1〜3層まで使用（E2E と Interaction Cost まで）
- **cosmetic**: 第1層のみ使用（型・ビルド・テストのみ）

旧記法（高/中/低）は後方互換のため受理する（高=critical / 中=standard / 低=cosmetic）。

#### UX制約（任意）
[UX 3問プロトコルで回答された Must 閾値と禁止挙動]

- Must 閾値: [クリック数・遷移深度・応答時間・完了率・エラー率 等]
- 禁止挙動: [特定操作の禁止や警告表示の必須化 等。DONT.md にも転記]
- 参考類似サービス: [インスピレーション源。AI が類似UXパターンを参照可能にする]

未指定時は業界標準値（クリック 3-5 回・遷移 3 以内・応答 30 秒以内・完了率 95%・エラー率 5%）を適用。詳細は `../SKILL.md` ステップ 2.5 を参照。

#### エッジケース（任意）
[判明しているエッジケースがあれば記述。なければ省略可]

### [機能名B]
...

## 制約
- [守るべき規約、使ってはいけない技術、予算上限等]
- ARC: [選択パターン名]（未指定時は monolith。選択肢は `arc-patterns/` 配下参照）
- 情報代謝 regime（任意・LC ≥ 1）: 定義は layer0-reindex-librarian/references/metabolism-regime.md、パラメータは REGIME.md「情報代謝設定」。本 SPEC は実体を持たずポインタのみ（購読量保護）

## 機能間相互作用（永続化レイヤ・状態共有）

複数機能が同一の永続化レイヤ（DB / localStorage / ファイル等）または共有状態を読み書きする場合、
機能ごとの仕様だけでは整合性を保てない可能性がある。以下を明示する：

- **共有レイヤ一覧**：機能 A・B・C がどのキー／テーブル／ストアを共有するか
- **副作用マトリクス**：機能 X の実行が機能 Y の状態にどう影響するか
- **同時刻整合性ルール**：例「インポート時は A 層スナップショットも当日付で強制更新」

このセクションは**データ系機能・永続化機能・トランザクション系機能**で必須。
ステートレスな表示系・計算系のみの機能では省略可。

[省略可の判定基準]
- 永続化レイヤへの書き込みを行わない機能：省略可
- 共有キーが 2 つ未満：副作用マトリクス記述は任意
- ステートレスな表示系・計算系のみ：省略可

### 共有レイヤ一覧
[例]
- localStorage キー "user_preferences"：設定機能・テーマ機能で共有
- DB テーブル "sessions"：認証機能・ログ機能で共有

### 副作用マトリクス
[例]
| 機能実行 | 影響先機能 | 副作用内容 |
|---------|-----------|-----------|
| データインポート | スナップショット機能 | 古いスナップショットが無効化される |
| ユーザー削除 | セッション管理 | 該当ユーザーのセッションが強制終了 |

### 同時刻整合性ルール
[例]
- インポート実行時は、A 層スナップショットを同日付で強制更新する
- ユーザー削除時は、関連セッションを同一トランザクション内で削除する

## データモデル進化（任意・詳細は `schema-evolution.md`）

以下のいずれかに該当する場合のみ記入。該当しなければセクションごと省略可:
- 本番運用中で既存レコードがある / 外部クライアントが依存 / ARC = event-sourcing / realtime-pubsub

### 現行バージョン
[例: users テーブル v3]

### 互換性ポリシー
[full-compat / read-compat / breaking のいずれか。理由を1行で]

### デプロイ戦略
[expand-contract / blue-green schema / versioned-endpoint のいずれか]

### 進行中のマイグレーション
[expand/backfill/switch-read/contract の各期限]
```

---

## DONT.md テンプレート

```markdown
# スコープ外定義

以下はこのプロジェクトのスコープ外とする。
AI能力の向上に伴い、将来的にスコープ内に移行する可能性がある。

## 現時点のスコープ外
- 創造的UXデザイン
- 複雑な状態管理UI
- パフォーマンス最適化
- 未知の外部API統合
- [プロジェクト固有のスコープ外項目]

## スコープ外の理由
[各項目がなぜスコープ外かの簡潔な説明]
```

---

## REGIME.md テンプレート

体制判定結果を記録する。判定プロトコルは `regime-assessment.md` を参照。

```markdown
# 開発体制判定

## 判定時のAI能力バージョン
- モデル: [例: Claude Opus 4.7]
- 判定日: [YYYY-MM-DD]

（将来モデルで再判定する際の基準点として必須記録）

## スコア
- 規模スコア（S）: [X]点
- 不確実性スコア（U）: [Y]点
- リスクスコア（R）: [Z]点
- NFRスコア（N）: [W]点（内訳は下記。未収集時は N=0）
- 合計: [X+Y+Z]点（N は S/U/R 合計に加算しない。独立軸として評価）

## 判定結果
モード: [M1 / M2 / L2]

## dev_mode（v5.0.0 追加 / v5.6.0 で `autonomous` 本格化）
- mode: [local_only / github_assisted / autonomous]
- ctl: [0 / 1 / 2 / 3]   # Council Trust Level（crosscut-council/references/ctl-calculation.md 参照）
- 判定根拠: [GitHub 利用有無 + 規模 + LC の組み合わせ]

旧名 `github_autonomous` は v5.6.0 で `autonomous` にリネーム。後方互換: 既存記述で `github_autonomous` は `autonomous` + `autonomous_scope: full` と等価扱い。

（判定プロトコルは `regime-assessment.md` §dev_mode 判定 参照。昇格・降格は手動 + ADR 記録必須。）

## autonomous_scope（v5.6.0 追加、dev_mode = autonomous の場合のみ記載）
- scope: [full / merge_gated / custom]
- 判定根拠: [autonomous-drive 機構の運用粒度の選択理由]
- deployment: [crosscut-autonomous-drive skill による template 適用済 / 未適用 / 部分適用]

（判定プロトコルは `regime-assessment.md` §autonomous_scope 判定 参照。詳細は `dev-env-spec.md` Level C 参照。Person 責務 P1〜P4 と autonomous_scope の対応は `philosophy.md` 第 7 条参照。）

## persona（v5.17.0 追加、任意）
- active: [persona 名（拡張子なし） / 例: default, sheep-navigator]
- override_state: [Normal / Overflow / Attention / null]

（持続切替の永続化先。未指定時は `default` が active になり既存挙動と同一（後方互換）。対話中の一時切替は人間発話で即時可能。詳細は `persona-spec.md` 参照。適用対象は L0 三兄弟の対話面のみ。）

ロード規約（L0 三兄弟で共通）:
- `active` の解決順: (1) `<project-root>/.dh/personas/<active>.persona.md` → (2) `<dialog-harness>/templates/personas/<active>.persona.md`、最初に見つかったものを採用。両方なければ default にフォールバック
- `override_state` が null（既定）: State Machine 自動遷移
- `override_state` が非 null（`Normal` / `Overflow` / `Attention`）: その状態に強制固定。STEP 1 の `<system_state>` も固定値を出力
- ユーザーが指定しない場合は `override_state: null` を明示記録する（仕様齟齬防止）

## current_focus（v5.7.0 追加、autonomous-drive 入口側 Issue pickup で参照）
- type: [bug-fix / feature / refactor / docs / chore]   # 今このプロジェクトで何に集中しているか
- target: [master / develop / 等のブランチ名]
- since: [YYYY-MM-DD]
- priority: [critical / standard / low]

（判定プロトコルは `regime-assessment.md` §current_focus 判定 参照。β 半自動: spec-architect 対話で更新、γ ブランチ命名フォールバック: `fix/*` `feat/*` `refactor/*` から推論。Issue pickup 時の整合判定で参照される。dev_mode `autonomous` でなくても記録可能だが、active 機能として効くのは autonomous-drive 入口側稼働時）

## 判定根拠

### 規模スコアの内訳
- 機能数: [具体値] → [点数]
- 画面数: [具体値] → [点数]
- 登場人物: [具体値] → [点数]
- 外部連携: [具体値] → [点数]

### 不確実性スコアの内訳
- イメージの明確さ: [評価] → [点数]
- 既知度: [評価] → [点数]
- 変更予測: [評価] → [点数]

### リスクスコアの内訳
- 失敗時の影響: [評価] → [点数]

### NFRスコアの内訳（詳細は `nfr-scoring.md`）
- 性能（P）: [評価] → [0-3]
- 可用性（A）: [評価] → [0-3]
- セキュリティ（S）: [評価] → [0-3]
- コンプライアンス（C）: [評価] → [0-3]
- スケーラビリティ（L）: [評価] → [0-3]
- N 合計: [0-15]

※ NFR 情報が対話で引き出せなかった場合は N=0 と記録し、次サイクル以降で精緻化する。

## L2発動閾値チェック
- SPEC.mdトークン数: [概算値] / 15k
- 想定ファイル数: [概算値] / 80
- 想定総行数: [概算値] / 10k
- 独立ドメイン数: [数] / 5
- 並行可能サブゴール数: [数] / 3
- L1 1サイクル想定時間: [時間] / 2h
- → 超過項目: [該当項目を列挙。なければ「なし」]

## オーバーライド適用
- L2発動閾値: [適用 / 非適用]
- U >= 3（L0対話延長）: [適用 / 非適用]
- R >= 2（M2以上強制）: [適用 / 非適用]
- N >= 9（モノリス解除強制）: [適用 / 非適用]
- N >= 5（ARC切替推奨）: [適用 / 非適用]
- セキュリティ >= 2（M2強制）: [適用 / 非適用]
- 可用性 = 3（権限レベル記録必須）: [適用 / 非適用]

## ARC（アーキテクチャパターン）
- 選択: [monolith / realtime-pubsub / event-sourcing]（未指定時は monolith）
- 判断経緯: [AI推奨 → 人間確定 / 人間明示指定 / デフォルト適用]
- 根拠: [NFRマッピングおよびドメイン特性]

## 体制構成
- Layer 0: [構成内容]
- Layer 1: [単体 / ドメイン分割。M2なら layer1-independent-reviewer 常時起動]
- Layer 2: [L2の場合のみ。統括指揮 + layer2-integration-verifier]
- 検証: [M2: layer1-independent-reviewer / L2: + layer2-integration-verifier]

## L2の場合のサブドメイン構成（フラクタル適用）
[L2判定の場合のみ記載]

- ドメインA: S=X, U=Y, R=Z → モード [M1/M2]
- ドメインB: S=X, U=Y, R=Z → モード [M1/M2]
- ...
- ドメイン間インターフェース: [概要。詳細は DOMAINS.md]

## L2 配下Agent構成指定（L2判定の場合のみ記載）

L0 が認識擦り合せで決定し明示する。L2 はこの指定を受け取って実行する（L2 は構成を判断しない）。
詳細プロトコルは `../../layer2-orchestrator/references/sub-agent-protocol.md` を参照。

```yaml
L2-subagents:
  playwright-test-agents:
    enabled: [true / false]
    agents: [Planner, Generator, Healer, Reviewer]  # enabled=true の場合
  l1-parallel:
    enabled: [true / false]
    domains: [ドメインA, ドメインB, ...]
  integration-verifier:
    enabled: true  # L2 では常時 true
    scope: [cross-domain-invariants, e2e-scenarios, ...]
```

## LC（1→5運用対応）
- LC: [LC=0 / LC=1 / LC=2]
- 判定根拠: [history/ の有無、CHANGELOG.md 最終更新日]

## 履歴層設定（LC ≥ 1 の場合のみ記載）
- archive 移動年数: 2 年（デフォルト、上書き可）
- 儀式拒否連続警告閾値: 5 回
- 儀式スキップ連続警告閾値: 5 回

## 履歴更新承認設定（LC ≥ 1 の場合のみ記載）
- レベルA（自動承認）: スキップ
- レベルB（確認推奨）: 通知のみ、デフォルト承認
- レベルC（必須承認）: 必ず確認

## 情報代謝設定（LC ≥ 1 の場合のみ記載・v5.19.0 追加）

3 層保持 regime（HOT/WARM/COLD）の **project 固有パラメータ**のみを置く。定義の正本は
layer0-reindex-librarian の references/metabolism-regime.md（framework 叡智）。
決定3 三分割: 定義→SK references / パラメータ→本セクション / SPEC.md→ポインタ1行。

- token_budget: 12000            # AI 購読量（既定ロード）の上限トークン。history 層が超過で reindex 発火（リズム）
- recrystallize_trigger: token_budget   # cycle 境界で実行。N-cycle 駆動は採らない（enum: token_budget）
- tier_paths:
  - HOT:  CLAUDE.md / SPEC.md / DOMAINS.md / history/SUMMARY.md（結晶層・常時ロード対象）
  - WARM: history/INTENT.md / history/CHANGELOG.md / history/E2E-LOG.md（圧縮層・関連時ロード）
  - COLD: history/archive/YYYY-MM/（アーカイブ層・既定非ロード・retrievable。E2E は archive/YYYY-MM/e2e/）
- cursor_path: history/.metabolism-cursor.yml   # 処理済みマーカー（増分・冪等の生命線）
- dry_run_cycles: 3              # 初期サイクル数だけ Dry-run（差分レポートのみ）。0 で本番昇格
- council_gate.repetition_threshold: 3   # 同一パターン N 回反復で結晶化候補（flaky 罠化にも流用）
- council_gate.cross_type_threshold: 3   # 同一 override が M 機能タイプ以上で反復したら Council 諮問
- council_gate.min_age_days: 7           # 候補化から X 日経過まで HOT 昇格しない

### E2E 代謝設定（UI プロジェクト & E2E あり時のみ・v5.24.0）

E2E run 履歴を代謝の episodic ソースとして扱う際の project 固有パラメータ。定義の正本は
layer0-reindex-librarian/references/metabolism-regime.md §7、構築は e2e-best-practices.md §9。

- e2e_metabolism.enabled: true            # UI プロジェクトで E2E を持つ場合のみ。DH 本体は対面アプリ無しのため非適用
- e2e_metabolism.warm_log: history/E2E-LOG.md       # run 要約（append-only・cursor 追跡）
- e2e_metabolism.cold_artifacts: history/archive/YYYY-MM/e2e/   # 相 A artifact・生 run ログ（COLD 直行・既定非ロード）
- e2e_metabolism.flaky_rate_threshold: 0.05         # ④還流 teeth の閾値（opt-in/段階。実運用データで較正）
- e2e_metabolism.quarantine_max_age_days: 14        # 隔離テストの修正/削除期限（超過で設計層へ還流）

（プロトコルは layer0-reindex-librarian の SKILL.md と references 参照。初回 reindex は必ず Dry-run。
HOT 昇格は Council ゲート経由・人間最終承認。COLD=archive≠delete。④還流 teeth の auto-merge 強制連動は opt-in/段階。）

## 判定ログ
[対話の中で得られた判定材料となる発言の要約]
```

---

## DOMAIN-CONTEXT.md テンプレート（任意・詳細は `domain-context-dialog.md`）

業界・業務特有の前提条件を構造化する。純粋な技術プロジェクトでは不要。
機密情報は `DOMAIN-CONTEXT.secret.md` に分離し `.gitignore` 対象にする。

```markdown
# ドメイン文脈

## 業界
[業界 / B2B・B2C / 類似プロダクト]

## 業務慣習
- [IT 知らない人向けに分かりにくい慣習]
- [紙時代の名残]
- [他業界と語が同じでも意味が違うもの]

## 既存システム制約
- 基幹: [システム名・接続方式]
- 連携必須: [SAP / SFDC / 会計 SaaS 等]
- 置き換え対象: [現行手段]

## 規制・コンプライアンス
- [法令・業法。`nfr-scoring.md` の C スコアと連動]
- 監査: [年次 / 内部 / 外部認証]
- 保管期間: [法定要件]

## 用語集
- [略語・専門用語・通称 vs 正式名称]
```

---

## history/ 配下テンプレート（LC ≥ 1）

既存プロジェクト継続時は `history/` 配下に以下を配置する。各ファイルの詳細テンプレートは `history-layer-spec.md` を参照。

- `history/SUMMARY.md` — 自動生成される圧縮サマリ（L0振り返り儀式で使用）
- `history/INTENT.md` — 機能の意図・却下案・廃止理由・確度メタデータ
- `history/CHANGELOG.md` — 時系列の機能変遷（献上サイクル単位で追記）
- `history/REGIME-LOG.md` — 判定×実績の対応表、儀式記録
- `history/ARCH-DECISIONS.md` — ADR形式の軽量版（任意）
- `history/PATTERNS.md` — 罠／成功パターン集（任意）
- `history/archive/` — 廃止から2年経過した INTENT の退避先

訂正は取り消し線方式＋理由併記（`history-layer-spec.md` の「訂正記述」参照）。
人間は承認のみ行い、更新本体は AI が書く。

---

## 記述ルール

### 粒度
- 最低ライン：「機能×条件」。これ未満の仕様はLayer 1に渡さない
- 条件は具体的・定量的に記述する（「適切に処理する」ではなく「最大30件、超過時はエラーコード429を返す」）
- HOW（実装方法）は書かない。WHAT（何ができるべきか）のみ

### 言語
- 自然言語で記述する（DSLは使わない）
- 曖昧な表現を避ける。「いい感じに」「適切に」「必要に応じて」は禁止
- 主語を明確にする（「ユーザーが」「システムが」「管理者が」）

### 変更管理
- 仕様変更時はドキュメントを直接更新する（差分ファイルは作らない）
- 重大な変更にはドキュメント先頭の更新履歴セクションに記録する
- REGIME.md は仕様変更時に再評価する。スコアが変わったらモードも見直す
