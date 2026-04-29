# BOUNDARY — DH と harness-verifier の境界線

DH 本体（D4）と本機構（D4 検査機構）の責務分離を明示化する。
越境してはいけない領域を定義し、独立性要請を保持する。

---

## 1. 5 次元論（用語定義）

dialog-harness は次の 5 次元で構成される：

| 次元 | 名称 | 実体 | 配置 |
|---|---|---|---|
| D1 | ソースコード | プロジェクト実装ファイル群（`src/` 等） | 配布先プロジェクト内 |
| D2 | 開発環境 | D1 の足場（`package.json` / `vite.config` / `sensors/` / `SPEC.md` 等） | 配布先プロジェクト内 |
| D3 | 配布 skill | 利用者プロジェクトに配置される `.claude/skills/` インスタンス | 配布先プロジェクト内 |
| **D4** | **マスタ skill（メタスキル）** | **`.claude/skills/layerN-*` + `crosscut-*` のマスタ定義** | **dialog-harness リポジトリ内** |
| D5 | Meta モニタリング層 | D4 を外側から監視する人間 | リポジトリ外（人間の判断） |

機械可読命名は D-numbering（D1〜D5）を使用。
思想文書（`philosophy.md` / 本機構の `PHILOSOPHY.md`）でのみ「meta-layer」「meta-meta-layer」等の階層形容詞を併走させる二重命名を採用。

---

## 2. DH 本体（D4）の責務

| 責務 | スコープ |
|---|---|
| ユーザーハーネスを生成する | D2 / D3 を生み出す |
| 仕様策定の対話プロトコル | L0（spec-architect / onboarding） |
| AI 自律実装 | L1（autonomous-dev / independent-reviewer） |
| 大規模統括 | L2（orchestrator / integration-verifier） |
| 横断機構 | crosscut-* 系列（council / issue-dispatcher / issue-implementer / verifier-drift / verifier-philosophy / feedback-loop） |
| 生成物（D2 / D3）の検証 | §7.4 自己検証 / 5 層検出スタック / crosscut-verifier-drift |

**DH 本体は D4 自身の整合性を検査しない**。
これは v5.1.0 まで盲点だった。v5.2.0 で本機構が責務を引き受ける。

---

## 3. 本機構（harness-verifier）の責務

| 責務 | 検査対象 | 性格 |
|---|---|---|
| frontmatter 整合性 | 全 SKILL.md の name / description / 必須フィールド | linter |
| 参照 path 有効性 | references/ 相対パス + skill 間相対パスの dead link | 静的解析 |
| SK 間依存グラフ循環 | 関連スキル参照グラフの循環 | 静的解析 |
| 5 層構造保全 | `inferential-sensor-v2.md` 内の 5 層名と他 skill 引用の整合 | grep |
| 用語辞書整合 | `glossary.yml` 定義語の DH 全 skill 内での正しい使用 | grep + AST |

**全 5 項目は計算的検証のみ**。推論的検証（思想整合）は対象外。

---

## 4. 越境してはいけない領域

### 本機構が **やってはいけない** こと

| 禁止事項 | 理由 |
|---|---|
| DH 本体（D4）skill の自動修正 | 独立性要請違反。D5（人間）の判定領域 |
| crosscut-verifier-philosophy の責務（思想整合）の代行 | 計算的検証と推論的検証は別機構 |
| crosscut-verifier-drift の責務（生成物の SPEC drift）の代行 | D2 / D3 は本機構の対象外 |
| §7.4 自己検証の責務（個別プロジェクトの broken reference / smoke test）の代行 | 同上、対象次元が違う |
| DH 本体の skill を import / 呼び出し | 独立性要請違反（依存方向は一方向のみ） |
| GitHub Issue 自動作成 | crosscut-issue-dispatcher の責務、独立性要請違反 |
| ユーザーへのプロンプト出力 | 本機構は人間と直接対話しない（D5 が監視するのみ） |

### DH 本体（D4）が **やってはいけない** こと

| 禁止事項 | 理由 |
|---|---|
| `harness-verifier/` の skill 化（`.claude/skills/` 配下への移動） | 自己言及パラドックス再発、論理階層違反 |
| `harness-verifier/` を skill 内 references から参照 | 依存方向逆流、独立性要請違反 |
| `harness-verifier/` 検出結果に基づく自動改修 | D5 の領域への侵入、人間責務原則違反 |

---

## 5. 既存検証機構との責務マトリクス

DH には複数の検証機構が存在する。本機構との責務分離：

