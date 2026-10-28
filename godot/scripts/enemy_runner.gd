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
# Sprite visuals (V1.1-a, MC 11466): the bank answers first; the
# committed sheet moves with the record's pos like the mesh did. No
# committed sheet (future ids) keeps the primitive —
# the same add/move/free lifecycle either way, one path.

extends Node3D

const LANE_PATH := preload("res://scripts/lane_path.gd")
const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")

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
	var node: Node3D = SPRITE_BANK.make_sprite(String(row["enemy_id"]),
			SPRITE_BANK.WORLD_H_UNIT)
	if node == null:
		node = MeshInstance3D.new()
		if bool(def.get("fly", false)):
			node.mesh = MESH_AIR.duplicate()
			node.material_override = MAT_AIR.duplicate()
		else:
			node.mesh = MESH_GROUND.duplicate()
			node.material_override = MAT_GROUND.duplicate()
	add_child(node)
	node.position = lane["wps"][0]
	# Facing at spawn: the sheet reads the FIRST lane step (V2: a
	# left-facing sheet mirrors only when the walk heads screen-right).
	var wps: Array = lane["wps"]
	if wps.size() > 1:
		SPRITE_BANK.face(node, float((wps[1] as Vector3).x)
				- float((wps[0] as Vector3).x))
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


# Nearest live entity within r of pos ({} = none) — the ONE search loop
# (W16 dedup: hero_combat._nearest and defense_obj._nearest were this
# same loop over the runner's records; both now delegate HERE). Air
# entities carry their authored waypoint y (F16), which plain 3D
# distance weighs naturally — the declared melee-reach reading, no
# fly-flag branch.
func nearest(pos: Vector3, r: float) -> Dictionary:
	var best: Dictionary = {}
	var best_d := r
	for ent: Dictionary in entities:
		var d: float = (ent["pos"] as Vector3).distance_to(pos)
		if d <= best_d:
			best_d = d
			best = ent
	return best


# Every live entity within r of pos (aoe application; W16 dedup of the
# hero_combat copy, same records, same read).
func in_range(pos: Vector3, r: float) -> Array:
	var picked: Array = []
	for ent: Dictionary in entities:
		if (ent["pos"] as Vector3).distance_to(pos) <= r:
			picked.append(ent)
	return picked


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
		var old_pos: Vector3 = ent["pos"]
		var mv: Dictionary = LANE_PATH.advance(
				ent["pos"], ent["lane"]["wps"], float(ent["speed"]), delta)
		ent["pos"] = mv["pos"]
		ent["wp_index"] = int(mv["wp_index"])
		ent["node"].position = mv["pos"]   # mission-local space (root identity)
		# The ONE shared facing mechanism (V2): a step toward screen-right
		# flips the left-facing enemy sheet; a no-op on greybox nodes.
		SPRITE_BANK.face(ent["node"], (mv["pos"] as Vector3).x - old_pos.x)
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
