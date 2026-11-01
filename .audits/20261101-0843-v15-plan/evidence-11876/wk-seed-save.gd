extends SceneTree
# W-K served-leg SEED (MC 11876): produce a REAL shipped-format save
# (GWSaveStore atomic write through the GWCompose mutated->save wiring,
# shipped C13 mutators only — P7 probe seed shape for the kit rows).
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const DECK := ["warden", "deadeye", "embercaller"]

var tables = null
var state = null

func _fail(why: String) -> void:
	print("SEED-FAIL " + why)
	quit(1)

func _kit(base_id: String) -> Dictionary:
	var base: Dictionary = {}
	for row: Dictionary in tables.rows("items"):
		if String(row.get("id", "")) == base_id:
			base = row
	if base.is_empty():
		_fail("no items.json kit row " + base_id)
		return {}
	return {
		"uid": 0,
		"base_id": String(base["id"]),
		"slot": String(base["slot"]),
		"rarity": "powerful",
		"ilvl": 3,
		"primary": {"stat": String(base["primary"]), "value": 3.0},
		"secondary": null,
		"atk_speed": float(base["roll_ranges"]["atk_speed"][0]),
		"shot_type": null,
		"proj_count": int(base["roll_ranges"]["proj_count"][0]),
		"mods": [],
		"upgraded": 0,
	}

func _init() -> void:
	tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	state = graph["state"]
	state.set_deck(DECK.duplicate())
	state.bank_add(_kit("orb_of_the_deep"))
	state.bank_add(_kit("mark_of_fervor"))
	print("SEED ack=%d bank=%d path=%s" % [int(state.saved_ack),
			int(state.bank.size()), OS.get_user_data_dir()])
	quit(0)
