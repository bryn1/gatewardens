"""v1.2 F1 return-to-hub gate (MC 11623 / wave W2, V12-PLAN §F1).

OWNER RULING 2026-10-28 verbatim: "rec on all 3" — END-ONLY: NO mid-
mission exit control ships; return-to-hub is available from the mission
END (victory AND defeat) screens only. The ruling is TESTED, not
assumed: the MID leg fails if ANY control in the routed mission tree
routes to main's return path, while outcome == null.

ENGINE TIER (conftest.run_probe_script — the ONE harness mechanism; the
probe source lives HERE, test_mission_clicks.py idiom; W4 stderr-strict:
rc0 + EMPTY stderr). The probe boots the SHIPPED router (res://Main.tscn
+ main._ready driven, E5 idiom) and crosses the router through the
SHIPPED entry points only (main.start_mission; the button's own pressed
chain via root.push_input picking, test_mission_clicks.py:404 idiom):
  MID   outcome==null: zero return-path controls in the tree (runtime
        scan of every Button's pressed connections — the negative leg
        pinning the owner ruling) AND a direct call of the shipped
        click path REFUSES (router state byte-unchanged, mission kept).
  WIN   win_pending -> the natural mission step sets outcome + commits
        (C13 once); the RETURN TO HUB button then EXISTS bottom-center
        UNDER the mission subtree; its click (real picking) defers
        open_hub (F-2 answer, no second router); next frames: _routed
        is the Hub, main.mission null, state PRESERVED — read back
        through the SHIPPED C5 mirror (__GW_LAST_SNAPSHOT saved_ack +
        bank_count byte-equal; same state object; saved_ack unchanged
        = NO second C13 write) — and no return control SURVIVES into
        the hub (teardown boundary).
  LOSE  the same legs on the defeat screen (core destroyed).
PLANTED-RED (the DoD's planted mutation, arg "no_return_ctl"): the end
control is freed before the end-screen leg reads it (the control-removed
shape) — the WIN leg MUST go RED rc1.
"""

import json
import re
import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for code greps)

MAIN_GD = Path(conftest.repo_path("godot", "scripts", "main.gd"))


# ---------- engine tier: shipped router, real picking, real frames ------

