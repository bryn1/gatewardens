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
