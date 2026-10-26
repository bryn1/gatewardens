# hub_probe_stations — the REAL hub-scene legs of the hub probe (W16
# split of hub_probe.gd, MC 11274.1.28 / card 11384; legs authored W9 +
# W14, MC 11274.1.16/.25). Pure move — code and rows byte-identical.
#   WAR      the REAL hub.tscn under a RouterSpy: war_table.start calls
#            start_mission("gatefall","hard") (difficulty into the
#            shipped mission routing); Digit3 opens the blacksmith panel.
#   ASC      the ascension station over the REAL hub mount (W14 P1-3):
#            points earned through the shipped level mutator; every
#            refusal (unknown power, over the balance) is spend_asc's own
#            answer, never a panel-side copy; the spend rides the
#            station's OWN button signal; balance + per-node counts read
#            back off meta + the station's label. The EFFECT leg is
#            asserted at the pinned consumer site in the mission leg.
# Machine rows: WAR PANELS ASC (tests/test_hub.py re-derives the
# ascension numbers from ascension.json + xp.json).
extends RefCounted

const HUB_SCENE := "res://scenes/hub.tscn"


# Records the pinned war_table crossing start_mission(map_id, difficulty)
# exactly as the main.gd router would receive it (hub.get_parent() at
# runtime IS the main root — same call shape asserted here).
class RouterSpy:
	extends Node

	var calls: Array = []

	func start_mission(map_id: String, difficulty: String) -> void:
		calls.append({"map": map_id, "difficulty": difficulty})


static func run(probe, leg: Dictionary) -> bool:
	var state = probe.state
	var root = probe.root
	var hero0: String = String(leg["hero0"])

	# ---- WAR + PANELS legs: the REAL hub scene ----
	var spy = RouterSpy.new()
	spy.name = "RouterSpy"
	root.add_child(spy)
	var packed = ResourceLoader.load(HUB_SCENE)
	if packed == null:
		probe._fail("hub.tscn not loadable")
		return false
	var hub = packed.instantiate()
	spy.add_child(hub)
	hub._ready()                                   # E5: drive _ready (no-op)
	hub.setup(probe.tables, state, probe.save, probe.bridge, probe.rng)
	if hub.war.maps.is_empty() or String(hub.war.maps[0]["id"]) != "gatefall" \
			or not (hub.war.maps[0]["difficulties"] as Array).has("hard"):
		probe._fail("war table map data wrong: %s" % str(hub.war.maps))
		return false
	hub.war.start("gatefall", "hard")
	if spy.calls.size() != 1 or String(spy.calls[0]["map"]) != "gatefall" \
			or String(spy.calls[0]["difficulty"]) != "hard":
		probe._fail("war start crossing: %s" % str(spy.calls))
		return false
	var diffs := ""
	for d: Variant in hub.war.maps[0]["difficulties"]:
		diffs += String(d) + ","
	print("HUB-PROBE-WAR maps=gatefall:[%s] start=gatefall difficulty=hard" % diffs)
	hub.handle_press("Digit3")                     # greybox station code
	if not bool(hub.blacksmith.visible) or bool(hub.gear.visible):
		probe._fail("station routing: blacksmith=%s gear=%s" % [
				str(hub.blacksmith.visible), str(hub.gear.visible)])
		return false
	print("HUB-PROBE-PANELS open=blacksmith")

	# ---- ASC leg (W14 P1-3, MC 11274.1.25 / card 11341): the ascension
	#      station over the REAL hub mount. Points are earned through the
	#      shipped level mutator; every refusal (unknown power, over the
	#      balance) is spend_asc's own answer, never a panel-side copy;
	#      the spend rides the station's OWN button signal; the balance
	#      and per-node counts read back off meta + the station's label.
	#      The EFFECT leg is asserted at the pinned consumer site in the
	#      mission leg (mission setup applies the tree modifier —
	#      blue_max row).
	var asc_json: Dictionary = probe.tables.table("ascension")
	var asc_tree: Dictionary = asc_json["tree"]
	var per_level := int(asc_json["points_per_level"])
	state.add_hero_xp(hero0, int(probe.tables.table("xp")["hero_curve"][0]))
	var asc_earned := int(state.asc_earned)
	var asc_unknown_no: bool = state.spend_asc(asc_tree, "no_such_power", 1)
	var asc_over_no: bool = state.spend_asc(asc_tree, "iron_will", asc_earned + 1)
	if asc_earned != per_level or bool(asc_unknown_no) or bool(asc_over_no) \
			or not state.asc_spent.is_empty():
		probe._fail("asc earn/refusals: earned=%d unknown=%s over=%s spent=%s" % [
				asc_earned, str(asc_unknown_no), str(asc_over_no),
				str(state.asc_spent)])
		return false
	hub._open("ascension")
	if not bool(hub.ascension.visible) or bool(hub.blacksmith.visible):
		probe._fail("ascension station routing wrong: %s" % str(hub._panels))
		return false
	var spend_btn = hub.ascension.get_node(
			"Ascension/Trees/Power_reservoir/Spend_reservoir")
	spend_btn.pressed.emit()                    # the station's own control
	var res_pts := int(state.asc_spent.get("reservoir", 0))
	hub.ascension.refresh()
	if res_pts != 1 or hub.ascension.available() != 0 \
			or not bool(spend_btn.disabled):
		probe._fail("asc spend: pts=%d avail=%d grey=%s" % [
				res_pts, hub.ascension.available(), str(spend_btn.disabled)])
		return false
	print("HUB-PROBE-ASC earned=%d refused_unknown=1 refused_over=1 spent=1 available=%d station=visible" % [
			asc_earned, hub.ascension.available()])
	leg["asc_earned"] = asc_earned
	leg["res_pts"] = res_pts
	return true
