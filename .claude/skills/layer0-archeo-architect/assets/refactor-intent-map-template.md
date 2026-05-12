# Refactor Intent Map

archeo-architect が生成する意図マップテンプレート。
本テンプレートを `delivery/refactor-intent-map.md`（canonical filename）に複写・記入して使う。複数回生成時は新版で canonical を上書きし、旧版は `delivery/archive/refactor-intent-map-YYYY-MM-DD.md` にアーカイブ移動する（L1 は archive/ を参照しない）。

**捏造防止規約（P-Arch-2 実装）**: `human_confirmation` が未入力（`pending`）の Island は §7.4 自己検証で FAIL。AI 単独での `corrected` / `absent` 確定は物理的に禁止する（必須フィールドで担保）。

---

## Meta

```yaml
target: <対象コードベースのパスまたはリポジトリ名>
scanned_at: <ISO 8601 timestamp、例: 2026-05-01T12:00:00Z>
delivered_at: <Step 7 合意完了時の ISO 8601 timestamp>
archeo_session_id: <識別子、例: archeo-2026-05-01-001>
archaeology_depth: <shallow | standard | deep | full>  # archaeology-protocol.md 準拠
ai_capability_version: <例: Claude Opus 4.7>
self_verification: <pending | passed | failed>  # §7.4 完了時に passed
```

`target` / `scanned_at` / `archeo_session_id` / `archaeology_depth` は Phase α（Step 1 構造走査）で記入。
`delivered_at` / `self_verification` は Phase γ/δ（Step 7 / §7.4）で記入。

---

## Islands

各島について以下のフィールドを全て記入する。1 フィールドでも欠けていれば §7.4 FAIL。

### Island-001: <名前、AI が命名 + 人間承認で最終確定>

```yaml
paths:
  - <ファイルパスまたはディレクトリ、例: src/auth/register.ts>
  - <例: src/auth/register.ts:42-78 で行範囲も指定可>

island_type: <logic | visual>
  # v5.16.0 追加。logic = 機能・データ・ロジック領域（既存挙動）。
  # visual = UI 視覚仕様の島（CSS / Tailwind config / styled-components / theme.ts /
  # デザイントークン）。UI プロジェクト & DESIGN.md 存在時のみ visual を採用。
  # 未指定時は logic とみなす（後方互換）

inferred_intent: |
  <AI が仮説として提示した意図、自然言語 1-3 文>
  # visual Island の場合: 「なぜこの色を採用したか」「なぜこの spacing にしたか」等の
  # 視覚的判断の意図を仮説化する（例: 「primary を CTA 専用にしているのは視線誘導を
  # 1 つに絞るため」「mono-data を等幅にしているのは数値の桁揃え目的」）

human_confirmation: <confirmed | corrected | forgotten | absent>
  # confirmed: AI 仮説が合っていると人間が確認
  # corrected: 人間が訂正（corrected_intent を必ず記入）
  # forgotten: 思い出せない（Step 5 で再判定、最終確定時には別 4 値のいずれかへ）
  # absent: 当時から意図なし（人間明示宣言必須、notes に発話を記録）

corrected_intent: |
  <human_confirmation が corrected の場合のみ記入。人間が訂正した意図>
  <それ以外は空欄または "N/A">

confidence: <code_check | git_log_check | ai_inference>
  # archaeology-protocol.md と同じ語彙
  # code_check: コードを直接確認した
  # git_log_check: git log / blame で意図を確認した
  # ai_inference: AI 推定（人間承認待ち）

S: <0-3>  # Scale: リファクタの影響範囲（行数 / 依存数）
U: <0-3>  # Uncertainty: 意図の不明瞭度（仮説の確信度の逆数）
R: <0-3>  # Risk: 壊した時のダメージ（本番影響度）

refactor_directive: <preserve | restructure | discard_and_redesign>
  # preserve: 現状維持（リファクタ対象外）
  # restructure: 既存意図を保ったまま再構造化
  # discard_and_redesign: 破棄して新規設計（absent 時の典型）

design_md_impact: <none | tokens_only | dos_and_donts | both>
  # v5.16.0 追加、island_type: visual の場合のみ意味を持つ
  # none: DESIGN.md への影響なし（純粋なコード整理）
  # tokens_only: DESIGN.md YAML フロントマターのトークン定義に影響（追加 / 改名 / 削除）
  # dos_and_donts: DESIGN.md Markdown 本体の Do's and Don'ts に影響（規約追加 / 緩和）
  # both: 両方に影響
  # logic Island では常に "none"

notes: |
  <自由記述。human_confirmation: absent の場合は人間の明示宣言を引用すること>
  <例: 「ひでさん発話: 思い出せない、当時から意図がなかった (2026-05-01)」>
  # visual Island の場合は DESIGN.md 該当セクションへの言及を含めると後続 L1 が
  # 意図合致検証時に参照しやすい
```

### Island-002: ...

（Island-001 と同形式で繰り返し）

---

## Boundaries

島と島の境界が曖昧な箇所のリスト。Step 4（境界曖昧領域の特定）で記録する。

### Boundary-001: <該当箇所のパス、例: src/auth/middleware.ts>

```yaml
candidates:
  - <候補島1、例: Island-001 (auth-register)>
  - <候補島2、例: Island-003 (session-management)>
  - <候補島3、例: 新島として切り出し: Island-007 (auth-middleware)>

human_decision: <Island-XXX | both | new_island | undecided>
  # Island-XXX: いずれかの島に帰属
  # both: 両方に属する（共有所有）
  # new_island: 新島として切り出し（candidates の 3 番目等）
  # undecided: 判断保留（次回 archeo 起動時に再判定）

rationale: |
  <人間が判断した根拠、または AI が選択肢提示時に出した根拠>

resolved_at: <ISO 8601 timestamp>
```

### Boundary-002: ...

---

## Absent-Intent Zones

意図不在と判定された領域（`human_confirmation: absent` で確定された Island の集約）。
新規設計に切り替えるべき範囲を明示する。

### AbsentZone-001: <領域名、例: legacy-config-loader>

```yaml
covered_islands:
  - Island-XXX  # human_confirmation: absent の Island ID

scope_paths:
  - <ファイルパスまたはディレクトリ>

human_declaration: |
  <人間の明示宣言を引用、発話日時付き>
  <例: 「特に考えてなかった、意図なし (ひでさん発話, 2026-05-01)」>

redesign_directive: <required | optional | deferred>
  # required: 新規設計が必須（discard_and_redesign）
  # optional: 新規設計を推奨するが優先度低
  # deferred: 当面凍結、将来の archeo 再起動時に再判定

notes: |
  <DONT.md への移送候補なら明記>
```

### AbsentZone-002: ...

---

## Summary（自動集計、Step 7 合意時に AI が記入）

```yaml
total_islands: <数>
confirmed_count: <数>
corrected_count: <数>
forgotten_count: <数>  # Step 5 完了後はゼロが正常
absent_count: <数>

refactor_directive_distribution:
  preserve: <数>
  restructure: <数>
  discard_and_redesign: <数>

boundaries_resolved: <数> / <total>
absent_zones_count: <数>

avg_confidence:
  code_check: <数>
  git_log_check: <数>
  ai_inference: <数>
```

---

## 拡張余地（v6.0.0 候補、温存）

将来 AI エージェント間引き継ぎへの拡張可能性のため、Islands スキーマは AI 組織応用に拡張可能な形を保つ。
v5.x 帯では「コードベース内の意図復元」に限定し、AI 組織応用は射程外（DONT 相当）。
