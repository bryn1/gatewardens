# tower_forms — V-B world tower visual (MC 12082, V16-PLAN-c2 §3 V-B,
# pillar P2 "real 3D tower structures"): primitive-composed 3D forms for
# the five placed-defense ids, replacing the medallion billboard on the
# WORLD node only (P2b: the HUD/picker icons ride the separate icon_*
# bank ids and are byte-untouched — defense_obj delegates here, the
# panel never does). Geometry is engine-managed PrimitiveMesh ONLY
# (BoxMesh/CylinderMesh — the L5 web-raster law, kb 2d5274003: runtime
# ArrayMesh never rasterizes on web; the G2 lane_bands lesson pinned);
# the materials are the shipped mat_defense_*.tres tints REUSED through
# per-build duplicate() (the greybox idiom, no invented palette).
# ALL presentation numbers live HERE (the sprite_bank ICON_PX /
# lane_bands doctrine: this file is deliberately outside the I2 governed
# set — defense_obj.gd stays governed-clean with zero literals, the BN1
# split). Tier variants (defense_obj.tier, 0-BASED): the base column
# grows by TIER_H per rung through the ONE body_height() home, plus
# addition steps at the declared thresholds; the upgrade repaint rebuilds
# the whole form through _make_visual (the V1.1-b swap slot unchanged).
# The shooters (tower-class rows) carry a child node named exactly
# "Turret" — the part tower_aim.gd yaws; blockade and trap have none
# (nothing aims: a blockade never fires, a snare is ground furniture).
# This is the scene's first non-billboard geometry, so it is the first
# thing the already-shadow-enabled Sun falls on (plan risk 7 — the V-G
# frame-time row owns the measurement; no per-frame code lives HERE).
extends RefCounted

const MAT_TOWER := preload("res://assets/mat_defense_tower.tres")
const MAT_BLOCKADE := preload("res://assets/mat_defense_blockade.tres")
const MAT_TRAP := preload("res://assets/mat_defense_trap.tres")

const FORM_NAME := "TowerForm"       # container name PREFIX (uid-suffixed:
                                     # duplicate sibling names are engine-
                                     # renamed to @Node3D@N on add_child —
                                     # the Row_%d uid idiom of defense_rows_ui)
const TURRET_NAME := "Turret"         # the aim driver's ONE node handle

# Shared ladder: the base column's height, read by every form (the
# test_tower_forms growth leg re-computes from THESE, never a copy).
const BASE_H := 1.8                   # T1 base column, world units
const TIER_H := 0.45                  # added height per upgrade rung

# Ballista — stone column, plank deck, firing stock on the Turret.
const BAL_BASE_R := 0.62
const BAL_DECK := Vector3(1.5, 0.22, 1.5)
const BAL_TURRET_Y := 0.6             # turret lift above the deck top
const BAL_BARREL := Vector3(0.26, 0.3, 2.4)   # long stock, +Z = facing
const BAL_STOCK := Vector3(0.3, 0.32, 1.0)

# Bombard — squat fat barrel drum; the cylinder barrel lies along +Z.
const BOMB_BASE_R := 0.9
const BOMB_H_FRAC := 0.75             # drum height = body_height * frac
const BOMB_H_MIN := 0.4               # floor so T1 still reads solid
const BOMB_TURRET_Y := 0.5
const BOMB_BARREL_R := 0.34
const BOMB_BARREL_L := 1.6
const BOMB_MUZZLE_R := 0.44
const BOMB_MUZZLE_L := 0.3

# Hailspire — tapered shaft under a rotated crystal cap.
const HAIL_SHAFT_R := 0.55
const HAIL_CAP := Vector3(0.8, 0.8, 0.8)     # cube, yawed 45 deg
const HAIL_TURRET_Y := 0.4
const HAIL_SPIRE := Vector3(0.22, 0.22, 1.9)  # aiming shard, +Z facing

# Gate blockade — a wall segment with corner posts (never aims).
const BLK_WALL := Vector3(2.4, 0.8, 0.9)      # width / T1 height / depth
const BLK_POST := Vector3(0.5, 0.4, 0.5)      # post section, +0.4 taller
const BLK_CREN := Vector3(0.45, 0.35, 0.55)   # top crenel block (T2+)

