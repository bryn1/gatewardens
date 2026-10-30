"""G3 build-phase wave telegraph (MC card 11696 / V121-PLAN G3).

The telegraph contract, per the plan: during the BUILD phase a small
billboard preview of the UPCOMING wave rides each spawner that the wave
carries — the enemy's OWN sheet icon (ids already in sprite_bank) + one
world_text count, grouped by lane -> spawner through the RAW map_def
lane rows; CLEARED on the combat edge; re-shown next build phase with
UPDATED counts. One mechanism: the fx_director OBSERVER idiom — new
wave_telegraph.gd as a mission.tscn scene child (the FxDirector
precedent), own _process diffing the public fields (m.wave / phase_kind
/ waves_file / map_def), ZERO writes to sim state.

ENGINE LEG (EMPTY stderr, W4 ruling): the shipped kit
godot/sim/g3_wave_telegraph_probe.gd boots the REAL mission and drives
mission.step + telegraph_step in lockstep (E5) across the REAL phase
edges. Rows re-checked here against EXPECTATIONS RE-DERIVED FROM THE
DATA FILES (waves_gatefall_normal.json x gatefall.json) — no count
literal in this file: wave-0 build (pre-first-spawn ENT row), the
combat-edge CLEAR, the alive-COMBAT negative leg (markers GONE while
entities walk), the wave-1 build UPDATE leg (counts == wave row 1,
spawn_b absent as the per-row negative), and the wave-2 ground/air leg
(air entry above the ground entry at the same gate).

SOURCE-TRUTH LEGS: zero mutator calls / zero state writes in
wave_telegraph.gd (the fx doctrine, test_hud/test_damage families);
the ONE wave read (SIM_WAVE.wave_comp — the same public read
mission.start_wave drives), the ONE sprite factory and the DECLARED
world-text factory (no hand-rolled Sprite3D/Label3D). DATA LEG: every
enemy_id in EVERY wave row (both difficulties) has a TEXTURES sheet —
the preview never silently drops a shipped carrier. MOUNT LEG:
mission.tscn carries the WaveTelegraph node on an ext row whose uid ==
its .uid sidecar (the export-poison ban test_mission_clicks extends),
and the load_steps header counts every resource.
"""

import json
import os
import re
from pathlib import Path

import conftest
from conftest import repo_path

import sys
sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for code greps)

PROBE = "res://sim/g3_wave_telegraph_probe.gd"
GODOT = repo_path("godot")
TELE_GD = repo_path("godot", "scripts", "wave_telegraph.gd")
TSCN = repo_path("godot", "scenes", "mission.tscn")
MAP_JSON = repo_path("godot", "data", "maps", "gatefall.json")
BANK_GD = repo_path("godot", "scripts", "sprite_bank.gd")
WAVES_JSON = {d: repo_path("godot", "data", "waves",
                           "waves_gatefall_%s.json" % d)
              for d in ("normal", "hard")}

# The shipped mutator families + direct-write shapes — families per the
# test_hud.py home (kept local per this repo's one-module-per-contract
# test style, no cross-test imports anywhere in tests/).
MUT_RE = re.compile(r"\b(?:add_|spend_|consume_|set_|equip|place_)\w*\s*\(")
PLUMBING = {"add_child"}
WRITE_RE = re.compile(
    r"\b(?:m|mission|state|game_state)\.[A-Za-z_]\w*"
    r"(?:\[[^\]]*\])?\s*(?:[+\-*/]?=[^=])")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def expected_entries(wave_idx, difficulty="normal"):
    """Re-derive the telegraph contract FROM DATA (no literals):
    (spawner, enemy_id, kind) -> summed count for one wave row, grouped
    lane -> spawner through the raw map lane rows — the reads the
    mechanism names, restated here independently."""
    waves = _json(WAVES_JSON[difficulty])["waves"][wave_idx]["enemies"]
    lanes = {l["id"]: l for l in _json(MAP_JSON)["lanes"]}
    groups = {}
    for r in waves:
        lane = lanes[r["lane"]]
        key = (lane["spawner"], r["enemy_id"], lane["kind"])
        groups[key] = groups.get(key, 0) + r["count"]
    return groups


