"""W17e stale-panel-state gate (MC 11274.1.32 / card 11397).

Served-build repros: the panel's button enabled/disabled state only ever
synced inside refresh(), and refresh() ran ONLY on action-driven events
(mission.gd:249 relays presses through poll(); between presses NOTHING
re-gates). Two swallows followed:
  REPRO-B: green regained (kills/wave awards) while the class buttons
    stayed disabled at the last refresh's verdict -> the browser silently
    swallows clicks on disabled buttons -> place dead despite green >= cost.
  REPRO-A: Sell click while sell_btn was still disabled at the last
    refresh (the row-select refresh had not re-gated it yet, or the row
    click was lost in refresh()'s row REBUILD churn — a rebuilt row Button
    is an unsized new control until the frame-end container sort).
FIX: poll(presses) syncs the enabled flags + row selected-marks from the
CURRENT sim state every poll (cheap), while the expensive clear+rebuild
of the defense rows runs only when the list actually changed (dirty check
on count/uids; E9 detach+queue_free kept for the churn that remains).

ENGINE TIER (EMPTY stderr idiom, test_mission_clicks.py boot): real
mission under -s, push_input clicks (the browser-input pipeline).
LEG REGAIN (models REPRO-B): place until the class button is disabled;
regain green via the existing mission_smoke start_green lever (a
mission.green write, NOT an action); next poll click place with NO other
action -> MUST place + spend.
LEG SELLS (models REPRO-A): with 3 rows, one browser-style attempt = click
Row_1, then click Row_2 at its coords measured BEFORE the first click
(pre-fix the select's rebuild churns Row_2 into an unsized control ->
the second click is lost); on the IMMEDIATELY next poll, ONE Sell click
on the damaged row -> refund lands in green AND defenses -1.
PLANTED-RED: "stale_buttons" (re-freeze the class button every frame
after the mission's poll — the sync-removed shape) and "rows_churn"
(rebuild the rows right after a select — the rebuild-every-refresh shape);
the SAME legs MUST go RED. Both legs are RED against the pre-fix panel
BY CONSTRUCTION (the pre-fix transcripts live in W17e-evidence.md).
"""

import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (blank_code for the source gate)

GODOT = Path(conftest.repo_path("godot"))
PANEL_GD = GODOT / "scripts" / "defense_panel.gd"

