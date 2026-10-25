class_name GWCompose
extends RefCounted

# The ONE wiring site (F2-5, MC 11274.1.11): the core trio is constructed
# ONLY here and returned for constructor injection (C1/R3 — no autoloads,
# `-s` runs work by construction). main.gd `_ready` AND every `-s` probe
# call build_graph; nothing else constructs or wires the trio.
#
# Cross-file references bind via preload(), never class_name refs: the
# global class cache is an editor-scan artifact that a clean-checkout
# `--headless --import` does not guarantee for new files (W3b finding,
# W4 ruling — the same mechanism sim_inventory.gd already proved).

const GW_GAME_STATE := preload("res://scripts/game_state.gd")
const GW_SAVE_STORE := preload("res://scripts/save_store.gd")
const GW_BRIDGE := preload("res://scripts/bridge.gd")


# C13 trigger listener: every `mutated` emit writes the save; on success
# write_seq mirrors into state.saved_ack (C5 saved_ack == write_seq). The
# state is held as a WeakRef so signal -> listener -> state never forms a
# RefCounted leak cycle (the round-3 compose_test lambda form VERIFIED to
# leak: stderr "ObjectDB instances were leaked" at exit, checked this
# gate). Wiring stays signal-to-callable — a connected method, nothing
# else. The bridge is NOT wired (C13: input is no save trigger).
class StateCommit:
	extends RefCounted

	var _state_ref: WeakRef
	var _save

	func _init(state, save) -> void:
		_state_ref = weakref(state)
		_save = save

	func commit() -> void:
		var state = _state_ref.get_ref()
		if state == null:
			return
		if _save.write(state.to_save()):
			state.saved_ack = _save.write_seq


static func build_graph(tables) -> Dictionary:
	var state: GW_GAME_STATE = GW_GAME_STATE.new(tables)
	var save: GW_SAVE_STORE = GW_SAVE_STORE.new()
	var bridge: GW_BRIDGE = GW_BRIDGE.new()
	var listener := StateCommit.new(state, save)
	state.commit_listener = listener
	state.mutated.connect(listener.commit)
	return {"state": state, "save": save, "bridge": bridge}
