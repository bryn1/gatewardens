# defense_placer — build-phase placement API (Modules row
# scripts/defense_placer.gd, MC 11274.1.15 / card 11322): ghost, validity
# (range/overlap), confirm/cancel, cost via SimEconomy — and the pinned
# row's interface note verbatim: it CALLS mission.place_defense, the ONE
# placement application site (cap check, can_afford gate and the single
# green spend live there; no cost math is duplicated here, I2/I4).
#
# Name contract: the pinned Modules table names this file (the brief's
# "defense_placement.gd" paraphrase never applies — table wins).
#
# Buildable slots (brief: "buildable slots from map data ... lanes
# geometry"): the pinned C7 shape carries NO slot list, so slots are the
# GROUND lane waypoints of the map (deduplicated, minus core positions;
# the LIST is emitted round-robin across the ground lanes — W17f). Overlap validity is therefore one defense per slot; air
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
var tower_defs: Array = []      # towers.json rows (GWTables.rows door)
var slots: Array = []           # Vector3 candidates, stable map order
var ghost := -1                 # armed slot index (-1 = no ghost)


func setup(mission) -> void:
	m = mission
	tower_defs = m.tables.rows("towers")
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
# Not-found is _rec's refusal ITSELF — the same {"ok": false, "why": "uid"}
# shape sell() returns (W11b, MC 11274.1.20 / card 11330: the old
# rec.is_empty() guard could never see the non-empty sentinel, so an
# unknown uid fell through and rec["obj"] was a SCRIPT ERROR under -s).
func upgrade(uid: int) -> Dictionary:
	var rec := _rec(uid)
	if not rec.has("obj"):
		return rec
	return (rec["obj"] as RefCounted).upgrade()


func repair(uid: int) -> Dictionary:
	var rec := _rec(uid)
	if not rec.has("obj"):
		return rec
	return (rec["obj"] as RefCounted).repair()


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
# file order preserved): ground waypoints only, dedup, cores excluded —
# EMITTED ROUND-ROBIN ACROSS THE GROUND LANES (W17f, MC 11274.1.33 /
# card 11403): g1a, g2a, g3a, g1b, g2b, ... The old lane-file-BLOCKED
# order made every first-free place pile into the first ground lane
# until it was full, so consecutive panel places defended ONE lane only
# (browser journey wave-4/5 wall). Content rules UNCHANGED (ground-only,
# dedup-by-position, cores excluded); only the emission order rotates —
# explicit-slot callers resolve positions via slot_at and are unaffected.
func _build_slots() -> Array:
	var blocked := {m.core_main.pos: true}
	for sid: String in m.core_subs:
		blocked[m.core_subs[sid].pos] = true
	var per_lane: Array = []         # one slot list per ground lane,
	var seen: Dictionary = {}         #   lane file order preserved
	for lane_id: String in m.lanes:
		var lane: Dictionary = m.lanes[lane_id]
		if String(lane["kind"]) != "ground":
			continue
		var lane_slots: Array = []
		for wp: Variant in lane["wps"]:
			var v: Vector3 = wp
			if blocked.has(v) or seen.has(v):
				continue
			seen[v] = true
			lane_slots.append(v)
		per_lane.append(lane_slots)
	var out: Array = []
	var rank := 0
	var more := true
	while more:                       # interleave: rank r of every lane
		more = false
		for lane_slots: Array in per_lane:
			if rank < lane_slots.size():
				out.append(lane_slots[rank])
				more = true
		rank += 1
	return out
