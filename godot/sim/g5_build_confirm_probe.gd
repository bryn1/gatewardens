# g5_build_confirm_probe — the G5 build-confirm UX headless proof
# (v1.2.1, MC card 11700 / V121-PLAN §1 G5 + §4 G5 card). Boot idiom =
# g3_wave_telegraph_probe / g1_gate_eye_probe (itself the v1_world_probe/
# v4 line): mission.tscn instantiated, _ready and setup driven directly
# (E5), pinned smoke seed; the mission's own _process keeps stepping, so
# presses are asserted through the REAL step (5) pump — queue a code on
# the shipped bridge relay, then one manual mission.step drains it
# exactly like production (the smoke KeyM idiom, mission_smoke.gd:126).
# Legs (machine rows G5B-*; any failed check prints G5B-FAIL <why>,
# quit 1 — the fleet negative-leg rule inside every leg: the ARM row
# proves count+green DID NOT move, the cancel row proves RMB placed
# NOTHING, the once-leg proves a second LMB press cannot double-place):
#  ARM    a class-button press ARMS: defense_list count + green byte
#         unchanged (the plan DoD negative), armed=1, ghost == the first
#         buildable() slot.
#  CYCLE  ArrowLeft/ArrowRight (held relay, rising edge) move the ghost
#         over placer.buildable(): forward one, wrap-back one.
#  LMB    MouseLeft places ONCE via the ONE m.place_defense site: count
#         +1, green drop EXACTLY the towers.json base_cost, then DISARMED
#         (ghost -1); a second MouseLeft places nothing more.
#  RMB    MouseRight cancels: armed 0, ghost -1, count unchanged.
#  KEYMA  KeyM WHILE ARMED places the armed row AT the ghost slot.
#  KEYMU  KeyM UNARMED = the legacy first-free instant place, unchanged
#         (the pinned standing behavior, plan Rev 2 / DA A4.3).
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]   # starter deck (v4)
const DT := 0.05              # one short step to drain the queued code


var _failed := false
var _frames := 0
var _m = null
var _panel = null
var _placer = null


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
	rng.seed = 11700                            # pinned seed, smoke idiom
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	if String(m.phase_kind) != "build":
		_fail("mission setup did not land the build phase")
		return
	_m = m
	_panel = m.get_node_or_null("DefensePanel")
	if _panel == null:
		_fail("shipped panel not mounted by mission.setup")
		return
	_placer = _panel.placer


func _process(_delta: float) -> bool:
	if _failed:
		return true                       # quit(1) already fired
	_frames += 1
	if _frames == 4:
		_legs()
		if not _failed:
			print("G5B-OK")
			quit(0)
	return false


