# lane_bands — the G2 lit lane bands (MC 11694, V121-PLAN G2): one
# translucent quad-strip MeshInstance3D per GROUND lane, painted along
# the EXISTING waypoint polylines of m.lanes (build_lanes' records —
# the only lane read; zero writes, zero sim state, no second lane model
# and no duplicated lane geometry: the band is derived from the same
# wps the sim walks). AIR lanes get NO band — the winged gate-eye of G1
# is their declared cue. Mounted ONCE from mission_world.build_cores
# (the paint_arena/G1 visual-hook precedent; mission.gd at its 400
# ceiling adds ZERO lines). Presentation numbers live HERE, on the
# builder (the sprite_bank ICON_PX doctrine: ungoverned file).
extends RefCounted

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
		var strip := _strip_mesh(lane["wps"])
		if strip == null:
			continue                       # no drawable segment
		var node := MeshInstance3D.new()
		node.name = BAND_PREFIX + lid
		node.mesh = strip
		node.material_override = _band_material()
		m.add_child(node)


# One quad per waypoint segment, joined at the shared wp (corners sit
# at wp ± halfwidth along the segment normal — at the shallow map
# angles this reads as one continuous strip). Upward-facing triangles;
# a degenerate segment draws nothing rather than a NaN normal.
static func _strip_mesh(wps: Array[Vector3]) -> ArrayMesh:
	var verts := PackedVector3Array()
	var idx := PackedInt32Array()
	for i: int in wps.size() - 1:
		var a: Vector3 = wps[i]
		var b: Vector3 = wps[i + 1]
		var d := Vector3(b.x - a.x, 0.0, b.z - a.z)
		if d.length() < 0.001:
			continue
		var n := Vector3(-d.z, 0.0, d.x).normalized() * (BAND_WIDTH * 0.5)
		var base := verts.size()
		verts.append(Vector3(a.x + n.x, BAND_Y, a.z + n.z))
		verts.append(Vector3(b.x + n.x, BAND_Y, b.z + n.z))
		verts.append(Vector3(b.x - n.x, BAND_Y, b.z - n.z))
		verts.append(Vector3(a.x - n.x, BAND_Y, a.z - n.z))
		idx.append_array([base, base + 1, base + 2, base, base + 2, base + 3])
	if verts.is_empty():
		return null
	var arrays: Array = []
	arrays.resize(Mesh.ARRAY_MAX)            # ARRAY_INDEX lives at slot 12
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_INDEX] = idx
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh


# The ONE band material shape, built per node (runtime-duplicate idiom
# — no .tres on disk to keep in sync): unshaded so it reads lit on the
# dark arena, alpha-blended so the painted ground shows through.
static func _band_material() -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = BAND_COLOR
	return mat
