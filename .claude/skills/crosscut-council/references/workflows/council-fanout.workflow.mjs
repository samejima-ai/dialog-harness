// council-fanout.workflow.mjs — Council business 3 軸独立観測 + 決定論評定の実行基盤
// v6.11.0 F1（upgrade-spec-v6.11.0.md）。crosscut-council/SKILL.md §処理フローの実行体。
//
// 呼び出し: Workflow({ scriptPath: ".claude/skills/crosscut-council/references/workflows/council-fanout.workflow.mjs",
//                      args: { context, options, question_to_answer, source_skill, category,
//                              decision_category, invocation_id, timestamp, repo_root } })
// - invocation_id / timestamp は呼び出し側（Pre-Check 採番者）が渡す（スクリプト内で Date 不可）
// - H1-H4 は本スクリプトを呼ばず即時人間献上（呼んでも status: "escalate_to_human" で即返す）
// - degrade 経路（仕様 C-2）: Workflow tool 非対応環境・judgment_failed 時は従来 subagent 手動フローで完遂
// - 決定論部（Phase 0 検証 / 重み計算 / 対立度判定 / weighted_score / 帯）は全て本スクリプト内 JS。LLM 不使用
// - 帯・閾値の正典は judgment-agent.md §confidence 帯 / conflict-typology.md（DIMENSION_JACCARD_MAX = 0.30）。
//   校正時は正典と本スクリプトを同時更新すること（片方だけ変えると検算が恒常的に落ちる）

export const meta = {
  name: 'council-fanout',
  description: 'Council 3軸独立観測→決定論の重み付き評定→§8ログブロック生成',
  phases: [
    { title: 'Weights', detail: 'council-weights.md 読取と決定論の重み計算' },
    { title: 'Phase1', detail: '3ペルソナ独立並列観測（相互参照なし）' },
    { title: 'Phase3', detail: '決定論スコアリング + Judgment（帯検算つき）' },
  ],
}

// ---- Phase 0: 入力検証（決定論・pre-check.md 準拠） ----
const REQUIRED = ['context', 'options', 'question_to_answer', 'source_skill', 'category', 'decision_category', 'invocation_id', 'timestamp', 'repo_root']
const missing = REQUIRED.filter(k => !args || args[k] == null || args[k] === '')
if (missing.length) return { status: 'pre_check_failed', reason: `required field(s) missing: ${missing.join(', ')}`, required_fields: REQUIRED }
if (!Array.isArray(args.options) || args.options.length < 2 || args.options.length > 8)
  return { status: 'pre_check_failed', reason: 'options must be an array of 2-8 entries' }
if (/^H[1-4]$/.test(args.decision_category))
  return { status: 'escalate_to_human', reason: 'H カテゴリは人間専管（philosophy 第6条）。Council を起動しない' }
if (!/^C[1-4]$/.test(args.decision_category))
  return { status: 'pre_check_failed', reason: `decision_category must be C1-C4 or H1-H4, got: ${args.decision_category}` }

const KNOWN_CATEGORIES = ['implementation', 'operation', 'maintenance', 'issue_triage', 'error_handling', 'judgment', 'conception']
const categoryFallback = !KNOWN_CATEGORIES.includes(args.category)
const category = categoryFallback ? 'judgment' : args.category
const R = args.repo_root.replace(/\/$/, '')

