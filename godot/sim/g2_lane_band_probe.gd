# g2_lane_band_probe — the G2 lit lane band headless proof (MC card
# 11694 / V121-PLAN G2). Boot idiom = g1_gate_eye_probe (itself
# v1_world_probe): mission.tscn instantiated, _ready and setup driven
# directly (E5), the pinned smoke seed, root.size = the served canvas.
# Rows (machine lines, any failure prints LB-FAIL <why> and quits 1):
#  BANDS  the mission root carries EXACTLY one band node per GROUND
#         lane of m.lanes (derived count + pinned n=3 for gatefall).
#  BAND   each ground lane owns its node (name = prefix + lane id), the
#         node sits at mission origin (verts carry lane-local coords),
#         verts are the pinned one-quad-per-segment count, and the
#         override material is the pinned lit-translucent shape
#         (unshaded + alpha + BAND_COLOR — bank-never-oracle: the
#         expectation is a pinned literal, not the material itself).
#  WPS    sampled band vertices FOLLOW the lane waypoints: every ground
#         wp is the exact midpoint (EPS-declared) of a vertex pair
#         whose spread is BAND_WIDTH — the band walks the same polyline
#         the sim walks, no duplicated lane geometry.
#  NEG    NO band node names an air lane (lane_a1/lane_a2 unbanded —
#         the plan's declared treatment; without this row an inverted
#         kind filter stays green).
# The planted-red for this card suppresses one ground band in
# lane_bands.paint_lane_bands and trips the BANDS row; transcript rides
# G2-wave.log.
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
		by_lane[nm.trim_prefix(LANE_BANDS.BAND_PREFIX)] = c as MeshInstance3D
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
		var node: MeshInstance3D = bands[lid]
		var wps: Array = m.lanes[lid]["wps"]
		if node.position != Vector3.ZERO:
			_fail("band %s off origin: %s" % [lid, str(node.position)])
			return
		var verts: PackedVector3Array = \
				node.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
		if verts.size() != 4 * (wps.size() - 1):
			_fail("band %s verts = %d (want one quad per segment = %d)" % [
					lid, verts.size(), wps.size() - 1])
			return
		var mat := node.material_override as StandardMaterial3D
		if mat == null or int(mat.shading_mode) != UNSHADED \
				or int(mat.transparency) != ALPHA \
				or mat.albedo_color != LANE_BANDS.BAND_COLOR:
			_fail("band %s is not the pinned lit-translucent shape" % lid)
			return
		print("LB-BAND %s verts=%d mat=1" % [lid, verts.size()])
		_wps(lid, wps, verts)
		if _failed:
			return
	for lid: String in air:
		if bands.has(lid):
			_fail("NEG: air lane %s must carry NO band" % lid)
			return
	print("LB-NEG air=%d banded=0" % air.size())
	_done = true


# Every waypoint must be the midpoint (within EPS, all three axes) of a
# vertex pair spread by BAND_WIDTH — the strip's centreline walks the
# lane polyline, it does not approximate some other path.
func _wps(lid: String, wps: Array, verts: PackedVector3Array) -> void:
	for wp: Vector3 in wps:
		var hit := false
		for i: int in verts.size():
			for j: int in range(i + 1, verts.size()):
				var mid := (verts[i] + verts[j]) * 0.5
				if (mid - wp).length() > EPS:
					continue
				if absf((verts[i] - verts[j]).length() \
						- LANE_BANDS.BAND_WIDTH) <= EPS:
					hit = true
					break
			if hit:
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
