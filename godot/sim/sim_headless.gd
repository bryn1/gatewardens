# sim_headless — the C12 golden-mission runner (Modules row
# sim/sim_headless.gd, MC 11274.1.19 / card 11326). Loads the pinned
# fixture (header line + kind:"in" rows), boots the REAL mission scene the
# mission_smoke way (E5: add_child, then drive _ready + setup DIRECTLY),
# seeds ONE RandomNumberGenerator(fixture.seed) and hands it to the shipped
# funnels (F2-2: same parameter-passing shape as the app's injected rng),
# applies every in-row BEFORE the step for its tick, drives
# mission.step(1.0/60.0) through the FULL 11-wave Gatefall run to outcome,
# and prints one canonical out-row per C12 event.
# Rows are stable JSON — one fixed key-insertion order per ev (Dictionaries
# keep insertion order, so stringify is byte-stable); every number is a
# read from shipped state. Emit modes (C12: "goldens regen only via
# --regen"): replay prints ONLY the out-rows (stdout is byte-compared to
# the committed expected rows by tests/test_sim_golden.py); --regen prints
# header + in-rows + out-rows, i.e. the whole fixture — the only sanctioned
# regeneration, never run by the number pytest. Fixture + mode arrive via
# `--` user args (--fixture <fs path> [--regen]) or GW_GOLDEN_FIXTURE
# (save_probe's arg-or-env precedent).
# user:// isolation = the save_probe idiom: the caller redirects
# XDG_DATA_HOME to a temp dir, so the C13 mission-end commit writes there.
# Exit: rc 0 only with every row ok:true and outcome "win"; any failed
# check, timeout or unpinned act prints GOLDEN-FAIL and exits 1. E3: quit()
# under -s does not abort the running frame — every failure path early-
# returns and quit() fires exactly once per process.
# Purity (test_purity scans this file): no node-path lookups, no engine
# singleton refs, no draws — the harness rolls NOTHING; rng.randf() stays
# the shipped funnels' sanctioned draw path.
extends SceneTree

const MISSION_SCENE := "res://scenes/mission.tscn"
const DT := 1.0 / 60.0
const TICK_MAX := 180000
const DECK_KEYS := ["F1", "F2", "F3"]
const C9_KEYS := ["uid", "base_id", "slot", "rarity", "ilvl", "primary",
	"secondary", "atk_speed", "shot_type", "proj_count", "mods", "upgraded"]

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const DEF_PLACER := preload("res://scripts/defense_placer.gd")
const SIM_WAVE := preload("res://sim/sim_wave.gd")

var _bad := 0            # rows emitted with a failed check
var _regen := false
var _fixture := ""
var _in_rows: Array = []
var _raw_header := ""    # authored fixture bytes (regen echoes raw)
var _raw_in: Array = []
var _next := 0           # in-row walk pointer (fixture order == tick order)
var _seen_loot := 0      # loot_events mirror cursor
var _cd_prev := {}       # hero_id -> last observed cooldown array
var _boss_rowed := false
var _max_alive := 0
var _blue_capped := true


func _init() -> void:
	var args := OS.get_cmdline_user_args()
	var i := 0
	while i < args.size():
		if String(args[i]) == "--fixture" and i + 1 < args.size():
			_fixture = String(args[i + 1])
			i += 2
		elif String(args[i]) == "--regen":
			_regen = true
			i += 1
		else:
			i += 1
	if _fixture == "":
		_fixture = OS.get_environment("GW_GOLDEN_FIXTURE")
	if _fixture == "" or not FileAccess.file_exists(_fixture):
		print("GOLDEN-FAIL fixture=" + _fixture)
		quit(1)
		return
	var header := _read_fixture()
	if header.is_empty():
		return
	var tables := GW_TABLES.new()
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	var rng := RandomNumberGenerator.new()
	rng.seed = int(header["seed"])
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		print("GOLDEN-FAIL mission scene not loadable")
		quit(1)
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                       # E5: the harness drives the real entry
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			String(header["map"]), String(header["difficulty"]), rng)
	var placer = DEF_PLACER.new()
	placer.setup(m)
	if _regen:
		print(_raw_header)                 # raw bytes: the authored fixture
		for raw: String in _raw_in:        # in-rows echo verbatim, not
			print(raw)                     # re-typed (JSON ints read as float)
	_run(m, graph, tables, placer)


