# Upgrade Spec v5.21.0 — DH Self-Update Protocol（最小構成）

**リリース予定**: 2026-06-07
**バージョン昇格**: minor（v5.20.0 → v5.21.0、後方互換維持の追加のみ）
**起点**: ユーザー要請「既存プロジェクトの旧 DH をアップデートする方法／DH 側で更新方法を提供して参照させる策」

---

## §1 概要

既存プロジェクトの旧 DH を更新する際、これまで **DH 側に正典の更新手順が無く**、各プロジェクトが
手探りで再コピーしていた（boundary の推測ミス・in-progress master の混入・メジャー跨ぎの破壊など
落とし穴が各プロジェクトに分散）。

v5.21.0 は **DH 側が更新の boundary と手順を正典として提供**する最小構成を導入する。プロジェクトの
CC が DH リモートを参照したとき、これらを読めば安全に更新できる（単一情報源化）。

### 起点問題

- DH の配布は「コピー方式」だが、**何が DH 所有（差し替え可）で何がプロジェクト所有（保護）か**が
  README の install 例にしか暗黙化されておらず、機械可読でない。
- リリースタグが 0 個、`master` は in-progress 版を含むため、**ピン留めの指針が無い**。
- メジャー跨ぎ移行は `dh-upgrades/` にあるが、更新フロー全体を束ねる入口が無い。

---

## §2 scope（本 PR で実装）

| # | 成果物 | 役割 |
|---|---|---|
| 1 | `dh-manifest.yml`（新設） | DH 所有／プロジェクト所有の boundary を機械可読に正典化（overwrite / merge / redeploy / never_touch）|
| 2 | `VERSION`（新設） | 現行 DH バージョンの単一情報源（散在していた版表記の正典）|
| 3 | `UPDATE.md`（新設） | 更新の正典手順（ピン留め → sync → merge → redeploy → 検証 → 版記録、メジャー跨ぎ分岐）|
| 4 | `README.md` ポインタ | 更新時は UPDATE.md を参照する旨を追記 |
| 5 | 本 upgrade-spec / CHANGELOG | ガバナンス記録 |

### 設計判断

- **boundary は「sync（置換）」を既定**にする（merge ではなく）。skill の rename/削除（例 v5.0.0 の
  `council→crosscut-council`）が orphan として残らないようにするため。`overwrite` パスはディレクトリごと置換。
- **manifest は分類のみ・手順は持たない**（UPDATE.md と責務分離）。
- **ピン留めは commit SHA**（タグが無いため）。タグ運用は将来の改善として申し送り。

---

## §3 後方互換性

- 完全な**追加のみ**。既存 SKILL.md / references / workflow / 挙動は一切変更しない。
- 新規ファイル（`dh-manifest.yml` / `VERSION` / `UPDATE.md`）はプロジェクト更新時の `overwrite` 対象に
  含めない（DH リポジトリ自身のメタデータ。プロジェクトへはコピーしない運用）。
- LC ≥ 1 既存プロジェクトへの遡及適用は不要。

---

## §4 申し送り（v5.22.0 以降）

| 項目 | 理由 |
|---|---|
| `crosscut-dh-self-update` skill | 「DH を更新して」で起動する更新自動化（manifest 読込 → minor 自動 sync / major 移行誘導 → verifier 検証 → 版記録）|
| リリースタグ運用 | `<PIN>` をタグ（例 `v5.21.0`）にできるようにし、ピン留めを容易化 |
| `migrations.yml` | 版遷移 → 必要手順の索引（メジャー跨ぎ移行の自動チェーン化の素地）|
| harness-verifier ガード | 更新が `never_touch` を侵していないかの構造検査 |

---

## §5 関連

- `dh-manifest.yml` — boundary 正典
- `UPDATE.md` — 更新手順正典
- `dh-upgrades/upgrade-spec-v5.0.0.md` §既存DHからの移行 — メジャー跨ぎの先例
- `.claude/skills/crosscut-autonomous-drive/` — `redeploy` パス（workflow）の再展開主体
