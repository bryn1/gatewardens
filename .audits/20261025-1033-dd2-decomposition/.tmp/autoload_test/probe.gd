extends SceneTree
func _init() -> void:
	print("INIT: has_autoload_singleton=", Engine.has_singleton("Data"))
	var s = load("res://scene.tscn").instantiate()
	root.add_child(s)
	print("AFTER_ADD_CHILD (same tick) done")
	quit()
