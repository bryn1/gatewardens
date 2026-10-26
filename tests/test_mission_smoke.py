"""W6 mission-scene smoke + funnel source-truth gate, W7 hero extension,
W8 defense extension (MC 11274.1.13 / card 11308; MC 11274.1.14 / card
11321; MC 11274.1.15 / card 11322).

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
import math
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
OBJ_GD = conftest.repo_path("godot", "scripts", "defense_obj.gd")
PLACER_GD = conftest.repo_path("godot", "scripts", "defense_placer.gd")
PANEL_GD = conftest.repo_path("godot", "scripts", "defense_panel.gd")
HEROES_JSON = conftest.repo_path("godot", "data", "heroes.json")
TOWERS_JSON = conftest.repo_path("godot", "data", "towers.json")
ECONOMY_JSON = conftest.repo_path("godot", "data", "economy.json")
ENEMIES_JSON = conftest.repo_path("godot", "data", "enemies.json")
GATEFALL_JSON = conftest.repo_path("godot", "data", "maps", "gatefall.json")
ITEMS_JSON = conftest.repo_path("godot", "data", "items.json")
RARITY_JSON = conftest.repo_path("godot", "data", "rarity.json")

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
    _w8_rows(proc.stdout)
    _loot_row(proc.stdout)
    _w14_rows(proc.stdout)


def _w14_rows(out):
    """W14 machine rows (MC 11274.1.25 / card 11341): placement is
    reachable THROUGH the mission-mounted panel over the shipped bridge
    (green drops EXACTLY the data base_cost; the pinned R1 full-HP sell
    refunds 0), and the Digit2 press casts WITHOUT swapping the active
    hero while the F-keys stay the swap path (P1-1 / P1-4). Every number
    re-derives from towers.json / heroes.json / gatefall.json."""
    towers = _json(TOWERS_JSON)
    seen, first = set(), None
    for row in towers:
        if row["class"] not in seen:
            seen.add(row["class"])
            if first is None:
                first = row
    panel = _row(out, "MISSION-SMOKE-W14PANEL")
    assert panel["mount"] == "1", panel
    assert panel["class"] == first["class"], panel
    assert int(panel["cost"]) == int(first["base_cost"]), panel
    assert int(panel["refund"]) == 0, panel          # R1: full-HP refund 0
    assert int(panel["green"]) == _json(GATEFALL_JSON)["start_green"], panel
    swap = _row(out, "MISSION-SMOKE-W14SWAP")
    warden = _hero_row("warden")
    ab = warden["abilities"][1]                        # Digit2 = ability 2
    assert swap["hero"] == "warden" and swap["digit2_cast"] == "1", swap
    expected = float(ab["mana_cost"]) \
            - float(warden["base"]["blue_regen"]) / 60.0   # regen ticks once
    assert abs(float(swap["blue_drop"]) - expected) < 1e-6, (swap, expected)
    assert swap["f2_hero"] == "deadeye", swap


def _loot_row(out):
    """W11 (card 11326) MISSION-SMOKE-LOOT: the slot-(6) loot_pickup event
    feed + HUD toast. base_id re-derives from items.json, rarity from the
    rarity.json ladder — the row binds to DATA, never literals here."""
    hits = [l for l in out.splitlines()
            if l.startswith("MISSION-SMOKE-LOOT ")]
    assert len(hits) == 1, "MISSION-SMOKE-LOOT row count=%d" % len(hits)
    loot = dict(kv.split("=", 1) for kv in hits[0].split(" ")[1:])
    bases = {b["id"] for b in _json(ITEMS_JSON)}
    ladder = _json(RARITY_JSON)["ladder"]
    assert int(loot["events"]) >= 1, loot
    assert loot["base"] in bases, loot
    assert loot["rarity"] in ladder, loot
    assert loot["toast"] == "on", loot
    return loot


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

def _json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _half_away(x):
    """Godot's roundi semantics: round half AWAY from zero."""
    return math.floor(abs(x) + 0.5) * (1 if x >= 0 else -1)


