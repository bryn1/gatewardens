"""G4 yellow range ring (MC card 11707 / V121-PLAN row G4 + §4, Rev 2).

The contract, per the plan (DA A4.1 binding on the range-0 negative): a
YELLOW ring, flat on the ground, at the ARMED ghost showing that family's
CURRENT tier range, the radius a towers.json TIER-ROW NUMBER (never a
literal). ONE mechanism rides the ghost lifecycle: the placer (which owns
the aim/ghost state, G5) calls _sync_ring from its three ghost
chokepoints — set_ghost/cycle_ghost (SHOW + RESIZE) and cancel_ghost,
which place-confirm, RMB/Escape and the W17e combat-lock all route
through (HIDE). No second driver exists: defense_panel.gd carries ZERO
ring lines — the armed row is OBSERVED off the panel's pinned armed_id
(fx_director observer idiom, read-only), so the G5 caller-set pins
(test_g5_build_confirm's counts) stay byte-green.

GEOMETRY — the G2 ArrayMesh lesson (MC 11698) at the mechanism level:
engine-managed PrimitiveMesh only. The ring is a UNIT TorusMesh (the
class family the G2 fix proved rasterizes under GL Compatibility/web),
the node TRANSFORM carrying the range (scale.x == scale.z == the range
number). After creation only position/scale/visibility ever change. The
CLASS row of the probe is the WEB-PROOF PROXY (LB-CLASS idiom); the
served-browser pixel re-check is the orchestrator's leg.

DECLARED FINDINGS (plan row G4 parenthetical — "declare what you found"):
a real selection mechanism DOES exist in code (defense_panel.selected_uid
+ select_defense, player-reachable through the defense_rows_ui rows since
W17c) — the ring ships GHOST-FIRST, the plan's declared case; the
selected-defense leg is the plan's OWN D4-row P2/P4 backlog (its change
sites live in defense_panel.gd, outside this card's owned paths). The
HIDDEN leg's "no ghost & no selection" still holds as a NEGATIVE.
RANGE-0 (Rev 2 / DA A4.1): the five gate_blockade tier rows carry range
0 — NO ring renders (hidden, not a zero-radius dot).

ENGINE LEG: godot/sim/g4_range_ring_probe.gd (g5_real_relay idiom: real
mission boot, real main.gd forwarder, SYNTHESIZED InputEvents, presses
through the production button signals). Transcript rows re-checked here,
not eyeballed; stderr EMPTY; G4-OK must be the LAST row (completion-flag
guarded — the G2 mid-abort lesson). Planted-red: the tier-index swap
(tiers[tier - 1] -> tiers[tier]) MUST turn the DATA leg RED — proven
live for the transcript (G4-wave.log) and pinned source-side below.
"""

import json
import os
import re
import sys

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg

PROBE = "res://sim/g4_range_ring_probe.gd"
RING_GD = conftest.repo_path("godot", "scripts", "range_ring.gd")
PLACER_GD = conftest.repo_path("godot", "scripts", "defense_placer.gd")
PANEL_GD = conftest.repo_path("godot", "scripts", "defense_panel.gd")
TOWERS_JSON = conftest.repo_path("godot", "data", "towers.json")

FAMILIES = ["ballista", "bombard", "hailspire_tower", "gate_blockade",
            "barbed_snare"]
EPS = 1e-9


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _kv(line):
    return {p.split("=")[0]: p.split("=")[1] for p in line.split()[1:]
            if "=" in p}


# ---------- engine leg: the transcript IS the contract -------------------

