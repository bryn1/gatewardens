extends CharacterBody3D

# hero_controller — CharacterBody3D move/jump/facing + the hero step entry
# (Modules row scripts/hero_controller.gd, MC 11274.1.14 / card 11321).
# Every movement number is read at setup from balance.feel + the heroes
# rows (F6) — zero balance literals in this file (I2 structural whitelist
# only). Reads the Bridge ONLY (pinned row): WASD via bridge.move_vector(),
# jump on the held "Enter" edge. Reading on the card trail: the bridge
# relay (W4, out of W7 scope) carries no Space code, so "Enter" is the
# shipped greybox jump until a controls wave widens bridge.gd by ruling.
# The camera rig is the mission root's (F8) — NOTHING here ever touches
# or re-parents it.
#
# Movement idiom: manual velocity integration (position += velocity*delta),
# the same -s-safe lane-walk mechanism enemy_runner ships; no
# move_and_slide, no physics-server dependence (E5/E3 discipline: the
# smoke drives every line of this file).
#
# Hero step (funnel slot 2, C12): step(delta) = pawn visual sync + move/
# jump/facing + hero_combat.tick. "Downed cannot act" holds at the single
# pinned gate: mission.step_hero returns BEFORE calling step() whenever
# the active hero is downed (C4).
#
# Pawn sync = the C4 swap semantics on the visual side: exactly the ACTIVE
# still-healthy hero's pawn node is visible; the old pawn is hidden
# (visible=false, the W6 destroyed-core idiom), never freed, and the per-
# hero pawns are children of THIS body so the active visual follows the
# hero stand. Hot-swap keys F1-F3 keep being consumed by mission step (5)
# exactly as W6 shipped — this file adds no press consumer.

const HERO_PAWN := preload("res://scenes/hero_pawn.tscn")
const HERO_COMBAT := preload("res://scripts/hero_combat.gd")

var mission = null
var feel: Dictionary = {}
var combat = null
var pawns: Dictionary = {}       # hero id -> pawn node (visibility = swap state)
var vel := Vector3.ZERO
var grounded := true


func setup(m) -> void:
	mission = m
	feel = m.balance.get("feel", {})
	combat = HERO_COMBAT.new()
	combat.setup(m)
	position = m.core_main.pos    # hero stand = main core stand (map data)
	for hid: Variant in m.deck:
		var pawn = HERO_PAWN.instantiate()
		pawn.name = "Pawn_" + String(hid)
		pawn.setup_pawn(String(hid))
		add_child(pawn)
		pawns[String(hid)] = pawn
	_sync_pawns()


# One funnel slot-(2) tick: visuals first (so a swap recorded last tick is
# reflected before anything moves), then move/jump/facing, then combat.
func step(delta: float) -> void:
	_sync_pawns()
	_move(delta)
	combat.tick(delta, position)   # the body's stand is the combat anchor


func _sync_pawns() -> void:
	var active_id := ""
	if mission.active < mission.deck.size():
		active_id = String(mission.deck[mission.active])
	for hid: String in pawns:
		var hs: Dictionary = mission.hero_state[hid]
		# hp>0 (not the downed flag) is the rule: same-tick hp writes land
		# before this sync, so the all-down state shows zero pawns even on
		# the tick the mission ends (step() no longer runs after outcome).
		pawns[hid].visible = hid == active_id and float(hs["hp"]) > 0.0


func _move(delta: float) -> void:
	var vec: Vector2 = mission.bridge.move_vector()
	var dir := Vector3(vec.x, 0.0, vec.y)   # W/S -> ∓z, A/D -> ±x (declared)
	var base: Dictionary = mission.hero_defs[mission.hero_id]["base"]
	var target := dir * float(base["speed"])
	var flat := Vector3(vel.x, 0.0, vel.z)
	var rate := float(feel.get("move_accel", 0.0))
	if dir.length_squared() <= 0.0:
		rate = float(feel.get("move_decel", 0.0))
	flat = flat.move_toward(target, rate * delta)
	vel.x = flat.x
	vel.z = flat.z
	# Jump + gravity: feel numbers only (F6/I2). Ground plane is the
	# mission-root y=0 sentinel (structural), the same plane lane_path
	# authors ground lanes on (F16: y never rewritten here either).
	if grounded and mission.bridge.held.has("Enter"):
		vel.y = float(feel.get("jump_speed", 0.0))
		grounded = false
	vel.y -= float(feel.get("gravity", 0.0)) * delta
	position += vel * delta
	if position.y <= 0.0:
		position.y = 0.0
		if vel.y < 0.0:
			vel.y = 0.0
			grounded = true
	# Facing: pawn visual yaw eases toward the move direction at the
	# feel rate (visual side of the body; pawns are children of this node).
	if Vector2(flat.x, flat.z).length_squared() > 0.0:
		var face := atan2(flat.x, flat.z)
		var t := minf(float(feel.get("facing_interp_rate", 0.0)) * delta, 1.0)
		rotation.y = lerp_angle(rotation.y, face, t)
