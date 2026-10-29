# V121-PLAN — v1.2.1 READABILITY WAVE (MC 11680 · plan seat · 2026-10-29)

Rev 2 (2026-10-29) — DA c1 amendments folded in place (verdict FIX:
`.audits/20261029-2100-v121-plan/out/DA-verdict.md` A1–A4; the judged copy + verdict are NOT touched).
Length reason (file hygiene): Rev 2 amendments push the doc to ~308 lines over the ~300 mark —
kept whole deliberately: it is one plan, the per-card DoD legs are read against their feature row,
and splitting the plan across files at amendment time would split the contract the cards cite.

Base: tip `fa131fc` (= v1.2 tag `c95798b` + release rows). This plan edits NO repo code;
every anchor below was READ this session (line refs are from this tree).
Owner identity artifact (verbatim 2026-10-29): "Go. This iss supposed to be a third person tower
defence game where the hero char runs around and build towers on lanes/maze gor mobs tryibg to
reach the center" — the read must land at a glance: where I am (hero), where mobs come from,
which path they take, where I can build, what my click does.
DoD reading used: features = gap rows 1,2,3,4,5,10,11 of `DD-REFERENCE.md` §5 (row 2 = the lane
band, treated with its smallest honest cut) + row 7 pulled in (its DoD example is named in the
task); rows 6,8,9,12-14 stay P2/P4 backlog; anything needing a real design pass lands as a
DEFER row (§4), never as silent scope.
R2 wall (binding): cite ONLY DD-REFERENCE's public-material findings; NEVER fetch game assets;
all art/code ours (new sheets ride the same 3090 generation pipeline as the v11 batches).

## 0 Verified anchors (all read this session at fa131fc)

- Observer idiom: `fx_director.gd` — visual-only observer, reads `runner.entities`, diffs hp
  per frame (`:105-134` `drops[iid]` = hp lost this frame — already computed), ONE spawn site
  `_spawn_fx` via `sprite_bank.make_sprite` (`:189-200`), `MAX_FX=64` cap (`:59`). Mounted as
  mission.tscn scene child (`mission.tscn:6,:43` — the precedent for new visual nodes).
- Billboard factory: `sprite_bank.gd:115-123 make_sprite(id, world_h, tier)` (camera-facing
  Sprite3D; null = greybox keeps, no second render path); id→file map `TEXTURES :24-68`;
  presentation-number home `ICON_PX/ICON_GAP :74-75` (the "numbers live in the bank" precedent).
- Emblem mount precedent: `mission_world.gd:104` core emblem child via make_sprite;
  `build_cores` calls `paint_arena` once per mission build (`:81`) — the visual-hook home that
  keeps mission.gd at its ceiling.
- Lanes: `gatefall.json` = 3 spawners (spawn_a/b/c), 3 ground + 2 air lanes with waypoint lists;
  `mission_world.build_lanes` (`:57-69`) stores `{id,kind,wps,target,open}` (drops the map's
  per-lane `"spawner"` key — raw `m.map_def` carries it, a public read).
- Placement: `defense_placer.gd` — ghost state `set_ghost/cancel_ghost` (`:105-110`) has
  ZERO callers outside the file (re-grep this session: none); `place_id` (`:135-148`) uses the
  ghost when armed, ONE `m.place_defense` call site (`:148`); `row_for_id` (`:66`); slots =
  ground waypoints round-robin (`:199-227`).
- Damage: the ONLY hp-decrement write is `enemy_runner.gd:161 damage()`; every caller routes
  through it (defense_obj.gd:176,183,196; hero_combat.gd:126) — the single damage site.
- Banner: `hud.gd:95 banner=$Root/Banner`, `banner_text():241` (outcome-mapped),
  `banner_shown():267`; `phase_controller.gd:26 signal phase_changed(kind)` fires `"combat"`
  exactly once per wave start (`:82`) — re-checked emission sites `:74,:82`.
