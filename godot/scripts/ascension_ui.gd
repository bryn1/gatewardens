extends Control

# ascension_ui — Ascension spend station (W14 leg 3, MC 11274.1.25 /
# card 11341; the station-row idiom of the W9 panels, opened from the
# hub bar — mouse path only, NO new bridge codes invented, the hub-side
# Digit map stays exactly as shipped). Pinned A2 row: account-wide
# Ascension points over the Offense/Defense/Utility trees.
#
# Everything listed is ascension.json data (tree rows carry
# id/max/per_point{stat,val}); the ONLY write crossing is the shipped
# C13 mutator GWGameState.spend_asc — its pinned gates (unknown power,
# node max, points balance) are the refusal mechanism and are NEVER
# duplicated here (the buttons merely grey out for legibility; a
# keyboardless caller still gets spend_asc's answer). The EFFECT of a
# spend is live at the single pinned consumer site, mission._build_heroes
# via SimProgression.asc_modifier — no math lives in this panel (I2:
# zero balance numbers here; the point balance shown is a meta-field
# read, the same arithmetic spend_asc itself checks, UI-side).
# Greybox Control styling per the defense_panel precedent.

var tables = null
var state = null
var _points = null                   # Points label (meta read, no math)
var _tree_box = null
var _power_rows: Dictionary = {}     # power id -> {"label":, "button":}


func setup(tables_in, game_state) -> void:
	tables = tables_in
	state = game_state
	var box := VBoxContainer.new()
	box.name = "Ascension"
	add_child(box)
	var title := Label.new()
	title.text = "ASCENSION"
	box.add_child(title)
	_points = Label.new()
	_points.name = "Points"
	box.add_child(_points)
	_tree_box = VBoxContainer.new()
	_tree_box.name = "Trees"
	box.add_child(_tree_box)
	_build_trees()
	# E1-safe anchor (the gear_panel precedent): a Node in the tree, and
	# every C13 meta-write repaints through the SAME signal the save rides.
	state.mutated.connect(refresh)
	refresh()


func _tree() -> Dictionary:
	return tables.table("ascension").get("tree", {})


# Available points = earned minus spent — the balance read spend_asc
# enforces; shown, never enforced here (the refusal is spend_asc's).
func available() -> int:
	var spent := 0
	for id: String in state.asc_spent:
		spent += int(state.asc_spent[id])
	return int(state.asc_earned) - spent


func _build_trees() -> void:
	for branch: String in _tree():
		var head := Label.new()
		head.name = "Head_" + branch
		head.text = branch.to_upper()
		_tree_box.add_child(head)
		for row: Dictionary in _tree()[branch]:
			var id := String(row["id"])
			var line := HBoxContainer.new()
			line.name = "Power_" + id
			var lab := Label.new()
			lab.name = "Info"
			line.add_child(lab)
			var b := Button.new()
			b.name = "Spend_" + id
			b.text = "+1"
			b.pressed.connect(_on_spend.bind(id))
			line.add_child(b)
			_tree_box.add_child(line)
			_power_rows[id] = {"label": lab, "button": b}


func _on_spend(power: String) -> void:
	state.spend_asc(_tree(), power, 1)
	refresh()


func refresh() -> void:
	_points.text = "ascension points available %d" % available()
	var spent_total: Dictionary = state.asc_spent
	for id: String in _power_rows:
		var points := int(spent_total.get(id, 0))
		var per: Dictionary = _power_row(id)
		_power_rows[id]["label"].text = "%s: %d/%d (+%s %s /pt)" % [
			id, points, int(per["max"]),
			str(per["per_point"]["val"]), String(per["per_point"]["stat"])]
		_power_rows[id]["button"].disabled = available() <= 0 \
				or points >= int(per["max"])


func _power_row(power: String) -> Dictionary:
	for branch: String in _tree():
		for row: Dictionary in _tree()[branch]:
			if String(row["id"]) == power:
				return row
	return {}