def _marks(out, tag):
    """tag-MARK lines -> {(spawner,id,kind): (count, y)}."""
    marks = {}
    for ln in out.splitlines():
        if not ln.startswith("G3T-%s-MARK " % tag):
            continue
        kv = dict(x.split("=", 1) for x in ln.split(" ")[1:])
        marks[(kv["spawner"], kv["id"], kv["kind"])] = (
            int(kv["count"]), float(kv["y"]))
    return marks


def _check_marks(out, tag, wave_idx):
    want = {(s, e, k): c for (s, e, k), c in
            expected_entries(wave_idx).items()}
    got = {k: v[0] for k, v in _marks(out, tag).items()}
    assert got == want, "%s telegraph %r != wave %d rows %r\n%s" % (
        tag, got, wave_idx, want, out)


def test_wave_telegraph_engine_probe(tmp_path, class_cache):
    proc = conftest.run_probe_script(PROBE, (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "G3T-FAIL" not in out, out
    assert out.rstrip().endswith("G3T-OK"), out

    # MOUNT: the scene ships it, on the pinned script.
    assert "G3T-MOUNT script=res://scripts/wave_telegraph.gd" \
        in out.splitlines(), out

    # build-w0: PRE-FIRST-SPAWN leg + per-spawner counts == wave row 0.
    assert "G3T-W0-ENT n=0" in out.splitlines(), out
    _check_marks(out, "W0", 0)

    # combat edge: markers GONE...
    assert "G3T-CLEAR children=0 entries=0" in out.splitlines(), out
    # ...and STAY gone while entities walk (NEG — a clear that only
    # rides an empty frame passes the line above alone; fleet
    # negative-leg rule; the planted-red target row).
    neg = [ln for ln in out.splitlines() if ln.startswith("G3T-NEG ")]
    assert len(neg) == 1, out
    kv = dict(x.split("=", 1) for x in neg[0].split(" ")[1:])
    assert int(kv["alive"]) > 0 and int(kv["markers"]) == 0, neg

    # wave-1 build: UPDATED counts == wave row 1, spawn_b absent (the
    # row carries no spawn_b lane — the per-spawner negative).
    _check_marks(out, "W1", 1)
    assert {k[0] for k in _marks(out, "W1")} == {"spawn_a", "spawn_c"}, out
    assert "G3T-W1-NEG spawn_b=0" in out.splitlines(), out

    # wave-2 build: the air group rides ABOVE the ground group at the
    # same gate (the ground/air distinction, lane data at lane spawn y).
    _check_marks(out, "W2", 2)
    w2 = _marks(out, "W2")
    air_y = [y for (s, _e, k), (_c, y) in w2.items()
             if s == "spawn_a" and k == "air"]
    ground_y = [y for (s, _e, k), (_c, y) in w2.items()
                if s == "spawn_a" and k == "ground"]
    assert len(air_y) == 1 and len(ground_y) == 1, out
    assert air_y[0] > ground_y[0], out
    assert "G3T-AIR spawn_a" in out and "above=1" in out, out


def test_wave_telegraph_zero_writes_source_truth():
    """The fx_director header doctrine extends here: the observer calls
    NO shipped mutator and writes NO injected state (families per
    test_hud.py); its only children are its own billboards."""
    code = hyg.blank_code(read(TELE_GD), "gd")
    muts = [mm.group(0).rstrip("(").strip()
            for mm in MUT_RE.finditer(code)
            if mm.group(0).rstrip("(").strip() not in PLUMBING]
    assert muts == [], "wave_telegraph calls a shipped mutator: %s" % muts
    writes = [mm.group(0) for mm in WRITE_RE.finditer(code)]
    assert writes == [], "wave_telegraph writes injected state: %s" % writes


def test_wave_telegraph_one_mechanism_source_truth():
    """ONE wave read (SIM_WAVE.wave_comp — the public read
    mission.start_wave drives, cited in the header; no raw
    waves_file[...] indexing), ONE sprite factory (make_sprite, no
    hand-rolled Sprite3D), the DECLARED world-text factory (no raw
    Label3D — world_text owns that mechanism, test_damage_numbers
    walks the tree for exactly this)."""
    code = hyg.blank_code(read(TELE_GD), "gd")
    assert code.count("SIM_WAVE.wave_comp(") == 1, code
    assert "m.waves_file[" not in code and "waves_file[\"" not in code, \
        "telegraph must ride the public wave read, not raw indexing"
    assert code.count("SPRITE_BANK.make_sprite(") == 1, code
    assert "Sprite3D.new()" not in code, "billboards come from the bank"
    assert code.count("WORLD_TEXT.make_text(") == 1, code
    assert "Label3D" not in code, "world_text owns the world-text mechanism"


def test_every_previewed_enemy_is_on_the_bank():
    """DATA leg: every enemy_id in EVERY wave row of BOTH difficulties
    resolves in THE ONE sprite_bank TEXTURES map — a telegraphed carrier
    never silently drops to the null guard on shipped data."""
    bank = read(BANK_GD)
    textures = bank[bank.index("const TEXTURES"):
                    bank.index("const TIER_TEXTURES")]
    ids = set(re.findall(r'"([a-z_]+)":\s*preload\(', textures))
    for path in WAVES_JSON.values():
        for wrow in _json(path)["waves"]:
            for erow in wrow["enemies"]:
                assert erow["enemy_id"] in ids, \
                    "%s has no TEXTURES sheet — the preview would drop it" \
                    % erow["enemy_id"]


def test_mission_tscn_mounts_the_telegraph_append_only():
    """The mount rides the scene (FxDirector precedent): the ext row's
    uid == its .uid sidecar byte-for-byte (the export-poison ban), the
    node is a scene child on that ext id, and the load_steps header
    counts every resource (a stale header is the Godot WARNING that
    would pollute every EMPTY-stderr gate)."""
    tscn = read(TSCN)
    m = re.search(r'\[ext_resource type="Script" uid="(uid://[a-z0-9]+)"'
                  r' path="res://scripts/wave_telegraph\.gd" id="([^"]+)"',
                  tscn)
    assert m, "mission.tscn carries no wave_telegraph ext row"
    uid, ext_id = m.group(1), m.group(2)
    sidecar = Path(GODOT) / "scripts" / "wave_telegraph.gd.uid"
    assert sidecar.read_text(encoding="utf-8").strip() == uid, \
        "tscn uid %s != sidecar — the export ERROR source" % uid
    assert '[node name="WaveTelegraph" type="Node3D" parent="."]' in tscn
    assert 'script = ExtResource("%s")' % ext_id in tscn.split(
        '[node name="WaveTelegraph"')[1], "node not on the ext row"
    steps = int(re.search(r"\[gd_scene load_steps=(\d+)", tscn).group(1))
    n_res = tscn.count("[ext_resource ") + tscn.count("[sub_resource ")
    assert steps == n_res + 1, \
        "load_steps %d stale: %d ext + %d sub + 1" % (
            steps, tscn.count("[ext_resource "),
            tscn.count("[sub_resource "))


def _combat_edge_clears(text):
    """Source-truth detector: telegraph_step's non-build branch carries
    the _clear() call — the combat edge is THE clear site (plan G3,
    'cleared at wave start on the existing phase_changed("combat")
    edge', detected as its observable effect per the header)."""
    edge = text[text.index('if phase != "build":'):text.index("_paint(m, w)")]
    return "_clear()" in edge


def test_planted_red_clear_removed_goes_red():
    """The fleet gate rule — a check that never went red is not a
    check — as a STANDING leg: with the combat-edge _clear() call
    removed (the planted regression), the detector goes RED on exactly
    that shape (the engine-side RED transcript for the same plant rides
    G3-wave.log beside the green probe run)."""
    src = read(TELE_GD)
    assert _combat_edge_clears(src), "real mechanism must clear on combat"
    clear_line = "\t\t_clear()               # the combat edge"
    assert src.count(clear_line) == 1, \
        "the single clear-on-combat site moved — retarget this leg"
    planted = src.replace(clear_line, "\t\tpass  # PLANTED: clear removed", 1)
    assert not _combat_edge_clears(planted), \
        "planted-red: removed combat clear slipped the detector"
