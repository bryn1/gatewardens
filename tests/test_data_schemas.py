"""W2 data-layer schema guard (card 11298): every godot/data JSON parses,
carries the keys/types of the ARCHITECTURE.md data-files table, and every
cross-reference resolves — no engine, stdlib json only.

The I1 structural guard reuses the SAME token list the hygiene gate uses:
tools/check_hygiene.py exposes TRIPWIRE + tripwire_hit(), imported here
(no inline copy). It is applied to FIELD NAMES (dict keys at any depth)
of every data file — the schema-absence guard named by I1.

Ambiguity readings taken (recorded on the card trail):
- drop_table_id resolves against rarity.json drop_weights keys ("normal",
  "hard") — the only weight tables the pinned schema declares.
- abilities carry an `effect` STRING key per the task brief (engine
  behaviour lands in W7); the 6 table keys are also required.
- blacksmith reroll is {gold:int} per the pinned table (not gold+materials).
- towers family enum ("arrow|cannon|frost") binds class=="tower" rows;
  blockade/trap rows carry family "none".
"""

import json
import sys

import pytest

from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse of the I1 token list)

DATA = ("godot", "data")
FILES = [("economy.json",), ("balance.json",), ("xp.json",), ("heroes.json",),
         ("towers.json",), ("enemies.json",), ("rarity.json",), ("items.json",),
         ("mods.json",), ("ascension.json",), ("blacksmith.json",),
         ("maps", "gatefall.json"), ("waves", "waves_gatefall_normal.json"),
         ("waves", "waves_gatefall_hard.json")]
FILE_IDS = ["/".join(f) for f in FILES]
LADDER = ["worn", "sturdy", "powerful", "epic", "mythical", "legendary"]
MOD_SLOTS = {"worn": 0, "sturdy": 0, "powerful": 1, "epic": 2,
             "mythical": 2, "legendary": 3}


def load(*parts):
    with open(repo_path(*(DATA + parts)), encoding="utf-8") as handle:
        return json.load(handle)


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_str(v):
    return isinstance(v, str)


def is_bool(v):
    return isinstance(v, bool)


def is_list(v):
    return isinstance(v, list)


def is_dict(v):
    return isinstance(v, dict)


def is_int_list(v):
    return is_list(v) and all(is_int(x) for x in v)


def is_str_list(v):
    return is_list(v) and all(is_str(x) for x in v)


def is_num_list3(v):
    return is_list(v) and len(v) == 3 and all(is_num(x) for x in v)


def is_band(v):
    return (is_list(v) and len(v) == 2
            and all(is_num(x) for x in v) and v[0] <= v[1])


def is_hp_dict(v):
    return is_dict(v) and set(v) == {"normal", "hard"} \
        and all(is_num(x) for x in v.values())


def check_shape(obj, schema, where, errors):
    """schema: key -> predicate | ("opt", predicate); collects every miss."""
    if not isinstance(obj, dict):
        errors.append("%s: not a dict" % where)
        return
    for key, pred in schema.items():
        optional = isinstance(pred, tuple)
        pred = pred[1] if optional else pred
        if key not in obj:
            if not optional:
                errors.append("%s: missing key %r" % (where, key))
        elif not pred(obj[key]):
            errors.append("%s: key %r bad type %s"
                          % (where, key, type(obj[key]).__name__))


