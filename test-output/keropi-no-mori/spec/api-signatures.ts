/**
 * spec/api-signatures.ts — L0-3 API 契約（簡易モード）
 *
 * 自前 API は設計しない（PWA 単体構成）。外部 API（Google Sheets / Gemini）
 * の利用 signature のみを記述する。実装は src/services/ に配置する想定。
 */

import type { Problem, Judgement, ReactionKind, Drawing } from "./domain";

// ============================================================
// Google Sheets 連携
// ============================================================

/**
 * 問題プールを Google Sheets から取得する。
 *
 * 実装オプション:
 *  (a) Sheets を「ウェブに公開」 → CSV エクスポート URL を fetch
 *  (b) Google Visualization API (`gviz/tq?tqx=out:json`)
 *  (c) Google Sheets API v4（API キー不要の公開シート向け）
 *
 * 推奨: (b) — 認証不要、JSON 直取得、公開 URL で動作。
 *
 * 失敗時の挙動:
 *  - 最終取得分のキャッシュ（IndexedDB）を返す
 *  - キャッシュも無ければバンドル同梱の問題セット（Phase 1.0 用）を返す
 */
export interface FetchProblemsFromSheets {
  (sheetId: string, options?: { sheetName?: string }): Promise<{
    problems: Problem[];
    fetchedAt: Date;
    source: "remote" | "cache" | "bundle";
  }>;
}

/**
 * 取得した行データを Problem 型にパース・バリデーション。
 * Zod スキーマで検証し、不正な行はスキップしてログ。
 */
export interface ParseProblemRows {
  (rows: unknown[][]): { valid: Problem[]; invalid: { row: unknown[]; reason: string }[] };
}

// ============================================================
// Gemini API 連携（マルチモーダル絵判定）
// ============================================================

/**
 * 妹さんの描いた絵を Gemini に送り、判定結果を 3 段階のいずれかに正規化して返す。
 *
 * 重要制約（DONT.md A 節）:
 *  - 出力は ReactionKind の 3 段階のみ
 *  - 「不正解」「失敗」「間違い」を出力させないプロンプト設計
 *  - 失敗時は isFallback=true で「ケロぴ考え中」演出
 *
 * プロンプトテンプレートは assets/judgment-prompt.md に切り出し（チューニング可）。
 */
export interface JudgeDrawingViaGemini {
  (input: {
    drawing: Drawing;
    problem: Problem;
    apiKey: string;
    timeoutMs?: number; // 既定 10 秒
  }): Promise<Judgement>;
}

/**
 * Gemini レスポンスを 3 段階に正規化する純粋関数。
 * 不明なレスポンスは "encourage"（寄り添い）にフォールバック。
 */
export interface NormalizeReaction {
  (rawResponse: string): {
    reactionKind: ReactionKind;
    reactionUtterance: string;
    followupHint?: string;
  };
}

// ============================================================
// IndexedDB 永続化（ローカル）
// ============================================================

/** 妹さんの絵 / 図鑑 / 絵巻 / 設定の保存・取得 */
export interface LocalStore {
  saveDrawing(drawing: Drawing): Promise<void>;
  loadScroll(): Promise<import("./domain").Scroll>;
  loadDex(): Promise<import("./domain").Dex>;
  saveDexEntry(character: import("./domain").Character): Promise<void>;
  loadSettings(): Promise<import("./domain").Settings>;
  saveSettings(settings: import("./domain").Settings): Promise<void>;
}

// ============================================================
// 待ち時間ミニゲーム / 解説アニメ供給
// ============================================================

/**
 * 判定中（API 待ち時間）に表示する体験を返す。
 * SPEC.md F6 準拠。判定完了で必ず中断可能であること。
 */
export interface WaitingExperienceProvider {
  pickRandom(unit: import("./domain").Unit): Promise<{
    kind: "minigame" | "explanation";
    componentName: string;
    durationHintMs?: number;
  }>;
}
