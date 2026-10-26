# defense_obj — one placed defense (Modules row scripts/defense_obj.gd,
# MC 11274.1.15 / card 11322): tier hp/damage, repair, sell, target+fire
# through SimCombat.tower_dps ONLY, trap charges, relic bonus applied
# (C11 — later wave, see readings), tracks `total_spent:int` (green spent
# on place + upgrades ONLY — the C3 sell base) and the class-dispatch
# dict {tower,blockade,trap} the pinned row names.
#
# RefCounted record in the scene layer (the core_obj/bridge/game_state
# mechanism: injectable under `-s`, no _ready). The mission's step-(3)
# hook (W6, `rec["tick"]`) calls tick(delta): the tower_dps application
# site is the ONE place tower damage is applied (C12 slot (3), I4 — a
# grep for SIM_COMBAT.tower_dps in scripts/ finds exactly this call).
#
# C3/R1 (all math through SimEconomy statics, zero formulas here):
#   upgrade T(i)->T(i+1) = upgrade_cost(base_cost, tier, ratios), tier is
#     the 0-BASED current index (ratios[0]=0.5 is the T1->T2 step);
#   repair = repair_cost(base_cost, missing_ratio, economy.repair_ratio);
#   sell   = sell_value(total_spent, missing_ratio, economy.sell_ratio),
#     refund routed through add_green (never above the green cap).
# The green ledger writes land HERE, once per operation (place_defense
# owns the place leg's write in mission.gd).
#
# Readings (declared; full text in W8-evidence.md):
# - Fire model: sustained dps — damage per tick = tower_dps(tier_row) x
#   delta against the NEAREST live entity inside the tier row's range
#   (target selection per the pinned row's wording, the hero_combat
#   nearest idiom; plain 3D distance so air lanes weigh by their F16 y).
#   No discrete projectile sim ships in v1 (none is pinned; C4's
#   ownerless-projectile rule is a snapshot-damage rule for when one does).
# - Blockade: fire_rate 0 -> tower_dps 0 -> never fires; the "block"
#   effect string has no consumer yet (the pinned runner row is lane-walk
#   only — nothing attacks a defense in v1), so a blockade ships as a
#   placeable hp record that counts to cap and repairs/sells like any
#   defense. Honest inert, not an invented mechanic.
# - Trap: fires like a tower (same dps idiom) but drains 1 trap_charge
#   per fire-second (charges are seconds of sustained fire; the row's
#   "slow" effect string is data for a later wave — no slow magnitude
#   exists in towers.json to read, and inventing one is I2-breaking).
# - Upgrade restocks the new tier's hp to full (tier change = new
#   hp_max row); repair tops hp to hp_max. total_spent never counts
#   repairs (C3). A full-HP sell refunds roundi(0) = 0 — the pinned R1
#   formula's literal reading.
# - Nothing damages defenses in v1 (same no-attacker reading as
#   blockades); take_damage(d) is the pinned core_obj-shaped entry the
#   later engagement wave will call, and the smoke harness uses it to
#   set up C3's missing-ratio legs (the boot_probe drive-real-entry-points
#   license).
# - Relic bonus (C11): APPLIED HERE (W14 leg 2, MC 11274.1.25 / card
#   11341) on top of the tier row via SimInventory.relic_bonuses — the
#   ONE relic stat site (mission.assign_relic routes the row here; the
#   relic bases' stats are exactly the tier-row keys items.json rolls:
#   damage/hp/fire_rate/range — no stat is invented).

const SIM_ECONOMY := preload("res://sim/sim_economy.gd")
const SIM_COMBAT := preload("res://sim/sim_combat.gd")
const SIM_INVENTORY := preload("res://sim/sim_inventory.gd")

const MESH_TOWER := preload("res://assets/mesh_capsule.tres")
const MESH_BLOCK := preload("res://assets/mesh_box.tres")
const MAT_TOWER := preload("res://assets/mat_defense_tower.tres")
const MAT_BLOCKADE := preload("res://assets/mat_defense_blockade.tres")
const MAT_TRAP := preload("res://assets/mat_defense_trap.tres")

var m = null                # mission root (injected: green + runner + economy)
var uid := 0
var trow: Dictionary = {}   # the towers.json row (read-only data)
var class_id := ""          # "tower" | "blockade" | "trap"
var tier := 0               # 0-BASED tiers index (display T1 = tier 0 + 1)
var hp := 0.0
var hp_max := 0.0
var total_spent := 0        # C3 sell base: place + upgrade green ONLY
var charges := 0            # trap_charges countdown (others: 0, unused)
var fire_acc := 0.0         # trap charge meter (one drain per fire-second)
var pos := Vector3.ZERO
var node = null             # greybox MeshInstance3D (made here, added by mission)
var fire_by_class: Dictionary = {}   # pinned class-dispatch dict
var relic_uid := 0          # assigned relic pool uid (0 = none, C11)
var relic_bonuses: Dictionary = {}   # stat -> add (SimInventory's, C11)


# C11 (W14 leg 2): the mission's assign_relic/unassign_relic crossing
# lands its bonus HERE (the pinned application site, header). The hp leg
# re-derives hp_max through the tier application; current hp is clamped,
# never healed, by a relic move (declared reading).
func assign_relic(item: Dictionary) -> void:
	relic_uid = int(item.get("uid", 0))
	relic_bonuses = SIM_INVENTORY.relic_bonuses(item)
	hp_max = float(bonus_row()["hp"])
	hp = minf(hp, hp_max)


func clear_relic() -> void:
	relic_uid = 0
	relic_bonuses = {}
	hp_max = float(bonus_row()["hp"])
	hp = minf(hp, hp_max)


