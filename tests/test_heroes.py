"""W3b heroes/progression gate (MC 11274.1.10 / card 11300).

Values + source-truth style (test_economy_numbers precedent, one idiom per
repo): the DATA legs read xp.json / heroes.json / ascension.json with stdlib
json; the .gd leg regexes godot/sim/sim_progression.gd — pytest cannot
execute GDScript, so behavior equality lands in the W11 goldens and this
file pins the CONTRACT SURFACE and the cap gates in source truth.

Readings recorded (card trail):
- The brief's names allocate_stat / gear_power / asc_point_gain /
  asc_unlock_ok / asc_spend / xp_for_level are superseded by the
  ARCHITECTURE Modules table (level_from_xp, xp_need, asc_points,
  asc_modifier) — the brief's own "READ FIRST (binding)" clause settles it
  (same reading W3a recorded for its divergences). The brief's rows map:
  "allocate_stat caps respected" = asc_modifier's per-node `max` clamp (a
  spend gate IS the stat-allocation cap, per-tree in one function);
  "gear_power shape" = the C9 rolled-item shape (primary/secondary
  {stat,value} legs are a gear's power), pinned in
  tests/test_loot_structure.py::test_roll_item_return_literal_is_exactly_
  the_c9_key_set; the two brief names are also grep-asserted ABSENT so no
  invented second mechanism hides beside the pinned one.
- Curve semantics (also in the .gd header): hero_curve[i] is the cumulative
  xp reaching level i+2; the hero level caps at the curve SIZE (A2's level
  cap 50 = the shipped 50-entry curve), so the cap is a data property and
  no 50 literal may exist in the .gd.
"""

import json
import re
import sys

from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for code-only greps)


def read_json(*parts):
    with open(repo_path(*parts), encoding="utf-8") as fh:
        return json.load(fh)


def read_sim(name):
    with open(repo_path("godot", "sim", name), encoding="utf-8") as fh:
        return fh.read()


XP = read_json("godot", "data", "xp.json")
HEROES = read_json("godot", "data", "heroes.json")
ASC = read_json("godot", "data", "ascension.json")
PROG_RAW = read_sim("sim_progression.gd")
PROG = hyg.blank_code(PROG_RAW, "gd")


def func_body(source, func):
    """Source lines of one static func, up to the next `static func`."""
    m = re.search(r"static func %s\(.*?(?=\nstatic func |\Z)" % func,
                  source, re.S)
    assert m, "static func %s missing" % func
    return m.group(0)


# ---------- 1. xp curve DATA (json): the cap-50 ladder ----------

def test_hero_curve_50_strictly_increasing():
    curve = XP["hero_curve"]
    assert len(curve) == 50
    assert all(b > a for a, b in zip(curve, curve[1:]))
    assert curve[0] > 0


# ---------- 2. level/xp source truth: walked + capped AT THE DATA ----------

def test_level_from_xp_walks_the_curve_and_caps_at_its_size():
    assert re.search(
        r"static func level_from_xp\(curve: Array, xp: int\) -> int:",
        PROG_RAW)
    body = func_body(PROG_RAW, "level_from_xp")
    assert re.search(r"if xp < threshold:", body), \
        "thresholds must be walked in order"
    assert re.search(r"return mini\(level, curve\.size\(\)\)", body), \
        "level must cap at the curve size (A2's cap lives IN THE CURVE)"


def test_xp_need_is_the_index_inverse_of_level_from_xp():
    assert re.search(
        r"static func xp_need\(curve: Array, level: int\) -> int:",
        PROG_RAW)
    body = func_body(PROG_RAW, "xp_need")
    assert re.search(r"if curve\.is_empty\(\) or level <= 1:\s*\n"
                     r"\t\treturn 0", body), "level 1 costs 0 xp"
    assert re.search(r"return int\(curve\[clampi\(level - 2, 0, "
                     r"curve\.size\(\) - 1\)\]\)", body), \
        "curve[i] reaches level i+2 — the pinned inverse, index-clamped"


def test_no_level_or_curve_numbers_are_hardcoded_in_progression():
    # The whole file is data-parameterised: no multi-digit integer literal
    # may exist in its CODE (curve values, the cap 50 — all data).
    m = re.search(r"(?<![\w.])\d{2,}", PROG)
    assert m is None, "progression hardcodes %r (I2: read xp.json)" \
        % m.group(0)


# ---------- 3. three heroes x four blue-cost abilities (data) ----------

def test_three_heroes_four_blue_cost_abilities_each():
    assert len(HEROES) == 3
    for hero in HEROES:
        abilities = hero["abilities"]
        assert len(abilities) == 4, hero["id"]
        costs = [a["mana_cost"] for a in abilities]
        assert all(c > 0 for c in costs), \
            "%s: every ability costs blue (A1)" % hero["id"]
        assert len({a["id"] for a in abilities}) == 4, hero["id"]


def test_hero_blue_pool_rows_are_present_and_positive():
    # F7: heroes.json base is the SOLE blue source.
    for hero in HEROES:
        base = hero["base"]
        assert base["blue_max"] > 0 and base["blue_regen"] > 0, hero["id"]


# ---------- 4. ascension: per-tree gates, source truth + json ----------

def test_asc_points_multiplies_levels_by_the_declared_rate():
    assert re.search(
        r"static func asc_points\(levels_total: int, per_level: int\) "
        r"-> int:", PROG_RAW)
    assert re.search(r"return levels_total \* per_level",
                     func_body(PROG_RAW, "asc_points"))
    rate = ASC["points_per_level"]
    assert isinstance(rate, int) and rate >= 1


def test_asc_modifier_gates_every_spend_at_its_declared_max():
    # The brief's "allocate_stat caps respected" row, on the pinned name:
    # per node inside every tree, spend is clamped at the node's `max`.
    assert re.search(
        r"static func asc_modifier\(tree: Dictionary, "
        r"spent: Dictionary\) -> Dictionary:", PROG_RAW)
    body = func_body(PROG_RAW, "asc_modifier")
    assert re.search(r"for branch: String in tree:", body), \
        "every tree must be walked (per-tree)"
    assert re.search(r'clampi\(int\(spent\.get\(id, 0\)\), 0, '
                     r'int\(row\.get\("max", 0\)\)\)', body), \
        "spend must clamp at the node's declared max (the gate)"
    assert re.search(r'totals\[stat\] = float\(totals\.get\(stat, 0\.0\)\)',
                     body), "same-stat nodes must aggregate"


def test_ascension_trees_are_three_with_positive_gates():
    tree = ASC["tree"]
    assert set(tree) == {"offense", "defense", "utility"}
    seen = set()
    for branch, powers in tree.items():
        assert powers, branch
        for power in powers:
            assert power["max"] >= 1, power["id"]
            assert power["per_point"]["val"] > 0, power["id"]
            assert power["id"] not in seen
            seen.add(power["id"])


def test_pinned_contract_names_replaced_the_briefs():
    # No invented second mechanism hides beside the pinned one: the brief's
    # divergent names must NOT exist in the pinned file either.
    for absent in ("gear_power", "allocate_stat", "asc_unlock_ok",
                   "asc_spend", "xp_for_level", "asc_point_gain"):
        assert absent not in PROG_RAW, absent
