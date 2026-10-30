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
#
# G4 (v1.2.1, MC 11707 / V121-PLAN row G4): the range ring RIDES THE
# GHOST — this file owns the aim/ghost state (G5), so its three ghost
# chokepoints (set/cancel/cycle — the pinned ghost-API caller set) call
# _sync_ring, the ONE ring driver: arm/cycle SHOW+RESIZE, and place /
# RMB/Escape cancel / the W17e combat-lock all HIDE through cancel_ghost.
# The radius is the towers.json tier-row range NUMBER of the armed row
# (tier_range; GHOST_TIER — the confirm tier, the ghost's only tier);
# range-0 rows (the five gate_blockade tier rows) render NO ring (Rev 2 /
# DA A4.1). The armed ROW itself is observed off the mounted panel's
# public armed_id (fx_director observer idiom, read-only — the panel's
# "armed ⇔ ghost" invariant, G5-wave.log's caller-set census), so
# defense_panel.gd needs ZERO drive lines for the ring (owned-paths
# discipline); a placer with no mounted panel resolves no row and stays
# ring-silent. Geometry + show/hide live in scripts/range_ring.gd.

const SIM_ECONOMY := preload("res://sim/sim_economy.gd")
const RANGE_RING := preload("res://scripts/range_ring.gd")

# G4 (MC 11707): the ghost's tier — the confirm tier. place_defense is
# T1-only by the pinned build contract (mission.gd "if tier != 1"), and
# _confirm places (armed_id, 1); the ghost therefore HAS no other tier.
const GHOST_TIER := 1

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
# V4 (MC 11549): the row carries the WINNING row's data id too — the
# panel maps the shop ICON from it, so "first row wins" keeps its single
# home here instead of a second dedupe in the UI.
func classes() -> Array:
	var out: Array = []
	var seen: Dictionary = {}
	for row: Dictionary in tower_defs:
		var cls := String(row["class"])
		if seen.has(cls):
			continue
		seen[cls] = true
		out.append({"class": cls, "id": String(row["id"]),
			"name": String(row["name"]), "cost": int(row["base_cost"])})
	return out


func row_for(class_id: String) -> Dictionary:
	for row: Dictionary in tower_defs:
		if String(row["class"]) == class_id:
			return row
	return {}


# F4 (MC 11616 / V12-PLAN §F4): the family picker resolves by towers.json
# DATA ID (ballista/bombard/hailspire_tower/...), not by class.
func row_for_id(tower_id: String) -> Dictionary:
	for row: Dictionary in tower_defs:
		if String(row["id"]) == tower_id:
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
# G4 (MC 11707): the three ghost chokepoints below are the ONE ring
# driver — every transition runs _sync_ring (arm SHOWS, cancel HIDES).
func set_ghost(slot: int) -> void:
	ghost = slot if not occupied(slot) else -1
	_sync_ring()


func cancel_ghost() -> void:
	ghost = -1
	_sync_ring()


# G5 (v1.2.1, MC 11700 / V121-PLAN §1 G5): the ghost CYCLE step over the
# buildable slots — the ghost moves dir (-1/+1) through buildable() with
# wrap; with no ghost on a buildable slot yet it lands on the first one.
# The panel's arrow relay rides this (cycle helper HERE, I2-clean);
# placement itself stays the confirm route — place_id resolves the ghost
# inside, this moves the AIM only (no second placement mechanism).
# G4 (MC 11707): the early returns folded to ONE exit so the ring sync
# rides every transition (the ghost/cycle semantics byte-equivalent).
func cycle_ghost(dir: int) -> void:
	var free: Array = buildable()
	if free.is_empty():
		ghost = -1
	else:
		var at: int = free.find(ghost)
		if at < 0:
			ghost = free[0]
		else:
			ghost = free[(at + dir + free.size()) % free.size()]
	_sync_ring()


