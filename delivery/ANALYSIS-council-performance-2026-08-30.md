# Council 判定支援機構の性能計測 — 何が測れて、何が測れていないか

- 日付: 2026-08-30
- 対象: `history/COUNCIL-LOG.md`（§8 ブロック形式 67 発動、2026-04-29 〜 2026-08-28）
- 実装: `scripts/council-performance.py` / 回帰テスト `scripts/test-council-performance.py`
- 位置づけ: `scripts/council-axis-audit.py`（**入力側** = 3 軸が独立に観測できているか）の双対として、**出力側** = 出た判定がその後どうなったかを測る

---

## 0. 要旨

1. **機構は「使われて」いる**: 67 発動、判定→合意リードタイム中央値 5 分、94% が 24 時間以内に決着。follow-up 質問が発生したのは 3.5%。**運用コストの面では機能している**
2. **`judgment_confidence` は弱いが有意に当たっている**: Brier 0.1617、ベースレート予測器比 skill score **+0.096**、AUC **0.689**。系統誤差 −0.024 で過信はない。**自信の値は prompt の飾りではなく、結果と相関する情報を持っている**
3. **しかし CTL 算出の入力である `agreement_rate` は 1.000 で、下がる経路が構造的に存在しない**: 67 発動中 `rejected` 0 件、`modified`（骨格差し替え）0 件。負例が空の指標で自律権限を昇格させている
4. **決定的な限界**: `implementer_consent` は **受容の記録であって正解の記録ではない**。判定が現実に妥当だったかを保持する field はログに存在しない。したがって本計測が出せるのは「推奨が採られる率」と「自信の当たり具合」までで、**判断の正しさは原理的に測れていない**

---

## 1. 採択 — 同じログから出る 2 本の率

| implementer_consent（正規化） | 件数 | 比率 |
|---|---|---|
| `agreed`（無修正で採用） | 52 | 77.6% |
| `agreed_with_synthesis`（骨格を採り、少数意見等を併合） | 14 | 20.9% |
| `modified`（骨格を差し替え） | 0 | 0% |
| `rejected` | 0 | 0% |
| 未記録 | 1 | 1.5% |

- **CTL 定義の `agreement_rate` = 1.000**（分子 = `agreed + agreed_with_synthesis`、母数 66、負例 0）
- **無修正採択率 = 0.788**（骨格に何も足されずそのまま採られた率、母数 66）

`ctl-calculation.md` §status が v6.12.0 で `agreed_with_synthesis` を分子に入れたのは論理として正しい（止揚は推奨動作であり不同意ではない。それを `modified` に落とすと「推奨動作を行うほど CTL が上がらない」逆行が起きる）。しかし**結果として指標が全実測点で 1.000 に張り付いた**。

CTL-1/2/3 の閾値はいずれも `agreement_rate ≥ 0.90` または `≥ 0.95` を要求する（`ctl-calculation.md` L126-128）。実測で分子から落ちるのは `modified` と `rejected` の 2 値だけであり、**その 2 値は 67 発動で一度も記録されていない**。これは「Council の判定が一度も差し替えられなかった」ことを意味するのではなく、より正確には次のいずれかである:

- (a) 実装者が骨格を差し替えたケースがあったが、`_with_` 語尾で記録された
- (b) 判定と実装が同一セッションの同一 AI で連続しており、**判定を出した側が consent も書いている**ため、差し替えが「別案の採用」ではなく「判定の修正」として吸収された

`ctl-calculation.md` L188 は「AI が自らの判定を `agreed_with_synthesis` と称して agreement_rate を押し上げる経路は無い（本区分は人間の事後評価が入力する）」と規定する。しかし COUNCIL-LOG の `implementer_consent` は §8 の後追記フィールドであり、**その後追記を人間が行ったことを検証する機械経路は存在しない**。規定と実装のあいだにギャップがある。

> **これは指標の閾値の問題ではなく、負例の生成経路の問題である。** 閾値を 0.95 に上げても 1.000 は通る。

