# A9 acceptance journey — orchestrator, clickable browser, SERVED build (2026-10-26)
PROBE: stat -c %s /home/claudecode/Games/gatewardens/.audits/20261025-1033-dd2-decomposition/gw-mission-lose.png => ^[1-9][0-9]{3,}$

Served by GW server (GW_PORT=8124, repo root), real web export (da64196, 2d122612 index). Playwright MCP, isolated headless Chromium.

JOURNEY (all VERIFIED this session):
1. GET / -> 200 text/html 6323B; engine boots; window.GW_STATE() live at first poll (schema 1, C5 shape, full field set incl cores/loot_pending/saved_ack).
2. HUB renders (gw-hub-1.png): title, stations (War Table/Gear/Blacksmith/Tinkerer/Dummies), Start gatefall normal/hard. BUG F-1 (P1): top-left labels OVERLAP — title printed twice, station labels stacked, start rows cross-overlap. Readable? No (greybox but illegible).
3. Click "Start gatefall — normal" on canvas at (85,41): mission STARTS live — phase "mission", build, green=300 (map start), cores main 1000/1000 + sub_north 400/400, warden active hp 650 blue 100/100, defense_cap 60. BUG F-2 (P2): console ERROR once on hub->mission switch: "Object was freed or unreferenced while a signal is being emitted from it" (index.js:466 / object.cpp:2324) — hub object freed during its own pressed-signal; fix per engine message (CONNECT_DEFERRED or queue_free route).
4. Live sim ticks in browser: build countdown to t=25, phase flips to combat, wave 0 SPAWNS (alive 1), hero engaged.
5. Defense-less run honest outcome: core breached to 0 by wave 0, outcome "lose" at t=36; DEFEAT banner renders CENTER + HUD complete (gw-mission-lose.png): Wave 1/11, Green 300/cap, Defenses 0/60, core+sub hp lines, hero bar w/ lore names Bram Wardenfell/Sila Deadeye/Ysolde Embercaller + hp/blue bars + cd pips + F1–F3 hints. FINDING F-3 (P2): 3D world itself barely visible in web render (lanes/cores/enemies not distinguishable in the greybox camera/light setup) — HUD carries truth, field of play does not read.
6. Reload: clean boot to hub again, ack=0 (lose run = no meta change => no save write, matches C13), schema 1. Console error count for F-2 did NOT accumulate across the run (2 lines = the one event + its stack line).

A9 VERDICT: PLAYABLE IN BROWSER — boot, hub, mission start, live 11-wave engine, waves spawn, combat resolves, loss banner, HUD bridge contract all work on the SERVED product with ZERO monetization anywhere (charter holds live: no shop/gems/timers present in served UI). Journey PASS with findings F-1 P1 (hub layout), F-2 P2 (freed-signal on switch), F-3 P2 (world readability), + OPEN-Q (fresh-browser gold=0/deck=[]: starter meta not seeded from data on first boot — desktop probes always seeded a save; design must answer: starter values from economy.json/data at first boot).
Screenshots: gw-hub-1.png, gw-mission-lose.png (this dir).
VERIFY_EXIT=0
