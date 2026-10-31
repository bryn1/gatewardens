"""Z2 camera-zoom unit legs (v1.3 zoom, MC card 11813; ZOOM_SPEC §1-§2
.audits/20261031-1100-v13-zoom-plan/, DA-verdict-c2 SHIP). The script
camera_zoom.gd is NOT mounted in mission.tscn yet (Z3 wires it) — these
legs instantiate the script DIRECTLY, the g5_real_relay_probe idiom
("the closest production analogue runnable under -s"): a fake Node3D
rig stands at the shipped mission.tscn:34 CameraRig row VERBATIM and
SYNTHESIZED InputEventMouseButton WHEEL_UP/DOWN events (the shipped
wheel model of test_hub_scroll.py:249-251 — button_index, pressed) are
fed through the script's OWN _unhandled_input.

Legs (machine rows ZM-*):
- CAP       _ready captures the default FROM the scene row — no 64
            literal in the script: the distance is |origin| ~ 63.9092.
- STEP      one wheel-DOWN tick = +ZOOM_STEP exactly; one wheel-UP tick
            back = the default again (round-trip exact, ±0.01).
- DEDUP     the SAME tick (press+release pair, the g5 _mouse shape) fed
            TWICE inside ONE event frame = EXACTLY ONE step — the §1
            press-only + per-frame edge guard keyed on button_index
            (frame source Engine.get_process_frames(), declared in the
            script header, DA note N-A).
- 2FRAMES   one tick on THIS frame + one tick on the NEXT frame = TWO
            steps — the guard never eats real input.
- BOUNDMIN  repeated wheel-UP ticks (each its own frame) clamp at
            D_MIN=56.0 and STAY there under a further tick.
- BOUNDMAX  repeated wheel-DOWN ticks clamp at D_MAX=128.0; one UP tick
            interleaved at the ceiling steps off to 120.0 and back DOWN
            re-clamps 128.0 (order of ticks irrelevant).
- PRESSONLY a release-only feed steps NOTHING.
- BASIS     the rig basis (the tscn row's pitch basis) is byte-equal
            after the whole leg — the D3 pin, position-only writes.
PLANTED-RED (permanent): the source-truth clamp gate below — replacing
the clampf() with its raw argument goes RED (same gate, fixture trick,
nothing written); the engine BOUNDMIN/BOUNDMAX legs are its numeric
twins (the card's break-the-clamp transcript lives in the Z2.log).
SOURCE TRUTH (stdlib): camera_zoom.gd stays OUT of GOVERNED_LITERALS
(presentation numbers, the range_ring/world_text doctrine) and the
pinned set stays 17.
"""

import os
import re
import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for code greps)

CAMERA_ZOOM_GD = conftest.repo_path("godot", "scripts", "camera_zoom.gd")

# The shipped rig owner row, godot/scenes/mission.tscn:34 —
# `transform = Transform3D(1, 0, 0, 0, 0.669, 0.743, 0, -0.743, 0.669,
# 0, 47.47, 42.79)` — rendered in GDScript notation (identical values:
# the three tscn basis rows + origin; 4.x has no 12-float constructor).
# The fake rig stands at the byte-pinned default the zoom node captures.
RIG_BASIS = ("Basis(Vector3(1.0, 0.0, 0.0), Vector3(0.0, 0.669, 0.743), "
             "Vector3(0.0, -0.743, 0.669))")
RIG_ORIGIN = "Vector3(0.0, 47.47, 42.79)"

