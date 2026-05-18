# Consensus Protocol — 実装者と Council の合意プロセス

Judgment Agent 出力を受け取った実装者が、その判断に対して合意して方針を決定するプロトコル。

## 重要な前提

**Judgment Agent の出力は判断（judgment）であって決定（decision）ではない**。
決定は実装者が合意プロセスを経て確立する。
詳細は [council-philosophy.md](council-philosophy.md) §3 認識合わせと合意の分離 を参照。

## 合意の定義

> 合意 = 判断者の出力に対して実装者が理解と質問をして方針が決まること

認識合わせと合意は異なる：

- **認識合わせ**: 発言側の主観を擦り合せる（Persona 間、人間⇄AI）
- **合意**: 判断者の出力を実装者が受け取って方針化する（Council 出力 → 実装者）

## プロトコル

```
[Judgment Agent 出力受領]
        ↓
[Step 1] 実装者が出力全体を読む
        - recommended / reasoning / minority_opinion / weight_note / judgment_confidence
        - judgment_confidence < 0.5 → 即座に人間エスカレーションへ
        ↓
[Step 2] 実装者が理解する
        - reasoning が論理整合しているか
        - minority_opinion を実装に反映できる箇所はないか
        - weight_note の重み配分がカテゴリと整合しているか
        ↓
[Step 3] 必要なら追加質問（最大 2 往復）
        ↓ （質問あり）           ↓ （質問なし）
[Step 4a] Council に追加質問     [Step 5] 方針決定 = 合意成立
        ↓                              ↓
[Step 4b] Council が delta 応答  [Step 6] 実装に反映
        ↓                              ↓
        Step 3 に戻る              [Step 7] COUNCIL-LOG に
        （3 回目で Step 8 へ）          implementer_consent を後追記
                                       ↓
                                       完了

[Step 8] 合意できない / 質問 3 回到達 → 人間に献上（保留）
```

## Step 1: 出力受領

実装者は Judgment Agent 出力を受領する。出力スキーマは [output-format.md](output-format.md) §4 Judgment Agent 出力 を参照。

`judgment_confidence < 0.5` の場合、Council 自体が自信を持っていない。
合意プロセスを実行せず、即座に人間エスカレーションする（Step 8 へ）。

## Step 2: 理解

実装者は以下を確認する：

- **論理整合性**: `reasoning` が `recommended` をサポートしているか
- **重み妥当性**: `weight_note` のカテゴリが今回の発動に適切か
- **少数意見の扱い**: `minority_opinion` を実装で部分的に反映できないか（例: 採用案 + 少数意見の懸念点を mitigations として実装）

## Step 3: 追加質問の判断

理解できない / 不足を感じる場合のみ追加質問する。
追加質問が**ない場合**は Step 5（方針決定）に進む。

質問の例：

- 「reasoning で言及された『短期 ROI』は具体的にどの指標か」
- 「minority_opinion の哲学者の懸念点は、案 B の実装で mitigation 可能か」
- 「weight_note の implementation カテゴリ適用は妥当か。本件は judgment カテゴリのほうが適切では」

## Step 4: 追加質問プロトコル

### 入力フォーマット

```json
{
  "type": "follow_up_question",
  "original_invocation_id": "council-2026-04-21T15:30:00Z-a1b2c3",
  "additional_question": "minority_opinion の懸念点は案 B の実装で mitigation 可能か",
  "current_understanding": "案 B 採用、ただし哲学者の懸念点を CHANGELOG に明記する方針"
}
```

### 応答（Judgment Agent）

Judgment Agent は **delta（差分）のみ**を返す（再判定はしない）：

```json
{
  "type": "follow_up_response",
  "original_invocation_id": "council-2026-04-21T15:30:00Z-a1b2c3",
  "delta_response": "案 B 採用時の哲学者懸念点（意味付けの希薄化）は、CHANGELOG への記載で部分 mitigation 可能。完全 mitigation には INTENT.md への明示記録が必要",
  "updates_to_judgment": null  // 元の judgment は変更しない
}
```

