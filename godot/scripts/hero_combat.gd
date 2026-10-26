extends RefCounted

# hero_combat — the ACTIVE hero's two attacks + 4 abilities (Modules row
# scripts/hero_combat.gd, MC 11274.1.14 / card 11321). NO numeric balance
# literals (I2 structural whitelist only): every number is the heroes row
# (attacks/abilities/base), mission.hero_state (C4), or SimCombat math
# (C2). Damage resolves via SimCombat.hero_hit with the passed rng's roll
# — crit via rng, receiver-qualified rng.randf() (F2-1/I6). Ability gate =
# blue (SimCombat.ability_ready) AND the C4 cooldowns[i] array; blue spend
# and cooldown writes land in the mission-local state, nowhere else (I3:
# blue is spent ONLY here among hero files).
#
# Active-only scoping (F2-8): the mission calls tick() exactly when the
# ACTIVE hero is not downed (step_hero gate) — attack timers therefore
# tick for the active hero only; inactive AND downed timers freeze and
# survive swaps unchanged, same rule as the cooldown arrays.
#
# Greybox input map (declared readings; brief: "targeting per its wording"
# — the pinned row words no more than nearest-target application):
#   MouseLeft / MouseRight held  -> attacks.primary / .secondary, one hit
#     per attacks.cooldown against the NEAREST entity inside attacks.range
#     (3D distance: ground lanes sit at y=0, air lanes at their authored
#     waypoint y (F16) — a melee reach simply never contains a flyer, no
#     fly-flag special case exists here).
#   Digit1..Digit4 held -> abilities 1..4. Digit4 is why the W4 bridge
#     added that code. Digit1-3 stay the W6 hot-swap press-alias untouched:
#     this file consumes NO presses (mission step (5) drains the bridge
#     exactly as W6 shipped); held-level casting cannot re-route presses.
#   Ability effect fields: "pierce" on a single-target row has a
#     consumer (W15b) — the hit continues along the impact entity's
#     lane via the ONE SimCombat selection static, same rule a tower
#     tier row rides. The others (stun/taunt/barrier/...) are data for
#     later waves: a dmg_scale==0 ability pays blue + cooldown and
#     lands no hit.
#   Ability damage = base.ability_power x dmg_scale (single source read;
#     attacks use base.damage x dmg_scale), crits via hero_hit like any
#     hero hit. aoe>0 hits EVERY entity within the radius of the hero
#     stand; aoe==0 single-hits the nearest at primary attack range.

const SIM_COMBAT := preload("res://sim/sim_combat.gd")

const ABILITY_CODES := ["Digit1", "Digit2", "Digit3", "Digit4"]

var mission = null
var atk_cd: Dictionary = {}      # hero_id -> [primary, secondary] timers


func setup(m) -> void:
	mission = m


# One funnel slot-(2) tick from the hero body's stand position.
func tick(delta: float, pos: Vector3) -> void:
	var hero: Dictionary = mission.hero_defs[mission.hero_id]
	var timers: Array = atk_cd.get(mission.hero_id, [0.0, 0.0])
	atk_cd[mission.hero_id] = timers
	for i: int in timers.size():
		timers[i] = maxf(float(timers[i]) - delta, 0.0)
	var held: Dictionary = mission.bridge.held
	if held.has("MouseLeft") and float(timers[0]) <= 0.0:
		_attack("primary", timers, 0, hero, pos)
	if held.has("MouseRight") and float(timers[1]) <= 0.0:
		_attack("secondary", timers, 1, hero, pos)
	for i: int in ABILITY_CODES.size():
		if held.has(ABILITY_CODES[i]):
			_ability(i, hero, pos)


func _attack(slot: String, timers: Array, ti: int, hero: Dictionary,
		pos: Vector3) -> void:
	var atk: Dictionary = hero["attacks"][slot]
	var target: Dictionary = _nearest(pos, float(atk["range"]))
	if target.is_empty():
		return                 # timer stays ready: no whiffed cooldown burn
	_hit(target, float(hero["base"]["damage"]) * float(atk["dmg_scale"]),
			hero)
	timers[ti] = float(atk["cooldown"])


func _ability(i: int, hero: Dictionary, pos: Vector3) -> void:
	var ab: Dictionary = hero["abilities"][i]
	var cds: Array = mission.hero_state[mission.hero_id]["cooldowns"]
	if float(cds[i]) > 0.0:
		return                 # C4/F2-8 cooldown gate (ticks only active)
	var cost := float(ab["mana_cost"])
	if not SIM_COMBAT.ability_ready(mission.blue, cost):
		return                 # C2 blue gate (I3: the ONLY blue spend leg)
	mission.blue = float(mission.blue) - cost
	cds[i] = float(ab["cd"])
	if float(ab["dmg_scale"]) <= 0.0:
		return                 # non-damage effect: cost + cooldown only
	var dmg := float(hero["base"]["ability_power"]) * float(ab["dmg_scale"])
	var aoe := float(ab["aoe"])
	var targets: Array = []
	if aoe > 0.0:
		targets = _in_range(pos, aoe)
	else:
		var solo: Dictionary = _nearest(pos,
				float(hero["attacks"]["primary"]["range"]))
		if solo.is_empty():
			return
		targets = [solo]
		# W15b: a single-target ability whose row says "pierce" continues
		# through the lane via the ONE selection static (SimCombat, the
		# same rule a tower tier row rides) — each extra hit rides the
		# same dmg through _hit (I4: no second damage path; crit rolls
		# per hit, the shipped hero_hit shape). The radius is the data
		# range already used to pick the primary; AoE casts never reach
		# this leg.
		targets.append_array(SIM_COMBAT.extra_targets(solo,
				mission.get_node("EnemyRunner").entities,
				float(hero["attacks"]["primary"]["range"]),
				String(ab.get("effect", "none"))))
	for ent: Variant in targets:
		_hit(ent, dmg, hero)


# One resolved hero hit: damage through SimCombat.hero_hit, the crit roll
# drawn from the mission rng (receiver-qualified, F2-1), applied through
# the runner's damage entry point (the mission's step-(4) death funnel
# awards green+xp+drops — no reward math here).
func _hit(ent: Variant, dmg: float, hero: Dictionary) -> void:
	var base: Dictionary = hero["base"]
	var hit: Dictionary = SIM_COMBAT.hero_hit(dmg, float(base["crit_chance"]),
			float(base["crit_damage"]), mission.rng.randf())
	mission.get_node("EnemyRunner").damage(ent, float(hit["damage"]))


# The search legs delegate to the runner that OWNS the records (W16
# dedup: the ONE nearest/in_range loop lives in enemy_runner).
func _nearest(pos: Vector3, r: float) -> Dictionary:
	return mission.get_node("EnemyRunner").nearest(pos, r)


func _in_range(pos: Vector3, r: float) -> Array:
	return mission.get_node("EnemyRunner").in_range(pos, r)
