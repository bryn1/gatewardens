"""W3a purity + parse-leg gate (I6 / F2-1 / F14, MC 11274.1.9 / card 11299).

(a) SOURCE: every godot/sim/*.gd is pure sim code — no `extends Node`,
    no Engine references, no get_node, no BARE randf()/randi(): the bare
    regex is the hygiene gate's OWN compiled pattern (BARE_RAND_RE, reused
    via tools/check_hygiene.py import — one mechanism per concern, never
    an inline copy). receiver-qualified rng.randf()/rng.randi() is the
    sanctioned draw path (F2-1) and never a hit.
(b) PARSE LEG: the brief's tests/probe_sim_parse.gd placement is DROPPED
    per its own stated reading — a res:// load cannot reach tests/, and
    the architecture places harness scripts in sim/ (sim_headless /
    save_probe / validate_probe; hollow_dawn's sim_headless is the live
    precedent). godot/sim/sim_parse_probe.gd IS the parse harness and the
    -s leg references THAT: after conftest's ensure_class_cache() run
    `godot --headless --path godot/ -s res://sim/sim_parse_probe.gd` and
    judge the machine rows: one SIMPARSE-OK per sim MODULE (every
    sim_*.gd except the harness itself), a final SIMPARSE-DONE carrying
    that same count, zero SIMPARSE-FAIL, rc 0.
"""

import os
import re
import subprocess
import sys

import pytest

import conftest
from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: BARE_RAND_RE, blank_code)

HARNESS = "sim_parse_probe.gd"
SIM_DIR = repo_path("godot", "sim")
EXPECTED_MODULES = {"sim_tables", "sim_economy", "sim_combat", "sim_wave"}


def sim_files():
    return sorted(f for f in os.listdir(SIM_DIR)
                  if f.startswith("sim_") and f.endswith(".gd"))


def module_basenames():
    return sorted(f[:-len(".gd")] for f in sim_files() if f != HARNESS)


def read(name):
    with open(os.path.join(SIM_DIR, name), encoding="utf-8") as fh:
        return fh.read()


# ---------- (a) source purity, per sim file ----------

def test_sim_dir_carries_the_four_w3a_modules():
    assert set(module_basenames()) >= EXPECTED_MODULES


@pytest.mark.parametrize("name", sim_files())
def test_purity_bans(name):
    code = hyg.blank_code(read(name), "gd")  # comments/strings never mask
    assert not re.search(r"extends\s+Node", code), "%s extends Node" % name
    assert not re.search(r"\bEngine\b", code), "%s references Engine" % name
    assert not re.search(r"get_node", code), "%s calls get_node" % name
    hit = None
    for lineno, line in enumerate(code.split("\n"), 1):
        if hyg.BARE_RAND_RE.search(line):
            hit = (lineno, line.strip())
            break
    assert hit is None, "%s:%d bare randf()/randi() (F2-1): %r" % (
        (name,) + hit)


# ---------- (b) parse leg: -s probe over every sim module ----------

def test_parse_leg_all_modules_parse():
    if not os.path.exists(conftest.GODOT):
        pytest.skip("Godot binary not installed")
    conftest.ensure_class_cache()
    proc = subprocess.run(
        [conftest.GODOT, "--headless", "--path", repo_path("godot"),
         "-s", "res://sim/" + HARNESS],
        capture_output=True, text=True, timeout=300)
    out = proc.stdout
    assert proc.returncode == 0, \
        "parse probe rc=%d\n%s\n%s" % (proc.returncode, out, proc.stderr)
    lines = [l.strip() for l in out.splitlines()]
    assert not any(l.startswith("SIMPARSE-FAIL") for l in lines), out
    oks = sorted(l.split(" ", 1)[1] for l in lines
                 if l.startswith("SIMPARSE-OK "))
    expected = module_basenames()
    assert oks == expected, \
        "SIMPARSE-OK rows %r != sim modules %r" % (oks, expected)
    done = [l for l in lines if l.startswith("SIMPARSE-DONE ")]
    assert len(done) == 1 and done[0] == "SIMPARSE-DONE %d" % len(expected), \
        "final DONE row missing or miscounted: %r" % done
    assert len(expected) >= 4, "parse leg must never pass vacuously"
