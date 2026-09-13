# upgrade-spec v7.0.0 — 現行モデル世代向けメタハーネス刷新（認知足場の剥離・環境足場の強化）

> **状態: 実装中（F1 / F2 / F4 / F5 / F6 / F7 / F8 / F9 / F10 済 / F3 未）**。
> F1 / F2 / F4 / F5 / F7 / F8 / F9 / F10 + F3 fixtures は PR-1（#288・2026-09-13 merge）で着地。F6 は PR-2。
> F3（description 圧縮 + 再測定）は基準値計測後の PR-3。PR-1 の状態行は F8 / F9 を「未」と書いていたが
> 両方とも PR-1 で着地済み（`delivery/ABLATION-council-2026-09-13.md` / DELIVERY-PR1 §F9）— PR-2 で訂正。Council 諮問 `council-2026-09-13T01:40:00Z-v7phsa`
> 通過（案C・jc 0.78・reason_divergence・consensus_mode は escalate_to_human だが人間が 2026-09-13 に「すべて実行」で
> 事前承認、D-1〜D-5 は推奨案で確定）。着地順序は案C: PR-1（F1+F2+F4+F5+F7+F10+fixtures）→ 基準凍結 → PR-2（F6）→ PR-3（F3）。着地の PR 番号は `history/CHANGELOG.md` の各節が持つ。
>
> **本 spec は 2 段構成である。** Phase A は L-FULL 領域（第 9 条：revert で原状回復可能）のみを扱い、
> philosophy.md / delegation-boundary.md / auto-merge-boundary.md に一切触れない。Phase B は H1（哲学変更）を
> 含み、**2026-11-06 の roll-back 評価ゲート通過後に人間が起票する**（L-FROZEN-PHIL・第 6 条 憲法の自己改訂禁止）。
> `VERSION` の 7.0.0 昇格は Phase B に属する。Phase A は 6.x 系 minor として先行着地してよい
> （`dev-env-spec.md` §spec 番号は起草時の予約）。
>
> **起点**: 利用者発話（2026-09-13、L0 メタハーネス開発）「既出の情報も含めて DH の刷新を設計する。現行最新モデルに
> 合わせた対話設計・自律実行メタハーネスの自己開発を開始する」。判断材料は
> `delivery/DIAGNOSIS-metaharness-rebuild-2026-09-13.md`（本 spec と同 PR）および前段の
> 「ハーネスの半減期」（減衰する層 / しない層の線引き）。
>
> **人間決定（2026-09-13・L0 儀式 F2 の 4 問）**: スコープ = 全部（v7.0.0 major）/ H1 の起票 = 11-06 ゲート後 /
> Council 3 ペルソナ = **ablation を先に回す** / 環境再評価（前回 B−）= 今サイクル献上時に同梱。

---

## 0. 位置づけ — 「足場を剥がす」ではなく「剥がれる足場と残る足場を分ける」

2026-09 時点の一次研究は一貫して次を示す：モデルに吸収されたのは**認知を教える足場**（多ペルソナ合議・
役割分割・段階思考の明示・自己批評・ペルソナ付与）であり、**環境を区切る足場**（決定論検査・文脈隔離・
権限段階・ツール絞り・失効可能な記憶）は残っている。足場の選択だけで同一モデルの成績が最大 28 ポイント動く
（arXiv 2606.08529）ため、全剥離は誤り。本 spec はこの線に沿って DH を 3 層に割り直す。

| 層 | 内容 | 扱い | DH の該当 |
|---|---|---|---|
| **不変核** | 可逆性で委譲線 / 採用判断は人間 / 憲法の自己改訂禁止 / 人間＝意図・AI＝実装 | 3〜4 条に絞り、compaction 後に再注入 | 第 4・6・8・9 条、第 7 条 P1〜P4 |
| **環境足場** | 決定論検査 / 文脈隔離レビュー / 権限段階 / skill・tool 絞り / 失効可能な記憶 | 維持・強化 | 第 2 条、第 9 条 §決定論の保全、independent-reviewer、review_trigger |
| **認知足場** | 多ペルソナ合議 / 役割分割 / 献上 4 分類 / 情報純度の損失前提 | 実測で無効か有害 → 時限化・縮退 | 第 3・5 条、第 7 条 4 役割、Council 3 ペルソナ、L2 雛形 |

