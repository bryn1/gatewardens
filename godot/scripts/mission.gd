# hygiene: C12 funnel root + W7 hero hook lines + W8 place_defense
# (MC 11274.1.14/.15) — hard ceiling exempt per header rule, file stays smallest-correct
extends Node3D

# mission — mission scene root (Modules row scripts/mission.gd,
# MC 11274.1.13 / card 11308). Builds lanes/cores from C7, owns the
# spawn loop + balance.max_alive cap (I7), the mission-local hero_state
# table (C4: ONE blue pool, regen = ACTIVE hero's base.blue_regen F7,
# cooldowns tick ONLY for the active hero F2-8, down/swap F2-10; the
# full-HP revival is phase_controller's build-start leg), the C11 relic
# pool copy, and the camera rig (F8, this root). _process(d)=step(d)
# and NOTHING else (C12). setup(...) is main.gd's router contract (W5):
# the router loads res://scenes/mission.tscn and injects the seven
# params — zero main.gd change. Under `-s` no frame dispatches _ready
# (E5), so construction lives in setup(); _ready() stays a no-op the
# smoke may drive (add_child fires it BEFORE setup).
#
# Readings (full text in W6-evidence.md; pinned table wins per
# MC 11274.1.9/.10/.11/.12): lane_path binds the pinned static
# advance(pos,wps,speed,dt)->{pos,wp_index,arrived} (F16 y never
# rewritten); SimWave.next_event does not exist, so spawn k of a group
# lands at row.delay + k*balance.wave_delay (wave_delay = per-entity
# stagger; build_seconds owns time between waves); a wave-row
# mods.hp_mult resolves here at schedule build onto the pinned
# spawn(row,...) crossing (identity 0.0 absent); respawn_core_ratio =
# its target core for ratio x core max via dmg_to_core (armor 0.0 identity,
# C7 cores carry none) and a breach is NOT a kill (no rewards, C12 step 4
# is death-only) — the breacher is consumed, dead-sub lanes despawn (C7
# opens lanes on sub destruction, no retargeting); GWGameState ships no
# commit() so the mission-end commit calls the ONE C13 listener
# (state.commit_listener.commit()), once, AFTER step-(6) loot (F2-2 chest
# rolls pre-commit); array-shaped data files (heroes/enemies/items/mods)
# have no GWTables dict door — the raw FileAccess+JSON door (main.gd boot
# precedent); deck = C6 deck_json, empty deck falls back to all heroes;
# victory chest tier: normal->chest_tiers[0], hard->[1] (BN3; no v1 tier economy).

const CORE_OBJ := preload("res://scripts/core_obj.gd")
const DEF_OBJ := preload("res://scripts/defense_obj.gd")
const HERO_RIG := preload("res://scripts/hero_controller.gd")
const SIM_WAVE := preload("res://sim/sim_wave.gd")
const SIM_COMBAT := preload("res://sim/sim_combat.gd")
const SIM_ECONOMY := preload("res://sim/sim_economy.gd")
const SIM_LOOT := preload("res://sim/sim_loot.gd")
const MESH_CORE := preload("res://assets/mesh_core.tres")
const MAT_CORE := preload("res://assets/mat_core.tres")

const SWAP_KEYS := {"F1": 0, "F2": 1, "F3": 2,   # hero_controller row's
	"Digit1": 0, "Digit2": 1, "Digit3": 2}        # F1-F3 + Digit aliases

# ---- C5-readable mission fields (game_state.snapshot_json reads by name)
var mission_id := ""
var difficulty := "normal"
var wave := 0
var phase_kind := "build"
var in_combat := false
var wave_remaining := 0
var alive := 0
var green := 0
var blue := 0.0
var blue_max := 0.0
var hero_id := ""
var hero_hp := 0.0
var hero_hp_max := 0.0
var cores: Dictionary = {}
var defenses := 0
var defense_cap := 0
var relics_assigned := 0
var loot_pending := 0
var outcome: Variant = null      # "win" | "lose" | null
var boss_hp: Variant = null      # C5 F13: non-null while wave 10 is live
var t := 0.0