// ---- Weights: council-weights.md の YAML を読取（単一情報源維持のため agent が読む）→ 決定論計算 ----
phase('Weights')
const WEIGHTS_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    base_weights: { type: 'object', properties: { 経営者: { type: 'number' }, 開発者: { type: 'number' }, 哲学者: { type: 'number' } }, required: ['経営者', '開発者', '哲学者'], additionalProperties: false },
    ethos_multiplier: { type: 'object', properties: { 経営者: { type: 'number' }, 開発者: { type: 'number' }, 哲学者: { type: 'number' } }, required: ['経営者', '開発者', '哲学者'], additionalProperties: false },
    situational_modifier: { type: 'object', additionalProperties: { type: 'object', properties: { 経営者: { type: 'number' }, 開発者: { type: 'number' }, 哲学者: { type: 'number' } }, required: ['経営者', '開発者', '哲学者'], additionalProperties: false } },
  },
  required: ['base_weights', 'ethos_multiplier', 'situational_modifier'],
}
const weightsDoc = await agent(
  `${R}/.claude/skills/crosscut-council/council-weights.md の fenced YAML ブロック（base_weights / ethos_multiplier / situational_modifier）を読み、business Council 分のみを JSON で返せ。値の解釈・改変はせず転記のみ行うこと。`,
  { label: 'read:council-weights', phase: 'Weights', schema: WEIGHTS_SCHEMA, effort: 'low' },
)
if (!weightsDoc) return { status: 'workflow_failed', reason: 'council-weights.md の読取に失敗。従来経路（subagent 手動フロー）へ degrade せよ' }

const PERSONAS = ['経営者', '開発者', '哲学者']
const finalWeights = {}
for (const p of PERSONAS) {
  const mod = (weightsDoc.situational_modifier[category] || weightsDoc.situational_modifier['judgment'] || {})[p] || 0
  finalWeights[p] = weightsDoc.base_weights[p] * weightsDoc.ethos_multiplier[p] + mod
}
const sigmaW = PERSONAS.reduce((s, p) => s + finalWeights[p], 0)

// ---- Phase 1: 3 ペルソナ独立並列（情報純度: 本スクリプト構造が相互参照経路を持たない） ----
phase('Phase1')
const PERSONA_FILES = { 経営者: 'ceo.md', 開発者: 'dev.md', 哲学者: 'phil.md' }
const stanceEnum = [...args.options, '保留', '第3の道']
const PERSONA_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    persona: { type: 'string' },
    stance: { type: 'string', description: '立場の自由記述（options のいずれか、または独自の第3の道）' },
    stance_normalized: { type: 'string', enum: stanceEnum, description: 'stance を options へ正規化した値。options で表せないなら「第3の道」、判断保留なら「保留」' },
    reason: { type: 'string', maxLength: 600 },
    confidence: { type: 'number', minimum: 0, maximum: 1 },
    dimension: { type: 'string', description: '評価軸（必須・ROI / 保守性 / 意味 等）' },
    premise: { type: 'string' },
    concerns: { type: 'array', items: { type: 'string' }, maxItems: 5 },
    notes: { type: 'string', description: 'schema に収まらない異見・違和感の自由記述（任意。仕様 C-3 の受け皿）' },
  },
  required: ['persona', 'stance', 'stance_normalized', 'reason', 'confidence', 'dimension', 'premise', 'concerns'],
}
const personaPrompt = (p) => `あなたは dialog-harness Council System の Persona エージェント（${p}軸）である。
1. ${R}/.claude/skills/crosscut-council/references/personas/business/${PERSONA_FILES[p]} を読み、その system prompt に完全に従うこと。
2. 情報純度原則: 他ペルソナのファイル・出力、history/COUNCIL-LOG.md を読んではならない。context 内で参照されたファイルは読んでよい。

## 議題 context
${args.context}

## options
${args.options.map((o, i) => `${i + 1}. ${o}`).join('\n')}

## question_to_answer
${args.question_to_answer}

独立に観測し、構造化出力を返せ。stance_normalized は options のいずれか（表せないなら「第3の道」）。dimension は必須。schema に収まらない違和感があれば notes に書け。`

const personas = await parallel(PERSONAS.map(p => () =>
  agent(personaPrompt(p), { label: `persona:${p}`, phase: 'Phase1', schema: PERSONA_SCHEMA })
    .then(out => out ? { ...out, persona: p } : null)
))
const valid = personas.filter(Boolean)
const malformedCount = PERSONAS.length - valid.length
if (valid.length === 0) return { status: 'workflow_failed', reason: '全ペルソナが失敗。従来経路へ degrade せよ' }

