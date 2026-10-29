# g1_gate_eye_probe — the G1 spawn-gate eye headless proof (MC card
# 11690 / V121-PLAN G1). Boot idiom = v1_world_probe (itself v4):
# mission.tscn instantiated, _ready and setup driven directly (E5), the
# pinned smoke seed, root.size = the served canvas.
# Rows (machine lines, any failure prints G1E-FAIL <why> and quits 1):
#  EYES   the mission root carries EXACTLY 3 gate-eye billboards — the
#         spawner-row count of the shipped gatefall map (pinned n=3).
#  MARK   each spawner row of m.map_def has its marker at the map x/z,
#         the pinned mount y, on a COMMITTED sheet path (never through
#         the bank — the v11_sprite_probe bank-as-oracle lesson) and
#         billboarded.
#  WING   the WINGED sheet sits on spawn_a AND spawn_b exactly (they
#         carry lane_a1/a2 — the plan's declared reading, pinned here
#         as a literal set, never re-derived by the mechanism).
#  NEG    spawn_c carries the PLAIN sheet and NOT the winged one — the
#         negative leg; without it a "winged on a,b" pin passes while
#         the filter is inverted (fleet negative-leg rule).
# The planted-red for this card inverts the winged branch in
# mission_world.paint_spawn_gates (air.has -> not air.has) and trips
# the WING row; transcript rides G1-wave.log.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MISSION_WORLD := preload("res://scripts/mission_world.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const HERO_IDS := ["warden", "deadeye", "embercaller"]  # deck seed (v4)
const VIEW := Vector2i(1280, 720)          # the A9 screenshot viewport
const EYE_PATH := "res://assets/v11/icon_gate_eye.png"
const EYE_AIR_PATH := "res://assets/v11/icon_gate_eye_air.png"
const WINGED := ["spawn_a", "spawn_b"]  # the plan-declared air carriers (gatefall)
const N_SPAWNERS := 3                    # gatefall map rows (pinned, not derived)
const BILLBOARD_ENABLED := 1             # BaseMaterial3D.BillboardMode literal pin
const EYE_SCALE := 5.0 / (512.0 / 100.0)  # make_sprite math, pinned

var _failed := false
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
		_eyes(_m)
		if not _failed:
			print("G1E-OK")
			quit(0)
	return false


func _eyes(m) -> void:
	var by_id := {}
	var n := 0
	for c: Node in m.get_children():
		var spr := c as Sprite3D
		if spr == null or spr.texture == null:
			continue
		var path := String(spr.texture.resource_path)
		if path != EYE_PATH and path != EYE_AIR_PATH:
			continue
		n += 1
		for sid: String in m.map_def["spawners"]:
			var p: Array = m.map_def["spawners"][sid]
			if spr.position.x == float(p[0]) \
					and spr.position.z == float(p[2]):
				by_id[sid] = spr
	if n != N_SPAWNERS:
		_fail("gate-eye markers = %d (want %d)" % [n, N_SPAWNERS])
		return
	print("G1E-EYES n=%d" % n)
	for sid: String in m.map_def["spawners"]:
		if not by_id.has(sid):
			_fail("spawner %s has no marker at its map position" % sid)
			return
		var spr: Sprite3D = by_id[sid]
		var p: Array = m.map_def["spawners"][sid]
		if spr.position != Vector3(float(p[0]), MISSION_WORLD.GATE_EYE_Y,
				float(p[2])):
			_fail("marker %s off the pinned mount: pos=%s (want y %s at map x/z)" % [
					sid, str(spr.position), str(MISSION_WORLD.GATE_EYE_Y)])
			return
		if int(spr.billboard) != BILLBOARD_ENABLED:
			_fail("marker %s is not a billboard: %d" % [sid, int(spr.billboard)])
			return
		if not is_equal_approx(spr.scale.x, EYE_SCALE):
			_fail("marker %s scale drifted: %s" % [sid, str(spr.scale.x)])
			return
		print("G1E-MARK %s pos=%s tex=%s" % [sid, str(spr.position),
				String(spr.texture.resource_path)])
	var winged := {}
	for sid: String in by_id:
		if String((by_id[sid] as Sprite3D).texture.resource_path) == EYE_AIR_PATH:
			winged[sid] = true
	var want := ""
	for sid: String in WINGED:
		want += ("" if want == "" else ",") + String(sid)
	var got := ""
	for sid: String in winged:
		got += ("" if got == "" else ",") + String(sid)
	if winged.size() != WINGED.size():
		_fail("winged markers = %d (want %d)" % [winged.size(), WINGED.size()])
		return
	for sid: String in WINGED:
		if not winged.has(sid):
			_fail("WING: %s must carry the winged sheet, got: %s" % [sid, got])
			return
	print("G1E-WING want=%s got=%s" % [want, got])
	if winged.has("spawn_c") \
			or String((by_id["spawn_c"] as Sprite3D).texture.resource_path) != EYE_PATH:
		_fail("NEG: spawn_c must be the PLAIN eye, not the winged sheet")
		return
	print("G1E-NEG spawn_c plain=1 air=0")


func _fail(why: String) -> void:
	_failed = true
	print("G1E-FAIL " + why)
	quit(1)