func _read_fixture() -> Dictionary:
	var header: Dictionary = {}
	for line: String in FileAccess.get_file_as_string(_fixture).split("\n"):
		if line.strip_edges() == "":
			continue
		var parsed: Variant = JSON.parse_string(line)
		if not (parsed is Dictionary):
			print("GOLDEN-FAIL unparsable fixture line: " + line)
			quit(1)
			return {}
		var row: Dictionary = parsed
		if not row.has("kind"):
			header = row          # line 1: the pinned header row
			_raw_header = line
		elif String(row["kind"]) == "in":
			_in_rows.append(row)  # kind "out" rows are the committed expected
			_raw_in.append(line)
	for key: String in ["schema", "seed", "map", "difficulty"]:
		if not header.has(key):
			print("GOLDEN-FAIL header missing " + key)
			quit(1)
			return {}
	return header


func _run(m, graph: Dictionary, tables, placer) -> void:
	_emit({
		"kind": "out", "tick": 0, "ev": "start",
		"map": String(m.mission_id), "difficulty": String(m.difficulty),
		"waves": SIM_WAVE.total_waves(m.waves_file),
		"deck": m.deck.duplicate(), "green": int(m.green),
		"checks": {
			"deck_fallback_3": m.deck.size() == 3,
			"first_build": String(m.phase_kind) == "build",
			"core_full": float(m.cores["main"]["hp"]) \
					== float(m.cores["main"]["max"]),
		}})
	var tick := 0
	var prev_phase := String(m.phase_kind)
	while tick < TICK_MAX:
		tick += 1
		while _next < _in_rows.size() \
				and int(_in_rows[_next]["tick"]) <= tick:
			_act(m, graph["bridge"], placer, _in_rows[_next])
			_next += 1
		m.step(DT)
		_max_alive = maxi(_max_alive, int(m.alive))
		if float(m.blue) > float(m.blue_max):
			_blue_capped = false
		var casts: Array = _cast_watch(m, tick)   # ability rows for this tick
		if String(m.phase_kind) != prev_phase:
			_phase_row(m, tick, not casts.is_empty())
			prev_phase = String(m.phase_kind)
		if not _boss_rowed and m.boss != null:
			_boss_rowed = true
			_emit({"kind": "out", "tick": tick, "ev": "boss",
					"wave": int(m.wave), "hp": float(m.boss["hp"]),
					"hp_max": float(m.boss["hp_max"]),
					"checks": {"boss_is_last_wave": int(m.wave) \
							== SIM_WAVE.total_waves(m.waves_file) - 1}})
		for crow: Dictionary in casts:
			_emit(crow)
		while _seen_loot < m.loot_events.size():
			var item: Dictionary = m.loot_events[_seen_loot]
			_seen_loot += 1
			_emit({"kind": "out", "tick": tick, "ev": "loot_pickup",
					"item": item,
					"checks": {"c9_keys": _c9_shape(item),
							"rarity_known": String(item["rarity"]) \
							in tables.table("rarity").get("ladder", [])}})
		if m.outcome != null:
			_end_row(m, graph, tick)
			if _bad > 0:
				print("GOLDEN-FAIL bad_rows=%d" % _bad)
				quit(1)
				return
			quit(0)
			return
	print("GOLDEN-FAIL timeout tick=%d outcome_phase=%s" % [tick, m.phase_kind])
	quit(1)


# One in-row applied before the step for its tick (C12): the act vocabulary
# is the pinned list; args carry bridge key events or mission call args.
func _act(m, bridge, placer, row: Dictionary) -> void:
	var act := String(row["act"])
	var args: Dictionary = row["args"]
	var res: Dictionary = {}
	match act:
		"input":
			bridge.on_key(String(args["code"]), bool(args["down"]))
			res = {"ok": true}
		"hotswap":
			var key := String(DECK_KEYS[int(args["index"])])
			bridge.on_key(key, true)     # press+release: step (5) drains
			bridge.on_key(key, false)
			res = {"ok": true}
		"place":
			var lane: Dictionary = m.lanes.get(String(args["lane"]), {})
			if lane.is_empty():
				res = {"ok": false, "why": "lane"}
			else:
				res = placer.place(String(args["class"]), int(args["tier"]),
						placer.slot_at(lane["wps"][int(args["wp"])]))
		"upgrade":
			res = placer.upgrade(int(args["uid"]))
		"repair":
			res = placer.repair(int(args["uid"]))
		"sell":
			res = placer.sell(int(args["uid"]))
		_:
			# assign/unassign have NO shipped mission call site (relic
			# assignment lives in defense_panel over the C11 pool) — an
			# in-row using them is unpinned for this runner.
			res = {"ok": false, "why": "act_unpinned"}
	var checks: Dictionary = {}
	if act == "repair" and not bool(res.get("ok", false)):
		checks = {"refused_full": String(res.get("why", "")) == "full"}
	else:
		checks = {"applied": bool(res.get("ok", false))}
	_emit({"kind": "out", "tick": int(row["tick"]), "ev": "act", "act": act,
			"args": args, "result": res, "green": int(m.green),
			"defenses": int(m.defenses), "checks": checks})


