"""v1.2.1 G6 — floating damage numbers incl. KILL BLOW (MC 11691).

Contract (V121-PLAN §G6 Rev 2, the BINDING kill-blow shape (b)):
a number's value == the hp drop OBSERVED for every observed hit, and
== snap["hp"] (DECLARED LOWER BOUND of the killing blow — overkill is
unobservable because mission.step applies ALL damage before the runner
drains hp<=0 in the same tick) on the killing blow; BOTH routes (hero
hit, tower hit) terminate at the ONE damage site (enemy_runner.damage).
The hp<=0-never-seen-alive sub-case renders nothing; a breacher
reached at hp>0 renders no final number. Numbers COUNT toward the same
MAX_FX=64 cap; past the cap they drop, never queue-starve.

ENGINE leg (conftest.run_probe_script idiom, test_pierce_splash boot,
v5_fx_probe cap rows): the probe is generated into tmp_path (R5), boots
the REAL mission under -s (E5), and drives ONLY shipped entries —
defense_obj.tick (tower route), HeroRig.combat.tick + Digit1 (hero
route), runner.damage (the ONE damage site itself, probe license) and
runner.step (the slot-(4) drain). pytest re-derives every expected
value from the shipped JSON — no literals copied (TOW_DPS from
towers.json, ability floor from heroes.json).

Planted-red transcripts (fleet gate rule) ride the G6 wave log:
(1) drop format halved -> VAL value legs RED; (2) final-number branch
removed -> KILL legs RED (fails LOUD, the plan's point of the row).

SOURCE-TRUTH legs: the observer doctrine extends to the number spawn —
zero writes to mission/runner state (MUT_RE/WRITE_RE families per the
test_hud home, kept local like every other test module here); and the
DECLARED one world-text mechanism: Label3D lives in world_text.gd only.
"""

import json
import os
import re
import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: the gate's blank_code)

FX_GD = conftest.repo_path("godot", "scripts", "fx_director.gd")
WORLD_TEXT_GD = conftest.repo_path("godot", "scripts", "world_text.gd")
GODOT_DIR = conftest.repo_path("godot")

TOWERS = json.load(open(conftest.repo_path("godot", "data", "towers.json"),
                        encoding="utf-8"))
HEROES = json.load(open(conftest.repo_path("godot", "data", "heroes.json"),
                        encoding="utf-8"))
BALLISTA = next(r for r in TOWERS if r["id"] == "ballista")
# The ONE tower-route applied amount: sim_combat.tower_dps = damage *
# fire_rate, applied as dps() * delta with delta = 1.0 in the probe.
TOW_DPS = (float(BALLISTA["tiers"][0]["damage"])
           * float(BALLISTA["tiers"][0]["fire_rate"]))
DEADEYE = next(r for r in HEROES if r["id"] == "deadeye")
PIERCER = DEADEYE["abilities"][0]
# Ability damage floor (no-crit): base.ability_power x dmg_scale — the
# hero_route oversize proof: even the floor kills a SNAP-hp entity.
AB_FLOOR = (float(DEADEYE["base"]["ability_power"])
            * float(PIERCER["dmg_scale"]))
SNAP = 5.0            # probe-side last-observed hp (scenario, not data)

# The shipped mutator families + direct-write shapes — families per the
# test_hud.py home (kept local per this repo's one-module-per-contract
# test style, no cross-test imports anywhere in tests/).
MUT_RE = re.compile(r"\b(?:add_|spend_|consume_|set_|equip|place_)\w*\s*\(")
PLUMBING = {"add_child"}
WRITE_RE = re.compile(
    r"\b(?:m|mission|state|game_state)\.[A-Za-z_]\w*"
    r"(?:\[[^\]]*\])?\s*(?:[+\-*/]?=[^=])")

