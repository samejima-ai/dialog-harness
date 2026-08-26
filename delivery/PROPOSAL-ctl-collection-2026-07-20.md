# CTL 収集経路の改善提案 — 利用者プロジェクトからの実地適用で判明した 5 つの欠落

- 日付: 2026-07-20
- 対象版: DH v6.3.0（master 6e7b04a 時点）
- 種別: 提案（タイプ C: 仕様改訂提案 / 実地適用で発見した改善余地）
- 起点: 利用者の要請「kakuman-platform の CTL を蓄積していきたい」
- 実地結果: **CTL-0 → CTL-1 到達**（評価済み 3 件 → 89 件、C1 が count=20 / rate=0.90 で委譲対象に）

---

## 0. 要旨

v6.1.0 で CTL 記録経路の分断（発動 53 回に対し記録 1 件）は解消された。しかし本提案の起点となった
実作業で、**「1 プロジェクト内で完結する前提」が残っていたために利用者プロジェクトの Council 資産
（42 件）が CTL に 1 件も載っていなかった**ことが判明した。

v6.1.0 は「書く側の経路」を直したが、**「複数プロジェクトから集める側の経路」は手つかずだった**。
これは AD-004（v4.2）「機構はあるが動作分岐に未接続」/ v6.1.0「記録経路の分断」と**同型の第 3 波**である。
philosophy 第 6 条は「Council データは `~/.claude/council-data/` にユーザー単位で蓄積する。プロジェクト
横断で学習資産が引き継がれる」と明記しているが、その横断経路を担う実装が存在しなかった。

以下、実作業で踏んだ 5 つの欠落を、深刻度順に提案として整理する。

---

## 1. 【最重要】`--prune` が複数プロジェクト運用でデータを破壊する

### 現象

`council-log-sync.py sync --prune` は「引数で渡された COUNCIL-LOG に対応しない invocation」を
すべて孤児とみなして削除する。DH 本体の COUNCIL-LOG で同期すると、**利用者プロジェクト由来の
invocation 全件が孤児判定される**（逆も同様）。

実測（本作業時点）:

```
# DH 本体のログで同期 → platform 由来 43 件が孤児扱い
注意: COUNCIL-LOG に対応しない孤児 invocation が 43 件あります（手動 record 等）。--prune で掃除できます

# platform のログで同期 → DH 由来 55〜57 件が孤児扱い
注意: COUNCIL-LOG に対応しない孤児 invocation が 57 件あります（手動 record 等）。--prune で掃除できます
```

`--prune` は README で「二重計上の解消」として推奨されており、警告文も「掃除できます」と実行を
促す語調である。**利用者が素直に従うと、他プロジェクトの Council 資産が消える。**

### 深刻度

**高**。CTL は「横断蓄積」が設計思想の中核（philosophy 第 6 条）であり、その中核データが
推奨コマンドで失われる。しかも失われたことは stats の総数が減るまで気づけない。

### 提案

1. **`--prune` のスコープを「同期対象ログに由来する invocation」に限定する**。
   invocation JSON に由来ログの識別子（`_source_log` 等）を持たせ、prune は同一 `_source_log`
   のもののみを対象とする。これにより「同一ログ内での孤児（別採番の手動 record）」という
   本来の狙い（`council-2026-07-01T13:30:57Z-ctldedup` 案A）は維持したまま、他プロジェクトを守れる。
2. 移行期の暫定措置として、**警告文に「他プロジェクト由来の可能性」を明記**する。
   現行の「手動 record 等」という例示は、複数プロジェクト運用を想定していない書き方になっている。
3. `--prune` 実行前に削除対象を列挙し、確認を求める（`--prune --dry-run` は既にあるが、
   `--prune` 単体でも件数だけでなく **id の一覧**を出す）。

### 暫定回避策（本作業で採った方法）

`--prune` を一切使わず、事前に `~/.claude/council-data` を丸ごとバックアップした上で同期した。
これは利用者が「複数プロジェクトが同居する」と気づいて初めて選べる回避策であり、
**気づかなければ踏む**。

---

## 2. `implementer_consent` の語彙が利用者プロジェクトで発散し、写像テーブルから漏れる

### 現象

`CONSENT_TO_STATUS` は 2 値（`agreed_recommended` / `agreed_with_modification`）のみを写像する。
しかし kakuman-platform の COUNCIL-LOG には以下の語彙が実在した:

| implementer_consent | 件数 | 現行写像 |
|---|---:|---|
| `agreed_recommended` | 25 | agreed |
| `agreed` | 7 | **null（脱落）** |
| `approved` | 2 | **null（脱落）** |
| `agreed_recommended_with_3_conditions` | 1 | **null（脱落）** |
| `agreed_recommended_with_6_conditions` | 1 | **null（脱落）** |
| `agreed_recommended_with_5_conditions_under_purity_caveat` | 1 | **null（脱落）** |
| `agreed_recommended_with_substitution` | 1 | **null（脱落）** |
| `agreed_minority_opinion` | 1 | **null（脱落）** |

