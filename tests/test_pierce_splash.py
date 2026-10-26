"""W15b — pierce/splash consumers (MC 11274.1.27 / card 11379).

The dead towers.json per-tier "effect" strings and the heroes.json
"piercer" ability row get their ONE consumer: SimCombat.extra_targets
(selects WHO ELSE a landed single hit also strikes; I4 — no second
damage path, every extra rides the caller's own damage through the
runner's same damage entry). Readings (also in the file headers):
- "pierce"  continues along the impact entity's LANE (C7 lanes are 1-D
  walks): every other same-lane entity within the row's data radius of
  the impact point — the data names no count and no direction, so the
  chain is the lane ∩ radius, inclusive boundary (proven at distance
  EXACTLY r — an off-by-one on the comparison flips this leg RED).
- "splash" hits every other entity within that radius of the impact
  point REGARDLESS of lane (crossing lanes near an impact splash).
- Any other effect ("none"/"slow"/"block"/missing field) = plain single
  hit. r <= 0 = plain single hit (degenerate leg). Hero leg: the
  single-target ability branch only, radius = the primary-attack range
  already used to pick the target; AoE-around-hero stays the shipped
  _in_range mechanism untouched.

Tier/radius/dps and hero rows are RE-DERIVED from the shipped JSON here,
never copied as literals (I2). Engine idiom per test_defense_boundaries:
the probe is generated into tmp_path (R5), boots the REAL mission under
-s (E5), drives shipped entries (defense_obj.tick / hero_combat.tick /
runner.spawn), asserts rc 0 + EMPTY stderr + named machine rows.
"""

import json
import re

import conftest

TOWERS = json.load(open(conftest.repo_path("godot", "data", "towers.json"),
                         encoding="utf-8"))
HEROES = json.load(open(conftest.repo_path("godot", "data", "heroes.json"),
                        encoding="utf-8"))
TOWER = {str(r["id"]): r for r in TOWERS}
DEADEYE = next(r for r in HEROES if r["id"] == "deadeye")

