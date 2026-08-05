# ANALYSIS — DH モデル選定基準更新の判断材料（2026-08-05）

> **位置づけ**: L0（spec-architect）メタハーネス開発の対話フェーズ成果物。
> LLM モデル世代更新（Claude 5 系 / GPT-5.6 系 / Gemini 3.5-3.6 系）に伴い、
> DH のエージェント振り分け・モデル選定基準を最適化するための**判断材料**を提供する。
> 本ドキュメントは判断（judgment）の材料であって決定（decision）ではない。
> 最終決定は人間レビュー（§8 確認事項）を経て確定し、実装は別 PR で行う。
>
> 調査日: 2026-08-05 / 調査手段: ローカル一次情報源（claude-api リファレンス、2026-06-24 キャッシュ）
> + Web 調査エージェント 4 系統（Anthropic 公式 / OpenAI 公式 / Google 公式 / ベンチマーク比較）

---

## 1. 背景と課題

現行のモデル選定基準は 2026-04-18 時点・**Claude Opus 4.7 世代**を基準に策定されている
（`model-recommendations.md` 冒頭に「参照モデル世代: Claude Opus 4.7 / GPT-5.4 / Gemini 3.1 Pro 世代」と明記。
同ドキュメント自身が「新モデルリリース時に更新する」と更新条件を宣言済み）。

2026年4月以降、3社すべてで世代交代が発生:

- **Anthropic**: Fable 5 / Mythos 5（6/9）、Sonnet 5（6/30）、Opus 5（7/24）リリース。**Opus 4.1 は本日 2026-08-05 退役**
- **OpenAI**: GPT-5.5（4/23）→ GPT-5.6 ファミリー Sol/Terra/Luna（7/9 GA）。GPT-5.4 系は Codex から 8/31 削除予定
- **Google**: Gemini 3.5 Flash（5/19）/ 3.6 Flash（7/21）GA。**gemini-2.5-pro は 2026-10-16 リタイア予定・新規プロジェクトから利用不可の報告あり**

---

## 2. DH 内モデル依存箇所インベントリ

| # | 箇所 | 現在値 | 更新緊急度 |
|---|---|---|---|
| 1 | `.claude/skills/layer0-spec-architect/references/model-recommendations.md` | 全体が Opus 4.7 世代基準（2026-04-18） | **高**（選定基準の正本） |
| 2 | `.github/workflows/claude-review.yml:146` + `templates/github-workflows/claude-review.yml.template:163` | OC = `claude-opus-4-7` ハードピン | 中（Opus 4.7 は Active、retirement 下限 2027-04-16） |
| 3 | `.claude/agents/review-{fetch,difficulty,intent-gate,evidence}.md` frontmatter | `model: claude-haiku-4-5` | **低**（後継不在、現状維持が妥当） |
| 4 | `claude-review.yml` persona_tier 規則（tier2→sonnet / tier3→opus） | 抽象エイリアス指定 | 中（エイリアス解決先が CLI バージョン依存） |
| 5 | `.github/workflows/gemini-review.yml:46` + template | `GEMINI_MODEL: gemini-2.5-pro` | **高**（2026-10-16 リタイア・新規 404 報告） |
| 6 | `.github/workflows/issue-pickup.yml` | triage = gemini-cli（デフォルトルーティング） | 低〜中（CLI 側の Auto ルーティングに追従） |
| 7 | `regime-assessment.md:240`「L2発動閾値（Claude Opus 4.7 基準）」/ `layer2-orchestrator/SKILL.md`「Opus 4.7 の能力では M2 で吸収可能」 | AI 能力バージョン依存の閾値 | 中（能力向上で M2 吸収域がさらに拡大する方向） |
| 8 | `layer1-autonomous-dev/references/delivery-format.md:339` 等のテンプレ例示値 | Sonnet 4.6 / Opus 4.7 例示 | 低（例示のみ） |

**影響なしを確認済み**: 本日退役の Opus 4.1（`claude-opus-4-1`）への参照は DH 内にゼロ。

---

## 3. 各社現行ラインナップ（2026-08-05 時点）

### 3.1 Anthropic（一次情報源: ローカル claude-api リファレンス + 公式発表）

