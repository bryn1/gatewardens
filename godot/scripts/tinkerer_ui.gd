extends Control

# tinkerer_ui — mod-transfer station (Modules row scripts/tinkerer_ui.gd,
# MC 11274.1.16 / card 11323). The whole transfer decision is the shipped
# SimInventory.tinkering static: mod index validity, the declared
# mod_slots cap (rarity.json mod_slots via the sim's mod_slots()) and the
# material affordability all gate INSIDE it, and on ok the mod moves
# in place on both caller-owned rows. The panel adds only the gold gate
# BEFORE the call (tinkering mutates on ok, so the can_afford gate rides
# the declared tinkering gold — a data read through the shipped static,
# the W8 panel idiom, never arithmetic, I4) and pays afterwards through
# the BN2/F2-6 GameState mutators only (C13 rides `mutated`).
#
# setup(tables, game_state, rng): the rng is the pinned F2-2 setup param
# (hub rolls have a named owner); the shipped tinkering static draws
# nothing, so the panel holds the rng without consuming it (declared —
# the signature is the table's, the draw would be data's to request).
#
# Source/target pickers are lists of the SHARED item_row scene (F2-12):
# one list-build implementation beside the gear and blacksmith panels.

const BANK_LIST := preload("res://scripts/bank_list.gd")
const SIM_INVENTORY := preload("res://sim/sim_inventory.gd")
const SIM_ECONOMY := preload("res://sim/sim_economy.gd")

var tables = null
var state = null
var rng = null                  # pinned F2-2 param; tinkering draws nothing
var ctx: Dictionary = {}        # {stem: data} dict SimInventory.tinkering reads
var source_uid := 0
var target_uid := 0
var mod_i := 0                  # which of the source's mods to move
var buttons: Dictionary = {}
var _info_label = null
var _source_list = null
var _target_list = null


func setup(tables_in, game_state, rng_in) -> void:
	tables = tables_in
	state = game_state
	rng = rng_in
	ctx = {"blacksmith": tables.table("blacksmith"),
		"rarity": tables.table("rarity")}
	var box := VBoxContainer.new()
	box.name = "Tinkerer"
	add_child(box)
	var title := Label.new()
	title.text = "TINKERER — mod transfer"
	box.add_child(title)
	_info_label = Label.new()
	_info_label.name = "Costs"
	box.add_child(_info_label)
	_source_list = _picker(box, "Source")
	_target_list = _picker(box, "Target")
	var b := Button.new()
	b.name = "Transfer"
	b.text = "Transfer"
	b.pressed.connect(_on_transfer)
	box.add_child(b)
	buttons["transfer"] = b
	state.mutated.connect(refresh)
	refresh()


func set_source(uid: int) -> void:
	source_uid = int(uid)
	mod_i = 0                   # re-picking the source re-arms its first mod
	refresh()


func set_target(uid: int) -> void:
	target_uid = int(uid)
	refresh()


func select_mod(i: int) -> void:
	mod_i = int(i)


# The one transfer crossing: gate gold (the pre-call peek, header), then
# let the shipped static decide + move, then pay through the mutators.
func transfer() -> Dictionary:
	var source: Variant = _bank_row(source_uid)
	var target: Variant = _bank_row(target_uid)
	if source == null or target == null or source == target:
		return {"ok": false, "why": "row"}
	if not SIM_ECONOMY.can_afford(int(state.gold),
			int(ctx["blacksmith"]["tinkering"]["gold"])):
		return {"ok": false, "why": "gold"}
	var res: Dictionary = SIM_INVENTORY.tinkering(source, target, mod_i,
			ctx, state.materials)
	if bool(res["ok"]):
		_pay(res["cost"])
	return res


func refresh() -> void:
	var svc: Dictionary = ctx["blacksmith"]["tinkering"]
	_info_label.text = "transfer %d gold + declared materials" % int(svc["gold"])
	_fill(_source_list, source_uid)
	_fill(_target_list, target_uid)
	buttons["transfer"].disabled = source_uid <= 0 or target_uid <= 0


func _picker(box, label: String) -> VBoxContainer:
	var head := Label.new()
	head.text = label
	box.add_child(head)
	var rows := VBoxContainer.new()
	rows.name = "Rows_" + label
	box.add_child(rows)
	return rows


func _fill(list_box: VBoxContainer, marked_uid: int) -> void:
	# The ONE fill loop (bank_list, W16); bind() appends the box name so
	# _on_picked routes the pick back to the RIGHT list.
	BANK_LIST.fill(list_box, tables, state.bank, marked_uid,
			_on_picked.bind(list_box.name))


func _on_picked(uid: int, box_name: String) -> void:
	# bind() appends the picked box name AFTER the signal's uid argument.
	if box_name == "Rows_Source":
		set_source(uid)
	else:
		set_target(uid)


func _on_transfer() -> void:
	transfer()
	refresh()


func _pay(cost: Dictionary) -> void:
	state.spend_gold(int(cost["gold"]))
	for id: String in cost["materials"]:
		state.consume_material(id, int(cost["materials"][id]))


func _bank_row(uid: int) -> Variant:
	if uid <= 0:
		return null
	for row: Dictionary in state.bank:
		if int(row.get("uid", 0)) == uid:
			return row
	return null
