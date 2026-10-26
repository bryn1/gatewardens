# hub_probe_mission — the RELIC + CHEST legs of the hub probe over the
# REAL mission.tscn (W16 split of hub_probe.gd, MC 11274.1.28 / card
# 11384; legs authored W9 + W14, MC 11274.1.16/.25). Pure move — code and
# rows byte-identical.
#   RELIC    the REAL mission.tscn + the pinned C11 crossing: both relic
#            legs observable on the placed defense (dps / hp_max through
#            the SAME bonus_row + tower_dps sites), refusals BOTH ways
#            (relic taken / defense taken / unknown uid / unknown relic /
#            wrong phase / unassign-none), unequip-return, and the meta
#            save round-trip through the save FILE (relics AND ascension).
#   CHEST    the REAL mission.tscn: harness sets win_pending (drive-real-
#            entry-points license), step (6) rolls the FREE victory chest
#            (chest_tiers[0] for normal, BN3) and the row enters the bank
#            INSIDE the same C13 mission-end commit — bank grows by
#            EXACTLY one, gold untouched, the gear panel shows the grown
#            bank after the return.
# Machine rows: RELIC CHEST (tests/test_hub.py re-derives hp_delta from
# items.json — orb_of_the_deep's hp primary x the scripted ilvl the probe
# seeds — and the chest rarity from rarity.json chest_tiers).
extends RefCounted

const MISSION_SCENE := "res://scenes/mission.tscn"
const GW_GAME_STATE := preload("res://scripts/game_state.gd")


