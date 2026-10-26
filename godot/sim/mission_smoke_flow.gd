# mission_smoke_flow — the wave-flow legs of the mission smoke (W16 split
# of mission_smoke.gd, MC 11274.1.28 / card 11384; legs authored W6-W11,
# MC 11274.1.13/.15/.18/.19). Pure move — code and rows byte-identical.
# Build→combat alternation, the wave-0 spawn, lane advance, the core
# breach, the W7 hero kill, the wave awards + harness kill leg, the W11
# loot feed, the C4 refill, the W8 tower kill, the W7b ability + HUD
# blue-bar legs. Hero down-states are driven DIRECTLY by the harness:
# the pinned runner row is lane-walk only, so enemies never damage a hero
# (W7 ships the hero->enemy direction: hero_combat is the live damage
# source from the W7 legs on). Driving hero state directly is exactly the
# boot_probe precedent of driving real entry points.
# Machine rows: SPAWN HUD-WAVE HUD-GREEN ADVANCE CORE KILL WAVE LOOT
# REFILL W8KILL ABILITY HUD-BLUE (detail as printed; the pytest leg
# re-derives every number from waves/economy/xp/enemies data).
extends RefCounted


static func run(smoke, leg: Dictionary) -> bool:
	var m = leg["m"]
	var hud = leg["hud"]
	var rng = leg["rng"]
	var waves_total: int = int(leg["waves_total"])
	var per_wave: int = int(leg["per_wave"])
	var wave_xp: int = int(leg["wave_xp"])
	var w8_left: int = int(leg["w8_left"])
	# --- 1) build phase lasts build_seconds(waves[0]) = 25.0s, and the
	#        wave-0 delay-0 group spawns at combat-local t = 0 (tick 1)
	var guard := 0
	while guard < 1700 and String(m.phase_kind) == "build":
		m.step(1.0 / 60.0)
		guard += 1
	if guard >= 1700:
		smoke._fail("first combat never started (build alternation broken)")
		return false
	if guard < 1490 or guard > 1510:
		smoke._fail("first combat tick %d outside 25.0s +/-1s" % guard)
		return false
	if int(m.alive) != 1 or int(m.wave) != 0:
		smoke._fail("wave-0 spawn at combat start: alive=%d wave=%d" % [m.alive, m.wave])
		return false
	print("MISSION-SMOKE-SPAWN t=%d wave=%d alive=%d" % [guard, m.wave, m.alive])
	hud.refresh()
	if String(hud.wave_text()) != "Wave %d / %d" % [int(m.wave) + 1,
			waves_total]:
		smoke._fail("HUD combat wave label: %s" % hud.wave_text())
		return false
	print("MISSION-SMOKE-HUD-WAVE wave=%d text=%s" % [m.wave, hud.wave_text()])
	if String(hud.green_text()) != "Green %d / cap %d" % [int(m.green),
			int(m.economy["green"]["cap"])]:
		smoke._fail("HUD green label %s != state green %d" % [
				hud.green_text(), m.green])
		return false
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
		smoke._fail("no lane advance d0=%.2f d1=%.2f" % [d0, d1])
		return false
	print("MISSION-SMOKE-ADVANCE d0=%.2f d1=%.2f" % [d0, d1])
	# --- 3) reaching the gate reduces core HP; the skitterling def loads
	#        first because the W7 kill leg and the award math share it.
	var skit: Dictionary = {}
	for e: Dictionary in m.enemy_defs:
		if String(e.get("id", "")) == "skitterling":
			skit = e
	if skit.is_empty():
		smoke._fail("skitterling def missing from enemies data")
		return false
	leg["skit"] = skit
	guard = 0
	while guard < 1700 \
			and float(m.cores["main"]["hp"]) >= float(m.cores["main"]["max"]):
		m.step(1.0 / 60.0)
		guard += 1
	if guard >= 1700:
		smoke._fail("main core never took breach damage")
		return false
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
		smoke._fail("hero primary kill: green=%d xp=%d loot=%d phase=%s wave=%d" % [
				m.green, m.xp_earned, m.loot_pending, m.phase_kind, m.wave])
		return false
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
		smoke._fail("wave 0 never completed")
		return false
	if kills < 1 or int(m.wave) != 1 \
			or int(m.green) != w8_left \
				+ (kills + hero_kills) * int(skit["green"]) + per_wave \
			or int(m.xp_earned) != wave_xp \
				+ (kills + hero_kills) * int(skit["xp"]) \
			or int(m.loot_pending) != kills + hero_kills:
		smoke._fail("wave awards wrong: kills=%d wave=%d green=%d xp=%d loot=%d" % [
				kills, m.wave, m.green, m.xp_earned, m.loot_pending])
		return false
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
		smoke._fail("loot_events empty after kills (loot=%d)" % m.loot.size())
		return false
	var ev_last: Dictionary = m.loot_events[m.loot_events.size() - 1]
	hud.refresh()
	if String(hud.toast_text()).is_empty():
		smoke._fail("loot toast empty with %d events" % m.loot_events.size())
		return false
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
		smoke._fail("second combat never started")
		return false
	if float(m.blue) != float(m.blue_max) or float(m.blue_max) \
			!= float(m.hero_defs[m.hero_id]["base"]["blue_max"]):
		smoke._fail("no full blue refill at combat start: %s/%s" % [m.blue, m.blue_max])
		return false
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
		smoke._fail("W8 tower kill: green=%d xp=%d phase=%s" % [
				m.green, m.xp_earned, m.phase_kind])
		return false
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
		smoke._fail("ability spend: blue=%s != %s (tick-then-exact-cost)" % [
				m.blue, expect])
		return false
	m.bridge.on_key("Digit4", true)    # re-cast inside the cooldown window
	var b2 := float(m.blue)
	m.step(dt)
	if float(m.blue) < b2 - 1e-9 \
			or float(m.hero_state["warden"]["cooldowns"][3]) <= 0.0:
		smoke._fail("second cast not cooldown-gated: blue=%s cd=%s" % [
				m.blue, m.hero_state["warden"]["cooldowns"][3]])
		return false
	m.bridge.on_key("Digit4", false)
	print("MISSION-SMOKE-ABILITY ability=%s cost=%s blue=%s gated=1" % [
			String(w_abil["id"]), str(cost), str(m.blue)])
	hud.refresh()
	var blue_slot = hud.slot_node(int(m.active))
	var bbar: ProgressBar = blue_slot.get_node("BlueBar")
	if float(bbar.value) != float(m.blue) or float(bbar.max_value) \
			!= float(m.blue_max):
		smoke._fail("HUD blue bar %s/%s != state %s/%s" % [
				bbar.value, bbar.max_value, m.blue, m.blue_max])
		return false
	print("MISSION-SMOKE-HUD-BLUE active=%s blue=%s max=%s bar=%s ratio=%s" % [
			m.hero_id, m.blue, m.blue_max, bbar.value,
			str(float(bbar.value) / float(bbar.max_value))])
	return true
