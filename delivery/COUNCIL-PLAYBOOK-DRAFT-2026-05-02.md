# Council 諮問プレイブック（草案）2026-05-02

adrv01 / adrv02 / adrv03 の 3 連続 Council 諮問で観察されたパターンを抽象化した、拮抗時 Council 諮問のテンプレ。

**ステータス**: 草案（DRAFT）。SPEC 化フェーズで `.claude/skills/crosscut-council/references/playbook.md` 等への正式配置を決定。
**用途**: 後続セッションで AI / 実装者が拮抗判定に直面した時の参照資産。
**前提**: `.claude/skills/crosscut-council/SKILL.md` および同 `references/` の規格に従う。本プレイブックは規格の **使い方** であって規格を上書きしない。

---

## 1. 諮問トリガー判定（いつ Council を呼ぶか）

`SKILL.md` §発動基準の判定指標を実例で言い直す:

| 観察された状況 | 諮問適格性 | 例（adrv01-03 から）|
|---|---|---|
| 2 案以上の実装パスが viable で、当事者の自己判断で決められない | ✅ 諮問 | adrv01: AI自己申告 / 独立観測 / 二重チェック |
| 既存原則（philosophy.md / ユーザー哲学）と複数案が複雑に絡む | ✅ 諮問 | adrv02: WF 形状単一性 + INSIGHTS 第10.10 + 連鎖駆動 |
| バージョン配置・ロードマップなど経営的便宜を含む判断 | ✅ 諮問 | adrv03: v5.5.0/v5.6.0/v6.0.0 のどこに何を置くか |
| タイポ修正、明確仕様の素直実装 | ❌ 諮問しない | — |
| 単一パス実装、選択肢のない技術判断 | ❌ 諮問しない | — |

**注意**: 「ユーザー（実装者）が対話段階で迷っている」場面は本来 spec-architect の対話で吸収すべきもので、Council の起動条件ではない（`SKILL.md` の DO NOT TRIGGER 規約）。adrv01-03 はいずれも「実装上の判断点で実装者が拮抗を感知した」ケース。

## 2. 選択肢の構成法

### 2.1 a/b/c 三択の組み立て

adrv01-03 で共通したパターン:

- **(a)** = 既存機構流用 / 短期コスト最小 / 現状維持寄り（経営者が好みやすい）
- **(b)** = 新規構造導入 / 技術的に堅実 / 中期投資（開発者が好みやすい）
- **(c)** = ハイブリッド / 段階移行 / 両者の中庸（バランス）

ただし、これは結果論で観察された傾向であって、**「a=現状維持 / b=新規 / c=ハイブリッド」を機械的に当てはめてはいけない**。論点ごとに最も自然な分割軸で 3 案を立てる。

### 2.2 第3の道（third_way）の予兆

adrv01-03 すべてで哲学者が options 外の「第3の道」を提示した。これは偶然ではなく:

- 哲学者 temperature 0.7 + 「単なる否定ではなく代替の問い・視点を提示」制約（`personas/business/phil.md`）
- conception カテゴリの situational_modifier で哲学者重み +2（base 3 → final 5）

つまり **conception カテゴリでは第3の道がデフォルトで出る前提**で諮問を組み立てる。a/b/c で完結すると思って諮問すると、哲学者 weight 5 が `third_way_excluded` で 30%+ の閾値を超え、`judgment_confidence < 0.5` で human_escalation_required が立ちやすい（adrv01 で発生）。

### 2.3 第3の道を吸収する選択肢設計

第3の道の影響を抑える方法:

- **a/b/c に「思想的軸」を 1 つ含める**: 単純な技術選択肢に加え、「c = ハイブリッド + 既存原則統合」のように哲学的余地を含めると哲学者が options 内 stance を取りやすい
- **諮問の question_to_answer を絞る**: 「どれにすべきか」で広く問わず「Phase 1 でどれから始めるか」など範囲限定する
- **adrv02 / adrv03 で観察された機能**: (c) ハイブリッド段階移行は哲学的余地を含むため、哲学者が完全に options 外に行かず weight が a/b/c に集約される傾向

