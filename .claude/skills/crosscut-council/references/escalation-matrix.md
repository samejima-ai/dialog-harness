# Escalation Matrix — 開発ポジション×段階の判定促し（v6.10.0 新設）

> 起点: Council `council-2026-08-14T14:22:00Z-f9b2c4`（v6.9.0 事後評価）の是正勧告に対する
> 人間決定（2026-08-14）:
> 「開発のポジションや段階で人間または Council への判定を促すようにする。
> AI 判定矛盾については Council 機構で緩和とする」。
> 本文書はこの決定の実装であり、philosophy 第6条（H/C カテゴリ）・第9条（委譲境界）の
> **新設ではなく既存規範の配線表**である。新しい判定カテゴリを発明しない。

## 0. 目的

v6.9.0 で顕在化した瑕疵 — 規範文書の改変が「一文依頼 → 実装 → auto-merge」を
判定の促しなしに通過した — の構造的是正。**どのポジションのどの段階で、誰の判定
（人間 / Council / 自律）を促すか**を一表に固定し、実行主体の裁量から外す。

促し（prompt）とは: 該当セルに達した実行主体が、**先に進む前に**指定された判定先へ
明示的に諮ること。自律セルでも H 抵触を検知したら即時献上（第6条例外）が常に優先する。

## 1. マトリクス

| ポジション | 段階 / 場面 | 促す判定先 | 根拠 |
|---|---|---|---|
| L0 spec-architect | 仕様策定・SPEC/DONT 確定 | **人間**（対話が本体） | 第6条 H3 隣接 |
| L0 | dev_mode 昇降格・モード判定・L2 発動 | **人間**（ADR 込み） | 第6条 H4 |
| L1 autonomous-dev | 実装中の C1-C4 検出（案の拮抗・confidence < 0.6・不可逆操作前・仕様曖昧） | **Council**（CTL 連動） | SKILL §発動基準・自己申告プロトコル |
| L1 | H カテゴリ抵触の検知 | **人間**（即時献上・中断） | 第6条 例外条項 |
| L1 | 仕様不足・実装不能 | **人間**（Type C/D 献上。質問はしない） | philosophy §5 献上哲学 |
| L1-reviewer | AI 判定矛盾の検出（§2） | **Council**（C4/C1）→ jc < 0.5 で人間 | 本改修（f9b2c4 人間決定） |
| L2 orchestrator / integration-verifier | 跨ぎドメイン方針対立 | **Council** → 解消不能は人間 | SKILL §直接起動 |
| crosscut verifiers（drift / philosophy） | 検出結果の還流 | **feedback-loop 経由**（CTL 連動で自動化度変化） | crosscut-feedback-loop |
| **全ポジション** | **規範文書改変の実装前**（`.claude/skills/**` / `VERSION` / `templates/**` の規格・ルール） | **Council 諮問を促す**。献上時は**人間判定を促す**（auto-merge の通過に判定を代行させない） | f9b2c4 是正 (2) |
| 全ポジション | L-FROZEN 3 文書（philosophy / delegation-boundary / auto-merge-boundary） | **人間専管**（AI は提案 PR も不可） | 第6条 憲法の自己改訂禁止 |
| 全ポジション | 献上後の事後評価 | **人間**（明示同意で起動、自動起動しない） | 第6条 事後評価 |

- 「規範文書改変」行が v6.9.0 の瑕疵の直接是正である。利用者の一文依頼は**着手の承認**として
  有効だが、**規範改変の内容確定の判定**は Council 諮問（実装前）と人間判定（献上時）で別途促す。
  依頼文言だけを承認スコープの全域と解釈しない。
- 通常の SPEC/DONT 改変（枠内・可逆 = 第9条 L-FULL）はこの行の対象外 — 対象は DH 本体の
  規範・規格・skill 定義の改変に限る。

## 2. AI 判定矛盾の Council 緩和

**AI 判定矛盾** = 独立した AI 判定主体（またはセンサー）同士の判定が食い違う状態。
従来は「FAIL 扱いで差戻し」等の一律処理だったが、矛盾は情報（どの観測が割れたか）を
持っており、握り潰さず Council で構造化して緩和する（人間決定 2026-08-14）。

### 類型と経路

| 類型 | 例 | 経路 |
|---|---|---|
| (i) 自己検証 vs 独立検証 | L1 が PASS、reviewer が FAIL（またはその逆） | 検出側（reviewer）が Council 起動（**C4** 判定衝突）。judgment を VERIFICATION.md に添えて差戻し or 献上 |
| (ii) verifier 間矛盾 | drift PASS だが philosophy 違反検出、sensor PASS だが推論判定 FAIL | 検出側が Council 起動（**C1** 抵触判断）→ feedback-loop へ judgment 添付で還流 |
| (iii) Council 内部の対立 | persona の simple_conflict / 第3の道 | **既存機構で処理済み**（重み付き評定・jc 帯・escalate）。本表の対象外 |
| (iv) 反証と確証の矛盾 | 確証チェック全 PASS だが反証成立（falsification-protocol） | 反証成立は矛盾ではなく **FAIL 確定**（反証が優先）。Council 不要 |

### 緩和プロトコル

1. 矛盾を検出した主体が、両判定の内容・観測点・根拠を context に列挙して Council を起動する
   （options は「判定 X を採る / 判定 Y を採る / 両判定とも保留し人間へ」の形を基本とする）
2. `judgment_confidence ≥ 0.5` → Council の judgment を添えて処理を続行
   （差戻し・還流・献上のいずれか。judgment は記録であり決定ではない — final_decision null）
3. `judgment_confidence < 0.5` → 既存規則どおり人間エスカレーション
4. **再帰の遮断**: Council 自体が矛盾の当事者である場合（judgment の検算不一致等）は
   Council で緩和せず直接人間へ（第6条 憲法の自己改訂禁止と同型の理由）
5. 全件 COUNCIL-LOG に記録（decision_category は C4 または C1。§8 ブロック形式）

## 3. 運用境界

- 本マトリクスは**促しの表**であり、判定結果を先取りしない。Council の出力は常に判断
  （final_decision null）で、決定は人間または実装者の合意プロセスに残る
- **オーケストレーション実行基盤（Workflow / 議論型協調層）は判定を持たない実行機構**であり、
  判定は本マトリクスの定めに従う（v6.11.0 F7-1・upgrade-spec I-1）。リード agent・スクリプトが
  判定を代行し始めたら drift として verifier / 儀式で検出対象とする
- CTL 昇格時（CTL-1 以上）は第6条の委譲範囲に従い、C カテゴリの該当セルが自律側へ動く。
  H カテゴリ・L-FROZEN 行は CTL に依らず不変
- 本表の改変自体が「規範文書改変」行の適用対象である（自己適用）
- 未掲載の場面に遭遇したら: 迷ったら献上（philosophy §5）。表の増補は L0 経由で行う
