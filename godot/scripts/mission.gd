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
# rolls pre-commit). W16 (MC 11274.1.28) split the build legs into
# mission_world (lanes/cores), mission_heroes (hero table + C4 swap)
# and mission_relics (C11 crossing) — bodies byte-identical, the public
# crossings stay HERE; array-shaped data files ride the ONE GWTables
# .rows door; deck = C6 deck_json, empty deck falls back to all heroes;
# victory chest tier: normal->chest_tiers[0], hard->[1] (BN3; no v1 tier economy).

const DEF_OBJ := preload("res://scripts/defense_obj.gd")
const MISSION_RELICS := preload("res://scripts/mission_relics.gd")
const MISSION_HEROES := preload("res://scripts/mission_heroes.gd")
const MISSION_WORLD := preload("res://scripts/mission_world.gd")
const DEF_PANEL := preload("res://scripts/defense_panel.gd")
const HERO_RIG := preload("res://scripts/hero_controller.gd")
const HUD_SCENE := preload("res://scenes/hud.tscn")
const SIM_WAVE := preload("res://sim/sim_wave.gd")
const SIM_COMBAT := preload("res://sim/sim_combat.gd")
const SIM_ECONOMY := preload("res://sim/sim_economy.gd")
const SIM_LOOT := preload("res://sim/sim_loot.gd")

# W14 (MC 11274.1.25 / card 11341, P1-4): the swap keys are F1-F3 ONLY
# (C4, the HUD hints). The Digit1..3 swap aliases are REMOVED — Digit1..4
# are the hero_combat ability codes (W7 hold-level); one press must not
# cast AND teleport the hero. Hub Digit use is hub-side routing, untouched.
const SWAP_KEYS := {"F1": 0, "F2": 1, "F3": 2}    # hero_controller row's
                                                   # pinned F1-F3 swap keys

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
var loot_events: Array = []      # C12 slot-(6) loot_pickup event rows (W11,
                                 # MC 11274.1.19 / card 11326): item drops in
                                 # the pinned C9 shape verbatim, HUD-toast read
