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
#
# W13 (MC 11274.1.22 / card 11332): F-1 the layout scheme is containers
# end to end (the A9 hub-overlap fix, setup() site), and F-2 the war
# table's start crossing is routed out of the pressed-signal frame
# (the A9 freed-during-emit console ERROR fix, _retarget_war_buttons).

const WAR_TABLE := preload("res://scripts/war_table.gd")
const GEAR_PANEL := preload("res://scripts/gear_panel_ui.gd")
const BLACKSMITH_UI := preload("res://scripts/blacksmith_ui.gd")
const TINKERER_UI := preload("res://scripts/tinkerer_ui.gd")
const DUMMY_RANGE := preload("res://scripts/dummy_range.gd")
const ASCENSION_UI := preload("res://scripts/ascension_ui.gd")

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
var ascension = null    # W14 leg 3 station (MC 11274.1.25 / card 11341)
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
	# F-1 (W13, MC 11274.1.22 / card 11332): the layout is CONTAINERS,
	# never origins. The hub root carries ONE layout child, a full-rect
	# VBox whose rows are the header ("Stations": title / Meta status /
	# station Bar) and the shared "PanelSlot" that carries the five
	# station panels — exactly one visible at a time (the shipped _open
	# model). A Container ASSIGNS its children's positions, so the
	# A9-finding overlap (title + stations + start entries all stacking at
	# (0,0)) is structurally impossible: nothing that reads is a bare
	# child of the origin any more. test_hub_layout.py enforces the
	# scheme engine-tier AND source-tier (stacking reintroduced = RED).
	var root_box := VBoxContainer.new()
	root_box.name = "Layout"
	root_box.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root_box)
	var box := VBoxContainer.new()
	box.name = "Stations"
	root_box.add_child(box)
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
			["dummies", "Dummies"], ["ascension", "Ascension"]]:
		var b := Button.new()
		b.name = "Open_" + String(entry[0])
		b.text = String(entry[1])
		b.pressed.connect(_open.bind(String(entry[0])))
		bar.add_child(b)
	var slot := VBoxContainer.new()
	slot.name = "PanelSlot"
	root_box.add_child(slot)
	# The five station panels (pinned rows), each fed only injected deps,
	# mounted into the shared slot — placed by the container, never by a
	# stacked origin (F-1 above).
	war = WAR_TABLE.new()
	war.name = "WarTable"
	slot.add_child(war)
	war.setup(get_parent(), tables)     # get_parent() IS main at runtime
	_retarget_war_buttons(war)          # F-2, below
	gear = GEAR_PANEL.new()
	gear.name = "GearPanel"
	slot.add_child(gear)
	gear.setup(tables, state)
	blacksmith = BLACKSMITH_UI.new()
	blacksmith.name = "Blacksmith"
	slot.add_child(blacksmith)
	blacksmith.setup(tables, state, rng)
	tinkerer = TINKERER_UI.new()
	tinkerer.name = "Tinkerer"
	slot.add_child(tinkerer)
	tinkerer.setup(tables, state, rng)
	dummies = DUMMY_RANGE.new()
	dummies.name = "DummyRange"
	slot.add_child(dummies)
	dummies.setup(tables, state, rng)
	# W14 leg 3 (MC 11274.1.25 / card 11341): the ascension spend station,
	# sixth panel in the same shared slot, opened from the bar (mouse path
	# — the Digit map above stays exactly as shipped, no new bridge codes).
	ascension = ASCENSION_UI.new()
	ascension.name = "Ascension"
	slot.add_child(ascension)
	ascension.setup(tables, state)
	_panels = {"war": war, "gear": gear, "blacksmith": blacksmith,
		"tinkerer": tinkerer, "dummies": dummies, "ascension": ascension}
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


# F-2 (W13, MC 11274.1.22 / card 11332): the served journey caught the
# console ERROR "Object was freed or unreferenced while a signal is being
# emitted from it" on the hub->mission switch — the Button.pressed emit
# was still on the stack when main._mount freed the hub subtree (the
# emitter's own ancestors). Engine's OWN remedy, the route-out-of-signal-
# frame form: the Start buttons keep war_table's EXACT crossing (its own
# start->router.start_mission callables, bound args untouched — this only
# re-schedules them), but the crossing lands at idle time, when nothing
# is emitting. One mechanism, hub-side: main.gd and war_table.gd stay
# verbatim, no second router. The shipped hub_probe WAR leg is
# unaffected — it drives war.start() directly (never the button), and
# the direct call stays synchronous (deferred flush under `-s` is
# VERIFIED to land only at loop exit, never before the probe's asserts).
func _retarget_war_buttons(panel: Control) -> void:
	var table := panel.get_node_or_null("WarTable")
	if table == null:
		return
	for child: Node in table.get_children():
		var b := child as Button
		if b == null:
			continue
		for c: Dictionary in b.pressed.get_connections():
			var fn: Callable = c["callable"]
			if fn.get_object() != panel:
				continue    # not the station's own crossing — leave it
			b.pressed.disconnect(fn)
			b.pressed.connect(_route_out_of_signal_frame.bind(fn))


func _route_out_of_signal_frame(fn: Callable) -> void:
	fn.call_deferred()


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