def _w8_rows(out):
    """W8 machine rows, every number re-derived from the shipped data
    files (towers.json / economy.json / enemies.json / gatefall.json)."""
    towers = {row["id"]: row for row in _json(TOWERS_JSON)}
    eco = _json(ECONOMY_JSON)
    skit = [e for e in _json(ENEMIES_JSON) if e["id"] == "skitterling"][0]
    start_green = _json(GATEFALL_JSON)["start_green"]
    # class placement costs = the FIRST towers.json row of each class
    # (the placer.classes() idiom, mirrored here from file order).
    first = {}
    for row in _json(TOWERS_JSON):
        first.setdefault(row["class"], row)
    tower, block, trap = first["tower"], first["blockade"], first["trap"]
    ratios = eco["upgrade_ratios"]

    place = _row(out, "MISSION-SMOKE-W8PLACE")
    assert place["class"] == "tower" and place["tier"] == "1", place
    assert int(place["cost"]) == tower["base_cost"], place
    assert int(place["green"]) == start_green - tower["base_cost"], \
        "green must drop EXACTLY the data cost: %s" % place

    up = _row(out, "MISSION-SMOKE-W8UPGRADE")
    assert int(up["cost"]) == int(tower["base_cost"] * ratios[0]), \
        "T1->T2 ladder price: %s" % up
    t1, t2 = tower["tiers"][0], tower["tiers"][1]
    assert abs(float(up["dps"]) - t2["damage"] * t2["fire_rate"]) < 1e-6, up
    assert float(up["dps"]) > t1["damage"] * t1["fire_rate"], \
        "the dps must RISE with the tier (from data): %s" % up
    assert int(up["green"]) == start_green - tower["base_cost"] - int(up["cost"])

    rep = _row(out, "MISSION-SMOKE-W8REPAIR")
    want = max(1, _half_away(tower["base_cost"] * eco["repair_ratio"] * 0.5))
    assert int(rep["cost"]) == want, "repair = base x ratio x missing: %s" % rep
    assert float(rep["hp"]) == float(t2["hp"]), "repair tops to full hp: %s" % rep

    rep1 = _row(out, "MISSION-SMOKE-W8REPAIR1")
    want1 = max(1, _half_away(tower["base_cost"] * eco["repair_ratio"]
                              * (1.0 / t2["hp"])))
    assert int(rep1["cost"]) == want1 == 1, "floor-1 leg: %s" % rep1

    place2 = _row(out, "MISSION-SMOKE-W8PLACE2")
    assert int(place2["cost"]) == block["base_cost"], place2

    cap = _row(out, "MISSION-SMOKE-W8CAP")
    assert cap["why"] == "cap", cap
    assert int(cap["green"]) == int(place2["green"]), \
        "cap+1 refusal must leave green UNCHANGED: %s vs %s" % (cap, place2)
    assert int(cap["count"]) >= 1, cap

    sell = _row(out, "MISSION-SMOKE-W8SELL")
    refund = _half_away(block["base_cost"] * eco["sell_ratio"] * 0.5)
    assert int(sell["refund"]) == refund, "sell = total_spent x ratio x missing: %s" % sell
    assert int(sell["green"]) == int(cap["green"]) + refund, sell

    free = _row(out, "MISSION-SMOKE-W8FREESLOT")
    assert int(free["cost"]) == trap["base_cost"], free
    assert int(free["charges"]) == trap["trap_charges"], free
    assert int(free["green"]) == int(sell["green"]) - trap["base_cost"], free

    pan = _row(out, "MISSION-SMOKE-W8PANEL")
    assert pan["classes"].split("|") == ["tower", "blockade", "trap"], pan
    gate_at = trap["base_cost"]
    assert int(pan["gate"]) == sum(1 for row in first.values()
                                   if row["base_cost"] <= gate_at), pan

    act = _row(out, "MISSION-SMOKE-W8PANEL-ACT")
    assert int(act["refund"]) == 0, "full-HP sell = ratio x 0 = 0 (pinned R1): %s" % act
    assert int(act["cost"]) == block["base_cost"], act
    assert int(act["green"]) == gate_at - block["base_cost"], act

    kill = _row(out, "MISSION-SMOKE-W8KILL")
    assert int(kill["green"].lstrip("+")) == skit["green"], \
        "tower dps kill awards exactly one skitterling green: %s" % kill
    assert int(kill["xp"].lstrip("+")) == skit["xp"], kill
    assert int(kill["t"]) > 0, kill


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ---------- W8 source truth (I2/I4): costs only from data, single sites ---

