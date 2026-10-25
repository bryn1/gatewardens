"""W3b loot-structure gate (MC 11274.1.10 / card 11300).

Values + source-truth style (the repo number-test idiom, test_economy_numbers
precedent). The pinned contract surface is asserted from the SOURCE TEXT,
because pytest cannot execute GDScript (no engine here): the pinned
signatures, receiver-qualified rng draws ONLY (F2-1), and the EXACT key sets
of the roll/service return literals — a rolled dict carries exactly the C9
keys and nothing else (the I1 structural guard: no paid/clock/timer field
exists in ANY rolled dict because none exists in the schema; the schema IS
the defense). The brief's own reading applies: pytest cannot run GDScript,
so behavior equality lands in the W11 goldens — the brief's "scripted rng
stub" belongs to that -s golden harness, not to this file. Data legs assert
the ladder, mod-slot map, drop weights and chest tiers ARE in data/ — so the
sim files carry no ladder names and no weight numbers ("declared weights
only", I2), each absence pinned as its own source-truth row.

Readings recorded (card trail):
- The brief's loot function names (roll_stats/roll_weapon_extras/roll_drop)
  are superseded by the ARCHITECTURE Modules table (roll_rarity, roll_item,
  enemy_drops, victory_chest) — the brief's "READ FIRST (binding)" clause
  makes the pinned table the contract; same reading W3a recorded for its
  divergences.
- SimInventory.equip's {ok, bank} replace-return (F2-11) is pinned here as
  the return-literal key set; equip's merge-in semantics are documented in
  the .gd header (GWGameState.equip owns the caller side, W5+).
- uid 0 on rolled rows: the uid stamp is the bank's (bank_add), not a roll
  concern — pinned as part of the C9 literal.
"""

import json
import re
import sys

from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code, rand regexes, tripwire)


def read_json(*parts):
    with open(repo_path(*parts), encoding="utf-8") as fh:
        return json.load(fh)


def read_sim(name):
    with open(repo_path("godot", "sim", name), encoding="utf-8") as fh:
        return fh.read()


RARITY = read_json("godot", "data", "rarity.json")
ITEMS = read_json("godot", "data", "items.json")
MODS = read_json("godot", "data", "mods.json")
BLACKSMITH = read_json("godot", "data", "blacksmith.json")
LOOT_RAW = read_sim("sim_loot.gd")
INV_RAW = read_sim("sim_inventory.gd")
LOOT = hyg.blank_code(LOOT_RAW, "gd")   # comments/strings out, lines true
INV = hyg.blank_code(INV_RAW, "gd")

# C9 — the pinned item-instance shape (ARCHITECTURE Contracts, verbatim keys).
C9_KEYS = {"uid", "base_id", "slot", "rarity", "ilvl", "primary",
           "secondary", "atk_speed", "shot_type", "proj_count", "mods",
           "upgraded"}
LADDER = ["worn", "sturdy", "powerful", "epic", "mythical", "legendary"]


def func_body(source, func):
    """Source lines of one static func, up to the next `static func`."""
    m = re.search(r"static func %s\(.*?(?=\nstatic func |\Z)" % func,
                  source, re.S)
    assert m, "static func %s missing" % func
    return m.group(0)


def literal_at(text, start):
    """The {...} block (as text) opening at index start; returns (lit, end)."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1], i + 1
    raise AssertionError("unbalanced dict literal from offset %d" % start)


def top_keys(literal):
    """Dict keys at depth 1 of one dict-literal text."""
    keys, depth, i = [], 0, 0
    while i < len(literal):
        ch = literal[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif ch == '"' and depth == 1:
            j = literal.index('"', i + 1)
            k = j + 1
            while k < len(literal) and literal[k] == " ":
                k += 1
            if k < len(literal) and literal[k] == ":":
                keys.append(literal[i + 1:j])
            i = j + 1
            continue
        i += 1
    return keys


def return_key_sets(source, func):
    """Key sets of every `return {…}` literal inside one static func."""
    body = func_body(source, func)
    sets, pos = [], 0
    while True:
        m = re.search(r"return\s*\{", body[pos:])
        if not m:
            return sets
        start = body.index("{", pos + m.start())
        lit, end = literal_at(body, start)
        sets.append(set(top_keys(lit)))
        pos = end


def cost_key_set(source, func):
    """Key set of the `var cost := {…}` literal inside one static func."""
    body = func_body(source, func)
    m = re.search(r"var cost :?= \{", body)
    assert m, "%s has no cost literal" % func
    lit, _ = literal_at(body, body.index("{", m.start()))
    return set(top_keys(lit))


def walk_keys(obj):
    """All dict keys at any depth (same guard shape as test_data_schemas)."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            yield key
            yield from walk_keys(val)
    elif isinstance(obj, list):
        for val in obj:
            yield from walk_keys(val)


