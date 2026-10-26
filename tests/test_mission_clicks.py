"""W17b+W17c mission-clicks gate (MC 11274.1.29/.30 / cards 11386-11387).

Journey-found P1s, one false-green class: the harness had powers the
player did not. W17b: the served panel was UNCLICKABLE — the CODE-BUILT
display controls on the top CanvasLayer kept engine defaults (hero-slot
VBox=PASS, ProgressBars=STOP: a Control that ANSWERS a click swallows
what is beneath it; the hud.tscn rows were IGNORE since W10). W17c:
select_defense was harness-only — Upgrade/Repair/Sell were player-
unreachable. Full transcripts: evidence W17b/W17c. The probe SOURCE
LIVES HERE (test_hub_layout.py idiom; a clean checkout runs the same).

ENGINE TIER (EMPTY stderr, W4 ruling): boot the REAL mission under -s,
force the served size (root.size=Vector2i(1280,720) takes effect under
-s, VERIFIED; the dummy display starts 64x64), read the REAL tree back:
  (a) FILTER — every HUD Control IGNORE; the read-only HUD owns ZERO
      Buttons (IGNORE then cannot swallow an interactive control);
  (b) GEOMETRY — panel Buttons on-screen + disjoint from the HUD rects
      at 1280x720 ($Root, the full-viewport background container, is
      excluded — declared in-probe; panel controls sit inside it);
  (c) PICK — each Button center clicked through the engine's OWN
      Viewport GUI picking (root.push_input = the pipeline browser
      input enters on web; the Button emitting `pressed` IS the
      receiver): enabled pick THEMSELVES, disabled receive NOTHING,
      Class_* clicks PLANT defenses (state one bookkeeping step later);
  (d) SELECT (W17c) — placed defenses get ROWS; a ROW click sets
      selected_uid and marks it "»"; Upgrade tiers +1 with an EXACT
      green drop; Sell clears the selection and removes the row.
PLANTED-RED (engine tier): "stop_root" (Root back to STOP) and
"no_row_refresh" (rows detached) — the SAME legs MUST go RED.
SOURCE TRUTH (stdlib): the _ignore_mouse pass; the mount positions the
panel (x=904 clears TopLeft 520 / BossBar 900); every ext_resource uid
== its .uid sidecar (the stale uid://dki88udyr8g1w / uid://n3w0umenqbws
pair poisoned the EXPORTED mission.scn — byte-proofs in evidence).
"""

import json
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


# ---------- engine tier: real mission, real picking, real frames --------