**評価済み 39 件のうち 14 件（36%）が「未評価」として統計から脱落**していた。
実際には人間が合意済みの判定である。

### 深刻度

**中〜高**。CTL の燃料（agreement_rate の素）が 3 分の 1 以上失われる。しかも
「未評価」として扱われるため `pending` に現れ、利用者は「まだ評価していない」と誤認する。

### 提案

**接頭辞 + マーカーによる正規化に置き換える**。本作業では以下を実装し、既存テスト全 PASS を確認した:

```python
CONSENT_TO_STATUS = {
    "agreed_recommended": "agreed",
    "agreed_with_modification": "modified",
    # 表記ゆれ（利用プロジェクト側の語彙）
    "agreed": "agreed",
    "approved": "agreed",
    "agreed_minority_opinion": "agreed",
}
_CONDITIONAL_MARKERS = ("_with_", "_under_")

def normalize_consent(consent):
    if not consent: return None
    v = consent.strip()
    if v in CONSENT_TO_STATUS: return CONSENT_TO_STATUS[v]
    # 条件・置換を伴う同意は「推奨そのままではない」= modified
    if v.startswith(("agreed", "approved")) and any(m in v for m in _CONDITIONAL_MARKERS):
        return "modified"
    if v.startswith(("agreed", "approved")): return "agreed"
    return None
```

**機械導出禁止（`ctlrec1`）に抵触しない理由**: 却下されたのは `category`（重み軸）→
`decision_category`（委譲軸）という**直交する別軸**への写像。本提案は
`implementer_consent` → `status` の**同一軸内の表記ゆれ正規化**であり、
「同意したが推奨そのままではない」という原文の意味を保存する方向にしか動かさない。

なお `_with_N_conditions` を `modified` に倒すのは保守的判断（一致率を過大評価しない）。
`agreed` に倒す解釈もありうるが、CTL が実力以上に見えるリスクを避けた。

---

## 3. 複数 COUNCIL-LOG を束ねる正規経路が無い

### 現象

`sync --log <path>` で任意のログを指定できるが、**複数ログを継続的に同期する運用が想定されていない**。
利用者は以下を自力で発明する必要がある:

- どのプロジェクトのログを、どの順で、いつ同期するか
- `--prune` を使ってよいか（§1 の通り使えない）
- 新しいプロジェクトが増えたらどうするか

`README-council-ctl.md` の「発火主体: L0 振り返り儀式（F1 ステップ 4）」も、
**自プロジェクトのログのみ**を同期する前提で書かれている。

### 深刻度

**中**。CTL の横断蓄積という設計思想（philosophy 第 6 条）が、実装の欠落によって
「気づいた人だけが手動で回す」状態になっている。

### 提案

1. **同期対象ログのレジストリを user-scope に持つ**。
   `~/.claude/council-data/sources.yml` 等に「このユーザーが同期すべき COUNCIL-LOG のパス一覧」を
   登録し、`sync --all` で全件を順に同期する。
   ```yaml
   sources:
     - path: ~/dialog-harness/history/COUNCIL-LOG.md
       label: dh-core
     - path: ~/kakuman-platform-v3.0/history/COUNCIL-LOG.md
       label: kakuman-platform
   ```
2. **L0 振り返り儀式の F1 同期を `sync --all` に変える**。現行の「自プロジェクトのみ」では
   横断蓄積が儀式で保証されない。
3. レジストリ登録を **onboarding / spec-architect の初期化時に自動追記**する
   （利用者が手で書かなくてよい＝フラクタル原則「新規質問ゼロ」に整合）。

---

## 4. `decision_category` の遡及付与を支援する経路が無い

### 現象

v6.1.0 は Phase 0 で `decision_category` を必須ゲート化し、**将来分**の欠落を防いだ。
しかし**過去分の救済経路が無い**。CHANGELOG 自身が「過去分の真の救済には C1〜C4 の人手分類が必要」と
認めているが、その人手分類を支援する道具が無いため、実際には放置されていた。

実測: 本作業開始時点で 97 件中 **93 件が `decision_category=null`**。CTL 統計に載っていたのは 3 件のみ。
つまり **88 件の事後評価済みデータが、分類ラベルの欠落だけで死蔵されていた**。

### 深刻度

**高**。これが CTL-0 から動かない直接原因だった。燃料（評価）は十分にあり、
ラベルだけが無いという状態は、機構の設計ミスではなく**移行支援の欠落**である。

### 提案

