# defense_placer — build-phase placement API (Modules row
# scripts/defense_placer.gd, MC 11274.1.15 / card 11322): ghost, validity
# (range/overlap), confirm/cancel, cost via SimEconomy — and the pinned
# row's interface note verbatim: it CALLS mission.place_defense, the ONE
# placement application site (cap check, can_afford gate and the single
# green spend live there; no cost math is duplicated here, I2/I4).
#
# REFERENCE NOTE: the pinned Modules row names this file
# scripts/defense_placer.gd; the W8 brief's "defense_placement.gd" is the
# paraphrase and the table wins (precedent MC 11274.1.9-.14) — the W6
# mission.gd hook comment already reads "W8 (defense_placer) fills this".
#
# Buildable slots (brief: "buildable slots from map data ... lanes
# geometry"): the pinned C7 shape carries NO slot list, so slots are the
# GROUND lane waypoints of the map (file order, deduplicated, minus core
# positions). Overlap validity is therefore one defense per slot; air
# lanes are not buildable in v1 (declared reading — building inside the
# flight corridor is undeclared mechanics). Free placement (DD2 §4, pads
# rejected) rides this data-derived set; a finer grid is map data, not
# code.
#
# The panel talks to THIS file only (row: defense_panel is pure UI over
# mission/defense_obj state); lifecycle actions resolve the uid onto the
# defense record and route to the defense_obj method that owns its leg.

const SIM_ECONOMY := preload("res://sim/sim_economy.gd")

var m = null                    # mission root (injected, duck-typed)
var tower_defs: Array = []      # towers.json rows (array door: raw read)
var slots: Array = []           # Vector3 candidates, stable map order
var ghost := -1                 # armed slot index (-1 = no ghost)


func setup(mission) -> void:
	m = mission
	tower_defs = _load_array("towers")
	slots = _build_slots()


# v1 class list (brief: "lists v1 classes"): one entry per distinct
# towers.json class, first row of that class wins — the tower class ships
# three families and the family picker is a later frontend row (declared).
func classes() -> Array:
	var out: Array = []
	var seen: Dictionary = {}
	for row: Dictionary in tower_defs:
		var cls := String(row["class"])
		if seen.has(cls):
			continue
		seen[cls] = true
		out.append({"class": cls, "name": String(row["name"]),
			"cost": int(row["base_cost"])})
	return out


func row_for(class_id: String) -> Dictionary:
	for row: Dictionary in tower_defs:
		if String(row["class"]) == class_id:
			return row
	return {}


func slot_at(at: Vector3) -> int:
	for i: int in slots.size():
		if slots[i] == at:
			return i
	return -1


func occupied(slot: int) -> bool:
	if slot < 0 or slot >= slots.size():
		return true
	for rec: Dictionary in m.defense_list:
		if (rec["obj"] as RefCounted).pos == slots[slot]:
			return true
	return false


func first_free() -> int:
	for i: int in slots.size():
		if not occupied(i):
			return i
	return -1


func buildable() -> Array:
	var out: Array = []
	for i: int in slots.size():
		if not occupied(i):
			out.append(i)
	return out


# Ghost confirm/cancel (pinned row): the ghost must sit on a free slot.
func set_ghost(slot: int) -> void:
	ghost = slot if not occupied(slot) else -1


func cancel_ghost() -> void:
	ghost = -1


# place(class, tier) per the brief, plus an explicit-slot override for
# deterministic callers. With no armed ghost the confirm falls to the
# FIRST free slot (greybox confirm reading). Validity that belongs to the
# placer (phase, slot, known class) is checked here; cap + affordability
# + the spend are the mission application site's answer (single site).
func place(class_id: String, tier: int, slot: int = -1) -> Dictionary:
	if String(m.phase_kind) != "build":
		return {"ok": false, "why": "phase"}
	var row := row_for(class_id)
	if row.is_empty():
		return {"ok": false, "why": "class"}
	var at := slot
	if at < 0:
		at = ghost
	if at < 0:
		at = first_free()
	if occupied(at):
		return {"ok": false, "why": "slot"}
	return m.place_defense(row, tier, slots[at])


# Lifecycle routes: resolve the uid onto the mission's defense record and
# call the obj method that owns the leg (its C3 static + ledger write).
func upgrade(uid: int) -> Dictionary:
	var rec := _rec(uid)
	return rec if rec.is_empty() else (rec["obj"] as RefCounted).upgrade()


func repair(uid: int) -> Dictionary:
	var rec := _rec(uid)
	return rec if rec.is_empty() else (rec["obj"] as RefCounted).repair()


func sell(uid: int) -> Dictionary:
	for i: int in m.defense_list.size():
		var rec: Dictionary = m.defense_list[i]
		if int(rec["uid"]) == uid:
			var res: Dictionary = (rec["obj"] as RefCounted).sell()
			if bool(res["ok"]):
				(rec["obj"] as RefCounted).node.queue_free()
				m.defense_list.remove_at(i)
			return res
	return {"ok": false, "why": "uid"}


func _rec(uid: int) -> Dictionary:
	for rec: Dictionary in m.defense_list:
		if int(rec["uid"]) == uid:
			return rec
	return {"ok": false, "why": "uid"}


# Slots from the C7 lanes the mission already parsed (lanes dict, map
# file order preserved): ground waypoints only, dedup, cores excluded.
func _build_slots() -> Array:
	var blocked := {m.core_main.pos: true}
	for sid: String in m.core_subs:
		blocked[m.core_subs[sid].pos] = true
	var out: Array = []
	var seen: Dictionary = {}
	for lane_id: String in m.lanes:
		var lane: Dictionary = m.lanes[lane_id]
		if String(lane["kind"]) != "ground":
			continue
		for wp: Variant in lane["wps"]:
			var v: Vector3 = wp
			if blocked.has(v) or seen.has(v):
				continue
			seen[v] = true
			out.append(v)
	return out


func _load_array(stem: String) -> Array:
	# Array-shaped files have no GWTables dict door (the mission._load_array
	# / main.gd boot raw-door precedent).
	var text := FileAccess.get_file_as_string("res://data/" + stem + ".json")
	var parsed: Variant = JSON.parse_string(text)
	return parsed if parsed is Array else []
