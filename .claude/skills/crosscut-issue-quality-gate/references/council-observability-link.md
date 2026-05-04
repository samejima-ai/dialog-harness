# Council 観測性連携

本ドキュメントは crosscut-issue-quality-gate の軸 vi（観測性統一）が Council 入力データレイヤーの整合保証として機能する仕組みを定義する。

## 基本構造

### 因果関係

```
観測性規格のバラつき
    ↓
Council 3 ペルソナが同じ事実を見られない
    ↓
合議が成立しない
```

本 skill の軸 vi は **Council 判定の入力データレイヤー** 整合保証であり、philosophy.md 第 6 条「人間 ≒ Council」の実装上の前提条件として機能する。

### 観測対象の 2 階層

| 階層 | 観測対象 | 性質 | Council への影響 |
|---|---|---|---|
| **DH メタ層** | AI 駆動結果・Council 議事録・献上記録・対話セッション履歴・skill 起動ログ・Issue ライフサイクル・センサー出力 | DH 自身が AI 自律駆動を回すための内部観測 | Council 自身の判定精度・履歴参照・メタ認知 |
| **アプリ層** | 各プロジェクトの log/metric/trace/event | 各プロジェクトのアプリ運用観測 | Council がプロジェクト判定を行うためのファクト |

## 軸 vi の二層モデル詳細

### 収集層 (Raw Data Layer)

**目的**: 後追い分析と LLM 推論のための充実したデータ基盤

**原則**:
- **精緻に・高解像度で・構造化**して取る
- **データは薄くしない**（集約・サンプリングは提示層で行う）
- **構造化**（JSON・structured logging・schema 準拠）
- **命名規則統一**（後で提示層との連続性を保つため）

**合格基準**:
```yaml
収集層要件:
  構造化: JSON 形式または構造化 schema 準拠
  命名規則: kebab-case または snake_case で統一
  高解像度: 
    - trace: 全 request 取得
    - metric: p99 まで記録
    - log: DEBUG レベル保持許容
  schema統一: 同一種別のデータは同一 schema
```

**例（合格）**:
```json
// 注文処理のログ - 構造化・高解像度
{
  "timestamp": "2026-05-04T05:45:00.123Z",
  "level": "INFO",
  "service": "order-service", 
  "trace_id": "abc123",
  "span_id": "def456",
  "order_id": "ord_789",
  "event": "order_processed",
  "duration_ms": 245,
  "user_id": "usr_101",
  "items_count": 3,
  "total_amount": 1299
}

// メトリクス - 命名規則統一・高解像度
order_process_duration_seconds_bucket{le="0.1"} 45
order_process_duration_seconds_bucket{le="0.5"} 123  
order_process_duration_seconds_bucket{le="1.0"} 234
order_process_duration_seconds_count 250
order_process_duration_seconds_sum 125.4
```

**例（不合格）**:
```
// 非構造化・情報薄い
2026-05-04 05:45:00 INFO Order processed in 245ms

// 命名規則バラバラ  
orderDuration vs order_process_time vs OrderProcessingLatency
```

### 提示層 (Presentation Layer)

**目的**: P3（人間の事後確認）が一目で理解できる粒度への集約

**原則**:
- **P3 が一目で意味を取れる**粒度
- **ダッシュボード項目数 ≤ N**（認知負荷の制限）
- **カーディナリティ上限**（データ爆発の回避）
- **要約粒度が業務単位**（技術単位ではない）

**合格基準**:
```yaml
提示層要件:
  項目数制限: ダッシュボード 1 画面あたり ≤ 8 項目
  カーディナリティ: metric label 組み合わせ ≤ 1000
  要約粒度: 業務上意味のある単位（機能・ユーザー種別・地域等）
  一目理解: P3 が 3 秒以内で状況把握可能
```

**例（合格）**:
```yaml
# 注文システムダッシュボード - 業務視点・一目理解
panels:
  - title: "注文成功率"
    metric: "order_success_rate"
    target: "> 99.5%"
    current: "99.7%"
    
  - title: "平均処理時間"  
    metric: "order_avg_duration"
    target: "< 500ms"
    current: "245ms"
    
  - title: "エラー率"
    metric: "order_error_rate" 
    target: "< 0.1%"
    current: "0.03%"
```

**例（不合格）**:
```yaml
# 項目過多・技術視点
panels:
  - CPU使用率
  - メモリ使用率  
  - ディスクIO
  - ネットワーク帯域
  - JVM GC回数
  - DB接続プール
  - Redis HIT率
  - ... (15項目) ← 認知負荷過多
```

### 両層の整合性

**drilldown 連続性**:
提示層の「注文エラー率 0.03%」をクリックすると、収集層の該当ログ・トレースに飛べる設計。

**命名規則連続性**:
```
提示層: order_error_rate
    ↓ drilldown
収集層: order_service.event=order_failed (same naming convention)
```

## Council 3 ペルソナとの関係

### Business ペルソナへの影響

**ニーズ**: ビジネス影響の一目理解、KPI ダッシュボード

**軸 vi による保証**:
- 提示層でビジネス KPI が分かりやすく表示される
- 収集層で詳細な要因分析が可能
- 命名規則統一で「同じ事実」を共有

**不合格例の影響**:
- 技術メトリクス中心 → ビジネス影響が分からない
- 項目過多 → 重要指標が埋もれる

### Developer ペルソナへの影響

**ニーズ**: 技術的根本原因の特定、詳細データへのアクセス

