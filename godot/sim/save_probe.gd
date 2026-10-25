# save_probe — save round-trip probe (Modules row sim/save_probe.gd;
# MC 11274.1.11 / card 11302). BN4/I5: the reload check runs in a FRESH
# PROCESS, so this harness is invoked twice, never twice-in-one-run:
#   A: godot --headless --path godot/ -s res://sim/save_probe.gd -- write
#   B: godot --headless --path godot/ -s res://sim/save_probe.gd -- read
# (mode also reads the GW_SAVE_PROBE env when no user arg is given —
# the brief's "--` args or env"; both processes share ONE save file via
# the XDG_DATA_HOME redirection this row names for the desktop leg:
# user:// resolves under $XDG_DATA_HOME/godot/app_userdata/<project>, so
# a temp dir isolates the probe from the developer's real save.)
# Machine rows (tests/test_persistence.py drives + asserts):
#   SAVE-PROBE-A ack=<n>        one per C13 mutator fired, strictly grows
#   SAVE-PROBE-A negative=OK    short spend/consume: false + no mutation
#   SAVE-PROBE-A saved_ack=<n>  final C13 ack
#   SAVE-PROBE-B roundtrip=OK   fresh-process byte-equal meta (incl. mats)
#   SAVE-PROBE-B detail=<json>  the arch row's {ok,diff,ack} JSONL shape
#   SAVE-PROBE-X FAIL <reason>  any failed assertion, quit(1)
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

# The scripted meta mutations: A performs them, B expects their result.
const ADD_GOLD := 50
const SPEND_GOLD := 20
const HERO_XP := 250
const DECK := ["deadeye", "warden", "embercaller"]
const BANK_ITEM := {
	"uid": 0, "base_id": "oaken_cleaver", "slot": "weapon",
	"rarity": "sturdy", "ilvl": 3,
	"primary": {"stat": "damage", "value": 10.0}, "secondary": null,
	"atk_speed": 1.0, "shot_type": null, "proj_count": 1,
	"mods": [], "upgraded": 0,
}


func _init() -> void:
	var args := OS.get_cmdline_user_args()
	var mode := String(args[0]) if args.size() > 0 \
			else OS.get_environment("GW_SAVE_PROBE")
	var tables := GW_TABLES.new()
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	if mode == "write":
		_leg_a(graph["state"], graph["save"], graph["bridge"], tables)
	elif mode == "read":
		_leg_b(graph["state"], graph["save"])
	else:
		print("SAVE-PROBE-A FAIL bad_mode=%s" % mode)
		quit(1)


func _leg_a(state, save, bridge, tables) -> void:
	if bridge == null:
		print("SAVE-PROBE-A FAIL bridge missing from build_graph")
		quit(1)
		return
	# NOTE: quit() under `-s` does NOT abort the running function (VERIFIED
	# this gate) — every failure path below returns immediately and each
	# process path calls quit() exactly once.
	var prev := 0
	state.add_gold(ADD_GOLD)
	prev = _step(state, save, "add_gold", prev)
	if prev < 0:
		return
	state.add_hero_xp("warden", HERO_XP)
	prev = _step(state, save, "add_hero_xp", prev)
	if prev < 0:
		return
	state.spend_asc(tables.table("ascension").get("tree", {}),
		"power_strike", 1)
	prev = _step(state, save, "spend_asc", prev)
	if prev < 0:
		return
	state.add_material("iron_bar", 3)
	prev = _step(state, save, "add_material", prev)
	if prev < 0:
		return
	state.add_material("aether_crystal", 1)
	prev = _step(state, save, "add_material_2", prev)
	if prev < 0:
		return
	state.consume_material("iron_bar", 1)
	prev = _step(state, save, "consume_material", prev)
	if prev < 0:
		return
	state.bank_add(BANK_ITEM)
	prev = _step(state, save, "bank_add", prev)
	if prev < 0:
		return
	state.set_deck(DECK)
	prev = _step(state, save, "set_deck", prev)
	if prev < 0:
		return
	state.complete_mission("gatefall_normal")
	prev = _step(state, save, "complete_mission", prev)
	if prev < 0:
		return
	if not state.spend_gold(SPEND_GOLD):
		print("SAVE-PROBE-A FAIL spend_gold refused on funded gold")
		quit(1)
		return
	prev = _step(state, save, "spend_gold", prev)
	if prev < 0:
		return
	# Negative leg (BN-style): refused ops change NOTHING (the unconditional
	# C13 emit may rewrite identical bytes — that is the pinned contract).
	if state.spend_gold(ADD_GOLD * 100) or state.gold != ADD_GOLD - SPEND_GOLD:
		print("SAVE-PROBE-A FAIL overspend mutated gold")
		quit(1)
		return
	if state.consume_material("iron_bar", 99) \
			or int(state.materials.get("iron_bar", 0)) != 2:
		print("SAVE-PROBE-A FAIL overconsume mutated materials")
		quit(1)
		return
	print("SAVE-PROBE-A negative=OK")
	print("SAVE-PROBE-A saved_ack=%d" % save.write_seq)
	print("SAVE-PROBE-A detail=" + JSON.stringify(
		{"ok": true, "diff": {}, "ack": save.write_seq}))
	quit(0)


