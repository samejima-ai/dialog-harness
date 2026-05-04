# 機械検査規格

本ドキュメントは crosscut-issue-quality-gate の各軸における機械検査の具体的な実装仕様を定義する。

## 軸 A: 仕様整合

### SPEC.md 整合チェック

```bash
# SPEC.md の存在確認
test -f SPEC.md || echo "SPEC.md not found"

# Issue 本文と SPEC.md のキーワード照合
grep -i "$(echo "$issue_body" | tr ' ' '\n' | head -10 | tr '\n' '|')" SPEC.md

# 禁止事項チェック（DONT.md）
if [ -f DONT.md ]; then
  grep -i "$(echo "$issue_body" | tr ' ' '\n' | head -10 | tr '\n' '|')" DONT.md && echo "DONT violation detected"
fi
```

### ADR 矛盾チェック

```bash
# ADR ファイルとの照合
find . -name "*.md" -path "*/history/*" -o -path "*/decisions/*" | xargs grep -l "deprecated\|obsolete\|replaced"
```

## 軸 B: データ整合

### Schema diff チェック

```bash
# データベース schema ファイルの変更検出
git diff --name-only HEAD~1 | grep -E "\.(sql|migration|schema)\$"

# schema-evolution.md の存在確認
test -f docs/schema-evolution.md || test -f schema-evolution.md
```

### Migration 必須化

```bash
# migration script の存在確認（schema 変更時）
if git diff --name-only HEAD~1 | grep -q schema; then
  find . -name "*migration*" -newer schema.sql || echo "Migration required"
fi
```

## 軸 C: コード整合

### 既存抽象 grep

```bash
# 同名 export の検出
find src -name "*.ts" -o -name "*.js" | xargs grep "export.*function\|export.*class\|export.*const" | sort | uniq -d

# 重複インターフェース検出
grep -r "interface.*{" src/ | cut -d: -f2 | sort | uniq -d
```

### Import パターン整合

```bash
# import 形式の統一確認
grep -r "import.*from" src/ | grep -v -E "from ['\"](@|\.)"
```

## 軸 D: 依存整合

### package.json チェック

```bash
# package.json の変更検出
git diff --name-only HEAD~1 | grep package.json

# 新しい依存の検出
git diff HEAD~1 package.json | grep "^\+.*\":"
```

### ライセンス検査

```bash
# license-checker の実行
npx license-checker --summary

# GPL 系ライセンスの検出
npx license-checker --json | jq '.[] | select(.licenses | contains("GPL"))'
```

### Bundle size チェック

```bash
# webpack-bundle-analyzer でサイズ測定
npm run build && npx webpack-bundle-analyzer build/static/js/*.js --no-open --report
```

## 軸 E: 品質均一化

### テスト必須項目

```bash
# テストファイルの存在確認
find . -name "*.test.*" -o -name "*.spec.*" | wc -l

# カバレッジ設定確認
grep -E "coverageThreshold|coverage" package.json jest.config.js 2>/dev/null
```

### Sensor 配置確認

```bash
# sensor ファイルの存在
find . -name "*sensor*" -o -name "*monitor*"

# 観測性設定確認
grep -r "winston\|console\|logger" src/ | grep -v test
```

## 軸 ii: 重複検出

### Issue 類似度計算

```python
# Python script for n-gram similarity
import re
from collections import Counter

def ngram_similarity(text1, text2, n=3):
    def get_ngrams(text, n):
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        words = text.split()
        return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    
    ngrams1 = Counter(get_ngrams(text1, n))
    ngrams2 = Counter(get_ngrams(text2, n))
    
    intersection = sum((ngrams1 & ngrams2).values())
    union = sum((ngrams1 | ngrams2).values())
    
    return intersection / union if union > 0 else 0
```

### 既存 Issue 検索

```bash
# GitHub CLI で既存 Issue を取得
gh issue list --state all --json title,body,number --limit 100 > existing_issues.json

# キーワード重複チェック
echo "$issue_title" | tr ' ' '\n' | while read word; do
  grep -i "$word" existing_issues.json
done
```

## 軸 iii: セキュリティ

### Secrets scan

```bash
# git-secrets でシークレット検出
git secrets --scan

# 一般的なシークレットパターン
grep -r -E "(password|secret|key|token|api_key)" --include="*.js" --include="*.ts" src/
```

### Auth 関連検査

```bash
# 認証関連パターンのチェック
grep -r -E "(auth|login|session|jwt|oauth)" src/ | grep -v test

# 認可テーブルとの整合確認
test -f docs/authorization-matrix.md || echo "Authorization matrix not found"
```

## 軸 v: 後方互換

### API schema diff

