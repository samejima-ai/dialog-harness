# INTENT

DH 本体の設計意図・新規概念の記録。

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
