// one-off served leg MC 11852: SR11852 console capture + select/deselect
// frames (throwaway; not product). Port via $PW_PORT (default 8177).
const dshDir = process.env.DSH_DIR || '/home/claudecode/opt/deepseek-harness';
let chromium;
try { ({ chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core')); }
catch { ({ chromium } = require('playwright-core')); }
const SHOTS = process.env.PW_SHOTS || 'shots';
const PORT = process.env.PW_PORT || '8177';
(async () => {
  const b = await chromium.launch({ headless: true, executablePath: process.env.PW_CHROME });
  const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const lines = [];
  page.on('console', m => lines.push(m.type() + '|' + m.text()));
  await page.goto(`http://127.0.0.1:${PORT}/index.html`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(14000);
  await page.mouse.click(105, 165);            // START
  await page.waitForTimeout(10000);            // mission build phase
  await page.screenshot({ path: `${SHOTS}/00-mission.png` });
  await page.mouse.click(1048, 55);            // Ballista row = arm
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${SHOTS}/01-armed.png` });
  await page.mouse.click(640, 380);            // LMB confirm = place at ghost
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${SHOTS}/02-placed.png` });
  await page.mouse.click(1024, 390);           // uid row = SELECT (panel)
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${SHOTS}/03-selected.png` });
  await page.mouse.click(1048, 55);            // arm again -> priority ARMED
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${SHOTS}/04-rearm.png` });
  await page.waitForTimeout(1000);
  await page.keyboard.press('Escape');         // cancel arm -> back to SELECTED
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${SHOTS}/05-fallback.png` });
  await page.mouse.click(1024, 325);           // Sell = deselect teardown
                                               // (shipped selected_uid=0
                                               //  reset, P5 declared read)
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${SHOTS}/06-teardown.png` });
  console.log(lines.join('\n'));
  await b.close();
})();