1. **`council-ctl.py classify` サブコマンドの新設**。未分類 invocation を 1 件ずつ
   「議題 / 判定 / 現在の category」とともに提示し、C1〜C4 を対話的に付与する。
   付与先は **COUNCIL-LOG 側**（単一ソース原則。council-data に直接書いても次回同期で消える — §5）。
2. **分類の判定基準をドキュメント化する**。philosophy 第 6 条の C1〜C4 定義は 1 行ずつしかなく、
   実際の分類では判断が割れる。本作業で用いた運用基準を参考として示す:

   | カテゴリ | 定義（philosophy 第 6 条） | 実運用での判定基準 |
   |---|---|---|
   | C1 抵触判断 | 既存哲学・ルールに照らした実装中のジャッジ | 既存の罠・規約・原則・哲学に照らして「違反か / どう準拠するか」を裁いたもの。哲学への昇格判断も含む |
   | C2 トレードオフ | スコープ・優先度・実装方針の選択 | 複数案の拮抗から 1 つを選んだもの。最頻出（本作業で 55/89 件） |
   | C3 不可逆操作 | 権限レベル内での判断 | 本番 DB 書込・migration・push・データ移送など revert が効かない操作の可否 |
   | C4 仕様矛盾解決 | SPEC.md 内部の矛盾解消 | 記述間の不整合・前提事実誤認・命名/表記の不統一・判定同士の衝突の解消 |

   注意点として、**語彙の正規表現マッチによる自動分類は機能しない**ことを実測で確認した。
   「適用」「投入」等の語が実装判断一般に頻出するため C3 が過剰検出され（28/85 件と最多になった）、
   実態と乖離する。これは `ctlrec1` の「満ちているが意味は空」の再演であり、破棄した。
   **分類は人間の承認を要する**（AI は原案提示まで）。
3. 移行支援として、**未分類件数を `status` に常時表示する**。現行の `status` は
   「未評価 9 件」は出すが「**未分類 93 件**」は出さない。CTL が上がらない真因が見えない。

---

## 5. council-data 側の手動編集が次回同期で消える（設計は正しいが導線が無い）

### 現象

`sync` は COUNCIL-LOG 対応の invocation を**常に上書き**する（`ctldedup` 案A・単一ソース化）。
これは設計として正しい。しかし利用者視点では:

- CTL を上げたい → `decision_category` を足したい
- 手近にあるのは `~/.claude/council-data/invocations/*.json`
- そこに書く → **次回同期で消える**

消えることは警告されず、静かに巻き戻る。

### 深刻度

**低〜中**。設計は正しく、正しい導線（COUNCIL-LOG に書く）も存在する。問題は
「どちらに書くべきか」が実行時に示されないこと。

### 提案

- invocation JSON に `"_source": "council-log-sync"` は既に入っている。これを利用して、
  **`_source` が sync のファイルを手編集した形跡を検出したら警告する**
  （例: `decision_category` が JSON にあり COUNCIL-LOG に無い場合、「COUNCIL-LOG に書いてください」と促す）。
- `README-council-ctl.md` に「**council-data は導出物。編集は COUNCIL-LOG へ**」を
  §記録経路の冒頭に太字で置く（現行は §記録経路の説明文中に埋もれている）。

---

## 6. 実地適用の結果（提案の裏付け）

本提案は机上のレビューではなく、実際に kakuman-platform の Council 資産を CTL に載せる作業から得た。

| 指標 | 作業前 | 作業後 |
|---|---:|---:|
| invocations 総数 | 55 | **97** |
| 事後評価済み（status 非 null） | 50 | **89** |
| `decision_category` 付与済み | 4 | **93** |
| CTL 統計に算入 | 3 | **89** |
| **CTL** | **CTL-0** | **CTL-1** |

カテゴリ別内訳（作業後）:

```
C1: count=20 agreed=18 modified=2 rate=0.90   ← 委譲対象カテゴリ
C2: count=55 agreed=48 modified=7 rate=0.8727
C3: count=5  agreed=5  modified=0 rate=1.0
C4: count=9  agreed=8  modified=1 rate=0.8889
```

CTL-2 への残条件は「4 カテゴリ中 3 以上で count≥10 かつ rate≥0.90」。
C3（count=5）と C4（count=9）は件数不足、C2 は rate 0.87 で質的に未達。
**C3/C4 は母数が小さく、自然蓄積を待つのが妥当**（無理に分類を寄せれば §4 の「満ちているが空」に陥る）。

### 本作業で加えた変更

- `scripts/council-log-sync.py`:
  - `normalize_consent()` 新設（§2 の提案を実装）。
  - 孤児警告の文言を複数プロジェクト運用向けに修正（§1 提案 2 を実装）。
    「--prune で掃除できます」→「他プロジェクト由来ならこれは正常です / --prune は全件削除します」。
