const PW = '/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core';
const { chromium } = require(PW);
const PORT = require('fs').readFileSync('.tmp/wk-serve.port', 'utf8').match(/PORT=(\d+)/)[1];
(async () => {
  const b = await chromium.launch({ executablePath: '/home/claudecode/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args: ['--no-sandbox'] });
  const pg = await b.newPage({ viewport: { width: 1280, height: 800 } });
  pg.on('console', m => { const x = m.text(); if (/WKSEED|SCRATCH|IndexedDB/.test(x)) console.log('CONSOLE', x.slice(0, 160)); });
  await pg.goto(`http://127.0.0.1:${PORT}/index.html`);
  await pg.waitForTimeout(15000);
  await pg.screenshot({ path: '.tmp/shots/wc-0-hub.png' });
  await pg.mouse.click(105, 165); await pg.waitForTimeout(3000);
  // place ballista
  await pg.mouse.click(1048, 55); await pg.waitForTimeout(800);
  await pg.mouse.click(640, 380); await pg.waitForTimeout(1500);
  // wait into combat (wave ~16-26s of build clock)
  await pg.waitForTimeout(26000);
  const t0 = Date.now();
  for (let i = 0; i < 12; i++) {
    await pg.screenshot({ path: `.tmp/shots/wc-${String(i).padStart(2, '0')}.png`, clip: { x: 240, y: 230, width: 460, height: 260 } });
    await pg.waitForTimeout(700);
  }
  console.log('SHOTS', Math.round((Date.now() - t0) / 1000) + 's');
  const snap = await pg.evaluate(() => window.__gwSnapshot ? JSON.stringify(window.__gwSnapshot()) : 'none');
  console.log('SNAP', snap);
  await b.close();
})();
