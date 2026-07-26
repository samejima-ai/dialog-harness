# Conflict Typology — 対立類型（PR1: スタブ ＋ 類型 B 実装済み）

3 Persona の発言から対立構造を分類し、適切な対応を導く。

> **ステータス**: 類型 A-G を**定義**する。判定は現在 **3 値**（`unanimous` / `reason_divergence` / `simple_conflict`）。
> `reason_divergence`（類型 B）は v6.7.0 で `unanimous` から**分離**した（§類型 B の分離 参照）。
> 残る類型 A/C/D/E/F/G の完全判定は PR2 で実装する。

## 対立類型一覧

| 類型 | 定義 | 対応 | 現在の動作 |
|------|------|------|---------|
| A. 結論対立 | `stance` が割れる | Phase 2 反駁 → Phase 3 | simple_conflict として Phase 3 直行 |
| B. 理由対立 | 結論同じ、`reason` 違う | 対立ではない、Phase 3 で多様性として構造化 | **`reason_divergence` として分離（v6.7.0 実装済み）** |
| C. 確信度対立 | `confidence` に大差 | Phase 2 質問 → Phase 3 | simple_conflict として Phase 3 直行 |
| D. 次元ずれ | `dimension` がバラバラ | Phase 3 で客観的に多次元分離 | simple_conflict として Phase 3 直行 |
| E. 前提対立 | `premise` が揃っていない | Phase 0 差し戻し + 人間献上 | simple_conflict として Phase 3 直行（PR2 で正規化） |
| F. 時間軸対立 | 短期 vs 長期 | Phase 3 で時間軸を分けて判定 | simple_conflict として Phase 3 直行 |
| G. メタ対立 | 問い自体が疑われる | 人間エスカレーション + 何があったかを報告 | simple_conflict として Phase 3 直行（PR2 で正規化） |

## 類型 B の分離（v6.7.0・D5 決定「C1' は分離して別物として扱う」）

### なぜ分離するか

PR1 は類型 B を `unanimous` として処理していた。しかし実測（`delivery/ANALYSIS-council-axis-independence-2026-07-26.md`）で
**`stance` が一致した判定でも観測次元は完全に分離していた**ことが判明した
（軸ペアの `dimension` 語彙の Jaccard は 25/25 で 0.000、3 軸の共有トークンは 0 件）。
すなわち **類型 B は例外ではなく主要形態**であり、`unanimous` に潰すと
「何が独立に支持されたか」が記録から消える。

さらに重要なのは、**現行の扱いが逆になっていた**ことである。

| | 現行（v6.6.0 まで） | 是正後（v6.7.0） |
|---|---|---|
| 「多様性（プルラリティ）として質を評価し confidence を高くする」対象 | `unanimous`（次元が同じか違うかを問わない） | **`reason_divergence` のみ** |
| 同一次元での一致 | 同じく高 confidence | **被覆不足の疑いとして confidence を引き下げる** |

3 軸が**同じ物差しで**同じ答えを出したなら、それは多様性ではなく**観測の重複**である。
逆に**独立した次元から**同じ結論に達したなら、それは 3 つの独立した支持であり最も強い推奨根拠になる。
この区別は `council-philosophy.md` 第2条の系「全会一致は被覆不足の可能性も同時に疑う」の実装であり、
分離しなければ実装できない。

### 判定ロジック（決定論・v6.7.0）

#### 前提: stance の正規化（v6.7.0 で明文化）

**`stance` の完全一致で比較してはならない。** 実運用では各軸が同じ選択肢を指しつつ
自分の条件を付記する（実例: `council-2026-07-01T13:04:40Z-ctlrec1` は 3 軸すべてが
案A を支持しながら `案A（同期＋事後評価運用の確立を条件）` / `案A（category→decision_category 導出せず null 埋め）` /
`案A（decision_category は機械導出せず未分類保持）` と記録された）。
完全一致で比較すると、これらが `simple_conflict` になり分類が実態から乖離する
（`scripts/council-axis-audit.py` B6 の実測で **32 件中 11 件**がこの乖離だった）。

正規化は `options` への**双方向の接頭辞一致**で行う。これは
`recommended` と `max_score_stance` の接頭辞一致検証（[judgment-agent.md](judgment-agent.md)）と
同型の既存イディオムであり、新しい判定原理を導入しない。

```python
def normalize_stance(stance, options):
    """stance を options のいずれかへ正規化する。決定論。

    - stance が option で始まる、または option が stance で始まるなら一致とみなす
    - 複数一致する場合は**最長の option** を採る（"案A" と "案A: 詳細" の両方があるケース）
    - どの option にも一致しなければ stance をそのまま返す（options 外 stance ＝ 第3の道）
    """
    matched = [o for o in options if stance.startswith(o) or o.startswith(stance)]
    return max(matched, key=len) if matched else stance
```

#### 分類本体