- Input: `bridge.gd` relays `MouseLeft/MouseRight` as discrete press codes (`:20-23`),
  arrows as held MOVE_KEYS (`:17`); panel consumes presses via `poll()` — NO new input
  mechanism is needed. No camera picking (W17c constraint) — none proposed.
- Ranges: `towers.json` tier rows carry `range` 12.0–20.0 u (shooters) and 2.0–3.0 (barbed_snare),
  plus EXACTLY FIVE `range: 0.0` tier rows — all of `gate_blockade` (counted Rev 2); zero render
  sites today.
- Wave data: `godot/data/waves/waves_gatefall_<difficulty>.json` wave rows = `{build_seconds,
  enemies:[{enemy_id, count, lane, delay}]}` — the telegraph's read-only source. `Label3D` appears ZERO times in
  godot/ (grep) — first use is DECLARED as the one world-text mechanism (`world_text.gd`).
- Suite: 239 collected green (measured this session); fixtures `tests/fixtures/mission_gatefall_
  {normal,hard}.jsonl` byte-pinned; hygiene gate = `tools/check_hygiene.py`, LOC metric
  `read(path).split("\n")` (`:197-198`).

## 1 Feature rows (replace-not-add; each names its mechanism and what it replaces)

**G1 — spawn-gate eye billboards (gap row 1, P1).** Original eye billboard at each spawner pos
(`m.map_def["spawners"]`), winged variant on spawn_a/spawn_b (they carry air lanes lane_a1/a2;
ground-only spawn_c plain — declared reading). MECHANISM: `make_sprite` + emblem-mount idiom
(`mission_world.gd:104`), built from `build_cores` (paint_arena hook `:81`); NEW ids
`icon_gate_eye`, `icon_gate_eye_air` in `sprite_bank.TEXTURES` + 2 new original 3090 sheets.
REPLACES: nothing runs today (DD-REFERENCE grep: zero spawner visuals) — this is the one marker
mechanism, the v7 "tiny badges in the top band" stay as HUD icons (row 10 note), untouched.
Files: `mission_world.gd`, `sprite_bank.gd`, `assets/v11/` (2 pngs), new probe/test.

**G2 — lane bands, smallest honest treatment (gap row 2, P1).** Lit translucent band painted
along the EXISTING waypoint polylines: per ground lane, one quad-strip per waypoint segment at
y slightly > 0, one material, `m.lanes` read-only. Air lanes get NO band (the winged eye of G1
is their cue — declared). MECHANISM: new static builder `lane_bands.gd`, called once from
`mission_world.build_cores` (the paint_arena hook precedent `:81`); material/height numbers live
in `lane_bands.gd` (ungoverned presentation file, the sprite_bank doctrine). REPLACES: nothing
(no lane mesh exists, LEDGER V1 honest cut). DEFER rows D2/D3 own the shimmer + painted-texture
treatment (§4). Files: `lane_bands.gd` NEW, `mission_world.gd` (+~2-line hook), test.