DH 内部の観測が外部実測と一致している点を強調する：`scripts/council-axis-audit.py` は 3 ペルソナとも
confidence σ ≈ 0.05 で「議題ではなく役柄を採点している」と warn を出しており（2026-09-13 実行）、
これは「チームは自チームの最良メンバーに最大 41.1% 負ける」（arXiv 2602.01011）の内部再現である。
また `layer2-orchestrator/SKILL.md` は自ら「雛形」「M2 で吸収可能なケースが多い」と記しており、
モデル改善が役割を 1 つ空洞化させた記録＝カービィ効果の DH 内サンプル 1 である。

## 1. 計測（2026-09-13・`.claude/` 配下 139 md 全数）

| 指標 | 実測 | 含意 |
|---|---|---|
| skill description 合計（常駐） | 12,943 字 ≈ 9,000〜13,000 tok | skill 一覧の既定枠（文脈窓の 1% ≈ 2,000 tok @200K）の **4.5〜6.5 倍**。溢れると起動回数の少ない skill から description ごと落ちる＝無音の失敗（実務者由来・**`/context` で要実測**） |
| description 中央値 / 最大 | 631 字 / 963 字 | 個別上限 1,536 字には収まる。拘束は合計枠 |
| SKILL.md 500 行超 | 3 本（spec-architect 860 / council 527 / autonomous-dev 516） | compaction 時の再添付は 1 skill 5,000 tok・合計 25,000 tok。超過分は圧縮の瞬間に落ちる |
| `.claude/` 総計 | 1,592,127 字（spec-architect 単独 41.4%） | — |
| `review_trigger` 保有 | 7 / 139 本（5.0%） | 失効注釈の適用率 |
| `model_generation` 実適用 | 1 件 | 規格・検知器は 2026-08 に設計済み。適用が無い |
| `model_generation` 発火 | 0 件（norm-scan 2026-09-13） | 発火条件が「model-recommendations.md の更新」に間接化され、実際の世代交代（REGIME-LOG 記録の世代 → 現行 5 系）を検出できていない |
| philosophy.md の失効注釈 | 0 件 | 最も減衰しやすい資産に注釈が無く、かつ L-FROZEN-PHIL で AI は付与 PR も出せない |
| `disable-model-invocation` | 0 skill | 「明示トリガーのみ」と自著する skill が 12 本 |
| DH 自身の CLAUDE.md | 不在 | 常駐層は skill description のみ |

## 2. 不変条件

- **I-1 L-FROZEN 不可侵**: Phase A は `philosophy.md` / `delegation-boundary.md` / `auto-merge-boundary.md` を
  1 バイトも変更しない。不変核の再注入（F1）は philosophy を**引用**するだけで、改訂ではない。
- **I-2 パージは品質根拠**: トークン削減を目的にしない。請求の約 87% はキャッシュ traffic であり、トークンを
  38.4% 削って請求が 6.8% 増えた実測がある（arXiv 2607.12161）。常駐部分を**動かさず**キャッシュを効かせる方が効く。
- **I-3 検知は決定論**: anchor / norm-scan / 失効列挙に LLM 判定を入れない（既存 I-3 の継承）。
- **I-4 自己適用**: 本 spec が追加する規範には全て `review_trigger` を付す（うち `model_generation` は必須）。
- **I-5 ablation 規律**: 部品を削る判断は「基準を凍結 → 固定ケースで測る → 実測の劣化が出たものだけ戻す」。
  外部研究はこの順序を決めるだけで、削除の根拠にはならない。
