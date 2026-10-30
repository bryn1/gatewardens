"""G2 lit lane bands (MC card 11694 / V121-PLAN G2).

The band contract, per the plan (Rev 2 binding): a lit translucent band
painted along the EXISTING waypoint polylines — per GROUND lane one
quad-strip MeshInstance3D at y slightly > 0, one material, reading
m.lanes (build_lanes' records) ONLY. AIR lanes get NO band (the winged
gate-eye of G1 is their declared cue). One mechanism: the static
builder lane_bands.gd, called ONCE from mission_world.build_cores (the
paint_arena/G1 visual-hook precedent); mission.gd adds ZERO lines (it
sits at the 400-line ceiling). No duplicated lane geometry, no second
lane model, no new lane semantics — visual-only, zero sim writes.

ENGINE LEG: the shipped kit godot/sim/g2_lane_band_probe.gd (boot idiom
= g1_gate_eye_probe) asserts the band node count == ground-lane count,
the per-lane one-quad-per-segment vertex count, the pinned
lit-translucent material shape, sampled waypoints FOLLOWING the lane
wps within the declared EPS, and the air-lane NEGATIVE row (without it
an inverted kind filter stays green — fleet negative-leg rule). It
also refuses to print LB-OK if the pass aborted mid-way (a GDScript
runtime error aborts a function SILENTLY, rc stays 0 — proven this
session), so the transcript, not the rc, is the contract. Transcript
rows re-checked here, not eyeballed; stderr must be EMPTY.

SOURCE-TRUTH LEGS (pytest cannot exec GDScript — the test_gate_eye/
test_heroes idiom parses the .gd text): exactly ONE mount call in
build_cores, the builder reads m.lanes and NEVER m.map_def (the band
rides build_lanes' public records — no second lane model), it WRITES
nothing on m (mount child only), and the kind filter is the literal
"ground" branch with air continuing.

DATA LEG: gatefall.json itself is re-read — ground lanes are exactly
{lane_g1, lane_g2, lane_g3} and air exactly {lane_a1, lane_a2}: the
map contract the probe's pinned counts and the band==ground pin rest
on. Every ground lane carries >= 2 waypoints (a drawable segment).
"""

import json
import re

import conftest
from conftest import repo_path

PROBE = "res://sim/g2_lane_band_probe.gd"
BANDS_GD = repo_path("godot", "scripts", "lane_bands.gd")
WORLD_GD = repo_path("godot", "scripts", "mission_world.gd")
MAP_JSON = repo_path("godot", "data", "maps", "gatefall.json")

GROUND = {"lane_g1", "lane_g2", "lane_g3"}
AIR = {"lane_a1", "lane_a2"}
EPS = "0.05"


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def test_lane_band_engine_probe(tmp_path, class_cache):
    proc = conftest.run_probe_script(PROBE, (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "LB-FAIL" not in out, out
    assert out.splitlines()[-1] == "LB-OK", \
        "LB-OK must be the LAST transcript row (completion, not rc)"
    assert "LB-BANDS n=3 ground=3" in out, out
    bands = [ln for ln in out.splitlines() if ln.startswith("LB-BAND ")]
    assert len(bands) == 3 and {ln.split()[1] for ln in bands} == GROUND, out
    wps = [ln for ln in out.splitlines() if ln.startswith("LB-WPS ")]
    assert len(wps) == 3, out          # every ground lane's wps followed
    assert all(("eps=" + EPS) in ln for ln in wps), out
    # NEGATIVE leg: air lanes carry NO band.
    assert "LB-NEG air=2 banded=0" in out.splitlines(), out
    assert "LB-OK" in out.splitlines(), out


def test_mount_one_call_in_build_cores_source_truth():
    """The mount is exactly ONE call in the build_cores visual hook (the
    paint_arena/G1 precedent — mission.gd at its 400-line ceiling adds
    ZERO lines); the geometry itself lives in the builder file, not
    bolted onto mission_world (one concern per file)."""
    world = read(WORLD_GD)
    assert 'const LANE_BANDS := preload("res://scripts/lane_bands.gd")' \
        in world, "builder preloaded on the const block (G1 idiom)"
    cores = _fn_body(world, "static func build_cores(")
    assert cores.count("LANE_BANDS.paint_lane_bands(m)") == 1, cores
    assert "paint_arena(m)" in cores, cores      # the hook home unchanged
    assert "paint_spawn_gates(m)" in cores, cores
    assert "ArrayMesh" not in world and "ARRAY_VERTEX" not in world, \
        "geometry must live in lane_bands.gd, not mission_world"


def _fn_body(text, header):
    start = text.index(header)
    rest = text[start + len(header):]
    end = rest.find("\nstatic func ")
    return rest if end < 0 else rest[:end]


def test_builder_reads_lane_data_only_source_truth():
    """No duplicated lane geometry and zero sim writes: the builder
    reads m.lanes (build_lanes' PUBLIC records — the plan's named read)
    and never re-reads m.map_def, never touches any other m field, and
    assigns NOTHING onto m (the mount child is a node add, not state).
    The kind filter is the literal ground branch; air continues."""
    src = read(BANDS_GD)
    mount = _fn_body(src, "static func paint_lane_bands(")
    assert 'if String(lane["kind"]) != "ground":' in mount, mount
    assert "m.map_def" not in src, "band must ride build_lanes, not a " \
        "second lane model off the raw map"
    assert re.search(r'(?<![\w.])m\.[\w.\[\]"]*\s*=[^=]', src) is None, \
        "lane_bands must assign NOTHING onto m (visual-only, zero writes)"
    assert mount.count("m.add_child(") == 1, mount
    assert mount.count("MeshInstance3D.new()") == 1, \
        "one node per ground lane, ONE mechanism"


def test_gatefall_ground_air_split_is_the_pinned_data():
    """DATA leg: the probe pins ground=3/air=2 and the NEG row names
    the air set; both rest on this map contract, re-read here — the
    ground lanes are exactly {lane_g1, lane_g2, lane_g3}, air exactly
    {lane_a1, lane_a2}, and every ground lane carries >= 2 waypoints
    (at least one drawable segment, so a missing band always trips the
    BANDS row rather than spinning vacuous)."""
    with open(MAP_JSON, encoding="utf-8") as fh:
        mmap = json.load(fh)
    ground = {lane["id"] for lane in mmap["lanes"]
              if lane["kind"] == "ground"}
    air = {lane["id"] for lane in mmap["lanes"] if lane["kind"] == "air"}
    assert ground == GROUND, ground
    assert air == AIR, air
    for lane in mmap["lanes"]:
        if lane["kind"] == "ground":
            assert len(lane["waypoints"]) >= 2, lane["id"]
