# upgrade-spec v6.15.0 — 多起点ループ（テレメトリ逆流の最小実装と、受入・介入の計測）

> **状態: L0 起草（人間レビュー待ち）**。本仕様の実装は escalation-matrix「規範文書改変」行に従い、
> 人間レビュー通過後・実装前に Council 諮問を経る。
> 起点: L0 対話（2026-08-27）のビジョン提示 ──
> 「目指しているのは必要な時だけ人間にエスカレーションする仕組み／開発のトリガーを複数経路作って
> 複数のループ経路もいるかな／グラフエンジニアリングに繋げたい／DH はその仕組みを保持するが
> カクマンプラットフォーム v3 が実運用開発している DH 展開プロジェクト」
> ＋ 追補指示（2026-08-27）「適当に挙げただけ、世界水準を調べて網羅的に考えたい」。
> **一次材料**: `delivery/ANALYSIS-agentic-sdlc-world-standard-2026-08-28.md`（3 系統の出典付き網羅調査。
> 本仕様の機能はすべて同分析のギャップ順位 G1〜G7 に対応する）。

---

## 0. 位置づけ — 世界水準照合の結論を機能に落とす

網羅調査（前掲 ANALYSIS）の結論:

- 業界は単一バックボーン（トリガー → 計画 → 隔離実行 → 自己検証 → PR → 人間レビュー）に収束済み（W1）
- DH の**中間工程は 7.5/10 で世界水準以上**の箇所もある（Falsification 明示・Council 重み意味論・CTL の機械化）
- 空白は**入口 1.5/10**（テレメトリ逆流が 1 本も無い・W3）と**計測**（受入・介入率が無い・W9）に集中
- 業界標準からの意図的逸脱は 1 点（opt-out auto-merge）。担保は境界 SPEC + roll-back ゲート 2026-11-06

本仕様は空白の上位 2 つ（G1 テレメトリ逆流・G2 受入監査）を閉じ、多起点をグラフに宣言する。
**中間工程には触れない。**

「必要な時だけ人間にエスカレーション」の現在地: confidence 帯別介入率 33/18/10%（n=137, d=0.62）、
CTL-2 で C カテゴリ 96% 自律・献上 8%。欠けているのは判断の絞り込みではなく**判断の手前**
（仕事が人間のラベルからしか生まれない）と**判断の後**（受け入れられたかの計測）である。

### 多起点がグラフを本物にする（課題 2 との接続）

入口が 1 つのグラフに edge 評価は要らない。トリガーが複数になって初めて「この起点から来た仕事は
どの経路を通り、どこで止まるか」が実行時の問いになり、GRAPH.yml の predicate 併置（課題 2 案 A）が
仕事をする。世界水準でもグラフ表現は「型付き状態グラフ + checkpoint + interrupt/resume」に収束しており
（ANALYSIS §2-E）、**本仕様は課題 2-A の前提**にあたる。

### DH と kakuman-platform-v3.0 の分業

DH = D4（機構の保持・F1/F2/F3 の実装先）、kakuman-v3.0 = D1-D3（実運用・F4 の適用先）。
還流は `dh-manifest.yml` upstream（U-1〜U-5）のみ。

---

## 不変条件（全機能共通）

- **I-1 新トリガーは全て「観測 → 候補化 → 人間最終承認」の 3 段階から始める**（philosophy 第 8 条）。
  signal-scan が起こす Issue は**候補**（`ready-for-ai` を付けない）。世界水準でも還流は
  「人間承認ゲート付き段階昇格」に収斂している（W8）。自動昇格は CTL-3 + Council 再諮問まで凍結
- **I-2 検知は決定論**。LLM 判定を含む検知器を作らない（第 2 条）。Sentry fixability score 型の
  「数値化された自己評価で無人発火を制御する」（W2）は将来拡張とし、初版は存在検知のみ