PROBE_SRC = '''
extends SceneTree
# gw stale-panel probe (W17e). Machine rows: GWSYNC-ARM / -REGAIN /
# -SEL / -SELL2 / GWMICE-OK; any failed check prints GWMICE-FAIL + rc1.
# PLANTED-RED args: "stale_buttons" (class button re-frozen after every
# mission poll: the poll-sync-removed shape) and "rows_churn" (rows
# rebuilt right after a select: the rebuild-every-refresh shape).
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const REGAIN := 150          # > tower base_cost 100 (data read in python)


class Monitor:
	extends Node
	var m
	var planted := ""
	var frames := 0

	func _fail(why: String) -> void:
		print("GWMICE-FAIL " + why)
		get_tree().quit(1)

	func _p():
		return m.get_node("DefensePanel")

	func _click(at: Vector2) -> void:
		# The Viewport's OWN GUI picking (the browser-input pipeline).
		var vp := get_tree().root
		var mm := InputEventMouseMotion.new()
		mm.position = at
		mm.global_position = at
		vp.push_input(mm, true)
		var dn := InputEventMouseButton.new()
		dn.button_index = MOUSE_BUTTON_LEFT
		dn.position = at
		dn.global_position = at
		dn.pressed = true
		dn.button_mask = MOUSE_BUTTON_MASK_LEFT
		vp.push_input(dn, true)
		var up := dn.duplicate() as InputEventMouseButton
		up.pressed = false
		up.button_mask = 0
		vp.push_input(up, true)

	func _class_btn():
		return _p().class_buttons["tower"] as Button

	func _row(uid: int):
		return m.get_node("DefensePanel/Rows/Rows_defenses/Row_%d" % uid) \
				as Control

	func _process(_d: float) -> void:
		frames += 1
		if frames == 2:
			get_tree().root.size = Vector2i(1280, 720)   # served size
		# PLANT stale_buttons: re-freeze AFTER the mission poll synced
		# (mission._process runs first: tree order) -> sync-removed shape.
		if planted == "stale_buttons" and frames >= 6:
			_class_btn().disabled = true
		if frames == 4:
			_click(_class_btn().get_global_rect().get_center())   # 300->200
		if frames == 5:
			_click(_class_btn().get_global_rect().get_center())   # 200->100
		if frames == 6:
			_click(_class_btn().get_global_rect().get_center())   # 100->0
			if not _class_btn().disabled:
				_fail("class button not disabled after spend-to-zero")
				return
			# damage uid2 (mission_smoke_w8 take_damage half idiom) so a
			# sell of THAT row must refund > 0.
			m.defense_list[1]["obj"].take_damage(
					m.defense_list[1]["obj"].hp_max * 0.5)
			# green regains via the existing start_green lever — a sim
			# state write, NOT a panel action (models kill/wave income).
			m.green = REGAIN
			print("GWSYNC-ARM green=%d class_disabled=%s list=%d" % [
					int(m.green), str(_class_btn().disabled),
					int(m.defense_list.size())])
		if frames == 7:
			# LEG REGAIN: no action since the green write — click place.
			_click(_class_btn().get_global_rect().get_center())
			var placed: int = m.defense_list.size()
			var spent: int = int(m.green)
			print("GWSYNC-REGAIN placed=%d green=%d class_disabled=%s" \
					% [placed, spent, str(_class_btn().disabled)])
			if placed != 4 or spent != REGAIN - 100:
				_fail("place starved while affordable (placed=%d " \
						% placed + "green=%d)" % spent)
				return
		if frames == 8:
			# LEG SELLS: browser-style one attempt. Measure Row_2 FIRST
			# (the coords a served-clicker has — rows sorted: the f7 place
			# rebuilt them LAST frame), click Row_1, then click Row_2 at
			# those measured coords in the SAME frame.
			var r2 := _row(2).get_global_rect()
			_click(_row(1).get_global_rect().get_center())
			if planted == "rows_churn":
				# PLANT rows_churn: rebuild right after the select (the
				# rebuild-every-refresh shape the dirty check removes).
				_p()._rebuild_defense_rows()
			_click(r2.get_center())
			var sel := int(_p().selected_uid)
			print("GWSYNC-SEL want=2 selected=%d" % sel)
			if sel != 2:
				_fail("browser-style row click lost (selected=%d)" % sel)
				return
		if frames == 9:
			# IMMEDIATELY next poll: ONE Sell attempt.
			var g0 := int(m.green)
			var n0: int = m.defense_list.size()
			_click((_p().sell_btn as Control).get_global_rect().get_center())
			var refund := int(m.green) - g0
			var n1: int = m.defense_list.size()
			var left := ""
			for rec: Dictionary in m.defense_list:
				left += "%d," % int(rec["uid"])
			print("GWSYNC-SELL2 refund=%d n=%d->%d left=%s selected=%d" \
					% [refund, n0, n1, left, int(_p().selected_uid)])
			if refund <= 0 or n1 != n0 - 1 or left != "1,3,4," \
					or int(_p().selected_uid) != 0:
				_fail("one Sell attempt did not refund+remove " \
						+ "(refund=%d n=%d left=%s)" % [refund, n1, left])
				return
			print("GWMICE-OK")
			get_tree().quit(0)


func _init() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	var state = graph["state"]
	state.set_deck(DECK.duplicate())     # starter deck via the C13 write
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		print("GWMICE-FAIL mission.tscn not loadable")
		quit(1)
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                           # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274                     # pinned seed, smoke idiom
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	var mon := Monitor.new()
	mon.m = m
	var args: Array = OS.get_cmdline_user_args()
	mon.planted = "stale_buttons" if args.has("stale_buttons") else (
			"rows_churn" if args.has("rows_churn") else "")
	root.add_child(mon)
'''


def _run_probe(extra_args, tmp_path):
    probe = Path(tmp_path) / "gw_stale_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), extra_args,
                                     tmp_path / "user_home")


def _only(out, tag):
    rows = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert len(rows) == 1, out
    return rows[0]


def _kv(line):
    return dict(x.split("=", 1) for x in line.split(" ")[1:])


def _tower_cost():
    import json
    towers = json.loads((GODOT / "data/towers.json").read_text(
        encoding="utf-8"))
    rows = towers["towers"] if isinstance(towers, dict) else towers
    return int(rows[0]["base_cost"])