**G3 — build-phase wave telegraph (gap row 3, P1).** During build phase, a small billboard per
spawner: enemy sheet icon (ids already in the bank) + `Label3D` count, for the upcoming wave
(`m.wave` row), grouped by lane→spawner via raw `m.map_def` lanes rows; cleared on combat start.
MECHANISM: fx_director OBSERVER idiom — new `wave_telegraph.gd`, mounted as a mission.tscn scene
child (the `FxDirector` precedent, `mission.tscn:43`), own `_process`, reads mission fields
(m.wave/phase_kind/waves_file/map_def), ZERO writes (the fx_director header doctrine extends to
it); counts via `world_text.gd` (G6's factory). REPLACES: nothing (no per-gate preview exists);
the HUD "Wave n/11" label stays (panel = when, billboards = what/where).
Files: `wave_telegraph.gd` NEW, `mission.tscn` (append-only Rev 2/DA A4.2: new ext_resource +
node + the `wave_telegraph.gd.uid` SIDECAR riding the same commit + the `load_steps` header bump
— test_mission_clicks pins every ext uid == its sidecar and BANS stale pairs (`:31-32,:54`);
pin rows themselves untouched, fx_director precedent `:6,:43`), probe/test.

**G4 — range ring while placing / when selected (gap row 4, P1).** Flat translucent ground ring
at the ARMED slot (armed family's T1 tier range) and at a selected defense (its tier range).
Range values read from `towers.json` tier rows (never literals — placer/panel are I2-governed);
range≤0 rows render NO ring (the five gate_blockade tier rows — declared, Rev 2/DA A4.1).
MECHANISM: leg of the placement readout file (G5) + `make_sprite` is NOT it (ground ring is not
camera-facing) → same primitive-quad + material approach as G2; ONE readout file serves marker +
ring (one concern: aimed-placement readout). REPLACES: nothing renders range today (grep: zero
render sites). Files: `placement_readout.gd` (with G5), `defense_panel.gd` (drive lines, post-split).

**G5 — ghost aim + LMB-confirm / RMB-cancel (gap row 5, P1).** Ship the ALREADY-BUILT ghost:
class/family button press now ARMS (sets `selected_class`/id AND `placer.set_ghost(first_free)`);
`◀`/`▶` panel buttons cycle `set_ghost` through `placer.buildable()`; a `MouseLeft` press while
armed CONFIRMS (routes `placer.place_id(armed_id, 1)` — the ghost resolves inside it,
`:141-143`); `MouseRight`/`Escape` CANCELS (`cancel_ghost`). Codes are relayed today
(`bridge.gd:20-23`) — no new input mechanism; no camera picking (constraint holds).
REPLACES (declared UX change): "panel press = instant place at first free slot" becomes
"press = arm + visible ghost; confirm = place" — `place_id`'s no-ghost first-free fallback STAYS
(explicit-slot/harness callers unchanged); the shipped placement tests (test_mission_clicks,
test_family_picker) are updated to the new flow IN THE SAME card. The panel's PRESS map
(`defense_panel.gd:50`) gains the confirm/cancel codes beside KeyM/KeyE/KeyN (KeyM keeps place =
confirm when armed — same route; **KeyM UNARMED = today's behavior unchanged: legacy instant
place through the first-free fallback `place_id:141-145`, pinned as a standing behavior, not
re-decidable by a later card — Rev 2/DA A4.3**). Files: `defense_panel.gd`, `defense_placer.gd`
(cycle helper, I2-clean), `placement_readout.gd` NEW, tests — SPLIT PRECONDITION below (§3 C-1).

**G6 — floating damage numbers (gap row 7, P2 pulled in — the task names its DoD).** Reuse
fx_director's existing per-frame drop diff (`_observe_enemies :113-114` — `drops[iid]` already
equals the hp lost this frame): at each spark drop also spawn a short-lived number at the same
point via NEW `world_text.gd.make_text(str(int(amount)), ...)` (Label3D factory, first use
DECLARED as the one world-text mechanism; shared by G3/G7). Lives under the SAME `MAX_FX=64`
cap (numbers count toward `_fx`; drop-past-cap unchanged — DECLARED: on busy waves NUMBERS can
be starved by tracers/sparks riding the same cap, DA A5; rides the release known-limits line).
REPLACES: nothing; the spark still fires (number rides it, one event one position).
**Kill-blow truth (Rev 2 / DA A1):** `mission.step` applies ALL damage before
`enemy_runner.step` DRAINS `hp<=0` in the SAME tick (`enemy_runner.gd:133-136`), so the observer
never sees the killing amount — the plain contract is false for the headline case. CHOSEN SHAPE
(orchestrator decision, read-only route VERIFIED): the `_tracked`-erase branch
(`fx_director.gd:126-133`) ALREADY holds `snap["hp"]` = last-observed hp (the observer's own
per-frame bookkeeping `:122`; no sim write, no new read), and already DISCRIMINATES death
(hp<=0 or last pos NOT at lane end, `:130-131`) from breacher (at end, hp>0). So on the
DEATH-disappearance branch G6 also renders the FINAL number at `snap["hp"]`, semantics DECLARED:
"hp remaining at last observation == a LOWER BOUND of the killing blow (overkill unobservable —
DA A1); non-death drops stay exact". CONTRACT (re-written): a number's value == the hp drop
OBSERVED for every observed hit, == snap["hp"] (declared lower bound) on the killing blow; both
routes terminate at the ONE damage site (`enemy_runner.damage()`). The death `snap["hp"]<=0`
sub-case (never observed alive) renders nothing — honest. Files: `fx_director.gd`,
`world_text.gd` NEW, test.

