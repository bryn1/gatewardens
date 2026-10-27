# Gatewardens v1 — Architecture Design (draft)

MC 11274.1.2 / card 11280 · design profile · 2026-10-25
Inputs: LEDGER.md A1–A10, DD2-MECHANICS.md (ground truth), hollow_dawn_3d (tests/ + sim/ +
export preset), vampire_survivor (server/ + bridge + VS_STATE pattern).
Decides the LEDGER open question: **v1 ships exactly ONE map (Gatefall)**; lanes/waves/cores are
pure data (C7/C8), so map #2 is a data-only change post-v1. A4 demands one polished map; a second
map before polish proves nothing new.

## Placement plan

Layout v2 (one dir per project; never a sibling naming scheme):

```
~/Games/gatewardens/                    # git root (exists)
  README.md LEDGER.md                   # exist; README gains the FREE-FOR-ALL row (A8) at pin time
  docs/ARCHITECTURE.md                  # created at PIN time, mirrors this doc (Architect keeps true)
  .audits/<YYYYMMDD-HHMM>-<slug>/       # every audit/verify/fix run (this run exists)
  .tmp/                                 # scratch + export scratch (gitignored)
  godot/                                # the Godot 4.7.2 project
    project.godot Main.tscn export_presets.cfg web_head.js
    data/   *.json                      # ALL balance numbers (see Modules; the pytest target)
      maps/gatefall.json
      waves/waves_gatefall_normal.json waves_gatefall_hard.json
    sim/    sim_*.gd                    # pure-logic math (RefCounted, zero Node refs) + headless
                                        # harness scripts (sim_headless.gd, save_probe.gd)
    scripts/ *.gd                       # scene layer: autoloads + per-concern scene scripts
    scenes/ *.tscn                      # hub.tscn mission.tscn + component scenes
    assets/                             # greybox: procedural/BoxMesh placeholders + materials
  static/                               # committed web-export output (index.html/.js/.wasm/.pck)
  server/ server.py static_app.py       # copied from vampire_survivor, api.py/db.py DROPPED (no
                                        # leaderboard in v1; meta save is client-side, see C6)
  tests/ conftest.py test_*.py fixtures/  # headless Python pytest; fixtures/*.jsonl goldens
tools/  check_hygiene.py                # line-ceiling + banned-key greps (run by tests too)
```

EXTENDED (not replaced): export preset = hollow_dawn_3d/godot/export_presets.cfg preset.0
(Web, thread_support=false, export_path ../static/index.html) with the head_include swapped from
`godot/web_head.js` (VS keeps the same head_include-source-of-truth file). Bridge = VS bridge.gd
key-relay mechanism, renamed gw. Server = VS server.py+static_app.py trim. Save atomicity =
hollow_dawn save.gd tmp+rename pattern, format ConfigFile (MUST HOLD 4). Number-gate tests =
hollow_dawn/VS test_game_numbers.py style (source-truth regex) EXTENDED with a JSON data layer —
the new mechanism this design adds, because MUST HOLD 2 demands numbers OUT of .gd sources.

## Modules

Hygiene: every .gd ≤ 250 soft / 400 hard (header comment may exceed); tests ≤ 600; data exempt.
Split below keeps every entry under the soft ceiling by construction.

### Data files (the balance truth — pytest reads these with stdlib json, no engine)

