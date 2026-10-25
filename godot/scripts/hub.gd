extends Control

# Hub ROUTER TARGET placeholder (W5 scope, MC 11274.1.12 / card 11304):
# root Control + a label identifying the hub, nothing more. The full
# hub.gd Modules row (tavern room, NPC proximity zones) and the panel
# rows (war_table, gear_panel_ui, blacksmith_ui, tinkerer_ui,
# dummy_range) are later milestone rows — placeholder precedent: the W1
# main.gd stub, replaced when its row landed. What IS real here: the
# pinned setup(tables, game_state, save_store, bridge, rng) injection
# (hub.gd Modules row), so the router -> hub handoff shape is proven
# before the panels exist. No monetization vocab, no invented UI.

var tables = null   # GWTables by injection (R3/C1 — no autoloads)
var state = null    # GWGameState
var save = null     # GWSaveStore
var bridge = null   # GWBridge
var rng = null      # main.gd's ONE runtime RNG (F2-2)


func setup(tables_in, game_state, save_store, bridge_in, rng_in) -> void:
	tables = tables_in
	state = game_state
	save = save_store
	bridge = bridge_in
	rng = rng_in
