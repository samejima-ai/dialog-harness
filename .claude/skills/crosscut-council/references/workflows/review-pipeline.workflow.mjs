// review-pipeline.workflow.mjs — dialog-harness PR レビュー Council の決定論実行基盤
// v6.11.0 F2（upgrade-spec-v6.11.0.md）。claude-review.yml の OC が回してきた
// Phase 1-a〜3-c（fetch / difficulty / intent-gate / evidence / persona×3 / judgment）を
// pipeline 化する。既存 review-* サブエージェント定義（.claude/agents/）を agentType で再利用し、
// プロンプト資産は書き換えない（F2-1）。フィールド単位の出力規格の正典は
// .github/reviews/ の output-format（§3/§4）が持ち、本スクリプトは JSON 構造化のみを強制する（F2-2）。
// ローカル実行可能（F2-4・I-2）: CI からも同一スクリプトを呼ぶ。
// degrade 経路（仕様 C-2）: Workflow tool 非対応環境では従来どおり OC が subagent を個別起動して完遂する。
//
// 呼び出し: Workflow({ scriptPath: ".../review-pipeline.workflow.mjs",
//                      args: { pr_number, repo_root } })

export const meta = {
  name: 'review-pipeline',
  description: 'PR レビュー Council（fetch→評価 3 種→3 ペルソナ独立→judgment）の実行基盤',
  phases: [
    { title: 'Fetch', detail: 'PR bundle 取得（推論なし）' },
    { title: 'Assess', detail: 'difficulty / intent-gate / evidence 並列' },
    { title: 'Council', detail: '3 ペルソナ独立評価（相互参照なし）' },
    { title: 'Judgment', detail: '決定論 conflict_type + 判定' },
  ],
}

const REQUIRED = ['pr_number', 'repo_root']
const missing = REQUIRED.filter(k => !args || args[k] == null || args[k] === '')
if (missing.length) return { status: 'pre_check_failed', reason: `required field(s) missing: ${missing.join(', ')}` }
const R = String(args.repo_root).replace(/\/$/, '')
// 既知の限界（独立検証 v6.11.0 P-6 / upgrade-spec §既知の限界）: 本スクリプトは JSON 構造化のみを強制し、
// フィールド単位の schema 強制（output-format §3/§4 準拠）は次サイクル。既存 review-* agent が
// output-format を自ら参照するため実害は限定的だが、F1 のような構造強制には至っていない
const OBJ = { type: 'object' }

phase('Fetch')
const bundle = await agent(
  `PR #${args.pr_number} の title / body / diff / 変更ファイル一覧 / linked Issue / 参照設計 doc / コメント履歴を取得し、コンパクトな JSON bundle を返せ。判断・評価はしない。`,
  { label: 'fetch', phase: 'Fetch', agentType: 'review-fetch', schema: OBJ, effort: 'low' },
)
if (!bundle) return { status: 'workflow_failed', reason: 'fetch 失敗。従来経路（OC の個別 subagent 起動）へ degrade せよ' }
const bundleStr = JSON.stringify(bundle)

phase('Assess')
const [difficulty, intentGate, evidence] = await parallel([
  () => agent(`以下の PR bundle の難度 tier (1/2/3) を依存深度中心に保守的に判定し JSON を返せ。\n${bundleStr}`,
    { label: 'difficulty', phase: 'Assess', agentType: 'review-difficulty', schema: OBJ, effort: 'low' }),
  () => agent(`以下の PR bundle について、PR 本文が実質的な diff の意図・トレードオフを述べているかを diff 単位で判定し JSON を返せ。\n${bundleStr}`,
    { label: 'intent-gate', phase: 'Assess', agentType: 'review-intent-gate', schema: OBJ, effort: 'low' }),
  () => agent(`以下の PR bundle の変更ファイルに対し利用可能な linter/formatter/型チェック/test を実行または既存出力を収集し、file:line + tool verdict の Evidence 項目に正規化して JSON を返せ。推論的判断はしない。\n${bundleStr}`,
    { label: 'evidence', phase: 'Assess', agentType: 'review-evidence', schema: OBJ, effort: 'low' }),
])

