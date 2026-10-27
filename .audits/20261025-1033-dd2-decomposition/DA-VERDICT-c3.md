# DA-VERDICT-c3 — T7 gate round 3 (FINAL, capped) over DESIGN-draft-c3.md (MC 11274.1.6 / card 11291)

Fresh devils-advocate (third reviewer of this line), 2026-10-25. Reads: DESIGN-draft-c3.md (target),
DA-VERDICT-c2.md (F2-1..F2-12 + F8 residue), LEDGER.md §c3 rulings (13 bindings — applied mechanically,
not relitigated here), DESIGN-draft-c2.md (regression base), DD2-MECHANICS.md.
Empirics re-run THIS session on the pinned binary `Godot_v4.7.2-stable_linux.x86_64`:
`.tmp/shell_test` BOTH legs (full shell → `out_full_r3/index.html` 5438 B with `new Engine` +
`<canvas id="canvas">`; head-JS-only shell → `out_noph_r3/index.html` 125 B, 0 bootstrap hits — the
F2-3 trap still fires silently with exit 0, and the new asserts catch it); `.tmp/rng_test` twice
(Seed 12345 → byte-identical `rng.randf()/randi()` output across runs); `.tmp/autoload_test` (compile-fail
`Identifier not found: Data` still reproduces — R3's base intact). NEW probe `.tmp/compose_test/`:
GWCompose-shaped `class_name … extends RefCounted` static factory constructing two RefCounted objects
and connecting `state.mutated` → lambda → `save.write(state.to_save())`, run under `-s` after
`--import` (the F14 conftest shape): `ACK=2 GOLD=8 LASTSAVED={ "gold": 8, ...}` — signal-on-RefCounted
wiring, static factory, class_name resolution under `-s`, and at-emit (not bind-time) `to_save()` values
all PROVEN; only RefCounted-leak noise at exit (harmless probe artifact).
Template fact-check: extracted `godot.html` from `~/.local/share/godot/export_templates/4.7.2.stable/`
— 5088 B (exactly the claimed `shell_full.html` size), containing EXACTLY the 8 tokens c3 lists
($GODOT_PROJECT_NAME, $GODOT_SPLASH, $GODOT_SPLASH_CLASSES, $GODOT_SPLASH_COLOR, $GODOT_HEAD_INCLUDE,
$GODOT_URL, $GODOT_CONFIG, $GODOT_THREADS_ENABLED) + `new Engine` + `<canvas id="canvas">`, and ZERO of
the I1 banned tokens (the copied shell cannot self-trip the tripwire; engine bundles were checked clean
in round 2).

## r2 findings closure

1. **F8 (residue)** — CLOSED. C4: "**Cooldown tick scope (F2-8/F8, binding): step (2) decrements ONLY `hero_state[active_hero].cooldowns[i] -= delta`; inactive AND downed heroes' cooldown arrays are FROZEN — they neither tick nor reset, and survive every swap with their remaining time unchanged.**" + C12 step (2) "(ONLY the active hero's cooldowns tick — C4/F2-8)" + hero_combat row "ticks ONLY for the ACTIVE hero, inactive/downed arrays frozen". Contract text, not the ledger.
2. **F2-1** — CLOSED. C12 Draw rule: "every roll flows through the injected `RandomNumberGenerator` parameter via `rng.randf()`/`rng.randi()` …; BARE `randf()`/`randi()` (no receiver) = 0 hits in godot/sim/ + godot/scripts/ (check_hygiene + test_purity)"; check_hygiene row: "**BARE** `randf(`/`randi(` (call sites not preceded by `.`) = 0 hits … receiver-qualified `rng.randf(`/`rng.randi(` is the REQUIRED sanctioned path and is NOT a hit"; same receiver definition in test_purity row and I6; sim_loot row: "draws via `rng.randf()`/`rng.randi()` ONLY (F2-1)". Rejected table carries the c2 substring-ban rejection.
3. **F2-2** — CLOSED. C12 fixture encoding: "LINE 1 (header): `{\"schema\":int,\"seed\":int,\"map\":String,\"difficulty\":String}`; the remaining lines are … SCRIPTED-INPUT rows `{\"kind\":\"in\",\"tick\":int,\"act\":\"input|place|upgrade|repair|sell|assign|unassign|hotswap\",\"args\":{…}}` … and EXPECTED-OUTPUT rows `{\"kind\":\"out\",\"tick\":int,\"ev\":String,…,\"checks\":{…},\"ok\":true}`" (+ `--regen` rule); RNG ownership: main.gd row "owns the app RNG … `RandomNumberGenerator.new()` seeded from OS entropy at `_ready` — SOLE RNG owner at runtime" + hub/blacksmith/tinkerer rows take rng setup params; chest trigger: C12 step (6) "fires the victory-chest roll … BEFORE any C13 mission-end commit" mirrored in loot_pickup row and C13. Probe re-run proves the seeded draw path deterministic.
4. **F2-3** — CLOSED. Placement plan: "GW's shell IS the engine's default 4.7 web template page with GW JS inlined" + full token list + "`<canvas id=\"canvas\">` and `const engine = new Engine(GODOT_CONFIG);`"; test_bridge_contract row adds "**web_shell.html contains `$GODOT_URL` + `$GODOT_CONFIG` + `new Engine` + `<canvas`**" and test_served adds "served index.html contains `new Engine` and `<canvas`"; rejected table bans the head-JS-only stub. EMPIRICAL this round: template = 5088 B with exactly the c3 token set; full export 5438 B live; dead-shell leg stays a silent 125 B — and would now fail BOTH new asserts.
5. **F2-4** — CLOSED. I1 on its face: "**this grep is a TRIPWIRE over a NAMED-TOKEN LIST, NOT a closure of the concept** … ANY field added to or renamed in C5/C6/C8/C9 requires a design-review row in a new c-revision first" + "`egg` is deliberately NOT banned … the tripwire is never quietly disabled to pass a legitimate feature"; deferral list repeats "`egg` stays a legal word".
6. **F2-5** — CLOSED. sim/gw_compose.gd row: "`static func build_graph(tables:GWTables)->Dictionary` → `{state:GWGameState, save:GWSaveStore, bridge:GWBridge}` … Called by main.gd `_ready` AND by every `-s` probe (sim_headless, save_probe, validate_probe) — nothing else constructs/wires the trio"; C1 "the core trio is constructed ONLY inside `GWCompose.build_graph`"; main.gd row wires nothing itself; I6 "every `-s` probe wires the core trio through `GWCompose.build_graph`"; C13 listener "wired inside GWCompose.build_graph". Mechanism PROVEN by the new compose probe (signal-on-RefCounted legal; sim/ purity grep unaffected — zero Node refs; at-emit `to_save()` value correct).
7. **F2-6** — CLOSED. game_state row: meta gains "**materials:{id:int}**" + `add_material(id,n)`/`consume_material(id,n)->bool` ("false when short; no partial spend"); C6 `[meta2]` gains `materials_json:String`; C13 trigger list names both mutators; blacksmith.json row declares `materials:[{id,name}]` + service costs `{gold…, materials:{…}}`; enemies.json gains optional `material_drop:{id,chance}` rolled via `rng.randf()`; sim_loot.enemy_drops emits `{kind:"material",id}`; loot_pickup routes to `GameState.add_material`; svc_* take `mats:Dictionary` and return `{ok,cost:{gold,materials}}`; test_data_schemas checks declared-id closure; I5 byte-equal now names materials_json; test_persistence gains the round-trip row. Deferral list honestly scopes chest-material to post-v1 data.
8. **F2-7** — CLOSED. C5: "`relics_assigned:int` … NEW (F2-7) = count of currently assigned mission relics; the journey asserts +1 after `assign_relic` and −1 after `unassign_relic`"; C11 "the COUNT is observable via C5 `relics_assigned`"; defense_panel row and the served-journey breakdown row both assert ±1.
9. **F2-8** — CLOSED. Same C4 verbatim rule as F8 row 1 (one rule, both ids), and C12 step (2) names the tick site.
10. **F2-9** — CLOSED. C4: "**step (5) evaluates win FIRST, then lose; a lose condition true on the same tick OVERWRITES a win already recorded — LOSE wins.**" + C12 step (5) "(win evaluated FIRST, lose checked after and OVERWRITES on a same-tick tie, F2-9)". Matches the LEDGER ruling wording.
11. **F2-10** — CLOSED. C4: "**next healthy = deck ARRAY order starting immediately AFTER the fallen hero, wrapping around at most once (F2-10); found-none → the all-down lose path fires in step (5)**".
12. **F2-11** — CLOSED. sim_inventory row: "`equip(bank,hero,item)->Dictionary` returning `{ok:bool, bank:Array}` — the replaced item, if any, is ALWAYS returned into the returned bank BY equip (F2-11 contract, not UI)"; C9 "**every caller (gear panel, future auto-equip) gets the same replace semantics; no caller may reimplement it**"; game_state.equip delegates; gear_panel_ui row: "replace-return is NOT panel logic".
13. **F2-12** — CLOSED. item_row row: "`scenes/item_row.tscn` … `show_item(item,selected)`, emits `picked(uid)`; instantiated by BOTH gear_panel_ui (bank list) and defense_panel (relic picker)"; both panel rows consume it; Hygiene section: "Re-checked after F2-12/F2-5: item_row.gd ≈ 80 lines; gear_panel_ui keeps section + slot logic only … fits soft ceiling … gw_compose.gd ≈ 40 lines"; scenes list and breakdown include the scene; rejected table bans per-panel rows.

## Regression hunt at touch-points

- **GWCompose in sim/ vs I6 purity grep** — no refutation found: the factory's only cross-layer refs are
  three RefCounted class_names; grep terms (`extends Node`/`get_node`/`Engine.get_singleton`/bare rand) appear
  nowhere in the mechanism, and the compose probe ran clean under `-s`; signals on RefCounted are legal engine
  behavior (proven: ACK=2).
- **Fixture rows vs sim_headless row** — no refutation found: C12 says "in-rows … out-rows … every line is one
  of the three kinds"; sim_headless says "replays fixture `kind:\"in\"` rows at their ticks"; test_sim_golden says
  "emitted out-rows byte-equal to the committed expected rows, every `ok:true`" — same names, same directions,
  regen-only rule in both.
- **Full-template shell vs export-preset/C10 rows** — no refutation found: preset row keeps
  `custom_html_shell="res://web_shell.html"` + `head_include` EMPTY; the template's `$GODOT_HEAD_INCLUDE` stays
  (fills empty); I8 keeps the cfg+rename grep and explicitly moves the bootstrap asserts to
  test_bridge_contract/test_served — no key contradiction; I1 scan of the template text = 0 hits, so the copied
  shell cannot self-trip.
- **Materials leg vs I5 byte-equal save_probe** — no refutation found: I5 now reads "byte-equal meta dict **incl.
  materials_json** (save_probe golden)"; save_probe "runs mutators (incl. add_material)"; JSON round-trip
  preserves key order so a fresh-process re-stringify is stable (Dictionary insertion order = save order = reload
  order).
- **Bare-vs-receiver rule wording, check_hygiene vs test_purity** — consistent: both define BARE as a call site
  whose preceding char is not `.`; a literal-text implementation of the stated rule classifies
  `rng.randf()`→0, `randf()`→1, `randf_range(`/`randi_range(`→0, `my_rng.randf()`→0 (micro-test this session,
  ALL-MATCH). Caveats recorded in Build notes.
- **C5 relics_assigned vs the journey row** — no refutation found: both say ±1 on assign/unassign; C11 keeps the
  pool mission-local (no C6 leak) so the only save-observable is the count — matching the field added.
- **equip {ok,bank} vs every caller row** — no refutation found: all callers enumerated (gear panel via
  GameState.equip; C9 bans reimplementation for "future auto-equip"; loot uses bank_add, not equip).
- **item_row vs the 250-line ceilings claim** — no refutation found: the ceiling story is now stated per file
  (item_row ≈ 80, panels keep only section/selection logic) and is mechanically enforced by test_hygiene; if a
  panel still overflows, the gate goes red — an author-visible check, not a spec hole.
- **Chest-before-commit vs C13 trigger list** — no refutation found: C12 (6) and C13 both state bank_add BEFORE
  the mission-end commit; each bank_add bumps `mutated`→write (extra ack increments), and the Playwright rule is
  "ack EXCEEDS pre-action value", tolerant of write count — no order ambiguity, no ack race.
- **F2-6 ruling "gold+materials" vs `reroll:{gold:int}`** — no refutation found: blacksmith.json is the SOLE cost
  source and DD2-MECHANICS §7 (re-read this session) pins materials on Evolve/Advancing (+ upgrade), with the
  reroll row a separate stat-reroll cost; the builder implements the file, so the ruling's summary prose cannot
  diverge from the schema.
- **c3 rulings vs LEDGER §c3 rulings text** — all 13 rulings located in contract/module/test text quoted above;
  no row found that exists only in the `## Fix ledger r2` table (the F8/F2-8 double-id is one rule stated twice,
  in-text both times).
- **11-wave + A3 prose sweep (scope 3)** — clean: identical "waves array has 11 entries: index 0..9 … + index 10
  kind 'boss'" wording in C8, I4, test_waves (c3 lines 186/203/167); LEDGER A4 "10 waves + boss wave" = 11;
  `total_waves == 11` in sim_wave. A3: LEDGER corrected line (repair = base×0.75×missing, sell =
  total-spent×0.75×missing) matches C3, sim_economy, economy.json (repair_ratio/sell_ratio 0.75) and
  test_economy_numbers; the R1 header restates it. No surviving contradiction at either sweep site.

## Build notes

Carried into the build phase (gated by the number-test suite; none blocks a competent builder):

- BN1 (P3): the stated BARE rule is raw-text — `randf(`/`randi(` inside a comment or string is a hit;
  check_hygiene should strip comments (or the codebase avoid the literal in prose). Round-2 lineage, still unstated.
- BN2 (P3): no gold mutator is named on GWGameState (services/mission-end "write gold through mutators" but the
  list is add_hero_xp/spend_asc/bank_add/equip/add_material/consume_material); a `spend_gold`-shaped mutator is
  forced — the builder names it; C13's "EVERY mutator emits mutated" absorbs it. Pre-existing (c2-era), surfaced by F2-6.
- BN3 (P3): `victory_chest(tier,…)`: the tier source is unnamed (rarity.json `chest_tiers` indexing — presumably
  difficulty); one line at build time decides it.
- BN4 (P3): I5 says fresh-process reload while the save_probe row describes a single-run reload — test_persistence
  should drive the probe twice (mutate-leg, then fresh verify-leg) to satisfy I5 literally.
- BN5 (P3): the down→auto-swap fire point inside a tick is not named (same-tick in the damage handler is the
  natural, deterministic reading; both readings freeze cooldowns identically per C4).
- BN6 (P3): test_purity's "rolls appear … as `rng.randf(`/`rng.randi(` only" is descriptive — a receiver named
  other than `rng` passes the bare-gate text; the sim signatures name `rng` everywhere, so the convention is
  self-enforcing in practice.

## Verdict rationale

All 13 r2 findings are closed IN the contract/module/test text (quotes above, one per line), not in the ledger
rows. Every empirically load-bearing claim re-ran green this session on the pinned binary: the dead-shell trap
(125 B silent) and its new catcher (`new Engine`/`<canvas` asserts match the real exported page, and the template's
token list matches c3's list exactly); seeded receiver-qualified draws are byte-stable; the autoload `-s` repro
stays red, keeping R3's ground honest; and the NEW compose probe proves the F2-5 factory + RefCounted-signal
wiring actually runs under `-s` with at-emit save values — the one c3 mechanism that rested purely on prose.
The touch-point regressions named in the task (I6 purity vs GWCompose, fixture rows vs sim_headless, shell vs
preset/C10/I1, materials vs I5, bare-rand wording across both gates, relics_assigned vs journey, equip callers,
ceiling claim, chest vs C13) all resolved with no refutation, and the 11-wave/A3 prose sweeps are clean across
LEDGER/C3/I4/test wording. What remains is six P3 polish items (Build notes) — no proven trap, no acceptance-
breaking observation gap, and no contract seam where two builders must diverge. Per the round-3 acceptance rule
declared by the orchestrator, minor findings alone do not justify FIX: the builder can implement every module
without inventing a decision.

# VERDICT: SHIP
