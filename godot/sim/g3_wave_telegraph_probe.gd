# g3_wave_telegraph_probe — the G3 build-phase wave telegraph headless
# proof (MC card 11696 / V121-PLAN G3). Boot idiom = g1_gate_eye_probe
# (itself the v1_world_probe/v4 line): mission.tscn instantiated, _ready
# and setup driven directly (E5), pinned smoke seed. Lockstep idiom =
# v5_fx_probe/G6: WaveTelegraph.telegraph_step() is driven by hand AFTER
# every mission.step (E5: -s dispatches no _process; this is the exact
# live tree order). The mount is pinned through mission.tscn — the probe
# never add_childs it (the G6 mount-assert idiom).
# The sim keeps its own contract honest: NO phase fields are faked —
# edges are crossed by driving mission.step over the real build_timer,
# and 3 ballistae (the shipped place_defense crossing, wave-0 build
# green) keep wave-0/1 leakers under the main core's lose line so the
# wave-1 build edge actually lands.
# Rows (machine lines; any failed check prints G3T-FAIL <why>, quit 1):
#  MOUNT  WaveTelegraph is a mission.tscn scene child on the pinned script.
#  W0     wave-0 BUILD phase: per-entry MARK lines (spawner/enemy/kind/
#         count/y) + ENT n=0 — the PRE-FIRST-SPAWN leg (the plan DoD:
#         observer state read at build, before any EnemyRunner.spawn).
#  CLEAR  the REAL combat edge (phase_changed "combat" fired inside
#         PhaseController.step): telegraph has 0 children, 0 entries.
#  NEG    combat CONTINUES with entities alive: still 0 markers — the
#         clear is the edge, not an empty-frame coincidence (the fleet
#         negative-leg rule; the planted-red target row).
#  W1     wave-1 build edge: markers re-shown with UPDATED counts, and
#         spawn_b absent (NEG: wave row 1 carries no spawn_b lane).
#  W2     wave-2 build: the air group paints ABOVE the ground group at
#         the same gate (air origin y comes off the lane data).
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]   # starter deck (v4)
const TELE_SCRIPT := "res://scripts/wave_telegraph.gd"
const DT := 0.25              # the live frame step (production cadence)
const EDGE_BUDGET := 600      # steps a phase edge may need before it is dead

var _failed := false
var _frames := 0
var _m = null
var _tel = null


func _init() -> void:
	root.size = Vector2i(1280, 720)
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	graph["state"].set_deck(DECK.duplicate())   # starter deck (C13)
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                                  # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274                            # pinned seed, smoke idiom
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	if String(m.phase_kind) != "build":
		_fail("mission setup did not land the build phase")
		return
	_m = m
	_tel = m.get_node_or_null("WaveTelegraph")
	if _tel == null:
		_fail("mission.tscn does not ship WaveTelegraph")
		return
	if String(_tel.script.resource_path) != TELE_SCRIPT:
		_fail("WaveTelegraph on wrong script: %s" % _tel.script.resource_path)


func _process(_delta: float) -> bool:
	if _failed:
		return true                       # quit(1) already fired
	_frames += 1
	if _frames == 4:
		_legs()
		if not _failed:
			print("G3T-OK")
			quit(0)
	return false