## 2. キャリブレーション — 自信は当たっているか

「無修正採択（`agreed`）を 1、それ以外を 0」とし、`judgment_confidence` を予測確率とみなして評価した（n=60）。

| 指標 | 値 | 読み |
|---|---|---|
| 実測ベースレート | 0.767 | |
| 平均 confidence | 0.743 | |
| **系統誤差** | **−0.024** | 過信なし。むしろわずかに控えめ |
| **Brier score** | **0.1617** | |
| ベースレート予測器の Brier | 0.1789 | 常に 0.767 と答える無情報予測器 |
| **skill score** | **+0.096** | 無情報予測器より 9.6% 改善 |
| **AUC** | **0.689** | 0.5 = ランダム |

| confidence ビン | n | 予測平均 | 実測無修正採択率 |
|---|---|---|---|
| 0.00–0.70 | 9 | 0.536 | 0.556 |
| 0.70–0.80 | 32 | 0.750 | 0.750 |
| 0.80–0.90 | 18 | 0.827 | 0.889 |
| 0.90–1.00 | 1 | 0.900 | 1.000 |

ビンごとの予測平均と実測がほぼ一致しており、**キャリブレーションは良好**。判別力 AUC 0.689 は強くはないが、ランダムからは明確に離れている。

これは `council-axis-audit.py` の B2 所見（各ペルソナの confidence が σ ≈ 0.04 で固定＝ prompt の産物の疑い）と**矛盾しない**。ペルソナ個々の confidence は固定的でも、**judgment 段の合成 confidence は議題に反応している**。σ の警告はペルソナ層に対するものであり、判定層はそれとは別に評価すべきである。

## 3. 事前シグナルは結果を予測するか

機構が「自分の弱い判定」を事前に見分けられているかを測る。

**`human_escalated` — 最も強いシグナル**

| 値 | n | 無修正採択率 | 平均 confidence |
|---|---|---|---|
| auto | 55 | **0.855** | 0.774 |
| escalated | 11 | **0.455** | 0.605 |

人間へ上げた判定は、上げなかった判定の**半分近くしかそのまま通っていない**。これは機構の失点ではなく**エスカレーション基準が正しく効いている証拠**である。低 confidence → escalate → 実際に修正が入る、という連鎖が観測できる。

**`conflict_type`**

| 値 | n | 無修正採択率 | 平均 confidence |
|---|---|---|---|
| `unanimous` | 25 | 0.880 | 0.795 |
| `simple_conflict` | 25 | 0.680 | 0.676 |
| `reason_divergence` | 6 | **0.500** | 0.793 |

注目すべきは `reason_divergence`（異なる次元から同じ結論に到達）である。**confidence は高い（0.793）のに無修正採択率は最低（0.500）**。3 軸が別々の理由で同じ結論に達したとき、機構は強く確信するが、実際にはその後に何かが足されている。n=6 と小さく断定はできないが、`conflict-typology.md` の対立類型 B を「情報量が多い good case」として扱う現行の解釈に対する反証候補として観測を続ける価値がある。

**`category`（重み軸）**

| 値 | n | 無修正採択率 |
|---|---|---|
| `implementation` | 10 | 0.900 |
| `conception` | 32 | 0.812 |
| `operation` | 4 | 0.750 |
| `judgment` | 16 | **0.625** |

既定カテゴリである `judgment` が最も低い。`category_fallback` で流れ込む先が最も弱いという構図であり、カテゴリ判定の精度が結果に効いている可能性がある。

## 4. 計測可能性 — 測れないものは性能の欠落ではない

| フィールド | 記録率 |
|---|---|
| `decision_category` | 94.0% (63/67) |
| `judgment_confidence` | 91.0% (61/67) |
| `conflict_type` | 88.1% (59/67) |
| `persona_summary` | 86.6% (58/67) |
| `timestamp` | 86.6% (58/67) |
| `dimension` | **58.2% (39/67)** |
| `options` | **16.4% (11/67)** |
| `execution_mode` | **1.5% (1/67)** |

