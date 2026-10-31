# g6_zoom_relay_probe — the v1.3 ZOOM served-path leg (v1.3 zoom Z3,
# MC 11817; ZOOM_SPEC §1/§5 A4/§6 S4, the DA-verdict-c2 SHIP gate).
# The g5_real_relay_probe idiom, EXTENDED: boots the REAL mission scene
# (now WITH the mounted CameraZoom node — the leg only passes because
# the scene carries it), mounts the REAL main.gd script as a relay
# object (_ready NEVER runs — no app boot; only bridge is needed) and
# feeds SYNTHESIZED InputEventMouseButtons. The WHEEL ticks go through
# the REAL tree path (root.push_input — the shipped W17b viewport-push
# idiom of v1_world_shot/test_hub_scroll) so the MOUNTED zoom node's OWN
# _unhandled_input + per-frame edge guard run; the PLACE leg's confirm
# rides the shipped slot-cycle route (arm -> KEY_RIGHT cycle -> MouseLeft
# through main's relay -> the ONE pump -> place_id at the ghost).
# Rows (G6-*):
#  WHEELIN   one WHEEL_UP tick = EXACTLY one step toward the map, read
#            back to the default (measured after WHEELOUT: a tick IN
#            from the default lands 55.909 and sits ON the 56.0 floor
#            at once, so the clean unclamped -8 reads coming back in).
#  WHEELOUT  one synthesized WHEEL_DOWN tick = EXACTLY one step out
#            (d = default + ZOOM_STEP) — measured first.
#  DEDUP     BOTH clauses of the §1 press-only + per-tick edge guard:
#            the same tick fed TWICE inside ONE engine frame = ONE step
#            (dup=1, the served 19715d4 double-feed shape); the same
#            button on TWO distinct frames = TWO steps (distinct=2 —
#            the guard never eats real input).
#  BOUNDSMIN repeated WHEEL_UP clamps at D_MIN 56.0 and HOLDS under a
#            further tick (value quoted from the engine).
#  BOUNDSMAX repeated WHEEL_DOWN clamps at D_MAX 128.0 and HOLDS (order
#            of ticks irrelevant — the floor was just visited).
#  PLACE     at D_MAX (then again at D_MIN): arm the tower row, cycle the
#            ghost (shipped idiom), relay MouseLeft -> tower count +1 at
#            the ghost slot, id=ballista (the §5 A3 producing rows —
#            placement is zoom-invariant by construction, this measures
#            it anyway).
# Any failed check prints G6-FAIL <detail> + rc1; the last row is G6-OK.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MAIN := preload("res://scripts/main.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const DT := 0.05
const WHEEL_AT := Vector2(640, 400)  # over the play area (spec §1)

var _failed := false
var _f := 0
var _m = null
var _panel = null
var _placer = null
var _main = null          # the REAL main.gd relay object (no _ready)
var _rig: Node3D = null
var _zoom: Node = null    # the MOUNTED zoom node (the scene carries it)
var _d0 := 0.0
var _d := 0.0
var _dupd := 0.0


func _init() -> void:
	root.size = Vector2i(1280, 720)
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	graph["state"].set_deck(DECK.duplicate())
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()
	var rng := RandomNumberGenerator.new()
	rng.seed = 11817
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
	_zoom = m.get_node_or_null("CameraRig/CameraZoom")
	if _zoom == null:
		_fail("CameraZoom not mounted under CameraRig in the scene")
		return
	_rig = m.get_node("CameraRig") as Node3D
	_main = MAIN.new()                 # script instance; NEVER add_child:
	_main.bridge = graph["bridge"]     # _ready would boot the whole app


# One physical wheel tick: the g5_real_relay_probe._mouse press+release
# pair, dispatched through the REAL tree path so the mounted node's own
# _unhandled_input runs (the served input path, W17b push_input idiom).
func _wheel(up: bool) -> void:
	for down: bool in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_WHEEL_UP if up \
				else MOUSE_BUTTON_WHEEL_DOWN
		ev.pressed = down
		ev.position = WHEEL_AT
		ev.global_position = WHEEL_AT
		root.push_input(ev)


func _dist() -> float:
	return _rig.position.length()


func _near(a: float, b: float) -> bool:
	return absf(a - b) < 0.01


# ---------- g5 verbatim relay helpers (the PLACE leg's confirm) --------

func _key(kc: int) -> void:
	_key_press(kc, true)
	_m.step(DT)
	_key_press(kc, false)
	_m.step(DT)


func _key_press(kc: int, down: bool) -> void:
	var ev := InputEventKey.new()
	ev.physical_keycode = kc
	ev.keycode = kc
	ev.pressed = down
	_main._unhandled_input(ev)


func _mouse(btn_idx: int) -> void:
	for down: bool in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = btn_idx
		ev.pressed = down
		_main._unhandled_input(ev)
	_m.step(DT)


