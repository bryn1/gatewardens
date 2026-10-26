# hub_probe_services — the blacksmith/tinkerer/dummy legs of the hub
# probe (W16 split of hub_probe.gd, MC 11274.1.28 / card 11384; legs
# authored W9 + W14, MC 11274.1.16/.25). Pure move — code and rows
# byte-identical.
#   UPGRADE  blacksmith svc_upgrade: gold+materials drop EXACTLY the
#            blacksmith.json values; rarity unchanged (upgrade != step).
#   EVOLVE   svc_evolve: ONE rarity ladder step per rarity.json, exact
#            evolve cost; a top-rung item is REFUSED gold-unchanged (the
#            data-derived gate; harness legendary write = boot_probe
#            drive-real-entry-points license).
#   REROLL   svc_reroll through the panel's rng param: stats change, the
#            rolled mod survives (slot count kept), gold-only cost.
#   TINKERCAP a worn target declares ZERO mod slots (rarity.json): the
#            shipped tinkering REFUSES — mods and gold untouched.
#   TINKER   the transfer leg: the mod moves source->target, exact
#            gold+materials, once.
#   DUMMY    SimCombat.hero_hit damage onto an hp-LESS (unkillable by
#            shape) dummy; dps = absorbed/elapsed (live clock). W14
#            P3-11: the practice-XP faucet is CLOSED — a strike pays
#            ZERO xp and touches meta NEVER.
# Machine rows: UPGRADE EVOLVE REROLL TINKERCAP TINKER DUMMY (re-
# derived by tests/test_hub.py from blacksmith/rarity/xp.json).
extends RefCounted

const BLACKSMITH_UI := preload("res://scripts/blacksmith_ui.gd")
const TINKERER_UI := preload("res://scripts/tinkerer_ui.gd")
const DUMMY_RANGE := preload("res://scripts/dummy_range.gd")


