# ARCH-DECISIONS

DH 本体の設計判断の記録（ADR 軽量版）。

## v5.2.0

### AD-010: 5 次元論（D1〜D5）の導入と D-numbering 採用

| 項目 | 内容 |
|---|---|
| 状況 | DH の検証機構（5 層検出スタック / crosscut-verifier-drift / §7.4 自己検証等）が、それぞれどの抽象階層を対象にしているかが暗黙のままで、責務重複・責務漏れ判定が困難だった |
| 判断 | 5 次元論を導入：D1（ソースコード）/ D2（開発環境）/ D3（配布 skill インスタンス）/ D4（マスタ skill = メタスキル）/ D5（Meta モニタリング層 = 人間）。機械可読命名は D-numbering、思想文書では meta-layer / meta-meta-layer 等の階層形容詞を併走させる二重命名 |
| 根拠 | Council 合議（invocation_id: council-2026-04-29T21:00:00Z-d4mtr1, 論点 1）で D-numbering を recommended（judgment_confidence 0.78）。理由: (a) 既存 M1/M2/L0/L1/L2/CTL と prefix 衝突なし、(b) 短く grep 性能良好、(c) 案 b の T-numbering は既存予約のチーム軸 T1-T5 と衝突する致命的問題、(d) 案 c 階層形容詞は冗長で表記揺れリスク。哲学者の「関係性を呼び起こす命名は思想的支柱」少数意見を二重命名で吸収 |
| 影響 | layer0-spec-architect SKILL.md に v5.2.0 セクション追加、harness-verifier/PHILOSOPHY.md / BOUNDARY.md で 5 次元定義を明示。既存 skill の用語使用には影響なし |

### AD-011: D4 検査機構を DH 本体外（リポジトリルート直下）に独立配置

| 項目 | 内容 |
|---|---|
| 状況 | DH は生成物（D2/D3）の検証機構を完備していたが D4 自身の整合性検査が不在（靴屋の靴問題）。フラクタル原則 P1 の自然な拡張として「規律の自己相似性」を実装する必要があった。`.claude/skills/` 配下の crosscut-* skill として実装する案（crosscut-verifier-self-static 新設）と、DH 本体外に独立配置する案が拮抗 |
| 判断 | リポジトリルート直下 `harness-verifier/` に独立配置する。`.claude/skills/` 配下には置かない。`crosscut-verifier-drift` の拡張案も却下 |
| 根拠 | DH 内部 skill として実装すると自己言及パラドックス（自身が壊れたら自身を検査できない循環）が生じる。論理階層が一段違う（D4 vs D4 を検査する機構＝メタメタ層）ため Russell タイプ理論・Gödel 不完全性定理と同型の構造的回避が必要。HANDOFF §4.1 の特異点メタファに従う。Council 出力（案A: DH 内部 skill 新設）よりも哲学者の「特異点扱い」少数意見が、ユーザー確定の独立性要請（C: 一切影響されない独立性）と整合 |
| 影響 | 新規ディレクトリ `harness-verifier/` を作成。DH 本体（`.claude/skills/`）の挙動は完全不変。本機構は DH 本体に **読み取り専用** で依存（逆方向の依存は禁止） |

### AD-012: D4 検査機構の名称を `harness-verifier/` とする命名判断

| 項目 | 内容 |
|---|---|
| 状況 | HANDOFF 仮称 `self-monitoring/` は「self-」誤読リスク（自己が自己を監視＝独立性要請に反する読み）を持つ。命名候補: meta-verifier / harness-verifier / dh-integrity / singularity 等が拮抗 |
| 判断 | ディレクトリ名・機械可読名は `harness-verifier/` を採用。PHILOSOPHY.md 冒頭で「別名: singularity（特異点メタファ）」を併記する二重命名 |
| 根拠 | Council 合議（invocation_id 同上, 論点 2）で recommended（judgment_confidence 0.82）。理由: (a) `crosscut-verifier-drift` / `verifier-philosophy` と命名形式が同型でフラクタル原則 P1 整合、(b) 動詞由来（verifier）でファイル群の責務が明示、(c) grep 性能良好、(d) 外部説明コスト最小。哲学者の「singularity を命名で宣言する」少数意見は PHILOSOPHY.md 内で吸収 |
| 影響 | ディレクトリ名・コード・grep 対象では `harness-verifier` で統一。PHILOSOPHY.md においてのみ singularity 表記を保持 |

