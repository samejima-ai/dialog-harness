# INTENT

DH 本体の設計意図・新規概念の記録。

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

4 仕様は同型構造（CTL 連動 / mode 別動作 / 還流ポイント明示）を持ち、5本柱 P1（フラクタル原則）を skill レベルで発現する。
