# V14-PLAN — v1.4 scope: dispose the open backlog, wave-decompose (MC 11827 · plan seat · 2026-10-31)

Base: HEAD `78f9be0` = tag `v1.3` + three doc-only release-tail rows (`git log v1.3..HEAD`
VERIFIED: RN marker / release log / paperwork sweep — zero code delta). This plan edits NO repo
code; READ-ONLY over the repo except this file. Length reason (file hygiene): one plan, one
subject — the disposition table and its waves are one contract; kept whole by the V121 precedent.

V121-PLAN §2 re-verification (the brief's named rows, read this session):
- **D1 SHIPPED — VERIFIED.** LEDGER:158-160 (zoom Z2 `camera_zoom.gd` wheel-only; Z3 mount) +
  LEDGER:160 RELEASE v1.3 row: "wheel zoom 56..128, default byte-ident (0a40d116) … 287 green |
  DONE 2026-10-31". README:9 states the shipped truth. D1 is CLOSED — not carried into v1.4.
- **D2 shimmer** — owner-deferred, KEEP DEFERRED (restated in §4 OD7; no new artifact reopens it).
- **D3 lanes-painted-into-texture** — REJECTED by the V1 honest cut (second visual mechanism
  beside lane_bands); KEEP REJECTED.
- **D4 open rows** — disposed individually in §2 (rows 1,2,3 below + ready-up/minimap).

## 0 Verified anchors (every number measured this session at 78f9be0, not memory)

- Gate metric (`tools/check_hygiene.py:197-198` `read(path).split("\n")`): `mission.gd` **400 =
  AT the ceiling — cards add ZERO lines to it**; `hud.gd` 385; `game_state.gd` 396 (untouchable);
  `defense_panel.gd` 366; `defense_placer.gd` 336; `fx_director.gd` 261; `defense_rows_ui.gd`
  185; `sprite_bank.gd` 145; `range_ring.gd` 89; `hero_pawn.gd` 91.
  `tests/test_mission_clicks.py` **600 = at the tests-tier 600 ceiling** — no card may grow it.
- Suite: `python3 -m pytest --collect-only -q` → **287 tests collected**; v1.3 row: 287 green.
  Hygiene at HEAD: `check_hygiene: 0 hit(s)`, HYGIENE_EXIT=0 (23 informational notes = baseline).
  System `pytest 9.0.3` (measured — matters for the mutmut card).
- REUSE idioms read this session: `range_ring.gd` (ONE unit TorusMesh, engine-managed PrimitiveMesh
  + `lit_material.gd` make() — the header's web-raster law: "the class family the G2 fix moved to
  … rasterizes under GL Compatibility/web"; the ring's three ghost chokepoints are its ONLY
  drivers); `fx_director.gd` (visual-only observer, per-frame walk over `runner.entities` AND
  `m.defense_list` in `fx_step`, MAX_FX=64 cap, mission.tscn LAST scene child); `world_text.gd`
  (the ONE Label3D mechanism); `defense_rows_ui.gd` (W17c selectable rows + W17e dirty-guarded
  sync pass — the shipped per-frame UI-sync hook); `lit_material.gd` (the ONE ground-material
  builder, v1.3 W3 fold).
- The open selection-ring row is a DECLARED finding, verbatim `range_ring.gd:14-20`: "a real
  selection mechanism EXISTS in code (defense_panel.selected_uid + select_defense…) … a
  selected-defense leg would be a second trigger site + a ring-priority rule (armed AND selected
  at once)" — and G4-wave.log:89 proves the hidden leg with `selected=0`.
- Refusal vocabulary (the F3 idiom's subject): `defense_placer.place_id` returns
  `{"ok":false,"why":"phase"|"class"|"id"|"slot"}` (defense_placer.gd:225,228,245,248,255);
  `mission.place_defense` returns `{"ok":false,"why":"tier"|"cap"|"green"}` (mission.gd:330,332,
  335). F3-wave.log's instrument set: refusal dicts + probe rc0 + **EMPTY stderr** as the
  no-exception proof + planted-red via working-tree mutation reverted `git checkout --`.
- G5 shipped the ARM-side combat lock (test_g5_build_confirm.py:257 "combat locks the rows WHILE
  AFFORDABLE and nothing places"); test_defense_boundaries.py covers the uid/cap boundary class.
  The full place_id×place_defense refusal matrix as ONE negative-test leg set is NOT shipped.
- v5_fx_probe kit: last run BYTE-STABLE vs `gen/probe-v5-fx-green.log` at CLEAN-CODE W1
  (LEDGER:87, 2026-10-28) — BEFORE G6 (damage numbers now count toward MAX_FX, fx_director.gd:35)
  and before the zoom wave; F5 never ran it (F5-wave.log:31-66 used a throwaway /tmp probe + the
  v1_world_probe smoke instead) — **V12-PLAN:297's "v5_fx_probe tracer rows unchanged (kit leg)"
  leg was NEVER executed**. §Verification kits (ARCHITECTURE.md:140-158) documents only
  v11_boss_shot; v5_fx_probe has no documented kit home.
- Hero crest: shipped by G7 (WORLD_H_HERO 3.0, name crest via world_text, LEDGER:154) — LEDGER:154
  closes with "crest leg **UNVERIFIED-in-web-pixels** (release known-limit)". F6 measured the
  scale class: char gain = 70.45/D px-per-unit at pitch-48 (V12-PLAN:325-326) → at the DEFAULT
  D=64 a 2 u sprite ≈ 13.3 px; crest-text height in served px has NEVER been measured.
- DD-REFERENCE.md §5 gap rows (read at `.audits/202610281826-9924ad48/out/DD-REFERENCE.md`,
  outside the repo — R2 public-material wall honored): row 6 selected-defense in-world P2; row 8
  defense hp tint P2 ("cheap modulate; the sprite swap already lives in sprite_bank"); row 9 icon
  grey/red/cd states P2 ("presentation-only over the shipped W17e poll sync"); row 12 ready-up P4
  ("start wave early" + bonus); row 13 minimap P4 ("Defer — value arrives when map 2+ or bigger
  arenas ship").
- Abandon row is ALREADY RULED: V12-PLAN:84-91 recommended END-ONLY; owner ruling 2026-10-28
  verbatim "rec on all 3" ratified it (LEDGER:95: "OWNER RULING END-ONLY … NO mid-mission exit
  control ships"), and the ruling is TESTED (test_return_hub.py NEGATIVE-MID leg + source-truth
  pin). No owner artifact since reopens it.
- Pure sim functions = `godot/sim/sim_*.gd` — **GDScript**; repo Python universe = tools/ server/
  tests/ only (40 tracked .py; grep VERIFIED no Python sim replica exists). mutmut mutates Python
  AST — it cannot target .gd files.

## 1 Constraint rows (binding on EVERY v1.4 card — quote in each brief)

1. **Camera pin:** D=64 is the DEFAULT distance; the v1.3 wheel zoom (56..128) is the ONLY rig
   move. Owner grant MC 11719 verbatim: **"Go 1 and zoom control for 2"** — ZOOM ONLY (README:9,
   RELEASE_NOTES:44, ZOOM_SPEC:11). Pan/rotate/pitch stay NOT granted; LOCKED pin #3 stays SPENT;
   no card edits the CameraRig row, `camera_zoom.gd` consts, or mission.tscn pin rows.
2. **ZERO monetization forever:** README:5 verbatim "No monetization, ever — by owner ruling
   2026-10-25" (+ "No shop. No loot boxes. No timers.", MC 11274.1). The I1 structural guard +
   `check_hygiene.py` TRIPWIRE token list are the shipped gates; any tripwire hit is a P0 STOP
   (the tripwire is never quietly widened or disabled — F2-4 on the record).
3. **mission.gd AT the 400-LOC ceiling** (measured 400 by the gate metric): v1.4 cards land in NEW
   scripts or the named ungoverned files; ZERO added lines to mission.gd. New files ≤250 soft
   (≤400 hard); tests ≤600 and `test_mission_clicks.py` sits AT 600 — no card grows it.
4. **Fixtures byte-pinned EMPTY:** every card's gate includes `git diff --stat tests/fixtures/`
   EMPTY + `git status --porcelain tests/fixtures/` EMPTY (golden/hard jsonl; eafe3932/5e37c4b0
   hash rows, LEDGER).
5. **Tags FROZEN:** v1.1/v1.2/v1.2.1/v1.3 never move; all work rides main on top. A new tag
   (`v1.4`) is a release-tail event only (§4 OD6).
6. **Suite ≥ 287 green at every card tip** (287 measured collected at HEAD; each card's bar = full
   suite green AT ITS tree, ≥ 287 + its own legs) + `check_hygiene` 0 hits + planted-red
   transcript beside the green one (fleet rule: a check that never went red is not a check).
7. **I2 governed literals:** the `GOVERNED_LITERALS` universe = 17 files
   (`tools/check_hygiene.py:80-85`, includes `defense_panel.gd`, `defense_placer.gd`,
   `defense_rows_ui.gd`): those files gain ZERO non-structural number literals — presentation
   numbers live in the ungoverned files (sprite_bank / range_ring / fx_director / world_text
   doctrine, C-4).
8. **Test ceiling 600** (hygiene:600-210): a header exemption never buys past it (W16 law).
9. Children are LEAVES (never spawn); lane pre-flight (`lane-load.sh <n>`) before each parallel
   wave; LEDGER row in-commit; pathspec-only commits; commit author = profile (card).

## 2 DISPOSITION TABLE — every open row, one each

| row (source) | disposition | mechanism it REUSES / reason |
|---|---|---|
| **selection ring on a PLACED tower** (V121 D4; DD row 6; the declared G4 finding range_ring.gd:14-20) | **SHIP — card P5 (W2)** | The ring itself EXISTS: `range_ring.gd` ONE TorusMesh PrimitiveMesh + `lit_material` (the PrimitiveMesh/rasterize-proven web path, G2 lesson honored). New leg = the selection trigger through the SAME single-site `_sync_ring` discipline + the DECLARED priority rule armed-ghost > selected > hidden. Replaces nothing (zero selection visuals today). |
| **tower hp tint** (V121 D4; DD row 8) | **SHIP — card P2 (W1)** | Rides `fx_director`'s EXISTING per-frame `m.defense_list` walk (no new observer, no mission.tscn growth): reads `obj.hp/hp_max` (public reads), writes ONLY the defense's own Sprite3D `modulate` (engine presentation property; greybox MeshInstance3D left neutral — declared). Sim-state writes: zero (fixtures-empty leg proves it). |
| **icon grey/red/cd states** (V121 D4; DD row 9) | **SHIP the grey/red half — card P6 (W3). cd-overlay half REJECTED (declared):** no build-cooldown state EXISTS in the sim (no cd field on towers.json rows / placer) — a cd overlay would paint a mechanism that has no source. | Presentation-only over the shipped W17e poll sync (`defense_rows_ui` sync pass precedent, `sync_marks` idiom): red when `cost > green`, grey when phase ≠ build; state READS the shipped fields, the shipped refusals stay the only enforcement (negative leg). Tint Color consts in `sprite_bank` (ungoverned home — panel/rows_ui are I2-governed). |
| **ready-up / early-call** (V121 D4; DD row 12, P4) | **DEFER** | A new SIM mechanic (early wave start + bonus) in the I2-governed phase_controller + a balance number the owner has never ruled; P4 in DD-REFERENCE; no owner artifact. Not v1.4. |
| **minimap** (V121 D4; DD row 13, P4) | **DEFER** | DD-REFERENCE's own row: "Defer — value arrives when map 2+ or bigger arenas ship". One map, one static-ish rig where the whole arena reads; a second navigation/overview mechanism answers no question the shipped rig asks. |
| **mid-mission abandon instrument** (V12-PLAN:84-91) | **REJECT (keep the ruling)** | Already RULED: owner 2026-10-28 "rec on all 3" ratified END-ONLY; the refusal is TESTED (test_return_hub NEG-MID + source-truth pin). Reopening needs a NEW owner artifact — none exists. Reload already loses nothing (C13 live commits, LEDGER:67). |
| **phase/slot REFUSAL negative tests** (F3 idiom row) | **SHIP — card P1 (W1), tests-only** | The refusal dicts exist (§0 vocabulary) but the matrix is untested as one F3-idiom set: place-in-combat (`why:"phase"`), bad/occupied slot (`why:"slot"`), unknown id, insufficient green, cap-full — each refusal asserts NO green spend, NO defense_list growth, NO save write, ghost unchanged; rc0 + EMPTY stderr; planted-red ×2. |
| **v5_fx_probe tracer kit leg** (V12-PLAN:297, never executed) | **SHIP — card P7 (W4), verification/docs** | The kit leg is due: run `sim/v5_fx_probe.gd` at the final tree in the ARCHITECTURE doc-leg form, diff counters vs the 2026-10-28 `gen/probe-v5-fx-green.log` baseline line-by-line (G6 numbers now share MAX_FX — any shift is DECLARED and re-pinned as the new honest baseline), and give the kit its documented home in §Verification kits (DC-1 homing idiom). Replaces the current zero-doc / stale-baseline state. |
| **mutmut mutation pass over the pure sim functions under a pytest<9 venv** (tooling row) | **SHIP the tooling card — P3 (W1), with a DECLARED re-read; the GDScript half REJECTED as infeasible (declared)** | mutmut mutates PYTHON (AST) — the pure sim functions are GDScript (`godot/sim/sim_*.gd`; VERIFIED no Python replica exists). The honest card: venv recipe (`python3 -m venv` outside the repo + pinned `pytest<9` + mutmut, the pytest-9.0.3 incompat reproduced once as the reason) run over the repo's ACTUAL pure-Python layer (`tools/check_hygiene.py`, `server/static_app.py`) against the full suite, and return the MEASURED mutant kill-rate row + survived-mutant triage. GDScript mutation coverage today = the planted-red rule + golden fixtures (same risk class, shipped mechanism); a GDScript mutation harness beside them = new machinery for a covered risk — its own design card ONLY if the owner asks (§4 OD3). |
| **hero-crest legibility at 1280px** (LEDGER:154 "UNVERIFIED-in-web-pixels") | **SHIP as a MEASURE card — P4 (W1); fix card P8 is CONDITIONAL (only if measured illegible)** | The shipped verification class for game visuals (MC 11509 D3): served browser 1280×720 at the DEFAULT D=64 + describe-image read-back (name spells correctly = legible = PASS) + a pixel-census row (crop at the unprojected crest point per the v1_world_shot idiom; glyph-block px height + contrast). Zero repo change. If ILLEGIBLE: fix rides the SAME files' presentation consts (`hero_pawn.gd` crest consts / `world_text.gd` TEXT_PX-OUTLINE — ungoverned, one mechanism, no new node type). |

D-rows restated for the record: D1 SHIPPED (§0), D2 DEFER (owner), D3 REJECT — all three ride
§4, none is a v1.4 card.

## 3 WAVES — same-file rows sequenced, parallel-safe across waves

Files disjoint INSIDE a wave; dependencies named. Per-card log at
`.audits/20261031-1830-v14-plan/<card>.log` ending `VERIFY_EXIT=0`, planted-red transcript beside
the green one. Every card's DoD (unrolled per card below): full suite green AT ITS tree (≥287 +
own legs), hygiene 0, fixtures diff EMPTY, no lines added to `mission.gd` or
`test_mission_clicks.py`, governed-file zero-literal check, LEDGER row in-commit, log closes
VERIFY_EXIT=0.

| wave | cards (∥ = parallel) | shared-file / dependency reason |
|---|---|---|
| **W1** | **P1 ∥ P2 ∥ P3 ∥ P4** | disjoint: tests/test_place_refusals.py NEW only • fx_director.gd(+new test) • NO repo change (venv + log) • NO repo change (browser artifacts + log) |
| **W2** | **P5** (selection ring) | defense_panel.gd + defense_placer.gd + range_ring.gd — shares defense_panel.gd with P6, so P6 is NOT in W1 |
| **W3** | **P6** (icon states) | defense_rows_ui.gd + defense_panel.gd (one drive line) + sprite_bank.gd — AFTER P5 (same file, panel byte-quiet at P5's tip) |
| **W4** | **P7** (kit leg + docs) | AFTER P2 (fx_director changed under it — the byte-stability claim must read the FINAL tree) |
| conditional | **P8** (crest fix) | ONLY IF P4 verdict ILLEGIBLE; hero_pawn.gd + world_text.gd (disjoint vs W2-W3 — can slot beside them after P4 lands) |

Lane pre-flight before W1's 4-way fan; children are leaves.

**Per-card DoD (checkable legs — the load-bearing ones):**

- **P1 (W1) place-refusal matrix** — files: `tests/test_place_refusals.py` NEW + log + LEDGER
  (tests-only, ZERO production edits; F3 scratch-revert rule verbatim). Engine probe
  (conftest.run_probe_script, tmp-probe R5 idiom, REFUSE-* rows): (a) place during combat via BOTH
  the armed panel route and a direct `placer.place_id` → `why:"phase"`; (b) occupied/off-list slot
  → `why:"slot"`; (c) unknown id → `why:"id"`; (d) cost>green → `why:"green"`; (e) cap-full →
  `why:"cap"` (name vs test_defense_boundaries coverage honestly — no duplicate legs, gap legs
  only). Every refusal row carries green/defense_list/saved_ack/ghost UNCHANGED reads; rc0 +
  stderr EMPTY. Planted-red ×2: phase-guard dropped → phase leg RED; slot-guard dropped → slot
  leg RED; `git checkout --` + byte-identical diff rows. DoD: 287+new legs green, hygiene 0,
  fixtures diff EMPTY.
- **P2 (W1) hp tint** — files: `fx_director.gd` + NEW `tests/test_hp_tint.py` + NEW
  `sim/g7_hp_tint_probe.gd`(+.uid) + log. Tint pass inside the existing `fx_step` walk (ONE
  site, header doctrine extended DECLARED: "writes stay confined to engine presentation
  properties of observed visual nodes"). Buckets = fx_director consts (e.g. hp_frac thresholds
  in-file, header-declared — never in a governed file); full hp = neutral Color(1,1,1). Legs:
  damaged defense → Sprite3D modulate != neutral; healed-to-full → neutral again (transition
  leg); TIER-UP node swap (defense_obj rebuilds `node`) → tint re-applies within one frame
  (upgrade-during-combat leg); greybox path untouched (negative); DEAD defense frees clean
  (teardown leg); fixtures diff EMPTY + mission public fields byte-stable across a tinted run
  (sim-untouched proof). Planted-red ×2: bucket comparison inverted → RED; tint branch removed →
  tint leg RED. describe-image/served leg orchestrator (C-6 class).
- **P3 (W1) mutmut tooling** — files: NONE in the repo (git porcelain empty except the log);
  artifacts: `P3-mutmut.log` + venv recipe + MEASURED kill-rate table. Legs: (1) reproduce the
  pytest-9.0.3 incompatibility once (measured transcript, then pin `pytest<9` + mutmut versions
  in the venv recipe — the recipe lands in the log, venv OUTSIDE the repo tree); (2) mutmut run
  scoped to `tools/check_hygiene.py` + `server/static_app.py` against the full pytest suite;
  (3) kill-rate row = killed/survived/suspicious counts, VERBATIM machine output; (4) survived
  mutants triaged P-class — P0/P1 survivors are FILED as new rows for the orchestrator, NOT
  silently fixed in this card; (5) the GDScript half closes with the declared REJECT text +
  §0's file-evidence. DoD: log carries the measured ratio line + the recipe + zero repo diffs.
- **P4 (W1) crest legibility MEASURE** — files: NONE in the repo; artifacts: served PNGs +
  describe-image transcript + pixel-census rows in `P4-crest-legibility.log` (run dir).
  Legs: serve the current export at 1280×720, mission booted to combat, default D=64 (the shipped
  default — camera UNtouched, constraint 1); unproject the active crest point, crop (the
  v1_world_shot crop idiom); pixel census = glyph-block height in px + contrast rows;
  describe-image read-back MUST state the active hero's name — PASS = spells correctly (vision
  verdict governs; census is the supporting measurement, both recorded). Verdict row LEGIBLE /
  ILLEGIBLE, one word, measured. DoD: both transcripts + verdict + VERIFY_EXIT=0. NO code change
  even if illegible — P8 is then filed as its own card.
- **P5 (W2) selection ring** — files: `defense_placer.gd`, `defense_panel.gd` (ONE drive line),
  `range_ring.gd` (selection entry points if needed), `tests/test_g4_range_ring.py` extension,
  `sim/g4_range_ring_probe.gd` extension, log. Mechanism = REUSE the ONE ring node
  (TorusMesh PrimitiveMesh + lit_material — the proven web-raster path, replace-not-add: the
  selected tower gets the SAME yellow ring, no second ring, no new material). Priority rule
  SHIPPED + DECLARED: armed ghost > selected > hidden — arm/cycle still win; `cancel_ghost`
  re-syncs to the selected defense if `selected_uid != 0`; deselect/combat-lock hides via the
  existing chokepoints. Range number via the SAME `tier_range` data door at the obj's tier (zero
  literals in governed files). Legs: select → ring visible, node position == obj pos (declared
  EPS), scale == that defense's tier-row range number (DATA leg, re-derived from towers.json);
  deselect → hidden (negative, `selected=0` pinned as in G4-HIDE0); selected blockade (range 0) →
  hidden, non-vacuous (the same node shown minutes earlier for a positive family — G4 pattern);
  armed-overrides-selected (priority leg); source-truth: exactly ONE ring node + the panel gains
  exactly ONE ring token (byte-count leg like G4's "panel carries no ring tokens" retargets);
  planted-red ×2: priority flip → priority leg RED; selection branch dropped → select leg RED.
  LOC watch rows in the log (panel 366 / placer 336, both < 400 after). describe-image served leg
  (ring visible on click-select) orchestrator.
- **P6 (W3) icon states** — files: `defense_rows_ui.gd`, `defense_panel.gd` (setup/sync wiring
  only), `sprite_bank.gd` (Tint Color consts — ungoverned), NEW `tests/test_icon_states.py`,
  tmp-probe (R5 idiom), log. Grey/red over the shipped W17e poll sync (the `sync_marks` cheap
  pass is the precedent — no per-frame churn). State reads only: `m.phase_kind`, `green` vs the
  row's data-carried `cost` (picker_rows already carry it — §0). Legs: affordable+build →
  neutral; unaffordable+build → RED tint class; non-build phase → GREY tint class (affordability
  irrelevant there — precedence leg, red does NOT mask grey); the tint NEVER gates: with a red
  button shown, the shipped place route still returns the same `{"ok":false,"why":"green"}` and
  vice-versa (negative leg); no churn: sync pass re-applies without freeing buttons (E9-safe,
  source-truth); cd-overlay half closes with the declared REJECT line (§2). Planted-red ×2:
  comparison swapped → red/grey legs swap-RED; sync removal → states leg RED.
- **P7 (W4) kit leg** — files: `docs/ARCHITECTURE.md` §Verification kits (add the v5_fx_probe
  row: unique leg + exact run command, the v11_boss_shot doc-leg form verbatim) + run-dir `gen/`
  capture + LEDGER + `P5`… `P7-kit-leg.log`. Legs: run `sim/v5_fx_probe.gd` with the conftest-
  pinned canonical binary (GW_GODOT-overridable), rc0 + stderr EMPTY; diff vs
  `.audits/20261027-1500-visual-target/gen/probe-v5-fx-green.log` — TRACER/SPARK/POOF/MOUNT rows
  byte-stable (any non-stability is named + re-declared, e.g. CAP live_max shift from G6 numbers
  sharing MAX_FX — explained line-by-line or the card FAILS); new baseline captured into the run
  dir gen/ + referenced from the log; doc gate: `grep -c v5_fx_probe docs/ARCHITECTURE.md` ≥ 1
  (was 0 in §Verification kits — measured). Full suite + hygiene + fixtures gates at the FINAL
  tree. No code change (if the diff shows a behavior change, that is a FINDING filed to the
  orchestrator, not a silent kit edit).

## 4 Owner-decision summary (each with a recommendation)

- **OD1 mid-mission abandon** — RECOMMEND: keep the existing END-ONLY ruling (it is owner-made
  and already tested). Reopening needs a new owner artifact; none exists.
- **OD2 ready-up / early-call** — RECOMMEND: keep DEFERRED (P4; if the owner ever wants it, the
  early-call BONUS is his balance ruling before any card exists).
- **OD3 GDScript mutation coverage** (the mutmut row's infeasible half) — RECOMMEND: NO new
  mechanism for v1.4. The shipped planted-red rule + golden fixtures already carry the "would the
  tests go red?" risk for the sim; a GDScript mutation harness beside them is a second mechanism
  for a covered concern. If the owner wants it anyway, it is its own design card in a later
  milestone (P3 still lands the Python-tier kill-rate number this session).
- **OD4 minimap** — RECOMMEND: keep DEFERRED until map 2+ / bigger arenas (DD-REFERENCE's own
  condition).
- **OD5 crest legibility** — no decision until P4 measures; if ILLEGIBLE the recommendation is a
  one-const presentation bump in the SAME crest mechanism (P8), not a new mechanism.
- **OD6 v1.4 tag + release** — RECOMMEND: yes, at the W4 close (conditional P8 folded in): tag
  `v1.4` + committed release notes + README-current + doc-sweep grep-to-zero, per the
  GitHub-Release doctrine; old tags FROZEN. The release tail is the orchestrator's own card.
- **OD7 D2 spawn-mouth shimmer** — KEEP DEFERRED (owner-deferred since V121; the gate-eye is the
  shipped cue). No artifact reopens it.

## 5 Shape of the result

7 SHIP cards (P1-P7) + 1 conditional fix card (P8, only if P4 measures ILLEGIBLE) + 1
already-ruled REJECT + 2 DEFERs, in 4 waves (4-parallel, 1, 1, 1) with the declared conditional. Zero mission.gd lines, zero new scene mounts,
zero new governed literals, zero new visual mechanisms — every shipped row rides a named existing
mechanism (the one ring, the one observer, the one poll sync, the one crop/describe instrument,
the one Label3D factory). Plan seat authored ZERO repo code; this document is the artifact.

## 6 Plan-file verification (run this session at 78f9be0, commands echoed above)

Disposition rows present for ALL ten backlog rows; waves W1-W4 with per-card checkable DoDs
(P1-P7 + conditional P8) and artifact paths under `.audits/20261031-1830-v14-plan/`; owner-decision
summary OD1-OD7 each with a recommendation; constraint quotes verified by grep (zoom grant
verbatim, monetization-ever, 400 ceiling, fixtures EMPTY, tags FROZEN, >=287 suite, 600 test
ceiling, GOVERNED_LITERALS). Repo untouched read-only check: `git status --porcelain` = plan dir
only; `git diff --stat tests/fixtures/` EMPTY; suite collects 287 at HEAD; hygiene 0 hits at HEAD.
All legs rc=0.

VERIFY_EXIT=0
