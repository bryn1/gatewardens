"""F4 — shop family picker (MC 11616 / V12-PLAN §F4, wave W3).

GAP closed: defense_placer.classes() returns one row per class, first
row wins, so the tower class button always placed the BALLISTA; the
family picker was the placer's own DECLARED later row (defense_placer.gd
header). V12-PLAN §F4 ships it: two build-bar buttons, icons committed +
TEX-pinned at scripts/sprite_bank.gd:47-48 (icon_bombard, icon_hailspire
— grep-VERIFIED this card), placing THAT family's T1 through the EXISTING
placement path — placer.place_id -> mission.place_defense, THE one
application site (cap + can_afford + the single green spend; C12 step (5)
is the sanctioned crossing, mission.gd:321-342). NO second placement
mechanism: place(class) now delegates to place_id on the winner's data
id — the gates have ONE implementation (replace-not-add, guarded below).

Contract legs (plan §F4, engine tier = the conftest.run_probe_script
idiom — ONE harness mechanism, embedded probe written to tmp_path at
runtime, test_defense_boundaries/test_mission_stale precedent):
- VALID: select bombard via the SHIPPED selection entry (the panel
  button's own pressed signal — the same signal chain a browser click
  emits; GUI pickability of EVERY panel button is pinned by
  test_mission_clicks' push_input legs, which collect all buttons) ->
  defense_list row family=bombard via the SAME path ballista uses (the
  FP-CLASS row places ballista through place() and lands on the same
  chain), green delta EXACTLY the towers.json base_cost (160 bombard,
  140 hailspire — re-derived from data, never literals; the brief's
  "items.json price" is a wording slip: items.json carries relics, tower
  prices ride towers.json base_cost, per plan "green -160 / -140").
- INVALID: green short -> the application site refuses {"why":"green"}
  WITHOUT state change (list count + green byte-unchanged); the W17e
  poll-sync enabled flags read OFF (disabled) from the poll, never from
  the pressed handler. Unknown id -> the NEW {"why":"id"} refusal.
- BOUNDARY: alternating bombard/hailspire presses across a refuse + a
  top-up place the RIGHT family EVERY time (FP-COUNT fams order).

PLANTED-RED (wave log transcript): a scratch mutation swaps the id
mapping in row_for_id (row["id"] -> row["class"]) -> the family legs go
RED rc1; git checkout -- restores; green re-run beside the red one.
"""

import json

import conftest

TOWERS = json.load(open(conftest.repo_path("godot", "data", "towers.json"),
                        encoding="utf-8"))
GATEFALL = json.load(open(conftest.repo_path("godot", "data", "maps",
                                             "gatefall.json"),
                          encoding="utf-8"))
BY_ID = {row["id"]: int(row["base_cost"]) for row in TOWERS}
START_GREEN = int(GATEFALL["start_green"])
COST_B = BY_ID["bombard"]            # 160 by data, pinned from HERE only
COST_H = BY_ID["hailspire_tower"]    # 140
COST_BALL = BY_ID["ballista"]        # 100 — the class-winner control

PLACER_GD = conftest.repo_path("godot", "scripts", "defense_placer.gd")
PANEL_GD = conftest.repo_path("godot", "scripts", "defense_panel.gd")