- **I-6 独立性**: anchor hook は `crosscut-hook-observer` に同居させない（同 skill は「観測専用・注入しない」を
  憲章に持つ。命令層と観測層の分離）。

## 3. Phase A — 環境足場（L-FULL・今サイクル・6.x minor として着地可）

効果 ÷ コスト の降順。各 F は独立に着地できる。

### F1 不変核の再注入（最優先）

**根拠**: compaction だけで規範違反率が 0% → 30%（一部 59%）、組織ポリシー型は安全規範の 8.3 倍の速さで
減衰、約 47 トークンの再注入で全 7 モデルが 0% に復帰（arXiv 2606.22528）。

**経路（訂正済み）**: PreCompact hook は文脈を注入できない（Claude Code 公式：情報提供のみ）。注入できるのは
**SessionStart hook の stdout**（matcher: `startup` / `resume` / `clear` / `compact`）。DH は PreCompact を配線済みだが
注入点として使えないため、**SessionStart に 1 command を追加**する。

- 新設 `templates/hooks/anchor-core.py`（**1 本のみ**。DH 本体も同ファイルを直接実行する。`scripts/` へのコピーは作らない — 二重コピーの drift を避ける。実装時に改訂）。
  `.dh/anchor-core.md`（利用者プロジェクト）または `.claude/anchor-core.md`（DH 本体）を読んで stdout に出すだけ。
  LLM 判定なし・失敗時は exit 0 で無出力（degrade）。
- `.claude/settings.json` の `SessionStart` に matcher なし（＝全 source）で追加。compact 直後にも startup にも効く。
- `anchor-core.md` の内容（D-1 で人間が確定。以下は起草案・philosophy の引用のみ・≤ 250 字目安。検査上限は 400 字 / 8 行）:

  ```
  # 不変核（philosophy.md の引用。改訂は人間専管）
  1. 委譲線は可逆性だけで引く。原状回復できない操作は PR 前に発話で確認する（第9条）
  2. 採用判断は人間。AI は観測 → 候補化まで（第8条）
  3. philosophy / delegation-boundary / auto-merge-boundary は AI が提案 PR も作らない（第6条）
  4. 機械的棄却は LLM 承認に常に優越する。逆は無い（第2条・第9条 §決定論の保全）
  ```

- **受け入れ基準**: (a) `claude --debug` 相当で SessionStart 後の文脈に 4 行が現れる（手動確認、DELIVERY に記録）
  (b) hook 不在・ファイル不在でも DH が通常動作する (c) `harness-verifier/checks/hook_observations.py`（検査 6）が anchor 配線と
  本文上限を検査項目に持ち、`scripts/test-hook-wiring.py` §5 が回帰テストする（実装時に改訂: `hook_wiring.py` は存在しない）。
- 規範メタデータ: `stage: 全段階` / `review_trigger: [model_generation, measured: 再注入後も規範違反が観測される]`

### F2 休眠 skill の一覧枠からの退避

**根拠**: 旧モデル向け skill の過剰発火が「モデルの自己検証を押しのける」（OpenAI・GPT-6 Astra 3 欠陥の第 1、
2026-09-13）。skill 一覧は溢れると低起動 skill から落ちる。

| skill | 処置 | 理由 |
|---|---|---|
| `crosscut-verifier-philosophy` | **配布から除去**（D-2 で deprecation-protocol を通す） | v5.0.0「発動禁止」placeholder のまま v6.18.0 まで同梱。CTL-1 では起動条件（CTL ≥ 2）も未達 |
| `rtk-integration` | `disable-model-invocation: true` | Windows 専用の install 手順。人間が `/rtk-integration` で呼ぶ |
| `layer0-onboarding` | 同上 | 1 プロジェクト 1 回の使い捨て・人間明示 |
| `layer0-archeo-architect` | 同上 | 「自動起動しない。人間明示トリガーのみ」と自著 |
| `layer2-orchestrator` / `layer2-integration-verifier` / `crosscut-autonomous-drive` | **フラグを付けない**（F3 で圧縮のみ） | 他 skill から model 経由で起動される（autonomous-dev → orchestrator、spec-architect → autonomous-drive）。フラグは「Claude が起動できない」ため連鎖が切れる |

