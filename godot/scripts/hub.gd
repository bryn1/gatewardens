extends Control

# hub — War Table + station wiring (Modules row scripts/hub.gd,
# MC 11274.1.16 / card 11323; supersedes the W5 router-target placeholder
# honestly — the pinned setup(tables, game_state, save_store, bridge,
# rng) injection is kept verbatim, main.gd's router handoff unchanged).
# The hub mounts the five station panels the pinned rows name —
# war_table (mission select: the panel's start calls main.start_mission
# (map_id, difficulty), the difficulty riding the already-shipped mission
# routing), gear_panel_ui, blacksmith_ui, tinkerer_ui and dummy_range —
# one open at a time, hub landing open on the War Table (greybox default,
# declared).
#
# Input (pinned row: keyboard/mouse via the bridge model): _process
# drains the GWBridge relay once per frame (the mission step (5) owns the
# queue in-mission; in the hub the hub IS the drainer — only one routed
# scene is mounted at a time, so no second pump exists) and routes the
# codes the W4 relay already ships; the Button press signals are the
# mouse path (native GUI clicks on desktop and web). No new bridge codes
# are invented. Greybox bindings (declared, defense_panel precedent):
# Digit1 War Table, Digit2 Gear, Digit3 Blacksmith, Digit4 Tinkerer,
# KeyE Dummies, Escape closes.
#
# Declared reading: the pinned row's 3D tavern room with proximity NPC
# zones is the scene/frontend layer ("HUD + hot-swap deck UI", the
# greybox precedent of W6–W8); the W9 machine-verifiable deliverable is
# the station wiring below, which the hub_probe drives through the real
# scene and real panels (E5: _ready stays the router-safe no-op, the
# mission.gd precedent — everything builds in setup() after injection).

const WAR_TABLE := preload("res://scripts/war_table.gd")
const GEAR_PANEL := preload("res://scripts/gear_panel_ui.gd")
const BLACKSMITH_UI := preload("res://scripts/blacksmith_ui.gd")
const TINKERER_UI := preload("res://scripts/tinkerer_ui.gd")
const DUMMY_RANGE := preload("res://scripts/dummy_range.gd")

# Bridge relay code -> station (Escape maps to "": closes every panel).
const STATION := {"Digit1": "war", "Digit2": "gear", "Digit3": "blacksmith",
	"Digit4": "tinkerer", "KeyE": "dummies", "Escape": ""}

var tables = null   # GWTables by injection (R3/C1 — no autoloads)
var state = null    # GWGameState
var save = null     # GWSaveStore
var bridge = null   # GWBridge
var rng = null      # main.gd's ONE runtime RNG (F2-2)

var war = null
var gear = null
var blacksmith = null
var tinkerer = null
var dummies = null
var _panels: Dictionary = {}
var _status = null


func _ready() -> void:
	# No-op by contract: the router fires _ready at add_child BEFORE the
	# setup() injection, so nothing here may read injected deps (E5).
	return


func setup(tables_in, game_state, save_store, bridge_in, rng_in) -> void:
	tables = tables_in
	state = game_state
	save = save_store
	bridge = bridge_in
	rng = rng_in
	var box := VBoxContainer.new()
	box.name = "Stations"
	add_child(box)
	var title := Label.new()
	title.text = "GATEWARDENS — HUB"
	box.add_child(title)
	_status = Label.new()
	_status.name = "Meta"
	box.add_child(_status)
	var bar := HBoxContainer.new()
	bar.name = "Bar"
	box.add_child(bar)
	for entry: Array in [["war", "War Table"], ["gear", "Gear"],
			["blacksmith", "Blacksmith"], ["tinkerer", "Tinkerer"],
			["dummies", "Dummies"]]:
		var b := Button.new()
		b.name = "Open_" + String(entry[0])
		b.text = String(entry[1])
		b.pressed.connect(_open.bind(String(entry[0])))
		bar.add_child(b)
	# The five station panels (pinned rows), each fed only injected deps.
	war = WAR_TABLE.new()
	war.name = "WarTable"
	add_child(war)
	war.setup(get_parent(), tables)     # get_parent() IS main at runtime
	gear = GEAR_PANEL.new()
	gear.name = "GearPanel"
	add_child(gear)
	gear.setup(tables, state)
	blacksmith = BLACKSMITH_UI.new()
	blacksmith.name = "Blacksmith"
	add_child(blacksmith)
	blacksmith.setup(tables, state, rng)
	tinkerer = TINKERER_UI.new()
	tinkerer.name = "Tinkerer"
	add_child(tinkerer)
	tinkerer.setup(tables, state, rng)
	dummies = DUMMY_RANGE.new()
	dummies.name = "DummyRange"
	add_child(dummies)
	dummies.setup(tables, state, rng)
	_panels = {"war": war, "gear": gear, "blacksmith": blacksmith,
		"tinkerer": tinkerer, "dummies": dummies}
	state.mutated.connect(_refresh_status)
	_open("war")


func _process(_delta: float) -> void:
	if bridge == null:
		return
	for code: Variant in bridge.drain_presses():
		handle_press(String(code))


# One relayed bridge code -> the station route (greybox bindings header).
func handle_press(code: String) -> void:
	if not STATION.has(code):
		return
	_open(String(STATION[code]))


func _open(which: String) -> void:
	for key: String in _panels:
		_panels[key].visible = key == which
	_refresh_status()


func _refresh_status() -> void:
	var parts: Array[String] = []
	for id: String in state.materials:
		parts.append("%s x%d" % [id, int(state.materials[id])])
	_status.text = "gold %d | bank %d | deck %d | %s" % [
			int(state.gold), int(state.bank.size()), int(state.deck.size()),
			", ".join(parts)]
