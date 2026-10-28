"""v1.2 F3 relic-assign negative gate (MC 11609) — TESTS-ONLY.

The shipped C11 crossing (scripts/mission_relics.gd) already refuses
uid/relic/phase/none/taken and the hub probe pins all of it
(hub_probe_mission.gd:97-98; test_hub.py:207-213). The ONE uncovered
negative per V12-PLAN §F3 was the stale uid ACROSS SELL: sell-safety is
defense_placer.gd's defense_list.remove_at (:152) — relic_owner (:61-65)
and live_count (:71-76) iterate defense_list, so a sold row's relic is
unowned again and the C5 mirror recomputes in step_bookkeeping
(mission.gd:259). Nothing ever SELLed a relic-carrying defense before
(grep sell in hub_probe_mission.gd = 0 hits).

ENGINE TIER (test_hub.py:118 + test_mission_stale.py embedded-probe
idiom — ONE probe run per file, EMPTY stderr is the verdict): the real
mission.tscn under -s, seeded through the shipped mutators only, legs
driven THROUGH THE SHIPPED ENTRY POINTS (mission.assign_relic /
unassign_relic; the REAL sell path = the panel's own placer, the call
the Sell button makes, defense_panel.gd:247):
  DUP    same relic assigned twice -> second refused "taken"
         (mission_relics.gd:24), owner unchanged, mirror unchanged;
  SELL   sell the relic-carrying row -> row gone from defense_list,
         relic_owner 0, live_count 0, C5 mirror read back through
         snapshot_json (read-what-reached-the-world), pool row STILL
         pool-resident (C11 pool = clear, not move);
  STALE  assign to the sold (dead) uid -> refused "uid", defense_list
         unchanged, NO exception (EMPTY stderr + rc 0 is that proof);
  REUSE  the sold defense's relic re-assigns to a live defense in the
         same build phase -> ok; after the phase transition a new
         assign is refused "phase" (transition gate);
  IDEM   unassign twice -> second "none"; gold/pool unchanged across
         the sequence.
MEASURED, NOT INVENTED (sell refund): the pinned formula is
sell_value(total_spent, missing_ratio, sell_ratio) (defense_obj.gd
header + :249) — a FRESH full-hp T1 carrying a damage-primary relic has
missing_ratio 0, so the refund is EXACTLY 0 and green is byte-unchanged
across the sell (a damaged row refunds the missing share — the
test_mission_stale SELLS leg pins that shape). Re-asserting the
zero-refund here is a guard: a sell-formula change must trip it.

PLANTED-RED: this card is tests-only, so the plants mutate the asserted
RULE in the production tree as THROWAWAY scratch, reverted with
`git checkout --` immediately (porcelain verified empty; transcripts in
.audits/20261028-1500-v12-plan/F3-wave.log): (a) drop the :24 taken
guard -> the DUP leg goes RED; (b) make sell skip the defense_list
remove_at -> the SELL/STALE class goes RED (the relic still reads
owned, the mirror fails to drop). No permanent argv plant is embeddable
here — both bugs live in shipped code the probe must not fake.
"""

import json
import sys
from pathlib import Path

import conftest

GODOT = Path(conftest.repo_path("godot"))

