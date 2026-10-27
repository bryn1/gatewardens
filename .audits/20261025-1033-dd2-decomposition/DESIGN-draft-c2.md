# Gatewardens v1 — Architecture Design (c2)

SUPERSEDES: DESIGN-draft.md (c1) — MC 11274.1.3 / card 11288, round 2, after the round-1 FIX verdict.

Inputs: DA-VERDICT.md (16 findings; empirical repros in `.tmp/` of this dir), LEDGER.md A1–A10,
DD2-MECHANICS.md, hollow_dawn_3d + vampire_survivor source facts. Binding orchestrator rulings,
not relitigated here: **R1** wiki formulas (repair = base_cost × 0.75 × missing_ratio; sell =
total_spent × 0.75 × missing_ratio) · **R2** relics-for-towers stays in v1 (fix = add gear panel +
relic-equip contract C11, no descope) · **R3** NO autoloads anywhere; composition root in main.gd,
constructor/parameter injection, `-s` harness runs work by construction · **R4** one map (Gatefall);
pets/Stables named as deferred rows; A10 gets an owning row.
Shape carried from c1 where it survived the gate: data-JSON layer, sim/ statics, contracts as
concept, one map, greybox art, rejected alternatives. Contract ids C1–C10 keep meaning; new:
C11 (relic equip), C12 (step funnel), C13 (save trigger/ack).

## Fix ledger

