extends Control

# defense_panel — in-mission build-phase selection panel (Modules row
# scripts/defense_panel.gd, MC 11274.1.15 / card 11322): lists the v1
# defense classes, tiers/actions gated by SimEconomy.can_afford, and the
# Upgrade/Repair/Sell buttons + class buttons the pinned row names — all
# routed THROUGH the defense_placer / defense_obj APIs (pure UI: no cost
# math, no formulas here, I2; every gate is the shipped static).
#
# Readings (declared; W8-evidence.md, W14 amendment MC 11274.1.25 / card
# 11341):
# - Functional greybox styling only (plain VBox of Labels/Buttons, no
#   theme): the full HUD styling is the separate "HUD + hot-swap deck UI"
#   frontend row named by the breakdown table.
# - The pinned row's relic picker (F2-12 item_row over the C11 pool)
#   SHIPS with W14 leg 2 below — the W8 note that item_row.gd/.tscn "do
#   not exist" was STALE (they shipped in W9: scripts/item_row.gd,
#   scenes/item_row.tscn); the picker instantiates the SHARED widget, it
#   renders no row of its own (F2-12 one-widget rule).
# - Bridge input model (row: relay in / state out): this file NEVER polls
#   Input — handle_press(code) consumes one GWBridge relay code and
#   poll(presses) drains a relayed press list. Greybox bindings (KeyM place
#   selected class, KeyE upgrade selected, KeyN sell selected) ride codes
#   the W4 relay already ships; the real keymap is the HUD row's, and the
#   W14 mission.setup mount ("mission adds this Control") is the row's
#   own scene wiring, now live (P1-1).
# - SELECT path (W17c, MC 11274.1.30 / card 11387): placed defenses are
#   listed as selectable rows (uid/class/tier/hp, selected marked "»"),
#   rebuilt inside refresh() off m.defense_list. Before this card
#   select_defense was harness-only — a real player could never reach
#   Upgrade/Repair/Sell (W17b's false-green class, one layer deeper).
# - POLL sync (W17e, MC 11274.1.32 / card 11397): button enabled/disabled
#   used to change ONLY inside refresh(), and refresh() ran ONLY on
#   action-driven events — green rising between refreshes left buttons
#   stale-disabled and the browser silently swallowed real clicks
#   (served REPRO-B: place dead while affordable; REPRO-A: the same
#   staleness + refresh()'s row REBUILD churn losing the click beside it).
#   poll(presses) now runs sync() — enabled flags + selected-marks only,
#   from CURRENT sim state — EVERY poll, while the expensive row
#   clear+rebuild stays behind a dirty check on the defense list
#   (count/uids). E9 unchanged: the rebuild that remains keeps detach +
#   queue_free (never free a control mid-emit).
# - S split (v1.2.1, MC 11699 / V121-PLAN §3 C-1 FULL MOVE): the ROW-LIST
#   UI — class/family button build, the DEFENSES + RELICS sections, the
#   W17c rebuild, the W17e marks and dirty check — moved WHOLE to
#   scripts/defense_rows_ui.gd (the rows_ui below builds and refreshes;
#   no second copy lives here). Selection state, bridge input and the
#   action buttons stay: this file is the panel, rows_ui is its rows.

const PLACER := preload("res://scripts/defense_placer.gd")
const BANK_LIST := preload("res://scripts/bank_list.gd")
const SIM_ECONOMY := preload("res://sim/sim_economy.gd")
const UITWEEN := preload("res://scripts/ui_tween.gd")
const ROWS_UI := preload("res://scripts/defense_rows_ui.gd")

const PRESS := {"KeyM": "place", "KeyE": "upgrade", "KeyN": "sell"}

var m = null
var placer = null
var class_rows: Array = []
var picker_rows: Array = []              # F4: class winners + family rows
var selected_class := 0              # index into class_rows
var selected_uid := 0                # 0 = no defense selected
var selected_relic := 0              # C11: pool relic uid armed for assign
var class_buttons: Dictionary = {}   # class id -> Button
var upgrade_btn = null
var repair_btn = null
var sell_btn = null
var assign_btn = null
var unassign_btn = null
var rows_ui = null                   # S split: the row-list UI, moved
                                     # out whole (defense_rows_ui.gd)
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
	rows_ui = ROWS_UI.new()          # S split (MC 11699): rows_ui builds
	rows_ui.setup(self, m)           # every row list, into this box
	var box := VBoxContainer.new()
	box.name = "Rows"
	add_child(box)
	info_label = Label.new()
	info_label.name = "Green"
	box.add_child(info_label)
	rows_ui.build_class_buttons(box)
	upgrade_btn = _action(box, "Upgrade", _on_upgrade)
	repair_btn = _action(box, "Repair", _on_repair)
	sell_btn = _action(box, "Sell", _on_sell)
	rows_ui.build_sections(box)      # Head/Rows_defenses + Head/Rows_relic
	assign_btn = _action(box, "Assign relic", _on_assign)
	unassign_btn = _action(box, "Unassign relic", _on_unassign)
	select_class(0)
	refresh()


