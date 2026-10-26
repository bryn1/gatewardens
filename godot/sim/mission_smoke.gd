# hygiene: W8 legs carry this smoke asset past 400 lines (test asset,
# kept whole; MC 11274.1.15) — hard ceiling exempt per header rule.
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
#   MISSION-SMOKE-LOOT events=<n> base=<id> rarity=<r> toast=on (W11: the
#                          same kill fed the slot-(6) loot_pickup event
#                          mirror; the HUD toast renders the newest C9 row)
#   MISSION-SMOKE-WAVE green=<x> xp=<y>   (wave awards + build alternation)
#   MISSION-SMOKE-REFILL blue=<x> max=<y> (full refill at combat start)
#   MISSION-SMOKE-ABILITY ability=<id> cost=<c> blue=<b> gated=1 (W7: blue
#                          spent EXACTLY the cost; second cast cooldown-gated)
#   MISSION-SMOKE-SWAP hero=<id>          (F3 manual + down-swap F2-10)
#   MISSION-SMOKE-F1SWAP hero=<id> swap_blue=<b> deadeye_max=<m> (W7: F2/F1
#                          swap changes the ACTIVE pawn visual; the C4 blue
#                          swap clamp bites exactly at the new hero's cap)
#   MISSION-SMOKE-W14PANEL mount=1 class=<c> cost=<c> refund=<r> green=<g>
#                          (W14 P1-1: the panel is mounted by mission.setup
#                          itself; a KeyM press enters the shipped bridge,
#                          step (5) relays it to panel.poll, the tower
#                          lands for EXACTLY the data base_cost, and the
#                          undo sell through the SAME panel refunds the
#                          pinned R1 full-HP 0)
#   MISSION-SMOKE-W14SWAP hero=<id> digit2_cast=1 blue_drop=<b> f2_hero=
#                          <id> (W14 P1-4: a held Digit2 CASTS and changes
#                          NO hero — pre-W14 it teleported warden->deadeye;
#                          the F-keys stay the swap path)
#   MISSION-SMOKE-DOWN pawns=<n> visible=<v> (all-down F2-9 with pawns live)
#   MISSION-SMOKE-LOSE outcome=<o> ack=<a> seq=<s> (F2-9 same-tick LOSE
#                          wins + the single C13 mission-end commit)
#   (W8, MC 11274.1.15 / card 11322 — defenses; legs run in the build
#   phase except the tower-kill, which rides the REAL wave-1 combat):
#   MISSION-SMOKE-W8PLACE class=tower cost=<c> green=<g> tier=1 (green
#                          drops EXACTLY the towers.json base_cost)
#   MISSION-SMOKE-W8UPGRADE cost=<c> dps=<d> green=<g> (T1->T2 ladder
#                          price + the dps rise, both from data)
#   MISSION-SMOKE-W8REPAIR missing=0.5 cost=<c> green=<g> hp=<h>
#   MISSION-SMOKE-W8REPAIR1 cost=<c> green=<g> (floor-1 leg: missing=1/hp_max)
#   MISSION-SMOKE-W8PLACE2 class=blockade cost=<c> green=<g>
#   MISSION-SMOKE-W8CAP why=cap green=<g> count=<n> (cap+1 refused, green
#                          unchanged — harness cap write, boot_probe license)
#   MISSION-SMOKE-W8SELL refund=<r> green=<g> count=<n> (damaged defense:
#                          total_spent x sell_ratio x missing, R1 pinned)
#   MISSION-SMOKE-W8FREESLOT class=trap cost=<c> green=<g> charges=<t>
#   MISSION-SMOKE-W8PANEL classes=<a|b|c> gate=<n-affordable at trap cost>
#   MISSION-SMOKE-W8PANEL-ACT refund=<r> cost=<c> green=<g> (panel routes
#                          through placer/obj APIs — bridge-code presses)
#   MISSION-SMOKE-W8KILL t=<frames> green=+<g> xp=+<x> (tower dps kills a
#                          live enemy through funnel slot (3) + step-(4)
#                          awards; hero holds nothing — attribution clean)
#   (W10, MC 11274.1.18 / card 11325 — the read-only HUD mounted by the
#   mission's DECLARED hook; refresh() is driven here exactly as the W8
#   panel legs drive panel.refresh(), E5: no _process dispatch under -s):
#   MISSION-SMOKE-HUD-BUILD wave=<i> secs=<s> text=<label> (build-phase
#                          label rides SimWave build_seconds + the phase
#                          controller's ONE timer — never a second timer)
#   MISSION-SMOKE-HUD-WAVE wave=<i> text=<label>   (combat "Wave n / 11",
#                          the total via SimWave.total_waves — no literal)
#   MISSION-SMOKE-HUD-GREEN green=<g> cap=<c> text=<label> (green count
#                          matches the state mirror; cap is economy.json's)
#   MISSION-SMOKE-HUD-BLUE active=<hero> blue=<b> max=<m> ratio=<r> (the
#                          ACTIVE slot's blue bar mirrors the one C4 pool
#                          and its max; ratio checked against the state)
#   MISSION-SMOKE-HUD-HL slot=<i> hero=<id> (x2: F2 then F1 — the ACTIVE
#                          highlight READS BACK off the slot tint and
#                          moves with the shipped swap, incl. the F2-10
#                          down-swap already asserted above)
#   MISSION-SMOKE-HUD-BOSS visible=1 wave=<i> hp=<h> max=<m> text=<label>
#                          (boss bar appears exactly while C5 boss_hp is
#                          non-null on the boss wave; the harness drives
#                          the wave index + the real start_wave entry —
#                          the boot_probe license, the funnel fills boss
#                          + boss_hp unchanged)
#   MISSION-SMOKE-HUD-BANNER outcome=<o> text=<t> (outcome banner row:
#                          honest copy off the shipped outcome field)
#   MISSION-SMOKE-OK
# E3: quit() under -s does NOT abort the running frame — every failure
# path early-returns; each quit() fires exactly once.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const DEF_PLACER := preload("res://scripts/defense_placer.gd")
const DEF_PANEL := preload("res://scripts/defense_panel.gd")

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
	# --- HUD (W10, MC 11274.1.18 / card 11325): the read-only overlay the
	#        mission's DECLARED hook mounted. refresh() is driven here
	#        exactly as the W8 panel legs drive panel.refresh() (E5: no
	#        frame dispatch under -s); every label the pytest leg re-
	#        derives rides shipped data (waves/economy/heroes/enemies),
	#        never a test-side copy.
	var hud = m.get_node("HUD")
	if hud == null:
		_fail("declared hook mounted no HUD node on the mission root")
		return
	var waves_total: int = m.waves_file.get("waves", []).size()
	hud.refresh()
	var build_secs := int(ceilf(float(m.waves_file["waves"][0].get(
			"build_seconds", 0.0))))
	if String(hud.wave_text()) != "Build: wave %d in %d s" % [
			int(m.wave) + 1, build_secs] or String(hud.banner_text()) != "":
		_fail("HUD build label: %s (banner %s)" % [
				hud.wave_text(), hud.banner_text()])
		return
	print("MISSION-SMOKE-HUD-BUILD wave=%d secs=%d text=%s" % [
			m.wave, build_secs, hud.wave_text()])
	# --- W14 P1-1 (MC 11274.1.25 / card 11341): placement is reachable
	#        IN THE LIVE PATH — mission.setup() mounted the panel itself
	#        (the W10 HUD idiom); a KeyM press enters the SHIPPED bridge,
	#        mission step (5) relays it to panel.poll, and the tower
	#        lands for EXACTLY the towers.json base_cost — THROUGH the
	#        panel path, never around it. Undo: the fresh full-HP defense
	#        is sold through the SAME panel (pinned R1: full-HP refund 0)
	#        and green is harness-written back to start_green (the W8
	#        green-write / boot_probe license, declared) so the W8 legs
	#        below run on the state they were authored against.
	var panel = m.get_node("DefensePanel")
	if panel == null:
		_fail("mission.setup() mounted no DefensePanel (P1-1)")
		return
	if panel.class_rows.is_empty() or panel.placer == null:
		_fail("DefensePanel.setup() built no classes/placer")
		return
	var p_green0 := int(m.green)
	var p_class: Dictionary = panel.class_rows[0]
	m.bridge.on_key("KeyM", true)
	m.bridge.on_key("KeyM", false)
	m.step(1.0 / 60.0)                 # step (5) routes the relayed press
	if m.defense_list.size() != 1 \
			or int(m.green) != p_green0 - int(p_class["cost"]):
		_fail("P1-1 bridge place: green=%d count=%d" % [
				m.green, m.defense_list.size()])
		return
	panel.select_defense(int(m.defense_list[0]["uid"]))
	panel.handle_press("KeyN")         # full-HP sell: the pinned R1 refund
	var p_after_sell := int(m.green)
	var p_refund := p_after_sell - (p_green0 - int(p_class["cost"]))
	m.green = p_green0                 # license write (header comment)
	print("MISSION-SMOKE-W14PANEL mount=1 class=%s cost=%d refund=%d green=%d" % [
			String(p_class["class"]), int(p_class["cost"]), p_refund,
			int(m.green)])
	# --- W0) W8 defense legs (MC 11274.1.15 / card 11322), all in the
	#        build phase; every price/refund is asserted against the data
	#        files by the pytest leg, never decided from literals here.
	var placer = DEF_PLACER.new()
	placer.setup(m)
	var blockade_row: Dictionary = placer.row_for("blockade")
	var trap_row: Dictionary = placer.row_for("trap")
	if blockade_row.is_empty() or trap_row.is_empty() \
			or placer.row_for("tower").is_empty():
		_fail("towers.json class rows missing")
		return
	var slot_t := placer.slot_at(m.lanes["lane_g3"]["wps"][0])
	var slot_b := placer.slot_at(m.lanes["lane_g2"]["wps"][2])
	var slot_a := placer.slot_at(m.lanes["lane_g1"]["wps"][0])
	if slot_t < 0 or slot_b < 0 or slot_a < 0 or slot_a == slot_b:
		_fail("lane-geometry buildable slots missing")
		return
	var pres := placer.place("tower", 1, slot_t)
	if not bool(pres["ok"]) or int(m.green) != start_green - int(pres["cost"]):
		_fail("W8 place: ok=%s green=%d" % [str(pres["ok"]), m.green])
		return
	print("MISSION-SMOKE-W8PLACE class=tower cost=%d green=%d tier=1" % [
			int(pres["cost"]), m.green])
	var tower_uid := int(pres["uid"])
	var tower_obj = _w8obj(m, tower_uid)
	var dps1: float = tower_obj.dps()
	var ures := placer.upgrade(tower_uid)
	var dps2: float = tower_obj.dps()
	if not bool(ures["ok"]) or int(m.green) != start_green \
			- int(pres["cost"]) - int(ures["cost"]) or dps2 <= dps1:
		_fail("W8 upgrade: %s dps %s->%s green=%d" % [
				str(ures), str(dps1), str(dps2), m.green])
		return
	print("MISSION-SMOKE-W8UPGRADE cost=%d dps=%.2f green=%d" % [
			int(ures["cost"]), dps2, m.green])
	tower_obj.take_damage(tower_obj.hp_max * 0.5)   # harness half-missing leg
	var rres := placer.repair(tower_uid)
	if not bool(rres["ok"]) or float(tower_obj.hp) != float(tower_obj.hp_max):
		_fail("W8 repair: %s hp=%s" % [str(rres), str(tower_obj.hp)])
		return
	print("MISSION-SMOKE-W8REPAIR missing=0.5 cost=%d green=%d hp=%s" % [
			int(rres["cost"]), m.green, str(tower_obj.hp)])
	tower_obj.take_damage(1.0)                      # floor-1 leg (<1 rounds to 0)
	var fres := placer.repair(tower_uid)
	if not bool(fres["ok"]) or int(fres["cost"]) != 1:
		_fail("W8 repair floor-1: %s" % str(fres))
		return
	print("MISSION-SMOKE-W8REPAIR1 cost=%d green=%d" % [int(fres["cost"]), m.green])
	var bres := placer.place("blockade", 1, slot_b)
	if not bool(bres["ok"]):
		_fail("W8 blockade place: %s" % str(bres))
		return
	print("MISSION-SMOKE-W8PLACE2 class=blockade cost=%d green=%d" % [
			int(bres["cost"]), m.green])
	# Cap boundary: harness writes the cap DOWN to the live count (the
	# boot_probe drive-real-entry-points license) so the NEXT place is the
	# pinned cap+1 refusal; green must not move.
	m.defense_cap = m.defense_list.size()
	var g_before := int(m.green)
	var cres := placer.place("blockade", 1, slot_a)
	if String(cres["why"]) != "cap" or int(m.green) != g_before \
			or m.defense_list.size() != m.defense_cap:
		_fail("W8 cap+1: %s green=%d count=%d" % [
				str(cres), m.green, m.defense_list.size()])
		return
	print("MISSION-SMOKE-W8CAP why=cap green=%d count=%d" % [
			m.green, m.defense_list.size()])
	var block_obj = _w8obj(m, int(bres["uid"]))
	block_obj.take_damage(block_obj.hp_max * 0.5)   # damaged -> refund > 0
	var g_pre_sell := int(m.green)
	var sres := placer.sell(int(bres["uid"]))
	if not bool(sres["ok"]) or m.defense_list.size() != 1 \
			or int(m.green) != g_pre_sell + int(sres["refund"]):
		_fail("W8 sell: %s green=%d count=%d" % [
				str(sres), m.green, m.defense_list.size()])
		return
	print("MISSION-SMOKE-W8SELL refund=%d green=%d count=%d" % [
			int(sres["refund"]), m.green, m.defense_list.size()])
	var tres := placer.place("trap", 1, slot_b)     # the freed slot, exact-cost
	if not bool(tres["ok"]) or int(m.green) != g_pre_sell + int(sres["refund"]) \
			- int(tres["cost"]):
		_fail("W8 sell frees no cap slot: %s green=%d" % [str(tres), m.green])
		return
	var trap_obj = _w8obj(m, int(tres["uid"]))       # affordability edge
	print("MISSION-SMOKE-W8FREESLOT class=trap cost=%d green=%d charges=%d" % [
			int(tres["cost"]), m.green, int(trap_obj.charges)])
	# Panel leg: functional greybox Control — lists v1 classes, gates by
	# can_afford, and its actions route THROUGH the placer/obj APIs. The
	# gate count rides a harness green write at exactly the trap price
	# (the two data-cheap classes affordable, the tower class not).
	# W14 (MC 11274.1.25): this leg now drives the SAME panel the mission
	# mounted at setup (reuse-first; the pre-W14 smoke instantiated its
	# own second panel around the live one).
	m.green = int(trap_row["base_cost"])
	panel.refresh()
	var ids: Array = []
	for crow: Dictionary in panel.class_rows:
		ids.append(String(crow["class"]))
	var enabled := 0
	for cid: String in panel.class_buttons:
		if not bool(panel.class_buttons[cid].disabled):
			enabled += 1
	print("MISSION-SMOKE-W8PANEL classes=%s gate=%d" % ["|".join(ids), enabled])
	var ps0 := int(m.green)
	panel.select_defense(int(tres["uid"]))
	panel.handle_press("KeyN")        # sell the full-HP trap: pinned refund 0
	var w8_refund := int(m.green) - ps0
	panel.select_class(1)             # data order: tower, blockade, trap
	panel.handle_press("KeyM")        # place blockade, first free slot
	var p_cost := ps0 - int(m.green)
	if w8_refund != 0 or p_cost != int(blockade_row["base_cost"]) \
			or m.defense_list.size() != int(m.defense_cap):
		_fail("W8 panel actions: refund=%d cost=%d count=%d" % [
				w8_refund, p_cost, m.defense_list.size()])
		return
	print("MISSION-SMOKE-W8PANEL-ACT refund=%d cost=%d green=%d" % [
			w8_refund, p_cost, m.green])
	var w8_left := int(m.green)       # the wave-award formula's green base
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
	hud.refresh()
	if String(hud.wave_text()) != "Wave %d / %d" % [int(m.wave) + 1,
			waves_total]:
		_fail("HUD combat wave label: %s" % hud.wave_text())
		return
	print("MISSION-SMOKE-HUD-WAVE wave=%d text=%s" % [m.wave, hud.wave_text()])
	if String(hud.green_text()) != "Green %d / cap %d" % [int(m.green),
			int(m.economy["green"]["cap"])]:
		_fail("HUD green label %s != state green %d" % [
				hud.green_text(), m.green])
		return
	print("MISSION-SMOKE-HUD-GREEN green=%d cap=%d text=%s" % [
			m.green, int(m.economy["green"]["cap"]), hud.green_text()])
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
			or int(m.green) != w8_left \
				+ (kills + hero_kills) * int(skit["green"]) + per_wave \
			or int(m.xp_earned) != wave_xp \
				+ (kills + hero_kills) * int(skit["xp"]) \
			or int(m.loot_pending) != kills + hero_kills:
		_fail("wave awards wrong: kills=%d wave=%d green=%d xp=%d loot=%d" % [
				kills, m.wave, m.green, m.xp_earned, m.loot_pending])
		return
	print("MISSION-SMOKE-WAVE kills=%d green=%d xp=%d loot=%d" % [
			kills + hero_kills, m.green, m.xp_earned, m.loot_pending])
	# --- 4a) (W11, MC 11274.1.19 / card 11326) the loot_pickup event feed:
	#        every kill dropped into the tray in funnel slot (4); slot (6)
	#        mirrored the item rows (pinned C9 shape) into m.loot_events
	#        and the HUD toast renders the newest one (DECLARED read —
	#        I4: the HUD writes nothing). The count is rng-shaped (drop
	#        weights roll per kill), so the leg asserts feed-not-empty +
	#        C9-field reads; pytest re-derives base/rarity from data.
	if m.loot_events.is_empty():
		_fail("loot_events empty after kills (loot=%d)" % m.loot.size())
		return
	var ev_last: Dictionary = m.loot_events[m.loot_events.size() - 1]
	hud.refresh()
	if String(hud.toast_text()).is_empty():
		_fail("loot toast empty with %d events" % m.loot_events.size())
		return
	print("MISSION-SMOKE-LOOT events=%d base=%s rarity=%s toast=on" % [
			m.loot_events.size(), String(ev_last["base_id"]),
			String(ev_last["rarity"])])
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
	# --- 5a) (W8) the placed+upgraded TOWER KILLS a live enemy through
	#        the pinned funnel: the harness spawns one skitterling on the
	#        far sub-lane (real C2 runner.spawn entry, closed lane = no
	#        mission spawns there), the tower's step-(3) dps tick drains
	#        it and the step-(4) death funnel awards green+xp unchanged.
	#        Nothing else holds input or deals damage in this window
	#        (the trap was sold in the panel leg) — attribution is clean.
	var srow := {"enemy_id": "skitterling", "count": 1, "lane": "lane_g3",
		"delay": 0.0}
	runner.spawn(srow, m.lanes["lane_g3"], m.enemy_defs, rng)
	var gk := int(m.green)
	var xk := int(m.xp_earned)
	guard = 0
	while guard < 600 and int(m.green) == gk:
		m.step(1.0 / 60.0)
		guard += 1
	if int(m.green) != gk + int(skit["green"]) \
			or int(m.xp_earned) != xk + int(skit["xp"]) \
			or String(m.phase_kind) != "combat":
		_fail("W8 tower kill: green=%d xp=%d phase=%s" % [
				m.green, m.xp_earned, m.phase_kind])
		return
	print("MISSION-SMOKE-W8KILL t=%d green=+%d xp=+%d" % [
			guard, int(m.green) - gk, int(m.xp_earned) - xk])
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
	hud.refresh()
	var blue_slot = hud.slot_node(int(m.active))
	var bbar: ProgressBar = blue_slot.get_node("BlueBar")
	if float(bbar.value) != float(m.blue) or float(bbar.max_value) \
			!= float(m.blue_max):
		_fail("HUD blue bar %s/%s != state %s/%s" % [
				bbar.value, bbar.max_value, m.blue, m.blue_max])
		return
	print("MISSION-SMOKE-HUD-BLUE active=%s blue=%s max=%s bar=%s ratio=%s" % [
			m.hero_id, m.blue, m.blue_max, bbar.value,
			str(float(bbar.value) / float(bbar.max_value))])
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
	hud.refresh()
	if int(hud.highlight_index()) != 0 or String(hud.banner_text()) != "":
		_fail("HUD highlight after F2-10 down-swap: hl=%s banner=%s" % [
				hud.highlight_index(), hud.banner_text()])
		return
	print("MISSION-SMOKE-HUD-HL slot=%d hero=%s" % [
			hud.highlight_index(), m.hero_id])
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
	hud.refresh()
	if int(hud.highlight_index()) != 1 or String(hud.hero_of_slot(1)) \
			!= "deadeye":
		_fail("HUD highlight after F2: hl=%s slot1=%s" % [
				hud.highlight_index(), hud.hero_of_slot(1)])
		return
	print("MISSION-SMOKE-HUD-HL slot=%d hero=%s" % [
			hud.highlight_index(), m.hero_id])
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
	hud.refresh()
	if int(hud.highlight_index()) != 0 or String(hud.hero_of_slot(0)) \
			!= "warden":
		_fail("HUD highlight after F1: hl=%s slot0=%s" % [
				hud.highlight_index(), hud.hero_of_slot(0)])
		return
	print("MISSION-SMOKE-HUD-HL slot=%d hero=%s" % [
			hud.highlight_index(), m.hero_id])
	print("MISSION-SMOKE-F1SWAP hero=%s swap_blue=%s deadeye_max=%s" % [
			m.hero_id, str(swap_blue),
			str(m.hero_defs["deadeye"]["base"]["blue_max"])])
	# --- 6b2) W14 P1-4 (MC 11274.1.25 / card 11341): the digit-as-swap
	#        collision is GONE. A held Digit2 press CASTS ability 2 (blue
	#        drops EXACTLY heroes.json mana_cost, the shipped hero_combat
	#        crossing) and changes the ACTIVE HERO NOT AT ALL — the same
	#        press pre-W14 teleported the hero warden->deadeye (the audit
	#        P1-4 RED). The F-keys stay the swap path: the follow-up F2
	#        press DOES swap (C4 pinned keys).
	var w14_hero := String(m.hero_id)
	var w14_blue := float(m.blue)
	m.bridge.on_key("Digit2", true)
	m.step(1.0 / 60.0)
	m.bridge.on_key("Digit2", false)
	var w14_cost := w14_blue - float(m.blue)
	if String(m.hero_id) != w14_hero or w14_cost <= 0.0:
		_fail("digit-collision: hero=%s (was %s) blue-drop=%s" % [
				m.hero_id, w14_hero, str(w14_cost)])
		return
	m.bridge.on_key("F2", true)
	m.step(1.0 / 60.0)
	m.bridge.on_key("F2", false)
	if String(m.hero_id) == w14_hero:
		_fail("F2 stopped swapping after the digit-alias removal")
		return
	print("MISSION-SMOKE-W14SWAP hero=%s digit2_cast=1 blue_drop=%s f2_hero=%s" % [
			w14_hero, str(w14_cost), m.hero_id])
	# --- 6c) (W10) boss bar on the boss wave: the harness writes the wave
	#        index and calls the REAL start_wave entry (boot_probe drive-
	#        real-entry-points license — nothing in v1 clears waves 0..9 to
	#        reach index 10 inside a smoke); the boss spawn + the boss_hp
	#        mirror are filled by the shipped funnel step-(4)/(5) paths, and
	#        the HUD bar renders C5's non-null truth (F13) with no literals.
	var pc = m.get_node("PhaseController")
	pc.wave = waves_total - 1
	m.wave = waves_total - 1
	m.start_wave(waves_total - 1)
	guard = 0
	while guard < 600 and m.boss == null:
		m.step(1.0 / 60.0)
		guard += 1
	if m.boss == null:
		_fail("boss never spawned on the boss wave")
		return
	hud.refresh()
	if not bool(hud.boss_visible()) or String(hud.wave_text()) \
			!= "Wave %d / %d" % [waves_total, waves_total]:
		_fail("HUD boss bar: visible=%s text=%s" % [
				hud.boss_visible(), hud.wave_text()])
		return
	print("MISSION-SMOKE-HUD-BOSS visible=1 wave=%d hp=%s max=%s text=%s" % [
			m.wave, m.boss_hp, m.boss["hp_max"], hud.boss_text()])
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
	hud.refresh()
	if String(hud.banner_text()) != "DEFEAT" or not bool(hud.banner_shown()):
		_fail("HUD banner: text=%s shown=%s outcome=%s" % [
				hud.banner_text(), hud.banner_shown(), m.outcome])
		return
	print("MISSION-SMOKE-HUD-BANNER outcome=%s text=%s" % [
			m.outcome, hud.banner_text()])
	print("MISSION-SMOKE-LOSE outcome=%s ack=%d seq=%d" % [
			m.outcome, state.saved_ack, save.write_seq])
	print("MISSION-SMOKE-OK")
	quit(0)
	return


func _fail(why: String) -> void:
	print("MISSION-SMOKE FAIL " + why)
	quit(1)


func _w8obj(m, uid: int):
	for rec: Dictionary in m.defense_list:
		if int(rec["uid"]) == uid:
			return rec["obj"]
	return null
