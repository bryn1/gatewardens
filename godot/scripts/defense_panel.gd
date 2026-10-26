extends Control

# defense_panel — in-mission build-phase selection panel (Modules row
# scripts/defense_panel.gd, MC 11274.1.15 / card 11322): lists the v1
# defense classes, tiers/actions gated by SimEconomy.can_afford, and the
# Upgrade/Repair/Sell buttons + class buttons the pinned row names — all
# routed THROUGH the defense_placer / defense_obj APIs (pure UI: no cost
# math, no formulas here, I2; every gate is the shipped static).
#
# Readings (declared; W8-evidence.md):
# - Functional greybox styling only (plain VBox of Labels/Buttons, no
#   theme): the full HUD styling is the separate "HUD + hot-swap deck UI"
#   frontend row named by the breakdown table.
# - The pinned row's relic picker (F2-12 item_row over the C11 pool) is
#   NOT built here yet: scripts/item_row.gd / scenes/item_row.tscn belong
#   to the gear-panel wave and do not exist; mission.relic_pool and the
#   C5 relics_assigned leg already ship (W6). Declared open, not faked.
# - Bridge input model (row: relay in / state out): this file NEVER polls
#   Input — handle_press(code) consumes one GWBridge relay code and
#   poll(bridge) drains a relayed press list. Greybox bindings (KeyM place
#   selected class, KeyE upgrade selected, KeyN sell selected) ride codes
#   the W4 relay already ships; the real keymap is the HUD row's, and the
#   scene mount (mission adds this Control) is that row's wiring too.

const PLACER := preload("res://scripts/defense_placer.gd")
const SIM_ECONOMY := preload("res://sim/sim_economy.gd")

const PRESS := {"KeyM": "place", "KeyE": "upgrade", "KeyN": "sell"}

var m = null
var placer = null
var class_rows: Array = []
var selected_class := 0              # index into class_rows
var selected_uid := 0                # 0 = no defense selected
var class_buttons: Dictionary = {}   # class id -> Button
var upgrade_btn = null
var repair_btn = null
var sell_btn = null
var info_label = null


# One-call build; the placer arrives injected (one instance shared with
# every caller) or is constructed here as the panel's own placement API.
func setup(mission, placer_in = null) -> void:
	m = mission
	placer = placer_in
	if placer == null:
		placer = PLACER.new()
		placer.setup(m)
	class_rows = placer.classes()
	var box := VBoxContainer.new()
	box.name = "Rows"
	add_child(box)
	info_label = Label.new()
	info_label.name = "Green"
	box.add_child(info_label)
	for row: Dictionary in class_rows:
		var b := Button.new()
		b.name = "Class_" + String(row["class"])
		b.pressed.connect(_on_place_pressed.bind(String(row["class"])))
		box.add_child(b)
		class_buttons[String(row["class"])] = b
	upgrade_btn = _action(box, "Upgrade", _on_upgrade)
	repair_btn = _action(box, "Repair", _on_repair)
	sell_btn = _action(box, "Sell", _on_sell)
	select_class(0)
	refresh()


func select_class(i: int) -> void:
	if i >= 0 and i < class_rows.size():
		selected_class = i


func select_defense(uid: int) -> void:
	selected_uid = uid


func selected_tier() -> int:
	var obj = _selected_obj()
	return int(obj.tier) + 1 if obj != null else 0


# One relayed bridge code -> the routed action (greybox bindings header).
func handle_press(code: String) -> void:
	match String(PRESS.get(code, "")):
		"place":
			place_selected()
		"upgrade":
			if selected_uid > 0:
				placer.upgrade(selected_uid)
		"sell":
			if selected_uid > 0 and bool(placer.sell(selected_uid)["ok"]):
				selected_uid = 0
		_:
			return
	refresh()


# Reads the relay (drain-once model: the mission step (5) owns the queue,
# so callers hand the codes over — no second pump here).
func poll(presses: Array) -> void:
	for code: Variant in presses:
		handle_press(String(code))


func place_selected() -> Dictionary:
	var res: Dictionary = placer.place(String(class_rows[selected_class]["class"]), 1)
	refresh()
	return res


func _result_upgrade() -> Dictionary:
	var res: Dictionary = placer.upgrade(selected_uid) if selected_uid > 0 \
			else {"ok": false, "why": "none"}
	refresh()
	return res


func _result_repair() -> Dictionary:
	var res: Dictionary = placer.repair(selected_uid) if selected_uid > 0 \
			else {"ok": false, "why": "none"}
	refresh()
	return res


func _result_sell() -> Dictionary:
	var res: Dictionary = placer.sell(selected_uid) if selected_uid > 0 \
			else {"ok": false, "why": "none"}
	if bool(res.get("ok", false)):
		selected_uid = 0
	refresh()
	return res


func refresh() -> void:
	info_label.text = "green %d / cap %d / defenses %d" % [
		int(m.green), int(m.defense_cap), int(m.defenses)]
	for row: Dictionary in class_rows:
		var btn = class_buttons[String(row["class"])]
		btn.disabled = not SIM_ECONOMY.can_afford(int(m.green),
				int(row["cost"]))
		btn.text = "%s (%d)%s" % [String(row["name"]), int(row["cost"]),
			" *" if class_rows[selected_class]["class"] == String(row["class"]) else ""]
	var obj = _selected_obj()
	var ucost := int(obj.next_upgrade_cost()) if obj != null else -1
	upgrade_btn.disabled = ucost < 0 \
			or not SIM_ECONOMY.can_afford(int(m.green), ucost)
	repair_btn.disabled = obj == null or float(obj.missing_ratio()) <= 0.0
	sell_btn.disabled = obj == null


func _on_place_pressed(class_id: String) -> void:
	for i: int in class_rows.size():
		if String(class_rows[i]["class"]) == class_id:
			select_class(i)
	place_selected()


func _on_upgrade() -> void:
	_result_upgrade()


func _on_repair() -> void:
	_result_repair()


func _on_sell() -> void:
	_result_sell()


func _action(box, label: String, handler: Callable):
	var b := Button.new()
	b.name = label
	b.text = label
	b.pressed.connect(handler)
	box.add_child(b)
	return b


func _selected_obj():
	for rec: Dictionary in m.defense_list:
		if int(rec["uid"]) == selected_uid:
			return rec["obj"]
	return null