# The family-picker probe (test_defense_boundaries R5 idiom: generated
# into tmp_path — the probe home outside the shipped tree). Machine rows,
# every number re-derived by pytest from the shipped data files:
#   FP-FIND buttons=2 bombard_disabled=<0|1> hail_disabled=<0|1>
#   FP-PLACE n=<1..4> fam=<id> uid=<u> green=<g> count=<c>
#   FP-SYNC phase=off|on2 bombard_disabled=<0|1> hail_disabled=<0|1>
#   FP-REFUSE ok=0 why=green green=<g> count=<c>     (green short)
#   FP-ID ok=0 why=id green=<g> count=<c>            (unknown id)
#   FP-CLASS ok=1 fam=ballista cost=<c> green=<g> count=<c>
#   FP-COUNT n=<c> fams=<comma list>
#   FP-OK
# Every contract refusal is ALSO checked in-probe (FP-FAIL + quit 1), so
# a failure names its leg before the stderr leg even matters.
PROBE_SRC = '''\
# family_picker probe — F4 (MC 11616). Test asset under -s (E5: _ready
# and setup driven directly; E3: failure paths early-return).
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const BAD_ID := "not_a_tower"


func _init() -> void:
\tvar tables = GW_TABLES.new("res://data")
\tvar graph: Dictionary = GW_COMPOSE.build_graph(tables)
\tvar state = graph["state"]
\tstate.set_deck(DECK.duplicate())
\tvar packed = ResourceLoader.load(MISSION_SCENE)
\tif packed == null:
\t\t_fail("mission.tscn not loadable")
\t\treturn
\tvar m = packed.instantiate()
\troot.add_child(m)
\tm._ready()
\tvar rng := RandomNumberGenerator.new()
\trng.seed = 11616
\tm.setup(tables, state, graph["save"], graph["bridge"], "gatefall", "normal", rng)
\tvar panel = m.get_node_or_null("DefensePanel")
\tif panel == null:
\t\t_fail("shipped panel not mounted by mission.setup")
\t\treturn
\tvar bb := panel.get_node_or_null("Rows/Family_bombard") as Button
\tvar hh := panel.get_node_or_null("Rows/Family_hailspire_tower") as Button
\tif bb == null or hh == null:
\t\t_fail("family buttons missing: %s %s" % [str(bb), str(hh)])
\t\treturn
\tvar placer = panel.placer
\tprint("FP-FIND buttons=2 bombard_disabled=%d hail_disabled=%d" % [
\t\t\t1 if bb.disabled else 0, 1 if hh.disabled else 0])
\tif bb.disabled or hh.disabled:
\t\t_fail("affordable family buttons not enabled at start")
\t\treturn
\t# VALID x2 (boundary half 1): press the SHIPPED buttons' own pressed
\t# signal — the same chain a browser click emits (pickability of every
\t# panel button is test_mission_clicks' pinned push_input legs).
\tbb.pressed.emit()
\t_place_row(m, 1, "bombard")
\thh.pressed.emit()
\t_place_row(m, 2, "hailspire_tower")
\t# INVALID: green is now short — the W17e poll-sync gates the buttons
\t# OFF from CURRENT state (never from the pressed handlers)...
\tpanel.poll([])
\tprint("FP-SYNC phase=off bombard_disabled=%d hail_disabled=%d" % [
\t\t\t1 if bb.disabled else 0, 1 if hh.disabled else 0])
\tif not bb.disabled or not hh.disabled:
\t\t_fail("poll did not re-gate family buttons when green ran short")
\t\treturn
\t# ...and the DEEPER invariant: the green-short refusal at the SAME
\t# site the shipped handler calls (a GUI click on a disabled button is
\t# already swallowed — mission_clicks' pinned push_input legs), with
\t# NO state change.
\tvar g0 := int(m.green)
\tvar c0: int = m.defense_list.size()
\tvar rres: Dictionary = placer.place_id("bombard", 1)
\tprint("FP-REFUSE ok=%d why=%s green=%d count=%d" % [
\t\t\t1 if bool(rres.get("ok", false)) else 0,
\t\t\tString(rres.get("why", "")), int(m.green),
\t\t\tm.defense_list.size()])
\tif bool(rres.get("ok", false)) \\
\t\t\tor String(rres.get("why", "")) != "green" \\
\t\t\tor int(m.green) != g0 or m.defense_list.size() != c0:
\t\t_fail("green-short refusal broken: %s g %d->%d list %d->%d" % [
\t\t\t\tstr(rres), g0, int(m.green), c0, m.defense_list.size()])
\t\treturn
\t# Top-up = the shipped green-income lever (mission.green write, the
\t# W17e smoke precedent), sized from the DATA costs through
\t# placer.row_for_id — the very resolution under test.
\tvar top := int(placer.row_for_id("bombard")["base_cost"]) \\
\t\t\t+ int(placer.row_for_id("hailspire_tower")["base_cost"]) \\
\t\t\t+ int(placer.row_for_id("ballista")["base_cost"])
\tm.green += top
\tpanel.poll([])
\tprint("FP-SYNC phase=on2 bombard_disabled=%d hail_disabled=%d" % [
\t\t\t1 if bb.disabled else 0, 1 if hh.disabled else 0])
\tif bb.disabled or hh.disabled:
\t\t_fail("poll did not re-enable the family buttons after income")
\t\treturn
\t# BOUNDARY half 2: alternate again — the RIGHT family EVERY time.
\tbb.pressed.emit()
\t_place_row(m, 3, "bombard")
\thh.pressed.emit()
\t_place_row(m, 4, "hailspire_tower")
\t# Unknown id = the NEW "id" refusal (plan contract), no state change.
\tvar g1 := int(m.green)
\tvar ires: Dictionary = placer.place_id(BAD_ID, 1)
\tprint("FP-ID ok=%d why=%s green=%d count=%d" % [
\t\t\t1 if bool(ires.get("ok", false)) else 0,
\t\t\tString(ires.get("why", "")), int(m.green),
\t\t\tm.defense_list.size()])
\tif bool(ires.get("ok", false)) or String(ires.get("why", "")) != "id" \\
\t\t\tor int(m.green) != g1:
\t\t_fail("unknown-id refusal broken: %s" % str(ires))
\t\treturn
\t# REPLACE-NOT-ADD guard: the class button path is UNCHANGED — place()
\t# still lands the ballista winner on the SAME chain.
\tvar cres: Dictionary = placer.place("tower", 1)
\tif not bool(cres.get("ok", false)):
\t\t_fail("class path place(tower) broke: %s" % str(cres))
\t\treturn
\tvar lob = (m.defense_list[m.defense_list.size() - 1] as Dictionary)["obj"]
\tprint("FP-CLASS ok=1 fam=%s cost=%d green=%d count=%d" % [
\t\t\tString(lob.trow["id"]), int(cres.get("cost", -1)),
\t\t\tint(m.green), m.defense_list.size()])
\tvar fams: Array = []
\tfor rec: Dictionary in m.defense_list:
\t\tfams.append(String((rec["obj"] as RefCounted).trow["id"]))
\tprint("FP-COUNT n=%d fams=%s" % [m.defense_list.size(), ",".join(fams)])
\tprint("FP-OK")
\tquit(0)


func _place_row(m, n: int, want_fam: String) -> void:
\tif m.defense_list.is_empty():
\t\t_fail("place %d: empty defense_list" % n)
\t\treturn
\tvar obj = (m.defense_list[m.defense_list.size() - 1] as Dictionary)["obj"]
\tvar fam := String(obj.trow["id"])
\tprint("FP-PLACE n=%d fam=%s uid=%d green=%d count=%d" % [
\t\t\tn, fam, int(obj.uid), int(m.green), m.defense_list.size()])
\tif fam != want_fam:
\t\t_fail("place %d placed %s, not %s" % [n, fam, want_fam])


func _fail(why: String) -> void:
\tprint("FP-FAIL " + why)
\tquit(1)
'''


