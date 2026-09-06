# DH 更新プロトコル（既存プロジェクトの旧 DH を更新する正典手順）

> このドキュメントは **DH 側が提供する正典の更新手順**。既存プロジェクトの CC（Claude Code）が
> DH リモートを参照して更新するとき、**本ファイルと `dh-manifest.yml` に従えば安全に更新できる**。
> 各プロジェクトが手順を再発明しなくてよいようにするのが目的（単一情報源）。
>
> 関連: 配布 boundary は `dh-manifest.yml`、現行版は `VERSION`、メジャー移行経路は `dh-upgrades/`。

---

## 0. 前提と原則

- **配布＝コピー方式**: DH はパッケージマネージャや submodule ではなく、フレームワーク部を
  プロジェクトへコピーして導入する。更新も「新しい DH の DH 所有物を再 sync する」だけ。
- **boundary は推測しない**: 何を上書きし何を保護するかは `dh-manifest.yml` が正典（§2）。
- **同一メジャー内は後方互換**: v5.x → v5.y は追加のみ。再 sync で安全。メジャー跨ぎ（v4 以前→v5）だけ
  個別移行が要る（§4）。
- **移行の決定はプロジェクト個別判断**: DH は手順を**提供**するが、メジャー跨ぎの適用是非は各プロジェクトが判断する。

---

## 1. ピン留め（最初に必ず）

DH には現状リリースタグが無く、`master` HEAD は **開発途中状態（in progress 版）を含む**。
更新先を**特定の commit SHA に固定**して、全プロジェクトを同じ版に揃える。

```bash
# DH リモートを参照（一意な一時ディレクトリへ clone）。<PIN> は更新時に決めた DH の commit SHA
DH=$(mktemp -d)
trap 'rm -rf "$DH"' EXIT   # 手順終了時に一時 clone を後始末（/tmp を汚さない・繰り返し実行可）
git clone https://github.com/samejima-ai/dialog-harness "$DH" && git -C "$DH" checkout <PIN>
cat "$DH/VERSION"          # 更新先バージョンを確認
cat "$DH/dh-manifest.yml"  # boundary を確認
```

> 注: `trap ... EXIT` で `$DH` を消すため、§2 以降を**同一シェルセッション**で続けて実行すること
> （別セッションに分ける場合は trap を外し、§5 完了後に手動で `rm -rf "$DH"`）。

> DH 側がリリースタグ運用を始めたら `<PIN>` をタグ（例 `v5.21.0`）にできる（推奨・将来）。

---

## 2. プロジェクト側で更新を実行（同一メジャー内）

`dh-manifest.yml` の分類どおりに処理する。**後続の `rm -rf` は破壊的なので、復旧点の確保を必須化する**。

```bash
cd <your-project>
# 破壊的更新の前に必ず復旧点を確保する。git 管理下必須 / 変更なしはスキップ / commit 失敗は中断。
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "git 管理下で実行すること（ロールバック点が作れない）"; exit 1; }
git add -A
if git diff --cached --quiet; then
  echo "（変更なし＝直前の commit が復旧点）"
else
  git commit -m "pre-DH-update snapshot" || { echo "snapshot commit 失敗（git user.name/email 等を確認）。破壊的更新を中断。"; exit 1; }
fi

# (a) overwrite: DH 所有 → **列挙された dir 単位**で sync（置換）。
#     merge ではなく置換にするのは rename/削除（例 council→crosscut-council）を orphan にしないため。
#     **`.claude/skills/` を丸ごと置換してはならない**（v6.17.0 F4 / Council D-4）。同 dir には
#     利用者プロジェクトの固有 skill（Level B）が同居しており、丸ごと置換すると消える。
#     置換する skill は dh-manifest.yml の `paths.owned_skills` が正典（prefix で判定しない —
#     DH 配布の rtk-integration が layer/crosscut prefix を持たず破れる）。
python3 - "$DH" <<'PY'
import re, shutil, sys
from pathlib import Path

dh = Path(sys.argv[1])
manifest = (dh / "dh-manifest.yml").read_text(encoding="utf-8")

# paths.owned_skills を読む（インデント 2 の分類名 + インデント 4 以上の "- 値"）
owned, cur = [], None
in_paths = False
for raw in manifest.splitlines():
    if raw.startswith("paths:"):
        in_paths = True; continue
    if not in_paths: continue
    if raw.strip() and not raw.startswith(" ") and not raw.startswith("#"): break
    s = raw.strip()
    if not s or s.startswith("#"): continue
    indent = len(raw) - len(raw.lstrip(" "))
    if indent == 2 and s.endswith(":"): cur = s[:-1]
    elif indent >= 4 and s.startswith("- ") and cur == "owned_skills":
        owned.append(s[2:].split("#", 1)[0].strip().strip('"').strip("'"))

if not owned:
    sys.exit("owned_skills が読めない。dh-manifest.yml を確認して中断")

dst_root = Path(".claude/skills")
dst_root.mkdir(parents=True, exist_ok=True)
for name in owned:
    src = dh / ".claude" / "skills" / name
    if not src.is_dir():
        print(f"  skip（DH 側に無い）: {name}"); continue
    dst = dst_root / name
    if dst.exists(): shutil.rmtree(dst)   # dir 単位の置換 = orphan を残さない
    shutil.copytree(src, dst)
    print(f"  synced: {name}")

kept = sorted(d.name for d in dst_root.iterdir() if d.is_dir() and d.name not in owned)
print(f"\nDH 所有 {len(owned)} dir を同期。プロジェクト固有 skill {len(kept)} dir は保全: {', '.join(kept) or '(なし)'}")
PY

rm -rf templates && cp -r "$DH/templates" ./

#     `.claude/agents/` も DH 所有。改行コードが DH 側 CRLF / 配布先 LF で分かれるため、
#     差分確認は改行を正規化してから行う（byte 比較は全ファイルを差分に見せる）。
rm -rf .claude/agents && cp -r "$DH/.claude/agents" .claude/

# (b) merge: プロジェクトがカスタムしうる → 差分を見て手動マージ（raw 上書き禁止）。
#     diff は「差分なし=exit0 / 差分あり=exit1」。両分岐を明示:
diff -u .claude/settings.json "$DH/.claude/settings.json" && echo "（差分なし・マージ不要）" || echo "↑ 上記差分を手動マージ（raw 上書き禁止。hooks キーは DH 提供、他キーは利用者固有）"
diff -u .gitignore "$DH/.gitignore" && echo "（差分なし・マージ不要）" || echo "↑ 上記差分を手動マージ（追記マージ。上書きすると利用者の除外行が消える）"

# (c) redeploy: placeholder を含む → raw コピー不可。crosscut-autonomous-drive で再展開。
#     CC に「autonomous-drive で workflow を再 deploy（placeholder 再展開・衝突は確認）」と指示。

# (d) never_touch: SPEC/DONT/REGIME/CLAUDE/history/delivery/.claude/disabled/ と自コードは触らない。
#     **overwrite と never_touch が同一パスにマッチする場合は never_touch が勝つ**（v6.17.0 F3 / D-3）。
#     例: `.claude/skills/crosscut-council/history/` は owned_skills 配下だが `history/` にも該当し、
#     配布対象から外れる。迷ったら配らない・触らない。
```

