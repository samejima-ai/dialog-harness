# Council 上程議題草稿 — メタスキル開発案件

**作成日時**: 2026-05-11 JST
**起点 HANDOFF**: `5fd827fa-HANDOFFDHmetaskillindustryabsorption.md`
**上程主体**: layer0-spec-architect（L0、本セッション）
**Council 機構**: crosscut-council Phase 1（v5.10.0 で SDK 独立呼出に切替済、3 ペルソナ並列独立判定）

---

## 議題 1: ECC 参照カタログ 5 ファイルの出力先ディレクトリ判定

### 背景

ECC（`affaan-m/everything-claude-code` v2.0.0-rc.1）は業界実装プリミティブの典型例として、DH の方法論で「同等以上を生成可能」と示すための参照標本となる。Phase 0 で 5 ファイル（agents-catalog / skills-pattern / hooks-trigger-points / agentshield-spec / instincts-design）を生成するが、DH 内のどのディレクトリに配置するかが未確定。一旦 `delivery/refs-draft/ecc/` に draft 配置し、本議題で正式配置先を確定する。

### 候補と原則照合

| 候補 | 整合する DH 原則 | 違反/懸念する DH 原則 |
|---|---|---|
| **A. `.claude/refs/industry/ecc/`** | skill 分散モデルとの整合 / D2-D4 境界明確 / 業界横断の新カテゴリ確立 | `.claude/` 配下に skill 以外のディレクトリ新設 → 既存規約からの逸脱、説明責任 |
| **B. `history/refs/industry/ecc/`** | narrative 集中管理 / D5 監視層に近い配置 | history/ は「過去記録」、参照標本は「現在も有効な事実」→ 意味的不一致 |
| **C. `intent/references/industry/ecc/`** | Issue #70「観測温存」と同方向の振り分け | `intent/` ディレクトリ現状 0 件、新規 root ディレクトリ作成の説明責任 |
| **D. `assets/industry/ecc/`** | skill-creator progressive disclosure 準拠 | `assets/` は「埋めて使うテンプレート」、参照標本（読み専用）と意味的不一致 |
| **E. `.claude/skills/layer0-spec-architect/references/ecc-catalog/`** | L0 拡張の最も自然な配置先 | 「業界横断の参照標本」を 1 skill 配下に閉じ込めるのは不適切（複数 skill から参照されるべき） |

### L0 推奨（Council に上程する判断材料）

**推奨: 候補 A `.claude/refs/industry/{ecc, bmad, ...}/`**

- 業界実装プリミティブの参照標本を **「skill とは別の D2 境界」** として新カテゴリ化
- 将来的に BMAD / Cline / Aider 等を吸収する場合も `.claude/refs/industry/<name>/` で拡張可能
- skill 内部からは相対 path `../../refs/industry/ecc/agents-catalog.md` で参照可
- `.claude/` 配下に skill 以外のディレクトリを新設する説明責任は negligible（D2 境界の明示化）

**反対意見想定**:
- 候補 C も合理的（観測温存方針との整合）。ただし `intent/` ディレクトリの新規創出コストが高い
- 候補 E は L0 拡張として自然だが、業界横断の概念を 1 skill に閉じ込める哲学的不整合

### 求める Council 判定

- A/B/C/D/E から 1 つ選択、または別案を提示
- 採決後、`delivery/refs-draft/ecc/` の 5 ファイルを正式パスへ移動

---

## 議題 2: philosophy.md 追記内容（独占 4 軸 + 業界 5 パターン位置付け + CaaF/CDD 新規導入の是非）

### 背景

HANDOFF Section 5 タスク D は philosophy.md レベルでの位置付け明文化を要求。本案件で「DH は業界実装を吸収するが、業界の語彙で DH を説明することはできない」という独占性を philosophy で規範化する必要がある。philosophy.md は **二層実装**（`harness-verifier/PHILOSOPHY.md` + `.claude/skills/layer0-spec-architect/references/philosophy.md`）のため、両ファイルに整合的に追記する必要がある。

### 上程する追記文 3 候補

#### 候補 P1: 業界実装吸収方針（必須追記）

```
DH は業界実装プリミティブを「吸収して使う」のではなく、
「同等以上のものをドメイン固有で生成できる方法論」を目指す。
参照標本としての吸収は許容するが、業界の語彙で DH を説明することはできない。
```