### 制約

- **最大 2 往復**（合計 3 回目の質問で Step 8 強制エスカレーション）
- 各質問はコンテキスト全体を再送せず、`original_invocation_id` で参照する（コスト削減）
- Judgment Agent は元の judgment を**書き換えない**。delta だけ返す

### なぜ delta のみか

完全な再判定は新規発動と同等のコスト。少数の追加質問は元判定への補足として処理することで、合意プロセスを軽量に保つ（`philosophy.md` §3 情報純度・コスト）。

## Step 5-7: 合意成立

実装者が方針を決定したら：

1. 方針を明示（コミットメッセージ・実装メモ等で記録）
2. 実装に反映
3. COUNCIL-LOG の該当エントリに `implementer_consent` を後追記
   - `implementer_consent`: `"agreed_recommended"` / `"agreed_with_modification"` / `"escalated"` のいずれか

`agreed_with_modification` の例: 推奨案を採用したが、minority_opinion を mitigation として追加実装した場合。

## Step 8: 合意できない場合

以下の場合は人間に献上する（実装者は独自判断で進めない）：

- `judgment_confidence < 0.5`（Council 自体が自信を持っていない）
- 追加質問が 3 回目に到達
- 実装者が論理整合性に納得できない
- 実装者が重み配分の妥当性に納得できない
- minority_opinion が実装で fundamental な問題を提起している
- Orchestrator の決定論検算（`verify_weight_calculation`、[orchestrator.md](orchestrator.md) §決定論検算プロトコル）が **2 回連続不一致**（COUNCIL-LOG の `weight_calculation_retry_count = 2`、`status = judgment_failed`）
- `weight_calculation.tie_break_applied = true` かつ `judgment_confidence ≥ 0.4`（同点処理で Judgment Agent が高 confidence を出した不整合）

献上時の記録：

- COUNCIL-LOG: `implementer_consent: "escalated"` + `human_escalated: true`
- DELIVERY.md（LC ≥ 1 環境では）: 該当 invocation_id と escalation 理由を記録
- `judgment_failed`（検算不一致）の場合: `escalation_reason` に「weight_calculation 検算 2 回不一致: <verify_weight_calculation の reason>」を記録（PR1 新規）

### エッジケース: escalated 経路での合意成立（v5.5.0 adrv01-Ph1 で明文化）

`judgment_confidence < 0.5` で escalation が発火した後、人間（実装者）が献上を受けて合意内容を回答した場合、protocol 上の `implementer_consent` は **`"escalated"` を維持し、合意内容は `escalation_reason` に記録する**。`agreed_with_modification` を採用してはならない（後者は escalation を経由しない経路のための値）。

**正しい記録パターン**:

```yaml
implementer_consent: "escalated"
human_escalated: true
escalation_reason: "judgment_confidence 0.45 < 0.5 + third_way_excluded weight 比率 45% > 30% の二重トリガーで escalation 経路。人間は recommended（V-1）を採用しつつ哲学者の第3の道を併用する止揚案で合意（β）。記録のみ、判定は人間が引き受け"
follow_up_questions_count: 0
agreed_at: "..."
```

`escalated` を維持する理由:

- protocol §Step 8 の値域は 3 値択一であり、escalated は escalated のまま記録するのが schema-strict（`output-format.md` §8 COUNCIL-LOG エントリのフィールド定義）
- 後付けで実装者が合意したとしても、**Council 自体は自信を持っていなかった**事実は不変（`judgment_confidence < 0.5` の歴史的記録を尊重）
- 振り返り儀式（PR3 の F1）で「どのカテゴリで escalation が多いか」「escalation 経路の合意品質」を分析する際、`agreed_with_modification` で塗りつぶすと escalation の頻度が見えなくなる

**根本原因への対処**:

escalation の多くは `category` 誤選択（特に scope/PR 境界判断を `conception` と分類）が哲学者重みを過剰にして連鎖する構造（COUNCIL-LOG `vrfy01` の事例）。本エッジケースを記録する場合は、同時に [pre-check.md](pre-check.md) §scope/PR 境界 vs 新規思想 の判別シナリオ で再発防止のフィードバックを行う。

