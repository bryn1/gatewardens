SUPERSEDED 2026-11-01 (MC 11871 DA gate r1, FIX round): DO NOT USE — live version: V15-PLAN-c2.md (same dir)

# V15-PLAN — v1.5 "make-it-sing" scope: dispose the v1.4 backlog, pick the heart (MC 11871 · plan seat · 2026-11-01)

Base: HEAD `65da857` = v1.4 RELEASE (verified `git log -1`). READ-ONLY over the repo except this
dir. Length reason (file hygiene): one plan, one subject — the disposition table, its waves and
its matrix are one contract (V14-PLAN precedent); kept whole at ~300 ln.
Every number below was re-measured THIS session at 65da857 (instruments in V15-PLAN.log); the
brief's input list was verified row-by-row, never trusted. Path correction carried from V14-PLAN
§0: DD-REFERENCE.md resolves OUTSIDE the repo at
`/home/claudecode/Games/.audits/202610281826-9924ad48/out/DD-REFERENCE.md` (R2 clean-room wall),
NOT at `docs/DD-REFERENCE.md` as the brief wrote it.

## 1 GOAL + TESTABLE ACCEPTANCE — what the player FEELS different in v1.5

v1.4 shipped the kit FEATURE with zero presentation (the P7 probe FINDING, pinned in
tests/test_kit_fx.py): assigning a kit to a defense is an invisible state crossing, and every
loot/item row renders the same gray because `rarity.json` never got a `colors` key while the
`item_row.gd` tint mechanism already ships waiting for it (its header:18-21 declares exactly
this). v1.5 "make-it-sing" = the two state crossings the player makes most — "I equipped a kit"
and "I picked up loot" — become VISIBLE through EXISTING mechanisms only (fx_director read-only
observer; rarity-data → shipped item_row tint), plus the honest test-debt closure the v1.4
mutation pass routed forward (F-2/F-3/F-3a/F-4) and the v5_fx_probe baseline re-declaration
declared NOT RUN at v1.4.

Testable acceptance for the milestone (release-tail leg, orchestrator-driven):
- A1 SERVED: in the loopback-served game, placing a Ballista and assigning a kit through shipped
  clicks paints a visible fx burst at the tower (state's own panel marker verified in-frame FIRST,
  then pixel census vs an empty control frame + describe-image read; kb 1acdc1c3 discipline).
- A2 SERVED: bank/inventory item rows render per-rarity COLORS and the mission loot toast tints
  by rarity — vision reads distinct quality colors; every color arrives from rarity.json (zero
  new literals in I2-governed files).
- A3 TESTED: full suite green AT the final tree ≥ the projection of §5; `check_hygiene` 0 hits;
  `tests/fixtures/` diff EMPTY; GOVERNED_LITERALS still 17.
- V15-TESTED-debt: the four P3 test-gap rows have shipped in-process legs, each with a planted-red
  transcript beside the green one.
- A4 VERIFIED-kit: `sim/v5_fx_probe.gd` runs at the final tree, counter diff vs the 2026-10-28
  baseline is EXPLAINED row-by-row, and a re-declared baseline lands in the v1.5 run dir +
  ARCHITECTURE row (never quietly overwritten — DOC-TAIL rule).

## 2 DISPOSITIONS — every input row, with grounds checked this session

