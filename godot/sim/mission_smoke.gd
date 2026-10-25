# mission_smoke — headless mission-flow smoke (W6, MC 11274.1.13 /
# card 11308). Test asset in sim/ (harness idiom: no sim_ prefix, the
# parse-probe scan skips it; boot_probe/save_probe are the precedent).
# Boots the REAL mission scene under -s: load mission.tscn, instantiate,
# mount under root, then drive _ready() + setup(...) DIRECTLY (E5: the
# main loop never runs under -s, add_child does not dispatch _ready) and
# drive mission.step(1.0/60.0) frames — the exact call _process makes
# in the shipped game (C12: _process = step, nothing else).
# user:// isolation = the save_probe idiom (caller redirects
# XDG_DATA_HOME to a temp dir). The 3-hero deck is seeded through the
# REAL C13 wiring (GWCompose trio; the set_deck mutator writes the file),
# so the save path is exercised before the mission reads the deck.
# Hero down-states are driven DIRECTLY by the harness: no damage source
# to heroes ships before W7 (the pinned runner row is lane-walk only),
# exactly the boot_probe precedent of driving real entry points.
# Machine rows (the pytest leg asserts, EMPTY stderr per the W4 ruling):
#   MISSION-SMOKE-SEED deck=<json>
#   MISSION-SMOKE-SPAWN t=<tick> wave=<i> alive=<n> (wave-0 delay-0 group
#                          spawns at combat-local t = 0)
#   MISSION-SMOKE-ADVANCE d0=<x> d1=<y>   (ground-lane walk closes on core)
#   MISSION-SMOKE-CORE hp=<x> max=<y>     (reaching the gate cut core HP)
#   MISSION-SMOKE-WAVE green=<x> xp=<y>   (wave awards + build alternation)
#   MISSION-SMOKE-REFILL blue=<x> max=<y> (full refill at combat start)
#   MISSION-SMOKE-SWAP hero=<id>          (F3 manual + down-swap F2-10)
#   MISSION-SMOKE-LOSE outcome=<o> ack=<a> seq=<s> (F2-9 same-tick LOSE
#                          wins + the single C13 mission-end commit)
#   MISSION-SMOKE-OK
# E3: quit() under -s does NOT abort the running frame — every failure
# path early-returns; each quit() fires exactly once.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const SAVE_PATH := "user://gatewardens.cfg"
const DECK := ["warden", "deadeye", "embercaller"]


