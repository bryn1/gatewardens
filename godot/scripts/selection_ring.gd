# selection_ring — the P5 selection-ring DRIVER (v1.4, MC card 11837 /
# V14-PLAN row P5): one pass per frame decides the ONE RangeRing node
# (scripts/range_ring.gd — the G4 mechanism, geometry + show/hide stay
# THERE) from EXISTING published state only, with the plan's DECLARED
# priority rule ARMED > SELECTED > HIDDEN:
# - ARMED placement (panel.armed, G5): ring AT the armed slot (placer.
#   ghost, the shipped arm/cycle aim — "slot/hover" realized as the
#   ghost slot: v1 has no free-cursor hover, the ghost IS the aim),
#   ARMED color (RING_COLOR — the G4 yellow stays the armed visual,
#   byte-for-byte). An arm with no placeable ring (ghost -1 or the
#   range-0 gate_blockade treatment, Rev 2 / DA A4.1) HIDES — the armed
#   STATE wins the priority; it never falls through to the selection.
# - else SELECTED defense (panel.selected_uid, the W17c player path):
#   ring AT the defense, SELECTED color, radius = that obj's tier-row
#   range number through the SAME placer.tier_range data door (I2: the
#   number is READ, no literal; tier is defense_obj's 0-BASED index + 1).
#   range-0 rows hide, same treatment.
# - else hidden.
#
# THE PUMP: mounted in mission.tscn as a root-last Node3D child — the
# fx_director mount ruling verbatim ("the smallest hook that cannot
# reorder sim steps: the root's _process runs step() first, then this
# node's _process observes the finished frame"). mission.gd carries ZERO
# new lines (the LOC 400 gate sits at 399 — a mount line would tip it;
# the scene mount needs no code line at all). Under `-s` no frame
# dispatches _process (E5), so the probe drives ring_step() by hand in
# lockstep — the fx_step idiom.
#
# OBSERVER DISCIPLINE (fx_director, MC 11552): READS ONLY — panel.armed
# / armed_id / selected_uid, placer.ghost / slots / tier_range, mission.
# defense_list records. ZERO writes to any sim or panel field, no signal
# wiring, no new sim state, no new node types (the ring node itself is
# range_ring's lazy mission-root child, unchanged). Coexistence with the
# G4 ghost chokepoints (_sync_ring on set/cancel/cycle) is idempotent:
# the armed leg of this pass re-asserts exactly what _sync_ring writes
# (same slot, same tier_range, same color), so the two never disagree —
# G4's event-driven show/hide stays byte-green and this pass adds the
# SELECTED leg + the per-frame re-set that a selection change outside
# the ghost API could never reach.

extends Node3D

const RANGE_RING := preload("res://scripts/range_ring.gd")
const PLACER := preload("res://scripts/defense_placer.gd")


func _process(_d: float) -> void:
	ring_step()


# One decision pass. Public so the headless probe drives it in lockstep
# with the panel actions (E5 idiom). No setup state is held: every frame
# reads the CURRENT published picture.
func ring_step() -> void:
	var m = get_parent()
	if m == null or not ("defense_list" in m):
		return                       # not set up (E5: scene child, pre-setup)
	var p = m.get_node_or_null(NodePath("DefensePanel"))
	if p == null or p.placer == null:
		return                       # no panel/placer mounted: ring-silent
	if bool(p.armed):
		# PRIORITY BRANCH (the planted-red target): ARMED outranks the
		# selection; an arm without a placeable ring HIDES, it never
		# falls through to the selected leg.
		var ghost := int(p.placer.ghost)
		var radius := 0.0
		if ghost >= 0:
			radius = p.placer.tier_range(String(p.armed_id), PLACER.GHOST_TIER)
		if radius <= 0.0:
			RANGE_RING.hide_ring(m)
			return
		RANGE_RING.show_ring(m, p.placer.slots[ghost], radius)
		return
	var uid := int(p.selected_uid)
	if uid > 0:
		for rec: Dictionary in m.defense_list:
			if int(rec["uid"]) != uid:
				continue
			var obj = rec["obj"]
			# defense_obj.tier is the 0-BASED index (display T1 = 0);
			# tier_range takes the 1-based tier (G4's pinned door).
			var r: float = p.placer.tier_range(String(obj.trow["id"]),
					int(obj.tier) + 1)
			if r <= 0.0:
				RANGE_RING.hide_ring(m)   # range-0 rows: hidden (A4.1)
			else:
				RANGE_RING.show_ring(m, obj.pos, r, RANGE_RING.SELECTED_COLOR)
			return
	RANGE_RING.hide_ring(m)