func _phase_row(m, tick: int, cast_now: bool) -> void:
	var combat := String(m.phase_kind) == "combat"
	var downed_any := false
	for hid: Variant in m.hero_state:
		if bool(m.hero_state[hid]["downed"]):
			downed_any = true
	_emit({"kind": "out", "tick": tick, "ev": "phase",
			"phase": m.phase_kind, "wave": int(m.wave),
			"green": int(m.green), "blue": float(m.blue),
			"blue_max": float(m.blue_max),
			"checks": {
				"wave_in_range": int(m.wave) >= 0 and int(m.wave) \
						< SIM_WAVE.total_waves(m.waves_file),
				# I4 refill: proven at every combat start the hero does NOT
				# spend on the same tick (a held ability casts off the just-
				# refilled pool inside this very step — the vacuous pass is
				# named, never faked; non-cast starts carry the byte-truth).
				"refill_full": (not combat) or cast_now \
						or float(m.blue) == float(m.blue_max),
				"revive_at_build": (combat) or (not downed_any),
			}})


func _cast_watch(m, tick: int) -> Array:
	# A cast is a cooldown-array RISE (cd -> 0..cd_max); between casts the
	# array only falls (active-only ticking, C4/F2-8), so the rise rule
	# catches casts that fire right after a phase-start recharge too.
	var rows: Array = []
	var hero := String(m.hero_id)
	var cds: Array = m.hero_state[hero]["cooldowns"]
	var prev: Array = _cd_prev.get(hero, [0.0, 0.0, 0.0, 0.0])
	for i: int in cds.size():
		if float(cds[i]) > float(prev[i]):
			var cost := float(m.hero_defs[hero]["abilities"][i]["mana_cost"])
			rows.append({"kind": "out", "tick": tick, "ev": "ability",
					"hero": hero, "ability": i, "cd": float(cds[i]),
					"cost": cost, "blue": float(m.blue),
					"blue_max": float(m.blue_max),
					"checks": {"armed": float(cds[i]) > 0.0,
							"cost_from_data": cost > 0.0,
							"blue_le_cap": float(m.blue) <= float(m.blue_max)}})
	_cd_prev[hero] = cds.duplicate()
	return rows


func _end_row(m, graph: Dictionary, tick: int) -> void:
	var state = graph["state"]
	var save = graph["save"]
	_emit({"kind": "out", "tick": tick, "ev": "outcome",
			"outcome": m.outcome, "wave": int(m.wave),
			"boss_hp": float(m.boss_hp) if m.boss_hp != null else 0.0,
			"green": int(m.green),
			"blue": float(m.blue), "blue_max": float(m.blue_max),
			"max_alive": _max_alive, "loot_events": m.loot_events.size(),
			"bank_count": state.bank.size(), "materials": state.materials,
			"saved_ack": int(state.saved_ack), "write_seq": int(save.write_seq),
			"checks": {
				"outcome_win": String(m.outcome) == "win",
				"win_at_last_wave": int(m.wave) \
						== SIM_WAVE.total_waves(m.waves_file) - 1,
				# C7/C12: a breacher is CONSUMED at the core (a breach is
				# not a kill, no rewards) — the golden's win path is the
				# wave-10 clear with the boss eaten at the core: boss seen,
				# lanes empty, core still standing.
				"boss_neutralized": m.boss != null and int(m.alive) == 0,
				"alive_cap_i7": _max_alive <= int(m.balance.get("max_alive", 0)),
				"blue_capped": _blue_capped,
				"bank_is_tray_plus_chest": state.bank.size() \
						== m.loot_events.size() + 1,
				"ack_mirror": int(state.saved_ack) == int(save.write_seq),
			}})


func _c9_shape(item: Dictionary) -> bool:
	if item.size() != C9_KEYS.size():
		return false
	for key: String in C9_KEYS:
		if not item.has(key):
			return false
	return true


func _emit(row: Dictionary) -> void:
	var checks: Dictionary = row["checks"]
	var ok := true
	for key: String in checks:
		if not bool(checks[key]):
			ok = false
	row["ok"] = ok
	if not ok:
		_bad += 1
	print(JSON.stringify(row))