### 自己申告 → Council 起動の hook 経路（v5.6.0 Ph2 で本実装）

実装者の自己 confidence < 0.6 自己評価から Council 起動までの経路は v5.5.0 adrv01-Ph1 で **明文化のみ**（[crosscut-council/SKILL.md](../SKILL.md) §自己申告プロトコル）。v5.6.0 adrv01-Ph2 で以下を本実装する予定：

- `crosscut-feedback-loop` への自己申告イベント還流ルートの新設
- `~/.claude/council-data/stats.json` への自己申告イベントスキーマ拡張
- 独立観測機構（harness-verifier 同型の新規 crosscut-* skill）による自己申告事実の事後検証

v5.5.0 段階では本節は先行宣言。実装は v5.6.0 まで延期する（philosophy.md §5 献上哲学と adrv01 の段階的組み込みで止揚パターンに整合）。

### なぜ独自判断で進めないか

実装者が Council 判断を無視して独自実装することは `philosophy.md` §5 献上哲学に反する。
Council は実装者の支援機構であり、合意できない場合の正しい応答は「保留して人間に献上」である。
これは `council-philosophy.md` §5 実装者への信頼 とも整合する（実装者は優秀だからこそ、自分の限界を認識して人間に判断を仰ぐ）。

## 合意プロセスのログ化

COUNCIL-LOG への追記項目（合意プロセス完了時）：

```yaml
implementer_consent: agreed_recommended | agreed_with_modification | escalated
follow_up_questions_count: 0-3
agreed_at: 2026-04-21T15:35:00Z
modification_note: "..." # agreed_with_modification の場合のみ
escalation_reason: "..." # escalated の場合のみ
```

## PR1 での簡略化

- 追加質問の delta 応答は最低限実装（Judgment Agent prompt に「delta のみ返す」を明記）
- COUNCIL-LOG への後追記は手動（PR3 で自動化）
- escalation 時の DELIVERY.md 連携は LC ≥ 1 環境でのみ

## PR2 以降の予告

- 追加質問の往復回数を動的に調整（confidence 高い時は 1 回まで）
- 合意プロセス自体のログ分析（どのカテゴリで escalation が多いか）
- 実装者の confidence 自己評価ツール（チェックリスト形式）

## PR2 で決着させる未決事項: `consensus_mode` フラグの導入

### 問題

PR1 実装後の実運用で、Claude（実装者エージェント）が Council 判定を受領した後、**「選択肢を再提示してユーザーに選ばせる」** というデフォルト質問パターンを合意プロセスに上書きしてしまう事例が発生した（COUNCIL-LOG `council-2026-04-21T15:30:00Z-m4t4q1` のメタ反復後の挙動）。

これは Council の judgment（confidence 0.85、全会一致）を「また選択肢リスト」に降格させ、Council の価値を構造的に薄める問題。個々の AI エージェントの「気をつけ」に依存すると同じ失敗が繰り返されるため、**Council 出力側に構造として埋め込む**のが正しい。

### 提案: Judgment Agent 出力に `consensus_mode` フィールド追加（2 モードのみ）

```json
{
  "recommended": "...",
  "judgment_confidence": 0.85,
  "consensus_mode": "auto_agree" | "escalate_to_human",
  "final_decision": null
}
```

| モード | 受信側 AI の挙動 | 典型場面 |
| --- | --- | --- |
| `auto_agree` | 実装者として即同意 → そのまま実行。人間には事後報告のみ | カテゴリ別 confidence 閾値を超えた判定 |
| `escalate_to_human` | 実装者は判断せず、人間に完全献上（DELIVERY.md 経由） | 閾値未達 / life Council / 対立類型 E・G |

### なぜ 2 モードのみか（中間 `confirm_with_human` を排除した根拠）

