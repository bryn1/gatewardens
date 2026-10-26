class_name SimCombat
extends RefCounted

# Damage/ability formulas (Modules row sim_combat). Pure functions: every
# roll arrives as a parameter — the RNG is the caller's (C12), no draws here
# (I6/F2-1). No balance literals: chances/mults come from data (I2).


# One hero attack resolved: the caller rolled `roll` (rng.randf()); crit
# fires when roll < crit_chance, scaled by crit_mult.
static func hero_hit(dmg: float, crit_chance: float, crit_mult: float, roll: float) -> Dictionary:
	if roll < crit_chance:
		return {"damage": dmg * crit_mult, "crit": true}
	return {"damage": dmg, "crit": false}


# C4 blue pool tick: regen is the ACTIVE hero's base.blue_regen (sole
# source, F7), clamped at that hero's blue_max cap.
static func tick_blue(blue: float, regen: float, cap: float, dt: float) -> float:
	return minf(blue + regen * dt, cap)


static func ability_ready(blue: float, cost: float) -> bool:
	return blue >= cost


# Sustained dps of one placed defense tier row (towers.json tiers carry
# damage + fire_rate).
static func tower_dps(tier_row: Dictionary) -> float:
	return float(tier_row.get("damage", 0.0)) * float(tier_row.get("fire_rate", 0.0))


# Armor mitigation to a core: armor = fraction of damage absorbed, clamped
# so the result never goes negative.
static func dmg_to_core(dmg: float, armor: float) -> float:
	return dmg * maxf(0.0, 1.0 - armor)


# The ONE effect consumer (W15b, MC 11274.1.27 / card 11379): which EXTRA
# entities a landed single hit also strikes — WHO is hit only, never HOW
# MUCH (every extra carries the caller's own already-computed damage
# through the runner's same damage entry; I4 — no second damage path).
# The lane model (C7): lanes are 1-D waypoint walks, so "pierce" continues
# along the impact entity's lane — every other same-lane entity within the
# DATA radius r of the impact point (the row's own range; the data names
# no count and no direction, so the chain is the lane ∩ radius, declared).
# "splash" is the blast reading: every other entity within r of the impact
# point REGARDLESS of lane (crossing lanes near an impact splash across
# them — the W15 double-flood this data was cut for). Any other effect
# ("none", "slow", "block", "stun", ..., missing) adds no extra target —
# plain single hit; magnitudes for those never exist in the data (I2).
# Skips the primary itself and entities already dead (hp <= 0); r <= 0
# adds nothing (degenerate leg). Entity identity uses GDScript Dictionary
# equality, which is CONTENT equality (probed 4.7.2): live records always
# carry a distinct per-entity node, so the primary is the only content-
# equal match; synthetic probe records keep distinct positions.
static func extra_targets(primary: Dictionary, pool: Array, r: float,
		effect: String) -> Array:
	var picked: Array = []
	if r <= 0.0 or (effect != "pierce" and effect != "splash"):
		return picked
	var impact: Vector3 = primary["pos"]
	for ent: Dictionary in pool:
		if ent == primary or float(ent["hp"]) <= 0.0:
			continue
		if effect == "pierce" \
				and String(ent["lane"]["id"]) != String(primary["lane"]["id"]):
			continue
		if (ent["pos"] as Vector3).distance_to(impact) <= r:
			picked.append(ent)
	return picked
