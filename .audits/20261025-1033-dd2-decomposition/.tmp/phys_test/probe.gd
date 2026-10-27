extends SceneTree
func _init() -> void:
	var b: RigidBody3D = load("res://fall.tscn").instantiate()
	root.add_child(b)
	var t := 0.0
	for i in 60:
		iterate(1.0 / 60.0)
		t += 1.0 / 60.0
	print("POS_AFTER_60_ITERATES y=", b.global_position.y, " expected_free_fall=", 10.0 - 0.5 * 9.8 * t * t)
	print("SLEEPING=", b.is_sleeping(), " LINEAR_VEL=", b.linear_velocity)
	quit()