PROBE_SRC = '''
extends SceneTree
# gw return-to-hub probe (F1, MC 11623). Machine rows: GWRETURN-MID /
# -WIN / -LOSE / -OK; any failed check prints GWRETURN-FAIL <detail>
# + rc1. PLANTED-RED arg: "no_return_ctl" (frees the end control before
# the end-screen leg — the removal shape; the WIN leg must go RED).
const DECK := ["warden", "deadeye", "embercaller"]

var main = null
var mon = null

func _init() -> void:
	var packed = ResourceLoader.load("res://Main.tscn")
	if packed == null:
		print("GWRETURN-FAIL Main.tscn not loadable")
		quit(1)
		return
	main = packed.instantiate()
	root.add_child(main)
	main._ready()                          # E5: -s never dispatches _ready
	main.state.set_deck(DECK.duplicate())  # shipped C13 mutator, live save
	var args: Array = OS.get_cmdline_user_args()
	mon = Monitor.new()
	mon.p = self
	mon.planted = "no_return_ctl" if args.has("no_return_ctl") else ""
	root.add_child(mon)


class Monitor:
	extends Node
	var p            # the SceneTree probe (main lives on p)
	var planted := ""
	var frames := 0
	var mission1 = null
	var ack_before := 0
	var bank_before := 0
	var state_ref = null

	func _fail(why: String) -> void:
		print("GWRETURN-FAIL " + why)
		p.quit(1)

	func _click(at: Vector2) -> void:
		# The Viewport's OWN GUI picking (test_mission_clicks idiom — the
		# pipeline browser input enters on web); the Button that receives
		# this complete press emits `pressed`.
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

	# Every Button under a root, any depth.
	func _buttons(n: Node, out: Array) -> void:
		if n is Button:
			out.append(n)
		for c: Node in n.get_children():
			_buttons(c, out)

	# The negative instrument: count controls whose pressed connections
	# route into main's return path (method name or the end-layer name).
	func _return_ctls() -> int:
		var btns: Array = []
		_buttons(p.main, btns)
		var hits := 0
		for b: Variant in btns:
			for c: Dictionary in (b as Button).pressed.get_connections():
				var fn: Callable = c["callable"]
				if fn.get_object() == p.main \\
						and fn.get_method() == "_return_to_hub":
					hits += 1
		return hits

	func _snap(key: String) -> Variant:
		# SHIPPED read-back: the C5 mirror main pushes every frame.
		var j = JSON.parse_string(p.main.__GW_LAST_SNAPSHOT)
		return j[key] if j != null else null

	func _end_ctl(m):
		return null if m == null \\
				else m.get_node_or_null("EndReturn/ReturnToHub")

	# The end-screen leg, shared by WIN and LOSE: control present under
	# the mission subtree, click -> routed hub, state preserved, control
	# gone in the hub. tag distinguishes the printed rows.
	func _leg_end(tag: String, outcome_want: String) -> void:
		var m = p.main.mission
		if m == null:
			_fail(tag + " end: mission is null before the end leg")
			return
		if String(m.outcome) != outcome_want or not m.committed:
			_fail("%s end not reached outcome=%s committed=%s" \\
					% [tag, String(m.outcome), str(m.committed)])
			return
		if _end_ctl(m) == null:
			_fail("%s end screen exposes NO return control" % tag)
			return
		if _return_ctls() != 1:
			_fail("%s return-path controls=%d (want the ONE button)" \\
					% [tag, _return_ctls()])
			return
		ack_before = p.main.state.saved_ack
		bank_before = p.main.state.bank.size()
		if int(_snap("saved_ack")) != ack_before \\
				or int(_snap("bank_count")) != bank_before:
			_fail("%s shipped mirror disagrees state (ack/bank)" % tag)
			return
		_click((_end_ctl(m) as Control).get_global_rect().get_center())
		print("GWRETURN-%s ctl=1 ack=%d bank=%d clicked=1" % [tag.to_upper(),
				ack_before, bank_before])

	# Read leg after the deferred route flushed at end of frame.
	func _leg_routed(tag: String) -> void:
		if p.main.mission != null:
			_fail("%s mission kept after RETURN click" % tag)
			return
		if p.main._routed == null or String(p.main._routed.name) != "Hub":
			_fail("%s routed=%s (want Hub)" % [tag,
					String(p.main._routed.name) if p.main._routed != null
					else "null"])
			return
		if p.main.state != state_ref:
			_fail("%s state object swapped (second composition)" % tag)
			return
		if p.main.state.saved_ack != ack_before \\
				or p.main.state.bank.size() != bank_before \\
				or int(_snap("saved_ack")) != ack_before \\
				or int(_snap("bank_count")) != bank_before:
			_fail("%s state NOT preserved ack=%d/%d bank=%d/%d (a second " \\
					% [tag, p.main.state.saved_ack, ack_before,
					p.main.state.bank.size(), bank_before] \\
					+ "C13 write? mirror desync?)" + "")
			return
		var btns: Array = []
		_buttons(p.main, btns)
		for b: Variant in btns:
			for c: Dictionary in (b as Button).pressed.get_connections():
				var fn: Callable = c["callable"]
				if fn.get_object() == p.main:
					_fail("%s stale return control survived into the hub" \\
							% tag)
					return
		print("GWRETURN-%s routed=Hub preserved ack=%d bank=%d" \\
				% [tag.to_upper(), ack_before, bank_before])

	func _process(_d: float) -> void:
		frames += 1
		if frames == 2:
			get_tree().root.size = Vector2i(1280, 720)   # E8 served size
		if frames == 3:
			p.main.start_mission("gatefall", "normal")   # shipped router
			mission1 = p.main.mission
			state_ref = p.main.state
			if mission1 == null:
				_fail("start_mission routed nothing")
		if frames == 4:
			_leg_mid()
		if frames == 5:
			_leg_refused()
		if frames == 6:
			mission1.win_pending = true                  # plan's win lever
		if frames == 9:
			if planted == "no_return_ctl":
				_end_ctl(mission1).free()   # PLANT: control removed
				print("GWRETURN-PLANT freed=1")
			_leg_end("win", "win")
		if frames == 11:
			_leg_routed("win")
		if frames == 12:
			p.main.start_mission("gatefall", "normal")
			if p.main.mission == null or p.main.mission == mission1:
				_fail("second mission did not route")
			p.main.mission.core_main.destroyed = true    # plan's lose lever
			state_ref = p.main.state
		if frames == 15:
			_leg_end("lose", "lose")
		if frames == 17:
			_leg_routed("lose")
			print("GWRETURN-OK")
			p.quit(0)

	# MID — the OWNER RULING leg: while outcome == null the in-mission
	# UI exposes NO exit-to-hub control anywhere in the routed tree.
	func _leg_mid() -> void:
		if p.main.mission == null or p.main.mission.outcome != null:
			_fail("MID: not mid-mission (mission/outcome wrong)")
			return
		var btns: Array = []
		_buttons(p.main, btns)
		var end = _end_ctl(p.main.mission)
		if end != null or _return_ctls() != 0:
			_fail("MID: in-mission exit-to-hub control EXISTS " \\
					+ "(owner ruling END-ONLY violated)")
			return
		print("GWRETURN-MID buttons=%d return_ctls=0 ctl=0" % btns.size())

	# Invalid leg: the shipped click path itself refuses mid-mission —
	# direct call, then the next frame asserts router state unchanged.
	func _leg_refused() -> void:
		p.main._return_to_hub()
		if p.main.mission != mission1 or p.main._routed != mission1:
			_fail("refused click changed the router")
			return
		print("GWRETURN-MID refused=1 mission_kept=1")
'''


