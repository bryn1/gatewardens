# g4_range_ring_probe — the G4 yellow range ring headless proof (v1.2.1,
# MC card 11707 / V121-PLAN row G4 + §4). Boot + real-relay idiom =
# g5_real_relay_probe: the REAL mission boots, the REAL panel is mounted
# by mission.setup, and main.gd's script is mounted as the relay object
# (_ready NEVER runs — no app boot) fed SYNTHESIZED InputEvents; picker
# presses fire through the production GUI signal (btn.pressed.emit()).
# The ring node ("RangeRing", the mission-root child range_ring.gd lazy-
# creates) is read directly; expectations re-derive the ranges from the
# tables rows INDEPENDENTLY of placer.tier_range (the DATA leg compares
# implementation vs data, never vs itself). Rows (machine lines; any
# failure prints G4-FAIL <why> and quits 1; G4-OK LAST, completion-flag
# guarded — the G2 mid-abort lesson):
#  HIDE0 pre-arm: NO ghost & NO selection -> the ring renders nothing
#        (node absent = renders nothing too; printed node=0). NEGATIVE leg.
#  DATA  for every sampled family a REAL picker press arms: ghost >= 0,
#        ring visible, node scale.x == scale.z == the towers.json T1
#        range number (BOTH printed), position == the ghost slot xz at y
#        RING_Y. gate_blockade: visible=0 WITH ghost >= 0 — the RANGE-0
#        leg riding the same press loop, non-vacuous because the PREVIOUS
#        sampled rows printed visible=1 for the same node.
#  CLASS the WEB-PROOF PROXY (the G2 ArrayMesh lesson, MC 11698): the
#        ring mesh is a TorusMesh AND a PrimitiveMesh, and the material
#        is the pinned lit-translucent shape (unshaded + alpha +
#        RING_COLOR). The served-browser pixel re-check is the
#        orchestrator's leg.
#  TIER  placer.tier_range(id, t) == the JSON tiers[t-1]["range"] for
#        t = 1..5 of EVERY family (BOTH printed) — the ring's radius
#        lookup sampled across tiers; plus the non-vacuity row for the
#        planted-red: >= 1 family whose T2 range differs from T1 (the
#        tier-index swap MUST be able to change a number).
#  CYCLE a real InputEventKey(KEY_RIGHT) through the forwarder moves the
#        ghost forward AND the ring moves with it (position == the new
#        slot, still visible).
#  PLACE a real MOUSE_BUTTON_LEFT confirms: +1 defense, ring hidden
#        (place hides — lifecycle leg).
#  RMB   a real MOUSE_BUTTON_RIGHT cancels an armed ring: armed 0,
#        ghost -1, ring hidden (lifecycle leg).
#  LOCK  armed -> ring visible; phase_kind "combat" + one step (the W17e
#        sync runs the ONE _cancel_arm route): ring hidden, armed 0
#        (combat-lock lifecycle leg).
#  R0    the FIVE gate_blockade tier rows re-read from the tables carry
#        range 0.0 each (premise pinned), and with gate_blockade ARMED
#        (ghost >= 0) the ring stays hidden; RE-ARMING ballista makes the
#        SAME node paint again (repaint=1) — the R0 treatment is the
#        RANGE, not a dead mechanism.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MAIN := preload("res://scripts/main.gd")
const RANGE_RING := preload("res://scripts/range_ring.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const DT := 0.05
const EPS := 0.001                         # float-compare tolerance, u
const UNSHADED := 0                        # pinned material shape (g2)
const ALPHA := 1
const FAMILIES := ["ballista", "bombard", "hailspire_tower", "barbed_snare"]

var _failed := false
var _done := false
var _frames := 0
var _m = null
var _panel = null
var _placer = null
var _main = null          # the REAL main.gd relay object (no _ready)
var _ranges := {}         # id -> [range per TIER 1..5] (probe-derived)


func _init() -> void:
	root.size = Vector2i(1280, 720)
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	graph["state"].set_deck(DECK.duplicate())
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()
	var rng := RandomNumberGenerator.new()
	rng.seed = 11707
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	if String(m.phase_kind) != "build":
		_fail("mission setup did not land the build phase")
		return
	_m = m
	_panel = m.get_node_or_null("DefensePanel")
	if _panel == null:
		_fail("shipped panel not mounted by mission.setup")
		return
	_placer = _panel.placer
	_main = MAIN.new()                 # script instance; NEVER add_child:
	_main.bridge = graph["bridge"]     # _ready would boot the whole app
	# Expectations FIRST: probe's own walk of the SAME data door the sim
	# reads (the DATA leg compares the ring's scale against THIS, never
	# against placer.tier_range).
	for row: Dictionary in tables.rows("towers"):
		var tiers: Array = row["tiers"]
		var rs: Array = []
		for t: Dictionary in tiers:
			rs.append(float(t["range"]))
		_ranges[String(row["id"])] = rs
	if _ranges.size() != 5:
		_fail("towers.json families drifted: %d rows" % _ranges.size())


func _process(_delta: float) -> bool:
	if _failed:
		return true
	_frames += 1
	if _frames == 4:
		_legs()
		_main.free()                    # a Node: un-freed it leaks onto
		                                # stderr (EMPTY-stderr ruling)
		if not _failed:
			# A runtime error aborts _legs SILENTLY (rc stays 0, g2
			# lesson) — only the completion flag proves the leg ran.
			if not _done:
				_fail("ring pass aborted mid-way (completion flag unset)")
			else:
				print("G4-OK")
				quit(0)
	return false


func _legs() -> void:
	# ---- HIDE0: no ghost & no selection -> renders nothing (NEGATIVE) ----
	if int(_placer.ghost) != -1 or int(_panel.selected_uid) != 0:
		_fail("HIDE0 premise: pre-arm ghost/selection not clean")
		return
	var node = _ring()
	if node != null and node.visible:
		_fail("HIDE0: ring renders with no ghost & no selection")
		return
	print("G4-HIDE0 node=%d selected=0 ghost=-1 visible=%d" % [
			1 if node != null else 0,
			1 if node != null and node.visible else 0])

	# ---- DATA (+ embedded RANGE-0): real picker press per family ----
	for fam: String in FAMILIES + ["gate_blockade"]:
		_press_family(fam)
		if _failed:
			return
		var want: float = (_ranges[fam] as Array)[0]   # T1, probe-derived
		var nd = _ring()
		var vis: bool = nd != null and nd.visible
		if int(_placer.ghost) < 0:
			_fail("DATA %s: press armed no ghost" % fam)
			return
		if want <= 0.0:
			if vis:
				_fail("R0 %s: range-0 row renders a ring" % fam)
				return
			print("G4-R0 %s ghost=%d visible=0 want=%.1f scale=%.1f" % [
					fam, int(_placer.ghost), want, 0.0])
		else:
			if not vis:
				_fail("DATA %s: positive range rendered nothing" % fam)
				return
			var sc: float = nd.scale.x
			var pos: Vector3 = _placer.slots[int(_placer.ghost)]
			var ok_pos: bool = absf(nd.position.x - pos.x) <= EPS \
					and absf(nd.position.z - pos.z) <= EPS \
					and absf(nd.position.y - RANGE_RING.RING_Y) <= EPS \
					and absf(nd.scale.z - sc) <= EPS
			if not ok_pos:
				_fail("DATA %s: ring at %s scale %s, want slot %s r=%s" \
						% [fam, str(nd.position), str(nd.scale),
						str(pos), str(sc)])
				return
			print("G4-DATA %s tier=1 want=%.1f scale=%.1f vis=1" \
					% [fam, want, sc])
			if absf(sc - want) > EPS:
				_fail("DATA %s: scale %s != towers.json range %s" \
						% [fam, str(sc), str(want)])
				return
			if fam == "ballista":
				_class(nd)
				if _failed:
					return
		_panel._cancel_arm()

	# ---- TIER: the ring's radius lookup, sampled across tiers ----
	var variance := 0
	for fam: String in _ranges:
		var rs: Array = _ranges[fam]
		for t: int in rs.size():
			var got: float = _placer.tier_range(fam, t + 1)
			if absf(got - float(rs[t])) > EPS:
				_fail("TIER %s T%d: tier_range=%s want=%s" % [
						fam, t + 1, str(got), str(rs[t])])
				return
			print("G4-TIER %s tier=%d want=%.1f got=%.1f" % [
					fam, t + 1, float(rs[t]), got])
		if absf(float(rs[1]) - float(rs[0])) > EPS:
			variance += 1
	if variance < 1:
		_fail("TIER non-vacuous premise: no family differs T1 vs T2")
		return
	print("G4-TIERDIFF families=%d" % variance)

	# ---- CYCLE: a real KEY_RIGHT moves ghost AND ring ----
	_press_family("ballista")
	var free: Array = _placer.buildable()
	if free.size() < 2:
		_fail("CYCLE premise: buildable() < 2 slots")
		return
	_key(KEY_RIGHT)
	if int(_placer.ghost) != int(free[1]):
		_fail("CYCLE: ghost=%d want %d" % [int(_placer.ghost), int(free[1])])
		return
	var nd2 = _ring()
	var pos2: Vector3 = _placer.slots[int(free[1])]
	if nd2 == null or not nd2.visible \
			or absf(nd2.position.x - pos2.x) > EPS \
			or absf(nd2.position.z - pos2.z) > EPS:
		_fail("CYCLE: ring did not move with the ghost")
		return
	print("G4-CYCLE fwd=%d vis=1" % int(free[1]))

	# ---- PLACE: real LMB confirms, the ring HIDES ----
	var c0: int = _m.defense_list.size()
	_mouse(MOUSE_BUTTON_LEFT)
	if _m.defense_list.size() != c0 + 1:
		_fail("PLACE: real LMB did not confirm")
		return
	if _ring_vis():
		_fail("PLACE: ring stayed visible after a successful place")
		return
	print("G4-PLACE placed=1 vis=0 count=%d" % _m.defense_list.size())

	# ---- RMB: arm, real right-click cancels, the ring HIDES ----
	_press_family("bombard")
	if not _ring_vis():
		_fail("RMB premise: bombard arm rendered nothing (r=12.0)")
		return
	_mouse(MOUSE_BUTTON_RIGHT)
	if _ring_vis() or int(_placer.ghost) != -1 or bool(_panel.armed):
		_fail("RMB: cancel did not hide the ring")
		return
	print("G4-RMB vis=0 ghost=-1 armed=0")

	# ---- LOCK: combat hides the ring through the ONE cancel route ----
	_press_family("bombard")
	if not _ring_vis():
		_fail("LOCK premise: ring not visible before the lock")
		return
	_m.green = int(_m.green) + 300       # afford true: phase is the gate
	_m.phase_kind = "combat"
	_m.step(DT)                           # one poll -> W17e sync
	if _ring_vis() or bool(_panel.armed):
		_fail("LOCK: combat did not hide the armed ring")
		return
	print("G4-LOCK vis=0 armed=0")

	# ---- R0 sweep: blockade premise + repaint (non-vacuous) ----
	var bt: Array = _ranges["gate_blockade"]
	if bt.size() != 5:
		_fail("R0 premise: gate_blockade has %d tier rows" % bt.size())
		return
	for t: int in bt.size():
		if float(bt[t]) > 0.0:
			_fail("R0 premise: blockade T%d range=%s" % [t + 1, str(bt[t])])
			return
	_press_family("gate_blockade")
	if int(_placer.ghost) < 0 or _ring_vis():
		_fail("R0: armed blockade rendered a ring")
		return
	_panel._cancel_arm()
	_press_family("ballista")
	var rep := _ring_vis()
	_panel._cancel_arm()
	if not rep:
		_fail("R0 repaint: ring node dead after blockade arms")
		return
	print("G4-R0SWEEP zero_rows=5 armed_hidden=1 repaint=1")

	# ---- final HIDDEN: no ghost (and no selection) -> hidden again ----
	if int(_placer.ghost) != -1 or int(_panel.selected_uid) != 0 \
			or _ring_vis():
		_fail("final HIDDEN: ring left visible with no ghost/selection")
		return
	print("G4-HIDE1 ghost=-1 selected=0 vis=0")
	_done = true


# ---------- production-entry helpers (g5_real_relay idiom) ----------

# The family's OWN picker button (winner class rows AND Family_ rows all
# carry row["btn"] from build_class_buttons) pressed through the shipped
# signal — the same press a served-browser click lands.
func _press_family(fam: String) -> void:
	for row: Dictionary in _panel.picker_rows:
		if String(row["id"]) == fam:
			(row["btn"] as Button).pressed.emit()
			return
	_fail("picker row %s has no button" % fam)


func _ring():                          # -> MeshInstance3D | null
	return _m.get_node_or_null(NodePath(RANGE_RING.RING_NAME))


func _ring_vis() -> bool:
	var nd = _ring()
	return nd != null and nd.visible


# Pinned WEB-PROOF PROXY + material shape (g2 LB-CLASS idiom): engine-
# managed PrimitiveMesh geometry, unshaded + alpha + RING_COLOR.
func _class(nd: MeshInstance3D) -> void:
	if nd.mesh == null or not nd.mesh is TorusMesh \
			or not nd.mesh is PrimitiveMesh:
		var cls := "null" if nd.mesh == null else nd.mesh.get_class()
		_fail("CLASS: ring mesh is %s (want TorusMesh/PrimitiveMesh)" % cls)
		return
	var mat := nd.material_override as StandardMaterial3D
	if mat == null or int(mat.shading_mode) != UNSHADED \
			or int(mat.transparency) != ALPHA \
			or mat.albedo_color != RANGE_RING.RING_COLOR:
		_fail("CLASS: ring is not the pinned lit-translucent shape")
		return
	print("G4-CLASS mesh=TorusMesh prim=1 mat=1")


func _key(kc: int) -> void:
	_key_press(kc, true)
	_m.step(DT)
	_key_press(kc, false)
	_m.step(DT)


func _key_press(kc: int, down: bool) -> void:
	var ev := InputEventKey.new()
	ev.physical_keycode = kc
	ev.keycode = kc
	ev.pressed = down
	_main._unhandled_input(ev)


func _mouse(btn_idx: int) -> void:
	for down: bool in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = btn_idx
		ev.pressed = down
		_main._unhandled_input(ev)
	_m.step(DT)


func _fail(why: String) -> void:
	_failed = true
	print("G4-FAIL " + why)
	quit(1)
