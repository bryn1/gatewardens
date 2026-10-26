"""W13 hub-layout + mission-framing gate (MC 11274.1.22 / card 11332).

A9-journey findings F-1 (hub labels overlapped — every panel was a bare
child at the origin) and F-3 (mission world invisible at default zoom),
plus the F-2 relay mechanism pin, each gated:

- ENGINE TIER (conftest idiom): a SceneTree probe whose SOURCE LIVES HERE
  (so a clean checkout runs identically) is written to a temp dir and run
  headless: it boots the REAL Main.tscn under REAL frames (engine fact
  VERIFIED this card: under `-s` the main loop iterates once the script
  stops quitting inside _init — a child Node's _process fires and
  Container layout computes for real), reads the shipped hub's REAL
  geometry back, and asserts title / Meta / Bar / station are four
  mutually DISJOINT laid-out rows with the five station buttons on one
  distinct laid-out row of their own. EMPTY stderr (W4 ruling). The
  arg "stacked" runs the same overlap check against the F-1 regression
  shape (labels piled at the origin) — the check MUST go RED there
  (planted-red, engine tier).
- SOURCE TRUTH (stdlib): hub.gd mounts every station through the
  PanelSlot container and owns exactly one root-level layout mount
  (stacking reintroduced = RED, planted-red in-suite), and
  mission.tscn's CameraRig frames the WHOLE shipped map: every lane
  waypoint, both cores, all spawners and the hero battle space project
  inside the camera frustum at the default 75° FOV on the 1280x720
  viewport (planted-red: a sky-aimed rig must trip it). Lighting row
  pinned: WorldEnvironment ambient > 0 and a background color distinct
  from the ground albedo ("greybox fine, invisible not").

Declared reading (F-1): the shipped hub shows ONE station at a time
(hub._open), so "distinct layout position per station" is enforced the
Godot-idiomatic way the brief names (rows/anchors/containers): stations
are placed BY THE CONTAINERS, never by origins; the header rows and the
station area never intersect; any direct origin-mounted panel or manual
position assignment is RED. test_hub.py's station-routing contract
(one visible panel in the shared slot) is untouched.
"""

import json
import math
import re
import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for code greps)

