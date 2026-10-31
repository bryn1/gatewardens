"""v1.4 P5 selection ring on the ONE existing ring mechanism
(MC card 11837 / V14-PLAN row P5, wave W2).

The contract (plan row P5 + the declared priority rule): ONE RangeRing
node — scripts/range_ring.gd, the G4 TorusMesh mechanism, geometry and
show/hide stay THERE — driven per frame by scripts/selection_ring.gd
(mission.tscn root-last mount, the fx_director mount ruling) from
EXISTING published state only, priority ARMED > SELECTED > HIDDEN:
ARMED (picker armed, G5) -> ring AT the armed slot, ARMED color
(RING_COLOR — the G4 yellow, byte-kept); else SELECTED defense (panel.
selected_uid, W17c player path) -> ring AT the defense, SELECTED color,
radius through the SAME placer.tier_range data door at the obj's tier;
else hidden. mission.gd carries ZERO new lines (LOC gate 399/400 — the
scene mount needs no code line); zero new sim fields, zero new node
types (the driver creates NOTHING — source-truth below), camera diff
EMPTY.

Harness = the P1/F3 idiom verbatim: conftest.run_probe_script, probe
generated into tmp_path (R5), REAL mission.tscn boot + REAL panel +
main.gd relay fed SYNTHESIZED InputEvents, picker presses through the
production button signal; P5-* machine rows, IN-PROBE P5-FAIL guards,
P5-OK LAST (a silent skip cannot go green), EMPTY stderr. The driver is
driven by hand (ring_step) — under `-s` no _process dispatches (E5),
the fx_step idiom; deterministic, zero wave flakiness.

Declared readings (wave log): "armed slot/hover" realizes as the ghost
slot (v1 ships no free-cursor hover — the ghost IS the aim); deselect
teardown rides the shipped panel.select_defense(0) door (0 = "no
defense selected", defense_panel.gd:79 — the player has no separate
deselect control; sell's reset is the same field).

PLANTED-RED x1 (wave log transcripts, RED row beside GREEN): the
priority branch loses its precedence (armed guard gains an
`and selected==0` term = selected outranks armed when both — the
inversion the priority row exists to catch) -> P5-PRI goes RED rc1
in-probe, other rows stay green; the driver was STAGED first (F4
lesson) so `git checkout --` + diff-vs-index reverts the plant only.
"""

import json
from pathlib import Path

import conftest

GODOT = Path(conftest.repo_path("godot"))
DRIVER_GD = GODOT / "scripts" / "selection_ring.gd"
RING_GD = GODOT / "scripts" / "range_ring.gd"
TSCN = GODOT / "scenes" / "mission.tscn"
TOWERS_JSON = GODOT / "data" / "towers.json"

