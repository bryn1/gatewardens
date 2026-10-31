"""v1.4 P6 tower-row grey/red icon states (MC 11854 / V14-PLAN row P6,
wave W3) — BUILD card on the EXISTING defense_rows_ui.gd; the pathspec
commit proves the footprint: godot/scripts/defense_rows_ui.gd (the one
painter) + THIS file + LEDGER/log — defense_panel.gd, mission.gd,
camera and the fixtures stay byte-EMPTY (gate rows in
.audits/20261031-1830-v14-plan/P6-wave.log).

STATE MAP (the card's; DECLARED against the older plan-row wording,
which pre-dates the DA phase-source verification the card cites):
UNAFFORDABLE (cost > green, read through the shipped can_afford static)
-> GREY (darken/desaturate modulate, the hud._tint_down named-tone
idiom); COMBAT phase (phase_kind, live writers phase_controller
_enter_build/_enter_combat) -> RED on the rows that COULD build;
affordable + BUILD -> neutral identity white. Overlap reading (literal
in the brief — RED-tint the BUILDABLE rows): affordability wins, an
unaffordable row is not buildable so combat never paints it red.
Presentation ONLY: the two ENFORCEMENT rows re-run the shipped
refusals UNDER the painted state (grey rows still answer why:"green",
red rows still answer why:"phase", zero state writes) — the tints
never enforce anything.

Harness rows (machine lines, the P1 tmp-probe idiom — conftest
.run_probe_script into tmp_path, R5; E5: the probe hand-drives the
shipped pump pair p.poll(m.bridge.drain_presses()) with NO world step;
the F3 :235/:237 phase_kind+in_combat write/restore pair):
  BOOT        neutral default — start green over every towers.json
              cost, every picker row neutral (costs csv re-derived
              here from towers.json: the cost numbers stay DATA);
  DRILL       harness green write BELOW the cheapest cost (declared
              cap-leg idiom: write, check, restore next act) -> every
              row grey, tints compared hex-exact python-side;
  ENFG        the grey rows stay refused (why=green, green/list fixed);
  GREENBACK   green restored -> neutral again;
  COMBAT      F3 combat write -> every affordable row RED;
  ENFP        the red rows stay refused (why=phase, green/list fixed);
  PHASEBACK   phase restored -> neutral again;
  TEARDOWN    clean — rows neutral, green + phase byte-equal to the
              BOOT reads, defense list empty.
IN-PROBE P6-FAIL guards quit(1) AND return; P6-OK is the LAST print —
the P5 lesson made structural (no P6-OK after a FAIL row; quit(0) once
overwrote quit(1) in the wild). The grey/red hexes are READ from the
shipped source (the _save_name source-truth idiom) and re-checked
STRUCTURALLY here (grey: equal channels under white = desaturated +
darkened; red: red channel dominant) — the probe-side constant compare
can never agree with a plant and stay green.

PLANTED-RED x1 (P6-wave.log transcript, byte-verified revert): the
affordability predicate inverted in _paint_states (sed "not
SIM_ECONOMY.can_afford" -> "SIM_ECONOMY.can_afford") -> DRILL goes RED
(drilled-green rows answer white, not grey), P6-OK never prints,
pytest rc 1 -> git checkout -- + diff-vs-index REVERT_VERIFIED -> the
green re-run.
"""

import json
import re
from pathlib import Path

import conftest

GODOT = Path(conftest.repo_path("godot"))
ROWS_GD = GODOT / "scripts" / "defense_rows_ui.gd"

_TOWERS = json.loads((GODOT / "data" / "towers.json").read_text(
        encoding="utf-8"))
_ROWS = _TOWERS["towers"] if isinstance(_TOWERS, dict) else _TOWERS

# The picker-row ORDER defense_rows_ui.build_class_buttons builds:
# classes() winners (FIRST row per class, file order) then the non-
# winner family rows (file order) — the cost csv the probe prints is
# re-derived from towers.json through THIS same rule (data, never a
# hand-copy of the numbers).
def _picker_costs():
    seen, winners, fam = set(), [], []
    for r in _ROWS:
        if r["class"] in seen:
            fam.append(int(r["base_cost"]))
        else:
            seen.add(r["class"])
            winners.append(int(r["base_cost"]))
    return winners + fam