| モデル | ID | 価格 in/out ($/M tok) | ctx / max out | 状態・備考 |
|---|---|---|---|---|
| Claude Fable 5 | `claude-fable-5` | $10 / $50 | 1M / 128K | 最上位（Mythos クラス）。thinking 常時オン、**30日データ保持必須（ZDR 不可）**、`stop_reason: "refusal"` ハンドリング必須。CI 用途にはフォールバック設計が前提 |
| Claude Mythos 5 | `claude-mythos-5` | $10 / $50 | 1M / 128K | Project Glasswing 限定・招待制（DH 選定対象外） |
| **Claude Opus 5** | `claude-opus-5` | **$5 / $25**（Opus 4.8 と同額） | 1M / 128K | 7/24 リリース。**Opus 4.8 のドロップイン後継**。thinking デフォルトオン。レートリミットは 4.x Opus と**別バケット**。安全分類器 refusal あり（フォールバック先 Opus 4.8） |
| Claude Opus 4.8 / 4.7 / 4.6 | `claude-opus-4-8` 等 | $5 / $25 | 1M / 128K | Active 継続。4.7 retirement 下限 2027-04-16 |
| **Claude Sonnet 5** | `claude-sonnet-5` | $3 / $15（**導入価格 $2/$10 は 2026-08-31 まで**） | 1M / 128K | 6/30 リリース。**新トークナイザで同一テキスト約 +30% トークン**（単価据置でも実効コスト増に注意） |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | $3 / $15 | 1M / 128K | Active。retirement 下限 2027-02-17 |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1 / $5 | 200K / 64K | **後継（Haiku 5）は存在せず**、バジェット層の現行正解。retirement 下限 2026-10-15（60日前通知ポリシー） |

**プロンプトキャッシュ最小プレフィックス**（DH の反復レビューに直結）: Opus 5 = **512** tok / Opus 4.8・Sonnet 5 = 1024 / **Opus 4.7 = 2048** / Opus 4.6・Haiku 4.5 = 4096。
→ OC を 4.7 → 5 に上げるとキャッシュ効率も改善（最小プレフィックスが 1/4 に）。

**Claude Code / claude-code-action での指定方法**（DH の subagent 構成に直結）:

- subagent frontmatter `model:` の許可値: `sonnet` / `opus` / `haiku` / `fable` / フル ID / `inherit`
- エイリアス解決は CLI バージョン依存（`opus`→Opus 5 は v2.1.219+、`sonnet`→Sonnet 5 は v2.1.197+）
- claude-code-action は `claude_args: --model <ID>` で指定。同梱 CLI バージョン差でエイリアス解決が変わるため、**再現性重視ならフル ID 指定を推奨**

### 3.2 OpenAI（公式: developers.openai.com）

現行世代は **GPT-5.6 ファミリー**（7/9 GA、1.05M ctx）。GPT-6 は未リリース。

| ティア | モデル | ID | 価格 in/out | 備考 |
|---|---|---|---|---|
| フラッグシップ | GPT-5.6 Sol | `gpt-5.6-sol` | $5 / $30 | `gpt-5.6` エイリアスは Sol にルーティング |
| 標準 | GPT-5.6 Terra | `gpt-5.6-terra` | $2 / $12 | 旧 mini 相当ティア。「GPT-5.5 同等性能を低コストで」 |
| バジェット | GPT-5.6 Luna | `gpt-5.6-luna` | $0.20 / $1.20 | 旧 nano 相当 |

- 現行基準が参照する **GPT-5.4 系は Codex から 2026-08-31 に削除予定**（API では当面現役）
- 世代交代型の実質値下げ: 標準 $2.5/$15 → $2/$12、軽量 $0.38/$2.25 → $0.20/$1.20
- ※ベンチ調査側の二次ソースでは Terra $2.50/$15 / Luna $1/$6 と記載が割れた。**公式ドキュメント値（上表）を採用**し、実装時に価格ページ原本で最終確認のこと

### 3.3 Google（公式: ai.google.dev）

Gemini 4 は未リリース。フラッグシップは 3.1 Pro（**Preview のまま長期運用**）。

| ティア | モデル | ID | 価格 in/out | 備考 |
|---|---|---|---|---|
| フラッグシップ | Gemini 3.1 Pro | `gemini-3.1-pro-preview` | $2 / $12（≤200K） | 無料 tier なし。Preview のまま（SLA 要件があるなら明記すべきリスク） |
| 標準 | Gemini 3.6 Flash | `gemini-3.6-flash` | $1.50 / $7.50 | 7/21 GA。**コーディング系ベンチで 3.1 Pro に全勝**（後述） |
| バジェット | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | $0.30 / $2.50 | 無料 tier あり |

**DH 直撃の変化**:

