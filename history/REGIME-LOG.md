# REGIME-LOG

DH 本体のモード判定・major/minor 昇格の記録。

## v5.0.0（major 昇格、後方互換破壊あり）

- 判定日: 2026-04-27
- AI 能力バージョン: claude-opus-4-7
- 改修主体: layer0-spec-architect → layer1-autonomous-dev（M2 体制）
- spec 原典: `dh-upgrades/upgrade-spec-v5.0.0.md`（1500 行）
- 自己検証: `delivery/SELF-VERIFICATION-v5.0.0.md`

### 破壊項目（後方互換 break）

| 項目 | 旧 | 新 | 影響 |
|---|---|---|---|
| Level A skill 名 | `.claude/skills/council/` | `.claude/skills/crosscut-council/` | 既存プロジェクトの skill 参照が破壊。migration-guide で個別対応 |
| .gitignore 規約 | `council-workspace/` | `crosscut-council-workspace/` | 同上 |
| skill 命名規則 | `layerN-` のみ | `layerN-` + `crosscut-` | Level A 第二の prefix 確立 |
| バージョン記法 | `v4.0` 等の `vX.Y` | `v5.0.0` 等の semver 厳格 | v4.x 互換受理 |

### 非破壊追加

- L0 判定軸に dev_mode 追加（既存プロジェクトは local_only 相当として扱える）
- 5 つの crosscut skill 追加（local_only モードでは無視される）
- CTL 連動 protocol 追加（既存 CTL 計算ロジックの拡張、v4.2 互換）
- GitHub Actions 雛形 9 yml（templates/、採用は任意）
- `crosscut-council/references/ctl-maturity-strategy.md` 新規（既存 ctl-calculation.md と並列）
- philosophy.md は不変（パス参照のみ更新、思想本文は触らず）

### 移行方針

既存プロジェクト向けの移行手順は `docs/migration-guide-v5.0.0.md` を参照。

要約：
1. `.claude/skills/council/` → `.claude/skills/crosscut-council/` を git mv
2. 全 SKILL.md / references の `council/` パス参照を `crosscut-council/` に置換
3. `.gitignore` の `council-workspace/` を `crosscut-council-workspace/` に置換
4. REGIME.md に `## dev_mode` セクションを追加（local_only 相当を記録するだけで OK）
5. 必要に応じて `templates/.github/workflows/` をプロジェクトの `.github/workflows/` にコピー

DH 本体改修対象は本体配布元のみ（spec §1.4）。各既存プロジェクトの council/ 参照は本リリースでは触らない。

### 不変項目（spec §2 遵守確認）

| 不変項目 | 遵守状況 |
|---|---|
| 5本柱原則（P1-P5） | ○ |
| 履歴層規約 | ○（history/ 4 ファイルを v5.0.0 で初期化、形式は既存準拠） |
| 献上プロトコル | ○（`delivery/SELF-VERIFICATION-v5.0.0.md` 経由で献上） |
| Level A skill 本体不変 | ○（既存 layer skill は references 追記のみ、本体ロジック不変） |
| 継承禁止項目の指定自体 | ○（spec §2 を本ファイルで明示再掲） |
| 3層 + 1横断構造 | ○（crosscut- prefix の確立により構造を命名で明示化、L3 は新設しない） |

### モード判定（DH 本体自身）

DH 本体自身の REGIME.md は本改修スコープ外（メタ案件）。改修体制は以下：

- Mode: M2 標準（S=大、U=低、R=中、N=低、単一ドメイン、L2 閾値未達）
- 体制: L0（spec-architect）→ L1（autonomous-dev）+ layer1-independent-reviewer
- AI 能力バージョン: claude-opus-4-7

### 次バージョン予定

- v5.1.0: `crosscut-verifier-philosophy` 本実装（5本柱整合の自動検証）
- v5.x: チーム軸（T1-T5）operational 化（dev_mode 推論精度向上）