func _init() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)  # F2-5 wiring site
	var state = graph["state"]
	var save = graph["save"]
	var start_green := int(tables.map("gatefall").get("start_green", -1))
	var main_hp := int(tables.map("gatefall").get("cores", {})
			.get("main", {}).get("hp", {}).get("normal", -1))
	var per_wave := int(tables.table("economy").get("green", {}).get("per_wave", 0))
	var wave_xp := int(tables.table("xp").get("wave_xp", 0))
	state.set_deck(DECK.duplicate())     # the seed lands via the C13 write
	if not FileAccess.file_exists(SAVE_PATH):
		_fail("no user:// save after set_deck")
		return
	var saved: Dictionary = save.load_save()
	if not String(saved.get("deck_json", "")).contains("deadeye"):
		_fail("deck missing from the save file: %s" % str(saved.get("deck_json", "")))
		return
	print("MISSION-SMOKE-SEED deck=" + String(saved.get("deck_json", "")))
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                           # E5: drive _ready directly (no-op)
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274                     # pinned seed: the smoke is deterministic
	m.setup(tables, state, save, graph["bridge"], "gatefall", "normal", rng)
	if String(m.phase_kind) != "build" or int(m.green) != start_green \
			or int(m.wave) != 0 or int(m.cores["main"]["hp"]) != main_hp:
		_fail("setup: phase=%s green=%d wave=%d core=%s" % [
				m.phase_kind, m.green, m.wave, str(m.cores["main"]["hp"])])
		return
	# Harness-driven state (same license as driving _ready/setup): the
	# main core is made 5x sturdier so the W6 run with NO damage source
	# cannot end the mission on a core breach during the checks below.
	# Breach damage scales WITH core max (reading: ratio x max), so the
	# buff also scales leak damage — wave 0 is cleared by harness KILLS
	# (check 4), the licensed stand-in for W7/W8 damage sources.
	m.core_main.hp_max *= 5.0
	m.core_main.hp = m.core_main.hp_max
	# --- 1) build phase lasts build_seconds(waves[0]) = 25.0s, and the
	#        wave-0 delay-0 group spawns at combat-local t = 0 (tick 1)
	var guard := 0
	while guard < 1700 and String(m.phase_kind) == "build":
		m.step(1.0 / 60.0)
		guard += 1
	if guard >= 1700:
		_fail("first combat never started (build alternation broken)")
		return
	if guard < 1490 or guard > 1510:
		_fail("first combat tick %d outside 25.0s +/-1s" % guard)
		return
	if int(m.alive) != 1 or int(m.wave) != 0:
		_fail("wave-0 spawn at combat start: alive=%d wave=%d" % [m.alive, m.wave])
		return
	print("MISSION-SMOKE-SPAWN t=%d wave=%d alive=%d" % [guard, m.wave, m.alive])
	# --- 2) positions ADVANCE along the ground lane (lane_g1 -> main core)
	var runner = m.get_node("EnemyRunner")
	var ents: Array = runner.entities
	var d0: float = (ents[0]["pos"] as Vector3).distance_to(Vector3.ZERO)
	for _f: int in 60:
		m.step(1.0 / 60.0)
	ents = runner.entities
	var d1: float = (ents[0]["pos"] as Vector3).distance_to(Vector3.ZERO)
	if d1 >= d0 - 1.0:
		_fail("no lane advance d0=%.2f d1=%.2f" % [d0, d1])
		return
	print("MISSION-SMOKE-ADVANCE d0=%.2f d1=%.2f" % [d0, d1])
	# --- 3) reaching the gate reduces core HP
	guard = 0
	while guard < 1700 \
			and float(m.cores["main"]["hp"]) >= float(m.cores["main"]["max"]):
		m.step(1.0 / 60.0)
		guard += 1
	if guard >= 1700:
		_fail("main core never took breach damage")
		return
	print("MISSION-SMOKE-CORE hp=%s max=%s" % [
			str(m.cores["main"]["hp"]), str(m.cores["main"]["max"])])
	# --- 4) wave 0 clears -> awards + build alternation. No hero/defense
	#        damage source ships before W7/W8, so the harness supplies the
	#        kill leg: every entity left on the lanes (spawned after the
	#        first breach, which check 3 needed) is killed via runner.damage
	#        and the mission's own death-awards + clear logic run unchanged.
	var skit: Dictionary = {}
	for e: Dictionary in m.enemy_defs:
		if String(e.get("id", "")) == "skitterling":
			skit = e
	if skit.is_empty():
		_fail("skitterling def missing from enemies data")
		return
	var kills := 0
	guard = 0
	while guard < 1700 and String(m.phase_kind) == "combat":
		for ent: Dictionary in runner.entities:
			kills += 1
			runner.damage(ent, 1.0e9)
		m.step(1.0 / 60.0)
		guard += 1
	if guard >= 1700:
		_fail("wave 0 never completed")
		return
	if kills < 1 or int(m.wave) != 1 \
			or int(m.green) != start_green + kills * int(skit["green"]) + per_wave \
			or int(m.xp_earned) != wave_xp + kills * int(skit["xp"]) \
			or int(m.loot_pending) != kills:
		_fail("wave awards wrong: kills=%d wave=%d green=%d xp=%d loot=%d" % [
				kills, m.wave, m.green, m.xp_earned, m.loot_pending])
		return
	print("MISSION-SMOKE-WAVE kills=%d green=%d xp=%d loot=%d" % [
			kills, m.green, m.xp_earned, m.loot_pending])
	# --- 5) the blue pool refills FULL at every combat start (C4/I4)
	m.blue = 0.0
	guard = 0
	while guard < 1700 and String(m.phase_kind) == "build":
		m.step(1.0 / 60.0)
		guard += 1
	if guard >= 1700:
		_fail("second combat never started")
		return
	if float(m.blue) != float(m.blue_max) or float(m.blue_max) \
			!= float(m.hero_defs[m.hero_id]["base"]["blue_max"]):
		_fail("no full blue refill at combat start: %s/%s" % [m.blue, m.blue_max])
		return
	print("MISSION-SMOKE-REFILL blue=%s max=%s" % [m.blue, m.blue_max])
	# --- 6) hot-swap F3 (manual) + down-swap to next healthy (F2-10)
	m.bridge.on_key("F3", true)
	m.step(1.0 / 60.0)
	if String(m.hero_id) != "embercaller":
		_fail("F3 manual swap: hero_id=%s" % m.hero_id)
		return
	m.hero_state["embercaller"]["hp"] = 0.0
	m.step(1.0 / 60.0)
	if String(m.hero_id) != "warden" or not bool(m.hero_state["embercaller"]["downed"]):
		_fail("F2-10 down-swap: hero_id=%s" % m.hero_id)
		return
	print("MISSION-SMOKE-SWAP hero=%s" % m.hero_id)
	# --- 7) F2-9: all-down SAME TICK as a recorded win -> LOSE wins; the
	#        mission-end commit fired once through the C13 wiring.
	m.win_pending = true
	for hid: String in DECK:
		m.hero_state[hid]["hp"] = 0.0
	m.step(1.0 / 60.0)
	if String(m.outcome) != "lose":
		_fail("F2-9 same-tick: outcome=%s (lose must overwrite win)" % m.outcome)
		return
	if not bool(m.committed) or int(save.write_seq) < 1 \
			or int(state.saved_ack) != int(save.write_seq):
		_fail("mission-end commit/ack: committed=%s seq=%d ack=%d" % [
				m.committed, save.write_seq, state.saved_ack])
		return
	if int(state.heroes["warden"]["xp"]) != int(m.xp_earned):
		_fail("end xp award: %s != %s" % [state.heroes["warden"]["xp"], m.xp_earned])
		return
	print("MISSION-SMOKE-LOSE outcome=%s ack=%d seq=%d" % [
			m.outcome, state.saved_ack, save.write_seq])
	print("MISSION-SMOKE-OK")
	quit(0)
	return


func _fail(why: String) -> void:
	print("MISSION-SMOKE FAIL " + why)
	quit(1)
