class_name SimEconomy
extends RefCounted

# Green-mana + build/upgrade/repair/sell math (C3, R1 pinned wiki formulas;
# F12). Every rate/ratio arrives as a parameter from economy.json — no
# balance literals live in this file (I2). Green only: blue never appears
# in any signature here (I3).


# Green award/cap arithmetic: the running total never exceeds cap.
static func add_green(cur: int, amt: int, cap: int) -> int:
	return mini(cur + amt, cap)


# C3: T(i) -> T(i+1) = base_cost * ratios[i]; ratios = economy.upgrade_ratios
# ([0.5, 1.0, 1.5, 2.0] -> 50/100/150/200 on base 100).
static func upgrade_cost(base: int, tier: int, ratios: Array) -> int:
	return int(base * ratios[tier])


# C3/R1: repair = base_cost * ratio * missing_ratio, min 1 while missing > 0.
static func repair_cost(base_cost: int, missing_ratio: float, ratio: float) -> int:
	if missing_ratio <= 0.0:
		return 0
	return maxi(roundi(base_cost * ratio * missing_ratio), 1)


# C3/R1: sell = total_spent * ratio * missing_ratio (total_spent = green spent
# on place + upgrades only; defense_obj tracks it).
static func sell_value(total_spent: int, missing_ratio: float, ratio: float) -> int:
	return roundi(total_spent * ratio * missing_ratio)


static func can_afford(green: int, cost: int) -> bool:
	return green >= cost
