# v5_fx_probe — the V5 combat-FX headless proof (MC card 11552 /
# milestone 11462). Boots the REAL Main.tscn, enters the mission through
# the shipped router (main.start_mission — never around it, the
# v11_sprite_probe idiom), then drives mission.step AND the mounted
# FxDirector.fx_step in lockstep (E5: -s dispatches no _process, so the
# probe pumps both by hand, mission root first — the exact live tree
# order). Asserts, on a real fight (3 shooter towers + fed enemies):
# (a) the director mounted from mission.tscn (pinned script RESOURCE
#     PATH, not the node name alone);
# (b) at least one tracer, one spark and one poof spawned in combat,
#     and the four fx sheets are seen on LIVE nodes pinned by committed
#     RESOURCE PATH — bolt, ice, spark, poof (the bank is never the
#     oracle: the V1.1-b lesson, a broken map self-agrees via fallback);
# (c) live fx nodes never exceed the 64 cap and FREE THEMSELVES: with
#     the sim frozen the child count walks back to 0 (the leak row,
#     high-water vs settled baseline);
# (d) teardown: freeing the mission frees the director and every fx.
# Harness license (the mission_smoke/sprite_probe precedent, declared):
# the main core is HELD topped-up every combat frame (a probe-side
# write — breach costs scale with hp_max, so a boost alone is still
# 4-breaches-deep), green is topped up to fund the place leg, and the
# probe feeds extra spawn rows onto the real lane_g1 — everything else
# drives shipped entry points. The settle phase freezes the SIM (no
# new damage) and pumps only the director: fx lifetimes alone drain it.
# Machine rows: V5FX-MOUNT TRACER SPARK POOF ART CAP SETTLE TEARDOWN OK;
# any failure prints V5FX-FAIL <why> and quits 1.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

const HERO_IDS := ["warden", "deadeye", "embercaller"]
const TOWER_IDS := ["ballista", "bombard", "hailspire_tower"]
const FEED_IDS := ["skitterling", "husk_brute", "ash_bandit"]
const MAX_FX := 64                    # pinned from the director's own
                                      # cap constant (fleet lesson: the
                                      # probe states the expected, the
                                      # mechanism cannot move it)
const ART := {                        # fx id -> committed sheet path,
	"fx_proj_bolt": "res://assets/v11/fx_proj_bolt.png",
	"fx_proj_ice": "res://assets/v11/fx_proj_ice.png",
	"fx_spark_hit": "res://assets/v11/fx_spark_hit.png",
	"fx_poof_death": "res://assets/v11/fx_poof_death.png",
}   # (c) planted-red route: mis-pin an id in fx_director's PROJ_FOR
     # and the ART row goes RED on the live-node resource paths.