static func run(probe, leg: Dictionary) -> bool:
	var state = probe.state
	var root = probe.root
	var bs: Dictionary = leg["bs"]
	var ladder: Array = leg["ladder"]
	var item_a: Dictionary = leg["item_a"]
	var item_b: Dictionary = leg["item_b"]
	var gear = leg["gear"]
	var uid_a: int = int(leg["uid_a"])
	var uid_b: int = int(leg["uid_b"])
	var upgrade_cost: int = int(leg["upgrade_cost"])
	var evolve_cost: int = int(leg["evolve_cost"])
	var reroll_cost: int = int(leg["reroll_cost"])
	var tinker_cost: int = int(leg["tinker_cost"])

	# ---- UPGRADE leg: blacksmith panel, exact gold+materials ----
	var smith = BLACKSMITH_UI.new()
	root.add_child(smith)
	smith.setup(probe.tables, state, probe.rng)
	var row_a: Dictionary = state.bank[probe._bank_index_of(String(item_a["base_id"]))]
	var gold0 := int(state.gold)
	var mats0: Dictionary = state.materials.duplicate(true)
	var res: Dictionary = smith.upgrade(uid_a)
	if not bool(res["ok"]) or int(res["cost"]["gold"]) != upgrade_cost \
			or int(state.gold) != gold0 - upgrade_cost \
			or int(row_a["upgraded"]) != 1 \
			or String(row_a["rarity"]) != String(item_a["rarity"]) \
			or not probe._mats_dropped(mats0, bs["upgrade"]["materials"]):
		probe._fail("upgrade: %s gold=%d upgraded=%s" % [
				str(res), state.gold, str(row_a.get("upgraded", -1))])
		return false
	print("HUB-PROBE-UPGRADE cost=%d mats_dropped=%s upgraded=1 rarity=%s gold_left=%d" % [
			upgrade_cost, probe._mats_text(bs["upgrade"]["materials"]),
			String(row_a["rarity"]), int(state.gold)])

	# ---- EVOLVE leg: ONE ladder step (rarity.json), exact cost ----
	gold0 = int(state.gold)
	mats0 = state.materials.duplicate(true)
	res = smith.evolve(uid_a)
	var to_rung := String(ladder[ladder.find(String(item_a["rarity"])) + 1])
	if not bool(res["ok"]) or String(row_a["rarity"]) != to_rung \
			or int(state.gold) != gold0 - evolve_cost \
			or not probe._mats_dropped(mats0, bs["evolve"]["materials"]):
		probe._fail("evolve: %s rarity=%s gold=%d" % [str(res), row_a["rarity"], state.gold])
		return false
	# Data-derived top gate: a harness-written legendary (drive-real-
	# entry-points license) must be refused with gold untouched.
	row_a["rarity"] = String(ladder[ladder.size() - 1])
	gold0 = int(state.gold)
	res = smith.evolve(uid_a)
	if bool(res["ok"]) or int(state.gold) != gold0:
		probe._fail("evolve top-rung: %s gold=%d" % [str(res), state.gold])
		return false
	print("HUB-PROBE-EVOLVE from=%s to=%s cost=%d refused=1 gold_left=%d" % [
			String(item_a["rarity"]), to_rung, evolve_cost, int(state.gold)])

	# ---- re-EQUIP: wear A (legendary) -> B returns to the bank (F2-11
	#      asserted a second time, and B becomes the reroll/tinker source)
	gear.pick(uid_a)
	if not gear.equip_selected("warden", "weapon") \
			or probe._bank_index_of(String(item_b["base_id"])) < 0:
		probe._fail("re-equip: B never returned to the bank")
		return false
	var row_b: Dictionary = state.bank[probe._bank_index_of(String(item_b["base_id"]))]

	# ---- REROLL leg: stats change, slot count kept, gold-only ----
	var before := str(row_b["secondary"]) + str(row_b["atk_speed"]) \
			+ str(row_b["shot_type"]) + str(row_b["proj_count"])
	var mods_before := int(row_b["mods"].size())
	gold0 = int(state.gold)
	res = smith.reroll(uid_b)
	var after := str(row_b["secondary"]) + str(row_b["atk_speed"]) \
			+ str(row_b["shot_type"]) + str(row_b["proj_count"])
	if not bool(res["ok"]) or before == after \
			or int(row_b["mods"].size()) != mods_before \
			or String(row_b["rarity"]) != String(item_b["rarity"]) \
			or int(state.gold) != gold0 - reroll_cost \
			or int(res["cost"]["materials"].size()) != 0:
		probe._fail("reroll: %s changed=%s mods=%d gold=%d" % [
				str(res), str(before != after), row_b["mods"].size(), state.gold])
		return false
	print("HUB-PROBE-REROLL cost=%d stats_changed=1 mods_kept=%d rarity=%s gold_left=%d" % [
			reroll_cost, mods_before, String(row_b["rarity"]), int(state.gold)])

	# ---- TINKERCAP leg: worn target = ZERO declared slots -> refused ----
	var tink = TINKERER_UI.new()
	root.add_child(tink)
	tink.setup(probe.tables, state, probe.rng)
	state.bank_add(probe._scripted_item(leg["cap_spec"]))
	var cap_row: Dictionary = state.bank[probe._bank_index_of(String(leg["cap_spec"]["base_id"]))]
	gold0 = int(state.gold)
	tink.set_source(uid_b)
	tink.set_target(int(cap_row["uid"]))
	tink.select_mod(0)
	res = tink.transfer()
	if bool(res["ok"]) or int(state.gold) != gold0 \
			or int(cap_row["mods"].size()) != 0 \
			or int(row_b["mods"].size()) != mods_before:
		probe._fail("tinkercap passed (cap bypassed): %s gold=%d" % [str(res), state.gold])
		return false
	print("HUB-PROBE-TINKERCAP refused=1 gold_unchanged=1 mods_unchanged=1")

	# ---- TINKER leg: a powerful target has ONE declared free slot ----
	state.bank_add(probe._scripted_item(leg["free_spec"]))
	var tgt_row: Dictionary = state.bank[probe._bank_index_of(String(leg["free_spec"]["base_id"]))]
	gold0 = int(state.gold)
	mats0 = state.materials.duplicate(true)
	tink.set_source(uid_b)
	tink.set_target(int(tgt_row["uid"]))
	tink.select_mod(0)
	res = tink.transfer()
	if not bool(res["ok"]) or int(row_b["mods"].size()) != mods_before - 1 \
			or int(tgt_row["mods"].size()) != 1 \
			or int(state.gold) != gold0 - tinker_cost \
			or not probe._mats_dropped(mats0, bs["tinkering"]["materials"]):
		probe._fail("tinker: %s src=%d tgt=%d gold=%d" % [str(res),
				row_b["mods"].size(), tgt_row["mods"].size(), state.gold])
		return false
	print(("HUB-PROBE-TINKER moved=1 cost=%d mats_dropped=%s source_mods=%d "
			+ "target_mods=%d gold_left=%d") % [
			tinker_cost, probe._mats_text(bs["tinkering"]["materials"]),
			int(row_b["mods"].size()), int(tgt_row["mods"].size()),
			int(state.gold)])

	# ---- DUMMY leg: hero_hit damage + the LIVE DPS readout. W14 P3-11
	#      (MC 11274.1.25): the practice-XP faucet is CLOSED — a strike
	#      pays ZERO xp and touches meta NEVER (heroes table and gold do
	#      not move: the faucet crossed add_hero_xp, a mutated emitter).
	#      Declared reading: A6 names the dummies as the DPS test only;
	#      no data file declares a practice-XP bound, so the zero-XP
	#      closure is the single-site honest fix (the bound would need a
	#      literal the I2 law forbids). ----
	var dummy_panel = DUMMY_RANGE.new()
	root.add_child(dummy_panel)
	dummy_panel.setup(probe.tables, state, probe.rng)
	var hero0: String = String(leg["hero0"])
	gold0 = int(state.gold)
	var heroes_before := JSON.stringify(state.heroes)
	res = dummy_panel.strike(hero0)
	if not bool(res.get("ok", false)) or res.has("xp") \
			or float(res["damage"]) <= 0.0 \
			or int(state.gold) != gold0 \
			or JSON.stringify(state.heroes) != heroes_before:
		probe._fail("dummy paid xp or wrote meta: %s heroes=%s gold=%d" % [
				str(res), str(state.heroes), state.gold])
		return false
	# Invulnerable BY SHAPE: the dummy record has no hp key, so no damage
	# path can lower one — the leg asserts the shape, not a magic number.
	if dummy_panel.dummy.has("hp"):
		probe._fail("dummy carries an hp key: %s" % str(dummy_panel.dummy))
		return false
	for _t: int in 60:
		dummy_panel.tick(1.0 / 60.0)               # one live second of clock
	var d_absorbed := float(dummy_panel.dummy["absorbed"])
	if d_absorbed <= 0.0 or absf(dummy_panel.dps() - d_absorbed) > 1e-9:
		probe._fail("dummy dps: absorbed=%s dps=%s" % [str(d_absorbed), str(dummy_panel.dps())])
		return false
	print("HUB-PROBE-DUMMY xp_paid=0 meta_untouched=1 absorbed=%.2f dps=%.2f invulnerable=1" % [
			d_absorbed, dummy_panel.dps()])
	return true