初期設計では `auto_agree` / `confirm_with_human` / `escalate_to_human` の 3 モードを検討したが、中間の `confirm_with_human`（yes/no ダイアログ）は以下の理由で不採用：

1. **dialog-harness の「人間介入 0 を理想」とする核心思想と衝突**。中途半端な yes/no 介入は philosophy 違反
2. **L1 autonomous-dev の「開発中に人間に質問しない」原則と矛盾**（`layer1-autonomous-dev/SKILL.md`）
3. **献上哲学（`philosophy.md` §5）が既に正しい逃げ道を規定済み**。confidence 不足時は DELIVERY.md 経由で人間にまとまった形で渡すのが正解。yes/no はこの哲学の劣化版
4. **コスパ観点**: 3 Persona × Judgment Agent の全工程を回した結果が yes/no では、計算量に対するアウトプット価値が釣り合わない
5. **グレーゾーンは存在させない**: 「自動進行 or 献上」の二値に閉じることで、受信側の分岐ロジックが単純化され自律駆動を阻害しない

### 導出ロジック（決定論）

`consensus_mode` は Judgment Agent の LLM ではなく **Orchestrator が決定論で計算**する（`philosophy.md` §2 Shift Left）。このメタ判断自体が LLM で揺れると Council 全体の信頼性が崩れるため、ルール表で固定する：

```python
def compute_consensus_mode(council_type, category, decision_category, confidence, conflict_type, ctl, stats):
    """
    Args:
        council_type: "business" or "life"
        category: 重み配分カテゴリ ("operation" / "judgment" / "conception" / "implementation" 等)。
                  既存の Council 内部分類で、threshold 計算と重み補正に使用。
                  pre-check.md / output-format.md COUNCIL-LOG エントリの category と同義。
        decision_category: 第 6 条の判断委譲カテゴリ ("H1"-"H4" / "C1"-"C4")。
                           v4.2 新規。H カテゴリ即時献上 / CTL stats lookup に使用。
                           category と直交する概念（philosophy.md 第 6 条）。
        confidence: Judgment Agent の judgment_confidence (0.0〜1.0)
        conflict_type: "A" / "C" / "E" / "G" 等
        ctl: REGIME.md に記録された Council Trust Level（CTL-0〜CTL-3）
        stats: ~/.claude/council-data/stats.json から読み込まれた横断蓄積統計

    Returns:
        "auto_agree" or "escalate_to_human"
    """
    # ハードストップ: 献上確定
    if council_type == "life":
        return "escalate_to_human"
    if conflict_type in ["E", "G"]:  # 前提対立 / メタ対立（PR2 で実装）
        return "escalate_to_human"

    # H カテゴリ抵触検知時は即時献上（v4.2 新規 / philosophy.md 第6条）
    # H1 哲学変更 / H2 ルール変更 / H3 方向性発案 / H4 根本設計見直し
    if decision_category in ["H1", "H2", "H3", "H4"]:
        return "escalate_to_human"

    # weight category 別 confidence 閾値（既存運用カテゴリ）
    base_threshold = {
        "operation": 0.7,    # 不可逆操作は高い閾値
        "judgment": 0.6,     # スコープ・優先度・メタ判断
        "conception": 0.6,   # 新規構造・思想
    }.get(category, 0.5)     # 未定義カテゴリのみデフォルト 0.5

    # CTL 連動の閾値調整（v4.2 新規）
    # CTL-0: コールドスタート → 全件献上
    if ctl == "CTL-0":
        return "escalate_to_human"

    # CTL-1: decision_category 別実績で判定（該当カテゴリのみ自律）
    if ctl == "CTL-1":
        category_stats = stats.get("categories", {}).get(decision_category, {})
        if category_stats.get("count", 0) < 10:
            return "escalate_to_human"
        if category_stats.get("agreement_rate", 0) < 0.90:
            return "escalate_to_human"
        adjusted_threshold = base_threshold

    # CTL-2: 標準運用（既存閾値）
    elif ctl == "CTL-2":
        adjusted_threshold = base_threshold

    # CTL-3: 高度委譲（閾値を 0.1 緩和）
    elif ctl == "CTL-3":
        adjusted_threshold = base_threshold - 0.1

    else:
        # 未知の CTL は安全側に倒して献上
        return "escalate_to_human"

    if confidence < adjusted_threshold:
        return "escalate_to_human"
    return "auto_agree"
```