`dimension` / `options` / `execution_mode` の低さは既知（axis-audit B5 / B6 正規化ギャップ / B7 観測窓未到達）で、本計測でも同じ結論に達した。**これらは機構の性能が低いのではなく、性能を測る手段が無いことを示す。** 是正は記録側（`output-format.md` §8）に対して行う。

## 5. 測れていないもの（最重要）

**`implementer_consent` は受容の記録であって正解の記録ではない。**

判定が現実に妥当だったか — 採用した案が後に問題を起こさなかったか、棄却した案のほうが良かったのではないか — を保持する field はログに存在しない。67 発動のうち後続 Council が明示的に前の判定を参照するのは 2 件（`parent_invocation_id` / `references_prior`）にとどまる。一方で `minority_opinion` には「Wave N 末で観測し、条件が満たされれば再諮問」という**将来検証の約束**が 8 件以上書き込まれているが、**それが実際に検証されたかを追跡する機械経路は無い**。

したがって現状の計測が答えているのは次の 2 問までである:

- 「この機構の推奨は採られるか」→ はい（無修正 78.8%、何らかの形での採用 100%）
- 「この機構は自分の判定の弱さを事前に見分けられるか」→ ある程度（AUC 0.689、escalation が 0.855 vs 0.455 で分離）

答えていないのは「**この機構の判断は正しいか**」である。そして CTL（自律権限の昇格）は前者の指標だけを入力としている。

### 提案（判断は人間 = D5 に残す）

1. **`minority_opinion` の再諮問約束に期日と invocation_id を持たせる** — 「Wave N 末で観測」を機械が拾える形（`revisit_at` / `revisit_condition`）にすれば、初めて**予測 → 検証**のループが閉じる。これが唯一、受容ではなく妥当性を測る経路になる
2. **`implementer_consent` の後追記に記入主体を残す** — `consent_source: human | implementer_ai`。`ctl-calculation.md` L188 の規定を機械可読にするだけで、負例ゼロの解釈が (a) と (b) に切り分けられる
3. **CTL の入力に `agreement_rate` 以外を足すかは L0 対話** — 本文書は指標を追加しない。負例ゼロの事実を提示するにとどめる（`council-weights.md` §編集プロトコルと同型で、数値・算出式の変更は L0/D5 専管）

---

## 6. 参考: AI 判断のベンチマークは存在するか

外部にベンチマークは存在するが、**本機構が測りたいものとは対象がずれている**。3 層に分けて整理する。

### 層 1: LLM-as-a-Judge の評価（最も近い、しかし対象が違う）

「LLM が採点者として人間とどれだけ一致するか」を測る系統。標準指標は **Cohen's κ による人間ラベルとの一致率**、および較正指標（**ECE / Brier score / MCE / NLL**）。2026 年の大規模評価では、frontier モデルの judge が**一致率と一貫性は高いのに妥当性（validity）が伴わない**ことが報告されている（"Reliability without Validity"）。また judge の**過信**は診断済みの既知問題として扱われている。

- 本機構との差: これらは**既に正解ラベルがある**タスクの採点者を測る。Council が扱うのは正解ラベルの無い設計判断であり、そのまま適用できない
- 転用できる部分: **較正の測り方**はそのまま使える。本計測の Brier / skill score / ビン別実測はこの系統の標準手法をそのまま持ってきたもの
- 実務基準として流通している線: judge を人間注釈セットに対し **κ を実測し 85-90% 一致**まで較正する、位置バイアス・冗長性バイアスの統制、別系統モデルとのクロスチェック

### 層 2: 多エージェント熟議の評価（構造が最も近い）

複数ペルソナが議論して結論を出す構造そのものを評価する系統。2026 年に該当研究が複数出ている:

- **12 Angry AI Agents** — 映画に忠実な 12 ペルソナが殺人事件を評議する設定で多エージェント熟議を評価する。ペルソナ付与が結論に与える影響を測る点が Council と同型
- **LLM Agents for Deliberative Collaboration**（部分観測下の共同意思決定）— 熟議協調が**どこで失敗するか**の診断ツールとして設計されており、ベンチマークというより故障モード分類に近い
- **Budgeted Act-or-Defer Multi-Agent LLM Deliberation** — 「自分で決めるか、上に上げるか」を局所信頼性の上界で決める枠組み。**本機構の `human_escalated` とほぼ同じ問題設定**であり、実測の 0.855 vs 0.455 という分離はこの系統の言葉で言えば defer 判定が機能していることを意味する
- 汎用ベンチ（MMLU-Pro / LogiQA 等）上で異種エージェントを複数ラウンド議論させる評価も標準化されつつある

### 層 3: 方針曖昧性下の判断（Council の実際の用途に最も近い）

- **DRIP-R** — 実世界の方針が曖昧な状況での意思決定・推論のベンチマーク。「規約が矛盾する / 明記が無い場面でどう判断するか」を測る設計で、Council が実際に扱っている問題（SPEC 矛盾・トレードオフ）に最も近い

### 結論

**Council を丸ごと当てはめられる既製ベンチマークは無い。** 理由は対象の性質で、上記いずれも**正解が外部に定義できる問題**を扱うのに対し、Council が扱うのは「この repo でこの設計判断が妥当か」という**正解が事後にしか現れない問題**だからである。

したがって現実的な取り方は 2 つ:

1. **借りられるのは指標であって課題ではない** — Brier / skill score / AUC / ECE / κ という較正の道具立ては層 1 からそのまま借りられる。本計測が既に借りている
2. **課題は自分で作るしかない** — §5 の提案 1（`minority_opinion` の再諮問約束を機械可読にする）は、**自前のベンチマークを蓄積する仕掛け**そのものである。「Wave N 末に条件 X なら再諮問」は予測であり、その検証結果は正解ラベルになる。67 発動で 8 件以上の予測が既に書かれているのに回収されていない — **ベンチマークの材料は生成済みで、回収経路だけが無い**

参考文献:

- [Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias](https://arxiv.org/html/2606.19544v1)
- [Overconfidence in LLM-as-a-Judge: Diagnosis and Confidence-Driven Solution](https://arxiv.org/pdf/2508.06225)
- [Benchmarking LLM-as-a-Judge for Long-Form Output Evaluation](https://arxiv.org/html/2606.01629v1)
- [12 Angry AI Agents: Evaluating Multi-Agent LLM Decision-Making Through Cinematic Jury Deliberation](https://arxiv.org/pdf/2605.01986)
- [LLM Agents for Deliberative Collaboration: A Study on Joint Decision Making Under Partial Observability](https://arxiv.org/html/2607.06157v1)
- [Budgeted Act-or-Defer Multi-Agent LLM Deliberation with Local Reliability Bounds](https://arxiv.org/pdf/2606.29654)
- [DRIP-R: A Benchmark for Decision-Making and Reasoning Under Real-World Policy Ambiguity in the Retail Domain](https://arxiv.org/pdf/2605.07699)
- [CalibraEval: Calibrating Prediction Distribution to Mitigate Selection Bias in LLMs-as-Judges](https://arxiv.org/pdf/2410.15393)
- [Awesome-LLMs-as-Judges（サーベイのリンク集）](https://github.com/CSHaitao/Awesome-LLMs-as-Judges)

---

## 7. 再現手順

```
python3 scripts/council-performance.py           # 本文書の全数値
python3 scripts/council-performance.py --json    # 機械可読
python3 scripts/test-council-performance.py      # 回帰テスト（55 checks）
```

本計測は集計のみで **LLM 判定を一切含まない**（axis-audit と同じ設計制約 — 死角を持つ者に死角の有無を尋ねない）。終了コードは常に 0（warn のみ・block しない、philosophy.md 第 6 条 人間最終承認）。