PROBE_SRC = '''
extends SceneTree
# gw mission-clicks probe (W17b + W17c). Machine rows: GWMICE-FILTER /
# -GEOM / -PICK / -SEL / -UPL / -UPL2 / -SEL2 / -OK; any failed check
# prints GWMICE-FAIL <detail> + rc1. PLANTED-RED args: "stop_root" (HUD
# Root back to STOP — the W17b shape) and "no_row_refresh" (rows surface
# detached — the W17c shape); the SAME legs must go RED.
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
	var sel_uid := 0
	var pre_tier := 0
	var pre_green := 0
	var up_cost := 0

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
		# The Viewport's OWN GUI picking (the browser-input pipeline); the
		# Button that receives this complete press emits `pressed`.
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
		if frames == 4 and planted == "no_row_refresh":
			# PLANT: detach the rows surface (the W17c regression).
			var bx = m.get_node("DefensePanel/Rows")
			bx.remove_child(m.get_node("DefensePanel/Rows/Rows_defenses"))
		if frames == 6:
			_legs_filter()
			_legs_geom()
			_legs_pick()
		if frames == 7:
			_check_placed()
			_sel_rows()
		if frames == 8:
			_sel_select()
		if frames == 9:
			_sel_upgrade()
		if frames == 10:
			_sel_sell()

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
			# $Root is the full-viewport IGNORE background CONTAINER, not
			# a HUD text/control rect (every panel control sits inside it
			# by construction) — the disjointness contract is against the
			# laid-out display controls, so it is skipped (declared).
			if String(hc.get_path()).ends_with("/HUD/Root"):
				continue
			var hr0: Rect2 = hc.get_global_rect()
			hud_rects.append(hr0)
			print("GWMICE-GEOM h=%s,%s,%s,%s,%s" % [String(hc.get_path()), str(hr0.position.x), str(hr0.position.y), str(hr0.size.x), str(hr0.size.y)])
		for b: Variant in _panel_buttons():
			var btn := b as Button
			var r: Rect2 = btn.get_global_rect()
			print("GWMICE-GEOM b=%s,%s,%s,%s,%s" % [String(btn.get_path()), str(r.position.x), str(r.position.y), str(r.size.x), str(r.size.y)])
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
			# Read enabled/disabled BEFORE the click: an enabled Class_*
			# click places + refresh() re-gates affordability (declared).
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
		# step (5) mirrors defense_list into m.defenses ONE step after the
		# click (mission.gd:258, VERIFIED). Served bug: zero defenses.
		var placed := int(m.defenses)
		print("GWMICE-PICK clicked=%d class_clicks=%d placed=%d" \
				% [clicked, class_clicks, placed])
		if class_clicks > 0 and placed < class_clicks:
			_fail("clicks never reached the placer: class_clicks=%d " \
					% class_clicks + "defenses=%d" % placed)
			return

	# (d) W17c SELECT (frames 7-10): ROW click SELECTS -> Upgrade -> Sell.
	func _sel_rows() -> void:
		var box = m.get_node_or_null("DefensePanel/Rows/Rows_defenses")
		if box == null:
			_fail("defense rows surface missing (no player select path)")
			return
		var rows: Array = box.get_children()
		sel_uid = int(m.defense_list[0]["uid"])
		print("GWMICE-SEL rows=%d list=%d want_uid=%d" \
				% [rows.size(), m.defense_list.size(), sel_uid])
		if rows.is_empty() or int(m.defense_list.size()) == 0:
			_fail("no defense ROWS after place (refresh not rebuilding)")
			return
		var row = box.get_node_or_null("Row_%d" % sel_uid)
		if row == null:
			_fail("no Row_%d in the DEFENSES list" % sel_uid)
			return
		_click((row as Control).get_global_rect().get_center())

	func _sel_select() -> void:
		var p = m.get_node("DefensePanel")
		if int(p.selected_uid) != sel_uid:
			_fail("row click set selected_uid=%d not %d" \
					% [int(p.selected_uid), sel_uid])
			return
		var box = m.get_node("DefensePanel/Rows/Rows_defenses")
		var row = box.get_node("Row_%d" % sel_uid)
		if not String(row.text).begins_with("»"):
			_fail("selected row not visibly marked: %s" % String(row.text))
			return
		var obj = m.defense_list[0]["obj"]
		up_cost = int(obj.next_upgrade_cost())
		pre_tier = int(obj.tier)
		pre_green = int(m.green)
		print("GWMICE-UPL cost=%d green=%d tier=%d" % [up_cost,
				pre_green, pre_tier])
		if p.upgrade_btn.disabled:
			_fail("Upgrade still disabled while a defense is selected")
			return
		_click((p.upgrade_btn as Control).get_global_rect().get_center())

	func _sel_upgrade() -> void:
		var obj = m.defense_list[0]["obj"]
		var drop := pre_green - int(m.green)
		print("GWMICE-UPL2 tier=%d green_drop=%d" % [int(obj.tier), drop])
		if int(obj.tier) != pre_tier + 1 or drop != up_cost or up_cost <= 0:
			_fail("Upgrade button did not tier+1/exact-cost (tier %d, " \
					% int(obj.tier) + "drop %d, cost %d)" % [drop, up_cost])
			return
		var p = m.get_node("DefensePanel")
		if p.sell_btn.disabled:
			_fail("Sell disabled while a defense is selected")
			return
		_click((p.sell_btn as Control).get_global_rect().get_center())

	func _sel_sell() -> void:
		var p = m.get_node("DefensePanel")
		var box = m.get_node("DefensePanel/Rows/Rows_defenses")
		print("GWMICE-SEL2 selected=%d rows=%d list=%d" \
				% [int(p.selected_uid), box.get_children().size(), \
				int(m.defense_list.size())])
		if int(p.selected_uid) != 0 \
				or box.get_node_or_null("Row_%d" % sel_uid) != null:
			_fail("Sell did not clear selection + its row")
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
	mon.planted = "stop_root" if args.has("stop_root") else (
			"no_row_refresh" if args.has("no_row_refresh") else "")
	root.add_child(mon)
'''


