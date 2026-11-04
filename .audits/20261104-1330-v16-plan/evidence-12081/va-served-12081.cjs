// V-A served leg (MC 12081): fresh web export (pck md5 logged beside
// this file), loopback-served on GW_PORT, shipped START route only
// (hub click (105,165) — the icon-leg-11854 route), >=600ms input
// pacing, state marker read FIRST (snapshot phase + canvas marker by
// the describe-image pass), then the P1 census screenshots at the
// declared 1280x720 poses. No seeded save needed: the build-phase
// frame is the shipped default boot.
const { chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core');
const SHOTS = process.env.SHOTS || '.';
const PORT = process.env.PORT || '51208';
const CHROME = '/home/claudecode/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';

(async () => {
  const b = await chromium.launch({ headless: true, executablePath: CHROME,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const errs = [];
  page.on('pageerror', e => errs.push('PAGEERROR ' + String(e).slice(0, 140)));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 140)); });
  await page.goto(`http://127.0.0.1:${PORT}/index.html`,
                  { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(14000);
  await page.screenshot({ path: `${SHOTS}/va-0-hub.png` });
  await page.mouse.click(105, 165);              // START (shipped route)
  await page.waitForTimeout(10000);              // mission, build phase
  const snap = await page.evaluate(() => (window.__gwSnapshot || {}));
  console.log('SNAP phase_kind=' + snap.phase_kind + ' wave=' + snap.wave
    + ' core=' + (snap.cores && snap.cores.main ? snap.cores.main.hp : '?'));
  await page.screenshot({ path: `${SHOTS}/va-1-build.png` });
  // Crops at the probe's DG-SCREEN coords (keep 640,331; spawn_a
  // 326,331; spawn_b 640,179) + the declared TOP-STRIP band.
  await page.screenshot({ path: `${SHOTS}/va-2-core.png`,
    clip: { x: 540, y: 246, width: 200, height: 174 } });
  await page.screenshot({ path: `${SHOTS}/va-3-gate-a.png`,
    clip: { x: 260, y: 266, width: 132, height: 130 } });
  await page.screenshot({ path: `${SHOTS}/va-4-topstrip.png`,
    clip: { x: 250, y: 40, width: 630, height: 110 } });
  console.log('ERRS ' + JSON.stringify(errs));
  await b.close();
})();
