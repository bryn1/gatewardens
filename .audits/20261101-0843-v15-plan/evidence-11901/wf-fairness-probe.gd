extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

const HERO_IDS := ["warden", "deadeye", "embercaller"]
const TOWER_IDS := ["ballista", "bombard", "hailspire_tower"]
const FEED_IDS := ["skitterling", "husk_brute", "ash_bandit"]
const ICE_PATH := "res://assets/v11/fx_proj_ice.png"
const BOLT_PATH := "res://assets/v11/fx_proj_bolt.png"
const WALK := 3000     # sim+fx run ~7 fps headless here: 3000 frames
                       # ~ 7 min worst case (pre-fix runs the FULL budget)


func _init() -> void:
	# Boot: mission.tscn instantiated directly (the E5 test_kit_fx idiom
	# — headless-safe; the kit's Main-router boot is xvfb-only, declared).
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	var state = graph["state"]
	state.set_deck(HERO_IDS.duplicate())
	var packed = ResourceLoader.load("res://scenes/mission.tscn")
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()
	var rng := RandomNumberGenerator.new()
	rng.seed = 11901
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	if m.core_main == null:
		_fail("mission setup produced no core")
		return
	var fx = m.get_node_or_null("FxDirector")
	if fx == null:
		_fail("mission.tscn does not ship FxDirector")
		return
	m.core_main.hp_max *= 5.0
	m.core_main.hp = m.core_main.hp_max
	var guard := 0
	while guard < 4000 and String(m.phase_kind) == "build":
		m.step(1.0 / 60.0)
		fx.fx_step(1.0 / 60.0)
		guard += 1
	if String(m.phase_kind) != "combat":
		_fail("combat never started")
		return
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
			var pl: Dictionary = m.place_defense(trows[tid], 1, offs[ti])
			if not bool(pl["ok"]):
				_fail("place_defense refused %s: %s" % [tid, str(pl)])
				return
			ti += 1
	if int(m.defense_list.size()) != 6:
		_fail("defense_list not 6 rows")
		return
	print("WF2-ORDER first=%s last=%s" % [
		String(m.defense_list[0]["obj"].trow["id"]),
		String(m.defense_list[5]["obj"].trow["id"])])
	var runner = m.get_node("EnemyRunner")
	var lane: Dictionary = m.lanes["lane_g1"]
	var ice_n := 0
	var bolt_n := 0
	var f := 0
	var feed_k := 0
	while f < WALK:
		f += 1
		if f % 45 == 0:
			runner.spawn({"enemy_id": FEED_IDS[feed_k % FEED_IDS.size()],
					"count": 1}, lane, m.enemy_defs, m.rng)
			feed_k += 1
		m.step(1.0 / 60.0)
		m.core_main.hp = m.core_main.hp_max
		fx.fx_step(1.0 / 60.0)
		for c: Node in fx.get_children():
			var spr := c as Sprite3D
			if spr != null and spr.texture != null:
				var p := String(spr.texture.resource_path)
				if p == ICE_PATH:
					ice_n += 1
				elif p == BOLT_PATH:
					bolt_n += 1
		if ice_n >= 1 and bolt_n >= 1:
			break
		if m.outcome != null:
			_fail("mission ended before the fairness legs were met (f=%d)" % f)
			return
	print("WF2-BOLT n=%d frames=%d" % [bolt_n, f])
	if ice_n < 1:
		_fail("last-placed hailspires never got a leftover slot (f=%d bolts=%d)" 				% [f, bolt_n])
		return
	print("WF2-ICE n=%d frames=%d" % [ice_n, f])
	print("WF2-OK")
	quit(0)


func _fail(why: String) -> void:
	print("WF2-FAIL " + why)
	quit(1)