func _step(state, save, label: String, prev: int) -> int:
	var ack: int = int(save.write_seq)
	if ack <= prev:
		print("SAVE-PROBE-A FAIL %s did not bump write_seq (%d<=%d)" \
				% [label, ack, prev])
		quit(1)
		return -1
	if int(state.saved_ack) != ack:
		print("SAVE-PROBE-A FAIL saved_ack=%d != write_seq=%d after %s" \
				% [int(state.saved_ack), ack, label])
		quit(1)
		return -1
	print("SAVE-PROBE-A ack=%d" % ack)
	return ack


func _leg_b(state, save) -> void:
	var d: Dictionary = save.load_save()
	if d.is_empty():
		print("SAVE-PROBE-B roundtrip=FAIL")
		print("SAVE-PROBE-B FAIL no_save (missing/corrupt/foreign schema)")
		quit(1)
		return
	state.from_save(d)
	var expected := expected_meta()
	var got: Dictionary = state.to_save()
	var diff: Array = []
	for key: String in expected:
		# I5 leg 1 (file): load_save -> dict is BYTE-equal to the expected
		# meta — ConfigFile keeps the JSON blobs and typed ints verbatim.
		if JSON.stringify(expected[key]) != JSON.stringify(d.get(key)):
			diff.append("file." + key)
			continue
		# Leg 2 (state): from_save -> to_save compares the *_json blobs
		# SEMANTICALLY — Godot JSON.parse returns every number as float,
		# so a re-stringified blob prints int 3 as 3.0 (named limitation,
		# recorded on the card trail; the file leg above is the byte gate).
		if key.ends_with("_json"):
			if JSON.parse_string(String(expected[key])) \
					!= JSON.parse_string(String(got.get(key))):
				diff.append("state." + key)
		elif JSON.stringify(expected[key]) != JSON.stringify(got.get(key)):
			diff.append("state." + key)
	var ok := diff.is_empty()
	print("SAVE-PROBE-B detail=" + JSON.stringify(
		{"ok": ok, "diff": diff, "ack": save.write_seq}))
	if not ok:
		print("SAVE-PROBE-B roundtrip=FAIL")
		quit(1)
		return
	print("SAVE-PROBE-B roundtrip=OK")
	quit(0)


# The meta the write leg must produce through file -> load -> from_save
# (C6 key set; I5 byte-equal incl. materials_json; insertion order is the
# to_save()/load_save() order, so the byte compare is meaningful).
func expected_meta() -> Dictionary:
	var worn := BANK_ITEM.duplicate(true)
	worn["uid"] = 1
	return {
		"schema_version": 1,
		"asc_earned": 2,
		"asc_spent_json": JSON.stringify({"power_strike": 1}),
		"heroes": {"warden": {"level": 3, "xp": HERO_XP}},
		"items_json": JSON.stringify([worn]),
		"gold": ADD_GOLD - SPEND_GOLD,
		"deck_json": JSON.stringify(DECK),
		"completed_json": JSON.stringify({"gatefall_normal": true}),
		"materials_json": JSON.stringify(
			{"iron_bar": 2, "aether_crystal": 1}),
	}
