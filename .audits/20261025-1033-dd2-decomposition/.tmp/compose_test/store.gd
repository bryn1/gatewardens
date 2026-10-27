class_name GWStore extends RefCounted
var write_seq: int = 0
var last: Dictionary = {}
func write(d: Dictionary) -> bool:
	last = d
	write_seq += 1
	return true