PROBE_SRC = '''\\

extends SceneTree
# gw camera-zoom probe (Z2, MC 11813). Machine rows ZM-CAP / -STEP /
# -DEDUP / -2FRAMES / -BOUNDMIN / -BOUNDMAX / -PRESSONLY / -BASIS /
# -OK; any failed check prints ZM-FAIL <detail> + rc1. Instantiates
# camera_zoom.gd directly under a fake rig at the shipped row.
const ZOOM := preload("res://scripts/camera_zoom.gd")

var _f := 0
var _rig: Node3D = null
var _zoom: Node = null
var _d0 := 0.0
var _basis := Basis()
var _d := 0.0
var _off := 0.0


func _init() -> void:
	_rig = Node3D.new()
	_rig.name = "FakeRig"
	_rig.transform = Transform3D(@RIG_BASIS@, @RIG_ORIGIN@)
	root.add_child(_rig)
	_zoom = ZOOM.new()
	_zoom.name = "CameraZoom"
	_rig.add_child(_zoom)
	_zoom._ready()               # E5 under -s: add_child dispatches no
	                             # _ready; the harness drives it (g5 idiom)


# One physical wheel tick: the g5_real_relay_probe._mouse press+release
# pair, fed DIRECTLY into the zoom node's own handler.
func _tick(up: bool) -> void:
	for down: bool in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_WHEEL_UP if up \\
				else MOUSE_BUTTON_WHEEL_DOWN
		ev.pressed = down
		_zoom._unhandled_input(ev)


func _dist() -> float:
	return _rig.position.length()


func _near(a: float, b: float) -> bool:
	return absf(a - b) < 0.01


func _fail(why: String) -> void:
	print("ZM-FAIL " + why)
	quit(1)


# feed: one _tick in THIS frame; expect: the distance checked NEXT
# frame; act/assert ordering keeps every assert in its own _process
# frame, so Engine.get_process_frames() moved exactly one between ticks.
func _process(_delta: float) -> bool:
	_f += 1
	if _f == 1:
		_d0 = _dist()
		_basis = _rig.transform.basis
		if not _near(_d0, 63.909195):
			_fail("CAP captured d=%.6f, wanted |origin| ~ 63.9092" % _d0)
			return true
		print("ZM-CAP d=%.6f" % _d0)
	elif _f == 2:
		_tick(false)                      # wheel-DOWN: zoom OUT one step
	elif _f == 3:
		_d = _dist()
		if not _near(_d, _d0 + 8.0):
			_fail("STEP down d=%.6f, wanted %.6f" % [_d, _d0 + 8.0])
			return true
		_tick(true)                       # wheel-UP: back one step
	elif _f == 4:
		_d = _dist()
		if not _near(_d, _d0):
			_fail("STEP round-trip d=%.6f, wanted %.6f" % [_d, _d0])
			return true
		print("ZM-STEP down=%.6f back=%.6f" % [_d0 + 8.0, _d])
		_tick(false)                      # SAME tick fed TWICE, SAME
		_tick(false)                      #   frame: the web double-feed
	elif _f == 5:
		_d = _dist()
		if not _near(_d, _d0 + 8.0):
			_fail("DEDUP same-frame double-feed stepped d=%.6f, wanted " \\
					+ "one step %.6f" % [_d, _d0 + 8.0])
			return true
		print("ZM-DEDUP steps=1 d=%.6f" % _d)
		_tick(false)                      # the SAME button, a NEW frame:
		                                  #   two distinct ticks ...
	elif _f == 6:
		_d = _dist()
		if not _near(_d, _d0 + 16.0):
			_fail("2FRAMES two distinct frames stepped d=%.6f, wanted " \\
					+ "two steps %.6f" % [_d, _d0 + 16.0])
			return true
		print("ZM-2FRAMES steps=2 d=%.6f" % _d)
	elif _f >= 7 and _f <= 14:
		_tick(true)                       # 8 UP ticks, each its own frame
	elif _f == 15:
		_d = _dist()
		if not _near(_d, 56.0):
			_fail("BOUNDMIN floor d=%.6f, wanted D_MIN 56.0" % _d)
			return true
		_tick(true)                       # one MORE up at the floor
	elif _f == 16:
		_d = _dist()
		if not _near(_d, 56.0):
			_fail("BOUNDMIN floor moved to %.6f under a further tick" % _d)
			return true
		print("ZM-BOUNDMIN d=%.6f" % _d)
	elif _f >= 17 and _f <= 28:
		_tick(false)                      # 12 DOWN ticks: past the cap
	elif _f == 29:
		_d = _dist()
		if not _near(_d, 128.0):
			_fail("BOUNDMAX ceiling d=%.6f, wanted D_MAX 128.0" % _d)
			return true
		_tick(true)                       # order of ticks irrelevant:
		                                  #   UP off the ceiling ...
	elif _f == 30:
		_d = _dist()
		if not _near(_d, 120.0):
			_fail("BOUNDMAX step-off d=%.6f, wanted 120.0" % _d)
			return true
		_off = _d
		_tick(false)
		_tick(false)                      #   ... and DOWN re-clamps
	elif _f == 31:
		_d = _dist()
		if not _near(_d, 128.0):
			_fail("BOUNDMAX re-clamp d=%.6f, wanted 128.0" % _d)
			return true
		print("ZM-BOUNDMAX d=%.6f off=%.6f" % [_d, _off])
		_zoom._unhandled_input(_release_only())   # a release NEVER steps
	elif _f == 32:
		_d = _dist()
		if not _near(_d, 128.0):
			_fail("PRESSONLY a release stepped to %.6f" % _d)
			return true
		print("ZM-PRESSONLY d=%.6f" % _d)
		if _rig.transform.basis != _basis:
			_fail("BASIS the rig basis moved: %s" % _rig.transform.basis)
			return true
		print("ZM-BASIS unchanged=true")
		print("ZM-OK")
		quit(0)
	return false


func _release_only() -> InputEventMouseButton:
	var ev := InputEventMouseButton.new()
	ev.button_index = MOUSE_BUTTON_WHEEL_UP
	ev.pressed = false
	return ev
'''.replace("@RIG_BASIS@", RIG_BASIS).replace("@RIG_ORIGIN@", RIG_ORIGIN)


