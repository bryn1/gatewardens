# defense_rows_ui — the defense panel's ROW-LIST UI (v1.2.1 S split, MC
# 11699 / V121-PLAN §3 C-1 FULL MOVE): the class/family picker button
# build (V4/V6/F4), the DEFENSES + RELICS section heads and containers,
# the W17c selectable-row clear+rebuild, the W17e selected-mark pass and
# the W17e dirty check — all MOVED whole out of defense_panel.gd (pure
# move: bodies byte-identical, the mission_world.gd W16 gate idiom). No
# second copy stays behind: defense_panel.gd instantiates and delegates
# (its `rows_ui`), and the coupled gate tests/test_mission_stale.py is
# retargeted to THIS home in the same commit (pin #10 — the sibling also
# joins GOVERNED_LITERALS in tools/check_hygiene.py, same commit).
# extends RefCounted (the bank_list.gd idiom): the helper is NOT a tree
# Node — it injects its controls into the panel's shared "Rows" box, so
# the shipped path DefensePanel/Rows/Rows_defenses (the stale/clicks
# probes' get_node address) is byte-identical to before the split.
# Pure UI: no cost math, no formulas here (I2; every gate is the shipped
# static, read through the panel).
extends RefCounted

const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")
const UITWEEN := preload("res://scripts/ui_tween.gd")

# V4 (MC 11549 / VISUAL-TARGET row V4): class-id -> icon id, explicit
# (the sprite_bank sheet-map idiom — never a stem rule). All five tower
# ids carry an icon so the declared family picker (defense_placer
# header) rides rows that already resolve; the shipped classes() list
# shows the class winners (tower/blockade/trap). Decoration only: the
# Button.icon scales WITH the button under ui_tween.attach (V6) and
# sync() never touches icons — texts, handlers, signals unchanged.
const ICON_FOR := {
	"ballista": "icon_ballista", "bombard": "icon_bombard",
	"hailspire_tower": "icon_hailspire", "gate_blockade": "icon_blockade",
	"barbed_snare": "icon_snare",
}

var panel = null                   # the owning defense_panel: selection
                                   # state + press handlers route there
var m = null                       # mission: defense_list/tables reads
var relic_rows = null              # shared item_row list over the pool
var defense_rows = null            # W17c: selectable rows (defense list)
var _rows_uids: Array = []         # W17e: uids the rows were last built
                                   # for — the rebuild dirty check


# One-call wiring; the panel injects itself (the selection state and the
# press handlers stay THERE — this file only builds and refreshes rows).
func setup(panel_in, mission) -> void:
	panel = panel_in
	m = mission


func build_class_buttons(box: Node) -> void:
	panel.picker_rows = panel.class_rows.duplicate()   # F4 (MC 11616):
	# the family picker rows (the NON-winner towers.json rows — bombard,
	# hailspire) ride the SAME button loop and the SAME W17e poll sync; a
	# press places THAT family's T1 via placer.place_id, the one gate
	# sequence.
	var winner_ids: Array = []
	for crow: Dictionary in panel.class_rows:
		winner_ids.append(String(crow["id"]))
	for row: Dictionary in m.tables.rows("towers"):
		if not winner_ids.has(String(row["id"])):
			panel.picker_rows.append({"id": String(row["id"]),
					"name": String(row["name"]),
					"cost": int(row["base_cost"]), "fam": true})
	for row: Dictionary in panel.picker_rows:
		var fam: bool = bool(row.get("fam", false))
		var cid := String(row.get("class", ""))
		var b := Button.new()
		b.name = ("Family_" + String(row["id"])) if fam else ("Class_" + cid)
		var target: Callable = panel._on_family_pressed if fam \
				else panel._on_place_pressed
		b.pressed.connect(target.bind(String(row["id"]) if fam else cid))
		var icon_id := String(ICON_FOR.get(String(row["id"]), ""))
		if icon_id != "":            # V4: icon-bearing rows (brief row 2)
			b.icon = SPRITE_BANK.texture_for(icon_id)
			b.icon_alignment = HORIZONTAL_ALIGNMENT_LEFT
			b.add_theme_constant_override("icon_max_width",
					SPRITE_BANK.ICON_PX)   # 4.x Control override API
		box.add_child(b)
		UITWEEN.attach(b)             # V6 (MC 11530): hover/press motion
		if not fam:
			panel.class_buttons[cid] = b
		row["btn"] = b


