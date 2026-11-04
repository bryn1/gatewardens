// V-G reproducible two-pose capture (MC 12115, plan W3 V-G). ONE script runs
// BOTH sides of the pair (AFTER = merged v1.6 tip, BEFORE-rig = fresh v1.5
// 1271a6c re-export in the scratch worktree): same code, same rig, same
// 1280x720 viewport, ZERO wheel events (L4 — the camera never moves from its
// shipped default, so "the exact same pose" IS "the same route").
// Route (V16-BEFORE.md): hub click (90,132) = WAR TABLE "Start gatefall —
// normal" (the VE-wave-verified coord; the BEFORE frames carry the NORMAL
// difficulty — v16-before-defeat.png prints "Core 0/1000", the normal core
// max; the (105,165) HARD route the W1/W2 cards used is NOT the pair route).
//   pose 1 = build phase, countdown visible ("Build: wave 1 in N s")
//   pose 2 = wave 1 undefended — zero placements, wait for outcome=lose,
//            the shipped DEFEAT screen ("DEFEAT / Core 0/1000 / RETURN TO HUB")
// Law rows honored: L2 state MARKER first (snapshot + marker crop printed
// before the pose shot), >=600ms input pacing (ONE deliberate click, long
// waits), STALE-PCK clause kb e4aa7e1f — a fresh chromium is an empty cache,
// and the pck md5+size is fetched and logged BESIDE every captured frame
// (PCK0 route / PCK1 build / PCK2 defeat); the caller logs the on-disk export
// md5 and asserts served==export. L6: no product file is touched by this run.
// Env: SHOTS (out dir), PORT (served loopback), TAG (frame name prefix).
const fs = require('fs');
const http = require('http');
const crypto = require('crypto');
const { chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core');
const SHOTS = process.env.SHOTS || '.';
const PORT = process.env.PORT || '51241';
const TAG = process.env.TAG || 'v16-after';
const CHROME = '/home/claudecode/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const DEFEAT_CAP_MS = 600000;

function pckLine(label) {
  return new Promise((res, rej) => {
    http.get({ host: '127.0.0.1', port: PORT, path: '/index.pck',
               headers: { 'Cache-Control': 'no-cache' } }, (r) => {
      const h = crypto.createHash('md5'); let n = 0;
      r.on('data', (d) => { h.update(d); n += d.length; });
      r.on('end', () => res(`PCK ${label} md5=${h.digest('hex')} bytes=${n}`));
    }).on('error', rej);
  });
}

async function frameTime(page, label) {
  // Same sampler as vf-served-12111.cjs: 6 s of rAF deltas (a ROW, not a
  // claim — the ~7 fps class is the swiftshader web floor, plan §18).
  const ds = await page.evaluate(() => new Promise((res) => {
    const a = []; let last = performance.now(); const t0 = last;
    const tick = (t) => { a.push(t - last); last = t;
      if (t - t0 < 6000) requestAnimationFrame(tick); else res(a); };
    requestAnimationFrame(tick);
  }));
  const s = ds.slice().sort((a, c) => a - c);
  console.log(`FRAMETIME pose=${label} n=${ds.length}`
    + ` median_ms=${s[Math.floor(s.length / 2)].toFixed(1)}`
    + ` p95_ms=${s[Math.floor(s.length * 0.95)].toFixed(1)}`
    + ` max_ms=${s[s.length - 1].toFixed(1)}`);
}

const snapOf = (p) => p.evaluate(() => {
  const s = window.__gwSnapshot || {};
  return { phase: s.phase, phase_kind: s.phase_kind, difficulty: s.difficulty,
           wave: s.wave, green: s.green, outcome: s.outcome,
           alive: s.alive, wave_remaining: s.wave_remaining,
           core_hp: s.cores && s.cores.main ? s.cores.main.hp : null,
           core_max: s.cores && s.cores.main ? s.cores.main.max : null };
});

(async () => {
  const b = await chromium.launch({ headless: true, executablePath: CHROME,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const errs = [];
  page.on('pageerror', (e) => errs.push('PAGEERROR ' + String(e).slice(0, 140)));
  page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text().slice(0, 140)); });
  await page.goto(`http://127.0.0.1:${PORT}/index.html`,
                  { waitUntil: 'domcontentloaded', timeout: 60000 });
  console.log(await pckLine('0-route'));
  await page.waitForTimeout(14000);
  await page.mouse.click(90, 132);          // "Start gatefall — normal" (VE coord)
  await page.waitForTimeout(10000);         // mission, build phase (one deliberate click)
  let snap = await snapOf(page);
  console.log('SNAP-BUILD ' + JSON.stringify(snap));
  if (snap.phase !== 'mission' || snap.phase_kind !== 'build'
      || snap.difficulty !== 'normal' || snap.core_max !== 1000) {
    console.log('FAIL pose1 is not the normal-difficulty build phase'); process.exit(2);
  }
  await page.screenshot({ path: `${SHOTS}/${TAG}-build-marker.png`,
                          clip: { x: 0, y: 0, width: 520, height: 116 } });  // MARKER FIRST
  await page.screenshot({ path: `${SHOTS}/${TAG}-build.png` });              // POSE 1
  console.log(await pckLine('1-build'));
  await frameTime(page, 'build');
  // Pose 2: zero placements; watch the shipped sim reach the defeat crossing.
  const t0 = Date.now(); let poll = 0;
  for (;;) {
    await page.waitForTimeout(3000);
    snap = await snapOf(page);
    if (++poll % 10 === 0) {
      console.log(`WATCH t=${Math.round((Date.now() - t0) / 1000)}s ` + JSON.stringify(snap));
    }
    if (snap.outcome === 'lose') break;
    if (snap.outcome === 'win') { console.log('FAIL sim declared WIN undefended'); process.exit(2); }
    if (Date.now() - t0 > DEFEAT_CAP_MS) { console.log('FAIL defeat cap exceeded'); process.exit(2); }
  }
  console.log(`SNAP-DEFEAT after ${Math.round((Date.now() - t0) / 1000)}s ` + JSON.stringify(snap));
  await page.waitForTimeout(1500);          // end-screen paint settles (>=600ms pacing)
  await page.screenshot({ path: `${SHOTS}/${TAG}-defeat-marker.png`,
                          clip: { x: 0, y: 0, width: 520, height: 116 } });
  await page.screenshot({ path: `${SHOTS}/${TAG}-defeat.png` });             // POSE 2
  console.log(await pckLine('2-defeat'));
  await frameTime(page, 'defeat');
  console.log('ERRS ' + JSON.stringify(errs));
  await b.close();
})().catch((e) => { console.log('FAIL ' + String(e).slice(0, 200)); process.exit(2); });
