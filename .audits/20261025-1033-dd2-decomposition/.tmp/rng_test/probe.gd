extends SceneTree
func _init():
	var rng := RandomNumberGenerator.new()
	rng.seed = 12345
	print("METHOD_NAMES_OK: ", rng.randf(), " ", rng.randi(), " ", rng.randf_range(0.0, 1.0))
	quit()
