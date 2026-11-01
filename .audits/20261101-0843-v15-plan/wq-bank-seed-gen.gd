extends SceneTree
const SimLoot = preload("res://sim/sim_loot.gd")
func _init():
	var tables := {}
	tables["rarity"] = JSON.parse_string(FileAccess.get_file_as_string("res://data/rarity.json"))
	var bases: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/items.json"))
	tables["mods"] = JSON.parse_string(FileAccess.get_file_as_string("res://data/mods.json"))
	tables["items"] = bases
	var rng := RandomNumberGenerator.new(); rng.seed = 424242
	var items: Array = []
	var ladder: Array = tables["rarity"]["ladder"]
	var uid := 1
	for i in ladder.size():
		var base: Dictionary = bases[i % bases.size()]
		var row: Dictionary = SimLoot.roll_item(base, String(ladder[i]), tables, rng)
		row["uid"] = uid; uid += 1
		items.append(row)
	var cfg := ConfigFile.new()
	cfg.set_value("meta", "schema_version", 1)
	cfg.set_value("meta", "asc_earned", 0); cfg.set_value("meta", "asc_spent_json", "[]")
	cfg.set_value("bank", "items_json", JSON.stringify(items))
	var err := cfg.save("/tmp/gw-bank-seed/seed.cfg")
	print("SAVERC=", err, " ROWS=", items.size())
	quit(0)