var loot_events_seen := 0        # the slot-(6) tray-walk cursor
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
	enemy_defs = tables.rows("enemies")
	sim_tables = {"rarity": tables.table("rarity"),
		"items": tables.rows("items"), "mods": tables.rows("mods")}
	max_alive = int(balance.get("max_alive", 0))
	wave_delay = float(balance.get("wave_delay", 0.0))
	respawn_ratio = float(balance.get("respawn_core_ratio", 0.0))
	defense_cap = int(map_def.get("defense_cap", 0))
	green = int(map_def.get("start_green", 0))   # C7 sole source (F7)
	MISSION_WORLD.build_lanes(self)
	MISSION_WORLD.build_cores(self)
	MISSION_HEROES.build_heroes(self)
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
	MISSION_WORLD.refresh_cores(self)   # C5 mirrors readable from the very first snapshot
	hero_hp = float(hero_state[hero_id]["hp"])
	hero_hp_max = float(hero_state[hero_id]["hp_max"])
	# W10 HUD hook (DECLARED, MC 11274.1.18 / card 11325): the read-only
	# overlay mounts as a CanvasLayer child of this root; it READS mission
	# fields only and mutates NOTHING (I4 — test_hud.py source-truth gates
	# zero mutator calls / zero state writes in hud.gd).
	var hud := HUD_SCENE.instantiate()
	hud.name = "HUD"
	add_child(hud)
	hud.setup(self)
	# W14 (MC 11274.1.25 / card 11341, P1-1): the build-phase defense panel
	# mounts HERE — the same declared-hook idiom as the HUD above (E5-safe:
	# everything builds in setup() after injection). This is the row's own
	# wiring note ("the scene mount (mission adds this Control) is that
	# row's wiring"); until now smoke-only, so placement was UNREACHABLE in
	# the served game. Pure UI over mission/defense_obj; step (5) relays.
	var panel := DEF_PANEL.new()
	panel.name = "DefensePanel"
	panel.position = Vector2(904, 12)  # W17b card 11386: right column,
	add_child(panel)                   # clear of EVERY HUD rect at
	panel.setup(self)                  # 1280x720 (test_mission_clicks)

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
	var presses: Array = bridge.drain_presses()   # one pump, routed (C12 (5))
	for code: String in presses:                  # hot-swap = index change
		if SWAP_KEYS.has(code):
			MISSION_HEROES.try_swap(self, SWAP_KEYS[code])
	# W14 (P1-1): the build panel's codes (KeyM/KeyE/KeyN) route THROUGH
	# the mounted panel (row: bridge input in, action out); poll() ignores
	# every non-panel code, so the swap leg above is untouched (P1-4).
	$DefensePanel.poll(presses)
	for hid: String in deck:                        # down detection (BN5)
		var hs: Dictionary = hero_state[hid]
		if float(hs["hp"]) <= 0.0 and not bool(hs["downed"]):
			hs["downed"] = true
	if hero_id != "" and bool(hero_state[hero_id]["downed"]):  # F2-10
		MISSION_HEROES.auto_swap(self)
	alive = $EnemyRunner.alive_count()
	wave_remaining = spawn_queue.size() + alive
	defenses = defense_list.size()
	relics_assigned = MISSION_RELICS.live_count(self)   # C5 mirror, one recompute site
	loot_pending = loot.size()
	hero_id = deck[active] if active < deck.size() else ""
	hero_hp = float(hero_state[hero_id]["hp"]) if hero_id != "" else 0.0
	hero_hp_max = float(hero_state[hero_id]["hp_max"]) if hero_id != "" else 0.0
	boss_hp = float(boss["hp"]) if boss != null else null
	MISSION_WORLD.refresh_cores(self)
	# F2-9 (binding): win FIRST; a same-tick lose condition OVERWRITES it.
	if win_pending:
		outcome = "win"
	if bool(core_main.destroyed) or MISSION_HEROES.all_down(self):
		outcome = "lose"

func step_loot(_delta: float) -> void:
	# C12 slot (6) loot feed (W11, MC 11274.1.19 / card 11326): the tray
	# grows in slot-(4) deaths (_on_death drops); the loot_pickup event
	# mirror drains it HERE, one walk per drop row, item drops carried in
	# the pinned C9 shape VERBATIM (the rolled row — no field invented;
	# uid stays the roll-side 0, identity is the bank's C6/C9 concern).
	# A material row is not a C9 item row (C9 is the item shape): it stays
	# tray-only and routes to the bank's add_material leg in _end_mission.
	# The victory-chest row is appended below on the end tick only, after
	# this walk — it enters the bank directly, never the event feed.
	while loot_events_seen < loot.size():
		var drop: Dictionary = loot[loot_events_seen]
		if String(drop.get("kind", "")) == "item":
			loot_events.append(drop["item"])
		loot_events_seen += 1
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
	# (W16: the body lives in mission_heroes.revive, byte-identical.)
	MISSION_HEROES.revive(self)

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

# C11 (R2 relics-for-towers; W14 leg 2, MC 11274.1.25 / card 11341):
# the pinned mission-row crossing. Build phase ONLY, one relic per
# defense, one defense per relic (pool uids unique). The bank is NOT
# consumed — relic_pool is the mission-local copy setup() made; the
# bonus application lives on defense_obj (the row), the stat math in
# SimInventory.relic_bonuses (the ONE relic static, never reimplemented).
func assign_relic(defense_uid: int, relic_uid: int) -> Dictionary:
	# (W16: the body lives in mission_relics.assign, byte-identical.)
	return MISSION_RELICS.assign(self, defense_uid, relic_uid)

func unassign_relic(defense_uid: int) -> Dictionary:
	# (W16: the body lives in mission_relics.unassign, byte-identical.)
	return MISSION_RELICS.unassign(self, defense_uid)

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

static func _by_at(a: Dictionary, b: Dictionary) -> bool:
	return float(a["at"]) < float(b["at"])