def _rows(out, tag):
    hits = [line for line in out.splitlines() if line.startswith(tag + " ")]
    assert len(hits) == 1, "%s row count=%d\n%s" % (tag, len(hits), out)
    return dict(kv.split("=", 1) for kv in hits[0].split(" ")[1:])


def check_rows(out):
    """All machine-row asserts over probe stdout — shared so the
    planted-red mutated run must fail the SAME checks."""
    find = _rows(out, "FP-FIND")
    assert find["buttons"] == "2", find
    assert find["bombard_disabled"] == "0" and find["hail_disabled"] == "0", find

    p1 = _rows(out, "FP-PLACE n=1")
    assert p1["fam"] == "bombard", p1
    assert int(p1["green"]) == START_GREEN - COST_B, \
        "bombard charged EXACTLY towers.json base_cost: %s" % p1
    assert int(p1["uid"]) > 0 and int(p1["count"]) == 1, p1

    p2 = _rows(out, "FP-PLACE n=2")
    assert p2["fam"] == "hailspire_tower", \
        "family switch placed the wrong family: %s" % p2
    assert int(p2["green"]) == START_GREEN - COST_B - COST_H, p2

    off = _rows(out, "FP-SYNC phase=off")
    assert off["bombard_disabled"] == "1" and off["hail_disabled"] == "1", off

    ref = _rows(out, "FP-REFUSE")
    assert ref["ok"] == "0" and ref["why"] == "green", \
        "the why=green refusal string is the plan contract: %s" % ref
    assert int(ref["green"]) == int(p2["green"]) and \
        int(ref["count"]) == 2, "green-short refused WITHOUT state change: %s" % ref

    on2 = _rows(out, "FP-SYNC phase=on2")
    assert on2["bombard_disabled"] == "0" and on2["hail_disabled"] == "0", on2

    p3 = _rows(out, "FP-PLACE n=3")
    assert p3["fam"] == "bombard" and int(p3["count"]) == 3, p3
    assert int(p3["green"]) == int(ref["green"]) + COST_H + COST_BALL, p3
    p4 = _rows(out, "FP-PLACE n=4")
    assert p4["fam"] == "hailspire_tower" and int(p4["count"]) == 4, p4
    assert int(p4["green"]) == int(p3["green"]) - COST_H, p4

    ident = _rows(out, "FP-ID")
    assert ident["ok"] == "0" and ident["why"] == "id", \
        "unknown id must refuse with the NEW 'id' string: %s" % ident
    assert int(ident["green"]) == int(p4["green"]) and \
        int(ident["count"]) == 4, ident

    cls = _rows(out, "FP-CLASS")
    assert cls["fam"] == "ballista" and int(cls["cost"]) == COST_BALL, \
        "place(class) still places the ballista winner: %s" % cls
    assert int(cls["green"]) == int(p4["green"]) - COST_BALL, cls

    cnt = _rows(out, "FP-COUNT")
    assert cnt["n"] == "5", cnt
    assert cnt["fams"] == "bombard,hailspire_tower,bombard," \
        "hailspire_tower,ballista", \
        "boundary: right family EVERY time, in order: %s" % cnt

    assert "FP-OK" in out.splitlines(), out