PROBE_SRC = '''\
# w15b_effects probe — effect consumers under -s (E5: _ready/setup
# driven directly; E3: failure paths early-return before quit()).
# Rows: EFFECT <leg> <k>=<1|0>... + DROP <leg> <k>=<%.17g>; pytest
# re-derives every expectation from the shipped JSON.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const DEF_OBJ := preload("res://scripts/defense_obj.gd")
const SIM_COMBAT := preload("res://sim/sim_combat.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["deadeye", "warden", "embercaller"]
const BRUTE := "husk_brute"        # highest normal hp: nothing one-shots
const BIG_GREEN := 99999999        # sentinel (W11b UNKNOWN_UID idiom)
const D := 1.0                     # one whole delta-second per fire leg
const STAND := Vector3.ZERO        # hero stand = main core pos = [0,0,0]

var m = null
var uid := 0
var tower_rows: Dictionary = {}   # towers.json raw door (mission idiom)


func _init() -> void:
	for row: Variant in JSON.parse_string(
			FileAccess.get_file_as_string("res://data/towers.json")):
		tower_rows[String(row["id"])] = row
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	var state = graph["state"]
	state.set_deck(DECK.duplicate())
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	m = packed.instantiate()
	root.add_child(m)
	m._ready()
	var rng := RandomNumberGenerator.new()
	rng.seed = 11379
	m.setup(tables, state, graph["save"], graph["bridge"], "gatefall",
			"normal", rng)
	_leg_none()
	_leg_pierce()
	_leg_pierce_end()
	_leg_splash()
	_leg_splash_solo()
	_leg_no_effect()
	_leg_hero_pierce()
	_leg_hero_aoe()
	_leg_static(graph)
	print("EFFECT-OK")
	quit(0)


func _runner():
	return m.get_node("EnemyRunner")


func _clear() -> void:
	for ent: Dictionary in _runner().entities:
		ent["node"].free()
	_runner().entities.clear()


func _ent(eid: String, lane_id: String, p: Vector3) -> Dictionary:
	_runner().spawn({"enemy_id": eid, "count": 1, "lane": lane_id,
			"delay": 0.0}, m.lanes[lane_id], m.enemy_defs, m.rng)
	var ent: Dictionary = _runner().entities.back()
	ent["pos"] = p
	return ent


func _tower(tid: String, to_tier: int):
	var obj = DEF_OBJ.new()
	uid += 1
	obj.init_defense(m, tower_rows[tid], Vector3.ZERO, uid)
	m.add_child(obj.node)          # tree-owned visual: no leak at exit
	m.green = BIG_GREEN
	for i: int in to_tier:
		var res: Dictionary = obj.upgrade()
		if not bool(res.get("ok", false)):
			_fail("upgrade %s -> %s" % [tid, str(res)])
			return null
	return obj


func _hit_flags(ent: Dictionary, before: float) -> String:
	return "1" if float(ent["hp"]) < before else "0"


func _drops(leg: String, pairs: Array) -> void:
	# str(float) is Godot's shortest round-trip float form (Python
	# float() reads it EXACTLY); the per-entity drops come off the SAME
	# hp base with the SAME product, so the printed strings are equal
	# whenever the damage is — that is the single-site check.
	var s := "DROP " + leg
	for p: Array in pairs:
		s += " %s=%s" % [String(p[0]), str(float(p[1]) - float(p[2]["hp"]))]
	print(s)


func _row(leg: String, pairs: Array) -> void:
	var s := "EFFECT " + leg
	for p: Array in pairs:
		s += " %s=%s" % [String(p[0]), _hit_flags(p[2], float(p[1]))]
	print(s)


func _leg_none() -> void:
	_clear()
	var t = _tower("ballista", 0)
	if t == null:
		return
	var e1 := _ent(BRUTE, "lane_g1", Vector3(6, 0, 0))
	var e2 := _ent(BRUTE, "lane_g1", Vector3(10, 0, 0))
	var b1 := float(e1["hp"])
	var b2 := float(e2["hp"])
	t.tick(D)
	_row("TOW-NONE", [["e1", b1, e1], ["e2", b2, e2]])
	_drops("TOW-NONE", [["e1", b1, e1]])


func _leg_pierce() -> void:
	_clear()
	var t = _tower("ballista", 2)          # T3: first pierce tier
	if t == null:
		return
	var e1 := _ent(BRUTE, "lane_g1", Vector3(6, 0, 0))
	var e2 := _ent(BRUTE, "lane_g1", Vector3(14, 0, 0))
	# distance-from-impact EXACTLY 18.0 = the inclusive boundary leg:
	# an off-by-one (`<` on the radius) drops this hit -> RED.
	var e3 := _ent(BRUTE, "lane_g1", Vector3(24, 0, 0))
	var e4 := _ent(BRUTE, "lane_g2", Vector3(12, 0, 0))
	var e5 := _ent(BRUTE, "lane_g1", Vector3(41, 0, 0))
	var b: Array = []
	for e: Dictionary in [e1, e2, e3, e4, e5]:
		b.append(float(e["hp"]))
	t.tick(D)
	_row("TOW-PIERCE", [["e1", b[0], e1], ["e2", b[1], e2],
			["e3", b[2], e3], ["e4", b[3], e4], ["e5", b[4], e5]])
	_drops("TOW-PIERCE", [["e1", b[0], e1], ["e2", b[1], e2],
			["e3", b[2], e3]])


func _leg_pierce_end() -> void:
	# degenerate lane-end: the only entity rides lane_g2, the chain
	# finds no second target -> plain single hit, no crash.
	_clear()
	var t = _tower("ballista", 2)
	if t == null:
		return
	var e1 := _ent(BRUTE, "lane_g2", Vector3(8, 0, 0))
	var b1 := float(e1["hp"])
	t.tick(D)
	_row("TOW-PIERCE-END", [["e1", b1, e1]])


func _leg_splash() -> void:
	_clear()
	var t = _tower("bombard", 2)           # T3: first splash tier
	if t == null:
		return
	var e1 := _ent(BRUTE, "lane_g1", Vector3(8, 0, 0))       # primary
	var e2 := _ent(BRUTE, "lane_g1", Vector3(20.5, 0, 0))    # d 12.5
	# distance-from-impact EXACTLY 13.0 = the inclusive boundary leg.
	var e3 := _ent(BRUTE, "lane_g1", Vector3(21, 0, 0))
	var e4 := _ent(BRUTE, "lane_g2", Vector3(13.5, 0, 0))    # cross-lane
	var e5 := _ent(BRUTE, "lane_g1", Vector3(30, 0, 0))      # d 22 > r
	var b: Array = []
	for e: Dictionary in [e1, e2, e3, e4, e5]:
		b.append(float(e["hp"]))
	t.tick(D)
	_row("TOW-SPLASH", [["e1", b[0], e1], ["e2", b[1], e2],
			["e3", b[2], e3], ["e4", b[3], e4], ["e5", b[4], e5]])
	_drops("TOW-SPLASH", [["e1", b[0], e1], ["e2", b[1], e2],
			["e3", b[2], e3], ["e4", b[3], e4]])


func _leg_splash_solo() -> void:
	# degenerate radius leg: one entity in the world -> single hit.
	_clear()
	var t = _tower("bombard", 2)
	if t == null:
		return
	var e1 := _ent(BRUTE, "lane_g1", Vector3(8, 0, 0))
	var b1 := float(e1["hp"])
	t.tick(D)
	_row("TOW-SPLASH-SOLO", [["e1", b1, e1]])


func _leg_no_effect() -> void:
	# missing-field tier = plain single hit: the SAME geometry as
	# TOW-NONE on a synthetic tier row with the "effect" key REMOVED.
	_clear()
	var row: Dictionary = tower_rows["ballista"].duplicate(true)
	(row["tiers"][0] as Dictionary).erase("effect")
	var obj = DEF_OBJ.new()
	uid += 1
	obj.init_defense(m, row, Vector3.ZERO, uid)
	m.add_child(obj.node)
	var e1 := _ent(BRUTE, "lane_g1", Vector3(6, 0, 0))
	var e2 := _ent(BRUTE, "lane_g1", Vector3(10, 0, 0))
	var b1 := float(e1["hp"])
	var b2 := float(e2["hp"])
	obj.tick(D)
	_row("TOW-NOEFFECT", [["e1", b1, e1], ["e2", b2, e2]])


func _leg_hero_pierce() -> void:
	# deadeye ability 1 (piercer, aoe 0, effect "pierce"): the lane
	# chain rides the SAME static as towers; radius = primary range.
	_clear()
	m.get_node("HeroRig").combat.tick(D, STAND)   # timer warm-up, no hold
	var ab: Dictionary = m.hero_defs["deadeye"]["abilities"][0]
	m.blue = float(m.blue_max)
	m.hero_state["deadeye"]["cooldowns"][0] = 0.0
	m.bridge.on_key("Digit1", true)
	var e1 := _ent(BRUTE, "lane_g1", Vector3(5, 0, 0))
	var e2 := _ent(BRUTE, "lane_g1", Vector3(17, 0, 0))
	# cross-lane INSIDE the radius: pierce must NOT hit it (sqrt(314)~17.7)
	var e3 := _ent(BRUTE, "lane_g2", Vector3(0, 0, 17))
	var e4 := _ent(BRUTE, "lane_g1", Vector3(30, 0, 0))
	var b: Array = []
	for e: Dictionary in [e1, e2, e3, e4]:
		b.append(float(e["hp"]))
	var blue_before := float(m.blue)
	m.get_node("HeroRig").combat.tick(D, STAND)
	m.bridge.on_key("Digit1", false)
	print("EFFECT HERO-PIERCE-STATE ok=%d" % [1 if (
			float(m.blue) == blue_before - float(ab["mana_cost"])
			and float(m.hero_state["deadeye"]["cooldowns"][0])
			== float(ab["cd"])) else 0])
	_row("HERO-PIERCE", [["e1", b[0], e1], ["e2", b[1], e2],
			["e3", b[2], e3], ["e4", b[3], e4]])


func _leg_hero_aoe() -> void:
	# control: the shipped AoE-around-hero mechanism stays UNTOUCHED
	# (arrow_storm aoe 5.0; the pierce leg must not have moved it).
	_clear()
	m.blue = float(m.blue_max)
	m.hero_state["deadeye"]["cooldowns"][1] = 0.0
	m.bridge.on_key("Digit2", true)
	var e1 := _ent(BRUTE, "lane_g1", Vector3(2, 0, 0))
	var e2 := _ent(BRUTE, "lane_g2", Vector3(0, 0, 4))
	var e3 := _ent(BRUTE, "lane_g1", Vector3(8, 0, 0))
	var b: Array = []
	for e: Dictionary in [e1, e2, e3]:
		b.append(float(e["hp"]))
	m.get_node("HeroRig").combat.tick(D, STAND)
	m.bridge.on_key("Digit2", false)
	_row("HERO-AOE", [["e1", b[0], e1], ["e2", b[1], e2],
			["e3", b[2], e3]])


func _syn(id: String, x: float, hp: float) -> Dictionary:
	return {"hp": hp, "lane": {"id": id}, "pos": Vector3(x, 0, 0)}


func _leg_static(graph) -> void:
	# the selection static DIRECTLY: degenerate/negative legs.
	var prim := _syn("l1", 10.0, 100.0)
	var near_same := _syn("l1", 14.0, 100.0)
	var near_other := _syn("l2", 14.0, 100.0)
	var dead := _syn("l1", 12.0, 0.0)
	var ok := true
	ok = ok and SIM_COMBAT.extra_targets(prim, [], 18.0, "pierce").is_empty()
	ok = ok and SIM_COMBAT.extra_targets(
			prim, [near_same], 18.0, "slow").is_empty()
	ok = ok and SIM_COMBAT.extra_targets(
			prim, [near_same], 18.0, "none").is_empty()
	ok = ok and SIM_COMBAT.extra_targets(
			prim, [near_same], 0.0, "splash").is_empty()
	ok = ok and SIM_COMBAT.extra_targets(
			prim, [near_same], -1.0, "splash").is_empty()
	ok = ok and SIM_COMBAT.extra_targets(
			prim, [dead], 18.0, "splash").is_empty()
	ok = ok and SIM_COMBAT.extra_targets(
			prim, [prim, near_same], 18.0, "splash").size() == 1
	ok = ok and SIM_COMBAT.extra_targets(
			prim, [near_other], 18.0, "pierce").is_empty()
	ok = ok and SIM_COMBAT.extra_targets(
			prim, [near_other], 18.0, "splash").size() == 1
	print("EFFECT STATIC ok=%d" % [1 if ok else 0])


func _fail(why: String) -> void:
	print("EFFECT FAIL " + why)
	quit(1)
'''


