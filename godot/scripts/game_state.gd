class_name GWGameState
extends RefCounted

# Meta state object (Modules row scripts/game_state.gd, MC 11274.1.11):
# hero levels/xp, ascension points+spend, gear bank, gold, materials
# {id:int} (F2-6), mission completions, active deck — plus the in-memory
# equipped map the C5 snapshot exposes. RefCounted, engine-light: NO
# autoloads, NO Node/Engine refs; it arrives through GWCompose.build_graph
# with `tables` constructor-injected (R3/C1), so every `-s` probe can
# construct it. Cross-file binds are preload(), never class_name refs
# (W3b clean-checkout finding, W4 ruling).
#
# C13: EVERY mutator emits `mutated` — the save trigger — on every call
# (unconditional emit, the pinned contract's literal reading; a no-op
# spend/consume just re-writes identical state, never a partial spend).
# C5: snapshot_json(mission) merges these meta fields with the mission's
# own properties (phase/wave/cores/… read by name, defaults in the hub);
# `saved_ack` mirrors GWSaveStore.write_seq through the compose wiring.
#
# Readings recorded on the card trail:
# - to_save()/from_save() carry the C6 save-fields subset (the pinned C6
#   key list; [meta2].equipped_json ADDED by the MC 11408 round-4 P1
#   ruling: equip removed the row from the bank (persisted) while
#   equipped was never written, so equip+reload DESTROYED the item —
#   equipped gear is the meta (DD2 lineage) and persists now. Old saves
#   miss the key -> {} (I5 back-compat; NO schema bump — a bump would
#   fail the version guard and wipe every real player save).
# - bank_add stamps uid from data only: next uid = max bank uid + 1, so
#   uid uniqueness survives reload with NO extra C6 counter key.
# - hero meta rows initialize lazily (level 1 / xp 0): C6 [hero:<id>]
#   sections exist only for heroes the meta actually touched.
# - The W3a GWTables dict-door loads object-shaped files only; this class
#   therefore reads ONLY xp.json + ascension.json (both objects) from the
#   tables — heroes.json is an ARRAY file and never enters this class
#   THROUGH THE TABLE DOOR. W13 amendment (MC 11274.1.22): the fresh-boot
#   starter deck DOES read the roster through its OWN raw array door
#   (FileAccess + JSON) — W16 made GWTables.rows the ONE shared array
#   door, and this seeding leg stays raw per this amendment: seeding,
#   not a table-door use; the sentence above holds verbatim for the
#   door itself.

const SIM_PROGRESSION := preload("res://sim/sim_progression.gd")
const SIM_INVENTORY := preload("res://sim/sim_inventory.gd")

signal mutated

const SAVE_SCHEMA := 1    # C6 [meta].schema_version
const C5_SCHEMA := 1      # C5 snapshot "schema"

var tables # GWTables by injection (duck-typed: the door is .table(name))

var heroes: Dictionary = {}      # hero_id -> {level:int, xp:int}
var asc_earned: int = 0
var asc_spent: Dictionary = {}   # power_id -> points
var bank: Array = []             # C9 item rows
var gold: int = 0
var materials: Dictionary = {}   # material_id -> count (F2-6)
var completed: Dictionary = {}   # "gatefall_normal" -> true
var deck: Array = []             # hero ids, array order = C4 swap order
var equipped: Dictionary = {}    # hero_id -> {slot -> C9 row} (C6 equipped_json, W17g r4)
var saved_ack: int = 0           # C5 mirror of GWSaveStore.write_seq (C13)
# Lifetime anchor for the C13 listener GWCompose wires to `mutated`: a
# signal connection keeps only an ObjectID on a RefCounted target, so an
# unwired listener dies at the end of build_graph and every emit reaches
# nothing (VERIFIED this gate: write_seq stayed 0). The listener holds
# this state back as a WeakRef only — no leak cycle either way.
var commit_listener = null


func _init(tables_in) -> void:
	tables = tables_in


# ---------- C13 mutators — every one emits `mutated` ----------

func add_hero_xp(hero_id: String, xp: int) -> void:
	var row: Dictionary = heroes.get(hero_id, {"level": 1, "xp": 0})
	var before := int(row["level"])
	row["xp"] = int(row["xp"]) + xp
	var curve: Array = _table("xp").get("hero_curve", [])
	row["level"] = SIM_PROGRESSION.level_from_xp(curve, int(row["xp"]))
	var gained := int(row["level"]) - before
	if gained > 0:
		var per_level := int(_table("ascension").get("points_per_level", 0))
		asc_earned += SIM_PROGRESSION.asc_points(gained, per_level)
	heroes[hero_id] = row
	mutated.emit()


# Spend `pts` ascension points on node `power` (tree = ascension.json
# "tree"); false when unknown node, non-positive, over the node's declared
# max, or over the unspent balance — no partial spend.
func spend_asc(tree: Dictionary, power: String, pts: int) -> bool:
	var node_max := -1
	for branch: String in tree:
		for row: Dictionary in tree[branch]:
			if String(row.get("id", "")) == power:
				node_max = int(row.get("max", 0))
	var spent_now := int(asc_spent.get(power, 0))
	var free := asc_earned - asc_spent_total()
	var ok := node_max >= 0 and pts > 0 and pts <= free \
			and spent_now + pts <= node_max
	if ok:
		asc_spent[power] = spent_now + pts
	mutated.emit()
	return ok


