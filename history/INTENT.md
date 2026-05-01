# INTENT

DH 本体の設計意図・新規概念の記録。

## 保留中の長期計画

### CI/CD 強化計画（2026-05-01 開始、保留中）

- **起源**: 下流プロジェクト（Next.js + Supabase 系、`apps/platform` 等を持つ dev_mode=github_assisted 確定済プロジェクト）からの献上ブレスト
- **保管場所**: `history/deliveries/2026-05-01-cicd-automation-brainstorm.md`
- **DH 一般化候補**: 10 カテゴリ × 多数選択肢のうち、DH 本体に一般化可能な議題を以下 5 つに集約
  1. **scaffold-checklist の CI 章追加**: `.github/workflows/ci.yml` 雛形（typecheck + lint + test の PR ゲート）を v5.1.0 標準 stack の必須生成ファイルに加える案
  2. **crosscut-* 段階稼働プロトコル**: 未稼働の dispatcher / implementer / drift / feedback-loop について dev_mode × CTL ごとの推奨稼働順を reference 化する案
  3. **「罠 → 検出器」一般化パターン**: プロジェクト固有の踏みやすい誤りを DONT.md に言語化し sensors/computational.md へ lint として載せる汎用フローを reference 化する案
  4. **自動化 LOC 予算ガイダンス**: 1 自動化 = 1 ファイル 200 行未満、自動化総量の本体 LOC × 1.5 上限等のガイダンスを philosophy or dev-env-spec に追加する案（Bus factor 軽減）
  5. **sensor 自動実行化**: markdown 手順書としての sensor を実行可能スクリプト化し VERIFICATION.md に machine-readable 結果を残す案
- **未消化の 7 質問（ブレスト原文 §5）**:
  - Q1 テストフレームワーク方針（Vitest / Playwright / Cucumber の 3 層採否）
  - Q2 自動化 LOC 上限の基準
  - Q3 crosscut-* 稼働順序
  - Q4 罠検出器の SPEC / docs / DONT 振り分け
  - Q5 production 切替と down migration（プロジェクト固有、DH 採用外）
  - Q6 Bus factor 対策と自動化増加の逆説
  - Q7 v5.2.0/v5.3.0 で送られた philosophy verifier の取り扱い（既決：v5.3.0 候補から外し継続検討）
- **保留理由**: 起点プロジェクトおよび harness 利用者側で「CI/CD で何のどこをチェックするか」の認識共有が未達。L0 spec-architect 原則「認識のズレがゼロになるまでレビューループを回す」に従い、ズレが残ったままの開発環境構築を避ける
- **次サイクル発動条件**:
  - (a) 利用者プロジェクト側で CI/CD の対象範囲（typecheck / lint / unit / E2E / drift / 罠検出 のいずれか以上）を具体化した HANDOFF が届く、または
  - (b) PR #30（v5.4.0 archeo-architect）merge 後の安定期に DH 本体側でドッグフード対象として再起動
- **PR #30 との関係**: 本計画は PR #30 と独立。両者ともに `history/INTENT.md` と他ファイルを触る場合は merge 後 rebase で整合させる。本サイクルでは PR #30 が予約した v5.4.0 を侵さないため版上げを行わない
- **当面のリリース対象**: なし（記録のみ）。実体改修は次サイクル以降の minor or 別 PR に委ねる

## v5.3.0 で追加された概念

### 1 機能完遂の自律駆動 WF を「形状単一・薄い基底」として確定

HANDOFF「1 機能完遂の自律駆動 WF 設計」2026-04-30 を起源とする L0 設計判断。
論点 1（WF 基底）/ 論点 2（献上トリガー 4 種）/ 論点 3（WF 選択責任）の 3 件を
Council 合議 (`council-2026-04-30T14:30:00Z-wfsurf1` / `council-2026-04-30T14:50:00Z-wfbase1`) と
実装者裁量（論点 3）で確定し、AD-015 / AD-016 / AD-017 に記録した。

設計意図の核：

**(a) 機能タイプ別 WF 群を作らない**。bug-fix / 新規機能 / リファクタ / 仕様改訂等は
`.claude/skills/layer1-autonomous-dev/SKILL.md` §4「実装タスク分解」内で扱う context 差異であって、独立 WF を生成する分業軸ではない。
これは philosophy.md §1 フラクタル原則 P1（同型再帰）が要求する「形状単一性」を運用原則として
組み込む判断である。職種別分業（フロント/バック/SRE 等）が職能のサイロ化を生むのと同型に、
機能タイプ別 WF 群は 5 年スパンで「タイプ N+1 の追加要求」を再発させる罠を持つ。
当面は単一 WF + 動的 context 注入で吸収し、観測（同一 override パターンの 3 機能タイプ以上での
反復）が閾値を超えた場合のみ Council 経由で基底側引き上げを再諮問する。