def _run_zoom_probe(tmp_path):
    probe = Path(tmp_path) / "gw_zoom_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), [], tmp_path / "user_home")


def _kv(out, tag):
    hits = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert len(hits) == 1, "%s row count=%d\n%s" % (tag, len(hits), out)
    return dict(kv.split("=", 1) for kv in
                hits[0].split(" ")[1:] if kv)


def test_camera_zoom_wheel_legs_engine(tmp_path, class_cache):
    # The 8 legs above, through the script's OWN _unhandled_input (kit
    # idiom, g5_real_relay_probe). EMPTY stderr (W4 ruling).
    proc = _run_zoom_probe(tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    out = proc.stdout
    assert "ZM-FAIL" not in out, out
    assert out.rstrip().endswith("ZM-OK"), out

    # Second lock: re-assert the printed machine rows numerically
    # (test_hub_scroll idiom — the probe cannot pass on a silent leg).
    near = lambda v, w: abs(float(v) - w) < 0.01
    assert near(_kv(out, "ZM-CAP")["d"], 63.909195), out       # tscn:34
    st = _kv(out, "ZM-STEP")
    assert near(st["down"], 71.909195) and near(st["back"], 63.909195), out
    assert near(_kv(out, "ZM-DEDUP")["d"], 71.909195), out     # 1 step
    assert near(_kv(out, "ZM-2FRAMES")["d"], 79.909195), out   # 2 steps
    assert near(_kv(out, "ZM-BOUNDMIN")["d"], 56.0), out
    bm = _kv(out, "ZM-BOUNDMAX")
    assert near(bm["d"], 128.0) and near(bm["off"], 120.0), out
    assert near(_kv(out, "ZM-PRESSONLY")["d"], 128.0), out
    assert _kv(out, "ZM-BASIS")["unchanged"] == "true", out


# ---------- source truth: ungoverned set + the clamp gate ------------

def _zoom_code():
    return hyg.blank_code(Path(CAMERA_ZOOM_GD).read_text(encoding="utf-8"),
                          "gd")


def _clamp_violations(code):
    bad = []
    if not re.search(r"clampf\([^)]*\bD_MIN\b[^)]*\bD_MAX\b", code):
        bad.append("the step must be applied THROUGH clampf(..., D_MIN, "
                   "D_MAX) — the envelope is the contract (ZOOM_SPEC §2)")
    return bad


def test_camera_zoom_stays_ungoverned_set_stays_17():
    # The new file joins the DECLARED-UNGOVERNED presentation doctrine
    # (range_ring/world_text/sprite_bank/hero_pawn-crest family), NOT
    # the pinned governed set: 17 -> 17, unchanged (ZOOM_SPEC §2).
    rel = os.path.join("godot", "scripts", "camera_zoom.gd")
    assert rel not in hyg.GOVERNED_LITERALS, \
        "camera_zoom.gd must NOT join GOVERNED_LITERALS (set is a " \
        "same-commit governance event, pin #10)"
    assert len(hyg.GOVERNED_LITERALS) == 17, \
        "GOVERNED_LITERALS changed size: %d" % len(hyg.GOVERNED_LITERALS)


def test_camera_zoom_planted_red_unclamped_step_goes_red():
    # Fixture trick (nothing written): apply the raw step, skip the
    # clamp — the SAME gate MUST catch it (a clamp that has never gone
    # RED is no clamp).
    planted = re.sub(r"clampf\(([^)]*)\)", r"(\1)", _zoom_code(), count=1)
    bad = _clamp_violations(planted)
    assert bad, "planted-red: an unclamped step slipped the zoom gate"
    assert not _clamp_violations(_zoom_code()), \
        "the shipped zoom script must pass its own clamp gate"