### AD-014: harness-verifier の glossary.yml を subset YAML 形式に限定する

| 項目 | 内容 |
|---|---|
| 状況 | 独立検証 (VERIFICATION-v5.2.0.md) で C-1 として、`harness-verifier/checks/glossary.py` の `_parse_yaml` が複数行 block list 構文 `- item` を誤読し、検査 5（用語辞書整合）が空回りしていた事象が判明。`forbidden_uses` の最初の要素消失、`crosscut_prefix.members` / `layern_prefix.members` の空 dict 化を確認 |
| 判断 | `glossary.yml` を **subset YAML 形式** に限定する。block list 構文を使用禁止とし、インライン list / list of dict のみ許容。パーサが block list 構文を検出した時点で `SyntaxError` を raise（黙って誤読しない）。BOUNDARY.md §9 に「独立性の代償」として明文化 |
| 根拠 | Council 合議（invocation_id: council-2026-04-29T22:30:00Z-c1fix1）で recommended（judgment_confidence 0.88）。3 ペルソナ全会一致で「案 b（インラインリスト書き換え）」を支持、開発者が「+ 案 a の防御コード」を補強、哲学者が「+ ドキュメント宣言」を補強する三段統合に着地。案 c（PyYAML 採用）は哲学者が「独立性要請の最初の妥協、5 本柱 P3（情報純度）侵食」と却下、本案件のスコープを越える BOUNDARY.md 改訂を要するため後送。subset YAML 制約により (i) C-1 即解消、(ii) 将来の偽陽性を構造的予防、(iii) 独立性要請の哲学的根拠強化を同時達成 |
| 影響 | `harness-verifier/glossary.yml` を subset YAML 形式に書き換え（forbidden_uses / members をインライン化）。`harness-verifier/checks/glossary.py` の `_parse_yaml` に block list 検出 → SyntaxError 機構を追加、加えてインライン list of dict 完全対応を含む全面改修（ネスト dict / quote 保持 / top-level split）。BOUNDARY.md §9「独立性の代償」を追加。glossary.yml 冒頭コメントで形式制約を明示。少数意見として「subset YAML が glossary 肥大化時に破綻したら PyYAML 採用を Council 再諮問」を温存 |

### AD-013: バージョン昇格を v5.2.0 minor とし philosophy verifier 本実装は v5.3.0 へ後送

| 項目 | 内容 |
|---|---|
| 状況 | 次元論導入 + D4 検査機構実装は (a) v5.2.0 minor / (b) v6.0.0 major / (c) v5.2.0 minor で次元論+D4 機構、philosophy verifier は v5.3.0 へ後送、の 3 案で拮抗 |
| 判断 | (c) v5.2.0 minor で次元論導入 + D4 検査機構（harness-verifier/）実装、`crosscut-verifier-philosophy` 本実装は v5.3.0 へ後送 |
| 根拠 | Council 合議（invocation_id 同上, 論点 3）で recommended（judgment_confidence 0.70）。理由: (a) 後方互換完全維持（新規ディレクトリ追加のみ、既存 SKILL.md / references / crosscut-* 不変）、(b) AD-008 / AD-009 の前例（後方互換維持で minor）と整合、(c) 開発者の semver 厳格論と経営者のリリース文脈説明可能性を両立。哲学者の「次元論導入は major 級の自己同定更新」少数意見は v6.0.0 で philosophy.md 第 7 条として吸収する候補として保持 |
| 影響 | v5.1.0 → v5.2.0、後方互換維持。`crosscut-verifier-philosophy/` placeholder は v5.2.0 でも未実装のまま、v5.3.0 候補として継続検討 |