- 回収量: フラグ 4 本 = 1,775 字（13.7%）。除去は同時に SKILL.md 2,490 字 + 検査対象の縮小。
- **受け入れ基準**: `dh-manifest.yml` の配布リストと `GRAPH.yml` の node が整合（`harness-verifier` 検査 8・9 が PASS）。
- 規範メタデータ: `review_trigger: [model_generation, cycles: 6]`

### F3 description の圧縮（残 17 skill）

**根拠**: Anthropic 公開 17 skill の discovery 中央値は約 80 tok/skill。DH は 430〜620 tok/skill。
「混同を避ける」の列挙は方向として正しい（負例が collision を減らす）が、1 回の書き直しで得られる routing F1 の
ほぼ全部が取れ、追加の文言は 0.5% 未満（arXiv 2606.30775）。

- 目安 **≤ 300 字 / skill**（合計 ≤ 5,100 字）。「何をするか・いつ使うか・使わない境界 1 行」の 3 要素のみ。
  トリガー語の長い列挙と兄弟 skill との差分説明は SKILL.md 本体 §起動条件へ移す。
- **トリガー評価集合の先行作成**（Council 案C・3 軸が独立に指摘した本文矛盾の是正）: `harness-verifier/fixtures/skill-triggers.yml`
  に skill ごと **正例 8・負例 8** の発話を **圧縮前に** 置く（決定論 artifact・PR-1 で着地済み）。routing の実測は LLM を要するため
  harness-verifier では検査しない（I-3）。**基準値は PR-1 merge 後の master（F2 で一覧が変わった後の 17 skill 構成）で 3 run 取り、
  平均と揺れ幅を DELIVERY に記録して凍結する**（I-5・Council 重み 8 vs 2）。圧縮（PR-3）後に同じ fixtures で再測定し、
  正例再現率 −5pt 超 / 負例誤発火率 +5pt 超（揺れ幅が 5pt を超える指標は揺れ幅を閾値に置換）を劣化と判定して戻す。
  閾値と反復回数は測定前に fixtures ヘッダで宣言済み（測定器を答えに合わせない）。
- **受け入れ基準**: fixtures が 17 skill 分ある（PR-1）/ 基準値（3 run 平均・揺れ幅）が DELIVERY にある（PR-1 merge 後）/ 合計 ≤ 5,100 字（検査で FAIL・PR-3）/ 再測定で劣化なし（PR-3）。
- 規範メタデータ: `review_trigger: [model_generation, measured: 負例誤発火率が圧縮前より悪化]`

### F4 独立レビュアーの読み順制約

**根拠**: 新規文脈・成果物のみのレビュー F1 28.6% ＞ 自己レビュー 24.6% ＞ **生成側の文脈を継承した
サブエージェント 23.8%**（arXiv 2603.12123・n=360）。DH の reviewer は「実装コンテキストを引き継がない」で最良手に
一致しているが、処理フロー 5.4 / 5.9 で L1 の自己評価（DELIVERY.md「意図合致検証」/ HANDOFF.md）を読む。

- `layer1-independent-reviewer/SKILL.md` 処理フローに 1 行追加: **「3〜5（仕様合致・動作・使用）の判定を確定するまで
  `delivery/DELIVERY.md` と `delivery/HANDOFF.md` を開かない。5.4 / 5.9 は必ずその後」**。
- **受け入れ基準**: SKILL.md の記述順が上記を満たす（目視）。behaviour の実測は F8 の ablation に同梱。
- 規範メタデータ: `review_trigger: [model_generation]`

### F5 機械的棄却の優越を配線表へ

