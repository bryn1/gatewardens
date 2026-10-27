class_name GWState extends RefCounted
signal mutated
var gold: int = 0
var materials: Dictionary = {}
func add_gold(n: int) -> void:
	gold += n
	mutated.emit()
func to_save() -> Dictionary:
	return {"gold": gold, "materials": materials}