# ---------- 1. The rolled item shape IS C9 (structural I1 defense) ----------

def test_roll_item_return_literal_is_exactly_the_c9_key_set():
    sets = return_key_sets(LOOT_RAW, "roll_item")
    assert len(sets) == 1, "roll_item must have one return literal"
    assert sets[0] == C9_KEYS, "rolled item keys != C9: %r" % (
        sets[0] ^ C9_KEYS)


def test_no_banned_i1_token_in_any_rolled_or_cost_key():
    # The schema IS the defense: every key any roll or service can emit is
    # checked against the hygiene gate's OWN I1 token list (reused, never
    # copied — same guard the data-schema test reuses).
    rolled_keys = (C9_KEYS | {"stat", "value", "mod_id", "kind", "item",
                              "id", "ok", "bank", "cost", "gold",
                              "materials"})
    for key in rolled_keys:
        assert hyg.tripwire_hit(key) is None, "banned I1 field %r" % key
    assert hyg.tripwire_hit("purchase") == "purchase"  # guard is live


def test_loot_relevant_data_files_carry_no_banned_field_names():
    for doc in (RARITY, ITEMS, MODS, BLACKSMITH):
        for key in walk_keys(doc):
            assert hyg.tripwire_hit(key) is None, \
                "data field %r trips the I1 token list" % key


# ---------- 2. Equip / services: pinned return shapes ----------

def test_equip_returns_ok_and_bank_per_f2_11():
    assert re.search(
        r"static func equip\(bank: Array, hero: String, "
        r"item: Dictionary\) -> Dictionary:", INV_RAW)
    sets = return_key_sets(INV_RAW, "equip")
    assert sets and all(s == {"ok", "bank"} for s in sets), \
        "every equip return must be {ok, bank} (F2-11): %r" % sets


def test_service_returns_are_ok_and_cost_with_gold_and_materials():
    for func in ("svc_upgrade", "svc_evolve", "svc_reroll", "tinkering"):
        sets = return_key_sets(INV_RAW, func)
        assert sets, "%s: no return literal" % func
        assert all(s == {"ok", "cost"} for s in sets), \
            "%s return keys %r != {ok, cost}" % (func, sets)
    for func in ("svc_upgrade", "svc_evolve", "tinkering"):
        assert cost_key_set(INV_RAW, func) == {"gold", "materials"}, func
    assert cost_key_set(INV_RAW, "svc_reroll") == {"gold", "materials"}, \
        "reroll cost carries gold + an EMPTY materials map (pinned shape)"


def test_service_signatures_are_the_pinned_shapes():
    assert re.search(
        r"static func svc_upgrade\(item: Dictionary, tables, "
        r"mats: Dictionary\) -> Dictionary:", INV_RAW)
    assert re.search(
        r"static func svc_evolve\(item: Dictionary, tables, "
        r"mats: Dictionary\) -> Dictionary:", INV_RAW)
    # F2-2: the reroll draws THROUGH the passed rng — it is a parameter.
    assert re.search(r"static func svc_reroll\(item, rng, tables\)", INV_RAW)
    assert re.search(
        r"static func tinkering\(source, target, mod_i, tables, mats\)",
        INV_RAW)


def test_enemy_drops_rows_are_item_and_material_shapes():
    body = func_body(LOOT_RAW, "enemy_drops")
    assert re.search(r'drops\.append\(\{"kind": "item", "item": item\}\)',
                     body), "gear drop row shape changed"
    assert re.search(r'drops\.append\(\{"kind": "material", "id": '
                     r'String\(mat\["id"\]\)\}\)', body), \
        "material drop row must be exactly {kind, id} (F2-6)"
    assert re.search(r'rng\.randf\(\) < float\(mat\["chance"\]\)', body), \
        "material gate must be the DECLARED chance (F2-6), rng-qualified"


# ---------- 3. RNG discipline (C12 / F2-1) ----------

def test_roll_signatures_take_the_rng_parameter():
    assert re.search(
        r"static func roll_rarity\(tables: Dictionary, diff: String, "
        r"luck: float, rng: RandomNumberGenerator\) -> String:", LOOT_RAW)
    assert re.search(
        r"static func roll_item\(base: Dictionary, rarity: String, "
        r"tables, rng\) -> Dictionary:", LOOT_RAW)
    assert re.search(
        r"static func enemy_drops\(row: Dictionary, tables, rng\) -> "
        r"Array:", LOOT_RAW)
    assert re.search(
        r"static func victory_chest\(tier: int, tables, rng\) -> Array:",
        LOOT_RAW)


