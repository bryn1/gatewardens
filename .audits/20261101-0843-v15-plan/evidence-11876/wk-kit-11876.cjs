// W-K served leg (MC 11876): loopback-served build, shipped clicks
// START -> place Ballista -> select uid row -> relic row -> Assign
// relic, with the seed save injected through a DISCLOSED harness-side
// route wrapper (wraps Engine.prototype.startGame to write the save
// file into the engine's own IDB user:// store before boot; product
// bytes unchanged). PASS=2 stops at the selected panel (measure);
// PASS=3 + RELIC_Y + ASSIGN_Y runs the full click + burst leg.
const { chromium } = require('/home/claudecode/opt/deepseek-harness/node_modules/.pnpm/playwright-core@1.63.0-alpha-2026-08-31/node_modules/playwright-core');
const SHOTS = '.tmp/shots';
const PORT = '54803';
const CHROME = '/home/claudecode/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const PASS = process.env.PASS || '3';
const RELIC_Y = parseInt(process.env.RELIC_Y || '0', 10);
const ASSIGN_Y = parseInt(process.env.ASSIGN_Y || '0', 10);

const SEED_BLOCK = `\nfunction __wkSeed() {\n  return fetch('/seed.bin').then(function (r) { return r.arrayBuffer(); })\n    .then(function (arr) {\n      return new Promise(function (res, rej) {\n        const rq = indexedDB.open('/userfs', 21);\n        rq.onupgradeneeded = function (e) {\n          const db2 = e.target.result;\n          const tx = e.target.transaction;\n          let st;\n          if (db2.objectStoreNames.contains('FILE_DATA')) st = tx.objectStore('FILE_DATA');\n          else st = db2.createObjectStore('FILE_DATA');\n          if (!st.indexNames.contains('timestamp'))\n            st.createIndex('timestamp', 'timestamp', { unique: false });\n        };\n        rq.onsuccess = function () {\n          const db = rq.result;\n          const tx = db.transaction('FILE_DATA', 'readwrite');\n          for (const d of ['/userfs/godot', '/userfs/godot/app_userdata', '/userfs/godot/app_userdata/Gatewardens']) {\n            tx.objectStore('FILE_DATA').put({ timestamp: new Date(1762000000000), mode: 16877 }, d);\n          }\n          tx.objectStore('FILE_DATA').put(\n            { timestamp: new Date(1762000000000), mode: 33188, contents: new Uint8Array(arr) },\n            '/userfs/godot/app_userdata/Gatewardens/gatewardens.cfg');\n          tx.oncomplete = function () { db.close(); console.log('WKSEED put ok'); res(); };\n          tx.onerror = function () { db.close(); rej(tx.error); };\n        };\n        rq.onerror = function () { rej(rq.error); };\n      });\n    });\n}\nconsole.log('WKSEED chained');\nconst _wksg = engine.startGame.bind(engine);\nengine.startGame = function (o) {\n  return __wkSeed().then(function () {\n    console.log('WKSEED starting'); return _wksg(o);\n  }, function (e) { console.log('WKSEED seedfail ' + e); return _wksg(o); });\n};\n`;

(async () => {
  const b = await chromium.launch({ headless: true, executablePath: CHROME,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const errs = [];
  page.on('pageerror', e => errs.push('PAGEERROR ' + String(e).slice(0, 140)));
  page.on('console', m => {
    const t = m.text();
    if (t.startsWith('SCRATCH11876') || t.startsWith('WKSEED')
        || t.includes('IndexedDB')) console.log('CONSOLE ' + t);
    if (m.type() === 'error') errs.push(t.slice(0, 140));
  });
  await page.route('**/index.html', async route => {
    console.log('ROUTE-HIT ' + route.request().url());
    const res = await route.fetch();
    let html = await res.text();
    const marker = '<script src="index.js"></script>';
    if (!html.includes(marker)) { console.log('INJECT-MARKER-MISS'); }
    const shellLine = 'const engine = new Engine(GODOT_CONFIG);';
    if (!html.includes(shellLine)) console.log('SHELL-MARKER-MISS');
    html = html.replace(shellLine, shellLine + '\n' + SEED_BLOCK);
    const h = { ...res.headers(), 'Cache-Control': 'no-store' };
    delete h['content-length']; delete h['Content-Length'];
    await route.fulfill({ status: res.status(), headers: h, body: html });
  });
  await page.goto(`http://127.0.0.1:${PORT}/index.html`,
                  { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(14000);
  const bank = await page.evaluate(() => (window.__gwSnapshot || {}).bank_count);
  console.log('BANK ' + bank);
  if (bank !== 2) { console.log('SEED-READBACK-FAIL'); console.log('ERRS ' + JSON.stringify(errs)); await b.close(); process.exit(1); }
  await page.screenshot({ path: `${SHOTS}/k0-hub-seeded.png` });
  await page.mouse.click(105, 165);              // START (gatefall hard, icon-leg route)
  await page.waitForTimeout(10000);
  await page.mouse.click(1048, 55);              // Ballista arm
  await page.waitForTimeout(700);
  await page.mouse.click(640, 380);              // place at ghost
  await page.waitForTimeout(700);
  await page.mouse.click(1024, 390);             // uid row = SELECT
  await page.waitForTimeout(900);
  await page.screenshot({ path: `${SHOTS}/k1-selected.png` });
  if (PASS === '2') { await b.close(); console.log('PASS2-OK'); return; }

  // --- PASS 3: control frame, relic row, pre-click panel, ASSIGN, burst
  await page.screenshot({ path: `${SHOTS}/k2-control.png` });
  await page.screenshot({ path: `${SHOTS}/k2c-control-clip.png`,
    clip: { x: 240, y: 230, width: 210, height: 230 } });
  await page.mouse.click(1024, RELIC_Y);         // relic row = select kit
  await page.waitForTimeout(600);
  await page.screenshot({ path: `${SHOTS}/k3-relic-selected.png` });
  await page.mouse.click(1024, ASSIGN_Y);        // Assign relic -> crossing -> spark
  const burst = [];
  for (let i = 0; i < 48; i++) {
    const f = `${SHOTS}/kb-${String(i).padStart(2, '0')}.png`;
    await page.screenshot({ path: f, clip: { x: 240, y: 230, width: 210, height: 230 } });
    burst.push(f);
  }
  console.log('SNAP-ASSIGN ' + await page.evaluate(() => JSON.stringify({
    relics_assigned: (window.__gwSnapshot || {}).relics_assigned,
    bank_count: (window.__gwSnapshot || {}).bank_count,
    phase_kind: (window.__gwSnapshot || {}).phase_kind })));
  await page.screenshot({ path: `${SHOTS}/k4-after.png` });
  await page.screenshot({ path: `${SHOTS}/k4-panel.png`,
    clip: { x: 908, y: 330, width: 240, height: 330 } });
  console.log('ERRS ' + JSON.stringify(errs));
  await b.close();
})();