func select_class(i: int) -> void:
	if i >= 0 and i < class_rows.size():
		selected_class = i


func select_defense(uid: int) -> void:
	selected_uid = uid
	refresh()                      # W17c: the row mark + URS re-gate the
	                               # player path must be VISIBLE at once


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
# so callers hand the codes over — no second pump here). W17e: the
# enabled-flags + selected-marks sync runs BEFORE draining presses (state
# re-gated from the CURRENT sim, and a defense that DIED since the last
# action refresh re-enters the rebuild through the same dirty check).
func poll(presses: Array) -> void:
	sync()
	rows_ui.refresh()              # W17e: dirty-guarded rows rebuild
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


# W17e (MC 11274.1.32 / card 11397): the poll-path sync — button
# enabled/disabled + the selected-marks ONLY, computed from CURRENT sim
# state (I2: gates stay the shipped can_afford static; no cost math here).
# Cheap by contract: text is touched only where a mark changed (no
# churn), rows are NEVER freed here (E9 lives in the rebuild alone).
func sync() -> void:
	for row: Dictionary in picker_rows:
		var btn = row["btn"]
		btn.disabled = not SIM_ECONOMY.can_afford(int(m.green),
				int(row["cost"]))
		var want := "%s (%d)%s" % [String(row["name"]), int(row["cost"]),
			" *" if class_rows[selected_class]["class"] \
				== String(row.get("class", "")) else ""]
		if String(btn.text) != want:
			btn.text = want
	var obj = _selected_obj()
	var ucost := int(obj.next_upgrade_cost()) if obj != null else -1
	upgrade_btn.disabled = ucost < 0 \
			or not SIM_ECONOMY.can_afford(int(m.green), ucost)
	repair_btn.disabled = obj == null or float(obj.missing_ratio()) <= 0.0
	sell_btn.disabled = obj == null
	assign_btn.disabled = obj == null or selected_relic <= 0 \
			or int(obj.relic_uid) != 0
	unassign_btn.disabled = obj == null or int(obj.relic_uid) == 0
	rows_ui.sync_marks()           # W17e: the "»" selected-mark pass


func refresh() -> void:
	info_label.text = "green %d / cap %d / defenses %d" % [
		int(m.green), int(m.defense_cap), int(m.defenses)]
	sync()                           # W17e: the ONE enabled/mark pass
	# Relic picker repaint (shared item_row rows over the C11 pool; the
	# assigned row is BADGED selected, assignment itself is mission-side).
	BANK_LIST.fill(rows_ui.relic_rows, m.tables, m.relic_pool,
			selected_relic,
			_on_relic_picked)   # the ONE fill loop (bank_list, W16)
	rows_ui.refresh()                # W17e: rows track LIST changes only


func _on_place_pressed(class_id: String) -> void:
	for i: int in class_rows.size():
		if String(class_rows[i]["class"]) == class_id:
			select_class(i)
	place_selected()


# F4 (MC 11616): the family press — the SAME place-then-refresh shape as
# _on_place_pressed; every gate is the placer/application-site answer.
func _on_family_pressed(tower_id: String) -> void:
	placer.place_id(tower_id, 1)
	refresh()


func _on_upgrade() -> void:
	_result_upgrade()


func _on_repair() -> void:
	_result_repair()


func _on_sell() -> void:
	_result_sell()


func pick_relic(uid: int) -> void:
	selected_relic = int(uid)
	refresh()


func _on_assign() -> void:
	if selected_uid > 0 and selected_relic > 0:
		m.assign_relic(selected_uid, selected_relic)
	refresh()


func _on_unassign() -> void:
	if selected_uid > 0:
		m.unassign_relic(selected_uid)
	refresh()


func _on_relic_picked(uid: int) -> void:
	pick_relic(uid)


func _action(box, label: String, handler: Callable):
	var b := Button.new()
	b.name = label
	b.text = label
	b.pressed.connect(handler)
	box.add_child(b)
	UITWEEN.attach(b)                 # V6 (MC 11530): hover/press motion
	return b


func _selected_obj():
	for rec: Dictionary in m.defense_list:
		if int(rec["uid"]) == selected_uid:
			return rec["obj"]
	return null
