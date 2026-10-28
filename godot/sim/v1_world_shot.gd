# v1_world_shot — V1 PIXEL proof (MC card 11559 / milestone 11462): the
# v5_fx_shot capture path UNCHANGED in mechanics (real Main.tscn boot,
# real InputEventMouseButton on "Start gatefall — normal", shipped router,
# 6 shooters at the lane_g1 run-in, enemies fed, core held — the declared
# v5_fx_probe license) so towers, enemies AND the mounted FxDirector are
# live in the frame. Captures ONE full 1280x720 frame (gen/v1world_shot
# .png) plus a 512x512 ZOOM CROP centred on the main core's on-screen
# position read through the shipped Camera3D (gen/v1world_zoom.png) —
# the crop is where the emblem + arena board read at pixel scale.
#   xvfb-run Godot --rendering-driver opengl3 --path godot \
#       -s res://sim/v1_world_shot.gd
extends SceneTree

const OUT_DIR := "/home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/"
const OFFS := [Vector3(-20, 0.0, 2.0), Vector3(-24, 0.0, 3.0),
		Vector3(-28, 0.0, 5.0), Vector3(-32, 0.0, 1.0),
		Vector3(-14, 0.0, 3.0), Vector3(-17, 0.0, 7.0)]
const TOWER_IDS := ["ballista", "bombard", "hailspire_tower"]
const FEED_IDS := ["skitterling", "husk_brute", "ash_bandit"]
const CROP := 512

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
		if _frames > 60 and _frames % 30 == 0 and _shots < 1:
			runner.spawn({"enemy_id": FEED_IDS[_feed_k % FEED_IDS.size()],
					"count": 1}, lane, _mission.enemy_defs, _mission.rng)
			_feed_k += 1
		if _shots < 1 and _frames >= 120 \
				and int(_fx.get_child_count()) > 0:
			var img := root.get_texture().get_image()
			if img != null:
				var p := OUT_DIR + "v1world_shot.png"
				img.save_png(p)
				var cam: Camera3D = _mission.get_node("CameraRig/Camera3D")
				var c := cam.unproject_position(_mission.core_main.pos)
				var half := CROP / 2
				var x := int(clampf(c.x - half, 0.0,
						float(img.get_width() - CROP)))
				var y := int(clampf(c.y - half, 0.0,
						float(img.get_height() - CROP)))
				var zp := OUT_DIR + "v1world_zoom.png"
				img.get_region(Rect2i(x, y, CROP, CROP)).save_png(zp)
				print("SHOT-OK %s crop=%s core@%s x=%d y=%d live=%d tracers=%d sparks=%d poofs=%d" \
						% [p, zp, str(c), x, y, int(_fx.get_child_count()),
						int(_fx.spawned_tracers), int(_fx.spawned_sparks),
						int(_fx.spawned_poofs)])
				_shots += 1
	if _frames >= 400:
		if _shots < 1:
			print("SHOT-FAIL captured %d/1 (never caught live fx)" % _shots)
			quit(1)
		else:
			print("SHOT-DONE")
			quit(0)
