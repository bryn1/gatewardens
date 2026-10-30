# hud_coach_probe — G8 first-session coach banner probe (MC 11692 /
# V121-PLAN §G8). Test asset in sim/ (boot_probe/mission_smoke idiom).
# Boots the REAL mission scene under -s through mission.setup — the
# PRODUCTION mount order ($PhaseController.setup at mission.gd:153 runs
# BEFORE the HUD mounts at :168-171) — so the first row proves the
# BOOTSTRAP path, not a re-implementation of it (Rev 2/DA A2). Then
# drives mission.step frames like the smoke (E5: no frame dispatch
# under -s) through the phase edges; idle build waits ride dt 0.5 (the
# build phase is ONE timer decrement — every edge stays the production
# emit; box-load discipline on the 900s probe wall); kills are the
# smoke's licensed harness runner.damage leg; the priority leg rides the
# harness win_pending write (boot_probe license, declared here) in a
# SECOND production boot — win during wave-0 combat must read VICTORY.
# Core sturdiness x5: the mission_smoke precedent, same reason (the
# wave-walk loops must not end the run on a breach). EMPTY stderr is
# the verdict; one pinned seed 11274; quit() fires exactly once (E3).
# Machine rows, in print order (tests/test_hud_coach.py asserts):
#   BOOT COMBAT W1BUILD W1HOLD | SILENT x3 | PRIORITY OK
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]


func _init() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)  # F2-5 wiring
	var state = graph["state"]
	state.set_deck(DECK.duplicate())     # the C13 seed, smoke preamble
	var m = _boot(tables, graph)
	if m == null:
		return
	var hud = m.get_node("HUD")
	# --- BOOT leg: right after the production setup — the wave-0 build
	#     edge is UNSEEN by any connect (it fired before the HUD existed);
	#     only the bootstrap can carry this line. banner_shown() is the
	#     shipped read-back.
	hud.refresh()
	if String(hud.banner_text()) != String(hud.COACH_BUILD_W0) \
			or not bool(hud.banner_shown()):
		_fail("BOOT: build-w0 line absent at production mount: %s" \
				% hud.banner_text())
		return
	print("GWCOACH-BOOT shown=1 text=%s" % hud.banner_text())
	# --- combat edge: the line SWITCHES (bootstrap copy -> signal copy).
	var guard := 0
	# Build waits ride dt 0.5: the build phase is ONE timer decrement
	# (phase_controller.step) — the edge itself is still the production
	# _enter_combat emit, only the idle countdown is coarser (box-load
	# discipline; the 900s probe wall on a loaded box).
	while guard < 200 and String(m.phase_kind) == "build":
		m.step(0.5)
		guard += 1
	if guard >= 200:
		_fail("combat edge never arrived")
		return
	hud.refresh()
	if String(hud.banner_text()) != String(hud.COACH_FIGHT_W0):
		_fail("COMBAT: line did not switch at the combat edge: %s" \
				% hud.banner_text())
		return
	print("GWCOACH-COMBAT shown=1 text=%s" % hud.banner_text())
	# --- wave 0 cleared -> build w1 telegraph line, held (the line shows
	#     ONCE — a later refresh inside the same build cannot change it).
	if not _clear_wave(m, 0):
		return
	hud.refresh()
	if String(hud.banner_text()) != String(hud.COACH_TELEGRAPH_W1) \
			or not bool(hud.banner_shown()):
		_fail("W1BUILD: telegraph line absent in build w1: %s" \
				% hud.banner_text())
		return
	print("GWCOACH-W1BUILD shown=1 text=%s" % hud.banner_text())
	for _t: int in 10:
		m.step(0.5)                 # 5 s into the 15 s build w1 — still build
	hud.refresh()
	if String(hud.banner_text()) != String(hud.COACH_TELEGRAPH_W1):
		_fail("W1HOLD: telegraph line drifted inside build w1: %s" \
				% hud.banner_text())
		return
	print("GWCOACH-W1HOLD text=%s" % hud.banner_text())
	# --- silence: wave-1 combat, build w2, combat w2 — nothing on
	#     waves >= 2 (and the w1-combat row proves the telegraph was
	#     REPLACED by nothing, not left standing).
	if not _to_phase(m, "combat"):
		return
	if not _silent_row(m, hud, 1, "combat"):
		return
	if not _clear_wave(m, 1):
		return
	if not _silent_row(m, hud, 2, "build"):
		return
	if not _to_phase(m, "combat"):
		return
	if not _silent_row(m, hud, 2, "combat"):
		return
	# --- PRIORITY leg (negative, the DA row): a SECOND production boot,
	#     driven to wave-0 combat (coach = FIGHT line live), then the
	#     harness sets the shipped win flag — step (5) decides outcome,
	#     and the banner must read VICTORY, never the coach.
	var m2 = _boot(tables, graph)
	if m2 == null:
		return
	if not _to_phase(m2, "combat"):
		return
	var hud2 = m2.get_node("HUD")
	if String(hud2.banner_text()) != String(hud2.COACH_FIGHT_W0):
		_fail("PRIORITY: coach not live before the win write: %s" \
				% hud2.banner_text())
		return
	m2.win_pending = true                # harness license (header)
	m2.step(1.0 / 60.0)
	if String(m2.outcome) != "win":
		_fail("PRIORITY: outcome=%s after win_pending" % m2.outcome)
		return
	hud2.refresh()
	if String(hud2.banner_text()) != "VICTORY" \
			or not bool(hud2.banner_shown()):
		_fail("PRIORITY: coach beat the outcome: %s" % hud2.banner_text())
		return
	print("GWCOACH-PRIORITY outcome=win shown=1 text=VICTORY")
	print("GWCOACH-OK")
	quit(0)                              # E3: exactly once


