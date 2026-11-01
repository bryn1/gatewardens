const { chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core');
(async () => {
  const b = await chromium.launch({ headless: true, executablePath: process.env.PW_CHROME });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await ctx.newPage();
  const logs = []; page.on('console', m => { const t = m.text(); if (t.startsWith('BSEED') || m.type()==='error') logs.push(t.slice(0,90)); });
  await page.goto('http://127.0.0.1:8158/index.html', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(16000);
  await page.screenshot({ path: 'shots/b1-hub.png' });
  // Blacksmith button approx (174,68) from hub frame; ship-route click with pacing
  await page.mouse.click(174, 68); await page.waitForTimeout(900);
  await page.screenshot({ path: 'shots/b2-blacksmith.png' });
  console.log(JSON.stringify({ logs }));
  await b.close();
})();
