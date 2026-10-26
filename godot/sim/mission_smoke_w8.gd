# mission_smoke_w8 — the W8 defense legs of the mission smoke (W16 split
# of mission_smoke.gd, MC 11274.1.28 / card 11384; legs authored W8,
# MC 11274.1.15 / card 11322). Pure move — code and rows byte-identical
# to the pre-split file except three comment-word renames (price -> cost,
# the I1 vocabulary discipline). Runs in the build phase; every
# cost/refund is asserted against the data files by the pytest leg,
# never decided from literals here.
# Machine rows (pytest re-derives each number from towers/economy):
#   MISSION-SMOKE-W8PLACE class=tower cost=<c> green=<g> tier=1 (green
#                          drops EXACTLY the towers.json base_cost)
#   MISSION-SMOKE-W8UPGRADE cost=<c> dps=<d> green=<g> (T1->T2 ladder
#                          cost + the dps rise, both from data)
#   MISSION-SMOKE-W8REPAIR missing=0.5 cost=<c> green=<g> hp=<h>
#   MISSION-SMOKE-W8REPAIR1 cost=<c> green=<g> (floor-1 leg: missing=1/hp_max)
#   MISSION-SMOKE-W8PLACE2 class=blockade cost=<c> green=<g>
#   MISSION-SMOKE-W8CAP why=cap green=<g> count=<n> (cap+1 refused, green
#                          unchanged — harness cap write, boot_probe license)
#   MISSION-SMOKE-W8SELL refund=<r> green=<g> count=<n> (damaged defense:
#                          total_spent x sell_ratio x missing, R1 pinned)
#   MISSION-SMOKE-W8FREESLOT class=trap cost=<c> green=<g> charges=<t>
#   MISSION-SMOKE-W8PANEL classes=<a|b|c> gate=<n-affordable at trap cost>
#   MISSION-SMOKE-W8PANEL-ACT refund=<r> cost=<c> green=<g> (panel routes
#                          through placer/obj APIs — bridge-code presses)
extends RefCounted

const DEF_PLACER := preload("res://scripts/defense_placer.gd")