// ---- 対立度判定（決定論・v6.7.0 3 値） ----
// 正典と同値契約: conflict-typology.md / scripts/council-axis-audit.py `_dimension_tokens`
// （`/` `／` 区切り・完全一致・lowercase しない）。片方だけ変えると監査と分類器が食い違う
const tokenize = (s) => new Set(String(s).split(/[/／]/).map(t => t.trim()).filter(Boolean))
const jaccard = (a, b) => {
  const A = tokenize(a), B = tokenize(b)
  const inter = [...A].filter(x => B.has(x)).length
  const uni = new Set([...A, ...B]).size
  return uni === 0 ? 0 : inter / uni
}
const DIMENSION_JACCARD_MAX = 0.30 // council-axis-audit.py と同値契約
const stances = valid.map(v => v.stance_normalized)
const allSame = stances.every(s => s === stances[0])
let conflictType
if (!allSame) conflictType = 'simple_conflict'
else {
  const pairs = []
  for (let i = 0; i < valid.length; i++) for (let j = i + 1; j < valid.length; j++) pairs.push(jaccard(valid[i].dimension, valid[j].dimension))
  conflictType = pairs.every(x => x <= DIMENSION_JACCARD_MAX) ? 'reason_divergence' : 'unanimous'
}

// ---- weighted_score（決定論） ----
const round2 = (x) => Math.round(x * 100) / 100
const inOptions = valid.filter(v => args.options.includes(v.stance_normalized))
const thirdWay = valid.filter(v => !args.options.includes(v.stance_normalized))
const scoreMap = {}
for (const v of inOptions) {
  scoreMap[v.stance_normalized] ||= { stance: v.stance_normalized, supporters: [], weight_sum: 0, _raw: 0, components: [] }
  const e = scoreMap[v.stance_normalized]
  e.supporters.push(v.persona)
  e.weight_sum += finalWeights[v.persona]
  e._raw += finalWeights[v.persona] * v.confidence   // 総和後に丸める（正典: 逐次丸めは誤差を生む）
  e.components.push({ persona: v.persona, weight: finalWeights[v.persona], confidence: v.confidence })
}
const scores = Object.values(scoreMap)
  .map(e => ({ stance: e.stance, supporters: e.supporters, weight_sum: e.weight_sum, weighted_score: round2(e._raw), _raw: e._raw, components: e.components }))
  .sort((a, b) => b._raw - a._raw)
// tie 判定は丸め前の生値で「差 < 0.01」（正典）。丸め後の厳密等値だと境界で取り逃す
const tieBreak = scores.length >= 2 && Math.abs(scores[0]._raw - scores[1]._raw) < 0.01
const maxScoreStance = scores.length === 0 ? null : (tieBreak ? null : scores[0].stance)

// ---- 帯計算（judgment-agent.md §confidence 帯・決定論） ----
// 全 persona が options 外（保留・第3の道のみ）→ 選択形式では吸収不能。判定を降りて人間へ
if (scores.length === 0) return {
  status: 'escalate_to_human',
  reason: '全 persona の stance が options 外（scores 空）。選択肢では吸収できないシグナルのため判定を降りる',
  personas: valid, conflict_type: conflictType, final_weights: finalWeights,
  third_way_excluded: thirdWay.map(v => ({ persona: v.persona, stance: v.stance, weight: finalWeights[v.persona], confidence: v.confidence })),
}
let band
if (malformedCount > 0) band = { lo: 0.00, hi: 0.30, basis: 'malformed' }
else if (tieBreak) band = { lo: 0.00, hi: 0.39, basis: 'tie_break' }
else if (allSame) band = conflictType === 'reason_divergence' ? { lo: 0.60, hi: 0.90, basis: 'reason_divergence' } : { lo: 0.45, hi: 0.70, basis: 'unanimous' }
else {
  const gapRatio = scores.length >= 2 ? (scores[0]._raw - scores[1]._raw) / sigmaW : scores[0]._raw / sigmaW
  band = gapRatio < 0.10 ? { lo: 0.30, hi: 0.50, basis: 'gap_ratio' } : gapRatio < 0.25 ? { lo: 0.45, hi: 0.70, basis: 'gap_ratio' } : { lo: 0.60, hi: 0.90, basis: 'gap_ratio' }
}
const thirdWayWeight = thirdWay.reduce((s, v) => s + finalWeights[v.persona], 0)
// 正典 compute_confidence_band: hi を 0.50 に切り下げたら lo も min(lo, hi - 0.10) に補正する。
// この 1 行がないと [0.60, 0.50] の空帯が生まれ、jc が論理的に帯内に収まらず恒常 judgment_failed になる
if (thirdWayWeight / sigmaW >= 0.30 && band.hi > 0.50) {
  const hi = 0.50
  band = { lo: round2(Math.min(band.lo, hi - 0.10)), hi, basis: 'third_way_ratio' }
}