- **`gemini-2.5-pro`: 2026-10-16 リタイア予定（公示済み）+ 新規 GCP プロジェクトからは既に 404 報告あり**。GitHub Copilot では 7/31 に廃止済み。公式推奨移行先は 3.1 Pro（コスト重視なら 3.6 Flash）
- gemini-cli のデフォルトは「Auto (Gemini 3)」ルーティング化（単純→2.5 Flash、複雑→3 Pro）。DH の issue-pickup triage はこの追従で概ね問題なし
- Gemini 新世代でもサンプリングパラメータ（temperature/top_p/top_k）deprecated — 3 社共通の流れ

---

## 4. ベンチマーク比較の要点

### 4.1 指標選定の前提（重要）

- **SWE-bench Verified は選定基準から降格推奨**: 上位が 95-97% に飽和し弁別力なし。汚染問題（gold パッチ逐語再現、困難問題の 59.4% にテスト不備）で OpenAI は 2026年2月に公表を廃止。
- 主軸は **SWE-bench Pro**（汚染対策後の実質標準）と **Terminal-Bench 2.1**（エージェントループ性能）。
- scaffold 差・試行回数差で数〜10 ポイント級のブレが常態（例: Sonnet 5 の SWE-V が出典間で 72.7 / 82.1 / 85.2 と乖離）。ベンダー公表値と第三者値の併記が必須。

### 4.2 主要スコア（抜粋）

| モデル | SWE-bench Pro | Terminal-Bench 2.1 | SWE-V（参考） |
|---|---|---|---|
| Claude Fable 5 | **80.3%**（全モデル中トップ） | 不明 | 95.0 |
| Claude Opus 5 | 不明 | 不明 | 96-97（vals.ai 97.0） |
| Claude Opus 4.8 | 69.2% | 74.6% | 88.6 |
| GPT-5.6 Sol | 64.6% | **88.8%**（シングル） | 96.2（第三者） |
| Claude Sonnet 5 | 63.2% | **80.4%** | 72.7-85.2（乖離大） |
| Gemini 3.6 Flash | 58.7% | 78.0% | — |
| Claude Sonnet 4.6 | 58.1% | — | — |
| Gemini 3.1 Pro | 54.2% | 73.8% | 80.6 |
| Claude Haiku 4.5 | 不明 | 約 40%（旧版・第三者） | 73.3（公式・簡素 scaffold） |

### 4.3 選定基準に効く構造変化

1. **ティア名 ≠ 性能の逆転が発生**: Sonnet 5 > Opus 4.8（Terminal-Bench 2.1: 80.4 vs 74.6）、Gemini 3.6 Flash > 3.1 Pro（コーディング系全勝）。「上位ティア = エージェント性能上位」の前提が崩れており、**ティア名でなくベンチ実測でマッピングすべき**。
2. **軸によるねじれ**: SWE-bench Pro は Anthropic 優位、Terminal-Bench は OpenAI 優位。単一指標での序列化は不可。
3. **Haiku 4.5 の解像度**: 単発パッチ生成・分類・PR レビューのサブステップは実用ライン（SWE-V 73.3）だが、長い端末エージェントループは非推奨（TB 約 40%）。→ DH の「ワーカー = Haiku / 判断 = 上位」分業は**ベンチ的にも正しい設計**として追認される。
4. コスト対性能: 500 行 PR のレビューコストはフロンティア 3 社とも約 $0.07/PR。3 モデル並列レビューで単独比約 1/3 多く問題検出（Claude=ロジック、GPT=セキュリティ、Gemini=リポジトリ全体）— DH の多層防御（Copilot + Gemini + Claude 併走）を支持するデータ。

---

## 5. 同等 SPEC マッピング更新案（2026-08 版）

現行 `model-recommendations.md` の表（Opus 4.7 / GPT-5.4 / Gemini 3.1 Pro 世代）を以下に置換する案:

| ティア | Anthropic | OpenAI | Google | 補足 |
|---|---|---|---|---|
| 最上位（新設検討） | Fable 5（$10/$50） | — | — | 超長時間自律・最難タスク限定。CI 組込は refusal/データ保持要件から非推奨 |
| フラッグシップ | **Opus 5**（$5/$25） | **GPT-5.6 Sol**（$5/$30） | Gemini 3.1 Pro（$2/$12）※1段劣後・価格は標準帯 | Opus 5 と Sol はほぼ互角（軸によるねじれあり） |
| 標準 | **Sonnet 5**（$3/$15） | **GPT-5.6 Terra**（$2/$12） | **Gemini 3.6 Flash**（$1.50/$7.50） | Google 採用時は Pro でなく 3.6 Flash を標準実装モデルに |
| バジェット | **Haiku 4.5**（$1/$5） | **GPT-5.6 Luna**（$0.20/$1.20） | Gemini 3.5 Flash-Lite（$0.30/$2.50） | Haiku 4.5 が品質最強、Luna/Flash-Lite が価格最強 |

