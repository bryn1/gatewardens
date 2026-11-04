// V-C served leg (MC 12110): fresh web export (pck md5 + byte size
// logged BEFORE the run — L2 stale-pck clause kb e4aa7e1f), loopback
// server/server.py on GW_PORT, shipped START route only (hub click
// (105,165), the icon-leg-11854/va-served route), >=600ms input pacing
// (waits 14s/10s hold it), STATE MARKER first (phase_kind snapshot +
// the describe-marker crop), then the P3 census screenshots: the full
// build-phase frame + the three declared PATH-REGION crops (same rects
// measured on the BEFORE control frames — PATH-A centre lane
// 620,225,115x100; PATH-B left corridor 365,360,225x55; PATH-C lower
// right 865,520,140x75). The build-phase frame is the shipped default
// boot — no seeded save.
const { chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core');
const SHOTS = process.env.SHOTS || '.';
const PORT = process.env.PORT || '51223';
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
  await page.screenshot({ path: `${SHOTS}/vc-0-hub.png` });
  await page.mouse.click(105, 165);              // START (shipped route)
  await page.waitForTimeout(10000);              // mission, build phase
  const snap = await page.evaluate(() => (window.__gwSnapshot || {}));
  console.log('SNAP phase_kind=' + snap.phase_kind + ' wave=' + snap.wave
    + ' core=' + (snap.cores && snap.cores.main ? snap.cores.main.hp : '?'));
  await page.screenshot({ path: `${SHOTS}/vc-1-build.png` });
  await page.screenshot({ path: `${SHOTS}/vc-2-marker.png`,
    clip: { x: 0, y: 0, width: 520, height: 116 } });
  await page.screenshot({ path: `${SHOTS}/vc-3-path-a.png`,
    clip: { x: 620, y: 225, width: 115, height: 100 } });
  await page.screenshot({ path: `${SHOTS}/vc-4-path-b.png`,
    clip: { x: 365, y: 360, width: 225, height: 55 } });
  await page.screenshot({ path: `${SHOTS}/vc-5-path-c.png`,
    clip: { x: 865, y: 520, width: 140, height: 75 } });
  console.log('ERRS ' + JSON.stringify(errs));
  await b.close();
})();
