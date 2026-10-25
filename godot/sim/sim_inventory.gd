class_name SimInventory
extends RefCounted

# The one cross-sim dependency binds via preload, NOT the class_name: the
# global class cache is an editor-scan artifact that `-s` runs do not
# guarantee (VERIFIED this gate: a fresh `--import`-only cache leaves the
# class_name unresolvable and the load fails at parse). preload binds at
# compile time and keeps every `-s` leg cache-independent.
const SIM_LOOT := preload("res://sim/sim_loot.gd")

# Bank/equip + blacksmith/tinkerer services + relic math (Modules row
# sim_inventory). EVERY cost is read from blacksmith.json through tables
# (F2-6 sole source; I2): gold_by_rarity for upgrade, flat gold + materials
# for evolve/tinkering, gold-only for reroll (the pinned reroll shape).
# Services return {ok, cost:{gold:int, materials:{id:int}}}; the caller pays
# through the GameState mutators (consume_material / gold, F2-6) — mats here
# is the CURRENT material counts, checked for affordability (F2-6).
# The only randomness is svc_reroll, which draws through the injected rng
# parameter via SimLoot's sanctioned receiver-qualified path (C12/F2-1/F2-2).
#
# Readings recorded on the card trail:
# - equip() is the F2-11 contract, not UI: it returns {ok, bank}; the
#   returned bank is the passed array MINUS only the row worn onto the hero,
#   so every other row the caller merged in — the replaced item is merged in
#   by GWGameState.equip per C9 — returns inside this same call. Replace-to-
#   bank thus lives in equip's contract; no caller may reimplement it.
# - Relic rows are tower gear, not hero-worn (C11 copies them from the bank
#   into the mission relic pool): slot "relic" equips with ok:false.
# - svc_evolve walks the item one ladder step up (DD2 Evolving): the top-rung
#   gate is data-derived (ladder index vs ladder size), no name list here.
# - svc_reroll rerolls the item's secondary stat + weapon extras (DD2 stat
#   reroll row) IN PLACE — item is the caller-owned reference Dict already
#   held in the bank; primary, mods, ilvl and upgraded survive unchanged.
# - tinkering moves source.mods[mod_i] onto the target when the target has a
#   free declared mod slot and the cost is affordable; on ok the transfer
#   happens in place on both caller-owned rows.


# F2-11/C9 equip crossing: {ok, bank}; see the header for the replace
# contract. A worn row leaves the bank; everything else in the array —
# including the merged-in replaced row — returns with it.
static func equip(bank: Array, hero: String, item: Dictionary) -> Dictionary:
	if hero.is_empty() or String(item.get("slot", "")) not in ["weapon", "armor", "ring"]:
		return {"ok": false, "bank": bank}
	var kept: Array = bank.duplicate()
	var uid := int(item.get("uid", 0))
	var index := -1
	for i: int in kept.size():
		var row: Dictionary = kept[i]
		if uid > 0:
			if int(row.get("uid", 0)) == uid:
				index = i
				break
		elif row == item:
			index = i
			break
	if index >= 0:
		kept.remove_at(index)
	return {"ok": true, "bank": kept}


# Blacksmith Upgrade: gold ladder by the item's declared rarity + the flat
# service materials (blacksmith.json); ok = materials affordable (gold is
# paid at the mutator site, its pool never enters this signature, I3); the
# upgrade level itself is applied by the caller on ok.
static func svc_upgrade(item: Dictionary, tables, mats: Dictionary) -> Dictionary:
	var svc: Dictionary = tables["blacksmith"]["upgrade"]
	var cost := {
		"gold": int(svc["gold_by_rarity"][String(item["rarity"])]),
		"materials": Dictionary(svc["materials"]),
	}
	return {"ok": _can_pay(cost, mats), "cost": cost}


# Blacksmith Evolve (same pinned shape): one ladder step up costs flat gold +
# materials; the ladder top cannot evolve (gate derived from the data).
static func svc_evolve(item: Dictionary, tables, mats: Dictionary) -> Dictionary:
	var svc: Dictionary = tables["blacksmith"]["evolve"]
	var cost := {
		"gold": int(svc["gold"]),
		"materials": Dictionary(svc["materials"]),
	}
	var ladder: Array = tables["rarity"]["ladder"]
	var rung := ladder.find(String(item["rarity"]))
	var ok := rung >= 0 and rung < ladder.size() - 1
	return {"ok": ok and _can_pay(cost, mats), "cost": cost}


# Blacksmith Reroll (gold-only cost, the pinned reroll shape): re-rolls the
# item's secondary stat + weapon extras in place through SimLoot's single
# roll mechanism; ok:true — the gold is paid at the mutator (no gold pool
# enters this signature, I3).
static func svc_reroll(item, rng, tables) -> Dictionary:
	var rolled: Dictionary = SIM_LOOT.roll_item(_base_row(tables, String(item["base_id"])), String(item["rarity"]), tables, rng)
	item["secondary"] = rolled["secondary"]
	item["atk_speed"] = rolled["atk_speed"]
	item["shot_type"] = rolled["shot_type"]
	item["proj_count"] = rolled["proj_count"]
	var svc: Dictionary = tables["blacksmith"]["reroll"]
	var cost := {"gold": int(svc["gold"]), "materials": {}}
	return {"ok": true, "cost": cost}


# Tinkerer mod transfer: the source's mods[mod_i] moves onto the target
# when the index is real, the target has a free declared slot, and the
# service cost is affordable. On ok both rows are updated in place.
static func tinkering(source, target, mod_i, tables, mats) -> Dictionary:
	var svc: Dictionary = tables["blacksmith"]["tinkering"]
	var cost := {
		"gold": int(svc["gold"]),
		"materials": Dictionary(svc["materials"]),
	}
	var mods: Array = source["mods"]
	if mod_i < 0 or mod_i >= mods.size():
		return {"ok": false, "cost": cost}
	var free := mod_slots(String(target["rarity"]), tables["rarity"]["mod_slots"]) \
		- int(target["mods"].size())
	if free <= 0 or not _can_pay(cost, mats):
		return {"ok": false, "cost": cost}
	target["mods"].append(mods.pop_at(mod_i))
	return {"ok": true, "cost": cost}


# Declared mod-slot count for a rarity (rarity.json mod_slots map arrives as
# `ladder` — the pinned parameter name for that data map).
static func mod_slots(rarity: String, ladder: Dictionary) -> int:
	return int(ladder.get(rarity, 0))


# C11 relic bonus over a defense tier row: stat -> total add across the
# relic's rolled primary + secondary legs (mods ride their own data path in
# defense_obj, C9 mods rows carry no values).
static func relic_bonuses(item: Dictionary) -> Dictionary:
	var bonuses: Dictionary = {}
	var legs: Array = [item["primary"]]
	if item["secondary"] != null:
		legs.append(item["secondary"])
	for leg: Dictionary in legs:
		var stat := String(leg["stat"])
		bonuses[stat] = float(bonuses.get(stat, 0.0)) + float(leg["value"])
	return bonuses


# Material affordability for a {gold, materials} cost (gold is paid at the
# mutator site, never checked from here — I3 pool split).
static func _can_pay(cost: Dictionary, mats: Dictionary) -> bool:
	var required: Dictionary = cost["materials"]
	for id: String in required:
		if int(mats.get(id, 0)) < int(required[id]):
			return false
	return true


# Declared base row behind an item instance (items.json by base_id).
static func _base_row(tables, base_id: String) -> Dictionary:
	for base: Dictionary in tables["items"]:
		if String(base.get("id", "")) == base_id:
			return base
	return {}
