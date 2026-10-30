# g2_lane_band_probe — the G2 lit lane band headless proof (MC card
# 11694 / V121-PLAN G2; G2-FIX MC 11698). Boot idiom = g1_gate_eye_probe
# (itself v1_world_probe): mission.tscn instantiated, _ready and setup
# driven directly (E5), the pinned smoke seed, root.size = the served
# canvas. Rows (machine lines, any failure prints LB-FAIL <why> and
# quits 1):
#  BANDS  the mission root carries EXACTLY one band node per GROUND
#         lane of m.lanes (derived count + pinned n=3 for gatefall).
#  BAND   each ground lane owns its node (name = prefix + lane id) at
#         the mission origin, carrying ONE MeshInstance3D child per
#         waypoint segment; every child sits at the segment midpoint
#         at y BAND_Y, is scaled (segment length, 1, BAND_WIDTH) and
#         carries the override material in the pinned lit-translucent
#         shape (unshaded + alpha + BAND_COLOR — bank-never-oracle:
#         the expectation is a pinned literal, not the material).
#  CLASS  the WEB-PROOF PROXY (the G2-fix): every segment mesh is a
#         PlaneMesh AND a PrimitiveMesh — engine-managed geometry, the
#         class the arena ground rasterizes from under GL Compatibility
#         (the G2 runtime-ArrayMesh never painted in the web export:
#         6 px of pure red on a VERIFIED build-phase frame,
#         w2-bandexp3). The class rows print; the served-browser pixel
#         re-check is the orchestrator's leg.
#  WPS    sampled band segments FOLLOW the lane waypoints: every
#         segment spans exactly its wp pair — endpoints derived from
#         the NODE midpoint (to_global of the unit plane's ±X ends)
#         match those wps within EPS-declared.
#  NEG    NO band node names an air lane (lane_a1/lane_a2 unbanded —
#         the plan's declared treatment; without this row an inverted
#         kind filter stays green).
# The planted-red for this card suppresses one ground band in
# lane_bands.paint_lane_bands and trips the BANDS row; transcript rides
# G2FIX-wave.log.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const LANE_BANDS := preload("res://scripts/lane_bands.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const HERO_IDS := ["warden", "deadeye", "embercaller"]  # deck seed (v4)
const VIEW := Vector2i(1280, 720)          # the A9 screenshot viewport
const N_GROUND := 3                        # gatefall ground lanes (pinned)
const N_AIR := 2                           # gatefall air lanes (pinned)
const EPS := 0.05                          # wp-follow tolerance, u
const UNSHADED := 0                        # BaseMaterial3D literals, pinned
const ALPHA := 1


var _failed := false
var _done := false
var _frames := 0
var _m = null


func _init() -> void:
	root.size = VIEW
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	graph["state"].set_deck(HERO_IDS.duplicate())   # starter deck (C13)
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                                  # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274                            # pinned seed, smoke idiom
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	if String(m.phase_kind) != "build":
		_fail("mission setup did not land the build phase")
		return
	_m = m


func _process(_delta: float) -> bool:
	if _failed:
		return true                       # quit(1) already fired
	_frames += 1
	if _frames == 4:
		_bands(_m)
		if not _failed:
			# A GDScript runtime error aborts _bands SILENTLY (rc stays 0,
			# LB-OK still prints — proven this session); only the pass's
			# own completion flag proves the transcript ran to its end.
			if not _done:
				_fail("band pass aborted mid-way (completion flag unset)")
			else:
				print("LB-OK")
				quit(0)
	return false


func _band_nodes(m) -> Dictionary:
	var by_lane := {}
	for c: Node in m.get_children():
		var nm := String(c.name)
		if not nm.begins_with(LANE_BANDS.BAND_PREFIX):
			continue
		by_lane[nm.trim_prefix(LANE_BANDS.BAND_PREFIX)] = c as Node3D
	return by_lane


