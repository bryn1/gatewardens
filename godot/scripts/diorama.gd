# diorama — the v1.6 V-A fortress plateau (MC 12081, V16-PLAN-c2 §3 V-A,
# the milestone HEART): the flat checkered board floating in a void
# becomes a FORTRESS on stone. The play plane stays the FORTRESS TOP —
# all height lives OUTSIDE/BELOW the grid: a cliff-skirt plateau mass
# under the plane, rim walls + corner towers on the board rim, one
# gatehouse at each map spawner, and a keep body under the main core.
# The grid is FROZEN: placement slots are discrete waypoint candidates
# (defense_placer._build_slots), zero raycasts exist, and the ground
# node's transform/size are NEVER touched — test_diorama byte-pins the
# ground transform as the grid-frozen proof.
# Geometry law (the G2 web lesson, kb 2d5274003): engine-managed
# PrimitiveMesh ONLY — BoxMesh/CylinderMesh (the core box already proves
# BoxMesh rasterizes on web); NO runtime ArrayMesh, NO get_image().
# Textures ride the ONE sprite_bank id map (L5): the fortress_stone
# sheet is this file's only consumer; a null sheet degrades to the
# tinted flat material, never a crash (the bank null-safe idiom).
# Budget law (DA F-2): total fortress primitives are budget-pinned <=
# MAX_PRIMITIVES, counted by the SAME test_diorama probe (the shadow
# pass cost that motivated it is deferred WITH the shadows — see the
# SHADOW RULING below). All presentation numbers live HERE on the
# builder (the lane_bands/sprite_bank ICON_PX doctrine, ungoverned file).
extends RefCounted

const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")

const FORTRESS_NAME := "Fortress"          # the container node marker
const MAX_PRIMITIVES := 30                 # DA F-2 node budget
const STONE_ID := "fortress_stone"         # the ONE bank id consumed

# Board frame: mirrors mesh_plane.tres (PlaneMesh 160x160 at the origin,
# the value v1_world_probe byte-pins) — the plateau hangs off its edges.
const BOARD_HALF := 80.0
const PLATEAU := Vector3(168.0, 22.0, 168.0)
# Plateau centre Y carries its TOP FACE flush with the play plane (y 0):
# the ground stays the walkable surface, the stone reads beneath it.
const PLATEAU_Y := -PLATEAU.y * 0.5
const RIM_H := 3.0                         # rim wall height above stone
const RIM_T := 4.0                         # rim wall thickness
const TOWER_H := 6.0                       # corner tower height
const TOWER_R := 3.5
const GATE_TOWER_H := 5.5
const GATE_TOWER_R := 1.6
const GATE_GAP := 2.6                      # tower offset beside the lane
const GATE_LENTEL := Vector3(7.0, 1.6, 2.4)
const GATE_LENTEL_Y := GATE_TOWER_H + GATE_LENTEL.y * 0.5
# Keep body under the main core. Height 4.0 is CREST CLEARANCE: the
# core's pinned crest sprite rides y 4.5 (another card's pin — it may
# not move); at the first 5.5 body the served describe-image read the
# crest as a "small dark object" half-swallowed by the roof. A 4.0 keep
# seats the emblem's lower third at roofline, the rest against sky —
# and the 7.5 turrets still tower over the body.
const KEEP := Vector3(9.0, 4.0, 9.0)
const KEEP_TURRET_H := 7.5
const KEEP_TURRET_R := 1.5
const KEEP_TURRET_XZ := 4.5                # turret inset from the keep face
# Warm sandstone tints over the committed stone sheet (presentation
# consts, the ARENA_MODULATE precedent): the cliff reads darker/deeper
# than the sunlit walls.
const STONE_TINT := Color(1.0, 0.92, 0.82)
const CLIFF_TINT := Color(0.62, 0.55, 0.5)
# DECLARED SHADOW RULING (this card, served-leg evidence): env_greybox
# ships ambient_light_source=1 = DISABLED (Godot's enum 0=BG/1=DISABLED/
# 2=COLOR — VERIFIED at the scene row; plan §0's "flat cool ambient 0.6"
# premise CONTRADICTED: the color/energy values sit under a DISABLED
# source). The scene's FIRST shaded geometry under that env painted
# unlit faces and ground shadows PURE BLACK on the served frame (black
# gate-shadow blob at spawn_c, black inner rim faces). So V-A ships
# CAST_SHADOW_OFF + an emission floor (albedo * EMISSION_FILL reads
# torch-lit warm, zero black faces). V-E owns the mission.tscn WorldEnv/
# Sun rows — when that env carries real ambient, re-enable casting in
# _box/_cyl (one line each); the SHADOW_CASTING const lives HERE so the
# flip is ONE word. No env/Sun line moved HERE (L2, the V-E ownership).
const SHADOW_CASTING := false              # GeometryInstance3D setting
const EMISSION_FILL := 0.3                 # ambient-substitute floor
                                         # (0.42 read blown-out on the
                                         # served re-shoot; 0.3 keeps
                                         # sunlit stone vs floor contrast)
