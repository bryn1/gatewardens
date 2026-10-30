# lane_bands — the G2 lit lane bands (MC 11694, V121-PLAN G2; G2-FIX
# MC 11698): one top-level band Node3D per GROUND lane, carrying ONE
# MeshInstance3D per waypoint SEGMENT whose mesh is a unit PlaneMesh
# (PrimitiveMesh — engine-managed geometry). G2 (6e98ab4) built each
# strip as a runtime ArrayMesh + material_override: the nodes built
# correct headless (probe LB-OK, AABB sane, winding verified) yet the
# mesh NEVER rasterized in the web export — opaque pure red measured
# 6 px on a VERIFIED build-phase frame (w2-bandexp3) while Sprite3D/
# Label3D children of the SAME parent painted. Params were not the
# fault (BAND_Y/CULL/ARRAY_TEX_UV probes: zero change); the MECHANISM
# was. Engine-managed PrimitiveMesh geometry rasterizes under GL
# Compatibility — PlaneMesh is the class the arena ground rides, and
# it paints through material_override in that same web build — so each
# segment is now a unit PlaneMesh node at the segment midpoint
# (y BAND_Y), rotated so its local +X walks the segment, scaled to
# (segment length, 1, BAND_WIDTH). The CONTRACT is unchanged: exactly
# ONE node named LaneBand_<lane> per ground lane of m.lanes
# (build_lanes' records — the only lane read; zero writes, zero sim
# state, no second lane model and no duplicated lane geometry: the
# band rides the SAME wps the sim walks), segment nodes ride INSIDE
# the band node, AIR lanes get NO band — the winged gate-eye of G1 is
# their declared cue. Mounted ONCE from mission_world.build_cores (the
# paint_arena/G1 visual-hook precedent; mission.gd at its 400 ceiling
# adds ZERO lines). Presentation numbers live HERE, on the builder
# (the sprite_bank ICON_PX doctrine: ungoverned file).
extends RefCounted

const LIT_MATERIAL := preload("res://scripts/lit_material.gd")

const BAND_PREFIX := "LaneBand_"   # node-name marker the probe counts by
const BAND_WIDTH := 1.6            # u, across the polyline (mobs are 2u)
const BAND_Y := 0.02               # slightly > 0: rides the ground, no z-fight
const BAND_COLOR := Color(0.55, 0.8, 1.0, 0.30)  # lit cool cyan, translucent


# One band node per ground lane of m.lanes. Closed ground lanes keep
# their band (the polyline exists even when the sim holds the lane —
# filtering on "open" would BE lane semantics the plan does not grant).
static func paint_lane_bands(m) -> void:
	for lid: String in m.lanes:
		var lane: Dictionary = m.lanes[lid]
		if String(lane["kind"]) != "ground":
			continue                       # air lanes: G1's winged eye
		var band := Node3D.new()
		band.name = BAND_PREFIX + lid
		var mat := LIT_MATERIAL.make(BAND_COLOR)  # the ONE shared shape
		var wps: Array[Vector3] = lane["wps"]
		for i: int in wps.size() - 1:
			var seg := _segment_node(wps[i], wps[i + 1], mat)
			if seg == null:
				continue                   # degenerate: draws nothing
			band.add_child(seg)
		if band.get_child_count() > 0:
			m.add_child(band)              # an all-degenerate lane: no node


# One waypoint segment as engine-managed geometry: a unit PlaneMesh
# (default size 1x1 — the node scale carries the dimensions), at the
# segment midpoint at y BAND_Y, rotated about Y so the plane's local
# +X walks the segment direction and +Z the lateral normal, scaled to
# (segment length, 1, BAND_WIDTH). A degenerate segment returns null
# instead of a zero-scale / NaN-rotation node.
static func _segment_node(a: Vector3, b: Vector3, mat: StandardMaterial3D) \
		-> MeshInstance3D:
	var d := Vector3(b.x - a.x, 0.0, b.z - a.z)
	var seg_len := d.length()
	if seg_len < 0.001:
		return null
	var seg := MeshInstance3D.new()
	seg.mesh = PlaneMesh.new()
	seg.position = Vector3((a.x + b.x) * 0.5, BAND_Y, (a.z + b.z) * 0.5)
	seg.rotation.y = atan2(-d.z, d.x)      # local +X -> the segment dir
	seg.scale = Vector3(seg_len, 1.0, BAND_WIDTH)
	seg.material_override = mat
	return seg

