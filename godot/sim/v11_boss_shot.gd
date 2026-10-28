# v11_boss_shot — boss BILLBOARD pixel proof (MC 11462 DA fix loop):
# the v1_world_shot capture path UNCHANGED in mechanics (real Main.tscn
# boot, real InputEventMouseButton on "Start gatefall — normal", the
# shipped router swaps scenes, the declared core-hold license) with ONE
# warden_breaker spawn on lane_g1 in place of the enemy feed — no
# towers, no fx gating. Captures ONE full 1280x720 frame
# (gen/v112-boss-shot.png) plus a 512px crop centred on the boss's
# on-screen position read through the shipped static CameraRig (F8) —
# the crop is where the boss billboard reads at pixel scale. At the
# default rig (F8, 71u out) a 2u billboard is a ~13px speck, so the kit
# ALSO nudges the Camera3D (kit-local only, the .tscn is untouched) on
# the frame AFTER the default captures and takes a close third frame
# (gen/v112-boss-near.png) where the art itself is readable — declared
# here because it is the one number the kit changes (camera transform).
# The kit asserts the spawned node IS a Sprite3D and prints its texture
# resource_path beside the crop: a greybox frame cannot pass quietly.
#   xvfb-run Godot --rendering-driver opengl3 --path godot \
#       -s res://sim/v11_boss_shot.gd
extends SceneTree

const OUT_DIR := "/home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/"
const CROP := 512

var _frames := 0
var _placed := false
var _mission
var _boss_node
var _shots := 0


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
		_mission.green = 100000               # license (header)
		_mission.core_main.hp_max *= 5.0
		_mission.core_main.hp = _mission.core_main.hp_max
		var runner = _mission.get_node("EnemyRunner")
		runner.spawn({"enemy_id": "warden_breaker", "count": 1},
				_mission.lanes["lane_g1"], _mission.enemy_defs, _mission.rng)
		_boss_node = (runner.entities[-1] as Dictionary)["node"]
		print("SPAWNED warden_breaker class=%s" % _boss_node.get_class())
	if _placed:
		_mission.core_main.hp = _mission.core_main.hp_max   # license
		if _shots == 0 and _frames >= 120:
			if not (_boss_node is Sprite3D):
				print("SHOT-FAIL boss node is not a Sprite3D (greybox)")
				quit(1)
				return
			var img := root.get_texture().get_image()
			if img != null:
				var p := OUT_DIR + "v112-boss-shot.png"
				img.save_png(p)
				var cam: Camera3D = _mission.get_node("CameraRig/Camera3D")
				var c := cam.unproject_position(_boss_node.global_position)
				var half := CROP / 2
				var x := int(clampf(c.x - half, 0.0,
						float(img.get_width() - CROP)))
				var y := int(clampf(c.y - half, 0.0,
						float(img.get_height() - CROP)))
				var zp := OUT_DIR + "v112-boss-zoom.png"
				img.get_region(Rect2i(x, y, CROP, CROP)).save_png(zp)
				print("SHOT-OK %s crop=%s boss@%s x=%d y=%d tex=%s" % [
						p, zp, str(c), x, y,
						String((_boss_node as Sprite3D).texture.resource_path)])
				_shots = 1
		elif _shots == 1 and _frames >= 122:
			# Nudge (kit-local, header): one close frame where the art
			# itself is readable; the rendered frame now in hand was
			# still the default view, the nudge paints NEXT frame.
			var cam2: Camera3D = _mission.get_node("CameraRig/Camera3D")
			cam2.look_at_from_position(_boss_node.global_position
					+ Vector3(3.0, 2.2, 3.0),
					_boss_node.global_position + Vector3(0.0, 1.0, 0.0),
					Vector3.UP)
			_shots = 2
		elif _shots == 2 and _frames >= 124:
			var img2 := root.get_texture().get_image()
			if img2 != null:
				var np := OUT_DIR + "v112-boss-near.png"
				img2.save_png(np)
				print("SHOT-OK-NEAR %s" % np)
				_shots = 3
	if _frames >= 400:
		if _shots < 3:
			print("SHOT-FAIL captured %d/3" % _shots)
			quit(1)
		else:
			print("SHOT-DONE")
			quit(0)