# ---- injected deps (R3: everything arrives as a param) ----
var tables = null
var state = null
var save_store = null            # pinned setup param; commit is state's listener
var bridge = null
var rng = null

# ---- mission-local state ----
var map_def: Dictionary = {}
var waves_file: Dictionary = {}
var economy: Dictionary = {}
var balance: Dictionary = {}
var xp_table: Dictionary = {}
var sim_tables: Dictionary = {}  # the plain {stem: data} dict SimLoot takes
var enemy_defs: Array = []
var hero_defs: Dictionary = {}
var lanes: Dictionary = {}       # lane id -> C7 record + open flag
var core_main = null
var core_subs: Dictionary = {}
var hero_state: Dictionary = {}  # id -> {hp, hp_max, cooldowns, downed}
var deck: Array = []
var active := 0
var relic_pool: Array = []       # C11 copy; the bank is NOT consumed
var defense_list: Array = []     # W8 (defense_placer) fills this
var defense_uid := 0             # W8: mission-local defense uid counter
var xp_earned := 0
var loot: Array = []             # mission-local pending tray
var spawn_queue: Array = []
var wave_t := 0.0
var wave_delay := 0.0
var max_alive := 0
var respawn_ratio := 0.0
var boss = null                  # the sole boss entity record (wave 10)
var win_pending := false
var committed := false

func _ready() -> void:
	# No-op by contract: the router fires _ready at add_child, BEFORE the
	# setup() injection, so nothing here may read injected deps (E5-safe).
	return

func setup(tables_in, state_in, save_store_in, bridge_in, map_id,
		difficulty_in, rng_in) -> void:
	tables = tables_in
	state = state_in
	save_store = save_store_in
	bridge = bridge_in
	difficulty = String(difficulty_in)
	rng = rng_in
	mission_id = String(map_id)
	map_def = tables.map(mission_id)
	waves_file = tables.table("waves/waves_" + mission_id + "_" + difficulty)
	economy = tables.table("economy")
	balance = tables.table("balance")
	xp_table = tables.table("xp")
	enemy_defs = _load_array("enemies")
	sim_tables = {"rarity": tables.table("rarity"),
		"items": _load_array("items"), "mods": _load_array("mods")}
	max_alive = int(balance.get("max_alive", 0))
	wave_delay = float(balance.get("wave_delay", 0.0))
	respawn_ratio = float(balance.get("respawn_core_ratio", 0.0))
	defense_cap = int(map_def.get("defense_cap", 0))
	green = int(map_def.get("start_green", 0))   # C7 sole source (F7)
	_build_lanes()
	_build_cores()
	_build_heroes()
	for row: Dictionary in state.bank:            # C11 relic pool copy
		if String(row.get("slot", "")) == "relic":
			relic_pool.append(row.duplicate(true))
	$EnemyRunner.setup(difficulty)
	$PhaseController.setup(self)
	# W7 hero hook (DECLARED, MC 11274.1.14): the rig builds the per-hero
	# pawns + hero_combat from the injected data; its visuals are children
	# of the rig body, the camera rig on this root is never touched (F8).
	var rig := HERO_RIG.new()
	rig.name = "HeroRig"
	add_child(rig)
	rig.setup(self)
	_refresh_cores()    # C5 mirrors readable from the very first snapshot
	hero_hp = float(hero_state[hero_id]["hp"])
	hero_hp_max = float(hero_state[hero_id]["hp_max"])

func step(delta: float) -> void:
	if outcome != null:
		return
	t += delta
	$PhaseController.step(delta)   # (1) phase: transitions, refill, awards
	step_hero(delta)               # (2) heroes: ACTIVE hero state math only
	step_defenses(delta)           # (3) defenses: target/fire/repair (W8)
	step_enemies(delta)            # (4) enemies: advance/attack/death awards
	step_bookkeeping(delta)        # (5) swap/down, win FIRST, lose overwrites
	step_loot(delta)               # (6) loot: chest pre-commit, end commit