| # | resolution | lands in |
|---|---|---|
| F1 | Autoloads dropped entirely (R3 + the `.tmp/autoload_test` repro: autoload identifiers are unregistered under `-s`, scene scripts compile-fail). Composition root `main.gd` instantiates `GWTables`/`GWGameState`/`GWSaveStore`/`GWBridge` (all `class_name … extends RefCounted`) and injects them as arguments. No `[autoload]` section in project.godot — grep-forbidden. Both source repos already do exactly this (hollow_dawn main.gd `GameState.new()`…; VS main.gd:21-42). | C1, Placement plan, Modules, I6 |
| F2 | Step-funnel contract named: mission root exposes `step(delta)`; fixed order phase→hero→defenses→enemies→bookkeeping→loot; `_process` = `step(delta)` and nothing else; `-s` harness calls `step(1.0/60.0)` directly (mirrors hollow_dawn sim_headless driving the real `_step`). RNG: fixture header `{seed:int}` → ONE seeded RNG; every roll passed as a parameter; `randf(`/`randi(` grep-zero in sim/+scripts/ → goldens byte-equal. | C12, I6, sim_headless row |
| F3 | Trimmed server is its OWN two-file module: `server/server.py` + `server/static_app.py`; GW static_app carries its OWN `send_error_json()` + static-only dispatcher (realpath jail, ext allowlist incl. .wasm/.pck, 404 `{"error":"NOT_FOUND"}`). NO api.py/db.py kept — the VS `from api import send_error_json` import (verified static_app.py:13) is replaced, not stubbed. | server/ rows, C10 |
| F4 | Gear/equip panel added: `scripts/gear_panel_ui.gd` (hub: bank list + 3 hero cards with weapon/armor/ring slots; click bank item → click compatible slot → `GameState.equip`) + `scripts/defense_panel.gd` (in-mission, build phase only: click a placed defense → tier/HP + Upgrade/Repair/Sell + relic slot → relic picker lists the mission relic pool). A9 "equip" step = hub gear panel equips a bank weapon onto a hero (observable via C5 `equipped`/`bank_count`), then in-mission relic assign (C11) exercises A6. | gear_panel_ui/defense_panel rows, C11, breakdown |
| F5 | Save triggers named (C13): every meta mutator (`add_hero_xp`, `spend_asc`, `bank_add`, `equip`) + mission-end commit → main.gd listener → `GWSaveStore.write()`; store keeps monotonic `write_seq`; C5 gains `saved_ack:int`. Playwright rule pinned: mutate → poll `GW_STATE().saved_ack > ack_before` → THEN reload. Desktop save_probe leg proves round-trip; A9 journey proves the browser (IndexedDB-backed user://) leg under the ack rule. | C13, C5, I5, test_persistence |
| F6 | I2 restated honestly: FEEL params (gravity, jump_speed, move accel/decel, interp/cam-follow rates) moved into `balance.json feel:{}` and read at setup; remaining literals in the 5 governed scripts must be ⊆ named structural set {0,1,2,3,4,-1,0.5} (0/1/2 math, 3/4 = slot/ability arity, -1 sentinel, 0.5 halving). What the gate CANNOT catch, on record: string-encoded numbers (`"3.5".to_float()`), `.tscn` scene properties, ungoverned files (hud/ui/mission setup defaults), constants inside sim/ formulas. Widening the whitelist itself is a design change, not a builder edit. | I2, balance.json row |
| F7 | Single sources: blue regen/cap are PER-HERO fields in heroes.json only (`base.blue_regen`, `base.blue_max`); economy.json keeps ONLY `blue:{refill_on_phase_start:bool}`. Map file owns `start_green` + `defense_cap`; economy.json DROPS `green.start` and `defense_cap_default` (chosen: drop, not "fallback" — a fallback is a second truth). `green.cap` stays global in economy.json (wiki global cap). | economy/heroes/map rows, C7 |
| F8 | Hot-swap semantics pinned (C4 extended): ONE mission-local blue pool clamped `blue = min(blue, new_hero.blue_max)` on swap; per-hero HP lives in a mission-local `hero_state[hero_id]={hp,hp_max,cooldowns:[float×4],downed:bool}` surviving swaps; downed hero auto-swaps out and is unswappable until the NEXT BUILD-PHASE START (revives at full HP then); all deck downed = mission lose; cooldowns tick only for the active hero, persist per hero; projectiles in flight keep flying ownerlessly (damage snapshot at launch); camera rig lives on the mission root and retargets to the new pawn — never re-parented with the pawn. | C4, hero_controller/mission rows |
| F9 | Single-source decision: **custom_html_shell**, not a generated cfg string. `godot/web_shell.html` is the one and only head-JS source (fresh GW JS written from the VS relay mechanism — `__gwSnapshot`/`GW_STATE()`/`gwHost`; VS leaderboard/submit-panel JS NOT carried — v1 has no api). `export_presets.cfg`: `html/custom_html_shell="res://web_shell.html"`, `html/head_include=""` (verified: the key exists in both source cfgs) → zero duplication by construction. test_bridge_contract asserts: cfg head_include empty + shell path set + GW names present in web_shell.html AND main.gd + VS names absent in I8 scope. hollow_dawn's cfg is NOT copied verbatim — its head_include carries VS-branded dead JS (verified). | web_shell.html row, I8, test_bridge_contract |
| F10 | I1 relabeled: STRUCTURAL guard is the real defense (C6/C8/C9 have no key/timer/paid-currency fields; test_data_schemas/test_loot_structure assert no banned FIELD names in any data file) + a tripwire grep, fixed: identifier-aware (extract identifiers, split camelCase/snake_case, case-insensitive, whole-token compare) with word-boundary word forms for prose. Banned tokens: lockbox, purchase, cash_store, iap, paywall, wallet, monetize, buyback, gacha, premium, battle_pass, gem/gems (whole word only — fixes `lane_management`), shop (whole identifier), price, key_count, real_money, timer_unlock. Limits on the record: prose strings can carry words; the grep is a tripwire, the schema absence is the guard. | I1, check_hygiene row |
| F11 | I8 grep scope pinned to `godot/ server/ static/ README.md docs/ARCHITECTURE.md`; `.audits/` explicitly exempt, stated IN the invariant text (this doc quotes VS names legitimately). | I8 |
| F12 | C3 per R1: `repair_cost(base_cost, missing_ratio, ratio)` = roundi(base_cost × ratio × missing_ratio), min 1 when missing>0; `sell_value(total_spent, missing_ratio, ratio)` = roundi(total_spent × ratio × missing_ratio) — missing-health factor RESTORED on sell (DA F12 seam closed: no cheap-repair/full-value-sell). ratio args come from economy.json repair_ratio/sell_ratio = 0.75. | C3, sim_economy row |
| F13 | C5 gains `outcome:"win"\|"lose"\|null` and `boss_hp:float\|null` (non-null while wave index 10 is live). | C5 |
| F14 | tests/conftest.py carries `ensure_class_cache()` (`godot --headless --import` once before any `-s` run; the hollow_dawn-VERIFIED quirk: preload alone cannot dodge it, fresh clone dies at parse) — named in the conftest row, inherited by every engine tier. | tests/ row, conftest |
| F15 | Deferral list under the module breakdown: Stables/pets (A6 stretch) named deferred with reason; A10 release-doctrine gets an owning row (`docs/release`). | Module task breakdown |
| F16 | `Tables.map(id)` is a real instance method (not prose); `lane_path.advance(pos:Vector3, wps:Array[Vector3], speed, dt)` — waypoints are already `[x,y,z]` (C7): air lanes carry y = flight height, ground lanes y = 0, authored in the map file; lane_path never modifies y (no projection step). `SimTables.validate` callers named: composition-root boot (fail-fast: print errors, quit) AND a `-s` validate_probe leg run by test_data_schemas (engine tier, like save_probe). Wave wording fixed everywhere: "waves array has 11 entries: index 0..9 kind normal + index 10 kind boss". | tables/lane_path/sim_tables rows, C7/C8, I4, test_waves |

## Placement plan

Layout v2 (one dir per project; never a sibling naming scheme):

```
~/Games/gatewardens/                    # git root (exists)
  README.md LEDGER.md                   # README gains the FREE-FOR-ALL row (A8) at pin time
  docs/ARCHITECTURE.md                  # created at PIN time, mirrors this doc (Architect keeps true)
  .audits/<YYYYMMDD-HHMM>-<slug>/       # every audit/verify/fix run (this run exists)
  .tmp/                                 # scratch + export scratch (gitignored)
  godot/                                # the Godot 4.7.2 project — NO [autoload] SECTION (C1)
    project.godot Main.tscn export_presets.cfg
    web_shell.html                      # THE single-source head JS shell (custom_html_shell;
                                        # head_include stays "" — F9, no duplication)
    data/   *.json                      # ALL balance + feel numbers (Modules; the pytest target)
      maps/gatefall.json
      waves/waves_gatefall_normal.json waves_gatefall_hard.json
    sim/    sim_*.gd                    # pure logic: class_name RefCounted statics/instances,
                                        # zero Node refs + harness scripts (sim_headless,
                                        # save_probe, validate_probe)
    scripts/ *.gd                       # scene layer — every dep injected as an argument
    scenes/ *.tscn                      # hub.tscn mission.tscn + component scenes
    assets/                             # greybox: procedural/BoxMesh placeholders + materials
  static/                               # committed web-export output ("web export x2" rule)
  server/ server.py static_app.py       # GW's OWN static-only server (F3): both files written
                                        # for GW, static_app.py self-contained (own
                                        # send_error_json); NO api.py, NO db.py
  tests/ conftest.py test_*.py fixtures/  # ensure_class_cache in conftest (F14); fixtures/*.jsonl
tools/  check_hygiene.py                # ceilings + I1 tripwire + I2 literal gate + randf ban
```

EXTENDED (not replaced): export preset = hollow_dawn preset.0 (Web, `variant/thread_support=false`,
`export_path="../static/index.html"` — both VERIFIED in source cfgs) with `html/custom_html_shell`
set + head_include EMPTY (F9). Bridge = VS bridge.gd key-relay mechanism (on_key/held/
drain_presses/move_vector — VERIFIED), renamed gw, restructured `class_name GWBridge extends
RefCounted` (VS's is a Node; main.gd forwards `_input`/web callbacks into it — R3). Snapshot push =
VS main.gd:84 mechanism (`_js_eval("window.__gwSnapshot="+…)`, VERIFIED). Save atomicity =
hollow_dawn `class_name DawnWell extends RefCounted` tmp+rename pattern (it is NOT an autoload —
the F1 fix direction both repos already ship). Number-gate tests = source-truth regex style + the
JSON data layer (the one genuinely new mechanism).

## Modules

Hygiene: every .gd ≤ 250 soft / 400 hard (header comment may exceed); tests ≤ 600; data exempt.

### Data files (the balance + feel truth — pytest reads these with stdlib json, no engine)

| file | JSON schema (top-level; rows are arrays of dicts) |
|---|---|
| data/economy.json | `{green:{cap:int, per_kill_default:int, per_wave:int}, upgrade_ratios:[0.5,1.0,1.5,2.0], repair_ratio:0.75, sell_ratio:0.75, blue:{refill_on_phase_start:true}}` — NO start, NO blue regen, NO defense_cap_default (F7: map owns those) |
| data/balance.json | `{max_alive:int, build_seconds_default:float, wave_delay:float, pickup_radius:float, respawn_core_ratio:float, feel:{gravity:float, jump_speed:float, move_accel:float, move_decel:float, facing_interp_rate:float, cam_follow_rate:float, cam_yaw_rate:float, death_fade:float}}` (F6) |
| data/xp.json | `{hero_curve:[int;50], enemy_xp_base:{normal:int,fly:int,boss:int}, wave_xp:int}` |
| data/heroes.json | rows `{id,name,archetype:"melee|ranger|mage", base:{health,damage,ability_power,crit_chance,crit_damage,speed,blue_max,blue_regen}, attacks:{primary:{dmg_scale,cooldown,range},secondary:{…}}, abilities:[{id,name,mana_cost,dmg_scale,aoe,cd}×4], defense_id}` — blue_max/blue_regen are the SOLE blue sources (F7) |
| data/towers.json | rows `{id,class:"tower|blockade|trap",family:"arrow|cannon|frost",name,base_cost:int,tiers:[{hp,damage,fire_rate,range,effect}×5],trap_charges:int?}` |
| data/enemies.json | rows `{id,name,hp:{normal,hard},damage,speed,fly:bool,xp,green,drop_table_id}` |
| data/rarity.json | `{ladder:["worn","sturdy","powerful","epic","mythical","legendary"], mod_slots:{worn:0,…,legendary:3}, drop_weights:{normal:{…},hard:{…}}, chest_tiers:[…]}` |
| data/items.json | bases `{id,slot:"weapon|armor|ring|relic",level_band,name,primary,pool_secondary:[…],roll_ranges:{atk_speed:[lo,hi],proj_count:[lo,hi]},shot_types:[…],mods_pool:[…]}` |
| data/mods.json | rows `{id,name,rarity_min,effect:{stat,add?%,flat?}}` |
| data/ascension.json | `{points_per_level:int, tree:{offense:[{id,max,per_point:{stat,val}}],defense:[…],utility:[…]}}` |
| data/blacksmith.json | `{upgrade:{gold_by_rarity:{…},materials:{…}}, evolve:{…}, reroll:{gold,int}}` |
| data/maps/gatefall.json | C7 shape — SOLE source of start_green + defense_cap (F7) |
| data/waves/waves_gatefall_normal.json / _hard.json | C8 shape (11 entries; index 10 boss) |

### sim/ — pure logic (class_name + extends RefCounted; NO Node/Engine refs; NO randf/randi — I6)

| file | concern | exposed interface (exact) |
|---|---|---|
| sim/sim_tables.gd | `class_name GWTables extends RefCounted` — load + hold + validate data JSON | ctor-time `func load_dir(dir:String)`; `func table(name:String)->Dictionary`; `func map(id:String)->Dictionary` (= `table("maps/"+id)`, a REAL method per F16); `static func validate(tables:Dictionary)->Array[String]` (pure, also used by validate_probe + boot) |
| sim/sim_economy.gd | green mana + build/upgrade/repair/sell math (R1) | `static func add_green(cur:int,amt:int,cap:int)->int`; `static func upgrade_cost(base:int,tier:int,ratios:Array)->int`; `static func repair_cost(base_cost:int,missing_ratio:float,ratio:float)->int` (roundi, min 1 if missing>0); `static func sell_value(total_spent:int,missing_ratio:float,ratio:float)->int` (roundi); `static func can_afford(green:int,cost:int)->bool` |
| sim/sim_combat.gd | damage/ability formulas | `static func hero_hit(dmg:float,crit_chance:float,crit_mult:float,roll:float)->Dictionary`; `static func tick_blue(blue:float,regen:float,cap:float,dt:float)->float`; `static func ability_ready(blue:float,cost:float)->bool`; `static func tower_dps(tier_row:Dictionary)->float`; `static func dmg_to_core(dmg:float,armor:float)->float` |
| sim/sim_wave.gd | wave/phase sequencing decisions | `static func wave_comp(waves_file:Dictionary,i:int)->Array`; `static func is_boss(wave_row:Dictionary)->bool`; `static func build_seconds(wave_row:Dictionary,d:float)->float`; `static func total_waves(waves_file:Dictionary)->int` (== 11 asserted by test_waves) |
| sim/sim_progression.gd | hero XP/level/ascension | `static func level_from_xp(curve:Array,xp:int)->int`; `static func xp_need(curve:Array,level:int)->int`; `static func asc_points(levels_total:int,per_level:int)->int`; `static func asc_modifier(tree:Dictionary,spent:Dictionary)->Dictionary` |
| sim/sim_loot.gd | drop + chest rolls (declared weights only) | `static func roll_rarity(tables:Dictionary,diff:String,luck:float,rng:RandomNumberGenerator)->String`; `static func roll_item(base:Dictionary,rarity:String,tables,rng)->Dictionary`; `static func enemy_drops(row:Dictionary,tables,rng)->Array`; `static func victory_chest(tier:int,tables,rng)->Array` — rng ALWAYS a parameter (C12) |
| sim/sim_inventory.gd | bank/equip + blacksmith/tinkerer ops + relic math | `static func equip(bank:Array,hero:String,item:Dictionary)->Dictionary`; `static func svc_upgrade(item:Dictionary,tables)->Dictionary`; `static func svc_evolve(…)`; `static func svc_reroll(item,rng,tables)`; `static func tinkering(source,target,mod_i,tables)`; `static func mod_slots(rarity:String,ladder:Dictionary)->int`; `static func relic_bonuses(item:Dictionary)->Dictionary` (stat→add for the owning defense, C11) |
| sim/sim_headless.gd | full-mission golden runner | `extends SceneTree`; `func _init()` — loads mission.tscn, builds GWTables/GWGameState/GWBridge/GWSaveStore itself (NO autoloads exist to break compilation, F1), seeds ONE RNG from the fixture header line, drives `mission.step(1.0/60.0)` for the full 11-wave mission, prints JSONL (extends hollow_dawn sim_headless "drives the real _step manually" pattern); fixtures regen only, never run by the number pytest |
| sim/save_probe.gd | save round-trip probe | `extends SceneTree`; builds GWGameState+GWSaveStore (user:// redirected via XDG_DATA_HOME on the desktop leg), runs mutators, reloads, prints `{ok:bool,diff:…,ack:int}` JSONL |
| sim/validate_probe.gd | data-validation probe (F16) | `extends SceneTree`; loads all data, runs GWTables.validate, prints one error line per failure; nonzero-marker output on any error (test_data_schemas engine leg) |

### scripts/ — scene layer (NO autoloads; every dependency arrives as a setup()/call argument — R3/C1)

| file | concern | interface / note |
|---|---|---|
| scripts/game_state.gd | `class_name GWGameState extends RefCounted`: meta (hero levels/xp, ascension points+spend, gear bank, gold, mission completions, active deck) | `GWGameState.new(tables)`; mutators `add_hero_xp(id,xp)`, `spend_asc(tree,power,pts)->bool`, `bank_add(item)`, `equip(hero,slot,item)`; EVERY mutator emits signal `mutated` (C13 trigger); `func snapshot_json(mission:Variant)->String` (C5); `to_save()/from_save()` |
| scripts/save_store.gd | `class_name GWSaveStore extends RefCounted`: ConfigFile user://, atomic tmp+rename + corrupt quarantine (DawnWell pattern) | `func write(d:Dictionary)->bool` — on success `write_seq += 1`; `var write_seq:int` (C13 ack source); `load_save()->Dictionary` |
| scripts/bridge.gd | `class_name GWBridge extends RefCounted`: keyboard relay (VS bridge.gd mechanism EXTENDED: adds Digit4, KeyE, KeyN, F1–F3, mouse-button codes); NO Node/`_input` here | `on_key(code,down)`, `held:Dictionary`, `drain_presses()->Array`, `move_vector()->Vector2`; main.gd forwards desktop `_input` + web JS callbacks into it |
| scripts/main.gd | APP ROOT + COMPOSITION ROOT + router Main.tscn: in `_ready` builds `tables=GWTables.new()` (runs validate → print + `quit(1)` fail-fast, F16), `game_state=GWGameState.new(tables)`, `save_store=GWSaveStore.new()`, `bridge=GWBridge.new()`; hub↔mission switching; connects `game_state.mutated` → `save_store.write` (C13); on web pushes snapshot each frame via `_js_eval("window.__gwSnapshot="+…)` (VS main.gd:84, renamed; no-op off-web) | the ONLY place the four core objects are constructed |
| scripts/hub.gd | tavern scene: static room, NPC interaction zones (proximity → open panel) | `setup(tables, game_state, save_store, bridge)` (injected from main) |
| scripts/war_table.gd | mission select panel: map + difficulty, start | calls `main.start_mission(map_id, difficulty)` |
| scripts/gear_panel_ui.gd | NEW (F4): hub gear panel — bank list (weapon/armor/ring/relic sections) + 3 hero cards with slots; click item → click compatible slot → `GameState.equip(hero,slot,item)`; equipped item returns to bank on replace | pure UI; all math in SimInventory; visible in C5 (`equipped`, `bank_count`) |
| scripts/blacksmith_ui.gd | Upgrade/Evolve/Reroll panel — ALL logic in SimInventory, pure UI | `refresh(bank)`, button → `SimInventory.svc_*(…)` → GameState |
| scripts/tinkerer_ui.gd | mod-transfer panel (source/target pick) | wraps `SimInventory.tinkering` |
| scripts/dummy_range.gd | training dummies: invulnerable dummy + live DPS readout | uses real mission combat on a mini-spawn |
| scripts/mission.gd | mission root: builds lanes/cores from C7, owns spawner loop + alive cap + the mission-local hero_state table + relic pool; OWNS the camera rig (F8) | `setup(tables, game_state, save_store, bridge, map_id, difficulty)`; `func step(delta)` = the C12 funnel; `_process(d)` calls `step(d)` ONLY; `place_defense/assign_relic/unassign_relic` |
| scripts/phase_controller.gd | build↔combat alternation; blue refill at combat start; green award at wave end; build-phase-start downed-hero revival (C4) | `step(delta)`; signals `phase_changed(kind)`, `wave_done(index)`; state machine only, numbers from economy/balance |
| scripts/hero_controller.gd | CharacterBody3D move/jump, hot-swap (F1–F3) with C4 semantics | feel params from `balance.feel` + heroes row, read at setup (F6); reads Bridge only; rig stays on mission |
| scripts/hero_combat.gd | two attacks + 4 abilities; spends blue; damage via SimCombat | NO numeric balance literals (I2); cooldowns in mission `hero_state` (C4) |
| scripts/enemy_runner.gd | lane path follow (ground/air), attack core/melee, death → green+xp+drops | `spawn(row,lane,tables,rng_source)`; lane walk only — gravity never applied on-lanes (air lanes = waypoint y, F16); projectiles ownerless (C4) |
| scripts/lane_path.gd | waypoint walker (shared by enemy_runner) | `static func advance(pos:Vector3, wps:Array[Vector3], speed:float, dt:float)->Dictionary` (`{pos,wp_index,arrived}`); y comes from the map waypoints, never rewritten (F16) |
| scripts/core_obj.gd | main/sub core health bar, game-over/open-lane-on-death | `take_damage(d)`; sub-core death opens lane ids (C7) |
| scripts/defense_placer.gd | build-phase placement: ghost, validity (range/overlap), confirm/cancel, cost via SimEconomy | validity from injected tables; calls mission.place_defense |
| scripts/defense_obj.gd | placed defense: tier hp/damage, repair, sell, target+fire (SimCombat), trap charges, relic bonus applied (C11) | tracks `total_spent:int` (green spent on place+upgrades ONLY — C3 sell base); class-dispatch dict {tower,blockade,trap} |
| scripts/defense_panel.gd | NEW (F4): in-mission build-phase selection panel — Upgrade/Repair/Sell buttons (C3) + relic slot → relic picker from the mission relic pool (C11) | pure UI over mission/defense_obj state |
| scripts/hud.gd | HP/blue/green bars, wave/phase label, defense count, loot toast | renders injected state only, no logic |
| scripts/loot_pickup.gd | world drops → pickup into pending-loot tray → bank on victory | rolls via SimLoot at drop time (rng from the mission RNG, C12); victory chest UI at mission end (free, per win) |

### Scenes: scenes/hub.tscn, scenes/mission.tscn, scenes/enemy.tscn, scenes/defense.tscn,
### scenes/core.tscn, scenes/ghost.tscn, scenes/pawn_<archetype>.tscn ×3, scenes/dummy.tscn
### Assets: greybox = ArrayMesh/BoxMesh + material tints (VS tint pattern); 3090 pipeline later.

### static/ server/ tests/ tools/
- static/ — export target, committed ("web export x2" rule inherited from VS README).
- server/server.py — ThreadingHTTPServer, binds 127.0.0.1, port env `GW_PORT` (default 8124); routes EVERYTHING to static_app (no /api — GW's own file, F3).
- server/static_app.py — GW's own static-only dispatcher: realpath jail, ext allowlist incl. .wasm/.pck, NUL-byte guard, own `send_error_json(handler, code, obj)` → 404 `{"error":"NOT_FOUND"}` (mechanism EXTENDED from VS static_app.py with its api import REPLACED by a local function, not a stub — F3).
- tests/conftest.py — repo-root helper + `ensure_class_cache()` (F14): once per session `godot --headless --import godot/` before ANY `-s` run; engine tiers (golden, persistence, validate_probe, served) call it; number tests never touch the engine. tests/test_data_schemas.py (JSON parses + required keys/types, no engine; + validate_probe `-s` leg, F16), test_economy_numbers.py (ratios 50/100/150/200 base; repair = base×0.75×missing (min 1); sell = total_spent×0.75×missing — F12; cap), test_waves.py (both files: waves array has 11 entries — index 0..9 normal + index 10 kind boss; hard hp ≥ normal — wording matches C8, F16), test_heroes.py (3 heroes, 4 abilities each cost blue, cap 50, ascension 3 trees), test_loot_structure.py (rarity ladder order, mod-slot map, NO banned FIELDS in ANY data file — the I1 structural guard — every weight table sums >0), test_bridge_contract.py (cfg `html/head_include == ""` + `custom_html_shell` = res://web_shell.html; GW names present in web_shell.html AND main.gd; VS names 0 hits in I8 scope — CONTENT IDENTITY is structural: one source file, F9), test_purity.py (sim/*.gd: no `extends Node|Engine|get_node|randf(|randi(`), test_sim_golden.py (fixtures jsonl byte-equal, seeded per C12; planted-bad red run required per A9), test_persistence.py (save_probe desktop leg + `saved_ack` monotonic, F5), test_served.py (GW_PORT server serves static/index.html 200 + C10 shapes), test_hygiene.py (calls tools/check_hygiene.py).
- tools/check_hygiene.py — stdlib-only: .gd/.py line ceilings; I1 tripwire (identifier-aware token match, F10 word list); I2 literal whitelist over the 5 governed scripts; `randf(`/`randi(` = 0 hits in godot/sim/ + godot/scripts/ (C12); `[autoload]` = 0 hits in project.godot (C1).

## Contracts

C1 — Tables access: NO autoload identifiers exist (project.godot has no `[autoload]`; grep-forbidden). The composition root (main.gd `_ready`) constructs the one GWTables and injects it into every consumer as an argument (setup()/call params). `tables.table(name)->Dictionary` (name = file stem; maps via `tables.map(id)` — a real method). Read-only doctrine: consumers never mutate a loaded table; sim never writes into one.

C2 — mission.gd → lane/enemy spawn crossing: enemy spawn row `{enemy_id:String, count:int, lane:String, delay:float}` from C8; `enemy_runner` gets `hp = row.hp[difficulty]`; mission.gd holds no HP math.

C3 — SimEconomy crossing (defense lifecycle, R1 pinned): place = `base_cost`; T(i)→T(i+1) = `upgrade_cost(base_cost, i, economy.upgrade_ratios)` = base×0.5/1.0/1.5/2.0; repair = `repair_cost(base_cost, missing_ratio, 0.75)` = roundi(base_cost×0.75×missing), min 1 when missing>0; sell = `sell_value(total_spent, missing_ratio, 0.75)` = roundi(total_spent×0.75×missing). `total_spent` = green spent on place+upgrades only (defense_obj tracks it). Green only; blue never appears in any signature (I3).

C4 — hero mission-state crossing (extended per F8): ONE mission-local blue pool (float); regen source = ACTIVE hero's `base.blue_regen` (sole source, F7), ticked via `tick_blue`; `refill_on_phase_start` handled ONLY in phase_controller (one path). On swap: clamp `blue = min(blue, new_hero.blue_max)`. Per-hero `hp/hp_max/cooldowns[4]/downed` live in mission-local `hero_state`, initialized from heroes.json at mission start, surviving swaps. Downed hero: auto-swap to next healthy hero, unswappable until NEXT BUILD-PHASE START (revives full HP); all deck downed = `outcome="lose"`. In-flight projectiles keep flying ownerlessly (snapshot damage at launch). Camera rig on the mission root retargets to the new pawn; the rig is never re-parented with a pawn.

C5 — GW_STATE snapshot (window.__gwSnapshot, accessor `window.GW_STATE()`): `{schema:int, phase:"hub"|"mission", mission_id:String, difficulty:"normal"|"hard", wave:int, phase_kind:"build"|"combat", wave_remaining:int, alive:int, green:int, green_cap:int, blue:float, blue_max:float, hero_id:String, hero_hp:float, hero_hp_max:float, cores:{main:{hp:float,max:float}, subs:[{id:String,hp:float,max:float}]}, defenses:int, defense_cap:int, deck:[{id:String,level:int}], asc_points:int, bank_count:int, gold:int, loot_pending:int, equipped:{hero_id:{weapon:String|null,armor:String|null,ring:String|null}}, outcome:"win"|"lose"|null, boss_hp:float|null, saved_ack:int, t:float}`. `equipped`/`saved_ack` new (F4/F5); `outcome`+`boss_hp` new (F13); boss_hp non-null while wave index 10 is live. One snapshot per frame on web only; Playwright reads it.

C6 — save file: ConfigFile `user://gatewardens.cfg`; sections `[meta]{schema_version:int, asc_earned:int, asc_spent_json:String}`, `[hero:<id>]{level:int, xp:int}`, `[bank]{items_json:String}` (Array of C9), `[meta2]{gold:int, deck_json:String, completed_json:String}` (`{"gatefall_normal":true,…}`). Write: tmp+rename (DawnWell pattern); unreadable previous → `*.corrupt` copy kept. Browser reload restores hero levels, ascension, gear bank (A7) — desktop round-trip via save_probe, browser leg via the A9 journey under C13.

C7 — map file (data/maps/*.json): `{id,name,defense_cap:int,start_green:int, spawners:{id:[x,y,z]}, cores:{main:{hp:{normal:float,hard:float},pos:[x,y,z]}, subs:[{id:String,hp:{…},pos,opens_lanes:[lane_id]}]}, lanes:[{id:String,kind:"ground"|"air",spawner:String,waypoints:[[x,y,z],…], target:"main"|sub_id}]}`. SOLE source of start_green + defense_cap (F7). Waypoint y: air lanes = flight height, ground lanes = 0, as authored; lane_path never rewrites y (F16).

C8 — wave file: `{map:String, difficulty:"normal"|"hard", waves:[{kind:"normal"|"boss", build_seconds:float, enemies:[{enemy_id,count,lane,delay}]}]}` — waves array has 11 entries: index 0..9 kind "normal" + index 10 kind "boss" (sole boss).

C9 — item instance (bank, drops, GW bank_count): `{uid:int, base_id:String, slot:String, rarity:String, ilvl:int, primary:{stat:String,value:float}, secondary:{…}|null, atk_speed:float|null, shot_type:String|null, proj_count:int|null, mods:[{mod_id:String,rarity:String}], upgraded:int}`. Rolls ONLY from items.json roll_ranges/pools via SimLoot (declared weights; seeded rng per C12).

C10 — served contract: GET `/` → 200 text/html; `.wasm` → application/wasm; `.pck` → application/octet-stream; unknown/escaping path → 404 `{"error":"NOT_FOUND"}` (VS static contract shape implemented by GW's own static_app + its own send_error_json — F3; test_served pins it).

C11 — relic-equip crossing (NEW, R2): at mission start, mission copies all bank rows with `slot=="relic"` into a mission-local relic pool (bank itself is NOT consumed — reload mid-mission loses only the mission). `mission.assign_relic(defense_uid, relic_uid)` / `unassign_relic(defense_uid)`: build phase ONLY, one relic per defense, one defense per relic (uids unique in pool). Defense stat bonus applied via `SimInventory.relic_bonuses(item)` on top of the tier row (defense_obj). Pool and assignments are mission-local; nothing about them enters C6.

C12 — step-funnel crossing (NEW, F2): the mission root exposes `step(delta)`; fixed call order INSIDE step: (1) phase_controller.step (transitions, refill, wave-end green, revival), (2) hero (bridge input → hero_controller → hero_combat), (3) defenses (target/fire/repair), (4) enemies (advance/attack/death→green+xp+drops), (5) mission bookkeeping (alive cap, win/lose detection → C5 outcome), (6) loot. `_process(d)` = `step(d)`, nothing more. The `-s` golden harness constructs the objects itself and calls `step(1.0/60.0)` per row line. Seed rule: each fixtures/*.jsonl FIRST LINE is `{"seed":int,…}`; the harness seeds ONE `RandomNumberGenerator(seed)`; every roll (crit, loot, chest) receives THAT rng as a parameter; `randf(`/`randi(` = 0 hits in sim/+scripts/ (check_hygiene) → goldens byte-equal. At runtime main creates the RNG seeded from OS entropy — same parameter-passing shape, determinism not required there.

C13 — save trigger/ack crossing (NEW, F5): triggers = every GWGameState mutator (signal `mutated`) + the mission-end commit (XP/loot/gold written through mutators) → main.gd listener → `save_store.write(game_state.to_save())`; on success `write_seq` increments. C5 `saved_ack` mirrors `write_seq`. Playwright rule (A7/A9): perform the meta mutation → poll `GW_STATE().saved_ack` until it exceeds the pre-action value → only THEN reload; never reload on a timer. Known limit on the record: the ack proves the write through Godot's user:// API (IndexedDB-backed on web); browser eviction is outside app control — the A9 reload is the durable proof.

## Invariants

I1 Zero monetization (MUST HOLD 1/A8) — STRUCTURAL guard (the real defense): no key/timer/paid-currency FIELDS exist in C6/C8/C9/C5 and test_data_schemas + test_loot_structure assert no banned field names in any data file; + a TRIPWIRE grep (tools/check_hygiene.py) over godot/ server/ static/ data/: identifier-aware, case-insensitive, whole-token matching (identifiers split on camelCase/snake_case; prose via word-boundary forms): lockbox|purchase|cash_store|iap|paywall|wallet|monetize|buyback|gacha|premium|battle_pass|gem(s) (whole word only)|shop (whole identifier)|price|key_count|real_money|timer_unlock → 0 hits. Named limits: prose strings can hide words; the tripwire is a tripwire — schema absence is the guard. `gem` whole-word kills the `lane_management`/`engagement_ring` false positives; `lockbox`/`purchase`/`cash_store` close the DA-measured false negatives. README states FREE-FOR-ALL (A8).
I2 Numbers-in-data (MUST HOLD 2, restated honestly per F6): balance VALUES live only in godot/data/*.json (number pytest reads JSON with stdlib json, NO engine). FEEL params live in balance.json `feel:{}` and are read at setup — governed scripts (hero_combat, enemy_runner, defense_obj, phase_controller, hero_controller) carry remaining literals ⊆ {0,1,2,3,4,-1,0.5} (structural set: math constants, slot/ability arity, sentinel, halving). The gate CANNOT catch: string-encoded numbers ("3.5".to_float()), .tscn scene properties, ungoverned files, sim/-internal constants — stated limitation, not a claim of coverage. Widening the whitelist = a design change to this section, never a builder edit to check_hygiene.py.
I3 Mana split: green spent ONLY by place/upgrade/repair/sell (SimEconomy sigs); blue spent ONLY by abilities (SimCombat/hero_combat). No function takes both pools.
I4 Wave shape (A4): both wave files — waves array has 11 entries: index 0..9 kind "normal" + index 10 kind "boss" (wording identical in test_waves, C8, here). Wave-completion green + blue-refill + downed-hero revival happen ONLY in phase_controller (one grep-able site).
I5 Persistence (MUST HOLD 4/A7): save→fresh process→load returns byte-equal meta dict (save_probe golden); schema_version mismatch → fresh-start, never crash; every write bumps `write_seq` (C13) and the A9 browser leg waits for the ack change before reload.
I6 Sim purity + determinism: sim/*.gd contain no `extends Node`, no `get_node`, no `Engine.get_singleton`, no `randf(`/`randi(` (test_purity + check_hygiene) — with zero autoloads anywhere, every scene loads under `-s` (F1 repro passes by construction) and every roll flows through the seeded C12 RNG.
I7 Performance cap (MUST HOLD 5): mission spawner never exceeds `balance.max_alive` (=100); golden run proves alive ≤ 100 across a full mission; web preset keeps thread_support=false; greybox meshes only in v1.
I8 Bridge rename-complete (MUST HOLD 3), scope-pinned (F11): within `godot/ server/ static/ README.md docs/ARCHITECTURE.md` — `VS_STATE`/`__vsSnapshot`/`vsHost` = 0 hits; `GW_STATE`/`__gwSnapshot`/`gwHost` present in web_shell.html + main.gd; cfg `html/head_include` = "" and `custom_html_shell` = "res://web_shell.html" (single source, F9). `.audits/**` IS EXPLICITLY EXEMPT from this grep (audit docs quote VS names by necessity).
I9 Hygiene: tools/check_hygiene.py enforces 250/400/600 ceilings on every .gd/.py in-repo; CI = the pytest suite itself (test_hygiene).

## Rejected alternatives

| rejected | why |
|---|---|
| Autoload singletons (Data/GameState/SaveStore/Bridge), as c1 had | REFUTED empirically (F1: `-s` compile-fail, `.tmp/autoload_test`) + ruling R3. Both source repos ship zero autoloads; composition root + injection is the inherited mechanism. |
| Keeping a subset of VS api.py for send_error_json | A stub api.py is a dead module by VS attribution; GW static_app grows its OWN send_error_json (F3). Chose named own module over "kept subset". |
| Generating the cfg head string from web_head.js | Two-file sync (generation script + committed cfg) is exactly the drift the gate found; `html/custom_html_shell` (key VERIFIED in both source cfgs) makes single-source structural. Also: hollow_dawn's cfg is NOT copied — it carries VS-branded dead leaderboard JS (F9). |
| economy.json keeping start_green/defense_cap as "fallbacks" | A fallback is a second truth (F7). Dropped; the map file owns them; global `green.cap` stays in economy. |
| Descoping relics-for-towers | Ruling R2: owner-approved A6 stays; fix = gear panel + C11, not descope. |
| Per-mission tower XP trees + ability picks | CONTRADICTED ground truth (DD2-MECHANICS §4: flat-tier green-mana defenses). Also splits tower progression across mechanisms. |
| 4-attribute hero stats (STR/DEX/INT/END) | CONTRADICTED (premise-check row 1); DD2 = damage/health/ability-power + crit/speed rolls. |
| Loot-box-style reward rolls (keys, paid rerolls, pity, time-gated chests) | Rejected STRUCTURALLY: no keys/paid-currency/timer FIELDS exist in any schema (C5/C6/C8/C9); I1 guard + tripwire. A future paywall has nothing to hang on. |
| Full 5 defense classes in v1 (Auras, Nodes deferred) | Auras need a buff-stacking ruleset; Nodes need multi-part placement linking — neither required by A3. Dispatch dict keeps the seam open; deferred, not redesigned-away. |
| .tres for balance data | JSON = zero-dep read from pytest AND Godot with one loader (GWTables). One data format, one loader. |
| Python re-implementation of the sim in tests | Tests assert DATA values + formula SHAPES + committed headless goldens; the golden runner is real game code under `-s`, never duplicated in Python. |
| Leaderboard/server-side profile (VS api.py+db.py) | v1 single-player; A7 answered by user:// ConfigFile. Dropping api/db removes a DB mechanism rather than adding a second save path. |
| Placement pads | DD2 truth = open placement with confirm/cancel (§4 INFERRED row); pads add a map-art dependency. |

## Module task breakdown

| module | depends_on | capabilities |
|---|---|---|
| repo scaffold: project.godot (NO [autoload]), web_shell.html (fresh GW bridge JS — no VS-branded code), export preset (custom_html_shell + empty head_include), server/server.py + server/static_app.py (F3), tools/check_hygiene.py, tests/conftest.py (ensure_class_cache, F14) | — | infra |
| data files (all of data/, incl. balance.json feel{} + per-hero blue rows) + schema tests (incl. validate_probe leg) | scaffold | code, test |
| sim/sim_tables (GWTables: table/map/validate) + sim_economy (F12 formulas) + economy tests | data | code, test |
| sim/sim_combat, sim_wave, sim_progression (+ tests) | data | code, test |
| sim/sim_loot, sim_inventory (incl. relic_bonuses) (+ tests) | data | code, test |
| core objects: GWGameState (+snapshot_json+mutated signal), GWSaveStore (write_seq), GWBridge — RefCounted, constructor injection | sim_tables | code |
| main.gd composition root (instantiate+inject+validate fail-fast+save listener) + router + JS snapshot push + bridge-contract test | core objects | code, test |
| mission scene: mission.gd (C12 step funnel + hero_state + relic pool), phase_controller, lane_path, core_obj, enemy_runner | sim tables, core objects | code |
| defense system: defense_placer, defense_obj (total_spent tracking), defense_panel.gd (F4) | sim_economy, mission, sim_inventory | code, frontend |
| hero: hero_controller (feel params, C4 swap), hero_combat (per-hero cooldowns), pawn scenes ×3 | sim_combat, bridge, items data | code, frontend |
| HUD + hot-swap deck UI | mission, game_state | frontend |
| hub + war_table + GEAR PANEL (gear_panel_ui, F4) + blacksmith_ui + tinkerer_ui + dummy_range | sim_inventory, game_state | code, frontend |
| loot pipeline: loot_pickup + victory chest UI | sim_loot, mission kill-funnel | code, frontend |
| golden sim: sim_headless (seeded fixtures per C12) + fixtures + test_sim_golden (byte-equal + planted red) | mission, defense, hero, phase | code, test |
| persistence: save_probe + test_persistence (ack leg) + validate_probe leg | save_store, game_state | code, test |
| docs/release (A10 OWNING ROW): README FREE-FOR-ALL row, docs/ARCHITECTURE.md kept from this doc, release-notes template; doc-sync grep sweep at tag per MC 11277 doctrine | everything above | tech-writer |
| served journey: static export ×2, test_served, Playwright A9 journey — wave 10 + boss kill asserted via outcome/boss_hp (F13), place/upgrade, loot pickup, equip via gear panel + relic assign (F4/C11), save+reload under the C13 ack rule | everything above | infra, test, frontend |

Deferral list (named, per F15/R4 — nothing of them ships; no seam is reserved):
- **Stables / pet eggs → pets** (A6 "v1 stretch row"): DD2 pets are an egg-hatch + Empowerment-stat companion system (DD2-MECHANICS §9); it rides its own NPC, hatching service, rarity roll and stat pipeline — a full subsystem, deferred out of v1.
- **Auras + Nodes defense classes** (carried from c1's rejected table): deferred mechanics, dispatch seam in defense_obj stays open.
- **Maps beyond Gatefall** (R4): lanes/waves are pure data (C7/C8), so map #2 is a data-only change post-v1.

## RESULT

Gatewardens v1 = pure-logic sim/ statics + RefCounted core objects reading godot/data/*.json (balance AND feel), a NO-AUTOLOAD composition root in main.gd injecting every dependency, a named step funnel (C12) that makes the `-s` golden tier run by construction, the wiki-pinned repair/sell formulas (C3/R1), gear panel + relic-equip (C11/R2) making the A9 "equip" step reachable, save triggers + ack (C13) making A7 synchronously testable, and honestly-labeled gates (I1 structural + tripwire; I2 with named blind spots; I8 with pinned scope). All 16 round-1 findings have a row above. The round-2 gate should attack: (1) whether C12's fixed step order + hero_state actually reproduces across builders (byte-equal golden is the instrument), (2) whether the gear-panel interaction shape is small enough to ship in one module each, (3) whether the I1 structural guard's field-name list is closed, and (4) the swap-revival edge (all-heroes-down during a build phase, boss wave bookkeeping).

# VERDICT: DONE
