#!/usr/bin/env node
// check_layout.js — 判断キット v2 の HTML を PC 幅（1440）とスマホ幅（390）× 明 / 暗で開き、
// 全ページ（項目・解説 / 選ぶ・まとめ）を「次へ」で順にめくって ①横はみ出し ②スクリーンショット を取る。
// console の error も数える（1 件でも exit 1）。
//
// 使い方: NODE_PATH=$(npm root -g) node check_layout.js <kit.html> [outdir]
// 出力: <outdir>/shot-<幅>-<明暗>-p<ページ>.png。はみ出しか console error があれば exit 1。
// playwright が無ければ playwright-core + 手元の Chrome（CHROME_PATH）で動かす
let chromium; try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('playwright-core')); }
const path = require('path');

(async () => {
  const file = process.argv[2];
  const out = process.argv[3] || path.dirname(path.resolve(file));
  if (!file) { console.error('usage: node check_layout.js <kit.html> [outdir]'); process.exit(2); }
  const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
  let bad = 0;
  for (const [width, scheme] of [[1440, 'light'], [390, 'light'], [390, 'dark']]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
    page.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) { bad++; console.log(`  console error (${width}/${scheme}): ${m.text()}`); } });
    page.on('pageerror', (e) => { bad++; console.log(`  pageerror (${width}/${scheme}): ${e.message}`); });
    await page.goto('file://' + path.resolve(file));
    for (let k = 0; k < 200; k++) {
      if (k > 0) await page.click('#next');
      const r = await page.evaluate(() => {
        const W = document.documentElement.clientWidth; const over = [];
        document.querySelectorAll('body *').forEach((e) => {
          // 横スクロール容器（項目の並び・表）の中身は意図的なはみ出し
          if (e.closest('#map, .tbl, pre, .zoom')) return;
          const b = e.getBoundingClientRect();
          if (b.width && b.right > W + 1) over.push(`${e.tagName.toLowerCase()}.${e.className} right=${Math.round(b.right)}`);
        });
        return { W, sw: document.documentElement.scrollWidth, over: over.slice(0, 10) };
      });
      const ok = r.sw <= r.W && r.over.length === 0;
      if (!ok) bad++;
      const sum = await page.$('.page.sum');
      console.log(`${width}px/${scheme} p${k + 1}${sum ? '（まとめ）' : ''}: ${ok ? 'OK' : 'はみ出し'} (scrollWidth=${r.sw})${r.over.length ? '\n  ' + r.over.join('\n  ') : ''}`);
      await page.screenshot({ path: path.join(out, `shot-${width}-${scheme}-p${k + 1}.png`), fullPage: true });
      if (sum) break;
    }
    await page.close();
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
