# V15-PLAN REV c2 — v1.5 "make-it-sing" scope (MC 11871 · plan seat · 2026-11-01, post-DA-gate-r1)

DA gate r1 verdict = FIX (`/home/claudecode/.local/state/knut-dispatch/card-11871.out/DA-verdict.md`).
REV c2 applied: F-A→W-T2 RE-SCOPED to the true residual (P1-1); F-B→KF re-pin proof promoted to a
HARD W-K acceptance leg (P1-2); F-C→LEDGER law restated per the real F1 precedent + matrix row
added (P2); F-D→W-R wrapper file NAMED in the matrix (P3-1); F-E→W-T1 F-4 leg requires an
UPPERCASE-X name (P3-2); F-F→chmod-000 root-sensitivity note added (P4); F-G citation drift fixed
(item_row header :17-24; F-2 block starts P3-wave.log:320; fx_director "261" = gate metric, wc 260).
Every changed claim RE-MEASURED this session (V15-PLAN.log REV-C2 rows). The heart (W-K/W-Q) is
UNTOUCHED in design — DA's own refutation round failed to move it.
VERSIONED-TRUTH CALL (declared): c1 is RETIRED, not amended — its first line now carries the
`SUPERSEDED — DO NOT USE` marker pointing here, because a builder must read ONE plan (the DA fixed
§2/§3/§4/§5/§7 rows in place across the doc; an amendment file beside a still-standing original
invites reading the wrong half). Same dir per the orchestrator's instruction; nothing deleted.

