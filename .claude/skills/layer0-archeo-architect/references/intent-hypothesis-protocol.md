# 意図仮説生成プロトコル

archeo-architect の Step 1 (構造走査) ・ Step 2 (意図仮説提示) で使うヒューリスティックと確度規約。

---

## 設計原則

- **仮説は提示するが捏造しない**: 確度の低い仮説は確度メタデータで明示的にラベル付けする
- **ヒント単独では確定しない**: 仮説生成ヒントは「疑い」レベル。人間の認識合わせ（Step 3）か明示宣言（Step 5）でのみ確定する
- **人間裁量への委譲**: AI は仮説と確度を提示するのみ。確定は常に人間

---

## 仮説生成ヒューリスティック

各島について、以下のヒントを内部的に評価し、`inferred_intent` の生成材料にする。

| ヒント | 検出方法 | 確度寄与 |
|---|---|---|
| **コメント不在** | コメント密度がプロジェクト平均の下位 20% | 低（confidence: ai_inference） |
| **命名混乱** | 関数名・変数名が処理内容と乖離（LLM 推論判定） | 低〜中 |
| **重複ロジック** | 構造的類似度が高い（既存ツール or LLM 判定） | 中（複数箇所の意図統合の可能性） |
| **git log 不在 / squash されている** | git log の意図記述が極端に短い、squash で詳細失われ | 高（高確度の意図不在シグナル） |
| **テスト不在** | テストカバレッジが 0%、関連テストファイルなし | 中 |
| **マジックナンバー** | 数値リテラルへのコメント・定数化なし | 低 |
| **TODO/FIXME 散乱** | コメント内に TODO / FIXME / XXX が複数 | 中（未完成意図のシグナル） |
| **deprecated 痕跡** | コメント or git log に deprecated の言及あり | 高（意図移行中の可能性） |

### 複合判定

複数のヒントが該当する場合、以下のように `inferred_intent` の自然言語に反映する：

```
inferred_intent: |
  ユーザー認証のセッション管理を担う処理と推測。
  根拠: src/auth/session.ts の関数群が auth-register を呼び出し、cookie 操作を行う。
  ただしコメント不在 + git log 沈黙のため、確度は ai_inference。
  人間確認を要する。
```

---

## Code Smells カノンとの対応（業界知見統合）

ファウラー（Martin Fowler）/ ヘルマンズ（Felienne Hermans）が体系化した「Code Smells（コードの不吉な臭い）」のカノンと、本プロトコルの仮説生成ヒントの対応関係。Code Smells は確立された業界用語であり、AI 検出の信頼性向上と人間との対話精度向上の両方に資する。

業界根拠: Council 諮問 `council-2026-05-01T10:30:00Z-archeo01` で agreed_recommended 確定。

### 対応表

| Code Smell（カノン） | 本プロトコルの対応ヒント | 仮説生成への寄与 |
|---|---|---|
| **Long Method（巨大関数）** | コメント不在 + S 軸高（行数大） | 認知負荷の主因。意図が複数機能に分散している可能性 |
| **Duplicate Code（重複コード）** | 重複ロジック | 同一意図の複数実装、または異なる意図の偶然の類似。仮説の確度判定で要分離 |
| **Large Class / God Class（巨大クラス）** | S 軸高 + 命名混乱 | 単一責務原則違反、意図が複数領域に渡る |
| **Feature Envy（不適切な責務）** | 命名混乱 + 呼び出し関係の歪み | 意図の所属が誤っている。Boundaries の再裁定候補 |
| **Shotgun Surgery（散弾銃手術）** | git log で同時更新が頻発 | 単一意図が複数ファイルに散逸。Island 統合候補 |
| **Divergent Change（発散的変更）** | git log で同一ファイルが多目的更新 | 単一ファイルに複数意図が同居。Island 分割候補 |
| **Dead Code（死コード）** | 呼び出し元なし + テスト不在 | 廃止済み意図の残骸。`absent` 候補 |
| **Magic Number / Magic String** | マジックナンバー（既存ヒント） | 数値・文字列リテラルの意図不明、`forgotten` 候補 |
| **Comments（過剰コメント）** | コメント不在の逆 | 過剰コメントは意図の言語化失敗のシグナル、確度メタデータの参照優先度を下げる |
| **Speculative Generality（投機的汎用化）** | 使用されない汎用引数・拡張点 | 想定された未来意図が未実現、`absent` 候補 |
| **Temporary Field（一時フィールド）** | クラス内で稀にしか使われないフィールド | 特定意図専用のフィールドが共有領域に侵入、Boundaries 再裁定候補 |
| **Refused Bequest（拒否された遺産）** | 親クラス機能の不使用継承 | 継承意図と実装意図の乖離、`corrected` 候補 |

