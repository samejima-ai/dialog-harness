# CTL 記録（user-scope, COUNCIL-LOG から同期）

> v7.0.0 Phase A F10 で `SKILL.md` §ログ要件 から移送（SKILL.md を 500 行未満に保つ）。内容は不変。
> 正本参照: `ctl-calculation.md` §4（スキーマ・命名）/ `SKILL.md` §クロージング手順（発火主体）。

CTL（Council Trust Level）の蓄積データ `~/.claude/council-data/invocations/` は、
**`history/COUNCIL-LOG.md`（project-scope, append-only）を単一情報源として同期で導出する**
（スキーマ・命名は [references/ctl-calculation.md](ctl-calculation.md) §4 が一次情報源）。

**なぜ同期経路か（v6.1.0 で再設計、Council 諮問 `council-2026-07-01T-ctlrec1`）**:
かつては「発動のたびに手で `record` を叩く」手順書依存だったが、それを強制する実行主体が
無く空文化した（発動 53 回に対し CTL 記録は 1 件）。COUNCIL-LOG には**全発動が確実に追記される**
（本 SKILL §ログ要件）ので、これを唯一のソースとし、`scripts/council-log-sync.py` が
council-data を導出する。これで「書く側の経路」の二重化を解消する。詳細は
`dh-upgrades/upgrade-spec-v6.1.0.md`。

```bash
python3 scripts/council-log-sync.py sync --recompute           # 同期 + CTL 再計算（主経路）
python3 scripts/council-log-sync.py sync --dry-run             # 生成予定を確認（書かない）
```

> **`--prune` を主経路に置かない**（2026-07-20 改訂）: `--prune` は「引数のログに対応しない
> invocation」を全件削除する。council-data は **user-scope でプロジェクト横断**（philosophy 第 6 条）
> ゆえ、あるプロジェクトのログで同期すると**他プロジェクト由来の invocation が全件孤児判定される**。
> 実測では DH 本体のログで同期して platform 由来 43 件が、逆で DH 由来 57 件が孤児として列挙された。
> `--prune` は「同一ログ内の別採番手動 record を掃除する」目的でのみ、**削除対象 id を目視確認した上で**
> 使う。孤児警告が出ても、他プロジェクトを併用しているなら**それは正常**であり掃除してはならない。

**同期の発火主体（実行経路への接続 — 手順書依存に戻さない）**:
同期は「スクリプトを作っただけ」では①と同じ轍を踏む。以下 2 つを主経路とする：

- **【主】Council 発動のたび、本 SKILL の最終ステップで同期する**（§9 クロージング手順）。
  COUNCIL-LOG への追記直後に実行するため、**発動と記録の間に時間差が生じない**。
  「発動 → COUNCIL-LOG 追記 → 同期」を 1 つの不可分な手順として扱う。
- **【従】L0 振り返り儀式（F1/F2/F3）の冒頭でも同期を走らせる**
  （`layer0-spec-architect/references/ritual-protocol.md` §CTL 事後評価）。
  儀式は「同期 → `pending` 列挙 → 未評価判定を人間に問う」を 1 手順として固定する。
  主経路が失敗・省略された場合の**取りこぼし回収**として機能する（同期は冪等ゆえ二重実行は無害）。

CC hooks は tool 単位発火で「Council 発動」という抽象イベントに口が無いため、**hook 発火は採らない**
（`upgrade-spec-v6.1.0.md` §2.1 案B 却下理由）。上記【主】は hook ではなく**skill 自身の手順**として
実装するため、この却下理由の射程外である（skill は自分の発動を知っている）。

**decision_category は同期で機械導出しない**: COUNCIL-LOG に明示された C1〜C4 / H1〜H4 が
あればそれを使い、無ければ `null` で載せる。重み配分軸の `category`（conception/judgment 等）
から `decision_category`（委譲軸）へ写像してはならない（両者は
[references/consensus-protocol.md](consensus-protocol.md) §category と decision_category の役割分担
で直交と明記。写像は非全射で、埋めると「満ちているが意味は空」な統計になり CTL 算出が偽の確信を生む）。
`null` の invocation は `_compute_stats` の null-skip で統計から除外される。よって**将来分は
Phase 0（発動時）で `decision_category` を必須記録する**（[references/pre-check.md](pre-check.md) §decision_category 必須ゲート）。

**記録失敗時の規範（判断 ＞ 記録）**: Council の一次成果物は judgment であり、CTL 記録は従属物。
COUNCIL-LOG への追記（本 SKILL §ログ要件）さえ済んでいれば、同期はいつでも後追いできる。
同期・record が失敗しても **Council フロー（出力・合意プロセス）は止めない**。失敗は **warn として
可視化**し（黙殺しない）、後日 `sync --recompute` で復元する。記録失敗を理由に判断を握り潰すのは
献上哲学（philosophy.md §5）に反する。