def test_stale_poll_sync_leg(tmp_path, class_cache):
    proc = _run_probe([], tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "GWMICE-FAIL" not in out, out
    assert out.rstrip().endswith("GWMICE-OK"), out

    arm = _kv(_only(out, "GWSYNC-ARM"))
    assert _tower_cost() == 100, arm          # data truth the leg assumes
    # ARM: green regained by a bare sim write leaves the button disabled
    # AT THE WRITE (synced on the mission's NEXT poll — the fix's frame):
    assert int(arm["green"]) == 150 and arm["class_disabled"] == "true", arm
    regain = _kv(_only(out, "GWSYNC-REGAIN"))
    # LEG REGAIN: the next-poll click placed + spent EXACTLY cost, no
    # other action in between (REPRO-B shape).
    assert int(regain["placed"]) == 4 and int(regain["green"]) == 50, regain
    sel = _kv(_only(out, "GWSYNC-SEL"))
    # LEG SELLS attempt 1: the browser-style click chain selected Row_2.
    assert int(sel["selected"]) == 2, sel
    s2 = _kv(_only(out, "GWSYNC-SELL2"))
    # ONE Sell click on the immediately-next poll: refund landed AND the
    # damaged row (uid 2) is gone (1,3,4 left) + selection cleared.
    assert int(s2["refund"]) > 0, s2
    assert s2["n"] == "4->3" and s2["left"] == "1,3,4," \
        and int(s2["selected"]) == 0, s2


def test_stale_planted_red_stale_buttons_goes_red(tmp_path, class_cache):
    # The W17e regression shape (poll-path enabled-sync removed — the
    # REPRO-B swallow reintroduced): the REGAIN leg MUST go RED.
    proc = _run_probe(["stale_buttons"], tmp_path)
    assert proc.returncode == 1, \
        "planted-red: frozen buttons slipped the sync gate\n%s" \
        % proc.stdout
    assert "GWMICE-FAIL" in proc.stdout and "GWMICE-OK" not in \
        proc.stdout, proc.stdout
    assert "starved while affordable" in proc.stdout, proc.stdout


def test_stale_planted_red_rows_churn_goes_red(tmp_path, class_cache):
    # The W17e regression shape (rows rebuilt on every refresh — the
    # REPRO-A churn losing a player click): the SELLS leg MUST go RED.
    proc = _run_probe(["rows_churn"], tmp_path)
    assert proc.returncode == 1, \
        "planted-red: row churn slipped the dirty-check gate\n%s" \
        % proc.stdout
    assert "GWMICE-FAIL" in proc.stdout and "GWMICE-OK" not in \
        proc.stdout, proc.stdout
    assert "browser-style row click lost" in proc.stdout, proc.stdout


# ---------- source truth: poll() runs the sync (W17b gate idiom) --------

def _sync_violations(code):
    """poll() must call sync() BEFORE draining presses (state re-gated
    from the CURRENT sim, then actions), and refresh() must rebuild the
    rows only behind the dirty check. Dropped call = REPRO-B reintroduced;
    unguarded rebuild = REPRO-A churn reintroduced."""
    bad = []
    if "func sync" not in code:
        bad.append("no sync() — the poll-path state sync is gone")
    poll_body = code.split("func poll(presses: Array) -> void:")
    body = poll_body[1].split("func ")[0] if len(poll_body) > 1 else ""
    if "sync()" not in body:
        bad.append("poll() never calls sync() (W17e stale buttons)")
    refresh_body = code.split("func refresh() -> void:")
    rb = refresh_body[1].split("func ")[0] if len(refresh_body) > 1 else ""
    if "_rows_dirty()" not in rb or "_rebuild_defense_rows()" not in rb:
        bad.append("refresh() rebuild is not dirty-guarded (W17e churn)")
    return bad


def test_panel_poll_declares_the_sync():
    bad = _sync_violations(hyg.blank_code(
        PANEL_GD.read_text(encoding="utf-8"), "gd"))
    assert not bad, "defense_panel.gd lost the W17e poll sync: %r" % bad


def test_panel_poll_planted_red_dropped_sync_goes_red():
    code = hyg.blank_code(PANEL_GD.read_text(encoding="utf-8"), "gd")
    head, tail = code.split("func poll(presses: Array) -> void:", 1)
    planted = head + "func poll(presses: Array) -> void:" \
        + tail.replace("sync()", "pass", 1)
    bad = _sync_violations(planted)
    assert bad, "planted-red: dropped poll sync slipped the source gate"