**配置先**: philosophy.md 第 7 条「AI 組織論」の後に第 8 条候補 として、または既存条文の補論として
**整合性**: 既存第 1-7 条と矛盾なし、AI 組織論第 7 条「4 役割 + サポート」が業界実装吸収の受け皿として既に確立されているため、その上に位置付けを明文化する形

#### 候補 P2: 業界 5 パターンの位置付け（必須追記）

```
DH は業界の協調パターン（業界 5 パターン: agent定義 / skill定義 / hook機構 /
security scanner / instinct学習）を設計プリミティブとして包含し得るが、
これらは DH の方法論層の出力先（D2 = 開発環境、D3 = 配布 skill）であって、
DH 自体ではない。DH は対話 → 仕様 → 自律実装 → 検証 → 献上の方法論層に位置する。
```

**配置先**: 第 8 条候補後半、または `harness-verifier/PHILOSOPHY.md` の D4 メタスキル層の存在論節
**整合性**: D1-D5 5 次元論と整合、業界 5 パターンが D2-D3 出力に対応することを明示

#### 候補 P3: 独占 4 軸の規範化（必須追記）

```
対話・フラクタル・献上・5 次元は DH の中核独自領域であり、
業界実装プリミティブには対応概念が存在しない。
これらは DH の方法論層の独占構成要素であり、業界吸収によって希釈されない。
```

**配置先**: `harness-verifier/PHILOSOPHY.md` の D4 メタスキル層存在論節（規律の自己相似性の系として）
**整合性**: 既存第 1 条「フラクタル原則」第 6 条「人間最終承認」と直接連結、第 8 条候補として系統化

### 議論論点

#### 論点 2.1: CaaF / CDD 新規用語の導入是非

- HANDOFF が独自に持ち込んだ用語、DH 内出現数 **0**
- 既存 `dialog-questions.md` + `subphase-common-protocol.md` の α/β/γ/δ 4 フェーズ骨格と意味的重複
- **導入賛成**: 業界向け広報文脈で識別子として有用、対外説明に名前があると伝達効率↑
- **導入反対**: 用語増殖、既存 dialog-questions 概念で十分、HANDOFF 独自ラベルを正式採用する説明責任が DH 内に欠ける

**L0 推奨**: 用語の正式導入は **保留**（議題 2 で Council 判断）、philosophy 追記では「対話」のままで、必要なら別途 v6.0.0 候補として用語化を温存

#### 論点 2.2: 第 8 条新設か既存条文補論か

- 第 8 条新設: 構造的明確性高、変更影響大（philosophy.md ナンバリング変動）
- 既存条文の補論として埋込: 影響小、構造的見通し悪化

**L0 推奨**: **第 8 条新設**（v5.12.0 minor、追加のみ・破壊なし）

#### 論点 2.3: 二層 philosophy.md への配分

| 追記内容 | `harness-verifier/PHILOSOPHY.md` | `.claude/skills/layer0-spec-architect/references/philosophy.md` |
|---|---|---|
| P1（業界吸収方針） | ✓ 簡潔版 | ✓ 詳説版（業界 5 パターン具体例含む） |
| P2（業界 5 パターン位置付け） | △ 概要のみ | ✓ 完全版 |
| P3（独占 4 軸規範化） | ✓ 完全版（D4 存在論の系として） | ✓ 完全版 |

### 求める Council 判定

1. P1 / P2 / P3 各候補の文言を承認 / 修正 / 棄却
2. CaaF / CDD 用語導入の是非
3. 第 8 条新設 vs 既存条文補論
4. 二層 philosophy.md への配分案承認

---

## 議題上程後のフロー

1. Council 発動（crosscut-council Phase 1 SDK 独立呼出）
2. 3 ペルソナ（経営者 / 開発者 / 哲学者）が並列独立判定（business Council 固定）
3. judgment_confidence + 重み付き判定取得
4. final_decision は null（人間最終承認待ち）→ ユーザーが承認
5. 採決結果を `delivery/COUNCIL-DECISION-metaskill-YYYY-MM-DDTHH:MM:SSZ.md` に記録
6. 議題 1 採決 → `refs-draft/` 移動、議題 2 採決 → Phase 1（タスク D）着手

---

## 起動コマンド想定

```
Council を発動。議題 1 と議題 2 を上程。
入力: delivery/COUNCIL-AGENDA-metaskill-2026-05-11.md
出力: delivery/COUNCIL-DECISION-metaskill-{timestamp}.md
```
