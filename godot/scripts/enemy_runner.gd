# enemy_runner — lane-path follower for spawned enemies (Modules row
# scripts/enemy_runner.gd, MC 11274.1.13 / card 11308). Lane walk ONLY:
# gravity is NEVER applied on-lanes (air lanes ride the waypoint y the C7
# map authors, F16) and projectiles are ownerless (C4).
#
# Entity records are runner-local (reading on the card trail, consistent
# everywhere: the pinned mission row owns the SPAWN LOOP + alive cap, the
# pinned runner row owns the walk). step(delta) advances every record and
# returns the drained {dead, reached} events; the mission's funnel step
# (4) routes death/reach awards, so every reward rule stays at the single
# pinned funnel site.
#
# C2 crossing (binding): hp = enemies[id].hp[difficulty] resolved HERE;
# mission.gd holds no HP math. The `tables` param is the enemies table
# (Array of rows): the W3a GWTables dict door serves object-shaped files
# only, so the mission loads array-shaped files raw with FileAccess+JSON
# — the same scene-side raw read main.gd's boot-fail-fast row ships.
# Optional row key "hp_mult" carries the wave row's mods.hp_mult resolved
# by mission at schedule build (C8 ships no mods field in v1 — identity
# then); applied here as (1 + hp_mult).
#
# Greybox visuals: primitive meshes from assets/ per entity, moving with
# the record's pos; visuals are throwaway (3090 pipeline later).

extends Node3D

const LANE_PATH := preload("res://scripts/lane_path.gd")

const MESH_GROUND := preload("res://assets/mesh_capsule.tres")
const MESH_AIR := preload("res://assets/mesh_box.tres")
const MAT_GROUND := preload("res://assets/mat_enemy_ground.tres")
const MAT_AIR := preload("res://assets/mat_enemy_air.tres")

var difficulty := "normal"
var entities: Array = []    # runner-local entity dicts, walk order


func setup(difficulty_in: String) -> void:
	difficulty = difficulty_in


# C2: one entity from a C8 spawn row resolved onto one C7 lane record
# {id, wps:Array[Vector3], target, ...}. rng = the injected mission RNG
# (draws stay receiver-qualified, F2-1; no draw is needed at spawn time,
# but the pinned signature carries it).
func spawn(row: Dictionary, lane: Dictionary, tables, _rng) -> void:
	var def: Dictionary = {}
	for e: Dictionary in tables:
		if String(e.get("id", "")) == String(row["enemy_id"]):
			def = e
			break
	var hp := float(def["hp"][difficulty]) * (1.0 + float(row.get("hp_mult", 0.0)))
	var node := MeshInstance3D.new()
	if bool(def.get("fly", false)):
		node.mesh = MESH_AIR.duplicate()
		node.material_override = MAT_AIR.duplicate()
	else:
		node.mesh = MESH_GROUND.duplicate()
		node.material_override = MAT_GROUND.duplicate()
	add_child(node)
	node.position = lane["wps"][0]
	entities.append({
		"id": String(row["enemy_id"]),
		"def": def,
		"hp": hp,
		"hp_max": hp,
		"speed": float(def["speed"]),
		"lane": lane,
		"pos": lane["wps"][0],
		"wp_index": 0,
		"node": node,
	})


func alive_count() -> int:
	return entities.size()


# One lane-walk tick; returns the drained events {dead, reached} — both
# classes leave the walk list here, once, and their greybox nodes are
# freed. The caller applies awards (deaths) / core damage (reach) at the
# pinned funnel site, never here.
func step(delta: float) -> Dictionary:
	var dead: Array = []
	var reached: Array = []
	var keep: Array = []
	for ent: Dictionary in entities:
		if float(ent["hp"]) <= 0.0:
			dead.append(ent)
			ent["node"].queue_free()
			continue
		var mv: Dictionary = LANE_PATH.advance(
				ent["pos"], ent["lane"]["wps"], float(ent["speed"]), delta)
		ent["pos"] = mv["pos"]
		ent["wp_index"] = int(mv["wp_index"])
		ent["node"].position = mv["pos"]   # mission-local space (root identity)
		if bool(mv["arrived"]):
			reached.append(ent)
			ent["node"].queue_free()
			continue
		keep.append(ent)
	entities = keep
	return {"dead": dead, "reached": reached}


# Damage entry point for later waves (W7 hero_combat / W8 defense_obj).
# No death handling here: the next step() drains hp<=0 as a dead event.
func damage(ent: Dictionary, amount: float) -> void:
	ent["hp"] = float(ent["hp"]) - amount
