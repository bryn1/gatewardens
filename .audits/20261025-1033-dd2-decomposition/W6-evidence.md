# W6 evidence — mission scene core (funnel, phases, lanes, cores, runner)

Card: MC 11274.1.13 / 11308. Commit: `9532f56` (branch main, verified
`git show --stat HEAD`: 22 files, exactly the whitelist: godot/scripts/
{mission,phase_controller,lane_path,core_obj,enemy_runner}.gd (+.uid x5),
godot/scenes/mission.tscn, godot/assets/ x8 .tres, godot/sim/
mission_smoke.gd (+.uid), tests/test_mission_smoke.py). main.gd NOT
touched — W5's router already calls the pinned setup signature and loads
res://scenes/mission.tscn, which now resolves to the real scene. conftest
NOT extended — run_probe_script/class_cache sufficed (declared).
`git -c user.name="code (11308)" -c user.email=code@agent-town.local commit`
(never `git config`).

## Gate 1 — full pytest suite, exit 0

```
$ python3 -m pytest tests/ -q
........................................................................ [ 54%]
...........................................................              [100%]
131 passed in 4.24s
```

127 prior + 4 new (tests/test_mission_smoke.py: funnel-order source truth,
_process one-liner, shipped planted-red matcher, engine smoke leg).

## Gate 2 — hygiene, 0 hits

```
$ python3 tools/check_hygiene.py
check_hygiene: 0 hit(s)   (rc 0; notes only: game_state soft-250 carry-over,
                           sim_loot sanctioned draws — both pre-existing)
```

File sizes: mission.gd 400 (at ceiling, trimmed to fit — readings moved
here), phase_controller.gd 105, enemy_runner.gd 109, lane_path.gd 49,
core_obj.gd 31, mission_smoke.gd 205, test_mission_smoke.py 94.

## Gate 3 — engine smoke transcript (rc 0, EMPTY stderr)

```
$ XDG_DATA_HOME=$(mktemp -d) godot --headless --path godot -s res://sim/mission_smoke.gd
MISSION-SMOKE-SEED deck=["warden","deadeye","embercaller"]
MISSION-SMOKE-SPAWN t=1501 wave=0 alive=1
MISSION-SMOKE-ADVANCE d0=39.92 d1=35.21
MISSION-SMOKE-CORE hp=3750.0 max=5000.0
MISSION-SMOKE-WAVE kills=3 green=346 xp=72 loot=3
MISSION-SMOKE-REFILL blue=100.0 max=100.0
MISSION-SMOKE-SWAP hero=warden
MISSION-SMOKE-LOSE outcome=lose ack=5 seq=5
MISSION-SMOKE-OK
STDERR_BYTES=0
```

Row-by-row: SEED = 3-hero deck written by the set_deck MUTATOR through
the real C13 wiring and read back from user:// BEFORE setup (XDG temp
dir, save_probe idiom). SPAWN = build phase lasted SimWave.build_seconds
(waves[0])=25.0s (tick 1501, +/-1s window) and wave-0's delay-0 group
spawned at combat-local t=0. ADVANCE = ground-lane walk closes on the
main core (lane_path, F16 y untouched). CORE = a breach cut core HP.
WAVE = wave-0 cleared through the pinned "all spawned dead + nothing left
to spawn" path; awards exact: green 300 + 3*2 (skitterling rows) + 40
(economy green.per_wave), xp 3*4 + 60 (xp.wave_xp), loot_pending = 3 gear
drops (SimLoot always fires the item row). REFILL = full blue ONLY at
combat start (= warden base.blue_max 100). SWAP = F3 manual swap to
embercaller, then embercaller down -> F2-10 next-healthy scan from
downed+1 wrapping once -> warden. LOSE = F2-9: win_pending recorded the
same tick the deck went all-down -> outcome=lose (LOSE wins), mission-end
commit fired through the C13 listener with saved_ack == write_seq (5==5)
and warden xp awarded.

Harness-driven state (licensed E5-style driving, like boot_probe's
_ready): hero downs and wave-0 kills go through runner.damage because no
damage source ships before W7/W8; the main core is made 5x sturdier so
the no-defense run cannot die on breaches mid-checks (the stock core
dies at 4 breaches — see reading R4; VERIFIED by instrumented debug run:
outcome=lose froze the mission at f~2350 when buffed x1000 — breach
damage scales WITH core max, so wave 0 was cleared by harness kills).

## Gate 4 — planted-red, both forms

(a) SHIPPED (in the suite, runs every pytest): the same funnel matcher
over an in-memory copy with the (3) defenses / (4) enemies call lines
swapped MUST reject — test_planted_red_funnel_swap_goes_red passes, i.e.
the matcher demonstrably goes RED on a swapped funnel.

(b) LIVE (this session, on the real file, restored immediately):
```
PLANTED: (4) enemies call moved AFTER (5) bookkeeping in step()
$ python3 -m pytest tests/test_mission_smoke.py::test_step_funnel_is_the_six_pinned_calls_in_order -q
tests/test_mission_smoke.py:60: AssertionError
FAILED tests/test_mission_smoke.py::test_step_funnel_is_the_six_pinned_calls_in_order
1 failed in 0.07s
```
Restored via /tmp/mission.gd.bak; full suite green again after restore.
The engine leg additionally goes RED by construction: it asserts EMPTY
stderr (W4/W5 ruling — a broken -s script can still load as a non-null
resource, so stderr is the true parse signal; VERIFIED this wave when a
real bug produced ERROR lines on stderr and the FAIL row caught it).

