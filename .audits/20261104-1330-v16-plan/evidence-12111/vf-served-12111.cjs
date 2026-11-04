// V-F served leg (MC 12111): fresh web export (pck md5 logged beside
// this file), loopback-served on GW_PORT, shipped START route only
// (hub click (105,165) — the icon-leg-11854 route, >=600ms pacing —
// one deliberate click, one wait), state marker read FIRST (snapshot
// phase_kind + the HUD build-phase line), then the P6 census frames:
// the full build frame + the declared DECOR region crop (340,40,560,
// 120 — the north rim band the DC-SCREEN probe leg pins its canopy
// tops inside). Frame-time sampler: 6 s of rAF deltas in the build
// phase (a ROW, not a claim — the known ~7 fps floor is the web build
// class, decor adds zero per-frame code).
const { chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core');
const SHOTS = process.env.SHOTS || '.';
const PORT = process.env.PORT || '51211';
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
  await page.screenshot({ path: `${SHOTS}/vf-0-hub.png` });
  await page.mouse.click(105, 165);              // START (shipped route)
  await page.waitForTimeout(10000);              // mission, build phase
  const snap = await page.evaluate(() => (window.__gwSnapshot || {}));
  console.log('SNAP phase_kind=' + snap.phase_kind + ' wave=' + snap.wave
    + ' core=' + (snap.cores && snap.cores.main ? snap.cores.main.hp : '?'));
  await page.screenshot({ path: `${SHOTS}/vf-1-build.png` });
  await page.screenshot({ path: `${SHOTS}/vf-2-decor.png`,
    clip: { x: 340, y: 40, width: 560, height: 120 } });
  // Frame-time row: rAF deltas over 6 s, build phase, after shots.
  const ft = await page.evaluate(() => new Promise(res => {
    const ds = []; let last = performance.now(); const t0 = last;
    const tick = (t) => { ds.push(t - last); last = t;
      if (t - t0 < 6000) requestAnimationFrame(tick); else res(ds); };
    requestAnimationFrame(tick);
  }));
  const s = ft.slice().sort((a, c) => a - c);
  console.log('FRAMETIME n=' + ft.length + ' median_ms=' + s[Math.floor(s.length / 2)].toFixed(1)
    + ' p95_ms=' + s[Math.floor(s.length * 0.95)].toFixed(1)
    + ' max_ms=' + s[s.length - 1].toFixed(1));
  console.log('ERRS ' + JSON.stringify(errs));
  await b.close();
})();
