# range_ring — the G4 armed-ghost range ring (v1.2.1, MC 11707 / V121-PLAN
# row G4): ONE translucent YELLOW ring, flat on the ground, outer edge at
# the CURRENT tier range of the ARMED ghost. The radius is a towers.json
# TIER-ROW NUMBER the placer reads (tier_range) — never a literal here or
# in the placer (I2: placer/panel are governed, and this file is asked for
# that number, it never derives one).
#
# ONE mechanism riding the ghost lifecycle: the placer owns the aim/ghost
# state (G5, MC 11700) and its set_ghost/cancel_ghost/cycle_ghost are the
# shipped lifecycle chokepoints the G5 card pinned as the ghost API's
# EXTERNAL caller set — so those three call _sync_ring (arm/cycle SHOW and
# RESIZE; place, RMB/Escape cancel and the combat-lock all ride
# cancel_ghost, so they HIDE through the same single site). No second
# driver. SELECTION (declared finding, plan row G4 parenthetical): a real
# selection mechanism EXISTS in code (defense_panel.selected_uid +
# select_defense, player-reachable through the defense_rows_ui rows since
# W17c) — the ring stays GHOST-FIRST, the plan's declared case; a
# selected-defense leg would be a second trigger site + a ring-priority
# rule (armed AND selected at once) beyond this card's DoD, declared here,
# not silently skipped.
#
# GEOMETRY — the G2 ArrayMesh lesson (MC 11698) honored at the mechanism
# level: runtime ArrayMesh built correct nodes headless yet rasterized ~6
# px in the web export. This is a UNIT TorusMesh — engine-managed
# PrimitiveMesh geometry, the class family the G2 fix moved to (PlaneMesh)
# rasterizes under GL Compatibility/web — and the node TRANSFORM carries
# the range: scale.x == scale.z == the tier range number (the unit torus'
# outer_radius 1.0; the DATA leg asserts node scale == the towers.json
# number), scale.y flattens the tube to a ground ribbon. Only
# position/scale/visibility ever change after creation.
#
# RANGE-0 TREATMENT (Rev 2 / DA A4.1, binding): the five gate_blockade
# tier rows carry range 0 — show_ring() reads radius <= 0 as HIDE (a
# zero-radius dot reads as noise; hidden is the plan's answer). The
# negative leg is non-vacuous: the SAME node is proven visible for a
# positive-range family minutes before, WITH the ghost armed.
extends RefCounted

const RING_NAME := "RangeRing"        # the node name the probe reads by
const RING_Y := 0.05                  # rides above the ground and the G2
                                      # bands (BAND_Y 0.02), no z-fight
const RING_INNER := 0.92              # unit annulus: band width = 8% of range
const RING_FLATTEN := 0.2             # tube vertical extent -> flat ribbon
const RINGS := 32                     # torus segments (4.7 derives both
                                      #   directions from it)
const RING_COLOR := Color(1.0, 0.88, 0.25, 0.55)   # yellow, translucent


# Show THE ring at slot position `at` with outer edge `radius` (the tier
# range number the placer read). radius <= 0 = the declared NO-RING
# treatment above (it HIDES, never renders a dot).
static func show_ring(m, at: Vector3, radius: float) -> void:
	if radius <= 0.0:
		hide_ring(m)
		return
	var node := _ensure(m)
	node.visible = true
	node.position = Vector3(at.x, RING_Y, at.z)
	node.scale = Vector3(radius, RING_FLATTEN, radius)


# Hide THE ring (the node persists, visibility-only — the cancel/place/
# phase-lock answer; the ring rides the ghost, never the mission tree).
static func hide_ring(m) -> void:
	var node = m.get_node_or_null(NodePath(RING_NAME))
	if node != null:
		node.visible = false


# The ONE ring node, lazy on the FIRST positive show (a blockade-only
# session never grows one — m.get_node_or_null reads it as hidden either
# way): the mission-root child idiom the G2 bands proved web-painting,
# unit TorusMesh + the pinned G2 translucent-lit material shape.
static func _ensure(m) -> MeshInstance3D:
	var node = m.get_node_or_null(NodePath(RING_NAME))
	if node == null:
		node = MeshInstance3D.new()
		node.name = RING_NAME
		var torus := TorusMesh.new()      # ONE geometry-construction site
		torus.outer_radius = 1.0          # unit annulus: the SCALE carries
		torus.inner_radius = RING_INNER   #   the towers.json range number
		torus.rings = RINGS
		node.mesh = torus
		node.material_override = _ring_material()
		node.visible = false
		m.add_child(node)
	return node


# The ONE material shape, the pinned G2 lit-translucent contract (the
# mechanism G2 proved rasterizes in the web export): unshaded so it reads
# lit on the dark arena, alpha-blended so the painted ground shows through.
static func _ring_material() -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = RING_COLOR
	return mat
