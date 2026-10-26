# mission_heroes — the mission-local hero table build + the C4 swap
# legs (W16 split of mission.gd, MC 11274.1.28 / card 11384; authored
# W6/W7 + W14). Pure move — bodies byte-identical. C4: ONE blue pool;
# the ACTIVE slot's identity, the swap clamp, and the all-down read all
# live HERE so the mission root stays the C12 funnel it declares itself
# to be. mission.gd keeps the call sites (step_bookkeeping routes the
# pinned SWAP_KEYS here; phase_controller's full-HP revival calls
# mission.revive_downed, which delegates to revive below).
extends RefCounted

const SIM_PROGRESSION := preload("res://sim/sim_progression.gd")


static func build_heroes(m) -> void:
	for row: Dictionary in m.tables.rows("heroes"):
		m.hero_defs[String(row["id"])] = row
	# W14 (MC 11274.1.25 / card 11341, P1-3): the ONE consumer site of
	# asc_modifier — spent ascension points ride onto the mission-local
	# hero rows (SimProgression's own aggregation, zero literals here).
	# The rows are this mission's freshly-parsed tables.rows copies, so
	# the loaded table is never touched (C1 read-only). Every reader of
	# base stats (hero_state hp, C4 blue_max/regen, hero_combat damage/
	# crit/ability_power) picks the modifiers up THROUGH THIS ONE WRITE.
	var mods: Dictionary = SIM_PROGRESSION.asc_modifier(
			m.tables.table("ascension").get("tree", {}), m.state.asc_spent)
	for stat: String in mods:
		for hid: String in m.hero_defs:
			var hero_base: Dictionary = m.hero_defs[hid]["base"]
			if hero_base.has(stat):
				hero_base[stat] = float(hero_base[stat]) + float(mods[stat])
	m.deck = m.state.deck.duplicate() if not m.state.deck.is_empty() \
			else m.hero_defs.keys()
	for hid: Variant in m.deck:
		var base: Dictionary = m.hero_defs[String(hid)]["base"]
		m.hero_state[String(hid)] = {"hp": float(base["health"]),
			"hp_max": float(base["health"]), "downed": false,
			"cooldowns": [0.0, 0.0, 0.0, 0.0]}
	select(m, 0)
	m.blue = m.blue_max    # setup init (NOT the refill path — that is pc-only)


# C4: build-phase-start revival at full HP; downed stay unswappable.
static func revive(m) -> void:
	for hid: String in m.hero_state:
		var hs: Dictionary = m.hero_state[hid]
		if bool(hs["downed"]):
			hs["downed"] = false
			hs["hp"] = float(hs["hp_max"])


static func try_swap(m, i: int) -> void:
	if i < 0 or i >= m.deck.size() or i == m.active:
		return
	if bool(m.hero_state[m.deck[i]]["downed"]):
		return    # downed heroes are unswappable until next build start
	select(m, i)


static func auto_swap(m) -> void:
	# F2-10: deck order from downed+1, wrapping at most once; none found
	# -> the all-down lose path (step 5).
	for off: int in range(1, m.deck.size()):
		var j: int = (m.active + off) % m.deck.size()
		if not bool(m.hero_state[m.deck[j]]["downed"]):
			select(m, j)
			return


static func select(m, i: int) -> void:
	m.active = i
	m.hero_id = String(m.deck[i])
	m.blue_max = float(m.hero_defs[m.hero_id]["base"]["blue_max"])
	m.blue = minf(m.blue, m.blue_max)   # C4 swap clamp


static func all_down(m) -> bool:
	if m.hero_state.is_empty():
		return false
	for hid: String in m.hero_state:
		if not bool(m.hero_state[hid]["downed"]):
			return false
	return true