func _init() -> void:
	var seed_graph: Dictionary = GW_COMPOSE.build_graph(GW_TABLES.new("res://data"))
	seed_graph["state"].set_deck(HERO_IDS.duplicate())
	var packed = ResourceLoader.load("res://Main.tscn")
	if packed == null:
		_fail("Main.tscn not loadable")
		return
	var main = packed.instantiate()
	root.add_child(main)
	main._ready()                                  # E5 (no loop dispatch)
	main.start_mission("gatefall", "normal")       # the shipped router
	var m = main.mission
	if m == null or String(m.phase_kind) != "build":
		_fail("router start_mission did not land a mission")
		return

	# --- (a) the mount: scene child of the mission root, on the pinned
	#         script path (the tscn hook, not a probe-side add_child) ---
	var fx = m.get_node_or_null("FxDirector")
	if fx == null:
		_fail("mission.tscn does not ship FxDirector")
		return
	if String(fx.script.resource_path) != "res://scripts/fx_director.gd":
		_fail("FxDirector on wrong script: %s" % fx.script.resource_path)
		return
	if int(fx.get_index()) < int(m.get_node("EnemyRunner").get_index()):
		_fail("FxDirector mounts before EnemyRunner in the tree")
		return
	print("V5FX-MOUNT child=1 after_runner=1")

	m.core_main.hp_max *= 5.0                      # license (header)
	m.core_main.hp = m.core_main.hp_max
	var guard := 0
	while guard < 4000 and String(m.phase_kind) == "build":
		m.step(1.0 / 60.0)
		fx.fx_step(1.0 / 60.0)
		guard += 1
	if String(m.phase_kind) != "combat":
		_fail("combat never started")
		return
	m.green = 100000                               # license (header)
	var trows := {}
	for row: Dictionary in m.tables.rows("towers"):
		trows[String(row["id"])] = row
	# TWO of each shooter at the lane_g1 run-in (waypoints (-40,0,0)->
	# (-28,0,4)): T1 ranges 16/12/13 cover the walk through the cluster;
	# 6 guns keep deaths coming despite the feed (each type fires, so
	# BOTH projectile sheets are exercised every run).
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
	var runner = m.get_node("EnemyRunner")
	var lane: Dictionary = m.lanes["lane_g1"]

	# --- (b) the fight: feed lane_g1 with cheap enemies, pump the real
	#         step order, read counters + LIVE fx node textures ---
	var paths_seen := {}
	var live_max := 0
	var f := 0
	var feed_k := 0
	guard = 0
	while guard < 40000:
		guard += 1
		if f % 45 == 0:                            # license feed (header)
			runner.spawn({"enemy_id": FEED_IDS[feed_k % FEED_IDS.size()],
					"count": 1}, lane, m.enemy_defs, m.rng)
			feed_k += 1
		m.step(1.0 / 60.0)
		# License (header): the breach leg costs 25% of core hp_max PER
		# reach (balance.respawn_core_ratio, hp_max-proof), so a beefed
		# core is still 4 breaches from a loss — the probe HOLDS the
		# main core topped-up every frame (a probe-side write, the
		# v11_shot3 green/hp lever idiom; the director writes nothing).
		m.core_main.hp = m.core_main.hp_max
		fx.fx_step(1.0 / 60.0)
		f += 1
		live_max = maxi(live_max, fx.get_child_count())
		for c: Node in fx.get_children():
			var spr := c as Sprite3D
			if spr != null and spr.texture != null:
				paths_seen[String(spr.texture.resource_path)] = true
		if int(fx.spawned_tracers) >= 1 and int(fx.spawned_sparks) >= 1 \
				and int(fx.spawned_poofs) >= 1 and paths_seen.size() >= 4:
			break
		if m.outcome != null:
			_fail("mission ended before the fx legs were met (f=%d)" % f)
			return
	if int(fx.spawned_tracers) < 1:
		_fail("no tracer after %d combat frames" % guard)
		return
	print("V5FX-TRACER n=%d frames=%d" % [int(fx.spawned_tracers), guard])
	if int(fx.spawned_sparks) < 1:
		_fail("no damage spark after %d combat frames" % guard)
		return
	print("V5FX-SPARK n=%d" % int(fx.spawned_sparks))
	if int(fx.spawned_poofs) < 1:
		_fail("no death poof after %d combat frames" % guard)
		return
	print("V5FX-POOF n=%d" % int(fx.spawned_poofs))
	for fxid: String in ART.keys():
		if not paths_seen.has(String(ART[fxid])):
			_fail("fx sheet never seen on a live node (id=%s path=%s)" \
					% [fxid, String(ART[fxid])])
			return
	print("V5FX-ART n=4 paths=pinned")

	# --- (c) cap + self-free leak row: the high-water mark never passed
	#         the pinned cap; freeze the SIM (zero new damage -> zero new
	#         fx) and the director drains itself to its empty baseline ---
	if live_max > MAX_FX:
		_fail("live fx nodes passed the cap: %d > %d" % [live_max, MAX_FX])
		return
	if live_max < 2:
		_fail("never two fx live at once — cap/free legs vacuous: %d" \
				% live_max)
		return
	print("V5FX-CAP live_max=%d cap=%d" % [live_max, MAX_FX])
	var settle := 0
	while fx.get_child_count() > 0 and settle < 3000:
		fx.fx_step(1.0 / 60.0)                     # sim FROZEN (header)
		settle += 1
	if fx.get_child_count() != 0:
		_fail("fx did not free: %d children after settle" \
				% fx.get_child_count())
		return
	print("V5FX-SETTLE live_max=%d baseline=0 settle_frames=%d" \
			% [live_max, settle])

	# --- (d) teardown: mission cleanup frees the director with every fx
	#         (the children die with their parent — no orphan leaves) ---
	var kids: int = fx.get_child_count()
	m.free()
	if is_instance_valid(fx) or is_instance_valid(m):
		_fail("teardown m=%s fx=%s kids=%d" % [
				str(is_instance_valid(m)), str(is_instance_valid(fx)), kids])
		return
	print("V5FX-TEARDOWN freed=1 kids_at_free=%d" % kids)
	print("V5FX-OK")
	quit(0)


func _fail(why: String) -> void:
	print("V5FX-FAIL " + why)
	quit(1)