PROBE_SRC = '''\
# v121_g6_damage_numbers probe — floating damage numbers + KILL BLOW
# under -s (E5: mission steps and fx_step driven by hand, mission root
# first — the exact live tree order; test_pierce_splash boots, shipped
# entries drive; v5_fx_probe pins the cap from the director's own
# constant). Boots the REAL mission; FxDirector mounts off mission.tscn
# (pinned script path, the scene child — not a probe-side add_child).
# Damage rides ONLY the ONE damage site: runner.damage (direct probe
# license — it IS the site), defense_obj.tick (tower route), and
# HeroRig.combat.tick + Digit1 (hero route). Drain legs drive the
# shipped enemy_runner.step (the slot-(4) drain only, no awards). The
# director itself stays write-free end to end (source-truth leg).
# Machine rows: N6-MOUNT VAL-TOW VAL-HERO CAP KILL-TOW KILL-HERO
# NEG-BREACH NEG-UNSEEN OK; any failure prints N6-FAIL <why>, quit 1.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const DEF_OBJ := preload("res://scripts/defense_obj.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["deadeye", "warden", "embercaller"]
const BRUTE := "husk_brute"
const TOWER_ID := "ballista"
const D := 1.0                  # one whole delta-second per hit leg
const SNAP := 5.0               # kill-blow last-observed hp (lower bound)
const STAND := Vector3.ZERO       # hero stand = main core pos
const P5 := Vector3(5, 0, 0)    # inside ballista T1 range 16 AND the
                                # hero primary range 18
const CAP_FX := 64              # pinned from the director's own cap
const OBS := 0.02               # observation step < every fx life: the
                                # row scan sees the nodes the step made

var m = null
var fx = null
var uid := 0


func _init() -> void:
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
	rng.seed = 11691
	m.setup(tables, state, graph["save"], graph["bridge"], "gatefall",
			"normal", rng)
	fx = m.get_node_or_null("FxDirector")
	if fx == null:
		_fail("mission.tscn does not ship FxDirector")
		return
	if String(fx.script.resource_path) != "res://scripts/fx_director.gd":
		_fail("FxDirector on wrong script: %s" % fx.script.resource_path)
		return
	print("N6-MOUNT mounted=1")
	_leg_val_tow()
	_leg_val_hero()
	_leg_cap()
	_leg_kill_tow()
	_leg_kill_hero()
	_leg_breach()
	_leg_unseen()
	print("N6-OK")
	quit(0)


func _runner():
	return m.get_node("EnemyRunner")


func _trow(tid: String) -> Dictionary:
	for row: Dictionary in m.tables.rows("towers"):
		if String(row["id"]) == tid:
			return row
	_fail("no towers.json row for %s" % tid)
	return {}


func _settle() -> void:
	# Drop every entity, then one delta=1.0 fx_step: it ages out every
	# fx kind (all lives <= NUMBER_LIFE 0.5 < 1.0) AND erases the freed
	# snapshots — a settle step never leaves a node live into the next
	# leg, so every leg reads ONLY its own labels.
	for ent: Dictionary in _runner().entities:
		ent["node"].free()
	_runner().entities.clear()
	fx.fx_step(1.0)


func _labels() -> Array:
	var out: Array = []
	for c: Node in fx.get_children():
		var lb := c as Label3D
		if lb != null:
			out.append(String(lb.text))
	return out


func _only(leg: String) -> String:
	var ls := _labels()
	if ls.size() != 1:
		_fail("%s: expected exactly one live number, got %s" \\
				% [leg, str(ls)])
		return ""
	return String(ls[0])


func _ent(p: Vector3) -> Dictionary:
	_runner().spawn({"enemy_id": BRUTE, "count": 1, "lane": "lane_g1",
			"delay": 0.0}, m.lanes["lane_g1"], m.enemy_defs, m.rng)
	var ent: Dictionary = _runner().entities.back()
	ent["pos"] = p
	return ent


func _leg_val_tow() -> void:
	_settle()
	var obj = DEF_OBJ.new()
	uid += 1
	obj.init_defense(m, _trow(TOWER_ID), Vector3.ZERO, uid)
	m.add_child(obj.node)                 # tree-owned visual: no leak
	var e := _ent(P5)
	fx.fx_step(OBS)                         # track at full hp: nothing
	var tl := _labels().size()            #   spawns on the track step
	var before := float(e["hp"])
	var s0 := int(fx.spawned_sparks)
	var n0 := int(fx.spawned_numbers)
	obj.tick(D)                           # THE tower route
	var drop := before - float(e["hp"])
	fx.fx_step(OBS)
	print("N6-VAL-TOW track_labels=%d drop=%s label=%s sparks=%d numbers=%d" \
			% [tl, str(drop), _only("VAL-TOW"), int(fx.spawned_sparks) \
			- s0, int(fx.spawned_numbers) - n0])


func _leg_val_hero() -> void:
	_settle()
	var rig = m.get_node("HeroRig")
	rig.combat.tick(D, STAND)            # timer warm-up, no hold (W15b)
	var e := _ent(P5)
	fx.fx_step(OBS)                         # track at full hp
	var tl := _labels().size()
	var before := float(e["hp"])
	var s0 := int(fx.spawned_sparks)
	var n0 := int(fx.spawned_numbers)
	m.blue = float(m.blue_max)
	m.hero_state["deadeye"]["cooldowns"][0] = 0.0
	m.bridge.on_key("Digit1", true)
	rig.combat.tick(D, STAND)            # THE hero route (Digit1 =
	m.bridge.on_key("Digit1", false)      #   deadeye piercer)
	var drop := before - float(e["hp"])
	fx.fx_step(OBS)
	print("N6-VAL-HERO track_labels=%d drop=%s label=%s sparks=%d numbers=%d" \
			% [tl, str(drop), _only("VAL-HERO"), int(fx.spawned_sparks) \
			- s0, int(fx.spawned_numbers) - n0])


func _leg_cap() -> void:
	# Saturation: 8 fed entities x (spark + number) per fx_step at
	# delta 0.004 (spark life 0.2 -> ~50 live, numbers outlive them)
	# passes the cap INSIDE the leg — the invariant is kids <= 64 every
	# frame, and numbers provably COUNT (a labels-only budget could not
	# pass 64 with 60 frames of sparks riding the same life).
	_settle()
	var ents: Array = []
	for i: int in 8:
		ents.append(_ent(Vector3(20, 0, 0)))
	var live_max := 0
	var labels_live := 0
	var drop_frames := 0
	for f: int in 60:
		var fed := 0
		for e: Dictionary in ents:
			if float(e["hp"]) > 2.0:
				_runner().damage(e, 1.0)  # the ONE damage site (header)
				fed += 1
		if fed == 0:
			break
		drop_frames += 1
		fx.fx_step(0.004)
		var kids: int = fx.get_child_count()
		if kids > CAP_FX:
			_fail("cap leg: %d live fx > cap %d" % [kids, CAP_FX])
			return
		live_max = maxi(live_max, kids)
		labels_live = maxi(labels_live, _labels().size())
	print("N6-CAP live_max=%d labels_live=%d drop_frames=%d" \\
			% [live_max, labels_live, drop_frames])


func _leg_kill_tow() -> void:
	_settle()
	var obj = DEF_OBJ.new()
	uid += 1
	obj.init_defense(m, _trow(TOWER_ID), Vector3.ZERO, uid)
	m.add_child(obj.node)
	var e := _ent(P5)
	_runner().damage(e, float(e["hp"]) - SNAP)   # license: set the hp
	var p0 := int(fx.spawned_poofs)              #   the observer LAST
	var n0 := int(fx.spawned_numbers)            #   sees (ONE site)
	fx.fx_step(OBS)                                # OBSERVED ALIVE at SNAP
	var tl := _labels().size()
	obj.tick(D)                                  # applied TOW_DPS*1 > SNAP
	_runner().step(D)                            # slot-(4) drain only
	fx.fx_step(OBS)
	print("N6-KILL-TOW track_labels=%d label=%s poofs=%d numbers=%d" \\
			% [tl, _only("KILL-TOW"), int(fx.spawned_poofs) - p0,
			int(fx.spawned_numbers) - n0])


func _leg_kill_hero() -> void:
	_settle()
	var rig = m.get_node("HeroRig")
	rig.combat.tick(D, STAND)            # warm-up, no hold
	var e := _ent(P5)
	_runner().damage(e, float(e["hp"]) - SNAP)
	var p0 := int(fx.spawned_poofs)
	var n0 := int(fx.spawned_numbers)
	fx.fx_step(OBS)                         # OBSERVED ALIVE at SNAP
	var tl := _labels().size()
	m.blue = float(m.blue_max)
	m.hero_state["deadeye"]["cooldowns"][0] = 0.0
	m.bridge.on_key("Digit1", true)
	rig.combat.tick(D, STAND)            # ability floor > SNAP: oversize
	m.bridge.on_key("Digit1", false)
	_runner().step(D)                     # slot-(4) drain only
	fx.fx_step(OBS)
	print("N6-KILL-HERO track_labels=%d label=%s poofs=%d numbers=%d" \\
			% [tl, _only("KILL-HERO"), int(fx.spawned_poofs) - p0,
			int(fx.spawned_numbers) - n0])


func _leg_breach() -> void:
	# NEGATIVE: a breacher is consumed AT the lane end with hp > 0 —
	# the same death discrimination as the poof must render NO final
	# number (and no poof).
	_settle()
	var e := _ent(P5)
	var wps: Array = (e["lane"] as Dictionary).get("wps", [])
	e["pos"] = wps[wps.size() - 1]        # LAST OBSERVED pos = lane end
	fx.fx_step(OBS)                         # tracked alive, hp > 0
	var p0 := int(fx.spawned_poofs)
	var n0 := int(fx.spawned_numbers)
	var ev: Dictionary = _runner().step(D)
	var reached: int = (ev["reached"] as Array).size()
	fx.fx_step(OBS)
	print("N6-NEG-BREACH labels=%d poofs=%d numbers=%d reached=%d" \\
			% [_labels().size(), int(fx.spawned_poofs) - p0,
			int(fx.spawned_numbers) - n0, reached])


func _leg_unseen() -> void:
	# The declared sub-case: killed before ANY fx_step ever saw it
	# alive -> never in _tracked -> renders nothing (honest).
	_settle()
	var p0 := int(fx.spawned_poofs)
	var n0 := int(fx.spawned_numbers)
	var e := _ent(P5)
	_runner().damage(e, float(e["hp"]) + 1.0)
	var ev: Dictionary = _runner().step(D)
	var dead: int = (ev["dead"] as Array).size()
	fx.fx_step(OBS)
	print("N6-NEG-UNSEEN labels=%d poofs=%d numbers=%d dead=%d" \\
			% [_labels().size(), int(fx.spawned_poofs) - p0,
			int(fx.spawned_numbers) - n0, dead])


func _fail(why: String) -> void:
	print("N6-FAIL " + why)
	quit(1)
'''


