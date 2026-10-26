"""W17b mission-clicks gate (MC 11274.1.29 / card 11386).

Journey-found P1: the served build's panel was UNCLICKABLE (grid probe x
0-160 x y 74-134, dozens of synthetic MouseEvents, green/defenses never
moved, mission lost at t=36) while the smoke harness drove it fine — the
KeyM bridge never touches the mouse, so click reachability was never
tested. Mechanism (VERIFIED headless this card, evidence W17b):
the overlay is a CanvasLayer ABOVE the panel, and its CODE-BUILT display
controls keep the engine defaults — hero-slot VBoxContainers PASS, their
ProgressBars STOP (a Control on the top layer that answers a click
swallows everything beneath it). The hud.tscn containers were already
IGNORE since W10, which is why the $Root-default-STOP suspect needed
engine verification before fixing.

Gates (test_hub_layout.py idiom — probe SOURCE LIVES HERE, a clean
checkout runs identically):

- ENGINE TIER: boot the REAL mission scene under -s, force the served
  logical size (VERIFIED: root.size = Vector2i(1280,720) takes effect
  under -s; the dummy display starts the window at 64x64), then read the
  REAL tree back:
    (a) FILTER — every Control under HUD reports mouse_filter IGNORE and
        the read-only HUD owns ZERO Buttons (the pinned row proves no
        interactive HUD control exists, so IGNORE cannot swallow one);
    (b) GEOMETRY — every panel Button rect lies fully on-screen and is
        disjoint from every HUD Control rect at 1280x720;
    (c) PICK — at each panel Button center the Control that RECEIVES the
        input IS that Button. Picking mechanism (declared): the engine's
        OWN Viewport GUI picking — root.push_input(motion, press,
        release) is the same pipeline a browser mouse event enters on
        the web build (Window::push_input -> Viewport hit-test by
        global rect + mouse_filter, top CanvasLayer first); a Button
        that receives a complete press emits `pressed`. Enabled buttons
        assert exactly-one-receiver (themselves); disabled buttons
        assert the click lands NOWHERE (disabled controls do not answer);
        the first enabled Class_* clicks must PLANT defenses (state
        change one bookkeeping frame later — the served-bug signature
        is zero). EMPTY stderr (W4 ruling).
- PLANTED-RED (engine tier): arg "stop_root" puts HUD/Root back to STOP
  after setup — the legs MUST go RED (an unbroken gate is no gate).
- SOURCE TRUTH (stdlib): hud.gd setup() ends with the one
  _ignore_mouse pass; mission.gd's mount positions the panel (right
  column, x past every HUD rect); every tscn ext_resource uid attribute
  equals its .uid sidecar (the export-sidecar truth the served console
  errored on: mission.tscn's stale uids uid://dki88udyr8g1w /
  uid://n3w0umenqbws were embedded in the exported mission.scn — the
  byte-proof lives in the evidence file, the string-truth lives here).
"""

import re
import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for code greps)