static func run(smoke, leg: Dictionary) -> bool:
	var m = leg["m"]
	var panel = leg["panel"]
	var start_green: int = int(leg["start_green"])
	# --- W0) W8 defense legs (MC 11274.1.15 / card 11322), all in the
	#        build phase; every cost/refund is asserted against the data
	#        files by the pytest leg, never decided from literals here.
	var placer = DEF_PLACER.new()
	placer.setup(m)
	var blockade_row: Dictionary = placer.row_for("blockade")
	var trap_row: Dictionary = placer.row_for("trap")
	if blockade_row.is_empty() or trap_row.is_empty() \
			or placer.row_for("tower").is_empty():
		smoke._fail("towers.json class rows missing")
		return false
	var slot_t := placer.slot_at(m.lanes["lane_g3"]["wps"][0])
	var slot_b := placer.slot_at(m.lanes["lane_g2"]["wps"][2])
	var slot_a := placer.slot_at(m.lanes["lane_g1"]["wps"][0])
	if slot_t < 0 or slot_b < 0 or slot_a < 0 or slot_a == slot_b:
		smoke._fail("lane-geometry buildable slots missing")
		return false
	var pres := placer.place("tower", 1, slot_t)
	if not bool(pres["ok"]) or int(m.green) != start_green - int(pres["cost"]):
		smoke._fail("W8 place: ok=%s green=%d" % [str(pres["ok"]), m.green])
		return false
	print("MISSION-SMOKE-W8PLACE class=tower cost=%d green=%d tier=1" % [
			int(pres["cost"]), m.green])
	var tower_uid := int(pres["uid"])
	var tower_obj = _w8obj(m, tower_uid)
	var dps1: float = tower_obj.dps()
	var ures := placer.upgrade(tower_uid)
	var dps2: float = tower_obj.dps()
	if not bool(ures["ok"]) or int(m.green) != start_green \
			- int(pres["cost"]) - int(ures["cost"]) or dps2 <= dps1:
		smoke._fail("W8 upgrade: %s dps %s->%s green=%d" % [
				str(ures), str(dps1), str(dps2), m.green])
		return false
	print("MISSION-SMOKE-W8UPGRADE cost=%d dps=%.2f green=%d" % [
			int(ures["cost"]), dps2, m.green])
	tower_obj.take_damage(tower_obj.hp_max * 0.5)   # harness half-missing leg
	var rres := placer.repair(tower_uid)
	if not bool(rres["ok"]) or float(tower_obj.hp) != float(tower_obj.hp_max):
		smoke._fail("W8 repair: %s hp=%s" % [str(rres), str(tower_obj.hp)])
		return false
	print("MISSION-SMOKE-W8REPAIR missing=0.5 cost=%d green=%d hp=%s" % [
			int(rres["cost"]), m.green, str(tower_obj.hp)])
	tower_obj.take_damage(1.0)                      # floor-1 leg (<1 rounds to 0)
	var fres := placer.repair(tower_uid)
	if not bool(fres["ok"]) or int(fres["cost"]) != 1:
		smoke._fail("W8 repair floor-1: %s" % str(fres))
		return false
	print("MISSION-SMOKE-W8REPAIR1 cost=%d green=%d" % [int(fres["cost"]), m.green])
	var bres := placer.place("blockade", 1, slot_b)
	if not bool(bres["ok"]):
		smoke._fail("W8 blockade place: %s" % str(bres))
		return false
	print("MISSION-SMOKE-W8PLACE2 class=blockade cost=%d green=%d" % [
			int(bres["cost"]), m.green])
	# Cap boundary: harness writes the cap DOWN to the live count (the
	# boot_probe drive-real-entry-points license) so the NEXT place is the
	# pinned cap+1 refusal; green must not move.
	m.defense_cap = m.defense_list.size()
	var g_before := int(m.green)
	var cres := placer.place("blockade", 1, slot_a)
	if String(cres["why"]) != "cap" or int(m.green) != g_before \
			or m.defense_list.size() != m.defense_cap:
		smoke._fail("W8 cap+1: %s green=%d count=%d" % [
				str(cres), m.green, m.defense_list.size()])
		return false
	print("MISSION-SMOKE-W8CAP why=cap green=%d count=%d" % [
			m.green, m.defense_list.size()])
	var block_obj = _w8obj(m, int(bres["uid"]))
	block_obj.take_damage(block_obj.hp_max * 0.5)   # damaged -> refund > 0
	var g_pre_sell := int(m.green)
	var sres := placer.sell(int(bres["uid"]))
	if not bool(sres["ok"]) or m.defense_list.size() != 1 \
			or int(m.green) != g_pre_sell + int(sres["refund"]):
		smoke._fail("W8 sell: %s green=%d count=%d" % [
				str(sres), m.green, m.defense_list.size()])
		return false
	print("MISSION-SMOKE-W8SELL refund=%d green=%d count=%d" % [
			int(sres["refund"]), m.green, m.defense_list.size()])
	var tres := placer.place("trap", 1, slot_b)     # the freed slot, exact-cost
	if not bool(tres["ok"]) or int(m.green) != g_pre_sell + int(sres["refund"]) \
			- int(tres["cost"]):
		smoke._fail("W8 sell frees no cap slot: %s green=%d" % [str(tres), m.green])
		return false
	var trap_obj = _w8obj(m, int(tres["uid"]))       # affordability edge
	print("MISSION-SMOKE-W8FREESLOT class=trap cost=%d green=%d charges=%d" % [
			int(tres["cost"]), m.green, int(trap_obj.charges)])
	# Panel leg: functional greybox Control — lists v1 classes, gates by
	# can_afford, and its actions route THROUGH the placer/obj APIs. The
	# gate count rides a harness green write at exactly the trap cost
	# (the two data-cheap classes affordable, the tower class not).
	# W14 (MC 11274.1.25): this leg drives the SAME panel the mission
	# mounted at setup (reuse-first; the pre-W14 smoke instantiated its
	# own second panel around the live one).
	m.green = int(trap_row["base_cost"])
	panel.refresh()
	var ids: Array = []
	for crow: Dictionary in panel.class_rows:
		ids.append(String(crow["class"]))
	var enabled := 0
	for cid: String in panel.class_buttons:
		if not bool(panel.class_buttons[cid].disabled):
			enabled += 1
	print("MISSION-SMOKE-W8PANEL classes=%s gate=%d" % ["|".join(ids), enabled])
	var ps0 := int(m.green)
	panel.select_defense(int(tres["uid"]))
	panel.handle_press("KeyN")        # sell the full-HP trap: pinned refund 0
	var w8_refund := int(m.green) - ps0
	panel.select_class(1)             # data order: tower, blockade, trap
	panel.handle_press("KeyM")        # place blockade, first free slot
	var p_cost := ps0 - int(m.green)
	if w8_refund != 0 or p_cost != int(blockade_row["base_cost"]) \
			or m.defense_list.size() != int(m.defense_cap):
		smoke._fail("W8 panel actions: refund=%d cost=%d count=%d" % [
				w8_refund, p_cost, m.defense_list.size()])
		return false
	print("MISSION-SMOKE-W8PANEL-ACT refund=%d cost=%d green=%d" % [
			w8_refund, p_cost, m.green])
	leg["w8_left"] = int(m.green)     # the wave-award formula's green base
	return true


static func _w8obj(m, uid: int):
	for rec: Dictionary in m.defense_list:
		if int(rec["uid"]) == uid:
			return rec["obj"]
	return null