閾値設計の意図：**中間モードを置かない代わりに、高リスク・高不可逆性のカテゴリでは confidence 閾値自体を上げる**。これにより「Council が強い自信を持っている時のみ自動進行」が実現できる。閾値を超えなければ献上。超えれば AI が自律実行。

### category と decision_category の役割分担（v4.2 新規）

v4.2 では既存の `category`（重み配分・閾値計算用、operation/judgment/conception 等）と、
第 6 条で導入された `decision_category`（判断委譲用、H1-H4 / C1-C4）を**直交した別概念**として
扱う。両者は同じ判定で同時に使われる:

| 引数 | 用途 | 値の種類 | 由来ドキュメント |
|---|---|---|---|
| `category` | 重み配分・閾値選択 | `operation` / `judgment` / `conception` / `implementation` 等 | 既存 `pre-check.md` / `output-format.md` |
| `decision_category` | 判断委譲フィルタ | `H1`-`H4` / `C1`-`C4` | v4.2 `philosophy.md` 第 6 条 |

例: 不可逆操作の C3 カテゴリ判断であれば、`category="operation"`（閾値 0.7）+
`decision_category="C3"` の組で渡される。閾値は category で決まり、CTL stats lookup と
H 即時献上は decision_category で決まる。これにより既存の重み配分ロジックを保ったまま、
v4.2 の判断委譲フィルタを直交追加できる。

v4.2 で追加された CTL 連動は、横断蓄積データ（`~/.claude/council-data/stats.json`）から
決定論で算出された Council Trust Level に応じて、上記閾値を動的に調整する。
CTL-0（蓄積なし）では全件献上、CTL-3（高度委譲）では閾値を 0.1 緩和して自律性を高める。
H カテゴリ（哲学変更・ルール変更・方向性発案・根本設計見直し）は CTL に関わらず常に献上する
（philosophy.md 第 6 条 / `ctl-calculation.md` 参照）。

### 合意プロセスでやってはいけないパターン（PR2 で明文化）

- **選択肢の再提示**: Council が判定した後に「1: 案A / 2: 案B / 3: 保留」のような形で再度選ばせない。Council の judgment を advisory に降格させる
- **yes/no ダイアログでの事前確認**: 上記 2 モード設計の理由と同じ。`auto_agree` なら実行、`escalate_to_human` なら献上。中間形式は philosophy 違反
- **Council 判定の無視**: 実装者が独自実装で進める（`philosophy.md` §5 献上哲学違反）
- **合意プロセスの省略**: `auto_agree` モードでも、実装に反映した事実と `implementer_consent` の COUNCIL-LOG 追記は必須

### 決定論出力の副次的価値: 自律駆動のフック化

`consensus_mode` が決定論で出力され、かつ値が 2 種類に限定されることで、受信側は LLM 解釈を挟まずに挙動を分岐できる。最悪ケースではトリガーやフックで完全自動運用可能（`auto_agree` なら hook で即実行、`escalate_to_human` なら DELIVERY.md への自動追記 + 人間通知）。

自律駆動開発を断続的に継続する上で、この「決定論出力 → 機械可読な二値分岐」は重要な土台となる。

### 実装計画（PR2）

1. `output-format.md` §4 Judgment Agent 出力に `consensus_mode` フィールド追加（値は 2 種類のみ）
2. `orchestrator.md` に `compute_consensus_mode` 導出ルール表と計算式を追加
3. 本ファイルに「モード別の正しい合意形式」と「やってはいけないパターン」節を上記 memo 参照で追加
4. 受信側 skill（L1 / L0 / skill-creator 等）に `auto_agree` / `escalate_to_human` 分岐のテンプレ挙動を規定

