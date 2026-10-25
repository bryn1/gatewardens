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
# Hero down-states are driven DIRECTLY by the harness: the pinned runner
# row is lane-walk only, so enemies never damage a hero (W7 ships the
# hero->enemy direction: hero_combat is the live damage source from the
# W7 legs on). Driving hero state directly is exactly the boot_probe
# precedent of driving real entry points.
# Machine rows (the pytest leg asserts, EMPTY stderr per the W4 ruling):
#   MISSION-SMOKE-SEED deck=<json>
#   MISSION-SMOKE-SPAWN t=<tick> wave=<i> alive=<n> (wave-0 delay-0 group
#                          spawns at combat-local t = 0)
#   MISSION-SMOKE-ADVANCE d0=<x> d1=<y>   (ground-lane walk closes on core)
#   MISSION-SMOKE-CORE hp=<x> max=<y>     (reaching the gate cut core HP)
#   MISSION-SMOKE-KILL t=<tick> wave=<i> green=<x> xp=<y> loot=<l> (W7:
#                          hero PRIMARY attack kills a live wave-0 enemy,
#                          awards flow through the pinned death funnel)
#   MISSION-SMOKE-WAVE green=<x> xp=<y>   (wave awards + build alternation)
#   MISSION-SMOKE-REFILL blue=<x> max=<y> (full refill at combat start)
#   MISSION-SMOKE-ABILITY ability=<id> cost=<c> blue=<b> gated=1 (W7: blue
#                          spent EXACTLY the cost; second cast cooldown-gated)
#   MISSION-SMOKE-SWAP hero=<id>          (F3 manual + down-swap F2-10)
#   MISSION-SMOKE-F1SWAP hero=<id> swap_blue=<b> deadeye_max=<m> (W7: F2/F1
#                          swap changes the ACTIVE pawn visual; the C4 blue
#                          swap clamp bites exactly at the new hero's cap)
#   MISSION-SMOKE-DOWN pawns=<n> visible=<v> (all-down F2-9 with pawns live)
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
	# --- 3) reaching the gate reduces core HP; the skitterling def loads
	#        first because the W7 kill leg and the award math share it.
	var skit: Dictionary = {}
	for e: Dictionary in m.enemy_defs:
		if String(e.get("id", "")) == "skitterling":
			skit = e
	if skit.is_empty():
		_fail("skitterling def missing from enemies data")
		return
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
	# --- 3b) (W7a) hero PRIMARY attack KILLS a live wave-0 enemy: the rig
	#        stands on the main core (map data), so the lane walk enters the
	#        melee range; MouseLeft held drives hero_combat -> SimCombat.
	#        hero_hit (crit roll from the pinned-seed rng) -> runner.damage,
	#        and the mission's step-(4) death funnel applies the awards
	#        unchanged (green+xp+one drop for exactly one skitterling).
	m.bridge.on_key("MouseLeft", true)
	var g0 := int(m.green)
	var x0 := int(m.xp_earned)
	var l0 := int(m.loot_pending)
	guard = 0
	while guard < 1700 and int(m.green) == g0:
		m.step(1.0 / 60.0)
		guard += 1
	m.bridge.on_key("MouseLeft", false)
	if int(m.green) != g0 + int(skit["green"]) \
			or int(m.xp_earned) != x0 + int(skit["xp"]) \
			or int(m.loot_pending) != l0 + 1 \
			or String(m.phase_kind) != "combat" or int(m.wave) != 0:
		_fail("hero primary kill: green=%d xp=%d loot=%d phase=%s wave=%d" % [
				m.green, m.xp_earned, m.loot_pending, m.phase_kind, m.wave])
		return
	var hero_kills := 1
	print("MISSION-SMOKE-KILL t=%d wave=%d green=%d xp=%d loot=%d" % [
			guard, m.wave, m.green, m.xp_earned, m.loot_pending])
	# --- 4) wave 0 clears -> awards + build alternation. The harness
	#        supplies the remaining kill leg (runner.damage on every entity
	#        left on the lanes): the wave-CLEAR transition and the award
	#        FORMULA are what this leg proves; W7's hero kill (3b) counts
	#        into the same totals.
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
			or int(m.green) != start_green \
				+ (kills + hero_kills) * int(skit["green"]) + per_wave \
			or int(m.xp_earned) != wave_xp \
				+ (kills + hero_kills) * int(skit["xp"]) \
			or int(m.loot_pending) != kills + hero_kills:
		_fail("wave awards wrong: kills=%d wave=%d green=%d xp=%d loot=%d" % [
				kills, m.wave, m.green, m.xp_earned, m.loot_pending])
		return
	print("MISSION-SMOKE-WAVE kills=%d green=%d xp=%d loot=%d" % [
			kills + hero_kills, m.green, m.xp_earned, m.loot_pending])
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
	# --- 5b) (W7b) ability dispatch, ACTIVE hero (warden) with blue full:
	#        Digit4 (the W4 code added for abilities, no swap alias) casts
	#        the 4th ability — blue spends EXACTLY its mana_cost (tick-then-
	#        spend, same frame) and the second cast is cooldown-gated (the
	#        cd array is the gate; the planted-red proof in the evidence
	#        shows removing it makes this leg go RED).
	var w_abil: Dictionary = m.hero_defs["warden"]["abilities"][3]
	var cost := float(w_abil["mana_cost"])
	var regen := float(m.hero_defs["warden"]["base"]["blue_regen"])
	var dt := 1.0 / 60.0
	m.bridge.on_key("Digit4", true)
	var b_pre := float(m.blue)
	m.step(dt)
	var expect := minf(b_pre + regen * dt, float(m.blue_max)) - cost
	if absf(float(m.blue) - expect) > 1e-9:
		_fail("ability spend: blue=%s != %s (tick-then-exact-cost)" % [
				m.blue, expect])
		return
	m.bridge.on_key("Digit4", true)    # re-cast inside the cooldown window
	var b2 := float(m.blue)
	m.step(dt)
	if float(m.blue) < b2 - 1e-9 \
			or float(m.hero_state["warden"]["cooldowns"][3]) <= 0.0:
		_fail("second cast not cooldown-gated: blue=%s cd=%s" % [
				m.blue, m.hero_state["warden"]["cooldowns"][3]])
		return
	m.bridge.on_key("Digit4", false)
	print("MISSION-SMOKE-ABILITY ability=%s cost=%s blue=%s gated=1" % [
			String(w_abil["id"]), str(cost), str(m.blue)])
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
	# --- 6b) (W7d) hot-swap changes the ACTIVE pawn visual and the C4 blue
	#        clamp bites EXACTLY at the new hero's cap: a harness blue write
	#        above every deck cap, then F2 (warden->deadeye, lower cap) —
	#        the swap clamp is min(100 -> 90) at the C4 _select site. F1
	#        swaps back and the pawn visuals toggle with the active hero.
	var rig = m.get_node("HeroRig")
	m.blue = 130.0                            # harness: above every cap
	m.bridge.on_key("F2", true)
	m.step(1.0 / 60.0)                        # clamp: 130->100 tick, 100->90 swap
	m.step(1.0 / 60.0)                        # pawn sync follows the swap
	var swap_blue := float(m.blue)
	if String(m.hero_id) != "deadeye" \
			or swap_blue != float(m.hero_defs["deadeye"]["base"]["blue_max"]) \
			or not bool(rig.pawns["deadeye"].visible) \
			or bool(rig.pawns["warden"].visible):
		_fail("F2 swap/clamp: hero=%s blue=%s deadeye_vis=%s" % [
				m.hero_id, m.blue, str(rig.pawns["deadeye"].visible)])
		return
	m.bridge.on_key("F1", true)
	m.step(1.0 / 60.0)
	m.step(1.0 / 60.0)
	if String(m.hero_id) != "warden" \
			or float(m.blue) > float(m.hero_defs["warden"]["base"]["blue_max"]) \
			or not bool(rig.pawns["warden"].visible) \
			or bool(rig.pawns["deadeye"].visible):
		_fail("F1 swap/clamp: hero=%s blue=%s warden_vis=%s" % [
				m.hero_id, m.blue, str(rig.pawns["warden"].visible)])
		return
	print("MISSION-SMOKE-F1SWAP hero=%s swap_blue=%s deadeye_max=%s" % [
			m.hero_id, str(swap_blue),
			str(m.hero_defs["deadeye"]["base"]["blue_max"])])
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
	# (W7c) the pawns are LIVE through this path: the rig holds one pawn
	# per deck hero and the all-down hero stand shows NONE of them (the
	# hp>0 sync rule — same-tick hp writes land before the sync).
	var shown := 0
	for pid: String in rig.pawns:
		if bool(rig.pawns[pid].visible):
			shown += 1
	if int(rig.pawns.size()) != DECK.size() or shown != 0:
		_fail("pawns in all-down path: total=%d shown=%d" % [
				rig.pawns.size(), shown])
		return
	print("MISSION-SMOKE-DOWN pawns=%d visible=%d" % [rig.pawns.size(), shown])
	print("MISSION-SMOKE-LOSE outcome=%s ack=%d seq=%d" % [
			m.outcome, state.saved_ack, save.write_seq])
	print("MISSION-SMOKE-OK")
	quit(0)
	return


func _fail(why: String) -> void:
	print("MISSION-SMOKE FAIL " + why)
	quit(1)
