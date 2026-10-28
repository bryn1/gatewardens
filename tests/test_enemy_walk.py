"""v1.2 F5 procedural enemy walk — pose math (MC card 11610 / W12-PLAN F5).

SOURCE-TRUTH idiom (test_heroes precedent, one idiom per repo): pytest
cannot execute GDScript, so the pure legs parse the constants out of
godot/scripts/enemy_anim.gd and mirror its three static funcs in Python
(the formulas are abs(sin(phase))*amp / sin(phase)*amp / fmod — the
mirror is the same math to the bit for the asserted properties). The
ENGINE leg the plan names (step N frames -> node y oscillates while
every ent["pos"] equals the no-anim run) rode the throwaway probe of
the card's VISUAL-VERIFICATION row — transcript in the F5 wave log —
and the shipped-kit smoke (v1_world_probe UNCHANGED) re-ran rc=0.

REUSE CHECK (second-mechanism law, wave log row): fx_director.gd and
ui_tween.gd grepped for bob/scale/sine motion helpers FIRST — fx_director
is tracer/spark/poof LIFETIMES (its only motion is the tracer chord
lerp; no sine/bob/velocity helper exists), ui_tween is Control-panel
create_tween motion (an engine Tween, unusable for a per-tick visual
offset on Node3D billboards). Neither fits; enemy_anim.gd is that ONE
new mechanism, mounted by ONE call line.

Legs: (1) zero distance -> neutral pose exactly 0.0; (2) phase
advances monotonically with distance and stays wrapped in [0, TAU);
(3) amplitude BOUNDED — the cycle peak equals the declared BOB_AMP and
BOB_AMP sits inside the plan's honest +-1-2 px band (this is the
planted-red target: BOB_AMP -> 0 trips the band leg); (4) the golden
proxy in source truth — enemy_anim NEVER names ent["pos"], step() keeps
its ONE ent["pos"] write, the mount is ONE call line, and the
I2-governed runner gained ZERO literals (check_hygiene.literal_violations
is the gate's own function, reused).
"""

import math
import re
import sys

from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: the gate's own scans)


def read_gd(*parts):
    with open(repo_path(*parts), encoding="utf-8") as fh:
        return fh.read()


ANIM_RAW = read_gd("godot", "scripts", "enemy_anim.gd")
RUNNER_RAW = read_gd("godot", "scripts", "enemy_runner.gd")


def const(name):
    m = re.search(r"^const %s := ([0-9.]+)" % name, ANIM_RAW, re.M)
    assert m, "constant %s missing from enemy_anim.gd" % name
    return float(m.group(1))


PHASE_PER_UNIT = const("PHASE_PER_UNIT")   # rad per world unit walked
BOB_AMP = const("BOB_AMP")                 # world units, +y
SWAY_AMP = const("SWAY_AMP")               # radians, roll about Z


# ---- the mirror of the three static funcs (values parsed above) ----

def phase_advance(prev, distance):
    return math.fmod(prev + abs(distance) * PHASE_PER_UNIT, math.tau)


def bob_offset(phase):
    return abs(math.sin(phase)) * BOB_AMP


def sway_offset(phase):
    return math.sin(phase) * SWAY_AMP


# ---------- 1. zero distance -> neutral pose (EXACT, no epsilon) ----------

def test_zero_distance_walk_holds_the_neutral_pose_exactly_zero():
    # A fresh node sits at phase 0; a zero-speed (zero-distance) step
    # must leave it there, and the neutral pose is exactly on the sim
    # pos — no epsilon: the pre-F5 tree painted this same identity.
    assert PHASE_PER_UNIT > 0.0 and BOB_AMP > 0.0 and SWAY_AMP > 0.0
    p = phase_advance(0.0, 0.0)
    assert p == 0.0
    assert bob_offset(p) == 0.0
    assert sway_offset(p) == 0.0
    # mid-cycle too: walking 0 never re-poses (phase unchanged)
    assert phase_advance(1.234, 0.0) == 1.234
    # and negative distance can never walk the phase backwards (absf)
    assert phase_advance(1.0, -0.5) == phase_advance(1.0, 0.5)


# ---------- 2. phase advances monotonically with distance ----------

def test_phase_advances_monotonically_with_distance():
    # strictly increasing within a cycle, at every step > 0
    p = 0.0
    for _ in range(8):
        q = phase_advance(p, 0.05)
        assert q > p, "phase must advance with every positive step"
        p = q
    # a bigger distance advances by exactly its extra phase (mod TAU)
    assert abs((phase_advance(0.3, 0.4) - phase_advance(0.3, 0.1))
               - PHASE_PER_UNIT * 0.3) < 1e-12
    # wrapped forever: any accumulation stays inside [0, TAU)
    p = 0.0
    for k in range(500):
        p = phase_advance(p, 0.37)
        assert 0.0 <= p < math.tau, "phase escaped the wrap at step %d" % k


# ---------- 3. amplitude bounded: peak == BOB_AMP, in the declared band ----------

def test_bob_amplitude_bounded_and_declared_band_holds():
    # dense sample over one full cycle: |sin| peak == the declared amp,
    # nothing exceeds it (the pose is amplitude-BOUNDED by construction)
    peak = max(bob_offset(k * math.tau / 2048.0) for k in range(2049))
    assert abs(peak - BOB_AMP) < 1e-12, "cycle peak must equal BOB_AMP"
    assert all(abs(bob_offset(k * math.tau / 64.0)) <= BOB_AMP
               for k in range(65))
    assert all(abs(sway_offset(k)) <= SWAY_AMP + 1e-12 for k in range(65))
    # the plan's honest-limitation band: ~13 px character at the shipped
    # camera => +-1-2 px of bob => 0.15 u ~ the declared 0.23 u; a
    # planted BOB_AMP=0 (the card's planted-red) goes RED right here.
    assert 0.10 <= BOB_AMP <= 0.35, \
        "bob amplitude left the plan's +-1-2 px limitation band"


# ---------- 4. the golden proxy, in source truth ----------

def test_enemy_anim_never_writes_ent_pos():
    # the mechanism the goldens trust: ent["pos"] is the sim truth and
    # this file may only NAME it in comments — no code reference, no
    # write. Line-wise comment scan: every mention sits right of a '#'.
    assert re.search(r"ent\[\s*[\"']pos[\"']\s*\]\s*(=|\+=|-=)",
                     ANIM_RAW) is None
    for line in ANIM_RAW.splitlines():
        if "ent[\"pos\"]" in line:
            h = line.find("#")
            assert h != -1 and h < line.find("ent[\"pos\"]"), \
                "ent[\"pos\"] leaked into code, not comment: %s" % line
    # and it holds no entity record at all (no ent[...] anywhere)
    assert "ent[" not in hyg.blank_code(ANIM_RAW, "gd")


def test_step_keeps_its_one_sim_pos_write_and_one_anim_call():
    # raw scan: blank_code blanks the quoted KEY string too (VERIFIED
    # this card), so the pin runs on the file itself
    assert RUNNER_RAW.count("ent[\"pos\"] =") == 1, \
        "step() must keep exactly ONE ent[\"pos\"] assignment"
    assert RUNNER_RAW.count("ENEMY_ANIM.walk_step(") == 1, \
        "the mount is exactly ONE call line"


def test_runner_gained_zero_literals_i2():
    # the gate's own rule function, called on the mounted file: the F5
    # change must not have introduced a single structural number
    # literal into the I2-governed runner
    assert hyg.literal_violations(RUNNER_RAW) == []