**根拠**: 自己改善ループで judge 信号は 11 通りに失敗（reward hacking 含む）。ルーブリック改善 4 ラウンドで進捗ゼロ、
機械的棄却のみが回帰を捕捉（arXiv 2609.02246）。DH 第 2 条・第 9 条 §決定論の保全は方向一致だが
「機械的棄却は LLM 承認を常に上書きする。逆は無い」の一文が無い。philosophy は L-FROZEN ゆえ、L-FULL の配線表に置く。

- `crosscut-council/references/escalation-matrix.md` §1 に行追加:
  `| 全ポジション | 決定論検査（型 / lint / test / harness-verify）の FAIL | **FAIL 確定**。Council・reviewer・drift の PASS では覆らない | 第2条・第9条 §決定論の保全 |`
- `layer1-autonomous-dev/references/inferential-sensor-v2.md` §スタック全体像に 1 行:
  「第 1・2 層の FAIL は第 4・5 層の PASS で覆らない（優越は一方向）」。
- **受け入れ基準**: 両ファイルに文言がある。`crosscut-feedback-loop` の還流表と矛盾しない（目視）。
- 規範メタデータ: `review_trigger: [model_generation]`

### F6 叡智層の失効セマンティクス

**根拠**: 環境が転回すると append-only 記憶は成功率 0.210、記憶なし 0.309（記憶が害）、明示的失効で 0.950
（arXiv 2608.07429）。DH の COLD は「archive ≠ delete」で退避のみ、失効記法は INTENT.md の機能廃止に限定、
罠カタログ・RL・叡智層は対象外、退避は 2 年後。

- `dev-env-spec.md` §規範メタデータに 3 フィールド追加: `status: active | revoked` / `revoked_at: <date>` /
  `superseded_by: <path#anchor>`。**revoked は購読対象から外す**（reindex-librarian の COLD 移送条件に
  「revoked は次サイクルで COLD」を追加）。
- `scripts/norm-scan.py` に「revoked なのに HOT/WARM に残っている規範」の列挙を追加（判定はしない）。
  儀式 F2.6 の問いに「失効済み N 件が購読に残っています。COLD へ？」を追加。
- 適用対象を INTENT.md 以外へ拡張: 罠エントリ / RL frontmatter / `history/DH-PHILOSOPHY-INSIGHTS.md` の各節。
- **受け入れ基準**: メタデータ規格に 3 フィールド / norm-scan が列挙する / 儀式 F2.6 に問いがある。
- 規範メタデータ: `review_trigger: [model_generation, cycles: 6]`
- **実装注記（PR-2）**: (1) 列挙の走査範囲は `review_trigger` の走査と異なり `history/` を含む（叡智層 `DH-PHILOSOPHY-INSIGHTS.md`
  が適用対象のため）。除外は COLD = `history/archive/` のみ。(2) `superseded_by` は後継なしでも `none` を明示する（「書き忘れ」と
  区別）。(3) `deprecation-protocol.md` 廃止決定時の記録と `history-layer-spec.md` §archive にも失効規範の経路を追記
  （2 年規則は機能 INTENT のみ・失効規範は次サイクル）。(4) 実リポの第一適用例は作っていない — 何を失効させるかは採用判断
  （第 8 条）ゆえ人間。列挙が空振りでないことは `scripts/test-norm-scan.py` の fixtures で実証。

### F7 `model_generation` 検知の修正

**根拠**: §1 の計測。発火条件が model-recommendations.md の更新に間接化されているため、同ファイルが更新されない限り
永久に発火しない（代理指標が人間の作業に依存）。

- 新設 `history/.model-generation.yml`: `current: <世代ラベル>` / `changed_at: <date>` / `recorded_by: ritual-F1`。
  儀式 F1 で AI が当該セッションの世代を記録（世代が変わっていれば `changed_at` を更新）。
- `norm-scan.py` の `model_epoch` を `max(model-recommendations.md の最終 commit, .model-generation.yml の changed_at)`
  に変更。