GODOT = Path(conftest.repo_path("godot"))
SCRIPTS = GODOT / "scripts"
HUB_GD = SCRIPTS / "hub.gd"
MISSION_TSCN = GODOT / "scenes" / "mission.tscn"
MAP = json.loads((GODOT / "data" / "maps" / "gatefall.json").read_text())
# One Start button per shipped (map, difficulty) pair = per waves file
# (war_table derives its buttons from exactly these stems).
START_BUTTONS = len(list((GODOT / "data" / "waves").glob("waves_*.json")))


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def _rect_disjoint(a, b):
    """Strict-interior disjointness (edge-touching rows are fine)."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax < bx + bw and bx < ax + aw and ay < by + bh
                and by < ay + ah)


# ---------- engine tier: real hub geometry under real frames ----------

PROBE_SRC = '''
extends SceneTree
# gw hub-layout probe (W13). Machine rows: GWLAYOUT-STRUCT / -ROWS /
# -BTN / -F2 / -OK; any failed check prints GWLAYOUT-FAIL <rects> + rc1.
# Arg "stacked": the SAME overlap check runs against the F-1 regression
# shape (bare labels piled at the origin) and must FAIL.
const MAIN_SCENE := "res://Main.tscn"


class Monitor:
	extends Node
	var main_ref
	var stacked_flag := false
	var frames := 0

	func _process(_d: float) -> void:
		frames += 1
		if frames > 240:               # 4s ceiling: a hang is FAIL, not a spin
			print("GWLAYOUT-FAIL no layout after %d frames" % frames)
			get_tree().quit(1)
			return
		if frames < 3:
			return                       # real layout needs enter+sort
		var stacked: bool = stacked_flag
		var rects: Dictionary = {}
		var btns: Array = []
		var parents := ""
		var relayed := 0
		var ok: bool
		if stacked:
			ok = _planted(rects)
		else:
			var hub = main_ref._routed
			var stations = hub.get_node("Layout/Stations")
			rects["title"] = stations.get_child(0).get_global_rect()
			rects["meta"] = stations.get_node("Meta").get_global_rect()
			rects["bar"] = stations.get_node("Bar").get_global_rect()
			rects["station"] = hub.war.get_global_rect()
			for key: String in ["war", "gear", "blacksmith", "tinkerer",
					"dummies"]:
				parents += String(hub.get(key).get_parent().name) + ","
			for b: Node in stations.get_node("Bar").get_children():
				btns.append((b as Control).get_global_rect())
			for entry: Node in hub.war.get_node("WarTable").get_children():
				var bt := entry as Button
				if bt == null:
					continue
				for c: Dictionary in bt.pressed.get_connections():
					var fn: Callable = c["callable"]
					if String(fn.get_method()) == \\
							"_route_out_of_signal_frame":
						relayed += 1
			ok = not _overlaps(rects) and _laid_out(rects, btns)
		if not ok:
			print("GWLAYOUT-FAIL %s" % str(rects))
			get_tree().quit(1)
			return
		var parts := ""
		for key: String in rects:
			var r: Rect2 = rects[key]
			parts += "%s=%s,%s,%s,%s " % [key, str(r.position.x),
					str(r.position.y), str(r.size.x), str(r.size.y)]
		var xs := ""
		for r: Rect2 in btns:
			xs += "%s," % str(r.position.x)
		print("GWLAYOUT-STRUCT slot_parents=%s" % parents)
		print("GWLAYOUT-ROWS " + parts)
		print("GWLAYOUT-BTN x=%s" % xs)
		print("GWLAYOUT-F2 relayed=%d" % relayed)
		print("GWLAYOUT-OK")
		get_tree().quit(0)

	func _overlaps(rects: Dictionary) -> bool:
		var keys: Array = rects.keys()
		for i: int in keys.size():
			for j: int in range(i + 1, keys.size()):
				if _intersects(rects[keys[i]], rects[keys[j]]):
					return true
		return false

	func _intersects(a: Rect2, b: Rect2) -> bool:
		# Strict interior overlap: edge-touching laid-out rows are legal.
		return a.position.x < b.position.x + b.size.x \\
				and b.position.x < a.position.x + a.size.x \\
				and a.position.y < b.position.y + b.size.y \\
				and b.position.y < a.position.y + a.size.y

	func _laid_out(rects: Dictionary, btns: Array) -> bool:
		if rects["station"].position.y < rects["bar"].position.y \\
				+ rects["bar"].size.y:
			return false                  # station area below the bar
		if btns.size() != 5:
			return false
		var last_x := -1.0
		for r: Rect2 in btns:
			if r.size.x <= 10.0 or r.position.x <= last_x:
				return false              # a real laid-out row, not a pile
			last_x = r.position.x
		return true

	func _planted(rects: Dictionary) -> bool:
		# The F-1 regression shape; true = check FAILED to catch it.
		var host := Control.new()
		get_tree().root.add_child(host)
		host.size = Vector2(1280, 720)
		var i := 0
		for t: String in ["GATEWAY TITLE", "gold line", "War Table"]:
			var l := Label.new()
			l.text = t
			host.add_child(l)
			rects["row%d" % i] = l.get_global_rect()
			i += 1
		return not _overlaps(rects)


func _init() -> void:
	var packed = ResourceLoader.load(MAIN_SCENE)
	if packed == null:
		print("GWLAYOUT-FAIL Main.tscn not loadable")
		quit(1)
		return
	var main = packed.instantiate()
	root.add_child(main)
	# E5 (VERIFIED again this card): under `-s` add_child never dispatches
	# _ready — not even once frames run. The harness drives the real boot
	# entry point directly, the boot_probe precedent. Frames THEN run for
	# the Monitor so Container layout computes for real.
	main._ready()
	var mon := Monitor.new()
	mon.main_ref = main
	# Script user-args arrive after "--" (conftest.run_probe_script form)
	# and read back through OS.get_cmdline_user_args() (the SceneTree
	# script itself has no args getter in 4.7 — VERIFIED this card).
	mon.stacked_flag = "stacked" in OS.get_cmdline_user_args()
	root.add_child(mon)
'''


def _run_layout_probe(extra_args, tmp_path):
    probe = Path(tmp_path) / "gw_layout_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), extra_args,
                                     tmp_path / "user_home")


def test_hub_layout_engine_leg(tmp_path, class_cache):
    proc = _run_layout_probe([], tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    out = proc.stdout
    assert "GWLAYOUT-FAIL" not in out, out
    assert out.rstrip().endswith("GWLAYOUT-OK"), out

    struct = _kv(out, "GWLAYOUT-STRUCT")
    assert struct["slot_parents"] == ",".join(["PanelSlot"] * 5) + ",", \
        "all five stations must share the PanelSlot container: %s" % struct

    rows = _rects(out)
    # The A9 finding inverted: title / Meta / Bar / station pairwise
    # disjoint, and the station row starts below the bar row.
    keys = list(rows)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            assert _rect_disjoint(rows[a], rows[b]), \
                "F-1 overlap reintroduced: %s %s vs %s %s" % (
                    a, rows[a], b, rows[b])
    assert rows["station"][1] >= rows["bar"][1] + rows["bar"][3], rows

    btn = _kv(out, "GWLAYOUT-BTN")
    xs = [float(x) for x in btn["x"].rstrip(",").split(",")]
    assert len(xs) == 5 and xs == sorted(xs) and len(set(xs)) == 5, xs

    # F-2 mechanism pinned live: every war-table Start button crossed
    # through the hub's out-of-signal-frame relay (one mechanism).
    f2 = _kv(out, "GWLAYOUT-F2")
    assert int(f2["relayed"]) == START_BUTTONS, \
        "Start buttons not relayed (F-2): %s, want %d" % (
            f2, START_BUTTONS)


def test_hub_layout_planted_red_stacked_goes_red_engine_tier(
        tmp_path, class_cache):
    # The F-1 regression shape run through the SAME engine check: it
    # MUST go RED (an unbroken overlap check is no check).
    proc = _run_layout_probe(["stacked"], tmp_path)
    assert proc.returncode == 1, \
        "planted-red: origin-stacked labels slipped the engine check\n%s" \
        % proc.stdout
    assert "GWLAYOUT-FAIL" in proc.stdout and \
        "GWLAYOUT-OK" not in proc.stdout, proc.stdout


def _kv(out, tag):
    hits = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert len(hits) == 1, "%s row count=%d\n%s" % (tag, len(hits), out)
    return dict(kv.split("=", 1) for kv in hits[0].split(" ")[1:] if kv)


def _rects(out):
    parts = _kv(out, "GWLAYOUT-ROWS")
    return {k: tuple(float(v) for v in s.split(","))
            for k, s in parts.items()}


# ---------- source truth: hub.gd lays out through containers only ------

def _hub_code():
    return hyg.blank_code(read_text(HUB_GD), "gd")


def _stacking_violations(code):
    """The F-1 structural ban: stations mount ONLY through the slot
    container; the hub root mounts ONLY the one layout root; no manual
    positions beside the containers."""
    bad = []
    for root_mount in re.findall(r"^add_child\((\w+)\)", code, re.M):
        if root_mount != "root_box":
            bad.append("origin-mounted root child %s" % root_mount)
    for panel in ["war", "gear", "blacksmith", "tinkerer", "dummies"]:
        if not re.search(r"slot\.add_child\(%s\)" % panel, code):
            bad.append("station %s not mounted in the PanelSlot" % panel)
    if re.search(r"\.position\s*=\s*Vector2", code):
        bad.append("manual position assignment beside the containers")
    return bad


def test_hub_mounts_stations_through_containers_only():
    bad = _stacking_violations(_hub_code())
    assert not bad, "hub layout regressed toward origin stacking: %r" % bad
    for ctor in ["VBoxContainer", "HBoxContainer"]:
        assert ctor in read_text(HUB_GD), \
            "the layout scheme is containers (Godot idiom), %s missing" \
            % ctor


def test_hub_planted_red_origin_stacking_goes_red():
    planted = _hub_code().replace("slot.add_child(war)", "add_child(war)", 1)
    bad = _stacking_violations(planted)
    assert bad, "planted-red: origin-stacked station slipped the layout gate"


def test_hub_f2_relay_is_the_single_mechanism():
    code = _hub_code()
    assert re.search(r"pressed\.disconnect\(fn\)", code) and \
        re.search(r"fn\.call_deferred\(\)", code), \
        "F-2 must be the engine's own route-out-of-signal-frame relay " \
        "(re-fire the station's own crossing deferred)"
    # war_table.gd's crossing itself stays verbatim (test_hub.py pins it).
    war = hyg.blank_code(read_text(SCRIPTS / "war_table.gd"), "gd")
    assert re.search(r"router\.start_mission\(", war), \
        "the pinned start crossing must stay war_table's own"


# ---------- source truth: mission.tscn frames the WHOLE map (F-3) -----

FOV_DEG = 75.0          # Godot Camera3D default, untouched by the scene
VIEW = (1280.0, 720.0)  # the A9 screenshot viewport
MARGIN = 0.92           # points must sit INSIDE 92% of each half-FOV


def _cam_from_tscn(text):
    m = re.search(r'\[node name="CameraRig"[^\]]*\]\n'
                  r'transform = Transform3D\(([^)]*)\)', text)
    assert m, "CameraRig transform row missing in mission.tscn"
    nums = [float(x) for x in m.group(1).split(",")]
    assert len(nums) == 12, nums
    # .tscn Transform3D rows are row-major basis + origin (VERIFIED
    # against the W6 rig: the old 30° pitch row read exactly Rx(30°)).
    r0, r1, r2 = nums[0:3], nums[3:6], nums[6:9]
    origin = nums[9:12]
    z_col = (r0[2], r1[2], r2[2])           # basis Z column
    forward = tuple(-c for c in z_col)      # a camera looks down -Z
    n = math.sqrt(sum(c * c for c in forward))
    return origin, tuple(c / n for c in forward)


def _map_points():
    pts = []
    for lane in MAP["lanes"]:
        pts += [tuple(float(c) for c in wp) for wp in lane["waypoints"]]
    cores = MAP["cores"]
    pts.append(tuple(float(c) for c in cores["main"]["pos"]))
    for sub in cores["subs"]:
        pts.append(tuple(float(c) for c in sub["pos"]))
    pts += [tuple(float(c) for c in p) for p in MAP["spawners"].values()]
    pts.append((0.0, 0.0, 0.0))             # the hero pawn's battle space
    return pts


def _in_frustum(origin, forward, point):
    v = tuple(point[i] - origin[i] for i in range(3))
    along = sum(v[i] * forward[i] for i in range(3))
    if along <= 0.0:
        return False                        # behind the camera
    # Vertical = the plane spanned by forward and world up; decompose the
    # offset angle against the camera's half-FOVs in those two directions.
    f = forward
    u = (0.0, 1.0, 0.0)
    fdot = sum(f[i] * u[i] for i in range(3))
    up_p = tuple(u[i] - fdot * f[i] for i in range(3))
    un = math.sqrt(sum(c * c for c in up_p))
    up_p = tuple(c / un for c in up_p)
    right = (f[2], 0.0, -f[0])              # forward x up, horizontal
    vfov = math.radians(FOV_DEG)
    hfov = 2 * math.atan(math.tan(vfov / 2) * (VIEW[0] / VIEW[1]))
    ang_v = abs(math.atan2(sum(v[i] * up_p[i] for i in range(3)), along))
    ang_h = abs(math.atan2(abs(sum(v[i] * right[i] for i in range(3))),
                           along))
    return ang_v <= (vfov / 2) * MARGIN and ang_h <= (hfov / 2) * MARGIN


def test_mission_camera_frames_the_whole_gatefall_playfield():
    origin, forward = _cam_from_tscn(read_text(MISSION_TSCN))
    outside = [p for p in _map_points() if not _in_frustum(origin, forward, p)]
    assert not outside, \
        "map points outside the default frustum (F-3: field of play " \
        "unframed/invisible): %r" % (outside[:8],)


def test_mission_framing_planted_red_aimed_away_goes_red():
    # Fixture trick (nothing written): a rig pitched near the sky must
    # trip the frustum gate — an unbroken framing gate is no gate.
    planted = read_text(MISSION_TSCN).replace(
        "transform = Transform3D(1, 0, 0, 0, 0.667, 0.667, 0, -0.746, "
        "0.746, 0, 58, 46)",
        "transform = Transform3D(1, 0, 0, 0, 0.995, -0.0995, 0, 0.0995, "
        "0.995, 0, 58, 46)")
    assert planted != read_text(MISSION_TSCN)
    origin, forward = _cam_from_tscn(planted)
    assert any(not _in_frustum(origin, forward, p) for p in _map_points()), \
        "planted-red: sky-aimed rig slipped the framing gate"


def test_mission_lighting_row_exists():
    text = read_text(MISSION_TSCN)
    ambient = re.search(r"ambient_light_energy\s*=\s*([0-9.]+)", text)
    assert 'type="WorldEnvironment"' in text and ambient \
        and float(ambient.group(1)) > 0.0, \
        "greybox must be LIT (F-3): WorldEnvironment ambient > 0"
    bg = re.search(r"background_color = Color\(([0-9., ]+)\)", text)
    assert bg, "custom background row missing (ground-vs-sky contrast)"
    ground = re.search(r"albedo_color = Color\(([0-9., ]+)\)",
                       read_text(GODOT / "assets" / "mat_ground.tres"))
    bg_c = [float(x) for x in bg.group(1).split(",")]
    gr_c = [float(x) for x in ground.group(1).split(",")]
    assert sum(abs(a - b) for a, b in zip(bg_c, gr_c)) > 0.15, \
        "background and ground read identical — the world dissolves (F-3)"
