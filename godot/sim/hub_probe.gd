# hygiene: W9 hub probe — deterministic station harness (test asset,
# kept whole; MC 11274.1.16) — hard ceiling exempt per header rule.
# hub_probe — headless hub/station probe (W9, MC 11274.1.16 / card 11323).
# Test asset in sim/ per the harness idiom (no sim_ prefix; the purity +
# parse scans skip it — boot_probe/save_probe/mission_smoke precedents).
# Boots the REAL graph (GWCompose.build_graph, F2-5) under `-s`, seeds
# meta through the shipped C13 mutators only (set_deck/add_gold/
# add_material/bank_add), then drives every station leg THROUGH THE
# SHIPPED ENTRY POINTS (E5: panels/hub get setup() called directly — a
# Button press fires the very same methods):
#   EQUIP    gear panel pick->slot: bank->equipped; a replaced row
#            returns to the bank INSIDE equip (F2-11, asserted twice —
#            the swap and the re-equip); a relic row is listed but
#            refused by the shipped equip crossing (F2-12/C11).
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
#            shape) dummy + the xp.json practice XP through the shipped
#            add_hero_xp mutator; dps = absorbed/elapsed (live clock).
#   WAR      the REAL hub.tscn under a RouterSpy: war_table.start calls
#            start_mission("gatefall","hard") (difficulty into the
#            shipped mission routing); Digit3 opens the blacksmith panel.
#   CHEST    the REAL mission.tscn: harness sets win_pending (drive-real-
#            entry-points license), step (6) rolls the FREE victory chest
#            (chest_tiers[0] for normal, BN3) and the row enters the bank
#            INSIDE the same C13 mission-end commit — bank grows by
#            EXACTLY one, gold untouched, the gear panel shows the grown
#            bank after the return.
# Determinism: ONE pinned seed 11274 (mission_smoke idiom). EMPTY stderr
# is the verdict (W4 ruling). E3: every failure path prints its FAIL row
# and early-RETURNS; quit() fires exactly once.
# Machine rows (tests/test_hub.py re-derives every number from the data
# files, never from literals):
#   HUB-PROBE-BOOT bank=<n> gold=<g> mats=<id:n,...>
#   HUB-PROBE-EQUIP bank_after_first=<n> bank_after_swap=<n> returned=<uid>
#                   equipped=<base_id> relic_refused=1 bank_after_relic=<n>
#   HUB-PROBE-UPGRADE cost=<g> mats_dropped=<id:n,...> upgraded=1 rarity=<r> gold_left=<g>
#   HUB-PROBE-EVOLVE from=<r> to=<r> cost=<g> refused=1 gold_left=<g>
#   HUB-PROBE-REROLL cost=<g> stats_changed=1 mods_kept=<n> rarity=<r> gold_left=<g>
#   HUB-PROBE-TINKERCAP refused=1 gold_unchanged=1 mods_unchanged=1
#   HUB-PROBE-TINKER moved=1 cost=<g> mats_dropped=<id:n,...> source_mods=<n> target_mods=<n> gold_left=<g>
#   HUB-PROBE-DUMMY xp=<n> level=<l> absorbed=<f> dps=<f> invulnerable=1
#   HUB-PROBE-WAR maps=gatefall:[<diffs>,] start=gatefall difficulty=hard
#   HUB-PROBE-PANELS open=blacksmith
#   HUB-PROBE-CHEST bank_before=<n> bank_after=<n> gold_untouched=1 rarity=<r> shown=<n>
#   HUB-PROBE-OK
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const GEAR_PANEL := preload("res://scripts/gear_panel_ui.gd")
const BLACKSMITH_UI := preload("res://scripts/blacksmith_ui.gd")
const TINKERER_UI := preload("res://scripts/tinkerer_ui.gd")
const DUMMY_RANGE := preload("res://scripts/dummy_range.gd")

const HUB_SCENE := "res://scenes/hub.tscn"
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye"]

# The scripted C9 seed rows (uids are stamped by the bank_add mutator).
# ITEM_B carries ONE mod = its base's first declared mods_pool entry at
# that mod's declared mods.json rarity_min — the "one modded" item and
# the tinkering source. The relic row is the F2-12 listing/refusal leg.
const ITEM_A := {"base_id": "oaken_cleaver", "rarity": "worn", "ilvl": 5}
const ITEM_B := {"base_id": "twin_fang", "rarity": "powerful", "ilvl": 12,
	"mod": true}
const RELIC_SPEC := {"base_id": "mark_of_fervor", "rarity": "powerful",
	"ilvl": 3}