## 3. category と重み配分の確認

`council-weights.md` の situational_modifier を起動前に確認:

| category | 経営者 | 開発者 | 哲学者 | 適用場面 |
|---|---|---|---|---|
| implementation | -1 | +2 | -1 | 技術選択（adrv は該当しない） |
| operation | +1 | 0 | -1 | 不可逆操作・リリース |
| conception | 0 | -1 | +2 | 新規構造・思想・将来性（**adrv01-03 はこれ**）|
| judgment | +1 | 0 | 0 | 判断一般（迷ったらこれ） |
| error_handling | -2 | +3 | -1 | エラー対応 |

**adrv01-03 は全て conception**: 自律駆動機構の思想・将来性議論のため。哲学者重み 5 は妥当だが、第3の道による third_way_excluded リスクが高い（§2.2 参照）。

迷ったら `judgment` フォールバックで良い（COUNCIL-LOG に `category_fallback: true` 記録）。

## 4. Persona 出力の典型パターン（adrv01-03 観察）

| Persona | confidence 範囲 | 典型 stance | 典型 dimension |
|---|---|---|---|
| 経営者 | 0.65-0.75 | (a) 既存機構流用 / 早期実用化 / ROI 最良 | ROI / 機会損失 / リスク |
| 開発者 | 0.85-0.95 | (b) or (c) 技術的堅実 / Shift Left 整合 | 技術的実現性 / 保守性 / 可逆性 |
| 哲学者 | 0.55-0.70 | 第3の道 / 前提への問い / 軸再構成 | 前提への問い / 長期影響 |

開発者の confidence が最も高く、判定の決定打になりやすい。経営者と開発者の stance が一致した場合（adrv02 / adrv03）は支配的に判定される（weighted_score 4.65）。

## 5. 第3の道の受け止め（minority_opinion 統合）

哲学者の第3の道は「**recommended と排他関係にあるか統合可能か**」で扱いを変える:

| 関係 | 例 | 受け止め |
|---|---|---|
| 排他的 | 哲学者が a/b を否定して別案を提示 | minority_opinion に保持、人間献上 |
| 統合可能 | 哲学者が a/b の **メタ層・軸再構成** を提示 | recommended と並行統合（adrv01-03 全例） |

adrv01-03 で観察された統合パターン:

- adrv01: a vs b の二項対立 → 哲学者「メタ層構造」（a を一次入力 / b を検証メタ層） → **段階的組み込みで止揚**
- adrv02: 主従集約 vs 全派生常駐 → 哲学者「subagent isolation で context 分離」 → **軸再構成（共有 vs 分離）として Phase 2 評価軸**
- adrv03: minor 路線 vs 大統合 → 哲学者「破壊変更基準で version 再配置」 → **SPEC 化時の再評価軸**

統合可能型の第3の道は **recommended の上位概念または評価軸として扱う**（recommended を否定せず、recommended の意味付けを深める）。

## 6. 段階的組み込みで止揚パターン

adrv01 で確定し、adrv02 / adrv03 にも波及した実装パターン。一般化:

```
[拮抗] (a) 短期コスト最小 vs (b) 中期投資
   ↓
[止揚] 時間軸で両立
   ↓
Phase 1: (a) 既存機構流用で即運用（コスト 0）
Phase 2: (b) 新規構造を後付け（破壊変更最小）
Phase 3: 階層構造として統合（哲学者第3の道を取り込む）
```

このパターンは **既存原則を壊さず将来選択肢を保持する**ための DH 標準テンプレ。`agreed_with_modification` の典型形。

## 7. judgment_confidence の解釈

`judgment-agent.md` §confidence 算出指針を実例で言い直す:

| 状況 | 範囲 | 例 |
|---|---|---|
| 全会一致 | 0.7-0.9 | — |
| 単純対立で重み差大 | 0.6-0.8 | adrv02 / adrv03（経営者+開発者一致で支配） |
| 単純対立で重み拮抗 | 0.4-0.6 | — |
| third_way_excluded が全 weight の 30%+ | < 0.5 | adrv01（哲学者 weight 5 / 全 11 = 45%）|
| tie_break_applied | < 0.4 | — |

**`judgment_confidence < 0.5` は強制人間エスカレーション**だが、実装者 = 人間（ひでさん）= エスカレーション先が同一人物の場合、合意プロセスでの (B) 修正合意が Step 8 解決と等価になる（adrv01 で観察）。

## 8. implementer_consent の選び方

| 値 | 適用場面 |
|---|---|
| `agreed_recommended` | recommended そのまま採用、第3の道は minority_opinion として保持のみ |
| `agreed_with_modification` | recommended を採用するが、修正（段階的組み込み等）を加える。`modification_note` フィールドで詳細記録 |
| `escalated` | Council 判断を保留、人間に献上（実装者 ≠ 人間の場合） |

**判断基準**:
- 第3の道が排他的 → `escalated` 検討
- 第3の道が統合可能で recommended に取り込める → `agreed_with_modification`
- 第3の道が排他的でも minority_opinion 保持で十分 → `agreed_recommended`

## 9. 失敗パターン（先行事例）

過去の COUNCIL-LOG から学ぶべき失敗例:

### 9.1 weight 分割逸脱（d1m4n5）

`council-2026-04-29T18-00-00Z-d1m4n5` で開発者 weight 6 を A 寄り 4 / C 寄り 2 に按分し、A を recommended に捏造した事例。これを契機に Orchestrator 決定論検算が導入された（`orchestrator.md` §決定論検算プロトコル）。

**回避策**: 1 persona = 1 weight 不可分の原則を厳守。stance は単一値で表明、複数 stance への按分は哲学違反。

### 9.2 invocation_id 重複（d4mtr1）

PR #21 で 4 論点を同 invocation_id `d4mtr1` で記録、後で `d4mtr1-d4mtr4` に renumber 訂正された事例（COUNCIL-LOG 冒頭の訂正記録参照）。

**回避策**: 1 invocation = 1 question_to_answer = 1 entry の原則。複合論点は分割して諮問する（adrv01 / adrv02 / adrv03 のように）。

### 9.3 conflict_type schema 違反

`unanimous_with_variance` という存在しない conflict_type が使われた事例。

**回避策**: PR1 では `unanimous` / `simple_conflict` の 2 値のみ。variance は `persona_summary` の dimension / premise で表現する。

## 10. プレイブック使用フロー（諮問者向け）

```
[実装中に拮抗を感知]
  ↓
[§1 諮問トリガー判定] → 適格性確認
  ↓
[§3 category 選択] → 重み配分確認
  ↓
[§2 選択肢構成] → a/b/c + 第3の道予兆を考慮
  ↓
[Council 起動]
  ↓
[Phase 1-3 実行]
  ↓
[§7 judgment_confidence 解釈]
  ↓
[§5 第3の道の関係判定] → 排他 or 統合可能
  ↓
[§8 implementer_consent 選択]
  ↓
[§6 段階的組み込みで止揚パターン適用（必要に応じて）]
  ↓
[COUNCIL-LOG 後追記、commit]
```

## 11. 後続改修候補

このプレイブックは草案。SPEC 化時の検討事項:

- **正式配置**: `.claude/skills/crosscut-council/references/playbook.md` か、別の references/ ディレクトリか
- **PR2 への反映**: 対立類型 A-G が PR2 で実装される際、§5 第3の道の扱いを類型 D（次元ずれ）等に再マッピング
- **F1-F3 振り返り儀式との連携**: 本プレイブックに記録された傾向を儀式で監査・更新
- **adrv01-03 以外の事例の蓄積**: conception 以外の category（implementation / operation 等）での諮問パターン

## バージョン

v0.1.0（草案、DH v5.4.0 リリース後の adrv01-03 を起点に作成）