Base: HEAD `65da857` = v1.4 RELEASE (verified `git log -1`). READ-ONLY over the repo except this
dir. Length reason (file hygiene): one plan, one subject (V14-PLAN precedent).
DD-REFERENCE.md resolves OUTSIDE the repo at
`/home/claudecode/Games/.audits/202610281826-9924ad48/out/DD-REFERENCE.md` (R2 clean-room wall;
the brief's `docs/DD-REFERENCE.md` path does not exist — declared c1, still true).

## 1 GOAL + TESTABLE ACCEPTANCE — what the player FEELS different in v1.5

v1.4 shipped the kit FEATURE with zero presentation (P7 probe FINDING, pinned in
tests/test_kit_fx.py): assigning a kit is an invisible state crossing, and every loot/item row
renders gray because `rarity.json` never got a `colors` key while `item_row.gd`'s tint mechanism
already ships waiting for it (its header :17-24 declares exactly this). v1.5 "make-it-sing" = the
two state crossings the player makes most — "I equipped a kit" and "I picked up loot" — become
VISIBLE through EXISTING mechanisms only (fx_director read-only observer; rarity-data → shipped
item_row tint), plus the honest test-debt closure the v1.4 mutation pass routed forward
(F-2/F-3/F-3a/F-4, re-scoped where P9 already landed coverage) and the v5_fx_probe baseline
re-declaration declared NOT RUN at v1.4.

Milestone acceptance (release-tail leg, orchestrator-driven):
- A1 SERVED: placing a Ballista and assigning a kit through shipped clicks paints a visible fx
  burst at the tower (state's own panel marker verified in-frame FIRST, then pixel census vs an
  empty control frame + describe-image read; kb 1acdc1c3 discipline).
- A2 SERVED: bank/inventory item rows render per-rarity COLORS and the mission loot toast tints
  by rarity — vision reads distinct quality colors; every color arrives from rarity.json (zero
  new literals in I2-governed files).
- A3 TESTED: full suite green AT the final tree ≥ the §5 projection; `check_hygiene` 0 hits;
  `tests/fixtures/` diff EMPTY; GOVERNED_LITERALS still 17.
- A4 TESTED-debt: the P3 routed rows have shipped in-process legs (css + js-block-comment at the
  EXISTING positive-controls home), each with a planted-red transcript beside the green one.
- A5 VERIFIED-kit: `sim/v5_fx_probe.gd` runs at the final tree; counter diff vs the 2026-10-28
  baseline EXPLAINED row-by-row; re-declared baseline lands in the v1.5 run dir + ARCHITECTURE
  row (never quietly overwritten — DOC-TAIL rule).

## 2 DISPOSITIONS — every input row, grounds re-checked this session

| # | input row (brief) | disposition | grounds (what was read at 65da857) |
|---|---|---|---|
| 1 | **KIT PRESENTATION** (marquee; MC 11857 FINDING) | **SHIP — W1, card W-K** | test_kit_fx.py:25-37: writers are pure state crossings, fx_director spawns ONLY from `_observe_enemies/_observe_fires`; the re-pin clause is live (`_PRESENT_BAN` :439-443 applies to `_WRITER_BODIES` :445-449 = mission_relics/defense_obj/mission.gd — fx_director.gd is NOT in that tuple, DA-confirmed: the ban neither blocks nor touches the planned observer pass). Fix = observer-side: new kit-crossing pass in fx_director.gd (mounted mission.tscn:46, 261 ln gate metric / wc 260, ungoverned) detects `relic_uid` 0→uid on published defense rows and spawns one EXISTING sheet (`fx_spark_hit`, sprite_bank.gd:57) through the cap-respecting `_spawn_fx`; KF-PRESENT (live-fx 0→0, :383-385) + KF-FINDING (exact string, :391-392) WILL redden under W-K and get re-pinned — with the HARD re-pin-proof leg (F-B, §3 W-K). Kit assigns are build-phase-only (mission_relics.gd:16) → no enemy hp drops on those frames → the pass MUST be UNCONDITIONAL in `fx_step` (DA P1-B rule; a drops-guarded pass ships it dead). |
| 2a | P3 **F-2** blank_code families | **SHIP — W1, card W-T2 RE-SCOPED (tests-only)** — REV c2 | c1's grounds were FALSE at tip (DA F-A): `tests/test_hygiene_positive_controls.py` (v1.4 **P9**, MC 11838, LEDGER:165, 332 ln, 30 legs) ALREADY exercises blank_code in-process over gd (8 legs incl. block comments), py (:128/:136 triple-quote), js (:142 backtick), cfg (:156), html (:163/:166) — re-verified by opening the file this session. TRUE residual at tip (branch read at check_hygiene.py:96-135): (i) the **css** family — no test ever passes `"css"`, it appears only in the block-comment set `("gd","js","css")`; (ii) the **js block-comment branch** — js's only leg uses backticks + `//`; a mutant removing `"js"` from the block set survives (gd's block legs never notice `"js"` vanishing). W-T2 = EXACTLY those two legs, appended AT THE P9 HOME (one mechanism, one file — replace-do-not-add honored). |
| 2b | P3 **F-3 + F-3a** static_app in-process + OSError branch | **SHIP — W1, card W-T1 (tests-only)** | P3-wave.log:323-327: 11 survivors on the OSError branch; module reaches the suite only via subprocess (no mutmut association). New tests/test_static_app.py, ephemeral port. ROOT-SENSITIVITY NOTE (DA F-F): the OSError leg uses chmod-000 + open()-must-fail; true only for an unprivileged uid — the suite runs as `claudecode` on VM350 (VERIFIED whoami today); under root (DAC_OVERRIDE) the leg would RED — fails LOUD, not silent; declared. |
| 2c | P3 **F-4** `_resolve` lstrip("/") boundary | **SHIP — W1, same card W-T1; DECLARED route deviation** | P3-wave.log:327 + :102 (mutant_21 = `lstrip("/")` → `lstrip("XX/XX")`, strips the SET {X,/}): a post-slash name starting LOWERCASE `x` behaves IDENTICALLY under the mutant — lowercase survives (DA F-E). The leg therefore requests an **UPPERCASE-X** post-slash name (e.g. `/XHR.js`), asserted served-BYTE-INTACT, plus the lowercase `/xhr.js` case kept as the companion row so the leg kills the mutant AND pins the ordinary case. Route: new in-process file, not growing test_served.py (160 ln) / test_purity.py (107 ln) — the association mutmut needs lands with the direct import. |
| 2d | P3 **F-5** VM350 `python3 -m venv` broken | **DEFER — out of repo scope** | P3-wave.log F-5 row: host fact "worth fixing fleet-wide" — an infra card on the fleet board, not a gatewardens row. Recorded, not silently dropped. |
| 3 | **v5_fx_probe re-baseline** (declared NOT RUN at v1.4) | **SHIP — W2, card W-R (verification)** | docs/ARCHITECTURE.md:154-156 kit home + declared command; baseline `.audits/20261027-1500-visual-target/gen/probe-v5-fx-green.log` predates G6/zoom and any v1.5 fx change. Must run AT the W1-final tree — hence W2, never parallel with W-K. Wrapper file NAMED (DA F-D): new `tests/test_v5_fx_baseline.py` — deliberately NOT test_kit_fx.py (W-K's file) so no matrix cell lies; W2's sequencing makes any overlap moot anyway, but the matrix now tells the truth. |
| 4 | **hp-tint DEFER** — re-open only if a defense-damage source exists NOW | **DEFER (grounds stand)** | Assault code re-checked at tip: `_on_reach` (mission.gd:369-374) routes `rec.take_damage` where `rec` is `core_main`/`core_subs` (cores live OUTSIDE defense_list); sim_combat.gd exposes only `dmg_to_core`; `defense_obj.take_damage` (:156) has NO production caller (grep = `mission_smoke_w8.gd` harness legs only). A live tint can never paint. RE-OPENS when any tower-targeting mechanic lands (V14-PLAN §2 trigger). |
| 5 | **ready-up** | **OWNER-DECISION — OD1 (§6)** | V14-PLAN §2:123 + LEDGER:170: new SIM mechanic in the I2-GOVERNED phase_controller.gd; the bonus number has never existed as an owner artifact (LEDGER grep: none). No artifact = no mechanic. |
| 6 | **minimap** (DD row 13 P4) | **DEFER** | `godot/data/maps/` = ONE file (`gatefall.json`, ls); DD-REFERENCE §5 row 13's own text read at source: "Defer — value arrives when map 2+ or bigger arenas ship." |
| 7 | **D2 spawn-mouth shimmer** | **DEFER — stays parked (as instructed)** | Owner-deferred; RELEASE_NOTES.md:193 + :300 "stay deferred"; V121-PLAN:172 (authored-shader need). No new owner artifact — disposing it differently would manufacture consent. |
| 8a | READABILITY heart — kb f821c305's named rows | **CLOSED, mostly — verified shipped; remainder disposed below** | The kb (2026-10-28) predates the v1.2.1 G-wave; verified per row at tip: spawn-eye billboards SHIPPED (LEDGER:147 G1), lane bands SHIPPED (lane_bands.gd + LEDGER:150), wave telegraphs (G3/:151), range-while-placing (G4/:155), ghost placement (G5/:153), damage numbers (G6/:148), crest + P8 legibility fix (:154/:162), coach banner (G8/:149), selection ring (P5/:166), icon grey/red (P6). The kb's premise "ships zero of these" is STALE — re-planning it would duplicate shipped waves. |
| 8b | per-tower interaction keys (DD Q/R/Z) | **REJECT for v1.5** | No per-tower mode mechanic exists to key into (towers.json tiers carry range/dps only, no mode/cd field) — same class as the v1.4 cd-overlay REJECT ("would paint a mechanism that has no source"). Ring + panel rows already answer "which tower". |
| 8c | loot/item quality read (DD row 14 half) | **SHIP — W1, card W-Q** | rarity.json keys = {ladder, mod_slots, drop_weights, chest_tiers, sell_value} — NO colors key (printed); item_row.gd :42-70 already binds `$Tint.color` from `rarity["colors"]` with "gray" fallback; hud.gd:254-263 toast renders rarity as TEXT only. Shipping the DATA key lights the already-wired mechanism everywhere items render + a data-driven toast tint (F2's sell_value precedent: schema gate tolerates extra keys). colors is not sim input (SIM_LOOT reads drop_weights) — golden fixtures stay byte-pinned (proven leg). |
| 8d | damage-number starvation at MAX_FX (RN known-limit) | **DEFER** | fx_director header declares the cap discipline (:56-59/:75, "drop past the cap, never queued"); re-ordering drop priority changes a PINNED cost rule for a busy-wave nicety. Stays an honest known-limit. |
| 8e | "first maps AS the tutorial" (DD §4) | **DEFER** | Needs map CONTENT (one map ships); G8's coach banner carries the first-mission teaching in the shipped one-map product. Content class, not this milestone. |
| 9 | hygiene watch rows (mission.gd 400 / test_mission_clicks 600) | **CONSTRAINT (not a card)** | Gate metric (`len(read().split("\n"))`, check_hygiene.py:199-200): mission.gd **400**, tests/test_mission_clicks.py **600** — both AT ceiling; NO v1.5 card touches either (matrix §4). Near-ceiling growth named: hud.gd 385 (W-Q, headroom 15); tests/test_hygiene_positive_controls.py 332 → ~360 by W-T2 (soft note already baseline; far below the 600 tests ceiling). |

Frozen constraints honored: ZERO monetization; camera ZOOM-ONLY (D_MIN 56/D_MAX 128/STEP 8,
camera_zoom.gd:45-47, untouched); END-ONLY (no mid-mission row); tags v1..v1.4 frozen.

## 3 WAVES — per-card brief sketches

PLAN LAW rows ride every card: per-card git worktree; full suite green AT the card tree + hygiene
0 hits + fixtures diff EMPTY; planted-red transcript beside the green one; pathspec-only commit;
author = profile (card); children never spawn.
**LEDGER LAW, REV c2 (DA F-C) — restated as the real F1 precedent:** EVERY card writes its OWN
LEDGER row in its OWN pathspec commit (v1.4 F1/F2 precedent: F1 staged LEDGER.md PARTIAL =
HEAD + its own row, letting the sibling's row land untouched in the sibling's commit). The
orchestrator is NOT a single writer — it LANDS the four W1 cards SEQUENTIALLY (cherry-pick order
declared before the wave); four worktrees appending at the same LEDGER EOF is a KNOWN RACE
(declared c1, now acknowledged in the §4 matrix cell) and the resolution rule is **keep-both**
(append-order rows never conflict semantically; a textual conflict at EOF resolves by keeping both
rows in cherry-pick order). "Stage-before-plant" stays a per-card discipline, not the merge
mechanism (c1's category error, named by DA).

### W1 — four DISJOINT product-file cards, parallel-safe (lane pre-flight `lane-load.sh 4`)

**W-K — kit-crossing presentation via the fx_director observer (the milestone HEART)** — DESIGN
UNCHANGED BY DA GATE (F-B adds a leg, not a redesign).
- Files touched: `godot/scripts/fx_director.gd` (one new UNCONDITIONAL observation pass in
  `fx_step`: per-defense last-frame `relic_uid` snapshot; 0→uid → one `fx_spark_hit` at the defense
  through `_spawn_fx` (cap-respecting); unassign symmetric poof DECLARED OUT — smallest leg),
  `tests/test_kit_fx.py` (re-pin KF-PRESENT + KF-FINDING to the new measured shape; the
  `_PRESENT_BAN` source-truth leg STAYS green untouched), `LEDGER.md` (own row, own commit).
  ZERO mission.gd / mission.tscn / sim / sprite_bank lines (fx id + mount already exist).
- HARD acceptance legs (REV c2, F-B):
  1. **RE-PIN PROOF (planted-red class, runs FIRST in the card's transcript):** with W-K's
     fx_director change landed but test_kit_fx.py NOT yet re-pinned, RUN the OLD KF-PRESENT +
     KF-FINDING asserts against the NEW tree → both must go RED (the old 0→0/sparks_delta-0
     assert and the exact NONE-string cannot survive the new shape) — RED transcript archived
     BEFORE any re-pin edit; only then re-pin and show green. A re-pin whose old asserts never
     reddened is the false-green class and FAILS the card's DoD.
  2. dead-shape detector: move the kit pass behind the drops-guard (DA-verified sound: kit
     assigns are build-phase-only, zero drops those frames) → re-pinned KF-PRESENT RED.
  3. MAX_FX: kit fx obeys the cap (cap-planted leg, drop-past-cap).
  4. zero-writes source-truth on the new pass (F3 idiom; rc0 + EMPTY stderr).
  5. `_PRESENT_BAN` leg green untouched (writers never touched — observer-side proof).
- Planted-red for the pass itself: delete the new pass call from `fx_step` → re-pinned KF-PRESENT
  RED rc1 → byte-verified revert green.
- SERVED leg (MC 11509 D3): loopback serve + headless chromium; shipped route: START → place
  Ballista (panel button → board click) → select defense ROW → click relic row → "Assign relic"
  (defense_panel.gd:118); verify the state's OWN marker first (Unassign ENABLED + Assign disabled,
  served read-back), THEN pixel census: fx pixels at the tower's unprojected point in the burst
  window vs the identical pre-click frame + describe-image literal read. Frames archived.
- Watch: fx_director.gd 261 (gate metric) → ~285 (ungoverned; >250 soft note already baseline).

**W-Q — rarity colors: light the data-waiting tint + tint the loot toast** — UNTOUCHED by DA gate.
- Files touched: `godot/data/rarity.json` (+`colors`: one Color-string per ladder name, authored
  DATA — F2 sell_value precedent), `godot/scripts/item_row.gd` (header :17-24 de-stale,
  replace-not-delete; tint already reads the key), `godot/scripts/hud.gd` (toast `modulate` from
  the same data map, zero literals, I2-safe; 385→~390 WATCH ROW), new `tests/test_rarity_colors.py`.
- Legs: data (key present, one parseable color per ladder name, order pinned); engine tier
  (item_row.bind per rarity → `$Tint.color` == data color, all six — shipped-node probe); toast
  (seeded loot_events row → toast modulate == data color); golden-fixture proof (`git diff
  tests/fixtures/` EMPTY — colors is not sim input); hygiene 0 hits.
- Planted-red: color swapped → engine leg RED; key removed → data leg RED.
- SERVED legs: hub bank mixed rarities (shipped routes) → per-rarity row-bg pixel-census + vision
  "distinct colors"; mission toast at the shipped pickup moment — TEXT visible first, then tint
  censused.
- Pre-flight check named: grep that no in-suite leg asserts the gray fallback string (risk row).

**W-T1 — static_app in-process test card (closes F-3 + F-3a + F-4)**
- Files touched: new `tests/test_static_app.py` ONLY (server/static_app.py untouched — test-gap,
  the 13 survivors die at the next sweep by association).
- Legs (~6): 200 byte-serve; 404 exact `{"error":"NOT_FOUND"}` body; 405 wrong method; F-3a
  OSError branch (isfile true + chmod-000 open fails → pinned error path; ROOT-SENSITIVITY
  DECLARED per §2 2b — suite runs unprivileged, root would flip it RED-loud); F-4 boundary with
  an **UPPERCASE-X** post-slash name (`/XHR.js` served byte-intact) + lowercase companion
  (§2 2c); unknown-dir refusal. Ephemeral port (port 0) — zero collision with subprocess-tier
  served tests.
- Planted-red: OSError branch short-circuited (scratch) → that leg RED.

**W-T2 — blank_code TRUE residual at the EXISTING P9 home (RE-SCOPED, REV c2 / DA F-A)**
- Files touched: APPEND to `tests/test_hygiene_positive_controls.py` ONLY (the P9 file IS the
  blank_code fixture home — named choice: extending it keeps ONE fixture mechanism; a new file
  would be the second mechanism beside a shipped one, the exact defect DA F-A named). LOC 332 →
  ~360 (soft >250 note already baseline; 600 tests ceiling far). No production edit. No
  tmp_path set needed (inline fixture strings, the file's own idiom).
- Legs (+2, EXACTLY the residual): (i) **css family** block-comment blanking (`/* hidden */`
  passes as "css" → blanked, newlines kept; + in-leg passthrough control: `/* keep */` survives a
  "gd"-NOT call only where true — mirror the file's html-leg shape); (ii) **js block-comment**
  branch (`/* */` passes as "js" → blanked — the branch the js leg set never entered; kills the
  remove-"js"-from-set mutant).
- Planted-red: blank the css input as family "gd"-with-block-set-mutant style — i.e. mutate
  GW_HYGIENE_MUTANT_DIR copy to drop "css" from `("gd","js","css")` → css leg RED (the file's own
  mutant-dir mechanism, no second harness).
- §2 grounds corrected in-place here: c1's "only gd runs in-suite" line was FALSE at tip (P9 read
  AFTER P3-wave.log shipped); this row states the tree, not the finding.

### W2 — one verification card (sequential after ALL W1 cards are committed and landed)

**W-R — v5_fx_probe counter re-baseline (declared-not-run debt, paid at the v1.5 tree)**
- Files touched: run transcripts + re-declared baseline in THIS run family
  (`.audits/…v15…/gen/probe-v5-fx-*.log` — never overwriting the 2026-10-27 file),
  `docs/ARCHITECTURE.md` §kits baseline-honesty row, `LEDGER.md` (own row), and the named wrapper
  file **`tests/test_v5_fx_baseline.py`** (NEW; runs the kit via the ARCHITECTURE-documented
  command, asserts V5FX markers + counters vs the RE-DECLARED file — P7 pytest-kit-probe precedent
  shape, own file so no W-K overlap, §4 matrix now carries the cell).
- Acceptance: kit rc0 stderr EMPTY at the final tree; every counter shift vs the old baseline
  EXPLAINED row-by-row (expected zero at rest — the kit run crosses no kit-assign and W-K's pass
  is a no-op without assignments — declared, then MEASURED); a shift without a written cause is a
  FINDING + re-declared baseline, never a quiet overwrite.
- Planted-red: wrapper leg against a doctored COPY of the baseline file → RED (tracked kit/baseline
  byte-untouched).

Release tail (RN v1.5 section, README AT tag, docs grep-to-zero, tag/export/VM120, GitHub-Release
doctrine) = the orchestrator's, not a plan card.

## 4 FILE-OVERLAP MATRIX + parallel safety (REV c2)

| file | W-K | W-Q | W-T1 | W-T2 | W-R |
|---|---|---|---|---|---|
| godot/scripts/fx_director.gd | ✔ | — | — | — | (runs it, read-only) |
| tests/test_kit_fx.py | ✔ | — | — | — | — |
| godot/data/rarity.json | — | ✔ | — | — | — |
| godot/scripts/item_row.gd | — | ✔ | — | — | — |
| godot/scripts/hud.gd | — | ✔ | — | — | — |
| tests/test_rarity_colors.py (new) | — | ✔ | — | — | — |
| tests/test_static_app.py (new) | — | — | ✔ | — | — |
| tests/test_hygiene_positive_controls.py (extend) | — | — | — | ✔ | — |
| tests/test_v5_fx_baseline.py (new) | — | — | — | — | ✔ |
| docs/ARCHITECTURE.md (§kits row) | — | — | — | — | ✔ |
| gen baselines (v15 run-dir) | — | — | — | — | ✔ |
| LEDGER.md | ✔ own row | ✔ own row | ✔ own row | ✔ own row | ✔ own row — **known race cell**: 4 W1 cards append at the same EOF in 4 worktrees; resolution = orchestrator lands SEQUENTIALLY, cherry-pick conflicts resolved KEEP-BOTH in pick order (F1 PARTIAL-staging precedent, §3 LEDGER LAW) |
| mission.gd (400) / test_mission_clicks.py (600) | — | — | — | — | — (untouched by design) |

W1's four cards share NO product or test file (LEDGER.md is the one shared file, race-resolved by
the declared rule — acknowledged, not excluded). W-R measures the W1 FINAL TREE → sequential W2.
Lane pre-flight sized 4 (orchestrator duty; this plan never spawns).

## 5 SUITE-COUNT MATH (REV c2) — baseline measured: 324 collected with-export / 319 clean
(the 319 already contains P9's 30 legs — the reconciliation the v1.4 DOC-TAIL row states, re-read
this session)

| card | new pytest legs | projection (with-export) |
|---|---|---|
| baseline (65da857) | — | **324** (319 clean) |
| W-K | KF re-pin count-neutral; +1 dead-shape detector, +1 zero-write/cap source-truth (re-pin proof is a transcript, not a new leg) | 326 |
| W-Q | data + engine-tint + toast + fixture-proof/source-truth = +3..4 | 329–330 |
| W-T1 | ~6 (success/404/405/OSError/X-boundary/refusal) | 335–336 |
| W-T2 | **+2 (css, js-block — RE-SCOPED; was +5 in c1)** | 337–338 |
| W-R | +1 wrapper leg (tests/test_v5_fx_baseline.py) | **338–339** |

Clean-collect projection **333–334** (319 + the same 19–20 deltas). A card landing BELOW its bar
is honest only with a named count line in its wave log; the bar never moves up silently.

## 6 OWNER-DECISION (exactly one row)

**OD1 — ready-up / early wave call (DD row 12, P4).**
Question: *Should a "start next wave early" control ship at all — and if yes, at what bonus?*
The mechanic needs a balance number that has never existed as a literal artifact.
Recommendation: **DEFER v1.5** — the milestone is presentation/feel; ready-up is a NEW sim
mechanic in an I2-governed file with golden-replay adjacency, and nothing measured says the player
is waiting for it (telegraphs + countdown already teach the wave rhythm).
If the owner wants it, the minimal ruling: SPACE (or a HUD button) during BUILD starts the wave
immediately; bonus = floor(build seconds remaining × N) green, N a NEW economy.json data key
`early_call_green_per_sec`, default **1** (no governed-file literal). Tested boundaries: zero
bonus at timer expiry, double-press refused, golden fixtures byte-ident (no golden run presses the
key).
Default-if-silent: **DEFER** (no ruling = no mechanic; row stays parked exactly as at v1.4).
No other row needs the owner: kit fx reuses shipped art, rarity colors are presentation DATA
(F2 precedent), D2/hp-tint/minimap re-opens need a mechanic or artifact, not a ruling.

## 7 RISKS

1. **W-K burst transience**: single post-click screenshot can miss the spark; acceptance shape
   (state-marker-first, screenshot loop in the burst window, empty control frame) mitigates; the
   engine legs carry the hard proof, the served leg the user-visible proof (v1.4 P5/P6 split).
2. **W-Q is visually broader than "the toast"**: the colors key lights item_row EVERYWHERE it
   renders; served scope covers every reachable item_row surface; a contrast miss is a DATA tweak.
3. **KF re-pin false-green class** — c1 carried this as prose; REV c2 (DA F-B) it is W-K
   acceptance leg 1 (OLD asserts shown RED on the NEW tree before re-pinning). Risk stands only as
   a pointer to the leg.
4. **W-R drift**: G6/zoom-era counter shifts beyond "no kit crossing" → explained FINDING +
   re-declared baseline, never overwrite (DOC-TAIL rule).
5. **hud.gd headroom (385/400)**: W-Q is the only near-ceiling growth; any push past ~392 triggers
   the extract-first rule (banner/coach block is the named extractable — declared NOW).
6. **Port collisions** (W-T1): ephemeral bind mandatory (stated in the sketch).
7. **chmod-000 root-sensitivity** (W-T1 OSError leg): unprivileged-only truth, declared §2 2b; a
   future root-context run flips it LOUD.
8. **LEDGER EOF race** (§4 cell): real, owned by the sequential-landing + keep-both rule; the card
   that skips its own LEDGER row is the defect the F1 PARTIAL-staging idiom prevents.
9. **Lane load**: W1 = 4 children on the fleet's only lane; pre-flight + one-watcher rule are the
   orchestrator's (AGENTS.md §fan-out).

*End REV c2: dispositions unchanged in count (5 SHIP / 6 DEFER / 1 REJECT / 1 OWNER-DECISION /
3 CLOSED-verified + constraint rows) — W-T2 re-scoped, W-K gains one hard acceptance leg. Waves:
W1 = W-K ∥ W-Q ∥ W-T1 ∥ W-T2 (LEDGER race owned), W2 = W-R. Suite 324 → 338–339 projected
(333–334 clean). Next gate: DA r2 on THIS file (orchestrated — this seat never spawns).*
