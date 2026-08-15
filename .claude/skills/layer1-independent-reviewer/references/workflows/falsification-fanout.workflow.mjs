// falsification-fanout.workflow.mjs — 反証チェック（処理フロー 5.10）の並列実行基盤
// v6.11.0 F3（upgrade-spec-v6.11.0.md）。falsification-protocol.md が定める反証 3 類型
// （A 挙動反証 / B テスト反証 / C Oracle 反証）を critical 機能ごとに並列試行する。
// - 反証記録は schema 強制（F3-1: 対象 / 類型 / 試行内容 / 結果）
// - 「この PASS が保証しない範囲」欄を必須出力に含める（F3-2）
// - B 類型（ミューテーション）は worktree 隔離で実行し原状復帰を構造保証。
//   preserve 領域（archeo no_modification）の機能では B 類型を起動しない（F3-3）
// - degrade 経路（仕様 C-2）: Workflow tool 非対応環境では falsification-protocol.md の
//   手動手順（reviewer 本体が直列に試行）で完遂する
//
// 呼び出し: Workflow({ scriptPath: ".../falsification-fanout.workflow.mjs",
//   args: { repo_root, project_root,
//           features: [{ name, priority, spec_excerpt, preserve }] } })

export const meta = {
  name: 'falsification-fanout',
  description: '反証 3 類型（挙動/テスト/Oracle）を critical 機能ごとに並列試行し反証記録を生成',
  phases: [
    { title: 'Falsify', detail: '機能×類型の並列反証試行' },
    { title: 'Scope', detail: '「この PASS が保証しない範囲」の統合' },
  ],
}

const REQUIRED = ['repo_root', 'project_root', 'features']
const missing = REQUIRED.filter(k => !args || args[k] == null)
if (missing.length) return { status: 'pre_check_failed', reason: `required field(s) missing: ${missing.join(', ')}` }
if (!Array.isArray(args.features) || args.features.length === 0)
  return { status: 'pre_check_failed', reason: 'features must be a non-empty array' }
const R = String(args.repo_root).replace(/\/$/, '')
const P = String(args.project_root).replace(/\/$/, '')
const PROTOCOL = `${R}/.claude/skills/layer1-independent-reviewer/references/falsification-protocol.md`

const ATTEMPT_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    target: { type: 'string', description: '対象機能名' },
    type: { type: 'string', enum: ['A', 'B', 'C'] },
    attempt: { type: 'string', description: '試行内容（何をどう壊そうとしたか）' },
    result: { type: 'string', enum: ['反証不成立', '反証成立', '提起'] },
    detail: { type: 'string', description: '結果の根拠。B 類型は原状復帰確認（diff clean）を必ず含める' },
  },
  required: ['target', 'type', 'attempt', 'result', 'detail'],
}

// リスクベース選定（falsification-protocol §1）: critical は必須、それ以外はスキップして未実施を保証範囲外へ記録
const targets = args.features.filter(f => f.priority === 'critical')
const skipped = args.features.filter(f => f.priority !== 'critical')

const typePrompt = (f, t) => {
  const base = `あなたは独立検証の反証試行エージェントである。${PROTOCOL} を読み、その規約に従うこと。
プロジェクト: ${P}
対象機能: ${f.name}
SPEC 抜粋: ${f.spec_excerpt}
`
  if (t === 'A') return base + `類型 A（挙動反証）: SPEC 記述から境界値・異常系・順序/並行の counterexample を導出して実際に実行し、SPEC の保証を破る挙動を探せ（試行 1〜3 件）。導出元は SPEC 記述のみ — 実装コードから「通りそうな入力」を逆算しない。`
  if (t === 'B') return base + `類型 B（テスト反証・test-the-tests）: 対象機能の実装 1 箇所を意図的に壊し、対応テストが FAIL することを確認して必ず原状復帰せよ（作業は worktree 内・復元後の diff clean 確認を detail に記録）。あわせて恒真アサーション / over-mock / 自己整合テストを静的検出せよ。`
  return base + `類型 C（Oracle 反証）: 対象機能のテストの観測点が SPEC の保証を観測できているかを問え（HTTP 200 のみで DB/キュー状態を見ていない等）。不足観測点は result: "提起" として記録せよ（テストを増やす検査ではない）。`
}

phase('Falsify')
const attempts = (await pipeline(
  targets,
  (f) => parallel([
    () => agent(typePrompt(f, 'A'), { label: `A:${f.name}`, phase: 'Falsify', schema: ATTEMPT_SCHEMA }),
    // preserve 領域では B 類型（ミューテーション）を起動しない（一時的でも変更禁止と衝突）
    ...(f.preserve ? [] : [() => agent(typePrompt(f, 'B'), { label: `B:${f.name}`, phase: 'Falsify', schema: ATTEMPT_SCHEMA, isolation: 'worktree' })]),
    () => agent(typePrompt(f, 'C'), { label: `C:${f.name}`, phase: 'Falsify', schema: ATTEMPT_SCHEMA }),
  ]),
)).flat().filter(Boolean)

phase('Scope')
const SCOPE_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: { uncovered_scope: { type: 'array', items: { type: 'string' }, description: '試行しなかった反証・観測していない状態・実行していない経路（1-3 行相当）' } },
  required: ['uncovered_scope'],
}
const scope = await agent(
  `以下の反証試行記録とスキップ済み機能一覧から、「この PASS が保証しない範囲」を 1〜3 行で列挙せよ（falsification-protocol §4。省略はセンサー FAIL 扱いのため空配列は返さない）。
試行記録: ${JSON.stringify(attempts)}
反証スキップ（critical 以外）: ${JSON.stringify(skipped.map(f => f.name))}
preserve 領域で B 類型を省略した機能: ${JSON.stringify(targets.filter(f => f.preserve).map(f => f.name))}`,
  { label: 'uncovered-scope', phase: 'Scope', schema: SCOPE_SCHEMA, effort: 'low' },
)

const falsified = attempts.filter(a => a.result === '反証成立')
log(`falsification-fanout 完了: 試行 ${attempts.length} 件 / 反証成立 ${falsified.length} 件`)
return {
  status: 'ok',
  attempts,                    // VERIFICATION.md「反証記録」表の行データ
  uncovered_scope: scope ? scope.uncovered_scope : ['（統合失敗 — reviewer が手動で記載すること）'],
  has_falsified: falsified.length > 0,   // true → FAIL 確定（反証が確証に優先、escalation-matrix §2 (iv)）
  next_steps: 'attempts と uncovered_scope を VERIFICATION.md「反証記録」セクションへ転記。反証成立があれば FAIL 差戻し（提起のみ）',
}