**G7 — third-person hero identity at the shipped D=64 rig (gap row 10, P1, camera-locked cut).**
NO camera move (pin #3 SPENT — §3 C-2). Two levers, both visual-only: (a) `sprite_bank` gains
`WORLD_H_HERO` (> WORLD_H_UNIT; heroes-only presentation const — capsules, pos, and every sim
read untouched; enemies unchanged), so the hero reads bigger than the 2 u mobs it fights;
(b) name-crest above the ACTIVE pawn: `world_text.make_text(hero name from heroes.json)` + the
hero's own sheet as a small crest child, parented in `hero_pawn.setup_pawn` — the pawn visibility
swap (`hero_controller.gd:65-74`) already moves children with the active hero, so the crest
follows F1-F3 for free. REPLACES: nothing (no hero marker exists); crest is ours-authored text
over committed sheets — zero new art. Files: `sprite_bank.gd`, `hero_pawn.gd`, test.

**G8 — first-session coach banner (gap row 11, P1).** One scripted first-mission coach over the
SHIPPED banner: a LOCAL display var (zero mission writes — I4 and the test_hud.py source-truth
gate intact) carries the timed line: build wave 0 → "BUILD: tower buttons on the right panel —
click arms, click again places"; combat wave 0 → "FIGHT: both mouse buttons hit, F1-F3 swap
heroes"; build wave 1 → "NEXT WAVE: watch the gate billboards". Copy strings are strings
(I2-safe). **Boot-order fix (Rev 2 / DA A2):** the wave-0 build edge fires at
`$PhaseController.setup` → `_enter_build(0)` → `emit("build")` (`mission.gd:153`,
`phase_controller.gd:46,:74`) BEFORE the HUD exists (`mission.gd:168-171`) — a connect made in
`hud.setup` can never see it (Godot drops no-listener emissions). So `hud.setup` BOOTSTRAPS the
coach var from the public reads (`m.phase_kind` + `m.wave` == "build"/0 → line one — a read +
local assign; the test_hud.py MUT_RE `:46` / WRITE_RE `:49-51` trip neither, DA re-verified) and
the `$../PhaseController.phase_changed` connect carries only the LATER edges (`:82` combat, `:74`
build from `_finish_wave`). `banner_text()` priority becomes outcome > coach > "" (outcome NEVER
overridden); `banner_shown()` read-back unchanged. REPLACES: nothing; the outcome banner keeps
its exact behavior. Files: `hud.gd` (328 → ~360, room), test.

## 2 DEFER rows (explicit, reasoned — not silent scope)

- **D1 — player zoom / camera modes (gap row 10 second half):** LOCKED pin #3 re-pin is SPENT
  (v1.2 F6 moved it once under the owner grant, LEDGER F6 row). Camera numbers are immovable in
  this wave without a NEW owner grant; G7 answers identity at the shipped rig. Needs owner
  decision + design pass, not a card.
- **D2 — protected-zone shimmer at the spawn mouth (DD-REFERENCE §2):** needs authored shader
  material + the same design pass the row-2 "NEEDS v1.2.1 design pass" cell names. The eye
  billboard (G1) is the shipped cue for v1.2.1.
- **D3 — lanes painted INTO the ground texture:** explicitly rejected by the V1 honest cut
  (authoring a second visual mechanism beside G2's band); revisit only if the band reads poorly
  served-browser. G2's band IS the v1.2.1 treatment.
- **D4 — gap rows 6,8,9,12-13 (selection ring on placed tower — partial in G4's selected-range
  leg, tower hp tint, icon grey/red/cd states, ready-up, minimap):** P2/P4 backlog, unchanged.

## 3 Constraint rows (binding on every card)

- **C-1 400-LOC HARD ceiling (gate metric = `split("\n")`):** measured now: `mission.gd` **400 =
  at ceiling — cards may ADD ZERO LINES** (all mounts ride mission.tscn scene children or
  mission_world's build hook — precedents named above); `defense_panel.gd` 399 (one-line
  headroom → G5 REQUIRES the SPLIT first: extract the defense-rows UI (`:133-208,:297-322`
  region) to `defense_rows_ui.gd` sibling IN THE SAME COMMIT as its first growing edit, and add
  the sibling to `GOVERNED_LITERALS` `tools/check_hygiene.py:78-84` in that commit — pin #10,
  precedent V12 W3/F4 note "fallback split adds the sibling to GOVERNED_LITERALS in-commit").
  **S shape DECLARED (Rev 2 / DA A3): FULL MOVE, not a wrapper-shim** — rows-UI bodies move
  byte-identical to the sibling and the coupled test is retargeted IN THE SAME COMMIT:
  `tests/test_mission_stale.py` pins the mechanism by name in defense_panel.gd SOURCE at `:300`
  (the `refresh()` body must contain `_rows_dirty()` + `_rebuild_defense_rows()`) and calls
  `_p()._rebuild_defense_rows()` ON THE PANEL NODE at `:149`; both retarget to
  `defense_rows_ui.gd`/the sibling (gate follows the mechanism — pinned dead wrappers are a
  refusal). `tests/test_mission_stale.py` is named in the S card's same-commit file list.
  `game_state.gd` 396 — NO card touches it; `main.gd` 245, `hud.gd` 328, `defense_placer.gd`
  228, `fx_director.gd` 217, `mission_world.gd` 120 — all have room; every NEW file stays ≤250.
- **C-2 LOCKED pins, FINDINGS §5 (clean-code run, `.audits/20261028-0758-clean-code/FINDINGS.md`
  §5, 11 items):** touched NONE as written. Pin #3 (camera regex `test_hub_layout.py:337-341` +
  planted literal `:398-403`): re-pin SPENT (one move, v1.2, LEDGER-declared) — no card edits
  mission.tscn CameraRig. Pin #4 lighting rows / pin #1 ext-rows: mission.tscn edits APPEND a
  new ext_resource + node only (fx_director did exactly this), never reorder/re-pin. Pin #11
  MISSION_SCENE path literal: no scene moves. Pin #10: split → set update same commit (§3 C-1).
- **C-3 Sim determinism / golden fixtures:** readability fx are READ-ONLY observers or visual
  mounts; no writes to mission/enemy_runner/defense_obj/phase_controller state; every card's
  gate includes `git diff --stat tests/fixtures/` EMPTY; suite ≥239 green (239 = measured today).
- **C-4 I2 governed-literals:** hud.gd, defense_panel.gd, defense_placer.gd (+ new sibling) carry
  ZERO number literals — presentation numbers live in the new ungoverned files
  (`lane_bands.gd`, `world_text.gd`, `placement_readout.gd`, sprite_bank consts), ranges/rng
  values read from towers.json/hero rows (the shipped statics; `check_hygiene.py` must go GREEN
  on the new set, and the SPLIT card must plant one RED first — planted-red rule, §5).
- **C-5 I4 (hud write-free):** G8's coach state is LOCAL display state; the test_hud.py
  zero-mutator/zero-write source-truth gate stays green, unchanged.
- **C-6 Verification per shipped feature (orchestrator legs, MC 11509 D3):** web served-browser
  (Playwright dogfood on server/ + static/ export) + describe-image read-back per feature, plus
  the owner-facing before/after pair at release (§6). Engine legs per conftest.run_probe_script
  idiom; every card ships its own planted-red transcript (fleet gate rule: a check that never
  went red is not a check).
- **C-7 LEDGER row in-commit; attribution `plan (MC 11680)`-per-card style per fleet trail;
  commit bodies complete (no heredoc truncation).**

## 4 WAVES (each card = one concern = one child; files DISJOINT inside a wave; dependencies
declared, never inferred; per-card log `.audits/20261029-2100-v121-plan/G<n>-wave.log` ending
`VERIFY_EXIT=0`, planted-red transcript beside the green one)