DEFENSE_GD = (OBJ_GD, PLACER_GD, PANEL_GD)
# The I2 structural set (ARCHITECTURE.md): math constants, slot/arity
# indices, sentinels — NO cost or ratio values can survive it. ONE home:
# tools/check_hygiene.py (W16) — the gate's i2-literal rule and this
# guard read the SAME set, so they cannot drift apart.
STRUCT_VALS = hyg.STRUCT_VALS
NUM_RE = hyg.LITERAL_RE


def _literal_violations(code):
    # blank_code is idempotent; callers pass blanked OR raw text, the
    # hygiene helper blanks first and the set/regex are the gate's own.
    return hyg.literal_violations(code)


def test_defense_files_carry_no_cost_or_ratio_literals():
    for path in DEFENSE_GD:
        code = hyg.blank_code(read_text(path), "gd")
        bad = _literal_violations(code)
        assert not bad, "%s carries non-structural number literals %r " \
            "(I2: costs/ratios come from data via SimEconomy)" % (path, bad)


def test_defense_planted_red_ratio_literal_goes_red():
    # Fixture trick (nothing written to disk): inject the 0.75 ratio as a
    # code literal — the SAME gate must flag it (an unbroken number gate
    # is no gate at all).
    text = read_text(OBJ_GD)
    planted = text.replace(
        "func missing_ratio() -> float:",
        "func _planted(x: float) -> float:\n\treturn x * 0.75\n\n"
        "func missing_ratio() -> float:", 1)
    assert _literal_violations(hyg.blank_code(planted, "gd")) == [0.75], \
        "planted-red: 0.75 slipped through the defense literal gate"


def test_cost_formulas_have_single_application_sites():
    obj = hyg.blank_code(read_text(OBJ_GD), "gd")
    for call in ["SIM_ECONOMY\\.upgrade_cost\\(", "SIM_ECONOMY\\.repair_cost\\(",
                 "SIM_ECONOMY\\.sell_value\\(", "SIM_COMBAT\\.tower_dps\\("]:
        assert len(re.findall(call, obj)) == 1, \
            "defense_obj must call %s at exactly one site (C3/I4)" % call
    panel = hyg.blank_code(read_text(PANEL_GD), "gd")
    assert not re.search(r"SIM_ECONOMY\.(upgrade_cost|repair_cost|sell_value)"
                         r"\(|SIM_COMBAT\.tower_dps\(", panel), \
        "defense_panel is pure UI: no cost/fire STATIC may be called (row; " \
        "the next_upgrade_cost() obj READ of the priced rung is state)"
    assert re.search(r"SIM_ECONOMY\.can_afford\(", panel), \
        "the panel's tier gate is the shipped can_afford static"
    mis = hyg.blank_code(read_text(MISSION_GD), "gd")
    assert not re.search(r"tower_dps|upgrade_cost|repair_cost|sell_value", mis), \
        "mission.gd holds no defense cost math (the obj/placer own their legs)"
    assert len(re.findall(r"green -= cost", mis)) == 1, \
        "place is the mission's ONE green write (I4 single site)"


def test_mission_place_defense_pins_cap_afford_spend_order():
    tail = read_text(MISSION_GD)
    assert re.search(r"func place_defense\(row: Dictionary, tier: int, "
                     r"at: Vector3\) -> Dictionary:", tail), \
        "mission.gd must expose place_defense (pinned row)"
    for pat in [r"defense_list\.size\(\) >= defense_cap",
                r"SIM_ECONOMY\.can_afford\(green, cost\)",
                r"green -= cost",
                r"defense_list\.append\(\{\"uid\""]:
        hit = re.search(pat, tail)
        assert hit is not None, "place_defense crossing missing: %s" % pat
        tail = tail[hit.end():]


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
