"""G1 spawn-gate eye billboards (MC card 11690 / V121-PLAN G1).

The gate marker contract, per the plan: an original eye billboard rides
EVERY spawner position of the map, the WINGED variant marks the gates
that carry an air lane (on gatefall: spawn_a + spawn_b carry lane_a1/a2
— the plan's declared reading), the ground-only gate spawn_c stays
plain. One mechanism: sprite_bank.make_sprite billboards mounted from
mission_world.build_cores (the paint_arena visual-hook precedent);
mission.gd adds ZERO lines (it sits at the 400-line ceiling).

ENGINE LEG: the shipped kit godot/sim/g1_gate_eye_probe.gd (boot idiom
= v1_world_probe) asserts exactly 3 markers at the map positions, the
billboard flag, and the pinned winged set with the spawn_c NEGATIVE row
(a "winged on a,b" pin alone passes with an inverted filter — fleet
negative-leg rule). Transcript rows re-checked here, not eyeballed.

SOURCE-TRUTH LEGS (pytest cannot exec GDScript — the test_heroes/
test_enemy_walk idiom parses the .gd text): both ids ride the ONE
sprite_bank TEXTURES map (no second render path), the mount is exactly
ONE call inside build_cores (paint_arena precedent), and the marker
body uses make_sprite — mission_world never hand-rolls a Sprite3D.

DATA LEG: gatefall.json itself is re-read — exactly 3 spawners and the
air-lane carrier set is EXACTLY {spawn_a, spawn_b}: that is the map
data the probe's pinned winged set and the mechanism's derivation both
rest on.
"""

import json
import re

import conftest
from conftest import repo_path

PROBE = "res://sim/g1_gate_eye_probe.gd"
BANK_GD = repo_path("godot", "scripts", "sprite_bank.gd")
WORLD_GD = repo_path("godot", "scripts", "mission_world.gd")
MAP_JSON = repo_path("godot", "data", "maps", "gatefall.json")

EYE_PATH = "res://assets/v11/icon_gate_eye.png"
EYE_AIR_PATH = "res://assets/v11/icon_gate_eye_air.png"
WINGED = {"spawn_a", "spawn_b"}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def test_gate_eye_engine_probe(tmp_path, class_cache):
    proc = conftest.run_probe_script(PROBE, (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "G1E-FAIL" not in out, out
    assert "G1E-OK" in out.splitlines(), out
    assert "G1E-EYES n=3" in out, out
    marks = [ln for ln in out.splitlines() if ln.startswith("G1E-MARK")]
    assert len(marks) == 3, out
    winged_seen = {ln.split()[1] for ln in marks
                   if EYE_AIR_PATH in ln}
    plain_seen = {ln.split()[1] for ln in marks if EYE_PATH + " " in ln
                  or ln.endswith(EYE_PATH)}
    assert winged_seen == WINGED, out
    assert "G1E-WING want=spawn_a,spawn_b got=spawn_a,spawn_b" in out, out
    # NEGATIVE leg: spawn_c plain, never winged.
    assert "G1E-NEG spawn_c plain=1 air=0" in out.splitlines(), out
    assert "spawn_c" not in winged_seen and "spawn_c" in plain_seen, out


def test_bank_ids_on_the_one_textures_map_source_truth():
    """Both ids join THE ONE id->file map (no second preload path, no
    parallel marker system) and point at the committed sheets."""
    bank = read(BANK_GD)
    textures = bank[bank.index("const TEXTURES"):bank.index("const TIER_TEXTURES")]
    for id_, path in (("icon_gate_eye", EYE_PATH),
                      ("icon_gate_eye_air", EYE_AIR_PATH)):
        m = re.search(r'"%s":\s*preload\("([^"]+)"\)' % id_, textures)
        assert m, "id %s missing from sprite_bank TEXTURES" % id_
        assert m.group(1) == path, \
            "id %s maps to %s, not the committed sheet" % (id_, m.group(1))


def _fn_body(text, header):
    start = text.index(header)
    rest = text[start + len(header):]
    end = rest.find("\nstatic func ")
    return rest if end < 0 else rest[:end]


def test_mount_one_call_in_build_cores_source_truth():
    """The mount is exactly ONE call in the build_cores visual hook (the
    paint_arena precedent — mission.gd at its 400-line ceiling adds
    ZERO lines) and the body rides make_sprite, never a hand-rolled
    Sprite3D — one mechanism, no second render path."""
    world = read(WORLD_GD)
    cores = _fn_body(world, "static func build_cores(")
    assert cores.count("paint_spawn_gates(") == 1, cores
    assert "paint_arena(m)" in cores, cores   # the hook home is unchanged
    body = _fn_body(world, "static func paint_spawn_gates(")
    assert body.count("SPRITE_BANK.make_sprite(") == 1, body
    assert "Sprite3D.new()" not in body, "marker must not hand-roll a sprite"
    assert world.count("static func paint_spawn_gates(") == 1, \
        "exactly one definition"


def test_gatefall_air_carriers_are_exactly_spawn_a_b():
    """DATA leg: the mechanism derives WINGED from the raw lane rows'
    spawner key; the probe pins the answer. Both rest on this map
    contract: 3 spawner rows, and the air lanes' carriers are exactly
    {spawn_a, spawn_b} (spawn_c ground-only)."""
    with open(MAP_JSON, encoding="utf-8") as fh:
        mmap = json.load(fh)
    assert len(mmap["spawners"]) == 3, mmap["spawners"].keys()
    carriers = {lane["spawner"] for lane in mmap["lanes"]
                if lane["kind"] == "air"}
    assert carriers == WINGED, carriers
    ground = {lane["spawner"] for lane in mmap["lanes"]
              if lane["kind"] == "ground"}
    assert "spawn_c" in ground and "spawn_c" not in carriers, \
        "declared reading: spawn_c is ground-only, plain eye"
