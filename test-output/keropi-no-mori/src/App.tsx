/**
 * ケロぴの森 — 最小骨格コンポーネント。
 *
 * Phase 1.0 MVP の placeholder。L1 (autonomous-dev) がここから state-machine.ts
 * (`spec/state-machine.ts`) に接続して各画面 (F1〜F9) を実装する。
 *
 * 仮素材: ◯目玉カエル（妹さんが Phase 1.1 で本キャラを描く）
 */

export function App() {
  return (
    <main className="app">
      <header className="hero">
        <div className="keropi-stub" aria-hidden="true">
          <span className="keropi-eye" />
          <span className="keropi-eye" />
        </div>
        <h1 className="title">ケロぴの森</h1>
        <p className="subtitle">そのうち、はじまるよ</p>
      </header>
    </main>
  );
}