def _run_probe(tmp_path):
    probe = Path(tmp_path) / "v121_g6_damage_numbers.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), (), tmp_path / "user_home")


def _row(out, tag):
    hits = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert len(hits) == 1, "%s: want exactly one row\n%s" % (tag, out)
    fields = {}
    for chunk in hits[0].split(" ")[1:]:
        k, _, v = chunk.partition("=")
        fields[k] = v
    return fields


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def test_kill_blow_and_number_legs(tmp_path, class_cache):
    proc = _run_probe(tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "N6-FAIL" not in out, out
    assert out.rstrip().splitlines()[-1].startswith("N6-OK"), out
    assert _row(out, "N6-MOUNT") == {"mounted": "1"}

    # VALUE legs (both damage routes terminate at the ONE site): the
    # number text == str(int(observed drop)); the tower drop equals the
    # sim's own applied amount re-derived from towers.json (float
    # round-trips the last ulp through hp — agreement is at int()).
    tow = _row(out, "N6-VAL-TOW")
    assert tow["track_labels"] == "0", out
    assert abs(float(tow["drop"]) - TOW_DPS) < 1e-6, tow
    assert tow["label"] == str(int(TOW_DPS)), tow
    assert (tow["sparks"], tow["numbers"]) == ("1", "1"), tow
    hero = _row(out, "N6-VAL-HERO")
    assert hero["track_labels"] == "0", out
    assert float(hero["drop"]) > 0.0, hero
    assert hero["label"] == str(int(float(hero["drop"]))), hero
    assert (hero["sparks"], hero["numbers"]) == ("1", "1"), hero

    # CAP leg: numbers COUNT toward MAX_FX — the high-water mark hits
    # the pinned 64 WITH numbers among the live nodes, the invariant
    # never breaks, and drops keep coming past the cap (480 feed frames
    # vs a 64-node ceiling): dropped, never queue-starved.
    cap = _row(out, "N6-CAP")
    assert int(cap["live_max"]) == 64, cap
    assert int(cap["labels_live"]) >= 1, cap
    assert int(cap["drop_frames"]) == 60, cap

    # KILLING-BLOW legs (oversized hit both routes — floor proofs from
    # the shipped JSON): the FINAL number == snap["hp"] (declared
    # LOWER BOUND; overkill unobservable), one poof, one number.
    assert TOW_DPS * 1.0 > SNAP and AB_FLOOR > SNAP, \
        "kill legs vacuous: hits not oversized"
    for tag in ("N6-KILL-TOW", "N6-KILL-HERO"):
        kill = _row(out, tag)
        assert kill["track_labels"] == "0", kill
        assert kill["label"] == str(int(SNAP)), kill
        assert (kill["poofs"], kill["numbers"]) == ("1", "1"), kill

    # NEGATIVE legs: breacher (reached, hp>0) renders NO final number
    # and NO poof; the never-observed-alive sub-case renders nothing.
    br = _row(out, "N6-NEG-BREACH")
    assert (br["labels"], br["poofs"], br["numbers"]) == ("0", "0", "0"), br
    assert br["reached"] == "1", br
    un = _row(out, "N6-NEG-UNSEEN")
    assert (un["labels"], un["poofs"], un["numbers"]) == ("0", "0", "0"), un
    assert un["dead"] == "1", un


def test_observer_and_factory_make_zero_state_writes():
    # Observer doctrine extends to the number spawn: neither the
    # observer nor the world-text factory calls a shipped mutator or
    # writes onto injected mission state (families per test_hud.py).
    for path in (FX_GD, WORLD_TEXT_GD):
        code = hyg.blank_code(_read(path), "gd")
        muts = [mm.group(0).rstrip("(").strip()
                for mm in MUT_RE.finditer(code)
                if mm.group(0).rstrip("(").strip() not in PLUMBING]
        assert muts == [], "%s calls a shipped mutator: %s" % (path, muts)
        writes = [mm.group(0) for mm in WRITE_RE.finditer(code)]
        assert writes == [], "%s writes injected state: %s" % (path, writes)
        # and the sim's OWN fields stay unread-for-write through dicts:
        assert re.search(r'\bent\["hp"\]\s*=', code) is None, \
            "%s writes ent hp" % path


def test_label3d_lives_only_in_world_text():
    # The DECLARED first use: world_text.gd is the ONE world-text
    # mechanism — no other godot/ source may touch Label3D directly.
    hits = []
    for root, dirs, files in os.walk(GODOT_DIR):
        dirs[:] = [d for d in dirs if d not in (".godot", "archive")]
        for f in files:
            if not f.endswith(".gd"):
                continue
            p = os.path.join(root, f)
            if "Label3D" in hyg.blank_code(_read(p), "gd"):
                hits.append(os.path.relpath(p, GODOT_DIR))
    assert hits == [os.path.join("scripts", "world_text.gd")], hits