PROBE_SRC = '''
extends SceneTree
# gw P5 selection-ring probe (MC 11837). Machine rows: P5-MOUNT /
# -HIDE0 / -ARM / -PLACE / -SEL / -PRI / -RMB / -TEARDOWN / P5-OK
# (LAST print). Any failed check prints P5-FAIL <detail> + quit(1).
# Boot + real-relay idiom = g4_range_ring_probe; the driver node is
# driven by hand (E5: -s dispatches no _process, fx_step idiom).
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MAIN := preload("res://scripts/main.gd")
const RANGE_RING := preload("res://scripts/range_ring.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const DT := 0.05
const EPS := 0.001

var _m = null
var _panel = null
var _drv = null
var _main = null          # the REAL main.gd relay object (no _ready)
var _failed := false      # completion flag (G4 lesson): a FAIL row
                          # must NOT be followed by P5-OK/quit(0)
var _ranges := {}         # id -> [range per TIER 1..5] (probe-derived)


func _fail(why: String) -> void:
	_failed = true
	print("P5-FAIL " + why)
	quit(1)


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
	rng.seed = 11837
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	_m = m
	_panel = m.get_node_or_null("DefensePanel")
	if _panel == null:
		_fail("shipped panel not mounted by mission.setup")
		return
	# THE mount leg: the SHIPPED scene, not a probe-built node.
	_drv = m.get_node_or_null(NodePath("SelectionRing"))
	if _drv == null:
		_fail("MOUNT: mission.tscn does not ship SelectionRing")
		return
	print("P5-MOUNT mounted=1")
	_main = MAIN.new()
	_main.bridge = m.bridge            # the SAME bridge the mission pumps
	                                      # (g4 relay idiom; no _ready boot)
	# Expectations FIRST: the probe's OWN walk of the SAME data door
	# (DATA legs compare the ring against THIS, never against placer).
	for row: Dictionary in tables.rows("towers"):
		var tiers: Array = row["tiers"]
		var rs: Array = []
		for t: Dictionary in tiers:
			rs.append(float(t["range"]))
		_ranges[String(row["id"])] = rs
	_legs()
	_main.free()
	if _failed:
		return               # the FAIL row's quit(1) stands; no P5-OK
	print("P5-OK")
	quit(0)


func _legs() -> void:
	# ---- HIDE0 default: clean state + one drive pass -> NOTHING ----
	if bool(_panel.armed) or int(_panel.selected_uid) != 0:
		_fail("HIDE0 premise: armed/selected not clean at boot")
		return
	_drv.ring_step()
	var nd = _ring()
	if nd != null and nd.visible:
		_fail("HIDE0: ring renders with no armed row & no selection")
		return
	print("P5-HIDE0 node=%d visible=%d armed=0 selected=0" % [
			1 if nd != null else 0,
			1 if nd != null and nd.visible else 0])

	# ---- ARMED row: REAL picker press -> ARMED color AT the slot ----
	_press_family("ballista")
	_drv.ring_step()
	var want: float = (_ranges["ballista"] as Array)[0]
	var nd2 = _ring()
	if nd2 == null or not nd2.visible:
		_fail("ARM: armed ballista rendered nothing (T1 range %s)" % str(want))
		return
	var ok_pos := _at_slot(nd2)
	var col := _color(nd2)
	if not ok_pos or col != "ARMED":
		_fail("ARM: ring %s at %s (want slot pos, ARMED color)" % [col,
				str(nd2.position)])
		return
	print("P5-ARM fam=ballista vis=1 color=%s posok=1 want=%.1f scale=%.1f" \
			% [col, want, nd2.scale.x])

	# ---- place through the REAL LMB, then SELECT via the player row --
	var c0: int = _m.defense_list.size()
	_mouse(MOUSE_BUTTON_LEFT)
	if _m.defense_list.size() != c0 + 1:
		_fail("PLACE: real LMB did not confirm the armed row")
		return
	var uid := int(_m.defense_list[_m.defense_list.size() - 1]["uid"])
	var row = _panel.rows_ui.defense_rows.get_node_or_null(
			NodePath("Row_%d" % uid))
	if row == null:
		_fail("PLACE: the placed defense has no selectable Row_%d" % uid)
		return
	row.pressed.emit()                 # the W17c player select path
	if int(_panel.selected_uid) != uid:
		_fail("SELECT row press did not set selected_uid=%d" % uid)
		return
	var pre = _ring()
	if pre != null and pre.visible:
		# Nothing but the driver may paint a SELECTION ring (selection
		# is no ghost chokepoint) — pre-drive it must still be hidden.
		_fail("SEL premise: something else showed the ring on select")
		return
	_drv.ring_step()
	var nd3 = _ring()
	var obj = _obj(uid)
	if nd3 == null or not nd3.visible:
		_fail("SEL: selected defense rendered nothing")
		return
	var col3 := _color(nd3)
	if col3 != "SELECTED" or not _at_pos(nd3, obj.pos) \
			or absf(nd3.scale.x - want) > EPS:
		_fail("SEL: ring %s at %s scale %s, want SELECTED at %s r=%s" % [
				col3, str(nd3.position), str(nd3.scale), str(obj.pos),
				str(want)])
		return
	print("P5-SEL uid=%d vis=1 pre=0 color=%s posok=1 want=%.1f scale=%.1f" \
			% [uid, col3, want, nd3.scale.x])

	# ---- PRIORITY: arm while the selection stands -> ARMED wins ----
	_press_family("ballista")
	if int(_panel.selected_uid) != uid:
		_fail("PRI premise: arming dropped the selection")
		return
	_drv.ring_step()
	var nd4 = _ring()
	var col4 := "NONE" if nd4 == null or not nd4.visible else _color(nd4)
	var sep := 1000.0
	if nd4 != null:
		sep = Vector2(nd4.position.x - obj.pos.x,
				nd4.position.z - obj.pos.z).length()
	if col4 != "ARMED" or not _at_slot(nd4) or sep <= EPS:
		var where: String = "nil" if nd4 == null else str(nd4.position)
		_fail("PRI: want ARMED at the ghost slot apart from the tower, "
				+ "got " + col4 + " at " + where + " sep=" + str(sep))
		return
	print("P5-PRI color=%s posok=1 selected=%d sep=%.2f" % [col4, uid, sep])

	# ---- disarm (REAL RMB) falls back to the standing selection ----
	_mouse(MOUSE_BUTTON_RIGHT)
	if bool(_panel.armed) or int(_panel.placer.ghost) != -1:
		_fail("RMB premise: cancel left the aim armed")
		return
	_drv.ring_step()
	var nd5 = _ring()
	var col5 := "NONE" if nd5 == null or not nd5.visible else _color(nd5)
	if col5 != "SELECTED" or not _at_pos(nd5, obj.pos):
		_fail("RMB: disarming did not fall back to SELECTED (got %s)" % col5)
		return
	print("P5-RMB armed=0 fallback=%s selected=%d" % [col5, uid])

	# ---- deselect (shipped select_defense(0) door) -> hidden --------
	_panel.select_defense(0)
	if int(_panel.selected_uid) != 0:
		_fail("TEARDOWN premise: select_defense(0) kept a selection")
		return
	_drv.ring_step()
	var nd6 = _ring()
	if nd6 == null or nd6.visible:
		_fail("TEARDOWN: ring still rendering after disarm+deselect")
		return
	print("P5-TEARDOWN node=1 visible=0 armed=0 selected=0")


# ---------- production-entry helpers (g5_real_relay/g4 idiom) ----------

func _press_family(fam: String) -> void:
	for row: Dictionary in _panel.picker_rows:
		if String(row["id"]) == fam:
			(row["btn"] as Button).pressed.emit()
			return
	_fail("picker row %s has no button" % fam)


func _mouse(btn_idx: int) -> void:
	for down: bool in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = btn_idx
		ev.pressed = down
		_main._unhandled_input(ev)
	_m.step(DT)                        # the shipped pump pair verbatim


func _ring():
	return _m.get_node_or_null(NodePath(RANGE_RING.RING_NAME))


func _obj(uid: int):
	for rec: Dictionary in _m.defense_list:
		if int(rec["uid"]) == uid:
			return rec["obj"]
	_fail("no defense record uid %d" % uid)
	return null


# Which STATE tone is painted (the G4 CLASS leg material shape, pinned:
# unshaded + alpha; only the COLOR varies per state).
func _color(nd) -> String:
	var mat := nd.material_override as StandardMaterial3D
	if mat == null or int(mat.shading_mode) != 0 or int(mat.transparency) \
			!= 1:
		return "BADMAT"
	if mat.albedo_color == RANGE_RING.RING_COLOR:
		return "ARMED"
	if mat.albedo_color == RANGE_RING.SELECTED_COLOR:
		return "SELECTED"
	return "OTHER"


func _at_pos(nd, at: Vector3) -> bool:
	return absf(nd.position.x - at.x) <= EPS \
			and absf(nd.position.z - at.z) <= EPS \
			and absf(nd.position.y - RANGE_RING.RING_Y) <= EPS


func _at_slot(nd) -> bool:
	var g: int = int(_panel.placer.ghost)
	if g < 0:
		return false
	return _at_pos(nd, _panel.placer.slots[g])
'''


