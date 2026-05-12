# project-derived-councils — 利用者プロジェクト由来 COUNCIL ログのミラー

本フォルダ配下は **dialog-harness の利用者プロジェクト (D3 配備先) から献上された Council 判定ログ** のミラーを格納する。dialog-harness 自身の判定履歴である `history/COUNCIL-LOG.md` とは **論理的に独立した別系統**として扱う。

## 分離の論拠

- dialog-harness 自身の改修判定 (D4 マスタ skill の進化) と、利用者プロジェクトの運用判定 (D3 配備先での日々の判断) は、council `d4at01` 「S/U/R 独立維持」判定により **同じ S/U/R 軸では評価しない** ことが確定している
- council `l0agg1-4` (cross-project ログ集約設計) で確定済の **schema-only + 経路分離** 哲学に基づき、ファイル配置レベルで明示的に分離する (本フォルダ = project-scope、`history/COUNCIL-LOG.md` = user-scope DH 自身)
- `~/.claude/dh-data/` への user-scope schema-only push の本格実装 (council `l0agg4` D-2) は別サイクルで扱う。本フォルダはそれまでの **プロジェクト別ファイル配置による擬似実現 (MVP)** として機能する

## 分析時の取扱い

本フォルダ配下の COUNCIL-LOG ミラーを **dialog-harness 自身の改修統計と混ぜて集計してはならない**。具体的には：

| 用途 | 対象 |
|------|------|
| F1 (週次) / F2 (月次) / F3 (四半期) 振り返り儀式の DH 自身の改修動向集計 | `history/COUNCIL-LOG.md` **のみ** |
| council-weights 再校正の DH 自身の傾向反映 | `history/COUNCIL-LOG.md` **のみ** |
| 利用者プロジェクト由来の運用傾向観察 | 本フォルダ配下を **別軸で** 集計 |
| 全体動向のメタ観察 (将来需要が顕在化した場合) | DH 自身 + project-derived を **別軸として明示集計** (混合集計禁止) |

## 命名規約

```
history/project-derived-councils/<owner>-<repo>/COUNCIL-LOG.md
```

`<owner>-<repo>` は GitHub の owner/repo を `-` 連結したフォルダ名。プロジェクト識別子としては `samejima-ai/kakuman-platform-v3.0` → `kakuman-platform-v3.0` のように owner プレフィックスを省略してよい (同一 owner 配下の利用者プロジェクトに限定する運用前提)。

## append-only 規約

- 本フォルダ配下の COUNCIL-LOG.md は **kakuman 等 D3 側からの献上時点のスナップショット**である。DH 側で内容を編集してはならない (本リポジトリは読み取り保管のみ)
- 同名 D3 ファイルが更新された場合は、その時点の最新版でファイル全体を上書きする (本フォルダ配下ファイルの内部編集は禁止)
- ヘッダー注記 (献上元の ref / 取得日 / 重複の取扱い) はミラー時に毎回更新する

## harness-verifier との関係

`harness-verifier/verify.py` の検査 scope は `.claude/skills/` 配下に限定されており、`history/` 全体および本フォルダ配下はもとから検査対象外。本フォルダの追加で harness-verifier 設定の更新は不要 (scope は既に disjoint)。

## 関連

- `harness-verifier/BOUNDARY.md` §3 — harness-verifier の検査対象スコープ (`.claude/skills/` のみ)
- `history/COUNCIL-LOG.md` — DH 自身の council 履歴 (本フォルダと **混合禁止**)
- DH `.claude/skills/crosscut-council/SKILL.md` — Council 機構本体
- council `d4at01` (2026-04-30) — S/U/R 独立維持判定
- council `l0agg1-4` (2026-04-30) — cross-project ログ集約設計 (Push/Pull 経路分離 / schema-only / 共通ライブラリ)
