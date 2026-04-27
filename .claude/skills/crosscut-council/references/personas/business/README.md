# Business Council Personas

事業 Council の 3 ペルソナ：経営者 / 開発者 / 哲学者。

## ファイル構成

| ファイル | Persona | Temperature | 特徴 |
|---------|---------|-------------|------|
| [ceo.md](ceo.md) | 経営者 | 0.3 | 利益追求、収束的、慎重 |
| [dev.md](dev.md) | 開発者 | 0.2 | ロジカルシンキング、決定論的、厳密 |
| [phil.md](phil.md) | 哲学者 | 0.7 | アウフヘーベン、発散的、創造的 |

各ファイルは Persona の system prompt + Few-shot 例で構成される。
Orchestrator は本ファイル群を読み込んで Persona LLM 呼び出しを構成する。

## Few-shot 例の収集方針

### PR1 段階: AI が draft する

実運用ログがまだ存在しないため、PR1 では各 Persona に **AI draft の Few-shot 例を 3 件**埋め込む。
draft の作成方針：

- philosophy.md（dialog-harness 5 条憲法）と council-philosophy.md（Council 6 公理）から、その Persona が立場として強調しそうな論点を抽出
- 「対立場面で stance を取る」例を 1 件
- 「全会一致場面で多様性を示す」例を 1 件
- 「confidence 低めで保留する」例を 1 件

### PR2 段階: 実 COUNCIL-LOG から 3 件追加

実運用 10 件以上の COUNCIL-LOG が貯まった時点で、各 Persona の優れた発言例を 3 件抽出して追加。
draft 例は保持し、Few-shot は合計 6 件構成にする（多様性確保）。

### PR3 段階: 質的評価ラウンド

F2（月次儀式）で各 Persona の Few-shot 例を見直し：

- 重複している例を統合
- 意図と異なる stance を取る例を差し替え
- 古い Few-shot を archive へ移動

## Few-shot 例のフォーマット

各 Persona ファイル内で：

```markdown
## Few-shot 例

### 例 1: 対立場面（PR1: AI draft / PR2 以降: 実ログ抽出）

**入力**:
- context: ...
- options: [案A, 案B]
- question_to_answer: ...

**出力**:
```json
{
  "persona": "...",
  "stance": "案A",
  "reason": "...",
  "confidence": 0.7,
  "dimension": "ROI",
  "premise": "短期 6 ヶ月の事業判断として",
  "concerns": ["..."]
}
```
```

## 視点の独立性に関する重要事項

各 Persona は **Phase 1 では他 Persona の出力を見ない**（情報純度原則、council-philosophy.md §1）。
Few-shot 例も**他 Persona に言及しない**形式で記述する：

- ✅ OK: 「経営者として ROI を重視し、案A を推奨」
- ❌ NG: 「開発者は技術的に案B を推すだろうが、経営者として ROI を重視し案A を推奨」

他 Persona への言及は Phase 2 討論（PR2 で実装）でのみ許可される。

## モデル独立性

ブリーフ §5.1 の通り、視点の独立性を優先しモデルの独立性は求めない。
3 Persona は同一 LLM の異なる人格づけで実装する（人間が立場によって性格が変わるのと同じ）。
モデル切り替えは将来の拡張余地として保留（PR3 以降の検討事項）。
