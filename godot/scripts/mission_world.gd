# mission_world — the map build (lanes + cores) and the C5 core mirror
# of the mission root (W16 split of mission.gd, MC 11274.1.28 / card
# 11384; authored W6, MC 11274.1.13 / card 11308). Pure move — bodies
# byte-identical. C7 map data shapes the lane records (closed-until-
# sub-death opens_lanes reading) and the core objects; refresh_cores
# writes the C5-readable `cores` mirror the game_state snapshot reads
# by name — one write site, still owned through the mission root.
# V1 world pass (MC 11559) adds the two VISUAL mounts that ride this
# build: the core emblem (make_core child) and the arena paint, which
# build_cores calls once per mission build — NOT from mission.gd, whose
# file sits at the 400-line hygiene ceiling; this is the map-build and
# visual-mount file the brief names. G1 (MC 11690) adds the third such
# mount: the spawn-gate eye billboards, same build_cores hook. G2
# (MC 11694) adds the fourth: the lit lane bands, same hook, builder
# lives in lane_bands.gd.
# Zero step order / zero sim data touched — the lane rows, waypoints
# and core records are byte-identical; git show proves it.
extends RefCounted

const CORE_OBJ := preload("res://scripts/core_obj.gd")
const LANE_BANDS := preload("res://scripts/lane_bands.gd")
const MESH_CORE := preload("res://assets/mesh_core.tres")
const MAT_CORE := preload("res://assets/mat_core.tres")
const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")

# V1 presentation sizes (the sprite_bank ICON_PX precedent: presentation
# numbers live on the visual mount, pinned by sim/v1_world_probe.gd).
# ARENA_MODULATE: the framed board reads ~10% darker with a cool cast
# so the warm unit sprites + emblems stay readable on top of it.
const ARENA_MODULATE := Color(0.9, 0.9, 0.95)
# Emblem: the 3x4 core box tops out at y 2; a 6u wolf-crest centred at
# y 4.5 rides the box (sub cores inherit their 0.5 node scale, so the
# emblem follows core state — same single mount site for both kinds).
const CORE_EMBLEM_H := 6.0
const CORE_EMBLEM_Y := 4.5
# G1 gate-eye markers (MC 11690, V121-PLAN G1): the 5u plaque rides the
# spawner's map x/z at y 3 so it reads the gate mouth at the shipped
# D=64 rig without occluding the 2u mobs walking out of it (the
# CORE_EMBLEM_H precedent: the number lives on the visual mount).
const GATE_EYE_H := 5.0
const GATE_EYE_Y := 3.0


# V1 arena paint (MC 11559): the ground material albedo becomes the
# framed arena board from the ONE sprite_bank map, 1:1 over the whole
# plane (PlaneMesh UVs cover the plane; the board is NOT seamless so
# repeat is OFF). The ground node's size/transform are never touched
# (placement raycasts + lane paths depend on them); mat_ground.tres on
# disk is the bank-null fallback material only — the override below is
# a runtime duplicate, applied every boot (V1 ships sprited: no shipped
# id renders greybox).
static func paint_arena(m) -> void:
	var ground := m.get_node_or_null("Ground") as MeshInstance3D
	if ground == null:
		return                                   # greybox stays greybox
	var mat := ground.material_override as StandardMaterial3D
	var tex := SPRITE_BANK.texture_for("ground_arena")
	if mat == null or tex == null:
		return
	mat = mat.duplicate()
	mat.albedo_texture = tex
	mat.albedo_color = ARENA_MODULATE
	mat.texture_repeat = false   # 4.7.2: a BOOL property (VERIFIED via ClassDB dump); OFF keeps the framed board 1:1
	ground.material_override = mat


static func build_lanes(m) -> void:
	var closed := {}
	for sub: Dictionary in m.map_def.get("cores", {}).get("subs", []):
		for lid: Variant in sub.get("opens_lanes", []):
			closed[String(lid)] = true
	for lane: Dictionary in m.map_def.get("lanes", []):
		var wps: Array[Vector3] = []
		for wp: Variant in lane.get("waypoints", []):
			wps.append(Vector3(float(wp[0]), float(wp[1]), float(wp[2])))
		m.lanes[String(lane["id"])] = {"id": String(lane["id"]),
			"kind": String(lane["kind"]), "wps": wps,
			"target": String(lane["target"]),
			"open": not closed.has(String(lane["id"]))}


