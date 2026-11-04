// V-H served leg (MC 12114): fresh web export (pck md5 + byte size logged
// BEFORE each run — L2 stale-pck clause kb e4aa7e1f), loopback
// server/server.py on GW_PORT, shipped START route only (hub click
// (105,165), the icon-leg-11854/va-served/vc-served route), >=600ms input
// pacing (waits 14s/10s hold it), STATE MARKER first (phase_kind snapshot
// + the describe-marker crop). CROPS LOCKED HERE BEFORE any AFTER frame
// existed: HERO (460,210,360x360) = the VD hero crop widened 300->360 so
// the re-tuned figure (stands ~4u further camera-side, projects ~40px
// lower) cannot leave it; MARK-CTRL (0,0,520x116) = the coach/marker strip
// non-vacuity control (the wave countdown differs run to run). Env:
// PORT, SHOTS, PREFIX. No seeded save — shipped default boot.
const { chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core');
const SHOTS = process.env.SHOTS || '.';
const PREFIX = process.env.PREFIX || 'vh';
const PORT = process.env.PORT || '51231';
const CHROME = '/home/claudecode/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const HERO = { x: 460, y: 210, width: 360, height: 360 };
const MARK = { x: 0, y: 0, width: 520, height: 116 };

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
  await page.screenshot({ path: `${SHOTS}/${PREFIX}-0-hub.png` });
  await page.mouse.click(105, 165);              // START (shipped route)
  await page.waitForTimeout(10000);              // mission, build phase
  const snap = await page.evaluate(() => (window.__gwSnapshot || {}));
  console.log('SNAP phase_kind=' + snap.phase_kind + ' wave=' + snap.wave
    + ' core=' + (snap.cores && snap.cores.main ? snap.cores.main.hp : '?'));
  await page.screenshot({ path: `${SHOTS}/${PREFIX}-1-build.png` });
  await page.screenshot({ path: `${SHOTS}/${PREFIX}-2-marker.png`, clip: MARK });
  await page.screenshot({ path: `${SHOTS}/${PREFIX}-3-hero.png`, clip: HERO });
  console.log('ERRS ' + JSON.stringify(errs));
  await b.close();
})();