## v5.1.0

### AD-008: L0 完了の定義をドキュメント生成完了から「scaffold smoke test 通過 + 受け入れ基準充足」へ再定義

| 項目 | 内容 |
|---|---|
| 状況 | PR #19 テストレビュー（シナリオ「ケロぴの森」）で L0 が SPEC.md / DONT.md / REGIME.md の生成は完遂したが、L1 が即座に開発開始できる scaffold が一切生成されず、参照ファイル 8 種も未読のまま L0 完了と判定されていた。L0 charter「AI 自律駆動開発が可能な開発環境の構築」が達成不能 |
| 判断 | L0 完了の定義を「ドキュメント生成完了」から「§0 受け入れ基準 4 条件すべて充足（仕様充足 / scaffold 実体生成 / smoke test 通過または保留事由明記 / §7.4 自己検証 PASS）」に再定義する |
| 根拠 | 5 本柱原則 P3（責務分離）と P4（情報純度）に整合。L0 が「実行可能な開発環境を作る」という charter を満たさないまま L1 へ譲渡することは責務不履行であり、人間 ≒ Council 原則（philosophy.md 第6条）の観点でも検証層の前段で受け入れ基準を確定する必要がある |
| 影響 | SKILL.md §0 に受け入れ基準セクションを追加。Lifecycle ≥ 1 既存プロジェクトには段階適用とし、既存成果物の遡及修正は要求しない（後方互換維持） |

### AD-009: scaffold-checklist の単一 stack（Vite+TS+React+PWA）採用方針

| 項目 | 内容 |
|---|---|
| 状況 | scaffold-checklist.md を新設するにあたり、複数 stack を初期から網羅するか単一 stack に絞るかを判断する必要があった |
| 判断 | v5.1.0 では Vite + TypeScript + React + PWA の **1 stack に絞る**。他 stack（Next.js / Vue / Astro / SvelteKit / 純 Node CLI）は将来 minor で追加 |
| 根拠 | (a) PR #19 テストレビュー対象が M2 monolith Web PWA で本 stack に直結する、(b) scaffold-checklist は「実体ファイルの厳密な必須リスト」が責務であり、stack ごとに必須要件が異なるため網羅は本リリース範囲を逸脱、(c) 利用者数が多い stack を一つ確定させてから stack 別の最小要件パターンを抽出するほうが将来 minor の品質が上がる |
| 影響 | 他 stack を使う既存プロジェクトでは scaffold-checklist の対象外となるが、§0 受け入れ基準 2「対応 stack テンプレートで指示されたファイル群」と表現することで「対応 stack なし → 該当条項は適用対象外」と扱える。将来 minor で stack 追加時は scaffold-checklist 内の「将来拡張ポイント」表に従う |

## v5.0.0

### AD-001: crosscut- prefix の導入

| 項目 | 内容 |
|---|---|
| 状況 | council/ は「全 Layer 横断」の判定機構だが、命名が層構造を示していなかった |
| 判断 | `crosscut-` prefix を Level A skill の第二の命名規則として確立し、`council/` を `crosscut-council/` にリネーム |
| 根拠 | spec §3.1.3 / §4.1。3 層 + 1 横断の構造を命名で明示化、フラクタル原則 P1 に整合 |
| 影響 | 後方互換破壊（major 昇格）。既存プロジェクト側の参照は migration-guide で個別対応 |

### AD-002: dev_mode 軸の追加