# Stone-sheet UV scale on the primitive faces (box/cyl UVs are 0..1 per
# face, so > 1 repeats the masonry across the big plateau/wall faces).
const STONE_UV_SCALE := Vector3(4.0, 4.0, 4.0)


# Mount once from mission_world.build_cores (the paint_arena/G1/G2
# visual-hook precedent — mission.gd at its 400 ceiling adds ZERO
# lines). One container node; every primitive parents INSIDE it.
static func build_fortress(m) -> void:
	var fort := Node3D.new()
	fort.name = FORTRESS_NAME
	var stone := _stone_mat(STONE_TINT)
	var cliff := _stone_mat(CLIFF_TINT)
	# The cliff-skirt plateau mass: its top face IS the play plane.
	_box(fort, cliff, PLATEAU, Vector3(0.0, PLATEAU_Y, 0.0), "Plateau")
	_paint_rim(fort, stone)
	_paint_gates(fort, m, stone)
	_paint_keep(fort, m, stone)
	m.add_child(fort)                        # ONE add_child, one mount


# Rim walls on the four board edges + a corner tower at each corner —
# the silhouette that replaces the void at the frame's far band.
static func _paint_rim(fort, mat: StandardMaterial3D) -> void:
	var off := BOARD_HALF + RIM_T * 0.5
	var long_side := Vector3(2.0 * BOARD_HALF + RIM_T, RIM_H, RIM_T)
	var cross_side := Vector3(RIM_T, RIM_H, 2.0 * BOARD_HALF + RIM_T)
	_box(fort, mat, long_side, Vector3(0.0, RIM_H * 0.5, -off), "RimWall_n")
	_box(fort, mat, long_side, Vector3(0.0, RIM_H * 0.5, off), "RimWall_s")
	_box(fort, mat, cross_side, Vector3(-off, RIM_H * 0.5, 0.0), "RimWall_w")
	_box(fort, mat, cross_side, Vector3(off, RIM_H * 0.5, 0.0), "RimWall_e")
	for i: int in 4:
		var x := BOARD_HALF if i % 2 == 0 else -BOARD_HALF
		var z := BOARD_HALF if i < 2 else -BOARD_HALF
		_cyl(fort, mat, TOWER_R, TOWER_H, Vector3(x, TOWER_H * 0.5, z), \
				"CornerTower_%d" % i)


# One gatehouse per m.map_def["spawners"] row (the raw public read —
# the paint_spawn_gates precedent): two cylinder towers flanking the
# lane's exit direction + a lintel block across them. The exit
# DIRECTION rides build_lanes' own records (m.lanes, kind=="ground",
# first waypoint at the spawner) — no second lane model, no RNG.
static func _paint_gates(fort, m, mat: StandardMaterial3D) -> void:
	for sid: String in m.map_def.get("spawners", {}):
		var p: Array = m.map_def["spawners"][sid]
		var pos := Vector3(float(p[0]), 0.0, float(p[2]))
		var lat := _lane_lateral(m, pos)
		var base := "Gate_%s" % sid
		var dy := GATE_TOWER_H * 0.5
		_cyl(fort, mat, GATE_TOWER_R, GATE_TOWER_H,
				pos + Vector3(lat.x * GATE_GAP, dy, lat.z * GATE_GAP),
				base + "_tower_a")
		_cyl(fort, mat, GATE_TOWER_R, GATE_TOWER_H,
				pos + Vector3(-lat.x * GATE_GAP, dy, -lat.z * GATE_GAP),
				base + "_tower_b")
		var lintel := _box(fort, mat, GATE_LENTEL,
				pos + Vector3(0.0, GATE_LENTEL_Y, 0.0), base + "_lintel")
		lintel.rotation.y = atan2(-lat.z, lat.x)


