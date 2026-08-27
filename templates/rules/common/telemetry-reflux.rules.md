# Telemetry Reflux RL（テレメトリ逆流の宣言枠・利用者プロジェクト用）

> ROLE: プロダクトが自らの逆流源（エラー監視・analytics・計算可能 UX 代理指標）と閾値を
> **宣言**するための枠。宣言された信号は「観測データ → Issue 候補」の逆流路に載る。
> SCOPE: DH 展開プロジェクト（D1-D3）。DH 本体はこの枠だけを持ち、実定義は各プロダクトが行う。
> SEVERITY: 本ファイルは宣言テンプレートであり、未宣言はエラーではない（逆流路が無いだけ）。
> ORIGIN: dialog-harness v6.15.0 F4（G3・W3）。世界水準調査
> `delivery/ANALYSIS-agentic-sdlc-world-standard-2026-08-28.md` §W3 —
> 「仕事の自動発見はテレメトリ逆流が主戦場。人間起票はトリガーの一種にすぎない」。

---

## 不変条件（宣言より優先）

- **TR-1 起票は候補のみ**。逆流路が生む Issue は `signal-detected` 相当のラベルを持ち、
  実装パイプラインへの昇格（`ready-for-ai`）は**人間が判断**する
  （philosophy 第 8 条「観測 → 候補化 → 人間最終承認」。世界水準 W8 と同型）
- **TR-2 検知は決定論**。閾値比較・存在判定のみで構成し、LLM 判定を検知器に入れない
  （DH 第 2 条。fixability score 型の数値化は将来拡張であり、その場合もスコアの
  算出根拠が決定論で追跡可能であること）
- **TR-3 閾値は目標値ではない**。逆流の量を KPI 化しない（Goodhart 回避・v6.15.0 I-4）
- **TR-4 常時発火する検知は形骸化する**。検知器は絞って始め、実測 1 ヶ月で見直す
  （`dh-manifest.yml` upstream 節に記録された kakuman 実地知見）

## 宣言フォーマット

プロダクトはリポジトリに `telemetry-reflux.yml`（または REGIME.md 内ブロック）で宣言する:

```yaml
reflux_sources:
  - id: sentry-new-errors            # 一意 id
    kind: error-monitoring           # error-monitoring | analytics | ux-proxy | ci
    source: "Sentry（接続済み MCP / API）"
    condition: "新規 issue が production で発生し、event 数が閾値超"
    threshold: { events: 10, window: "24h" }
    output: "Issue 候補（title: '[signal:sentry] <issue title>'）"
    owner: human                     # 昇格判断の主体（常に human・TR-1）
  - id: ux-error-rate
    kind: ux-proxy
    source: "計算可能 UX 代理指標（philosophy 第 4 条: エラー率・完了率・レイテンシ）"
    condition: "エラー率が baseline の 2 倍超（7 日移動平均）"
    threshold: { ratio: 2.0, window: "7d" }
    output: "Issue 候補"
    owner: human
```

## signal-scan との接続（F4-2）

宣言された逆流源は、DH の `scripts/signal-scan.py` の**検知器 (e) 以降として追加可能な形式**
（`detector` / `target` / `title` / `body` の 4 フィールドを返す）で実装する。
title は `[signal:<id>] <対象>` に揃える（重複起票防止の dedup キーになる）。

## DH への還流

本枠で得た知見（誤検知パターン・有効だった閾値・事故を経た教訓）は
`dh-manifest.yml` upstream の U-5 に従い、**事故の日付と解いた問題を添えて**還流する。
機構そのものを先に還流しない（事故を経ていない規範の自己増殖を防ぐ）。
