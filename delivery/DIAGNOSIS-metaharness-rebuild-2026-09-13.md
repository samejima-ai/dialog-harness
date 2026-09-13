# DIAGNOSIS — メタハーネス再構築診断（2026-09-13）

> **位置づけ**: `dh-upgrades/upgrade-spec-v7.0.0.md` の判断材料。DH v6.18.0 の全実測（`.claude/` 139 md）と
> 2026-09 時点の一次研究 4 軸（context 構造 / 吸収済み足場 / context rot 対策 / skill・tool 経済）を突き合わせた。
> 判定は含まない — 結論の採否は L0 儀式 F2 の人間決定（2026-09-13）が持つ。
> HTML 版（証拠等級付き・全表）: claude.ai/code/artifact/3c574055-f04e-4b4b-9fab-896b0be6c8f1
>
> 規範メタデータ:
> ```yaml
> stage: 全段階
> review_trigger:
>   - model_generation
>   - date: 2027-03-13
> ```

## 0. 結論（4 行）

1. **最優先**: 不変核の再注入。compaction で規範違反 0% → 30%、約 47 tok の再注入で 0% に復帰。DH は hook を配線済みだが
   注入 payload が無い。注入点は **SessionStart（matcher: compact）の stdout**（PreCompact は注入不可）。
2. **パージ**: 認知足場（多ペルソナ合議 / 役割分割 / 段階思考 / 自己批評 / ペルソナ付与）は実測で無効か有害。
3. **強化**: 環境足場（決定論検査 / 文脈隔離 / 権限段階 / ツール絞り / 失効可能な記憶）は健在。足場差だけで 28pt 動く。
4. **修正**: 常駐 description が一覧枠の 4.5〜6.5 倍。休眠 skill 4 本はフラグで退避、3 本は圧縮（他 skill から起動されるため）。

## 1. 計測（DH v6.18.0）

| 指標 | 実測 |
|---|---|
| skill 数 / description 合計 | 21 / 12,943 字（≈ 9,000〜13,000 tok）・中央値 631・最大 963 |
| SKILL.md 合計 / 500 行超 | 314,594 字 / 3 本（860・527・516 行） |
| references / `.claude/` 総計 | 101 本 1,186,511 字 / 1,592,127 字（spec-architect 41.4%） |
| `review_trigger` 保有 / `model_generation` 実適用 | 7 / 139（5.0%） / 1 件 |
| `model_generation` 発火（norm-scan） | 0 件 — model-recommendations.md 未更新のため検出不能（代理指標の欠陥） |
| philosophy.md 失効注釈 / `disable-model-invocation` | 0 / 0 |
| council-axis-audit | 3 ペルソナとも confidence σ ≈ 0.05（議題に反応していない） |

## 2. 訂正（前段の評定・診断からの修正 4 件）

| # | 旧 | 新 | 根拠 |
|---|---|---|---|
| 1 | philosophy.md は 58 規範で遵守の崖の底 | 文書長・位置・矛盾は効果なし（n=1,650 セッション要因計画、肯定的帰無 BF₁₀ 0.05〜0.10）。効くのは**セッション内減衰 −5.6%/生成**と**同時拘束数 k\*=2〜4** | arXiv 2605.10039 / 2608.12426 |
| 2 | description は個別上限に余裕 | 拘束は**一覧合計枠**（≈ 2,000 tok）。4.5〜6.5 倍超過の可能性。実務者由来ゆえ `/context` で要実測 | 実務者解析 |
| 3 | PreCompact hook に payload を載せる | PreCompact は注入不可。**SessionStart（compact）の stdout** が文脈に入る | Claude Code 公式 hooks |
| 4 | 休眠 7 skill をフラグで退避（26.4%） | フラグ 4 本（13.7%）。L2×2 と autonomous-drive は他 skill から model 起動されるためフラグ不可 → 圧縮 | Claude Code 公式 skills（フラグ = Claude が起動不可） |

## 3. パージ台帳（要約・等級 A = 統制付き一次）

| 足場 | 実測 | DH 該当 |
|---|---|---|
| 多ペルソナ合議 | 最良メンバーに最大 41.1% 負ける（ICML 2026） | crosscut-council（236,539 字） |
| Planner/Executor/Critic | 単体と p=0.80 で区別不能・1.79 倍コスト | L2 統括・judgment 分離 |
| graph 駆動 orchestration | 自己統括が 15/15 で勝利・失敗率ほぼ倍 | GRAPH.yml は宣言のみ＝正しい |
| 常時オン規範の積み上げ | k=8 で全条項同時充足 5.7% | 9 条を常時有効扱い |
| 外部信号なし自己批評 / 自己 judge | 横ばい〜劣化 / 自己選好は能力と無相関 | DELIVERY 自己評価 |
| 旧モデル向け回避策 | Claude Code 自身が Opus 5 向けに約 80% 削除（二次・等級 C） | 「AI は気づかないので明示」型 |

## 4. 強化台帳（要約）

| 足場 | 実測 | DH 状態 |
|---|---|---|
| compaction 後の再注入 | 0% → 30% 違反、再注入で 0%（47 tok） | **未実装**（F1） |
| 決定論検査の優越 | judge 信号は 11 通りに失敗・機械的棄却のみ回帰を捕捉 | 方向一致。「上書きは一方向」の一文が無い（F5） |
| 新規文脈・成果物のみレビュー | F1 28.6 ＞ 24.6 ＞ 23.8（生成文脈継承） | 設計一致。DELIVERY 読み順のみ（F4） |
| 失効可能な記憶 | append-only 0.210 ＜ 記憶なし 0.309、失効で 0.950 | COLD は退避のみ（F6） |
| 足場選択そのもの | GAIA 最大 28pp | 過剰パージの歯止め |

## 5. 歯止め

- 足場を全部剥がすのは誤り（28pp）。線は「認知／環境」。
- Council の −41.1% は「チームが答えを出す」設定。DH の Council は判断材料出し（final_decision: null）で射程外。ablation を先に。
- 等級 C（一覧枠 2,000 tok / hook すり抜け 5% / 80% 削減）は方向のみ信用し、設計値にしない。
