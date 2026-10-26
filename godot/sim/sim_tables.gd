class_name GWTables
extends RefCounted

# Data load + hold (C1): reads the pinned data-files table via FileAccess +
# JSON and keys every file by its res-relative stem under the data dir
# ("economy", "maps/gatefall", "waves/waves_gatefall_hard", ...).
# table(name) is the ONLY dict read door (name = file stem); rows(stem)
# is the ONE array door (W16: the raw FileAccess+JSON copies in
# mission/defense_placer/blacksmith_ui/dummy_range/hub_probe collapsed
# into this static — a fresh parse per call, never cached: consumers like
# mission._build_heroes write onto their own copy, C1); map(id) is a REAL
# method (F16). Read-only doctrine (C1): consumers never mutate a loaded
# table and this class never writes into one. Deep validation deferred —
# the pytest schema layer (test_data_schemas) + main.gd's file-level boot
# check own F16 (was: "validate() lands with validate_probe (W5)" — that
# probe never shipped; W16 truth per doc-sweep S6). No Node/Engine (I6).

# The exact data set the ARCHITECTURE data-files table pins (W2 shipped it).
const STEMS: Array[String] = [
	"economy", "balance", "xp", "heroes", "towers", "enemies", "rarity",
	"items", "mods", "ascension", "blacksmith", "maps/gatefall",
	"waves/waves_gatefall_normal", "waves/waves_gatefall_hard",
]

var _tables: Dictionary[String, Dictionary] = {}
var _dir: String = "res://data"


func _init(dir: String = "res://data") -> void:
	load_dir(dir)


# Loads every pinned stem under dir; a missing/unparsable file simply
# stays absent from _tables — boot detects that at FILE level in
# main.gd's fail-fast (deep-validation deferred; doc-sweep S6 truth).
func load_dir(dir: String) -> void:
	_dir = dir
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


# Array door (W16, one home for five copies): fresh-parse one array-shaped
# file (heroes/towers/enemies/items/mods), [] if absent or not an Array —
# byte-for-byte the door mission/defense_placer/blacksmith_ui/dummy_range/
# hub_probe each used to carry inline. Never cached (callers own their
# copy; C1 read-only covers the dict side only).
func rows(stem: String) -> Array:
	var text := FileAccess.get_file_as_string(_dir + "/" + stem + ".json")
	var parsed: Variant = JSON.parse_string(text)
	return parsed if parsed is Array else []