## Readings (bound the implementation; pinned table wins over brief)

R1 lane_path: binds the PINNED Modules-row static
advance(pos:Vector3,wps:Array[Vector3],speed,dt)->{pos,wp_index,arrived};
the brief's advance(entity,dist) paraphrase is superseded (precedent MC
11274.1.9/.10/.11/.12). Static/stateless; waypoint y (C7 ground 0 / air
flight height) is data the walker NEVER rewrites (F16). Lane unlock on
sub-core destruction via the map's opens_lanes (C7) — opening, not
retargeting: lanes whose target died despawn their breachers there.

R2 SimWave.next_event does not exist (pinned row = 4 statics). Spawn
spacing is built in mission.start_wave: spawn k of a C8 group lands at
row.delay + k * balance.wave_delay. wave_delay read = the per-entity
stagger inside a wave (build_seconds owns time BETWEEN waves; row delay
owns the group start), so a delay-0.0 group's first spawn lands at
combat-local t = 0 — smoke-asserted (t=1501 -> alive=1 at tick 1).

R3 hp_mult: C8 ships no mods field in the data; an OPTIONAL wave-row
mods:{hp_mult} is resolved at schedule build and crosses the pinned
spawn(row,lane,tables,rng) boundary onto the enemy record (identity 0.0
additive when absent). enemy_runner resolves
hp = enemies[id].hp[difficulty] * (1 + hp_mult) — C2: all HP math at the
pinned crossing, none in mission.gd.

R4 respawn_core_ratio (balance, 0.25) read: a breach hits its target
core for ratio x core max HP, mitigated via SimCombat.dmg_to_core (C7
cores carry no armor field -> armor 0.0 identity input). A breach is NOT
a kill: no green/xp/drops (C12 step-(4) rewards are death-only) and the
breacher is consumed at the target. Consequence VERIFIED this wave: any
core falls in exactly 1/ratio = 4 breaches regardless of its HP (damage
scales with max) — lives-style bounded leak pressure, which is what the
brief's reach-leg parenthetical "(respawn_core_ratio rule)" asks for.
Alternatives rejected: build-phase start regen (a heal with no C7 data
source, and it made the core unkillable given wave sizes) and a
respawning-lane loop (a breaching entity that persists has no wave-clear
exit in W6 since nothing kills it before W7).

R5 wave clear = nothing left to spawn AND nothing alive on the lanes.
The pinned "all spawned dead" wording cannot be the sole exit in W6: a
breaching entity is CONSUMED at the target (R4), which removes it exactly
as a death does; with no damage source shipped before W7 this is the only
exit that terminates a wave at all. Stated as a reading, smoke-verified.

R6 commit: the pinned W4 GWGameState row ships no commit() method, so
the mission-end commit calls the ONE C13 listener GWCompose wired
(state.commit_listener.commit()) — same single write path, no second
mechanism. Fired exactly once on the outcome tick, AFTER funnel step (6)
rolled the victory chest (F2-2: chest rows bank through bank_add
mutators BEFORE the commit). Mission-local noise (hp/pos/timers/tray)
never mutates meta; meta writes are end-scoped: add_hero_xp (both
outcomes), bank_add/add_material of the tray + complete_mission (win
only; a loss DROPS the tray — DD2 truth), then commit. saved_ack
mirroring write_seq asserted in the smoke (5==5).

R7 data doors: GWTables.load_dir stores Dictionary-shaped JSON only, so
the array-shaped files heroes/enemies/items/mods are NOT reachable via
table(stem) (main.gd's boot row already relies on this at FILE level).
mission.gd reads them with the same raw FileAccess+JSON door; SimLoot
gets the plain {"rarity","items","mods"} dict it was built for.

R8 funnel table-wins divergences as in precedent: hot-swap input drains
in bookkeeping step (5) (the pinned swap site; F1-F3 + Digit aliases);
step_hero carries hero STATE math only (pawn scenes = W7, stateless
scene pattern, meshes not needed); step_defenses carries the pinned slot
with an empty list until W8; victory chest tier index: normal ->
chest_tiers[0], hard -> chest_tiers[1] (BN3; no tier-selection economy in
v1); deck = C6 deck_json, empty deck falls back to all declared heroes
in heroes.json order (war_table ships later).

R9 engine facts learned this wave (headless -s): (a) global_position
reads/writes on a freshly add_child'd Node3D fire
"!is_inside_tree()" ERRORs under -s — scene code writes mission-local
`position` instead (root at origin; the game runs the same space);
(b) `--headless --import` does NOT mint .gd.uid sidecars (headless
--editor even core-dumps at is_cmdline_mode) — the six sidecars were
minted with the engine's own ResourceUID.create_id()/id_to_text() and
survive subsequent imports, matching the committed idiom of every prior
wave; (c) an uncaught script error inside a -s _init leaves the process
hung (quit never fires) — harness failure paths all early-return (E3)
and pytest runs the leg under a timeout.

## Scope confirmation

git show --stat HEAD: 22 files, all whitelisted (list at top). LEDGER:
not in this wave's whitelist (parent integrates the row). .audits/ stays
untracked per fleet trail rule (this file is the trail, appended to the
MC card by the parent).

VERIFY_EXIT=0