| 項目 | 内容 |
|---|---|
| 状況 | 既存軸（規模 S / 不確実性 U / リスク R / NFR N / Lifecycle）に GitHub 連携前提の判定軸が無かった |
| 判断 | dev_mode 軸（local_only / github_assisted / github_autonomous）を 3 軸目の動的判定軸として追加 |
| 根拠 | spec §3.2.1〜§3.2.3。GitHub 無しでも DH ベースは完全動作の原則を保ちつつ段階的移行を可能にする |
| 影響 | regime-assessment.md / REGIME.md テンプレ拡張。後方互換あり（既存プロジェクトは local_only 相当として扱える） |

### AD-003: 仕様 1〜4 を crosscut- skill 化

| 項目 | 内容 |
|---|---|
| 状況 | GitHub 連携の 4 仕様（Issue 射出・実装・検証・還流）は L0/L1/L2 のいずれにも純粋には属さず、横断的に発動する |
| 判断 | 仕様 1〜4 を `crosscut-issue-dispatcher` / `crosscut-issue-implementer` / `crosscut-verifier-drift` / `crosscut-verifier-philosophy` (placeholder) / `crosscut-feedback-loop` の 5 skill として配置 |
| 根拠 | spec §4.3。3 層 + 1 横断構造の維持、責務分離（P3）、各 skill の同型構造によるフラクタル原則発現 |
| 影響 | 新規 skill 5 件追加。layer1-* から参照を追加、既存 layer 機構は不変 |

### AD-004: CTL 連動条件分岐の組み込み

| 項目 | 内容 |
|---|---|
| 状況 | CTL システム（v4.2 で追加）は判定ロジックは存在したが、各 skill の動作分岐に組み込まれていなかった |
| 判断 | 仕様 1〜4 すべての protocol references で CTL-0/1/2/3 の段階的自動化を明文化 |
| 根拠 | spec §3.2.4〜§3.2.7、§4.4。再帰進化原則 P2 を CTL 育成戦略として実装 |
| 影響 | 各 crosscut- skill 配下に protocol.md を追加。CTL 育成戦略は ctl-maturity-strategy.md として独立 |

### AD-005: claude-code-action 公式採用

| 項目 | 内容 |
|---|---|
| 状況 | Issue → 実装の自動化手段として複数選択肢があった |
| 判断 | Anthropic 公式の claude-code-action を採用、GitHub Actions 雛形に組み込み |
| 根拠 | spec §3.2.5、§3.2.9。業界 BP 取り込み、保守性、エコシステム整合性 |
| 影響 | templates/.github/workflows/issue-to-impl.yml の依存。バージョンは `<latest>` プレースホルダ（実装時点で公式リポジトリ確認） |

### AD-007: docs/ ディレクトリの限定許可

| 項目 | 内容 |
|---|---|
| 状況 | リポジトリは "skill-only policy" (PR #3) で `docs/` を gitignore 済み。spec §5.4.2 が `docs/migration-guide-v5.0.0.md` を v5.0.0 配布物として要求 |
| 判断 | `docs/` 全体の gitignore は維持しつつ、配布対象の migration guide のみを許可（`!docs/migration-guide-*.md`） |
| 根拠 | 設計ドラフト（drafts policy）と配布ドキュメント（migration guide）は性質が異なる。最小例外で skill-only policy の精神を保つ |
| 影響 | `.gitignore` 1 行追加。今後の v6.0.0 以降の migration guide も同パターンで許可される |

### AD-006: README バッジ作業のスキップ（適用対象外）

| 項目 | 内容 |
|---|---|
| 状況 | spec §4.6.2.4 で README に v5.0.0 バッジを追加する指示があるが、リポジトリルートに README.md が存在しない |
| 判断 | README バッジ追加作業はスキップ。SKILL.md バージョン履歴 / credit-template.md / REGIME-LOG.md でバージョン更新を完結させる |
| 根拠 | スキルは SKILL.md の frontmatter + 本文が標準。README は人間向けプロジェクト紹介で本案件のスコープ外。SELF-VERIFICATION §5.3.2 で「適用対象外」明記 |
| 影響 | バージョン更新は他経路で完結。README 整備は別案件として保留 |
