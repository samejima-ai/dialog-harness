#!/usr/bin/env node
// check_layout.js — 判断キット HTML を PC 幅（1100・明）と mobile 幅（375・明 / 暗）で開き、
// ①ページ全体の横はみ出し ②スクリーンショット を 1 回で取る。
// chromium CLI の --window-size は最小幅の制約で 375 を再現できないため Playwright を使う。
// console の error も数える（1 件でも exit 1）。
//
// 使い方: NODE_PATH=$(npm root -g) node check_layout.js <kit.html(--standalone で build したもの)> [outdir]
// 出力: <outdir>/shot-1100-light.png, shot-375-light.png, shot-375-dark.png, shot-375-q1.png。はみ出しか console error があれば exit 1。
// playwright が無ければ playwright-core + 手元の Chrome（CHROME_PATH）で動かす
let chromium; try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('playwright-core')); }
const path = require('path');

(async () => {
  const file = process.argv[2];
  const out = process.argv[3] || path.dirname(path.resolve(file));
  if (!file) { console.error('usage: node check_layout.js <kit.html> [outdir]'); process.exit(2); }
  const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
  let bad = 0;
  for (const [width, scheme] of [[1100, 'light'], [375, 'light'], [375, 'dark']]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
    page.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) { bad++; console.log(`  console error (${width}/${scheme}): ${m.text()}`); } });
    page.on('pageerror', (e) => { bad++; console.log(`  pageerror (${width}/${scheme}): ${e.message}`); });
    await page.goto('file://' + path.resolve(file));
    const r = await page.evaluate(() => {
      const W = document.documentElement.clientWidth; const over = [];
      document.querySelectorAll('body *').forEach((e) => {
        // 横スクロール容器の中身は意図的なはみ出し
        if (e.closest('.flowh, .flow-wrap, .tl, .tbl-wrap, pre, .lb, .copy-ta')) return;
        const b = e.getBoundingClientRect();
        if (b.width && b.right > W + 1) over.push(`${e.tagName.toLowerCase()}.${e.className} right=${Math.round(b.right)}`);
      });
      return { W, sw: document.documentElement.scrollWidth, over: over.slice(0, 10) };
    });
    const ok = r.sw <= r.W && r.over.length === 0;
    if (!ok) bad++;
    console.log(`${width}px/${scheme}: ${ok ? 'OK' : 'はみ出し'} (scrollWidth=${r.sw})${r.over.length ? '\n  ' + r.over.join('\n  ') : ''}`);
    await page.screenshot({ path: path.join(out, `shot-${width}-${scheme}.png`), fullPage: true });
    if (width === 375 && scheme === 'light') {
      const q1 = await page.$('.q');
      if (q1) await q1.screenshot({ path: path.join(out, 'shot-375-q1.png') });
    }
    await page.close();
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