# Barbed snare — flat plate with spike rows (never aims).
const SNR_PLATE := Vector3(2.0, 0.24, 2.0)
const SNR_SPIKE := Vector3(0.16, 0.5, 0.16)

# Greybox fallback shapes for ids with no form yet (the bank-null
# greybox contract carried: never null, always something on the slot).
const GB_TOWER := Vector3(0.6, 3.6, 0.6)      # the old capsule footprint
const GB_BLOCKADE := Vector3(1.2, 1.2, 1.2)
const GB_TRAP := Vector3(2.0, 0.5, 2.0)

# Addition thresholds (0-BASED tiers): collar T2+, second step T3+.
const ADD_COLLAR_TIER := 1
const ADD_STEP_TIER := 2


# The ONE height home: T1..T5 base-column height (0-based tier index).
static func body_height(tier: int) -> float:
	return BASE_H + float(tier) * TIER_H


# Build the visual for one defense_obj record (READS id/class/tier/pos
# only — the same fields the medallion path read). Returns the container
# AT obj.pos; defense_obj owns adding it to the tree (contract kept:
# _make_visual hands back a positioned node, place_defense add_child's).
static func build(obj) -> Node3D:
	var root := Node3D.new()
	root.name = FORM_NAME + "_" + str(int(obj.uid))
	root.position = obj.pos
	var tier := int(obj.tier)
	match String(obj.trow["id"]):
		"ballista":
			_form_ballista(root, tier)
		"bombard":
			_form_bombard(root, tier)
		"hailspire_tower":
			_form_hailspire(root, tier)
		"gate_blockade":
			_form_blockade(root, tier)
		"barbed_snare":
			_form_snare(root, tier)
		_:
			_form_greybox(root, String(obj.class_id), tier)
	return root


static func _form_ballista(root: Node3D, tier: int) -> void:
	var mat := MAT_TOWER.duplicate()
	var h := body_height(tier)
	root.add_child(_cyl(BAL_BASE_R, BAL_BASE_R, h, Vector3(0, h * 0.5, 0), mat))
	if tier >= ADD_COLLAR_TIER:
		root.add_child(_cyl(0.95, 0.95, 0.16, Vector3(0, h * 0.55, 0), mat))
	root.add_child(_box(BAL_DECK, Vector3(0, h + 0.11, 0), mat))
	var turret := _turret(root, h + BAL_TURRET_Y)
	turret.add_child(_box(BAL_BARREL, Vector3(0, 0, BAL_BARREL.z * 0.5), mat))
	turret.add_child(_box(BAL_STOCK, Vector3(0, -0.1, -0.4), mat))


static func _form_bombard(root: Node3D, tier: int) -> void:
	var mat := MAT_TOWER.duplicate()
	var h := maxf(body_height(tier) * BOMB_H_FRAC, BOMB_H_MIN)
	root.add_child(_cyl(BOMB_BASE_R, BOMB_BASE_R, h, Vector3(0, h * 0.5, 0), mat))
	if tier >= ADD_COLLAR_TIER:
		root.add_child(_cyl(1.15, 1.15, 0.16, Vector3(0, h * 0.45, 0), mat))
	var turret := _turret(root, h + BOMB_TURRET_Y)
	turret.add_child(_barrel_cyl(BOMB_BARREL_R, BOMB_BARREL_R,
			BOMB_BARREL_L, Vector3(0, 0, BOMB_BARREL_L * 0.5), mat))
	if tier >= ADD_STEP_TIER:
		turret.add_child(_barrel_cyl(BOMB_MUZZLE_R, BOMB_MUZZLE_R,
				BOMB_MUZZLE_L, Vector3(0, 0, BOMB_BARREL_L + 0.1), mat))


static func _form_hailspire(root: Node3D, tier: int) -> void:
	var mat := MAT_TOWER.duplicate()
	var h := body_height(tier)
	root.add_child(_cyl(HAIL_SHAFT_R * 0.6, HAIL_SHAFT_R, h,
			Vector3(0, h * 0.5, 0), mat))
	if tier >= ADD_COLLAR_TIER:
		root.add_child(_cyl(0.85, 0.85, 0.16, Vector3(0, h * 0.5, 0), mat))
	var cap := _box(HAIL_CAP, Vector3(0, h + 0.25, 0), mat)
	cap.rotation.y = PI * 0.25              # diamond-set the crystal
	root.add_child(cap)
	var turret := _turret(root, h + HAIL_TURRET_Y + 0.25)
	turret.add_child(_box(HAIL_SPIRE, Vector3(0, 0, HAIL_SPIRE.z * 0.5), mat))
	if tier >= ADD_STEP_TIER:
		turret.add_child(_box(Vector3(0.3, 0.3, 0.3),
				Vector3(0, 0, -0.35), mat))


