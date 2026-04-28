/**
 * spec/state-machine.ts — L0-4 状態遷移（完全モード）
 *
 * XState v5 風の宣言で、ケロぴの森全体の状態遷移を定義する。
 * 実装時は実際の XState v5 actor として src/state/ に配置する想定。
 * 図解は state-diagrams.md 参照。
 */

import { setup } from "xstate";

// ============================================================
// イベント定義
// ============================================================

type AppEvent =
  | { type: "OPENING_DONE"; userDrawnKeropi?: string }
  | { type: "OPENING_SKIP" }
  | { type: "REQUEST_PICKED"; problemId: string }
  | { type: "REQUEST_DECLINED" }
  | { type: "DRAWING_DONE"; imageData: string }
  | { type: "DRAWING_CANCEL" }
  | { type: "JUDGEMENT_RECEIVED"; reactionKind: "delight" | "encourage" | "redirect" }
  | { type: "JUDGEMENT_FALLBACK" }
  | { type: "REACTION_DISMISSED" }
  | { type: "GO_DEX" }
  | { type: "GO_SCROLL" }
  | { type: "GO_HOME" }
  | { type: "GO_SETTINGS" }
  | { type: "QUIT_SESSION" };

// ============================================================
// トップレベル状態機械
// ============================================================

export const appMachine = setup({
  types: {} as {
    events: AppEvent;
    context: {
      sessionId: string | null;
      currentProblemId: string | null;
      currentDrawingData: string | null;
    };
  },
}).createMachine({
  id: "keropi-no-mori",
  initial: "boot",
  context: {
    sessionId: null,
    currentProblemId: null,
    currentDrawingData: null,
  },
  states: {
    /** 起動時、初回判定 */
    boot: {
      always: [
        { target: "opening", guard: "isFirstLaunch" },
        { target: "home" },
      ],
    },

    /** F1: オープニング（Phase 1.1 で本格化、1.0 は仮素材スキップ可） */
    opening: {
      on: {
        OPENING_DONE: { target: "home", actions: "saveUserKeropi" },
        OPENING_SKIP: { target: "home" },
      },
    },

    /** F2: 森ホーム（中央拠点） */
    home: {
      on: {
        REQUEST_PICKED: {
          target: "drawing",
          actions: "setCurrentProblem",
        },
        GO_DEX: { target: "dex" },
        GO_SCROLL: { target: "scroll" },
        GO_SETTINGS: { target: "settings" },
        QUIT_SESSION: { target: "boot" },
      },
    },

    /** F4: 描画キャンバス */
    drawing: {
      on: {
        DRAWING_DONE: {
          target: "judging",
          actions: "saveDrawingData",
        },
        DRAWING_CANCEL: { target: "home" },
      },
    },

    /**
     * F5 + F6: 判定中。
     * 重要: 必ず F6（待ち時間体験）が並行して走る。
     * direct で reaction にジャンプしない。
     */
    judging: {
      type: "parallel",
      states: {
        api: {
          initial: "calling",
          states: {
            calling: {
              on: {
                JUDGEMENT_RECEIVED: { target: "received" },
                JUDGEMENT_FALLBACK: { target: "received" },
              },
              after: {
                10000: { target: "received", actions: "markFallback" },
              },
            },
            received: { type: "final" },
          },
        },
        waitingExperience: {
          initial: "active",
          states: {
            active: {
              // ミニゲーム or 解説アニメ。判定完了で必ず中断可能
              on: {
                JUDGEMENT_RECEIVED: { target: "interrupting" },
                JUDGEMENT_FALLBACK: { target: "interrupting" },
              },
            },
            interrupting: { type: "final" },
          },
        },
      },
      onDone: "reaction",
    },

    /** F7: リアクション（3 段階） */
    reaction: {
      on: {
        REACTION_DISMISSED: {
          target: "home",
          actions: ["addToScroll", "maybeAddToDex"],
        },
      },
    },

    /** 図鑑 */
    dex: {
      on: { GO_HOME: { target: "home" } },
    },

    /** 絵巻 */
    scroll: {
      on: { GO_HOME: { target: "home" } },
    },

    /** 設定 */
    settings: {
      on: { GO_HOME: { target: "home" } },
    },
  },
});

// ============================================================
// 描画キャンバス サブステート（drawing 内部）
// ============================================================

type DrawingEvent =
  | { type: "STROKE_START" }
  | { type: "STROKE_END" }
  | { type: "UNDO" }
  | { type: "REDO" }
  | { type: "ERASE" }
  | { type: "CLEAR_ALL" }
  | { type: "FINISH" }
  | { type: "CANCEL" };

export const drawingMachine = setup({
  types: {} as { events: DrawingEvent },
}).createMachine({
  id: "drawing-canvas",
  initial: "idle",
  states: {
    idle: {
      on: {
        STROKE_START: { target: "stroking" },
        UNDO: { target: "idle", actions: "undoLastStroke" },
        REDO: { target: "idle", actions: "redoStroke" },
        ERASE: { target: "erasing" },
        CLEAR_ALL: { target: "confirming_clear" },
        FINISH: { target: "finishing" },
        CANCEL: { target: "cancelled", type: "final" },
      },
    },
    stroking: {
      on: { STROKE_END: { target: "idle", actions: "commitStroke" } },
    },
    erasing: {
      on: {
        STROKE_END: { target: "idle" },
        // erase tool は通常の stroke と別ロジック
      },
    },
    confirming_clear: {
      // 全消し前に「ほんとに消す？」の優しい確認（強制ではない）
      on: {
        CLEAR_ALL: { target: "idle", actions: "clearAll" },
        CANCEL: { target: "idle" },
      },
    },
    finishing: { type: "final" },
    cancelled: { type: "final" },
  },
});