### 適用順序

Step 2（意図仮説提示）で、以下の順で Code Smells を判定し、仮説生成に反映する：

1. **構造的 Smells**（Long Method / Large Class / Duplicate Code）→ S 軸推定への寄与大
2. **責務 Smells**（Feature Envy / Shotgun Surgery / Divergent Change）→ Boundaries セクション候補の生成
3. **意図不在 Smells**（Dead Code / Speculative Generality / Magic Number）→ `absent` 候補の検出材料
4. **設計乖離 Smells**（Refused Bequest / Temporary Field）→ `corrected` 候補の検出材料

### 注意

- Code Smells はあくまで仮説生成ヒント。Step 3 の人間確認なしで `corrected` / `absent` を確定しない（P-Arch-2 捏造防止）
- ファウラーのカノン全 22 種のうち、archeo の文脈で意図復元に寄与するもの 12 種を厳選した。残り 10 種（Comments の細分類等）はリファクタ実行段階（L1 / Phase γ）で参照する

---

## 確度メタデータ規約

archaeology-protocol.md と同じ 3 段階を使う（再定義しない）：

| 確度 | 意味 | 提示時の文型 |
|---|---|---|
| `code_check` | コードを直接確認した。型シグネチャ・呼び出し関係から確実に読み取れる | 「コード確認: <内容>」 |
| `git_log_check` | git log / blame / PR コメントで意図を確認した | 「git 履歴で確認: <内容> (commit X)」 |
| `ai_inference` | AI が状況証拠から推定した。人間承認待ち | 「AI 推定: <内容>（要確認）」 |

### 必須付与

- すべての `inferred_intent` フィールドに必ず付与
- 確度メタデータが空の Island は §7.4 自己検証で FAIL（捏造防止メカニズム）
- 確度の根拠（どのコード行・どのコミット）を notes に記録

---

## S/U/R 推定（リファクタ文脈の読み替え）

`harness-verifier/glossary.yml` の `score_axes` を、本 skill のリファクタ文脈で読み替える。

| 軸 | 一般定義 | リファクタ文脈での読み替え | 推定方法 |
|---|---|---|---|
| **S (Scale)** | プロジェクト/判断モーメントの規模軸（影響範囲・対象数） | リファクタの影響範囲（行数・依存数 + **Git ホットスポット指標**） | 該当 paths の行数合計、import 元の数、テスト依存数、**Git 修正頻度 × 複雑性スコア** |
| **U (Uncertainty)** | プロジェクト/判断モーメントの不確実性軸（仕様・前提の確定度） | 意図の不明瞭度（仮説の確信度の逆数） | 確度メタデータが ai_inference なら高め、code_check なら低め |
| **R (Risk)** | プロジェクト/判断モーメントのリスク軸（不可逆性・影響度） | 壊した時の本番影響度 | 認証・決済・データ永続化等に該当すれば高、UI 装飾なら低 |

### Git ホットスポット分析（S 軸の補強）

業界知見（Adam Tornhill「Your Code as a Crime Scene」/ ヘルマンズの認知負荷論）に基づき、「**修正頻度が高く複雑性も高い領域**」をホットスポットとして S 軸に統合する。リファクタ投資対効果を最大化するための定量指標。

業界根拠: Council 諮問 `council-2026-05-01T10:30:00Z-archeo01` で agreed_recommended 確定。

#### 指標の算出

各島について、Step 1 構造走査時に以下を計算：

```
hotspot_score = log(修正頻度) × 複雑性指標
```

- **修正頻度**: `git log --follow --format='%H' <path>` のコミット数（過去 N ヶ月、N は archaeology_depth で決定: shallow=3 / standard=6 / deep=12 / full=24）
- **複雑性指標**: 行数 + 関数の循環的複雑度（cyclomatic complexity）の単純和。算出が困難な言語では行数のみで代替可

#### S 軸への寄与

`hotspot_score` の分布から該当島の S 軸を補正：

