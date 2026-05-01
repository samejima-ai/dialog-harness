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
| **S (Scale)** | プロジェクト/判断モーメントの規模軸（影響範囲・対象数） | リファクタの影響範囲（行数・依存数） | 該当 paths の行数合計、import 元の数、テスト依存数 |
| **U (Uncertainty)** | プロジェクト/判断モーメントの不確実性軸（仕様・前提の確定度） | 意図の不明瞭度（仮説の確信度の逆数） | 確度メタデータが ai_inference なら高め、code_check なら低め |
| **R (Risk)** | プロジェクト/判断モーメントのリスク軸（不可逆性・影響度） | 壊した時の本番影響度 | 認証・決済・データ永続化等に該当すれば高、UI 装飾なら低 |

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
- `discard_and_redesign` 推奨時は必ず `absent_intent_protocol.md` の確定条件をクロスチェック

---

## 仮説提示の注意事項

- **3 島ずつバッチ提示**: 1 応答で 5 島以上を一括提示すると人間の判断疲労が増える
- **5 問ルール**: 1 セッションで AI 質問数が 5 問超過したら、残り島の確度を下げて `forgotten` で仮確定し、Step 5 で一括判定（`dialog-flow-archeo.md` §自己制限規約）
- **転記禁止**: archaeology-protocol.md の深度判定を本ファイルに転記しない。参照のみ
- **DONT.md 移送候補**: `human_confirmation: absent` で `redesign_directive: deferred` の Island は DONT.md 移送候補として `notes` に明記