---

## 人間可読並存規約（Council 諮問 `clrdbl` 採決、`agreed_recommended`）

### 背景

Council 判定の最終出力（`history/COUNCIL-LOG.md`）は schema 準拠の **YAML（machine-readable）** で記録される。これは harness-verifier / F1-F3 振り返り儀式 / council-weights 再校正等の **機械処理経路** には適しているが、人間が離席復帰時に「あの判定どんな議論だったか」と振り返るときの **判断スピード（philosophy 第 4 条 UX 代理指標）** には弱い。

本規約は YAML エントリと並存する **人間可読 markdown** の発行を義務化する。

### 配置

```
history/council-readable/<filename_id>.md
```

1 council = 1 markdown ファイル。`<filename_id>` は `<invocation_id>` から **time component の `:` を削除する変換** で導出する（**date 部分の `-` 区切りは温存** — full ISO 8601 basic format ではなく、time-only basic variant）:

| | date 部分 | time 部分 | 例 |
|---|---|---|---|
| `<invocation_id>` (YAML 識別子) | extended (`YYYY-MM-DD`) | extended (`THH:MM:SSZ`) | `council-2026-05-13T03:35:00Z-rtkSHA` |
| `<filename_id>` (ファイル名) | extended (`YYYY-MM-DD`) | basic (`THHMMSSZ`) | `council-2026-05-13T033500Z-rtkSHA` |

変換規則: `T(\d{2}):(\d{2}):(\d{2})Z` → `T\1\2\3Z` （`-` 区切りの date 部分には触れない）。`council-20260513T033500Z-...` のような full basic format は **採用しない**（PR #105 で rename 済みの実ファイル名と不一致）。

**論理 ID とファイル名の表現を分離する** 理由:

- **cross-platform 互換性**: Windows NTFS は `: \ / * ? " < > |` をファイル名に許可せず、`:` は Alternate Data Stream 区切りとして予約されている。ISO 8601 extended の `:` を含むファイル名は Windows クライアントで `git checkout` 不能となる（DH PR #105 で実害発生、council-readable 4 ファイルを basic format に rename）。
- **YAML 識別子は不変**: `invocation_id` は COUNCIL-LOG.md の YAML 正本上で履歴 ID として参照され続けるため、表現を ISO 8601 extended のまま固定する。本文中で council を引用する際も `invocation_id` を使う。ファイル名としての参照（`history/council-readable/<filename_id>.md` の path 表記）のみ上記変換規則を適用する。

cross-platform 規約は council-readable に限定せず、**本リポジトリで commit するすべての path** に適用する（`: \ / * ? " < > |` を含むファイル名を作成しない）。

**適用範囲**: DH PR #105 merge 時点の全 council-readable ファイル（4 件）を retroactive に rename 済み。本規約発動以降の council は最初から本変換規則に従って `<filename_id>` で作成する（downstream プロジェクトも同様 — §適用範囲 #downstream 参照）。

### 内容形式（4 section）

各 markdown は以下 4 セクションを **必ず** 含む（[philosophy.md](../../layer0-spec-architect/references/philosophy.md) 第 4 条 UX 代理指標 — 「クリック数 / 遷移深度 / 完了率」と同型に「**復帰判断スピード**」を最大化する構造）:

1. **議題** — 問いの背景（発動契機）+ 選択肢一覧
2. **発言** — 3 persona の `stance` / `confidence` / `dimension` / `reasoning`（独立記載、Phase 1 規格と整合）
3. **結果** — `conflict_type` / `final_weights` / `weight_calculation` 要約 / `judgment_confidence` / `recommended` / `minority_opinion` / `consensus_mode`
4. **選択** — 人間判断の選択肢 3 択（`agreed_recommended` / `agreed_with_modification` / `escalated`）+ 確定後の `implementer_consent` / `modification_note` / `agreed_at`

### 発行タイミング