func _process(d: float) -> void:
	step(d)

func step_hero(delta: float) -> void:
	# C4/F2-8: only the ACTIVE hero's regen (base.blue_regen, sole source
	# F7) and cooldowns tick; inactive/downed arrays stay frozen.
	if hero_state.is_empty():
		return
	var hs: Dictionary = hero_state[hero_id]
	if bool(hs["downed"]):
		return
	var base: Dictionary = hero_defs[hero_id]["base"]
	blue = SIM_COMBAT.tick_blue(blue, float(base["blue_regen"]),
			float(base["blue_max"]), delta)
	var cds: Array = hs["cooldowns"]
	for i: int in cds.size():
		cds[i] = maxf(float(cds[i]) - delta, 0.0)
	$HeroRig.step(delta)   # W7 hook (DECLARED): funnel slot (2) hero step

func step_defenses(_delta: float) -> void:
	# C12 slot (3): defense records arrive with W8; loop carries the slot.
	for rec: Dictionary in defense_list:
		if rec.has("tick"):
			rec["tick"].call(_delta)

func step_enemies(delta: float) -> void:
	if String(phase_kind) == "combat":
		wave_t += delta
		while not spawn_queue.is_empty() \
				and float(spawn_queue[0]["at"]) <= wave_t:
			if $EnemyRunner.alive_count() >= max_alive:
				break    # I7: stalled at the cap — delayed, never exceeded
			var item: Dictionary = spawn_queue.pop_front()
			var lane: Dictionary = item["lane"]
			if lane.is_empty() or not bool(lane["open"]):
				continue    # closed lane sends nothing (reading on trail)
			$EnemyRunner.spawn(item["row"], lane, enemy_defs, rng)
			if bool(item["boss"]):
				var ents: Array = $EnemyRunner.entities
				boss = ents[ents.size() - 1]
	var ev: Dictionary = $EnemyRunner.step(delta)
	for ent: Dictionary in ev["dead"]:
		_on_death(ent)
	for ent: Dictionary in ev["reached"]:
		_on_reach(ent)

func step_bookkeeping(_delta: float) -> void:
	for code: String in bridge.drain_presses():    # hot-swap = index change
		if SWAP_KEYS.has(code):
			_try_swap(SWAP_KEYS[code])
	for hid: String in deck:                        # down detection (BN5)
		var hs: Dictionary = hero_state[hid]
		if float(hs["hp"]) <= 0.0 and not bool(hs["downed"]):
			hs["downed"] = true
	if hero_id != "" and bool(hero_state[hero_id]["downed"]):  # F2-10
		_auto_swap()
	alive = $EnemyRunner.alive_count()
	wave_remaining = spawn_queue.size() + alive
	defenses = defense_list.size()
	loot_pending = loot.size()
	hero_id = deck[active] if active < deck.size() else ""
	hero_hp = float(hero_state[hero_id]["hp"]) if hero_id != "" else 0.0
	hero_hp_max = float(hero_state[hero_id]["hp_max"]) if hero_id != "" else 0.0
	boss_hp = float(boss["hp"]) if boss != null else null
	_refresh_cores()
	# F2-9 (binding): win FIRST; a same-tick lose condition OVERWRITES it.
	if win_pending:
		outcome = "win"
	if bool(core_main.destroyed) or _all_down():
		outcome = "lose"

func step_loot(_delta: float) -> void:
	# C12 slot (6) + F2-2: on the win tick the free victory chest rolls
	# HERE, before the C13 mission-end commit (_end_mission, once). A loss
	# drops the pending tray (the run's loot is lost; only chest banks).
	if outcome == null or committed:
		return
	if String(outcome) == "win":
		var tier := 0 if difficulty == "normal" else 1
		for item: Dictionary in SIM_LOOT.victory_chest(tier, sim_tables, rng):
			loot.append({"kind": "item", "item": item})
	_end_mission()

