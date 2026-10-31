const { chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core');
(async () => {
  const b = await chromium.launch({ headless: true, executablePath: process.env.PW_CHROME });
  const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const errs = []; page.on('console', m => m.type() === 'error' && errs.push(m.text().slice(0,120)));
  await page.goto('http://127.0.0.1:8154/index.html', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(14000);
  await page.mouse.click(105, 165);              // START
  await page.waitForTimeout(9000);               // mission, build phase
  await page.screenshot({ path: 'shots/i0-build-neutral.png' });
  await page.mouse.click(1048, 55); await page.mouse.click(500, 300);   // Ballista #1 (shipped arm->place)
  await page.waitForTimeout(800);
  await page.mouse.click(1048, 55); await page.mouse.click(640, 380);   // Ballista #2
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'shots/i1-lowgreen.png' });            // green ~100 < Hailspire 140
  await page.waitForTimeout(26000);              // wave starts -> phase != build
  await page.screenshot({ path: 'shots/i2-combat.png' });
  console.log(JSON.stringify({ errs }));
  await b.close();
})();