**個別 record は「COUNCIL-LOG 即時追記トリガ」であって第二の記録ストアではない**
（v6.1.0 案A / Council `council-2026-07-01T-ctldedup`）:

「単一情報源は COUNCIL-LOG」と宣言しながら手動 record を独立ストアとして温存すると、
同一発動が二重計上され CTL 統計を歪める（v6.1.0 が葬った二重書き経路の再来）。よって
**手動 record を使う時は必ず COUNCIL-LOG にも同じ発動を追記する**。追記すれば次の同期で
正規版（COUNCIL-LOG 由来の invocation_id）に一本化される。COUNCIL-LOG に追記しない手動
record は「孤児」として `council-log-sync sync --prune` の掃除対象になる（残すと二重計上源）。

1. `scripts/council-ctl.py` が存在すれば、同期を待たず 1 件だけ即記録できる。
   **ただし同時に COUNCIL-LOG へ追記すること**（§ログ要件。追記なしは二重計上源）:

   ```bash
   python3 scripts/council-ctl.py record \
     --decision-category <C1|C2|C3|C4> \
     --category <operation|judgment|conception 等> \
     --topic "<question_to_answer の抽象要約・80字以内>" \
     --judgment "<recommended の抽象表現>" \
     --confidence <judgment_confidence> \
     --consensus <consensus_mode>
   # → この発動を history/COUNCIL-LOG.md にも必ず追記する（同期で正規版へ一本化される）
   ```

   **`init` は不要**: `record` は未初期化（`~/.claude/council-data/` 不在）でも
   自動で CTL-0 コールドスタート初期化してから記録する（ctl-calculation.md §1/§8）。

2. `scripts/council-ctl.py` が無い（DH skill のみ取り込んだ利用者プロジェクト等）場合は、
   下記スキーマの invocation JSON を `~/.claude/council-data/invocations/` に直接書く
   （この経路だけで self-contained に記録できるよう全フィールドを以下に明示する。
   一次情報源は `ctl-calculation.md` §4）。ディレクトリが無ければ先に作る。

   - **ファイル名**: `<ISO8601Z のコロンをハイフン化>-<invocation_id 末尾6文字>.json`
   - **中身**（`actual_outcome.status` は `null` で作成）:

     ```json
     {
       "invocation_id": "council-<ISO8601Z>-<6hex>",
       "council_type": "business",
       "category": "<operation|judgment|conception 等>",
       "decision_category": "<C1|C2|C3|C4>",
       "topic_summary": "<抽象要約・80字以内>",
       "judgment": "<recommended の抽象表現>",
       "judgment_confidence": 0.85,
       "consensus_mode": "<auto_agree|escalate_to_human 等>",
       "ctl_at_invocation": "<記録時点の CTL>",
       "actual_outcome": {"status": null, "evaluated_at": null, "modifier_note": null}
     }
     ```

   必須フィールドが欠けたり `decision_category` が C1〜C4 以外だと、後段の `_recompute`/
   振り返り儀式で **warn skip され統計から静かに落ちる**（CTL が実態より低く出る）。
   直接書き経路を採るときはこのスキーマ厳守が CTL の正確性の前提になる。

**フィールド対応**:

| council-data | 供給元 |
|---|---|
| `decision_category` | Phase 0 / consensus-protocol の decision_category 判定（C1〜C4） |
| `category` | 重み配分用カテゴリ（operation/judgment/conception 等） |
| `topic_summary` | question_to_answer の**抽象要約**（固有名・コード断片・人物名を入れない） |
| `judgment` | recommended の抽象表現 |
| `judgment_confidence` | Judgment Agent 出力 |
| `consensus_mode` | auto_agree / escalate_to_human 等 |
| `ctl_at_invocation` | 記録時点の CTL |

**H カテゴリは記録しない**（CTL に関係なく常時人間献上のため。ctl-calculation.md §2）。

**事後評価（actual_outcome）は record とは分離する**: 記録は発動と同時に自動で行うが、
`actual_outcome`（agreed/modified/rejected）は合意プロセス完了時または振り返り儀式（F1-F3）で
埋める。事後評価は「Council の判断が正しかったか」の**証拠フィードバック＝人間ゲート**であり、
ここを自動で `agreed` 埋めにすると CTL の信頼性が崩れる（philosophy.md 第6条 人間最終承認 /
crosscut-continuous-learning の「自動 promote は実装しない」決定と整合）。`scripts/council-ctl.py`
があれば `evaluate <id> --status <...>` で埋め、stats.json と CTL が即再計算される。