def _tint_consts():
    """The shipped presentation hexes, READ from the source (source-
    truth idiom); Color() string hexes are blanked by the I2 gate's BN1
    pre-pass, so they exist for THIS reader and no governed literal."""
    src = ROWS_GD.read_text(encoding="utf-8")
    out = {}
    for name in ("TINT_GREY", "TINT_RED", "TINT_NEUTRAL"):
        m = re.search(r'const %s := Color\("([0-9a-fA-F]{6})"\)' % name,
                      src)
        assert m, "shipped tint const %s not found in defense_rows_ui.gd" % name
        out[name] = m.group(1).lower()
    return out


PROBE_SRC = '''
extends SceneTree
# gw icon-states probe (v1.4 P6, MC 11854). Machine rows: P6-BOOT /
# -DRILL / -ENFG / -GREENBACK / -COMBAT / -ENFP / -PHASEBACK /
# -TEARDOWN / P6-OK (LAST print). Any failed check prints P6-FAIL
# <detail> + quit(1) AND returns — a FAIL row can never be followed by
# P6-OK (the P5 completion-flag lesson). DECLARED (test docstring):
# the green drill is the harness-caller cap-leg write, restored one
# act later; the combat entry is the F3 :235/:237 drive-real-entry-
# points pair; every pump is the shipped pair with NO world step.
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const ROWS_UI := preload("res://scripts/defense_rows_ui.gd")
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]

var m = null
var placer = null


func _fail(why: String) -> void:
	print("P6-FAIL " + why)
	quit(1)


func _pump(p) -> void:
	p.poll(m.bridge.drain_presses())   # E5 hand-driven shipped pump


func _tints(p) -> Array:
	# [white, grey, red, tints-csv] over the picker rows, build order.
	# Classification is the SHIPPED consts compared; the raw hex csv
	# travels so python re-judges it against the source independently.
	var w := 0
	var g := 0
	var r := 0
	var csv := ""
	for row: Dictionary in p.picker_rows:
		var b: Button = row["btn"]
		var col: Color = b.modulate
		if csv != "":
			csv += ","
		csv += col.to_html().to_lower()
		if col == ROWS_UI.TINT_GREY:
			g += 1
		elif col == ROWS_UI.TINT_RED:
			r += 1
		elif col == ROWS_UI.TINT_NEUTRAL:
			w += 1
	return [w, g, r, csv]


func _init() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	var st = graph["state"]
	st.set_deck(DECK.duplicate())      # smoke-idiom deck (P1 boot)
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		print("P6-FAIL mission.tscn not loadable")
		quit(1)
		return
	m = packed.instantiate()
	root.add_child(m)
	m._ready()                         # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = 11854                   # pinned seed, smoke idiom
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	var p = m.get_node("DefensePanel")
	placer = p.placer

	# BOOT — neutral default: BUILD phase, start green over EVERY cost.
	_pump(p)
	var t: Array = _tints(p)
	var costs := ""
	for row: Dictionary in p.picker_rows:
		if costs != "":
			costs += ","
		costs += str(int(row["cost"]))
	print("P6-BOOT rows=%d costs=%s white=%d grey=%d red=%d green=%d phase=%s tints=%s" % [
			p.picker_rows.size(), costs, int(t[0]), int(t[1]), int(t[2]),
			int(m.green), String(m.phase_kind), String(t[3])])
	if int(t[1]) != 0 or int(t[2]) != 0 \\
			or int(t[0]) != p.picker_rows.size():
		_fail("BOOT not neutral-default: " + String(t[3]))
		return
	var g0 := int(m.green)
	var cheap_id := ""
	var cheap_cost := 1 << 30
	for row: Dictionary in p.picker_rows:
		if int(row["cost"]) < cheap_cost:
			cheap_cost = int(row["cost"])
			cheap_id = String(row["id"])

	# DRILL — harness green write below the CHEAPEST cost: every row
	# UNAFFORDABLE -> grey (the overlap reading needs no combat here:
	# affordability paints first in BUILD).
	m.green = cheap_cost - 1
	_pump(p)
	t = _tints(p)
	print("P6-DRILL green=%d white=%d grey=%d red=%d tints=%s" % [
			int(m.green), int(t[0]), int(t[1]), int(t[2]), String(t[3])])
	if int(t[1]) != p.picker_rows.size() or int(t[0]) != 0 \\
			or int(t[2]) != 0:
		_fail("drill below every cost did not grey every row")
		return
	# ENFG — the tint is presentation ONLY: under grey the shipped green
	# refusal still answers, writing nothing.
	var gres: Dictionary = placer.place_id(cheap_id, 1)
	print("P6-ENFG ok=%s why=%s green=%d list=%d" % [
			str(bool(gres.get("ok", false))),
			String(gres.get("why", "NONE")), int(m.green),
			int(m.defense_list.size())])
	if bool(gres.get("ok", false)) \\
			or String(gres.get("why", "NONE")) != "green" \\
			or int(m.green) != cheap_cost - 1 \\
			or int(m.defense_list.size()) != 0:
		_fail("grey rows did not stay enforcement-refused")
		return
	m.green = g0                       # restore twin (cap-leg idiom)
	_pump(p)
	t = _tints(p)
	print("P6-GREENBACK green=%d white=%d grey=%d red=%d" % [
			int(m.green), int(t[0]), int(t[1]), int(t[2])])
	if int(m.green) != g0 or int(t[0]) != p.picker_rows.size() \\
			or int(t[1]) != 0 or int(t[2]) != 0:
		_fail("green restore did not return the rows to neutral")
		return

	# COMBAT — F3 :235 pair write; every row affordable at g0, so the
	# RED half covers the whole picker (no overlap cases to hide in).
	m.phase_kind = "combat"
	m.in_combat = true
	_pump(p)
	t = _tints(p)
	print("P6-COMBAT white=%d grey=%d red=%d tints=%s" % [
			int(t[0]), int(t[1]), int(t[2]), String(t[3])])
	if int(t[2]) != p.picker_rows.size() or int(t[0]) != 0 \\
			or int(t[1]) != 0:
		_fail("combat phase did not RED-tint the buildable rows")
		return
	# ENFP — under red the shipped phase refusal still answers.
	var pres: Dictionary = placer.place_id(cheap_id, 1)
	print("P6-ENFP ok=%s why=%s green=%d list=%d" % [
			str(bool(pres.get("ok", false))),
			String(pres.get("why", "NONE")), int(m.green),
			int(m.defense_list.size())])
	if bool(pres.get("ok", false)) \\
			or String(pres.get("why", "NONE")) != "phase" \\
			or int(m.green) != g0 or int(m.defense_list.size()) != 0:
		_fail("red rows did not stay enforcement-refused")
		return
	m.phase_kind = "build"             # F3 :237 restore twin
	m.in_combat = false
	_pump(p)
	t = _tints(p)
	print("P6-PHASEBACK white=%d grey=%d red=%d" % [
			int(t[0]), int(t[1]), int(t[2])])
	if int(t[0]) != p.picker_rows.size() or int(t[1]) != 0 \\
			or int(t[2]) != 0:
		_fail("phase restore did not return the rows to neutral")
		return

	# TEARDOWN — the matrix left NOTHING: neutral rows, green/phase
	# byte-equal to the BOOT reads, no defense, and the empty-stderr
	# guard covers any write that printed an error.
	var same := 1 if int(m.green) == g0 else 0
	print("P6-TEARDOWN white=%d grey=%d red=%d green_same=%d phase=%s list=%d" % [
			int(t[0]), int(t[1]), int(t[2]), same,
			String(m.phase_kind), int(m.defense_list.size())])
	if int(t[0]) != p.picker_rows.size() or same != 1 \\
			or String(m.phase_kind) != "build":
		_fail("teardown not clean")
		return
	print("P6-OK")
	quit(0)
'''