# Lateral unit across the lane that EXITS this spawner (its first
# waypoint sits on the spawner — the shipped gatefall data). Ground
# lanes only; a spawner with no ground lane faces the mission origin
# (a declared map-data fallback, never RNG).
static func _lane_lateral(m, pos: Vector3) -> Vector3:
	var dir := Vector3.ZERO
	for lid: String in m.lanes:
		var lane: Dictionary = m.lanes[lid]
		if String(lane["kind"]) != "ground":
			continue
		var wps: Array = lane["wps"]
		if wps.size() < 2 or (wps[0] as Vector3).distance_to(pos) > 0.5:
			continue
		dir = (wps[1] as Vector3) - (wps[0] as Vector3)
		break
	if dir == Vector3.ZERO:
		dir = -pos
	if dir == Vector3.ZERO:
		dir = Vector3(1.0, 0.0, 0.0)
	dir.y = 0.0
	dir = dir.normalized()
	return Vector3(-dir.z, 0.0, dir.x)


# The keep body under the main core (map_def cores.main pos — the
# make_core read precedent) + four corner turrets. The main core's box
# and its crest emblem ride ON TOP untouched (the row-1b crest leg).
static func _paint_keep(fort, m, mat: StandardMaterial3D) -> void:
	var p: Array = m.map_def.get("cores", {}).get("main", {}).get( \
			"pos", [0.0, 0.0, 0.0])
	var pos := Vector3(float(p[0]), 0.0, float(p[2]))
	_box(fort, mat, KEEP, pos + Vector3(0.0, KEEP.y * 0.5, 0.0), "Keep")
	for i: int in 4:
		var sx: float = KEEP_TURRET_XZ if i % 2 == 0 else -KEEP_TURRET_XZ
		var sz: float = KEEP_TURRET_XZ if i < 2 else -KEEP_TURRET_XZ
		_cyl(fort, mat, KEEP_TURRET_R, KEEP_TURRET_H,
				pos + Vector3(sx, KEEP_TURRET_H * 0.5, sz),
				"KeepTurret_%d" % i)


# ONE shared stone material per build: the committed sheet through the
# ONE bank map, repeated on the primitive faces; a null sheet keeps the
# tinted flat material (greybox-safe, the bank consumer guard idiom).
static func _stone_mat(tint: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = tint
	mat.emission_enabled = true
	mat.emission = Color(tint.r * EMISSION_FILL, tint.g * EMISSION_FILL,
			tint.b * EMISSION_FILL)
	var tex := SPRITE_BANK.texture_for(STONE_ID)
	if tex != null:
		mat.albedo_texture = tex
		mat.texture_repeat = true    # 4.7.2: a BOOL property (mission_world
		mat.uv1_scale = STONE_UV_SCALE   # paint_arena VERIFIED-via-ClassDB idiom)
	return mat


# ONE BoxMesh construction site (the lane_bands ONE-mesh-site pin):
# engine-managed geometry, sized per node, named for the probe census.
static func _box(parent: Node, mat: StandardMaterial3D, size: Vector3,
		at: Vector3, node_name: String) -> MeshInstance3D:
	var node := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	node.mesh = mesh
	node.material_override = mat
	node.cast_shadow = (GeometryInstance3D.SHADOW_CASTING_SETTING_ON
			if SHADOW_CASTING else
			GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
	node.position = at
	node.name = node_name
	parent.add_child(node)
	return node


# ONE CylinderMesh construction site (the same primitive law).
static func _cyl(parent: Node, mat: StandardMaterial3D, radius: float,
		height: float, at: Vector3, node_name: String) -> void:
	var node := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = height
	node.mesh = mesh
	node.material_override = mat
	node.cast_shadow = (GeometryInstance3D.SHADOW_CASTING_SETTING_ON
			if SHADOW_CASTING else
			GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
	node.position = at
	node.name = node_name
	parent.add_child(node)