```python
# dimension トークン化は scripts/council-axis-audit.py と同一規則（`/` `／` 区切り・完全一致）
DIMENSION_OVERLAP_MAX = 0.30   # 同 script の DIMENSION_JACCARD_MAX と同値

def classify_conflict(persona_outputs, options):
    """conflict_type を決定論で導く。LLM 判定は禁止（§決定論性）。

    Returns: "unanimous" | "reason_divergence" | "simple_conflict"
    """
    stances = [normalize_stance(p["stance"], options) for p in persona_outputs]
    if len(set(stances)) != 1:
        return "simple_conflict"

    # 以降は stance 全一致。観測次元が分離しているかで 2 分する
    dims = [p.get("dimension") for p in persona_outputs]
    if any(not d for d in dims):
        # dimension 欠落時は判定不能 → 保守的に unanimous
        # （output-format.md §8 で dimension は必須。欠落は記録側の不備）
        return "unanimous"

    def toks(s):
        return {t.strip() for t in re.split(r"[/／]", s) if t.strip()}

    for a, b in itertools.combinations(dims, 2):
        ta, tb = toks(a), toks(b)
        if not (ta or tb):
            continue
        jaccard = len(ta & tb) / len(ta | tb)
        if jaccard > DIMENSION_OVERLAP_MAX:
            # どこか 1 ペアでも次元が重なっていれば「独立な支持」とは言えない
            return "unanimous"
    return "reason_divergence"
```

**しきい値を `council-axis-audit.py` と共有する理由**: 同じ現象（次元の重複）を
2 箇所で別の基準で判定すると、監査が「冗長なし」と言う一方で分類器が `unanimous` を出す等の
不整合が生じる。閾値を変えるときは**両方を同時に**変える（同 script の B6 が不一致を検出する）。

> **監査側は正規化できない**: `options` は COUNCIL-LOG に記録されていないため、
> `council-axis-audit.py` は `normalize_stance` を再現できない。したがって同 script の B6 は
> 「閾値ずれ」と「正規化ギャップ」を**別の診断として分けて報告する**。
> `options` を §8 に記録すれば監査側も正規化できるようになる
> （[output-format.md](output-format.md) §8 で optional field として追加済み）。

### 既存エントリの扱い

**再解釈しない。** COUNCIL-LOG は append-only であり、既存の `unanimous` 24 件は
当時の規格での記録として保持する。本分類は**v6.7.0 以降の新規発動から適用**する。
過去分の類型 B 実態を知りたい場合は `scripts/council-axis-audit.py` の
dimension Jaccard を見る（記録を書き換えずに観測できる）。

## PR2 以降に残る判定

`premise` / `confidence` 差による類型 C/D/E/F/G の判定は PR2 で実装する。
データ（`reason` / `confidence` / `dimension` / `premise`）は PR1 から取り続けている。

## 第3の道 stance の PR1 暫定運用ルール

Persona（特に哲学者）が `options` 外の自由記述 stance（「第3の道」「前提自体への保留」「自由記述」等）を
返した場合の取り扱い。COUNCIL-LOG `council-2026-04-29T18-00-00Z-d1m4n5` で Judgment Agent が
哲学者の「第3の道（実質 A）」を任意の options に按分加算した事象を契機に、PR1 で以下の暫定ルールに固定する。

### ルール

1. **weight 加算対象外**: options 外 stance には weight を加算しない
2. **退避先**: `weight_calculation.third_way_excluded` に persona / stance / weight / confidence / reason を構造化記録（[output-format.md](../references/output-format.md) §4）
3. **`minority_opinion` への転載**: 退避された意見は必ず `minority_opinion` 末尾に「【options 外 stance】<persona>: <stance>（理由: ...）」形式で転載する
4. **`conflict_type` への影響なし**: PR1 簡略判定（`stance` 完全一致のみ `unanimous`）に third_way の有無は影響しない。third_way が混ざる時は `simple_conflict` として処理
5. **`judgment_confidence` への影響**: `third_way_excluded` の weight 合計が全 weight の 30% 以上を占める場合、`judgment_confidence` は 0.5 以下が妥当（[judgment-agent.md](judgment-agent.md) §judgment_confidence の算出指針）

### 設計意図

Judgment Agent の weight 分割裁量を構造的に排除する（哲学違反の予防）。
第3の道を「上澄み」として保存しつつ、weight 計算は純粋関数で再現可能に保つ。
意味的寄せを LLM 判定に委ねる従前の挙動は、d1m4n5 で実証された通り
recommended の捏造を許してしまう。PR1 では退避一択とする。

### PR2 移行パス

PR2 で対立類型 A-G を完全実装する際、`weight_calculation.third_way_excluded` に蓄積されたデータから
新類型 `third_way` を導入できる。判定ロジック候補（PR2 で決着）:

- (a) `third_way` 単独で新類型化し、Judgment Agent が「止揚案」として再構成
- (b) options に含まれる stance への意味的寄せを LLM 判定で行う（d1m4n5 の轍を踏まないよう
  接頭辞一致検証等の構造的安全弁を併設すること）