- **受け入れ基準**: `scripts/test-norm-scan.py` に「.model-generation.yml が新しければ発火」のケース追加。
- 規範メタデータ: `review_trigger: [measured: 6 cycle 連続で発火 0 なら代理指標を再設計]`

### F8 Council ablation（Phase B の判断材料）

**根拠**: 外部実測（−41.1% / Planner-Critic 分割は p=0.80 で単体と区別不能・1.79 倍コスト）と DH 内部の
軸監査 warn が一致。ただし外部実測は「チームが答えを出す」設定で、DH の Council は `final_decision: null`
＝人間の判断材料出し。判断支援としての価値は未計測。**削る前に測る**（I-5）。

- データ: `~/.claude/council-data/invocations/`（90 件・事後評価済み 82 件）から **10 件を category 層化抽出**。
- 条件: (a) 現行 3 ペルソナ Council / (b) 単一レビュアー・新規文脈・`topic_summary` + options のみ（history 非参照）。
- 指標: `actual_outcome.status`（人間判定）との一致率 / judgment_confidence の σ（議題反応性）/ トークン消費。
- **ラベル汚染の注意**: 記録された `judgment` は Council 自身の出力なので一致率の基準にしない。基準は
  `actual_outcome`（人間の agreed / rejected / synthesis）のみ。
- 出力: `delivery/ABLATION-council-<date>.md`。Phase B の H1 起票材料。
- **受け入れ基準**: 10 件 × 2 条件の結果表と σ がある。結論は書かない（判断は人間）。

### F9 環境再評価（儀式 F2.7）

前回 2026-08-26 `delivery/DIAGNOSIS-loop-graph-engineering-2026-08-26.html` 総合 **B−**。Phase A 着地後に同じ
外部規格（ループ 6 軸 / グラフ 10 特徴 / 成熟度 8 段階）で再採点し、**前回値との差分を必須出力**。

### F10 SKILL.md 500 行超 3 本の分割

- `layer0-spec-architect/SKILL.md`（860 行）: 「v3.1 追加」〜「v6.3.0 追加」の版履歴節（約 300 行）は SKILL.md の
  責務ではない。`history/CHANGELOG.md` へ移送し、SKILL.md には「版履歴は CHANGELOG を参照」の 1 行のみ残す（D-4）。
- `crosscut-council/SKILL.md`（527 行）/ `layer1-autonomous-dev/SKILL.md`（516 行）: 本体から references へ移送し
  500 行未満へ。
- **受け入れ基準**: 3 本とも < 500 行。`harness-verifier` 参照検査 PASS。

## 4. Phase B — 不変核と認知足場の再編（H1・2026-11-06 ゲート後・人間起票）

AI は本節の**設計材料**（ADR ドラフト・分割案・F8 の実測）までを用意する。起票は人間。

- **B1 philosophy.md の 2 分割**: 不変条（第 4 条 [「質問しない」を除く]・第 6 条・第 8 条・第 9 条・第 7 条 P1〜P4）を
  `philosophy.md` に残し L-FROZEN-PHIL を維持。運用条（第 1・2・3・5 条・第 7 条 4 役割）を
  `philosophy-operational.md`（仮）へ分離し **L-FULL** に置く。運用条には全節 `review_trigger: [model_generation]`。
  併せてヘッダー「6条憲法」の実態（9 条）とのずれを解消。
- **B2 第 7 条 4 役割の改訂**: F8 の結果で Council を「3 ペルソナ合議」のまま維持するか「単一・新規文脈・成果物のみ」へ
  縮退するかを決める。第 8 条 minority C（4 段階拡張）と逆向きになる場合は同時に再諮問。
- **B3 L2 雛形の扱い**: `deprecation-protocol.md` を通して廃止 / 統合 / 温存を決める。
- **B4 VERSION 7.0.0**。

## 5. 判断点

