/**
 * spec/domain.ts — L0-2 ドメインモデル（完全モード）
 *
 * Zod + TypeScript でケロぴの森のドメイン型を定義。
 * 互換性ポリシー: additive only（既存フィールド削除禁止）。
 * 列挙型の拡張は許容（例: subject に Phase 2 で他教科追加）。
 */

import { z } from "zod";

// ============================================================
// 列挙型
// ============================================================

export const SubjectSchema = z.enum([
  "math", // Phase 1
  // "japanese", "english", "science", "social" — Phase 2 で追加予定
]);
export type Subject = z.infer<typeof SubjectSchema>;

export const UnitSchema = z.enum([
  "shape", // 図形・面積・立体（Phase 1.0 で先行）
  "fraction", // 分数・割合（Phase 1.0）
  "quantity", // 量・グラフ（Phase 1.3）
  "negative", // マイナス概念（Phase 1.4）
  "wordproblem", // 文章題（Phase 1.5）
]);
export type Unit = z.infer<typeof UnitSchema>;

export const DifficultySchema = z.enum(["star1", "star2", "star3"]);
export type Difficulty = z.infer<typeof DifficultySchema>;

export const PhaseSchema = z.enum(["1.0", "1.1", "1.2", "1.3", "1.4", "1.5"]);
export type Phase = z.infer<typeof PhaseSchema>;

/** 判定結果の 3 段階。これ以外は禁止（DONT.md A 節）。 */
export const ReactionKindSchema = z.enum([
  "delight", // 🌟 ケロぴ大喜び（概念表現 OK）
  "encourage", // 💭 寄り添い・ヒント
  "redirect", // 🌱 別角度誘導
]);
export type ReactionKind = z.infer<typeof ReactionKindSchema>;

// ============================================================
// 問題（依頼）
// ============================================================

export const ProblemSchema = z.object({
  /** 一意 ID（例: "Q001"） */
  id: z.string().regex(/^Q\d{3,}$/),
  /** 教科。Phase 1 では math のみ */
  subject: SubjectSchema,
  /** 単元 */
  unit: UnitSchema,
  /** 依頼者名（例: "ケロぴ", "カメ吉", "ホタル"） */
  requesterName: z.string().min(1),
  /** 依頼者キャラ ID（任意、figurine 表示に使用） */
  requesterCharId: z.string().optional(),
  /** 依頼セリフ。「問題」「学習」NG（DONT.md C 節） */
  requestUtterance: z.string().min(1).max(120),
  /** 期待する概念（Gemini 判定プロンプトに渡す） */
  expectedConcept: z.string().min(1).max(200),
  /** ヒント（寄り添い時に表示） */
  hint: z.string().max(120),
  /** 難易度 */
  difficulty: DifficultySchema,
  /** 有効フラグ。false にすると一時無効化 */
  enabled: z.boolean().default(true),
  /** どの Phase 以降で出題可能か */
  availableFromPhase: PhaseSchema,
});
export type Problem = z.infer<typeof ProblemSchema>;

// ============================================================
// 妹さんの絵（Drawing）
// ============================================================

export const DrawingSchema = z.object({
  id: z.string().uuid(),
  /** どの問題に対する絵か */
  problemId: z.string(),
  /** 描画データ（PNG dataURL or SVG path） */
  imageData: z.string(),
  /** 描画開始時刻 */
  startedAt: z.date(),
  /** 描画完了時刻（「できた！」を押した時刻） */
  completedAt: z.date(),
  /** Undo 回数（学習行動分析用、SPEC.md UX 制約参考） */
  undoCount: z.number().int().min(0).default(0),
});
export type Drawing = z.infer<typeof DrawingSchema>;

// ============================================================
// 判定結果（Judgement）
// ============================================================

export const JudgementSchema = z.object({
  id: z.string().uuid(),
  drawingId: z.string().uuid(),
  /** 3 段階のいずれか */
  reactionKind: ReactionKindSchema,
  /** ケロぴ / 住人のリアクションセリフ */
  reactionUtterance: z.string().min(1).max(120),
  /** 寄り添い / 別角度時のヒント文 */
  followupHint: z.string().max(120).optional(),
  /** Gemini API レスポンス（生データ、デバッグ用） */
  rawResponse: z.string().optional(),
  /** 判定にかかった実時間 (ms) */
  latencyMs: z.number().int().min(0),
  /** API 失敗時のフォールバック判定か */
  isFallback: z.boolean().default(false),
  judgedAt: z.date(),
});
export type Judgement = z.infer<typeof JudgementSchema>;

// ============================================================
// キャラクター（ケロぴ + 住人）
// ============================================================

export const CharacterSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  /** 種族（カエル / カメ / ホタル など） */
  species: z.string(),
  /**
   * 妹さんが描いた本キャラかどうか。
   * Phase 1.0 では false（仮素材）、Phase 1.1 でケロぴが true になる。
   */
  isUserDrawn: z.boolean().default(false),
  /** キャラ画像（仮素材 or 妹さん描画 dataURL） */
  imageData: z.string(),
  /** 図鑑追加日時 */
  addedToDexAt: z.date().optional(),
});
export type Character = z.infer<typeof CharacterSchema>;

// ============================================================
// 図鑑（Dex）
// ============================================================

export const DexSchema = z.object({
  characters: z.array(CharacterSchema),
});
export type Dex = z.infer<typeof DexSchema>;

// ============================================================
// 絵巻（Scroll）— 妹さんの全作品コレクション
// ============================================================

export const ScrollEntrySchema = z.object({
  drawing: DrawingSchema,
  judgement: JudgementSchema,
  problem: ProblemSchema,
});
export type ScrollEntry = z.infer<typeof ScrollEntrySchema>;

export const ScrollSchema = z.object({
  /** 全エントリは保存される（reaction kind に関係なく）。SPEC.md F7 */
  entries: z.array(ScrollEntrySchema),
});
export type Scroll = z.infer<typeof ScrollSchema>;

// ============================================================
// セッション
// ============================================================

export const SessionSchema = z.object({
  id: z.string().uuid(),
  startedAt: z.date(),
  endedAt: z.date().optional(),
  /** このセッションで完了した依頼 ID リスト */
  completedProblemIds: z.array(z.string()),
});
export type Session = z.infer<typeof SessionSchema>;

// ============================================================
// 設定
// ============================================================

export const SettingsSchema = z.object({
  inputMode: z.enum(["stylus", "finger"]).default("stylus"),
  soundEnabled: z.boolean().default(true),
  fontScale: z.enum(["small", "medium", "large"]).default("medium"),
  furiganaEnabled: z.boolean().default(true),
});
export type Settings = z.infer<typeof SettingsSchema>;
