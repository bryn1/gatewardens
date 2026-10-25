"""W6 mission-scene smoke + funnel source-truth gate (MC 11274.1.13 /
card 11308).

(a) ENGINE SMOKE: godot/sim/mission_smoke.gd under `-s` over a temp
    user:// (XDG_DATA_HOME, the save_probe idiom) whose 3-hero deck is
    seeded through the real C13 wiring: rc 0, MISSION-SMOKE-OK in
    stdout, and EMPTY stderr (W4/W5 ruling: the -s verdict is stderr —
    a broken script can still load as a non-null resource).
(b) FUNNEL SOURCE TRUTH (C12): the step(delta) body of mission.gd
    contains the six pinned calls IN ORDER — phase_controller.step,
    heroes, defenses, enemies, bookkeeping, loot — and _process(d)
    calls step(d) and nothing else. Shipped planted-red: the same
    matcher over an in-memory copy whose (3)/(4) lines are swapped MUST
    report red — the gate proves it can fail without touching the file.
"""

import re

import conftest

SMOKE = "res://sim/mission_smoke.gd"
MISSION_GD = conftest.repo_path("godot", "scripts", "mission.gd")

# The six pinned C12 calls (1)..(6), verbatim call forms, in order.
FUNNEL = [
    r"\$PhaseController\.step\(",
    r"step_hero\(",
    r"step_defenses\(",
    r"step_enemies\(",
    r"step_bookkeeping\(",
    r"step_loot\(",
]


def read_mission():
    with open(MISSION_GD, encoding="utf-8") as fh:
        return fh.read()


def step_body(text):
    m = re.search(r"func step\(delta: float\) -> void:\n(.*?)(?=\nfunc )",
                  text, re.S)
    assert m, "mission.gd exposes no func step(delta: float) -> void:"
    return m.group(1)


def funnel_ok(body):
    tail = body
    for pat in FUNNEL:
        m = re.search(pat, tail)
        if m is None:
            return False
        tail = tail[m.end():]
    return True


# ---------- (b) source truth, no engine ----------

def test_step_funnel_is_the_six_pinned_calls_in_order():
    assert funnel_ok(step_body(read_mission())), \
        "step(delta) must call phase -> heroes -> defenses -> enemies -> " \
        "bookkeeping -> loot in the pinned C12 order"


def test_process_calls_step_and_nothing_else():
    m = re.search(r"func _process\(d: float\) -> void:\n\t(.*)\n",
                  read_mission())
    assert m is not None, "_process(d) missing or not one line"
    assert m.group(1).strip() == "step(d)", \
        "C12: _process(d) is step(d) and NOTHING else, got %r" % m.group(1)


def test_planted_red_funnel_swap_goes_red():
    # Fixture trick (nothing written to disk): swap the (3) defenses and
    # (4) enemies call lines; the SAME matcher must reject the result.
    body = step_body(read_mission())
    i3, i4 = body.index("step_defenses("), body.index("step_enemies(")
    j3, j4 = body.index("\n", i3), body.index("\n", i4)
    line3, line4 = body[i3:j3], body[i4:j4]
    planted = body[:i3] + line4 + body[j3:i4] + line3 + body[j4:]
    assert not funnel_ok(planted), \
        "planted-red: matcher stayed GREEN on a swapped funnel — dead gate"


# ---------- (a) engine smoke leg ----------

def test_mission_smoke_engine_leg(tmp_path, class_cache):
    proc = conftest.run_probe_script(SMOKE, (), tmp_path)
    assert proc.returncode == 0, \
        "smoke rc=%d\nOUT:%s\nERR:%s" % (
            proc.returncode, proc.stdout, proc.stderr)
    assert "MISSION-SMOKE-OK" in proc.stdout, proc.stdout
    assert proc.stderr == "", \
        "-s smoke stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