| # | 判断 | 誰が | 状態 |
|---|---|---|---|
| D-1 | anchor-core.md の 4 行の文言確定（引用のみ・≤ 250 字） | 人間 | 起草案あり（F1） |
| D-2 | `crosscut-verifier-philosophy` の除去（deprecation-protocol 発動：利用率 0・代替は Phase B・依存なし） | 人間（一言承認・非対称原則） | 未 |
| D-3 | Phase A の Council 諮問。escalation-matrix「規範文書改変の実装前 → Council 諮問を促す」に該当するが、**F8 は Council 自身が当事者**（v6.10.0「Council 自体が当事者なら直接人間へ」）。F8 を除く F1〜F7・F9・F10 のみ諮問に掛け、F8 は人間直行とするか | 人間 | 未 |
| D-4 | spec-architect SKILL.md の版履歴節の移送先（CHANGELOG / 新設 `references/skill-history.md`） | 人間 | 未 |
| D-5 | Phase A の着地版番号（6.20.0 を予約するか、6.19.0 の D-6 昇格と束ねるか） | 人間 | 未 |

## 6. モード判定（DH 本体自身）

- Mode: **M2 標準**（S=大 / U=低 / R=**高**（自己改修・憲法隣接・配布物） / N=低 / 単一ドメイン / L2 閾値未達）
- 体制: L0（spec-architect）→ L1（autonomous-dev）+ layer1-independent-reviewer（F4 の読み順制約を本サイクルから適用）
- dev_mode: DH 本体は `github_assisted` 相当（PR + 人間判定。規範文書改変は auto-merge の opt-in 領域）
- AI 能力バージョン: `model-recommendations.md` 2026-08-05 版の参照世代（REGIME-LOG 既存記録より 1 世代進んでいる。
  F7 で機械記録に切り替える）
- CTL: CTL-1（2026-09-13 同期・66/66 一致）
- 儀式: レベル 3 実施済み（F1 / F2 矛盾 3 件・再提案 1 件 / F2.6 発火 0・検知器欠陥 / F2.7 再評価同梱 / F3 予告）

## 7. 実装しないもの

- philosophy.md / delegation-boundary.md / auto-merge-boundary.md の変更（I-1）
- 全 skill の英語化（日本語のトークン倍率は 1.78× → 1.21× に縮小済み。効くのは短縮であって翻訳ではない）
- 常駐 description の削減を「コスト削減」として提示すること（I-2）
- LLM を用いた routing / 失効の自動判定（I-3）
- `crosscut-hook-observer` への注入機能の同居（I-6）
- 4 段階 Council（第 8 条 minority C）の採否 — Phase B で F8 と同時に扱う

## 8. 検証

- Phase A 各 F の受け入れ基準（§3）。
- `python3 harness-verifier/verify.py --strict` 全 PASS（配布リスト / GRAPH / 参照 / hook 配線）。
- F3 の実測値と F8 の結果表が DELIVERY にある（基準値の凍結）。
- F9 の差分表が DELIVERY にある。
- 本 spec に `実装済み` を書けるのは `VERSION` ≥ 着地版（検査 9）になってから。

## 9. 参照（一次）

- 再注入: arXiv 2606.22528 / 合議の損失: arXiv 2602.01011 (ICML 2026) / 役割分割: arXiv 2609.04217 /
  自己統括 vs orchestration: arXiv 2604.27891 / 同時拘束数: arXiv 2608.12426 / 設定ファイル構造の帰無: arXiv 2605.10039 /
  文脈隔離レビュー: arXiv 2603.12123 / append-only 記憶: arXiv 2608.07429 / judge の失敗様式: arXiv 2609.02246 /
  足場効果 28pp: arXiv 2606.08529 / 請求とトークン: arXiv 2607.12161 / description 書き直し: arXiv 2606.30775
- Claude Code 公式: hooks（SessionStart stdout は文脈へ・PreCompact は注入不可）/ skills（`disable-model-invocation` /
  1,536 字 / 500 行 / compaction 25,000・5,000 tok）
- OpenAI（2026-09-13）: GPT-6 Astra 3 欠陥の第 1「旧モデル向け skill の過剰発火が自己検証を阻害」