# G4 (MC 11707 / V121-PLAN row G4): the tier-row RANGE NUMBER — the ring's
# radius source and the DATA leg's sampled function. tower_id is the
# towers.json DATA id (the row_for_id door), tier is 1-BASED (T1..T5, the
# display convention GHOST_TIER (the confirm tier) carries) — the tier entry
# is tiers[tier - 1] (defense_obj.tier_row holds the 0-based twin). The
# number is READ, never computed (I2). Unknown id, out-of-range tier or a
# missing range = 0.0, which the ring reads as the declared NO-RING answer
# — the five gate_blockade tier rows carry range 0 (Rev 2 / DA A4.1:
# hidden, not a zero-radius dot).
func tier_range(tower_id: String, tier: int) -> float:
	var row := row_for_id(tower_id)
	if row.is_empty():
		return 0.0
	var tiers: Array = row["tiers"]
	if tier < 1 or tier > tiers.size():
		return 0.0
	return float((tiers[tier - 1] as Dictionary).get("range", 0.0))


# G4: the armed ghost's ROW id, OBSERVED from the panel (declared reading:
# the ghost is slot-only state; the armed family is the panel's G5-pinned
# armed_id — its header's "armed ⇔ ghost" invariant, and the ONE arm
# route _arm writes armed_id BEFORE it lands the ghost, so every ghost
# transition already carries the row; place/RMB/Escape/combat-lock clear
# it on the same cancel route that hides the ring). fx_director observer
# idiom: public-field read, ZERO writes, no signal wiring. A standalone
# placer with no mounted panel resolves no row -> no ring: the honest
# shape (without an armed row there is no range to claim — harness
# set_ghost legs stay ring-silent).
func _armed_id() -> String:
	if m == null:
		return ""
	var p = m.get_node_or_null(NodePath("DefensePanel"))
	if p == null:
		return ""
	var armed: Variant = p.get("armed_id")
	return String(armed) if armed != null else ""


# G4: the ONE ring sync — called by the three ghost chokepoints above
# (the set G5 pinned as the ghost API's whole external caller set, cited
# in G5-wave.log: set = the arm route, cancel = confirm-success + RMB/
# Escape + the W17e combat-lock, cycle = the arrow relay), so arm/cycle
# SHOW+RESIZE and place/cancel/lock HIDE through this single site — no
# second driver. Radius = tier_range of the armed row (GHOST_TIER: the
# confirm tier, the ghost's only tier); range <= 0 or no armed row = hide
# (the declared DA A4.1 treatment, one branch not a second mechanism).
func _sync_ring() -> void:
	if m == null:
		return
	var radius := 0.0
	if ghost >= 0:
		radius = tier_range(_armed_id(), GHOST_TIER)
	if radius <= 0.0:
		RANGE_RING.hide_ring(m)
		return
	RANGE_RING.show_ring(m, slots[ghost], radius)


# place(class, tier) per the brief, plus an explicit-slot override for
# deterministic callers. F4 (MC 11616): the gates live ONCE in place_id
# (replace-not-add) — this keeps its class semantics (first-row-wins) and
# delegates to place_id on the winning row's data id; phase + class are
# checked here FIRST so the class refusals keep their shipped order.
func place(class_id: String, tier: int, slot: int = -1) -> Dictionary:
	if String(m.phase_kind) != "build":
		return {"ok": false, "why": "phase"}
	var row := row_for(class_id)
	if row.is_empty():
		return {"ok": false, "why": "class"}
	return place_id(String(row["id"]), tier, slot)


# F4 (MC 11616 / V12-PLAN §F4): THE one placement gate sequence by data
# id — the family picker's entry, and place()'s own delegate. With no
# armed ghost the confirm falls to the FIRST free slot (greybox confirm
# reading, the SAME resolution order the class buttons always used).
# G5 (v1.2.1, MC 11700): panel confirms now arrive WITH an armed ghost;
# the no-ghost fallback rides the KeyM-UNARMED legacy and the explicit/
# harness callers — pinned standing behavior (plan Rev 2 / DA A4.3),
# unchanged. Validity that belongs to the placer (phase, known id, slot)
# is checked here; cap + affordability + the spend are the mission
# application site's answer (mission.place_defense — single site, I2/I4).
# Unknown id is the NEW "id" refusal (plan contract row).
func place_id(tower_id: String, tier: int, slot: int = -1) -> Dictionary:
	if String(m.phase_kind) != "build":
		return {"ok": false, "why": "phase"}
	var row := row_for_id(tower_id)
	if row.is_empty():
		return {"ok": false, "why": "id"}
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