func _legs() -> void:
	var btn = _panel.class_buttons.get("tower")
	if btn == null:
		_fail("class_buttons has no tower row")
		return
	# ---- ARM: press arms, places NOTHING (DoD negative leg) ----
	var c0: int = _m.defense_list.size()
	var g0 := int(_m.green)
	btn.pressed.emit()
	var free: Array = _placer.buildable()
	if free.is_empty():
		_fail("no buildable slots on a fresh map")
		return
	if _m.defense_list.size() != c0 or int(_m.green) != g0 \
			or not bool(_panel.armed):
		_fail("ARM leg: press placed/armed wrong (count %d->%d green " \
				% [c0, _m.defense_list.size()] + "%d->%d armed=%s)" \
				% [g0, int(_m.green), str(_panel.armed)])
		return
	if int(_placer.ghost) != int(free[0]):
		_fail("ARM leg: ghost %d not on the first buildable slot %d" \
				% [int(_placer.ghost), int(free[0])])
		return
	print("G5B-ARM armed=1 ghost=%d count=%d green=%d" \
			% [int(_placer.ghost), _m.defense_list.size(), int(_m.green)])
	if free.size() < 2:
		_fail("CYCLE needs >= 2 buildable slots, got %d" % free.size())
		return
	# ---- CYCLE over buildable() (held relay, rising edge) ----
	_hold("ArrowRight")
	if int(_placer.ghost) != int(free[1]):
		_fail("CYCLE fwd: ghost %d, expected %d" \
				% [int(_placer.ghost), int(free[1])])
		return
	_hold("ArrowLeft")
	if int(_placer.ghost) != int(free[0]):
		_fail("CYCLE back: ghost %d, expected %d" \
				% [int(_placer.ghost), int(free[0])])
		return
	print("G5B-CYCLE size=%d fwd=%d back=%d" \
			% [free.size(), int(free[1]), int(_placer.ghost)])
	# ---- LMB places ONCE (count +1, green -cost, disarmed) ----
	var cost := int(_placer.row_for_id(String(_panel.armed_id))["base_cost"])
	_press("MouseLeft")
	if _m.defense_list.size() != c0 + 1 or int(_m.green) != g0 - cost \
			or bool(_panel.armed) or int(_placer.ghost) != -1:
		_fail("LMB leg: place-once/disarm broken (count=%d green=%d " \
				% [_m.defense_list.size(), int(_m.green)] + "armed=%s ghost=%d cost=%d)" \
				% [str(_panel.armed), int(_placer.ghost), cost])
		return
	print("G5B-LMB count=%d green_drop=%d armed=0 ghost=-1" \
			% [_m.defense_list.size(), g0 - int(_m.green)])
	_press("MouseLeft")                      # second press: nothing more
	if _m.defense_list.size() != c0 + 1:
		_fail("LMB once-leg: a second press placed again")
		return
	print("G5B-LMB2 count=%d" % _m.defense_list.size())
	# ---- RMB cancels, no place ----
	btn.pressed.emit()
	if not bool(_panel.armed) or int(_placer.ghost) < 0:
		_fail("RMB leg: re-arm did not set the ghost")
		return
	_press("MouseRight")
	if bool(_panel.armed) or int(_placer.ghost) != -1 \
			or _m.defense_list.size() != c0 + 1:
		_fail("RMB cancel leg broken (armed=%s ghost=%d count=%d)" \
				% [str(_panel.armed), int(_placer.ghost),
					_m.defense_list.size()])
		return
	print("G5B-RMB armed=0 ghost=-1 count=%d" % _m.defense_list.size())
	# ---- KeyM WHILE ARMED: place at the GHOST slot ----
	btn.pressed.emit()
	_hold("ArrowRight")                      # aim off first-free, prove
	var want = _placer.slots[int(_placer.ghost)]    # the ghost honoured
	var gc: int = _m.defense_list.size()
	_press("KeyM")
	if _m.defense_list.size() != gc + 1 \
				or (_m.defense_list[gc] as Dictionary)["obj"].pos != want \
				or bool(_panel.armed):
		_fail("KEYMA leg: armed KeyM did not place at the ghost slot")
		return
	print("G5B-KEYMA count=%d at_ghost=1 disarmed=1" \
			% _m.defense_list.size())
	# ---- KeyM UNARMED: the legacy first-free instant place, unchanged ----
	var f0: int = _placer.first_free()
	var want2 = _placer.slots[f0]
	var gc2: int = _m.defense_list.size()
	_press("KeyM")
	if _m.defense_list.size() != gc2 + 1 \
				or (_m.defense_list[gc2] as Dictionary)["obj"].pos != want2 \
				or bool(_panel.armed):
		_fail("KEYMU leg: legacy unarmed KeyM place moved (first-free)")
		return
	print("G5B-KEYMU count=%d first_free=1 armed=0" \
			% _m.defense_list.size())


# One discrete relay code through the SHIPPED bridge + one real step (5)
# drain (the smoke KeyM idiom: down, up, step).
func _press(code: String) -> void:
	_m.bridge.on_key(code, true)
	_m.bridge.on_key(code, false)
	_m.step(DT)


# A held-key RISING EDGE through the relay: down, one step (the panel
# cycles on that poll), up.
func _hold(code: String) -> void:
	_m.bridge.on_key(code, true)
	_m.step(DT)
	_m.bridge.on_key(code, false)
	_m.step(DT)


func _fail(why: String) -> void:
	_failed = true
	print("G5B-FAIL " + why)
	quit(1)
