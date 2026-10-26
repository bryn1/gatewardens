# mission_world — the map build (lanes + cores) and the C5 core mirror
# of the mission root (W16 split of mission.gd, MC 11274.1.28 / card
# 11384; authored W6, MC 11274.1.13 / card 11308). Pure move — bodies
# byte-identical. C7 map data shapes the lane records (closed-until-
# sub-death opens_lanes reading) and the core objects; refresh_cores
# writes the C5-readable `cores` mirror the game_state snapshot reads
# by name — one write site, still owned through the mission root.
extends RefCounted

const CORE_OBJ := preload("res://scripts/core_obj.gd")
const MESH_CORE := preload("res://assets/mesh_core.tres")
const MAT_CORE := preload("res://assets/mat_core.tres")


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
