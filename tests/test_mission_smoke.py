"""W6 mission-scene smoke + funnel source-truth gate, W7 hero extension
(MC 11274.1.13 / card 11308; MC 11274.1.14 / card 11321).

(a) ENGINE SMOKE: godot/sim/mission_smoke.gd under `-s` over a temp
    user:// (XDG_DATA_HOME, the save_probe idiom) whose 3-hero deck is
    seeded through the real C13 wiring: rc 0, MISSION-SMOKE-OK in
    stdout, and EMPTY stderr (W4/W5 ruling: the -s verdict is stderr —
    a broken script can still load as a non-null resource). The W7 legs
    (hero primary KILL, ability ABILITY spend/cooldown gate, F2/F1
    pawn-swap + blue clamp F1SWAP, all-down with pawns DOWN) are parsed
    as machine rows; their numbers are re-derived from the shipped data
    files (heroes.json/enemies.json), never from literals here.
(b) FUNNEL SOURCE TRUTH (C12): the step(delta) body of mission.gd
    contains the six pinned calls IN ORDER — phase_controller.step,
    heroes, defenses, enemies, bookkeeping, loot — and _process(d)
    calls step(d) and nothing else. Shipped planted-red: the same
    matcher over an in-memory copy whose (3)/(4) lines are swapped MUST
    report red — the gate proves it can fail without touching the file.
(c) W7 CROSSINGS (C2/C4, source truth): hero_combat resolves every hit
    through SimCombat.hero_hit / ability_ready with the rng passed to
    the draw, the cooldown array gate sits BEFORE the blue gate, and
    hero_controller reads bridge + balance.feel with no physics-server
    calls. Shipped planted-red on the gate matcher.
"""

import json
import re
import sys

import conftest
from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code, comment blanking)

SMOKE = "res://sim/mission_smoke.gd"
MISSION_GD = conftest.repo_path("godot", "scripts", "mission.gd")
COMBAT_GD = conftest.repo_path("godot", "scripts", "hero_combat.gd")
CTRL_GD = conftest.repo_path("godot", "scripts", "hero_controller.gd")
HEROES_JSON = conftest.repo_path("godot", "data", "heroes.json")

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
    _w7_rows(proc.stdout)


def _hero_row(hero_id):
    with open(HEROES_JSON, encoding="utf-8") as fh:
        for h in json.load(fh):
            if h["id"] == hero_id:
                return h
    raise AssertionError("hero %s missing from heroes.json" % hero_id)


def _row(stdout, tag):
    hits = [line for line in stdout.splitlines() if line.startswith(tag + " ")]
    assert len(hits) == 1, "%s row count=%d\n%s" % (tag, len(hits), stdout)
    return dict(kv.split("=", 1) for kv in hits[0].split(" ")[1:])


def _w7_rows(out):
    """W7 machine rows, numbers re-derived from the shipped data files."""
    warden = _hero_row("warden")
    deadeye = _hero_row("deadeye")
    # (a) hero primary attack killed a wave-0 enemy (seed 11274 pinned).
    kill = _row(out, "MISSION-SMOKE-KILL")
    assert kill["wave"] == "0" and int(kill["loot"]) >= 1, kill
    # (b) ability dispatch spent EXACTLY the data cost and the second
    #     cast was cooldown-gated (gated=1 row flag; engine asserted the
    #     exact float arithmetic — this leg binds cost to the DATA).
    ability = _row(out, "MISSION-SMOKE-ABILITY")
    data_cost = float(warden["abilities"][3]["mana_cost"])
    assert float(ability["cost"]) == data_cost, ability
    assert ability["gated"] == "1", ability
    assert abs(float(ability["blue"])
               - (float(warden["base"]["blue_max"]) - data_cost)) < 1.0, \
        "blue after spend must sit at cap-cost: %s" % ability
    # (d) hot-swap F2/F1: the C4 blue swap clamp bit exactly at the new
    #     hero's cap, and the ACTIVE hero after F1 is warden again.
    swap = _row(out, "MISSION-SMOKE-F1SWAP")
    assert swap["hero"] == "warden", swap
    assert float(swap["swap_blue"]) == float(deadeye["base"]["blue_max"]), \
        "swap clamp must land exactly on the new hero's blue_max: %s" % swap
    # (c) all-down path ran with the pawn rig live: deck-sized pawns,
    #     none visible while every hero stands at 0 HP.
    down = _row(out, "MISSION-SMOKE-DOWN")
    assert int(down["pawns"]) == 3 and int(down["visible"]) == 0, down


# ---------- (c) W7 crossings, source truth, no engine ----------

def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def combat_gate_ok(text):
    """The pinned C4/C2 crossings in hero_combat, IN ORDER: cooldown
    array gate, then SimCombat.ability_ready, then the blue write, then
    the SimCombat.hero_hit resolution drawing through the passed rng."""
    tail = text
    for pat in [
        r"if float\(cds\[i\]\) > 0\.0:",
        r"SIM_COMBAT\.ability_ready\(",
        r"mission\.blue = float\(mission\.blue\) - cost",
        r"SIM_COMBAT\.hero_hit\(",
        r"mission\.rng\.randf\(\)",
    ]:
        m = re.search(pat, tail)
        if m is None:
            return False
        tail = tail[m.end():]
    return True


def test_hero_combat_pins_the_c2_c4_crossings():
    assert combat_gate_ok(read_text(COMBAT_GD)), \
        "hero_combat must gate on the C4 cooldown array, then " \
        "SimCombat.ability_ready, write the mission-local blue spend, " \
        "and resolve damage through SimCombat.hero_hit with the rng's " \
        "own randf() draw (C2/C4/F2-1)"


def test_hero_combat_planted_red_gate_removal_goes_red():
    # Fixture trick (nothing written to disk): drop the cooldown-gate
    # line; the SAME matcher must reject the result (the live disabled-
    # gate RED run is recorded in W7-evidence.md).
    text = read_text(COMBAT_GD)
    line = re.search(r"\n\tif float\(cds\[i\]\) > 0\.0:\n\t\treturn[^\n]*\n",
                     text)
    assert line is not None, "cooldown gate not in its pinned shape"
    planted = text[:line.start()] + "\n" + text[line.end():]
    assert not combat_gate_ok(planted), \
        "planted-red: matcher stayed GREEN with the cooldown gate " \
        "deleted — dead gate"


def test_hero_controller_reads_bridge_and_feel_only():
    code = hyg.blank_code(read_text(CTRL_GD), "gd")   # comments blanked
    assert re.search(r"mission\.bridge\.move_vector\(\)", code), \
        "movement must read the Bridge (pinned row: reads Bridge only)"
    assert re.search(r"feel = m\.balance\.get\(", code), \
        "movement numbers arrive from balance.feel (F6)"
    assert not re.search(r"\bInput\b\.", code), \
        "no Input singleton: input arrives through the bridge relay"
    assert "move_and_slide" not in code, \
        "physics-server movement would break -s determinism (E5)"


def test_mission_carries_the_declared_w7_hooks_only():
    code = hyg.blank_code(read_text(MISSION_GD), "gd")
    assert re.search(r"\$HeroRig\.step\(delta\)", code), \
        "funnel slot (2) must drive the hero rig (C12 W7)"
    assert re.search(r"rig\.setup\(self\)", code), \
        "the rig is built by the declared setup hook"