const CAP_SPEC := {"base_id": "iron_hauberk", "rarity": "worn", "ilvl": 10}
const FREE_SPEC := {"base_id": "embercaller_focus", "rarity": "powerful",
	"ilvl": 14}


# Records the pinned war_table crossing start_mission(map_id, difficulty)
# exactly as the main.gd router would receive it (hub.get_parent() at
# runtime IS the main root — same call shape asserted here).
class RouterSpy:
	extends Node

	var calls: Array = []

	func start_mission(map_id: String, difficulty: String) -> void:
		calls.append({"map": map_id, "difficulty": difficulty})


var tables = null
var state = null
var save = null
var bridge = null
var rng = null
var ctx: Dictionary = {}        # the {stem: data} dict the sim statics read


func _init() -> void:
	tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)   # F2-5 wiring
	state = graph["state"]
	save = graph["save"]
	bridge = graph["bridge"]
	rng = RandomNumberGenerator.new()
	rng.seed = 11274                                  # pinned: deterministic
	ctx = {"blacksmith": tables.table("blacksmith"),
		"rarity": tables.table("rarity"), "items": _rows("items")}
	var bs: Dictionary = ctx["blacksmith"]
	var ladder: Array = ctx["rarity"]["ladder"]

	# ---- seeded meta through the shipped C13 mutators ONLY. Gold covers
	# the whole service chain EXACTLY plus a structural +1, so the final
	# gold_left rows carry the whole-chain exact-drop proof. ----
	state.set_deck(DECK.duplicate())
	var upgrade_cost := int(bs["upgrade"]["gold_by_rarity"][String(ITEM_A["rarity"])])
	var evolve_cost := int(bs["evolve"]["gold"])
	var reroll_cost := int(bs["reroll"]["gold"])
	var tinker_cost := int(bs["tinkering"]["gold"])
	var gold_total := upgrade_cost + evolve_cost + reroll_cost + tinker_cost + 1
	state.add_gold(gold_total)
	var want: Dictionary = {}
	for cost: Dictionary in [bs["upgrade"]["materials"],
			bs["evolve"]["materials"], bs["tinkering"]["materials"]]:
		for id: String in cost:
			want[id] = int(want.get(id, 0)) + int(cost[id])
	for id: String in want:
		state.add_material(id, int(want[id]) * 2)
	state.bank_add(_scripted_item(ITEM_A))
	state.bank_add(_scripted_item(ITEM_B))
	if int(state.bank.size()) != 2 or int(state.gold) != gold_total:
		_fail("seed: bank=%d gold=%d" % [state.bank.size(), state.gold])
		return
	print("HUB-PROBE-BOOT bank=%d gold=%d mats=%s" % [
			state.bank.size(), state.gold, _mats_text(want)])

	# ---- EQUIP leg: gear panel -> the shipped equip crossing ----
	var gear = GEAR_PANEL.new()
	root.add_child(gear)
	gear.setup(tables, state)
	var uid_a := int(state.bank[0]["uid"])
	var uid_b := int(state.bank[1]["uid"])
	gear.pick(uid_a)
	if not gear.equip_selected("warden", "weapon") \
			or state.bank.size() != 1 or int(state.bank[0]["uid"]) != uid_b:
		_fail("equip first: bank=%s" % str(state.bank))
		return
	var bank_first := int(state.bank.size())
	gear.pick(uid_b)
	if not gear.equip_selected("warden", "weapon") \
			or state.bank.size() != 1:
		_fail("equip swap: bank=%s" % str(state.bank.size()))
		return
	# F2-11: the replaced row A returned INTO the bank inside equip.
	var returned := _bank_index_of(String(ITEM_A["base_id"])) >= 0
	var worn: Dictionary = state.equipped["warden"]["weapon"]
	if not returned or String(worn.get("base_id", "")) != String(ITEM_B["base_id"]):
		_fail("equip swap: returned=%s worn=%s" % [
				str(returned), str(worn.get("base_id", ""))])
		return
	var bank_swap := int(state.bank.size())
	# F2-12/C11: a relic row is listed (it rides the same item_row widget)
	# but hero-slot equip is the shipped refusal — bank untouched.
	state.bank_add(_scripted_item(RELIC_SPEC))
	var relic_row: Dictionary = state.bank[_bank_index_of(String(RELIC_SPEC["base_id"]))]
	gear.pick(int(relic_row["uid"]))
	var relic_ok := gear.equip_selected("warden", "weapon")
	if relic_ok or state.bank.size() != 2:
		_fail("relic equip not refused: ok=%s bank=%d" % [
				str(relic_ok), state.bank.size()])
		return
	print(("HUB-PROBE-EQUIP bank_after_first=%d bank_after_swap=%d returned=%d "
			+ "equipped=%s relic_refused=1 bank_after_relic=%d") % [
			bank_first, bank_swap, uid_a, String(worn["base_id"]),
			int(state.bank.size())])

	# ---- UPGRADE leg: blacksmith panel, exact gold+materials ----
	var smith = BLACKSMITH_UI.new()
	root.add_child(smith)
	smith.setup(tables, state, rng)
	var row_a: Dictionary = state.bank[_bank_index_of(String(ITEM_A["base_id"]))]
	var gold0 := int(state.gold)
	var mats0: Dictionary = state.materials.duplicate(true)
	var res: Dictionary = smith.upgrade(uid_a)
	if not bool(res["ok"]) or int(res["cost"]["gold"]) != upgrade_cost \
			or int(state.gold) != gold0 - upgrade_cost \
			or int(row_a["upgraded"]) != 1 \
			or String(row_a["rarity"]) != String(ITEM_A["rarity"]) \
			or not _mats_dropped(mats0, bs["upgrade"]["materials"]):
		_fail("upgrade: %s gold=%d upgraded=%s" % [
				str(res), state.gold, str(row_a.get("upgraded", -1))])
		return
	print("HUB-PROBE-UPGRADE cost=%d mats_dropped=%s upgraded=1 rarity=%s gold_left=%d" % [
			upgrade_cost, _mats_text(bs["upgrade"]["materials"]),
			String(row_a["rarity"]), int(state.gold)])

	# ---- EVOLVE leg: ONE ladder step (rarity.json), exact cost ----
	gold0 = int(state.gold)
	mats0 = state.materials.duplicate(true)
	res = smith.evolve(uid_a)
	var to_rung := String(ladder[ladder.find(String(ITEM_A["rarity"])) + 1])
	if not bool(res["ok"]) or String(row_a["rarity"]) != to_rung \
			or int(state.gold) != gold0 - evolve_cost \
			or not _mats_dropped(mats0, bs["evolve"]["materials"]):
		_fail("evolve: %s rarity=%s gold=%d" % [str(res), row_a["rarity"], state.gold])
		return
	# Data-derived top gate: a harness-written legendary (drive-real-
	# entry-points license) must be refused with gold untouched.
	row_a["rarity"] = String(ladder[ladder.size() - 1])
	gold0 = int(state.gold)
	res = smith.evolve(uid_a)
	if bool(res["ok"]) or int(state.gold) != gold0:
		_fail("evolve top-rung: %s gold=%d" % [str(res), state.gold])
		return
	print("HUB-PROBE-EVOLVE from=%s to=%s cost=%d refused=1 gold_left=%d" % [
			String(ITEM_A["rarity"]), to_rung, evolve_cost, int(state.gold)])

	# ---- re-EQUIP: wear A (legendary) -> B returns to the bank (F2-11
	#      asserted a second time, and B becomes the reroll/tinker source)
	gear.pick(uid_a)
	if not gear.equip_selected("warden", "weapon") \
			or _bank_index_of(String(ITEM_B["base_id"])) < 0:
		_fail("re-equip: B never returned to the bank")
		return
	var row_b: Dictionary = state.bank[_bank_index_of(String(ITEM_B["base_id"]))]

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
			or String(row_b["rarity"]) != String(ITEM_B["rarity"]) \
			or int(state.gold) != gold0 - reroll_cost \
			or int(res["cost"]["materials"].size()) != 0:
		_fail("reroll: %s changed=%s mods=%d gold=%d" % [
				str(res), str(before != after), row_b["mods"].size(), state.gold])
		return
	print("HUB-PROBE-REROLL cost=%d stats_changed=1 mods_kept=%d rarity=%s gold_left=%d" % [
			reroll_cost, mods_before, String(row_b["rarity"]), int(state.gold)])

	# ---- TINKERCAP leg: worn target = ZERO declared slots -> refused ----
	var tink = TINKERER_UI.new()
	root.add_child(tink)
	tink.setup(tables, state, rng)
	state.bank_add(_scripted_item(CAP_SPEC))
	var cap_row: Dictionary = state.bank[_bank_index_of(String(CAP_SPEC["base_id"]))]
	gold0 = int(state.gold)
	tink.set_source(uid_b)
	tink.set_target(int(cap_row["uid"]))
	tink.select_mod(0)
	res = tink.transfer()
	if bool(res["ok"]) or int(state.gold) != gold0 \
			or int(cap_row["mods"].size()) != 0 \
			or int(row_b["mods"].size()) != mods_before:
		_fail("tinkercap passed (cap bypassed): %s gold=%d" % [str(res), state.gold])
		return
	print("HUB-PROBE-TINKERCAP refused=1 gold_unchanged=1 mods_unchanged=1")

	# ---- TINKER leg: a powerful target has ONE declared free slot ----
	state.bank_add(_scripted_item(FREE_SPEC))
	var tgt_row: Dictionary = state.bank[_bank_index_of(String(FREE_SPEC["base_id"]))]
	gold0 = int(state.gold)
	mats0 = state.materials.duplicate(true)
	tink.set_source(uid_b)
	tink.set_target(int(tgt_row["uid"]))
	tink.select_mod(0)
	res = tink.transfer()
	if not bool(res["ok"]) or int(row_b["mods"].size()) != mods_before - 1 \
			or int(tgt_row["mods"].size()) != 1 \
			or int(state.gold) != gold0 - tinker_cost \
			or not _mats_dropped(mats0, bs["tinkering"]["materials"]):
		_fail("tinker: %s src=%d tgt=%d gold=%d" % [str(res),
				row_b["mods"].size(), tgt_row["mods"].size(), state.gold])
		return
	print(("HUB-PROBE-TINKER moved=1 cost=%d mats_dropped=%s source_mods=%d "
			+ "target_mods=%d gold_left=%d") % [
			tinker_cost, _mats_text(bs["tinkering"]["materials"]),
			int(row_b["mods"].size()), int(tgt_row["mods"].size()),
			int(state.gold)])

	# ---- DUMMY leg: hero_hit damage + declared practice XP ----
	var dummy_panel = DUMMY_RANGE.new()
	root.add_child(dummy_panel)
	dummy_panel.setup(tables, state, rng)
	var xp_declared := int(tables.table("xp")["enemy_xp_base"]["normal"])
	var hero0 := String(DECK[0])
	gold0 = int(state.gold)
	res = dummy_panel.strike(hero0)
	if not bool(res.get("ok", false)) or int(res["xp"]) != xp_declared \
			or int(state.heroes[hero0]["xp"]) != xp_declared \
			or int(state.gold) != gold0:
		_fail("dummy xp: %s state=%s gold=%d" % [str(res), str(state.heroes), state.gold])
		return
	# Invulnerable BY SHAPE: the dummy record has no hp key, so no damage
	# path can lower one — the leg asserts the shape, not a magic number.
	if dummy_panel.dummy.has("hp"):
		_fail("dummy carries an hp key: %s" % str(dummy_panel.dummy))
		return
	for _t: int in 60:
		dummy_panel.tick(1.0 / 60.0)               # one live second of clock
	var d_absorbed := float(dummy_panel.dummy["absorbed"])
	if d_absorbed <= 0.0 or absf(dummy_panel.dps() - d_absorbed) > 1e-9:
		_fail("dummy dps: absorbed=%s dps=%s" % [str(d_absorbed), str(dummy_panel.dps())])
		return
	print("HUB-PROBE-DUMMY xp=%d level=%d absorbed=%.2f dps=%.2f invulnerable=1" % [
			xp_declared, int(state.heroes[hero0]["level"]), d_absorbed,
			dummy_panel.dps()])

	# ---- WAR + PANELS legs: the REAL hub scene ----
	var spy = RouterSpy.new()
	spy.name = "RouterSpy"
	root.add_child(spy)
	var packed = ResourceLoader.load(HUB_SCENE)
	if packed == null:
		_fail("hub.tscn not loadable")
		return
	var hub = packed.instantiate()
	spy.add_child(hub)
	hub._ready()                                   # E5: drive _ready (no-op)
	hub.setup(tables, state, save, bridge, rng)
	if hub.war.maps.is_empty() or String(hub.war.maps[0]["id"]) != "gatefall" \
			or not (hub.war.maps[0]["difficulties"] as Array).has("hard"):
		_fail("war table map data wrong: %s" % str(hub.war.maps))
		return
	hub.war.start("gatefall", "hard")
	if spy.calls.size() != 1 or String(spy.calls[0]["map"]) != "gatefall" \
			or String(spy.calls[0]["difficulty"]) != "hard":
		_fail("war start crossing: %s" % str(spy.calls))
		return
	var diffs := ""
	for d: Variant in hub.war.maps[0]["difficulties"]:
		diffs += String(d) + ","
	print("HUB-PROBE-WAR maps=gatefall:[%s] start=gatefall difficulty=hard" % diffs)
	hub.handle_press("Digit3")                     # greybox station code
	if not bool(hub.blacksmith.visible) or bool(hub.gear.visible):
		_fail("station routing: blacksmith=%s gear=%s" % [
				str(hub.blacksmith.visible), str(hub.gear.visible)])
		return
	print("HUB-PROBE-PANELS open=blacksmith")

	# ---- CHEST leg: the mission-end commit carries the bank +1 ----
	var mpacked = ResourceLoader.load(MISSION_SCENE)
	if mpacked == null:
		_fail("mission.tscn not loadable")
		return
	var m = mpacked.instantiate()
	root.add_child(m)
	m._ready()
	var m_rng := RandomNumberGenerator.new()
	m_rng.seed = 11274
	m.setup(tables, state, save, bridge, "gatefall", "normal", m_rng)
	var bank_before := int(state.bank.size())
	gold0 = int(state.gold)
	m.win_pending = true                           # drive-real-entry-points
	m.step(1.0 / 60.0)                             # step (6) chest, then commit
	if String(m.outcome) != "win" or not bool(m.committed) \
			or int(state.bank.size()) != bank_before + 1:
		_fail("chest: outcome=%s committed=%s bank=%d(before %d)" % [
				m.outcome, str(m.committed), state.bank.size(), bank_before])
		return
	var chest_row: Dictionary = state.bank[state.bank.size() - 1]
	var tier0 := String(ctx["rarity"]["chest_tiers"][0])
	if String(chest_row["rarity"]) != tier0 or int(state.gold) != gold0:
		_fail("chest row wrong: %s gold=%d(before %d)" % [
				str(chest_row["rarity"]), state.gold, gold0])
		return
	gear.refresh()                                 # the bank after the return
	if gear.shown_rows() != state.bank.size():
		_fail("gear bank stale after the chest commit: %d != %d" % [
				gear.shown_rows(), state.bank.size()])
		return
	print(("HUB-PROBE-CHEST bank_before=%d bank_after=%d gold_untouched=1 "
			+ "rarity=%s shown=%d") % [bank_before, int(state.bank.size()),
			tier0, gear.shown_rows()])

	print("HUB-PROBE-OK")
	quit(0)
	return