func start_wave(i: int) -> void:
	spawn_queue = []
	wave_t = 0.0
	var wrow: Dictionary = waves_file.get("waves", [])[i]
	var is_last := i + 1 == SIM_WAVE.total_waves(waves_file)
	var hp_mult := float(wrow.get("mods", {}).get("hp_mult", 0.0))
	var first_group := true
	for row: Dictionary in SIM_WAVE.wave_comp(waves_file, i):
		var srow: Dictionary = row.duplicate(true)
		srow["hp_mult"] = hp_mult
		var count := int(row["count"])
		for k: int in count:
			spawn_queue.append({"at": float(row["delay"]) + float(k) * wave_delay,
				"row": srow, "lane": lanes.get(String(row["lane"]), {}),
				"boss": is_last and first_group})
		first_group = false
	spawn_queue.sort_custom(_by_at)

func revive_downed() -> void:
	# C4: build-phase-start revival at full HP; downed stay unswappable.
	for hid: String in hero_state:
		var hs: Dictionary = hero_state[hid]
		if bool(hs["downed"]):
			hs["downed"] = false
			hs["hp"] = float(hs["hp_max"])

func place_defense(row: Dictionary, tier: int, at: Vector3) -> Dictionary:
	# W8 (DECLARED hook, pinned mission row names place_defense): THE
	# placement application site — C7 defense_cap + SimEconomy can_afford
	# guards, the ONE `green -= cost` write for the place leg (upgrade/
	# repair/sell writes live in defense_obj, one per leg), T1-only build
	# (DD2 flat-tier: higher tiers ride the C3 upgrade ladder), then the
	# defense_obj record enters defense_list carrying its tick — funnel
	# slot (3) fires it unchanged (C12 word-for-word intact).
	if tier != 1:
		return {"ok": false, "why": "tier"}
	if defense_list.size() >= defense_cap:
		return {"ok": false, "why": "cap"}
	var cost := int(row.get("base_cost", 0))
	if not SIM_ECONOMY.can_afford(green, cost):
		return {"ok": false, "why": "green", "cost": cost}
	green -= cost
	defense_uid += 1
	var obj = DEF_OBJ.new()
	obj.init_defense(self, row, at, defense_uid)
	add_child(obj.node)
	defense_list.append({"uid": defense_uid, "obj": obj, "tick": obj.tick})
	return {"ok": true, "uid": defense_uid, "cost": cost}

func _try_swap(i: int) -> void:
	if i < 0 or i >= deck.size() or i == active:
		return
	if bool(hero_state[deck[i]]["downed"]):
		return    # downed heroes are unswappable until next build start
	_select(i)

func _auto_swap() -> void:
	# F2-10: deck order from downed+1, wrapping at most once; none found
	# -> the all-down lose path (step 5).
	for off: int in range(1, deck.size()):
		var j := (active + off) % deck.size()
		if not bool(hero_state[deck[j]]["downed"]):
			_select(j)
			return

func _select(i: int) -> void:
	active = i
	hero_id = String(deck[i])
	blue_max = float(hero_defs[hero_id]["base"]["blue_max"])
	blue = minf(blue, blue_max)   # C4 swap clamp

func _all_down() -> bool:
	if hero_state.is_empty():
		return false
	for hid: String in hero_state:
		if not bool(hero_state[hid]["downed"]):
			return false
	return true

func _on_death(ent: Dictionary) -> void:
	var row: Dictionary = ent["def"]
	var green_block: Dictionary = economy.get("green", {})
	green = SIM_ECONOMY.add_green(green, int(row.get("green", 0)),
			int(green_block.get("cap", 0)))
	xp_earned += int(row.get("xp", 0))
	for drop: Dictionary in SIM_LOOT.enemy_drops(row, sim_tables, rng):
		loot.append(drop)
	if boss != null and ent == boss:
		$PhaseController.boss_died()

func _on_reach(ent: Dictionary) -> void:
	var rec = core_main if String(ent["lane"]["target"]) == "main" \
			else core_subs.get(String(ent["lane"]["target"]))
	if rec == null or bool(rec.destroyed):
		return
	rec.take_damage(SIM_COMBAT.dmg_to_core(float(rec.hp_max) * respawn_ratio, 0.0))
	if bool(rec.destroyed):
		rec.node.visible = false
		for lid: String in rec.opens_lanes:
			if lanes.has(lid):
				lanes[lid]["open"] = true

