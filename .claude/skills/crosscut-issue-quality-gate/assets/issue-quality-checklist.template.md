# Issue Quality Checklist Template

このファイルは crosscut-issue-quality-gate で使用される、プロジェクト固有の Issue 品質チェックリストのテンプレートです。

各プロジェクトは本テンプレートをカスタマイズし、プロジェクト固有の要件に合わせて調整してください。

## 使用方法

1. 本ファイルを `.github/issue-quality-checklist.yml` としてコピー
2. プロジェクト固有の要件に合わせて各軸の設定を調整
3. crosscut-issue-quality-gate が自動的に本設定を読み込み

## テンプレート設定

```yaml
# Issue Quality Gate Configuration
# Project: [PROJECT_NAME]
# Version: 1.0.0

# 全体設定
global:
  project_name: "your-project-name"
  quality_gate_version: "5.8.0"
  strict_mode: true  # 厳格モード（false で一部軸を warning 化）
  
# 12軸個別設定
axes:
  
  # 軸 A: 仕様整合
  specification_alignment:
    enabled: true
    spec_files: 
      - "SPEC.md"
      - "docs/specification.md"
    dont_files:
      - "DONT.md" 
      - "docs/constraints.md"
    architecture_docs:
      - "ARCHITECTURE.md"
      - "docs/architecture/"
    # プロジェクト固有の仕様キーワード
    required_keywords: []  # 例: ["authentication", "database"]
    forbidden_patterns: []  # 例: ["hardcoded", "temporary fix"]
    
  # 軸 B: データ整合  
  data_consistency:
    enabled: true
    schema_files:
      - "schema.sql"
      - "migrations/*.sql"
      - "prisma/schema.prisma"
    evolution_guide: "docs/schema-evolution.md"
    migration_required: true  # schema 変更時に migration 必須
    backward_compatibility: true
    
  # 軸 C: コード整合
  code_consistency:
    enabled: true
    source_directories:
      - "src/"
      - "lib/"
    duplicate_threshold: 0.7  # 重複検出閾値
    abstraction_patterns:
      - "export function"
      - "export class" 
      - "export interface"
    
  # 軸 D: 依存整合
  dependency_consistency:
    enabled: true
    package_files:
      - "package.json"
      - "requirements.txt"
      - "Cargo.toml"
    license_checker: true
    bundle_size_threshold: 0.10  # bundle 増加許容率（10%）
    maintenance_check: true
    max_age_months: 12  # 依存の最大年数
    
  # 軸 E: 品質均一化
  quality_standardization:
    enabled: true
    test_directories:
      - "tests/"
      - "spec/"
      - "__tests__/"
    coverage_threshold: 80  # カバレッジ最低基準（%）
    test_patterns:
      - "*.test.js"
      - "*.spec.ts"
      - "*_test.py"
    sensor_files:
      - "monitoring/"
      - "observability/"
      
  # 軸 ii: 重複検出
  duplication_detection:
    enabled: true
    similarity_threshold: 0.7  # 類似度閾値
    ngram_size: 3
    check_title: true
    check_body: true
    check_labels: true
    
  # 軸 iii: セキュリティ
  security:
    enabled: true
    secret_patterns:
      - "password"
      - "secret"
      - "api_key"
      - "private_key"
    auth_files:
      - "auth/"
      - "security/"
    owasp_check: true
    security_docs: "docs/security.md"
    
  # 軸 v: 後方互換
  backward_compatibility:
    enabled: true
    api_spec_files:
      - "api.yaml"
      - "openapi.json"
    semver_required: true
    rollback_plan: true  # 破壊的変更時にロールバック計画必須
    changelog_required: true
    
  # 軸 vi: 観測性統一
  observability_unification:
    enabled: true
    # 収集層設定
    collection_layer:
      structured_format: "json"  # json | structured | custom
      naming_convention: "snake_case"  # snake_case | kebab-case | camelCase
      retention_days: 90
      high_resolution: true  # 高解像度データ保持
    # 提示層設定  
    presentation_layer:
      max_dashboard_items: 8
      max_cardinality: 1000
      business_focus: true  # 業務視点の集約
    # Council連携
    council_integration:
      enable_drilldown: true
      unified_naming: true
      meta_observability: true
      
  # 軸 vii: ドキュメント波及
  documentation_propagation:
    enabled: true
    doc_files:
      - "README.md"
      - "INDEX.md" 
      - "docs/"
    changelog_required: true
    api_docs:
      - "api-docs/"
      - "swagger/"
    link_check: true
    
  # 軸 viii: テスト粒度
  test_granularity:
    enabled: true
    test_first_required: true  # test-first 計画必須
    tdd_compliance: true
    test_strategy_required: true
    coverage_per_module: true
    integration_test_required: false  # プロジェクトに応じて調整
    
  # 軸 ix: 並列安全性
  parallel_safety:
    enabled: true
    scope_labels:
      - "scope:frontend"
      - "scope:backend" 
      - "scope:db"
      - "scope:api"
      - "scope:docs"
      - "scope:infra"
      # プロジェクト固有 scope を追加
    mutex_labels:
      - "mutex:auth-model"
      - "mutex:state-machine"
      - "mutex:payment-flow"
      # プロジェクト固有 mutex を追加
    refactor_controls:
      major_freeze: true  # refactor:major で全 Issue 凍結
      minor_scope_freeze: true  # refactor:minor で同 scope 凍結
    depends_on_check: true
    ai_conflict_detection: true
    confidence_threshold: 0.8

# 特例設定
exceptions:
  emergency_bypass:
    enabled: true
    bypass_label: "emergency-bypass" 
    reason_required: true
    post_review_required: true
    
  admin_override:
    enabled: true
    override_label: "gate-override:admin"
    audit_logging: true
    
  experimental_features:
    enabled: true
    experimental_label: "experimental"
    relaxed_axes: ["v", "E", "vi"]  # 後方互換・品質・観測性を緩和

# 通知設定
notifications:
  gate_failure:
    issue_comment: true
    label_assignment: true
    team_mention: "@dev-team"
    
  gate_success:
    silent: true  # 成功時は静音
    metrics_logging: true

# AI推論設定
ai_judgment:
  model_preference: "claude"  # claude | gpt | gemini
  confidence_threshold: 0.8
  context_window: "extended"  # basic | extended | full
  
  # プロンプトカスタマイズ
  custom_prompts:
    project_context: |
      This project is a [PROJECT_TYPE] with the following key characteristics:
      - Technology stack: [STACK]
      - Architecture pattern: [ARCHITECTURE] 
      - Business domain: [DOMAIN]
      - Team size: [TEAM_SIZE]
      
    quality_focus: |
      Pay special attention to:
      - [CUSTOM_FOCUS_1]
      - [CUSTOM_FOCUS_2]

# プロジェクト固有拡張
project_specific:
  # カスタム軸（将来拡張）
  custom_axes: []
  
  # 追加チェック
  additional_checks:
    - name: "license_headers"
      description: "Source files must have license headers"
      enabled: false
      
    - name: "commit_message_format" 
      description: "Commit messages must follow conventional commits"
      enabled: false
      
  # 業界固有要件
  industry_compliance:
    gdpr: false
    hipaa: false
    pci_dss: false
    sox: false

# 統計・監視
monitoring:
  success_rate_tracking: true
  failure_pattern_analysis: true
  performance_monitoring: true
  false_positive_tracking: true
  
  # メトリクス出力先
  metrics_export:
    prometheus: false
    datadog: false
    custom_webhook: ""

# バージョン管理
versioning:
  config_version: "1.0.0"
  last_updated: "2026-05-04"
  updated_by: "quality-gate-setup"
  changelog:
    - "1.0.0: Initial template creation"
```