// ---- Phase 3: Judgment（帯だけ渡す — gap 生値は渡さない） ----
phase('Phase3')
const JUDGMENT_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    recommended: { type: 'string' },
    reasoning: { type: 'string', maxLength: 1000 },
    minority_opinion: { type: 'string', maxLength: 400 },
    weight_note: { type: 'string', maxLength: 200 },
    judgment_confidence: { type: 'number', minimum: 0, maximum: 1 },
  },
  required: ['recommended', 'reasoning', 'minority_opinion', 'weight_note', 'judgment_confidence'],
}
const judgmentPrompt = (retryNote) => `あなたは dialog-harness Council の Judgment Agent（人格なし・低温度）である。
${R}/.claude/skills/crosscut-council/references/judgment-agent.md を読み、その規格に従うこと。

## 入力
question_to_answer: ${args.question_to_answer}
conflict_type: ${conflictType}（reason_divergence なら多様性として質を評価。unanimous なら被覆不足を疑う）
final_weights: ${JSON.stringify(finalWeights)}
scores（決定論計算済み・検算不要）: ${JSON.stringify(scores)}
third_way_excluded: ${JSON.stringify(thirdWay.map(v => ({ persona: v.persona, stance: v.stance, weight: finalWeights[v.persona], confidence: v.confidence })))}
persona 出力（reason / concerns / notes 含む）: ${JSON.stringify(valid)}

## 制約
- recommended は max_score_stance「${maxScoreStance}」を骨格とし、敗れた軸・第3の道の主張は minority_opinion と本文へ吸収する
- judgment_confidence は帯 [${band.lo}, ${band.hi}] の内側でのみ自己評価せよ（帯は決定論計算済み）
- final_decision は常に null（あなたは決定しない）
${retryNote || ''}`

// リトライ上限は正典 output-format.md §バリデーション「最大 1 回リトライ、2 回目も不一致なら judgment_failed」に一致させる
let judgment = null
let retries = 0
for (; retries <= 1; retries++) {
  const j = await agent(judgmentPrompt(retries ? `- 前回出力の judgment_confidence が帯外だった。帯 [${band.lo}, ${band.hi}] の内側で再評価せよ` : ''),
    { label: `judgment${retries ? `:retry${retries}` : ''}`, phase: 'Phase3', schema: JUDGMENT_SCHEMA })
  if (j && j.judgment_confidence >= band.lo && j.judgment_confidence <= band.hi) { judgment = j; break }
}
if (!judgment) return {
  status: 'judgment_failed', reason: `judgment_confidence が帯 [${band.lo}, ${band.hi}] に 3 回収まらず。従来経路へ degrade し人間に warn を残せ`,
  personas: valid, conflict_type: conflictType, final_weights: finalWeights, scores,
}