- **draft**: Council Phase 3（Judgment Agent 出力確定）と並行して作成、人間判断点（`implementer_consent` 入力前）に提示する
- **確定**: `implementer_consent` 確定後、選択結果 / `modification_note`（該当時）/ `agreed_at` を追記して commit
- **同 commit 配置**: YAML エントリ（`history/COUNCIL-LOG.md`）と markdown（`history/council-readable/<filename_id>.md`）は **同一 commit** で配置し、内容 drift を防ぐ

### 適用範囲

本規約は **upstream (dialog-harness) で本規約を確立した PR (DH PR #96) の merge 時点の、次の council から適用**する。既存 council 群への遡及適用はしない（経営者 minority 採用、即時 ROI 観点 + 過去ログの append-only 規約と整合）。

ただし、本規約を **upstream で確立した PR (DH #96) 自身** では **2 件の retroactive 作成を例外的に許容** する:

1. 本規約のメタ council 自身（`clrdbl`）— 規約と同 commit で人間可読版を併合することで「規約変更 + 実例 1 件」が同 PR に揃い即時に効果検証可能
2. 本規約の起動契機となった council（`rtkSHA`）— 人間が「人間可読に整備された?」と問うた具体例

以降の PR では retroactive 作成を行わない（規約を本規約発動以降の council にのみ適用）。

#### Downstream プロジェクト (D3 sync 受領側) での扱い

本規約は dialog-harness (D4 マスタ) から cookpato / kakuman 等 (D3 配備) へ D3 sync で **byte-identical** に伝播する (council `d3d4b1` 規格 + DIMENSIONS.md §3.2)。**downstream プロジェクトでは本例外条項 (retroactive 2 件作成) は適用しない**:

- downstream は規約を「確立」ではなく「受領」する立場であり、`clrdbl` / `rtkSHA` の人間可読版は upstream DH project-scope に閉じている
- downstream 側の既存 council 群 (PR1 walking-skeleton 起源 + 利用者プロジェクト固有 council 等) も遡及作成しない
- downstream は **規約受領 PR の merge 後** に新規発動する council から本規約を適用する (本ドキュメント §配置 と同じく、リポジトリ root 直下の `history/council-readable/<filename_id>.md` を 4 section format で作成 — `<filename_id>` は §配置 の変換規則で `<invocation_id>` から導出する。`.claude/skills/crosscut-council/history/` 等の skill 内 prefix は誤り)

D3 = D4 byte-identical 不変性の維持を優先するため、downstream 側で本規約本文を modify することも禁止する。文言の改善は upstream DH 側で行い、D3 sync で全 downstream に伝播させる経路を保つ。

### 責務

- 起動側 skill（L1 / L0 / 他）: Council Phase 3 と同タイミングで markdown を draft
- 実装者: 人間判断点で markdown を提示、`implementer_consent` 確定後に追記 commit
- 受信側 skill: YAML をパースして機械処理経路、markdown を grep / open で人間振り返り経路

両経路は **責務分離**: YAML は機械可読の正本、markdown は presentation。drift 発生時は YAML を正とする。

### harness-verifier との関係

`harness-verifier/verify.py` の検査スコープは `.claude/skills/` 配下に限定されており、`history/council-readable/` は対象外（scope disjoint、`harness-verifier/BOUNDARY.md` §3 と整合）。本規約による追加検証コストはゼロ。

### 関連 council

- `council-2026-05-13T03:55:00Z-clrdbl` — 本規約の確立（メタ council、本規約 §4 結果に基づき `agreed_recommended`）
- `council-2026-05-13T03:35:00Z-rtkSHA` — 本規約の起動契機（PR #96、人間が「Council 最終出力は人間可読に整備された?」と問うた）
- `council-2026-04-21T15:30:00Z-m4t4q1`（kakuman / DH 共通履歴）— Council を Council に諮るメタ反復の先例

### 関連ドキュメント

- `output-format.md` §8 — COUNCIL-LOG YAML schema（本規約は schema を変更しない）
- `../../layer0-spec-architect/references/philosophy.md` 第 4 条 UX 代理指標 — 復帰判断スピードの位置づけ根拠
