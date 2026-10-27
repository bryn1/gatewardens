"""W17f lane round-robin placement order (MC 11274.1.33 / card 11403).

DEFECT (browser journey, wave-4/5 wall): _build_slots() emitted the
placeable slots in LANE-FILE BLOCK order (all lane_g1 waypoints, then
lane_g2's, then lane_g3's) and the panel's place() falls to first_free —
so every consecutive UI-style place piled into lane_g1 until it was
full. The player's defenses all stood in one lane; the other ground
lanes walked free (the wave-4/5 wall: leaks across lanes the towers
never covered).

FIX (defense_placer.gd only): the slot LIST is emitted INTERLEAVED
round-robin across the ground lanes (g1a, g2a, g3a, g1b, g2b, g3b, ...)
— same content rules (ground-only, dedup-by-position, cores excluded),
same first-free semantics; only the ORDER rotates. Explicit lane+wp
callers (fixtures, smoke, panel row-select, upgrades by uid) resolve
positions via slot_at and are order-independent.

ENGINE TIER (EMPTY stderr idiom, test_mission_stale.py boot): real
mission under -s; placer.place(class, 1) with NO slot arg IS the panel
class-button call (defense_panel place_selected) — the UI-style place.
LEG: three consecutive first-free places (build phase, map start_green
300, tower base_cost 100) MUST land on THREE DISTINCT ground lanes;
the 4th (green topped by the data cost — the mission.green write lever
models kill/wave income) MUST land on an empty slot, never an occupied
one. PLANTED-RED: "blocked_order" rebuilds placer.slots in the pre-fix
lane-blocked order (the defect reintroduced); the SAME leg MUST go RED.
"""

import sys
from pathlib import Path

import conftest

GODOT = Path(conftest.repo_path("godot"))

PROBE_SRC = '''
extends SceneTree
# gw lane-order probe (W17f). Machine rows: GWRR-PLACE n= lane= pos= /
# GWRR-OK; any failed check prints GWRR-FAIL + rc1. PLANTED-RED arg
# "blocked_order": rebuild placer.slots in the pre-fix lane-file-blocked
# order (g1a..g1d, g2a.., g3a..) — the W17f defect shape.
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const DEF_PLACER := preload("res://scripts/defense_placer.gd")
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]

var m = null


func _fail(why: String) -> void:
	print("GWRR-FAIL " + why)
	quit(1)


func _init() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	var state = graph["state"]
	state.set_deck(DECK.duplicate())     # starter deck via the C13 write
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	m = packed.instantiate()
	root.add_child(m)
	m._ready()                           # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274                     # pinned seed, smoke idiom
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	var placer = DEF_PLACER.new()
	placer.setup(m)
	# pos -> ground lane_id, read from the map lanes (data, no literals).
	var pos_lane: Dictionary = {}
	for lane_id: String in m.lanes:
		var lane: Dictionary = m.lanes[lane_id]
		if String(lane["kind"]) != "ground":
			continue
		for wp: Variant in lane["wps"]:
			if not pos_lane.has(wp):
				pos_lane[wp] = lane_id
	if OS.get_cmdline_user_args().has("blocked_order"):
		# PLANTED-RED: the W17f pre-fix lane-file-blocked slot order,
		# rebuilt with the pre-fix rules verbatim (file order, dedup,
		# cores excluded) — the defect reintroduced on the live placer.
		var blocked: Dictionary = {m.core_main.pos: true}
		for sid: String in m.core_subs:
			blocked[m.core_subs[sid].pos] = true
		var rebuilt: Array = []
		var seen: Dictionary = {}
		for lane_id: String in m.lanes:
			var lane: Dictionary = m.lanes[lane_id]
			if String(lane["kind"]) != "ground":
				continue
			for wp: Variant in lane["wps"]:
				if blocked.has(wp) or seen.has(wp):
					continue
				seen[wp] = true
				rebuilt.append(wp)
		placer.slots = rebuilt
	var cost := int(placer.row_for("tower")["base_cost"])
	var landed: Array = []
	var lanes_seen: Array = []
	for i: int in 4:
		if i == 3:
			# 4th leg needs green again: the mission.green write lever
			# (mission_smoke start_green idiom) models kill/wave income;
			# the top-up is the DATA cost, no literal (I2).
			m.green += cost
		var res: Dictionary = placer.place("tower", 1)   # the panel's
		if not bool(res.get("ok", false)):               #   first-free
			_fail("place %d refused: %s" % [i + 1, str(res)])
			return
		var rec: Dictionary = m.defense_list[m.defense_list.size() - 1]
		var at: Vector3 = (rec["obj"] as RefCounted).pos
		if landed.has(at):
			_fail("place %d landed on an OCCUPIED slot at %s" \\
					% [i + 1, str(at)])
			return
		landed.append(at)
		var lane := String(pos_lane.get(at, "?"))
		lanes_seen.append(lane)
		print("GWRR-PLACE n=%d lane=%s pos=%s" % [i + 1, lane, str(at)])
	# LEG: the first three UI-style places MUST cover three distinct
	# ground lanes (spread before doubling up on one lane).
	if lanes_seen[0] == lanes_seen[1] or lanes_seen[0] == lanes_seen[2] \\
			or lanes_seen[1] == lanes_seen[2]:
		_fail("first three places share a lane: %s" % str(lanes_seen))
		return
	print("GWRR-OK lanes=%s" % "|".join(lanes_seen))
	quit(0)
'''


def _run_probe(extra_args, tmp_path):
    probe = Path(tmp_path) / "gw_lane_order_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), extra_args,
                                     tmp_path / "user_home")


def _places(out):
    rows = []
    for ln in out.splitlines():
        if not ln.startswith("GWRR-PLACE "):
            continue
        # "GWRR-PLACE n=1 lane=lane_g1 pos=(-40.0, 0.0, 0.0)" — pos
        # carries spaces, so split the three fields only.
        fields = ln.split(" ", 3)
        rows.append({"n": fields[1].split("=", 1)[1],
                     "lane": fields[2].split("=", 1)[1],
                     "pos": fields[3].split("=", 1)[1]})
    assert len(rows) == 4, out
    return rows


def test_first_free_round_robin_leg(tmp_path, class_cache):
    proc = _run_probe([], tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "GWRR-FAIL" not in out, out
    assert out.rstrip().splitlines()[-1].startswith("GWRR-OK"), out
    places = _places(out)
    # LEG 1: three consecutive UI-style first-free places land on THREE
    # DIFFERENT ground lanes — the exact set the map builds (gatefall).
    first3 = [p["lane"] for p in places[:3]]
    assert sorted(first3) == ["lane_g1", "lane_g2", "lane_g3"], places
    # LEG 2: the 4th place lands in rotation — a ground-lane slot that
    # is not one of the three occupied positions (never an occupied one;
    # the probe itself refuses any repeat position).
    assert places[3]["lane"] in ("lane_g1", "lane_g2", "lane_g3"), places
    assert len({p["pos"] for p in places}) == 4, places


def test_planted_red_blocked_order_goes_red(tmp_path, class_cache):
    # The W17f defect shape (lane-file-blocked slot order + first-free):
    # the SAME leg MUST go RED — three places pile into lane_g1.
    proc = _run_probe(["blocked_order"], tmp_path)
    assert proc.returncode == 1, \
        "planted-red: lane-blocked order slipped the round-robin gate\n%s" \
        % proc.stdout
    assert "GWRR-FAIL" in proc.stdout and "GWRR-OK" not in \
        proc.stdout, proc.stdout
    assert "share a lane" in proc.stdout, proc.stdout
