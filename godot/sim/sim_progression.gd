class_name SimProgression
extends RefCounted

# Hero XP/level/ascension math (Modules row sim_progression). Pure statics:
# the curve/tree arrive as data parameters (xp.json / ascension.json via
# GWTables) — no balance literals live in this file (I2) and nothing here
# draws randomness at all (I6).
#
# Curve semantics (reading recorded on the card trail): hero_curve[i] is
# the CUMULATIVE xp that reaches level i+2 (entry 0 is the level-2
# threshold; a hero starts at level 1 with xp 0). The hero level is capped
# by the curve size — A2's level cap 50 is the shipped 50-entry hero_curve,
# so the cap is a data property and never a code literal; the final entry
# is the overflow-guard threshold the clamp reads.


# Level for a total xp: thresholds passed in order, capped at the curve
# size (the level cap stays in the data, A2).
static func level_from_xp(curve: Array, xp: int) -> int:
	if curve.is_empty():
		return 1
	var level := 1
	for threshold: int in curve:
		if xp < threshold:
			break
		level += 1
	return mini(level, curve.size())


# Total xp needed to reach `level`: the exact inverse of level_from_xp
# (level 1 costs 0; indices are clamped so the function never ranges out).
static func xp_need(curve: Array, level: int) -> int:
	if curve.is_empty() or level <= 1:
		return 0
	return int(curve[clampi(level - 2, 0, curve.size() - 1)])


# Ascension points earned from total levels gained; per_level is
# ascension.json points_per_level — the value stays in the data (I2).
static func asc_points(levels_total: int, per_level: int) -> int:
	return levels_total * per_level


# Aggregate the per_point value of every spent ascension node, keyed by stat
# (tree = ascension.json "tree" {branch: rows}; spent = {power_id: points}).
# The gate is on its face per node inside every tree: spend is clamped at
# the node's declared `max` (and at 0), so no branch or node is ever read
# past its declared cap. Nodes sharing a stat sum together.
static func asc_modifier(tree: Dictionary, spent: Dictionary) -> Dictionary:
	var totals: Dictionary = {}
	for branch: String in tree:
		for row: Dictionary in tree[branch]:
			var id := String(row.get("id", ""))
			var points := clampi(int(spent.get(id, 0)), 0, int(row.get("max", 0)))
			if points <= 0:
				continue
			var stat := String(row["per_point"]["stat"])
			totals[stat] = float(totals.get(stat, 0.0)) \
				+ float(row["per_point"]["val"]) * points
	return totals
