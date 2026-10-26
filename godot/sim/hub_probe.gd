# hub_probe — headless hub/station probe (W9, MC 11274.1.16 / card 11323;
# W16 split MC 11274.1.28 / card 11384). Test asset in sim/ per the
# harness idiom (no sim_ prefix; the purity + parse scans skip it —
# boot_probe/save_probe/mission_smoke precedents). W16: one file per
# leg-group — this driver (graph + seeded meta + BOOT + the shared
# helpers) + _equip.gd, _services.gd, _stations.gd, _mission.gd. Pure
# move: printed rows unchanged, one byte. Boots the REAL graph
# (GWCompose.build_graph, F2-5) under `-s`, seeds meta through the
# shipped C13 mutators only (set_deck/add_gold/add_material/bank_add),
# then drives every station leg THROUGH THE SHIPPED ENTRY POINTS (E5:
# panels/hub get setup() called directly — a Button press fires the very
# same methods): EQUIP gear pick->slot with F2-11 return + F2-12/C11
# relic refusal + P2-10 unknown-uid refusal; UPGRADE/EVOLVE/REROLL/
# TINKERCAP/TINKER blacksmith+tinkerer exact gold+materials; DUMMY the
# xp-closed DPS faucet; WAR/PANELS/ASC the REAL hub.tscn under a
# RouterSpy; RELIC the pinned C11 crossing + save round-trip; CHEST the
# FREE victory chest through the REAL mission.tscn step (6) + commit.
# Determinism: ONE pinned seed 11274 (mission_smoke idiom). EMPTY stderr
# is the verdict (W4 ruling). E3: every failure path prints its FAIL row
# and early-RETURNS; quit() fires exactly once (the driver's).
# Machine rows, in print order (tests/test_hub.py re-derives every
# number from the data files, never from literals; per-row detail lives
# with the leg that prints it):
#   BOOT | EQUIP | UPGRADE EVOLVE REROLL TINKERCAP TINKER DUMMY |
#   WAR PANELS ASC | RELIC CHEST | OK
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const HUB_PROBE_EQUIP := preload("res://sim/hub_probe_equip.gd")
const HUB_PROBE_SERVICES := preload("res://sim/hub_probe_services.gd")
const HUB_PROBE_STATIONS := preload("res://sim/hub_probe_stations.gd")
const HUB_PROBE_MISSION := preload("res://sim/hub_probe_mission.gd")

const DECK := ["warden", "deadeye", "embercaller"]

# The scripted C9 seed rows (uids are stamped by the bank_add mutator).
# ITEM_B carries ONE mod = its base's first declared mods_pool entry at
# that mod's declared mods.json rarity_min — the "one modded" item and
# the tinkering source. The relic row is the F2-12 listing/refusal leg.
const ITEM_A := {"base_id": "oaken_cleaver", "rarity": "worn", "ilvl": 5}
const ITEM_B := {"base_id": "twin_fang", "rarity": "powerful", "ilvl": 12,
	"mod": true}
const RELIC_SPEC := {"base_id": "mark_of_fervor", "rarity": "powerful",
	"ilvl": 3}
const RELIC2_SPEC := {"base_id": "orb_of_the_deep", "rarity": "powerful",
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
		"rarity": tables.table("rarity"), "items": tables.rows("items")}
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

	# Shared leg state (the W16 split's ONE home for cross-leg values).
	var leg := {"bs": bs, "ladder": ladder,
		"item_a": ITEM_A, "item_b": ITEM_B, "relic_spec": RELIC_SPEC,
		"relic2_spec": RELIC2_SPEC, "cap_spec": CAP_SPEC,
		"free_spec": FREE_SPEC, "deck": DECK, "hero0": String(DECK[0]),
		"upgrade_cost": upgrade_cost, "evolve_cost": evolve_cost,
		"reroll_cost": reroll_cost, "tinker_cost": tinker_cost}
	if not HUB_PROBE_EQUIP.run(self, leg):
		return
	if not HUB_PROBE_SERVICES.run(self, leg):
		return
	if not HUB_PROBE_STATIONS.run(self, leg):
		return
	if not HUB_PROBE_MISSION.run(self, leg):
		return

	print("HUB-PROBE-OK")
	quit(0)
	return


# ---------- helpers (shared by the leg files through the probe) ----------

func _probe_defense(m, uid: int):
	for rec: Dictionary in m.defense_list:
		if int(rec["uid"]) == uid:
			return rec["obj"]
	_fail("no defense uid %d" % uid)
	return null


func _asc_power(power: String) -> Dictionary:
	for branch: Variant in tables.table("ascension")["tree"].values():
		for row: Dictionary in branch:
			if String(row["id"]) == power:
				return row
	_fail("no ascension power %s" % power)
	return {}


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
	for mod_row: Dictionary in tables.rows("mods"):
		if String(mod_row.get("id", "")) == mod_id:
			return String(mod_row.get("rarity_min", ""))
	return ""


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
