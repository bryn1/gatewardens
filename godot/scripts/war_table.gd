extends Control

# war_table — mission select panel (Modules row scripts/war_table.gd,
# MC 11274.1.16 / card 11323): map + difficulty + start, and the pinned
# crossing is verbatim — start calls main.start_mission(map_id,
# difficulty), the W5 router leg that mounts res://scenes/mission.tscn
# and injects the difficulty (zero main.gd change; R4 ships the ONE map
# Gatefall, and the buttons are DERIVED, not hardcoded: the map list is
# every GWTables.STEMS entry "maps/<id>" whose table door loaded, and a
# map's difficulties are the "waves/waves_<id>_<difficulty>" stems —
# data-driven per R4's map-count ruling, no invented title scene).
#
# The router arrives as the setup() parameter the hub passes from
# get_parent() — at runtime that IS the main.gd root (main._mount adds
# the routed scene under itself); the hub_probe drives the same crossing
# through a recorder stub, which is what asserts the call shape.

const GW_TABLES := preload("res://sim/sim_tables.gd")

var router = null
var maps: Array = []      # [{id:String, difficulties:Array}] from STEMS


func setup(router_in, tables) -> void:
	router = router_in
	maps = _declared_maps(tables)
	var box := VBoxContainer.new()
	box.name = "WarTable"
	add_child(box)
	var title := Label.new()
	title.text = "WAR TABLE"
	box.add_child(title)
	for entry: Dictionary in maps:
		for difficulty: Variant in entry["difficulties"]:
			var b := Button.new()
			b.name = "Start_%s_%s" % [String(entry["id"]), String(difficulty)]
			b.text = "Start %s — %s" % [String(entry["id"]), String(difficulty)]
			b.pressed.connect(start.bind(String(entry["id"]), String(difficulty)))
			box.add_child(b)


# The pinned row's crossing, called by the buttons and the probe.
func start(map_id: String, difficulty: String) -> void:
	router.start_mission(map_id, difficulty)


func _declared_maps(tables) -> Array:
	var out: Array = []
	for stem: String in GW_TABLES.STEMS:
		if not stem.begins_with("maps/") or tables.table(stem).is_empty():
			continue
		var map_id := stem.trim_prefix("maps/")
		var prefix := "waves/waves_" + map_id + "_"
		var diffs: Array = []
		for wstem: String in GW_TABLES.STEMS:
			if wstem.begins_with(prefix):
				diffs.append(wstem.trim_prefix(prefix))
		out.append({"id": map_id, "difficulties": diffs})
	return out