| # | input row (brief) | disposition | grounds (what I read at 65da857) |
|---|---|---|---|
| 1 | **KIT PRESENTATION** (marquee; MC 11857 FINDING) | **SHIP — W1, card W-K** | tests/test_kit_fx.py:25-37: writers are pure state crossings, fx_director "spawns ONLY from _observe_enemies/_observe_fires"; the re-pin clause is live (`_PRESENT_BAN` over the writer bodies, test_kit_fx.py:437-470). The fix is OBSERVER-SIDE by construction (writers are BANNED from touching fx tokens): a new kit-crossing observation pass in fx_director.gd (mounted mission.tscn:46, 261 ln, NOT in GOVERNED_LITERALS) detects `relic_uid` 0→uid on the published defense rows and spawns one existing fx sheet (`fx_spark_hit`, sprite_bank.gd:57) at the defense — zero new art, zero writer edits, zero mission.gd lines. KF-PRESENT/KF-FINDING re-pinned to the new measured shape in the same card (the clause is why it "cannot false-green"). DA P1-B rule rides (V14-PLAN §2 hp-tint row): the kit pass must be an UNCONDITIONAL pass in `fx_step` (a kit assign happens on frames with NO enemy hp drops — the `_observe_fires` drop-guard pattern would ship it dead). |
| 2a | P3 **F-2** blank_code families | **SHIP — W1, card W-T2 (tests-only)** | P3-wave.log:321 "js/html/css/cfg/py blanking families never exercised in-process"; `blank_code` lives in tools/check_hygiene.py:96, only "gd" runs in-suite (test files reuse it but only the gd family). Family-scoped tmp_path fixtures kill the class; fixtures generated per-run — NEVER under tests/fixtures/ (byte-pinned corpus). |
| 2b | P3 **F-3 + F-3a** static_app no in-process test; serve() OSError branch untested | **SHIP — W1, card W-T1 (tests-only)** | P3-wave.log:323-327 (11 survivors on the OSError branch; module reaches the suite only via subprocess, mutmut cannot associate). One new tests/test_static_app.py, ephemeral port (port 0) so the subprocess-tier tests never collide. |
| 2c | P3 **F-4** `_resolve` lstrip("/") boundary | **SHIP — W1, same card W-T1; DECLARED route deviation** | P3-wave.log:327/96 suggests adding `/xhr.js` rows to test_served/test_purity; the in-process file covers the SAME boundary with a post-slash name starting `x` (what the mutant needs to die) and keeps test_served.py (160 ln) untouched — the association that mutmut needs lands in the new module. Deviation named here per plan law. |
| 2d | P3 **F-5** VM350 `python3 -m venv` broken | **DEFER — out of repo scope** | P3-wave.log:328 calls it a host fact "worth fixing fleet-wide" — an infra card on the fleet board, not a gatewardens v1.5 row. Recorded, not silently dropped. |
| 3 | **v5_fx_probe re-baseline** (declared NOT RUN at v1.4) | **SHIP — W2, card W-R (verification)** | DOC-TAIL row + docs/ARCHITECTURE.md:154-156: the kit's documented home exists; baseline `.audits/20261027-1500-visual-target/gen/probe-v5-fx-green.log` predates G6/zoom and now predates W-K. Must run AT the W1-final tree — hence W2, never parallel with W-K. |
| 4 | **hp-tint DEFER** — re-open only if a defense-damage source exists NOW | **DEFER (grounds stand)** | Re-checked the assault code THIS session: enemies damage CORES only — mission.gd:369-374 `_on_reach` routes `rec.take_damage` where `rec` is `core_main`/`core_subs` (Cores live OUTSIDE defense_list); sim_combat.gd exposes `dmg_to_core` only; `defense_obj.take_damage` (defense_obj.gd:156) has NO production caller (grep of godot/scripts/*.gd + godot/sim/*.gd = the `mission_smoke_w8.gd` harness legs only). A live tint can still never paint. RE-OPENS the moment any tower-targeting mechanic lands (same trigger V14-PLAN §2 set). |
| 5 | **ready-up** (balance ruling never existed) | **OWNER-DECISION — OD1 (§6)** | V14-PLAN §2:123 + RN:DEFER row: new SIM mechanic in the I2-GOVERNED phase_controller.gd + a bonus number with no owner artifact; no new artifact found this session (LEDGER grep). Never-build-without-a-ruling applies. |
| 6 | **minimap** (DD row 13 P4) | **DEFER** | Condition still unmet — VERIFIED this session: `godot/data/maps/` holds ONE file (`gatefall.json`); DD-REFERENCE §5 row 13's own text: "Defer — value arrives when map 2+ or bigger arenas ship." |
| 7 | **D2 spawn-mouth shimmer** | **DEFER — stays parked (as instructed)** | Owner-deferred, restated by RELEASE_NOTES.md:193 + :300 "stay deferred"; V121-PLAN:172 (needs authored shader pass). No new owner artifact reopens it — disposing it differently would manufacture consent. |
| 8a | READABILITY heart — kb f821c305's named rows | **CLOSED, mostly — verified shipped; remainder disposed below** | The kb row (2026-10-28) predates the v1.2.1 G-wave: spawn-eye billboards SHIPPED (LEDGER:147 G1), lit lane bands SHIPPED (`lane_bands.gd` exists + LEDGER:150 G2), wave telegraphs SHIPPED (G3, LEDGER:151), range-while-placing SHIPPED (G4, LEDGER:155), ghost placement SHIPPED (G5, LEDGER:153), damage numbers SHIPPED (G6, LEDGER:148), hero crest taught + P8 legibility FIX SHIPPED (LEDGER:154/:162), coach banner SHIPPED (G8, LEDGER:149), selection ring SHIPPED (v1.4 P5, LEDGER:166), icon grey/red SHIPPED (v1.4 P6). The kb's premise "ships zero of these" is STALE — citing it as open work would re-plan shipped waves. |
| 8b | per-tower interaction keys (DD Q/R/Z family) | **REJECT for v1.5** | Gatewardens towers have no per-tower mode mechanic to key into — a key overlay would paint a mechanism that has no source (the exact class V14-PLAN used to REJECT the cd overlay). Selection ring + panel rows already answer "which tower am I acting on". Re-opens only with a tower-modes design card. |
| 8c | loot/item quality read (DD row 14 half) | **SHIP — W1, card W-Q** (planner-proposed from the row-8 remainder) | VERIFIED: rarity.json keys = {ladder, mod_slots, drop_weights, chest_tiers, sell_value} — NO colors key; item_row.gd:42-70 already binds `$Tint.color` from `rarity["colors"]` and falls back to gray everywhere; hud.gd:254-263 toast renders rarity as TEXT only. Adding the DATA key lights the already-wired mechanism everywhere items render (reuse-first made literal) + a data-driven toast tint. Monotone-safe: colors are not sim input (SIM_LOOT reads drop_weights) — golden fixtures stay byte-pinned (proven leg on the card). |
| 8d | damage-number starvation at MAX_FX (RN known-limit) | **DEFER** | fx_director header declares the cap discipline ("drop past the cap, never queued", MAX_FX=64, :56-59/:75); re-ordering drop priority changes a PINNED cost rule for a busy-wave nicety — not the smallest highest-value row in scope. Stays an honest known-limit. |
| 8e | "first maps AS the tutorial" (DD §4) | **DEFER** | Needs map CONTENT (one map ships — see row 6); G8's coach banner already carries the first-mission teaching in the shipped one-map product. Content milestone, not a presentation wave. |
| 9 | hygiene watch rows (mission.gd 400 / test_mission_clicks 600) | **CONSTRAINT (not a card)** | Measured with the gate metric (`len(read().split("\n"))`, check_hygiene.py:199-200): mission.gd **400**, tests/test_mission_clicks.py **600** — both AT ceiling. NO v1.5 card touches either (matrix §4 shows zero cells); hud.gd 385 carries the only near-ceiling growth (+few lines, W-Q) — named watch row. |

Frozen constraints honored across all waves: ZERO monetization (no row touches prices/store);
camera ZOOM-ONLY (D_MIN 56/D_MAX 128/STEP 8 re-read at camera_zoom.gd:45-47 — no card touches it);
END-ONLY (no mid-mission row proposed); tags v1..v1.4 frozen; suite/hygiene/fixtures law per §5.

## 3 WAVES — per-card brief sketches

PLAN LAW rows ride every card: per-card git worktree; LEDGER row in the card's own commit
(orchestrator single-writer for the LEDGER file — v1.4 P-rows precedent); pathspec-only commit;
author = profile (card); full suite green AT the card tree + hygiene 0 hits + fixtures diff
EMPTY; planted-red transcript beside the green one; children never spawn.

### W1 — four DISJOINT cards, parallel-safe (lane pre-flight `lane-load.sh 4` before the wave)

**W-K — kit-crossing presentation via the fx_director observer (the milestone HEART)**
- Files touched: `godot/scripts/fx_director.gd` (one new UNCONDITIONAL observation pass in
  `fx_step`: per-defense last-frame `relic_uid` snapshot; 0→uid → one `fx_spark_hit` billboard at
  the defense node position through the existing `_spawn_fx` (cap-respecting); optional symmetric
  unassign poof is DECLARED OUT (smallest leg)), `tests/test_kit_fx.py` (re-pin KF-PRESENT to
  "spark spawned across the assign window, delta > 0 under hand-driven pump" + re-pin the exact
  KF-FINDING string to the new measured shape; the `_PRESENT_BAN` source-truth leg stays UNTOUCHED
  and must stay green — proof the crossing lives observer-side), `LEDGER.md` row.
  ZERO mission.gd / mission.tscn / sim / sprite_bank lines (fx id + mount already exist).
- Test legs: existing KF matrix re-pinned; new standing detector: kit-crossing pass moved behind
  the drops-guard (the DA P1-B dead-shape) → KF-PRESENT RED; kit fx respects MAX_FX (cap-planted
  leg); zero-writes pin on the new pass (source-truth, F3 idiom).
- Planted-red: delete the new pass call from `fx_step` → re-pinned KF-PRESENT RED rc1 → byte-
  verified revert green.
- SERVED leg (per MC 11509 D3 — this is a visual SHIP row): loopback serve (static/ export
  present at tip) + headless chromium; shipped route: START → place Ballista (panel button →
  board click) → select the defense ROW → click a relic row → click "Assign relic"
  (defense_panel.gd:118). Verify the state's OWN marker first (Unassign button ENABLED + Assign
  disabled — served read-back), THEN pixel census: fx pixels at the tower's unprojected point in
  the burst window vs the identical pre-click frame, + describe-image literal read. Frames archived
  to the wave log.
- Watch: fx_director.gd 261 → ~285 (soft-note row already >250; ungoverned file).

**W-Q — rarity colors: light the data-waiting tint mechanism + tint the loot toast**
- Files touched: `godot/data/rarity.json` (+`colors` map: one Color-string per ladder name, the
  DD-class ladder worn→legendary gray/green/blue/purple/orange/red as authored DATA — F2's
  sell_value key precedent: schema gate tolerates extra keys, VERIFIED v1.2 F2 row),
  `godot/scripts/item_row.gd` (header de-stale to the truth, replace-not-delete; tint code
  ALREADY reads the key), `godot/scripts/hud.gd` (toast `modulate` from the same data map —
  zero literals, I2-safe; LOC 385 → ~390, WATCH ROW, headroom 15), new `tests/test_rarity_colors.py`.
- Test legs: data leg (key present, one parseable color per ladder name, ladder order pinned);
  engine tier (item_row.bind per rarity → `$Tint.color` == data color for all six — probe reads
  the SHIPPED node); toast leg (seeded loot_events row → toast modulate == data color); golden-
  fixture proof (`git diff tests/fixtures/` EMPTY — colors is not sim input); hygiene 0 hits.
- Planted-red: one color value swapped → engine leg RED; colors key removed → data leg RED.
- SERVED legs: hub bank with mixed rarities (shipped gear/victory routes) → per-rarity row-bg
  pixel-census rows + vision "distinct colors" read; mission toast: shipped pickup moment, toast
  TEXT visible first, then its tint censused.
- Regression risk check named: test_hub/test_hub_scroll state-reads unaffected (they pin state,
  not pixels); any tint-fallback string asserted in tests greps zero (card pre-flight leg).

**W-T1 — static_app in-process test card (closes F-3 + F-3a + F-4)**
- Files touched: new `tests/test_static_app.py` ONLY (server/static_app.py untouched — test-gap,
  not a code bug; the 13 survivors die at the next mutation sweep by association).
- Legs (~6): 200 byte-serve; 404 with the exact `{"error":"NOT_FOUND"}` JSON body; 405 wrong
  method; F-3a OSError branch (isfile true + chmod-000 open fails → pinned error path); F-4
  boundary (`/xhr.js`-class post-slash name starting `x` served intact); unknown-dir refusal.
  Ephemeral port bind (port 0) — zero collision with the subprocess-tier tests.
- Planted-red: OSError branch short-circuited (scratch) → the OSError leg RED.

**W-T2 — blank_code family fixtures (closes F-2)**
- Files touched: new `tests/test_blank_families.py` ONLY.
- Legs (~5): one per family (js/html/css/cfg/py) — strings/comments blanked, plain number
  literals survive (the gate's contract), plus one cross-family control asserting the "gd" row
  unchanged. Fixtures GENERATED in tmp_path (tests/fixtures/ is byte-pinned — never written).
  This tests the LIBRARY function, not the gate (I9 note idiom: not a second gate-runner).
- Planted-red: a family blanked with the wrong family (css as gd) → the surviving-string leg RED.

### W2 — one verification card (sequential after all W1 cards are committed)

**W-R — v5_fx_probe counter re-baseline (declared-not-run debt, paid at the v1.5 tree)**
- Files touched: the run transcripts + re-declared baseline in THIS run family
  (`.audits/…v15…/gen/probe-v5-fx-*.log` — never overwriting the 2026-10-27 visual-target file),
  `docs/ARCHITECTURE.md` §kits baseline-honesty row, `LEDGER.md` row, +1 pytest wrapper leg
  (run the kit via the documented command, assert V5FX markers + compare counters to the
  RE-DECLARED file — the P7 pytest-kit-probe precedent).
- Acceptance: kit rc0 stderr EMPTY at the final tree; every counter shift vs the old baseline
  EXPLAINED row-by-row (expected zero at rest — the kit run crosses no kit-assign; W-K's pass is
  a no-op without assignments — declared, then MEASURED, not assumed); a shift without a written
  cause is a FINDING, not a re-pin.
- Planted-red: the wrapper leg against a doctored copy of the baseline file → RED (never on the
  tracked kit itself).

Release tail (RN v1.5 section + README AT tag + docs grep-to-zero + tag/export/VM120/release-
notes doctrine) is the orchestrator's, per the GitHub-Release doctrine rows — not a plan card.

## 4 FILE-OVERLAP MATRIX + parallel safety

| file | W-K | W-Q | W-T1 | W-T2 | W-R |
|---|---|---|---|---|---|
| godot/scripts/fx_director.gd | ✔ | — | — | — | (runs it) |
| tests/test_kit_fx.py | ✔ | — | — | — | — |
| godot/data/rarity.json | — | ✔ | — | — | — |
| godot/scripts/item_row.gd | — | ✔ | — | — | — |
| godot/scripts/hud.gd | — | ✔ | — | — | — |
| tests/test_rarity_colors.py (new) | — | ✔ | — | — | — |
| tests/test_static_app.py (new) | — | — | ✔ | — | — |
| tests/test_blank_families.py (new) | — | — | — | ✔ | — |
| docs/ARCHITECTURE.md (§kits row) | — | — | — | — | ✔ |
| gen baselines (run-dir) | — | — | — | — | ✔ |
| mission.gd (400) / test_mission_clicks.py (600) | — | — | — | — | — (untouched by design) |

W1 is four mutually disjoint cards → one parallel wave (lane pre-flight sized 4; the wave is the
orchestrator's duty, this plan never spawns). W-R shares no EDITED file but depends on the W1
FINAL TREE (it measures W-K's fx behavior + W-Q's suite) → W2. LEDGER.md is excluded from the
matrix per the v1.4 single-writer-orchestrator precedent (each card stages its own row in its
pathspec commit; the F1/F2 LEDGER-race lesson is cited on every W1 brief: stage-before-plant).

## 5 SUITE-COUNT MATH (baseline measured THIS session: 324 collected with-export / 319 clean — the
test_served 5-leg module-skip reconciliation from the v1.4 DOC-TAIL row holds at tip)

| card | new pytest legs | projection |
|---|---|---|
| baseline (65da857) | — | **324** (319 clean) |
| W-K | KF re-pin is count-neutral; +1 standing dead-shape detector, +1 zero-write/cap source-truth | 326 |
| W-Q | data + engine-tint + toast + fixture-proof/source-truth legs = +3..4 | 329–330 |
| W-T1 | ~6 (success/404/405/OSError/lstrip/refusal) | 335–336 |
| W-T2 | ~5 (four families + control) | 340–341 |
| W-R | +1 kit wrapper leg | **341–342** with-export |

Clean-collect projection **336–337** (319 + the same 17–18). A card landing BELOW its bar (e.g.
merging legs) is honest only with a named count line in its wave log; suite-count drift never
re-sizes the bar upward without the count line.

## 6 OWNER-DECISION (exactly one row in scope)

**OD1 — ready-up / early wave call (DD row 12, P4).**
Question: *Should a "start next wave early" control ship at all — and if yes, at what bonus?*
The mechanic needs a balance number that has never existed as a literal artifact (fleet rule 2:
never-build-without-one).
Recommendation: **DEFER v1.5** — the milestone is presentation/feel; ready-up is a NEW sim
mechanic in an I2-governed file with golden-replay adjacency, and nothing measured says the
player is waiting for it (the telegraphs + countdown already teach the wave rhythm).
If the owner wants it anyway, the minimal ruling is: SPACE (or a HUD button) during BUILD starts
the wave immediately; bonus = floor(build seconds remaining × N) green with N a NEW economy.json
data key `early_call_green_per_sec`, N default **1** (no governed-file literal); tested
boundaries: zero bonus at timer expiry, double-press refused, golden fixtures byte-ident (no
golden run presses the key).
Default-if-silent: **DEFER** (no ruling = no mechanic; the row stays parked exactly as it is
parked at v1.4).

No other row in this plan needs the owner: the kit fx reuses shipped art, the rarity color ladder
is presentation DATA authored like F2's sell_value ladder (no balance content), and D2/hp-tint/
minimap re-opens all require a mechanic or artifact, not a ruling.

## 7 RISKS

1. **W-K burst transience**: `fx_spark_hit` life is short; a single post-click screenshot can miss
   it. Mitigation is IN the acceptance shape (state-marker-first, screenshot loop in the burst
   window, empty control frame for the census) — the engine leg carries the hard proof, the
   served leg carries the user-visible proof, exactly the v1.4 P5/P6 split.
2. **W-Q is visually broader than "the toast"**: the colors key lights item_row EVERYWHERE it
   renders (bank, blacksmith, toasts). That is the point (reuse-first), but the served scope must
   cover every item_row surface it can reach in-browser; if any hub surface reads WORSE (contrast),
   the card comes back with a data-only tweak (colors are data — the fix is a value edit, no code).
3. **KF re-pin is a contract flip**: KF-FINDING asserts an exact string today; a re-pin that
   preserves the old string while the shape changed is the false-green class. The card must show
   the OLD string failing against the NEW tree in the planted-red transcript before pinning the
   new one.
4. **W-R shift risk**: G6/zoom-era drift may move counters beyond "no kit crossing" explanation;
   then the row is an explained FINDING + re-declared baseline (DOC-TAIL rule), never a quiet
   overwrite of the 2026-10-27 file.
5. **hud.gd headroom (385/400)**: W-Q is the only growth near a ceiling; if a card proposal ever
   pushes hud.gd past ~392, the extract-first rule applies (banner/coach logic is the known
   extractable block — declared NOW, not at card panic).
6. **Port collisions** (W-T1) vs the subprocess-tier served tests — ephemeral bind mandatory,
   stated in the brief sketch.
7. **Lane load**: W1 = 4 children on the fleet's only lane; orchestrator runs the pre-flight and
   the one-watcher rule (AGENTS.md §fan-out) — this plan only sizes the wave.

*End: dispositions 16 rows (5 SHIP / 6 DEFER / 1 REJECT / 1 OWNER-DECISION / 3 CLOSED-verified /
constraint rows incl. hygiene watch). Wave plan: W1 = W-K ∥ W-Q ∥ W-T1 ∥ W-T2, W2 = W-R.
Suite 324 → 341–342 projected. Next gate: devils-advocate (orchestrated — this seat never spawns).*
