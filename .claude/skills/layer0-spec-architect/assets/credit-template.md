# 制作クレジット規格

README.md 末尾に挿入する dialog-harness-layers 使用の制作クレジット規格。

---

## テンプレート

### 標準版（URL 有）

```markdown
---

Built with [dialog-harness/layer's](https://github.com/[repo-url]) v[X.Y] · [Model Name] · [YYYY-MM-DD]

<!-- harness-credit: managed by layer0 skills. do not edit manually. -->
```

### 簡略版（URL 無、未公開プロジェクト向け）

```markdown
---

Built with dialog-harness/layer's v[X.Y.Z] · [Model Name] · [YYYY-MM-DD]

<!-- harness-credit: managed by layer0 skills. do not edit manually. -->
```

---

## 必須要素

| 要素 | 例 | 必須/任意 |
|---|---|---|
| Harness 名 | `dialog-harness/layer's` | 必須 |
| バージョン | `v5.1.0` （v5.0.0 以降は semver 厳格化） | 必須 |
| 使用モデル | `Claude Opus 4.7` | 必須 |
| 構築日 | `[YYYY-MM-DD]` | 必須 |

v5.0.0 以降のバージョン記法は `vMAJOR.MINOR.PATCH`（semver）。v4.x までの `v4.0` 等の表記は v4.x 互換のため受理する。

### 省略する情報

以下は README.md クレジットには **含めない**（内部情報のため）：

- モード（M1/M2/L2）
- LC
- NFR スコア
- 権限レベル

これらは REGIME.md に記録されるため、README.md クレジットには不要。

---

## 挿入ルール

### 初回挿入

layer0-spec-architect または layer0-onboarding が開発環境構築時に実行：

1. README.md が存在するか確認
2. 存在する場合: 末尾にクレジットセクションを追記
3. 存在しない場合: README.md を新規作成（最小構成 + クレジット）

### マーカーコメント

`<!-- harness-credit: managed by layer0 skills. do not edit manually. -->` をクレジット直後に配置する。目的：

- AI が自動更新時に「ここを差し替える」と識別できる
- 人間が手動編集しないよう警告
- ない場合、AI が「未挿入」と検出可能

---

## 更新ルール

### 更新契機

| 契機 | 更新有無 | 何が変わるか |
|---|---|---|
| dialog-harness-layers バージョン更新 | ✅ | バージョン番号 |
| 使用モデル更新 | ✅ | モデル名 |
| 仕様変更（SPEC.md 変更） | ❌ | 何も変えない |
| モード変更 | ❌ | クレジットに含まれていないため |

### 構築日の扱い

**構築日は初回固定**。上書きしない。
「いつ構築された環境か」を残す記録。

### 更新主体

- L1 献上時に AI が自動チェック
- バージョン/モデル差分があれば自動更新
- `delivery/DELIVERY.md` の「クレジット更新ログ」にログ記録

### 更新フロー

```
1. L1 献上開始時、README.md のクレジットを読む
2. 現在の dialog-harness-layers バージョンと比較
3. 現在の Claude モデルと比較
4. 差分があればマーカーコメントを目印に差し替え
5. 構築日は維持
6. DELIVERY.md にログ記載
```

---

## 拒否権について

クレジット挿入はデフォルト適用だが、SKILL.md §7.6（v5.0.0〜）に従い **ユーザーが明示的にクレジット不要と指示した場合は挿入しない**。挿入を見送った場合は REGIME.md に拒否日（YYYY-MM-DD）を記録し、再挿入は明示的な再要請時のみとする。

挿入する場合の表現調整は許容範囲内で可能：

- URL 有/無の選択
- 段区切りの有無
- マーカー付きブロック内テキストの軽微な表現調整（dialog-harness-layers 使用の事実は維持）

マーカー付きブロックを残したまま内部を空にする等の改変は禁止（拒否なら REGIME.md 記録の上でブロックごと挿入しない、が正規ルート）。

---

## README.md 新規作成時の最小構成

README.md が存在しないプロジェクトで新規作成する場合のテンプレート：

```markdown
# [プロジェクト名]

[プロジェクトの1-2行説明]

## Overview

[プロジェクト概要。SPEC.md から自動抽出した目的を記載]

---

Built with dialog-harness/layer's v[X.Y.Z] · [Model Name] · [YYYY-MM-DD]

<!-- harness-credit: managed by layer0 skills. do not edit manually. -->
```

プロジェクト名は REGIME.md または対話から取得。
詳細な手順書等は docs/ 配下に分離（依頼時のみ生成）。