static func _form_blockade(root: Node3D, tier: int) -> void:
	var mat := MAT_BLOCKADE.duplicate()
	var wh := BLK_WALL.y + float(tier) * TIER_H * 0.5
	root.add_child(_box(Vector3(BLK_WALL.x, wh, BLK_WALL.z),
			Vector3(0, wh * 0.5, 0), mat))
	var ph := wh + BLK_POST.y
	for dx: float in [-BLK_WALL.x * 0.5, BLK_WALL.x * 0.5]:
		root.add_child(_box(Vector3(BLK_POST.x, ph, BLK_POST.z),
				Vector3(dx, ph * 0.5, 0), mat))
	if tier >= ADD_COLLAR_TIER:
		for dx: float in [-BLK_WALL.x * 0.25, BLK_WALL.x * 0.25]:
			root.add_child(_box(BLK_CREN, Vector3(dx, wh + 0.175, 0), mat))


static func _form_snare(root: Node3D, tier: int) -> void:
	var mat := MAT_TRAP.duplicate()
	root.add_child(_box(SNR_PLATE, Vector3(0, SNR_PLATE.y * 0.5, 0), mat))
	root.add_child(_box(SNR_SPIKE, Vector3(-0.55, 0.45, -0.4), mat))
	root.add_child(_box(SNR_SPIKE, Vector3(0.5, 0.45, 0.1), mat))
	root.add_child(_box(SNR_SPIKE, Vector3(-0.1, 0.45, 0.6), mat))
	if tier >= ADD_COLLAR_TIER:
		root.add_child(_box(SNR_SPIKE, Vector3(0.6, 0.45, -0.65), mat))
		root.add_child(_box(SNR_SPIKE, Vector3(-0.7, 0.45, 0.45), mat))


static func _form_greybox(root: Node3D, class_id: String, tier: int) -> void:
	match class_id:
		"tower":
			root.add_child(_box(GB_TOWER, Vector3(0, GB_TOWER.y * 0.5, 0),
					MAT_TOWER.duplicate()))
			_turret(root, GB_TOWER.y)      # future shooters aim too
		"blockade":
			root.add_child(_box(GB_BLOCKADE,
					Vector3(0, GB_BLOCKADE.y * 0.5, 0),
					MAT_BLOCKADE.duplicate()))
		_:
			root.add_child(_box(GB_TRAP, Vector3(0, GB_TRAP.y * 0.5, 0),
					MAT_TRAP.duplicate()))


# The aiming element: a bare Node3D (writes its rotation.y ONLY from
# tower_aim.gd — the visible yaw lives on its mesh children).
static func _turret(root: Node3D, y: float) -> Node3D:
	var t := Node3D.new()
	t.name = TURRET_NAME
	t.position = Vector3(0, y, 0)
	root.add_child(t)
	return t


static func _box(size: Vector3, at: Vector3, mat: StandardMaterial3D) \
		-> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	return _mesh_node(mesh, at, mat)


static func _cyl(r_top: float, r_bottom: float, h: float, at: Vector3,
		mat: StandardMaterial3D) -> MeshInstance3D:
	var mesh := CylinderMesh.new()
	mesh.top_radius = r_top
	mesh.bottom_radius = r_bottom
	mesh.height = h
	return _mesh_node(mesh, at, mat)


# A cylinder pointing +Z (its authored axis is +Y — the node tips it;
# that static tilt is the FORM, the yaw above it stays the driver's).
static func _barrel_cyl(r_top: float, r_bottom: float, h: float,
		at: Vector3, mat: StandardMaterial3D) -> MeshInstance3D:
	var mi := _cyl(r_top, r_bottom, h, at, mat)
	mi.rotation.x = PI * 0.5
	return mi


static func _mesh_node(mesh: Mesh, at: Vector3,
		mat: StandardMaterial3D) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.position = at
	mi.material_override = mat
	return mi