func bank_add(item: Dictionary) -> void:
	var row: Dictionary = item.duplicate(true)
	if int(row.get("uid", 0)) <= 0:
		row["uid"] = next_uid()
	bank.append(row)
	mutated.emit()


# F2-11/C9 crossing: delegates to SimInventory.equip; the replaced row is
# merged into the array passed in, so the returned bank carries it back
# (replace-to-bank is equip's contract, never caller logic).
func equip(hero: String, slot: String, item: Dictionary) -> bool:
	var ok := slot in ["weapon", "armor", "ring"] \
			and String(item.get("slot", "")) == slot
	var bank_in: Array = bank.duplicate()
	var current: Variant = equipped.get(hero, {}).get(slot)
	if ok and current != null:
		bank_in.append(current)
	var res: Dictionary = SIM_INVENTORY.equip(bank_in, hero, item)
	ok = ok and bool(res["ok"])
	if ok:
		if not equipped.has(hero):
			equipped[hero] = {}
		equipped[hero][slot] = item
		bank = res["bank"]
	mutated.emit()
	return ok


func add_gold(n: int) -> void:
	gold += n
	mutated.emit()


# BN2: the named gold mutator. false when short — no partial spend.
func spend_gold(n: int) -> bool:
	var ok := n > 0 and gold >= n
	if ok:
		gold -= n
	mutated.emit()
	return ok


func add_material(id: String, n: int) -> void:
	materials[id] = int(materials.get(id, 0)) + n
	mutated.emit()


func consume_material(id: String, n: int) -> bool:
	var have := int(materials.get(id, 0))
	var ok := n > 0 and have >= n
	if ok:
		materials[id] = have - n
	mutated.emit()
	return ok


func set_deck(hero_ids: Array) -> void:
	deck = hero_ids.duplicate()
	mutated.emit()


func complete_mission(mission_key: String) -> void:
	completed[mission_key] = true
	mutated.emit()


# ---------- C6 save-fields subset ----------

func to_save() -> Dictionary:
	return {
		"schema_version": SAVE_SCHEMA,
		"asc_earned": asc_earned,
		"asc_spent_json": JSON.stringify(asc_spent),
		"heroes": heroes_save(),
		"items_json": JSON.stringify(bank),
		"gold": gold,
		"deck_json": JSON.stringify(deck),
		"completed_json": JSON.stringify(completed),
		"materials_json": JSON.stringify(materials),
		"equipped_json": JSON.stringify(equipped),
	}


# I5: empty dict or a foreign schema_version = fresh start, never crash.
# W13 (MC 11274.1.22 / card 11332): the fresh start now SEEDS the declared
# starter kit (OPEN-Q of the A9 journey: a fresh browser booted
# gold=0/deck=[] because every desktop probe pre-seeded a save); the seed
# is silent — a boot default is not a meta mutation, so no `mutated`
# emit and no C13 write fires on a fresh boot (A9's ack=0-on-first-boot
# reading holds; the kit persists with the player's first real mutation).
func from_save(d: Dictionary) -> void:
	if d.is_empty() or int(d.get("schema_version", 0)) != SAVE_SCHEMA:
		_seed_starter_meta()
		return
	var heroes_in: Dictionary = d.get("heroes", {})
	for hero_id: String in heroes_in:
		var row: Dictionary = heroes_in[hero_id]
		heroes[hero_id] = {"level": int(row.get("level", 1)),
			"xp": int(row.get("xp", 0))}
	asc_earned = int(d.get("asc_earned", 0))
	asc_spent = int_dict(json_dict(d.get("asc_spent_json", "{}")))
	bank = json_array(d.get("items_json", "[]"))
	gold = int(d.get("gold", 0))
	deck = json_array(d.get("deck_json", "[]"))
	completed = json_dict(d.get("completed_json", "{}"))
	materials = int_dict(json_dict(d.get("materials_json", "{}")))
	# W17g r4 (MC 11408): equipped restores from [meta2].equipped_json;
	# an OLD save misses the key -> {} (json_dict's I5 default — the same
	# back-compat door every *_json key rides). JSON numbers arrive as
	# float (named limitation the bank blob already carries; consumers
	# int() the row fields, VERIFIED by the persist probe's round-trip).
	equipped = json_dict(d.get("equipped_json", "{}"))


func heroes_save() -> Dictionary:
	var out: Dictionary = {}
	for hero_id: String in heroes:
		out[hero_id] = {"level": int(heroes[hero_id]["level"]),
			"xp": int(heroes[hero_id]["xp"])}
	return out


# ---------- C5 snapshot ----------