GODOT = Path(conftest.repo_path("godot"))
SCRIPTS = GODOT / "scripts"
SCENES = GODOT / "scenes"
HUD_GD = SCRIPTS / "hud.gd"
MISSION_GD = SCRIPTS / "mission.gd"
MISSION_TSCN = SCENES / "mission.tscn"
VIEW = (1280.0, 720.0)              # project viewport, the served size
# The served-console stale pair (fixed by the uid resync; banned strings):
STALE_UIDS = ("uid://dki88udyr8g1w", "uid://n3w0umenqbws")


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def _rect_disjoint(a, b):
    """Strict-interior disjointness (edge-touching rects are legal)."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax < bx + bw and bx < ax + aw and ay < by + bh
                and by < ay + ah)


# ---------- engine tier: real mission, real picking, real frames --------

PROBE_SRC = '''
extends SceneTree
# gw mission-clicks probe (W17b). Machine rows: GWMICE-FILTER / -GEOM /
# -PICK / -OK; any failed check prints GWMICE-FAIL <detail> + rc1.
# Arg "stop_root": PLANTED-RED — HUD/Root back to STOP after setup (the
# W17b regression shape); the SAME legs must go RED.
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]


class Monitor:
	extends Node
	var m
	var planted := ""
	var frames := 0
	var fired := {}
	var clicked := 0
	var class_clicks := 0

	func _ping(k: String) -> void:
		fired[k] = int(fired.get(k, 0)) + 1

	func _fail(why: String) -> void:
		print("GWMICE-FAIL " + why)
		get_tree().quit(1)

	func _controls(n: Node, out: Array) -> void:
		if n is Control:
			out.append(n)
		for c: Node in n.get_children():
			_controls(c, out)

	func _click(at: Vector2) -> void:
		# The Viewport's OWN GUI picking — the same pipeline a browser
		# mouse event enters on the web build; which Button emits
		# `pressed` IS the receiver answer (the docstring's mechanism).
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

	func _process(_d: float) -> void:
		frames += 1
		if frames == 2:
			get_tree().root.size = Vector2i(1280, 720)   # served size
		if frames == 4 and planted == "stop_root":
			(m.get_node("HUD/Root") as Control).mouse_filter = \
					Control.MOUSE_FILTER_STOP
		if frames == 6:
			_legs_filter()
			_legs_geom()
			_legs_pick()
		if frames == 7:
			_check_placed()

	# (a) FILTER ----------------------------------------------------------
	func _legs_filter() -> void:
		var ctrls: Array = []
		_controls(m.get_node("HUD"), ctrls)
		var ignored := 0
		var btns := 0
		for c: Variant in ctrls:
			var ctl := c as Control
			if ctl.mouse_filter == Control.MOUSE_FILTER_IGNORE:
				ignored += 1
			else:
				_fail("filter %s mf=%d (display overlay must IGNORE)" \
						% [String(ctl.get_path()), ctl.mouse_filter])
				return
			if ctl is Button:
				btns += 1
		if ctrls.is_empty():
			_fail("no HUD controls found")
			return
		print("GWMICE-FILTER controls=%d ignore=%d buttons=%d" \
				% [ctrls.size(), ignored, btns])

	# (b) GEOMETRY --------------------------------------------------------
	func _legs_geom() -> void:
		var hud_rects: Array = []
		var hud_ctrls: Array = []
		_controls(m.get_node("HUD"), hud_ctrls)
		for c: Variant in hud_ctrls:
			var hc := c as Control
			# $Root is the full-viewport (1280x720) IGNORE background
			# CONTAINER, not a HUD text/control rect — every panel control
			# sits inside it by construction. The disjointness contract is
			# against the HUD's laid-out display controls (its children),
			# so the one background container is skipped (declared).
			if String(hc.get_path()).ends_with("/HUD/Root"):
				continue
			var hr0: Rect2 = hc.get_global_rect()
			hud_rects.append(hr0)
			print("GWMICE-GEOM h=%s,%s,%s,%s,%s" % [
					String(hc.get_path()), str(hr0.position.x),
					str(hr0.position.y), str(hr0.size.x), str(hr0.size.y)])
		for b: Variant in _panel_buttons():
			var btn := b as Button
			var r: Rect2 = btn.get_global_rect()
			print("GWMICE-GEOM b=%s,%s,%s,%s,%s" % [
					String(btn.get_path()), str(r.position.x), str(r.position.y),
					str(r.size.x), str(r.size.y)])
			if r.size.x <= 10.0 or r.size.y <= 10.0:
				_fail("panel button %s never laid out %s" \
						% [String(btn.name), str(r)])
				return
			if r.position.x < 0.0 or r.position.y < 0.0 \
					or r.position.x + r.size.x > 1280.0 \
					or r.position.y + r.size.y > 720.0:
				_fail("panel button %s off-screen %s" \
						% [String(btn.name), str(r)])
				return
			for hr: Rect2 in hud_rects:
				if _intersects(r, hr):
					_fail("panel button %s overlaps HUD rect %s" \
							% [String(btn.name), str(hr)])
					return

	func _panel_buttons() -> Array:
		var out: Array = []
		_collect_buttons(m.get_node("DefensePanel"), out)
		return out

	func _collect_buttons(n: Node, out: Array) -> void:
		if n is Button:
			out.append(n)
		for c: Node in n.get_children():
			_collect_buttons(c, out)

	func _intersects(a: Rect2, b: Rect2) -> bool:
		# Strict interior overlap: edge-touching rects are legal.
		return a.position.x < b.position.x + b.size.x \
				and b.position.x < a.position.x + a.size.x \
				and a.position.y < b.position.y + b.size.y \
				and b.position.y < a.position.y + a.size.y

	# (c) PICK ------------------------------------------------------------
	func _legs_pick() -> void:
		var btns: Array = _panel_buttons()
		for b: Variant in btns:
			(b as Button).pressed.connect(_ping.bind(String((b as Button).name)))
		for b: Variant in btns:
			var btn := b as Button
			var before := fired.duplicate()
			# Capture enabled/disabled BEFORE the click: an enabled
			# Class_* click places + refresh() re-gates affordability, so
			# reading btn.disabled after would misread a real receiver as
			# "disabled still received" (declared reading of the gate).
			var was_disabled := btn.disabled
			_click((btn as Control).get_global_rect().get_center())
			clicked += 1
			if String(btn.name).begins_with("Class_"):
				class_clicks += 1
			var mine := int(fired.get(String(btn.name), 0)) \
					- int(before.get(String(btn.name), 0))
			var total := 0
			for k: String in fired:
				total += int(fired[k])
			var before_total := 0
			for k: String in before:
				before_total += int(before[k])
			if was_disabled:
				if total != before_total:
					_fail("disabled button %s still received the click" \
							% String(btn.name))
					return
			elif mine != 1 or total - before_total != 1:
				_fail("pick %s receiver=%d extras=%d" \
						% [String(btn.name), mine,
						total - before_total - mine])
				return

	func _check_placed() -> void:
		# Class buttons place through placer.place; step (5) bookkeeping
		# mirrors defense_list into m.defenses ONE step after the click
		# (mission.gd:258, VERIFIED). The served bug's signature: the
		# clicks land nowhere -> zero defenses -> RED here.
		var placed := int(m.defenses)
		print("GWMICE-PICK clicked=%d class_clicks=%d placed=%d" \
				% [clicked, class_clicks, placed])
		if class_clicks > 0 and placed < class_clicks:
			_fail("clicks never reached the placer: class_clicks=%d " \
					% class_clicks + "defenses=%d" % placed)
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
	mon.planted = "stop_root" if OS.get_cmdline_user_args().has(
			"stop_root") else ""
	root.add_child(mon)
'''


def _run_probe(extra_args, tmp_path):
    probe = Path(tmp_path) / "gw_clicks_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), extra_args,
                                     tmp_path / "user_home")


def _rows(out, tag):
    return [ln for ln in out.splitlines() if ln.startswith(tag + " ")]


def _geom(out, kind):
    rows = {}
    for ln in _rows(out, "GWMICE-GEOM"):
        side, vals = ln.split(" ", 1)[1].split("=", 1)
        if side != kind:
            continue
        parts = vals.split(",")
        rows[parts[0]] = tuple(float(v) for v in parts[1:])
    return rows


def test_mission_clicks_engine_leg(tmp_path, class_cache):
    proc = _run_probe([], tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    out = proc.stdout
    assert "GWMICE-FAIL" not in out, out
    assert out.rstrip().endswith("GWMICE-OK"), out

    # (a) every HUD display control IGNORE; the read-only HUD owns no
    #     Button, so IGNORE cannot swallow an interactive control.
    filt = _rows(out, "GWMICE-FILTER")
    assert len(filt) == 1, out
    kv = dict(x.split("=", 1) for x in filt[0].split(" ")[1:])
    assert int(kv["controls"]) > 0 and int(kv["ignore"]) == int(kv["controls"])
    assert int(kv["buttons"]) == 0, "HUD grew an interactive control: %s" % kv

    # (b) geometry: every panel button on-screen and disjoint from every
    #     HUD rect at 1280x720 (probe asserts too; re-derive here).
    btn_rects = _geom(out, "b")
    hud_rects = _geom(out, "h")
    assert len(btn_rects) >= 6 and len(hud_rects) > 0, \
        "expected the 6 pinned panel buttons (3 class + URS + assign pair)"
    for bn, br in btn_rects.items():
        assert 0.0 <= br[0] and 0.0 <= br[1] \
            and br[0] + br[2] <= VIEW[0] and br[1] + br[3] <= VIEW[1], \
            "panel button %s off the served viewport: %s" % (bn, br)
        for hn, hr in hud_rects.items():
            assert _rect_disjoint(br, hr), \
                "panel button %s %s overlaps HUD control %s %s (W17b)" % (
                    bn, br, hn, hr)

    # (c) pick: each button center clicked; the first enabled Class_*
    #     clicks PLANTED defenses (state, not just the signal).
    picks = _rows(out, "GWMICE-PICK")
    assert len(picks) == 1, out
    pkv = dict(x.split("=", 1) for x in picks[0].split(" ")[1:])
    assert int(pkv["class_clicks"]) >= 1, pkv
    assert int(pkv["placed"]) >= int(pkv["class_clicks"]), \
        "clicks reached buttons but the placer planted nothing: %s" % pkv


def test_mission_clicks_planted_red_stop_root_goes_red(tmp_path,
                                                      class_cache):
    # The W17b regression shape (HUD/Root back to STOP): the SAME engine
    # legs MUST go RED — the swallow gate has proven it can fail.
    proc = _run_probe(["stop_root"], tmp_path)
    assert proc.returncode == 1, \
        "planted-red: HUD Root STOP slipped the engine gate\n%s" % proc.stdout
    assert "GWMICE-FAIL" in proc.stdout and "GWMICE-OK" not in \
        proc.stdout, proc.stdout
    assert "filter" in proc.stdout, \
        "expected the FILTER leg to catch the planted Root STOP"


# ---------- source truth: the fix is the one mechanism ------------------

def _hud_code():
    return hyg.blank_code(read_text(HUD_GD), "gd")


def _ignore_violations(code):
    """The HUD must run the one IGNORE pass in setup(): the recursive
    helper exists AND setup() calls it (a missing call = the W17b bug
    reintroduced — display controls back to PASS/STOP defaults)."""
    bad = []
    if "func _ignore_mouse" not in code:
        bad.append("no _ignore_mouse helper")
    if "_ignore_mouse(self)" not in code:
        bad.append("setup() never runs the IGNORE pass")
    if "MOUSE_FILTER_IGNORE" not in code:
        bad.append("no MOUSE_FILTER_IGNORE anywhere")
    return bad


def test_hud_declares_pure_display_ignore_pass():
    bad = _ignore_violations(_hud_code())
    assert not bad, "hud.gd lost the W17b display-ignore mechanism: %r" % bad


def test_hud_planted_red_missing_ignore_pass_goes_red():
    planted = _hud_code().replace("_ignore_mouse(self)", "pass", 1)
    bad = _ignore_violations(planted)
    assert bad, "planted-red: dropped IGNORE pass slipped the source gate"


def _mount_position(code):
    m = re.search(r"panel\.position = Vector2\((\d+),\s*(\d+)\)", code)
    return (int(m.group(1)), int(m.group(2))) if m else None


def _mount_violations(code):
    """The panel must mount positioned (mission.gd owns the mount line —
    W16 pinned it there). No position line = back at the origin under
    the TopLeft block (the W17b screenshot fact)."""
    bad = []
    pos = _mount_position(code)
    if pos is None:
        bad.append("mission.gd mounts the panel with no position")
    elif pos[0] < 520:
        bad.append("panel x=%d still left of/inside the TopLeft block" \
                % pos[0])
    if "add_child(panel)" not in code or "panel.setup(self)" not in code:
        bad.append("the pinned panel mount crossings are gone")
    return bad


def test_mission_mount_positions_the_panel_right_of_the_hud():
    code = hyg.blank_code(read_text(MISSION_GD), "gd")
    bad = _mount_violations(code)
    assert not bad, "mission.gd panel mount regressed: %r" % bad
    # x=904 is data-truth, not magic: TopLeft right edge 520 and BossBar
    # right edge 640+260=900 are the shipped hud.tscn rows (grep here,
    # engine-disjoint in the probe leg above).
    tscn = read_text(SCENES / "hud.tscn")
    assert "offset_right = 520.0" in tscn, "TopLeft block widened — re-check"
    assert "offset_right = 260.0" in tscn, "BossBar widened — re-check"
    assert _mount_position(code)[0] > 900, \
        "panel x must sit right of the widest HUD rect (BossBar ends 900)"


def test_mission_mount_planted_red_origin_panel_goes_red():
    code = hyg.blank_code(read_text(MISSION_GD), "gd")
    planted = code.replace(
        re.search(r"panel\.position = Vector2\(\d+,\s*\d+\)", code).group(0),
        "panel.position = Vector2(0, 0)")
    bad = _mount_violations(planted)
    assert bad, "planted-red: origin-mounted panel slipped the mount gate"


# ---------- source truth: tscn uid attributes == .uid sidecars ----------

def _ext_rows(text):
    return re.findall(
        r'\[ext_resource type="Script" uid="(uid://[a-z0-9]+)" '
        r'path="(res://[^"]+)"', text)


def _uid_consistency_violations(tscn_text):
    bad = []
    for uid, path in _ext_rows(tscn_text):
        sidecar = GODOT / Path(path.replace("res://", ""))
        if not sidecar.with_suffix(sidecar.suffix + ".uid").exists():
            bad.append("%s has no .uid sidecar" % path)
            continue
        want = sidecar.with_suffix(sidecar.suffix + ".uid").read_text(
                encoding="utf-8").strip()
        if uid != want:
            bad.append("%s: tscn uid %s != sidecar %s" % (path, uid, want))
    for stale in STALE_UIDS:
        if stale in tscn_text:
            bad.append("stale served-console uid %s still in the scene"
                       % stale)
    return bad


def test_mission_tscn_uids_match_the_sidecars():
    bad = _uid_consistency_violations(read_text(MISSION_TSCN))
    assert not bad, "mission.tscn uid drift (export ERROR source): %r" % bad
    # the three script rows carry explicit uids (an attribute-less ext
    # row resolves through the editor cache AT CONVERSION TIME — the
    # stale-cache poisoning this card closed; the .tres assets carry no
    # uid by shipped design, so exactly the 3 scripts are pinned):
    assert len(_ext_rows(read_text(MISSION_TSCN))) == 3, \
        "the script ext_resource rows must all carry uid attributes"


def test_tscn_uids_planted_red_stale_uid_goes_red():
    planted = read_text(MISSION_TSCN).replace(
        "uid://d4iftsrpsjard", "uid://dki88udyr8g1w", 1)
    bad = _uid_consistency_violations(planted)
    assert bad, "planted-red: a stale ext uid slipped the sidecar gate"