PROBE_SRC = '''
extends SceneTree
# gw relic-negative probe (v1.2 F3, MC 11609). Machine rows: RELICNEG-BOOT
# / -DUP / -SELL / -STALE / -REUSE / -IDEM / RELICNEG-OK; any failed check
# prints RELICNEG-FAIL <why> + rc1. E3: every fail path prints its FAIL
# row and early-RETURNS; quit() fires exactly once.
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MISSION_RELICS := preload("res://scripts/mission_relics.gd")
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
# Scripted relic seeds, hub_probe _scripted_item shape verbatim (uid
# stamped by the bank_add mutator; rarity/ilvl are fixture inputs, not
# balance literals). RELIC_A primary is damage (items.json-pinned by the
# test) so the relic leg never moves the sold row's hp and the sell
# refund rides the pinned formula exactly (measured: a fresh full-hp T1
# refunds 0).
const RELIC_A := "mark_of_fervor"
const RELIC_B := "orb_of_the_deep"

var tables = null
var state = null


func _fail(why: String) -> void:
	print("RELICNEG-FAIL " + why)
	quit(1)


func _scripted_relic(base_id: String) -> Dictionary:
	var base: Dictionary = {}
	for row: Dictionary in tables.rows("items"):
		if String(row.get("id", "")) == base_id:
			base = row
	if base.is_empty():
		_fail("no items.json base " + base_id)
		return {}
	return {
		"uid": 0,
		"base_id": String(base["id"]),
		"slot": String(base["slot"]),
		"rarity": "powerful",
		"ilvl": 3,
		"primary": {"stat": String(base["primary"]), "value": 3.0},
		"secondary": null,
		"atk_speed": float(base["roll_ranges"]["atk_speed"][0]),
		"shot_type": null,
		"proj_count": int(base["roll_ranges"]["proj_count"][0]),
		"mods": [],
		"upgraded": 0,
	}


func _pool_row(m, base_id: String) -> Dictionary:
	for row: Dictionary in m.relic_pool:
		if String(row.get("base_id", "")) == base_id:
			return row
	return {}


func _uids(m) -> String:
	var out := ""
	for rec: Dictionary in m.defense_list:
		out += "%d," % int(rec["uid"])
	return out


func _owner(m, relic_uid: int) -> int:
	# THE shipped statics, preloaded — relic_owner/live_count are read
	# through the same module mission.gd preloads (the sell-safety
	# mechanism itself, never a probe-side reimplementation).
	return MISSION_RELICS.relic_owner(m, relic_uid)


func _snap_assigned(m) -> int:
	var snap: Dictionary = JSON.parse_string(state.snapshot_json(m))
	return int(snap.get("relics_assigned", -1))


func _init() -> void:
	tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)   # F2-5 wiring
	state = graph["state"]
	var save = graph["save"]
	var bridge = graph["bridge"]
	state.set_deck(DECK.duplicate())     # starter deck via the C13 write
	state.bank_add(_scripted_relic(RELIC_A))
	state.bank_add(_scripted_relic(RELIC_B))
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                           # E5: drive _ready directly
	var m_rng := RandomNumberGenerator.new()
	m_rng.seed = 11274                   # pinned seed, smoke idiom
	m.setup(tables, state, save, bridge, "gatefall", "normal", m_rng)
	var pa := _pool_row(m, RELIC_A)
	var pb := _pool_row(m, RELIC_B)
	if pa.is_empty() or pb.is_empty() or int(m.relic_pool.size()) != 2 \\
			or int(m.relics_assigned) != 0:
		_fail("pool copy=%d" % int(m.relic_pool.size()))
		return
	var tower_row: Dictionary = {}
	for trow: Dictionary in tables.rows("towers"):
		if String(trow["class"]) == "tower":
			tower_row = trow
			break
	var p1: Dictionary = m.place_defense(tower_row, 1, Vector3.ZERO)
	var p2: Dictionary = m.place_defense(tower_row, 1, Vector3(2, 0, 0))
	if not bool(p1.get("ok", false)) or not bool(p2.get("ok", false)):
		_fail("place: %s %s" % [str(p1), str(p2)])
		return
	var uid1 := int(p1["uid"])
	var uid2 := int(p2["uid"])
	print("RELICNEG-BOOT pool=%d green=%d uid1=%d uid2=%d" % [
			int(m.relic_pool.size()), int(m.green), uid1, uid2])

	# ---- leg DUP: same relic TWICE -> second refused "taken" (:24),
	# the FIRST carrier keeps it, the C5 field unchanged. ----
	var ar1: Dictionary = m.assign_relic(uid1, int(pa["uid"]))
	var ar2: Dictionary = m.assign_relic(uid2, int(pa["uid"]))
	var kept := _owner(m, int(pa["uid"]))
	print("RELICNEG-DUP first_ok=%s second=%s owner_kept=%d assigned=%d" % [
			str(bool(ar1.get("ok", false))), String(ar2.get("why", "NONE")),
			kept, int(m.relics_assigned)])
	if not bool(ar1.get("ok", false)) or String(ar2.get("why", "")) != "taken" \\
			or kept != uid1 or int(m.relics_assigned) != 1:
		_fail("dup: %s %s owner=%d assigned=%d" % [str(ar1), str(ar2),
				kept, m.relics_assigned])
		return

	# ---- leg SELL (sell-return, MEASURED): the relic-carrying row sold
	# through the REAL sell path (the panel's placer — the Sell button's
	# own call). Pre-step reads ride the sell-safety mechanism; ONE
	# step tick recomputes the C5 mirror (mission.gd:259) and
	# snapshot_json reads back what reached the world. One build tick
	# moves no green (phase_controller awards only on kills/wave clear).
	var g0 := int(m.green)
	var sellres: Dictionary = m.get_node("DefensePanel").placer.sell(uid1)
	var refund := int(sellres.get("refund", -1))
	var live := MISSION_RELICS.live_count(m)
	var owner_after := _owner(m, int(pa["uid"]))
	var list_after := _uids(m)
	m.step(1.0 / 60.0)
	var snap_a := _snap_assigned(m)
	print("RELICNEG-SELL ok=%s refund=%d green=%d->%d list=%s owner=%d live=%d snap=%d pool=%d" % [
			str(bool(sellres.get("ok", false))), refund, g0, int(m.green),
			list_after, owner_after, live, snap_a,
			int(m.relic_pool.size())])
	if not bool(sellres.get("ok", false)) or list_after != "%d," % uid2 \\
			or owner_after != 0 or live != 0 or snap_a != 0 \\
			or int(m.relic_pool.size()) != 2 or int(m.green) != g0 + refund:
		_fail("sell: %s list=%s owner=%d live=%d snap=%d pool=%d" % [
				str(sellres), list_after, owner_after, live, snap_a,
				m.relic_pool.size()])
		return

	# ---- leg STALE: assign onto the SOLD (dead) uid -> refused "uid",
	# defense_list untouched; NO exception (rc 0 + EMPTY stderr is that
	# proof at the pytest wrapper). ----
	var stale: Dictionary = m.assign_relic(uid1, int(pa["uid"]))
	var list_stale := _uids(m)
	print("RELICNEG-STALE why=%s list=%s assigned=%d" % [
			String(stale.get("why", "NONE")), list_stale,
			int(m.relics_assigned)])
	if String(stale.get("why", "")) != "uid" or list_stale != "%d," % uid2 \\
			or int(m.relics_assigned) != 0:
		_fail("stale: %s list=%s assigned=%d" % [str(stale), list_stale,
				m.relics_assigned])
		return

	# ---- leg REUSE: the sold defense's relic re-assigns to a live
	# defense in the same build phase; across the phase transition a
	# new assign is refused "phase" (transition gate first). ----
	var ar3: Dictionary = m.assign_relic(uid2, int(pa["uid"]))
	m.phase_kind = "combat"              # drive-real-entry-points write
	var ref_phase: Dictionary = m.assign_relic(uid2, int(pb["uid"]))
	m.phase_kind = "build"
	print("RELICNEG-REUSE ok=%s assigned=%d phase=%s" % [
			str(bool(ar3.get("ok", false))), int(m.relics_assigned),
			String(ref_phase.get("why", "NONE"))])
	if not bool(ar3.get("ok", false)) or int(m.relics_assigned) != 1 \\
			or String(ref_phase.get("why", "")) != "phase":
		_fail("reuse: %s %s assigned=%d" % [str(ar3), str(ref_phase),
				m.relics_assigned])
		return

	# ---- leg IDEM: unassign twice -> second "none"; gold/pool
	# unchanged across the sequence. ----
	var g1 := int(m.green)
	var pool_n := int(m.relic_pool.size())
	var un1: Dictionary = m.unassign_relic(uid2)
	var un2: Dictionary = m.unassign_relic(uid2)
	print("RELICNEG-IDEM unequip=%s none=%s green_same=%s pool=%d assigned=%d" % [
			str(bool(un1.get("ok", false))), String(un2.get("why", "NONE")),
			str(int(m.green) == g1), int(m.relic_pool.size()),
			int(m.relics_assigned)])
	if not bool(un1.get("ok", false)) \\
			or String(un2.get("why", "")) != "none" \\
			or int(m.green) != g1 or int(m.relic_pool.size()) != pool_n \\
			or int(m.relics_assigned) != 0:
		_fail("idem: %s %s" % [str(un1), str(un2)])
		return
	print("RELICNEG-OK")
	quit(0)
'''


