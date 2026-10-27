# W3a evidence — sim core statics, part A (MC 11274.1.9 / card 11299)

BUILD: commit `f276f2bdb055be21bd25c7eddbca072fb9290ccd` (author `code (11299)`), 12 files,
touching ONLY `godot/sim/` (4 modules + parse harness + the repo-idiom `.gd.uid` artifacts)
and `tests/` (2 new test files). conftest.py NOT extended — ensure_class_cache() + GODOT +
repo_path() already covered the `-s` leg (extend-only-if-needed read: not needed).

## Deliverables

- `godot/sim/sim_tables.gd` — `class_name GWTables extends RefCounted`: `load_dir(dir)` at
  ctor (`_init(dir := "res://data")`), typed `Dictionary[String, Dictionary]` store,
  `table(name)`, `map(id)` = `table("maps/"+id)` (F16 real method). Reads the exact pinned
  data set (14 stems incl. maps/gatefall + both wave files) via FileAccess + JSON.
  validate() NOT here (W5, per brief).
- `godot/sim/sim_economy.gd` — `SimEconomy`: add_green/upgrade_cost/repair_cost/sell_value/
  can_afford, C3 wiki formulas, params carry all ratios (I2), green-only (I3).
- `godot/sim/sim_combat.gd` — `SimCombat`: hero_hit/tick_blue/ability_ready/tower_dps/
  dmg_to_core; rolls arrive as parameters (C12), zero draws (I6).
- `godot/sim/sim_wave.gd` — `SimWave`: wave_comp/is_boss/build_seconds/total_waves over C8 rows.
- `godot/sim/sim_parse_probe.gd` — harness (see reading 2), extends SceneTree, prints
  `SIMPARSE-OK <name>` / `SIMPARSE-FAIL` + rc 1 / `SIMPARSE-DONE <count>` rc 0.
- `tests/test_economy_numbers.py` — DATA asserts (ratios [0.5,1.0,1.5,2.0]; 50/100/150/200 on
  base 100; repair/sell 0.75; per-tower ladders from towers.json base_costs) + source-truth
  regexes (repair multiplies base_cost*ratio*missing_ratio with roundi + maxi-floor-1 while
  missing>0; sell multiplies total_spent*ratio*missing_ratio; add_green clamps cap; hero_hit
  branches `if roll < crit_chance` + `dmg * crit_mult`; I3: "blue" absent from economy CODE).
- `tests/test_purity.py` — (a) per sim/*.gd bans `extends Node` / `\bEngine\b` / `get_node` /
  BARE randf(/randi( (reuses check_hygiene.BARE_RAND_RE + blank_code — one mechanism);
  (b) parse leg: ensure_class_cache then `--headless --path godot/ -s
  res://sim/sim_parse_probe.gd`, OK-count == module count (sim_*.gd minus harness),
  SIMPARSE-DONE carries the count, no FAIL row, rc 0, never vacuous (>= 4).

## Ambiguity readings taken (binding per SOUL; stated on the deliverable)

1. **Brief signatures vs the PINNED architecture table.** The brief's numbered list
   (load_tables/enemy()/tower()/upgrade_cost_at/green_award/wall_absorb/slow_factor/
   trap_explode/downed_heroes/SimWave.tick…) appears in NO project document — while the
   brief itself says "READ FIRST (binding): docs/ARCHITECTURE.md — the Modules table … =
   EXACT GDScript signatures you must match" and "Implement (signatures verbatim from the
   architecture, no invented extras)". Resolution: the ARCHITECTURE table wins; the brief's
   list is a divergent paraphrase (its own test spec — C3, 50/100/150/200, add_green cap,
   hero_hit crit branch — matches the table, not the paraphrase). C1 additionally pins the
   Tables API to table()+map(), so the 8 accessor fns would have been invented extras.
2. **Probe placement (brief's own reading, applied):** `tests/probe_sim_parse.gd` DROPPED —
   a res:// load cannot reach tests/; architecture places harness scripts in sim/ (hollow_dawn
   sim_headless/save_probe precedent). The harness is `godot/sim/sim_parse_probe.gd` and the
   pytest -s leg references THAT path.
3. **roundi vs brief's "int()":** C3 pins roundi() for repair/sell (min 1 when missing>0) —
   implemented verbatim; the brief's "int() present" read as "integer conversion present"
   (test accepts the roundi form; upgrade_cost truncates via int(), exact on shipped data).
4. **dmg_to_core armor:** v1 data carries no armor field; formula pinned as fraction
   mitigation clamped ≥ 0 (wiki Stats: armor reduces damage by %) for W7 callers.

## Verification (this session, real runs)

Green (full suite, 67 prior + 19 new):

    ..............                                                           [100%]
    86 passed in 1.30s
    PYTEST_RC=0

Planted-red proof (temp rename `static func repair_cost(` -> `repair_cost_RENAMED(` in
godot/sim/sim_economy.gd; source-truth test goes RED):

    =========================== short test summary info ============================
    FAILED tests/test_economy_numbers.py::test_repair_cost_multiplies_all_three_and_floors_at_one
    1 failed, 11 passed in 0.08s
    PYTEST_RED_RC=1

Restore + green again:

    static func repair_cost(base_cost: int, missing_ratio: float, ratio: float) -> int:   (grep, line 22)
    ..............                                                           [100%]
    86 passed in 1.23s
    PYTEST_RC=0

Parse probe direct run (before commit):

    SIMPARSE-OK sim_combat
    SIMPARSE-OK sim_economy
    SIMPARSE-OK sim_tables
    SIMPARSE-OK sim_wave
    SIMPARSE-DONE 4
    PROBE_RC=0

Scratch functional check (temp file, removed before commit — not a committed asset):
upgrade base100 -> [50, 100, 150, 200]; base160 t2 -> 240; repair full 100/1.0 -> 75,
0.01 -> 1 (floor), zero -> 0; sell 300/0.5 -> 113 (roundi of 112.5); add_green 9990+50 cap
10000 -> 10000; hero_hit crit {damage 20.0, crit true}; GWTables loads all 14 stems, map
id=gatefall, waves=11 rows, is_boss idx10 true / idx0 false.

Hygiene: `python3 tools/check_hygiene.py` -> `check_hygiene: 0 hit(s)` (rc 0). File sizes:
sim .gd 30–43 lines, tests 97/150 lines — all under ceilings.

Commit sha: f276f2bdb055be21bd25c7eddbca072fb9290ccd

VERIFY_EXIT=0