static func build_cores(m) -> void:
	var cores_row: Dictionary = m.map_def.get("cores", {})
	m.core_main = make_core(m, "main", "main", cores_row.get("main", {}),
			Vector3.ONE)
	for sub: Dictionary in cores_row.get("subs", []):
		m.core_subs[String(sub["id"])] = make_core(
				m, String(sub["id"]), "sub", sub, Vector3(0.5, 0.5, 0.5))
	# V1 hook (DECLARED, MC 11559): painted ground SURFACE only — no sim
	# field, no step order (W7/W10 visual-hook mount precedent).
	paint_arena(m)
	# G1 hook (DECLARED, MC 11690): gate-eye billboards at the spawner
	# positions — same visual-mount home, zero sim data.
	paint_spawn_gates(m)
	# G2 hook (DECLARED, MC 11694): lit bands on the GROUND lane polylines
	# of m.lanes — same visual-mount home, read-only, air lanes unbanded.
	LANE_BANDS.paint_lane_bands(m)


# G1 spawn-gate eyes (MC 11690, V121-PLAN G1): one billboard per
# m.map_def["spawners"] row. The WINGED variant marks the gates that
# carry an air lane — read from the RAW map lane rows' "spawner" key
# (build_lanes drops that key, so this reads map_def directly, a public
# read; gatefall: spawn_a/spawn_b carry lane_a1/a2, spawn_c plain).
# Null-safe like every sprite_bank consumer: an un-sprited id mounts
# nothing and no crash (the icon_core guard idiom).
static func paint_spawn_gates(m) -> void:
	var air: Dictionary = {}
	for lane: Dictionary in m.map_def.get("lanes", []):
		if String(lane.get("kind", "")) == "air":
			air[String(lane.get("spawner", ""))] = true
	for sid: String in m.map_def.get("spawners", {}):
		var eye := SPRITE_BANK.make_sprite(
				"icon_gate_eye_air" if air.has(sid) else "icon_gate_eye",
				GATE_EYE_H)
		if eye == null:
			continue
		var p: Array = m.map_def["spawners"][sid]
		eye.position = Vector3(float(p[0]), GATE_EYE_Y, float(p[2]))
		m.add_child(eye)


static func make_core(m, id: String, kind: String, row: Dictionary, sc: Vector3):
	var rec = CORE_OBJ.new()
	rec.id = id
	rec.kind = kind
	rec.hp_max = float(row["hp"][m.difficulty])
	rec.hp = rec.hp_max
	var p: Array = row.get("pos", [0, 0, 0])
	rec.pos = Vector3(float(p[0]), float(p[1]), float(p[2]))
	rec.opens_lanes = row.get("opens_lanes", [])
	var node := MeshInstance3D.new()
	node.mesh = MESH_CORE.duplicate()
	node.material_override = MAT_CORE.duplicate()
	node.scale = sc
	node.position = rec.pos   # mission-local space (root at origin)
	# V1 core emblem (MC 11559): the gold wolf-crest billboard rides the
	# box (the box stays), parented to the core node itself so it walks
	# with the core's scale/state. Null-safe like every sprite_bank
	# consumer: a null sheet means no child and no crash — the guard
	# rides future un-sprited ids; icon_core itself IS committed (bank
	# TEXTURES), so the emblem parents on every real boot.
	var emblem := SPRITE_BANK.make_sprite("icon_core", CORE_EMBLEM_H)
	if emblem != null:
		emblem.position = Vector3(0, CORE_EMBLEM_Y, 0)
		node.add_child(emblem)
	m.add_child(node)
	rec.node = node
	return rec


static func refresh_cores(m) -> void:
	var subs: Array = []
	for sid: String in m.core_subs:
		subs.append({"id": sid, "hp": float(m.core_subs[sid].hp),
			"max": float(m.core_subs[sid].hp_max)})
	m.cores = {"main": {"hp": float(m.core_main.hp),
			"max": float(m.core_main.hp_max)}, "subs": subs}