**軸 vi による保証**:
- 収集層で高解像度データが充実
- 提示層から収集層への drilldown が可能
- 構造化により LLM での分析が可能

**不合格例の影響**:
- 収集データ不足 → 根本原因特定不能
- 非構造化 → 自動分析困難

### Philosopher ペルソナへの影響

**ニーズ**: 設計思想の一貫性、アーキテクチャ原則の確認

**軸 vi による保証**:
- 命名規則・schema の統一で設計一貫性を確認
- 観測性の設計思想（収集 vs 提示の分離）の確認
- メタ観測（観測システム自体の健全性）

**不合格例の影響**:
- 規格バラツキ → 設計思想の一貫性確認不能
- アドホックな観測 → 原則違反の検出困難

## Council 合議への具体的影響

### シナリオ 1: パフォーマンス問題の判定

**合格時（軸 vi PASS）**:
```
Business: 「ダッシュボードで注文処理時間が目標500msを超えて750msになってる」
Developer: 「収集層を見ると、DB クエリが原因。trace ID xyz123 で詳細確認済み」
Philosopher: 「観測データの命名規則が統一されているので、同じ事実を見て議論できている」
→ Council 合意: パフォーマンス改善を優先実施
```

**不合格時（軸 vi FAIL）**:
```
Business: 「売上への影響がダッシュボードから分からない」
Developer: 「ログが非構造化で分析困難。どのクエリが遅いか特定できない」  
Philosopher: 「観測データの品質がバラバラで、同じ事実を共有できていない」
→ Council 決議不能: 観測性改善を先行実施
```

### シナリオ 2: 新機能の影響評価

**合格時**:
```
Business: 「新機能追加後、コンバージョン率が 3.2% → 3.8% に向上」
Developer: 「エラー率は 0.03% で目標内、レスポンス時間も 245ms で良好」
Philosopher: 「収集層の構造化データにより、新機能の影響が定量的に評価できている」
→ Council 合意: 新機能展開継続
```

**不合格時**:
```
Business: 「新機能の効果が数値で見えない」
Developer: 「技術メトリクスしかなく、ビジネス影響が不明」
Philosopher: 「観測データの粒度が不適切で、意思決定に使えない」
→ Council 決議困難: 観測性設計の見直し要請
```

## Quality Gate での判定方法

### 機械検査

```bash
# 収集層チェック
## 構造化確認
grep -r "JSON.stringify\|structured" src/ | grep log

## 命名規則確認  
grep -r "metrics\|prometheus" src/ | grep -E "[a-z_]+_[a-z_]+_(total|count|duration|gauge)"

# 提示層チェック
## ダッシュボード項目数
dashboard_items=$(grep -c "panel\|widget\|metric" dashboards/*.json 2>/dev/null || echo "0")
[ "$dashboard_items" -le 8 ] || echo "Too many dashboard items: $dashboard_items"

## カーディナリティ制限
prometheus_cardinality_check || echo "High cardinality detected"
```

### AI 推論

**判定ポイント**:
1. **Business 視点**: 提示層でビジネス KPI が理解できるか？
2. **Developer 視点**: 収集層で技術的根本原因分析が可能か？
3. **Philosopher 視点**: 観測性設計の一貫性があるか？
4. **連続性**: 提示層から収集層への drilldown が機能するか？

**合格例**:
```json
{
  "axis": "vi",
  "judgment": "pass",
  "confidence": 0.92,
  "reasoning": "収集層は構造化され高解像度、提示層は業務視点で一目理解可能、両層の命名規則が統一されている",
  "evidence": [
    "JSON structured logging with consistent schema",
    "Dashboard items: 6 (within limit of 8)",
    "Metric naming: snake_case unified",
    "Drilldown links from dashboard to raw logs"
  ],
  "council_impact": "3 ペルソナが同じ事実を共有し、合意形成可能"
}
```

**不合格例**:
```json
{
  "axis": "vi", 
  "judgment": "fail",
  "confidence": 0.88,
  "reasoning": "収集層が非構造化で薄い、提示層が技術視点中心で業務影響不明、命名規則がバラバラ",
  "evidence": [
    "Plain text logs without structure",
    "Dashboard items: 15 (exceeds limit of 8)", 
    "Mixed naming: camelCase/snake_case/kebab-case",
    "No drilldown capability"
  ],
  "council_impact": "3 ペルソナが異なるデータを見て、合意形成困難"
}
```

## DH メタ層の観測性

### DH 自身の Council との関係

DH 自身も軸 vi の対象となり、以下を観測：

**収集層（DH メタ）**:
- skill 起動ログ（構造化）
- Issue ライフサイクル（JSON）
- Council 議事録（structured）
- 献上記録（schema 統一）

**提示層（DH メタ）**:
- DH 健全性ダッシュボード
- Council 合意率・confidence 分布
- Issue 処理速度・品質指標

**Council 自己観測**:
Council 自身が本軸 vi の恩恵を受け、自身の合議品質向上に活用。

## プロジェクト固有カスタマイズ

各プロジェクトは観測性要件をカスタマイズ可能：

```yaml
# .github/observability-config.yml
observability:
  collection_layer:
    structured_format: "json"  # json|structured|custom
    naming_convention: "snake_case"  # snake_case|kebab-case|camelCase
    retention_days: 90
    
  presentation_layer:
    max_dashboard_items: 8
    max_cardinality: 1000
    business_kpis: ["conversion_rate", "error_rate", "response_time"]
    
  council_integration:
    enable_drilldown: true
    unified_naming: true
    meta_observability: true
```