def test_g4_ring_engine_probe(tmp_path, class_cache):
    proc = conftest.run_probe_script(PROBE, (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    lines = out.splitlines()
    assert "G4-FAIL" not in out, out
    assert lines[-1] == "G4-OK", \
        "G4-OK must be the LAST transcript row (completion, not rc)"
    kv = {ln.split()[0]: _kv(ln) for ln in lines if ln.startswith("G4-")}

    # HIDDEN negative legs: pre-arm NOTHING renders (node absent counts —
    # it lazy-creates), and after the final cancel nothing renders again.
    assert kv["G4-HIDE0"]["node"] == "0" \
        and kv["G4-HIDE0"]["visible"] == "0", kv["G4-HIDE0"]
    assert kv["G4-HIDE1"]["vis"] == "0" \
        and kv["G4-HIDE1"]["ghost"] == "-1" \
        and kv["G4-HIDE1"]["selected"] == "0", kv["G4-HIDE1"]

    # DATA legs: REAL picker presses, want == scale == the towers.json
    # T1 number (the probe derives want from its OWN tables walk).
    data = [ln for ln in lines if ln.startswith("G4-DATA ")]
    fams = {ln.split()[1] for ln in data}
    assert fams == {"ballista", "bombard", "hailspire_tower",
                    "barbed_snare"}, out
    want = {f: None for f in fams}
    for ln in data:
        r = _kv(ln)
        assert r["vis"] == "1", ln
        assert abs(float(r["want"]) - float(r["scale"])) < 0.01, ln
    # WEB-PROOF PROXY row (the G2 lesson): engine-managed primitive.
    assert kv["G4-CLASS"]["mesh"] == "TorusMesh" \
        and kv["G4-CLASS"]["prim"] == "1" \
        and kv["G4-CLASS"]["mat"] == "1", kv["G4-CLASS"]

    # TIER legs: the ring's radius lookup == JSON at EVERY tier row,
    # every family (BOTH numbers printed by the probe, parsed here).
    tiers = [ln for ln in lines if ln.startswith("G4-TIER ")]
    assert len(tiers) == 25, out          # 5 families x 5 tier rows
    for ln in tiers:
        r = _kv(ln)
        assert abs(float(r["want"]) - float(r["got"])) < 0.01, ln
    assert int(kv["G4-TIERDIFF"]["families"]) >= 1, kv["G4-TIERDIFF"]

    # RANGE-0 (DA A4.1): blockade T1 press renders NO ring WITH THE GHOST
    # ARMED (non-vacuous — the same node printed vis=1 above, and the
    # sweep below repaints it after five range-0 premise rows).
    r0 = kv["G4-R0"]
    assert r0["visible"] == "0" and int(r0["ghost"]) >= 0, r0
    assert kv["G4-R0SWEEP"]["zero_rows"] == "5" \
        and kv["G4-R0SWEEP"]["armed_hidden"] == "1" \
        and kv["G4-R0SWEEP"]["repaint"] == "1", kv["G4-R0SWEEP"]

    # Lifecycle legs: cycle MOVES the ring with the ghost; place, RMB
    # cancel and the combat lock each HIDE it.
    assert kv["G4-CYCLE"]["vis"] == "1" and int(kv["G4-CYCLE"]["fwd"]) >= 0
    assert kv["G4-PLACE"]["placed"] == "1" and kv["G4-PLACE"]["vis"] == "0"
    assert kv["G4-RMB"]["vis"] == "0" and kv["G4-RMB"]["ghost"] == "-1"
    assert kv["G4-LOCK"]["vis"] == "0" and kv["G4-LOCK"]["armed"] == "0"


# ---------- source truth: the ONE mechanism, primitive-only --------------

def _body(code, header):
    parts = code.split(header)
    assert len(parts) > 1, "lost %s" % header
    return parts[1].split("func ")[0]


def test_ring_geometry_primitive_only_source_truth():
    """THE G2 lesson pinned source-side (MC 11698 idiom): the ring rides
    engine-managed TorusMesh geometry and NONE of the retired runtime-
    ArrayMesh mechanism survives — the web-dead path may not creep back
    by copy-paste. Comments are blanked: the header NAMES the retired
    mechanism to explain the fix."""
    code = hyg.blank_code(read(RING_GD), "gd")
    assert "TorusMesh.new()" in code, "the ring must ride TorusMesh"
    assert code.count("TorusMesh.new()") == 1, "ONE mesh-construction site"
    assert code.count("MeshInstance3D.new()") == 1, "ONE ring node site"
    for retired in ("ArrayMesh", "add_surface_from_arrays",
                    "ARRAY_VERTEX", "ARRAY_INDEX",
                    "PackedVector3Array", "PackedInt32Array",
                    "SurfaceTool"):
        assert retired not in code, \
            "retired web-dead mechanism crept back: %s" % retired


def test_placer_ring_lifecycle_source_truth():
    """The single-driver contract: ALL THREE ghost chokepoints call
    _sync_ring, the one site that touches RANGE_RING; the ring files are
    touched nowhere else. _sync_ring's shape: no ghost -> hide, radius
    <= 0 -> hide (the DA A4.1 treatment), else show AT the ghost slot."""
    assert "res://scripts/range_ring.gd" in read(PLACER_GD), \
        "ring preloaded (raw text; blank_code erases strings)"
    src = hyg.blank_code(read(PLACER_GD), "gd")
    for fn in ("func set_ghost(slot: int) -> void:",
               "func cancel_ghost() -> void:",
               "func cycle_ghost(dir: int) -> void:"):
        assert "_sync_ring()" in _body(src, fn), fn
    body = _body(src, "func _sync_ring() -> void:")
    assert "hide_ring" in body and "show_ring" in body, body
    assert src.count("RANGE_RING.show_ring") == 1 \
        and src.count("RANGE_RING.hide_ring") == 1, \
        "ONE show site + ONE hide site — no second driver"
    # the ring driver is _sync_ring alone: no direct RANGE_RING call
    # lives in ANY other function body.
    for fn in ("func set_ghost", "func cancel_ghost", "func cycle_ghost",
               "func place_id", "func place"):
        assert "RANGE_RING." not in _body(src, fn + ""), fn


def test_tier_lookup_pinned_source_truth():
    """The DATA leg's lookup, pinned: 1-BASED tier indexes the JSON tiers
    array AT tiers[tier - 1] (defense_obj.tier_row is the 0-based twin),
    guarded by row presence + range — the number is READ, no range value
    can appear as a literal (I2-governed file)."""
    src = hyg.blank_code(read(PLACER_GD), "gd")
    body = _body(src, "func tier_range(tower_id: String, tier: int)")
    assert "tiers[tier - 1]" in body, body
    assert "tier < 1" in body and "tier > tiers.size()" in body, body
    assert "row_for_id(" in body, "the row door is row_for_id (F4)"
    assert not hyg.literal_violations(read(PLACER_GD)), \
        "defense_placer.gd (governed) grew a non-structural literal"
    assert not hyg.literal_violations(read(PANEL_GD)), \
        "defense_panel.gd (governed) grew a non-structural literal"


def test_panel_carries_zero_ring_lines_source_truth():
    """Owned-paths discipline made executable: the ring needs NO drive
    lines in defense_panel.gd — the armed row is OBSERVED (the panel's
    G5-pinned armed_id, its "armed ⇔ ghost" invariant). The panel's G5
    caller-set counts are additionally re-pinned unchanged."""
    panel = read(PANEL_GD)
    assert "range_ring" not in panel and "RANGE_RING" not in panel \
        and "_sync_ring" not in panel and "RangeRing" not in panel
    assert panel.count("set_ghost(") == 1 \
        and panel.count("cancel_ghost(") == 2 \
        and panel.count("cycle_ghost(") == 1, \
        "the G5 ghost caller-set pins drifted"


# ---------- data leg: the JSON the ring is pinned against -----------------

def test_towers_json_range0_and_tier_variance():
    """The premise rows the probe's legs rest on, re-read from the DATA
    itself: gate_blockade has EXACTLY five tier rows and every one
    carries range 0 (the DA A4.1 negative's input); the other four
    families carry range > 0 at every tier (so a hidden ring there is a
    bug, not the treatment); and >= 1 family has range(T2) != range(T1)
    — the non-vacuity the planted-red tier swap depends on."""
    with open(TOWERS_JSON, encoding="utf-8") as fh:
        rows = json.load(fh)
    by_id = {r["id"]: r for r in rows}
    assert set(by_id) == set(FAMILIES), set(by_id)
    block = by_id["gate_blockade"]["tiers"]
    assert len(block) == 5, len(block)
    assert all(float(t["range"]) == 0.0 for t in block), block
    variance = 0
    for fam in FAMILIES:
        tiers = by_id[fam]["tiers"]
        assert len(tiers) == 5, fam
        ranges = [float(t["range"]) for t in tiers]
        if fam == "gate_blockade":
            continue
        assert all(r > 0.0 for r in ranges), (fam, ranges)
        if abs(ranges[1] - ranges[0]) > EPS:
            variance += 1
    assert variance >= 1, "planted-red would be vacuous"


# ---------- planted-red: the pinned lookup proves it can fail ------------

def _lookup_violations(code):
    """The source-gate over the tier lookup (the DATA leg's RED target)."""
    bad = []
    try:
        body = _body(code, "func tier_range(tower_id: String, tier: int)")
    except AssertionError:
        return ["tier_range is gone"]
    if "tiers[tier - 1]" not in body:
        bad.append("the tier lookup left tiers[tier - 1] (1-based T1..T5)")
    return bad


def test_planted_red_tier_swap_goes_red():
    """Swap the tier index lookup (tiers[tier - 1] -> tiers[tier]): the
    gate MUST report the violation (the live probe transcript for this
    exact plant rides G4-wave.log: G4-DATA ballista want=16.0 scale=17.0
    -> G4-FAIL, rc=1)."""
    code = read(PLACER_GD)
    assert not _lookup_violations(code), "GREEN premise broken"
    planted = code.replace("tiers[tier - 1] as Dictionary",
                           "tiers[tier] as Dictionary")
    assert planted != code, "planted-red: the lookup string drifted"
    assert _lookup_violations(planted), \
        "planted-red: a tier-index swap slipped the source gate"