| file | JSON schema (top-level; rows are arrays of dicts) |
|---|---|
| data/economy.json | `{green:{start:int, cap:int, per_kill_default:int, per_wave:int}, upgrade_ratios:[0.5,1.0,1.5,2.0], repair_ratio:0.75, sell_ratio:0.75, blue:{regen_per_sec:float, refill_on_phase_start:true}, defense_cap_default:int}` |
| data/balance.json | `{max_alive:int, build_seconds_default:float, wave_delay:float, pickup_radius:float, respawn_core_ratio:float}` |
| data/xp.json | `{hero_curve:[int;50], enemy_xp_base:{normal:int,fly:int,boss:int}, wave_xp:int}` |
| data/heroes.json | rows `{id,name,archetype:"melee|ranger|mage", base:{health,damage,ability_power,crit_chance,crit_damage,speed,blue_max,blue_regen}, attacks:{primary:{dmg_scale,cooldown,range},secondary:{...}}, abilities:[{id,name,mana_cost,dmg_scale,aoe,cd}×4], defense_id}` |
| data/towers.json | rows `{id,class:"tower|blockade|trap",family:"arrow|cannon|frost",name,base_cost:int,tiers:[{hp,damage,fire_rate,range,effect}×5],trap_charges:int?}` |
| data/enemies.json | rows `{id,name,hp:{normal,hard},damage,speed,fly:bool,xp,green,drop_table_id}` |
| data/rarity.json | `{ladder:["worn","sturdy","powerful","epic","mythical","legendary"], mod_slots:{worn:0,…,legendary:3}, drop_weights:{normal:{...},hard:{...}}, chest_tiers:[…]}` |
| data/items.json | bases `{id,slot:"weapon|armor|ring|relic",level_band,name,primary,pool_secondary:[…],roll_ranges:{atk_speed:[lo,hi],proj_count:[lo,hi]},shot_types:[…],mods_pool:[…]}` |
| data/mods.json | rows `{id,name,rarity_min,effect:{stat,add?%,flat?}}` |
| data/ascension.json | `{points_per_level:int, tree:{offense:[{id,max,per_point:{stat,val}}],defense:[…],utility:[…]}}` |
| data/blacksmith.json | `{upgrade:{gold_by_rarity:{…},materials:{…}}, evolve:{…}, reroll:{gold,int}}` |
| data/maps/gatefall.json | C7 shape (below) |
| data/waves/waves_gatefall_normal.json / _hard.json | C8 shape (below) |

### sim/ — pure logic (class_name + extends RefCounted; NO Node/Engine refs — I8)

| file | concern | exposed interface (exact) |
|---|---|---|
| sim/sim_tables.gd | load + validate data JSON | `static func load_table(path:String)->Dictionary`; `static func load_all(dir:String)->Dictionary` (name→table); `static func validate(tables:Dictionary)->Array[String]` |
| sim/sim_economy.gd | green/blue mana + build/upgrade/repair/sell math | `static func add_green(cur:int,amt:int,cap:int)->int`; `static func upgrade_cost(base:int,tier:int,ratios:Array)->int`; `static func repair_cost(base_total:int,missing_ratio:float,ratio:float)->int`; `static func sell_value(base_total:int,ratio:float)->int`; `static func can_afford(green:int,cost:int)->bool` |
| sim/sim_combat.gd | damage/ability formulas | `static func hero_hit(dmg:float,crit_chance:float,crit_mult:float,roll:float)->Dictionary` (`{dmg:float,crit:bool}`); `static func tick_blue(blue:float,regen:float,cap:float,dt:float)->float`; `static func ability_ready(blue:float,cost:float)->bool`; `static func tower_dps(tier_row:Dictionary)->float`; `static func dmg_to_core(dmg:float,armor:float)->float` |
| sim/sim_wave.gd | wave/phase sequencing decisions | `static func wave_comp(waves_file:Dictionary,i:int)->Array` (spawn rows); `static func is_boss(wave_row:Dictionary)->bool`; `static func build_seconds(wave_row:Dictionary,d:float)->float`; `static func total_waves(waves_file:Dictionary)->int` |
| sim/sim_progression.gd | hero XP/level/ascension | `static func level_from_xp(curve:Array,xp:int)->int`; `static func xp_need(curve:Array,level:int)->int`; `static func asc_points(levels_total:int,per_level:int)->int`; `static func asc_modifier(tree:Dictionary,spent:Dictionary)->Dictionary` (stat→mult) |
| sim/sim_loot.gd | drop + chest rolls (declared weights only) | `static func roll_rarity(tables:Dictionary,diff:String,luck:float,rng:RandomNumberGenerator)->String`; `static func roll_item(base:Dictionary,rarity:String,tables,rng)->Dictionary` (C8 item-instance); `static func enemy_drops(row:Dictionary,tables,rng)->Array`; `static func victory_chest(tier:int,tables,rng)->Array` |
| sim/sim_inventory.gd | bank/equip + blacksmith/tinkerer ops | `static func equip(bank:Array,hero:String,item:Dictionary)->Dictionary`; `static func svc_upgrade(item:Dictionary,tables)->Dictionary` (`{ok,item,cost}`); `static func svc_evolve(same)->Dictionary`; `static func svc_reroll(item,rng,tables)->Dictionary`; `static func tinkering(source:Dictionary,target:Dictionary,mod_i:int,tables)->Dictionary`; `static func mod_slots(rarity:String,ladder:Dictionary)->int` |
| sim/sim_headless.gd | full-mission golden runner | `extends SceneTree`; `func _init()` — loads real Main.tscn, drives 10-wave+boss mission at fixed 1/60 dt, prints JSONL (extends hollow_dawn sim_headless pattern); fixtures regen only, never run by the number pytest |
| sim/save_probe.gd | save round-trip probe | `extends SceneTree`; writes a known meta state via SaveStore, reloads, prints `{ok:bool,diff:…}` JSONL (pattern: hollow_dawn save_probe) |