def _run_probe(extra_args, tmp_path):
    probe = Path(tmp_path) / "gw_clicks_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), extra_args,
                                     tmp_path / "user_home")


def _rows(out, tag):
    return [ln for ln in out.splitlines() if ln.startswith(tag + " ")]


def _kv(line):
    return dict(x.split("=", 1) for x in line.split(" ")[1:])


def _only(out, tag):
    r = _rows(out, tag)
    assert len(r) == 1, out
    return r[0]


def _upgrade_cost_t1():
    """T1->T2 = base_cost * upgrade_ratios[0] (C3), mirrored FROM DATA."""
    towers = json.loads(read_text(GODOT / "data/towers.json"))
    rows = towers["towers"] if isinstance(towers, dict) else towers
    base = next(r["base_cost"] for r in rows if r["class"] == "tower")
    eco = json.loads(read_text(GODOT / "data/economy.json"))
    return int(base * eco["upgrade_ratios"][0])


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

    # (b) geometry: every panel button on-screen at 1280x720; the
    #     disjointness check runs IN-PROBE (guard: no GWMICE-FAIL).
    btn_rects = _geom(out, "b")
    assert len(btn_rects) >= 6 and len(_geom(out, "h")) > 0, \
        "expected the 6 pinned panel buttons (3 class + URS + assign pair)"
    for bn, br in btn_rects.items():
        assert 0.0 <= br[0] and 0.0 <= br[1] \
            and br[0] + br[2] <= VIEW[0] and br[1] + br[3] <= VIEW[1], \
            "panel button %s off the served viewport: %s" % (bn, br)

    # (c) pick: the enabled Class_* clicks PLANTED defenses (state).
    picks = _rows(out, "GWMICE-PICK")
    assert len(picks) == 1, out
    pkv = dict(x.split("=", 1) for x in picks[0].split(" ")[1:])
    assert int(pkv["class_clicks"]) >= 1, pkv
    assert int(pkv["placed"]) >= int(pkv["class_clicks"]), \
        "clicks reached buttons but the placer planted nothing: %s" % pkv

    # (d) W17c SELECT: place -> ROW; the row click SELECTS (its "»" mark
    #     asserted in-probe); Upgrade tiers up with the EXACT data cost;
    #     Sell clears the selection and removes exactly the sold row.
    skv = _kv(_only(out, "GWMICE-SEL"))
    assert int(skv["rows"]) == int(skv["list"]) >= 1, skv
    u = _kv(_only(out, "GWMICE-UPL"))
    u2 = _kv(_only(out, "GWMICE-UPL2"))
    s2 = _kv(_only(out, "GWMICE-SEL2"))
    assert int(u["cost"]) == _upgrade_cost_t1(), \
        "upgrade cost off the shipped formula: %s != %d" % (
            u["cost"], _upgrade_cost_t1())
    assert int(u2["tier"]) == int(u["tier"]) + 1, (u, u2)
    assert int(u2["green_drop"]) == int(u["cost"]), (u, u2)
    assert int(s2["selected"]) == 0, s2
    assert int(s2["rows"]) == int(s2["list"]) == int(skv["rows"]) - 1, \
        "sell did not remove exactly the sold row: %s" % s2


def test_mission_clicks_planted_red_no_row_refresh_goes_red(tmp_path,
                                                            class_cache):
    # The W17c regression shape (the rows surface detached — the player
    # select path gone): the SELECT leg MUST go RED.
    proc = _run_probe(["no_row_refresh"], tmp_path)
    assert proc.returncode == 1, \
        "planted-red: detached rows slipped the engine gate\n%s" % proc.stdout
    assert "GWMICE-FAIL" in proc.stdout and "GWMICE-OK" not in \
        proc.stdout, proc.stdout


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
