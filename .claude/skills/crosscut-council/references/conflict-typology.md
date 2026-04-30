# Conflict Typology — 対立類型（PR1: スタブ）

3 Persona の発言から対立構造を分類し、適切な対応を導く。

> **PR1 ステータス**: スタブ。本ファイルでは類型 A-G を**定義**するが、PR1 では `unanimous` と `simple_conflict` の 2 値のみ判定する。完全な類型判定は PR2 で実装する。

## 対立類型一覧

| 類型 | 定義 | 対応 | PR1 動作 |
|------|------|------|---------|
| A. 結論対立 | `stance` が割れる | Phase 2 反駁 → Phase 3 | simple_conflict として Phase 3 直行 |
| B. 理由対立 | 結論同じ、`reason` 違う | 対立ではない、Phase 3 で多様性として構造化 | unanimous として処理 |
| C. 確信度対立 | `confidence` に大差 | Phase 2 質問 → Phase 3 | simple_conflict として Phase 3 直行 |
| D. 次元ずれ | `dimension` がバラバラ | Phase 3 で客観的に多次元分離 | simple_conflict として Phase 3 直行 |
| E. 前提対立 | `premise` が揃っていない | Phase 0 差し戻し + 人間献上 | simple_conflict として Phase 3 直行（PR2 で正規化） |
| F. 時間軸対立 | 短期 vs 長期 | Phase 3 で時間軸を分けて判定 | simple_conflict として Phase 3 直行 |
| G. メタ対立 | 問い自体が疑われる | 人間エスカレーション + 何があったかを報告 | simple_conflict として Phase 3 直行（PR2 で正規化） |

## PR1 の簡略判定ロジック

```
def classify_conflict(persona_outputs):
    stances = [p.stance for p in persona_outputs]
    if len(set(stances)) == 1:
        return "unanimous"
    else:
        return "simple_conflict"
```

`reason` / `confidence` / `dimension` / `premise` は記録するが PR1 では判定に使わない。
PR2 で完全類型判定に拡張する際、過去の COUNCIL-LOG エントリから類型分布を分析できるよう、データは取り続ける。

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

## 全会一致時の扱い

`conflict_type = "unanimous"`（PR1）または類型 B（PR2）の場合、Judgment Agent は**多様性として質を評価**する。
詳細は [judgment-agent.md](judgment-agent.md) §全会一致時の扱い 参照。

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
- conflict_type（unanimous / simple_conflict）
- `weight_calculation.third_way_excluded`（PR1 新規、third_way 類型移行のための分布データ）
- `weight_calculation_retry_count`（決定論検算リトライ回数、Judgment Agent の規定逸脱頻度の指標）

PR2 開発時に過去の COUNCIL-LOG を分析し、類型分布を実データで検証する。