**(b) 既存 §処理フローが thin baseline を充足している**。
`layer1-autonomous-dev/SKILL.md §処理フロー（1〜8）` は HANDOFF が要求する「薄い基底」を
既に満たしている。新規 WF テンプレートを追加しない判断は、既存実装への信頼の表明であり、
かつ YAGNI 原則と整合する。

**(c) 献上経路を 4 分類化して情報純度を上げる**。
従来 Type A（仕様レビュー結果）に詰め込まれていた「AI 自己解決不能な技術的例外」を
Type D（異常献上）として分離する。仕様起因（Type A → L0 差し戻し）と
技術例外（Type D → 人間判断要請）は本質的に異なる救済経路であり、混同は P3 責務分離違反。

**(d) WF 選択責任は問題化しない**。
WF が単一形状で確定したため、「どの WF を起動するか」という選択問題が構造的に消失する。
残課題（機能タイプ誤認 / モード誤判定 / 権限・CTL 誤り）はすべて既存メカニズム
（Type C / 体制事後評価 / Type D）で吸収可能。新規ディスパッチャ等は不要。

### v6.0.0 候補として温存される思想拡張

論点 1 で哲学者が提示した第 3 の道「**単一 WF + 動的 context 注入**」を、現行 v5.3.0 の
運用原則を超える形での実装案として v6.0.0 major 候補に温存する。これは context engineering
の中核に WF 設計を据え直す思想転換であり、minor 改修では実装し得ない。

論点 2 で哲学者が提示した「**献上 3 軸構造**（トリガー × 中身 × 権限）」を philosophy 第 8 条
候補（第 7 条＝次元論と D4 の独立性 と並列の「献上 3 軸の存在論」）として温存する。
Type D 単純追加は二項分類の罠（Type E/F/G の追加要求が将来再発する可能性）を構造的に
解消できないため、3 軸構造への昇格を v6.0.0 major 昇格時に併合検討する。

## v5.2.0 で追加された概念

### 5 次元論（D1〜D5）の確立

dialog-harness は従来「メタスキル」「ユーザーハーネス」等の語彙で自身を語ってきたが、
個別の検証機構（5 層検出スタック / crosscut-verifier-drift / §7.4 自己検証等）が
それぞれどの抽象階層を対象にしているかが暗黙のままだった。

PR #19 後の HANDOFF（DH 自己検証機構ブレスト、2026-04-29）と Council 合議
（invocation_id: council-2026-04-29T21:00:00Z-d4mtr1）を経て、5 次元論を確立する：

| 次元 | 名称 | 実体 |
|---|---|---|
| D1 | ソースコード | プロジェクト実装ファイル群 |
| D2 | 開発環境 | D1 の足場（package.json / vite.config / sensors / SPEC.md 等） |
| D3 | 配布 skill | 利用者プロジェクトに配置される `.claude/skills/` インスタンス |
| **D4** | **マスタ skill（メタスキル）** | **dialog-harness リポジトリ内 skill マスタ定義** |
| D5 | Meta モニタリング層 | D4 を外側から監視する人間（自動化禁止） |

機械可読命名は D-numbering（D1〜D5）を使用。思想文書では `meta-layer` / `meta-meta-layer`
等の階層形容詞を併走させる二重命名を採用（DH の二層性 = 仕様核 + 対話的成長領域 と整合）。

### D4 検査機構（harness-verifier）の独立配置

DH 本体は v5.1.0 まで D2 / D3 の検証機構を完備していたが、**D4 自身の整合性検査は不在**だった
（靴屋の靴問題）。フラクタル原則 P1 の自然な拡張として「規律の自己相似性」を導入し、
DH が自身に課す規律と同等の規律を自身に課す。

ただし D4 検査機構を `.claude/skills/` 配下の crosscut-* skill として実装すると
**自己言及パラドックス**（自身が壊れたら自身を検査できない循環）が生じる。
これを構造的に回避するため、**DH 本体と並列のリポジトリルート直下に独立配置**する：

```
dialog-harness/
├── .claude/skills/    # DH 本体（D4）
└── harness-verifier/  # D4 検査機構（独立）
```

### 自己言及パラドックスの構造的回避（D5 を人間で止める）

D4 検査機構（harness-verifier）の検査結果を **自動的に DH 本体へフィードバックする回路は意図的に作らない**。
そこを自動化すると、D4 と D5 の間に新たな自己言及ループが発生し、再びパラドックスに陥る。
D5（人間）は機械が代替できない判定者として最外殻に固定される。
これは Russell タイプ理論・Gödel 不完全性定理と同型の構造判断であり、
philosophy.md 第 6 条「人間 ≒ Council」原則とも整合する。

将来 v6.0.0 で major 昇格する際、philosophy.md 第 7 条「次元論と D4 の独立性」として
本体に組み込む候補（v5.2.0 では PHILOSOPHY.md に閉じる）。

## v5.1.0 で追加された概念

### L0 charter 達成可能性の確保