# ---------- helpers ----------

func _fail(why: String) -> void:
	print("HUB-PROBE FAIL " + why)
	quit(1)


# C9 row built from DECLARED items.json base data (the SimLoot base-row
# reading). spec["mod"] (ITEM_B only) attaches the base's first declared
# mods_pool entry at its declared mods.json rarity_min.
func _scripted_item(spec: Dictionary) -> Dictionary:
	var base: Dictionary = {}
	for row: Dictionary in ctx["items"]:
		if String(row.get("id", "")) == String(spec["base_id"]):
			base = row
	if base.is_empty():
		_fail("no items.json base %s" % String(spec.get("base_id", "")))
	var mods: Array = []
	if bool(spec.get("mod", false)):
		var mod_id := String(base["mods_pool"][0])
		mods.append({"mod_id": mod_id, "rarity": _mod_rarity(mod_id)})
	return {
		"uid": 0,
		"base_id": String(base["id"]),
		"slot": String(base["slot"]),
		"rarity": String(spec["rarity"]),
		"ilvl": int(spec["ilvl"]),
		"primary": {"stat": String(base["primary"]), "value": float(spec["ilvl"])},
		"secondary": null,
		"atk_speed": float(base["roll_ranges"]["atk_speed"][0]),
		"shot_type": (String(base["shot_types"][0])
				if int(base["shot_types"].size()) > 0 else null),
		"proj_count": int(base["roll_ranges"]["proj_count"][0]),
		"mods": mods,
		"upgraded": 0,
	}


func _mod_rarity(mod_id: String) -> String:
	for mod_row: Dictionary in _rows("mods"):
		if String(mod_row.get("id", "")) == mod_id:
			return String(mod_row.get("rarity_min", ""))
	return ""


func _rows(stem: String) -> Array:
	var parsed: Variant = JSON.parse_string(
			FileAccess.get_file_as_string("res://data/" + stem + ".json"))
	return parsed if parsed is Array else []


func _bank_index_of(base_id: String) -> int:
	for i: int in state.bank.size():
		if String(state.bank[i]["base_id"]) == base_id:
			return i
	return -1


# Every seeded material id dropped EXACTLY its declared cost, nothing
# else moved (the exact-drop proof behind the mats_dropped rows).
func _mats_dropped(before: Dictionary, cost: Dictionary) -> bool:
	for id: String in before:
		var delta := int(before[id]) - int(state.materials.get(id, 0))
		if delta != int(cost.get(id, 0)):
			return false
	return true


func _mats_text(cost: Dictionary) -> String:
	var out := ""
	for id: String in cost:
		out += "%s:%d," % [id, int(cost[id])]
	return out