| wave | cards (∥ = parallel, → = sequential-after) | shared-file reason for sequencing |
|---|---|---|
| **W1** | **G1 ∥ G6 ∥ G8** | disjoint: mission_world+sprite_bank+art • fx_director+world_text • hud |
| **W2** | **G2 ∥ G7 ∥ G3** | disjoint: mission_world(+lane_bands NEW) • hero_pawn+sprite_bank • mission.tscn+wave_telegraph NEW; G3+G7 depend on G6 (world_text); G2 depends on G1 (same file, done) |
| **W3** | **S → G5 → G4** | all touch defense_panel/placer/readout; S = zero-behavior split first |
| **W4** | **R (release tail, §5)** | after all feature commits land |

Lane pre-flight (`lane-load.sh <n>`) before each parallel wave per fleet doctrine; children are
leaves (never spawn).

**Per-card DoD (checkable; full list on each child card — the load-bearing legs):**

- **G1:** engine probe: 3 spawner markers exist at map positions, winged exactly on spawn_a/b
  (negative leg: spawn_c has NO winged child); fixtures diff empty; hygiene 0; suite ≥240;
  planted-red: winged-branch inverted → winged leg RED; served-browser + describe-image
  ("three gate markers visible at lane mouths, two read winged").
- **G2:** one band node per ground lane, ZERO on air lanes (negative leg); slot list +
  test_lane_order byte-green (band is visual-only); planted-red: lane-kind filter inverted →
  air-band leg RED; describe-image: "lit path from each gate to cores readable at a glance".
