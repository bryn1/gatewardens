extends Control

# blacksmith_ui — Upgrade / Evolve / Reroll station (Modules row
# scripts/blacksmith_ui.gd, MC 11274.1.16 / card 11323). PURE UI: every
# decision is a shipped static — SimInventory.svc_upgrade/svc_evolve/
# svc_reroll gate the leg against blacksmith.json and the CURRENT
# material counts and compute the {gold,materials} cost; SimEconomy.
# can_afford is the gold gate (the W8 defense_panel idiom: a shipped
# static decides affordability, the panel never does arithmetic, I4);
# the bill is paid ONLY through the BN2 GameState mutators spend_gold /
# consume_material — each emits `mutated`, so C13 carries the service
# result to the save with no second write mechanism.
#
# Cost-peek before svc (declared): svc_reroll re-rolls the row IN PLACE
# at call time, so its gold gate must be checked BEFORE the call — the
# panel peeks the declared reroll gold (a data read, not math) and gates
# with can_afford; upgrade/evolve never mutate, so their gate rides the
# sim's own returned cost. svc_evolve's ok already excludes the ladder
# top, so the caller's ladder step is index+1 — the rung data stays in
# rarity.json (no name list here, I2).
#
# Bank-list rows come from the SHARED item_row scene (F2-12) — the same
# widget the gear panel instantiates, one list-build implementation.
# setup(tables, game_state, rng): the rng is main.gd's ONE runtime RNG
# (F2-2), handed straight to svc_reroll as the sanctioned draw owner.

const ITEM_ROW := preload("res://scenes/item_row.tscn")
const SIM_INVENTORY := preload("res://sim/sim_inventory.gd")
const SIM_ECONOMY := preload("res://sim/sim_economy.gd")

var tables = null
var state = null
var rng = null
var ctx: Dictionary = {}        # the plain {stem: data} dict the SimInventory statics read
var selected_uid := 0
var _list_box = null
var _cost_label = null
var buttons: Dictionary = {}    # action -> Button


func setup(tables_in, game_state, rng_in) -> void:
	tables = tables_in
	state = game_state
	rng = rng_in
	ctx = {"blacksmith": tables.table("blacksmith"),
		"rarity": tables.table("rarity"),
		"items": _load_array("items"), "mods": _load_array("mods")}
	var box := VBoxContainer.new()
	box.name = "Blacksmith"
	add_child(box)
	var title := Label.new()
	title.text = "BLACKSMITH"
	box.add_child(title)
	_cost_label = Label.new()
	_cost_label.name = "Costs"
	box.add_child(_cost_label)
	_list_box = VBoxContainer.new()
	_list_box.name = "Bank"
	box.add_child(_list_box)
	for action: String in ["upgrade", "evolve", "reroll"]:
		var b := Button.new()
		b.name = action.to_pascal_case()
		b.text = action.to_pascal_case()
		b.pressed.connect(_on_action.bind(action))
		box.add_child(b)
		buttons[action] = b
	state.mutated.connect(refresh)
	refresh()


func pick(uid: int) -> void:
	selected_uid = int(uid)
	refresh()


func upgrade(uid: int) -> Dictionary:
	var row: Variant = _bank_row(uid)
	if row == null:
		return {"ok": false, "why": "row"}
	var res: Dictionary = SIM_INVENTORY.svc_upgrade(row, ctx, state.materials)
	if not bool(res["ok"]) \
			or not SIM_ECONOMY.can_afford(int(state.gold), int(res["cost"]["gold"])):
		res["ok"] = false
		return res
	row["upgraded"] = int(row["upgraded"]) + 1   # the sim's stated caller-side level
	_pay(res["cost"])
	return res


func evolve(uid: int) -> Dictionary:
	var row: Variant = _bank_row(uid)
	if row == null:
		return {"ok": false, "why": "row"}
	var res: Dictionary = SIM_INVENTORY.svc_evolve(row, ctx, state.materials)
	if not bool(res["ok"]) \
			or not SIM_ECONOMY.can_afford(int(state.gold), int(res["cost"]["gold"])):
		res["ok"] = false
		return res
	var ladder: Array = ctx["rarity"]["ladder"]
	# one ladder step up (pinned wording); svc_evolve.ok already proved
	# the rung exists below the ladder top.
	row["rarity"] = String(ladder[ladder.find(String(row["rarity"])) + 1])
	_pay(res["cost"])
	return res


func reroll(uid: int) -> Dictionary:
	var row: Variant = _bank_row(uid)
	if row == null:
		return {"ok": false, "why": "row"}
	if not SIM_ECONOMY.can_afford(int(state.gold),
			int(ctx["blacksmith"]["reroll"]["gold"])):
		return {"ok": false, "why": "gold"}
	# svc_reroll re-rolls the row in place and returns the gold-only bill.
	var res: Dictionary = SIM_INVENTORY.svc_reroll(row, rng, ctx)
	_pay(res["cost"])
	return res


func refresh() -> void:
	var svc: Dictionary = ctx["blacksmith"]
	_cost_label.text = ("upgrade %d gold + declared mats | evolve %d "
			+ "gold + declared mats | reroll %d gold") % [
			int(svc["upgrade"]["gold_by_rarity"].get(
					String(_selected_row().get("rarity", "")), 0)),
			int(svc["evolve"]["gold"]), int(svc["reroll"]["gold"])]
	_clear(_list_box)
	for row: Dictionary in state.bank:
		var item = ITEM_ROW.instantiate()
		item.name = "Row_%d" % int(row.get("uid", 0))
		item.bind(tables)
		item.show_item(row, int(row.get("uid", 0)) == selected_uid)
		item.picked.connect(_on_picked)
		_list_box.add_child(item)
	for action: String in buttons:
		buttons[action].disabled = _selected_row().is_empty()


func _on_picked(uid: int) -> void:
	pick(uid)


func _on_action(action: String) -> void:
	match action:
		"upgrade":
			upgrade(selected_uid)
		"evolve":
			evolve(selected_uid)
		"reroll":
			reroll(selected_uid)
	refresh()


# The ONE payment crossing: BN2 gold mutator + F2-6 material mutator,
# each emitting `mutated` (C13). svc.ok already checked the materials and
# the can_afford gate the gold, so a refusal can never half-pay.
func _pay(cost: Dictionary) -> void:
	state.spend_gold(int(cost["gold"]))
	for id: String in cost["materials"]:
		state.consume_material(id, int(cost["materials"][id]))


func _selected_row() -> Dictionary:
	var row: Variant = _bank_row(selected_uid)
	return row if row is Dictionary else {}


func _bank_row(uid: int) -> Variant:
	if uid <= 0:
		return null
	for row: Dictionary in state.bank:
		if int(row.get("uid", 0)) == uid:
			return row
	return null


func _clear(node: Node) -> void:
	for child: Node in node.get_children():
		child.free()


func _load_array(stem: String) -> Array:
	# Array-shaped data files have no GWTables dict door (the mission.gd
	# _load_array precedent); svc_reroll reads the declared base pools.
	var text := FileAccess.get_file_as_string("res://data/" + stem + ".json")
	var parsed: Variant = JSON.parse_string(text)
	return parsed if parsed is Array else []