func _end_mission() -> void:
	committed = true
	for hid: String in deck:
		if xp_earned > 0:
			state.add_hero_xp(hid, xp_earned)
	if String(outcome) == "win":
		for drop: Dictionary in loot:
			if String(drop.get("kind", "")) == "item":
				state.bank_add(drop["item"])
			else:
				state.add_material(String(drop["id"]), 1)
		state.complete_mission(mission_id + "_" + difficulty)
	loot = []
	loot_pending = 0
	if state.commit_listener != null:
		state.commit_listener.commit()   # C13 mission-end commit, ONCE

func _build_lanes() -> void:
	var closed := {}
	for sub: Dictionary in map_def.get("cores", {}).get("subs", []):
		for lid: Variant in sub.get("opens_lanes", []):
			closed[String(lid)] = true
	for lane: Dictionary in map_def.get("lanes", []):
		var wps: Array[Vector3] = []
		for wp: Variant in lane.get("waypoints", []):
			wps.append(Vector3(float(wp[0]), float(wp[1]), float(wp[2])))
		lanes[String(lane["id"])] = {"id": String(lane["id"]),
			"kind": String(lane["kind"]), "wps": wps,
			"target": String(lane["target"]),
			"open": not closed.has(String(lane["id"]))}

func _build_cores() -> void:
	var cores_row: Dictionary = map_def.get("cores", {})
	core_main = _make_core("main", "main", cores_row.get("main", {}), Vector3.ONE)
	for sub: Dictionary in cores_row.get("subs", []):
		core_subs[String(sub["id"])] = _make_core(
				String(sub["id"]), "sub", sub, Vector3(0.5, 0.5, 0.5))

func _make_core(id: String, kind: String, row: Dictionary, sc: Vector3):
	var rec = CORE_OBJ.new()
	rec.id = id
	rec.kind = kind
	rec.hp_max = float(row["hp"][difficulty])
	rec.hp = rec.hp_max
	var p: Array = row.get("pos", [0, 0, 0])
	rec.pos = Vector3(float(p[0]), float(p[1]), float(p[2]))
	rec.opens_lanes = row.get("opens_lanes", [])
	var node := MeshInstance3D.new()
	node.mesh = MESH_CORE.duplicate()
	node.material_override = MAT_CORE.duplicate()
	node.scale = sc
	node.position = rec.pos   # mission-local space (root at origin)
	add_child(node)
	rec.node = node
	return rec

func _build_heroes() -> void:
	for row: Dictionary in _load_array("heroes"):
		hero_defs[String(row["id"])] = row
	deck = state.deck.duplicate() if not state.deck.is_empty() \
			else hero_defs.keys()
	for hid: Variant in deck:
		var base: Dictionary = hero_defs[String(hid)]["base"]
		hero_state[String(hid)] = {"hp": float(base["health"]),
			"hp_max": float(base["health"]), "downed": false,
			"cooldowns": [0.0, 0.0, 0.0, 0.0]}
	_select(0)
	blue = blue_max    # setup init (NOT the refill path — that is pc-only)

func _refresh_cores() -> void:
	var subs: Array = []
	for sid: String in core_subs:
		subs.append({"id": sid, "hp": float(core_subs[sid].hp),
			"max": float(core_subs[sid].hp_max)})
	cores = {"main": {"hp": float(core_main.hp), "max": float(core_main.hp_max)},
		"subs": subs}

func _load_array(stem: String) -> Array:
	# Array-shaped files have no GWTables dict door (header) — raw door.
	var text := FileAccess.get_file_as_string("res://data/" + stem + ".json")
	var parsed: Variant = JSON.parse_string(text)
	return parsed if parsed is Array else []

static func _by_at(a: Dictionary, b: Dictionary) -> bool:
	return float(a["at"]) < float(b["at"])