- **G3:** telegraph present for EVERY spawner of the upcoming wave DURING build (pre-first-spawn
  leg: observer state read at build, before any `EnemyRunner.spawn`), counts == waves-file
  sums per lane (data leg re-derives, no literals), CLEARED on combat (exactly-once transition
  leg); source-truth leg: zero writes to `m` (mutator grep, fx doctrine); planted-red: wave-index
  off-by-one → count leg RED; mission.tscn pin rows byte-unchanged (`git diff` shows append only).
- **G4:** ring radius == towers.json tier range (data leg); ring HIDDEN with no ghost/selection
  (negative leg); **range≤0 rows (the five gate_blockade tier rows) render NO ring — declared
  treatment + negative leg (Rev 2/DA A4.1: without it the "hidden" leg is vacuous for those
  families)**; planted-red: tier index swap → radius leg RED.
- **G5:** S card (FULL MOVE per §3 C-1): split lands + GOVERNED_LITERALS updated +
  `tests/test_mission_stale.py` retargeted (`:300` source-grep → defense_rows_ui.gd; `:149` probe
  → sibling) in the same commit + full suite byte-green with ZERO behavior change (239 unchanged
  legs; the retargeted legs test the SAME mechanism at its new home) + hygiene gate RED with the
  sibling absent from the set (planted-red, then green). G5 card: button press = arm (placement did NOT happen — negative
  leg asserting defense_list count unchanged), cycle moves the ghost index (leg over
  `placer.buildable()`), MouseLeft places ONCE via the ONE `m.place_defense` site (contract:
  grep `m.place_defense(` count == 1 stays), MouseRight cancels (no place); KeyM-when-armed
  places; legacy explicit-slot callers unaffected (test_mission_clicks/test_family_picker
  updated to the arm→confirm flow, same commit); banner of W17f first-free behavior retired
  in docs (replace-not-delete: LEDGER + ARCHITECTURE rows rewritten same commit).
