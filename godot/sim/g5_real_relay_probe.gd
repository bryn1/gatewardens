# g5_real_relay_probe — the G5 SERVED-PATH leg (v1.2.1 follow-up,
# MC card 11700 / orchestrator served-browser result). The g5 kit proves
# the mechanism when codes are handed to the bridge directly; the LIVE
# browser reaches the bridge through main.gd: InputEventKey/MouseButton
# -> _unhandled_input -> native_code/mouse_code -> on_key (desktop + the
# engine's own web pipeline), and window.gwHost.on_key -> _on_js_key ->
# on_key (the served shell's JS relay). This kit boots the REAL mission,
# mounts the REAL main.gd script as a relay object (_ready NEVER runs —
# no app boot; only bridge is needed) and feeds it SYNTHESIZED
# InputEvents: the closest production analogue runnable under -s.
# Rows (G5R-*):
#  ARM     GUI row press arms, places NOTHING (count 0).
#  KEYM    a real InputEventKey(KEY_M) through main's _unhandled_input
#          confirms the armed row: +1 exactly at the ghost, disarmed.
#  DEDUP   ONE physical press fed TWICE (engine _unhandled_input + the
#          JS relay _on_js_key — the served 19715d4 double-feed that
#          placed TWO from one KeyM) now places EXACTLY ONE.
#  LMB     InputEventMouseButton(LEFT) through the relay confirms: +1,
#          disarmed (ghost -1).
#  RMB     MOUSE_BUTTON_RIGHT cancels: armed 0, ghost -1, count kept.
#  CYCLE   InputEventKey(KEY_RIGHT) cycles the ghost forward over
#          buildable() (held relay, rising edge).
#  LOCK    combat phase: picker rows DISABLED (affordable green — the
#          gate is the PHASE, W17e sync), a forced emit cannot stay
#          armed, and the relayed confirm places NOTHING (place_id's
#          own phase refusal, second belt).
#  UNLOCK  back to build: the rows light up again (afford + phase true).
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MAIN := preload("res://scripts/main.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const DT := 0.05

var _failed := false
var _frames := 0
var _m = null
var _panel = null
var _placer = null
var _main = null          # the REAL main.gd relay object (no _ready)


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
	rng.seed = 11700
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
	_main = MAIN.new()                 # script instance; NEVER add_child:
	_main.bridge = graph["bridge"]     # _ready would boot the whole app


func _process(_delta: float) -> bool:
	if _failed:
		return true
	_frames += 1
	if _frames == 4:
		_legs()
		_main.free()                    # a Node: un-freed it leaks onto
		                                # stderr (EMPTY-stderr ruling)
		if not _failed:
			print("G5R-OK")
			quit(0)
	return false


func _legs() -> void:
	var btn = _panel.class_buttons.get("tower")
	if btn == null:
		_fail("class_buttons has no tower row")
		return
	# ---- ARM through the GUI signal (production picker press) ----
	var c0: int = _m.defense_list.size()
	btn.pressed.emit()
	if _m.defense_list.size() != c0 or not bool(_panel.armed):
		_fail("ARM leg: press placed/armed wrong")
		return
	print("G5R-ARM armed=1 count=%d" % c0)

	# ---- KEYM armed, through the REAL _unhandled_input forwarder ----
	var g0 := int(_m.green)
	var want = _placer.slots[_placer.ghost]
	_key(KEY_M)
	if _m.defense_list.size() != c0 + 1 \
			or (_m.defense_list[c0] as Dictionary)["obj"].pos != want \
			or bool(_panel.armed):
		_fail("KEYM leg: real-forwarder KeyM did not confirm at the ghost")
		return
	print("G5R-KEYM count=%d green_drop=%d disarmed=1" \
			% [_m.defense_list.size(), g0 - int(_m.green)])

	# ---- DEDUP: the served web double-feed = ONE action ----
	btn.pressed.emit()
	if not bool(_panel.armed):
		_fail("DEDUP leg: re-arm before the double-feed failed")
		return
	var c1: int = _m.defense_list.size()
	# one physical press, both live paths: engine + JS relay, both edges
	_key_press(KEY_M, true)
	_main._on_js_key(["KeyM", true])
	_key_press(KEY_M, false)
	_main._on_js_key(["KeyM", false])
	_m.step(DT)
	if _m.defense_list.size() != c1 + 1:
		_fail("DEDUP leg: double-feed placed %d (planned: exactly 1)"
				% (_m.defense_list.size() - c1))
		return
	print("G5R-DEDUP placed=%d" % (_m.defense_list.size() - c1))

	# ---- LMB through the mouse arm of the SAME forwarder ----
	btn.pressed.emit()
	var c2: int = _m.defense_list.size()
	var g1 := int(_m.green)
	_mouse(MOUSE_BUTTON_LEFT)
	if _m.defense_list.size() != c2 + 1 or bool(_panel.armed) \
			or int(_placer.ghost) != -1 \
			or g1 - int(_m.green) <= 0:
		_fail("LMB leg: relayed MouseLeft did not confirm exactly once")
		return
	print("G5R-LMB count=%d green_drop=%d disarmed=1 ghost=-1" \
			% [_m.defense_list.size(), g1 - int(_m.green)])

	# ---- RMB cancels through the same mouse arm ----
	btn.pressed.emit()
	if not bool(_panel.armed):
		_fail("RMB leg: re-arm before cancel failed")
		return
	var c3: int = _m.defense_list.size()
	_mouse(MOUSE_BUTTON_RIGHT)
	if bool(_panel.armed) or int(_placer.ghost) != -1 \
			or _m.defense_list.size() != c3:
		_fail("RMB leg: relayed MouseRight did not cancel")
		return
	print("G5R-RMB armed=0 ghost=-1 count=%d" % c3)

	# ---- CYCLE: a real InputEventKey(KEY_RIGHT) walks the ghost ----
	btn.pressed.emit()
	var free: Array = _placer.buildable()
	if free.size() < 2 or int(_placer.ghost) != int(free[0]):
		_fail("CYCLE leg: ghost not on the first buildable after arm")
		return
	_key(KEY_RIGHT)
	if int(_placer.ghost) != int(free[1]):
		_fail("CYCLE leg: ghost=%d, wanted %d after a real KEY_RIGHT"
				% [int(_placer.ghost), int(free[1])])
		return
	print("G5R-CYCLE fwd=%d" % int(free[1]))
	_panel._cancel_arm()

	# ---- LOCK: combat disables the rows WHILE AFFORDABLE (the served
	# trap: rows stayed live into combat and silently refused) ----
	_m.green = g1 + 300                     # afford true: phase is the gate
	_m.phase_kind = "combat"
	_m.step(DT)                             # one poll -> W17e sync
	btn.pressed.emit()                      # a stuck GUI press attempt
	_m.step(DT)
	var c4: int = _m.defense_list.size()
	_mouse(MOUSE_BUTTON_LEFT)               # relayed confirm in combat
	if not bool(btn.disabled) or bool(_panel.armed) \
			or _m.defense_list.size() != c4:
		_fail("LOCK leg: combat rows not locked (dis=%s armed=%s)"
				% [str(bool(btn.disabled)), str(bool(_panel.armed))])
		return
	print("G5R-LOCK disabled=1 armed=0 placed=0")

	# ---- UNLOCK: build again -> the rows answer ----
	_m.phase_kind = "build"
	_m.step(DT)
	if bool(btn.disabled):
		_fail("UNLOCK leg: rows stayed disabled back in build")
		return
	btn.pressed.emit()
	if not bool(_panel.armed):
		_fail("UNLOCK leg: armed route dead after unlock")
		return
	print("G5R-UNLOCK disabled=0 armed=1")


# ---------- real-input feed helpers (production analogue) ----------

# One physical key held DOWN through one real step (5) pump, then the
# keyup: press codes queue on the down edge, but HELD-based readers (the
# ghost arrows) must be observed WHILE held — the real browser frames
# sit between the edges.
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


func _fail(why: String) -> void:
	_failed = true
	print("G5R-FAIL " + why)
	quit(1)