```bash
# OpenAPI spec の変更検出
git diff HEAD~1 -- "*.yaml" "*.json" | grep -E "required|properties"

# 破壊的変更の検出
git diff HEAD~1 -- "*.yaml" | grep "^-" | grep -E "required|properties"
```

### Semver チェック

```bash
# package.json version の形式確認
grep '"version"' package.json | grep -E "[0-9]+\.[0-9]+\.[0-9]+"

# CHANGELOG の更新確認
git diff HEAD~1 CHANGELOG.md | grep "^+"
```

## 軸 vi: 観測性統一

### 収集層チェック

```bash
# 構造化ログの形式確認
grep -r "JSON.stringify\|structured" src/ | grep log

# メトリクス命名規則確認
grep -r "metrics\|prometheus\|statsd" src/ | grep -E "[a-z_]+_[a-z_]+_(total|count|duration|gauge)"
```

### 提示層チェック

```bash
# ダッシュボード設定ファイル
find . -name "*dashboard*" -o -name "*grafana*" | head -10

# 項目数カウント
grep -c "panel\|widget\|metric" dashboards/*.json 2>/dev/null || echo "0"
```

## 軸 vii: ドキュメント波及

### ドキュメント更新確認

```bash
# README.md の更新
git diff HEAD~1 README.md | grep "^+"

# INDEX.md の更新
test -f INDEX.md && git diff HEAD~1 INDEX.md

# ADR の追加
find history/ -name "*.md" -newer package.json 2>/dev/null
```

### リンク整合性

```bash
# 内部リンクのチェック: markdown link 構文を検出する regex
grep -rE '\[[^]]+\]\([^)]+\.md\)' *.md | while IFS=: read file link; do
  target=$(echo "$link" | sed 's/.*](\([^)]*\)).*/\1/')
  test -f "$target" || echo "Broken link: $file -> $target"
done
```

## 軸 viii: テスト粒度

### テストファイル検証

```bash
# テストファイルと実装ファイルの対応確認
find src -name "*.ts" | while read file; do
  testfile=$(echo "$file" | sed 's/\.ts$/.test.ts/')
  test -f "$testfile" || echo "Missing test: $testfile"
done
```

### カバレッジ閾値

```bash
# Jest カバレッジ設定確認
grep -A5 "coverageThreshold" jest.config.js package.json 2>/dev/null

# カバレッジレポート生成
npm test -- --coverage --watchAll=false
```

## 軸 ix: 並列安全性

### ラベル取得・検証

```bash
# Issue ラベルの取得
issue_labels=$(gh issue view "$issue_number" --json labels | jq -r '.labels[].name')

# scope ラベルの確認
echo "$issue_labels" | grep "^scope:" || echo "No scope label"

# mutex ラベルの確認
echo "$issue_labels" | grep "^mutex:"

# depends-on の確認（Issue body から）
grep -E "depends[- ]on:?\s*#[0-9]+" <<< "$issue_body"
```

### 並列 Issue チェック

```bash
# in-progress Issue の取得
gh issue list --label "in-progress" --json number,labels,title

# scope 衝突チェック
current_scope=$(echo "$issue_labels" | grep "^scope:" | head -1)
if [ -n "$current_scope" ]; then
  gh issue list --label "$current_scope" --label "in-progress" --json number
fi
```

### Big Refactor 検出

```bash
# refactor:major の検出
echo "$issue_labels" | grep "refactor:major" && echo "Major refactor detected - consider freeze"

# freeze-period チェック
gh issue list --label "freeze-period" --json number | jq length
```

## 実行環境要件

### 必要ツール

- `bash` 4.0+
- `git` 2.20+
- `gh` (GitHub CLI) 2.0+
- `jq` 1.6+
- `grep` (GNU grep 推奨)
- `find` (GNU findutils 推奨)

### Node.js プロジェクト固有

- `npm` または `yarn`
- `npx` (license-checker, webpack-bundle-analyzer 用)

### Python プロジェクト固有

- `python3` 3.8+
- `pip` (requirements.txt の解析用)

## エラーハンドリング

### 機械検査失敗時の対応

1. **ツール不在**: 該当軸をスキップし、AI 推論のみで判定
2. **権限不足**: read-only チェックに降格
3. **タイムアウト**: 部分結果で判定、理由をログに記録
4. **例外**: エラー内容をログに記録し、AI 推論へ委譲

### 設定のカスタマイズ

プロジェクト固有の機械検査設定は `.github/issue-quality-gate-config.yml` で上書き可能：

```yaml
machine_checks:
  axis_a:
    spec_files: ["SPEC.md", "docs/specification.md"]
    dont_files: ["DONT.md", "docs/constraints.md"]
  axis_d:
    bundle_size_threshold: 0.15  # default: 0.10 (10%)
  axis_vi:
    max_dashboard_items: 12      # default: 8
```