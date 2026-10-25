"""W3a economy/combat number gate (MC 11274.1.9 / card 11299).

Two legs, the repo's number-test idiom (hollow_dawn test_game_numbers
source-truth style): (1) assert the DATA — economy.json upgrade_ratios /
repair_ratio / sell_ratio + towers.json base_costs — against the pinned
wiki ladder (R1): upgrade = base x 0.5/1.0/1.5/2.0, i.e. 50/100/150/200 on
base 100, repair/sell both x 0.75; (2) SOURCE TRUTH — regex over
godot/sim/sim_economy.gd and sim_combat.gd proving the .gd functions
multiply the same args per C3 (repair multiplies base_cost, ratio AND
missing_ratio with an integer conversion and a min-1 floor while missing>0;
sell multiplies total_spent, ratio, missing_ratio; add_green clamps at cap;
hero_hit branches crit when roll < crit_chance), and the I3 split (the
word "blue" never appears in the green-side file).

Readings taken (recorded on the card trail):
- The task brief paraphrased different sim signatures (load_tables/
  upgrade_cost_at/wall_absorb/...); the brief's own line "signatures
  verbatim from the architecture, no invented extras" + its "READ FIRST
  (binding)" clause settle it: the ARCHITECTURE Modules table is what is
  implemented and what this file pins.
- C3 pins roundi() for repair/sell; the brief's "int()" reading =
  "an integer conversion is present" — roundi satisfies it and is what
  the PINNED contract names (upgrade_cost truncates via int(), the wiki
  ladder divides exactly on the shipped base_costs).
"""

import json
import re
import sys

from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: comment/string blanking)


def read_json(*parts):
    with open(repo_path(*parts), encoding="utf-8") as fh:
        return json.load(fh)


def read_sim(name):
    with open(repo_path("godot", "sim", name), encoding="utf-8") as fh:
        return fh.read()


ECONOMY = read_json("godot", "data", "economy.json")
TOWERS = read_json("godot", "data", "towers.json")
ECO = read_sim("sim_economy.gd")
COMBAT = read_sim("sim_combat.gd")


def body(source, func):
    """Source lines of one static func, up to the next `static func`."""
    m = re.search(r"static func %s\(.*?(?=\nstatic func |\Z)" % func,
                  source, re.S)
    assert m, "static func %s missing" % func
    return m.group(0)


# ---------- 1. DATA (stdlib json, no engine) — the wiki ladder ----------

def test_upgrade_ratio_ladder_is_the_wiki_ladder():
    ratios = ECONOMY["upgrade_ratios"]
    assert ratios == [0.5, 1.0, 1.5, 2.0]
    # 50/100/150/200 on base 100 (C3, the pinned example row).
    assert [int(100 * r) for r in ratios] == [50, 100, 150, 200]


def test_every_tower_ladder_derives_from_its_base_cost():
    ratios = ECONOMY["upgrade_ratios"]
    for row in TOWERS:
        base = row["base_cost"]
        assert isinstance(base, int) and base > 0, row["id"]
        ladder = [int(base * r) for r in ratios]
        assert ladder[0] == int(base * 0.5), row["id"]
        assert ladder == sorted(ladder), row["id"]
        assert all(c > 0 for c in ladder), row["id"]


def test_repair_and_sell_ratios_are_pinned_wiki_values():
    assert ECONOMY["repair_ratio"] == 0.75  # R1
    assert ECONOMY["sell_ratio"] == 0.75    # R1


def test_green_cap_and_award_rows_are_ints():
    assert isinstance(ECONOMY["green"]["cap"], int) and ECONOMY["green"]["cap"] > 0
    assert isinstance(ECONOMY["green"]["per_kill_default"], int)
    assert isinstance(ECONOMY["green"]["per_wave"], int)


# ---------- 2. SOURCE TRUTH — the .gd multiplies the same args ----------

def test_upgrade_cost_multiplies_base_by_ratios_entry():
    assert re.search(
        r"static func upgrade_cost\(base: int, tier: int, ratios: Array\) -> int:",
        ECO), "upgrade_cost signature per C3 missing"
    assert re.search(r"return int\(base \* ratios\[tier\]\)", ECO)


def test_repair_cost_multiplies_all_three_and_floors_at_one():
    assert re.search(
        r"static func repair_cost\(base_cost: int, missing_ratio: float,"
        r" ratio: float\) -> int:", ECO)
    b = body(ECO, "repair_cost")
    assert re.search(r"base_cost \* ratio \* missing_ratio", b), \
        "repair must multiply base, the 0.75-style ratio param AND missing"
    assert re.search(r"roundi\(", b), "integer conversion (roundi, C3) missing"
    assert re.search(r"maxi\(roundi\(base_cost \* ratio \* missing_ratio\), 1\)", b), \
        "min-1 floor while missing>0 missing"
    assert re.search(r"missing_ratio <= 0\.0", b), "zero-damage guard missing"


def test_sell_value_multiplies_total_spent_ratio_missing():
    assert re.search(
        r"static func sell_value\(total_spent: int, missing_ratio: float,"
        r" ratio: float\) -> int:", ECO)
    assert re.search(r"roundi\(total_spent \* ratio \* missing_ratio\)",
                     body(ECO, "sell_value"))


def test_add_green_clamps_at_cap():
    assert re.search(r"return mini\(cur \+ amt, cap\)", body(ECO, "add_green"))


def test_can_afford_is_a_plain_green_check():
    assert re.search(r"return green >= cost", body(ECO, "can_afford"))


def test_economy_signature_never_mentions_blue_i3():
    # Code only — comments/strings blanked first with the hygiene gate's
    # own pre-pass (I3 binds signatures, not prose).
    code = hyg.blank_code(ECO, "gd")
    assert not re.search(r"\bblue\b", code, re.I), \
        "I3: no green-side signature may carry blue"


def test_hero_hit_branches_crit_on_roll_below_chance():
    assert re.search(
        r"static func hero_hit\(dmg: float, crit_chance: float,"
        r" crit_mult: float, roll: float\) -> Dictionary:", COMBAT)
    b = body(COMBAT, "hero_hit")
    assert re.search(r"if roll < crit_chance:", b)
    assert re.search(r"dmg \* crit_mult", b)


def test_blue_tick_clamps_at_cap_and_ready_is_blue_side():
    assert re.search(r"return minf\(blue \+ regen \* dt, cap\)",
                     body(COMBAT, "tick_blue"))
    assert re.search(r"return blue >= cost", body(COMBAT, "ability_ready"))