## カスタマイズガイド

### 1. 基本設定の調整

```yaml
# プロジェクト名とバージョンを設定
global:
  project_name: "your-actual-project"
  strict_mode: false  # 初期は false、慣れたら true に

# 使わない軸を無効化
axes:
  observability_unification:
    enabled: false  # 観測性が未整備なら一時無効
```

### 2. ファイルパスの調整

```yaml
# プロジェクト構造に合わせてパスを調整
specification_alignment:
  spec_files: 
    - "docs/requirements.md"  # SPEC.md がない場合
    - "README.md"             # READMEで代用
```

### 3. プロジェクト固有軸の追加

```yaml
# 例: モバイルアプリの場合
custom_axes:
  - name: "platform_compatibility"
    description: "iOS/Android compatibility check"
    enabled: true
    ios_check: true
    android_check: true
```

### 4. 緩和規定の設定

```yaml
# 小規模プロジェクト向け緩和
axes:
  test_granularity:
    coverage_threshold: 60  # 80% → 60% に緩和
  parallel_safety:
    ai_conflict_detection: false  # AI判定無効化
```

### 5. 通知のカスタマイズ

```yaml
notifications:
  gate_failure:
    team_mention: "@your-team"
    slack_webhook: "https://hooks.slack.com/..."
```

## 段階的導入

### Phase 1: 基本軸のみ

```yaml
# 最初は基本的な軸のみ有効化
axes:
  specification_alignment: {enabled: true}
  duplication_detection: {enabled: true}
  security: {enabled: true}
  # その他は無効
```

### Phase 2: 品質軸追加

```yaml
# 慣れたら品質関連軸を追加
  quality_standardization: {enabled: true}
  test_granularity: {enabled: true}
  documentation_propagation: {enabled: true}
```

### Phase 3: 高度な軸

```yaml
# 最終的に全軸を有効化
  observability_unification: {enabled: true}
  parallel_safety: {enabled: true}
  backward_compatibility: {enabled: true}
```

## トラブルシューティング

### よくある設定ミス

1. **ファイルパス不正**: 存在しないパスを指定
2. **閾値が厳しすぎる**: 現実的でない基準設定
3. **AI設定過負荷**: context_window を "full" にして重くなる

### 設定確認コマンド

```bash
# 設定ファイルの構文チェック
npx js-yaml .github/issue-quality-checklist.yml

# Quality Gate のテスト実行
crosscut-issue-quality-gate --dry-run --config-check
```

## 更新履歴

- 1.0.0 (2026-05-04): 初期テンプレート作成
- [今後の更新履歴をここに記録]