- **I-3 宣言と配線を同一 PR で行う**。新トリガー・新ループは GRAPH.yml のノード/エッジ追加と実装を
  同じ PR に含める（「宣言はあるが配線がない」の再生産を構造的に禁じる）
- **I-4 エスカレーション削減を目標値にしない**。介入率・受入率は**観測**するが目標化しない（Goodhart。
  W9 の知見「熟練者ほど auto-approve と interrupt が同時に増える」が示すとおり、介入の減少は
  単独では改善を意味しない）
- **I-5 単調性の継承**。新トリガーが CTL を参照する場合、権限の縮小方向にのみ用いる（Council 634df2）

---

## F1. signal-scan — テレメトリ逆流の最小実装（priority: critical / G1・W3）

`scripts/signal-scan.py` + `.github/workflows/signal-scan.yml`（cron 日次）を新設する。

| 条件 | 内容 |
|---|---|
| F1-1 | 検知器は初版 **4 本に固定**: (a) 赤 CI（master 上の workflow 連続失敗）(b) 滞留 PR（open のまま N 日超・stop ラベル無し）(c) 期限切れ `review_trigger`（規範メタデータの cycles/measured 超過）(d) CTL 未評価の滞留（`pending` N 件超）。業界の主要逆流源（エラー監視・アラート・CI 失敗・analytics）のうち、**DH 自身のリポジトリで観測可能なもの**に限定 |
| F1-2 | 出力は **Issue 起票（候補）**。`signal-detected` ラベルを付け、`ready-for-ai` は付けない（I-1）。本文に検知器名・実測値・根拠パスを機械出力 |
| F1-3 | 重複起票の禁止（open Issue に同一検知器×同一対象があれば skip） |
| F1-4 | 起票上限 1 run 3 件（circuit breaker） |
| F1-5 | GRAPH.yml に `signal-scan`（kind: tool）ノードと `signal-scan → issue-quality-gate` エッジを同 PR で宣言（I-3） |

**書かないもの**: LLM 検知（I-2）／エラー監視連携（F4 で kakuman 側から）／通知・ダッシュボード。

## F2. agent-PR 受入監査 — 受入・介入の決定論計測（priority: critical / G2・W9）

`scripts/pr-audit.py` を新設する。**gh api のみで算出可能・LLM 判定なし**。

| 条件 | 内容 |
|---|---|
| F2-1 | 算出する指標は世界水準の事実上の標準 4 つ: **merge 率**（agent 発 PR の merge/close 比）/ **revert 率**（merge 後 revert された比）/ **human-commit 介入率**（merge された agent PR のうち人間 commit が積まれた比）/ **タスク種別別受入率**（feat/fix/docs/chore 別） |
| F2-2 | 参照値を併記する: dotnet/runtime 実測（merge 67.9% / revert 0.6% / 介入 45%）。**目標値にはしない**（I-4）。比較の物差しとしてのみ |
| F2-3 | 出力は `delivery/PR-AUDIT-<YYYY-MM>.md`（月次・cycle-retrospective から参照）。既存 `harness-verifier/reports/` の月次経路に相乗りしてよい |
| F2-4 | CTL の agreement_rate（判断への同意）と本監査（成果物の受入）は**別の軸**として扱い、混ぜない。前者は Council の、後者はパイプライン全体の指標 |

## F3. 多起点の GRAPH 宣言 + predicate 併置（priority: high / 課題 2-A 前提）

| 条件 | 内容 |
|---|---|
| F3-1 | 起点を列挙する: `human-label` / `signal-scan`（F1）/ `ritual` / `upstream-decision`。各起点からの経路を edge で宣言 |
| F3-2 | `condition` に省略可能な `predicate:` を併置。書けるもののみ（`judgment_confidence < 0.5` / `ctl == "CTL-0"` 等）。書けないもの（案の拮抗・仕様曖昧）は書かない。**人間の課題 2 判断（案 A/B/C/D）を待って実装する** |
| F3-3 | `execution_graph.py` に G-6 を追加: `predicate:` を持つ edge の述語が CI で評価可能（参照値が repo-scope に実在）かを検査。WARN 開始 |
| F3-4 | GRAPH.yml 不変条件 I-2（実装が正・宣言が従）は変更しない。predicate は「実行系が宣言を参照する」形（PR #201 の CTL ゲートと同型）で実装 |