def _rows(out, tag):
    hits = [l for l in out.splitlines() if l.startswith(tag + " ")]
    assert len(hits) == 1, "%s row count=%d\n%s" % (tag, len(hits), out)
    return dict(kv.split("=", 1) for kv in hits[0][len(tag) + 1:].split(" "))


def _dps(tid, tier):
    t = TOWER[tid]["tiers"][tier]
    return float(t["damage"]) * float(t["fire_rate"])


def _drop_ok(row_map, keys, want):
    """Every named drop printed off the SAME hp base: EXACTLY equal
    strings (same damage through the one site), and numerically the
    shipped dps (float round-trip tolerance only)."""
    vals = [row_map[k] for k in keys]
    assert len(set(vals)) == 1, "extras carry different damage: %s" % vals
    return abs(float(vals[0]) - want) <= abs(want) * 1e-9


def check_rows(out):
    """All machine-row asserts over probe stdout; shared with the
    planted-red legs so the SAME checks must reject mutated rows."""
    # Tier effect presence is a DATA fact the legs ride (no drift):
    assert str(TOWER["ballista"]["tiers"][0]["effect"]) == "none"
    assert str(TOWER["ballista"]["tiers"][2]["effect"]) == "pierce"
    assert str(TOWER["bombard"]["tiers"][2]["effect"]) == "splash"

    # T1 "none": primary only, and the EXACT shipped-dps drop (no rng).
    assert _rows(out, "EFFECT TOW-NONE") == {"e1": "1", "e2": "0"}
    assert _drop_ok(_rows(out, "DROP TOW-NONE"), ["e1"],
                    _dps("ballista", 0))

    # T3 pierce: same-lane inside radius (incl. the EXACT-radius
    # boundary e3) hit; cross-lane inside radius (e4) and same-lane
    # beyond (e5) do not; extras carry the identical dps (single site).
    assert _rows(out, "EFFECT TOW-PIERCE") == {"e1": "1", "e2": "1",
                                               "e3": "1", "e4": "0",
                                               "e5": "0"}
    assert _drop_ok(_rows(out, "DROP TOW-PIERCE"), ["e1", "e2", "e3"],
                    _dps("ballista", 2))

    # Degenerate lane-end: single hit only.
    assert _rows(out, "EFFECT TOW-PIERCE-END") == {"e1": "1"}

    # T3 splash: same-lane inside radius (incl. the EXACT-radius
    # boundary e3) AND cross-lane inside radius (e4) hit; beyond (e5)
    # not; every hit carries the same dps (I4 — splash widens WHO).
    assert _rows(out, "EFFECT TOW-SPLASH") == {"e1": "1", "e2": "1",
                                               "e3": "1", "e4": "1",
                                               "e5": "0"}
    assert _drop_ok(_rows(out, "DROP TOW-SPLASH"),
                    ["e1", "e2", "e3", "e4"], _dps("bombard", 2))

    # Degenerate radius (one enemy) and the missing-field tier.
    assert _rows(out, "EFFECT TOW-SPLASH-SOLO") == {"e1": "1"}
    assert _rows(out, "EFFECT TOW-NOEFFECT") == {"e1": "1", "e2": "0"}

    # Hero leg: piercer = primary + same-lane chain inside the primary
    # range; cross-lane inside radius NOT hit; blue/cd pay the row.
    assert _rows(out, "EFFECT HERO-PIERCE-STATE") == {"ok": "1"}
    assert _rows(out, "EFFECT HERO-PIERCE") == {"e1": "1", "e2": "1",
                                                "e3": "0", "e4": "0"}
    piercer = DEADEYE["abilities"][0]
    assert str(piercer["effect"]) == "pierce"
    assert float(piercer["aoe"]) == 0.0

    # AoE-around-hero control stays the shipped mechanism.
    assert _rows(out, "EFFECT HERO-AOE") == {"e1": "1", "e2": "1",
                                            "e3": "0"}

    # Direct static legs: empty pool / inert effects / r<=0 / dead
    # extras / primary exclusion / lane discrimination.
    assert _rows(out, "EFFECT STATIC") == {"ok": "1"}

    assert "EFFECT-OK" in out.splitlines(), out


