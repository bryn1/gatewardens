// one-off served leg: ring armed/selected screenshots (throwaway; not product)
const path = require('path');
const dshDir = process.env.DSH_DIR || '/home/claudecode/opt/deepseek-harness';
let chromium;
try { ({ chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core')); }
catch { ({ chromium } = require('playwright-core')); }
(async () => {
  const b = await chromium.launch({ headless: true, executablePath: process.env.PW_CHROME });
  const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const errs = []; page.on('console', m => m.type() === 'error' && errs.push(m.text().slice(0, 120)));
  await page.goto('http://127.0.0.1:8153/index.html', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(14000);
  await page.mouse.click(105, 165);            // START
  await page.waitForTimeout(10000);            // mission build phase
  await page.screenshot({ path: 'shots/00-mission.png' });
  await page.mouse.click(1048, 55);            // Ballista row = arm
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'shots/01-armed.png' });
  await page.mouse.click(640, 380);            // click a slot: place
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'shots/02-placed.png' });
  await page.mouse.click(640, 380);            // click the tower: select
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'shots/03-selected.png' });
  console.log(JSON.stringify({ errs }));
  await b.close();
})();