> **Level B（プロジェクト固有 skill）は規格上の同居である**（v5.0.0 の決定）。上記 (a) の選択同期は
> `paths.owned_skills` に列挙された DH 所有 dir だけを置換するため、固有 skill は保全される。
> v6.17.0 以前の手順（`rm -rf .claude/skills`）は固有 skill を消すため**使ってはならない**。
> 実運用は同期 8 回すべて選択同期に逃げており、旧手順は一度も使われていなかった（D-4 がこれを正典化した）。

---

## 3. バージョン記録

更新後、プロジェクトの `REGIME.md` に更新先バージョンと PIN を記録する（次回更新の起点になる）。
見出しレベル（`##`/`###`）は REGIME.md の既存構成に合わせてよい（衝突回避）。

```
### DH バージョン
- updated_to: 5.22.0
- pinned_sha: <PIN>
- updated_at: <date>
```

### 既知の番号のズレ（2026-09-05 の一度きり）

**2026-09-05 以前に配布されたツリーが名乗る `6.11.0` は、実際には後の v6.12.0 / v6.15.0 相当の内容を含みうる。**

DH は 2026-08-15 の `VERSION` = 6.11.0 以降、昇格の契機を定めないまま実装だけが master に入り続けた
（PR #191 / #203 / #206 / #207 / #217 / #221 / #223）。2026-09-05 に v6.17.0 F1 で昇格規則を定め、
実態に合わせて `VERSION` を **6.11.0 → 6.15.0** へ一度だけまとめて昇格させた。

- **この読み替えが要るのは 2026-09-05 より前に配布されたツリーだけ**である。以後は
  「merge 時に上げる・遡及しない」（`dev-env-spec.md` §昇格の契機）ため、同種のズレは起きない
- **正確な内容の同一性は版番号ではなく `pinned_sha` で判定すること**。上記期間のツリーについては
  版番号は「約束の区切り」の目安にすぎない

---

## 4. メジャー跨ぎ（v4 以前 → v5）の場合

`dh-manifest.yml` の `min_same_major_from` より前のプロジェクトは**後方互換破壊あり**。
§2 の素朴な再 sync では壊れる。該当メジャーの `dh-upgrades/upgrade-spec-vX.0.0.md` の
**移行経路**に従う（例 v5.0.0: `council/` → `crosscut-council/` 配置換え、不要要素は削除でなく
`.claude/disabled/` へ退避、各段階で動く状態を保つ段階的移行）。

> upgrade-spec の注意どおり「設計意図を理解せずに手順だけ実行は禁止」。メジャー跨ぎは個別判断。

---

## 5. 更新後の検証（必須）

- `harness-verifier` を実行して構造健全性を確認
- 振り返り儀式（LC ≥ 1 なら）で文脈整合を確認
- `dh-manifest.yml` の `never_touch` が侵されていないか（SPEC/REGIME/history 等が無傷か）を確認

問題があれば §2 冒頭の pre-update commit に `git reset --hard` で戻す。

---

## 6. 将来の自動化（申し送り）

本プロトコルを skill 化した `crosscut-dh-self-update`（「DH を更新して」で起動 → manifest 読込 →
minor 自動 sync / major 移行誘導 → verifier 検証 → バージョン記録）を v5.22.0 以降で検討。
リリースタグ運用・`migrations.yml`（版遷移→手順の索引）も併せて。