func _boot(tables, graph) -> Node:
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return null
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                           # E5: drive _ready directly (no-op)
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274                     # pinned seed: deterministic probe
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	m.core_main.hp_max *= 5.0            # the smoke's x5 precedent (header)
	m.core_main.hp = m.core_main.hp_max
	return m


# Licensed kill leg (mission_smoke_flow leg 4 idiom): damage whatever
# the runner holds every tick until the phase flips — the transition,
# not the combat, is what this probe proves.
func _clear_wave(m, wave: int) -> bool:
	var runner = m.get_node("EnemyRunner")
	var guard := 0
	while guard < 400 and String(m.phase_kind) == "combat":
		for ent: Dictionary in runner.entities:
			runner.damage(ent, 1.0e9)
		m.step(0.5)                 # spawn delays are sim-time (waves max 2s)
		guard += 1
	if guard >= 400 or int(m.wave) != wave + 1:
		_fail("wave %d never cleared (wave=%d)" % [wave, m.wave])
		return false
	return true


func _to_phase(m, kind: String) -> bool:
	var guard := 0
	while guard < 200 and String(m.phase_kind) != kind:
		m.step(0.5)
		guard += 1
	if String(m.phase_kind) != kind:
		_fail("phase never reached %s" % kind)
		return false
	return true


func _silent_row(m, hud, wave: int, kind: String) -> bool:
	if int(m.wave) != wave or String(m.phase_kind) != kind:
		_fail("SILENT state drift: wave=%d phase=%s" % [m.wave, m.phase_kind])
		return false
	hud.refresh()
	if String(hud.banner_text()) != "" or bool(hud.banner_shown()):
		_fail("SILENT: coach line survived wave %d %s: %s" \
				% [wave, kind, hud.banner_text()])
		return false
	print("GWCOACH-SILENT wave=%d phase=%s shown=0 text=" % [wave, kind])
	return true


func _fail(why: String) -> void:
	print("GWCOACH FAIL " + why)
	quit(1)