func build_sections(box: Node) -> void:
	# W17c (MC 11274.1.30 / card 11387): placed defenses get SELECTABLE
	# rows — until now select_defense() was only ever called by the smoke
	# harness, so in a real game selected_uid stayed 0 and Upgrade/Repair/
	# Sell were player-unreachable (the W17b false-green class, one layer
	# deeper). Data = the EXISTING defense-list API (m.defense_list, the
	# same list _selected_obj and the placer read). Plain greybox Buttons,
	# NOT item_row: that widget is the pinned ITEM-pool renderer (F2-12 —
	# a placed defense is not an inventory item); the clear+rebuild loop
	# keeps the shipped bank_list.fill shape (W16 dedupe idiom).
	var def_head := Label.new()
	def_head.name = "Head_defenses"
	def_head.text = "DEFENSES"
	box.add_child(def_head)
	defense_rows = VBoxContainer.new()
	defense_rows.name = "Rows_defenses"
	box.add_child(defense_rows)
	# W14 leg 2 (pinned defense_panel row): relic slot -> relic picker =
	# item_row instances over mission.relic_pool (F2-12 shared widget).
	# Pick a pool row, then Assign/Unassign routes through the pinned
	# mission crossing — the panel file is pure UI (C11 rules live there).
	var relic_head := Label.new()
	relic_head.name = "Head_relic"
	relic_head.text = "RELICS"
	box.add_child(relic_head)
	relic_rows = VBoxContainer.new()
	relic_rows.name = "Rows_relic"
	box.add_child(relic_rows)


# W17e (MC 11274.1.32 / card 11397): the dirty-guarded rebuild the panel
# calls from poll() and refresh() — rows track LIST changes only.
func refresh() -> void:
	if _rows_dirty():                # W17e: rows track LIST changes only
		_rebuild_defense_rows()


# W17c (MC 11274.1.30 / card 11387): the clear+rebuild over the EXISTING
# m.defense_list API (no new mechanism); uid + class + tier + hp per row,
# the selected row marked by its "»" text prefix (greybox-visible, no
# theme). Text is data-only (I2: no formulas); clicks call the shipped
# select_defense — the harness's old entry point becomes the player's too.
func _rebuild_defense_rows() -> void:
	# Detach NOW (no flicker) + queue_free: a row Button can be the very
	# object emitting `pressed` when refresh() rebuilds (row click ->
	# select_defense -> refresh), and free() on a locked (mid-emit)
	# object is an engine ERROR (VERIFIED this card) — queue_free is the
	# safe idiom, deferred to frame end after the emit unwinds.
	for child: Node in defense_rows.get_children():
		defense_rows.remove_child(child)
		child.queue_free()
	var built: Array = []
	for rec: Dictionary in m.defense_list:
		var obj = rec["obj"]
		var b := Button.new()
		b.name = "Row_%d" % int(rec["uid"])
		b.text = "%suid %d %s T%d hp %d/%d" % [
				"» " if int(rec["uid"]) == int(panel.selected_uid) else "",
				int(rec["uid"]), String(obj.class_id), int(obj.tier) + 1,
				int(obj.hp), int(obj.hp_max)]
		b.pressed.connect(_on_defense_row.bind(int(rec["uid"])))
		defense_rows.add_child(b)
		built.append(int(rec["uid"]))
	_rows_uids = built


func _on_defense_row(uid: int) -> void:
	panel.select_defense(uid)


# W17e (MC 11274.1.32 / card 11397): the selected-mark pass the panel's
# sync() runs — the "» " prefix rides the existing text (hp/tier text is
# refresh data, never re-rendered on this path). Cheap by contract: text
# is touched only where a mark changed (no churn), rows are NEVER freed
# here (E9 lives in the rebuild alone).
func sync_marks() -> void:
	for child: Node in defense_rows.get_children():
		var b := child as Button
		if b == null:
			continue
		var marked := int(String(b.name).trim_prefix("Row_")) \
				== int(panel.selected_uid)
		var text := String(b.text)
		if marked and not text.begins_with("»"):
			b.text = "» " + text
		elif not marked and text.begins_with("»"):
			b.text = text.substr(2)


# W17e dirty check: the rebuild runs only when the defense LIST changed
# (count, or uids in order). A select/sell-refresh no longer churns the
# rows into unsized new controls — the REPRO-A shape of losing the
# player's next click to a mid-frame rebuild.
func _rows_dirty() -> bool:
	if _rows_uids.size() != m.defense_list.size():
		return true
	for i: int in m.defense_list.size():
		if int(m.defense_list[i]["uid"]) != int(_rows_uids[i]):
			return true
	return false