# The tier row with the relic's stat adds on top — the ONE read path for
# a tier VALUE (dps, range, hp all ride it). No relic = the bare tier row.
func bonus_row() -> Dictionary:
	var row: Dictionary = tier_row().duplicate()
	for stat: String in relic_bonuses:
		if row.has(stat):
			row[stat] = float(row[stat]) + float(relic_bonuses[stat])
	return row


# One-call parameterization (setup-by-injection, R3): T1 at build (the
# flat-tier build reading), hp from the tiers[0] row.
func init_defense(mission, row: Dictionary, at: Vector3, uid_in: int) -> void:
	m = mission
	trow = row
	class_id = String(row["class"])
	uid = uid_in
	pos = at
	tier = 0
	_apply_tier()
	# C3: the place leg's whole base_cost is sell-base (mission.place_defense
	# spends exactly this at its single green write).
	total_spent = int(row["base_cost"])
	charges = int(row.get("trap_charges", 0))
	fire_by_class = {"tower": _fire_tower, "blockade": _fire_blockade,
		"trap": _fire_trap}
	node = _make_visual()


func tier_row() -> Dictionary:
	return trow["tiers"][tier]


func dps() -> float:
	return SIM_COMBAT.tower_dps(bonus_row())


func missing_ratio() -> float:
	if hp_max <= 0.0:
		return 0.0
	return (hp_max - hp) / hp_max


# Damage entry (core_obj shape: the amount is already mitigated; nothing
# attacks defenses in v1, so only harness legs call this today).
func take_damage(d: float) -> void:
	hp = maxf(hp - d, 0.0)


# ---- funnel slot (3) fire leg (C12): the tick the W6 hook carries ----

func tick(delta: float) -> void:
	if hp <= 0.0:
		return
	fire_by_class[class_id].call(delta)


func _fire_tower(delta: float) -> void:
	var target: Dictionary = _nearest(float(bonus_row()["range"]))
	if target.is_empty():
		return
	# THE tower_dps application site (slot 3, single I4 site):
	m.get_node("EnemyRunner").damage(target, dps() * delta)


func _fire_blockade(_delta: float) -> void:
	return    # "block": no damage source in data, no attacker in v1 (header)


func _fire_trap(delta: float) -> void:
	if charges <= 0:
		return
	var target: Dictionary = _nearest(float(bonus_row()["range"]))
	if target.is_empty():
		return
	m.get_node("EnemyRunner").damage(target, dps() * delta)
	fire_acc += delta
	while fire_acc >= 1.0 and charges > 0:
		fire_acc -= 1.0
		charges -= 1


# Nearest live entity within r of pos ({} = none) — the hero_combat _nearest
# idiom over the runner's records, 3D distance (F16 air y weighs naturally).
func _nearest(r: float) -> Dictionary:
	var best: Dictionary = {}
	var best_d := r
	for ent: Dictionary in m.get_node("EnemyRunner").entities:
		var d: float = (ent["pos"] as Vector3).distance_to(pos)
		if d <= best_d:
			best_d = d
			best = ent
	return best


# ---- C3 lifecycle: cost from the static, ledger write once, effect once ----

# Next ladder rung's price (-1 = already T5): the SAME static the upgrade
# leg pays through, exposed for the panel's can_afford gate (UI reads,
# never recomputes).
func next_upgrade_cost() -> int:
	if tier + 1 >= int((trow["tiers"] as Array).size()):
		return -1
	return SIM_ECONOMY.upgrade_cost(int(trow["base_cost"]), tier,
			m.economy["upgrade_ratios"])


func upgrade() -> Dictionary:
	var cost := next_upgrade_cost()
	if cost < 0:
		return {"ok": false, "why": "max"}
	if not SIM_ECONOMY.can_afford(int(m.green), cost):
		return {"ok": false, "why": "green", "cost": cost}
	m.green = int(m.green) - cost
	tier += 1
	_apply_tier()
	total_spent += cost
	return {"ok": true, "cost": cost, "tier": tier + 1}


func repair() -> Dictionary:
	var cost := SIM_ECONOMY.repair_cost(int(trow["base_cost"]),
			missing_ratio(), float(m.economy["repair_ratio"]))
	if cost <= 0:
		return {"ok": false, "why": "full", "cost": 0}
	if not SIM_ECONOMY.can_afford(int(m.green), cost):
		return {"ok": false, "why": "green", "cost": cost}
	m.green = int(m.green) - cost
	hp = hp_max
	return {"ok": true, "cost": cost}


func sell() -> Dictionary:
	var refund := SIM_ECONOMY.sell_value(total_spent, missing_ratio(),
			float(m.economy["sell_ratio"]))
	m.green = SIM_ECONOMY.add_green(int(m.green), refund,
			int(m.economy.get("green", {}).get("cap", 0)))
	return {"ok": true, "refund": refund}


func _apply_tier() -> void:
	hp_max = float(bonus_row()["hp"])
	hp = hp_max


# Greybox visual per idiom (W6/W7: primitives + .tres tints, zero
# per-entity .tscn): tower capsule, blockade cube, trap flat plate.
func _make_visual():
	var vis := MeshInstance3D.new()
	match class_id:
		"tower":
			vis.mesh = MESH_TOWER.duplicate()
			vis.material_override = MAT_TOWER.duplicate()
			vis.scale = Vector3(0.5, 2, 0.5)
		"blockade":
			vis.mesh = MESH_BLOCK.duplicate()
			vis.material_override = MAT_BLOCKADE.duplicate()
		_:
			vis.mesh = MESH_BLOCK.duplicate()
			vis.material_override = MAT_TRAP.duplicate()
			vis.scale = Vector3(2, 0.5, 2)
	vis.position = pos
	return vis
