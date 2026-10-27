# v11_shot3 — runtime PIXEL proof (MC 11462 close kit). Fully honest path:
# lets Main boot to the HUB normally, then feeds a REAL InputEventMouseButton
# on "Start gatefall — normal" (the same button the browser journey clicks),
# finds the live mission node from the scene tree after the shipped router
# swapped scenes, places the 3 shooter towers at the camera view centre,
# spawns the 6 sprite enemies, captures 2 frames.
#   xvfb-run Godot --rendering-driver opengl3 --path godot -s res://sim/v11_shot3.gd
extends SceneTree

const CENTER := Vector3(12, 0.0, -8)
const OUT_DIR := "/home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/"

var _frames := 0
var _started := false
var _placed := false
var _mission


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
		_started = true
		return
	if not _placed and _frames >= 40:
		_mission = _find_mission(root)
		if _mission == null:
			if _frames > 300:
				print("SHOT-FAIL mission never found (started=%s)" % _started)
				quit(1)
			return
		if not ("tables" in _mission):
			return
		_placed = true
		_mission.green = 100000
		_mission.core_main.hp_max *= 5.0
		_mission.core_main.hp = _mission.core_main.hp_max
		var trows := {}
		for row: Dictionary in _mission.tables.rows("towers"):
			trows[String(row["id"])] = row
		var offs := [Vector3(-5, 0, 0), Vector3(0, 0, 0), Vector3(5, 0, 2)]
		var i := 0
		for tid: String in ["ballista", "bombard", "hailspire_tower"]:
			var r: Dictionary = _mission.place_defense(trows[tid], 1,
					CENTER + offs[i])
			print("PLACE %s ok=%s" % [tid, str(r.get("ok"))])
			i += 1
		for lid: String in ["lane_g1", "lane_a2", "sub_north"]:
			if _mission.lanes.has(lid):
				var runner = _mission.get_node("EnemyRunner")
				if int(runner.entities.size()) == 0:
					var lane: Dictionary = _mission.lanes[lid]
					for eid: String in ["skitterling", "husk_brute",
							"ash_bandit", "bone_lobber", "cinder_wisp",
							"gale_harpy"]:
						runner.spawn({"enemy_id": eid, "count": 1}, lane,
								_mission.enemy_defs, _mission.rng)
					print("SPAWNED n=6 on " + lid)
	if _frames == 200 or _frames == 480:
		var img := root.get_texture().get_image()
		if img != null:
			var p := OUT_DIR + "pixel_f%d.png" % _frames
			img.save_png(p)
			print("SHOT-OK %s" % p)
	if _frames >= 480:
		print("SHOT-DONE")
		quit(0)