def _run_probe(extra_args, tmp_path):
    probe = Path(tmp_path) / "gw_return_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), extra_args,
                                     tmp_path / "user_home")


def _rows(out, tag):
    return [ln for ln in out.splitlines() if ln.startswith(tag)]


# ---------- the contract legs (engine tier, one harness) ----------------

def test_return_hub_engine_legs(tmp_path, class_cache):
    proc = _run_probe([], tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    out = proc.stdout
    assert "GWRETURN-FAIL" not in out, out
    assert "GWRETURN-PLANT" not in out, out
    assert out.rstrip().endswith("GWRETURN-OK"), out

    # MID: negative leg — no in-mission exit control, and the shipped
    # click path refuses (the owner ruling pinned at runtime).
    mid = _rows(out, "GWRETURN-MID")
    assert len(mid) == 2, out
    m = re.search(r"buttons=(\d+) return_ctls=(\d+) ctl=(\d+)", mid[0])
    assert m and int(m.group(1)) > 0 and m.group(2) == "0" \
        and m.group(3) == "0", mid[0]
    assert "refused=1 mission_kept=1" in mid[1], mid[1]

    # WIN end screen: control -> click -> hub, state preserved off the
    # SHIPPED C5 mirror (ack + bank byte-equal before and after).
    win = _rows(out, "GWRETURN-WIN")
    assert len(win) == 2, out
    a = re.search(r"ctl=1 ack=(\d+) bank=(\d+) clicked=1", win[0])
    r = re.search(r"routed=Hub preserved ack=(\d+) bank=(\d+)", win[1])
    assert a and r and a.group(1) == r.group(1) and a.group(2) == r.group(2), win
    # Acknowledged end commit rides BEFORE the click: saved_ack moved
    # past a boot save (mission-end C13 commit happened once).
    assert int(a.group(1)) >= 2, win[0]

    # LOSE end screen: the same legs from the defeat banner.
    lose = _rows(out, "GWRETURN-LOSE")
    assert len(lose) == 2, out
    assert "ctl=1" in lose[0] and "routed=Hub preserved" in lose[1], lose


def test_planted_red_no_return_control_goes_red(tmp_path, class_cache):
    # PLANTED mutation per the DoD: the end control removed -> the
    # end-screen leg must go RED (a gate that never failed is no gate).
    proc = _run_probe(["no_return_ctl"], tmp_path)
    assert proc.returncode == 1, \
        "planted removal must RED the probe, rc=%d\nOUT:%s" % (
            proc.returncode, proc.stdout)
    assert "GWRETURN-PLANT freed=1" in proc.stdout, proc.stdout
    assert "GWRETURN-FAIL win end screen exposes NO return control" \
        in proc.stdout, proc.stdout
    assert "GWRETURN-OK" not in proc.stdout, proc.stdout


# ---------- source truth: the ruling is structural, not a coincidence ---

def test_end_only_guards_in_main_gd():
    code = hyg.blank_code(MAIN_GD.read_text(encoding="utf-8"), "gd")
    # Both the builder and the click path gate on the shipped outcome
    # field; the route defers through the ONE open_hub entry (F-2 form);
    # the layer mounts UNDER the mission, never beside _routed.
    assert re.search(r"if mission == null or mission\.outcome == null:\s*\n"
                     r"\s*return", code), "builder outcome-guard missing"
    assert code.count("mission.outcome == null") >= 2, \
        "the click path lost its outcome guard (mid-mission ships an exit)"
    assert "open_hub.call_deferred()" in code, \
        "route not deferred (F-2: free inside pressed emit = engine error)"
    assert "open_hub()" not in re.sub(r"open_hub\.call_deferred\(\)", "",
                                       code.split("func _return_to_hub")[1]), \
        "a synchronous open_hub beside the deferred route (second router)"
    assert "mission.add_child(layer)" in code \
        and "add_child(layer)" in code, "end layer not mounted under mission"
    assert re.search(r"push_snapshot\(\)\s*\n\s*_f1_end_screen\(\)", code), \
        "the frame pump lost its END-ONLY builder call"
    # The hub-side belt: a stale control cannot survive into the hub.
    hub_body = code.split("func open_hub")[1].split("func start_mission")[0]
    assert "_return_ctl.visible = false" in hub_body, "hub belt removed"
