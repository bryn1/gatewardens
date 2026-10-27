extends Control

# gear_panel_ui — hub gear panel (Modules row scripts/gear_panel_ui.gd,
# MC 11274.1.16 / card 11323): the bank list built from FOUR slot-
# sections of shared item_row instances (weapon/armor/ring/relic — the
# pinned row's "4 slot-sections", F2-12), plus one row of slot buttons
# per deck hero (weapon/armor/ring, the C5 `equipped` fields). The click
# crossing is the pinned one: pick a bank item, press a compatible hero
# slot -> GameState.equip(hero,slot,item). Replace-return is NOT panel
# logic — SimInventory.equip owns the {ok,bank} F2-11 contract and
# GWGameState.equip merges the worn row back into the bank; this file
# calls the shipped mutator and NOTHING else (pure UI: zero cost math,
# zero sim imports).
#
# Readings recorded on the card trail:
# - Unequip/salvage: the W9 brief paraphrases SimInventory statics
#   named "unequip"/"salvage_yield" — neither exists in the shipped
#   sim_inventory contract (the pinned table wins, MC 11274.1.9-.15
#   precedent) and no data file declares a salvage value, so building
#   one here would invent an undeclared number (I2) and a mutator the
#   pinned game_state row does not name. NOT faked — declared open; the
#   v1 return path IS equip's replace-to-bank.
# - Relic rows are listed and BADGED (slot "relic", C11 tower gear) but
#   a hero-slot press over one is refused by the shipped equip (ok:false,
#   bank untouched) — the refusal is the pinned mechanism, asserted by
#   the hub_probe EQUIP leg.
# - An empty deck renders a placeholder: deck selection is the HUD row
#   (the C6 deck_json array order is the sole source read here).
# - Greybox Control styling per the defense_panel precedent; full HUD
#   styling is the named frontend row.

const BANK_LIST := preload("res://scripts/bank_list.gd")

const SECTIONS := ["weapon", "armor", "ring", "relic"]   # pinned 4 slot-sections
const HERO_SLOTS := ["weapon", "armor", "ring"]          # C5 equipped slots

var tables = null
var state = null
var selected_uid := 0
var _lists: Dictionary = {}       # section id -> row VBoxContainer
var _hero_box = null


func setup(tables_in, game_state) -> void:
	tables = tables_in
	state = game_state
	var box := VBoxContainer.new()
	box.name = "Gear"
	add_child(box)
	for section: String in SECTIONS:
		var head := Label.new()
		head.name = "Head_" + section
		head.text = section.to_upper()
		box.add_child(head)
		var rows := VBoxContainer.new()
		rows.name = "Rows_" + section
		box.add_child(rows)
		_lists[section] = rows
	var deck_head := Label.new()
	deck_head.text = "DECK"
	box.add_child(deck_head)
	_hero_box = VBoxContainer.new()
	_hero_box.name = "Heroes"
	box.add_child(_hero_box)
	# E1-safe anchor: this Node lives in the tree; every C13 meta-write
	# repaints the bank (the same signal the save rides, no new trigger).
	state.mutated.connect(refresh)
	refresh()


# ---------- pinned crossing: pick item -> press compatible slot ----------

func pick(uid: int) -> void:
	selected_uid = int(uid)
	refresh()


# The one equip application crossing: GameState.equip delegates to
# SimInventory.equip — {ok,bank} and replace-to-bank stay there (F2-11).
func equip_selected(hero: String, slot: String) -> bool:
	var row: Variant = _bank_row(selected_uid)
	if row == null:
		return false
	var ok: bool = state.equip(hero, slot, row)
	refresh()
	return ok


# Rows currently shown (the hub_probe bank-after-chest leg reads this).
func shown_rows() -> int:
	var total := 0
	for section: String in SECTIONS:
		total += _lists[section].get_child_count()
	return total


func refresh() -> void:
	# Rows bucket by their declared slot FIRST (rows of other slots never
	# enter a section); each section then rides the ONE fill loop
	# (bank_list, W16) — which clears its box before filling, so a
	# bucket that went empty this refresh shows nothing stale.
	var bucket: Dictionary = {}
	for s: String in SECTIONS:
		bucket[s] = []
	for row: Dictionary in state.bank:
		var section := String(row.get("slot", ""))
		if bucket.has(section):
			bucket[section].append(row)
	for s: String in SECTIONS:
		BANK_LIST.fill(_lists[s], tables, bucket[s], selected_uid,
				_on_picked)
	_rebuild_heroes()


func _on_picked(uid: int) -> void:
	pick(uid)


func _rebuild_heroes() -> void:
	_clear(_hero_box)
	if state.deck.is_empty():
		var wait := Label.new()
		wait.text = "deck empty — deck select ships with the HUD row"
		_hero_box.add_child(wait)
		return
	for entry: Variant in state.deck:
		var hero := String(entry)
		var row := HBoxContainer.new()
		row.name = "Hero_" + hero
		var hero_name := Label.new()
		hero_name.text = hero
		row.add_child(hero_name)
		for slot: String in HERO_SLOTS:
			var worn: Variant = state.equipped.get(hero, {}).get(slot)
			var b := Button.new()
			b.name = "Slot_%s_%s" % [hero, slot]
			b.text = "%s: %s" % [slot,
					String(worn["base_id"]) if worn != null else "-"]
			b.pressed.connect(_on_slot.bind(hero, slot))
			row.add_child(b)
		_hero_box.add_child(row)


func _on_slot(hero: String, slot: String) -> void:
	equip_selected(hero, slot)


func _bank_row(uid: int) -> Variant:
	if uid <= 0:
		return null
	for row: Dictionary in state.bank:
		if int(row.get("uid", 0)) == uid:
			return row
	return null


func _clear(node: Node) -> void:
	# E9 (the shipped defense_panel/bank_list idiom, MC 11274.1.30/.32):
	# a hero slot Button can be the very object emitting `pressed` when
	# the equip crossing repaints (slot press -> _on_slot ->
	# equip_selected -> state.equip -> refresh -> _clear), and free() on
	# a locked (mid-emit) object is an engine ERROR (VERIFIED this card,
	# served pck 244392 — the console "Object ... was freed or
	# unreferenced while a signal is being emitted"): the abort kills
	# the refresh. Detach NOW (no flicker) + queue_free — the free lands
	# at frame end, after the emit has unwound.
	for child: Node in node.get_children():
		node.remove_child(child)
		child.queue_free()