| hotspot_score | S 軸への寄与 | 解釈 |
|---|---|---|
| 上位 10% | +1（最大 3 にクリップ） | リファクタ投資の最優先対象 |
| 上位 30% | +0.5 | 高優先度 |
| それ以外 | ±0 | 標準 |

#### 戦略的含意

- **U 軸高 + ホットスポット高** → archeo 対話の優先対象（意図不明 + 頻繁に変更されている = 認知負荷の主因）
- **U 軸低 + ホットスポット高** → archeo 対話を経ずに L1 へ直接渡してよい（意図明確 + リファクタ価値高）
- **U 軸高 + ホットスポット低** → 意図不明だが触られていない領域。`refactor_directive: preserve` または `discard_and_redesign` が妥当
- **U 軸低 + ホットスポット低** → リファクタ対象外。Step 4 で archeo セッションから除外する候補

#### 業界アンチパターンとの整合

業界ガイドが指摘する **「90 日の法則」**（最初の 90 日で 5% の機能を移行できないと 92% の確率で失敗）に対応するため、ホットスポット上位 10% は archeo セッションの**初期対話対象**として優先提示する。「低リスク・高価値」モジュールの早期着手で実績を作る戦略。

#### 計測の制約

- shallow 深度では `hotspot_score` 計算をスキップしてよい（過去 3 ヶ月のデータで信頼性が低い）
- 新規プロジェクト（Lifecycle L=0）では本指標は適用外（archeo 自体が L≥1 で発動）
- Git ホスティング外のリポジトリ（Subversion 等）では複雑性指標のみで代替

### 0-3 段階の推奨閾値

| スコア | S 目安 | U 目安 | R 目安 |
|---|---|---|---|
| 0 | < 100 行、依存 0 | code_check 確度高、コメント完備 | UI 装飾 / ログ等の周辺機能 |
| 1 | 100-500 行、依存 1-3 | code_check 確度中、コメント部分あり | 業務ロジック（読み取り専用） |
| 2 | 500-2000 行、依存 4-10 | git_log_check 確度、コメント希薄 | 業務ロジック（書き込みあり） |
| 3 | > 2000 行、依存 > 10 | ai_inference のみ、コメント皆無 | 認証 / 決済 / データ整合性等 |

### 戦略的優先度

archeo の対話戦略として、**U が高い島から優先的に対話する**。S が大きく U が低い島は意図が明確なので、Step 3 で `confirmed` を一括収集して Layer 1 に直接渡してよい。

---

## refactor_directive の AI 推奨ロジック

`refactor_directive` は人間が決定するが、AI は推奨を提示できる。推奨ロジック：

| 条件 | 推奨 directive | 根拠 |
|---|---|---|
| `human_confirmation: confirmed` + S 低 | `preserve` | 意図明確、リファクタ不要 |
| `human_confirmation: confirmed` + S 高 + U 低 | `restructure` | 意図明確、規模により再構造化価値あり |
| `human_confirmation: corrected` | `restructure` | 訂正された意図で再構造化 |
| `human_confirmation: absent` | `discard_and_redesign` | 意図不在、新規設計が妥当 |
| `human_confirmation: forgotten`（Step 5 未通過） | （推奨保留） | Step 5 完了後に再評価 |

### 提示文型

```
Island-NNN の refactor_directive 推奨: <preserve | restructure | discard_and_redesign>
根拠: <human_confirmation: X + S=N + U=N + R=N>

異論があれば指摘してください。
```

### 禁則

- AI が `refactor_directive` を単独確定しない（人間レビュー必須）
- `discard_and_redesign` 推奨時は必ず `absent-intent-protocol.md` の確定条件をクロスチェック

---

## 仮説提示の注意事項

- **3 島ずつバッチ提示**: 1 応答で 5 島以上を一括提示すると人間の判断疲労が増える
- **5 問ルール**: 1 セッションで AI 質問数が 5 問超過したら、残り島の確度を下げて `forgotten` で仮確定し、Step 5 で一括判定（`dialog-flow-archeo.md` §自己制限規約）
- **転記禁止**: archaeology-protocol.md の深度判定を本ファイルに転記しない。参照のみ
- **DONT.md 移送候補**: `human_confirmation: absent` で `redesign_directive: deferred` の Island は DONT.md 移送候補として `notes` に明記
