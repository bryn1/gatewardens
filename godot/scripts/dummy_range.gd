extends Control

# dummy_range — training dummies station (Modules row scripts/
# dummy_range.gd, MC 11274.1.16 / card 11323). Pinned row wording:
# "invulnerable dummy + live DPS readout", "uses real mission combat on
# a mini-spawn"; the W9 brief words the leg "XP sink" and names the row
# terse — DECLARED READING (both readings, no invented mechanism):
#   - Combat resolution is the shipped combat static SimCombat.hero_hit
#     (the C2 single damage site heroes also ride; hero_combat itself is
#     mission-RefCounted-bound and cannot leave the mission scene), the
#     crit draw flows through the injected rng receiver-qualified (F2-1).
#   - Each landed practice hit pays ONE hero exactly xp.json's declared
#     enemy_xp_base.normal (the nearest declared XP row — no dummy-only
#     xp key exists in the pinned data set, and inventing one would be
#     an undeclared number, I2) through the shipped add_hero_xp mutator:
#     SimProgression's level math and the C13 save ride inside that one
#     mutator, nowhere else.
#   - The dummy is INVULNERABLE BY CONSTRUCTION: the record has no hp
#     key, so no damage path can kill it; it only accumulates absorbed
#     damage, and the live DPS readout is absorbed / elapsed (the tick
#     clock the caller drives — E5-safe under -s).
# Greybox Control styling per the defense_panel precedent; the 3D dummy
# art is the frontend row (W8 shipped zero per-entity .tscn by idiom).

const SIM_COMBAT := preload("res://sim/sim_combat.gd")

var tables = null
var state = null
var rng = null
var dummy: Dictionary = {"absorbed": 0.0}   # no hp key: unkillable by shape
var elapsed := 0.0
var last: Dictionary = {}
var _readout = null
var strike_button = null


func setup(tables_in, game_state, rng_in) -> void:
	tables = tables_in
	state = game_state
	rng = rng_in
	var box := VBoxContainer.new()
	box.name = "DummyRange"
	add_child(box)
	var title := Label.new()
	title.text = "TRAINING DUMMIES"
	box.add_child(title)
	_readout = Label.new()
	_readout.name = "Readout"
	box.add_child(_readout)
	strike_button = Button.new()
	strike_button.name = "Strike"
	strike_button.text = "Strike dummy"
	strike_button.pressed.connect(_on_strike)
	box.add_child(strike_button)
	state.mutated.connect(refresh)
	refresh()


# One practice hit by hero_id against the invulnerable dummy: damage
# through SimCombat.hero_hit (crit roll from the injected rng), the
# declared practice XP through the shipped C13 mutator.
func strike(hero_id: String) -> Dictionary:
	var hero: Dictionary = {}
	for row: Dictionary in _load_array("heroes"):
		if String(row.get("id", "")) == hero_id:
			hero = row
	if hero.is_empty():
		return {"ok": false, "why": "hero"}
	var base: Dictionary = hero["base"]
	var atk: Dictionary = hero["attacks"]["primary"]
	var hit: Dictionary = SIM_COMBAT.hero_hit(
			float(base["damage"]) * float(atk["dmg_scale"]),
			float(base["crit_chance"]), float(base["crit_damage"]),
			rng.randf())
	dummy["absorbed"] = float(dummy["absorbed"]) + float(hit["damage"])
	var xp := int(tables.table("xp")["enemy_xp_base"]["normal"])
	state.add_hero_xp(hero_id, xp)          # the ONE xp app site (C13)
	last = {"ok": true, "hero": hero_id, "damage": float(hit["damage"]),
			"crit": bool(hit["crit"]), "xp": xp}
	refresh()
	return last


# Live DPS readout (the dummy clock the caller drives; 0 before time).
func dps() -> float:
	if elapsed <= 0.0:
		return 0.0
	return float(dummy["absorbed"]) / elapsed


func tick(delta: float) -> void:
	elapsed += delta
	refresh()


func active_hero() -> String:
	return String(state.deck[0]) if not state.deck.is_empty() else ""


func _on_strike() -> void:
	strike(active_hero())


func refresh() -> void:
	_readout.text = "absorbed %.1f | dps %.1f | last hit %s" % [
			float(dummy["absorbed"]), dps(),
			("crit x%s" % str(last["damage"])) if bool(last.get("crit", false))
			else str(last.get("damage", 0.0))]


func _load_array(stem: String) -> Array:
	# Array-shaped data files have no GWTables dict door (the mission.gd
	# _load_array precedent); the heroes row is the sole damage source.
	var text := FileAccess.get_file_as_string("res://data/" + stem + ".json")
	var parsed: Variant = JSON.parse_string(text)
	return parsed if parsed is Array else []