def test_draws_are_receiver_qualified_never_bare():
    # Reuses the hygiene gate's own compiled patterns (one mechanism).
    for name, code in (("sim_loot.gd", LOOT), ("sim_inventory.gd", INV)):
        assert not hyg.BARE_RAND_RE.search(code), \
            "%s: BARE randf()/randi() (F2-1)" % name
    assert len(hyg.QUAL_RAND_RE.findall(LOOT)) >= 4, \
        "loot must actually draw through the injected rng"


# ---------- 4. Weights/ladder live in DATA; sim files carry none ----------

def test_ladder_and_slot_map_are_the_data_values():
    assert RARITY["ladder"] == LADDER
    slots = RARITY["mod_slots"]
    assert set(slots) == set(LADDER), "mod_slots must cover the ladder"
    ladder_slots = [slots[r] for r in LADDER]
    assert ladder_slots == sorted(ladder_slots), "slots never shrink up-ladder"


def test_drop_weight_tables_are_declared_and_positive():
    dw = RARITY["drop_weights"]
    assert set(dw) == {"normal", "hard"}
    for diff in ("normal", "hard"):
        table = dw[diff]
        assert set(table) == set(LADDER), "%s: weights cover the ladder" % diff
        assert all(v >= 0 for v in table.values())
        assert sum(table.values()) > 0, "%s: weight table must sum > 0" % diff


def test_chest_tiers_rides_the_declared_ladder():
    tiers = RARITY["chest_tiers"]
    assert tiers and set(tiers) <= set(LADDER)


def test_no_rarity_ladder_names_in_the_sim_files():
    # "declared weights only": the ladder stays in rarity.json. Comments are
    # stripped but strings are KEPT, so a hardcoded ladder name cannot hide.
    for name, raw in (("sim_loot.gd", LOOT_RAW), ("sim_inventory.gd", INV_RAW)):
        code = re.sub(r"#.*", "", raw)
        for rarity_name in LADDER:
            assert rarity_name not in code, \
                "%s hardcodes ladder name %r" % (name, rarity_name)


def test_no_weight_or_cost_numbers_in_the_loot_or_inventory_files():
    # Every weight/cost value is a table read, so no integer literal >= 2
    # may exist in either file's CODE (strings/comments blanked first with
    # the hygiene gate's own pre-pass; 0/1 are structural).
    for name, code in (("sim_loot.gd", LOOT), ("sim_inventory.gd", INV)):
        m = re.search(r"(?<![\w.])[2-9]", code)
        assert m is None, "%s carries numeric literal %r (I2: table-read it)" \
            % (name, m.group(0) if m else None)


def test_rolls_happen_inside_declared_ranges_only():
    body = func_body(LOOT_RAW, "roll_item")
    assert re.search(r"int\(band\[0\]\) \+ rng\.randi\(\) % "
                     r"\(int\(band\[1\]\) - int\(band\[0\]\) \+ 1\)", body), \
        "ilvl must roll inside the declared level_band"
    assert re.search(r"float\(speed\[0\]\) \+ rng\.randf\(\) \* "
                     r"\(float\(speed\[1\]\) - float\(speed\[0\]\)\)", body), \
        "atk_speed must lerp the declared roll_ranges pair"
    assert re.search(r"rng\.randi\(\) % \(int\(counts\[1\]\) - "
                     r"int\(counts\[0\]\) \+ 1\)", body), \
        "proj_count must roll the declared integer range"
    assert re.search(r'base\["mods_pool"\]\.duplicate\(\)', body), \
        "mods roll from the base's declared pool"


def test_rarity_and_chest_read_the_declared_tables():
    body = func_body(LOOT_RAW, "roll_rarity")
    assert re.search(r'\["drop_weights"\]\[diff\]', body), \
        "weights come from drop_weights[diff] (data)"
    assert re.search(r"\(1\.0 \+ luck \* float\(i\)\)", body), \
        "luck is a ladder-index bias, 0 = declared weights verbatim"
    assert re.search(r"rng\.randf\(\) \* total", body)
    chest = func_body(LOOT_RAW, "victory_chest")
    assert re.search(r'tables\["rarity"\]\["chest_tiers"\]', chest)
    assert re.search(r"clampi\(tier, 0, tiers\.size\(\) - 1\)", chest), \
        "chest tier indexes the declared ladder, clamped"


def test_mod_slots_function_reads_the_data_map():
    assert re.search(
        r"static func mod_slots\(rarity: String, ladder: Dictionary\) "
        r"-> int:", INV_RAW)
    assert re.search(r"return int\(ladder\.get\(rarity, 0\)\)",
                     func_body(INV_RAW, "mod_slots")), \
        "slot count is the rarity.json mod_slots read, no table here"