def test_effect_consumers_engine_leg(tmp_path, class_cache):
    probe = tmp_path / "w15b_effects_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    proc = conftest.run_probe_script(str(probe), (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    assert "EFFECT FAIL" not in proc.stdout, proc.stdout
    check_rows(proc.stdout)


def _fire_tower_body(text):
    m = re.search(r"func _fire_tower\(delta: float\) -> void:\n(.*?)(?=\n"
                  r"(?:@|func|var) )", text + "\nfunc var_sentinel() -> "
                  "void:\n\tpass\n", re.S)
    assert m, "defense_obj.gd exposes no func _fire_tower(delta)"
    return m.group(1)


def effect_wired(text, path_marker):
    """Source truth: the shipped fire leg reads the row's effect string
    and routes it through the ONE selection static (no second damage
    site — the runner damage call count stays one pattern)."""
    body = _fire_tower_body(text)
    return ('row.get("effect"' in body
            and "SIM_COMBAT.extra_targets" in body
            and path_marker in body)


def test_fire_leg_wiring_with_planted_red():
    """Planted-red leg #1 (mutation gate): a copy of defense_obj.gd
    with the pierce/splash consumer REMOVED (the effect arg pinned to
    "none", the shipped pre-W15b state) MUST fail the same matcher —
    the gate can go RED without touching any file."""
    with open(conftest.repo_path("godot", "scripts", "defense_obj.gd"),
              encoding="utf-8") as fh:
        text = fh.read()
    assert effect_wired(text, "runner.damage(ent, dmg)"), \
        "_fire_tower must route the row effect through extra_targets"
    broken = text.replace('String(row.get("effect", "none"))',
                          '"none"')
    assert broken != text, "planted-red anchor drifted — update this leg"
    assert not effect_wired(broken, "runner.damage(ent, dmg)"), \
        "gate stayed green with the effect consumer removed"