def _run_probe(tmp_path):
    probe = Path(tmp_path) / "gw_relic_neg_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), (), tmp_path / "user_home")


def _only(out, tag):
    rows = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert len(rows) == 1, out
    return dict(x.split("=", 1) for x in rows[0].split(" ")[1:])


def _json(name):
    return json.loads((GODOT / "data" / ("%s.json" % name)).read_text(
        encoding="utf-8"))


def test_relic_negatives_engine_leg(tmp_path, class_cache):
    # ONE probe run over the real mission.tscn (test_hub pattern — the
    # file's single engine leg; no second harness mechanism).
    proc = _run_probe(tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (parse noise AND the no-exception " \
        "proof of the STALE leg):\n%s" % proc.stderr
    assert "RELICNEG-FAIL" not in proc.stdout, proc.stdout
    assert proc.stdout.rstrip().endswith("RELICNEG-OK"), proc.stdout
    out = proc.stdout

    # Data truth, re-derived — never from a test-side copy of a cost.
    towers = _json("towers")
    trows = towers["towers"] if isinstance(towers, dict) else towers
    cost = int(next(r for r in trows
                    if r["class"] == "tower")["base_cost"])
    start_green = int(_json("maps/gatefall")["start_green"])
    items = {r["id"]: r for r in _json("items")}
    sell_ratio = float(_json("economy")["sell_ratio"])

    boot = _only(out, "RELICNEG-BOOT")
    assert boot["pool"] == "2", boot                # bank->pool copy, both seeds
    assert int(boot["green"]) == start_green - 2 * cost, boot
    uid1, uid2 = int(boot["uid1"]), int(boot["uid2"])
    assert uid1 > 0 and uid2 > 0 and uid1 != uid2, boot

    dup = _only(out, "RELICNEG-DUP")
    # Second assign of the SAME relic refused (the :24 guard, both
    # directions covered by the hub probe — this is the relic-owned one);
    # the first carrier is still the owner; the mirror stayed at 1.
    assert dup == {"first_ok": "true", "second": "taken",
                   "owner_kept": str(uid1), "assigned": "1"}, dup

    sell = _only(out, "RELICNEG-SELL")
    # MEASURED refund (pinned formula, defense_obj.gd header): fresh
    # full-hp T1 + damage-primary relic -> missing_ratio 0 -> refund 0,
    # green byte-unchanged. Relic A's primary is data-pinned non-hp:
    assert items["mark_of_fervor"]["primary"] != "hp", items["mark_of_fervor"]
    assert int(sell["refund"]) == int(round(cost * sell_ratio * 0.0)), sell
    g_before, g_after = sell["green"].split("->")
    assert g_before == g_after, sell
    # The row left defense_list; its relic reads UNOWNED (relic_owner +
    # live_count are the shipped sell-safe mirrors read through the
    # preloaded module); the C5 mirror read back through snapshot_json;
    # the pool row never left relic_pool (C11 pool = clear, not move).
    assert sell["ok"] == "true" and sell["list"] == "%d," % uid2, sell
    assert sell["owner"] == "0" and sell["live"] == "0", sell
    assert sell["snap"] == "0" and sell["pool"] == "2", sell

    stale = _only(out, "RELICNEG-STALE")
    # Dead uid refused "uid"; defense_list still the one live row (no
    # resurrection, no partial); rc 0 + EMPTY stderr above = no exception.
    assert stale["why"] == "uid", stale
    assert stale["list"] == "%d," % uid2 and str(uid1) not in stale["list"], \
        stale
    assert stale["assigned"] == "0", stale

    reuse = _only(out, "RELICNEG-REUSE")
    # The sold defense's relic re-uses onto the live row in build; the
    # phase transition gates any NEW assign.
    assert reuse == {"ok": "true", "assigned": "1", "phase": "phase"}, reuse

    idem = _only(out, "RELICNEG-IDEM")
    # Unassign twice -> second "none"; gold/pool untouched across the run.
    assert idem == {"unequip": "true", "none": "none", "green_same": "true",
                    "pool": "2", "assigned": "0"}, idem
