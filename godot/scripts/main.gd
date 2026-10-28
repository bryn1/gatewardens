# App root + scene router (Modules row scripts/main.gd; MC 11274.1.12 /
# card 11304 — replaces the W1 scaffold placeholder). Composition root:
# _ready builds GWTables (load_dir via ctor), boot fail-fast on any
# missing pinned table (printerr BOOT_VALIDATE_FAIL + quit(1), F16 — the
# stem list is READ from GWTables.STEMS, never duplicated here), calls
# the ONE wiring site GWCompose.build_graph (F2-5 — state/save/bridge
# construction + the C13 wiring live there, not here), loads the user://
# save through from_save (I5), and owns the runtime RNG: seeded ONCE
# from OS entropy at _ready (F2-2), handed to routed scenes through
# their setup() params.
#
# Router (pinned row: hub <-> mission): the root Node persists and the
# routed scene mounts as a child — change_scene_to_file would destroy
# this composition root and the graph it owns. Title: the pinned scene
# list ships no title.tscn, so boot routes straight to hub (reading on
# the card trail). Mission target is the pinned res://scenes/mission.
# tscn; until the mission milestone lands it, routing falls back to the
# clearly-labeled NOT-BUILT stub — the pinned path stays a constant, so
# the real mission scene needs zero main.gd change.
#
# C5 push: every frame snapshot_json (mission fields subset, outcome/
# boss_hp/relics_assigned and the saved_ack mirror included — all
# assembled in game_state.gd) is pushed via the pinned bridge mechanism:
# JavaScriptBridge eval "window.__gwSnapshot="+… (main.gd:84 mechanism,
# renamed) behind the OS.has_feature("web") guard (the singleton exists
# off-web but is neutered — VERIFIED this gate) — and the same payload
# lands in the __GW_LAST_SNAPSHOT desktop readback. The web page's
# GW_STATE() accessor reads window.__gwSnapshot (web_shell.html).
# C13: NO second write trigger here — the mutated->write wiring is
# GWCompose's (W4); mission-local noise emits no mutated, so save
# commits stay meta-mutator + mission-end scoped.
#
# Readings (declared): the brief's "GWTables.validate" boot call cannot
# run — that static never shipped (W16 truth pass over sim_tables.gd);
# deep per-row schema validation lives in the pytest schema layer
# (tests/test_data_schemas.py), so the BOOT fail-fast is the
# table-presence check over STEMS below; the brief's "bridge.read_input()" paraphrase is the
# pinned forward-only relay: _unhandled_input maps events through
# bridge.native_code/mouse_code into bridge.on_key (no read_input
# method invented; bridge.gd untouched).
extends Node

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

const HUB_SCENE := "res://scenes/hub.tscn"
const MISSION_SCENE := "res://scenes/mission.tscn"
const MISSION_STUB := "res://scenes/mission_stub.tscn"
const DATA_DIR := "res://data"

var tables = null       # GWTables by injection (duck-typed door: .table)
var state = null        # GWGameState from GWCompose.build_graph
var save = null         # GWSaveStore
var bridge = null       # GWBridge
var rng := RandomNumberGenerator.new()   # sole runtime RNG (F2-2)

var mission = null      # routed mission node; null in the hub
var __GW_LAST_SNAPSHOT: String = ""   # desktop readback of the C5 push

var _routed = null              # current routed scene (child of root)
var _js_bridge = null           # JavaScriptBridge singleton; null off-web
var _js_relay = null            # keeps the gwHost callback alive (E1)
var _return_ctl = null          # F1 end-screen CanvasLayer (child of mission)
var _return_pending := false    # one route per end (DA F1 flush-edge guard)


func _ready() -> void:
	tables = GW_TABLES.new(DATA_DIR)   # load_dir over the pinned stems
	# Boot fail-fast (F16), FILE level per stem: the W3a dict door
	# deliberately drops array-shaped files (heroes/towers/enemies/
	# items/mods are row ARRAYS — game_state.gd header), so a
	# table(stem)-empty check would false-RED on healthy data. Missing
	# or unparsable JSON = dead-on-arrival boot; the deep per-row
	# validator is the pytest schema layer, never a boot call.
	for stem: String in GW_TABLES.STEMS:
		var text := FileAccess.get_file_as_string(DATA_DIR + "/" + stem \
				+ ".json")
		if text.is_empty() or JSON.parse_string(text) == null:
			printerr("BOOT_VALIDATE_FAIL table=%s" % stem)
			get_tree().quit(1)
			return
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	state = graph["state"]
	save = graph["save"]
	bridge = graph["bridge"]
	state.from_save(save.load_save())   # user:// save load on boot (I5)
	rng.randomize()                     # ONE OS-entropy seed (F2-2)
	# Web guard (E-fact discipline): off-web the JavaScriptBridge
	# singleton EXISTS but is NEUTERED (VERIFIED this gate: desktop
	# -s call -> "Nonexistent function 'get_object'" SCRIPT ERROR on
	# stderr) — existence is not the guard, the platform is.
	if OS.has_feature("web"):
		_js_bridge = Engine.get_singleton("JavaScriptBridge")
		_install_js_relay()
	open_hub()


# ---------- router — root persists, scenes mount as children ----------

