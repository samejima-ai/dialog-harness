# 自律駆動機構ブレスト結晶 2026-05-02

HANDOFF v0.1.0「自律駆動機構の哲学的座標」を起点とする L0 前段ブレストの結晶。
SPEC 化フェーズ（後続セッション、L0 spec-architect 起動時）の入力ドキュメント。

## 起点

- `(HANDOFF)` 自律駆動機構の哲学的座標 v0.1.0（思想・原則レベル確定済み、実装は別 HANDOFF）
- `history/DH-PHILOSOPHY-INSIGHTS.md`（特に第3章 経営構造同型性 / 第7章 業界差異 / 第10章 P3 メタ原理）
- 既存ロードマップ: v5.4.0 リリース後、v5.5.0 候補 Phase γ / v6.0.0 候補 第3の道 / crosscut-verifier-philosophy 後送

## 確定したひでさん哲学（ブレスト中に言語化）

| 原則 | 内容 |
|---|---|
| 三権分立 | D4 で基準設定、D3 で測定・管理。当事者は基準を決めない / 自分を測らない（不正温床回避） |
| 自律駆動最大化 | AI は基本自己判断で進める。拮抗 / 原則抵触で Council 発火、解決しないとき人間献上 |
| 現実的実装 | 「絵に描いた餅」を避ける、出来る限り自律駆動を支持 |
| 段階的組み込みで止揚 | 二項対立を時間軸で両立する手法（adrv01 で確定、adrv02 / adrv03 にも適用） |

## Council 諮問結果（3 件、全て agreed_recommended / agreed_with_modification 確定）

### adrv01: 拮抗検出主体の設計

- recommended: **(b) 独立観測機構** + 哲学者第3の道（メタ層構造）統合
- judgment_confidence: 0.45（third_way 45% で escalation 経路、実装者=人間で同一人物のため (B) で解決）
- implementer_consent: `agreed_with_modification`
- 修正内容: **段階的組み込みで止揚**
  - Phase 1: (a) AI 自己申告のみ運用（既存 Council confidence < 0.6 機構流用、コスト 0）
  - Phase 2: (b) 独立観測機構を後付け（autonomous-dev 出力 / 試行回数 / 往復パターンの客観観測、harness-verifier 同型）
  - Phase 3: 階層構造として止揚（自己申告 = 一次入力、独立機構 = 申告事実の検証メタ層、哲学者法廷モデル）

### adrv02: 動的ドメイン組織化 × 連鎖駆動

- recommended: **(c) ハイブリッド段階移行** + 哲学者第3の道（subagent isolation）統合
- judgment_confidence: 0.55
- implementer_consent: `agreed_recommended`
- 内容:
  - Phase 1: 全派生常駐維持（現状）
  - Phase 2: 運用データを基に主従集約 or context 分離モデルへの移行判断
  - 評価軸: 「常駐 vs on-demand」ではなく **「context 共有 vs context 分離」** に軸再構成（subagent isolation 活用、追加コスト 0）

### adrv03: ロードマップ吸収戦略

- recommended: **(a) autonomous-drive 独立 minor 路線**
- judgment_confidence: 0.55
- implementer_consent: `agreed_recommended`
- 哲学者第3の道（破壊変更基準で version 再配置）は SPEC 化時の再評価軸として保持

## 確定したロードマップ

| version | 内容 | 根拠 |
|---|---|---|
| v5.5.0 | adrv01-Ph1（AI 自己申告閾値の Council 連動明文化）+ Phase γ（L1 意図合致軸） | adrv03 (a) |
| v5.6.0 | adrv01-Ph2（独立観測機構新設、新規 crosscut-* skill） | adrv03 (a) |
| v6.0.0 | adrv01-Ph3 + adrv02-Ph2 + 第3の道 + crosscut-verifier-philosophy 大統合 | adrv03 (a) |
| 不要 | adrv02-Ph1（現状維持で version bump 不要） | adrv02 (c) |
| 代替案 | adrv01-Ph1 を v5.4.x patch で先出し（哲学者第3の道）| adrv03 minority、SPEC 化時再評価 |

## 軽い 3 件の合意（対話処理、Council 諮問対象外）

### 整合性発見: HANDOFF §2.2 引用先問題

- **問題**: HANDOFF §2.2 が参照する「INSIGHTS §10.5.2 既存原則の再確認」が実際の INSIGHTS に存在しない
- **合意**: HANDOFF §2.2 を adrv01 結果に基づき書き直す（メタ層モデルに更新、INSIGHTS 第10.5.2 は新設しない）
- **根拠**: INSIGHTS は不変原則ドキュメントで頻繁な追記は避けるべき（第6章「役員会で定款を変更しない」原則と整合）

### 論点 1: HANDOFF §2.3 検証三層と既存スタックの用語整合

- **マッピング**:
  - 事前検証ゲート = **Shift Left 基盤**
  - 並走検証 = **第 1 層 計算的センサー**
  - 事後検証 = **第 2 層 E2E** + **第 4 層 Inferential レビュー**
  - 第 3 層（IC）は事後測定、第 5 層は人間/harness-verifier
- **合意**: HANDOFF §2.3 の三層分離は「Shift Left 基盤 + 5 層スタック」の **時間軸 view 追加**として記述（既存スタックを上書きしない）

### 論点 5: HANDOFF §2.1 重複整理

- **問題**: HANDOFF §2.1「実行時間優位 vs 検証時間優位」表は INSIGHTS 第7章とほぼ同内容
- **合意**: HANDOFF §2.1 を「INSIGHTS 第7章への参照のみ + 1 行の要約」に圧縮、HANDOFF を思想層から実装指示層に寄せる

## 次のステップ（後続セッション、SPEC 化フェーズ）

1. **L0 起動（spec-architect）**: 本結晶を入力として subphase-selection → 適切なフェーズ選択
2. **HANDOFF 更新**: §2.1 圧縮 / §2.2 メタ層モデルに書き直し / §2.3 時間軸 view として明示
3. **v5.5.0 SPEC 化**: adrv01-Ph1（AI 自己申告閾値の Council 連動明文化）+ Phase γ（L1 意図合致軸）の具体仕様策定
4. **HANDOFF §6 後続検討事項の SPEC 化**:
   - 事前検証ゲートの具体化（Shift Left 基盤への配置）
   - Council Hook 発火条件の精緻化（adrv01 で大筋合意、SPEC 化で詳細化）
   - 失敗経路の還流先マッピング（既存 crosscut-feedback-loop の延長）
   - 連鎖トリガー停止条件（adrv02 の運用データ蓄積期間 + 主従集約評価軸）
5. **history/INTENT.md / ARCH-DECISIONS.md / REGIME-LOG.md 更新**: SPEC 化フェーズで履歴記録

## 関連ドキュメント

- `history/DH-PHILOSOPHY-INSIGHTS.md`（第3章 / 第7章 / 第10章）
- `history/COUNCIL-LOG.md`（adrv01 / adrv02 / adrv03 エントリ）
- `.claude/skills/layer1-autonomous-dev/references/inferential-sensor-v2.md`
- `.claude/skills/layer0-spec-architect/references/dev-env-spec.md`
- `.claude/skills/crosscut-council/`
- `.claude/skills/crosscut-feedback-loop/`

## バージョン

v1.0.0（ブレスト結晶 2026-05-02 確定、L0 SPEC 化フェーズの入力として後続セッションで使用）
