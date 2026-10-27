# DOC-SWEEP — pre-GA truth surfaces vs measured reality
MC 11274.1.24 / card 11340 — hygiene child — 2026-10-26. Base: main HEAD 817f8d2 (== origin/main, 0 ahead).
Exceeds 150 lines BY DESIGN: the DoD mandates per-surface fix-text (quoting stale lines + replacement blocks) — the reason is stated here, near the top, per file hygiene.

MEASURED THIS SESSION (not assumed): `python3 -m pytest tests/ -q` → **190 passed, exit 0** (21.26s); `tools/check_hygiene.py` gate rides the suite (0 hits); README serve command ran VERBATIM: `/`→200 text/html 6323B, `/index.wasm`→application/wasm, unknown/escape→404 {"error":"NOT_FOUND"} (GW_PORT=8139, killed after); export wrapper NOT run (heavy — its TEXT verified line-by-line vs export_presets.cfg + the pinned binary at /home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64 (exists, 146MB): preset "Web", thread_support=false, custom_html_shell=res://web_shell.html, head_include="", export_path=../static/index.html — all match README + wrapper). Product files: ZERO edits (git status below).

## ACCEPTANCE TABLE (A1–A10 × evidence level × one-line why)

| row | level | why (one line) |
|---|---|---|
| A1 combat | TESTED | hero kill/blue/cooldown/swap smoke legs + golden run (headless); browser move/jump never exercised served |
| A2 heroes | TESTED | test_heroes (3 heroes, 4 abilities, cap 50, 3 asc trees), deck swap in smoke/golden |
| A3 defenses | TESTED (wording fix) | all formulas/cap/classes proven (W8 legs + golden); BUT "place anywhere" is contradicted by shipped slot-derived placement (see S1-f) |
| A4 mission | TESTED | golden plays 11 waves normal incl boss WIN; hard file is data-schema-tested only — hard full-run UNVERIFIED |
| A5 loot | TESTED | loot-structure + drop/chest tests + W11 loot toast/smoke leg; scripts/loot_pickup.gd row never shipped (S2-b) |
| A6 gear+services | TESTED w/ gap | blacksmith/tinkerer/gear/dummies legs in hub_probe+test_hub; C11 relic assign/unassign methods DO NOT EXIST in shipped code (S2-c) |
| A7 persistence | TESTED (desktop) | save_probe fresh-process round-trip incl materials (I5); browser mutation→ack→reload leg never run (journey reload was ack=0/no-write) |
| A8 free-forever | VERIFIED | check_hygiene 0 hits + own greps this session + README row present (line 5) |
| A9 served journey | UNVERIFIED (row overstates) | served VERIFIED for boot/hub/mission-live/lose/reload + F-1/F-2/F-3/starter re-journey; the A9-NAMED legs (wave-10+boss IN BROWSER, place/upgrade in browser, loot pickup in browser, equip in browser, save mutation+ack+reload) exist ONLY headless-golden |
| A10 release doctrine | UNVERIFIED (pending, correct) | no tag yet; the doc-sync sweep it requires is this run + the orchestrator fix pass |

## PER-SURFACE VERDICTS

### S1 LEDGER.md — TRUE except two rows
All 16 DONE rows match `git log` (hash + pytest count verified for W1 8 / W2 67 / W3a 86 / W3b 116 / W4 122 / W5 127 / W6 131 / W7 135 / W8 139 / W9 155 / W10 167 / W11 172 / W11b 175 / W12 180 / W13 190 against the W*-close-evidence.md files; 190 re-measured green now).
(a) STALE/CONTRADICTED row — line 61–62:
    `| A9 journey | PASS w/ findings — evidence A9-journey.md + screenshots; ... |`
    `| BUILD W13 ... | DONE — ... A9 re-journey PASS (0 console errors, visible world, data starter live) ... |`
  The A9-journey.md journey covered boot/hub/mission-start/live-waves/lose/reload; W13 re-journey covered fresh-boot-starter/hub-legibility/2×switch/lose. Neither ran wave-10+boss-kill, place/upgrade, loot pickup, equip, or a save-mutation ack+reload in the browser. REPLACEMENT (row 61):
    `| A9 journey | PARTIAL — boot/hub/mission-live/lose/reload + F-1/F-2/F-3/starter fixes VERIFIED served (A9-journey.md, W13 evidence); wave-10+boss/place/upgrade/loot/equip/save+reload browser legs NOT yet run — golden proves them headless only. Full-browser journey leg REQUIRED before GA tag |`
(b) STALE header line 3–5 — no change needed (4.7.2 matches project.godot + conftest binary).
(c) cosmetic: W9 row cites MC 11274.1.16 printed after W8's .17 — leave.
(d) row "CLEAN-CODE AUDIT ... | spawning" — leave (in flight).
(f) A3 line 16 "place anywhere" — contradicted by the shipped model (defense_placer slots derived from lane waypoints, W8 declared). REPLACEMENT: "place on buildable slots derived from lane geometry (open placement, no pads; confirm falls to first free slot)".

### S2 docs/ARCHITECTURE.md — STALE in 6 places (living doc, edit IN PLACE; versioned-truth: this file IS the live version, git history is the archive)
(a) sim/ table + placement plan claim `sim/validate_probe.gd` + `GWTables.validate`: **neither exists**. Shipped instead: sim/sim_parse_probe.gd, sim/boot_probe.gd, sim/hub_probe.gd, sim/mission_smoke.gd (absent from the table); boot fail-fast is FILE-level parse in main.gd (W5 declared); deep validation is the pytest schema layer. FIX: replace the validate_probe row + the "(sim_headless, save_probe, validate_probe)" lists with:
    `| sim/sim_parse_probe.gd | parse-leg harness (W3a): imports the sim set, machine rows + EMPTY-stderr parse signal (W4 ruling) |`
    `| sim/boot_probe.gd | boots the REAL Main.tscn flow under -s, drives _ready (E5), asserts BOOT-PROBE-OK + EMPTY stderr (W5) |`
    `| sim/hub_probe.gd | drives hub.tscn through the real scene: 11 station/service/relic-refusal legs (W9) |`
    `| sim/mission_smoke.gd | mission funnel smoke: spawn/advance/breach/awards/swap/lose+commit legs, MISSION-SMOKE-OK (W6+) |`
  and drop the `static func validate` claim from the sim_tables.gd row (→ "validate() deferred; pytest schema layer + file-level boot check own F16").
(b) scripts/ table claims `scripts/loot_pickup.gd`: **file never shipped** (loot rows are mission step (6) + hud toast, W11). FIX: mark the row "SHIPPED AS mission.step_loot + hud loot toast (no own file, W11)".
(c) scripts/mission.gd row claims `place_defense/assign_relic/unassign_relic`: only place_defense exists (grep 0 hits for the relic pair; sim_headless says so itself, line 211). FIX: "place_defense ✓; assign_relic/unassign_relic NOT SHIPPED — relic assignment deferred with defense_panel picker (declared open W8, still open); C11 pool-copy + SimInventory.relic_bonuses + C5 relics_assigned DO ship".
(d) scripts/ row missing: `scripts/hero_pawn.gd` (shipped W7, pawn scene). FIX: add the row.
(e) Scenes line claims `enemy.tscn, defense.tscn, core.tscn, ghost.tscn, pawn_<archetype>.tscn ×3, dummy.tscn`; shipped = `hub.tscn mission.tscn mission_stub.tscn hud.tscn hero_pawn.tscn (ONE, archetype-tinted) item_row.tscn` — per-entity scenes intentionally never shipped (W6/W8 greybox "zero per-entity .tscn" idiom). FIX: replace the scenes line with the shipped list + "per-entity tscn deferred to the frontend/art wave (greybox primitives by declaration)".
(f) data/economy.json row: "NO start" — W13 ADDED `"starter":{"gold":100}` (economy.json on disk + test_data_schemas exact-key row; W13 commit itself left this doc-sync owed). FIX: append to the row: `+ starter:{gold:int} — W13 fresh-boot meta seed, data-only (declared reading: display, not tuning)`.
(g) minor: Modules/C5 wording says main.gd pushes via `_js_eval(...)`; shipped code calls `_js_bridge.call("eval", ...)` (main.gd:163) — wording nit, one-line fix optional.

### S3 README.md — one STALE line
(a) line 9: `Status: Phase 0 (mechanics research) in flight — see MC 11274.1.` — CONTRADICTED: build is through W13, 190 green, HEAD 817f8d2. REPLACEMENT:
    `Status: v1 build waves W1–W13 DONE (190 pytest green, main @ 817f8d2); pre-GA clean-code/doc sweep in flight (MC 11274.1.24). Not yet GA — see LEDGER.md for the acceptance list with evidence levels.`
(b) commands: serve VERBATIM-RUN green (above); export wrapper TEXT matches preset+binary+pinned path (VERIFIED by inspection, not executed — heavy, per task). GW_PORT default 8124: VERIFIED in server.py. TRUE.
(c) "no monetization ever" vs hygiene tripwire: CONSISTENT (tripwire tokens + 0 gate hits; README hit below is the charter negation itself). Charter rows TRUE (clean-room, owner ruling 2026-10-25 MC 11274.1 quoted in LEDGER + README line 5).

### S4 fleet registry PROJECTS.md (/home/claudecode/agent-town/orchestrator/PROJECTS.md) — NO ROW (grep gatewardens = 0 hits). NOT edited (repo not mine). Draft below.

### S5 RETIRED-CLAIM GREP RESULTS (scope: godot/ server/ static/ README, ARCHITECTURE exempt; built index.wasm/js/pck grepped binary-side too)
- monetization vocab: hits ONLY in (i) negative/structural prose — README.md:5 (charter "No shop. No loot boxes. No timers."), tools/check_hygiene.py:36-44 (the tripwire token list itself), tests/test_hud.py:218-224 + test_hub.py:371-376 (guards), test_data_schemas.py:595-598 + test_loot_structure.py:161 (gate liveness); (ii) .gd COMMENTS with the word "price" — mission_smoke.gd:48,167,254, defense_obj.gd:162, test_hub.py:170,222 (comments are blanked before the tripwire per BN1 — no gate hit; prose nit only). Binary artifacts: 0 hits. → no product-surface monetization vocabulary.
- VS product names: 0 RAW hits (VS_STATE/__vsSnapshot/vsHost) incl. binaries; prose lineage mentions remain (web_shell.html:95, bridge.gd:20,49, server/static_app.py:3, test_scaffold.py:25-26) — allowed, I8 bans the three bridge names.
- 'autoload' outside the project.godot comment: all hits are negative claims/structural (gw_compose.gd:5, game_state.gd:8, hub.gd:46, item_row.gd:40, LEDGER.md:67, check_hygiene.py:195-196, test_scaffold.py) — no [autoload] section anywhere. PASS.
- 4-attribute stats residue (STR/DEX/INT/END/strength/...): ZERO hits in data/scripts/sim/server/static/README/tests/tools. PASS.
- 'loot box' style positive claims: only README.md:5 negation; raw/ scrape JSONs under .audits are research inputs, exempt. PASS.

### S6 stale code comments (grep function-names-in-comments vs definitions; 17 raw hits triaged, 2 real)
- STALE: sim/sim_tables.gd:9 "# validate() lands with validate_probe (W5), not here." and :27 "detecting that is validate()'s job (W5)." — W5 shipped WITHOUT validate/validate_probe; the promised future never landed. FIX: "(deep validate deferred — pytest schema layer + main.gd file-level boot check own F16; see ARCHITECTURE sim-table fix)".
- STALE-adjacent: main.gd:67-71 comment "the deep validator is the validate_probe row's static (reading recorded on the trail)" — names a nonexistent row's static; reword to "the pytest schema layer (test_data_schemas) is the deep validator".
- OK (accurate historical/declared, leave): main.gd:36 (read_input paraphrase), defense_placer.gd:9, lane_path.gd:3, mission.gd:21 (next_event does not exist — TRUE, grep-confirmed), sim_headless.gd:211, gear_panel_ui (GameState.equip exists, game_state.gd:114), picked(uid) signal exists (item_row.gd:26). Engine builtins (is_empty/get_parent/has_feature/rng.randf) false positives.

## PROJECTS.ROW DRAFT (for the orchestrator to apply to /home/claudecode/agent-town/orchestrator/PROJECTS.md)
| gatewardens | Gatewardens — clean-room DD2-style action TD, Godot 4.7.2 web export, permanently free (repo bryn1/gatewardens, checkout ~/Games/gatewardens) | **PRE-GA, W1–W13 DONE on main @ 817f8d2** (190 pytest green VERIFIED 2026-10-26; served contract live-verified; A9 full-browser journey legs + A10 release rows OPEN — see LEDGER acceptance table); doc-sweep findings routed MC 11274.1.24 | `LEDGER.md` + `.audits/20261025-1033-dd2-decomposition/` + `.audits/20261025-1046-doc-sweep/DOC-SWEEP.md` |
NEXT ACTION (row's next-action column if their table has one): full-browser A9 journey (boss kill + place/upgrade + loot + equip + save mutation→ack→reload), then clean-code refactor, then A10 release rows + tag.

## DoD SELF-CHECK
git -C /home/claudecode/Games/gatewardens status --porcelain → `?? .audits/` only (re-checked after this file's write; .tmp/ + __pycache__ gitignored). No product file edited. VERIFY_EXIT=0