PR #19 テストレビュー（シナリオ「ケロぴの森」）で、L0（spec-architect）の charter「AI 自律駆動開発が可能な開発環境の構築」が達成されないまま L1 へ譲渡され得る状態が判明した。SPEC.md / DONT.md / REGIME.md のドキュメント生成だけが完了し、scaffold（package.json 等の実行可能ファイル）が一切生成されない状態でも、従来の L0 完了判定では PASS となっていた。

v5.1.0 はこの欠陥を「**完了基準の再定義**」と「**Pre-flight 必読化**」と「**実行可能性の機械チェック（§7.4）**」の 3 軸で解消する。L0 完了 = ドキュメント生成 + scaffold 実体 + smoke test + 自己検証 PASS。これを下回る状態で L1 譲渡することは原則違反として明文化された。

### Pre-flight 必読化（読まずに進行禁止）

従来の SKILL.md は「詳細は references/X.md を参照」という参照表現にとどまっていた。v5.1.0 では主要ステップ（§1.5 / §3.5 / §4 / §6 / §7）の冒頭に「**Pre-flight: 起動前に X を必読**」を 1 行ずつ追加した。これは spec §0 受け入れ基準 4 とリンクし、Pre-flight 充足は §7.4 で逐項チェックされる。

「参照」と「必読」の差は運用上致命的。AI が SKILL.md だけを読んで進む（references を読み飛ばす）パターンを排除する目的で、命令形 + 違反明記 + 自己検証チェック項目化、の 3 点セットで運用する。

### Scaffold checklist（stack 別の生成必須リスト）

dev-env-spec.md は「ファイル配置規則」（全 stack 共通の規約）を扱うが、stack 固有の必須生成ファイルリストと smoke test 手順は不在だった。v5.1.0 では references/scaffold-checklist.md を新設し、「v5.1.0 標準 stack = Vite + TypeScript + React + PWA」の必須生成ファイル 12 種と smoke test 4 コマンドを規定する。

将来 minor で stack 追加（Next.js / Vue / Astro / SvelteKit / 純 Node CLI 等）するための「将来拡張ポイント」も併記。stack 選択軸は ARC + dev_mode + チーム軸（v5.x で追加予定）と整合させる。

### §7.4 自己検証ステップ

L0 完了判定の機械チェック化。broken reference / scaffold smoke test / DONT 自己照合 / Pre-flight 充足 / 受け入れ基準充足の 5 項目をチェックボックス形式で配置。FAIL があれば §7（出力）に進まず原因解消する。shell script 雛形は配置せず、L0 が ls / grep / cat 等の手作業で確認する粒度に絞ることで、人間運用の前提（人間は手を動かさない）を破らない。

5 項目は §0 受け入れ基準 4 条件と一対一に対応するように設計され、「自己検証で何をチェックすべきか」の暗黙仕様を明示化した。

## v5.0.0 で追加された概念

### dev_mode 軸

GitHub 連携前提の自律駆動開発を 3 段階で表現する軸。

| モード | 位置づけ |
|---|---|
| local_only | GitHub 不使用。DH ベースのみで完結 |
| github_assisted | GitHub Issue / PR は使うが、自動化は限定的。人間レビュー必須 |
| github_autonomous | claude-code-action 経由で自律実装、CTL 育成と連動して段階的に人間関与を縮小 |

理想形は github_autonomous + CTL-3 で「人間関与は L0 のみ」。

### CTL 連動の段階的自動化

仕様 1〜4 すべてに CTL-0/1/2/3 の動作分岐を組み込み、Council 判定の蓄積に応じて自動化度が上がる仕組み。CTL 昇格は量（判定件数）+ 質（一致率・override 率）のハイブリッド判定。退行（CTL 降格）も儀式で扱う。

### crosscut- prefix（Level A 第二の命名規則）

`layerN-` prefix と並列の Level A 識別子。3 層（L0/L1/L2）のいずれにも属さず、全層から呼ばれる横断機構を示す。

| Level A prefix | 意味 |
|---|---|
| `layerN-` | 特定 Layer 専属 skill |
| `crosscut-` | 全 Layer 横断 skill |

### 4 仕様（GitHub 連携の方法論化）

| 仕様 | skill | 役割 |
|---|---|---|
| 仕様 1 | crosscut-issue-dispatcher | SPEC/ADR 差分から Issue 生成 |
| 仕様 2 | crosscut-issue-implementer | Issue → CC 実装起動（claude-code-action 経由可） |
| 仕様 3 | crosscut-verifier-drift / -philosophy | drift 検知 + 思想検証（philosophy は v5.1.0 placeholder） |
| 仕様 4 | crosscut-feedback-loop | 検証結果を設計層・実装層・L0 に還流 |

4 仕様は同型構造（CTL 連動 / mode 別動作 / 還流ポイント明示）を持ち、5 本柱 P1（フラクタル原則）を skill レベルで発現する。
