# baseline_d64_kit — v1.3 zoom Z1 (MC 11812), ZOOM_SPEC stage S1 baseline
# capture (c2/DA P2-2): boots the UNMODIFIED mission and captures the ONE
# default-D64 frame that feeds §5 A2's byte-identity compare-basis, BEFORE
# S3 exists. The kit LIVES IN THIS AUDIT DIR (the zoom card forbids any
# code change outside .audits/) and runs by absolute -s path — verified
# working on this repo's Godot 4.7.2. Boot idiom = sim/v1_world_probe
# VERBATIM (mission.tscn instantiated, _ready + setup driven directly,
# pinned smoke seed 11274 — a router-boot kit rewrites its pixels every
# run through OS-entropy RNG, W3-wave.log lesson). Capture idiom =
# sim/v1_world_shot (root.get_texture().get_image().save_png under
# xvfb + opengl3, 1280x720, frame 120) — no second frame-capture
# mechanism is invented. The kit dispatches ZERO InputEvents (that is the
# "zero wheel input" of A2 — nothing is fed, not even a click). Rows
# (machine lines; any failure prints Z1-FAIL <why> and quits 1):
#  PHASE  the booted mission sits in the build phase, gatefall/normal,
#         the pinned seed.
#  RIG    the CameraRig/Camera3D origin + |origin| PRINTED FROM THE LIVE
#         ENGINE (quoted, not assumed) and pinned to the shipped default
#         row — the "D=64" shorthand is 63.909 u.
#  INPUT  bridge press/held queues empty after the capture frame: zero
#         input reached the mission.
#  SHOT   the ONE full 1280x720 frame saved to this dir.
# Run (repo root):
#   xvfb-run -a $G --rendering-driver opengl3 --path godot \
#       -s $PWD/.audits/20261031-1100-v13-zoom-plan/baseline_d64_kit.gd
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const HERO_IDS := ["warden", "deadeye", "embercaller"]       # deck seed (v4/v1W)
const SEED := 11274                                          # pinned smoke seed
const VIEW := Vector2i(1280, 720)
const CAPTURE_FRAME := 120                                   # v1_world_shot frame
const OUT := "/home/claudecode/Games/gatewardens/.audits/20261031-1100-v13-zoom-plan/baseline-default-D64.png"

# the shipped default rig row (mission.tscn CameraRig transform origin),
# quoted here ONLY as the expectation the LIVE engine output is pinned to:
const DEF_ORIGIN := Vector3(0, 47.47, 42.79)
const DEF_NORM := 63.909          # |DEF_ORIGIN| — the "D=64" shorthand

var _frames := 0
var _failed := false
var _m = null
var _bridge = null
var _shot := false


func _init() -> void:
	root.size = VIEW
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	graph["state"].set_deck(HERO_IDS.duplicate())
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                              # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = SEED
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	if String(m.phase_kind) != "build":
		_fail("mission setup did not land the build phase")
		return
	_m = m
	_bridge = graph["bridge"]
	print("Z1-PHASE kind=%s map=%s difficulty=%s seed=%d" % [
			String(m.phase_kind), String(m.mission_id),
			String(m.difficulty), SEED])
	process_frame.connect(_on_frame)


func _on_frame() -> void:
	if _failed:
		return
	_frames += 1
	if _frames == 2:
		root.size = VIEW                    # v4 pump: applied AT the pump
	if _frames < CAPTURE_FRAME:
		return
	if _shot:
		return
	_shot = true
	var rig: Node3D = _m.get_node("CameraRig") as Node3D
	var cam: Camera3D = _m.get_node("CameraRig/Camera3D") as Camera3D
	if cam == null or not cam.current:
		_fail("shipped Camera3D missing or not current at frame %d" % _frames)
		return
	var o: Vector3 = cam.get_global_position()
	var n: float = o.length()
	print("Z1-RIG origin=%s norm=%.3f rig_origin=%s fov=%.1f frame=%d" % [
			str(o), n, str(rig.get_transform().origin), cam.fov,
			_frames])
	if not (is_equal_approx(o.x, DEF_ORIGIN.x) \
			and is_equal_approx(o.y, DEF_ORIGIN.y) \
			and is_equal_approx(o.z, DEF_ORIGIN.z)):
		_fail("rig origin moved off the shipped default: %s != %s" % [
				str(o), str(DEF_ORIGIN)])
		return
	if absf(n - DEF_NORM) > 0.0005:
		_fail("rig distance off the D=64 shorthand: %.3f != %.3f" % [
				n, DEF_NORM])
		return
	if int(_bridge.presses.size()) != 0 or int(_bridge.held.size()) != 0:
		_fail("input reached the zero-input mission: presses=%d held=%d" % [
				int(_bridge.presses.size()), int(_bridge.held.size())])
		return
	print("Z1-INPUT dispatched_push_input=0 presses=0 held=0")
	var img := root.get_texture().get_image()
	if img == null or img.get_width() != VIEW.x or img.get_height() != VIEW.y:
		_fail("no 1280x720 frame to capture: %s" % [
				str(img.get_size()) if img != null else "null"])
		return
	if img.save_png(OUT) != OK:
		_fail("save_png failed: %s" % OUT)
		return
	print("Z1-SHOT-OK %s px=%dx%d frame=%d" % [OUT, VIEW.x, VIEW.y, _frames])
	print("Z1-OK")
	quit(0)


func _fail(why: String) -> void:
	if _failed:
		return
	_failed = true
	print("Z1-FAIL " + why)
	quit(1)