## F4. kakuman-v3.0 エラー監視逆流 — テンプレートのみ（priority: medium / G3・W3）

| 条件 | 内容 |
|---|---|
| F4-1 | `templates/rules/common/` に telemetry-reflux テンプレートを新設: プロダクトが自らの逆流源（エラー監視・analytics・計算可能 UX 代理指標）と閾値を宣言する枠。Sentry → 課題候補の経路を想定（kakuman-v3.0 は Sentry MCP 接続済み） |
| F4-2 | 逆流の出力形式は F1 の検知器 (e) として追加可能な形（プロダクト評価 → 課題探索 → Issue 候補のループ接続） |
| F4-3 | 実定義・実運用は kakuman-v3.0 側（D1-D3）の作業。DH へ還流するのは U-5 に従い実測を経た知見のみ |

## F5. 開発環境評価の機構化（priority: low / 再調査サイクル）

| 条件 | 内容 |
|---|---|
| F5-1 | DIAGNOSIS（ループ 6 軸 / グラフ 10 特徴 / 成熟度 8 段階）を再実行可能な儀式へ: `ritual-protocol.md` に「四半期ごと、または major 昇格前」の実行条項を追記。**前回値との差分**を必須出力に |
| F5-2 | 本仕様の一次材料（ANALYSIS 2026-08-28）も同周期で再調査する（工程カタログの陳腐化速度を考慮し 6 ヶ月目安） |

---

## 実装しないもの（明示的スコープ外・出典付き）

- **debate 相互参照** — PR #170 実測 + 「panels help, debates hurt」で既却下
- **進化的自己改善（DGM/AlphaEvolve 型）** — 第 8 条。DGM 自身の暴走防止（sandbox+人間監督+archive）と同型の結論に DH は独立到達済み
- **汎用コンテキスト要約の拡充** — 統制実験（arXiv 2602.11988）でタスク成功率を改善せず +20% コスト。DH の購読圧削減方針の外部裏付け
- **draft PR ゲートへの回帰** — 業界標準（W1）だが、DH は opt-out auto-merge を境界 SPEC + roll-back ゲートで維持する。**2026-11-06 の roll-back 評価で再判定**
- **dev-diary / S/U/R / conflict_type E/G** — 各既存線に従う（重複させない）
- 予算層停止条件（G4）・保守性遅行指標（G5）・feature list（G6）・EDDOps（G7）— 申し送り（下記）

## 判断点（人間へ）

1. F1-1 の閾値（滞留 N 日・pending N 件）— 提案初期値: 7 日 / 10 件
2. F3-2 は課題 2 の判断待ち — 案 A 採択なら本仕様に含める、案 D なら F3 を落とす
3. cron 頻度 — 提案: 日次 1 回
4. F2 の agent 判定基準 — author が ALLOWED_AUTHORS の PR を agent 発とみなす（提案）

## 申し送り

- G4（token/cost budget を実行経路へ）: W6 の 3 層のうち欠けている予算層。circuit breaker の拡張として次版
- G5（churn / 複製率の月次観測）: GitClear 型。harness-verify 月次レポートへの追加候補
- G6（feature list `passes:false` 型の完了防止）: L1 SKILL への 1 節追加で足りる可能性
- G7（EDDOps golden set）: 自動評価器の整備が前提。効果測定は「人間ラベル起点以外から生まれた PR の比率」（F2 で計測可能になる）を先に見る
- 検知器の拡張（W2 型の fixability score 化を含む）は F1 運用実測 1 ヶ月後に再評価
