# hub_probe_equip — the EQUIP leg of the hub probe (W16 split of
# hub_probe.gd, MC 11274.1.28 / card 11384; leg authored W9 + W14,
# MC 11274.1.16/.25). Pure move — code and rows byte-identical.
# gear panel -> the shipped equip crossing: bank->equipped; a replaced
# row returns to the bank INSIDE equip (F2-11, asserted twice — the swap
# and the re-equip); a relic row is listed (it rides the same item_row
# widget) but hero-slot equip is the shipped refusal (F2-12/C11).
# Machine row:
#   HUB-PROBE-EQUIP bank_after_first=<n> bank_after_swap=<n> returned=<uid>
#                   equipped=<base_id> relic_refused=1 bank_after_relic=<n>
#                   unknown_refused=1 (W14 P2-10: uid not in the bank ->
#                   pinned {ok:false,bank} refusal, bank AND worn row kept)
extends RefCounted

const GEAR_PANEL := preload("res://scripts/gear_panel_ui.gd")
const SIM_INV := preload("res://sim/sim_inventory.gd")


static func run(probe, leg: Dictionary) -> bool:
	var state = probe.state
	var root = probe.root
	var item_a: Dictionary = leg["item_a"]
	var item_b: Dictionary = leg["item_b"]
	var relic_spec: Dictionary = leg["relic_spec"]
	var deck: Array = leg["deck"]
	# ---- EQUIP leg: gear panel -> the shipped equip crossing ----
	var gear = GEAR_PANEL.new()
	root.add_child(gear)
	gear.setup(probe.tables, state)
	var uid_a := int(state.bank[0]["uid"])
	var uid_b := int(state.bank[1]["uid"])
	gear.pick(uid_a)
	if not gear.equip_selected("warden", "weapon") \
			or state.bank.size() != 1 or int(state.bank[0]["uid"]) != uid_b:
		probe._fail("equip first: bank=%s" % str(state.bank))
		return false
	var bank_first := int(state.bank.size())
	gear.pick(uid_b)
	if not gear.equip_selected("warden", "weapon") \
			or state.bank.size() != 1:
		probe._fail("equip swap: bank=%s" % str(state.bank.size()))
		return false
	# F2-11: the replaced row A returned INTO the bank inside equip.
	var returned: bool = probe._bank_index_of(String(item_a["base_id"])) >= 0
	var worn: Dictionary = state.equipped["warden"]["weapon"]
	if not returned or String(worn.get("base_id", "")) != String(item_b["base_id"]):
		probe._fail("equip swap: returned=%s worn=%s" % [
				str(returned), str(worn.get("base_id", ""))])
		return false
	var bank_swap := int(state.bank.size())
	# F2-12/C11: a relic row is listed (it rides the same item_row widget)
	# but hero-slot equip is the shipped refusal — bank untouched.
	state.bank_add(probe._scripted_item(relic_spec))
	var relic_row: Dictionary = state.bank[probe._bank_index_of(String(relic_spec["base_id"]))]
	gear.pick(int(relic_row["uid"]))
	var relic_ok := gear.equip_selected("warden", "weapon")
	if relic_ok or state.bank.size() != 2:
		probe._fail("relic equip not refused: ok=%s bank=%d" % [
				str(relic_ok), state.bank.size()])
		return false
	# P2-10 (W14, MC 11274.1.25): an equip over a uid the bank does NOT
	# hold is refused in the pinned {ok,bank} shape — ok only when a row
	# actually left the bank (the shipped equip static is the site; the
	# ghost row below is weapon-shaped so the slot gate cannot mask it).
	var ghost: Dictionary = state.equipped["warden"]["weapon"].duplicate(true)
	ghost["uid"] = int(ghost["uid"]) + 100000
	var bank_p210 := int(state.bank.size())
	var raw_p210: Dictionary = SIM_INV.equip(state.bank.duplicate(), String(deck[0]), ghost)
	var ghost_ok: bool = state.equip(String(deck[0]), "weapon", ghost)
	if bool(raw_p210["ok"]) or ghost_ok or int(state.bank.size()) != bank_p210 \
			or int(state.equipped[String(deck[0])]["weapon"].get("uid", 0)) \
			== int(ghost["uid"]):
		probe._fail("P2-10: unknown-uid equip ok raw=%s panel=%s bank=%d" % [
				str(raw_p210["ok"]), str(ghost_ok), state.bank.size()])
		return false
	print(("HUB-PROBE-EQUIP bank_after_first=%d bank_after_swap=%d returned=%d "
			+ "equipped=%s relic_refused=1 bank_after_relic=%d unknown_refused=1") % [
			bank_first, bank_swap, uid_a, String(worn["base_id"]),
			int(state.bank.size())])
	leg["gear"] = gear
	leg["uid_a"] = uid_a
	leg["uid_b"] = uid_b
	return true