def test_family_picker_engine_leg(tmp_path, class_cache):
    probe = tmp_path / "family_picker_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    proc = conftest.run_probe_script(str(probe), (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    assert "FP-FAIL" not in proc.stdout, proc.stdout
    check_rows(proc.stdout)


def _body(text, header):
    start = text.index(header)
    rest = text[start + len(header):]
    end = rest.find("\nfunc ")
    return rest if end < 0 else rest[:end]


def test_one_gate_implementation_source_truth():
    """REPLACE-NOT-ADD (plan §F4): place(class) DELEGATES to place_id on
    the winner's data id — the placer calls the application site exactly
    ONCE, and row_for_id (the picker's resolution) resolves by the row's
    data "id", not by class (the planted-red target)."""
    with open(PLACER_GD, encoding="utf-8") as fh:
        text = fh.read()
    assert text.count("m.place_defense(") == 1, \
        "the placer must call the ONE application site from exactly one place"
    place_body = _body(text, "func place(class_id: String, ")
    assert "place_id(String(row[\"id\"]), tier, slot)" in place_body, \
        "place(class) must delegate to place_id on the winner's id"
    rid_body = _body(text, "func row_for_id(tower_id: String) -> Dictionary:")
    assert 'String(row["id"]) == tower_id' in rid_body, \
        "row_for_id must resolve the towers.json data id"
    panel = open(PANEL_GD, encoding="utf-8").read()
    sync_body = _body(panel, "func sync() -> void:")
    assert "picker_rows" in sync_body, \
        "family buttons' disabled state must ride the W17e poll sync"
    fam_body = _body(panel, "func _on_family_pressed(tower_id: String)")
    assert "placer.place_id(tower_id, 1)" in fam_body \
        and ".disabled" not in fam_body, \
        "the handler places through place_id and never touches enabled flags"