def walk_keys(obj, path=""):
    """All dict keys at any depth, as (path, key)."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            yield (path, key)
            yield from walk_keys(val, path + "/" + str(key))
    elif isinstance(obj, list):
        for i, val in enumerate(obj):
            yield from walk_keys(val, "%s[%d]" % (path, i))


# Per-file top-level shape (the architecture data-files table). Row-internal
# depth is checked by the cross-reference tests below; here: presence+kind.
TOP_SHAPE = {
    "economy.json": {"green": is_dict, "upgrade_ratios": is_list,
                     "repair_ratio": is_num, "sell_ratio": is_num,
                     "blue": is_dict},
    "balance.json": {"max_alive": is_int, "build_seconds_default": is_num,
                     "wave_delay": is_num, "pickup_radius": is_num,
                     "respawn_core_ratio": is_num, "feel": is_dict},
    "xp.json": {"hero_curve": is_int_list, "enemy_xp_base": is_dict,
                "wave_xp": is_int},
    "heroes.json": is_list,
    "towers.json": is_list,
    "enemies.json": is_list,
    "rarity.json": {"ladder": is_str_list, "mod_slots": is_dict,
                    "drop_weights": is_dict, "chest_tiers": is_str_list},
    "items.json": is_list,
    "mods.json": is_list,
    "ascension.json": {"points_per_level": is_int, "tree": is_dict},
    "blacksmith.json": {"materials": is_list, "upgrade": is_dict,
                        "evolve": is_dict, "reroll": is_dict,
                        "tinkering": is_dict},
    "maps/gatefall.json": {"id": is_str, "name": is_str,
                           "defense_cap": is_int, "start_green": is_int,
                           "spawners": is_dict, "cores": is_dict,
                           "lanes": is_list},
    "waves/waves_gatefall_normal.json": {"map": is_str, "difficulty": is_str,
                                         "waves": is_list},
    "waves/waves_gatefall_hard.json": {"map": is_str, "difficulty": is_str,
                                       "waves": is_list},
}


# ------------------------------------------------------------------ parse
@pytest.mark.parametrize("parts", FILES, ids=FILE_IDS)
def test_file_parses(parts):
    assert load(*parts) is not None


@pytest.mark.parametrize("parts", FILES, ids=FILE_IDS)
def test_file_top_shape(parts):
    doc = load(*parts)
    schema = TOP_SHAPE["/".join(parts)]
    errors = []
    if callable(schema):
        assert schema(doc), "top-level kind wrong"
    else:
        check_shape(doc, schema, "/".join(parts), errors)
    assert not errors


# -------------------------------------------------------------- economy
def test_economy_exact_shape_and_ratios():
    eco = load("economy.json")
    assert set(eco) == {"green", "upgrade_ratios", "repair_ratio",
                        "sell_ratio", "blue"}
    assert set(eco["green"]) == {"cap", "per_kill_default", "per_wave"}
    assert all(is_int(v) and v > 0 for v in eco["green"].values())
    assert eco["upgrade_ratios"] == [0.5, 1.0, 1.5, 2.0]
    assert eco["repair_ratio"] == 0.75 and eco["sell_ratio"] == 0.75
    assert eco["blue"] == {"refill_on_phase_start": True}


def test_economy_has_no_map_owned_or_regen_keys():
    # F7: start_green/defense_cap live ONLY in the map; blue regen ONLY in
    # heroes.json. Grep the parsed dicts, not the text.
    keys = {key for _path, key in walk_keys(load("economy.json"))}
    banned = {"start", "start_green", "defense_cap", "defense_cap_default"}
    assert not keys & banned, keys & banned
    assert not [k for k in keys if "regen" in k]


# --------------------------------------------------------------- balance
def test_balance_feel_keys_and_kinds():
    bal = load("balance.json")
    assert bal["max_alive"] == 100
    feel_keys = {"gravity", "jump_speed", "move_accel", "move_decel",
                 "facing_interp_rate", "cam_follow_rate", "cam_yaw_rate",
                 "death_fade"}
    assert set(bal["feel"]) == feel_keys
    assert all(is_num(v) for v in bal["feel"].values())
    assert bal["feel"]["gravity"] > bal["feel"]["jump_speed"] > 0


# -------------------------------------------------------------------- xp
def test_hero_curve_50_strictly_increasing():
    curve = load("xp.json")["hero_curve"]
    assert len(curve) == 50
    assert all(b > a for a, b in zip(curve, curve[1:]))
    base = load("xp.json")["enemy_xp_base"]
    assert set(base) == {"normal", "fly", "boss"}
    assert all(is_int(v) and v > 0 for v in base.values())


# ---------------------------------------------------------------- heroes
def test_three_heroes_full_rows():
    heroes = load("heroes.json")
    assert len(heroes) == 3
    assert {h["id"] for h in heroes} == {"warden", "deadeye", "embercaller"}
    assert {h["archetype"] for h in heroes} == {"melee", "ranger", "mage"}
    base_keys = {"health", "damage", "ability_power", "crit_chance",
                 "crit_damage", "speed", "blue_max", "blue_regen"}
    attack_keys = {"dmg_scale": is_num, "cooldown": is_num, "range": is_num}
    ability_keys = {"id": is_str, "name": is_str, "effect": is_str,
                    "mana_cost": is_num, "dmg_scale": is_num,
                    "aoe": is_num, "cd": is_num}
    tower_ids = {t["id"] for t in load("towers.json")}
    errors = []
    for hero in heroes:
        where = "hero %s" % hero.get("id", "?")
        check_shape(hero, {"id": is_str, "name": is_str,
                          "archetype": is_str, "base": is_dict,
                          "attacks": is_dict, "abilities": is_list,
                          "defense_id": is_str}, where, errors)
        check_shape(hero.get("base", {}),
                    {k: is_num for k in base_keys}, where + ".base", errors)
        for slot in ("primary", "secondary"):
            check_shape(hero.get("attacks", {}).get(slot, {}), attack_keys,
                        "%s.attacks.%s" % (where, slot), errors)
        abilities = hero.get("abilities", [])
        if len(abilities) != 4:
            errors.append("%s: %d abilities, expected exactly 4"
                          % (where, len(abilities)))
        for ab in abilities:
            check_shape(ab, ability_keys, "%s.ability %s"
                        % (where, ab.get("id", "?")), errors)
        if hero.get("defense_id") not in tower_ids:
            errors.append("%s: defense_id %r not in towers.json"
                          % (where, hero.get("defense_id")))
    assert not errors


# ---------------------------------------------------------------- towers
def test_tower_rows_tiers_classes():
    rows = load("towers.json")
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    classes = [r["class"] for r in rows]
    assert set(classes) <= {"tower", "blockade", "trap"}
    assert classes.count("tower") >= 3
    assert classes.count("blockade") == 1 and classes.count("trap") == 1
    families = {r["family"] for r in rows if r["class"] == "tower"}
    assert families == {"arrow", "cannon", "frost"}
    tier_keys = {"hp": is_num, "damage": is_num, "fire_rate": is_num,
                 "range": is_num, "effect": is_str}
    errors = []
    for row in rows:
        where = "tower %s" % row.get("id", "?")
        check_shape(row, {"id": is_str, "name": is_str, "class": is_str,
                          "family": is_str, "base_cost": is_int,
                          "tiers": is_list,
                          "trap_charges": ("opt", is_int)},
                    where, errors)
        if not (is_int(row.get("base_cost")) and row["base_cost"] > 0):
            errors.append("%s: base_cost must be a positive int" % where)
        tiers = row.get("tiers", [])
        if len(tiers) != 5:
            errors.append("%s: %d tiers, expected exactly 5"
                          % (where, len(tiers)))
        for tier in tiers:
            check_shape(tier, tier_keys, where + ".tier", errors)
        if row["class"] == "blockade":
            if any(t["damage"] != 0 for t in tiers):
                errors.append("%s: blockade damage must be 0" % where)
            if not all(is_num(t["hp"]) and t["hp"] > 0 for t in tiers):
                errors.append("%s: blockade needs positive hp per tier"
                              % where)
        if row["class"] == "trap":
            if not (is_int(row.get("trap_charges"))
                    and row["trap_charges"] > 0):
                errors.append("%s: trap trap_charges must be > 0" % where)
            slowish = (any(t["damage"] > 0 for t in tiers)
                       or any(t["effect"] == "slow" for t in tiers))
            if not slowish:
                errors.append("%s: trap needs slow/damage effect" % where)
    assert not errors


# --------------------------------------------------------------- enemies
def test_enemy_rows_and_hard_scaling():
    rows = load("enemies.json")
    ground = [r for r in rows if not r["fly"]]
    flyers = [r for r in rows if r["fly"]]
    assert len(ground) >= 4 and len(flyers) >= 2 and len(rows) >= 7
    assert len(ground) + len(flyers) == len(rows)
    drop_tables = set(load("rarity.json")["drop_weights"])
    declared_materials = {m["id"] for m in load("blacksmith.json")
                          ["materials"]}
    errors = []
    for row in rows:
        where = "enemy %s" % row.get("id", "?")
        check_shape(row, {"id": is_str, "name": is_str, "hp": is_hp_dict,
                          "damage": is_num, "speed": is_num, "fly": is_bool,
                          "xp": is_num, "green": is_num,
                          "drop_table_id": is_str,
                          "material_drop": ("opt", is_dict)}, where, errors)
        hp = row.get("hp", {})
        if is_dict(hp) and hp.get("hard", 0) < hp.get("normal", 0):
            errors.append("%s: hp.hard < hp.normal" % where)
        if row.get("drop_table_id") not in drop_tables:
            errors.append("%s: drop_table_id %r does not resolve in "
                          "rarity.drop_weights"
                          % (where, row.get("drop_table_id")))
        mat = row.get("material_drop")
        if mat is not None:
            check_shape(mat, {"id": is_str, "chance": is_num},
                        where + ".material_drop", errors)
            if mat.get("id") not in declared_materials:
                errors.append("%s: material id %r undeclared in "
                              "blacksmith.materials" % (where, mat.get("id")))
    assert not errors


# ---------------------------------------------------------------- rarity
def test_rarity_ladder_slots_and_weights():
    rar = load("rarity.json")
    assert rar["ladder"] == LADDER
    assert rar["mod_slots"] == MOD_SLOTS
    dw = rar["drop_weights"]
    assert set(dw) == {"normal", "hard"}
    for diff in ("normal", "hard"):
        table = dw[diff]
        assert set(table) <= set(LADDER)
        assert sum(table.values()) > 0
        if diff == "normal":
            assert all(v > 0 for v in table.values()), "each rarity > 0"
    top = {"epic", "mythical", "legendary"}
    share = lambda t: sum(v for k, v in t.items() if k in top) / sum(t.values())
    assert share(dw["hard"]) > share(dw["normal"]), "hard shifts upward"
    assert is_list(rar["chest_tiers"]) and rar["chest_tiers"]
    assert set(rar["chest_tiers"]) <= set(LADDER)


# ----------------------------------------------------------------- items
def test_item_bases_slots_and_rolls():
    rows = load("items.json")
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    mod_ids = {m["id"] for m in load("mods.json")}
    weapons = [r for r in rows if r["slot"] == "weapon"]
    melee = [r for r in weapons if r["shot_types"] == []]
    ranged = [r for r in weapons if r["shot_types"]]
    counts = {"armor": [r for r in rows if r["slot"] == "armor"],
              "ring": [r for r in rows if r["slot"] == "ring"],
              "relic": [r for r in rows if r["slot"] == "relic"]}
    assert len(weapons) >= 6 and melee and ranged
    assert len(counts["armor"]) >= 3 and len(counts["ring"]) >= 2
    assert len(counts["relic"]) >= 2
    schema = {"id": is_str, "slot": is_str, "level_band": is_band,
              "name": is_str, "primary": is_str,
              "pool_secondary": is_str_list, "roll_ranges": is_dict,
              "shot_types": is_str_list, "mods_pool": is_str_list}
    errors = []
    for row in rows:
        where = "item %s" % row.get("id", "?")
        check_shape(row, schema, where, errors)
        if row.get("slot") not in ("weapon", "armor", "ring", "relic"):
            errors.append("%s: bad slot" % where)
        rr = row.get("roll_ranges", {})
        check_shape(rr, {"atk_speed": is_band, "proj_count": is_band},
                    where + ".roll_ranges", errors)
        for mod in row.get("mods_pool", []):
            if mod not in mod_ids:
                errors.append("%s: mods_pool %r undeclared in mods.json"
                              % (where, mod))
    assert not errors


# ------------------------------------------------------------------ mods
def test_mods_rows():
    rows = load("mods.json")
    assert len(rows) >= 8
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    errors = []
    for row in rows:
        where = "mod %s" % row.get("id", "?")
        check_shape(row, {"id": is_str, "name": is_str, "rarity_min": is_str,
                          "effect": is_dict}, where, errors)
        if row.get("rarity_min") not in LADDER:
            errors.append("%s: rarity_min %r off the ladder"
                          % (where, row.get("rarity_min")))
        eff = row.get("effect", {})
        check_shape(eff, {"stat": is_str, "add": ("opt", is_num),
                          "flat": ("opt", is_num)}, where + ".effect", errors)
        if not {"add", "flat"} & set(eff):
            errors.append("%s: effect needs add or flat" % where)
    assert not errors


# ------------------------------------------------------------- ascension
def test_ascension_three_trees():
    asc = load("ascension.json")
    assert is_int(asc["points_per_level"]) and asc["points_per_level"] >= 1
    tree = asc["tree"]
    assert set(tree) == {"offense", "defense", "utility"}
    seen = set()
    errors = []
    for branch, powers in tree.items():
        if len(powers) < 4:
            errors.append("tree.%s: %d powers, need >= 4" % (branch, len(powers)))
        for power in powers:
            where = "asc %s.%s" % (branch, power.get("id", "?"))
            check_shape(power, {"id": is_str, "max": is_int,
                              "per_point": is_dict}, where, errors)
            check_shape(power.get("per_point", {}),
                        {"stat": is_str, "val": is_num},
                        where + ".per_point", errors)
            if power.get("id") in seen:
                errors.append("%s: duplicate power id" % where)
            seen.add(power.get("id"))
    assert not errors


# ------------------------------------------------------------- blacksmith
def test_blacksmith_costs_and_material_ids():
    blk = load("blacksmith.json")
    declared = [m["id"] for m in blk["materials"]]
    assert len(declared) == len(set(declared)) and declared
    assert all({"id", "name"} <= set(m) for m in blk["materials"])
    up = blk["upgrade"]
    assert is_dict(up["gold_by_rarity"]) and is_dict(up["materials"])
    assert set(up["gold_by_rarity"]) == set(LADDER)
    assert all(is_int(v) and v > 0 for v in up["gold_by_rarity"].values())
    services = {"upgrade": up, "evolve": blk["evolve"],
                "tinkering": blk["tinkering"]}
    for name, svc in services.items():
        mats = svc.get("materials", {})
        assert set(mats) <= set(declared), "%s undeclared material" % name
        assert all(is_int(v) and v > 0 for v in mats.values())
        gold = svc.get("gold", up["gold_by_rarity"]) if name == "upgrade" \
            else svc.get("gold")
        assert gold, name
    assert set(blk["reroll"]) == {"gold"}
    assert is_int(blk["reroll"]["gold"]) and blk["reroll"]["gold"] > 0


# -------------------------------------------------------------------- map
def test_map_c7_contract():
    m = load("maps", "gatefall.json")
    assert m["id"] == "gatefall"
    assert m["defense_cap"] == 60
    cheapest = min(t["base_cost"] for t in load("towers.json"))
    assert m["start_green"] >= 2 * cheapest, "must open with 2-3 cheap towers"
    for spawner, pos in m["spawners"].items():
        assert is_num_list3(pos), spawner
    cores = m["cores"]
    subs = cores["subs"]
    assert len(subs) == 1
    lane_ids = [lane["id"] for lane in m["lanes"]]
    assert len(lane_ids) == len(set(lane_ids))
    errors = []
    check_shape(cores["main"], {"hp": is_hp_dict, "pos": is_num_list3},
                "map.cores.main", errors)
    for sub in subs:
        check_shape(sub, {"id": is_str, "hp": is_hp_dict,
                          "pos": is_num_list3, "opens_lanes": is_str_list},
                    "map.sub %s" % sub.get("id"), errors)
        assert set(sub["opens_lanes"]) <= set(lane_ids)
    assert not errors
    kinds = [lane["kind"] for lane in m["lanes"]]
    assert kinds.count("ground") == 3 and kinds.count("air") == 2
    sub_ids = {sub["id"] for sub in subs}
    errors = []
    for lane in m["lanes"]:
        where = "lane %s" % lane.get("id")
        check_shape(lane, {"id": is_str, "kind": is_str, "spawner": is_str,
                           "waypoints": is_list, "target": is_str},
                    where, errors)
        if lane.get("spawner") not in m["spawners"]:
            errors.append("%s: spawner %r does not exist"
                          % (where, lane.get("spawner")))
        wps = lane.get("waypoints", [])
        if not wps:
            errors.append("%s: empty waypoint chain" % where)
        y_want = 2.5 if lane.get("kind") == "air" else 0
        for wp in wps:
            if not is_num_list3(wp):
                errors.append("%s: waypoint %r malformed" % (where, wp))
            elif wp[1] != y_want:
                errors.append("%s: waypoint %r y=%r, expected %r"
                              % (where, wp, wp[1], y_want))
        if lane.get("target") != "main" and lane.get("target") not in sub_ids:
            errors.append("%s: target %r unknown" % (where, lane.get("target")))
        # converge on the target core (x/z; air keeps flight height y)
        target = cores["main"] if lane.get("target") == "main" \
            else next(s for s in subs if s["id"] == lane["target"])
        if wps and (wps[-1][0], wps[-1][2]) != (target["pos"][0],
                                                target["pos"][2]):
            errors.append("%s: last waypoint does not reach target" % where)
    assert not errors


# ------------------------------------------------------------------ waves
def _wave_rows():
    return {diff: load("waves", "waves_gatefall_%s.json" % diff)
            for diff in ("normal", "hard")}


@pytest.mark.parametrize("difficulty", ("normal", "hard"))
def test_waves_c8_contract(difficulty):
    doc = _wave_rows()[difficulty]
    assert doc["map"] == "gatefall"
    assert doc["difficulty"] == difficulty
    waves = doc["waves"]
    assert len(waves) == 11
    kinds = [w["kind"] for w in waves]
    assert kinds.count("boss") == 1 and kinds[10] == "boss"
    assert all(k == "normal" for k in kinds[:10]), "SOLE boss at index 10"
    enemy_ids = {r["id"] for r in load("enemies.json")}
    cmap = load("maps", "gatefall.json")
    lane_ids = {lane["id"] for lane in cmap["lanes"]}
    air_lanes = {lane["id"] for lane in cmap["lanes"]
                 if lane["kind"] == "air"}
    opened = set().union(*(s["opens_lanes"]
                           for s in cmap["cores"]["subs"]))
    errors = []
    for index, wave in enumerate(waves):
        where = "%s wave %d" % (difficulty, index)
        check_shape(wave, {"kind": is_str, "build_seconds": is_num,
                           "enemies": is_list}, where, errors)
        if wave.get("build_seconds", 0) <= 0:
            errors.append("%s: build_seconds must be > 0" % where)
        entries = wave.get("enemies", [])
        if not entries:
            errors.append("%s: no enemies" % where)
        used = set()
        for entry in entries:
            check_shape(entry, {"enemy_id": is_str, "count": is_int,
                                "lane": is_str, "delay": is_num},
                        where + ".entry", errors)
            if entry.get("enemy_id") not in enemy_ids:
                errors.append("%s: enemy_id %r not in enemies.json"
                              % (where, entry.get("enemy_id")))
            if entry.get("lane") not in lane_ids:
                errors.append("%s: lane %r not in map" % (where, entry.get("lane")))
            if not (is_int(entry.get("count")) and entry["count"] > 0):
                errors.append("%s: count must be positive int" % where)
            if not (is_num(entry.get("delay")) and entry["delay"] >= 0):
                errors.append("%s: delay must be >= 0" % where)
            used.add(entry.get("lane"))
        # air lanes first appear wave 3+ (index 2+)
        if index < 2 and used & air_lanes:
            errors.append("%s: air lane before wave 3: %s" % (where, sorted(used & air_lanes)))
        # sub-core-opened lanes appear only mid-ramp (index >= 5)
        if index < 5 and used & opened:
            errors.append("%s: sub-opened lane before mid-ramp: %s"
                          % (where, sorted(used & opened)))
    assert not errors


def test_hard_richer_counts_than_normal():
    files = _wave_rows()
    for index in range(11):
        total = {diff: sum(e["count"]
                           for e in files[diff]["waves"][index]["enemies"])
                 for diff in ("normal", "hard")}
        assert total["hard"] >= total["normal"], (index, total)


# ------------------------------------------- I1 structural field guard
@pytest.mark.parametrize("parts", FILES, ids=FILE_IDS)
def test_no_banned_i1_field_names_in_data(parts):
    """Reuses tools/check_hygiene.TRIPWIRE via tripwire_hit() — the same
    token list the hygiene gate enforces. Field names = dict keys anywhere."""
    doc = load(*parts)
    hits = []
    for path, key in walk_keys(doc):
        token = hyg.tripwire_hit(key)
        if token:
            hits.append("%s: field %r trips %r" % (path, key, token))
    assert not hits


def test_tripwire_really_imported_from_hygiene_gate():
    assert hasattr(hyg, "TRIPWIRE") and "purchase" in hyg.TRIPWIRE
    # the guard can go red: a planted banned field name is caught
    assert hyg.tripwire_hit("purchase") == "purchase"
    assert hyg.tripwire_hit("cashStore") == "cash_store"
    assert hyg.tripwire_hit("base_cost") is None
