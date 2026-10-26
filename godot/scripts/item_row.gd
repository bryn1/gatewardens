extends Button

# item_row — the shared list-row widget (F2-12 pinned pair: this script
# on scenes/item_row.tscn; MC 11274.1.16 / card 11323). ONE list-build
# concern, ONE implementation: the gear bank list AND the blacksmith /
# tinkerer item pickers instantiate this scene — no panel re-renders a
# row (source-truth-gated in tests/test_hub.py). show_item(item,selected)
# is the pinned interface; picked(uid) is the pinned signal; the script
# stays class-less on the scene (the pinned row's wording).
#
# Everything the row paints comes from its OWN C9 item row: the name
# leg is the base_id, the stat lines are primary/secondary (weapon
# extras on line two), the mod line lists the rolled mods, and the
# relic badge marks slot=="relic" tower gear (C11 — never hero-worn;
# SimInventory.equip refuses it, the bank still shows it).
#
# Rarity tint (reading recorded on the card trail): the W9 brief reads
# rarity.json as carrying a colors ladder, but the shipped rarity.json
# (W2) has NO colors key and data files are outside this card's write
# scope — the row therefore binds the data door
# bind(tables) -> rarity["colors"]: a declared color string per rarity
# paints the swatch the moment that data row lands (BN3 extensibility,
# the same shape as chest_tiers), until then the swatch stays a NEUTRAL
# named grey. No hex literals and no invented palette anywhere here (I2).

signal picked(uid: int)

var uid := 0
var _colors: Dictionary = {}


func _init() -> void:
	# The Button press IS the pinned picked(uid) emit (mouse path; the
	# keyboard path calls picked handlers through the panels).
	pressed.connect(_on_pressed)


# Data door (declared extra over the pinned interface): the rarity
# colors map arrives from rarity.json through GWTables by injection
# (C1 — no autoload reads, no data mutation).
func bind(tables) -> void:
	_colors = {}
	if tables != null and tables.has_method("table"):
		_colors = tables.table("rarity").get("colors", {})


func show_item(item: Dictionary, selected: bool) -> void:
	uid = int(item.get("uid", 0))
	var rarity := String(item.get("rarity", ""))
	$NameLabel.text = "%s  [%s%s]" % [String(item.get("base_id", "")), rarity,
		" +%d" % int(item.get("upgraded", 0)) if int(item.get("upgraded", 0)) > 0 else ""]
	var lines: Array[String] = [_leg(item.get("primary"))]
	var secondary := _leg(item.get("secondary"))
	if secondary != "":
		lines.append(secondary)
	$StatLabel.text = "\n".join(lines)
	var extras: Array[String] = []
	if item.get("atk_speed") != null:
		extras.append("spd %.2f" % float(item["atk_speed"]))
	if item.get("shot_type") != null:
		extras.append(String(item["shot_type"]))
	if item.get("proj_count") != null:
		extras.append("proj %d" % int(item["proj_count"]))
	$ExtraLabel.text = "  ".join(extras)
	var names: Array[String] = []
	for mod: Variant in item.get("mods", []):
		names.append("%s@%s" % [String(mod["mod_id"]), String(mod["rarity"])])
	$ModLabel.text = ", ".join(names)
	$Badge.text = "RELIC" if String(item.get("slot", "")) == "relic" else ""
	$Tint.color = Color.from_string(String(_colors.get(rarity, "gray")),
			Color("gray"))
	self_modulate = Color("white") if selected else Color("darkgray")


func _leg(leg: Variant) -> String:
	if not (leg is Dictionary):
		return ""
	return "%s %s" % [str(leg["stat"]), str(leg["value"])]


func _on_pressed() -> void:
	picked.emit(uid)
