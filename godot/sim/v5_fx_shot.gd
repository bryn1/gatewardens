# v5_fx_shot — V5 PIXEL proof (MC card 11552 / milestone 11462): the
# v11_shot3 capture path with the FxDirector MOUNTED (it rides
# mission.tscn, so the shipped router mounts it — this script adds no
# fx code path) and MANY towers firing. Real Main.tscn boot, real
# InputEventMouseButton on "Start gatefall — normal", the live mission
# found from the tree; 6 shooters (2 per family) at the lane_g1 run-in,
# enemies fed onto the lane every 30 frames, the main core held (the
# v5_fx_probe license, declared there: breach cost scales with hp_max
# so a boost alone is 4-breaches-deep), then 3 frames saved WHILE fx
# nodes are live (the live count + counters printed with the path —
# the honest caught/missed record).
#   xvfb-run Godot --rendering-driver opengl3 --path godot \
#       -s res://sim/v5_fx_shot.gd
extends SceneTree

const OUT_DIR := "/home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/"
const OFFS := [Vector3(-20, 0.0, 2.0), Vector3(-24, 0.0, 3.0),
		Vector3(-28, 0.0, 5.0), Vector3(-32, 0.0, 1.0),
		Vector3(-14, 0.0, 3.0), Vector3(-17, 0.0, 7.0)]
const TOWER_IDS := ["ballista", "bombard", "hailspire_tower"]
const FEED_IDS := ["skitterling", "husk_brute", "ash_bandit"]

var _frames := 0
var _placed := false
var _mission
var _fx
var _shots := 0
var _feed_k := 0


func _init() -> void:
	root.size = Vector2i(1280, 720)
	var packed = ResourceLoader.load("res://Main.tscn")
	root.add_child(packed.instantiate())
	process_frame.connect(_on_frame)


func _click(x: int, y: int) -> void:
	var d := InputEventMouseButton.new()
	d.position = Vector2i(x, y); d.global_position = d.position
	d.button_index = MOUSE_BUTTON_LEFT
	var p := d.duplicate() as InputEventMouseButton
	d.pressed = true
	p.pressed = false
	root.push_input(d)
	root.push_input(p)


func _find_mission(n: Node) -> Node:
	if n.has_signal("phase_ended") or ("phase_kind" in n):
		return n
	for k in n.get_children():
		var r := _find_mission(k)
		if r != null:
			return r
	return null


func _on_frame() -> void:
	_frames += 1
	if _frames == 10:
		_click(80, 132)                       # "Start gatefall — normal"
		return
	if not _placed and _frames >= 40:
		_mission = _find_mission(root)
		if _mission == null:
			if _frames > 300:
				print("SHOT-FAIL mission never found")
				quit(1)
			return
		if not ("tables" in _mission):
			return
		_placed = true
		_fx = _mission.get_node_or_null("FxDirector")
		if _fx == null:
			print("SHOT-FAIL FxDirector not mounted by mission.tscn")
			quit(1)
			return
		_mission.green = 100000               # license (header)
		_mission.core_main.hp_max *= 5.0
		_mission.core_main.hp = _mission.core_main.hp_max
		var trows := {}
		for row: Dictionary in _mission.tables.rows("towers"):
			trows[String(row["id"])] = row
		var ti := 0
		for tid: String in TOWER_IDS:
			for k: int in 2:
				var r: Dictionary = _mission.place_defense(trows[tid], 1,
						OFFS[ti])
				print("PLACE %s ok=%s" % [tid, str(r.get("ok"))])
				ti += 1
	if _placed:
		_mission.core_main.hp = _mission.core_main.hp_max   # license
		var runner = _mission.get_node("EnemyRunner")
		var lane: Dictionary = _mission.lanes["lane_g1"]
		if _frames > 60 and _frames % 30 == 0 and _shots < 3:
			runner.spawn({"enemy_id": FEED_IDS[_feed_k % FEED_IDS.size()],
					"count": 1}, lane, _mission.enemy_defs, _mission.rng)
			_feed_k += 1
		# three captures on THREE DIFFERENT frames with live fx — the
		# first such frame after 90, then +90, +180 (never two shots on
		# one frame: one fx lifetime is 12-18 frames, a per-capture
		# fresh spawn keeps sparks AND tracers in the paint)
		if _shots < 3 and _frames >= 90 + _shots * 90 \
				and int(_fx.get_child_count()) > 0:
			var img := root.get_texture().get_image()
			if img != null:
				var p := OUT_DIR + "v5fx_f%d.png" % _frames
				img.save_png(p)
				print("SHOT-OK %s live=%d tracers=%d sparks=%d poofs=%d" \
						% [p, int(_fx.get_child_count()),
						int(_fx.spawned_tracers), int(_fx.spawned_sparks),
						int(_fx.spawned_poofs)])
				_shots += 1
	if _frames >= 400 and _shots < 3:
		print("SHOT-FAIL captured %d/3 (never caught live fx)" % _shots)
		quit(1)
	if _frames >= 400:
		print("SHOT-DONE")
		quit(0)
