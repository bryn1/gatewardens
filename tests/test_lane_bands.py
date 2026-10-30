"""G2 lit lane bands (MC card 11694 / V121-PLAN G2; G2-FIX MC 11698).

The band contract, per the plan (Rev 2 binding): a lit translucent band
painted along the EXISTING waypoint polylines — per GROUND lane ONE
band node carrying one segment plane per waypoint segment at y
slightly > 0, one material, reading m.lanes (build_lanes' records)
ONLY. AIR lanes get NO band (the winged gate-eye of G1 is their
declared cue). One mechanism: the static builder lane_bands.gd, called
ONCE from mission_world.build_cores (the paint_arena/G1 visual-hook
precedent); mission.gd adds ZERO lines (it sits at the 400-line
ceiling). No duplicated lane geometry, no second lane model, no new
lane semantics — visual-only, zero sim writes.

THE G2-FIX (MC 11698): the original mesh mechanism — a runtime-built
ArrayMesh + material_override per lane — built correct nodes headless
yet rasterized NOTHING in the web export (pure red BAND_COLOR measured
6 px on a VERIFIED build-phase frame, w2-bandexp3, while Sprite3D/
Label3D children of the same parent painted; BAND_Y/cull/UV-array
param probes changed nothing — the MECHANISM was the bug). Each band
is now a Node3D named LaneBand_<id> whose CHILD MeshInstance3Ds each
carry a unit PlaneMesh (a PrimitiveMesh — the engine-managed class the
arena ground rasterizes from under GL Compatibility, and that paints
through material_override in that same web build), positioned at the
segment midpoint, rotated to the segment direction, scaled to
(segment length, 1, BAND_WIDTH). Node names, lane counts, the read-
only m.lanes contract and every probe/test LEG are preserved.

ENGINE LEG: the shipped kit godot/sim/g2_lane_band_probe.gd (boot idiom
= g1_gate_eye_probe) asserts the band node count == ground-lane count,
the per-lane one-segment-per-wp-segment child count, the pinned
midpoint/scale/material shape of every segment, the LB-CLASS rows
(every segment mesh is a PlaneMesh AND a PrimitiveMesh — the machine-
checkable WEB-PROOF PROXY for GL Compatibility rasterization),
sampled waypoints FOLLOWING the lane wps via the NODE-derived segment
endpoints within the declared EPS, and the air-lane NEGATIVE row
(without it an inverted kind filter stays green — fleet negative-leg
rule). It also refuses to print LB-OK if the pass aborted mid-way (a
GDScript runtime error aborts a function SILENTLY, rc stays 0 — proven
in the G2 session), so the transcript, not the rc, is the contract.
Transcript rows re-checked here, not eyeballed; stderr must be EMPTY.
The served-browser PIXEL re-check (expected >20k band-tinted px on a
build-phase frame) is the orchestrator's leg — pytest cannot run a
browser.

SOURCE-TRUTH LEGS (pytest cannot exec GDScript — the test_gate_eye/
test_heroes idiom parses the .gd text): exactly ONE mount call in
build_cores, the builder reads m.lanes and NEVER m.map_def (the band
rides build_lanes' public records — no second lane model), it WRITES
nothing on m (mount child only), the kind filter is the literal
"ground" branch with air continuing, and the geometry is PRIMITIVE-
MESH ONLY: no ArrayMesh / surface-array / raw-vertex-array code
survives anywhere in the builder (the retired broken mechanism may not
creep back).

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
    # one segment child per waypoint segment, per ground lane, derived
    # from the map data leg — the probe counts what build_lanes stored.
    with open(MAP_JSON, encoding="utf-8") as fh:
        mmap = json.load(fh)
    segs = {lane["id"]: len(lane["waypoints"]) - 1
            for lane in mmap["lanes"] if lane["kind"] == "ground"}
    bands = [ln for ln in out.splitlines() if ln.startswith("LB-BAND ")]
    assert len(bands) == 3 and {ln.split()[1] for ln in bands} == GROUND, out
    for ln in bands:
        lid = ln.split()[1]
        assert ("segs=%d " % segs[lid]) in ln, out
        assert "mat=1" in ln, out            # pinned material shape
    # WEB-PROOF PROXY rows: engine-managed PlaneMesh/PrimitiveMesh
    # geometry per segment (the G2 ArrayMesh never rasterized in web).
    classes = [ln for ln in out.splitlines()
               if ln.startswith("LB-CLASS ")]
    assert len(classes) == 3 and \
        {ln.split()[1] for ln in classes} == GROUND, out
    for ln in classes:
        assert "mesh=PlaneMesh prim=1" in ln, out
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
    The kind filter is the literal ground branch; air continues. One
    mechanism: one band-container site, one segment site, one add_child
    of the band node onto m."""
    src = read(BANDS_GD)
    mount = _fn_body(src, "static func paint_lane_bands(")
    assert 'if String(lane["kind"]) != "ground":' in mount, mount
    assert "m.map_def" not in src, "band must ride build_lanes, not a " \
        "second lane model off the raw map"
    assert re.search(r'(?<![\w.])m\.[\w.\[\]"]*\s*=[^=]', src) is None, \
        "lane_bands must assign NOTHING onto m (visual-only, zero writes)"
    assert mount.count("m.add_child(") == 1, mount
    assert src.count("Node3D.new()") == 1, \
        "one band node per ground lane, ONE mechanism"
    assert src.count("MeshInstance3D.new()") == 1, \
        "one segment node site, ONE mechanism (segments ride in the band)"


def test_builder_rides_primitive_mesh_geometry_source_truth():
    """THE G2-FIX LEG (MC 11698, source side of the probe's LB-CLASS
    rows): bands rasterize ONLY on engine-managed PrimitiveMesh
    geometry under GL Compatibility — the runtime-ArrayMesh mechanism
    built correct nodes headless yet painted ~6 px in the web export.
    So: PlaneMesh is built, and NONE of the retired mechanism's raw-
    array calls survives in CODE (no ArrayMesh, no
    add_surface_from_arrays, no vertex/index array constants) — the
    broken path may not creep back by copy-paste. Comments are stripped
    first: the builder header must be allowed to NAME the retired
    mechanism to explain the fix (the header is why this file reads
    the way it does); the probe's LB-CLASS rows police actual
    geometry at runtime."""
    code = re.sub(r"#.*", "", read(BANDS_GD))
    assert "PlaneMesh.new()" in code, "segments must ride PlaneMesh"
    assert code.count("PlaneMesh.new()") == 1, "ONE mesh-construction site"
    for retired in ("ArrayMesh", "add_surface_from_arrays",
                    "ARRAY_VERTEX", "ARRAY_INDEX",
                    "PackedVector3Array", "PackedInt32Array"):
        assert retired not in code, \
            "retired web-dead mechanism crept back: %s" % retired


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