### scripts/ — scene layer (autoloads first)

| file | concern | interface / note |
|---|---|---|
| scripts/data_registry.gd | autoload `Data` | `func table(name:String)->Dictionary` — thin wrapper: `SimTables.load_all("res://data")` once in `_ready` |
| scripts/game_state.gd | autoload `GameState`: meta (hero levels/xp, ascension points+spend, gear bank, gold, mission completions, active deck) | mutators `add_hero_xp(id,xp)`, `spend_asc(tree,power,pts)->bool`, `bank_add(item)`, `equip(hero,slot,item)`; `func snapshot_json()->String` (C5); `func to_save()->Dictionary` / `func from_save(d:Dictionary)->void` |
| scripts/save_store.gd | autoload `SaveStore`: ConfigFile user://, atomic tmp+rename (EXTENDED from hollow_dawn save.gd), corrupt-file quarantine | `func load_save()->Dictionary`; `func write_save(d:Dictionary)->bool`; keys per C6 |
| scripts/bridge.gd | autoload `Bridge`: keyboard relay, web DOM + desktop native (VS bridge.gd EXTENDED: adds Digit4, KeyE, KeyN, F1–F3, mouse-button codes) | `on_key(code,down)`, `held:Dictionary`, `drain_presses()->Array`, `move_vector()->Vector2` |
| scripts/main.gd | app router Main.tscn: hub↔mission scene switching; on web pushes snapshot each frame | `_js:JavaScriptBridge` via `Engine.get_singleton`, `_js_eval(s)` guarded no-op off-web; `_js_eval("window.__gwSnapshot="+GameState.snapshot_json())` (VS main.gd:84 mechanism, renamed) |
| scripts/hub.gd | tavern scene: static room, NPC interaction zones (proximity → open panel) | zone table → `open_panel(kind)` |
| scripts/war_table.gd | mission select panel: map + difficulty, start | calls `main.start_mission(map_id, difficulty)` |
| scripts/blacksmith_ui.gd | Upgrade/Evolve/Reroll panel — ALL logic in SimInventory, this is pure UI | `refresh(bank)`, button→ `SimInventory.svc_*(...)` → GameState |
| scripts/tinkerer_ui.gd | mod-transfer panel (source/target pick) | wraps `SimInventory.tinkering` |
| scripts/dummy_range.gd | training dummies: invulnerable dummy + live DPS readout | uses real mission combat on a mini-spawn |
| scripts/mission.gd | mission root: builds lanes/cores from C7, owns spawner loop + alive cap | `start(map:Dictionary,waves:Dictionary,diff:String)`; `_process` gates spawns by `SimWave.wave_comp` + `Data.table("balance").max_alive` |
| scripts/phase_controller.gd | build↔combat alternation; blue refill at combat start; green award at wave end | signals `phase_changed(kind)`, `wave_done(index)`; state machine only, numbers via economy/balance |
| scripts/hero_controller.gd | CharacterBody3D move/jump, camera yaw, hot-swap (F1–F3) | reads Bridge only; deck swap calls GameState/mission re-parent pawn |
| scripts/hero_combat.gd | two attacks + 4 abilities; spends blue; damage via SimCombat | NO numeric balance literals (I2): reads heroes.json rows |
| scripts/enemy_runner.gd | lane path follow (ground/air), attack core/melee, death → green+xp+drops | `spawn(row:Dictionary,lane:Dictionary,tables)`; air = fixed fly height |
| scripts/lane_path.gd | waypoint walker (shared by enemy_runner) | `static func advance(pos:Vector2, wps:Array, speed:float, dt:float)->Dictionary` |
| scripts/core_obj.gd | main/sub core health bar, game-over/open-lane-on-death | `take_damage(d)`; sub-core death opens lane ids (C7) |
| scripts/defense_placer.gd | build-phase placement: ghost, validity (range/overlap), confirm/cancel, cost via SimEconomy | validity from Data economy+towers; calls mission.place_defense |
| scripts/defense_obj.gd | placed defense: tier hp/damage, repair, sell, target+fire (SimCombat), trap charges | class-dispatch dict {tower,blockade,trap}; tier row from towers.json |
| scripts/hud.gd | HP/blue/green bars, wave/phase label, defense count, loot toast | renders GameState+mission only, no logic |
| scripts/loot_pickup.gd | world drops → pickup into pending-loot tray → bank on victory | rolls via SimLoot at drop time; chest UI at mission end (free, per win) |

