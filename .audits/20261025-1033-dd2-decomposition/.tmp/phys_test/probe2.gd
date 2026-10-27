extends SceneTree
func _init() -> void:
	var h: CharacterBody3D = load("res://move.tscn").instantiate()
	root.add_child(h)
	for i in 60:
		h.velocity = Vector3(2, 0, 0)
		h.move_and_slide()
		iterate(1.0 / 60.0)
	print("HERO_X_AFTER_60 move_and_slide+iterate=", h.global_position.x, " (engine physics would give ~2.0 if stepped)")
	quit()