# The shipped slot-cycle confirm idiom at the CURRENT distance: arm the
# tower row (production picker press), cycle the ghost one forward over
# buildable() (relayed KEY_RIGHT), relay MouseLeft -> confirm places ONE
# at the ghost slot. Asserts the +1 and the row id.
func _place(leg: String) -> void:
	var btn = _panel.class_buttons.get("tower")
	if btn == null:
		_fail("%s leg: class_buttons has no tower row" % leg)
		return
	var c0: int = _m.defense_list.size()
	btn.pressed.emit()
	if not bool(_panel.armed):
		_fail("%s leg: arm failed" % leg)
		return
	var free: Array = _placer.buildable()
	if free.size() < 2:
		_fail("%s leg: fewer than 2 buildables to cycle" % leg)
		return
	_key(KEY_RIGHT)
	if int(_placer.ghost) != int(free[1]):
		_fail("%s leg: ghost=%d, wanted %d after a relayed KEY_RIGHT" \
				% [leg, int(_placer.ghost), int(free[1])])
		return
	var want = _placer.slots[_placer.ghost]
	_mouse(MOUSE_BUTTON_LEFT)
	if _m.defense_list.size() != c0 + 1:
		_fail("%s leg: count %d, wanted %d (zoom-invariance broken?)" \
				% [leg, _m.defense_list.size(), c0 + 1])
		return
	var obj = (_m.defense_list[c0] as Dictionary)["obj"]
	if obj.pos != want or String(obj.trow["id"]) != "ballista":
		_fail("%s leg: placed %s at %s, wanted ballista at ghost %s" \
				% [leg, String(obj.trow["id"]), str(obj.pos), str(want)])
		return
	print("G6-PLACE d=%.6f count=%d delta=1 id=ballista" \
			% [_dist(), _m.defense_list.size()])


func _fail(why: String) -> void:
	_failed = true
	print("G6-FAIL " + why)
	quit(1)


# act/assert ordering per Z2: every tick in its own _process frame (the
# edge guard's declared frame source), every assert in the NEXT frame.
func _process(_delta: float) -> bool:
	if _failed:
		return true
	_f += 1
	if _f == 1:
		_d0 = _dist()
		if not _near(_d0, 63.909195):
			_fail("default rig row d=%.6f, wanted |origin| ~ 63.9092" % _d0)
			return true
		_wheel(false)                   # WHEELOUT first, ONE tick out:
		                                #   a tick IN from the default
		                                #   lands 55.909 and sits ON the
		                                #   56.0 floor at once (Z2 CAP/
		                                #   STEP math), so the clean
		                                #   unclamped -8 reads on the
		                                #   WHEELIN leg back to default
	elif _f == 2:
		_d = _dist()
		if not _near(_d, _d0 + 8.0):
			_fail("WHEELOUT d=%.6f, wanted %.6f (exactly one step out)" \
					% [_d, _d0 + 8.0])
			return true
		print("G6-WHEELOUT steps=1 d=%.6f" % _d)
		_wheel(true)                    # WHEELIN: one tick toward the map
	elif _f == 3:
		_d = _dist()
		if not _near(_d, _d0):
			_fail("WHEELIN d=%.6f, wanted default %.6f (exactly one " \
					+ "step in)" % [_d, _d0])
			return true
		print("G6-WHEELIN steps=1 d=%.6f" % _d)
		_wheel(false)                   # DEDUP clause 1: the SAME tick
		_wheel(false)                   #   fed TWICE, SAME engine frame
	elif _f == 4:
		_d = _dist()
		if not _near(_d, _d0 + 8.0):
			_fail("DEDUP same-frame double-feed stepped d=%.6f, wanted " \
					+ "one step %.6f" % [_d, _d0 + 8.0])
			return true
		_dupd = _d
		_wheel(false)                   # clause 2: a NEW frame = a real
		                                #   second tick -> two steps
	elif _f == 5:
		_d = _dist()
		if not _near(_d, _d0 + 16.0):
			_fail("DEDUP two distinct frames stepped d=%.6f, wanted two " \
					+ "steps %.6f" % [_d, _d0 + 16.0])
			return true
		print("G6-DEDUP dup=1 distinct=2 d=%.6f" % _d)
		_wheel(true)                    # head for the floor
	elif _f >= 6 and _f <= 7:
		_wheel(true)                    # 2 more UP ticks: the 3rd lands
		                                #   on the 56.0 clamp
	elif _f == 8:
		_wheel(true)                    # one MORE up AT the floor
	elif _f == 9:
		_d = _dist()
		if not _near(_d, 56.0):
			_fail("BOUNDSMIN floor d=%.6f, wanted D_MIN 56.0" % _d)
			return true
		print("G6-BOUNDSMIN d=%.6f held=1" % _d)
		_wheel(false)                   # traverse to the ceiling
	elif _f >= 10 and _f <= 17:
		_wheel(false)                   # 8 more DOWN ticks land exactly
		                                #   on the 128.0 ceiling
	elif _f == 18:
		_wheel(false)                   # one MORE down AT the ceiling
	elif _f == 19:
		_d = _dist()
		if not _near(_d, 128.0):
			_fail("BOUNDSMAX ceiling d=%.6f, wanted D_MAX 128.0" % _d)
			return true
		print("G6-BOUNDSMAX d=%.6f held=1" % _d)
		_place("PLACE")                 # A3 producing row AT zoomed-OUT
		_wheel(true)                    # traverse to the floor
	elif _f >= 20 and _f <= 27:
		_wheel(true)                    # 8 more UP ticks land exactly 56
	elif _f == 28:
		_d = _dist()
		if not _near(_d, 56.0):
			_fail("PLACE-at-min distance d=%.6f, wanted 56.0" % _d)
			return true
		_place("PLACE-min")             # A3's also-run-at-D_MIN clause
	elif _f == 29:
		_main.free()                    # a Node: un-freed it leaks onto
		                                # stderr (EMPTY-stderr ruling)
		print("G6-OK")
		quit(0)
	return false
