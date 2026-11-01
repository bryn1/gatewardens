# SCRATCH diagnostic for MC 11897 W-R — NOT for the repo. Mechanism
# probe: does hailspire_tower become a fire candidate (dps>0, target in
# range, FIRE_FRAC drop met, replicated READ-ONLY from fx_director
# _observe_fires) but lose the MAX_FX cap race to sparks+numbers?
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const HERO_IDS := ["warden", "deadeye", "embercaller"]
const TOWER_IDS := ["ballista", "bombard", "hailspire_tower"]
const FEED_IDS := ["skitterling", "husk_brute", "ash_bandit"]
const MAX_FX := 64
const FIRE_FRAC := 0.5
const HP_EPS := 1e-6


func _init() -> void:
	var seed_graph: Dictionary = GW_COMPOSE.build_graph(GW_TABLES.new("res://data"))
	seed_graph["state"].set_deck(HERO_IDS.duplicate())
	var packed = ResourceLoader.load("res://Main.tscn")
	var main = packed.instantiate()
	root.add_child(main)
	main._ready()
	main.start_mission("gatefall", "normal")
	var m = main.mission
	var fx = m.get_node("FxDirector")
	m.core_main.hp_max *= 5.0
	m.core_main.hp = m.core_main.hp_max
	var guard := 0
	while guard < 4000 and String(m.phase_kind) == "build":
		m.step(1.0 / 60.0)
		fx.fx_step(1.0 / 60.0)
		guard += 1
	m.green = 100000
	var trows := {}
	for row: Dictionary in m.tables.rows("towers"):
		trows[String(row["id"])] = row
	var offs := [Vector3(-20, 0.0, 2.0), Vector3(-24, 0.0, 3.0),
			Vector3(-28, 0.0, 5.0), Vector3(-32, 0.0, 1.0),
			Vector3(-14, 0.0, 3.0), Vector3(-17, 0.0, 7.0)]
	var ti := 0
	for tid: String in TOWER_IDS:
		for k: int in 2:
			m.place_defense(trows[tid], 1, offs[ti])
			ti += 1
	var runner = m.get_node("EnemyRunner")
	var lane: Dictionary = m.lanes["lane_g1"]
	# candidate + space census, per defense index (list order)
	var cand := [0, 0, 0, 0, 0, 0]
	var sat := [0, 0, 0, 0, 0, 0]
	var space := [0, 0, 0, 0, 0, 0]
	# replicated external drop map (READ-ONLY duplication of fx_director
	# _observe_enemies hp-drop detection, harness license, scratch only)
	var tracked := {}
	var f := 0
	var feed_k := 0
	guard = 0
	while guard < 40000:
		guard += 1
		if f % 45 == 0:
			runner.spawn({"enemy_id": FEED_IDS[feed_k % FEED_IDS.size()],
					"count": 1}, lane, m.enemy_defs, m.rng)
			feed_k += 1
		m.step(1.0 / 60.0)
		m.core_main.hp = m.core_main.hp_max
		# pre-step snapshot for drops (same shape as the director's)
		var drops := {}
		var seen := {}
		for ent: Dictionary in runner.entities:
			var iid: int = (ent["node"] as Node).get_instance_id()
			var hp := float(ent["hp"])
			var prev: Variant = tracked.get(iid)
			if prev != null and hp < float(prev) - HP_EPS:
				drops[iid] = float(prev) - hp
			tracked[iid] = hp
			seen[iid] = true
		var live_before := int(fx.get_child_count())
		fx.fx_step(1.0 / 60.0)
		# candidate census: replicate the gate conditions of _observe_fires
		if not drops.is_empty():
			var di := 0
			for rec: Dictionary in m.defense_list:
				var obj = rec["obj"]
				if float(obj.hp) <= 0.0:
					di += 1
					continue
				var applied := float(obj.dps()) * (1.0 / 60.0)
				if applied <= 0.0:
					di += 1
					continue
				var row: Dictionary = obj.bonus_row()
				var target: Dictionary = runner.nearest(obj.pos, float(row["range"]))
				if target.is_empty():
					di += 1
					continue
				var tiid: int = (target["node"] as Node).get_instance_id()
				if float(drops.get(tiid, 0.0)) < applied * FIRE_FRAC:
					di += 1
					continue
				cand[di] += 1
				if live_before >= MAX_FX:
					sat[di] += 1
				else:
					space[di] += 1
				di += 1
		for iid: int in tracked.keys():
			if not seen.has(iid):
				tracked.erase(iid)
		f += 1
	print("DIAG-DEFS")
	var di2 := 0
	for rec: Dictionary in m.defense_list:
		var obj = rec["obj"]
		print("DIAG-DEF idx=%d id=%s cand=%d sat=%d space=%d" % [
				di2, String(obj.trow["id"]), cand[di2], sat[di2], space[di2]])
		di2 += 1
	print("DIAG-TRACER n=%d DIAG-SPARK n=%d DIAG-POOF n=%d DIAG-NUMBER n=%d live_max=%d" % [
			int(fx.spawned_tracers), int(fx.spawned_sparks),
			int(fx.spawned_poofs), int(fx.spawned_numbers), int(fx.live_max)])
	quit(0)
