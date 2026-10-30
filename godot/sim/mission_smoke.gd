# mission_smoke — headless mission-flow smoke (W6, MC 11274.1.13 /
# card 11308; W16 split MC 11274.1.28 / card 11384). Test asset in sim/
# (harness idiom: no sim_ prefix, the parse-probe scan skips it;
# boot_probe/save_probe are the precedent). W16: one file per leg-group —
# this driver (boot + seed + setup + HUD-BUILD + W14PANEL), _w8.gd (the
# W8 defense + panel legs), _flow.gd (wave flow + kills + loot + ability),
# _swap.gd (swap/HUD/boss/lose). Pure move: printed rows unchanged, one
# byte. Boots the REAL mission scene under -s: load mission.tscn,
# instantiate, mount under root, then drive _ready() + setup(...)
# DIRECTLY (E5: the main loop never runs under -s, add_child does not
# dispatch _ready) and drive mission.step(1.0/60.0) frames — the exact
# call _process makes in the shipped game (C12: _process = step, nothing
# else). user:// isolation = the save_probe idiom (caller redirects
# XDG_DATA_HOME to a temp dir). The 3-hero deck is seeded through the
# REAL C13 wiring (GWCompose trio; the set_deck mutator writes the file),
# so the save path is exercised before the mission reads the deck.
# Determinism: ONE pinned seed 11274. EMPTY stderr is the verdict.
# Machine rows, in print order (the pytest leg asserts; per-leg detail
# lives in each leg file's header):
#   SEED HUD-BUILD W14PANEL | W8PLACE W8UPGRADE W8REPAIR W8REPAIR1
#   W8PLACE2 W8CAP W8SELL W8FREESLOT W8PANEL W8PANEL-ACT | SPAWN HUD-WAVE
#   HUD-GREEN ADVANCE CORE KILL WAVE LOOT REFILL W8KILL ABILITY HUD-BLUE |
#   SWAP HUD-HL x2 F1SWAP W14SWAP HUD-BOSS DOWN HUD-BANNER LOSE OK
# E3: quit() under -s does NOT abort the running frame — every failure
# path early-returns; each quit() fires exactly once (leg files report
# false after smoke._fail and the driver early-returns).
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const SMOKE_W8 := preload("res://sim/mission_smoke_w8.gd")
const SMOKE_FLOW := preload("res://sim/mission_smoke_flow.gd")
const SMOKE_SWAP := preload("res://sim/mission_smoke_swap.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const SAVE_PATH := "user://gatewardens.cfg"
const DECK := ["warden", "deadeye", "embercaller"]


func _init() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)  # F2-5 wiring site
	var state = graph["state"]
	var save = graph["save"]
	var start_green := int(tables.map("gatefall").get("start_green", -1))
	var main_hp := int(tables.map("gatefall").get("cores", {})
			.get("main", {}).get("hp", {}).get("normal", -1))
	state.set_deck(DECK.duplicate())     # the seed lands via the C13 write
	if not FileAccess.file_exists(SAVE_PATH):
		_fail("no user:// save after set_deck")
		return
	var saved: Dictionary = save.load_save()
	if not String(saved.get("deck_json", "")).contains("deadeye"):
		_fail("deck missing from the save file: %s" % str(saved.get("deck_json", "")))
		return
	print("MISSION-SMOKE-SEED deck=" + String(saved.get("deck_json", "")))
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                           # E5: drive _ready directly (no-op)
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274                     # pinned seed: the smoke is deterministic
	m.setup(tables, state, save, graph["bridge"], "gatefall", "normal", rng)
	if String(m.phase_kind) != "build" or int(m.green) != start_green \
			or int(m.wave) != 0 or int(m.cores["main"]["hp"]) != main_hp:
		_fail("setup: phase=%s green=%d wave=%d core=%s" % [
				m.phase_kind, m.green, m.wave, str(m.cores["main"]["hp"])])
		return
	# Harness-driven state (same license as driving _ready/setup): the
	# main core is made 5x sturdier so the W6 run with NO damage source
	# cannot end the mission on a core breach during the checks below.
	# Breach damage scales WITH core max (reading: ratio x max), so the
	# buff also scales leak damage — wave 0 is cleared by harness KILLS
	# (check 4), the licensed stand-in for W7/W8 damage sources.
	m.core_main.hp_max *= 5.0
	m.core_main.hp = m.core_main.hp_max
	# --- HUD (W10, MC 11274.1.18 / card 11325): the read-only overlay the
	#        mission's DECLARED hook mounted. refresh() is driven here
	#        exactly as the W8 panel legs drive panel.refresh() (E5: no
	#        frame dispatch under -s); every label the pytest leg re-
	#        derives rides shipped data (waves/economy/heroes/enemies),
	#        never a test-side copy.
	var hud = m.get_node("HUD")
	if hud == null:
		_fail("declared hook mounted no HUD node on the mission root")
		return
	var waves_total: int = m.waves_file.get("waves", []).size()
	hud.refresh()
	var build_secs := int(ceilf(float(m.waves_file["waves"][0].get(
			"build_seconds", 0.0))))
	# G8 (MC 11692): this boot IS the production mount order (PhaseController
	# .setup ran at mission.gd:153, the HUD mounts at :168-171), so the
	# banner here proves the BOOTSTRAP path — the coach's build wave-0 copy
	# (the old assertion banner_text()=="" predates the coach row).
	if String(hud.wave_text()) != "Build: wave %d in %d s" % [
			int(m.wave) + 1, build_secs] \
			or String(hud.banner_text()) != String(hud.COACH_BUILD_W0) \
			or not bool(hud.banner_shown()):
		_fail("HUD build label: %s (banner %s)" % [
				hud.wave_text(), hud.banner_text()])
		return
	print("MISSION-SMOKE-HUD-BUILD wave=%d secs=%d text=%s" % [
			m.wave, build_secs, hud.wave_text()])
	# --- W14 P1-1 (MC 11274.1.25 / card 11341): placement is reachable
	#        IN THE LIVE PATH — mission.setup() mounted the panel itself
	#        (the W10 HUD idiom); a KeyM press enters the SHIPPED bridge,
	#        mission step (5) relays it to panel.poll, and the tower
	#        lands for EXACTLY the towers.json base_cost — THROUGH the
	#        panel path, never around it. Undo: the fresh full-HP defense
	#        is sold through the SAME panel (pinned R1: full-HP refund 0)
	#        and green is harness-written back to start_green (the W8
	#        green-write / boot_probe license, declared) so the W8 legs
	#        below run on the state they were authored against.
	var panel = m.get_node("DefensePanel")
	if panel == null:
		_fail("mission.setup() mounted no DefensePanel (P1-1)")
		return
	if panel.class_rows.is_empty() or panel.placer == null:
		_fail("DefensePanel.setup() built no classes/placer")
		return
	var p_green0 := int(m.green)
	var p_class: Dictionary = panel.class_rows[0]
	m.bridge.on_key("KeyM", true)
	m.bridge.on_key("KeyM", false)
	m.step(1.0 / 60.0)                 # step (5) routes the relayed press
	if m.defense_list.size() != 1 \
			or int(m.green) != p_green0 - int(p_class["cost"]):
		_fail("P1-1 bridge place: green=%d count=%d" % [
				m.green, m.defense_list.size()])
		return
	panel.select_defense(int(m.defense_list[0]["uid"]))
	panel.handle_press("KeyN")         # full-HP sell: the pinned R1 refund
	var p_after_sell := int(m.green)
	var p_refund := p_after_sell - (p_green0 - int(p_class["cost"]))
	m.green = p_green0                 # license write (header comment)
	print("MISSION-SMOKE-W14PANEL mount=1 class=%s cost=%d refund=%d green=%d" % [
			String(p_class["class"]), int(p_class["cost"]), p_refund,
			int(m.green)])
	# Shared leg state (the W16 split's ONE home for cross-leg values).
	var leg := {"m": m, "hud": hud, "panel": panel, "rng": rng,
		"state": state, "save": save, "start_green": start_green,
		"waves_total": waves_total, "deck": DECK,
		"per_wave": int(tables.table("economy").get("green", {})
				.get("per_wave", 0)),
		"wave_xp": int(tables.table("xp").get("wave_xp", 0))}
	if not SMOKE_W8.run(self, leg):
		return
	if not SMOKE_FLOW.run(self, leg):
		return
	if not SMOKE_SWAP.run(self, leg):
		return


func _fail(why: String) -> void:
	print("MISSION-SMOKE FAIL " + why)
	quit(1)