- `scripts/test-council-log-sync.sh`: 上記文言変更に追随（挙動の変更なし）。全 15 項目 PASS。
- `.claude/skills/crosscut-council/SKILL.md`:
  - **§クロージング手順を新設** — Council 発動のたびに `sync --recompute` を実行する手順を
    処理フローの必須ステップとして明記（後述）。
  - 主経路コマンドから `--prune` を除去し、危険性の警告ブロックを追加。
- `.claude/skills/crosscut-council/references/pre-check.md`: C1〜C4 の**運用判定基準表**を追加
  （§4 提案 2 を実装）。語彙マッチによる自動判定を禁止する旨も明記。
- `history/COUNCIL-LOG.md`: 47 エントリに `decision_category` を追記（null 宣言済みフィールドへの
  単方向埋め込み＝ append-only 例外条項に適合）。
- 利用者プロジェクト側 `history/COUNCIL-LOG.md`: 38 エントリに同様の追記。

### 発動時自動同期の実装（§3 の一部を実装）

利用者要請「Council スキル実行時に自動実行するように」を受け、**skill 自身の手順**として実装した。

v6.1.0 は「案B（hook-observer 経由発火）」を **CC hooks が tool 単位発火で『Council 発動』という
抽象イベントに口が無い**ため却下している。本実装はこの却下理由の**射程外**である —
hook で外から検知するのではなく、**skill が自分の発動を知っている**という自明な事実を使い、
COUNCIL-LOG 追記の直後に同期を走らせる手順を SKILL に固定した。hook は導入していない。

主経路 / 従経路の二段構成:

| 経路 | 発火点 | 役割 |
|---|---|---|
| **主** | Council skill のクロージング手順（発動のたび） | 発動と記録の時間差をゼロにする |
| 従 | L0 振り返り儀式 F1 冒頭 | 主経路の失敗・省略分の取りこぼし回収（同期は冪等ゆえ二重実行は無害） |

同期対象は**自プロジェクトの COUNCIL-LOG のみ**とした（`--prune` なし）。各プロジェクトが自分の分を
流せば user-scope で自然に合流するため、§3 のレジストリ（`sources.yml` + `sync --all`）は
**本実装では不要**と判断した。ただし「同期を一度も走らせないプロジェクト」が存在する場合は
その分が永久に載らないため、レジストリ案は §3 として温存する。

### 未実装（採否は DH 側の判断に委ねる）

- §1 提案 1・3: `--prune` のスコープ限定（`_source_log` による由来識別）と削除対象 id の列挙。
  **警告文の修正のみ先行実装**したが、構造的な安全化は未着手。
- §3: 同期対象レジストリ（`sources.yml` + `sync --all`）。上記の通り本実装では不要と判断したが、
  横断蓄積を機構として保証するなら必要。
- §4 提案 1・3: `council-ctl.py classify` サブコマンドと、`status` への未分類件数表示。
- §5: council-data 手動編集の検出警告。

---

## 7. 通底する構造的観察

v6.1.0 の CHANGELOG は自らの欠陥を「**機構を作るが実行経路に接続しない**」反復欠陥と名指した。
本作業で見つかった 5 件は、その系譜のさらに先にある:

| 波 | 欠陥の型 | 版 |
|---|---|---|
| 第 1 波 | 機構はあるが動作分岐に未接続 | AD-004（v4.2）で修正 |
| 第 2 波 | 機構はあるが記録経路が分断 | v6.1.0 で修正 |
| **第 3 波** | **記録経路はあるが横断集約経路が無い / 移行支援が無い** | **本提案** |

いずれも「作った機構が、実際に価値を生む地点まで配線されていない」という同一の形をしている。
第 3 波に共通するのは、**「1 プロジェクト内で完結する」という暗黙前提**である。
philosophy 第 6 条は横断蓄積を明記しているのに、実装・ドキュメント・儀式のすべてが
自プロジェクト単独を前提に書かれていた。

v6.3.0 で `runtime_profile` 軸を新設した際の教訓（「暗黙前提を軸として明示化する」）は、
ここにも適用できる。**「単一プロジェクト前提 / 複数プロジェクト横断」もまた明示化されるべき軸**
ではないか、というのが本提案の最も抽象度の高い問いである。

---

## 8. 申し送り

- 本提案は**タイプ C（仕様改訂提案）**であり、SPEC 改変は行っていない。採否判断は人間 / Council に委ねる。
- §1（`--prune` のデータ破壊）は実害が大きく、**採否判断を待たずに警告文だけでも先行修正する価値**がある。
- `~/.claude/council-data.bak-20260720/`（作業前バックアップ・55 件）は、本提案の検証が済み次第
  利用者側で削除する。残置すると将来の混乱源になる。