| 機構 | 対象次元 | 検査内容 | 起動条件 |
|---|---|---|---|
| 5 層検出スタック | D1 | 型 / lint / 単体 / E2E / 推論 | 利用者プロジェクトの CI |
| `crosscut-verifier-drift` | D2 + D3 | SPEC ↔ 実装 drift | 利用者プロジェクトの CI（CTL ≥ 1）|
| `crosscut-verifier-philosophy` (v5.3.0 候補) | D2 + D3 | philosophy.md 5 本柱整合 | 利用者プロジェクトの CI（CTL ≥ 2）|
| L0 §7.4 自己検証 | D2 | broken reference / smoke test / DONT 自己照合 / Pre-flight 充足 | L0 完了時 |
| **`harness-verifier/`（本機構）** | **D4** | **DH 本体の内部整合（5 項目）** | **dialog-harness リポジトリの CI（月次 + push/PR）** |

責務の重複なし。各機構が異なる次元 / 異なるタイミング / 異なる対象を担当する。

---

## 6. 5 層構造保全の D4 解釈（曖昧さ回避）

検証項目 4「5 層構造保全」は D2 と D4 の両解釈が可能だが、本機構では **D4 解釈** を採る。

### D2 解釈（本機構の対象外）

利用者プロジェクトに **5 層検出スタックが正しく植え付けられているか** の検証。
これは §7.4 自己検証 + crosscut-verifier-drift の責務。

### D4 解釈（本機構の対象）

DH 本体内で **`layer1-autonomous-dev/references/inferential-sensor-v2.md` 内の 5 層記述が他 skill の引用箇所と矛盾していないか** の検証。

具体例：
- `inferential-sensor-v2.md` で「型 / lint / 単体 / E2E / 推論」と定義
- 他 skill が「型 / lint / テスト / 統合 / 推論」と引用していたら矛盾検出
- grep + 用語辞書（`glossary.yml`）で照合

---

## 7. 依存方向

```
[harness-verifier/] ──読み取り──> [.claude/skills/**]
                                   [philosophy.md]
                                   [SPEC / DONT / REGIME 等]

逆方向の依存は禁止：
[.claude/skills/**] ──×──> [harness-verifier/]
```

`harness-verifier/` は DH 本体を **読み取り専用** で扱う。
DH 本体は `harness-verifier/` の存在を **知らない**（参照リンクなし、依存なし）。

例外: dialog-harness リポジトリのトップレベル `INDEX.md` から本機構を **紹介** する記述は許容（ナビゲーション目的、機能依存ではない）。

---

## 8. バージョニング

本機構（`harness-verifier/`）のバージョンは **DH 本体と独立** に進行する。

| 項目 | 値 |
|---|---|
| 本機構の初版 | v0.1.0（dialog-harness v5.2.0 で導入） |
| 連動するか | 連動しない（独立 semver） |
| バージョン記録場所 | `harness-verifier/README.md` 末尾 |

DH 本体が v5.x → v6.x に上がっても、本機構が v0.1.0 のままで機能し続けるなら本機構の昇格は不要。

---

## 9. 独立性の代償（subset YAML 制約、AD-014）

独立性要請（外部依存ゼロ、Python 標準ライブラリのみ）の代償として、`glossary.yml` は **subset YAML 形式** に限定する。一般の YAML 1.1/1.2 を網羅実装すると保守困難性が増し、再帰バグ（例: 複数行リスト構文の誤読）が周期的に発生するため。

### 制約内容

| 構文 | 対応 |
|---|---|
| `key: value`（key-value） | ○ |
| `key:` + 次行 indent でネスト dict 開始 | ○ |
| インラインリスト `[a, b, c]` | ○ |
| インライン list of dict `[{key: val}, {key: val}]` | ○（**1 行に収める**、複数行インラインも対応外） |
| 複数行 block list 構文 `- item` | **× 使用禁止**（パーサが SyntaxError を発生） |
| anchor (`&`) / merge (`<<`) / multi-document (`---`) / block scalar (`\|`/`>`) | × |

### 判断根拠

- C-1 (VERIFICATION-v5.2.0.md) で複数行 block list の誤読が判明し、検査 5 が空回りしていた事象を構造的に解消する
- 自前パーサの仕様明示化により、glossary.yml 編集時の誤りを **静的に検出可能**（開発者裁量で逸脱を許容しない）
- subset YAML の制約は `glossary.yml` 限定。本機構が読み取る他のファイル（`.claude/skills/**/*.md`）は通常の Markdown として扱う

### 違反時の挙動

`harness-verifier/checks/glossary.py` の `_parse_yaml` が複数行 block list を検出した時点で `SyntaxError` を raise。`verify.py` は exit code 2（検査機構自体のエラー）で終了する。

## 10. 改訂条件

本 BOUNDARY.md の改訂は **D5（人間）の判定** で行う。
本機構自身による改訂・DH 本体 skill による改訂は禁止。

改訂例：
- 新規検証項目の追加（5 → 6 項目）→ D5 判断で追記
- 既存検証項目のスコープ変更 → D5 判断で改訂
- 越境禁止事項の追加・緩和 → D5 判断で改訂
- subset YAML 制約の緩和（PyYAML 採用検討等）→ D5 判断 + Council 招集（独立性要請の解釈変更を伴うため）