- **G6:** non-lethal number text == the hp drop the observer saw == what `runner.damage()`
  applied (the ONE-site contract leg); **KILLING-BLOW leg (Rev 2): kill via one oversized hit —
  assert the FINAL number == snap["hp"] at erase (declared lower-bound semantics) for BOTH a
  hero hit and a tower hit; negative leg: a breacher arrival (reached, hp>0) renders NO final
  number**; one number per drop event (counter leg); live fx ≤ 64 cap leg (numbers counted);
  planted-red ×2: format-amount halved → value leg RED; final-number branch removed → the
  killing-blow leg RED (it fails LOUD, not silent — that is the point of this row); fixtures empty.
- **G7:** crest child exists on each pawn and follows the F1→F3 swap (visibility leg through the
  shipped `_sync_pawns` path, untouched); crest text == heroes.json name (data leg); enemy sheet
  heights byte-unchanged (negative leg); v11 sprite probes green; fixtures empty (visual const,
  not sim state); describe-image: "hero reads clearly bigger than the mobs".
- **G8:** **BOOT leg (Rev 2/DA A2): real mission booted under -s through `mission.setup` with the
  HUD mounted in PRODUCTION order (after `$PhaseController.setup`) — the wave-0 build line is
  VISIBLE (bootstrap path, not the missed signal)**; coach line switches at the combat edge,
  wave-1 build line once, nothing on waves ≥ 2 (phase-transition-driven legs); outcome WINS
  priority (win during wave-0 combat → VICTORY not coach — negative leg); test_hud.py
  unchanged-green (I4 gate); `phase_changed` connect is the ONLY new signal wiring (source-truth
  leg); planted-red: coach-beats-outcome inversion → priority leg RED; planted-red ×2 (DA A2
  class): bootstrap removed + leg run in production order → BOOT leg RED.

Suite floor rises as legs land; each card's bar = full suite green at ITS tree (≥ the count its
parent tip had + its own legs), hygiene 0, `VERIFY_EXIT=0` in its log.

## 5 Release tail (W4 · card R)

- Full-suite gate + hygiene 0 + fixtures byte-pinned at the final tree (re-run, not inferred).
- README + RELEASE_NOTES rows per the GitHub-Release doctrine (what shipped + known limits —
  per Rev 2 the notes MUST carry: damage numbers share the `MAX_FX=64` cap and can be starved on
  busy waves (DA A5), and the killing-blow final number is the declared LOWER-BOUND read
  (hp at last observation; overkill unobservable — DA A1) — plus the honest non-shipped line:
  D1 zoom, D2 shimmer — promised-class, not shipped); doc-sweep grep-to-zero for retired claims
  (the W17f "falls to first free slot" copy is G5's row, re-checked here); LEDGER rows present
  per feature.
- Tag `v1.2.1` + GitHub Release (release-notes body committed at the tag). Tags v1.1 `fd5cd53`
  and v1.2 `c95798b` NEVER move. VM120 native run leg at the new tag (Windows export recipe,
  MC 11658 precedent) — orchestrator leg.
- **Owner-facing before/after screenshot pair** (served browser + describe-image): same mission
  state, v1.2 baseline vs v1.2.1 — gates, bands, ghost/ring, hero crest, coach line readable in
  the AFTER frame; the pair rides the release evidence file.

## 6 Shape of the result

9 feature cards + 1 release card, 4 waves (3-parallel, 3-parallel, 3-sequential, release).
Two original art sheets total (G1 gate-eye pair); everything else reuses shipped mechanisms
(make_sprite, the observer idiom, bridge codes, phase_changed signal, towers.json/map data).
Plan seat authored ZERO repo code; this document is the artifact.