phase('Council')
const PERSONA_AGENTS = { 経営者: 'review-persona-ceo', 開発者: 'review-persona-dev', 哲学者: 'review-persona-phil' }
const personaInput = JSON.stringify({ bundle, evidence, intent_gate: intentGate })
// 情報純度: 各ペルソナには bundle + evidence のみを渡す。他ペルソナ出力を渡す経路は存在しない
const personas = (await parallel(Object.entries(PERSONA_AGENTS).map(([name, at]) => () =>
  agent(`以下の PR レビュー入力を独立評価し、output-format §3 の Persona 出力 JSON のみ返せ。dimension を必ず含めること。schema に収まらない異見・違和感があれば notes フィールドに自由記述してよい。\n${personaInput}`,
    { label: `persona:${name}`, phase: 'Council', agentType: at, schema: OBJ })
    .then(o => o ? { ...o, persona: name } : null)
))).filter(Boolean)
if (personas.length < 3) return { status: 'workflow_failed', reason: `persona 出力 ${personas.length}/3。従来経路へ degrade せよ`, partial: { bundle, difficulty, intentGate, evidence, personas } }

// conflict_type は決定論（v6.7.0 3 値・council-fanout と同一契約）
// 正典と同値契約: council-axis-audit.py `_dimension_tokens`（`/` `／` 区切り・完全一致）
const tokenize = (s) => new Set(String(s || '').split(/[/／]/).map(t => t.trim()).filter(Boolean))
const jaccard = (a, b) => { const A = tokenize(a), B = tokenize(b); const i = [...A].filter(x => B.has(x)).length; const u = new Set([...A, ...B]).size; return u === 0 ? 0 : i / u }
const stances = personas.map(p => p.stance)
const allSame = stances.every(s => s === stances[0])
let conflictType = 'simple_conflict'
if (allSame) {
  const pairs = []
  for (let i = 0; i < personas.length; i++) for (let j = i + 1; j < personas.length; j++) pairs.push(jaccard(personas[i].dimension, personas[j].dimension))
  conflictType = pairs.every(x => x <= 0.30) ? 'reason_divergence' : 'unanimous'
}

phase('Judgment')
// final_weights は council-weights.md 由来（ハードコードは単一情報源バイパス。独立検証 P-7）
const WEIGHTS_SCHEMA = { type: 'object', properties: { 経営者: { type: 'number' }, 開発者: { type: 'number' }, 哲学者: { type: 'number' } }, required: ['経営者', '開発者', '哲学者'], additionalProperties: false }
const finalWeights = await agent(
  `${R}/.claude/skills/crosscut-council/council-weights.md の fenced YAML から business Council の final_weight を計算して JSON で返せ: base_weights × ethos_multiplier + situational_modifier["maintenance"]（PR レビューは保守判断）。値の解釈・改変はせず計算のみ。`,
  { label: 'read:weights', phase: 'Judgment', schema: WEIGHTS_SCHEMA, effort: 'low' },
) || { 経営者: 3, 開発者: 5, 哲学者: 2 }  // 読取失敗時の degrade（maintenance 補正の既定値）
const judgment = await agent(
  `以下の 3 ペルソナ出力 + final_weights + conflict_type を受け取り、weighted_score = Σ(weight×confidence) で recommended を決定し、output-format §4 の判定 JSON のみ返せ。final_decision は常に null。\n${JSON.stringify({ personas, final_weights: finalWeights, conflict_type: conflictType, difficulty })}`,
  { label: 'judgment', phase: 'Judgment', agentType: 'review-judgment', schema: OBJ },
)
if (!judgment) return { status: 'judgment_failed', reason: 'judgment 失敗。従来経路へ degrade し人間に warn を残せ', partial: { bundle, difficulty, intentGate, evidence, personas, conflict_type: conflictType } }

log(`review-pipeline 完了: PR #${args.pr_number} / ${conflictType}`)
return {
  status: 'ok',
  pr_number: args.pr_number,
  difficulty, intent_gate: intentGate, evidence,
  personas, conflict_type: conflictType, final_weights: finalWeights,
  judgment: { ...judgment, final_decision: null },
}