### Scenes: scenes/hub.tscn, scenes/mission.tscn, scenes/enemy.tscn, scenes/defense.tscn,
### scenes/core.tscn, scenes/ghost.tscn, scenes/pawn_<archetype>.tscn ×3, scenes/dummy.tscn
### Assets: greybox = ArrayMesh/BoxMesh + material tints (VS tint pattern); 3090 pipeline later.

### static/ server/ tests/ tools/
- static/ — export target, committed ("web export x2" rule inherited from VS README).
- server/server.py — ThreadingHTTPServer 127.0.0.1, static_app.serve only (api/db REMOVED:
  v1 has no leaderboard; single-player meta lives in user://). Port env `GW_PORT` (default 8124).
- server/static_app.py — copied verbatim from VS (realpath jail, ext allowlist incl. .wasm/.pck).
- tests/conftest.py — repo-root helper (EXTENDED: no server subprocess fixture needed for number
  tests; server fixture only for the served-contract test). tests/test_data_schemas.py (every
  data file parses + required keys/types), test_economy_numbers.py (ratios 50/100/150/200 base;
  repair/sell 75; cap), test_waves.py (normal+hard 10 waves, wave 10 kind=="boss", hard hp ≥
  normal), test_heroes.py (3 heroes, 4 abilities each cost blue, cap 50, ascension 3 trees),
  test_loot_structure.py (rarity ladder order, mod-slot map, NO banned keys in ANY data file,
  every roll weight table sums >0 — declared odds, no hidden box), test_bridge_contract.py
  (GW_STATE/__gwSnapshot names present in web_head.js AND export_presets.cfg AND main.gd),
  test_purity.py (sim/*.gd: no `extends Node|Engine|get_node`), test_sim_golden.py (fixtures/
  jsonl goldens vs committed files), test_persistence.py (runs godot --headless save_probe,
  second tier — engine allowed HERE, forbidden in number tests), test_served.py (server.py
  serves static/index.html 200), test_hygiene.py (calls tools/check_hygiene.py: line ceilings
  + monetization-key grep = 0 hits).
- tools/check_hygiene.py — stdlib-only; walks godot/**.gd for ceilings, godot/**.json +
  scripts for banned keys (C-list below).

## Contracts

C1 — DataRegistry read: every consumer gets tables ONLY via `Data.table(name)` (name = file
stem, e.g. "economy", "towers", "maps/gatefall" → maps keyed separately as `Data.map(id)`).
Crossing shape: plain JSON Dictionary, unmodified at runtime (read-only doctrine: sim never
writes into a table).

C2 — mission.gd → lane/enemy spawn crossing (row shapes): enemy spawn row
`{enemy_id:String, count:int, lane:String, delay:float}` from C8; enemy table row per data
table above. mission.gd holds no HP math: `enemy_runner` gets `hp = row.hp[difficulty]`.

C3 — SimEconomy crossing (defense lifecycle): place costs `base_cost`; T(i)→T(i+1) costs
`upgrade_cost(base_cost, i, economy.upgrade_ratios)` = base×0.5/1.0/1.5/2.0; repair
`repair_cost(total_spent, missing_ratio, 0.75)`; sell `sell_value(total_spent, 0.75)`.
Green only; blue never appears in any of these signatures (I4).

C4 — hero ability crossing: hero_combat.gd checks `SimCombat.ability_ready(blue, cost)` and on
cast subtracts cost from mission-local blue (float), regen via `tick_blue` each frame;
`refill_on_phase_start` handled ONLY in phase_controller (one path, mechanism-monogamy).

C5 — GW_STATE snapshot (window.__gwSnapshot, accessor `window.GW_STATE()`):
`{schema:int, phase:"hub"|"mission", mission_id:String, difficulty:"normal"|"hard",
wave:int, phase_kind:"build"|"combat", wave_remaining:int, alive:int,
green:int, green_cap:int, blue:float, blue_max:float, hero_id:String,
hero_hp:float, hero_hp_max:float, cores:{main:{hp:float,max:float}, subs:[{id:String,hp:float,max:float}]},
defenses:int, defense_cap:int, deck:[{id:String,level:int}], asc_points:int, bank_count:int,
gold:int, loot_pending:int, t:float}`. One snapshot per frame on web only; Playwright reads it.

C6 — save file: ConfigFile `user://gatewardens.cfg`; sections
`[meta]{schema_version:int, asc_earned:int, asc_spent_json:String}`,
`[hero:<id>]{level:int, xp:int}`, `[bank]{items_json:String}` (Array of C8),
`[meta2]{gold:int, deck_json:String, completed_json:String}` (`{"gatefall_normal":true,…}`).
Write: `save(path=tmp)` then DirAccess rename; unreadable previous → `*.corrupt` copy kept.
Browser reload restores: hero levels, ascension, gear bank (A7) — read by save_probe leg.

C7 — map file (data/maps/*.json): `{id,name,defense_cap:int,start_green:int,
spawners:{id:[x,y,z]}, cores:{main:{hp:{normal:float,hard:float},pos:[x,y,z]},
subs:[{id:String,hp:{…},pos,opens_lanes:[lane_id]}]},
lanes:[{id:String,kind:"ground"|"air",spawner:String,waypoints:[[x,y,z],…],
target:"main"|sub_id}]}`. Air lanes: waypoints carry y = fly height, no pathfinding.

C8 — wave file: `{map:String, difficulty:"normal"|"hard",
waves:[{kind:"normal"|"boss", build_seconds:float,
enemies:[{enemy_id,count,lane,delay}]}]}` — 11 entries, index 10 is the sole kind=="boss".

C9 — item instance (bank, drops, GW bank_count): `{uid:int, base_id:String, slot:String,
rarity:String, ilvl:int, primary:{stat:String,value:float}, secondary:{…}|null,
atk_speed:float|null, shot_type:String|null, proj_count:int|null,
mods:[{mod_id:String,rarity:String}], upgraded:int}`. Rolls come ONLY from items.json
roll_ranges/pools via SimLoot (declared weights; rng seedable).

C10 — served contract: GET `/` → 200 text/html; `.wasm` → application/wasm; `.pck` →
application/octet-stream; anything else unknown/escaping → 404 `{"error":"NOT_FOUND"}` (VS
static contract verbatim; test_served pins it).

## Invariants

I1 Zero monetization (MUST HOLD 1): `tools/check_hygiene.py` greps godot/ + server/ + data/ for
`(?i)shop\b|price|buy_|gem|coin_store|premium|battle.?pass|gacha|loot.?box|key_count|real.?
money|cooldown_unlock|time.?gate|timer_unlock` → 0 hits (gold/earned medals are the only
currencies; Victory Chest = free per-win reward, declared-weights roll, no keys/timers). README
states FREE-FOR-ALL (A8). Test: test_loot_structure + test_hygiene.
I2 Numbers-in-data (MUST HOLD 2): number pytest runs with NO engine: stdlib json on godot/data/
only. Combat-feel scripts (hero_combat, enemy_runner, defense_obj, phase_controller,
mission.gd) carry zero balance magic numbers — check: integer/float literals in those files ⊆
{0,1,2,-1,0.5} whitelist (tools/check_hygiene.py). Formulas live in sim/ as shapes; test style =
hollow_dawn source-truth regex for shapes, JSON for values.
I3 Mana split (DD2 truth): green spent ONLY by place/upgrade/repair/sell (SimEconomy sigs); blue
spent ONLY by abilities (SimCombat/hero_combat). Test asserts no function takes both pools.
I4 Wave shape (A4): both wave files = 10 normal + exactly 1 boss (last). Wave-completion green +
blue-refill happen ONLY in phase_controller (one grep-able site).
I5 Persistence (MUST HOLD 4 / A7): save→fresh process→load returns byte-equal meta dict
(save_probe golden); schema_version mismatch → fresh-start, never crash.
I6 Sim purity (I8 of tests): sim/*.gd contain no `extends Node`, no `get_node`, no
`Engine.get_singleton` (test_purity greps) — guarantees headless-runability and scene/test reuse.
I7 Performance cap (MUST HOLD 5): mission spawner never exceeds `balance.max_alive` (=100);
golden run (test_sim_golden) proves alive ≤ 100 across a full mission; web preset keeps
thread_support=false, export filter excludes nothing oversized, greybox meshes only in v1.
I8 Bridge rename-complete (MUST HOLD 3): `GW_STATE`/`__gwSnapshot`/`gwHost` present in
web_head.js + export_presets.cfg + main.gd; `VS_STATE`/`__vsSnapshot`/`vsHost` absent
repo-wide (replace-not-add, grep-zero DoD).
I9 Hygiene: tools/check_hygiene.py enforces the 250/400/600 ceilings on every .gd/.py in-repo;
CI = the pytest suite itself (test_hygiene).

## Rejected alternatives

| rejected | why |
|---|---|
| Per-mission tower XP trees + ability picks | CONTRADICTED ground truth (DD2-MECHANICS §4: DD2 defenses are flat-tier green-mana; XP trees are DD1-era). Also splits tower progression across two mechanisms. |
| 4-attribute hero stats (STR/DEX/INT/END) | CONTRADICTED (§premise-check row 1); DD2 = damage/health/ability-power + crit/speed rolls. Building the contradicted premise would fail A1/A2's own cited basis. |
| Loot-box-style reward rolls (keys, paid rerolls, pity, time-gated chests) | Rejected STRUCTURALLY, not by feature flag: no keys/paid-currency/timer FIELDS exist in any schema (C8/C6 have no such fields; check_hygiene bans the words). A future paywall has nothing to hang on. |
| Full 5 defense classes in v1 (Auras, Nodes deferred) | Auras need a buff-stacking/interaction ruleset; Nodes need multi-part placement linking — two whole new mechanics, neither required by A3 (which names Towers/Blockades/Traps: offense/tank/debuff coverage). Class dispatch in defense_obj/C7 leaves the seam open; deferred, not redesigned-away. |
| .tres for balance data | .tres is parseable but Godot-proprietary-ish INI; JSON = zero-dep read from pytest AND Godot with one loader (SimTables). Mechanism-monogamy: one data format, one loader. |
| Python re-implementation of the sim in tests | A second math implementation always drifts. Tests assert DATA values + formula SHAPES (regex, inherited style) + committed headless-goldens; the golden runner is the real game code, run via godot --headless as a separate tier — never duplicated in Python. |
| Leaderboard/server-side profile (VS api.py+db.py) | v1 is single-player; A7 only demands browser-reload persistence, which user:// ConfigFile answers. Dropping api/db removes a DB mechanism rather than adding a second save path. |
| Placement pads | DD2 truth = open placement with confirm/cancel (§4 INFERRED row); pads would add a map-art dependency. |

## Module task breakdown

| module | depends_on | capabilities |
|---|---|---|
| repo scaffold: project.godot, preset+web_head.js (gw rename sweep), server trim, tools/check_hygiene.py, tests/conftest | — | infra |
| data files (all of data/) + schema test | scaffold | code, test |
| sim/sim_tables + sim_economy + economy tests | data | code, test |
| sim/sim_combat, sim_wave, sim_progression (+ tests) | data | code, test |
| sim/sim_loot, sim_inventory (+ tests) | data | code, test |
| autoloads: data_registry, game_state (+snapshot_json), save_store, bridge | sim_tables | code |
| main.gd router + js snapshot push + bridge-contract test | autoloads | code, test |
| mission scene: mission.gd, phase_controller, lane_path, core_obj, enemy_runner | sim_economy/combos/wave, autoloads | code |
| defense system: defense_placer, defense_obj (+ tower/trap dispatch) | sim_economy, mission | code |
| hero: hero_controller, hero_combat, pawn scenes ×3 | sim_combat, bridge, items data | code, frontend |
| HUD + hot-swap UI | mission, game_state | frontend |
| hub + war_table + blacksmith_ui + tinkerer_ui + dummy_range | sim_inventory, game_state | code, frontend |
| loot pipeline: loot_pickup + victory chest UI | sim_loot, defense of mission kill-funnel | code, frontend |
| golden sim: sim_headless + fixtures + test_sim_golden | mission, defense, hero, phase | code, test |
| persistence: save_probe + test_persistence + A7 reload check | save_store, game_state | code, test |
| served journey: static export ×2, test_served, Playwright A9 journey (wave10+boss, place/upgrade, loot, equip, save+reload) | everything above | infra, test, frontend |

## RESULT

Gatewardens v1 = pure-logic sim/ (RefCounted statics, zero balance literals) reading godot/data/*.json,
thin scene layer on top; all four MUST HOLDs are mechanized as greps/pytest (no-monetization word-gate,
JSON-only numbers, GW_STATE rename-complete, ConfigFile save_probe). The gate should attack: (1) whether
the I2 literal-whitelist actually holds once combat feel lands (cheapest place to cheat it), (2) the
sim-purity claim — one stray get_node in sim/ collapses the whole test story, (3) whether one map +
11 waves exercises enough (A9 journey completeness), and (4) the hot-swap mid-mission pawn re-parent seam.

# VERDICT: DONE