func snapshot_json(mission: Variant) -> String:
	var in_mission := mission != null and is_instance_valid(mission)
	var snap := {
		"schema": C5_SCHEMA,
		"phase": "mission" if in_mission else "hub",
		"mission_id": _mget(mission, "mission_id", ""),
		"difficulty": _mget(mission, "difficulty", "normal"),
		"wave": int(_mget(mission, "wave", 0)),
		"phase_kind": _mget(mission, "phase_kind", "build"),
		"wave_remaining": int(_mget(mission, "wave_remaining", 0)),
		"alive": int(_mget(mission, "alive", 0)),
		"green": int(_mget(mission, "green", 0)),
		"green_cap": int(_table("economy").get("green", {}).get("cap", 0)),
		"blue": float(_mget(mission, "blue", 0.0)),
		"blue_max": float(_mget(mission, "blue_max", 0.0)),
		"hero_id": _mget(mission, "hero_id", ""),
		"hero_hp": float(_mget(mission, "hero_hp", 0.0)),
		"hero_hp_max": float(_mget(mission, "hero_hp_max", 0.0)),
		"cores": _mget(mission, "cores",
			{"main": {"hp": 0.0, "max": 0.0}, "subs": []}),
		"defenses": int(_mget(mission, "defenses", 0)),
		"defense_cap": int(_mget(mission, "defense_cap", 0)),
		"relics_assigned": int(_mget(mission, "relics_assigned", 0)),
		"deck": deck_rows(),
		"asc_points": asc_earned - asc_spent_total(),
		"bank_count": bank.size(),
		"gold": gold,
		"loot_pending": int(_mget(mission, "loot_pending", 0)),
		"equipped": equipped_snapshot(),
		"outcome": _mget(mission, "outcome", null),
		"boss_hp": _mget(mission, "boss_hp", null),
		"saved_ack": saved_ack,
		"t": float(_mget(mission, "t", 0.0)),
	}
	return JSON.stringify(snap)


func deck_rows() -> Array:
	var out: Array = []
	for hero_id: String in deck:
		out.append({"id": hero_id,
			"level": int(heroes.get(hero_id, {}).get("level", 1))})
	return out


func equipped_snapshot() -> Dictionary:
	var out: Dictionary = {}
	for hero_id: String in equipped:
		var slots: Dictionary = {}
		for slot: String in ["weapon", "armor", "ring"]:
			var row: Variant = equipped[hero_id].get(slot)
			slots[slot] = String(row["base_id"]) if row != null else null
		out[hero_id] = slots
	return out


# ---------- helpers ----------

func asc_spent_total() -> int:
	var total := 0
	for power: String in asc_spent:
		total += int(asc_spent[power])
	return total


func next_uid() -> int:
	var top := 0
	for row: Dictionary in bank:
		top = maxi(top, int(row.get("uid", 0)))
	# W9 (MC 11274.1.16, declared W9 finding): uid identity is a bank
	# concern, but rows worn by heroes are OUT of the bank mid-session —
	# scanning ONLY the bank lets the next bank_add stamp a uid a worn row
	# still carries (the mission-end chest leg creates exactly this
	# state). Panels key the pinned picked(uid) signal, so the stamp must
	# anchor on in-flight rows too. Save schema untouched (C6 carries no
	# equipped key; a fresh boot's bank-only sequence stamps identically).
	for slots: Dictionary in equipped.values():
		for row: Dictionary in slots.values():
			top = maxi(top, int(row.get("uid", 0)))
	return top + 1


func _table(name: String) -> Dictionary:
	return tables.table(name) if tables != null else {}


# W13 starter kit (OPEN-Q fix, ZERO literals — every value DATA): gold =
# economy.json "starter.gold"; deck = the heroes.json roster in FILE order
# (the C4 swap order — roster order IS the declared deck order for a
# fresh account). Seeded silently: direct field writes, NO mutator call,
# NO mutated emit (a boot default is not a meta mutation; C13 stays the
# only save trigger).
func _seed_starter_meta() -> void:
	gold = int(_table("economy").get("starter", {}).get("gold", 0))
	deck = _roster_ids()


func _roster_ids() -> Array:
	# Array-shaped heroes.json: this seeding leg keeps its OWN raw door
	# (the W13 amendment in the header; GWTables.rows is the shared one).
	var text := FileAccess.get_file_as_string("res://data/heroes.json")
	var parsed: Variant = JSON.parse_string(text)
	var out: Array = []
	if parsed is Array:
		for row: Variant in parsed:
			out.append(String(row["id"]))
	return out


func _mget(mission: Variant, prop: String, fallback: Variant) -> Variant:
	if mission == null or not is_instance_valid(mission):
		return fallback
	var v: Variant = mission.get(prop)
	return v if v != null else fallback


func int_dict(src: Dictionary) -> Dictionary:
	var out: Dictionary = {}
	for key: String in src:
		out[key] = int(src[key])
	return out


func json_dict(text: Variant) -> Dictionary:
	var parsed: Variant = JSON.parse_string(String(text))
	return parsed if parsed is Dictionary else {}


func json_array(text: Variant) -> Array:
	var parsed: Variant = JSON.parse_string(String(text))
	return parsed if parsed is Array else []
