# boot_probe — boot-flow probe (W5, MC 11274.1.12 / card 11304). Test
# asset in sim/ per the harness placement idiom (save_probe is the live
# precedent: harness files carry no sim_ prefix and the parse-probe scan
# skips them). Boots the REAL main flow headless: loads Main.tscn (so
# the root-scene wiring itself is in the verified path), instantiates,
# mounts it under root — _ready runs the boot: tables load + fail-fast,
# GWCompose.build_graph, from_save of the user:// save, ONE rng seed,
# hub route. Then pushes ONE C5 snapshot and reads __GW_LAST_SNAPSHOT
# back (the desktop readback of the pinned push mechanism; on web the
# same payload lands in window.__gwSnapshot).
# user:// isolation = the save_probe idiom VERIFIED there: the caller
# redirects XDG_DATA_HOME to a temp dir. tests/test_bridge_contract.py
# pre-seeds that dir with a save via save_probe write, so the boot leg
# exercises a REAL from_save, not only the empty-file fresh start.
# Machine rows (the pytest leg asserts):
#   BOOT-PROBE-SNAP <json>   the read-back C5 snapshot, one line
#   BOOT-PROBE-OK            last row on success, rc 0
#   BOOT-PROBE FAIL <why>    any failed check, rc 1
# E3: quit() under -s does NOT abort the running frame — every failure
# path early-returns and each process path calls quit() exactly once.
extends SceneTree

const MAIN_SCENE := "res://Main.tscn"
const MAIN_SCRIPT := preload("res://scripts/main.gd")


func _init() -> void:
	var packed = ResourceLoader.load(MAIN_SCENE)
	if packed == null:
		print("BOOT-PROBE FAIL Main.tscn not loadable")
		quit(1)
		return
	var main = packed.instantiate()
	if main == null or not (main is MAIN_SCRIPT):
		print("BOOT-PROBE FAIL Main.tscn root script is not main.gd")
		quit(1)
		return
	root.add_child(main)   # mount as child of root (the router's parent)
	# E3-adjacent engine fact (VERIFIED this gate): under `-s` the main
	# loop never processes frames, so add_child ALONE does not dispatch
	# _ready. The harness drives the real boot entry point directly —
	# the same _ready the shipped runtime runs on web/desktop.
	main._ready()
	if main.state == null or main.save == null or main.bridge == null:
		print("BOOT-PROBE FAIL graph not built (boot fail-fast fired)")
		quit(1)
		return
	main.push_snapshot()
	var snap: String = String(main.__GW_LAST_SNAPSHOT)
	if snap.is_empty():
		print("BOOT-PROBE FAIL __GW_LAST_SNAPSHOT empty after push")
		quit(1)
		return
	var parsed: Variant = JSON.parse_string(snap)
	if not (parsed is Dictionary):
		print("BOOT-PROBE FAIL snapshot is not a JSON object")
		quit(1)
		return
	var snap_dict: Dictionary = parsed
	if int(snap_dict.get("schema", 0)) != 1 \
			or String(snap_dict.get("phase", "")) != "hub":
		print("BOOT-PROBE FAIL hub snapshot wrong: %s" % snap)
		quit(1)
		return
	# C13 mirror rows: the pushed saved_ack equals the live write_seq,
	# and state.saved_ack (fed by the GWCompose listener) equals it too.
	var write_seq: int = int(main.save.write_seq)
	if int(snap_dict.get("saved_ack", -1)) != write_seq \
			or int(main.state.saved_ack) != write_seq:
		print("BOOT-PROBE FAIL saved_ack does not mirror write_seq=%d" \
				% write_seq)
		quit(1)
		return
	print("BOOT-PROBE-SNAP " + snap)
	print("BOOT-PROBE-OK")
	quit(0)
	return