def _run_probe(tmp_path):
    probe = Path(tmp_path) / "gw_icon_states_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), (),
                                     tmp_path / "user_home")


def _only(out, tag):
    r = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert len(r) == 1, "expected exactly one %s row:\n%s" % (tag, out)
    return dict(x.split("=", 1) for x in r[0].split(" ")[1:])


def _rgb(hex6):
    return tuple(int(hex6[i:i + 2], 16) for i in (0, 2, 4))


def test_icon_states_matrix(tmp_path, class_cache):
    consts = _tint_consts()
    grey, red, neutral = (consts["TINT_GREY"], consts["TINT_RED"],
                          consts["TINT_NEUTRAL"])
    # STRUCTURAL tone legs (independent of the shipped constants): the
    # grey IS darkened + desaturated, the red IS red-dominant, neutral
    # IS the ui_tween rest identity. A plant cannot agree its way out.
    gr, gg, gb = _rgb(grey)
    assert gr == gg == gb and gr < 0xFF, "TINT_GREY not grey: %s" % grey
    rr, rg, rb = _rgb(red)
    assert rr > rg and rr > rb, "TINT_RED not red-dominant: %s" % red
    assert neutral == "ffffff", "neutral tint is not identity: %s" % neutral

    costs = _picker_costs()
    assert costs, "no tower rows parsed"
    min_cost = min(costs)

    proc = _run_probe(tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    out = proc.stdout
    assert "P6-FAIL" not in out, out
    assert out.rstrip().endswith("P6-OK"), \
        "P6-OK must be the LAST row (a skipped leg cannot reach it)"

    # BOOT: neutral default over DATA costs.
    boot = _only(out, "P6-BOOT")
    rows = int(boot["rows"])
    assert rows == len(costs), (boot, costs)
    assert [int(x) for x in boot["costs"].split(",")] == costs, \
        "picker costs are not the towers.json order: %s" % boot
    assert int(boot["green"]) >= max(costs), \
        "neutral-default premise (start green over every cost) broken"
    assert boot["phase"] == "build" and int(boot["white"]) == rows \
        and int(boot["grey"]) == 0 and int(boot["red"]) == 0, boot
    assert boot["tints"] == ",".join([neutral + "ff"] * rows), boot

    # DRILL: grey everywhere, hex-exact python-side.
    drill = _only(out, "P6-DRILL")
    assert int(drill["green"]) == min_cost - 1, drill
    assert int(drill["grey"]) == rows and int(drill["white"]) == 0 \
        and int(drill["red"]) == 0, drill
    assert drill["tints"] == ",".join([grey + "ff"] * rows), drill

    # ENFG: the shipped refusal is still the ONLY enforcement.
    efg = _only(out, "P6-ENFG")
    assert efg["ok"] == "false" and efg["why"] == "green", efg
    assert int(efg["green"]) == min_cost - 1 and int(efg["list"]) == 0, efg

    back = _only(out, "P6-GREENBACK")
    assert int(back["green"]) == int(boot["green"]) \
        and int(back["white"]) == rows and int(back["grey"]) == 0 \
        and int(back["red"]) == 0, back

    # COMBAT: red on every buildable row (all affordable at start
    # green), hex-exact.
    combat = _only(out, "P6-COMBAT")
    assert int(combat["red"]) == rows and int(combat["white"]) == 0 \
        and int(combat["grey"]) == 0, combat
    assert combat["tints"] == ",".join([red + "ff"] * rows), combat

    enfp = _only(out, "P6-ENFP")
    assert enfp["ok"] == "false" and enfp["why"] == "phase", enfp
    assert int(enfp["green"]) == int(boot["green"]) \
        and int(enfp["list"]) == 0, enfp

    phb = _only(out, "P6-PHASEBACK")
    assert int(phb["white"]) == rows and int(phb["grey"]) == 0 \
        and int(phb["red"]) == 0, phb

    # TEARDOWN: nothing behind but the neutral defaults.
    td = _only(out, "P6-TEARDOWN")
    assert int(td["white"]) == rows and int(td["grey"]) == 0 \
        and int(td["red"]) == 0, td
    assert td["phase"] == "build" and int(td["green_same"]) == 1 \
        and int(td["list"]) == 0, td
