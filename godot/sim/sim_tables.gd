class_name GWTables
extends RefCounted

# Data load + hold (C1): reads the pinned data-files table via FileAccess +
# JSON and keys every file by its res-relative stem under the data dir
# ("economy", "maps/gatefall", "waves/waves_gatefall_hard", ...).
# table(name) is the ONLY read door (name = file stem); map(id) is a REAL
# method (F16). Read-only doctrine (C1): consumers never mutate a loaded
# table and this class never writes into one. validate() lands with
# validate_probe (W5), not here. No Node/Engine refs (I6).

# The exact data set the ARCHITECTURE data-files table pins (W2 shipped it).
const STEMS: Array[String] = [
	"economy", "balance", "xp", "heroes", "towers", "enemies", "rarity",
	"items", "mods", "ascension", "blacksmith", "maps/gatefall",
	"waves/waves_gatefall_normal", "waves/waves_gatefall_hard",
]

var _tables: Dictionary[String, Dictionary] = {}


func _init(dir: String = "res://data") -> void:
	load_dir(dir)


# Loads every pinned stem under dir; a missing/unparsable file simply
# stays absent from _tables — detecting that is validate()'s job (W5).
func load_dir(dir: String) -> void:
	for stem: String in STEMS:
		var text := FileAccess.get_file_as_string(dir + "/" + stem + ".json")
		if text.is_empty():
			continue
		var parsed: Variant = JSON.parse_string(text)
		if parsed is Dictionary:
			_tables[stem] = parsed


func table(name: String) -> Dictionary:
	return _tables.get(name, {})


func map(id: String) -> Dictionary:
	return table("maps/" + id)