- (c) PR1 暫定ルール（weight 加算対象外）を継続し `minority_opinion` で扱う

PR2 開発時は PR1 期間中の `third_way_excluded` ログ分布を集計して判断する。

## PR2 完全版の予告

### 判定優先順位（PR2）

```
1. premise が揃っていない → E（差し戻し + 人間献上）
2. 問い自体への疑問が含まれる → G（人間エスカレーション）
3. dimension がバラバラ → D（多次元分離）
4. stance が割れる
   ├ confidence 差が大きい（max - min > 0.4）→ C（質問形式）
   └ それ以外 → A（反駁形式）
5. stance 一致 + reason 多様 → B（多様性として評価）
6. stance 一致 + reason 一致 → unanimous
```

### 各類型の対応詳細（PR2 実装時）

#### A. 結論対立 → Phase 2 反駁形式

対立する Persona に**反論**を書かせる：

- 例: 経営者「案A」、開発者「案B」、哲学者「案A」
- 開発者に「案A 派の主張に対する反論を 200 字以内で」依頼
- 経営者・哲学者に「案B 派の主張に対する反論を 200 字以内で」依頼
- 各反論は他 Persona の **stance のみ**見せる（reason / concerns は見せない、`council-philosophy.md` 解釈 B）

#### C. 確信度対立 → Phase 2 質問形式

確信度低い Persona から高い Persona へ**質問**：

- 例: 経営者 confidence 0.4、開発者 confidence 0.9
- 経営者から開発者へ「あなたの高い確信度の根拠を 1 つ教えてください」
- 質問と応答のみを Phase 3 入力に追加

#### D. 次元ずれ → 多次元分離

各 Persona が異なる評価軸を使っている場合、Judgment Agent が `reasoning` で**次元ごとに分離して評価**：

```
"reasoning": "経営者は ROI 軸で案A、開発者は保守性軸で案B、哲学者は意味軸で案A を支持。
ROI と意味軸の合計重みが保守性軸を上回るため、案A を推奨"
```

#### E. 前提対立 → 差し戻し + 人間献上

`premise` が根本的に異なる場合、Council 内では合意不可能。

- 発動要請を **Phase 0 に差し戻し**
- 同時に人間に「前提が揃っていない」を献上
- 人間が前提を統一してから再発動

#### F. 時間軸対立 → 時間軸分離

短期と長期で意見が分かれる場合、Judgment Agent が **時間軸ごとに分けて推奨**：

```
"recommended": "短期: 案A（ROI 優先）、長期: 案B（保守性優先）。
段階的移行を推奨"
```

#### G. メタ対立 → 人間エスカレーション

Persona の発言中に「この問い自体が誤っている」「options が不適切」等のメタ的疑義が含まれる場合：

- Phase 3 を実行せず人間エスカレーション
- COUNCIL-LOG に「メタ対立検出」と Persona 発言の該当箇所を記録

## stance 一致時の扱い（v6.7.0 で 2 分）

| conflict_type | 意味 | Judgment Agent の扱い |
|---|---|---|
| `reason_divergence`（類型 B） | 独立した次元から同一結論 ＝ **真の多様性** | 多様性として質を評価。各次元がどう満たされたかを `reasoning` に列挙。confidence は高め |
| `unanimous`（次元も一致） | 同じ物差しで同じ答え ＝ **観測の重複の疑い** | 被覆不足を疑う。重複した次元を明示し、`concerns` から未被覆の観点を拾う。confidence は引き下げ |

詳細は [judgment-agent.md](judgment-agent.md) §stance 一致時の扱い 参照。

## 対立類型判定の主体

対立類型の判定主体は**発言側の各 Persona**である（`council-philosophy.md` §3 認識合わせと合意の分離）。

- Persona の発言を集約して対立構造を整理するのが対立類型判定の役割
- ここでの「認識合わせ」は Persona 間の認識構造の整理
- 合意ではない（合意は実装者と Council の間で行われる）

## 決定論性

対立類型判定は**決定論**で実装する（`philosophy.md` §2 Shift Left 原則）。
Persona 出力の構造化フィールド（`stance` / `confidence` / `dimension` / `premise`）から純粋関数で類型を導出する。
LLM による判定は禁止する。

## PR1 でのデータ収集

PR1 では類型判定はしないが、後続 PR で類型分析できるよう、COUNCIL-LOG に以下を記録する：

- 各 Persona の `stance` / `confidence` / `dimension` / `premise`
- conflict_type（unanimous / reason_divergence / simple_conflict）
- `weight_calculation.third_way_excluded`（PR1 新規、third_way 類型移行のための分布データ）
- `weight_calculation_retry_count`（決定論検算リトライ回数、Judgment Agent の規定逸脱頻度の指標）

PR2 開発時に過去の COUNCIL-LOG を分析し、類型分布を実データで検証する。
