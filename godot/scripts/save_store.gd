class_name GWSaveStore
extends RefCounted

# Meta save file (Modules row scripts/save_store.gd, MC 11274.1.11):
# ConfigFile per C6 with EXACTLY the pinned key list —
#   [meta]      schema_version:int, asc_earned:int, asc_spent_json:String
#   [hero:<id>] level:int, xp:int          (one section per touched hero)
#   [bank]      items_json:String          (Array of C9 rows)
#   [meta2]     gold:int, deck_json:String, completed_json:String,
#               materials_json:String (materials_json = F2-6),
#               equipped_json:String  (the C5 equipped map — added by the
#               MC 11408 round-4 P1 ruling: equip persisted bank-1 while
#               equipped had no key, so equip+reload DESTROYED the item)
# Write = hollow_dawn DawnWell mechanism EXTENDED (atomic temp+rename, a
# torn write cannot land mid-save); unreadable previous file -> *.corrupt
# copy kept + fresh defaults (C6 recovery rule, I5 "never crash").
#
# Readings recorded on the card trail:
# - saved_ack is NOT a save key: the pinned C6 [meta2] list carries no ack
#   row, and C13 mirrors the IN-MEMORY write_seq into C5 saved_ack (the
#   W4 brief's extra [meta2] line is superseded by the pinned table —
#   stop-condition precedent MC 11274.1.9/.10). tests/test_persistence.py
#   pins both the exact key list and this absence.
# - OLD SAVES: [meta2] may lack equipped_json (every file written before
#   MC 11408 r4); load_save defaults it to "{}" — a missing key is the
#   same I5 door every *_json key rides, NO schema bump (a bump fails
#   from_save's version guard and would wipe real saves to the seed).
# - Pinned row API wins over the brief's paraphrase: write(d:Dictionary)
#   -> bool, load_save() -> Dictionary ({} = missing/corrupt/foreign),
#   var write_seq (C13 ack source). The dict d is GWGameState.to_save().
# - ctor(user_path, rng_optional): the second param is accepted unused,
#   per the brief's own "unused here" note (a save write is deterministic).

var path: String
var write_seq: int = 0 # C13 ack source: bumped on every successful write


func _init(user_path: String = "user://gatewardens.cfg", _rng = null) -> void:
	path = user_path


# Whole-file atomic write (DawnWell pattern): tmp + rename. False only
# when the write/rename itself failed; callers keep in-memory state.
func write(d: Dictionary) -> bool:
	var cfg := ConfigFile.new()
	cfg.set_value("meta", "schema_version", int(d.get("schema_version", 0)))
	cfg.set_value("meta", "asc_earned", int(d.get("asc_earned", 0)))
	cfg.set_value("meta", "asc_spent_json",
		String(d.get("asc_spent_json", "{}")))
	var heroes_in: Dictionary = d.get("heroes", {})
	for hero_id: String in heroes_in:
		var row: Dictionary = heroes_in[hero_id]
		cfg.set_value("hero:" + hero_id, "level", int(row.get("level", 1)))
		cfg.set_value("hero:" + hero_id, "xp", int(row.get("xp", 0)))
	cfg.set_value("bank", "items_json", String(d.get("items_json", "[]")))
	cfg.set_value("meta2", "gold", int(d.get("gold", 0)))
	cfg.set_value("meta2", "deck_json", String(d.get("deck_json", "[]")))
	cfg.set_value("meta2", "completed_json",
		String(d.get("completed_json", "{}")))
	cfg.set_value("meta2", "materials_json",
		String(d.get("materials_json", "{}")))
	cfg.set_value("meta2", "equipped_json",
		String(d.get("equipped_json", "{}")))
	var tmp_path := path + ".tmp"
	if cfg.save(tmp_path) != OK:
		printerr("SAVE_WRITE_FAIL path=%s" % tmp_path)
		return false
	var dir := DirAccess.open(path.get_base_dir())
	if dir == null \
			or dir.rename(path.get_file() + ".tmp", path.get_file()) != OK:
		printerr("SAVE_WRITE_FAIL path=%s" % path)
		return false
	write_seq += 1
	return true


# Missing file is NOT a failure: {} = fresh start (I5). Unreadable file:
# quarantine copy kept, fresh start.
func load_save() -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var cfg := ConfigFile.new()
	if cfg.load(path) != OK:
		_quarantine()
		return {}
	var d := {
		"schema_version": int(cfg.get_value("meta", "schema_version", 0)),
		"asc_earned": int(cfg.get_value("meta", "asc_earned", 0)),
		"asc_spent_json": String(cfg.get_value("meta", "asc_spent_json", "{}")),
		"heroes": {},
		"items_json": String(cfg.get_value("bank", "items_json", "[]")),
		"gold": int(cfg.get_value("meta2", "gold", 0)),
		"deck_json": String(cfg.get_value("meta2", "deck_json", "[]")),
		"completed_json": String(cfg.get_value("meta2", "completed_json", "{}")),
		"materials_json": String(cfg.get_value("meta2", "materials_json", "{}")),
		"equipped_json": String(cfg.get_value("meta2", "equipped_json", "{}")),
	}
	for section: String in cfg.get_sections():
		if section.begins_with("hero:"):
			d["heroes"][section.trim_prefix("hero:")] = {
				"level": int(cfg.get_value(section, "level", 1)),
				"xp": int(cfg.get_value(section, "xp", 0)),
			}
	return d


# Rename the offending save aside (DawnWell's MOVE — a copy could not be
# read if the unreadability is the failure; a previous corrupt copy is
# replaced, inspection is its point) and print the load-fail marker.
func _quarantine() -> void:
	var dir := DirAccess.open(path.get_base_dir())
	if dir != null:
		dir.remove(path.get_file() + ".corrupt")
		dir.rename(path.get_file(), path.get_file() + ".corrupt")
	printerr("SAVE_LOAD_FAIL path=%s" % path)