def _run_probe(tmp_path):
    probe = Path(tmp_path) / "p5_selection_ring_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), (), tmp_path / "user_home")


def _only(out, tag):
    r = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert len(r) == 1, "expected exactly one %s row:\n%s" % (tag, out)
    return dict(x.split("=", 1) for x in r[0].split(" ")[1:])


def _towers_t1(tower_id):
    rows = json.loads(TOWERS_JSON.read_text(encoding="utf-8"))
    rows = rows["towers"] if isinstance(rows, dict) else rows
    for row in rows:
        if row["id"] == tower_id:
            return float(row["tiers"][0]["range"])
    raise AssertionError("towers.json lost %s" % tower_id)


def test_p5_selection_ring(tmp_path, class_cache):
    proc = _run_probe(tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "P5-FAIL" not in out, out
    assert out.rstrip().endswith("P5-OK"), \
        "P5-OK must be the LAST row (a skipped leg cannot reach it)"

    assert _only(out, "P5-MOUNT")["mounted"] == "1", \
        "the driver is not shipped in mission.tscn"

    # hidden-default: clean state + one drive pass renders NOTHING (the
    # node is lazy — node=0 counts as hidden, the G4 HIDE0 idiom).
    h0 = _only(out, "P5-HIDE0")
    assert h0["visible"] == "0" and h0["armed"] == "0" \
        and h0["selected"] == "0", h0

    # ARMED row: color + pos pinned in-probe; the radius re-checked HERE
    # against towers.json (DATA leg, independent of any implementation).
    arm = _only(out, "P5-ARM")
    assert arm["vis"] == "1" and arm["color"] == "ARMED" \
        and arm["posok"] == "1", arm
    t1 = _towers_t1("ballista")
    assert abs(float(arm["want"]) - t1) < 0.01, (arm, t1)
    assert abs(float(arm["scale"]) - t1) < 0.01, (arm, t1)

    # SELECTED row: the ring stands on the DEFENSE (pos + SELECTED color
    # in-probe); pre=0 pins nothing-but-the-driver wrote it; the radius
    # is the SAME tier-row number through the tier_range door.
    sel = _only(out, "P5-SEL")
    assert sel["vis"] == "1" and sel["pre"] == "0" \
        and sel["color"] == "SELECTED" and sel["posok"] == "1", sel
    assert int(sel["uid"]) > 0, sel
    assert abs(float(sel["scale"]) - t1) < 0.01, (sel, t1)

    # PRIORITY row: armed OVER a standing selection — ARMED color at the
    # ghost slot, the selection intact (selected>0), the two apart.
    pri = _only(out, "P5-PRI")
    assert pri["color"] == "ARMED" and pri["posok"] == "1", pri
    assert int(pri["selected"]) > 0 and float(pri["sep"]) > 0.001, pri

    # disarm falls back to the selection (the state machine, not a
    # hide-on-everything driver).
    rmb = _only(out, "P5-RMB")
    assert rmb["armed"] == "0" and rmb["fallback"] == "SELECTED" \
        and int(rmb["selected"]) > 0, rmb

    # teardown: disarm + deselect -> hidden, node persists.
    td = _only(out, "P5-TEARDOWN")
    assert td["visible"] == "0" and td["node"] == "1" \
        and td["armed"] == "0" and td["selected"] == "0", td

    # ---- source truth: ONE ring, ZERO new node types, pump mount ----
    drv = DRIVER_GD.read_text(encoding="utf-8")
    ring = RING_GD.read_text(encoding="utf-8")
    assert ".new()" not in drv, \
        "the driver constructs NOTHING (zero new node types)"
    assert ring.count("MeshInstance3D.new()") + drv.count(
        "MeshInstance3D.new()") == 1, "ONE ring node site"
    assert ring.count("TorusMesh.new()") == 1, "ONE geometry site"
    tscn = TSCN.read_text(encoding="utf-8")
    assert 'name="SelectionRing"' in tscn and "selection_ring.gd" in tscn, \
        "mission.tscn must ship the mount (the pump, zero mission.gd lines)"
    mission = (GODOT / "scripts" / "mission.gd").read_text(encoding="utf-8")
    assert "selection_ring" not in mission \
        and "SelectionRing" not in mission, \
        "mission.gd carries ZERO P5 lines"

    # the gate metric (wave-log LOC rows): files stay under the ceilings
    for path, cap in ((DRIVER_GD, 400), (RING_GD, 400)):
        assert len(path.read_text(encoding="utf-8").split("\n")) <= cap, path