---

## 6. DH 各接点への影響と選択肢

### 6.1 claude-review.yml — OC モデル（現: `claude-opus-4-7`）

| 案 | 内容 | 評価 |
|---|---|---|
| **A（推奨）** | `claude-opus-5` へ昇格 | 同価格（$5/$25）でベンチ大幅向上・キャッシュ最小 2048→512 tok。ただし下記「移行時の必須プロンプト再調整」を同時適用すること |
| B | `claude-opus-4-8` へ昇格 | 安全側の一段刻み。同価格・破壊的変更なし（4.7 と同一リクエスト面）。refusal 考慮も最小 |
| C | 現状維持（4.7） | retirement 下限 2027-04-16 で当面可。ただし世代 2 つ遅れ・キャッシュ最小 2048 tok のまま |

**案 A 採用時の必須プロンプト再調整**（Opus 5 移行ガイドの公式知見、DH のレビュー文脈に直結）:

1. **severity フィルタ問題**: 「重大なもののみ報告せよ」型の指示に忠実に従い**測定 recall が低下**する。→ 発見段階は「確信度・重大度付きで全件報告、フィルタは下流」へ。DH は既に Council/judgment の 2 段構造なので適合しやすいが、各ペルソナ・OC プロンプトの文言確認が必要
2. **検証 scaffolding の削除**: Opus 5 は指示なしで自己検証する。「検証せよ」「サブエージェントで確認せよ」型の指示は過剰検証を招くため**削除**が公式推奨
3. **サブエージェント委譲の抑制**: Opus 4.8 と逆に**委譲過多**の傾向。OC に明示的な委譲キャップ（DH は委譲 1 階層・役割固定なので構造的に緩和されているが、文言確認は必要）
4. thinking デフォルトオン化に伴う `max_tokens` 見直し、`stop_reason: "refusal"` ハンドリング（cyber 系パス検査で誤発動の可能性 → フォールバック先 Opus 4.8 の設定検討）
5. レートリミットが 4.x Opus と別バケット（移行時に限度確認）

**関連**: Routine pre-gate（tier1 で Opus OC ごとスキップ）の決定論ゲートは、OC 単価が変わらないため設計変更不要。

### 6.2 persona_tier 規則（tier2→sonnet / tier3→opus）

- 昇格ロジック自体（難度で縦昇格・3 ペルソナ横対称）は維持で問題なし
- 解決先を **Sonnet 5 / Opus 5 のフル ID で明示**することを推奨（claude-code-action 同梱 CLI のバージョン差でエイリアス解決が `4.6/4.7` に留まるリスク回避）
- **Sonnet 5 の注意**: 新トークナイザで同一テキスト約 +30% トークン。導入価格 $2/$10 は 8/31 終了 → 9 月以降のコスト試算は $3/$15 で。Terminal-Bench で Opus 4.8 を上回るため、「tier3 = opus」の価値は Opus **5** とセットで初めて維持される（tier3 を Opus 4.8 のままにすると tier2 Sonnet 5 と逆転しうる）

### 6.3 ワーカー 4 種（現: `claude-haiku-4-5`）

**現状維持を推奨**。Haiku 5 は存在せず、Haiku 4.5 がバジェット層の現行正解。DH のワーカーは単発・定型タスク（fetch/難度判定/意図ゲート/Evidence 化）でベンチ特性（単発は実用・長ループは苦手）とも整合。retirement 下限 2026-10-15 のため、**60 日前通知の監視だけ継続**。

### 6.4 gemini-review.yml（現: `gemini-2.5-pro`）— 最優先

- **今サイクルで移行必須**。10/16 リタイア公示済み + 新規プロジェクト 404 報告 + Copilot では廃止済み
- 選択肢: **A（推奨）`gemini-3.6-flash`** — コーディング系で 3.1 Pro に全勝・出力 58% 安・無料 tier あり（gemini-review の「無料 tier 併走」という当初採用理由と整合） / B `gemini-3.1-pro-preview` — 公式推奨移行先だが Preview のまま・無料 tier なし・コーディングでは 3.6 Flash に劣る
- v5.5.1 の「flash→pro 昇格」判断は当時の世代では正しかったが、**現世代では Flash 系が逆転**しており、pro 固定の前提が崩れている（gemini-review.yml のコメント根拠も要書き換え）