func open_hub() -> void:
	# F1 teardown belt (plan boundary): a stale RETURN-TO-HUB control
	# cannot survive into the hub — _mount frees it with the mission
	# subtree, hide it here as the second guard.
	if _return_ctl != null and is_instance_valid(_return_ctl):
		_return_ctl.visible = false
	_return_pending = false
	mission = null
	_routed = _mount(HUB_SCENE)
	if _routed != null and _routed.has_method("setup"):
		_routed.setup(tables, state, save, bridge, rng)


func start_mission(map_id: String, difficulty: String) -> void:
	# war_table row crossing: main.start_mission(map_id, difficulty).
	var target := MISSION_SCENE
	if not ResourceLoader.exists(target):
		target = MISSION_STUB     # NOT-BUILT until the mission milestone
	_routed = _mount(target)
	mission = _routed
	# has_method guard: the NOT-BUILT stub is a script-less placeholder —
	# the real mission row's setup(...) is injected when it lands.
	if _routed != null and _routed.has_method("setup"):
		_routed.setup(tables, state, save, bridge, map_id, difficulty, rng)


func _mount(path: String):
	if _routed != null:
		remove_child(_routed)
		_routed.free()
	_routed = null
	var packed = ResourceLoader.load(path)
	if packed == null:
		printerr("ROUTE_FAIL missing=%s" % path)
		return null
	var node = packed.instantiate()
	add_child(node)
	_routed = node
	return node


# ---------- F1 return to base — END-ONLY (MC 11623) ----------
# Owner ruling 2026-10-28 verbatim "rec on all 3": NO mid-mission exit
# control ships; RETURN TO HUB exists on the victory AND defeat end
# screens only. Rides the ONE existing frame pump (_process); the
# control mounts UNDER the routed mission subtree (never a sibling of
# _routed), so _mount's remove_child+free tears it down with the
# mission (plan teardown boundary). The route reuses the ONE router
# entry open_hub() — the deferred form is hub.gd's shipped F-2 answer
# (free-inside-pressed-emit = engine error), not a second mechanism.

func _f1_end_screen() -> void:
	if mission == null or mission.outcome == null:
		return                 # END-ONLY: mid-mission the control does NOT exist
	if _return_ctl != null and is_instance_valid(_return_ctl):
		return
	var layer := CanvasLayer.new()
	layer.name = "EndReturn"
	var btn := Button.new()
	btn.name = "ReturnToHub"
	btn.text = "RETURN TO HUB"
	btn.anchor_left = 0.5
	btn.anchor_right = 0.5
	btn.anchor_top = 1.0
	btn.anchor_bottom = 1.0
	btn.offset_left = -120.0
	btn.offset_right = 120.0
	btn.offset_top = -88.0
	btn.offset_bottom = -48.0   # bottom-center, over the outcome banner
	btn.pressed.connect(_return_to_hub)
	layer.add_child(btn)
	mission.add_child(layer)   # under the routed mission: freed WITH it
	_return_ctl = layer


func _return_to_hub() -> void:
	if mission == null or mission.outcome == null:
		return                 # Invalid leg: the click path refuses
	if _return_pending:
		return                 # DA F1 edge: click during the flush — once only
	_return_pending = true
	open_hub.call_deferred()   # F-2: the route lands outside the pressed emit


# ---------- input — pinned forward-only relay into the bridge ----------

func _unhandled_input(event: InputEvent) -> void:
	if bridge == null:
		return
	var key := event as InputEventKey
	if key != null:
		_forward(bridge.native_code(key.physical_keycode), key.pressed)
		return
	var button := event as InputEventMouseButton
	if button != null:
		_forward(bridge.mouse_code(button.button_index), button.pressed)


func _forward(code: String, down: bool) -> void:
	if code != "":
		bridge.on_key(code, down)


# ---------- C5 snapshot push ----------

func _process(_delta: float) -> void:
	push_snapshot()
	_f1_end_screen()   # END-ONLY return control (built only once outcome != null)


func push_snapshot() -> void:
	if state == null:
		return
	var snap: String = state.snapshot_json(mission)
	__GW_LAST_SNAPSHOT = snap
	if _js_bridge != null:
		_js_bridge.call("eval", "window.__gwSnapshot=" + snap, true)


# JS -> GDScript input relay, installed once at boot (4.7 mechanism:
# create_callback; Godot 3's register() AND get_object() are gone — W17d
# measured get_object ABSENT from the shipped 4.7.2 ClassDB, so the old
# call errored and gwHost.on_key never installed: the dead served
# keyboard). 4.7's get_interface(name) returns a transparent JS proxy:
# every METHOD call on it routes to the JS side (host.set(...) never
# assigns), so the callback installs through the PROPERTY path —
# host.on_key = _js_relay, on an UNTYPED host var (dynamic by design).
# VERIFIED live (4.7.2 wasm + shipped shell, card 11396): keydown/keyup
# reach _on_js_key as one Array [code:String, down:bool]; the JS call
# returns null synchronously — this engine has no .dispatch, no promise.
# E1 anchor is load-bearing, not ceremony: a relay held only in a local
# died at _ready return and the JS side no-op'd silently (measured).
func _install_js_relay() -> void:
	if _js_bridge == null:
		return
	_js_relay = _js_bridge.call("create_callback", _on_js_key)
	_js_bridge.call("eval", "window.gwHost = window.gwHost || {};", true)
	var host = _js_bridge.call("get_interface", "gwHost")
	if host != null and _js_relay != null:
		host.on_key = _js_relay


func _on_js_key(args: Array) -> void:
	if bridge != null and args.size() >= 2:
		bridge.on_key(String(args[0]), bool(args[1]))
