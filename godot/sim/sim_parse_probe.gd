# Sim parse probe harness (W3a, MC 11274.1.9 / card 11299). Lives in sim/
# per the architecture's harness placement (sim_headless/save_probe/
# validate_probe — hollow_dawn's sim_headless precedent); a res:// load
# cannot reach tests/, so the parse harness is a sim/ asset and the pytest
# -s leg references THIS path (reading recorded on the card trail).
# Loads every sim_*.gd module in this directory for real (the harness file
# itself is not a module and is skipped) and prints machine-readable rows:
#   SIMPARSE-OK <name>     once per module that parses + loads cleanly
#   SIMPARSE-FAIL <name>   on the first compile/load error, then rc 1
#   SIMPARSE-DONE <count>  last row on full success, rc 0
# Runner: godot --headless --path godot/ -s res://sim/sim_parse_probe.gd
# after the F14 class-cache import (tests/test_purity.py drives it).
# W4 ruling on the W3b finding: a NON-NULL Resource is not proof of a
# clean parse (a broken resource can load non-null) — the true parse
# signal is the run's EMPTY stderr, asserted by the pytest leg; the
# OK/DONE rows below stay exactly as they are.
extends SceneTree

const HARNESS := "sim_parse_probe.gd"


func _init() -> void:
	var module_names: Array[String] = []
	var dir := DirAccess.open("res://sim")
	if dir != null:
		dir.list_dir_begin()
		var fname := dir.get_next()
		while fname != "":
			if fname != HARNESS and fname.begins_with("sim_") \
					and fname.ends_with(".gd"):
				module_names.append(fname.get_basename())
			fname = dir.get_next()
		dir.list_dir_end()
	module_names.sort()
	var count := 0
	for module_name: String in module_names:
		var script: Resource = ResourceLoader.load(
			"res://sim/%s.gd" % module_name)
		if script == null:
			print("SIMPARSE-FAIL " + module_name)
			quit(1)
			return
		print("SIMPARSE-OK " + module_name)
		count += 1
	print("SIMPARSE-DONE %d" % count)
	quit(0)