static func run(probe, leg: Dictionary) -> bool:
	var state = probe.state
	var root = probe.root
	var ctx: Dictionary = probe.ctx
	var hero0: String = String(leg["hero0"])
	var asc_earned: int = int(leg["asc_earned"])
	var res_pts: int = int(leg["res_pts"])
	var gear = leg["gear"]

	# ---- RELIC leg (W14 P1-2, MC 11274.1.25 / card 11341): the pinned
	#      C11 crossing on the REAL mission scene (instantiated below).

	# ---- CHEST leg: the mission-end commit carries the bank +1 ----
	var mpacked = ResourceLoader.load(MISSION_SCENE)
	if mpacked == null:
		probe._fail("mission.tscn not loadable")
		return false
	var m = mpacked.instantiate()
	root.add_child(m)
	m._ready()
	var m_rng := RandomNumberGenerator.new()
	m_rng.seed = 11274
	state.bank_add(probe._scripted_item(leg["relic2_spec"]))   # pool-side before setup()
	m.setup(probe.tables, state, probe.save, probe.bridge, "gatefall", "normal", m_rng)
	# RELIC leg body (comment above): pinned C11 crossing + refusals +
	# unequip-return + the single-site bonus observable + save round-trip.
	var pool_a: Dictionary = {}
	var pool_b: Dictionary = {}
	for pool_row: Dictionary in m.relic_pool:
		if String(pool_row["base_id"]) == String(leg["relic_spec"]["base_id"]):
			pool_a = pool_row
		if String(pool_row["base_id"]) == String(leg["relic2_spec"]["base_id"]):
			pool_b = pool_row
	if pool_a.is_empty() or pool_b.is_empty() or int(m.relics_assigned) != 0:
		probe._fail("relic pool copy: %s assigned=%d" % [str(m.relic_pool.size()),
				m.relics_assigned])
		return false
	var tower_row: Dictionary = {}
	for trow: Dictionary in probe.tables.rows("towers"):
		if String(trow["class"]) == "tower":
			tower_row = trow
			break
	var rl_g0 := int(m.green)
	var rl_p1: Dictionary = m.place_defense(tower_row, 1, Vector3.ZERO)
	var rl_p2: Dictionary = m.place_defense(tower_row, 1, Vector3(2, 0, 0))
	if not bool(rl_p1["ok"]) or not bool(rl_p2["ok"]) \
			or int(m.green) != rl_g0 - 2 * int(tower_row["base_cost"]):
		probe._fail("relic leg place: %s %s green=%d" % [str(rl_p1), str(rl_p2),
				m.green])
		return false
	var def_a = probe._probe_defense(m, int(rl_p1["uid"]))
	var def_b = probe._probe_defense(m, int(rl_p2["uid"]))
	var dps0 := float(def_a.dps())
	var hp0 := float(def_a.hp_max)
	var ref_none: Dictionary = m.unassign_relic(int(rl_p1["uid"]))
	var ar1: Dictionary = m.assign_relic(int(rl_p1["uid"]),
			int(pool_a["uid"]))          # damage leg rides onto the tower
	if not bool(ar1["ok"]) or int(m.relics_assigned) != 1 \
			or float(def_a.dps()) <= dps0 or float(def_a.hp_max) != hp0:
		probe._fail("assign A: %s assigned=%d dps %s->%s" % [str(ar1),
				m.relics_assigned, str(dps0), str(def_a.dps())])
		return false
	var hp_b0 := float(def_b.hp_max)     # BEFORE the bonus leg rides on
	var dps_b0 := float(def_b.dps())
	var ar2: Dictionary = m.assign_relic(int(rl_p2["uid"]),
			int(pool_b["uid"]))          # hp leg: hp_max rises, dps stays
	if not bool(ar2["ok"]) or int(m.relics_assigned) != 2 \
			or float(def_b.hp_max) <= hp_b0 or float(def_b.dps()) != dps_b0:
		probe._fail("assign B: %s assigned=%d hp %s->%s" % [str(ar2),
				m.relics_assigned, str(hp_b0), str(def_b.hp_max)])
		return false
	# Slot-cap refusals BOTH ways: a relic already worn is refused, and
	# a defense that already carries one is refused; uid/relic/phase/none
	# refusals ride the same shipped gates.
	var ref_taken: Dictionary = m.assign_relic(int(rl_p2["uid"]),
			int(pool_a["uid"]))
	var ref_uid: Dictionary = m.assign_relic(999999, int(pool_a["uid"]))
	var ref_rel: Dictionary = m.assign_relic(int(rl_p1["uid"]), 999999)
	m.phase_kind = "combat"              # drive-real-entry-points write
	var ref_phase: Dictionary = m.assign_relic(int(rl_p1["uid"]),
			int(pool_b["uid"]))
	m.phase_kind = "build"
	if String(ref_taken["why"]) != "taken" or String(ref_uid["why"]) != "uid" \
			or String(ref_rel["why"]) != "relic" \
			or String(ref_none["why"]) != "none" \
			or String(ref_phase["why"]) != "phase" \
			or int(m.relics_assigned) != 2:
		probe._fail("relic refusals: %s %s %s %s %s count=%d" % [str(ref_taken),
				str(ref_uid), str(ref_rel), str(ref_none), str(ref_phase),
				m.relics_assigned])
		return false
	# Unequip-return (C11 pool): the clear drops the bonus legs; the row
	# never left relic_pool, so the pool count is intact afterwards.
	var un: Dictionary = m.unassign_relic(int(rl_p1["uid"]))
	if not bool(un["ok"]) or int(m.relics_assigned) != 1 \
			or absf(float(def_a.dps()) - dps0) > 1e-6 \
			or absf(float(def_a.hp_max) - hp0) > 1e-6 \
			or m.relic_pool.size() != 2:
		probe._fail("unequip-return: %s assigned=%d dps=%s pool=%d" % [str(un),
				m.relics_assigned, str(def_a.dps()), m.relic_pool.size()])
		return false
	# Save round-trip (C13): every seeded relic row AND the ascension
	# spend ride the save FILE into a freshly reloaded state — the pool
	# of the NEXT mission is rebuilt from that bank (setup() above read
	# it live; the same source feeds the reload).
	var raw_r: Dictionary = probe.save.load_save()
	var st_r = GW_GAME_STATE.new(probe.tables)
	st_r.from_save(raw_r)
	var relics_back := 0
	for row: Dictionary in st_r.bank:
		if String(row.get("slot", "")) == "relic":
			relics_back += 1
	if relics_back != 2 or int(st_r.asc_earned) != asc_earned \
			or int(st_r.asc_spent.get("reservoir", 0)) != res_pts:
		probe._fail("save round-trip: relics=%d asc=%s/%s" % [relics_back,
				str(st_r.asc_earned), str(st_r.asc_spent)])
		return false
	# Effect at the pinned consumer site: mission setup applied reservoir
	# (+val blue_max per point) to the LOCAL hero rows — blue_max reads
	# it, and the snapshot mirrors the same value.
	var wbase := 0.0
	for hrow: Dictionary in probe.tables.rows("heroes"):
		if String(hrow["id"]) == hero0:
			wbase = float(hrow["base"]["blue_max"])
	var rrow: Dictionary = probe._asc_power("reservoir")
	var want_blue := wbase + float(rrow["per_point"]["val"]) * res_pts
	var snap: Dictionary = JSON.parse_string(state.snapshot_json(m))
	if absf(float(m.blue_max) - want_blue) > 1e-6 \
			or absf(float(snap.get("blue_max", -1.0)) - want_blue) > 1e-6 \
			or int(snap.get("relics_assigned", -1)) != int(m.relics_assigned):
		probe._fail("asc effect at mission site: blue_max=%s want=%s snap=%s" % [
				str(m.blue_max), str(want_blue), str(snap.get("blue_max"))])
		return false
	print("HUB-PROBE-RELIC assigned=1 refused_taken=1 refused_uid=1 refused_relic=1 refused_phase=1 refused_none=1 unequip=1 pool_intact=2 hp_delta=%.1f save_roundtrip=2 asc_kept=1 effect_blue=%.1f" % [
			float(def_b.hp_max) - hp_b0, want_blue])
	var bank_before := int(state.bank.size())
	var gold0 := int(state.gold)
	m.win_pending = true                           # drive-real-entry-points
	m.step(1.0 / 60.0)                             # step (6) chest, then commit
	if String(m.outcome) != "win" or not bool(m.committed) \
			or int(state.bank.size()) != bank_before + 1:
		probe._fail("chest: outcome=%s committed=%s bank=%d(before %d)" % [
				m.outcome, str(m.committed), state.bank.size(), bank_before])
		return false
	var chest_row: Dictionary = state.bank[state.bank.size() - 1]
	var tier0 := String(ctx["rarity"]["chest_tiers"][0])
	if String(chest_row["rarity"]) != tier0 or int(state.gold) != gold0:
		probe._fail("chest row wrong: %s gold=%d(before %d)" % [
				str(chest_row["rarity"]), state.gold, gold0])
		return false
	gear.refresh()                                 # the bank after the return
	if gear.shown_rows() != state.bank.size():
		probe._fail("gear bank stale after the chest commit: %d != %d" % [
				gear.shown_rows(), state.bank.size()])
		return false
	print(("HUB-PROBE-CHEST bank_before=%d bank_after=%d gold_untouched=1 "
			+ "rarity=%s shown=%d") % [bank_before, int(state.bank.size()),
			tier0, gear.shown_rows()])
	return true
