# decor — the v1.6 V-F world decor (MC 12111, V16-PLAN-c2 §3 W2 V-F,
# pillar P6): STATIC stacked-primitive trees/rocks along the V-A rim
# walls sell SCALE at the board edge (F-BUILD: the only scale sellers
# were baked grass specks in the ground texture). The layout is 100%
# const data (ROWS below) — no RNG anywhere (the bare-rand ban), so
# every build is byte-identical (test_decor's determinism leg compares
# two full builds). Instances are STATIC: this file owns zero per-frame
# code, zero scripts on scene nodes, zero _process — the build runs
# once from mission_world.build_cores (the paint_arena/G1/G2/V-A visual
# hook precedent; mission.gd at its 400 ceiling adds ZERO lines).
# Node-class law (L5, the G2 web lesson kb 2d5274003): engine-managed
# PrimitiveMesh ONLY as the source mesh of every prop (trunk/canopy =
# CylinderMesh, rock = BoxMesh — the classes V-A's fortress already
# proves rasterize on web). Instancing rides MultiMeshInstance3D (the
# pillar's word); its web rasterization is PROVEN by this card's served
# leg BEFORE merge (plan V-F leg 1) — if that proof had failed the
# declared fallback is one MeshInstance3D per prop (the lane_bands
# idiom) behind the SAME fill()/build_decor() seam.
# Shadow law (V-A's DECLARED ruling, scene row verified): env_greybox
# ambient is DISABLED, so EVERY material here carries the same emission
# floor as diorama.gd and nothing casts — one rule, one shape.
# Budget law: MAX_PROPS caps the static PROPS (trees+rocks); the part
# census (props × stacked parts) is pinned by the SAME test_decor
# probe, so any growth past the budget reddens the count leg.
extends RefCounted

const DIORAMA := preload("res://scripts/diorama.gd")

const DECOR_NAME := "Decor"          # the container node marker
const XFORMS_META := "gw_xforms"     # authored-transform stamp (see _emit)
const MAX_PROPS := 40                # budget: total static props (plan row)
# The rim shape is READ from the V-A builder (the plan's own coupling:
# "placement needs V-A's rim shape") — one source for wall top/line, so
# decor can never drift off the walls it stands on.
const RIM_Y := DIORAMA.RIM_H                       # wall top face
const RIM_LINE := DIORAMA.BOARD_HALF + DIORAMA.RIM_T * 0.5  # wall center
const EMISSION_FILL := 0.3           # the diorama.gd shadow-ruling floor
const BARK_TINT := Color(0.42, 0.3, 0.2)
const CANOPY_TINT := Color(0.18, 0.42, 0.26)   # deep pine: the DECOR-region
                                               # census colour, distinct
                                               # from the old board grass
const ROCK_TINT := Color(0.75, 0.72, 0.66)
# Unit prop meshes at scale 1 (the lane_bands unit-mesh idiom: the
# instance transform carries the size): trunk h 3.0, canopy h 4.0 cone,
# rock a 2.0 box. Parts stack: canopy base sits on the trunk top.
const TRUNK_H := 3.0
const TRUNK_R := 0.45
const CANOPY_H := 4.0
const CANOPY_R := 1.7
const ROCK_SIZE := Vector3(2.0, 1.6, 2.0)
# Trunk height above the rim-line so crowns clear the 3u wall + the 6u
# corner towers only partially: trees read 5-8u tall AT THE RIM.
# LAYOUT — the deterministic table (row = [x, z, scale, yaw]):
# 14 trees + 10 rocks = 24 props, 38 parts (trees carry trunk+canopy),
# both under budget. Every row sits on a rim-wall centerline (±RIM_LINE
# on one axis, the other axis inside +-RIM_LINE) and clear of the 6u
# corner towers (|x|,|z| >= 84 or the row moves inward); zero RNG, zero
# derived randomness — re-ordering this table is a DATA edit reddening
# the determinism/counts legs, never a runtime shuffle.
const TREES := [
	[-66.0, -RIM_LINE, 1.00, 0.10],
	[-52.0, -RIM_LINE, 1.25, 0.55],
	[-18.0, -RIM_LINE, 0.90, 1.10],
	[14.0, -RIM_LINE, 1.15, 0.30],
	[36.0, -RIM_LINE, 0.95, 0.80],
	[58.0, -RIM_LINE, 1.30, 1.40],
	[-RIM_LINE, -60.0, 1.10, 0.20],
	[-RIM_LINE, -24.0, 0.85, 0.95],
	[-RIM_LINE, 18.0, 1.20, 1.25],
	[-RIM_LINE, 56.0, 0.95, 0.45],
	[RIM_LINE, -66.0, 1.05, 1.60],
	[RIM_LINE, -12.0, 1.25, 0.05],
	[RIM_LINE, 40.0, 0.90, 0.70],
	[-30.0, RIM_LINE, 1.10, 1.50],
]
const ROCKS := [
	[-76.0, -RIM_LINE, 0.70, 0.35],
	[-34.0, -RIM_LINE, 0.95, 0.90],
	[-2.0, -RIM_LINE, 0.60, 1.30],
	[26.0, -RIM_LINE, 0.85, 0.15],
	[74.0, -RIM_LINE, 0.75, 0.60],
	[-RIM_LINE, -42.0, 0.80, 1.05],
	[-RIM_LINE, 4.0, 0.65, 0.25],
	[-RIM_LINE, 70.0, 0.90, 1.45],
	[RIM_LINE, -38.0, 0.70, 0.75],
	[RIM_LINE, 66.0, 0.85, 0.50],
]


