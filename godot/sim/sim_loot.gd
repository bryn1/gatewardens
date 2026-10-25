class_name SimLoot
extends RefCounted

# Drop + chest rolls (Modules row sim_loot): declared weights only. The
# rarity ladder, drop weights, chest tiers, base pools, roll ranges and mod
# pools all arrive from the tables (rarity.json / items.json / mods.json via
# GWTables) — no rarity names and no weight numbers exist in this file
# (pinned by tests/test_loot_structure.py, I2). Every random draw flows
# through the injected rng parameter as receiver-qualified rng.randf() /
# rng.randi() ONLY (C12/F2-1); there is no other randomness here.
#
# Output shape (the I1 defense — the schema IS the guard): rolled item rows
# carry EXACTLY the C9 keys; drop rows carry {kind,item} / {kind,id} only.
# No paid/clock/timer field exists in any rolled dict because none exists
# in the pinned schema.
#
# Readings recorded on the card trail:
# - luck is a caller-side bias with no v1 data source: luck 0 rolls the
#   declared drop_weights verbatim; higher ladder positions scale by
#   (1 + luck * ladder_index).
# - uid is stamped by the bank (GWGameState.bank_add); a rolled row ships
#   uid 0 — identity is a bank concern (C6/C9), not a roll concern.
# - items.json declares roll_ranges for atk_speed/proj_count only, so the
#   sole data source for a rolled stat value is the rolled item level itself
#   (ilvl, rolled inside the base's declared level_band).
# - enemy_drops emits the gear row {kind:"item"} on every kill (A5 "direct
#   enemy drops"; the declared drop_weights pick the rarity — inventing an
#   extra drop rate would be an undeclared number) plus the optional
#   chance-gated {kind:"material"} row (F2-6).
# - victory_chest resolves its rarity from rarity.json chest_tiers (clamped
#   index, ladder stays in the data); the rolled row enters the bank through
#   the bank_add mutators in mission step (6) (C12/F2-2).


# Weighted ladder pick for one difficulty (drop_weights[diff]); returns the
# chosen rarity name. Purely declared weights + the caller's luck bias.
static func roll_rarity(tables: Dictionary, diff: String, luck: float, rng: RandomNumberGenerator) -> String:
	var rarity_table: Dictionary = tables["rarity"]
	var ladder: Array = rarity_table["ladder"]
	var weights: Dictionary = rarity_table["drop_weights"][diff]
	var shifted: Array[float] = []
	var total := 0.0
	for i: int in ladder.size():
		var weight := float(weights.get(ladder[i], 0)) * (1.0 + luck * float(i))
		shifted.append(weight)
		total += weight
	var pick: float = rng.randf() * total
	for i: int in ladder.size():
		pick -= shifted[i]
		if pick <= 0.0:
			return String(ladder[i])
	return String(ladder[ladder.size() - 1])


# One C9 item instance rolled from a base row + a chosen rarity. The return
# literal below IS the C9 key set (12 keys, tests pin it); every value is a
# declared pool pick or a roll inside declared ranges.
static func roll_item(base: Dictionary, rarity: String, tables, rng) -> Dictionary:
	var band: Array = base["level_band"]
	var ilvl: int = int(band[0]) + rng.randi() % (int(band[1]) - int(band[0]) + 1)
	var pool: Array = base["pool_secondary"]
	var secondary: Variant = null
	if not pool.is_empty():
		secondary = {"stat": String(pool[rng.randi() % pool.size()]), "value": float(ilvl)}
	var shot_types: Array = base["shot_types"]
	var shot_type: Variant = null
	if not shot_types.is_empty():
		shot_type = String(shot_types[rng.randi() % shot_types.size()])
	var ranges: Dictionary = base["roll_ranges"]
	var speed: Array = ranges["atk_speed"]
	var counts: Array = ranges["proj_count"]
	var candidates: Array = base["mods_pool"].duplicate()
	var slots := int(tables["rarity"]["mod_slots"].get(rarity, 0))
	var mods: Array = []
	for _slot: int in mini(slots, candidates.size()):
		var mod_id := String(candidates.pop_at(rng.randi() % candidates.size()))
		mods.append({"mod_id": mod_id, "rarity": _mod_rarity_min(tables, mod_id)})
	return {
		"uid": 0,
		"base_id": String(base["id"]),
		"slot": String(base["slot"]),
		"rarity": rarity,
		"ilvl": ilvl,
		"primary": {"stat": String(base["primary"]), "value": float(ilvl)},
		"secondary": secondary,
		"atk_speed": float(speed[0]) + rng.randf() * (float(speed[1]) - float(speed[0])),
		"shot_type": shot_type,
		"proj_count": int(counts[0]) + rng.randi() % (int(counts[1]) - int(counts[0]) + 1),
		"mods": mods,
		"upgraded": 0,
	}


# All world drops for one kill (C2 death crossing): the gear row — kill
# always fires the declared-weight roll (A5) — plus the optional
# chance-gated material row {kind:"material"} (F2-6).
static func enemy_drops(row: Dictionary, tables, rng) -> Array:
	var drops: Array = []
	var rarity := roll_rarity(tables, String(row["drop_table_id"]), 0.0, rng)
	var item := roll_item(_pick_base(tables["items"], rng), rarity, tables, rng)
	drops.append({"kind": "item", "item": item})
	var mat: Variant = row.get("material_drop")
	if mat is Dictionary and rng.randf() < float(mat["chance"]):
		drops.append({"kind": "material", "id": String(mat["id"])})
	return drops


# The free victory chest for one win (A5): rarity = rarity.json chest_tiers
# at the clamped tier index, one C9 row returned in an Array (the bank_add
# mutators route it per C12/F2-2).
static func victory_chest(tier: int, tables, rng) -> Array:
	var tiers: Array = tables["rarity"]["chest_tiers"]
	var rarity := String(tiers[clampi(tier, 0, tiers.size() - 1)])
	return [roll_item(_pick_base(tables["items"], rng), rarity, tables, rng)]


# Uniform base pick from the declared items pool (rng-qualified draw).
static func _pick_base(items: Array, rng) -> Dictionary:
	return items[rng.randi() % items.size()]


# The mod's declared rarity floor (mods.json rarity_min); "" when the pool
# references an undeclared mod — test_data_schemas forbids that data state.
static func _mod_rarity_min(tables, mod_id: String) -> String:
	for mod_row: Dictionary in tables["mods"]:
		if String(mod_row.get("id", "")) == mod_id:
			return String(mod_row.get("rarity_min", ""))
	return ""