func _legs() -> void:
	print("G3T-MOUNT script=%s" % TELE_SCRIPT)
	# ---- wave-0 BUILD phase: markers present, nothing spawned yet ----
	_step()
	var runner = _m.get_node("EnemyRunner")
	if runner.entities.size() != 0:
		_fail("W0-ENT entities alive during the build phase")
		return
	print("G3T-W0-ENT n=0")
	_marks("W0")
	if int(_tel.shown_total) <= 0:
		_fail("W0 no telegraph entries during wave-0 build")
		return
	# Keep the sim winnable the SHIPPED way: three ballistae on lane_g1
	# (place_defense is the ONE placement crossing; wave-0 build green
	# 300 = 3 x base_cost — the towers are here to stop the mission
	# LOSING on wave 0, not to test placement, which W17b pins).
	for i: int in [1, 2, 3]:
		var r: Variant = _lane_wps("lane_g1")[i]
		var res: Dictionary = _m.place_defense(_tower_row("ballista"), 1,
				Vector3(float(r[0]), float(r[1]), float(r[2])))
		if not bool(res.get("ok", false)):
			_fail("probe could not place its ballista: %s" % str(res))
			return
	# ---- the REAL combat edge: markers must be GONE ----
	_until("combat", -1)
	_step()
	if _tel.get_child_count() != 0 or int(_tel.shown_total) != 0:
		_fail("CLEAR markers survive the combat edge (children=%d " \
				% _tel.get_child_count() + "entries=%d)" \
				% int(_tel.shown_total))
		return
	print("G3T-CLEAR children=0 entries=0")
	# ---- NEG: combat runs on with entities ALIVE: still zero markers ----
	var guard := 0
	while int(_m.alive) == 0 and guard < 40:
		_m.step(DT)
		_step()
		guard += 1
	if int(_m.alive) == 0:
		_fail("NEG wave-0 combat never spawned anything to clear over")
		return
	if _tel.get_child_count() != 0 or int(_tel.shown_total) != 0:
		_fail("NEG telegraph reappeared mid-combat (alive=%d)" \
				% int(_m.alive))
		return
	print("G3T-NEG alive=%d markers=0" % int(_m.alive))
	# ---- wave-1 build edge: UPDATED counts, spawn_b stays empty ----
	_until("build", 1)
	_step()
	_marks("W1")
	var s1: Dictionary = _tel.shown
	if not s1.has("spawn_a") or not s1.has("spawn_c") \
			or int(_tel.shown_total) <= 0:
		_fail("W1 wave-1 spawners missing (shown=%s)" % str(s1.keys()))
		return
	if s1.has("spawn_b"):
		_fail("W1-NEG spawn_b telegraphed — wave row 1 carries no spawn_b lane")
		return
	print("G3T-W1-NEG spawn_b=0")
	# ---- wave-2 build edge: the air group rides above the ground one ----
	_until("build", 2)
	_step()
	_marks("W2")
	var s2: Dictionary = _tel.shown
	var ay := -1.0
	var gy := -1.0
	for e: Dictionary in s2.get("spawn_a", []):
		if String(e["kind"]) == "air":
			ay = float(e["y"])
		else:
			gy = float(e["y"])
	if ay < 0.0 or gy < 0.0 or ay <= gy:
		_fail("AIR wave-2 air group not painted above the ground group " \
				+ "(air_y=%s ground_y=%s)" % [str(ay), str(gy)])
		return
	print("G3T-AIR spawn_a air_y=%s ground_y=%s above=1" \
			% [str(ay), str(gy)])


# One lockstep observation — always AFTER mission.step (live tree order).
func _step() -> void:
	_tel.telegraph_step()


func _marks(tag: String) -> void:
	for sid: String in _tel.shown:
		for e: Dictionary in _tel.shown[sid]:
			print("G3T-%s-MARK spawner=%s id=%s kind=%s count=%s y=%s" \
					% [tag, sid, String(e["id"]), String(e["kind"]),
					str(int(e["count"])), str(float(e["y"]))])


func _until(kind: String, w: int) -> void:
	var guard := 0
	while true:
		if String(_m.phase_kind) == kind \
				and (w < 0 or int(_m.wave) == w):
			return
		guard += 1
		if guard > EDGE_BUDGET:
			_fail("EDGE phase %s wave %d never landed (got %s wave %d)" \
					% [kind, w, String(_m.phase_kind), int(_m.wave)])
			return
		_m.step(DT)
		_step()


func _lane_wps(lid: String) -> Array:
	for lane: Dictionary in _m.map_def.get("lanes", []):
		if String(lane.get("id", "")) == lid:
			return lane.get("waypoints", [])
	_fail("lane %s missing from the map rows" % lid)
	return []


func _tower_row(id: String) -> Dictionary:
	for row: Dictionary in _m.tables.rows("towers"):
		if String(row.get("id", "")) == id:
			return row
	_fail("tower row %s missing" % id)
	return {}


func _fail(why: String) -> void:
	_failed = true
	print("G3T-FAIL " + why)
	quit(1)