# Mount once from mission_world.build_cores (the visual-hook precedent).
# One container node; the three instanced part-nodes parent INSIDE it.
static func build_decor(m) -> void:
	var decor := Node3D.new()
	decor.name = DECOR_NAME
	fill(decor)
	m.add_child(decor)                   # ONE add_child, one mount


# Fill a container with every prop. PUBLIC seam on purpose: test_decor's
# determinism leg calls it on two containers and byte-compares the
# serialized builds (two builds, one mechanism — no test-only copy).
static func fill(decor: Node) -> void:
	var bark := _mat(BARK_TINT)
	var canopy := _mat(CANOPY_TINT)
	var rock := _mat(ROCK_TINT)
	var trunks: Array[Transform3D] = []
	var canopies: Array[Transform3D] = []
	for row: Array in TREES:
		var s: float = float(row[2])
		var yaw: float = float(row[3])
		var at := Vector3(float(row[0]), RIM_Y, float(row[1]))
		trunks.append(_xform(at, yaw, Vector3(s, s, s)))
		canopies.append(_xform(at + Vector3(0.0, s * TRUNK_H \
				+ s * CANOPY_H * 0.5, 0.0), yaw, Vector3(s, s, s)))
	var stones: Array[Transform3D] = []
	for row: Array in ROCKS:
		var s2: float = float(row[2])
		stones.append(_xform(Vector3(float(row[0]), RIM_Y \
				+ s2 * ROCK_SIZE.y * 0.35, float(row[1])), \
				float(row[3]), Vector3(s2, s2, s2)))
	_emit(decor, "PropTrunks", _trunk_mesh(), bark, trunks)
	_emit(decor, "PropCanopies", _canopy_mesh(), canopy, canopies)
	_emit(decor, "PropRocks", _rock_mesh(), rock, stones)


# ONE MultiMesh construction site: engine-managed source mesh + the
# static instance transforms, no per-frame anything. cast_shadow OFF
# (V-A's ruling), material_override carries the emission floor. The
# transforms are ALSO stamped onto the node as meta (XFORMS_META):
# runtime MultiMesh transforms live server-side (the 4.7 set/get
# round-trips through the RenderingServer — headless reads back ZERO
# for every instance, VERIFIED this session), so the probe's authored-
# build legs read this CPU-side stamp (never a duplicated arithmetic
# oracle), while the served leg proves the server-side copy PAINTS in
# the right place. Data-only, zero per-frame, never read by the sim.
static func _emit(parent: Node, node_name: String, src: PrimitiveMesh,
		mat: StandardMaterial3D, xforms: Array[Transform3D]) -> void:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = src                       # the engine-managed source mesh
	mm.instance_count = xforms.size()
	for i: int in xforms.size():
		mm.set_instance_transform(i, xforms[i])
	var node := MultiMeshInstance3D.new()
	node.name = node_name
	node.multimesh = mm
	node.set_meta(XFORMS_META, xforms)
	node.material_override = mat
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(node)


# Unit trunk (the size rides the instance scale).
static func _trunk_mesh() -> CylinderMesh:
	var mesh := CylinderMesh.new()
	mesh.top_radius = TRUNK_R * 0.7
	mesh.bottom_radius = TRUNK_R
	mesh.height = TRUNK_H
	return mesh


# Unit canopy cone: top radius ~0 sells the stylized pine read.
static func _canopy_mesh() -> CylinderMesh:
	var mesh := CylinderMesh.new()
	mesh.top_radius = 0.01
	mesh.bottom_radius = CANOPY_R
	mesh.height = CANOPY_H
	return mesh


# Unit rock box (yaw-varied per instance).
static func _rock_mesh() -> BoxMesh:
	var mesh := BoxMesh.new()
	mesh.size = ROCK_SIZE
	return mesh


static func _xform(at: Vector3, yaw: float, scale: Vector3) -> Transform3D:
	var basis := Basis(Vector3.UP, yaw).scaled(scale)
	return Transform3D(basis, at)


# Flat tinted material with the diorama emission floor baked in — the
# same lit shape as every other v1.6 primitive mass (no texture: the
# decor read is silhouette + colour, the sheets stay with the fortress).
static func _mat(tint: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = tint
	mat.emission_enabled = true
	mat.emission = Color(tint.r * EMISSION_FILL, tint.g * EMISSION_FILL,
			tint.b * EMISSION_FILL)
	return mat
