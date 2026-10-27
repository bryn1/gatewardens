# W3b evidence — sim core statics part B (MC 11274.1.10 / card 11300)

**BUILD commit:** `de3b04491d5266788e25a08d71f587e1745dd716` — author `code (11300) <code@agent-town.local>`,
touches ONLY `godot/sim/` (sim_progression.gd, sim_loot.gd, sim_inventory.gd + the repo-idiom
`.gd.uid` artifacts) and `tests/` (test_loot_structure.py, test_heroes.py). 8 files, 845 insertions.

## What landed (pinned ARCHITECTURE Modules table, signatures verbatim)

- `godot/sim/sim_progression.gd` — SimProgression: `level_from_xp(curve,xp)->int`,
  `xp_need(curve,level)->int`, `asc_points(levels_total,per_level)->int`,
  `asc_modifier(tree,spent)->Dictionary` (per-node spend clamp at the declared `max`).
- `godot/sim/sim_loot.gd` — SimLoot: `roll_rarity(tables,diff,luck,rng)->String`,
  `roll_item(base,rarity,tables,rng)->Dictionary` (one return literal = EXACTLY the 12 C9
  keys), `enemy_drops(row,tables,rng)->Array` (`{kind:"item"}` gear row + chance-gated
  `{kind:"material","id"}` F2-6 row), `victory_chest(tier,tables,rng)->Array`. All draws are
  receiver-qualified `rng.randf()`/`rng.randi()` on the passed parameter ONLY (C12/F2-1);
  no rarity name and no weight number exists in the file (source-truth gates).
- `godot/sim/sim_inventory.gd` — SimInventory: `equip(bank,hero,item)->{ok,bank}` (F2-11 —
  see reading 3), `svc_upgrade(item,tables,mats)` / `svc_evolve(item,tables,mats)` /
  `svc_reroll(item,rng,tables)` / `tinkering(source,target,mod_i,tables,mats)` all
  `{ok,cost:{gold,materials}}` with every cost a blacksmith.json read, `mod_slots(rarity,
  ladder)->int`, `relic_bonuses(item)->Dictionary` (C11 primary+secondary legs).
- I1 structural guard: the rolled/service key sets (C9 + stat/value/mod_id/kind/item/id/ok/
  bank/cost/gold/materials) are tripwire-checked against the hygiene gate's OWN token list in
  `test_no_banned_i1_token_in_any_rolled_or_cost_key`, plus the loot data files' field names.
  No paid/clock/timer field exists in ANY rolled dict — the schema IS the defense.

## Readings (ambiguities, stated per stop-condition)

1. **Brief's divergent names superseded** (brief's own "READ FIRST (binding)" clause; same
   reading W3a recorded): `xp_for_level/allocate_stat/asc_point_gain/asc_unlock_ok/asc_spend/
   gear_power` -> the pinned progression table; `roll_stats/roll_weapon_extras/roll_drop` ->
   the pinned loot table (`roll_rarity/roll_item/enemy_drops`, the latter F2-6's material-row
   named finding). Brief rows mapped: "allocate_stat caps respected" = asc_modifier's
   per-node `max` clamp; "gear_power shape" = the C9 rolled shape (pinned in
   test_loot_structure). test_heroes greps the brief names ABSENT from the .gd.
2. **"pytest builds an rng stub" adapted** (brief's own NOTE): pytest cannot execute GDScript,
   so the shape check IS source-truth — regex over the return-literals' key sets + data files
   carry the weights/ladders; behavior equality lands in the W11 goldens (the scripted-rng
   stub belongs to the -s golden harness).
3. **equip() mechanism (F2-11)**: returns `{ok, bank}`; the returned bank = passed array minus
   only the worn row, so whatever the caller merged in (the replaced item, merged by
   GWGameState.equip per C9's caller side, W5+) returns INSIDE this call — replace-to-bank
   lives in equip's contract, no UI reimplements it. `slot=="relic"` -> ok:false (C11 relic
   rows are tower gear, never hero-worn). Documented in the .gd header.
4. **Curve semantics** (nowhere pinned): `hero_curve[i]` = cumulative xp that reaches level
   i+2; level caps at the curve SIZE (A2's cap 50 = the shipped 50-entry curve; no 50 literal
   in code, gated by `test_no_level_or_curve_numbers_are_hardcoded_in_progression`);
   `xp_need` is the exact index inverse. Documented in the .gd header.
5. **Rolled stat value = ilvl**: items.json declares roll_ranges for atk_speed/proj_count only;
   the sole declared number a primary/secondary value can ride is the rolled item level
   (level_band roll). Balance can widen this via a later data revision.
6. **enemy_drops gear leg is ungated by design**: inventing a drop rate would be an
   undeclared number ("declared weights only" + A5 "direct enemy drops"); the chance-gated
   leg is the material row (declared `chance`). luck param = ladder-index bias (luck 0 =
   declared weights verbatim); uid 0 = bank_add stamps identity (C6).
7. **Cross-sim dep binds via `preload`, not class_name** — VERIFIED this gate: a fresh
   `--headless --import` (conftest's ensure_class_cache command) does NOT build the global
   class cache (only an editor scan does; reproduced: fresh import leaves SimLoot
   unresolvable and the sim_inventory load fails at parse). `preload` is compile-time and
   cache-independent. Finding for the orchestrator (not in my scope to fix):
   `sim_parse_probe` reports OK even for a load that failed at parse (Godot returns a
   non-null broken resource) — the real signal is stderr; from a clean checkout the probe
   would have printed `SIMPARSE-OK sim_inventory` red-ish-green without the preload fix.

## Verification (this session, at the commit)

`python3 -m pytest tests/ -q` tail:

    ........................................................................ [ 62%]
    ............................................                             [100%]
    116 passed in 1.61s

116 = prior 86 + 27 new tests (test_loot_structure 17, test_heroes 10) + 3 extra
test_purity params (its per-sim-file parametrize now covers the 3 new modules).
Parse-probe leg (test_purity, 10 passed) now reports all 7 sim files, dynamic as required:

    SIMPARSE-OK sim_combat
    SIMPARSE-OK sim_economy
    SIMPARSE-OK sim_inventory
    SIMPARSE-OK sim_loot
    SIMPARSE-OK sim_progression
    SIMPARSE-OK sim_tables
    SIMPARSE-OK sim_wave
    SIMPARSE-DONE 7   (rc 0, stderr 0 bytes)

`python3 tools/check_hygiene.py`:

    check_hygiene: 0 hit(s)

File sizes: sim_progression 60 / sim_loot 128 / sim_inventory 159 lines (soft 250);
tests 324 / 171 (ceiling 600).

## Planted-red proof (one, per A9 / verify-discipline)

`"upgraded": 0,` deleted from `roll_item`'s return literal -> gate goes RED:

    ___________ test_roll_item_return_literal_is_exactly_the_c9_key_set ____________
        sets = return_key_sets(LOOT_RAW, "roll_item")
        assert len(sets) == 1, "roll_item must have one return literal"
    >       assert sets[0] == C9_KEYS, "rolled item keys != C9: %r" % (
    FAILED tests/test_loot_structure.py::test_roll_item_return_literal_is_exactly_the_c9_key_set
    1 failed in 0.09s

Restored -> full suite green again (116 passed, 1.62s) and the committed tree carries
`"upgraded": 0,` (sim_loot.gd:90). The test cannot stay green while the schema shrinks.

Commit sha: de3b04491d5266788e25a08d71f587e1745dd716

VERIFY_EXIT=0