func _bands(m) -> void:
	var ground := {}
	var air := {}
	for lid: String in m.lanes:
		var kind := String(m.lanes[lid]["kind"])
		if kind == "ground":
			ground[lid] = true
		elif kind == "air":
			air[lid] = true
	var bands := _band_nodes(m)
	if ground.size() != N_GROUND or air.size() != N_AIR:
		_fail("map lane kinds drifted: ground=%d air=%d (want %d/%d)" % [
				ground.size(), air.size(), N_GROUND, N_AIR])
		return
	if bands.size() != ground.size():
		_fail("band nodes = %d (want %d ground-lane bands)" % [
				bands.size(), ground.size()])
		return
	print("LB-BANDS n=%d ground=%d" % [bands.size(), ground.size()])
	for lid: String in ground:
		if not bands.has(lid):
			_fail("ground lane %s has no band node" % lid)
			return
		var node: Node3D = bands[lid]
		var wps: Array = m.lanes[lid]["wps"]
		if node == null:
			_fail("band %s is not a Node3D" % lid)
			return
		if node.position != Vector3.ZERO:
			_fail("band %s off origin: %s" % [lid, str(node.position)])
			return
		var segs = _segment_nodes(lid, node)   # -> Array | null (untyped)
		if _failed or segs == null:
			return
		if segs.size() != wps.size() - 1:
			_fail("band %s segments = %d (want one per wp segment = %d)" % [
					lid, segs.size(), wps.size() - 1])
			return
		print("LB-BAND %s segs=%d mat=1" % [lid, segs.size()])
		print("LB-CLASS %s mesh=PlaneMesh prim=1 segs=%d" % [
				lid, segs.size()])
		for i: int in segs.size():
			_segment(lid, segs[i], wps[i], wps[i + 1])
			if _failed:
				return
		_wps(lid, wps, segs)
		if _failed:
			return
	for lid: String in air:
		if bands.has(lid):
			_fail("NEG: air lane %s must carry NO band" % lid)
			return
	print("LB-NEG air=%d banded=0" % air.size())
	_done = true


func _segment_nodes(lid: String, band: Node3D):          # -> Array | null
	var segs: Array = []
	for c: Node in band.get_children():
		var mi := c as MeshInstance3D
		if mi == null:
			_fail("band %s child %s is not a MeshInstance3D" % [lid, str(c.name)])
			return null
		segs.append(mi)
	return segs


# One segment child pinned three ways: engine-managed geometry (CLASS —
# the web-rasterization fix), the pinned material shape, and the node
# transform: midpoint y = BAND_Y, scale = (segment length, 1,
# BAND_WIDTH), and the unit plane's ±X ends mapped to global land on
# the segment's two wps (either order) within EPS.
func _segment(lid: String, seg: MeshInstance3D, a: Vector3, b: Vector3) \
		-> void:
	if seg.mesh == null or not seg.mesh is PlaneMesh \
			or not seg.mesh is PrimitiveMesh:
		var cls := "null" if seg.mesh == null else seg.mesh.get_class()
		_fail("CLASS: band %s segment mesh is %s " % [lid, cls]
				+ "(want PlaneMesh/PrimitiveMesh)")
		return
	var mat := seg.material_override as StandardMaterial3D
	if mat == null or int(mat.shading_mode) != UNSHADED \
			or int(mat.transparency) != ALPHA \
			or mat.albedo_color != LANE_BANDS.BAND_COLOR:
		_fail("band %s segment is not the pinned lit-translucent shape" % lid)
		return
	if absf(seg.position.y - LANE_BANDS.BAND_Y) > EPS:
		_fail("band %s segment y = %s (want BAND_Y %s)" % [lid,
				str(seg.position.y), str(LANE_BANDS.BAND_Y)])
		return
	var seg_len := Vector3(b.x - a.x, 0.0, b.z - a.z).length()
	if absf(seg.scale.x - seg_len) > EPS \
			or absf(seg.scale.z - LANE_BANDS.BAND_WIDTH) > EPS:
		_fail("band %s segment scale = %s (want (%s, 1, %s))" % [lid,
				str(seg.scale), str(seg_len), str(LANE_BANDS.BAND_WIDTH)])
		return
	var ea := seg.to_global(Vector3(-0.5, 0.0, 0.0))
	var eb := seg.to_global(Vector3(0.5, 0.0, 0.0))
	var fwd := (ea - a).length() <= EPS and (eb - b).length() <= EPS
	var swapped := (ea - b).length() <= EPS and (eb - a).length() <= EPS
	if not fwd and not swapped:
		_fail("WPS: band %s segment ends %s/%s not at wps %s/%s within EPS %s" \
				% [lid, str(ea), str(eb), str(a), str(b), str(EPS)])


# Every waypoint must be an endpoint of some segment node — the strip's
# centreline walks the lane polyline (NODE midpoints + unit-plane
# ends), it does not approximate some other path.
func _wps(lid: String, wps: Array, segs: Array) -> void:
	for wp: Vector3 in wps:
		var hit := false
		for s: MeshInstance3D in segs:
			if (s.to_global(Vector3(-0.5, 0.0, 0.0)) - wp).length() <= EPS \
					or (s.to_global(Vector3(0.5, 0.0, 0.0)) - wp).length() <= EPS:
				hit = true
				break
		if not hit:
			_fail("WPS: band %s does not follow waypoint %s within EPS %s" \
					% [lid, str(wp), str(EPS)])
			return
	print("LB-WPS %s wp=%d matched=%d eps=%s" % [lid, wps.size(),
			wps.size(), str(EPS)])


func _fail(why: String) -> void:
	_failed = true
	print("LB-FAIL " + why)
	quit(1)