### 6.5 model-recommendations.md（選定基準の正本）

全面改訂が必要。改訂項目: (1) 参照モデル世代を 2026-08 に更新 (2) モード別推奨表（M1 = Sonnet 5/Terra/3.6 Flash、M2 = Opus 5/Sonnet 5、L2 = Opus 5/Sol） (3) 同等 SPEC マッピング → §5 の表 (4) ハイブリッド運用表（標準推奨: L0 = Opus 5、L1 = Sonnet 5） (5) モデル別劣化と対策（Opus 5 の severity フィルタ/過剰検証/委譲過多、Sonnet 5 のトークナイザ、Fable 5 の refusal/ZDR、Haiku の従来劣化モード継続） (6) 価格表 (7) 「ティア名でなくベンチ実測でマッピング」原則の明文化（§4.3-1 の逆転現象）。

### 6.6 regime-assessment.md L2 発動閾値 / layer2-orchestrator

「Claude Opus 4.7 基準」の閾値は Opus 5 世代で M2 吸収域がさらに拡大する方向。閾値の緩和は Council 諮問マターだが、少なくとも**基準バージョン表記の更新**（+必要なら「4.7 時点の閾値を暫定継続」の明記）が必要。

---

## 7. 判断材料の限界

- ベンチスコアの多くは第三者測定・scaffold 非開示で、±数ポイントの不確度がある。特に **Opus 5 の SWE-bench Pro / Terminal-Bench 公式値は未公表**（不明のまま採用判断することになる）
- OpenAI の Terra/Luna 価格は公式ドキュメント値を採用したが、二次ソースと乖離があった（実装時に再確認）
- Gemini 3.1 Pro のコンテキスト長は 1M/2M で情報源が割れており未確定
- Aider Polyglot は 2025-11 から未更新のため不使用。LMArena coding は GPT-5.6 参加直後で順位未安定

---

## 8. 人間への確認事項（decision points）

| # | 論点 | 選択肢 | AI 推奨 |
|---|---|---|---|
| D1 | OC モデル | A: Opus 5（+プロンプト再調整） / B: Opus 4.8 / C: 4.7 維持 | **A**（同価格・キャッシュ改善。再調整コストを許容できるなら） |
| D2 | persona_tier 解決先 | フル ID 明示（sonnet-5/opus-5） / エイリアス継続 | **フル ID 明示** |
| D3 | gemini-review | A: 3.6 Flash / B: 3.1 Pro Preview | **A**（無料 tier 整合・ベンチ優位。10/16 前に必着） |
| D4 | ワーカー | Haiku 4.5 維持 / Sonnet 5 昇格 | **維持**（後継不在・用途適合） |
| D5 | Fable 5 の扱い | 選定基準に「最上位ティア」として記載のみ / 記載せず | **記載のみ**（CI 組込は refusal・データ保持要件から非推奨と明記） |
| D6 | L2 発動閾値 | 表記更新のみ / Council 諮問して緩和 | **表記更新のみ**（緩和は実運用データが貯まってから） |
| D7 | 実装の分割 | 一括 PR / 緊急度順に分割（gemini 先行） | **分割**（D3 は期日制約があるため先行可能） |

---

## 9. 出典

**一次情報源**: ローカル claude-api リファレンス（2026-06-24 キャッシュ、モデル表・価格・migration guide）/ anthropic.com 公式発表（Fable 5・Opus 5・Sonnet 5）/ platform.claude.com（models overview・deprecations）/ code.claude.com（model-config・sub-agents）/ developers.openai.com（GPT-5.6 各モデル・deprecations）/ learn.chatgpt.com（Codex models・changelog）/ ai.google.dev（models・pricing・changelog・rate-limits）

**第三者**: vals.ai / BenchLM / llm-stats（リーダーボード）、Vellum / The Agent Report / codingfleet / emergent.sh（分析）、GitHub Changelog（Copilot の Gemini 廃止）、Google AI Developers Forum（2.5-pro 404 報告）

詳細 URL は各調査エージェントの出力に記録（本ドキュメントの各節に主要 URL を記載済み）。
