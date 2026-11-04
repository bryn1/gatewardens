// V-B served census (MC 12082): loopback-served fresh build, shipped
// clicks START -> arm Ballista (panel row) -> place at ghost -> STATE
// MARKER (__gwSnapshot.defenses==1) -> silhouette frames -> uid-row
// select -> relic row -> ASSIGN (kit spark re-census, WK2 window reused)
// -> combat wait -> two-frame turret crop delta.
//
// Seed route = the DECLARED WK2 harness-side wrapper (wraps
// Engine.prototype.startGame to write the save into the engine's own
// IDB user:// store before boot; product bytes unchanged) — upgraded:
// the seed bytes ride INLINE base64 (server allowlist carries no .bin,
// so NOTHING extra is served; VB-wave.log row).
// PASS=2 stops after the uid-row select (measure relic/assign rows).
// PASS=3 needs RELIC_Y ASSIGN_Y + optional TOWER_CLIP=x,y,w,h.
const { chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core');
const SHOTS = process.env.SHOTS || '.audits/20261104-1330-v16-plan/shots';
const PORT = process.env.PORT || '54877';
const CHROME = '/home/claudecode/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const PASS = process.env.PASS || '2';
const RELIC_Y = parseInt(process.env.RELIC_Y || '0', 10);
const ASSIGN_Y = parseInt(process.env.ASSIGN_Y || '0', 10);
const UNASSIGN_Y = parseInt(process.env.UNASSIGN_Y || '0', 10);
const TC = (process.env.TOWER_CLIP || '560,280,170,140').split(',').map(Number);
const PLACE = (process.env.PLACE || '640,380').split(',').map(Number);
const UID_ROW = parseInt(process.env.UID_ROW || '428', 10);
const EXPECT = parseInt(process.env.EXPECT || '3', 10);
const SEED_B64 = process.env.SEED_B64;

const SEED_BLOCK = `
function __vbSeed() {
  const bin = atob('${SEED_B64}');
  const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  return new Promise(function (res, rej) {
    const rq = indexedDB.open('/userfs', 21);
    rq.onupgradeneeded = function (e) {
      const db2 = e.target.result;
      const tx = e.target.transaction;
      let st;
      if (db2.objectStoreNames.contains('FILE_DATA')) st = tx.objectStore('FILE_DATA');
      else st = db2.createObjectStore('FILE_DATA');
      if (!st.indexNames.contains('timestamp'))
        st.createIndex('timestamp', 'timestamp', { unique: false });
    };
    rq.onsuccess = function () {
      const db = rq.result;
      const tx = db.transaction('FILE_DATA', 'readwrite');
      for (const d of ['/userfs', '/userfs/godot', '/userfs/godot/app_userdata', '/userfs/godot/app_userdata/Gatewardens']) {
        tx.objectStore('FILE_DATA').put({ timestamp: new Date(1762000000000), mode: 16877 }, d);
      }
      tx.objectStore('FILE_DATA').put(
        { timestamp: new Date(1762000000000), mode: 33188, contents: arr },
        '/userfs/godot/app_userdata/Gatewardens/gatewardens.cfg');
      tx.oncomplete = function () { db.close(); console.log('VBSEED put ok'); res(); };
      tx.onerror = function () { db.close(); rej(tx.error); };
    };
    rq.onerror = function () { rej(rq.error); };
  });
}
console.log('VBSEED chained');
const _vbSG = engine.startGame.bind(engine);
engine.startGame = function (o) {
  return __vbSeed().then(function () {
    console.log('VBSEED starting'); return _vbSG(o);
  }, function (e) { console.log('VBSEED seedfail ' + e); return _vbSG(o); });
};
`;

(async () => {
  const b = await chromium.launch({ headless: true, executablePath: CHROME,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const errs = [];
  page.on('pageerror', e => errs.push('PAGEERROR ' + String(e).slice(0, 140)));
  page.on('console', m => {
    const t = m.text();
    if (t.startsWith('VBSEED')) console.log('CONSOLE ' + t);
    if (m.type() === 'error') errs.push(t.slice(0, 140));
  });
  await page.route('**/index.html', async route => {
    const res = await route.fetch();
    let html = await res.text();
    const shellLine = 'const engine = new Engine(GODOT_CONFIG);';
    if (!html.includes(shellLine)) { console.log('SHELL-MARKER-MISS'); }
    html = html.replace(shellLine, shellLine + '\n' + SEED_BLOCK);
    const h = { ...res.headers(), 'Cache-Control': 'no-store' };
    delete h['content-length']; delete h['Content-Length'];
    await route.fulfill({ status: res.status(), headers: h, body: html });
  });
  await page.goto(`http://127.0.0.1:${PORT}/index.html`,
                  { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(15000);
  const hub = await page.evaluate(() => JSON.stringify({
    bank_count: (window.__gwSnapshot || {}).bank_count,
    phase: (window.__gwSnapshot || {}).phase }));
  console.log('HUB ' + hub);
  if (!hub.includes('"bank_count":' + EXPECT)) {
    console.log('SEED-READBACK-FAIL'); console.log('ERRS ' + JSON.stringify(errs));
    await b.close(); process.exit(1);
  }
  await page.screenshot({ path: `${SHOTS}/vb-hub-seeded.png` });

  // ---- shipped clicks, 600ms+ pacing ----
  await page.mouse.click(105, 165);               // START gatefall
  await page.waitForTimeout(parseInt(process.env.BOOT_MS || '10000', 10));
  console.log('PRE-BUILD ' + await page.evaluate(() => JSON.stringify({
    phase: (window.__gwSnapshot || {}).phase,
    phase_kind: (window.__gwSnapshot || {}).phase_kind,
    defenses: (window.__gwSnapshot || {}).defenses })));
  await page.screenshot({ path: `${SHOTS}/vb-empty-full.png` });
  await page.screenshot({ path: `${SHOTS}/vb-empty-towerclip.png`,
    clip: { x: TC[0], y: TC[1], width: TC[2], height: TC[3] } });

  await page.mouse.click(1048, 98);               // Gate Blockade row = arm
  await page.waitForTimeout(800);
  await page.mouse.click(PLACE[0], PLACE[1]);     // blockade takes slot 1
  await page.waitForTimeout(900);
  if (process.env.PLACE3) {                       // hailspire -> slot 3 (clear)
    await page.mouse.click(1048, 221);            // Hailspire row = arm
    await page.waitForTimeout(800);
    await page.mouse.click(PLACE[0], PLACE[1]);
    await page.waitForTimeout(900);
  }
  await page.mouse.click(1048, 55);               // Ballista panel row = arm
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${SHOTS}/vb-armed-full.png` });
  await page.mouse.click(PLACE[0], PLACE[1]);     // ballista -> next free slot
  await page.waitForTimeout(1000);
  // STATE MARKER FIRST: the snapshot + panel line before any pixel claim.
  console.log('MARKER ' + await page.evaluate(() => JSON.stringify({
    defenses: (window.__gwSnapshot || {}).defenses,
    green: (window.__gwSnapshot || {}).green,
    phase_kind: (window.__gwSnapshot || {}).phase_kind })));
  await page.screenshot({ path: `${SHOTS}/vb-placed-full.png` });
  await page.screenshot({ path: `${SHOTS}/vb-placed-towerclip.png`,
    clip: { x: TC[0], y: TC[1], width: TC[2], height: TC[3] } });
  await page.screenshot({ path: `${SHOTS}/vb-placed-panel.png`,
    clip: { x: 908, y: 40, width: 240, height: 620 } });

  if (PASS === '2') {
    await page.mouse.click(1024, UID_ROW);          // uid row = SELECT
    await page.waitForTimeout(900);
    await page.screenshot({ path: `${SHOTS}/vb-selected-panel.png`,
      clip: { x: 908, y: 40, width: 240, height: 620 } });
    console.log('ERRS ' + JSON.stringify(errs));
    await b.close(); console.log('PASS2-OK'); return;
  }

  // ---- PASS 3: select, relic, assign (spark re-census), combat ----
  await page.mouse.click(1024, UID_ROW);          // uid row = SELECT
  await page.waitForTimeout(700);
  await page.screenshot({ path: `${SHOTS}/vb-sel-control-full.png` });
  await page.screenshot({ path: `${SHOTS}/vb-sel-control-towerclip.png`,
    clip: { x: TC[0], y: TC[1], width: TC[2], height: TC[3] } });
  await page.waitForTimeout(450);
  await page.screenshot({ path: `${SHOTS}/vb-sel-control2-towerclip.png`,
    clip: { x: TC[0], y: TC[1], width: TC[2], height: TC[3] } });
  await page.mouse.click(1024, RELIC_Y);          // relic row = kit select
  await page.waitForTimeout(700);
  await page.mouse.click(1024, ASSIGN_Y);         // ASSIGN -> crossing spark
  await page.waitForTimeout(700);
  await page.mouse.click(1024, UNASSIGN_Y);       // unassign (shipped btn)
  await page.waitForTimeout(700);
  await page.mouse.click(1024, ASSIGN_Y);         // assign -> crossing
  // WK2 pacing: burst starts the SAME tick as the assign (spark life is
  // sub-second; the 700ms settle of the first pass waited it out —
  // VB-wave.log lesson). Snap AFTER the burst (assignment state persists).
  const burst = [];
  for (let i = 0; i < 24; i++) {
    const f = `${SHOTS}/vb-kb-${String(i).padStart(2, '0')}.png`;
    await page.screenshot({ path: f, clip: { x: TC[0], y: TC[1], width: TC[2], height: TC[3] } });
    burst.push(f);
    if (i === 2) await page.screenshot({ path: `${SHOTS}/vb-kb-full-a.png` });
    if (i === 6) await page.screenshot({ path: `${SHOTS}/vb-kb-full-b.png` });
  }
  console.log('BURST ' + burst.length + ' frames');
  console.log('SNAP-ASSIGN ' + await page.evaluate(() => JSON.stringify({
    relics_assigned: (window.__gwSnapshot || {}).relics_assigned,
    bank_count: (window.__gwSnapshot || {}).bank_count,
    phase_kind: (window.__gwSnapshot || {}).phase_kind })));

  // combat: poll the snapshot (build_seconds_default 20s, wave 1 lands)
  let combat = 0;
  for (let w = 0; w < 40; w++) {
    const s = await page.evaluate(() => JSON.stringify({
      phase_kind: (window.__gwSnapshot || {}).phase_kind,
      alive: (window.__gwSnapshot || {}).alive,
      wave: (window.__gwSnapshot || {}).wave }));
    if (s.includes('"phase_kind":"combat"') && !s.includes('"alive":0')) {
      console.log('COMBAT ' + s); combat = 1; break;
    }
    await page.waitForTimeout(1500);
  }
  if (!combat) { console.log('NO-COMBAT-WINDOW'); }
  await page.screenshot({ path: `${SHOTS}/vb-combat-a.png` });
  for (let p2 = 0; p2 < 6; p2++) {
    await page.screenshot({ path: `${SHOTS}/vb-combat-a${p2}-turretclip.png`,
      clip: { x: TC[0], y: TC[1], width: TC[2], height: TC[3] } });
    await page.waitForTimeout(900);
    await page.screenshot({ path: `${SHOTS}/vb-combat-b${p2}-turretclip.png`,
      clip: { x: TC[0], y: TC[1], width: TC[2], height: TC[3] } });
  }
  await page.screenshot({ path: `${SHOTS}/vb-combat-b.png` });
  await page.screenshot({ path: `${SHOTS}/vb-after-full.png` });
  console.log('ERRS ' + JSON.stringify(errs));
  await b.close();
  console.log('CENSUS-OK');
})();