// ---- §8 ログブロック生成（output-format.md §8・フィールド欠落の構造的排除） ----
// YAML ダブルクォート文字列のエスケープ: バックスラッシュ → クォート → 改行/タブの順（順序が逆だと二重エスケープ）。
// 改行を残すと行ベースパーサ（council-log-sync.py / council-axis-audit.py）がエントリを読めず CTL から脱落する
const y = (s) => String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\r?\n/g, '\\n').replace(/\t/g, '\\t')
const logBlock = [
  `- invocation_id: "${y(args.invocation_id)}"`,
  `  timestamp: "${y(args.timestamp)}"`,
  `  source_skill: "${y(args.source_skill)}"`,
  `  question_to_answer: "${y(args.question_to_answer)}"`,
  `  council_type: "business"`,
  `  category: "${category}"`,
  `  category_fallback: ${categoryFallback}`,
  `  decision_category: "${args.decision_category}"`,
  `  phase_reached: "phase_3"`,
  // execution_mode は本スクリプトが到達した時点で必ず workflow（Council `wfdflt`・2026-08-29）。
  // 手動 degrade 側は自己申告ゆえ漏れうるので、council-axis-audit.py が
  // components / weight_calculation_retry_count / confidence_band の有無から推定した値と突合する
  `  execution_mode: "workflow"`,
  `  degrade_reason: null`,
  `  conflict_type: "${conflictType}"`,
  `  options:`,
  ...args.options.map(o => `    - "${y(o)}"`),
  `  final_weights:`,
  ...PERSONAS.map(p => `    ${p}: ${finalWeights[p]}`),
  `  persona_summary:`,
  ...valid.map(v => `    ${v.persona}: { stance: "${y(v.stance_normalized)}", confidence: ${v.confidence}, dimension: "${y(v.dimension)}"${v.notes ? `, note: "${y(v.notes)}"` : ''} }`),
  `  judgment_confidence: ${judgment.judgment_confidence}`,
  `  weight_calculation:`,
  `    method: "weight_times_confidence"`,
  `    max_score_stance: ${maxScoreStance === null ? 'null' : `"${y(maxScoreStance)}"`}`,
  `    scores:`,
  ...scores.flatMap(s2 => [
    `      - stance: "${y(s2.stance)}"`,
    `        supporters: [${s2.supporters.map(x => `"${x}"`).join(', ')}]`,
    `        weight_sum: ${s2.weight_sum}`,
    `        weighted_score: ${s2.weighted_score}`,
    `        components:`,
    ...s2.components.map(c => `          - { persona: "${c.persona}", weight: ${c.weight}, confidence: ${c.confidence} }`),
  ]),
  `    third_way_excluded:${thirdWay.length ? '' : ' []'}`,
  ...thirdWay.map(v => `      - { persona: "${v.persona}", stance: "${y(v.stance)}", weight: ${finalWeights[v.persona]}, confidence: ${v.confidence}, reason: "options 外の自由記述。weight 非加算・minority_opinion へ転載" }`),
  `    tie_break_applied: ${tieBreak}`,
  `  weight_calculation_retry_count: ${retries}`,
  `  confidence_band: { lo: ${band.lo}, hi: ${band.hi}, basis: "${band.basis}" }`,
  `  recommended: "${y(judgment.recommended)}"`,
  `  minority_opinion: "${y(judgment.minority_opinion)}"`,
  `  weight_note: "${y(judgment.weight_note)}"`,
  `  reasoning: "${y(judgment.reasoning)}"`,
  `  consensus_mode: "escalate_to_human"`,
  `  human_escalated: ${judgment.judgment_confidence < 0.5}`,
  `  final_decision: null`,
  `  implementer_consent: null  # 合意プロセス完了時に単方向埋め込み`,
].join('\n')

log(`council-fanout 完了: ${conflictType} / recommended=${judgment.recommended.slice(0, 40)}... / jc=${judgment.judgment_confidence}`)
return {
  status: judgment.judgment_confidence < 0.5 ? 'escalate_to_human' : 'ok',
  pre_check: { council_type: 'business', category, category_fallback: categoryFallback, decision_category: args.decision_category, invocation_id: args.invocation_id },
  final_weights: finalWeights,
  personas: valid,
  conflict_type: conflictType,
  weight_calculation: { method: 'weight_times_confidence', scores: scores.map(({ _raw, ...rest }) => rest), third_way_excluded: thirdWay.map(v => ({ persona: v.persona, stance: v.stance, weight: finalWeights[v.persona], confidence: v.confidence })), max_score_stance: maxScoreStance, tie_break_applied: tieBreak },
  confidence_band: band,
  judgment: { ...judgment, final_decision: null },
  log_block: logBlock,
  next_steps: 'log_block を history/COUNCIL-LOG.md へ追記し、scripts/council-log-sync.py sync --recompute を実行すること（クロージング手順）',
}
